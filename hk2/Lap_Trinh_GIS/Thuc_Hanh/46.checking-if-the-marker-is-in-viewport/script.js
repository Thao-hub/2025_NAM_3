/* eslint-disable no-undef */
/**
 * Checking if the marker is in viewport
 */

// config map
const config = {
	minZoom: 7,
	maxZoom: 18,
};

// magnification with which the map will start
const zoom = 18;

// co-ordinates
const lat = 52.22977;
const lng = 21.01178;

// calling map
const map = L.map("map", config).setView([lat, lng], zoom);

// Used to load and display tile layers on the map
// Most tile servers require attribution, which you can set under `Layer`
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
	attribution:
		'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);

// create legend
const legend = L.control({ position: "bottomleft" });

legend.onAdd = () => {
	const div = L.DomUtil.create("div", "description");
	L.DomEvent.disableClickPropagation(div);
	const text =
		'We check if the marker is in the page view. Move the map or drag the marker so that it is outside the map.<br>Marker in view: <b class="checkMarker">true</b>';
	div.insertAdjacentHTML("beforeend", text);
	return div;
};

legend.addTo(map);

// add marker to map
const marker = L.marker([52.22983, 21.011728], {
	draggable: true,
})
	.addTo(map)
	.bindPopup("Center Warsaw");

// check if marker is in viewport
function markerInMapView() {
	const mapBounds = map.getBounds();
	const contains = mapBounds.contains(marker.getLatLng());

	const markerInfo = document.querySelector(".checkMarker");
	markerInfo.textContent = contains;
	markerInfo.classList[contains ? "remove" : "add"]("color-red");
}

markerInMapView();

// check if marker is in viewport on moveend map
map.on("moveend", () => {
	markerInMapView();
});

marker.on("dragend", () => {
	markerInMapView();
});
