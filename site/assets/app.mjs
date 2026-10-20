import {pageRows, redact, findCapabilities, LatestRequest} from './models.mjs';
const data = window.AC_DATA;
const $ = id => document.getElementById(id);
const node = (tag, text, className) => {
  const element = document.createElement(tag);
  if (text !== undefined) element.textContent = text;
  if (className) element.className = className;
  return element;
};
const external = (element, url) => {
  element.href = url;
  element.target = '_blank';
  element.rel = 'noopener noreferrer';
  return element;
};
let toastTimer;
function announce(message) {
  $('announcement').textContent = message;
  $('announcement').hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {$('announcement').hidden = true;}, 2600);
}
async function copy(text) {
  try {
    await navigator.clipboard.writeText(text);
    announce('命令已复制。');
  } catch {
    announce('浏览器不允许复制，请选中命令手动复制。');
  }
}
document.querySelectorAll('[data-link]').forEach(element => external(element, data[element.dataset.link]));
$('revision').textContent = `文档版本 ${data.revision.length === 40 ? data.revision.slice(0, 7) : data.revision}`;
const contexts = {table: 'desktop.table', form: 'desktop.forms', search: 'desktop.background', redact: 'desktop.diagnostics'};
const titles = {table: '数据表格', form: '配置表单', search: '异步搜索', redact: '结构化脱敏'};
let currentTab = 'table';
function selectTab(tab, focus = false) {
  if (tab !== currentTab && currentTab === 'search') cancelSearch();
  currentTab = tab;
  document.querySelectorAll('[data-tab]').forEach(button => {
    const selected = button.dataset.tab === tab;
    button.setAttribute('aria-selected', String(selected));
    button.tabIndex = selected ? 0 : -1;
    $(`pane-${button.dataset.tab}`).hidden = !selected;
    if (selected && focus) button.focus();
  });
  $('lab-title').textContent = titles[tab];
  const item = data.capabilities.find(capability => capability.id === contexts[tab]);
  if (item) {
    external($('context-guide'), item.guide);
    external($('context-contract'), item.contract);
    external($('context-source'), item.source);
    $('context-id').textContent = item.id;
  }
  $('context-command').textContent = `python demo/run.py ${tab === 'search' ? 'desktop-search' : tab === 'redact' ? 'desktop-failures' : 'desktop-ui'}`;
}
document.querySelectorAll('[data-tab]').forEach(button => {
  button.addEventListener('click', () => selectTab(button.dataset.tab));
  button.addEventListener('keydown', event => {
    const tabs = Object.keys(titles);
    let index = tabs.indexOf(button.dataset.tab);
    if (event.key === 'ArrowRight') index = (index + 1) % tabs.length;
    else if (event.key === 'ArrowLeft') index = (index + tabs.length - 1) % tabs.length;
    else if (event.key === 'Home') index = 0;
    else if (event.key === 'End') index = tabs.length - 1;
    else return;
    event.preventDefault();
    selectTab(tabs[index], true);
  });
});
$('copy-context').addEventListener('click', () => copy($('context-command').textContent));
document.querySelectorAll('[data-nav]').forEach(link => link.addEventListener('click', () => {
  document.querySelectorAll('[data-nav]').forEach(item => item.classList.toggle('active', item === link));
}));

const sampleRows = [
  {name: '分页表格', category: '界面组件', status: '样例可用'},
  {name: '配置表单', category: '界面组件', status: '样例可用'},
  {name: '联想筛选', category: '界面组件', status: '样例可用'},
  {name: 'SQLite 快照', category: '数据工具', status: '样例可用'},
  {name: '结构化日志', category: '工程基础', status: '样例可用'},
  {name: '服务管理', category: '工程基础', status: '样例可用'},
  {name: '查询构建', category: '数据工具', status: '样例可用'},
  {name: '后台任务', category: '工程基础', status: '样例可用'}
];
let page = 1;
function renderTable() {
  const result = pageRows(sampleRows, $('table-query').value, $('table-category').value, page);
  page = result.page;
  const body = $('sample-rows');
  body.replaceChildren();
  result.rows.forEach(row => {
    const tr = node('tr');
    tr.append(node('td', row.name), node('td', row.category));
    const status = node('td'); status.append(node('span', row.status, 'badge'));
    const actions = node('td');
    const view = node('button', '查看');
    view.type = 'button';
    view.setAttribute('aria-label', `查看${row.name}`);
    view.addEventListener('click', () => announce(`${row.name} · ${row.category}${row.note ? ` · ${row.note}` : ' · 演示数据，不关联业务记录'}`));
    actions.append(view); tr.append(status, actions); body.append(tr);
  });
  if (!result.total) {const td = node('td', '没有匹配的记录。', 'empty'); td.colSpan = 4; const tr = node('tr'); tr.append(td); body.append(tr);}
  $('table-count').textContent = `共 ${result.total} 条样例`;
  $('page-number').textContent = `${result.page} / ${result.pages}`;
  $('previous').disabled = result.page === 1;
  $('next').disabled = result.page === result.pages;
}
$('table-query').addEventListener('input', () => {page = 1; renderTable();});
$('table-category').addEventListener('change', () => {page = 1; renderTable();});
$('previous').addEventListener('click', () => {page -= 1; renderTable();});
$('next').addEventListener('click', () => {page += 1; renderTable();});
$('sample-form').addEventListener('submit', event => {
  event.preventDefault();
  const name = $('record-name').value.trim();
  if (!name) { $('record-name').setCustomValidity('请输入名称，不能只有空格。'); $('record-name').reportValidity(); return; }
  sampleRows.unshift({name, category: $('record-category').value, note: $('record-note').value.trim(), status: '新建样例'});
  $('sample-form').reset();
  $('form-status').textContent = `已添加「${name}」，切换数据表格可查看。仅保留在当前页面。`;
  $('table-query').value = ''; $('table-category').value = ''; page = 1; renderTable();
});
$('record-name').addEventListener('input', () => $('record-name').setCustomValidity(''));
$('sample-form').addEventListener('reset', () => { $('record-name').setCustomValidity(''); $('form-status').textContent = ''; });

const latest = new LatestRequest();
let debounce;
function cancelSearch() {
  clearTimeout(debounce);
  latest.cancel();
  $('cancel-search').disabled = true;
  $('async-results').replaceChildren();
  $('async-status').textContent = '查询已取消，迟到结果不会显示。';
}
$('cancel-search').addEventListener('click', cancelSearch);
$('async-query').addEventListener('input', () => {
  clearTimeout(debounce);
  latest.cancel();
  const query = $('async-query').value.trim();
  $('async-results').replaceChildren();
  $('cancel-search').disabled = !query;
  if (!query) { $('async-status').textContent = '输入关键词开始搜索。'; return; }
  $('async-status').textContent = '等待输入完成…';
  debounce = setTimeout(async () => {
    $('async-status').textContent = '模拟查询中…';
    const result = await latest.start(query, query === '超时' ? 1200 : 450);
    if (result.cancelled || query !== $('async-query').value.trim()) return;
    $('cancel-search').disabled = true;
    if (query === '超时') { $('async-status').textContent = '模拟查询超时，请修改关键词后重试。'; return; }
    const matches = findCapabilities(data.capabilities, query);
    $('async-status').textContent = `已交付最新请求 #${result.identity} · ${matches.length} 项结果`;
    matches.slice(0, 6).forEach(item => {
      const li = node('li');
      li.append(external(node('a', item.name), item.guide), node('small', item.id));
      $('async-results').append(li);
    });
  }, 250);
});
$('redact-button').addEventListener('click', () => {
  try {
    const raw = $('redact-input').value;
    if (raw.length > 20000) throw new Error('样例过大，请控制在 20,000 个字符以内。');
    $('redact-output').textContent = JSON.stringify(redact(JSON.parse(raw)), null, 2);
    $('redact-status').textContent = '已处理结构化敏感键，原输入未修改。';
    $('redact-status').classList.remove('error');
  } catch (error) {
    $('redact-output').textContent = '';
    $('redact-status').textContent = error instanceof SyntaxError ? 'JSON 格式无效，请检查引号、逗号与括号。' : error.message;
    $('redact-status').classList.add('error');
  }
});
function renderCapabilities() {
  const matches = findCapabilities(data.capabilities, $('capability-query').value);
  $('capability-count').textContent = `${matches.length} / ${data.capabilities.length} 项能力`;
  $('capability-list').replaceChildren();
  matches.forEach(item => {
    const row = node('div', undefined, 'capability-row');
    const name = node('div'); name.append(node('strong', item.name), node('small', item.id));
    const links = node('div', undefined, 'row-actions');
    const tab = Object.keys(contexts).find(key => contexts[key] === item.id);
    if (tab) {
      const tryIt = node('button', '体验'); tryIt.type = 'button';
      tryIt.addEventListener('click', () => { selectTab(tab, true); $('lab').scrollIntoView({block: 'start'}); });
      links.append(tryIt);
    }
    links.append(external(node('a', '指南 ↗'), item.guide), external(node('a', '契约 ↗'), item.contract));
    row.append(name, node('span', `${item.package} / ${item.modules.join(', ')}`, 'modules'), links);
    $('capability-list').append(row);
  });
  if (!matches.length) $('capability-list').append(node('p', '没有匹配的能力，试试模块名或稳定 ID。', 'empty'));
}
$('capability-query').addEventListener('input', renderCapabilities);
data.demos.forEach(item => {
  const row = node('article', undefined, 'demo-row');
  const intro = node('div'); intro.append(node('h3', item.title), node('p', item.id));
  const links = node('div', undefined, 'row-actions');
  links.append(external(node('a', '示例源码 ↗'), item.source), external(node('a', '运行说明 ↗'), item.guide));
  intro.append(links);
  const commands = node('div');
  const command = node('div', undefined, 'code-line'); command.append(node('code', item.command));
  const button = node('button', '复制', 'copy'); button.type = 'button';
  button.setAttribute('aria-label', `复制 ${item.id} 运行命令`);
  button.addEventListener('click', () => copy(item.command));
  command.append(button); commands.append(command, node('code', item.install, 'install'));
  if (item.smoke) commands.append(node('code', `无显示器：QT_QPA_PLATFORM=offscreen ${item.command} --smoke`, 'install'));
  row.append(intro, commands); $('demo-list').append(row);
});
window.addEventListener('pagehide', () => {clearTimeout(debounce); clearTimeout(toastTimer); latest.cancel();});
selectTab('table'); renderTable(); renderCapabilities();
