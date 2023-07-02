<script lang="ts">
    import { preview_store, detail_store, cols_store, q_store } from "./stores.js";

    import { page } from "$app/stores";
    import type { PageData } from "./$types";

    let q = $page.url.searchParams.get("q");
    let min_cols = 1;
    let max_cols = 30;
    let cols = 7;
    let inv_cols = max_cols - cols + 1;

    $: cols_store.set(max_cols - inv_cols + min_cols)
    let questions = [
        { id: 1, text: `Img` },
        { id: 2, text: `Txt` },
    ];

    q_store.subscribe((x)=>q=x)
    let selected = 0;

    let answer = "";    
</script>    

<form>
    <div
        class="p-1 pr-3 rounded-2xl flex w-full bg-transparent [&>*]:bg-gray-900 [&>*]:border-gray-500 [&>*]:border"
    >
        <div class="rounded-l-lg p-1">
            <a href="/" class="inline-block" style="transform: rotate(45deg);"
                >⚲</a
            >
        </div>
        <div class="flex-grow flex w-10">
        <input
            type="search"
            name="q"
            bind:value={q}
            class="inline-flex flex-grow p-1 bg-gray-800"
        /></div>
        <select bind:value={selected} on:change={() => (answer = "")} class="">
            {#each questions as question}
                <option value={question}>
                    {question.text}
                </option>
            {/each}
        </select>
        <label class="pt-2 flex-shrink">
            <input type="range" 
            class="flex-shrink"
            bind:value={inv_cols} min="{min_cols}" max="{max_cols}" />
        </label>
        <button type="submit" class="rounded-r-lg">
            <div class="inline-flex">&nbsp;👀&nbsp;</div>
        </button>
    </div>
</form>
