"""Save the live, user-approved Blender state before starting Rev C."""
import bpy
import hashlib
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
source = ROOT / 'design/percival-rev-b-bdx.blend'
target = ROOT / f'design/percival-rev-b-approved-{stamp}.blend'
assert bpy.data.scenes.get('Percival • Rev B / BDX character study')
original_hash = hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.save_as_mainfile(filepath=str(target), copy=True)
result = {
    'status': 'SAVED',
    'approved_checkpoint': str(target),
    'approved_checkpoint_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
    'original_rev_b_sha256': original_hash,
    'original_rev_a_sha256': hashlib.sha256((ROOT / 'design/percival.blend').read_bytes()).hexdigest(),
    'active_scene': bpy.context.scene.name,
}
(ROOT / 'evidence/rev-c-preserved-baseline.json').write_text(json.dumps(result, indent=2) + '\n')
