"""Check repository-relative Markdown links without importing package code."""
import argparse
import ast
import tomllib
from pathlib import Path
import re
from urllib.parse import unquote


def check_capability_pages(root):
    """Keep current desktop module pages independently usable and tied to their source API."""
    package = root / 'packages/python/desktop'
    source = package / 'src/ctf_desktop'
    if not source.is_dir():
        return 0
    version = tomllib.loads((package / 'pyproject.toml').read_text(encoding='utf-8'))['project']['version']
    required = {'用途与范围', '模块信息', '运行环境', '依赖要求', '版本信息', '兼容要求',
                '安装与导入', '返回值', '信号', '错误与边界', '线程与资源', '验证与源码依据'}
    failures = []
    count = 0
    for module in sorted(source.glob('*.py')):
        text = module.read_text(encoding='utf-8')
        identities = set(re.findall(r'@ac-capability\s+(desktop\.[\w.]+)', text))
        if not identities:
            continue
        tree = ast.parse(text)
        needs_qt = any(isinstance(node, ast.ImportFrom) and (node.module or '').startswith('PyQt5')
                       for node in tree.body)
        for kind in ('guides', 'contracts'):
            path = package / 'docs' / kind / (module.stem + '.md')
            if not path.is_file():
                failures.append(f'{path.relative_to(root)}: missing module page')
                continue
            body = path.read_text(encoding='utf-8')
            label = str(path.relative_to(root))
            headings = set(re.findall(r'^## (.+)$', body, re.M))
            missing = required - headings
            if missing:
                failures.append(f'{label}: missing own-page topics: {", ".join(sorted(missing))}')
            version_row = r'^\|\s*(?:能力)?包版本\s*\|\s*`?' + re.escape(version) + r'`?\s*\|'
            if not re.search(version_row, body, re.M):
                failures.append(f'{label}: package version must be stated on this page ({version})')
            if '```python\n' not in body:
                failures.append(f'{label}: missing an inline runnable example')
            if needs_qt and not re.search(r'^required_extra:\s*qt\s*$', body, re.M):
                failures.append(f'{label}: Qt page must declare required_extra: qt for example checks')
            if re.search(r'^\|\s*(接入项|项目)\s*\|\s*要求 / (用法|行为)\s*\|', body, re.M):
                failures.append(f'{label}: mixed access-summary table must be split by topic')
            if kind == 'contracts':
                undocumented = sorted(identity for identity in identities if f'`{identity}`' not in body)
                if undocumented:
                    failures.append(f'{label}: undocumented source interfaces: {", ".join(undocumented)}')
            count += 1
    if failures:
        raise ValueError('Incomplete capability pages:\n' + '\n'.join(failures))
    return count


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
    pages = check_capability_pages(root)
    print(f'Documentation links valid: {len(files)} Markdown files; {pages} self-contained module pages')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    check(parser.parse_args().root.resolve())
