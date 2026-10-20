---
title: "GitHub Pages Demo 站点"
category: "工程能力"
tags: ["type/handbook", "demo", "github-pages"]
summary: "静态能力实验室的构建、交互边界、验证与发布维护。"
created: 2026-10-20
updated: 2026-10-20
metadata_status: reviewed
home_area: theme
article_status: published
---

# GitHub Pages Demo 站点

站点入口：<https://weisiwu.github.io/ac-reusable-capabilities/>。内容由本目录静态页面与仓库真实能力清单构建；是否完成某次发布，以 GitHub Actions 的部署状态及线上版本为准。

## 能体验什么

- 表格：按名称和分类筛选，分页、查看样例。
- 表单：必填校验、创建样例、回到表格查看，刷新即清空。
- 异步搜索：模拟防抖、最新请求交付、取消；输入「超时」体验超时提示。
- 脱敏：嵌套 JSON 和数组按敏感键名处理，保留非敏感值；不识别自由文本中的隐私。
- 能力索引与运行清单：自动收录根能力索引和 demo 清单，提供指南、契约、源码、安装与本地运行命令。

浏览器交互是 JavaScript 行为示意，不执行 Python / Qt，也不访问设备、业务数据库或远端业务服务。Python 的实际契约、线程模型、迁移和失败恢复以包内实现与测试为准。页面输入仅存在当前页面内存；没有表单上传、持久化或统计服务。

## 本地构建与预览

在仓库根目录使用 Python >= 3.11；构建只需标准库，不需要安装 Qt 或 Node 依赖。

```bash
python site/build.py
python -m http.server 8000 --bind 127.0.0.1 --directory dist/pages
```

打开 `http://127.0.0.1:8000/`，结束后停止预览服务。不要直接打开 HTML 文件：站点使用浏览器模块加载。所有静态资源使用相对路径，兼容 GitHub 项目站点的仓库路径前缀。

`--output` 可指定构建目录，默认 `dist/pages`；`--repository owner/name` 支持同结构 fork。`--ref` 指定源码链接版本，CI 使用 `GITHUB_SHA`，使指南与源码指向同一发布提交。本地默认 `main`。不从目录扫描复制资料，仅输出显式静态资源与从两个公开清单派生的数据。

## 发布

[Pages 工作流](../.github/workflows/pages.yml) 在 PR 上执行构建与测试，在 `main` 推送后构建并发布；也支持从 `main` 手动触发。仓库 Pages 的 Build and deployment 使用 GitHub Actions。部署权限仅授予 deploy job，PR 不发布站点。

发布使用 `configure-pages`、`upload-pages-artifact` 与 `deploy-pages`，配置依据 [GitHub 官方文档](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)。开启服务不等于发布成功，需核对 deploy job、站点可访问性和页脚提交号。回滚时对默认分支执行经审阅的还原提交并重新部署，不手改站点成功状态。

## 维护与验证

```bash
python scripts/check_catalog.py
python scripts/check_docs.py
python demo/run.py --check
python -m unittest discover -s tests -v
node --test site/tests/*.test.mjs
node --check site/assets/app.mjs
python site/build.py
```

Node >= 22 仅用于内置测试工具与语法检查，没有 npm 安装步骤。`catalog.json` 与 `demo/catalog.json` 是真实内容来源；新增 Python 包会自动进入索引。源码文件、运行时与命令由清单显式声明，构建器不再按 Python 布局推导。多类型接入见 [元数据与站点设计](../docs/多类型能力与站点接入.md)。新语言仍需补原生代码验证适配与 CI。浏览器交互是显式选择的场景，不因新增清单项自动生成交互实现。

本次本地验证：根工具 9 条、浏览器模型 5 条测试通过；在 Codex 内置浏览器验证筛选、分页、表单创建、搜索成功/取消/超时、无效 JSON 与脱敏、能力搜索和文档链接，控制台无错误。桌面 1440×1000、手机 390×844 走查；手机修正表格列宽后无页面横向溢出。视觉核对包括侧栏、标题、双色面板、表格排版、字体与间距；样例文字和分类以真实清单及模拟数据为准，替换了概念图中不存在的能力。没有据此宣称真实设备或 Python/Qt 目标系统验收。

## 多项目调整

默认首页改为能力目录，按语言、领域、类型、来源、体验方式组合筛选并分页；详情展示用途、包版本/许可、全部源码、来源及示例。实验室仅展示 site/demos.json 登记的实际场景，不作为其他类型能力的必经入口。本地示例按能力包筛选，不为所有内容拼接 Python/Qt 命令。

本轮多类型验证：根工具 11 条、浏览器模型 6 条通过；临时跨语言条目保留 TypeScript/Shell 源码、Node 命令和纯文档接入，不进入发布内容。内置浏览器验证类型+关键词组合筛选、4 项浏览器能力筛选、详情/来源/源码、目录分页、空结果与本地示例跳转；390px 手机无页面横向溢出。新增语言的原生代码检查仍需对应适配器，没有据此声明所有语言的代码都已验收。
