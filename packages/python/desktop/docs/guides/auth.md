---
title: "密码与访问控制使用指南"
category: "工程能力"
tags: ["desktop", "auth", "type/usage-guide"]
summary: "密码与访问控制的场景选择、接入步骤、错误处理、资源所有权与验证入口。"
created: 2026-10-20
updated: 2026-10-20
metadata_status: reviewed
home_area: theme
article_status: published
---

# 密码与访问控制

## 适用场景

本地软件已有账号存储，但需要统一密码校验和显式权限决策。

## 接口与接入

CredentialStore 由应用实现；AuthService 校验并返回 Principal；AccessPolicy 只执行应用传入的判定函数。

用 PasswordHasher 创建存储值；lookup 返回 id、password_hash、roles；服务写入入口必须调用 require，不能只隐藏界面按钮。

## 失败与边界

默认 310000 轮，最低 100000 轮；verify 默认上限 2000000，可通过 max_verify_iterations 显式放宽。畸形载荷、盐或摘要长度不符在计算前拒绝；needs_rehash 会识别损坏哈希。

没有注册、登录会话、锁定、限流或机器绑定。PBKDF2 格式不是数据加密。存量高于上限的合法哈希需先调整策略，再做有计划迁移。

## 线程与资源

不会读写账号文件或持有长期资源；CredentialStore 的连接、错误和并发由应用管理。

## 示例与验证

- [最小调用与公开契约](../contracts/auth.md)。每个模块的最小例子均由 `python examples/check_contract_examples.py` 执行；Qt 模块追加 `--qt`。
- [异常与恢复场景](../../examples/failure_scenarios.py)；[可交互桌面示例](../../examples/qt_showcase.py)。
- 验证入口：`tests/test_core.py、tests/test_contracts.py、tests/test_review_core.py`。

示例账户只存在于临时测试中；不要把真实账号和口令提交仓库。
