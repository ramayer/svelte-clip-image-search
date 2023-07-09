<script lang="ts">
    import { goto } from "$app/navigation";
    import Preview from "./Preview.svelte";
    import type { PageData } from "./$types";

    export let results: PageData;
    import { preview_store, cols_store } from "./stores.js";

    // console.log("Detail.svelte for d = ", results.d);

    let cols = 7;
    $: d_img = results.d || 0;
    let p_img = 0;
    preview_store.subscribe((x) => (p_img = x));
    cols_store.subscribe((x) => (cols = x));
    let ids = results ? results.ids : [];
    $: d_idx = ids.indexOf(d_img ?? 0);
    // $: related_pic_ids = Array.from({ length: 9 }, (_, i) =>
    //     idx_to_id(d_idx + i - 4)
    // );

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

    function cliplink(new_d: number, model: string = "clip") {
        let base_url = "?";
        let new_q = model + ":" + new_d;
        let p = new URLSearchParams({ q: new_q });
        return base_url + p;
    }

    $: title = results?.details?.metadata
        ? results.details.metadata.title
        : "" + d_img;

    let key: string;
    let code: string;

    function handleKeydown(event: KeyboardEvent) {
        console.log("detail keydown ", event);
        if (event.code == "Escape") {
            let loc = makelink(null);
            goto(loc,{noScroll:true});
        }
        if (event.code == "ArrowRight") {
            let loc = makelink(idx_to_id(d_idx + 1));
            goto(loc,{noScroll:true});
        }
        if (event.code == "ArrowLeft") {
            let loc = makelink(idx_to_id(d_idx - 1));
            goto(loc,{noScroll:true});
        }
        // console.log("key event = ", event);
        // key = event.key;
        // code = event.code;
    }

    function face_data_to_overlay(f: { bbox: number[] }, w: number, h: number) {
        let x0 = f.bbox[0];
        let y0 = f.bbox[1];
        let x1 = f.bbox[2];
        let y1 = f.bbox[3];
        return {
            x: (100 * x0) / w,
            y: (100 * y0) / h,
            w: (100 * (x1 - x0)) / w,
            h: (100 * (y1 - y0)) / h,
            c: "#f80",
        };
    }
    $: h = results.details?.img_data.height;
    $: w = results.details?.img_data.width;
    $: overlay_data = results.details?.face_dat?.map((f: { bbox: number[] }) =>
        face_data_to_overlay(f, w, h)
    );
</script>

<svelte:window on:keydown={handleKeydown} />

{#if d_img != 0}
    <div
        class="detail_container rounded-none  bg-slate-900 border-slate-500 border-0 "
        style="width:{100 * (cols-1)/cols}%"
    >
    <div class="image-container">
        {#if false}
            <img class="detail_img" src="/i/{d_img}" alt={title} />
        {:else}
            <Preview
                b_url="/i/{d_img}"
                s_url="/t/{d_img}"
                img_id={d_img}
                width={results.details?.img_data.width}
                height={results.details?.img_data.height}
                {overlay_data}
            />
        {/if}
    </div>

        <div
            class="border-0 w-full flex justify-around items-center text-2xl focus:outline-none whitespace-nowrap"
        >
            <div class="px-4">
                <a href={makelink(idx_to_id(d_idx - 20))}>&#x22B2;&#xFE0E;</a>
            </div>
            |
            <div class="m_2 text-sm px-1">
                <a href={"/d/" + d_img}>{title}</a>
            </div>
            |
            <div class="px-2 text-sm">
                <a href={cliplink(d_img, "face")}
                    >{results.details?.face_dat?.length} faces</a
                >
            </div>
            |
            <div class="px-2 text-sm">
                <a href={cliplink(d_img)}>More like this</a>
            </div>
            |
            <div class="px-2">
                <a href={makelink(idx_to_id(d_idx + 20))}>&#x22B3;&#xFE0E;</a>
            </div>
            |
            <div class="px-2">
                <a href={makelink(null)}>&#x2715;&#xFE0E;</a>
            </div>
        </div>
    </div>
{/if}

<style>
    .m_2 {
        flex-grow: 1;
        flex-shrink: 1;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .detail_container {
        position: fixed;
        top: 50%;
        right: 0%;
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

    @supports (padding-top: env(safe-area-inset-top)) {
        /* annoying phone browsers cover up parts of vh x vw */
        .detail_container {
            top: calc(45px + env(safe-area-inset-top));
            bottom: env(safe-area-inset-bottom);
            right: 0px;
            width: 80vw;
            transform: none;
            height: calc(
                100vh - env(safe-area-inset-top) - env(safe-area-inset-bottom) -
                    45px
            );
        }
    }
</style>
