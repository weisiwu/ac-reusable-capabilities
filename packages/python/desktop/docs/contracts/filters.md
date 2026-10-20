---
title: "desktop.filters 公开契约"
category: "工程能力"
tags: ["type/api-contract", "desktop", "filters"]
summary: "filters 模块的公开输入输出、边界与副作用。"
created: 2026-10-20
updated: 2026-10-20
metadata_status: reviewed
home_area: theme
article_status: published
required_extra: qt
---

# desktop.filters

导入路径：`ctf_desktop.filters`。场景接入见 [使用指南](../guides/filters.md)。

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
