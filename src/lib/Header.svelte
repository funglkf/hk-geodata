<script>
  import { page } from "$app/stores";

  const headerList = [
    { href: "/", name: "DataSet" },
    { href: "/dataset", name: "DataTable" },
    // { href: "/map", name: "map" },
  ];
</script>

<header>
  <div class="px-6 py-1">
    <div
      class="container mx-auto flex items-center justify-center border-b-2 border-gray-900"
    >
      <img class="h-4 w-4 mx-1" src="/favicon.svg" alt="Icon" />
      <a
        class="flex md:hidden items-center font-serif italic font-semibold text-lg mr-4"
        href="/"
      >
        HK Geo Data
      </a>
      <a
        class="hidden md:flex items-center font-serif italic font-semibold text-lg mr-4"
        href="/"
      >
        Hong Kong Geo Data
      </a>
      <ul
        class="flex items-end space-x-3 scrollmenu overflow-x-auto header-scrollbar"
      >
        {#each headerList as item}
          <li>
            <a
              href={item.href}
              class={`text-base text-gray-500 hover:text-gray-400  
											${$page.url.pathname === item.href ? "underline" : " "}`}
            >
              {item.name}</a
            >
          </li>
        {/each}
      </ul>
    </div>
  </div>
</header>

<style>
  /* Thin scrollbar for Chrome, Safari and Opera */
  .header-scrollbar::-webkit-scrollbar {
    height: 4px; /* height of horizontal scrollbar */
    /* width: 4px;               /* width of vertical scrollbar */
    /* border: 4px solid #2f19be;  */
  }

  .header-scrollbar::-webkit-scrollbar-track {
    border-radius: 100vh;
    background: #ffffff;
  }

  .header-scrollbar::-webkit-scrollbar-thumb {
    background: #ababab;
    border-radius: 100vh;
    /* border: 3px solid #20ccb8; */
  }

  .header-scrollbar::-webkit-scrollbar-thumb:hover {
    background: #5f5f5f;
  }

  /* a.active{
	color: rgb(168, 168, 168);
} */
</style>
