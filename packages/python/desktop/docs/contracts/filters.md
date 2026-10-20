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
---

# desktop.filters

导入路径：`ctf_desktop.filters`。标识一经收录保持稳定。下列契约包含适用边界；外部回调与业务事务由接入方管理。

## FilterField

稳定标识：`desktop.filters.FilterField`

Immutable key/label, kind=text, optional choice pairs; supports text/choice/date_range, else ValueError.

## FilterPanel

稳定标识：`desktop.filters.FilterPanel`

GUI-thread filter widgets; search_requested(dict) on search and reset_requested on clear; no persistence or SQL execution.

## FilterPanel.values

稳定标识：`desktop.filters.FilterPanel.values`

Return nonempty filter values; strip text, choices return data, date ranges return ISO start/end or None; 1900-01-01 is the unset sentinel.

## FilterPanel.clear

稳定标识：`desktop.filters.FilterPanel.clear`

Reset text/choice/date widgets and emit reset_requested; repeatable; never starts IO.

## LiveSearchComboBox

稳定标识：`desktop.filters.LiveSearchComboBox`

GUI-thread editable combo; debounce user edits by delay_ms=200 and emit search_requested(str); caller performs query; text matching is not request-generation ordering.

## LiveSearchComboBox.set_results

稳定标识：`desktop.filters.LiveSearchComboBox.set_results`

Reject query unequal to current stripped text with false; otherwise replace (id,label) results, preserve text, show popup and return true; repeated same-text request races must be handled by caller.

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
