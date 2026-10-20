"""Verify Pages artifacts and links without installing desktop dependencies."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PagesTests(unittest.TestCase):
    def test_build_uses_real_catalogs_and_revision_pinned_links(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'pages'
            revision = 'a' * 40
            result = subprocess.run([sys.executable, str(ROOT / 'site/build.py'), '--output', str(output), '--ref', revision],
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            raw = (output / 'data.js').read_text(encoding='utf-8')
            data = json.loads(raw.removeprefix('window.AC_DATA = ').strip().removesuffix(';'))
            packages = json.loads((ROOT / 'catalog.json').read_text())['packages']
            self.assertEqual(len(data['capabilities']), sum(len(p['capabilities']) for p in packages))
            self.assertEqual(len(data['demos']), len(json.loads((ROOT / 'demo/catalog.json').read_text())['demos']))
            self.assertIn(f'/blob/{revision}/', data['wiki'])
            for relative in ['index.html', 'assets/app.mjs', 'assets/models.mjs', 'assets/style.css', '.nojekyll']:
                self.assertTrue((output / relative).is_file(), relative)
            self.assertNotIn(str(ROOT), raw)
            self.assertNotIn('/assets/', (output / 'index.html').read_text().replace('./assets/', ''))

    def test_invalid_repository_rejected_before_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'pages'
            result = subprocess.run([sys.executable, str(ROOT / 'site/build.py'), '--output', str(output),
                                     '--repository', 'https://unexpected.example'], capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())
