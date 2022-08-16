<script lang="ts">

    console.log("======== starting script ========")

    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import ImageGrid from '../components/ImageGrid.svelte';
    
    let base_url = "http://192.168.12.110:8000/"; // "http://image-search.0ape.com/"; //
    
    let search_query=$page.url.searchParams.get('q');
    
    async function get_search_results(q: string|number|boolean|null) {
      console.log("searching for "+q);
      if (!q) {
        return await [];
      }
      //const url = `http://image-search.0ape.com/search_api?num=300&q=`+encodeURIComponent(q);
      const url = base_url + `search_api?num=2500&q=`+encodeURIComponent(q);
      const resp = await fetch(url);
      if (resp.ok) {
        return await resp.json();
      } else {
        throw new Error(resp.statusText);
      }
    }

    let search_results = get_search_results(search_query);
    let cached_search_results = null;
    function submit_form() {
      goto('?q='+encodeURIComponent(search_query||''));
      search_results = get_search_results(search_query);
    }
    let foo = null
</script>

<form on:submit|preventDefault={submit_form}>
    <input type="search" name="q" 
      bind:value={search_query} 
      on:input={() => cached_search_results = get_search_results(search_query)}
    />
    <button type="submit">Search</button>
</form>


{#await search_results}
  <p>...loading</p>
{:then api_response}
  <ImageGrid imgs={api_response} bind:base_url={base_url}></ImageGrid>
{:catch error}
  <p style="color: #ccc">{error.message}</p>
{/await}
