---
title: "desktop.filters 公开契约"
category: "工程能力"
tags: ["type/api-contract", "desktop", "filters"]
summary: "filters 模块的公开输入输出、边界与副作用。"
created: 2026-10-20
updated: 2026-10-28
metadata_status: reviewed
home_area: theme
article_status: published
required_extra: qt
---

# desktop.filters

导入路径：`ctf_desktop.filters`。场景接入见 [使用指南](../guides/filters.md)。

## 调用签名与默认值

以下表格核对当前源码声明；`*` 后的参数只能按名称传入。未标注返回类型的接口，其实际输出和异常以本页后续契约为准。

| 接口 | 签名 |
| --- | --- |
| `FilterField` | `FilterField(key: str, label: str, kind: str = 'text', choices: tuple[tuple[Any, str], ...] = ())` |
| `FilterPanel` | `FilterPanel(fields: Sequence[FilterField], parent=None)` |
| `FilterPanel.values` | `values() -> dict[str, Any]` |
| `FilterPanel.clear` | `clear() -> None` |
| `LiveSearchComboBox` | `LiveSearchComboBox(delay_ms: int=200, parent=None)` |
| `LiveSearchComboBox.set_results` | `set_results(query: str, results: Sequence[tuple[Any, str]], *, request_id: int \| None=None) -> bool` |

## 配置字段与只读属性

| 字段 / 属性 | 类型 | 默认值 / 要求 |
| --- | --- | --- |
| `FilterField.key` | `str` | 必填 |
| `FilterField.label` | `str` | 必填 |
| `FilterField.kind` | `str` | `'text'` |
| `FilterField.choices` | `tuple[tuple[Any, str], ...]` | `()` |

## Qt 信号

这些信号在 Qt 线程连接和处理；信号参数中的 `object` 具体含义见使用指南。

| 信号 | 参数类型 |
| --- | --- |
| `FilterPanel.search_requested` | `(dict)` |
| `FilterPanel.reset_requested` | `()` |
| `LiveSearchComboBox.search_requested` | `(str)` |
| `LiveSearchComboBox.request_started` | `(int, str)` |

## FilterField

稳定标识：`desktop.filters.FilterField`

Immutable key/label, kind=text, optional choice pairs; supports text/choice/date_range, else ValueError.

## FilterPanel

稳定标识：`desktop.filters.FilterPanel`

GUI-thread filters with unique nonempty keys; search_requested(dict) on search and reset_requested on clear; no persistence or SQL execution.

## FilterPanel.values

稳定标识：`desktop.filters.FilterPanel.values`

Return nonempty filter values; strip text, choices return data, date ranges return ISO start/end or None; 1900-01-01 is the unset sentinel.

## FilterPanel.clear

稳定标识：`desktop.filters.FilterPanel.clear`

Reset text/choice/date widgets and emit reset_requested; repeatable; never starts IO.

## LiveSearchComboBox

稳定标识：`desktop.filters.LiveSearchComboBox`

GUI-thread editable combo; debounce edits then emit request_started(id,text) and compatible search_requested(text); IDs advance on edits and requests; request_id in set_results rejects same-text stale responses.

## LiveSearchComboBox.set_results

稳定标识：`desktop.filters.LiveSearchComboBox.set_results`

Reject stale query or optional request_id with false; validate all (value,text) pairs before mutation; preserve prior signal-block state on all exits, replace results and return true; old calls without request_id retain text-only comparison.

## 最小调用示例

```python
from PyQt5.QtWidgets import QApplication
from ctf_desktop.filters import FilterField, FilterPanel
app = QApplication.instance() or QApplication([])
widget = FilterPanel([FilterField("name", "Name")])
assert widget.values() == {}
widget.clear()
widget.close()
```
