---
title: "desktop.forms 公开契约"
category: "工程能力"
tags: ["type/api-contract", "desktop", "forms"]
summary: "forms 模块的公开输入输出、边界与副作用。"
created: 2026-10-20
updated: 2026-10-28
metadata_status: reviewed
home_area: theme
article_status: published
required_extra: qt
---

# desktop.forms

导入路径：`ctf_desktop.forms`。场景接入见 [使用指南](../guides/forms.md)。

## 调用签名与默认值

以下表格核对当前源码声明；`*` 后的参数只能按名称传入。未标注返回类型的接口，其实际输出和异常以本页后续契约为准。

| 接口 | 签名 |
| --- | --- |
| `FieldSpec` | `FieldSpec(key: str, label: str, kind: str = 'text', required: bool = False, choices: tuple[tuple[Any, str], ...] = (), validate: Callable[[Any], str \| None] \| None = None, widget_factory: Callable[[Any], QWidget] \| None = None, value_reader: Callable[[QWidget], Any] \| None = None)` |
| `validate_values` | `validate_values(fields: Sequence[FieldSpec], values: Mapping[str, Any]) -> dict[str, str]` |
| `FormDialog` | `FormDialog(title: str, fields: Sequence[FieldSpec], initial=None, parent=None)` |
| `FormDialog.values` | `values() -> dict[str, Any]` |
| `DetailView` | `DetailView(fields: Sequence[FieldSpec], values: Mapping[str, Any], parent=None)` |

## 配置字段与只读属性

| 字段 / 属性 | 类型 | 默认值 / 要求 |
| --- | --- | --- |
| `FieldSpec.key` | `str` | 必填 |
| `FieldSpec.label` | `str` | 必填 |
| `FieldSpec.kind` | `str` | `'text'` |
| `FieldSpec.required` | `bool` | `False` |
| `FieldSpec.choices` | `tuple[tuple[Any, str], ...]` | `()` |
| `FieldSpec.validate` | `Callable[[Any], str \| None] \| None` | `None` |
| `FieldSpec.widget_factory` | `Callable[[Any], QWidget] \| None` | `None` |
| `FieldSpec.value_reader` | `Callable[[QWidget], Any] \| None` | `None` |

## Qt 信号

这些信号在 Qt 线程连接和处理；信号参数中的 `object` 具体含义见使用指南。

| 信号 | 参数类型 |
| --- | --- |
| `FormDialog.submitted` | `(dict)` |
| `FormDialog.validation_failed` | `(object)` |

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
