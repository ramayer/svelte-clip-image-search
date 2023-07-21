<script>
    import SearchForm from "./s/SearchForm.svelte";
</script>

<SearchForm />

<div class="m-10 p-10">
    <h1 class="text-3xl my-10">
        SvelteKit UI for CLIP and Face based Image Search
    </h1>
    <h2 class="text-2xl my-10 mx-5">
    Features:
    </h2>

    <h3 class="text-xl m-10">CLIP based embedding math</h3>
    <div class="m-10">
    Similar to the famous "king -man +woman" example the for word embeddings,
    you can also do math with CLIP images.
    <ul class="list-disc p-5">
        <li>
            <a href="/s?q=zebra+-horse+%2Bfish">zebra -horse +fish</a> shows black&white
            striped fish
        </li>
        <li>
            Searching for
            <a href="/s?q=zebra+-horse+%2Bcat+-stripes+%2Bspots">
                zebra -horse +cat -stripes +spots
            </a>
            finds tigers
        </li>
        <li>
            Searching for

            <a href="/s?q=skiing+-snowy+winter+%2Bsunny+summer">
                skiing -snowy winter +sunny summer
            </a>
        </li>
        <li>
            This picture of <a href="/s?q=clip%3A24881">
                a spider on a pink flower
            </a>
            minus
            <a href="/s?q=clip%3A24880">
                this picture of the same kind of flower
            </a>
            equals
            <a href="/s?q=clip%3A24881+-clip%3A24880">
                this picture of the same kind of spider without the flower
            </a>
        </li>
    </ul>
    </div>

    <div class="text-sm">
        Images in this demo are from Wikimedia Commons, available under various
        different licenses specified on their description page. Click on the
        "details" link for each image to see its specific license.
        <br /><br />
        Source code availble
        <a href="https://github.com/ramayer/svelte-clip-image-search"
            >on githb here</a
        >. Much thanks to
        <a href="https://github.com/yurijmikhalevich/rclip">rclip</a> that inspired
        this project and providied the back-end indexes.
    </div>
</div>
