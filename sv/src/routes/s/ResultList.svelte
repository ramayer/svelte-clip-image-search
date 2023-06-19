<script lang="ts">

    import ResultImg from './ResultImg.svelte';
    export let results: { q: string | null; ids: number[] } | null;
    export let cols = 4;

    let imgs: number[] = [];
    
    $: num_available = results ? results["ids"].length : 0;
    $: imgs = results ? results["ids"] : [];
    $: gridstyle = `grid-template-columns: ${"1fr ".repeat(cols)}`;
    $: console.log("ResultList.svetle imgs", imgs);
    $: console.log("ResultList.svetle results", results && results["ids"]);

    // Organize the images into lists-of-lists for a nicer column-oriented output
    function organize_images_into_columns(imgs: number[], 
                                          cols: number, 
                                          num_visible_imgs: number) {
        let ic: number[][] = [];
        ic = [...Array(cols)].map((_, i) => []);
        for (const [idx, img] of imgs.entries()) {
            ic[idx % cols].push(imgs[0]);
            if (idx > num_visible_imgs) {
                break;
            }
        }
        return ic;
    }
    $: img_cols = organize_images_into_columns(imgs, cols, 20)

    console.log();
</script>

Hello ResultList

<div class="grid" style="{gridstyle};">
    {#if imgs}
        {#each imgs as r}
            <ResultImg img_id={String(r)}></ResultImg>
        {/each}
    {/if}
</div>

<slot>cool</slot>
