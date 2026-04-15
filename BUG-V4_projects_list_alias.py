"""
BUG-V4 FIX: /api/projects/list Returns 404 (API Inconsistency)
================================================================
File: combined_calc/tf_handlers.py
Severity: MEDIUM (API inconsistency)
Discovered: Post-patch verification, April 15, 2026

PROBLEM:
  The API endpoint /api/projects/list returns 404.
  The correct endpoint is /api/projects (no /list suffix).
  This is inconsistent with other API patterns in the app which use
  /api/<resource>/list (e.g., /api/work-orders/list, /api/customers).

  Some frontend code or external integrations may expect /list to work.

ROOT CAUSE:
  The route table in get_routes() only registers:
    (r"/api/projects",  ProjectListHandler),

  There is no alias for /api/projects/list.

FIX:
  Add a route alias in get_routes() in tf_handlers.py.

  Find the projects API routes section (around line 5772):
    (r"/api/projects",               ProjectListHandler),

  Add immediately after:
    (r"/api/projects/list",          ProjectListHandler),

  This maps both /api/projects and /api/projects/list to the same handler,
  making the API consistent with other resource patterns.

FULL CONTEXT of the change:
    # ── API - Projects (versioned system) ───────────────────
    (r"/api/project/save",           ProjectSaveHandler),
    (r"/api/project/load",           ProjectLoadHandler),
    (r"/api/project/revisions",      ProjectRevisionsHandler),
    (r"/api/project/compare",        ProjectCompareHandler),
    (r"/api/projects",               ProjectListHandler),
    (r"/api/projects/list",          ProjectListHandler),    # <-- ADD THIS

VERIFICATION:
  After applying:
  1. Visit /api/projects — should return JSON list of projects
  2. Visit /api/projects/list — should return the same JSON list
  3. Both endpoints should behave identically
"""
