<script lang="ts">
    import { selected_img, selected_state, cols_store } from "./stores.js";

    import { page } from "$app/stores";
    import ResultList from "./ResultList.svelte";
    import ResultDetail from "./ResultDetail.svelte";
    import type { PageData } from "./$types";

    let q = $page.url.searchParams.get("q");
    let min_cols = 1;
    let max_cols = 20;
    let cols = 10;
    let inv_cols = max_cols - cols;

    $: cols_store.set(max_cols - inv_cols + min_cols)
    let questions = [
        { id: 1, text: `Img` },
        { id: 2, text: `Txt` },
    ];

    let selected = 0;

    let answer = "";    
</script>    

<form>
    <div
        class="p-2 flex w-full [&>*]:bg-gray-900 [&>*]:border-gray-600 [&>*]:border"
    >
        <div class="rounded-l-lg p-1">
            <a href="/" class="inline-block" style="transform: rotate(45deg);"
                >⚲</a
            >
        </div>
        <input
            type="search"
            name="q"
            bind:value={q}
            class="inline-flex flex-grow p-1"
        />
        <select bind:value={selected} on:change={() => (answer = "")} class="">
            {#each questions as question}
                <option value={question}>
                    {question.text}
                </option>
            {/each}
        </select>
        <button type="submit" class="rounded-r-lg">
            <div class="inline-flex">&nbsp;👀&nbsp;</div>
        </button>
        <label style="border:0px; padding-top:5px">
            <input type="range" bind:value={inv_cols} min="{min_cols}" max="{max_cols}" />
        </label>
    </div>
</form>
