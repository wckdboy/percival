# Percival — Rev A engineering prototype

This project puts the supplied cream/purple/orange character design around the real **ToddlerBot 2XC gripper** mechanism. It contains an editable Blender assembly, custom shell fit prototypes, source geometry, a purchasing plan and verification evidence. **It is not a released, fully validated walking robot design.** Build and commission the documented bare chassis first.

The user requirements are walking, maximum 600 mm height, Bambu Lab A1 / Prusa XL printing, and Denmark/EU sourcing. The supplied images specify appearance; they are not dimensioned mechanical drawings.

## What is in the model

`design/percival.blend` contains source hardware at its original dimensions, 32 actuated axes including two grippers, link frames imported from the source URDF, and removable custom skins. The scene uses metres internally and displays millimetres. X is robot left, Y is rear, Z is up. The import preserves each mesh's visual origin; it does not stretch the chassis to match the illustration.

Collections distinguish OEM assembly reference, kinematics, printable custom parts, camera envelopes, visual details, source images and studio lighting. The OEM head is hidden for the exterior view but retained for inspection. The imported hierarchy is a neutral pose reference, **not a simulation of the closed-chain transmissions**. Rotating arbitrary link frames is not a valid gait test.

The custom head has a 236 × 108 × 112 mm main enclosure. Flexible fins bring the neutral assembly to 594 mm, leaving only 6 mm below the height limit. This is a neutral-pose dimension, not an all-pose guarantee. Head cameras move to 120 mm centre spacing. Their optics, USB strain relief, cable routing and calibration must be checked.

## Chassis to print and build

Use the authors' [ToddlerBot 2.0 printing instructions](https://hshi74.github.io/toddlerbot/hardware/03_3d_printing.html), [MakerWorld plates](https://makerworld.com/en/models/1733983), [editable Onshape CAD](https://cad.onshape.com/documents/565bc33af293a651f66e88d2) and [assembly instructions](https://hshi74.github.io/toddlerbot/hardware/04_assembly_manual.html). Select **2XC with grippers**, and reconcile the selected printing profile with the pinned model revision before ordering.

**The official chassis print plates are not bundled here.** The automated MakerWorld request returned HTTP 402, so their download and plate-level compatibility have not been verified. The authors recommend the supplied print orientations/profiles. The `reference/.../assets/*visual.stl` files contain merged printed and purchased hardware and must never be sliced as chassis parts.

Source revision: `e337f3b177b4b53abff70b31d1695a7b66cc6d2e`. The exact URDF and mesh hashes are recorded in `reference/toddlerbot/SOURCE_MANIFEST.json`.

## What to buy

The [published BOM](https://docs.google.com/spreadsheets/d/e/2PACX-1vQmoxJnTnUaQ_-WAAjnchBhaX5HZ4ElUV5pXksEV6GEbeEjiie1E_BdN9XCMt6FtfBaopXoaeSOeMDg/pubhtml) is saved locally as `reference/toddlerbot/published_bom_2026-10-30.csv`. It includes bearings, shafts, fasteners, cables and tools omitted from this overview. This table is an architecture shortlist, not a complete purchase order.

| Item | Quantity | Selection / procurement note |
|---|---:|---|
| DYNAMIXEL 2XC430-W250-T | 2 | Dual-axis TTL module; do not substitute RS485 suffix R |
| DYNAMIXEL 2XL430-W250-T | 6 | Dual-axis TTL module; resolve power-rail maximum before energising |
| DYNAMIXEL XC330-T288-T | 8 | Six in base, two for the gripper option |
| DYNAMIXEL XC430-T240BB-T | 4 | Match exact model and bracket/horn system |
| DYNAMIXEL XM430-W210-T | 4 | Match exact speed/gear ratio; not W350 |
| HN11-I101 idler sets | 10 | Base quantities from current BOM; check gripper assembly hardware separately |
| HN12-I101 idler sets | 4 | Do not interchange with HN11 |
| Seeed reComputer J4012, SKU 110110145 | 1 | Orin NX 16 GB + SSD; use the documented board/cooling assembly, not its complete retail enclosure |
| ToddlerBot TTLPowerBoardV8 | 1 assembled board | Custom 8-channel USB/TTL board; fabrication archive included; this is the motor interface, not a hobby PWM shield |
| Pololu D36V50F12, #4095 | 2 | Upstream candidate; independent regulated rails; voltage acceptance issue below |
| Adafruit BNO085, #4754 | 1 | Preserve upstream placement, orientation and interface |
| Arducam B0202 IMX291 USB cameras | 2 | 38 × 38 mm boards; 34 mm fixing pitch used in visor; lens-depth fit remains open |
| AW-CB375NF Wi-Fi, MHF4 antennas | 1 set | Follow upstream BOM and Jetson setup |
| Speaker + M38 audio board, USB hub/cables | 1 set | Follow upstream BOM; there is no functional speaker inside the cosmetic ear pods |
| Assembled 4S 2000 mAh LiPo | 1 | See battery options below; do not substitute raw cells or 3S without revisiting power |
| SkyRC S65 SK-100152 balance charger | 1 | External charger; correct XT60/balance leads and EU mains cable |
| Main fuse/holder and actuator stop switch | 1 each | Final ratings and exact parts require harness/current review; not released in this revision |

Use ROBOTIS manuals for specifications, since reseller summaries sometimes disagree. EU starting points include [Generation Robots](https://www.generationrobots.com/en/403555-dynamixel-2-axis-actuator-2xc430-w250-t.html) and [MYBOTSHOP](https://www.mybotshop.de/DYNAMIXEL-2XC430-W250-T_2); availability and delivered Danish prices are not confirmed. Reconcile any prepacked motor bundle against the current BOM: an older bundle includes different accessory counts.

The authors' 2XC essentials estimate is **US$5,727.94**, before the separately sourced PCB, tools and EU landed-cost differences. Gripper motors add **US$206.78** at the BOM's listed prices. These are historical planning figures, not a current quote. For example, [Seeed currently lists J4012 at US$1,399](https://www.seeedstudio.com/reComputer-J4012-p-5586.html), versus $955 in the saved BOM. No purchase has been made.

### Battery and charger

The upstream battery link resolves to a Tattu R-Line V3 2000 mAh 4S pack. A dimensioned [Tattu TAA20004S15X6](https://gensace.de/products/taa20004s15x6) is 74 × 39 × 40 mm, 217 g, but was shown out of stock during research.

A candidate available through an [EU retailer](https://www.drone-fpv-racer.com/en/cnhl-black-series-2000mah-4s-100c-9413.html) is [CNHL Black Series 2001004BK](https://chinahobbyline.com/products/cnhl-black-series-2000mah-14-8v-4s-100c-lipo-battery-with-tx60-plug): 4S 2000 mAh, XT60 and JST-XH, nominal 76 × 38 × 47 mm, 234 ± 5 g. The manufacturer allows 1–5 mm size variation. **It is not a confirmed drop-in fit in the source chassis.** Measure the delivered pack, allow wire bends and noncompressive padding, and validate the battery tray before ordering or printing a replacement enclosure. No final replacement tray is supplied.

The [SkyRC S65](https://www1.skyrc.com/s65?from=nav) supports 2–4S LiPo balance charging. Use the normal 4S LiPo setting, 4.20 V/cell, both main and balance connections, and initially 2 A for a 2000 mAh pack subject to its manufacturer's instructions. Remove the pack from the robot for charging. Do not charge through the motor board.

Nominal battery energy is `14.8 V × 2 Ah = 29.6 Wh`. A planning calculation using 80% accessible energy and 60–100 W average battery draw gives about 14–24 minutes. **Neither the draw nor runtime has been measured**; the calculation is not a runtime specification. The regulator dropout and battery sag also matter before the pack is depleted.

## Wiring architecture and the unresolved supply issue

Retain the documented Jetson and V8 interface for the first build. Raspberry Pi Zero and OpenCR are not drop-in substitutes for this software/hardware configuration. The V8 [fabrication package and ordering instructions](https://hshi74.github.io/toddlerbot/hardware/02_pcb8ch.html) are available; `reference/toddlerbot/TTLPowerBoardV8.zip` preserves the downloaded fabrication package; its archive digest is recorded in `reference/toddlerbot/FABRICATION_SOURCE.json`.

Gerber net attributes in that package show this topology (verify against the delivered PCB revision before connecting power):

```text
4S pack (16.8 V full) -> external fuse to be specified -> raw battery rail
  +-> J10 -> Jetson J401 carrier (unswitched; 9–19 V input)
  +-> J12 physical motor-power switch -> switched +BATT
       +-> buck 1 -> /Vout1 -> motor ports J1/J2/J3/J4
       +-> buck 2 -> /Vout2 -> motor ports J6/J7/J8/J11
       +-> J16/J18 auxiliary outputs: RAW switched battery voltage

Jetson USB -> V8 CH348L interface -> eight TTL signal channels
Jetson -> cameras / IMU / audio using the upstream wiring
```

Do not connect raw 4S to the DYNAMIXEL supply ports. Do not parallel the two regulator outputs. Keep the board's prescribed common signal ground. The motor-power switch leaves the Jetson powered, allowing a controlled shutdown; it is not a whole-robot battery disconnect or a certified emergency-stop system.

**Resolve this before powering motors:** [Pololu #4095](https://www.pololu.com/product/4095) specifies 12 V with 4% accuracy, which permits 12.48 V, while [2XL430](https://emanual.robotis.com/docs/en/dxl/x/2xl430-w250/) specifies an operating maximum of 12 V. The source build's existence does not resolve that specification mismatch. Obtain manufacturer guidance or select and validate a revised regulated supply; bench-check setpoint, startup, load transients and motor deceleration with appropriate instruments. No revised regulator has been qualified here.

The regulator's headline 4.5 A figure is at 36 V input and depends on cooling. It is not a verified continuous capacity at a 4S battery voltage inside this enclosure. Verify each rail independently. Final fuse, wire, connector and switch ratings must follow the actual branch currents and weakest component. The V8 BOM did not establish an onboard main fuse. Connector polarity and pin numbering must be checked directly against the board and manufacturer's drawings, not inferred from cable colours.

## Printing the custom skins

`print_prototypes/` contains one STL and one geometry-only 3MF per passing custom part. Units are **millimetres**; do not apply a 1000× rescale. 3MF files contain geometry and a proposed orientation, not tested Bambu/Prusa machine profiles or G-code. All custom parts fit within A1 256 mm and XL 360 mm envelopes according to computed bounds; bed fit does not establish print success.

Start with **P04L, one lens bezel**, and one small limb fairing. Measure holes, wall thickness and the mating hardware. Then print P03 visor to check camera mounting and field of view before spending filament on P01/P02. Use the source chassis profiles for structural parts; the settings below apply only to these new cosmetic parts.

Suggested first fit-print settings: PETG, 0.4 mm nozzle, 0.20 mm layer height, four 0.45 mm wall lines where the 1.8 mm skin permits, and local supports for internal bosses/ear brackets as previewed in the slicer. Inspect the actual toolpaths. Use TPU 95A for flexible fins/ear inserts if available; the TPU parts are not load-bearing. Separate colours are separate parts, so AMS/multi-tool printing is unnecessary. A 4 mm brim fits the measured envelopes. Remove supports without enlarging mating holes accidentally.

Nominal holes: M2 clearance 2.4 mm; M2.5 clearance 2.8 mm; M3 clearance 3.4 mm. Rear M3 nut pockets use 5.9 mm across flats. These are design allowances, not demonstrated fit on your machines. Drill/ream or revise them after a test print; do not force a nut into a splitting boss.

### Shell assembly

1. Build the stock chassis with the authors' parts and instructions. Establish a baseline of motor temperatures, current, weight, calibration and supported standing before adding skins.
2. Fit the camera visor P03 and P04 rings on the bench. Use M2 hardware through the 34 mm board pattern with insulating standoffs. **Standoff length and screw length remain to be set from the delivered lens/PCB**, so the shown camera depth is only an allowance. Ensure the lens projects beyond the baffle and the 160° camera view is not obstructed. Recalibrate the camera pair after repositioning it.
3. Join P01 front bezel and P02 rear shell with four M3×25 bolts and M3 nuts, with the visor removed for access. Rear nut pockets are open. Fit P03 using four M2.5 bolts/nuts; choose length after measuring the printed tab stack. No heat-set inserts are assumed.
4. Attach each flexible ear using two M3 through bolts and nuts through the matching P02 upstand; approximately M3×16, to be confirmed on the printed stack. Seat cosmetic pod inserts with removable adhesive; pods must be removable to open the head seam.
5. Prototype the head's retention to the **retained stock head cage/neck assembly** using the rear 6 mm strap ports and soft noncompressive pads. The final head adapter, restraint against rotation and cable strain relief are **not released**. Do not rely on cosmetic pods or the small camera screws to support the head.
6. Limb shields have slots for 6 mm hook-and-loop straps. Route around one rigid link only, clear of motor cases that must cool, gears, cables and moving joints. Actual strap routing, standoff pads and retention need physical fitting. Chest trim P11 has matching chest holes; its fastening does not replace the source electronics cover.
7. Keep the original sole/contact surfaces. P34 is only a toe cowl; check floor clearance across ankle movement. Leave it off if it contacts the ground or foot mechanisms.

The full custom skin is a substantial addition to the source robot's mass. Consult `evidence/geometry-verification.json` for the computed material estimate and centre-of-mass shift. It uses solid modeled PETG/TPU volumes, retains the original head mass conservatively, and excludes additional screws, adhesives and wires. **Weigh each printed part** and update the robot's collision and inertial models before locomotion training/testing. Stock policies are not validated with these skins.

## Commissioning and release gates

Use the authors' software setup, motor-ID assignment, calibration, standing and walking procedures. This project does not provide new locomotion firmware or a ready-to-run walking policy. Use a suitable support rig with the bare robot first, then add one body region at a time. A torque-off command can make a biped fall; the support must catch it.

Before powered locomotion with the shell: resolve the voltage issue; inspect polarity and branch protection; verify low-voltage cutoff and rail temperature under measured load; establish head retention; check full mechanism travel including linked gears and grippers; verify wiring bend radius and pinch clearance; weigh the assembly and update inertia/collision models; validate supported standing, then supported stepping. The present geometric check is **neutral-pose surface intersection only** and does not cover enclosed-volume interference, cable volumes, full motion, FEA, fatigue, impacts, balance or gait stability.

## Why DYNAMIXEL for this revision

The chosen mechanical/control platform already uses these actuators. QDD remains an alternative architecture, not an interchangeable motor upgrade. [RobStride's own table](https://github.com/RobStride/Product_Information) gives RS05 at 191 g, 1.8 N·m rated / 5.5 N·m peak, 15–60 V input, with rated torque dependent on specified heatsinking. Twenty RS05 units alone would be 3.82 kg before structure or power. [CubeMars AK40-10 V3](https://www.cubemars.com/product/ak40-10-v3-0-kv170-robotic-actuator.html) is another 190 g, 24 V integrated option. Either demands different structure, CAN control, power handling and thermal validation. “RoboMars” was not verified as a manufacturer; CubeMars may be the intended name.

## Verification and rollback

See `evidence/geometry-verification.json`, `evidence/geometry-before-clearance-fixes.json` and `evidence/verify-mcp.json`. They record actual topology, connected-component, print-envelope, neutral dimensions and static intersection results. The source file hashes are checked independently by `scripts/check_artifacts.py`.

The repository started with only README/icon files, clean `main` at `b94ce4b`, with no test/build manifest or `.agents` kit. Engineering-kit fast/full/evidence gates are **unavailable and were not installed**. Original Blender `Scene` is preserved; generated scene checkpoints are in `design/`. To roll back, open a checkpoint or the original scene. At the Rev A verification stage, no hardware had been energised, purchases made, repository pushed or external design published. Later repository publication is recorded separately; it does not validate the hardware.

Source hardware and derived design are **CC BY-NC-SA 4.0**. Original ToddlerBot code/docs are MIT. See `ATTRIBUTION.md`; do not describe the source hardware as commercially unrestricted.
