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
    @ac-tests tests/test_core.py and tests/test_contracts.py
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
    @ac-tests tests/test_core.py and tests/test_contracts.py
    """
    pass


class ServiceRegistry:
    """Own registered instances; topologically start dependencies then reverse-stop; single-threaded registry, no global singleton.

    @ac-reusable
    @ac-capability desktop.services.ServiceRegistry
    @ac-kind capability
    @ac-tags desktop, services, ServiceRegistry
    @ac-contract Own registered instances; topologically start dependencies then reverse-stop; single-threaded registry, no global singleton.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected.
    @ac-example See examples/desktop_demo.py and docs/contracts/services.md.
    @ac-tests tests/test_core.py and tests/test_contracts.py
    """
    def __init__(self) -> None:
        self._specs: dict[str, ServiceSpec] = {}
        self._instances: dict[str, Any] = {}
        self._started: list[str] = []

    def register(self, spec: ServiceSpec) -> None:
        """Register unique ServiceSpec before start; ValueError for duplicate or started registry.

        @ac-reusable
        @ac-capability desktop.services.ServiceRegistry.register
        @ac-kind function
        @ac-tags desktop, services, ServiceRegistry
        @ac-contract Register unique ServiceSpec before start; ValueError for duplicate or started registry.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/services.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
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
        """Validate missing/cyclic dependencies before side effects; invoke factories/start hooks; failure triggers cleanup then ServiceStartError; duplicate start raises RuntimeError.

        @ac-reusable
        @ac-capability desktop.services.ServiceRegistry.start
        @ac-kind function
        @ac-tags desktop, services, ServiceRegistry
        @ac-contract Validate missing/cyclic dependencies before side effects; invoke factories/start hooks; failure triggers cleanup then ServiceStartError; duplicate start raises RuntimeError.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/services.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        if self._started:
            raise RuntimeError("registry already started")
        order = self._order()
        try:
            for name in order:
                instance = self._specs[name].factory(self)
                self._instances[name] = instance
                self._started.append(name)
                starter = getattr(instance, "start", None)
                if callable(starter):
                    starter()
        except Exception as error:
            try:
                self.stop()
            except RuntimeError:
                pass
            raise ServiceStartError(f"failed to start {name}") from error

    def get(self, name: str) -> Any:
        """Return current instance by name or raise KeyError; never lazily create services.

        @ac-reusable
        @ac-capability desktop.services.ServiceRegistry.get
        @ac-kind function
        @ac-tags desktop, services, ServiceRegistry
        @ac-contract Return current instance by name or raise KeyError; never lazily create services.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/services.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        return self._instances[name]

    def stop(self) -> None:
        """Stop all started instances in reverse order, clear ownership; stop-hook exceptions produce RuntimeError after remaining hooks; repeated stop is harmless.

        @ac-reusable
        @ac-capability desktop.services.ServiceRegistry.stop
        @ac-kind function
        @ac-tags desktop, services, ServiceRegistry
        @ac-contract Stop all started instances in reverse order, clear ownership; stop-hook exceptions produce RuntimeError after remaining hooks; repeated stop is harmless.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/services.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        first_error = None
        for name in reversed(self._started):
            stopper = getattr(self._instances[name], "stop", None)
            try:
                if callable(stopper):
                    stopper()
            except Exception as error:
                first_error = first_error or error
        self._started.clear()
        self._instances.clear()
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
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        return bool(self._started)
