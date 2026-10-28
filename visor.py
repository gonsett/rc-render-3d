# Abre a Tomi en el visor: vista de materiales, encuadre de cuerpo entero y de frente. Con "-- captura.png" renderiza Eevee y sale.
import bpy, sys, math, mathutils
from mathutils import Vector
sc = bpy.context.scene
arm = bpy.data.objects.get("Armature")
mins = Vector((9e9,)*3); maxs = Vector((-9e9,)*3)
for o in bpy.data.objects:
    if o.type == 'MESH':
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c); mins = Vector(map(min, mins, w)); maxs = Vector(map(max, maxs, w))
cen = (mins + maxs) / 2; h = maxs.z - mins.z
# luz de estudio tibia de tres puntos + cámara 85 mm de frente
for n, loc, e, col in [("Key", (1.6, -2.2, cen.z + 1.0), 420, (1, .9, .78)), ("Fill", (-2.2, -1.5, cen.z + .3), 90, (.75, .85, 1)), ("Rim", (0.8, 2.2, cen.z + 1.2), 500, (1, .95, .9))]:
    L = bpy.data.lights.new(n, 'AREA'); L.energy = e; L.size = 1.2; L.color = col
    ob = bpy.data.objects.new(n, L); sc.collection.objects.link(ob); ob.location = loc
    ob.rotation_euler = (Vector(cen) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
cam = bpy.data.cameras.new("Cam"); cam.lens = 85
co = bpy.data.objects.new("Cam", cam); sc.collection.objects.link(co); sc.camera = co
mode = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else ""
tgt = Vector((0.0, -0.13, 1.672)) if "ojos" in mode else Vector((0.0, -0.03, 1.70)) if "pelo" in mode else (Vector((cen.x, cen.y, maxs.z - h * 0.075)) if "cara" in mode else cen)
dist = 0.42 if "ojos" in mode else 0.55 if "pelo" in mode else (1.15 if "cara" in mode else 9.0)
ang = math.radians(150) if 'atras' in mode else (math.radians(35) if '34' in mode else 0.0)
co.location = tgt + Vector((dist * math.sin(ang), -dist * math.cos(ang), 0)); co.rotation_euler = (math.radians(90), 0, ang)
w = bpy.context.scene.world or bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (.035, .033, .03, 1)
if "gesto" in mode:  # cejas levantadas: comprueba que las hebras siguen las claves de forma
    for o in bpy.data.objects:
        ks = o.type == 'MESH' and o.data.shape_keys
        if ks and "browInnerUp" in ks.key_blocks: ks.key_blocks["browInnerUp"].value = 1.0
if mode.endswith(".png"):
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; alta = 'alta' in mode; sc.cycles.samples = 160 if alta else (64 if ('pelo' in mode or 'ojos' in mode) else 24); sc.cycles.use_denoising = True; sc.render.resolution_x, sc.render.resolution_y = (1080, 1350) if alta else ((960, 540) if 'ojos' in mode else (800, 800) if 'pelo' in mode else (640, 800))
    sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Punchy'
    sc.render.filepath = mode.split("|")[-1]; bpy.ops.render.render(write_still=True); print("CAPTURA", sc.render.filepath)
else:
    def vista():
        for a in bpy.context.window_manager.windows[0].screen.areas:
            if a.type == 'VIEW_3D':
                s = a.spaces[0]; s.shading.type = 'MATERIAL'; s.overlay.show_overlays = False
                r = s.region_3d; r.view_location = Vector((cen.x, cen.y, maxs.z - h * 0.3)); r.view_distance = h * 0.9
                r.view_rotation = mathutils.Euler((math.radians(85), 0, 0)).to_quaternion(); r.view_perspective = 'PERSP'
    bpy.app.timers.register(vista, first_interval=1.5)
