"""Declarative Qt filters and a provider-neutral live-search input."""

from dataclasses import dataclass
from typing import Any, Sequence

from PyQt5.QtCore import QDate, QTimer, Qt, QSignalBlocker, pyqtSignal
from PyQt5.QtWidgets import QComboBox, QDateEdit, QFormLayout, QLineEdit, QPushButton, QVBoxLayout, QWidget


@dataclass(frozen=True)
class FilterField:
    """Immutable key/label, kind=text, optional choice pairs; supports text/choice/date_range, else ValueError.

    @ac-reusable
    @ac-capability desktop.filters.FilterField
    @ac-kind component
    @ac-tags desktop, filters, FilterField
    @ac-contract Immutable key/label, kind=text, optional choice pairs; supports text/choice/date_range, else ValueError.
    @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
    @ac-example See examples/desktop_demo.py and docs/contracts/filters.md.
    @ac-tests tests/test_qt.py, tests/test_qt_contracts.py and tests/test_review_qt.py
    """
    key: str
    label: str
    kind: str = "text"
    choices: tuple[tuple[Any, str], ...] = ()

    def __post_init__(self) -> None:
        if self.kind not in {"text", "choice", "date_range"}:
            raise ValueError(f"unsupported filter kind: {self.kind}")


class FilterPanel(QWidget):
    """GUI-thread filters with unique nonempty keys; search_requested(dict) on search and reset_requested on clear; no persistence or SQL execution.

    @ac-reusable
    @ac-capability desktop.filters.FilterPanel
    @ac-kind component
    @ac-tags desktop, filters, FilterPanel
    @ac-contract GUI-thread filters with unique nonempty keys; search_requested(dict) on search and reset_requested on clear; no persistence or SQL execution.
    @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
    @ac-example See examples/desktop_demo.py and docs/contracts/filters.md.
    @ac-tests tests/test_qt.py, tests/test_qt_contracts.py and tests/test_review_qt.py
    """
    search_requested = pyqtSignal(dict)
    reset_requested = pyqtSignal()

    def __init__(self, fields: Sequence[FilterField], parent=None):
        super().__init__(parent)
        self.fields = tuple(fields)
        if any(not field.key for field in self.fields) or len({field.key for field in self.fields}) != len(self.fields):
            raise ValueError("field keys must be nonempty and unique")
        self._widgets: dict[str, object] = {}
        form = QFormLayout()
        for field in self.fields:
            if field.kind == "choice":
                widget = QComboBox(self)
                widget.addItem("全部", None)
                for value, label in field.choices:
                    widget.addItem(label, value)
            elif field.kind == "date_range":
                start, end = QDateEdit(self), QDateEdit(self)
                for widget in (start, end):
                    widget.setCalendarPopup(True)
                    widget.setMinimumDate(QDate(1900, 1, 1))
                    widget.setSpecialValueText("不限")
                    widget.setDate(widget.minimumDate())
                wrapper = QWidget(self)
                pair = QVBoxLayout(wrapper)
                pair.setContentsMargins(0, 0, 0, 0)
                pair.addWidget(start)
                pair.addWidget(end)
                widget = wrapper
                self._widgets[field.key] = (start, end)
            else:
                widget = QLineEdit(self)
            form.addRow(field.label, widget)
            if field.kind != "date_range":
                self._widgets[field.key] = widget
        search = QPushButton("查询", self)
        reset = QPushButton("重置", self)
        search.clicked.connect(lambda: self.search_requested.emit(self.values()))
        reset.clicked.connect(self.clear)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(search)
        layout.addWidget(reset)

    def values(self) -> dict[str, Any]:
        """Return nonempty filter values; strip text, choices return data, date ranges return ISO start/end or None; 1900-01-01 is the unset sentinel.

        @ac-reusable
        @ac-capability desktop.filters.FilterPanel.values
        @ac-kind function
        @ac-tags desktop, filters, FilterPanel
        @ac-contract Return nonempty filter values; strip text, choices return data, date ranges return ISO start/end or None; 1900-01-01 is the unset sentinel.
        @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
        @ac-example See examples/desktop_demo.py and docs/contracts/filters.md.
        @ac-tests tests/test_qt.py, tests/test_qt_contracts.py and tests/test_review_qt.py
        """
        result = {}
        for field in self.fields:
            widget = self._widgets[field.key]
            if field.kind == "choice":
                value = widget.currentData()
            elif field.kind == "date_range":
                start, end = widget
                value = (
                    None if start.date() == start.minimumDate() else start.date().toString(Qt.ISODate),
                    None if end.date() == end.minimumDate() else end.date().toString(Qt.ISODate),
                )
            else:
                value = widget.text().strip()
            if value not in (None, "", (None, None)):
                result[field.key] = value
        return result

    def clear(self) -> None:
        """Reset text/choice/date widgets and emit reset_requested; repeatable; never starts IO.

        @ac-reusable
        @ac-capability desktop.filters.FilterPanel.clear
        @ac-kind function
        @ac-tags desktop, filters, FilterPanel
        @ac-contract Reset text/choice/date widgets and emit reset_requested; repeatable; never starts IO.
        @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
        @ac-example See examples/desktop_demo.py and docs/contracts/filters.md.
        @ac-tests tests/test_qt.py, tests/test_qt_contracts.py and tests/test_review_qt.py
        """
        for field in self.fields:
            widget = self._widgets[field.key]
            if field.kind == "choice":
                widget.setCurrentIndex(0)
            elif field.kind == "date_range":
                for edit in widget:
                    edit.setDate(edit.minimumDate())
            else:
                widget.clear()
        self.reset_requested.emit()


class LiveSearchComboBox(QComboBox):
    """GUI-thread editable combo; debounce edits then emit request_started(id,text) and compatible search_requested(text); IDs advance on edits and requests; request_id in set_results rejects same-text stale responses.

    @ac-reusable
    @ac-capability desktop.filters.LiveSearchComboBox
    @ac-kind component
    @ac-tags desktop, filters, LiveSearchComboBox
    @ac-contract GUI-thread editable combo; debounce edits then emit request_started(id,text) and compatible search_requested(text); IDs advance on edits and requests; request_id in set_results rejects same-text stale responses.
    @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
    @ac-example See examples/desktop_demo.py and docs/contracts/filters.md.
    @ac-tests tests/test_qt.py, tests/test_qt_contracts.py and tests/test_review_qt.py
    """
    search_requested = pyqtSignal(str)
    request_started = pyqtSignal(int, str)

    def __init__(self, delay_ms: int = 200, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self._request_id = 0
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(delay_ms)
        self._timer.timeout.connect(self._request_search)
        self.lineEdit().textEdited.connect(self._edited)

    def _edited(self, text):
        self._request_id += 1
        self._timer.start()

    def _request_search(self):
        self._request_id += 1
        query = self.currentText().strip()
        self.request_started.emit(self._request_id, query)
        self.search_requested.emit(query)

    def set_results(self, query: str, results: Sequence[tuple[Any, str]], *, request_id: int | None = None) -> bool:
        """Reject stale query or optional request_id with false; validate all (value,text) pairs before mutation; preserve prior signal-block state on all exits, replace results and return true; old calls without request_id retain text-only comparison.

        @ac-reusable
        @ac-capability desktop.filters.LiveSearchComboBox.set_results
        @ac-kind function
        @ac-tags desktop, filters, LiveSearchComboBox
        @ac-contract Reject stale query or optional request_id with false; validate all (value,text) pairs before mutation; preserve prior signal-block state on all exits, replace results and return true; old calls without request_id retain text-only comparison.
        @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
        @ac-example See examples/desktop_demo.py and docs/contracts/filters.md.
        @ac-tests tests/test_qt.py, tests/test_qt_contracts.py and tests/test_review_qt.py
        """
        if query != self.currentText().strip() or (request_id is not None and request_id != self._request_id):
            return False
        prepared = []
        for row in results:
            if not isinstance(row, (tuple, list)) or len(row) != 2 or not isinstance(row[1], str):
                raise ValueError("search results must contain (value, text) pairs")
            prepared.append(tuple(row))
        blocker = QSignalBlocker(self)
        try:
            self.clear()
            for value, label in prepared:
                self.addItem(label, value)
            self.setEditText(query)
        finally:
            del blocker
        self.showPopup()
        return True
