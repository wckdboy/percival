"""Remove sub-micron boolean slivers before float32 STL serialization.

Applied to custom skins only. This repairs geometry; it does not relax the
independent STL edge/winding checks. Original precision is kept in checkpoint.
"""
import bpy,bmesh
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'design/percival-before-export-cleanup.blend'),copy=True)
changes=[]
for ob in bpy.data.collections['03 • PERCIVAL PRINTS — Rev A fit prototypes'].objects:
    bm=bmesh.new();bm.from_mesh(ob.data);before=(len(bm.verts),len(bm.faces))
    # A 0.001 mm grid is well below FDM dimensional accuracy and STL precision issues.
    for v in bm.verts:
        for axis in range(3): v.co[axis]=round(v.co[axis],6)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY')
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    after=(len(bm.verts),len(bm.faces));bm.to_mesh(ob.data);bm.free()
    ob['export_grid_mm']=.001
    changes.append({'part':ob['part_id'],'before':before,'after':after})
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'design/percival.blend'))
result={'cleanup_grid_mm':.001,'parts':changes}
