/* eslint-disable no-undef */
/**
 * Back to home button
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

const markerPosition = document.querySelector(".marker-position");

const htmlTemplate =
  '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><path d="M32 18.451L16 6.031 0 18.451v-5.064L16 .967l16 12.42zM28 18v12h-8v-8h-8v8H4V18l12-9z" /></svg>';

const customControl = L.Control.extend({
  options: {
    position: "topleft",
  },

  onAdd: () => {
    const btn = L.DomUtil.create("button");
    btn.title = "back to home";
    btn.innerHTML = htmlTemplate;
    btn.className += "leaflet-bar back-to-home hidden";

    L.DomEvent.disableClickPropagation(btn);

    return btn;
  },
});

map.addControl(new customControl());

const buttonBackToHome = document.querySelector(".back-to-home");

function compareToArrays(a, b) {
  return JSON.stringify(a) === JSON.stringify(b);
}

function updateCenterInfo() {
  const { lat: centerLat, lng: centerLng } = map.getCenter();
  const latRounded = +centerLat.toFixed(3);
  const lngRounded = +centerLng.toFixed(3);
  const defaultCoordinate = [+lat.toFixed(3), +lng.toFixed(3)];
  const centerCoordinate = [latRounded, lngRounded];

  markerPosition.textContent = `center: ${latRounded}, ${lngRounded}`;

  if (compareToArrays(centerCoordinate, defaultCoordinate)) {
    buttonBackToHome.classList.add("hidden");
    return;
  }

  buttonBackToHome.classList.remove("hidden");
}

buttonBackToHome.addEventListener("click", () => {
  map.flyTo([lat, lng], zoom);
});

map.on("moveend", updateCenterInfo);
updateCenterInfo();
