<script lang="ts">
    import * as Three from "three";
    import { T } from "@threlte/core";
    import { watch } from "@threlte/core";
    import { Grid } from "@threlte/extras";
    import { OrbitControls } from "@threlte/extras";
    import { useTexture } from "@threlte/extras";
    import { randFloat } from "three/src/math/MathUtils";

    // Note, NPM buid may fail with:
    // https://stackoverflow.com/questions/68462419/three-js-breaks-when-trying-to-import-orbitcontrols-js


    //// Note that useTexture is much cleaner than useLoader(TextureLoader)
    // 
    // const mytexture = useTexture("/t/1");
    // $: console.log("tex", $mytexture); // eventually THREE.Texture
    //
    //// vs 
    // 
    // import { useLoader } from "@threlte/core";
    // import { TextureLoader } from "three";
    // const { load } = useLoader(TextureLoader);
    // function get_tex(path:string) {
    //     load(path).then((tex)=>{
    //         tex.colorSpace = Three.SRGBColorSpace;
    //     })
    // }

    function fixcolorspace(cs: Three.Texture | undefined) {
        if (cs) {
            console.log("fixing colorspace for ", cs);
            cs.colorSpace = Three.SRGBColorSpace;
        } else {
            console.log("can't fix cs");
        }
    }

    /* 
      lazily load textures, and fix their colorspace, before
      putting them in the array of textures.
    */
    let nboxes = 100;
    let texids = Array.from({ length: nboxes }, (x, i) => i);
    let texes: (Three.Texture | undefined)[] = Array.from({ length: nboxes });

    texids.map((texid) => {
        const ut = useTexture("/t/" + texid);
        watch(ut, (t) => {
            fixcolorspace(t);
            texes[texid] = t;
        });
        return ut;
    });

    let boxen = Array(nboxes)
        .fill(0)
        .map((x) => {
            let p = [randFloat(-10, 10), randFloat(1, 1.1), randFloat(-10, 10)];
            let dp = [randFloat(-0.01, 0.01), 0, randFloat(-0.01, 0.01)];
            return { p: p, dp: dp };
        });

    setInterval(() => {
        boxen.forEach((box) => {
            box.p[0] += box.dp[0];
            box.p[1] += box.dp[1];
            box.p[2] += box.dp[2];
            if (box.p[0] > 10) box.dp[0] -= 0.001;
            if (box.p[1] > 10) box.dp[1] -= 0.001;
            if (box.p[2] > 10) box.dp[2] -= 0.001;
            if (box.p[0] < -10) box.dp[0] += 0.001;
            if (box.p[1] < -10) box.dp[1] += 0.001;
            if (box.p[2] < -10) box.dp[2] += 0.001;
        });
        boxen = boxen;
    }, 0.03);
</script>

<T.PerspectiveCamera
    makeDefault
    position={[0, 10, 20]}
    fov={36}
    target={[0, 0, 0]}
>
    <OrbitControls />
</T.PerspectiveCamera>

<Grid
    axes={"xzy"}
    cellColor={"#000077"}
    cellSize={1}
    cellThickness={1}
    sectionColor={"#0000cc"}
    sectionSize={10}
    sectionThickness={2}
    followCamera={false}
    infiniteGrid={true}
    fadeDistance={100}
    fadeStrength={0.5}
    gridSize={[1, 10]}
/>


{#each { length: nboxes } as _h, x}
    {#if texes[x]}
        {#await useTexture("/t/2") then value}
            <T.Mesh position={boxen[x].p}>
                <T.BoxGeometry />
                <T.MeshBasicMaterial map={texes[x]} />
            </T.Mesh>
        {/await}
    {/if}
{/each}
