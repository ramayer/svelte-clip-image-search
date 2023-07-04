<script lang="ts">
  import { fade } from "svelte/transition";
  import { browser } from "$app/environment"; // for infinite scroll

  export let b_url: string = "/t/0";
  export let s_url: string = "/t/0?w=60";
  export let href: string|null = null;
  let f_url: string | null = null;

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

  $: b_url && preload_image(b_url);
</script>

<div class="overlay_container">
  <div class="overlay overlay-1">
    <a href={href}>
    <img class="overlay-image" src={s_url} alt="small" />
    </a>
  </div>
  {#if f_url}
    <div class="overlay overlay-2" in:fade={{ duration: 300 }}>
      <a href={href}>
        <img class="overlay-image" src={f_url} alt="large" />
        </a>
    </div>
  {/if}
</div>

<style>
  .overlay_container {
    position: relative;
    width: 100%;
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
    background-color: rgba(50, 50, 70, 0.5);
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
