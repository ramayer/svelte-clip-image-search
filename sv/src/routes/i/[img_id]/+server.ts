import { error } from '@sveltejs/kit';
import config from '../../config';
import type { RequestHandler } from './$types';

export const GET = (async ({ setHeaders, url, params }) => {
    console.log('i',url.href)
    const w = Number(url.searchParams.get('w'));
    const h = Number(url.searchParams.get('h'));
    const img_id = params.img_id;
    //console.log("t",img_id,params)
    //try {
    //const img_url = 'https://picsum.photos/302'
    //const img_url = `http://192.168.12.110:8000/thm/${img_id}`
    //const img_url = config.app_uri + `/img/${img_id}`
    const img_url = config.thm_uri + `/img/${img_id}`

    const img_res = await fetch(img_url, { redirect: 'manual' })
    //console.log('i',img_res)
    const loc = img_res.headers.get('Location');
    if (loc) {
        setHeaders({
            'Last-Modified': new Date(0).toUTCString(),
            'Cache-Control': 'public, max-age=600',
            'Location': loc
        });
        //return new Response(String(img_id))
        return new Response("redirect", { status: 301 });
    } else {
        const img_abuf = await img_res.arrayBuffer();
        const img_ct = img_res.headers.get('content-type')

        // TODO - consider checking timing info here.
        // https://www.w3.org/TR/resource-timing/
        // https://fetch.spec.whatwg.org/
        // img_res has that info in a timing struct
        // console.log('i',img_res)

        //console.log(img_res)
        //const img_buf = Buffer.from(new Uint8Array(img_abuf));
        setHeaders({
            'Content-Type': img_ct ?? 'image/webp',
            'Content-Length': img_abuf.byteLength.toString(),
            //'Last-Modified': new Date(img.lastModified).toUTCString(),
            'Last-Modified': new Date(0).toUTCString(),
            'Cache-Control': 'public, max-age=600',
        });
        return new Response(img_abuf)
    }

    // } catch (e) {
    //     throw error(500, "Internal server error")
    // }

}) satisfies RequestHandler;

// TODO - consider preprocessing tiny thumbnails to data urls like
// https://stackoverflow.com/questions/71529104/how-to-convert-sveltekit-fetch-response-to-a-buffer