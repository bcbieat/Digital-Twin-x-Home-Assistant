# Active V2 AABB Overlap Screening — 16 November 2026

## Scope and method

Read-only screening of the active production GLBs used by V2:

- `blender/exports/A3_interior_measured.glb`
- `blender/exports/A3_A4_transition_interior_measured.glb`
- `blender/exports/A4_interior_measured.glb`

The check grouped canonical device/electrical node families, accumulated world-space AABBs through the GLB node hierarchy, and reported pair intersections whose overlap was greater than 3 mm on all three axes. This is an AABB screening signal only; it is not a mesh collision test and does not prove a placement defect.

No Blender file, GLB, transform, or source asset was modified.

## Results

| Asset | Semantic groups screened | Positive inter-group AABB pairs >3 mm | Result |
|---|---:|---:|---|
| A3 | 7 | 0 | No confirmed inter-device AABB overlap |
| Transition | 4 | 0 | No confirmed inter-device AABB overlap |
| A4 | 6 | 0 | No confirmed inter-device AABB overlap |

### Screened A3 groups

- `DEV_A3_AC_WALL_01`
- `DEV_A3_CAMERA_01`
- `DEV_A3_LIGHT_CEILING_01`
- `DEV_A3_OUTLET_WALL_01`
- `DEV_A3_OUTLET_WALL_02`
- `DEV_A3_SWITCH_WALL_01`
- `ELEC_A3_PANEL_01`

### Screened Transition groups

- `DEV_A3_A4_TRANSITION_LIGHT_CEILING_01`
- `DEV_A3_A4_TRANSITION_OUTLET_WALL_01`
- `DEV_A3_A4_TRANSITION_OUTLET_WALL_02`
- `DEV_TRANSITION_TV_01`

### Screened A4 groups

- `DEV_A4_AC_WALL_01`
- `DEV_A4_LIGHT_CEILING_01`
- `DEV_A4_OUTLET_WALL_01`
- `DEV_A4_OUTLET_WALL_02`
- `DEV_A4_SWITCH_WALL_01`
- `ELEC_A4_PANEL_01`

## Interpretation

- The expected wall-mounted contacts and architectural embedding are not classified as inter-device defects by this check.
- The earlier QA report's seven camera-assembly AABB signals remain a separate historical review candidate; they are not reproduced as positive overlap between the grouped active device roots in this export-level screen.
- No panel-overlap defect is verified by this screen.
- AABB gaps do not prove correct wall clearance, face direction, or real mesh-level separation. Close-up/elevation review remains required for breaker A3, transition light, vegetation, and panel/framing relationships.

## Disposition

**No automatic correction applied.** Preserve current manual placements and source files. Any geometry or transform change requires a focused visual/mesh-level finding and separate authorization.

## Related records

- `docs/MODEL_QA_REPORT_2026-11-13.md`
- `docs/DEFECT_LOG_2026-11-16.md`
- `docs/ASSET_IDENTITY_COORDINATE_CONTRACT.md`
