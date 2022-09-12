#  Svelte CLIP Image Search

A SvelteKit UI for a CLIP-based image search backend. 

## My first attempt at a SvelteKit based UI.

This project uses the [same FastAPI backend for CLIP-based image search](ramayer/rclip-server) as my earlier Vue-based UI found [here](https://github.com/ramayer/rclip-server/blob/main/assets/rclip_server.html).

## Demo

A demo of this UI, using Wikimedia Commons images, can be [seen here](http://image-search.0ape.com/).

Try searching for somethign like [skiing -summer +winter](http://image-search.0ape.com/?q=skiing%20%2Bsummer%20-winter) to see sports that are kinda-like skiing, but happen in summer instead of winter.

## Thanks

Special Thanks to: 

* Github user @yurijmikhalevich for his [rclip](https://github.com/yurijmikhalevich/rclip) CLI tools that inspired this project and are now used to manage all my home photos.
* Github user @berkinakkaya for his [svelte-image-gallery](https://github.com/berkinakkaya/svelte-image-gallery) project that made me interested in porting the front-end to Svelte, (and whose code I used, though I need to double-check with him about licensing.... doing that now)
