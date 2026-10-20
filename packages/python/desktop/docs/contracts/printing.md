---
title: "desktop.printing 公开契约"
category: "工程能力"
tags: ["type/api-contract", "desktop", "printing"]
summary: "printing 模块的公开输入输出、边界与副作用。"
created: 2026-10-20
updated: 2026-10-20
metadata_status: reviewed
home_area: theme
article_status: published
---

# desktop.printing

导入路径：`ctf_desktop.printing`。场景接入见 [使用指南](../guides/printing.md)。

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
