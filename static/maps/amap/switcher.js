/* Cross-origin iframe events cannot verify tiles; use load plus a bounded connectivity probe. */
(() => {
  'use strict';
  const container = document.getElementById('map-container');
  let settled = false, loaded = false, reachable = false, current = '';
  const show = provider => {
    if (current === provider) return;
    current = provider;
    const frame = document.createElement('iframe');
    frame.title = provider === 'google' ? 'Google Maps — ENN Engineering Building' : '高德地图 — 北京大学新奥工学大楼';
    frame.referrerPolicy = 'strict-origin-when-cross-origin';
    frame.allowFullscreen = true;
    frame.className = provider === 'google' ? 'google-map' : 'amap';
    frame.src = provider === 'google' ? 'https://www.google.com/maps?q=%E5%8C%97%E4%BA%AC%E5%B8%82%E6%B5%B7%E6%B7%80%E5%8C%BA%E4%B8%AD%E5%85%B3%E6%9D%91%E5%8C%97%E5%A4%A7%E8%A1%97116%E5%8F%B7&z=17&hl=en&output=embed' : './amap.html?v=dual-map-2';
    if (provider === 'google') frame.onload = () => { loaded = true; if (reachable) finish(true); };
    container.replaceChildren(frame);
  };
  const probe = new Image();
  const finish = success => {
    if (settled) return;
    settled = true;
    clearTimeout(timeout);
    probe.onload = probe.onerror = null;
    if (!success) show('amap');
  };
  const timeout = setTimeout(() => finish(false), 3000);
  show('google');
  probe.onload = () => { reachable = true; if (loaded) finish(true); };
  probe.onerror = () => finish(false);
  probe.src = 'https://www.google.com/mapfiles/ms/icons/red-dot.png';
})();
