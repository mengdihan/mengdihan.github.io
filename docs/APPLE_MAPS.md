# Contact Apple Maps integration

Status: integration prepared; NOT activated or verified against Apple's live map service.
The campus image remains visible until a valid MapKit JS token is configured.

1. An Apple Developer account holder/admin creates a **MapKit JS** Maps token in
   Certificates, Identifiers & Profiles → Services → Maps. Restrict its allowed
   website/domain to `hanmd1990.github.io`, and set a suitable expiration date.
   Do not use a private `.p8` signing key in this repository or paste one in chat.
2. Put the public, domain-restricted browser token into `static/apple-maps-config.js`.
3. Build and deploy. Check the actual Apple search result for 新奥工学大楼,
   its pin against the existing campus map, mouse dragging, zoom controls,
   scroll zoom, and touch gestures. This live acceptance check is still required.
4. If the exact building cannot be resolved, retain the campus fallback and verify
   an Apple place identifier/coordinate in Apple Maps before changing the code.
   Do not guess coordinates or label the university gate as the laboratory.
5. Renew the browser token before expiry. Load/auth/search failures retain the
   original campus map and all external map links.

Official references:
- https://developer.apple.com/documentation/mapkitjs/creating-a-maps-token
- https://developer.apple.com/maps/web/
- https://developer.apple.com/documentation/mapkitjs/search/search1

No Apple Developer account, token or payment service has been created/enabled.
