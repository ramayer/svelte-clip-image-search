import { writable } from 'svelte/store';

export const preview_store = writable(0);
export const detail_store  = writable(0);
export const cols_store  = writable(4);
export const q_store     = writable("");
export const thm_size_store  = writable(240);

