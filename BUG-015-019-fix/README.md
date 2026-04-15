# BUG-015 thru 019 Fix: Low Priority Polish Batch

## BUG-015: Sidebar Navigation Click Fix
**Problem**: Sidebar clicks occasionally fail to register.
**Root Cause**: Child elements (icons, labels, badges) intercepting clicks instead of the parent `<a>` tag. Section labels can also intercept clicks near the top of navigation groups.
**Fix**: CSS `pointer-events: none` on child elements, `z-index` on nav items.

### Patch: `templates/shared_nav.py`
Add the CSS from `bug015_sidebar_fix.css` to the NAV_CSS string.

---

## BUG-016: TC Summary Per-Building SA Line Items
**Problem**: TC Summary tab only shows aggregate SA cost, no per-building breakdown.
**Fix**: Collapsible per-building table in the Summary tab showing weight, material cost, and sell price per building.

### Patch: `templates/tc_quote.py`
**Reference**: `bug016_tc_summary_per_building.js`

1. Add the HTML for the per-building breakdown card in the Summary tab (after the main summary table, before intelPanel, ~line 583)
2. Add the `renderPerBuildingBreakdown()` function to the script section

Uses the same `/api/project/bom-summary` endpoint created for BUG-006.

---

## BUG-017: Shop Drawing PDF Export
**Problem**: No way to download shop drawings as PDF files.
**Fix**: Server-side PDF generation using ReportLab. Export single drawing or all drawings for a project.

### New File: `shop_drawings/drawing_pdf_export.py`
Add `BUG-015-019-fix/bug017_shop_drawing_pdf_export.py` as `combined_calc/shop_drawings/drawing_pdf_export.py`

### Patch: `tf_handlers.py`
Add `ShopDrawingPDFExportHandler` and `ShopDrawingAllPDFExportHandler` classes and routes:
```python
(r"/api/shop-drawings/export-pdf/([^/]+)/([^/]+)", ShopDrawingPDFExportHandler),
(r"/api/shop-drawings/export-all-pdf/([^/]+)", ShopDrawingAllPDFExportHandler),
```

### Patch: `templates/shop_drawings.py`
Add export buttons to the shop drawings toolbar:
```html
<button onclick="exportDrawingPDF()" class="btn-outline">Export PDF</button>
<button onclick="exportAllPDF()" class="btn-outline">Export All PDFs</button>
```

Dependencies: `pip install PyPDF2` for multi-page merge (optional — single-page works without it).

---

## BUG-018: Global Search Backend
**Problem**: Search UI exists in the nav (Ctrl+K), but `/api/search` endpoint doesn't exist.
**Fix**: Backend search handler that searches across projects, customers, coils, and work orders.

### Patch: `tf_handlers.py`
**Reference**: `bug018_global_search.py`

Add `GlobalSearchHandler` class and route:
```python
(r"/api/search", GlobalSearchHandler),
```

The existing `shared_nav.py` search overlay automatically connects to this endpoint. Searches:
- Projects (by job code, name, customer)
- Customers (by name, company, email)
- Inventory coils (by name, gauge, heat number)
- Work orders (by WO ID, job code)

Returns up to 10 results, typeahead with 250ms debounce.

---

## BUG-019: Audit Trail / Activity Log
**Problem**: No system-wide log of who changed what and when.
**Fix**: JSONL-based audit log with categorized actions, user tracking, and admin viewer page.

### New File: `shop_drawings/audit_trail.py`
Add `BUG-015-019-fix/bug019_audit_trail.py` as `combined_calc/shop_drawings/audit_trail.py`

### Patch: `tf_handlers.py`
Add imports and three handler classes:
```python
from shop_drawings.audit_trail import log_action, get_recent_logs, get_audit_stats, ACTION_CATEGORIES
```
Routes:
```python
(r"/api/audit-log", AuditLogHandler),
(r"/api/audit-log/recent", AuditLogRecentHandler),
(r"/admin/audit", AuditLogPageHandler),
```

### Integration
To log actions from existing handlers, add calls to `log_action()`:
```python
from shop_drawings.audit_trail import log_action
log_action(BASE_DIR, "wo.status_change", user="admin",
           details={"wo_id": "WO-001", "old_status": "queued", "new_status": "approved"},
           job_code="SA-2024-001")
```

### Storage
- File: `data/audit/audit_log.jsonl` (append-only, one JSON object per line)
- No retention limit — logs accumulate indefinitely
- Admin-only access for viewing

### Action Categories
Projects, SA/TC estimates, work orders, inventory, field ops, admin, shipping — 30+ categorized action types.

---

## Testing

### BUG-015
1. Click every sidebar nav link — all should register on first click
2. Test in collapsed sidebar mode
3. Test on mobile viewport width

### BUG-016
1. Open TC Summary tab for a multi-building project
2. Click the per-building breakdown header → table should expand
3. Verify each building's weight, cost, and sell price

### BUG-017
1. Open shop drawings for a project
2. Click "Export PDF" → should download a PDF
3. Click "Export All PDFs" → should download combined PDF

### BUG-018
1. Press Ctrl+K → search overlay opens
2. Type a project job code → results should appear
3. Type a customer name → customer results appear
4. Click a result → navigates to that item

### BUG-019
1. Navigate to `/admin/audit`
2. Verify stats cards show data
3. Filter by action category → results update
4. Perform an action (e.g., approve a work order) → verify it appears in the log
