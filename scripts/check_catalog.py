"""Validate registered paths, module ownership and searchable public contracts.

Uses only the standard library and AST; never imports optional GUI/hardware code.
"""
import ast
import json
import re
import tomllib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
TAGS = ('@ac-reusable', '@ac-capability', '@ac-kind', '@ac-tags', '@ac-contract', '@ac-dependencies', '@ac-example', '@ac-tests')

def owned_path(value):
    relative = Path(value)
    if not (not relative.is_absolute() and '..' not in relative.parts):
        raise ValueError(f'unsafe path: {value}')
    path = ROOT / relative
    if not (path.exists() and (not path.is_symlink())):
        raise ValueError(f'missing or linked path: {value}')
    if not path.resolve().is_relative_to(ROOT):
        raise ValueError(f'path escapes repository: {value}')
    return path

def main(root=None):
    global ROOT
    if root is not None:
        ROOT = Path(root).resolve()
    catalog = json.loads((ROOT / 'catalog.json').read_text())
    if not catalog['schema_version'] == 1:
        raise ValueError('invalid catalog')
    ids, interface_ids = (set(), set())
    for package in catalog['packages']:
        if not package['id'] not in ids:
            raise ValueError('duplicate package id')
        ids.add(package['id'])
        expected = f"packages/{package['language']}/{package['domain']}"
        if not package['path'] == expected:
            raise ValueError(f'package layout must be {expected}')
        path = owned_path(package['path'])
        owned_path(package['readme'])
        if 'documentation' in package:
            owned_path(package['documentation'])
        for example in package['examples']:
            owned_path(example)
        if package['language'] != 'python':
            raise ValueError('add an explicit manifest adapter for a new language')
        manifest = tomllib.loads((path / 'pyproject.toml').read_text())['project']
        if not (manifest['name'] == package['distribution'] and manifest['version'] == package['version']):
            raise ValueError('invalid catalog')
        module_names = set()
        for capability in package['capabilities']:
            if not capability['id'] not in ids:
                raise ValueError('duplicate capability id')
            ids.add(capability['id'])
            owned_path(capability['contract'])
            if 'guide' in capability:
                owned_path(capability['guide'])
            for test in capability['tests']:
                owned_path(test)
            module_names.update(capability['modules'])
        source = owned_path(str((path / 'src' / package['import_package']).relative_to(ROOT)))
        init = ast.parse((source / '__init__.py').read_text())
        versions = [ast.literal_eval(node.value) for node in init.body if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == '__version__' for target in node.targets)]
        if versions != [package['version']]:
            raise ValueError('import version differs from package manifest')
        actual = {p.stem for p in source.glob('*.py') if p.stem != '__init__'}
        if not module_names == actual:
            raise ValueError(f'unregistered or missing modules: {module_names ^ actual}')
        for module in sorted(module_names):
            tree = ast.parse((source / f'{module}.py').read_text())
            for node in tree.body:
                if not isinstance(node, (ast.ClassDef, ast.FunctionDef)) or node.name.startswith('_'):
                    continue
                nodes = [node]
                if isinstance(node, ast.ClassDef):
                    nodes += [n for n in node.body if isinstance(n, ast.FunctionDef) and (not n.name.startswith('_'))]
                for public in nodes:
                    doc = ast.get_docstring(public) or ''
                    if not all((tag in doc for tag in TAGS)):
                        raise ValueError(f'missing contract tags: {module}.{public.name}')
                    identity = re.search('@ac-capability\\s+(\\S+)', doc).group(1)
                    if not identity not in interface_ids:
                        raise ValueError(f'duplicate public id: {identity}')
                    interface_ids.add(identity)
    print(f"Catalog valid: {len(catalog['packages'])} package(s), {len(ids) - len(catalog['packages'])} capabilities, {len(interface_ids)} public interfaces")
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    main(args.root)
