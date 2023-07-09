<script lang="ts">
    export let img_id: number;
    export let q: string;
    export let selected: boolean = false;

    import { onMount, tick } from "svelte";
    import { browser } from "$app/environment"; // for infinite scroll
    import {
        preview_store,
        cols_store,
        thm_size_store,
    } from "./stores.js";

    let cols = 7;
    let d_img = 0;
    let p_img = 0;
    let thm_size = 240;
    preview_store.subscribe((x) => (p_img = x));
    thm_size_store.subscribe((x) => (thm_size = x));
    cols_store.subscribe((x) => (cols = x));

    import { page } from "$app/stores";

    let isMobile =
        browser && /iPhone|iPad|iPod|Android/i.test(window.navigator.userAgent);

    function make_link(iid: number) {
        let base_url = "?";
        let new_q = q || "";
        let params = new URLSearchParams({
            q: new_q,
            d: "" + img_id,
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

<div id="i{img_id}" class="i {selected ? 'selected' : ''}">
    <a
        href={make_link(img_id)}
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
        <img id={"" + img_id} alt={"" + img_id} src="/t/{img_id}?w={thm_size}" />
    </a>
</div>

<style>
    .i {
        border: 2px solid black;
    }
    .selected {
        border: 2px solid yellow;
    }
</style>
