<script lang="ts">
    export let img_id:string;

    import { onMount, tick } from "svelte";

    import { selected_img, selected_state } from './stores.js';

    import { page } from "$app/stores";
    let q = $page.url.searchParams.get("q");

    function make_link(new_idx: string) {
        let base_url = "?";
        let new_q = q || '';
        let params = new URLSearchParams({
            q: new_q,
            d: ""+img_id,
        });
        return base_url + params;
    }

    async function handle_interaction(r:string) {
        console.log("hi")
        selected_img.set('');
        await tick()
		selected_img.set(r);
        return true;
    }

    async function handle_click(r:string) {
        selected_img.set('');
        await tick()
        selected_img.set(r);
        selected_state.update(n => n + 1);
        return true;
    }

</script>

<div
on:mouseenter={(e) => handle_interaction(img_id)}
    on:keydown={(e) => handle_interaction(img_id)}
    on:click={(e) => handle_click(img_id)}
    >
    <a href="{make_link(img_id)}">
        <img alt={"" + img_id} src="/t/{img_id}" />
    </a>
</div>
