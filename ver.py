# Render de control en Cycles. Uso:
# blender -b tomi_v4.blend -P ver.py -- <modo> <salida.png> [ancho alto muestras [franja n_franjas]]
# con franja/n_franjas renderiza solo esa banda horizontal (con 32 px de solape) para repartir en la nube
# modos: cara (frente), cara34, ojo (detalle), cuerpo (plano entero con ropa)
import bpy, sys, os, math
from mathutils import Vector
args = sys.argv[sys.argv.index('--') + 1:]
modo, salida = args[0], os.path.abspath(args[1])
W, H, SPP = (int(args[2]), int(args[3]), int(args[4])) if len(args) > 4 else (640, 800, 32)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
sc.cycles.samples = SPP; sc.cycles.use_denoising = True
sc.cycles.max_bounces = 8; sc.cycles.transparent_max_bounces = 16
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = W, H, 100
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
sc.render.film_transparent = False
OJOS = Vector((0, -0.137, 1.666))

def luz(nombre, pos, mira, energia, tam, color=(1, 1, 1)):
    l = bpy.data.lights.new(nombre, 'AREA'); l.energy = energia; l.size = tam; l.color = color
    o = bpy.data.objects.new(nombre, l); sc.collection.objects.link(o)
    o.location = pos; o.rotation_euler = (Vector(mira) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    return o
cuerpo = modo == 'cuerpo'
foco = Vector((0, -0.10, 1.25)) if cuerpo else OJOS
k = 3.0 if cuerpo else 1.0
# luz de cine: llave grande y suave (ventana) adelante a la izquierda, casi sin relleno,
# contraluz frío alto y tenue (más fuerte atraviesa el pelo y lo pone naranja)
luz('Llave', foco + Vector((-1.25, -0.55, 0.5)) * k, foco, 50 * k * k, 1.2 * k, (1.0, 0.94, 0.87))
luz('Relleno', foco + Vector((1.3, -0.9, -0.1)) * k, foco, 2.5 * k * k, 2.0 * k, (0.85, 0.92, 1.0))
luz('Borde', foco + Vector((0.6, 0.8, 0.9)) * k, foco, 18 * k * k, 0.6 * k, (0.88, 0.93, 1.0))
# fondo: pared gris cálida lejos
bpy.ops.mesh.primitive_plane_add(size=12, location=(0, 1.6, 1.5), rotation=(math.radians(90), 0, 0))
fondo = bpy.context.object
mf = bpy.data.materials.new('Fondo'); mf.use_nodes = True
mf.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.035, 0.03, 0.026, 1)
fondo.data.materials.append(mf)

cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); sc.collection.objects.link(cam); sc.camera = cam
cd = cam.data; cd.dof.use_dof = True
if modo == 'cara':
    cd.lens = 85; pos = OJOS + Vector((0, -0.95, -0.02)); mira = OJOS + Vector((0, 0, -0.035)); cd.dof.aperture_fstop = 4.0
elif modo == 'cara34':
    cd.lens = 85; a = math.radians(-35); pos = OJOS + Vector((0.95 * math.sin(a), -0.95 * math.cos(a), -0.02)); mira = OJOS + Vector((0, 0, -0.035)); cd.dof.aperture_fstop = 4.0
elif modo == 'ojo':
    cd.lens = 100; pos = OJOS + Vector((-0.031 - 0.06, -0.33, 0.0)); mira = OJOS + Vector((-0.031, 0, -0.005)); cd.dof.aperture_fstop = 8.0
else:
    cd.lens = 50; pos = foco + Vector((0.6, -3.6, 0.05)); mira = foco; cd.dof.aperture_fstop = 5.6
cam.location = pos; cam.rotation_euler = (mira - pos).to_track_quat('-Z', 'Y').to_euler()
cd.dof.focus_distance = (OJOS - pos).length if not cuerpo else (foco - pos).length
if len(args) > 6:   # banda i de n (0 = arriba), recortada; une_franjas.py la vuelve a juntar
    i, n = int(args[5]), int(args[6]); sol = 32 / H
    sc.render.use_border = True; sc.render.use_crop_to_border = True
    sc.render.border_min_x, sc.render.border_max_x = 0, 1
    sc.render.border_max_y = min(1, 1 - i / n + sol); sc.render.border_min_y = max(0, 1 - (i + 1) / n - sol)
sc.render.filepath = salida
bpy.ops.render.render(write_still=True)
