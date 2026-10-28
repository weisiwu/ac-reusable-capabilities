---
title: "服务生命周期使用指南"
category: "工程能力"
tags: ["desktop", "services", "type/usage-guide"]
summary: "服务生命周期的场景选择、接入步骤、错误处理、资源所有权与验证入口。"
created: 2026-10-20
updated: 2026-10-28
metadata_status: reviewed
home_area: theme
article_status: published
---

# 服务生命周期

<span id="适用场景" class="legacy-anchor" aria-hidden="true"></span>

## 用途与范围

按依赖启动数据库、缓存、后台服务，并在失败后清理已启动资源。

注册唯一 ServiceSpec.name、工厂及依赖名，先注册完再启动。

## 模块信息

| 标识项 | 本模块信息 |
| --- | --- |
| API 命名空间 | `desktop.services` |
| Python 导入 | `ctf_desktop.services` |
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
| 本模块接口与升级 | 0.2.0 生命周期回调中拒绝重入；依赖缺失/环在实例创建前拒绝。running 只表示持有服务，不代表健康检查通过。 |
| 接入应用兼容 | 本模块不替代应用的业务数据、权限规则或外部依赖兼容检查。 |
| 验证边界 | 依赖下限不等于所有版本组合已验证；Python/Qt、目标系统与真实设备须按实际环境确认。 |

完整历史记录可继续查阅[架构与依赖](../架构与依赖.md)和[升级与兼容](../升级与兼容.md)；本模块当前要求已在本页说明。

## 安装与导入

以下命令在本仓库根目录执行，使用当前源码安装，不假定 PyPI 已发布同名版本。

```bash
python -m pip install "./packages/python/desktop"
```

导入路径：`ctf_desktop.services`。

## 接入准备

| 应用需要提供 | 具体要求 |
| --- | --- |
| 服务定义 | 注册唯一 ServiceSpec.name、工厂及依赖名，先注册完再启动。 |
| 拥有者线程 | 由同一拥有者线程控制注册、启动和停止，生命周期回调中不重入。 |
| 资源责任 | 工厂在返回实例前失败时须自行释放已创建资源；框架只能清理已取得的实例。 |

## 核心入口

| 入口 | 职责 |
| --- | --- |
| `ServiceSpec` | 冻结的服务名、接收注册表的工厂及依赖名 tuple（默认空）；具体服务由应用实现。 |
| `ServiceStartError` | 启动失败并尝试反序清理后抛出的 RuntimeError 子类，保留原始 cause。 |
| `ServiceRegistry` | 单线程服务注册表，负责依赖拓扑启动和反序释放；with 会启动/停止，生命周期回调中拒绝重入。 |

## 接入流程

```mermaid
flowchart LR
    N0["register"]
    N1["拓扑排序"]
    N0 --> N1
    N2["start"]
    N1 --> N2
    N3["get"]
    N2 --> N3
    N4["反序 stop"]
    N3 --> N4
```

## 调用步骤

| 步骤 | 操作 |
| --- | --- |
| 1 | register |
| 2 | 拓扑排序 |
| 3 | start |
| 4 | get |
| 5 | 反序 stop |

## 输入签名

### 构造入口

| 入口 | 输入签名 |
| --- | --- |
| `ServiceRegistry` | `ServiceRegistry()` |

### 方法

| 入口 | 输入签名 |
| --- | --- |
| `ServiceRegistry.register` | `ServiceRegistry.register(spec: ServiceSpec)` |
| `ServiceRegistry.start` | `ServiceRegistry.start()` |
| `ServiceRegistry.get` | `ServiceRegistry.get(name: str)` |
| `ServiceRegistry.stop` | `ServiceRegistry.stop()` |

签名只列输入，返回结果另表说明；类型标注不意味着每个参数都在运行时强制校验。

## 配置字段

### ServiceSpec 字段

| 字段 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `name` | `str` | 必填 | 非空且唯一的服务注册名。 |
| `factory` | `Callable[['ServiceRegistry'], Any]` | 必填 | factory(registry) 返回服务实例；未返回前的失败资源由工厂自行释放。 |
| `depends_on` | `tuple[str, ...]` | `()` | 已注册服务名 tuple，默认空；依赖不存在或有环会在创建实例前被拒绝。 |

冻结值对象禁止直接重新赋值字段；含映射或其他对象时，不代表内部对象被深度冻结。

## 配置参数与调用参数

### ServiceRegistry.register 输入参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `spec` | `ServiceSpec` | 必填 | 位置或关键字 | 对应的 PageSpec 或 ServiceSpec 配置；按声明类型使用。 |

### ServiceRegistry.get 输入参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `name` | `str` | 必填 | 位置或关键字 | 已启动并由注册表持有的服务名，不作惰性创建。 |

## 只读属性

| 只读属性 | 类型 | 读取语义 |
| --- | --- | --- |
| `ServiceRegistry.running` | `bool` | 只读地判断是否持有已启动服务，不检测服务线程或外部依赖是否健康。 |

## 返回值

| 接口 | 返回类型 | 返回结果 |
| --- | --- | --- |
| `ServiceRegistry.register` | `None` | None；没有业务返回值。对应操作与失败边界分别在接口说明和错误表中列明。 |
| `ServiceRegistry.start` | `None` | None；没有业务返回值。对应操作与失败边界分别在接口说明和错误表中列明。 |
| `ServiceRegistry.get` | `Any` | 当前已启动并持有的服务实例；不会创建新实例。 |
| `ServiceRegistry.stop` | `None` | None；没有业务返回值。对应操作与失败边界分别在接口说明和错误表中列明。 |

## 信号

本模块不新增 Qt 信号。同步调用结果见返回值表；应用注入回调的输入约定见参数表。

## 错误与边界

| 触发情况 | 错误或结果 | 调用方处理 |
| --- | --- | --- |
| 重复注册、缺依赖或依赖环 | ValueError；缺依赖或环由拓扑检查直接拒绝 | 启动前检查定义，查看原始 cause。 |
| 工厂或 start 失败 | ServiceStartError，尝试回滚 | 工厂内部失败先自行释放尚未返回的资源。 |
| stop 失败或生命周期重入 | RuntimeError | 清理仍会尝试全部实例；检查异常原因，不在 hook 中重入。 |

### 失败与边界

重复名称或运行后注册被拒绝；启动/停止回调中的生命周期重入被拒绝。启动失败抛 ServiceStartError；关闭会尝试全部服务，再从首个失败构造 RuntimeError。

工厂在返回实例前创建资源后抛错时，工厂必须自行清理；注册表只拥有已返回实例。它不提供跨线程同步或健康检查。

## 线程与资源

| 资源 | 拥有者 | 线程与释放要求 |
| --- | --- | --- |
| 已返回的服务实例 | ServiceRegistry | 同一拥有者线程 start/stop，反序清理；with 退出自动 stop。 |

start/stop 在同一拥有者线程调度；服务自己的 stop 必须等待工作线程和 socket 结束。关闭失败会释放注册表引用，但服务需报告未释放外部资源。

## 接口与接入

ServiceSpec 声明名称、工厂和依赖；ServiceRegistry 按拓扑顺序启动，按反序关闭。

先注册所有规范，再 start；工厂通过 registry.get 获取先前依赖；应用 finally 中 stop。缺失依赖和循环在创建实例前失败。

<span id="示例与验证" class="legacy-anchor" aria-hidden="true"></span>

## 最小调用示例

示例使用虚构数据和临时资源，不连接真实设备或业务存储。

```python
from ctf_desktop.services import ServiceRegistry, ServiceSpec
registry = ServiceRegistry()
registry.register(ServiceSpec("sample", lambda registry: object()))
try:
    registry.start()
    assert registry.running and registry.get("sample") is not None
finally:
    registry.stop()
```

## 验证与源码依据

实现依据：[services.py](../../src/ctf_desktop/services.py)；版本与依赖声明：[pyproject.toml](../../pyproject.toml)。

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
