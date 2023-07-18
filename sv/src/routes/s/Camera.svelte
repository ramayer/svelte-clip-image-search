<script lang="ts">
    /*
        https://webrtchacks.com/still-image-from-webcam-stream-approaches/
        https://github.com/tensorflow/tfjs-models/tree/master/face-landmarks-detection
        https://storage.googleapis.com/tfjs-models/demos/face-landmarks-detection/index.html?model=mediapipe_face_mesh
        https://github.com/microsoft/onnxruntime-inference-examples/tree/main/js/quick-start_onnxruntime-web-bundler
        https://github.com/josephrocca/openai-clip-js
        https://github.com/ml5js/ml5-library
        https://editor.p5js.org/p5/sketches/Sound:_FFT_Spectrum
    */
    import { onMount, tick } from "svelte";
    import { onDestroy } from "svelte";
    import { goto } from "$app/navigation";

    let stream: MediaStream | null;
    let videoRef: HTMLVideoElement;
    let img_canvas: HTMLCanvasElement;

    onMount(() => {
        getStream();
    })

    onDestroy(() => {
        stopStream()
    })
    
    async function getStream() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: false,
            });
            await tick;
            videoRef.srcObject = stream;
            console.log(stream.getTracks()[0]);
        } catch (err) {
            console.error(err);
        }
    }

    async function stopStream() {
        if (!stream) {
            return;
        }
        stream.getTracks().forEach((track) => track.stop());
        videoRef.srcObject = null;
    }

    async function getFrame() {
        if (!videoRef) {
            return;
        }
        const bitmap = await createImageBitmap(videoRef);

        console.log("here bitmap is ", bitmap);
        const ctx = img_canvas.getContext("bitmaprenderer");
        console.log("here canvas is ", img_canvas);
        img_canvas.width = bitmap.width;
        img_canvas.height = bitmap.height;
        
        ctx?.transferFromImageBitmap(bitmap);

        const compressedDataUrl = img_canvas.toDataURL("image/jpeg", 0.8);
        const response = await fetch("/q", {
            method: "POST",
            body: JSON.stringify({data_uri:compressedDataUrl,src:'cam'})
        });
        if (response.ok) {
            const j = await response.json()
            console.log("in getframe's response j is ",j)
            let params = new URLSearchParams({ q: 'clip:'+JSON.stringify(j.embs)});
            goto("?" + params);
        }
    }

    /*

    let startBtn ;
    let stopBtn;
    let hideVid;
    let intervalSec ;
    let videoElem ;
    let imageCountSpan ;
    let imagesDiv;

    const storage: ImageBitmap[] = []; // Use this array as our database
    let stream: MediaProvider | null, captureInterval: number | undefined;

    onMount(() => {
        startBtn = document.querySelector("button#start");
        stopBtn = document.querySelector("button#stop");
        hideVid = document.querySelector("input#hideVid");
        videoElem = document.querySelector("video");
        imageCountSpan = document.querySelector("span#image_count");
        imagesDiv = document.querySelector("div#images");

        if (!startBtn || !hideVid || !videoElem || !intervalSec) {
            return;
        }
    });

    //const hideVid_onclick = () => (videoElem.hidden = hideVid.checked);
    const startBtn_onclick = async () => {

        if (!(startBtn && videoElem && videoElem)) {
            return;
        }

        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        videoElem.onplaying = () =>
            console.log("video playing stream:", videoElem?.srcObject);
        videoElem.srcObject = stream;

        const interval = 1000;

    };

*/

    /*

    captureInterval = setInterval(async () => {
            if (!videoElem) {return}
            const bitmap = await createImageBitmap(videoElem);
            console.log("here bitmap is "+bitmap);
            storage.push(bitmap);
            //imageCountSpan.innerText++;
        }, interval);



const stopBtn_onclick = () => {

        if (!stream) {
            return;
        }
        // stop capture
        clearInterval(captureInterval);

        // close the camera
        stream.getTracks().forEach((track: { stop: () => any; }) => track.stop());

        // Display each image
        async function showImages() {
            const bitmap = storage.shift();
            const width = bitmap.width;
            const height = bitmap.height;

            console.log(bitmap);
            const canvas = document.createElement("canvas");
            canvas.width = width;
            canvas.height = height;
            const ctx = canvas.getContext("bitmaprenderer");
            ctx.transferFromImageBitmap(bitmap);
            imagesDiv.appendChild(canvas);

            if (storage.length > 0) await showImages();
        }
        console.log("stored images");
        showImages();
    };
    */
</script>
{#if stream}
<section class="container mx-auto px-4 flex">
    <!-- svelte-ignore a11y-media-has-caption -->
    <video
        class="mt-4 rounded-sm"
        style="max-width:100px; max-height:100px; object-fit: contain;"
        width="320"
        height="240"
        autoplay={true}
        bind:this={videoRef}
    />
    <button
        class="rounded-sm bg-slate-600 text-white px-2 py-1"
        on:click={getFrame}>Search for Image</button
    >
    <canvas id="output" bind:this={img_canvas} style="max-width:100px; max-height:100px;    object-fit: contain;"/>
</section>

{/if}
