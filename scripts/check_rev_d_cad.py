#!/usr/bin/env python3
"""Check exported prototype mesh topology, bounds, hashes and native CAD evidence.

This deliberately does not claim slicer readiness, fastening, strength or walking.
Uses the standard library so verification works without a CAD installation.
"""
import collections
import hashlib
import json
import math
import struct
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CAD=ROOT/'cad'/'rev-d'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def payload(item):
    return json.loads(next(c['text'] for c in item['result']['content'] if c['type']=='text'))


def check_mesh(path):
    data=path.read_bytes()
    count=struct.unpack_from('<I',data,80)[0]
    if len(data)!=84+50*count:
        raise ValueError(f'Invalid binary STL length: {path.name}')
    edges=collections.Counter()
    directed=collections.Counter()
    bounds=[[float('inf')]*3,[float('-inf')]*3]
    volume=0.0
    degenerates=0
    origin=None
    for i in range(count):
        row=struct.unpack_from('<12fH',data,84+i*50)
        vertices=[tuple(row[j:j+3]) for j in [3,6,9]]
        if not all(math.isfinite(v) for p in vertices for v in p):
            raise ValueError(f'Nonfinite STL coordinate: {path.name}')
        origin=origin or vertices[0]
        for p in vertices:
            for j in range(3):
                bounds[0][j]=min(bounds[0][j],p[j])
                bounds[1][j]=max(bounds[1][j],p[j])
        # STL repeats vertices per triangle; weld only to 0.00001 mm.
        keys=[tuple(round(v,5) for v in p) for p in vertices]
        if len(set(keys))<3:
            degenerates+=1
        for a,b in zip(keys,keys[1:]+keys[:1]):
            edges[tuple(sorted([a,b]))]+=1
            directed[(a,b)]+=1
        a,b,c=[[p[j]-origin[j] for j in range(3)] for p in vertices]
        volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
    bad_edges=sum(n!=2 for n in edges.values())
    winding=sum(directed[(a,b)]!=directed[(b,a)] for a,b in edges)
    dims=[bounds[1][j]-bounds[0][j] for j in range(3)]
    return dict(triangles=count,bounds_mm=bounds,dimensions_mm=dims,
                signed_volume_mm3=volume,nonmanifold_edges=bad_edges,
                inconsistent_edge_winding=winding,degenerate_triangles=degenerates,
                watertight=bad_edges==0 and winding==0 and degenerates==0 and volume>0,
                fits_256_mm_cube_bounds=all(d<=256 for d in dims),sha256=sha(path))


def main():
    manifest=json.loads((CAD/'prototype-parts.json').read_text())
    native=json.loads((CAD/'export-mcp.json').read_text())
    quality=payload(native[0]);design=payload(native[1]);measure=payload(native[2])
    failures=[]
    parameters=json.loads((CAD/'evidence'/'parameter-checks.json').read_text())
    step=json.loads((CAD/'evidence'/'step-roundtrip.json').read_text())
    if parameters['provenance']['source_sha256']!=sha(CAD/'percival-rev-d.polykrom'):
        failures.append('Parameter checks refer to a different native artifact')
    if not all(row['pass'] for row in parameters['checks']):
        failures.append('Parameter geometry assertion failed')
    for file,expected in step['input_sha256'].items():
        if sha(CAD/file)!=expected: failures.append('STEP evidence hash mismatch: '+file)
    if quality.get('verdict')!='pass': failures.append('Native CAD quality did not pass')
    if any(s.get('error') for s in design['timeline']): failures.append('Native timeline errors')
    rows=[]
    volumes={b['name']:b['volume_mm3'] for b in measure['bodies']}
    for part in manifest['parts']:
        row=dict(part,**check_mesh(CAD/part['file']))
        row['native_volume_mm3']=volumes[part['body']]
        row['relative_volume_error']=abs(row['signed_volume_mm3']-row['native_volume_mm3'])/row['native_volume_mm3']
        if row['relative_volume_error']>0.002:
            failures.append(part['body']+': mesh volume differs from native by >0.2%')
        if not row['watertight']: failures.append(part['body']+': mesh topology failed')
        if not row['fits_256_mm_cube_bounds']: failures.append(part['body']+': bounds exceed 256 mm')
        rows.append(row)
    mins=[min(b['bbox']['min'][i] for b in measure['bodies']) for i in range(3)]
    maxs=[max(b['bbox']['max'][i] for b in measure['bodies']) for i in range(3)]
    dimensions=[maxs[i]-mins[i] for i in range(3)]
    if dimensions[2]>600: failures.append('Height exceeds 600 mm')
    report=dict(status='PASS' if not failures else 'FAIL',failures=failures,
        native_quality=quality,body_count=len(measure['bodies']),
        timeline_features=len(design['timeline']),overall_bounds_mm=[mins,maxs],
        overall_dimensions_mm=dimensions,prototype_mesh_count=len(rows),parts=rows,
        artifact_sha256={name:sha(CAD/name) for name in ['percival-rev-d.polykrom','percival-rev-d.step','build.json']},
        unverified=['minimum wall thickness across lofts','slicer toolpaths and supports',
            'mounts, threads, fastener engagement and retention','motor choice, torque and complete packaging',
            'assembly interferences and swept clearances','wiring, battery protection and thermal duty',
            'rigidity, structural loads, whole-robot mass and balance','walking and powered hardware'])
    (CAD/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['status','failures','body_count','timeline_features',
        'overall_dimensions_mm','prototype_mesh_count']},indent=2))
    raise SystemExit(bool(failures))


if __name__=='__main__':
    main()
