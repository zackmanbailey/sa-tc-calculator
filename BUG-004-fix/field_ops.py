"""
BUG-004 FIX — Field Operations Data Module
============================================

Backend logic for field operations:
- Installation tracking (job site progress per building)
- Crew dispatch & scheduling (placeholder data model)
- Field inspection & punch list (placeholder data model)

Storage: data/field_ops/{job_code}/field_ops.json
"""

import os
import json
import uuid
from datetime import datetime, date


# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────

INSTALL_STATUSES = [
    "not_started",
    "mobilizing",       # crew traveling to site
    "site_prep",        # layout, digging, forms
    "foundations",      # concrete poured, curing
    "erection",         # steel going up
    "roofing",          # panels/trim
    "punch_list",       # finishing items
    "complete",         # signed off
    "on_hold",          # weather/issue delay
]

INSTALL_STATUS_LABELS = {
    "not_started": "Not Started",
    "mobilizing": "Mobilizing",
    "site_prep": "Site Prep",
    "foundations": "Foundations",
    "erection": "Steel Erection",
    "roofing": "Roofing & Trim",
    "punch_list": "Punch List",
    "complete": "Complete",
    "on_hold": "On Hold",
}

INSTALL_STATUS_COLORS = {
    "not_started": "#94A3B8",
    "mobilizing": "#F59E0B",
    "site_prep": "#8B5CF6",
    "foundations": "#6366F1",
    "erection": "#3B82F6",
    "roofing": "#10B981",
    "punch_list": "#F97316",
    "complete": "#22C55E",
    "on_hold": "#EF4444",
}

CREW_ROLES = ["Foreman", "Welder", "Laborer", "Crane Operator", "Driver"]

DELAY_REASONS = [
    "Weather - Rain",
    "Weather - Wind",
    "Weather - Extreme Heat",
    "Material Delay",
    "Equipment Issue",
    "Crew Shortage",
    "Site Access Issue",
    "Customer Request",
    "Permit/Inspection Wait",
    "Safety Concern",
    "Other",
]


# ─────────────────────────────────────────────
# STORAGE
# ─────────────────────────────────────────────

def _field_ops_path(base_dir, job_code):
    return os.path.join(base_dir, "field_ops", job_code, "field_ops.json")


def load_field_ops(base_dir, job_code):
    """Load field ops data for a project. Returns default structure if none exists."""
    path = _field_ops_path(base_dir, job_code)
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    return {
        "job_code": job_code,
        "installations": [],
        "daily_logs": [],
        "crews": [],
        "inspections": [],
        "punch_items": [],
        "created_at": datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }


def save_field_ops(base_dir, job_code, data):
    """Save field ops data for a project."""
    path = _field_ops_path(base_dir, job_code)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data["updated_at"] = datetime.utcnow().isoformat() + "Z"
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    return True


# ─────────────────────────────────────────────
# INSTALLATION TRACKING (Core Feature)
# ─────────────────────────────────────────────

def create_installation(base_dir, job_code, building_name, building_id=None,
                        scheduled_start=None, scheduled_end=None, notes=""):
    """Create a new installation record for a building at a job site."""
    data = load_field_ops(base_dir, job_code)

    install = {
        "install_id": str(uuid.uuid4())[:8],
        "building_id": building_id or f"bldg_{len(data['installations']) + 1}",
        "building_name": building_name,
        "status": "not_started",
        "status_history": [{
            "status": "not_started",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "changed_by": "system",
            "notes": "Installation created",
        }],
        "scheduled_start": scheduled_start,
        "scheduled_end": scheduled_end,
        "actual_start": None,
        "actual_end": None,
        "crew_assigned": [],
        "progress_pct": 0,
        "daily_logs": [],
        "delays": [],
        "notes": notes,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }

    data["installations"].append(install)
    save_field_ops(base_dir, job_code, data)
    return {"ok": True, "install_id": install["install_id"], "installation": install}


def update_installation_status(base_dir, job_code, install_id, new_status,
                                changed_by="system", notes=""):
    """Update an installation's status."""
    if new_status not in INSTALL_STATUSES:
        return {"ok": False, "error": f"Invalid status: {new_status}"}

    data = load_field_ops(base_dir, job_code)
    install = None
    for inst in data["installations"]:
        if inst["install_id"] == install_id:
            install = inst
            break

    if not install:
        return {"ok": False, "error": f"Installation {install_id} not found"}

    old_status = install["status"]
    install["status"] = new_status
    install["status_history"].append({
        "status": new_status,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "changed_by": changed_by,
        "notes": notes,
        "previous_status": old_status,
    })

    # Auto-set timestamps
    if new_status == "mobilizing" and not install["actual_start"]:
        install["actual_start"] = datetime.utcnow().isoformat() + "Z"
    elif new_status == "complete":
        install["actual_end"] = datetime.utcnow().isoformat() + "Z"

    # Calculate progress percentage based on status
    status_progress = {
        "not_started": 0, "mobilizing": 5, "site_prep": 15,
        "foundations": 30, "erection": 55, "roofing": 80,
        "punch_list": 90, "complete": 100, "on_hold": install.get("progress_pct", 0),
    }
    install["progress_pct"] = status_progress.get(new_status, 0)

    save_field_ops(base_dir, job_code, data)
    return {"ok": True, "installation": install}


def add_daily_log(base_dir, job_code, install_id, log_date, crew_count,
                  hours_worked, weather, work_performed, issues="",
                  logged_by="system"):
    """Add a daily log entry for an installation."""
    data = load_field_ops(base_dir, job_code)
    install = None
    for inst in data["installations"]:
        if inst["install_id"] == install_id:
            install = inst
            break

    if not install:
        return {"ok": False, "error": f"Installation {install_id} not found"}

    log = {
        "log_id": str(uuid.uuid4())[:8],
        "date": log_date,
        "crew_count": crew_count,
        "hours_worked": hours_worked,
        "weather": weather,
        "work_performed": work_performed,
        "issues": issues,
        "logged_by": logged_by,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    install["daily_logs"].append(log)
    data["daily_logs"].append({**log, "install_id": install_id, "building_name": install["building_name"]})
    save_field_ops(base_dir, job_code, data)
    return {"ok": True, "log": log}


def add_delay(base_dir, job_code, install_id, reason, description="",
              estimated_days=0, logged_by="system"):
    """Record a delay for an installation."""
    data = load_field_ops(base_dir, job_code)
    install = None
    for inst in data["installations"]:
        if inst["install_id"] == install_id:
            install = inst
            break

    if not install:
        return {"ok": False, "error": f"Installation {install_id} not found"}

    delay = {
        "delay_id": str(uuid.uuid4())[:8],
        "reason": reason,
        "description": description,
        "estimated_days": estimated_days,
        "logged_by": logged_by,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "resolved": False,
    }

    install["delays"].append(delay)
    save_field_ops(base_dir, job_code, data)
    return {"ok": True, "delay": delay}


def get_installation_summary(base_dir, job_code):
    """Get summary of all installations for a project."""
    data = load_field_ops(base_dir, job_code)

    summary = {
        "total": len(data["installations"]),
        "by_status": {},
        "avg_progress": 0,
        "total_delays": 0,
        "installations": data["installations"],
    }

    if data["installations"]:
        total_progress = 0
        for inst in data["installations"]:
            s = inst["status"]
            summary["by_status"][s] = summary["by_status"].get(s, 0) + 1
            total_progress += inst.get("progress_pct", 0)
            summary["total_delays"] += len(inst.get("delays", []))
        summary["avg_progress"] = round(total_progress / len(data["installations"]), 1)

    return summary


# ─────────────────────────────────────────────
# AUTO-CREATE INSTALLATIONS FROM WORK ORDERS
# ─────────────────────────────────────────────

def auto_create_from_bom(base_dir, job_code, bom_data):
    """Auto-create installation records from BOM building data.

    Called when user first opens Field Ops for a project that has a saved BOM
    but no field ops data yet.
    """
    data = load_field_ops(base_dir, job_code)

    if data["installations"]:
        return {"ok": True, "message": "Installations already exist", "count": len(data["installations"])}

    buildings = bom_data.get("buildings", [])
    created = 0
    for b in buildings:
        create_installation(
            base_dir, job_code,
            building_name=b.get("building_name", f"Building {created + 1}"),
            building_id=b.get("building_id", ""),
            notes=f"{b.get('width_ft', 0)}'W x {b.get('length_ft', 0)}'L {b.get('type', 'tee')}",
        )
        created += 1

    return {"ok": True, "message": f"Created {created} installation(s) from BOM", "count": created}


# ─────────────────────────────────────────────
# EXPORTS (for reference by other modules)
# ─────────────────────────────────────────────

def get_field_ops_for_project(base_dir, job_code):
    """Get complete field ops data for project dashboard integration."""
    data = load_field_ops(base_dir, job_code)
    summary = get_installation_summary(base_dir, job_code)
    return {
        "ok": True,
        "data": data,
        "summary": summary,
        "statuses": INSTALL_STATUSES,
        "status_labels": INSTALL_STATUS_LABELS,
        "status_colors": INSTALL_STATUS_COLORS,
        "delay_reasons": DELAY_REASONS,
    }
