# Percival Rev D — parametric CAD

[Open the native Polykrom model](percival-rev-d.polykrom) · [STEP assembly](percival-rev-d.step) · [CAD views](../../rev-d-cad-review.html) · [Prototype STL parts](prototype_stl/)

This is an analytic solid reconstruction of the approved Rev D Blender design. The large head, short torso, substantial legs, small waving arm, cream/purple armor and orange details are retained. Existing Blender revisions are unchanged.

The native file contains **18 named parameters, 115 fully constrained sketches, 718 timeline features and 524 bodies**. Its posed bounds are **324.919 × 188.618 × 547.280 mm**, including the raised arm and antenna. Nine purchased-component/clearance envelopes are hidden; the STEP export contains the 515 visible bodies.

## What is editable

The `.polykrom` file retains component organization, sketches, dimensions, ruled loft segments, extrusions, bores, moves, colors and material metadata. STEP preserves solid geometry and body names, but does not carry the native parameter history.

| Parameter | Initial value | Drives |
|---|---:|---|
| `head_w`, `head_h` | 234, 112 mm | Head shell control widths/heights, bezel and rear lid |
| `head_depth` | 124 mm | Head enclosure fore/aft datums |
| `head_wall` | 2.6 mm | Head wall cross sections |
| `head_z` | 438 mm | Head assembly pose origin |
| `head_pitch`, `head_roll`, `head_yaw` | −3°, 6°, −5° | Expressive head pose |
| `torso_w`, `torso_d`, `torso_h` | 120, 96, 98 mm | Torso control sections |
| `body_wall`, `limb_wall` | 3, 2.8 mm | Nominal transverse enclosure/armor walls |
| `limb_scale` | 1 | Limb armor width/depth multiplier |
| `sole_w`, `sole_d` | 88, 134 mm | Sole control dimensions |
| `panel_t` | 2.5 mm | Selected service panel thicknesses |
| `m3_clearance` | 3.4 mm | Four front-frame clearance bores |

These are deliberately scoped parameters, not a fully constrained robot mechanism. For example, torso size does not automatically reposition every decorative cheek, screw or shoulder. Arm and leg poses are explicit feature transforms; joint motion is not simulated.

The head shell uses three adjacent two-section lofts joined into one wall solid. This avoids the smooth multi-section loft overshoot tracked in [Polycore #21](https://github.com/WCKDai/polycore/issues/21). With the head pose neutral, its shell is exactly **234 × 118 × 112 mm**; the front bezel and rear lid extend the enclosure beyond the shell's 118 mm depth. Optics, ear pods, fins and antenna extend the complete head farther.

## Prototype print files

There are **53 individual STL bodies** indexed in [prototype-parts.json](prototype-parts.json). Every mesh is closed with consistent edge winding and positive volume. Their current bounds fit a 256 mm cube; the largest axis-aligned dimension is 241.263 mm. This checks geometry bounds only, without brim, supports, chosen bed orientation or slicer toolpaths.

STLs retain assembly positions and poses. Place each selected part on the bed and choose its print orientation in the slicer. They are separate prototypes, not an assembled-robot print and not a manufacturing release. Inspect an individual part before printing it.

The walls have nominal transverse thicknesses; minimum thickness over slopes has not been certified. Head/frame bores and chest grille holes are real cuts. Most other screws are appearance geometry, and most cover mounting bosses, threaded inserts, bearing seats, panel access openings and retention features are not designed. Shells and panels can overlap, and generic joint housings are not released motor brackets. The STEP assembly intentionally preserves these concept interfaces.

Rigid-shell `ABS Plastic` and flexible-part `TPU nominal - grade unselected` metadata are provisional CAD density assignments, not material or printer settings. Do not use the CAD total mass as a robot mass estimate: generic actuator geometry, overlapping decorations and packaging envelopes are included.

The hidden J401, nominal 4S battery, four XM430 and two camera PCB envelopes retain the earlier layout sizes. This is not a complete component allocation, mounting design or Rev D bill of materials. The earlier [build/purchasing guide](../../BUILD_GUIDE.md) describes the Rev A study; it is not a purchase release for this new chassis.

## Verification

Run `python3 scripts/check_rev_d_cad.py` from the repository root. It verifies native gate evidence, all 53 STL meshes, bounds and artifact hashes. [verification.json](verification.json) records the results.

Independent parameter tests neutralized the head pose and checked width 234→244 mm, then checked head height 438→448 mm, including the bounding box and center of mass. All 13 strict geometry assertions passed at the original 1e-6 mm tolerance, six quality gates passed, and all five changed parameters were restored. [Evidence](evidence/parameter-checks.json). The earlier failed smooth-loft envelope test is retained in [the before-fix record](evidence/parameter-checks-before-ruled-fix.json).

The native file was reopened independently. The STEP file was also reopened and compared against the visible native bodies; see [STEP verification](evidence/step-roundtrip.json). Generic structural quality checks do not prove fastening, clearances, stiffness, thermal performance or walking.

Still unverified: complete hardware fit and wiring, motor torque and duty cycle, power protection, minimum wall thickness, slicer supports, panel retention, swept joint collisions, structural loads, balance and locomotion. A feasible walking prototype needs that mechanical/control engineering phase before purchase or assembly release.

## Rebuild and MCP setup

Built with the official [Polykrom v0.21.0-rc.1 release](https://github.com/WCKDai/polykrom/releases/tag/v0.21.0-rc.1), the latest published release checked on 2026-10-30. It is a release candidate. Download hashes and installation evidence are in [polykrom-installation.json](evidence/polykrom-installation.json).

On the authoring Mac the release is installed beside the previous app at `/Applications/Polykrom 0.21.0-rc.1.app`. The separate original app/design was preserved. A persistent Codex MCP server named `polykrom-percival` points to this release, connects to `127.0.0.1:27879`, and permits file access to this project's `cad/` directory. Its handshake and modeling calls were verified. After restarting Polykrom, check its actual control port before reconnecting; the port can change when another instance is running.

The official MCP is also usable in a headless session. That is useful for deterministic builds and verification:

```sh
export POLYKROM_CLI="/Applications/Polykrom 0.21.0-rc.1.app/Contents/MacOS/polykrom-cli"
python3 scripts/build_rev_d_cad.py
"$POLYKROM_CLI" run cad/rev-d/build.json --save cad/rev-d/percival-rev-d.polykrom
"$POLYKROM_CLI" mcp --headless --in cad/rev-d/percival-rev-d.polykrom --allow-path "$PWD/cad"
```

[build.json](build.json) contains all 1,123 engine commands; [stages.json](stages.json) groups them for MCP batches. The generator is [build_rev_d_cad.py](../../scripts/build_rev_d_cad.py). [polykrom_mcp.py](../../scripts/polykrom_mcp.py) runs request lists through the official MCP using the Python `mcp` package. It treats a failed quality verdict as a failure even when the transport reports a successful tool call.

Exporting again after a parameter change is required; STL and STEP files do not update automatically. Preserve the current `.polykrom` first when experimenting. Git history and the untouched Rev C/D Blender files are the rollback path.
