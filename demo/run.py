"""Discover and run installed-package demos from the versioned demo catalog."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def _file(value):
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        raise ValueError('demo paths must be nonempty repository-relative strings')
    path = (ROOT / value).resolve()
    if not path.is_relative_to(ROOT) or not path.is_file():
        raise ValueError(f'missing or outside-repository demo file: {value}')
    return path


def _catalog():
    data = json.loads((ROOT / 'demo/catalog.json').read_text(encoding='utf-8'))
    if not isinstance(data, dict) or type(data.get('schema_version')) is not int or data.get('schema_version') != 1 or not isinstance(data.get('demos'), list):
        raise ValueError('expected demo catalog schema_version=1 with demos list')
    packages = {item['id'] for item in json.loads((ROOT / 'catalog.json').read_text(encoding='utf-8'))['packages']}
    demos = {}
    for item in data['demos']:
        if not isinstance(item, dict) or not {'id', 'title', 'package_id', 'guide'} <= item.keys():
            raise ValueError('demo entry is missing required fields')
        identity = item.get('id')
        if not isinstance(identity, str) or not identity or identity in demos:
            raise ValueError(f'invalid or duplicate demo id: {identity}')
        if item.get('package_id') not in packages:
            raise ValueError(f'{identity}: unknown package_id')
        if not isinstance(item.get('title'), str) or not item['title']:
            raise ValueError(f'{identity}: title required')
        mode = item.get('mode', 'local')
        if mode not in ('local', 'documentation'):
            raise ValueError(f'{identity}: unsupported demo mode')
        if mode == 'documentation':
            _file(item['guide'])
            demos[identity] = item
            continue
        if not {'script', 'args', 'dependencies', 'smoke_args'} <= item.keys():
            raise ValueError(f'{identity}: local demo is missing run fields')
        script = _file(item.get('script'))
        if item.get('runtime', 'python') == 'python' and script.suffix != '.py':
            raise ValueError(f'{identity}: Python demo requires .py script')
        if item.get('runtime', 'python') != 'python' and not item.get('command'):
            raise ValueError(f'{identity}: non-Python demo requires explicit command')
        _file(item.get('guide'))
        for key in ('args', 'dependencies', 'smoke_args'):
            value = item.get(key)
            if key == 'smoke_args' and value is None:
                continue
            if not isinstance(value, list) or any(not isinstance(part, str) or not part for part in value):
                raise ValueError(f'{identity}: {key} must contain nonempty strings')
        demos[identity] = item
    return demos


def _main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('demo', nargs='?', help='demo ID; use --list for available demos')
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--list', action='store_true', help='list demos without importing optional dependencies')
    modes.add_argument('--check', action='store_true', help='validate demo IDs, package references and file paths')
    parser.add_argument('--smoke', action='store_true', help='automatically exercise and exit a UI demo')
    args = parser.parse_args()
    if (args.list or args.check) and (args.demo or args.smoke):
        parser.error('--list/--check cannot be combined with a demo or --smoke')
    try:
        demos = _catalog()
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, f'Demo catalog invalid: {error}\n')
    if args.check:
        print(f'Demo catalog valid: {len(demos)} entries')
        return
    if args.list:
        for identity, item in demos.items():
            mode = ('documentation' if item.get('mode') == 'documentation' else
                    'run declared command' if item.get('runtime', 'python') != 'python' else
                    'interactive; --smoke supported' if item['smoke_args'] is not None else 'automatic exit')
            print(f"{identity}: {item['title']} [{mode}]")
        return
    if args.demo not in demos:
        parser.error('choose a valid demo ID from --list')
    item = demos[args.demo]
    if item.get('mode') == 'documentation':
        parser.exit(1, f"Documentation demo: {item['guide']}\n")
    if item.get('runtime', 'python') != 'python':
        parser.exit(1, f"This launcher executes Python only. Run the declared command in the repository root:\n  {item['command']}\n")
    if args.smoke and item['smoke_args'] is None:
        parser.error(f'{args.demo} exits automatically and does not accept --smoke')
    missing = [name for name in item['dependencies'] if importlib.util.find_spec(name) is None]
    if missing:
        extra = '[qt]' if 'PyQt5' in item['dependencies'] else ''
        package = next(entry for entry in json.loads((ROOT / 'catalog.json').read_text(encoding='utf-8'))['packages'] if entry['id'] == item['package_id'])
        install_path = ROOT / package['path']
        parser.exit(1, f"Missing dependencies: {', '.join(missing)}\nInstall with the same interpreter:\n  {sys.executable} -m pip install '{install_path}{extra}'\n")
    script = _file(item['script'])
    flags = item['args'] + (item['smoke_args'] if args.smoke else [])
    # Replace this process: demo exit status and interrupt handling stay intact.
    # Import the installed package, never inject its src directory into sys.path.
    os.execv(sys.executable, [sys.executable, str(script), *flags])


if __name__ == '__main__':
    _main()
