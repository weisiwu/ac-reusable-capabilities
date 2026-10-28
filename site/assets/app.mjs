import {findCapabilities} from './models.mjs';
import {sceneRenderers} from './scene-registry.mjs';
import {element, action, status} from './demo-kit.mjs';

const data = window.AC_DATA;
const $ = identity => document.getElementById(identity);
const link = (node, url) => {
  node.href = url;
  if (/^https?:\/\//.test(url)) {node.target = '_blank'; node.rel = 'noopener noreferrer';}
  return node;
};
document.querySelectorAll('[data-link]').forEach(node => link(node, data[node.dataset.link]));

const scenes = data.browserDemos.filter(scene => typeof sceneRenderers[scene.renderer] === 'function');
const kindLabels = {component:'组件', library:'基础库', workflow:'流程能力', adapter:'适配器', tool:'工程工具'};
let currentScene = null;
let disposeScene = () => {};
let catalogPage = 1;
const pageSize = 8;

function sceneForHash() {
  if (!location.hash.startsWith('#demo/')) return null;
  try {return scenes.find(scene => scene.renderer === decodeURIComponent(location.hash.slice(6))) || null;}
  catch {return null;}
}

function chooseScene(scene, {updateHash = true, scroll = true, reset = false} = {}) {
  if (!scene) return;
  if (scene !== currentScene || reset) {
    disposeScene();
    disposeScene = () => {};
    $('scene-content').replaceChildren();
    currentScene = scene;
    const capability = data.capabilities.find(item => item.id === scene.capability_id);
    $('scene-title').textContent = scene.title;
    $('scene-summary').textContent = scene.summary || capability?.summary || '';
    $('scene-picker').value = scene.renderer;
    if (capability) link($('context-guide'), capability.guide);
    try {
      disposeScene = sceneRenderers[scene.renderer]($('scene-content'), {capabilities: data.capabilities, scene}) || (() => {});
    } catch (error) {
      console.error(error);
      $('scene-content').replaceChildren(status('样例暂时无法显示，请重置样例或选择其他功能。', 'error'));
    }
    renderNavigation();
  }
  if (updateHash) history.replaceState(null, '', `#demo/${encodeURIComponent(scene.renderer)}`);
  if (scroll) $('lab').scrollIntoView({block:'start'});
}

function renderNavigation() {
  const matches = new Set(findCapabilities(data.capabilities, $('capability-query').value).map(item => item.id));
  const nav = $('demo-navigation');
  nav.replaceChildren();
  const grouped = new Map();
  scenes.filter(scene => matches.has(scene.capability_id)).forEach(scene => {
    const name = scene.group || '功能体验';
    if (!grouped.has(name)) grouped.set(name, []);
    grouped.get(name).push(scene);
  });
  for (const [name, items] of grouped) {
    const details = element('details');
    details.open = true;
    details.append(element('summary', name));
    items.forEach(scene => {
      const anchor = link(element('a', scene.title), `#demo/${encodeURIComponent(scene.renderer)}`);
      if (scene === currentScene) {anchor.className = 'is-active'; anchor.setAttribute('aria-current', 'page');}
      anchor.addEventListener('click', event => {event.preventDefault(); chooseScene(scene);});
      details.append(anchor);
    });
    nav.append(details);
  }
  if (!grouped.size) nav.append(element('p', '没有匹配的演示，清除关键词后查看全部能力。', 'empty'));
}

function option(control, value, title) {
  const node = element('option', title); node.value = value; control.append(node);
}
scenes.forEach(scene => option($('scene-picker'), scene.renderer, scene.title));
$('scene-picker').addEventListener('change', () => chooseScene(scenes.find(scene => scene.renderer === $('scene-picker').value), {scroll:false}));
$('reset-scene').addEventListener('click', () => chooseScene(currentScene, {reset:true, scroll:false}));
window.addEventListener('hashchange', () => {
  const scene = sceneForHash();
  if (scene) chooseScene(scene, {updateHash:false, scroll:false});
});

for (const [field, id] of [['language','filter-language'], ['domain','filter-domain'], ['kind','filter-kind']]) {
  [...new Set(data.capabilities.map(item => item[field]))].sort().forEach(value => option($(id), value, kindLabels[value] || value));
}
data.packages.forEach(item => option($('demo-package'), item.id, `${item.language} / ${item.domain}`));
function filters() {
  return {language:$('filter-language').value, domain:$('filter-domain').value,
    kind:$('filter-kind').value, mode:$('filter-mode').value};
}
function renderCapabilities() {
  const matches = findCapabilities(data.capabilities, $('capability-query').value, filters());
  const pages = Math.max(1, Math.ceil(matches.length / pageSize));
  catalogPage = Math.min(catalogPage, pages);
  $('capability-count').textContent = `${matches.length} / ${data.capabilities.length} 项能力`;
  $('catalog-summary').textContent = `${scenes.length} 项在线样例已就绪，可直接操作并查看结果。`;
  $('catalog-page-number').textContent = `${catalogPage} / ${pages}`;
  $('catalog-previous').disabled = catalogPage === 1;
  $('catalog-next').disabled = catalogPage === pages;
  const list = $('capability-list');
  list.replaceChildren();
  matches.slice((catalogPage - 1) * pageSize, catalogPage * pageSize).forEach(item => {
    const row = element('article', undefined, 'capability-card');
    row.append(element('h3', item.name), element('p', item.summary, 'capability-summary'));
    const actions = element('div', undefined, 'row-actions');
    const scene = scenes.find(scene => scene.capability_id === item.id);
    if (scene) actions.append(action('体验样例', () => chooseScene(scene)));
    actions.append(link(element('a', '使用文档 →'), item.guide));
    row.append(actions); list.append(row);
  });
  if (!matches.length) list.append(element('p', '没有找到对应功能，调整关键词或清除筛选。', 'empty'));
}
function resetCatalogPage() {catalogPage = 1; renderCapabilities();}
$('capability-query').addEventListener('input', () => {resetCatalogPage(); renderNavigation();});
['language','domain','kind','mode'].forEach(key => $(`filter-${key}`).addEventListener('change', resetCatalogPage));
$('clear-filters').addEventListener('click', () => {
  $('capability-query').value = '';
  ['language','domain','kind','mode'].forEach(key => {$(`filter-${key}`).value = '';});
  resetCatalogPage(); renderNavigation();
});
$('catalog-previous').addEventListener('click', () => {catalogPage -= 1; renderCapabilities();});
$('catalog-next').addEventListener('click', () => {catalogPage += 1; renderCapabilities();});

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
  demos.forEach(item => {
    const row = element('article', undefined, 'scenario-row'); row.id = `demo-${item.id}`;
    const intro = element('div'); intro.append(element('h3', item.title));
    const preset = scenarioExamples[item.id];
    if (preset) intro.append(element('p', preset.summary));
    const actions = element('div', undefined, 'row-actions');
    const scene = scenes.find(scene => scene.renderer === preset?.scene);
    if (scene) actions.append(action('体验样例', () => chooseScene(scene)));
    actions.append(link(element('a', '查看场景文档 →'), item.guide));
    row.append(intro, actions); list.append(row);
  });
  if (!demos.length) list.append(element('p', '这个分类尚未登记组合场景。', 'empty'));
}
$('demo-package').addEventListener('change', renderDemos);
window.addEventListener('pagehide', () => {disposeScene(); disposeScene = () => {};});
window.addEventListener('pageshow', event => {
  if (event.persisted && currentScene) chooseScene(sceneForHash() || currentScene, {reset:true, updateHash:false, scroll:false});
});
if (scenes.length) chooseScene(sceneForHash() || scenes[0], {updateHash:false, scroll:false});
else {
  $('scene-content').append(status('这个能力包尚未登记在线演示，请从能力目录查阅使用文档。'));
  $('reset-scene').disabled = true; $('scene-picker').disabled = true;
  renderNavigation();
}
renderCapabilities(); renderDemos();
