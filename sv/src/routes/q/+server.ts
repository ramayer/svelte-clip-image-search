import { error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import config from '../config';
import { json } from '@sveltejs/kit';

interface ResponseData {
    imgids: number[];
    scores: number[];
}

export const GET = (async ({ setHeaders, url, params, fetch }) => {
    const q = url.searchParams.get('q');

    const hdrs = {
        //'Content-Type': 'application/json',
        //'Last-Modified': new Date(img.lastModified).toUTCString(),
        'Last-Modified': new Date(0).toUTCString(),
        'Cache-Control': 'public, max-age=600'
    }
    setHeaders(hdrs);

    let base_url = config.app_uri + '/search?';
    let search_params = new URLSearchParams({
        q: q || ''
    })
    let search_url = base_url + search_params;
    let resp1 = await fetch(search_url)
    let resp: ResponseData = { imgids: [1, 2, 3], scores: [3, 2, 1] }
    if (resp1.ok) {
        const j = await resp1.json()
        resp = { imgids: j.imgids, scores: j.scores }
        return json(resp);
    } else {
        throw error(500, `Internal server error ${resp1.statusText}` )
    }

}) satisfies RequestHandler;

// TODO - consider preprocessing tiny thumbnails to data urls like
// https://stackoverflow.com/questions/71529104/how-to-convert-sveltekit-fetch-response-to-a-buffer