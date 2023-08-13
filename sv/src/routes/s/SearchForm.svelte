<script lang="ts">

    import { page } from "$app/stores";
    import type { PageData } from "./$types";
    import { onMount } from "svelte";

    let q_input: HTMLInputElement;
    onMount(() => {
        q = $page.url.searchParams.get("q");
    });

    let q = $page.url.searchParams.get("q");

    function q_changed(new_q: string | null) {
        if (q != new_q) {
            console.log("q changed from " + q + " to ", new_q);
            q = new_q;
        }
    }
    $: q_changed($page.url.searchParams.get("q"));
</script>

<form class="flex-shrink flex w-full" style="flex-wrap: nowrap">
    <input
        bind:this={q_input}
        type="search"
        name="q"
        bind:value={q}
        class="flex-grow flex-shrink focus:outline-none focus p-1 bg-black border border-slate-700 text-s w-7"
    />
    <button type="submit" class="header-item p-2">
        <!--<div class="inline-flex">&nbsp;👀&nbsp;</div>-->
        <div style="transform: rotate(45deg);">⚲</div>
    </button>
</form>

<style>

.header-item {
        border-right: 1px solid #666;
        font-weight: bolder;
        padding: 0.25rem 0.5rem 0.25rem 0.5rem;
    }

    .header-item:last-child {
        border-right: none;
    }
    *.header-item:hover {
        background: rgba(0, 0, 200, 0.8);
        color: #ccf;
    }
    a.header-item {
        display: block;
        /*background-color: rgba(0, 0, 0, 0.5);*/
        text-align: center;
        color: rgb(2 132 199 / var(--tw-text-opacity));
    }
</style>
