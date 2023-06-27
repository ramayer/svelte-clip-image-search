<script lang="ts">
    export let selected_img:string;
    export let selected_state:number;
    let vh="50vh";
    let vw="50vw";
    $:vh = (selected_state % 2) ? "50vh" : "100vh"
</script>

{#if selected_img}
<div class="fixed rounded-2xl bottom-1 right-1 h-[{vh}] w-[{vw}] bg-black ...">
    ResultDetail for {selected_img} {selected_state}
    <img alt={"" + selected_img} 
    class="m-auto"
         style="max-height: calc({vh} - 30px)"
         src="/i/{selected_img}" />
</div>
{/if}