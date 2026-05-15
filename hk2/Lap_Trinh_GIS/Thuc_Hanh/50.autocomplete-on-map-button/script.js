/* eslint-disable no-undef */
/**
 * autocomplete on map
 * https://github.com/tomickigrzegorz/autocomplete
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

// create search button
const buttonTemplate = `
	<div class="leaflet-search">
		<svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
			<path d="M31.008 27.231l-7.58-6.447c-0.784-0.705-1.622-1.029-2.299-0.998 1.789-2.096 2.87-4.815 2.87-7.787 0-6.627-5.373-12-12-12s-12 5.373-12 12c0 6.591 5.348 11.938 11.927 11.998 2.299 6.447 7.58c1.104 1.226 2.987 1.33 4.007 0.235 0.997-2.903-0.234-0.077M12 20c-4.418 0-8-3.582-8-8s3.582-8 8-8 8 3.582 8 8-3.582 8-8 8z"></path>
		</svg>
	</div>
	<div class="auto-search-wrapper max-height">
		<input
			type="text"
			id="marker"
			autocomplete="off"
			aria-describedby="instruction"
			aria-label="Search ..."
		/>
		<div id="instruction" class="hidden">
			When autocomplete results are available use up and down arrows to review and enter to select.
		</div>
	</div>
`;

// create custom button
const customControl = L.Control.extend({
	// button position
	options: {
		position: "topleft",
		className: "leaflet-autocomplete",
	},

	// method
	onAdd: function () {
		return this._initialLayout();
	},

	_initialLayout: function () {
		// create button
		const container = L.DomUtil.create(
			"div",
			`leaflet-bar ${this.options.className}`
		);

		L.DomEvent.disableClickPropagation(container);
		container.innerHTML = buttonTemplate;

		return container;
	},
});

// adding new button to map controll
map.addControl(new customControl());

// input element
const root = document.getElementById("marker");

function clickOnClearButton() {
	const clearButton = document.querySelector(".auto-clear");

	if (!clearButton) {
		return;
	}

	clearButton.click();
}

function addClassToParent() {
	const searchBtn = document.querySelector(".leaflet-search");

	searchBtn.addEventListener("click", (e) => {
		// toggle class
		e.target
			.closest(".leaflet-autocomplete")
			.classList.toggle("active-autocomplete");

		// add placeholder
		root.placeholder = "Search ...";

		// focus on input
		root.focus();

		// use destroy method
		autocomplete.destroy();
	});
}

addClassToParent();

// function clear input
map.on("click", () => {
	document
		.querySelector(".leaflet-autocomplete")
		.classList.remove("active-autocomplete");

	clickOnClearButton();
});

// autocomplete section
// more config find in https://github.com/tomickigrzegorz/autocomplete
let locatedMarker = null;

const autocomplete = new Autocomplete("marker", {
	delay: 1000,
	selectFirst: true,
	howManyCharacters: 2,

	onSearch: ({ currentValue }) => {
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
	},

	onResults: ({ currentValue, matches, template }) => {
		const regex = new RegExp(currentValue, "i");

		return matches === 0
			? template
			: matches
					.map((element) => {
						return `
						<li role="option">
							<p>${element.properties.display_name.replace(
								regex,
								(str) => `<b>${str}</b>`
							)}</p>
						</li>`;
					})
					.join("");
	},

	onSubmit: ({ object }) => {
		const { display_name } = object.properties;
		const cord = object.geometry.coordinates;

		// remove last marker
		if (locatedMarker) {
			map.removeLayer(locatedMarker);
		}

		// add marker
		const marker = L.marker([cord[1], cord[0]], {
			title: display_name,
		});

		// add marker to map
		marker.addTo(map).bindPopup(display_name);
		locatedMarker = marker;

		// set marker to coordinates
		map.setView([cord[1], cord[0]], 8);

		// add class to marker
		L.DomUtil.addClass(marker._icon, "leaflet-marker-locate");
	},

	// the method presents no results
	noResults: ({ currentValue, template }) =>
		template(`<li>No results found: "${currentValue}"</li>`),
});
