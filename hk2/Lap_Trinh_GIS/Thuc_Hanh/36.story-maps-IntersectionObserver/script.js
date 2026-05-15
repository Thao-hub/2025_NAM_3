/* eslint-disable no-undef */
/**
 * Story maps
 */

const config = {
  minZoom: 7,
  maxZoom: 18,
  zoomControl: false,
};

const zoom = 18;
const lat = 52.22977;
const lng = 21.01178;

const map = L.map("map", config).setView([lat, lng], zoom);

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);

L.control.zoom({ position: "topright" }).addTo(map);

const articles = document.querySelectorAll("article");
let activeMarker = null;

function setMarker([lat, lng], title) {
  if (activeMarker) {
    map.removeLayer(activeMarker);
  }

  activeMarker = L.marker([lat, lng], { title }).addTo(map).bindPopup(title);
  activeMarker.openPopup();
}

function centerMap([lat, lng], target, title) {
  map.setView([lat, lng], 16);

  articles.forEach((article) => {
    article.classList.remove("active");
  });

  target.classList.add("active");
  setMarker([lat, lng], title);
}

function onChange(changes) {
  changes.forEach((change) => {
    const data = change.target.dataset.coordinates;
    const title = change.target.dataset.title;

    if (change.intersectionRatio > 0.5) {
      centerMap(JSON.parse(data), change.target, title);
    }
  });
}

if ("IntersectionObserver" in window) {
  const observerConfig = {
    root: null,
    rootMargin: "0px",
    threshold: [0, 0.25, 0.5, 0.75, 1],
  };

  const observer = new IntersectionObserver(onChange, observerConfig);
  articles.forEach((article) => {
    observer.observe(article);
  });
}

const firstArticle = articles[0];
if (firstArticle) {
  centerMap(
    JSON.parse(firstArticle.dataset.coordinates),
    firstArticle,
    firstArticle.dataset.title
  );
}
