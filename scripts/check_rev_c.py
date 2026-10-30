"""Saved-file visual/layout checks; this is not manufacturing or gait validation."""
import bpy
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
report = json.loads((ROOT / 'evidence/rev-c-layout.json').read_text())
old = json.loads((ROOT / 'evidence/rev-b-layout.json').read_text())
scene = bpy.data.scenes['Percival • Rev C / compact industrial character']
bpy.context.window.scene = scene
assert scene['revision'] == 'C'
assert scene.unit_settings.system == 'METRIC' and scene.unit_settings.scale_length == 1
assert scene.frame_start == 1 and scene.frame_end == 73 and scene.render.fps == 24
assert not any('part_id' in o for o in scene.objects), 'No inherited print-release identifiers'

for path, expected in [
    (ROOT / 'design/percival.blend', report['source_rev_a_sha256']),
    (ROOT / 'design/percival-rev-b-bdx.blend', report['source_rev_b_sha256']),
    (ROOT / 'design' / Path(report['approved_rev_b_checkpoint']).name, report['approved_rev_b_sha256']),
]:
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, f'Preserved file changed: {path}'

servos = [o for o in scene.objects if 'manufacturer_envelope_mm' in o]
assert len(servos) == 4
for o in servos:
    assert all(abs(a-b) < .01 for a, b in zip(sorted(v*1000 for v in o.dimensions), [28.5, 34, 46.5]))
    assert all(abs(v-1) < 1e-6 for v in o.scale)
body = scene.objects['C • compact chamfered torso']
assert all(abs(a-b) < .1 for a, b in zip((v*1000 for v in body.dimensions), [136, 98, 62]))

collections = [c for c in scene.collection.children if c.name.startswith(('C01', 'C02', 'C03'))]
assert len(collections) == 3
objects = [o for c in collections for o in c.objects if o.type in {'MESH', 'CURVE', 'FONT'} and not o.hide_render]
assert len([o for o in objects if 'panel_type' in o]) >= 45
assert len([o for o in objects if 'socket screw' in o.name]) >= 90

# Re-measure the actual saved evaluated geometry, independent of the build report.
heights = []
for frame in range(1, 74):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    lo, hi = float('inf'), float('-inf')
    for ob in objects:
        eo = ob.evaluated_get(dg)
        mesh = eo.to_mesh()
        for v in mesh.vertices:
            co = eo.matrix_world @ v.co
            assert all(math.isfinite(value) for value in co)
            lo, hi = min(lo, co.z), max(hi, co.z)
        eo.to_mesh_clear()
    assert abs(lo) < .0001, 'The illustrated soles should be at ground level'
    heights.append((hi-lo)*1000)
assert 530 < heights[0] < 550
assert max(heights) < 555
assert old['posed_height_mm'] - heights[0] > 25
assert abs(heights[0] - report['posed_height_mm']) < .05
assert abs(max(heights) - report['max_idle_gesture_height_mm']) < .05
scene.frame_set(1)
for view in ['hero', 'front', 'side', 'head']:
    assert (ROOT / f'renders/rev-c/percival-rev-c-{view}.png').stat().st_size > 10000
result = {
    'status': 'PASS',
    'scene': scene.name,
    'saved_file': bpy.data.filepath,
    'original_revisions_and_approved_checkpoint_unchanged': True,
    'independently_measured_height_mm': round(heights[0], 2),
    'max_illustrated_gesture_height_mm': round(max(heights), 2),
    'shorter_than_rev_b_mm': round(old['posed_height_mm'] - heights[0], 2),
    'full_size_servo_envelopes': len(servos),
    'concept_panels': len([o for o in objects if 'panel_type' in o]),
    'socket_screw_appearances': len([o for o in objects if 'socket screw' in o.name]),
    'unverified': ['physical fit', 'printable wall construction', 'fastener mounting', 'torque', 'full-motion interference', 'balance', 'walking'],
}
