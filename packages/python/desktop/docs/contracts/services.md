---
title: "desktop.services 公开契约"
category: "工程能力"
tags: ["type/api-contract", "desktop", "services"]
summary: "services 模块的公开输入输出、边界与副作用。"
created: 2026-10-20
updated: 2026-10-28
metadata_status: reviewed
home_area: theme
article_status: published
---

# desktop.services

导入路径：`ctf_desktop.services`。场景接入见 [使用指南](../guides/services.md)。

## 调用签名与默认值

以下表格核对当前源码声明；`*` 后的参数只能按名称传入。未标注返回类型的接口，其实际输出和异常以本页后续契约为准。

| 接口 | 签名 |
| --- | --- |
| `ServiceSpec` | `ServiceSpec(name: str, factory: Callable[['ServiceRegistry'], Any], depends_on: tuple[str, ...] = ())` |
| `ServiceRegistry` | `ServiceRegistry() -> None` |
| `ServiceRegistry.register` | `register(spec: ServiceSpec) -> None` |
| `ServiceRegistry.start` | `start() -> None` |
| `ServiceRegistry.get` | `get(name: str) -> Any` |
| `ServiceRegistry.stop` | `stop() -> None` |

## 配置字段与只读属性

| 字段 / 属性 | 类型 | 默认值 / 要求 |
| --- | --- | --- |
| `ServiceSpec.name` | `str` | 必填 |
| `ServiceSpec.factory` | `Callable[['ServiceRegistry'], Any]` | 必填 |
| `ServiceSpec.depends_on` | `tuple[str, ...]` | `()` |
| `ServiceRegistry.running` | `bool` | 只读计算属性 |

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

## 上下文管理

| 用法 | 进入 `with` | 离开 `with` |
| --- | --- | --- |
| `with ServiceRegistry(...) as resource` | 按依赖启动并返回自身 | 反序停止已启动服务；正常或异常退出都执行，异常不被吞掉 |

清理本身也可能失败；应用应记录并处理未释放资源，不应把进入 `with` 视为业务操作已成功。

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
