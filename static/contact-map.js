/* Keep Bing on capable browsers; provide a 2D map when WebGL is unavailable. */
(() => {
  'use strict';
  const frame = document.querySelector('.lab-contact-map-frame');
  if (!frame) return;
  let supported = false;
  try {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('webgl2') || canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    supported = Boolean(context);
    context?.getExtension('WEBGL_lose_context')?.loseContext();
  } catch (_) {}
  if (!supported) {
    frame.src = '/static/contact-map-fallback.html?v=20261024-2';
    frame.title = 'Interactive map — 北京大学新奥工学大楼';
  }
})();
