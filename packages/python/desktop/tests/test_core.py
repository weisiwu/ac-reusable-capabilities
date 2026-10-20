import json
import sqlite3

import pytest

from ctf_desktop.auth import AccessPolicy, AuthService, PasswordHasher, Principal
from ctf_desktop.crud import CrudController
from ctf_desktop.diagnostics import AuditEvent, AuditJournal, redact
from ctf_desktop.printing import BatchPrintRunner, CancellationToken, PrintItem
from ctf_desktop.query import PageRequest, PageResult, SqlWhere
from ctf_desktop.runtime import AppPaths, load_json_config
from ctf_desktop.services import ServiceRegistry, ServiceSpec, ServiceStartError
from ctf_desktop.storage import Migration, SqliteStore
from ctf_desktop.transport import SerialConfig, SerialTransport, TransportError


def test_query_builder_binds_values_and_escapes_like():
    where = SqlWhere({"name": "display_name"}).contains("name", "a%_\\b")
    sql, values = where.build()
    assert sql == "WHERE display_name LIKE ? ESCAPE '\\'"
    assert values == ("%a\\%\\_\\\\b%",)
    with pytest.raises(ValueError):
        where.equal("untrusted; DROP TABLE users", "x")
    assert PageRequest(3, 10).offset == 20
    assert PageResult((), 21, PageRequest(3, 10)).pages == 3
    with pytest.raises(ValueError):
        PageRequest(1.5, 20)
    with pytest.raises(ValueError):
        PageResult((), -1, PageRequest())


def test_service_dependency_order_and_failure_rollback():
    events = []

    class Service:
        def __init__(self, name):
            self.name = name

        def start(self):
            events.append("start:" + self.name)
            if self.name == "broken":
                raise RuntimeError("failed")

        def stop(self):
            events.append("stop:" + self.name)

    registry = ServiceRegistry()
    registry.register(ServiceSpec("broken", lambda _r: Service("broken"), ("base",)))
    registry.register(ServiceSpec("base", lambda _r: Service("base")))
    with pytest.raises(ServiceStartError):
        registry.start()
    assert events == ["start:base", "start:broken", "stop:broken", "stop:base"]
    assert not registry.running


def test_authentication_and_host_authorization():
    hasher = PasswordHasher(100_000)
    encoded = hasher.hash("correct")

    class Store:
        def find_by_username(self, _username):
            return {"id": "u1", "roles": ("editor",), "password_hash": encoded}

    service = AuthService(Store(), hasher)
    assert service.authenticate("u", "bad") is None
    principal = service.authenticate("u", "correct")
    assert principal == Principal("u1", frozenset({"editor"}))
    policy = AccessPolicy(lambda actor, action, _resource: action == "read" or "admin" in actor.roles)
    policy.require(principal, "read")
    with pytest.raises(PermissionError):
        policy.require(principal, "delete")


def test_crud_validates_and_authorizes_before_write():
    calls = []

    class Repository:
        def create(self, values):
            calls.append(("write", values["name"]))
            return 7

    controller = CrudController(
        Repository(),
        validate=lambda values: calls.append(("validate", values["name"])),
        authorize=lambda action, _resource: calls.append(("authorize", action)),
        changed=lambda action, identity: calls.append(("changed", action, identity)),
    )
    assert controller.create({"name": "A"}) == 7
    assert calls == [("authorize", "create"), ("validate", "A"), ("write", "A"), ("changed", "create", 7)]


def test_serial_transport_rejects_partial_write():
    class FakeSerial:
        is_open = True

        def __init__(self, **_kwargs):
            self.flushed = False

        def write(self, payload):
            return len(payload) - 1

        def flush(self):
            self.flushed = True

        def close(self):
            self.is_open = False

    transport = SerialTransport(SerialConfig("test-port"), FakeSerial)
    transport.open()
    with pytest.raises(TransportError, match="incomplete"):
        transport.write(b"abcd")
    transport.close()
    assert not transport.is_open


def test_sqlite_migration_is_atomic_and_restore_keeps_rollback(tmp_path):
    store = SqliteStore(tmp_path / "live.sqlite")
    store.migrate([Migration(1, lambda db: db.execute("CREATE TABLE items (name TEXT)"))])
    store.connect().execute("INSERT INTO items VALUES ('before')")
    store.connect().commit()
    snapshot = store.backup(tmp_path / "snapshot.sqlite")
    store.connect().execute("INSERT INTO items VALUES ('after')")
    store.connect().commit()
    rollback = store.restore(snapshot)
    assert rollback and rollback.exists()
    assert store.connect().execute("SELECT name FROM items").fetchall() == [("before",)]
    def failing(db):
        db.execute("CREATE TABLE extra (value TEXT)")
        raise RuntimeError("abort")
    with pytest.raises(RuntimeError):
        store.migrate([Migration(1, lambda _db: None), Migration(2, failing)])
    assert store.connect().execute("PRAGMA user_version").fetchone()[0] == 1
    assert store.connect().execute("SELECT name FROM sqlite_master WHERE name='extra'").fetchone() is None
    store.close()


def test_batch_print_prepares_once_and_stops_on_uncertain_submission():
    prepared, submitted = [], []
    token = CancellationToken()
    runner = BatchPrintRunner(
        lambda key: prepared.append(key) or key.encode(),
        lambda artifact: submitted.append(artifact),
    )
    result = runner.start([PrintItem("one", 3), PrintItem("two", 1)], token).result(timeout=2)
    runner.close()
    assert prepared == ["one", "two"]
    assert submitted == [b"one", b"one", b"one", b"two"]
    assert (result.total, result.succeeded, result.failed, result.skipped) == (4, 4, 0, 0)


def test_batch_print_cancels_at_copy_boundary_and_never_retries_unknown_submit():
    token = CancellationToken()
    submitted = []
    runner = BatchPrintRunner(
        lambda key: key.encode(),
        lambda artifact: submitted.append(artifact),
        on_progress=lambda _key, _copy, _total: token.cancel(),
    )
    result = runner.run([PrintItem("one", 3), PrintItem("two")], token)
    assert (result.succeeded, result.skipped) == (1, 3)
    assert submitted == [b"one"]
    runner.close()

    attempts = []
    def uncertain(_artifact):
        attempts.append(1)
        raise RuntimeError("unknown printer outcome")
    runner = BatchPrintRunner(lambda _key: b"pdf", uncertain)
    result = runner.run([PrintItem("one", 3)])
    runner.close()
    assert attempts == [1]
    assert (result.succeeded, result.failed, result.skipped) == (0, 1, 2)


def test_batch_print_progress_callback_failure_does_not_reclassify_submitted_copy():
    runner = BatchPrintRunner(
        lambda _key: b"report",
        lambda _artifact: None,
        on_progress=lambda _key, _copy, _total: (_ for _ in ()).throw(RuntimeError("display gone")),
    )
    result = runner.run([PrintItem("one")])
    runner.close()
    assert (result.succeeded, result.failed, result.skipped) == (1, 0, 0)
    assert result.error == "display gone"


def test_runtime_config_and_diagnostic_redaction(tmp_path):
    config = tmp_path / "config.json"
    config.write_text('{"port": 1234}', encoding="utf-8")
    values = load_json_config(config, lambda item: item["port"] > 0 or (_ for _ in ()).throw(ValueError()))
    assert values == {"port": 1234}
    assert AppPaths("sample-app").user_data().name == "sample-app"
    with pytest.raises(ValueError):
        AppPaths("..")
    assert redact({"token": "secret", "nested": [{"password": "x"}]}) == {
        "token": "[REDACTED]", "nested": [{"password": "[REDACTED]"}]
    }
    journal = AuditJournal(tmp_path / "audit.jsonl")
    journal.append(AuditEvent("export", "user-1", "item-1", {"api_key": "raw"}))
    assert json.loads((tmp_path / "audit.jsonl").read_text())["detail"] == {"api_key": "[REDACTED]"}


def test_restore_rejects_corrupt_snapshot_without_changing_live_db(tmp_path):
    store = SqliteStore(tmp_path / "live.sqlite")
    store.migrate([Migration(1, lambda db: db.execute("CREATE TABLE items (id INTEGER)"))])
    bad = tmp_path / "bad.sqlite"
    bad.write_bytes(b"not sqlite")
    with pytest.raises(sqlite3.DatabaseError):
        store.restore(bad)
    assert store.connect().execute("PRAGMA user_version").fetchone()[0] == 1
    store.close()
