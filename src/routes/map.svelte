<script>
  import LeafletMap from "$lib/LeafletMap.svelte";
  const apiUrl =
    'https://geodata.gov.hk/gs/api/v1.0.0/geoDataQuery?q=%7Bv%3A"1%2E0%2E0"%2Cid%3A"2852ec0f-719f-494e-9772-e53af3a2f5bb"%2Clang%3A"ALL"%7D';
</script>

<h1 class="px-6 text-lg font-semibold">Leaflet Map</h1>
<div class="mx-5">
  <LeafletMap {apiUrl} />
</div>
