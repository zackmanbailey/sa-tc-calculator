# PROJECT DASHBOARD — Source of Truth Feature

## Overview
Central project dashboard that shows the status of every module for a given project. Each project becomes the **single source of truth** — all information is specific to that project and scanned from actual saved data.

## Status Cards
| Status | Color | Icon | Description |
|--------|-------|------|-------------|
| Complete | Green (solid, white text) | ✅ + version | Module data is saved. Shows details (cost, weight, count). |
| In Progress | Blue (solid, white text) | ⏳ | Partial data exists (e.g., some work orders done). |
| Needs Completion | Red (solid, white text) | ❌ | No data saved. Shows requirements and links to the screen. |
| Needs Attention | Amber (solid, white text) | ⚠️ | Data exists but has issues (corrupted file, etc). |

## Module Pipeline (Dependency Chain)
```
SA Estimator ──┬──> TC Estimator
               ├──> Bill of Materials ──┬──> Shop Drawings
               │                        └──> Work Orders ──┬──> Field Operations
               │                                           └──> Shipping
```

## Files

### 1. `project_tracker.py` → `combined_calc/project_tracker.py`
Backend module that scans data directories to determine module status.

- `PROJECT_MODULES`: 7 module definitions with dependency chain
- `scan_project_state(base_dir, job_code)`: Scans all directories, returns per-module status
- `list_projects_with_status(base_dir)`: Returns all projects with summary
- Individual checkers: `_check_sa_estimate`, `_check_tc_estimate`, `_check_bom`, `_check_shop_drawings`, `_check_work_orders`, `_check_field_ops`, `_check_shipping`

### 2. `project_dashboard_template.py` → `combined_calc/templates/project_dashboard_template.py`
Full HTML template with:
- Project selector dropdown
- Metadata cards (job code, customer, completion count)
- Overall progress bar
- Pipeline flow visualization (colored dots with arrows)
- Next action banner with direct link
- Module status card grid (colored cards with details)

### 3. `tf_handlers_project_dashboard_patch.py` → Add to `tf_handlers.py`
Three handler classes:
- `ProjectDashboardPageHandler` — Serves the dashboard page
- `ProjectDashboardListHandler` — API: list all projects with summary
- `ProjectDashboardStateHandler` — API: full state scan for one project

## Integration Steps

### 1. Add files
```
combined_calc/project_tracker.py
combined_calc/templates/project_dashboard_template.py
```

### 2. Add imports to `tf_handlers.py`
```python
from templates.project_dashboard_template import get_project_dashboard_html
from project_tracker import scan_project_state, list_projects_with_status, PROJECT_MODULES, STATUS_LABELS, STATUS_COLORS
```

### 3. Add handler classes to `tf_handlers.py`
Copy the three handler classes from `tf_handlers_project_dashboard_patch.py`.

### 4. Add routes to `get_routes()`
```python
(r"/project-dashboard", ProjectDashboardPageHandler),
(r"/project-dashboard/([^/]+)", ProjectDashboardPageHandler),
(r"/api/project-dashboard/list", ProjectDashboardListHandler),
(r"/api/project-dashboard/state", ProjectDashboardStateHandler),
```

### 5. Update sidebar navigation
In `templates/shared_nav.py`, add a Project Dashboard link:
```html
<a href="/project-dashboard" class="nav-link">
  <span class="nav-icon">📋</span>
  <span class="nav-label">Project Dashboard</span>
</a>
```

### 6. Update main dashboard project clicks
When clicking a project on the main dashboard, navigate to `/project-dashboard/{job_code}` to use this as the primary entry point.

## Data Sources Scanned
| Module | File(s) Checked |
|--------|----------------|
| SA Estimate | `data/projects/{job}/sa_result.json`, `data/projects/{job}/bom.json` |
| TC Estimate | `data/projects/{job}/tc_quote.json`, `data/projects/TC-{job}/tc_quote.json` |
| BOM | `data/projects/{job}/bom.json`, `data/bom_results/{job}.json` |
| Shop Drawings | `data/shop_drawings/{job}/drawings/*.json` |
| Work Orders | `data/shop_drawings/{job}/work_orders/*.json` |
| Field Ops | `data/field_ops/{job}/field_ops.json` |
| Shipping | `data/shipping/{job}/*.json` |

## Testing

1. Navigate to `/project-dashboard`
2. Select a project from the dropdown → dashboard loads with colored cards
3. Verify complete modules show green with ✅ and version number
4. Verify missing modules show red with ❌ and "Needs Completion"
5. Click a red card → navigates to the appropriate module screen
6. Navigate to `/project-dashboard/SA-2024-001` → auto-loads that project
7. Verify progress bar and flow visualization update correctly
8. Verify next action banner shows the correct next step
