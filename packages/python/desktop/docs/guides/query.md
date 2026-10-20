---
title: "分页与查询使用指南"
category: "工程能力"
tags: ["desktop", "query", "type/usage-guide"]
summary: "分页与查询的场景选择、接入步骤、错误处理、资源所有权与验证入口。"
created: 2026-10-20
updated: 2026-10-20
metadata_status: reviewed
home_area: theme
article_status: published
---

# 分页与查询

## 适用场景

数据库列表接口、服务端分页、按白名单字段筛选。

## 接口与接入

PageRequest 描述页码和每页数量；PageResult 描述当前页与总数；SqlWhere 只生成 SQLite 风格的问号绑定谓词。

由应用维护 columns 白名单；用户值进入 equal/contains/range；将 build 返回的 SQL 与参数分开交给仓储。count 和行查询必须使用相同条件。

## 失败与边界

页码、页大小必须是正整数，空数据仍显示一页。range 结束值不包含在区间内；日期仅传字符串时调用方将含当天的结束日换算成下一天。contains 把百分号、下划线和反斜线作为字面量。

不能把用户输入当列表达式。工具不执行 SQL、不验证整条查询，也不提供跨数据库 placeholder 适配。

## 线程与资源

无连接或线程所有权；builder 具有可变累积状态，不跨请求共享。PageResult 和记录仅按约定浅层使用，不是深度不可变业务快照。

## 示例与验证

- [最小调用与公开契约](../contracts/query.md)。每个模块的最小例子均由 `python examples/check_contract_examples.py` 执行；Qt 模块追加 `--qt`。
- [异常与恢复场景](../../examples/failure_scenarios.py)；[可交互桌面示例](../../examples/qt_showcase.py)。
- 验证入口：`tests/test_core.py、tests/test_contracts.py`。

先验证筛选值，再调用仓储并返回 PageResult；UI 只读取分页结果。
