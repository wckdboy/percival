"""Independent standard-library checks of exported STL/3MF and source hashes."""
import collections
import hashlib
import json
import math
import struct
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'print_prototypes/parts-manifest.json').read_text())
geometry=json.loads((ROOT/'evidence/geometry-verification.json').read_text())
failures=[]; checked=[]
for p in manifest:
    pid=p['part_id']; path=ROOT/'print_prototypes'/f'{pid}.stl'
    if not path.exists(): failures.append(f'{pid}: missing STL'); continue
    data=path.read_bytes(); count=struct.unpack_from('<I',data,80)[0]
    if len(data)!=84+50*count: failures.append(f'{pid}: STL length')
    edges=collections.Counter(); directions=collections.Counter(); coords=[]
    for n in range(count):
        values=struct.unpack_from('<12fH',data,84+50*n)
        tri=[tuple(values[i:i+3]) for i in (3,6,9)]; coords+=tri
        if not all(math.isfinite(v) for t in tri for v in t): failures.append(f'{pid}: nonfinite vertex')
        for a,b in zip(tri,tri[1:]+tri[:1]):
            edge=tuple(sorted((a,b))); edges[edge]+=1; directions[edge]+=1 if a<b else -1
    if any(n!=2 for n in edges.values()): failures.append(f'{pid}: STL boundary/nonmanifold edges')
    if any(n!=0 for n in directions.values()): failures.append(f'{pid}: inconsistent STL winding')
    lo=[min(v[i] for v in coords) for i in range(3)];hi=[max(v[i] for v in coords) for i in range(3)]
    dims=[hi[i]-lo[i] for i in range(3)]
    if abs(lo[2])>1e-4 or max(dims)>256.001: failures.append(f'{pid}: bed placement or A1 bounds')
    if any(abs(a-b)>.002 for a,b in zip(dims,p['print_bounds_mm'])): failures.append(f'{pid}: units/extent mismatch')
    if hashlib.sha256(data).hexdigest()!=p['stl_sha256']: failures.append(f'{pid}: STL hash')
    with zipfile.ZipFile(path.with_suffix('.3mf')) as z:
        if z.testzip(): failures.append(f'{pid}: 3MF CRC')
        model=ET.fromstring(z.read('3D/3dmodel.model'))
        if model.get('unit')!='millimeter': failures.append(f'{pid}: 3MF unit')
        triangles=model.findall('.//{*}triangle')
        if len(triangles)!=count: failures.append(f'{pid}: 3MF triangle count')
        vertices=model.findall('.//{*}vertex')
        if any(int(t.get(k))>=len(vertices) for t in triangles for k in ['v1','v2','v3']): failures.append(f'{pid}: 3MF indices')
    checked.append(pid)
source=json.loads((ROOT/'reference/toddlerbot/SOURCE_MANIFEST.json').read_text())
for entry in source['files']:
    if hashlib.sha256((ROOT/entry['path']).read_bytes()).hexdigest()!=entry['sha256']:
        failures.append('source hash: '+entry['path'])
if not geometry['height_under_600mm']:failures.append('height limit')
if geometry['mesh_passes']!=geometry['custom_parts']:failures.append('Blender geometry gate')
if geometry['hardware_intersections']:failures.append('neutral-pose hardware surface intersection')
if geometry['print_pair_surface_contacts']:failures.append('custom part surface intersections')
result={'status':'PASS' if not failures else 'FAIL','stl_and_3mf_pairs_checked':len(checked),
        'source_hashes_checked':len(source['files']),'failures':failures,
        'unverified':['slicer toolpaths','minimum wall thickness across entire surface','continuous motion and containment collisions','physical assembly/retention','wiring and power','structural loads and thermal duty','walking']}
(ROOT/'evidence/artifact-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
raise SystemExit(bool(failures))
