"""Reusable desktop feedback widgets with caller-owned wording."""

from PyQt5.QtCore import Qt, QTimer, QEvent, QObject
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
    @ac-tests tests/test_qt.py, tests/test_qt_contracts.py and tests/test_review_qt.py
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
        @ac-tests tests/test_qt.py, tests/test_qt_contracts.py and tests/test_review_qt.py
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
    @ac-tests tests/test_qt.py, tests/test_qt_contracts.py and tests/test_review_qt.py
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


class _ParentResizeFilter(QObject):
    def eventFilter(self, watched, event):
        if event.type() == QEvent.Resize:
            self.parent().setGeometry(watched.rect())
        return False


class BusyOverlay(QWidget):
    """GUI-thread child overlay initially hidden; automatically follows parent resize; caller controls visibility and owns cancellation/work.

    @ac-reusable
    @ac-capability desktop.feedback.BusyOverlay
    @ac-kind component
    @ac-tags desktop, feedback, BusyOverlay
    @ac-contract GUI-thread child overlay initially hidden; automatically follows parent resize; caller controls visibility and owns cancellation/work.
    @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
    @ac-example See examples/desktop_demo.py and docs/contracts/feedback.md.
    @ac-tests tests/test_qt.py, tests/test_qt_contracts.py and tests/test_review_qt.py
    """
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._resize_filter = _ParentResizeFilter(self)
        parent.installEventFilter(self._resize_filter)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background: rgba(0, 0, 0, 90); color: white;")
        self.label = QLabel("", self)
        self.label.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        self.hide()

    def show_message(self, message: str) -> None:
        """Cover parent current rect, set wording and show/raise; parent resize events maintain geometry while widget exists.

        @ac-reusable
        @ac-capability desktop.feedback.BusyOverlay.show_message
        @ac-kind function
        @ac-tags desktop, feedback, BusyOverlay
        @ac-contract Cover parent current rect, set wording and show/raise; parent resize events maintain geometry while widget exists.
        @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
        @ac-example See examples/desktop_demo.py and docs/contracts/feedback.md.
        @ac-tests tests/test_qt.py, tests/test_qt_contracts.py and tests/test_review_qt.py
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
    @ac-tests tests/test_qt.py, tests/test_qt_contracts.py and tests/test_review_qt.py
    """
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.hide)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background: #25334a; color: white; padding: 8px;")
        self.hide()

    def show_message(self, message: str, duration_ms: int = 3000) -> None:
        """Validate nonnegative integer duration_ms=3000 before mutation; show message and restart one owned timer so earlier messages cannot hide newer ones.

        @ac-reusable
        @ac-capability desktop.feedback.Toast.show_message
        @ac-kind function
        @ac-tags desktop, feedback, Toast
        @ac-contract Validate nonnegative integer duration_ms=3000 before mutation; show message and restart one owned timer so earlier messages cannot hide newer ones.
        @ac-dependencies Python >=3.11; PyQt5 >=5.15; all UI calls on Qt event thread.
        @ac-example See examples/desktop_demo.py and docs/contracts/feedback.md.
        @ac-tests tests/test_qt.py, tests/test_qt_contracts.py and tests/test_review_qt.py
        """
        if type(duration_ms) is not int or duration_ms < 0:
            raise ValueError("duration_ms must be a nonnegative integer")
        self.setText(message)
        self.adjustSize()
        parent = self.parentWidget()
        self.move(max(0, (parent.width() - self.width()) // 2), 12)
        self.raise_()
        self.show()
        self._hide_timer.start(duration_ms)
