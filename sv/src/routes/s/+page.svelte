<script lang="ts">
    import {
        preview_store,
        detail_store,
        cols_store,
        q_store,
    } from "./stores.js";
    import { page } from "$app/stores";
    import ResultList from "./ResultList.svelte";
    import Detail from "./Detail.svelte";
    import PreviewContainer from "./PreviewContainer.svelte";
    import SearchForm from "./SearchForm.svelte";
    import type { PageData } from "./$types";
    import { onMount } from "svelte";
    export let data: PageData;

    function handleKeydown(
        event: KeyboardEvent) {
        if (event.code == "Escape") {
            preview_store.set(0)
        }
    }
    const url = $page.url; // this will stay as the original value of the url

    $: q_store.set($page.url.searchParams.get("q") || "");
    $: detail_store.set(parseInt($page.url.searchParams.get("d") || "0"));

    let top_element: HTMLDivElement;

    onMount(() => {
        console.log("s/+page.svelte onMount()");
        top_element?.scrollIntoView();
    });

    let cols = 7;
    let d_img = 0;
    detail_store.subscribe((x) => (d_img = x));
    cols_store.subscribe((x) => (cols = x));

    $: console.log("=== +page.svelte");
    // $: console.log("+page.svelte page", $page);
    // $: console.log("+page.svelte data", data);
    // $: console.log("+page.svelte url", url);
    // $: console.log("+page.svelte q", q);
</script>

<svelte:window on:keydown={handleKeydown} />

<SearchForm />
<div class="h-12" bind:this={top_element} />
<ResultList results={data}>hi</ResultList>
{#if cols > 4}
    <PreviewContainer />
{/if}
<Detail results={data} />
