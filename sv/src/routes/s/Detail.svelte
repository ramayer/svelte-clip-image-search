<script lang="ts">
    export let results: { q: string | null; ids: number[] } | null;
    import { preview_store, detail_store, cols_store } from "./stores.js";

    let cols = 7;
    let d_img = 0;
    let p_img = 0;
    preview_store.subscribe((x) => (p_img = x));
    detail_store.subscribe((x) => (d_img = x));
    cols_store.subscribe((x) => (cols = x));
    let ids = results ? results.ids : [];
    $: d_idx = ids.indexOf(d_img ?? 0);
    $: related_pic_ids = Array.from({ length: 10 }, (_, i) =>
        idx_to_id(d_idx + i - 5)
    );

    function idx_to_id(idx: number) {
        return ids[(idx + ids.length) % ids.length];
    }

    function makelink(new_d: number | null) {
        let base_url = "?";
        let new_q = results && results.q ? results.q : "";
        let p;
        if (new_d) {
            p = new URLSearchParams({ q: new_q, d: "" + new_d });
        } else {
            p = new URLSearchParams({ q: new_q });
        }
        return base_url + p;
    }

    function cliplink(new_d: number) {
        let base_url = "?";
        let new_q = 'clip:'+new_d
        let p = new URLSearchParams({ q: new_q });
        return base_url + p;
    }

    console.log(related_pic_ids);
</script>

{#if d_img != 0}
    <div
        class="fixed p-10 rounded-2xl top-[5vh] left-[5vw] h-[90vh] w-[90vw] bg-slate-900 z-0"
    >
        <div
            class="w-full bg-gray-800 py-2 px-4 flex justify-between items-center text-white text-2xl focus:outline-none"
        >
            <a href={makelink(idx_to_id(d_idx - 20))}>&#x2AF7;&#xFE0E;</a>
            {#each related_pic_ids as rid}
                <a href={makelink(rid)} class="inline-block">
                    <img
                        style="max-height:30px;"
                        alt={"" + rid}
                        src="/t/{rid}"
                    />
                </a>
            {/each}
            <a href={makelink(idx_to_id(d_idx + 20))}>&#x2AF8;&#xFE0E;</a>
            <a href={makelink(null)}>&#x2715;&#xFE0E;</a>
        </div>

        Details for {d_img}
        <a href={"/d/"+d_img} class="hover:underline text-slate-400">Source</a> | 
        <a href={cliplink(d_img)} class="hover:underline text-slate-400">More like this</a>
        <div>
        <img
            alt={"" + d_img}
            style="max-height:80%; max-width:100%;"
            src="/i/{d_img}"
        />
        </div>
    </div>
{/if}
