import type {PageServerLoad} from './$types';

console.log("============== +page.server.ts")
export const load = (async (event) => {
    console.log("============== +page.server.ts load")
    const q = event.url.searchParams.get('q');
    const start = 6500 // Math.floor(Math.random() * 100) * 100;
    console.log('q',q);
    return {
        q: q,
        ids: [...Array(21).keys()].map((x)=>x+start),
    }
}) satisfies PageServerLoad;