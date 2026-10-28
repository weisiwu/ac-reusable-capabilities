// DOM helpers and bounded lifetimes for browser-only examples.
export function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined && text !== null) node.textContent = String(text);
  if (className) node.className = className;
  return node;
}

export function action(label, onClick, variant = '') {
  const button = element('button', label, variant);
  button.type = 'button';
  button.addEventListener('click', onClick);
  return button;
}

export function input(label, value = '', type = 'text') {
  const wrap = element('label', undefined, 'mock-field');
  const control = element('input', undefined, 'mock-input');
  control.type = type;
  control.value = value;
  wrap.append(element('span', label), control);
  return {wrap, control};
}

export function select(label, options, value = '') {
  const wrap = element('label', undefined, 'mock-field');
  const control = element('select', undefined, 'mock-input');
  for (const entry of options) {
    const [key, title] = Array.isArray(entry) ? entry : [entry, entry];
    const option = element('option', title);
    option.value = String(key);
    control.append(option);
  }
  control.value = value;
  wrap.append(element('span', label), control);
  return {wrap, control};
}

export function table(headers, rows) {
  const wrap = element('div', undefined, 'mock-table-wrap');
  const node = element('table', undefined, 'mock-table');
  const head = element('thead');
  const heading = element('tr');
  for (const title of headers) {
    const cell = element('th', title);
    cell.scope = 'col';
    heading.append(cell);
  }
  head.append(heading);
  const body = element('tbody');
  for (const row of rows) {
    const tr = element('tr');
    for (const value of row) {
      const cell = element('td');
      if (value && typeof value === 'object' && value.nodeType) cell.append(value);
      else cell.textContent = value === undefined || value === null ? '' : String(value);
      tr.append(cell);
    }
    body.append(tr);
  }
  if (!rows.length) {
    const tr = element('tr');
    const cell = element('td', '没有匹配记录，调整条件后可恢复样例。');
    cell.colSpan = headers.length;
    tr.append(cell);
    body.append(tr);
  }
  node.append(head, body);
  wrap.append(node);
  return wrap;
}

export function status(text, tone = 'info') {
  const node = element('p', text, `mock-status ${tone}`);
  node.setAttribute('role', 'status');
  return node;
}

export function stats(entries) {
  const list = element('dl', undefined, 'mock-stats');
  for (const [title, value] of entries) {
    const item = element('div', undefined, 'mock-stat');
    item.append(element('dt', title), element('dd', value));
    list.append(item);
  }
  return list;
}

export function group(...nodes) {
  const row = element('div', undefined, 'mock-actions');
  row.append(...nodes);
  return row;
}

export function makeScope() {
  const timers = new Set();
  const cleanups = new Set();
  let active = true;
  const clear = identity => {
    clearTimeout(identity);
    clearInterval(identity);
    timers.delete(identity);
  };
  return {
    later(callback, delay) {
      if (!active) return null;
      const identity = setTimeout(() => {
        timers.delete(identity);
        if (active) callback();
      }, delay);
      timers.add(identity);
      return identity;
    },
    repeat(callback, delay) {
      if (!active) return null;
      const identity = setInterval(() => {if (active) callback();}, delay);
      timers.add(identity);
      return identity;
    },
    clear,
    onDispose(callback) {
      if (active) cleanups.add(callback);
      else callback();
    },
    dispose() {
      if (!active) return;
      active = false;
      for (const identity of timers) clear(identity);
      for (const callback of cleanups) callback();
      cleanups.clear();
    },
  };
}
