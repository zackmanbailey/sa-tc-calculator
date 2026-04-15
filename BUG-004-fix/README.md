# BUG-004 Fix: Field Operations Page

## What This Fixes
- `/field-ops` route no longer returns 404
- New **Field Operations** hub with three tabs:
  - **Installation Tracking** (fully functional) — track per-building installation progress, daily logs, delays
  - **Crew Dispatch** (placeholder — Phase 14)
  - **Inspections & Punch List** (placeholder — Phase 14)
- Auto-create installations from saved SA BOM data
- Installation status pipeline: Not Started → Mobilizing → Site Prep → Foundations → Erection → Roofing → Punch List → Complete
- Daily log entries per installation (crew count, hours, weather, work performed)
- Delay reporting with categorized reasons

## Files

### 1. `shop_drawings/field_ops.py` (NEW FILE)
**Add**: `combined_calc/shop_drawings/field_ops.py`
**From**: `BUG-004-fix/field_ops.py`

Backend data module with:
- Installation CRUD and status management
- Daily log entries
- Delay tracking
- Auto-create from BOM data
- Storage: `data/field_ops/{job_code}/field_ops.json`

### 2. `templates/field_ops.py` (NEW FILE)
**Add**: `combined_calc/templates/field_ops.py`
**From**: `BUG-004-fix/field_ops_template.py`

Full HTML template with:
- Job selector dropdown
- Summary cards (total, complete, in progress, avg progress, delays)
- Installation card grid with progress bars
- Status change dropdowns
- Daily log modal
- Delay report modal
- Placeholder tabs for Crew Dispatch and Inspections

### 3. `tf_handlers.py` (PATCH — add handlers + routes)
**Reference**: `BUG-004-fix/tf_handlers_field_ops_patch.py`

Steps:
1. Add `FIELD_OPS_DIR` constant:
```python
FIELD_OPS_DIR = os.path.join(BASE_DIR, "data")
```

2. Add imports:
```python
from shop_drawings.field_ops import (
    load_field_ops, save_field_ops, create_installation,
    update_installation_status, add_daily_log, add_delay,
    get_installation_summary, get_field_ops_for_project,
    auto_create_from_bom
)
from templates.field_ops import get_field_ops_html
```

3. Copy 7 handler classes from the patch file

4. Add routes to `get_routes()`:
```python
(r"/field-ops", FieldOpsPageHandler),
(r"/api/field-ops", FieldOpsDataHandler),
(r"/api/field-ops/install", FieldOpsCreateInstallHandler),
(r"/api/field-ops/status", FieldOpsStatusHandler),
(r"/api/field-ops/daily-log", FieldOpsDailyLogHandler),
(r"/api/field-ops/delay", FieldOpsDelayHandler),
(r"/api/field-ops/auto-create", FieldOpsAutoCreateHandler),
```

### 4. `templates/shared_nav.py` (PATCH — add nav link)
Find the "Current Project" section in the sidebar navigation.
Add this link:
```html
<a href="/field-ops">Field Ops</a>
```

## Installation Status Pipeline
```
Not Started → Mobilizing → Site Prep → Foundations → Steel Erection → Roofing & Trim → Punch List → Complete
                                                                                                    ↕
                                                          Any status ↔ On Hold
```

## API Endpoints

| Method | Endpoint | Purpose |
|--------|---------|---------|
| GET | `/field-ops` | Field Operations page |
| GET | `/api/field-ops?job_code=X` | Get field ops data + summary |
| POST | `/api/field-ops/install` | Create installation record |
| POST | `/api/field-ops/status` | Update installation status |
| POST | `/api/field-ops/daily-log` | Add daily log entry |
| POST | `/api/field-ops/delay` | Report a delay |
| POST | `/api/field-ops/auto-create` | Auto-create from BOM data |

## Testing
1. Navigate to `/field-ops` — should load without 404
2. Select a project from the dropdown
3. Click "Auto-Create from BOM" — should create installation cards for each building
4. Change an installation status using the dropdown
5. Add a daily log entry
6. Report a delay
7. Verify progress bars update with status changes
8. Check "Crew Dispatch" and "Inspections" tabs show "Coming Soon" placeholders
