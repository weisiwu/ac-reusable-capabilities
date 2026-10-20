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

导入路径：`ctf_desktop.printing`。标识一经收录保持稳定。下列契约包含适用边界；外部回调与业务事务由接入方管理。

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

Inject byte preparation and submission; own one executor; optional blocking GUI dispatcher and progress callback; call close at shutdown.

## BatchPrintRunner.run

稳定标识：`desktop.printing.BatchPrintRunner.run`

Prepare once per plan item and submit each copy; stop at cancellation boundaries or first error; never retry uncertain submissions; progress errors are reported without reclassifying copies.

## BatchPrintRunner.start

稳定标识：`desktop.printing.BatchPrintRunner.start`

Snapshot plan then schedule run on owned worker; return Future; callbacks run there unless dispatch_submit synchronously marshals submission; no automatic retries.

## BatchPrintRunner.close

稳定标识：`desktop.printing.BatchPrintRunner.close`

Wait for executor shutdown and cancel queued tasks; running host callbacks must terminate; no preemptive IO timeout.

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
