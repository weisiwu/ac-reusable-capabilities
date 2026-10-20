"""Run from an installed package: python examples/desktop_demo.py [--qt]."""
from __future__ import annotations

import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from ctf_desktop.auth import AccessPolicy, Principal
from ctf_desktop.crud import CrudController
from ctf_desktop.printing import BatchPrintRunner, PrintItem
from ctf_desktop.query import PageRequest, PageResult
from ctf_desktop.services import ServiceRegistry, ServiceSpec
from ctf_desktop.storage import Migration, SqliteStore


class Inventory:
    """Example-only in-memory repository; no private business schema."""
    def __init__(self): self.rows = {}
    def list_page(self, request, filters):
        values = tuple(dict(id=key, **row) for key, row in self.rows.items())
        return PageResult(values[request.offset:request.offset+request.size], len(values), request)
    def get(self, identity): return self.rows.get(identity)
    def create(self, values):
        key = max(self.rows, default=0) + 1
        self.rows[key] = dict(values)
        return key
    def update(self, identity, values): self.rows[identity].update(values)
    def delete(self, identity): del self.rows[identity]


def main():
    actor = Principal('example-user', frozenset({'editor'}))
    policy = AccessPolicy(lambda user, action, resource: 'editor' in user.roles)
    controller = CrudController(Inventory(), authorize=lambda action, resource: policy.require(actor, action, resource))
    identity = controller.create({'name': 'Example item'})
    assert controller.detail(identity)['name'] == 'Example item'
    with TemporaryDirectory() as directory:
        store = SqliteStore(Path(directory)/'sample.sqlite')
        try:
            store.migrate([Migration(1, lambda db: db.execute('CREATE TABLE sample (id INTEGER)'))])
            assert store.backup(Path(directory)/'snapshot.sqlite').exists()
        finally:
            store.close()
    submitted = []
    printer = BatchPrintRunner(lambda key: key.encode(), submitted.append)
    try:
        result = printer.start([PrintItem('sample', 2)]).result(timeout=2)
        assert result.succeeded == 2 and submitted == [b'sample', b'sample']
    finally:
        printer.close()
    registry = ServiceRegistry()
    registry.register(ServiceSpec('inventory', lambda registry: controller))
    try:
        registry.start()
        assert registry.get('inventory') is controller
    finally:
        registry.stop()
    if '--qt' in sys.argv:
        from PyQt5.QtWidgets import QApplication
        from ctf_desktop.table import Column, PagedTable
        app = QApplication.instance() or QApplication([])
        table = PagedTable([Column('id','ID'), Column('name','Name')])
        try:
            table.set_page(controller.list_page(PageRequest()))
            assert table.model.rowCount() == 1
            app.processEvents()
        finally:
            table.close()
            table.deleteLater()
            app.processEvents()
            app.quit()
    print('Desktop example passed: injected CRUD, SQLite snapshot, print dispatch, services' + (' and Qt table.' if '--qt' in sys.argv else '.'))


if __name__ == '__main__':
    main()
