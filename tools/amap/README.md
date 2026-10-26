# Clean English Amap iframe

Published assets live in `static/maps/amap/`. Contact embeds the same-origin
`map.html`; the build fingerprints its scripts, stylesheet and iframe URL.

The owner supplied a Web (JS API) application configuration for browser use.
`config.js` is intentionally browser-visible. Keep the application restricted to
`hmd-lab.com` and `hanmd1990.github.io`; never put account tokens or passwords here.
Amap recommends a server-side service proxy to keep securityJsCode private. This
adapter also supports that through `serviceHost` if a proxy is introduced later.

The adapter requests English labels, converts the existing WGS84 building
position to GCJ-02 with Amap, and creates exactly one non-interactive red pin.
It does not create a location card, search box, routing panel, app-opening button
or text label. Amap's required attribution remains visible. Navigation uses the
three existing buttons outside the iframe.

JS API 2.0 uses `languageCode: 'en'` and `logoLanguage: 'en'`; the older 1.4
`lang` option is not the current language setting. Amap's current documentation
requires the owner to enable multilingual map permission for the application
through a support ticket. Setting the parameters alone does not grant that
permission. Do not claim English production tiles have been verified without
checking the live map and the application's entitlement.

Run `node --test tools/amap/map.test.cjs` to check configuration order, language,
coordinate conversion, marker behavior and failure handling with an SDK stub.
The stub does not establish live provider availability or production domain
whitelisting; check the actual website after key changes.

Official documentation:
- https://developer.amap.com/api/javascript-api-v2/guide/abc/jscode
- https://lbs.amap.com/api/javascript-api/reference/map
- https://lbs.amap.com/api/javascript-api-v2/guide/map/englishmap
