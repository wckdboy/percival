"""Reopen and measure Rev D; no printability, mechanism or walking claims."""
import bpy
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
report = json.loads((ROOT / 'evidence/rev-d-layout.json').read_text())
scene = bpy.data.scenes['Percival • Rev D / reference proportions']
bpy.context.window.scene = scene
assert scene['revision'] == 'D'
assert scene.unit_settings.system == 'METRIC' and scene.unit_settings.scale_length == 1
assert scene.frame_start == 1 and scene.frame_end == 73 and scene.render.fps == 24
assert not any('part_id' in o for o in scene.objects), 'No print-release identifiers'

for path, expected in [
    (ROOT / 'design/percival.blend', report['source_rev_a_sha256']),
    (ROOT / 'design/percival-rev-b-bdx.blend', report['source_rev_b_sha256']),
    (ROOT / 'design/percival-rev-c-chamfer.blend', report['source_rev_c_sha256']),
    (ROOT / 'design' / Path(report['approved_rev_c_checkpoint']).name, report['approved_rev_c_sha256']),
]:
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, f'Preserved file changed: {path}'

servos = [o for o in scene.objects if 'manufacturer_envelope_mm' in o]
assert len(servos) == 4
for o in servos:
    assert all(abs(a-b) < .01 for a, b in zip(sorted(v*1000 for v in o.dimensions), [28.5, 34, 46.5]))
    assert all(abs(v-1) < 1e-6 for v in o.scale)
body = scene.objects['D • tapered torso enclosure']
assert 118 < body.dimensions.x*1000 < 121
assert 97 < body.dimensions.z*1000 < 99
head = scene.objects['D • sculpted deep head shell']
visor = scene.objects['D • recessed black face']
assert .78 < visor.dimensions.x / head.dimensions.x < .84
for label in ['L', 'R']:
    joint = scene.objects[f'D • {label} hip central actuator case']
    assert abs(joint.location.z*1000 - 216) < .01
assert 'D • separate pelvic pod' in scene.objects

collections = [c for c in scene.collection.children if c.name.startswith(('D01', 'D02', 'D03'))]
assert len(collections) == 3
objects = [o for c in collections for o in c.objects if o.type in {'MESH', 'CURVE', 'FONT'} and not o.hide_render]
# Independently measure evaluated geometry from the saved file at every gesture frame.
heights = []
for frame in range(1, 74):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    lo, hi = float('inf'), float('-inf')
    for ob in objects:
        eo = ob.evaluated_get(dg)
        mesh = eo.to_mesh()
        for vertex in mesh.vertices:
            co = eo.matrix_world @ vertex.co
            assert all(math.isfinite(v) for v in co)
            lo, hi = min(lo, co.z), max(hi, co.z)
        eo.to_mesh_clear()
    assert abs(lo) < .0001
    heights.append((hi-lo)*1000)
assert 535 < heights[0] < 565
assert max(heights) < 575
assert .36 < 216/heights[0] < .42
assert abs(heights[0]-report['posed_height_mm']) < .05
assert abs(max(heights)-report['max_idle_gesture_height_mm']) < .05
scene.frame_set(1)
for view in ['hero', 'front', 'side', 'top', 'head']:
    assert (ROOT / f'renders/rev-d/percival-rev-d-{view}.png').stat().st_size > 10000
result = {
    'status': 'PASS',
    'scene': scene.name,
    'saved_file': bpy.data.filepath,
    'rev_a_b_c_and_approved_checkpoint_unchanged': True,
    'independently_measured_height_mm': round(heights[0], 2),
    'max_illustrated_gesture_height_mm': round(max(heights), 2),
    'hip_height_fraction': round(216/heights[0], 3),
    'full_size_servo_envelopes': len(servos),
    'reference_status': 'Visual approximation of supplied images; not measured drawings',
    'unverified': ['physical fit', 'printable wall construction', 'fastener mounting', 'torque', 'full-motion interference', 'balance', 'walking'],
}
