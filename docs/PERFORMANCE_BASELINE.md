# GLB Performance Baseline

**Measurement date:** 13 November 2026
**Measurement ID:** `glb-baseline-2026-11-13`
**Git commit:** `50ff93e` (`Organize project files and add gitignore`)
**Scope:** Read-only baseline for the three active measured GLB exports loaded by `app/room_3d_preview.html`.

> This is a development-machine baseline, not a production acceptance test. The project has not yet supplied target-device, network, polygon, draw-call, FPS, or first-load budgets.

## 1. Test conditions

| Item | Observed condition |
|---|---|
| OS | Windows 11 Home Single Language |
| Browser | Microsoft Edge 157.0.4341.46, headless Chromium mode |
| Browser user agent | `HeadlessChrome/157.0.0.0`, `Edg/157.0.0.0` |
| Viewport reported by page | 1254 × 627 CSS pixels |
| Device pixel ratio | 1 |
| WebGL | WebGL 2.0 (OpenGL ES 3.0 Chromium) |
| WebGL vendor | Google Inc. (Intel) |
| WebGL renderer | ANGLE (Intel, Intel(R) UHD Graphics (0x0000A7A8) Direct3D11) |
| Three.js | r128 |
| Renderer | antialias enabled, `powerPreference: "high-performance"` |
| Shadows | enabled, `PCFSoftShadowMap` |
| Server | local static server at `http://127.0.0.1:8765/` |
| Loading | three GLBs requested concurrently by `THREE.GLTFLoader` |
| Browser trials | 3 cold-profile runs and 3 shared-profile sequential runs |
| FPS sample | 1,000 ms warm-up, approximately 10,000 ms steady-state sample after all GLBs were ready |

The browser sample used the existing page scene, including procedural fallback construction, lights, shadows, controls, and the three measured GLBs. It is therefore a whole-page scene sample, not a GLB-only GPU isolation test.

## 2. Static GLB inventory

Metrics were computed by reading each GLB container and JSON chunk without opening Blender, importing, exporting, or rewriting any asset. `triangles` counts indexed triangle primitives; the active files use mode 4 (`TRIANGLES`). `draw-call estimate` is the number of mesh primitives and is not the final browser render-call count.

| Asset | File size | SHA-256 | Nodes | Meshes | Primitives / draw-call estimate | Materials | Textures / images | Vertices | Indices | Triangles | Accessors / bufferViews |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A3 | 249,856 B (244.0 KiB) | `f4b334e2647f9d20c2d46e2df47fce783bbe794efa8930c910277ec0a4fadfc5` | 125 | 124 | 124 | 13 | 0 / 0 | 4,638 | 7,830 | 2,610 | 374 / 374 |
| Transition | 81,908 B (80.0 KiB) | `e7b7b38a66b0dc4f189157673ac836fce1c70d31297a1c669be12101623822bf` | 31 | 30 | 30 | 8 | 0 / 0 | 1,728 | 3,096 | 1,032 | 92 / 92 |
| A4 | 205,852 B (201.0 KiB) | `85a6152b0b11ba160c5e57315c0b58a97003cbdb9f02924a1873796d8108a932` | 118 | 117 | 117 | 13 | 0 / 0 | 3,462 | 5,562 | 1,854 | 352 / 352 |
| **Total** | **537,616 B (525.0 KiB)** | — | **274** | **271** | **271** | — | **0 / 0** | **9,828** | **16,488** | **5,496** | — |

All three files declare `KHR_materials_emissive_strength`. No Draco or Meshopt compression extension is declared. The files contain no texture or image payload according to their glTF JSON; this records the current payload, not a validation of a future texture pipeline.

## 3. Browser loading baseline

The page instrumentation records `performance.now()` from each `GLTFLoader.load()` call to its parse-completion callback. The `all-assets-ready` value is measured from page instrumentation start to the callback that attaches the combined `MEASURED_GLB_LATEST` group. Resource timing is also recorded separately; local request duration is not the same as parse/upload/readiness duration.

### 3.1 Per-run all-assets readiness and steady-state results

Times are milliseconds. FPS values are calculated from frame intervals; they are not a target-device certification.

| Condition | Run | All assets ready | A3 callback duration | Transition callback duration | A4 callback duration | Median FPS | Average FPS | Median frame time | Calls/frame | Triangles/frame |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Cold profile | 0 | 1,518.3 | 1,406.2 | 1,408.0 | 1,412.2 | 142.86 | 146.21 | 7.0 | 271 | 5,496 |
| Cold profile | 1 | 1,445.2 | 1,338.8 | 1,340.9 | 1,344.5 | 142.86 | 146.07 | 7.0 | 271 | 5,496 |
| Cold profile | 2 | 1,674.1 | 1,559.2 | 1,566.2 | 1,564.0 | 144.93 | 146.28 | 6.9 | 271 | 5,496 |
| Shared profile | 10 | 1,522.6 | 1,424.9 | 1,426.9 | 1,430.7 | 144.93 | 145.84 | 6.9 | 271 | 5,496 |
| Shared profile | 11 | 381.7 | 244.1 | 247.0 | 251.0 | 144.93 | 145.68 | 6.9 | 271 | 5,496 |
| Shared profile | 12 | 575.1 | 359.6 | 362.2 | 366.7 | 144.93 | 145.69 | 6.9 | 271 | 5,496 |

Run 10 created the shared profile's initial cache state and is retained as observed data. Runs 11–12 show the subsequent cached behavior; the shared-profile condition should not be interpreted as a strict network-cache benchmark because the local server and browser startup still contribute variability.

### 3.2 Condition summary

| Condition | All-assets-ready median (min–max) | A3 callback median (min–max) | Transition callback median (min–max) | A4 callback median (min–max) | Median FPS range | Resource timing sum median |
|---|---:|---:|---:|---:|---:|---:|
| Cold profile, n=3 | 1,518.3 ms (1,445.2–1,674.1) | 1,406.2 ms (1,338.8–1,559.2) | 1,408.0 ms (1,340.9–1,566.2) | 1,412.2 ms (1,344.5–1,564.0) | 142.86–144.93 | 16.8 ms |
| Shared profile, n=3 | 575.1 ms (381.7–1,522.6) | 359.6 ms (244.1–1,424.9) | 362.2 ms (247.0–1,426.9) | 366.7 ms (251.0–1,430.7) | 144.93 | 24.8 ms |

Every measured GLB request returned the expected uncompressed body size: 249,856 B for A3, 81,908 B for Transition, and 205,852 B for A4. The local HTTP resource timing `transferSize` included approximately 300 bytes of response overhead per request; it should not replace the on-disk asset size in the asset budget.

## 4. Runtime renderer snapshot

After all three GLBs were ready, the page reported the following stable whole-scene snapshot during the samples:

| Metric | Observed value |
|---|---:|
| Loaded GLB meshes | 271 |
| Visible GLB meshes | 271 |
| Materials referenced by loaded GLBs | 34 |
| `renderer.info.render.calls` | 271 |
| `renderer.info.render.triangles` | 5,496 |
| `renderer.info.render.points` | 0 |
| `renderer.info.render.lines` | 0 |
| `renderer.info.memory.geometries` | 450 |
| `renderer.info.memory.textures` | 5 |
| `renderer.info.programs` | 7 |
| Frame sample duration | approximately 10.0 s |
| Sample frame count | 1,441 in the first captured run |
| First captured average FPS | 146.21 |
| First captured median FPS | 142.86 |
| First captured median frame time | 7.0 ms |

The 271 render calls match the 271 active GLB primitives in this scene snapshot. This is a useful correlation for this page, but `renderer.info` values can change with visibility, camera, shadows, procedural objects, material compilation, and future Three.js changes.

## 5. Interpretation and limitations

### Observed

- The three active measured exports total **537,616 bytes / 525.0 KiB** on disk.
- Geometry is small by raw triangle count: **5,496 triangles** across all three exports.
- The current export is highly segmented: **271 primitives**, which corresponded to **271 render calls** in the measured whole-page snapshot.
- The scene reported five renderer textures even though the GLB JSON files contained zero embedded texture/image records; these are runtime renderer resources and should not be treated as GLB texture bytes.
- On this Edge/Intel headless environment, the current combined scene sustained approximately **146 average FPS** with a median frame time near **7 ms** during the sampled runs.
- Cached/shared-profile readiness was faster in two subsequent runs, but timing variability is visible and should be measured again when a real delivery network and target hardware are available.

### Not yet verified

- No target phone, tablet, production GPU, or representative user hardware was tested.
- No approved maximum GLB size, triangle budget, primitive/draw-call budget, minimum FPS, or first-load threshold exists in the project documents.
- No real network/CDN transfer baseline was measured.
- The page uses a local server and headless browser; results may differ from an interactive browser with a different GPU path.
- The report does not prove that reducing primitives is safe for object selection, stable IDs, shadows, or future Home Assistant visual state changes.
- The current texture count is zero in the GLB payload, but texture compression and future textured assets remain unvalidated.

### Recommended next measurements

1. Repeat the same protocol on the team’s representative target device(s), including an interactive browser if that is the deployment mode.
2. Measure first load over the intended delivery path with compression and cache behavior representative of production.
3. Agree platform budgets before optimizing; then compare primitive count/draw calls, triangles, load readiness, and FPS before/after each change.
4. Evaluate primitive consolidation or instancing carefully because selectable device nodes and stable object names are part of the planned mapping contract.
5. Consider Draco/Meshopt, texture compression, and LOD only after the platform and target-device constraints are confirmed.

## 6. Mapping and safety status

`config/device-mapping.example.json` remains a draft with `status: "placeholder-unverified"`, null entity/circuit values, and visual-only breaker semantics. No Home Assistant credentials, entity IDs, circuit assignments, or live control behavior were introduced by this baseline task.

The measurement was non-destructive: no Blender builder was run, no `.blend` was opened or saved, and no GLB/reference asset was rewritten.

## 7. Reproduction notes

1. Start a static server from the project root and open `app/room_3d_preview.html`.
2. Use a fixed Edge headless viewport and isolated profile.
3. Read `window.__GLB_PERF_BASELINE__` after `frameSample.status === "complete"`.
4. Compare the static GLB table against the three files’ SHA-256 values.
5. Repeat at least three runs per cache condition and report raw values alongside median/min/max.

The instrumentation is intentionally read-only from the application’s perspective: it exposes a cloned snapshot at `window.__GLB_PERF_BASELINE__` and does not send telemetry or call Home Assistant.
