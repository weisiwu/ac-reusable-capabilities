---
title: "desktop.table 公开契约"
category: "工程能力"
tags: ["type/api-contract", "desktop", "table"]
summary: "table 模块的公开输入输出、边界与副作用。"
created: 2026-10-20
updated: 2026-10-20
metadata_status: reviewed
home_area: theme
article_status: published
required_extra: qt
---

# desktop.table

导入路径：`ctf_desktop.table`。场景接入见 [使用指南](../guides/table.md)。

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
