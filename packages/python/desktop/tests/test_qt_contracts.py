import uuid

import pytest
pytest.importorskip('PyQt5')
from PyQt5.QtCore import QDate, QModelIndex, Qt, QEvent
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QDialog, QLineEdit, QWidget

from ctf_desktop.crud import CrudController
from ctf_desktop.crud_page import CrudPage
from ctf_desktop.feedback import BusyOverlay, ConfirmDialog, EmptyState, Toast
from ctf_desktop.filters import FilterField, FilterPanel, LiveSearchComboBox
from ctf_desktop.forms import DetailView, FieldSpec, FormDialog, validate_values
from ctf_desktop.navigation import PageHost, PageSpec
from ctf_desktop.query import PageRequest, PageResult
from ctf_desktop.runtime import SingleInstance
from ctf_desktop.table import Column, PagedTable, RecordTableModel


def test_table_roles_reset_empty_state_and_invalid_columns(qapp):
    for columns in ([], [Column('id','one'), Column('id','two')]):
        with pytest.raises(ValueError): RecordTableModel(columns)
    model = RecordTableModel([Column('id', 'ID', lambda v: f'#{v}')])
    rows = [{'id': 3}]
    model.set_records(rows); rows[0]['id'] = 8
    assert model.data(model.index(0, 0)) == '#3'
    assert model.data(model.index(0, 0), Qt.UserRole) == {'id': 3}
    assert model.data(QModelIndex()) is None
    assert model.rowCount(model.index(0, 0)) == model.columnCount(model.index(0, 0)) == 0
    assert model.headerData(0, Qt.Horizontal) == 'ID'
    table = PagedTable([Column('id','ID')], page_size=2)
    table.set_page(PageResult(({'id': 1},), 1, PageRequest(1, 2)))
    table.table.selectRow(0)
    assert table.selected_records() == ({'id': 1},)
    table.set_page(PageResult((), 0, PageRequest(1, 2)))
    assert not table.previous.isEnabled() and not table.next.isEnabled()
    assert table.selected_records() == ()


def test_form_kinds_valid_submit_reject_invalid_and_detail(qapp):
    for kwargs in ({'kind':'unsupported'}, {'kind':'custom'}):
        with pytest.raises(ValueError): FieldSpec('bad','Bad',**kwargs)
    fields = (
        FieldSpec('text','Text',required=True), FieldSpec('multi','Multi',kind='multiline'),
        FieldSpec('int','Int',kind='integer'), FieldSpec('bool','Bool',kind='boolean',required=True),
        FieldSpec('choice','Choice',kind='choice',choices=((1,'One'),)),
        FieldSpec('custom','Custom',kind='custom',widget_factory=lambda v: QLineEdit(v or ''),value_reader=lambda w:w.text()),
    )
    initial = {'text':'value','multi':'two lines\nnext','int':-2,'bool':False,'choice':1,'custom':'custom'}
    dialog = FormDialog('Sample',fields,initial)
    assert dialog.values() == initial
    buttons = dialog.findChildren(__import__('PyQt5.QtWidgets',fromlist=['QDialogButtonBox']).QDialogButtonBox)[0]
    submitted=[]; dialog.submitted.connect(submitted.append)
    dialog._widgets['text'].clear()
    buttons.accepted.emit()
    assert submitted == [] and 'text' in dialog.error_label.text()
    dialog._widgets['text'].setText('  valid  ')
    buttons.accepted.emit()
    assert submitted[0]['text'] == 'valid' and dialog.result() == QDialog.Accepted
    assert validate_values([FieldSpec('value','Value',validate=lambda v:'bad')],{}) == {'value':'bad'}
    detail=DetailView([FieldSpec('value','Value')],{'value':None})
    assert detail.layout().itemAt(1).widget().text() == ''


def test_filter_signals_date_boundary_and_reset(qapp):
    with pytest.raises(ValueError): FilterField('x','X',kind='bad')
    panel=FilterPanel([FilterField('name','Name'),FilterField('when','When',kind='date_range')])
    panel._widgets['name'].setText('  sample  ')
    start,end=panel._widgets['when']; start.setDate(QDate(2026,10,1)); end.setDate(QDate(2026,10,20))
    assert panel.values()=={'name':'sample','when':('2026-10-01','2026-10-20')}
    events=[]; panel.reset_requested.connect(lambda:events.append(panel.values()))
    panel.clear(); panel.clear()
    assert events==[{},{}]


def test_search_debounce_ignores_old_text_and_emits_latest_query(qapp):
    combo=LiveSearchComboBox(delay_ms=15)
    events=[]; combo.search_requested.connect(events.append)
    QTest.keyClicks(combo.lineEdit(),'ab')
    QTest.qWait(50)
    assert events==['ab']
    assert not combo.set_results('old',[(1,'Old')])
    assert combo.set_results('ab',[(2,'AB')])
    assert combo.itemData(0)==2
    combo.hidePopup()


def test_navigation_failure_restores_previous_page_and_disposes_once(qapp):
    events=[]
    class Page(QWidget):
        def on_enter(self):events.append('enter')
        def on_leave(self):events.append('leave')
        def dispose(self):events.append('dispose')
    class Broken(QWidget):
        def on_enter(self):raise ValueError('enter failed')
    host=PageHost()
    host.register(PageSpec('first','First',Page)); host.register(PageSpec('broken','Broken',Broken))
    host.register(PageSpec('invalid','Invalid',lambda:object()))
    with pytest.raises(ValueError):host.register(PageSpec('first','Again',Page))
    first=host.navigate('first')
    assert host.navigate('first') is first
    with pytest.raises(KeyError):host.navigate('unknown')
    with pytest.raises(TypeError):host.navigate('invalid')
    with pytest.raises(ValueError):host.navigate('broken')
    assert host.stack.currentWidget() is first and host.sidebar.currentRow()==0
    host.dispose(); host.dispose()
    assert events==['enter','leave','enter','dispose']


def test_feedback_confirmation_defaults_and_single_instance_release(qapp,monkeypatch):
    from PyQt5.QtWidgets import QMessageBox
    parent=QWidget(); parent.resize(320,200); parent.show()
    overlay=BusyOverlay(parent); overlay.show_message('Busy')
    assert overlay.isVisible() and overlay.geometry()==parent.rect()
    overlay.hide(); assert not overlay.isVisible()
    toast=Toast(parent); toast.show_message('Done',15)
    QTest.qWait(50); assert not toast.isVisible()
    observed=[]
    monkeypatch.setattr(QMessageBox,'question',lambda *args:observed.append(args[-1]) or QMessageBox.No)
    assert not ConfirmDialog.ask(parent,'Question','Continue?')
    assert observed==[QMessageBox.No]
    monkeypatch.setattr(QMessageBox,'question',lambda *args:QMessageBox.Yes)
    assert ConfirmDialog.ask(parent,'Question','Continue?')
    name='ac-instance-'+uuid.uuid4().hex
    one,two=SingleInstance(name),SingleInstance(name)
    try:
        assert one.acquire() and one.acquire()
        assert not two.acquire()
        one.release(); one.release()
        assert two.acquire()
    finally:
        one.release();two.release()


def test_crud_ui_create_edit_detail_delete_and_cancel(qapp,monkeypatch):
    from test_contracts import MemoryRepository
    repository=MemoryRepository()
    page=CrudPage(CrudController(repository,authorize=lambda *a:None),identity_key='id',columns=[Column('id','ID'),Column('name','Name')],fields=[FieldSpec('name','Name')])
    # Real controller/repository with modal interaction replaced at dialog boundary.
    monkeypatch.setattr(FormDialog,'exec_',lambda self:QDialog.Accepted)
    monkeypatch.setattr(FormDialog,'values',lambda self:{'name':'created'})
    changed=[];page.changed.connect(lambda *a:changed.append(a))
    page.create_record()
    assert repository.rows=={1:{'name':'created'}}
    page.table.table.selectRow(0)
    monkeypatch.setattr(FormDialog,'values',lambda self:{'name':'edited'})
    page.edit_selected();assert repository.rows[1]['name']=='edited'
    page.table.table.selectRow(0)
    monkeypatch.setattr(QDialog,'exec_',lambda self:QDialog.Accepted)
    page.show_detail()
    monkeypatch.setattr(ConfirmDialog,'ask',lambda *a:False)
    page.delete_selected();assert 1 in repository.rows
    monkeypatch.setattr(ConfirmDialog,'ask',lambda *a:True)
    page.delete_selected();assert repository.rows=={}
    assert changed==[('create',1),('update',1),('delete',1)]
    monkeypatch.setattr(FormDialog,'exec_',lambda self:QDialog.Rejected)
    page.create_record();assert repository.rows=={}
