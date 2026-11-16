# Target Device and Production Network Performance — 16 November 2026

## Scope

Hosted V2 demo tested at:

`https://iv3diotproject.vercel.app/app/room_3d_preview_v2`

This is a production-path measurement on the available target laptop, plus browser-emulated mobile CPU/network profiles. It is **not** a physical-phone certification because no physical mobile device or approved acceptance thresholds were supplied.

## Target laptop

| Item | Observed value |
|---|---|
| Device | Acer Nitro ANV15-51 |
| OS | Windows 11 Home Single Language |
| CPU | Intel Core i5-13420H, 8 cores / 12 logical processors |
| RAM | 34,049,220,608 bytes (~31.7 GiB) |
| Installed GPUs | NVIDIA GeForce RTX 4050 Laptop GPU; Intel UHD Graphics |
| Browser | Chrome 157.0.8103.78 |
| Active WebGL renderer during interactive sample | ANGLE / Intel UHD Graphics / Direct3D 11 |
| Viewport | 1440 × 900 CSS px, DPR 1 |
| Three.js | r128 |

The test browser selected the Intel UHD Graphics path, not the discrete RTX 4050. This must be retained when interpreting the FPS result.

## Current production asset/runtime snapshot

| Metric | Observed value |
|---|---:|
| A3 GLB | 1,248,408 bytes |
| Transition GLB | 902,336 bytes |
| A4 GLB | 1,136,528 bytes |
| Total GLB payload | 3,287,272 bytes (~3.14 MiB) |
| GLB responses | HTTP 200, `model/gltf-binary` |
| Vercel cache on header check | HIT |
| Page readiness | `3/3 ROOMS READY` |
| Render calls/frame | 765 |
| Triangles/frame | 42,976 |
| Renderer geometries | 822 |
| Renderer textures | 1 |

Compared with the 13 November baseline, the active exports and scene are materially larger/more segmented. The old baseline (271 calls, 5,496 triangles, ~525 KiB total) is no longer representative of the current V2 production scene.

## Interactive target-laptop result

A 10-second steady-state sample was captured in normal Chrome using the active Intel UHD Graphics WebGL path after the three GLBs reached ready state.

| Metric | Result |
|---|---:|
| Sample duration | 10,022 ms |
| Frames | 283 |
| Average FPS | 28.24 |
| Median frame time | 30.1 ms |
| Median FPS | 33.22 |

**Assessment:** usable for a controlled desktop demo, but below a typical 60 FPS target. No project-approved minimum FPS exists, so this is an observation rather than a formal pass/fail acceptance.

## Production-network observations

The three GLBs loaded concurrently from Vercel and returned HTTP 200. Header checks reported `X-Vercel-Cache: HIT` with `Cache-Control: public, max-age=0, must-revalidate`. No content encoding was advertised for the binary GLBs.

Observed response-start ranges across repeated production-path runs:

| Profile | A3 / Transition / A4 response-start range | Readiness outcome |
|---|---:|---|
| Desktop, unthrottled | ~113–787 ms | `3/3 ROOMS READY` |
| Emulated mobile 4G | ~129–697 ms | `3/3 ROOMS READY` |
| Emulated mobile 3G | ~257–1,086 ms | `3/3 ROOMS READY` |

The measurement harness intentionally disabled browser cache for the cold/network runs. Vercel edge caching could still serve a HIT. The binary payloads remain about 3.14 MiB in total; response-start timing does not equal complete download/parse/GPU-upload readiness.

## Emulated mobile rendering observations

These profiles used a 390 × 844 mobile viewport, device pixel ratio 2, production URL, CPU throttling, and browser network emulation. They are diagnostic only—not a substitute for a real mobile device.

| Profile | CPU throttle | Network model | Average FPS range (2 runs) | Median FPS range |
|---|---:|---|---:|---:|
| Mobile 4G | 4× | 70 ms RTT, ~1.6 Mbps down | 10.09–16.00 | 10.00–15.02 |
| Mobile 3G | 6× | 180 ms RTT, ~0.75 Mbps down | 8.43–11.12 | 8.57–10.01 |

**Assessment:** current scene is not performance-accepted for constrained mobile profiles. The responsive layout renders, and all assets eventually load, but frame rate is low under throttling.

## Errors and limitations

- No GLB request failed.
- `favicon.ico` returned 404; this does not affect the scene.
- `net::ERR_ABORTED` document events were produced by automated page navigation/reload in the harness, not by GLB loading.
- No physical phone/tablet was available in this session.
- No approved limits exist for first-load time, total bytes, draw calls, triangles, minimum FPS, or thermal behavior.
- The current V2 page lacks the detailed readiness instrumentation exposed by the legacy page's `window.__GLB_PERF_BASELINE__`; therefore browser wall-clock waits and response-start timings are reported separately and are not presented as exact all-assets parse time.

## Recommended next actions

1. Treat **765 render calls** as the primary performance concern; optimize only after the picking/identity budget is approved because object segmentation supports selection and state changes.
2. Add V2-specific readiness/FPS instrumentation before the next formal benchmark.
3. Test on at least one physical mobile device over the intended Wi-Fi/cellular path and record browser, GPU, temperature/thermal state, cold load, cached load, and 30–60 second FPS.
4. Agree acceptance thresholds before claiming pass/fail (recommended fields: max first ready time, min median FPS, max calls/frame, max total GLB payload).
5. Do not merge primitives or apply Draco/Meshopt until platform picking and node-name preservation are verified.

## Status

- **Production desktop/laptop observation:** completed.
- **Emulated mobile/network diagnostic:** completed.
- **Physical target-mobile acceptance:** pending.
- **Formal performance acceptance:** pending thresholds and platform approval.
