"""Validated pagination and parameterized SQL predicates."""

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class PageRequest:
    """Immutable number=1 and size=20; require positive integers (bool rejected), else ValueError; no IO.

    @ac-reusable
    @ac-capability desktop.query.PageRequest
    @ac-kind capability
    @ac-tags desktop, query, PageRequest
    @ac-contract Immutable number=1 and size=20; require positive integers (bool rejected), else ValueError; no IO.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected.
    @ac-example See examples/desktop_demo.py and docs/contracts/query.md.
    @ac-tests tests/test_core.py and tests/test_contracts.py
    """
    number: int = 1
    size: int = 20

    def __post_init__(self) -> None:
        if type(self.number) is not int or type(self.size) is not int or self.number < 1 or self.size < 1:
            raise ValueError("page number and size must be positive integers")

    @property
    def offset(self) -> int:
        """Return zero-based (number-1)*size without changing state.

        @ac-reusable
        @ac-capability desktop.query.PageRequest.offset
        @ac-kind function
        @ac-tags desktop, query, PageRequest
        @ac-contract Return zero-based (number-1)*size without changing state.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/query.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        return (self.number - 1) * self.size


@dataclass(frozen=True)
class PageResult:
    """Immutable items tuple, nonnegative integer total and PageRequest; reject negative/noninteger totals; no IO.

    @ac-reusable
    @ac-capability desktop.query.PageResult
    @ac-kind capability
    @ac-tags desktop, query, PageResult
    @ac-contract Immutable items tuple, nonnegative integer total and PageRequest; reject negative/noninteger totals; no IO.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected.
    @ac-example See examples/desktop_demo.py and docs/contracts/query.md.
    @ac-tests tests/test_core.py and tests/test_contracts.py
    """
    items: tuple[Any, ...]
    total: int
    request: PageRequest

    def __post_init__(self) -> None:
        if type(self.total) is not int or self.total < 0:
            raise ValueError("total must be a nonnegative integer")

    @property
    def pages(self) -> int:
        """Return ceiling(total/size), at least one page even for an empty result.

        @ac-reusable
        @ac-capability desktop.query.PageResult.pages
        @ac-kind function
        @ac-tags desktop, query, PageResult
        @ac-contract Return ceiling(total/size), at least one page even for an empty result.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/query.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        return max(1, (self.total + self.request.size - 1) // self.request.size)


class SqlWhere:
    """Copy a caller-trusted column whitelist; accumulate SQLite ? predicates and bound values; never execute SQL.

    @ac-reusable
    @ac-capability desktop.query.SqlWhere
    @ac-kind capability
    @ac-tags desktop, query, SqlWhere
    @ac-contract Copy a caller-trusted column whitelist; accumulate SQLite ? predicates and bound values; never execute SQL.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected.
    @ac-example See examples/desktop_demo.py and docs/contracts/query.md.
    @ac-tests tests/test_core.py and tests/test_contracts.py
    """

    def __init__(self, columns: Mapping[str, str]):
        self._columns = dict(columns)
        self._parts: list[str] = []
        self._values: list[Any] = []

    def _column(self, field: str) -> str:
        try:
            return self._columns[field]
        except KeyError as error:
            raise ValueError(f"unknown filter field: {field}") from error

    def equal(self, field: str, value: Any) -> "SqlWhere":
        """Skip None/empty text; otherwise whitelist field or raise ValueError, append equality and return self.

        @ac-reusable
        @ac-capability desktop.query.SqlWhere.equal
        @ac-kind function
        @ac-tags desktop, query, SqlWhere
        @ac-contract Skip None/empty text; otherwise whitelist field or raise ValueError, append equality and return self.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/query.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        if value is not None and value != "":
            self._parts.append(f"{self._column(field)} = ?")
            self._values.append(value)
        return self

    def contains(self, field: str, value: str) -> "SqlWhere":
        """Skip empty text; whitelist field, escape literal percent/underscore/backslash, append LIKE and return self.

        @ac-reusable
        @ac-capability desktop.query.SqlWhere.contains
        @ac-kind function
        @ac-tags desktop, query, SqlWhere
        @ac-contract Skip empty text; whitelist field, escape literal percent/underscore/backslash, append LIKE and return self.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/query.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        if value:
            escaped = str(value).replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            self._parts.append(f"{self._column(field)} LIKE ? ESCAPE '\\'")
            self._values.append(f"%{escaped}%")
        return self

    def range(self, field: str, start: Any = None, end: Any = None) -> "SqlWhere":
        """Whitelist field even for empty bounds; append inclusive start and exclusive end when not None; return self.

        @ac-reusable
        @ac-capability desktop.query.SqlWhere.range
        @ac-kind function
        @ac-tags desktop, query, SqlWhere
        @ac-contract Whitelist field even for empty bounds; append inclusive start and exclusive end when not None; return self.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/query.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        column = self._column(field)
        if start is not None:
            self._parts.append(f"{column} >= ?")
            self._values.append(start)
        if end is not None:
            self._parts.append(f"{column} < ?")
            self._values.append(end)
        return self

    def build(self) -> tuple[str, tuple[Any, ...]]:
        """Return detached (WHERE text, bound-value tuple); empty builder returns empty text and tuple; repeatable without mutation.

        @ac-reusable
        @ac-capability desktop.query.SqlWhere.build
        @ac-kind function
        @ac-tags desktop, query, SqlWhere
        @ac-contract Return detached (WHERE text, bound-value tuple); empty builder returns empty text and tuple; repeatable without mutation.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/query.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        return ("WHERE " + " AND ".join(self._parts) if self._parts else "", tuple(self._values))
