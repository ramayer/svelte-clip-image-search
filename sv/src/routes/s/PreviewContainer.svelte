<script lang="ts">
  import Preview from "./Preview.svelte";
  import { preview_store, thm_size_store } from "./stores.js";
	import mouseposition from './mouseposition';
  import { browser } from "$app/environment"; // for infinite scroll

  // https://svelte.dev/docs/svelte-motion
  import { tweened } from 'svelte/motion';
  import {  cubicInOut, sineInOut } from 'svelte/easing';
  const tweened_offset = tweened(1, {
    duration: 400,
    easing:sineInOut
  });

  const tweened_bottom_offset = tweened(1, {
    duration: 400,
    easing:sineInOut
  });

  let target_x=-1;
  let target_y=-1;

  function move_out_of_the_way(mp: { x: any; y: any; }) {
     let new_target_x = ($mouseposition.x > inner_width/2) ? 0 : 67;
     if (target_x != new_target_x) {
       $tweened_offset = new_target_x;
       target_x = new_target_x;
     }
  }

  //$: $tweened_offset = ($mouseposition.x > inner_width/2) ? 0 : 67;
  $: move_out_of_the_way($mouseposition)

  let leftoffsetn = 5
  let leftoffsetstr = "5vw"
  let p_img = 0;
  let thm_size = 60;
  preview_store.subscribe((x) => (p_img = x));
  thm_size_store.subscribe((x) => (thm_size = x));
  let inner_width = 0;
  
  let b_url: string = "/t/0";
  let s_url: string = "/t/0";

  $: b_url = "/t/" + p_img;
  $: s_url = "/t/" + p_img + "?w=" + thm_size;

  // set up a timer to preload up to one full image per second.
  let full_image_preloader = browser ? new Image() : undefined;
  let image_to_preload : string | undefined = undefined;
  $: image_to_preload = "/i/" + p_img;
    
  if (browser && full_image_preloader) {
    setInterval(()=>{
      if (image_to_preload && full_image_preloader) {
        full_image_preloader.src = image_to_preload
        image_to_preload = undefined
      }
    },1000)
  }
  

  $: leftoffsetstr = $tweened_offset + "vw"
  $: bottomoffsetstr = $tweened_bottom_offset + "vh"
</script>

<svelte:window bind:innerWidth={inner_width} />

{#if p_img}
  <div
    class="preview_container fixed rounded-2xl bottom-1 h-[33vh] bg-black p-2"
    style:--leftoffsetstr={leftoffsetstr}
    style:--bottomoffsetstr={bottomoffsetstr}
  >
    <Preview {s_url} {b_url} img_id={p_img}/>
  </div>
{/if}

<style>
  .preview_container {
    border: 3px solid #446;
    position: fixed;
    z-index: 99;
    display: flex;
    width: 32vw;
    left: var(--leftoffsetstr);
    transition: transform 2s;
  }


  /* https://svelte.dev/tutorial/svelte-body */
</style>
