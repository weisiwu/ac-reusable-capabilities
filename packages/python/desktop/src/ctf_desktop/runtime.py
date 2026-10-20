"""Desktop paths, validated JSON configuration and Qt single-instance guard."""

import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping


@dataclass(frozen=True)
class AppPaths:
    """Immutable safe app_id path segment; reject dot/dotdot and invalid characters; no directory creation until ensure_user_data.

    @ac-reusable
    @ac-capability desktop.runtime.AppPaths
    @ac-kind capability
    @ac-tags desktop, runtime, AppPaths
    @ac-contract Immutable safe app_id path segment; reject dot/dotdot and invalid characters; no directory creation until ensure_user_data.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected. PyQt5 only for SingleInstance.
    @ac-example See examples/desktop_demo.py and docs/contracts/runtime.md.
    @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
    """
    app_id: str

    def __post_init__(self) -> None:
        if self.app_id in {".", ".."} or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", self.app_id):
            raise ValueError("app_id must be a safe path segment")

    def user_data(self) -> Path:
        """Return platform user-data path using APPDATA/XDG_DATA_HOME or home defaults; does not create directories.

        @ac-reusable
        @ac-capability desktop.runtime.AppPaths.user_data
        @ac-kind function
        @ac-tags desktop, runtime, AppPaths
        @ac-contract Return platform user-data path using APPDATA/XDG_DATA_HOME or home defaults; does not create directories.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected. PyQt5 only for SingleInstance.
        @ac-example See examples/desktop_demo.py and docs/contracts/runtime.md.
        @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
        """
        if sys.platform == "darwin":
            base = Path.home() / "Library" / "Application Support"
        elif sys.platform == "win32":
            base = Path(os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming")))
        else:
            base = Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share")))
        return base / self.app_id

    def ensure_user_data(self) -> Path:
        """Create user-data directory and parents then return Path; IO errors propagate; never touches application database.

        @ac-reusable
        @ac-capability desktop.runtime.AppPaths.ensure_user_data
        @ac-kind function
        @ac-tags desktop, runtime, AppPaths
        @ac-contract Create user-data directory and parents then return Path; IO errors propagate; never touches application database.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected. PyQt5 only for SingleInstance.
        @ac-example See examples/desktop_demo.py and docs/contracts/runtime.md.
        @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
        """
        directory = self.user_data()
        directory.mkdir(parents=True, exist_ok=True)
        return directory


def load_json_config(path: str | Path, validate: Callable[[Mapping[str, Any]], None]) -> dict[str, Any]:
    """Read UTF-8 JSON object then invoke mandatory validator; return dict; JSON/IO/validation errors propagate; no writes.

    @ac-reusable
    @ac-capability desktop.runtime.load_json_config
    @ac-kind function
    @ac-tags desktop, runtime, load_json_config
    @ac-contract Read UTF-8 JSON object then invoke mandatory validator; return dict; JSON/IO/validation errors propagate; no writes.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected. PyQt5 only for SingleInstance.
    @ac-example See examples/desktop_demo.py and docs/contracts/runtime.md.
    @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
    """
    values = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(values, dict):
        raise ValueError("configuration root must be an object")
    validate(values)
    return values


class SingleInstance:
    """Qt local-server guard for caller app_id; reject empty id; caller owns release and requires Qt event environment.

    @ac-reusable
    @ac-capability desktop.runtime.SingleInstance
    @ac-kind capability
    @ac-tags desktop, runtime, SingleInstance
    @ac-contract Qt local-server guard for caller app_id; reject empty id; caller owns release and requires Qt event environment.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected. PyQt5 only for SingleInstance.
    @ac-example See examples/desktop_demo.py and docs/contracts/runtime.md.
    @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
    """

    def __init__(self, app_id: str):
        if not app_id:
            raise ValueError("app_id is required")
        self.app_id = app_id
        self._server = None

    def acquire(self) -> bool:
        """Return true on acquired/already-owned socket; false for active peer; remove stale socket then retry; RuntimeError if listen still fails.

        @ac-reusable
        @ac-capability desktop.runtime.SingleInstance.acquire
        @ac-kind function
        @ac-tags desktop, runtime, SingleInstance
        @ac-contract Return true on acquired/already-owned socket; false for active peer; remove stale socket then retry; RuntimeError if listen still fails.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected. PyQt5 only for SingleInstance.
        @ac-example See examples/desktop_demo.py and docs/contracts/runtime.md.
        @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
        """
        from PyQt5.QtNetwork import QLocalServer, QLocalSocket

        if self._server is not None:
            return True
        server = QLocalServer()
        if not server.listen(self.app_id):
            probe = QLocalSocket()
            probe.connectToServer(self.app_id)
            active = probe.waitForConnected(150)
            probe.abort()
            if active:
                return False
            QLocalServer.removeServer(self.app_id)
            if not server.listen(self.app_id):
                raise RuntimeError(f"could not acquire instance name: {self.app_id}")
        self._server = server
        return True

    def release(self) -> None:
        """Close owned Qt server and clear ownership; idempotent; no killing peer processes.

        @ac-reusable
        @ac-capability desktop.runtime.SingleInstance.release
        @ac-kind function
        @ac-tags desktop, runtime, SingleInstance
        @ac-contract Close owned Qt server and clear ownership; idempotent; no killing peer processes.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected. PyQt5 only for SingleInstance.
        @ac-example See examples/desktop_demo.py and docs/contracts/runtime.md.
        @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
        """
        if self._server is not None:
            self._server.close()
            self._server = None
