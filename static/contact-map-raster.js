/* Raster tiles keep the location map usable without WebGL. */
(() => {
  'use strict';
  // AMap share POI B0JRUL5E8O: GCJ-02 39.994262896822455,116.31628721952437.
  // Converted to WGS84 for OpenStreetMap; do not mix coordinate systems.
  const location = [39.9929816, 116.3101824];
  const map = L.map('map', {scrollWheelZoom: true, zoomControl: true}).setView(location, 17);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    minZoom: 2, maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors'
  }).addTo(map);
  L.marker(location, {
    icon: L.divIcon({className: 'lab-map-pin', iconSize: [20, 20], iconAnchor: [10, 10]}),
    title: '北京大学新奥工学大楼', alt: 'Laboratory location'
  }).addTo(map).bindTooltip('北京大学新奥工学大楼', {permanent: true, direction: 'top', offset: [0, -12]});
  L.control.scale({imperial: false}).addTo(map);
})();
