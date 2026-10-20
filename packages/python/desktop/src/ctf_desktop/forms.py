"""Declarative Qt editing and read-only detail views."""

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QLabel,
    QLineEdit, QPlainTextEdit, QSpinBox, QVBoxLayout, QWidget,
)


@dataclass(frozen=True)
class FieldSpec:
    """Immutable field key/label; text default, required false; supports multiline/integer/boolean/choice/custom; custom requires factory and reader; invalid kind raises ValueError.

    @ac-reusable
    @ac-capability desktop.forms.FieldSpec
    @ac-kind component
    @ac-tags desktop, forms, FieldSpec
    @ac-contract Immutable field key/label; text default, required false; supports multiline/integer/boolean/choice/custom; custom requires factory and reader; invalid kind raises ValueError.
    @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
    @ac-example See examples/desktop_demo.py and docs/contracts/forms.md.
    @ac-tests tests/test_qt.py and tests/test_qt_contracts.py
    """
    key: str
    label: str
    kind: str = "text"
    required: bool = False
    choices: tuple[tuple[Any, str], ...] = ()
    validate: Callable[[Any], str | None] | None = None
    widget_factory: Callable[[Any], QWidget] | None = None
    value_reader: Callable[[QWidget], Any] | None = None

    def __post_init__(self) -> None:
        if self.kind not in {"text", "multiline", "integer", "boolean", "choice", "custom"}:
            raise ValueError(f"unsupported field kind: {self.kind}")
        if self.kind == "custom" and (self.widget_factory is None or self.value_reader is None):
            raise ValueError("custom fields need a widget factory and value reader")


def validate_values(fields: Sequence[FieldSpec], values: Mapping[str, Any]) -> dict[str, str]:
    """Return field-key to error-text mapping for required/host validator failures; false and zero are valid required values; validator exceptions propagate; no writes.

    @ac-reusable
    @ac-capability desktop.forms.validate_values
    @ac-kind function
    @ac-tags desktop, forms, validate_values
    @ac-contract Return field-key to error-text mapping for required/host validator failures; false and zero are valid required values; validator exceptions propagate; no writes.
    @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
    @ac-example See examples/desktop_demo.py and docs/contracts/forms.md.
    @ac-tests tests/test_qt.py and tests/test_qt_contracts.py
    """
    errors = {}
    for field in fields:
        value = values.get(field.key)
        if field.required and (value is None or value == ""):
            errors[field.key] = "必填"
        elif field.validate:
            message = field.validate(value)
            if message:
                errors[field.key] = message
    return errors


class FormDialog(QDialog):
    """GUI-thread dialog with caller title/fields/initial values; submitted(dict) only on valid save then accepts; failed validation retains dialog with errors; cancel rejects.

    @ac-reusable
    @ac-capability desktop.forms.FormDialog
    @ac-kind component
    @ac-tags desktop, forms, FormDialog
    @ac-contract GUI-thread dialog with caller title/fields/initial values; submitted(dict) only on valid save then accepts; failed validation retains dialog with errors; cancel rejects.
    @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
    @ac-example See examples/desktop_demo.py and docs/contracts/forms.md.
    @ac-tests tests/test_qt.py and tests/test_qt_contracts.py
    """
    submitted = pyqtSignal(dict)

    def __init__(self, title: str, fields: Sequence[FieldSpec], initial=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.fields = tuple(fields)
        self._widgets: dict[str, QWidget] = {}
        initial = initial or {}
        form = QFormLayout()
        for field in self.fields:
            widget = self._create_widget(field, initial.get(field.key))
            self._widgets[field.key] = widget
            form.addRow(field.label, widget)
        self.error_label = QLabel(self)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel, parent=self)
        buttons.accepted.connect(self._submit)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self.error_label)
        layout.addWidget(buttons)

    def _create_widget(self, field: FieldSpec, value: Any) -> QWidget:
        if field.kind == "custom":
            return field.widget_factory(value)
        if field.kind == "multiline":
            widget = QPlainTextEdit(self)
            widget.setPlainText(str(value or ""))
        elif field.kind == "integer":
            widget = QSpinBox(self)
            widget.setRange(-2_147_483_648, 2_147_483_647)
            widget.setValue(int(value or 0))
        elif field.kind == "boolean":
            widget = QCheckBox(self)
            widget.setChecked(bool(value))
        elif field.kind == "choice":
            widget = QComboBox(self)
            if not field.required:
                widget.addItem("", None)
            for option_value, label in field.choices:
                widget.addItem(label, option_value)
            index = widget.findData(value)
            if index >= 0:
                widget.setCurrentIndex(index)
        else:
            widget = QLineEdit(self)
            widget.setText(str(value or ""))
        return widget

    def values(self) -> dict[str, Any]:
        """Read current fields to new mapping; text stripped, choice returns data, integer/bool preserve types; custom reader errors propagate.

        @ac-reusable
        @ac-capability desktop.forms.FormDialog.values
        @ac-kind function
        @ac-tags desktop, forms, FormDialog
        @ac-contract Read current fields to new mapping; text stripped, choice returns data, integer/bool preserve types; custom reader errors propagate.
        @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
        @ac-example See examples/desktop_demo.py and docs/contracts/forms.md.
        @ac-tests tests/test_qt.py and tests/test_qt_contracts.py
        """
        values = {}
        for field in self.fields:
            widget = self._widgets[field.key]
            if field.kind == "custom":
                value = field.value_reader(widget)
            elif field.kind == "multiline":
                value = widget.toPlainText()
            elif field.kind == "integer":
                value = widget.value()
            elif field.kind == "boolean":
                value = widget.isChecked()
            elif field.kind == "choice":
                value = widget.currentData()
            else:
                value = widget.text().strip()
            values[field.key] = value
        return values

    def _submit(self) -> None:
        values = self.values()
        errors = validate_values(self.fields, values)
        if errors:
            self.error_label.setText("；".join(f"{key}: {message}" for key, message in errors.items()))
            return
        self.submitted.emit(values)
        self.accept()


class DetailView(QWidget):
    """GUI-thread read-only labels for provided fields/values; None displays empty text, others stringify; parent owns widget lifetime.

    @ac-reusable
    @ac-capability desktop.forms.DetailView
    @ac-kind component
    @ac-tags desktop, forms, DetailView
    @ac-contract GUI-thread read-only labels for provided fields/values; None displays empty text, others stringify; parent owns widget lifetime.
    @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
    @ac-example See examples/desktop_demo.py and docs/contracts/forms.md.
    @ac-tests tests/test_qt.py and tests/test_qt_contracts.py
    """
    def __init__(self, fields: Sequence[FieldSpec], values: Mapping[str, Any], parent=None):
        super().__init__(parent)
        layout = QFormLayout(self)
        for field in fields:
            value = values.get(field.key)
            layout.addRow(field.label, QLabel("" if value is None else str(value), self))
