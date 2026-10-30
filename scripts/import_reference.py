"""Run through Blender MCP. Import real, unscaled URDF geometry into a NEW scene."""
import bpy
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path
from mathutils import Matrix, Euler, Vector

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "reference/toddlerbot/toddlerbot/descriptions/toddlerbot_2xc_gripper"
OUT = ROOT / "design"
OUT.mkdir(exist_ok=True)

scene = bpy.data.scenes.new("Percival • engineering assembly")
bpy.context.window.scene = scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
scene.unit_settings.length_unit = "MILLIMETERS"
scene["design_status"] = "Prototype packaging; custom shell has not undergone walking or physical fit tests"
scene["hardware_base"] = "ToddlerBot 2XC at source dimensions; no geometric rescaling"
scene["source_revision"] = "e337f3b177b4b53abff70b31d1695a7b66cc6d2e"
scene["coordinates"] = "X robot left; Y robot rear; Z up; all stored distances meters"
hardware = bpy.data.collections.new("01 • REAL HARDWARE — ToddlerBot 2XC reference, DO NOT PRINT")
scene.collection.children.link(hardware)
kinematics = bpy.data.collections.new("02 • URDF LINK FRAMES — reference zero pose")
scene.collection.children.link(kinematics)

def move_to(obj, collection):
    for col in list(obj.users_collection): col.objects.unlink(obj)
    collection.objects.link(obj)

def mat(name, rgba, metallic=0, roughness=.45):
    m=bpy.data.materials.new(name); m.diffuse_color=rgba; m.use_nodes=True
    bsdf=m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value=rgba
    bsdf.inputs["Metallic"].default_value=metallic
    bsdf.inputs["Roughness"].default_value=roughness
    return m

graphite=mat("Hardware • graphite",(.052,.059,.067,1),.45,.34)
metal=mat("Hardware • anodized aluminum",(.32,.36,.40,1),.75,.28)
cream=mat("Shell • warm ivory",(.78,.73,.61,1),.03,.35)
purple=mat("Shell • muted violet",(.19,.10,.28,1),.20,.36)
orange=mat("Details • amber orange",(1,.27,.018,1),.15,.32)
black=mat("Face • charcoal",(.015,.020,.026,1),.1,.30)

def xyz(text): return tuple(float(v) for v in text.split())
def origin(elem):
    if elem is None: return Matrix.Identity(4)
    rotation=Euler(xyz(elem.get("rpy","0 0 0")),"XYZ").to_matrix().to_4x4()
    rotation.translation=Vector(xyz(elem.get("xyz","0 0 0")))
    return rotation

robot=ET.parse(MODEL / "toddlerbot_2xc_gripper.urdf").getroot()
frames={}
for link in robot.findall("link"):
    ob=bpy.data.objects.new("LINK • "+link.get("name"),None)
    ob.empty_display_type="PLAIN_AXES"; ob.empty_display_size=.012
    kinematics.objects.link(ob); frames[link.get("name")]=ob
    inertial=link.find("inertial")
    if inertial is not None:
        ob["source_mass_kg"]=float(inertial.find("mass").get("value"))
        ob["source_com_m"]=list(xyz(inertial.find("origin").get("xyz","0 0 0")))

for joint in robot.findall("joint"):
    ob=frames[joint.find("child").get("link")]
    ob.parent=frames[joint.find("parent").get("link")]
    ob.matrix_parent_inverse=Matrix.Identity(4); ob.matrix_basis=origin(joint.find("origin"))
    ob["joint"]=joint.get("name"); ob["joint_type"]=joint.get("type")
    if joint.find("axis") is not None: ob["axis_local"]=list(xyz(joint.find("axis").get("xyz")))
    lim=joint.find("limit")
    if lim is not None:
        ob["source_limits_rad"]=[float(lim.get("lower",0)),float(lim.get("upper",0))]
        ob["limit_note"]="Kinematic range only. URDF effort/velocity placeholders are not motor ratings."
frames["world"].rotation_euler.z=-math.pi/2

for link in robot.findall("link"):
    for visual in link.findall("visual"):
        mesh=visual.find("geometry/mesh")
        if mesh is None: continue
        bpy.ops.wm.stl_import(filepath=str(MODEL / mesh.get("filename")))
        ob=bpy.context.object; ob.name="OEM • "+link.get("name")
        move_to(ob,hardware); ob.parent=frames[link.get("name")]
        ob.matrix_parent_inverse=Matrix.Identity(4); ob.matrix_basis=origin(visual.find("origin"))
        ob.scale=xyz(mesh.get("scale","1 1 1"))
        ob.data.materials.clear(); ob.data.materials.append(metal if "gear" in link.get("name") else graphite)
        ob["type"]="PURCHASED + PRINTED MERGED REFERENCE — NOT A PRINT FILE"
        ob["source_mesh"]=mesh.get("filename")
        ob["license"]="ToddlerBot design © authors; CC BY-NC-SA 4.0"

bpy.context.view_layer.update()
def bounds(ob):
    vs=[ob.matrix_world @ Vector(v) for v in ob.bound_box]
    lo=[min(v[i] for v in vs) for i in range(3)]
    hi=[max(v[i] for v in vs) for i in range(3)]
    return {"min_mm":[round(v*1000,3) for v in lo],"max_mm":[round(v*1000,3) for v in hi]}
report={ob.name:bounds(ob) for ob in hardware.objects if ob.type=="MESH"}
lo=min(v["min_mm"][2] for v in report.values())
frames["world"].location.z=-lo/1000
bpy.context.view_layer.update()
report={ob.name:bounds(ob) for ob in hardware.objects if ob.type=="MESH"}
report["_metadata"]={"base_floor_adjustment_mm":-lo,"mesh_count":len(hardware.objects),"pose":"URDF zero configuration, not a walking stance"}
(ROOT/"evidence"/"hardware-bounds.json").write_text(json.dumps(report,indent=2)+"\n")
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"percival.blend"))
result={"scene":scene.name,"mesh_count":len(hardware.objects),"saved":str(OUT/"percival.blend"),
        "head":report.get("OEM • head"),"torso":report.get("OEM • torso"),
        "height_mm":max(v["max_mm"][2] for k,v in report.items() if not k.startswith('_'))}
