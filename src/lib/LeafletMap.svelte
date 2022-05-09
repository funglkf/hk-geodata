<script>
  import { onMount } from "svelte";
  import { browser } from "$app/env";
  //import JSONFormatter from "json-formatter-js";

  export let apiUrl;
  let last_select = null;

  onMount(async () => {
    if (browser) {
      const JSONFormatter = (await import("json-formatter-js")).default;
      const leaflet = await import("leaflet");

      const OSM = leaflet.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        {
          attribution:
            '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        }
      );

      const grayscale = leaflet.tileLayer(
        "https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png",
        {
          attribution: "© Cartodb contributors",
        }
      );

      const hybirdmap = leaflet.tileLayer(
        "https://mapapi.geodata.gov.hk/gs/api/v1.0.0/xyz/imagery/WGS84/{z}/{x}/{y}.png",
        {
          attribution: "© The Government of Hong Kong SAR",
        }
      );

      let map = leaflet.map("map", {
        center: [22.31, 114.16],
        zoom: 11,
        layers: [OSM],
      });

      // const map = leaflet.map('map').setView([51.505, -0.09], 13)
      // var coords = leaflet.latLng(51.505, -0.09);
      let markerLayer1 = leaflet.layerGroup();
      let markerLayer2 = leaflet.layerGroup();

      const baselayers = {
        "Street Map": OSM,
        "Grays Scale": grayscale,
        Hybrid: hybirdmap,
      };
      const overlaylayers = {
        Point: markerLayer1,
        "Point Label": markerLayer2,
      };

      leaflet.control
        .layers(baselayers, overlaylayers, { collapsed: false })
        .addTo(map);

      // create a div with a class "point_info"
      const info = leaflet.control({ position: "topleft" });
      info.onAdd = function (map) {
        this._div = leaflet.DomUtil.create("div", "point_info");
        this._div.innerHTML = "<h4>Click point to view info</h4>";
        leaflet.DomEvent.disableClickPropagation(this._div);
        leaflet.DomEvent.on(
          this._div,
          "mousewheel",
          leaflet.DomEvent.stopPropagation
        );
        return this._div;
      };
      map.addControl(info);

      fetch(apiUrl)
        .then((response) => response.json())
        .then((responseData) => {
          // console.log(responseData);

          var circleMarkerOptions = {
            radius: 6,
            fillColor: "#ff7800",
            color: "#000",
            weight: 1,
            opacity: 1,
            fillOpacity: 0.8,
          };

          const geojsonapi_layer = leaflet.geoJSON(responseData, {
            pointToLayer: (feature, latlng) => {
              return leaflet.circleMarker(latlng, circleMarkerOptions);
            },
            onEachFeature: (feature, layer) => {
              if (feature.properties && feature.properties["設施名稱"]) {
                layer.bindPopup(feature.properties["設施名稱"]);
              }
            },
          });

          map.fitBounds(geojsonapi_layer.getBounds());

          markerLayer1.addLayer(geojsonapi_layer);
        });

      fetch(apiUrl)
        .then((response) => response.json())
        .then((responseData) => {
          // console.log(responseData);
          const geojsonapi_layer_2 = leaflet.geoJSON(responseData, {
            pointToLayer: (feature, latlng) => {
              return leaflet.marker(latlng, {
                icon: leaflet.divIcon({
                  iconSize: null,
                  html:
                    '<div class="map-label"><div class="map-label-content">' +
                    feature.properties["設施名稱"] +
                    '</div><div class="map-label-arrow"></div></div>',
                }),
              });
            },
            onEachFeature: (feature, layer) => {
              layer.on({
                click: (e) => {
                  //// highlight selected
                  if (last_select) {
                    leaflet.DomUtil.removeClass(
                      last_select._icon,
                      "text-red-600"
                    );
                    leaflet.DomUtil.removeClass(last_select._icon, "font-bold");
                  }
                  leaflet.DomUtil.addClass(
                    e.target._icon,
                    "font-bold text-red-600"
                  );
                  last_select = e.target;

                  //// display properties info in side

                  // let propertiesAndInfo = [];
                  // for (let prop in feature.properties) {
                  // 	propertiesAndInfo.push(prop + ': ' + feature.properties[prop]);
                  // }
                  // info._div.innerHTML = propertiesAndInfo.join('<br />');

                  // Use JSONFormatter to parse Json to HTML
                  info._div.innerHTML = "";
                  const formatter = new JSONFormatter(feature, 2);
                  info._div.appendChild(formatter.render());
                },
              });
            },
          });

          markerLayer2.addLayer(geojsonapi_layer_2).addTo(map);
        });

      // restore info DIV and remove selected
      map.on("click", function (e) {
        info._div.innerHTML = "<h4>Click point to view info</h4>";
        if (last_select) {
          // console.log(last_select);
          leaflet.DomUtil.removeClass(last_select._icon, "text-red-600");
          leaflet.DomUtil.removeClass(last_select._icon, "font-bold");
        }
      });
    }
  });
</script>

<main>
  <div class="h-noHeader-noFooter-noTitle" id="map" />
</main>

<style>
  @import "leaflet/dist/leaflet.css";

  /* Svelte will purge unused class, user global for workaround*/
  /*Wraperclass for the divicon*/
  :global(.map-label) {
    position: absolute;
    bottom: 0;
    left: -50%;
    display: flex;
    flex-direction: column;
    text-align: center;
  }
  /*Wrap the content of the divicon (text) in this class*/
  :global(.map-label-content) {
    order: 1;
    position: relative;
    left: -50%;
    background-color: #fff;
    border-radius: 5px;
    border-width: 2px;
    border-style: solid;
    border-color: #444;
    padding: 3px;
    white-space: nowrap;
    opacity: 0.6;
  }
  /*Add this arrow*/
  :global(.map-label-arrow) {
    order: 2;
    width: 0px;
    height: 0px;
    left: 50%;
    border-style: solid;
    border-color: #444 transparent transparent transparent;
    border-width: 10px 6px 0 6px; /*[first number is height, second/fourth are rigth/left width]*/
    margin-left: -6px;
  }

  :global(.point_info) {
    width: 100%;
    max-width: 300px;
    height: 100%;
    max-height: calc(100vh - 200px);
    padding: 6px 8px;
    font: 14px/16px Arial, Helvetica, sans-serif;
    background: white;
    background: rgba(255, 255, 255, 0.8);
    box-shadow: 0 0 15px rgba(0, 0, 0, 0.2);
    border-radius: 5px;
    overflow-x: auto;
    overflow-y: auto;
  }
  :global(.point_info h4) {
    margin: 0 0 5px;
    color: #777;
  }
</style>
