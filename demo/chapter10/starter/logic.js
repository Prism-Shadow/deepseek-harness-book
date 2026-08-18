(function exposeTaskLogic(globalScope) {
  function getBlockingTasks() {
    return [];
  }

  const taskLogic = { getBlockingTasks };

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = taskLogic;
  }

  globalScope.TaskLogic = taskLogic;
})(typeof window !== 'undefined' ? window : globalThis);
