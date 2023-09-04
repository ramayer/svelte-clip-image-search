<script lang="ts">
    import { T } from "@threlte/core";
    import { OrbitControls } from "@threlte/extras";
    import { Grid } from "@threlte/extras";
    //import { THREE } from "three"

    import * as Three from "three";

    import { useTexture } from "@threlte/extras";
    import { watch } from "@threlte/core";
    const mytexture = useTexture("/t/1");
    $: console.log("tex", $mytexture); // eventually THREE.Texture
    import { useLoader } from "@threlte/core";
    import { TextureLoader } from "three";
    const { load } = useLoader(TextureLoader);

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
    // this works
    $: fixcolorspace($mytexture)
    */
    let myactualtexture: Three.Texture | undefined;

    watch(mytexture, (t) => {
        fixcolorspace(t);
        myactualtexture = t;
    });

    let nboxes = 100;
    let texids = Array.from({ length: nboxes }, (x, i) => i);
    let texes = Array.from({ length: nboxes });
    texids.map((texid) => {
        const ut = useTexture("/t/" + texid);
        watch(ut, (t) => {
            fixcolorspace(t);
            texes[texid] = t;
        });
        return ut;
    });

    import { BoxGeometry } from "three";
    import { randFloat } from "three/src/math/MathUtils";
    const boxColors = [
        "#3c42c4",
        "#6e51c8",
        "#a065cd",
        "#ce79d2",
        "#d68fb8",
        "#dda2a3",
        "#eac4ae",
        "#f4dfbe",
    ];

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

<!-- Make a box in every second cell to show aligment -->
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
{#await mytexture then value}
    <T.Mesh>
        <T.BoxGeometry />
        <T.MeshBasicMaterial map={value} />
    </T.Mesh>
{/await}

{#await mytexture then value}
    <T.Mesh position={[5, 2, 3]}>
        <T.SphereGeometry />
        <T.MeshBasicMaterial map={value} />
    </T.Mesh>
{/await}
{#if myactualtexture}
    <T.Mesh position={[5, 5, 3]}>
        <T.SphereGeometry />
        <T.MeshBasicMaterial map={myactualtexture} />
    </T.Mesh>
{/if}

{#each { length: nboxes } as _h, x}
{#if texes[x]}
    {#await useTexture("/t/2") then value}
        <T.Mesh position={boxen[x].p}>
            <T.BoxGeometry />
            <T.MeshBasicMaterial map={texes[x]} />
        </T.Mesh>
    {/await}
{/if}
    {#if false}
        {#await mytexture then value}
            <T.Group position={boxen[x].p}>
                <T.Mesh>
                    <T.BoxGeometry />
                    {#if false}
                        <T.MeshBasicMaterial
                            args={[
                                {
                                    color: boxColors[
                                        Math.floor(
                                            Math.random() * boxColors.length
                                        )
                                    ],
                                    opacity: 0.9,
                                    transparent: true,
                                },
                            ]}
                        />
                    {/if}
                    <T.MeshBasicMaterial {value} />
                </T.Mesh>
                <T.LineSegments>
                    <T.EdgesGeometry args={[new BoxGeometry()]} />
                    <T.MeshBasicMaterial
                        args={[
                            {
                                color: 0x000000,
                            },
                        ]}
                    />
                </T.LineSegments>
            </T.Group>
        {/await}
    {/if}
{/each}
