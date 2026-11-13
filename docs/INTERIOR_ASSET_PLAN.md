# A3/A4 Interior & Equipment Asset Plan

## Objective

Create interior and electrical/IoT assets as a **separate GLB asset** for the existing Mars3D + Cesium platform, leaving the current A3.glb and A4.glb untouched. Assets will be placed as a child/overlay at an agreed local origin and transform by the platform team.

## Existing building-model inspection

Downloaded reference files are in `reference_buildings/`:

- `A3.glb` — 1,479,832 bytes; 8 nodes, 7 meshes, 12 materials; local model bounds approximately X 5.039 m × Y 4.013 m × Z 7.000 m.
- `A4.glb` — 1,483,452 bytes; 8 nodes, 7 meshes, 12 materials; local model bounds approximately X 5.039 m × Y 4.013 m × Z 7.003 m.
- Both report glTF 2.0, generated with Blender I/O 5.2.40.
- Existing nodes represent exterior structure such as floor/steps, frames/details, glazing, roof, sign, unverified closures, walls, and detail root. Interior furniture and electrical equipment are not among the named mesh nodes.

**Important:** bounds alone do not establish each building's world location, georeferenced anchor, heading, or the platform's model offset. Do not assume two buildings' local frames or origins align. Obtain the platform placement transform from the team before producing a combined assembly.

## Proposed asset organization

Prefer either one interior overlay per building or separate object-level GLBs, depending on platform review:

- `blender/exports/A3_interior_measured.glb` — current measured A3 deliverable.
- `blender/exports/A3_A4_transition_interior_measured.glb` — current measured transition deliverable.
- `blender/exports/A4_interior_measured.glb` — current measured A4 deliverable.
- Keep current Blender source in `blender/source/`, scripts in `blender/scripts/`, review images in `blender/previews/`, and retired prototypes in `blender/archive/`.
- Alternatively, export a room overlay plus independently selectable devices if the application needs per-asset loading and entity selection.

Do not overwrite existing `A3.glb` / `A4.glb` without explicit review from the platform team.

## Object naming

Use stable, unique IDs (avoid relying only on localized labels):

- `ROOM_A3_INTERIOR_ROOT`, `ROOM_A4_INTERIOR_ROOT`
- `FURN_A3_MEETING_TABLE_01`, `FURN_A4_SOFA_01`
- `DEV_A3_LIGHT_CEILING_01`
- `DEV_A3_SWITCH_WALL_01`
- `DEV_A3_OUTLET_WALL_01`
- `DEV_A3_AC_WALL_01`
- `DEV_A3_TV_WALL_01`
- `DEV_A3_CAMERA_01`
- `ELEC_A3_PANEL_01`

Use analogous A4 IDs. The actual entity IDs and breaker mappings remain unverified until checked in Home Assistant and with the electrical panel schedule.

## Blender setup and placement

1. Work in a new Blender file; import copies of the reference GLBs for visual alignment only.
2. Preserve the source building meshes; do not edit or re-export them as part of the interior deliverable.
3. Determine whether imported building assets are meters, their local axes, origins, and exact transforms. Confirm against platform team's placement/heading config.
4. Model and position the interior in a clearly named root collection, separate from imported reference buildings.
5. Use Metric units. Follow the target platform coordinate convention, and confirm GLB's Y-up conversion and the Cesium local East-North-Up/RTC placement with the platform team.
6. Apply scale and rotation on exportable asset roots only after validating alignment. Retain separate selectable objects for lights/devices.
7. Keep pivots at sensible attachment points; use a separate child mesh for moving controls such as a breaker lever, but initially treat breaker interactions as visual mockups only.

## Modeling priority

1. Room shell alignment / open connection between A3 and A4.
2. Ceiling lights: three long fixtures (A3, transition area, A4).
3. Wall-mounted ACs, breakers, switches and outlet plates.
4. Existing TV and cameras.
5. Main furniture silhouettes and materials.
6. Fine detail only after room dimensions and references are verified.

Prefer rounded bevels, smooth shading where appropriate, realistic proportions, and PBR materials (base color, roughness, metallic only for actual metal). Avoid excessive polygon density; use bevels/normal maps and reuse materials/meshes where appropriate.

## Survey data required

- Room dimensions, ceiling height, wall/opening geometry, and the transform/datum corresponding to the building GLBs.
- Position and dimensions of each fixture/furniture/electrical device, measured from a clear origin.
- Full-view photos and close-ups for the exact device model, including switch/outlet and breaker labels.
- Electrical circuit schedule confirmed by the responsible staff member.
- Home Assistant entity inventory confirmed by the Home Assistant administrator.
- Platform supported asset hierarchy, max GLB/file budget, allowed texture formats, click-picking method, and placement API/config.

## Export validation checklist

- Export `.glb` (glTF 2.0) from Blender; keep source `.blend` plus linked textures in the project.
- Test each overlay in a clean scene and in the platform team's local integration branch.
- Verify axes, scale, origin, heading, coordinates, floor clearance, and alignment with existing building shell.
- Verify each required device remains a separate selectable node and carries stable IDs (metadata/extensions only if platform supports them).
- Check texture paths/embedding, material response, file size, load time, and browser/GPU performance.
- Confirm device states are mock-only until a reviewed integration mapping is implemented through a secure backend.

## Scope and safety

This plan creates a visual interior/equipment overlay. It does not assert real breaker slot assignments, Home Assistant entity IDs, or live hardware control. Breakers are protective equipment; any real switching must be explicitly approved and supported by installed control hardware and the responsible electrical professional.
