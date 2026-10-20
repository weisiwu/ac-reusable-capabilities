---
title: "筛选与联想输入使用指南"
category: "工程能力"
tags: ["desktop", "filters", "type/usage-guide"]
summary: "筛选与联想输入的场景选择、接入步骤、错误处理、资源所有权与验证入口。"
created: 2026-10-20
updated: 2026-10-20
metadata_status: reviewed
home_area: theme
article_status: published
---

# 筛选与联想输入

## 适用场景

管理页收集条件，或异步获取联想选项。

## 接口与接入

FilterField 支持文本、选项、日期范围；FilterPanel 发查询/重置信号；LiveSearchComboBox 防抖后发查询文字。

字段键非空唯一。search_requested 后由应用发起查询；结果使用 set_results(query, pairs) 应用到当前文字。所有选项先验证再改控件。

## 失败与边界

过期文字结果返回 false；格式不对抛 ValueError 且保持旧选项；更新选项恢复原信号屏蔽状态。日期 1900-01-01 为不限哨兵，结束日期转换由应用负责。

完整异步接入可监听 request_started(request_id,query)，并把 ID 传给 set_results；BackgroundTaskRunner 提供有界 latest-wins 任务、取消和超时。日期先后关系由应用校验。

## 线程与资源

GUI 线程操作控件；查询 IO 在应用层调度并用信号回传；防抖计时器由控件拥有。

## 示例与验证

- [最小调用与公开契约](../contracts/filters.md)。每个模块的最小例子均由 `python examples/check_contract_examples.py` 执行；Qt 模块追加 `--qt`。
- [异常与恢复场景](../../examples/failure_scenarios.py)；[可交互桌面示例](../../examples/qt_showcase.py)。
- 验证入口：`tests/test_qt.py、tests/test_qt_contracts.py、tests/test_review_qt.py`。

异步结果不能直接从后台线程修改 Qt 控件。
