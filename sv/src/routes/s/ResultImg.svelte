<script lang="ts">
    export let img_id:string;

    import { selected_img, selected_state } from './stores.js';
    function handle_interaction(r:string) {
		selected_state.update(n => n + 1);
        selected_img.set(r);
        return true;
    }

</script>

<div on:mouseenter={(e) => handle_interaction(img_id)}
    on:keydown={(e) => handle_interaction(img_id)}
    on:click={(e) => handle_interaction(img_id)}
    >
    <img alt={"" + img_id} src="/t/{img_id}" />
</div>
