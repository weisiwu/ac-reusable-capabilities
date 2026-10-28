import {pageRows, redact, findCapabilities, LatestRequest} from './models.mjs';
const data = window.AC_DATA;
const $ = id => document.getElementById(id);
const node = (tag, text, className) => {
  const element = document.createElement(tag);
  if (text !== undefined) element.textContent = text;
  if (className) element.className = className;
  return element;
};
const link = (element, url) => {
  element.href = url;
  if (/^https?:\/\//.test(url)) {
    element.target = '_blank';
    element.rel = 'noopener noreferrer';
  }
  return element;
};
let toastTimer;
function announce(message) {
  $('announcement').textContent = message;
  $('announcement').hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {$('announcement').hidden = true;}, 2600);
}
document.querySelectorAll('[data-link]').forEach(element => link(element, data[element.dataset.link]));
const contexts = Object.fromEntries(data.browserDemos.map(scene => [scene.renderer, scene.capability_id]));
const titles = Object.fromEntries(data.browserDemos.map(scene => [scene.renderer, scene.title]));
const kindLabels = {component:'组件', library:'基础库', workflow:'流程能力', adapter:'适配器', tool:'工程工具'};
const sceneStories = {
  table: {label:'查找与浏览', title:'从一组记录中，快速找到目标。', summary:'搜索、分类、翻页，一起体验。', outcomes:['按关键词找到记录','切换分类缩小范围','翻页浏览全部样例']},
  form: {label:'采集与校验', title:'一份表单，完成信息采集。', summary:'填写、校验、保存，看见新记录。', outcomes:['必填信息即时校验','多种字段集中填写','新建结果直接出现在表格']},
  search: {label:'输入与响应', title:'输入一直变，结果跟得上。', summary:'试着快速输入，再取消一次查询。', outcomes:['输入完成后开始查找','只展示最新搜索结果','随时取消，失败可以重试']},
  redact: {label:'隐藏敏感信息', title:'保留有用信息，隐藏敏感内容。', summary:'处理一份样例，对照查看结果。', outcomes:['隐藏密码与令牌','一并处理嵌套内容','保留其他字段与原始输入']}
};
let currentTab = null;
document.querySelectorAll('[data-tab]').forEach(button => {
  const available = Boolean(contexts[button.dataset.tab]);
  button.hidden = !available;
  if (!available) $(`pane-${button.dataset.tab}`).hidden = true;
});
if (!data.browserDemos.length) {
  $('lab').hidden = true;
  document.querySelector('.intro p:last-child').textContent = '浏览功能目录，找到适合项目的能力。';
  document.querySelector('[data-nav="lab"]').hidden = true;
}
$('catalog-summary').textContent = `${data.capabilities.length} 项能力，找到适合下一次项目的功能。`;

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
  if (item) link($('context-guide'), item.guide);
  const story = sceneStories[tab];
  $('scene-label').textContent = story.label;
  $('experience-title').textContent = story.title;
  $('experience-summary').textContent = story.summary;
  $('experience-outcomes').replaceChildren(...story.outcomes.map(text => node('li', text)));

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
    $('async-status').textContent = `搜索完成 · ${matches.length} 项结果`;
    matches.slice(0, 6).forEach(item => {
      const li = node('li');
      li.append(link(node('a', item.name), item.guide));
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
function option(select, value, label) {
  const element = node('option', label); element.value = value; select.append(element);
}
for (const [field, id] of [['language','filter-language'], ['domain','filter-domain'], ['kind','filter-kind']]) {
  [...new Set(data.capabilities.map(item => item[field]))].sort().forEach(value => option($(id), value, kindLabels[value] || value));
}
data.packages.forEach(item => option($('demo-package'), item.id, `${item.language} / ${item.domain}`));
let catalogPage = 1;
const pageSize = 8;
function filters() {
  return {language:$('filter-language').value, domain:$('filter-domain').value, kind:$('filter-kind').value,
    mode:$('filter-mode').value};
}
function showScene(scene) {
  selectTab(scene.renderer, true);
  $('lab').scrollIntoView({block:'start'});
}
function renderCapabilities() {
  const matches = findCapabilities(data.capabilities, $('capability-query').value, filters());
  const pages = Math.max(1, Math.ceil(matches.length / pageSize));
  catalogPage = Math.min(catalogPage,pages);
  $('capability-count').textContent = `${matches.length} / ${data.capabilities.length} 项能力`;
  $('catalog-page-number').textContent = `${catalogPage} / ${pages}`;
  $('catalog-previous').disabled = catalogPage === 1;
  $('catalog-next').disabled = catalogPage === pages;
  $('capability-list').replaceChildren();
  matches.slice((catalogPage-1)*pageSize,catalogPage*pageSize).forEach(item => {
    const card = node('article', undefined, 'capability-card');
    const scene = data.browserDemos.find(scene => scene.capability_id === item.id);
    const title = node('h3', item.name);
    card.append(title, node('p', item.summary, 'capability-summary'));
    const links = node('div', undefined, 'row-actions');
    if (scene) {
      const tryIt = node('button', '在线体验');
      tryIt.type='button';
      tryIt.setAttribute('aria-label', `体验${item.name}`);
      tryIt.addEventListener('click', () => showScene(scene));
      links.append(tryIt);
    }
    links.append(link(node('a', '使用文档 →'), item.guide));
    card.append(links);
    $('capability-list').append(card);
  });
  if (!matches.length) $('capability-list').append(node('p', '没有找到对应功能，试试其他关键词或清除筛选。', 'empty'));
}
function resetCatalogPage() {catalogPage=1;renderCapabilities();}
$('capability-query').addEventListener('input',resetCatalogPage);
['language','domain','kind','mode'].forEach(key => $(`filter-${key}`).addEventListener('change',resetCatalogPage));
$('clear-filters').addEventListener('click',() => {
  $('capability-query').value=''; ['language','domain','kind','mode'].forEach(key => {$(`filter-${key}`).value='';}); resetCatalogPage();
});
$('catalog-previous').addEventListener('click',() => {catalogPage-=1;renderCapabilities();});
$('catalog-next').addEventListener('click',() => {catalogPage+=1;renderCapabilities();});
const scenarioDescriptions = {
  'desktop-core':'从记录管理到数据备份，把常用基础功能连接起来。',
  'desktop-ui':'在表格、表单、筛选、反馈和记录管理之间切换。',
  'desktop-search':'边输入边查找，让界面持续响应。',
  'desktop-failures':'看看操作失败后，如何取消、恢复和继续。',
  'desktop-contracts':'通过小例子，认识各项基础功能。',
  'desktop-contracts-qt':'结合界面组件，浏览完整功能示例。'
};
function renderDemos() {
  $('demo-list').replaceChildren();
  const items = data.demos.filter(item => !$('demo-package').value || item.package === $('demo-package').value);
  items.forEach(item => {
    const row = node('article', undefined, 'scenario-row');
    row.id = `demo-${item.id}`;
    const intro = node('div');
    intro.append(node('h3', item.title));
    if (scenarioDescriptions[item.id]) intro.append(node('p', scenarioDescriptions[item.id]));
    row.append(intro, link(node('a', '查看场景 →'), item.guide));
    $('demo-list').append(row);
  });
  if (!items.length) $('demo-list').append(node('p', '这个分类暂未登记组合场景。', 'empty'));
}
$('demo-package').addEventListener('change',renderDemos);
window.addEventListener('pagehide', () => {clearTimeout(debounce); clearTimeout(toastTimer); latest.cancel();});
if (data.browserDemos.length) selectTab(data.browserDemos[0].renderer);
renderTable(); renderCapabilities(); renderDemos();
