# BUG-008, 009, 013, 014 Fix: Medium Priority UX Batch

## BUG-008: TC Estimator Card Reorganization
**Problem**: Fuel/transport fields hard to find in the TC Estimator.
**Fix**: Reorganize cards into logical sections with colored section headers.

### Patch: `templates/tc_quote.py`
**Reference**: `tc_quote_layout_patch.html`

Add section dividers between card groups in `#tab-quote`. The cards stay the same, just grouped:

1. **SITE WORK** (blue header) — Concrete, Labor, Equipment, Drilling
2. **LOGISTICS & TRAVEL** (amber header) — Shipping, Fuel, Hotels, Per Diem, Transport
3. **ADDITIONAL COSTS** (indigo header) — Miscellaneous

Insert the section divider HTML from `tc_quote_layout_patch.html` before each group.

---

## BUG-009: Misc Items Common Presets
**Problem**: Misc Items tab lacks guidance on what to add.
**Fix**: Dropdown with 15 common misc items (permits, inspections, dumpster, porta potty, etc.) plus custom entry.

### Patch: `templates/tc_quote.py`
**Reference**: `bug009_misc_presets.js`

1. **Replace** the misc card HTML (lines 560-571) with the enhanced version from the patch file
2. **Replace** the `addMiscItem()` and `renderMiscTable()` functions (lines 836-863) with the new versions

New functions added:
- `addMiscPreset()` — adds selected preset item with default price
- `MISC_PRESET_LABELS` — maps preset keys to display names
- Enhanced `renderMiscTable()` — shows helpful placeholder text when empty

Preset items include: Building Permits ($1,500), Inspections ($500), Site Cleanup ($800), Dumpster Rental ($450), Porta Potty ($250), Temporary Power ($350), Survey/Layout ($600), Performance Bond, Insurance, Welding Supplies ($400), Anchor Bolts ($300), Grout ($200), Water Truck ($500), Crane Mobilization ($1,200), Safety Supplies ($350).

---

## BUG-013: Machine Assignment Reassignment
**Problem**: Machine assignments on work order items cannot be changed after creation.
**Fix**: Machine badge becomes a dropdown select. Any shop role can reassign. Logged in item notes.

### Patch 1: `shop_drawings/work_orders.py`
**Reference**: `bug013_machine_reassign_patch.py`

Add the `reassign_machine()` function after `qr_scan_finish()`. Also add `VALID_MACHINES` list.

Rules:
- Items in "in_progress" or "complete" status cannot be reassigned
- Change is logged in item notes with timestamp and who changed it
- All shop roles can reassign (admin, estimator, shop, qc)

### Patch 2: `tf_handlers.py`
Add `WorkOrderMachineReassignHandler` class and route:
```python
(r"/api/work-orders/reassign-machine", WorkOrderMachineReassignHandler),
```

### Patch 3: `templates/work_orders.py`
Replace the machine badge `<span>` with a `<select>` dropdown (see patch file for exact HTML).
Add `reassignMachine()` JS function.

---

## BUG-014: Building Duplication & Templates
**Problem**: Each SA building must be configured from scratch.
**Fix**: Duplicate button + save/load template system.

### Patch: `templates/sa_calc.py`
**Reference**: `bug014_building_duplicate_patch.js`

1. **Replace** the building buttons (lines 235-237) with the enhanced button group that includes:
   - Duplicate Selected
   - Save as Template
   - Load Template

2. **Add** the modal HTML for save/load template dialogs (see patch file)

3. **Add** the JS functions from the patch file:
   - `duplicateBuilding()` — deep clones selected building
   - `showSaveTemplateModal()` / `saveTemplate()` — save to localStorage
   - `showLoadTemplateModal()` / `loadTemplate()` — load from saved templates
   - `deleteTemplate()` — remove a saved template

Templates are stored in localStorage with key `tf_building_templates`. Falls back to API endpoint `/api/building-templates` if localStorage is unavailable.

## Testing

### BUG-008
1. Open TC Estimator → verify three section headers appear (Site Work, Logistics & Travel, Additional)
2. Fuel & Gas card should be visually grouped with Hotels, Per Diem, and Transport

### BUG-009
1. Open TC Estimator → scroll to Misc card
2. Use the preset dropdown → select "Building Permits" → click "Add Selected"
3. Verify it adds a row with "Building Permits" and $1,500
4. Click "+ Custom Item" → verify blank row added
5. Verify totals calculate correctly

### BUG-013
1. Open a Work Order detail view
2. Machine column should show dropdown selects instead of badges
3. Change a machine → verify API call succeeds and toast shows
4. Start an item → verify its machine dropdown becomes disabled

### BUG-014
1. Open SA Estimator → add a building with custom settings
2. Click "Duplicate Selected" → verify new building appears with "(Copy)" suffix
3. Click "Save as Template" → enter name → save
4. Click "Load Template" → verify saved template appears in list
5. Click "Load" on a template → verify new building added with template values
6. Delete a template → verify it's removed from the list
