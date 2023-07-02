<script lang="ts">
    import { preview_store, detail_store } from "./stores.js";
    let p_img = 0;
    preview_store.subscribe((x) => (p_img = x));
        let d_img = 0;
    detail_store.subscribe((x) => (d_img = x));
</script>

{#if p_img && !d_img}
<div 
class="preview fixed rounded-2xl bottom-1 right-1 h-[50vh] bg-black p-4">
        <img
        id="preview"
            alt={"" + p_img}
            class="m-auto"
            style="max-height: calc(50vh - 30px); max-width:100vw"
            src="/t/{p_img}"
        />
</div>
{/if}

<style>
.preview {
    color: #fff;
    border: 2px solid #446;
    position: fixed;
    /*background-color: #8884;*/
    /*border: 2px outset #555;*/

    /* top: 60px */
    right: 0px;
    z-index: 99;
    display: flex;
  }
  .underlay {
    background-color: #000;
  }

  .preview img {
    object-fit: contain;
    display: block;
    margin: auto;
    max-width: 100%;
    max-height: 100%;
  }
</style>
