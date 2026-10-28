---
title: "批量打印调度使用指南"
category: "工程能力"
tags: ["desktop", "printing", "type/usage-guide"]
summary: "批量打印调度的场景选择、接入步骤、错误处理、资源所有权与验证入口。"
created: 2026-10-20
updated: 2026-10-28
metadata_status: reviewed
home_area: theme
article_status: published
---

# 批量打印调度


## 接入速查

| 接入项 | 要求 / 用法 |
| --- | --- |
| 环境与依赖 | 标准库；应用注入 prepare / submit |
| 核心入口 | `BatchPrintRunner` / `PrintItem` |
| 调用顺序 | 准备成品 → 逐份取消检查 → 提交 → 统计结果 → close |
| 关键边界 | 计数表示提交；未知提交错误停止且不自动重试 |
| 方法 / 属性 | `run`, `start`, `close` |
| 版本与兼容 | [依赖说明](../架构与依赖.md) · [升级说明](../升级与兼容.md) |

## 接入流程

```mermaid
flowchart LR
    N0["准备成品"]
    N1["逐份取消检查"]
    N0 --> N1
    N2["提交"]
    N1 --> N2
    N3["统计结果"]
    N2 --> N3
    N4["close"]
    N3 --> N4
```


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
