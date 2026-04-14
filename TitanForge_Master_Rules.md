# TitanForge (Titan Carports) - Complete Technical Rules and Specifications

> **Companion Documents:** This file covers **fabrication specifications and material rules.** For system architecture, RBAC roles, permissions, and UI/UX rules, see [`RULES.md`](RULES.md). For the interactive rafter shop drawing architecture, see [`RAFTER_SESSION_STATE.md`](RAFTER_SESSION_STATE.md).

## COMPANY INFORMATION
- **Company:** Structures America (fabricator), Titan Carports (construction/sales entity)
- **Location:** 14369 FM 1314 Conroe, TX 77302
- **Primary Product:** Steel carports for RV/Boat storage, solar installations, and parking structures
- **Key Personnel:** Zachary Bailey (owner, TX), Brad Spence (CO), Andrew Brown (CO)
- **Building Type:** Single slope roof (no center ridge, no two slopes)

---

## COLUMN SPECIFICATIONS & RULES

### Column Material & Gauge
- **Standard Material Grade:** G90 80ksi steel
- **Standard Gauge:** 10GA
- **Standard Profile:** CEE 14"×4"×10GA (C purlins stitch-welded together)
- **Column Configuration Types:**
  - TEE frame: 1 column per rafter (column in middle of rafter)
  - 2-post frame: 2 columns per rafter pair (columns divided equally)
  - Columns placed 1/3 from front of rafter and back (for 2-post frames)

### Column Spacing Rules
- **Parking stalls (standard):** 9' spacing (typical)
- **RV/Boat storage stalls:** 11' or 12' spacing
- **Desired column spacing frequency:** Columns every 22'-36' maximum
- **Maximum column spacing:** 36' maximum (preferred limit)
- **Spacing calculation:** If building is 204' with 36' bays and default 1 space overhang: 6 columns total
  - With no overhangs: 7 columns (unequally spaced)
  - Odd spacing should be in the middle of building when possible
- **Column placement:** Can start on building edge or have overhang (default = 1 space size overhang)
- **Overhang rule:** If overhang, can be maximum of 1 space width (e.g., for 12' spaces, max 12' overhang)

### Column Height & Length Calculation
- **Formula:** Clearance + Angle addition + Embedment + Buffer = Total column length
  - **Clearance:** 14' (typical RV/Boat storage, client-dependent)
  - **Angle addition:** ~5.645" = 0.47' (varies by roof slope)
  - **Embedment depth:** 4'4" = 4.333' (standard footing depth)
  - **Buffer:** 6" = 0.5' (safety margin)
  - **Result:** Total LFT ≈ 40% higher than if clearance only
- **Location dependency:** Column sizing depends on wind/seismic zone from building location
- **Clear height requirement:** Minimum 14' (RV/Boat storage specific)

### Column Cap Plates
- **Standard size:** 3/4" × 26" × 14" (rectangle plate)
- **Quantity per column:** Always exactly 2 cap plates
  - 1 cap plate welded on top of column
  - 1 cap plate welded on rafter where they connect
- **Material:** 3/4" steel, G90
- **Inventory tracking:** Required (track mill certs)
- **Default price per unit:** $95 (editable by user)
- **For 2-post systems:** 4 cap plates per column pair (2 per column)

### Column Gusset Triangles (Angle Bracing)
- **Standard size:** 6"×6"×3/8" steel triangles
- **Quantity per column:** Always 4 triangles
  - 2 triangles per side of column
  - Both sides have different hypotenuse lengths due to roof slope
- **Hypotenuse variation by roof pitch:**
  - **1.2 degree slope:** 2 triangles at 6"×6"×8.3960", 2 triangles at 6"×6"×8.8.5737"
  - **5 degree slope:** 2 triangles at 6"×6"×8.1071", 2 triangles at 6"×6"×8.8473"
  - **10 degree slope:** 2 triangles at 6"×6"×7.7135", 2 triangles at 6"×6"×9.1925"
- **Orientation:** Uphill side = shorter hypotenuse (compressed), Downhill side = longer hypotenuse (expanded)
- **Material:** G90 80ksi, 3/8" thick
- **Inventory tracking:** Required (track mill certs)
- **Default price per unit:** $13 (editable by user)
- **Inventory rule:** One batch/group of triangles gets a single sticker and work order

### Column Rebar (Reinforcement)
- **Material specification:** Weldable rebar only (A706 grade)
- **Rebar sizes:** Options from #5 to #11, default #9
- **Quantity:** Always 4 pieces of rebar per column (one per corner of box)
- **Types of reinforcement:**
  - **Reinforced columns:** Rebar welded INSIDE the column at all four corners
  - **Non-reinforced columns:** Rebar welded OUTSIDE with 6" weld
- **Default:** Reinforced columns (user can toggle)
- **Reinforced column rebar length calculation:**
  - Depth of hole + 8' extension
  - Standard example: If 4'4" embedment + 8' = total length needed
- **Non-reinforced column rebar length calculation:**
  - Depth of hole minus 4'4" embedment
- **Welding pattern:** Stitch welded (consistent throughout both column and rebar)
- **Inventory tracking:** Each size of rebar (#5-#11) needs own inventory item with trigger for reorder
- **Cost tracking:** Track per pound or per foot (user can set)

### Column Cut Angle
- **Top cut angle:** Varies by roof slope/pitch
- **Top cut degrees:** Automatically calculated from roof slope but editable
- **Cutting location:** Bandsaw operation after main column assembly
- **Verification:** Cut must match roof slope requirement before welding cap plate

### Column Assembly Weld Specs
- **WPS-B:** Stitch welds for joining C purlins (standard, doesn't change)
- **WPS-D:** Rebar attachment welds (standard, doesn't change)
- **WPS-F:** Column end welds/cap plate welds (standard, doesn't change)
- **Stitch weld pattern:** Regular intervals along entire seam where C purlins join
- **Cold galvanize:** Applied to all welds, cap plates, and triangles after assembly
- **QA/QC inspection:** Required after all welds completed, before cold galvanizing

### Column Inventory & Tracking
- **Stickers per column:** Each column gets 1 weatherized sticker (4"×6", wax-resin thermal transfer)
- **Sticker placement:** On column cap plate
- **Sticker data fields:** 
  - Piece mark number (auto-assigned sequential)
  - Cut length
  - Coil ID (material source)
  - Heat number
  - Building name
  - Bay number
  - Position (left/right column)
  - Date fabricated
  - QR code (scans to applicable shop drawing)
  - Machine ID (what machine made it)
  - Fabricator name (left blank for shop to fill)
- **Coil data tracked:** Coil ID, material description, gauge, width, heat number, weight received, QR code
- **Group marking:** Each coil should have own unique coil number that never repeats
- **Fabricator capacity:** 4-6 columns per 8-hour day (average production rate)

---

## RAFTER SPECIFICATIONS & RULES

### Rafter Material & Gauge
- **Standard Material Grade:** G90 80ksi steel (default, editable)
- **Standard Gauge:** 10GA (default, editable)
- **Standard Profile:** CEE 14"×4"×10GA (two CEEs stitch-welded together into box beam)

### CEE Channel Anatomy (STANDARD TERMINOLOGY)
- **Web:** The tall vertical part of the CEE (14" for standard 14"×4" CEE)
- **Flange:** The horizontal parts at top and bottom of the CEE (4" each)
- **Lip:** The small return/kick at the edge of each flange (folds inward when assembled)

### Box Beam Assembly (Two CEEs → Box)
- **Orientation:** Two CEEs face each other with open sides together
- **Webs:** Become the LEFT and RIGHT outer walls (vertical, 14" tall)
- **Flanges:** Meet at TOP and BOTTOM (4" + 4" = 8" total width)
- **Lips:** Fold INWARD inside the box where they meet
- **Flanges do NOT overlap** — they butt up edge-to-edge at top and bottom
- **Resulting box beam cross-section:** 8" wide × 14" tall (rectangular)

### Box Beam Stitch Weld Locations
- **Lip-to-lip joints:** Stitch welds run where the lips meet INSIDE the box
- **Flange seams (top & bottom):** Stitch welds also run along the top and bottom where flanges butt together
- **Weld spec (WPS-B):** 5/16" size, 3" weld every 36" O.C. for middle of beam
- **End weld spec:** 1" long welds @ 6" O.C. for first 12" at each end of beam

### Rafter Length Calculation
- **Formula:** Building width - (roofing overhang extension × 2) - (Z purlin reduction if used)
- **Building width:** Length of the structure (distance to span)
- **Roofing overhang:** Amount roofing extends past eaves (default 1', editable)
- **Z purlin reduction:** If Z purlins used on top, rafter is 7" shorter
  - With Z purlins and 1' roofing overhang: Example 40' width = 40' - (2' roofing) - (7") = 37'5"
- **Endcap allowance:** Add 4" on each end for endcap on outside rafters: 4" + 4" = 8" additional
- **Example for 110' building with no overhang:**
  - Rafter lengths: 10', 30', 20', 30', 30' (staggered, not equally spaced)
  - Or with overhang: 10' (overhang), then 36', 30', 36', (overhang with overhang)

### Rafter Configuration in Frame Types
- **TEE frame:** Single column in middle, rafter length = width of building
- **2-post frame:** Two columns per rafter, columns divide rafter equally
  - Front column: 1/3 from front of rafter
  - Back column: varies by back wall requirement
- **With back walls:** Back column set back 12" from back of rafter to accommodate purlin girts

### Rafter Purlin Clips — P1 (CORRECTED FROM Q&A)
- **Part type:** P1 and P2 are the SAME type of part — both are vertical flat plate fins perpendicular to the rafter. P2 is simply a larger version that also caps the beam opening.
- **Dimensions:** 6" base × 10" tall × 10GA thick
- **Material:** 10GA G90 galvanized
- **Orientation:** P1 is a VERTICAL plate/fin — the 6" base sits flat on top of the beam, the 10" sticks STRAIGHT UP like a vertical tab
- **Weld (shop):** 1/8" fillet welds on BOTH 6" edges (the short sides), running perpendicular to rafter length. This is a SHOP WELD (WPS-C)
- **Purlin attachment (field):** The purlin web sits against the flat face of the vertical P1 plate. Tek screws go through the pre-punched holes in P1 into the purlin web
- **Pre-punched holes:** On BOTH sides of the vertical plate (purlins can attach from either side). See purlin facing rules for which side they sit on
- **Hole pattern:** 8 holes total in a 4-column × 2-row grid
  - **Hole diameter:** 1/4"
  - **Horizontal spacing:** 3" between columns (center-to-center)
  - **Vertical spacing:** 2" between rows (center-to-center)
  - **Grid location:** Centered in the upper portion of the 10" extension (above the 6" weld base)
- **Hole edge distance:** 1.5" default (USER VARIABLE — editable per project)
- **Spacing rule:** The input spacing is a MAXIMUM allowed spacing. Actual spacing may be equal to or LESS than the max, but NEVER more.
  - Purlins are placed at BOTH eave ends (0' and full rafter length) plus evenly between
  - Number of spans = ceil(rafter cut length / max spacing)
  - Number of P1 clips = spans + 1 (includes both end purlins)
  - Actual spacing = rafter cut length / number of spans (always ≤ max spacing)
  - Example: 40' rafter, 5' max → ceil(456.375/60) = 8 spans → 9 purlins at 4'-9⅜" O.C.
  - Example: 38' rafter, 5' max → 8 spans → 9 purlins at 4'-6" O.C.
- **Made from:** 10" wide coil, cut to 6" length
- **Roll former:** P1 machine
- **Quantity formula:** Number of purlins × number of rafters
- **Cost:** User-editable default

### Rafter End Caps — P2 (CORRECTED FROM Q&A)
- **Part type:** P1 and P2 are the SAME type of part — both are vertical flat plate fins perpendicular to the rafter. P2 is simply a larger version that also caps the beam opening.
- **Dimensions:** 9" wide × 24" tall × 10GA thick
- **Material:** 10GA G90 galvanized
- **Orientation & fit:** Sits FLUSH against the open end of the box beam like a lid
  - **Bottom:** Extends ½" past beam bottom
  - **Left/right sides:** Extends ½" past each beam side
  - **Top:** Extends 9.5" ABOVE the top of the rafter
  - **Math check:** 14" beam + ½" bottom + 9.5" top = 24" ✓ | 8" beam + ½" + ½" sides = 9" ✓
- **Upper extension purpose:** The 9.5" portion above the rafter is for EAVE PURLIN ATTACHMENT in the field
- **Holes in upper extension:** 8 holes total (4 rows × 2 columns), 1/4" diameter, 3" horizontal spacing, 2" vertical spacing between rows
- **Lower portion:** SOLID — no holes (just wraps around beam end)
- **Weld (shop):** Welded ALL AROUND in shop (WPS-F)
- **Quantity by frame type:**
  - **TEE frame:** 2 P2 per rafter (one on each eave end)
  - **Spliced rafter:** Only on the EAVE end — splice end gets splice plates instead. Both rafter halves get P2 on their far (non-splice) ends
- **Made from:** 24"×9" coil, cut to length
- **Roll former:** P1 machine (same machine as P1)
- **Cost:** User-editable default

### Rafter Connection Plate — P3 (CORRECTED FROM Q&A)
- **Dimensions:** 3/4" thick × 14" wide × 26" long
- **Material:** A572 Gr.50
- **Orientation on rafter:**
  - **26" runs ALONG the rafter length** (parallel to beam)
  - **14" runs ACROSS the rafter** (perpendicular to beam)
- **Attachment:** Welded to the BOTTOM of the rafter in SHOP
- **Location:** At the column position (wherever the column is along the rafter — NOT necessarily at the end)
- **Bolt holes:** 4 holes in 2×2 rectangular pattern
  - **Hole diameter:** 15/16"
  - **Edge distance:** 1½" all around
  - **Horizontal spacing:** 11" between holes (1½" + 11" + 1½" = 14")
  - **Vertical spacing:** 23" (1'-11") between holes (1½" + 23" + 1½" = 26")
- **Field connection:** P3 on rafter bolts to cap plate on column top (4 bolts per connection)
- **Quantity:** 1 per column connection point on the rafter

### Rafter Splice Plates (CORRECTED FROM Q&A — Separate Part from P3)
- **Trigger:** When rafter slope length exceeds 53'
- **Rule:** Must split into pieces, with splice plates joining sections at the joint
- **Splice plate placement:** Within 10' of nearest column position
- **Material:** A36 UNO, 10GA flat plate, G90 paint
- **Flat dimensions (before bending):** ~20½" × 1'-6" (18")
- **Fabrication:** Flat plate with pre-punched holes, then BRAKE-FORMED (bent up 90°) into a U-channel shape
- **Bent shape:** Wraps around the outside of the box beam:
  - Center section: 1'-2" (14") tall — matches beam depth
  - Top/bottom flanges: fold over top and bottom of beam (4" and 3" returns)
- **Holes:** 3/16" diameter, 6 across the top row spaced 3" apart, 1½" edge distance each side
- **Quantity per splice joint:** TWO splice plates (one on EACH side of beam, sandwiching both webs)
- **Field installation:** Tek-screwed to the beam AND welded on TOPS AND BOTTOMS only (NOT sides)
- **Both rafter halves:** Each get P2 caps on their far (non-splice) ends
- **Machine:** C1 roll former with puncher aligned
- **Snap rule:** Snap splice to midpoint between adjacent purlin clips
- **Multi-splice:** If needed, add intermediate columns; middle pieces have no P2 caps

### Rafter Reinforcement — Rebar (CORRECTED FROM Q&A)
- **Default:** Reinforced rafters (user can toggle)
- **Rebar size options:** #5 to #11, default #9 (eventually from engineering)
- **Rebar material:** A706 weldable rebar
- **Quantity:** 4 rebar pieces total per rafter (one per corner of box beam)
  - **2 rebar per CEE half** (one in each web-to-flange corner of that half)
  - Rebar sits in the corners formed between the WEB and the FLANGE on each side
- **Rebar placement (reinforced):**
  - Welded INSIDE the rafter at all 4 corners
  - Location: Interior web-to-flange corners of box section
  - Length: Entire rafter length MINUS first and last 5' on each end
  - Example: 40' rafter with reinforcement = rebar runs 5' to 35' (30' of rebar in 40' rafter)
- **Rebar welding process (CRITICAL — done BEFORE box assembly):**
  1. Rebar is TACK-WELDED to each CEE half first
  2. Then 3" long, 5/16" stitch welds every 3' O.C. along the rebar (WPS-D)
  3. ALL rebar welding is completed BEFORE the two CEE halves are brought together
- **Rebar placement (non-reinforced):**
  - If non-reinforced: NO rebar on rafter at all
  - Only columns have non-reinforced rebar (on outside)
- **Cost tracking:** Per pound or per foot (user editable)

### Rafter Assembly Weld Specs (CORRECTED FROM Q&A)
- **WPS-B:** Stitch welds for joining two CEEs into box beam — runs along lip-to-lip joints AND flange butt seams (top/bottom)
- **WPS-C:** P1 clip-to-rafter welds — 1/8" fillet welds on both 6" edges of P1 base
- **WPS-D:** Rebar attachment welds — 3" long, 5/16" stitch welds every 3' O.C. along rebar (done BEFORE box assembly)
- **WPS-F:** P2 end cap welds — welded all around; also P3 connection plate to rafter bottom
- **Cold galvanize:** Applied to all welds after assembly (outside only, not inside box)

### Rafter Shop Assembly Sequence (CONFIRMED FROM Q&A)
1. **Weld rebar into BOTH CEE halves** (2 rebar per half, one per web-to-flange corner) — tack weld then stitch weld (WPS-D)
2. **Bring two CEE halves together** with lips meeting inside
3. **Stitch weld the lip joints and flange seams** (WPS-B) — both top/bottom flange butt seams and interior lip-to-lip joints
4. **Weld P2 end caps** on eave ends (WPS-F) — welded all around
5. **Weld P3 connection plate** to bottom of rafter at column position (WPS-F)
6. **Weld P1 clips** on top of rafter at purlin spacing positions (WPS-C) — 1/8" fillets on both 6" edges

### Rafter Inventory & Tracking
- **Stickers per rafter:** Each rafter gets 1 weatherized sticker (4"×6")
- **Sticker placement:** On rafter
- **Sticker data:**
  - Piece mark number (auto-assigned sequential)
  - Cut length
  - Coil ID
  - Heat number
  - Building name
  - Bay number
  - Position (which bay, which rafter)
  - Date fabricated
  - QR code (links to shop drawing)
  - Machine list (auto-assigned by part type)
  - Fabricator name (blank)
- **Fabricator capacity:** 4-6 rafters per 8-hour day

---

## PURLIN SPECIFICATIONS & RULES

### Purlin Types Available
- **Z-Purlin:** 12"×3.5"×3/4" lip at 45 degrees
  - **Coil width before roll forming:** 20.125"
  - **Roll former:** Z1 machine only
  - **Roll weight:** 5000 lbs typical
  - **Production:** 5 rolls per 8-hour day
  - **Material:** 29 gauge typical, G90 or G50

- **C-Purlin:** Variable sizes from 16"×4" down to 6"×2"
  - **Lip options:** 3/4" lip for C purlins OR no lip for U purlin
  - **Roll former:** C1 machine (variable purlin machine)
  - **Roll weight:** 5000 lbs typical
  - **Production:** Can make 12"×3.5" Z purlin OR variable C purlins
  - **Material:** 29 gauge typical, G90 or G50
  - **Use case:** Rarely used for roof purlins (Z preferred), but available as option

- **Column Purlins:** 14"×4"×3/4" lip
  - **Roll former:** C2 machine (dedicated for column/rafter purlins)
  - **Purpose:** Only for columns and rafters (not roof purlins)
  - **Material:** 10GA (heavier than roof purlins)

### Purlin Gauge
- **Standard gauge:** 12 gauge (typical)
- **Material grade:** G90 or G50
- **Gauge option:** 29 gauge available for roofing/decking
- **Gauge is editable:** User can change per project needs

### Purlin Spacing Rules
- **On-center spacing:** User input (typical defaults: 4', 5', 8')
- **Row calculation:** Rafter length ÷ purlin spacing = number of rows
  - Example: 40' rafter with 4' spacing = 10 rows of purlins
  - Example: 40' rafter with 5' spacing = 8 rows of purlins
- **Purlin facing direction:** Flanges must face each other
  - Alternating pattern on Z purlins
  - If odd number of purlins, first two bottom-side face same direction
  - Top flange faces out at eaves, alternates inward for interior purlins
- **Minimum purlin requirement:** Purlins can NEVER land on just one rafter
  - Must span between 2+ rafters
  - Can span up to 3 rafters (if total length ≤ 53')

### Purlin Overhang & Splice Rules
- **Overhang option:** Can extend past rafter edges
- **Default overhang:** 6' from center of rafter (editable)
- **Overlap tolerance:** Purlin can extend 6' past rafter on each side
- **Splice requirement:** If purlin extends past rafter, splice plate required
- **Splice default:** 6" overlap splice plate (editable)
- **C-purlin limitation:** NO overhang allowed on C purlins
  - C purlins must land directly on rafter centers
  - No splice option for C purlins
- **Purlin groups generated:**
  - All purlins landing on same rafter span = 1 group
  - Different landing pattern = different group
  - Example: 4 rafters at 10', 30', 30', 30', 10' spans:
    - Group 1: 5 purlins at 46' (over 10' + 30' + back 6')
    - Group 2: 5 purlins at 19' (short middle span)
    - Group 3: 5 purlins at 46' (over 30' + 30' + back 6')

### Purlin Length Calculation
- **Default landing:** Purlin lands on center of internal rafters
  - No overhang: Lengths = exact spacing between rafter centers
  - Example: For 40', 30', 40' spacing: purlins would be 40', 30', 40'
  
- **With overhang (Z purlins only):**
  - Default 6' extension past rafter center
  - Splice requirement: 6" overlap splice
  - Example: 40', 30', 40' → becomes 46', 39', 46' (with 6' overhang and 6" splices)

- **Purlin length limits:**
  - Maximum single length: 53' (soft limit)
  - Length beyond 35': Becomes difficult to handle/install
  - Solution: Split into near-equal pieces landing on intermediate purlins
  - Groups cannot exceed: 2,000 lbs or 50 sheets (whichever comes first)

### Purlin Connection to Rafter (Tek Screws)
- **Screw type:** TEK screw with neoprene washer
- **Screw size/length:** 3/4" long
- **Valley connections (between purlin overlaps):**
  - 2 tek screws per valley at purlin ends
  - 1 tek screw per valley in middle field
  - = 10 screws per 35.79" (one panel width) when panels overlap
  
- **Purlin-to-rafter connections:**
  - 8 tek screws per purlin-to-rafter connection
  - For 5 purlins landing on same rafter: 5 × 8 = 40 screws total

- **Total calculation example (40' rafter, 4' on center, 11 rows):**
  - 68 sheets needed (40' ÷ 35.79" = 67.058 → round up to 68)
  - 68 sheets of 20'3" + 68 sheets of 20' (total 1400 LFT ÷ 35.79" = coverage)
  - Screw calculation per row pattern:
    - Rows 1, 6, 11 (eave/ridge): 10 screws each
    - Rows 2-5, 7-10 (interior): 5 screws each
    - Per 40' section: (10+5+5+5+5+10+5+5+5+5+10) = 70 screws per 40' width
    - Total: 70 × number of building-widths = total screws needed

### Purlin Inventory & Stickers
- **Sticker per group:** Each group of purlins of same size/length gets 1 sticker
- **Bay stickers:** Each "bay" of purlins (group of same size) gets sticker
- **Sticker placement:** On purlin bundle
- **Sticker data:**
  - Piece mark/group number
  - Purlin size (12"×3.5" Z, 14"×4" C, etc.)
  - Length
  - Quantity in group
  - Coil ID
  - Heat number
  - Building name
  - Row numbers (which purlin rows)
  - Weight (calculated for loading)
  - QR code (links to shop drawing)
  - Machine ID (Z1 or C1, etc.)

### Purlin Weight Calculation
- **Weight required:** Per group, for shipping/loading
- **Appears on:** Sticker for shipping purposes

### Purlin Fabrication Capacity
- **Z-purlins:** 5 rolls per 8-hour day (each roll = 5000 lbs)
- **C-purlins:** 5 rolls per 8-hour day (same machine, variable setup)
- **Standard linear feet output:** ~8,000 LFT per day typical range

---

## DECKING / ROOF PANELS SPECIFICATIONS

### Panel Type & Material
- **Standard type:** Spartan Rib, 29 gauge
- **Gauge:** 29 GA (standard), varies by loads
- **Coil width before roll forming:** 48" wide
- **Coil material:** G50 or G90 (depending on project)
- **Roll formed dimension:** 35.79" wide after roll forming
- **Profile:** Spartan Rib pattern
- **Roll former machine:** Spartan rib roll former
- **Roll weight:** 7500 lbs typical
- **Production capacity:** 3 rolls per 8-hour day

### Panel Length Calculation
- **Formula:** Building length ÷ 35.79" = number of sheets (round up)
- **Sheet division rule:** No single sheet longer than 35' (installation limit)
- **Length division:** If total exceeds 35', split into pieces
  - Try to make lengths nearly equal if possible
  - Each sheet must land on purlin for support
  - Sheets can overlap 3" at purlin location

- **Example 1: 40' building, 4' purlin spacing**
  - Total: 40' ÷ 35.79" = 1.118 → need 2 sheets minimum
  - Cannot do 40', must split: Try 20'3" + 20' (totals ~40' with overlap)
  - If 5' on center: (40' ÷ 35.79") × (5' ÷ 4') = different count

- **Example 2: 100' building**
  - 100' ÷ 35.79" = 2.795 → need 3 sheets
  - But each limited to 35' max: Could be 35' + 35' + 30' or 33' + 33' + 34'
  - Depending on where purlins land, adjust to land on purlins

- **Height/Clearance calculation:**
  - Clear height: 14'
  - Rafter thickness: 14" (1'2")
  - Purlin girt thickness: 12" (1')
  - Ground clearance: 6" minimum
  - Formula: 14' + 1'2" + 1' - 6" - (purlin height if wall)
  - For back/side walls with panels: Account for slope height addition

### Panel Fastening (Tek Screws - Roof)
- **Screw type:** TEK with neoprene washers (roofing screws)
- **Screw length:** 3/4"
- **Cost:** $383.22 per 3000 screws (reference price, editable)
- **Valley connections:** 2 screws where panels overlap at valleys
  - Plus 1 additional screw per valley in field
- **Screw count per purlin connection:** 8 screws per connection
- **Total per 35.79" width (one panel width):**
  - Valleys (overlaps): 2 per end + 1s in field = ~10 screws per panel width
  - Purlin connections: 8 per purlin row

- **Complete calculation (40' rafter, 4' purlin, 68 sheets):**
  - Valley screws: 68 sheets × 10 screws = 680 screws
  - Purlin connections: 68 sheets × 11 rows × 8 screws = ~6,000 screws
  - Total estimate: ~6,680 screws (user editable waste factor)

### Panel Waste Factor
- **Default:** 1.05 (5% waste/overage)
- **User editable:** Can change based on actual waste experience
- **Applied to:** Total linear feet calculation

### Panel Inventory & Shipping
- **Grouping rule:** All same-size sheets ship together in groups
- **Weight limit per group:** 2,000 lbs maximum OR 50 sheets (whichever comes first)
- **Shipping flat:** Panels ship flat, stacked
- **Stacking method:** Alternating U-up, U-down (like nested "N" shapes)
- **Sticker per group:** Each group gets 1 weatherized sticker (4"×6")
- **Sticker data:**
  - Length and width of panels in group
  - Quantity
  - Coil ID
  - Heat number
  - Building name
  - QR code
  - Weight (for loading)
  - Machine ID (Spartan rib machine)

### Panel Installation Notes
- **On roof:** Installed last in field
- **Not included in shop drawings:** Panels installed in field, not fabricated components
- **Overlaps:** 3" overlap at purlin (account when calculating length)

---

## ENDCAP SPECIFICATIONS

### Endcap Material & Type
- **Material:** Spartan Rib, 29 gauge, same as roof panels
- **Coil width:** 48" rolls, roll-formed to 35.79"
- **Use:** Ends of roof structure (front and back eaves)
- **Roll former:** Spartan rib roll former (same as roof panels)

### Endcap Orientation
- **Installation:** Vertically (top to bottom)
- **Open structure:** Typically open (not fully enclosed)
- **Exception:** "Fortress" style (Palamento project) may have closed back wall

### Endcap Length Calculation (NEW/REVISED)
- **Formula:** Building clearance + rafter depth + purlin depth - ground clearance - (purlin profile height)
  - **Clearance:** 14' (typical)
  - **Rafter depth:** 14" (1'2")
  - **Purlin depth:** 12" (1')
  - **Ground clearance:** 6" minimum
  - **Z purlin reduction:** 3.5" (if Z purlins on back)
  - **C purlin:** No reduction
  - **Example (Z purlins):** 14' + 1'2" + 1' - 6" - 3.5" = 15'3.5" height

### Endcap Fastening
- **Connection:** Tek screwed to purlins
- **Screw count:** 2 tek screws per purlin (direct attachment underneath)
- **Example (11 purlins):** 11 × 2 = 22 tek screws per endcap
- **Screw type:** Same 3/4" TEK with neoprene washer

### Endcap Inventory & Shipping
- **Grouping:** All same-height endcaps = 1 group
- **Weight limit:** 2,000 lbs or 50 sheets (whichever comes first)
- **Shipping flat:** Stack flat, alternate U-up/U-down
- **Sticker per group:** 1 weatherized sticker (4"×6")
- **Sticker data:** Same as roof panels (length, quantity, coil ID, heat, weight, etc.)

---

## SAG RODS (BRACING) SPECIFICATIONS

### Sag Rod Material & Profile
- **Material:** 2"×2" angle
- **Gauge:** 16 GA
- **Machine:** Angle roll former
- **Coil weight:** 4000 lbs typical
- **Production capacity:** 2 rolls per 8-hour day
- **Standard production:** ~8,000 linear feet per day typical

### Sag Rod Quantity Rules
- **Formula:** Number of spaces in building - 1 = number of sag rod positions
  - Example: 6-bay building = 5 sag rod positions
  - Example: 4-column building = 3 sag rod positions

- **Per position:** Multiple sag rods per position
  - **One per rafter = sag rods that equal number of rafters**
  - Example: For 6-column TEE frame = 6 rafters = 6 sag rods per position
  - **Simple default:** 2 sag rods per rafter = 2× rafter count total

- **Exact formula:** 2 × number of rafters = total sag rod pieces
  - Example: 6 rafters × 2 = 12 sag rod pieces needed for entire building

### Sag Rod Length Rules
- **Primary length:** Same as rafter length
- **Field fabrication:** Can be cut down to smaller sizes in field if needed
- **Handling constraint:** Must be in specific increments for shop handling
- **Increment length:** 20'3" maximum (for worker handling)
- **Multi-piece example:** If rafter is 40' long, cannot make single 40' sag rod
  - Must split: 2 × 20'3" sag rods per rafter position
  - Example 90' rafter: Would need multiple 20'3" pieces per position

### Sag Rod Installation & Orientation
- **Location:** Undersides of purlins
- **Direction:** Parallel with rafters and endcaps
- **Fastening:** 2 tek screws per purlin connection
  - Example: 11 purlins × 2 screws = 22 screws per sag rod
- **Pre-punch holes:** NOT required for sag rods

### Sag Rod Inventory & Stickers
- **Grouping:** Each 10 sag rods of same size = 1 group
- **Sticker:** 1 weatherized sticker per group
- **Sticker data:**
  - Length
  - Quantity (10 pieces)
  - Coil ID
  - Heat number
  - Building name
  - Position
  - QR code
  - Weight
  - Machine ID (angle machine)

---

## HURRICANE STRAPS / BRACING SPECIFICATIONS

### Hurricane Strap Type & Quantity
- **Standard quantity:** 4 per rafter (default, editable)
- **Material:** Same 2"×2"×16GA angle as sag rods (or pre-formed strap)
- **Purpose:** Wind/seismic bracing at column-rafter connections

### Hurricane Strap Installation Location
- **Placement:** 1 purlin in from eave purlins (2 purlin rows in from eave on each rafter)
- **Per rafter:** 4 straps minimum (standard rule)
- **Fastening:** 2 tek screws per connection

### Hurricane Strap Inventory & Stickers
- **Grouping:** Each 10 hurricane straps = 1 group
- **Sticker:** 1 weatherized sticker per group
- **Sticker data:** Same as sag rods

---

## TRIM SPECIFICATIONS

### Trim Material & Type
- **Material:** Metal trim (purchased from Home Depot)
- **Standard length:** 10' sticks
- **Installation:** Front and back of carports (along roof eaves)
- **Fastening:** 5 screws per 10' stick
- **Overlap requirement:** 3" overlap between pieces (must account when calculating)

### Trim Quantity Calculation
- **Formula:** (Building length ÷ 10' per stick) + 1 for overlap = number of pieces per side
  - **Roof line (front/back):** (Building length ÷ 10) + 1 = pieces needed for front
  - **Same for back:** (Building length ÷ 10) + 1 = pieces for back
  - **Sides (if applicable):** (Building width ÷ 10) + 1 = pieces per side
  
- **Example: 200' long, 40' wide building:**
  - Front trim: (200' ÷ 10) + 1 = 21 pieces
  - Back trim: (200' ÷ 10) + 1 = 21 pieces
  - Left side: (40' ÷ 10) + 1 = 5 pieces
  - Right side: (40' ÷ 10) + 1 = 5 pieces
  - **Total: 52 pieces needed**

### Trim Installation & Fastening
- **Fastening:** 5 screws per 10' stick
- **Overlap:** 3" overlap at each joint (account in ordering)
- **Optional feature:** Can be toggled on/off in calculator

### Trim Inventory & Tracking
- **Cost:** Cost per 10' stick (user editable, currently $0)
- **Inventory:** Tracked as purchased items
- **Stickers:** Not typically stickered individually (optional)

---

## WALL SPECIFICATIONS (BACK & SIDE WALLS)

### Wall Applicability Rules
- **Only with:** 2-post or multi-column frames
- **NOT with:** TEE frames (cannot accommodate back walls structurally)
- **Types:** Back wall (parallel to building length), Side walls (perpendicular)
- **Option:** Both walls, back wall only, or no walls

### Wall Panel Material
- **Type:** Spartan Rib, 29 gauge (same as roof)
- **Orientation:** Vertical (top to bottom)
- **Roll former:** Spartan rib roll former
- **Coil:** 48" wide, rolls to 35.79"

### Wall Height Calculation
- **Base formula:** Building clearance + rafter depth + purlin depth - ground clearance - Z purlin height
  - **Clearance:** 14' standard
  - **Rafter depth:** 14" (1'2")
  - **Wall girt purlin depth:** 12" (1')
  - **Ground clearance:** 6" minimum
  - **Z purlin on wall girts:** 3.5" reduction
  - **Result example:** 14' + 1'2" + 1' - 6" - 3.5" = 15'3.5" wall height

- **Back wall (with slope):** Must add additional height for roof slope
  - Formula adjusts to account for increased height due to roof pitch
  - Height varies depending on roof slope (1.2°, 5°, 10°, etc.)

- **Maximum height warning:** If wall panels exceed 20' long, trigger warning
  - Message: "Proceed with caution, may be too tall for wall panel handling"

### Wall Girt Spacing
- **Default:** 5' on center (same as roof purlins, but editable independently)
- **User control:** Can set different spacing than roof purlins

### Wall Panel Length Calculation
- **Per panel:** Building height ÷ 35.79" = number of sheets needed
- **Single sheet limit:** 20' maximum (different from roof 35' limit)
- **Splitting rule:** If exceeds 20', split into multiple panels

### Wall Panel Fastening
- **Fastening:** Tek screws to wall girts
- **Screw count:** Same pattern as roof panels
- **Neoprene washers:** Required (roofing-grade screws)

### Wall Overhang Limits
- **Back wall maximum overhang:** 3.5" past rafter end (Z purlin profile)
  - Cannot extend more than 3.5" past back of rafter
  - Hard limit (error if exceeded)

- **Front/side wall maximum overhang:** 2'8.5" maximum
  - Soft limit with warning: "This exceeds maximum overhang, adjust below this number"

### Wall Extension Rule (Critical)
- **Cannot extend past rafter more than:** 3.5" (Z purlin width) on back wall
- **Front wall:** Can extend user input amount, but not more than 2'8.5"

### Wall Inventory & Stickers
- **Grouping:** Same-size panels = 1 group
- **Weight limit:** 2,000 lbs or 50 sheets
- **Sticker per group:** 1 weatherized sticker
- **Shipping:** Flat, alternating stack (U-up, U-down)

---

## FASTENERS & HARDWARE SPECIFICATIONS

### Tek Screws (Main Fastener)
- **Types:**
  - **Roofing screws:** 3/4" long with neoprene washer (for panels to purlins)
  - **General TEK:** 3/4" long (for other connections)
- **Cost (roofing):** $383.22 per 3,000 screws (editable default)
- **Cost (other):** User editable per type
- **Calculation:** Based on panel count and purlin count, connection types

### Connection Plates (Purlin Clips) — See Rafter Section for Full Details
- **P1 (Interior clips):** 6" base × 10" tall × 1/8" thick vertical plate/fin
  - Welded to rafter top in shop (1/8" fillet both sides of 6" base)
  - Pre-punched holes on both sides for purlin tek-screw attachment in field
  - Quantity: Number of purlins × number of rafters
  - Machine: P1 cut-to-length machine
  - Price default: $0 (user editable)
  - Inventory tracking: Required

- **P2 (End caps):** 9" wide × 24" tall × 1/8" thick
  - Flush lid on beam end, extends ½" past bottom/sides, 9.5" above top
  - 8 holes (4×2 grid) in upper extension for eave purlin attachment
  - Welded all-around in shop
  - Quantity varies by frame type (see Rafter section)
  - Machine: P1 machine
  - Price default: $0 (user editable)
  - Inventory tracking: Required

- **P3 (Connection plate):** 3/4" × 14" × 26", A572 Gr.50
  - Welded to rafter bottom at column position
  - 4 bolt holes (15/16") in 2×2 pattern, 1½" edge distance
  - Bolts to column cap plate in field

### Bolts (Field Connections)
- **Used for:** Column-to-rafter connections
- **Quantity:** 4 per connection
- **Total per building:** Varies by number of columns
- **Example (6 columns):** 4 bolts × 6 = 24 bolts total
- **Currently:** Missing from BOM (needs to be added)
- **Price:** User editable

---

## CONCRETE SPECIFICATIONS

### Concrete Mix & Footing
- **Footing depth:** 4'4" standard (embedment depth)
- **Concrete type:** Standard concrete mix
- **Client specification:** Can vary by region/code
- **Price input:** User inputs cost per cubic yard
- **Calculation:** System calculates yards based on column count and footing depth
- **Note:** Currently separated from fabrication calculator
  - Will be in "Construction" section (Titan Carports quote)
  - Not in "Structures America Fabrication" section

### Concrete Calculation Formula
- **Hole dimensions:** Based on column size (typically 14"×14" for CEE columns)
- **Depth:** 4'4" embedment
- **Volume calculation:** (Width × Width × Depth) × Number of columns = total cubic feet ÷ 27 = cubic yards
- **User input:** Cost per cubic yard
- **Editable:** User can override calculated yards or cost

---

## REBAR (REINFORCEMENT) SPECIFICATIONS

### Rebar Purchase & Inventory
- **Material specification:** A706 weldable rebar ONLY
- **Sizes offered:** #5 through #11
- **Standard size default:** #9
- **Purchase form:** Typically in 40' sticks
- **Purchase method:** By weight
- **Bundling:** Purchased in bundles (quantity per bundle varies by size)
- **Supplier:** Purchased from outside vendor
- **Fabrication:** Structures America cuts to length
- **Inventory tracking:** CRITICAL - must track per size (#5-#11)
- **Cost tracking:** Per pound or per foot (user editable)

### Rebar Quantity Rules
- **Per column (reinforced):** 4 pieces (one per corner of box)
- **Per column (non-reinforced):** 4 pieces (outside placement)
- **Per rafter (reinforced):** 4 pieces (one per corner)
- **Per rebar (non-reinforced):** 0 pieces
- **Total formula:** (Number of columns × 4) + (Number of rafters × 4) = total rebar count

### Rebar Length Rules
- **Reinforced column:** Depth of hole + 8' extension
  - Example: 4'4" embedment + 8' = 12'4" length
- **Non-reinforced column:** Depth of hole minus 4'4" embedment
  - Example: Footing depth minus 4'4"
- **Reinforced rafter:** Entire rafter length minus first 5' and last 5'
  - Example: 40' rafter = rebar runs 5' to 35' (30' of rebar)
- **Non-reinforced rafter:** No rebar (zero pieces)

### Rebar Inventory & Tracking
- **Inventory item per size:** Separate tracking for #5, #6, #7, #8, #9, #10, #11
- **Mill certificates:** REQUIRED - upload and track per coil/batch
- **Heat number:** Track heat number (for validation/traceability)
- **Reorder trigger:** When inventory falls below user-set threshold
- **Cost:** Per pound or per foot (default editable)
- **Testing:** If questioned by engineer, mill certs or independent testing required

---

## PRODUCTION SPECIFICATIONS & LABOR

### Factory Layout
- **Office:** Administrative area
- **Main warehouse:** Material storage, houses C1, C2, Z1, P1, angle roll former
- **Roofing roll former shop:** Separate area for Spartan rib production
- **Welding shop:** Primary assembly area (4 major work areas)
- **Rebar area:** Outdoor storage and cutting (outside welding shop)
- **Cleaning/painting area:** Outdoor, outside welding shop (for cold galvanizing)

### Equipment Inventory
- **C1 Machine:** Variable C purlin roll former (16"×4" to 6"×2", with or without lip), splice plates
- **C2 Machine:** Dedicated column/rafter purlin roll former (14"×4")
- **Z1 Machine:** Z purlin roll former (12"×3.5" with 45° lip)
- **P1 Machine:** Purlin clip (P1/P2 plates) roll former and cut-to-length
- **Angle machine:** 2"×2"×16GA angle roll former (for sag rods)
- **Spartan Rib roll former:** Roofing and wall panel production
- **Robot welders:** 2 robot welding stations
- **Lincoln Cobot:** Collaborative arm on table
- **Bandsaw:** For cutting angles on column tops
- **Punch/cut-to-length roll former:** Cuts P1 clips (6" base × 10" tall) and P2 end caps (9"×24") with pre-punched holes

### Production Capacity (Per 8-Hour Day, One Product Type)
- **Boxed columns/rafters:** 4 rolls = 72 pieces (4-6 finished pieces per day average)
- **Z-purlins:** 5 rolls, roll weight 5000 lbs each
- **Spartan Rib decking:** 3 rolls, roll weight 7500 lbs each
- **Sag rod angle:** 2 rolls, roll weight 4000 lbs each
- **Labor:** 4 people × 8 hours = typical crew
- **Labor cost:** $30/hour average × 4 people × 8 hours = $960/day flat cost
- **Fabrication time (preliminary):** Columns: 1 day each for groups; rafters vary by length

### Production Sequencing Rules (Shop Floor Priority)
- **Default sequence:** Columns first, then rafters, then purlins
- **Optional:** Can modify sequence, but this is standard
- **Work orders:** Assigned to specific shop crews with due dates and checkoff lists
- **Quality gates:** QA/QC check required between major steps

### Shipping & Logistics Rules

#### Truck Specifications
- **Flatbed truck:** Standard shipping vehicle
- **Maximum length:** 53'
- **Maximum load:** 45,000 lbs
- **Shipping sequence:** Columns, rafters, purlins (in that order if possible)
- **Weight maximization:** Fill to weight capacity whenever possible

#### Shipping Strategy
- **Out-of-order rule:** If a finished part will fill remaining weight on current truck, ship it
  - Example: Truck has 5,000 lbs remaining, next part is ready but out of sequence
  - If part fits weight: Ship it (don't wait for in-sequence items)
- **Equal distribution (Purlins):** Attempt to balance purlin load across multiple shipments
- **Sticker groups:** Each shipment group must have clear sticker identifying contents

#### Bill of Lading Generation
- **Automatic generation:** System generates bill of lading based on truck loads
- **Load sequence:** Shows order of items on truck, weights, dimensions
- **Weight per item:** Listed on sticker and load manifest
- **Tie-down points:** Can be specified per load (currently estimated, editable)

### Sticker Specifications (All Components)

#### Sticker Physical Specs
- **Size:** 4" × 6" (standard)
- **Material:** Weatherized sticker (wax-resin thermal transfer ribbon)
- **Printer:** Zebra ZT411 Industrial Barcode Printer (203 dpi)
- **Adhesive:** Weather-resistant (for outdoor storage)
- **Replicable:** Never re-use same barcode number

#### Sticker Data Fields (Standard)
- **Piece mark number:** Auto-assigned sequential (never repeats)
- **Part description:** What component (column, rafter, P1, purlin, etc.)
- **Cut length or dimensions:** Specific to piece
- **Coil ID:** Which coil material came from
- **Heat number:** Material heat/batch number
- **Building name:** Project identifier
- **Bay number or position:** Where it goes (column 1-6, rafter position, etc.)
- **Date fabricated:** When made
- **QR code:** Scans to applicable shop drawing
- **Machine ID:** Which machine produced it
- **Fabricator name:** Blank (shop to fill)
- **Weight:** For loading/shipping (on purlin/panel groups)

#### Sticker Grouping Rules
- **Single component:** Each column, each rafter = 1 sticker
- **Purlin groups:** Each group of same-size purlins = 1 sticker
- **Panel groups:** Each group of same-size panels = 1 sticker
- **Sag rod groups:** Each 10 sag rods = 1 sticker
- **Strap groups:** Each 10 hurricane straps = 1 sticker
- **P1/P2 batch:** One batch of fabricated clips = 1 sticker + work order
- **Endcap groups:** Same-size endcaps = 1 sticker

#### Scanning Workflow
- **On production:** Scan part, system records fabrication
- **On QA/QC:** Scan part, record inspection results
- **On inventory pull:** Scan material coil, confirm it matches work order
- **On shipment:** Scan load manifest, verify weight and contents
- **On receipt:** Site can scan to verify delivered items

### Weld Procedure Specifications (WPS) — CORRECTED FROM Q&A
- **WPS-B:** Stitch welds for joining two CEEs into box beam — runs along lip-to-lip joints inside AND flange butt seams at top/bottom. Spec: 5/16", 3" weld every 36" O.C. (middle); 1" welds @ 6" O.C. for first 12" at ends
- **WPS-C:** P1 clip-to-rafter welds — 1/8" fillet welds on both 6" edges of P1 clip base (shop weld)
- **WPS-D:** Rebar attachment welds — 3" long, 5/16" stitch welds every 3' O.C. along rebar inside CEE (done BEFORE box assembly)
- **WPS-F:** End welds, cap plate welds, P2 end cap all-around welds, P3 connection plate to rafter bottom
- **Stitch weld pattern:** Regular intervals along seams (specify in drawing)
- **Welder certification:** Track and verify for AISC compliance
- **Documentation:** All welds must be documented in weld log per AISC requirements

### Quality & Compliance (AISC)
- **Weld map/weld log:** Track weld locations, welder certifications, inspection results
- **Non-conformance reports (NCRs):** Document non-compliant items with photos, root cause, corrective action
- **Inspection results:** QC sign-off required on all critical welds
- **Mill certificates:** Track and store for all material (upstream responsibility)
- **Photo documentation:** Tie to QC inspection records (audit requirement)

---

## QUOTING & ESTIMATING RULES

### Quote Types
- **Structures America Estimator Quote:** Fabrication only (materials, labor, equipment)
- **Titan Carports Estimator Quote:** Full project (includes fabrication + construction labor, installation, equipment, concrete, etc.)

### Quote Generation Rules
- **Output formats:** PDF and Excel
- **Company name:** "Structures America" for fabrication (no "Titan Carports" reference)
- **Pricing display:** Show MARKED UP price only (not cost + markup separately)
- **Markup visibility:** Hidden from user (shows final price)
- **Project summary:** Shows square footage, estimated steel pounds, options selected

### Quote Contents - Structures America Fabrication
- Bill of Materials (all components with quantities and pricing)
- Labor (single line item, flat rate, total fabrication time)
- Equipment usage (if applicable)
- Shipping instructions (truck count, weight per truck)
- Total fabrication time estimate
- Delivery timeline

### Quote Contents - Titan Carports (Construction)
- **Inherited from SA Estimator:** Materials and labor from fabrication
- **Additional line items:**
  - Concrete (user inputs cost per cubic yard)
  - Installation labor (crew cost per day)
  - Equipment rental (cranes, lifts, etc.)
  - Gas/fuel for equipment
  - Shipping cost (user inputs cost per truck)
  - Drilling (if needed)
  - Hotel/lodging for crew
  - Per diem for crew
  - Transportation costs
  - Any other project-specific costs (user editable)
- **Payment terms:** Billed monthly on percentage of completed milestones (user editable)
- **Total project cost:** All-inclusive estimate

### Coil/Material Entry
- **User inputs coil information:**
  - Coil ID (unique identifier)
  - Material description (thickness, width, type)
  - Gauge
  - Width
  - Heat number
  - Weight received (not footage initially)
  - Price per pound or per foot (user selectable)
- **Cost calculation:** Weight × price per pound = coil cost
- **Inventory tracking:** Track usage, flag reorder when low

### Waste Factor
- **Default:** 1.05 (5% waste)
- **User editable:** Can adjust based on experience
- **Applied to:** Total linear feet calculations (panels, purlins, etc.)

---

## SYSTEM ARCHITECTURE & DATABASE RULES

### Project Structure
- **One project = multiple buildings (canopies)**
- **User specifies:** Number of buildings per project
- **Input methods:** Total square footage OR breakdown by individual space sizes
- **Flexibility:** Can have different frame types (TEE, 2-post, etc.) in same project

### Building Configuration Input
- **Building length:** Option A = direct length input, Option B = spaces × space width
- **Building width:** Rafter span distance
- **Overhang options:** Toggle overhang (default 1 space size) or no overhang
- **Roof slope:** 1/4" per 12" (default), 1.2°, 5°, 7.5°, or 10° (or custom)
  - Solar projects typically 5° slope (different from standard 1/4":12")
- **Column spacing:** User input (every X feet)
- **Purlin spacing:** User input (4', 5', 8', or custom on-center)
- **Frame type:** TEE or 2-post
- **Wall options:** None, back wall only, side walls, or both
- **Solar panels:** Yes/no; if yes, provide panel specs or Helioscope data
- **Decking type:** Spartan Rib standard
- **Trim:** Optional checkbox

### Environmental Input (for design)
- **Project location:** Address or city/state (system looks up building codes)
- **Wind load zone:** Automatic lookup from location (user can override)
- **Seismic zone:** Automatic lookup (user can override)
- **Design standard assumptions:** System notifies user of what it's assuming

### Learning & Improvement
- **Image/PDF recognition:** System can learn from uploaded images to improve square footage identification
- **User feedback loop:** If system is wrong, user corrects it, system learns not to repeat error
- **Cost accuracy:** System tracks actual costs vs. estimates to improve future quotes
- **Production time:** System tracks actual production time vs. estimates

### Data Validation & Warnings
- **Building dimension validation:** Warning if building dimensions don't align with column spacing
  - Example: 200' building with 36' bays = warning if not even multiple
  - Solution: Offer to adjust building or spacing
- **Height overflow:** Warning if wall panels exceed 20' (handling limit)
- **Overhang overflow:** Error if overhang exceeds structural capability
- **Splice trigger:** Automatic detection if rafter > 53' (triggers splice plate requirement)
- **Weight limits:** Warning if panel group or purlin group exceeds 2,000 lbs or 50 sheets

### Data Transfer Between Sections
- **Roofing overhang:** Should transfer from questionnaire to BOM calculator
- **Conflict resolution:** If values differ between sections, popup shows differences and lets user choose which is correct
- **Purlin facing toggle:** Option to show or hide purlin facing direction in shop drawing

### User Permissions & Access Control
- **Role-based access:**
  - Admin: Full access (pricing, costs, all features)
  - Sales: Can create quotes, view projects (no pricing details)
  - Engineering: View all technical details, can edit but limited cost visibility
  - Shop floor: Can view work orders, scanning, QA/QC (no cost data)
  - Fabricator: Assigned pieces, can scan, update status
- **Document access:** Can set permissions per document (quote, contract, drawing, etc.)
- **Permission levels:** View-only, edit, delete, share

---

## SOLAR-SPECIFIC RULES

### Solar Panel Integration
- **Input method 1:** Helioscope export with panel specifications
- **Input method 2:** Manual panel specs (dimension, wattage, etc.)
- **Panel spec format:** Not fully detailed in transcript but mentioned
- **Solar mount points:** Must fit on roof structure
- **Roof slope for solar:** Typically 5 degrees (vs. standard 1/4":12")
- **Panel coverage:** System adjusts purlin spacing and panel count to fit panel layout
- **Status:** Marked as "for later detailed work" - basic framework exists but needs expansion

### Solar-Specific Design Rules
- **Purlin spacing constraint:** Different calculation for solar carports vs. standard
- **Panel orientation:** Different installation pattern
- **Weight distribution:** Solar panels add significant load
- **Detailed rules:** To be developed in future iteration

---

## SHOP DRAWING AUTO-GENERATION RULES

### Column Shop Drawings (Auto-Generated)
- **Layout:** Multiple views
  - Front view (2D profile)
  - Side view (end view)
  - Section A-A (cross-section showing rebar placement)
  - Section B-B (showing angle cuts and gusset triangles)
- **Title block:** Project name, job number, drawing number, date, drawn by, checked by, revision
- **Revision tracking:** Rev A, Rev B, etc. with revision block showing changes/dates
- **Component callouts:**
  - Rebar positions with measurements
  - Gusset triangle dimensions and angles
  - Weld specifications (WPS callouts)
  - Cap plate placement and orientation
  - Material grades and gauges
- **Scaling:** Multiple views, dimensions to scale
- **Digital format:** PDF (must support zoom for phone/tablet viewing)
- **Display:** Can view on phone/tablet/laptop
- **Template:** Based on provided examples (SF21-464-C1, etc.)
- **Auto-populate:** From BOM calculator inputs (column height, angle, rebar size, etc.)
- **Editing:** User can edit after generation, system tracks revisions

### Rafter Shop Drawings (CORRECTED FROM Q&A)
- **Views required:** Elevation (side), Top view, Bottom view, Side (end) view
- **Section A-A:** Cross-section at a P1 clip location showing box beam (8" wide × 14" tall), CEE profiles with webs on sides and flanges at top/bottom, rebar in corners, stitch welds at lips and flanges, P1 clip sitting on top as vertical fin
- **Detail views:** P1 clip detail, P2 end cap detail (showing 9.5" extension with holes), P3 connection plate detail (showing bolt pattern)
- **Weld specifications:** Show WPS-B (stitch), WPS-C (P1 clips), WPS-D (rebar), WPS-F (P2 caps, P3 plate) at correct locations
- **Splice plate detail:** If rafter > 53', show splice plate (BS101) wrapping beam — two plates sandwiching
- **P2 end cap detail:** Show flush lid with ½" extension on 3 sides, 9.5" above, hole pattern in upper portion
- **P1 clip detail:** Show vertical fin orientation (10" tall, 6" base), weld symbols on both 6" edges, pre-punched holes on both faces, hole pattern: 8 holes (4×2 grid, 1/4" dia, 3" horiz × 2" vert spacing)

### Rafter — No-Paint Zones
- **Rafters do NOT have no-paint (NP) zones.** Do not show NP zones on any rafter view.
- Note: Columns MAY have NP zones, but rafters never do.

### Rafter Shop Drawing — Scale Rules
- **Consistent scale within each view:** Horizontal and vertical MUST use the same px/in ratio. Do NOT exaggerate beam width/height relative to length.
- **Each view may have its own scale** (elevation vs. plan views), but within a single view both axes must match.
- **Part sizing:** All parts (P1, P2, P3, rebar) must use the same scale as the beam in their respective views. No artificial enlargement or minimums.

### Rafter Shop Drawing — Dimension Standards
- **All dimensions measured from the LEFT eave end** (cumulative from one side)
- **Row 1 — P1 purlin positions:** Tick marks at each P1 location along a baseline, with cumulative distance labels from the left end (e.g., 0', 4'-9", 9'-6", 14'-3"...)
- **Row 2 — Rebar positions:** Separate dimension row showing distance from left end to RB START, rebar length, and distance from RB END to right end
- **Row 3 — Overall length:** Full rafter cut length
- **No repetitive spacing chains** (e.g., don't show "5' 5' 5' 5'" between each purlin — the cumulative row handles this)
- **Spacing note:** A single text label showing total P1 count and actual spacing (e.g., "9 P1 @ 4'-9" O.C.")

### Rafter Shop Drawing — Rebar Display Rules
- **Rebar drawn semi-transparent** (fill-opacity ~0.4) so beam and other parts are visible through them
- **Reinforced/Non-Reinforced toggle:** Must be functional — when set to non-reinforced, rebar is removed from ALL views, BOM, weight calculations, and dimension rows

### Rafter Shop Drawing — View Representation Rules (STANDARD)
These rules define how each part appears in each view. This is the standard for all rafter shop drawings.

#### ELEVATION VIEW (looking at side of rafter — sees the 14" tall web face)
- **Beam:** Rectangle showing full rafter length × 14" tall
- **P1 clips:** Appear as THIN VERTICAL LINES on top of beam (we see the 10GA edge from the side — the flat face is perpendicular to us). Height = 10" above beam top
- **P2 end caps:** Appear as THIN VERTICAL LINES at each eave end (same reason as P1 — we see the edge). Height extends 9.5" above beam top and ½" below beam bottom
- **P3 connection plate:** Appears as a THIN HORIZONTAL LINE under beam bottom (we see the ¾" edge from the side). Length = 26" (along rafter length)
- **Rebar:** Shown as 1 small rectangle at top of beam + 1 at bottom (the left+right rebar at each height overlap in this view). Semi-transparent fill. Inside the beam, near the flanges — NOT floating below.
- **Stitch welds:** Small tick marks along top and bottom of beam at specified O.C.
- **No NP zones:** Rafters do not have no-paint zones — do not show them.

#### TOP VIEW (looking down at rafter from above)
- **Beam:** Long rectangle showing full rafter length × 8" wide (SAME SCALE both axes)
- **Flange butt joint:** DASHED LINE running down the center of beam (where two CEE flanges meet)
- **P1 clips:** THIN LINES across the 8" beam width at purlin spacing positions (we see the 10GA edge from above). Placed at BOTH eave ends + evenly between per spacing rule.
- **P2 end caps:** THIN 9" LINES across beam at each eave end (9" because P2 extends ½" past each side)
- **P3 connection plate:** Visible but BEHIND/BLOCKED BY rafter (shown as hidden lines — dashed or lighter). 14" wide × 26" long rectangle centered under beam at column position. Uses SAME SCALE as beam.
- **Rebar:** 2 semi-transparent rectangles, one near each web edge (top+bottom rebar at same web overlap into 1 line per web)

#### BOTTOM VIEW (looking up at rafter from below)
- **Beam:** Long rectangle showing full rafter length × 8" wide (SAME SCALE both axes)
- **P3 connection plate:** Rectangle at column position, 26" ALONG rafter × 14" ACROSS rafter (oriented correctly with long dimension parallel to beam). Uses SAME SCALE as beam.
- **Bolt holes:** 4 holes in 2×2 pattern with dimensions
- **Rebar:** 2 semi-transparent rectangles, one near each web edge

#### SIDE VIEW / END VIEW (looking at open end of rafter — at eave)
- **Beam cross-section:** 8" wide × 14" tall rectangle
- **P2 end cap:** Thin plate covering the opening, extending ½" past sides and bottom, 9.5" above top
- **Rebar:** 4 circles (cross-sections) IN THE CORNERS — touching both web and flange surfaces. Each rebar sits right in the web-to-flange corner
- **NO purlin rectangles** in this view (purlins are field-installed, not shown on shop drawing)

#### SECTION A-A (cross-section cut through beam at P1 location)
- **Beam:** 8" wide × 14" tall box showing both CEE profiles
- **P1 clip:** Vertical fin on top of beam, 10" tall, shown as thin rectangle (10GA thick)
- **Rebar:** 4 circles in corners touching both web and flange
- **P3:** If section is at column location, show as THIN RECTANGLE under beam (¾" thick × 14" wide — proportional to beam)

#### DETAIL VIEWS
- **P1 Detail:** Full-size or enlarged view showing 6" × 10" plate, weld symbols on both 6" edges, hole pattern (8 holes in 4×2 grid, 1/4" dia, 3" horiz × 2" vert spacing), material callout: 10GA G90
- **P2 Detail:** Enlarged view showing 9" × 24" plate, lower portion solid, upper 9.5" extension with hole pattern (8 holes, 4×2, 1/4" dia, 3" × 2" spacing), material callout: 10GA G90. Text must NOT overlap drawing
- **P3 Detail:** Enlarged view showing 14" × 26" plate, 4 bolt holes in 2×2 pattern (15/16" dia, 11" × 23" spacing, 1½" edge distance), material callout: ¾" A572 Gr.50
- **Column connection detail:** Show P3 plate on rafter bottom bolting to column cap plate
- **P3 Weld Detail (Detail 4):** Cross-section showing how ¾" P3 plate attaches to bottom of box beam — shows partial beam bottom, P3 plate underneath, fillet welds at junction and overhang edges, 3" overhang dimension each side, 3/16" all-around weld (WPS-F), MT inspection callout

### Rafter Shop Drawing — Layout Spacing Rules
- **Dynamic positioning:** All zones (elevation, plan views, details) use dynamic Y-coordinates that cascade from the elevation view downward. No hardcoded Y positions between zones.
- **Elevation dim rows:** Minimum 32px gap from beam bottom to first dimension row (P1 cumulative). Minimum 34px gap between P1 row and rebar row.
- **Rebar weld symbol:** Routes UPWARD (above beam) to avoid overlapping dimension rows below.
- **Piece mark leaders:** Staggered vertically into two tiers (pmY1 = highest, pmY2 = second) to prevent leader lines from crossing.
- **P3 elevation labels:** Positioned 20px below beam bottom, above the dim row zone.
- **Section A-A cut labels:** Offset 18px above/24px below beam edges to clear P1 clips and dim rows.
- **Plan views gap:** Minimum 42px from top view bottom (including dims) to bottom view top.
- **Side view:** Positioned at bvCy + 10 (vertically aligned with bottom view) but shifted right (x=620) to avoid horizontal overlap.
- **Zone 3 (Details):** Starts 72px below side view bottom content, giving clear separation from plan views.
- **BOM table:** Positioned at zone3Top + 10, right-aligned (x=800+).
- **Title block:** Fixed at y=680. All detail content must stay above y=670 (10px clearance minimum).

### Rafter Shop Drawing — AISC 360-22 Compliance Checklist
- **Material grades on sheet:** CEE = Gr.80 G90 Galvanized (NOT A36, NOT A570 Gr.50). P1/P2 = 10GA G90. P3 = A572 Gr.50. Rebar = A615 Gr.60.
- **Camber:** Always NONE for rafters (straight members)
- **Hole type:** 15/16" DIA STD — Bolts: A325-N bearing type, snug tight
- **Piece mark = erection mark** (noted on drawing)
- **Rebar preheat:** 300°F min per AWS D1.4 when chemical composition unknown
- **Weld inspection:** VT all welds / MT on P3 and P2 (critical connections)
- **Weld schedule on drawing:** WPS-B (CEE stitch), WPS-C (P1 clip fillet), WPS-D (rebar stitch), WPS-F (end cap/conn plate all-around)
- **Shop assembly order:** 1) Rebar→CEE 2) Box weld 3) P2 caps 4) P3 plate 5) P1 clips
- **Tolerances:** Length ±1/16" / Holes ±1/32"
- **Scale labels:** Each view shows its calculated scale (e.g., SCALE: 1"=18")
- **BOM:** Both on-sheet (SVG table) AND sidebar panel, with Material and Weight columns
- **DO NOT SCALE DRAWING** notation required
- **Optional toggle:** Can choose to show/hide purlin facing details

### Purlin Shop Drawings
- **Layout:** 3D profile view, length, BOM, standard title block
- **Splice detail:** Show purlin splice location and overlap if applicable
- **Purlin groups:** Group same-size purlins together on drawing
- **Weight per group:** Shown for loading/shipping
- **Quantity per group:** Clearly marked

### Sag Rod Shop Drawings
- **Simple installation/framing plan:** Show sag rod placement under purlins
- **Direction:** Parallel to rafters/endcaps
- **Connection points:** Which purlins it connects to
- **Length and quantity:** Per position

### Endcap Shop Drawings
- **Installation plan:** Vertical orientation, height details
- **Connection details:** Tek screw locations to purlins
- **Quantity per side:** Front and back endcap count

### Decking Panel Shop Drawings
- **Layout sheet:** Show which panels go where by size
- **Stacking arrangement:** How to stack for shipping (U-up, U-down)
- **Weight per stack:** For loading
- **Quantity per stack:** Clear count
- **No shop fabrication drawing** (panels not fabricated, only installed)

### General Shop Drawing Rules
- **PE stamp block:** NOT included
- **Values source:** User inputs or from questionnaire (offer both modes)
- **Questionnaire:** Structured questions to auto-populate shop drawing variables
- **Defaults:** Pre-filled with project-standard values (Sanford defaults, etc.)
- **Engineering report output:** Separate PDF that shares drawing info with engineer
  - Excludes all cost data
  - Includes all structural variables (loads, stresses, calculations)
  - Helps engineer understand project and do their work

---

## BUSINESS PROCESS RULES

### Project Workflow
1. **Intake:** Sales creates quote (Titan Carports Estimator)
2. **Engineering:** MSC (McClish) or similar firm designs structure (separate process)
3. **Fabrication quote:** Structures America Estimator updated with final engineering
4. **Production plan:** System generates work orders, shipping manifest, schedule
5. **Fabrication:** Work orders printed, shop floor executes
6. **QA/QC:** Inspections logged, NCRs filed if needed
7. **Shipping:** Manifest generated, trucks loaded per specifications
8. **Installation:** On-site erection using stickers as reference

### Quoting Process
- **Customer database:** Track customers and their preferences
- **Quote template:** Standardized format
- **Version control:** Track quote iterations (V1, V2, etc.)
- **Approval workflow:** Requires sign-off before sending to customer
- **Shared access:** Can share with customer via dashboard/portal

### Dashboard Features
- **Global search:** Find any project, document, customer, part
- **Inventory tracking:** Pull from dashboard (linked to SA Estimator)
- **QA/QC section:** All AISC documentation, WPS procedures, welder certifications
- **Work order section:** Current jobs, schedules, bottleneck identification
- **Gantt/timeline view:** See overlapping jobs, capacity planning

### Document Management
- **Project documents:** Quotes, contracts, engineering, layouts, shop drawings
- **Permission control:** Set who can view/edit each document
- **Upload capability:** Import PDFs, images, DXF files, etc.
- **Version history:** Track changes and revisions
- **Archive:** Store completed projects for reference

### System Architecture Considerations
- **Data capacity:** Track data growth, plan upgrades as needed
- **Offline capability:** PWA/service worker support for shop floor (WiFi can be spotty)
- **Mobile-first:** Designed for phones/tablets in shop, office, field
- **Export formats:** PDF, Excel, DXF (for engineering)
- **API/integration:** Consider integration with accounting, ERP (future)

### Inventory Management
- **Coil tracking:** Track usage, trigger reorder alerts
- **Mill certificates:** Upload and store per material batch
- **Parts inventory:** P1/P2 plates, cap plates, triangles, rebar (by size)
- **Barcode scanning:** Generate and scan barcodes on all tracked items
- **Low-stock alerts:** Automatic notification when inventory below threshold
- **Reorder rules:** Suggested quantities based on production schedule

### Fabrication Scheduling
- **Work order generation:** From BOM (sequential: columns, rafters, purlins)
- **Crew assignment:** Assign to specific shop teams with due dates
- **Checkoff lists:** Track completion of each step
- **Priority queuing:** System suggests smart queue (based on dependencies)
- **Multi-job visibility:** Gantt view for capacity planning
- **Bottleneck detection:** Flags when multiple jobs overlap

---

## COST & PRICING RULES

### Material Costs
- **Coil cost:** Weight × Price per pound (or Footage × Price per foot)
- **Purchased items:** Cap plates ($95 default), triangles ($13 default), rebar (per pound)
- **Hardware:** Tek screws ($383.22 per 3,000), bolts (user input), trim (per 10' stick)
- **Editable:** All prices user-editable with saved defaults

### Labor Costs
- **Shop labor:** $960 per day flat rate (4 people × $30/hour × 8 hours)
- **Single line item:** Total fabrication labor
- **BOM display:** Total estimated days to complete
- **Fabrication time:** Calculate based on component quantities and production rates

### Equipment/Facility
- **Machine time:** Included in labor cost
- **Facility overhead:** Included or separate (user specifies)
- **Cold galvanizing:** Material cost + labor (separate or bundled)

### Shipping Costs
- **Per truck:** User inputs cost per truck
- **Calculated trucks:** System calculates number of trucks needed (max 45,000 lbs each)
- **Load manifests:** Generated automatically

### Markup & Pricing
- **Markup:** Applied but hidden from customer view on quote
- **Final price:** Shown as all-in (cost + markup combined)
- **Editable markup:** Sales can adjust per job

### Quote Summary
- **Total material cost:** Sum of all materials
- **Total labor cost:** Fabrication labor line item
- **Total shipping cost:** Calculated trucks × per-truck cost
- **Subtotal:** All above
- **Markup:** Applied (shown in internal view only)
- **Total:** Final price to customer
- **Price per square foot:** Calculated for comparison

---

## GENERAL BUSINESS RULES

### Standard Defaults (Editable)
- **Building clearance:** 14'
- **Roof slope:** 1/4" per 12" or 1.2°
- **Solar roof slope:** 5°
- **Roof overhang:** 1'
- **Purlin spacing:** 4', 5', 8' options
- **Column spacing:** 36' max
- **Rebar size:** #9
- **Reinforced (default):** Yes for both columns and rafters
- **Hurricane straps per rafter:** 4
- **Sag rod multiplier:** 2× rafter count
- **Sag rod increment length:** 20'3"
- **Purlin overhang:** 6' from rafter center
- **Purlin splice overlap:** 6"
- **Wall girt spacing:** 5' on center
- **Wall panel max length:** 20'
- **Decking panel max length:** 35'
- **Waste factor:** 1.05 (5%)
- **Concrete cost:** User input per cubic yard
- **Tek screw cost:** $383.22 per 3,000 (roofing)
- **Trim cost:** User input per 10' stick
- **Cap plate cost:** $95 per unit
- **Triangle gusset cost:** $13 per unit
- **Labor cost:** $960 per day flat
- **Shipping cost:** User input per truck
- **Payment terms:** Billed monthly on milestones (construction only)

### Location-Based Rules
- **Wind load:** Automatic lookup from location (can override)
- **Seismic zone:** Automatic lookup (can override)
- **Building codes:** Automatically referenced based on location
- **Column sizing:** Adjusted based on location requirements

### Quality Assurance Rules
- **All components:** Must have QA/QC sign-off before shipping
- **Critical welds:** Inspected and documented
- **Material verification:** Mill certs on file
- **Non-conformance:** NCRs filed with photos and corrective action
- **Traceability:** Barcodes track every piece from material to installation

---

## KNOWN GAPS / FUTURE DEVELOPMENT

### Shop Drawing Improvements Needed
- Triangle placement needs refinement (positioning in drawings)
- Rebar visualization needs work (corners vs. sides)
- Angle cuts need dynamic adjustment (section B-B changes with slope)
- Welds symbols need better implementation
- Consider interactive/dynamic rendering option
- Consider copying professional template layout from examples

### Features to Add Later
- Solar carport detailed rules (different purlin spacing, panel layout)
- Electrical tracking (solar panel count/type only, no electrical work)
- Purchase order generation (triggered by inventory reorder)
- Packing slip/bill of lading auto-generation
- Time tracking integration (compare estimate vs. actual)
- Photo attachments on QC inspections
- Offline/PWA capability for shop floor
- Multi-job Gantt scheduling
- Automated email/notifications for order status

### Data Management
- File upload capacity planning
- Database scaling strategy
- Backup and disaster recovery
- User access audit trail

---

## MULTI-POST COLUMN RULES (EXPANDED)

### When to Use Multiple Columns Per Rafter
- **Tee (1 column):** Default for buildings ≤ 45' wide. Single column at midpoint of rafter.
- **2-Post:** Required when ANY of these conditions are true:
  - Customer requests it
  - Engineering requires it
  - There is a back wall
  - Building width exceeds 45'
- **3-Post:** Building width exceeds 90' — add a 3rd column
- **4-Post:** Building width exceeds 135' — add a 4th column
- **General rule:** Every additional ~45' of width adds another column
- **Column placement (2-post):** Columns at 1/3 points from front and back of rafter
- **Back wall columns:** ONLY on 2-post frames, offset 19" from main column center

### Back Wall Column Rules
- **Availability:** Only on 2-post or multi-post frames — NEVER on Tee frames
- **Offset:** 19" from main column center toward back wall
- **Purpose:** Support back wall girts and panels
- **When required:** Whenever a back wall is present on a 2-post+ frame

---

## RAFTER REBAR PLACEMENT RULES (EXPANDED)

### Rebar Stick Placement (Reinforced Rafters)
- **Stick length:** Typically always 20' long (standard stick length)
- **Placement locations:**
  - Halfway between columns (centered between adjacent column positions)
  - Above/at each column position
  - Within 5' of each eave end
- **Quantity per corner:** 4 rebar pieces total (one per corner of box beam)
- **Non-reinforced rafters:** Zero rebar — no rebar at all
- **Lap splice:** 2' lap splice where rebar sticks overlap

### Rebar Stick Count Formula (from codebase)
- `sticks_per_side = max(1, ceil(max(0, rafter_length - 10) / 20))`
- This ensures enough 20' sticks to cover rafter length minus 5' from each end

---

## RAFTER OVERHANG RULES

### Roofing Overhang
- **Rule:** Customer-specified (NOT a fixed formula)
- **Default:** 1' per side (editable)
- **Maximum:** 2'8.5" (32.5") past rafter end — error if exceeded
- **Z-purlin deduction:** If Z-purlins used, rafter is 7" shorter (3.5" per side)

---

## RAFTER DXF GEOMETRY REFERENCE (From Production DXF)

### Component Layout (Tee Frame, Single Slope) — CORRECTED FROM Q&A
- **Main body:** Two 14×4 CEE channels facing each other forming box beam (webs = sides, flanges butt at top/bottom, lips fold inward)
- **P2 end caps:** At eave ends of rafter (9"×24"×1/8", welded all around, 9.5" extends above beam for eave purlin attachment)
- **P1 interior clips:** Vertical fin/tab — 6" base welded to beam top, 10" sticks up. Spaced at purlin spacing. Shop-welded with 1/8" fillet welds on both 6" edges
- **P3 connection plate:** At column position, welded to BOTTOM of rafter (3/4"×14"×26" A572 Gr.50). 26" along rafter, 14" across
- **Rebar group:** 4 pieces total (2 per CEE half) in web-to-flange corners of box beam

### DXF-Verified Dimensions (with Q&A corrections)
- **P1 clip spacing:** Based on purlin spacing (e.g., 60" for 5' O.C.)
- **P1 clip:** 6" base × 10" tall vertical fin, 1/8" fillet welds both sides of 6" base
- **P2 end cap:** 9" wide × 24" tall, extends ½" past bottom/sides, 9.5" above beam top
- **P3 connection plate:** 26" along rafter × 14" across, on bottom of rafter at column location
- **End-to-end span (P2 to P2):** ~480" for a 40' rafter
- **Box beam cross-section:** 8" wide × 14" tall (webs on sides, flanges butt at top/bottom)

---

## RAFTER SPLICE RULES (EXPANDED)

### Splice Plate Details (CORRECTED FROM Q&A + Production Drawing BS101)
- **Part designation:** Beam Splice (BS101 in production drawings) — SEPARATE part from P3
- **Material:** A36 UNO, 10GA, G90 paint
- **Flat plate dimensions (before bending):** ~20½" × 1'-6" (18")
- **Fabrication:** Flat plate with 3/16" pre-punched holes, then BRAKE-FORMED with 90° bends into U-channel shape
- **Bent shape wraps around box beam:**
  - Center: 1'-2" (14") matching beam depth
  - Top/bottom returns: 4" and 3" flanges with returns
- **Hole pattern:** 6 holes across top, spaced 3" apart, 1½" edge distance each side
- **Field install:** TWO splice plates per joint (one each side, sandwiching both webs). Tek-screwed to beam AND welded on tops and bottoms ONLY (not sides)
- **Trigger:** Rafter slope length > 53'
- **Position:** Within 10' of nearest column position
- **Snap rule:** Snap splice to midpoint between adjacent purlin clips
- **Both rafter halves get P2 caps on their far ends** — splice plates are at the joint only
- **Multi-splice:** If needed, add intermediate columns; middle pieces have no P2 caps

---

## SHOP DRAWING LAYOUT RULES (Production Standard)

### Rafter Shop Drawing Layout (from 6 production PDFs: SF21-464-B1 through B6)
- **Sheet orientation:** Landscape
- **Main view:** ONE elevation view of full rafter (side profile) — NOT multiple grid views
- **Purlin bay grid:** Shown ABOVE the main elevation view with decimal-inch dimensions (e.g., 60.0000 = 5')
- **Detail callouts:** BELOW the main elevation view:
  - P1 TYP (typical interior clip detail)
  - P2 end cap detail
  - Rebar placement detail
  - P3 bolt hole pattern
  - Section A-A cross-section
- **BOM panel:** On the RIGHT side of the drawing
- **Title block:** Far RIGHT edge of sheet
- **Dimensions:** Shown in feet-inches with fractions OR decimal inches depending on context
- **Weld symbols:** Called out on main elevation with WPS codes

### Column Shop Drawing Layout (Established Gold Standard)
- **Views:** Front, side, Section A-A, Section B-B
- **Interactive features (all drawings must have):**
  - Zoom/pan (SVG viewBox manipulation)
  - Keyboard shortcuts
  - Weld drag/rotate editing
  - Label dragging
  - Annotations
  - 60-deep undo/redo stack
  - Copy/paste welds
  - Footer status bar
  - Touch events (single-finger pan, two-finger pinch zoom)
  - BOM slide-out panel

---

## STITCH WELD DETAILS (from codebase config.py)

### Column/Rafter Stitch Weld Specification (WPS-B)
- **Weld size:** 5/16"
- **Pattern:** 3-36 (3" weld every 36" O.C.) for middle of beam
- **End weld:** 1" long welds @ 6" O.C. for first 12" at each end of beam
- **Locations on box beam:** Lip-to-lip joints (inside) AND flange butt seams (top/bottom)
- **WPS code:** WPS-B (standard, never changes)

### Rebar Stitch Weld Specification (WPS-D)
- **Weld size:** 5/16"
- **Pattern:** 3" long stitch welds every 3' O.C. along rebar
- **Process:** Tack weld rebar first, then stitch weld — ALL done before box assembly
- **Location:** Inside each CEE half, in web-to-flange corners

---

## BOLT HOLE SPECIFICATION (from codebase config.py)

### Connection Bolt Holes
- **Diameter:** 15/16"
- **Pattern:** Standard 4-bolt pattern
- **Quantity:** 4 bolts per column-to-rafter connection
- **Editable:** Yes

---

## COATING SPECIFICATION

### Cold Galvanize
- **Application:** Cold galv all plain steel and welds
- **Note:** "Cold galv paint on welds and cut/plain steel edges only"
- **Timing:** Applied after all welding and QA/QC inspection complete

---

## MARK/PREFIX CONVENTIONS (from codebase config.py)

### Piece Mark Prefixes
- **Ship marks (columns):** "C" prefix
- **Piece marks:** "p" prefix
- **Rebar marks:** "rb" prefix
- **Rule:** Any component difference = new ship mark (grouping_rule: any_difference_new_mark)

---

## ENDCAP DETAILS (from codebase config.py)

### Endcap Specification
- **Profile:** U-channel (no lips) for both Z and C purlins
- **Inside dimension:** 12"
- **Leg height:** 4"
- **Gauge:** 12GA (same as purlin)
- **Material:** G90
- **Machine:** C1
- **Tek screws per purlin:** 4 (2 top + 2 bottom)
- **Max length:** 30'4" (364")
- **Must land on purlin if split:** Yes
- **Quantity per building:** 2 (one per building end)
- **Shipping:** Nested alternating (U-up, N-down)

---

## PURLIN FACING RULES (from codebase config.py)

### Z-Purlin Facing Direction
- **First purlin (eave):** Flanges face OUT (away from building center)
- **Alternating pattern:** Each subsequent row alternates direction
- **Odd count rule:** If odd number of purlins, first two bottom-side face same direction
- **Z-purlins:** Facing matters (asymmetric profile)
- **C-purlins:** All face same direction (symmetric profile doesn't matter)
- **Toggle:** Show/hide purlin facing on rafter drawing (default: hidden)

---

## PURLIN SPLICE DETAILS (from codebase config.py)

### Purlin Splice Specification
- **Overlap:** 6" default (editable)
- **Tek screws per splice:** 8 (#10 tek screws)
- **Splice location:** 6' from rafter in mid-span
- **Splice piece length:** 6" default (editable)
- **Splice piece position:** Sits on top of purlins

---

## END OF EXTRACTED RULES

**Document Complete — Version 2.0 (Updated April 13, 2026)**

**Version 2.0 Changes (from 20-question Q&A session with Zack):**
- Added CEE Channel Anatomy section (Web, Flange, Lip definitions)
- Added Box Beam Assembly section (how two CEEs form the box)
- CORRECTED P1 clip: vertical fin (10" up, 6" base), shop-welded to rafter, purlin tek-screwed to P1 in field
- CORRECTED P2 end cap: extends ½" past bottom/sides, 9.5" above top for eave purlin attachment, 8 holes (4×2) in upper extension
- CORRECTED P3 orientation: 26" along rafter, 14" across, welded to rafter bottom at column location
- CORRECTED splice plate: separate part from P3, A36 10GA, brake-formed U-channel, two per joint sandwiching beam
- CORRECTED rebar: tack-welded then stitch-welded (3" @ 3' O.C.) to each CEE half BEFORE box assembly
- CORRECTED stitch weld locations: lip-to-lip AND flange butt seams
- Added complete rafter shop assembly sequence (6 steps)
- Added P1 hole edge distance as user variable (1.5" default)

Total rules extracted: 450+ specifications across 25+ major categories

**IMPORTANT: Claude must READ this file before asking Zack any rule-related questions. If Claude asks about a rule already documented here, Zack should say "read the rules file."**

