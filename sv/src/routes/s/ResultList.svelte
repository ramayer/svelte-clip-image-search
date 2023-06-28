<script lang="ts">
    import ResultImg from "./ResultImg.svelte";
    import { browser } from "$app/environment"; // for infinite scroll
    import { onMount, tick } from "svelte";
    export let results: { q: string | null; ids: number[] } | null;
    export let cols = 4;

    let num_available = 12;
    let num_visible = 1;
    let imgs: number[] = [];

    $: num_available = results ? results["ids"].length : 0;
    $: imgs = results ? results["ids"] : [];
    $: gridstyle = `grid-template-columns: ${"1fr ".repeat(cols)}`;

    $: num_visible = results ? 1 : 1

    $: console.log("ResultList.svetle imgs", imgs);
    // $: console.log("ResultList.svetle results", results && results["ids"]);

    let observer: IntersectionObserver | null;
    let result_grid_element: Element | null = null;


    onMount(() => {
        num_visible = 1
    });



    ///////////////////////////////////////////////////////////////////////////////
    // Organize the images into lists-of-lists for a nicer column-oriented output
    function organize_images_into_columns(
        imgs: number[],
        cols: number,
        num_visible_imgs: number
    ) {
        let ic: number[][] = [];
        ic = [...Array(cols)].map((_, i) => []);
        for (const [idx, img] of imgs.entries()) {
            ic[idx % cols].push(img);
            if (idx > num_visible_imgs) {
                break;
            }
        }
        console.log("organized ",num_visible_imgs, " of ", imgs.length,  " into ", cols, " cols");
        return ic;
    }

    function col_footers() {
        const e: NodeListOf<HTMLDivElement> =
            document.querySelectorAll("div.column_footer");
        return e;
    }

    async function update_observers(col_data: number[][]) {
        if (!observer) return;
        const cf = col_footers()
        observer.disconnect();
        cf.forEach((f) => {
            observer?.observe(f);
        });
        console.log("added ", cf.length, " observers");
    }


    $: img_cols = organize_images_into_columns(imgs, cols, num_visible);
    $: setTimeout(()=>{update_observers(img_cols)},100);
    //$: attempt_reducing_num_visible_images(cols);

    ///////////////////////////////////////////////////////////////////////////////
    // Observe if more images are needed
    let visibility_from_observers = 0;

    function attempt_reducing_num_visible_images(c: number) {
        // TODO - get the old code
        num_visible = c * 2;
    }

    function get_incomplete_images() {
        return Array.from(document.images).filter((img) => !img.complete)
    }
    function get_promise_for_all_loading_images() {
        return Promise.all(
            get_incomplete_images()
                .map(
                    (img) =>
                        new Promise((resolve) => {
                            img.onload = img.onerror = resolve;
                        })
                )
        )
    }

    function wait_for_all_images_to_load(f: () => void) {
        console.log("waiting for more images to load");
        get_promise_for_all_loading_images() .then(() => {
            console.log("all images loaded");
            f();
        });
    }

    let already_trying_to_add_images = false;
    async function try_adding_images() {
        if (already_trying_to_add_images){
            console.log("try_adding_images: not adding because already_trying_to_add_images");
            return;
        }
        if (num_visible > num_available) {
            console.log("try_adding_images: not adding because no more available");
            return;
        }
        already_trying_to_add_images = true;
        console.log("try_adding_images: will try to add some after waiting")

        await get_promise_for_all_loading_images();
        console.log("try_adding_images: waited, checking footers")

        if (is_any_footer_visible()) {
            console.log("try_adding_images: footer is visible, adding images")
            num_visible += 1;
            await tick // hopefully they get added to the dom here
            setTimeout(() => { // throttle loading wikipedia images about 10/second
                try_adding_images();
            }, 100);
        } else {
            console.log("try_adding_images: no footer is visible, not adding images")
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
        onMount(() => {
        });
    }
    //console.log(img_cols);
    /*
    [&>*]:bg-gray-300
    https://flaviocopes.com/apply-a-style-to-a-children-with-tailwind/
    */
</script>

<div class="fixed bottom-20 left-1 w-50 bg-black ...">
    visibility_of_bottom = {visibility_from_observers}<br />
    num_visible = {num_visible}
</div>

<div id="grid" class="grid" style="{gridstyle};" bind:this={result_grid_element}>
    {#if imgs}
        {#each img_cols as c}
            <div
                class="[&>*]:rounded-md [&>*]:border [&>*]:border-black [&>*]:overflow-clip"
            >
                {#each c as i}
                    <ResultImg img_id={String(i)} />
                {/each}
                <div
                    class="column_footer text-gray-700 h-[50vh]"
                    style="border:0px"
                >
                    ...
                </div>
            </div>
        {/each}
    {/if}
</div>


<slot>cool</slot>
