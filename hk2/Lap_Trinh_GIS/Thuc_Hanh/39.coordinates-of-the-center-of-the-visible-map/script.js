/* eslint-disable no-undef */
/**
 * Coordinates of the center of the visible map
 */

const config = {
  minZoom: 3,
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

map.on("dragend", updateInfo);
map.on("zoomend", updateInfo);

const coordinates = L.control({ position: "bottomleft" });

coordinates.onAdd = () => {
  const div = L.DomUtil.create("div", "center-of-map-description");
  L.DomEvent.disableClickPropagation(div);
  return div;
};

coordinates.addTo(map);

document.addEventListener("DOMContentLoaded", () => {
  updateInfo();
});

const markerPlace = document.querySelector(".center-of-map-description");

function updateInfo() {
  const { lat, lng } = map.getCenter();
  const zoom = map.getZoom();

  markerPlace.innerHTML = `center: ${lat.toFixed(5)}, ${lng.toFixed(
    5
  )} | zoom: ${zoom}`;
}
