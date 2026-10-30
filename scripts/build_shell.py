"""Percival Rev A: removable non-structural skins around a real 2XC chassis.

Dimensions below are millimetres. Source hardware is never scaled or edited.
Run once in the imported assembly via the official Blender MCP.
"""
import bpy
import bmesh
import math
import json
from pathlib import Path
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parents[1]
scene=bpy.context.scene
if scene.name != "Percival • engineering assembly": raise RuntimeError("Select the imported assembly scene")
if bpy.data.collections.get("03 • PERCIVAL PRINTS — Rev A fit prototypes"):
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'design'/'percival-shell-checkpoint.blend'),copy=True)
    for name in ['03 • PERCIVAL PRINTS — Rev A fit prototypes',
                 '04 • HARDWARE ENVELOPES — allowances, not machining drawings',
                 '05 • VISUAL DETAILS — purchased fasteners and optics',
                 '80 • USER REFERENCES — images, not dimensioned drawings']:
        col=bpy.data.collections.get(name)
        if col:
            for ob in list(col.objects): bpy.data.objects.remove(ob,do_unlink=True)
            bpy.data.collections.remove(col)
prints=bpy.data.collections.new("03 • PERCIVAL PRINTS — Rev A fit prototypes"); scene.collection.children.link(prints)
detail=bpy.data.collections.new("04 • HARDWARE ENVELOPES — allowances, not machining drawings"); scene.collection.children.link(detail)
cosmetic=bpy.data.collections.new("05 • VISUAL DETAILS — purchased fasteners and optics"); scene.collection.children.link(cosmetic)
cream=bpy.data.materials['Shell • warm ivory']; purple=bpy.data.materials['Shell • muted violet']
orange=bpy.data.materials['Details • amber orange']; black=bpy.data.materials['Face • charcoal']
metal=bpy.data.materials['Hardware • anodized aluminum']; graphite=bpy.data.materials['Hardware • graphite']
for m,c in [(cream,(.67,.60,.47,1)),(purple,(.10,.043,.17,1)),(graphite,(.014,.018,.022,1)),(black,(.006,.009,.013,1))]:
    m.diffuse_color=c; m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=c
glass=bpy.data.materials.new('Optics • coated lens'); glass.use_nodes=True
bs=glass.node_tree.nodes['Principled BSDF']; bs.inputs['Base Color'].default_value=(.008,.025,.045,1)
bs.inputs['Metallic'].default_value=.65; bs.inputs['Roughness'].default_value=.12
green=bpy.data.materials.new('PCB • green'); green.diffuse_color=(.015,.15,.08,1)
green.use_nodes=True; green.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.015,.15,.08,1)

def collect(ob,col):
    for c in list(ob.users_collection): c.objects.unlink(ob)
    col.objects.link(ob)
def select(ob):
    bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active=ob
def material(ob,m):
    if m: ob.data.materials.append(m)
    return ob
def rr(name,w,h,d,loc,r=4,m=None,col=None):
    """Rounded rectangular prism: width X, height Z, extrusion Y."""
    r=min(r,w/2-.01,h/2-.01); points=[]
    for cx,cz,start in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
        for i in range(9):
            a=math.radians(start+i*90/8)
            points.append(((cx+r*math.cos(a))/1000,(cz+r*math.sin(a))/1000))
    n=len(points); vs=[(x,y/1000,z) for y in [-d/2,d/2] for x,z in points]
    fs=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]
    fs.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(vs,[],fs); mesh.update()
    ob=bpy.data.objects.new(name,mesh); (col or prints).objects.link(ob)
    ob.location=Vector(loc)/1000; material(ob,m)
    bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(mesh); bm.free()
    return ob
def box(name,dims,loc,m=None,bevel=0,col=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=Vector(loc)/1000)
    ob=bpy.context.object; ob.name=name; ob.dimensions=Vector(dims)/1000
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); collect(ob,col or prints); material(ob,m)
    if bevel:
        mod=ob.modifiers.new('Edge radius','BEVEL'); mod.width=bevel/1000; mod.segments=3
        select(ob); bpy.ops.object.modifier_apply(modifier=mod.name)
    return ob
def cyl(name,r,d,loc,axis='Y',m=None,col=None,vertices=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r/1000,depth=d/1000,location=Vector(loc)/1000)
    ob=bpy.context.object; ob.name=name
    if axis=='Y': ob.rotation_euler.x=math.pi/2
    if axis=='X': ob.rotation_euler.y=math.pi/2
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True); collect(ob,col or prints); material(ob,m)
    for p in ob.data.polygons: p.use_smooth=(len(p.vertices)==4)
    return ob
def boolean(ob,tool,op='DIFFERENCE'):
    select(ob); mod=ob.modifiers.new(op,'BOOLEAN'); mod.operation=op; mod.solver='EXACT'; mod.object=tool
    bpy.ops.object.modifier_apply(modifier=mod.name); bpy.data.objects.remove(tool,do_unlink=True)
def attach(ob,link):
    bpy.context.view_layer.update(); world=ob.matrix_world.copy()
    ob.parent=bpy.data.objects['LINK • '+link]; ob.matrix_parent_inverse=Matrix.Identity(4)
    ob.matrix_basis=ob.parent.matrix_world.inverted()@world
def register(ob,pid,link,material_name='PETG',notes='Cosmetic fit prototype; do not bridge moving joints.'):
    ob.name=pid+' • '+ob.name; ob['part_id']=pid; ob['print_material']=material_name
    ob['status']='FIT PROTOTYPE — physical fit, retention and motion unverified'
    ob['notes']=notes; ob['nominal_wall_mm']=1.8; ob['source_link']=link
    ob['license']='CC BY-NC-SA 4.0; adapted around ToddlerBot hardware'
    attach(ob,link); return ob
def strap_slots(ob,xs,y,z):
    for x in xs: boolean(ob,box('6 mm strap slot',(2.4,12,8.4),(x,y,z)))
def shield(pid,name,w,h,d,loc,link,m=cream):
    x,y,z=loc; wall=1.8
    ob=rr(name,w,h,d,loc,6,m)
    boolean(ob,rr('Hollow back',w-2*wall,h-2*wall,d+4,(x,y+wall+2,z),4.2))
    strap_slots(ob,[x-w/2+8,x+w/2-8],y-d/2,z)
    return register(ob,pid,link)

# Head: two 1.8 mm shells, open neck/cable passage, removable perforated face.
head_center=(0,8,502); W,H,D,T=236,112,108,1.8
front=rr('Head front bezel',W,H,D/2,(0,-19,502),20,cream)
boolean(front,rr('Inner cavity',W-2*T,H-2*T,D/2+4,(0,-15.2,502),18.2))
# Re-cut cavity to ensure exactly 1.8 mm front lip before the face opening.
boolean(front,rr('Face aperture',214,88,12,(0,-45,502),14))
back=rr('Head rear cover',W,H,D/2,(0,35,502),20,cream)
boolean(back,rr('Rear cavity',W-2*T,H-2*T,D/2+4,(0,31.2,502),18.2))
for ob in [front,back]:
    boolean(ob,box('Neck and loom opening',(58,80,22),(0,8,449)))
# Four internal joining bosses; access with the face plate removed.
for x in [-108,108]:
    for z in [457,547]:
        for ob,y,depth in [(front,3,10),(back,14,12)]:
            boss=cyl('M3 shell joining boss',7,depth,(x,y,z)); boolean(ob,boss,'UNION')
            boolean(ob,cyl('M3 clearance',1.7,24,(x,y,z)))
        # Back nut pocket, M3 hex nut nominal 5.5 mm across flats, 5.9 mm fit allowance.
        boolean(back,cyl('M3 hex nut pocket',5.9/math.sqrt(3),4,(x,19, z),vertices=6))
# Rear passive ventilation and four retention strap ports.
for x in range(-75,76,15):
    for z in [479,488,516,525]: boolean(back,rr('Vent',9,2.4,12,(x,61,z),1.1))
for x in [-44,44]:
    for z in [478,526]: boolean(back,box('Helmet retention strap port',(8.4,12,2.4),(x,61,z)))
register(front,'P01','head',notes='1.8 mm shell; M3 x25 seam bolts/nuts. Neck attachment remains a prototype retention interface.')
register(back,'P02','head',notes='Rear access and vents. 6 mm hook-and-loop straps through four rear ports; fit to retained OEM head structure before powered motion.')

face=rr('Camera visor',213.4,87.4,2,(0,-45.9,502),13.7,black)
for x in [-60,60]:
    boolean(face,cyl('Optical opening',22,12,(x,-46,505)))
    # Mount through the verified 34 x34 camera PCB mounting pattern; standoff depth needs lens measurement.
    for dx in [-17,17]:
        for dz in [-17,17]: boolean(face,cyl('M2 camera fixing',1.2,8,(x+dx,-46,505+dz)))
for x in [-96,96]:
    for z in [469,535]: boolean(face,cyl('M2.5 face screw',1.4,8,(x,-46,z)))
boolean(face,cyl('Optional 3mm status LED',1.6,10,(0,-46,526)))
# Exact booleans can omit one very small triangle at a curved cut. Repair only
# a three-edge boundary; larger/open defects remain failures in verify_export.
bm=bmesh.new(); bm.from_mesh(face.data)
boundary=[e for e in bm.edges if e.is_boundary]
if len(boundary)==3:
    bmesh.ops.holes_fill(bm,edges=boundary,sides=3)
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
bm.to_mesh(face.data); bm.free()
register(face,'P03','head',notes='Two real Arducam B0202 cameras; 34 mm mounting pattern. Relocating cameras requires lens-depth measurement, standoffs and stereo recalibration. NOT a released optical mount.')

# Face mounting pads connected to the front lip, for M2.5 bolts + nuts.
for x in [-96,96]:
    for z in [469,535]:
        # Pads bridge from the outer rim into the removable face.
        pad=rr('Face mounting tab',24,12,4,(math.copysign(102,x),-42.8,z),2)
        boolean(front,pad,'UNION'); boolean(front,cyl('M2.5 face clearance',1.4,12,(x,-43,z)))

for side in [-1,1]:
    x=side*60
    rim=cyl('Optical bezel',26,4,(x,-49,505),m=purple)
    boolean(rim,cyl('Optical opening',22,10,(x,-49,505)))
    baffle=cyl('Integral lens light baffle',23,1.6,(x,-47.8,505),m=black)
    boolean(baffle,cyl('Lens barrel clearance',9.8,8,(x,-47.8,505)))
    boolean(rim,baffle,'UNION')
    # Four M2 holes share the face and camera pattern, leaving assembly possible.
    for dx in [-17,17]:
        for dz in [-17,17]: boolean(rim,cyl('M2 clearance',1.2,10,(x+dx,-48,505+dz)))
    register(rim,'P04L' if side>0 else 'P04R','head',notes='Separate cosmetic lens ring. Ensure lens protrudes beyond visor; verify full camera field of view.')
    pcb=box('Arducam B0202 • 38 x38 PCB allowance',(38,1.6,38),(x,-27,505),green,col=detail)
    pcb['verified']='38 x38 mm PCB;34 mm fixing pitch'; pcb['unverified']='lens depth, USB plug and exact board thickness'
    attach(pcb,'head')
    barrel=cyl('B0202 lens envelope — depth allowance',9.5,22,(x,-39,505),m=black,col=cosmetic); attach(barrel,'head')
    lens=cyl('B0202 coated optic • visualization',8.8,1.5,(x,-50.5,505),m=glass,col=cosmetic); attach(lens,'head')
    # Side pods: hollow with rear opening and strap slots; amber ear insert is passive.
    pod=cyl('Side ear pod',32,7,(side*121.8,8,502),axis='X',m=purple)
    boolean(pod,cyl('Pod recess',29.2,9,(side*124.8,8,502),axis='X'))
    register(pod,'P05L' if side>0 else 'P05R','head',notes='Nonfunctional decorative pod; adhesive or prototype retaining strap, no actuator inside.')
    disc=cyl('Ear pod charcoal insert',29,1.2,(side*121.05,8,502),axis='X',m=black)
    register(disc,'P05AL' if side>0 else 'P05AR','head','TPU 95A',notes='Removable adhesive decoration; no speaker or actuator implied.')
    bracket=rr('Ear mounting upstand',26,18,5,(side*100,19.4,561),3)
    boolean(back,bracket,'UNION')
    ear=rr('Passive ear fin',22,38,7,(side*100,13,575),10,cream)
    for z in [562,569]:
        boolean(ear,cyl('M3 ear attachment',1.7,12,(side*100,13,z)))
        boolean(back,cyl('M3 ear attachment',1.7,16,(side*100,20,z)))
    # Cut the fin's insertion clearance out of the curved roof; 0.3 mm each side.
    boolean(back,rr('Ear fin insertion clearance',22.6,38.6,7.6,(side*100,13,575),10.3))
    register(ear,'P06L' if side>0 else 'P06R','head','TPU 95A',notes='Flexible passive fin; top594 mm in zero pose. Prototype fixing must be checked on rear cover.')
    accent=rr('Ear amber insert',6,19,1.6,(side*100,8.6,581),2,orange)
    register(accent,'P07L' if side>0 else 'P07R','head','TPU 95A',notes='Adhesive insert; cosmetic, not an antenna.')

crest=rr('Crown accent',52,15,2,(0,-8,559),3,purple)
crest.rotation_euler.x=math.pi/2
register(crest,'P08','head',notes='Cosmetic crown panel; apply with removable adhesive after head fit.')

# Front torso cover stays clear of shoulder mechanisms and existing rear cooling.
chest=shield('P10','Chest fairing',151,117,18,(0,-31,373),'torso')
for x in [-50,-41,-32,32,41,50]:
    for z in [345,353,361]: boolean(chest,cyl('Chest ventilation',2,12,(x,-39,z)))
spine=rr('Violet chest service panel',38,92,2,(0,-41,373),5,purple)
for z in [335,411]: boolean(spine,cyl('M2.5 trim hole',1.4,8,(0,-41,z)))
for z in [335,411]: boolean(chest,cyl('M2.5 trim hole',1.4,12,(0,-39,z)))
register(spine,'P11','torso',notes='Removable front trim; it does not replace the upstream electronics service cover.')
pelvis=shield('P12','Pelvis armor',106,49,14,(0,-23,270),'pelvis_link')

for side,label in [(1,'L'),(-1,'R')]:
    prefix='left' if side>0 else 'right'
    shoulder=shield('P20'+label,'Shoulder cap',51,39,12,(side*106,-11,414),prefix+'_shoulder_roll_link')
    forearm=shield('P21'+label,'Forearm fairing',47,45,12,(side*106,-11,326),prefix+'_elbow_roll_link')
    stripe=rr('Forearm amber marker',8,25,2,(side*118,-18,326),3,orange)
    register(stripe,'P22'+label,prefix+'_elbow_roll_link',notes='Removable adhesive decoration.')
    wrist=shield('P23'+label,'Wrist guard',47,20,12,(side*94.5,-7,267),prefix+'_wrist_pitch_link')
    thigh=shield('P30'+label,'Upper leg fairing',49,36,10,(side*37,-13,217),prefix+'_hip_roll_link')
    knee=shield('P31'+label,'Knee fairing',53,49,12,(side*37,-10,161),prefix+'_hip_yaw_link')
    knee_trim=rr('Violet knee panel',30,29,1.6,(side*37,-16.8,161),5,purple)
    register(knee_trim,'P32'+label,prefix+'_hip_yaw_link',notes='Removable adhesive decoration.')
    shin=shield('P33'+label,'Shin guard',37,50,9,(side*37,-7,101),prefix+'_knee_link')
    # No custom sole: preserve stock contact geometry and sole friction for walking development.
    toe=shield('P34'+label,'Toe cowl',43,17,27,(side*37,-32,24),prefix+'_ankle_roll_link')
    toe['notes']='Decorative toe cowl only, no change to sole/contact polygon. Check ankle flexion and front ground clearance.'

# Pack reference images for scale/style comparison. Hidden reference collection.
refs=bpy.data.collections.new('80 • USER REFERENCES — images, not dimensioned drawings'); scene.collection.children.link(refs)
ref_paths=[
 '/Users/dearwolf/.t3/userdata/attachments/e882e32b-9780-4a16-8b84-34d7f640b3d3-619c17a0-3fa2-413c-b41b-7cd52c2db0f5.png',
 '/Users/dearwolf/.t3/userdata/attachments/e882e32b-9780-4a16-8b84-34d7f640b3d3-c91892c2-8a35-493b-a18a-367f56ee8163.png',
 '/Users/dearwolf/.t3/userdata/attachments/e882e32b-9780-4a16-8b84-34d7f640b3d3-81483aeb-d64e-4f60-9f04-07905ec7352e.png']
for i,path in enumerate(ref_paths):
    im=bpy.data.images.load(path,check_existing=True); im.pack()
    ob=bpy.data.objects.new('REFERENCE • '+['front','side','top'][i],None); ob.empty_display_type='IMAGE'; ob.data=im
    ob.empty_display_size=.6; ob.location=(1+i*.6,0,.3); refs.objects.link(ob)
refs.hide_viewport=True; refs.hide_render=True

# The original head is retained as a hidden interference reference (not destroyed).
# The assembly BOM retains its original mass as a conservative budgeting baseline.
bpy.data.objects['OEM • head'].hide_render=True
bpy.data.objects['OEM • head'].hide_set(True)
bpy.context.view_layer.update()
scene['height_limit_mm']=600; scene['head_strategy']='New visor relocates cameras; retained neck/stock head cage interface requires fit test. No walking validation.'
scene['camera_calibration']='Required after changing lens spacing to 120 mm'
scene['print_profile']='A1 256x256x256 or Prusa XL360. Rev A custom skins only; use upstream MakerWorld profiles for chassis.'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'design'/'percival.blend'))
scene.render.filepath=str(ROOT/'renders'/'percival-hero.png')
bpy.ops.render.render(write_still=True)
result={'printed_prototypes':len(prints.objects),'file':str(ROOT/'design'/'percival.blend'),'render':scene.render.filepath}
