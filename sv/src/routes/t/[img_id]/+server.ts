import { error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import config from '../../config';


export const GET = (async ({ setHeaders, url, params }) => {
    const w = url.searchParams.get('w');
    const h = url.searchParams.get('h');
    const img_id = params.img_id;

    //console.log("t",img_id,params)
    //try {
        // Use a different backend server for thumbnails than
        // the rest of the API endpoints, because thumbnails
        // are performance constrained (10ms matters) so 
        // prefer a uvicorn server with dozens of backends;
        // while other endpoints are RAM contrained and would
        // be expensive to run with dozens of backends.
        const img_url_base = `${config.thm_uri}/thm/${img_id}`
        const img_url = (w || h) ? img_url_base + '?' + (w?"w="+w:"") + (h?"&h="+h:""): img_url_base

        const img_res = await fetch(img_url)
        const img_abuf = await img_res.arrayBuffer();
        const img_ct = img_res.headers.get('Content-Type');
        const hdrs = {
            //'Content-Type': 'text/plain',
            'Content-Type': img_ct ?? 'image/webp',
            'Content-Length': img_abuf.byteLength.toString(),
            //'Last-Modified': new Date(img.lastModified).toUTCString(),
            'Last-Modified': new Date(0).toUTCString(),
            'Cache-Control': 'public, max-age=600'
        }
        const debug_no_cache_hdrs = {
            //'Content-Type': 'text/plain',
            'Content-Type': img_ct ?? 'image/webp',
            'Content-Length': img_abuf.byteLength.toString(),
            //'Last-Modified': new Date(img.lastModified).toUTCString(),
            'Last-Modified': new Date(0).toUTCString(),
            'Cache-Control': 'public, max-age=0'
        }
        
        //console.log(img_res)
        //const img_buf = Buffer.from(new Uint8Array(img_abuf));
        setHeaders(hdrs);
        //return new Response(String(img_id))
        return new Response(img_abuf)

    // } catch (e) {
    //     throw error(500, "Internal server error")
    // }

}) satisfies RequestHandler;

// TODO - consider preprocessing tiny thumbnails to data urls like
// https://stackoverflow.com/questions/71529104/how-to-convert-sveltekit-fetch-response-to-a-buffer