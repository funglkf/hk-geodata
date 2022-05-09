<script>
  import TableAuto from "$lib/TabulatorAutoUse.svelte";

  const tableDataUrl = "/json/simplified_datasetinfo.json";

  const tablePluginSettings = {
    title: "Dataset Overview (Click to open on map)",
    copyData: true,
    saveExcel: true,
    saveCSV: false,
  };

  const customTableConfig = {
    layout: "fitColumns", //fit columns to width of table
    paginationSize: 1000,
    tooltips: true, //show tool tips on cells
    paginationCounter: "rows", //display count of paginated rows in footer
  };

  const rowClickfFunction = (e, row) => {
    window
      .open(
        "/map/" + row.getData()["DATASET_NAME_EN"].replace(/[^\w_-]/g, "_"),
        "_self"
      )
      .focus();
  };

  const autoColumnFunction = (column) => {
    column.headerFilter = true; // add header filter to every column
    column.headerFilterPlaceholder = "filter";
    if (column.field == "DATASET_UUID") {
      column.visible = false;
    }
  };
</script>

<main>
  <TableAuto
    {tableDataUrl}
    {...tablePluginSettings}
    {customTableConfig}
    {rowClickfFunction}
    {autoColumnFunction}
  />
</main>
