<img src="assets/icon.svg" width="64" height="64" alt="">

# Percival — printable biped design study

**Editable parametric CAD: [Rev D in Polykrom](cad/rev-d/README.md).** The native model includes 18 parameters, 115 constrained sketches, hollow enclosures, separate panels and a complete feature history. The package includes a STEP assembly, 53 prototype STL bodies, four CAD views and verification evidence. Overall posed height is 547.28 mm. These are prototype geometry, not a manufacturing or walking release.

**Latest visual direction: [Rev D — reference proportions](design/percival-rev-d-reference.blend)**, about 547 mm tall. Lower hips, shorter tapered leg links, a taller/narrower chest, a distinct pelvic pod, slimmer articulated arms and sloping boots follow the supplied reference images. The head has smaller recessed optics, a central sensor capsule, larger purple side housings and a shaped rear shell. [View all five renders](rev-d-review.html). The illustrated head gesture stays below 550 mm.

The approved [Rev C checkpoint](design/percival-rev-c-approved-20261030-155239.blend) and [original Rev C model](design/percival-rev-c-chamfer.blend) are preserved. `evidence/rev-d-preserved-baseline.json` records their hashes; `scripts/check_rev_d.py` remeasures the saved geometry and verifies preservation. Copies of the four user-supplied references are in `reference/design-images/`. Their proportions are visual estimates, not dimensional engineering drawings.

Rev D remains a mechanical-layout concept. The CAD reconstruction adds nominal wall thicknesses and selected clearance holes, but minimum walls, structural interfaces, fastener mounts, electronics packing, torque, full-motion interference and walking remain unverified. Prototype STL exports are explicitly separate from a print release.

The approved [Rev B checkpoint](design/percival-rev-b-approved-20261030-153815.blend), [Rev B model and notes](REV_B.md), and Rev A files below are preserved. `evidence/rev-c-preserved-baseline.json` records their hashes; `scripts/check_rev_c.py` independently measures the saved scene and checks those files remain unchanged. Rev C produces no new print-release STL/3MF files.

Reference-inspired robot built in Blender through the official local Blender MCP, around real ToddlerBot 2XC gripper hardware. Maximum requested height: 600 mm. Printers: Bambu A1 / Prusa XL. Sourcing: Denmark/EU.

Blender models, Polykrom designs, STEP, STL and 3MF files use Git LFS. Install Git LFS before cloning, or run `git lfs install` followed by `git lfs pull` in an existing checkout to download the full files. Open the Rev C or Rev D `.blend` directly in Blender; regeneration scripts use the local Blender MCP setup described in `scripts/blender_mcp.py`. Verification scripts resolve checkpoint files within the checkout; historical evidence retains the original machine paths.

**Rev A is a fit-test prototype, not a validated walking or purchase-ready release.**

- [Build, purchasing and electrical guide](BUILD_GUIDE.md)
- [Editable Blender assembly](design/percival.blend)
- [Custom STL / geometry-only 3MF prototypes](print_prototypes/)
- [Part manifest](print_prototypes/parts-manifest.json)
- [Geometry verification evidence](evidence/geometry-verification.json)
- [Source attribution and licenses](ATTRIBUTION.md)

Real component and chassis meshes are kept separate from the custom print files. Download the authors' actual chassis plates from the link in the guide; do not slice reference assembly meshes.

Regeneration scripts are in `scripts/`. The original Blender scene is preserved, and generated checkpoints are saved before rebuilding. No purchases, powered hardware tests or walking tests have been performed.
