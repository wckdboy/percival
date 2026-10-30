"""Fresh Blender-process checks of the saved Rev B concept; no physical-fit claims."""
import bpy
import json
import hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
report=json.loads((ROOT/'evidence/rev-b-layout.json').read_text())
scene=bpy.data.scenes['Percival • Rev B / BDX character study']
assert scene['revision']=='B'
assert scene.unit_settings.scale_length==1 and scene.unit_settings.system=='METRIC'
assert scene.frame_start==1 and scene.frame_end==73
assert scene.render.fps==24
assert report['max_idle_gesture_height_mm']<600
assert 550<report['posed_height_mm']<600
assert not any('part_id' in o for o in scene.objects),'Do not inherit Rev A printable part IDs'
servos=[o for o in scene.objects if 'manufacturer_envelope_mm' in o]
assert len(servos)==4
for o in servos:
    assert all(abs(a-b)<.01 for a,b in zip(sorted(v*1000 for v in o.dimensions),[28.5,34,46.5]))
    assert all(abs(v-1)<1e-6 for v in o.scale),'Purchased envelope must not be scaled'
actual=hashlib.sha256((ROOT/'design/percival.blend').read_bytes()).hexdigest()
assert actual==report['source_rev_a_sha256'],'Rev A must remain unchanged'
for name in ['percival-bdx-hero.png','percival-bdx-front.png','percival-bdx-side.png','percival-bdx-head.png']:
    assert (ROOT/'renders/rev-b'/name).stat().st_size>10000
result={'status':'PASS','saved_file':bpy.data.filepath,'scene':scene.name,'full_size_servo_envelopes':len(servos),
        'original_rev_a_unchanged':True,'posed_height_mm':report['posed_height_mm'],
        'measured_gesture_maximum_mm':report['max_idle_gesture_height_mm'],
        'limits':'Design illustration only; no print, full-motion, packing, balance or hardware validation.'}
