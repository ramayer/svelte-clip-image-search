import { error } from '@sveltejs/kit';
import config from '../../config';
import type { RequestHandler } from './$types';

export const GET = (async ({ setHeaders, url, params }) => {

    const w = Number(url.searchParams.get('w'));
    const h = Number(url.searchParams.get('h'));
    const img_id = params.img_id;
    //console.log("t",img_id,params)
    try {
        //const img_url = 'https://picsum.photos/302'
        //const img_url = `http://192.168.12.110:8000/thm/${img_id}`
        const img_url = config.app_uri + `/det/${img_id}`

        const img_res = await fetch(img_url, { redirect: 'manual' })
        let loc = img_res.headers.get('Location');
        if (!loc) {
            loc = "/i/" + img_id;
        }
        setHeaders({
            'Last-Modified': new Date(0).toUTCString(),
            'Cache-Control': 'public, max-age=600',
            'Location': loc
        });
        //return new Response(String(img_id))
        return new Response("redirect", { status: 301 });

    } catch (e) {
        throw error(500, "Internal server error")
    }

}) satisfies RequestHandler;

// TODO - consider preprocessing tiny thumbnails to data urls like
// https://stackoverflow.com/questions/71529104/how-to-convert-sveltekit-fetch-response-to-a-buffer