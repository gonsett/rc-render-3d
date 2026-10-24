# Render de un tramo de cuadros de la escena v3 (lo llama el workflow render.yml).
import bpy, sys, time
a = sys.argv[sys.argv.index("--") + 1:]; ini, fin, out = int(a[0]), int(a[1]), a[2]
sc = bpy.context.scene; sc.camera = bpy.data.objects["CamV3"]
sc.cycles.device = 'CPU'; sc.render.use_persistent_data = True; sc.cycles.samples = int(a[3]) if len(a) > 3 else sc.cycles.samples
for f in range(ini, fin + 1):
    t = time.time(); sc.frame_set(f); sc.render.filepath = f"{out}/f_{f:04d}.png"
    bpy.ops.render.render(write_still=True); print("CUADRO", f, round(time.time() - t, 1), flush=True)
