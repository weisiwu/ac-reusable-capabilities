"""Bounded queue, Qt delivery, deadlines and owned-worker cleanup."""
import threading
import time
import pytest
pytest.importorskip('PyQt5')
from PyQt5.QtCore import QCoreApplication, QEvent, QThread
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QWidget
from ctf_desktop.background import BackgroundTaskRunner
from ctf_desktop.filters import LiveSearchComboBox


def until(predicate, milliseconds=2000):
    deadline=time.monotonic()+milliseconds/1000
    while not predicate() and time.monotonic()<deadline:QTest.qWait(5)
    assert predicate()


def test_result_and_error_delivery_are_on_gui_thread(qapp):
    runner=BackgroundTaskRunner();results=[];errors=[];workers=[]
    runner.succeeded.connect(lambda identity,value:results.append((identity,value,QThread.currentThread())))
    runner.failed.connect(lambda identity,error:errors.append((identity,error,QThread.currentThread())))
    try:
        identity=runner.submit(lambda event:workers.append(threading.get_ident()) or 7)
        until(lambda:len(results)==1)
        assert results==[(identity,7,qapp.thread())]
        assert workers[0]!=threading.get_ident()
        def fail(event):raise ValueError('sample')
        second=runner.submit(fail)
        until(lambda:len(errors)==1)
        assert errors[0][0]==second and isinstance(errors[0][1],ValueError) and errors[0][2]==qapp.thread()
    finally:runner.close()
    assert not runner._worker.thread.is_alive()


def test_only_latest_pending_operation_runs_and_stale_result_is_ignored(qapp):
    runner=BackgroundTaskRunner();entered=threading.Event();release=threading.Event();results=[];executed=[]
    runner.succeeded.connect(lambda *args:results.append(args))
    def first(cancel):
        entered.set();assert release.wait(2)
        assert cancel.is_set()
        return 'stale'
    try:
        runner.submit(first);assert entered.wait(1)
        for i in range(30):latest=runner.submit(lambda cancel,i=i:executed.append(i) or i)
        release.set()
        until(lambda:bool(results))
        assert results==[(latest,29)] and executed==[29]
    finally:release.set();runner.close()


def test_timeout_cancels_cooperatively_and_suppresses_late_result(qapp):
    runner=BackgroundTaskRunner();timed=[];succeeded=[];stopped=threading.Event()
    runner.timed_out.connect(timed.append);runner.succeeded.connect(lambda *args:succeeded.append(args))
    def work(cancel):
        assert cancel.wait(2)
        stopped.set()
        return 'too late'
    try:
        identity=runner.submit(work,timeout_ms=20)
        until(lambda:bool(timed));until(stopped.is_set)
        QTest.qWait(20)
        assert timed==[identity] and succeeded==[]
        runner.submit(lambda cancel:'recovered')
        until(lambda:bool(succeeded))
        assert succeeded[0][1]=='recovered'
    finally:runner.close()


def test_cancel_is_idempotent_close_rejects_new_work_and_joins(qapp):
    runner=BackgroundTaskRunner();entered=threading.Event();cancelled=[];results=[]
    runner.cancelled.connect(cancelled.append);runner.succeeded.connect(lambda *args:results.append(args))
    def work(cancel):entered.set();cancel.wait(2);return 5
    identity=runner.submit(work);assert entered.wait(1)
    runner.cancel();runner.cancel()
    runner.close(wait=False);runner.close(wait=True)
    qapp.processEvents()
    assert cancelled==[identity] and not results and not runner._worker.thread.is_alive()
    with pytest.raises(RuntimeError):runner.submit(lambda cancel:None)


def test_parent_destruction_cancels_and_releases_idle_worker(qapp):
    parent=QWidget();runner=BackgroundTaskRunner(parent);thread=runner._worker.thread
    parent.deleteLater();QCoreApplication.sendPostedEvents(None,QEvent.DeferredDelete)
    thread.join(timeout=2)
    assert not thread.is_alive()


@pytest.mark.parametrize('timeout',[0,-1,True,2**31])
def test_invalid_submit_does_not_cancel_active_work(qapp,timeout):
    runner=BackgroundTaskRunner();entered=threading.Event();release=threading.Event();results=[]
    runner.succeeded.connect(lambda *args:results.append(args))
    def work(cancel):entered.set();release.wait(2);assert not cancel.is_set();return 'kept'
    try:
        identity=runner.submit(work);assert entered.wait(1)
        with pytest.raises(ValueError):runner.submit(lambda cancel:0,timeout_ms=timeout)
        release.set();until(lambda:bool(results))
        assert results==[(identity,'kept')]
    finally:release.set();runner.close()


def test_search_request_ids_reject_same_text_old_results(qapp):
    combo=LiveSearchComboBox(delay_ms=10);requests=[]
    combo.request_started.connect(lambda *args:requests.append(args))
    QTest.keyClicks(combo.lineEdit(),'same');until(lambda:len(requests)==1)
    old,query=requests[-1]
    combo.lineEdit().selectAll();QTest.keyClicks(combo.lineEdit(),'same');until(lambda:len(requests)==2)
    current,_=requests[-1]
    assert current>old
    assert not combo.set_results(query,[(1,'old')],request_id=old)
    assert combo.set_results(query,[(2,'new')],request_id=current)
    assert combo.itemData(0)==2
    combo.hidePopup()


def test_parent_destruction_during_work_cancels_without_late_gui_delivery(qapp):
    parent=QWidget();runner=BackgroundTaskRunner(parent);started=threading.Event();results=[]
    runner.succeeded.connect(lambda *args:results.append(args))
    def work(cancel):started.set();assert cancel.wait(2);return 'late'
    runner.submit(work);assert started.wait(1)
    thread=runner._worker.thread
    parent.deleteLater();QCoreApplication.sendPostedEvents(None,QEvent.DeferredDelete)
    thread.join(timeout=2);qapp.processEvents()
    assert not thread.is_alive() and not results
