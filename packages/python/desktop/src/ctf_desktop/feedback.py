"""Reusable desktop feedback widgets with caller-owned wording."""

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QLabel, QMessageBox, QVBoxLayout, QWidget


class ConfirmDialog:
    """GUI-thread yes/no confirmation wrapper; caller supplies wording, default response No.

    @ac-reusable
    @ac-capability desktop.feedback.ConfirmDialog
    @ac-kind component
    @ac-tags desktop, feedback, ConfirmDialog
    @ac-contract GUI-thread yes/no confirmation wrapper; caller supplies wording, default response No.
    @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
    @ac-example See examples/desktop_demo.py and docs/contracts/feedback.md.
    @ac-tests tests/test_qt.py and tests/test_qt_contracts.py
    """
    @staticmethod
    def ask(parent: QWidget | None, title: str, message: str) -> bool:
        """Block in Qt question dialog; return true only for Yes, false otherwise; parent/title/message are caller-owned.

        @ac-reusable
        @ac-capability desktop.feedback.ConfirmDialog.ask
        @ac-kind function
        @ac-tags desktop, feedback, ConfirmDialog
        @ac-contract Block in Qt question dialog; return true only for Yes, false otherwise; parent/title/message are caller-owned.
        @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
        @ac-example See examples/desktop_demo.py and docs/contracts/feedback.md.
        @ac-tests tests/test_qt.py and tests/test_qt_contracts.py
        """
        return QMessageBox.question(
            parent, title, message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        ) == QMessageBox.Yes


class EmptyState(QWidget):
    """GUI-thread static title/detail labels, empty detail default; parent owns lifetime.

    @ac-reusable
    @ac-capability desktop.feedback.EmptyState
    @ac-kind component
    @ac-tags desktop, feedback, EmptyState
    @ac-contract GUI-thread static title/detail labels, empty detail default; parent owns lifetime.
    @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
    @ac-example See examples/desktop_demo.py and docs/contracts/feedback.md.
    @ac-tests tests/test_qt.py and tests/test_qt_contracts.py
    """
    def __init__(self, title: str, detail: str = "", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.title_label = QLabel(title, self)
        self.detail_label = QLabel(detail, self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.detail_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        layout.addWidget(self.detail_label)


class BusyOverlay(QWidget):
    """GUI-thread child overlay initially hidden; no background work or cancellation; caller hides/closes it.

    @ac-reusable
    @ac-capability desktop.feedback.BusyOverlay
    @ac-kind component
    @ac-tags desktop, feedback, BusyOverlay
    @ac-contract GUI-thread child overlay initially hidden; no background work or cancellation; caller hides/closes it.
    @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
    @ac-example See examples/desktop_demo.py and docs/contracts/feedback.md.
    @ac-tests tests/test_qt.py and tests/test_qt_contracts.py
    """
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background: rgba(0, 0, 0, 90); color: white;")
        self.label = QLabel("", self)
        self.label.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        self.hide()

    def show_message(self, message: str) -> None:
        """Set wording, cover current parent rect and show/raise; caller must refresh geometry after later parent resize.

        @ac-reusable
        @ac-capability desktop.feedback.BusyOverlay.show_message
        @ac-kind function
        @ac-tags desktop, feedback, BusyOverlay
        @ac-contract Set wording, cover current parent rect and show/raise; caller must refresh geometry after later parent resize.
        @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
        @ac-example See examples/desktop_demo.py and docs/contracts/feedback.md.
        @ac-tests tests/test_qt.py and tests/test_qt_contracts.py
        """
        self.label.setText(message)
        self.setGeometry(self.parentWidget().rect())
        self.raise_()
        self.show()


class Toast(QLabel):
    """GUI-thread label initially hidden; parent owns it; fixed-style temporary feedback.

    @ac-reusable
    @ac-capability desktop.feedback.Toast
    @ac-kind component
    @ac-tags desktop, feedback, Toast
    @ac-contract GUI-thread label initially hidden; parent owns it; fixed-style temporary feedback.
    @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
    @ac-example See examples/desktop_demo.py and docs/contracts/feedback.md.
    @ac-tests tests/test_qt.py and tests/test_qt_contracts.py
    """
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background: #25334a; color: white; padding: 8px;")
        self.hide()

    def show_message(self, message: str, duration_ms: int = 3000) -> None:
        """Show centered-top wording and schedule hide after duration_ms=3000; older timers are not reset, so overlapping calls may hide earlier.

        @ac-reusable
        @ac-capability desktop.feedback.Toast.show_message
        @ac-kind function
        @ac-tags desktop, feedback, Toast
        @ac-contract Show centered-top wording and schedule hide after duration_ms=3000; older timers are not reset, so overlapping calls may hide earlier.
        @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
        @ac-example See examples/desktop_demo.py and docs/contracts/feedback.md.
        @ac-tests tests/test_qt.py and tests/test_qt_contracts.py
        """
        self.setText(message)
        self.adjustSize()
        parent = self.parentWidget()
        self.move(max(0, (parent.width() - self.width()) // 2), 12)
        self.raise_()
        self.show()
        QTimer.singleShot(duration_ms, self.hide)
