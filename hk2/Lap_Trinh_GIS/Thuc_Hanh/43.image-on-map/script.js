/* eslint-disable no-undef */
/**
 * image on map
 */

const config = {
  minZoom: 1,
  maxZoom: 18,
};

const zoom = 15;
const lat = 50.0595;
const lng = 19.9379;

const map = L.map("map", config).setView([lat, lng], zoom);

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);

const imageUrl =
  "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Krakow_Center_-_basic_map.svg/1440px-Krakow_Center_-_basic_map.svg.png";

const funny = L.icon({
  iconUrl: "http://grzegorztomicki.pl/serwisy/pin.png",
  iconSize: [50, 58],
  iconAnchor: [20, 58],
  popupAnchor: [0, -60],
});

const customPopup =
  '<div class="customPopup"><figure><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/A-10_Sukiennice_w_Krakowie_Krak%C3%B3w%2C_Rynek_G%C5%82%C3%B3wny_-_MM.jpg" /><figcaption>Source: wikipedia.org/figcaption</figure><div>Krakow,[a] also written in English as Krakow and traditionally known as Cracow, is the second-largest and one of the oldest cities in Poland. Situated on the Vistula River in Lesser Poland Voivodeship... <a href="https://en.wikipedia.org/wiki/Krak%C3%B3w" target="_blank"> show more</a></div></div>';

const customOptions = {
  minWidth: "220",
  keepInView: true,
};

L.marker([50.0616, 19.9373], {
  icon: funny,
})
  .bindPopup(customPopup, customOptions)
  .on("click", clickZoom)
  .addTo(map);

function clickZoom(e) {
  map.setView(e.target.getLatLng(), zoom);
}

const imageBounds = [
  [50.0665, 19.93],
  [50.0522, 19.9455],
];

L.imageOverlay(imageUrl, imageBounds, { opacity: 1 }).addTo(map);
