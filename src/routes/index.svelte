<script>
  import { onMount } from "svelte";
  import LeafletMap from "$lib/LeafletMap.svelte";

  const datasetInfoUrl = "/json/simplified_datasetinfo.json";

  let allDatasets = [];
  let selectedDatasets = [];

  let sidebarOpen = true;
  let searchTerm = "";
  let filterNameTC = "";
  let filterNameEN = "";

  function datasetIdFromEnName(en) {
    return (en ?? "").replace(/[^\w_-]+/g, "_");
  }

  function datasetUrlFromEnName(en) {
    return "/json/" + datasetIdFromEnName(en) + ".geojson";
  }

  function displayName(ds) {
    const tc = ds.DATASET_NAME_TC ?? ds.nameTC ?? "";
    const en = ds.DATASET_NAME_EN ?? ds.nameEN ?? "";
    if (tc && en) return `${tc} / ${en}`;
    return tc || en || ds.id;
  }

  function isSelected(id) {
    return selectedDatasets.some((d) => d.id === id);
  }

  function toggleDataset(ds) {
    const id = ds.id;
    const idx = selectedDatasets.findIndex((d) => d.id === id);
    if (idx >= 0) {
      selectedDatasets = [
        ...selectedDatasets.slice(0, idx),
        ...selectedDatasets.slice(idx + 1),
      ];
      return;
    }
    selectedDatasets = [
      ...selectedDatasets,
      { id, name: displayName(ds), url: ds.url },
    ];
  }

  $: filteredDatasets = allDatasets.filter((d) => {
    const needle = searchTerm.trim().toLowerCase();
    if (!needle) return true;
    const tc = (d.DATASET_NAME_TC ?? d.nameTC ?? "").toLowerCase();
    const en = (d.DATASET_NAME_EN ?? d.nameEN ?? "").toLowerCase();
    return tc.includes(needle) || en.includes(needle);
  });

  $: nameTCOptions = Array.from(
    new Set(allDatasets.map((d) => d.nameTC).filter((v) => typeof v === "string" && v.trim()))
  ).sort((a, b) => a.localeCompare(b));

  $: nameENOptions = Array.from(
    new Set(allDatasets.map((d) => d.nameEN).filter((v) => typeof v === "string" && v.trim()))
  ).sort((a, b) => a.localeCompare(b));

  $: filteredDatasets = filteredDatasets.filter((d) => {
    if (filterNameTC && d.nameTC !== filterNameTC) return false;
    if (filterNameEN && d.nameEN !== filterNameEN) return false;
    return true;
  });

  $: selectedDatasets = selectedDatasets.map((d) => {
    // keep selected names in sync with latest metadata
    const original = allDatasets.find((x) => x.id === d.id);
    if (!original) return d;
    return { ...d, name: displayName(original) };
  });

  onMount(async () => {
    const data = await fetch(datasetInfoUrl).then((r) => r.json());
    allDatasets = (data ?? []).map((obj) => {
      const id = datasetIdFromEnName(obj["DATASET_NAME_EN"]);
      return {
        ...obj,
        id,
        url: datasetUrlFromEnName(obj["DATASET_NAME_EN"]),
      };
    });
  });
</script>

<main>
  {#if !sidebarOpen}
    <!-- Mobile toggle button (only when sidebar is closed) -->
    <button
      class="md:hidden fixed bottom-4 left-4 z-40 bg-white/95 hover:bg-white border rounded px-3 py-2 shadow"
      on:click={() => (sidebarOpen = true)}
    >
      Show Datasets ({selectedDatasets.length})
    </button>
  {/if}

  <div class="flex h-noHeader-noFooter">
    <!-- Sidebar -->
    <aside
      class={`z-30 w-[320px] bg-white border-r h-full flex flex-col
        md:translate-x-0 md:static
        ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}
        fixed left-0 top-[60px] md:top-auto`}
      style="transition: transform 150ms ease"
    >
      <div class="p-3 border-b">
        <div class="flex items-center justify-between gap-2">
          <div class="font-semibold">Datasets</div>
          <div class="text-sm text-gray-600">{selectedDatasets.length} selected</div>
        </div>

        <div class="mt-2 flex items-center gap-2">
          <input
            class="flex-1 border rounded px-2 py-1 text-sm"
            placeholder="Search (TC / EN)"
            bind:value={searchTerm}
          />

          <div class="text-xs text-gray-500">{filteredDatasets.length}</div>
        </div>

        <div class="mt-2 grid grid-cols-2 gap-2">
          <div>
            <div class="text-xs text-gray-500 mb-1">NameTC</div>
            <select class="w-full border rounded px-2 py-1 text-sm" bind:value={filterNameTC}>
              <option value="">All</option>
              {#each nameTCOptions as opt}
                <option value={opt}>{opt}</option>
              {/each}
            </select>
          </div>
          <div>
            <div class="text-xs text-gray-500 mb-1">NameEN</div>
            <select class="w-full border rounded px-2 py-1 text-sm" bind:value={filterNameEN}>
              <option value="">All</option>
              {#each nameENOptions as opt}
                <option value={opt}>{opt}</option>
              {/each}
            </select>
          </div>
        </div>

        <div class="mt-2 flex items-center justify-between">
          <button
            class="md:hidden text-sm bg-gray-100 hover:bg-gray-200 border rounded px-2 py-1"
            on:click={() => (sidebarOpen = false)}
            type="button"
          >
            Hide
          </button>
          <div class="text-xs text-gray-500">
            Click dataset to add/remove
          </div>
        </div>

        {#if selectedDatasets.length > 0}
          <div class="mt-2 flex flex-wrap gap-1">
            {#each selectedDatasets as ds (ds.id)}
              <button
                class="text-xs bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded px-2 py-1"
                title="Remove"
                on:click={() => (selectedDatasets = selectedDatasets.filter((d) => d.id !== ds.id))}
              >
                {ds.name}
              </button>
            {/each}
            <button
              class="text-xs bg-gray-100 hover:bg-gray-200 border rounded px-2 py-1"
              on:click={() => (selectedDatasets = [])}
            >
              Clear
            </button>
          </div>

        {/if}
      </div>

      <div class="flex-1 overflow-y-auto">
        {#each filteredDatasets as ds (ds.id)}
          <button
            class={`w-full text-left px-3 py-2 border-b hover:bg-gray-50 ${
              isSelected(ds.id) ? "bg-blue-50" : ""
            }`}
            on:click={() => toggleDataset(ds)}
          >
            <div class="text-sm font-medium">{displayName(ds)}</div>
            <div class="text-xs text-gray-500">{ds.id}</div>
          </button>
        {/each}
      </div>
    </aside>

    <!-- Map main -->
    <div class="flex-1 min-w-0 h-full">
      <LeafletMap
        datasets={selectedDatasets}
        visible={true}
        showPointsLayer={false}
        showPointGeometry={false}
        mapId="main-map"
        containerClass="h-full"
      />
    </div>
  </div>
</main>
