---
title: "desktop.storage 公开契约"
category: "工程能力"
tags: ["type/api-contract", "desktop", "storage"]
summary: "storage 模块的公开输入输出、边界与副作用。"
created: 2026-10-20
updated: 2026-10-28
metadata_status: reviewed
home_area: theme
article_status: published
---

# desktop.storage

导入路径：`ctf_desktop.storage`。场景接入见 [使用指南](../guides/storage.md)。

## 调用签名与默认值

以下表格核对当前源码声明；`*` 后的参数只能按名称传入。未标注返回类型的接口，其实际输出和异常以本页后续契约为准。

| 接口 | 签名 |
| --- | --- |
| `Migration` | `Migration(version: int, apply: Callable[[sqlite3.Connection], None])` |
| `SqliteStore` | `SqliteStore(path: str \| Path)` |
| `SqliteStore.connect` | `connect() -> sqlite3.Connection` |
| `SqliteStore.close` | `close() -> None` |
| `SqliteStore.migrate` | `migrate(migrations: Iterable[Migration]) -> int` |
| `SqliteStore.backup` | `backup(destination: str \| Path) -> Path` |
| `SqliteStore.restore` | `restore(source: str \| Path) -> Path \| None` |

## 配置字段与只读属性

| 字段 / 属性 | 类型 | 默认值 / 要求 |
| --- | --- | --- |
| `Migration.version` | `int` | 必填 |
| `Migration.apply` | `Callable[[sqlite3.Connection], None]` | 必填 |

## Migration

稳定标识：`desktop.storage.Migration`

Immutable positive integer version (bool rejected) and callable SQLite migration; invalid spec raises ValueError; callbacks must not commit, executescript or manage transactions.

## SqliteStore

稳定标识：`desktop.storage.SqliteStore`

Own one same-thread plaintext SQLite connection; creates parent directory; with connects and always closes without implicit commit; no SQLCipher or key management.

## SqliteStore.connect

稳定标识：`desktop.storage.SqliteStore.connect`

Lazily open and reuse SQLite connection with foreign_keys enabled; host commits/rolls back writes; errors propagate.

## SqliteStore.close

稳定标识：`desktop.storage.SqliteStore.close`

Close owned connection and reset reference; repeated close harmless; uncommitted writes are not committed.

## SqliteStore.migrate

稳定标识：`desktop.storage.SqliteStore.migrate`

Sort unique positive versions; run newer callbacks in BEGIN IMMEDIATE and update user_version; commit all or rollback on error; reject newer stored schema and invalid versions.

## SqliteStore.backup

稳定标识：`desktop.storage.SqliteStore.backup`

Return new consistent SQLite snapshot Path; reject existing/live target and pending writes; atomic no-overwrite publication via same-filesystem hard link, with no unsafe fallback; remove staging and close handles on every exit.

## SqliteStore.restore

稳定标识：`desktop.storage.SqliteStore.restore`

Require different valid SQLite file; snapshot existing data for rollback, stage and check incoming copy, close owned connection then replace; return rollback Path or None; caller stops all other writers/connections; no crash-atomic multi-file recovery.

## 上下文管理

| 用法 | 进入 `with` | 离开 `with` |
| --- | --- | --- |
| `with SqliteStore(...) as resource` | 连接数据库并返回自身 | 关闭连接；不隐式提交事务；正常或异常退出都执行，异常不被吞掉 |

清理本身也可能失败；应用应记录并处理未释放资源，不应把进入 `with` 视为业务操作已成功。

## 最小调用示例

```python
from pathlib import Path
from tempfile import TemporaryDirectory
from ctf_desktop.storage import Migration, SqliteStore
with TemporaryDirectory() as directory:
    store = SqliteStore(Path(directory) / "sample.sqlite")
    try:
        assert store.migrate([Migration(1, lambda db: db.execute("CREATE TABLE items (id INTEGER)"))]) == 1
        assert store.backup(Path(directory) / "snapshot.sqlite").is_file()
    finally:
        store.close()
```
