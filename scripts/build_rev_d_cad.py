#!/usr/bin/env python3
"""Generate native Polykrom commands for Percival Rev D, in millimetres.

This is an analytic, editable CAD reconstruction, not a mesh import. Run the
generated stages through polykrom_mcp.py; the .polykrom file retains the sketches,
expressions and feature history. Mechanical release remains a separate task.
"""
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'cad' / 'rev-d'
STAGES = []
C = []
BODIES = []
COLORS = {}
GROUP = []
PRINT_PARTS = []
PALETTE = dict(ivory='#e5dbc7', purple='#624978', dark='#242b33',
               rubber='#151a20', steel='#89939d', orange='#ff940e',
               glass='#172a41', cyan='#5bdaff', pcb='#227557')


def cmd(command, **params):
    C.append(dict(command=command, params=params))


def stage(name):
    if C:
        STAGES.append(dict(name=name, commands=list(C)))
        C.clear()


def component(name):
    cmd('component.activate', component='root')
    cmd('component.create', name=name)
    GROUP.clear()


def register(name, color, printable=False):
    BODIES.append(name)
    GROUP.append(name)
    COLORS.setdefault(color, []).append(name)
    if printable:
        PRINT_PARTS.append(name)


def octagon(w, h, c):
    """All coordinates are expressions: fully constrained, parameter-driven."""
    return [[f'-({w})/2+({c})', f'-({h})/2'],
            [f'({w})/2-({c})', f'-({h})/2'],
            [f'({w})/2', f'-({h})/2+({c})'],
            [f'({w})/2', f'({h})/2-({c})'],
            [f'({w})/2-({c})', f'({h})/2'],
            [f'-({w})/2+({c})', f'({h})/2'],
            [f'-({w})/2', f'({h})/2-({c})'],
            [f'-({w})/2', f'-({h})/2+({c})']]


def sketch(name, origin=(0, 0, 0), axis='Z'):
    # Explicit plane origins are numeric in rc.1. Its offset field, unlike the
    # origin, evaluates expressions and remains linked to the parameters.
    if axis == 'Z':
        base=[float(origin[0]),float(origin[1]),0]
        offset=str(origin[2])
    else:
        base=[float(origin[0]),0,float(origin[2])]
        offset=f'-({origin[1]})'
    cmd('sketch.create',name=name,offset=offset,
        plane=dict(origin=base,x_dir=[1,0,0],
                   y_dir=[0,1,0] if axis=='Z' else [0,0,1]))


def draw_loop(points, first=1):
    points=[[str(x),str(y)] for x,y in points]
    cmd('sketch.line',points=points,closed=True)
    # The kernel auto-binds parameter expressions. Pure numeric coordinates are
    # an editable starting position, so explicitly fix only those static points.
    static=[f'l{i+first}.start' for i,xy in enumerate(points)
            if not re.search(r'\b(?:head_\w+|torso_\w+|body_wall|limb_\w+|sole_\w+|panel_t)\b',' '.join(xy))]
    if static:
        cmd('sketch.constraint.fix',entities=static,fixed=True)


def poly(name, pts, depth, loc=(0, 0, 0), color='ivory', axis='Y', printable=False):
    sketch(name + ' outline', loc, axis)
    draw_loop(pts)
    cmd('sketch.finish')
    cmd('solid.extrude', distance=str(depth), operation='new',
        body_name=name, name=name + ' thickness')
    register(name, color, printable)


def panel(name, w, h, d, loc, c=4, color='ivory', axis='Y', printable=True):
    poly(name, octagon(w, h, c), d, loc, color, axis, printable)


def loft(name, sections, loc=(0, 0, 0), axis='Z', color='ivory', wall=None,
         printable=True):
    """Sections: axial position, width expr, height expr, clip expr, nominal width.

    Annular profiles construct wall solids directly, avoiding offset-shell kernel
    failures. Nominal width is used only to select the initial annular region.
    """
    profiles = []
    for i, section in enumerate(sections):
        a,w,h,clip,nominal=section[:5]
        shift=section[5] if len(section)>5 else 0
        org = [str(v) for v in loc]
        k = 2 if axis == 'Z' else 1
        org[k] = f'({org[k]})+({a})'
        if shift:
            j=1 if axis=='Z' else 2
            org[j]=str(float(org[j])+shift)
        sk = f'{name} section {i + 1}'
        sketch(sk, org, axis)
        draw_loop(octagon(w, h, clip))
        if wall:
            draw_loop(octagon(f'({w})-2*({wall})',
                f'({h})-2*({wall})', f'({clip})-({wall})*(2-sqrt(2))'),9)
        cmd('sketch.finish')
        p = dict(sketch=sk)
        if wall:
            p['profiles'] = [dict(point=[nominal / 2 - 1, 0])]
        profiles.append(p)
    # Two-section lofts are ruled. Joining adjacent segments reproduces the
    # Blender facets without the smooth multi-section loft's envelope overshoot.
    for i in range(len(profiles)-1):
        args=dict(sections=profiles[i:i+2],operation='new' if i==0 else 'join',
                  name=f'{name} ruled segment {i+1}')
        if i==0:
            args['body_name']=name
        else:
            args['targets']=[name]
        cmd('solid.loft',**args)
    register(name, color, printable)


def box(name, dims, loc, color='dark'):
    cmd('solid.box', length=str(dims[0]), width=str(dims[1]), height=str(dims[2]),
        center=[str(v) for v in loc], operation='new', body_name=name, name=name + ' solid')
    register(name, color)


def cyl(name, radius, length, loc, color='dark', axis='X', cut=None):
    base = [str(v) for v in loc]
    k = 'XYZ'.index(axis)
    base[k] = f'({base[k]})-({length})/2'
    args = dict(radius=str(radius), height=str(length), base=base, axis=axis,
                operation='cut' if cut else 'new', name=name + (' bore' if cut else ' turned'))
    if cut:
        args['targets'] = [cut]
    else:
        args['body_name'] = name
    cmd('solid.cylinder', **args)
    if not cut:
        register(name, color)


def move(names, translation=(0, 0, 0), axis=(0, 0, 1), angle='0 deg'):
    cmd('solid.move', bodies=list(names), translate=[str(v) for v in translation],
        axis=list(axis), angle=angle, copy=False)


def screw(name, loc, axis='Y'):
    cyl(name + ' seat', 2.8, .7, loc, 'dark', axis)
    cyl(name + ' head', 2.1, 1.2, loc, 'steel', axis)
    cyl(name + ' socket', .9, 1.5, loc, 'dark', axis)


def joint(name, at, r, side, width, cap='ivory'):
    x, y, z = at
    cyl(name + ' actuator envelope', r, width, at)
    cyl(name + ' bearing rim', r + 1, 3, (x + side * (width / 2 + 1), y, z), 'steel')
    cyl(name + ' cover', r - 1.5, 4, (x + side * (width / 2 + 2.5), y, z), cap)
    cyl(name + ' recessed hub', r - 7, 5, (x + side * (width / 2 + 3), y, z))
    cyl(name + ' axle ring', r * .36, 6, (x + side * (width / 2 + 4), y, z), 'steel')
    cyl(name + ' axle cap', r * .22, 7, (x + side * (width / 2 + 4), y, z))
    for i in range(4):
        a = i * math.pi / 2 + math.pi / 4
        screw(name + f' fixing {i + 1}', (x + side * (width / 2 + 5),
              y + math.sin(a) * (r - 4), z + math.cos(a) * (r - 4)), 'X')


def link(name, a, b, wa, wb, da, db, start, end, scale='limb_scale'):
    delta = [b[i] - a[i] for i in range(3)]
    length = math.sqrt(sum(v*v for v in delta))
    z = [v / length for v in delta]
    aa = [a[i] + z[i] * start for i in range(3)]
    bb = [b[i] - z[i] * end for i in range(3)]
    length -= start + end
    mid = [(aa[i] + bb[i]) / 2 for i in range(3)]
    body_start = len(BODIES)
    loft(name, [(-length/2, f'{wa*.9}*{scale}', f'{da*.9}*{scale}', 6, wa*.9),
                (-length*.25, f'{wa}*{scale}', f'{da}*{scale}', 8, wa),
                (length*.30, f'{wb}*{scale}', f'{db}*{scale}', 8, wb),
                (length/2, f'{wb*.86}*{scale}', f'{db*.9}*{scale}', 6, wb*.86)], wall='limb_wall')
    return body_start, mid, z, length


def link_pose(start, mid, z):
    # Same basis as the Rev D Blender builder: project +Y onto the normal plane.
    y = [-z[0]*z[1], 1-z[1]*z[1], -z[2]*z[1]]
    yn = math.sqrt(sum(v*v for v in y))
    y = [v/yn for v in y]
    x = [y[1]*z[2]-y[2]*z[1], y[2]*z[0]-y[0]*z[2], y[0]*z[1]-y[1]*z[0]]
    angle = math.acos(max(-1, min(1, (x[0]+y[1]+z[2]-1)/2)))
    axis = [y[2]-z[1], z[0]-x[2], x[1]-y[0]]
    n = math.sqrt(sum(v*v for v in axis))
    if n < 1e-9:
        axis = [1, 0, 0]
    else:
        axis = [v/n for v in axis]
    move(BODIES[start:], mid, axis, f'{math.degrees(angle)} deg')


def build():
    cmd('file.new',name='Percival Rev D - Parametric CAD')
    for name, value, comment in [
        ('head_w','234 mm','Maximum head shell width'),
        ('head_h','112 mm','Maximum head shell height'),
        ('head_depth','124 mm','Fore-aft head envelope'),
        ('head_wall','2.6 mm','Nominal transverse wall; verify minimum after printing'),
        ('head_z','438 mm','Head pose origin height'),
        ('head_roll','6 deg','Expressive Rev D tilt'),
        ('head_pitch','-3 deg','Rev D pitch'),
        ('head_yaw','-5 deg','Rev D yaw'),
        ('torso_w','120 mm','Torso maximum width'),
        ('torso_d','96 mm','Torso maximum depth'),
        ('torso_h','98 mm','Torso height'),
        ('body_wall','3 mm','Nominal torso/pelvis transverse wall'),
        ('limb_wall','2.8 mm','Nominal hollow armor wall'),
        ('limb_scale','1','Armor width/depth multiplier; unitless'),
        ('sole_w','88 mm','Boot sole maximum width'),
        ('sole_d','134 mm','Boot sole length'),
        ('panel_t','2.5 mm','Removable armor plate thickness'),
        ('m3_clearance','3.4 mm','Prototype M3 clearance bore')]:
        cmd('parameters.add', name=name, expression=value, comment=comment,
            unit='' if name=='limb_scale' else ('deg' if 'deg' in value else 'mm'))
    stage('00_parameters')

    component('01 Head enclosure and optics')
    loft('H01 hollow head shell', [
        ('-head_depth/2+6','head_w-10','head_h-4',24,224),
        ('-head_depth/2+17','head_w','head_h',25,234),
        ('head_depth/2-24','head_w-8','head_h-2',25,226),
        ('head_depth/2','head_w-34','head_h-18',23,200)],
        axis='Y', wall='head_wall')
    # Broad separate face frame, with a through opening and screw clearances.
    sk='H02 bezel section'
    sketch(sk,(0,'-head_depth/2+6',0),'Y')
    draw_loop(octagon('head_w-10','head_h-4',24))
    draw_loop(octagon('head_w-48','head_h-36',13),9)
    cmd('sketch.finish')
    cmd('solid.extrude', distance='3 mm', profiles=[dict(point=[105,0])],
        operation='new', name='H02 bezel wall', body_name='H02 face frame')
    register('H02 face frame','ivory',True)
    panel('H03 rear service lid','head_w-34','head_h-18',3,(0,'head_depth/2+3',0),23)
    panel('H04 black faceplate','head_w-48.6','head_h-36.6',3,
          (0,'-head_depth/2+4.3',0),12.7,'dark')
    for side in [-1,1]:
        for z in [-39,39]:
            x=f'{side}*(head_w/2-23)'
            cyl(f'H02 M3 clearance {side} {z}','m3_clearance/2',8,(x,-58,z),axis='Y',cut='H02 face frame')
            screw(f'Head frame fixing {side} {z}',(x,-60.2,z))
    for x,z,r,label in [(-53,3,25,'left large eye'),(54,0,18.5,'right small eye')]:
        for suffix,rad,depth,y,color in [('housing',r,3.5,-61,'dark'),
            ('aperture',r-3,4,-63,'rubber'),('alloy rim',r-6,4.5,-64,'steel'),
            ('barrel',r-7,6,-65,'dark'),('lens',r-10,6.5,-66,'glass')]:
            cyl(label+' '+suffix,rad,depth,(x,y,z),color,'Y')
    panel('central sensor bezel',40,17,2.3,(0,-60,-12),7,'dark',printable=False)
    for x in [-12,12]:
        cyl(f'sensor {x} rim',4.3,3,(x,-63,-12),'steel','Y')
        cyl(f'sensor {x} optic',3.2,4,(x,-64,-12),'glass','Y')
    cyl('blue head status',2,2,(-7,-62,24),'cyan','Y')
    for x in [5,15]: cyl(f'microphone {x}',1.2,2,(x,-61.5,24),'dark','Y')
    for x in [-82,82]:
        for z in [-26,26]: screw(f'Faceplate fixing {x} {z}',(x,-61.2,z))
    for side in [-1,1]:
        cyl(f'ear {side} purple pod',34,12,(f'{side}*(head_w/2-1)',4,0),'purple')
        cyl(f'ear {side} black ring',28,14,(f'{side}*(head_w/2+2)',4,0))
        cyl(f'ear {side} cover',23,15,(f'{side}*(head_w/2+3)',4,0),'rubber')
        fin_start=len(BODIES)
        cyl(f'ear {side} hinge',8,18,(0,0,0))
        panel(f'H05 ear fin {side}',22,47,9,(0,5.5,24),7)
        panel(f'ear {side} fin inset',14,38,2,(0,-4,25),5,'dark',printable=False)
        panel(f'ear {side} orange strip',4,29,2,(side*8,-5,25),1.5,'orange',printable=False)
        move(BODIES[fin_start:],(f'{side}*(head_w/2-15)',3,46),(0,1,0),f'{side*(11 if side<0 else 15)} deg')
    panel('H06 crown hatch',55,32,'panel_t',(0,-26,'head_h/2+1'),5,'purple','Z')
    for x in [-20,20]:
        for y in [-36,-16]: screw(f'Crown fixing {x} {y}',(x,y,'head_h/2+4'),'Z')
    cyl('crown auxiliary turret',9,8,(-54,13,'head_h/2+2'),'dark','Z')
    cyl('antenna base',5,7,(64,18,'head_h/2+2'),'dark','Z')
    cyl('antenna lower',2.6,20,(64,18,'head_h/2+14'),'rubber','Z')
    cyl('antenna whip',1.8,41,(64,18,'head_h/2+41'),'dark','Z')
    head_names=list(GROUP)
    move(head_names,axis=(1,0,0),angle='head_pitch')
    move(head_names,axis=(0,1,0),angle='head_roll')
    move(head_names,(0,-9,'head_z'),axis=(0,0,1),angle='head_yaw')
    stage('01_head')

    component('02 Compact torso pelvis and backpack')
    loft('T01 hollow torso',[('-torso_h/2','torso_w-34','torso_d-34',12,86),
        ('-torso_h/2+13','torso_w-7','torso_d-10',13,113),
        ('torso_h/2-27','torso_w','torso_d',16,120),
        ('torso_h/2-7','torso_w-12','torso_d-15',14,108),
        ('torso_h/2','torso_w-35','torso_d-30',12,85)],(0,7,306),wall='body_wall')
    cheek=[(22,40),(42,42),(56,26),(53,-28),(35,-43),(23,-38)]
    for side in [-1,1]:
        poly(f'T02 chest cheek {side}',[(side*x,z) for x,z in cheek],2.5,(0,-44,306),printable=True)
        for x,z in [(side*36,34),(side*45,-25),(side*29,-34)]:
            screw(f'Chest cheek screw {x} {z}',(x,-47.2,306+z))
    spine=[(-19,39),(19,39),(16,7),(15,-40),(9,-44),(-9,-44),(-15,-40),(-16,7)]
    poly('T03 purple service spine',spine,'panel_t',(0,-42.5,306),'purple',printable=True)
    for x in [-12,12]:
        for z in [338,273]: screw(f'Chest spine screw {x} {z}',(x,-46,z))
    panel('chest status rim',18,5.5,2,(35,-47,325),2,'dark',printable=False)
    panel('chest status light',14,2.6,2,(35,-49,325),1,'cyan',printable=False)
    for row in range(5):
        for col in range(4):
            x=29+col*4.5+(row%2)*2.1
            if x<47: cyl(f'Chest vent {row}-{col}',1.1,5,(x,-45,299+row*4.8),axis='Y',cut='T02 chest cheek 1')
    loft('T04 hollow pelvic pod',[(-29,54,52,10,54),(-18,72,70,12,72),
        (20,76,70,13,76),(29,58,54,10,58)],(0,8,215),wall='body_wall')
    panel('T05 pelvis access hatch',47,42,2.5,(0,-29,215),7)
    for x in [-17,17]:
        for z in [202,230]: screw(f'Pelvis screw {x} {z}',(x,-32,z))
    cyl('Waist yaw envelope',29,15,(0,7,248),axis='Z')
    cyl('Waist alloy trim',25,3,(0,7,240),'steel','Z')
    box('Waist gimbal envelope',(64,48,20),(0,7,243))
    loft('T06 hollow battery backpack',[(-42.5,72,37,6,72),(-34.5,80,45,8,80),
        (34.5,80,45,8,80),(42.5,72,37,6,72)],(0,73,307),wall='body_wall',color='dark')
    panel('T07 rear backpack hatch',65,68,3,(0,98,307),8,'dark')
    for x in [-24,24]:
        for z in [283,331]: screw(f'Backpack screw {x} {z}',(x,99,z))
    for x in [-22,22]: box(f'Handle upright {x}',(6,7,12),(x,74,356),'orange')
    box('Orange carrying handle',(50,7,6),(0,74,361),'orange')
    cyl('Neck yaw envelope',24,16,(0,7,365),axis='Z')
    cyl('Neck lower trim',21,3,(0,7,374),'steel','Z')
    box('Neck pitch fork envelope',(46,34,20),(0,6,381))
    cyl('Neck pitch axle',12,58,(0,6,382))
    for side in [-1,1]: cyl(f'Neck rim {side}',8,3,(side*30,6,382),'steel')
    stage('02_torso')

    for side,label,foot_y,knee_y,knee_z in [(1,'L',-18,-27,132),(-1,'R',-3,-17,138)]:
        component(f'03 {label} leg and boot')
        hip=(side*60,8,216); knee=(side*70,knee_y,knee_z); ankle=(side*73,foot_y+18,56)
        joint(label+' hip',hip,31,side,34,'steel')
        joint(label+' knee',knee,28,side,35)
        joint(label+' ankle',ankle,20,side,29,'dark')
        start,mid,z,length=link(label+'01 hollow thigh',hip,knee,61,56,59,55,15,10)
        panel(label+'02 thigh panel',48,50,2.2,(0,-30,0),8)
        for x in [-16,16]:
            for dz in [-18,18]: screw(label+f' thigh screw {x} {dz}',(x,-33,dz))
        link_pose(start,mid,z)
        poly(label+'03 purple kneecap',[(-17,18),(17,18),(20,9),(15,-21),(8,-27),(-8,-27),(-16,-20),(-20,9)],
             2.6,(knee[0],knee[1]-27,knee[2]),'purple',printable=True)
        for x in [-12,12]:
            for dz in [-16,11]: screw(label+f' knee panel screw {x} {dz}',(knee[0]+x,knee[1]-30,knee[2]+dz))
        start,mid,z,length=link(label+'04 hollow shin',knee,ankle,52,45,47,42,17,8)
        panel(label+' shin mechanism recess',26,39,2,(0,-24,0),4,'dark',printable=False)
        for x in [-19,19]:
            panel(label+f'05 shin rail {x}',9,42,2,(x,-24,0),3)
            for dz in [-13,13]: screw(label+f' shin rail screw {x} {dz}',(x,-27,dz))
        link_pose(start,mid,z)
        start=len(BODIES)
        loft(label+'06 rubber sole',[(0,'sole_w-1','sole_d',14,87),(5,'sole_w','sole_d',14,88),
             (9,'sole_w-2','sole_d-2',13,86)],color='rubber')
        panel(label+' boot midsole gasket',81,122,8,(0,0,7),3,'rubber','Z')
        loft(label+'07 hollow boot',[(-62,61,17,7,61,23.5),(-40,85,31,9,85,30.5),
             (-3,83,40,10,83,35),(29,72,39,9,72,34.5),(56,55,19,7,55,24.5)],
             axis='Y',wall='limb_wall')
        panel(label+' boot toe cap',61,17,2.5,(0,-62,23.5),7)
        panel(label+' boot heel cap',55,19,2.5,(0,58.5,24.5),7)
        hatch_start=len(BODIES)
        panel(label+'08 purple instep hatch',41,39,2,(0,1,0),5,'purple')
        move(BODIES[hatch_start:],(0,-22,50),(1,0,0),'97 deg')
        for x in [-14,14]:
            for y in [-35,-9]:
                screw(label+f' boot hatch screw {x} {y}',(x,y,50.5+(y+22)*.12),'Z')
        panel(label+' toe bumper',62,9,4,(0,-64,11),4,'rubber',printable=False)
        box(label+' orange heel latch',(47,8,8),(0,43,36),'orange')
        move(BODIES[start:],(side*73,foot_y,0),angle=f'{-side*6} deg')
        stage('03_leg_'+label)

    for label,side,shoulder,elbow,wrist,hand in [
        ('L',1,(80,5,334),(111,-2,280),(132,-20,226),(134,-25,210)),
        ('R',-1,(-80,5,334),(-120,-7,300),(-151,-25,351),(-155,-29,367))]:
        component(f'04 {label} expressive arm')
        joint(label+' shoulder',shoulder,23,side,27)
        joint(label+' elbow',elbow,14,side,24,'dark')
        for tag,a,b,wa,wb,da,db,aoff,boff,depth in [
            ('upper arm',shoulder,elbow,35,31,36,31,18,10,18),
            ('forearm',elbow,wrist,33,29,34,29,9,7,17)]:
            start,mid,z,length=link(label+' hollow '+tag,a,b,wa,wb,da,db,aoff,boff)
            panel(label+' '+tag+' faceplate',20.5,28,2,(0,-depth-1.4,0),3.5)
            for dz in [-9,9]: screw(label+f' {tag} screw {dz}',(0,-depth-4,dz))
            if tag=='forearm': box(label+' forearm orange control',(7,4,19),(12,-16,0),'orange')
            link_pose(start,mid,z)
        cyl(label+' wrist joint',10,17,wrist)
        start=len(BODIES)
        panel(label+' palm mechanism',26,20,20,(0,10,14),4,'dark',printable=False)
        panel(label+' palm armor',24,21,3,(0,-10.8,14),5)
        for x in [-8,8]:
            screw(label+f' palm screw {x}',(x,-14,14))
            panel(label+f' small claw {x}',10,24,16,(x,5,36),3,'rubber',printable=True)
        delta=[hand[i]-wrist[i] for i in range(3)]
        n=math.sqrt(sum(v*v for v in delta))
        link_pose(start,wrist,[v/n for v in delta])
        stage('04_arm_'+label)

    component('05 Purchased size envelopes - unverified integration')
    for name,dims,loc in [
        ('J401 PCB envelope',(100,80,1.6),(0,7,292)),
        ('J401 cooling allowance',(100,80,35),(0,7,312)),
        ('4S battery nominal envelope',(76,38,47),(0,73,307)),
        ('XM430 L hip envelope',(28.5,34,46.5),(60,8,216)),
        ('XM430 R hip envelope',(28.5,34,46.5),(-60,8,216)),
        ('XM430 L knee envelope',(28.5,34,46.5),(70,-27,132)),
        ('XM430 R knee envelope',(28.5,34,46.5),(-70,-17,138))]: box(name,dims,loc,'pcb')
    hidden=list(GROUP)
    camera_start=len(BODIES)
    for x in [-53,54]: box(f'Camera {x} PCB envelope',(38,1.6,38),(x,-32,0),'pcb')
    cameras=BODIES[camera_start:]
    move(cameras,axis=(1,0,0),angle='head_pitch')
    move(cameras,axis=(0,1,0),angle='head_roll')
    move(cameras,(0,-9,'head_z'),axis=(0,0,1),angle='head_yaw')
    hidden+=cameras
    cmd('component.activate',component='root')
    for color,names in COLORS.items():
        cmd('appearance.assign',bodies=names,color=PALETTE[color],
            pbr=dict(metallic=.7 if color=='steel' else .1,
                     roughness=.15 if color=='glass' else .45,dielectric_ior=1.45))
    flexible=[name for name in PRINT_PARTS if name in COLORS['rubber']]
    rigid=[name for name in PRINT_PARTS if name not in flexible]
    cmd('material.assign',bodies=rigid,material='ABS Plastic')
    cmd('material.create',name='TPU nominal - grade unselected',density_g_cm3=1.21)
    cmd('material.assign',bodies=flexible,material='TPU nominal - grade unselected')
    cmd('browser.visibility',items=hidden,visible=False)
    cmd('browser.visibility',folder='sketches',visible=False)
    cmd('browser.visibility',folder='origin',visible=False)
    cmd('view.apply',camera=dict(target=[0,0,273],yaw=-.42,pitch=.12,distance=875))
    stage('05_appearance_and_envelopes')
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'stages.json').write_text(json.dumps(STAGES,indent=2)+'\n')
    (OUT/'build.json').write_text(json.dumps(dict(commands=[c for s in STAGES for c in s['commands']]),indent=2)+'\n')
    (OUT/'parts.json').write_text(json.dumps(dict(bodies=BODIES,print_candidates=PRINT_PARTS,
        hidden_envelopes=hidden,colors=COLORS,status='CAD concept; not a manufacturing release'),indent=2)+'\n')
    print(json.dumps(dict(stages=len(STAGES),commands=sum(len(s['commands']) for s in STAGES),
                          bodies=len(BODIES),print_candidates=len(PRINT_PARTS))))


if __name__=='__main__':
    build()
