<script lang="ts">
  import { preview_store, detail_store, thm_size_store } from "./stores.js";
  import { fade } from "svelte/transition";
  import { browser } from "$app/environment"; // for infinite scroll

  let p_img = 0;
  let d_img = 0;
  let thm_size = 60;
  preview_store.subscribe((x) => (p_img = x));
  detail_store.subscribe((x) => (d_img = x));
  thm_size_store.subscribe((x) => (thm_size = x));

  let f_url: string | null = null; // full sized thumbnail ready
  let b_url: string | null = null; // big thumbnail
  let s_url: string | null = null; // small thumbnail
  
  $: b_url = "/t/" + p_img;
  $: s_url = "/t/" + p_img + "?w=" + thm_size;

  // https://svelte.dev/examples/deferred-transitions
  // will set f_url to b_url when b_url has pre-loaded

  let image_preloader = browser ? new Image() : null;
  const preload_image = (img_url: string) => {
    if (!image_preloader) return;
    f_url = null;
    image_preloader.onload = () => {
      f_url = img_url;
    };
    image_preloader.src = img_url;
  };

  $: b_url && preload_image(b_url)


</script>

{#if p_img && !d_img}
  <div
    class="preview_container fixed rounded-2xl bottom-1 right-1 h-[50vh] bg-black p-4"
  >
    <div class="overlay_container">
      <div class="overlay overlay-1">
        <img class="overlay-image" src={s_url} alt="small" />
      </div>
      {#if f_url}
      <div class="overlay overlay-2" in:fade={{ duration: 300 }}>
        <img            
        class="overlay-image" src={b_url} alt="large" />
      </div>
      {/if}
    </div>
  </div>
{/if}

<style>
  .preview_container {
    border: 3px solid #446;
    position: fixed;
    z-index: 99;
    display: flex;
  }
  .overlay_container {
    position: relative;
    width: 50vw;
    height: 100%;
  }

  .overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
  }

  .overlay-1 {
    background-color: rgba(50, 50, 150, 0.5);
    opacity: 0.9;
  }

  .overlay-2 {
    background-color: rgba(0, 0, 0, 1);
  }

  .overlay-image {
    width: 100%;
    height: 100%;
    object-fit: contain;
  }
</style>
