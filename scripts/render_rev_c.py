"""Review renders for Rev C, preserving the final hero camera and pose."""
import bpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
scene=bpy.data.scenes['Percival • Rev C / compact industrial character'];bpy.context.window.scene=scene
cam=scene.camera;original=(cam.matrix_world.copy(),cam.data.ortho_scale,scene.render.resolution_x,scene.render.resolution_y,scene.render.filepath)
floor=scene.objects['C • studio ground'];floor.dimensions=(200,200,.001);floor.location.z=-.0015
def render(name,loc,target,scale,w=1100,h=1300):
    cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.ortho_scale=scale;scene.render.resolution_x=w;scene.render.resolution_y=h
    scene.render.filepath=str(ROOT/'renders/rev-c'/name);bpy.ops.render.render(write_still=True)
try:
    floor.hide_render=True
    render('percival-rev-c-front.png',(0,-1.5,.272),(0,0,.272),.63)
    floor.hide_render=False
    render('percival-rev-c-side.png',(1.5,-.10,.32),(0,0,.272),.63)
    render('percival-rev-c-head.png',(.85,-1.5,.68),(0,-.015,.420),.39,1200,1000)
finally:
    floor.hide_render=False
    cam.matrix_world=original[0];cam.data.ortho_scale=original[1]
    scene.render.resolution_x=original[2];scene.render.resolution_y=original[3];scene.render.filepath=original[4]
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'design/percival-rev-c-chamfer.blend'))
result={'views':3,'saved_file':bpy.data.filepath,'status':'Illustrative views only; not physical pose validation'}
