---
title: "AC 可复用能力库"
category: "AI"
tags: ["area/software-development", "type/reusable-capabilities"]
summary: "收集从项目中提炼的可复用函数、组件和工程能力，以完整契约、测试和 Pull Request 交付。"
created: 2026-10-08
updated: 2026-10-20
metadata_status: reviewed
home_area: theme
article_status: published
---

# ac-reusable-capabilities

从项目开发中提炼可复用函数、组件和工程能力。每项能力都需要清晰契约、可搜索注释、独立测试与使用示例，通过 MR（GitHub Pull Request）提交。

桌面基础能力包已收录到默认分支。包发布与接入项目验收分别进行，具体依据见包内验证记录。

[运行 Demo](demo/README.md) · [Wiki](wiki/Home.md) · [文档中心](docs/README.md)

```bash
# 在仓库根目录，使用 Python >= 3.11
python -m pip install ./packages/python/desktop
python demo/run.py --list
python demo/run.py desktop-core
```

交互展示、后台搜索和无显示器 smoke 的安装与命令见 [Demo 运行入口](demo/README.md)。

| 能力包 | 内容 | 入口 |
| --- | --- | --- |
| Desktop / Python | 表格、表单、查询、授权、CRUD、串口、打印、SQLite、服务、诊断及有界异步任务 | [独立包](packages/python/desktop/README.md) · [使用手册](packages/python/desktop/docs/README.md) · [能力目录](packages/python/desktop/docs/能力目录.md) |

提交前先检索已有能力，优先复用或改进。对于新增产物，说明复用场景、依赖与适用边界；提取后的代码重新验证，业务项目的测试通过不能替代提取版测试。

每个可复用公开接口保留 @ac-reusable 和稳定 @ac-capability 标识，并记录类型、语义标签、契约、依赖、示例与测试入口。标记是检索入口，实际行为仍以源码和测试为准。

按语言和能力领域组织目录，来源项目只作为溯源信息。跨项目迁入前先检索 [机器能力索引](catalog.json)，优先扩展同一实现。目录与后续收录遵循 [目录与收录规则](docs/目录与收录规则.md)。

完整要求见 [贡献规范](CONTRIBUTING.md)。Agent 执行规则见 [协作规则](AGENTS.md)。文档中的 MR 在 GitHub 中对应 Pull Request；未经维护者授权不自动合并或发布。

原创贡献按 [MIT License](LICENSE) 交付。第三方内容保留原许可、归属及必要声明，必须与引入和分发方式兼容。
