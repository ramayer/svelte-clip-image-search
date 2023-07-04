import { readable } from 'svelte/store';
import { browser } from "$app/environment"; // for infinite scroll

export default readable({x:0, y:0}, (set: (arg0: { x: any; y: any; }) => void) => {

	if (!browser) {
		return;
	}
	
	document.body.addEventListener("mousemove", move);
	
	function move(event: { clientX: any; clientY: any; }) {
		set({
			x: event.clientX,
			y: event.clientY,
		});
	}
	
	return () => {
		document.body.removeEventListener("mousemove", move);
	}
})