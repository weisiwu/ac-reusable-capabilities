/* Documentation-only controls. All reading content is rendered during build. */
const scriptRoot = new URL('../', document.currentScript.src);
const search = document.getElementById('doc-search');
const results = document.getElementById('search-results');
const navigationToggle = document.getElementById('docs-nav-toggle');
const navigationPanel = document.getElementById('docs-navigation-panel');
if (navigationToggle && navigationPanel) {
  const narrowViewport = window.matchMedia('(max-width: 900px)');
  let navigationOpen = false;
  const syncNavigation = () => {
    const expanded = !narrowViewport.matches || navigationOpen;
    navigationPanel.hidden = !expanded;
    navigationToggle.setAttribute('aria-expanded', String(expanded));
    const label = navigationToggle.querySelector('[data-docs-nav-label]');
    if (label) label.textContent = expanded ? '收起' : '展开';
  };
  document.body.classList.add('docs-navigation-ready');
  navigationToggle.addEventListener('click', () => {
    navigationOpen = !navigationOpen;
    syncNavigation();
  });
  narrowViewport.addEventListener('change', () => {
    navigationOpen = false;
    syncNavigation();
  });
  navigationPanel.addEventListener('keydown', event => {
    if (event.key === 'Escape' && narrowViewport.matches && navigationOpen) {
      navigationOpen = false;
      syncNavigation();
      navigationToggle.focus();
    }
  });
  navigationPanel.addEventListener('click', event => {
    if (narrowViewport.matches && event.target.closest('a')) {
      navigationOpen = false;
      syncNavigation();
    }
  });
  syncNavigation();
}
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
  const tokens = getComputedStyle(document.documentElement);
  const ink = tokens.getPropertyValue('--ink').trim() || '#202939';
  const surface = tokens.getPropertyValue('--surface').trim() || '#f5f7fb';
  const line = tokens.getPropertyValue('--line').trim() || '#dfe4ed';
  const muted = tokens.getPropertyValue('--muted').trim() || '#59677d';
  window.mermaid.initialize({startOnLoad: false, securityLevel: 'strict', theme: 'base',
    fontFamily: tokens.getPropertyValue('--font-sans').trim() || 'system-ui, sans-serif',
    themeVariables: {primaryColor: surface, primaryTextColor: ink, primaryBorderColor: line,
      lineColor: muted, secondaryColor: '#e5edff', tertiaryColor: '#fff'},
    flowchart: {htmlLabels: false, useMaxWidth: true}});
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
window.addEventListener('pagehide', () => {
  clearTimeout(copyTimer);
  const status = document.querySelector('.copy-status');
  if (status) status.hidden = true;
});
