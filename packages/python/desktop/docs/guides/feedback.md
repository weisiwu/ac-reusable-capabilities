---
title: "反馈控件使用指南"
category: "工程能力"
tags: ["desktop", "feedback", "type/usage-guide"]
summary: "反馈控件的场景选择、接入步骤、错误处理、资源所有权与验证入口。"
created: 2026-10-20
updated: 2026-10-28
metadata_status: reviewed
home_area: theme
article_status: published
required_extra: qt
---

# 反馈控件

<span id="适用场景" class="legacy-anchor" aria-hidden="true"></span>

## 用途与范围

让应用组合确认框、空态、忙碌遮罩与短时提示。

在 Qt 线程提供有效父控件，子控件生命周期遵循 Qt 父子关系。

## 模块信息

| 标识项 | 本模块信息 |
| --- | --- |
| API 命名空间 | `desktop.feedback` |
| Python 导入 | `ctf_desktop.feedback` |
| 所属发行包 | `common-tech-framework-desktop` |
| 包导入名 | `ctf_desktop` |

<span id="接入速查" class="legacy-anchor" aria-hidden="true"></span>

## 运行环境

| 环境项 | 要求 | 说明 |
| --- | --- | --- |
| Python | >=3.11 | 安装声明；不把更高版本的可安装性当作实际验证。 |
| Qt 运行环境 | 需要事件循环 | 示例使用 QApplication；控件/执行器由创建它的 Qt 线程使用。 |

## 依赖要求

### 运行依赖

| 依赖 | 版本 / 状态 | 使用条件 |
| --- | --- | --- |
| PyQt5 | >=5.15 | 使用 qt extra；本模块导入 Qt API。 |

### 构建依赖

| 依赖 | 声明下限 | 使用阶段 |
| --- | --- | --- |
| setuptools | >=77 | 从源码安装/构建时由 pip 隔离构建环境使用。 |
| wheel | 未声明下限 | 发行包构建依赖，不是应用运行依赖。 |

## 版本信息

| 版本项 | 当前值 / 识别方式 | 说明 |
| --- | --- | --- |
| 能力包版本 | `0.2.0` | 对应 pyproject.toml 与包版本常量。 |
| 模块版号 | 随所属包发布 | 本模块没有另行声明独立的模块版本号。 |
| 源码身份 | 网页头部的构建提交或所读 Git 版本 | 接入时记录实际安装 commit/wheel 来源；相同包版本不能代替源码身份。 |

## 兼容要求

| 兼容维度 | 本页具体要求与边界 |
| --- | --- |
| 本模块接口与升级 | 重复 Toast 会重启其计时器；BusyOverlay 跟随父窗口尺寸。控件只负责呈现，不承诺工作完成或取消。 |
| GUI 适配范围 | 当前使用 PyQt5，没有 PyQt6/PySide 适配承诺；目标系统真实窗口需应用验证。 |
| 验证边界 | 依赖下限不等于所有版本组合已验证；Python/Qt、目标系统与真实设备须按实际环境确认。 |

完整历史记录可继续查阅[架构与依赖](../架构与依赖.md)和[升级与兼容](../升级与兼容.md)；本模块当前要求已在本页说明。

## 安装与导入

以下命令在本仓库根目录执行，使用当前源码安装，不假定 PyPI 已发布同名版本。

```bash
python -m pip install "./packages/python/desktop[qt]"
```

导入路径：`ctf_desktop.feedback`。

## 接入准备

| 应用需要提供 | 具体要求 |
| --- | --- |
| 父窗口 | 在 Qt 线程提供有效父控件，子控件生命周期遵循 Qt 父子关系。 |
| 工作执行 | 应用自己执行/取消任务；BusyOverlay 仅显示状态。 |
| 文案与清理 | 标题、详情和成功/失败文案由应用提供；关闭拥有者时释放子控件。 |

## 核心入口

| 入口 | 职责 |
| --- | --- |
| `ConfirmDialog` | Qt 线程的确认包装，标题和正文由应用提供，默认回答为 No。 |
| `EmptyState` | 显示标题和可选详情的静态控件，详情默认空，Qt 父对象拥有生命周期。 |
| `BusyOverlay` | 初始隐藏的子控件，自动跟随父窗口尺寸；只显示忙碌状态，工作与取消仍由应用实现。 |
| `Toast` | 初始隐藏的短时反馈标签，Qt 父对象拥有生命周期。 |

## 接入流程

```mermaid
flowchart LR
    N0["确认操作"]
    N1["显示忙碌"]
    N0 --> N1
    N2["工作结果"]
    N1 --> N2
    N3["隐藏忙碌并反馈"]
    N2 --> N3
```

## 调用步骤

| 步骤 | 操作 |
| --- | --- |
| 1 | 确认操作 |
| 2 | 显示忙碌 |
| 3 | 工作结果 |
| 4 | 隐藏忙碌并反馈 |

## 输入签名

### 构造入口

| 入口 | 输入签名 |
| --- | --- |
| `EmptyState` | `EmptyState(title: str, detail: str='', parent=None)` |
| `BusyOverlay` | `BusyOverlay(parent: QWidget)` |
| `Toast` | `Toast(parent: QWidget)` |

### 方法

| 入口 | 输入签名 |
| --- | --- |
| `ConfirmDialog.ask` | <code>ConfirmDialog.ask(parent: QWidget &#124; None, title: str, message: str)</code> |
| `BusyOverlay.show_message` | `BusyOverlay.show_message(message: str)` |
| `Toast.show_message` | `Toast.show_message(message: str, duration_ms: int=3000)` |

签名只列输入，返回结果另表说明；类型标注不意味着每个参数都在运行时强制校验。

## 配置字段

本模块未声明单独的 dataclass 配置字段；构造参数列在下一节。

## 配置参数与调用参数

### ConfirmDialog.ask 输入参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `parent` | <code>QWidget &#124; None</code> | 必填 | 位置或关键字 | 必须显式传入 Qt 父对象；类型允许时可传 None，所有权遵循 Qt 父子关系。 |
| `title` | `str` | 必填 | 位置或关键字 | 应用提供的窗口、页面或列标题；不作为 SQL 表达式。 |
| `message` | `str` | 必填 | 位置或关键字 | 应用提供的提示文字；该参数不执行工作或决定业务成功。 |

### EmptyState 构造参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `title` | `str` | 必填 | 位置或关键字 | 应用提供的窗口、页面或列标题；不作为 SQL 表达式。 |
| `detail` | `str` | `''` | 位置或关键字 | 空状态的补充说明文字，默认空字符串。 |
| `parent` | 未标注 | `None` | 位置或关键字 | Qt 父对象，默认 None；子控件/对象的所有权遵循 Qt 父子关系。 |

### BusyOverlay 构造参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `parent` | `QWidget` | 必填 | 位置或关键字 | 必须显式传入 Qt 父对象；类型允许时可传 None，所有权遵循 Qt 父子关系。 |

### BusyOverlay.show_message 输入参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `message` | `str` | 必填 | 位置或关键字 | 应用提供的提示文字；该参数不执行工作或决定业务成功。 |

### Toast 构造参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `parent` | `QWidget` | 必填 | 位置或关键字 | 必须显式传入 Qt 父对象；类型允许时可传 None，所有权遵循 Qt 父子关系。 |

### Toast.show_message 输入参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `message` | `str` | 必填 | 位置或关键字 | 应用提供的提示文字；该参数不执行工作或决定业务成功。 |
| `duration_ms` | `int` | `3000` | 位置或关键字 | 非负整数显示毫秒数；再次提示时重启已有计时器。 |

## 只读属性

本模块未额外声明 @property 只读访问器；值对象字段与调用参数分别在相应表中说明。

## 返回值

| 接口 | 返回类型 | 返回结果 |
| --- | --- | --- |
| `ConfirmDialog.ask` | `bool` | 用户明确选择 Yes 时 True，其余选择为 False。 |
| `BusyOverlay.show_message` | `None` | None；没有业务返回值。对应操作与失败边界分别在接口说明和错误表中列明。 |
| `Toast.show_message` | `None` | None；没有业务返回值。对应操作与失败边界分别在接口说明和错误表中列明。 |

## 信号

本模块不新增 Qt 信号。同步调用结果见返回值表；应用注入回调的输入约定见参数表。

## 错误与边界

| 触发情况 | 错误或结果 | 调用方处理 |
| --- | --- | --- |
| Toast 时长非法 | ValueError，在修改状态前拒绝 | 使用非负整数毫秒。 |
| 任务失败或取消 | 控件不会自动执行处理 | 应用在完成路径隐藏 busy 并给出反馈。 |

### 失败与边界

Toast duration_ms 必须非负整数，非法参数在改变界面前拒绝；新文案不会被旧文案计时器提前隐藏。

busy 不执行任务或自动取消；确认框不执行权限检查。默认样式是参考值，可由应用主题替换。

## 线程与资源

| 资源 | 拥有者 | 线程与释放要求 |
| --- | --- | --- |
| 控件与计时器 | Qt 父对象 | 只在 Qt 线程操作；关闭父对象时释放；遮罩不拥有工作任务。 |

GUI 线程使用，父窗口拥有控件；父窗口销毁后计时器一同销毁，不创建常驻线程。

## 接口与接入

ConfirmDialog 默认选择 No；EmptyState 为标签；BusyOverlay 跟随父窗大小；Toast 拥有可重启的单次隐藏计时器。

应用提供文案；确认框返回 true 才写入；显示 busy 前启动任务、完成/失败后 hide；重复 toast 会替换文案并重新计时。

<span id="示例与验证" class="legacy-anchor" aria-hidden="true"></span>

## 最小调用示例

示例使用虚构数据和临时资源，不连接真实设备或业务存储。 需要先安装 qt 依赖；创建 QApplication 后再建立控件。

```python
from PyQt5.QtWidgets import QApplication, QWidget
from ctf_desktop.feedback import EmptyState, BusyOverlay, Toast
app = QApplication.instance() or QApplication([])
parent = QWidget()
empty = EmptyState("Empty", parent=parent)
overlay = BusyOverlay(parent)
overlay.show_message("Working")
Toast(parent).show_message("Done", 100)
parent.close()
```

## 验证与源码依据

实现依据：[feedback.py](../../src/ctf_desktop/feedback.py)；版本与依赖声明：[pyproject.toml](../../pyproject.toml)。

| 验证文件 | 用途 |
| --- | --- |
| [test_qt.py](../../tests/test_qt.py) | 源码标注的契约或回归入口；按改动范围选用。 |
| [test_qt_contracts.py](../../tests/test_qt_contracts.py) | 源码标注的契约或回归入口；按改动范围选用。 |
| [test_review_qt.py](../../tests/test_review_qt.py) | 源码标注的契约或回归入口；按改动范围选用。 |

在已按本页安装依赖的仓库根目录运行：

```bash
python packages/python/desktop/examples/check_contract_examples.py --qt
```

示例检查只执行本仓库文档代码；pytest 回归另需 test extra（pytest>=8），Qt 回归还需 qt extra。浏览器 mock、离屏示例与真实 GUI/设备验收是不同验证范围。
