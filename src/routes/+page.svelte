<script lang="ts">
  import { page } from "$app/stores";
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";
  import ImageGrid from "../components/ImageGrid.svelte";

  // let base_url = "http://192.168.12.110:8000/";
  let base_url = "http://image-search.0ape.com/";

  let search_query = $page.url.searchParams.get("q");
  let search_results = get_search_results(search_query);

  function q_parameter_changed(new_q) {
    console.log("new_q = " + new_q + " old_q = " + search_query);
    if (search_query != new_q) {
      search_query = new_q;
      search_results = get_search_results(search_query);
    }
  }

  $: q_parameter_changed($page.url.searchParams.get("q"));

  onMount(() => {
    console.log("in onMount");
  });

  async function get_search_results(q: string | number | boolean | null) {
    console.log("searching for " + q);
    if (!q) {
      return await [];
    }
    const url = base_url + `search_api?num=2500&q=` + encodeURIComponent(q);
    const resp = await fetch(url);
    if (resp.ok) {
      return await resp.json();
    } else {
      throw new Error(resp.statusText);
    }
  }

  let cached_search_results = null;

  function submit_form() {
    goto("?q=" + encodeURIComponent(search_query || ""));
    search_results = get_search_results(search_query);
  }
  let foo = null;
</script>

<div id="search_form">
  <form on:submit|preventDefault={submit_form}>
    <label for="q">Search</label>
    <input
      id="q"
      type="search"
      name="q"
      bind:value={search_query}
      on:input={() =>
        (cached_search_results = get_search_results(search_query))}
    />
    <button type="submit">Search</button>
  </form>
</div>
<div id="search_form_spacer" />

{#await search_results}
  <p>...loading</p>
{:then api_response}
  <ImageGrid imgs={api_response} bind:base_url bind:search_query />
{:catch error}
  <p style="color: #ccc">{error.message}</p>
{/await}

<style>
  #search_form,
  #search_form_spacer {
    width: 100%;
    height: 30px;
  }
  #search_form {
    position: fixed;
    z-index: 30;
  }
  #search_form #q{
    width:80%
  }
</style>
