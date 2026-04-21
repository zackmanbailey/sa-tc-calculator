# TitanForge Purlin Integration Plan

> Created: 2026-04-20
> Source: Design sessions between Zack (Titan Carports) and engineering.
> Reference: docs/PURLIN_RULES.md

---

## Overview

This plan maps every rule in PURLIN_RULES.md to the TitanForge modules that need to change. The goal is to make the SA estimator, BOM engine, and shop drawings fully aware of purlin layout rules — including solar panel mode, angled purlins, Z/C purlin differences, and the 4-option cost comparison.

---

## 1. SA Estimator — New and Modified Inputs

### 1.1 Solar Mode Toggle (NEW)

The SA estimator currently has `solar_toggle: False` stubbed in `config.py` but it does nothing. This needs to become a real toggle that swaps which input sections are visible.

**What changes:**
- `templates/sa_calc.py`: Add a solar/standard mode selector at the top of each building form. When solar is selected, hide standard purlin spacing input and show solar-specific inputs (Section 1.3 below). When standard is selected, hide solar inputs.
- `config.py`: `solar_toggle` default becomes a real per-building field.
- `calc/defaults.py`: Already has `"solar": {"deg": 5.0, ...}` for slope — wire this as the default when solar mode is on.

### 1.2 New Standard Mode Inputs (MISSING from SA estimator)

These inputs currently exist ONLY in the interactive purlin layout drawing. They need to be added to the SA estimator so the BOM can use them.

| Input | Default | Where to Add |
|---|---|---|
| Max purlin length (ft) | 45 (hard cap 53) | Building form, structural section |
| Z-purlin extension past rafter (ft) | 4 | Building form, shown only when purlin_type = Z |
| Z-purlin eave flange overhang (in) | 3.5 | Building form, shown only when purlin_type = Z |
| Cost per foot — C-purlin ($/ft) | user input | Building form, cost section |
| Cost per foot — Z-purlin ($/ft) | user input | Building form, cost section |
| Purlin angle from perpendicular (°) | 90 (perpendicular) | Building form, new "Angled Purlins" section |

**Files affected:**
- `templates/sa_calc.py` — add input fields and wire to building data object
- `config.py` — add defaults to `DEFAULT_CONFIG`
- `calc/defaults.py` — add to defaults dict

### 1.3 New Solar Mode Inputs (ENTIRELY NEW)

None of these exist anywhere in the SA estimator today. They only exist in the interactive purlin layout drawing controls.

| Input | Default | Notes |
|---|---|---|
| Panel width (mm) | — | Required in solar mode |
| Panel length (mm) | — | Required in solar mode |
| Mounting hole distance from panel edge (mm) | — | Required for bolt hole placement |
| Mounting hole inset from panel short edge (mm) | — | Required for bolt hole placement |
| Panels across (count) | — | Panel count mode |
| Panels along (count) | — | Panel count mode |
| OR: Available space W × L (ft) | — | Fit-to-dimensions mode |
| Gap width between panels (in) | 0.25 | Universal default |
| Gap length between panels (in) | 0.25 | Universal default |
| Panel orientation | landscape / portrait / compare | Compare = show all 4 options |
| Solar slope (°) | 5 | Already in calc/defaults.py |
| Rafter spacing override (ft) | — | Only when no parking stalls |

**Files affected:**
- `templates/sa_calc.py` — new solar input section, conditionally shown
- `config.py` — solar defaults
- `calc/defaults.py` — solar slope already exists, add others

### 1.4 Inputs That Stay the Same in Solar Mode

These existing SA estimator inputs remain and are used by both standard and solar modes:
- Reinforced columns and rafters
- Footing depth, embedment, column buffer
- Column rebar size, beam rebar size
- Column mode (auto/spacing/manual)
- Cut allowance
- Wall panels and girts (optional in solar)
- Max rebar stick, end gap, splice location override
- Overhang mode (none / 1space)
- Space width (used for overhang distance and rafter placement when over parking)

---

## 2. BOM Engine (`calc/bom.py`) — Calculations to Add/Update

### 2.1 Rafter Length Calculation (UPDATE)

**Current:** Rafter length = building width. No purlin-type adjustment.

**Needed:**
- C-purlin: rafter length = building width (no change)
- Z-purlin: rafter length = building width − (2 × eave flange overhang)
  - Default overhang = 3.5" → 40' building = 39'-5" rafter
- This affects rafter material weight and cost

**File:** `calc/bom.py` — rafter length calculation section

### 2.2 Purlin Piece Length Calculation (NEW)

**Current:** BOM calculates total linear feet of purlins but does NOT break them into pieces with joint rules.

**Needed — C-purlin pieces:**
- Pieces break at rafter centers, 4" per purlin on each rafter at a joint
- End pieces: +8" past end rafter center (4" endcap + 4" half-rafter) when no overhang
- End pieces: +overhang distance when overhang mode is on
- Algorithm: maximize piece length up to max purlin length, break at rafter centers

**Needed — Z-purlin pieces:**
- Pieces extend past rafter by Z-extension (default 4')
- 6" overlap where two Z-purlins meet
- Same end piece rules as C-purlin (8" past center, no overhang; overhang distance when on)
- Splice holes through both purlins in overlap zone

**Needed — Angled purlins:**
- Adjusted length = perpendicular_length / cos(angle from perpendicular)
- All pieces on a line are the same length even when angled
- Butt joint rule unchanged (4" of rafter width per purlin)

**File:** `calc/bom.py` — new purlin piece-break function, called from existing purlin calculation

### 2.3 Purlin Layout Options Generator (NEW)

**Needed:** Generate 2-3 ranked layout options per purlin type showing:
- Piece count and lengths for each option
- Total linear feet
- Waste/efficiency metric

This powers both the BOM summary and the interactive drawing's cut list.

**File:** `calc/bom.py` or new `calc/purlin_layout.py` module

### 2.4 Solar Panel BOM Items (NEW)

**Current:** No solar hardware in BOM.

**Needed:**
- 4 stainless steel bolt stacks per panel (bolt + washer + star washer + lock washer + nut)
- Total bolt stacks = 4 × total_panels
- Panel count (informational line item)
- Dummy panel count if fit-to-dimensions mode was used

**File:** `calc/bom.py` — new solar hardware section

### 2.5 Solar Building Dimensions (NEW)

**Current:** Building length comes from n_spaces × space_width. Building width is a direct input.

**Needed in panel count mode:**
- Building width = panels_across × panel_width + (panels_across − 1) × gap_width + 2 × edge_clearance
  - Landscape: panel_width = panel short side
  - Portrait: panel_width = mounting_hole_distance (between purlin pairs)
- Building length = panels_along × panel_length + (panels_along − 1) × gap_length + 2 × endcap_clearance

**Needed in fit-to-dimensions mode:**
- Calculate how many panels fit in each orientation
- Report dummy panel count for each option

**File:** `calc/bom.py` or new `calc/solar_layout.py` module

### 2.6 Purlin Spacing in Solar Mode (UPDATE)

**Current:** Purlin spacing is a user input or auto-calculated from building width.

**Needed in solar mode:** Purlin spacing is DICTATED by panels, user does NOT input it.
- Landscape: spacing = panel short-side width (e.g., 992mm ≈ 3'-3")
- Portrait: spacing = mounting hole distance within each panel pair; pairs are spaced by panel width + gap
- N panels across in landscape = N+1 purlin lines
- N panels across in portrait = 2N purlin lines

**File:** `calc/bom.py` — purlin count/spacing calculation, solar branch

### 2.7 Cost Comparison (NEW)

**Needed:** When orientation = "compare", calculate all 4 options:
1. Landscape + C-Purlin
2. Landscape + Z-Purlin
3. Portrait + C-Purlin
4. Portrait + Z-Purlin

For each: total linear feet × cost_per_foot. Recommend lowest cost option.
Building dimensions held constant across all 4.

**File:** `calc/bom.py` or `calc/purlin_layout.py`

### 2.8 Error/Warning Checks (NEW)

Add validation checks from PURLIN_RULES.md Section 11:

**Errors (block calculation):**
- Bay size > max purlin length
- Z-extension > bay size
- Purlin flange too narrow for shared panels (solar)
- Bolt hole outside purlin flange (solar)

**Warnings (flag but allow):**
- Purlin piece < 8' long
- Bolt hole within 0.5" of C-purlin butt joint (solar)
- Bolt hole through Z-purlin overlap zone (solar, informational)
- Dummy panels needed in fit-to-dimensions
- Uneven bay sizes

**File:** `calc/bom.py` — validation function called before/after purlin calculations

---

## 3. Shop Drawings — Updates and New Features

### 3.1 Purlin Layout Drawing (`templates/purlin_layout.py`) — ALREADY BUILT

This interactive drawing already exists and handles most of the visualization. Remaining work:

- **Wire to BOM data**: Currently uses only interactive controls. Need to populate controls from SA estimator config when available (max purlin length, Z-extension, cost/ft, solar inputs).
- **Add facing direction callouts**: SVG must show which direction each purlin faces (arrows or labels for each purlin line per PURLIN_RULES.md Section 4).
- **Add P1/P2 plate positions**: Mark P1 plate positions on the rafter (small gap / big gap pattern based on facing direction).
- **Add splice hole callouts for Z-purlins**: Show splice holes in the overlap zone.
- **Add angled purlin support**: Rotate purlin lines in plan view, adjust piece lengths by cos(angle), show stagger offset.
- **Bolt hole positions for solar**: Show drilled hole positions on purlin top flange at mounting hole locations from panel spec.

### 3.2 Purlin Detail Drawing (`templates/purlin_drawing_v2.py`) — UPDATE

The existing per-group purlin drawing needs:
- **Facing direction indicator**: Show which way the purlin faces in the cross-section view.
- **Z-purlin overlap detail**: Show the 6" lap zone with splice holes.
- **Angled purlin cross-section**: Show the angled footprint on the rafter with contact length = bottom_flange_width / sin(angle).

### 3.3 Rafter Drawing (`templates/rafter_drawing.py`) — UPDATE

- **P1 plate positions**: Show welded plate positions on top of rafter, reflecting the small-big-small gap pattern from purlin facing.
- **P2 plate at eave**: Show P2 plate at rafter ends (perpendicular purlins only).
- **End cap plate**: Show end cap plate at rafter ends when purlins are angled (replaces P2).
- **Rafter length adjustment**: Z-purlin buildings have shorter rafters (building width − 2 × 3.5").

### 3.4 Shop Drawings Hub (`templates/shop_drawings.py`) — DONE

Already has the Purlin Layout card added (this session's commit).

### 3.5 Cut List Generator (`shop_drawings/cutlist_gen.py`) — UPDATE

- Add purlin piece-break data to the cut list output.
- Include piece lengths, quantities, and group labels (end piece vs middle piece).
- For Z-purlins: note which pieces have splice holes.

### 3.6 Purlin Generator (`shop_drawings/purlin_gen.py`) — UPDATE

- Feed purlin layout calculations (piece breaks, facing direction, splice holes) into the PDF generator.
- Support angled purlins in the generated drawing.

---

## 4. Config and Data Flow

### 4.1 Config Pipeline

The data flows: SA Estimator → `config.py` → `calc/bom.py` → shop drawing config → interactive templates.

New fields need to be added at every step:

**`config.py` DEFAULT_CONFIG additions:**
```
max_purlin_length_ft: 45
z_extension_ft: 4
z_eave_overhang_in: 3.5
purlin_cost_per_ft_c: null
purlin_cost_per_ft_z: null
purlin_angle_deg: 90
solar_mode: false
panel_width_mm: null
panel_length_mm: null
mounting_hole_dist_mm: null
mounting_hole_inset_mm: null
panels_across: null
panels_along: null
panel_gap_width_in: 0.25
panel_gap_length_in: 0.25
panel_orientation: 'landscape'
solar_slope_deg: 5
rafter_spacing_override_ft: null
```

### 4.2 `_load_shop_config` and `_enrich_config_for_building` (tf_handlers.py)

These functions populate the config dict passed to interactive drawings. Need to:
- Include all new purlin/solar fields from the building's saved data.
- Pass through to the PURLIN_LAYOUT_CONFIG_JSON template variable.

### 4.3 Database Schema

If buildings are stored in `titanforge.db`, the building record may need new columns for solar inputs. Check whether buildings use JSON blob storage (flexible) or fixed columns (need migration).

---

## 5. Implementation Phases

### Phase 1: Standard Mode Purlin Layout (Foundation)
**Goal:** SA estimator collects all standard purlin inputs, BOM calculates piece breaks correctly.

1. Add missing SA estimator inputs (max purlin length, Z-extension, eave overhang, cost/ft, angle)
2. Add purlin piece-break calculation to `calc/bom.py`
3. Wire piece-break data into purlin layout drawing config
4. Add facing direction callouts to purlin layout drawing
5. Add P1/P2 plate positions to rafter drawing
6. Add error/warning validation checks
7. **Test:** Standard carport with C-purlins, Z-purlins, verify piece lengths match PURLIN_RULES.md examples

### Phase 2: Solar Mode Inputs and Layout
**Goal:** SA estimator supports solar mode, building dimensions calculated from panels.

1. Build solar mode toggle in SA estimator (show/hide input sections)
2. Add all solar-specific inputs to building form
3. Build solar building dimension calculator (panel count mode and fit-to-dimensions mode)
4. Calculate purlin spacing from panel dimensions (landscape and portrait)
5. Calculate purlin line count (N+1 for landscape, 2N for portrait)
6. Add bolt hole position validation (fits on flange, 0.5" clearance)
7. Add solar hardware to BOM (4 bolt stacks × total panels)
8. Wire solar data into purlin layout drawing
9. **Test:** 5×20 landscape solar array with CS3K-P specs, verify building dimensions and purlin count

### Phase 3: Cost Comparison and Optimization
**Goal:** 4-option cost comparison works end-to-end from SA estimator.

1. Build comparison engine (all 4 combos: L+C, L+Z, P+C, P+Z)
2. Add comparison output to BOM results
3. Wire comparison data into purlin layout drawing's Compare All feature
4. Add dummy panel reporting for fit-to-dimensions mode
5. **Test:** Same building, compare all 4 options, verify lowest cost recommendation

### Phase 4: Angled Purlins
**Goal:** Angled purlin support throughout the system.

1. Add angle input to SA estimator
2. Adjust purlin length calculation (÷ cos(angle))
3. Update P1/P2 plate logic (P1 only when angled, end cap plate replaces P2)
4. Add angled purlin visualization to purlin layout drawing
5. Update rafter drawing for angled plate positions
6. **Test:** 45° angled purlins on a standard carport, verify lengths and plate callouts

### Phase 5: Shop Drawing Polish
**Goal:** All shop drawings reflect purlin rules correctly.

1. Add splice hole callouts for Z-purlins to purlin layout and detail drawings
2. Add facing direction indicators to purlin detail drawing (v2)
3. Update cut list generator with piece-break data
4. Update purlin PDF generator
5. Cross-check all error/warning conditions fire correctly
6. **Test:** Full end-to-end: SA estimator → BOM → all shop drawings for both solar and standard buildings

---

## 6. Files Affected Summary

| File | Phase | Change Type |
|---|---|---|
| `templates/sa_calc.py` | 1, 2 | Major — new input sections |
| `config.py` | 1, 2 | Add defaults for all new fields |
| `calc/defaults.py` | 1, 2 | Add defaults |
| `calc/bom.py` | 1, 2, 3 | Major — piece breaks, solar dims, comparison |
| `templates/purlin_layout.py` | 1, 2, 3, 4 | Wire to config, add facing/plates/angle |
| `templates/purlin_drawing_v2.py` | 5 | Add facing, overlap detail |
| `templates/rafter_drawing.py` | 1, 4 | P1/P2 plates, rafter length |
| `tf_handlers.py` | 1, 2 | Config enrichment for new fields |
| `shop_drawings/cutlist_gen.py` | 5 | Piece-break data |
| `shop_drawings/purlin_gen.py` | 5 | PDF generation updates |

---

## 7. Open Questions for Next Session

1. **Database storage**: Are building records stored as JSON blobs or fixed columns? This determines whether we need a DB migration for solar fields.
2. **Panel spec library**: Should we build a saved panel spec library (dropdown of common panels like CS3K-P) so users don't re-enter dimensions every time?
3. **Girt layout drawing**: Girts follow the same piece-break rules as purlins — should we extend the purlin layout drawing to include a girt layout view, or keep it separate?
4. **PDF export of comparison**: Should the 4-option cost comparison be exportable as a standalone PDF for customer quotes?
5. **Multiple buildings with different modes**: Can one job have both a solar building and a standard building? If so, the solar toggle is per-building, not per-job.
6. **Purlin weight lookup**: The BOM currently uses purlin weight per foot. Should cost comparison use the same weight-based pricing or switch to the new cost-per-foot input?
7. **Panel spec validation**: Should we validate that user-entered panel dimensions are reasonable (e.g., width 800-1200mm, length 1500-2400mm)?

---

*End of integration plan.*
