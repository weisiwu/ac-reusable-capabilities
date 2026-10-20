---
title: "桌面能力文档导航"
category: "工程能力"
tags: ["desktop", "type/handbook"]
summary: "从场景指南到接口契约、失败示例和验证记录。"
created: 2026-10-20
updated: 2026-10-20
metadata_status: reviewed
home_area: theme
article_status: published
---

# 桌面能力文档导航

## 阅读顺序

1. [快速开始](快速开始.md) 确定安装项并执行例子。
2. [架构与依赖](架构与依赖.md) 确认应用和框架的职责。
3. 按下面模块指南接入，再查精确公开契约。
4. 处理 [生命周期与线程](生命周期与线程.md)、[安全与数据边界](安全与数据边界.md)。
5. 升级前读 [兼容说明](升级与兼容.md)，定位失败时读 [排障](常见问题与排障.md)。

## 模块指南

| 模块 | 场景与接入 | 输入输出及异常 |
| --- | --- | --- |
| background | [使用指南](guides/background.md) | [公开契约](contracts/background.md) |
| auth | [使用指南](guides/auth.md) | [公开契约](contracts/auth.md) |
| crud | [使用指南](guides/crud.md) | [公开契约](contracts/crud.md) |
| crud_page | [使用指南](guides/crud_page.md) | [公开契约](contracts/crud_page.md) |
| diagnostics | [使用指南](guides/diagnostics.md) | [公开契约](contracts/diagnostics.md) |
| feedback | [使用指南](guides/feedback.md) | [公开契约](contracts/feedback.md) |
| filters | [使用指南](guides/filters.md) | [公开契约](contracts/filters.md) |
| forms | [使用指南](guides/forms.md) | [公开契约](contracts/forms.md) |
| navigation | [使用指南](guides/navigation.md) | [公开契约](contracts/navigation.md) |
| printing | [使用指南](guides/printing.md) | [公开契约](contracts/printing.md) |
| query | [使用指南](guides/query.md) | [公开契约](contracts/query.md) |
| runtime | [使用指南](guides/runtime.md) | [公开契约](contracts/runtime.md) |
| services | [使用指南](guides/services.md) | [公开契约](contracts/services.md) |
| storage | [使用指南](guides/storage.md) | [公开契约](contracts/storage.md) |
| table | [使用指南](guides/table.md) | [公开契约](contracts/table.md) |

## 例子与验证

| 示例 | 运行方式 | 覆盖 |
| --- | --- | --- |
| 组合入门 | `python examples/desktop_demo.py [--qt]` | CRUD、快照、服务、打印和可选 Qt |
| 文档例子 | `python examples/check_contract_examples.py [--qt]` | 9 个核心／16 个全部模块 |
| 异常恢复 | `python examples/failure_scenarios.py` | 授权拒绝、迁移失败、恢复、串口短写、打印取消等 9 个场景 |
| 后台搜索 | `python examples/background_search.py [--smoke]` | 请求代次、异步交付与安全退出 |
| 桌面展示 | `python examples/qt_showcase.py [--smoke]` | 六个可交互页面；smoke 自动走查并退出 |

[评审与修复记录](评审与修复记录.md) · [验证记录](验证记录.md) · [来源与迁入边界](来源与迁入边界.md) · [能力目录](能力目录.md)
