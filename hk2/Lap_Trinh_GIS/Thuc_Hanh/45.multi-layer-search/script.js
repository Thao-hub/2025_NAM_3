/* eslint-disable no-undef */
/**
 * multi-layer serch
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

async function fetchData(url) {
  try {
    const response = await fetch(url);
    const data = await response.json();
    return data;
  } catch (err) {
    console.error(err);
    return null;
  }
}

function clickZoom(e) {
  map.setView(e.target.getLatLng(), zoom);
}

const geojsonOpts = {
  pointToLayer: (feature, latlng) =>
    L.marker(latlng, {
      icon: L.divIcon({
        className: feature.properties.amenity,
        iconSize: L.point(16, 16),
        html: feature.properties.amenity[0].toUpperCase(),
        popupAnchor: [3, -5],
      }),
    })
      .bindPopup(
        `${feature.properties.amenity}<br><b>${feature.properties.name}</b>`
      )
      .on("click", clickZoom),
};

const poiLayers = L.layerGroup().addTo(map);

["bar", "pharmacy", "restaurant"].map((json) => {
  fetchData(`./data/${json}.json`).then((data) => {
    if (data) {
      L.geoJSON(data, geojsonOpts).addTo(poiLayers);
    }
  });
});

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

new Autocomplete("multi-layer-serch", {
  cache: true,
  selectFirst: true,

  onSearch: ({ currentValue }) => {
    const places = [];
    const safeValue = escapeRegExp(currentValue);

    poiLayers.eachLayer((layer) => {
      if (layer instanceof L.LayerGroup) {
        layer.eachLayer((markerLayer) => {
          if (markerLayer instanceof L.Marker) {
            places.push(markerLayer.feature);
          }
        });
      }
    });

    return places
      .sort((a, b) => a.properties.name.localeCompare(b.properties.name))
      .filter((element) =>
        element.properties.name.match(new RegExp(safeValue, "i"))
      );
  },

  onResults: ({ currentValue, matches, template }) => {
    const safeValue = escapeRegExp(currentValue);

    return matches.length === 0
      ? template
      : matches
          .map((element) => {
            return `
              <li class="place">
                <div>${element.properties.name.replace(
                  new RegExp(safeValue, "i"),
                  (str) => `<mark>${str}</mark>`
                )}</div>
                <div class="place-item ${element.properties.amenity}">${element.properties.amenity}</div>
              </li>
            `;
          })
          .join("");
  },

  onSubmit: ({ object }) => {
    const [placeLng, placeLat] = object.geometry.coordinates;

    map.flyTo([placeLat, placeLng]);

    poiLayers.eachLayer((layer) => {
      layer.eachLayer((markerLayer) => {
        if (markerLayer instanceof L.Marker) {
          if (markerLayer.feature.id === object.id) {
            markerLayer.openPopup();
          }
        }
      });
    });
  },

  noResults: ({ currentValue, template }) =>
    template(`<li>No results found: "${currentValue}"</li>`),
});

const legend = L.control({
  position: "bottomright",
});

const color = ["be4dff", "ff8146", "ff3939"];
const label = ["bar", "pharmacy", "restaurant"];
const rows = [];

legend.onAdd = () => {
  const div = L.DomUtil.create("div", "legend");

  L.DomEvent.disableClickPropagation(div);

  color.map((item, index) => {
    rows.push(`
      <div class="row" style="margin: 1px auto;">
        <i style="background: #${item}"></i>${label[index]}
      </div>
    `);
  });

  div.innerHTML = rows.join("");
  return div;
};

legend.addTo(map);
