---
title: "AC 可复用能力库"
category: "AI"
tags: ["area/software-development", "type/reusable-capabilities"]
summary: "收集从项目中提炼的可复用函数、组件和工程能力，以完整契约、测试和 Pull Request 交付。"
created: 2026-10-08
updated: 2026-10-08
metadata_status: reviewed
home_area: theme
article_status: published
---

# ac-reusable-capabilities

从项目开发中提炼可复用函数、组件和工程能力。每项能力都需要清晰契约、可搜索注释、独立测试与使用示例，通过 MR（GitHub Pull Request）提交。

当前为仓库初始化，尚未收录实现代码。初始化 MR 提供贡献规范和审阅模板，不代表已经验收任何复用能力。

提交前先检索已有能力，优先复用或改进。对于新增产物，说明复用场景、依赖与适用边界；提取后的代码重新验证，业务项目的测试通过不能替代提取版测试。

每个可复用公开接口保留 @ac-reusable 和稳定 @ac-capability 标识，并记录类型、语义标签、契约、依赖、示例与测试入口。标记是检索入口，实际行为仍以源码和测试为准。

完整要求见 [贡献规范](CONTRIBUTING.md)。Agent 执行规则见 [协作规则](AGENTS.md)。文档中的 MR 在 GitHub 中对应 Pull Request；未经维护者授权不自动合并或发布。

原创贡献按 [MIT License](LICENSE) 交付。第三方内容保留原许可、归属及必要声明，必须与引入和分发方式兼容。
