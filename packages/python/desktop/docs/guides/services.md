---
title: "服务生命周期使用指南"
category: "工程能力"
tags: ["desktop", "services", "type/usage-guide"]
summary: "服务生命周期的场景选择、接入步骤、错误处理、资源所有权与验证入口。"
created: 2026-10-20
updated: 2026-10-20
metadata_status: reviewed
home_area: theme
article_status: published
---

# 服务生命周期

## 适用场景

按依赖启动数据库、缓存、后台服务，并在失败后清理已启动资源。

## 接口与接入

ServiceSpec 声明名称、工厂和依赖；ServiceRegistry 按拓扑顺序启动，按反序关闭。

先注册所有规范，再 start；工厂通过 registry.get 获取先前依赖；应用 finally 中 stop。缺失依赖和循环在创建实例前失败。

## 失败与边界

重复名称或运行后注册被拒绝；启动/停止回调中的生命周期重入被拒绝。启动失败抛 ServiceStartError；关闭会尝试全部服务，再从首个失败构造 RuntimeError。

工厂在返回实例前创建资源后抛错时，工厂必须自行清理；注册表只拥有已返回实例。它不提供跨线程同步或健康检查。

## 线程与资源

start/stop 在同一拥有者线程调度；服务自己的 stop 必须等待工作线程和 socket 结束。关闭失败会释放注册表引用，但服务需报告未释放外部资源。

## 示例与验证

- [最小调用与公开契约](../contracts/services.md)。每个模块的最小例子均由 `python examples/check_contract_examples.py` 执行；Qt 模块追加 `--qt`。
- [异常与恢复场景](../../examples/failure_scenarios.py)；[可交互桌面示例](../../examples/qt_showcase.py)。
- 验证入口：`tests/test_core.py、tests/test_contracts.py、tests/test_review_core.py`。

把应用退出路径集中到 try/finally，不在每个页面里单独停止全局服务。
