# TODOs


* Fix [mypy and/or pylama and/or pyre-check and/or pyright and/or pytype warnings](https://inventwithpython.com/blog/2022/11/19/python-linter-comparison-2022-pylint-vs-pyflakes-vs-flake8-vs-autopep8-vs-bandit-vs-prospector-vs-pylama-vs-pyroma-vs-black-vs-mypy-vs-radon-vs-mccabe/)

## Ideas

* quantify errors from encoding normalized vectors as int(999*max(abs(x))).
* or better, as base64 versions of that.

* Clip5 or Clip10 - test if it's worth the disk space and/or RAM.

* GIS

* Text

* remove deprecated pieces 

## api

* Scale embedding vectors so they can be transmitted more compactly
  (int8 is almost enough precision; maybe 10-bit (+/- 1024) that has a
  compact json representation for the JSON apis. [Done]

* Make /d a top-level page focused on an image.

## UI/UX

* safe-offset-right needed on horizontal phones

* Nginx rate limit, [Done]

  * burst with nodelay https://www.nginx.com/blog/rate-limiting-nginx/
  * large_client_header_buffers 16 16k; // search for a text clip vector

* support video

* suppport both openclip and lion's bigger models

* merge the feature that blends thumbnails with the high-res image
  during loading. [Done]

* mobile phones have no mouseover events, so perhaps use a single
  click to emulate mouseover.  (touch start may be even better)

* this gallery makes better use of space for its details:
  https://rob-sheridan.com/highlights/1

## Storage

* Only convert some of the ML model results to float16 before storing on disk.  Some should stay ints, others should stay 32-bit.
* Store separate thm indexes for faces?
* Store a text embedding.
* TMDB: https://developer.themoviedb.org/reference/movie-images

## Bugs

* The URLs in the result images need to get their 'q' parameter from
  the result data. There's a race condition if getting from the url or
  the store. [Done]

* DONE: Height and width are backwards in the indexer.  Only fix it at the
  same time that data is migrated.

* Broken thumbnails: http://localhost:5173/s?q=clip%3A160854

* Some wikimedia thumbnails are 100s of times wider than tall or taller than wide; tweak the thumbnail logic.

* OOM

FATAL ERROR: Reached heap limit Allocation failed - JavaScript heap out of memory
 1: 0xb675b4 node::Abort() [node]
 2: 0xa8afbc void node::FPrintF<>(_IO_FILE*, char const*) [node]
 3: 0xd3ac00 v8::Utils::ReportOOMFailure(v8::internal::Isolate*, char const*, bool) [node]
 4: 0xd3add0 v8::internal::V8::FatalProcessOutOfMemory(v8::internal::Isolate*, char const*, bool) [node]
 5: 0xf1935c  [node]
 6: 0xf2b2fc v8::internal::Heap::CollectGarbage(v8::internal::AllocationSpace, v8::internal::GarbageCollectionReason, v8::GCCallbackFlags) [node]
 7: 0xf96458 v8::internal::ScavengeJob::Task::RunInternal() [node]
 8: 0xe145a0 non-virtual thunk to v8::internal::CancelableTask::Run() [node]
 9: 0xbca134  [node]
10: 0xbcd568 node::PerIsolatePlatformData::FlushForegroundTasksInternal() [node]
11: 0x15df7ec  [node]
12: 0x15f1928  [node]
13: 0x15e0254 uv_run [node]
14: 0xab8fe8 node::SpinEventLoop(node::Environment*) [node]
15: 0xba6bf8 node::NodeMainInstance::Run() [node]
16: 0xb27458 node::LoadSnapshotDataAndRun(node::SnapshotData const**, node::InitializationResult const*) [node]
17: 0xb2ac34 node::Start(int, char**) [node]
18: 0xfffc05eb46a4 __libc_start_main [/lib64/libc.so.6]
19: 0xab75b8  [node]


* document npm build process.  Something like:

    export IEI_PATH=$HOME/data/wikipedia.iei/
    export IEI_USER_AGENT="[your user agent]"
    (cd iei; nohup uvicorn --reload image_embedding_indexer_api:app --port=8001) &
    # (cd sv; nohup npm run dev -- --host=127.0.0.1 --port=5172 )&
    # (cd sv; nohup env PORT=5172 node build/index.js > node.out 2>&1) &
    (cd sv; npm run build)
    (cd sv; nohup env PORT=5172 pm2 start build/index.js > node.out 2>&1) &



* consider pm2 for restarting after memory leaks

  https://pm2.keymetrics.io/

