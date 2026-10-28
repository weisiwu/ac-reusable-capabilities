---
title: "desktop.filters 公开契约"
category: "工程能力"
tags: ["type/api-contract", "desktop", "filters"]
summary: "filters 模块的公开输入输出、边界与副作用。"
created: 2026-10-20
updated: 2026-10-28
metadata_status: reviewed
home_area: theme
article_status: published
required_extra: qt
---

# desktop.filters

## 用途与范围

冻结的筛选字段配置，kind 默认 text；支持 text、choice、date_range，非法种类抛 ValueError。

导入模块为 `ctf_desktop.filters`，下列参数、返回值和资源条件均对应本页模块。

## 模块信息

| 标识项 | 本模块信息 |
| --- | --- |
| API 命名空间 | `desktop.filters` |
| Python 导入 | `ctf_desktop.filters` |
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
| 本模块接口与升级 | 保留 search_requested(query) 与无 request_id 的调用；它们仅按文字匹配，不能保证相同文字的代次隔离。 |
| GUI 适配范围 | 当前使用 PyQt5，没有 PyQt6/PySide 适配承诺；目标系统真实窗口需应用验证。 |
| 验证边界 | 依赖下限不等于所有版本组合已验证；Python/Qt、目标系统与真实设备须按实际环境确认。 |

## 安装与导入

以下命令在本仓库根目录执行，使用当前源码安装，不假定 PyPI 已发布同名版本。

```bash
python -m pip install "./packages/python/desktop[qt]"
```

导入路径：`ctf_desktop.filters`。

## 调用前置条件

| 调用方责任 | 要求 |
| --- | --- |
| 筛选字段 | 提供唯一、非空的 FilterField.key；组合日期的先后关系由应用检查。 |
| 数据提供者 | 接收查询信号，自行查询；结果必须是(value, text)对。 |
| 代次绑定 | 保存 request_started 的 ID，并传给 set_results(request_id=...)，避免相同文字的旧响应覆盖。 |

## 调用签名与默认值

### 构造入口

| 入口 | 输入签名 |
| --- | --- |
| `FilterPanel` | `FilterPanel(fields: Sequence[FilterField], parent=None)` |
| `LiveSearchComboBox` | `LiveSearchComboBox(delay_ms: int=200, parent=None)` |

### 方法

| 入口 | 输入签名 |
| --- | --- |
| `FilterPanel.values` | `FilterPanel.values()` |
| `FilterPanel.clear` | `FilterPanel.clear()` |
| `LiveSearchComboBox.set_results` | <code>LiveSearchComboBox.set_results(query: str, results: Sequence[tuple[Any, str]], *, request_id: int &#124; None=None)</code> |

签名只列输入，返回结果另表说明；类型标注不意味着每个参数都在运行时强制校验。

## 配置字段与只读属性

### 配置字段

### FilterField 字段

| 字段 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `key` | `str` | 必填 | 筛选字段键；FilterPanel 要求非空且唯一。 |
| `label` | `str` | 必填 | 应用提供的字段标签文字。 |
| `kind` | `str` | `'text'` | 控件种类：text、choice、date_range。 |
| `choices` | `tuple[tuple[Any, str], ...]` | `()` | (value, label)选项 tuple；显示 label，读取时返回 value。 |

冻结值对象禁止直接重新赋值字段；含映射或其他对象时，不代表内部对象被深度冻结。
### 只读属性

本模块未额外声明 @property 只读访问器；值对象字段与调用参数分别在相应表中说明。

## 输入参数

### FilterPanel 构造参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `fields` | `Sequence[FilterField]` | 必填 | 位置或关键字 | FilterField 配置序列；键应唯一且非空。 |
| `parent` | 未标注 | `None` | 位置或关键字 | Qt 父对象，默认 None；子控件/对象的所有权遵循 Qt 父子关系。 |

### LiveSearchComboBox 构造参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `delay_ms` | `int` | `200` | 位置或关键字 | 联想输入的防抖毫秒间隔，默认200，由 Qt 计时器调度。 |
| `parent` | 未标注 | `None` | 位置或关键字 | Qt 父对象，默认 None；子控件/对象的所有权遵循 Qt 父子关系。 |

### LiveSearchComboBox.set_results 输入参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `query` | `str` | 必填 | 位置或关键字 | 该次请求的查询文字；结果交付时仍需与控件当前文字匹配。 |
| `results` | `Sequence[tuple[Any, str]]` | 必填 | 位置或关键字 | (value, text)候选序列；先整体校验再替换已有选项。 |
| `request_id` | <code>int &#124; None</code> | `None` | 仅关键字 | request_started 产生的代次 ID；None 只比较文字，不能隔离同文字的不同请求。 |

## 返回值

| 接口 | 返回类型 | 返回结果 |
| --- | --- | --- |
| `FilterPanel.values` | `dict[str, Any]` | 非空筛选值的新字典；文字去空白、选项取 data、日期取 ISO 范围。 |
| `FilterPanel.clear` | `None` | None；没有业务返回值。对应操作与失败边界分别在接口说明和错误表中列明。 |
| `LiveSearchComboBox.set_results` | `bool` | 成功替换候选为 True；文字或请求 ID 已过期为 False。 |

## 信号

| 信号 | 载荷类型（按顺序） | 发出条件与含义 |
| --- | --- | --- |
| `FilterPanel.search_requested` | `dict` | 筛选条件字典，应用自行查询。 |
| `FilterPanel.reset_requested` | 无参数 | 无参数；筛选字段已重置，应用自行决定是否重新读取数据。 |
| `LiveSearchComboBox.search_requested` | `str` | 查询文字；兼容旧信号，没有请求代次保证。 |
| `LiveSearchComboBox.request_started` | `int, str` | 递增请求 ID 与查询文字；结果必须保留并传回该 ID。 |

## 错误与边界

| 触发情况 | 错误或结果 | 调用方处理 |
| --- | --- | --- |
| 字段配置或结果对非法 | ValueError 等配置错误 | 先校验字段/结果，非法结果不替换已有选项。 |
| 过期文字或请求 ID | set_results 返回 False | 丢弃旧结果，不更新当前选择。 |
| 日期范围业务冲突 | 由应用判断 | 检查起止和业务范围再查询。 |

### 失败与边界

过期文字结果返回 false；格式不对抛 ValueError 且保持旧选项；更新选项恢复原信号屏蔽状态。日期 1900-01-01 为不限哨兵，结束日期转换由应用负责。

完整异步接入可监听 request_started(request_id,query)，并把 ID 传给 set_results；BackgroundTaskRunner 提供有界 latest-wins 任务、取消和超时。日期先后关系由应用校验。

## 线程与资源

| 资源 | 拥有者 | 线程与释放要求 |
| --- | --- | --- |
| 控件与防抖计时器 | Qt 父对象 | Qt 线程使用并随父对象释放；外部查询自行取消/关闭。 |

GUI 线程操作控件；查询 IO 在应用层调度并用信号回传；防抖计时器由控件拥有。

## 调用流程

```mermaid
flowchart LR
    N0["输入"]
    N1["防抖"]
    N0 --> N1
    N2["request_started"]
    N1 --> N2
    N3["查询"]
    N2 --> N3
    N4["set_results"]
    N3 --> N4
```

## FilterField

稳定标识：`desktop.filters.FilterField`

冻结的筛选字段配置，kind 默认 text；支持 text、choice、date_range，非法种类抛 ValueError。

## FilterPanel

稳定标识：`desktop.filters.FilterPanel`

在 Qt 线程采集筛选条件，要求字段键唯一且非空；发出查询和重置信号，不持久化或执行 SQL。

## FilterPanel.values

稳定标识：`desktop.filters.FilterPanel.values`

返回非空条件字典；文字去两端空白，选项返回 data，日期范围返回 ISO 起止值或 None，1900-01-01 作为未设置标记。

## FilterPanel.clear

稳定标识：`desktop.filters.FilterPanel.clear`

重置文字、选项和日期控件并发出 reset_requested；可以重复调用，不启动 IO。

## LiveSearchComboBox

稳定标识：`desktop.filters.LiveSearchComboBox`

可编辑 Qt 联想框，编辑后防抖并发出带代次 ID 的 request_started，同时保留旧 search_requested；结果应携带 request_id 防止相同文字的旧代次覆盖。

## LiveSearchComboBox.set_results

稳定标识：`desktop.filters.LiveSearchComboBox.set_results`

查询文字或可选请求 ID 已过期时返回 False；先校验所有(value, text)结果再整体替换，保留既有信号阻塞状态，成功返回 True；省略 ID 仅比较文字。

## 最小调用示例

示例使用虚构数据和临时资源，不连接真实设备或业务存储。 需要先安装 qt 依赖；创建 QApplication 后再建立控件。

```python
from PyQt5.QtWidgets import QApplication
from ctf_desktop.filters import FilterField, FilterPanel
app = QApplication.instance() or QApplication([])
widget = FilterPanel([FilterField("name", "Name")])
assert widget.values() == {}
widget.clear()
widget.close()
```

<span id="qt-信号" class="legacy-anchor" aria-hidden="true"></span>

## 验证与源码依据

实现依据：[filters.py](../../src/ctf_desktop/filters.py)；版本与依赖声明：[pyproject.toml](../../pyproject.toml)。

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
