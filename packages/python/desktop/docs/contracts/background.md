---
title: "desktop.background 公开契约"
category: "工程能力"
tags: ["desktop", "async", "type/api-contract"]
summary: "后台任务提交、取消、超时与资源释放的公开契约。"
created: 2026-10-20
updated: 2026-10-28
metadata_status: reviewed
home_area: theme
article_status: published
required_extra: qt
---

# desktop.background

## 用途与范围

由 Qt 线程拥有的最新请求执行器，最多一个执行任务和一个可替换等待项；通过信号交付结果，关闭或父对象销毁会取消任务，不强杀线程。

导入模块为 `ctf_desktop.background`，下列参数、返回值和资源条件均对应本页模块。

## 模块信息

| 标识项 | 本模块信息 |
| --- | --- |
| API 命名空间 | `desktop.background` |
| Python 导入 | `ctf_desktop.background` |
| 所属发行包 | `common-tech-framework-desktop` |
| 包导入名 | `ctf_desktop` |

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
| 本模块接口与升级 | 最新请求与有限等待槽，不适用于必须逐条执行的写入/收费/打印；取消与超时不撤销外部副作用，也不强杀阻塞 IO。 |
| GUI 适配范围 | 当前使用 PyQt5，没有 PyQt6/PySide 适配承诺；目标系统真实窗口需应用验证。 |
| 验证边界 | 依赖下限不等于所有版本组合已验证；Python/Qt、目标系统与真实设备须按实际环境确认。 |

## 安装与导入

以下命令在本仓库根目录执行，使用当前源码安装，不假定 PyPI 已发布同名版本。

```bash
python -m pip install "./packages/python/desktop[qt]"
```

导入路径：`ctf_desktop.background`。

## 调用前置条件

| 调用方责任 | 要求 |
| --- | --- |
| 任务函数 | 提供 operation(cancel_event)，工作线程自行创建和关闭 IO 资源。 |
| 结束条件 | 外部 IO 设置有限超时，操作检查 Event；不能依靠执行器强杀线程。 |
| 结果接收 | 在 Qt 线程连接成功、失败、取消和超时信号，以请求 ID 判断当前结果。 |

## 调用签名与默认值

### 构造入口

| 入口 | 输入签名 |
| --- | --- |
| `BackgroundTaskRunner` | `BackgroundTaskRunner(parent=None)` |

### 方法

| 入口 | 输入签名 |
| --- | --- |
| `BackgroundTaskRunner.submit` | <code>BackgroundTaskRunner.submit(operation: Callable[[Event], Any], *, timeout_ms: int &#124; None=None)</code> |
| `BackgroundTaskRunner.cancel` | `BackgroundTaskRunner.cancel()` |
| `BackgroundTaskRunner.close` | `BackgroundTaskRunner.close(*, wait: bool=True)` |

签名只列输入，返回结果另表说明；类型标注不意味着每个参数都在运行时强制校验。

## 配置字段与只读属性

### 配置字段

本模块未声明单独的 dataclass 配置字段；构造参数列在下一节。
### 只读属性

本模块未额外声明 @property 只读访问器；值对象字段与调用参数分别在相应表中说明。

## 输入参数

### BackgroundTaskRunner 构造参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `parent` | 未标注 | `None` | 位置或关键字 | Qt 父对象，默认 None；子控件/对象的所有权遵循 Qt 父子关系。 |

### BackgroundTaskRunner.submit 输入参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `operation` | `Callable[[Event], Any]` | 必填 | 位置或关键字 | 工作线程调用的 operation(cancel_event)；自行设置 IO 超时、检查取消并释放资源。 |
| `timeout_ms` | <code>int &#124; None</code> | `None` | 仅关键字 | 可选正整数毫秒截止时间；None 不设截止时间，超时不强杀外部 IO。 |

### BackgroundTaskRunner.close 输入参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `wait` | `bool` | `True` | 仅关键字 | 是否等待有界工作线程退出；False 先返回但不代表资源已全部释放。 |

## 返回值

| 接口 | 返回类型 | 返回结果 |
| --- | --- | --- |
| `BackgroundTaskRunner.submit` | `int` | 当前提交的递增整数请求 ID，用于关联结果与取消/超时通知。 |
| `BackgroundTaskRunner.cancel` | `None` | None；没有业务返回值。对应操作与失败边界分别在接口说明和错误表中列明。 |
| `BackgroundTaskRunner.close` | `None` | None；没有业务返回值。对应操作与失败边界分别在接口说明和错误表中列明。 |

## 信号

| 信号 | 载荷类型（按顺序） | 发出条件与含义 |
| --- | --- | --- |
| `BackgroundTaskRunner.succeeded` | `int, object` | 最新有效请求成功；依次携带请求 ID 与结果值，在 Qt 线程交付。 |
| `BackgroundTaskRunner.failed` | `int, object` | 最新有效请求失败；依次携带请求 ID 与异常对象。 |
| `BackgroundTaskRunner.cancelled` | `int` | 被替换或显式取消的请求 ID，不代表外部 IO 已立即结束。 |
| `BackgroundTaskRunner.timed_out` | `int` | 超时请求 ID；与手动取消分开，迟到结果不再交付。 |

## 错误与边界

| 触发情况 | 错误或结果 | 调用方处理 |
| --- | --- | --- |
| operation 或 timeout_ms 非法 | ValueError | 提交前检查配置。 |
| 已关闭后提交 | RuntimeError | 为新拥有者创建新执行器。 |
| 操作失败/取消/超时 | 对应 failed/cancelled/timed_out 信号 | 按请求 ID 展示结果，仍需等待外部工作释放。 |

### 取消、超时与清理

| 状态 | 用户可见结果 | 资源约束 |
| --- | --- | --- |
| 替换 / 取消 | 旧结果不显示 | 已开始的操作仍须观察 Event；不能依靠取消撤销副作用 |
| 超时 | 发出 `timed_out`，忽略晚到结果 | 外部原生调用仍可能运行；设置它自身的 IO 超时 |
| `close(wait=True)` | 停止新交付并等待退出 | 只能等待有界、可合作的操作；不在 worker 内等待自己 |
| 父对象销毁 | 非阻塞取消 | 不能据此声称第三方 IO 已立即结束 |

不要在工作线程读写 Qt 控件。关闭应用时先取消、再等待任务与其连接释放。测试覆盖正常、异常、取消、超时、队列上限、重入及父对象销毁，入口为 [test_background.py](../../tests/test_background.py)；[公开契约](../contracts/background.md) 给出精确签名。

## 线程与资源

| 资源 | 拥有者 | 线程与释放要求 |
| --- | --- | --- |
| Qt 执行器 | 创建它的 Qt 线程 | close(wait=True) 等待有界工作退出；父对象销毁仅非阻塞取消。 |
| 任务内 IO | operation 自己 | 在工作线程建立并在 finally 关闭，不借用 GUI 线程连接。 |

## 调用流程

```mermaid
flowchart TD
    A[Qt 线程 submit] --> B[递增 ID 并取消旧请求]
    B --> C[一个运行槽和一个可替换等待槽]
    C --> D[工作线程 operation 接收取消 Event]
    D --> E{仍为最新有效请求}
    E -->|否| F[忽略迟到结果]
    E -->|是| G{操作结果}
    G -->|返回| H[succeeded 在 Qt 线程交付]
    G -->|异常| I[failed 在 Qt 线程交付]
    A --> J[cancel 或超时]
    J --> K[通知取消 Event 并阻止结果交付]
```

## BackgroundTaskRunner

稳定标识：`desktop.background.BackgroundTaskRunner`

由 Qt 线程拥有的最新请求执行器，最多一个执行任务和一个可替换等待项；通过信号交付结果，关闭或父对象销毁会取消任务，不强杀线程。

## BackgroundTaskRunner.submit

稳定标识：`desktop.background.BackgroundTaskRunner.submit`

提交 operation(cancel_event) 并返回递增请求 ID；可设置正整数 timeout_ms，较新请求替换等待项并取消旧代次，晚到的旧结果不交付。

## BackgroundTaskRunner.cancel

稳定标识：`desktop.background.BackgroundTaskRunner.cancel`

停止当前截止计时器，清除等待项并向正在执行的操作设置取消标记；不会强行中断外部 IO。

## BackgroundTaskRunner.close

稳定标识：`desktop.background.BackgroundTaskRunner.close`

停止接收和交付请求并发出取消；wait=True 等待工作线程退出，操作必须能有限结束，不能让工作线程等待自己。

## 最小调用示例

示例启动 Qt 事件循环等待信号，并设置兜底退出。真实 IO 必须在操作内设置超时、创建并关闭连接；不能借用 GUI 线程的 SQLite 连接。

```python
from PyQt5.QtCore import QEventLoop, QTimer
from PyQt5.QtWidgets import QApplication
from ctf_desktop.background import BackgroundTaskRunner

app = QApplication.instance() or QApplication([])
runner = BackgroundTaskRunner()
loop = QEventLoop()
received = []

def operation(cancel_event):
    if cancel_event.wait(0.01):
        return None
    return ["示例结果"]

def delivered(identity, value):
    received.append((identity, value))
    loop.quit()

runner.succeeded.connect(delivered)
runner.failed.connect(lambda identity, error: loop.quit())
runner.timed_out.connect(lambda identity: loop.quit())
watchdog = QTimer()
watchdog.setSingleShot(True)
watchdog.timeout.connect(loop.quit)
try:
    identity = runner.submit(operation, timeout_ms=1000)
    watchdog.start(2000)
    loop.exec_()
    assert received == [(identity, ["示例结果"])]
finally:
    watchdog.stop()
    runner.close()
```

<span id="qt-信号" class="legacy-anchor" aria-hidden="true"></span>

## 验证与源码依据

实现依据：[background.py](../../src/ctf_desktop/background.py)；版本与依赖声明：[pyproject.toml](../../pyproject.toml)。

| 验证文件 | 用途 |
| --- | --- |
| [test_background.py](../../tests/test_background.py) | 源码标注的契约或回归入口；按改动范围选用。 |

在已按本页安装依赖的仓库根目录运行：

```bash
python packages/python/desktop/examples/check_contract_examples.py --qt
```

示例检查只执行本仓库文档代码；pytest 回归另需 test extra（pytest>=8），Qt 回归还需 qt extra。浏览器 mock、离屏示例与真实 GUI/设备验收是不同验证范围。
