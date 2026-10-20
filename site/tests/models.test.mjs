import test from 'node:test';
import assert from 'node:assert/strict';
import {pageRows, redact, findCapabilities, LatestRequest} from '../assets/models.mjs';

test('pagination clamps page after filters change and keeps source unchanged', () => {
  const rows = [{name:'Table',category:'ui'}, {name:'Storage',category:'data'}, {name:'Table helper',category:'data'}];
  assert.deepEqual(pageRows(rows, ' TABLE ', '', 99, 1), {rows:[rows[2]],total:2,pages:2,page:2});
  assert.equal(pageRows(rows, '', 'ui', 2).page, 1);
  assert.equal(pageRows(rows, 'none').total, 0);
  assert.equal(rows.length, 3);
  assert.throws(() => pageRows(rows, '', '', 1, 0), RangeError);
});
test('redaction recursively handles arrays without altering input or free text', () => {
  const input = {Password:'private',rows:[{token:'secret',count:0}],message:'password in text',nil:null};
  const result = redact(input);
  assert.equal(result.Password, '[REDACTED]');
  assert.equal(result.rows[0].token, '[REDACTED]');
  assert.equal(result.rows[0].count, 0);
  assert.equal(result.message, 'password in text');
  assert.equal(result.nil, null);
  assert.equal(input.Password, 'private');
});
test('capability lookup searches stable IDs and modules case insensitively', () => {
  const rows = [{name:'本地存储',id:'desktop.storage',package:'python.desktop',modules:['storage']}];
  assert.equal(findCapabilities(rows, ' STORAGE ').length, 1);
  assert.equal(findCapabilities(rows, '本地').length, 1);
  assert.equal(findCapabilities(rows, 'missing').length, 0);
});
test('latest request resolves superseded waits as cancelled even for identical text', async () => {
  const latest = new LatestRequest();
  try {
    const first = latest.start('same', 1000);
    const second = latest.start('same', 1);
    assert.deepEqual(await first, {cancelled:true});
    const result = await second;
    assert.equal(result.value, 'same');
    assert.equal(result.identity, latest.generation);
    assert.equal(latest.timer, null);
  } finally {latest.cancel();}
});
test('explicit cancellation settles the promise and releases timer', async () => {
  const latest = new LatestRequest();
  const pending = latest.start('cancelled', 1000);
  latest.cancel(); latest.cancel();
  assert.deepEqual(await pending, {cancelled:true});
  assert.equal(latest.timer, null);
});
