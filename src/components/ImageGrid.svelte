<script>
	import {onMount} from 'svelte';
 
  // Based on
  // https://github.com/BerkinAKKAYA/svelte-image-gallery

	export let imgs;

  let num_imgs = 4;
  let max_imgs = 20;

  // Wait for the images on top of the gallery to load before the ones further down.

  function wait_for_images_to_load(f){
    Promise.all(
      Array.from(document.images)
		    .filter(img => !img.complete)
		    .map(img => new Promise(resolve => { img.onload = img.onerror = resolve; }))
    ).then(() => { f() });
  }

  function increase_limit(upto){
    num_imgs += 3;
    if (num_imgs < upto) {
      process_images()
      setTimeout( () => 
        wait_for_images_to_load(()=>{increase_limit(upto)})
        ,500
      )
    }
  }

  // infinite scroll
  export const infiniteScroll = ({ fetch, element }) => {
    if (element) {
      const observer = new IntersectionObserver(
        (entries) => {
          const first = entries[0];
          if (first.isIntersecting) {
            fetch();
          }
        },
        { threshold: 1 }
      );
      observer.observe(element);//Element of DOM
    }
  };
  let scroll_element = null;
  let already_done_scroll = null;
  $: {
    if (scroll_element && !already_done_scroll) {
      already_done_scroll = true;
      console.log("constructing infinite scroll")
      infiniteScroll({ fetch: ()=>{
        console.log("fetching")
        if (num_imgs < images_available)
          max_imgs = max_imgs + 20;
          increase_limit(max_imgs);
      }, element: scroll_element });
    }
  }

  // infinite scroll

  onMount(() => {
    increase_limit(20);
  });

  // set up gallery parameters

  let galleryWidth = 0;
  let columnCount = 0;
  export let gap = 1;
  export let maxColumnWidth = 200;
  export let hover = true;
  //export let loading;

  $: columnCount = parseInt(galleryWidth / maxColumnWidth) || 1;
  $: columnCount && process_images();
  $: max_imgs && process_images();
  $: galleryStyle = `grid-template-columns: repeat(${columnCount}, 1fr); --gap: ${gap}px`;

  let num_cols = 3;
  let images_available = 0;
  async function process_images() {
    let cols = [];
    let img_array = await imgs;
    images_available = img_array.length
    cols = [...Array(columnCount)].map((_, i) => []);
    for (const [idx, img] of img_array.entries()) {
      cols[idx%columnCount].push(img[0])
      if (idx > num_imgs) {break}
    }
    debugtxt = cols;
    return(cols)
  }
  let debugtxt = 'initial'
  //$: debugtxt = process_images(imgs);
  $: process_images(imgs);
</script>

{debugtxt}
{#await debugtxt}
  loading...
{:then img_cols}
  <div id="gallery" bind:clientWidth={galleryWidth} style={galleryStyle}>
    {#each img_cols as img_col, idx}
    <div class="column">
    {#each img_col as img_id}
      <img
        min-height:10px
        src="http://image-search.0ape.com/thm/{img_id}?size=100"
        loading="lazy"><br>
    {/each}
   </div>
  {/each}
  </div>
{:catch error}
	<p style="color: red">{error.message}</p>
{/await}
<div id="summary" bind:this={scroll_element}>{num_imgs} vs {max_imgs} images of {images_available}</div>

<hr style="clear:both">

<style>
    #slotHolder {
        display: none;
    }
    #gallery {
        width: 100%;
        display: grid;
        gap: var(--gap);
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
