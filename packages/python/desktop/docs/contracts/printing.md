---
title: "desktop.printing 公开契约"
category: "工程能力"
tags: ["type/api-contract", "desktop", "printing"]
summary: "printing 模块的公开输入输出、边界与副作用。"
created: 2026-10-20
updated: 2026-10-28
metadata_status: reviewed
home_area: theme
article_status: published
---

# desktop.printing

导入路径：`ctf_desktop.printing`。场景接入见 [使用指南](../guides/printing.md)。

## 调用签名与默认值

以下表格核对当前源码声明；`*` 后的参数只能按名称传入。未标注返回类型的接口，其实际输出和异常以本页后续契约为准。

| 接口 | 签名 |
| --- | --- |
| `PrintItem` | `PrintItem(key: str, copies: int = 1)` |
| `BatchPrintResult` | `BatchPrintResult(total: int, succeeded: int, failed: int, skipped: int, error: str \| None = None)` |
| `CancellationToken` | `CancellationToken() -> None` |
| `CancellationToken.cancel` | `cancel() -> None` |
| `BatchPrintRunner` | `BatchPrintRunner(prepare: Callable[[str], bytes], submit: Callable[[bytes], None], *, dispatch_submit: Callable[[Callable[[], None]], None] \| None=None, on_progress: Callable[[str, int, int], None] \| None=None)` |
| `BatchPrintRunner.run` | `run(items: Iterable[PrintItem], token: CancellationToken \| None=None) -> BatchPrintResult` |
| `BatchPrintRunner.start` | `start(items: Iterable[PrintItem], token: CancellationToken \| None=None) -> Future` |
| `BatchPrintRunner.close` | `close() -> None` |

## 配置字段与只读属性

| 字段 / 属性 | 类型 | 默认值 / 要求 |
| --- | --- | --- |
| `PrintItem.key` | `str` | 必填 |
| `PrintItem.copies` | `int` | `1` |
| `BatchPrintResult.total` | `int` | 必填 |
| `BatchPrintResult.succeeded` | `int` | 必填 |
| `BatchPrintResult.failed` | `int` | 必填 |
| `BatchPrintResult.skipped` | `int` | 必填 |
| `BatchPrintResult.error` | `str \| None` | `None` |
| `CancellationToken.cancelled` | `bool` | 只读计算属性 |

## PrintItem

稳定标识：`desktop.printing.PrintItem`

Immutable nonempty key and copies=1 positive integer (bool rejected); ValueError for invalid plan item.

## BatchPrintResult

稳定标识：`desktop.printing.BatchPrintResult`

Immutable total/succeeded/failed/skipped counters and optional error; counts describe submission, not physical paper output.

## CancellationToken

稳定标识：`desktop.printing.CancellationToken`

Thread-safe cooperative flag initially false; no interrupts of in-flight host IO.

## CancellationToken.cancel

稳定标识：`desktop.printing.CancellationToken.cancel`

Set cancellation flag permanently; repeated calls are harmless and return None.

## CancellationToken.cancelled

稳定标识：`desktop.printing.CancellationToken.cancelled`

Read cooperative cancellation flag without mutation.

## BatchPrintRunner

稳定标识：`desktop.printing.BatchPrintRunner`

Inject prepare and submit callbacks; own one executor and exclusive run state; with closes on exit; host supplies synchronous GUI dispatch and bounded IO.

## BatchPrintRunner.run

稳定标识：`desktop.printing.BatchPrintRunner.run`

Exclusively prepare once per item and submit copies in order; RuntimeError on overlapping run or closed runner; cancel at boundaries, no retries; progress errors do not reclassify submissions.

## BatchPrintRunner.start

稳定标识：`desktop.printing.BatchPrintRunner.start`

Snapshot plan then submit on owned single worker; return Future; reject closed runner; GUI dispatcher must synchronously finish submission; callbacks otherwise run on worker.

## BatchPrintRunner.close

稳定标识：`desktop.printing.BatchPrintRunner.close`

Mark closed, cancel queued futures and wait for executor plus any synchronous run; reject self-close from an active callback with RuntimeError; repeatable from owner thread; host IO must have finite completion.

## 上下文管理

| 用法 | 进入 `with` | 离开 `with` |
| --- | --- | --- |
| `with BatchPrintRunner(...) as resource` | 核验尚未关闭并返回自身 | 关闭调度器并等待其工作线程；正常或异常退出都执行，异常不被吞掉 |

清理本身也可能失败；应用应记录并处理未释放资源，不应把进入 `with` 视为业务操作已成功。

## 最小调用示例

```python
from ctf_desktop.printing import BatchPrintRunner, PrintItem
submitted = []
runner = BatchPrintRunner(lambda key: key.encode(), submitted.append)
try:
    assert runner.start([PrintItem("sample", 2)]).result(timeout=2).succeeded == 2
    assert submitted == [b"sample", b"sample"]
finally:
    runner.close()
```
