# Blender Workflow — A3/A4 Interior Overlay

## Deliverable

A separate glTF 2.0 `.glb` interior/equipment asset (or two room-specific GLBs), aligned to the existing platform buildings, without replacing the platform's source building files.

## 0. Before modeling

- Get approval to use the platform model files as references and distribute the resulting overlay.
- Ask the platform developer for A3/A4 scene placement, heading, coordinate reference/local origin, unit scale, import method, and picking behavior.
- Verify the imported GLB size/units in Blender. Metadata bounds are approximately 5.039 m × 4.013 m × 7.000 m for both, but a bounding box does not determine their placement transform or interior clearances.
- Gather real room measurements, device close-ups and exact installation positions. Use `assets/pictures/` as the source collection; convert HEIC images to JPEG/PNG locally if Blender or the image viewer cannot decode them.

## 1. Create the working file

1. Work from `blender/scripts/` and save the current source under `blender/source/`, such as `blender/source/iv_a3_a4_interior_working.blend`.
2. Set Scene Units to Metric. Confirm whether the target pipeline treats one Blender unit as one metre.
3. Create collections:
   - `REF_BUILDING_A3` and `REF_BUILDING_A4` (imported, locked, reference-only)
   - `INTERIOR_A3`
   - `INTERIOR_A4`
   - `EQUIPMENT_A3`
   - `EQUIPMENT_A4`
   - `LIGHTS_A3_A4`
4. Import copies of `reference_buildings/A3.glb` and `A4.glb`. Do not overwrite or re-export them. Hide or lock the reference collections after alignment.
5. Record the import transform and compare the model against measured dimensions. Confirm object origins/axes with the platform team.

## 2. Establish the coordinate contract

- Use one agreed local origin and axes for the overlay.
- Prefer separate A3/A4 overlays when each building has a different geographic transform; use one combined overlay only when the platform confirms a shared aligned frame.
- Record the mapping from Blender coordinates to the platform's local East-North-Up and placement/heading configuration.
- Do not infer exact Cesium coordinates from the GLB bounds; the platform team must provide or approve the anchor transform.

## 3. Block out and align

1. Build a measured floor/wall/opening guide from the survey.
2. Model only the interior surfaces not supplied by the exterior models, and avoid duplicate floors/ceilings that may z-fight.
3. Keep the A3-A4 connection open as required; no dividing wall unless the updated site survey contradicts that requirement.
4. Place the three long ceiling fixtures in measured positions: A3, transition zone, A4.
5. Add wall devices and furniture as independent named objects. Keep interactive equipment separable from decorative geometry.

## 4. Model assets

- Use reference photos and dimensions for each actual device. Model the recognizable silhouette, proportions, vents, bezels, faceplates and fixtures before fine details.
- Use bevel modifiers for manufactured edges; apply only where appropriate. Use smooth shading on curved geometry and weighted normals/bevel shading for hard-surface objects.
- Prefer PBR materials with measured/credible base color and roughness. Use metallic values only for metal surfaces; plastic and painted surfaces are generally non-metallic.
- Use separate emission material/mesh for lights so the application can change visual state.
- Keep breaker lever as a separate child mesh/pivot for visual animation only; do not imply control of real mains wiring.
- Avoid needless high-poly geometry. Reuse shared materials and repeated assets.

## 5. Naming and hierarchy

Use stable object names without spaces or localized labels as identifiers, for example:

```text
ROOM_A3_INTERIOR_ROOT
ROOM_A4_INTERIOR_ROOT
DEV_A3_LIGHT_CEILING_01
DEV_A3_AC_WALL_01
DEV_A3_PANEL_01
DEV_A3_SWITCH_WALL_01
DEV_A3_OUTLET_WALL_01
FURN_A4_SOFA_01
```

Keep a separate table mapping stable object IDs to human-readable names, location, measurements, and verified HA entity IDs. Entity IDs and circuit assignments remain null/unconfirmed until checked in the actual systems and electrical schedule.

## 6. Prepare GLB export

1. Remove or disable reference collections from export.
2. Select only the intended overlay collection(s); export A3 and A4 separately unless the platform confirms combined export.
3. Ensure object names and required selectable nodes are preserved.
4. Apply transforms on asset roots only after the coordinate contract has been validated; preserve meaningful pivots on device subparts.
5. Export glTF 2.0 `.glb` with embedded textures, PBR materials, UVs, and normals.
6. Avoid exporting cameras/lights unless the platform specifically requests them; application lighting is typically managed in Cesium.
7. Record Blender version, exporter version, asset version, file size, and transform used.

## 7. Validate in the platform

- Test an early simple prototype first, ideally one lamp plus one wall device.
- Compare scale, rotation, alignment, floor clearance and origin against A3.glb/A4.glb.
- Confirm the overlay does not hide the exterior shell or create z-fighting.
- Confirm selectable nodes can be picked by the app and names/metadata survive import.
- Test visual state change on an offline/mock entity before any live Home Assistant integration.
- Check load time, file size, draw calls and browser/GPU performance.

## Current machine status

The project now contains a verified Blender source scene under `blender/source/`, measured GLB deliverables under `blender/exports/`, and review renders under `blender/previews/`. The current source was inspected and corrected with a non-destructive QA pass; this workflow remains the reference for future edits. Home Assistant entities and live control mappings remain unverified.
