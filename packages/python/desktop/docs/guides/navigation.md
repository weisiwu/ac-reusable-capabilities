---
title: "页面导航使用指南"
category: "工程能力"
tags: ["desktop", "navigation", "type/usage-guide"]
summary: "页面导航的场景选择、接入步骤、错误处理、资源所有权与验证入口。"
created: 2026-10-20
updated: 2026-10-20
metadata_status: reviewed
home_area: theme
article_status: published
---

# 页面导航

## 适用场景

按路由懒加载一次页面，并执行进入、离开与清理回调。

## 接口与接入

PageSpec 提供 key/title/factory；PageHost 缓存 QWidget；可选 on_enter/on_leave/dispose 都是应用回调。

先注册唯一非空路由；navigate 成功才发 page_changed；调用当前路由返回同一实例；退出前 dispose。

## 失败与边界

新页进入失败会清理并移除失败实例，再尝试恢复旧页；原始错误保留，恢复或清理错误追加说明。dispose 会尝试所有页，最后汇总首个失败。

不提供异步路由或回调重入调度。生命周期重入会抛 RuntimeError；不要在 on_enter/on_leave/dispose 里再次 navigate/dispose，可用 QTimer 安排当前回调完成后的导航。侧栏进入失败会发 navigation_failed(key,error)，直接 navigate 的错误由调用方捕获。hook 必须短且不阻塞。

## 线程与资源

工厂与所有 hook 在 Qt 线程；dispose 删除使用 deleteLater，应用需要继续处理延迟删除事件；退出时仍须关闭页面自己启动的后台任务。

## 示例与验证

- [最小调用与公开契约](../contracts/navigation.md)。每个模块的最小例子均由 `python examples/check_contract_examples.py` 执行；Qt 模块追加 `--qt`。
- [异常与恢复场景](../../examples/failure_scenarios.py)；[可交互桌面示例](../../examples/qt_showcase.py)。
- 验证入口：`tests/test_qt.py、tests/test_qt_contracts.py、tests/test_review_qt.py`。

页面资源所有权放在页面本身，不能只从 stack 移除控件就视为线程和串口已关闭。
