"""Check repository-relative Markdown links without importing package code."""
import argparse
from pathlib import Path
import re
from urllib.parse import unquote


def check(root):
    failures=[]
    files=[]
    excluded={'.git','.project-context','.venv','build','dist','__pycache__'}
    for path in root.rglob('*.md'):
        if any(part in excluded or part.endswith('.egg-info') for part in path.relative_to(root).parts):continue
        files.append(path)
        for raw in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
            target=raw.strip().strip('<>')
            if target.startswith(('http:','https:','mailto:','#')):continue
            target=unquote(target.split('#',1)[0])
            if not target:continue
            resolved=(path.parent/target).resolve()
            if not resolved.is_relative_to(root) or not resolved.exists():
                failures.append(f'{path.relative_to(root)}: {raw}')
    if failures:raise ValueError('Broken/local-outside links:\n'+'\n'.join(failures))
    print(f'Documentation links valid: {len(files)} Markdown files')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    check(parser.parse_args().root.resolve())
