/* Chinese basemap and one non-interactive pin. No search, route UI or info window. */
(() => {
  'use strict';
  const status = document.getElementById('map-status');
  const config = window.HMD_AMAP_CONFIG || {};
  const unavailable = () => {
    status.hidden = false;
    status.textContent = 'Map unavailable. Please use the navigation buttons below.';
  };
  if (!config.key || !(config.serviceHost || config.securityJsCode)) {
    unavailable();
    return;
  }
  if (config.serviceHost && !/^https:\/\//.test(config.serviceHost)) {
    unavailable();
    return;
  }
  window._AMapSecurityConfig = config.serviceHost
    ? {serviceHost: config.serviceHost}
    : {securityJsCode: config.securityJsCode};
  const timeout = setTimeout(unavailable, 20000);
  const fail = () => { clearTimeout(timeout); unavailable(); };
  const script = document.createElement('script');
  script.src = 'https://webapi.amap.com/maps?v=2.0&key=' + encodeURIComponent(config.key);
  script.async = true;
  script.onerror = fail;
  script.onload = () => {
    try {
      if (!window.AMap) return fail();
      // The stored building position is WGS84; Amap uses GCJ-02.
      window.AMap.convertFrom([116.3101824, 39.9929816], 'gps', (result, data) => {
        try {
          if (result !== 'complete' || !data?.locations?.length) return fail();
          const position = data.locations[0];
          const map = new window.AMap.Map('map', {
            center: position, zoom: 17, viewMode: '2D',
            isHotspot: false, showIndoorMap: false,
            dragEnable: true, keyboardEnable: true,
            scrollWheel: true, doubleClickZoom: true
          });
          const pin = '<svg width="24" height="34" viewBox="0 0 24 34" aria-hidden="true"><path d="M12 33C10 29 1 19 1 12a11 11 0 0 1 22 0c0 7-9 17-11 21Z" fill="#d93025" stroke="#fff" stroke-width="1.5"/><circle cx="12" cy="12" r="4" fill="#fff"/></svg>';
          map.add(new window.AMap.Marker({
            position, content: pin, offset: new window.AMap.Pixel(-12, -34),
            clickable: false, cursor: 'default'
          }));
          map.on('complete', () => { clearTimeout(timeout); status.hidden = true; });
        } catch { fail(); }
      });
    } catch { fail(); }
  };
  document.head.append(script);
})();
