# BUG-006 Fix: TC Estimator Per-Building Concrete Breakdown

## What This Fixes
- Concrete section now shows a **per-building breakdown table** instead of a single aggregate total
- Auto-populates from SA BOM data (pier counts, footing depths per building)
- Default 24" diameter hole, editable per building
- Each building's depth pulled from SA BOM calculations
- User can override any value per building
- Per-building detail appears in **PDF and Excel exports**

## Files

### 1. `templates/tc_quote.py` (PATCH — replace concrete card + JS)

#### Step A: Replace the Concrete HTML card
**Find** the concrete card (lines 248-281):
```html
<div class="card" id="card-concrete">
  ...
</div>
```
**Replace** with contents of `tc_quote_html_patch.html`

#### Step B: Replace JS functions
**Find** `syncConcreteFromSA()` (line 685) and `calcConcrete()` (line 699).
**Replace** both functions with the contents of `tc_quote_concrete_patch.js`.
The new JS includes:
- `loadBuildingConcreteData()` — fetches per-building data from SA BOM
- `initSingleBuildingFallback()` — fallback when no BOM data available
- `addConcreteBuilding()` / `removeConcreteBuilding()` — manual add/remove
- `renderConcreteTable()` — renders the per-building table
- `calcConcrete()` — recalculates totals from all buildings
- `buildConcretePayload()` — builds the new concrete data structure for saves/exports

#### Step C: Update buildPayload()
**Find** the concrete line in `buildPayload()` (line 1009-1010):
```javascript
concrete: { n_piers: numVal('conc_n_piers'), dia_in: numVal('conc_dia_in'),
  depth_ft: numVal('conc_depth_ft'), price_cy: numVal('conc_price_cy'), total: concreteCost },
```
**Replace** with:
```javascript
concrete: buildConcretePayload(),
```

### 2. `tf_handlers.py` (PATCH — add BOM summary endpoint)
**Reference**: `tf_handlers_bom_summary_patch.py`

Steps:
1. Copy `ProjectBOMSummaryHandler` class and paste it AFTER `CalculateHandler` (~line 823)
2. Add this route to `get_routes()`:
```python
(r"/api/project/bom-summary", ProjectBOMSummaryHandler),
```

### 3. `outputs/tc_pdf_gen.py` (PATCH — add concrete detail table)
**Reference**: `tc_pdf_concrete_patch.py`

Steps:
1. Add the `_render_concrete_detail()` function BEFORE `generate_construction_quote_pdf()`
2. In `generate_construction_quote_pdf()`, after the equipment detail section (~line 185), add:
```python
concrete_data = costs.get("concrete", {})
if concrete_data.get("buildings") and len(concrete_data.get("buildings", [])) > 1:
    _render_concrete_detail(story, concrete_data, None)
```

### 4. `outputs/tc_excel_gen.py` (PATCH — add concrete detail section)
**Reference**: `tc_excel_concrete_patch.py`

In `generate_construction_quote_excel()`, after the equipment detail block, add the concrete per-building detail rendering from `tc_excel_concrete_patch.py`.

## Per-Building Concrete Table

| Column | Description |
|--------|------------|
| Building | Building name (editable, auto-filled from SA) |
| # Piers | Number of pier footings (from SA BOM's n_struct_cols) |
| Dia (in) | Hole diameter in inches (default 24") |
| Depth (ft) | Footing depth (from SA BOM's footing_depth_ft) |
| $/CY | Price per cubic yard (global default with per-building override) |
| Cubic Yards | Calculated: pi * r^2 * depth / 27 * n_piers * 1.10 (10% waste) |
| Cost | Cubic Yards * $/CY |

## Data Flow
```
SA BOM Calculation
  └→ Per-building geometry (concrete_n_piers, concrete_cy, footing_depth_ft)
      └→ /api/project/bom-summary endpoint
          └→ TC Estimator auto-populates per-building table
              └→ User can override any values
                  └→ buildConcretePayload() → save/export
                      └→ PDF/Excel show per-building detail table
```

## Testing
1. Open TC Estimator for a project with saved SA BOM data
2. Concrete section should show a table with one row per building
3. Verify pier counts and depths match SA BOM values
4. Change a building's diameter → total should recalculate
5. Click "Add Building" → new row appears
6. Remove a building → row disappears, total updates
7. Change global $/CY → all buildings update
8. Export PDF → should show per-building concrete detail table
9. Export Excel → should show per-building concrete detail section
10. Test with no SA BOM data → should fall back to single building using SA aggregate values
