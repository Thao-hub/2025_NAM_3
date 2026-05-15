/* eslint-disable no-undef */
/**
 * location
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

map
  .locate({
    setView: true,
    enableHighAccuracy: true,
  })
  .on("locationfound", (e) => {
    console.log(e);

    const marker = L.marker([e.latitude, e.longitude]).bindPopup(
      "Your are here :)"
    );

    const circle = L.circle([e.latitude, e.longitude], e.accuracy / 2, {
      weight: 2,
      color: "red",
      fillColor: "red",
      fillOpacity: 0.1,
    });

    map.addLayer(marker);
    map.addLayer(circle);
  })
  .on("locationerror", (e) => {
    console.log(e);
    alert("Location access denied.");
  });
