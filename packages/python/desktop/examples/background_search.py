"""Latest-request search with cooperative cancellation and Qt-safe results."""
import sys
from PyQt5.QtCore import QCoreApplication,QEvent
from PyQt5.QtWidgets import QApplication,QLabel,QPushButton,QVBoxLayout,QWidget
from ctf_desktop.background import BackgroundTaskRunner
from ctf_desktop.filters import LiveSearchComboBox


class SearchPanel(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.combo=LiveSearchComboBox(delay_ms=40,parent=self)
        self.status=QLabel('Type to search; previous requests are superseded.',self)
        self.runner=BackgroundTaskRunner(self)
        self.combo.request_started.connect(self.search)
        self.runner.succeeded.connect(self.deliver)
        self.runner.failed.connect(lambda identity,error:self.status.setText(f'Failed: {type(error).__name__}'))
        self.runner.timed_out.connect(lambda identity:self.status.setText('Timed out; late result ignored.'))
        cancel=QPushButton('Cancel',self);cancel.clicked.connect(self.runner.cancel)
        layout=QVBoxLayout(self);layout.addWidget(self.combo);layout.addWidget(self.status);layout.addWidget(cancel)
        self.delivered=[]

    def search(self,request_id,query):
        # Capture query on GUI thread; no widget access from the operation.
        def fetch(cancel_event):
            if cancel_event.wait(0.08):return request_id,query,[]
            return request_id,query,[(1,query+' result')]
        self.runner.submit(fetch,timeout_ms=1000)
        self.status.setText('Searching…')

    def deliver(self,identity,payload):
        request_id,query,rows=payload
        if self.combo.set_results(query,rows,request_id=request_id):
            self.delivered.append(query)
            self.status.setText(f'{len(rows)} result(s)')

    def dispose(self):
        self.runner.close()


def main():
    app=QApplication.instance() or QApplication([])
    panel=SearchPanel();panel.resize(520,200)
    try:
        if '--smoke' in sys.argv:
            from PyQt5.QtTest import QTest
            QTest.keyClicks(panel.combo.lineEdit(),'sample')
            for i in range(100):
                if panel.delivered:break
                QTest.qWait(10)
            assert panel.delivered==['sample']
            print('Background search smoke passed: request identity and Qt delivery.')
        else:
            panel.show();app.exec_()
    finally:
        panel.dispose();panel.close();panel.deleteLater()
        QCoreApplication.sendPostedEvents(None,QEvent.DeferredDelete)
        app.processEvents();app.quit()


if __name__=='__main__':main()
