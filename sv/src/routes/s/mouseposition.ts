import { readable } from 'svelte/store';

export default readable({x:0, y:0}, (set: (arg0: { x: any; y: any; }) => void) => {
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