<script lang="ts">
    import { writable } from "svelte/store";
    export let results: { q: string | null; ids: number[] } | null;
</script>

Hello ResultList
<div>
    {#if results}
        {#each results["ids"] as r}
        <img src="http://localhost:8000/thm/{r}">
            {r}<br />
        {/each}
    {/if}
</div>

<slot>cool</slot>
