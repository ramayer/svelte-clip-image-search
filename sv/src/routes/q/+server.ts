import { error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import config from '../config';
import { json } from '@sveltejs/kit';
import type { RequestEvent } from "./$types";

interface ResponseData {
    imgids: number[];
    scores: number[];
    target: number[];
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
    let default_resp: ResponseData = { imgids: [], scores: [], target: [] }

    try {
        let resp1 = await fetch(search_url)
        if (resp1.ok) {
            const j = await resp1.json()
            let resp = { 
                imgids: j?.imgids || [], 
                scores: j?.scores || [],
                target: j?.target || [],
            }
            return json(resp);
        } else {
            return (json(default_resp, { status: 500 }))
        }
    } catch (error) {
        return (json(default_resp, { status: 500 }))
    }
}) satisfies RequestHandler;

// TODO - consider preprocessing tiny thumbnails to data urls like
// https://stackoverflow.com/questions/71529104/how-to-convert-sveltekit-fetch-response-to-a-buffer

export async function POST({ request } : RequestEvent) 
{
    const dataobject : any = await request.json();
    console.log('dataobject is ',dataobject.src, ' with data of ',dataobject.data_uri.length)

    let base_url = config.app_uri + '/handle_webcam_image';
    const response = await fetch(base_url, {
        method: "POST",
        body: JSON.stringify(dataobject),
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
        }
    });
    if (response.ok) {
        const j = await response.json()
        console.log("ok and j is ",j)
        return (json(j, { status: 200 }))
    }
    return json({"body":response.body}, { status: 200 })
}
