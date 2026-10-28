---
title: "资料管理协调使用指南"
category: "工程能力"
tags: ["desktop", "crud", "type/usage-guide"]
summary: "资料管理协调的场景选择、接入步骤、错误处理、资源所有权与验证入口。"
created: 2026-10-20
updated: 2026-10-28
metadata_status: reviewed
home_area: theme
article_status: published
---

# 资料管理协调


## 接入速查

| 接入项 | 要求 / 用法 |
| --- | --- |
| 环境与依赖 | 标准库；应用注入仓储与授权 |
| 核心入口 | `CrudController(repository, authorize=...)` |
| 调用顺序 | 授权 → 校验 → 仓储写入 → changed 通知 |
| 关键边界 | 仓储异常上抛；写后通知失败不会回滚写入 |
| 方法 / 属性 | `list_page`, `detail`, `create`, `update`, `delete` |
| 版本与兼容 | [依赖说明](../架构与依赖.md) · [升级说明](../升级与兼容.md) |

## 接入流程

```mermaid
flowchart LR
    N0["授权"]
    N1["校验"]
    N0 --> N1
    N2["仓储写入"]
    N1 --> N2
    N3["changed 通知"]
    N2 --> N3
```


## 适用场景

多个列表和编辑页面共享仓储操作、校验和权限检查。

## 接口与接入

CrudRepository 定义 list/get/create/update/delete；CrudController 负责授权、校验、写入与变更通知顺序。

仓储自定义事务与主键；构造时必须显式传 authorize；create/update 可插入 validate；changed 用于通知缓存或视图。

## 失败与边界

拒绝授权和校验失败发生在仓储写入前。仓储错误原样上抛。changed 在写后运行；其异常不能撤销已成功的写入，调用方不能据此盲目重试 create。

控制器不是事务管理器。远程写入、通知投递或重复请求需要应用自己的幂等键与事务设计。

## 线程与资源

同步调用，不创建线程；不要在 GUI 线程执行慢仓储。通知函数应短、可重入且不抛错，资源归仓储所有。

## 示例与验证

- [最小调用与公开契约](../contracts/crud.md)。每个模块的最小例子均由 `python examples/check_contract_examples.py` 执行；Qt 模块追加 `--qt`。
- [异常与恢复场景](../../examples/failure_scenarios.py)；[可交互桌面示例](../../examples/qt_showcase.py)。
- 验证入口：`tests/test_core.py、tests/test_contracts.py`。

为读、写、删除分别定义授权行为；接口层与页面使用相同控制器。
