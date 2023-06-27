<script lang="ts">
    import ResultImg from "./ResultImg.svelte";
    import { browser } from "$app/environment"; // for infinite scroll
    import { onMount, tick } from "svelte";
    export let results: { q: string | null; ids: number[] } | null;
    export let cols = 4;

    let num_available = 12;
    let num_visible = 3;

    let imgs: number[] = [];

    $: num_available = results ? results["ids"].length : 0;
    $: imgs = results ? results["ids"] : [];
    $: gridstyle = `grid-template-columns: ${"1fr ".repeat(cols)}`;

    $: console.log("ResultList.svetle imgs", imgs);
    // $: console.log("ResultList.svetle results", results && results["ids"]);

    let observer: IntersectionObserver | null;
    let result_grid_element: Element | null = null;

    ///////////////////////////////////////////////////////////////////////////////
    // Organize the images into lists-of-lists for a nicer column-oriented output
    function organize_images_into_columns(
        imgs: number[],
        cols: number,
        num_visible_imgs: number
    ) {
        console.log("organizing into ", cols, " cols with ", num_visible_imgs);
        let ic: number[][] = [];
        ic = [...Array(cols)].map((_, i) => []);
        for (const [idx, img] of imgs.entries()) {
            ic[idx % cols].push(img);
            if (idx > num_visible_imgs) {
                break;
            }
        }
        return ic;
    }

    async function update_observers(col_data: number[][]) {
        await tick();
        observer?.disconnect();
        await tick();
        if (result_summary_element) {
            //observer?.observe(result_summary_element)
        }
        let column_footers =
            result_grid_element?.querySelectorAll(".column_footer");
        let col_count = 0;
        column_footers?.forEach((f) => {
            console.log("adding another observer", f);
            observer?.observe(f);
            col_count++;
        });
        if (col_data.length != col_count) {
            console.log("unexpected column count");
        }
    }
    $: img_cols = organize_images_into_columns(imgs, cols, num_visible);
    $: attempt_reducing_num_visible_images(cols);
    $: update_observers(img_cols);
    ///////////////////////////////////////////////////////////////////////////////
    // Observe if more images are needed
    let visibility_of_column_bottoms = 0;
    let result_summary_element: Element | null = null;

    function attempt_reducing_num_visible_images(c: number) {
        // TODO - get the old code
        num_visible = c * 2;
    }

    function wait_for_all_images_to_load(f: () => void) {
        console.log("waiting for more images to load");
        Promise.all(
            Array.from(document.images)
                .filter((img) => !img.complete)
                .map(
                    (img) =>
                        new Promise((resolve) => {
                            img.onload = img.onerror = resolve;
                        })
                )
        ).then(() => {
            console.log("all images loaded");
            f();
        });
    }

    let more_images_are_loading = false;
    async function try_adding_images() {
        await tick()
        if (num_visible > num_available) {
            console.log("try_adding_images: no more available");
            return;
        }
        if (more_images_are_loading) {
            console.log("try_adding_images: already loading");
            return;
        }
        if (!visibility_of_column_bottoms) {
            console.log("try_adding_images: bottom isn't visible");
            return;
        }
        console.log("increasing num_visible from ", num_visible);
        num_visible += 1;
        more_images_are_loading = true;
        wait_for_all_images_to_load(async () => {
            await tick();
            console.log("try_adding_images: images loaded so checking again");
            more_images_are_loading = false;
            setTimeout(() => {
                try_adding_images();
            }, 100);
        });
    }

    function check_if_bottom_is_visible(entries: any[]) {
        let visibility = 0;
        entries.forEach(function (item) {
            console.log("X");
            visibility += item.intersectionRatio;
        });
        visibility_of_column_bottoms = visibility;
        if (visibility_of_column_bottoms) {
            try_adding_images();
        }
        console.log("column bottoms visibility = ", visibility);
    }

    if (browser) {
        let observer_options = {
            root: document.querySelector("#scrollArea"),
            rootMargin: "0px",
            threshold: 0.01,
        };
        observer = new IntersectionObserver(
            check_if_bottom_is_visible,
            observer_options
        );
        onMount(() => {
            if (result_summary_element && observer) {
                observer.observe(result_summary_element);
            }
        });
    }
    //console.log(img_cols);
    /*
    [&>*]:bg-gray-300
    https://flaviocopes.com/apply-a-style-to-a-children-with-tailwind/
    */
</script>

<div class="fixed bottom-20 left-1 w-50 bg-black ...">
    visibility_of_bottom = {visibility_of_column_bottoms}<br />
    num_visible = {num_visible}
</div>

<div class="grid" style="{gridstyle};" bind:this={result_grid_element}>
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
<div
    id="result_summary_element"
    class="h-[50vh]"
    bind:this={result_summary_element}
>
    result summary
</div>

<slot>cool</slot>
