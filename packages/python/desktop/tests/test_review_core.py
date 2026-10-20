"""Failures found by reviewing the complete desktop package after initial import."""
import hashlib
import importlib.util
import logging
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path

import pytest

from ctf_desktop.auth import PasswordHasher
from ctf_desktop.diagnostics import configure_json_logger
from ctf_desktop.printing import BatchPrintRunner, PrintItem
from ctf_desktop.services import ServiceRegistry, ServiceSpec
from ctf_desktop.storage import Migration, SqliteStore
from ctf_desktop.transport import SerialConfig, SerialTransport, TransportError


def test_malformed_hash_rehash_and_unbounded_work_are_rejected(monkeypatch):
    hasher = PasswordHasher(100_000)
    calls = []
    monkeypatch.setattr(hashlib, 'pbkdf2_hmac', lambda *args: calls.append(args) or b'\0' * 32)
    for encoded in ('pbkdf2_sha256$100000$zz$zz', 'pbkdf2_sha256$999999999$00$' + '00' * 32, 'pbkdf2_sha256$100000$00$' + '00' * 32):
        assert hasher.needs_rehash(encoded)
        assert not hasher.verify('example', encoded)
    assert calls == []


def test_service_stop_descriptor_failure_still_releases_other_services():
    events = []
    class Base:
        def stop(self): events.append('base stopped')
    class Broken:
        @property
        def stop(self): raise ValueError('lookup failed')
    registry = ServiceRegistry()
    registry.register(ServiceSpec('base', lambda registry: Base()))
    registry.register(ServiceSpec('broken', lambda registry: Broken(), ('base',)))
    registry.start()
    with pytest.raises(RuntimeError): registry.stop()
    assert events == ['base stopped'] and not registry.running
    registry.stop()


def test_service_registration_is_rejected_inside_first_factory():
    registry = ServiceRegistry()
    def create(registry):
        with pytest.raises(RuntimeError):
            registry.register(ServiceSpec('late', lambda registry: object()))
        return object()
    registry.register(ServiceSpec('first', create))
    try:
        registry.start()
    finally:
        registry.stop()


def test_print_run_rejects_overlap_and_closed_runner():
    started, release = threading.Event(), threading.Event()
    def prepare(key):
        started.set()
        assert release.wait(3)
        return b'pdf'
    runner = BatchPrintRunner(prepare, lambda artifact: None)
    try:
        future = runner.start([PrintItem('sample')])
        assert started.wait(2)
        with pytest.raises(RuntimeError, match='running'):
            runner.run([])
    finally:
        release.set()
        runner.close()
    assert future.result().succeeded == 1
    with pytest.raises(RuntimeError, match='closed'):
        runner.run([])


def test_backup_publication_never_overwrites_concurrently_created_target(tmp_path, monkeypatch):
    store = SqliteStore(tmp_path / 'live.sqlite')
    target = tmp_path / 'snapshot.sqlite'
    store.migrate([Migration(1, lambda db: db.execute('CREATE TABLE items (id INTEGER)'))])
    original = store._check
    def check(path):
        original(path)
        target.write_bytes(b'other writer owns this')
    monkeypatch.setattr(store, '_check', check)
    try:
        with pytest.raises(FileExistsError): store.backup(target)
        assert target.read_bytes() == b'other writer owns this'
        assert not list(tmp_path.glob('.ctf-backup-*'))
    finally:
        store.close()


@pytest.mark.parametrize('version', [True, 1.5, '1', 0])
def test_migration_requires_positive_integer_version(version):
    with pytest.raises(ValueError): Migration(version, lambda db: None)


@pytest.mark.parametrize('kwargs', [{'port': ' '}, {'port': 'x', 'timeout': float('nan')}, {'port': 'x', 'write_timeout': float('inf')}, {'port': 'x', 'baudrate': True}])
def test_serial_configuration_rejects_unusable_settings(kwargs):
    with pytest.raises(ValueError): SerialConfig(**kwargs)


def test_failed_serial_close_preserves_handle_for_retry():
    class Handle:
        is_open = True
        failed = False
        def __init__(self, **kwargs): pass
        def close(self):
            if not self.failed:
                self.failed = True
                raise OSError('temporary close failure')
            self.is_open = False
    transport = SerialTransport(SerialConfig('fake'), Handle)
    transport.open()
    try:
        with pytest.raises(TransportError): transport.close()
        assert transport.is_open
    finally:
        transport.close()
    assert not transport.is_open


def test_logger_reconfiguration_updates_redaction_policy(tmp_path):
    path = tmp_path / 'logger.jsonl'
    logger = configure_json_logger('review-reconfigure', path)
    try:
        configure_json_logger('review-reconfigure', path, lambda key: key == 'private')
        logger.info('safe', extra={'data': {'private': 'do-not-record'}})
        assert 'do-not-record' not in path.read_text()
    finally:
        for handler in list(logger.handlers):
            handler.close(); logger.removeHandler(handler)
