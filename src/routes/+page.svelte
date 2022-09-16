<script lang="ts">
  import { page } from "$app/stores";
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";
  import ImageGrid from "../components/ImageGrid.svelte";

  //let base_url = "http://192.168.12.110:8000/";
  let base_url = "http://image-search.0ape.com/";
  // let base_url = "http://localhost:8000/";

  let search_query = $page.url.searchParams.get("q");
  let search_results = get_search_results(search_query);
  let thm_size = 224;

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

<form on:submit|preventDefault={submit_form}>
  <nav id="search_form">
    <div class="nav_q nav_item">
      <label for="q"><a href="/" class="mag">&#9906;</a></label>
      <input
        id="q"
        type="search"
        name="q"
        bind:value={search_query}
        on:input={() =>
          (cached_search_results = get_search_results(search_query))}
      />
      <button class="qbtn" type="submit"><div>&nbsp;👀&nbsp;</div></button>
    </div>
    <div class="nav_sz nav_item">
      <nobr>
        <label for="sz">▫</label><input
          id="sz"
          class="sz .slider"
          type="range"
          bind:value={thm_size}
          min="56"
          max="896"
        /><label for="sz">◻</label>
      </nobr>
    </div>
  </nav>
</form>
<div id="search_form_spacer" />

{#await search_results}
  <p>...loading</p>
{:then api_response}
  {#if api_response.length > 0}
    <ImageGrid
      imgs={api_response}
      bind:base_url
      bind:search_query
      desired_size={thm_size}
    />
  {:else}
    <div id="no_results_msg" class="no_results_msg">
      <h2>
        SvelteKit UI for a CLIP embedding based search of Wikimedia images
      </h2>

      This system lets you do simple math on CLIP embeddings with prefixes like
      "-" to subtract CLIP vectors and "+" to add them.
      <ul>
        <li>
          <a href="/?q=zebra -stripes %2Bspots">zebra -stripes +spots</a> - Animals
          that look kinda like zebras but with spots instead of stripes.
        </li>
        <li>
          <a href="/?q=zebra -mammal %2Bfish">zebra -mammal +fish</a> - Animals that
          are like zebras but fish instead of mammals.
        </li>
        <li>
          <a href="/?q=zebra -animal %2Bcar">zebra -animal +car</a> - Objects colored
          like zebras but more cars than animals.
        </li>
        <li>
          <a href="/?q=zebra%20-%22black%20and%20white%22"
            >zebra -"black and white"</a
          >
          - Baby zebras (brown & white) and a Greater Kudu (a brown & white striped
          4-legged animal). Of course you could also just search for
          <ul>
            <li>
              <a href="/?q=zebra%20-big %2Bsmall">zebra -big +small</a>
              or even more simply, just
            </li>
            <li>
              <a href="/?q=baby%20zebra">baby zebra</a> to find the same baby zebra.
            </li>
          </ul>
        </li>
        <li>
          <a href="/?q=furry black and white striped animal"
            >furry black and white striped animal</a
          >
          - zebras but also lemurs, and other furry black and white animals.
        </li>
        <li>
          <a href="/?q=striped horse-like animal">striped horse-like animal</a> -
          more zebras (and horses with stripes)
        </li>
        <li>
          <a href="/?q=zebra habitat -zebra">zebra habitat -zebra</a> - places that
          look like zebras might live there.
        </li>
      </ul>
      It can also do a search based on the difference between the CLIP embeddings
      of two images directly. For example, CLIP considers
      <a href="/?q=%7B%22image_id%22%3A28754%7D"
        >this image of a spider on a purple flower</a
      >
      minus
      <a href="/?q=%7B%22image_id%22%3A174054%7D"
        >this image of the same kind of spider on a white flower</a
      >
      to be
      <a
        href="/?q=%7B%22image_id%22%3A28754%7D%20-%7B%22image_id%22%3A174054%7D"
        >this set of pictures which is mostly purple flowers without the spider</a
      >.

      <br />
      <br />
      <br />
    </div>
    <hr />

    <small
      >Images in this demo are from Wikimedia Commons, available under various
      different licenses specified on their description page. Click on the
      "details" link for each image to see its specific license.
      <br /><br />
      Source code for the server-side of this project is
      <a href="https://github.com/ramayer/rclip-server"
        >available here on github</a
      >. Source code for the client side will be posted soon.</small
    >
  {/if}
{:catch error}
  <p style="color: #ccc">{error.message}</p>
{/await}

<style>
  #search_form,
  #search_form_spacer {
    width: 100%;
    height: 40px;
  }
  #search_form {
    flex-direction: row;
    position: fixed;
    z-index: 30;
    display: flex;
    vertical-align: middle;
    background-color: rgba(0, 0, 0, 0.5);
    border: 1px solid green;
    /*border: 1px solid red;*/
  }
  #search_form #q {
    flex-shrink: 1;
    flex-grow: 1;
    margin: 3px;
  }
  #search_form * {
    vertical-align: middle;
  }
  .nav_item {
    padding: 3px;
    flex-shrink: 1;
    flex-grow: 1;
    border: 1px solid red;
    display: flex;
  }
  #sz {
   flex-grow: 1;
  }
  .nav_q {
    flex-grow: 2;
    flex-shrink: 1;
  }
  .nav_sz {
    flex-grow: 0;
    flex-shrink: 1;
  }


  a {
    text-decoration: none;
    color: #88f;
  }
  a:hover {
    text-decoration: underline;
    color: #ccf;
  }
  #search_form a {
    color: #fff;
    font-size: 20pt;
    font-weight: bold;
  }
  .no_results_msg {
    width: 70%;
    padding: 30px;
    margin: 40px auto 40px auto;
    background-color: #000;
  }
  .mag {
    display: inline-block;
    -webkit-transform: rotate(45deg);
    -moz-transform: rotate(45deg);
    -o-transform: rotate(45deg);
    transform: rotate(45deg);
    font-weight: bold;
    border: 0;
    margin: 0;
    padding: 0;
  }
  .qbtn {
    background-color: #333;
    border-radius: 8px;
    border-width: 1;
    border-color: #ccc;
    color: #fff;
    cursor: pointer;
    display: inline-block;
    font-family: "Haas Grot Text R Web", "Helvetica Neue", Helvetica, Arial,
      sans-serif;
    font-size: 17px;
    font-weight: 500;
    line-height: 15px;
    list-style: none;
    margin: 0;
    padding: 3px 12px;
    text-align: center;
    transition: all 200ms;
    vertical-align: baseline;
    white-space: nowrap;
    user-select: none;
    -webkit-user-select: none;
    touch-action: manipulation;
  }
  .sz {
    width: 80%;
  }
</style>
