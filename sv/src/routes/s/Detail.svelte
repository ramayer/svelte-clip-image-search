<script lang="ts">
    import { goto } from "$app/navigation";
    import Preview from "./Preview.svelte";
    import type { PageData } from "./$types";
    import { browser } from "$app/environment"; // for infinite scroll
    // import { swipe } from 'svelte-gestures'; // consider https://www.npmjs.com/package/svelte-gestures

    export let results: PageData;
    import { preview_store, cols_store, split_header_store } from "./stores.js";

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
        //console.log("detail keydown ", event);
        if (event.code == "Escape") {
            let loc = makelink(null);
            goto(loc, { noScroll: true });
        }
        if (event.code == "ArrowRight") {
            let loc = makelink(idx_to_id(d_idx + 1));
            goto(loc, { noScroll: true });
        }
        if (event.code == "ArrowLeft") {
            let loc = makelink(idx_to_id(d_idx - 1));
            goto(loc, { noScroll: true });
        }
        // console.log("key event = ", event);
        // key = event.key;
        // code = event.code;
    }

    interface FaceData {
        bbox: number[];
        embedding: number[];
    }

    function face_data_to_overlay(f: FaceData, w: number, h: number, clr: number[]) {
        let x0 = f.bbox[0];
        let y0 = f.bbox[1];
        let x1 = f.bbox[2];
        let y1 = f.bbox[3];
        return {
            x: (100 * x0) / w,
            y: (100 * y0) / h,
            w: (100 * (x1 - x0)) / w,
            h: (100 * (y1 - y0)) / h,
            c: clr, // "#f80",
        };
    }

    /* This vector math should move to a different javascript file */
    function dotProduct(vector1: number[], vector2: number[]): number {
        if (vector1.length !== vector2.length) {
            throw new Error("Vectors must have the same length");
        }

        return vector1.reduce(
            (acc, val, index) => acc + val * vector2[index],
            0
        );
    }

    function magnitude(vector: number[]): number {
        return Math.sqrt(vector.reduce((acc, val) => acc + val * val, 0));
    }

    function cosineSimilarity(vectorX: number[], vectorY: number[]): number {
        if (!Array.isArray(vectorX) || !Array.isArray(vectorY)) {
            throw new Error("Input must be arrays");
        }

        const dotProd = dotProduct(vectorX, vectorY);
        const magX = magnitude(vectorX);
        const magY = magnitude(vectorY);

        if (magX === 0 || magY === 0) {
            throw new Error("One or both vectors have zero magnitude");
        }

        return dotProd / (magX * magY);
    }
    /*  end of vector math */

    /* nice color */
    function floatToColor(hue: number): number[] {
        // Ensure the value is within the valid range [0, 1]
        //value = Math.min(1, Math.max(0, value));

        // Calculate hue based on the value
        //const hue: number = (1 - value) * 240; // 0 represents green, 240 represents red

        // Convert HSL to RGB
        const h: number = hue / 360;
        const s: number = 1;
        const l: number = 0.5;
        const c: number = (1 - Math.abs(2 * l - 1)) * s;
        const x: number = c * (1 - Math.abs(((h * 6) % 2) - 1));
        const m: number = l - c / 2;

        let r: number, g: number, b: number;

        if (h < 1 / 6) {
            [r, g, b] = [c, x, 0];
        } else if (h < 2 / 6) {
            [r, g, b] = [x, c, 0];
        } else if (h < 3 / 6) {
            [r, g, b] = [0, c, x];
        } else if (h < 4 / 6) {
            [r, g, b] = [0, x, c];
        } else if (h < 5 / 6) {
            [r, g, b] = [x, 0, c];
        } else {
            [r, g, b] = [c, 0, x];
        }
        return ([r,g,b]);
        //console.log("RRRRRRRRRRRRRGBAA ",r,g,b)
        //return rgb_to_hex(0,0,1);
        /*
        return rgb_to_rgb(1,0,1,0.5);
        return rgb_to_rgba(r,g,b,0.5);
        return "rgb("+r*255+" "+g*255+" "+b*255+")"
        return rgb_to_hex(r+m,g+m,b+m);
        */
    }
    function rgb_to_rgb(r: number,g: number,b: number,a: string | number) {
        return("rgb(" +
        [r,g,b].map((x)=>Math.round(x*255)).join(" ") +
        ")");
    }
    function rgb_to_rgba(r: number,g: number,b: number,a: string | number) {
        return("rgba(" +
        [r,g,b].map((x)=>Math.round(x*255)).join(" ") +
        " "+a+")");
    }
    function rgb_to_hex(r: number,g: number,b: number) {
     // Convert RGB to hexadecimal color code
        const toHex = (c: number): string => {
            const hex = Math.round(c * 255).toString(16);
            return hex.length === 1 ? "0" + hex : hex;
        };

        const color: string = `#${toHex(r)}${toHex(g)}${toHex(b)}`;
        return color;
    }

    function calculate_box_color(f: FaceData, r: PageData) {
        var cos_sim = cosineSimilarity(f.embedding, r.target);
        var hsl_degrees = (360 + 120 - (Math.acos(cos_sim) * 180/Math.PI))%360
        var clr = floatToColor(hsl_degrees);
        console.log("cos_sim = ", cos_sim , " giving ", clr);
        return clr
    }

    $: h = results.details?.img_data.height;
    $: w = results.details?.img_data.width;
    $: overlay_data = results.details?.face_dat?.map((f: FaceData) => {
        let clr = calculate_box_color(f, results);
        return face_data_to_overlay(f, w, h, clr);
    });
    $: numfaces = results.details?.face_dat?.length || 0;

    let prev_image = browser ? new Image() : undefined;
    let next_image = browser ? new Image() : undefined;
    let prev_thm = browser ? new Image() : undefined;
    let next_thm = browser ? new Image() : undefined;
    function prefetch_next_full_sized_images(d_idx: number) {
        setTimeout( () => {
        if (browser && prev_image && next_image && next_thm && prev_thm) {
            next_image.src = "/i/" + idx_to_id(d_idx + 1);
            prev_image.src = "/i/" + idx_to_id(d_idx - 1);
            next_thm.src = "/t/" + idx_to_id(d_idx + 1);
            prev_thm.src = "/t/" + idx_to_id(d_idx - 1);
            console.log("attempting to prefetch",next_image.src, " and ", prev_image.src)
        }},1000);
    }
    $: prefetch_next_full_sized_images(d_idx);

    let split_header = false;
    split_header_store.subscribe((x) => (split_header = x));
</script>

<svelte:window on:keydown={handleKeydown} />

{#if d_img != 0}
    <div
        class="detail_container rounded-none bg-slate-900 border-slate-500 border-0"
        style="width:{(100 * (cols - 1)) /
            cols}%; --detail-container-bottom:{split_header
            ? 2
            : 70}px; --detail-container-top:{split_header ? 2 : 70}px"
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
            class=" mr-20 text-center flex flex-nowrap whitespace-nowrap justify-center"          
        >
            <div class="grow" />
            {#if false}
            <!-- firefox and chrome differ about "min-width"-->
            {/if}
            <a
                class="shrink grow whitespace-nowrap text-clip overflow-clip mr-4"
                style="min-width:10%; max-width:50%"
                href={"/d/" + d_img}>{title}</a
            >
            {#if /.*commons.wikimedia.org.*/.test(results.details.metadata.src_uri)}
                <a
                    href={"/d/" + d_img}
                    class="grow whitespace-nowrap mx-4"
                    style="min-width:10%; max-width:50%"
                    title="Copyright © information for this image on wikimedia commons here."
                    >copyright © info on wikimedia</a
                >
            {/if}
            <div class="grow" />
            {#if numfaces}
                <a
                    class="whitespace-nowrap mx-2"
                    href={cliplink(d_img, "face")}
                    title="Search for any of the {results.details?.face_dat
                        ?.length} faces in the image [f]; or click one of the highlighted faces below"
                    >{numfaces > 10
                        ? "👤 * " + numfaces
                        : "👤".repeat(numfaces % 2) +
                          "👥".repeat(numfaces / 2)}</a
                >
            {/if}
            <div class="grow" />
            <a
                class="whitespace-nowrap mx-2"
                href={cliplink(d_img)}
                title="Similar images according to a clip model [c]">▦</a
            >
            <div class="grow" />
        </div>
        <div class="safe_footer_area_l">
            <a
                href={makelink(idx_to_id(d_idx - 1))}
                data-sveltekit-noscroll
                title="[Left Arrow]"
                class="text-white bg-blue-800 hover:bg-blue-800
                focus:ring-4 focus:outline-none focus:ring-blue-300
                font-medium rounded-lg text-sm p-2.5
                text-center inline-flex items-center mr-2
                dark:bg-slate-700 dark:hover:bg-blue-900 dark:focus:ring-blue-800"
            >
                <svg
                    class="w-5 h-5"
                    aria-hidden="true"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 14 10"
                >
                    <path
                        stroke="currentColor"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M12 1 L 1 5 L 12 9"
                    />
                </svg>
                <span class="sr-only">Icon description</span>
            </a>
            <!--
            <div
                class=" items-stretch
                m-0 text-3xl rounded-xl border border-gray-500
                flex w-full
                justify-center align-middle object-center
                overflow-clip
                 header
                whitespace-nowrap
                footer"
            >
                <a
                    class="footer-item p-1 bg-slate-800"
                    href={makelink(idx_to_id(d_idx - 1))}
                    data-sveltekit-noscroll
                    title="[Left Arrow]">&#x22B2;&#xFE0E;</a
                >
            </div>
        -->
        </div>

        <div class="safe_footer_area_r">
            <a
                href={makelink(idx_to_id(d_idx + 1))}
                data-sveltekit-noscroll
                title="[Right Arrow]"
                class="text-white bg-blue-800 hover:bg-blue-800
            focus:ring-4 focus:outline-none focus:ring-blue-300
            font-medium rounded-lg text-sm p-2.5
            text-center inline-flex items-center mr-2
            dark:bg-slate-700 dark:hover:bg-blue-900 dark:focus:ring-blue-800"
            >
                <svg
                    class="w-5 h-5"
                    aria-hidden="true"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 14 10"
                >
                    <path
                        stroke="currentColor"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M1 1 L 12 5 L 1 9"
                    />
                </svg>
                <span class="sr-only">Icon description</span>
            </a>
            <!--
            <div
                class=" items-stretch
                        m-0 text-3xl rounded-xl border border-gray-500
                        
                        flex w-full
                        justify-center align-middle object-center
                        overflow-clip
                         header
                        whitespace-nowrap
                        footer"
            >
                <a
                    href={makelink(idx_to_id(d_idx + 1))}
                    class="footer-item p-1 bg-slate-800"
                    data-sveltekit-noscroll
                    title="[Right Arrow]">&#x22B3;&#xFE0E;</a
                >


            </div>
            -->
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
        top: 0;
        right: 0%;
        width: 95vw;
        display: flex;
        flex-direction: column;
    }

    .image-container {
        flex: 1;
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
            zbottom: calc(
                var(--detail-container-bottom) + env(safe-area-inset-bottom)
            );
            top: calc(var(--detail-container-top) + env(safe-area-inset-top));
            /*bottom: calc(2px + env(safe-area-inset-bottom));*/
            bottom: 0px;
            right: 0px;
            width: 80vw;
            transform: none;
            /*
            height: calc(
                100vh - env(safe-area-inset-top) - env(safe-area-inset-bottom) -
                    45px
            );
            */
        }
    }

    .safe_footer_area {
        position: fixed;
        /* background-color: rgba(0, 0, 0, 0.5); */
        padding: 1mm;
        bottom: 10px; /* Fallback value */
        left: 10px;
        right: 10px;
        z-index: 50;
    }
    @supports (padding-top: env(safe-area-inset-top)) {
        .safe_footer_area_l {
            position: fixed;
            bottom: env(safe-area-inset-bottom);
            left: env(safe-area-inset-left);
            /*background-color: rgba(0, 0, 0, 0.5);*/
            padding-top: 1mm;
            padding-bottom: 1mm;
            padding-left: 1mm;
            padding-right: 1mm;
            z-index: 50;
        }
        .safe_footer_area_r {
            position: fixed;
            bottom: env(safe-area-inset-bottom);
            right: env(safe-area-inset-right);
            /*background-color: rgba(0, 0, 0, 0.5);*/
            padding-top: 1mm;
            padding-bottom: 1mm;
            padding-left: 1mm;
            padding-right: 1mm;
            z-index: 50;
        }
    }
    .footer {
        display: flex;
    }
    .footer-item {
        border-right: 1px solid #666;
        font-weight: bolder;
    }

    .footer-item:last-child {
        border-right: none;
    }
    *.footer-item:hover {
        background: rgba(0, 0, 200, 0.8);
        color: #ccf;
    }
    a.footer-item {
        display: block;
        /*background-color: rgba(0, 0, 0, 0.5);*/
        text-align: center;
        color: rgb(2 132 199 / var(--tw-text-opacity));
    }
</style>
