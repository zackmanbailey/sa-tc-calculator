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
- Overlap/splice connection: Z-purlins extend past the rafter by a configurable distance (default 6'). Where two Z-purlins overlap, there is a 6" lap. Splice holes go through BOTH purlins in the overlap zone.
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
- Pieces extend past the rafter by the Z-extension distance (default 6', configurable).
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
- A 9" × 15" flat end cap plate (10GA) is welded across each rafter end to close the open C-sections. This is purely structural capping — no purlin connection.
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
- Each purlin line is offset along the building length by: `purlin_spacing × tan(angle_from_perpendicular)`.
- Despite the stagger, all purlin pieces still break at the CENTER of each rafter (same rule as perpendicular purlins).

---

## 8. P1 and P2 Plates

### 8.1 P1 Plates (Interior)
- Used at every INTERIOR purlin-to-rafter connection (i.e., not the eave purlins).
- Welded to the top of the rafter. Material: 10GA.
- Purlin web bolts to the P1 plate.
- Position on rafter depends on purlin facing direction (small gap / big gap pattern).
- **Count per rafter (perpendicular purlins)**: `n_purlin_lines - 2` (the 2 eave purlins get P2 plates instead).
- **Count per rafter (angled purlins)**: `n_purlin_lines` (all positions get P1, including the 2 eave positions, since P2 cannot be used at an angle). Plus 2 endcap plates per rafter.
- **Total P1 plates**: P1_per_rafter × n_rafters.
- **Fasteners**: 8 tek screws per P1 connection (purlin-to-clip and P1 clip counts are the same thing — 8 screws total per connection, not 8+8).

### 8.2 P2 Plates (Eave)
- Used only at the eave (first and last purlin on the rafter) for PERPENDICULAR purlins.
- Material: 10GA (same as P1).
- **Count per rafter (perpendicular)**: 2 (one at each eave end).
- **Exception — rafter splice**: If the rafter is spliced (length > 53'), the splice plate occupies the connection point. No P2 plate at that position — the rafter splice plate takes priority.
- When purlins are angled, P2 is NOT used — all positions get P1 plates instead, and a separate 9" × 15" end cap plate (10GA) closes the rafter ends.
- Solar buildings with perpendicular purlins still use normal P2 plates — the endcap plate is only needed when purlins are angled.

### 8.5 Purlin Splice Connection (at Rafter)
- When two purlin pieces meet at a rafter (piece-break point), the splice uses a short purlin segment on top.
- The splice purlin sits ON TOP of the continuous purlin, centered over the rafter (boxed beam).
- **Fasteners**: 8 × #10 tek screws total (4 per side of the rafter center).
- The splice purlin must be the same depth and gauge as the main purlins.
- This detail replaces the older 4/S3.1 connection detail.
- In the BOM, splice purlins are a separate line item from main purlins.

### 8.3 Purlin Type and Facing
- Neither Z vs C nor facing direction changes which plate type (P1 vs P2) is used.
- Facing direction only affects WHERE on the rafter the plate is welded.

### 8.4 Plate Gauge Summary
- P1 plates: 10GA
- P2 plates: 10GA
- Rafter end cap plate (angled purlins only): 10GA, 9" × 15" flat

---

## 9. Coil and Material Specs

### 9.1 Purlin Coil (Z and C)
- Both Z-purlins and C-purlins use the SAME coil: 20.125" wide, 12GA, G90 galvanized.
- Same lbs/ft, same coil price. The only difference is the roll-forming profile.
- Cost per foot = lbs/ft × coil price per lb. These are the same number expressed two ways.

### 9.5 Purlin Cross-Section Dimensions (Standard 12")
- Web height: 12"
- Top flange width: 3.5"
- Bottom flange width: 3.5"
- Lip length: 0.75" (at flange ends)
- These dimensions are needed for bolt hole clearance validation in solar mode (§6.4 requires 0.5" minimum from flange edge to bolt hole center).

### 9.6 Purlin Depth
- Default purlin depth: 12".
- Purlin depth is a user-configurable option.
- **WARNING**: Changing the purlin depth requires a different coil width. If the user changes from 12", the system must warn them and prompt them to input the coil width and specifications for the non-standard depth.
- The U-channel endcap internal dimension must match whatever purlin depth is chosen.

### 9.2 Rafter End Cap Plate (Angled Purlins Only)
- When purlins are ANGLED (not perpendicular), a 9" × 15" flat plate (10GA) is welded across each rafter end.
- Purpose: closes the open C-section ends where P2 plates would normally go but can't because purlins don't align with the rafter end.
- Quantity: 2 per rafter (one each eave end).
- NOT needed for solar buildings with perpendicular purlins — those still use P2 plates normally.
- When combined with solar panels + angled purlins, the endcap plate is BELOW the panel line (no interference — panels sit on purlin flanges above the rafter).
- This is DIFFERENT from the U-channel endcap (which caps purlin ends on building ends).

### 9.3 U-Channel Endcaps (Building Ends)
- U-channel endcaps are used on ALL buildings (standard and solar) at both building ends.
- The endcap goes OVER the purlin ends — its internal dimension matches the purlin depth (e.g., 12" purlin = 12" internal endcap dimension).
- Profile: U-channel (no lips), same gauge as purlins (12GA), G90.
- Max length: 30'-4". If building width exceeds this, endcap must be spliced (lands on a purlin).
- Quantity: 2 per building (one each end).
- The endcap is NOT affected by solar mode — it's always present.

### 9.4 No Eave Strut — Front/Back Purlins ARE the Eave
- There is NO separate eave strut on any building type.
- The front and back purlins (first and last purlin lines on the slope) serve as the eave.
- The BOM should NOT include a separate "eave strut" line item.
- This applies to ALL buildings — standard, solar, angled, or otherwise.

---

## 10. Girts and Wall Panels

### 10.1 Girt Rules
- Girts use the same length rules as roof purlins (same piece break logic at rafter positions).
- Girt spacing: default 5' on-center, user-configurable.
- Girt rules do NOT change between solar and non-solar buildings.
- Girts are the same material as purlins (20.125" 12GA G90) — just installed vertically on columns instead of horizontally on rafters.
- Girts get their OWN cut list and piece-break output (separate from roof purlins) but appear on the same purlin shop drawings since they are the same material.

### 10.2 Wall Panels
- Solar carports may or may not have walls.
- If walls are included, wall panel rules are the same as non-solar buildings.
- SA estimator inputs for walls (back wall, end walls, side walls) still apply in solar mode.

---

## 11. Panel Type Consistency

### 11.1 One Panel Type Per Project
- All solar panels on a building must be the same type (same dimensions, same mounting holes).
- All buildings in a project also use the same panel type.
- The user enters panel specs once and they apply project-wide.

---

## 12. Roofing Panels vs Purlins

### 12.1 Independence
- Roofing panel piece breaks are NOT affected by purlin piece breaks.
- Roofing panels only care about WHERE purlins land (they must bear on a purlin), not how the purlins themselves are spliced.
- Purlin piece-break logic and roofing panel layout are independent systems.

---

## 13. BOM Line Items for Purlins

### 13.1 Purlin Breakdown
- The BOM should show purlins broken out by piece length, NOT as a single total LF line.
- Example: "Purlin 18'-8" × 24 pcs, Purlin 18'-0" × 12 pcs" rather than "Purlins — 1,440 LF".
- Each distinct piece length gets its own BOM line item with quantity and total LF.
- Splice purlins (short pieces at rafter connections) are a separate line item from main purlins.
- Girts get their own set of piece-length line items (same format, separate section).

### 13.2 Sag Rods
- Sag rods do NOT affect purlin layout, spacing, or piece-break logic.
- Sag rods attach to the BOTTOM of the purlin flanges.
- They are a completely independent system — just hole locations on the purlin web.
- Sag rod rules were established in the rafter/sag rod shop drawing sessions and are unchanged.

---

## 14. Cost Comparison

### 14.1 Four Options
The purlin layout drawing compares all four combinations:
1. Landscape + C-Purlin
2. Landscape + Z-Purlin
3. Portrait + C-Purlin
4. Portrait + Z-Purlin

### 14.2 Comparison Metrics
- Total linear feet of purlin material per option.
- Total piece count per option.
- Estimated cost (LF × cost-per-foot for each purlin type).
- Recommended option = lowest cost.

### 14.3 Building Size Held Constant
- When comparing portrait vs landscape, the building dimensions stay the same.
- The comparison shows how many panels fit and the purlin layout for each option within the same footprint.

---

## 15. Error Conditions and Warnings

### 15.1 Errors (Block Calculation)
| Condition | Message |
|---|---|
| Bay size > max purlin length | "Bay size exceeds max purlin length. Add intermediate rafters to reduce bay size." |
| Z-extension > bay size | "Z-purlin extension exceeds bay size. Reduce extension or increase bay spacing." |
| Purlin flange too narrow for shared panels | "Panel gap + bolt clearance exceeds purlin flange width. Use a wider purlin or reduce gap." |
| Bolt hole outside purlin flange | "Mounting hole position falls outside purlin flange. Check panel spec dimensions." |

### 15.2 Warnings (Allow but Flag)
| Condition | Message |
|---|---|
| Purlin piece < 8' long | "Purlin piece is less than 8'. Consider adjusting bay sizes." |
| Bolt hole within 0.5" of C-purlin butt joint | "Bolt hole is within 0.5\" of a butt joint. Structurally OK but verify with engineer." |
| Bolt hole through Z-purlin overlap zone | "Bolt hole passes through splice overlap — drilling through 2 purlins. This is acceptable." |
| Dummy panels needed in fit-to-dimensions | "N dummy panels needed to fill the space (X in portrait, Y in landscape)." |
| Uneven bay sizes | "Bay sizes are not equal. Shorter bays placed at building ends." |

---

## 16. SA Estimator Input Summary

### 16.1 Standard Mode (Already Exists)
- Building length, width, clear height
- Max bay size, space width, number of spaces
- Purlin type (Z/C), purlin spacing
- Overhang mode (none / 1 space)
- All structural inputs (columns, rebar, footings, etc.)

### 16.2 New Inputs Needed for Standard Purlin Layout
- Max purlin length (default 45', cap 53')
- Z-purlin extension past rafter (default 6')
- Z-purlin eave flange overhang (default 3.5")
- Cost per foot: C-purlin and Z-purlin

### 16.3 New Inputs Needed for Solar Mode
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

### 16.4 Inputs That Remain in Solar Mode
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
