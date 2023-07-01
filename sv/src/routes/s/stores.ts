import { writable } from 'svelte/store';

export const preview_img = writable(0);
export const detail_img  = writable(0);
export const cols_store  = writable(4);
export const q_store     = writable("");
