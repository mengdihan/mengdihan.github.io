/* Owner preference settings: local to this browser and website origin. */
(() => {
  'use strict';
  const modeKey = 'hmd-owner-analytics-v1';
  const deviceKey = 'hmd-owner-device-v1';
  const device = document.getElementById('device');
  const status = document.getElementById('status');
  function show() {
    try {
      const saved = localStorage.getItem(deviceKey);
      if (['office', 'laptop', 'phone'].includes(saved)) device.value = saved;
      status.textContent = localStorage.getItem(modeKey) === 'exclude'
        ? '已启用：' + device.options[device.selectedIndex].text + '。百度统计：已排除；Google Analytics：已排除。'
        : '尚未排除：当前浏览器的访问按普通访客统计。';
    } catch { status.textContent = '浏览器禁止保存网站数据，设置未生效。请允许本站保存数据后重试。'; }
  }
  document.getElementById('save').addEventListener('click', () => {
    try {
      localStorage.setItem(deviceKey, device.value);
      localStorage.setItem(modeKey, 'exclude');
      if (localStorage.getItem(modeKey) !== 'exclude') throw new Error('Not saved');
      show();
    } catch { status.textContent = '保存失败，设置未生效。请允许本站保存数据后重试。'; }
  });
  document.getElementById('reset').addEventListener('click', () => {
    try { localStorage.removeItem(modeKey); localStorage.removeItem(deviceKey); show(); }
    catch { status.textContent = '无法修改设置，请检查浏览器的网站数据权限。'; }
  });
  show();
})();
