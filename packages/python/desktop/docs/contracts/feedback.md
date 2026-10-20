---
title: "desktop.feedback 公开契约"
category: "工程能力"
tags: ["type/api-contract", "desktop", "feedback"]
summary: "feedback 模块的公开输入输出、边界与副作用。"
created: 2026-10-20
updated: 2026-10-20
metadata_status: reviewed
home_area: theme
article_status: published
---

# desktop.feedback

导入路径：`ctf_desktop.feedback`。标识一经收录保持稳定。下列契约包含适用边界；外部回调与业务事务由接入方管理。

## ConfirmDialog

稳定标识：`desktop.feedback.ConfirmDialog`

GUI-thread yes/no confirmation wrapper; caller supplies wording, default response No.

## ConfirmDialog.ask

稳定标识：`desktop.feedback.ConfirmDialog.ask`

Block in Qt question dialog; return true only for Yes, false otherwise; parent/title/message are caller-owned.

## EmptyState

稳定标识：`desktop.feedback.EmptyState`

GUI-thread static title/detail labels, empty detail default; parent owns lifetime.

## BusyOverlay

稳定标识：`desktop.feedback.BusyOverlay`

GUI-thread child overlay initially hidden; no background work or cancellation; caller hides/closes it.

## BusyOverlay.show_message

稳定标识：`desktop.feedback.BusyOverlay.show_message`

Set wording, cover current parent rect and show/raise; caller must refresh geometry after later parent resize.

## Toast

稳定标识：`desktop.feedback.Toast`

GUI-thread label initially hidden; parent owns it; fixed-style temporary feedback.

## Toast.show_message

稳定标识：`desktop.feedback.Toast.show_message`

Show centered-top wording and schedule hide after duration_ms=3000; older timers are not reset, so overlapping calls may hide earlier.

## 最小调用示例

```python
from PyQt5.QtWidgets import QApplication, QWidget
from ctf_desktop.feedback import EmptyState, BusyOverlay, Toast
app = QApplication.instance() or QApplication([])
parent = QWidget()
empty = EmptyState("Empty", parent=parent)
overlay = BusyOverlay(parent)
overlay.show_message("Working")
Toast(parent).show_message("Done", 100)
parent.close()
```
