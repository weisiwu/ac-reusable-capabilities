import pytest

pytest.importorskip("PyQt5")

from ctf_desktop.filters import FilterField, FilterPanel, LiveSearchComboBox
from ctf_desktop.forms import FieldSpec, FormDialog, validate_values
from ctf_desktop.navigation import PageHost, PageSpec
from ctf_desktop.query import PageRequest, PageResult
from ctf_desktop.table import Column, PagedTable
from ctf_desktop.feedback import BusyOverlay, EmptyState, Toast
from ctf_desktop.crud import CrudController
from ctf_desktop.crud_page import CrudPage
from ctf_desktop.runtime import SingleInstance


def test_table_page_and_selected_records(qapp):
    table = PagedTable([Column("id", "ID"), Column("name", "名称")], page_size=2)
    table.set_page(PageResult(({"id": 1, "name": "A"}, {"id": 2, "name": "B"}), 3, PageRequest(1, 2)))
    assert table.model.data(table.model.index(0, 1)) == "A"
    assert table.next.isEnabled()
    requested = []
    table.page_requested.connect(requested.append)
    table.next.click()
    assert requested == [PageRequest(2, 2)]
    table.table.selectRow(0)
    assert table.selected_records()[0]["id"] == 1


def test_form_validation_and_detail_values(qapp):
    fields = (FieldSpec("name", "名称", required=True), FieldSpec("active", "启用", kind="boolean"))
    assert validate_values(fields, {"name": "", "active": False}) == {"name": "必填"}
    dialog = FormDialog("编辑", fields, {"name": "A", "active": True})
    assert dialog.values() == {"name": "A", "active": True}


def test_filter_values_and_stale_live_search(qapp):
    panel = FilterPanel((FilterField("status", "状态", "choice", (("ok", "正常"),)),))
    panel._widgets["status"].setCurrentIndex(1)
    assert panel.values() == {"status": "ok"}
    panel.clear()
    assert panel.values() == {}
    combo = LiveSearchComboBox()
    combo.setEditText("new")
    assert not combo.set_results("old", ((1, "old"),))
    assert combo.set_results("new", ((2, "new result"),))
    date_panel = FilterPanel((FilterField("when", "日期", "date_range"),))
    assert date_panel.values() == {}


def test_page_host_keeps_one_instance_and_calls_hooks(qapp):
    from PyQt5.QtWidgets import QWidget

    events = []

    class Page(QWidget):
        def on_enter(self):
            events.append("enter")

        def on_leave(self):
            events.append("leave")

        def dispose(self):
            events.append("dispose")

    host = PageHost()
    host.register(PageSpec("first", "First", Page))
    host.register(PageSpec("second", "Second", QWidget))
    first = host.navigate("first")
    host.navigate("second")
    assert host.navigate("first") is first
    host.dispose()
    assert events == ["enter", "leave", "enter", "dispose"]


def test_crud_page_loads_through_controller_and_reports_failure(qapp):
    class Repository:
        def list_page(self, request, _filters):
            return PageResult(({"id": 8, "name": "Item"},), 1, request)

    page = CrudPage(
        CrudController(Repository(), authorize=lambda _action, _resource: None),
        identity_key="id",
        columns=(Column("id", "ID"), Column("name", "名称")),
        fields=(FieldSpec("name", "名称"),),
    )
    page.load_page()
    assert page.table.model.records[0]["id"] == 8
    failed = []
    page.operation_failed.connect(lambda action, error: failed.append((action, type(error))))
    page.controller.authorize = lambda _action, _resource: (_ for _ in ()).throw(PermissionError())
    page.load_page()
    assert failed == [("list", PermissionError)]


def test_feedback_widgets_and_single_instance(qapp):
    from PyQt5.QtWidgets import QWidget

    parent = QWidget()
    parent.resize(300, 200)
    overlay = BusyOverlay(parent)
    overlay.show_message("Loading")
    assert overlay.isVisible() == parent.isVisible()
    empty = EmptyState("No data")
    assert empty.title_label.text() == "No data"
    toast = Toast(parent)
    toast.show_message("Done", 100)
    assert toast.text() == "Done"
    one = SingleInstance("ctf-test-single-instance")
    two = SingleInstance("ctf-test-single-instance")
    assert one.acquire()
    assert not two.acquire()
    one.release()
    assert two.acquire()
    two.release()
