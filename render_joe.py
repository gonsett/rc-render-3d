# Render de un tramo del episodio Joe vs «Es caro» (lo llama ep_joe.yml). Cuadros: t, t+N, t+2N... dentro de 1..FIN
import bpy, sys, time, os
a = sys.argv[sys.argv.index("--") + 1:]
t, n, out, pct, muestras = int(a[0]), int(a[1]), a[2], int(a[3]), int(a[4])
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = muestras
sc.render.use_persistent_data = True; sc.render.resolution_percentage = pct
sc.render.image_settings.file_format = 'PNG'
os.makedirs(out, exist_ok=True)
for f in range(sc.frame_start + t, sc.frame_end + 1, n):
    t0 = time.time(); sc.frame_set(f); sc.render.filepath = f"{out}/c{f:04d}.png"
    bpy.ops.render.render(write_still=True); print("CUADRO", f, round(time.time() - t0, 1), flush=True)
