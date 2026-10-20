---
title: "desktop.runtime 公开契约"
category: "工程能力"
tags: ["type/api-contract", "desktop", "runtime"]
summary: "runtime 模块的公开输入输出、边界与副作用。"
created: 2026-10-20
updated: 2026-10-20
metadata_status: reviewed
home_area: theme
article_status: published
---

# desktop.runtime

导入路径：`ctf_desktop.runtime`。场景接入见 [使用指南](../guides/runtime.md)。

## AppPaths

稳定标识：`desktop.runtime.AppPaths`

Immutable safe app_id path segment; reject dot/dotdot and invalid characters; no directory creation until ensure_user_data.

## AppPaths.user_data

稳定标识：`desktop.runtime.AppPaths.user_data`

Return platform user-data path using APPDATA/XDG_DATA_HOME or home defaults; does not create directories.

## AppPaths.ensure_user_data

稳定标识：`desktop.runtime.AppPaths.ensure_user_data`

Create user-data directory and parents then return Path; IO errors propagate; never touches application database.

## load_json_config

稳定标识：`desktop.runtime.load_json_config`

Read UTF-8 JSON object then invoke mandatory validator; return dict; JSON/IO/validation errors propagate; no writes.

## SingleInstance

稳定标识：`desktop.runtime.SingleInstance`

Qt local-server guard for caller app_id; reject empty id; caller owns release and requires Qt event environment.

## SingleInstance.acquire

稳定标识：`desktop.runtime.SingleInstance.acquire`

Return true on acquired/already-owned socket; false for active peer; remove stale socket then retry; RuntimeError if listen still fails.

## SingleInstance.release

稳定标识：`desktop.runtime.SingleInstance.release`

Close owned Qt server and clear ownership; idempotent; no killing peer processes.

## 最小调用示例

```python
from ctf_desktop.runtime import AppPaths
assert AppPaths("sample-app").user_data().name == "sample-app"
```
