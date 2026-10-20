---
title: "desktop.navigation 公开契约"
category: "工程能力"
tags: ["type/api-contract", "desktop", "navigation"]
summary: "navigation 模块的公开输入输出、边界与副作用。"
created: 2026-10-20
updated: 2026-10-20
metadata_status: reviewed
home_area: theme
article_status: published
---

# desktop.navigation

导入路径：`ctf_desktop.navigation`。标识一经收录保持稳定。下列契约包含适用边界；外部回调与业务事务由接入方管理。

## PageSpec

稳定标识：`desktop.navigation.PageSpec`

Immutable route key/title and no-argument QWidget factory; host defines page on_enter/on_leave/dispose hooks.

## PageHost

稳定标识：`desktop.navigation.PageHost`

GUI-thread registry caching one widget per route; page_changed(str) after successful navigation; caller invokes dispose before shutdown.

## PageHost.register

稳定标识：`desktop.navigation.PageHost.register`

Add nonempty unique route and sidebar item; ValueError for invalid/duplicate key; does not construct page.

## PageHost.navigate

稳定标识：`desktop.navigation.PageHost.navigate`

Return cached/new QWidget; KeyError for unknown route, TypeError for bad factory; call leave/enter and emit on success; failed enter attempts previous-page restoration; no-op on current route.

## PageHost.dispose

稳定标识：`desktop.navigation.PageHost.dispose`

Invoke cached page cleanup hooks then detach/deleteLater widgets and clear current route; repeatable if cleanup succeeds; hook errors propagate.

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
