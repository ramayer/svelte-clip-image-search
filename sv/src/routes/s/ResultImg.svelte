<script lang="ts">
    export let img_id:number;
</script>

<div>
    <img alt={"" + img_id} src="http://localhost:8000/thm/{img_id}" />
    {img_id}<br />
</div>
