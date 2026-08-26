(() => {
  const storageKey = "book-sidebar-collapsed";
  const root = document.documentElement;
  const button = document.querySelector("[data-book-sidebar-toggle]");
  const sidebar = document.querySelector(".md-sidebar--primary");

  if (!button || !sidebar) return;

  sidebar.id = "book-primary-sidebar";
  button.setAttribute("aria-controls", sidebar.id);

  const updateButton = () => {
    const collapsed = root.classList.contains("book-sidebar-collapsed");
    const label = collapsed ? "显示章节目录" : "隐藏章节目录";
    button.setAttribute("aria-expanded", String(!collapsed));
    button.setAttribute("aria-label", label);
    button.dataset.bookTooltip = label;
  };

  button.addEventListener("click", () => {
    const collapsed = root.classList.toggle("book-sidebar-collapsed");
    try {
      localStorage.setItem(storageKey, String(collapsed));
    } catch {
      // 浏览器禁用本地存储时，开关在当前页面中仍可正常使用。
    }
    updateButton();
  });

  updateButton();
})();
