import test from 'node:test';
import assert from 'node:assert/strict';
import {makeRecords} from '../assets/mock-data.mjs';
import {makeScope} from '../assets/demo-kit.mjs';
import {sceneRenderers} from '../assets/scene-registry.mjs';
import {readFileSync} from 'node:fs';

test('every registered browser capability has a concrete interactive renderer', () => {
  const {scenes} = JSON.parse(readFileSync(new URL('../demos.json', import.meta.url), 'utf8'));
  assert.equal(new Set(scenes.map(item => item.capability_id)).size, scenes.length);
  assert.equal(new Set(scenes.map(item => item.renderer)).size, scenes.length);
  assert.deepEqual(new Set(Object.keys(sceneRenderers)), new Set(scenes.map(item => item.renderer)));
  for (const scene of scenes) {
    assert.equal(typeof sceneRenderers[scene.renderer], 'function');
    assert(scene.summary && scene.title && scene.group);
  }
});

test('sample records are complete, distinct and reset without shared mutation', () => {
  const first = makeRecords();
  const second = makeRecords();
  assert.equal(first.length, 24);
  assert.equal(new Set(first.map(item => item.id)).size, first.length);
  assert.equal(new Set(first.map(item => item.name)).size, first.length);
  for (const item of first) {
    for (const field of ['id','name','category','owner','status','updated','note']) assert(item[field]);
    assert(Number.isFinite(item.amount));
  }
  first[0].name = 'changed';
  first.pop();
  assert.equal(second.length, 24);
  assert.notEqual(second[0].name, 'changed');
});

test('leaving a scene releases pending work and invokes disposal once', async () => {
  const scope = makeScope();
  let changes = 0;
  let cleanup = 0;
  scope.later(() => {changes += 1;}, 15);
  scope.repeat(() => {changes += 1;}, 15);
  scope.onDispose(() => {cleanup += 1;});
  scope.dispose();
  scope.dispose();
  await new Promise(resolve => setTimeout(resolve, 35));
  assert.equal(changes, 0);
  assert.equal(cleanup, 1);
  assert.equal(scope.later(() => {changes += 1;}, 0), null);
});

test('completed and explicitly stopped work do not leave an active scene timer', async () => {
  const scope = makeScope();
  try {
    let count = 0;
    const stopped = scope.later(() => {count += 100;}, 15);
    scope.clear(stopped);
    await new Promise(resolve => scope.later(() => {count += 1; resolve();}, 1));
    await new Promise(resolve => setTimeout(resolve, 25));
    assert.equal(count, 1);
  } finally {scope.dispose();}
});
