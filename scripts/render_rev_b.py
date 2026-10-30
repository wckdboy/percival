"""Review renders for Rev B, preserving the final hero camera and pose."""
import bpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
scene=bpy.data.scenes['Percival • Rev B / BDX character study'];bpy.context.window.scene=scene
cam=scene.camera;original=(cam.matrix_world.copy(),cam.data.ortho_scale,scene.render.resolution_x,scene.render.resolution_y,scene.render.filepath)
floor=scene.objects['B • studio ground'];floor.dimensions=(200,200,.001);floor.location.z=-.0015
def render(name,loc,target,scale,w=1100,h=1300):
    cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.ortho_scale=scale;scene.render.resolution_x=w;scene.render.resolution_y=h
    scene.render.filepath=str(ROOT/'renders/rev-b'/name);bpy.ops.render.render(write_still=True)
try:
    floor.hide_render=True
    render('percival-bdx-front.png',(0,-1.5,.29),(0,0,.29),.68)
    floor.hide_render=False
    render('percival-bdx-side.png',(1.5,-.10,.35),(0,0,.29),.68)
    render('percival-bdx-head.png',(.85,-1.5,.72),(0,-.015,.452),.39,1200,1000)
finally:
    floor.hide_render=False
    cam.matrix_world=original[0];cam.data.ortho_scale=original[1]
    scene.render.resolution_x=original[2];scene.render.resolution_y=original[3];scene.render.filepath=original[4]
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'design/percival-rev-b-bdx.blend'))
result={'views':3,'saved_file':bpy.data.filepath,'status':'Illustrative views only; not physical pose validation'}
