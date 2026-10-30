"""Execute through Blender MCP's background tool, independently reopening the saved file."""
import bpy
scene=bpy.data.scenes['Percival • engineering assembly']
parts=[o for o in scene.objects if 'part_id' in o]
source=[o for o in scene.objects if o.name.startswith('OEM • ')]
assert len(parts)==35,(len(parts),'custom part count')
assert len(source)==51,(len(source),'source mesh count')
assert scene.unit_settings.system=='METRIC'
assert scene.unit_settings.scale_length==1
assert all(o.get('export_grid_mm')==.001 for o in parts)
assert scene.get('source_revision')=='e337f3b177b4b53abff70b31d1695a7b66cc6d2e'
assert bpy.data.scenes.get('Scene') is not None,'original scene retained'
result={'status':'PASS','saved_file':bpy.data.filepath,'custom_parts':len(parts),'source_meshes':len(source),
        'packed_images':sum(bool(i.packed_file) for i in bpy.data.images),'original_scene_retained':True}
