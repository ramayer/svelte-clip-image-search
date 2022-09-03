<script lang="ts">

  import {onMount} from 'svelte';
  import {tick} from "svelte";

  // array of images
  export let imgs  : number[][] = [];
  export let base_url : string;

  let num_visible_imgs = 4;
  let images_available = 0;

  let window_scrollY     = 0;
  let window_innerHeight = 0;
  let window_outerHeight = 0;
  let gallery_div;

  $: num_visible_imgs = imgs && 4

  function mlt_url(s) {
      let data = {"image_id":s}
      return(JSON.stringify(data))
  }

  // Wait for the images on top of the gallery to load before the ones further down.
  function wait_for_images_to_load(f: ()=>void){
    Promise.all(
      Array.from(document.images)
		    .filter(img => !img.complete)
		    .map(img => new Promise(resolve => { img.onload = img.onerror = resolve; }))
    ).then(() => { f() });
  }

  function add_images_if_scroll_visible() {
    if (scroll_element_visibility > 0 && num_visible_imgs < images_available){
      setTimeout( () => 
        wait_for_images_to_load(()=>{
          num_visible_imgs = num_visible_imgs + 12;
          add_images_if_scroll_visible()
        }),100
      )
    }
  }

  let scroll_element: Element|null = null;
  let scroll_element_visibility = 1;
  function check_if_more_images_needed(entries: any[]){
    let visibility = 0;
    entries.forEach(function(item) {
      visibility += item.intersectionRatio;
    })
    scroll_element_visibility = visibility;
    add_images_if_scroll_visible()
  }

  let intersection_observer  = null;
  const observer = new IntersectionObserver(check_if_more_images_needed)

  
  onMount(() => {
    if (scroll_element)
      observer.observe(scroll_element);
    add_images_if_scroll_visible();
    setTimeout( add_images_if_scroll_visible, 100)
  });

  // set up gallery parameters
  // let columnCount = 0;

  let galleryWidth = 0;
  let desired_size = 250;

  export let gap = 6;
  export let hover = true;
  //export let loading;

  $: columnCount = Math.floor(galleryWidth / desired_size) || 1;
  $: thm_size = Math.floor(desired_size / 100 + 1)*100 || 100;
  $: columnCount && process_images();

  function attempt_reducing_num_visible_imgs() {
    let est_imgs = (window_innerHeight * galleryWidth) / (desired_size*desired_size)
    if (num_visible_imgs > 2 * est_imgs) {
      num_visible_imgs = 2 * est_imgs;
    }
  }

  $: desired_size && attempt_reducing_num_visible_imgs()
  $: num_visible_imgs && process_images();
  $: galleryStyle = `grid-template-columns: repeat(${columnCount}, 1fr); --gap: ${gap}px`;
  $: images_available && add_images_if_scroll_visible();

  let num_cols = 3;
  let img_cols: any[] =[]
  async function process_images() {
    if (!columnCount) return
    let cols:number[][] = [];
    let img_array = imgs;
    images_available = img_array.length;
    cols = [...Array(columnCount)].map((_, i) => []);
    for (const [idx, img] of img_array.entries()) {
      cols[idx%columnCount].push(img[0])
      if (idx > num_visible_imgs) {break}
    }
    debugtxt = JSON.stringify(cols);
    img_cols = cols;

    await tick(); // wait til the dom was updated.

    observer.disconnect()
    observer.observe(scroll_element);
    if (gallery_div) {
      let column_footers = gallery_div.querySelectorAll('.column_footer')
      column_footers.forEach((f)=>{
        observer.observe(f);
      });
    }
    return(cols)
  }
  let debugtxt = 'initial'
  //$: debugtxt = process_images(imgs);
  $: process_images();

</script>

Size: <input type=range bind:value={desired_size} min=50 max=800>; scroll_element_visibility = {scroll_element_visibility}<br>

<br>{window_scrollY}, {window_innerHeight}, {window_outerHeight}

<svelte:window bind:scrollY={window_scrollY} bind:innerHeight={window_innerHeight} bind:outerHeight={window_outerHeight}/>

num_visible_imgs = {num_visible_imgs}
<a href="#1" on:click={add_images_if_scroll_visible}>load more</a>
img_cols = {img_cols.length} thm_size = {thm_size}


<div id="gallery" bind:this={gallery_div} bind:clientWidth={galleryWidth} style={galleryStyle}>
    {#each img_cols as img_col, idx}
    <div class="column">
    {#each img_col as img_id}
     <div class='image_container'>
	<div class="image_overlay">
	  <a href="?q={mlt_url(img_id)}" ><nobr>more like this</nobr></a>
	  <a href='#' ><nobr> + </nobr></a>
	  <a href='#' ><nobr> - </nobr></a>
	</div>
	<a href="{base_url}img/{img_id}?size={thm_size}" target=_blank>
      <img
        class='img-hover'
        style='min-height:10px'
        src = "{base_url}thm/{img_id}?size={thm_size}"
        alt = "{img_id}"
        >
        </a>
      </div>
    {/each}
    <div class="column_footer"> </div>
   </div>
  {/each}
</div>

<div id="summary" bind:this={scroll_element}>{num_visible_imgs}, images of {images_available}. <a href="#2" on:click={add_images_if_scroll_visible}>load more</a></div>

<hr style="clear:both">

<style>
  .column_footer {
    border: 1px solid red;
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
        transform: scale(1.25);
        /* border: 5px inset #666; */
        border: 10px solid black;
    }
    .image_container { position: relative;}
    .image_overlay   { position: absolute; top: 2px;  left: 2px; padding:4px; display:none; width: 80%; z-index:20; }
    .image_container:hover td {color: var(--brighttext)}
    .image_container:hover .image_overlay {display:block;  background:blue; background-color:#000;}
    .image_container:hover a {color: #88f}


</style>
