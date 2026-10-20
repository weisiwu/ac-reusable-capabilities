"""Declarative Qt filters and a provider-neutral live-search input."""

from dataclasses import dataclass
from typing import Any, Sequence

from PyQt5.QtCore import QDate, QTimer, Qt, pyqtSignal
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
    @ac-tests tests/test_qt.py and tests/test_qt_contracts.py
    """
    key: str
    label: str
    kind: str = "text"
    choices: tuple[tuple[Any, str], ...] = ()

    def __post_init__(self) -> None:
        if self.kind not in {"text", "choice", "date_range"}:
            raise ValueError(f"unsupported filter kind: {self.kind}")


class FilterPanel(QWidget):
    """GUI-thread filter widgets; search_requested(dict) on search and reset_requested on clear; no persistence or SQL execution.

    @ac-reusable
    @ac-capability desktop.filters.FilterPanel
    @ac-kind component
    @ac-tags desktop, filters, FilterPanel
    @ac-contract GUI-thread filter widgets; search_requested(dict) on search and reset_requested on clear; no persistence or SQL execution.
    @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
    @ac-example See examples/desktop_demo.py and docs/contracts/filters.md.
    @ac-tests tests/test_qt.py and tests/test_qt_contracts.py
    """
    search_requested = pyqtSignal(dict)
    reset_requested = pyqtSignal()

    def __init__(self, fields: Sequence[FilterField], parent=None):
        super().__init__(parent)
        self.fields = tuple(fields)
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
        @ac-tests tests/test_qt.py and tests/test_qt_contracts.py
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
        @ac-tests tests/test_qt.py and tests/test_qt_contracts.py
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
    """GUI-thread editable combo; debounce user edits by delay_ms=200 and emit search_requested(str); caller performs query; text matching is not request-generation ordering.

    @ac-reusable
    @ac-capability desktop.filters.LiveSearchComboBox
    @ac-kind component
    @ac-tags desktop, filters, LiveSearchComboBox
    @ac-contract GUI-thread editable combo; debounce user edits by delay_ms=200 and emit search_requested(str); caller performs query; text matching is not request-generation ordering.
    @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
    @ac-example See examples/desktop_demo.py and docs/contracts/filters.md.
    @ac-tests tests/test_qt.py and tests/test_qt_contracts.py
    """
    search_requested = pyqtSignal(str)

    def __init__(self, delay_ms: int = 200, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(delay_ms)
        self._timer.timeout.connect(lambda: self.search_requested.emit(self.currentText().strip()))
        self.lineEdit().textEdited.connect(lambda _text: self._timer.start())

    def set_results(self, query: str, results: Sequence[tuple[Any, str]]) -> bool:
        """Reject query unequal to current stripped text with false; otherwise replace (id,label) results, preserve text, show popup and return true; repeated same-text request races must be handled by caller.

        @ac-reusable
        @ac-capability desktop.filters.LiveSearchComboBox.set_results
        @ac-kind function
        @ac-tags desktop, filters, LiveSearchComboBox
        @ac-contract Reject query unequal to current stripped text with false; otherwise replace (id,label) results, preserve text, show popup and return true; repeated same-text request races must be handled by caller.
        @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
        @ac-example See examples/desktop_demo.py and docs/contracts/filters.md.
        @ac-tests tests/test_qt.py and tests/test_qt_contracts.py
        """
        if query != self.currentText().strip():
            return False
        self.blockSignals(True)
        self.clear()
        for value, label in results:
            self.addItem(label, value)
        self.setEditText(query)
        self.blockSignals(False)
        self.showPopup()
        return True
