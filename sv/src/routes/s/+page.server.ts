import type { PageServerLoad } from './$types';
import config from '../config';

console.log("============== +page.server.ts")

// TODO - set better typing in python and here.
interface MetadataResponseData extends Record<string, any> { }

interface ResponseData {
    imgids: number[];
    scores: number[];
    details: MetadataResponseData;
}

async function query_backend(q: string) {
    let base_url = config.app_uri + '/search/?';
    let params = new URLSearchParams({
        q: q
    })
    let url = base_url + params;
    let resp: ResponseData = await fetch(url).then((r) => {
        if (r.ok) {
            return r.json()
        } else {
            return { imgids: [1, 2, 3], scores: [3, 2, 1] }
        }
    })
    console.log('query_backend for ', url, ' returned ', resp.imgids.length, ' results')
    return resp;
}

async function get_metadata(img_id: number) {
    const m_url = `${config.app_uri}/met/${img_id}`
    let resp: MetadataResponseData = await fetch(m_url).then((r) => {
        if (r.ok) {
            return r.json()
        } else {
            return {}
        }
    })
    console.log('query_metadata for ', m_url, ' returned ', resp, ' results')
    return resp;
}

export const load = (async (event) => {
    console.log("============== +page.server.ts load")
    const q = event.url.searchParams.get('q');
    const ds = event.url.searchParams.get('d');
    const d = ds ? parseInt(ds) : undefined;
    const details = d ? await get_metadata(d) : undefined
    console.log('querying backend for q=', q, ' d=', d);
    if (q) {
        let result = query_backend(q)
        let q_results = await result
        let ids = q_results.imgids
        return {
            q: q,
            d: d,
            ids: ids,
            details: details
        }
    }
    return {
        q: q,
        d: d,
        ids: [...Array(1001).keys()].map((x) => x + 1),
        details: details
    }
}) satisfies PageServerLoad;