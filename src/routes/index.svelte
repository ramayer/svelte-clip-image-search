<h1>Welcome to SvelteKit</h1>

<script context="module" lang="ts">
    /** @type {import('./__types/[slug]').Load} */  
    export async function load({ params, fetch, session, stuff }) {

      const url = `http://image-search.0ape.com/search_api?num=1000&q=asdf`;
      const response = await fetch(url);
      return {
        status: response.status,
        props: {
          article: response.ok && (await response.json())
        }
      };

    }
</script>

<script lang="ts">
    
    import { page } from '$app/stores';
    let search_query=$page.url.searchParams.get('q');

    async function get_search_results(q) {
      const url = `http://image-search.0ape.com/search_api?num=10&q=`+q;
      const res = await fetch(url);
      const text = await res.json();
      if (res.ok) {
        return text;
      } else {
        throw new Error(text);
      }
    }
    let search_results = get_search_results(search_query);


</script>

<p>Current URL: {$page.url.searchParams}</p>
<p>Current q: {search_query}</p>

<h1>Search</h1>
<form >
    <input type="search" name="q" bind:value={search_query} /><button type="submit">Search</button>
</form>

{#await search_results}
	<p>...waiting</p>
{:then search_results}
  {#each search_results as [image_id,image_score], idx}
    <div style="float:left">
      <img src="http://image-search.0ape.com/thm/{image_id}?size=400"><br>
      {image_id} -- {image_score} -- {idx}<br>
    </div>
  {/each}
{:catch error}
	<p style="color: red">{error.message}</p>
{/await}
<!-- consider: https://www.youtube.com/watch?v=jpKbyiQsj3k -->
