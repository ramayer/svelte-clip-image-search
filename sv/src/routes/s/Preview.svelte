<script lang="ts">
  import { fade } from "svelte/transition";
  import { browser } from "$app/environment"; // for infinite scroll
  import { cols_store } from "./stores";
    import { goto } from "$app/navigation";

  export let b_url: string = "/t/0";
  export let s_url: string = "/t/0?w=60";
  export let detail_href: string | undefined = undefined;
  export let img_id: number;
  export let width = 0;
  export let height = 0;
  export let overlay_data: {
    x: number;
    y: number;
    w: number;
    h: number;
    c: string;
  }[] = [];

  let offset_width: number = 0;
  let offset_height: number = 0;

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
    <a href={detail_href}>
      <img class="overlay-image" src={s_url} alt="small" />
    </a>
  </div>
  {#if f_url}
    <div class="overlay overlay-2" in:fade={{ duration: 100 }}>
      <a href={detail_href}>
        <img class="overlay-image" src={f_url} alt="large" />
      </a>
    </div>
  {/if}
  {#if width & height}
    <div class="overlay c0">
      <div style="aspect-ratio: {width}/{height};" class="c1">
        <!-- https://stackoverflow.com/questions/31869087/how-to-set-two-directions-for-flex-box-css -->
        <div
          style="aspect-ratio: {width}/{height};"
          class="c2"
        >
          {#if overlay_data}
            {#each overlay_data as o,idx}
              <a href="/s?q=face:{img_id}.{idx}"><div
                class="c3"
                style="top:{o.y}%; left:{o.x}%; height:{o.h}%; width:{o.w}%; "
              >
              </div></a>  
            {/each}
          {/if}
        </div>
      </div>
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
    background-color: rgb(15 23 42 / var(--tw-bg-opacity));
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

  .c0 { /* a flex box the size of the container of arbitrary space */
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    pointer-events: none;
  }
  .c1 {/* a flex box constraining the height, but potentially narrower width */
    max-width: 100%;
    height: 100%;
    display: flex;
    flex-shrink: 1;
    flex-direction: column;
    justify-content: center;
    pointer-events: none;
  }
  .c2 { /* a flex box constraining the width, but potentially shorter height */
    max-height: 100%;
    width: 100%;
    flex-shrink: 1;
    flex-direction: row;
    flex-grow: 0;
    position: relative;
    pointer-events: none;
  }
  .c3 {
    pointer-events: auto;
    position: absolute;
    border: 1px solid  rgba(0,0,0, 0.75);   
    outline: 1px solid rgba(255, 255, 127, 0.75);
  }
  .c3:hover {
    outline: 4px solid rgba(255,255, 0, 1);
    background-color:rgba(255, 255, 127, 0.5);
  }
</style>
