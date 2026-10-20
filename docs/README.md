---
title: "文档中心"
category: "工程能力"
tags: ["type/handbook", "能力复用"]
summary: "按使用者和贡献者的阅读任务连接 Wiki、demo 和权威契约。"
created: 2026-10-20
updated: 2026-10-20
metadata_status: reviewed
home_area: theme
article_status: published
---

# 文档中心

[在线 Demo](https://weisiwu.github.io/ac-reusable-capabilities/) · [站点构建与发布](../site/README.md)

先运行 [Demo](../demo/README.md) 看行为，再从 [Wiki](../wiki/Home.md) 按场景选择能力。Wiki 负责导航和组合说明，精确接口、异常和生命周期以各包契约及源码测试为准。

| 你的目标 | 阅读入口 |
| --- | --- |
| 安装并跑通第一个例子 | [上手步骤](../wiki/Getting-Started.md) · [Demo 清单](../demo/README.md) |
| 选适合当前项目的能力 | [能力地图](../wiki/Capabilities.md) · [机器索引](../catalog.json) |
| 组合异步、存储、服务和日志 | [接入场景](../wiki/Recipes.md) · [架构与文档职责](架构与文档职责.md) |
| 查询输入输出、错误和依赖 | [Desktop 文档](../packages/python/desktop/docs/README.md) |
| 处理安装和运行失败 | [排障](../wiki/Troubleshooting.md) |
| 规划多语言与多类型接入 | [能力与站点设计](多类型能力与站点接入.md) |
| 从其他项目迁入能力 | [收录流程](能力收录流程.md) · [目录规则](目录与收录规则.md) · [贡献规范](../CONTRIBUTING.md) |
| 执行并核对验证 | [验证与维护](验证与维护.md) · [已有验证记录](../packages/python/desktop/docs/验证记录.md) |

## 当前内容

当前已收录 `python.desktop`，包含 15 类能力、16 个实现模块。`table` 与 `query` 有组合关系，因此能力分组数与模块数不相同。后续独立包增加到根目录 `catalog.json`；本文只提供导航，不维护另一套 API 清单。

## 文档分工

- `README.md`：仓库介绍和三个常用入口。
- `demo/`：运行和检查示例的统一入口。
- `wiki/`：按场景阅读的版本化 Wiki，随代码一起审阅。
- `docs/`：跨包架构、目录、收录与维护规则。
- `packages/<language>/<domain>/docs/`：权威指南、接口契约、来源和验证依据。

合并表示代码进入默认分支；包发布、业务接入与目标设备验收分别记录。本文不推定已经向包索引发布。
