---
title: "资料管理协调使用指南"
category: "工程能力"
tags: ["desktop", "crud", "type/usage-guide"]
summary: "资料管理协调的场景选择、接入步骤、错误处理、资源所有权与验证入口。"
created: 2026-10-20
updated: 2026-10-28
metadata_status: reviewed
home_area: theme
article_status: published
---

# 资料管理协调

<span id="适用场景" class="legacy-anchor" aria-hidden="true"></span>

## 用途与范围

多个列表和编辑页面共享仓储操作、校验和权限检查。

实现 CrudRepository 的 list_page/get/create/update/delete，并定义主键、事务和不存在记录行为。

## 模块信息

| 标识项 | 本模块信息 |
| --- | --- |
| API 命名空间 | `desktop.crud` |
| Python 导入 | `ctf_desktop.crud` |
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
| 本模块接口与升级 | 框架不定义事务和业务 schema；写入已完成后通知失败不能当作写入失败重试。仓储或授权回调变化需要接入应用回归。 |
| 接入应用兼容 | 本模块不替代应用的业务数据、权限规则或外部依赖兼容检查。 |
| 验证边界 | 依赖下限不等于所有版本组合已验证；Python/Qt、目标系统与真实设备须按实际环境确认。 |

完整历史记录可继续查阅[架构与依赖](../架构与依赖.md)和[升级与兼容](../升级与兼容.md)；本模块当前要求已在本页说明。

## 安装与导入

以下命令在本仓库根目录执行，使用当前源码安装，不假定 PyPI 已发布同名版本。

```bash
python -m pip install "./packages/python/desktop"
```

导入路径：`ctf_desktop.crud`。

## 接入准备

| 应用需要提供 | 具体要求 |
| --- | --- |
| 仓储 | 实现 CrudRepository 的 list_page/get/create/update/delete，并定义主键、事务和不存在记录行为。 |
| 授权 | authorize(action, resource) 拒绝时必须抛错；仅返回 False 不会自动阻止仓储调用。 |
| 校验与通知 | validate 通过时正常返回、失败时抛错；changed 在写入后调用，不是事务提交机制。 |

## 核心入口

| 入口 | 职责 |
| --- | --- |
| `CrudRepository` | 应用实现的分页、取详情和写入协议；事务、主键及持久化错误由应用定义。 |
| `CrudController` | 注入仓储和必需的授权回调，可另注入校验及变更通知；不实现界面、存储或事务。 |

## 接入流程

```mermaid
flowchart LR
    N0["授权"]
    N1["校验"]
    N0 --> N1
    N2["仓储写入"]
    N1 --> N2
    N3["changed 通知"]
    N2 --> N3
```

## 调用步骤

| 步骤 | 操作 |
| --- | --- |
| 1 | 授权 |
| 2 | 校验 |
| 3 | 仓储写入 |
| 4 | changed 通知 |

## 输入签名

### 构造入口

| 入口 | 输入签名 |
| --- | --- |
| `CrudController` | <code>CrudController(repository: CrudRepository, *, authorize: Callable[[str, Any], None], validate: Callable[[Mapping[str, Any]], None] &#124; None=None, changed: Callable[[str, Any], None] &#124; None=None)</code> |

### 方法

| 入口 | 输入签名 |
| --- | --- |
| `CrudRepository.list_page` | `CrudRepository.list_page(request: PageRequest, filters: Mapping[str, Any])` |
| `CrudRepository.get` | `CrudRepository.get(identity: Any)` |
| `CrudRepository.create` | `CrudRepository.create(values: Mapping[str, Any])` |
| `CrudRepository.update` | `CrudRepository.update(identity: Any, values: Mapping[str, Any])` |
| `CrudRepository.delete` | `CrudRepository.delete(identity: Any)` |
| `CrudController.list_page` | <code>CrudController.list_page(request: PageRequest, filters: Mapping[str, Any] &#124; None=None)</code> |
| `CrudController.detail` | `CrudController.detail(identity: Any)` |
| `CrudController.create` | `CrudController.create(values: Mapping[str, Any])` |
| `CrudController.update` | `CrudController.update(identity: Any, values: Mapping[str, Any])` |
| `CrudController.delete` | `CrudController.delete(identity: Any)` |

签名只列输入，返回结果另表说明；类型标注不意味着每个参数都在运行时强制校验。

## 配置字段

本模块未声明单独的 dataclass 配置字段；构造参数列在下一节。

## 配置参数与调用参数

### CrudRepository.list_page 输入参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `request` | `PageRequest` | 必填 | 位置或关键字 | 分页请求；CrudPage 的 None 表示沿用当前请求。 |
| `filters` | `Mapping[str, Any]` | 必填 | 位置或关键字 | 筛选映射或筛选字段序列，按本接口声明类型传入；控制器的 None 筛选按空映射处理。 |

### CrudRepository.get 输入参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `identity` | `Any` | 必填 | 位置或关键字 | 应用仓储使用的主键；存在性与具体类型由仓储定义。 |

### CrudRepository.create 输入参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `values` | `Mapping[str, Any]` | 必填 | 位置或关键字 | 本接口声明的值映射；校验、写入与显示按所在接口约定执行。 |

### CrudRepository.update 输入参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `identity` | `Any` | 必填 | 位置或关键字 | 应用仓储使用的主键；存在性与具体类型由仓储定义。 |
| `values` | `Mapping[str, Any]` | 必填 | 位置或关键字 | 本接口声明的值映射；校验、写入与显示按所在接口约定执行。 |

### CrudRepository.delete 输入参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `identity` | `Any` | 必填 | 位置或关键字 | 应用仓储使用的主键；存在性与具体类型由仓储定义。 |

### CrudController 构造参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `repository` | `CrudRepository` | 必填 | 位置或关键字 | 应用实现的 CrudRepository，负责事务、主键和持久化。 |
| `authorize` | `Callable[[str, Any], None]` | 必填 | 仅关键字 | authorize(action, resource)；拒绝必须抛错，仅返回 False 不会阻止操作。 |
| `validate` | <code>Callable[[Mapping[str, Any]], None] &#124; None</code> | `None` | 仅关键字 | validate(values) 失败时抛错；仅返回文字或 False 不会自动阻止写入。 |
| `changed` | <code>Callable[[str, Any], None] &#124; None</code> | `None` | 仅关键字 | changed(action, identity) 同步通知；在仓储写入之后调用，通知失败不会回滚已写入数据。 |

### CrudController.list_page 输入参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `request` | `PageRequest` | 必填 | 位置或关键字 | 分页请求；CrudPage 的 None 表示沿用当前请求。 |
| `filters` | <code>Mapping[str, Any] &#124; None</code> | `None` | 位置或关键字 | 筛选映射或筛选字段序列，按本接口声明类型传入；控制器的 None 筛选按空映射处理。 |

### CrudController.detail 输入参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `identity` | `Any` | 必填 | 位置或关键字 | 应用仓储使用的主键；存在性与具体类型由仓储定义。 |

### CrudController.create 输入参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `values` | `Mapping[str, Any]` | 必填 | 位置或关键字 | 本接口声明的值映射；校验、写入与显示按所在接口约定执行。 |

### CrudController.update 输入参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `identity` | `Any` | 必填 | 位置或关键字 | 应用仓储使用的主键；存在性与具体类型由仓储定义。 |
| `values` | `Mapping[str, Any]` | 必填 | 位置或关键字 | 本接口声明的值映射；校验、写入与显示按所在接口约定执行。 |

### CrudController.delete 输入参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `identity` | `Any` | 必填 | 位置或关键字 | 应用仓储使用的主键；存在性与具体类型由仓储定义。 |

## 只读属性

本模块未额外声明 @property 只读访问器；值对象字段与调用参数分别在相应表中说明。

## 返回值

| 接口 | 返回类型 | 返回结果 |
| --- | --- | --- |
| `CrudRepository.list_page` | `PageResult` | 仓储提供的 PageResult，包含 items、total 与对应 request。 |
| `CrudRepository.get` | <code>Mapping[str, Any] &#124; None</code> | 命中时为记录映射；未命中为 None。 |
| `CrudRepository.create` | `Any` | 新记录的应用主键，类型由仓储决定。 |
| `CrudRepository.update` | `None` | None；没有业务返回值。对应操作与失败边界分别在接口说明和错误表中列明。 |
| `CrudRepository.delete` | `None` | None；没有业务返回值。对应操作与失败边界分别在接口说明和错误表中列明。 |
| `CrudController.list_page` | `PageResult` | 授权后由仓储返回的 PageResult。 |
| `CrudController.detail` | <code>Mapping[str, Any] &#124; None</code> | 命中时为已授权的记录映射；未命中为 None。 |
| `CrudController.create` | `Any` | 仓储返回的新记录主键。 |
| `CrudController.update` | `None` | None；没有业务返回值。对应操作与失败边界分别在接口说明和错误表中列明。 |
| `CrudController.delete` | `None` | None；没有业务返回值。对应操作与失败边界分别在接口说明和错误表中列明。 |

## 信号

本模块不新增 Qt 信号。同步调用结果见返回值表；应用注入回调的输入约定见参数表。

## 错误与边界

| 触发情况 | 错误或结果 | 调用方处理 |
| --- | --- | --- |
| 授权、校验或仓储失败 | 原异常上抛 | 明确出错阶段并保持应用事务语义。 |
| 写后 changed 失败 | 异常上抛但写入可能已完成 | 先查证业务状态，不能盲目重试写入。 |

### 失败与边界

拒绝授权和校验失败发生在仓储写入前。仓储错误原样上抛。changed 在写后运行；其异常不能撤销已成功的写入，调用方不能据此盲目重试 create。

控制器不是事务管理器。远程写入、通知投递或重复请求需要应用自己的幂等键与事务设计。

## 线程与资源

| 资源 | 拥有者 | 线程与释放要求 |
| --- | --- | --- |
| 仓储/事务 | 应用 | 控制器同步调用，不建立连接、不自动提交或回滚。 |

同步调用，不创建线程；不要在 GUI 线程执行慢仓储。通知函数应短、可重入且不抛错，资源归仓储所有。

## 接口与接入

CrudRepository 定义 list/get/create/update/delete；CrudController 负责授权、校验、写入与变更通知顺序。

仓储自定义事务与主键；构造时必须显式传 authorize；create/update 可插入 validate；changed 用于通知缓存或视图。

<span id="示例与验证" class="legacy-anchor" aria-hidden="true"></span>

## 最小调用示例

```python
from ctf_desktop.crud import CrudController
from ctf_desktop.query import PageRequest, PageResult

class MemoryRepository:
    def __init__(self):
        self.rows = {}
        self.next_id = 1
    def list_page(self, request, filters):
        rows = tuple(self.rows.values())
        return PageResult(rows[request.offset:request.offset + request.size], len(rows), request)
    def get(self, identity):
        return self.rows.get(identity)
    def create(self, values):
        identity = self.next_id
        self.next_id += 1
        self.rows[identity] = {**values, "id": identity}
        return identity
    def update(self, identity, values):
        self.rows[identity] = {**values, "id": identity}
    def delete(self, identity):
        del self.rows[identity]

# 仅此演示显式放行；真实应用在 authorize 中拒绝未授权动作。
controller = CrudController(MemoryRepository(), authorize=lambda action, resource: None)
identity = controller.create({"name": "sample"})
assert controller.detail(identity)["name"] == "sample"
controller.update(identity, {"name": "updated"})
assert controller.list_page(PageRequest()).total == 1
assert controller.detail(identity)["name"] == "updated"
controller.delete(identity)
assert controller.list_page(PageRequest()).total == 0
```

## 验证与源码依据

实现依据：[crud.py](../../src/ctf_desktop/crud.py)；版本与依赖声明：[pyproject.toml](../../pyproject.toml)。

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
