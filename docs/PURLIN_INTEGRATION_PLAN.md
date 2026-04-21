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
| Z-purlin extension past rafter (ft) | 6 | Building form, shown only when purlin_type = Z |
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

### 2.1 Rafter Length Calculation (UPDATE — TWO LOCATIONS)

**Current state — there are TWO rafter length formulas that must stay in sync:**

1. **`calc/bom.py` line 787**: `calc_rafter_slope_length(width_ft, slope_deg)` — uses `2 × sqrt((width/2)² + rise²)`. Does NOT deduct Z-purlin overhang at all. This drives the BOM weight/cost for rafter coil.

2. **`shop_drawings/config.py` line 962**: `calc_rafter_length(width_ft, overhang_ft, use_z_purlins)` — deducts `2 × roofing_overhang` and 7" for Z-purlins. This drives the shop drawing cut length.

**RISK:** These two formulas diverge. The BOM uses full eave-to-eave slope length (for material ordering — you need the full coil length). The shop drawing uses the actual cut length after deductions. This is correct behavior — do NOT merge them.

**Needed:**
- `calc/bom.py`: No change to material length. But add rafter CUT length to geometry dict so shop drawings get it directly.
- `shop_drawings/config.py` line 970: The 7" hardcoded Z-purlin deduction (3.5" × 2) must become configurable — use `z_eave_overhang_in × 2` from config instead.
- C-purlin: cut length = building width − 2 × roofing_overhang (no Z deduction)
- Z-purlin: cut length = building width − 2 × roofing_overhang − 2 × z_eave_overhang_in

**Files:** `calc/bom.py` (add cut length to geometry), `shop_drawings/config.py` (parameterize Z deduction)

### 2.2 Purlin Piece Length Calculation (NEW — replaces simple LF calc)

**Current state (`calc/bom.py` lines 956-980):**
- Z-Purlin BOM: `purlin_net = n_purlin_lines × building_length_ft` (total linear feet, no piece breaks)
- Piece count: `n_purlin_lines × n_bays` (assumes 1 piece per bay per line — wrong for multi-bay purlins)
- Coil used: `z_purlin_20` (20.125" 12GA)
- No C-purlin coil option at all — currently hardcoded to Z only

**RISK:** Changing piece count/length will change the BOM total weight and cost. This is the correct behavior, but existing saved BOMs will produce different numbers on recalculation. Consider versioning or flagging.

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

**Needed — C-purlin coil option:**
- Currently only Z-purlin coil exists in BOM. Need to add C-purlin coil type to COILS dict in `calc/bom.py`.
- When `purlin_type = "C"`, use C-purlin coil pricing instead of Z.

**File:** `calc/bom.py` — new purlin piece-break function, called from existing purlin calculation. Must also update existing piece count and net LF formula.

**Interaction with `shop_drawings/purlin_gen.py`:**
- `calc_purlin_groups()` (line 58) already does its own piece-break math for shop drawings. The BOM and shop drawing piece-break logic MUST produce the same results.
- **Recommendation:** Extract piece-break logic into a shared function in `calc/bom.py` (or new `calc/purlin_layout.py`) that both BOM and `purlin_gen.py` call. Do NOT have two independent implementations.

**Existing `config.py` values that already align with PURLIN_RULES.md:**
- `PURLIN_DEFAULTS["max_length_ft"]` = 53 (hard cap) ✓
- `PURLIN_DEFAULTS["z_overhang_default_ft"]` = 6.0 (Z-extension past rafter) — BUT rules say default 4'. **CONFLICT: config says 6', rules say 4'.** Resolve: the 6' was set before rules were finalized. Change default to 4' per PURLIN_RULES.md, make editable.
- `PURLIN_DEFAULTS["splice_overlap_in"]` = 6.0 ✓
- `PURLIN_DEFAULTS["end_extension_past_rafter_in"]` = 4.0 ✓
- `PURLIN_DEFAULTS["facing"]` already has correct rules ✓

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
- **CRITICAL:** `calc_purlin_groups()` (line 58) has its own length formula: `bay_size + 2*overhang_ft` for Z, `bay_size + end_ext` for C. This must be replaced with the shared piece-break function from Section 2.2 to avoid divergence with BOM numbers.
- The function already handles first/middle/last grouping and splice checks — preserve this structure but feed it correct lengths.

### 3.7 Rafter Generator (`shop_drawings/rafter_gen.py`) — UPDATE

- `_calc_rafter_data()` (line 52) calls `calc_rafter_length()` which hardcodes 7" Z-deduction. Must be parameterized (see Section 2.1).
- `_draw_top_view()` (line 186) draws clip positions at linear offsets. When purlins are angled, the attachment surface footprint on the rafter changes — the rectangular grid assumption needs an `if angled_purlins` branch.

### 3.8 Work Order Fab Stickers (`shop_drawings/wo_fab_stickers.py`) — VERIFY

- Uses `purlin_type` (line 308) for machine assignment. Adding C-purlin option to BOM means stickers must handle both purlin types. Currently reads `purlin_type` from config — should work as-is if the field is populated.
- Uses `_n_purlin_lines()` (line 106) calculated from `purlin_spacing_ft`. In solar mode, purlin spacing is panel-dictated — ensure `purlin_spacing_ft` in config is set correctly BEFORE sticker generation runs.

### 3.9 Shipping Generator (`shop_drawings/shipping_gen.py`) — VERIFY

- References `purlin_spacing_ft`, `building_width_ft`, `purlin_type`. Same concern as stickers — ensure these values reflect solar mode when applicable.

### 3.10 PDF/Excel Exports (`outputs/pdf_gen.py`, `outputs/excel_gen.py`) — LOW RISK

- Both use `geometry.get()` with safe defaults. New fields added to geometry dict will be silently ignored by existing code. No breakage risk.
- To DISPLAY new fields (piece counts, solar panel info), add new lines to the BOM summary section in both generators.

---

## 4. Config and Data Flow

### 4.1 Config Pipeline (FULL TRACE)

The data flows through 5 layers. Every new field must exist in ALL layers:

```
SA Estimator UI (templates/sa_calc.py, JS building object)
    ↓ saves via AJAX to
BuildingConfig dataclass (calc/bom.py line 50)
    ↓ feeds into
BOM calculation → geometry dict (calc/bom.py line 846)
    ↓ saved to project JSON, then loaded by
_load_buildings_list → _enrich_config_for_building (tf_handlers.py line 8104)
    ↓ builds
ShopDrawingConfig dataclass (config.py line 742) → interactive templates
```

**Layer 1 — SA Estimator JS object** (`templates/sa_calc.py`):
New fields to add to the JS building data model:
```javascript
max_purlin_length_ft: 45,
z_extension_ft: 4,
z_eave_overhang_in: 3.5,
purlin_cost_per_ft_c: null,
purlin_cost_per_ft_z: null,
solar_mode: false,
panel_width_mm: null,
panel_length_mm: null,
mounting_hole_dist_mm: null,
mounting_hole_inset_mm: null,
panels_across: null,
panels_along: null,
panel_gap_width_in: 0.25,
panel_gap_length_in: 0.25,
panel_orientation: 'landscape',
solar_slope_deg: 5,
rafter_spacing_override_ft: null
```

**Layer 2 — BuildingConfig** (`calc/bom.py` line 50):
Add fields to the dataclass. NOTE: `angled_purlins` and `purlin_angle_deg` already exist (lines 82-83). `purlin_type` already exists (line 92).

**Layer 3 — Geometry dict** (`calc/bom.py` line 846):
Add new fields to the geometry dict so they flow downstream. `angled_purlins` and `purlin_angle_deg` already included (lines 883-884).

**Layer 4 — `_enrich_config_for_building`** (`tf_handlers.py` line 8104):
Already passes `angled_purlins`, `purlin_angle_deg`, `purlin_type`. Add solar fields.

**Layer 5 — ShopDrawingConfig** (`config.py` line 742):
Already has `is_solar: bool = False` (line 817), `purlin_type`, `purlin_spacing_ft`, `purlin_overhang_ft`, `purlin_end_extension_in`. Add:
- `max_purlin_length_ft`, `z_extension_ft`, `z_eave_overhang_in`
- `purlin_cost_per_ft_c`, `purlin_cost_per_ft_z`
- All solar panel fields
- Must also add to `_FLOAT_FIELDS`, `_BOOL_FIELDS`, `_INT_FIELDS` sets for `ensure_numeric()` to work

### 4.2 EXISTING CONFIG VALUES — Conflicts to Resolve

| Field in config.py | Current Value | PURLIN_RULES.md Value | Action |
|---|---|---|---|
| `PURLIN_DEFAULTS["z_overhang_default_ft"]` | 6.0 | 4.0 | Change to 4.0 |
| `PURLIN_DEFAULTS["max_length_ft"]` | 53.0 | 53 (hard cap), 45 (default max) | Keep 53 as hard cap, add `default_max_length_ft: 45` |
| `RAFTER_DEFAULTS["z_purlin_deduction_in"]` | 7.0 | 7.0 (3.5×2) | Keep, but make source configurable |
| `ShopDrawingConfig.purlin_overhang_ft` | 6.0 | 4.0 | Change to 4.0 |
| `BuildingConfig.purlin_angle_deg` | 15.0 | 90 (perpendicular default) | Change to 90.0 |

### 4.3 `_load_shop_config` and `_enrich_config_for_building` (tf_handlers.py)

These functions populate the config dict passed to interactive drawings. Need to:
- Include all new purlin/solar fields from the building's saved data.
- Pass through to the PURLIN_LAYOUT_CONFIG_JSON template variable.
- The `_enrich_config_for_building` function (line 8104) uses a pattern of `if target.get("field"): enriched["field"] = ...` — follow same pattern for new fields.

### 4.4 Database/Storage Schema

Buildings are stored as JSON blobs within project version files (not fixed DB columns). The `_load_buildings_list()` function reads from `projects/{job_code}/versions/*.json`. This means:
- **No DB migration needed** — JSON is flexible, new fields just appear.
- Old projects won't have solar fields — code must handle `None`/missing gracefully.
- `BuildingConfig` defaults ensure backward compatibility.

---

## 5. Immediate BOM Fix — Remove Eave Struts

### 5.0 Eave Struts Are Incorrect (ALL buildings)

**Discovery:** There is NO separate eave strut on any Titan Carports / Structures America building. The front and back purlins (first and last purlin lines) ARE the eave. The BOM currently adds 2 "Eave Strut" line items per building (`calc/bom.py` lines 528-550, `include_eave_struts: bool = True`).

**Fix required (Phase 0 — before any purlin integration):**
1. `calc/bom.py` line 106: Change `include_eave_struts: bool = True` to `include_eave_struts: bool = False`
2. `calc/bom.py` lines 528-550: The eave strut BOM block should be disabled or removed.
3. `templates/sa_calc.py`: If there's an eave strut checkbox/toggle in the SA estimator UI, remove it or default to off.
4. `tf_handlers.py` line 8455: The eave strut entry in purlin group data should be removed.
5. `templates/purlin_drawing_v2.py` lines 361, 528: The "eave strut" type handling in the purlin drawing should be removed.

**Impact:** This reduces BOM cost for every building. All new calculations will be lower. Existing saved BOMs are unaffected until recalculated.

---

## 6. Breakage Risk Assessment

### 5.1 HIGH RISK — BOM Numbers Will Change

Adding piece-break logic to `calc/bom.py` will change purlin LF totals, piece counts, and therefore costs. Currently the BOM uses `n_purlin_lines × building_length_ft` as total purlin LF. With piece breaks, the total will include overlap zones (Z-purlins add 6" overlap at every joint) and may change piece counts.

**Mitigation:** All BOM results are versioned in project JSON files. Old BOMs keep their saved values. Only recalculation produces new numbers. The BOM diff feature (already implemented) will highlight changes when recalculating.

### 5.2 MEDIUM RISK — Rafter Length Divergence

`shop_drawings/config.py` `calc_rafter_length()` hardcodes 7" Z-deduction. If we make `z_eave_overhang_in` configurable (e.g., user sets 4" per side = 8" total instead of 7"), the shop drawing cut length changes. Existing rafter drawings for saved projects will render differently.

**Mitigation:** Only affects new calculations. Saved shop drawing configs preserve their values. Add `z_eave_overhang_in` to ShopDrawingConfig with default 3.5 (→ 7" total) to match existing behavior.

### 5.3 MEDIUM RISK — `purlin_gen.py` and BOM Piece Counts Must Match

Two independent piece-break implementations (BOM and `purlin_gen.calc_purlin_groups()`) will produce different numbers if they diverge.

**Mitigation:** Extract shared piece-break engine. Both BOM and purlin_gen call the same function.

### 5.4 LOW RISK — PDF/Excel Exports

Exports use `.get()` with defaults. New geometry fields will be silently ignored. No breakage. Add display logic for new fields in a later pass.

### 5.5 LOW RISK — Stickers, Shipping, Cut Lists

Read existing config fields (`purlin_type`, `purlin_spacing_ft`). As long as these are populated correctly for solar mode, no breakage. Verify during Phase 2 testing.

### 5.6 NO RISK — TC Estimator

TC Estimator reads BOM line items for pricing. New purlin line items (C-purlin option, solar hardware) will appear as additional BOM rows. TC Estimator iterates all rows — no schema dependency. No changes needed to TC Estimator code.

### 5.7 CRITICAL DEFAULT CONFLICT — Z-Overhang 6' vs 4'

`config.py PURLIN_DEFAULTS["z_overhang_default_ft"]` = 6.0 but PURLIN_RULES.md says default 4'. The existing `purlin_gen.py` uses this 6' value for all current shop drawings. Changing to 4' will affect all NEW purlin drawings.

**Mitigation:** Change default to 4'. Existing saved configs keep their 6' value. Only new projects get 4'. The interactive drawing allows override.

### 5.8 CRITICAL DEFAULT CONFLICT — Purlin Angle Default

`BuildingConfig.purlin_angle_deg` defaults to 15.0 (line 83 of bom.py). This should default to 90 (perpendicular) since angled purlins are the exception, not the rule. The `angled_purlins` bool is False by default so the angle value is ignored, but it's confusing and could cause bugs if `angled_purlins` gets toggled on without setting the angle.

**Mitigation:** Change default to 90.0.

---

## 6. Implementation Phases

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

## 7. Files Affected Summary

| File | Phase | Change Type | Risk |
|---|---|---|---|
| `templates/sa_calc.py` | 1, 2 | Major — new input sections | Low (additive) |
| `config.py` | 1, 2 | Add defaults, fix conflicts | Medium (default changes) |
| `calc/defaults.py` | 1, 2 | Add defaults | Low (additive) |
| `calc/bom.py` | 1, 2, 3 | Major — piece breaks, solar dims, comparison | High (changes BOM numbers) |
| `templates/purlin_layout.py` | 1, 2, 3, 4 | Wire to config, add facing/plates/angle | Low (new features) |
| `templates/purlin_drawing_v2.py` | 5 | Add facing, overlap detail | Low (visual only) |
| `templates/rafter_drawing.py` | 1, 4 | P1/P2 plates, rafter length | Medium (dimensions) |
| `tf_handlers.py` | 1, 2 | Config enrichment for new fields | Low (additive) |
| `shop_drawings/config.py` | 1 | Parameterize Z-deduction in calc_rafter_length | Medium (formula change) |
| `shop_drawings/purlin_gen.py` | 1, 4, 5 | Replace with shared piece-break engine | High (must match BOM) |
| `shop_drawings/rafter_gen.py` | 4 | Angled purlin clip positions | Medium (geometry) |
| `shop_drawings/cutlist_gen.py` | 5 | Piece-break data, angled adjustment | Low (additive) |
| `shop_drawings/wo_fab_stickers.py` | 2 | Verify solar mode fields flow through | Low (verify only) |
| `shop_drawings/shipping_gen.py` | 2 | Verify solar mode fields flow through | Low (verify only) |
| `outputs/pdf_gen.py` | 5 | Add new field display | Low (additive) |
| `outputs/excel_gen.py` | 5 | Add new field display | Low (additive) |

---

## 9. Open Questions — Status Tracker

### Resolved
1. ~~**Database storage**~~ → JSON blobs in project version files. No DB migration needed.
2. ~~**C-purlin coil specs**~~ → Same as Z-purlin: 20.125" 12GA G90. Same lbs/ft and pricing.
3. ~~**Eave struts**~~ → NO eave struts on any building. Front/back purlins ARE the eave. Remove from BOM (Section 5.0).
4. ~~**Solar endcaps**~~ → Different piece: 9" × 15" flat plate welded on rafter ends. NOT the U-channel endcap. Used ONLY when purlins are angled (not solar-specific). 2 per rafter.
5. ~~**Hurricane straps + solar**~~ → Same count (4 per rafter) for solar and standard. No change needed.
6. ~~**Cost per foot vs weight pricing**~~ → They are the same calculation: cost/ft = lbs/ft × coil_price/lb. No conflict.
7. ~~**Girt cut list**~~ → Girts get their OWN cut list and piece-break output, separate from roof purlins, but appear on the same purlin shop drawings (same material).
8. ~~**Panel type consistency**~~ → One panel type per project. Specs entered once, apply to all buildings.
9. ~~**Z-overhang default**~~ → Confirmed 6' (matches existing code). PURLIN_RULES.md updated.

### Still Open
10. **Panel spec library**: Should we build a saved panel spec dropdown (CS3K-P, etc.) so users don't re-enter dimensions every time?
11. **PDF export of comparison**: Should the 4-option cost comparison be exportable as a standalone PDF for customer quotes?
12. **Multiple buildings with different modes**: Can one job have solar building + standard building? Solar toggle is per-building in BuildingConfig, but SA estimator UI needs to handle this.
13. **Panel spec validation**: Validate user-entered dimensions are reasonable (width 800-1200mm, length 1500-2400mm)?
14. ~~**Solar endcap plate in BOM**~~ → RESOLVED: 9"×15" 10GA flat plate, only for ANGLED purlins (not solar-specific). 2 per rafter. Same gauge as P1/P2.
15. ~~**Solar perpendicular purlins**~~ → RESOLVED: Solar with perpendicular purlins uses normal P2 plates. Endcap plate only for angled.
16. ~~**P1/P2 plate gauge**~~ → RESOLVED: Both P1 and P2 are 10GA.
17. ~~**Eave strut in purlin drawing**~~ → RESOLVED: Remove eave_strut type handling entirely from purlin_drawing_v2.py.
18. ~~**Panel spec library**~~ → RESOLVED: Manual entry is fine. Add a small diagram showing which measurements are needed.
19. ~~**Mixed-mode jobs**~~ → RESOLVED: Yes, per-building. One building can be solar, another standard, in the same project.
20. ~~**P1 position on angled rafter**~~ → RESOLVED: First P1 plate center is ~2-5/16" from rafter end.

21. ~~**U-channel endcap in solar mode**~~ → RESOLVED: Yes, U-channel endcaps are still used on ALL buildings including solar. They go over the purlin ends at both building ends. Internal dimension matches purlin depth (e.g., 12" purlin = 12" internal endcap).
22. ~~**Rafter end cap plate — angled solar**~~ → RESOLVED: The endcap plate is BELOW the panel line. Panels sit on purlin flanges above the rafter — no interference with the end cap plate.
23. ~~**Stagger calculation**~~ → RESOLVED: `purlin_spacing × tan(angle_from_perpendicular)`. All pieces still break at rafter centers.
24. ~~**Purlin depth**~~ → RESOLVED: Default 12". Make it user-configurable. Warn that different depths require different coil widths — prompt user to input coil specs if they change from 12".
25. ~~**Roofing panels vs purlin piece breaks**~~ → RESOLVED: Independent. Roofing panels only care about WHERE purlins land, not how they're spliced.
26. ~~**P1 count formula**~~ → RESOLVED: 1 P1 plate per purlin line per rafter = `n_purlin_lines × n_rafters`.
27. ~~**Tek screw clarification**~~ → RESOLVED: purlin-to-clip and P1 clip screws are the same thing — 8 total per connection, not 8+8.

28. ~~**Purlin flange width**~~ → RESOLVED: Top flange 3.5", bottom flange 3.5", lips 0.75", web 12". Usable flange for bolt holes = 3.5" - 0.75" lip = 2.75" per flange (minus 0.5" clearance each side = 1.75" usable).
29. ~~**SA estimator solar toggle**~~ → RESOLVED: Keep purlin spacing input visible but grayed out with note "Spacing is dictated by panels in solar mode."
30. ~~**Cost comparison auto-select**~~ → RESOLVED: Highlight cheapest with "Recommended" badge. Let user pick — do NOT auto-select into BOM.
31. ~~**Girt spacing on solar**~~ → RESOLVED: Still 5' OC default for solar buildings with walls. User can change if needed.
32. ~~**P1/P2 plate count formula**~~ → RESOLVED: Per rafter: P1 = n_purlin_lines - 2 (perpendicular) or n_purlin_lines (angled). P2 = 2 per rafter (one each eave) for perpendicular only. Exception: no P2 where rafter splice plate exists.

33. ~~**Rafter splice vs P2**~~ → RESOLVED: Rafter splices at > 53' length (already coded in rafter_gen.py). Splice plate occupies connection point, no P2 there. Existing code handles this correctly.
34. ~~**Rafter splice frequency**~~ → RESOLVED: Already implemented — rafter > 53' triggers splice. Max single piece = 53'. Splice within 10' of column, 2 plates per splice (10GA G90, 20-3/4" × 1'-6"). See shop_drawings/config.py line 279+.
35. ~~**Purlin BOM line items**~~ → RESOLVED: BOM should show purlins broken out by piece length (e.g., "18'-8" × 24 pcs") not as a single total LF line. Each distinct length = its own line item.
36. ~~**Z-purlin splice detail**~~ → RESOLVED: Per user's engineering drawing — splice uses a short purlin segment on TOP of continuous purlin, centered over rafter (boxed beam). 8 × #10 tek screws total. Splice purlin must match depth and gauge. Replaces old 4/S3.1 detail.
37. ~~**Sag rods**~~ → RESOLVED: Sag rods do NOT affect purlin layout at all. They attach to bottom of purlin flanges. Completely independent system.

### Still Open
38. **Purlin splice segment length**: The splice detail shows a short purlin piece on top at the rafter. How long is that splice segment? Is it a fixed length (e.g., 2') or does it scale with the rafter width?
39. **Shared piece-break engine**: The codebase has TWO independent piece-break implementations (purlin_gen.py and the interactive purlin_layout.py). When we build Phase 1, should we create one shared Python engine that both use, or keep the interactive JS version separate and just make sure the logic matches?
40. **TC Estimator impact**: Does the purlin piece-break and solar mode affect TC pricing at all? Or does the TC estimator only care about total LF and material weight (which the BOM already provides)?

---

*End of integration plan.*
*Updated: 2026-04-20 — Post-audit revision with breakage analysis, config conflicts, full data flow trace, and Q&A resolutions (rounds 1-3).*
