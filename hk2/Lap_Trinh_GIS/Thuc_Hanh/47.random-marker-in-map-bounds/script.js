/* eslint-disable no-undef */
/**
 * Random marker in map bounds
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

// add legend
const legend = L.control({ position: "bottomleft" });

legend.onAdd = () => {
	const div = L.DomUtil.create("div", "description");
	L.DomEvent.disableClickPropagation(div);
	const text = "Dynamic generation of 30 markers in the map view";
	div.insertAdjacentHTML("beforeend", text);
	return div;
};

legend.addTo(map);

// add "random" button
const buttonTemplate =
	'<svg version="1.1" xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32"><path d="M24 22h-3.172l-5-5 5-5h3.172v5l7-7-7-7v5h-4c-0.53 0-1.039 0.211-1.414 0.586l-5.586 5.586-5.586-5.586c-0.375-0.375-0.884-0.586-1.414-0.586h-6v4h5.172l5 5-5 5h-5.172v4h6c0.53 0 1.039-0.211 1.414-0.586l5.586-5.586 5.586 5.586c0.375 0.375 0.884 0.586 1.414 0.586h4v5l7-7-7-7v5z" /></svg>';

// create custom button
const customControl = L.Control.extend({
	// button position
	options: {
		position: "topleft",
		title: "random marker",
		className: "leaflet-random-marker",
	},

	// method
	onAdd: function (leafletMap) {
		this._map = leafletMap;
		return this._initialLayout();
	},

	_initialLayout: function () {
		// create button
		const container = L.DomUtil.create(
			"div",
			`leaflet-bar ${this.options.className}`
		);
		this._container = container;

		L.DomEvent.disableClickPropagation(container);

		container.title = this.options.title;
		container.innerHTML = buttonTemplate;

		// action when click on button
		// clear and add random marker
		L.DomEvent.on(container, "mousedown dblclick", L.DomEvent.stopPropagation)
			.on(container, "click", L.DomEvent.stop)
			.on(container, "click", removeMarkers)
			.on(container, "click", randomMarker);

		return this._container;
	},
});

// adding new button to map control
map.addControl(new customControl());

// random color
function randomColor() {
	return `#${Math.floor(Math.random() * 16777215)
		.toString(16)
		.padStart(6, "0")}`;
}

// create legend

// add feature group to map
const fg = L.featureGroup().addTo(map);

// create random marker
function randomMarker() {
	// get bounds of map
	const bounds = map.getBounds();

	const southWest = bounds.getSouthWest();
	const northEast = bounds.getNorthEast();
	const lngSpan = northEast.lng - southWest.lng;
	const latSpan = northEast.lat - southWest.lat;

	const allPoints = [];

	// generate random points and add to array `allPoints`
	for (let i = 0; i < 30; i++) {
		const points = [
			southWest.lat + latSpan * Math.random(),
			southWest.lng + lngSpan * Math.random(),
		];

		allPoints.push(points);
	}

	// add markers to feature group
	for (let i = 0; i < allPoints.length; i++) {
		L.marker(allPoints[i], {
			icon: L.divIcon({
				className: "custom-icon-marker",
				iconSize: L.point(40, 40),
				iconAnchor: [12, 24],
				popupAnchor: [9, -26],
				html: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" class="marker"><path fill-opacity="0.25" d="M16 31c0 0 10-12.353 10-18A10 10 0 106 13c0 5.647 10 18 10 18z"></path><path fill="${randomColor()}" stroke="#fff" stroke-width="1.5" d="M16 30S7 18.95 7 13a9 9 0 1118 0c0 5.95-9 17-9 17z"></path><circle cx="16" cy="13" r="4.25" fill="#fff"></circle></svg>`,
			}),
		})
			.bindPopup(`<b>Marker coordinates</b>:<br>${allPoints[i].toString()}`)
			.addTo(fg);
	}

	// zoom to feature group and add padding
	map.fitBounds(fg.getBounds(), { padding: [20, 20] });
}

// remove markers from feature group
function removeMarkers() {
	fg.clearLayers();
}

// initialize random marker
randomMarker();
