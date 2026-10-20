---
title: "数据表格使用指南"
category: "工程能力"
tags: ["desktop", "table", "type/usage-guide"]
summary: "数据表格的场景选择、接入步骤、错误处理、资源所有权与验证入口。"
created: 2026-10-20
updated: 2026-10-20
metadata_status: reviewed
home_area: theme
article_status: published
---

# 数据表格

## 适用场景

显示服务端分页结果并收集当前页选中记录。

## 接口与接入

Column 提供字段和展示函数；RecordTableModel 拥有记录浅拷贝；PagedTable 发 page_requested，不自行访问数据库。

应用接收 PageRequest，向仓储取 PageResult，再 set_page。Column 不接受用户 SQL；选中结果按当前行顺序返回。

## 失败与边界

空数据导航禁用；列必须非空且键唯一；转换无效记录失败时不会把模型留在 reset 状态；无效/越界/其他模型索引不会访问错误数据。

没有跨页全选、自动筛选或持久化排序。PageResult 不校正服务端总数或越界页码；仓储负责返回一致结果。展示函数必须纯且不能抛错。

## 线程与资源

Qt 线程更新；一次 set_page 会重置选择。大型结果应分页而不是将全部数据放入模型。

## 示例与验证

- [最小调用与公开契约](../contracts/table.md)。每个模块的最小例子均由 `python examples/check_contract_examples.py` 执行；Qt 模块追加 `--qt`。
- [异常与恢复场景](../../examples/failure_scenarios.py)；[可交互桌面示例](../../examples/qt_showcase.py)。
- 验证入口：`tests/test_qt.py、tests/test_qt_contracts.py、tests/test_review_qt.py`。

批量业务操作对传回主键重新授权，不把界面选择视为权限。
