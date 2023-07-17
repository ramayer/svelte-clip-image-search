<script lang="ts">
    import {
        preview_store,
        cols_store,
    } from "./stores.js";

    import { page } from "$app/stores";
    import type { PageData } from "./$types";

    import { onMount } from "svelte";

    let q_input: HTMLInputElement;

    onMount(() => {
        q = $page.url.searchParams.get("q");
        console.log("in searchform onMount attempting to set focus")
        q_input.focus()
    });

    let q = $page.url.searchParams.get("q");
    let min_cols = 1;
    let max_cols = 30;
    let cols = 7; // has an effect
    let inv_cols = max_cols - cols + 1;

    function q_changed(new_q: string | null) {
        if (q != new_q) {
            console.log("q changed from " + q + " to ",new_q);
            q = new_q;
        };
    }
    $: q_changed($page.url.searchParams.get("q"));

    $: cols_store.set(max_cols - inv_cols + min_cols);
    let questions = [
        { id: 1, text: `Img` },
        { id: 2, text: `Txt` },
    ];

    let selected = 0;
    let answer = "";
</script>

<div class="position_nav_bar_safely fixed top-1 left-1 w-full pr-2 z-50">
    <form>
        <div
            class="p-1 pr-3 rounded-2xl flex w-full bg-transparent [&>*]:bg-gray-900 [&>*]:border-gray-500 [&>*]:border"
            style="z-index:999"
        >
            <div class="rounded-l-lg p-1">
                <a
                    href="/"
                    class="inline-block"
                    style="transform: rotate(45deg);">⚲</a
                >
            </div>
            <div class="flex-grow flex w-10">
                <input
                    data-sveltekit-keepfocus
                    bind:this={q_input}
                    type="search"
                    name="q"
                    bind:value={q}
                    class="inline-flex flex-grow p-1 bg-gray-800"
                />
            </div>
            <select
                bind:value={selected}
                on:change={() => (answer = "")}
                class=""
            >
                {#each questions as question}
                    <option value={question}>
                        {question.text}
                    </option>
                {/each}
            </select>
            <label class="pt-2 flex-shrink">
                <input
                    type="range"
                    class="flex-shrink"
                    bind:value={inv_cols}
                    min={min_cols}
                    max={max_cols}
                />
            </label>
            <button type="submit" class="rounded-r-lg">
                <div class="inline-flex">&nbsp;👀&nbsp;</div>
            </button>
        </div>
    </form>
</div>

<style>
    .position_nav_bar_safely {
        position: fixed;
        top: 10px; /* Fallback value */
    }

    @supports (padding-top: env(safe-area-inset-top)) {
        .position_nav_bar_safely {
            top: env(safe-area-inset-top); /* Uses env() if supported */
        }
    }
</style>
