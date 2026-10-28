"""Catalog validation must still reject bad inputs under python -O."""
import json
import importlib.util
import tomllib
from unittest.mock import patch
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


class CapabilityPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = SCRIPT.parents[1]
        spec = importlib.util.spec_from_file_location('docs_quality_check', SCRIPT.with_name('check_docs.py'))
        cls.checker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.checker)

    def check_with_replaced_page(self, path, transform):
        read = Path.read_text
        original = read(path, encoding='utf-8')
        def changed(file, *args, **kwargs):
            return transform(original) if file == path else read(file, *args, **kwargs)
        with patch.object(Path, 'read_text', changed):
            self.checker.check_capability_pages(self.root)

    def test_link_only_version_is_rejected_even_when_other_sections_exist(self):
        package = self.root / 'packages/python/desktop'
        version = tomllib.loads((package / 'pyproject.toml').read_text())['project']['version']
        path = package / 'docs/guides/auth.md'
        with self.assertRaisesRegex(ValueError, 'package version must be stated on this page'):
            self.check_with_replaced_page(path, lambda text: text.replace(
                f'| 能力包版本 | `{version}` |', '| 能力包版本 | [仅公共入口](../升级与兼容.md) |'))

    def test_missing_current_source_interface_is_rejected(self):
        path = self.root / 'packages/python/desktop/docs/contracts/auth.md'
        with self.assertRaisesRegex(ValueError, 'undocumented source interfaces'):
            self.check_with_replaced_page(path, lambda text: text.replace(
                '`desktop.auth.PasswordHasher.verify`', '`desktop.auth.Legacy.verify`'))
