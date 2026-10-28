---
title: "desktop.navigation 公开契约"
category: "工程能力"
tags: ["type/api-contract", "desktop", "navigation"]
summary: "navigation 模块的公开输入输出、边界与副作用。"
created: 2026-10-20
updated: 2026-10-28
metadata_status: reviewed
home_area: theme
article_status: published
required_extra: qt
---

# desktop.navigation

导入路径：`ctf_desktop.navigation`。场景接入见 [使用指南](../guides/navigation.md)。

## 调用签名与默认值

以下表格核对当前源码声明；`*` 后的参数只能按名称传入。未标注返回类型的接口，其实际输出和异常以本页后续契约为准。

| 接口 | 签名 |
| --- | --- |
| `PageSpec` | `PageSpec(key: str, title: str, create: Callable[[], QWidget])` |
| `PageHost` | `PageHost(parent=None)` |
| `PageHost.register` | `register(spec: PageSpec) -> None` |
| `PageHost.navigate` | `navigate(key: str) -> QWidget` |
| `PageHost.dispose` | `dispose() -> None` |

## 配置字段与只读属性

| 字段 / 属性 | 类型 | 默认值 / 要求 |
| --- | --- | --- |
| `PageSpec.key` | `str` | 必填 |
| `PageSpec.title` | `str` | 必填 |
| `PageSpec.create` | `Callable[[], QWidget]` | 必填 |

## Qt 信号

这些信号在 Qt 线程连接和处理；信号参数中的 `object` 具体含义见使用指南。

| 信号 | 参数类型 |
| --- | --- |
| `PageHost.page_changed` | `(str)` |
| `PageHost.navigation_failed` | `(str, object)` |

## PageSpec

稳定标识：`desktop.navigation.PageSpec`

Immutable route key/title and no-argument QWidget factory; host defines page on_enter/on_leave/dispose hooks.

## PageHost

稳定标识：`desktop.navigation.PageHost`

GUI-thread page registry and lifecycle host; page_changed after success, navigation_failed(key,error) for sidebar failures; lifecycle reentry rejected; caller disposes before shutdown.

## PageHost.register

稳定标识：`desktop.navigation.PageHost.register`

Add nonempty unique route and sidebar item; ValueError for invalid/duplicate key; does not construct page.

## PageHost.navigate

稳定标识：`desktop.navigation.PageHost.navigate`

Reject lifecycle reentry; return cached/new page and emit page_changed only after successful hooks; failed new page is disposed and removed; attempt previous-page restoration and preserve original error with cleanup notes.

## PageHost.dispose

稳定标识：`desktop.navigation.PageHost.dispose`

Reject lifecycle reentry; attempt every cleanup hook, always detach/deleteLater all pages and clear current state; aggregate first cleanup failure as RuntimeError after cleanup; repeatable afterward.

## 最小调用示例

```python
from PyQt5.QtWidgets import QApplication, QWidget
from ctf_desktop.navigation import PageHost, PageSpec
app = QApplication.instance() or QApplication([])
widget = PageHost()
widget.register(PageSpec("sample", "Sample", QWidget))
try:
    first = widget.navigate("sample")
    assert widget.navigate("sample") is first
finally:
    widget.dispose()
    widget.close()
```
