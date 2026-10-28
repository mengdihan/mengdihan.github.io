/* HMD Lab: automatic GA4 and Baidu measurement on the production host. */
(() => {
  'use strict';
  if (!['hmd-lab.com', 'www.hmd-lab.com', 'mengdihan.github.io'].includes(location.hostname)) return;
  const id = 'G-WPKN8C626L';
  let previouslyDeclined = false;
  try { previouslyDeclined = localStorage.getItem('hmd-analytics-consent-v1') === 'declined'; } catch { /* No stored preference available. */ }
  if (navigator.globalPrivacyControl === true || navigator.doNotTrack === '1' || previouslyDeclined) {
    window['ga-disable-' + id] = true;
    return;
  }
  // Site-specific code supplied by the owner from Baidu Tongji.
  if (!document.querySelector('script[data-hmd-baidu-tag]')) {
    window._hmt = window._hmt || [];
    const baidu = document.createElement('script');
    baidu.async = true;
    baidu.dataset.hmdBaiduTag = 'true';
    baidu.src = 'https://hm.baidu.com/hm.js?a41405dd5bbde883fd62a55a5ae775a7';
    document.head.append(baidu);
  }
  if (document.querySelector('script[data-hmd-ga-tag]')) return;
  window.dataLayer = window.dataLayer || [];
  const gtag = function () { window.dataLayer.push(arguments); };
  gtag('js', new Date());
  gtag('config', id, {
    allow_google_signals: false,
    allow_ad_personalization_signals: false,
    page_location: location.origin + location.pathname,
    page_referrer: document.referrer ? document.referrer.split(/[?#]/)[0] : ''
  });
  const script = document.createElement('script');
  script.async = true;
  script.dataset.hmdGaTag = 'true';
  script.src = 'https://www.googletagmanager.com/gtag/js?id=' + id;
  document.head.append(script);
})();
