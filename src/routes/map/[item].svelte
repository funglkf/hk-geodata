<script context="module">
  export const prerender = true;
  export async function load({ fetch, params }) {
    // let post;
    // try {
    //   // here we are gonna fetch the single article by id
    //   post = await fetch(`/${params.item}`);
    //   post = await post.json();
    // } catch (e) {
    //   console.log(e);
    // }
    return {
      props: {
        apiUrl: "/json/" + params.item + ".geojson",
        item: params.item,
      },
    };
  }
</script>

<script>
  import LeafletMap from "$lib/LeafletMap.svelte";

  export let apiUrl;
  export let item;
</script>

<h1 class="px-6 text-lg font-semibold">{item.replace(/[_]/g, " ")}</h1>
<div class="mx-5">
  <LeafletMap {apiUrl} />
</div>
