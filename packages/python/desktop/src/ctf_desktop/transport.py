"""Byte transport contract and an optional pyserial implementation."""

from dataclasses import dataclass
import math
from threading import RLock
from typing import Callable, Protocol


class Transport(Protocol):
    """Host-neutral open/close/read/write protocol; concrete implementations define timeout and concurrency semantics; no device commands.

    @ac-reusable
    @ac-capability desktop.transport.Transport
    @ac-kind capability
    @ac-tags desktop, transport, Transport
    @ac-contract Host-neutral open/close/read/write protocol; concrete implementations define timeout and concurrency semantics; no device commands.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected. pyserial >=3.5 only for default hardware factory.
    @ac-example See examples/desktop_demo.py and docs/contracts/transport.md.
    @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
    """
    def open(self) -> None:
        """Open underlying transport or raise its documented error; return None.

        @ac-reusable
        @ac-capability desktop.transport.Transport.open
        @ac-kind function
        @ac-tags desktop, transport, Transport
        @ac-contract Open underlying transport or raise its documented error; return None.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected. pyserial >=3.5 only for default hardware factory.
        @ac-example See examples/desktop_demo.py and docs/contracts/transport.md.
        @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
        """
        ...
    def close(self) -> None:
        """Release underlying transport resources; return None.

        @ac-reusable
        @ac-capability desktop.transport.Transport.close
        @ac-kind function
        @ac-tags desktop, transport, Transport
        @ac-contract Release underlying transport resources; return None.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected. pyserial >=3.5 only for default hardware factory.
        @ac-example See examples/desktop_demo.py and docs/contracts/transport.md.
        @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
        """
        ...
    def write(self, payload: bytes) -> None:
        """Submit complete payload or raise; return None, not a delivery acknowledgement.

        @ac-reusable
        @ac-capability desktop.transport.Transport.write
        @ac-kind function
        @ac-tags desktop, transport, Transport
        @ac-contract Submit complete payload or raise; return None, not a delivery acknowledgement.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected. pyserial >=3.5 only for default hardware factory.
        @ac-example See examples/desktop_demo.py and docs/contracts/transport.md.
        @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
        """
        ...
    def read(self, size: int) -> bytes:
        """Return up to size bytes; concrete transport defines timeout/error behavior.

        @ac-reusable
        @ac-capability desktop.transport.Transport.read
        @ac-kind function
        @ac-tags desktop, transport, Transport
        @ac-contract Return up to size bytes; concrete transport defines timeout/error behavior.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected. pyserial >=3.5 only for default hardware factory.
        @ac-example See examples/desktop_demo.py and docs/contracts/transport.md.
        @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
        """
        ...


class TransportError(IOError):
    """IOError for normalized open/read/write failures, chained to underlying cause where available.

    @ac-reusable
    @ac-capability desktop.transport.TransportError
    @ac-kind capability
    @ac-tags desktop, transport, TransportError
    @ac-contract IOError for normalized open/read/write failures, chained to underlying cause where available.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected. pyserial >=3.5 only for default hardware factory.
    @ac-example See examples/desktop_demo.py and docs/contracts/transport.md.
    @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
    """
    pass


@dataclass(frozen=True)
class SerialConfig:
    """Immutable nonblank string port, positive integer baudrate=9600, finite nonnegative numeric timeout=1.0 and write_timeout=1.0; invalid values raise ValueError.

    @ac-reusable
    @ac-capability desktop.transport.SerialConfig
    @ac-kind capability
    @ac-tags desktop, transport, SerialConfig
    @ac-contract Immutable nonblank string port, positive integer baudrate=9600, finite nonnegative numeric timeout=1.0 and write_timeout=1.0; invalid values raise ValueError.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected. pyserial >=3.5 only for default hardware factory.
    @ac-example See examples/desktop_demo.py and docs/contracts/transport.md.
    @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
    """
    port: str
    baudrate: int = 9600
    timeout: float = 1.0
    write_timeout: float = 1.0

    def __post_init__(self) -> None:
        valid_timeouts = all(type(value) in (int, float) and math.isfinite(value) and value >= 0 for value in (self.timeout, self.write_timeout))
        if not isinstance(self.port, str) or not self.port.strip() or type(self.baudrate) is not int or self.baudrate <= 0 or not valid_timeouts:
            raise ValueError("invalid serial configuration")


class SerialTransport:
    """Own one serial handle and RLock; optional factory injection; with opens and closes on every exit; device protocol and retries remain host-owned.

    @ac-reusable
    @ac-capability desktop.transport.SerialTransport
    @ac-kind capability
    @ac-tags desktop, transport, SerialTransport
    @ac-contract Own one serial handle and RLock; optional factory injection; with opens and closes on every exit; device protocol and retries remain host-owned.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected. pyserial >=3.5 only for default hardware factory.
    @ac-example See examples/desktop_demo.py and docs/contracts/transport.md.
    @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
    """

    def __init__(self, config: SerialConfig, factory: Callable | None = None):
        self.config = config
        self._factory = factory
        self._handle = None
        self._lock = RLock()

    def open(self) -> None:
        """Idempotently construct serial handle using config; lazy-import pyserial if no factory; TransportError on dependency/open failure.

        @ac-reusable
        @ac-capability desktop.transport.SerialTransport.open
        @ac-kind function
        @ac-tags desktop, transport, SerialTransport
        @ac-contract Idempotently construct serial handle using config; lazy-import pyserial if no factory; TransportError on dependency/open failure.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected. pyserial >=3.5 only for default hardware factory.
        @ac-example See examples/desktop_demo.py and docs/contracts/transport.md.
        @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
        """
        with self._lock:
            if self._handle is not None:
                return
            factory = self._factory
            if factory is None:
                try:
                    import serial
                except ImportError as error:
                    raise TransportError("pyserial is required for SerialTransport") from error
                factory = serial.Serial
            try:
                self._handle = factory(
                    port=self.config.port,
                    baudrate=self.config.baudrate,
                    timeout=self.config.timeout,
                    write_timeout=self.config.write_timeout,
                )
            except Exception as error:
                raise TransportError("serial open failed") from error

    def close(self) -> None:
        """Close handle under lock; release ownership only on success; normalize failure as TransportError and retain handle for cleanup retry; repeated successful close harmless.

        @ac-reusable
        @ac-capability desktop.transport.SerialTransport.close
        @ac-kind function
        @ac-tags desktop, transport, SerialTransport
        @ac-contract Close handle under lock; release ownership only on success; normalize failure as TransportError and retain handle for cleanup retry; repeated successful close harmless.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected. pyserial >=3.5 only for default hardware factory.
        @ac-example See examples/desktop_demo.py and docs/contracts/transport.md.
        @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
        """
        with self._lock:
            if self._handle is not None:
                try:
                    self._handle.close()
                except Exception as error:
                    # Retain ownership so callers can retry resource cleanup.
                    raise TransportError("serial close failed") from error
                self._handle = None

    def write(self, payload: bytes) -> None:
        """Convert payload to bytes, serialize IO, require complete write then flush; TransportError if closed/short write/backend fails; never retry.

        @ac-reusable
        @ac-capability desktop.transport.SerialTransport.write
        @ac-kind function
        @ac-tags desktop, transport, SerialTransport
        @ac-contract Convert payload to bytes, serialize IO, require complete write then flush; TransportError if closed/short write/backend fails; never retry.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected. pyserial >=3.5 only for default hardware factory.
        @ac-example See examples/desktop_demo.py and docs/contracts/transport.md.
        @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
        """
        data = bytes(payload)
        with self._lock:
            if self._handle is None:
                raise TransportError("serial port is closed")
            try:
                count = self._handle.write(data)
                if count != len(data):
                    raise TransportError("incomplete serial write")
                self._handle.flush()
            except TransportError:
                raise
            except Exception as error:
                raise TransportError("serial write failed") from error

    def read(self, size: int) -> bytes:
        """Require nonnegative integer size (bool rejected); serialize IO and return bytes; ValueError for invalid size and TransportError for closed/backend error.

        @ac-reusable
        @ac-capability desktop.transport.SerialTransport.read
        @ac-kind function
        @ac-tags desktop, transport, SerialTransport
        @ac-contract Require nonnegative integer size (bool rejected); serialize IO and return bytes; ValueError for invalid size and TransportError for closed/backend error.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected. pyserial >=3.5 only for default hardware factory.
        @ac-example See examples/desktop_demo.py and docs/contracts/transport.md.
        @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
        """
        if type(size) is not int or size < 0:
            raise ValueError("size must be a nonnegative integer")
        with self._lock:
            if self._handle is None:
                raise TransportError("serial port is closed")
            try:
                return bytes(self._handle.read(size))
            except Exception as error:
                raise TransportError("serial read failed") from error

    @property
    def is_open(self) -> bool:
        """Return owned handle open status under lock; false when no handle is owned.

        @ac-reusable
        @ac-capability desktop.transport.SerialTransport.is_open
        @ac-kind function
        @ac-tags desktop, transport, SerialTransport
        @ac-contract Return owned handle open status under lock; false when no handle is owned.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected. pyserial >=3.5 only for default hardware factory.
        @ac-example See examples/desktop_demo.py and docs/contracts/transport.md.
        @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
        """
        with self._lock:
            return self._handle is not None and bool(self._handle.is_open)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()
        return False
