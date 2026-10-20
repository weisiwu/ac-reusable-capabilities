---
title: "后台任务与异步查询使用指南"
category: "工程能力"
tags: ["desktop", "async", "type/usage-guide"]
summary: "有界的最新请求任务、Qt线程交付、协作取消、超时和关闭。"
created: 2026-10-20
updated: 2026-10-20
metadata_status: reviewed
home_area: theme
article_status: published
---

# 后台任务与异步查询

## 使用场景

慢列表查询、联想输入、加载只读详情等只关心最新结果的任务。使用 BackgroundTaskRunner 将 IO 移出 GUI；只允许一个执行中任务和一个待执行任务，新请求替换等待槽，不为每次按键积累无界任务队列。

这不是批量队列；写入、收费、打印等必须执行每条请求的操作不能直接套用 latest-wins。它也不强制杀线程或终止原生库。

## 接口与信号

在 Qt 线程构造并调用 runner。submit(operation, timeout_ms=None) 返回递增请求 ID；operation 接收 threading.Event，在后台线程执行。正常结果通过 succeeded(id,value)，错误通过 failed(id,error) 回到 Qt 线程。取消与超时分别发 cancelled(id)、timed_out(id)，迟到结果被忽略。

每个回调自己创建/关闭该线程使用的数据库连接或 HTTP/串口句柄，不把 SqliteStore 的 GUI 线程连接传过去。外部 IO 设置超时，循环使用 event.wait 或检查 is_set；取消不是抢占式中断。

## 信号回调中的重入

替换任务时，先完成新任务的编号、等待槽和超时设置，再发出旧任务的 cancelled 通知。通知回调可以再次 submit 或 close；回调里提交的任务代次更新，外层 submit 仍返回自身的编号，不覆盖回调的状态。被取消的操作可能已经开始执行，因此仍须观察取消 Event，不能依赖取消撤销副作用。

close 在发出取消通知前已标记关闭；通知回调可以重复 close，随后 submit 会被拒绝。同一次联想搜索的 request_started 和 search_requested 使用相同文字快照，即使第一个信号的回调改了输入框。

## 生命周期

显式 close() 默认等待后台资源释放；只能在操作有有限结束条件时使用。close(wait=False) 先取消返回，之后 close(wait=True) 可以等待。QObject 父对象销毁会非阻塞取消；它不能保证不合作的第三方调用马上退出。不得在后台 operation 内关闭并等待自己的 worker。

## 联想输入配合

监听 LiveSearchComboBox.request_started(request_id,query)，将 ID 和文字一起作为任务输入。结果在 GUI 线程调用 set_results(query,rows,request_id=request_id)。这样同样文字的旧请求也会被拒绝。原 search_requested(query) 和不带 request_id 的调用保持兼容，但旧用法只有文字比较，不具备代次保证。

[完整搜索例子](../../examples/background_search.py) 可交互运行，也支持 --smoke 自动验证后退出。任务的正常、异常、取消、超时、队列上限、相同关键词乱序及父对象销毁见 tests/test_background.py。
