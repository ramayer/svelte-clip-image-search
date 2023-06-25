import type {PageServerLoad} from './$types';

console.log("============== +page.server.ts")


async function query_backend(q:string) {
    let base_url = 'http://localhost:8000/similar_images/?';
    let params = new URLSearchParams({
        q: q
    })
    let url = 'http://localhost:8000/similar_images/1';
    let resp:number[][][] = await fetch(url).then((r) => {
        if (r.ok) {
            return r.json()
        } else {
            return [[[0,0],[0,0]]]
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
       let ids = (await result)[0].map((x)=> x[1])
       console.log("here ids",ids)
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