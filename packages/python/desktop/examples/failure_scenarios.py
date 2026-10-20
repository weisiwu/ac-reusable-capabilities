"""Nine runnable failure/recovery scenarios using only the Python standard library."""
import json
import logging
from pathlib import Path
from tempfile import TemporaryDirectory

from ctf_desktop.auth import AccessPolicy, PasswordHasher, Principal
from ctf_desktop.crud import CrudController
from ctf_desktop.diagnostics import AuditEvent, AuditJournal, configure_json_logger
from ctf_desktop.printing import BatchPrintRunner, CancellationToken, PrintItem
from ctf_desktop.query import PageRequest, SqlWhere
from ctf_desktop.runtime import AppPaths, load_json_config
from ctf_desktop.services import ServiceRegistry, ServiceSpec, ServiceStartError
from ctf_desktop.storage import Migration, SqliteStore
from ctf_desktop.transport import SerialConfig, SerialTransport, TransportError


def auth_and_denied_write():
    hasher = PasswordHasher(100_000)
    encoded = hasher.hash('example-only')
    assert hasher.verify('example-only', encoded)
    assert not hasher.verify('wrong', encoded)
    assert hasher.needs_rehash('damaged')
    policy = AccessPolicy(lambda actor, action, resource: action == 'read')
    principal = Principal('reader')
    class Repository:
        def create(self, values): raise AssertionError('denied write reached repository')
    controller = CrudController(Repository(), authorize=lambda action, resource: policy.require(principal, action, resource))
    try:
        controller.create({'name': 'sample'})
    except PermissionError:
        return
    raise AssertionError('expected denial')


def literal_query_and_invalid_page():
    sql, values = SqlWhere({'name': 'name'}).contains('name', '100%').build()
    assert values == ('%100\\%%',) and '?' in sql
    try:
        PageRequest(0)
    except ValueError:
        return
    raise AssertionError('invalid page accepted')


def service_start_rollback():
    stopped = []
    class Resource:
        def stop(self): stopped.append('base')
    def fail(registry): raise RuntimeError('sample startup failure')
    registry = ServiceRegistry()
    registry.register(ServiceSpec('base', lambda registry: Resource()))
    registry.register(ServiceSpec('child', fail, ('base',)))
    try:
        registry.start()
    except ServiceStartError as error:
        assert isinstance(error.__cause__, RuntimeError)
        assert stopped == ['base'] and not registry.running
    finally:
        registry.stop()


def sqlite_failed_migration_and_restore(directory):
    store = SqliteStore(directory / 'sample.sqlite')
    try:
        store.migrate([Migration(1, lambda db: db.execute('CREATE TABLE items (name TEXT)'))])
        store.connect().execute("INSERT INTO items VALUES ('before')")
        store.connect().commit()
        backup = store.backup(directory/'snapshot.sqlite')
        def broken(db):
            db.execute('CREATE TABLE unfinished (id INTEGER)')
            raise RuntimeError('sample failed migration')
        try:
            store.migrate([Migration(1, lambda db: None), Migration(2, broken)])
        except RuntimeError:
            assert store.connect().execute('PRAGMA user_version').fetchone()[0] == 1
        store.connect().execute("INSERT INTO items VALUES ('after')")
        store.connect().commit()
        rollback = store.restore(backup)
        assert rollback.is_file()
        assert store.connect().execute('SELECT name FROM items').fetchall() == [('before',)]
    finally:
        store.close()


def serial_partial_write():
    class Handle:
        is_open = True
        def __init__(self, **kwargs): pass
        def write(self, data): return len(data)-1
        def flush(self): raise AssertionError('short write must not flush')
        def close(self): self.is_open = False
    transport = SerialTransport(SerialConfig('sample'), Handle)
    try:
        transport.open()
        try:
            transport.write(b'example')
        except TransportError:
            return
        raise AssertionError('short write accepted')
    finally:
        transport.close()


def cancelled_batch():
    token = CancellationToken()
    submitted = []
    runner = BatchPrintRunner(lambda key: key.encode(), submitted.append, on_progress=lambda *args: token.cancel())
    try:
        result = runner.start([PrintItem('sample', 3)], token).result(timeout=2)
        assert result.succeeded == 1 and result.skipped == 2
    finally:
        runner.close()


def uncertain_submission_is_not_retried():
    attempts = []
    def submit(data):
        attempts.append(data)
        raise RuntimeError('device did not confirm outcome')
    runner = BatchPrintRunner(lambda key: b'example', submit)
    try:
        result = runner.run([PrintItem('sample', 3)])
        assert result.failed == 1 and len(attempts) == 1 and result.skipped == 2
    finally:
        runner.close()


def structured_log_and_audit(directory):
    logger = configure_json_logger('sample-private-data', directory/'app.jsonl', lambda key: key == 'private')
    try:
        logger.info('sample operation', extra={'data': {'private': 'hidden'}})
        assert 'hidden' not in (directory/'app.jsonl').read_text()
    finally:
        for handler in list(logger.handlers):
            handler.close(); logger.removeHandler(handler)
    journal = AuditJournal(directory/'audit.jsonl')
    journal.append(AuditEvent('read', 'sample', 'item-1', {'token': 'hidden'}))
    assert json.loads(journal.path.read_text())['detail']['token'] == '[REDACTED]'


def configuration_validation(directory):
    config = directory/'config.json'; config.write_text('{"page_size": 0}')
    def validate(values):
        if values.get('page_size', 0) < 1: raise ValueError('page_size must be positive')
    try:
        load_json_config(config, validate)
    except ValueError:
        assert AppPaths('example').user_data().name == 'example'
        return
    raise AssertionError('invalid configuration accepted')


def main():
    with TemporaryDirectory() as temporary:
        directory = Path(temporary)
        for scenario in (auth_and_denied_write, literal_query_and_invalid_page, service_start_rollback, serial_partial_write, cancelled_batch, uncertain_submission_is_not_retried):
            scenario()
        for scenario in (sqlite_failed_migration_and_restore, structured_log_and_audit, configuration_validation):
            scenario(directory)
    print('9 failure/recovery scenarios passed; owned resources closed.')


if __name__ == '__main__':
    main()
