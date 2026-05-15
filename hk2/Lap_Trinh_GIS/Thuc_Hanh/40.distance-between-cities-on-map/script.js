/* eslint-disable no-undef */
/**
 * Distance between cities on map
 */

const config = {
  minZoom: 2,
  maxZoom: 18,
};

const zoom = 7;
const lat = 52.22977;
const lng = 21.01178;

const map = L.map("map", config).setView([lat, lng], zoom);

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);

const length = document.querySelector(".length");
const cityA = document.querySelector("#cityA");
const cityB = document.querySelector("#cityB");
const clearButton = document.querySelector(".clear-distance");

let markerSelections = {
  cityA: null,
  cityB: null,
};
let markerLayers = [];
let routeLine = null;

function results({ currentValue, matches, template }) {
  const regex = new RegExp(currentValue, "i");

  return matches.length === 0
    ? template
    : matches
        .map((element) => {
          return `
            <li class="autocomplete-item" role="option" aria-selected="false">
              <p>${element.properties.display_name.replace(
                regex,
                (str) => `<b>${str}</b>`
              )}</p>
            </li>
          `;
        })
        .join("");
}

function nominatim(currentValue) {
  const api = `https://nominatim.openstreetmap.org/search?format=geojson&limit=5&q=${encodeURI(
    currentValue
  )}`;

  return new Promise((resolve) => {
    fetch(api)
      .then((response) => response.json())
      .then((data) => {
        resolve(data.features);
      })
      .catch((error) => {
        console.error(error);
        resolve([]);
      });
  });
}

function clearMapLayers() {
  markerLayers.forEach((layer) => map.removeLayer(layer));
  markerLayers = [];

  if (routeLine) {
    map.removeLayer(routeLine);
    routeLine = null;
  }
}

function resetView() {
  map.setView([lat, lng], zoom);
}

function clearData() {
  markerSelections = {
    cityA: null,
    cityB: null,
  };
  clearMapLayers();
  resetView();
  length.textContent = "Markers and plines have been removed";
}

function distanceBetweenMarkers() {
  const orderedCoords = [markerSelections.cityA, markerSelections.cityB];
  const from = L.marker(orderedCoords[0]).getLatLng();
  const to = L.marker(orderedCoords[1]).getLatLng();
  const distance = from.distanceTo(to) / 1000;

  length.textContent = `Length (in kilometers): ${distance.toFixed(5)}`;
}

function updateRoute() {
  const orderedSelections = [
    { id: "cityA", coords: markerSelections.cityA, input: cityA },
    { id: "cityB", coords: markerSelections.cityB, input: cityB },
  ];
  const activeSelections = orderedSelections.filter((item) => item.coords);

  clearMapLayers();

  markerLayers = activeSelections.map(({ coords, input }, index) => {
    const marker = L.marker(coords, {
      title: input.value || `City ${index + 1}`,
    }).addTo(map);

    if (input.value) {
      marker.bindPopup(input.value);
    }

    return marker;
  });

  if (activeSelections.length === 2) {
    routeLine = L.polyline(
      [markerSelections.cityA, markerSelections.cityB],
      {
      color: "red",
      }
    ).addTo(map);

    const group = L.featureGroup(
      routeLine ? [...markerLayers, routeLine] : markerLayers
    );

    map.fitBounds(group.getBounds(), {
      padding: [20, 20],
    });

    distanceBetweenMarkers();
    return;
  }

  if (activeSelections.length === 1) {
    map.setView(activeSelections[0].coords, 8);
    length.textContent = "Select one more city";
    return;
  }

  length.textContent = "Select cities";
}

function addMarkerToMap(object, inputId) {
  const { display_name } = object.properties;
  const coords = [...object.geometry.coordinates].reverse();

  if (inputId === "cityA") {
    cityA.value = display_name;
  } else {
    cityB.value = display_name;
  }

  markerSelections[inputId] = coords;

  updateRoute();
}

window.addEventListener("DOMContentLoaded", () => {
  ["cityA", "cityB"].forEach((cityId) => {
    new Autocomplete(cityId, {
      clearButton: false,
      howManyCharacters: 2,
      onSearch: ({ currentValue }) => nominatim(currentValue),
      onResults: (object) => results(object),
      onSubmit: ({ object }) => addMarkerToMap(object, cityId),
      noResults: ({ currentValue, template }) =>
        template(`<li>No results found: "${currentValue}"</li>`),
    });
  });

  clearButton.addEventListener("click", () => {
    cityA.value = "";
    cityB.value = "";
    clearData();
    cityA.focus();
  });
});
