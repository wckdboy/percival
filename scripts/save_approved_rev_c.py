"""Save the live approved Rev C before the reference-led Rev D revision."""
import bpy
import hashlib
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
target = ROOT / f'design/percival-rev-c-approved-{stamp}.blend'
assert bpy.data.scenes.get('Percival • Rev C / compact industrial character')
preserved = {}
for rev, name in [('a', 'percival.blend'), ('b', 'percival-rev-b-bdx.blend'), ('c', 'percival-rev-c-chamfer.blend')]:
    preserved[f'original_rev_{rev}_sha256'] = hashlib.sha256((ROOT / 'design' / name).read_bytes()).hexdigest()
bpy.ops.wm.save_as_mainfile(filepath=str(target), copy=True)
result = {
    'status': 'SAVED',
    'approved_checkpoint': str(target),
    'approved_checkpoint_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
    'active_scene': bpy.context.scene.name,
    **preserved,
}
(ROOT / 'evidence/rev-d-preserved-baseline.json').write_text(json.dumps(result, indent=2) + '\n')
