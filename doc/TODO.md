# TODOs

## Ideas

* quantify errors from encoding normalized vectors as int(999*max(abs(x))).
* or better, as base64 versions of that.


## api

* Scale embedding vectors so they can be transmitted more compactly
  (int8 is almost enough precision; maybe 10-bit (+/- 1024) that has a
  compact json representation for the JSON apis.

## UI/UX

* Nginx rate limit,

  * burst with nodelay https://www.nginx.com/blog/rate-limiting-nginx/
  * large_client_header_buffers 16 16k; // search for a text clip vector

* support video

* merge the feature that blends thumbnails with the high-res image
  during loading.

* mobile phones have no mouseover events, so perhaps use a single
  click to emulate mouseover.  (touch start may be even better)

* this gallery makes better use of space for its details:
  https://rob-sheridan.com/highlights/1

## Storage

* Only convert some of the ML model results to float16 before storing on disk.  Some should stay ints, others should stay 32-bit.
* Store separate thm indexes for faces?
* Store a text embedding.

## Bugs

* The URLs in the result images need to get their 'q' parameter from
  the result data. There's a race condition if getting from the url or
  the store.

* DONE: Height and width are backwards in the indexer.  Only fix it at the
  same time that data is migrated.

* Broken thumbnails: http://localhost:5173/s?q=clip%3A160854

* Some wikimedia thumbnails are 100s of times wider than tall or taller than wide; tweak the thumbnail logic.