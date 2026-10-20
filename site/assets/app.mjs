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
const contexts = Object.fromEntries(data.browserDemos.map(scene => [scene.renderer, scene.capability_id]));
const titles = Object.fromEntries(data.browserDemos.map(scene => [scene.renderer, scene.title]));
const kindLabels = {component:'组件', library:'基础库', workflow:'流程能力', adapter:'适配器', tool:'工程工具'};
const modeLabels = {browser:'浏览器演示', local:'本地示例', documentation:'文档接入'};
let currentTab = null;
document.querySelectorAll('[data-tab]').forEach(button => {
  const available = Boolean(contexts[button.dataset.tab]);
  button.hidden = !available;
  if (!available) $(`pane-${button.dataset.tab}`).hidden = true;
});
if (!data.browserDemos.length) {
  $('lab').hidden = true;
  document.querySelector('.lab-heading').hidden = true;
  document.querySelector('[data-nav="lab"]').hidden = true;
}
$('catalog-summary').textContent = `${data.packages.length} 个能力包 · ${data.capabilities.length} 项能力 · 来源可追溯，契约独立维护`;

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
  const scene = data.browserDemos.find(scene => scene.renderer === tab);
  const demo = data.demos.find(demo => demo.id === scene?.demo_id);
  $('context-command').textContent = demo?.command || '请查看该能力的接入指南';
  $('copy-context').hidden = !demo?.command;
  $('lab-package').textContent = item ? `${item.language} / ${item.domain} · 浏览器行为示意` : '';

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
function option(select, value, label) {
  const element = node('option', label); element.value = value; select.append(element);
}
for (const [field, id] of [['language','filter-language'], ['domain','filter-domain'], ['kind','filter-kind']]) {
  [...new Set(data.capabilities.map(item => item[field]))].sort().forEach(value => option($(id), value, kindLabels[value] || value));
}
data.origins.forEach(item => option($('filter-origin'), item.id, item.name));
data.packages.forEach(item => option($('demo-package'), item.id, item.id));
let catalogPage = 1;
const pageSize = 8;
function filters() {
  return {language:$('filter-language').value,domain:$('filter-domain').value,kind:$('filter-kind').value,
    origin:$('filter-origin').value,mode:$('filter-mode').value};
}
function showDemo(identity) {
  const demo = data.demos.find(item => item.id === identity);
  if (!demo) return;
  $('demo-package').value = demo.package;
  renderDemos();
  const element = $(`demo-${identity}`);
  element.classList.add('highlight');
  element.scrollIntoView({block:'center'});
}
function showDetail(item) {
  $('detail-title').textContent = item.name;
  const content = $('detail-content'); content.replaceChildren();
  const pkg = data.packages.find(pkg => pkg.id === item.package);
  content.append(node('code',item.id,'detail-id'), node('p',item.summary));
  const facts = node('dl',undefined,'detail-facts');
  for (const [label,value] of [['语言',item.language],['领域',item.domain],['类型',kindLabels[item.kind] || item.kind],
    ['能力包',item.package],['包版本',pkg?.version || '未声明'],['许可',pkg?.license || '见来源说明']]) {
    facts.append(node('dt',label),node('dd',value));
  }
  content.append(facts);
  const links = node('div',undefined,'detail-links');
  links.append(external(node('a','使用指南 ↗'),item.guide),external(node('a','接口契约 ↗'),item.contract));
  item.sources.forEach((url,index) => links.append(external(node('a',`源码 ${index+1} ↗`),url)));
  content.append(links,node('h3','来源与演示'));
  item.origin_ids.forEach(id => {
    const origin = data.origins.find(origin => origin.id === id);
    content.append(external(node('a',`${origin.name} · 来源记录 ↗`),origin.provenance));
  });
  if (!item.origin_ids.length) content.append(node('p','来源尚未登记，接入前核实许可与归属。'));
  const demos = data.demos.filter(demo => item.demo_ids.includes(demo.id));
  demos.forEach(demo => {
    const box = node('div',undefined,'detail-demo'); box.append(node('h3',demo.title));
    box.append(node('p',`${demo.mode === 'local' ? '本地运行' : '文档示例'}${demo.runtime ? ` · ${demo.runtime}` : ''}`));
    if (demo.install) box.append(node('code',demo.install,'install'));
    if (demo.command) box.append(node('pre',demo.command));
    box.append(external(node('a','示例说明 ↗'),demo.guide)); content.append(box);
  });
  if (!demos.length) content.append(node('p','此能力通过指南与契约接入，没有登记可执行示例。'));
  content.append(node('p','网站登记与浏览器演示不代表已完成你的目标环境验收。','boundary'));
  $('capability-detail').showModal();
}
$('close-detail').addEventListener('click',() => $('capability-detail').close());
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
    const row = node('article',undefined,'capability-row');
    const name = node('div'); name.append(node('strong',item.name),node('small',item.id),node('p',item.summary,'capability-summary'));
    const meta = node('div',undefined,'modules');
    meta.append(node('span',`${item.language} / ${item.domain}`),node('span',kindLabels[item.kind] || item.kind,'kind-label'));
    const links = node('div',undefined,'row-actions');
    const detail = node('button','详情'); detail.type='button'; detail.setAttribute('aria-label',`查看${item.name}详情`);
    detail.addEventListener('click',() => showDetail(item)); links.append(detail);
    const scene = data.browserDemos.find(scene => scene.capability_id === item.id);
    if (scene) {
      const tryIt = node('button','浏览器演示'); tryIt.type='button';
      tryIt.addEventListener('click',() => { selectTab(scene.renderer,true); $('lab').scrollIntoView({block:'start'}); }); links.append(tryIt);
    } else {
      const demo = data.demos.find(demo => item.demo_ids.includes(demo.id) && demo.mode === 'local');
      if (demo) {const local = node('button','本地示例');local.type='button';local.addEventListener('click',() => showDemo(demo.id));links.append(local);}
      else links.append(external(node('a','文档接入 ↗'),item.guide));
    }
    links.append(external(node('a','指南 ↗'),item.guide));
    row.append(name,meta,links); $('capability-list').append(row);
  });
  if (!matches.length) $('capability-list').append(node('p','当前条件下没有能力。清除筛选，或尝试用途、标签和稳定 ID。','empty'));
}
function resetCatalogPage() {catalogPage=1;renderCapabilities();}
$('capability-query').addEventListener('input',resetCatalogPage);
['language','domain','kind','origin','mode'].forEach(key => $(`filter-${key}`).addEventListener('change',resetCatalogPage));
$('clear-filters').addEventListener('click',() => {
  $('capability-query').value=''; ['language','domain','kind','origin','mode'].forEach(key => {$(`filter-${key}`).value='';}); resetCatalogPage();
});
$('catalog-previous').addEventListener('click',() => {catalogPage-=1;renderCapabilities();});
$('catalog-next').addEventListener('click',() => {catalogPage+=1;renderCapabilities();});
function renderDemos() {
  $('demo-list').replaceChildren();
  const items = data.demos.filter(item => !$('demo-package').value || item.package === $('demo-package').value);
  items.forEach(item => {
    const row=node('article',undefined,'demo-row');row.id=`demo-${item.id}`;
    const intro=node('div');intro.append(node('h3',item.title),node('p',`${item.package} · ${item.runtime || '文档'} · ${item.id}`));
    const links=node('div',undefined,'row-actions');
    if (item.source) links.append(external(node('a','示例源码 ↗'),item.source));
    links.append(external(node('a','使用说明 ↗'),item.guide));intro.append(links);
    const commands=node('div');
    if (item.command) {
      const command=node('div',undefined,'code-line');command.append(node('code',item.command));
      const button=node('button','复制','copy');button.type='button';button.setAttribute('aria-label',`复制 ${item.id} 运行命令`);
      button.addEventListener('click',() => copy(item.command));command.append(button);commands.append(command);
    } else commands.append(node('p','按文档说明接入，无需本地启动命令。'));
    if (item.install) commands.append(node('code',item.install,'install'));
    if (item.smoke_command) commands.append(node('code',`自动验证：${item.smoke_command}`,'install'));
    row.append(intro,commands);$('demo-list').append(row);
  });
  if (!items.length) $('demo-list').append(node('p','这个能力包暂未登记示例，请查阅包文档。','empty'));
}
$('demo-package').addEventListener('change',renderDemos);
window.addEventListener('pagehide', () => {clearTimeout(debounce); clearTimeout(toastTimer); latest.cancel();});
if (data.browserDemos.length) selectTab(data.browserDemos[0].renderer);
renderTable(); renderCapabilities(); renderDemos();
