/* eslint-disable no-undef */
/**
 * part of the common turfjs
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

const centers = [
  { lat: 52.22990558765487, lng: 21.01168513298035 },
  { lat: 52.22962958994604, lng: 21.011593937873844 },
  { lat: 52.2297445891999, lng: 21.012012362480167 },
];

const options = {
  steps: 64,
  units: "meters",
  options: {},
};

const radius = 30;
const polygons = [];

centers.map(({ lat, lng }) => {
  const polygon = turf.circle([lng, lat], radius, options);

  L.geoJSON(polygon, { color: "red", weight: 2 }).addTo(map);
  polygons.push(polygon);
});

const intersection = turf.intersect(...polygons);

const intersectionColor = {
  color: "yellow",
  weight: 2,
  opacity: 1,
  fillColor: "yellow",
  fillOpacity: 0.7,
};

L.geoJSON(intersection, { style: intersectionColor }).addTo(map);
