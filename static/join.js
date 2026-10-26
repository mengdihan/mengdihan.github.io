/* Recruitment tabs: switch advertisements in place without anchor scrolling. */
(() => {
  'use strict';
  const list = document.querySelector('.lab-join-nav[role="tablist"]');
  if (!list) return;
  const tabs = Array.from(list.querySelectorAll('[role="tab"]'));
  const panels = tabs.map(tab => document.getElementById(tab.getAttribute('aria-controls')));
  function select(index, focus = false, updateURL = false) {
    tabs.forEach((tab, position) => {
      const active = position === index;
      tab.setAttribute('aria-selected', String(active));
      tab.tabIndex = active ? 0 : -1;
      panels[position].hidden = !active;
    });
    if (focus) tabs[index].focus({ preventScroll: true });
    if (updateURL) history.replaceState(null, '', '#'+panels[index].id);
  }
  function readHash() {
    const id = location.hash.slice(1);
    const index = panels.findIndex(panel => panel.id === id || (id === 'masters' && panel.id === 'phd'));
    select(index < 0 ? 0 : index);
  }
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => select(index, false, true));
    tab.addEventListener('keydown', event => {
      let next;
      if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
      if (event.key === 'ArrowLeft') next = (index + tabs.length - 1) % tabs.length;
      if (event.key === 'Home') next = 0;
      if (event.key === 'End') next = tabs.length - 1;
      if (next === undefined) return;
      event.preventDefault();
      select(next, true, true);
    });
  });
  readHash();
  window.addEventListener('hashchange', readHash);
})();
