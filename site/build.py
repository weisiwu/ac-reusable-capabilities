"""Build the Pages demo using only public repository catalogs and static files."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import sys
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
from docs_build import build_docs, canonical_document_path, document_path

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
    packages = {item['id']: item for item in catalog['packages']}
    origins = {item['id']: dict(id=item['id'], name=item['name'], provenance=link(item['provenance']))
               for item in catalog.get('origins', [])}
    demos = []
    demo_ids = set()
    for item in demo_catalog['demos']:
        if item['id'] in demo_ids or item['package_id'] not in packages:
            raise ValueError('duplicate demo or unknown package')
        demo_ids.add(item['id'])
        if item.get('mode') not in ('local', 'documentation'):
            raise ValueError('demo mode must be local or documentation')
        if item['mode'] == 'local' and (not item.get('runtime') or not item.get('command')):
            raise ValueError('local demo must declare runtime and command')
        demos.append(dict(id=item['id'], title=item['title'], package=item['package_id'],
                          runtime=item.get('runtime', ''), mode=item['mode'],
                          command=item.get('command', ''), install=item.get('install', ''),
                          smoke_command=item.get('smoke_command'),
                          source=link(item['script']) if item.get('script') else None,
                          guide=link(item['guide'])))
    capabilities = []
    capability_ids = set()
    package_data = []
    for package in packages.values():
        package_data.append(dict(id=package['id'], language=package['language'], domain=package['domain'],
                                 version=package['version'], license=package.get('license', ''),
                                 readme=link(package['readme'])))
        for item in package['capabilities']:
            if item['id'] in capability_ids:
                raise ValueError('duplicate capability id')
            capability_ids.add(item['id'])
            if not item.get('sources') or not item.get('summary') or not item.get('kind'):
                raise ValueError('capability requires sources, summary and kind')
            registered_demos = item.get('demo_ids', [])
            if any(identity not in demo_ids for identity in registered_demos):
                raise ValueError('capability references unknown demo')
            source_ids = item.get('origin_ids', package.get('origin_ids', []))
            if any(identity not in origins for identity in source_ids):
                raise ValueError('capability references unknown origin')
            capabilities.append(dict(id=item['id'], name=item['name'], package=package['id'],
                                     language=package['language'], domain=package['domain'],
                                     kind=item['kind'], summary=item['summary'], tags=item.get('tags', []),
                                     origin_ids=source_ids, demo_ids=registered_demos,
                                     modules=item.get('modules', []), guide=link(item['guide']),
                                     contract=link(item['contract']), sources=[link(path) for path in item['sources']],
                                     source=link(item['sources'][0])))
    scenes_path = ROOT / 'site/demos.json'
    scenes = json.loads(scenes_path.read_text(encoding='utf-8'))['scenes'] if scenes_path.is_file() else []
    renderers = set()
    for scene in scenes:
        if scene['renderer'] not in ('table', 'form', 'search', 'redact') or scene['renderer'] in renderers:
            raise ValueError('unknown or duplicate browser renderer')
        if scene['capability_id'] not in capability_ids or (scene.get('demo_id') and scene['demo_id'] not in demo_ids):
            raise ValueError('browser scene references unknown capability or demo')
        renderers.add(scene['renderer'])
    for capability in capabilities:
        local = any(demo['id'] in capability['demo_ids'] and demo['mode'] == 'local' for demo in demos)
        browser = any(scene['capability_id'] == capability['id'] for scene in scenes)
        capability['modes'] = ['documentation'] + (['local'] if local else []) + (['browser'] if browser else [])
    data = dict(repository=f'https://github.com/{repository}', revision=revision, packages=package_data,
                capabilities=capabilities, demos=demos, origins=list(origins.values()), browserDemos=scenes,
                docs=document_path('docs/README.md'), wiki=document_path('wiki/Home.md'),
                sourceWiki=link('wiki/Home.md'), sourceDocs=link('docs/README.md'),
                demoGuide=document_path('demo/README.md'))
    output = Path(output).resolve()
    if output == ROOT or output in ROOT.parents or output.is_relative_to(ROOT / 'site'):
        raise ValueError('output must not overwrite source files')
    (output / 'assets').mkdir(parents=True, exist_ok=True)
    public_docs = build_docs(ROOT, output, list(packages.values()), repository, revision)
    def reading_link(source):
        if source not in public_docs:
            raise ValueError(f'missing public documentation: {source}')
        return quote(canonical_document_path(source), safe='/')
    for item, original in zip(capabilities, (capability for package in packages.values() for capability in package['capabilities'])):
        item['guide'] = reading_link(original['guide'])
        item['contract'] = reading_link(original['contract'])
    for demo, original in zip(demos, demo_catalog['demos']):
        demo['guide'] = reading_link(original['guide'])
    shutil.copyfile(ROOT / 'site/index.html', output / 'index.html')
    for name in ('style.css', 'app.mjs', 'models.mjs', 'favicon.svg'):
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
