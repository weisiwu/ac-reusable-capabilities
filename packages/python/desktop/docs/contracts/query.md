---
title: "desktop.query 公开契约"
category: "工程能力"
tags: ["type/api-contract", "desktop", "query"]
summary: "query 模块的公开输入输出、边界与副作用。"
created: 2026-10-20
updated: 2026-10-28
metadata_status: reviewed
home_area: theme
article_status: published
---

# desktop.query

## 用途与范围

冻结的页号和页大小，默认1和20；必须为正整数且不接受 bool，否则抛 ValueError，不进行 IO。

导入模块为 `ctf_desktop.query`，下列参数、返回值和资源条件均对应本页模块。

## 模块信息

| 标识项 | 本模块信息 |
| --- | --- |
| API 命名空间 | `desktop.query` |
| Python 导入 | `ctf_desktop.query` |
| 所属发行包 | `common-tech-framework-desktop` |
| 包导入名 | `ctf_desktop` |

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
| 本模块接口与升级 | 使用 SQLite 风格问号占位符；不是通用数据库方言适配器。区间上界排除，范围空值也会核对字段白名单。 |
| 接入应用兼容 | 本模块不替代应用的业务数据、权限规则或外部依赖兼容检查。 |
| 验证边界 | 依赖下限不等于所有版本组合已验证；Python/Qt、目标系统与真实设备须按实际环境确认。 |

## 安装与导入

以下命令在本仓库根目录执行，使用当前源码安装，不假定 PyPI 已发布同名版本。

```bash
python -m pip install "./packages/python/desktop"
```

导入路径：`ctf_desktop.query`。

## 调用前置条件

| 调用方责任 | 要求 |
| --- | --- |
| 字段白名单 | SqlWhere 接收可信 SQL 列表达式映射，用户输入只能作为绑定值。 |
| 分页数据 | 仓储用同一筛选条件计算 items 与 total；PageResult 不替应用检查业务一致性。 |
| 执行连接 | 应用持有数据库连接并执行 SQL；本模块只生成数据对象与条件。 |

## 调用签名与默认值

### 构造入口

| 入口 | 输入签名 |
| --- | --- |
| `SqlWhere` | `SqlWhere(columns: Mapping[str, str])` |

### 方法

| 入口 | 输入签名 |
| --- | --- |
| `SqlWhere.equal` | `SqlWhere.equal(field: str, value: Any)` |
| `SqlWhere.contains` | `SqlWhere.contains(field: str, value: str)` |
| `SqlWhere.range` | `SqlWhere.range(field: str, start: Any=None, end: Any=None)` |
| `SqlWhere.build` | `SqlWhere.build()` |

签名只列输入，返回结果另表说明；类型标注不意味着每个参数都在运行时强制校验。

## 配置字段与只读属性

### 配置字段

### PageRequest 字段

| 字段 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `number` | `int` | `1` | 从1开始的页号，正整数且不接受 bool。 |
| `size` | `int` | `20` | 正整数页大小，默认20，不接受 bool。 |

### PageResult 字段

| 字段 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `items` | `tuple[Any, ...]` | 必填 | 当前页结果 tuple；对应 request 和 total。 |
| `total` | `int` | 必填 | 总数；PageResult 的 total 是匹配记录数，打印结果 total 是计划提交份数。 |
| `request` | `PageRequest` | 必填 | 分页请求；CrudPage 的 None 表示沿用当前请求。 |

冻结值对象禁止直接重新赋值字段；含映射或其他对象时，不代表内部对象被深度冻结。
### 只读属性

| 只读属性 | 类型 | 读取语义 |
| --- | --- | --- |
| `PageRequest.offset` | `int` | 只读的零基偏移量(number - 1) * size，不改变状态。 |
| `PageResult.pages` | `int` | 只读总页数，按 total/size 向上取整，空结果也至少1页。 |

## 输入参数

### SqlWhere 构造参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `columns` | `Mapping[str, str]` | 必填 | 位置或关键字 | 逻辑字段到可信 SQL 列表达式的映射；输入值通过绑定参数传入。 |

### SqlWhere.equal 输入参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `field` | `str` | 必填 | 位置或关键字 | 白名单中的逻辑字段键，不可直接传用户提供的 SQL 表达式。 |
| `value` | `Any` | 必填 | 位置或关键字 | 等值绑定值；None 与空文字被跳过，不拼接到 SQL。 |

### SqlWhere.contains 输入参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `field` | `str` | 必填 | 位置或关键字 | 白名单中的逻辑字段键，不可直接传用户提供的 SQL 表达式。 |
| `value` | `str` | 必填 | 位置或关键字 | 文字包含条件；空文字跳过，百分号/下划线/反斜杠按字面转义。 |

### SqlWhere.range 输入参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `field` | `str` | 必填 | 位置或关键字 | 白名单中的逻辑字段键，不可直接传用户提供的 SQL 表达式。 |
| `start` | `Any` | `None` | 位置或关键字 | 范围下界，非 None 时包含该边界。 |
| `end` | `Any` | `None` | 位置或关键字 | 范围上界，非 None 时排除该边界。 |

## 返回值

| 接口 | 返回类型 | 返回结果 |
| --- | --- | --- |
| `SqlWhere.equal` | `'SqlWhere'` | 当前 SqlWhere 自身，可继续累积其他条件。 |
| `SqlWhere.contains` | `'SqlWhere'` | 当前 SqlWhere 自身，可继续累积其他条件。 |
| `SqlWhere.range` | `'SqlWhere'` | 当前 SqlWhere 自身，可继续累积其他条件。 |
| `SqlWhere.build` | `tuple[str, tuple[Any, ...]]` | (WHERE文字, 绑定值tuple)；没有条件时为("", ())，与内部累积状态分离。 |

## 信号

本模块不新增 Qt 信号。同步调用结果见返回值表；应用注入回调的输入约定见参数表。

## 错误与边界

| 触发情况 | 错误或结果 | 调用方处理 |
| --- | --- | --- |
| 非法页号、页大小或 total | ValueError | 拒绝 bool/非整数及非法范围。 |
| 未知筛选字段 | ValueError | 维护可信字段白名单。 |
| items、total 与页码业务不一致 | 不自动修正 | 仓储使用一致查询条件计算结果。 |

### 失败与边界

页码、页大小必须是正整数，空数据仍显示一页。range 结束值不包含在区间内；日期仅传字符串时调用方将含当天的结束日换算成下一天。contains 把百分号、下划线和反斜线作为字面量。

不能把用户输入当列表达式。工具不执行 SQL、不验证整条查询，也不提供跨数据库 placeholder 适配。

## 线程与资源

| 资源 | 拥有者 | 线程与释放要求 |
| --- | --- | --- |
| 分页/条件对象 | 调用方局部变量 | 不持有连接、文件或线程，无 close；数据库 IO 在仓储侧。 |

无连接或线程所有权；builder 具有可变累积状态，不跨请求共享。PageResult 和记录仅按约定浅层使用，不是深度不可变业务快照。

## 调用流程

```mermaid
flowchart LR
    N0["验证分页"]
    N1["白名单条件"]
    N0 --> N1
    N2["build"]
    N1 --> N2
    N3["仓储执行"]
    N2 --> N3
    N4["返回页结果"]
    N3 --> N4
```

## PageRequest

稳定标识：`desktop.query.PageRequest`

冻结的页号和页大小，默认1和20；必须为正整数且不接受 bool，否则抛 ValueError，不进行 IO。

## PageRequest.offset

稳定标识：`desktop.query.PageRequest.offset`

只读的零基偏移量(number - 1) * size，不改变状态。

## PageResult

稳定标识：`desktop.query.PageResult`

冻结的结果条目、非负整数总数和分页请求；非法 total 被拒绝，不查询数据。

## PageResult.pages

稳定标识：`desktop.query.PageResult.pages`

只读总页数，按 total/size 向上取整，空结果也至少1页。

## SqlWhere

稳定标识：`desktop.query.SqlWhere`

复制应用可信的列白名单，累积 SQLite 问号占位符及绑定值；不执行 SQL。

## SqlWhere.equal

稳定标识：`desktop.query.SqlWhere.equal`

忽略 None 或空文字，否则先校验字段白名单，再追加等值条件并返回自身；未知字段抛 ValueError。

## SqlWhere.contains

稳定标识：`desktop.query.SqlWhere.contains`

忽略空文字，先校验字段，再转义百分号、下划线和反斜杠，追加 LIKE 条件并返回自身。

## SqlWhere.range

稳定标识：`desktop.query.SqlWhere.range`

即使起止皆空也校验字段；非 None 的下界包含、上界排除，追加条件后返回自身。

## SqlWhere.build

稳定标识：`desktop.query.SqlWhere.build`

返回独立的 WHERE 文字与绑定参数 tuple；空构造器返回空文字和空 tuple，重复调用不改变状态。

## 最小调用示例

示例使用虚构数据和临时资源，不连接真实设备或业务存储。

```python
from ctf_desktop.query import PageRequest, PageResult, SqlWhere
request = PageRequest(2, 10)
assert request.offset == 10
assert PageResult((), 0, request).pages == 1
assert SqlWhere({"name": "name"}).equal("name", "example").build() == ("WHERE name = ?", ("example",))
```

## 验证与源码依据

实现依据：[query.py](../../src/ctf_desktop/query.py)；版本与依赖声明：[pyproject.toml](../../pyproject.toml)。

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
