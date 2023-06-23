<script lang="ts">
    export let selected_img:string;
    export let selected_state:number;
</script>
{#if selected_img}
<div class="fixed bottom-1 right-1 h-[40vh] w-[50vw] bg-black ...">
    ResultDetail for {selected_img}
    <img alt={"" + selected_img} src="/t/{selected_img}" />
</div>
{/if}