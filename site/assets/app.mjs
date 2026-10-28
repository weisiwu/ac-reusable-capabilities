import {findCapabilities} from './models.mjs';
import {sceneRenderers} from './scene-registry.mjs';
import {element, status} from './demo-kit.mjs';

const data = window.AC_DATA;
const $ = identity => document.getElementById(identity);
const link = (node, url) => {
  node.href = url;
  if (/^https?:\/\//.test(url)) {node.target = '_blank'; node.rel = 'noopener noreferrer';}
  return node;
};
document.querySelectorAll('[data-link]').forEach(node => link(node, data[node.dataset.link]));
// Skip to the current view without replacing its hash route.
document.querySelector('.skip').addEventListener('click', event => {
  event.preventDefault();
  $('main').focus({preventScroll:true});
  $('main').scrollIntoView({block:'start', behavior:'instant'});
});
const scenes = data.browserDemos.filter(scene => typeof sceneRenderers[scene.renderer] === 'function');
const kindLabels = {component:'组件', library:'基础库', workflow:'流程能力', adapter:'适配器', tool:'工程工具'};
const sceneByCapability = new Map(scenes.map(scene => [scene.capability_id, scene]));
const groupFor = item => sceneByCapability.get(item.id)?.group || `${item.language} / ${item.domain}`;
const groups = [...new Set([...scenes.map(scene => scene.group || '功能体验'), ...data.capabilities.map(groupFor)])];
let currentScene = null;
let disposeScene = () => {};
let selectedGroup = '';
let lastCatalogHash = '#catalog';

function closeMenu() {
  document.querySelector('.app-sidebar').classList.remove('is-open');
  $('app-menu-toggle').setAttribute('aria-expanded', 'false');
}
$('app-menu-toggle').addEventListener('click', () => {
  const expanded = $('app-menu-toggle').getAttribute('aria-expanded') !== 'true';
  $('app-menu-toggle').setAttribute('aria-expanded', String(expanded));
  document.querySelector('.app-sidebar').classList.toggle('is-open', expanded);
});
document.querySelector('.app-sidebar').addEventListener('click', event => {
  if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
  const anchor = event.target.closest('a');
  if (!anchor || !anchor.hash || anchor.origin !== location.origin || anchor.pathname !== location.pathname || anchor.hash !== location.hash) return;
  event.preventDefault();
  closeMenu();
  document.querySelector('.app-main > section:not([hidden]) h1')?.focus({preventScroll:true});
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && $('app-menu-toggle').getAttribute('aria-expanded') === 'true') {
    closeMenu(); $('app-menu-toggle').focus();
  }
});

function releaseScene() {
  disposeScene(); disposeScene = () => {};
  $('scene-content').replaceChildren(); currentScene = null;
}
function renderScene(scene, reset = false) {
  if (scene === currentScene && !reset) return;
  releaseScene(); currentScene = scene;
  const capability = data.capabilities.find(item => item.id === scene.capability_id);
  $('scene-title').textContent = scene.title;
  $('scene-summary').textContent = scene.summary || capability?.summary || '';
  link($('context-guide'), capability?.guide || data.docs);
  try {
    disposeScene = sceneRenderers[scene.renderer]($('scene-content'), {capabilities:data.capabilities, scene}) || (() => {});
  } catch (error) {
    console.error(error);
    $('scene-content').replaceChildren(status('样例暂时无法显示，请重置样例或选择其他功能。', 'error'));
  }
}
$('reset-scene').addEventListener('click', () => {if (currentScene) renderScene(currentScene, true);});

function renderNavigation() {
  const catalog = $('catalog-navigation'); catalog.replaceChildren();
  for (const name of ['', ...groups]) {
    const anchor = link(element('a', name || '全部能力'), name ? `#group/${encodeURIComponent(name)}` : '#catalog');
    if (name === selectedGroup) anchor.setAttribute('aria-current', 'page');
    catalog.append(anchor);
  }
  const nav = $('demo-navigation'); nav.replaceChildren();
  for (const name of [...new Set(scenes.map(scene => scene.group || '功能体验'))]) {
    const items = scenes.filter(item => (item.group || '功能体验') === name);
    const section = element('details', undefined, 'demo-nav-group sidebar-group');
    section.setAttribute('name', 'demo-navigation-groups');
    section.open = items.includes(currentScene);
    const summary = element('summary', name, 'sidebar-group-title');
    section.append(summary);
    const links = element('div', undefined, 'sidebar-group-items');
    for (const scene of items) {
      const anchor = link(element('a', scene.title), `#demo/${encodeURIComponent(scene.renderer)}`);
      if (scene === currentScene) anchor.setAttribute('aria-current', 'page');
      links.append(anchor);
    }
    section.append(links);
    const closeOtherGroups = () => {
      // A replaced navigation can still deliver an already queued toggle event.
      if (!nav.contains(section)) return;
      for (const peer of nav.querySelectorAll('.sidebar-group')) {
        if (peer !== section) peer.open = false;
      }
    };
    // Native details supplies keyboard/expanded semantics; close peers on older browsers too.
    summary.addEventListener('click', () => {
      if (!section.open) closeOtherGroups();
    });
    section.addEventListener('toggle', () => {
      if (section.open) closeOtherGroups();
    });
    nav.append(section);
  }
  document.querySelectorAll('.sidebar-links a').forEach(anchor => {
    if (anchor.hash === '#recipes' && location.hash === '#recipes') anchor.setAttribute('aria-current', 'page');
    else anchor.removeAttribute('aria-current');
  });
}

function option(control, value, title) {
  const node = element('option', title); node.value = value; control.append(node);
}
for (const [field, id] of [['language','filter-language'], ['domain','filter-domain'], ['kind','filter-kind']]) {
  [...new Set(data.capabilities.map(item => item[field]))].sort().forEach(value => option($(id), value, kindLabels[value] || value));
}
data.packages.forEach(item => option($('demo-package'), item.id, `${item.language} / ${item.domain}`));
function filters() {
  return {language:$('filter-language').value, domain:$('filter-domain').value,
    kind:$('filter-kind').value, mode:$('filter-mode').value};
}
function arrow() {
  const ns = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(ns, 'svg');
  svg.setAttribute('viewBox', '0 0 20 20'); svg.setAttribute('width', '18'); svg.setAttribute('height', '18');
  svg.setAttribute('aria-hidden', 'true'); svg.setAttribute('fill', 'none');
  const path = document.createElementNS(ns, 'path');
  path.setAttribute('d', 'M4 10h11m-4-4 4 4-4 4');
  path.setAttribute('stroke', 'currentColor'); path.setAttribute('stroke-width', '1.5');
  path.setAttribute('stroke-linecap', 'round'); path.setAttribute('stroke-linejoin', 'round'); svg.append(path);
  return svg;
}
function renderCapabilities() {
  const matches = findCapabilities(data.capabilities, $('capability-query').value, filters())
    .filter(item => !selectedGroup || groupFor(item) === selectedGroup);
  $('capability-count').textContent = `${matches.length} / ${data.capabilities.length} 项能力`;
  $('capability-count').hidden = matches.length === data.capabilities.length;
  $('catalog-meta').textContent = `${data.capabilities.length} 项能力 · ${scenes.length} 项在线体验`;
  const list = $('capability-list'); list.replaceChildren();
  for (const [index, name] of groups.entries()) {
    const items = matches.filter(item => groupFor(item) === name);
    if (!items.length) continue;
    const section = element('section', undefined, 'capability-group');
    section.setAttribute('aria-labelledby', `group-${index}`);
    const heading = element('div', undefined, 'group-heading');
    const title = element('h2', name); title.id = `group-${index}`;
    heading.append(title, element('span', `${items.length} 项`));
    const entries = element('div', undefined, 'capability-entries');
    // Match the stable scene order, while keeping documentation-only capabilities visible.
    items.sort((a, b) => {
      const rank = item => {const i = scenes.findIndex(scene => scene.capability_id === item.id); return i < 0 ? Infinity : i;};
      return rank(a) - rank(b);
    });
    for (const item of items) {
      const scene = sceneByCapability.get(item.id);
      const row = element('article', undefined, 'capability-entry');
      const copy = element('div', undefined, 'entry-copy');
      const title = link(element('a', scene?.title || item.name, 'entry-title'), scene ? `#demo/${encodeURIComponent(scene.renderer)}` : item.guide);
      title.append(arrow());
      copy.append(title, element('p', scene?.summary || item.summary, 'entry-summary'));
      const actions = element('div', undefined, 'entry-actions');
      actions.append(link(element('a', scene ? '使用文档' : '查看文档'), item.guide));
      row.append(copy, actions); entries.append(row);
    }
    section.append(heading, entries); list.append(section);
  }
  if (!matches.length) {
    const empty = element('div', undefined, 'catalog-empty');
    empty.append(element('h2', '没有找到对应能力'), element('p', '试试其他关键词，或清除筛选后查看全部能力。'));
    const reset = element('button', '清除搜索与筛选'); reset.type = 'button';
    reset.addEventListener('click', resetFilters); empty.append(reset); list.append(empty);
  }
}
function resetFilters() {
  $('capability-query').value = '';
  ['language','domain','kind','mode'].forEach(key => {$(`filter-${key}`).value = '';});
  if (selectedGroup) location.hash = '#catalog';
  else renderCapabilities();
}
$('capability-query').addEventListener('input', renderCapabilities);
['language','domain','kind','mode'].forEach(key => $(`filter-${key}`).addEventListener('change', renderCapabilities));
$('clear-filters').addEventListener('click', resetFilters);

const scenarioExamples = {
  'desktop-core': {scene:'crud', summary:'使用现有资料体验新增、修改与数据查看。'},
  'desktop-ui': {scene:'table', summary:'从样例记录出发，体验筛选、翻页与详情。'},
  'desktop-search': {scene:'search', summary:'在已有结果上搜索，体验取消与超时反馈。'},
  'desktop-failures': {scene:'services', summary:'从运行中的服务开始，观察停止、失败与恢复。'},
  'desktop-contracts': {scene:'query', summary:'修改查询条件，直接对照匹配后的记录。'},
  'desktop-contracts-qt': {scene:'form', summary:'修改已填写的表单，查看校验和保存结果。'},
};
function renderDemos() {
  const list = $('demo-list'); list.replaceChildren();
  const demos = data.demos.filter(item => !$('demo-package').value || item.package === $('demo-package').value);
  for (const item of demos) {
    const row = element('article', undefined, 'scenario-row'); row.id = `demo-${item.id}`;
    const intro = element('div'); intro.append(element('h2', item.title));
    const preset = scenarioExamples[item.id];
    if (preset) intro.append(element('p', preset.summary));
    const actions = element('div', undefined, 'row-actions');
    const scene = scenes.find(scene => scene.renderer === preset?.scene);
    if (scene) actions.append(link(element('a', '体验样例', 'button-link'), `#demo/${scene.renderer}`));
    actions.append(link(element('a', '场景文档'), item.guide));
    row.append(intro, actions); list.append(row);
  }
  if (!demos.length) list.append(element('p', '这个分类尚未登记组合场景。', 'empty'));
}
$('demo-package').addEventListener('change', renderDemos);

function route({focus = false, reset = false} = {}) {
  const hash = location.hash;
  if (hash === '#docs') {location.replace(data.docs); return;}
  let renderer = '', group = '', invalid = false;
  try {
    if (hash.startsWith('#demo/')) renderer = decodeURIComponent(hash.slice(6));
    else if (hash.startsWith('#group/')) group = decodeURIComponent(hash.slice(7));
    else if (hash === '#lab') renderer = scenes[0]?.renderer || '';
    else if (hash && !['#catalog','#overview','#recipes','#examples','#main'].includes(hash)) invalid = true;
  } catch {invalid = true;}
  const scene = scenes.find(item => item.renderer === renderer);
  if ((hash.startsWith('#demo/') && !scene) || (hash.startsWith('#group/') && !groups.includes(group))) invalid = true;
  const experience = Boolean(scene) && !invalid;
  const recipes = !invalid && ['#recipes','#examples'].includes(hash);
  const catalog = !experience && !recipes;
  selectedGroup = catalog && !invalid ? group : '';
  $('catalog-view').hidden = !catalog;
  $('experience-view').hidden = !experience;
  $('recipes-view').hidden = !recipes;
  $('catalog-navigation').hidden = !catalog;
  $('demo-navigation').hidden = !experience;
  $('route-notice').hidden = !invalid;
  $('route-notice').textContent = invalid ? '这个入口暂不可用。请从能力目录重新选择功能。' : '';
  if (experience) renderScene(scene, reset);
  else {releaseScene(); if (catalog) {if (!invalid) lastCatalogHash = hash || '#catalog'; renderCapabilities();}}
  $('back-catalog').href = lastCatalogHash;
  document.title = `${experience ? scene.title : recipes ? '组合场景' : '能力目录'} · AC 能力库`;
  renderNavigation(); closeMenu();
  if (focus) {
    $(experience ? 'scene-title' : recipes ? 'recipes-title' : 'catalog-title').focus({preventScroll:true});
    window.scrollTo({top:0, behavior:'instant'});
  }
}
window.addEventListener('hashchange', () => route({focus:true}));
window.addEventListener('pagehide', releaseScene);
window.addEventListener('pageshow', event => {if (event.persisted) route({reset:true});});
$('package-version').textContent = data.packages.map(item => `${item.id} ${item.version}`).join(' · ');
$('site-revision').textContent = `提交 ${data.revision.slice(0, 7)}`;
renderDemos(); route();
