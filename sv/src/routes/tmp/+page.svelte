<script>
    let w=3;
    let h=4;
</script>

<div class="c0">
    <div class="c1" style="aspect-ratio: {w}/{h};">
        <div class="c2" style="aspect-ratio: {w}/{h};">
            hi
        </div>
    </div>
</div>
<style>
    .c0 {
        border: 1px solid blue;
        width: 80vw;
        height: 80vh;
        background: white;
        margin: 30px;
        display:flex;
        align-items: center;
        justify-content: center;
    }
    .c1 {
        border: 1px solid green;
        max-width: 100%;
        height: 100%;
        display:flex;
        flex-direction: column;
        flex-shrink: 1;
        align-items: center;
        justify-content: center;

    }
    .c2 {
        border: 1px solid red;
        max-height: 100%;
        width:100%;
        flex-shrink: 1;
        align-items: center;

    }

</style>