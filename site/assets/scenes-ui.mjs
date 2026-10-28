import {element, action, input, select, table, status, stats, group, makeScope} from './demo-kit.mjs';
import {makeRecords} from './mock-data.mjs';

const choices = (records, field) => [...new Set(records.map(record => String(record[field])))].map(value => [value, value]);
const money = value => `¥${Number(value || 0).toLocaleString('zh-CN', {maximumFractionDigits: 2})}`;
const matches = (record, value) => !value || [record.name, record.owner, record.category, record.note].some(part => String(part || '').toLowerCase().includes(value.toLowerCase()));
const resultLabel = (records, total) => `匹配 ${records.length} / ${total} 条样例`;

function mount(container, className = '') {
  const scope = makeScope();
  const root = element('div', undefined, `mock-panel ${className}`.trim());
  container.replaceChildren(root);
  return {scope, root, cleanup: () => {scope.dispose(); root.remove();}};
}
function labelledResult(id, text, tone = 'info') {
  const node = status(text, tone);
  node.id = id;
  node.setAttribute('aria-live', 'polite');
  return node;
}
function heading(text) {return element('h3', text);}
function badge(text) {return element('span', text, 'mock-badge');}
function fields(...items) {
  const node = element('div', undefined, 'mock-grid');
  node.append(...items.map(item => item.wrap));
  return node;
}
function detail(record) {
  const pane = element('div', undefined, 'mock-result');
  pane.append(heading('记录详情'));
  if (!record) {pane.append(status('没有匹配记录，调整条件后继续查看。')); return pane;}
  pane.append(heading(record.name), badge(record.status), stats([
    ['编号', record.id], ['分类', record.category], ['负责人', record.owner],
    ['金额', money(record.amount)], ['更新日期', record.updated],
  ]), element('p', record.note));
  return pane;
}
function pagination(page, pages, previous, next) {
  const before = action('上一页', previous);
  const after = action('下一页', next);
  before.disabled = page <= 1;
  after.disabled = page >= pages;
  const label = element('span', `第 ${page} / ${pages} 页`);
  label.setAttribute('aria-live', 'polite');
  return group(before, label, after);
}

function renderTable(container, context = {}) {
  const {root, cleanup} = mount(container, 'mock-table-scene');
  const records = makeRecords();
  const query = input('搜索记录', ''); query.control.id = 'table-record-query';
  const category = select('记录分类', [['', '全部分类'], ...choices(records, 'category')], '');
  const summary = element('div');
  const result = element('div');
  const selected = element('div');
  let page = 1;
  let selectedId = records[0]?.id;
  const size = 6;
  function render() {
    const filtered = records.filter(record => matches(record, query.control.value.trim()) && (!category.control.value || record.category === category.control.value));
    const pages = Math.max(1, Math.ceil(filtered.length / size));
    page = Math.min(page, pages);
    if (!filtered.some(record => record.id === selectedId)) selectedId = filtered[0]?.id;
    summary.replaceChildren(stats([['样例记录', records.length], ['当前匹配', filtered.length], ['每页显示', size]]));
    const visible = filtered.slice((page - 1) * size, page * size);
    if (!visible.some(record => record.id === selectedId)) selectedId = visible[0]?.id;
    const rows = visible.map(record => [
      record.name, record.category, record.owner, badge(record.status),
      action(`查看 ${record.name}`, () => {selectedId = record.id; renderDetail(); selected.scrollIntoView({block:'nearest'});}),
    ]);
    result.replaceChildren(table(['名称', '分类', '负责人', '状态', '操作'], rows));
    if (!rows.length) result.append(status('没有匹配记录。'));
    result.append(pagination(page, pages, () => {page -= 1; render();}, () => {page += 1; render();}));
    renderDetail();
  }
  function renderDetail() {selected.replaceChildren(detail(records.find(record => record.id === selectedId)));}
  query.control.addEventListener('input', () => {page = 1; render();});
  category.control.addEventListener('change', () => {page = 1; render();});
  const split = element('div', undefined, 'mock-split'); split.append(result, selected);
  root.append(fields(query, category), summary, split);
  render();
  return cleanup;
}

function renderForm(container, context = {}) {
  const {root, cleanup} = mount(container, 'mock-form-scene');
  const records = makeRecords();
  const sample = {...records[0]};
  const name = input('样例名称', sample.name); name.control.id = 'form-record-name';
  const owner = input('负责人', sample.owner);
  const category = select('分类', choices(records, 'category'), sample.category);
  const amount = input('金额', String(sample.amount), 'number'); amount.control.min = '0';
  const note = input('备注', sample.note);
  const notice = labelledResult('form-save-result', '样例已填写，可修改后保存。', 'success');
  const preview = element('div', undefined, 'mock-result'); preview.id = 'form-live-preview';
  function values() {return {name: name.control.value.trim(), owner: owner.control.value.trim(), category: category.control.value, amount: amount.control.value, note: note.control.value.trim()};}
  function refresh() {
    const value = values();
    preview.replaceChildren(heading('实时预览'), heading(value.name || '待填写名称'), stats([
      ['负责人', value.owner || '待填写'], ['分类', value.category], ['金额', value.amount === '' ? '待填写' : money(value.amount)],
    ]), element('p', value.note || '暂无备注'));
  }
  function save() {
    const value = values();
    const error = !value.name ? '请填写样例名称。' : !value.owner ? '请填写负责人。' : value.amount === '' || !Number.isFinite(Number(value.amount)) || Number(value.amount) < 0 ? '金额应为零或正数。' : '';
    notice.className = status('', error ? 'error' : 'success').className;
    notice.textContent = error || `已保存「${value.name}」的页面内样例。`;
    refresh();
  }
  const reset = action('恢复样例', () => {
    [name, owner, category, amount, note].forEach((field, index) => {field.control.value = [sample.name, sample.owner, sample.category, sample.amount, sample.note][index];});
    notice.className = status('', 'success').className;
    notice.textContent = '已恢复预填样例。';
    refresh();
  });
  [name, owner, category, amount, note].forEach(field => {
    field.control.addEventListener('input', refresh);
    field.control.addEventListener('change', refresh);
  });
  const editor = element('div'); editor.append(fields(name, owner, category, amount, note), group(action('保存样例', save, 'primary'), reset), notice);
  const split = element('div', undefined, 'mock-split'); split.append(editor, preview);
  root.append(split);
  refresh();
  return cleanup;
}

function renderFilters(container, context = {}) {
  const {root, cleanup} = mount(container, 'mock-filter-scene');
  const records = makeRecords();
  const query = input('筛选关键词', ''); query.control.id = 'filter-record-query';
  const category = select('筛选分类', [['', '全部分类'], ...choices(records, 'category')], records[0]?.category || '');
  const state = select('筛选状态', [['', '全部状态'], ...choices(records, 'status')], '');
  const lookup = input('联想输入', records[0]?.owner || ''); lookup.control.id = 'filter-suggestion-query';
  const candidates = element('div', undefined, 'mock-list'); candidates.id = 'filter-suggestions';
  const result = element('div', undefined, 'mock-result');
  const notice = labelledResult('filter-selection-result', '已显示预设分类和联想候选。');
  function render() {
    const filtered = records.filter(record => matches(record, query.control.value.trim()) && (!category.control.value || record.category === category.control.value) && (!state.control.value || record.status === state.control.value));
    result.replaceChildren(heading(resultLabel(filtered, records.length)), table(['名称', '分类', '状态', '负责人'], filtered.slice(0, 8).map(record => [record.name, record.category, badge(record.status), record.owner])));
    if (!filtered.length) result.append(status('当前条件没有结果，试试重置筛选。'));
  }
  function suggest() {
    const value = lookup.control.value.trim();
    const matches_ = records.filter(record => matches(record, value)).slice(0, 5);
    candidates.replaceChildren(...matches_.map(record => action(record.name, () => {
      lookup.control.value = record.name; query.control.value = record.name;
      category.control.value = ''; state.control.value = '';
      notice.textContent = `已选择「${record.name}」，结果已同步。`;
      render(); suggest();
    })));
    if (!matches_.length) candidates.append(status('没有联想候选，请换一个关键词。'));
  }
  [query, category, state].forEach(field => {
    field.control.addEventListener('input', render);
    field.control.addEventListener('change', render);
  });
  lookup.control.addEventListener('input', suggest);
  const clear = action('重置筛选', () => {
    query.control.value = ''; category.control.value = ''; state.control.value = '';
    lookup.control.value = '';
    notice.textContent = '已清除条件，显示全部样例。';
    render(); suggest();
  });
  const controls = element('div'); controls.append(fields(query, category, state), clear, heading('联想候选'), lookup.wrap, candidates, notice);
  const split = element('div', undefined, 'mock-split'); split.append(controls, result);
  root.append(split); render(); suggest();
  return cleanup;
}

function renderFeedback(container, context = {}) {
  const {root, scope, cleanup} = mount(container, 'mock-feedback-scene');
  const records = makeRecords().slice(0, 3);
  const notice = labelledResult('feedback-result', '样例已加载，3 条记录可查看。', 'success');
  const results = element('div', undefined, 'mock-result');
  const confirmation = element('div', undefined, 'mock-result'); confirmation.id = 'feedback-confirmation'; confirmation.hidden = true;
  let pending;
  function show(text, tone) {
    notice.className = status('', tone).className;
    notice.textContent = text;
  }
  function list() {results.replaceChildren(heading('处理结果样例'), table(['样例', '状态'], records.map(record => [record.name, badge(record.status)])));}
  const success = action('成功提示', () => show('样例保存成功，结果已更新。', 'success'));
  const failure = action('错误提示', () => show('模拟保存失败。样例仍保留，可以重试。', 'error'));
  const loading = action('模拟加载', () => {
    if (pending) scope.clear(pending);
    loading.disabled = true;
    results.setAttribute('aria-busy', 'true');
    show('正在加载样例…', 'info');
    pending = scope.later(() => {
      loading.disabled = false; results.removeAttribute('aria-busy');
      show(`加载完成，${records.length} 条样例已就绪。`, 'success'); list();
    }, 650);
  });
  const confirm = action('请求确认', () => {confirmation.hidden = false; show('请确认后再执行页面内样例操作。', 'info');});
  confirmation.append(heading('确认操作'), element('p', '将第一条样例标记为已确认？'), group(
    action('确认处理', () => {if (records[0]) records[0].status = '已确认'; confirmation.hidden = true; show('已确认并更新第一条页面内样例。', 'success'); list();}, 'primary'),
    action('暂不处理', () => {confirmation.hidden = true; show('已取消确认，样例保持原状。', 'info');}),
  ));
  root.append(stats([['可见样例', records.length], ['待确认操作', 1]]), group(success, failure, loading, confirm), notice, confirmation, results);
  list();
  return cleanup;
}

function renderNavigation(container, context = {}) {
  const {root, cleanup} = mount(container, 'mock-navigation-scene');
  const records = makeRecords();
  const tasks = records.slice(0, 6).map((record, index) => ({...record, status: index < 2 ? '已完成' : '待处理'}));
  const history = records.slice(6, 10).map(record => ({name: record.name, message: `${record.owner} 已完成样例处理`, date: record.updated}));
  const summary = element('div');
  const tabs = element('div', undefined, 'mock-tabs'); tabs.setAttribute('role', 'tablist'); tabs.setAttribute('aria-label', '示例页面导航');
  const panel = element('div', undefined, 'mock-result'); panel.id = 'navigation-current-page'; panel.setAttribute('role', 'tabpanel');
  const notice = labelledResult('navigation-result', '当前为概览，切换页面可继续操作。');
  let current = '概览';
  const buttons = new Map();
  function render() {
    summary.replaceChildren(stats([['任务总数', tasks.length], ['待处理', tasks.filter(task => task.status !== '已完成').length], ['已完成', tasks.filter(task => task.status === '已完成').length]]));
    buttons.forEach((button, name) => {button.classList.toggle('is-active', name === current); button.setAttribute('aria-selected', String(name === current)); button.tabIndex = name === current ? 0 : -1;});
    panel.setAttribute('aria-labelledby', buttons.get(current).id);
    panel.replaceChildren(heading(current));
    if (current === '概览') {
      panel.append(element('p', '今日样例进展'), table(['任务', '负责人', '状态'], tasks.slice(0, 4).map(task => [task.name, task.owner, badge(task.status)])), action('查看全部任务', () => navigate('任务')));
    } else if (current === '任务') {
      const finish = action('完成首项', () => {
        const task = tasks.find(task => task.status !== '已完成');
        if (!task) return;
        task.status = '已完成';
        history.unshift({name: task.name, message: '已在页面内标记为完成', date: task.updated});
        notice.textContent = `已完成「${task.name}」，概览和历史已同步。`; render();
      });
      finish.disabled = !tasks.some(task => task.status !== '已完成');
      panel.append(table(['任务', '负责人', '状态'], tasks.map(task => [task.name, task.owner, badge(task.status)])), finish);
    } else {
      const list = element('ul', undefined, 'mock-log');
      history.forEach(item => {const li = element('li'); li.append(element('strong', item.name), element('p', item.message), element('small', item.date)); list.append(li);});
      panel.append(list, action('返回概览', () => navigate('概览')));
    }
  }
  function navigate(name) {current = name; notice.textContent = `当前页面：${name}`; render();}
  ['概览', '任务', '历史'].forEach(name => {
    const button = action(name, () => navigate(name));
    button.id = `navigation-tab-${buttons.size}`;
    button.setAttribute('role', 'tab'); button.setAttribute('aria-controls', panel.id);
    button.addEventListener('keydown', event => {
      const names = ['概览', '任务', '历史']; let index = names.indexOf(current);
      if (event.key === 'ArrowRight') index = (index + 1) % names.length;
      else if (event.key === 'ArrowLeft') index = (index + names.length - 1) % names.length;
      else if (event.key === 'Home') index = 0;
      else if (event.key === 'End') index = names.length - 1;
      else return;
      event.preventDefault(); navigate(names[index]); buttons.get(names[index]).focus();
    });
    buttons.set(name, button); tabs.append(button);
  });
  root.append(summary, tabs, notice, panel); render();
  return cleanup;
}

function renderAuth(container, context = {}) {
  const {root, cleanup} = mount(container, 'mock-auth-scene');
  const permissions = ['查看记录', '编辑记录', '删除记录', '管理配置', '导出结果'];
  const roles = {
    viewer: {name: '只读成员', allowed: ['查看记录']},
    operator: {name: '操作成员', allowed: ['查看记录', '编辑记录', '导出结果']},
    admin: {name: '管理员', allowed: permissions},
  };
  const role = select('模拟角色', Object.entries(roles).map(([value, item]) => [value, item.name]), 'operator'); role.control.id = 'auth-role';
  const password = input('样例口令', 'demo-2026', 'password'); password.control.id = 'auth-sample-password';
  const matrix = element('div', undefined, 'mock-result');
  const roleResult = labelledResult('auth-role-result', '当前操作成员可查看、编辑和导出样例。', 'success');
  const passwordResult = labelledResult('auth-password-result', '预填样例口令已通过模拟校验。', 'success');
  const editing = action('尝试编辑样例', () => {
    const allowed = roles[role.control.value].allowed.includes('编辑记录');
    roleResult.className = status('', allowed ? 'success' : 'error').className;
    roleResult.textContent = allowed ? '模拟允许：此角色可以编辑页面内样例。' : '模拟拒绝：此角色没有编辑样例的权限。';
  });
  function render() {
    const current = roles[role.control.value];
    matrix.replaceChildren(heading('角色权限对照'), table(['操作', '只读成员', '操作成员', '管理员'], permissions.map(permission => [permission, ...Object.values(roles).map(item => item.allowed.includes(permission) ? '允许' : '拒绝')])));
    roleResult.className = status('', 'info').className;
    roleResult.textContent = `当前角色：${current.name}，可执行 ${current.allowed.length} 项样例操作。`;
  }
  role.control.addEventListener('change', render);
  const check = action('校验样例口令', () => {
    const passed = password.control.value === 'demo-2026';
    passwordResult.className = status('', passed ? 'success' : 'error').className;
    passwordResult.textContent = passed ? '模拟校验通过，样例口令匹配。' : '模拟校验未通过。恢复为 demo-2026 可再次体验。';
  }, 'primary');
  const controls = element('div');
  controls.append(status('仅演示角色与校验效果，不执行真实认证。'), role.wrap, group(editing), roleResult, password.wrap, group(check, action('恢复样例口令', () => {password.control.value = 'demo-2026'; passwordResult.className = status('', 'success').className; passwordResult.textContent = '已恢复样例口令，模拟校验通过。';})), passwordResult);
  const split = element('div', undefined, 'mock-split'); split.append(controls, matrix); root.append(split); render();
  return cleanup;
}

function renderCrud(container, context = {}) {
  const {root, cleanup} = mount(container, 'mock-crud-scene');
  const records = makeRecords();
  const categories = choices(records, 'category');
  const summary = element('div');
  const listing = element('div');
  const editor = element('div', undefined, 'mock-result');
  const name = input('编辑名称', records[0].name); name.control.id = 'crud-record-name';
  const owner = input('编辑负责人', records[0].owner);
  const category = select('编辑分类', categories, records[0].category);
  const amount = input('编辑金额', String(records[0].amount), 'number'); amount.control.min = '0';
  const note = input('编辑备注', records[0].note);
  const notice = labelledResult('crud-result', '已选中第一条样例，可直接修改并保存。', 'success');
  let selectedId = records[0].id;
  let sequence = 0;
  let changes = 0;
  const title = heading('编辑所选样例'); title.id = 'crud-editor-title';
  const save = action('保存修改', () => {
    const values = {name: name.control.value.trim(), owner: owner.control.value.trim(), category: category.control.value, amount: Number(amount.control.value), note: note.control.value.trim()};
    if (!values.name || !values.owner || amount.control.value === '' || !Number.isFinite(values.amount) || values.amount < 0) {
      notice.className = status('', 'error').className; notice.textContent = '请填写名称、负责人及有效的非负金额。'; return;
    }
    if (selectedId === null) {
      const created = {id: `MOCK-NEW-${++sequence}`, ...values, status: '待处理', updated: records[0]?.updated || '样例日期'};
      records.unshift(created); selectedId = created.id;
      notice.textContent = `已新增「${created.name}」的页面内样例。`;
    } else {
      const record = records.find(item => item.id === selectedId);
      if (!record) return;
      Object.assign(record, values);
      notice.textContent = `已更新「${record.name}」。`;
    }
    changes += 1; notice.className = status('', 'success').className;
    title.textContent = '编辑所选样例'; save.textContent = '保存修改'; renderList();
  }, 'primary');
  const remove = action('删除所选', () => {
    const index = records.findIndex(item => item.id === selectedId);
    if (index < 0) return;
    const [removed] = records.splice(index, 1); changes += 1;
    notice.className = status('', 'success').className; notice.textContent = `已删除「${removed.name}」的页面内样例。`;
    if (records.length) choose(records[0]); else newRecord();
    renderList();
  });
  function fill(record) {
    name.control.value = record.name; owner.control.value = record.owner; category.control.value = record.category;
    amount.control.value = String(record.amount); note.control.value = record.note || '';
  }
  function choose(record) {
    selectedId = record.id; fill(record); title.textContent = '编辑所选样例'; save.textContent = '保存修改'; remove.disabled = false;
    renderList();
  }
  function newRecord() {
    selectedId = null;
    fill({name: `新增样例 ${sequence + 1}`, owner: records[0]?.owner || '样例成员', category: categories[0]?.[0] || '', amount: 120, note: '用于体验新增操作的虚构样例。'});
    title.textContent = '新增样例'; save.textContent = '保存新增'; remove.disabled = true;
  }
  function renderList() {
    remove.disabled = selectedId === null || !records.some(record => record.id === selectedId);
    summary.replaceChildren(stats([['样例总数', records.length], ['本次变更', changes], ['当前选中', selectedId === null ? '新记录' : selectedId]]));
    const visible = [...records.slice(0, 6)];
    const selected = records.find(record => record.id === selectedId);
    if (selected && !visible.includes(selected)) visible.push(selected);
    listing.replaceChildren(table(['名称', '负责人', '操作'], visible.map(record => [record.name, record.owner, action(`编辑 ${record.name}`, () => {choose(record); notice.textContent = `已选中「${record.name}」。`;})])));
    if (!records.length) listing.append(status('样例已清空，可以新增一条。'));
  }
  editor.append(title, fields(name, owner, category, amount, note), group(save, remove), notice);
  const split = element('div', undefined, 'mock-split'); split.append(listing, editor);
  root.append(summary, group(action('新增样例', () => {newRecord(); renderList(); notice.textContent = '新增内容已预填，修改后保存即可。';})), split);
  renderList();
  return cleanup;
}

function renderQuery(container, context = {}) {
  const {root, cleanup} = mount(container, 'mock-query-scene');
  const records = makeRecords();
  const query = input('查询名称或负责人', ''); query.control.id = 'query-record-name';
  const category = select('查询分类', [['', '全部分类'], ...choices(records, 'category')], '');
  const minimum = input('最低金额', '0', 'number'); minimum.control.min = '0';
  const pageSize = select('每页条数', [['4', '4 条'], ['6', '6 条'], ['12', '12 条']], '6');
  const notice = labelledResult('query-result', '预设条件已应用，显示全部虚构记录。', 'success');
  const result = element('div', undefined, 'mock-result');
  let page = 1;
  let active = {query: '', category: '', minimum: 0, size: 6};
  function render() {
    const filtered = records.filter(record => matches(record, active.query) && (!active.category || record.category === active.category) && Number(record.amount) >= active.minimum);
    const pages = Math.max(1, Math.ceil(filtered.length / active.size)); page = Math.min(page, pages);
    const rows = filtered.slice((page - 1) * active.size, page * active.size);
    result.replaceChildren(heading('匹配结果'), stats([['匹配记录', filtered.length], ['结果页数', pages], ['本页条数', rows.length]]), table(['名称', '负责人', '分类', '金额'], rows.map(record => [record.name, record.owner, record.category, money(record.amount)])), pagination(page, pages, () => {page -= 1; render();}, () => {page += 1; render();}));
    if (!filtered.length) result.append(status('没有匹配结果，放宽条件后再次查询。'));
  }
  function apply() {
    const value = Number(minimum.control.value);
    if (minimum.control.value === '' || !Number.isFinite(value) || value < 0) {
      notice.className = status('', 'error').className; notice.textContent = '最低金额应为零或正数。'; return;
    }
    active = {query: query.control.value.trim(), category: category.control.value, minimum: value, size: Number(pageSize.control.value)};
    page = 1;
    notice.className = status('', 'success').className;
    notice.textContent = `已应用条件：${active.category || '全部分类'}，金额至少 ${money(active.minimum)}，每页 ${active.size} 条。`;
    render();
  }
  const reset = action('恢复预设条件', () => {query.control.value = ''; category.control.value = ''; minimum.control.value = '0'; pageSize.control.value = '6'; apply();});
  const controls = element('div'); controls.append(heading('查询条件'), fields(query, category, minimum, pageSize), group(action('应用条件', apply, 'primary'), reset), notice);
  const split = element('div', undefined, 'mock-split'); split.append(controls, result); root.append(split); render();
  return cleanup;
}

export const uiScenes = {
  table: renderTable,
  form: renderForm,
  filters: renderFilters,
  feedback: renderFeedback,
  navigation: renderNavigation,
  auth: renderAuth,
  crud: renderCrud,
  query: renderQuery,
};
