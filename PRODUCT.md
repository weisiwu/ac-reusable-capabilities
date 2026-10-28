---
title: AC 能力库产品约定
---
# Product

<!-- impeccable:product-schema 1 -->

## Platform
web

## Users
开发者通过在线功能体验评估可复用能力，再通过文档了解接入和使用方法。

## Product Purpose
集中呈现已沉淀的能力，并提供可操作的样例和深入的使用说明。

## Operating Context
GitHub Pages 静态站点；Python 构建文档，浏览器原生模块提供交互演示。

## Capabilities and Constraints
当前目录包含 15 项 Python desktop 能力及对应的浏览器模拟演示。目录同时支持其他语言、领域及只有文档的能力。保留全部样例操作、默认模拟数据、取消和超时处理、旧 Wiki 重定向、文档及其链接。演示使用虚构数据，设备与系统行为为模拟。

## Brand Commitments
站点名为 AC Lab / AC 能力库。用户要求功能展示与文档采用统一的文档风格，展示只负责功能体验，深入用法放在统一文档中心。2026-10-28 用户确认首页采用紧凑的分组索引列表，选择后进入独立演示页。

## Evidence on Hand
catalog.json、demo/catalog.json、site/demos.json 是能力及场景事实来源。site/assets/scenes-ui.mjs 与 scenes-system.mjs 提供已存在的操作。docs/ 和 packages/ 内 Markdown 是使用文档来源。

## Product Principles
- 先找到能力，再进入单项体验。
- 打开演示即有样例和结果。
- 功能展示与详细用法各有清楚的位置。
- 版本、依赖、兼容要求由文档准确说明。
