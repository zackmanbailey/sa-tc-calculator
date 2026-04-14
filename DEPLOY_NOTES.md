# TitanForge v4.1 — Deployment Package

**Date:** April 14, 2026  
**Critical Priority:** The SA Estimator on the live site is completely non-functional due to a JavaScript syntax error.

---

## Files to Deploy

Copy these files to your GitHub repo, replacing the existing versions:

| File | Location | What Changed |
|------|----------|-------------|
| `sa_calc.py` | `templates/sa_calc.py` | Fixed fatal JS syntax error, Calculate BOM crash fix, BOM price override feature, shared nav layout CSS |
| `tc_quote.py` | `templates/tc_quote.py` | Shared nav layout CSS compatibility |
| `shared_nav.py` | `templates/shared_nav.py` | Fixed white sidebar on SA/TC pages (CSS variable fallback) |
| `tf_handlers.py` | `tf_handlers.py` | TC save/load API routes, project data helpers |
| `RULES.md` | `RULES.md` | Updated documentation |
| `test_project_data.py` | `test_project_data.py` | 25-test suite (all passing) |

---

## Bugs Fixed

### 1. SA Estimator Completely Broken (CRITICAL)
The live site has a JavaScript syntax error at line 1880 that kills ALL button functionality:
- **Root cause:** Missing closing quote in `showToast('Calculation error:  + data.error);` — should be `showToast('Calculation error: ' + data.error);`
- **Impact:** Every button is dead — Add Building, Remove Last, Calculate BOM, Save, History, tab switching — ALL broken
- **Fix:** Corrected in `sa_calc.py`

### 2. Calculate BOM Crash
- **Root cause:** `document.getElementById('proj_footing')` returns null (footing depth is per-building, not project-level)
- **Fix:** Added null-safe fallback: checks `proj_footing` element, falls back to `buildings[0].footing_depth_ft`, then default 10

### 3. White Sidebar on SA/TC Estimator Pages
- **Root cause:** `shared_nav.py` uses `background: var(--tf-navy)` but SA/TC pages define `--tf-dark` in their `:root`, not `--tf-navy`
- **Fix:** Changed to `background: var(--tf-navy, #0F172A)` with hardcoded fallback (2 instances: lines 28 and 279)

---

## New Feature: BOM Price Overrides
- Added "Override $" column to the BOM table
- Users can enter custom prices per line item
- Override rows highlighted with gold background (#FFF8E0) and diamond marker
- Original costs shown with strikethrough
- Overrides persist through save/load cycle

---

## Deploy Steps

1. Copy the files from the `templates/` subfolder into your repo's `templates/` directory
2. Copy `tf_handlers.py`, `RULES.md`, and `test_project_data.py` to the repo root
3. Commit and push to GitHub
4. Railway will auto-redeploy from the push

---

## Verification After Deploy

1. Go to https://calc.titancarports.com/sa
2. Open browser console (F12) — should see NO errors
3. Click "Add Building" — should add a building form
4. Click "Calculate BOM" — should calculate without crashing
5. Check sidebar — should be dark navy (#0F172A), not white/transparent
6. Go to https://calc.titancarports.com/tc — verify sidebar is also dark navy
