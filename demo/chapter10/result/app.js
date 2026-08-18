const tasks = [
  {
    id: 'T-101',
    title: '确认交互稿',
    owner: '产品 Agent',
    status: 'completed',
    dependencies: [],
  },
  {
    id: 'T-102',
    title: '完成任务接口',
    owner: '开发 Agent',
    status: 'in_progress',
    dependencies: [],
  },
  {
    id: 'T-103',
    title: '联调看板',
    owner: '开发 Agent',
    status: 'blocked',
    dependencies: ['T-101', 'T-102'],
  },
  {
    id: 'T-104',
    title: '发布前验收',
    owner: '测试 Agent',
    status: 'blocked',
    dependencies: ['T-103'],
  },
];

const statusLabels = {
  completed: '已完成',
  in_progress: '进行中',
  blocked: '已阻塞',
};

const board = document.querySelector('#board');
const summary = document.querySelector('#summary');

function renderTask(task) {
  const blockingTasks = TaskLogic.getBlockingTasks(task, tasks);
  const blockingReason = blockingTasks.length > 0
    ? `<p class="blocking-reason">等待：${blockingTasks.map((item) => `${item.id} ${item.title}`).join('、')}</p>`
    : '';

  return `
    <article class="task-card" data-status="${task.status}">
      <div class="task-meta">
        <span>${task.id}</span>
        <span class="status">${statusLabels[task.status]}</span>
      </div>
      <h2>${task.title}</h2>
      <p class="owner">${task.owner}</p>
      ${blockingReason}
    </article>
  `;
}

board.innerHTML = tasks.map(renderTask).join('');

const completedCount = tasks.filter((task) => task.status === 'completed').length;
summary.textContent = `${completedCount}/${tasks.length} 项已完成`;
