(function exposeTaskLogic(globalScope) {
  function getBlockingTasks(task, allTasks) {
    if (task.status !== 'blocked') {
      return [];
    }

    const dependencyIds = task.dependencies || [];

    return dependencyIds
      .map((dependencyId) => allTasks.find((candidate) => candidate.id === dependencyId))
      .filter((dependency) => dependency && dependency.status !== 'completed');
  }

  const taskLogic = { getBlockingTasks };

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = taskLogic;
  }

  globalScope.TaskLogic = taskLogic;
})(typeof window !== 'undefined' ? window : globalThis);
