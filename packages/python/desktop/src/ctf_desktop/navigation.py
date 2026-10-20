"""Lazy page registry with one page instance per route and lifecycle hooks."""

from dataclasses import dataclass
from typing import Callable

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout, QListWidget, QStackedWidget, QWidget


@dataclass(frozen=True)
class PageSpec:
    """Immutable route key/title and no-argument QWidget factory; host defines page on_enter/on_leave/dispose hooks.

    @ac-reusable
    @ac-capability desktop.navigation.PageSpec
    @ac-kind component
    @ac-tags desktop, navigation, PageSpec
    @ac-contract Immutable route key/title and no-argument QWidget factory; host defines page on_enter/on_leave/dispose hooks.
    @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
    @ac-example See examples/desktop_demo.py and docs/contracts/navigation.md.
    @ac-tests tests/test_qt.py and tests/test_qt_contracts.py
    """
    key: str
    title: str
    create: Callable[[], QWidget]


class PageHost(QWidget):
    """GUI-thread registry caching one widget per route; page_changed(str) after successful navigation; caller invokes dispose before shutdown.

    @ac-reusable
    @ac-capability desktop.navigation.PageHost
    @ac-kind component
    @ac-tags desktop, navigation, PageHost
    @ac-contract GUI-thread registry caching one widget per route; page_changed(str) after successful navigation; caller invokes dispose before shutdown.
    @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
    @ac-example See examples/desktop_demo.py and docs/contracts/navigation.md.
    @ac-tests tests/test_qt.py and tests/test_qt_contracts.py
    """
    page_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.sidebar = QListWidget(self)
        self.stack = QStackedWidget(self)
        self._specs: dict[str, PageSpec] = {}
        self._pages: dict[str, QWidget] = {}
        self._current: str | None = None
        layout = QHBoxLayout(self)
        layout.addWidget(self.sidebar)
        layout.addWidget(self.stack, 1)
        self.sidebar.currentRowChanged.connect(self._on_row_changed)

    def register(self, spec: PageSpec) -> None:
        """Add nonempty unique route and sidebar item; ValueError for invalid/duplicate key; does not construct page.

        @ac-reusable
        @ac-capability desktop.navigation.PageHost.register
        @ac-kind function
        @ac-tags desktop, navigation, PageHost
        @ac-contract Add nonempty unique route and sidebar item; ValueError for invalid/duplicate key; does not construct page.
        @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
        @ac-example See examples/desktop_demo.py and docs/contracts/navigation.md.
        @ac-tests tests/test_qt.py and tests/test_qt_contracts.py
        """
        if not spec.key or spec.key in self._specs:
            raise ValueError("page key is empty or already registered")
        self._specs[spec.key] = spec
        self.sidebar.addItem(spec.title)

    def _on_row_changed(self, row: int) -> None:
        if row >= 0:
            self.navigate(tuple(self._specs)[row])

    def navigate(self, key: str) -> QWidget:
        """Return cached/new QWidget; KeyError for unknown route, TypeError for bad factory; call leave/enter and emit on success; failed enter attempts previous-page restoration; no-op on current route.

        @ac-reusable
        @ac-capability desktop.navigation.PageHost.navigate
        @ac-kind function
        @ac-tags desktop, navigation, PageHost
        @ac-contract Return cached/new QWidget; KeyError for unknown route, TypeError for bad factory; call leave/enter and emit on success; failed enter attempts previous-page restoration; no-op on current route.
        @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
        @ac-example See examples/desktop_demo.py and docs/contracts/navigation.md.
        @ac-tests tests/test_qt.py and tests/test_qt_contracts.py
        """
        if key not in self._specs:
            raise KeyError(key)
        if key == self._current:
            return self._pages[key]
        if key not in self._pages:
            page = self._specs[key].create()
            if not isinstance(page, QWidget):
                raise TypeError("page factory must return a QWidget")
            self._pages[key] = page
            self.stack.addWidget(page)
        page = self._pages[key]
        previous_key = self._current
        previous = self._pages.get(previous_key) if previous_key else None
        if previous is not None and callable(getattr(previous, "on_leave", None)):
            previous.on_leave()
        self.stack.setCurrentWidget(page)
        try:
            if callable(getattr(page, "on_enter", None)):
                page.on_enter()
        except Exception:
            if previous is not None:
                self.stack.setCurrentWidget(previous)
                if callable(getattr(previous, "on_enter", None)):
                    previous.on_enter()
            if previous_key is not None:
                self.sidebar.blockSignals(True)
                self.sidebar.setCurrentRow(tuple(self._specs).index(previous_key))
                self.sidebar.blockSignals(False)
            raise
        self._current = key
        row = tuple(self._specs).index(key)
        self.sidebar.blockSignals(True)
        self.sidebar.setCurrentRow(row)
        self.sidebar.blockSignals(False)
        self.page_changed.emit(key)
        return page

    def dispose(self) -> None:
        """Invoke cached page cleanup hooks then detach/deleteLater widgets and clear current route; repeatable if cleanup succeeds; hook errors propagate.

        @ac-reusable
        @ac-capability desktop.navigation.PageHost.dispose
        @ac-kind function
        @ac-tags desktop, navigation, PageHost
        @ac-contract Invoke cached page cleanup hooks then detach/deleteLater widgets and clear current route; repeatable if cleanup succeeds; hook errors propagate.
        @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
        @ac-example See examples/desktop_demo.py and docs/contracts/navigation.md.
        @ac-tests tests/test_qt.py and tests/test_qt_contracts.py
        """
        for page in self._pages.values():
            cleanup = getattr(page, "dispose", None)
            if callable(cleanup):
                cleanup()
            self.stack.removeWidget(page)
            page.deleteLater()
        self._pages.clear()
        self._current = None
