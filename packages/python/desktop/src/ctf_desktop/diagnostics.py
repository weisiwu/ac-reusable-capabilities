"""Structured logging, caller-defined redaction and append-only audit events."""

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Callable, Mapping


DEFAULT_SECRET_KEYS = frozenset({"password", "passwd", "secret", "token", "api_key", "authorization"})


def redact(value: Any, is_sensitive: Callable[[str], bool] | None = None) -> Any:
    """Recursively copy mappings/lists/tuples; replace values under matching secret keys with REDACTED marker; optional key predicate; does not sanitize free text.

    @ac-reusable
    @ac-capability desktop.diagnostics.redact
    @ac-kind function
    @ac-tags desktop, diagnostics, redact
    @ac-contract Recursively copy mappings/lists/tuples; replace values under matching secret keys with REDACTED marker; optional key predicate; does not sanitize free text.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected.
    @ac-example See examples/desktop_demo.py and docs/contracts/diagnostics.md.
    @ac-tests tests/test_core.py and tests/test_contracts.py
    """
    predicate = is_sensitive or (lambda key: key.lower() in DEFAULT_SECRET_KEYS)
    if isinstance(value, Mapping):
        return {str(key): "[REDACTED]" if predicate(str(key)) else redact(item, predicate) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [redact(item, predicate) for item in value]
    return value


class JsonFormatter(logging.Formatter):
    """JSON formatter with optional structured-key predicate; message text and exception content are not automatically redacted.

    @ac-reusable
    @ac-capability desktop.diagnostics.JsonFormatter
    @ac-kind capability
    @ac-tags desktop, diagnostics, JsonFormatter
    @ac-contract JSON formatter with optional structured-key predicate; message text and exception content are not automatically redacted.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected.
    @ac-example See examples/desktop_demo.py and docs/contracts/diagnostics.md.
    @ac-tests tests/test_core.py and tests/test_contracts.py
    """
    def __init__(self, is_sensitive: Callable[[str], bool] | None = None):
        super().__init__()
        self.is_sensitive = is_sensitive

    def format(self, record: logging.LogRecord) -> str:
        """Return JSON time/level/logger/message/data; redact record.data only; stringify unsupported values; do not emit or write.

        @ac-reusable
        @ac-capability desktop.diagnostics.JsonFormatter.format
        @ac-kind function
        @ac-tags desktop, diagnostics, JsonFormatter
        @ac-contract Return JSON time/level/logger/message/data; redact record.data only; stringify unsupported values; do not emit or write.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/diagnostics.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        payload = {
            "time": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "data": redact(getattr(record, "data", {}), self.is_sensitive),
        }
        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_json_logger(
    name: str, path: str | Path, is_sensitive=None, *, level: int = logging.INFO
) -> logging.Logger:
    """Create parent and UTF-8 file handler; reuse handler for same name/path, disable propagation, default INFO; caller closes/removes owned handlers; no rotation.

    @ac-reusable
    @ac-capability desktop.diagnostics.configure_json_logger
    @ac-kind function
    @ac-tags desktop, diagnostics, configure_json_logger
    @ac-contract Create parent and UTF-8 file handler; reuse handler for same name/path, disable propagation, default INFO; caller closes/removes owned handlers; no rotation.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected.
    @ac-example See examples/desktop_demo.py and docs/contracts/diagnostics.md.
    @ac-tests tests/test_core.py and tests/test_contracts.py
    """
    target = Path(path).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(level)
    for existing in logger.handlers:
        if isinstance(existing, logging.FileHandler) and Path(existing.baseFilename) == target:
            return logger
    handler = logging.FileHandler(target, encoding="utf-8")
    handler.setFormatter(JsonFormatter(is_sensitive))
    logger.addHandler(handler)
    return logger


@dataclass(frozen=True)
class AuditEvent:
    """Immutable action/actor/resource and detail mapping; use non-sensitive identifiers; detail is not deeply frozen.

    @ac-reusable
    @ac-capability desktop.diagnostics.AuditEvent
    @ac-kind capability
    @ac-tags desktop, diagnostics, AuditEvent
    @ac-contract Immutable action/actor/resource and detail mapping; use non-sensitive identifiers; detail is not deeply frozen.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected.
    @ac-example See examples/desktop_demo.py and docs/contracts/diagnostics.md.
    @ac-tests tests/test_core.py and tests/test_contracts.py
    """
    action: str
    actor: str
    resource: str
    detail: Mapping[str, Any]


class AuditJournal:
    """Append JSON events to caller path under a per-instance lock; fsync writes; no cross-process locking, rotation or tamper-proof guarantee.

    @ac-reusable
    @ac-capability desktop.diagnostics.AuditJournal
    @ac-kind capability
    @ac-tags desktop, diagnostics, AuditJournal
    @ac-contract Append JSON events to caller path under a per-instance lock; fsync writes; no cross-process locking, rotation or tamper-proof guarantee.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected.
    @ac-example See examples/desktop_demo.py and docs/contracts/diagnostics.md.
    @ac-tests tests/test_core.py and tests/test_contracts.py
    """
    def __init__(self, path: str | Path, is_sensitive=None):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.is_sensitive = is_sensitive
        self._lock = Lock()

    def append(self, event: AuditEvent) -> None:
        """Require nonempty actor/action; append one timestamped structured-redacted event and fsync; ValueError on invalid event, IO errors propagate.

        @ac-reusable
        @ac-capability desktop.diagnostics.AuditJournal.append
        @ac-kind function
        @ac-tags desktop, diagnostics, AuditJournal
        @ac-contract Require nonempty actor/action; append one timestamped structured-redacted event and fsync; ValueError on invalid event, IO errors propagate.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/diagnostics.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        if not event.action or not event.actor:
            raise ValueError("audit action and actor are required")
        payload = {
            "time": datetime.now(timezone.utc).isoformat(),
            "action": event.action,
            "actor": event.actor,
            "resource": event.resource,
            "detail": redact(event.detail, self.is_sensitive),
        }
        line = json.dumps(payload, ensure_ascii=False, default=str)
        with self._lock:
            with self.path.open("a", encoding="utf-8") as stream:
                stream.write(line + "\n")
                stream.flush()
                os.fsync(stream.fileno())
