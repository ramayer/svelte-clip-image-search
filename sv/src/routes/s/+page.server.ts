import type {PageServerLoad} from './$types';
import config from '../config';

console.log("============== +page.server.ts")

interface MetadataResponseData extends Record<string,any> {}

interface ResponseData {
    imgids: number[];
    scores: number[];
    metadata: MetadataResponseData;
}
  
async function query_backend(q:string) {
    let base_url = config.app_uri + '/search/?';
    let params = new URLSearchParams({
        q: q
    })
    let url = base_url + params;
    let resp:ResponseData = await fetch(url).then((r) => {
        if (r.ok) {
            return r.json()
        } else {
            return {imgids:[1,2,3],scores:[3,2,1]}
        }
    })
    console.log('query_backend for ',url,' returned ',resp.imgids.length, ' results')
    return resp;
}

async function get_metadata(img_id:number) {
    const m_url = `${config.app_uri}/met/${img_id}`
    let resp:MetadataResponseData = await fetch(m_url).then((r) => {
        if (r.ok) {
            return r.json()
        } else {
            return {}
        }
    })
    console.log('query_backend for ',m_url,' returned ',resp, ' results')
    return resp;
}

export const load = (async (event) => {
    console.log("============== +page.server.ts load")
    const q = event.url.searchParams.get('q');
    const d = event.url.searchParams.get('d');
    const start = 6500  *0// Math.floor(Math.random() * 100) * 100;
    let details = null
    console.log('querying backend for q=',q);
    if (q) {
       let result = query_backend(q)
       let ids = (await result).imgids
       if (d) {
         details = get_metadata(parseInt(d))
       }
       // console.log("here ids",ids)
       return {
            q: q,
            ids: ids,
            details: details
        }
    }
    return {
        q: q,
        ids: [...Array(101).keys()].map((x)=>x+start),
    }
}) satisfies PageServerLoad;