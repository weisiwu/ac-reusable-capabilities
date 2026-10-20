---
title: "desktop.services 公开契约"
category: "工程能力"
tags: ["type/api-contract", "desktop", "services"]
summary: "services 模块的公开输入输出、边界与副作用。"
created: 2026-10-20
updated: 2026-10-20
metadata_status: reviewed
home_area: theme
article_status: published
---

# desktop.services

导入路径：`ctf_desktop.services`。场景接入见 [使用指南](../guides/services.md)。

## ServiceSpec

稳定标识：`desktop.services.ServiceSpec`

Immutable name, registry-aware factory and dependency names (default empty); host owns service implementations.

## ServiceStartError

稳定标识：`desktop.services.ServiceStartError`

RuntimeError raised with original cause after start failure and attempted reverse cleanup.

## ServiceRegistry

稳定标识：`desktop.services.ServiceRegistry`

Own registered services, topological startup and reverse cleanup; with starts/stops; lifecycle callback reentry rejected; single-threaded registry.

## ServiceRegistry.register

稳定标识：`desktop.services.ServiceRegistry.register`

Register unique ServiceSpec before start; ValueError for duplicate/running registry; RuntimeError during start/stop callbacks; no lazy initialization.

## ServiceRegistry.start

稳定标识：`desktop.services.ServiceRegistry.start`

Topologically validate dependencies, start instances and rollback on error; lifecycle callback reentry rejected; ServiceStartError chains original failure and notes cleanup failure.

## ServiceRegistry.get

稳定标识：`desktop.services.ServiceRegistry.get`

Return current instance by name or raise KeyError; never lazily create services.

## ServiceRegistry.stop

稳定标识：`desktop.services.ServiceRegistry.stop`

Attempt every reverse-order cleanup including stop attribute lookup; always clear ownership, then raise RuntimeError from first failure; reentry rejected; idle stop harmless.

## ServiceRegistry.running

稳定标识：`desktop.services.ServiceRegistry.running`

Return whether registry owns any started services; does not inspect worker health.

## 最小调用示例

```python
from ctf_desktop.services import ServiceRegistry, ServiceSpec
registry = ServiceRegistry()
registry.register(ServiceSpec("sample", lambda registry: object()))
try:
    registry.start()
    assert registry.running and registry.get("sample") is not None
finally:
    registry.stop()
```
