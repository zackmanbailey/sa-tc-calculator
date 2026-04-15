"""
PROJECT DASHBOARD — Project State Tracker
==========================================

Central module that tracks what's been completed for each project.
Scans data directories to determine status of:
  - SA Estimate
  - TC Estimate
  - Bill of Materials
  - Shop Drawings
  - Work Orders
  - Field Operations
  - Shipping

Storage: data/projects/{job_code}/project.json
"""

import os
import json
import glob
from datetime import datetime


# ─────────────────────────────────────────────
# MODULE DEFINITIONS
# ─────────────────────────────────────────────

PROJECT_MODULES = [
    {
        "key": "sa_estimate",
        "label": "SA Estimator",
        "icon": "&#127959;",
        "url_template": "/sa?project={job_code}",
        "depends_on": [],
        "description": "Structures America fabrication estimate",
    },
    {
        "key": "tc_estimate",
        "label": "TC Estimator",
        "icon": "&#128663;",
        "url_template": "/tc?project={job_code}",
        "depends_on": ["sa_estimate"],
        "description": "Titan Carports construction quote",
    },
    {
        "key": "bom",
        "label": "Bill of Materials",
        "icon": "&#128203;",
        "url_template": "/project/{job_code}#bom",
        "depends_on": ["sa_estimate"],
        "description": "Generated from SA estimate",
    },
    {
        "key": "shop_drawings",
        "label": "Shop Drawings",
        "icon": "&#128208;",
        "url_template": "/shop-drawings/{job_code}",
        "depends_on": ["bom"],
        "description": "Fabrication drawings per component",
    },
    {
        "key": "work_orders",
        "label": "Work Orders",
        "icon": "&#128203;",
        "url_template": "/work-orders/{job_code}",
        "depends_on": ["bom"],
        "description": "Shop floor fabrication tasks",
    },
    {
        "key": "field_ops",
        "label": "Field Operations",
        "icon": "&#127959;",
        "url_template": "/field-ops?project={job_code}",
        "depends_on": ["work_orders"],
        "description": "Installation tracking & crew dispatch",
    },
    {
        "key": "shipping",
        "label": "Shipping",
        "icon": "&#128666;",
        "url_template": "/shipping/{job_code}",
        "depends_on": ["work_orders"],
        "description": "Shipment management & tracking",
    },
]

# Status definitions
STATUS_NOT_STARTED = "not_started"
STATUS_IN_PROGRESS = "in_progress"
STATUS_COMPLETE = "complete"
STATUS_NEEDS_ATTENTION = "needs_attention"

STATUS_COLORS = {
    STATUS_NOT_STARTED: {"bg": "#EF4444", "text": "#FFFFFF", "border": "#DC2626"},
    STATUS_IN_PROGRESS: {"bg": "#3B82F6", "text": "#FFFFFF", "border": "#2563EB"},
    STATUS_COMPLETE: {"bg": "#22C55E", "text": "#FFFFFF", "border": "#16A34A"},
    STATUS_NEEDS_ATTENTION: {"bg": "#F59E0B", "text": "#FFFFFF", "border": "#D97706"},
}

STATUS_LABELS = {
    STATUS_NOT_STARTED: "Needs Completion",
    STATUS_IN_PROGRESS: "In Progress",
    STATUS_COMPLETE: "Complete",
    STATUS_NEEDS_ATTENTION: "Needs Attention",
}


# ─────────────────────────────────────────────
# PROJECT STATE SCANNER
# ─────────────────────────────────────────────

def scan_project_state(base_dir, job_code):
    """Scan all data directories to determine the current state of a project.

    Returns a dict with status for each module:
    {
        "job_code": "SA-2024-001",
        "modules": {
            "sa_estimate": {
                "status": "complete",
                "version": "v3",
                "last_modified": "2024-01-15T10:30:00Z",
                "details": {...}
            },
            ...
        },
        "overall_progress": 57,  // percentage
        "next_action": {...},
    }
    """
    state = {
        "job_code": job_code,
        "modules": {},
        "overall_progress": 0,
        "next_action": None,
        "scanned_at": datetime.utcnow().isoformat() + "Z",
    }

    # Check each module
    state["modules"]["sa_estimate"] = _check_sa_estimate(base_dir, job_code)
    state["modules"]["tc_estimate"] = _check_tc_estimate(base_dir, job_code)
    state["modules"]["bom"] = _check_bom(base_dir, job_code)
    state["modules"]["shop_drawings"] = _check_shop_drawings(base_dir, job_code)
    state["modules"]["work_orders"] = _check_work_orders(base_dir, job_code)
    state["modules"]["field_ops"] = _check_field_ops(base_dir, job_code)
    state["modules"]["shipping"] = _check_shipping(base_dir, job_code)

    # Calculate overall progress
    total_modules = len(state["modules"])
    complete_count = sum(1 for m in state["modules"].values() if m["status"] == STATUS_COMPLETE)
    in_progress_count = sum(1 for m in state["modules"].values() if m["status"] == STATUS_IN_PROGRESS)
    state["overall_progress"] = round(
        (complete_count * 100 + in_progress_count * 50) / total_modules
    )

    # Determine next action
    for mod_def in PROJECT_MODULES:
        mod_state = state["modules"].get(mod_def["key"], {})
        if mod_state["status"] == STATUS_NOT_STARTED:
            # Check dependencies
            deps_met = all(
                state["modules"].get(dep, {}).get("status") in [STATUS_COMPLETE, STATUS_IN_PROGRESS]
                for dep in mod_def.get("depends_on", [])
            )
            if deps_met:
                state["next_action"] = {
                    "module": mod_def["key"],
                    "label": mod_def["label"],
                    "url": mod_def["url_template"].format(job_code=job_code),
                    "message": f"Next step: Complete {mod_def['label']}",
                }
                break

    # Save the scanned state
    _save_project_state(base_dir, job_code, state)

    return state


def _check_sa_estimate(base_dir, job_code):
    """Check SA estimate status."""
    paths = [
        os.path.join(base_dir, "data", "projects", job_code, "sa_result.json"),
        os.path.join(base_dir, "data", "projects", job_code, "bom.json"),
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                mtime = os.path.getmtime(p)
                with open(p, "r") as f:
                    data = json.load(f)
                version = data.get("version", "v1")
                n_buildings = len(data.get("buildings", []))
                return {
                    "status": STATUS_COMPLETE,
                    "version": version,
                    "last_modified": datetime.fromtimestamp(mtime).isoformat() + "Z",
                    "details": {
                        "buildings": n_buildings,
                        "total_cost": data.get("total_material_cost", 0),
                        "total_weight": data.get("total_weight_lbs", 0),
                    },
                    "file": p,
                }
            except (json.JSONDecodeError, IOError):
                return {"status": STATUS_NEEDS_ATTENTION, "version": None,
                        "last_modified": None, "details": {"error": "File corrupted"}}

    return {"status": STATUS_NOT_STARTED, "version": None, "last_modified": None, "details": {}}


def _check_tc_estimate(base_dir, job_code):
    """Check TC estimate status."""
    tc_code = "TC-" + job_code
    paths = [
        os.path.join(base_dir, "data", "projects", job_code, "tc_quote.json"),
        os.path.join(base_dir, "data", "projects", tc_code, "tc_quote.json"),
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                mtime = os.path.getmtime(p)
                with open(p, "r") as f:
                    data = json.load(f)
                return {
                    "status": STATUS_COMPLETE,
                    "version": data.get("version", "v1"),
                    "last_modified": datetime.fromtimestamp(mtime).isoformat() + "Z",
                    "details": {
                        "total_sell": data.get("total_sell_price", 0),
                    },
                }
            except (json.JSONDecodeError, IOError):
                pass

    return {"status": STATUS_NOT_STARTED, "version": None, "last_modified": None, "details": {}}


def _check_bom(base_dir, job_code):
    """Check BOM status."""
    paths = [
        os.path.join(base_dir, "data", "projects", job_code, "bom.json"),
        os.path.join(base_dir, "data", "bom_results", job_code + ".json"),
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                mtime = os.path.getmtime(p)
                with open(p, "r") as f:
                    data = json.load(f)
                return {
                    "status": STATUS_COMPLETE,
                    "version": data.get("version", "v1"),
                    "last_modified": datetime.fromtimestamp(mtime).isoformat() + "Z",
                    "details": {
                        "buildings": len(data.get("buildings", [])),
                        "total_items": sum(len(b.get("line_items", [])) for b in data.get("buildings", [])),
                    },
                }
            except (json.JSONDecodeError, IOError):
                pass

    return {"status": STATUS_NOT_STARTED, "version": None, "last_modified": None, "details": {}}


def _check_shop_drawings(base_dir, job_code):
    """Check shop drawings status."""
    drawings_dir = os.path.join(base_dir, "data", "shop_drawings", job_code, "drawings")
    if not os.path.isdir(drawings_dir):
        return {"status": STATUS_NOT_STARTED, "version": None, "last_modified": None, "details": {}}

    drawing_files = [f for f in os.listdir(drawings_dir) if f.endswith(".json")]
    if not drawing_files:
        return {"status": STATUS_NOT_STARTED, "version": None, "last_modified": None, "details": {}}

    latest_mtime = max(os.path.getmtime(os.path.join(drawings_dir, f)) for f in drawing_files)

    return {
        "status": STATUS_COMPLETE,
        "version": None,
        "last_modified": datetime.fromtimestamp(latest_mtime).isoformat() + "Z",
        "details": {"drawing_count": len(drawing_files)},
    }


def _check_work_orders(base_dir, job_code):
    """Check work orders status."""
    wo_dir = os.path.join(base_dir, "data", "shop_drawings", job_code, "work_orders")
    if not os.path.isdir(wo_dir):
        return {"status": STATUS_NOT_STARTED, "version": None, "last_modified": None, "details": {}}

    wo_files = [f for f in os.listdir(wo_dir) if f.endswith(".json")]
    if not wo_files:
        return {"status": STATUS_NOT_STARTED, "version": None, "last_modified": None, "details": {}}

    total = len(wo_files)
    complete = 0
    in_progress = 0
    latest_mtime = 0

    for wf in wo_files:
        fp = os.path.join(wo_dir, wf)
        latest_mtime = max(latest_mtime, os.path.getmtime(fp))
        try:
            with open(fp, "r") as f:
                wo = json.load(f)
            status = wo.get("status", "")
            if status == "complete":
                complete += 1
            elif status not in ["queued", ""]:
                in_progress += 1
        except (json.JSONDecodeError, IOError):
            pass

    overall = STATUS_COMPLETE if complete == total else (STATUS_IN_PROGRESS if (complete + in_progress) > 0 else STATUS_NOT_STARTED)

    return {
        "status": overall,
        "version": None,
        "last_modified": datetime.fromtimestamp(latest_mtime).isoformat() + "Z" if latest_mtime else None,
        "details": {"total": total, "complete": complete, "in_progress": in_progress},
    }


def _check_field_ops(base_dir, job_code):
    """Check field operations status."""
    fo_path = os.path.join(base_dir, "data", "field_ops", job_code, "field_ops.json")
    if not os.path.exists(fo_path):
        return {"status": STATUS_NOT_STARTED, "version": None, "last_modified": None, "details": {}}

    try:
        mtime = os.path.getmtime(fo_path)
        with open(fo_path, "r") as f:
            data = json.load(f)
        installs = data.get("installations", [])
        complete = sum(1 for i in installs if i.get("status") == "complete")
        total = len(installs)

        status = STATUS_COMPLETE if complete == total and total > 0 else (
            STATUS_IN_PROGRESS if any(i.get("status") not in ["not_started", ""] for i in installs) else STATUS_NOT_STARTED
        )

        return {
            "status": status,
            "version": None,
            "last_modified": datetime.fromtimestamp(mtime).isoformat() + "Z",
            "details": {"total": total, "complete": complete},
        }
    except (json.JSONDecodeError, IOError):
        return {"status": STATUS_NOT_STARTED, "version": None, "last_modified": None, "details": {}}


def _check_shipping(base_dir, job_code):
    """Check shipping status."""
    ship_dir = os.path.join(base_dir, "data", "shipping", job_code)
    if not os.path.isdir(ship_dir):
        return {"status": STATUS_NOT_STARTED, "version": None, "last_modified": None, "details": {}}

    ship_files = [f for f in os.listdir(ship_dir) if f.endswith(".json")]
    if not ship_files:
        return {"status": STATUS_NOT_STARTED, "version": None, "last_modified": None, "details": {}}

    return {
        "status": STATUS_IN_PROGRESS,
        "version": None,
        "last_modified": None,
        "details": {"shipment_count": len(ship_files)},
    }


def _save_project_state(base_dir, job_code, state):
    """Save the scanned project state."""
    path = os.path.join(base_dir, "data", "projects", job_code, "project_state.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(state, f, indent=2, default=str)


# ─────────────────────────────────────────────
# LIST ALL PROJECTS WITH STATUS
# ─────────────────────────────────────────────

def list_projects_with_status(base_dir):
    """Get all projects with their current status summary."""
    projects_dir = os.path.join(base_dir, "data", "projects")
    if not os.path.isdir(projects_dir):
        return []

    projects = []
    for job_dir in sorted(os.listdir(projects_dir)):
        job_path = os.path.join(projects_dir, job_dir)
        if not os.path.isdir(job_path):
            continue

        # Load project metadata
        meta = {}
        meta_path = os.path.join(job_path, "project.json")
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r") as f:
                    meta = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        # Scan state
        state = scan_project_state(base_dir, job_dir)

        projects.append({
            "job_code": job_dir,
            "name": meta.get("name", meta.get("project_name", job_dir)),
            "customer": meta.get("customer_name", ""),
            "overall_progress": state["overall_progress"],
            "modules": state["modules"],
            "next_action": state.get("next_action"),
        })

    return projects
