---
title: "desktop.diagnostics 公开契约"
category: "工程能力"
tags: ["type/api-contract", "desktop", "diagnostics"]
summary: "diagnostics 模块的公开输入输出、边界与副作用。"
created: 2026-10-20
updated: 2026-10-20
metadata_status: reviewed
home_area: theme
article_status: published
---

# desktop.diagnostics

导入路径：`ctf_desktop.diagnostics`。场景接入见 [使用指南](../guides/diagnostics.md)。

## redact

稳定标识：`desktop.diagnostics.redact`

Recursively copy mappings/lists/tuples; replace values under matching secret keys with REDACTED marker; optional key predicate; does not sanitize free text.

## JsonFormatter

稳定标识：`desktop.diagnostics.JsonFormatter`

JSON formatter with optional structured-key predicate; message text and exception content are not automatically redacted.

## JsonFormatter.format

稳定标识：`desktop.diagnostics.JsonFormatter.format`

Return JSON time/level/logger/message/data; redact record.data only; stringify unsupported values; do not emit or write.

## configure_json_logger

稳定标识：`desktop.diagnostics.configure_json_logger`

Serialize logger setup; create UTF-8 handler or reuse same name/path and update redaction formatter; default INFO, max_bytes=5MiB and backup_count=3; 0 bytes disables rotation; invalid limits fail before IO; caller closes/removes handlers.

## AuditEvent

稳定标识：`desktop.diagnostics.AuditEvent`

Immutable action/actor/resource and detail mapping; use non-sensitive identifiers; detail is not deeply frozen.

## AuditJournal

稳定标识：`desktop.diagnostics.AuditJournal`

Append JSON events to caller path under a per-instance lock; fsync writes; no cross-process locking, rotation or tamper-proof guarantee.

## AuditJournal.append

稳定标识：`desktop.diagnostics.AuditJournal.append`

Require nonempty actor/action; append one timestamped structured-redacted event and fsync; ValueError on invalid event, IO errors propagate.

## 最小调用示例

```python
from pathlib import Path
from tempfile import TemporaryDirectory
from ctf_desktop.diagnostics import AuditEvent, AuditJournal, redact
assert redact({"token": "hidden"}) == {"token": "[REDACTED]"}
with TemporaryDirectory() as directory:
    journal = AuditJournal(Path(directory) / "audit.jsonl")
    journal.append(AuditEvent("read", "sample-user", "item-1", {}))
    assert journal.path.is_file()
```
