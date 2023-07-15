// import type { PageServerLoad } from './$types';
import type { PageLoad } from './$types';

import { redirect } from '@sveltejs/kit';

export const load = (async ({ url, setHeaders, fetch }) => {

    console.log("============== +page.ts load for ",url.searchParams)
    const q = url.searchParams.get('q');
    if (q) {
        throw redirect(301, 's?'+url.searchParams);
    }

}) satisfies PageLoad;