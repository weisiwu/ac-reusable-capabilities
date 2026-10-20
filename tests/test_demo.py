"""Demo discovery must work before optional packages are installed."""
import copy
import json
from pathlib import Path
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'demo/run.py'


class DemoTests(unittest.TestCase):
    def test_discovery_and_validation_from_other_working_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            for option, expected in [('--list', 'desktop-search'), ('--check', '6 entries')]:
                result = subprocess.run([sys.executable, '-S', str(SCRIPT), option], cwd=directory,
                                        capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(expected, result.stdout)

    def test_missing_dependencies_explain_install_without_traceback(self):
        result = subprocess.run([sys.executable, '-S', str(SCRIPT), 'desktop-core'],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 1)
        self.assertIn('Missing dependencies: ctf_desktop', result.stderr)
        self.assertIn('-m pip install', result.stderr)
        self.assertNotIn('Traceback', result.stderr)

    def test_invalid_run_modes_do_not_launch_examples(self):
        for args in [('unknown',), ('desktop-core', '--smoke'), ('desktop-ui', '--list'), ('--smoke',)]:
            result = subprocess.run([sys.executable, '-S', str(SCRIPT), *args],
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertNotIn('Traceback', result.stderr)

    def test_catalog_rejects_broken_registration(self):
        spec = importlib.util.spec_from_file_location('demo_runner', SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        loader = module._catalog
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / 'demo').mkdir()
            (root / 'example.py').touch()
            (root / 'guide.md').touch()
            (root / 'catalog.json').write_text(json.dumps({'packages': [{'id': 'python.example'}]}))
            entry = dict(id='example', title='Example', package_id='python.example', script='example.py',
                         guide='guide.md', args=[], dependencies=[], smoke_args=None)
            valid = dict(schema_version=1, demos=[entry])
            cases = []
            for key, value in [('package_id', 'missing'), ('script', '../outside.py'),
                               ('guide', 'missing.md'), ('args', '--invalid'), ('smoke_args', [False])]:
                case = copy.deepcopy(valid)
                case['demos'][0][key] = value
                cases.append(case)
            cases.extend([dict(schema_version=1, demos=[entry, entry]),
                          dict(schema_version=1, demos=[{}]), [], dict(schema_version=True, demos=[entry])])
            with patch.dict(loader.__globals__, ROOT=root):
                (root / 'demo/catalog.json').write_text(json.dumps(valid))
                self.assertEqual(set(loader()), {'example'})
                for case in cases:
                    (root / 'demo/catalog.json').write_text(json.dumps(case))
                    with self.subTest(case=case), self.assertRaises(ValueError):
                        loader()

    def test_non_python_and_documentation_entries_are_discoverable_not_executed(self):
        import contextlib
        import io
        spec = importlib.util.spec_from_file_location('demo_runner_generic', SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / 'demo').mkdir()
            (root / 'example.mjs').touch()
            (root / 'guide.md').touch()
            (root / 'catalog.json').write_text(json.dumps({'packages':[{'id':'typescript.frontend'}]}))
            entry = dict(id='node-example',title='Node example',package_id='typescript.frontend',
                         runtime='node',mode='local',command='node example.mjs',script='example.mjs',
                         guide='guide.md',args=[],dependencies=[],smoke_args=None)
            docs = dict(id='docs-example',title='Contract',package_id='typescript.frontend',mode='documentation',guide='guide.md')
            (root / 'demo/catalog.json').write_text(json.dumps(dict(schema_version=1,demos=[entry,docs])))
            module.ROOT = root
            self.assertEqual(set(module._catalog()), {'node-example','docs-example'})
            for identity, expected in [('node-example','node example.mjs'),('docs-example','guide.md')]:
                stderr = io.StringIO()
                with patch.object(sys,'argv',[str(SCRIPT),identity]), patch.object(module.os,'execv') as execute:
                    with contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit) as failure:
                        module._main()
                    self.assertEqual(failure.exception.code,1)
                    self.assertIn(expected,stderr.getvalue())
                    execute.assert_not_called()
