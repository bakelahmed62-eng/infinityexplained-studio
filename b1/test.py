import bpy, math

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = 24
sc.render.resolution_x = 540
sc.render.resolution_y = 960
sc.render.filepath = 'out/blender_test.png'

world = bpy.data.worlds.new('w')
sc.world = world
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs[0].default_value = (0.01, 0.02, 0.06, 1)
bg.inputs[1].default_value = 0.8


def emission(name, color, strength):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    e = nt.nodes.new('ShaderNodeEmission')
    e.inputs[0].default_value = color
    e.inputs[1].default_value = strength
    o = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(e.outputs[0], o.inputs[0])
    return m


def diffuse(name, color):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes['Principled BSDF'].inputs[0].default_value = color
    return m


def put(obj, m):
    obj.data.materials.append(m)
    return obj


ivory = diffuse('ivory', (0.9, 0.92, 0.96, 1))
blue = diffuse('blue', (0.05, 0.3, 0.9, 1))
dark = diffuse('dark', (0.02, 0.03, 0.06, 1))
glow = emission('glow', (1.0, 0.6, 0.1, 1), 12.0)

bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
put(bpy.context.object, dark)
for i in range(5):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-2 + i * 1.0, 0, 0.25 + i * 0.25), scale=(0.5, 1.2, 0.25 + i * 0.25))
    put(bpy.context.object, blue)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.28, location=(1.9, 0, 1.9))
put(bpy.context.object, ivory)
bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.8, location=(1.9, 0, 1.35))
put(bpy.context.object, blue)
bpy.ops.mesh.primitive_torus_add(major_radius=1.6, minor_radius=0.03, location=(1.9, 0, 1.5), rotation=(math.radians(90), 0, 0))
put(bpy.context.object, glow)
bpy.ops.object.light_add(type='AREA', location=(0, -4, 5))
bpy.context.object.data.energy = 400
bpy.ops.object.camera_add(location=(0, -7, 2.2), rotation=(math.radians(82), 0, 0))
sc.camera = bpy.context.object
bpy.ops.render.render(write_still=True)
