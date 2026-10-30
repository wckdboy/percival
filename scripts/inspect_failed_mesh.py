import bpy,bmesh
ob=next(o for o in bpy.context.scene.objects if o.get('part_id')=='P03')
bm=bmesh.new();bm.from_mesh(ob.data)
result={'bad_edges':[{'verts':[[round(v*1000,4) for v in vert.co] for vert in e.verts],'faces':len(e.link_faces)} for e in bm.edges if not e.is_manifold]}
bm.free()
