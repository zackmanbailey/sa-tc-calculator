# Purlin Rules Reference — TitanForge / Structures America

> Living document. Last updated: 2026-04-29 (corrected §4.1/4.1b/4.2 facing directions — C pairs toward `[ ]`, Z pairs away `] [`; added component weights/gauges/coils §21, equal-length piece breaking §22, solar panel dimension-driving rules §6.2 update)
> Source: Design discussions between Zack (Titan Carports) and engineering team.

---

## 1. Purlin Types

### 1.1 C-Purlin
- Symmetric cross-section: web vertical, both flanges extend the same direction, lips curl inward.
- Butt-joint connection: two C-purlins butt end-to-end over the rafter. A single P1 clip bridges both purlin ends with 4 TEK screws per purlin (8 total per connection). At the last rafter, only one purlin is present, so all 8 screws go into that single purlin.
- C-purlins do NOT extend past the rafter at the eave. A 40' wide building with C-purlins has a 40' rafter.
- C-purlins alternate facing direction in pairs — pairs face TOWARD each other `[ ]` (see Section 4).
- Currently only 12" depth, 12GA available. System should support user-configurable depth for future use.

### 1.2 Z-Purlin
- Asymmetric cross-section: web vertical, top flange extends one direction, bottom flange extends the opposite direction. Lips at ~45° at flange ends.
- Z-purlins alternate facing direction in pairs — pairs face AWAY from each other `] [` (see Section 4). This is separate from the nesting behavior at splices.
- **Nesting at splices**: When two Z-purlins overlap at a splice point, one sits on top of the other (same direction at that joint) and the flanges stack/nest together. See the yellow-on-blue nesting drawing for reference.
- Overlap/splice connection: Z-purlins extend past the rafter by a configurable distance (default 6'). Where two Z-purlins overlap, there is a 6" lap (default, user-configurable). 8 TEK screws per lap splice.
- Z-purlin top flanges extend past the rafter at the eave. A 40' wide building with Z-purlins using 3.5" top flanges has a rafter length of 40' - 3.5" - 3.5" = 39'-5".
- The eave flange overhang dimension defaults to 3.5" but is user-overridable.
- Currently only 12" depth, 12GA, G90 galvanized available. System should support user-configurable depth for future use.

---

## 2. Purlin Layout Along Building Length

### 2.1 General Rules
- Every purlin LINE (across the building width) uses the SAME length pattern.
- Purlins must span at least 2 rafters.
- Maximum purlin length: prefer 45', absolute max 53'.
- Algorithm tries to maximize piece length up to the max, then suggests 2-3 ranked layout options.
- ALL roofs are single slope. There are NEVER two-pitched (gable) roofs.

### 2.2 C-Purlin Piece Lengths
- Pieces break cleanly at rafter locations. Two C-purlins butt end-to-end over the rafter.
- Connection at rafter: one P1 clip bridges both purlin ends — 4 TEK screws per purlin side = 8 total per joint. At the last rafter, 8 screws into one purlin.
- **No-overhang end pieces**: extend 4" past the outside face of the end rafter for the endcap, plus 4" for the half-rafter = 8" total past rafter center.
- **Overhang end pieces**: extend past the end rafter by the overhang distance (typically 1 parking space width).
- **Example (40'x100', 20' bays, C-purlins)**: 3 groups — 9 @ 30' + 9 @ 40' + 9 @ 30' = 100' coverage.

### 2.3 Z-Purlin Piece Lengths — Alternating Lapped Splice Algorithm

**Core Principle:** Splices alternate sides of consecutive rafters so that every rafter has a continuous (unspliced) purlin running over it. This provides structural continuity at all support points.

**Core Rules (fixed for all projects):**
- Splice type: Always 6" lap (overlap), user-configurable. 8 TEK screws per lap.
- Splice offset: Each splice center is exactly 6' from the nearest rafter.
- **Splice alternation**: Starting from R2, splices alternate between 6' BEFORE a rafter and 6' AFTER a rafter. First splice goes 6' before R2, second goes 6' after R3, third goes 6' before R4, and so on.
- The 6" lap is included in each piece's cut length. Adjacent pieces physically overlap by 6" at each splice.
- Maximum piece length: prefer 45', absolute max 53'.
- Goal: Every rafter has continuous purlin coverage (no splice at or near a rafter).

**Splice Position Algorithm:**
1. Gather inputs: rafter positions R[], building length L, overhang distance OH.
2. Walk rafters R2 through R(n-1), skipping R1 and R(last):
   - Odd splice (1st, 3rd, 5th...): position = R[i] − 6'  (6' BEFORE rafter)
   - Even splice (2nd, 4th, 6th...): position = R[i] + 6'  (6' AFTER rafter)
3. This creates alternating LONG and SHORT pieces.

**Piece Length Formulas (B = bay width, lap = 6" = 0.5'):**
| Piece Type     | Formula                           | B=36'     | B=24' (short bay) |
|----------------|-----------------------------------|-----------|--------------------|
| End piece      | OH + B − 6' + lap/2              | 42'-3"    | 30'-3"             |
| Long piece     | B + 6' + 6' + lap                | 48'-6"    | 36'-6"             |
| Short piece    | B − 6' − 6' + lap                | 24'-6"    | 12'-6"             |

- **End piece**: covers from building edge through overhang to first splice (OH + distance to first splice + 3" half-lap)
- **Long piece**: spans from one splice, across a rafter, to the next splice on the far side (rafter + 6' each way + 6" lap)
- **Short piece**: sits in the middle of a bay between two splices (bay − 12' + 6" lap)
- **Bridge piece** (across short bay): same as long piece formula but uses the short bay width

**Verification:** Total material = sum of all piece lengths. Total coverage after laps = L.
Formula: L = sum(piece_lengths) − (number_of_splices × lap). This must equal building length.

**No-overhang end pieces**: extend 4" past the outside face of the end rafter for endcap, plus 4" for the half-rafter = 8" total past rafter center. Purlins CANNOT go more than 8" past the center of the end rafter when overhang is off.
**Overhang end pieces**: extend up to 1 parking space width past the end rafter (user-configurable).

**Example 1 (35'×408', 12' spaces, 36' max bays, 1-space overhang, Z-purlins, 6" lap):**
- Rafters: R1=12, R2=48, R3=84, R4=120, R5=156, R6=192, R7=216, R8=252, R9=288, R10=324, R11=360, R12=396
- Bays: 10×36' + 1×24' (short bay between R6–R7)
- Splice centers: 42, 90, 114, 162, 186, 222, 246, 294, 318, 366
  (alternating: −6 from R2, +6 from R3, −6 from R4, +6 from R5, −6 from R6, +6 from R7, −6 from R8, +6 from R9, −6 from R10, +6 from R11)
- Pieces (11 per purlin line):
  1. 42'-3" (end) — 0' to 42.25'
  2. 48'-6" (long) — 41.75' to 90.25'
  3. 24'-6" (short) — 89.75' to 114.25'
  4. 48'-6" (long) — 113.75' to 162.25'
  5. 24'-6" (short) — 161.75' to 186.25'
  6. 36'-6" (bridge/long across short bay) — 185.75' to 222.25'
  7. 24'-6" (short) — 221.75' to 246.25'
  8. 48'-6" (long) — 245.75' to 294.25'
  9. 24'-6" (short) — 293.75' to 318.25'
  10. 48'-6" (long) — 317.75' to 366.25'
  11. 42'-3" (end) — 365.75' to 408'
- Verify: 42.25+48.5+24.5+48.5+24.5+36.5+24.5+48.5+24.5+48.5+42.25 = 413'. Minus 10 splices × 0.5' = 408' ✓
- Length groups: 2×42'3" + 4×48'6" + 4×24'6" + 1×36'6" = 4 distinct cut lengths
- BOM per line: 11 pieces. × 8 purlin lines = 88 pieces total.

**Example 2 (40'×100', 20' bays, 10' overhang, Z-purlins, 6" lap):**
- Rafters: R1=10, R2=30, R3=50, R4=70, R5=90
- Bays: 4×20'
- Splice centers: 24 (R2−6), 56 (R3+6)
- Pieces (3 per line):
  1. 36'-3" (end) — 0' to 36.25' (covers OH + first bay + 6' past R2 + 3" half-lap)
  2. 28'-6" (short) — 35.75' to 64.25'
  3. 36'-3" (end) — 63.75' to 100'
- Verify: 36.25+28.5+36.25 = 101'. Minus 2 splices × 0.5' = 100' ✓

### 2.4 Building Length Calculation (No Overhang)
Total building length = rafter-center-to-rafter-center span + (half-rafter + endcap) × 2

Example: 6 spaces × 9' = 54' rafter span. Building = 54' + (4" + 4") × 2 = 55'-4".

Purlin groups for this example (C-purlin, 18' max bay):
- Group 1 (end): 4" endcap + 4" half-rafter + 18' bay = 18'-8"
- Group 2 (middle): 18' center-to-center = 18'-0"
- Group 3 (end): 18' bay + 4" half-rafter + 4" endcap = 18'-8"
- Total: 18'-8" + 18'-0" + 18'-8" = 55'-4"

### 2.5 Uneven Bay Sizes
- Allowed. Smaller bays go on the ends. If there are multiple short bays, distribute one on each end.
- Flag a warning if any purlin piece is less than 8' long.

---

## 3. Rafter Positions

### 3.1 Standard Mode
- Rafters land on parking space lines (every N feet where N = space width).
- Bay size = number of spaces between structural rafters × space width.
- Max bay size is user-configurable; the BOM determines how many spaces per structural bay.
- **Example**: 100' building, 10' parking spaces, 20' max bay → rafters at 10', 30', 50', 70', 90' (5 rafters) with 10' overhangs on each end.

### 3.2 Solar Mode
- Rafters still land on parking space lines when the building is over a parking lot.
- If no parking (pure structural solar array), rafter spacing is user-configurable for structural purposes.
- Panel row boundaries do NOT need to align with rafter positions.
- The building length is derived from: panels_along × panel_length + (panels_along - 1) × gap + 2 × endcap_clearance.

### 3.3 Rafter Count
- Determined by: building length ÷ max bay size, constrained to land on space lines.
- Minimum 2 rafters (1 bay). A 36' building with 9' spaces and 36' max bay = 2 rafters, 1 bay.
- In this case, each purlin is the full building length (no joints).

---

## 4. Purlin Facing Direction (Z-Purlins and C-Purlins)

### 4.1 Facing Pattern — C-Purlins (Top View, Eave at Left)
- C-purlins alternate facing direction in pairs.
- **Even count (e.g., 8)**: `[ ] [ ] [ ] [ ]` — P1 faces `[` at eave, pairs face TOWARD each other `[ ]`.
- Between a pair: flanges face each other (smaller gap for P1 plates).
- Between pairs: flanges face away from each other (wider gap).
- This creates the small-big-small-big P1 plate spacing pattern on the rafter.

### 4.1b Facing Pattern — Z-Purlins (Top View, Eave at Left)
- Z-purlins also alternate in pairs, but the starting direction is **opposite** from C-purlins.
- **Even count (e.g., 8)**: `] [ ] [ ] [ ] [` — P1 faces `]` at eave, pairs face AWAY from each other `] [`.
- Same small-big-small-big P1 plate spacing, just mirrored from C.

### 4.2 Odd Purlin Count (Both Z and C)
- The eave purlin (#1, bottom of slope) and purlin #2 face the SAME direction.
- Pairs continue from #3 onward.
- The odd purlin is always absorbed at the eave end.
- **C-purlin odd (e.g., 9)**: `[ [ ] [ ] [ ] [ ]` — P1+P2 both `[`, then normal pairs.
- **Z-purlin odd (e.g., 9)**: `] ] [ ] [ ] [ ] [` — P1+P2 both `]`, then normal pairs.

### 4.3 Z-Purlin Nesting at Splices (Separate from Facing)
- The alternating facing direction is about the LINE-by-LINE pattern across the building width.
- At splice points (where two pieces on the SAME line overlap), one Z-purlin sits on top of the other and the flanges nest/stack together. The yellow-on-blue nesting drawing shows this.
- This nesting behavior is separate from the facing direction pattern.

### 4.4 Shop Drawing Requirement
- The purlin layout shop drawing MUST call out the facing direction for each purlin line.
- P1 plate positions must reflect the facing pattern (small gap / big gap alternation).
- Splice locations must also be called out.

---

## 5. Rafter Length and Purlin Type

### 5.1 C-Purlin Buildings
- Rafter length = building width (eave to eave).
- C-purlin flanges do not extend past the rafter.
- If decking does not overhang, rafter length = building width exactly.

### 5.2 Z-Purlin Buildings
- Rafter length = building width - (2 × top flange overhang).
- Default top flange overhang = 3.5" (user-overridable based on actual purlin spec).
- Example: 40' wide building → rafter = 40' - 3.5" - 3.5" = 39'-5".
- The decking/panels sit on the Z-purlin flange that extends past the rafter, so the covered area is still the full building width.

---

## 6. Solar Panel Mode

### 6.1 Panel Orientation
- **Landscape**: long side of panel parallel to building length. Panels share purlins across width. N panels across = N+1 purlin lines.
- **Portrait**: long side of panel perpendicular to building length (across width). Each panel gets its own 2 purlin lines, no sharing. N panels across = 2N purlin lines.

### 6.2 Panel Dimensions Drive Building Size
- Two sizing modes:
  - **Panel count mode**: user specifies panels_across × panels_along → building dimensions calculated.
  - **Fit-to-dimensions mode**: user specifies available space → algorithm calculates how many panels fit. Report dummy panel count needed to fill the space in both portrait and landscape.

### 6.3 Panel Gap
- Default 0.25" between all panels.
- User can set separate width-wise and length-wise gap values.

### 6.4 Mounting
- Through-bolted to purlins: 4 bolt stacks per panel (stainless steel bolt + washer + star washer + lock washer + nut).
- Bolt holes drilled in purlin top flange at mounting hole positions from panel spec.
- **Bolt holes are drilled in the shop and must appear on the cut list.**
- Mounting hole positions: user inputs distance from panel edge (e.g., 990mm for CS3K-P) and inset from panel short edge.
- Algorithm must validate that bolt holes fit on the purlin flange with minimum 0.5" clearance from flange edges.

### 6.5 Purlin Spacing in Solar Mode
- Purlin spacing is DICTATED by the panels — the user does NOT input purlin spacing in solar mode.
- **Landscape**: N+1 purlin lines for N panels. Purlins are positioned so the 1/4" gap between adjacent panels is CENTERED on the purlin's 3.5" top flange. Both adjacent panels' bolt holes (each 20mm / `mount_hole_from_edge_mm` inboard from their long edge) land on the same shared flange. Spacing ~ panel_width_mm (992mm), but purlin centers are at the midpoint of each panel gap, not at panel edges.
- **Portrait**: 2 purlin lines per panel (no sharing). Purlin positions are at the mounting hole INSET positions (`mount_hole_inset_mm`, default 250mm) measured from each SHORT edge of the panel. Intra-panel spacing = `panel_length_mm - 2 x mount_hole_inset_mm` (e.g., 2108 - 500 = 1608mm). **CRITICAL**: portrait uses `mount_hole_inset_mm` (250mm, from short edge), NOT `mount_hole_from_edge_mm` (20mm, from long edge).

### 6.6 Solar Overhang Rules
- **Front/back (eave sides, across width)**: panels CAN overhang both purlins and rafters.
- **Sides (building ends, along length)**: panels CANNOT overhang purlins. Panels CAN overhang rafters (since purlins extend past end rafters).
- **Portrait mode**: panels extend past the front/back outer purlins because the long side crosses the width and bolt holes land in the middle of the top purlin flange.
- **Landscape mode**: no side overhang past purlins.
- **Overhang on ends must be equal** on both ends of a solar building.

### 6.7 Solar Slope
- Default 5 deg (user-configurable).

### 6.8 Solar Hardware and BOM
- Add 4 bolt stacks per panel to the BOM (mounting hardware).
- Total bolt stacks = 4 x total_panels.
- Solar panels themselves appear on the BOM as an informational line item (quantity, dimensions, model) — typically customer-supplied, not included in material cost. Option to include panel cost if the customer wants Titan to purchase them.
- Mounting hardware (bolts, washers, star washers, lock washers, nuts) IS included in material cost.

### 6.9 Solar Panel Installation Pricing (TC Estimator)
- TC estimator adds a line item for solar panel installation: **$45 per panel** (default, user-overridable).
- Total install charge = $45 x total_panels.
- This covers labor for mounting panels to purlins — the panels themselves are customer-purchased separately (unless opted in).

### 6.10 Solar = NO Roofing (Spartan Rib)
- **Solar buildings have NO Spartan Rib roofing panels.** The solar panels themselves ARE the roof.
- Solar panels bolt directly through the purlins into pre-drilled holes in the solar panel frames.
- When solar mode is ON: remove all Spartan Rib coil, drip edge trim, and roofing fasteners from the BOM.
- The only "roofing" items are the solar panels and their bolt stacks.
- Endcaps, hurricane straps, sag rods, and all other structural components remain unchanged in solar mode.

### 6.11 Solar Carport Assembly Chain (Physical Structure)
The structural connection chain from ground to solar panel:

1. **Column** (vertical, sits at CENTER of rafter) → supports rafter
2. **Rafter** (horizontal/sloped rectangular beam) → spans building width
3. **P1/P2 Clip** (flat plate, **welded** to rafter) → connects purlin to rafter
   - P1 (interior): welded to TOP of rafter only
   - P2 (endcap): welded to rafter END FACE — rafter terminates at P2
4. **Z-Purlin** (web sits against clip, **tek screwed** through clip into web) → runs along building length
   - Bottom flange rests on rafter top
   - Top flange extends outward, providing the 3.5" panel mounting surface
5. **Solar Panel** (sits on purlin top flange, **through-bolted** at mounting hole positions)
   - Adjacent panels butt together with 1/4" gap CENTERED on the shared purlin's top flange
   - Each panel's bolt hole is 20mm (`mount_hole_from_edge_mm`) inboard from its long edge

Key details verified via 3D model review (2026-04-22):
- Rafter is a rectangular/box section (NOT an I-beam)
- Purlin top flanges overhang past the rafter (not the rafter extending past purlins)
- Tek screw hex heads are visible on the P1/P2 plate face
- P2 has 2 columns x 4 rows of tek screw holes in the portion above the rafter

---

## 7. Angled Purlins

### 7.1 Purpose
- Used when parking stalls are not perpendicular to the drive aisle.
- Common angles: 30 deg, 45 deg, 60 deg, 90 deg from the drive aisle.
- Drive aisle runs along building length (perpendicular to rafters).

### 7.2 Length Adjustment
- Angled purlins are longer than perpendicular purlins.
- Adjusted length = perpendicular_length / cos(angle from perpendicular).
- Example: 18' purlin at 15 deg from perpendicular → 18' / cos(15 deg) ~ 18'-7.5".

### 7.3 Rafter Contact
- Bottom flange sits on top of the rafter at an angle.
- Contact footprint on rafter = bottom_flange_width / sin(angle).
- Butt joint rule: still 4" of RAFTER width per purlin (unchanged by angle).

### 7.4 Connections at Angle
- Only P1 plates used at the top (no P2 at eave when angled).
- A 9" x 15" flat end cap plate (10GA) is welded across each rafter end to close the open C-sections. This is purely structural capping — no purlin connection.
- The first P1 plate on the rafter is positioned ~2-5/16" from the rafter end (center of plate to end of rafter).
- P1 plate weld positions along the rafter must account for the angled purlin spacing.

### 7.5 Solar + Angled Purlins
- Solar panels CAN go on angled purlins.
- Panels align with purlins (at the angle), not with the rafters.
- Panels are still square — they just rotate with the purlin angle.
- Bolt hole positions on the purlin remain the same.

### 7.6 All Purlin Pieces Same Length
- Even with angled purlins, all pieces on a given line are the same length.
- The purlins are staggered (offset along building length) but each piece is identical.

### 7.7 Stagger Calculation
- Each purlin line is offset along the building length by: `purlin_spacing x tan(angle_from_perpendicular)`.
- Despite the stagger, all purlin pieces still break at the CENTER of each rafter (same rule as perpendicular purlins).

---

## 8. P1, P2, and P3 Plates

### 8.1 P1 Plates (Interior)
- Used at every INTERIOR purlin-to-rafter connection (i.e., not the eave purlins).
- **Physical description**: A flat vertical plate welded to the TOP of the rafter only. The Z-purlin's web sits against the plate. Tek screws (with hex heads) go through the P1 plate into the purlin web, locking the purlin to the rafter. The purlin's bottom flange rests on the rafter top flange. The purlin's top flange extends outward from the web, providing the mounting surface for solar panels or decking.
- **C-purlin at P1**: The P1 clip bridges BOTH butt-joint purlin ends. 4 TEK screws per purlin side = 8 total per connection. At the LAST rafter (only one purlin present), all 8 screws go into that one purlin.
- Material: 10GA.
- Position on rafter depends on purlin layout.
- **Count per rafter (perpendicular purlins)**: `n_purlin_lines - 2` (the 2 eave purlins get P2 plates instead).
- **Count per rafter (angled purlins)**: `n_purlin_lines` (all positions get P1, including the 2 eave positions, since P2 cannot be used at an angle). Plus 2 endcap plates per rafter.
- **Total P1 plates**: P1_per_rafter x n_rafters.
- **Fasteners**: 8 tek screws per P1 connection total.

### 8.2 P2 Plates (Eave)
- Used only at the eave (first and last purlin on the rafter) for PERPENDICULAR purlins.
- **Physical description**: A flat vertical plate welded to the rafter END FACE at the building end. The P2 extends from below the rafter up above it. The upper portion (above the rafter top) provides the surface for the purlin web to tek screw into. The rafter TERMINATES at the P2 plate — the rafter does not extend past it. The purlin's bottom flange rests on the rafter top, and the web sits against the P2's upper extension.
- Material: 10GA (same as P1).
- **Count per rafter (perpendicular)**: 2 (one at each eave end).
- **Exception — rafter splice**: If the rafter is spliced (length > 53'), the splice plate occupies the connection point. No P2 plate at that position — the rafter splice plate takes priority.
- When purlins are angled, P2 is NOT used — all positions get P1 plates instead, and a separate 9" x 15" end cap plate (10GA) closes the rafter ends.
- Solar buildings with perpendicular purlins still use normal P2 plates — the endcap plate is only needed when purlins are angled.

### 8.3 P3 Plates (Column-to-Rafter)
- P3 plates are the column-to-rafter connection. They are NOT purlin-related.
- **2 per column-rafter connection**: one welded to the top of the column, one welded to the bottom of the rafter.
- Covered in detail in the interactive rafter shop drawings.
- Visible as maroon elements in the CAD layout drawings.

### 8.4 Purlin Type and Facing
- Neither Z vs C nor facing direction changes which plate type (P1 vs P2) is used.
- Facing direction only affects WHERE on the rafter the plate is welded.

### 8.5 Plate Dimensions and Gauge Summary
- **P1 plates**: 10GA (dimensions per existing rafter interactive drawing specs)
- **P2 plates**: 10GA x 9" wide x 24" long, G90 galvanized. 8 x 1/4" diameter holes for eave purlin attachment.
- **Rafter end cap plate** (angled purlins only): 10GA, 9" x 15" flat

### 8.6 Purlin Splice Connection (at Rafter)
- **Z-Purlins**: The splice IS the 6" lap overlap. Two Z-purlins nest on top of each other (same direction) in the overlap zone. 8 TEK screws per splice. No separate splice piece needed. End groups straddle the first two rafters + 6ft extension past the rafter. Interior splices may skip one full bay. See S2.3 for the production-ready splice algorithm.
- **C-Purlins**: C-purlins butt-joint at the rafter. The P1 plate bridges both ends — 4 TEK per side = 8 total. No overlap, no separate splice piece.

---

## 9. Coil and Material Specs

### 9.1 Purlin Coil (Z and C)
- Both Z-purlins and C-purlins use the SAME coil: 20.125" wide, 12GA, G90 galvanized.
- Same lbs/ft, same coil price. The only difference is the roll-forming profile.
- **Weight**: 7.43 lbs/ft (verified against coil cross-section calc: 20.125" x 0.105" = ~7.35-7.41 base + G90 coating).
- Cost per foot = lbs/ft x coil price per lb = 7.43 x coil_price_per_lb.

### 9.2 Purlin Cross-Section Dimensions
- Web height: 12" (currently the only size roll-formed; user-configurable for future use)
- Top flange width: 3.5"
- Bottom flange width: 3.5"
- Lip length: 0.75" (at flange ends)
- Gauge: 12GA (currently the only gauge roll-formed; user-configurable for future use)
- **WARNING**: Changing purlin depth requires a different coil width. If the user changes from 12", the system must warn and prompt for new coil width and specifications.
- The U-channel endcap internal dimension must match whatever purlin depth is chosen.
- These dimensions are needed for bolt hole clearance validation in solar mode (S6.4 requires 0.5" minimum from flange edge to bolt hole center).

### 9.3 Rafter End Cap Plate (Angled Purlins Only)
- When purlins are ANGLED (not perpendicular), a 9" x 15" flat plate (10GA) is welded across each rafter end.
- Purpose: closes the open C-section ends where P2 plates would normally go but can't because purlins don't align with the rafter end.
- Quantity: 2 per rafter (one each eave end).
- NOT needed for solar buildings with perpendicular purlins — those still use P2 plates normally.
- When combined with solar panels + angled purlins, the endcap plate is BELOW the panel line (no interference — panels sit on purlin flanges above the rafter).
- This is DIFFERENT from the U-channel endcap (which caps purlin ends on building ends).

### 9.4 U-Channel Endcaps (Building Ends)
- U-channel endcaps are used on ALL buildings (standard and solar) at both building ends.
- The endcap goes on the OUTSIDE of the purlins at each building end, UNDER the Spartan Rib panels (non-solar) or under the solar panels.
- **Profile**: U-channel (no lips), 4" flanges x 12" inside web dimension, same gauge as purlins (12GA), G90.
- **Length**: Same split logic as sag rods — max piece length 25', split at purlin locations, pieces overlap each other on the purlin flanges.
- **Connection**: 2 TEK screws per purlin-endcap connection (top and bottom of endcap at each purlin).
- **Quantity**: 2 runs per building (one each end). Each run may be multiple pieces if the building width exceeds 25'.
- The endcap is NOT affected by solar mode — it's always present.

### 9.5 No Eave Strut — Front/Back Purlins ARE the Eave
- There is NO separate eave strut on any building type.
- The front and back purlins (first and last purlin lines on the slope) serve as the eave.
- The BOM should NOT include a separate "eave strut" line item.
- This applies to ALL buildings — standard, solar, angled, or otherwise.

---

## 10. Sag Rods

### 10.1 What They Are
- Sag rods are 2"x2" angle iron, roll-formed from 4" wide 16GA coil.
- They are NOT round rods — they are formed angle.
- They thread through / attach to purlin webs to prevent purlins from rolling.

### 10.2 Orientation and Placement
- Sag rods run PARALLEL to the rafters (eave to ridge direction, perpendicular to purlins).
- They are placed at parking space line intervals along the building length.
- **Example**: 20' bays with 10' parking spaces → 1 sag rod per bay at the 10' mark = 1 sag rod between each pair of rafters.
- In a 30' bay with 10' parking: 2 sag rods per bay (at 10' and 20').
- Parking space width is a user INPUT — not fixed at 10'.

### 10.3 Piece Splitting
- Max sag rod piece length: 25'.
- Split at a purlin location for manageable handling.
- The two halves overlap on the purlin's BOTTOM flange at the split point.
- **Example (40' wide building)**: Each sag rod splits into 2 pieces at a purlin near the midpoint. Front piece: 20'. Back piece: 20'-3-1/2" (slightly longer due to single-slope roof pitch). 4 sag rods x 2 pieces = 8 pieces total.

### 10.4 Fasteners
- 2 TEK screws per sag-rod-to-purlin crossing (underside attachment, no pre-punch needed).
- Total crossings = n_sag_rods x n_purlin_lines.

### 10.5 Independence
- Sag rods do NOT affect purlin layout, spacing, or piece-break logic.
- They are a completely independent system — just hole locations on the purlin web.

---

## 11. Hurricane Straps

### 11.1 Placement
- Hurricane straps go on the SECOND row of purlins from BOTH the eave AND the ridge.
- On a 40' wide building with 5' purlin spacing (9 purlin lines): second row from eave = purlin line 2, second row from ridge = purlin line 8.
- **2 straps per rafter at each of the two purlin rows** (one on each side of the rafter).
- Total per rafter: 2 (eave-side row) + 2 (ridge-side row) = 4.
- **Total = 4 x n_rafters.** Example: 5 rafters x 4 = 20 hurricane straps.

### 11.2 Physical Connection
- Hurricane straps connect from the BOTTOM of the rafter to the BOTTOM FLANGE of the purlin.
- They prevent uplift of the purlin from the rafter during high wind events.

### 11.3 Solar Mode
- Hurricane strap rules are UNCHANGED for solar buildings. Same count, same placement.

---

## 12. Roofing — Spartan Rib Panels (Non-Solar Only)

### 12.1 Panel Specs
- **Spartan Rib** by Structures America.
- Coverage width: 35.79".
- Rib height: 1-1/2" (trapezoidal on 7.16" center).
- Available gauges: 29, 26, 24, 22, 20, 18, 16.
- Finishes: PVDF and Acrylic-Coated Galvalume.
- Min length: 5'. Max recommended: 45'.
- Panel cut angles: 90 deg, 30 deg, 60 deg.

### 12.2 Fastening
- Panels attach to the TOP of the purlin flange.
- Fasteners for steel: #12-14 XL Self Drilling Screw.
- Trim fastener: 1/4"-14 x 7/8" XL Stitch Screw.
- See Spartan Rib data sheet for end-of-panel vs field-of-panel fastening patterns.

### 12.3 Panel Count and Splitting
- Panel count along building length = ceiling(building_length_ft / (35.79 / 12)).
- Each panel run is split into 2 pieces at a purlin near the midpoint of the rafter width.
- **Example (40'x100')**: 100' / 2.9825' = 33.52 → 34 panel runs. Each splits into front piece (20') and back piece (20'-3-1/2" due to slope). Total: 34 + 34 = 68 pieces.
- The 3-1/2" difference between front and back pieces is because the single-slope roof makes one half slightly longer along the slope than the horizontal measurement.

### 12.4 Solar Buildings
- **NO Spartan Rib panels on solar buildings.** Solar panels ARE the roof.
- Remove all roofing coil, drip edge, and roofing fasteners from BOM when solar is ON.

---

## 13. Drip Edge Trim

### 13.1 Specs
- 2"x2" drip edge profile.
- **Purchased item** — comes in 10' sticks (NOT roll-formed from coil).
- Pieces overlap/stack 3" at joints.

### 13.2 Placement
- Goes OVER the ends of the Spartan Rib panels on ALL four sides of the building (eave, ridge, and both building ends).
- **Non-solar buildings only.** No drip edge on solar buildings (no Spartan Rib panels to trim).

### 13.3 Quantity Calculation
- Perimeter of building = 2 x (length + width).
- Pieces needed per side = ceiling(side_length / (10' - 0.25')) accounting for 3" overlap.
- Total sticks = sum of all four sides.

---

## 14. Girts and Wall Panels

### 14.1 Girt Rules
- Girts use the same length rules as roof purlins (same piece break logic at rafter positions).
- Girt spacing: default 5' on-center, user-configurable.
- Girt rules do NOT change between solar and non-solar buildings.
- Girts are the same material as purlins (20.125" 12GA G90) — just installed vertically on columns instead of horizontally on rafters.
- Girts get their OWN separate interactive builder page (not a tab within purlin builder). Same material, same piece-break logic, but separate page and separate PDF output. Side elevation view showing girts on columns.

### 14.2 Wall Panels
- Solar carports may or may not have walls.
- If walls are included, wall panel rules are the same as non-solar buildings.
- SA estimator inputs for walls (back wall, end walls, side walls) still apply in solar mode.

---

## 15. Panel Type Consistency

### 15.1 One Panel Type Per Project
- All solar panels on a building must be the same type (same dimensions, same mounting holes).
- All buildings in a project also use the same panel type.
- The user enters panel specs once and they apply project-wide.

---

## 16. Roofing Panels vs Purlins

### 16.1 Independence
- Roofing panel piece breaks are NOT affected by purlin piece breaks.
- Roofing panels only care about WHERE purlins land (they must bear on a purlin), not how the purlins themselves are spliced.
- Purlin piece-break logic and roofing panel layout are independent systems.

---

## 17. BOM Line Items for Purlins

### 17.1 Purlin Breakdown
- The BOM should show purlins broken out by piece length, NOT as a single total LF line.
- Example: "Purlin 18'-8" x 24 pcs, Purlin 18'-0" x 12 pcs" rather than "Purlins — 1,440 LF".
- Each distinct piece length gets its own BOM line item with quantity and total LF.
- Splice purlins (short pieces at rafter connections) are a separate line item from main purlins.
- Girts get their own set of piece-length line items (same format, separate section).

---

## 18. Cost Comparison

### 18.1 Four Options
The purlin layout drawing compares all four combinations:
1. Landscape + C-Purlin
2. Landscape + Z-Purlin
3. Portrait + C-Purlin
4. Portrait + Z-Purlin

### 18.2 Comparison Metrics
- Total linear feet of purlin material per option.
- Total piece count per option.
- Estimated cost (LF x cost-per-foot for each purlin type).
- Recommended option = lowest cost.

### 18.3 Building Size Held Constant
- When comparing portrait vs landscape, the building dimensions stay the same.
- The comparison shows how many panels fit and the purlin layout for each option within the same footprint.

---

## 19. Error Conditions and Warnings

### 19.1 Errors (Block Calculation)
| Condition | Message |
|---|---|
| Bay size > max purlin length | "Bay size exceeds max purlin length. Add intermediate rafters to reduce bay size." |
| Z-extension > bay size | "Z-purlin extension exceeds bay size. Reduce extension or increase bay spacing." |
| Purlin flange too narrow for shared panels | "Panel gap + bolt clearance exceeds purlin flange width. Use a wider purlin or reduce gap." |
| Bolt hole outside purlin flange | "Mounting hole position falls outside purlin flange. Check panel spec dimensions." |

### 19.2 Warnings (Allow but Flag)
| Condition | Message |
|---|---|
| Purlin piece < 8' long | "Purlin piece is less than 8'. Consider adjusting bay sizes." |
| Bolt hole within 0.5" of C-purlin butt joint | "Bolt hole is within 0.5\" of a butt joint. Structurally OK but verify with engineer." |
| Bolt hole through Z-purlin overlap zone | "Bolt hole passes through splice overlap — drilling through 2 purlins. This is acceptable." |
| Dummy panels needed in fit-to-dimensions | "N dummy panels needed to fill the space (X in portrait, Y in landscape)." |
| Uneven bay sizes | "Bay sizes are not equal. Shorter bays placed at building ends." |

---

## 20. SA Estimator Input Summary

### 20.1 Standard Mode (Already Exists)
- Building length, width, clear height
- Max bay size, space width, number of spaces
- Purlin type (Z/C), purlin spacing (default 5' O.C. for non-solar)
- Overhang mode (none / 1 space)
- All structural inputs (columns, rebar, footings, etc.)

### 20.2 New Inputs Needed for Standard Purlin Layout
- Max purlin length (default 45', cap 53')
- Z-purlin extension past rafter (default 6')
- Z-purlin eave flange overhang (default 3.5")
- Lap splice length (default 6", user-configurable)
- Cost per foot: C-purlin and Z-purlin

### 20.3 New Inputs Needed for Solar Mode
- Solar mode toggle (changes which inputs are shown)
- Panel width (mm)
- Panel length (mm)
- Mounting hole distance from panel edge (mm)
- Mounting hole inset from panel short edge (mm)
- Panels across / panels along (or fit-to-dimensions)
- Gap width and gap length (default 0.25")
- Panel orientation (landscape / portrait / best-fit comparison)
- Slope (default 5 deg for solar)
- Rafter spacing override (when no parking stalls)
- Option to include solar panel material cost in BOM (default: off, customer-supplied)

### 20.4 Inputs That Remain in Solar Mode
- Reinforced columns and rafters
- Footing depth, embedment, column buffer
- Column rebar size, beam rebar size
- Column mode (auto/spacing/manual)
- Cut allowance
- Wall panels and girts (optional)
- Max rebar stick, end gap, splice location override
- Angled purlins (angle from perpendicular)

---

## 21. Component Weights, Gauges, and Coil Specifications

### 21.1 Weight Table — All Components

| Component | Gauge | Material | Coil Width | Profile | Dimensions | Weight | Unit |
|-----------|-------|----------|-----------|---------|------------|--------|------|
| Z-Purlin | 12GA | G90 Galv | 20.125" | Z 12"×3.5"×¾" | — | 7.43 | lb/ft |
| C-Purlin | 12GA | G90 Galv | 20.125" | C 12"×3.5"×¾" | — | 7.43 | lb/ft |
| Sag Rod | 16GA | G90 Galv | 4" | 2"×2" Angle | — | 0.8656 | lb/ft |
| Endcap (U-Channel) | 12GA | G90 Galv | 20.125" | U 4.125"×12.125" | — | 7.43 | lb/ft |
| Roof Decking | 29GA | G50 Galv | 48" | Spartan Rib | 36" panel / 33" coverage | 2.89 | lb/ft |
| P1 Interior Clip | 10GA | G90 Galv | 6" | Flat plate | 6"×10" | 2.41 | lb/ea |
| P2 Eave Plate | 10GA | G90 Galv | 9" | Flat plate | 9"×24" | 8.44 | lb/ea |
| P3 Column Plate | ¾" | — | — | Flat plate (purchased) | 14"×26" | 77.34 | lb/ea |
| Hurricane Strap | 10GA | G90 Galv | 1.5" | Flat strap | 1.5"×28" | 1.68 | lb/ea |

### 21.2 Coil-to-Weight Derivations
- P1: 6" coil @ 2.89 lb/ft → each piece is 10" = 10/12 ft → 2.89 × (10/12) = 2.41 lb/ea
- P2: 9" coil @ 4.22 lb/ft → each piece is 24" = 2 ft → 4.22 × 2 = 8.44 lb/ea
- H-Strap: 1.5" coil @ 0.72 lb/ft → each piece is 28" = 28/12 ft → 0.72 × (28/12) = 1.68 lb/ea
- P3: Purchased plate, not roll-formed. 77.34 lb/ea (¾" thick steel, 14"×26").

### 21.3 P3 Column Plate Details
- ¾" × 14" × 26" flat steel plate.
- **Purchased piece by piece** — NOT roll-formed from coil.
- 2 per column-rafter connection (one welded to column top, one to rafter bottom).
- Total per building: 2 × number of rafters.
- At 77.34 lb each, P3 plates are the heaviest individual piece in the secondary member system.

### 21.4 Weight Calculation Formulas
- **Purlins**: total_material_LF_per_line × num_purlin_lines × 7.43 lb/ft
- **Sag Rods**: sum(piece_lengths × piece_counts × num_sag_rod_positions) × 0.8656 lb/ft
- **Endcaps**: sum(piece_lengths × piece_counts × 2 ends) × 7.43 lb/ft
- **Decking**: sum(piece_lengths × piece_counts × num_strips) × 2.89 lb/ft
- **Hardware**: (qty_P1 × 2.41) + (qty_P2 × 8.44) + (qty_P3 × 77.34) + (qty_HStrap × 1.68)
- **TEK screws**: negligible weight, not included in weight calculations

---

## 22. Secondary Member Piece Breaking — Equal-Length Rule

### 22.1 Core Rule
When sag rods, endcaps, or decking panels must be broken into multiple pieces (total length > max piece length), pieces should be **as close to equal length as possible**.

### 22.2 Algorithm
1. Calculate minimum number of pieces needed: `numPieces = ceil(totalLength / maxLength)`
2. Calculate ideal piece length: `idealLength = totalLength / numPieces`
3. Find the best split point(s) by snapping to the nearest purlin Y position that is closest to the ideal split location
4. Verify all resulting pieces are ≤ maxLength
5. If a candidate split point would create a piece > maxLength, skip it and try the next closest

### 22.3 Examples
| Total Length | Max Piece | Num Pieces | Split At | Resulting Pieces |
|-------------|-----------|------------|----------|------------------|
| 35' | 30' | 2 | P @ 15' | 15' + 20' |
| 50' | 30' | 2 | P @ 25' | 25' + 25' |
| 75' | 30' | 3 | P @ 25', 50' | 25' + 25' + 25' |
| 90' | 30' | 3 | P @ 30', 60' | 30' + 30' + 30' |
| 100' | 30' | 4 | P @ 25', 50', 75' | 25' + 25' + 25' + 25' |

### 22.4 Why Equal-Length
- **Handling**: equal pieces are easier to manage in the shop and on the truck
- **Material efficiency**: avoids short scrap pieces that are hard to use
- **Symmetry**: equal pieces look cleaner on the plan view drawing
- The old approach (greedy fill to max, then short remainder) produced pieces like 30' + 5' which are impractical

### 22.5 Overlap at Split Points
- Sag rods and endcaps: pieces overlap on the purlin at the split point (no gap between them)
- Decking: pieces overlap at purlin positions per the end overlap input (default 6")

---

## 23. Solar Panel Mode — Building Dimension Rules (Expanded)

### 23.1 Panels Drive Building Size (Default Mode)
- User selects: panel dimensions, orientation (portrait/landscape), panel count across × along
- Building width = f(panels_across, panel dimension in that direction, gaps)
- Building length = f(panels_along, panel dimension in that direction, gaps) + overhangs
- Overhangs are ADDED to the panel array dimensions — rafters still land on parking stall lines

### 23.2 Fit-to-Dimensions Mode (Alternate)
- User specifies available building footprint
- Algorithm calculates how many panels fit in portrait and landscape
- Reports panel counts and any "dummy panel" spaces needed to fill the footprint

### 23.3 Purlin Spacing — Panel-Driven
- In solar mode, purlin spacing is NOT a fixed value (not 5' O.C.)
- **Portrait**: 2 purlin lines per panel row. Purlin positions = mounting hole inset from each short edge of the panel. No sharing between panels.
- **Landscape**: N+1 purlin lines for N panels across. Middle purlins are shared between adjacent panels. Purlin centers align with the gap between panels.

### 23.4 Rafter Length — Orientation-Dependent
- Rafters must be long enough for the top purlin flange to center on the bolt holes
- **Portrait**: rafter length changes because the panel's long dimension crosses the building width, and bolt holes need to land in the center of the outer purlin flanges
- **Landscape**: rafter length is determined by panel width × panels_across + gaps, adjusted for flange centering
- This is different from standard mode where rafter length = building width − 2 × flange overhang (Z) or = building width (C)

### 23.5 Bolt Hole Positions on Purlins
- Each solar panel has **4 mounting holes** (Ø14×9 slotted), one near each corner of the frame
- Bolt holes are drilled in the shop and MUST appear on the purlin cut list / shop drawing
- **Landscape — interior/shared purlin**: the ¼" gap between adjacent panels is centered on the purlin's 3.5" top flange. Each panel's bolt hole lands at (gap/2 + hole_from_panel_long_edge) from purlin center. Two bolts per purlin flange — one from each adjacent panel.
- **Landscape — end purlin**: only one panel's holes. Bolt is centered on the purlin flange.
- **Portrait**: each panel has its own 2 purlin lines (no sharing). Bolt holes centered on purlin flange.
- Bolt holes must maintain minimum 0.5" clearance from purlin flange edges

### 23.6 Reference Panel — Canadian Solar CS3K-P (KuPower 295-320W)
- **Overall dimensions**: 1675mm × 992mm × 35mm (65.9" × 39.1" × 1.38")
- **Weight**: 18.5 kg (40.8 lbs)
- **Frame**: Anodized aluminum alloy, 35mm depth, ~24mm rail width
- **Inner width**: 944mm (between frame rails)
- **Mounting holes**: Ø14×9mm slotted holes, 4 per panel (one near each corner)
- **Hole inset from short edge**: 342.5mm (990mm between hole pairs, centered vertically)
- **Hole inset from long edge**: ~20mm (on frame rail, per §6.5 mount_hole_from_edge_mm)
- **Grounding hole**: Ø5.25mm, 180mm from top edge
- **Cell arrangement**: 120 cells [2 × (10 × 6)], poly-crystalline
- **Front cover**: 3.2mm tempered glass

### 23.7 Building Dimension Formula (Solar, Panels Cover Everything)

**Building Length** (along the panel array):
```
Building Length = (panels_along × panel_dim_along) + ((panels_along - 1) × gap) + 2 × 4.125"
```
Where:
- `panel_dim_along` = 992mm (portrait) or 1675mm (landscape)
- `gap` = ¼" (6.35mm) default between panels
- `4.125"` = endcap U-channel on each building end
- Panels cover the ENTIRE building edge to edge (including over overhang areas)
- Overhangs on both building ends MUST be equal

**Building Width** (across the panel array):
```
Building Width = (panels_across × panel_dim_across)  + ((panels_across - 1) × gap)
```
Where:
- `panel_dim_across` = 1675mm (portrait) or 992mm (landscape)
- Rafter length is adjusted so purlin flanges center on bolt holes (see §23.4)

**Rafter positions**: Rafters still land on parking stall lines within the building length. The equal overhangs on each end ensure the panel array is centered between the first and last rafter.

### 23.8 Key Principle
Everything downstream of purlin spacing (splices, sag rods, endcaps, decking, weights, BOM) follows the SAME rules as standard mode. The only difference is:
1. How building dimensions are calculated (from panels instead of direct input)
2. How purlin spacing is determined (from panel mounting requirements instead of fixed O.C.)
3. Rafter length calculation (flange centering on bolt holes)
4. Bolt hole patterns on each purlin piece (fabrication detail)

---

*End of purlin rules reference.*
