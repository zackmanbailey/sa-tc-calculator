# TitanForge v4.3 — Bug Fix Deployment Notes

**Date:** April 14, 2026
**Version:** 4.3
**Previous:** 4.2

## Files Changed

| File | Changes |
|------|---------|
| `tf_handlers.py` | BUG-01, BUG-02, BUG-03, BUG-04, BUG-06, BUG-12 |
| `templates/tc_quote.py` | BUG-05, BUG-13 |
| `templates/sa_calc.py` | BUG-07 |
| `templates/shared_nav.py` | BUG-11 |

## Deployment Instructions

1. Upload these 4 files to your GitHub repo, replacing the existing files:
   - `tf_handlers.py` (root)
   - `templates/tc_quote.py`
   - `templates/sa_calc.py`
   - `templates/shared_nav.py`

2. Railway will auto-redeploy from the GitHub push.

3. No database migrations needed. No new dependencies.

---

## Bug Fixes Included

### BUG-01 — svg2pdf.js Missing on Shop Drawings (CRITICAL)
**Error:** "Can't find variable: svg2pdf" when clicking Save PDF on column/rafter drawings.
**Fix:** Injected jsPDF + svg2pdf.js CDN script tags into both `ColumnDrawingHandler` and `RafterDrawingHandler` via `</head>` replacement. No template file changes needed.

### BUG-02 — SA-Created Projects Return 404 (HIGH)
**Error:** ProjectPageHandler crashed when opening SA Estimator-created projects because they only have `current.json` (no `metadata.json`).
**Fix:** Added fallback in `ProjectPageHandler.get()` that reads `current.json` and constructs metadata from SA project data when `metadata.json` is missing.

### BUG-03 — Dashboard Project Cards Not Clickable (HIGH)
**Error:** Clicking a project card on the dashboard did nothing.
**Fix:** Injected DOMContentLoaded script that adds click handlers to all `[data-job-code]` elements, with a MutationObserver for dynamically loaded cards. Navigates to `/project/{job_code}`.

### BUG-04 — "Welcome back, there" Instead of User Name (MEDIUM)
**Error:** Dashboard always showed "Welcome back, there" because the template JS rejects "Admin" as a display name.
**Fix:** Injected DOMContentLoaded script that overrides `heroName` text with the server-side `display` value, bypassing the template's client-side filtering.

### BUG-05 — TC Equipment Rental Shows $0.00 (MEDIUM)
**Error:** Equipment rental row totals stayed $0.00 even after entering values.
**Fix:** Added `oninput` event handlers alongside existing `onchange` handlers on qty and rate inputs in `renderEquipTable()`. The `oninput` fires immediately as the user types, while `onchange` only fires on blur — both are now wired up.

### BUG-06 — Login Form Sends GET Instead of POST (MEDIUM)
**Error:** Login form submitted via GET, but `LoginHandler.post()` expects a JSON POST body.
**Fix:** Injected script in `LoginHandler.get()` that intercepts form submit, prevents default, and sends credentials via `fetch()` as JSON POST. Handles success redirect and error display.

### BUG-07 — CALCULATE BOM Button Intermittent Click (MEDIUM)
**Error:** The CALCULATE BOM button in SA Estimator sometimes didn't respond to clicks, especially after scrolling.
**Fix:** Made the button container `position:sticky;bottom:0` with elevated `z-index:10` so it's always visible and clickable at the bottom of the sidebar, regardless of scroll position.

### BUG-11 — All Projects Sidebar Link Not Highlighted (LOW)
**Error:** The "All Projects" link in the sidebar was never highlighted as active when on the dashboard.
**Fix:** Changed the nav item key from `"projects"` to `"dashboard"` in `shared_nav.py` so it matches the `active_page="dashboard"` passed by `DashboardHandler`.

### BUG-12 — Missing Sidebar on Schedule, Job Costing, Reports, Activity Pages (MEDIUM)
**Error:** Several pages used `self.write()` directly instead of `render_with_nav()`, so they had no sidebar navigation.
**Fix:** Changed these handlers to use `self.render_with_nav()`:
- `ProductionSchedulePageHandler` → active_page="schedule"
- `JobCostingPageHandler` → active_page="jobcosting"
- `ProductionMetricsPageHandler` → active_page="reports"
- `ExecutiveSummaryPageHandler` → active_page="reports"
- `ActivityFeedPageHandler` → active_page="activity"

### BUG-13 — TC Summary Tab Missing Save/Export Buttons (MEDIUM)
**Error:** The TC Quote Summary tab had no way to save or export the quote.
**Fix:** Added "Save Quote" and "Export PDF" buttons at the top of the summary tab, wired to the existing `tcSaveProject()` and `tcExportPDF()` functions.

---

## Notes

- BUG-08 (showTab highlight) was already fixed in v4.2 — the `data-tab` attribute querySelector fallback works correctly.
- BUG-09 (Generate Labels) works correctly — labels require a BOM calculation first. The "Run BOM first" toast message is displayed when attempted without BOM data.
- BUG-10 (Shop Drawings sidebar link) — The global sidebar "Shop Drawings" link correctly points to `/documents` (Document Management). Per-project shop drawing links are handled by the "Current Project" section via `setProjectContext()`.
