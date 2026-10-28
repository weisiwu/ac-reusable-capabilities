---
title: "密码与访问控制使用指南"
category: "工程能力"
tags: ["desktop", "auth", "type/usage-guide"]
summary: "密码与访问控制的场景选择、接入步骤、错误处理、资源所有权与验证入口。"
created: 2026-10-20
updated: 2026-10-28
metadata_status: reviewed
home_area: theme
article_status: published
---

# 密码与访问控制

<span id="适用场景" class="legacy-anchor" aria-hidden="true"></span>

## 用途与范围

本地软件已有账号存储，但需要统一密码校验和显式权限决策。

实现 CredentialStore.find_by_username；记录必须有 id、password_hash，可选 roles。

## 模块信息

| 标识项 | 本模块信息 |
| --- | --- |
| API 命名空间 | `desktop.auth` |
| Python 导入 | `ctf_desktop.auth` |
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
| 本模块接口与升级 | 0.2.0 增加 max_verify_iterations，默认2000000；存量合法哈希超过上限时需显式评估策略，不能把验证失败直接当作密码错误迁移。盐为16字节、摘要32字节。 |
| 接入应用兼容 | 本模块不替代应用的业务数据、权限规则或外部依赖兼容检查。 |
| 验证边界 | 依赖下限不等于所有版本组合已验证；Python/Qt、目标系统与真实设备须按实际环境确认。 |

完整历史记录可继续查阅[架构与依赖](../架构与依赖.md)和[升级与兼容](../升级与兼容.md)；本模块当前要求已在本页说明。

## 安装与导入

以下命令在本仓库根目录执行，使用当前源码安装，不假定 PyPI 已发布同名版本。

```bash
python -m pip install "./packages/python/desktop"
```

导入路径：`ctf_desktop.auth`。

## 接入准备

| 应用需要提供 | 具体要求 |
| --- | --- |
| 凭据来源 | 实现 CredentialStore.find_by_username；记录必须有 id、password_hash，可选 roles。 |
| 权限规则 | 提供 allows(principal, action, resource)；写入前在服务入口调用 require。 |
| 策略配置 | 生成轮数与校验上限由应用选择；本模块不保存密码、不建立会话。 |

## 核心入口

| 入口 | 职责 |
| --- | --- |
| `CredentialStore` | 应用实现的凭据查询协议；记录包含 id、password_hash 和可选 roles，框架没有内置账户。 |
| `Principal` | 冻结的身份值对象，保存主体和角色集合；默认角色为空，不自行作权限决策。 |
| `PasswordHasher` | 使用 PBKDF2-SHA256 和每次新生成的 16 字节盐；默认 310000 轮，校验轮数上限默认 2000000，不保存账户或哈希。 |
| `AuthService` | 注入凭据存储与可选哈希器，负责验证并建立身份；没有注册、会话、锁定或限流。 |
| `AccessPolicy` | 接收应用的 allows(principal, action, resource) 判定函数；没有默认放行规则。 |

## 凭据记录字段

| 字段 | 要求 | 含义 |
| --- | --- | --- |
| `id` | 必填 | 认证成功后转成 Principal.subject。 |
| `password_hash` | 必填 | PasswordHasher 编码的哈希字符串，不是明文口令。 |
| `roles` | 可选 | 可为角色字符串或可迭代对象，缺省为空。 |

## 接入流程

```mermaid
flowchart LR
    N0["查账号"]
    N1["验证哈希"]
    N0 --> N1
    N2["返回 Principal"]
    N1 --> N2
    N3["服务入口授权"]
    N2 --> N3
```

## 调用步骤

| 步骤 | 操作 |
| --- | --- |
| 1 | 查账号 |
| 2 | 验证哈希 |
| 3 | 返回 Principal |
| 4 | 服务入口授权 |

## 输入签名

### 构造入口

| 入口 | 输入签名 |
| --- | --- |
| `PasswordHasher` | `PasswordHasher(iterations: int=310000, *, max_verify_iterations: int=2000000)` |
| `AuthService` | <code>AuthService(store: CredentialStore, hasher: PasswordHasher &#124; None=None)</code> |
| `AccessPolicy` | `AccessPolicy(allows: Callable[[Principal, str, object], bool])` |

### 方法

| 入口 | 输入签名 |
| --- | --- |
| `CredentialStore.find_by_username` | `CredentialStore.find_by_username(username: str)` |
| `PasswordHasher.hash` | `PasswordHasher.hash(password: str)` |
| `PasswordHasher.verify` | `PasswordHasher.verify(password: str, encoded: str)` |
| `PasswordHasher.needs_rehash` | `PasswordHasher.needs_rehash(encoded: str)` |
| `AuthService.authenticate` | `AuthService.authenticate(username: str, password: str)` |
| `AccessPolicy.require` | `AccessPolicy.require(principal: Principal, action: str, resource: object=None)` |

签名只列输入，返回结果另表说明；类型标注不意味着每个参数都在运行时强制校验。

## 配置字段

### Principal 字段

| 字段 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `subject` | `str` | 必填 | 主体标识字符串，仅描述身份，不执行授权。 |
| `roles` | `frozenset[str]` | 由 frozenset 为每个实例创建默认值 | 角色字符串的 frozenset，默认每个实例创建空集合。 |

冻结值对象禁止直接重新赋值字段；含映射或其他对象时，不代表内部对象被深度冻结。

## 配置参数与调用参数

### CredentialStore.find_by_username 输入参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `username` | `str` | 必填 | 位置或关键字 | 交给凭据存储查询的用户名；查找规则由应用定义。 |

### PasswordHasher 构造参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `iterations` | `int` | `310000` | 位置或关键字 | 生成新哈希的工作轮数，整数且不接受 bool；至少100000，不高于 max_verify_iterations。 |
| `max_verify_iterations` | `int` | `2000000` | 仅关键字 | 验证载荷允许的最大工作轮数，整数且不接受 bool；合法历史高轮数数据需先评估再显式放宽。 |

### PasswordHasher.hash 输入参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `password` | `str` | 必填 | 位置或关键字 | 待生成哈希或待验证的口令；hash 不接受空口令，不在日志中记录真实值。 |

### PasswordHasher.verify 输入参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `password` | `str` | 必填 | 位置或关键字 | 待生成哈希或待验证的口令；hash 不接受空口令，不在日志中记录真实值。 |
| `encoded` | `str` | 必填 | 位置或关键字 | 已保存的 PBKDF2 编码字符串；不在本函数内写回存储。 |

### PasswordHasher.needs_rehash 输入参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `encoded` | `str` | 必填 | 位置或关键字 | 已保存的 PBKDF2 编码字符串；不在本函数内写回存储。 |

### AuthService 构造参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `store` | `CredentialStore` | 必填 | 位置或关键字 | 实现 CredentialStore 的应用账号源，返回 id、password_hash 和可选 roles。 |
| `hasher` | <code>PasswordHasher &#124; None</code> | `None` | 位置或关键字 | PasswordHasher 实例；None 时创建使用默认策略的哈希器。 |

### AuthService.authenticate 输入参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `username` | `str` | 必填 | 位置或关键字 | 交给凭据存储查询的用户名；查找规则由应用定义。 |
| `password` | `str` | 必填 | 位置或关键字 | 待生成哈希或待验证的口令；hash 不接受空口令，不在日志中记录真实值。 |

### AccessPolicy 构造参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `allows` | `Callable[[Principal, str, object], bool]` | 必填 | 位置或关键字 | 应用授权谓词(principal, action, resource)；返回真允许，假值会被 require 转成 PermissionError。 |

### AccessPolicy.require 输入参数

| 参数 | 声明类型 | 默认值 | 传入方式 | 含义 |
| --- | --- | --- | --- | --- |
| `principal` | `Principal` | 必填 | 位置或关键字 | 已认证的 Principal，包含主体与角色；不是登录会话。 |
| `action` | `str` | 必填 | 位置或关键字 | 应用定义的动作标识；授权与审计应采用稳定且不含敏感信息的值。 |
| `resource` | `object` | `None` | 位置或关键字 | 应用提供的资源或资源标识，实际类型以接口声明为准。 |

## 只读属性

本模块未额外声明 @property 只读访问器；值对象字段与调用参数分别在相应表中说明。

## 可读运行状态

| 状态 | 类型 | 读取含义 |
| --- | --- | --- |
| `PasswordHasher.iterations` | `int` | 构造时确定的新哈希轮数；需要变更策略时宜新建并校验实例。 |
| `PasswordHasher.max_verify_iterations` | `int` | 构造时确定的载荷工作量上限；直接改写不会重新运行构造校验。 |

这些是可读取的实例状态；不把直接重新赋值当作受支持的更新接口。

## 返回值

| 接口 | 返回类型 | 返回结果 |
| --- | --- | --- |
| `CredentialStore.find_by_username` | <code>Mapping[str, object] &#124; None</code> | 命中时为包含账户凭据字段的映射；未命中为 None。 |
| `PasswordHasher.hash` | `str` | 新的 PBKDF2 编码字符串，包含算法、轮数、盐与摘要；不同调用使用新盐。 |
| `PasswordHasher.verify` | `bool` | 口令与合法载荷匹配时 True；格式、策略或口令不匹配时 False。 |
| `PasswordHasher.needs_rehash` | `bool` | 损坏、不支持或轮数低于配置时 True；符合当前工作策略时 False。 |
| `AuthService.authenticate` | <code>Principal &#124; None</code> | 成功时为 Principal；未知账号或口令不匹配时为 None。 |
| `AccessPolicy.require` | `None` | None；没有业务返回值。对应操作与失败边界分别在接口说明和错误表中列明。 |

## 信号

本模块不新增 Qt 信号。同步调用结果见返回值表；应用注入回调的输入约定见参数表。

## 错误与边界

| 触发情况 | 错误或结果 | 调用方处理 |
| --- | --- | --- |
| 轮数配置非法或生成哈希时口令为空 | `ValueError` | 轮数必须为满足策略的整数（不接受 bool），生成哈希时提供非空口令。 |
| 账号源缺失 id 或 roles 格式错误 | `KeyError` / `TypeError` 等原异常 | 修正账号源契约，不把存储结构错误伪装成密码错误。 |
| 未知账号或错误密码 | authenticate 返回 None | 向用户呈现认证失败，不伪造 Principal。 |
| 载荷格式或工作量不符合策略 | verify 返回 False；needs_rehash 返回 True | 区分损坏数据和合法高轮数数据，再安排迁移。 |
| 授权拒绝 | PermissionError | 在服务入口阻止操作，不能只隐藏按钮。 |

### 失败与边界

默认 310000 轮，最低 100000 轮；verify 默认上限 2000000，可通过 max_verify_iterations 显式放宽。畸形载荷、盐或摘要长度不符在计算前拒绝；needs_rehash 会识别损坏哈希。

没有注册、登录会话、锁定、限流或机器绑定。PBKDF2 格式不是数据加密。存量高于上限的合法哈希需先调整策略，再做有计划迁移。

## 线程与资源

| 资源 | 拥有者 | 线程与释放要求 |
| --- | --- | --- |
| 账号源 | 应用 | 连接、并发和错误由 CredentialStore 实现管理；框架不持久化。 |

不会读写账号文件或持有长期资源；CredentialStore 的连接、错误和并发由应用管理。

## 接口与接入

CredentialStore 由应用实现；AuthService 校验并返回 Principal；AccessPolicy 只执行应用传入的判定函数。

用 PasswordHasher 创建存储值；lookup 返回 id、password_hash、roles；服务写入入口必须调用 require，不能只隐藏界面按钮。

<span id="示例与验证" class="legacy-anchor" aria-hidden="true"></span>

## 最小调用示例

```python
from ctf_desktop.auth import PasswordHasher, AuthService, AccessPolicy

# 仅供演示的内存账户；真实应用实现自己的凭据存储。
hasher = PasswordHasher()
encoded = hasher.hash("example-only")
assert hasher.verify("example-only", encoded)
assert not hasher.needs_rehash(encoded)

class MemoryCredentials:
    def find_by_username(self, username):
        if username == "sample":
            return {"id": "sample-1", "password_hash": encoded, "roles": ["reader"]}
        return None

auth = AuthService(MemoryCredentials(), hasher)
principal = auth.authenticate("sample", "example-only")
assert principal is not None and principal.subject == "sample-1"
assert auth.authenticate("sample", "wrong-example") is None
policy = AccessPolicy(lambda actor, action, resource: action == "read" and "reader" in actor.roles)
policy.require(principal, "read", "sample-record")
try:
    policy.require(principal, "delete", "sample-record")
except PermissionError:
    pass
else:
    raise AssertionError("delete must be denied")
```

## 验证与源码依据

实现依据：[auth.py](../../src/ctf_desktop/auth.py)；版本与依赖声明：[pyproject.toml](../../pyproject.toml)。

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
