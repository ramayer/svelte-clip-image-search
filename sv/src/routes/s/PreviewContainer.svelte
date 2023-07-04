<script lang="ts">
  import Preview from "./Preview.svelte";
  import { preview_store, detail_store, thm_size_store } from "./stores.js";
	import mouseposition from './mouseposition';

  // https://svelte.dev/docs/svelte-motion
  import { tweened } from 'svelte/motion';
  import { cubicOut } from 'svelte/easing';
  const size = tweened(1, {
    duration: 300,
    easing: cubicOut
  });

  $: $size = ($mouseposition.x > inner_width/2) ? 0 : 50;


  let leftoffsetn = 5
  let leftoffsetstr = "5vw"
  let p_img = 0;
  let d_img = 0;
  let thm_size = 60;
  preview_store.subscribe((x) => (p_img = x));
  detail_store.subscribe((x) => (d_img = x));
  thm_size_store.subscribe((x) => (thm_size = x));
  let inner_width = 0;
  
  let b_url: string = "/t/0";
  let s_url: string = "/t/0";

  $: b_url = "/t/" + p_img;
  $: s_url = "/t/" + p_img + "?w=" + thm_size;

  $: leftoffsetn = ($mouseposition.x > inner_width/2) ? 0 : 50;
  $: leftoffsetstr = $size + "vw"
</script>

<svelte:window bind:innerWidth={inner_width} />

{#if p_img && !d_img}
  <div
    class="preview_container fixed rounded-2xl bottom-1  h-[50vh] bg-black p-2"
    style:--leftoffsetstr={leftoffsetstr}
  >
    <Preview {s_url} {b_url} />
  </div>
{/if}

<style>
  .preview_container {
    border: 3px solid #446;
    position: fixed;
    z-index: 99;
    display: flex;
    width: 50vw;
    left: var(--leftoffsetstr);
    transition: transform 2s;
  }


  /* https://svelte.dev/tutorial/svelte-body */
</style>
