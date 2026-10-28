---
title: "desktop.table 公开契约"
category: "工程能力"
tags: ["type/api-contract", "desktop", "table"]
summary: "table 模块的公开输入输出、边界与副作用。"
created: 2026-10-20
updated: 2026-10-28
metadata_status: reviewed
home_area: theme
article_status: published
required_extra: qt
---

# desktop.table

导入路径：`ctf_desktop.table`。场景接入见 [使用指南](../guides/table.md)。

## 调用签名与默认值

以下表格核对当前源码声明；`*` 后的参数只能按名称传入。未标注返回类型的接口，其实际输出和异常以本页后续契约为准。

| 接口 | 签名 |
| --- | --- |
| `Column` | `Column(key: str, title: str, display: Callable[[Any], str] = str)` |
| `RecordTableModel` | `RecordTableModel(columns: Sequence[Column], parent=None)` |
| `RecordTableModel.rowCount` | `rowCount(parent=QModelIndex()) -> int` |
| `RecordTableModel.columnCount` | `columnCount(parent=QModelIndex()) -> int` |
| `RecordTableModel.data` | `data(index: QModelIndex, role=Qt.DisplayRole)` |
| `RecordTableModel.headerData` | `headerData(section: int, orientation: Qt.Orientation, role=Qt.DisplayRole)` |
| `RecordTableModel.set_records` | `set_records(records: Sequence[Mapping[str, Any]]) -> None` |
| `PagedTable` | `PagedTable(columns: Sequence[Column], page_size: int=20, parent=None)` |
| `PagedTable.set_page` | `set_page(page: PageResult) -> None` |
| `PagedTable.selected_records` | `selected_records() -> tuple[Mapping[str, Any], ...]` |

## 配置字段与只读属性

| 字段 / 属性 | 类型 | 默认值 / 要求 |
| --- | --- | --- |
| `Column.key` | `str` | 必填 |
| `Column.title` | `str` | 必填 |
| `Column.display` | `Callable[[Any], str]` | `str` |

## Qt 信号

这些信号在 Qt 线程连接和处理；信号参数中的 `object` 具体含义见使用指南。

| 信号 | 参数类型 |
| --- | --- |
| `PagedTable.page_requested` | `(object)` |

## Column

稳定标识：`desktop.table.Column`

Immutable key/title and display callback (str default); rendering only, no SQL or sorting expressions.

## RecordTableModel

稳定标识：`desktop.table.RecordTableModel`

GUI-thread model over mapping records; require nonempty unique columns or ValueError; reset on set_records.

## RecordTableModel.rowCount

稳定标识：`desktop.table.RecordTableModel.rowCount`

Return zero for valid parent (flat model), otherwise current record count.

## RecordTableModel.columnCount

稳定标识：`desktop.table.RecordTableModel.columnCount`

Return zero for valid parent, otherwise column count.

## RecordTableModel.data

稳定标识：`desktop.table.RecordTableModel.data`

Return only for in-bounds indices owned by this model; UserRole returns mapping and DisplayRole formatted/empty text; invalid index/other role returns None; host display callback errors propagate.

## RecordTableModel.headerData

稳定标识：`desktop.table.RecordTableModel.headerData`

Horizontal DisplayRole returns in-bounds title, None for invalid section; other orientation/role delegates to Qt.

## RecordTableModel.set_records

稳定标识：`desktop.table.RecordTableModel.set_records`

Convert mappings before reset; conversion failure leaves existing model and reset signals untouched; success shallow-copies into tuple and resets selection.

## PagedTable

稳定标识：`desktop.table.PagedTable`

GUI-thread table with page_size=20, previous/next and extended row selection; page_requested(PageRequest) delegates fetch to host; empty initial page disables navigation.

## PagedTable.set_page

稳定标识：`desktop.table.PagedTable.set_page`

Display supplied PageResult and update page controls; no fetch, clamping or business validation; record mappings shallow copied.

## PagedTable.selected_records

稳定标识：`desktop.table.PagedTable.selected_records`

Return selected mappings ordered by displayed row index; empty selection returns empty tuple; no cross-page selection retention.

## 最小调用示例

```python
from PyQt5.QtWidgets import QApplication
from ctf_desktop.table import Column, PagedTable
from ctf_desktop.query import PageRequest, PageResult
app = QApplication.instance() or QApplication([])
widget = PagedTable([Column("name", "Name")])
widget.set_page(PageResult(({"name": "sample"},), 1, PageRequest()))
assert widget.model.rowCount() == 1
widget.close()
```
