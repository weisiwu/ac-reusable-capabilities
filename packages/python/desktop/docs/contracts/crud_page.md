---
title: "desktop.crud_page 公开契约"
category: "工程能力"
tags: ["type/api-contract", "desktop", "crud_page"]
summary: "crud_page 模块的公开输入输出、边界与副作用。"
created: 2026-10-20
updated: 2026-10-28
metadata_status: reviewed
home_area: theme
article_status: published
required_extra: qt
---

# desktop.crud_page

导入路径：`ctf_desktop.crud_page`。场景接入见 [使用指南](../guides/crud_page.md)。

## 调用签名与默认值

以下表格核对当前源码声明；`*` 后的参数只能按名称传入。未标注返回类型的接口，其实际输出和异常以本页后续契约为准。

| 接口 | 签名 |
| --- | --- |
| `CrudPage` | `CrudPage(controller: CrudController, *, identity_key: str, columns: Sequence[Column], fields: Sequence[FieldSpec], filters: Sequence[FilterField]=(), parent=None)` |
| `CrudPage.load_page` | `load_page(request: PageRequest \| None=None) -> None` |
| `CrudPage.create_record` | `create_record() -> None` |
| `CrudPage.edit_selected` | `edit_selected() -> None` |
| `CrudPage.show_detail` | `show_detail() -> None` |
| `CrudPage.delete_selected` | `delete_selected() -> None` |

## Qt 信号

这些信号在 Qt 线程连接和处理；信号参数中的 `object` 具体含义见使用指南。

| 信号 | 参数类型 |
| --- | --- |
| `CrudPage.changed` | `(str, object)` |
| `CrudPage.operation_failed` | `(str, object)` |

## CrudPage

稳定标识：`desktop.crud_page.CrudPage`

GUI-thread synchronous CRUD composition; missing identity emits operation_failed(action,ValueError); completed modal dialogs scheduled for deletion; changed and operation_failed signals delegate policy to host.

## CrudPage.load_page

稳定标识：`desktop.crud_page.CrudPage.load_page`

Fetch requested/current page using current filters; display or emit operation_failed(list,error); default page uses current request.

## CrudPage.create_record

稳定标识：`desktop.crud_page.CrudPage.create_record`

Open form, call authorized create only on acceptance, emit changed/reload first page; report controller errors and delete dialog on every exit.

## CrudPage.edit_selected

稳定标识：`desktop.crud_page.CrudPage.edit_selected`

Require one selected record with identity; report missing identity as operation_failed(update,error); accepted form updates then reloads; always delete dialog.

## CrudPage.show_detail

稳定标识：`desktop.crud_page.CrudPage.show_detail`

Require selected identity; authorized lookup errors become operation_failed(read,error); show detail or reload missing row; always delete detail dialog.

## CrudPage.delete_selected

稳定标识：`desktop.crud_page.CrudPage.delete_selected`

Require selected identity and affirmative confirmation; report malformed identity or controller failure; successful delete emits changed and reloads; cancellation writes nothing.

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
