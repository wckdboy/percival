"""Blender MCP: Rev C compact industrial character study, preserving approved Rev B.

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
OUT=ROOT/'renders/rev-c'; OUT.mkdir(parents=True,exist_ok=True)
preserved=json.loads((ROOT/'evidence/rev-c-preserved-baseline.json').read_text())
original_hash=preserved['original_rev_a_sha256']
assert hashlib.sha256((ROOT/'design/percival-rev-b-bdx.blend').read_bytes()).hexdigest()==preserved['original_rev_b_sha256']
previous=bpy.data.scenes.get('Percival • Rev C / compact industrial character')
if previous:
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'design/percival-rev-c-first-pass.blend'),copy=True)
    bpy.context.window.scene=bpy.data.scenes['Scene']
    for ob in list(previous.objects):bpy.data.objects.remove(ob,do_unlink=True)
    for col in list(previous.collection.children):bpy.data.collections.remove(col)
    bpy.data.scenes.remove(previous)
scene=bpy.data.scenes.new('Percival • Rev C / compact industrial character')
bpy.context.window.scene=scene
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;scene.unit_settings.length_unit='MILLIMETERS'
scene['status']='MECHANICAL-LAYOUT CONCEPT — new chassis, packaging, motion and print validation required'
scene['revision']='C';scene['height_limit_mm']=600
scene['source_relationship']='Approved Rev B checkpoint and Rev A preserved. Purchased envelopes are full-size. New proposed structural envelopes require engineering.'
bodycol=bpy.data.collections.new('C01 • Proposed body and limbs');scene.collection.children.link(bodycol)
headcol=bpy.data.collections.new('C02 • Expressive head');scene.collection.children.link(headcol)
jointcol=bpy.data.collections.new('C03 • Joint and fastener appearance');scene.collection.children.link(jointcol)
envcol=bpy.data.collections.new('C04 • Full-size purchased envelopes — layout allowances');scene.collection.children.link(envcol)
stage=bpy.data.collections.new('C90 • Studio');scene.collection.children.link(stage)

def mat(name,color,metallic=0,rough=.38):
    m=bpy.data.materials.new('C • '+name);m.diffuse_color=(*color,1);m.use_nodes=True
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
    ob.name='C • '+name;own(ob,col)
    if m:ob.data.materials.append(m)
    if parent:ob.parent=parent;ob.matrix_parent_inverse=Matrix.Identity(4)
    ob['status']='CONCEPT GEOMETRY — NOT A RELEASED PRINT PART'
    return ob
def empty(name,loc=(0,0,0),parent=None,col=bodycol):
    o=bpy.data.objects.new('C • '+name,None);col.objects.link(o);o.location=Vector(loc)/1000
    o.empty_display_type='PLAIN_AXES';o.empty_display_size=.012
    if parent:o.parent=parent
    return o
def cube(name,dims,loc,m=ivory,r=3,col=bodycol,parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=Vector(loc)/1000)
    o=bpy.context.object;o.dimensions=Vector(dims)/1000;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    finish(o,name,m,col,parent)
    if r:
        mod=o.modifiers.new('Broad flat chamfer','BEVEL');mod.width=r/1000;mod.segments=1
        micro=o.modifiers.new('Small edge break','BEVEL');micro.width=min(r/1000*.10,.0007);micro.segments=2
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
    z=v.normalized();y=Vector((0,1,0));y=(y-z*y.dot(z)).normalized();x=y.cross(z)
    ob.rotation_mode='QUATERNION';ob.rotation_quaternion=Matrix((x,y,z)).transposed().to_quaternion();return ob
def pipe(name,pts,r,m=dark,parent=None,col=jointcol):
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=12
    cu.bevel_depth=r/1000;cu.bevel_resolution=3;s=cu.splines.new('BEZIER');s.bezier_points.add(len(pts)-1)
    for p,co in zip(s.bezier_points,pts):p.co=Vector(co)/1000;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    ob=bpy.data.objects.new(name,cu);col.objects.link(ob);finish(ob,name,m,col,parent);return ob
def fastener(name,loc,axis='Y',parent=None):
    # Circular machined head with an actual recessed hexagonal socket.
    # Appearance geometry, not a purchasable fastener specification.
    sign=-1 if axis=='Y' else (-1 if axis=='X' and loc[0]<0 else 1)
    normal=Vector({'X':(sign,0,0),'Y':(0,sign,0),'Z':(0,0,1)}[axis])
    washer=cyl(name+' recessed seat',3.1,.6,loc,dark,axis,parent,vertices=36)
    mesh=bpy.data.meshes.get('C shared socket-head appearance')
    if mesh is None:
        vs=[];n=36
        for ring in range(4):
            for i in range(n):
                a=2*math.pi*i/n
                radius=2.25 if ring<2 else 1.05*math.cos(math.pi/6)/math.cos(a%(math.pi/3)-math.pi/6)
                z=[-.2,.65,.65,.03][ring]
                vs.append((radius*math.cos(a)/1000,radius*math.sin(a)/1000,z/1000))
        fs=[]
        for ring in range(3):
            for i in range(n):fs.append((ring*n+i,ring*n+(i+1)%n,(ring+1)*n+(i+1)%n,(ring+1)*n+i))
        fs.append(tuple(range(3*n,4*n)))
        mesh=bpy.data.meshes.new('C shared socket-head appearance');mesh.from_pydata(vs,[],fs);mesh.update()
        mesh.materials.append(steel);mesh.materials.append(dark);mesh.polygons[-1].material_index=1
        bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(mesh);bm.free()
    ob=bpy.data.objects.new('C • '+name+' socket screw',mesh);jointcol.objects.link(ob)
    ob.location=(Vector(loc)+normal*.2)/1000
    ob.rotation_mode='QUATERNION';ob.rotation_quaternion=normal.to_track_quat('Z','Y')
    if parent:ob.parent=parent
    ob['status']='CONCEPT FASTENER APPEARANCE; thread/mount not designed'
    return ob

def panel(name,w,h,d,loc,clip,m=ivory,parent=None,col=bodycol):
    clip=min(clip,w/2-.01,h/2-.01)
    pts=[(w/2-clip,h/2),(-w/2+clip,h/2),(-w/2,h/2-clip),(-w/2,-h/2+clip),(-w/2+clip,-h/2),(w/2-clip,-h/2),(w/2,-h/2+clip),(w/2,h/2-clip)]
    n=len(pts);vs=[(x/1000,y/1000,z/1000) for y in [-d/2,d/2] for x,z in pts]
    fs=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],fs);mesh.update()
    ob=bpy.data.objects.new(name,mesh);col.objects.link(ob);ob.location=Vector(loc)/1000
    finish(ob,name,m,col,parent)
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(mesh);bm.free()
    if m is not None:
        mod=ob.modifiers.new('Fine panel edge break','BEVEL');mod.width=.0005;mod.segments=2
        normal=ob.modifiers.new('Panel weighted normals','WEIGHTED_NORMAL');normal.keep_sharp=True
    ob['panel_type']='Clipped-corner concept armour with flat chamfers'
    return ob

def stencil(name,text,loc,size=5,parent=None,col=bodycol):
    cu=bpy.data.curves.new(name,'FONT');cu.body=text;cu.size=size/1000;cu.extrude=.00004;cu.space_character=1.2
    ob=bpy.data.objects.new(name,cu);col.objects.link(ob);finish(ob,name,steel,col,parent)
    ob.location=Vector(loc)/1000;ob.rotation_euler.x=math.pi/2
    return ob
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

# Compact faceted torso; the main leg and head volumes dominate the silhouette.
torso=cube('compact chamfered torso',(136,98,62),(0,8,327),ivory,10)
torso['repackaging_required']='New 62mm torso: full electronics fit/cooling and structural design unresolved.'
cube('waist bellows',(93,66,24),(0,8,289),dark,5)
cube('pelvic bridge',(122,74,34),(0,9,296),ivory,8)
panel('pelvis front seam',83,24,2,(0,-29,296),6,dark)
panel('pelvis front armour',79,21,2,(0,-30.5,296),5,ivory)
for x in [-28,28]:fastener('pelvis screw',(x,-32,296))
panel('torso face parting gasket',111,48,2,(0,-41,328),9,dark)
panel('torso face armour',108,45,2,(0,-42.5,328),8,ivory)
panel('violet chest service hatch',40,37,2.5,(-28,-44,328),6,violet)
for x in [-40,-16]:
    for z in [317,339]:fastener('chest hatch screw',(x,-46,z))
for x in [-48,48]:
    for z in [314,342]:fastener('torso corner screw',(x,-44.3,z))
rr('cyan chest status slit',21,3.5,2,(26,-44,342),1.6,cyan,col=bodycol)
for x in [10,17,24,31,38]:
    vent=rr('angled chest cooling slot',2.3,12,1.6,(x,-44,328),1.1,dark,col=bodycol)
    vent.rotation_euler.y=math.radians(-20)
stencil('chest serial','P-03',(9,-45,315),5.2)
backpack=cube('compact rear battery housing',(87,53,66),(0,82,327),dark,6)
panel('rear battery hatch',72,51,3,(0,109,327),7,violet)
for x in [-25,25]:
    for z in [309,345]:fastener('backpack hatch screw',(x,111, z))
pipe('orange carry loop',[(-24,82,360),(-24,82,371),(24,82,371),(24,82,360)],3,orange)
cube('J401 carrier envelope — full size',(100,80,1.6),(0,7,317),pcbmat,.3,envcol).hide_render=True
cube('J401 cooling clearance — allowance',(100,80,35),(0,7,336),dark,1,envcol).hide_render=True
cube('CNHL 4S nominal battery envelope',(76,38,47),(0,82,327),dark,1,envcol).hide_render=True
for ob in envcol.objects:
    ob.display_type='WIRE';ob['status']='PACKAGING ENVELOPE ONLY; connectors, cooling and mounting unresolved'

# Slightly shorter links with wider, chamfered armour and more substantial boots.
for side,label,foot_y,knee_y,knee_z in [(1,'L',-35,-48,162),(-1,'R',-8,-25,170)]:
    hip=(side*65,10,294);knee=(side*83,knee_y,knee_z);ankle=(side*88,foot_y+24,61)
    joint(label+' hip',hip,36,side)
    joint(label+' knee',knee,33,side)
    joint(label+' ankle',ankle,25,side)
    a=Vector(hip);b=Vector(knee);u=(b-a).normalized()
    thigh=bar(label+' wide chamfered thigh',a+u*24,b-u*24,86,80,ivory,10)
    thigh['mechanical_change']='New structural geometry; source chassis compatibility not established.'
    a=Vector(knee);b=Vector(ankle);u=(b-a).normalized()
    shin=bar(label+' chunky chamfered shin',a+u*21,b-u*18,79,74,ivory,9)
    for link,name,width,height,depth in [(thigh,'thigh',64,72,80),(shin,'shin',59,56,74)]:
        front=-depth/2
        panel(label+' '+name+' dark panel seam',width+3,height+3,1.5,(0,front-.6,0),9,dark,link)
        panel(label+' '+name+' angular faceplate',width,height,2.4,(0,front-2,0),8,ivory,link)
        panel(label+' '+name+' violet insert',25,height-20,2,(0,front-3.5,0),4,violet,link)
        for x in [-width/2+10,width/2-10]:
            for z in [-height/2+10,height/2-10]:fastener(label+' '+name+' panel screw',(x,front-4,z),parent=link)
        for z in [-8,0,8]:
            slot=cube(label+' '+name+' edge vent',(8,1,1.6),(width/2-8,front-3.6,z),dark,.3,parent=link)
    # Knee face plates interrupt the exposed barrel while leaving side discs visible.
    panel(label+' kneecap gasket',48,32,2,(knee[0],knee[1]-31,knee[2]),7,dark)
    panel(label+' violet kneecap',43,27,2,(knee[0],knee[1]-33,knee[2]),6,violet)
    for x in [-13,13]:fastener(label+' knee face screw',(knee[0]+x,knee[1]-35,knee[2]))
    cube(label+' knee amber service tab',(18,3,4),(knee[0],knee[1]-35,knee[2]-8),orange,.8)
    pipe(label+' ankle service cable',[(side*108,knee_y+24,knee_z-10),(side*116,foot_y+49,108),(side*105,foot_y+43,69)],2.7,dark)
    foot=empty(label+' foot',(side*88,foot_y,0));foot.rotation_euler.z=math.radians(-side*7)
    cube(label+' broad rubber sole',(102,148,16),(0,0,8),rubber,5,parent=foot)
    cube(label+' chamfered boot shell',(95,134,37),(0,0,29),ivory,9,parent=foot)
    for name,w,h,z,m in [('toe gasket',70,66,47,dark),('toe service panel',66,62,48.4,violet)]:
        p=panel(label+' '+name,w,h,2,(0,-24,z),9,m,foot);p.rotation_euler.x=math.pi/2
    for x in [-23,23]:
        for y in [-43,-5]:fastener(label+' boot panel screw',(x,y,50),'Z',foot)
    cube(label+' split toe bumper',(77,7,13),(0,-72,12),rubber,2,parent=foot)
    for x in [-29,-10,10,29]:cube(label+' tread divider',(2,5,10),(x,-75,11),dark,.5,parent=foot)
    cube(label+' amber heel latch',(45,8,8),(0,64,22),orange,1.5,parent=foot)
    servo_envelope(label+' knee servo',knee)
    servo_envelope(label+' hip servo',hip)

# Compact arms retain an asymmetric friendly greeting pose.
for label,side,shoulder,elbow,wrist,hand in [
    ('R',-1,(-91,5,340),(-117,-3,309),(-124,-26,288),(-125,-32,275)),
    ('L',1,(91,5,340),(124,-8,342),(144,-30,373),(153,-36,389))]:
    joint(label+' shoulder',shoulder,18,side)
    joint(label+' elbow',elbow,12.5,side)
    a,b=Vector(shoulder),Vector(elbow);u=(b-a).normalized()
    upper=bar(label+' short upper arm',a+u*10,b-u*8,31,33,ivory,6)
    a,b=Vector(elbow),Vector(wrist);u=(b-a).normalized()
    forearm=bar(label+' short forearm',a+u*8,b-u*6,28,31,ivory,5)
    panel(label+' forearm seam',22,24,1,(0,-16,0),4,dark,forearm)
    panel(label+' forearm hatch',19,21,1.6,(0,-17,0),3,ivory,forearm)
    for z in [-6,6]:fastener(label+' forearm screw',(0,-18,z),parent=forearm)
    cube(label+' orange arm latch',(5,3,12),(11,-16,0),orange,1,parent=forearm)
    cyl(label+' wrist collar',10.5,16,wrist,dark)
    root=empty(label+' gripper pose pivot',wrist)
    direction=(Vector(hand)-Vector(wrist)).normalized()
    root.rotation_mode='QUATERNION';root.rotation_quaternion=direction.to_track_quat('Z','Y')
    cube(label+' little palm',(25,21,21),(0,0,14),ivory,4,parent=root)
    panel(label+' palm purple hatch',17,12,1.5,(0,-11.5,14),2.5,violet,root)
    for x in [-6,6]:fastener(label+' palm screw',(x,-13,14),parent=root)
    for x in [-7.5,7.5]:
        finger=cube(label+' compact gripper finger',(9,15,18),(x,-2,32),dark,3,parent=root)
        finger.rotation_euler.y=math.radians(-x*.45)
        cube(label+' rubber fingertip',(8,16,6),(x,-2,39),rubber,2.5,parent=root)
    cyl(label+' thumb pivot',3.5,3,(14,0,14),orange,'X',root)

# Large clipped-corner head with separate cheeks, brow, and crown access panel.
cyl('neck yaw bearing',23,13,(0,8,366),dark,'Z')
cyl('neck yaw trim',19,3,(0,8,373),violet,'Z')
cube('neck pitch fork',(45,30,19),(0,6,382),dark,4)
cyl('neck pitch axle',11,53,(0,6,385),steel)
head=empty('head pose pivot',(0,-12,428),col=headcol)
head.rotation_euler=(math.radians(-3),math.radians(6),math.radians(-5))
shell=panel('large chamfered head enclosure',242,116,116,(0,0,0),18,ivory,head,headcol)
# Applying only the panel microbevel first keeps the booleans predictable.
for mod in list(shell.modifiers):
    bpy.context.view_layer.objects.active=shell;bpy.ops.object.modifier_apply(modifier=mod.name)
inner=panel('head cavity',237,111,112,(0,2,0),16,None,head,headcol);boolean(shell,inner)
opening=panel('visor opening',216,92,24,(0,-56,0),12,None,head,headcol);boolean(shell,opening)
edge=shell.modifiers.new('Head edge break','BEVEL');edge.width=.0008;edge.segments=2
visor=panel('recessed dark visor',215.4,91.4,3,(0,-57.2,0),11.7,face,head,headcol)
# Four visible corner armour pieces on a recessed dark face.
for side in [-1,1]:
    panel('upper face corner plate',33,16,3,(side*98,-59,48),5,ivory,head,headcol)
    panel('lower face corner plate',33,16,3,(side*98,-59,-48),5,ivory,head,headcol)
    for z in [-48,48]:fastener('face perimeter socket',(side*99,-61,z),parent=head)
for x,z,r,label in [(-57,4,35,'large eye'),(58,1,29,'small eye')]:
    cyl(label+' purple surround',r,6,(x,-60,z),violet,'Y',head)
    cyl(label+' dark optical recess',r-4,8,(x,-63,z),dark,'Y',head)
    cyl(label+' outer black lip',r-7,9,(x,-67,z),face,'Y',head)
    cyl(label+' alloy inner ring',r-14,10,(x,-69,z),steel,'Y',head)
    cyl(label+' glass optic',r-16,11,(x,-71,z),glass,'Y',head)
    camera=cube(label+' B0202 full-size board',(38,1.6,38),(x,-35,z),pcbmat,.3,envcol,head)
    camera.hide_render=True;camera.display_type='WIRE';camera['verified_envelope']='38 ×38 mm PCB; lens depth allowance not released'
    for i in [0,2,4]:
        a=i*2*math.pi/6
        fastener(label+' bezel screw',(x+math.sin(a)*(r-2),-65,z+math.cos(a)*(r-2)),parent=head)
rr('friendly cyan status bar',20,3.6,2,(0,-60,-26),1.8,cyan,head)
for i,x in enumerate([-5,0,5]):cyl('face indicator',1.2,2,(x,-60,25),cyan if i==0 else dark,'Y',head,vertices=24)
stencil('brow serial','P / 03',(-29,-59.5,37),4.5,head,headcol)
for x in [-98,98]:
    for z in [-30,30]:fastener('visor captive screw',(x,-60,z),parent=head)
for side in [-1,1]:
    for name,w,h,x,m in [('cheek gasket',84,87,121.2,dark),('cheek armour',81,84,123,ivory)]:
        p=panel(name,w,h,2,(side*x,3,0),11,m,head,headcol);p.rotation_euler.z=side*math.pi/2
    cyl('ear side housing',28,9,(side*126,3,0),violet,'X',head)
    cyl('ear dark inset',21,11,(side*127,3,0),dark,'X',head)
    cyl('ear alloy hub',12,12,(side*128,3,0),steel,'X',head)
    for y in [-24,30]:
        for z in [-28,28]:fastener('cheek socket screw',(side*125,y,z),'X',head)
    earroot=empty('ear hinge',(side*99,3,47),head,headcol)
    earroot.rotation_euler.y=math.radians(side*(13 if side<0 else 20))
    cyl('ear hinge pin',8.5,23,(0,0,0),dark,'X',earroot)
    tall=55 if side<0 else 42
    panel('angular listening antenna',23,tall,8,(0,1,tall/2+1),5.5,ivory,earroot,headcol)
    panel('antenna dark inlay',14,tall-10,1.8,(0,-4,tall/2+2),3,dark,earroot,headcol)
    panel('antenna amber edge',4,tall-20,2,(side*8,-4.8,tall/2+3),1.5,orange,earroot,headcol)
    fastener('antenna hinge screw',(0,-5,7),parent=earroot)
for name,w,h,z,m in [('crown panel seam',67,47,58.4,dark),('crown removable panel',64,44,59.7,violet)]:
    p=panel(name,w,h,2,(0,2,z),7,m,head,headcol);p.rotation_euler.x=math.pi/2
for x in [-23,23]:
    for y in [-11,15]:fastener('crown socket screw',(x,y,61.5),'Z',head)
# Thin side vents read as inset channels without adding visual clutter to the face.
for side in [-1,1]:
    for y in [-15,-5,5,15]:cube('crown cooling slot',(16,2.4,1),(side*82,y,58.1),dark,.3,headcol,head)
pipe('neck cable loop',[(-20,20,377),(-28,26,394),(-22,23,409)],2.5,dark)

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
floor=cube('studio ground',(200000,200000,1),(0,0,-1.5),mat('studio stone',(.09,.11,.14),0,.8),0,stage)
def aim(ob,target):ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
for name,pos,power,size in [('key',(.6,-.8,1.2),38,1),('fill',(-.6,-.4,.65),18,.8),('rim',(.25,.65,1),48,.7)]:
    data=bpy.data.lights.new('C '+name,'AREA');data.energy=power;data.shape='DISK';data.size=size
    ob=bpy.data.objects.new('C '+name,data);stage.objects.link(ob);ob.location=pos;aim(ob,(0,0,.3))
data=bpy.data.cameras.new('C character camera');cam=bpy.data.objects.new('C camera',data);stage.objects.link(cam)
cam.location=(.85,-1.5,.69);aim(cam,(0,-.005,.270));data.type='ORTHO';data.ortho_scale=.68;data.clip_start=.001;scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True
scene.render.resolution_x=1100;scene.render.resolution_y=1300;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.world=bpy.data.worlds.new('C studio world');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.19,.24,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.35;scene.view_settings.view_transform='AgX'
report={'status':'PROPORTION AND MECHANICAL-LAYOUT CONCEPT','source_rev_a_sha256':original_hash,'source_rev_b_sha256':preserved['original_rev_b_sha256'],
        'approved_rev_b_checkpoint':preserved['approved_checkpoint'],'approved_rev_b_sha256':preserved['approved_checkpoint_sha256'],
        'posed_height_mm':round((hi[2]-lo[2])*1000,2),'max_idle_gesture_height_mm':round(max(h for _,h in pose_bounds),2),
        'posed_bounds_mm':[[round(a*1000,2) for a in row] for row in [lo,hi]],
        'illustration_frames':73,'torso_envelope_mm':[136,98,62],'main_head_envelope_mm':[242,116,116],
        'sole_envelope_mm':[102,148,16],'leg_shell_widths_mm':[86,79],
        'mesh_objects':sum(o.type=='MESH' for o in scene.objects),
        'full_size_servo_envelopes':4,'print_export':False,
        'not_validated':['new structural links','joint torque and transmission','electronics packing/cooling','battery mount','camera optics','full-motion interference','balance and locomotion','printable wall construction'],
        'look':'Shorter character; broad legs and boots; 62mm torso; small arms; large angular head; chamfered panels and recessed socket screws.'}
(ROOT/'evidence/rev-c-layout.json').write_text(json.dumps(report,indent=2)+'\n')
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL';area.spaces.active.overlay.show_overlays=False
scene.render.filepath=str(OUT/'percival-rev-c-hero.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'design/percival-rev-c-chamfer.blend'))
bpy.ops.render.render(write_still=True)
result={'file':bpy.data.filepath,'render':scene.render.filepath,'height_mm':report['posed_height_mm'],'max_gesture_height_mm':report['max_idle_gesture_height_mm']}
