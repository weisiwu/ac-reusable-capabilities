"""Bounded latest-request background work with Qt-thread result delivery."""
from threading import Condition, Event, Thread, current_thread
from typing import Any, Callable
import weakref

from PyQt5.QtCore import QObject, QTimer, pyqtSignal


class _LatestWorker:
    def __init__(self, deliver):
        self.deliver = deliver
        self.condition = Condition()
        self.pending = None
        self.current_event = None
        self.closed = False
        self.thread = Thread(target=self._run, name=f'ctf-background-{id(self):x}', daemon=True)
        self.thread.start()

    def submit(self, identity, operation, cancel_event):
        with self.condition:
            if self.closed:
                raise RuntimeError('background worker is closed')
            if self.current_event is not None:
                self.current_event.set()
            if self.pending is not None:
                self.pending[2].set()
            self.pending = (identity, operation, cancel_event)
            self.condition.notify()

    def cancel(self):
        with self.condition:
            if self.current_event is not None:
                self.current_event.set()
            if self.pending is not None:
                self.pending[2].set()
                self.pending = None

    def close(self, wait):
        with self.condition:
            self.closed = True
            self.cancel()
            self.condition.notify_all()
        if wait:
            if current_thread() is self.thread:
                raise RuntimeError('cannot join background worker from its operation')
            self.thread.join()

    def _run(self):
        while True:
            with self.condition:
                self.condition.wait_for(lambda: self.closed or self.pending is not None)
                if self.closed:
                    return
                identity, operation, cancel_event = self.pending
                self.pending = None
                self.current_event = cancel_event
            value = error = None
            try:
                value = operation(cancel_event)
            except BaseException as failure:
                error = failure
            finally:
                with self.condition:
                    self.current_event = None
            self.deliver(identity, value, error)


class BackgroundTaskRunner(QObject):
    """Qt-thread owned latest-request runner with one active worker and one replaceable pending slot; operation(Event) owns bounded IO; succeeded/failed/cancelled/timed_out signals; explicit close or parent destruction cancels; no forced termination.

    @ac-reusable
    @ac-capability desktop.background.BackgroundTaskRunner
    @ac-kind component
    @ac-tags desktop, async, cancellation, timeout, latest-wins, GUI
    @ac-contract Qt-thread owned latest-request runner with one active worker and one replaceable pending slot; operation(Event) owns bounded IO; succeeded/failed/cancelled/timed_out signals; explicit close or parent destruction cancels; no forced termination.
        operation(Event) runs on one worker. Latest results/errors are delivered
        on Qt thread via succeeded(id,value)/failed(id,error). Replacing work
        cancels prior work cooperatively; cancelled(id)/timed_out(id) are distinct.
        Timeout suppresses late results, not native/preemptive thread execution.
        At most one task waits behind active work; no unbounded executor queue.
    @ac-dependencies Python >=3.11, PyQt5 >=5.15; operation owns worker resources.
    @ac-example See examples/background_search.py and docs/guides/background.md.
    @ac-tests tests/test_background.py
    """
    succeeded = pyqtSignal(int, object)
    failed = pyqtSignal(int, object)
    cancelled = pyqtSignal(int)
    timed_out = pyqtSignal(int)
    _completed = pyqtSignal(int, object, object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._generation = 0
        self._active = False
        self._closed = False
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._timeout)
        self._completed.connect(self._deliver)
        reference = weakref.ref(self)
        def deliver(identity, value, error):
            owner = reference()
            if owner is not None:
                try:
                    owner._completed.emit(identity, value, error)
                except RuntimeError:
                    # The QObject parent may have been destroyed during work.
                    pass
        self._worker = _LatestWorker(deliver)
        worker = self._worker
        self.destroyed.connect(lambda: worker.close(False))

    def submit(self, operation: Callable[[Event], Any], *, timeout_ms: int | None = None) -> int:
        """Schedule latest work and return its generation, superseding older work.

        @ac-reusable
        @ac-capability desktop.background.BackgroundTaskRunner.submit
        @ac-kind function
        @ac-tags async, latest-wins, cancellation, timeout
        @ac-contract Require callable operation and optional positive integer
            timeout_ms within Qt int range; invalid input raises before mutation.
            Closed runner raises RuntimeError. Operation must observe Event and
            use bounded external IO; it must never access Qt widgets. Commit
            replacement before cancelled notification; reentrant submissions win.
            Return this call's generation even if a slot submits again or closes.
        @ac-dependencies PyQt5; operation supplies and closes its own IO handles.
        @ac-example See examples/background_search.py.
        @ac-tests tests/test_background.py
        """
        if self._closed:
            raise RuntimeError('background runner is closed')
        if not callable(operation) or (timeout_ms is not None and (type(timeout_ms) is not int or not 0 < timeout_ms <= 2_147_483_647)):
            raise ValueError('operation must be callable and timeout_ms a positive Qt integer')
        previous = self._generation if self._active else None
        self._timer.stop()
        self._worker.cancel()
        self._generation += 1
        identity = self._generation
        self._active = True
        self._worker.submit(identity, operation, Event())
        if timeout_ms is not None:
            self._timer.start(timeout_ms)
        # Direct Qt slots may submit newer work or close us. Finish the state
        # transition first, and never overwrite their changes after notification.
        if previous is not None:
            self.cancelled.emit(previous)
        return identity

    def cancel(self) -> None:
        """Cooperatively cancel active/pending work and suppress its late result.

        @ac-reusable
        @ac-capability desktop.background.BackgroundTaskRunner.cancel
        @ac-kind function
        @ac-tags async, cancellation, lifecycle
        @ac-contract Stop deadline timer, cancel pending slot and signal active
            worker Event; emit cancelled(id) once if UI considers a task active.
            Does not interrupt in-flight IO; repeated idle cancel is harmless.
        @ac-dependencies PyQt5; caller invokes on Qt thread.
        @ac-example See examples/background_search.py.
        @ac-tests tests/test_background.py
        """
        self._timer.stop()
        self._worker.cancel()
        if self._active:
            self._active = False
            self.cancelled.emit(self._generation)

    def close(self, *, wait: bool = True) -> None:
        """Cancel owned work and close the worker; wait for cleanup by default.

        @ac-reusable
        @ac-capability desktop.background.BackgroundTaskRunner.close
        @ac-kind function
        @ac-tags async, resource-cleanup, shutdown
        @ac-contract Mark closed, suppress further results and cancel work.
            wait=True joins worker; only safe with cooperative, bounded IO and
            outside worker callbacks. wait=False returns before worker cleanup;
            a later close(wait=True) can join. QObject destruction also cancels
            without blocking. No unsafe thread termination or silent restart.
        @ac-dependencies PyQt5 and threading; application owns task IO timeouts.
        @ac-example See examples/background_search.py.
        @ac-tests tests/test_background.py
        """
        if not self._closed:
            self._closed = True
            self.cancel()
        self._worker.close(wait)

    def _timeout(self):
        if self._active:
            self._active = False
            self._worker.cancel()
            self.timed_out.emit(self._generation)

    def _deliver(self, identity, value, error):
        if self._closed or not self._active or identity != self._generation:
            return
        self._active = False
        self._timer.stop()
        if error is None:
            self.succeeded.emit(identity, value)
        else:
            self.failed.emit(identity, error)
