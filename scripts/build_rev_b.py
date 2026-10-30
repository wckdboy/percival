"""Blender MCP: BDX-inspired Rev B proportion study, separate from Rev A.

Purchased-component envelopes remain full-size. New limbs, torso, feet and
interfaces are design concepts; no Rev A print or gait validation is inherited.
"""
import bpy
import bmesh
import math
import json
import hashlib
from pathlib import Path
from mathutils import Vector, Matrix, Euler

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'renders/rev-b'; OUT.mkdir(parents=True,exist_ok=True)
original_hash=hashlib.sha256((ROOT/'design/percival.blend').read_bytes()).hexdigest()
previous=bpy.data.scenes.get('Percival • Rev B / BDX character study')
if previous:
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'design/percival-rev-b-first-pass.blend'),copy=True)
    bpy.context.window.scene=bpy.data.scenes['Scene']
    for ob in list(previous.objects):bpy.data.objects.remove(ob,do_unlink=True)
    for col in list(previous.collection.children):bpy.data.collections.remove(col)
    bpy.data.scenes.remove(previous)
scene=bpy.data.scenes.new('Percival • Rev B / BDX character study')
bpy.context.window.scene=scene
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;scene.unit_settings.length_unit='MILLIMETERS'
scene['status']='MECHANICAL-LAYOUT CONCEPT — new chassis, packaging, motion and print validation required'
scene['revision']='B';scene['height_limit_mm']=600
scene['source_relationship']='Original Rev A preserved. No source hardware has been scaled. Rev B uses new proposed structural envelopes.'
bodycol=bpy.data.collections.new('B01 • Proposed body and limbs');scene.collection.children.link(bodycol)
headcol=bpy.data.collections.new('B02 • Expressive head');scene.collection.children.link(headcol)
jointcol=bpy.data.collections.new('B03 • Joint and fastener appearance');scene.collection.children.link(jointcol)
envcol=bpy.data.collections.new('B04 • Full-size purchased envelopes — layout allowances');scene.collection.children.link(envcol)
stage=bpy.data.collections.new('B90 • Studio');scene.collection.children.link(stage)

def mat(name,color,metallic=0,rough=.38):
    m=bpy.data.materials.new('B • '+name);m.diffuse_color=(*color,1);m.use_nodes=True
    p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metallic;p.inputs['Roughness'].default_value=rough
    return m
ivory=mat('warm ceramic ivory',(.69,.63,.51),.06,.32)
violet=mat('aubergine purple',(.095,.039,.15),.25,.31)
orange=mat('tangerine orange',(.95,.22,.012),.12,.30)
dark=mat('graphite mechanism',(.012,.018,.024),.55,.30)
rubber=mat('rubber soles',(.008,.011,.014),0,.65)
steel=mat('machined alloy',(.30,.34,.37),.82,.24)
face=mat('matte visor',(.008,.013,.020),.15,.34)
glass=mat('coated optics',(.007,.026,.046),.6,.10)
cyan=mat('status cyan',(.02,.60,.92),.3,.2)
bs=cyan.node_tree.nodes['Principled BSDF'];bs.inputs['Emission Color'].default_value=(.01,.45,.85,1);bs.inputs['Emission Strength'].default_value=1.6
pcbmat=mat('PCB envelope',(.015,.16,.07),.12,.5)

def own(ob,col):
    for c in list(ob.users_collection):c.objects.unlink(ob)
    col.objects.link(ob)
def finish(ob,name,m,col,parent=None):
    ob.name='B • '+name;own(ob,col)
    if m:ob.data.materials.append(m)
    if parent:ob.parent=parent;ob.matrix_parent_inverse=Matrix.Identity(4)
    ob['status']='CONCEPT GEOMETRY — NOT A RELEASED PRINT PART'
    return ob
def empty(name,loc=(0,0,0),parent=None,col=bodycol):
    o=bpy.data.objects.new('B • '+name,None);col.objects.link(o);o.location=Vector(loc)/1000
    o.empty_display_type='PLAIN_AXES';o.empty_display_size=.012
    if parent:o.parent=parent
    return o
def cube(name,dims,loc,m=ivory,r=3,col=bodycol,parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=Vector(loc)/1000)
    o=bpy.context.object;o.dimensions=Vector(dims)/1000;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    finish(o,name,m,col,parent)
    if r:
        mod=o.modifiers.new('Soft manufactured edges','BEVEL');mod.width=r/1000;mod.segments=5
        bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
        for poly in o.data.polygons:poly.use_smooth=True
        n=o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL');n.keep_sharp=True;n.weight=40
    return o
def rr(name,w,h,d,loc,r,m=ivory,parent=None,col=headcol):
    pts=[];r=min(r,w/2-.01,h/2-.01)
    for cx,cz,a in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
        for i in range(13):
            q=math.radians(a+i*7.5);pts.append(((cx+r*math.cos(q))/1000,(cz+r*math.sin(q))/1000))
    n=len(pts);vs=[(x,y/1000,z) for y in [-d/2,d/2] for x,z in pts]
    fs=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],fs);mesh.update()
    o=bpy.data.objects.new(name,mesh);col.objects.link(o);o.location=Vector(loc)/1000
    finish(o,name,m,col,parent)
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(mesh);bm.free()
    return o
def cyl(name,r,d,loc,m=dark,axis='X',parent=None,col=jointcol,vertices=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r/1000,depth=d/1000,location=Vector(loc)/1000)
    o=bpy.context.object
    if axis=='X':o.rotation_euler.y=math.pi/2
    elif axis=='Y':o.rotation_euler.x=math.pi/2
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);finish(o,name,m,col,parent)
    for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
    mod=o.modifiers.new('Rim bevel','BEVEL');mod.width=.6/1000;mod.segments=3
    return o
def boolean(ob,tool,operation='DIFFERENCE'):
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
    mod=ob.modifiers.new('Opening','BOOLEAN');mod.object=tool;mod.operation=operation;mod.solver='EXACT'
    bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(tool,do_unlink=True)
def bar(name,a,b,width,depth,m=ivory,r=10,col=bodycol):
    a,b=Vector(a),Vector(b);v=b-a
    ob=cube(name,(width,depth,v.length),(a+b)/2,m,r,col)
    ob.rotation_mode='QUATERNION';ob.rotation_quaternion=v.to_track_quat('Z','Y');return ob
def pipe(name,pts,r,m=dark,parent=None,col=jointcol):
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=12
    cu.bevel_depth=r/1000;cu.bevel_resolution=3;s=cu.splines.new('BEZIER');s.bezier_points.add(len(pts)-1)
    for p,co in zip(s.bezier_points,pts):p.co=Vector(co)/1000;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    ob=bpy.data.objects.new(name,cu);col.objects.link(ob);finish(ob,name,m,col,parent);return ob
def fastener(name,loc,axis='Y',parent=None):
    cyl(name+' washer',2.6,.8,loc,dark,axis,parent,vertices=32)
    offset={'X':(1,0,0),'Y':(0,-1,0),'Z':(0,0,1)}[axis]
    cyl(name+' socket',1.45,1.0,Vector(loc)+Vector(offset)*.5,steel,axis,parent,vertices=6)
def joint(name,at,r,side):
    x,y,z=at
    cyl(name+' graphite bearing',r,43,(x,y,z),dark)
    cyl(name+' ivory ring',r+2,6,(x+side*23,y,z),ivory)
    cyl(name+' purple inset',r-5,7,(x+side*25,y,z),violet)
    cyl(name+' alloy hub',r*.43,8,(x+side*27,y,z),steel)
    cyl(name+' axle cover',r*.26,9,(x+side*28,y,z),dark)
    for i in range(5):
        a=i*2*math.pi/5
        fastener(name+f' bolt{i}',(x+side*29,y+math.sin(a)*(r-10),z+math.cos(a)*(r-10)),'X')
def servo_envelope(name,loc,rotation=(0,0,0)):
    ob=cube(name+' / XM430 28.5×46.5×34 mm',(28.5,34,46.5),loc,dark,1,col=envcol)
    ob.rotation_euler=Euler(rotation,'XYZ');ob.display_type='WIRE';ob.hide_render=True
    ob['manufacturer_envelope_mm']=[28.5,46.5,34]
    ob['status']='FULL-SIZE PURCHASED ENVELOPE; joint assignment/torque/mounting unverified'
    return ob

# Short, rounded belly and compact removable rear battery envelope.
torso=cube('compact torso envelope',(146,102,78),(0,8,355),ivory,19)
torso['repackaging_required']='Original ToddlerBot torso is 128.752 mm tall; this proposed 78 mm torso is a new layout.'
cube('narrow waist bellows',(100,72,32),(0,8,315),dark,11)
cube('rounded pelvic bridge',(124,76,42),(0,9,320),ivory,13)
chest=rr('small violet chest inset',40,47,3,(0,-44.5,357),9,violet,col=bodycol)
for z in [342,372]:fastener('chest captive screw',(0,-47,z))
rr('cyan chest status slit',19,4,2,(46,-44,365),2,cyan,col=bodycol)
for x in [32,40,48,56]:
    for z in [342,348,354]:cyl('speaker grille',1.3,2,(x,-43,z),dark,'Y',col=bodycol,vertices=24)
backpack=cube('removable rear battery housing',(89,55,77),(0,83,350),dark,12)
cube('backpack violet lid',(73,4,59),(0,112,350),violet,2)
pipe('orange carry loop',[(-24,84,389),(-24,84,400),(24,84,400),(24,84,389)],3.5,orange)
cube('J401 carrier envelope — full size',(100,80,1.6),(0,7,346),pcbmat,.3,envcol).hide_render=True
cube('J401 cooling clearance — allowance',(100,80,35),(0,7,365),dark,1,envcol).hide_render=True
cube('CNHL 4S nominal battery envelope',(76,38,47),(0,83,350),dark,1,envcol).hide_render=True
for ob in envcol.objects:
    ob.display_type='WIRE';ob['status']='PACKAGING ENVELOPE ONLY; connectors, cooling and mounting unresolved'

# Large, weighty-looking bent legs. Actual soles remain flat in this illustration.
for side,label,foot_y,knee_y,knee_z in [(1,'L',-35,-50,174),(-1,'R',-8,-25,183)]:
    hip=(side*64,10,310);knee=(side*82,knee_y,knee_z);ankle=(side*86,foot_y+24,61)
    joint(label+' hip',hip,37,side)
    joint(label+' knee',knee,34,side)
    joint(label+' ankle',ankle,25,side)
    a=Vector(hip);b=Vector(knee);u=(b-a).normalized()
    thigh=bar(label+' sculpted thigh',a+u*25,b-u*25,77,78,ivory,16)
    thigh['mechanical_change']='New link length and load-bearing structure; not ToddlerBot-compatible.'
    a=Vector(knee);b=Vector(ankle);u=(b-a).normalized()
    shin=bar(label+' tapered shin',a+u*23,b-u*19,70,70,ivory,14)
    # Front plates follow the segment orientation and leave visible dark joint gaps.
    for link,name,width,height in [(thigh,'thigh inset',44,54),(shin,'shin inset',40,48)]:
        ob=cube(label+' '+name,(width,3,height),(0,0,0),violet,1)
        ob.parent=link;ob.location=(0,-.040,0)
        for localz in [-height/2+7,height/2-7]:
            fastener(label+' inset bolt',(0,-42,localz),parent=link)
    pipe(label+' ankle service cable',[(side*107,knee_y+24,knee_z-10),(side*111,foot_y+49,115),(side*102,foot_y+43,69)],3,dark)
    foot=empty(label+' foot', (side*86,foot_y,0));foot.rotation_euler.z=math.radians(-side*7)
    cube(label+' broad rubber sole',(96,144,16),(0,0,8),rubber,7,parent=foot)
    cube(label+' soft boot shell',(89,129,35),(0,0,29),ivory,14,parent=foot)
    cube(label+' toe pad',(54,57,3),(0,-23,47.5),violet,1,parent=foot)
    cube(label+' front bumper',(73,7,13),(0,-69,13),rubber,3,parent=foot)
    for x in [-28,-10,10,28]:
        cube(label+' sole tread divider',(2,5,10),(x,-72,12),dark,1,parent=foot)
    cube(label+' amber heel release',(50,8,9),(0,62,22),orange,3,parent=foot)
    for x in [-21,21]:
        fastener(label+' toe screw',(x,-35,50),'Z',foot)
    servo_envelope(label+' knee servo',knee)
    servo_envelope(label+' hip servo',hip)

# Two small arms; one relaxed, one raised in greeting.
hand_roots=[]
for label,side,shoulder,elbow,wrist,hand in [
    ('R',-1,(-97,5,371),(-128,-3,333),(-137,-30,308),(-138,-37,293)),
    ('L',1,(97,5,371),(132,-8,371),(151,-30,407),(153,-38,425))]:
    joint(label+' shoulder',shoulder,20,side)
    joint(label+' elbow',elbow,14,side)
    a,b=Vector(shoulder),Vector(elbow);u=(b-a).normalized()
    bar(label+' small upper arm',a+u*12,b-u*10,35,38,ivory,10)
    a,b=Vector(elbow),Vector(wrist);u=(b-a).normalized()
    forearm=bar(label+' little forearm',a+u*9,b-u*7,32,35,ivory,9)
    patch=cube(label+' orange arm tab',(10,3,19),(0,0,0),orange,1)
    patch.parent=forearm;patch.location=(0,-.019,0)
    cyl(label+' wrist collar',12,18,wrist,dark)
    root=empty(label+' gripper pose pivot',wrist);hand_roots.append(root)
    direction=(Vector(hand)-Vector(wrist)).normalized()
    # Small mitten-like gripper, not the long default source gripper.
    root.rotation_mode='QUATERNION';root.rotation_quaternion=direction.to_track_quat('Z','Y')
    cube(label+' palm',(29,24,24),(0,0,17),ivory,7,parent=root)
    cube(label+' palm violet inset',(20,2,13),(0,-13,17),violet,.7,parent=root)
    for x in [-9,9]:
        finger=cube(label+' rounded gripper finger',(10,17,21),(x,-3,37),dark,4,parent=root)
        finger.rotation_euler.y=math.radians(-x*.45)
        cube(label+' soft fingertip',(9,18,8),(x,-3,45),rubber,3,parent=root)
    cyl(label+' thumb pivot',4,3,(17,0,16),orange,'X',root)

# Neck gimbal with a visible dark gap under the large head.
cyl('neck yaw bearing',24,14,(0,8,400),dark,'Z')
cyl('neck yaw trim',20,3,(0,8,408),violet,'Z')
cube('neck pitch fork',(47,31,20),(0,6,416),dark,6)
cyl('neck pitch axle',12,55,(0,6,419),steel)
head=empty('head pose pivot',(0,-12,462),col=headcol)
head.rotation_euler=(math.radians(-3),math.radians(6),math.radians(-5))
shell=rr('large soft head enclosure',234,112,112,(0,0,0),26,ivory,head)
inner=rr('head cavity',229,107,108,(0,2,0),23.5,None,head)
boolean(shell,inner)
opening=rr('visor opening',209,88,24,(0,-54,0),19,None,head);boolean(shell,opening)
edge=shell.modifiers.new('Rounded shell parting edges','BEVEL');edge.width=.002;edge.segments=4
for poly in shell.data.polygons:poly.use_smooth=len(poly.vertices)==4
visor=rr('wide recessed visor',208.4,87.4,3,(0,-55.2,0),18.7,face,head)
for x,z,r,label in [(-55,4,34,'large eye'),(57,1,28,'small eye')]:
    cyl(label+' purple surround',r,7,(x,-58,z),violet,'Y',head)
    cyl(label+' dark optical recess',r-4,8,(x,-62,z),dark,'Y',head)
    cyl(label+' outer black lip',r-7,10,(x,-66,z),face,'Y',head)
    cyl(label+' alloy inner ring',r-14,11,(x,-68,z),steel,'Y',head)
    cyl(label+' glass optic',r-16,12,(x,-70,z),glass,'Y',head)
    # The optical shroud appearance is not an assertion of lens FOV or fit.
    camera=cube(label+' B0202 full-size board',(38,1.6,38),(x,-35,z),pcbmat,.3,envcol,head)
    camera.hide_render=True;camera.display_type='WIRE';camera['verified_envelope']='38 ×38 mm PCB; lens depth allowance not released'
    for i in [0,2,4]:
        a=i*2*math.pi/6
        fastener(label+' bezel screw',(x+math.sin(a)*(r-2),-63,z+math.cos(a)*(r-2)),parent=head)
rr('friendly status bar',19,4,2,(0,-58,-25),2,cyan,head)
for i,x in enumerate([-5,0,5]):cyl('small face sensor indicator',1.2,2,(x,-58,23),cyan if i==0 else dark,'Y',head,vertices=24)
for x in [-92,92]:
    for z in [-31,31]:fastener('visor fastener',(x,-58,z),parent=head)
for side in [-1,1]:
    cyl('ear side housing',29,10,(side*118,3,0),violet,'X',head)
    cyl('ear inset',22,12,(side*120,3,0),dark,'X',head)
    cyl('ear center',12,13,(side*121,3,0),steel,'X',head)
    earroot=empty('ear hinge', (side*97,3,45),head,headcol)
    earroot.rotation_euler.y=math.radians(side*(13 if side<0 else 20))
    cyl('ear hinge pin',9,25,(0,0,0),dark,'X',earroot)
    tall=57 if side<0 else 43
    rr('asymmetric listening fin',23,tall,9,(0,1,tall/2+1),10,ivory,earroot)
    rr('ear dark inlay',13,tall-10,1.8,(0,-4.2,tall/2+2),5,dark,earroot)
    rr('ear orange marker',4.5,tall-20,2,(side*8,-5,tall/2+3),2,orange,earroot)
crest=cube('head crown tab',(43,26,2),(0,0,57),violet,.8,headcol,head)
for x in [-15,15]:fastener('crown bolt',(x,0,59),'Z',head)
pipe('neck cable loop',[(-20,20,411),(-29,27,429),(-22,23,444)],2.8,dark)

# Illustration-only idle gesture. No joint controller trajectories are generated.
headbase=head.rotation_euler.copy()
for frame,roll,yaw in [(1,6,-5),(25,9,-2),(49,4,-8),(73,6,-5)]:
    head.rotation_euler=(math.radians(-3),math.radians(roll),math.radians(yaw))
    head.keyframe_insert(data_path='rotation_euler',frame=frame)
scene.frame_start=1;scene.frame_end=73;scene.render.fps=24;scene.frame_set(1)

# Determine bounds from the evaluated mesh geometry, without the studio/envelopes.
def bounds():
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();vs=[]
    for col in [bodycol,headcol,jointcol]:
        for ob in col.objects:
            if ob.type not in {'MESH','CURVE'} or ob.hide_render:continue
            eo=ob.evaluated_get(dg);mesh=eo.to_mesh()
            vs.extend(eo.matrix_world@v.co for v in mesh.vertices);eo.to_mesh_clear()
    return [[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]]
pose_bounds=[]
for fr in range(1,74):
    scene.frame_set(fr);lo,hi=bounds();pose_bounds.append((fr,(hi[2]-lo[2])*1000))
scene.frame_set(1);lo,hi=bounds()
if max(h for _,h in pose_bounds)>600:raise RuntimeError('Gesture exceeds 600mm; revise head/ears rather than scaling hardware')

# Soft studio, matching the ivory/purple product design palette.
floor=cube('studio ground',(20000,20000,10),(0,0,-6),mat('studio stone',(.09,.11,.14),0,.8),0,stage)
def aim(ob,target):ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
for name,pos,power,size in [('key',(.6,-.8,1.2),38,1),('fill',(-.6,-.4,.65),18,.8),('rim',(.25,.65,1),48,.7)]:
    data=bpy.data.lights.new('B '+name,'AREA');data.energy=power;data.shape='DISK';data.size=size
    ob=bpy.data.objects.new('B '+name,data);stage.objects.link(ob);ob.location=pos;aim(ob,(0,0,.3))
data=bpy.data.cameras.new('B character camera');cam=bpy.data.objects.new('B camera',data);stage.objects.link(cam)
cam.location=(.85,-1.5,.75);aim(cam,(0,-.005,.285));data.type='ORTHO';data.ortho_scale=.73;data.clip_start=.001;scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True
scene.render.resolution_x=1100;scene.render.resolution_y=1300;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.world=bpy.data.worlds.new('B studio world');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.19,.24,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.35;scene.view_settings.view_transform='AgX'
report={'status':'PROPORTION AND MECHANICAL-LAYOUT CONCEPT','source_rev_a_sha256':original_hash,
        'posed_height_mm':round((hi[2]-lo[2])*1000,2),'max_idle_gesture_height_mm':round(max(h for _,h in pose_bounds),2),
        'posed_bounds_mm':[[round(a*1000,2) for a in row] for row in [lo,hi]],
        'illustration_frames':73,'torso_envelope_mm':[146,102,78],'main_head_envelope_mm':[234,112,112],
        'sole_envelope_mm':[96,144,16],'leg_shell_widths_mm':[77,70],
        'mesh_objects':sum(o.type=='MESH' for o in scene.objects),
        'full_size_servo_envelopes':4,'print_export':False,
        'not_validated':['new structural links','joint torque and transmission','electronics packing/cooling','battery mount','camera optics','full-motion interference','balance and locomotion','printable wall construction'],
        'look':'Big bent legs; short rounded torso; small greeting arm; unequal binocular eyes; curious head roll; asymmetric listening fins.'}
(ROOT/'evidence/rev-b-layout.json').write_text(json.dumps(report,indent=2)+'\n')
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL';area.spaces.active.overlay.show_overlays=False
scene.render.filepath=str(OUT/'percival-bdx-hero.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'design/percival-rev-b-bdx.blend'))
bpy.ops.render.render(write_still=True)
result={'file':bpy.data.filepath,'render':scene.render.filepath,'height_mm':report['posed_height_mm'],'max_gesture_height_mm':report['max_idle_gesture_height_mm']}
