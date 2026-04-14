# TitanForge Rafter Shop Drawing & 3D Viewer — Session State
## Last Updated: April 13, 2026

> **Companion Documents:** This file covers **rafter drawing code architecture and state management.** For system architecture, RBAC roles, permissions, and UI/UX rules, see [`RULES.md`](RULES.md). For fabrication specs (materials, welds, tolerances), see [`TitanForge_Master_Rules.md`](TitanForge_Master_Rules.md).

**Owner:** Zack Bailey (zack@titancarports.com) — Structures America / Titan Carports
**Purpose:** This file captures EVERYTHING needed to resume editing the rafter shop drawing and 3D viewer without losing context.

---

## FILES (all in same folder as this document)

| File | Lines | Description |
|------|-------|-------------|
| `RafterShopDrawing_v2.html` | ~3934 | Primary deliverable — interactive AISC-compliant rafter fabrication drawing |
| `Rafter3DViewer.html` | ~634 | Three.js orbit viewer for 3D rafter inspection |
| `extracted_rules_raw.md` | ~1556 | Master rules/specs document for all Titan Carports fabrication |

---

## RAFTER SHOP DRAWING (RafterShopDrawing_v2.html) — ARCHITECTURE

### Overall Structure
- **Single-file HTML** with embedded CSS + JS (~3934 lines)
- **SVG-based drawing** on white sheet (1100×850 viewBox) with dark UI chrome
- **5 drawing zones:** Elevation, Plan Views (Top/Bottom/Side), Details, BOM Table, Title Block
- **Span diagram** rendered above the drawing in a separate SVG

### Key State Variables
```javascript
let weldEditMode, selectedWeldId, weldOverrides, labelOverrides;
let layoutOverrides;    // 11 layout groups (notes-block, top-view, bottom-view, side-view, section-aa, detail-1..5, bom-table)
let layoutEditMode, selectedLayoutId;
let undoStack, redoStack;  // 60-deep undo/redo
let annotateMode, annotations, selectedAnnotation;
let currentWeldDefs, customWelds, deletedWelds, addWeldMode;
let activePiece;       // multi-piece tab index (0-based)
let columnEditMode;    // drag columns on elevation
let reinforced;        // true/false toggle
```

### Input Controls (toolbar)
| Input ID | Type | Default | Description |
|----------|------|---------|-------------|
| `inputWidth` | number | 40 | Building width in feet |
| `inputSpacing` | number | 5 | Purlin spacing in feet |
| `inputOverhang` | number | 1 | Rafter overhang in feet |
| `inputPurlinType` | select | Z | Z or C purlin |
| `inputAngledPurlins` | checkbox | off | Enable angled purlin mode |
| `inputPurlinAngle` | number | 15 | Purlin angle from perpendicular (degrees) |
| `inputBackWall` | checkbox | off | Enable back wall mode |
| `inputFrontCol` | number | 0 | Front column position (ft) when back wall on |
| `inputColMode` | select | auto | Column mode: auto/spacing/manual |
| `inputColSpacing` | number | 25 | Column spacing (ft) — spacing mode |
| `inputP3Count` | number | 1 | Manual column count — manual mode |
| `inputColumnPositions` | text | (auto) | Comma-separated column positions in ft |
| `inputSpliceLocation` | number | 0 | Splice position in ft from left |
| `inputRebarSize` | select | #9 | Rebar size #5–#11 |
| `inputMaxStick` | number | 20 | Max rebar stick length in ft |
| `inputEndGap` | number | 5 | Gap from rafter end to rebar in ft |
| `btnReinforced` / `btnNonReinforced` | button | Reinforced | Toggle rebar on/off |

### Core Functions
| Function | Purpose |
|----------|---------|
| `getParams()` | Collects all inputs into params object |
| `calc(p)` | Master calculation — returns all derived values (positions, counts, weights) |
| `draw()` | Clears SVG, calls calc(), renders all 5 zones |
| `drawSpanDiagram(p, d)` | Renders column position visualization above drawing |
| `updateBOM(p, d, rafterMark)` | Populates sidebar HTML BOM table |
| `setupTips(p, d)` | Hover tooltips for SVG part groups |
| `autoFillColumnPositions()` | Recalculates column positions from current mode |
| `updateColModeUI()` | Shows/hides column mode inputs + angled inputs |
| `updatePieceTabs()` | Creates/updates piece tabs for multi-piece rafters |
| `fmtFtIn(inches)` | Formats inches as feet-inches with fractions |
| `fmtScale(pxPerRealIn)` | Formats scale for 8.5"×11" print (e.g., `1" = 7'-0"`) |
| `weld(...)` | Renders AWS weld symbol with leader, reference line, tail |
| `dlabel(...)` | Draggable label with leader line |
| `dimH/dimV/dimHRebar(...)` | Dimension line helpers |

### calc() Return Object — Key Fields
```javascript
{
  totalCutLengthIn, totalCutLengthFt,     // Full rafter length
  cutLengthIn, cutLengthFt,               // Active piece length
  p3Count, p3Positions,                    // Column count and inch positions on rafter
  p1Count, p1Positions, p1Spans, p1ActualSpacingIn,  // P1 clip data
  pieceP1Positions, pieceP3Positions,      // Positions relative to active piece
  p2Count, p6Count, p3CountPiece, p5Count, // Part counts for active piece
  needsSplice, spliceCount, splicePositions, spliceWarnings,
  pieces, pieceCount, activePieceData,     // Multi-piece definitions
  leftEnd, rightEnd,                       // 'p2', 'p6', or 'p5' for each piece end
  endPlateType,                            // 'p2' or 'p6' globally
  angleRad, p1FootprintIn,                 // Angled purlin geometry
  rebarLengthIn, rebarSticks, rebarGapEach, rebarStickPositions, rebarBarDia, rebarAvailIn,
  ceeWeight, p1Weight, p2Weight, p6Weight, p3Weight, p5Weight, rebarTotalWeight, totalWeight,
}
```

### Drawing Zones Layout
1. **Zone 1 — Elevation View** (y≈80–200): Full rafter profile, P1 thin lines, P2/P6/P5 ends, P3 below, rebar, dimension chains, weld symbols, piece mark leaders, notes block
2. **Zone 2 — Plan Views** (below elevation):
   - **Top View** (tvL=30, tvR=500): Looking down — beam, P1 clips (angled diagonal or perpendicular), P2/P6 labels, P3 dashed, rebar
   - **Bottom View** (bvL=30, bvR=500): Looking up — same components with P3 bolt holes, P1 clips, end plate labels
   - **Side View** (sideViewX=620): P2 (tall, 8 holes) or P6 (compact, no holes) cross-section, rebar dots
3. **Zone 3 — Details Row**: Section A-A, P1 detail, P2 detail, P3 bolt pattern, P5 splice detail
4. **Zone 4 — BOM Table** (bomX=800): SVG table with all parts
5. **Zone 5 — Title Block** (y=680–815): Project info, customer, revision block

### Interactive Features
- **Weld editing:** Click welds to select, drag to reposition, rotate arrows
- **Label dragging:** Drag any dlabel to reposition
- **Layout repositioning:** Drag entire view groups (11 layout-wrapped groups)
- **Annotations:** Add text/arrow annotations anywhere
- **Undo/Redo:** 60-deep stack, Ctrl+Z / Ctrl+Y
- **Multi-piece tabs:** When rafter > 53', tabs appear for each piece
- **Column dragging:** Drag column positions on elevation view
- **Zoom/Pan:** Ctrl+scroll zoom, mouse drag pan on SVG
- **Touch:** Single-finger pan, two-finger pinch zoom

### CSS Classes for SVG Elements
| Class | Purpose |
|-------|---------|
| `obj thick/med/thin/hair` | Object outlines at different weights |
| `hidden` | Dashed hidden lines |
| `center` | Center lines (long-short-short dash) |
| `dim/dimtxt` | Dimension lines and text |
| `cee` | CEE channel fill (#F0F0F0) |
| `cap` | End cap fill (#E0E0E0) |
| `conn-plate` | P3 connection plate fill (#B8B8B8) |
| `clip-fill` | P1 clip fill (#C8D8E8) |
| `rebar-solid/rebar-circ/rebar-circ-out` | Rebar rendering |
| `weld-*` | AWS weld symbol elements |
| `cut-line` | Section cut indicators |

---

## RAFTER 3D VIEWER (Rafter3DViewer.html) — ARCHITECTURE

### Technology
- **Three.js r128** via CDN (`https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js`)
- **Custom orbit controls** (r128 doesn't bundle OrbitControls)
- **Left-drag:** orbit, **Right-drag:** pan, **Scroll:** zoom, **Click:** inspect/highlight part

### 3D Model Components
| Component | Geometry | Material Color | Position Logic |
|-----------|----------|----------------|----------------|
| Box Beam | BoxGeometry(8, 14, rafterIn) | #B0B0B0 (matCee) | Centered at origin |
| Inner void | BoxGeometry(innerW, innerH, rafterIn-0.5) | #3a3a3a | Inside beam |
| CEE seam | BoxGeometry(8.1, 0.15, rafterIn+0.2) | #666666 | Horizontal center |
| P1 Clips | BoxGeometry(6, 10, 0.135) | #5599DD (matP1) | Top of beam, spaced from 1×spacing to rafter-1×spacing |
| P1 Holes | CylinderGeometry(0.25) × 8 per clip | #1a1a1a | 4 rows × 2 cols, 3"H × 2"V spacing |
| P2 End Caps | BoxGeometry(9, 24, 0.135) | #DD8833 (matP2) | Each end, 9.5" above beam |
| P6 End Plates | BoxGeometry(9, 15, 0.135) | #DD8833 (matP2) | Each end, ½" overhang |
| P2 Bolt Holes | CylinderGeometry(0.25) × 8 | #EEEEEE | 4×2 on P2 upper extension |
| P3 Plates | BoxGeometry(14, 0.75, 26) | #888888 (matP3) | Below beam at column positions |
| P3 Bolt Holes | CylinderGeometry(0.46875) × 4 | #EEEEEE | 23"×11" pattern |
| P5 Splice | Box bottom + 2 side walls | #44AAAA (matP5) | At rafter center when >53' |
| Rebar | CylinderGeometry(dia/2) × 4 corners | #CC4400 (matRebar) | Inside beam at corners |
| Stitch welds | Line segments | #0055AA | 36" O.C. along top edges |

### Input Controls (3D viewer toolbar)
| Input ID | Maps to |
|----------|---------|
| `in3dWidth` | Building width |
| `in3dSpacing` | Purlin spacing |
| `in3dOverhang` | Overhang |
| `in3dReinforced` | Reinforced toggle |
| `in3dRebarSize` | Rebar size dropdown |
| `in3dAngled` | Angled purlins checkbox |
| `in3dAngle` | Purlin angle degrees |
| `in3dBackWall` | Back wall toggle |

### Key Functions
| Function | Purpose |
|----------|---------|
| `buildRafter()` | Clears scene, rebuilds all geometry from inputs |
| `clearModel()` | Removes all meshes from rafterGroup |
| `addPart(mesh, name, material)` | Registers mesh for raycasting + tooltips |
| `updateCamera()` | Positions camera from spherical coordinates |
| `animate()` | Render loop (requestAnimationFrame) |

### Part Inspection
- **Raycaster** on click: highlights part in gold (#F6AE2D), shows name label
- **partRegistry[]** array: all clickable meshes registered via addPart()
- **Hover cursor** changes to pointer over parts

---

## ENGINEERING RULES QUICK REFERENCE

### Column Count (building width-based)
```
width <= 45' → 1 column
width > 45' → max(2, ceil(width / 60))
```

### Column Placement
- **Auto:** Quarter-points (outermost at L/4, inner fill evenly)
- **Spacing:** User-defined ft apart, centered
- **Manual:** User count + explicit positions
- **Back wall:** Back col at 19" from right end, front col configurable

### P1 Clip Rules
- ½" minimum clearance from each rafter end (no overhang)
- Standard: perpendicular thin fins
- Angled: all clips at same angle (no mirroring), footprint = 6" × sin(angle)
- No P1 at ends where P2/P6 exists — P1s are interior only

### P2 vs P6
- P2: 9"×24", 9.5" above beam, 8 purlin holes — standard perpendicular purlins
- P6: 9"×15", ½" overhang all around — angled purlins only, replaces P2

### P3 Constraints
- P3 center ≥ 13" from rafter ends (half of 26" plate)
- Splice cannot land within 14" of P3 center (nudged away)

### Splice (P5)
- Triggers when rafter cut length > 53'
- BS101: 10GA × 20¾" × 18" U-channel
- Splits rafter into pieces with tabs in drawing

### Rebar
- Configurable max stick length (default 20') and end gap (default 5')
- 4 bars per stick position (one per corner)
- Data: {#5:[1.043,0.625], #6:[1.502,0.750], #7:[2.044,0.875], #8:[2.670,1.000], #9:[3.400,1.128], #10:[4.303,1.270], #11:[5.313,1.410]}

### Scale Labels
- Calculated for 8.5"×11" landscape print (100px = 1 paper inch at 1100px SVG width)
- `fmtScale(pxPerRealIn)` → e.g., `1" = 7'-0"`

---

## WHAT TO DO WHEN RESUMING

1. **Read this file first** to understand the full architecture
2. **Read `extracted_rules_raw.md`** for detailed fabrication rules
3. **Read the specific section** of `RafterShopDrawing_v2.html` or `Rafter3DViewer.html` that needs editing
4. **Use the function/variable reference above** to find the right code location
5. **Always run syntax check** after edits: `node -e "new Function(allJS)"` pattern
6. **Always present the file** after changes so Zack can test immediately

### Common Edit Patterns
- **Add new input:** Add HTML in toolbar → add to `getParams()` → use in `calc()` → render in `draw()` → add event listener
- **Add new part type:** Add to `calc()` return → render in each zone (elevation, top, bottom, side, details) → add to both BOM sections → update tooltips → add to 3D viewer
- **Change placement rules:** Edit `calc()` function → column rules near top, P1 placement after, splice logic in middle
- **Update 3D viewer:** Edit `buildRafter()` — all geometry is rebuilt from scratch on each input change
