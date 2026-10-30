# Executed verification and limits

Baseline: `git status --short --branch` was clean main; `git log -1 --oneline` was b94ce4b. There were no test/build manifests and no installed `.agents` kit. No kit was installed. `eng verify --profile fast`, `eng verify --profile full` and `eng evidence verify` were unavailable/unverified.

Blender was opened with `open -a Blender`. The installed official Blender MCP 1.0.3 was called through its MCP Python client using `/Users/dearwolf/.local/share/blender-mcp/1.0.3/.venv/bin/python scripts/blender_mcp.py ...`. Blender reported 5.2.1 LTS. The first MCP call inspected the existing scene before edits; it is retained in the saved file.

Commands/workflows executed:

- `python3 scripts/fetch_reference.py`: downloaded pinned official geometry and preserved source hashes. Final variant is toddlerbot_2xc_gripper, 59 source files. Downloaded source text was treated as data, not executed.
- `.../python scripts/blender_mcp.py scripts/import_reference.py`: PASS, 51 actual visual meshes and URDF link transforms. Initial 2XC without grippers was superseded by the documented gripper variant, with checkpoint saved.
- `.../python scripts/blender_mcp.py scripts/build_shell.py`: created and iterated 35 custom parts. Review found floating face tabs, seam-boss interference, inaccessible nut pockets, optical-part overlap and missing mating holes; these were fixed, not waived.
- `.../python scripts/blender_mcp.py scripts/verify_export.py`: first check found 12 neutral-pose hardware intersections and a visor mesh boundary. Final check passes 35/35 mesh checks with no reported hardware/custom-part surface intersections. Height 594 mm. Every custom part fits the A1 and XL bounds. See `geometry-before-clearance-fixes.json` and `geometry-verification.json`.
- `python3 scripts/check_artifacts.py`: first run FAILED on four float32 STL exports despite their Blender topology passing. Sub-micron boolean slivers were repaired using `clean_export_precision.py`, on a 0.001 mm geometry grid; the independent gate was unchanged. Final run PASS: 35 STL/3MF pairs and 59 source hashes. Original failure is `artifact-checks-before-precision-fix.json`.
- `.../python scripts/blender_mcp.py scripts/render_views.py`: front, side, top and cutaway renders; assembly visibility/positions restored after cutaway.
- `python3 -m py_compile scripts/*.py`: PASS.
- `git diff --check`: PASS.
- `.../python scripts/blender_mcp.py scripts/check_saved_blend.py --blend design/percival.blend`: see `saved-blend-check.json` for fresh-file readback result.

The exact machine-local interpreter path above uses the already-installed MCP environment; nothing was installed in this project. To regenerate in order: fetch, import into a fresh project, stage_scene, build_shell, clean_export_precision, verify_export, render_views, check_artifacts, saved-blend check. `reset_generated_scene.py` is an explicit rebuild helper that saves a checkpoint and removes only the known generated scene. Do not run it on unsaved manual edits you wish to keep. Rebuilding the shell replaces its generated collections after saving a checkpoint.

Computed full custom material estimate: approximately 537 g. Source gripper URDF mass: 3.663 kg. Combined geometric estimate: about 4.20 kg, excluding new fasteners/adhesives and without subtracting retained original head mass. Centre of mass rises by about 18 mm in the neutral calculation. These are calculations, not measurements or balance validation.

Unverified: actual slicer toolpaths/print success, whole-surface minimum thickness, continuous joint motion, containment collisions, full head retention adapter and strap routing, camera lens depth/FOV/calibration, battery-tray fit, regulator-voltage mismatch, fuse/switch/harness selection, thermal duty, impact/structural strength, firmware integration with revised inertia, and walking. Manufacturer source geometry and existing walking demonstrations do not verify this modified assembly.

Official chassis 3MF retrieval failed with HTTP 402 at MakerWorld. Chassis print plates are linked in the guide but not bundled. Existing geometry files in reference are assembly meshes, never structural print releases.

No physical hardware was powered, no purchasing completed, and no production or external publishing action performed.
