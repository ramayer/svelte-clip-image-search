<script lang="ts">
    import { preview_store, cols_store } from "./stores.js";
    import { page } from "$app/stores";
    import ResultList from "./ResultList.svelte";
    import Detail from "./Detail.svelte";
    import PreviewContainer from "./PreviewContainer.svelte";
    import SearchForm from "./SearchForm.svelte";
    import type { PageData } from "./$types";
    import { onMount } from "svelte";
    export let data: PageData;

    function handleEscape(event: KeyboardEvent) {
        if (event.code == "Escape") {
            preview_store.set(0);
        }
    }
    const url = $page.url; // this will stay as the original value of the url
    $: q = $page.url.searchParams.get("q") || "";

    let top_element: HTMLDivElement;

    onMount(() => {
        console.log("s/+page.svelte onMount()");
        if (data.d) {
            const selectedimg = document.getElementById("" + data.d);
            //selectedimg?.scrollIntoView();
            console.log("TODO - consider scrolling into view here, or maybe later")
        }
        //top_element?.scrollIntoView();
    });
    let cols = 9;
    cols_store.subscribe((x) => (cols = x));

    $: console.log("=== +page.svelte");
    // $: console.log("+page.svelte page", $page);
    // $: console.log("+page.svelte data", data);
    // $: console.log("+page.svelte url", url);
    // $: console.log("+page.svelte q", q);
</script>

<svelte:window on:keydown={handleEscape} />
<SearchForm />
<div class="h-12" bind:this={top_element} />

<ResultList results={data}>hi</ResultList>

{#if cols > 4 && !data.d}
    <PreviewContainer />
{/if}
{#if data.d}
    <Detail results={data} />
{/if}
