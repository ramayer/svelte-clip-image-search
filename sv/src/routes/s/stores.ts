import { writable } from 'svelte/store';

export const selected_img   = writable("");
export const selected_state = writable(0);
export const cols_store     = writable(4);
