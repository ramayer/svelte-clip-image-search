<script lang="ts">
    import { preview_store, cols_store } from "./stores.js";
    export let data: PageData;

    import { page } from "$app/stores";
    import type { PageData } from "./$types";
    import Camera from "./Camera.svelte";

    import { onMount } from "svelte";

    let q_input: HTMLInputElement;
    let camera_visible = false;
    let camera_button_visible = false;

    function checkCameraAvailability() {
        if (navigator.mediaDevices) {
            navigator.mediaDevices
                .enumerateDevices()
                .then((devices) => {
                    const cameras = devices.filter(
                        (device) => device.kind === "videoinput"
                    );
                    if (cameras.length > 0) {
                        console.log("found cameras");
                        camera_button_visible = true;
                        return true;
                    } else {
                        console.log("found no cameras");
                        return false;
                    }
                })
                .catch((error) => {
                    console.error("Error enumerating devices:", error);
                    return false;
                });
        } else {
            console.log("MediaDevices or getUserMedia are not supported");
            return false;
        }
        return false;
    }

    onMount(() => {
        q = $page.url.searchParams.get("q");
        // q_input.focus();
        camera_button_visible = checkCameraAvailability();
        //console.log("camera avalabile - ",camera_button_visible)
    });

    let q = $page.url.searchParams.get("q");
    let min_cols = 1;
    let max_cols = 30;
    let cols = 9; // has an effect
    let inv_cols = max_cols - cols + 1;

    function q_changed(new_q: string | null) {
        if (q != new_q) {
            console.log("q changed from " + q + " to ", new_q);
            q = new_q;
        }
    }
    $: q_changed($page.url.searchParams.get("q"));

    $: cols_store.set(max_cols - inv_cols + min_cols);
    let questions = [
        { id: 1, text: `Img` },
        { id: 2, text: `Txt` },
    ];

    let selected = 0;
    let answer = "";
</script>

<div class="safe_header_area">
    <form>
        <div
            class="m-0 text-2xl rounded-xl border border-gray-500 
            flex w-full bg-transparent
            justify-center align-middle object-center
            overflow-clip
            bg-gray-800 header"
        >
            <div class="header-item">
                <a
                    href="/"
                    class="block p-1 hover:bg-slate-400">
                    <div style="transform: rotate(45deg);">⚲</div></a
                >
            </div>            

            <div class="flex-grow flex w-10 basis-2/6 text-xl header-item">
                <input
                    bind:this={q_input}
                    type="search"
                    name="q"
                    bind:value={q}
                    class="inline-flex flex-grow p-1 bg-gray-800 text-s"
                />
            </div>
            {#if false}
            <select
                bind:value={selected}
                on:change={() => (answer = "")}
                class=""
            >
                {#each questions as question}
                    <option value={question}>
                        {question.text}
                    </option>
                {/each}
            </select>
            {/if}
            <button type="submit" class="header-item">
                <div class="inline-flex">&nbsp;👀&nbsp;</div>
            </button>
            {#if camera_button_visible}
                <button on:click={() => (camera_visible = !camera_visible)} class="header-item">
                    <div class="inline-flex">&nbsp;&#128247;&#xFE0E;&nbsp;</div>
                </button>
            {/if}

            <label class="p-1 flex-shrink block header-item content-center" style="flex-shrink:5">
                <input
                    type="range"
                    class="flex-shrink"
                    style="width:4em"
                    bind:value={inv_cols}
                    min={min_cols}
                    max={max_cols}
                />
            </label>

            <div class="px-2 header-item">
                <a href="help" title="Help [?]">?</a>
            </div>
            {#if data && data.d}
                <div class="px-2 header-item">
                    <a
                        href={"?" + new URLSearchParams({ q: data.q || "" })}
                        title="Back to list [ESC]">&#x2715;&#xFE0E;</a
                    >
                </div>
            {/if}
        </div>
    </form>
</div>
{#if camera_visible}
    <div class="fixed right-4 w-80 top-8 z-50">
        <Camera />
    </div>
{/if}

<style>
    .safe_header_area {
        position: fixed;
        background-color: rgba(0, 0, 0, 0.5);
        padding: 1mm;
        top: 10px; /* Fallback value */
        left: 10px;
        right: 10px;
        z-index: 50;

    }

    .header-item {
     border-right: 1px solid #666;
    }

    .header-item:last-child {
        border-right: none;
    }


    .header-item a {
      display:block;
      padding: 0.25rem/* 4px */;
    }

    @supports (padding-top: env(safe-area-inset-top)) {
        .safe_header_area {
        position: fixed;
        top: env(safe-area-inset-top);
        left: env(safe-area-inset-left);
        right: env(safe-area-inset-right);
        background-color: rgba(0, 0, 0, 0.5);
        padding-top: 1mm;
        padding-bottom: 1mm;
        padding-left: 1mm;
        padding-right: 1mm;
        z-index: 50;
    }        
    }


</style>
