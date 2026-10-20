"""Artifact-once batch preparation with explicit submission and cancellation."""

from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from threading import Event, Lock, get_ident
from typing import Callable, Iterable


@dataclass(frozen=True)
class PrintItem:
    """Immutable nonempty key and copies=1 positive integer (bool rejected); ValueError for invalid plan item.

    @ac-reusable
    @ac-capability desktop.printing.PrintItem
    @ac-kind capability
    @ac-tags desktop, printing, PrintItem
    @ac-contract Immutable nonempty key and copies=1 positive integer (bool rejected); ValueError for invalid plan item.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected.
    @ac-example See examples/desktop_demo.py and docs/contracts/printing.md.
    @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
    """
    key: str
    copies: int = 1

    def __post_init__(self) -> None:
        if not self.key or type(self.copies) is not int or self.copies < 1:
            raise ValueError("print key and copies must be valid")


@dataclass(frozen=True)
class BatchPrintResult:
    """Immutable total/succeeded/failed/skipped counters and optional error; counts describe submission, not physical paper output.

    @ac-reusable
    @ac-capability desktop.printing.BatchPrintResult
    @ac-kind capability
    @ac-tags desktop, printing, BatchPrintResult
    @ac-contract Immutable total/succeeded/failed/skipped counters and optional error; counts describe submission, not physical paper output.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected.
    @ac-example See examples/desktop_demo.py and docs/contracts/printing.md.
    @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
    """
    total: int
    succeeded: int
    failed: int
    skipped: int
    error: str | None = None


class CancellationToken:
    """Thread-safe cooperative flag initially false; no interrupts of in-flight host IO.

    @ac-reusable
    @ac-capability desktop.printing.CancellationToken
    @ac-kind capability
    @ac-tags desktop, printing, CancellationToken
    @ac-contract Thread-safe cooperative flag initially false; no interrupts of in-flight host IO.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected.
    @ac-example See examples/desktop_demo.py and docs/contracts/printing.md.
    @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
    """
    def __init__(self) -> None:
        self._event = Event()

    def cancel(self) -> None:
        """Set cancellation flag permanently; repeated calls are harmless and return None.

        @ac-reusable
        @ac-capability desktop.printing.CancellationToken.cancel
        @ac-kind function
        @ac-tags desktop, printing, CancellationToken
        @ac-contract Set cancellation flag permanently; repeated calls are harmless and return None.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/printing.md.
        @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
        """
        self._event.set()

    @property
    def cancelled(self) -> bool:
        """Read cooperative cancellation flag without mutation.

        @ac-reusable
        @ac-capability desktop.printing.CancellationToken.cancelled
        @ac-kind function
        @ac-tags desktop, printing, CancellationToken
        @ac-contract Read cooperative cancellation flag without mutation.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/printing.md.
        @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
        """
        return self._event.is_set()


class BatchPrintRunner:
    """Inject prepare and submit callbacks; own one executor and exclusive run state; with closes on exit; host supplies synchronous GUI dispatch and bounded IO.

    @ac-reusable
    @ac-capability desktop.printing.BatchPrintRunner
    @ac-kind capability
    @ac-tags desktop, printing, BatchPrintRunner
    @ac-contract Inject prepare and submit callbacks; own one executor and exclusive run state; with closes on exit; host supplies synchronous GUI dispatch and bounded IO.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected.
    @ac-example See examples/desktop_demo.py and docs/contracts/printing.md.
    @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
    """

    def __init__(
        self,
        prepare: Callable[[str], bytes],
        submit: Callable[[bytes], None],
        *,
        dispatch_submit: Callable[[Callable[[], None]], None] | None = None,
        on_progress: Callable[[str, int, int], None] | None = None,
    ):
        self.prepare = prepare
        self.submit = submit
        self.dispatch_submit = dispatch_submit or (lambda operation: operation())
        self.on_progress = on_progress or (lambda _key, _copy, _total: None)
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="ctf-print")
        self._run_lock = Lock()
        self._state_lock = Lock()
        self._closed = False
        self._running_thread = None

    def run(self, items: Iterable[PrintItem], token: CancellationToken | None = None) -> BatchPrintResult:
        """Exclusively prepare once per item and submit copies in order; RuntimeError on overlapping run or closed runner; cancel at boundaries, no retries; progress errors do not reclassify submissions.

        @ac-reusable
        @ac-capability desktop.printing.BatchPrintRunner.run
        @ac-kind function
        @ac-tags desktop, printing, BatchPrintRunner
        @ac-contract Exclusively prepare once per item and submit copies in order; RuntimeError on overlapping run or closed runner; cancel at boundaries, no retries; progress errors do not reclassify submissions.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/printing.md.
        @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
        """
        if not self._run_lock.acquire(blocking=False):
            raise RuntimeError("batch runner already running")
        try:
            with self._state_lock:
                if self._closed:
                    raise RuntimeError("batch runner is closed")
                self._running_thread = get_ident()
            return self._run_plan(items, token)
        finally:
            with self._state_lock:
                self._running_thread = None
            self._run_lock.release()

    def start(self, items: Iterable[PrintItem], token: CancellationToken | None = None) -> Future:
        """Snapshot plan then submit on owned single worker; return Future; reject closed runner; GUI dispatcher must synchronously finish submission; callbacks otherwise run on worker.

        @ac-reusable
        @ac-capability desktop.printing.BatchPrintRunner.start
        @ac-kind function
        @ac-tags desktop, printing, BatchPrintRunner
        @ac-contract Snapshot plan then submit on owned single worker; return Future; reject closed runner; GUI dispatcher must synchronously finish submission; callbacks otherwise run on worker.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/printing.md.
        @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
        """
        planned = tuple(items)
        with self._state_lock:
            if self._closed:
                raise RuntimeError("batch runner is closed")
            return self._executor.submit(self.run, planned, token)

    def close(self) -> None:
        """Mark closed, cancel queued futures and wait for executor plus any synchronous run; reject self-close from an active callback with RuntimeError; repeatable from owner thread; host IO must have finite completion.

        @ac-reusable
        @ac-capability desktop.printing.BatchPrintRunner.close
        @ac-kind function
        @ac-tags desktop, printing, BatchPrintRunner
        @ac-contract Mark closed, cancel queued futures and wait for executor plus any synchronous run; reject self-close from an active callback with RuntimeError; repeatable from owner thread; host IO must have finite completion.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/printing.md.
        @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
        """
        with self._state_lock:
            if self._running_thread == get_ident():
                raise RuntimeError("cannot close batch runner from its running callback")
            self._closed = True
        self._executor.shutdown(wait=True, cancel_futures=True)
        with self._run_lock:
            pass

    def _run_plan(self, items, token):
        planned = tuple(items)
        total = sum(item.copies for item in planned)
        succeeded = failed = 0
        progress_error = None
        token = token or CancellationToken()
        try:
            for item in planned:
                if token.cancelled:
                    break
                artifact = bytes(self.prepare(item.key))
                if not artifact:
                    raise ValueError(f"empty artifact for {item.key}")
                for copy_number in range(1, item.copies + 1):
                    if token.cancelled:
                        break
                    self.dispatch_submit(lambda artifact=artifact: self.submit(artifact))
                    succeeded += 1
                    try:
                        self.on_progress(item.key, copy_number, total)
                    except Exception as error:
                        progress_error = str(error)
            return BatchPrintResult(total, succeeded, failed, total - succeeded, progress_error)
        except Exception as error:
            failed = 1
            return BatchPrintResult(total, succeeded, failed, max(0, total - succeeded - failed), str(error))

    def __enter__(self):
        if self._closed:
            raise RuntimeError("batch runner is closed")
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()
        return False
