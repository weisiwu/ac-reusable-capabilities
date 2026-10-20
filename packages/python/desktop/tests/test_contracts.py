"""Public contract boundaries exercised against the independently installed package."""
import json
import logging
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing

import pytest

from ctf_desktop.auth import AccessPolicy, AuthService, PasswordHasher, Principal
from ctf_desktop.crud import CrudController
from ctf_desktop.diagnostics import AuditEvent, AuditJournal, configure_json_logger, redact
from ctf_desktop.printing import BatchPrintRunner, CancellationToken, PrintItem
from ctf_desktop.query import PageRequest, PageResult, SqlWhere
from ctf_desktop.runtime import AppPaths, load_json_config
from ctf_desktop.services import ServiceRegistry, ServiceSpec, ServiceStartError
from ctf_desktop.storage import Migration, SqliteStore
from ctf_desktop.transport import SerialConfig, SerialTransport, TransportError


@pytest.mark.parametrize('number,size', [(0, 1), (1, 0), (-1, 20), (True, 2), (1, False), (1.0, 2)])
def test_invalid_page_request(number, size):
    with pytest.raises(ValueError):
        PageRequest(number, size)


def test_sql_predicates_execute_literal_filters_without_interpolating_values():
    with closing(sqlite3.connect(':memory:')) as db:
        db.execute('CREATE TABLE items (name TEXT, quantity INTEGER)')
        db.executemany('INSERT INTO items VALUES (?,?)', [('a%_\\b', 2), ('axb', 2), ('a%_\\b', 5)])
        where = SqlWhere({'name': 'name', 'quantity': 'quantity'})
        assert where.build() == ('', ())
        assert where.equal('name', None).contains('name', '') is where
        where.contains('name', '%_\\').range('quantity', 1, 3)
        sql, parameters = where.build()
        assert db.execute('SELECT name FROM items ' + sql, parameters).fetchall() == [('a%_\\b',)]
        assert where.build() == (sql, parameters)
        assert PageResult((), 0, PageRequest()).pages == 1


@pytest.mark.parametrize('encoded', ['', 'x', 'sha1$100000$00$00', 'pbkdf2_sha256$1$00$00', 'pbkdf2_sha256$100000$zz$zz'])
def test_password_malformed_text_is_rejected(encoded):
    hasher = PasswordHasher(100_000)
    assert not hasher.verify('sample', encoded)


def test_hash_salts_rehash_policy_and_missing_account():
    hasher = PasswordHasher(100_000)
    one, two = hasher.hash('example-only'), hasher.hash('example-only')
    assert one != two and hasher.verify('example-only', one)
    assert not hasher.needs_rehash(one)
    assert PasswordHasher(110_000).needs_rehash(one)
    assert hasher.needs_rehash('invalid')
    with pytest.raises(ValueError):
        hasher.hash('')
    with pytest.raises(ValueError):
        PasswordHasher(99_999)
    class Store:
        def find_by_username(self, username):
            return None if username == 'unknown' else {'id': 'sample', 'password_hash': one, 'roles': 'reader'}
    service = AuthService(Store(), hasher)
    assert service.authenticate('unknown', 'example-only') is None
    assert service.authenticate('known', 'example-only').roles == frozenset({'reader'})


class MemoryRepository:
    def __init__(self):
        self.rows = {}
        self.next_id = 1
    def list_page(self, request, filters):
        rows = tuple(dict(id=i, **v) for i, v in self.rows.items() if not filters or v['name'] == filters['name'])
        return PageResult(rows[request.offset:request.offset+request.size], len(rows), request)
    def get(self, identity):
        return self.rows.get(identity)
    def create(self, values):
        identity = self.next_id
        self.next_id += 1
        self.rows[identity] = dict(values)
        return identity
    def update(self, identity, values):
        self.rows[identity].update(values)
    def delete(self, identity):
        del self.rows[identity]


def test_crud_full_lifecycle_and_denial_before_every_host_access():
    repo = MemoryRepository()
    events = []
    controller = CrudController(repo, authorize=lambda *a: None, changed=lambda *a: events.append(a))
    identity = controller.create({'name': 'initial'})
    assert controller.detail(identity) == {'name': 'initial'}
    controller.update(identity, {'name': 'changed'})
    assert controller.list_page(PageRequest(), {'name': 'changed'}).total == 1
    controller.delete(identity)
    assert controller.list_page(PageRequest()).total == 0
    assert events == [('create', identity), ('update', identity), ('delete', identity)]
    def deny(*args):
        raise PermissionError('denied')
    controller.authorize = deny
    for call in (lambda: controller.create({}), lambda: controller.update(1, {}), lambda: controller.delete(1), lambda: controller.detail(1), lambda: controller.list_page(PageRequest())):
        with pytest.raises(PermissionError):
            call()
    assert repo.rows == {}


def test_crud_validation_failure_does_not_persist_or_notify():
    repo = MemoryRepository()
    def invalid(values):
        raise ValueError('invalid name')
    controller = CrudController(repo, authorize=lambda *a: None, validate=invalid)
    with pytest.raises(ValueError):
        controller.create({'name': ''})
    assert not repo.rows


@pytest.mark.parametrize('specs', [
    [ServiceSpec('one', lambda r: object(), ('missing',))],
    [ServiceSpec('one', lambda r: object(), ('two',)), ServiceSpec('two', lambda r: object(), ('one',))],
])
def test_dependency_errors_happen_before_start(specs):
    registry = ServiceRegistry()
    for spec in specs:
        registry.register(spec)
    with pytest.raises(ValueError):
        registry.start()
    assert not registry.running


def test_service_success_duplicate_start_reverse_stop_and_cleanup_failure():
    events = []
    class Service:
        def __init__(self, name): self.name = name
        def start(self): events.append('start:' + self.name)
        def stop(self):
            events.append('stop:' + self.name)
            if self.name == 'child': raise ValueError('stop error')
    registry = ServiceRegistry()
    registry.register(ServiceSpec('base', lambda r: Service('base')))
    registry.register(ServiceSpec('child', lambda r: Service('child'), ('base',)))
    with pytest.raises(ValueError): registry.register(ServiceSpec('base', lambda r: None))
    registry.start()
    assert registry.get('base').name == 'base'
    with pytest.raises(RuntimeError): registry.start()
    with pytest.raises(ValueError): registry.register(ServiceSpec('late', lambda r: None))
    with pytest.raises(RuntimeError): registry.stop()
    registry.stop()
    assert not registry.running
    assert events == ['start:base', 'start:child', 'stop:child', 'stop:base']
    with pytest.raises(KeyError): registry.get('base')


class SerialDouble:
    def __init__(self, **kwargs): self.is_open = True; self.received = []; self.flushed = 0
    def close(self): self.is_open = False
    def write(self, data): self.received.append(data); return len(data)
    def flush(self): self.flushed += 1
    def read(self, size): return b'abc'[:size]


def test_serial_lifecycle_injected_io_and_error_causes():
    handles = []
    def factory(**kwargs):
        handle = SerialDouble(**kwargs); handles.append(handle); return handle
    transport = SerialTransport(SerialConfig('fake'), factory)
    try:
        for op in (lambda: transport.read(1), lambda: transport.write(b'a')):
            with pytest.raises(TransportError): op()
        transport.open(); transport.open()
        assert len(handles) == 1 and transport.is_open
        transport.write(b'hello')
        assert handles[0].received == [b'hello'] and handles[0].flushed == 1
        assert transport.read(2) == b'ab'
        with pytest.raises(ValueError): transport.read(-1)
        def broken(size): raise OSError('unplugged')
        handles[0].read = broken
        with pytest.raises(TransportError) as raised: transport.read(1)
        assert isinstance(raised.value.__cause__, OSError)
    finally:
        transport.close()
    transport.close()
    assert not transport.is_open and not handles[0].is_open
    def bad_factory(**kwargs): raise OSError('busy')
    with pytest.raises(TransportError): SerialTransport(SerialConfig('fake'), bad_factory).open()


@pytest.mark.parametrize('kwargs', [{'port': ''}, {'port': 'x', 'baudrate': 0}, {'port': 'x', 'timeout': -1}, {'port': 'x', 'write_timeout': -1}])
def test_invalid_serial_configuration(kwargs):
    with pytest.raises(ValueError): SerialConfig(**kwargs)


def test_store_pending_transaction_backup_fails_without_committing_or_hanging(tmp_path):
    store = SqliteStore(tmp_path/'db.sqlite')
    try:
        store.migrate([Migration(1, lambda db: db.execute('CREATE TABLE items (name TEXT)'))])
        store.connect().execute("INSERT INTO items VALUES ('pending')")
        with pytest.raises(RuntimeError, match='pending writes'):
            store.backup(tmp_path/'snapshot.sqlite')
        assert store.connect().in_transaction
        store.connect().rollback()
        assert store.connect().execute('SELECT * FROM items').fetchall() == []
        assert not (tmp_path/'snapshot.sqlite').exists()
    finally:
        store.close()


def test_store_repeated_migration_invalid_versions_newer_schema_and_existing_backup(tmp_path):
    store = SqliteStore(tmp_path/'has # space.sqlite')
    migrations = [Migration(1, lambda db: db.execute('CREATE TABLE items (name TEXT)'))]
    try:
        assert store.migrate(migrations) == store.migrate(migrations) == 1
        with pytest.raises(ValueError): store.migrate([Migration(0, lambda db: None)])
        with pytest.raises(ValueError): store.migrate(migrations * 2)
        snapshot = store.backup(tmp_path/'backup ? # space.sqlite')
        with pytest.raises(FileExistsError): store.backup(snapshot)
        with pytest.raises(ValueError): store.restore(store.path)
        assert store.restore(snapshot).exists()
        store.migrate([*migrations, Migration(2, lambda db: None)])
        with pytest.raises(ValueError): store.migrate(migrations)
    finally:
        store.close(); store.close()


def test_backup_and_restore_close_every_temporary_connection(tmp_path, monkeypatch):
    store = SqliteStore(tmp_path/'live.sqlite')
    store.migrate([Migration(1, lambda db: db.execute('CREATE TABLE items (id INTEGER)'))])
    original = sqlite3.connect
    connections = []
    def tracked(*args, **kwargs):
        conn = original(*args, **kwargs); connections.append(conn); return conn
    monkeypatch.setattr(sqlite3, 'connect', tracked)
    try:
        backup = store.backup(tmp_path/'snapshot.sqlite')
        store.restore(backup)
        for conn in connections:
            with pytest.raises(sqlite3.ProgrammingError, match='closed'):
                conn.execute('SELECT 1')
        assert not list(tmp_path.glob('.ctf-*'))
    finally:
        store.close()


def test_print_empty_plan_empty_artifact_precancel_and_executor_close():
    calls = []
    runner = BatchPrintRunner(lambda key: calls.append(key) or b'', lambda artifact: None)
    try:
        empty = runner.run([])
        assert (empty.total, empty.succeeded, empty.failed, empty.skipped) == (0, 0, 0, 0)
        token = CancellationToken(); token.cancel(); token.cancel()
        result = runner.start([PrintItem('one')], token).result(timeout=2)
        assert result.skipped == 1 and not calls
        result = runner.run([PrintItem('one'), PrintItem('two')])
        assert result.failed == 1 and result.skipped == 1 and calls == ['one']
    finally:
        runner.close()
    with pytest.raises(RuntimeError): runner.start([])


@pytest.mark.parametrize('key,copies', [('', 1), ('a', 0), ('a', True)])
def test_invalid_print_item(key, copies):
    with pytest.raises(ValueError): PrintItem(key, copies)


def test_explicit_print_dispatcher_owns_submission():
    events = []
    def dispatch(call): events.append('dispatch'); call()
    runner = BatchPrintRunner(lambda key: b'pdf', lambda data: events.append(data), dispatch_submit=dispatch)
    try:
        assert runner.start([PrintItem('x', 2)]).result(timeout=2).succeeded == 2
        assert events == ['dispatch', b'pdf', 'dispatch', b'pdf']
    finally:
        runner.close()


def test_diagnostics_file_handler_ownership_and_concurrent_audit(tmp_path):
    name = 'ac-test-diagnostics'
    logger = configure_json_logger(name, tmp_path/'app.jsonl')
    try:
        assert configure_json_logger(name, tmp_path/'app.jsonl') is logger
        assert len(logger.handlers) == 1
        logger.info('safe message', extra={'data': {'token': 'secret', 'ok': 3}})
        record = json.loads((tmp_path/'app.jsonl').read_text())
        assert record['data'] == {'token': '[REDACTED]', 'ok': 3}
    finally:
        for handler in list(logger.handlers):
            handler.close(); logger.removeHandler(handler)
    journal = AuditJournal(tmp_path/'audit.jsonl', lambda key: key == 'private')
    def write(i): journal.append(AuditEvent('read', str(i), 'sample', {'private': 'hidden'}))
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(write, range(12)))
    rows = [json.loads(line) for line in (tmp_path/'audit.jsonl').read_text().splitlines()]
    assert len(rows) == 12 and {row['actor'] for row in rows} == {str(i) for i in range(12)}
    assert all(row['detail'] == {'private': '[REDACTED]'} for row in rows)
    with pytest.raises(ValueError): journal.append(AuditEvent('', '', '', {}))
    source = {'nested': ({'custom': 'hidden'},)}
    assert redact(source, lambda key: key == 'custom') == {'nested': [{'custom': '[REDACTED]'}]}
    assert source['nested'][0]['custom'] == 'hidden'


@pytest.mark.parametrize('content', ['[]', 'not json'])
def test_config_rejects_nonobjects_and_malformed_json(tmp_path, content):
    path = tmp_path/'config.json'; path.write_text(content)
    with pytest.raises(ValueError): load_json_config(path, lambda values: None)


def test_config_validation_failure_and_data_directory(tmp_path, monkeypatch):
    path = tmp_path/'config.json'; path.write_text('{}')
    def invalid(values): raise ValueError('required field')
    with pytest.raises(ValueError): load_json_config(path, invalid)
    monkeypatch.setattr('ctf_desktop.runtime.sys.platform', 'linux')
    monkeypatch.setenv('XDG_DATA_HOME', str(tmp_path/'data'))
    paths = AppPaths('sample')
    assert not paths.user_data().exists()
    assert paths.ensure_user_data() == tmp_path/'data/sample'
    assert paths.ensure_user_data().is_dir()
