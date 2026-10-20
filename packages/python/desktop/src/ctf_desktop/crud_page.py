"""A generic list/detail/edit page wired to an injected CRUD controller."""

from typing import Any, Sequence

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QMessageBox, QPushButton, QVBoxLayout, QWidget

from .crud import CrudController
from .feedback import ConfirmDialog
from .filters import FilterField, FilterPanel
from .forms import DetailView, FieldSpec, FormDialog
from .query import PageRequest
from .table import Column, PagedTable


class CrudPage(QWidget):
    """GUI-thread synchronous CRUD composition; missing identity emits operation_failed(action,ValueError); completed modal dialogs scheduled for deletion; changed and operation_failed signals delegate policy to host.

    @ac-reusable
    @ac-capability desktop.crud_page.CrudPage
    @ac-kind component
    @ac-tags desktop, crud_page, CrudPage
    @ac-contract GUI-thread synchronous CRUD composition; missing identity emits operation_failed(action,ValueError); completed modal dialogs scheduled for deletion; changed and operation_failed signals delegate policy to host.
    @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
    @ac-example See examples/desktop_demo.py and docs/contracts/crud_page.md.
    @ac-tests tests/test_qt.py, tests/test_qt_contracts.py and tests/test_review_qt.py
    """
    changed = pyqtSignal(str, object)
    operation_failed = pyqtSignal(str, object)

    def __init__(
        self,
        controller: CrudController,
        *,
        identity_key: str,
        columns: Sequence[Column],
        fields: Sequence[FieldSpec],
        filters: Sequence[FilterField] = (),
        parent=None,
    ):
        super().__init__(parent)
        self.controller = controller
        self.identity_key = identity_key
        self.fields = tuple(fields)
        self.filters = FilterPanel(filters, self)
        self.table = PagedTable(columns, parent=self)
        self.table.page_requested.connect(self.load_page)
        self.filters.search_requested.connect(lambda _values: self.load_page(PageRequest(1, self.table.request.size)))
        self.filters.reset_requested.connect(lambda: self.load_page(PageRequest(1, self.table.request.size)))
        actions = QHBoxLayout()
        for label, callback in (
            ("新增", self.create_record),
            ("详情", self.show_detail),
            ("编辑", self.edit_selected),
            ("删除", self.delete_selected),
        ):
            button = QPushButton(label, self)
            button.clicked.connect(callback)
            actions.addWidget(button)
        layout = QVBoxLayout(self)
        layout.addWidget(self.filters)
        layout.addLayout(actions)
        layout.addWidget(self.table)

    def load_page(self, request: PageRequest | None = None) -> None:
        """Fetch requested/current page using current filters; display or emit operation_failed(list,error); default page uses current request.

        @ac-reusable
        @ac-capability desktop.crud_page.CrudPage.load_page
        @ac-kind function
        @ac-tags desktop, crud_page, CrudPage
        @ac-contract Fetch requested/current page using current filters; display or emit operation_failed(list,error); default page uses current request.
        @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
        @ac-example See examples/desktop_demo.py and docs/contracts/crud_page.md.
        @ac-tests tests/test_qt.py, tests/test_qt_contracts.py and tests/test_review_qt.py
        """
        try:
            page = self.controller.list_page(request or self.table.request, self.filters.values())
            self.table.set_page(page)
        except Exception as error:
            self.operation_failed.emit("list", error)

    def _single_selected(self) -> dict[str, Any] | None:
        records = self.table.selected_records()
        if len(records) != 1:
            QMessageBox.information(self, "选择记录", "请选择一条记录")
            return None
        return dict(records[0])

    def create_record(self) -> None:
        """Open form, call authorized create only on acceptance, emit changed/reload first page; report controller errors and delete dialog on every exit.

        @ac-reusable
        @ac-capability desktop.crud_page.CrudPage.create_record
        @ac-kind function
        @ac-tags desktop, crud_page, CrudPage
        @ac-contract Open form, call authorized create only on acceptance, emit changed/reload first page; report controller errors and delete dialog on every exit.
        @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
        @ac-example See examples/desktop_demo.py and docs/contracts/crud_page.md.
        @ac-tests tests/test_qt.py, tests/test_qt_contracts.py and tests/test_review_qt.py
        """
        dialog = FormDialog("新增", self.fields, parent=self)
        try:
            if dialog.exec_() == QDialog.Accepted:
                try:
                    identity = self.controller.create(dialog.values())
                    self.changed.emit("create", identity)
                    self.load_page(PageRequest(1, self.table.request.size))
                except Exception as error:
                    self.operation_failed.emit("create", error)
        finally:
            dialog.deleteLater()

    def edit_selected(self) -> None:
        """Require one selected record with identity; report missing identity as operation_failed(update,error); accepted form updates then reloads; always delete dialog.

        @ac-reusable
        @ac-capability desktop.crud_page.CrudPage.edit_selected
        @ac-kind function
        @ac-tags desktop, crud_page, CrudPage
        @ac-contract Require one selected record with identity; report missing identity as operation_failed(update,error); accepted form updates then reloads; always delete dialog.
        @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
        @ac-example See examples/desktop_demo.py and docs/contracts/crud_page.md.
        @ac-tests tests/test_qt.py, tests/test_qt_contracts.py and tests/test_review_qt.py
        """
        record = self._single_selected()
        if record is None:
            return
        identity = self._record_identity(record, "update")
        if identity is None:
            return
        dialog = FormDialog("编辑", self.fields, initial=record, parent=self)
        try:
            if dialog.exec_() == QDialog.Accepted:
                try:
                    self.controller.update(identity, dialog.values())
                    self.changed.emit("update", identity)
                    self.load_page()
                except Exception as error:
                    self.operation_failed.emit("update", error)
        finally:
            dialog.deleteLater()

    def show_detail(self) -> None:
        """Require selected identity; authorized lookup errors become operation_failed(read,error); show detail or reload missing row; always delete detail dialog.

        @ac-reusable
        @ac-capability desktop.crud_page.CrudPage.show_detail
        @ac-kind function
        @ac-tags desktop, crud_page, CrudPage
        @ac-contract Require selected identity; authorized lookup errors become operation_failed(read,error); show detail or reload missing row; always delete detail dialog.
        @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
        @ac-example See examples/desktop_demo.py and docs/contracts/crud_page.md.
        @ac-tests tests/test_qt.py, tests/test_qt_contracts.py and tests/test_review_qt.py
        """
        record = self._single_selected()
        if record is None:
            return
        identity = self._record_identity(record, "read")
        if identity is None:
            return
        try:
            detail = self.controller.detail(identity)
        except Exception as error:
            self.operation_failed.emit("read", error)
            return
        if detail is None:
            QMessageBox.information(self, "详情", "记录已不存在")
            self.load_page()
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("详情")
        try:
            layout = QVBoxLayout(dialog)
            layout.addWidget(DetailView(self.fields, detail, dialog))
            dialog.exec_()
        finally:
            dialog.deleteLater()

    def delete_selected(self) -> None:
        """Require selected identity and affirmative confirmation; report malformed identity or controller failure; successful delete emits changed and reloads; cancellation writes nothing.

        @ac-reusable
        @ac-capability desktop.crud_page.CrudPage.delete_selected
        @ac-kind function
        @ac-tags desktop, crud_page, CrudPage
        @ac-contract Require selected identity and affirmative confirmation; report malformed identity or controller failure; successful delete emits changed and reloads; cancellation writes nothing.
        @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
        @ac-example See examples/desktop_demo.py and docs/contracts/crud_page.md.
        @ac-tests tests/test_qt.py, tests/test_qt_contracts.py and tests/test_review_qt.py
        """
        record = self._single_selected()
        if record is None:
            return
        identity = self._record_identity(record, "delete")
        if identity is None:
            return
        if ConfirmDialog.ask(self, "删除", "确认删除所选记录？"):
            try:
                self.controller.delete(identity)
                self.changed.emit("delete", identity)
                self.load_page()
            except Exception as error:
                self.operation_failed.emit("delete", error)

    def _record_identity(self, record, action):
        identity = record.get(self.identity_key)
        if identity is None:
            self.operation_failed.emit(action, ValueError("record has no configured identity"))
            return None
        return identity
