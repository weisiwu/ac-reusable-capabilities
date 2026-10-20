---
title: "管理页面组合使用指南"
category: "工程能力"
tags: ["desktop", "crud_page", "type/usage-guide"]
summary: "管理页面组合的场景选择、接入步骤、错误处理、资源所有权与验证入口。"
created: 2026-10-20
updated: 2026-10-20
metadata_status: reviewed
home_area: theme
article_status: published
---

# 管理页面组合

## 适用场景

已经实现仓储、授权和字段配置，希望快速组合标准管理页面。

## 接口与接入

CrudPage 组合 FilterPanel、PagedTable、FormDialog、DetailView 和已授权 CrudController。

提供 identity_key；每行必须包含该标识，包括 0 等合法值。监听 changed(action,id) 和 operation_failed(action,error)。先 load_page，再由分页与筛选触发刷新。

## 失败与边界

缺少身份会发失败信号而不让 KeyError 逃出 Qt 槽；取消不写入；控制器错误走 operation_failed；完成/取消的弹窗统一 deleteLater，不随重复操作累积。

当前为同步仓储；慢查询必须另行调度，不能在事件线程直接连接慢远端。页面无独立权限规则，控制器是强制入口。

## 线程与资源

页面及仓储回调在 Qt 线程；页面关闭前释放仓储。写后刷新失败只说明刷新失败，不代表之前写入没有发生。

## 示例与验证

- [最小调用与公开契约](../contracts/crud_page.md)。每个模块的最小例子均由 `python examples/check_contract_examples.py` 执行；Qt 模块追加 `--qt`。
- [异常与恢复场景](../../examples/failure_scenarios.py)；[可交互桌面示例](../../examples/qt_showcase.py)。
- 验证入口：`tests/test_qt.py、tests/test_qt_contracts.py、tests/test_review_qt.py`。

单独使用基础组件时仍可保留同一控制器，不需要为了页面组合修改业务 schema。
