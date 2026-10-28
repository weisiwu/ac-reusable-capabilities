"""Execute the guide and contract examples; use --qt for Qt-dependent pages too."""
import os
import re
import sys
from pathlib import Path

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
app = None
if '--qt' in sys.argv:
    from PyQt5.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
count = 0
try:
    docs = Path(__file__).resolve().parents[1] / 'docs'
    pages = sorted(path for kind in ('guides', 'contracts') for path in (docs / kind).glob('*.md'))
    for path in pages:
        source = path.read_text()
        if re.search(r'^required_extra:\s*qt\s*$', source.split('---', 2)[1], re.M) and app is None:
            continue
        for code in re.findall(r'```python\n(.*?)```', source, re.S):
            try:
                exec(compile(code, str(path), 'exec'), {})
                count += 1
            finally:
                if app is not None:
                    from PyQt5.QtCore import QCoreApplication, QEvent
                    for widget in app.topLevelWidgets():
                        widget.close()
                        widget.deleteLater()
                    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
                    app.processEvents()
finally:
    if app is not None:
        app.quit()
print(f'{count} documented examples passed')
