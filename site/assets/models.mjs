// Browser-only presentation models. Python contracts remain authoritative.
export function pageRows(rows, query = '', category = '', number = 1, size = 5) {
  if (!Number.isInteger(size) || size < 1) throw new RangeError('page size must be positive');
  const keyword = query.trim().toLocaleLowerCase();
  const filtered = rows.filter(row => (!category || row.category === category) &&
    `${row.name} ${row.category}`.toLocaleLowerCase().includes(keyword));
  const pages = Math.max(1, Math.ceil(filtered.length / size));
  const page = Math.min(pages, Math.max(1, Number.isFinite(number) ? Math.trunc(number) : 1));
  return {rows: filtered.slice((page - 1) * size, page * size), total: filtered.length, pages, page};
}

export function redact(value) {
  const secrets = new Set(['password', 'passwd', 'secret', 'token', 'api_key', 'authorization']);
  if (Array.isArray(value)) return value.map(redact);
  if (value !== null && typeof value === 'object') {
    return Object.fromEntries(Object.entries(value).map(([key, item]) =>
      [key, secrets.has(key.toLowerCase()) ? '[REDACTED]' : redact(item)]));
  }
  return value;
}

export function findCapabilities(capabilities, query, filters = {}) {
  const keyword = query.trim().toLocaleLowerCase();
  return capabilities.filter(item => {
    const text = `${item.name} ${item.id} ${item.package} ${(item.modules || []).join(' ')} ${item.summary || ''} ${(item.tags || []).join(' ')}`;
    return text.toLocaleLowerCase().includes(keyword) &&
      ['language', 'domain', 'kind'].every(key => !filters[key] || item[key] === filters[key]) &&
      (!filters.origin || (item.origin_ids || []).includes(filters.origin)) &&
      (!filters.mode || (item.modes || []).includes(filters.mode));
  });
}

export class LatestRequest {
  constructor() { this.generation = 0; this.timer = null; this.resolve = null; }
  cancel() {
    this.generation += 1;
    clearTimeout(this.timer);
    this.timer = null;
    if (this.resolve) this.resolve({cancelled: true});
    this.resolve = null;
  }
  start(value, delay = 600) {
    this.cancel();
    const identity = this.generation;
    return new Promise(resolve => {
      this.resolve = resolve;
      this.timer = setTimeout(() => {
        this.timer = null;
        this.resolve = null;
        resolve(identity === this.generation ? {value, identity} : {cancelled: true});
      }, delay);
    });
  }
}
