import bpy
import bmesh
import math
import os
import sys
from pathlib import Path
from mathutils import Vector

# A3/A4 Interior Asset Builder
# Blender 5.2.x
# Creates a separate, editable interior/equipment scene and exports legacy GLB names.
# All dimensions and positions are preliminary placeholders until field survey data is supplied.

# Resolve the repository from this script's location so the builder is portable.
SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parents[2]
BLENDER_DIR = PROJECT_ROOT / "blender"
SOURCE_DIR = BLENDER_DIR / "source"
SCRIPT_DIR = BLENDER_DIR / "scripts"
OUTPUT_DIR = BLENDER_DIR / "archive"
REFERENCE_DIR = PROJECT_ROOT / "reference_buildings"
BLEND_OUTPUT = SOURCE_DIR / "iv_a3_a4_interior_working.blend"

# Existing building GLBs are reference-only. The script does not modify or overwrite them.
REFERENCE_A3 = REFERENCE_DIR / "A3.glb"
REFERENCE_A4 = REFERENCE_DIR / "A4.glb"

ROOM_W = 5.039
ROOM_Z = 7.0
CEILING_Y = 3.10
FLOOR_Y = 0.0

# Keep the scene modular and easy to replace after the survey.
COLLECTIONS = [
    "REF_BUILDING_A3",
    "REF_BUILDING_A4",
    "INTERIOR_A3",
    "INTERIOR_A4",
    "EQUIPMENT_A3",
    "EQUIPMENT_A4",
    "LIGHTS_A3_A4",
]


def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def clean_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for collection in list(bpy.data.collections):
        if collection.name != 'Collection':
            bpy.data.collections.remove(collection)
    base = bpy.data.collections.get('Collection')
    if base:
        base.name = 'INTERIOR_A3'
    for name in COLLECTIONS:
        if name == 'INTERIOR_A3':
            continue
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    # Remove unused default collection if it exists and is empty after rename.
    for col in list(bpy.data.collections):
        if col.name == 'Collection' and len(col.objects) == 0:
            bpy.data.collections.remove(col)


def collection(name):
    return bpy.data.collections.get(name) or bpy.data.collections.new(name)


def move_to_collection(obj, name):
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    target = collection(name)
    if target.name not in [c.name for c in bpy.context.scene.collection.children]:
        bpy.context.scene.collection.children.link(target)
    target.objects.link(obj)
    return obj


def material(name, color, roughness=0.55, metallic=0.0, emission=None):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    if hasattr(mat, 'node_tree') and mat.node_tree:
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (*color, 1.0)
            bsdf.inputs['Roughness'].default_value = roughness
            bsdf.inputs['Metallic'].default_value = metallic
            if emission:
                bsdf.inputs['Emission Color'].default_value = (*emission, 1.0)
                bsdf.inputs['Emission Strength'].default_value = 2.0
    return mat


MAT_WOOD = material('MAT_WOOD_WARM', (0.42, 0.18, 0.07), 0.62)
MAT_WOOD_LIGHT = material('MAT_WOOD_LIGHT', (0.63, 0.36, 0.14), 0.48)
MAT_GREEN = material('MAT_FABRIC_GREEN', (0.08, 0.24, 0.10), 0.86)
MAT_BEIGE = material('MAT_FABRIC_BEIGE', (0.67, 0.60, 0.48), 0.92)
MAT_GREY = material('MAT_FABRIC_GREY', (0.27, 0.31, 0.36), 0.90)
MAT_WHITE = material('MAT_PLASTIC_WHITE', (0.88, 0.89, 0.90), 0.30)
MAT_PLASTIC = material('MAT_PLASTIC_OFFWHITE', (0.74, 0.76, 0.77), 0.38)
MAT_DARK = material('MAT_DARK_RUBBER', (0.015, 0.02, 0.03), 0.30, 0.15)
MAT_GLASS = material('MAT_GLASS_BLUE', (0.22, 0.46, 0.65), 0.12, 0.1)
MAT_METAL = material('MAT_METAL_BRUSHED', (0.30, 0.33, 0.36), 0.28, 0.82)
MAT_LED = material('MAT_LED_DIFFUSER', (1.0, 0.91, 0.63), 0.20, 0.0, emission=(1.0, 0.72, 0.25))
MAT_BLACK = material('MAT_SCREEN_BLACK', (0.006, 0.009, 0.014), 0.18, 0.45)


def bevel(obj, amount=0.04, segments=3):
    modifier = obj.modifiers.new('BEVEL_SOFT_EDGES', 'BEVEL')
    modifier.width = amount
    modifier.segments = segments
    modifier.limit_method = 'ANGLE'
    return obj


def apply_material(obj, mat):
    if obj.data and hasattr(obj.data, 'materials'):
        obj.data.materials.append(mat)
    return obj


def set_id(obj, object_id, asset_type, room):
    obj.name = object_id
    obj['object_id'] = object_id
    obj['asset_type'] = asset_type
    obj['room_id'] = room
    obj['verification'] = 'placeholder-pending-field-survey'
    return obj


def cube(name, location, scale, mat, coll, bevel_amount=0.03):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.scale = (scale[0] / 2, scale[1] / 2, scale[2] / 2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_material(obj, mat)
    if bevel_amount:
        bevel(obj, bevel_amount)
    move_to_collection(obj, coll)
    set_id(obj, name, 'furniture_or_fixture', coll.replace('INTERIOR_', ''))
    return obj


def cylinder(name, location, radius, depth, mat, coll, vertices=48, rotation=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation or (0, 0, 0))
    obj = bpy.context.object
    apply_material(obj, mat)
    bevel(obj, 0.018, 2)
    move_to_collection(obj, coll)
    set_id(obj, name, 'furniture_or_fixture', coll.replace('INTERIOR_', ''))
    return obj


def parent(child, root):
    # Preserve world placement while organizing a clean export hierarchy.
    world_matrix = child.matrix_world.copy()
    child.parent = root
    child.matrix_world = world_matrix
    return child


def create_root(name, coll_name, room):
    root = bpy.data.objects.new(name, None)
    collection(coll_name).objects.link(root)
    set_id(root, name, 'interior_root', room)
    return root


def create_long_led(room, position, index, root):
    coll = 'LIGHTS_A3_A4'
    name = f'DEV_{room}_LIGHT_CEILING_{index:02d}'
    body = cube(name, position, (1.60, 0.07, 0.16), MAT_PLASTIC, coll, 0.035)
    body['entity_id'] = ''
    body['visual_state'] = 'off'
    parent(body, root)
    diffuser = cube(f'{name}_DIFFUSER', (position[0], position[1] - 0.045, position[2]), (1.44, 0.025, 0.115), MAT_LED, coll, 0.02)
    parent(diffuser, body)
    for x in (-0.73, 0.73):
        cap = cube(f'{name}_ENDCAP_{"L" if x < 0 else "R"}', (position[0] + x, position[1], position[2]), (0.06, 0.055, 0.17), MAT_WHITE, coll, 0.02)
        parent(cap, body)
    return body


def create_ac(room, position, root):
    coll = f'EQUIPMENT_{room}'
    name = f'DEV_{room}_AC_WALL_01'
    body = cube(name, position, (1.35, 0.46, 0.30), MAT_WHITE, coll, 0.10)
    body['entity_id'] = ''
    body['visual_state'] = 'unverified'
    parent(body, root)
    fascia = cube(f'{name}_FASCIA', (position[0], position[1] - 0.04, position[2] - 0.16), (1.18, 0.24, 0.03), MAT_PLASTIC, coll, 0.035)
    parent(fascia, body)
    for i in range(8):
        vent = cube(f'{name}_VENT_{i+1:02d}', (position[0] - 0.48 + i * 0.137, position[1] - 0.13, position[2] - 0.185), (0.07, 0.025, 0.015), MAT_DARK, coll, 0.004)
        parent(vent, body)
    return body


def create_panel(room, position, root):
    coll = f'EQUIPMENT_{room}'
    name = f'ELEC_{room}_PANEL_01'
    panel = cube(name, position, (0.48, 0.68, 0.16), MAT_WHITE, coll, 0.06)
    panel['entity_id'] = ''
    panel['circuit_mapping'] = 'unverified'
    parent(panel, root)
    window = cube(f'{name}_COVER', (position[0], position[1] + 0.01, position[2] - 0.086), (0.35, 0.47, 0.025), MAT_GLASS, coll, 0.02)
    parent(window, panel)
    for i in range(4):
        slot_y = position[1] - 0.18 + i * 0.12
        breaker = cube(f'{name}_SLOT_{i+1:02d}', (position[0], slot_y, position[2] - 0.105), (0.22, 0.075, 0.025), MAT_PLASTIC, coll, 0.012)
        breaker['circuit'] = 'unverified'
        parent(breaker, panel)
        lever = cube(f'{name}_SLOT_{i+1:02d}_LEVER', (position[0] - 0.01, slot_y, position[2] - 0.125), (0.04, 0.045, 0.018), MAT_DARK, coll, 0.008)
        parent(lever, breaker)
    return panel


def create_camera(room, position, root):
    coll = f'EQUIPMENT_{room}'
    name = f'DEV_{room}_CAMERA_01'
    body = cylinder(name, position, 0.12, 0.10, MAT_WHITE, coll, 32, rotation=(math.pi / 2, 0, 0))
    body['entity_id'] = ''
    parent(body, root)
    lens = cylinder(f'{name}_LENS', (position[0], position[1] - 0.06, position[2]), 0.055, 0.025, MAT_DARK, coll, 32, rotation=(math.pi / 2, 0, 0))
    parent(lens, body)
    return body


def create_wall_plate(room, position, kind, index, root):
    coll = f'EQUIPMENT_{room}'
    prefix = 'SWITCH' if kind == 'switch' else 'OUTLET'
    name = f'DEV_{room}_{prefix}_WALL_{index:02d}'
    plate = cube(name, position, (0.12, 0.12, 0.025), MAT_WHITE, coll, 0.018)
    plate['entity_id'] = ''
    parent(plate, root)
    if kind == 'switch':
        rocker = cube(f'{name}_ROCKER', (position[0], position[1], position[2] - 0.018), (0.055, 0.075, 0.012), MAT_PLASTIC, coll, 0.010)
        parent(rocker, plate)
    else:
        for y in (-0.025, 0.025):
            hole = cube(f'{name}_SLOT_{"UP" if y < 0 else "DOWN"}', (position[0], position[1] + y, position[2] - 0.019), (0.048, 0.018, 0.008), MAT_DARK, coll, 0.004)
            parent(hole, plate)
    return plate


def create_sofa(root):
    coll = 'INTERIOR_A4'
    base = cube('FURN_A4_SOFA_01', (1.10, 0.34, -2.45), (2.30, 0.62, 0.82), MAT_GREEN, coll, 0.18)
    parent(base, root)
    back = cube('FURN_A4_SOFA_01_BACK', (1.10, 0.76, -2.78), (2.30, 0.68, 0.22), MAT_GREEN, coll, 0.10)
    parent(back, base)
    for i, x in enumerate((0.35, 1.10, 1.85), 1):
        cushion = cube(f'FURN_A4_SOFA_01_CUSHION_{i:02d}', (x, 0.68, -2.35), (0.65, 0.18, 0.58), MAT_GREEN, coll, 0.08)
        parent(cushion, base)


def create_table_and_chairs(root):
    coll = 'INTERIOR_A3'
    table = cube('FURN_A3_MEETING_TABLE_01', (-1.25, 0.80, 1.25), (1.25, 0.12, 2.25), MAT_WOOD_LIGHT, coll, 0.055)
    parent(table, root)
    for i, x in enumerate((-1.72, -0.78), 1):
        for j, z in enumerate((0.45, 1.25, 2.05), 1):
            chair = cube(f'FURN_A3_CHAIR_{i}_{j}', (x, 0.42, z), (0.48, 0.72, 0.48), MAT_GREY, coll, 0.08)
            parent(chair, root)


def create_round_table(root):
    coll = 'INTERIOR_A3'
    table = cylinder('FURN_A3_ROUND_TABLE_01', (1.55, 0.42, 1.30), 0.48, 0.54, MAT_WOOD_LIGHT, coll, 48)
    parent(table, root)
    for i, angle in enumerate((0.4, 2.5, 4.5), 1):
        x = 1.55 + math.cos(angle) * 0.82
        z = 1.30 + math.sin(angle) * 0.82
        chair = cube(f'FURN_A3_ARMCHAIR_{i:02d}', (x, 0.44, z), (0.70, 0.78, 0.70), MAT_GREEN, coll, 0.13)
        parent(chair, root)


def create_reference_import(filepath, target_collection):
    if not Path(filepath).exists():
        print(f'[interior] Reference not found: {filepath}')
        return None
    # Blender 5.2 glTF importer; imported objects are placed into the active collection.
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection
    before = set(bpy.data.objects)
    try:
        bpy.ops.import_scene.gltf(filepath=str(filepath))
    except Exception as exc:
        print(f'[interior] Reference import failed: {filepath}: {exc}')
        return None
    imported = [obj for obj in bpy.data.objects if obj not in before]
    for obj in imported:
        move_to_collection(obj, target_collection)
        obj.hide_render = True
        obj.hide_viewport = True
        obj['reference_only'] = True
    return imported


def create_asset(room):
    interior_coll = f'INTERIOR_{room}'
    root = create_root(f'ROOM_{room}_INTERIOR_ROOT', interior_coll, room)

    # Each exported interior uses its own building-local coordinate frame.
    # Positions are intentionally approximate until the field survey and platform transform review.
    if room == 'A4':
        create_sofa(root)
        create_ac(room, (-ROOM_W / 2 + 0.22, 2.45, -2.05), root)
        create_panel(room, (-ROOM_W / 2 + 0.15, 2.05, -2.85), root)
        create_camera(room, (ROOM_W / 2 - 0.22, 2.65, -3.0), root)
        create_wall_plate(room, (-ROOM_W / 2 + 0.15, 1.05, -1.15), 'switch', 1, root)
        create_wall_plate(room, (-ROOM_W / 2 + 0.15, 0.38, -1.80), 'outlet', 1, root)
    else:
        create_table_and_chairs(root)
        create_round_table(root)
        create_ac(room, (-ROOM_W / 2 + 0.22, 2.45, 1.95), root)
        create_panel(room, (-ROOM_W / 2 + 0.15, 2.05, 0.80), root)
        create_camera(room, (ROOM_W / 2 - 0.22, 2.65, 3.0), root)
        create_wall_plate(room, (ROOM_W / 2 - 0.15, 1.05, 3.20), 'switch', 1, root)
        create_wall_plate(room, (ROOM_W / 2 - 0.15, 0.38, 1.00), 'outlet', 1, root)

    return root


def set_world_and_render():
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.length_unit = 'METERS'
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 50
    scene.world.color = (0.04, 0.05, 0.07)


def export_hierarchy(root_name, filename):
    ensure_dir(OUTPUT_DIR)
    # Export by parent hierarchy so the room's linked light collection is included too.
    bpy.ops.object.select_all(action='DESELECT')
    root = bpy.data.objects.get(root_name)
    if not root:
        print(f'[interior] Root not found for export: {root_name}')
        return
    selected = []
    for obj in bpy.data.objects:
        current = obj
        while current and current != root:
            current = current.parent
        if current == root and obj.type in {'MESH', 'EMPTY'}:
            obj.select_set(True)
            selected.append(obj)
    bpy.context.view_layer.objects.active = root
    filepath = OUTPUT_DIR / filename
    bpy.ops.export_scene.gltf(
        filepath=str(filepath),
        export_format='GLB',
        use_selection=True,
        export_apply=False,
        export_materials='EXPORT',
        export_cameras=False,
        export_lights=False,
        export_attributes=True,
        export_yup=True,
    )
    print(f'[interior] Exported: {filepath}')


def main():
    clean_scene()
    set_world_and_render()
    ensure_dir(OUTPUT_DIR)

    # Reference imports are hidden and never exported.
    create_reference_import(REFERENCE_A3, 'REF_BUILDING_A3')
    create_reference_import(REFERENCE_A4, 'REF_BUILDING_A4')

    # Two separate room roots in their own building-local coordinate frames.
    root_a4 = create_asset('A4')
    root_a3 = create_asset('A3')

    # The third light belongs to the transition overlay and is kept in its own collection/root.
    # Its final host file and local transform must be chosen with the platform team.
    transition_root = create_root('ROOM_A3_A4_TRANSITION_ROOT', 'LIGHTS_A3_A4', 'A3-A4-TRANSITION')
    create_long_led('A3_A4_TRANSITION', (0.0, CEILING_Y, 0.0), 1, transition_root)
    create_long_led('A4', (0.0, CEILING_Y, -2.2), 1, root_a4)
    create_long_led('A3', (0.0, CEILING_Y, 2.7), 1, root_a3)

    # Set save and export state.
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUTPUT))
    export_hierarchy('ROOM_A3_INTERIOR_ROOT', 'A3_interior.glb')
    export_hierarchy('ROOM_A4_INTERIOR_ROOT', 'A4_interior.glb')
    export_hierarchy('ROOM_A3_A4_TRANSITION_ROOT', 'A3_A4_transition_interior.glb')

    print('[interior] Completed preliminary interior asset build.')
    print('[interior] All dimensions, transforms, entity IDs and circuit mappings are placeholders until field survey/platform transform review.')


if __name__ == '__main__':
    main()
