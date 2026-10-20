"""Entity-neutral CRUD coordination; persistence and validation are injected."""

from typing import Any, Callable, Mapping, Protocol

from .query import PageRequest, PageResult


class CrudRepository(Protocol):
    """Host-owned list/get/create/update/delete protocol; transaction and identity semantics belong to the host.

    @ac-reusable
    @ac-capability desktop.crud.CrudRepository
    @ac-kind capability
    @ac-tags desktop, crud, CrudRepository
    @ac-contract Host-owned list/get/create/update/delete protocol; transaction and identity semantics belong to the host.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected.
    @ac-example See examples/desktop_demo.py and docs/contracts/crud.md.
    @ac-tests tests/test_core.py and tests/test_contracts.py
    """
    def list_page(self, request: PageRequest, filters: Mapping[str, Any]) -> PageResult:
        """Return PageResult for PageRequest and filter mapping; host owns filtering and IO errors.

        @ac-reusable
        @ac-capability desktop.crud.CrudRepository.list_page
        @ac-kind function
        @ac-tags desktop, crud, CrudRepository
        @ac-contract Return PageResult for PageRequest and filter mapping; host owns filtering and IO errors.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/crud.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        ...
    def get(self, identity: Any) -> Mapping[str, Any] | None:
        """Return record mapping or None for identity; host owns IO errors.

        @ac-reusable
        @ac-capability desktop.crud.CrudRepository.get
        @ac-kind function
        @ac-tags desktop, crud, CrudRepository
        @ac-contract Return record mapping or None for identity; host owns IO errors.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/crud.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        ...
    def create(self, values: Mapping[str, Any]) -> Any:
        """Persist supplied mapping and return its identity; host owns transaction/errors.

        @ac-reusable
        @ac-capability desktop.crud.CrudRepository.create
        @ac-kind function
        @ac-tags desktop, crud, CrudRepository
        @ac-contract Persist supplied mapping and return its identity; host owns transaction/errors.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/crud.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        ...
    def update(self, identity: Any, values: Mapping[str, Any]) -> None:
        """Update identity using values and return None; host defines missing-row behavior.

        @ac-reusable
        @ac-capability desktop.crud.CrudRepository.update
        @ac-kind function
        @ac-tags desktop, crud, CrudRepository
        @ac-contract Update identity using values and return None; host defines missing-row behavior.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/crud.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        ...
    def delete(self, identity: Any) -> None:
        """Delete identity and return None; host defines missing-row behavior.

        @ac-reusable
        @ac-capability desktop.crud.CrudRepository.delete
        @ac-kind function
        @ac-tags desktop, crud, CrudRepository
        @ac-contract Delete identity and return None; host defines missing-row behavior.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/crud.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        ...


class CrudController:
    """Require repository and explicit authorization callback; optional validation/change callbacks; no UI or persistence implementation.

    @ac-reusable
    @ac-capability desktop.crud.CrudController
    @ac-kind capability
    @ac-tags desktop, crud, CrudController
    @ac-contract Require repository and explicit authorization callback; optional validation/change callbacks; no UI or persistence implementation.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected.
    @ac-example See examples/desktop_demo.py and docs/contracts/crud.md.
    @ac-tests tests/test_core.py and tests/test_contracts.py
    """

    def __init__(
        self,
        repository: CrudRepository,
        *,
        authorize: Callable[[str, Any], None],
        validate: Callable[[Mapping[str, Any]], None] | None = None,
        changed: Callable[[str, Any], None] | None = None,
    ):
        self.repository = repository
        self.validate = validate or (lambda _values: None)
        self.authorize = authorize
        self.changed = changed or (lambda _action, _identity: None)

    def list_page(self, request: PageRequest, filters: Mapping[str, Any] | None = None) -> PageResult:
        """Authorize list before repository access; None filters become empty mapping; return PageResult; errors propagate.

        @ac-reusable
        @ac-capability desktop.crud.CrudController.list_page
        @ac-kind function
        @ac-tags desktop, crud, CrudController
        @ac-contract Authorize list before repository access; None filters become empty mapping; return PageResult; errors propagate.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/crud.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        self.authorize("list", None)
        return self.repository.list_page(request, filters or {})

    def detail(self, identity: Any) -> Mapping[str, Any] | None:
        """Authorize read on identity before repository get; return mapping or None; errors propagate.

        @ac-reusable
        @ac-capability desktop.crud.CrudController.detail
        @ac-kind function
        @ac-tags desktop, crud, CrudController
        @ac-contract Authorize read on identity before repository get; return mapping or None; errors propagate.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/crud.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        self.authorize("read", identity)
        return self.repository.get(identity)

    def create(self, values: Mapping[str, Any]) -> Any:
        """Authorize create, validate, write then notify changed; return identity; errors propagate; notification failure cannot roll back host write.

        @ac-reusable
        @ac-capability desktop.crud.CrudController.create
        @ac-kind function
        @ac-tags desktop, crud, CrudController
        @ac-contract Authorize create, validate, write then notify changed; return identity; errors propagate; notification failure cannot roll back host write.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/crud.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        self.authorize("create", None)
        self.validate(values)
        identity = self.repository.create(values)
        self.changed("create", identity)
        return identity

    def update(self, identity: Any, values: Mapping[str, Any]) -> None:
        """Authorize update, validate, write then notify changed; return None; errors propagate, no implicit transaction.

        @ac-reusable
        @ac-capability desktop.crud.CrudController.update
        @ac-kind function
        @ac-tags desktop, crud, CrudController
        @ac-contract Authorize update, validate, write then notify changed; return None; errors propagate, no implicit transaction.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/crud.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        self.authorize("update", identity)
        self.validate(values)
        self.repository.update(identity, values)
        self.changed("update", identity)

    def delete(self, identity: Any) -> None:
        """Authorize delete before write then notify changed; return None; errors propagate, no implicit transaction.

        @ac-reusable
        @ac-capability desktop.crud.CrudController.delete
        @ac-kind function
        @ac-tags desktop, crud, CrudController
        @ac-contract Authorize delete before write then notify changed; return None; errors propagate, no implicit transaction.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/crud.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        self.authorize("delete", identity)
        self.repository.delete(identity)
        self.changed("delete", identity)
