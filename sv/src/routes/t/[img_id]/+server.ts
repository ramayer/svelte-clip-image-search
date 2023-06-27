import { error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import config from '../../config';


export const GET = (async ({ setHeaders, url, params }) => {

    const w = Number(url.searchParams.get('w'));
    const h = Number(url.searchParams.get('h'));
    const img_id = params.img_id;
    //console.log("t",img_id,params)
    //try {
        //const img_url = 'https://picsum.photos/302'
        //const img_url = `http://192.168.12.110:8000/thm/${img_id}`
        const img_url = `${config.app_uri}/thm/${img_id}`

        const img_res = await fetch(img_url)
        const img_abuf = await img_res.arrayBuffer();
        const img_ct = img_res.headers.get('content-type')
        //console.log(img_res)
        //const img_buf = Buffer.from(new Uint8Array(img_abuf));
        setHeaders({
            //'Content-Type': 'text/plain',
            'Content-Type': img_ct ?? 'image/webp',
            'Content-Length': img_abuf.byteLength.toString(),
            //'Last-Modified': new Date(img.lastModified).toUTCString(),
            'Last-Modified': new Date(0).toUTCString(),
            'Cache-Control': 'public, max-age=600'
        });
        //return new Response(String(img_id))
        return new Response(img_abuf)

    // } catch (e) {
    //     throw error(500, "Internal server error")
    // }

}) satisfies RequestHandler;

// TODO - consider preprocessing tiny thumbnails to data urls like
// https://stackoverflow.com/questions/71529104/how-to-convert-sveltekit-fetch-response-to-a-buffer