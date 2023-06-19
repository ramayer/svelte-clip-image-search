<script lang="ts">

    import {page} from "$app/stores"
    import ResultList from './ResultList.svelte';
    import type {PageData} from './$types';

    export let data: PageData;

    let debug='';
    const searchform_class = "flex-1 h-10 px-4 m-1 text-gray-700 placeholder-gray-400 bg-transparent border-none appearance-none lg:h-12 dark:text-gray-200 focus:outline-none focus:placeholder-transparent focus:ring-0"; 

    const url = $page.url;  // this will stay as the original value of the url
    let q = $page.url.searchParams.get('q');
    
    $:console.log("===")
    $:console.log('+page.svelte page',$page)
    $:console.log('+page.svelte data',data)
    $:console.log('+page.svelte url',url)
    $:console.log('+page.svelte q',q)
    $:console.log("===")
    
</script>

<form>
<input type="search" name="q" bind:value={q} class={searchform_class} placeholder="Search Components">
</form>

<div>
    Debug = {debug}
</div>
<ResultList results={data}>hi

</ResultList>