<script lang="ts">
    export let img_id: number;
    export let q: string;
    export let selected: boolean = false;
    import { fade } from "svelte/transition";

    import { onMount, tick } from "svelte";
    import { browser } from "$app/environment"; // for infinite scroll
    import { preview_store, cols_store, thm_size_store } from "./stores.js";

    let cols = 7;
    let d_img = 0;
    let p_img = 0;
    let thm_size = 240;
    preview_store.subscribe((x) => (p_img = x));
    thm_size_store.subscribe((x) => (thm_size = x));
    cols_store.subscribe((x) => (cols = x));

    import { page } from "$app/stores";

    function srchlink(new_q: string) {
        let base_url = "?";
        let params = new URLSearchParams({ q: new_q});
        return base_url + params;
    }

    let isMobile =
        browser && /iPhone|iPad|iPod|Android/i.test(window.navigator.userAgent);

    function make_link(iid: number,new_q: string) {
        let base_url = "?";
        //let new_q = q || "";
        let params = new URLSearchParams({
            q: new_q,
            d: "" + iid,
        });
        return base_url + params;
    }

    async function handle_interaction(r: number) {
        preview_store.set(0);
        await tick();
        preview_store.set(r);
        return true;
    }
</script>

<div id="i{img_id}" class="i relative {selected ? 'selected' : ''}">
    <a
        href={make_link(img_id,q)}
        on:mouseenter={(e) => handle_interaction(img_id)}
        on:mousedown={(e) => handle_interaction(img_id)}
        on:touchstart={(e) => handle_interaction(img_id)}
        data-sveltekit-noscroll
    >
        <!-- 
        Don't add a keydown event here like:
        on:keydown={(e) => handle_interaction(img_id)}
        after ctrl-click opens an image in a new tab the old tab will continue listening.
    -->
        <img
            id={"" + img_id}
            alt={"" + img_id}
            src="/t/{img_id}?w={thm_size}&h={thm_size * 3}"
        />
    </a>
    {#if img_id == p_img}
    <div in:fade={{ duration: 200 }}
     class=" to-blue-400 text-center absolute bottom-1 img_hover">
        <a href={srchlink(q+" -clip:"+img_id)} title="less like this">▼</a>
        <a href={"?q=clip:"+img_id}  title="similar images">▦</a>
        <a href={make_link(img_id,q)}  title="details">▣</a>
        <a href={srchlink(q+" +clip:"+img_id)} title="more like this">▲</a>
    </div>
    {/if}
</div>

<style>
    .i {
        border: 2px solid black;
    }
    .selected {
        border: 2px solid yellow;
    }
    .img_hover a {
        color: #8cf;
    }
    .i .img_hover {
        /* transition: all 0.5s ease-in-out; */
        background-color: rgba(0, 0, 0, 0.5);
        border: 0px solid red;
        width: 100%;
        /*
        color: transparent;
        line-height: 0;
        padding: 0;
        margin: 0;
        height: 0px;
        */
        display: none;
    }
    .i:hover .img_hover {
        display: block;
        height: auto;
        color: white;
        line-height: 1;
        display: block;
    }
</style>
