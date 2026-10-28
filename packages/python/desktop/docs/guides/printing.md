---
title: "批量打印调度使用指南"
category: "工程能力"
tags: ["desktop", "printing", "type/usage-guide"]
summary: "批量打印调度的场景选择、接入步骤、错误处理、资源所有权与验证入口。"
created: 2026-10-20
updated: 2026-10-28
metadata_status: reviewed
home_area: theme
article_status: published
---

# 批量打印调度

<span id="适用场景" class="legacy-anchor" aria-hidden="true"></span>

## 用途与范围

一条数据准备一次成品，多份提交，有取消和失败统计。

prepare(key) 返回 bytes；每项内容只准备一次。

## 模块信息

| 标识项 | 本模块信息 |
| --- | --- |
| API 命名空间 | `desktop.printing` |
| Python 导入 | `ctf_desktop.printing` |
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
| 第三方运行依赖 | 无 | 使用标准库；应用后端的额外依赖由应用声明。 |

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
| 本模块接口与升级 | 0.2.0 拒绝重叠 run 和关闭后执行；成功计数是后端提交数，不是物理出纸数，框架没有自动重试。 |
| 接入应用兼容 | 本模块不替代应用的业务数据、权限规则或外部依赖兼容检查。 |
| 验证边界 | 依赖下限不等于所有版本组合已验证；Python/Qt、目标系统与真实设备须按实际环境确认。 |

完整历史记录可继续查阅[架构与依赖](../架构与依赖.md)和[升级与兼容](../升级与兼容.md)；本模块当前要求已在本页说明。

## 安装与导入

以下命令在本仓库根目录执行，使用当前源码安装，不假定 PyPI 已发布同名版本。

```bash
python -m pip install "./packages/python/desktop"
```

导入路径：`ctf_desktop.printing`。

## 接入准备

| 应用需要提供 | 具体要求 |
| --- | --- |
| 准备后端 | prepare(key) 返回 bytes；每项内容只准备一次。 |
| 提交后端 | submit(bytes) 同步完成一次提交；Qt 打印需同步 GUI dispatcher。 |
| 执行边界 | 同实例不允许重叠 run；IO 必须有界，未知提交结果不得盲目重试。 |

## 核心入口

| 入口 | 职责 |
| --- | --- |
| `PrintItem` | 冻结的打印计划项；key 非空，copies 默认1且必须为正整数（不接受 bool），非法配置抛 ValueError。 |
| `BatchPrintResult` | 冻结的总数、成功、失败、跳过和可选错误文字；计数描述后端提交，不代表纸张已经输出。 |
| `CancellationToken` | 初始未取消的线程安全协作标记；不打断正在进行的后端 IO。 |
| `BatchPrintRunner` | 注入准备和提交回调，拥有单工作线程执行器并排斥重叠执行；with 退出会关闭，GUI 提交需应用提供同步 dispatcher，IO 必须有界。 |

## 接入流程

```mermaid
flowchart LR
    N0["准备成品"]
    N1["逐份取消检查"]
    N0 --> N1
    N2["提交"]
    N1 --> N2
    N3["统计结果"]
    N2 --> N3
    N4["close"]
    N3 --> N4
```

## 调用步骤

| 步骤 | 操作 |
| --- | --- |
| 1 | 准备成品 |
| 2 | 逐份取消检查 |
| 3 | 提交 |
| 4 | 统计结果 |
| 5 | close |

## 输入签名

### 构造入口

| 入口 | 输入签名 |
| --- | --- |
| `CancellationToken` | `CancellationToken()` |
| `BatchPrintRunner` | <code>BatchPrintRunner(prepare: Callable[[str], bytes], submit: Callable[[bytes], None], *, dispatch_submit: Callable[[Callable[[], None]], None] &#124; None=None, on_progress: Callable[[str, int, int], None] &#124; None=None)</code> |

### 方法

| 入口 | 输入签名 |
| --- | --- |
| `CancellationToken.cancel` | `CancellationToken.cancel()` |
| `BatchPrintRunner.run` | <code>BatchPrintRunner.run(items: Iterable[PrintItem], token: CancellationToken &#124; None=None)</code> |
| `BatchPrintRunner.start` | <code>BatchPrintRunner.start(items: Iterable[PrintItem], token: CancellationToken &#124; None=None)</code> |
| `BatchPrintRunner.close` | `BatchPrintRunner.close()` |

签名只列输入，返回结果另表说明；类型标注不意味着每个参数都在运行时强制校验。

## 配置字段

### PrintItem 字段

| 字段 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `key` | `str` | 必填 | 传给 prepare 的非空计划项标识。 |
| `copies` | `int` | `1` | 每项提交份数，默认1，正整数且不接受 bool。 |

### BatchPrintResult 字段

| 字段 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `total` | `int` | 必填 | 总数；PageResult 的 total 是匹配记录数，打印结果 total 是计划提交份数。 |
| `succeeded` | `int` | 必填 | 已成功提交的份数，不表示物理出纸。 |
| `failed` | `int` | 必填 | 失败提交的份数，由执行结果给出。 |
| `skipped` | `int` | 必填 | 未执行的计划份数，例如取消或失败后未继续提交的部分。 |
| `error` | <code>str &#124; None</code> | `None` | 可选失败文字，None 表示没有记录该错误文字。 |

冻结值对象禁止直接重新赋值字段；含映射或其他对象时，不代表内部对象被深度冻结。

## 配置参数与调用参数

### BatchPrintRunner 构造参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `prepare` | `Callable[[str], bytes]` | 必填 | 位置或关键字 | prepare(key) 返回成品 bytes，每个 PrintItem 只准备一次。 |
| `submit` | `Callable[[bytes], None]` | 必填 | 位置或关键字 | submit(bytes) 同步提交一份内容；未知结果不得由框架自动重试。 |
| `dispatch_submit` | <code>Callable[[Callable[[], None]], None] &#124; None</code> | `None` | 仅关键字 | 同步调度提交的回调，必须在提交完成后返回；Qt 打印时切回 GUI 线程。 |
| `on_progress` | <code>Callable[[str, int, int], None] &#124; None</code> | `None` | 仅关键字 | on_progress(key, done, total) 进度回调；不是物理出纸确认，异常不重分类已提交结果。 |

### BatchPrintRunner.run 输入参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `items` | `Iterable[PrintItem]` | 必填 | 位置或关键字 | PrintItem 可迭代序列；start 在启动前将任务保存为快照。 |
| `token` | <code>CancellationToken &#124; None</code> | `None` | 位置或关键字 | 协作取消标记；None 时由执行器建立，不打断已进行的提交。 |

### BatchPrintRunner.start 输入参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `items` | `Iterable[PrintItem]` | 必填 | 位置或关键字 | PrintItem 可迭代序列；start 在启动前将任务保存为快照。 |
| `token` | <code>CancellationToken &#124; None</code> | `None` | 位置或关键字 | 协作取消标记；None 时由执行器建立，不打断已进行的提交。 |

## 只读属性

| 只读属性 | 类型 | 读取语义 |
| --- | --- | --- |
| `CancellationToken.cancelled` | `bool` | 只读协作取消标记，不改变状态。 |

## 返回值

| 接口 | 返回类型 | 返回结果 |
| --- | --- | --- |
| `CancellationToken.cancel` | `None` | None；没有业务返回值。对应操作与失败边界分别在接口说明和错误表中列明。 |
| `BatchPrintRunner.run` | `BatchPrintResult` | BatchPrintResult，统计本轮计划、成功提交、失败与跳过份数以及可选错误文字。 |
| `BatchPrintRunner.start` | `Future` | Future；其成功结果为 BatchPrintResult，等待结果需设置应用可接受的超时。 |
| `BatchPrintRunner.close` | `None` | None；没有业务返回值。对应操作与失败边界分别在接口说明和错误表中列明。 |

## 信号

本模块不新增 Qt 信号。同步调用结果见返回值表；应用注入回调的输入约定见参数表。

## 错误与边界

| 触发情况 | 错误或结果 | 调用方处理 |
| --- | --- | --- |
| 非法计划项 | ValueError | 使用非空 key 和正整数 copies。 |
| 重叠执行或关闭后执行 | RuntimeError | 保证同实例一次只执行一轮。 |
| 后端准备/提交失败 | BatchPrintResult 记录失败和 error | 提交结果不确定时停止并核验，不能自动重发。 |

### 失败与边界

单条的 copies 共用一次准备结果；提交结果不确定时停止且不重试。取消在准备前和每份提交前检查，不能打断正在执行的 IO。重叠 run 或关闭后运行抛 RuntimeError。

计数代表提交，不代表打印机实际出纸。不能把失败提交自动重试，否则可能重复打印。没有 PDF 摘要缓存或跨批次去重。

## 线程与资源

run 在调用线程同步执行，start 使用工作线程。若 dispatch_submit 需要 GUI 线程同步完成提交，GUI 线程不得阻塞等待该 Future，以免相互等待。

| 资源 | 拥有者 | 线程与释放要求 |
| --- | --- | --- |
| 执行器和工作 | BatchPrintRunner | 拥有者 finally close 或使用 with；不在活动回调内等待自己。 |
| 打印资源 | 应用后端 | prepare/submit 自行管理句柄，GUI dispatcher 必须同步完成。 |

start 在单工作线程运行；progress 也在那里。close 在拥有者线程调用并等待，不在 worker 回调内关闭；所有外部 IO 必须有有限超时。

## 接口与接入

PrintItem 声明 key/copies；BatchPrintRunner 负责准备与提交；CancellationToken 是协作取消；BatchPrintResult 描述提交计数。

prepare 返回非空 bytes；submit 成功返回 None，失败抛异常；真实 Qt 打印通过同步 dispatch_submit 回到 GUI 线程。

<span id="示例与验证" class="legacy-anchor" aria-hidden="true"></span>

## 最小调用示例

示例使用虚构数据和临时资源，不连接真实设备或业务存储。

```python
from ctf_desktop.printing import BatchPrintRunner, PrintItem
submitted = []
runner = BatchPrintRunner(lambda key: key.encode(), submitted.append)
try:
    assert runner.start([PrintItem("sample", 2)]).result(timeout=2).succeeded == 2
    assert submitted == [b"sample", b"sample"]
finally:
    runner.close()
```

## 验证与源码依据

实现依据：[printing.py](../../src/ctf_desktop/printing.py)；版本与依赖声明：[pyproject.toml](../../pyproject.toml)。

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
