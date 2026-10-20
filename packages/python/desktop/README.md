# Desktop 可复用基础能力包

安装保留 `ctf_desktop` 导入路径。本目录是独立可安装包，仓库根目录不作为 Python 包安装。无界面模块只依赖标准库；Qt 和 pyserial 按需安装。

```bash
python -m pip install './packages/python/desktop[test]'
python -m pytest -q packages/python/desktop/tests/test_core.py packages/python/desktop/tests/test_contracts.py
python packages/python/desktop/examples/desktop_demo.py

python -m pip install './packages/python/desktop[all]'
QT_QPA_PLATFORM=offscreen python -m pytest -q packages/python/desktop/tests
QT_QPA_PLATFORM=offscreen python packages/python/desktop/examples/desktop_demo.py --qt
```

[能力目录](docs/能力目录.md) · [来源与迁入边界](docs/来源与迁入边界.md) · [验证记录](docs/验证记录.md)

以下保留模块接入说明。已收录的是基础接口与组件，不能据此认定后续项目增强能力已迁入。

## 模块接入

面向 Python 3.11 与 PyQt5 桌面应用的可组合基础能力。仓库只提供通用机制；字段、权限规则、报表模板、设备协议、数据库表结构和发布配置由接入项目提供。

## 安装

```bash
python -m pip install -e '.[qt,serial]'
```

仅使用查询、账号、服务、存储、打印调度等无界面模块时，可以只安装基础包。需要窗口组件时安装 `qt`，需要真实串口时安装 `serial`。测试使用 `python -m pip install -e '.[all]'`，无显示器环境设置 `QT_QPA_PLATFORM=offscreen`。

## 能力与模块

| 能力 | 模块 | 已实现的边界 |
| --- | --- | --- |
| 数据表格体系 | `table`, `query` | 列映射、记录模型、选中记录、服务端分页协议 |
| 配置驱动表单与详情 | `forms` | 字段描述、基础校验、编辑弹窗和只读详情 |
| 筛选与联想输入 | `filters` | 筛选条件采集、日期区间、延迟查询和过期结果丢弃 |
| 基础交互组件 | `feedback` | 确认框、空状态、忙碌遮罩和短时提示 |
| 主窗口与页面导航 | `navigation` | 页面注册、懒加载、进入/离开回调、销毁 |
| 异步与批量打印 | `printing` | 后台准备、逐份提交、取消、失败即停、结果统计 |
| 账号与数据访问控制 | `auth` | PBKDF2 密码校验、主体、注入式访问策略 |
| 通用资料管理页面 | `crud`, `crud_page` | 注入仓储后的列表、详情、新增、编辑、删除 |
| 通信抽象与串口适配 | `transport` | 传输协议、串口参数、异常归一化 |
| 服务生命周期 | `services` | 依赖拓扑、启动、反序关闭、启动失败回滚 |
| 本地数据保障 | `storage` | SQLite 迁移、一致性备份、校验后恢复 |
| 查询工具 | `query` | 分页参数、白名单字段、绑定参数谓词 |
| 桌面应用运行底座 | `runtime` | 用户数据目录、配置校验、Qt 单实例锁 |
| 诊断与审计 | `diagnostics` | JSON 日志、结构化字段脱敏、追加式审计记录 |

## 最小接入

仓储、权限、校验与字段由应用侧注入。下面的示例展示无界面部分的组合方式：

```python
from ctf_desktop.auth import AccessPolicy, Principal
from ctf_desktop.crud import CrudController
from ctf_desktop.query import PageRequest

principal = Principal(subject="local-user", roles=frozenset({"editor"}))
policy = AccessPolicy(lambda actor, action, resource: "editor" in actor.roles)
controller = CrudController(
    repository,
    authorize=lambda action, resource: policy.require(principal, action, resource),
)
page = controller.list_page(PageRequest(number=1, size=20), {"keyword": "example"})
```

其中 `repository` 是接入项目实现的 `CrudRepository`。SQL 查询必须由接入项目使用可信字段白名单构造；`SqlWhere` 只返回谓词与绑定值，不执行 SQL。界面组合可使用 `CrudPage`，但仓储调用发生在 Qt 事件线程；大数据量或慢 IO 时应在接入层安排异步加载。

## 必须由接入方决定的行为

- `BatchPrintRunner.start()` 在工作线程执行准备和提交。Qt 打印 API 需要主线程时，通过 `dispatch_submit` 同步派发到 GUI 线程。提交结果不确定时框架停止，不自动重试，避免重复出纸。
- `AccessPolicy` 只执行接入方传入的判定函数；`CrudController` 要求显式传入授权回调。界面隐藏按钮不构成数据访问控制，服务和仓储边界仍需检查。
- `SqliteStore.restore()` 在恢复前生成回滚快照并返回路径。调用方应停止写入、关闭其他连接，验证业务数据后决定何时清理快照。
- `JsonFormatter` 脱敏 `record.data` 的结构化键值；自由文本日志消息可能包含敏感内容，调用方需避免写入或先行清理。审计事件的 `actor`、`action`、`resource` 应使用非敏感标识。
- 组件提供可组合的基础实现，不承诺继承任何源项目的全部外观与业务行为。接入方应在自身界面、设备和打印环境中验收。

## 验证

```bash
QT_QPA_PLATFORM=offscreen python -m pytest -q
```

当前测试覆盖分页与查询参数、账号校验与授权、服务回滚、批量打印取消和失败边界、SQLite 备份恢复、以及主要 Qt 组件的基础交互。实际打印机、串口设备和目标平台安装包需要接入项目验证。

## 目录

- `src/ctf_desktop/`：可安装的框架代码。
- `tests/`：核心与 Qt 离屏测试。
- `docs/`：接入说明和模块对应关系。
