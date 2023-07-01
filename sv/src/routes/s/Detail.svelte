<script lang="ts">
    export let d: string | null;
    export let results: { q: string | null; ids: number[] } | null;
    import { page } from "$app/stores";

    let ids = results ? results.ids : [];
    let d_idx = 0;
    let q = $page.url.searchParams.get("q");
    $: d = $page.url.searchParams.get("d");
    $: d_idx = ids.indexOf(parseInt(d ?? ""));
    function makelink(new_idx: number) {
        let new_d = ids[(new_idx + ids.length)%ids.length ]
        let base_url = "?";
        let new_q = results && results.q ? results.q : '';
        let params = new URLSearchParams({
            q: new_q,
            d: ""+new_d,
        });
        return base_url + params;
    }
</script>
{#if d}
<div
    class="fixed p-10 rounded-2xl top-[5vh] left-[5vw] h-[90vh] w-[90vw] bg-slate-900"
>
    Details for {d}

    <a href={makelink(d_idx-1)}>prv</a> -- 
    <a href={makelink(d_idx+1)}>nxt</a>

    {#if d}
        <img
            alt={"" + d}
            class="m-auto"
            style="max-height:100%, max-width:100%;"
            src="/i/{d}"
        />
    {/if}
</div>
{/if}