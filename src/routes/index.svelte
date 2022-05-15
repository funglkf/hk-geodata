<script>
  import TableAuto from "$lib/TabulatorAutoUse.svelte";

  const tableDataUrl = "/json/simplified_datasetinfo.json";

  const tablePluginSettings = {
    title: "Dataset (Click to open on map)",
    copyData: false,
    saveExcel: true,
    saveCSV: false,
  };

  const customTableConfig = {
    layout: "fitColumns", //fit columns to width of table
    paginationSize: 1000,
    tooltips: true, //show tool tips on cells
    paginationCounter: "rows", //display count of paginated rows in footer
    autoColumns: false,
    columns: [
      { title: "DATASET_UUID", field: "DATASET_UUID", visible: false },
      { title: "DATASET_NAME_TC", field: "DATASET_NAME_TC" ,minWidth:"250px",  headerFilter: true, headerFilterPlaceholder:"Filter"},
      { title: "nameTC", field: "nameTC",minWidth:"100px" , headerFilter: "list", headerFilterPlaceholder:"Filter"},
      { title: "DATASET_NAME_EN", field: "DATASET_NAME_EN" ,minWidth:"250px", headerFilter: true, headerFilterPlaceholder:"Filter"},
      { title: "nameEN", field: "nameEN",minWidth:"100px" , headerFilter: true, headerFilterPlaceholder:"Filter"},
    ],
  };

  const rowClickfFunction = (e, row) => {
    window
      .open(
        "/map/" + row.getData()["DATASET_NAME_EN"].replace(/[^\w_-]+/g, "_"),
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

  const dataLoadedFunction = (table, data) => {
    let list = { "": "" };
    let colData = data.map((a) => a["nameTC"]);
    colData.forEach(function (item) {
      if (typeof item !== "undefined") {
        list[item] = item;
      }
    });
    table.updateColumnDefinition("nameTC", {
      headerFilterParams: { values: list },
    });
  };
</script>

<main>
  <TableAuto
    {tableDataUrl}
    {...tablePluginSettings}
    {customTableConfig}
    {rowClickfFunction}
    {autoColumnFunction}
    {dataLoadedFunction}
  />
</main>
