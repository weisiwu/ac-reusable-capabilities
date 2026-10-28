---
title: "desktop.transport 公开契约"
category: "工程能力"
tags: ["type/api-contract", "desktop", "transport"]
summary: "transport 模块的公开输入输出、边界与副作用。"
created: 2026-10-20
updated: 2026-10-28
metadata_status: reviewed
home_area: theme
article_status: published
---

# desktop.transport

导入路径：`ctf_desktop.transport`。场景接入见 [使用指南](../guides/transport.md)。

## 调用签名与默认值

以下表格核对当前源码声明；`*` 后的参数只能按名称传入。未标注返回类型的接口，其实际输出和异常以本页后续契约为准。

| 接口 | 签名 |
| --- | --- |
| `Transport.open` | `open() -> None` |
| `Transport.close` | `close() -> None` |
| `Transport.write` | `write(payload: bytes) -> None` |
| `Transport.read` | `read(size: int) -> bytes` |
| `SerialConfig` | `SerialConfig(port: str, baudrate: int = 9600, timeout: float = 1.0, write_timeout: float = 1.0)` |
| `SerialTransport` | `SerialTransport(config: SerialConfig, factory: Callable \| None=None)` |
| `SerialTransport.open` | `open() -> None` |
| `SerialTransport.close` | `close() -> None` |
| `SerialTransport.write` | `write(payload: bytes) -> None` |
| `SerialTransport.read` | `read(size: int) -> bytes` |

## 配置字段与只读属性

| 字段 / 属性 | 类型 | 默认值 / 要求 |
| --- | --- | --- |
| `SerialConfig.port` | `str` | 必填 |
| `SerialConfig.baudrate` | `int` | `9600` |
| `SerialConfig.timeout` | `float` | `1.0` |
| `SerialConfig.write_timeout` | `float` | `1.0` |
| `SerialTransport.is_open` | `bool` | 只读计算属性 |

## Transport

稳定标识：`desktop.transport.Transport`

Host-neutral open/close/read/write protocol; concrete implementations define timeout and concurrency semantics; no device commands.

## Transport.open

稳定标识：`desktop.transport.Transport.open`

Open underlying transport or raise its documented error; return None.

## Transport.close

稳定标识：`desktop.transport.Transport.close`

Release underlying transport resources; return None.

## Transport.write

稳定标识：`desktop.transport.Transport.write`

Submit complete payload or raise; return None, not a delivery acknowledgement.

## Transport.read

稳定标识：`desktop.transport.Transport.read`

Return up to size bytes; concrete transport defines timeout/error behavior.

## TransportError

稳定标识：`desktop.transport.TransportError`

IOError for normalized open/read/write failures, chained to underlying cause where available.

## SerialConfig

稳定标识：`desktop.transport.SerialConfig`

Immutable nonblank string port, positive integer baudrate=9600, finite nonnegative numeric timeout=1.0 and write_timeout=1.0; invalid values raise ValueError.

## SerialTransport

稳定标识：`desktop.transport.SerialTransport`

Own one serial handle and RLock; optional factory injection; with opens and closes on every exit; device protocol and retries remain host-owned.

## SerialTransport.open

稳定标识：`desktop.transport.SerialTransport.open`

Idempotently construct serial handle using config; lazy-import pyserial if no factory; TransportError on dependency/open failure.

## SerialTransport.close

稳定标识：`desktop.transport.SerialTransport.close`

Close handle under lock; release ownership only on success; normalize failure as TransportError and retain handle for cleanup retry; repeated successful close harmless.

## SerialTransport.write

稳定标识：`desktop.transport.SerialTransport.write`

Convert payload to bytes, serialize IO, require complete write then flush; TransportError if closed/short write/backend fails; never retry.

## SerialTransport.read

稳定标识：`desktop.transport.SerialTransport.read`

Require nonnegative integer size (bool rejected); serialize IO and return bytes; ValueError for invalid size and TransportError for closed/backend error.

## SerialTransport.is_open

稳定标识：`desktop.transport.SerialTransport.is_open`

Return owned handle open status under lock; false when no handle is owned.

## 上下文管理

| 用法 | 进入 `with` | 离开 `with` |
| --- | --- | --- |
| `with SerialTransport(...) as resource` | 打开串口并返回自身 | 关闭拥有的串口句柄；正常或异常退出都执行，异常不被吞掉 |

清理本身也可能失败；应用应记录并处理未释放资源，不应把进入 `with` 视为业务操作已成功。

## 最小调用示例

```python
from ctf_desktop.transport import SerialConfig, SerialTransport
class Handle:
    is_open = True
    def __init__(self, **kwargs): pass
    def write(self, payload): return len(payload)
    def flush(self): pass
    def read(self, size): return b"ok"[:size]
    def close(self): self.is_open = False
transport = SerialTransport(SerialConfig("example-port"), Handle)
try:
    transport.open()
    transport.write(b"request")
    assert transport.read(2) == b"ok"
finally:
    transport.close()
```
