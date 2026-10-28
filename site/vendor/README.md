---
title: "文档图表运行依赖"
category: "工程能力"
tags: ["type/dependency", "mermaid"]
summary: "自托管 Mermaid 的版本、来源、许可和校验记录。"
created: 2026-10-28
updated: 2026-10-28
metadata_status: reviewed
---

# 文档图表运行依赖

Wiki 与 Docs 使用 Mermaid **11.12.1** 将 Markdown 中的流程图渲染为 SVG。运行文件随站点发布，读者无需访问 CDN。Markdown 原文是唯一正文来源；渲染失败时保留可读图表文本。

| 文件 | 来源 | SHA-256 |
| --- | --- | --- |
| `mermaid.min.js` | npm `mermaid@11.12.1`，`dist/mermaid.min.js` | `198b19442f86f0b46a17e56d3abf744c3a28a3427e66fa8dada3b589a77babcc` |
| `mermaid-LICENSE.txt` | 同包 `LICENSE`，MIT | `ec9fb67dcb25eccc416ed56e1aab819222c805a2a4bfe4cb19e7556bf2ffde80` |

上游：[Mermaid](https://github.com/mermaid-js/mermaid/tree/v11.12.1)。以上是站点图表依赖，不属于 Python 桌面能力的运行依赖。升级时同时核验许可、文件摘要和实际图表渲染。
