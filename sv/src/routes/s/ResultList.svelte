<script lang="ts">
    import ResultImg from "./ResultImg.svelte";
    import { browser } from "$app/environment"; // for infinite scroll
    import { onMount, tick } from "svelte";
    import {
        preview_store,
        cols_store,
        thm_size_store,
    } from "./stores.js";

    import type { PageData } from "./$types";
    export let results: PageData;

    let cols = 9;
    //let d_img = results.d || 0;
    let p_img = 0;
    preview_store.subscribe((x) => (p_img = x));
    cols_store.subscribe((x) => (cols = x));

    $: q = results?.q || "";

    let num_available = 12;
    let num_visible = 1; // has no effect
    let imgs: number[] = [];

    $: num_available = results ? results["ids"].length : 0;
    $: imgs = results ? results["ids"] : [];
    $: gridstyle = `grid-template-columns: ${"1fr ".repeat(cols)}`;

    // roughly assume square for people with javascript turned off
    $: num_visible = q ? cols * Math.min(cols,6) : 2; 

    $: console.log("ResultList.svetle imgs length is ", imgs.length);
    // $: console.log("ResultList.svetle results", results && results["ids"]);

    let observer: IntersectionObserver | null;
    let result_grid_element: Element | null = null;
    let gallery_width = 1024;

    // rounds up to 60, 120, 240, 480, 960, 1920
    function nice_thumbnail_size(cols: number, gallery_width: number) {
        if (cols == 0 || gallery_width == 0) {
            return 800;
        }
        const float_size = gallery_width / cols;
        const size_in_units_of_30px = float_size / 12;
        const exponent = Math.ceil(Math.log2(size_in_units_of_30px)/ .5);
        const rounded_value = 12 * Math.ceil(Math.pow(2, exponent/2));
        console.log(
            "trying thumnail size of ",
            float_size,
            " => ",
            rounded_value
        );
        return rounded_value;
    }

    $: thm_size_store.set(nice_thumbnail_size(cols, gallery_width));

    onMount(() => {
        //num_visible = 1
    });

    ///////////////////////////////////////////////////////////////////////////////
    // Organize the images into lists-of-lists for a nicer column-oriented output
    function organize_images_into_columns(
        imgs: number[],
        cols: number,
        num_visible_imgs: number
    ) {
        const cols_used = results.details? 1 : cols;
        let ic: number[][] = [];
        ic = [...Array(cols)].map((_, i) => []);
        for (const [idx, img] of imgs.entries()) {
            ic[idx % cols_used].push(img);
            if (idx > num_visible_imgs) {
                break;
            }
        }
        return ic;
    }

    function col_footers() {
        const e: NodeListOf<HTMLDivElement> =
            document.querySelectorAll("div.column_footer");
        return e;
    }

    async function update_observers(col_data: number[][]) {
        if (!observer) return;
        const cf = col_footers();
        observer.disconnect();
        cf.forEach((f) => {
            observer?.observe(f);
        });
        // console.log("added ", cf.length, " observers");
    }

    $: img_cols = organize_images_into_columns(imgs, cols, num_visible);
    $: setTimeout(() => {
        update_observers(img_cols);
    }, 100);
    $: attempt_reducing_num_visible_images(cols);
    $: details_id = results.details?.img_data.img_id

    ///////////////////////////////////////////////////////////////////////////////
    // Observe if more images are needed
    let visibility_from_observers = 0;

    function attempt_reducing_num_visible_images(c: number) {
        // TODO - get the old code
        num_visible = c * 2;
    }

    function get_incomplete_images() {
        return Array.from(document.images).filter((img) => !img.complete);
    }
    function get_promise_for_all_loading_images() {
        return Promise.all(
            get_incomplete_images().map(
                (img) =>
                    new Promise((resolve) => {
                        img.onload = img.onerror = resolve;
                    })
            )
        );
    }

    function debug_log(s: string) {
        // to debug loading of images, uncomment the following
        //console.log(s)
    }

    let already_trying_to_add_images = false;
    async function try_adding_images() {
        if (already_trying_to_add_images) {
            debug_log("try_adding_images: not adding because already_trying_to_add_images");
            return;
        }
        if (num_visible > num_available) {
            debug_log("try_adding_images: not adding because no more available");
            return;
        }
        already_trying_to_add_images = true;
        debug_log("try_adding_images: will try to add some after waiting")

        await get_promise_for_all_loading_images();
        debug_log("try_adding_images: waited, checking footers")

        if (is_any_footer_visible()) {
            debug_log("try_adding_images: footer is visible, adding images")
            num_visible += 24;
            await tick; // hopefully they get added to the dom here
            setTimeout(() => {
                // throttle loading wikipedia images about 10/second
                try_adding_images();
            }, 100);
        } else {
            debug_log("try_adding_images: no footer is visible, not adding images")
        }
        already_trying_to_add_images = false;
    }

    function is_any_footer_visible() {
        const divElements = col_footers();
        const v: boolean = Array.from(divElements).some(
            (element: HTMLDivElement) => {
                const rect: DOMRect = element.getBoundingClientRect();
                const visible =
                    rect.top < window.innerHeight && rect.bottom >= 0;
                return visible;
            }
        );
        return v;
    }
    function observer_callback(entries: any[]) {
        let visibility = 0;
        entries.forEach(function (item) {
            visibility += item.intersectionRatio;
            //item.target.textContent = item.intersectionRatio;
        });
        visibility_from_observers = visibility;
        let visibility_of_column_footers = is_any_footer_visible();
        if (visibility_from_observers || visibility_of_column_footers) {
            try_adding_images();
        }
    }

    if (browser) {
        let observer_options = {
            root: null,
            rootMargin: "0px",
            threshold: [0, 0.25, 0.5, 0.75, 1],
        };
        observer = new IntersectionObserver(
            observer_callback,
            observer_options
        );
        onMount(() => {});
    }
    //console.log(img_cols);
    /*
        [&>*]:bg-gray-300
        https://flaviocopes.com/apply-a-style-to-a-children-with-tailwind/
        https://github.com/tailwindlabs/tailwindcss/pull/8299
        https://tailwindcss.com/docs/hover-focus-and-other-states#using-arbitrary-variants
    */
</script>

<div
    data-sveltekit-preload-data="tap"
    id="grid"
    class="grid iei_result_grid"
    style="{gridstyle};"
    bind:this={result_grid_element}
    bind:clientWidth={gallery_width}
>
    {#if imgs}
        {#each img_cols as c}
            <div
                class="iei_result_col [&>*]:rounded-lg [&>*]:border-2 [&>*]:border-black [&>*]:overflow-clip "
            >
                {#each c as i}
                    <ResultImg img_id={i} {q} selected={i == details_id}/>
                {/each}
                {#if c.length > 0}
                <div
                    class="column_footer text-gray-700 h-[50vh]"
                    style="border:0px"
                >
                    ...
                </div>
                {/if}
            </div>
        {/each}
    {/if}
</div>

<slot>cool</slot>
