<script lang="ts">
    import { preview_store, cols_store, split_header_store } from "./stores.js";
    export let data: PageData;

    import { page } from "$app/stores";
    import type { PageData } from "./$types";
    import Camera from "./Camera.svelte";
    import Help from "./Help.svelte";

    import { onMount } from "svelte";
    import SearchForm from "./SearchForm.svelte";

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
        camera_button_visible = checkCameraAvailability();
    });

    let min_cols = 1;
    let max_cols = 30;
    let cols = 9; // has an effect
    let inv_cols = max_cols - cols + 1;
    $: cols_store.set(max_cols - inv_cols + min_cols);

    /* help */
    let help = false;
    function showhelp() {
        help = true;
    }

    $: backurl = "?" + new URLSearchParams({ q: data.q || "" });

    $: img_data = data?.details?.img_data;

    // Determine if the header should be split to make more room for the picture
    let innerHeight = 0;
    let innerWidth = 0;
    function select_split_header(
        img_data: { height: number; width: number },
        innerWidth: number,
        innerHeight: number
    ) {
        if (!img_data) return false;
        if (!img_data.height) return false;
        const img_aspect_ratio = img_data.height / img_data.width;
        const screen_aspect_ratio = innerHeight/innerWidth;
        let split_header = img_aspect_ratio > screen_aspect_ratio
        split_header_store.set(split_header);
        return split_header;
    }
    $: split_header = select_split_header(data?.details?.img_data, innerWidth, innerHeight);
</script>

<svelte:window bind:innerWidth bind:innerHeight />

{#if split_header}
    <div class="safe_header_area_l">
        <div
            class="m-0 text-3xl rounded-xl border border-gray-500
            flex w-full
            justify-center align-middle object-center
            overflow-clip
            bg-slate-800 headers
            whitespace-nowrap
            items-stretch
            "
        >
            <a href="/" class="header-item block hover:bg-slate-400">⌂</a>
            <div class="flex-grow flex-shrink w-10 basis-2/6 text-xl header-item p-1"
            style="flex-wrap: nowrap; display:flex">
                <SearchForm />
            </div>
        </div>
    </div>
    <div class="safe_header_area_r">
        <div
            class="m-0 text-3xl rounded-xl border border-gray-500
    flex w-full
    justify-center align-middle object-center
    overflow-clip
    bg-slate-800 headers
    whitespace-nowrap
    items-stretch
    "
        >
            {#if camera_button_visible}
                <button
                    on:click={() => (camera_visible = !camera_visible)}
                    class="header-item"
                >
                    <div class="inline-flex">&nbsp;&#128247;&#xFE0E;&nbsp;</div>
                </button>
            {/if}

            <label
                class="flex-shrink header-item content-center pt-2"
                style="flex-shrink:5"
            >
                <input
                    type="range"
                    class="flex-shrink"
                    style="max-width:3em"
                    bind:value={inv_cols}
                    min={min_cols}
                    max={max_cols}
                />
            </label>

            <a
                class="header-item"
                on:click={showhelp}
                href="#help"
                title="Help [?]">?</a
            >

            {#if data?.d}
                <a class="header-item" href={backurl} title="Back to list [ESC]"
                    >&#x2715;&#xFE0E;</a
                >
            {/if}
        </div>
    </div>
{:else}
    <div class="safe_header_area">
        <div
            class="m-0 text-3xl rounded-xl border border-gray-500
            flex w-full
            justify-center align-middle object-center
            overflow-clip
            bg-slate-800 headers
            whitespace-nowrap
            items-stretch
            "
        >
            <a href="/" class="header-item block hover:bg-slate-400">⌂</a>
            <div class="flex-grow flex w-10 basis-2/6 text-xl header-item p-1">
                <SearchForm />
            </div>

            {#if camera_button_visible}
                <button
                    on:click={() => (camera_visible = !camera_visible)}
                    class="header-item"
                >
                    <div class="inline-flex">&nbsp;&#128247;&#xFE0E;&nbsp;</div>
                </button>
            {/if}

            <label
                class="flex-shrink header-item content-center pt-2"
                style="flex-shrink:5"
            >
                <input
                    type="range"
                    class="flex-shrink"
                    style="max-width:3em"
                    bind:value={inv_cols}
                    min={min_cols}
                    max={max_cols}
                />
            </label>

            <a
                class="header-item"
                on:click={showhelp}
                href="#help"
                title="Help [?]">?</a
            >

            {#if data?.d}
                <a class="header-item" href={backurl} title="Back to list [ESC]"
                    >&#x2715;&#xFE0E;</a
                >
            {/if}
        </div>
    </div>
{/if}

<Help bind:enabled={help} />

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
        font-weight: bolder;
        padding: 0.25rem 0.5rem 0.25rem 0.5rem;
    }

    .header-item:last-child {
        border-right: none;
    }
    *.header-item:hover {
        background: rgba(0, 0, 200, 0.8);
        color: #ccf;
    }
    a.header-item {
        display: block;
        /*background-color: rgba(0, 0, 0, 0.5);*/
        text-align: center;
        color: rgb(2 132 199 / var(--tw-text-opacity));
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

        .safe_header_area_l {
            position: fixed;
            border-radius: 0.75rem /* 12px */;
            top: env(safe-area-inset-top);
            left: env(safe-area-inset-left);
            width: 25%;
            background-color: rgba(0, 0, 0, 0.5);
            padding-top: 1mm;
            padding-bottom: 1mm;
            padding-left: 1mm;
            padding-right: 1mm;
            z-index: 50;
        }

        .safe_header_area_r {
            position: fixed;
            border-radius: 0.75rem /* 12px */;
            top: env(safe-area-inset-top);
            right: env(safe-area-inset-right);
            max-width: 25%;
            background-color: rgba(0, 0, 0, 0.5);
            padding-top: 1mm;
            padding-bottom: 1mm;
            padding-left: 1mm;
            padding-right: 1mm;
            z-index: 50;
        }
    }
</style>
