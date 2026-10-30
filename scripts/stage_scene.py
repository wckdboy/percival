"""Lighting and a review camera, through Blender MCP."""
import bpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
scene=bpy.context.scene
stage=bpy.data.collections.new("90 • STUDIO — visualization only")
scene.collection.children.link(stage)
def own(ob):
    for c in list(ob.users_collection): c.objects.unlink(ob)
    stage.objects.link(ob)
def aim(ob,point): ob.rotation_euler=(Vector(point)-ob.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.001))
ground=bpy.context.object; ground.name="STUDIO • floor"; own(ground)
m=bpy.data.materials.new("Studio • slate"); m.diffuse_color=(.07,.085,.105,1); ground.data.materials.append(m)
for name,loc,power,size in [("Key",(.5,-.7,1.2),25,1.0),("Fill",(-.6,-.2,.7),15,.8),("Rim",(.2,.6,1.0),35,.7)]:
    data=bpy.data.lights.new(name,'AREA'); data.energy=power; data.shape='DISK'; data.size=size
    ob=bpy.data.objects.new(name,data); stage.objects.link(ob); ob.location=loc; aim(ob,(0,0,.3))
data=bpy.data.cameras.new("Assembly review"); cam=bpy.data.objects.new("CAM • hero",data); stage.objects.link(cam)
cam.location=(.80,-1.45,.79); aim(cam,(0,.020,.298)); data.type='ORTHO'; data.ortho_scale=.76; data.clip_start=.001
scene.camera=cam
scene.render.engine='CYCLES'; scene.cycles.samples=24; scene.cycles.use_denoising=True
scene.render.resolution_x=1000; scene.render.resolution_y=1200; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
scene.world=bpy.data.worlds.new("Studio • world"); scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.19,.23,.29,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.35
scene.view_settings.view_transform='AgX'
(ROOT/'renders').mkdir(exist_ok=True)
scene.render.filepath=str(ROOT/'renders'/'hardware-baseline.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'design'/'percival.blend'))
bpy.ops.render.render(write_still=True)
result={'render':scene.render.filepath}
