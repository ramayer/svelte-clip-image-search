<script lang="ts">

import { selected_img, selected_state } from './stores.js';

    import {page} from "$app/stores"
    import ResultList from './ResultList.svelte';
    import ResultDetail from './ResultDetail.svelte';
    import type {PageData} from './$types';

    let s_img = '';
    let s_state = 0;
    selected_img.subscribe(x => {
        s_img = x
    })    
    selected_state.subscribe(x => {
        s_state = x
    })

    export let data: PageData;
    let cols=20;

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

    let questions = [
		{ id: 1, text: `Img` },
		{ id: 2, text: `Txt` },
	];

	let selected=0;

	let answer = '';


    let searchtype_style="flex-shrink-0 z-10 inline-flex items-center py-2.5 px-4 text-sm font-medium text-center text-gray-900 bg-gray-100 border border-gray-300 rounded-l-lg hover:bg-gray-200 focus:ring-4 focus:outline-none focus:ring-gray-100 dark:bg-gray-700 dark:hover:bg-gray-600 dark:focus:ring-gray-700 dark:text-white dark:border-gray-600"
    let searchform_style="block p-2.5 w-full z-20 text-sm text-gray-900 bg-gray-50 rounded-r-lg border-l-gray-50 border-l-2 border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-l-gray-700  dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:border-blue-500" 
    let searchbutton_style="absolute top-0 right-0 p-2.5 text-sm font-medium text-white bg-blue-700 rounded-r-lg border border-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"

    
</script>

<form>
<input type="search" 
        name="q" bind:value={q} 
        class={searchform_class} placeholder="Search">

        <label>
            <input type=range bind:value={cols} min=1 max=20>
            </label>
</form>

<hr>
<form>
    <div class="flex">
        <div>
            <select bind:value={selected} on:change="{() => answer = ''}" class={searchtype_style}>
                {#each questions as question}
                    <option value={question}>
                        {question.text}
                    </option>
                {/each}
            </select>
                </div>
        <div class="relative w-full">
            <input type="search" name="q" bind:value={q}  class={searchform_style} placeholder="Search" required>
            </div><div>
    <input type=range class={searchbutton_style} bind:value={cols} min=1 max=20>
            <button type="submit" class={searchbutton_style}>
                <svg aria-hidden="true" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                <span class="sr-only">Search</span>
            </button>
            
        </div>
    </div>
</form>

<div>
    Debug = {s_img}, {s_state}
</div>
<ResultList results={data} cols={cols}>hi
</ResultList>
<ResultDetail selected_img={s_img} selected_state={s_state}> 
</ResultDetail>
