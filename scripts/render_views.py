"""Render review views, restoring the assembly after the cutaway illustration."""
import bpy
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
scene=bpy.context.scene; cam=scene.camera
saved=(cam.matrix_world.copy(),cam.data.ortho_scale,scene.render.resolution_x,scene.render.resolution_y,scene.render.filepath)
def render(name,loc,target,scale,width=1000,height=1200):
    cam.location=loc; cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.ortho_scale=scale; scene.render.resolution_x=width;scene.render.resolution_y=height
    scene.render.filepath=str(ROOT/'renders'/name); bpy.ops.render.render(write_still=True)
render('percival-front.png',(0,-1.5,.30),(0,0,.30),.70)
render('percival-side.png',(1.5,0,.30),(0,0,.30),.70)
render('percival-top.png',(0,.005,1.5),(0,.005,.3),.37,1000,1000)
visibility={ob:ob.hide_render for ob in scene.objects}
try:
    for ob in scene.objects:
        pid=ob.get('part_id','')
        if pid in ['P01','P03','P04L','P04R','P10','P11','P12'] or (pid.endswith('L') and pid.startswith(('P2','P3'))):
            ob.hide_render=True
    render('percival-cutaway.png',(.80,-1.45,.79),(0,.020,.298),.76)
finally:
    for ob,state in visibility.items(): ob.hide_render=state
    cam.matrix_world=saved[0];cam.data.ortho_scale=saved[1]
    scene.render.resolution_x=saved[2];scene.render.resolution_y=saved[3];scene.render.filepath=saved[4]
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.region_3d.view_perspective='CAMERA'
        area.spaces.active.shading.type='MATERIAL'
        area.spaces.active.overlay.show_overlays=False
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'design'/'percival.blend'))
result={'views':['percival-front.png','percival-side.png','percival-top.png','percival-cutaway.png'],'saved_scene':scene.name}
