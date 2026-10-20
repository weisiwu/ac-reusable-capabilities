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
---

# desktop.table

导入路径：`ctf_desktop.table`。标识一经收录保持稳定。下列契约包含适用边界；外部回调与业务事务由接入方管理。

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

For valid model index return mapping for UserRole or formatted/empty text for DisplayRole; invalid index/other role returns None; formatter errors propagate.

## RecordTableModel.headerData

稳定标识：`desktop.table.RecordTableModel.headerData`

Horizontal DisplayRole returns column title; other orientation/role delegates to Qt.

## RecordTableModel.set_records

稳定标识：`desktop.table.RecordTableModel.set_records`

Shallow-copy mappings into tuple inside model reset; clear selection through Qt reset; no database access.

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
