"""Publish the repository's reviewed Markdown as version-aligned reading pages."""
from html import escape
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
import unicodedata
from urllib.parse import quote, unquote, urlsplit, urlunsplit

import markdown


# Old Markdown files remain lightweight pointers; only these pages own the text.
DOCUMENT_REDIRECTS = {
    'wiki/Home.md': 'docs/README.md',
    'wiki/Getting-Started.md': 'docs/快速开始.md',
    'wiki/Capabilities.md': 'docs/能力地图.md',
    'wiki/Recipes.md': 'docs/组合场景.md',
    'wiki/Compatibility.md': 'docs/版本与兼容.md',
    'wiki/Troubleshooting.md': 'docs/排障指南.md',
    'wiki/Contributing.md': 'docs/能力收录流程.md',
    'wiki/_Sidebar.md': 'docs/README.md',
}

LEGACY_ANCHORS = {
    'docs/README.md': {'能力库 Wiki': '文档中心', 'Wiki 导航': '文档中心',
                       '从你的目标开始': '快速开始', '文档与代码对应': '贡献维护'},
    'docs/快速开始.md': {'上手步骤': '快速开始'},
    'docs/组合场景.md': {'接入场景': '组合场景'},
    'docs/版本与兼容.md': {'版本与兼容选择': '版本与兼容'},
    'docs/排障指南.md': {'常见问题': '排障指南'},
    'docs/能力收录流程.md': {'贡献入口': '贡献导航与文档同步'},
}


def slugify(value, separator='-'):
    value = unicodedata.normalize('NFKC', value).lower()
    value = re.sub(r'[^\w\s-]', '', value)
    return re.sub(r'[-\s]+', separator, value).strip(separator) or 'section'


def markdown_sources(root, packages):
    """Only public documentation roots enter the site; never walk the checkout."""
    root = Path(root).resolve()
    sources = {root / name for name in ('README.md', 'CONTRIBUTING.md', 'demo/README.md', 'site/README.md')}
    directories = [root / 'wiki', root / 'docs']
    for package in packages:
        sources.add(root / package['readme'])
        directories.append(root / package['path'] / 'docs')
    for directory in directories:
        if directory.is_symlink() or not directory.resolve().is_relative_to(root):
            raise ValueError('documentation directory must be inside repository')
        if directory.is_dir():
            sources.update(directory.rglob('*.md'))
    result = []
    for source in sources:
        if source.is_symlink() or not source.resolve().is_relative_to(root):
            raise ValueError('documentation source must be inside repository')
        if source.is_file() and not any(part.startswith('.') for part in source.relative_to(root).parts):
            result.append(source.relative_to(root).as_posix())
    return sorted(result)


def document_path(source):
    return str(Path(source).with_suffix('.html')).replace(os.sep, '/')


def canonical_document_path(source):
    return document_path(DOCUMENT_REDIRECTS.get(source, source))


def relative_url(target, page):
    return quote(os.path.relpath(target, Path(page).parent).replace(os.sep, '/'), safe='/')


class ReadingHTML(HTMLParser):
    """Keep Markdown structure, and resolve links without rewriting code examples."""
    tags = set('p h1 h2 h3 h4 h5 h6 a img ul ol li blockquote pre code table thead tbody tr th td br hr em strong del s div span details summary dl dt dd'.split())
    attributes = {'id', 'class', 'title', 'alt', 'colspan', 'rowspan', 'scope', 'open', 'start'}

    def __init__(self, root, source, sources, base):
        super().__init__(convert_charrefs=False)
        self.root, self.source, self.sources, self.base = root, source, sources, base
        self.output = []
        self.assets = set()

    def resolve_link(self, value, image=False):
        parts = urlsplit(value)
        if parts.scheme or parts.netloc:
            return value if parts.scheme in ('https', 'http', 'mailto') else None
        if not parts.path:
            return value
        target = (self.root / self.source).parent / unquote(parts.path)
        target = target.resolve()
        if not target.is_relative_to(self.root) or not target.exists():
            raise ValueError(f'invalid documentation link in {self.source}: {value}')
        relative = target.relative_to(self.root).as_posix()
        if target.is_dir() and f'{relative}/README.md' in self.sources:
            relative += '/README.md'
        if relative in self.sources:
            path = relative_url(canonical_document_path(relative), document_path(self.source))
        elif image and target.suffix.lower() in ('.png', '.jpg', '.jpeg', '.svg', '.webp', '.gif'):
            self.assets.add(relative)
            path = relative_url(relative, document_path(self.source))
        else:
            path = self.base + quote(relative, safe='/')
        return urlunsplit(('', '', path, parts.query, parts.fragment))

    def handle_starttag(self, tag, attrs):
        if tag not in self.tags:
            return
        kept = []
        for key, value in attrs:
            if key in ('href', 'src') and ((tag == 'a' and key == 'href') or (tag == 'img' and key == 'src')):
                value = self.resolve_link(value or '', image=tag == 'img')
                if value is not None:
                    kept.append((key, value))
            elif key in self.attributes:
                kept.append((key, value or ''))
        self.output.append('<' + tag + ''.join(f' {key}="{escape(value, quote=True)}"' for key, value in kept) + '>')

    def handle_endtag(self, tag):
        if tag in self.tags and tag not in ('img', 'br', 'hr'):
            self.output.append(f'</{tag}>')

    def handle_data(self, data):
        self.output.append(escape(data))

    def handle_entityref(self, name):
        self.output.append('&' + name + ';')

    def handle_charref(self, name):
        self.output.append('&#' + name + ';')


def render_markdown(root, source, sources, base):
    root = Path(root).resolve()
    raw = (root / source).read_text(encoding='utf-8')
    body = re.sub(r'\A---\s*\n.*?\n---\s*\n', '', raw, count=1, flags=re.S)
    parser = markdown.Markdown(extensions=['tables', 'fenced_code', 'sane_lists', 'toc'],
                               extension_configs={'toc': {'slugify': slugify, 'permalink': False}})
    rendered = parser.convert(body)
    cleaner = ReadingHTML(root, source, sources, base)
    cleaner.feed(rendered)
    rendered = ''.join(cleaner.output)
    rendered = re.sub(r'<pre><code class="language-mermaid">(.*?)</code></pre>',
                      lambda match: '<figure class="diagram"><pre class="mermaid">' + match[1]
                      + '</pre><details><summary>查看流程图文本</summary><pre><code>' + match[1]
                      + '</code></pre></details></figure>', rendered, flags=re.S)
    toc = ReadingHTML(root, source, sources, base)
    toc.feed(parser.toc)
    title = next((token['name'] for token in parser.toc_tokens if token['level'] == 1), Path(source).stem)
    title = re.sub(r'<[^>]+>', '', title)
    return title, rendered, ''.join(toc.output), body, cleaner.assets


def legacy_anchors(source, content):
    for previous, current in LEGACY_ANCHORS.get(source, {}).items():
        identity = slugify(previous)
        if f'id="{identity}"' in content:
            continue
        anchor = f'<span id="{identity}" class="legacy-anchor" aria-hidden="true"></span>'
        pattern = r'(<h[1-6] id="' + re.escape(slugify(current)) + r'")'
        if re.search(pattern, content):
            content = re.sub(pattern, lambda match: anchor + match[0], content, count=1)
        else:
            content = anchor + content
    return content


def navigation_groups(documents, packages):
    """Use reader tasks as categories, independent of the Markdown's location."""
    remaining = set(documents)
    groups = []

    def add(label, candidates):
        items = list(dict.fromkeys(source for source in candidates if source in remaining))
        remaining.difference_update(items)
        if items:
            groups.append((label, items))

    package_docs = [source for source in documents
                    if any(source.startswith(item['path'] + '/') for item in packages)]
    add('快速开始', ['docs/README.md', 'docs/快速开始.md', 'docs/能力地图.md']
        + [source for source in package_docs if source.endswith('/快速开始.md')])
    add('能力指南', [item['readme'] for item in packages]
        + [source for source in package_docs if source.endswith('/docs/README.md')]
        + [source for source in documents if '/guides/' in source])
    add('接口参考', [source for source in package_docs if source.endswith('/能力目录.md')]
        + [source for source in documents if '/contracts/' in source])
    environment = {'架构与依赖.md', '升级与兼容.md', '生命周期与线程.md', '安全与数据边界.md',
                   '验证记录.md', '来源与迁入边界.md', '评审与修复记录.md'}
    add('版本兼容', ['docs/版本与兼容.md']
        + [source for source in package_docs if Path(source).name in environment])
    add('组合排障', ['docs/组合场景.md', 'docs/排障指南.md']
        + [source for source in package_docs if source.endswith('/常见问题与排障.md')])
    add('贡献维护', ['docs/能力收录流程.md', 'CONTRIBUTING.md'] + sorted(remaining))
    return groups


def write_redirect(output, previous, current):
    page = document_path(previous)
    destination = relative_url(document_path(current), page)
    prefix = relative_url('index.html', page).removesuffix('index.html')
    html = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; object-src 'none'; base-uri 'none'">
<meta name="robots" content="noindex"><link rel="canonical" href="{destination}">
<noscript><meta http-equiv="refresh" content="0;url={destination}"></noscript>
<title>文档已迁移 · 文档中心</title><link rel="stylesheet" href="{prefix}assets/docs.css">
<link rel="icon" type="image/svg+xml" href="{prefix}assets/favicon.svg"></head>
<body><main class="doc-content"><h1>文档已迁移</h1><p>此页面已归入统一文档中心。</p>
<p><a id="redirect-target" href="{destination}">前往对应文档 →</a></p></main>
<script src="{prefix}assets/redirect.js" defer></script></body></html>'''
    target = output / page
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding='utf-8')


def build_docs(root, output, packages, repository, revision):
    root = Path(root).resolve()
    sources = set(markdown_sources(root, packages))
    base = f'https://github.com/{repository}/blob/{quote(revision, safe="")}/'
    documents = {}
    for source in sorted(sources):
        if source in DOCUMENT_REDIRECTS:
            if DOCUMENT_REDIRECTS[source] not in sources:
                raise ValueError(f'missing canonical document for {source}')
            continue
        documents[source] = render_markdown(root, source, sources, base)

    groups = navigation_groups(documents, packages)
    categories = {source: label for label, items in groups for source in items}
    search = []
    for source, (title, content, toc, body, assets) in documents.items():
        page = document_path(source)
        prefix = relative_url('index.html', page).removesuffix('index.html')
        section = categories.get(source, '文档中心')
        package = next((item for item in packages if source.startswith(item['path'] + '/')), None)
        nav = []
        for label, items in groups:
            links = ''.join(f'<a href="{relative_url(document_path(item), page)}"' + (' aria-current="page"' if item == source else '')
                            + f'>{escape(documents[item][0])}</a>' for item in items)
            opened = ' open' if source in items or label == '快速开始' else ''
            nav.append(f'<details{opened}><summary>{label}</summary>{links}</details>')
        version = ''
        if package:
            version = f'<span>{escape(package["id"])} · {escape(package["version"])}</span>'
        html = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; object-src 'none'; base-uri 'none'">
<meta name="description" content="{escape(title, quote=True)} · AC 能力库使用文档">
<title>{escape(title)} · 文档中心</title><link rel="stylesheet" href="{prefix}assets/docs.css">
<link rel="icon" type="image/svg+xml" href="{prefix}assets/favicon.svg"></head>
<body class="docs-page"><a class="skip" href="#content">跳到正文</a>
<header class="docs-header"><a class="docs-brand" href="{prefix}index.html">AC Lab</a><nav aria-label="站点导航">
<a href="{prefix}index.html">功能展示</a><a href="{prefix}docs/README.html" aria-current="page">文档中心</a></nav>
<a class="source-link" href="{base + quote(source, safe='/')}">查看源文档 ↗</a></header>
<div class="docs-mobile-toolbar"><button id="docs-nav-toggle" class="docs-nav-toggle" type="button" aria-expanded="false" aria-controls="docs-navigation-panel">文档目录<span data-docs-nav-label>展开</span></button><span class="docs-mobile-current">{escape(section)}</span></div>
<div class="docs-layout"><aside id="docs-navigation-panel" class="docs-sidebar"><label for="doc-search">搜索文档</label>
<input type="search" id="doc-search" placeholder="能力、参数或兼容要求" autocomplete="off"><div id="search-results" aria-live="polite"></div>
<nav aria-label="文档目录">{''.join(nav)}</nav></aside>
<main id="content" class="doc-content"><div class="document-meta"><span>{section}</span>{version}<span>提交 {escape(revision[:7])}</span></div>
{legacy_anchors(source, content)}<footer>本页与源码使用同一提交。<a href="{prefix}index.html">返回功能展示</a></footer></main>
<aside class="doc-toc" aria-label="本页目录"><span>本页目录</span>{toc}</aside></div>
<div class="copy-status" role="status" hidden></div>
<script src="{prefix}doc-index.js" defer></script><script src="{prefix}assets/mermaid.min.js" defer></script>
<script src="{prefix}assets/docs.js" defer></script></body></html>'''
        destination = output / page
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(html, encoding='utf-8')
        text = re.sub(r'```.*?```', '', body, flags=re.S)
        text = re.sub(r'[#*`|>\[\]()]', ' ', text)
        search.append(dict(title=title, path=page, section=section, text=' '.join(text.split())))
        for asset in assets:
            target = output / asset
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / asset, target)
    payload = json.dumps(search, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    (output / 'doc-index.js').write_text('window.AC_DOC_INDEX = ' + payload + ';\n', encoding='utf-8')
    for previous, current in DOCUMENT_REDIRECTS.items():
        if previous in sources:
            write_redirect(output, previous, current)
    for name in ('docs.css', 'docs.js', 'redirect.js'):
        shutil.copyfile(root / 'site/assets' / name, output / 'assets' / name)
    for name in ('mermaid.min.js', 'mermaid-LICENSE.txt'):
        shutil.copyfile(root / 'site/vendor' / name, output / 'assets' / name)
    return sources
