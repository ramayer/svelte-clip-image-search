<script context="module" lang="ts">
</script>

<script lang="ts">
    console.log("======== starting script ========")

    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import ImageGrid from '../components/ImageGrid.svelte';
    
    let search_query=$page.url.searchParams.get('q');

    async function get_search_results(q) {
      //const url = `http://image-search.0ape.com/search_api?num=300&q=`+encodeURIComponent(q);
      const url = `http://192.168.12.110:8000/search_api?num=300&q=`+encodeURIComponent(q);
      const res = await fetch(url);
      const text = await res.json();
      console.log("searching for "+q)
      if (res.ok) {
        return text;
      } else {
        throw new Error(text);
      }
    }

    let search_results = get_search_results(search_query);
    let cached_search_results = [];
    function submit_form() {
      goto('?q='+encodeURIComponent(search_query));
      search_results = get_search_results(search_query) 
    }
</script>

<form on:submit|preventDefault={submit_form}>
   
    <input type="search" name="q" 
      bind:value={search_query} 
      on:input={() => cached_search_results = get_search_results(search_query)}
    />
    <button type="submit">Search</button>
</form>

<ImageGrid bind:imgs={search_results}></ImageGrid>
