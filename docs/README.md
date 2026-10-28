---
title: "文档中心"
category: "工程能力"
tags: ["type/handbook", "能力复用"]
summary: "能力选择、使用指南、接口参考、版本兼容、组合排障和贡献维护的统一入口。"
created: 2026-10-20
updated: 2026-10-28
metadata_status: reviewed
home_area: theme
article_status: published
---

# 文档中心

[功能展示与 Demo](https://weisiwu.github.io/ac-reusable-capabilities/) 用于体验功能和效果。本中心统一提供能力选择、接入和深入使用文档；安装、属性、调用行为与异常以各包指南、契约及源码测试为准。

## 快速开始

第一次使用从 [快速开始](快速开始.md) 选择阅读与接入路径，再按 [桌面包快速开始](../packages/python/desktop/docs/快速开始.md) 完成隔离环境安装和最小调用。安装步骤、属性表与代码只在包内维护，避免多份说明漂移。

## 能力指南

| 目标 | 入口 |
| --- | --- |
| 按功能选择能力 | [能力地图](能力地图.md) |
| 查看模块接入流程 | [Desktop 使用手册](../packages/python/desktop/docs/README.md) |
| 理解应用与框架边界 | [架构与文档职责](架构与文档职责.md) · [包架构与依赖](../packages/python/desktop/docs/架构与依赖.md) |
| 查找本地演示 | [Demo 清单与运行说明](../demo/README.md) |

当前已收录 `python.desktop`，包含 15 类能力、16 个实现模块；`table` 与 `query` 存在组合关系，分组数与模块数不同。新增语言或领域声明自己的工具链与运行条件，不继承 Python / Qt 的验证结论。

## 接口参考

[能力目录与公开契约](../packages/python/desktop/docs/能力目录.md) 提供按模块查找的入口，[模块导航](../packages/python/desktop/docs/README.md#模块指南) 同时链接指南和契约。契约列明属性、类型、默认值、方法、信号、异常与最小调用；跨模块组合见下方场景文档。

## 版本兼容

| 需要确认的内容 | 入口 |
| --- | --- |
| 包版本、源码提交和应用数据版本的区别 | [版本与兼容](版本与兼容.md) |
| Python、Qt、串口与安装项的要求 | [架构与依赖](../packages/python/desktop/docs/架构与依赖.md) |
| 升级行为、兼容矩阵、数据恢复和降级条件 | [升级与兼容](../packages/python/desktop/docs/升级与兼容.md) |
| 真实环境、测试命令、范围及未验证项 | [验证记录](../packages/python/desktop/docs/验证记录.md) |

当前包声明版本为 `0.2.0`，以 [包配置](../packages/python/desktop/pyproject.toml) 为准。依赖声明、工作流配置和某次实际测试分别表达不同证据范围，不能将可安装或可演示写成目标平台已经验收。

## 组合排障

- [组合场景](组合场景.md)：异步搜索、资料编辑、备份恢复、服务启动、打印与通信的组合流程。
- [排障指南](排障指南.md)：按接入和 Demo 的失败现象定位。
- [包内排障](../packages/python/desktop/docs/常见问题与排障.md)、[生命周期与线程](../packages/python/desktop/docs/生命周期与线程.md)、[安全与数据边界](../packages/python/desktop/docs/安全与数据边界.md)：进一步核对异常、资源与数据责任。

## 贡献维护

| 工作 | 入口 |
| --- | --- |
| 迁入或扩展能力 | [能力收录流程](能力收录流程.md) · [目录规则](目录与收录规则.md) · [贡献规范](../CONTRIBUTING.md) |
| 增加语言、领域和体验方式 | [多类型能力与站点接入](多类型能力与站点接入.md) |
| 检查 Demo、文档和测试 | [验证与维护](验证与维护.md) · [本地 Demo 说明](../demo/README.md) |
| 构建和发布静态站点 | [站点维护](../site/README.md) |

文档网页从同一提交的 Markdown 构建，Markdown 是唯一正文来源。包内指南和契约保留精确接口正文，本中心只组织阅读路径。旧 Wiki 地址保留迁移入口；新增内容进入本中心及对应包文档。

合并、包发布、业务接入与目标设备验收分别记录，文档导航不推定包已上传到包索引。
