"""Exercise document publishing boundaries and real Markdown reading features."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('reading_builder', ROOT / 'site/docs_build.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class ReadingSiteTests(unittest.TestCase):
    def test_reserved_characters_in_document_paths_are_encoded(self):
        self.assertEqual(builder.relative_url('docs/C#.html', 'wiki/Home.html'), '../docs/C%23.html')

    def test_tables_code_diagrams_frontmatter_and_chinese_anchors(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'guide.md').write_text('''---
title: Internal metadata
---
# 中文指南

| 参数 | 默认值 |
| --- | --- |
| page | 1 |

```python
example = "[literal](missing.md)"
```

```mermaid
flowchart LR
 A[开始] --> B[结果]
```
''', encoding='utf-8')
            title, html, toc, _, _ = builder.render_markdown(root, 'guide.md', {'guide.md'}, 'https://github.com/test/repo/blob/abc/')
            self.assertEqual(title, '中文指南')
            self.assertNotIn('Internal metadata', html)
            self.assertIn('<table>', html)
            self.assertIn('id="中文指南"', html)
            self.assertIn('[literal](missing.md)', html)
            self.assertIn('<pre class="mermaid">', html)
            self.assertIn('查看流程图文本', html)
            self.assertIn('#中文指南', toc)

    def test_local_documents_stay_in_site_and_sources_are_revision_pinned(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'docs').mkdir()
            (root / 'src').mkdir()
            (root / 'src/example.py').write_text('value = 1')
            (root / 'docs/示例.md').write_text('# 示例')
            (root / 'README.md').write_text('[Guide](docs/示例.md#参数) [Code](src/example.py)', encoding='utf-8')
            _, html, _, _, _ = builder.render_markdown(root, 'README.md', {'README.md', 'docs/示例.md'}, 'https://github.com/test/repo/blob/frozen/')
            self.assertIn('docs/%E7%A4%BA%E4%BE%8B.html#参数', html)
            self.assertIn('https://github.com/test/repo/blob/frozen/src/example.py', html)

    def test_raw_html_and_unsafe_links_do_not_add_executable_markup(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'README.md').write_text('<script>alert(1)</script>\n\n<a href="javascript:alert(1)" onclick="alert(2)">unsafe</a>\n\n<img src="data:text/html,bad" onerror="alert(3)">')
            _, html, _, _, _ = builder.render_markdown(root, 'README.md', {'README.md'}, 'https://github.com/test/repo/blob/main/')
            for forbidden in ('<script', 'javascript:', 'onclick=', 'onerror=', 'data:text/html'):
                self.assertNotIn(forbidden, html)

    def test_only_declared_public_roots_are_published(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'docs').mkdir()
            (root / '.project-context').mkdir()
            for relative in ('README.md', 'docs/public.md', '.project-context/private.md', 'credentials.md'):
                (root / relative).write_text('# sample')
            self.assertEqual(builder.markdown_sources(root, []), ['README.md', 'docs/public.md'])
            (root / 'docs/outside.md').symlink_to(root / '.project-context/private.md')
            with self.assertRaises(ValueError):
                builder.markdown_sources(root, [])

    def test_links_cannot_escape_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'repo'
            root.mkdir()
            (root.parent / 'private.md').write_text('secret')
            (root / 'README.md').write_text('[Escape](../private.md)')
            with self.assertRaises(ValueError):
                builder.render_markdown(root, 'README.md', {'README.md'}, 'https://github.com/test/repo/blob/main/')

    def test_links_to_old_wiki_use_canonical_document_and_preserve_chapter(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'docs').mkdir()
            (root / 'wiki').mkdir()
            (root / 'wiki/Getting-Started.md').write_text('# Moved')
            (root / 'docs/快速开始.md').write_text('# 快速开始\n\n## 安装与第一次调用')
            (root / 'README.md').write_text('[Old](wiki/Getting-Started.md#安装与第一次调用)')
            sources = {'README.md', 'wiki/Getting-Started.md', 'docs/快速开始.md'}
            _, html, _, _, _ = builder.render_markdown(root, 'README.md', sources, 'https://github.com/test/repo/blob/main/')
            self.assertIn('docs/%E5%BF%AB%E9%80%9F%E5%BC%80%E5%A7%8B.html#安装与第一次调用', html)
            self.assertNotIn('wiki/Getting-Started.html', html)

    def test_renamed_heading_alias_is_next_to_matching_chapter(self):
        html = '<h1 id="文档中心">文档中心</h1><h2 id="快速开始">快速开始</h2>'
        output = builder.legacy_anchors('docs/README.md', html)
        self.assertIn('id="能力库-wiki"', output)
        self.assertIn('id="从你的目标开始" class="legacy-anchor" aria-hidden="true"></span><h2 id="快速开始"', output)
        self.assertEqual(builder.legacy_anchors('docs/README.md', output), output)
