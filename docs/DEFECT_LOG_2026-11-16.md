# Web Demo Visual Defect Log — 16 November 2026

**Scope:** Record close-up observations before additional visual/model changes. This log separates verified defects from review candidates and unknowns. No Blender source transform, GLB geometry, or placement was changed as part of this log.

**Review evidence:**
- `blender/previews/qa_breaker_closeup_2026-11-13.png`
- `blender/previews/qa_material_closeup_breaker_v2_2026-11-13.png`
- `blender/previews/qa_material_room_transition_2026-11-13.png`
- `docs/MODEL_QA_REPORT_2026-11-13.md` (AABB screening only)
- Hosted V2 smoke test of `https://iv3diotproject.vercel.app/app/room_3d_preview_v2` on 16 November 2026

## Findings

| ID | Area | Observation / defect | Evidence and confidence | Status | Next action before changing assets |
|---|---|---|---|---|---|
| VIZ-01 | A3 breaker | Earlier reports described the A3 breaker as facing outward/protruding. The measured builder places its panel near the south wall with `face='south'`; the current V2 breaker camera has been corrected to look at the panel from the interior/north side. The close-up render shows the six-lever face, but does not establish flushness from a side/elevation view or prove a geometry penetration. | `blender/scripts/build_measured_a3_a4_interior.py` (`create_panel` and A3 call); QA close-up image; current V2 browser close-up on 16 Nov. High confidence for the current interior-facing camera result; physical/model flushness remains unverified. | **Review candidate — do not call geometry fixed yet.** Camera-view issue is addressed in V2; mesh placement is not changed. | Capture front, side, and wall-section views of the active A3 panel and its wall; compare panel/body depth and wall normal. Confirm which face is interior before any Blender transform or re-export. |
| VIZ-02 | Transition light | A canonical transition-light node exists and its ID/mapping is documented, but the reviewed transition material close-up is an architectural/roof-junction view, not a clear close-up of the light fixture. The image therefore does not confirm fixture overlap, missing geometry, or whether its simulation visual and light source agree. | `DEV_A3_A4_TRANSITION_LIGHT_CEILING_01` is documented in `docs/ASSET_IDENTITY_COORDINATE_CONTRACT.md`; V2 GLB smoke test reached `3/3 ROOMS READY`. Close-up evidence insufficient. | **Needs focused inspection.** Runtime loading passes; close-up visual/state parity remains unknown. | Capture the fixture and surrounding ceiling from front/side; toggle transition light ON/OFF and inspect both its emissive mesh and any associated light object. Record separate geometry and state findings. |
| VIZ-03 | Trees / vegetation | No vegetation-named nodes (tree/plant/leaf/foliage/shrub/bush/grass/flower/palm) were found in the active A3, transition, or A4 GLB node names during the 16 Nov check. The hosted smoke-test frame did not show vegetation. This suggests trees may be absent from the exported demo, but node-name search alone cannot rule out unnamed geometry or intentionally external assets. | Read-only node-name scan of all three active exports; hosted V2 screenshot. Medium confidence that named vegetation is absent; intent and unnamed-mesh status unknown. | **Likely visual-content gap; confirm expected scope.** | Compare the room reference photos and source scene for intended tree locations. Inspect GLB geometry/source collections and deployment asset paths before adding or moving vegetation. |
| VIZ-04 | Panel overlap | The existing model QA report identifies seven AABB overlap signals among A3 camera components (body, bracket, mount, cable, pivot); it explicitly says these are screening candidates, not proof of collision. It does **not** establish a breaker-panel overlap. No reviewed close-up currently proves panel-to-wall penetration or overlap with another device. | `docs/MODEL_QA_REPORT_2026-11-13.md`, F-04; AABB screen of 30 canonical device/electrical bodies. High confidence that seven camera pair signals were recorded; no verified panel overlap. | **Unconfirmed — avoid treating AABB as a defect.** | Re-run a focused mesh/visual inspection of the A3/A4 panels, adjacent framing and devices. Log each confirmed intersecting pair separately from expected wall contact; retain the camera assembly candidates as their own review items. |

## Constraints for follow-up

- Preserve user-adjusted/manual transforms and the current `.blend` / `.blend1` files; do not restore or overwrite them.
- No broad automatic collision correction.
- Keep breaker/IoT behavior browser-simulation-only; no live Home Assistant or electrical control.
- Only change a mesh/transform or re-export after the relevant overlap/placement is visually confirmed and the change is specifically approved.

## Summary

- **Confirmed in scope:** V2's A3 breaker camera had been looking from the wrong side; the browser view was changed to inspect the panel from the interior. This is a camera correction, not a geometry correction.
- **Likely but not yet confirmed:** named vegetation appears absent from the active GLB exports.
- **Needs more evidence:** transition-light close-up/state parity and any breaker-panel overlap.
- **Existing separate review candidate:** the A3 camera assembly AABB signals documented in the prior QA report.
