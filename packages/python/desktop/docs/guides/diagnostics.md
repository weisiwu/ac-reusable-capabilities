---
title: "诊断日志与审计使用指南"
category: "工程能力"
tags: ["desktop", "diagnostics", "type/usage-guide"]
summary: "诊断日志与审计的场景选择、接入步骤、错误处理、资源所有权与验证入口。"
created: 2026-10-20
updated: 2026-10-20
metadata_status: reviewed
home_area: theme
article_status: published
---

# 诊断日志与审计

## 适用场景

为应用记录可查询 JSON 日志和追加式审计事件。

## 接口与接入

redact 按结构化键递归脱敏；JsonFormatter 格式化 record.data；AuditJournal 追加并 fsync；configure_json_logger 管理文件 handler。

应用为自身敏感字段注入 is_sensitive；日志 message 只放无敏感信息的固定文案，动态数据放 data。重配同 name/path 会更新脱敏策略。

## 失败与边界

无效 actor/action 被拒绝；IO 错误上抛。handler 查重和创建串行化；审计同实例用锁，多个实例/进程的写入不作保证。

不清洗任意自由文本，不支持循环对象或防篡改审计；默认按 5 MiB 轮转并保留 3 份历史文件；可显式配置，max_bytes=0 表示关闭轮转。单条超长记录可能超过单文件阈值，降低历史保留数不会删除此前更多份数的历史文件。

## 线程与资源

应用退出时关闭并移除自己创建的 logger handlers。AuditJournal 每次追加使用短期文件句柄，写完关闭。

## 示例与验证

- [最小调用与公开契约](../contracts/diagnostics.md)。每个模块的最小例子均由 `python examples/check_contract_examples.py` 执行；Qt 模块追加 `--qt`。
- [异常与恢复场景](../../examples/failure_scenarios.py)；[可交互桌面示例](../../examples/qt_showcase.py)。
- 验证入口：`tests/test_core.py、tests/test_contracts.py、tests/test_review_core.py`。

只用无敏感含义的 actor/resource 标识；异常对象和堆栈也可能含业务值。
