---
title: "desktop.background 公开契约"
category: "工程能力"
tags: ["desktop", "async", "type/api-contract"]
summary: "后台任务提交、取消、超时与资源释放的公开契约。"
created: 2026-10-20
updated: 2026-10-28
metadata_status: reviewed
home_area: theme
article_status: published
required_extra: qt
---

# desktop.background

导入路径：`ctf_desktop.background`。场景接入见 [使用指南](../guides/background.md)。

## 调用签名与默认值

以下表格核对当前源码声明；`*` 后的参数只能按名称传入。未标注返回类型的接口，其实际输出和异常以本页后续契约为准。

| 接口 | 签名 |
| --- | --- |
| `BackgroundTaskRunner` | `BackgroundTaskRunner(parent=None)` |
| `BackgroundTaskRunner.submit` | `submit(operation: Callable[[Event], Any], *, timeout_ms: int \| None=None) -> int` |
| `BackgroundTaskRunner.cancel` | `cancel() -> None` |
| `BackgroundTaskRunner.close` | `close(*, wait: bool=True) -> None` |

## Qt 信号

这些信号在 Qt 线程连接和处理；信号参数中的 `object` 具体含义见使用指南。

| 信号 | 参数类型 |
| --- | --- |
| `BackgroundTaskRunner.succeeded` | `(int, object)` |
| `BackgroundTaskRunner.failed` | `(int, object)` |
| `BackgroundTaskRunner.cancelled` | `(int)` |
| `BackgroundTaskRunner.timed_out` | `(int)` |

## BackgroundTaskRunner

稳定标识：`desktop.background.BackgroundTaskRunner`

Qt-thread owned latest-request runner with one active worker and one replaceable pending slot; operation(Event) owns bounded IO; succeeded/failed/cancelled/timed_out signals; explicit close or parent destruction cancels; no forced termination. operation(Event) runs on one worker. Latest results/errors are delivered on Qt thread via succeeded(id,value)/failed(id,error). Replacing work cancels prior work cooperatively; cancelled(id)/timed_out(id) are distinct. Timeout suppresses late results, not native/preemptive thread execution. At most one task waits behind active work; no unbounded executor queue.

## BackgroundTaskRunner.submit

稳定标识：`desktop.background.BackgroundTaskRunner.submit`

Require callable operation and optional positive integer timeout_ms within Qt int range; invalid input raises before mutation. Closed runner raises RuntimeError. Operation must observe Event and use bounded external IO; it must never access Qt widgets.

## BackgroundTaskRunner.cancel

稳定标识：`desktop.background.BackgroundTaskRunner.cancel`

Stop deadline timer, cancel pending slot and signal active worker Event; emit cancelled(id) once if UI considers a task active. Does not interrupt in-flight IO; repeated idle cancel is harmless.

## BackgroundTaskRunner.close

稳定标识：`desktop.background.BackgroundTaskRunner.close`

Mark closed, suppress further results and cancel work. wait=True joins worker; only safe with cooperative, bounded IO and outside worker callbacks. wait=False returns before worker cleanup; a later close(wait=True) can join. QObject destruction also cancels without blocking. No unsafe thread termination or silent restart.

## 最小调用示例

```python
from PyQt5.QtWidgets import QApplication
from ctf_desktop.background import BackgroundTaskRunner
app = QApplication.instance() or QApplication([])
runner = BackgroundTaskRunner()
try:
    identity = runner.submit(lambda cancel_event: 42, timeout_ms=1000)
    assert identity == 1
finally:
    runner.close()
```
