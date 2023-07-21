<script lang="ts">
    import { preview_store, cols_store } from "./stores.js";

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
                        console.log("found cameras")
                        camera_button_visible = true
                        return true;
                    } else {
                        console.log("found no cameras")
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

<div class="position_nav_bar_safely fixed top-1 left-1 w-full pr-2 z-50">
    <form>
        <div
            class="p-1 pr-3 rounded-2xl flex w-full bg-transparent [&>*]:bg-gray-900 [&>*]:border-gray-500 [&>*]:border"
            style="z-index:999"
        >
            <div class="rounded-l-lg p-1">
                <a
                    href="/"
                    class="inline-block"
                    style="transform: rotate(45deg);">⚲</a
                >
            </div>
            <div class="flex-grow flex w-10">
                <input
                    bind:this={q_input}
                    type="search"
                    name="q"
                    bind:value={q}
                    class="inline-flex flex-grow p-1 bg-gray-800"
                />
            </div>
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
            <button type="submit">
                <div class="inline-flex">&nbsp;👀&nbsp;</div>
            </button>
            {#if camera_button_visible}
                <button on:click={() => (camera_visible = !camera_visible)}>
                    <div class="inline-flex">&nbsp;&#128247;&#xFE0E;&nbsp;</div>
                </button>
            {/if}

            <label class="pt-2 flex-shrink rounded-r-lg" style="flex-shrink:5">
                <input
                    type="range"
                    class="flex-shrink"
                    style="width:4em"
                    bind:value={inv_cols}
                    min={min_cols}
                    max={max_cols}
                />
            </label>
        </div>
    </form>
</div>
{#if camera_visible}
    <div class="fixed right-4 w-80 top-8 z-50">
        <Camera />
    </div>
{/if}

<style>
    .position_nav_bar_safely {
        position: fixed;
        top: 10px; /* Fallback value */
    }

    @supports (padding-top: env(safe-area-inset-top)) {
        .position_nav_bar_safely {
            top: env(safe-area-inset-top); /* Uses env() if supported */
        }
    }
</style>
