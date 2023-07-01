# TODOs

## api

* Scale embedding vectors so they can be transmitted more compactly (int8 is almost enough precision; maybe 10-bit (+/- 1024) that has a compact json representation for the JSON apis. 

## UI

* merge the feature that blends thumbnails with the high-res image during loading.


## Storage

* Only convert some of the ML model results to float16 before storing on disk.  Some should stay ints, others should stay 32-bit.
* Store separate thm indexes for faces?
* Store a text embedding.
