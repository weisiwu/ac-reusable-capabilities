---
title: "批量打印调度使用指南"
category: "工程能力"
tags: ["desktop", "printing", "type/usage-guide"]
summary: "批量打印调度的场景选择、接入步骤、错误处理、资源所有权与验证入口。"
created: 2026-10-20
updated: 2026-10-20
metadata_status: reviewed
home_area: theme
article_status: published
---

# 批量打印调度

## 适用场景

一条数据准备一次成品，多份提交，有取消和失败统计。

## 接口与接入

PrintItem 声明 key/copies；BatchPrintRunner 负责准备与提交；CancellationToken 是协作取消；BatchPrintResult 描述提交计数。

prepare 返回非空 bytes；submit 成功返回 None，失败抛异常；真实 Qt 打印通过同步 dispatch_submit 回到 GUI 线程。

## 失败与边界

单条的 copies 共用一次准备结果；提交结果不确定时停止且不重试。取消在准备前和每份提交前检查，不能打断正在执行的 IO。重叠 run 或关闭后运行抛 RuntimeError。

计数代表提交，不代表打印机实际出纸。不能把失败提交自动重试，否则可能重复打印。没有 PDF 摘要缓存或跨批次去重。

## 线程与资源

start 在单工作线程运行；progress 也在那里。close 在拥有者线程调用并等待，不在 worker 回调内关闭；所有外部 IO 必须有有限超时。

## 示例与验证

- [最小调用与公开契约](../contracts/printing.md)。每个模块的最小例子均由 `python examples/check_contract_examples.py` 执行；Qt 模块追加 `--qt`。
- [异常与恢复场景](../../examples/failure_scenarios.py)；[可交互桌面示例](../../examples/qt_showcase.py)。
- 验证入口：`tests/test_core.py、tests/test_contracts.py、tests/test_review_core.py`。

取消、空成品、未知提交失败与正常打印都要展示为不同反馈。
