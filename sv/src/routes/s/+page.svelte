<script lang="ts">
    import { preview_img, detail_img, cols_store,q_store } from "./stores.js";
    import { page } from "$app/stores";
    import ResultList from "./ResultList.svelte";
    import Detail from "./Detail.svelte";
    import Preview from "./Preview.svelte";
    import SearchForm from "./SearchForm.svelte";
    import type { PageData } from "./$types";
    import { onMount } from "svelte";

    export let data: PageData;

    const url = $page.url; // this will stay as the original value of the url
    let q = $page.url.searchParams.get("q");
    q_store.set(q || '')
    $:d = parseInt($page.url.searchParams.get("d") || '0')
    $:detail_img.set(d)

    let top_element: HTMLDivElement;

    onMount(() => {
        console.log("s/+page.svelte onMount()");
        top_element?.scrollIntoView();
    });

    let cols = 7;
    let d_img = 0;
    detail_img.subscribe((x) => (d_img = x));
    cols_store.subscribe((x) => (cols = x));

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
<ResultList results={data}>hi</ResultList>
{#if cols > 4}
    <Preview/>
{/if}
    <Detail results={data} />
