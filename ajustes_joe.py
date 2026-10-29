# Ajustes del 28/10 sobre escena_joe_pack.blend: cámara del golpe, relleno neutro solo en Joe, denoiser
import bpy
from mathutils import Vector
sc = bpy.context.scene
cam = bpy.data.objects['C_golpe']
fc = cam.animation_data.action
# JOE se deduce de la primera clave vieja: pos(217) = JOE + (1.3, -1.7, 0.45)
cam.animation_data_clear(); sc.frame_set(217)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE' and any(c.type == 'MESH' for c in o.children)]
print("ARMATURES", [(o.name, tuple(round(v, 2) for v in o.location), len(o.children)) for o in arm])
joe = next(o for o in arm if abs(o.location.y + 20) < 1)
JOE = Vector((joe.location.x, joe.location.y, 0.1))
for c, pos, mira in [(217, (0.7, -2.0, 0.45), (0.2, 8, 3.0)), (246, (0.8, -2.4, 0.4), (0.2, 8, 3.6))]:
    p = JOE + Vector(pos); cam.location = p
    cam.rotation_euler = (JOE + Vector(mira) - p).to_track_quat('-Z', 'Y').to_euler()
    cam.keyframe_insert('location', frame=c); cam.keyframe_insert('rotation_euler', frame=c)
# relleno neutro desde atrás, enlazado solo a las mallas de Joe
col = bpy.data.collections.new('SoloJoe')
for m in joe.children_recursive:
    if m.type == 'MESH': col.objects.link(m)
ld = bpy.data.lights.new('RellenoEspalda', 'AREA'); ld.energy = 220; ld.size = 2.5; ld.color = (0.88, 0.92, 1.0)
lo = bpy.data.objects.new('RellenoEspalda', ld); sc.collection.objects.link(lo)
lo.location = JOE + Vector((0.8, -3.5, 2.3))
lo.rotation_euler = (JOE + Vector((0, 0, 1.0)) - lo.location).to_track_quat('-Z', 'Y').to_euler()
lo.light_linking.receiver_collection = col
sc.cycles.use_denoising = True; sc.cycles.denoiser = 'OPENIMAGEDENOISE'
print("AJUSTES OK", tuple(round(v, 2) for v in JOE), len(col.objects))
# foco que sigue los ojos en los primeros planos (cara y silencio): Empty colgado del hueso de la cabeza
from mathutils import Matrix
sc.frame_set(60); dg = bpy.context.evaluated_depsgraph_get(); dg.update()
eo = bpy.data.objects['Eyes_Eyes_0'].evaluated_get(dg)
vs = [eo.matrix_world @ v.co for v in eo.data.vertices]; pe = sum(vs, Vector()) / len(vs)
foco = bpy.data.objects.new('FocoOjos', None); sc.collection.objects.link(foco)
foco.parent = joe; foco.parent_type = 'BONE'; foco.parent_bone = 'mixamorig:Head'
bpy.context.view_layer.update(); foco.matrix_world = Matrix.Translation(pe)
for n in ('C_cara', 'C_silencio'): bpy.data.objects[n].data.dof.focus_object = foco
print('FOCO', tuple(round(v, 3) for v in pe))
