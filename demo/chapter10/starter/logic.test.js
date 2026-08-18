const test = require('node:test');
const assert = require('node:assert/strict');
const { getBlockingTasks } = require('./logic');

const tasks = [
  { id: 'T-101', title: '已完成的前置', status: 'completed', dependencies: [] },
  { id: 'T-102', title: '未完成的前置', status: 'in_progress', dependencies: [] },
  { id: 'T-103', title: '当前任务', status: 'blocked', dependencies: ['T-101', 'T-102'] },
];

test('只返回未完成的前置任务', () => {
  assert.deepEqual(getBlockingTasks(tasks[2], tasks), [tasks[1]]);
});

test('无依赖任务不会被标记为阻塞', () => {
  assert.deepEqual(getBlockingTasks(tasks[0], tasks), []);
});
