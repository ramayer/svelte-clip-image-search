// import type { PageServerLoad } from './$types';
import type { PageLoad } from './$types';
import config from '../config';
import { error } from '@sveltejs/kit';

console.log("============== +page.ts")

// TODO - set better typing in python and here.
interface MetadataResponseData extends Record<string, any> { }

interface ResponseData {
    imgids: number[];
    scores: number[];
    details: MetadataResponseData;
}

export const load = (async ({ url, setHeaders, fetch }) => {

    console.log("============== +page.ts load for ", url.searchParams)
    const q = url.searchParams.get('q');
    const ds = url.searchParams.get('d');
    const d = ds ? parseInt(ds) : undefined;
    const search_url = "/q?" + new URLSearchParams({ q: q || '' });
    const details = d ? await (await fetch(`/m/${d}`)).json() : undefined
    const q_results = await (await fetch(search_url)).json()

    setHeaders({
        'Last-Modified': new Date(0).toUTCString(),
        'Cache-Control': 'public, max-age=600',
    });
    // TOOD - IIRC there's some trick to make the slower parts async
    // by returning promises?
    if (d) {
        return {
            q: q,
            d: d,
            ids: q_results.imgids,
            details: details
        }
    } else {
        return {
            q: q,
            ids: q_results.imgids,
        }
    }

}) satisfies PageLoad;