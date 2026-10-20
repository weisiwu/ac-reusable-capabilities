---
title: "Demo 运行入口"
category: "工程能力"
tags: ["type/handbook", "能力复用"]
summary: "按能力领域发现和运行示例，区分交互演示、自动验证与依赖。"
created: 2026-10-20
updated: 2026-10-20
metadata_status: reviewed
home_area: theme
article_status: published
---

# Demo 运行入口

所有命令在仓库根目录执行，Python >= 3.11。执行入口复用包内的示例源码，不另建演示版实现。`--list` 和 `--check` 只需标准库；运行示例前安装对应包。

## 安装与第一次运行

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell 使用 .venv\Scripts\Activate.ps1
python -m pip install './packages/python/desktop'
python demo/run.py --list
python demo/run.py desktop-core
python demo/run.py desktop-failures
```

首次运行 core 应输出 `Desktop example passed`，验证注入式 CRUD、临时 SQLite 快照、模拟打印与服务管理。failures 应输出 9 个场景通过。失败返回非零状态；缺依赖会给出安装命令。

## 可运行清单

| ID | 场景 / 观察点 | 依赖 | 运行与预期 |
| --- | --- | --- | --- |
| desktop-core | CRUD、SQLite、服务、模拟打印的组合 | 基础包 | `python demo/run.py desktop-core`，自动退出 |
| desktop-ui | 分页表格、编辑表单、筛选、反馈、CRUD、后台搜索六页 | qt | `python demo/run.py desktop-ui`，显示窗口，关闭后退出 |
| desktop-search | 输入文字、取最新查询结果、取消任务 | qt | `python demo/run.py desktop-search`，显示搜索窗口 |
| desktop-failures | 授权拒绝、失败回滚、短写、取消、脱敏等 | 基础包，串口注入假句柄 | `python demo/run.py desktop-failures`，9 个场景通过 |
| desktop-contracts | 核心模块最小调用 | 基础包 | `python demo/run.py desktop-contracts`，9 个模块通过 |
| desktop-contracts-qt | 核心与 Qt 模块最小调用 | qt | `python demo/run.py desktop-contracts-qt`，16 个模块通过 |

交互示例先安装：

```bash
python -m pip install './packages/python/desktop[qt]'
python demo/run.py desktop-ui
python demo/run.py desktop-search
```

自动验证 UI 与搜索示例时使用 `--smoke`，结束后释放窗口与 worker：

```bash
# 无显示器环境；Windows PowerShell 先执行 $env:QT_QPA_PLATFORM='offscreen'
QT_QPA_PLATFORM=offscreen python demo/run.py desktop-ui --smoke
QT_QPA_PLATFORM=offscreen python demo/run.py desktop-search --smoke
QT_QPA_PLATFORM=offscreen python demo/run.py desktop-contracts-qt
```

core、failures 与 contracts 本身会自动退出，不接受 `--smoke`。这些例子不连接真实打印机、串口、网络服务或业务数据库；UI smoke 不代表目标平台或设备验收。

## 代码与进一步阅读

- [组合源码](../packages/python/desktop/examples/desktop_demo.py)、[六页展示](../packages/python/desktop/examples/qt_showcase.py)、[后台搜索](../packages/python/desktop/examples/background_search.py)。
- [失败恢复源码](../packages/python/desktop/examples/failure_scenarios.py)、[契约例子检查器](../packages/python/desktop/examples/check_contract_examples.py)。
- [Wiki 场景索引](../wiki/Home.md)、[文档总览](../docs/README.md)、[包内手册](../packages/python/desktop/docs/README.md)。

## 后续添加其他项目的 demo

真实示例放在 `packages/<language>/<domain>/examples/`，本目录只保留统一入口。更新 [demo 清单](catalog.json)，关联已有包 ID、脚本、指南、依赖与可选 smoke 参数；当前启动器支持 Python，其他运行时需要显式扩展并验证。不要为来源项目复制能力实现。

提交前运行 `python demo/run.py --check` 和受影响示例；同步 [收录流程](../docs/能力收录流程.md) 与 CI。交互例子应有可自动退出的 smoke，所有成功与失败路径均释放演示资源。
