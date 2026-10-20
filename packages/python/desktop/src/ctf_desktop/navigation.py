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
    @ac-tests tests/test_qt.py, tests/test_qt_contracts.py and tests/test_review_qt.py
    """
    key: str
    title: str
    create: Callable[[], QWidget]


class PageHost(QWidget):
    """GUI-thread page registry and lifecycle host; page_changed after success, navigation_failed(key,error) for sidebar failures; lifecycle reentry rejected; caller disposes before shutdown.

    @ac-reusable
    @ac-capability desktop.navigation.PageHost
    @ac-kind component
    @ac-tags desktop, navigation, PageHost
    @ac-contract GUI-thread page registry and lifecycle host; page_changed after success, navigation_failed(key,error) for sidebar failures; lifecycle reentry rejected; caller disposes before shutdown.
    @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
    @ac-example See examples/desktop_demo.py and docs/contracts/navigation.md.
    @ac-tests tests/test_qt.py, tests/test_qt_contracts.py and tests/test_review_qt.py
    """
    page_changed = pyqtSignal(str)
    navigation_failed = pyqtSignal(str, object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.sidebar = QListWidget(self)
        self.stack = QStackedWidget(self)
        self._specs: dict[str, PageSpec] = {}
        self._pages: dict[str, QWidget] = {}
        self._current: str | None = None
        self._transition = False
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
        @ac-tests tests/test_qt.py, tests/test_qt_contracts.py and tests/test_review_qt.py
        """
        if not spec.key or spec.key in self._specs:
            raise ValueError("page key is empty or already registered")
        self._specs[spec.key] = spec
        self.sidebar.addItem(spec.title)

    def _on_row_changed(self, row: int) -> None:
        if 0 <= row < len(self._specs):
            key = tuple(self._specs)[row]
            try:
                self.navigate(key)
            except Exception as error:
                self.navigation_failed.emit(key, error)

    def navigate(self, key: str) -> QWidget:
        """Reject lifecycle reentry; return cached/new page and emit page_changed only after successful hooks; failed new page is disposed and removed; attempt previous-page restoration and preserve original error with cleanup notes.

        @ac-reusable
        @ac-capability desktop.navigation.PageHost.navigate
        @ac-kind function
        @ac-tags desktop, navigation, PageHost
        @ac-contract Reject lifecycle reentry; return cached/new page and emit page_changed only after successful hooks; failed new page is disposed and removed; attempt previous-page restoration and preserve original error with cleanup notes.
        @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
        @ac-example See examples/desktop_demo.py and docs/contracts/navigation.md.
        @ac-tests tests/test_qt.py, tests/test_qt_contracts.py and tests/test_review_qt.py
        """
        if self._transition:
            raise RuntimeError("page lifecycle reentry is not supported")
        self._transition = True
        try:
            return self._navigate(key)
        finally:
            self._transition = False

    def dispose(self) -> None:
        """Reject lifecycle reentry; attempt every cleanup hook, always detach/deleteLater all pages and clear current state; aggregate first cleanup failure as RuntimeError after cleanup; repeatable afterward.

        @ac-reusable
        @ac-capability desktop.navigation.PageHost.dispose
        @ac-kind function
        @ac-tags desktop, navigation, PageHost
        @ac-contract Reject lifecycle reentry; attempt every cleanup hook, always detach/deleteLater all pages and clear current state; aggregate first cleanup failure as RuntimeError after cleanup; repeatable afterward.
        @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
        @ac-example See examples/desktop_demo.py and docs/contracts/navigation.md.
        @ac-tests tests/test_qt.py, tests/test_qt_contracts.py and tests/test_review_qt.py
        """
        if self._transition:
            raise RuntimeError("page lifecycle reentry is not supported")
        self._transition = True
        try:
            return self._dispose()
        finally:
            self._transition = False

    def _navigate(self, key):
        if key not in self._specs:
            raise KeyError(key)
        if key == self._current:
            return self._pages[key]
        created = key not in self._pages
        if created:
            page = self._specs[key].create()
            if not isinstance(page, QWidget):
                raise TypeError("page factory must return a QWidget")
            self._pages[key] = page
            self.stack.addWidget(page)
        page = self._pages[key]
        previous_key = self._current
        previous = self._pages.get(previous_key) if previous_key else None
        try:
            if previous is not None and callable(getattr(previous, "on_leave", None)):
                previous.on_leave()
            self.stack.setCurrentWidget(page)
            if callable(getattr(page, "on_enter", None)):
                page.on_enter()
        except Exception as error:
            if created:
                self._pages.pop(key, None)
                try:
                    cleanup = getattr(page, "dispose", None)
                    if callable(cleanup):
                        cleanup()
                except Exception as cleanup_error:
                    error.add_note(f"Failed-page cleanup also failed: {cleanup_error}")
                finally:
                    self.stack.removeWidget(page)
                    page.deleteLater()
            if previous is not None:
                self.stack.setCurrentWidget(previous)
                try:
                    if callable(getattr(previous, "on_enter", None)):
                        previous.on_enter()
                except Exception as restore_error:
                    error.add_note(f"Previous-page restoration also failed: {restore_error}")
            self.sidebar.blockSignals(True)
            try:
                self.sidebar.setCurrentRow(tuple(self._specs).index(previous_key) if previous_key else -1)
            finally:
                self.sidebar.blockSignals(False)
            raise
        self._current = key
        row = tuple(self._specs).index(key)
        self.sidebar.blockSignals(True)
        try:
            self.sidebar.setCurrentRow(row)
        finally:
            self.sidebar.blockSignals(False)
        self.page_changed.emit(key)
        return page

    def _dispose(self):
        first_error = None
        for page in tuple(self._pages.values()):
            try:
                cleanup = getattr(page, "dispose", None)
                if callable(cleanup):
                    cleanup()
            except Exception as error:
                first_error = first_error or error
            finally:
                self.stack.removeWidget(page)
                page.deleteLater()
        self._pages.clear()
        self._current = None
        if first_error is not None:
            raise RuntimeError("one or more page cleanup hooks failed") from first_error
