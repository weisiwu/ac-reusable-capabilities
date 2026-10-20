"""Small Qt table view with explicit page ownership and selected-row extraction."""

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QPushButton, QTableView, QVBoxLayout, QWidget

from .query import PageRequest, PageResult


@dataclass(frozen=True)
class Column:
    """Immutable key/title and display callback (str default); rendering only, no SQL or sorting expressions.

    @ac-reusable
    @ac-capability desktop.table.Column
    @ac-kind component
    @ac-tags desktop, table, Column
    @ac-contract Immutable key/title and display callback (str default); rendering only, no SQL or sorting expressions.
    @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
    @ac-example See examples/desktop_demo.py and docs/contracts/table.md.
    @ac-tests tests/test_qt.py, tests/test_qt_contracts.py and tests/test_review_qt.py
    """
    key: str
    title: str
    display: Callable[[Any], str] = str


class RecordTableModel(QAbstractTableModel):
    """GUI-thread model over mapping records; require nonempty unique columns or ValueError; reset on set_records.

    @ac-reusable
    @ac-capability desktop.table.RecordTableModel
    @ac-kind component
    @ac-tags desktop, table, RecordTableModel
    @ac-contract GUI-thread model over mapping records; require nonempty unique columns or ValueError; reset on set_records.
    @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
    @ac-example See examples/desktop_demo.py and docs/contracts/table.md.
    @ac-tests tests/test_qt.py, tests/test_qt_contracts.py and tests/test_review_qt.py
    """
    def __init__(self, columns: Sequence[Column], parent=None):
        super().__init__(parent)
        if not columns or len({column.key for column in columns}) != len(columns):
            raise ValueError("columns must be nonempty with unique keys")
        self.columns = tuple(columns)
        self.records: tuple[Mapping[str, Any], ...] = ()

    def rowCount(self, parent=QModelIndex()) -> int:
        """Return zero for valid parent (flat model), otherwise current record count.

        @ac-reusable
        @ac-capability desktop.table.RecordTableModel.rowCount
        @ac-kind function
        @ac-tags desktop, table, RecordTableModel
        @ac-contract Return zero for valid parent (flat model), otherwise current record count.
        @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
        @ac-example See examples/desktop_demo.py and docs/contracts/table.md.
        @ac-tests tests/test_qt.py, tests/test_qt_contracts.py and tests/test_review_qt.py
        """
        return 0 if parent.isValid() else len(self.records)

    def columnCount(self, parent=QModelIndex()) -> int:
        """Return zero for valid parent, otherwise column count.

        @ac-reusable
        @ac-capability desktop.table.RecordTableModel.columnCount
        @ac-kind function
        @ac-tags desktop, table, RecordTableModel
        @ac-contract Return zero for valid parent, otherwise column count.
        @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
        @ac-example See examples/desktop_demo.py and docs/contracts/table.md.
        @ac-tests tests/test_qt.py, tests/test_qt_contracts.py and tests/test_review_qt.py
        """
        return 0 if parent.isValid() else len(self.columns)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        """Return only for in-bounds indices owned by this model; UserRole returns mapping and DisplayRole formatted/empty text; invalid index/other role returns None; host display callback errors propagate.

        @ac-reusable
        @ac-capability desktop.table.RecordTableModel.data
        @ac-kind function
        @ac-tags desktop, table, RecordTableModel
        @ac-contract Return only for in-bounds indices owned by this model; UserRole returns mapping and DisplayRole formatted/empty text; invalid index/other role returns None; host display callback errors propagate.
        @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
        @ac-example See examples/desktop_demo.py and docs/contracts/table.md.
        @ac-tests tests/test_qt.py, tests/test_qt_contracts.py and tests/test_review_qt.py
        """
        if not index.isValid():
            return None
        if index.model() is not self or not (0 <= index.row() < len(self.records) and 0 <= index.column() < len(self.columns)):
            return None
        record = self.records[index.row()]
        if role == Qt.UserRole:
            return record
        if role == Qt.DisplayRole:
            column = self.columns[index.column()]
            value = record.get(column.key)
            return "" if value is None else column.display(value)
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole):
        """Horizontal DisplayRole returns in-bounds title, None for invalid section; other orientation/role delegates to Qt.

        @ac-reusable
        @ac-capability desktop.table.RecordTableModel.headerData
        @ac-kind function
        @ac-tags desktop, table, RecordTableModel
        @ac-contract Horizontal DisplayRole returns in-bounds title, None for invalid section; other orientation/role delegates to Qt.
        @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
        @ac-example See examples/desktop_demo.py and docs/contracts/table.md.
        @ac-tests tests/test_qt.py, tests/test_qt_contracts.py and tests/test_review_qt.py
        """
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.columns[section].title if 0 <= section < len(self.columns) else None
        return super().headerData(section, orientation, role)

    def set_records(self, records: Sequence[Mapping[str, Any]]) -> None:
        """Convert mappings before reset; conversion failure leaves existing model and reset signals untouched; success shallow-copies into tuple and resets selection.

        @ac-reusable
        @ac-capability desktop.table.RecordTableModel.set_records
        @ac-kind function
        @ac-tags desktop, table, RecordTableModel
        @ac-contract Convert mappings before reset; conversion failure leaves existing model and reset signals untouched; success shallow-copies into tuple and resets selection.
        @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
        @ac-example See examples/desktop_demo.py and docs/contracts/table.md.
        @ac-tests tests/test_qt.py, tests/test_qt_contracts.py and tests/test_review_qt.py
        """
        copied = tuple(dict(record) for record in records)
        self.beginResetModel()
        self.records = copied
        self.endResetModel()


class PagedTable(QWidget):
    """GUI-thread table with page_size=20, previous/next and extended row selection; page_requested(PageRequest) delegates fetch to host; empty initial page disables navigation.

    @ac-reusable
    @ac-capability desktop.table.PagedTable
    @ac-kind component
    @ac-tags desktop, table, PagedTable
    @ac-contract GUI-thread table with page_size=20, previous/next and extended row selection; page_requested(PageRequest) delegates fetch to host; empty initial page disables navigation.
    @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
    @ac-example See examples/desktop_demo.py and docs/contracts/table.md.
    @ac-tests tests/test_qt.py, tests/test_qt_contracts.py and tests/test_review_qt.py
    """
    page_requested = pyqtSignal(object)

    def __init__(self, columns: Sequence[Column], page_size: int = 20, parent=None):
        super().__init__(parent)
        self.model = RecordTableModel(columns, self)
        self.table = QTableView(self)
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setSelectionMode(QTableView.ExtendedSelection)
        self.request = PageRequest(1, page_size)
        self._page: PageResult | None = None
        self.previous = QPushButton("上一页", self)
        self.next = QPushButton("下一页", self)
        self.page_label = QLabel("0 条", self)
        self.previous.clicked.connect(lambda: self._request_page(self.request.number - 1))
        self.next.clicked.connect(lambda: self._request_page(self.request.number + 1))
        footer = QHBoxLayout()
        footer.addWidget(self.previous)
        footer.addWidget(self.page_label)
        footer.addWidget(self.next)
        layout = QVBoxLayout(self)
        layout.addWidget(self.table)
        layout.addLayout(footer)
        self._update_footer()

    def _request_page(self, number: int) -> None:
        if number < 1 or (self._page and number > self._page.pages):
            return
        self.page_requested.emit(PageRequest(number, self.request.size))

    def set_page(self, page: PageResult) -> None:
        """Display supplied PageResult and update page controls; no fetch, clamping or business validation; record mappings shallow copied.

        @ac-reusable
        @ac-capability desktop.table.PagedTable.set_page
        @ac-kind function
        @ac-tags desktop, table, PagedTable
        @ac-contract Display supplied PageResult and update page controls; no fetch, clamping or business validation; record mappings shallow copied.
        @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
        @ac-example See examples/desktop_demo.py and docs/contracts/table.md.
        @ac-tests tests/test_qt.py, tests/test_qt_contracts.py and tests/test_review_qt.py
        """
        self._page = page
        self.request = page.request
        self.model.set_records(page.items)
        self._update_footer()

    def _update_footer(self) -> None:
        pages = self._page.pages if self._page else 1
        total = self._page.total if self._page else 0
        self.page_label.setText(f"{self.request.number}/{pages} 页 · {total} 条")
        self.previous.setEnabled(self.request.number > 1)
        self.next.setEnabled(self._page is not None and self.request.number < pages)

    def selected_records(self) -> tuple[Mapping[str, Any], ...]:
        """Return selected mappings ordered by displayed row index; empty selection returns empty tuple; no cross-page selection retention.

        @ac-reusable
        @ac-capability desktop.table.PagedTable.selected_records
        @ac-kind function
        @ac-tags desktop, table, PagedTable
        @ac-contract Return selected mappings ordered by displayed row index; empty selection returns empty tuple; no cross-page selection retention.
        @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
        @ac-example See examples/desktop_demo.py and docs/contracts/table.md.
        @ac-tests tests/test_qt.py, tests/test_qt_contracts.py and tests/test_review_qt.py
        """
        rows = sorted({index.row() for index in self.table.selectionModel().selectedRows()})
        return tuple(self.model.records[row] for row in rows)
