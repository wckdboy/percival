"""Blender MCP: Rev D reference-proportion study, preserving approved Rev C.

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
OUT=ROOT/'renders/rev-d'; OUT.mkdir(parents=True,exist_ok=True)
preserved=json.loads((ROOT/'evidence/rev-d-preserved-baseline.json').read_text())
original_hash=preserved['original_rev_a_sha256']
assert hashlib.sha256((ROOT/'design/percival-rev-c-chamfer.blend').read_bytes()).hexdigest()==preserved['original_rev_c_sha256']
previous=bpy.data.scenes.get('Percival • Rev D / reference proportions')
if previous:
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'design/percival-rev-d-first-pass.blend'),copy=True)
    bpy.context.window.scene=bpy.data.scenes['Scene']
    for ob in list(previous.objects):bpy.data.objects.remove(ob,do_unlink=True)
    for col in list(previous.collection.children):bpy.data.collections.remove(col)
    bpy.data.scenes.remove(previous)
scene=bpy.data.scenes.new('Percival • Rev D / reference proportions')
bpy.context.window.scene=scene
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;scene.unit_settings.length_unit='MILLIMETERS'
scene['status']='MECHANICAL-LAYOUT CONCEPT — new chassis, packaging, motion and print validation required'
scene['revision']='D';scene['height_limit_mm']=600
scene['source_relationship']='Approved Rev C checkpoint and Rev A/B/C preserved. Purchased envelopes are full-size. New proposed structural envelopes require engineering.'
bodycol=bpy.data.collections.new('D01 • Proposed body and limbs');scene.collection.children.link(bodycol)
headcol=bpy.data.collections.new('D02 • Expressive head');scene.collection.children.link(headcol)
jointcol=bpy.data.collections.new('D03 • Joint and fastener appearance');scene.collection.children.link(jointcol)
envcol=bpy.data.collections.new('D04 • Full-size purchased envelopes — layout allowances');scene.collection.children.link(envcol)
stage=bpy.data.collections.new('D90 • Studio');scene.collection.children.link(stage)

def mat(name,color,metallic=0,rough=.38):
    m=bpy.data.materials.new('D • '+name);m.diffuse_color=(*color,1);m.use_nodes=True
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
glass=mat('coated optics',(.004,.009,.018),.40,.10)
glass.node_tree.nodes['Principled BSDF'].inputs['Coat Weight'].default_value=.7
cyan=mat('status cyan',(.02,.60,.92),.3,.2)
bs=cyan.node_tree.nodes['Principled BSDF'];bs.inputs['Emission Color'].default_value=(.01,.45,.85,1);bs.inputs['Emission Strength'].default_value=1.6
pcbmat=mat('PCB envelope',(.015,.16,.07),.12,.5)

def own(ob,col):
    for c in list(ob.users_collection):c.objects.unlink(ob)
    col.objects.link(ob)
def finish(ob,name,m,col,parent=None):
    ob.name='D • '+name;own(ob,col)
    if m:ob.data.materials.append(m)
    if parent:ob.parent=parent;ob.matrix_parent_inverse=Matrix.Identity(4)
    ob['status']='CONCEPT GEOMETRY — NOT A RELEASED PRINT PART'
    return ob
def empty(name,loc=(0,0,0),parent=None,col=bodycol):
    o=bpy.data.objects.new('D • '+name,None);col.objects.link(o);o.location=Vector(loc)/1000
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
    back=axis=='-Y';axis='Y' if back else axis
    sign=1 if back else (-1 if axis=='Y' else (-1 if axis=='X' and loc[0]<0 else 1))
    normal=Vector({'X':(sign,0,0),'Y':(0,sign,0),'Z':(0,0,1)}[axis])
    washer=cyl(name+' recessed seat',3.1,.6,loc,dark,axis,parent,vertices=36)
    mesh=bpy.data.meshes.get('D shared socket-head appearance')
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
        mesh=bpy.data.meshes.new('D shared socket-head appearance');mesh.from_pydata(vs,[],fs);mesh.update()
        mesh.materials.append(steel);mesh.materials.append(dark);mesh.polygons[-1].material_index=1
        bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(mesh);bm.free()
    ob=bpy.data.objects.new('D • '+name+' socket screw',mesh);jointcol.objects.link(ob)
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
def joint(name,at,r,side,width=30,cap=ivory):
    x,y,z=at;edge=width/2
    cyl(name+' central actuator case',r,width,(x,y,z),dark)
    for shift in [-width*.32,width*.32]:cyl(name+' casing rib',r+1.2,2,(x+shift,y,z),rubber)
    cyl(name+' polished bearing rim',r+1,3,(x+side*(edge+1),y,z),steel)
    cyl(name+' sculpted joint cover',r-1.5,4,(x+side*(edge+2.5),y,z),cap)
    cyl(name+' inset hub recess',r-7,5,(x+side*(edge+3),y,z),dark)
    cyl(name+' inner bearing ring',r*.36,5.8,(x+side*(edge+4),y,z),steel)
    cyl(name+' axle plug',r*.22,6.4,(x+side*(edge+4.5),y,z),dark)
    for i in range(5):
        a=i*2*math.pi/5
        fastener(name+f' perimeter screw{i}',(x+side*(edge+5),y+math.sin(a)*(r-4),z+math.cos(a)*(r-4)),'X')
    return None

# Variable cross-sections provide sloping armour, rather than repeated boxes.
def chamfer_points(w,h,c):
    c=min(c,w/2-.01,h/2-.01)
    return [(w/2-c,h/2),(-w/2+c,h/2),(-w/2,h/2-c),(-w/2,-h/2+c),(-w/2+c,-h/2),(w/2-c,-h/2),(w/2,-h/2+c),(w/2,h/2-c)]

def loft(name,sections,loc,m=ivory,axis='Z',parent=None,col=bodycol,edge=1):
    # sections: (axial position, width, height/depth, corner clip, centre shift).
    vs=[]
    for a,w,h,c,shift in sections:
        for x,b in chamfer_points(w,h,c):
            vs.append((x/1000,(b+shift)/1000,a/1000) if axis=='Z' else (x/1000,a/1000,(b+shift)/1000))
    n=len(sections);fs=[tuple(range(7,-1,-1)),tuple(range((n-1)*8,n*8))]
    fs += [(j*8+i,j*8+(i+1)%8,(j+1)*8+(i+1)%8,(j+1)*8+i) for j in range(n-1) for i in range(8)]
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],fs);mesh.update()
    ob=bpy.data.objects.new(name,mesh);col.objects.link(ob);ob.location=Vector(loc)/1000;finish(ob,name,m,col,parent)
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(mesh);bm.free()
    if edge:
        mod=ob.modifiers.new('Softened armour chamfers','BEVEL');mod.width=edge/1000;mod.segments=3
        wn=ob.modifiers.new('Armour face normals','WEIGHTED_NORMAL');wn.keep_sharp=True;wn.weight=40
    ob['shape_type']='Tapered multi-section concept shell'
    return ob

def link_shell(name,a,b,wa,wb,da,db,m=ivory):
    a,b=Vector(a),Vector(b);z=(b-a).normalized();length=(b-a).length
    ob=loft(name,[(-length/2,wa*.90,da*.9,8,0),(-length*.25,wa,da,10,0),(length*.30,wb,db,9,0),(length/2,wb*.86,db*.9,7,0)],(a+b)/2,m,edge=1.8)
    y=Vector((0,1,0));y=(y-z*y.dot(z)).normalized();x=y.cross(z)
    ob.rotation_mode='QUATERNION';ob.rotation_quaternion=Matrix((x,y,z)).transposed().to_quaternion()
    return ob

def shaped_plate(name,outline,loc,depth=2,m=ivory,parent=None,col=bodycol):
    n=len(outline);vs=[(x/1000,y/1000,z/1000) for y in [-depth/2,depth/2] for x,z in outline]
    fs=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],fs);mesh.update()
    ob=bpy.data.objects.new(name,mesh);col.objects.link(ob);ob.location=Vector(loc)/1000;finish(ob,name,m,col,parent)
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(mesh);bm.free()
    be=ob.modifiers.new('Panel perimeter edge','BEVEL');be.width=.0008;be.segments=2
    wn=ob.modifiers.new('Plate normals','WEIGHTED_NORMAL');wn.keep_sharp=True
    ob['panel_type']='Shaped concept armour panel'
    return ob

def servo_envelope(name,loc,rotation=(0,0,0)):
    ob=cube(name+' / XM430 28.5×46.5×34 mm',(28.5,34,46.5),loc,dark,1,col=envcol)
    ob.rotation_euler=Euler(rotation,'XYZ');ob.display_type='WIRE';ob.hide_render=True
    ob['manufacturer_envelope_mm']=[28.5,46.5,34]
    ob['status']='FULL-SIZE PURCHASED ENVELOPE; joint assignment/torque/mounting unverified'
    return ob

# Reference-led taller, tapered chest with central vertical service spine.
torso=loft('tapered torso enclosure',[(-49,86,62,12,0),(-36,113,86,13,0),(22,120,96,16,0),(42,108,81,14,0),(49,85,66,12,0)],(0,7,306),ivory,edge=2)
torso['repackaging_required']='New reference-proportion torso; mounting, wall thickness, cooling and complete hardware packing unresolved.'
# Front armour is split into two shaped cheeks and one long purple hatch.
cheek=[(22,40),(42,42),(56,26),(53,-28),(35,-43),(23,-38)]
for side in [-1,1]:
    outline=[(side*x,z) for x,z in cheek]
    shaped_plate('chest cheek seam',outline,(0,-39.8,306),2,dark)
    plate=shaped_plate('chest ivory cheek',[(x*.965,z*.965) for x,z in outline],(0,-41.4,306),2.5,ivory)
    for x,z in [(side*36,34),(side*45,-25),(side*29,-34)]:fastener('chest cheek fixing',(x,-43.2,306+z))
spine=[(-19,39),(19,39),(16,7),(15,-40),(9,-44),(-9,-44),(-15,-40),(-16,7)]
shaped_plate('vertical service spine gasket',[(x*1.12,z*1.02) for x,z in spine],(0,-42,306),2,dark)
shaped_plate('vertical purple chest spine',spine,(0,-43.7,306),2.5,violet)
for x in [-12,12]:
    for z in [338,273]:fastener('spine captive screw',(x,-45.3,z))
for z in [306,320]:cube('spine panel seam',(30,1,0.8),(0,-45.3,z),dark,.15)
rr('chest status rim',18,5.5,2,(35,-43,325),2.6,dark,col=bodycol)
rr('chest cyan status light',14,2.6,2,(35,-44.2,325),1.2,cyan,col=bodycol)
for row in range(5):
    for col in range(4):
        x=29+col*4.5+(row%2)*2.1;z=299+row*4.8
        if x<47:cyl('speaker perforation',1.1,1,(x,-43.1,z),dark,'Y',col=bodycol,vertices=20)
# Distinct dark waist and narrow central pelvic pod.
cyl('waist yaw bearing',29,15,(0,7,248),dark,'Z')
cyl('waist lower trim',25,3,(0,7,240),steel,'Z')
cube('waist gimbal fork',(64,48,20),(0,7,243),dark,5)
for side in [-1,1]:
    cyl('waist side pivot',15,7,(side*31,7,245),dark,'X')
    cyl('waist side rim',10,8,(side*32,7,245),steel,'X')
    pipe('torso side service hose',[(side*62,14,317),(side*65,24,281),(side*40,21,256)],2.7,dark)
pelvis=loft('separate pelvic pod',[(-29,54,52,10,0),(-18,72,70,12,0),(20,76,70,13,0),(29,58,54,10,0)],(0,8,215),ivory,edge=2)
panel('pelvis vertical hatch seam',51,45,2,(0,-28,215),8,dark)
panel('pelvis ivory hatch',47,42,2.5,(0,-29.6,215),7,ivory)
for x in [-17,17]:
    for z in [202,230]:fastener('pelvis access screw',(x,-31.2,z))
# Compact rear pack and recognisable orange handle.
backpack=cube('removable rear pack',(80,45,85),(0,73,307),dark,8)
panel('backpack rear hatch',65,68,3,(0,97,307),8,dark)
pipe('orange backpack handle',[(-22,74,350),(-22,74,361),(22,74,361),(22,74,350)],3.2,orange)
for x in [-24,24]:
    for z in [283,331]:fastener('backpack screw',(x,99,z),'-Y')
# Full-size purchased envelopes, not a complete validated component allocation.
cube('J401 carrier envelope — full size',(100,80,1.6),(0,7,292),pcbmat,.3,envcol).hide_render=True
cube('J401 cooling clearance — allowance',(100,80,35),(0,7,312),dark,1,envcol).hide_render=True
cube('CNHL 4S nominal battery envelope',(76,38,47),(0,73,307),dark,1,envcol).hide_render=True
for ob in envcol.objects:
    ob.display_type='WIRE';ob['status']='PACKAGING ENVELOPE ONLY; connectors, cooling and mounting unresolved'

# Shorter leg links: hip/knee discs and wrapping armour provide the bulk.
for side,label,foot_y,knee_y,knee_z in [(1,'L',-18,-27,132),(-1,'R',-3,-17,138)]:
    hip=(side*60,8,216);knee=(side*70,knee_y,knee_z);ankle=(side*73,foot_y+18,56)
    joint(label+' hip',hip,31,side,34,steel)
    joint(label+' knee',knee,28,side,35,ivory)
    joint(label+' ankle',ankle,20,side,29,dark)
    a,b=Vector(hip),Vector(knee);u=(b-a).normalized()
    thigh=link_shell(label+' tapered thigh armour',a+u*15,b-u*10,61,56,59,55)
    thigh['mechanical_change']='New shorter leg links; torque, bearings, transmission and collisions unverified.'
    # Shaped thigh cover terminates around the knee instead of a rectangular plaque.
    p=[(-20,27),(19,27),(27,15),(24,-19),(15,-28),(-15,-28),(-25,-17),(-26,13)]
    shaped_plate(label+' thigh seam',p,(0,-28.6,0),1.3,dark,thigh)
    shaped_plate(label+' thigh ivory wrap',[(x*.95,z*.95) for x,z in p],(0,-30,0),2.2,ivory,thigh)
    for x,z in [(-16,18),(16,18),(-15,-18),(15,-18)]:fastener(label+' thigh screw',(x,-31.6,z),parent=thigh)
    # A purple vertical knee guard echoes the reference's kneecap panel.
    p=[(-17,18),(17,18),(20,9),(15,-21),(8,-27),(-8,-27),(-16,-20),(-20,9)]
    shaped_plate(label+' kneecap gasket',[(x*1.1,z*1.08) for x,z in p],(knee[0],knee[1]-26,knee[2]),2,dark)
    shaped_plate(label+' purple wrapping knee guard',p,(knee[0],knee[1]-28,knee[2]),2.6,violet)
    for x,z in [(-12,11),(12,11),(-9,-16),(9,-16)]:fastener(label+' knee guard screw',(knee[0]+x,knee[1]-30,z+knee[2]))
    a,b=Vector(knee),Vector(ankle);u=(b-a).normalized()
    shin=link_shell(label+' tapered shin armour',a+u*17,b-u*8,52,45,47,42)
    # Front dark insert and small ivory rail plates suggest a clevis around the mechanism.
    panel(label+' shin mechanism insert',26,39,2,(0,-24,0),4,dark,shin)
    for x in [-19,19]:
        panel(label+' shin side rail',9,42,2,(x,-24,0),3,ivory,shin)
        for z in [-13,13]:fastener(label+' shin rail screw',(x,-25.7,z),parent=shin)
    for z in [-10,0,10]:cube(label+' shin recess rib',(19,1.2,2),(0,-25.5,z),rubber,.3,parent=shin)
    pipe(label+' ankle cable',[(side*93,knee_y+17,knee_z-10),(side*98,foot_y+35,88),(side*88,foot_y+31,60)],2.4,dark)
    foot=empty(label+' foot',(side*73,foot_y,0));foot.rotation_euler.z=math.radians(-side*6)
    loft(label+' shaped rubber sole',[(0,87,134,14,0),(5,88,134,14,0),(9,86,132,13,0)],(0,0,0),rubber,parent=foot,edge=.6)
    cube(label+' boot midsole gasket',(81,122,8),(0,0,11),rubber,3,parent=foot)
    loft(label+' sloping boot upper',[(-62,61,17,7,23.5),(-40,85,31,9,30.5),(-3,83,40,10,35),(29,72,39,9,34.5),(56,55,19,7,24.5)],(0,0,0),ivory,'Y',foot,edge=1.8)
    cube(label+' separate rubber heel',(61,37,17),(0,48,17),rubber,5,parent=foot)
    for name,w,h,z,m in [('instep seam',45,43,49,dark),('purple instep hatch',41,39,50,violet)]:
        plate=panel(label+' '+name,w,h,2,(0,-22,z),5,m,foot);plate.rotation_euler.x=math.radians(97)
    for x in [-14,14]:
        for y in [-35,-9]:fastener(label+' boot hatch screw',(x,y,50.5+(y+22)*.12),'Z',foot)
    panel(label+' front toe bumper',62,9,4,(0,-64,11),4,rubber,foot)
    for x in [-25,-8,8,25]:cube(label+' toe tread notch',(2.2,4,7),(x,-66.5,7),dark,.5,parent=foot)
    cube(label+' heel orange latch',(47,8,8),(0,43,36),orange,2,parent=foot)
    servo_envelope(label+' knee servo',knee)
    servo_envelope(label+' hip servo',hip)

# Slimmer articulated arms, with a reference-like raised greeting on the left of the image.
for label,side,shoulder,elbow,wrist,hand in [
    ('L',1,(80,5,334),(111,-2,280),(132,-20,226),(134,-25,210)),
    ('R',-1,(-80,5,334),(-120,-7,300),(-151,-25,351),(-155,-29,367))]:
    joint(label+' shoulder',shoulder,23,side,27,ivory)
    cyl(label+' shoulder orange seal',23.7,2,(shoulder[0]-side*9,shoulder[1],shoulder[2]),orange)
    joint(label+' elbow',elbow,14,side,24,dark)
    a,b=Vector(shoulder),Vector(elbow);u=(b-a).normalized()
    upper=link_shell(label+' sculpted upper arm',a+u*18,b-u*10,35,31,36,31)
    a,b=Vector(elbow),Vector(wrist);u=(b-a).normalized()
    forearm=link_shell(label+' sculpted forearm',a+u*9,b-u*7,33,29,34,29)
    for link,name,depth in [(upper,'upper arm',18),(forearm,'forearm',17)]:
        panel(label+' '+name+' face seam',23,30,1.4,(0,-depth,0),4,dark,link)
        panel(label+' '+name+' ivory face',20.5,28,2,(0,-depth-1.4,0),3.5,ivory,link)
        for z in [-9,9]:fastener(label+' '+name+' fastener',(0,-depth-2.7,z),parent=link)
    cube(label+' orange forearm control',(7,4,19),(12,-16,0),orange,1.8,parent=forearm)
    cyl(label+' wrist joint',10,17,wrist,dark)
    root=empty(label+' gripper pose pivot',wrist);direction=(Vector(hand)-Vector(wrist)).normalized()
    front_y=Vector((0,1,0));front_y=(front_y-direction*front_y.dot(direction)).normalized();palm_x=front_y.cross(direction)
    root.rotation_mode='QUATERNION';root.rotation_quaternion=Matrix((palm_x,front_y,direction)).transposed().to_quaternion()
    cube(label+' palm mechanism',(26,20,20),(0,0,14),dark,4,parent=root)
    panel(label+' palm armour',24,21,3,(0,-10.8,14),5,ivory,root)
    for x in [-8,8]:fastener(label+' palm screw',(x,-13,14),parent=root)
    for x in [-8,8]:
        f=cube(label+' little claw finger',(10,16,24),(x,-3,36),rubber,3,parent=root);f.rotation_euler.y=math.radians(-x*.7)
    cyl(label+' amber thumb pivot',3.8,4,(15,0,14),orange,'X',root)

# Visible neck gimbal between chest and head.
cyl('neck yaw mechanism',24,16,(0,7,365),dark,'Z')
cyl('neck lower trim',21,3,(0,7,374),steel,'Z')
cube('neck pitch fork',(46,34,20),(0,6,381),dark,5)
cyl('neck pitch axle',12,58,(0,6,382),dark)
for side in [-1,1]:
    cyl('neck pitch rim',8,3,(side*30,6,382),steel)
    cyl('neck pitch hub',5,4,(side*31,6,382),dark)
pipe('neck service loop',[(-21,17,371),(-33,23,385),(-29,21,405)],2.5,dark)
head=empty('head pose pivot',(0,-9,438),col=headcol)
head.rotation_euler=(math.radians(-3),math.radians(6),math.radians(-5))
# Rounded/chamfered deep shell: narrower at the back, broadest near the visor.
shell=loft('sculpted deep head shell',[(-59,224,108,24,0),(-45,234,112,25,0),(38,226,110,25,0),(65,200,94,23,0)],(0,0,0),ivory,'Y',head,headcol,edge=2.4)
for mod in list(shell.modifiers):
    bpy.context.view_layer.objects.active=shell;bpy.ops.object.modifier_apply(modifier=mod.name)
inner=loft('head internal cavity',[(-56,219,103,22,0),(-43,229,107,23,0),(37,221,105,23,0),(62,195,89,21,0)],(0,0,0),None,'Y',head,headcol,edge=0);boolean(shell,inner)
opening=rr('recessed visor opening',186,76,25,(0,-56,0),13,None,head);boolean(shell,opening)
be=shell.modifiers.new('Fine shell parting edge','BEVEL');be.width=.0008;be.segments=2
visor=rr('recessed black face',185.4,75.4,3,(0,-59.2,0),12.7,face,head)
# The wide ivory bezel is divided by fine seams and perimeter hardware.
for side in [-1,1]:
    for z in [-39,39]:fastener('head bezel socket',(side*94,-60.7,z),parent=head)
    for z in [-22,22]:fastener('bezel edge fixing',(side*109,-55.5,z),parent=head)
    for z in [-1,1]:
        seam=cube('bezel panel split',(0.7,1.4,14),(side*71,-60,z*47),dark,.15,headcol,head)
for x,z,r,label in [(-53,3,25,'large eye'),(54,0,18.5,'small eye')]:
    cyl(label+' recessed outer housing',r,3.5,(x,-61.3,z),dark,'Y',head)
    cyl(label+' aperture bevel',r-3,4,(x,-63,z),rubber,'Y',head)
    cyl(label+' alloy lens rim',r-6,4.5,(x,-64,z),steel,'Y',head)
    cyl(label+' black lens barrel',r-7,6,(x,-65,z),face,'Y',head)
    cyl(label+' coated glass',r-10,6.5,(x,-66,z),glass,'Y',head)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=20,radius=1,location=Vector((x,-68.8,z))/1000)
    lens=bpy.context.object;lens.scale=((r-10.7)/1000,1.9/1000,(r-10.7)/1000)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);finish(lens,label+' convex optical surface',glass,headcol,head)
    for poly in lens.data.polygons:poly.use_smooth=True
    camera=cube(label+' B0202 full-size board',(38,1.6,38),(x,-32,z),pcbmat,.3,envcol,head)
    camera.hide_render=True;camera.display_type='WIRE';camera['verified_envelope']='38 ×38 mm PCB only; lens integration unresolved'
# Central dark depth-sensor capsule and small upper status LED.
rr('central sensor bezel',40,17,2.3,(0,-61,-12),8,dark,head)
rr('central sensor inset',35,12,2.7,(0,-62,-12),5.8,face,head)
for x in [-12,12]:
    cyl('small sensor rim',4.3,3,(x,-63,-12),steel,'Y',head,vertices=32)
    cyl('small sensor optic',3.2,4,(x,-64,-12),glass,'Y',head,vertices=32)
cyl('central tiny sensor',1.8,3,(0,-63,-12),dark,'Y',head,vertices=24)
cyl('upper blue status light',2,2,(-7,-62,24),cyan,'Y',head,vertices=32)
for x in [5,15]:cyl('upper microphone port',1.2,2,(x,-61.5,24),dark,'Y',head,vertices=24)
rr('lower service port',12,3,2,(0,-61,-29),1.4,dark,head)
for x in [-82,82]:
    for z in [-26,26]:fastener('black face screw',(x,-61.2,z),parent=head)
# Broad purple cheek discs with black, screwed covers.
for side in [-1,1]:
    cyl('purple ear pod',34,12,(side*116,4,0),violet,'X',head)
    cyl('ear outer graphite rim',28,14,(side*119,4,0),dark,'X',head)
    cyl('ear inset cap',23,15,(side*120,4,0),face,'X',head)
    for i in range(6):
        a=i*math.pi/3;fastener('ear cover socket',(side*128,4+math.sin(a)*24,math.cos(a)*24),'X',head)
    earroot=empty('ear hinge',(side*102,3,46),head,headcol)
    earroot.rotation_euler.y=math.radians(side*(11 if side<0 else 15))
    cyl('ear hinge axle',8,18,(0,0,0),dark,'X',earroot)
    rr('ivory listening fin',22,47,9,(0,1,24),7,ivory,earroot)
    rr('black listening fin inset',14,38,2,(0,-4,25),5,dark,earroot)
    rr('orange fin side strip',4,29,2,(side*8,-5,25),1.7,orange,earroot)
    fastener('fin hinge fixing',(0,-5,6),parent=earroot)
# Top hatch, low turret and antenna, matching the top-view silhouette.
for name,w,h,z,m in [('crown hatch gasket',59,36,55.8,dark),('crown purple hatch',55,32,57,violet)]:
    p=panel(name,w,h,2,(0,-26,z),5,m,head,headcol);p.rotation_euler.x=math.pi/2
for x in [-20,20]:
    for y in [-36,-16]:fastener('crown hatch fixing',(x,y,58.3),'Z',head)
cyl('top auxiliary turret',9,8,(-54,13,58),dark,'Z',head)
cyl('antenna base',5,7,(64,18,58),dark,'Z',head)
cyl('slim antenna lower',2.6,20,(64,18,70),rubber,'Z',head,vertices=24)
cyl('slim antenna whip',1.8,41,(64,18,97),dark,'Z',head,vertices=24)
# Fine case seams around the top and rear establish removable shell sections.
for x in [-69,69]:cube('top case panel seam',(.7,86,.7),(x,0,56.2),dark,.1,headcol,head)
for x in [-85,85]:
    for y in [-36,33]:fastener('top shell screw',(x,y,54.4),'Z',head)

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
    data=bpy.data.lights.new('D '+name,'AREA');data.energy=power;data.shape='DISK';data.size=size
    ob=bpy.data.objects.new('D '+name,data);stage.objects.link(ob);ob.location=pos;aim(ob,(0,0,.3))
data=bpy.data.cameras.new('D character camera');cam=bpy.data.objects.new('D camera',data);stage.objects.link(cam)
cam.location=(.85,-1.65,.70);aim(cam,(0,-.005,.280));data.type='ORTHO';data.ortho_scale=.69;data.clip_start=.001;scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True
scene.render.resolution_x=1100;scene.render.resolution_y=1300;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.world=bpy.data.worlds.new('D studio world');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.19,.24,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.35;scene.view_settings.view_transform='AgX'
report={'status':'PROPORTION AND MECHANICAL-LAYOUT CONCEPT','source_rev_a_sha256':original_hash,'source_rev_b_sha256':preserved['original_rev_b_sha256'],
        'source_rev_c_sha256':preserved['original_rev_c_sha256'],
        'approved_rev_c_checkpoint':preserved['approved_checkpoint'],'approved_rev_c_sha256':preserved['approved_checkpoint_sha256'],
        'posed_height_mm':round((hi[2]-lo[2])*1000,2),'max_idle_gesture_height_mm':round(max(h for _,h in pose_bounds),2),
        'posed_bounds_mm':[[round(a*1000,2) for a in row] for row in [lo,hi]],
        'illustration_frames':73,'torso_envelope_mm':[120,96,98],'main_head_envelope_mm':[234,124,112],
        'sole_envelope_mm':[88,134,9],'leg_shell_widths_mm':[61,52],
        'hip_axis_height_mm':216,'knee_axis_heights_mm':[132,138],'ankle_axis_height_mm':56,
        'reference_ratios_are':'visual estimates from the supplied front/top/side images; not dimensional measurements of real hardware',
        'mesh_objects':sum(o.type=='MESH' for o in scene.objects),
        'full_size_servo_envelopes':4,'print_export':False,
        'not_validated':['new structural links','joint torque and transmission','electronics packing/cooling','battery mount','camera optics','full-motion interference','balance and locomotion','printable wall construction'],
        'look':'Reference proportions: lower hips, sculpted tapered chest and pelvis, wrapping leg armour, sloping boots, slimmer articulated arms, smaller recessed optics and central sensor capsule.'}
(ROOT/'evidence/rev-d-layout.json').write_text(json.dumps(report,indent=2)+'\n')
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL';area.spaces.active.overlay.show_overlays=False
scene.render.filepath=str(OUT/'percival-rev-d-hero.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'design/percival-rev-d-reference.blend'))
bpy.ops.render.render(write_still=True)
result={'file':bpy.data.filepath,'render':scene.render.filepath,'height_mm':report['posed_height_mm'],'max_gesture_height_mm':report['max_idle_gesture_height_mm']}
