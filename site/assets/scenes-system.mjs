import {element, action, input, select, table, status, stats, group, makeScope} from './demo-kit.mjs';
import {makeRecords} from './mock-data.mjs';
import {redact, LatestRequest} from './models.mjs';

const panel = (title, ...children) => {
  const section = element('section', undefined, 'mock-panel');
  section.append(element('h3', title), ...children);
  return section;
};
const box = (className = 'mock-result') => element('div', undefined, className);
const badge = text => element('span', text, 'mock-badge');
const button = (id, label, handler, variant = '') => {
  const control = action(label, handler, variant);
  control.id = id;
  return control;
};
const listen = (scope, control, type, handler) => {
  control.addEventListener(type, handler);
  scope.onDispose(() => control.removeEventListener(type, handler));
};
const setMessage = (target, text, tone = 'info') => {
  target.replaceChildren(status(text, tone));
};
const showLog = (target, lines) => {
  const list = element('ol', undefined, 'mock-log');
  lines.slice(-8).forEach(line => list.append(element('li', line)));
  target.replaceChildren(list);
};
const appendLog = (lines, line) => {
  lines.push(line);
  if (lines.length > 16) lines.splice(0, lines.length - 16);
};
const cloneRows = rows => rows.map(row => ({...row}));

function renderPrinting(container) {
  const scope = makeScope();
  const seed = [
    {name: '月度汇总报告', copies: 2, state: '已完成'},
    {name: '项目明细报告', copies: 1, state: '待打印'},
    {name: '结果汇总清单', copies: 2, state: '待打印'},
    {name: '归档确认单', copies: 1, state: '待打印'}
  ];
  let reports = cloneRows(seed);
  let running = false;
  let pending = null;
  const lines = ['月度汇总报告已完成，共 2 份。', '另外 3 项报告已加入队列。'];
  const metrics = box('mock-metrics');
  const queue = box();
  const message = box();
  message.setAttribute('aria-live', 'polite');
  const log = box();
  const start = button('mock-print-start', '开始批量', () => {
    if (running || reports.every(report => report.state === '已完成')) return;
    running = true;
    appendLog(lines, '批量任务开始。');
    next();
  }, 'primary');
  const cancel = button('mock-print-cancel', '取消任务', () => {
    if (!running) return;
    scope.clear(pending);
    pending = null;
    running = false;
    reports.forEach(report => { if (report.state === '打印中') report.state = '待继续'; });
    appendLog(lines, '已取消后续处理，完成的报告保持不变。');
    draw();
    setMessage(message, '任务已取消，可以继续未完成的报告。', 'warning');
  });
  const reset = button('mock-print-reset', '重置队列', () => {
    scope.clear(pending);
    pending = null;
    running = false;
    reports = cloneRows(seed);
    lines.splice(0, lines.length, '样例队列已重置，1 项已完成、3 项待处理。');
    draw();
    setMessage(message, '队列已恢复到初始状态。');
  });
  function draw() {
    const done = reports.filter(report => report.state === '已完成').length;
    metrics.replaceChildren(stats([['报告总数', reports.length], ['已完成', done], ['待处理', reports.length - done]]));
    queue.replaceChildren(table(['报告', '份数', '状态'], reports.map(report => [report.name, String(report.copies), badge(report.state)])));
    start.disabled = running || done === reports.length;
    start.textContent = done === reports.length ? '全部已完成' : done > 1 ? '继续批量' : '开始批量';
    cancel.disabled = !running;
    showLog(log, lines);
  }
  function next() {
    const report = reports.find(item => item.state !== '已完成');
    if (!report) {
      running = false;
      pending = null;
      appendLog(lines, '全部 4 项报告处理完成。');
      draw();
      setMessage(message, '批量任务已完成，共处理 6 份报告。', 'success');
      return;
    }
    report.state = '打印中';
    draw();
    setMessage(message, `正在处理：${report.name}。`);
    pending = scope.later(() => {
      report.state = '已完成';
      appendLog(lines, `${report.name}已完成，共 ${report.copies} 份。`);
      next();
    }, 480);
  }
  container.replaceChildren(metrics, panel('报告队列', queue, group(start, cancel, reset), message), panel('处理记录', log));
  draw();
  setMessage(message, '已有 1 项完成，点击开始处理剩余报告。', 'success');
  return () => scope.dispose();
}

function renderTransport(container) {
  const scope = makeScope();
  let connected = true;
  let busy = false;
  let pending = null;
  let generation = 0;
  const history = [
    ['接收', '设备已就绪', '成功'],
    ['发送', '读取设备状态', '已发送'],
    ['接收', '工作状态正常 · 电量 86%', '成功']
  ];
  const port = select('演示设备', [['device-a', '桌面终端 A'], ['device-b', '桌面终端 B']], 'device-a');
  port.control.id = 'mock-transport-device';
  const payload = input('发送内容', '读取设备状态');
  payload.control.id = 'mock-transport-payload';
  payload.control.maxLength = 120;
  const metrics = box('mock-metrics');
  const transcript = box();
  const message = box();
  message.setAttribute('aria-live', 'polite');
  function draw() {
    metrics.replaceChildren(stats([['连接状态', connected ? '已连接' : '已断开'],
      ['已发送', history.filter(row => row[0] === '发送').length], ['已接收', history.filter(row => row[0] === '接收').length]]));
    transcript.replaceChildren(table(['方向', '内容', '结果'], history.slice(-7).map(row => [row[0], row[1], badge(row[2])])));
    connect.textContent = connected ? '断开连接' : '连接设备';
    send.disabled = !connected || busy;
    timeout.disabled = !connected || busy;
    port.control.disabled = connected;
  }
  function transmit(simulateTimeout = false) {
    if (!connected || busy) return;
    const value = payload.control.value.trim();
    if (!value) { setMessage(message, '请输入发送内容。', 'error'); return; }
    const request = ++generation;
    busy = true;
    history.push(['发送', value, '已发送']);
    draw();
    setMessage(message, '已发送，正在等待设备回应。');
    pending = scope.later(() => {
      if (request !== generation || !connected) return;
      pending = null;
      busy = false;
      if (simulateTimeout) {
        history.push(['提示', '等待回应超时', '超时']);
        setMessage(message, '本次没有收到回应，可以重新发送。', 'warning');
      } else {
        history.push(['接收', `已确认「${value}」 · 工作状态正常`, '成功']);
        setMessage(message, '已收到设备回应。', 'success');
      }
      if (history.length > 20) history.splice(0, history.length - 20);
      draw();
    }, simulateTimeout ? 650 : 320);
  }
  const send = button('mock-transport-send', '发送样例', () => transmit(), 'primary');
  const connect = button('mock-transport-connect', '断开连接', () => {
    scope.clear(pending);
    pending = null;
    generation += 1;
    busy = false;
    connected = !connected;
    history.push(['连接', connected ? `已连接${port.control.selectedOptions[0].textContent}` : '连接已断开', connected ? '就绪' : '已断开']);
    draw();
    setMessage(message, connected ? '设备已连接，可以发送消息。' : '设备已断开，收发记录仍保留。', connected ? 'success' : 'warning');
  });
  const timeout = button('mock-transport-timeout', '模拟超时', () => transmit(true));
  container.replaceChildren(metrics, panel('设备收发', group(port.wrap, payload.wrap), group(send, connect, timeout), message), panel('收发记录', transcript));
  draw();
  setMessage(message, '桌面终端 A 已连接，最近一次回应正常。', 'success');
  return () => { generation += 1; scope.dispose(); };
}

function renderServices(container) {
  const scope = makeScope();
  const services = [
    {name: '配置中心', dependency: '无', state: '运行中'},
    {name: '日志服务', dependency: '配置中心', state: '运行中'},
    {name: '数据仓储', dependency: '配置中心、日志服务', state: '运行中'},
    {name: '后台任务', dependency: '数据仓储', state: '运行中'}
  ];
  const lines = ['配置中心已启动。', '日志服务已启动。', '数据仓储已启动。', '后台任务已启动，4 项服务运行中。'];
  const metrics = box('mock-metrics');
  const rows = box();
  const log = box();
  const message = box();
  message.setAttribute('aria-live', 'polite');
  const stop = button('mock-services-stop', '停止全部', () => {
    [...services].reverse().forEach(service => {
      if (service.state === '运行中') appendLog(lines, `已停止${service.name}。`);
      service.state = '已停止';
    });
    draw();
    setMessage(message, '已按相反顺序停止全部服务。', 'success');
  });
  const start = button('mock-services-start', '启动全部', () => {
    services.forEach(service => { service.state = '运行中'; appendLog(lines, `${service.name}已启动。`); });
    draw();
    setMessage(message, '4 项服务已按依赖顺序启动。', 'success');
  }, 'primary');
  const fail = button('mock-services-fail', '模拟失败回滚', () => {
    services.forEach(service => { service.state = '未启动'; });
    appendLog(lines, '重新演示启动流程。');
    services.slice(0, 2).forEach(service => { service.state = '运行中'; appendLog(lines, `${service.name}已启动。`); });
    services[2].state = '启动失败';
    appendLog(lines, '数据仓储启动失败。');
    [services[1], services[0]].forEach(service => { service.state = '已回滚'; appendLog(lines, `已回滚${service.name}。`); });
    draw();
    setMessage(message, '数据仓储启动失败；已回滚配置与日志服务，后台任务未启动。', 'warning');
  });
  function draw() {
    const running = services.filter(service => service.state === '运行中').length;
    metrics.replaceChildren(stats([['服务总数', 4], ['运行中', running], ['启动异常', services.filter(service => service.state === '启动失败').length]]));
    rows.replaceChildren(table(['服务', '依赖', '状态'], services.map(service => [service.name, service.dependency, badge(service.state)])));
    stop.disabled = running === 0;
    start.disabled = running === services.length;
    showLog(log, lines);
  }
  container.replaceChildren(metrics, panel('服务状态', rows, group(start, stop, fail), message), panel('启动与释放记录', log));
  draw();
  setMessage(message, '4 项服务运行中，后台任务已就绪。', 'success');
  return () => scope.dispose();
}

function renderStorage(container) {
  const scope = makeScope();
  const seed = makeRecords();
  let records = cloneRows(seed);
  let schema = 1;
  let sequence = records.length + 1;
  let backupNumber = 0;
  const snapshots = [
    {id: 'today', name: '今日 09:00', rows: cloneRows(seed.slice(0, 20)), schema: 1},
    {id: 'yesterday', name: '昨日 17:30', rows: cloneRows(seed.slice(0, 18)), schema: 1}
  ];
  const snapshot = select('选择恢复快照', snapshots.map(item => [item.id, `${item.name} · ${item.rows.length} 条`]), 'today');
  snapshot.control.id = 'mock-storage-snapshot';
  const metrics = box('mock-metrics');
  const rows = box();
  const backupRows = box();
  const message = box();
  message.setAttribute('aria-live', 'polite');
  const add = button('mock-storage-add', '新增样例', () => {
    const id = sequence++;
    records.unshift({id, name: `新增样例 ${id}`, category: '数据工具', owner: '演示用户', status: '待处理', updated: '刚刚', note: '本次新增的样例', amount: 1480});
    draw();
    setMessage(message, `已新增一条记录，目前共 ${records.length} 条。`, 'success');
  }, 'primary');
  const backup = button('mock-storage-backup', '创建备份', () => {
    backupNumber += 1;
    const item = {id: `manual-${backupNumber}`, name: `手动快照 ${backupNumber}`, rows: cloneRows(records), schema};
    snapshots.unshift(item);
    // Keep the scene bounded even after repeated interactions.
    if (snapshots.length > 8) snapshots.pop();
    refreshChoices(item.id);
    draw();
    setMessage(message, `已创建「${item.name}」，保存 ${item.rows.length} 条记录。`, 'success');
  });
  const restore = button('mock-storage-restore', '恢复所选快照', () => {
    const item = snapshots.find(candidate => candidate.id === snapshot.control.value);
    if (!item) return;
    records = cloneRows(item.rows);
    schema = item.schema;
    draw();
    setMessage(message, `已恢复「${item.name}」，当前 ${records.length} 条记录。`, 'success');
  });
  const upgrade = button('mock-storage-upgrade', '模拟升级', () => {
    schema = 2;
    draw();
    setMessage(message, `数据结构已升级，${records.length} 条样例全部保留。`, 'success');
  });
  function refreshChoices(selected) {
    snapshot.control.replaceChildren(...snapshots.map(item => {
      const option = element('option', `${item.name} · ${item.rows.length} 条`);
      option.value = item.id;
      return option;
    }));
    snapshot.control.value = selected;
  }
  function draw() {
    metrics.replaceChildren(stats([['当前记录', records.length], ['可用快照', snapshots.length], ['数据结构', schema === 1 ? '原始样例' : '已升级']]));
    rows.replaceChildren(table(['记录', '分类', '状态'], records.slice(0, 5).map(row => [row.name, row.category, badge(row.status)])));
    backupRows.replaceChildren(table(['快照', '记录数', '数据结构'], snapshots.slice(0, 4).map(item => [item.name, String(item.rows.length), item.schema === 1 ? '原始样例' : '已升级'])));
    upgrade.disabled = schema === 2;
  }
  container.replaceChildren(metrics,
    panel('当前样例数据', rows, group(add, backup, upgrade)),
    panel('备份与恢复', backupRows, group(snapshot.wrap, restore), message));
  draw();
  setMessage(message, '已载入 24 条记录，2 个快照可用于恢复。', 'success');
  return () => scope.dispose();
}

function renderRuntime(container) {
  const scope = makeScope();
  const sample = {workspace: '示例工作区', theme: 'light', pageSize: 20, notifications: true};
  const editor = element('textarea', undefined, 'mock-input');
  editor.id = 'mock-runtime-config';
  editor.rows = 8;
  editor.spellcheck = false;
  editor.maxLength = 12000;
  editor.value = JSON.stringify(sample, null, 2);
  const label = element('label', '应用配置');
  label.htmlFor = editor.id;
  const field = element('div', undefined, 'mock-field');
  field.append(label, editor);
  const message = box();
  message.setAttribute('aria-live', 'polite');
  const result = box();
  const instance = box();
  let accepted = {...sample};
  function showAccepted() {
    result.replaceChildren(table(['检查项', '当前有效值', '结果'], [
      ['工作区', accepted.workspace, badge('有效')],
      ['主题', accepted.theme === 'light' ? '浅色' : '深色', badge('有效')],
      ['每页条数', String(accepted.pageSize), badge('有效')],
      ['通知', accepted.notifications ? '开启' : '关闭', badge('有效')]
    ]));
  }
  function validate() {
    try {
      const value = JSON.parse(editor.value);
      if (value === null || Array.isArray(value) || typeof value !== 'object') throw new Error('配置需要是一个对象。');
      if (typeof value.workspace !== 'string' || !value.workspace.trim()) throw new Error('工作区名称不能为空。');
      if (!['light', 'dark'].includes(value.theme)) throw new Error('主题请选择 light 或 dark。');
      if (!Number.isInteger(value.pageSize) || value.pageSize < 1 || value.pageSize > 100) throw new Error('每页条数必须是 1 到 100 的整数。');
      if (typeof value.notifications !== 'boolean') throw new Error('通知开关必须为 true 或 false。');
      accepted = {...value};
      showAccepted();
      setMessage(message, '配置检查通过，右侧已更新为当前有效配置。', 'success');
    } catch (error) {
      const detail = error instanceof SyntaxError ? 'JSON 格式有误，请检查引号、逗号与括号。' : error.message;
      setMessage(message, `${detail} 已保留上次有效配置。`, 'error');
    }
  }
  const check = button('mock-runtime-check', '检查配置', validate, 'primary');
  const invalid = button('mock-runtime-invalid', '填入错误配置', () => {
    editor.value = JSON.stringify({...sample, pageSize: 0}, null, 2);
    validate();
  });
  const reset = button('mock-runtime-reset', '恢复样例', () => {
    editor.value = JSON.stringify(sample, null, 2);
    validate();
  });
  const second = button('mock-runtime-second', '模拟第二实例', () => {
    setMessage(instance, '第二实例已被拦截，当前主实例继续运行。', 'warning');
  });
  const directories = table(['样例目录', '用途', '状态'], [
    ['/demo-workspace/data', '应用数据', badge('已就绪')],
    ['/demo-workspace/logs', '运行日志', badge('已就绪')],
    ['/demo-workspace/cache', '临时缓存', badge('已就绪')]
  ]);
  const layout = box('mock-split');
  layout.append(panel('修改配置', field, group(check, invalid, reset), message), panel('检查结果', result));
  container.replaceChildren(panel('工作区目录', directories), layout, panel('单实例守卫', group(second), instance));
  showAccepted();
  setMessage(message, '样例配置检查通过，4 项设置均有效。', 'success');
  setMessage(instance, '主实例正在运行。', 'success');
  return () => scope.dispose();
}

function renderRedact(container) {
  const scope = makeScope();
  const example = {
    actor: '演示操作者',
    account: {username: 'demo_user', password: 'demo-password', api_key: 'demo-api-key'},
    request: {operation: '查询样例', token: 'demo-token-001', authorization: 'Bearer demo-access', page: 1},
    devices: [{name: '桌面终端 A', secret: 'demo-device-secret', state: 'online'}, {name: '桌面终端 B', secret: 'demo-secret-b', state: 'idle'}],
    result: {count: 24, category: '样例数据'}
  };
  const editor = element('textarea', undefined, 'mock-input');
  editor.id = 'mock-redact-input';
  editor.rows = 14;
  editor.spellcheck = false;
  editor.maxLength = 20000;
  editor.value = JSON.stringify(example, null, 2);
  const label = element('label', '原始内容');
  label.htmlFor = editor.id;
  const raw = element('div', undefined, 'mock-field');
  raw.append(label, editor);
  const output = element('pre', JSON.stringify(redact(example), null, 2), 'mock-result');
  output.id = 'mock-redact-output';
  const metrics = box('mock-metrics');
  const message = box();
  message.setAttribute('aria-live', 'polite');
  const audit = box();
  let processed = 1;
  const lines = ['首次样例已处理，6 个敏感字段已隐藏。'];
  function drawAudit() { showLog(audit, lines); }
  function updateMetrics() {
    const count = (output.textContent.match(/\[REDACTED\]/g) || []).length;
    metrics.replaceChildren(stats([['本次隐藏字段', count], ['成功处理', processed], ['审计记录', lines.length]]));
  }
  function process() {
    try {
      if (editor.value.length > 20000) throw new Error('内容过长，请使用较小的样例。');
      const value = JSON.parse(editor.value);
      output.textContent = JSON.stringify(redact(value), null, 2);
      processed += 1;
      appendLog(lines, `第 ${processed} 次处理成功，敏感字段已隐藏。`);
      setMessage(message, '已更新脱敏结果；名称、状态与记录数保持可读。', 'success');
    } catch (error) {
      const detail = error instanceof SyntaxError ? 'JSON 格式无效。' : error.message;
      appendLog(lines, '本次处理失败，保留了上次有效结果。');
      setMessage(message, `${detail} 右侧仍显示上次有效结果。`, 'error');
    }
    updateMetrics();
    drawAudit();
  }
  const run = button('mock-redact-run', '重新处理', process, 'primary');
  const invalid = button('mock-redact-invalid', '填入错误 JSON', () => {
    editor.value = '{"account": ';
    process();
  });
  const reset = button('mock-redact-reset', '恢复样例', () => {
    editor.value = JSON.stringify(example, null, 2);
    process();
  });
  const compare = box('mock-split');
  compare.append(panel('处理前', raw), panel('处理后', output));
  container.replaceChildren(metrics, group(run, invalid, reset), message, compare, panel('审计记录', audit));
  updateMetrics();
  drawAudit();
  setMessage(message, '初始样例已完成脱敏，可以修改左侧内容后重新处理。', 'success');
  return () => scope.dispose();
}

function renderSearch(container, context = {}) {
  const scope = makeScope();
  const latest = new LatestRequest();
  let disposed = false;
  let generation = 0;
  let debounce = null;
  const fallback = [
    {name: '数据表格', kind: 'component', summary: '筛选与分页查看记录'},
    {name: '配置表单', kind: 'component', summary: '编辑字段并验证输入'},
    {name: '筛选与联想', kind: 'component', summary: '组合筛选与关键词提示'},
    {name: '页面导航', kind: 'component', summary: '切换页面并保留状态'},
    {name: '后台任务', kind: 'workflow', summary: '取消查询并拒绝迟到结果'},
    {name: '批量打印', kind: 'workflow', summary: '处理报告队列与取消任务'},
    {name: '备份恢复', kind: 'library', summary: '保存快照并恢复样例'},
    {name: '服务管理', kind: 'library', summary: '按依赖启动与失败回滚'},
    {name: '结构化日志', kind: 'tool', summary: '查看脱敏与审计结果'}
  ];
  const capabilities = Array.isArray(context.capabilities) && context.capabilities.length >= 5 ? context.capabilities : fallback;
  const labels = {component: '界面组件', workflow: '组合流程', library: '基础能力', tool: '工程工具', adapter: '设备适配'};
  const matches = query => capabilities.filter(item => `能力 ${item.name} ${item.id || ''} ${item.summary || ''} ${(item.tags || []).join(' ')}`.toLocaleLowerCase().includes(query.toLocaleLowerCase()));
  const query = input('搜索关键词', '能力', 'search');
  query.control.id = 'mock-search-query';
  query.control.maxLength = 120;
  let results = matches('能力');
  const metrics = box('mock-metrics');
  const rows = box();
  const message = box();
  message.setAttribute('aria-live', 'polite');
  const history = box();
  const lines = [`已展示关键词「能力」的 ${results.length} 项结果。`];
  let loading = false;
  function draw() {
    metrics.replaceChildren(stats([['匹配结果', results.length], ['当前展示', Math.min(results.length, 8)], ['查询状态', loading ? '处理中' : '已就绪']]));
    if (results.length) rows.replaceChildren(table(['能力', '分类', '状态'], results.slice(0, 8).map(item => [item.name, labels[item.kind] || '基础能力', badge('可查看')])));
    else rows.replaceChildren(status('没有找到匹配结果，可以尝试「表格」或「表单」。', 'warning'));
    cancel.disabled = !loading;
    showLog(history, lines);
  }
  async function runSearch(forceTimeout = false) {
    scope.clear(debounce);
    debounce = null;
    const value = query.control.value.trim();
    generation += 1;
    const request = generation;
    latest.cancel();
    if (!value) {
      loading = false;
      draw();
      setMessage(message, '请输入关键词，上次结果仍保留。');
      return;
    }
    loading = true;
    draw();
    setMessage(message, `正在查询「${value}」，保留上次结果。`);
    const isTimeout = forceTimeout || value === '超时';
    const result = await latest.start(value, isTimeout ? 700 : 360);
    if (disposed || request !== generation || result.cancelled) return;
    loading = false;
    if (isTimeout) {
      appendLog(lines, `「${value}」查询超时，结果未替换。`);
      setMessage(message, '本次查询超时，已保留上次结果；可以重新搜索。', 'warning');
    } else {
      results = matches(value);
      appendLog(lines, `「${value}」返回 ${results.length} 项结果。`);
      setMessage(message, `已交付最新查询「${value}」，共 ${results.length} 项。`, 'success');
    }
    draw();
  }
  const search = button('mock-search-run', '立即搜索', () => runSearch(), 'primary');
  const cancel = button('mock-search-cancel', '取消查询', () => {
    scope.clear(debounce);
    debounce = null;
    generation += 1;
    latest.cancel();
    loading = false;
    appendLog(lines, '查询已取消，迟到结果不会替换当前列表。');
    draw();
    setMessage(message, '已取消查询，上次结果仍保留。', 'warning');
  });
  const timeout = button('mock-search-timeout', '模拟超时', () => {
    query.control.value = '超时';
    runSearch(true);
  });
  const reset = button('mock-search-reset', '恢复样例', () => {
    scope.clear(debounce);
    debounce = null;
    generation += 1;
    latest.cancel();
    loading = false;
    query.control.value = '能力';
    results = matches('能力');
    appendLog(lines, `已恢复 ${results.length} 项样例结果。`);
    draw();
    setMessage(message, '已恢复初始关键词与完整样例。', 'success');
  });
  listen(scope, query.control, 'input', () => {
    scope.clear(debounce);
    generation += 1;
    latest.cancel();
    loading = Boolean(query.control.value.trim());
    draw();
    setMessage(message, loading ? '等待输入完成，上次结果仍保留。' : '请输入关键词，上次结果仍保留。');
    if (loading) debounce = scope.later(() => runSearch(), 260);
  });
  scope.onDispose(() => { disposed = true; generation += 1; latest.cancel(); });
  container.replaceChildren(metrics, panel('搜索能力', query.wrap, group(search, cancel, timeout, reset), message), panel('查询结果', rows), panel('查询记录', history));
  draw();
  setMessage(message, `关键词「能力」已有 ${results.length} 项结果，可继续搜索。`, 'success');
  return () => scope.dispose();
}

export const systemScenes = {
  printing: renderPrinting,
  transport: renderTransport,
  services: renderServices,
  storage: renderStorage,
  runtime: renderRuntime,
  redact: renderRedact,
  search: renderSearch
};
