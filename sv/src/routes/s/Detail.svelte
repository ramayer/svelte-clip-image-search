<script lang="ts">
    import { goto } from "$app/navigation";
    import Preview from "./Preview.svelte";
    export let results: {
        q: string | null;
        ids: number[];
        details?: any;
    } | null;
    import { preview_store, detail_store, cols_store } from "./stores.js";

    console.log("here results is ", results);

    let cols = 7;
    let d_img = 0;
    let p_img = 0;
    preview_store.subscribe((x) => (p_img = x));
    detail_store.subscribe((x) => (d_img = x));
    cols_store.subscribe((x) => (cols = x));
    let ids = results ? results.ids : [];
    $: d_idx = ids.indexOf(d_img ?? 0);
    $: related_pic_ids = Array.from({ length: 9 }, (_, i) =>
        idx_to_id(d_idx + i - 4)
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
        let new_q = "clip:" + new_d;
        let p = new URLSearchParams({ q: new_q });
        return base_url + p;
    }

    $: title = results?.details?.metadata
        ? results.details.metadata.title
        : "" + d_img;
    console.log(related_pic_ids);

    let key: string;
    let code: string;

    function handleKeydown(event: KeyboardEvent) {
        if (event.code == "Escape") {
            let loc = makelink(null);
            goto(loc);
        }
        if (event.code == "ArrowRight") {
            let loc = makelink(idx_to_id(d_idx + 1));
            goto(loc);
        }
        if (event.code == "ArrowLeft") {
            let loc = makelink(idx_to_id(d_idx - 1));
            goto(loc);
        }
        console.log("key event = ", event);
        key = event.key;
        code = event.code;
    }
</script>

<svelte:window on:keydown={handleKeydown} />

{#if d_img != 0}
    <div
        class="detail_container bg-slate-900 p-4 rounded-2xl border-slate-500 border-2"
    >
        <div
            class="w-full bg-gray-800 py-2 px-4 flex justify-around items-center text-white text-2xl focus:outline-none"
        >
            <!-- &#x2AF7; is nicer but missing on old Ubuntu -->
            <div>
            <a href={makelink(idx_to_id(d_idx - 20))}>&#x22B2;&#xFE0E;</a></div>
            <div class="flex-grow flex  justify-around">
            {#each related_pic_ids as rid}
                <a href={makelink(rid)} class="inline-block max-w-[10%]">
                    <img
                    class="max-w-[100%]  "
                        style="max-height:30px;"
                        alt={"" + rid}
                        src="/t/{rid}"
                    />
                </a>
            {/each}
        </div>
            <div><a href={makelink(idx_to_id(d_idx + 20))}>&#x22B3;&#xFE0E;</a></div>
            <!-- 2AF8 is nicer -->
            <div><a href={makelink(null)}>&#x2715;&#xFE0E;</a></div>
        </div>
        <div class="caption">
            {title}
            <br />
            <a href={"/d/" + d_img}>Source</a>
            |
            <a href={cliplink(d_img)}>More like this</a>
        </div>
        <div class="image-container">
            {#if false}
                <img class="detail_img" src="/i/{d_img}" alt={title} />
            {:else}
                <Preview b_url="/i/{d_img}" s_url="/t/{d_img}" href={"/d/" + d_img}/>
            {/if}
        </div>
    </div>
{/if}

<style>
    .detail_container {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        height: 95vh;
        width: 95vw;
        display: flex;
        flex-direction: column;
    }

    .image-container {
        flex: 1;
        display: flex;
        justify-content: center;
        align-items: center;
        overflow: hidden;
    }

    .detail_img {
        max-width: 100%;
        max-height: 100%;
    }

    .caption {
        padding: 10px;
        text-align: center;
    }

    @supports (padding-top: env(safe-area-inset-top)) {
        /* annoying phone browsers cover up parts of vh x vw */
        .detail_container {
            top: calc(40px + env(safe-area-inset-top));
            left: 5vw;
            width: 90vw;
            transform: none;
            height: calc(
                100vh - env(safe-area-inset-top) - env(safe-area-inset-bottom) -
                    50px
            );
        }
    }
</style>
