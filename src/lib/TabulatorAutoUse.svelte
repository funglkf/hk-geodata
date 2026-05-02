<script>
  import { TabulatorFull as Tabulator } from "tabulator-tables";
  import "tabulator-tables/dist/css/tabulator_simple.min.css";
  import "$lib/xlsx.full.min.js";
  import AutoComplete from "$lib/SimpleAutocomplete.svelte";

  export let title = "Table View";

  export let tableDataUrl;
  export let tableList = [];
  export let copyData = true;
  export let saveExcel = true;
  export let saveCSV = true;
  export let customTableConfig = {};
  export let rowClickfFunction = () => {};
  export let dataLoadedFunction = () => {};
  export let autoColumnFunction = (column) => {
    column.headerFilter = true; // add header filter to every column
    column.headerFilterPlaceholder = "Filter";
  };

  let showItemSidebar = true;
  let searchTerm = "";
  let filterOrg = "";
  let selectName;
  let table;
  let selectedUrl = "";

  function makeTable(node, { ajaxurl }) {
    table = new Tabulator(node, {
      ...{
        ajaxURL: ajaxurl,
        ajaxResponse: (url, params, response) => {
          // console.log(response);
          return response;
        },
        autoColumns: true,
        autoColumnsDefinitions: function (definitions) {
          definitions.forEach(autoColumnFunction);
          return definitions;
        },
        // columns: columns,
        layout: "fitDataStretch",
        pagination: true,
        paginationSize: 100,
        clipboard: true,
      },
      ...customTableConfig,
    });

    table.on("rowClick", rowClickfFunction);
    table.on("dataLoaded", (data) => dataLoadedFunction(table, data));

    return {
      update: ({ ajaxurl }) => {
        if (typeof ajaxurl !== "undefined") {
          // console.log(ajaxurl);
          fetch(ajaxurl)
            .then((response) => response.json())
            .then((data) => {
              const tableData = (() => {
                if (data.type != "FeatureCollection") {
                  return data;
                } else {
                  return data.features.map((feature) => feature.properties);
                }
              })();
              table.setData(tableData, {});
            });
        }
      },
      // destroy: () => alert('bye bye table :\'(')
    };
  }

  function orgLabel(item) {
    const tc = (item?.nameTC ?? "").trim();
    const en = (item?.nameEN ?? "").trim();
    if (tc && en) return `${tc} / ${en}`;
    return tc || en || "";
  }

  $: orgOptions = Array.from(
    new Set(tableList.map((d) => orgLabel(d)).filter((v) => v))
  ).sort((a, b) => a.localeCompare(b));

  $: filteredItemList = tableList
    .filter((item) => {
      const needle = searchTerm.trim().toLowerCase();
      if (!needle) return true;
      const n = (item?.name ?? "").toLowerCase();
      const tc = (item?.nameTC ?? "").toLowerCase();
      const en = (item?.nameEN ?? "").toLowerCase();
      return n.includes(needle) || tc.includes(needle) || en.includes(needle);
    })
    .filter((item) => {
      if (filterOrg && orgLabel(item) !== filterOrg) return false;
      return true;
    });
</script>

<div class="flex">
  {#if showItemSidebar}
    <div
      class="overflow-y-auto w-[240px] h-noHeader-noFooter text-gray-800 border-r bg-white"
    >
      <div class="flex items-center">
        <svg
          style="width:20px;height:20px"
          viewBox="0 0 20 20"
          class="cursor-pointer"
          on:click={() => (showItemSidebar = !showItemSidebar)}
        >
          <path
            fill="currentColor"
            d="M1,4 H18 V6 H1 V4 M1,9 H18 V11 H1 V7 M3,14 H18 V16 H1 V14"
          />
        </svg>
        <h1 class="px-1 font-semibold text-base">List items</h1>
      </div>
      <input
        class="mx-2 my-2 w-[calc(100%-1rem)] text-xs border border-solid rounded px-2 py-1"
        placeholder="Search"
        bind:value={searchTerm}
      />
      <div class="mx-2 mb-2">
        <div class="text-[10px] text-gray-500 mb-1">Department (TC / EN)</div>
        <select class="w-full border rounded px-2 py-1 text-xs" bind:value={filterOrg}>
          <option value="">All</option>
          {#each orgOptions as opt}
            <option value={opt}>{opt}</option>
          {/each}
        </select>
      </div>
      <ul class="divide-y">
        {#each filteredItemList as { name, url }}
          <li>
            <button
              type="button"
              class={`w-full text-left px-2 py-2 text-xs font-normal
                ${selectedUrl === url ? "bg-blue-50" : "bg-white"}
                hover:bg-gray-50`}
              on:click={() => {
                selectedUrl = url;
                tableDataUrl = url;
              }}
            >
              <div class="whitespace-normal break-words leading-snug">{name}</div>
            </button>
          </li>
        {/each}
      </ul>
    </div>
  {/if}
  <div class="mx-5 flex-auto w-10">
    <div>
      <h1 class="font-semibold text-xl">{title}</h1>
    </div>
    <div class="flex items-center my-1 space-x-1">
      {#if !(tableList.length < 2)}
        <svg
          style="width:20px;height:20px"
          viewBox="0 0 20 20"
          class="cursor-pointer"
          on:click={() => (showItemSidebar = !showItemSidebar)}
        >
          <path
            fill="currentColor"
            d="M1,4 H18 V6 H1 V4 M1,9 H18 V11 H1 V7 M3,14 H18 V16 H1 V14"
          />
        </svg>
        <div
          class="max-w-[150px] md:max-w-[300px] p-0 border border-solid rounded text-base"
        >
          <AutoComplete
            items={tableList}
            bind:selectedItem={selectName}
            bind:value={tableDataUrl}
            labelFieldName="name"
            valueFieldName="url"
            placeholder="Select"
            onChange={(item) => {
              // keep sidebar highlight consistent even if user selects from autocomplete
              selectedUrl = item?.url ?? tableDataUrl;
            }}
          />
        </div>
        <!-- 				
				<select
					class="border border-solid border-gray-300 rounded text-base"
					bind:value={tableDataUrl}
					on:change={makeTable}
				>
					<option selected disabled>Select Table</option>
					{#each tableList as { name, url }}
						<option value={url}>{name}</option>
					{/each}
				</select> -->
      {/if}

      {#if copyData}
        <button
          class="bg-blue-500 hover:bg-blue-700 text-white px-1 rounded"
          on:click={() => table.copyToClipboard("all")}
          >Copy data
        </button>
      {/if}

      {#if saveCSV}
        <button
          class="bg-green-500 hover:bg-green-700 text-white px-1 rounded"
          on:click={() => table.download("csv", "data.csv", { delimiter: "," })}
          >Download CSV
        </button>
      {/if}

      {#if saveExcel}
        <button
          class="bg-green-500 hover:bg-green-700 text-white px-1 rounded"
          on:click={() =>
            table.download("xlsx", "data.xlsx", { sheetName: "MyData" })}
          >Download Excel
        </button>
      {/if}
    </div>

    <div
      class="h-noHeader-noFooter-noButton"
      use:makeTable={{ ajaxurl: tableDataUrl }}
    />
  </div>
</div>
