"""Blender MCP: inspect custom solids, export mm STL/3MF, check static intersections.

These checks do not validate print strength, motion, fits, optics or walking.
Only custom skins are exported; OEM visual meshes are never printable exports.
"""
import bpy
import bmesh
import json
import math
import struct
import zipfile
import hashlib
import xml.etree.ElementTree as ET
from pathlib import Path
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'print_prototypes'; OUT.mkdir(exist_ok=True)
scene=bpy.context.scene; bpy.context.view_layer.update()
parts=list(bpy.data.collections['03 • PERCIVAL PRINTS — Rev A fit prototypes'].objects)
hardware=list(bpy.data.collections['01 • REAL HARDWARE — ToddlerBot 2XC reference, DO NOT PRINT'].objects)

def components(mesh):
    adj=[[] for _ in mesh.vertices]
    for e in mesh.edges:
        a,b=e.vertices; adj[a].append(b); adj[b].append(a)
    seen=set(); groups=0
    for i in range(len(adj)):
        if i in seen: continue
        groups+=1; stack=[i]; seen.add(i)
        while stack:
            for j in adj[stack.pop()]:
                if j not in seen: seen.add(j); stack.append(j)
    return groups

def world_vertices(ob): return [ob.matrix_world@v.co for v in ob.data.vertices]
def bbox(vs):
    return ([min(v[i] for v in vs) for i in range(3)], [max(v[i] for v in vs) for i in range(3)])
def centroid_volume(vs,triangles):
    vol=0.; centroid=Vector((0,0,0))
    for tri in triangles:
        a,b,c=[vs[i] for i in tri]; v=a.dot(b.cross(c))/6
        vol+=v; centroid+=(a+b+c)*(v/4)
    return abs(vol),centroid/vol if abs(vol)>1e-15 else Vector((0,0,0))

def stl(path,vs,triangles):
    with path.open('wb') as f:
        f.write(b'PERCIVAL Rev A FIT PROTOTYPE | units: mm'.ljust(80,b' '))
        f.write(struct.pack('<I',len(triangles)))
        for tri in triangles:
            a,b,c=[vs[i] for i in tri]; normal=(b-a).cross(c-a).normalized()
            f.write(struct.pack('<12fH',*normal,*a,*b,*c,0))

def three_mf(path,vs,triangles,name):
    ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
    ET.register_namespace('',ns)
    model=ET.Element('{'+ns+'}model',unit='millimeter',attrib={'xml:lang':'en-US'})
    resources=ET.SubElement(model,'resources'); ob=ET.SubElement(resources,'object',id='1',type='model',name=name)
    mesh=ET.SubElement(ob,'mesh'); vertices=ET.SubElement(mesh,'vertices')
    for v in vs: ET.SubElement(vertices,'vertex',x=f'{v.x:.6f}',y=f'{v.y:.6f}',z=f'{v.z:.6f}')
    tris=ET.SubElement(mesh,'triangles')
    for a,b,c in triangles: ET.SubElement(tris,'triangle',v1=str(a),v2=str(b),v3=str(c))
    build=ET.SubElement(model,'build'); ET.SubElement(build,'item',objectid='1')
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml','<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr('_rels/.rels','<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        z.writestr('3D/3dmodel.model',ET.tostring(model,encoding='utf-8',xml_declaration=True))

results=[]; geometries={}; total_mass=0.; moment=Vector((0,0,0)); all_v=[]
for ob in sorted(parts,key=lambda ob:ob['part_id']):
    mesh=ob.data; mesh.calc_loop_triangles(); triangles=[tuple(t.vertices) for t in mesh.loop_triangles]
    bm=bmesh.new(); bm.from_mesh(mesh)
    nm=sum(not e.is_manifold for e in bm.edges); boundary=sum(e.is_boundary for e in bm.edges)
    loose=sum(not v.link_faces for v in bm.verts); zero=sum(f.calc_area()<1e-14 for f in bm.faces)
    signed=bm.calc_volume(signed=True); bm.free()
    ncomp=components(mesh); vs=world_vertices(ob); all_v+=vs
    volume,centroid=centroid_volume(vs,triangles)
    density=1.20 if ob['print_material'].startswith('TPU') else 1.27
    mass=volume*1e9/1000*density
    total_mass+=mass; moment+=centroid*mass
    pid=ob['part_id']
    if pid=='P02': rotation=Matrix.Rotation(-math.pi/2,3,'X')
    elif pid.startswith('P05'): rotation=Matrix.Rotation(math.pi/2,3,'Y')
    elif pid=='P08': rotation=Matrix.Identity(3)
    else: rotation=Matrix.Rotation(math.pi/2,3,'X')
    vprint=[rotation@v*1000 for v in vs]; lo,hi=bbox(vprint)
    offset=Vector(((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,lo[2]))
    vprint=[v-offset for v in vprint]; dims=[hi[i]-lo[i] for i in range(3)]
    ok=(nm==0 and boundary==0 and loose==0 and zero==0 and ncomp==1 and signed>0 and max(dims)<=256)
    rec={'part_id':pid,'name':ob.name,'material':ob['print_material'],'quantity':1,
         'nonmanifold_edges':nm,'boundary_edges':boundary,'loose_vertices':loose,'degenerate_faces':zero,
         'connected_components':ncomp,'signed_volume_positive':signed>0,'triangles':len(triangles),
         'print_bounds_mm':[round(d,3) for d in dims],
         'fits_A1_with_4mm_brim':dims[0]+8<=256 and dims[1]+8<=256 and dims[2]<=256,
         'fits_Prusa_XL':max(dims)<=360,'material_volume_cm3':round(volume*1e6,3),
         'estimated_mass_g':round(mass,2),'centroid_mm':[round(x*1000,3) for x in centroid],
         'mesh_checks_pass':ok,'physical_release':'FIT PROTOTYPE; NOT WALKING VALIDATED','notes':ob['notes']}
    if ok:
        path=OUT/(pid+'.stl'); stl(path,vprint,triangles); three_mf(OUT/(pid+'.3mf'),vprint,triangles,ob.name)
        rec['stl_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    results.append(rec); geometries[ob.name]=(vs,[tuple(p.vertices) for p in mesh.polygons])

# Static surface intersection check. Exact mating faces may touch; no continuous sweep is claimed.
trees={}; boxes={}
for ob in parts+hardware:
    if ob.type!='MESH': continue
    vs=world_vertices(ob); polys=[tuple(p.vertices) for p in ob.data.polygons]
    boxes[ob.name]=bbox(vs); trees[ob.name]=BVHTree.FromPolygons(vs,polys,all_triangles=False,epsilon=0)
def overlaps_box(a,b):
    return all(a[0][i]<b[1][i]-1e-7 and b[0][i]<a[1][i]-1e-7 for i in range(3))
collisions=[]
for a in parts:
    for b in hardware:
        if overlaps_box(boxes[a.name],boxes[b.name]) and trees[a.name].overlap(trees[b.name]):
            collisions.append({'print':a['part_id'],'reference':b.name,'status':'INTERFERENCE TO REVIEW'})
print_contacts=[]
for i,a in enumerate(parts):
    for b in parts[i+1:]:
        if overlaps_box(boxes[a.name],boxes[b.name]) and trees[a.name].overlap(trees[b.name]):
            print_contacts.append([a['part_id'],b['part_id']])
source_mass=0.; source_moment=Vector((0,0,0))
for ob in bpy.data.collections['02 • URDF LINK FRAMES — reference zero pose'].objects:
    if 'source_mass_kg' not in ob: continue
    m=ob['source_mass_kg']; source_mass+=m
    source_moment+=(ob.matrix_world@Vector(ob['source_com_m']))*m
source_com=source_moment/source_mass
total_com=(source_moment+moment/1000)/(source_mass+total_mass/1000)
for ob in hardware: all_v+=world_vertices(ob)
lo,hi=bbox(all_v)
report={'checks_scope':'Custom mesh topology/print envelope and neutral-pose surface intersections only. No motion/load/thermal/optical/physical-fit validation.',
        'height_neutral_mm':round((hi[2]-lo[2])*1000,3),'height_under_600mm':(hi[2]-lo[2])<=.6,
        'assembly_bounds_mm':[[round(x*1000,3) for x in lo],[round(x*1000,3) for x in hi]],
        'custom_parts':len(parts),'mesh_passes':sum(x['mesh_checks_pass'] for x in results),
        'custom_solid_material_estimate_g':round(total_mass,2),'source_URDF_mass_kg':round(source_mass,6),
        'source_com_mm':[round(x*1000,3) for x in source_com],
        'source_plus_shell_com_mm':[round(x*1000,3) for x in total_com],
        'mass_assumptions':'PETG1.27g/cm3,TPU1.20. Solid modeled geometry; excludes added fasteners/adhesives. Retains stock head mass conservatively; camera relocation/removed OEM skins not subtracted. Not measured.',
        'hardware_intersections':collisions,'print_pair_surface_contacts':print_contacts,'parts':results}
(ROOT/'evidence'/'geometry-verification.json').write_text(json.dumps(report,indent=2)+'\n')
(OUT/'parts-manifest.json').write_text(json.dumps(results,indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'design'/'percival.blend'))
result={k:v for k,v in report.items() if k not in ('parts','checks_scope','mass_assumptions')}
result['failed_parts']=[p['part_id'] for p in results if not p['mesh_checks_pass']]
