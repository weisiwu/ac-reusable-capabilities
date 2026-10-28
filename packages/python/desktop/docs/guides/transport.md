---
title: "字节传输与串口使用指南"
category: "工程能力"
tags: ["desktop", "serial", "type/usage-guide"]
summary: "串口工厂注入、配置、短写处理、关闭失败重试与设备协议边界。"
created: 2026-10-20
updated: 2026-10-28
metadata_status: reviewed
home_area: theme
article_status: published
---

# 字节传输与串口

## 用途与范围

与具体后端无关的 open/close/read/write 协议；超时与并发由实现定义，不包含设备指令。

真实串口需要 pyserial、设备驱动、端口权限及应用协议；注入工厂可不用真实硬件。

## 模块信息

| 标识项 | 本模块信息 |
| --- | --- |
| API 命名空间 | `desktop.transport` |
| Python 导入 | `ctf_desktop.transport` |
| 所属发行包 | `common-tech-framework-desktop` |
| 包导入名 | `ctf_desktop` |

<span id="接入速查" class="legacy-anchor" aria-hidden="true"></span>

## 运行环境

| 环境项 | 要求 | 说明 |
| --- | --- | --- |
| Python | >=3.11 | 安装声明；不把更高版本的可安装性当作实际验证。 |
| 图形环境 | 不需要 Qt | 本模块直接运行逻辑不要求 QApplication。 |

## 依赖要求

### 运行依赖

| 依赖 | 版本 / 状态 | 使用条件 |
| --- | --- | --- |
| pyserial | >=3.5（按需） | 只有默认串口工厂打开真实串口时需要 serial extra；注入工厂不需要。 |

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
| 本模块接口与升级 | 0.2.0 更早拒绝非法端口、bool 波特率和非有限超时；Transport 接口不等于真实设备协议兼容。 |
| 设备兼容范围 | 工厂注入测试或网页模拟不等于真实设备、驱动和协议验收。 |
| 验证边界 | 依赖下限不等于所有版本组合已验证；Python/Qt、目标系统与真实设备须按实际环境确认。 |

完整历史记录可继续查阅[架构与依赖](../架构与依赖.md)和[升级与兼容](../升级与兼容.md)；本模块当前要求已在本页说明。

## 安装与导入

以下命令在本仓库根目录执行，使用当前源码安装，不假定 PyPI 已发布同名版本。 若只使用协议或注入假工厂，可去掉 serial extra。

```bash
python -m pip install "./packages/python/desktop[serial]"
```

导入路径：`ctf_desktop.transport`。

## 接入准备

| 应用需要提供 | 具体要求 |
| --- | --- |
| 串口环境 | 真实串口需要 pyserial、设备驱动、端口权限及应用协议；注入工厂可不用真实硬件。 |
| 协议层 | 帧格式、CRC、ACK、重试与自动重连由应用实现。 |
| 关闭责任 | 应用提供有限读写超时并在退出时 close；关闭失败保留句柄供清理重试。 |

## 核心入口

| 入口 | 职责 |
| --- | --- |
| `Transport` | 与具体后端无关的 open/close/read/write 协议；超时与并发由实现定义，不包含设备指令。 |
| `TransportError` | 归一化打开、读取、写入等失败的 IOError 子类，能取得底层原因时通过异常链保留。 |
| `SerialConfig` | 冻结的串口配置：port 为非空白字符串，baudrate 默认9600且为正整数，读写超时默认1.0且为有限非负数；非法值抛 ValueError。 |
| `SerialTransport` | 拥有串口句柄与 RLock，可注入工厂；with 负责打开和所有退出路径的关闭，设备协议与重试由应用负责。 |

## 接入流程

```mermaid
flowchart LR
    N0["配置端口"]
    N1["open"]
    N0 --> N1
    N2["write/read"]
    N1 --> N2
    N3["协议层处理"]
    N2 --> N3
    N4["close"]
    N3 --> N4
```

## 调用步骤

| 步骤 | 操作 |
| --- | --- |
| 1 | 配置端口 |
| 2 | open |
| 3 | write/read |
| 4 | 协议层处理 |
| 5 | close |

## 输入签名

### 构造入口

| 入口 | 输入签名 |
| --- | --- |
| `SerialTransport` | <code>SerialTransport(config: SerialConfig, factory: Callable &#124; None=None)</code> |

### 方法

| 入口 | 输入签名 |
| --- | --- |
| `Transport.open` | `Transport.open()` |
| `Transport.close` | `Transport.close()` |
| `Transport.write` | `Transport.write(payload: bytes)` |
| `Transport.read` | `Transport.read(size: int)` |
| `SerialTransport.open` | `SerialTransport.open()` |
| `SerialTransport.close` | `SerialTransport.close()` |
| `SerialTransport.write` | `SerialTransport.write(payload: bytes)` |
| `SerialTransport.read` | `SerialTransport.read(size: int)` |

签名只列输入，返回结果另表说明；类型标注不意味着每个参数都在运行时强制校验。

## 配置字段

### SerialConfig 字段

| 字段 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `port` | `str` | 必填 | 真实或工厂识别的串口名，非空白字符串；不包含帧协议。 |
| `baudrate` | `int` | `9600` | 正整数波特率，默认9600，不接受 bool。 |
| `timeout` | `float` | `1.0` | 读取超时秒数，默认1.0，必须有限且非负。 |
| `write_timeout` | `float` | `1.0` | 写入超时秒数，默认1.0，必须有限且非负。 |

冻结值对象禁止直接重新赋值字段；含映射或其他对象时，不代表内部对象被深度冻结。

## 配置参数与调用参数

### Transport.write 输入参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `payload` | `bytes` | 必填 | 位置或关键字 | 提交的完整字节载荷；写入成功不代表设备已处理或返回 ACK。 |

### Transport.read 输入参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `size` | `int` | 必填 | 位置或关键字 | 最大读取字节数，具体实现规定超时和错误。 |

### SerialTransport 构造参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `config` | `SerialConfig` | 必填 | 位置或关键字 | 已校验的 SerialConfig，包含端口、波特率与有界读写超时。 |
| `factory` | <code>Callable &#124; None</code> | `None` | 位置或关键字 | 可选后端工厂，接收串口配置关键字并返回句柄；None 才加载 pyserial。 |

### SerialTransport.write 输入参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `payload` | `bytes` | 必填 | 位置或关键字 | 提交的完整字节载荷；写入成功不代表设备已处理或返回 ACK。 |

### SerialTransport.read 输入参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `size` | `int` | 必填 | 位置或关键字 | 非负整数字节数，不接受 bool；可能返回少于该数目的 bytes。 |

## 只读属性

| 只读属性 | 类型 | 读取语义 |
| --- | --- | --- |
| `SerialTransport.is_open` | `bool` | 只读地在锁内取得自有句柄打开状态；未持有句柄时为 False。 |

## 返回值

| 接口 | 返回类型 | 返回结果 |
| --- | --- | --- |
| `Transport.open` | `None` | None；没有业务返回值。对应操作与失败边界分别在接口说明和错误表中列明。 |
| `Transport.close` | `None` | None；没有业务返回值。对应操作与失败边界分别在接口说明和错误表中列明。 |
| `Transport.write` | `None` | None；提交不等于收到设备 ACK。 |
| `Transport.read` | `bytes` | 不多于 size 的 bytes，具体超时规则由实现规定。 |
| `SerialTransport.open` | `None` | None；没有业务返回值。对应操作与失败边界分别在接口说明和错误表中列明。 |
| `SerialTransport.close` | `None` | None；没有业务返回值。对应操作与失败边界分别在接口说明和错误表中列明。 |
| `SerialTransport.write` | `None` | None；本次完整写入并 flush，不提供设备处理确认。 |
| `SerialTransport.read` | `bytes` | 不多于 size 的 bytes，超时可能返回较短或空字节串。 |

## 信号

本模块不新增 Qt 信号。同步调用结果见返回值表；应用注入回调的输入约定见参数表。

## 错误与边界

| 触发情况 | 错误或结果 | 调用方处理 |
| --- | --- | --- |
| 端口、波特率、超时或 read size 非法 | ValueError | 使用有界且类型正确的配置。 |
| 未打开、短写或后端错误 | TransportError | 检查异常链，按业务协议决定恢复，不自动重试。 |
| 关闭失败 | TransportError，保留句柄 | 修复后端后重新清理，不把失败关闭当作已释放。 |

### 错误与副作用

open 在已拥有句柄时幂等；read/write 在锁内串行化。write 必须完整写入后才 flush，短写和驱动错误转换为 TransportError，并保留底层 __cause__；不自动重试不确定的发送，避免重复触发设备操作。

close 失败保留句柄以便再次清理，成功才释放所有权。with SerialTransport(...) 会打开并在退出时关闭；如果驱动关闭失败，应用仍需记录并重试释放。它不代表 USB 断开后能无条件恢复同一物理连接。

<span id="资源与线程" class="legacy-anchor" aria-hidden="true"></span>

## 线程与资源

| 资源 | 拥有者 | 线程与释放要求 |
| --- | --- | --- |
| 串口句柄和锁 | SerialTransport | finally close 或 with；失败保留句柄以便重试清理，应用 IO 需有限超时。 |

一个对象拥有一个句柄；不要绕开该对象同时操作底层串口。读写超时只约束对应驱动调用，不能替代上层任务的取消策略。串口任务放入后台时由任务创建/关闭对象，不把 GUI 控件带进 worker。

[公开契约与最小例子](../contracts/transport.md) 展示工厂注入；[异常场景](../../examples/failure_scenarios.py) 展示短写不重试。测试入口为 tests/test_core.py、tests/test_contracts.py、tests/test_review_core.py、tests/test_extensions_core.py；真实端口与平台安装包仍由接入项目验收。

## 接入顺序

Transport 是字节 IO 协议，SerialTransport 是可选 pyserial 实现。先注入一个模拟工厂验证正常收发、短写和关闭路径，再接真实端口；上层自行处理帧提取、命令、应答、重试和心跳。

SerialConfig 要求非空白端口、正整数波特率、有限非负读写超时，bool 不当整数使用。默认 9600 波特率、读写各 1 秒；真实设备参数由应用明确配置。

## 最小调用示例

示例使用虚构数据和临时资源，不连接真实设备或业务存储。 此处注入假串口工厂，不验证真实串口或设备协议。

```python
from ctf_desktop.transport import SerialConfig, SerialTransport
class Handle:
    is_open = True
    def __init__(self, **kwargs): pass
    def write(self, payload): return len(payload)
    def flush(self): pass
    def read(self, size): return b"ok"[:size]
    def close(self): self.is_open = False
transport = SerialTransport(SerialConfig("example-port"), Handle)
try:
    transport.open()
    transport.write(b"request")
    assert transport.read(2) == b"ok"
finally:
    transport.close()
```

## 验证与源码依据

实现依据：[transport.py](../../src/ctf_desktop/transport.py)；版本与依赖声明：[pyproject.toml](../../pyproject.toml)。

| 验证文件 | 用途 |
| --- | --- |
| [test_contracts.py](../../tests/test_contracts.py) | 源码标注的契约或回归入口；按改动范围选用。 |
| [test_core.py](../../tests/test_core.py) | 源码标注的契约或回归入口；按改动范围选用。 |
| [test_review_core.py](../../tests/test_review_core.py) | 源码标注的契约或回归入口；按改动范围选用。 |

在已按本页安装依赖的仓库根目录运行：

```bash
python packages/python/desktop/examples/check_contract_examples.py
```

示例检查只执行本仓库文档代码；pytest 回归另需 test extra（pytest>=8），Qt 回归还需 qt extra。浏览器 mock、离屏示例与真实 GUI/设备验收是不同验证范围。
