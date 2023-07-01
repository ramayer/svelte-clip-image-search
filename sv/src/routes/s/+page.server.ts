import type {PageServerLoad} from './$types';
import config from '../config';


console.log("============== +page.server.ts")

interface ResponseData {
    imgids: number[];
    scores: number[];
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
    console.log('query_backend for ',url,' returned ',resp)
    return resp;
}

export const load = (async (event) => {
    console.log("============== +page.server.ts load")
    const q = event.url.searchParams.get('q');
    const start = 6500  *0// Math.floor(Math.random() * 100) * 100;
    console.log('q',q);
    if (q) {
       let result = query_backend(q)
       let ids = (await result).imgids
       // console.log("here ids",ids)
       return {
            q: q,
            ids: ids,
        }
    }
    return {
        q: q,
        ids: [...Array(101).keys()].map((x)=>x+start),
    }
}) satisfies PageServerLoad;