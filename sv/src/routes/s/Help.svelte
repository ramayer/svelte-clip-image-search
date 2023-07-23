<script lang="ts">
  export let enabled = true;

  function close(e: KeyboardEvent | MouseEvent) {
    enabled = false;
  }

  let advanced_search = [
    [
      "zebra -horse +fish",
      "search for things like a zebra, but more fishy and less horsey ",
    ],
    [
      "clip:1234",
      "search for images similar to image #12345 according to CLIP models",
    ],
    [
      "clip:[3,-7,1,0,-15,7,-22,...]",
      "Search for images similar to a specifc CLIP embedding",
    ],

  ];
  let detail_page_tricks = [
    [
      "ctrl-click (or cmd-click) and drag on the detail image",
      "search for the specific region inside an image",
    ],
    [
      "click on a yellow box around a face",
      "search for images with similar faces to the one clicked",
    ],
    [
      "keypress-right-arrow",
      "go to the next image in the list",
    ],
    [
      "keypress-left-arrow",
      "go to the previous image in the list",
    ],
    [
      "keypress-ESC",
      "go back to the thumbnail view",
    ],

  ];
</script>

<svelte:window
  on:keydown={close}
/>

{#if enabled}
  <section
    id="help"
    on:keydown={close}
    on:click={close}
  >
    <div class="p-20">
      <h1 class="text-4xl">Help</h1>
      <h2 class="text-2xl pt-4">Advanced Search Syntax</h2>
      <ul class=" space-y-1 text-gray-500 list-disc list-inside dark:text-gray-400">
        {#each advanced_search as a}
        <li>
          <span class="font-bold">{a[0]}</span> -- {a[1]}
        </li>
        {/each}
      </ul>

      <h2 class="text-2xl pt-4">Detail page tricks</h2>
      <ul class=" space-y-1 text-gray-500 list-disc list-inside dark:text-gray-400">
        {#each detail_page_tricks as a}
        <li>
          <span class="font-bold">{a[0]}</span> -- {a[1]}
        </li>
        {/each}
      </ul>

    </div>
  </section>
{/if}

<style>
  #help {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: 2000;
    display: flex;
    justify-content: center;
    align-items: center;
    opacity: 1;
    background: rgba(0, 0, 0, 0.8);
  }
</style>
