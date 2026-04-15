"""
PROJECT DASHBOARD — Handler Classes for tf_handlers.py
=======================================================

INSTRUCTIONS:

1. Add imports at the top of tf_handlers.py:
     from templates.project_dashboard_template import get_project_dashboard_html
     from project_tracker import scan_project_state, list_projects_with_status, PROJECT_MODULES, STATUS_LABELS, STATUS_COLORS

2. Add these handler classes to tf_handlers.py

3. Add routes to get_routes():
     (r"/project-dashboard", ProjectDashboardPageHandler),
     (r"/project-dashboard/([^/]+)", ProjectDashboardPageHandler),
     (r"/api/project-dashboard/list", ProjectDashboardListHandler),
     (r"/api/project-dashboard/state", ProjectDashboardStateHandler),

4. Add project_tracker.py as: combined_calc/project_tracker.py

5. Add project_dashboard_template.py as: combined_calc/templates/project_dashboard_template.py

6. Update shared_nav.py to add a "Project Dashboard" link in the sidebar.
   In the nav links section, add before or after the existing project links:
     <a href="/project-dashboard" class="nav-link">
       <span class="nav-icon">&#128203;</span>
       <span class="nav-label">Project Dashboard</span>
     </a>

7. Update the main dashboard project click handler to navigate to /project-dashboard/{job_code}
   instead of (or in addition to) the current project detail view. This makes the dashboard
   the "source of truth" entry point for each project.
"""

import os
import json


class ProjectDashboardPageHandler(BaseHandler):
    """GET /project-dashboard — Project Dashboard page.
    GET /project-dashboard/{job_code} — Pre-loaded for a specific project.
    """

    def get(self, job_code=None):
        html = get_project_dashboard_html(job_code=job_code)
        self.render_with_nav(html, active_page="project_dashboard")


class ProjectDashboardListHandler(BaseHandler):
    """GET /api/project-dashboard/list — List all projects with summary status.

    Returns:
    {
        "ok": true,
        "projects": [
            {
                "job_code": "SA-2024-001",
                "name": "Project Name",
                "customer": "Customer Co",
                "overall_progress": 57,
                "next_action": {...}
            },
            ...
        ]
    }
    """

    def get(self):
        try:
            projects = list_projects_with_status(BASE_DIR)

            # Slim down for the list view (don't send full module details)
            slim = []
            for p in projects:
                slim.append({
                    "job_code": p["job_code"],
                    "name": p.get("name", p["job_code"]),
                    "customer": p.get("customer", ""),
                    "overall_progress": p.get("overall_progress", 0),
                    "next_action": p.get("next_action"),
                })

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({
                "ok": True,
                "projects": slim,
            }))
        except Exception as e:
            self.set_header("Content-Type", "application/json")
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class ProjectDashboardStateHandler(BaseHandler):
    """GET /api/project-dashboard/state?job_code=XXX — Full project state scan.

    Returns the complete module-by-module status with details, version info,
    dependencies, and next action recommendation.

    Returns:
    {
        "ok": true,
        "state": {
            "job_code": "SA-2024-001",
            "modules": {
                "sa_estimate": { "status": "complete", "version": "v3", ... },
                "tc_estimate": { "status": "not_started", ... },
                ...
            },
            "overall_progress": 57,
            "next_action": { "module": "tc_estimate", "label": "TC Estimator", ... },
            "scanned_at": "2024-01-15T10:30:00Z"
        },
        "meta": {
            "name": "Project Name",
            "customer_name": "Customer Co",
            ...
        },
        "module_defs": [...],
        "status_labels": {...},
        "status_colors": {...}
    }
    """

    def get(self):
        job_code = self.get_query_argument("job_code", "").strip()
        if not job_code:
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": False, "error": "job_code is required"}))
            return

        try:
            # Scan the project state
            state = scan_project_state(BASE_DIR, job_code)

            # Load project metadata
            meta = {}
            meta_path = os.path.join(BASE_DIR, "data", "projects", job_code, "project.json")
            if os.path.exists(meta_path):
                try:
                    with open(meta_path, "r") as f:
                        meta = json.load(f)
                except (json.JSONDecodeError, IOError):
                    pass

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({
                "ok": True,
                "state": state,
                "meta": meta,
                "module_defs": PROJECT_MODULES,
                "status_labels": STATUS_LABELS,
                "status_colors": STATUS_COLORS,
            }))
        except Exception as e:
            self.set_header("Content-Type", "application/json")
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))
