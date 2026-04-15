"""
BUG-004 FIX — Field Ops Handler Classes for tf_handlers.py
============================================================

INSTRUCTIONS:
1. Add these imports near the top of tf_handlers.py:

   from shop_drawings.field_ops import (
       load_field_ops, save_field_ops, create_installation,
       update_installation_status, add_daily_log, add_delay,
       get_installation_summary, get_field_ops_for_project,
       auto_create_from_bom
   )
   from templates.field_ops import get_field_ops_html

2. Add FIELD_OPS_DIR constant near the top:

   FIELD_OPS_DIR = os.path.join(BASE_DIR, "data")

3. Copy these handler classes into tf_handlers.py

4. Add these routes to get_routes():

   (r"/field-ops", FieldOpsPageHandler),
   (r"/api/field-ops", FieldOpsDataHandler),
   (r"/api/field-ops/install", FieldOpsCreateInstallHandler),
   (r"/api/field-ops/status", FieldOpsStatusHandler),
   (r"/api/field-ops/daily-log", FieldOpsDailyLogHandler),
   (r"/api/field-ops/delay", FieldOpsDelayHandler),
   (r"/api/field-ops/auto-create", FieldOpsAutoCreateHandler),

5. Add "Field Ops" to the navigation in templates/shared_nav.py:
   Find the "Current Project" section and add:
   <a href="/field-ops">Field Ops</a>
"""

import json
import os


class FieldOpsPageHandler(BaseHandler):
    """GET /field-ops — Field Operations page."""
    def get(self):
        from templates.field_ops import get_field_ops_html
        self.render_with_nav(get_field_ops_html(), active_page="field-ops")


class FieldOpsDataHandler(BaseHandler):
    """GET /api/field-ops?job_code=XXX — Get field ops data and summary."""
    required_roles = ["admin", "estimator", "shop", "qc"]

    def get(self):
        try:
            job_code = self.get_query_argument("job_code", "").strip()
            if not job_code:
                self.write(json_encode({"ok": False, "error": "Missing job_code"}))
                return

            result = get_field_ops_for_project(FIELD_OPS_DIR, job_code)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode(result))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class FieldOpsCreateInstallHandler(BaseHandler):
    """POST /api/field-ops/install — Create a new installation record."""
    required_roles = ["admin", "estimator", "shop"]

    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            building_name = body.get("building_name", "").strip()

            if not job_code or not building_name:
                self.write(json_encode({"ok": False, "error": "Missing job_code or building_name"}))
                return

            result = create_installation(
                FIELD_OPS_DIR, job_code,
                building_name=building_name,
                building_id=body.get("building_id"),
                scheduled_start=body.get("scheduled_start"),
                scheduled_end=body.get("scheduled_end"),
                notes=body.get("notes", ""),
            )

            self.set_header("Content-Type", "application/json")
            self.write(json_encode(result))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class FieldOpsStatusHandler(BaseHandler):
    """POST /api/field-ops/status — Update installation status."""
    required_roles = ["admin", "estimator", "shop", "qc"]

    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            install_id = body.get("install_id", "").strip()
            new_status = body.get("new_status", "").strip()

            if not job_code or not install_id or not new_status:
                self.write(json_encode({"ok": False, "error": "Missing required fields"}))
                return

            changed_by = body.get("changed_by", self.get_current_user() or "system")
            notes = body.get("notes", "")

            result = update_installation_status(
                FIELD_OPS_DIR, job_code, install_id,
                new_status=new_status,
                changed_by=changed_by,
                notes=notes,
            )

            self.set_header("Content-Type", "application/json")
            self.write(json_encode(result))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class FieldOpsDailyLogHandler(BaseHandler):
    """POST /api/field-ops/daily-log — Add daily log entry."""
    required_roles = ["admin", "estimator", "shop"]

    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            install_id = body.get("install_id", "").strip()

            if not job_code or not install_id:
                self.write(json_encode({"ok": False, "error": "Missing job_code or install_id"}))
                return

            result = add_daily_log(
                FIELD_OPS_DIR, job_code, install_id,
                log_date=body.get("log_date", ""),
                crew_count=int(body.get("crew_count", 4)),
                hours_worked=float(body.get("hours_worked", 8)),
                weather=body.get("weather", ""),
                work_performed=body.get("work_performed", ""),
                issues=body.get("issues", ""),
                logged_by=self.get_current_user() or "system",
            )

            self.set_header("Content-Type", "application/json")
            self.write(json_encode(result))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class FieldOpsDelayHandler(BaseHandler):
    """POST /api/field-ops/delay — Report a delay."""
    required_roles = ["admin", "estimator", "shop"]

    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            install_id = body.get("install_id", "").strip()

            if not job_code or not install_id:
                self.write(json_encode({"ok": False, "error": "Missing job_code or install_id"}))
                return

            result = add_delay(
                FIELD_OPS_DIR, job_code, install_id,
                reason=body.get("reason", "Other"),
                description=body.get("description", ""),
                estimated_days=int(body.get("estimated_days", 1)),
                logged_by=self.get_current_user() or "system",
            )

            self.set_header("Content-Type", "application/json")
            self.write(json_encode(result))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class FieldOpsAutoCreateHandler(BaseHandler):
    """POST /api/field-ops/auto-create — Auto-create installations from saved BOM data."""
    required_roles = ["admin", "estimator"]

    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            if not job_code:
                self.write(json_encode({"ok": False, "error": "Missing job_code"}))
                return

            # Find BOM data
            bom_data = self._find_bom_data(job_code)
            if not bom_data:
                self.write(json_encode({
                    "ok": False,
                    "error": "No saved BOM found for " + job_code
                }))
                return

            result = auto_create_from_bom(FIELD_OPS_DIR, job_code, bom_data)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode(result))

        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))

    def _find_bom_data(self, job_code):
        """Search for saved BOM data for a given job code."""
        search_paths = [
            os.path.join(BASE_DIR, "data", "projects", job_code, "bom.json"),
            os.path.join(BASE_DIR, "data", "projects", job_code, "sa_result.json"),
            os.path.join(BASE_DIR, "data", "bom_results", job_code + ".json"),
        ]
        for path in search_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r") as f:
                        data = json.load(f)
                    if "buildings" in data:
                        return data
                except (json.JSONDecodeError, IOError):
                    continue
        return None
