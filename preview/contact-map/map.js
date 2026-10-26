/* Worldwide interactive basemap, with the verified WGS84 building position. */
(async () => {
  'use strict';
  const response = await fetch('location.json');
  if (!response.ok) throw new Error('Location unavailable');
  const loc = await response.json();
  const map = L.map('map', {
    minZoom: 0, maxZoom: 22, scrollWheelZoom: true,
    dragging: true, touchZoom: true, doubleClickZoom: true
  }).setView([loc.position[1], loc.position[0]], 17);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    minZoom: 0, maxNativeZoom: 19, maxZoom: 22,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors'
  }).addTo(map);
  const pin = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="34" viewBox="0 0 24 34" aria-hidden="true"><path d="M12 33C10 29 1 19 1 12a11 11 0 0 1 22 0c0 7-9 17-11 21Z" fill="#d93025" stroke="#fff" stroke-width="1.5"/><circle cx="12" cy="12" r="4" fill="#fff"/></svg>';
  L.marker([loc.position[1], loc.position[0]], {
    icon: L.divIcon({html: pin, className: 'labpin', iconSize: [24, 34], iconAnchor: [12, 33]}),
    alt: '北京大学新奥工学大楼', keyboard: false, interactive: false
  }).addTo(map);
  L.control.scale({imperial: false}).addTo(map);
})().catch(() => {
  document.getElementById('map').textContent = 'Map could not load. Address: Xin Ao Engineering Building, No. 116 Zhongguancun North Street, Peking University.';
});
