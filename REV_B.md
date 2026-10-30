# Percival Rev B — BDX-inspired character proportions

Open [the Rev B Blender file](design/percival-rev-b-bdx.blend). The active scene is **Percival • Rev B / BDX character study**. Rev A remains unchanged at `design/percival.blend`.

This revision changes the character's silhouette: broad bent legs, large rounded boots, a short rounded torso, compact two-finger arms, a raised greeting hand, unequal ocular shrouds, a curious head tilt and asymmetrical listening fins. The original cream, purple and orange colours remain. The reference direction is [Disney Research's BDX droids](https://la.disneyresearch.com/bdx-droids/), interpreted with Percival's own arms and appearance.

The posed model is approximately **574.6 mm** high. Its 73-frame illustrative idle head gesture reaches approximately **579.5 mm**, below the requested 600 mm limit. Play the Blender timeline at 24 fps to see the gentle head movement; the raised hand and leg stance are static poses. Both soles lie on the ground in the illustration. This is not a demonstrated balanced stance or controller trajectory.

The main head envelope is 234 × 112 × 112 mm. The proposed body is 146 × 102 × 78 mm. Thigh and shin covers are 77 mm and 70 mm wide, respectively. Each sole is 96 × 144 mm. These are design dimensions, not manufacturing drawings.

**Mechanical-layout concept, not a revised print release.** The shorter body requires repackaging; the longer/bulkier legs, smaller arms and different feet require new structural interfaces, torque calculations, collision/inertia models and motion testing. Rev A's mesh and fit checks do not transfer to this design. No new STL/3MF files are presented as buildable parts.

The layout includes four full-size XM430 actuator envelopes, a 100 × 80 mm J401 carrier envelope, a separate cooling allowance, a nominal 76 × 38 × 47 mm battery envelope and 38 × 38 mm camera-board envelopes. They are kept in the named envelope collection and hidden in beauty renders. These are preliminary placement studies, not a complete actuator allocation or verified fit; connector access, cables, heat rejection, camera optics and battery tolerance remain unresolved.

Views: [hero](renders/rev-b/percival-bdx-hero.png), [front](renders/rev-b/percival-bdx-front.png), [side](renders/rev-b/percival-bdx-side.png), [head detail](renders/rev-b/percival-bdx-head.png). Measured dimensions and limits are in `evidence/rev-b-layout.json`; fresh-file checks are in `evidence/rev-b-saved-check.json`.

The model was created through the installed official Blender MCP. `build_rev_b.py` creates the separate scene; rerunning it saves a checkpoint before replacing that generated scene. `render_rev_b.py` renders the review views and restores the hero camera. `check_rev_b.py` reopens the saved file using MCP's background Blender tool to verify the scene, dimensions and unchanged Rev A hash. All physical, print, full-motion and locomotion checks remain unverified. See `ATTRIBUTION.md` for source/design terms.
