# TitanForge v4.2 — Bug Fix Deployment Package

**Date:** April 14, 2026  
**Fixes:** 8 bugs found during comprehensive end-to-end testing of v4.1

---

## Files to Deploy

Copy these files to your GitHub repo, replacing the existing versions:

| File | Location | Bugs Fixed |
|------|----------|-----------|
| `sa_calc.py` | `templates/sa_calc.py` | #1, #2, #7 |
| `tc_quote.py` | `templates/tc_quote.py` | #8 |
| `tf_handlers.py` | `tf_handlers.py` | #3, #4, #5, #6 |

**Note:** `shared_nav.py` is included but unchanged from v4.1. No changes needed to `templates/shared_nav.py`.

---

## Bugs Fixed

### Bug #1 — SA Estimator: `onStateChange` TypeError (HIGH)
- **Was:** Changing the State dropdown threw `TypeError: Cannot set properties of null (setting 'value')` because it tried to set `proj_footing` which no longer exists (footing is per-building now)
- **Fix:** Added null check for `proj_footing`; when missing, updates all building footing depths instead
- **File:** `templates/sa_calc.py` — `onStateChange()` function

### Bug #2 — SA Estimator: Tab Highlight Off By One (MEDIUM)
- **Was:** Active tab highlight didn't match visible content panel (e.g. viewing Price Overrides but BOM tab highlighted)
- **Fix:** Added `data-tab` attributes to tab elements; changed `showTab()` to use `querySelector('[data-tab="name"]')` instead of fragile index-based matching. Also scoped selector to `#tabs .tab` to avoid conflicts with injected nav elements
- **File:** `templates/sa_calc.py` — tab HTML + `showTab()` function

### Bug #3 — Dashboard: "Welcome back, there" (MEDIUM)
- **Was:** Welcome message showed "there" instead of user's name because `display_name` was empty string ("") and Python `.get()` returned it instead of falling back to username
- **Fix:** Changed display name logic to `(user_data.get("display_name") or user or "Admin").strip()` so empty strings fall through to the username
- **File:** `tf_handlers.py` — `DashboardHandler.get()` and `BaseHandler.render_with_nav()` (2 instances)

### Bug #4 — Project Page: Raw Unicode Escape Sequences (MEDIUM)
- **Was:** Tool tiles showed literal `\u2014 Not linked` and `\u2713 Linked` instead of `— Not linked` and `✓ Linked`
- **Fix:** Added post-processing in `ProjectPageHandler` to replace double-escaped `\\u2014` and `\\u2713` with actual Unicode characters before rendering
- **File:** `tf_handlers.py` — `ProjectPageHandler.get()`

### Bug #5 — Document Management: Missing Sidebar (MEDIUM)
- **Was:** `/documents` page used `self.write()` instead of `self.render_with_nav()`, so the shared sidebar navigation was never injected — the page was a navigation dead end
- **Fix:** Changed to `self.render_with_nav(html, active_page="documents")`
- **File:** `tf_handlers.py` — `DocumentManagementPageHandler.get()`

### Bug #6 — Global Search: Missing SA-Created Projects (LOW)
- **Was:** Search only checked `metadata.json` files; SA Estimator creates projects with only `current.json` (no metadata.json), so SA-created projects like "Riverside Marina Canopy" were invisible to search
- **Fix:** Added fallback to read `current.json` when `metadata.json` doesn't exist, extracting project_name, customer, and location from the SA data format
- **File:** `tf_handlers.py` — `GlobalSearchHandler.get()`

### Bug #7 — SA Estimator: Button Click Registration (LOW)
- **Was:** Add Building and Calculate BOM buttons occasionally didn't respond to clicks, likely due to z-index layering with the shared nav contextbar
- **Fix:** Added `position: relative; z-index: 2` to all `.btn` elements to ensure they stay above any overlapping nav elements
- **File:** `templates/sa_calc.py` — `.btn` CSS class

### Bug #8 — TC Estimator: Drilling Method Dropdown Blank (LOW)
- **Was:** Drilling Method dropdown appeared visually empty despite having options and calculations working correctly
- **Fix:** Added explicit `selected` attribute to the default "Per Hole ($/hole)" option
- **File:** `templates/tc_quote.py` — `drill_method` select element

---

## Deploy Steps

1. Copy `templates/sa_calc.py`, `templates/tc_quote.py` into your repo's `templates/` directory
2. Copy `tf_handlers.py` to the repo root
3. Commit and push to GitHub
4. Railway will auto-redeploy from the push

---

## Verification After Deploy

1. **Bug #1:** Go to `/sa` → Change State dropdown → No console errors
2. **Bug #2:** Go to `/sa` → Click through all 5 tabs → Active highlight matches content
3. **Bug #3:** Go to `/` → Should say "Welcome back, admin" (not "there")
4. **Bug #4:** Go to `/project/2026-0001` → Tool tiles show `— Not linked` and `✓ Linked` (real characters, not `\u` codes)
5. **Bug #5:** Go to `/documents` → Should have the standard TitanForge sidebar
6. **Bug #6:** Press Ctrl+K → Search "Riverside" → Should find "Riverside Marina Canopy"
7. **Bug #7:** Go to `/sa` → Click Add Building and Calculate BOM → Should respond consistently
8. **Bug #8:** Go to `/tc` → Drilling Method dropdown → Should show "Per Hole ($/hole)" by default
