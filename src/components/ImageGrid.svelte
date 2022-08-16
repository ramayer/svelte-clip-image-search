<script>
	import {onMount} from 'svelte';
 
  // Based on
  // https://github.com/BerkinAKKAYA/svelte-image-gallery

	export let imgs;
	export let base_url;

  //let num_imgs = 4;
  //let max_imgs = 20;
  let num_visible_imgs = 4;
  let images_available = 0;

  let window_scrollY     = 0;
  let window_innerHeight = 0;
  let window_outerHeight = 0;

  $: num_visible_imgs = imgs && 4

  // Wait for the images on top of the gallery to load before the ones further down.
  function wait_for_images_to_load(f){
    Promise.all(
      Array.from(document.images)
		    .filter(img => !img.complete)
		    .map(img => new Promise(resolve => { img.onload = img.onerror = resolve; }))
    ).then(() => { f() });
  }
  // function increase_limit(upto){
  //   num_imgs += 3;
  //   num_visible_imgs += 3;
  //   if (num_imgs < upto) {
  //     setTimeout( () => 
  //       wait_for_images_to_load(()=>{increase_limit(upto)})
  //       ,500
  //     )
  //   }
  // }

  // nicer scroll

  let scroll_element = null;
  let scroll_element_visibility = 0;
  function check_if_more_images_needed(entries){
    const first = entries[0];
    scroll_element_visibility = first.intersectionRatio;
    add_images_if_scroll_visible()
  }
  let intersection_observer  = null;
  
  function add_images_if_scroll_visible() {
    if (scroll_element_visibility > 0 && num_visible_imgs < images_available){
      console.log("need to add images")
      num_visible_imgs = num_visible_imgs + 12;
      setTimeout( () => 
        wait_for_images_to_load(()=>{add_images_if_scroll_visible()})
        ,100
      )
    } else {
      console.log("no need to add images: "+ 
        scroll_element_visibility + " " + 
        num_visible_imgs + " < " + images_available);
    }
  }

  onMount(() => {
    console.log('imagegrid onMount')
    console.log("scroll element = "+scroll_element)
    const observer = new IntersectionObserver(check_if_more_images_needed)
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
      $: num_visible_imgs = 2 * est_imgs;
    }
  }

  $: desired_size && attempt_reducing_num_visible_imgs()
  $: num_visible_imgs && process_images();
  $: galleryStyle = `grid-template-columns: repeat(${columnCount}, 1fr); --gap: ${gap}px`;
  $: images_available && add_images_if_scroll_visible();

  let num_cols = 3;
  let img_cols =[]
  async function process_images(imgs2) {
    let cols = [];
    let img_array = await imgs;
    images_available = img_array.length;
    cols = [...Array(columnCount)].map((_, i) => []);
    for (const [idx, img] of img_array.entries()) {
      cols[idx%columnCount].push(img[0])
      if (idx > num_visible_imgs) {break}
    }
    debugtxt = cols;
    img_cols = cols;
    return(cols)
  }
  let debugtxt = 'initial'
  //$: debugtxt = process_images(imgs);
  $: process_images();

</script>

Size: <input type=range bind:value={desired_size} min=50 max=800>; scroll_element_visibility = {scroll_element_visibility}<br>

<br>
  let {window_scrollY}, {window_innerHeight}, {window_outerHeight}



<svelte:window bind:scrollY={window_scrollY} bind:innerHeight={window_innerHeight} bind:outerHeight={window_outerHeight}/>

num_visible_imgs = {num_visible_imgs}
<a href="#" on:click={add_images_if_scroll_visible}>load more</a>

<div id="gallery" bind:clientWidth={galleryWidth} style={galleryStyle}>
    {#each img_cols as img_col, idx}
    <div class="column">
    {#each img_col as img_id}
      <img
        min-height:10px
        src = "{base_url}thm/{img_id}?size={thm_size}"
        >
    {/each}
   </div>
  {/each}
</div>

<div id="summary" bind:this={scroll_element}>{num_visible_imgs}, images of {images_available}. <a href="#" on:click={add_images_if_scroll_visible}>load more</a></div>

<hr style="clear:both">

<style>
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
    }
    .img-hover:hover {
        opacity: 1;
        transform: scale(1.05);
    }
</style>
