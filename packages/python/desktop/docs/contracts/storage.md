---
title: "desktop.storage 公开契约"
category: "工程能力"
tags: ["type/api-contract", "desktop", "storage"]
summary: "storage 模块的公开输入输出、边界与副作用。"
created: 2026-10-20
updated: 2026-10-20
metadata_status: reviewed
home_area: theme
article_status: published
---

# desktop.storage

导入路径：`ctf_desktop.storage`。标识一经收录保持稳定。下列契约包含适用边界；外部回调与业务事务由接入方管理。

## Migration

稳定标识：`desktop.storage.Migration`

Immutable positive version and SQLite callback; callbacks must not commit/executescript or manage transactions; schema is host-owned.

## SqliteStore

稳定标识：`desktop.storage.SqliteStore`

Own one same-thread plaintext SQLite connection; create parent directory; no SQLCipher, key handling, process locks or downgrade support.

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

Return new snapshot Path after backup API and integrity check; reject existing/live destination; RuntimeError on pending writes to avoid self-blocking; close temporary handles, remove staging file on failure.

## SqliteStore.restore

稳定标识：`desktop.storage.SqliteStore.restore`

Require different valid SQLite file; snapshot existing data for rollback, stage and check incoming copy, close owned connection then replace; return rollback Path or None; caller stops all other writers/connections; no crash-atomic multi-file recovery.

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
