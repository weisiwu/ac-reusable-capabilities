"""Build the Pages demo using only public repository catalogs and static files."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]


def _build(output, repository, revision):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
        raise ValueError('repository must be owner/name')
    if not revision or any(char in revision for char in '\r\n'):
        raise ValueError('revision must be nonempty')
    base = f'https://github.com/{repository}/blob/{quote(revision, safe="")}/'
    def link(path):
        target = (ROOT / path).resolve()
        if not target.is_relative_to(ROOT) or not target.is_file():
            raise ValueError(f'missing public source file: {path}')
        return base + quote(path, safe='/')
    catalog = json.loads((ROOT / 'catalog.json').read_text(encoding='utf-8'))
    demo_catalog = json.loads((ROOT / 'demo/catalog.json').read_text(encoding='utf-8'))
    capabilities = []
    packages = {item['id']: item for item in catalog['packages']}
    for package in packages.values():
        for item in package['capabilities']:
            capabilities.append(dict(id=item['id'], name=item['name'], package=package['id'],
                                     modules=item['modules'], guide=link(item['guide']),
                                     contract=link(item['contract']), source=link(f"{package['path']}/src/{package['import_package']}/{item['modules'][0]}.py")))
    demos = []
    for item in demo_catalog['demos']:
        package = packages[item['package_id']]
        extra = '[qt]' if 'PyQt5' in item['dependencies'] else ''
        demos.append(dict(id=item['id'], title=item['title'], package=item['package_id'],
                          command=f"python demo/run.py {item['id']}",
                          install=f"python -m pip install './{package['path']}{extra}'",
                          smoke=bool(item['smoke_args']), source=link(item['script']), guide=link(item['guide'])))
    data = dict(repository=f'https://github.com/{repository}', revision=revision, capabilities=capabilities, demos=demos,
                docs=link('docs/README.md'), wiki=link('wiki/Home.md'), demoGuide=link('demo/README.md'))
    output = Path(output).resolve()
    if output == ROOT or output in ROOT.parents or output.is_relative_to(ROOT / 'site'):
        raise ValueError('output must not overwrite source files')
    (output / 'assets').mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / 'site/index.html', output / 'index.html')
    for name in ('style.css', 'app.mjs', 'models.mjs'):
        shutil.copyfile(ROOT / 'site/assets' / name, output / 'assets' / name)
    payload = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
    (output / 'data.js').write_text('window.AC_DATA = ' + payload + ';\n', encoding='utf-8')
    (output / '.nojekyll').touch()
    print(f'Pages built: {len(capabilities)} capabilities, {len(demos)} demos → {output}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist/pages')
    parser.add_argument('--repository', default=os.environ.get('GITHUB_REPOSITORY', 'weisiwu/ac-reusable-capabilities'))
    parser.add_argument('--ref', default=os.environ.get('GITHUB_SHA', 'main'))
    args = parser.parse_args()
    _build(args.output, args.repository, args.ref)
