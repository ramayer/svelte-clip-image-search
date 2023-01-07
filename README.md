#  Svelte CLIP Image Search

A SvelteKit UI for a CLIP-based image search backend. 

## My first attempt at a SvelteKit based UI.

This project uses the [same FastAPI backend for CLIP-based image search](ramayer/rclip-server) as my earlier Vue-based UI found [here](https://github.com/ramayer/rclip-server/blob/main/assets/rclip_server.html).

## Demo

A demo of this UI, using Wikimedia Commons images, can be [seen here](http://image-search.0ape.com/).

Try searching for somethign like [skiing -summer +winter](http://image-search.0ape.com/?q=skiing%20%2Bsummer%20-winter) to see sports that are kinda-like skiing, but happen in summer instead of winter.

## Features:

* Incremental loading of thumbnails, with support for throttled image sources like Wikipedia (that only lets a single client load a few thumbnails a second).
* Flicker-free previews based on [Svelte deferred transitions](https://svelte.dev/examples/deferred-transitions) to not render partially-downloaded images.
* Fast previews based by initially showing a zoomed thumbnail, then fading into the full res image when its available.

* A search syntax that lets you do simple math on CLIP embeddings with prefixes like "-" to subtract CLIP vectors and "+" to add them.
 
  * [zebra -stripes +spots](http://image-search.0ape.com/search?q=zebra%20-stripes%20%2Bspots) \- Animals that look kinda like zebras but with spots instead of stripes.
  * [zebra -mammal +fish](http://image-search.0ape.com/search?q=zebra%20-mammal%20%2Bfish) \- Animals that look like zebras but fish instead of mammals.
  * [zebra -animal +car](http://image-search.0ape.com/search?q=zebra%20-animal%20%2Bcar) \- Objects colored like zebras but more cars than animals.
  * [zebra -"black and white"](http://image-search.0ape.com/search?q=zebra%20-%22black%20and%20white%22) \- Baby zebras (brown & white) and a Greater Kudu (a brown & white striped 4-legged animal). Of course you could also find the same baby zebra searching for [zebra -big +small](http://image-search.0ape.com/search?q=zebra%20-big%20%2Bsmall) or even more simply, just [baby zebra](http://image-search.0ape.com/search?q=baby%20zebra).
  * [furry black and white striped animal](http://image-search.0ape.com/search?q=furry%20black%20and%20white%20striped%20animal) \- zebras, lemurs, and other furry black and white animals.
  * [striped horse-like animal](http://image-search.0ape.com/search?q=striped%20horse-like%20animal) \- more zebras (and horses with stripes)
  * [zebra habitat -zebra](http://image-search.0ape.com/search?q=zebra%20habitat%20-zebra) \- places that look like somewhere a zebra might live

* Search for similar images

  * It can also do a search based on the difference between the CLIP embeddings of two images directly.  For example, CLIP considers [this image of a spider on a purple flower](http://image-search.0ape.com/search?q=%7B%22image_id%22%3A28754%7D) minus [this image of the same kind of spider on a white flower](http://image-search.0ape.com/search?q=%7B%22image_id%22%3A174054%7D) to be [this set of pictures which is mostly purple flowers without the spider](http://image-search.0ape.com/search?q=%7B%22image_id%22%3A28754%7D%20-%7B%22image_id%22%3A174054%7D).


## Thanks

Special Thanks to: 

* Github user @yurijmikhalevich for his [rclip](https://github.com/yurijmikhalevich/rclip) CLI tools that inspired this project and are now used to manage all my home photos.
* Github user @berkinakkaya for his [svelte-image-gallery](https://github.com/berkinakkaya/svelte-image-gallery) project that made me interested in porting the front-end to Svelte, (and whose code I used, though I need to double-check with him about licensing.... doing that now)

## TODO

* push some of the heavy lifting to the browser; especially to process images from webcams; possibly using this: https://github.com/josephrocca/openai-clip-js