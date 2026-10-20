---
title: "desktop.forms 公开契约"
category: "工程能力"
tags: ["type/api-contract", "desktop", "forms"]
summary: "forms 模块的公开输入输出、边界与副作用。"
created: 2026-10-20
updated: 2026-10-20
metadata_status: reviewed
home_area: theme
article_status: published
required_extra: qt
---

# desktop.forms

导入路径：`ctf_desktop.forms`。场景接入见 [使用指南](../guides/forms.md)。

## FieldSpec

稳定标识：`desktop.forms.FieldSpec`

Immutable field key/label; text default, required false; supports multiline/integer/boolean/choice/custom; custom requires factory and reader; invalid kind raises ValueError.

## validate_values

稳定标识：`desktop.forms.validate_values`

Return field-key to error-text mapping for required/host validator failures; false and zero are valid required values; validator exceptions propagate; no writes.

## FormDialog

稳定标识：`desktop.forms.FormDialog`

GUI-thread form with unique nonempty keys; preserve zero/false initial text; submitted(dict) on valid save; callback exceptions emit validation_failed(error) and keep dialog open; cancel rejects.

## FormDialog.values

稳定标识：`desktop.forms.FormDialog.values`

Read current fields to new mapping; text stripped, choice returns data, integer/bool preserve types; custom reader errors propagate.

## DetailView

稳定标识：`desktop.forms.DetailView`

GUI-thread read-only labels for provided fields/values; None displays empty text, others stringify; parent owns widget lifetime.

## 最小调用示例

```python
from PyQt5.QtWidgets import QApplication
from ctf_desktop.forms import FieldSpec, FormDialog, validate_values
app = QApplication.instance() or QApplication([])
fields = [FieldSpec("name", "Name", required=True)]
assert validate_values(fields, {"name": ""}) == {"name": "必填"}
widget = FormDialog("Sample", fields, {"name": "sample"})
assert widget.values() == {"name": "sample"}
widget.close()
```
