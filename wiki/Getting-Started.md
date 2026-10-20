---
title: "上手步骤"
category: "工程能力"
tags: ["type/handbook", "能力复用"]
summary: "从隔离环境安装到核心与交互 demo 的最短路径。"
created: 2026-10-20
updated: 2026-10-20
metadata_status: reviewed
home_area: theme
article_status: published
---

# 上手步骤

## 1. 从仓库根目录安装

Python >= 3.11。以下为克隆完成后的步骤，仓库根目录不是可安装 Python 包：

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install './packages/python/desktop'
python demo/run.py desktop-core
```

看到 `Desktop example passed` 后，基础组合运行成功。示例使用临时目录、内存仓储和模拟提交，不需要配置业务数据库或真实打印机。

## 2. 体验界面与后台任务

```bash
python -m pip install './packages/python/desktop[qt]'
python demo/run.py desktop-ui
python demo/run.py desktop-search
```

桌面示例可选择 Table、Form、Filters、Feedback、CRUD 和 Async search；尝试翻页、编辑样例和切换页面。搜索示例输入文字后返回样例行，Cancel 请求协作取消，关闭窗口释放后台任务。

没有图形会话时执行 [demo 的 smoke 命令](../demo/README.md)。`--list` 查看全部入口，`--check` 检查示例清单，无需先安装桌面依赖。

## 3. 接入自己的应用

按 [能力地图](Capabilities.md) 选择模块，阅读对应指南和契约，替换仓储、授权策略或设备适配。仅用标准库模块不用安装 Qt；连接真实串口额外安装 `serial`；跑全部测试使用 `all`。

安装本地包不会把能力自动接入任何已有项目。发行名为 `common-tech-framework-desktop`，导入名为 `ctf_desktop`；本仓库和旧来源提供同名发行包，应在应用隔离环境中明确选择一种来源。

[完整安装与接口例子](../packages/python/desktop/docs/快速开始.md) · [排障](Troubleshooting.md)
