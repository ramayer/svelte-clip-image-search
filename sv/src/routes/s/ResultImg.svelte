<script lang="ts">
    export let img_id:string;

    import { onMount, tick } from "svelte";

    import { selected_img, selected_state } from './stores.js';
    async function handle_interaction(r:string) {

        selected_img.set('');
        await tick()
		selected_img.set(r);
        selected_state.update(n => n + 1);
        return true;
    }

</script>

<div on:mouseenter={(e) => handle_interaction(img_id)}
    on:keydown={(e) => handle_interaction(img_id)}
    on:click={(e) => handle_interaction(img_id)}
    >
    <img alt={"" + img_id} src="/t/{img_id}" />
</div>
