"""Explicit service ownership, dependency ordering and rollback."""

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class ServiceSpec:
    """Immutable name, registry-aware factory and dependency names (default empty); host owns service implementations.

    @ac-reusable
    @ac-capability desktop.services.ServiceSpec
    @ac-kind capability
    @ac-tags desktop, services, ServiceSpec
    @ac-contract Immutable name, registry-aware factory and dependency names (default empty); host owns service implementations.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected.
    @ac-example See examples/desktop_demo.py and docs/contracts/services.md.
    @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
    """
    name: str
    factory: Callable[["ServiceRegistry"], Any]
    depends_on: tuple[str, ...] = ()


class ServiceStartError(RuntimeError):
    """RuntimeError raised with original cause after start failure and attempted reverse cleanup.

    @ac-reusable
    @ac-capability desktop.services.ServiceStartError
    @ac-kind capability
    @ac-tags desktop, services, ServiceStartError
    @ac-contract RuntimeError raised with original cause after start failure and attempted reverse cleanup.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected.
    @ac-example See examples/desktop_demo.py and docs/contracts/services.md.
    @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
    """
    pass


class ServiceRegistry:
    """Own registered services, topological startup and reverse cleanup; with starts/stops; lifecycle callback reentry rejected; single-threaded registry.

    @ac-reusable
    @ac-capability desktop.services.ServiceRegistry
    @ac-kind capability
    @ac-tags desktop, services, ServiceRegistry
    @ac-contract Own registered services, topological startup and reverse cleanup; with starts/stops; lifecycle callback reentry rejected; single-threaded registry.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected.
    @ac-example See examples/desktop_demo.py and docs/contracts/services.md.
    @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
    """
    def __init__(self) -> None:
        self._specs: dict[str, ServiceSpec] = {}
        self._instances: dict[str, Any] = {}
        self._started: list[str] = []
        self._starting = self._stopping = False

    def register(self, spec: ServiceSpec) -> None:
        """Register unique ServiceSpec before start; ValueError for duplicate/running registry; RuntimeError during start/stop callbacks; no lazy initialization.

        @ac-reusable
        @ac-capability desktop.services.ServiceRegistry.register
        @ac-kind function
        @ac-tags desktop, services, ServiceRegistry
        @ac-contract Register unique ServiceSpec before start; ValueError for duplicate/running registry; RuntimeError during start/stop callbacks; no lazy initialization.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/services.md.
        @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
        """
        if self._starting or self._stopping:
            raise RuntimeError("registry lifecycle transition in progress")
        if spec.name in self._specs or self._started:
            raise ValueError("duplicate service or registry already started")
        self._specs[spec.name] = spec

    def _order(self) -> list[str]:
        state: dict[str, int] = {}
        ordered: list[str] = []

        def visit(name: str) -> None:
            if name not in self._specs:
                raise ValueError(f"missing dependency: {name}")
            if state.get(name) == 1:
                raise ValueError(f"service dependency cycle at {name}")
            if state.get(name) == 2:
                return
            state[name] = 1
            for dependency in self._specs[name].depends_on:
                visit(dependency)
            state[name] = 2
            ordered.append(name)

        for name in self._specs:
            visit(name)
        return ordered

    def start(self) -> None:
        """Topologically validate dependencies, start instances and rollback on error; lifecycle callback reentry rejected; ServiceStartError chains original failure and notes cleanup failure.

        @ac-reusable
        @ac-capability desktop.services.ServiceRegistry.start
        @ac-kind function
        @ac-tags desktop, services, ServiceRegistry
        @ac-contract Topologically validate dependencies, start instances and rollback on error; lifecycle callback reentry rejected; ServiceStartError chains original failure and notes cleanup failure.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/services.md.
        @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
        """
        if self._starting or self._stopping or self._started:
            raise RuntimeError("registry already started or changing state")
        self._starting = True
        try:
            order = self._order()
            for name in order:
                try:
                    instance = self._specs[name].factory(self)
                    self._instances[name] = instance
                    self._started.append(name)
                    starter = getattr(instance, "start", None)
                    if callable(starter):
                        starter()
                except Exception as error:
                    self._starting = False
                    try:
                        self.stop()
                    except RuntimeError as cleanup_error:
                        error.add_note(f"Service rollback also failed: {cleanup_error}")
                    raise ServiceStartError(f"failed to start {name}") from error
        finally:
            self._starting = False

    def get(self, name: str) -> Any:
        """Return current instance by name or raise KeyError; never lazily create services.

        @ac-reusable
        @ac-capability desktop.services.ServiceRegistry.get
        @ac-kind function
        @ac-tags desktop, services, ServiceRegistry
        @ac-contract Return current instance by name or raise KeyError; never lazily create services.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/services.md.
        @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
        """
        return self._instances[name]

    def stop(self) -> None:
        """Attempt every reverse-order cleanup including stop attribute lookup; always clear ownership, then raise RuntimeError from first failure; reentry rejected; idle stop harmless.

        @ac-reusable
        @ac-capability desktop.services.ServiceRegistry.stop
        @ac-kind function
        @ac-tags desktop, services, ServiceRegistry
        @ac-contract Attempt every reverse-order cleanup including stop attribute lookup; always clear ownership, then raise RuntimeError from first failure; reentry rejected; idle stop harmless.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/services.md.
        @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
        """
        if self._starting or self._stopping:
            raise RuntimeError("registry lifecycle transition in progress")
        self._stopping = True
        first_error = None
        try:
            for name in reversed(self._started):
                try:
                    stopper = getattr(self._instances[name], "stop", None)
                    if callable(stopper):
                        stopper()
                except Exception as error:
                    first_error = first_error or error
        finally:
            self._started.clear()
            self._instances.clear()
            self._stopping = False
        if first_error:
            raise RuntimeError("one or more services failed to stop") from first_error

    @property
    def running(self) -> bool:
        """Return whether registry owns any started services; does not inspect worker health.

        @ac-reusable
        @ac-capability desktop.services.ServiceRegistry.running
        @ac-kind function
        @ac-tags desktop, services, ServiceRegistry
        @ac-contract Return whether registry owns any started services; does not inspect worker health.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/services.md.
        @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
        """
        return bool(self._started)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.stop()
        return False
