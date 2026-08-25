(() => {
  const drawer = document.querySelector('[data-md-toggle="drawer"]');
  if (!drawer) return;

  const listSelector = '.md-sidebar--primary .md-nav__list';

  document.addEventListener('wheel', (event) => {
    if (!drawer.checked || !event.deltaY) return;

    let list = event.target instanceof Element
      ? event.target.closest(listSelector)
      : null;

    while (list) {
      const maxScrollTop = list.scrollHeight - list.clientHeight;
      const canScroll = event.deltaY < 0
        ? list.scrollTop > 0
        : list.scrollTop < maxScrollTop - 1;

      if (canScroll) return;
      list = list.parentElement?.closest(listSelector) ?? null;
    }

    event.preventDefault();
  }, { capture: true, passive: false });
})();
