<script>
  import { onDestroy, onMount } from "svelte";
  import { tick } from "svelte";
  import { browser } from "$app/env";
  //import JSONFormatter from "json-formatter-js";

  // Backward compatible: existing routes pass a single `apiUrl`.
  // New behavior: pass `datasets=[{ id?, name, url }]` to show multiple datasets.
  export let apiUrl = undefined;
  export let datasets = [];
  export let visible = true;
  export let containerClass = "h-noHeader-noFooter-noTitle";
  export let showPointsLayer = false;
  export let mapId = "map";
  export let onDatasetStatus = (status) => {};
  export let showPointGeometry = false;

  let last_select = null;
  let map;
  let leaflet;
  let JSONFormatter;
  let layerControl;
  let info;

  // datasetId -> { pointsGroup?, labelsGroup, bounds, overlaysAdded }
  const datasetLayers = new Map();
  // url -> geojson response cache (in-memory)
  const geojsonCache = new Map();
  let syncQueue = Promise.resolve();

  function normalizeDatasets(datasets, apiUrl) {
    if (Array.isArray(datasets) && datasets.length > 0) {
      return datasets
        .filter((d) => d && d.url)
        .map((d) => ({
          id: d.id ?? d.url,
          name: d.name ?? d.id ?? d.url,
          url: d.url,
        }));
    }
    if (apiUrl) {
      return [{ id: apiUrl, name: "Dataset", url: apiUrl }];
    }
    return [];
  }

  async function fetchGeoJson(url) {
    if (geojsonCache.has(url)) return geojsonCache.get(url);
    const res = await fetch(url);
    if (!res.ok) {
      throw new Error(`Failed to load ${url} (${res.status})`);
    }
    const data = await res.json();
    geojsonCache.set(url, data);
    return data;
  }

  function emitStatus(patch) {
    try {
      onDatasetStatus(patch);
    } catch (e) {
      // ignore
    }
  }

  function getFeatureLabel(feature) {
    const props = feature?.properties ?? {};
    const candidates = [
      "設施名稱",
      "NAME_TC",
      "NAME_EN",
      "nameTC",
      "nameEN",
      "NAME",
      "Name",
      "name",
    ];
    for (const key of candidates) {
      const v = props[key];
      if (typeof v === "string" && v.trim()) return v.trim();
    }
    // fallback: first string property
    for (const [k, v] of Object.entries(props)) {
      if (typeof v === "string" && v.trim()) return v.trim();
    }
    return "";
  }

  function ensureInfoControl() {
    if (info) return;
    info = leaflet.control({ position: "topleft" });
    info.onAdd = function () {
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
  }

  function resetInfoAndSelection() {
    if (info?._div) info._div.innerHTML = "<h4>Click point to view info</h4>";
    if (last_select) {
      leaflet.DomUtil.removeClass(last_select._icon, "text-red-600");
      leaflet.DomUtil.removeClass(last_select._icon, "font-bold");
      last_select = null;
    }
  }

  function addDatasetOverlaysToControl(ds, layers) {
    if (!layerControl || layers.overlaysAdded) return;
    layerControl.addOverlay(layers.labelsGroup, ds.name);
    if (showPointsLayer && layers.pointsGroup) {
      layerControl.addOverlay(layers.pointsGroup, `${ds.name} (Points)`);
    }
    layers.overlaysAdded = true;
  }

  function removeDatasetOverlaysFromControl(layers) {
    if (!layerControl || !layers?.overlaysAdded) return;
    layerControl.removeLayer(layers.labelsGroup);
    if (layers.pointsGroup) layerControl.removeLayer(layers.pointsGroup);
    layers.overlaysAdded = false;
  }

  async function addDataset(ds) {
    if (datasetLayers.has(ds.id)) return;

    const labelsGroup = leaflet.layerGroup();
    const pointsGroup = showPointsLayer ? leaflet.layerGroup() : null;
    const state = {
      pointsGroup,
      labelsGroup,
      overlaysAdded: false,
      bounds: null,
    };
    datasetLayers.set(ds.id, state);

    let responseData;
    try {
      emitStatus({ id: ds.id, url: ds.url, state: "loading" });
      responseData = await fetchGeoJson(ds.url);
    } catch (e) {
      console.warn(e);
      emitStatus({
        id: ds.id,
        url: ds.url,
        state: "error",
        message: e?.message ?? String(e),
      });
      return;
    }

    // Draw the geometry (works for any geometry type)
    const geometryLayer = leaflet.geoJSON(responseData, {
      filter: (feature) => {
        // By default: don't draw point geometry (labels-only looks cleaner)
        if (!showPointGeometry && feature?.geometry?.type === "Point") return false;
        return true;
      },
      pointToLayer: (feature, latlng) => {
        // If point geometry is enabled, use circle markers (avoid default blue pins)
        return leaflet.circleMarker(latlng, {
          radius: 6,
          fillColor: "#ff7800",
          color: "#000",
          weight: 1,
          opacity: 1,
          fillOpacity: 0.8,
        });
      },
      style: () => ({
        color: "#2563eb",
        weight: 2,
        opacity: 0.9,
        fillColor: "#60a5fa",
        fillOpacity: 0.15,
      }),
      onEachFeature: (feature, layer) => {
        const label = getFeatureLabel(feature);
        if (label) layer.bindPopup(label);
      },
    });

    // Create label markers directly from GeoJSON points (even if point geometry is hidden),
    // and centroid markers for lines/polygons.
    const labelMarkers = leaflet.layerGroup();

    function addLabelMarker(latlng, feature) {
      const label = getFeatureLabel(feature);
      if (!label) return;

      const marker = leaflet.marker(latlng, {
        icon: leaflet.divIcon({
          iconSize: null,
          html:
            '<div class="map-label"><div class="map-label-content">' +
            label +
            '</div><div class="map-label-arrow"></div></div>',
        }),
      });

      marker.on("click", (e) => {
        if (last_select) {
          leaflet.DomUtil.removeClass(last_select._icon, "text-red-600");
          leaflet.DomUtil.removeClass(last_select._icon, "font-bold");
        }
        if (e?.target?._icon) {
          leaflet.DomUtil.addClass(e.target._icon, "font-bold text-red-600");
          last_select = e.target;
        }

        ensureInfoControl();
        info._div.innerHTML = "";
        const formatter = new JSONFormatter(feature, 2);
        info._div.appendChild(formatter.render());
      });

      labelMarkers.addLayer(marker);
    }

    if (responseData?.type === "FeatureCollection" && Array.isArray(responseData.features)) {
      for (const feature of responseData.features) {
        const t = feature?.geometry?.type;
        const coords = feature?.geometry?.coordinates;
        if (!t || !coords) continue;

        if (t === "Point" && Array.isArray(coords) && coords.length >= 2) {
          const [lng, lat] = coords;
          addLabelMarker(leaflet.latLng(lat, lng), feature);
        } else if (t === "MultiPoint" && Array.isArray(coords) && coords.length) {
          for (const pt of coords) {
            if (Array.isArray(pt) && pt.length >= 2) {
              const [lng, lat] = pt;
              addLabelMarker(leaflet.latLng(lat, lng), feature);
            }
          }
        }
      }
    }

    // For non-point geometries, add centroid labels from the rendered geometry.
    geometryLayer.eachLayer((layer) => {
      const feature = layer.feature;
      const t = feature?.geometry?.type;
      if (t === "Point" || t === "MultiPoint") return;

      let latlng = null;
      if (layer.getBounds) {
        const b = layer.getBounds();
        if (b?.isValid && b.isValid()) latlng = b.getCenter();
      }
      if (!latlng) return;
      addLabelMarker(latlng, feature);
    });

    state.bounds =
      geometryLayer?.getBounds && geometryLayer.getBounds().isValid()
        ? geometryLayer.getBounds()
        : null;

    // Put both geometry + labels into the single dataset overlay
    labelsGroup.addLayer(geometryLayer);
    labelsGroup.addLayer(labelMarkers);

    // Default show labels only; points are optional (off by default).
    labelsGroup.addTo(map);
    if (showPointsLayer && pointsGroup) pointsGroup.addTo(map);

    addDatasetOverlaysToControl(ds, state);
    emitStatus({
      id: ds.id,
      url: ds.url,
      state: "loaded",
      featureCount:
        responseData?.type === "FeatureCollection"
          ? responseData?.features?.length ?? 0
          : undefined,
    });
  }

  function removeDataset(datasetId) {
    const state = datasetLayers.get(datasetId);
    if (!state) return;

    removeDatasetOverlaysFromControl(state);
    if (state.pointsGroup) map.removeLayer(state.pointsGroup);
    map.removeLayer(state.labelsGroup);
    datasetLayers.delete(datasetId);
  }

  function fitToAllBounds() {
    const bounds = [];
    datasetLayers.forEach((s) => {
      if (s.bounds) bounds.push(s.bounds);
    });
    if (bounds.length === 0) return;
    const merged = bounds[0].clone();
    for (let i = 1; i < bounds.length; i++) merged.extend(bounds[i]);
    map.fitBounds(merged);
  }

  async function syncLayers() {
    const desired = normalizeDatasets(datasets, apiUrl);
    const desiredIds = new Set(desired.map((d) => d.id));

    // Remove datasets no longer selected
    for (const existingId of Array.from(datasetLayers.keys())) {
      if (!desiredIds.has(existingId)) removeDataset(existingId);
    }

    // Add newly selected datasets
    for (const ds of desired) {
      if (!datasetLayers.has(ds.id)) await addDataset(ds);
    }

    fitToAllBounds();
  }

  function queueSync() {
    // serialize to avoid race conditions when selection changes quickly
    syncQueue = syncQueue
      .then(() => syncLayers())
      .catch(() => {});
  }

  // Emit immediate status on selection changes so we can debug stuck states.
  $: if (browser) {
    const desiredNow = normalizeDatasets(datasets, apiUrl);
    for (const ds of desiredNow) {
      const has = datasetLayers.has(ds.id);
      if (has) continue;
      emitStatus({
        id: ds.id,
        url: ds.url,
        state: map && leaflet ? "queued" : "waiting_map",
      });
    }
  }

  onMount(async () => {
    if (browser) {
      JSONFormatter = (await import("json-formatter-js")).default;
      leaflet = await import("leaflet");

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

      map = leaflet.map(mapId, {
        center: [22.31, 114.16],
        zoom: 11,
        layers: [OSM],
      });

      const baselayers = {
        "Street Map": OSM,
        "Grays Scale": grayscale,
        Hybrid: hybirdmap,
      };

      layerControl = leaflet.control
        .layers(baselayers, {}, { collapsed: false })
        .addTo(map);

      map.on("click", resetInfoAndSelection);

      // Initial render based on props
      queueSync();
    }
  });

  onDestroy(() => {
    try {
      if (map) map.remove();
    } catch (e) {
      // ignore
    } finally {
      map = undefined;
      datasetLayers.clear();
      geojsonCache.clear();
    }
  });

  // Keep map layers in sync when parent changes selection.
  $: if (browser && map && leaflet) {
    // make this reactive to prop changes
    datasets;
    apiUrl;
    queueSync();
  }

  // If the map is shown after being hidden (overlay open), Leaflet needs a resize refresh.
  $: if (browser && visible && map) {
    (async () => {
      await tick();
      try {
        map.invalidateSize();
        fitToAllBounds();
      } catch (e) {
        // ignore
      }
    })();
  }

  // When dataset selection changes, make sure Leaflet refreshes sizing.
  $: if (browser && map) {
    datasets; // reactive dependency
    (async () => {
      await tick();
      try {
        map.invalidateSize();
      } catch (e) {
        // ignore
      }
    })();
  }
</script>

<main class="h-full w-full">
  <div class={`w-full ${containerClass}`} id={mapId} />
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
