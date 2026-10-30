"""Rebuild helper, for the agent-created scene only; retain original scene and a checkpoint."""
import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
scene=bpy.data.scenes.get('Percival • engineering assembly')
if not scene or scene.get('source_revision')!='e337f3b177b4b53abff70b31d1695a7b66cc6d2e':
    raise RuntimeError('Expected generated scene not found; refusing reset')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'design'/'percival-before-grippers.blend'),copy=True)
objects=list(scene.objects); collections=list(scene.collection.children)
bpy.context.window.scene=bpy.data.scenes['Scene']
for ob in objects: bpy.data.objects.remove(ob,do_unlink=True)
for col in collections: bpy.data.collections.remove(col)
bpy.data.scenes.remove(scene)
for mat in list(bpy.data.materials):
    if mat.users==0: bpy.data.materials.remove(mat)
result={'retained_scene':bpy.context.scene.name,'checkpoint':'design/percival-before-grippers.blend'}
