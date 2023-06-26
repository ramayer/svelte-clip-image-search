<script lang="ts">
    export let selected_img:string;
    export let selected_state:number;
</script>

{#if selected_img}
<div class="fixed bottom-1 right-1 h-[50vh] w-[50vw] bg-black ...">
    ResultDetail for {selected_img}z
    <img alt={"" + selected_img} 
    class="m-auto"
         style="max-height: calc(50vh - 30px)"
         src="/i/{selected_img}" />
</div>
{/if}