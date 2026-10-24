# Mide segundos por cuadro de distintos motores con la misma toma (rostro 3/4, 1080x1350).
# blender -b tomi_v3.blend -P bench.py -- <motor> <salida.png>    motor: eevee | cyc16 | cyc32
import bpy, sys, time
args = sys.argv[sys.argv.index("--") + 1:]; motor, salida = args
sys.argv = [sys.argv[0], "--", "cara34"]
exec(open(bpy.path.abspath("//visor.py"), encoding="utf-8").read())
sc = bpy.context.scene
sc.render.resolution_x, sc.render.resolution_y = 1080, 1350
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Punchy'
if motor == "eevee":
    sc.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
    e = sc.eevee; e.taa_render_samples = 64; e.use_raytracing = True; e.use_shadows = True
    e.ray_tracing_options.resolution_scale = '1'; e.use_fast_gi = False
    for L in bpy.data.lights: L.use_shadow = True
else:
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = int(motor[3:]); sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.05; sc.cycles.use_denoising = True; sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    sc.cycles.max_bounces = 6; sc.render.use_persistent_data = True
sc.render.filepath = salida
t = time.time(); bpy.ops.render.render(write_still=True); print("TIEMPO", motor, round(time.time() - t, 1), "s")
