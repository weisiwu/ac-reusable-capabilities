/* Documentation-only controls. All reading content is rendered during build. */
const scriptRoot = new URL('../', document.currentScript.src);
const search = document.getElementById('doc-search');
const results = document.getElementById('search-results');
search.addEventListener('input', () => {
  const query = search.value.trim().toLocaleLowerCase();
  results.replaceChildren();
  if (!query) return;
  const tokens = query.split(/\s+/);
  const matches = (window.AC_DOC_INDEX || []).map(item => ({...item,
    score: tokens.reduce((score, token) => score + (item.title.toLocaleLowerCase().includes(token) ? 3 : 0), 0)
  })).filter(item => tokens.every(token => `${item.title} ${item.text}`.toLocaleLowerCase().includes(token)))
    .sort((a, b) => b.score - a.score).slice(0, 12);
  if (!matches.length) results.textContent = '没有匹配文档，请换一个关键词。';
  for (const item of matches) {
    const link = document.createElement('a');
    link.href = new URL(item.path, scriptRoot);
    link.textContent = `${item.section} · ${item.title}`;
    results.append(link);
  }
});
let copyTimer;
for (const block of document.querySelectorAll('.doc-content pre:not(.mermaid)')) {
  if (block.closest('figure')) continue;
  const code = block.querySelector('code');
  if (!code) continue;
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'copy-code';
  button.textContent = '复制';
  button.setAttribute('aria-label', '复制此代码示例');
  button.addEventListener('click', async () => {
    const status = document.querySelector('.copy-status');
    try {
      await navigator.clipboard.writeText(code.textContent);
      status.textContent = '代码已复制';
    } catch {
      status.textContent = '请选中代码后复制';
    }
    status.hidden = false;
    clearTimeout(copyTimer);
    copyTimer = setTimeout(() => { status.hidden = true; }, 1800);
  });
  block.append(button);
}
async function diagrams() {
  if (!window.mermaid) return;
  window.mermaid.initialize({startOnLoad: false, securityLevel: 'strict', theme: 'neutral',
    fontFamily: 'system-ui, sans-serif', flowchart: {htmlLabels: false, useMaxWidth: true}});
  for (const diagram of document.querySelectorAll('.mermaid')) {
    const original = diagram.textContent;
    try { await window.mermaid.run({nodes: [diagram]}); }
    catch {
      diagram.textContent = original;
      diagram.classList.add('diagram-fallback');
    }
  }
}
diagrams();
window.addEventListener('pagehide', () => clearTimeout(copyTimer));
