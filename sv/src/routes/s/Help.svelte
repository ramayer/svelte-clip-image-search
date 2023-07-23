<script lang="ts">
  export let help = false;
</script>

{#if help}
  <section
    id="help"
    class="block h-full"
    on:click={() => {
      help = false;
    }}
    on:keydown={() => {
      help = false;
    }}
  >
    HELP!
    {help}
    <button
      on:click={() => {
        help = false;
      }}>hi</button
    >
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
    justify-content: center;
    align-items: center;
    opacity: 1;
    background: rgba(0, 0, 0, 0.8);
  }
</style>
