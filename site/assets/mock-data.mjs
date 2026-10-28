// Fictional sample records shared by the browser demonstrations, never user data.
const projects = ['晨光', '星河', '远山', '青禾', '云帆', '北辰'];
const subjects = ['设备巡检', '资料归档', '库存盘点', '项目验收'];
const owners = ['演示成员 A', '演示成员 B', '演示成员 C', '演示成员 D'];
const categories = ['设备维护', '资料管理', '项目协作'];
const states = ['已完成', '进行中', '待处理', '已完成'];

export function makeRecords() {
  return Array.from({length: 24}, (_, index) => ({
    id: `DEMO-${String(index + 1).padStart(3, '0')}`,
    name: `${projects[index % projects.length]} · ${subjects[Math.floor(index / projects.length)]}`,
    category: categories[index % categories.length],
    owner: owners[index % owners.length],
    status: states[index % states.length],
    updated: `2026-10-${String(28 - (index % 8)).padStart(2, '0')}`,
    note: `第 ${index + 1} 条虚构样例，包含任务资料、处理状态与协作记录。`,
    amount: (index + 1) * 120,
  }));
}
