"""Review renders for Rev D, preserving the final hero camera and pose."""
import bpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
scene=bpy.data.scenes['Percival • Rev D / reference proportions'];bpy.context.window.scene=scene
cam=scene.camera;original=(cam.matrix_world.copy(),cam.data.ortho_scale,scene.render.resolution_x,scene.render.resolution_y,scene.render.filepath)
floor=scene.objects['D • studio ground'];floor.dimensions=(200,200,.001);floor.location.z=-.0015
def render(name,loc,target,scale,w=1100,h=1300):
    cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.ortho_scale=scale;scene.render.resolution_x=w;scene.render.resolution_y=h
    scene.render.filepath=str(ROOT/'renders/rev-d'/name);bpy.ops.render.render(write_still=True)
try:
    floor.hide_render=True
    render('percival-rev-d-front.png',(0,-1.5,.280),(0,0,.280),.65)
    floor.hide_render=False
    render('percival-rev-d-side.png',(1.5,-.10,.33),(0,0,.280),.65)
    render('percival-rev-d-top.png',(0,-.001,1.7),(0,0,.28),.40,1200,1100)
    render('percival-rev-d-head.png',(.85,-1.5,.71),(0,-.010,.435),.38,1200,1000)
finally:
    floor.hide_render=False
    cam.matrix_world=original[0];cam.data.ortho_scale=original[1]
    scene.render.resolution_x=original[2];scene.render.resolution_y=original[3];scene.render.filepath=original[4]
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'design/percival-rev-d-reference.blend'))
result={'views':4,'saved_file':bpy.data.filepath,'status':'Illustrative views only; not physical pose validation'}
