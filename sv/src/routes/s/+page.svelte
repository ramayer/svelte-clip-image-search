<script lang="ts">

    import {page} from "$app/stores"
    import ResultList from './ResultList.svelte';

    import type {PageData} from './$types';

    export let data: PageData;

    const searchform_class = "flex-1 h-10 px-4 m-1 text-gray-700 placeholder-gray-400 bg-transparent border-none appearance-none lg:h-12 dark:text-gray-200 focus:outline-none focus:placeholder-transparent focus:ring-0"; 

    const url = $page.url;
    let q = $page.url.searchParams.get('q');
    
    console.log('page',$page)
    $:console.log('data',data)
    console.log('url',url)
    $:console.log('q',q)

</script>

<form>
<input type="search" name="q" bind:value={q} class={searchform_class} placeholder="Search Components">
</form>


<ResultList results={data}>hi

</ResultList>