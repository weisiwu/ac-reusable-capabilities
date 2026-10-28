---
title: "文档中心"
category: "工程能力"
tags: ["type/handbook", "能力复用"]
summary: "版本、依赖、兼容性、使用指南与接口契约的统一阅读入口。"
created: 2026-10-20
updated: 2026-10-28
metadata_status: reviewed
home_area: theme
article_status: published
---

# 文档中心

[功能展示](https://weisiwu.github.io/ac-reusable-capabilities/) 用于体验效果；[Wiki](../wiki/Home.md) 帮助选择接入路径。本中心提供深入使用和维护所需的规范文档，精确属性和调用行为以各包指南、契约及源码测试为准。

## 使用能力

| 你的目标 | 文档入口 | 内容 |
| --- | --- | --- |
| 安装并完成第一次调用 | [快速开始](../packages/python/desktop/docs/快速开始.md) | 依赖选择、环境步骤、调用示例和预期结果 |
| 确认运行要求 | [版本与依赖](../packages/python/desktop/docs/架构与依赖.md) | 包名、版本、Python、extras、模块关系和资源条件 |
| 升级或评估目标平台 | [升级与兼容](../packages/python/desktop/docs/升级与兼容.md) | 声明与验证矩阵、行为变化、数据升级和回退 |
| 查看能力使用流程 | [模块指南](../packages/python/desktop/docs/README.md) · [接入场景](../wiki/Recipes.md) | 场景步骤、流程图、属性与事件、资源释放 |
| 查询接口细节 | [能力目录](../packages/python/desktop/docs/能力目录.md) | 各模块公开契约：输入输出、默认值、异常与代码 |
| 处理运行失败 | [排障](../packages/python/desktop/docs/常见问题与排障.md) | 依赖、线程、数据、设备和错误恢复 |
| 核对已有验证 | [验证记录](../packages/python/desktop/docs/验证记录.md) | 实际环境、命令、提交范围与未验证项 |

当前已收录 `python.desktop`，包含 15 类能力、16 个实现模块；`table` 与 `query` 存在组合关系，分组数与模块数不同。当前包声明版本为 `0.2.0`，以 [包配置](../packages/python/desktop/pyproject.toml) 为准，不能将包版本、源码提交和应用数据库版本混作一个版本。

## 维护与贡献

| 工作 | 文档入口 |
| --- | --- |
| 了解文档权威来源 | [架构与文档职责](架构与文档职责.md) |
| 增加语言、领域和体验方式 | [多类型能力与站点接入](多类型能力与站点接入.md) |
| 迁入或扩展能力 | [收录流程](能力收录流程.md) · [目录规则](目录与收录规则.md) · [贡献规范](../CONTRIBUTING.md) |
| 维护 Demo 与文档 | [本地 Demo 说明](../demo/README.md) · [验证与维护](验证与维护.md) |
| 构建和发布静态站点 | [站点维护](../site/README.md) |

## 职责分层

| 层 | 回答的问题 | 内容边界 |
| --- | --- | --- |
| 展示与 Demo | 能做什么，效果怎样 | 功能与操作体验，简短文档入口 |
| Wiki | 我该如何选择与组合 | 场景路径、接入顺序与跨能力组合 |
| 跨包 Docs | 如何收录、组织和维护 | 版本化流程、目录约定、站点规范 |
| 包内 Docs | 具体怎样调用和兼容 | 安装、流程、属性、事件、代码、异常、版本与测试 |

合并、包发布、业务接入与目标设备验收分别记录。文档导航不会替目标项目完成验证，也不推定某个包已上传到包索引。
