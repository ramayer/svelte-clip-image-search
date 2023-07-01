<script lang="ts">
    import { selected_img, selected_state, cols_store } from "./stores.js";

    import { page } from "$app/stores";
    import ResultList from "./ResultList.svelte";
    // import ResultDetail from "./ResultDetail.svelte";
    import Detail from "./Detail.svelte";
    import Preview from "./Preview.svelte";
    import SearchForm from "./SearchForm.svelte";
    import type { PageData } from "./$types";
    import { onMount } from "svelte";

    let top_element: HTMLDivElement;

    onMount(() => {
        console.log("s/+page.svelte onMount()");
        top_element?.scrollIntoView()
    });

    let s_img = "";
    let s_state = 0;

    export let data: PageData;
    let cols = 7;

    let debug = "";
    const url = $page.url; // this will stay as the original value of the url
    let q = $page.url.searchParams.get("q");
    let d = $page.url.searchParams.get("d");

    selected_img.subscribe((x) => {
        s_img = x;
    });
    selected_state.subscribe((x) => {
        s_state = x;
    });
    cols_store.subscribe((x) => {
        cols = x;
    });

    $: console.log("=== +page.svelte");
    // $: console.log("+page.svelte page", $page);
    // $: console.log("+page.svelte data", data);
    // $: console.log("+page.svelte url", url);
    // $: console.log("+page.svelte q", q);
</script>

<div class="fixed top-1 left-1 w-full pr-2">
    <SearchForm />
</div>
<div class="h-12" bind:this={top_element} />
<ResultList results={data} {cols}>hi</ResultList>
{#if cols>4}
<Preview selected_img={s_img} selected_state={s_state} />
{/if}
{#if d}
<Detail d={d} results={data}></Detail>
{/if}