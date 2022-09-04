<script lang="ts">
  import { onMount } from "svelte";
  import { tick } from "svelte";
  import { loop_guard } from "svelte/internal";

  // array of images
  export let imgs: number[][] = [];
  export let base_url: string;
  export let search_query: string;

  let num_visible_imgs = 4;
  let images_available = 0;

  let window_scrollY = 0;
  let window_innerHeight = 0;
  let window_outerHeight = 0;
  let gallery_div;
  let preview_id = null;
  let preview_class = "right";
  let preview_class2 = "top";

  // Throttle image loading.  
  //   If using Wikimedia as an image source, anything faster than 12 in parallel, and 100ms between
  // batches will cause Wikimedia to return HTTP 429 Too Many Requests errors.
  
  let num_parallel_image_loads = 12;
  let thumnail_loading_throttle = 100;

  $: num_visible_imgs = imgs && 4;

  function mlt_url(s) {
    let data = { image_id: s };
    return JSON.stringify(data);
  }
  function search_for(q) {
    let eu = "?q=" + encodeURIComponent(q);
    return eu;
  }

  function mousedover(pid, x, y) {
    preview_id = pid;
    preview_class = x < galleryWidth / 2 ? "right" : "left";
    preview_class2 = y < innerHeight / 2 ? "bottom" : "top";
  }

  // Wait for the images on top of the gallery to load before the ones further down.
  function wait_for_images_to_load(f: () => void) {
    Promise.all(
      Array.from(document.images)
        .filter((img) => !img.complete)
        .map(
          (img) =>
            new Promise((resolve) => {
              img.onload = img.onerror = resolve;
            })
        )
    ).then(() => {
      f();
    });
  }

  let already_waiting_for_images = false;

  function add_images_if_scroll_visible() {
    if (already_waiting_for_images) {
      console.log("already waiting for images to load");
      return
    }
    if (scroll_element_visibility > 0 && num_visible_imgs < images_available) {
      console.log("adding images because num_visible_imgs = " + num_visible_imgs);
      already_waiting_for_images = true;
      setTimeout(
        () =>
          wait_for_images_to_load(() => {
            console.log("wait for images to load returned, num_visible="+num_visible_imgs)
            num_visible_imgs = num_visible_imgs + num_parallel_image_loads;
            already_waiting_for_images = false;
            add_images_if_scroll_visible();
          }),
        thumnail_loading_throttle
      );
    } else {
      console.log("not adding images because"+
                  " scroll_element_visibility = "+ scroll_element_visibility +
                  ", num_visible_imgs = " + num_visible_imgs + 
                  ", and images_available " + images_available)
    }
  }

  let scroll_element: Element | null = null;
  let scroll_element_visibility = 1;
  function check_if_more_images_needed(entries: any[]) {
    let visibility = 0;
    entries.forEach(function (item) {
      visibility += item.intersectionRatio;
    });
    scroll_element_visibility = visibility;
    console.log("check_if_more_images_needed calling add_images_if_scroll_visible")
    add_images_if_scroll_visible();
  }

  let intersection_observer = null;
  const observer = new IntersectionObserver(check_if_more_images_needed);

  onMount(() => {
    if (scroll_element) observer.observe(scroll_element);
    add_images_if_scroll_visible();
    //setTimeout(add_images_if_scroll_visible, 100);
  });

  // set up gallery parameters
  // let columnCount = 0;

  let galleryWidth = 0;
  let desired_size = 250;
  let preview_width = 10;
  export let gap = 6;
  export let hover = true;
  //export let loading;

  $: columnCount = Math.floor(galleryWidth / desired_size) || 1;
  $: thm_size = Math.floor(desired_size / 100 + 1) * 100 || 100;
  $: columnCount && process_images();
  $: preview_width = galleryWidth / columnCount* Math.floor(img_cols.length/2+1)
  $: preview_cols  = Math.floor(img_cols.length/2+1)
  function attempt_reducing_num_visible_imgs() {
    let est_imgs =
      (window_innerHeight * galleryWidth) / (desired_size * desired_size);
    if (num_visible_imgs > 2 * est_imgs) {
      num_visible_imgs = 2 * est_imgs;
    }
  }

  $: desired_size && attempt_reducing_num_visible_imgs();
  $: num_visible_imgs && process_images();
  $: galleryStyle = `grid-template-columns: repeat(${columnCount}, 1fr); --gap: ${gap}px`;
  $: images_available && add_images_if_scroll_visible();

  let num_cols = 3;
  let img_cols: any[] = [];
  async function process_images() {
    if (!columnCount) return;
    let cols: number[][] = [];
    let img_array = imgs;
    images_available = img_array.length;
    cols = [...Array(columnCount)].map((_, i) => []);
    for (const [idx, img] of img_array.entries()) {
      cols[idx % columnCount].push(img[0]);
      if (idx > num_visible_imgs) {
        break;
      }
    }
    debugtxt = JSON.stringify(cols);
    img_cols = cols;

    await tick(); // wait til the dom was updated.

    observer.disconnect();
    observer.observe(scroll_element);
    if (gallery_div) {
      let column_footers = gallery_div.querySelectorAll(".column_footer");
      column_footers.forEach((f) => {
        observer.observe(f);
      });
    }
    return cols;
  }
  let debugtxt = "initial";
  //$: debugtxt = process_images(imgs);
  $: process_images();
</script>

<svelte:window
  bind:scrollY={window_scrollY}
  bind:innerHeight={window_innerHeight}
  bind:outerHeight={window_outerHeight}
/>

Size: <input type="range" bind:value={desired_size} min="50" max="800" />

<!--
 scroll_element_visibility = {scroll_element_visibility}<br>
<br>{window_scrollY}, {window_innerHeight}, {window_outerHeight}
num_visible_imgs = {num_visible_imgs}
<a href="#1" on:click={add_images_if_scroll_visible}>load more</a>
img_cols = {img_cols.length} thm_size = {thm_size}
-->

<div class="gallery_container">
{#if img_cols.length > 4}
  <div class="preview" style="width:{preview_width}px; height:{innerHeight/2}px">
    {#if preview_id}
      <img src="{base_url}thm/{preview_id}?size=1024" style="max-width:100%; max-height:100%" />
    {:else}
      Nothing to preview
    {/if}
  </div>
{/if}

<div
  id="gallery"
  bind:this={gallery_div}
  bind:clientWidth={galleryWidth}
  style={galleryStyle}
>
  {#each img_cols as img_col, idx}
    <div class="column">
      {#if idx >= img_cols.length - preview_cols && img_cols.length > 4}
      <div class="spacer" style="height:{innerHeight/2}px">{idx}, </div>
      {/if}
      {#each img_col as img_id}
        <div
          class="image_container"
          on:mouseenter={(e) => mousedover(img_id, e.clientX, e.clientY)}
        >
          <div class="image_overlay">
            {#if desired_size > 150}
              <a href={search_for(mlt_url(img_id))}
                ><nobr>more like this</nobr></a
              >
            {:else}
              <a href={search_for(mlt_url(img_id))}><nobr>mlt</nobr></a>
            {/if}
            <nobr>
              <a href={search_for(search_query + " +" + mlt_url(img_id))}>▲</a>
              <a href={search_for(search_query + " -" + mlt_url(img_id))}>▼</a>
            </nobr>
          </div>
          <a href="{base_url}img/{img_id}" target="_blank">
            <img
              class="img-hover"
              style="min-height:10px"
              src="{base_url}thm/{img_id}?size={thm_size}"
              alt={img_id}
            />
          </a>
        </div>
      {/each}
      <div class="column_footer">...</div>
    </div>
  {/each}
</div>
</div>

<div id="summary" bind:this={scroll_element}>
  {num_visible_imgs}, images of {images_available}.
  <a href="#2" on:click={add_images_if_scroll_visible}>load more</a>
</div>


<hr style="clear:both" />

<style>
  .column_footer {
    border: 1px solid #222;
    color: #888;
  }
  #slotHolder {
    display: none;
  }
  #gallery {
    width: 100%;
    display: grid;
    gap: var(--gap);
    background: #000;
  }

  #gallery .column {
    display: flex;
    flex-direction: column;
  }
  #gallery .column * {
    width: 100%;
    margin-top: var(--gap);
  }
  #gallery .column *:nth-child(1) {
    margin-top: 0;
  }
  .img-hover {
    opacity: 0.9;
    transition: all 0.2s;
    z-index: 1;
  }
  .img-hover:hover {
    position: relative;
    opacity: 1;
    z-index: 10;
    transform: scale(1.15);
    /* border: 5px inset #666; */
    border: 10px solid black;
  }
  .image_container {
    position: relative;
  }
  .image_overlay {
    position: absolute;
    top: 2px;
    left: 2px;
    padding: 4px;
    display: none;
    width: 80%;
    z-index: 20;
  }
  .image_container:hover td {
    color: var(--brighttext);
  }
  .image_container:hover .image_overlay {
    display: block;
    background: blue;
    background-color: #000;
  }
  .image_container:hover a {
    color: #77f;
    text-decoration: none;
  }
  .image_container:hover a:hover {
    color: #eef;
  }

  .gallery_container {
    position: relative;
  }
  .preview {
    color: #fff;
    border: 1px solid red;
    position: fixed;
    background-color: #000;
    /* border: 2px outset #ccc; */
    border: 2px solid #f00; 
    top:30px;
    right:0px;
    z-index:99;
    display:flex;
  }
  
  .preview img {
    display: block;
    margin: auto;
    max-width: 100%;
    max-height: 100%;
  }
</style>
