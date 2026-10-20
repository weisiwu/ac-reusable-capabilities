"""Artifact-once batch preparation with explicit submission and cancellation."""

from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from threading import Event
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
    @ac-tests tests/test_core.py and tests/test_contracts.py
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
    @ac-tests tests/test_core.py and tests/test_contracts.py
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
    @ac-tests tests/test_core.py and tests/test_contracts.py
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
        @ac-tests tests/test_core.py and tests/test_contracts.py
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
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        return self._event.is_set()


class BatchPrintRunner:
    """Inject byte preparation and submission; own one executor; optional blocking GUI dispatcher and progress callback; call close at shutdown.

    @ac-reusable
    @ac-capability desktop.printing.BatchPrintRunner
    @ac-kind capability
    @ac-tags desktop, printing, BatchPrintRunner
    @ac-contract Inject byte preparation and submission; own one executor; optional blocking GUI dispatcher and progress callback; call close at shutdown.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected.
    @ac-example See examples/desktop_demo.py and docs/contracts/printing.md.
    @ac-tests tests/test_core.py and tests/test_contracts.py
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

    def run(self, items: Iterable[PrintItem], token: CancellationToken | None = None) -> BatchPrintResult:
        """Prepare once per plan item and submit each copy; stop at cancellation boundaries or first error; never retry uncertain submissions; progress errors are reported without reclassifying copies.

        @ac-reusable
        @ac-capability desktop.printing.BatchPrintRunner.run
        @ac-kind function
        @ac-tags desktop, printing, BatchPrintRunner
        @ac-contract Prepare once per plan item and submit each copy; stop at cancellation boundaries or first error; never retry uncertain submissions; progress errors are reported without reclassifying copies.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/printing.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
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

    def start(self, items: Iterable[PrintItem], token: CancellationToken | None = None) -> Future:
        """Snapshot plan then schedule run on owned worker; return Future; callbacks run there unless dispatch_submit synchronously marshals submission; no automatic retries.

        @ac-reusable
        @ac-capability desktop.printing.BatchPrintRunner.start
        @ac-kind function
        @ac-tags desktop, printing, BatchPrintRunner
        @ac-contract Snapshot plan then schedule run on owned worker; return Future; callbacks run there unless dispatch_submit synchronously marshals submission; no automatic retries.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/printing.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        planned = tuple(items)
        return self._executor.submit(self.run, planned, token)

    def close(self) -> None:
        """Wait for executor shutdown and cancel queued tasks; running host callbacks must terminate; no preemptive IO timeout.

        @ac-reusable
        @ac-capability desktop.printing.BatchPrintRunner.close
        @ac-kind function
        @ac-tags desktop, printing, BatchPrintRunner
        @ac-contract Wait for executor shutdown and cancel queued tasks; running host callbacks must terminate; no preemptive IO timeout.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/printing.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        self._executor.shutdown(wait=True, cancel_futures=True)
