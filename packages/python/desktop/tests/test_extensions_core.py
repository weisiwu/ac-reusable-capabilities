from pathlib import Path
import logging
import sqlite3
from contextlib import closing
import pytest
from ctf_desktop.diagnostics import configure_json_logger
from ctf_desktop.printing import BatchPrintRunner,PrintItem
from ctf_desktop.services import ServiceRegistry,ServiceSpec
from ctf_desktop.storage import SqliteStore,Migration
from ctf_desktop.transport import SerialTransport,SerialConfig


def test_context_managers_release_resources_on_failure(tmp_path):
    path=tmp_path/'context.sqlite'
    with pytest.raises(ValueError):
        with SqliteStore(path) as store:
            store.migrate([Migration(1,lambda db:db.execute('CREATE TABLE items (id INTEGER)'))])
            store.connect().execute('INSERT INTO items VALUES (1)')
            connection=store.connect()
            raise ValueError('application failed')
    with pytest.raises(sqlite3.ProgrammingError):connection.execute('SELECT 1')
    with closing(sqlite3.connect(path)) as check:assert check.execute('SELECT * FROM items').fetchall()==[]
    events=[]
    class Service:
        def stop(self):events.append('stopped')
    registry=ServiceRegistry();registry.register(ServiceSpec('sample',lambda registry:Service()))
    with pytest.raises(ValueError):
        with registry:
            assert registry.running
            raise ValueError('application failed')
    assert events==['stopped'] and not registry.running
    class Handle:
        is_open=True
        def __init__(self,**kwargs):pass
        def close(self):self.is_open=False
    with SerialTransport(SerialConfig('sample'),Handle) as transport:assert transport.is_open
    assert not transport.is_open
    with BatchPrintRunner(lambda key:b'pdf',lambda data:None) as runner:
        assert runner.start([PrintItem('sample')]).result(timeout=2).succeeded==1
    with pytest.raises(RuntimeError):runner.run([])


def test_rotating_logger_bounds_retained_files_and_keeps_redaction(tmp_path):
    path=tmp_path/'rotating.jsonl';logger=configure_json_logger('review-rotation',path,max_bytes=160,backup_count=2)
    try:
        for i in range(12):logger.info('sample operation',extra={'data':{'token':'secret-token-value','index':i}})
        files=list(tmp_path.glob('rotating.jsonl*'))
        assert len(files)==3 and {p.name for p in files}=={'rotating.jsonl','rotating.jsonl.1','rotating.jsonl.2'}
        assert all('secret-token-value' not in p.read_text() for p in files)
        assert configure_json_logger('review-rotation',path,max_bytes=320,backup_count=2) is logger
        assert len(logger.handlers)==1 and logger.handlers[0].maxBytes==320
    finally:
        for handler in list(logger.handlers):handler.close();logger.removeHandler(handler)


@pytest.mark.parametrize('kwargs',[{'max_bytes':-1},{'max_bytes':True},{'max_bytes':50,'backup_count':0},{'backup_count':-1}])
def test_invalid_rotation_does_not_create_files(tmp_path,kwargs):
    with pytest.raises(ValueError):configure_json_logger('invalid-rotation',tmp_path/'new.jsonl',**kwargs)
    assert list(tmp_path.iterdir())==[]


def test_print_close_waits_for_synchronous_run_owned_by_another_thread():
    import threading
    entered,release,closed=threading.Event(),threading.Event(),threading.Event()
    def prepare(key):entered.set();assert release.wait(2);return b'pdf'
    runner=BatchPrintRunner(prepare,lambda artifact:None)
    thread=threading.Thread(target=lambda:runner.run([PrintItem('sample')]))
    closer=threading.Thread(target=lambda:(runner.close(),closed.set()))
    try:
        thread.start();assert entered.wait(1)
        closer.start();assert not closed.wait(0.03)
        release.set();thread.join(2);closer.join(2)
        assert closed.is_set() and not thread.is_alive() and not closer.is_alive()
    finally:
        release.set();thread.join(2)
        if closer.ident is not None:closer.join(2)
        runner.close()


def test_print_callback_cannot_close_its_own_active_run():
    errors=[]
    runner=None
    def progress(*args):
        try:runner.close()
        except RuntimeError as error:errors.append(str(error))
    with BatchPrintRunner(lambda key:b'pdf',lambda data:None,on_progress=progress) as runner:
        assert runner.run([PrintItem('sample')]).succeeded==1
    assert errors and 'callback' in errors[0]
