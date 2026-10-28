---
title: "desktop.crud_page 公开契约"
category: "工程能力"
tags: ["type/api-contract", "desktop", "crud_page"]
summary: "crud_page 模块的公开输入输出、边界与副作用。"
created: 2026-10-20
updated: 2026-10-28
metadata_status: reviewed
home_area: theme
article_status: published
required_extra: qt
---

# desktop.crud_page

## 用途与范围

在 Qt 线程同步组合资料管理控件；通过 changed 和 operation_failed 信号把策略交给应用，模态对话框完成后安排删除。

导入模块为 `ctf_desktop.crud_page`，下列参数、返回值和资源条件均对应本页模块。

## 模块信息

| 标识项 | 本模块信息 |
| --- | --- |
| API 命名空间 | `desktop.crud_page` |
| Python 导入 | `ctf_desktop.crud_page` |
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
| 本模块接口与升级 | 0.2.0 的主键缺失通过 operation_failed 报告；写入后的列表刷新失败不能触发重复写入。仅适配 PyQt5。 |
| GUI 适配范围 | 当前使用 PyQt5，没有 PyQt6/PySide 适配承诺；目标系统真实窗口需应用验证。 |
| 验证边界 | 依赖下限不等于所有版本组合已验证；Python/Qt、目标系统与真实设备须按实际环境确认。 |

## 安装与导入

以下命令在本仓库根目录执行，使用当前源码安装，不假定 PyPI 已发布同名版本。

```bash
python -m pip install "./packages/python/desktop[qt]"
```

导入路径：`ctf_desktop.crud_page`。

## 调用前置条件

| 调用方责任 | 要求 |
| --- | --- |
| 控制器 | 先建立带明确授权回调的 CrudController。 |
| 字段配置 | 提供 identity_key、Column、FieldSpec 和可选 FilterField；记录必须包含主键。 |
| 响应性 | 仓储在 Qt 线程同步执行；慢查询需要应用另行安排异步加载。 |

## 调用签名与默认值

### 构造入口

| 入口 | 输入签名 |
| --- | --- |
| `CrudPage` | `CrudPage(controller: CrudController, *, identity_key: str, columns: Sequence[Column], fields: Sequence[FieldSpec], filters: Sequence[FilterField]=(), parent=None)` |

### 方法

| 入口 | 输入签名 |
| --- | --- |
| `CrudPage.load_page` | <code>CrudPage.load_page(request: PageRequest &#124; None=None)</code> |
| `CrudPage.create_record` | `CrudPage.create_record()` |
| `CrudPage.edit_selected` | `CrudPage.edit_selected()` |
| `CrudPage.show_detail` | `CrudPage.show_detail()` |
| `CrudPage.delete_selected` | `CrudPage.delete_selected()` |

签名只列输入，返回结果另表说明；类型标注不意味着每个参数都在运行时强制校验。

## 配置字段与只读属性

### 配置字段

本模块未声明单独的 dataclass 配置字段；构造参数列在下一节。
### 只读属性

本模块未额外声明 @property 只读访问器；值对象字段与调用参数分别在相应表中说明。

## 输入参数

### CrudPage 构造参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `controller` | `CrudController` | 必填 | 位置或关键字 | 已注入仓储和明确授权回调的 CrudController。 |
| `identity_key` | `str` | 必填 | 仅关键字 | 记录中的主键字段名；选中记录缺此字段通过 operation_failed 报告。 |
| `columns` | `Sequence[Column]` | 必填 | 仅关键字 | 用于列表显示的 Column 序列。 |
| `fields` | `Sequence[FieldSpec]` | 必填 | 仅关键字 | FieldSpec 配置序列；键应唯一且非空。 |
| `filters` | `Sequence[FilterField]` | `()` | 仅关键字 | FilterField 配置序列；默认空 tuple，不创建筛选字段。 |
| `parent` | 未标注 | `None` | 仅关键字 | Qt 父对象，默认 None；子控件/对象的所有权遵循 Qt 父子关系。 |

### CrudPage.load_page 输入参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `request` | <code>PageRequest &#124; None</code> | `None` | 位置或关键字 | 分页请求；CrudPage 的 None 表示沿用当前请求。 |

## 返回值

| 接口 | 返回类型 | 返回结果 |
| --- | --- | --- |
| `CrudPage.load_page` | `None` | None；没有业务返回值。对应操作与失败边界分别在接口说明和错误表中列明。 |
| `CrudPage.create_record` | `None` | None；没有业务返回值。对应操作与失败边界分别在接口说明和错误表中列明。 |
| `CrudPage.edit_selected` | `None` | None；没有业务返回值。对应操作与失败边界分别在接口说明和错误表中列明。 |
| `CrudPage.show_detail` | `None` | None；没有业务返回值。对应操作与失败边界分别在接口说明和错误表中列明。 |
| `CrudPage.delete_selected` | `None` | None；没有业务返回值。对应操作与失败边界分别在接口说明和错误表中列明。 |

## 信号

| 信号 | 载荷类型（按顺序） | 发出条件与含义 |
| --- | --- | --- |
| `CrudPage.changed` | `str, object` | 动作标识与记录主键；写入后通知，不能代替事务提交确认。 |
| `CrudPage.operation_failed` | `str, object` | 动作标识与异常对象；应用区分读写阶段并呈现错误。 |

## 错误与边界

| 触发情况 | 错误或结果 | 调用方处理 |
| --- | --- | --- |
| 缺失主键或控制器错误 | operation_failed(action, error) | 区分 list/read/create/update/delete 并展示错误。 |
| 用户取消表单或删除确认 | 不写入 | 保留当前业务数据。 |
| 写后刷新失败 | 错误信号；原写入不能据此撤销 | 核验写入结果后单独重试读取。 |

### 失败与边界

缺少身份会发失败信号而不让 KeyError 逃出 Qt 槽；取消不写入；控制器错误走 operation_failed；完成/取消的弹窗统一 deleteLater，不随重复操作累积。

当前为同步仓储；慢查询必须另行调度，不能在事件线程直接连接慢远端。页面无独立权限规则，控制器是强制入口。

## 线程与资源

| 资源 | 拥有者 | 线程与释放要求 |
| --- | --- | --- |
| 页面及子控件 | Qt 父对象/应用 | Qt 线程调用，页面退出时关闭；模态对话框由页面安排 deleteLater。 |

页面及仓储回调在 Qt 线程；页面关闭前释放仓储。写后刷新失败只说明刷新失败，不代表之前写入没有发生。

## 调用流程

```mermaid
flowchart LR
    N0["初始化字段"]
    N1["load_page"]
    N0 --> N1
    N2["用户操作"]
    N1 --> N2
    N3["控制器"]
    N2 --> N3
    N4["刷新"]
    N3 --> N4
```

## CrudPage

稳定标识：`desktop.crud_page.CrudPage`

在 Qt 线程同步组合资料管理控件；通过 changed 和 operation_failed 信号把策略交给应用，模态对话框完成后安排删除。

## CrudPage.load_page

稳定标识：`desktop.crud_page.CrudPage.load_page`

使用当前筛选和指定或当前 PageRequest 查询并展示；失败发出 operation_failed('list', error)。

## CrudPage.create_record

稳定标识：`desktop.crud_page.CrudPage.create_record`

打开编辑表单，仅接受后调用已授权的创建；成功通知并回到第一页，对话框在所有退出路径释放。

## CrudPage.edit_selected

稳定标识：`desktop.crud_page.CrudPage.edit_selected`

要求选中记录及主键；表单接受后更新并刷新，主键缺失或控制器失败发出操作失败信号，对话框始终释放。

## CrudPage.show_detail

稳定标识：`desktop.crud_page.CrudPage.show_detail`

按选中主键执行已授权查询并显示详情；记录已不存在时刷新，错误发出 read 失败信号，详情对话框始终释放。

## CrudPage.delete_selected

稳定标识：`desktop.crud_page.CrudPage.delete_selected`

要求选中主键并明确确认；取消不写入，成功删除后通知和刷新，主键或控制器错误通过信号报告。

## 最小调用示例

示例使用虚构数据和临时资源，不连接真实设备或业务存储。 需要先安装 qt 依赖；创建 QApplication 后再建立控件。

```python
from PyQt5.QtWidgets import QApplication
from ctf_desktop.crud import CrudController
from ctf_desktop.crud_page import CrudPage
from ctf_desktop.table import Column
from ctf_desktop.forms import FieldSpec
from ctf_desktop.query import PageResult
app = QApplication.instance() or QApplication([])
class Repository:
    def list_page(self, request, filters): return PageResult((), 0, request)
controller = CrudController(Repository(), authorize=lambda action, resource: None)
widget = CrudPage(controller, identity_key="id", columns=[Column("id", "ID")], fields=[FieldSpec("name", "Name")])
widget.load_page()
assert widget.table.model.rowCount() == 0
widget.close()
```

<span id="qt-信号" class="legacy-anchor" aria-hidden="true"></span>

## 验证与源码依据

实现依据：[crud_page.py](../../src/ctf_desktop/crud_page.py)；版本与依赖声明：[pyproject.toml](../../pyproject.toml)。

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
