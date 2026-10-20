"""SQLite migration, consistent snapshot and guarded restore primitives."""

import os
from contextlib import closing
import sqlite3
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable


@dataclass(frozen=True)
class Migration:
    """Immutable positive version and SQLite callback; callbacks must not commit/executescript or manage transactions; schema is host-owned.

    @ac-reusable
    @ac-capability desktop.storage.Migration
    @ac-kind capability
    @ac-tags desktop, storage, Migration
    @ac-contract Immutable positive version and SQLite callback; callbacks must not commit/executescript or manage transactions; schema is host-owned.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected.
    @ac-example See examples/desktop_demo.py and docs/contracts/storage.md.
    @ac-tests tests/test_core.py and tests/test_contracts.py
    """
    version: int
    apply: Callable[[sqlite3.Connection], None]


class SqliteStore:
    """Own one same-thread plaintext SQLite connection; create parent directory; no SQLCipher, key handling, process locks or downgrade support.

    @ac-reusable
    @ac-capability desktop.storage.SqliteStore
    @ac-kind capability
    @ac-tags desktop, storage, SqliteStore
    @ac-contract Own one same-thread plaintext SQLite connection; create parent directory; no SQLCipher, key handling, process locks or downgrade support.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected.
    @ac-example See examples/desktop_demo.py and docs/contracts/storage.md.
    @ac-tests tests/test_core.py and tests/test_contracts.py
    """
    def __init__(self, path: str | Path):
        self.path = Path(path).expanduser().resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._connection: sqlite3.Connection | None = None

    def connect(self) -> sqlite3.Connection:
        """Lazily open and reuse SQLite connection with foreign_keys enabled; host commits/rolls back writes; errors propagate.

        @ac-reusable
        @ac-capability desktop.storage.SqliteStore.connect
        @ac-kind function
        @ac-tags desktop, storage, SqliteStore
        @ac-contract Lazily open and reuse SQLite connection with foreign_keys enabled; host commits/rolls back writes; errors propagate.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/storage.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        if self._connection is None:
            self._connection = sqlite3.connect(self.path)
            self._connection.execute("PRAGMA foreign_keys = ON")
        return self._connection

    def close(self) -> None:
        """Close owned connection and reset reference; repeated close harmless; uncommitted writes are not committed.

        @ac-reusable
        @ac-capability desktop.storage.SqliteStore.close
        @ac-kind function
        @ac-tags desktop, storage, SqliteStore
        @ac-contract Close owned connection and reset reference; repeated close harmless; uncommitted writes are not committed.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/storage.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def migrate(self, migrations: Iterable[Migration]) -> int:
        """Sort unique positive versions; run newer callbacks in BEGIN IMMEDIATE and update user_version; commit all or rollback on error; reject newer stored schema and invalid versions.

        @ac-reusable
        @ac-capability desktop.storage.SqliteStore.migrate
        @ac-kind function
        @ac-tags desktop, storage, SqliteStore
        @ac-contract Sort unique positive versions; run newer callbacks in BEGIN IMMEDIATE and update user_version; commit all or rollback on error; reject newer stored schema and invalid versions.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/storage.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        ordered = sorted(tuple(migrations), key=lambda item: item.version)
        versions = [item.version for item in ordered]
        if any(version < 1 for version in versions) or len(set(versions)) != len(versions):
            raise ValueError("migration versions must be unique positive integers")
        connection = self.connect()
        current = int(connection.execute("PRAGMA user_version").fetchone()[0])
        if ordered and current > ordered[-1].version:
            raise ValueError("database is newer than the provided migrations")
        connection.execute("BEGIN IMMEDIATE")
        try:
            for migration in ordered:
                if migration.version > current:
                    migration.apply(connection)
                    connection.execute(f"PRAGMA user_version = {migration.version}")
                    current = migration.version
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        return current

    @staticmethod
    def _check(path: Path) -> None:
        with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as connection:
            result = connection.execute("PRAGMA integrity_check").fetchone()
            if result is None or result[0] != "ok":
                raise ValueError("SQLite integrity check failed")

    def backup(self, destination: str | Path) -> Path:
        """Return new snapshot Path after backup API and integrity check; reject existing/live destination; RuntimeError on pending writes to avoid self-blocking; close temporary handles, remove staging file on failure.

        @ac-reusable
        @ac-capability desktop.storage.SqliteStore.backup
        @ac-kind function
        @ac-tags desktop, storage, SqliteStore
        @ac-contract Return new snapshot Path after backup API and integrity check; reject existing/live destination; RuntimeError on pending writes to avoid self-blocking; close temporary handles, remove staging file on failure.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/storage.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        if self._connection is not None and self._connection.in_transaction:
            raise RuntimeError("commit or roll back pending writes before backup")
        target = Path(destination).expanduser().resolve()
        if target == self.path or target.exists():
            raise FileExistsError("backup destination exists or equals live database")
        target.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(prefix=".ctf-backup-", dir=target.parent)
        os.close(descriptor)
        temporary = Path(temporary_name)
        try:
            with closing(sqlite3.connect(temporary)) as snapshot:
                self.connect().backup(snapshot)
            self._check(temporary)
            os.replace(temporary, target)
            return target
        finally:
            temporary.unlink(missing_ok=True)

    def restore(self, source: str | Path) -> Path | None:
        """Require different valid SQLite file; snapshot existing data for rollback, stage and check incoming copy, close owned connection then replace; return rollback Path or None; caller stops all other writers/connections; no crash-atomic multi-file recovery.

        @ac-reusable
        @ac-capability desktop.storage.SqliteStore.restore
        @ac-kind function
        @ac-tags desktop, storage, SqliteStore
        @ac-contract Require different valid SQLite file; snapshot existing data for rollback, stage and check incoming copy, close owned connection then replace; return rollback Path or None; caller stops all other writers/connections; no crash-atomic multi-file recovery.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/storage.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        candidate = Path(source).expanduser().resolve()
        if candidate == self.path or not candidate.is_file():
            raise ValueError("restore source must be a different SQLite file")
        self._check(candidate)
        rollback = None
        if self.path.exists():
            rollback = self.path.with_name(f"{self.path.name}.before-restore-{uuid.uuid4().hex}.sqlite")
            self.backup(rollback)
        descriptor, temporary_name = tempfile.mkstemp(prefix=".ctf-restore-", dir=self.path.parent)
        os.close(descriptor)
        temporary = Path(temporary_name)
        try:
            with closing(sqlite3.connect(candidate.as_uri() + "?mode=ro", uri=True)) as incoming:
                with closing(sqlite3.connect(temporary)) as staged:
                    incoming.backup(staged)
            self._check(temporary)
            self.close()
            for suffix in ("-wal", "-shm", "-journal"):
                Path(str(self.path) + suffix).unlink(missing_ok=True)
            os.replace(temporary, self.path)
            return rollback
        finally:
            temporary.unlink(missing_ok=True)
