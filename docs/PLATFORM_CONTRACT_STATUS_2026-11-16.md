# Platform Coordinate and Placement Contract Status — 16 November 2026

## Outcome

The repository-side contract has been checked against the current measured GLBs and the hosted V2 Web Demo. **Formal platform-owner confirmation is not available in this repository**, so origin, axis, heading, picking, and acceptance are not marked as approved. The current result is an evidence-backed draft plus an explicit pending gate.

## Verified in the current implementation

| Contract area | Current evidence | Status |
|---|---|---|
| Authoring units | Builder sets Blender units to Metric; intended scale is 1 Blender unit = 1 metre. | **Verified locally** |
| Authoring axes | Blender X = east/west, Y = north/south, Z = up. | **Verified locally** |
| Authoring origin | South-west corner of A4 on the finished floor; room order is A4 → transition → A3 along X. | **Verified locally** |
| Export behavior | Separate A3, transition, and A4 room-root GLBs; measured exporter uses `export_yup=True` and `export_apply=False`. | **Verified locally; not platform-approved** |
| Runtime loader | V2 uses Three.js r128 with `GLTFLoader`; hosted browser smoke test loads all three GLBs. | **Verified in Web Demo** |
| Runtime picking | V2 registers canonical device/panel meshes and returns the mapped object key from Three.js raycasting. | **Verified in Web Demo; platform pipeline not confirmed** |
| Identity | Active GLBs preserve node names; current GLBs do not expose `object_id`/`room_id` as glTF `extras`. | **Verified locally** |
| Hosted acceptance environment | `https://iv3diotproject.vercel.app/app/room_3d_preview_v2`, Chrome desktop smoke test, Three.js r128, WebGL, A3/transition/A4 assets returning HTTP 200 and `3/3 ROOMS READY`. | **Web Demo smoke environment verified** |

## Still pending platform-owner confirmation

1. Platform world origin and overlay anchor.
2. Axis directions, handedness, and whether the platform applies its own glTF Y-up conversion.
3. Whether the target frame is building-local, ENU, RTC, or another convention.
4. Heading and rotation convention, including the authoritative north direction.
5. Whether A3, transition, and A4 share one platform frame.
6. Unit interpretation and any platform root scale.
7. Root-transform policy: preserve local roots or apply a platform-provided transform.
8. Whether exact node names are case-sensitive and authoritative after optimization, batching, or instancing.
9. Whether picking returns the clicked child or the canonical device parent.
10. Whether a sidecar manifest or glTF `extras` schema is required.
11. Required file split, polygon/material/texture/draw-call budgets.
12. Named acceptance scene/tool, approver, and approved source/export hash pair.

## Acceptance gate

The current Vercel Web Demo proves hosting, GLB reachability, browser loading, and local raycast interaction. It does **not** prove alignment with an external platform or field coordinates. Do not claim platform placement readiness, apply a new global transform, or re-export for a consuming platform until the platform owner supplies the pending answers and approves a source/export hash pair.

## Evidence references

- `docs/ASSET_IDENTITY_COORDINATE_CONTRACT.md`
- `docs/PLATFORM_SOURCE_HANDOFF_2026-11-13.md`
- `config/device-mapping.example.json`
- `app/room_3d_preview_v2.html`
- Hosted smoke test: `https://iv3diotproject.vercel.app/app/room_3d_preview_v2`
