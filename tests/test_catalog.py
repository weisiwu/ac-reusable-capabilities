"""Catalog validation must still reject bad inputs under python -O."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/check_catalog.py'


class CatalogTests(unittest.TestCase):
    def test_invalid_schema_rejected_with_optimization(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory)/'catalog.json').write_text(json.dumps({'schema_version': 2, 'packages': []}))
            for flags in ([], ['-O']):
                result = subprocess.run([sys.executable, *flags, str(SCRIPT), '--root', directory], capture_output=True, text=True, timeout=10)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('ValueError', result.stderr)

    def test_valid_repository_in_normal_and_optimized_mode(self):
        for flags in ([], ['-O']):
            result = subprocess.run([sys.executable, *flags, str(SCRIPT)], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('public interfaces', result.stdout)


class DocumentationTests(unittest.TestCase):
    def test_missing_link_is_rejected(self):
        script=SCRIPT.with_name('check_docs.py')
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory)/'README.md').write_text('[missing](missing.md)')
            result=subprocess.run([sys.executable,str(script),'--root',directory],capture_output=True,text=True,timeout=10)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('missing.md',result.stderr)
