/* eslint-disable no-undef */
/**
 * marker-draggable-on-a-click
 */

const config = {
  minZoom: 7,
  maxZoom: 18,
};

const zoom = 18;
const lat = 52.22977;
const lng = 21.01178;

const map = L.map("map", config).setView([lat, lng], zoom);

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);

const marker = L.marker([52.22983, 21.011728]);
marker.addTo(map).bindPopup("Center Warsaw");

marker.on("click", (e) => {
  e.target.dragging.enable();
  console.log(e);
});
