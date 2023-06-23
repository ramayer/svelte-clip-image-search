<script lang="ts">
    import { selected_img, selected_state, cols_store } from "./stores.js";

    import { page } from "$app/stores";
    import ResultList from "./ResultList.svelte";
    import ResultDetail from "./ResultDetail.svelte";
    import SearchForm from "./SearchForm.svelte";
    import type { PageData } from "./$types";
    import { onMount } from "svelte";

    onMount(() => {
        console.log("s/+page.svelte onMount()");
    });

    let s_img = "";
    let s_state = 0;

    export let data: PageData;
    let cols = 20;

    let debug = "";
    const url = $page.url; // this will stay as the original value of the url
    let q = $page.url.searchParams.get("q");

    selected_img.subscribe((x) => {
        s_img = x;
    });
    selected_state.subscribe((x) => {
        s_state = x;
    });
    cols_store.subscribe((x) => {
        cols = x;
    });

    $: console.log("===");
    $: console.log("+page.svelte page", $page);
    $: console.log("+page.svelte data", data);
    $: console.log("+page.svelte url", url);
    $: console.log("+page.svelte q", q);
</script>

<div class="fixed top-1 left-1 w-full bg-black ...">
    <SearchForm />
</div>
<div class="h-16" />

<div>
    Debug = {s_img}, {s_state}
</div>
<ResultList results={data} {cols}>hi</ResultList>
<ResultDetail selected_img={s_img} selected_state={s_state} />
