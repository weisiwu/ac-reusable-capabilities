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

    def test_non_python_packages_and_documentation_only_capabilities_build(self):
        import importlib.util
        import shutil
        spec = importlib.util.spec_from_file_location('pages_builder', ROOT / 'site/build.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory).resolve() / 'repository'
            fixture.mkdir()
            shutil.copytree(ROOT / 'site', fixture / 'site')
            # Temporary fixtures demonstrate presentation compatibility, not shipped packages.
            (fixture / 'site/demos.json').write_text(json.dumps({'schema_version':1,'scenes':[]}))
            for path in ['docs/README.md','wiki/Home.md','demo/README.md','origins.md',
                         'packages/typescript/frontend/README.md','packages/typescript/frontend/widget.ts',
                         'packages/typescript/frontend/example.mjs','packages/shell/operations/README.md',
                         'packages/shell/operations/task.sh']:
                target = fixture / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text('fixture only')
            packages = []
            for language, domain, source in [('typescript','frontend','widget.ts'),('shell','operations','task.sh')]:
                path = f'packages/{language}/{domain}'
                packages.append(dict(id=f'{language}.{domain}', language=language, domain=domain,
                                     path=path, version='0.0.0', readme=f'{path}/README.md', origin_ids=['fixture'],
                                     capabilities=[dict(id=f'{domain}.example',name='Fixture capability',
                                                        kind='component' if language=='typescript' else 'tool',
                                                        summary='Temporary schema fixture', sources=[f'{path}/{source}'],
                                                        guide=f'{path}/README.md',contract=f'{path}/README.md',
                                                        demo_ids=['node-example'] if language=='typescript' else [])]))
            (fixture / 'catalog.json').write_text(json.dumps(dict(packages=packages,origins=[dict(id='fixture',name='Fixture',provenance='origins.md')])))
            (fixture / 'demo/catalog.json').write_text(json.dumps(dict(demos=[dict(id='node-example',title='Node fixture',
                package_id='typescript.frontend',runtime='node',mode='local',command='node example.mjs',install='npm ci',
                script='packages/typescript/frontend/example.mjs',guide='packages/typescript/frontend/README.md')])))
            module.ROOT = fixture
            output = Path(directory) / 'output'
            module._build(output, 'test/fixture', 'main')
            data = json.loads((output / 'data.js').read_text().removeprefix('window.AC_DATA = ').strip().removesuffix(';'))
            self.assertEqual({item['language'] for item in data['packages']}, {'typescript','shell'})
            self.assertEqual(data['browserDemos'], [])
            self.assertTrue(data['capabilities'][0]['source'].endswith('widget.ts'))
            self.assertEqual(data['capabilities'][1]['modes'], ['documentation'])
            self.assertEqual(data['demos'][0]['command'], 'node example.mjs')
            self.assertEqual(data['demos'][0]['install'], 'npm ci')
            self.assertNotIn('python demo/run.py', (output / 'data.js').read_text())
