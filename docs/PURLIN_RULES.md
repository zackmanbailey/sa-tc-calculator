# Purlin Rules Reference — TitanForge / Structures America

> Living document. Last updated: 2026-04-20
> Source: Design discussions between Zack (Titan Carports) and engineering team.

---

## 1. Purlin Types

### 1.1 C-Purlin
- Symmetric cross-section: web vertical, both flanges extend the same direction, lips curl inward.
- Butt-joint connection: two C-purlins meet at the CENTER of a rafter. Each purlin sits on half the rafter width (4" on an 8" rafter).
- C-purlins do NOT extend past the rafter at the eave. A 40' wide building with C-purlins has a 40' rafter.
- C-purlins alternate facing direction using the same rules as Z-purlins (see Section 4).

### 1.2 Z-Purlin
- Asymmetric cross-section: web vertical, top flange extends one direction, bottom flange extends the opposite direction. Lips at ~45° at flange ends.
- Overlap/splice connection: Z-purlins extend past the rafter by a configurable distance (default 4'). Where two Z-purlins overlap, there is a 6" lap. Splice holes go through BOTH purlins in the overlap zone.
- Z-purlin top flanges extend past the rafter at the eave. A 40' wide building with Z-purlins using 3.5" top flanges has a rafter length of 40' - 3.5" - 3.5" = 39'-5".
- The eave flange overhang dimension defaults to 3.5" but is user-overridable.

---

## 2. Purlin Layout Along Building Length

### 2.1 General Rules
- Every purlin LINE (across the building width) uses the SAME length pattern.
- Purlins must span at least 2 rafters.
- Maximum purlin length: user-configurable, default 45', hard cap 53'.
- Algorithm tries to maximize piece length up to the max, then suggests 2-3 ranked layout options.

### 2.2 C-Purlin Piece Lengths
- Pieces break at rafter centers. Each piece sits 4" on each rafter it touches at a joint.
- The 4" rule references the RAFTER width, not the purlin contact — this applies regardless of purlin angle.
- **No-overhang end pieces**: extend 4" past the outside face of the end rafter for the endcap, plus 4" for the half-rafter = 8" total past rafter center.
- **Overhang end pieces**: extend past the end rafter by the overhang distance (typically 1 parking space width).

### 2.3 Z-Purlin Piece Lengths
- Pieces extend past the rafter by the Z-extension distance (default 4', configurable).
- Where two Z-purlins meet, they overlap by 6".
- Splice holes go through both purlins in the overlap zone — must be shown on shop drawing.
- **No-overhang end pieces**: extend 4" past the outside face of the end rafter for endcap, plus 4" for the half-rafter = 8" total past rafter center. Purlins CANNOT go more than 8" past the center of the end rafter when overhang is off.
- **Overhang end pieces**: extend up to 1 parking space width past the end rafter (user-configurable).

### 2.4 Building Length Calculation (No Overhang)
Total building length = rafter-center-to-rafter-center span + (half-rafter + endcap) × 2

Example: 6 spaces × 9' = 54' rafter span. Building = 54' + (4" + 4") × 2 = 55'-4".

Purlin groups for this example (C-purlin, 18' max bay):
- Group 1 (end): 4" endcap + 4" half-rafter + 18' bay = 18'-8"
- Group 2 (middle): 18' center-to-center = 18'-0"
- Group 3 (end): 18' bay + 4" half-rafter + 4" endcap = 18'-8"
- Total: 18'-8" + 18'-0" + 18'-8" = 55'-4" ✓

### 2.5 Uneven Bay Sizes
- Allowed. Smaller bays go on the ends. If there are multiple short bays, distribute one on each end.
- Flag a warning if any purlin piece is less than 8' long.

---

## 3. Rafter Positions

### 3.1 Standard Mode
- Rafters land on parking space lines (every N feet where N = space width).
- Bay size = number of spaces between structural rafters × space width.
- Max bay size is user-configurable; the BOM determines how many spaces per structural bay.

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

### 4.1 Facing Pattern
- Z-purlins face in pairs with top flanges pointing AWAY from each other: `[ ]`
- Between a pair: bottom flanges face each other (small gap for P1 plates).
- Between pairs: top flanges face each other (wider gap).
- This creates the small-big-small-big P1 plate spacing pattern on the rafter.

### 4.2 Odd Purlin Count
- The eave purlin (#1, bottom of slope) and purlin #2 face the SAME direction.
- Pairs continue from #3 onward: #3←  #4←  then #5→  #6→  etc.
- The odd purlin is always absorbed at the eave end.

### 4.3 C-Purlins
- C-purlins alternate facing direction using the same rules as Z-purlins.
- The facing affects P1/P2 plate weld positions on the rafter.

### 4.4 Shop Drawing Requirement
- The purlin layout shop drawing MUST call out the facing direction for each purlin line.
- P1 plate positions must reflect the facing pattern (small gap / big gap alternation).

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
- Mounting hole positions: user inputs distance from panel edge (e.g., 990mm for CS3K-P) and inset from panel short edge.
- Algorithm must validate that bolt holes fit on the purlin flange with minimum 0.5" clearance from flange edges.

### 6.5 Purlin Spacing in Solar Mode
- Purlins spacing is DICTATED by the panels — the user does NOT input purlin spacing in solar mode.
- Landscape: spacing = panel short-side width (e.g., 992mm ≈ 3'-3").
- Portrait: spacing = mounting hole distance within each panel pair.

### 6.6 Solar Overhang Rules
- **Front/back (eave sides, across width)**: panels CAN overhang both purlins and rafters.
- **Sides (building ends, along length)**: panels CANNOT overhang purlins. Panels CAN overhang rafters (since purlins extend past end rafters).
- **Portrait mode**: panels extend past the front/back outer purlins because the long side crosses the width and bolt holes land in the middle of the top purlin flange.
- **Landscape mode**: no side overhang past purlins.
- **Overhang on ends must be equal** on both ends of a solar building.

### 6.7 Solar Slope
- Default 5° (user-configurable).

### 6.8 Solar Hardware
- Add 4 bolt stacks per panel to the BOM.
- Total bolt stacks = 4 × total_panels.

---

## 7. Angled Purlins

### 7.1 Purpose
- Used when parking stalls are not perpendicular to the drive aisle.
- Common angles: 30°, 45°, 60°, 90° from the drive aisle.
- Drive aisle runs along building length (perpendicular to rafters).

### 7.2 Length Adjustment
- Angled purlins are longer than perpendicular purlins.
- Adjusted length = perpendicular_length / cos(angle from perpendicular).
- Example: 18' purlin at 15° from perpendicular → 18' / cos(15°) ≈ 18'-7.5".

### 7.3 Rafter Contact
- Bottom flange sits on top of the rafter at an angle.
- Contact footprint on rafter = bottom_flange_width / sin(angle).
- Butt joint rule: still 4" of RAFTER width per purlin (unchanged by angle).

### 7.4 Connections at Angle
- Only P1 plates used at the top (no P2 at eave when angled).
- A different end cap plate caps the rafter ends instead of P2.
- P1 plate weld position on rafter must account for the angle.

### 7.5 Solar + Angled Purlins
- Solar panels CAN go on angled purlins.
- Panels align with purlins (at the angle), not with the rafters.
- Panels are still square — they just rotate with the purlin angle.
- Bolt hole positions on the purlin remain the same.

### 7.6 All Purlin Pieces Same Length
- Even with angled purlins, all pieces on a given line are the same length.
- The purlins are staggered (offset along building length) but each piece is identical.

---

## 8. P1 and P2 Plates

### 8.1 P1 Plates (Interior)
- Used at every interior purlin-to-rafter connection.
- Welded to the top of the rafter.
- Purlin web bolts to the P1 plate.
- Position on rafter depends on purlin facing direction (small gap / big gap pattern).

### 8.2 P2 Plates (Eave)
- Used only at the eave (end of rafter) for perpendicular purlins.
- When purlins are angled, P2 is NOT used — only P1 plates at the top, with a separate end cap plate on the rafter ends.

### 8.3 Purlin Type and Facing
- Neither Z vs C nor facing direction changes which plate type (P1 vs P2) is used.
- Facing direction only affects WHERE on the rafter the plate is welded.

---

## 9. Girts and Wall Panels

### 9.1 Girt Rules
- Girts use the same length rules as roof purlins (same piece break logic at rafter positions).
- Girt spacing: default 5' on-center, user-configurable.
- Girt rules do NOT change between solar and non-solar buildings.

### 9.2 Wall Panels
- Solar carports may or may not have walls.
- If walls are included, wall panel rules are the same as non-solar buildings.
- SA estimator inputs for walls (back wall, end walls, side walls) still apply in solar mode.

---

## 10. Cost Comparison

### 10.1 Four Options
The purlin layout drawing compares all four combinations:
1. Landscape + C-Purlin
2. Landscape + Z-Purlin
3. Portrait + C-Purlin
4. Portrait + Z-Purlin

### 10.2 Comparison Metrics
- Total linear feet of purlin material per option.
- Total piece count per option.
- Estimated cost (LF × cost-per-foot for each purlin type).
- Recommended option = lowest cost.

### 10.3 Building Size Held Constant
- When comparing portrait vs landscape, the building dimensions stay the same.
- The comparison shows how many panels fit and the purlin layout for each option within the same footprint.

---

## 11. Error Conditions and Warnings

### 11.1 Errors (Block Calculation)
| Condition | Message |
|---|---|
| Bay size > max purlin length | "Bay size exceeds max purlin length. Add intermediate rafters to reduce bay size." |
| Z-extension > bay size | "Z-purlin extension exceeds bay size. Reduce extension or increase bay spacing." |
| Purlin flange too narrow for shared panels | "Panel gap + bolt clearance exceeds purlin flange width. Use a wider purlin or reduce gap." |
| Bolt hole outside purlin flange | "Mounting hole position falls outside purlin flange. Check panel spec dimensions." |

### 11.2 Warnings (Allow but Flag)
| Condition | Message |
|---|---|
| Purlin piece < 8' long | "Purlin piece is less than 8'. Consider adjusting bay sizes." |
| Bolt hole within 0.5" of C-purlin butt joint | "Bolt hole is within 0.5\" of a butt joint. Structurally OK but verify with engineer." |
| Bolt hole through Z-purlin overlap zone | "Bolt hole passes through splice overlap — drilling through 2 purlins. This is acceptable." |
| Dummy panels needed in fit-to-dimensions | "N dummy panels needed to fill the space (X in portrait, Y in landscape)." |
| Uneven bay sizes | "Bay sizes are not equal. Shorter bays placed at building ends." |

---

## 12. SA Estimator Input Summary

### 12.1 Standard Mode (Already Exists)
- Building length, width, clear height
- Max bay size, space width, number of spaces
- Purlin type (Z/C), purlin spacing
- Overhang mode (none / 1 space)
- All structural inputs (columns, rebar, footings, etc.)

### 12.2 New Inputs Needed for Standard Purlin Layout
- Max purlin length (default 45', cap 53')
- Z-purlin extension past rafter (default 4')
- Z-purlin eave flange overhang (default 3.5")
- Cost per foot: C-purlin and Z-purlin

### 12.3 New Inputs Needed for Solar Mode
- Solar mode toggle (changes which inputs are shown)
- Panel width (mm)
- Panel length (mm)
- Mounting hole distance from panel edge (mm)
- Mounting hole inset from panel short edge (mm)
- Panels across / panels along (or fit-to-dimensions)
- Gap width and gap length (default 0.25")
- Panel orientation (landscape / portrait / best-fit comparison)
- Slope (default 5° for solar)
- Rafter spacing override (when no parking stalls)

### 12.4 Inputs That Remain in Solar Mode
- Reinforced columns and rafters
- Footing depth, embedment, column buffer
- Column rebar size, beam rebar size
- Column mode (auto/spacing/manual)
- Cut allowance
- Wall panels and girts (optional)
- Max rebar stick, end gap, splice location override
- Angled purlins (angle from perpendicular)

---

*End of purlin rules reference.*
