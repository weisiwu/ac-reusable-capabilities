---
title: "反馈控件使用指南"
category: "工程能力"
tags: ["desktop", "feedback", "type/usage-guide"]
summary: "反馈控件的场景选择、接入步骤、错误处理、资源所有权与验证入口。"
created: 2026-10-20
updated: 2026-10-20
metadata_status: reviewed
home_area: theme
article_status: published
---

# 反馈控件

## 适用场景

让应用组合确认框、空态、忙碌遮罩与短时提示。

## 接口与接入

ConfirmDialog 默认选择 No；EmptyState 为标签；BusyOverlay 跟随父窗大小；Toast 拥有可重启的单次隐藏计时器。

应用提供文案；确认框返回 true 才写入；显示 busy 前启动任务、完成/失败后 hide；重复 toast 会替换文案并重新计时。

## 失败与边界

Toast duration_ms 必须非负整数，非法参数在改变界面前拒绝；新文案不会被旧文案计时器提前隐藏。

busy 不执行任务或自动取消；确认框不执行权限检查。默认样式是参考值，可由应用主题替换。

## 线程与资源

GUI 线程使用，父窗口拥有控件；父窗口销毁后计时器一同销毁，不创建常驻线程。

## 示例与验证

- [最小调用与公开契约](../contracts/feedback.md)。每个模块的最小例子均由 `python examples/check_contract_examples.py` 执行；Qt 模块追加 `--qt`。
- [异常与恢复场景](../../examples/failure_scenarios.py)；[可交互桌面示例](../../examples/qt_showcase.py)。
- 验证入口：`tests/test_qt.py、tests/test_qt_contracts.py、tests/test_review_qt.py`。

业务失败、用户取消和成功提示区分处理，不用成功 toast 掩盖操作错误。
