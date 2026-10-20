import pytest
pytest.importorskip('PyQt5')
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication, QDialog, QDialogButtonBox, QWidget

from ctf_desktop.feedback import BusyOverlay, Toast
from ctf_desktop.filters import FilterField, FilterPanel, LiveSearchComboBox
from ctf_desktop.forms import FieldSpec, FormDialog
from ctf_desktop.navigation import PageHost, PageSpec
from ctf_desktop.table import Column, RecordTableModel


def test_form_preserves_zero_false_text_and_rejects_duplicate_keys(qapp):
    fields = [FieldSpec('zero','Zero'), FieldSpec('false','False',kind='multiline')]
    dialog = FormDialog('Sample', fields, {'zero':0,'false':False})
    assert dialog.values() == {'zero':'0','false':'False'}
    with pytest.raises(ValueError): FormDialog('Sample',[FieldSpec('x','X'),FieldSpec('x','Again')])
    with pytest.raises(ValueError): FilterPanel([FilterField('x','X'),FilterField('x','Again')])


def test_live_search_preserves_signal_block_state_and_rejects_invalid_results_before_mutation(qapp):
    combo = LiveSearchComboBox(); combo.setEditText('same')
    combo.blockSignals(True)
    assert combo.set_results('same', [(1,'One')])
    assert combo.signalsBlocked()
    combo.blockSignals(False)
    with pytest.raises(ValueError): combo.set_results('same', [(2,'Two'), (3,)])
    assert not combo.signalsBlocked() and combo.count() == 1
    combo.hidePopup()


def test_navigation_disposes_every_page_even_if_one_hook_fails(qapp):
    cleaned = []
    class Broken(QWidget):
        def dispose(self): raise ValueError('failure')
    class Good(QWidget):
        def dispose(self): cleaned.append('good')
    host = PageHost()
    host.register(PageSpec('bad','Bad',Broken));host.register(PageSpec('good','Good',Good))
    host.navigate('bad');host.navigate('good')
    with pytest.raises(RuntimeError):host.dispose()
    assert cleaned == ['good'] and host.stack.count() == 0
    host.dispose()


def test_failed_first_navigation_does_not_leave_failed_page_visible(qapp):
    class Broken(QWidget):
        def on_enter(self): raise ValueError('failed enter')
    host=PageHost();host.register(PageSpec('bad','Bad',Broken))
    with pytest.raises(ValueError):host.navigate('bad')
    assert host.stack.count() == 0
    host.dispose()


def test_table_reset_failure_does_not_leave_model_in_reset(qapp):
    model=RecordTableModel([Column('id','ID')]);model.set_records([{'id':1}])
    signals=[];model.modelAboutToBeReset.connect(lambda:signals.append('begin'));model.modelReset.connect(lambda:signals.append('end'))
    with pytest.raises(TypeError):model.set_records([None])
    assert signals == [] and model.data(model.index(0,0))=='1'
    model.set_records([{'id':2}]);assert signals==['begin','end']
    assert model.headerData(-1,Qt.Horizontal) is None


def test_toast_restarts_timeout_instead_of_old_timer_hiding_new_message(qapp):
    parent=QWidget();parent.show()
    toast=Toast(parent);toast.show_message('first',40)
    QTest.qWait(25);toast.show_message('second',120)
    QTest.qWait(35)
    assert toast.isVisible() and toast.text()=='second'
    QTest.qWait(120);assert not toast.isVisible()


def test_busy_overlay_tracks_parent_resize(qapp):
    parent=QWidget();parent.resize(300,200);parent.show()
    overlay=BusyOverlay(parent);overlay.show_message('busy')
    parent.resize(420,320);qapp.processEvents()
    assert overlay.geometry()==parent.rect()


def test_form_validation_callback_failure_is_reported_without_escaping(qapp):
    def broken(value):raise RuntimeError('validator unavailable')
    dialog=FormDialog('Sample',[FieldSpec('name','Name',validate=broken)],{'name':'sample'})
    failures=[]
    dialog.validation_failed.connect(failures.append)
    dialog._submit()
    assert len(failures)==1 and isinstance(failures[0],RuntimeError)
    assert dialog.result()!=QDialog.Accepted and dialog.error_label.text()


def test_crud_missing_identity_is_reported_instead_of_escaping(qapp,monkeypatch):
    from ctf_desktop.crud import CrudController
    from ctf_desktop.crud_page import CrudPage
    from ctf_desktop.query import PageRequest,PageResult
    controller=CrudController(object(),authorize=lambda *args:None)
    page=CrudPage(controller,identity_key='id',columns=[Column('name','Name')],fields=[FieldSpec('name','Name')])
    page.table.set_page(PageResult(({'name':'missing identity'},),1,PageRequest()))
    page.table.table.selectRow(0)
    failures=[];page.operation_failed.connect(lambda *args:failures.append(args))
    page.edit_selected();page.show_detail();page.delete_selected()
    assert [action for action,error in failures]==['update','read','delete']
    assert all(isinstance(error,ValueError) for action,error in failures)


def test_crud_repeated_cancel_does_not_retain_modal_children(qapp,monkeypatch):
    from ctf_desktop.crud import CrudController
    from ctf_desktop.crud_page import CrudPage
    from PyQt5.QtCore import QCoreApplication,QEvent
    page=CrudPage(CrudController(object(),authorize=lambda *args:None),identity_key='id',columns=[Column('id','ID')],fields=[FieldSpec('name','Name')])
    monkeypatch.setattr(FormDialog,'exec_',lambda self:QDialog.Rejected)
    for i in range(4):page.create_record()
    QCoreApplication.sendPostedEvents(None,QEvent.DeferredDelete)
    assert page.findChildren(FormDialog)==[]


def test_navigation_sidebar_reports_hook_error_and_reentry_is_rejected(qapp):
    host=PageHost();errors=[]
    class Good(QWidget):pass
    class Broken(QWidget):
        def on_enter(self):raise ValueError('failed')
    class Reenter(QWidget):
        def on_enter(self):host.navigate('good')
    host.register(PageSpec('good','Good',Good));host.register(PageSpec('broken','Broken',Broken));host.register(PageSpec('reenter','Reenter',Reenter))
    good=host.navigate('good');host.navigation_failed.connect(lambda *args:errors.append(args))
    host._on_row_changed(1)
    assert errors[0][0]=='broken' and isinstance(errors[0][1],ValueError)
    assert host.stack.currentWidget() is good
    with pytest.raises(RuntimeError,match='reentry'):host.navigate('reenter')
    assert host.stack.currentWidget() is good
    host.dispose()
