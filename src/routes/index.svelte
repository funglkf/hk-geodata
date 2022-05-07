<script>
  import TableAuto from "$lib/TabulatorAutoUse.svelte";

  const tableDataUrl = "/json/simplified_datasetinfo.json";

  const tablePluginSettings = {
    title: "Dataset Overview",
    copyData: true,
    saveExcel: true,
    saveCSV: false,
  };

  const customTableConfig = {
    layout: "fitColumns", //fit columns to width of table
    paginationSize: 1000,
    tooltips: true, //show tool tips on cells
    paginationCounter: "rows", //display count of paginated rows in footer
    rowClickMenu: [
      {
        label: "Open Data in Map",
        action: function (e, row) {
          window
            .open(
              `https://geojson.tools/?url=https://geodata.gov.hk/gs/api/v1.0.0/geoDataQuery?q=%7Bv%3A%221%2E0%2E0%22%2Cid%3A%22` +
                row.getData()["DATASET_UUID"] +
                `%22%2Clang%3A%22ALL%22%7D`,
              "_blank"
            )
            .focus();
        },
      },
    ],
  };
</script>

<main>
  <TableAuto {tableDataUrl} {...tablePluginSettings} {customTableConfig} />
</main>
