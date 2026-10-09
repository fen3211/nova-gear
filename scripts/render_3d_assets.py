"""
Procedural 3D Scene Generator and Renderer for NOVA Gear
Renders high-end photorealistic editorial product visuals via Blender 5.2+ Cycles.
Outputs transparent RGBA PNGs and saves source .blend files to assets/scenes/.
"""

import bpy
import math
import os
import sys

BASE_DIR = r"D:\Projects\ууу"
SCENES_DIR = os.path.join(BASE_DIR, "assets", "scenes")
IMAGES_DIR = os.path.join(BASE_DIR, "assets", "images")

os.makedirs(SCENES_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 96
    scene.cycles.use_denoising = True
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    return scene

def create_material(name, base_color=(0.1, 0.1, 0.1, 1.0), metallic=0.0, roughness=0.5, 
                    transmission=0.0, emission_color=(0, 0, 0, 1), emission_strength=0.0,
                    coat_weight=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = base_color
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
        if "Transmission Weight" in bsdf.inputs:
            bsdf.inputs["Transmission Weight"].default_value = transmission
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = emission_color
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = emission_strength
        if "Coat Weight" in bsdf.inputs:
            bsdf.inputs["Coat Weight"].default_value = coat_weight
    return mat

def setup_studio_lighting(energy_mult=1.0):
    # Key light: large warm area light
    bpy.ops.object.light_add(type='AREA', location=(3.0, -3.0, 4.0))
    key = bpy.context.active_object
    key.name = "Key_Light"
    key.data.energy = 450.0 * energy_mult
    key.data.size = 2.5
    key.data.color = (1.0, 0.98, 0.95)

    # Fill light: soft cool area light
    bpy.ops.object.light_add(type='AREA', location=(-3.5, -2.5, 2.5))
    fill = bpy.context.active_object
    fill.name = "Fill_Light"
    fill.data.energy = 180.0 * energy_mult
    fill.data.size = 3.5
    fill.data.color = (0.92, 0.95, 1.0)

    # Rim / Accent light: sharp backlight
    bpy.ops.object.light_add(type='AREA', location=(1.0, 4.0, 3.5))
    rim = bpy.context.active_object
    rim.name = "Rim_Light"
    rim.data.energy = 380.0 * energy_mult
    rim.data.size = 1.8
    rim.data.color = (1.0, 0.85, 0.75)

    # Bottom soft bounce to prevent pitch-black underbelly
    bpy.ops.object.light_add(type='AREA', location=(0.0, 0.0, -2.5))
    bounce = bpy.context.active_object
    bounce.name = "Bounce_Light"
    bounce.data.energy = 60.0 * energy_mult
    bounce.data.size = 4.0
    bounce.data.color = (0.9, 0.9, 0.9)

# -----------------------------------------------------------------------------
# 1. CHARGER FLUX
# -----------------------------------------------------------------------------
def build_charger_flux():
    print("Building Charger Flux...")
    scene = reset_scene()
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024

    # Materials
    mat_charcoal = create_material("Charcoal_PBT", base_color=(0.11, 0.12, 0.13, 1.0), metallic=0.05, roughness=0.35)
    mat_orange = create_material("Nova_Orange", base_color=(0.88, 0.32, 0.12, 1.0), metallic=0.0, roughness=0.4)
    mat_metal = create_material("Alu_Metal", base_color=(0.7, 0.72, 0.75, 1.0), metallic=0.92, roughness=0.2)
    mat_gold = create_material("Gold_Pin", base_color=(0.95, 0.75, 0.2, 1.0), metallic=0.98, roughness=0.15)
    mat_inner_port = create_material("Port_Interior", base_color=(0.03, 0.03, 0.03, 1.0), metallic=0.0, roughness=0.6)
    mat_led = create_material("LED_Glow", base_color=(0.2, 1.0, 0.4, 1.0), emission_color=(0.2, 1.0, 0.4, 1.0), emission_strength=15.0)

    # Main Body: Cube bevelled
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0), scale=(0.85, 1.25, 1.35))
    body = bpy.context.active_object
    body.name = "Charger_Body"
    body.data.materials.append(mat_charcoal)
    bev = body.modifiers.new(name="Bevel", type='BEVEL')
    bev.width = 0.08
    bev.segments = 5
    bpy.ops.object.shade_smooth()

    # Front Face Bevel Insert
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.26, 0), scale=(0.76, 0.04, 1.25))
    front = bpy.context.active_object
    front.name = "Front_Panel"
    front.data.materials.append(mat_charcoal)
    fbev = front.modifiers.new(name="Bevel", type='BEVEL')
    fbev.width = 0.03
    fbev.segments = 3

    # Orange Accent Pinstripe along top/side
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.36), scale=(0.86, 1.26, 0.025))
    stripe = bpy.context.active_object
    stripe.name = "Accent_Stripe"
    stripe.data.materials.append(mat_orange)

    # LED Indicator
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.02, location=(0.26, -1.29, 0.95), rotation=(math.radians(90), 0, 0))
    led = bpy.context.active_object
    led.data.materials.append(mat_led)

    # USB-C Port 1 (Top)
    def add_usbc_port(loc_z, name):
        # Outer metal ring
        bpy.ops.mesh.primitive_cylinder_add(radius=0.14, depth=0.06, location=(0, -1.28, loc_z), rotation=(math.radians(90), 0, 0), scale=(1.8, 1.0, 0.75))
        port = bpy.context.active_object
        port.name = name
        port.data.materials.append(mat_metal)
        # Inner void
        bpy.ops.mesh.primitive_cylinder_add(radius=0.11, depth=0.08, location=(0, -1.29, loc_z), rotation=(math.radians(90), 0, 0), scale=(1.7, 1.0, 0.65))
        void = bpy.context.active_object
        void.data.materials.append(mat_inner_port)
        # Center tongue pin
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.285, loc_z), scale=(0.14, 0.04, 0.02))
        pin = bpy.context.active_object
        pin.data.materials.append(mat_gold)

    add_usbc_port(0.5, "USB_C_1")
    add_usbc_port(0.05, "USB_C_2")

    # USB-A Port (Bottom)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.28, -0.45), scale=(0.38, 0.06, 0.22))
    usba_frame = bpy.context.active_object
    usba_frame.data.materials.append(mat_metal)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.29, -0.45), scale=(0.34, 0.08, 0.18))
    usba_void = bpy.context.active_object
    usba_void.data.materials.append(mat_inner_port)
    # Orange USB-A plastic tongue
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.28, -0.41), scale=(0.32, 0.05, 0.05))
    usba_tongue = bpy.context.active_object
    usba_tongue.data.materials.append(mat_orange)

    # Foldable US/EU Prongs on the back
    for x_offset in [-0.22, 0.22]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x_offset, 1.4, -0.3), scale=(0.04, 0.25, 0.18))
        prong = bpy.context.active_object
        prong.data.materials.append(mat_metal)

    # Lighting & Camera
    setup_studio_lighting(energy_mult=1.1)

    # Camera at dynamic 3/4 angle
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = 72
    cam_obj = bpy.data.objects.new("Camera", cam_data)
    scene.collection.objects.link(cam_obj)
    cam_obj.location = (2.8, -3.2, 1.8)
    cam_obj.rotation_euler = (math.radians(65), 0, math.radians(40))
    scene.camera = cam_obj

    # Save & Render
    blend_path = os.path.join(SCENES_DIR, "charger_flux.blend")
    png_path = os.path.join(IMAGES_DIR, "charger-flux.png")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    scene.render.filepath = png_path
    bpy.ops.render.render(write_still=True)
    print("Charger Flux rendered ->", png_path)

# -----------------------------------------------------------------------------
# 2. NOVADESK MAT
# -----------------------------------------------------------------------------
def build_novadesk_mat():
    print("Building NovaDesk Mat...")
    scene = reset_scene()
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024

    # Materials
    mat_felt = create_material("Anthracite_Felt", base_color=(0.14, 0.15, 0.16, 1.0), metallic=0.0, roughness=0.88)
    mat_leather = create_material("Saddle_Leather", base_color=(0.42, 0.22, 0.11, 1.0), metallic=0.0, roughness=0.45, coat_weight=0.3)
    mat_brass = create_material("Brass_Rivet", base_color=(0.85, 0.65, 0.25, 1.0), metallic=0.95, roughness=0.18)
    mat_stitch = create_material("Stitch_Thread", base_color=(0.28, 0.29, 0.31, 1.0), metallic=0.0, roughness=0.6)

    # Main Mat Body
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0), scale=(3.4, 1.8, 0.04))
    mat_obj = bpy.context.active_object
    mat_obj.name = "Desk_Mat"
    mat_obj.data.materials.append(mat_felt)
    bev = mat_obj.modifiers.new(name="Bevel", type='BEVEL')
    bev.width = 0.06
    bev.segments = 5
    bpy.ops.object.shade_smooth()

    # Perimeter Stitched Border (represented as raised rim loop)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.022), scale=(3.32, 1.72, 0.01))
    stitch = bpy.context.active_object
    stitch.name = "Stitch_Track"
    stitch.data.materials.append(mat_stitch)
    sbev = stitch.modifiers.new(name="Bevel", type='BEVEL')
    sbev.width = 0.02
    sbev.segments = 3

    # Leather Brand Tag in Top Right
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.35, 0.72, 0.035), scale=(0.35, 0.18, 0.015))
    tag = bpy.context.active_object
    tag.name = "Leather_Tag"
    tag.data.materials.append(mat_leather)
    tbev = tag.modifiers.new(name="Bevel", type='BEVEL')
    tbev.width = 0.01
    tbev.segments = 3

    # Copper Rivet on Tag
    bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.02, location=(1.25, 0.72, 0.045))
    rivet = bpy.context.active_object
    rivet.name = "Brass_Rivet"
    rivet.data.materials.append(mat_brass)

    # Embossed Logo Mark on Tag
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.42, 0.72, 0.044), scale=(0.12, 0.04, 0.005))
    logo = bpy.context.active_object
    logo.name = "Emboss_Mark"
    logo.data.materials.append(mat_felt)

    # Lighting & Camera
    setup_studio_lighting(energy_mult=1.0)

    # Perspective Camera looking down at 45 deg angle
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = 55
    cam_obj = bpy.data.objects.new("Camera", cam_data)
    scene.collection.objects.link(cam_obj)
    cam_obj.location = (2.2, -3.2, 3.2)
    cam_obj.rotation_euler = (math.radians(48), 0, math.radians(35))
    scene.camera = cam_obj

    # Save & Render
    blend_path = os.path.join(SCENES_DIR, "mat_novadesk.blend")
    png_path = os.path.join(IMAGES_DIR, "mat-novadesk.png")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    scene.render.filepath = png_path
    bpy.ops.render.render(write_still=True)
    print("NovaDesk Mat rendered ->", png_path)

# -----------------------------------------------------------------------------
# 3. LIGHT BEAM
# -----------------------------------------------------------------------------
def build_light_beam():
    print("Building Light Beam...")
    scene = reset_scene()
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024

    # Materials
    mat_alu = create_material("Anodized_Alu", base_color=(0.16, 0.17, 0.18, 1.0), metallic=0.92, roughness=0.28)
    mat_gunmetal = create_material("Gunmetal_Mount", base_color=(0.12, 0.13, 0.14, 1.0), metallic=0.85, roughness=0.35)
    mat_diffuser = create_material("Frosted_Diffuser", base_color=(0.95, 0.95, 0.92, 1.0), metallic=0.0, roughness=0.45,
                                   emission_color=(1.0, 0.94, 0.85, 1.0), emission_strength=4.5)
    mat_accent = create_material("Orange_Ring", base_color=(0.88, 0.32, 0.12, 1.0), metallic=0.0, roughness=0.3)
    mat_glass_btn = create_material("Glass_Sensor", base_color=(0.05, 0.05, 0.05, 1.0), metallic=0.2, roughness=0.1, coat_weight=0.8)

    # Main Cylindrical Light Bar (Length 450mm scale)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.14, depth=3.2, location=(0, 0, 0), rotation=(0, math.radians(90), 0))
    bar = bpy.context.active_object
    bar.name = "Light_Bar"
    bar.data.materials.append(mat_alu)
    bpy.ops.object.shade_smooth()

    # Diffuser Strip along underside
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.06, -0.11), scale=(2.9, 0.12, 0.03))
    diff = bpy.context.active_object
    diff.name = "Diffuser"
    diff.data.materials.append(mat_diffuser)

    # End Caps
    for x_end in [-1.6, 1.6]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.142, depth=0.04, location=(x_end, 0, 0), rotation=(0, math.radians(90), 0))
        cap = bpy.context.active_object
        cap.data.materials.append(mat_alu)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.138, depth=0.015, location=(x_end * 1.01, 0, 0), rotation=(0, math.radians(90), 0))
        ring = bpy.context.active_object
        ring.data.materials.append(mat_accent)

    # Center Sensor Touch Dial
    bpy.ops.mesh.primitive_cylinder_add(radius=0.09, depth=0.03, location=(0, 0.02, 0.13), rotation=(math.radians(15), 0, 0))
    dial = bpy.context.active_object
    dial.data.materials.append(mat_glass_btn)

    # Monitor Clamp & Counterweight Base
    # Pivot joint arm
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.26, 0.04), scale=(0.28, 0.36, 0.16))
    joint = bpy.context.active_object
    joint.name = "Hinge_Joint"
    joint.data.materials.append(mat_gunmetal)
    jbev = joint.modifiers.new(name="Bevel", type='BEVEL')
    jbev.width = 0.03
    jbev.segments = 3

    # Heavy Counterweight Arm extending down and back
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.65, -0.25), scale=(0.26, 0.45, 0.32), rotation=(math.radians(-25), 0, 0))
    cweight = bpy.context.active_object
    cweight.name = "Counterweight"
    cweight.data.materials.append(mat_gunmetal)
    cbev = cweight.modifiers.new(name="Bevel", type='BEVEL')
    cbev.width = 0.04
    cbev.segments = 4

    # Lighting & Camera
    setup_studio_lighting(energy_mult=1.1)

    # Dynamic perspective camera showing bar profile & clamp
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = 65
    cam_obj = bpy.data.objects.new("Camera", cam_data)
    scene.collection.objects.link(cam_obj)
    cam_obj.location = (2.6, -3.5, 1.4)
    cam_obj.rotation_euler = (math.radians(72), 0, math.radians(36))
    scene.camera = cam_obj

    # Save & Render
    blend_path = os.path.join(SCENES_DIR, "light_beam.blend")
    png_path = os.path.join(IMAGES_DIR, "light-beam.png")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    scene.render.filepath = png_path
    bpy.ops.render.render(write_still=True)
    print("Light Beam rendered ->", png_path)

# -----------------------------------------------------------------------------
# 4. EXPLODED VIEW K75
# -----------------------------------------------------------------------------
def build_exploded_k75():
    print("Building Exploded K75 Hardware Architecture...")
    scene = reset_scene()
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 1200

    # Materials
    mat_case_cnc = create_material("CNC_Alu_6063", base_color=(0.13, 0.14, 0.15, 1.0), metallic=0.9, roughness=0.32)
    mat_brass_weight = create_material("PVD_Mirror_Brass", base_color=(0.95, 0.78, 0.32, 1.0), metallic=0.98, roughness=0.08)
    mat_silicone = create_material("Molded_Silicone", base_color=(0.82, 0.82, 0.80, 1.0), metallic=0.0, roughness=0.6)
    mat_pcb = create_material("Matte_Black_PCB", base_color=(0.06, 0.07, 0.08, 1.0), metallic=0.1, roughness=0.45)
    mat_gold_trace = create_material("ENIG_Gold_Pad", base_color=(0.96, 0.82, 0.35, 1.0), metallic=0.96, roughness=0.15)
    mat_poron = create_material("Poron_Foam", base_color=(0.03, 0.03, 0.03, 1.0), metallic=0.0, roughness=0.95)
    mat_fr4 = create_material("FR4_Plate", base_color=(0.10, 0.11, 0.12, 1.0), metallic=0.3, roughness=0.4)
    mat_gasket_tab = create_material("Poron_Gaskets", base_color=(0.88, 0.42, 0.15, 1.0), metallic=0.0, roughness=0.7)
    
    # Switch Materials
    mat_sw_pc = create_material("Switch_Polycarb_Top", base_color=(0.92, 0.94, 0.96, 0.6), metallic=0.05, roughness=0.18, transmission=0.85)
    mat_sw_stem = create_material("Switch_POM_Stem", base_color=(0.92, 0.36, 0.10, 1.0), metallic=0.0, roughness=0.35)
    mat_sw_spring = create_material("Gold_Spring", base_color=(0.95, 0.8, 0.25, 1.0), metallic=0.95, roughness=0.15)
    mat_sw_bottom = create_material("Switch_Nylon_Bottom", base_color=(0.15, 0.16, 0.18, 1.0), metallic=0.0, roughness=0.4)

    # Keycap Materials
    mat_kc_cream = create_material("PBT_Cream_Alpha", base_color=(0.92, 0.89, 0.83, 1.0), metallic=0.0, roughness=0.42)
    mat_kc_slate = create_material("PBT_Slate_Mod", base_color=(0.20, 0.22, 0.25, 1.0), metallic=0.0, roughness=0.4)
    mat_kc_accent = create_material("PBT_Nova_Orange", base_color=(0.90, 0.35, 0.12, 1.0), metallic=0.0, roughness=0.38)
    mat_kc_legend = create_material("PBT_DyeSub_Dark", base_color=(0.12, 0.13, 0.14, 1.0), metallic=0.0, roughness=0.5)

    width = 3.6    # X scale
    depth = 1.6    # Y scale
    
    # -------------------------------------------------------------------------
    # LAYER 1: PVD Mirror Brass Weight Bar (Z = -1.2)
    # -------------------------------------------------------------------------
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, -1.2), scale=(2.2, 0.6, 0.05))
    weight_bar = bpy.context.active_object
    weight_bar.name = "Layer1_Brass_Weight"
    weight_bar.data.materials.append(mat_brass_weight)
    wbev = weight_bar.modifiers.new(name="Bevel", type='BEVEL')
    wbev.width = 0.015
    wbev.segments = 3

    # -------------------------------------------------------------------------
    # LAYER 2: CNC 6063 Aluminum Bottom Case (Z = -0.85)
    # -------------------------------------------------------------------------
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, -0.85), scale=(width, depth, 0.14))
    case_bot = bpy.context.active_object
    case_bot.name = "Layer2_Bottom_Case"
    case_bot.data.materials.append(mat_case_cnc)
    cbev = case_bot.modifiers.new(name="Bevel", type='BEVEL')
    cbev.width = 0.04
    cbev.segments = 4

    # Type-C cutout on rear
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.9, depth * 0.51, -0.82), scale=(0.18, 0.04, 0.06))
    port_cut = bpy.context.active_object
    port_cut.data.materials.append(mat_brass_weight)

    # -------------------------------------------------------------------------
    # LAYER 3: Molded Silicone Acoustic Dampener (Z = -0.5)
    # -------------------------------------------------------------------------
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, -0.5), scale=(width * 0.94, depth * 0.92, 0.06))
    silicone = bpy.context.active_object
    silicone.name = "Layer3_Silicone_Dampener"
    silicone.data.materials.append(mat_silicone)
    sbev = silicone.modifiers.new(name="Bevel", type='BEVEL')
    sbev.width = 0.02
    sbev.segments = 3

    # -------------------------------------------------------------------------
    # LAYER 4: Matte Black PCB with Gold ENIG Pads (Z = -0.15)
    # -------------------------------------------------------------------------
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, -0.15), scale=(width * 0.95, depth * 0.93, 0.035))
    pcb = bpy.context.active_object
    pcb.name = "Layer4_PCB"
    pcb.data.materials.append(mat_pcb)
    
    # Flex cuts & decorative gold trace strips
    for x_i in [-1.2, -0.6, 0.0, 0.6, 1.2]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x_i, 0, -0.13), scale=(0.04, depth * 0.8, 0.005))
        trace = bpy.context.active_object
        trace.data.materials.append(mat_gold_trace)

    # -------------------------------------------------------------------------
    # LAYER 5: Poron Switch Pad & Plate Foam (Z = 0.2)
    # -------------------------------------------------------------------------
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.2), scale=(width * 0.95, depth * 0.93, 0.05))
    foam = bpy.context.active_object
    foam.name = "Layer5_Poron_Foam"
    foam.data.materials.append(mat_poron)

    # -------------------------------------------------------------------------
    # LAYER 6: FR4 Gasket Plate with Silicone Tabs (Z = 0.55)
    # -------------------------------------------------------------------------
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.55), scale=(width * 0.96, depth * 0.94, 0.04))
    plate = bpy.context.active_object
    plate.name = "Layer6_FR4_Plate"
    plate.data.materials.append(mat_fr4)

    # Gasket isolation tabs around perimeter
    for gx in [-1.6, -0.8, 0.0, 0.8, 1.6]:
        for gy in [-depth * 0.48, depth * 0.48]:
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(gx, gy, 0.55), scale=(0.14, 0.05, 0.06))
            gtab = bpy.context.active_object
            gtab.data.materials.append(mat_gasket_tab)

    # -------------------------------------------------------------------------
    # LAYER 7: Mechanical Switches Array (Z = 0.9)
    # -------------------------------------------------------------------------
    # Build representative 75% switch grid
    cols = 15
    rows = 5
    x_step = (width * 0.88) / (cols - 1)
    y_step = (depth * 0.84) / (rows - 1)
    x_start = - (width * 0.88) / 2
    y_start = - (depth * 0.84) / 2

    for r in range(rows):
        for c in range(cols):
            # Skip spacebar gaps
            if r == 0 and c in [4, 5, 6, 7, 8, 9, 10]:
                if c != 7: # place single center switch for spacebar
                    continue

            sx = x_start + c * x_step
            sy = y_start + r * y_step
            sz = 0.9

            # Switch housing
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, sy, sz), scale=(0.09, 0.09, 0.06))
            sw_house = bpy.context.active_object
            sw_house.data.materials.append(mat_sw_pc)

            # Switch stem (orange cross)
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, sy, sz + 0.04), scale=(0.035, 0.035, 0.04))
            sw_stem = bpy.context.active_object
            sw_stem.data.materials.append(mat_sw_stem)

    # -------------------------------------------------------------------------
    # LAYER 8: Keycaps Set 75% Layout (Z = 1.35)
    # -------------------------------------------------------------------------
    # Specific keys with accurate Cherry profiles and distinct labels/colors
    key_labels = [
        # row 4: Function row
        [("ESC", "accent"), ("F1", "cream"), ("F2", "cream"), ("F3", "cream"), ("F4", "cream"),
         ("F5", "cream"), ("F6", "cream"), ("F7", "cream"), ("F8", "cream"), ("F9", "cream"),
         ("F10", "cream"), ("F11", "cream"), ("F12", "cream"), ("DEL", "slate"), ("MUTE", "accent")],
        # row 3: Numbers
        [("`~", "slate"), ("1", "cream"), ("2", "cream"), ("3", "cream"), ("4", "cream"),
         ("5", "cream"), ("6", "cream"), ("7", "cream"), ("8", "cream"), ("9", "cream"),
         ("0", "cream"), ("-", "cream"), ("=", "cream"), ("BACK", "slate"), ("PGUP", "slate")],
        # row 2: QWERTY
        [("TAB", "slate"), ("Q", "cream"), ("W", "cream"), ("E", "cream"), ("R", "cream"),
         ("T", "cream"), ("Y", "cream"), ("U", "cream"), ("I", "cream"), ("O", "cream"),
         ("P", "cream"), ("[", "cream"), ("]", "cream"), ("\\", "cream"), ("PGDN", "slate")],
        # row 1: Home row
        [("CAPS", "slate"), ("A", "cream"), ("S", "cream"), ("D", "cream"), ("F", "cream"),
         ("G", "cream"), ("H", "cream"), ("J", "cream"), ("K", "cream"), ("L", "cream"),
         (";", "cream"), ("'", "cream"), ("ENTER", "accent"), ("END", "slate")],
        # row 0: Bottom row
        [("CTRL", "slate"), ("WIN", "slate"), ("ALT", "slate"), ("SPACE", "cream"), ("ALT", "slate"),
         ("FN", "slate"), ("LEFT", "slate"), ("UP", "slate"), ("DOWN", "slate"), ("RIGHT", "slate")]
    ]

    for r_idx, row_data in enumerate(reversed(key_labels)):
        y_pos = y_start + r_idx * y_step
        num_keys = len(row_data)
        cur_x = x_start
        
        for k_idx, (label, color_type) in enumerate(row_data):
            k_width = 0.095
            if label == "SPACE":
                k_width = 0.55
            elif label in ["ENTER", "BACK", "TAB", "CAPS", "SHIFT"]:
                k_width = 0.16

            x_pos = cur_x + k_width / 2
            cur_x += k_width + 0.015

            # Keycap body
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x_pos, y_pos, 1.35), scale=(k_width, 0.095, 0.075))
            kc = bpy.context.active_object
            kc.name = f"Key_{label}"
            
            if color_type == "accent":
                kc.data.materials.append(mat_kc_accent)
            elif color_type == "slate":
                kc.data.materials.append(mat_kc_slate)
            else:
                kc.data.materials.append(mat_kc_cream)

            kcbev = kc.modifiers.new(name="Bevel", type='BEVEL')
            kcbev.width = 0.015
            kcbev.segments = 3

            # Crisp embossed legend bar/letter mark on keycap top
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x_pos, y_pos, 1.39), scale=(k_width * 0.45, 0.02, 0.005))
            leg = bpy.context.active_object
            leg.name = f"Legend_{label}"
            leg.data.materials.append(mat_kc_legend)

    # Lighting & Camera
    setup_studio_lighting(energy_mult=1.2)

    # Isometric/Orthographic feel with 85mm portrait telephoto lens looking down and rotated 30 deg
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = 78
    cam_obj = bpy.data.objects.new("Camera", cam_data)
    scene.collection.objects.link(cam_obj)
    cam_obj.location = (4.8, -4.5, 4.2)
    cam_obj.rotation_euler = (math.radians(52), 0, math.radians(45))
    scene.camera = cam_obj

    # Save & Render
    blend_path = os.path.join(SCENES_DIR, "exploded_k75.blend")
    png_path = os.path.join(IMAGES_DIR, "exploded-k75.png")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    scene.render.filepath = png_path
    bpy.ops.render.render(write_still=True)
    print("Exploded K75 rendered ->", png_path)

if __name__ == "__main__":
    build_charger_flux()
    build_novadesk_mat()
    build_light_beam()
    build_exploded_k75()
    print("ALL 4 3D ASSETS SUCCESSFULLY CREATED AND RENDERED!")
