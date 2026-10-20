---
title: "desktop.crud_page 公开契约"
category: "工程能力"
tags: ["type/api-contract", "desktop", "crud_page"]
summary: "crud_page 模块的公开输入输出、边界与副作用。"
created: 2026-10-20
updated: 2026-10-20
metadata_status: reviewed
home_area: theme
article_status: published
---

# desktop.crud_page

导入路径：`ctf_desktop.crud_page`。标识一经收录保持稳定。下列契约包含适用边界；外部回调与业务事务由接入方管理。

## CrudPage

稳定标识：`desktop.crud_page.CrudPage`

GUI-thread CRUD composition requiring injected authorized controller, identity_key, columns and fields; filters optional; synchronous host IO; changed(str,object) and operation_failed(str,object) signals.

## CrudPage.load_page

稳定标识：`desktop.crud_page.CrudPage.load_page`

Fetch requested/current page using current filters; display or emit operation_failed(list,error); default page uses current request.

## CrudPage.create_record

稳定标识：`desktop.crud_page.CrudPage.create_record`

Show edit dialog; on accept call controller.create, emit changed and reload first page; controller errors become operation_failed; cancel makes no write.

## CrudPage.edit_selected

稳定标识：`desktop.crud_page.CrudPage.edit_selected`

Require exactly one selected record; show prefilled dialog; accepted edits update identity, emit changed and reload; controller errors become operation_failed.

## CrudPage.show_detail

稳定标识：`desktop.crud_page.CrudPage.show_detail`

Require one selection; authorized detail lookup; show read-only dialog or inform missing record and reload; controller errors become operation_failed(read,error).

## CrudPage.delete_selected

稳定标识：`desktop.crud_page.CrudPage.delete_selected`

Require one selection and affirmative confirmation; authorized delete then changed/reload; cancel makes no write; controller errors become operation_failed.

## 最小调用示例

```python
from PyQt5.QtWidgets import QApplication
from ctf_desktop.crud import CrudController
from ctf_desktop.crud_page import CrudPage
from ctf_desktop.table import Column
from ctf_desktop.forms import FieldSpec
from ctf_desktop.query import PageResult
app = QApplication.instance() or QApplication([])
class Repository:
    def list_page(self, request, filters): return PageResult((), 0, request)
controller = CrudController(Repository(), authorize=lambda action, resource: None)
widget = CrudPage(controller, identity_key="id", columns=[Column("id", "ID")], fields=[FieldSpec("name", "Name")])
widget.load_page()
assert widget.table.model.rowCount() == 0
widget.close()
```
