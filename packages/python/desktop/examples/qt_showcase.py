"""Interactive capability showcase; --smoke exercises every page and exits."""
import sys
from PyQt5.QtCore import QCoreApplication, QEvent
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget

from ctf_desktop.auth import AccessPolicy, Principal
from ctf_desktop.crud import CrudController
from ctf_desktop.crud_page import CrudPage
from ctf_desktop.feedback import BusyOverlay, EmptyState, Toast
from ctf_desktop.filters import FilterField, FilterPanel, LiveSearchComboBox
from ctf_desktop.forms import FieldSpec, FormDialog
from ctf_desktop.navigation import PageHost, PageSpec
from ctf_desktop.query import PageRequest, PageResult
from ctf_desktop.table import Column, PagedTable
from desktop_demo import Inventory
from background_search import SearchPanel


def table_page():
    widget = PagedTable([Column('id','ID'), Column('name','Name')], page_size=2)
    def fetch(request):
        rows = tuple({'id':i,'name':f'Item {i}'} for i in range(1,6))
        widget.set_page(PageResult(rows[request.offset:request.offset+request.size], len(rows), request))
    widget.page_requested.connect(fetch)
    fetch(PageRequest(1,2))
    return widget


def form_page():
    widget=QWidget();layout=QVBoxLayout(widget)
    label=QLabel('Open the form, submit valid values, or cancel.',widget)
    button=QPushButton('Edit sample',widget)
    def edit():
        dialog=FormDialog('Sample',[FieldSpec('name','Name',required=True)],{'name':'Example'},widget)
        try:
            dialog.submitted.connect(lambda values:label.setText(values['name']))
            dialog.exec_()
        finally:
            dialog.deleteLater()
    button.clicked.connect(edit);layout.addWidget(label);layout.addWidget(button)
    return widget


def filter_page():
    widget=QWidget();layout=QVBoxLayout(widget)
    filters=FilterPanel([FilterField('name','Name'),FilterField('created','Created',kind='date_range')],widget)
    combo=LiveSearchComboBox(parent=widget)
    label=QLabel('Type a word to search locally.',widget)
    # This provider is synchronous. Real async providers must discard superseded generations.
    combo.search_requested.connect(lambda query:combo.set_results(query,[(1,query+' result')]))
    filters.search_requested.connect(lambda values:label.setText(str(values)))
    layout.addWidget(filters);layout.addWidget(combo);layout.addWidget(label)
    return widget


def feedback_page():
    widget=QWidget();layout=QVBoxLayout(widget)
    layout.addWidget(EmptyState('No records','Create one in the CRUD page.',widget))
    toast=Toast(widget);overlay=BusyOverlay(widget)
    button=QPushButton('Show message',widget)
    button.clicked.connect(lambda:toast.show_message('Example complete',1200))
    layout.addWidget(button)
    return widget


def crud_page():
    repo=Inventory();repo.create({'name':'Editable sample'})
    principal=Principal('example-editor',frozenset({'editor'}))
    policy=AccessPolicy(lambda actor,action,resource:'editor' in actor.roles)
    controller=CrudController(repo,authorize=lambda action,resource:policy.require(principal,action,resource))
    widget=CrudPage(controller,identity_key='id',columns=[Column('id','ID'),Column('name','Name')],fields=[FieldSpec('name','Name',required=True)])
    status=QLabel(widget)
    widget.operation_failed.connect(lambda action,error:status.setText(f'{action} failed: {type(error).__name__}'))
    widget.layout().addWidget(status)
    widget.load_page()
    return widget


def main():
    app=QApplication.instance() or QApplication([])
    host=PageHost();host.resize(800,560);host.setWindowTitle('Reusable desktop capabilities')
    pages=[('table','Table',table_page),('forms','Form',form_page),('filters','Filters',filter_page),('feedback','Feedback',feedback_page),('crud','CRUD',crud_page),('background','Async search',SearchPanel)]
    for key,title,factory in pages:host.register(PageSpec(key,title,factory))
    try:
        host.navigate('table')
        if '--smoke' in sys.argv:
            for key,title,factory in pages:
                page=host.navigate(key)
                assert host.stack.currentWidget() is page
                app.processEvents()
            assert host.navigate('table').model.rowCount()==2
            print('Qt showcase smoke passed: six pages and lifecycle navigation.')
        else:
            host.show()
            app.exec_()
    finally:
        host.dispose();host.close();host.deleteLater()
        QCoreApplication.sendPostedEvents(None,QEvent.DeferredDelete)
        app.processEvents();app.quit()


if __name__=='__main__':main()
