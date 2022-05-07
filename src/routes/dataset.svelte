<script>
  import { onMount } from "svelte";
  import TableAuto from "$lib/TabulatorAutoUse.svelte";

  let tableList = [];
  const tableDataUrl = "/json/simplified_datasetinfo.json";

  onMount(async function () {
    const response = await fetch(tableDataUrl);
    const data = await response.json();
    console.log(data);
    tableList = data.map((obj) => {
      return {
        name: obj["DATASET_NAME_TC"],
        url:
          `https://geodata.gov.hk/gs/api/v1.0.0/geoDataQuery?q=%7Bv%3A%221%2E0%2E0%22%2Cid%3A%22` +
          obj["DATASET_UUID"] +
          `%22%2Clang%3A%22ALL%22%7D`,
      };
    });
  });

  tableList.push({
    name: "post",
    url: "https://jsonplaceholder.typicode.com/posts",
  });

  let tablePluginSettings = {
    copyData: true,
    saveExcel: true,
    saveCSV: false,
  };

  let customTableConfig = {
    // layout: "fitColumns", //fit columns to width of table
    paginationSize: 1000,
    tooltips: true, //show tool tips on cells
    paginationCounter: "rows", //display count of paginated rows in footer
  };
</script>

<main>
  <TableAuto
    {tableDataUrl}
    {...tablePluginSettings}
    {tableList}
    {customTableConfig}
  />
</main>
