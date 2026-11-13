import bpy
import math
from pathlib import Path
from mathutils import Vector

# Measured A3/A4 interior reconstruction (Blender 5.2+).
# Blender axes: X = east/west, Y = north/south, Z = up.
# Coordinate origin: south-west corner of A4 on the finished floor.
# All site-measured dimensions are in metres. Furniture positions are visual estimates
# based on supplied photographs and must be refined only if future survey data changes them.

# Resolve the repository from this script's location so the builder is portable.
SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parents[2]
BLENDER_DIR = PROJECT_ROOT / "blender"
SOURCE_DIR = BLENDER_DIR / "source"
SCRIPT_DIR = BLENDER_DIR / "scripts"
OUT_DIR = BLENDER_DIR / "exports"
PREVIEW_DIR = BLENDER_DIR / "previews"
REFERENCE_DIR = PROJECT_ROOT / "reference_buildings"
BLEND_FILE = SOURCE_DIR / "iv_a3_a4_measured_interior.blend"
PREVIEW = PREVIEW_DIR / "measured_interior_preview.png"
BREAKER_PREVIEW = PREVIEW_DIR / "breaker_panel_detail_preview.png"

# Measured construction envelope
A3_W, A4_W, TRANS_W = 2.40, 2.40, 2.00
ROOM_D, WALL_H, ROOF_RISE = 3.56, 2.00, 1.035
TOTAL_W = A3_W + TRANS_W + A4_W
# Cardinal layout from survey: A4 east wall opens to transition west wall;
# transition east wall opens to A3 west wall. Therefore west-to-east order is A4, transition, A3.
A4_X0, TRANS_X0, A3_X0 = 0.0, A4_W, A4_W + TRANS_W

COLS = ["SHELL", "FURNITURE", "EQUIPMENT", "LIGHTING", "REFERENCE"]


def get_col(name):
    return bpy.data.collections.get(name)


def clear():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)
    for name in COLS:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)


def mat(name, color, rough=0.5, metal=0.0, emission=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metal
    if emission:
        bsdf.inputs['Emission Color'].default_value = (*emission, 1)
        bsdf.inputs['Emission Strength'].default_value = 3.0
    return m

WOOD = mat('Wood wall / floor', (0.36, 0.13, 0.035), .45)
WOOD_LIGHT = mat('Wood furniture', (0.56, 0.30, 0.11), .42)
# Keep the roof visibly distinct from the darker wall cladding in presentation views.
OSB = mat('OSB roof', (0.42, 0.18, 0.050), .68)
BLACK_METAL = mat('Weathered black steel', (.018, .022, .025), .30, .65)
OFFWHITE = mat('Warm off-white plastic', (.74, .70, .60), .35)
DARK = mat('Dark grill / screen', (.004, .006, .009), .25, .35)
GLASS = mat('Window glass', (.12, .28, .34), .15, .1)
GREEN = mat('Green fabric', (.08, .24, .10), .90)
CANVAS = mat('Canvas cream', (.62, .55, .41), .95)
RUG = mat('Rug neutral', (.42, .36, .30), .96)
LED = mat('LED diffuser', (1, .87, .53), .20, 0, emission=(1, .78, .25))
WHITE = mat('White', (.84, .84, .80), .35)
BREAKER_RED = mat('Breaker lever red', (.68, .018, .012), .34)


def register(obj, name, collection, kind, room='A3-A4'):
    obj.name = name
    obj['object_id'] = name
    obj['asset_type'] = kind
    obj['room_id'] = room
    obj['measurement_source'] = 'site-survey-2026-11-10'
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    get_col(collection).objects.link(obj)
    return obj


def cube(name, loc, dims, material, collection='SHELL', kind='architecture', room='A3-A4', bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    obj = bpy.context.object
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    if bevel:
        mod = obj.modifiers.new('Soft edge', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
    return register(obj, name, collection, kind, room)


def cyl(name, loc, radius, depth, material, collection='FURNITURE', kind='furniture', room='A3-A4', rotation=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth, location=loc, rotation=rotation or (0, 0, 0))
    obj = bpy.context.object
    obj.data.materials.append(material)
    mod = obj.modifiers.new('Soft edge', 'BEVEL')
    mod.width = min(radius * .12, .025)
    mod.segments = 2
    return register(obj, name, collection, kind, room)


def parent(child, root):
    matrix = child.matrix_world.copy()
    child.parent = root
    child.matrix_world = matrix


def root(name, room):
    obj = bpy.data.objects.new(name, None)
    get_col('SHELL').objects.link(obj)
    obj['object_id'] = name
    obj['asset_type'] = 'room_root'
    obj['room_id'] = room
    return obj


def beam(name, a, b, thick=.07, room='A3-A4'):
    a, b = Vector(a), Vector(b)
    delta = b - a
    obj = cube(name, (a+b)/2, (thick, thick, delta.length), BLACK_METAL, 'SHELL', 'steel_frame', room, .01)
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = Vector((0,0,1)).rotation_difference(delta.normalized())
    return obj


def add_wall_panels():
    # Floor across open connection.
    cube('ARCH_FLOOR_A3_A4', (TOTAL_W/2, ROOM_D/2, -.04), (TOTAL_W, ROOM_D, .08), WOOD, 'SHELL', 'floor')
    # Exterior walls. South walls include doors, represented by frame and inset glass panel.
    for room, x0, width in [('A3', A3_X0, A3_W), ('A4', A4_X0, A4_W)]:
        # North full wall
        cube(f'ARCH_{room}_NORTH_WALL', (x0+width/2, ROOM_D-.035, WALL_H/2), (width, .07, WALL_H), WOOD, 'SHELL', 'wall', room)
        # South segmented wall around 1.20 m centered door
        side = (width - 1.20)/2
        cube(f'ARCH_{room}_SOUTH_WALL_L', (x0+side/2, .035, WALL_H/2), (side, .07, WALL_H), WOOD, 'SHELL', 'wall', room)
        cube(f'ARCH_{room}_SOUTH_WALL_R', (x0+width-side/2, .035, WALL_H/2), (side, .07, WALL_H), WOOD, 'SHELL', 'wall', room)
        # Door glass and black frame
        cube(f'ARCH_{room}_DOOR_GLASS', (x0+width/2, .045, 1.0), (1.20, .035, 2.0), GLASS, 'SHELL', 'door', room)
        for xx in (x0+side, x0+width-side):
            beam(f'ARCH_{room}_DOOR_FRAME_{xx:.2f}', (xx,.0,0), (xx,.0,2.0), .06, room)
        # Outside side walls: windowed (visual infill glass with a black mullion; these remain separate from shell).
        for direction, x in [('WEST', x0), ('EAST', x0+width)]:
            if room == 'A3' and direction == 'WEST':
                continue  # A3 west is open connection
            if room == 'A4' and direction == 'EAST':
                continue  # A4 east is open connection
            # Two complete adjacent window units on each exterior side wall.
            # Each unit is 1.15 x 1.05 m (survey range: 1.14–1.15 x 1.04–1.05 m).
            # A4 uses the west wall and A3 uses the east wall; the internal sides remain open.
            unit_w, sill, opening_h = 1.15, .60, 1.05
            opening_w = unit_w * 2
            lower_h = sill
            upper_h = WALL_H - (sill + opening_h)
            face_x = x + (-.041 if direction == 'WEST' else .041)
            cube(f'ARCH_{room}_{direction}_WALL_BELOW_WINDOWS', (x, ROOM_D/2, lower_h/2), (.07, ROOM_D, lower_h), WOOD, 'SHELL', 'wall', room)
            if upper_h > 0:
                cube(f'ARCH_{room}_{direction}_WALL_ABOVE_WINDOWS', (x, ROOM_D/2, sill+opening_h+upper_h/2), (.07, ROOM_D, upper_h), WOOD, 'SHELL', 'wall', room)
            side_margin = (ROOM_D - opening_w)/2
            for side_i, yy in enumerate((side_margin/2, ROOM_D-side_margin/2), 1):
                cube(f'ARCH_{room}_{direction}_WALL_JAMB_{side_i}', (x, yy, sill+opening_h/2), (.07, side_margin, opening_h), WOOD, 'SHELL', 'wall', room)
            # Build two separate complete window units. Their outer dimensions are
            # 1.15 x 1.05 m each, with the units touching at the centre line.
            frame_t = .045
            glass_margin = .10
            unit_centres = (ROOM_D/2 - unit_w/2, ROOM_D/2 + unit_w/2)
            for unit_i, yy in enumerate(unit_centres, 1):
                cube(
                    f'ARCH_{room}_{direction}_WINDOW_{unit_i:02d}',
                    (face_x, yy, sill+opening_h/2),
                    (.018, unit_w-glass_margin, opening_h-glass_margin),
                    GLASS, 'SHELL', 'window', room
                )
                # Individual perimeter frames make each 1.15 x 1.05 window
                # readable as its own unit rather than one wide opening.
                y_left = yy - unit_w/2 + frame_t/2
                y_right = yy + unit_w/2 - frame_t/2
                z_bottom = sill + frame_t/2
                z_top = sill + opening_h - frame_t/2
                for side_name, frame_y in [('LEFT', y_left), ('RIGHT', y_right)]:
                    beam(
                        f'ARCH_{room}_{direction}_WINDOW_{unit_i:02d}_FRAME_{side_name}',
                        (face_x, frame_y, sill), (face_x, frame_y, sill+opening_h),
                        frame_t, room
                    )
                for edge_name, frame_z in [('BOTTOM', z_bottom), ('TOP', z_top)]:
                    beam(
                        f'ARCH_{room}_{direction}_WINDOW_{unit_i:02d}_FRAME_{edge_name}',
                        (face_x, yy-unit_w/2, frame_z), (face_x, yy+unit_w/2, frame_z),
                        frame_t, room
                    )
    # Transition room: North and south walls, open to A3 and A4.
    cube('ARCH_TRANSITION_NORTH_WALL', (TRANS_X0+TRANS_W/2, ROOM_D-.035, WALL_H/2), (TRANS_W,.07,WALL_H), WOOD, 'SHELL', 'wall', 'TRANSITION')
    cube('ARCH_TRANSITION_SOUTH_WALL', (TRANS_X0+TRANS_W/2,.035,WALL_H/2), (TRANS_W,.07,WALL_H), WOOD, 'SHELL', 'wall', 'TRANSITION')
    # Perimeter and strong horizontal framing.
    for x in (0, A3_W, A3_W+TRANS_W, TOTAL_W):
        beam(f'ARCH_FRAME_VERTICAL_{x:.2f}', (x,0,0), (x,0,WALL_H), .08)
        beam(f'ARCH_FRAME_VERTICAL_N_{x:.2f}', (x,ROOM_D,0), (x,ROOM_D,WALL_H), .08)
    for y in (0, ROOM_D):
        beam(f'ARCH_FRAME_SOUTH_NORTH_{y:.2f}', (0,y,WALL_H), (TOTAL_W,y,WALL_H), .09)


def add_arch_end_cap(room, x0, y, side):
    """Close the arched space above a 2 m wall so the curved roof is not open at either end."""
    r = A3_W / 2
    center = x0 + r
    # Follow the same arch as the roof panels; the tiny Y offset prevents z-fighting with wall framing.
    y_face = y + (-.041 if side == 'SOUTH' else .041)
    vertices = [(x0, y_face, WALL_H), (x0 + A3_W, y_face, WALL_H)]
    for i in range(13):
        angle = math.pi * i / 12
        x = center + r * math.cos(angle)
        z = WALL_H + ROOF_RISE * math.sin(angle)
        vertices.append((x, y_face, z))
    mesh = bpy.data.meshes.new(f'ARCH_{room}_ROOF_{side}_END_CAP_MESH')
    mesh.from_pydata(vertices, [], [list(range(len(vertices)))])
    mesh.materials.append(OSB)
    mesh.update()
    obj = bpy.data.objects.new(f'ARCH_{room}_ROOF_{side}_END_CAP', mesh)
    return register(obj, obj.name, 'SHELL', 'roof_end_closure', room)


def add_transition_flashing():
    """Finish the four joints where the low connector roof meets the two arched rooms."""
    roof_overhang = .08
    z_top = WALL_H + .105
    # Raised metal caps stop the flat slab reading as an unfinished sheet and define drainage edges.
    for side, y in [('SOUTH', -roof_overhang), ('NORTH', ROOM_D + roof_overhang)]:
        cube(
            f'ARCH_TRANSITION_{side}_FASCIA',
            (TRANS_X0 + TRANS_W/2, y, WALL_H + .045),
            (TRANS_W + roof_overhang*2, .035, .16),
            BLACK_METAL, 'SHELL', 'roof_flashing', 'TRANSITION', .008
        )
        cube(
            f'ARCH_TRANSITION_{side}_DRIP_EDGE',
            (TRANS_X0 + TRANS_W/2, y + (-.025 if side == 'SOUTH' else .025), z_top),
            (TRANS_W + roof_overhang*2, .025, .035),
            BLACK_METAL, 'SHELL', 'roof_flashing', 'TRANSITION', .006
        )

    # Narrow upstands close the visible seams against the A4 and A3 roof spring lines.
    for side, x in [('A4', TRANS_X0), ('A3', TRANS_X0 + TRANS_W)]:
        cube(
            f'ARCH_TRANSITION_{side}_ROOF_UPSTAND',
            (x, ROOM_D/2, WALL_H + .115),
            (.045, ROOM_D + roof_overhang*2, .23),
            BLACK_METAL, 'SHELL', 'roof_flashing', 'TRANSITION', .008
        )
        cube(
            f'ARCH_TRANSITION_{side}_SEAL_STRIP',
            (x + (.032 if side == 'A4' else -.032), ROOM_D/2, WALL_H + .115),
            (.028, ROOM_D + roof_overhang*2, .08),
            OSB, 'SHELL', 'roof_joint', 'TRANSITION', .006
        )


def add_roofs():
    # A3 and A4 use the measured curved/arched roof profile.
    for room, x0 in [('A3', A3_X0), ('A4', A4_X0)]:
        r = A3_W / 2
        center = x0 + r
        prev = None
        for i in range(13):
            angle = math.pi - math.pi*i/12
            x = center + r * math.cos(angle)
            z = WALL_H + ROOF_RISE * math.sin(angle)
            if prev:
                # Roof panel and black rib between sampled arch points, running north/south.
                dx, dz = x-prev[0], z-prev[1]
                length = math.sqrt(dx*dx+dz*dz)
                panel = cube(f'ARCH_{room}_ROOF_PANEL_{i:02d}', ((x+prev[0])/2, ROOM_D/2, (z+prev[1])/2), (length+.02, ROOM_D, .045), OSB, 'SHELL', 'roof', room)
                panel.rotation_euler[1] = -math.atan2(dz, dx)
                beam(f'ARCH_{room}_ROOF_RIB_{i:02d}', (x,0,z), (x,ROOM_D,z), .045, room)
            prev = (x,z)
        add_arch_end_cap(room, x0, 0, 'SOUTH')
        add_arch_end_cap(room, x0, ROOM_D, 'NORTH')

    # The connecting section has a separate low, flat roof rather than an arch.
    # A shallow overhang follows the measured 2.00 m x 3.56 m transition envelope.
    roof_overhang = .08
    cube(
        'ARCH_TRANSITION_FLAT_ROOF',
        (TRANS_X0 + TRANS_W/2, ROOM_D/2, WALL_H + .045),
        (TRANS_W + roof_overhang*2, ROOM_D + roof_overhang*2, .09),
        OSB, 'SHELL', 'roof', 'TRANSITION', .02
    )
    # Black perimeter members make the flat roof read as the same lightweight steel/OSB construction.
    beam('ARCH_TRANSITION_FLAT_ROOF_FRONT_BEAM', (TRANS_X0-roof_overhang, -roof_overhang, WALL_H), (TRANS_X0+TRANS_W+roof_overhang, -roof_overhang, WALL_H), .055, 'TRANSITION')
    beam('ARCH_TRANSITION_FLAT_ROOF_BACK_BEAM', (TRANS_X0-roof_overhang, ROOM_D+roof_overhang, WALL_H), (TRANS_X0+TRANS_W+roof_overhang, ROOM_D+roof_overhang, WALL_H), .055, 'TRANSITION')
    beam('ARCH_TRANSITION_FLAT_ROOF_WEST_BEAM', (TRANS_X0-roof_overhang, -roof_overhang, WALL_H), (TRANS_X0-roof_overhang, ROOM_D+roof_overhang, WALL_H), .055, 'TRANSITION')
    beam('ARCH_TRANSITION_FLAT_ROOF_EAST_BEAM', (TRANS_X0+TRANS_W+roof_overhang, -roof_overhang, WALL_H), (TRANS_X0+TRANS_W+roof_overhang, ROOM_D+roof_overhang, WALL_H), .055, 'TRANSITION')
    for i, x in enumerate((TRANS_X0 + TRANS_W*.25, TRANS_X0 + TRANS_W*.75), 1):
        beam(f'ARCH_TRANSITION_FLAT_ROOF_JOIST_{i:02d}', (x, 0, WALL_H), (x, ROOM_D, WALL_H), .04, 'TRANSITION')
    add_transition_flashing()


def create_led(room, loc, root_obj):
    # Meter-accurate 150cm long suspended rectangular batten fixture; length along Y.
    name = f'DEV_{room}_LIGHT_CEILING_01'
    body = cube(name, loc, (.13, 1.50, .12), OFFWHITE, 'LIGHTING', 'light_fixture', room, .025)
    body['visual_state'] = 'off'
    body['entity_id'] = ''
    diff = cube(f'{name}_DIFFUSER', (loc[0],loc[1],loc[2]-.064), (.075,1.32,.025), LED, 'LIGHTING', 'light_diffuser', room, .008)
    parent(body, root_obj); parent(diff, body)


def create_ac(room, loc, root_obj, face='south'):
    # 78.5 x 29cm actual front size, horizontally wall mounted.
    # ``face`` is the wall side seen from inside the room; all sub-parts follow it.
    name = f'DEV_{room}_AC_WALL_01'
    side_face = face in ('west', 'east')
    inward = 1 if face == 'west' else -1 if face == 'east' else 0
    if side_face:
        body_dims = (.20, .785, .29)
        grille_loc = (loc[0] + inward*.112, loc[1], loc[2]-.055)
        grille_dims = (.012, .64, .075)
        vane_loc = (loc[0] + inward*.125, loc[1], loc[2]-.085)
        vane_dims = (.02, .61, .025)
        display_loc = (loc[0] + inward*.115, loc[1] + .29, loc[2]+.015)
        display_dims = (.012, .06, .035)
    else:
        inward = 1 if face == 'south' else -1
        body_dims = (.785, .20, .29)
        grille_loc = (loc[0], loc[1] + inward*.112, loc[2]-.055)
        grille_dims = (.64, .012, .075)
        vane_loc = (loc[0], loc[1] + inward*.125, loc[2]-.085)
        vane_dims = (.61, .02, .025)
        display_loc = (loc[0] + .29, loc[1] + inward*.115, loc[2]+.015)
        display_dims = (.06, .012, .035)
    body = cube(name, loc, body_dims, OFFWHITE, 'EQUIPMENT', 'air_conditioner', room, .055)
    grille = cube(f'{name}_GRILLE', grille_loc, grille_dims, DARK, 'EQUIPMENT', 'aircon_grille', room, .01)
    vane = cube(f'{name}_VANE', vane_loc, vane_dims, OFFWHITE, 'EQUIPMENT', 'aircon_vane', room, .01)
    display = cube(f'{name}_DISPLAY', display_loc, display_dims, WHITE, 'EQUIPMENT', 'aircon_display', room, .004)
    body['wall_face'] = face
    body['placement_source'] = 'reference-photo'
    body['placement_confidence'] = 'wall-confirmed'
    body['position_status'] = 'provisional'
    body['surveyed_offset_available'] = False
    for obj in (body,grille,vane,display): parent(obj, root_obj)
    return body


def mark_reference_placement(obj, source='top-view-reference', confidence='reference-relative'):
    obj['placement_source'] = source
    obj['placement_confidence'] = confidence
    obj['position_status'] = 'provisional'
    obj['surveyed_offset_available'] = False
    return obj


def create_panel(room, loc, root_obj, face='south'):
    """Measured 21 x 20 cm visual-only six-slot breaker panel.

    ``face`` is the wall side seen from inside the room. Each slot and lever is
    a separate object for later local viewer interaction; no live electrical
    entity or switching command is attached.
    """
    name = f'ELEC_{room}_PANEL_01'
    side_face = face in ('west', 'east')
    outward = 1 if face in ('south', 'west') else -1
    # 21 cm wide x 20 cm high enclosure; depth is kept shallow for surface mounting.
    body_dims = (.075, .21, .20) if side_face else (.21, .075, .20)
    body = cube(name, loc, body_dims, OFFWHITE, 'EQUIPMENT', 'electrical_panel_visual_only', room, .012)
    body['circuit_mapping'] = 'unverified'
    body['entity_id'] = ''
    body['control_mode'] = 'simulation_only'
    body['slot_count'] = 6
    body['measured_width_cm'] = 21
    body['measured_height_cm'] = 20
    body['wall_face'] = face

    def point(lateral, depth, z):
        if side_face:
            return (loc[0] + outward * depth, loc[1] + lateral, loc[2] + z)
        return (loc[0] + lateral, loc[1] + outward * depth, loc[2] + z)

    # Recessed window, clear cover, header, and lower label rail.
    recess_dims = (.012, .16, .12) if side_face else (.16, .012, .12)
    cover_dims = (.010, .18, .14) if side_face else (.18, .010, .14)
    label_dims = (.012, .15, .022) if side_face else (.15, .012, .022)
    recess = cube(f'{name}_RECESS', point(0, .041, .010), recess_dims, DARK, 'EQUIPMENT', 'breaker_recess', room, .006)
    cover = cube(f'{name}_COVER', point(0, .048, .010), cover_dims, GLASS, 'EQUIPMENT', 'panel_cover_simulation', room, .005)
    cover['transparent_cover'] = True
    header = cube(f'{name}_HEADER', point(0, .045, .072), label_dims, OFFWHITE, 'EQUIPMENT', 'panel_label', room, .002)
    label_rail = cube(f'{name}_LABEL_RAIL', point(0, .045, -.070), label_dims, OFFWHITE, 'EQUIPMENT', 'panel_label', room, .002)
    for obj in (recess, cover, header, label_rail):
        parent(obj, body)

    # Six independent breakers in a horizontal row, matching the reference photo.
    for i in range(6):
        slot = i + 1
        lateral = -.075 + i*.030
        breaker_dims = (.026, .024, .075) if side_face else (.024, .026, .075)
        lever_dims = (.014, .022, .018) if side_face else (.022, .014, .018)
        detail_dims = (.010, .012, .016) if side_face else (.012, .010, .016)
        breaker = cube(f'{name}_SLOT_{slot:02d}', point(lateral, .053, .002), breaker_dims, WHITE, 'EQUIPMENT', 'breaker_slot_visual_only', room, .003)
        breaker['slot_index'] = slot
        breaker['simulated_state'] = 'on'
        breaker['entity_id'] = ''
        breaker['control_mode'] = 'simulation_only'
        lever = cube(f'{name}_SLOT_{slot:02d}_LEVER', point(lateral, .072, .010), lever_dims, BREAKER_RED, 'EQUIPMENT', 'breaker_lever_simulation', room, .003)
        lever['slot_index'] = slot
        lever['simulated_state'] = 'on'
        lever['control_mode'] = 'simulation_only'
        lever['hinge_axis'] = 'X' if side_face else 'Y'
        terminal = cube(f'{name}_SLOT_{slot:02d}_TERMINAL', point(lateral, .070, .032), detail_dims, OFFWHITE, 'EQUIPMENT', 'breaker_terminal', room, .001)
        mark = cube(f'{name}_SLOT_{slot:02d}_MARK', point(lateral, .071, -.030), detail_dims, BLACK_METAL, 'EQUIPMENT', 'breaker_marking', room, .001)
        parent(breaker, body); parent(lever, breaker); parent(terminal, breaker); parent(mark, breaker)

    parent(body, root_obj)
    return body


def create_outlet(room, loc, axis, index, root_obj, wall_face='east'):
    # Measured 12 x 7 cm surface-mounted black outlet.
    name = f'DEV_{room}_OUTLET_WALL_{index:02d}'
    dims = (.12,.025,.07) if axis == 'Y' else (.025,.12,.07)
    body = cube(name,loc,dims,DARK,'EQUIPMENT','outlet',room,.01)
    body['entity_id'] = ''
    body['wall_face'] = wall_face if axis == 'X' else 'south'
    # The socket details face into the room: +X from west wall, -X from east wall.
    for j, dx in enumerate((-.025,.025)):
        if axis == 'Y':
            hole = cyl(f'{name}_SOCKET_{j+1:02d}', (loc[0]+dx,loc[1]-.017,loc[2]), .009,.008, WHITE, 'EQUIPMENT', 'outlet_socket', room, (math.pi/2,0,0))
        else:
            facing = .017 if wall_face == 'west' else -.017
            hole = cyl(f'{name}_SOCKET_{j+1:02d}', (loc[0]+facing,loc[1]+dx,loc[2]), .009,.008, WHITE, 'EQUIPMENT', 'outlet_socket', room, (0,math.pi/2,0))
        parent(hole,body)
    parent(body,root_obj)
    return body


def create_switch(room, loc, axis, double, root_obj, wall_face=None):
    name = f'DEV_{room}_SWITCH_WALL_01'
    dims=(.12,.025,.07) if axis=='Y' else (.025,.12,.07)
    plate=cube(name,loc,dims,DARK,'EQUIPMENT','light_switch',room,.008); plate['entity_id']=''
    plate['wall_face'] = wall_face or ('south' if axis == 'Y' else 'east')
    count=2 if double else 1
    for i in range(count):
        off=(i-(count-1)/2)*.032
        rocker_loc=(loc[0]+off,loc[1]-.018,loc[2]) if axis=='Y' else (loc[0]-.018,loc[1]+off,loc[2])
        rock_dims=(.022,.01,.048) if axis=='Y' else (.01,.022,.048)
        rocker=cube(f'{name}_ROCKER_{i+1:02d}',rocker_loc,rock_dims,OFFWHITE,'EQUIPMENT','switch_rocker',room,.004)
        parent(rocker,plate)
    parent(plate,root_obj)
    return plate


def create_camera(root_obj):
    # Compact black square camera on a white suction/pivot mount.
    # The anchor remains the existing A3 NE placement; only the device geometry
    # is refined so the front face aims diagonally into A3 instead of straight south.
    name='DEV_A3_CAMERA_01'
    cam_x = A3_X0 + A3_W - .15
    cam_y = ROOM_D - .28
    body_loc = Vector((cam_x, cam_y, 2.07))
    target = Vector((A3_X0 + A3_W/2, ROOM_D/2, 1.35))
    front = (target - body_loc).normalized()
    # Camera-local -Y is the face/lens direction.
    camera_q = Vector((0, -1, 0)).rotation_difference(front)

    def world_point(local):
        return body_loc + camera_q @ Vector(local)

    def oriented_cube(obj_name, loc, dims, material, kind, bevel, quat):
        obj = cube(obj_name, loc, dims, material, 'EQUIPMENT', kind, 'A3', bevel)
        obj.rotation_mode = 'QUATERNION'
        obj.rotation_quaternion = quat
        return obj

    def white_link(obj_name, a, b, thick=.03):
        a, b = Vector(a), Vector(b)
        delta = b - a
        obj = cube(obj_name, (a+b)/2, (thick, thick, delta.length), WHITE, 'EQUIPMENT', 'camera_bracket', 'A3', .008)
        obj.rotation_mode = 'QUATERNION'
        obj.rotation_quaternion = Vector((0,0,1)).rotation_difference(delta.normalized())
        return obj

    # Keep the primary body origin exactly where the existing scene places it.
    body = oriented_cube(name, body_loc, (.14, .065, .12), DARK, 'camera', .018, camera_q)
    body['entity_id']=''
    body['mount_corner'] = 'NE'
    body['view_target'] = 'A3 room centre'
    body['view_direction'] = tuple(round(v, 4) for v in front)

    # A shallow front face and concentric lens barrel make the camera readable
    # from the room instead of appearing as a thin floating plate.
    face = oriented_cube(f'{name}_FACE', world_point((0, -.037, 0)), (.118, .012, .098), BLACK_METAL, 'camera_face', .012, camera_q)
    bezel = cyl(f'{name}_LENS_BEZEL', world_point((0, -.048, -.006)), .032, .012, BLACK_METAL, 'EQUIPMENT', 'camera_lens_bezel', 'A3')
    bezel.rotation_mode = 'QUATERNION'
    bezel.rotation_quaternion = Vector((0,0,1)).rotation_difference(front)
    lens = cyl(f'{name}_LENS', world_point((0, -.057, -.006)), .023, .008, GLASS, 'EQUIPMENT', 'camera_lens', 'A3')
    lens.rotation_mode = 'QUATERNION'
    lens.rotation_quaternion = Vector((0,0,1)).rotation_difference(front)
    lens['lens_direction'] = tuple(round(v, 4) for v in front)

    # White suction cup, pivot, and short articulated bracket.
    mount_loc = Vector((cam_x, cam_y + .06, 1.92))
    mount = cyl(f'{name}_MOUNT', mount_loc, .078, .028, WHITE, 'EQUIPMENT', 'camera_mount', 'A3', (math.pi/2,0,0))
    pivot = cyl(f'{name}_PIVOT', world_point((0, .035, .035)), .035, .045, WHITE, 'EQUIPMENT', 'camera_pivot', 'A3')
    pivot.rotation_mode = 'QUATERNION'
    pivot.rotation_quaternion = Vector((0,0,1)).rotation_difference(front)
    bracket_end = world_point((0, .045, .015))
    bracket = white_link(f'{name}_BRACKET', mount_loc, bracket_end, .032)

    # A small white power lead follows the corner/frame downward, as in the photo.
    cable_start = world_point((.035, .025, -.045))
    cable_corner = Vector((cam_x + .055, cam_y + .10, 1.78))
    cable_low = Vector((cam_x + .055, cam_y + .10, .82))
    cable_1 = white_link(f'{name}_CABLE_01', cable_start, cable_corner, .012)
    cable_2 = white_link(f'{name}_CABLE_02', cable_corner, cable_low, .012)

    for o in (body, face, bezel, lens, mount, pivot, bracket, cable_1, cable_2):
        parent(o, root_obj)
    for o in (face, bezel, lens, pivot):
        parent(o, body)
    return body


def create_tv(root_obj):
    # 71.5 x 42cm TV with the user's current manual Y placement preserved.
    # The screen, bezel, stand, and base were captured from the working .blend
    # before this rebuild; do not restore the older nominal Y=3.40..3.48 values.
    name='DEV_TRANSITION_TV_01'
    screen=cube(name,(3.40,3.217261,.847521),(.715,.045,.42),DARK,'EQUIPMENT','television','TRANSITION',.018); screen['entity_id']=''
    bezel=cube(f'{name}_BEZEL',(3.40,3.187261,.847521),(.745,.018,.45),BLACK_METAL,'EQUIPMENT','tv_bezel','TRANSITION',.01)
    pole=cyl(f'{name}_STAND',(3.40,3.267261,.40),.025,.80,WHITE,'EQUIPMENT','tv_stand','TRANSITION')
    base=cyl(f'{name}_BASE',(3.40,3.267261,.03),.20,.06,WHITE,'EQUIPMENT','tv_base','TRANSITION')
    for o in (screen,bezel,pole,base): parent(o,root_obj)


def furniture_beam(name, a, b, thick, room):
    a, b = Vector(a), Vector(b)
    delta = b - a
    obj = cube(name, (a+b)/2, (thick, thick, delta.length), BLACK_METAL,
               'FURNITURE', 'furniture_support', room, .008)
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = Vector((0,0,1)).rotation_difference(delta.normalized())
    return obj


def chair(name, x, y, room, root_obj, color=CANVAS, facing=0.0):
    # Compact folding camp chair: canvas seat/back with crossed dark tubular legs.
    # Local back is +Y; facing=0 therefore points the seat toward -Y.
    seat=cube(name,(x,y,.43),(.52,.52,.10),color,'FURNITURE','camping_chair',room,.04)
    back=cube(f'{name}_BACK',(x,y+.19,.76),(.52,.08,.55),color,'FURNITURE','camping_chair_back',room,.04)
    for side, dx in enumerate((-.20,.20), 1):
        leg_a=furniture_beam(f'{name}_FRAME_{side:02d}_A',(x+dx,y-.20,.06),(x-dx*.82,y+.20,.40),.025,room)
        leg_b=furniture_beam(f'{name}_FRAME_{side:02d}_B',(x+dx,y+.20,.06),(x-dx*.82,y-.20,.40),.025,room)
        parent(leg_a,seat); parent(leg_b,seat)
    parent(seat,root_obj); parent(back,seat)
    seat.rotation_euler[2] = facing


def white_shelf(name, x, y, room, root_obj):
    # Six-tier compact white camping/minimal shelf; position is a rough blockout.
    for side, xx in enumerate((x-.28, x+.28), 1):
        upright = cube(f'{name}_UPRIGHT_{side}', (xx,y,.72), (.045,.36,1.40), WHITE,
                       'FURNITURE','shelf_support',room,.008)
        parent(upright,root_obj)
    for tier in range(6):
        z = .16 + tier*.22
        shelf = cube(f'{name}_LEVEL_{tier+1:02d}', (x,y,z), (.62,.40,.035), WHITE,
                     'FURNITURE','shelf_level',room,.008)
        parent(shelf,root_obj)


def angled_crate(name, x, y, room, root_obj, angle=0.0):
    crate = storage_crate(name,x,y,room,root_obj)
    crate.rotation_euler[2] = angle


def standing_mirror(name, x, y, room, root_obj):
    # Simple freestanding curved-mirror blockout oriented toward the transition/TV.
    panel = cube(name,(x,y,.90),(.52,.045,1.48),GLASS,'FURNITURE','standing_mirror',room,.16)
    frame = cube(f'{name}_FRAME',(x,y+.028,.90),(.58,.045,1.54),WOOD_LIGHT,
                 'FURNITURE','mirror_frame',room,.18)
    # Frame is behind the reflective face from the nominal TV viewing direction.
    parent(frame,root_obj); parent(panel,root_obj)
    panel.rotation_euler[2] = -math.pi/4
    frame.rotation_euler[2] = -math.pi/4
    foot = cube(f'{name}_FOOT',(x,y,.10),(.68,.38,.08),BLACK_METAL,
                'FURNITURE','mirror_foot',room,.025)
    parent(foot,root_obj)


def U_chair(name, x, y, room, root_obj):
    # Minimal U-shaped lounge chair placeholder; back toward +Y, seat faces -Y.
    seat = cube(name,(x,y,.40),(.54,.46,.09),GREEN,'FURNITURE','camping_lounge_chair',room,.06)
    back = cube(f'{name}_BACK',(x,y+.20,.70),(.54,.09,.55),GREEN,
                'FURNITURE','camping_lounge_back',room,.07)
    for dx in (-.22,.22):
        arm = cube(f'{name}_ARM_{dx:+.2f}',(x+dx,y,.56),(.07,.46,.08),GREEN,
                   'FURNITURE','camping_lounge_arm',room,.03)
        parent(arm,seat)
    parent(back,seat); parent(seat,root_obj)


def two_trees(name, x, y, room, root_obj):
    potted_plant(f'{name}_01',x,y,room,root_obj)
    potted_plant(f'{name}_02',x+.24,y-.22,room,root_obj)


def slatted_table(name, x, y, width, depth, height, room, root_obj):
    # Readable camping table made from separate wooden slats and folding supports.
    slat_count = 5
    gap = .018
    slat_depth = (depth - gap*(slat_count-1)) / slat_count
    boards=[]
    for i in range(slat_count):
        yy = y - depth/2 + slat_depth/2 + i*(slat_depth+gap)
        board_name = name if i == 0 else f'{name}_SLAT_{i+1:02d}'
        board = cube(board_name, (x, yy, height), (width, slat_depth, .055), WOOD_LIGHT,
                     'FURNITURE', 'camping_table_slat', room, .012)
        boards.append(board)
        parent(board, root_obj)
    apron = cube(f'{name}_APRON', (x, y, height-.10), (width-.10, .07, .10), WOOD_LIGHT,
                 'FURNITURE', 'camping_table_apron', room, .01)
    parent(apron, root_obj)
    for side, xx in enumerate((x-width/2+.13, x+width/2-.13), 1):
        for front, yy in enumerate((y-depth/2+.11, y+depth/2-.11), 1):
            leg = furniture_beam(f'{name}_LEG_{side}_{front}', (xx, yy, .06), (xx, yy, height-.11), .035, room)
            parent(leg, root_obj)
    # A pair of diagonal braces gives the table a folding-camp silhouette.
    for side, xx in enumerate((x-width/2+.13, x+width/2-.13), 1):
        brace = furniture_beam(f'{name}_BRACE_{side}', (xx, y-depth/2+.08, .22),
                               (xx, y+depth/2-.08, height-.18), .022, room)
        parent(brace, root_obj)
    return boards[0]


def storage_crate(name, x, y, room, root_obj):
    base = cube(name, (x, y, .17), (.42, .36, .30), WOOD_LIGHT, 'FURNITURE', 'camping_storage_crate', room, .025)
    parent(base, root_obj)
    for i, yy in enumerate((y-.17, y+.17), 1):
        rail = cube(f'{name}_RAIL_{i}', (x, yy, .24), (.44, .035, .18), WOOD_LIGHT,
                    'FURNITURE', 'crate_rail', room, .01)
        parent(rail, root_obj)
    return base


def potted_plant(name, x, y, room, root_obj):
    pot = cyl(name, (x, y, .10), .14, .20, OFFWHITE, 'FURNITURE', 'plant_pot', room)
    stem = cyl(f'{name}_STEM', (x, y, .38), .025, .42, WOOD, 'FURNITURE', 'plant_stem', room)
    parent(pot, root_obj); parent(stem, root_obj)
    for i, (dx, dy, rz) in enumerate(((-.10,.01,-.35),(.08,.03,.35),(0,.06,0)), 1):
        leaf = cube(f'{name}_LEAF_{i:02d}', (x+dx, y+dy, .57 + abs(dx)*.4), (.20,.07,.05), GREEN,
                    'FURNITURE', 'plant_leaf', room, .025)
        leaf.rotation_euler[2] = rz
        parent(leaf, root_obj)


def camp_lantern(name, x, y, z, room, root_obj):
    body = cyl(name, (x, y, z), .07, .13, BLACK_METAL, 'FURNITURE', 'camp_lantern', room)
    glow = cyl(f'{name}_GLOW', (x, y, z+.015), .045, .08, LED, 'FURNITURE', 'lantern_glow', room)
    handle = cube(f'{name}_HANDLE', (x, y, z+.10), (.09, .018, .018), BLACK_METAL,
                  'FURNITURE', 'lantern_handle', room, .008)
    for obj in (body, glow, handle): parent(obj, root_obj)


def furniture(a3_root, a4_root, trans_root):
    # Coordinate interpretation follows the user's top view: A4 is the north/west zone,
    # the long table is in the south edge of the transition, and A3 is the east/south zone.
    # A4: one camping table near the north side, U chairs on its north side, two small chairs at ends.
    table4 = slatted_table('FURN_A4_CAMP_TABLE_01', A4_X0 + 1.20, 2.55, 1.25, .48, .70, 'A4', a4_root)
    U_chair('FURN_A4_U_CHAIR_01', A4_X0 + .78, 2.92, 'A4', a4_root)
    U_chair('FURN_A4_U_CHAIR_02', A4_X0 + 1.62, 2.92, 'A4', a4_root)
    chair('FURN_A4_CAMP_CHAIR_S', A4_X0 + .52, 2.55, 'A4', a4_root, CANVAS, math.pi/2)
    chair('FURN_A4_CAMP_CHAIR_N', A4_X0 + 1.88, 2.55, 'A4', a4_root, CANVAS, -math.pi/2)
    white_shelf('FURN_A4_WHITE_SHELF_6TIER', A4_X0 + .68, .38, 'A4', a4_root)
    two_trees('DECOR_A4_NW_TREES', A4_X0 + .28, 3.10, 'A4', a4_root)

    # Transition: long table against south wall, 3 chairs south / 2 chairs north.
    slatted_table('FURN_TRANSITION_LONG_CAMP_TABLE_01', TRANS_X0 + 1.00, .70, .52, 1.75, .70, 'TRANSITION', trans_root)
    for i, y in enumerate((.22, .70, 1.18), 1):
        chair(f'FURN_TRANSITION_CAMP_CHAIR_S_{i:02d}', TRANS_X0 + .62, y, 'TRANSITION', trans_root, CANVAS, math.pi/2)
    for i, y in enumerate((.45, 1.05), 1):
        chair(f'FURN_TRANSITION_CAMP_CHAIR_N_{i:02d}', TRANS_X0 + 1.38, y, 'TRANSITION', trans_root, CANVAS, -math.pi/2)
    angled_crate('DECOR_TRANSITION_TABLE_CRATE_01', TRANS_X0 + 1.74, .48, 'TRANSITION', trans_root, math.pi/8)
    # Plant left of A3 door when viewed from transition toward A3; kept by the edge.
    potted_plant('DECOR_TRANSITION_A3_DOOR_PLANT_01', A3_X0 - .22, .34, 'TRANSITION', trans_root)

    # A3: round conversation group sits about 60 cm inside A3 from the TV and against north wall.
    table3 = cyl('FURN_A3_ROUND_TABLE_01', (A3_X0 + .72, ROOM_D - .48, .39), .31, .72, WOOD_LIGHT, 'FURNITURE', 'table', 'A3')
    parent(table3, a3_root)
    rug3 = cyl('FURN_A3_ROUND_RUG_01', (A3_X0 + .72, ROOM_D - .48, .012), .58, .024, RUG, 'FURNITURE', 'rug', 'A3')
    parent(rug3, a3_root)
    chair('FURN_A3_GREEN_CHAIR_NORTH', A3_X0 + .72, ROOM_D - .94, 'A3', a3_root, GREEN, 0.0)
    chair('FURN_A3_GREEN_CHAIR_EAST', A3_X0 + 1.18, ROOM_D - .48, 'A3', a3_root, GREEN, math.pi/2)
    angled_crate('DECOR_A3_ROUND_GROUP_CRATE_01', A3_X0 + 1.50, ROOM_D - .82, 'A3', a3_root, -math.pi/8)
    potted_plant('DECOR_A3_ROUND_GROUP_PLANT_01', A3_X0 + 1.92, ROOM_D - .76, 'A3', a3_root)

    # A3's lower work table and two chairs occupy the south portion, leaving the SE mirror clear.
    slatted_table('FURN_A3_CAMP_TABLE_01', A3_X0 + 1.20, .72, 1.15, .46, .70, 'A3', a3_root)
    chair('FURN_A3_CAMP_CHAIR_S_01', A3_X0 + .72, .34, 'A3', a3_root, CANVAS, math.pi)
    chair('FURN_A3_CAMP_CHAIR_S_02', A3_X0 + 1.68, .34, 'A3', a3_root, CANVAS, math.pi)
    standing_mirror('FURN_A3_SE_STANDING_MIRROR_01', A3_X0 + 2.03, .28, 'A3', a3_root)


def build_rooms():
    a4 = root('ROOM_A4_INTERIOR_ROOT', 'A4')
    trans = root('ROOM_A3_A4_TRANSITION_ROOT', 'TRANSITION')
    a3 = root('ROOM_A3_INTERIOR_ROOT', 'A3')
    add_wall_panels(); add_roofs()

    # Include room-specific architecture in each room GLB while retaining the shared floor/frame in the .blend scene.
    room_roots = {'A3': a3, 'A4': a4, 'TRANSITION': trans}
    for obj in list(get_col('SHELL').objects):
        room_root = room_roots.get(obj.get('room_id'))
        if room_root and obj != room_root and obj.parent is None:
            parent(obj, room_root)

    # Three ceiling batten fixtures: 1.50 m long, exactly one per zone along Y axis.
    create_led('A4', (A4_X0 + A4_W/2, ROOM_D/2, 2.78), a4)
    create_led('A3_A4_TRANSITION', (TRANS_X0 + TRANS_W/2, ROOM_D/2, 1.88), trans)
    create_led('A3', (A3_X0 + A3_W/2, ROOM_D/2, 2.78), a3)

    # A4 (west room): measured electrical placement.
    # Breaker: 21 x 20 cm, SW corner, mounted on the west wall.
    # Outlets: 12 x 7 cm, low at the left/right sides of the west-wall window.
    # Switch: immediately left of the south door, around 1.50 m eye level.
    create_ac('A4', (A4_X0 + A4_W/2, .18, 1.72), a4)
    create_panel('A4', (A4_X0 + .075, .18, 1.63), a4, face='west')
    # Place the two outlets at the outer lower corners of the paired west-wall window units,
    # just outside the window jambs so they do not overlap the frames or glass.
    window_side_margin = (ROOM_D - (1.15 * 2)) / 2
    # Align each outlet directly beneath the outside lower corner of the paired windows.
    # Window opening spans Y=0.28..3.28 m; outlets remain low at Z=.46 m.
    outlet_y_left = window_side_margin
    outlet_y_right = ROOM_D - window_side_margin
    create_outlet('A4', (A4_X0 + .04, outlet_y_left, .46), 'X', 1, a4, wall_face='west')
    create_outlet('A4', (A4_X0 + .04, outlet_y_right, .46), 'X', 2, a4, wall_face='west')
    create_switch('A4', (A4_X0 + (A4_W - 1.20)/2 - .08, .045, 1.50), 'Y', False, a4, wall_face='south')

    # Transition: TV north wall, outlets near A3 partition boundary.
    create_tv(trans)
    create_outlet('A3_A4_TRANSITION', (TRANS_X0 + .18, .12, .35), 'Y', 1, trans)
    create_outlet('A3_A4_TRANSITION', (TRANS_X0 + .40, 3.48, .35), 'Y', 2, trans)

    # A3 (east room): the AC is on the south/door wall. The paired east-wall
    # windows use the same lower-corner outlet pattern as A4's paired west windows.
    # Exact offsets are visual estimates because the supplied plan is not dimensioned.
    # Mount above the 2.0 m door opening in the curved-roof end zone; the 78.5 cm
    # indoor unit cannot fit on either 60 cm door-side wall segment.
    create_ac('A3', (A3_X0 + A3_W/2, .18, 2.15), a3, face='south')
    # Breaker returns to the original A3 south-wall SW corner, beside the
    # transition and clear of the centered door opening.
    panel = create_panel('A3', (A3_X0 + .18, .075, 1.63), a3, face='south')
    panel = mark_reference_placement(panel, source='top-view-reference', confidence='reference-relative')
    panel['hardware_dimension_source'] = 'breaker-photo'
    panel['offset_measurement'] = 'not-surveyed'

    # A3 has two east-wall outlets, aligned with the lower outer corners of its
    # paired window units, matching the confirmed A4 placement pattern.
    window_side_margin = (ROOM_D - (1.15 * 2)) / 2
    outlet_y_left = window_side_margin
    outlet_y_right = ROOM_D - window_side_margin
    east_outlet_1 = create_outlet('A3', (A3_X0 + A3_W - .04, outlet_y_left, .46), 'X', 1, a3, wall_face='east')
    east_outlet_2 = create_outlet('A3', (A3_X0 + A3_W - .04, outlet_y_right, .46), 'X', 2, a3, wall_face='east')
    # Preserve the manually adjusted switch placement from the current Blender scene.
    # It remains on ARCH_A3_EAST_WALL_JAMB_2, but is inset and lower than the
    # surveyed/reference estimate; rebuilding must not restore the older position.
    east_switch = create_switch('A3', (A3_X0 + A3_W - .04, 3.045, 1.22), 'X', False, a3, wall_face='east')
    for obj in (east_outlet_1, east_outlet_2, east_switch):
        mark_reference_placement(obj)
        obj['offset_measurement'] = 'not-surveyed'
    create_camera(a3)

    furniture(a3, a4, trans)
    return a3, trans, a4


def export_root(root_obj, filename):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        check=obj
        while check and check != root_obj:
            check=check.parent
        if check == root_obj:
            obj.select_set(True)
    bpy.context.view_layer.objects.active=root_obj
    bpy.ops.export_scene.gltf(filepath=str(OUT_DIR / filename), export_format='GLB', use_selection=True, export_apply=False, export_materials='EXPORT', export_cameras=False, export_lights=False, export_yup=True)


def preview_scene():
    scene=bpy.context.scene
    scene.render.engine='BLENDER_EEVEE'
    scene.render.resolution_x=1600; scene.render.resolution_y=1050; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(PREVIEW)
    scene.world.color=(.035,.045,.055)
    cam_data=bpy.data.cameras.new('REVIEW_CAMERA'); cam=bpy.data.objects.new('REVIEW_CAMERA',cam_data); bpy.context.scene.collection.objects.link(cam)
    cam.location=(10.2,-9.7,8.7); target=Vector((3.4,1.8,1.25)); cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler(); cam.data.lens=42; scene.camera=cam
    for name,loc,power,size in [('KEY',(3.0,-2,7.5),1500,5.5),('FILL',(9,4,5.5),1100,4),('BACK',(-1,5,5.2),900,3)]:
        ld=bpy.data.lights.new(name,'AREA'); ld.energy=power; ld.shape='DISK'; ld.size=size
        ob=bpy.data.objects.new(name,ld); bpy.context.scene.collection.objects.link(ob); ob.location=loc; ob.rotation_euler=(target-Vector(loc)).to_track_quat('-Z','Y').to_euler()
    bpy.ops.render.render(write_still=True)


def preview_breaker_panel():
    scene=bpy.context.scene
    scene.render.engine='BLENDER_EEVEE'
    scene.render.resolution_x=1200; scene.render.resolution_y=900; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(BREAKER_PREVIEW)
    scene.world.color=(.025,.030,.038)
    cam_data=bpy.data.cameras.new('BREAKER_DETAIL_CAMERA')
    cam=bpy.data.objects.new('BREAKER_DETAIL_CAMERA',cam_data)
    bpy.context.scene.collection.objects.link(cam)
    # Close-up of the A4 panel, mounted on its west wall and facing into the room.
    cam.location=(.95,.82,1.66)
    target=Vector((.10,.18,1.63))
    cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler()
    cam.data.lens=58
    scene.camera=cam
    for name,loc,power,size in [
        ('BREAKER_KEY',(4.2,.15,2.9),850,2.0),
        ('BREAKER_FILL',(5.8,-.8,1.8),500,1.5),
        ('BREAKER_RIM',(4.5,1.0,2.8),650,1.2),
    ]:
        ld=bpy.data.lights.new(name,'AREA'); ld.energy=power; ld.shape='DISK'; ld.size=size
        ob=bpy.data.objects.new(name,ld); bpy.context.scene.collection.objects.link(ob)
        ob.location=loc; ob.rotation_euler=(target-Vector(loc)).to_track_quat('-Z','Y').to_euler()
    bpy.ops.render.render(write_still=True)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    clear()
    scene=bpy.context.scene
    scene.unit_settings.system='METRIC'; scene.unit_settings.length_unit='METERS'
    a3,trans,a4=build_rooms()
    # Save after all measured objects and stable node IDs are included.
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_FILE))
    export_root(a3,'A3_interior_measured.glb')
    export_root(trans,'A3_A4_transition_interior_measured.glb')
    export_root(a4,'A4_interior_measured.glb')
    preview_scene()
    preview_breaker_panel()
    print('[measured] Built and exported A3/A4 interior reconstruction.')

if __name__=='__main__':
    main()
