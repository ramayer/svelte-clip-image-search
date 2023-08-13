<script lang="ts">
    import SearchForm from "./s/SearchForm.svelte";
</script>

<SearchForm/>

<div class="m-1 p-1">
    <h1 class="text-3xl mt-5 text-center">
        Sveltekit ML Image Gallery
    </h1>
    
    <div class="mx-10 my-3 py-3 bg-slate-900 px-5">
        <h2 class="text-2xl  text-center">
            Features
            </h2>
        <ul class="list-disc pl-5">
        <li>
            <a href="/s?q=zebra+%2Bfish+-horse">zebra +fish -horse</a> using CLIP embedding math
        </li>
        <li>
            <a href="/s?q=face:1685.0">find faces</a> using InsightFace's models
        </li>
    </ul>
    </div>
    <div class=" text-xs border-t pt-3 border-slate-600 ">
        Images in this demo are from Wikimedia Commons, available under various
        different licenses specified on their description page. Click on the
        "details" link for each image to see its specific license.
        Source code availble
        <a href="https://github.com/ramayer/svelte-clip-image-search"
            >on github here</a
        >. Much thanks to
        <a href="https://github.com/yurijmikhalevich/rclip">rclip</a> that inspired
        this project and provided the back-end CLIP indexes.
    </div>
</div>
