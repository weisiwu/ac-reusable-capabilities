---
title: "目录配置与单实例使用指南"
category: "工程能力"
tags: ["desktop", "runtime", "type/usage-guide"]
summary: "目录配置与单实例的场景选择、接入步骤、错误处理、资源所有权与验证入口。"
created: 2026-10-20
updated: 2026-10-20
metadata_status: reviewed
home_area: theme
article_status: published
---

# 目录配置与单实例

## 适用场景

桌面应用读取用户配置、确定数据目录、防止重复启动。

## 接口与接入

AppPaths 计算平台目录，ensure 才创建；load_json_config 读取对象后调用应用校验；SingleInstance 使用 Qt 本地 server 名。

用稳定、安全 app_id；配置校验器对非法内容抛异常；同一进程长期保留 SingleInstance 对象直到退出。

## 失败与边界

JSON 根必须是对象，文件或校验错误上抛。单实例获取成功返回 true，存在可连接对端返回 false；监听失败抛 RuntimeError。

单实例是本地入口守卫，不是授权或分布式锁；不能用它替代数据库写入协调。应用 ID 的变更可能改变数据目录和 socket 身份。

## 线程与资源

无 Qt 模块可单独安装。单实例需要 Qt 环境，退出时 finally release；不终止其他进程。

## 示例与验证

- [最小调用与公开契约](../contracts/runtime.md)。每个模块的最小例子均由 `python examples/check_contract_examples.py` 执行；Qt 模块追加 `--qt`。
- [异常与恢复场景](../../examples/failure_scenarios.py)；[可交互桌面示例](../../examples/qt_showcase.py)。
- 验证入口：`tests/test_core.py、tests/test_contracts.py、tests/test_qt.py`。

配置更新持久化和密钥保管由应用实现，框架不会自动创建新库覆盖旧数据。
