---
title: "能力库 Wiki"
category: "工程能力"
tags: ["type/handbook", "能力复用"]
summary: "按使用路径选择能力，进入版本、接入流程和权威接口文档。"
created: 2026-10-20
updated: 2026-10-28
metadata_status: reviewed
home_area: theme
article_status: published
---

# 能力库 Wiki

Wiki 说明如何选择和组合能力，Docs 提供安装条件、流程、属性、接口契约、调用示例与验证依据。[功能展示](https://weisiwu.github.io/ac-reusable-capabilities/) 只负责体验功能和效果。

## 从你的目标开始

| 目标 | 阅读入口 | 完成后得到 |
| --- | --- | --- |
| 选一项适合项目的能力 | [能力地图](Capabilities.md) | 对应的使用指南、契约和 Demo |
| 跑通第一次调用 | [上手步骤](Getting-Started.md) | 隔离环境安装与最小调用路径 |
| 核对版本、依赖和平台条件 | [版本与兼容选择](Compatibility.md) | 声明要求、验证范围与待补检查 |
| 将多个能力接入应用 | [接入场景](Recipes.md) | 数据、回调和资源所有权的组合流程 |
| 查参数、属性、事件与异常 | [Desktop 手册](../packages/python/desktop/docs/README.md) | 包内精确指南和公开契约 |
| 处理失败或贡献新能力 | [常见问题](Troubleshooting.md) · [贡献入口](Contributing.md) | 排障依据或收录步骤 |

## 文档与代码对应

本站 Wiki 与包内文档从仓库 Markdown 构建，链接指向同一次站点构建的内容。源码入口保留提交信息，接入时核对自己的安装来源与该提交。Wiki 源文件在仓库 `wiki/` 维护；独立 GitHub Wiki 远端不是这里的权威入口。

当前文档覆盖 `python.desktop`。新增语言或领域沿用 [多类型接入规范](../docs/多类型能力与站点接入.md)，声明自己的安装、版本和验证条件，不继承 Python / Qt 的结论。

[文档中心](../docs/README.md) · [Desktop 手册](../packages/python/desktop/docs/README.md) · [本地 Demo 说明](../demo/README.md) · [仓库首页](../README.md)
