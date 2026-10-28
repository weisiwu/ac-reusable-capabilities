---
title: "desktop.feedback 公开契约"
category: "工程能力"
tags: ["type/api-contract", "desktop", "feedback"]
summary: "feedback 模块的公开输入输出、边界与副作用。"
created: 2026-10-20
updated: 2026-10-28
metadata_status: reviewed
home_area: theme
article_status: published
required_extra: qt
---

# desktop.feedback

导入路径：`ctf_desktop.feedback`。场景接入见 [使用指南](../guides/feedback.md)。

## 调用签名与默认值

以下表格核对当前源码声明；`*` 后的参数只能按名称传入。未标注返回类型的接口，其实际输出和异常以本页后续契约为准。

| 接口 | 签名 |
| --- | --- |
| `ConfirmDialog.ask` | `ask(parent: QWidget \| None, title: str, message: str) -> bool` |
| `EmptyState` | `EmptyState(title: str, detail: str='', parent=None)` |
| `BusyOverlay` | `BusyOverlay(parent: QWidget)` |
| `BusyOverlay.show_message` | `show_message(message: str) -> None` |
| `Toast` | `Toast(parent: QWidget)` |
| `Toast.show_message` | `show_message(message: str, duration_ms: int=3000) -> None` |

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

GUI-thread child overlay initially hidden; automatically follows parent resize; caller controls visibility and owns cancellation/work.

## BusyOverlay.show_message

稳定标识：`desktop.feedback.BusyOverlay.show_message`

Cover parent current rect, set wording and show/raise; parent resize events maintain geometry while widget exists.

## Toast

稳定标识：`desktop.feedback.Toast`

GUI-thread label initially hidden; parent owns it; fixed-style temporary feedback.

## Toast.show_message

稳定标识：`desktop.feedback.Toast.show_message`

Validate nonnegative integer duration_ms=3000 before mutation; show message and restart one owned timer so earlier messages cannot hide newer ones.

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
