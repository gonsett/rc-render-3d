# Render de un tramo del episodio Joe vs «Es caro» (lo llama ep_joe.yml). Cuadros: t, t+N, t+2N... dentro de 1..FIN
import bpy, sys, time, os
a = sys.argv[sys.argv.index("--") + 1:]
t, n, out, pct, muestras = int(a[0]), int(a[1]), a[2], int(a[3]), int(a[4])
aj = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ajustes_joe.py")
if os.path.exists(aj): exec(open(aj).read())
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = muestras
sc.render.use_persistent_data = True; sc.render.resolution_percentage = pct
sc.render.image_settings.file_format = 'PNG'
os.makedirs(out, exist_ok=True)
lista = [int(x) for x in a[5].split(',')] if len(a) > 5 and a[5].strip() else list(range(sc.frame_start, sc.frame_end + 1))
for f in lista[t::n]:
    t0 = time.time(); sc.frame_set(f); sc.render.filepath = f"{out}/c{f:04d}.png"
    bpy.ops.render.render(write_still=True); print("CUADRO", f, round(time.time() - t0, 1), flush=True)
