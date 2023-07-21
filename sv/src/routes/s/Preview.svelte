<script lang="ts">
  import { fade } from "svelte/transition";
  import { browser } from "$app/environment"; // for infinite scroll
  import { cols_store } from "./stores";
    import { goto } from "$app/navigation";
    import { onMount, tick } from "svelte";

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

  $: console.log("Preview ",b_url,s_url,img_id)

  onMount(() => {
        console.log("Preview onMount()",b_url,s_url,img_id);
  });

  // console.log("overlay data is ",overlay_data, " w,h=",width,height)

  let offset_width: number = 0;
  let offset_height: number = 0;

  let f_url: string | null = null;

  // https://svelte.dev/examples/deferred-transitions
  // will set f_url to b_url when b_url has pre-loaded

  let image_preloader = browser ? new Image() : null;
  const preload_image = (img_url: string) => {
    if (!image_preloader) return;
    f_url = null;
    image_preloader.onload = async () => {
      await tick
      f_url = img_url;
    };
    image_preloader.src = img_url;
  };

  $: b_url && preload_image(b_url);


  /********************* selection outline ***********/
  let myDivElement: HTMLDivElement;
  let selection_outline_enabled = true;


  let isCtrlPressed = false;
  let startCoords = { x: 0, y: 0 };
  let endCoords = { x: 0, y: 0 };
  let selectionOutlineVisible = false;
  let selectionOutlineStyle = {
      display: 'none',
      left: '0px',
      top: '0px',
      width: '10px',
      height: '10px',
    };

  function handleMouseDown(event: MouseEvent) {
    if (event.ctrlKey || event.metaKey) {
      isCtrlPressed = true;
      const boundingRect = myDivElement.getBoundingClientRect();
      startCoords = {
        x: event.clientX - boundingRect.left,
        y: event.clientY - boundingRect.top,
      };
      endCoords = { x: startCoords.x, y: startCoords.y };
      selectionOutlineVisible = true;
      selectionOutlineStyle.display = 'block';
      updateSelectionOutline();
    }
  }

  function handleMouseMove(event: MouseEvent) {
    if (isCtrlPressed) {
      const boundingRect = myDivElement.getBoundingClientRect();
      endCoords = {
        x: event.clientX - boundingRect.left,
        y: event.clientY - boundingRect.top,
      };
      updateSelectionOutline();
    }
  }

  function handleMouseUp() {
      const boundingRect = myDivElement.getBoundingClientRect();
      const x = Math.min(startCoords.x, endCoords.x);
      const y = Math.min(startCoords.y, endCoords.y);
      const width = Math.abs(endCoords.x - startCoords.x);
      const height = Math.abs(endCoords.y - startCoords.y);

      const bbox = {
        x: Math.floor(x/boundingRect.width*100), 
        y: Math.floor(y/boundingRect.height*100), 
        w: Math.floor((width)/boundingRect.width*100), 
        h: Math.floor((height)/boundingRect.height*100), 
      }
      console.log(bbox);
      if (bbox.w > 0 && bbox.h > 0) {
        let u = ('?q=clip:'+img_id+"@"+bbox.x+","+bbox.y+","+bbox.w+","+bbox.h)
        console.log("going to ",u);
        goto(u);
      }
      isCtrlPressed = false;
      selectionOutlineVisible = false;
      selectionOutlineStyle.display = 'none';
  }

  function updateSelectionOutline() {
    const x = Math.min(startCoords.x, endCoords.x);
    const y = Math.min(startCoords.y, endCoords.y);
    const width = Math.abs(endCoords.x - startCoords.x);
    const height = Math.abs(endCoords.y - startCoords.y);
    const boundingRect = myDivElement.getBoundingClientRect(); 
    selectionOutlineStyle = {
      display: 'block',
      left: x + 'px',
      top: y + 'px',
      width: width + 'px',
      height: height + 'px',
    };
  }
</script>

<div class="overlay_container">
  <div class="overlay overlay-1">
    <a href={detail_href}>
      <img class="overlay-image" src={s_url} alt="small" />
    </a>
  </div>
  {#if f_url}
    <div class="overlay overlay-2" in:fade={{ duration: 333 }}>
      <a href={detail_href}>
        <img class="overlay-image" src={f_url} alt="large" />
      </a>
    </div>
  {/if}
  {#if width && height}
    <div class="overlay c0">
      <div style="aspect-ratio: {width}/{height};" class="c1">
        <!-- https://stackoverflow.com/questions/31869087/how-to-set-two-directions-for-flex-box-css -->
        <div
          style="aspect-ratio: {width}/{height};"
          class="c2"
          bind:this={myDivElement}
          on:mousedown={handleMouseDown}
          on:mousemove={handleMouseMove}
          on:mouseup={handleMouseUp}   
        >
        {#if selection_outline_enabled}
        <div id="selectionOutline"
             style="
             left: {selectionOutlineStyle.left};
             top: {selectionOutlineStyle.top};
             width: {selectionOutlineStyle.width};
             height: {selectionOutlineStyle.height};
             display: {selectionOutlineStyle.display};
             "
        >{JSON.stringify(startCoords)} to {JSON.stringify(endCoords)}</div>
        {/if}
        
          {#if overlay_data}
            {#each overlay_data as o,idx}
              <a href="/s?q=face:{img_id}.{idx}"><div
                class="c3"
                style="top:{o.y-o.h/6}%; left:{o.x-o.w/6}%; height:{o.h+o.h/3}%; width:{o.w+o.w/3}%; "
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
    background: linear-gradient(45deg, rgb(0 0 0),  rgb(15 23 42));
    opacity:0.95;
  }
  .overlay-2 {
    background: linear-gradient(-45deg, rgb(0 0 0),  rgb(15 23 42));
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
    /* pointer-events: none; */
  }
  .c1 {/* a flex box constraining the height, but potentially narrower width */
    max-width: 100%;
    height: 100%;
    display: flex;
    flex-shrink: 1;
    flex-direction: column;
    justify-content: center;
    /* pointer-events: none; */
  }
  .c2 { /* a flex box constraining the width, but potentially shorter height */
    max-height: 100%;
    width: 100%;
    flex-shrink: 1;
    flex-direction: row;
    flex-grow: 0;
    position: relative;
    /* pointer-events: none; */
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


  /* === selection === */
  #selectionOutline {
      position: absolute;
      border: 1px dashed red;
      background-color: rgba(255,0,0,0.5);
      pointer-events: none; /* Avoid blocking mouse events on #myDiv */
  }
  /* === selection === */
</style>
