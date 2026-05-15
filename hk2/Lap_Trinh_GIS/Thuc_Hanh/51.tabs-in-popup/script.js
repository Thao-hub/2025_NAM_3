/* eslint-disable no-undef */
/**
 * tabs in popup
 */

// config map
const config = {
	minZoom: 1,
	maxZoom: 18,
};

// magnification with which the map will start
const zoom = 15;

// co-ordinates
const lat = 50.0625;
const lng = 19.9379;

// calling map
const map = L.map("map", config).setView([lat, lng], zoom);

// Used to load and display tile layers on the map
// Most tile servers require attribution, which you can set under `Layer`
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
	attribution:
		'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);

// custom popup image + text
const customPopup = `<div class="customPopup">
	<ul class="tabs-example" data-tabs>
		<li><a data-tabby-default href="#sukiennice">Sukiennice</a></li>
		<li><a href="#town-hall-tower">Town Hall Tower</a></li>
	</ul>

	<div id="sukiennice">
		<figure>
			<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/A-10_Sukiennice_w_Krakowie_Krak%C3%B3w%2C_Rynek_G%C5%82%C3%B3wny_MM.jpg/320px-A-10_Sukiennice_w_Krakowie_Krak%C3%B3w%2C_Rynek_G%C5%82%C3%B3wny_MM.jpg" alt="Sukiennice in Krakow" />
			<figcaption>Source: wikipedia.org</figcaption>
		</figure>
		<div>
			Sukiennice in Krakow, Poland, are one of the most recognizable icons of the Main Market Square.
		</div>
	</div>

	<div id="town-hall-tower">
		<figure>
			<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Krak%C3%B3w_-_Town_Hall_Tower_01a.jpg/315px-Krak%C3%B3w_-_Town_Hall_Tower_01a.jpg" alt="Town Hall Tower in Krakow" />
			<figcaption>Source: wikipedia.org</figcaption>
		</figure>
		<div>
			Town Hall Tower in Krakow, Poland (Polish: Wieza ratuszowa w Krakowie) is one of the main focal points of the Main Market Square.
		</div>
	</div>
</div>`;

// specify popup options
const customOptions = {
	minWidth: "220", // set max-width
	keepInView: true, // Set it to true if you want to prevent users from panning the popup off of the screen while it is open.
};

// create marker object, pass custom icon as option, pass content and options to popup, add to map
const marker = L.marker([50.0616, 19.9373])
	.bindPopup(customPopup, customOptions)
	.on("click", runTabs);

marker.addTo(map);

// center map when click on marker
function runTabs() {
	new Tabby("[data-tabs]");
}
