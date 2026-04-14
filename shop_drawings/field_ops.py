"""
TitanForge v4 — Field Operations & Installation Tracking
==========================================================
Data model, storage, and business logic for:
  - Punch list items (issues found at job site)
  - Daily field reports
  - Installation confirmation per WO item
  - Project completion tracking / metrics

Reference: RULES.md §5 (Item Lifecycle: delivered → installed)
"""

import os
import json
import datetime
import secrets
from dataclasses import dataclass, field
from typing import List, Optional, Dict

from shop_drawings.work_orders import (
    WorkOrder, WorkOrderItem,
    STATUS_DELIVERED, STATUS_INSTALLED,
    load_work_order, save_work_order,
    transition_item_status,
    PHASE_SHIPPING, VALID_STATUSES,
)


# ─────────────────────────────────────────────
# PUNCH LIST CONSTANTS
# ─────────────────────────────────────────────

PUNCH_STATUS_OPEN = "open"
PUNCH_STATUS_IN_PROGRESS = "in_progress"
PUNCH_STATUS_RESOLVED = "resolved"
PUNCH_STATUS_VERIFIED = "verified"      # PM/foreman confirmed fix
PUNCH_STATUS_DEFERRED = "deferred"      # Pushed to later

PUNCH_STATUSES = [
    PUNCH_STATUS_OPEN, PUNCH_STATUS_IN_PROGRESS,
    PUNCH_STATUS_RESOLVED, PUNCH_STATUS_VERIFIED,
    PUNCH_STATUS_DEFERRED,
]

PUNCH_STATUS_LABELS = {
    PUNCH_STATUS_OPEN: "Open",
    PUNCH_STATUS_IN_PROGRESS: "In Progress",
    PUNCH_STATUS_RESOLVED: "Resolved",
    PUNCH_STATUS_VERIFIED: "Verified",
    PUNCH_STATUS_DEFERRED: "Deferred",
}

PUNCH_STATUS_COLORS = {
    PUNCH_STATUS_OPEN: "red",
    PUNCH_STATUS_IN_PROGRESS: "amber",
    PUNCH_STATUS_RESOLVED: "blue",
    PUNCH_STATUS_VERIFIED: "green",
    PUNCH_STATUS_DEFERRED: "gray",
}

PUNCH_FLOW = {
    PUNCH_STATUS_OPEN:        [PUNCH_STATUS_IN_PROGRESS, PUNCH_STATUS_DEFERRED],
    PUNCH_STATUS_IN_PROGRESS: [PUNCH_STATUS_RESOLVED, PUNCH_STATUS_DEFERRED],
    PUNCH_STATUS_RESOLVED:    [PUNCH_STATUS_VERIFIED, PUNCH_STATUS_IN_PROGRESS],  # reopen if bad fix
    PUNCH_STATUS_VERIFIED:    [],  # terminal
    PUNCH_STATUS_DEFERRED:    [PUNCH_STATUS_OPEN],  # reopen
}

PUNCH_PRIORITY_CRITICAL = "critical"    # Safety / structural
PUNCH_PRIORITY_HIGH = "high"            # Must fix before close-out
PUNCH_PRIORITY_MEDIUM = "medium"        # Standard issue
PUNCH_PRIORITY_LOW = "low"              # Cosmetic / minor

PUNCH_PRIORITIES = [
    PUNCH_PRIORITY_CRITICAL, PUNCH_PRIORITY_HIGH,
    PUNCH_PRIORITY_MEDIUM, PUNCH_PRIORITY_LOW,
]

PUNCH_CATEGORY_MISSING = "missing_item"
PUNCH_CATEGORY_DAMAGED = "damaged"
PUNCH_CATEGORY_WRONG = "wrong_item"
PUNCH_CATEGORY_FIT = "fit_issue"
PUNCH_CATEGORY_ALIGNMENT = "alignment"
PUNCH_CATEGORY_FINISH = "finish_defect"
PUNCH_CATEGORY_HARDWARE = "missing_hardware"
PUNCH_CATEGORY_OTHER = "other"

PUNCH_CATEGORIES = [
    PUNCH_CATEGORY_MISSING, PUNCH_CATEGORY_DAMAGED, PUNCH_CATEGORY_WRONG,
    PUNCH_CATEGORY_FIT, PUNCH_CATEGORY_ALIGNMENT, PUNCH_CATEGORY_FINISH,
    PUNCH_CATEGORY_HARDWARE, PUNCH_CATEGORY_OTHER,
]

PUNCH_CATEGORY_LABELS = {
    PUNCH_CATEGORY_MISSING: "Missing Item",
    PUNCH_CATEGORY_DAMAGED: "Damaged",
    PUNCH_CATEGORY_WRONG: "Wrong Item Shipped",
    PUNCH_CATEGORY_FIT: "Fit / Tolerance Issue",
    PUNCH_CATEGORY_ALIGNMENT: "Alignment Problem",
    PUNCH_CATEGORY_FINISH: "Finish / Coating Defect",
    PUNCH_CATEGORY_HARDWARE: "Missing Hardware",
    PUNCH_CATEGORY_OTHER: "Other",
}


# ─────────────────────────────────────────────
# DATA MODELS
# ─────────────────────────────────────────────

@dataclass
class PunchListItem:
    """A single issue found during field installation."""
    punch_id: str = ""
    job_code: str = ""
    item_id: str = ""               # Related WO item (optional)
    ship_mark: str = ""             # Related ship mark for context
    load_id: str = ""               # Load it arrived on

    status: str = PUNCH_STATUS_OPEN
    priority: str = PUNCH_PRIORITY_MEDIUM
    category: str = PUNCH_CATEGORY_OTHER

    title: str = ""                 # Short description
    description: str = ""           # Full description
    location: str = ""              # Where on the job site (grid ref, bay, etc.)

    photos: list = field(default_factory=list)  # Photo file references

    created_by: str = ""
    created_at: str = ""
    assigned_to: str = ""           # Who's responsible for fix
    resolved_by: str = ""
    resolved_at: str = ""
    resolution_notes: str = ""
    verified_by: str = ""
    verified_at: str = ""

    def to_dict(self) -> dict:
        return {
            "punch_id": self.punch_id, "job_code": self.job_code,
            "item_id": self.item_id, "ship_mark": self.ship_mark,
            "load_id": self.load_id, "status": self.status,
            "priority": self.priority, "category": self.category,
            "title": self.title, "description": self.description,
            "location": self.location, "photos": self.photos,
            "created_by": self.created_by, "created_at": self.created_at,
            "assigned_to": self.assigned_to, "resolved_by": self.resolved_by,
            "resolved_at": self.resolved_at, "resolution_notes": self.resolution_notes,
            "verified_by": self.verified_by, "verified_at": self.verified_at,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "PunchListItem":
        item = cls()
        for k, v in d.items():
            if hasattr(item, k):
                setattr(item, k, v)
        return item

    @property
    def status_label(self) -> str:
        return PUNCH_STATUS_LABELS.get(self.status, self.status)

    @property
    def status_color(self) -> str:
        return PUNCH_STATUS_COLORS.get(self.status, "gray")

    @property
    def priority_label(self) -> str:
        return self.priority.replace("_", " ").title()

    @property
    def category_label(self) -> str:
        return PUNCH_CATEGORY_LABELS.get(self.category, self.category)

    def can_transition_to(self, new_status: str) -> bool:
        return new_status in PUNCH_FLOW.get(self.status, [])


@dataclass
class DailyFieldReport:
    """A daily report from the field crew on a project."""
    report_id: str = ""
    job_code: str = ""
    date: str = ""                  # YYYY-MM-DD
    submitted_by: str = ""
    submitted_at: str = ""

    # Crew
    crew_count: int = 0
    crew_names: list = field(default_factory=list)
    hours_worked: float = 0.0

    # Work performed
    work_summary: str = ""          # What was done today
    items_installed: list = field(default_factory=list)  # item_ids installed today
    equipment_used: list = field(default_factory=list)

    # Conditions
    weather: str = ""               # sunny, rain, wind, snow, etc.
    temperature_f: float = 0.0
    delays: str = ""                # Any delays and reasons
    safety_incidents: str = ""      # Any safety issues

    # Photos
    photos: list = field(default_factory=list)

    # Notes
    notes: str = ""
    issues: str = ""                # Problems encountered

    def to_dict(self) -> dict:
        return {
            "report_id": self.report_id, "job_code": self.job_code,
            "date": self.date, "submitted_by": self.submitted_by,
            "submitted_at": self.submitted_at, "crew_count": self.crew_count,
            "crew_names": self.crew_names, "hours_worked": self.hours_worked,
            "work_summary": self.work_summary, "items_installed": self.items_installed,
            "equipment_used": self.equipment_used, "weather": self.weather,
            "temperature_f": self.temperature_f, "delays": self.delays,
            "safety_incidents": self.safety_incidents, "photos": self.photos,
            "notes": self.notes, "issues": self.issues,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "DailyFieldReport":
        rpt = cls()
        for k, v in d.items():
            if hasattr(rpt, k):
                setattr(rpt, k, v)
        return rpt


@dataclass
class InstallationRecord:
    """Confirmation that a specific WO item has been installed."""
    record_id: str = ""
    job_code: str = ""
    item_id: str = ""
    ship_mark: str = ""

    installed_by: str = ""          # Crew member who confirmed
    installed_at: str = ""          # ISO timestamp
    verified_by: str = ""           # PM/foreman who verified
    verified_at: str = ""

    location: str = ""              # Where installed (grid/bay ref)
    photos: list = field(default_factory=list)
    notes: str = ""

    # Punch items generated during install
    punch_ids: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "record_id": self.record_id, "job_code": self.job_code,
            "item_id": self.item_id, "ship_mark": self.ship_mark,
            "installed_by": self.installed_by, "installed_at": self.installed_at,
            "verified_by": self.verified_by, "verified_at": self.verified_at,
            "location": self.location, "photos": self.photos,
            "notes": self.notes, "punch_ids": self.punch_ids,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "InstallationRecord":
        rec = cls()
        for k, v in d.items():
            if hasattr(rec, k):
                setattr(rec, k, v)
        return rec


# ─────────────────────────────────────────────
# STORAGE
# ─────────────────────────────────────────────

def _field_dir(base_dir: str, job_code: str) -> str:
    d = os.path.join(base_dir, "data", "field_ops", job_code)
    os.makedirs(d, exist_ok=True)
    return d


def _load_field_data(base_dir: str, job_code: str) -> dict:
    """Load all field ops data for a project."""
    d = _field_dir(base_dir, job_code)
    path = os.path.join(d, "field_data.json")
    if os.path.isfile(path):
        with open(path) as f:
            return json.load(f)
    return {"punch_items": [], "daily_reports": [], "installations": []}


def _save_field_data(base_dir: str, job_code: str, data: dict):
    d = _field_dir(base_dir, job_code)
    path = os.path.join(d, "field_data.json")
    data["updated_at"] = datetime.datetime.now().isoformat()
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# ─── Punch List Storage ───

def save_punch_item(base_dir: str, job_code: str, punch: PunchListItem):
    """Save or update a punch list item."""
    data = _load_field_data(base_dir, job_code)
    items = data.get("punch_items", [])

    # Update existing or append new
    found = False
    for i, existing in enumerate(items):
        if existing.get("punch_id") == punch.punch_id:
            items[i] = punch.to_dict()
            found = True
            break
    if not found:
        items.append(punch.to_dict())

    data["punch_items"] = items
    _save_field_data(base_dir, job_code, data)


def load_punch_items(base_dir: str, job_code: str, status: str = "") -> List[PunchListItem]:
    """Load all punch list items for a project, optionally filtered."""
    data = _load_field_data(base_dir, job_code)
    items = [PunchListItem.from_dict(d) for d in data.get("punch_items", [])]
    if status:
        items = [i for i in items if i.status == status]
    return items


def load_punch_item(base_dir: str, job_code: str, punch_id: str) -> Optional[PunchListItem]:
    """Load a specific punch list item."""
    items = load_punch_items(base_dir, job_code)
    for item in items:
        if item.punch_id == punch_id:
            return item
    return None


def load_all_punch_items(base_dir: str) -> List[PunchListItem]:
    """Load punch items from ALL projects."""
    results = []
    field_root = os.path.join(base_dir, "data", "field_ops")
    if not os.path.isdir(field_root):
        return results
    for job_code in os.listdir(field_root):
        results.extend(load_punch_items(base_dir, job_code))
    results.sort(key=lambda x: x.created_at or "", reverse=True)
    return results


# ─── Daily Report Storage ───

def save_daily_report(base_dir: str, job_code: str, report: DailyFieldReport):
    data = _load_field_data(base_dir, job_code)
    reports = data.get("daily_reports", [])
    found = False
    for i, existing in enumerate(reports):
        if existing.get("report_id") == report.report_id:
            reports[i] = report.to_dict()
            found = True
            break
    if not found:
        reports.append(report.to_dict())
    data["daily_reports"] = reports
    _save_field_data(base_dir, job_code, data)


def load_daily_reports(base_dir: str, job_code: str) -> List[DailyFieldReport]:
    data = _load_field_data(base_dir, job_code)
    reports = [DailyFieldReport.from_dict(d) for d in data.get("daily_reports", [])]
    reports.sort(key=lambda x: x.date or "", reverse=True)
    return reports


# ─── Installation Record Storage ───

def save_installation_record(base_dir: str, job_code: str, record: InstallationRecord):
    data = _load_field_data(base_dir, job_code)
    records = data.get("installations", [])
    found = False
    for i, existing in enumerate(records):
        if existing.get("record_id") == record.record_id:
            records[i] = record.to_dict()
            found = True
            break
    if not found:
        records.append(record.to_dict())
    data["installations"] = records
    _save_field_data(base_dir, job_code, data)


def load_installation_records(base_dir: str, job_code: str) -> List[InstallationRecord]:
    data = _load_field_data(base_dir, job_code)
    records = [InstallationRecord.from_dict(d) for d in data.get("installations", [])]
    records.sort(key=lambda x: x.installed_at or "", reverse=True)
    return records


# ─────────────────────────────────────────────
# BUSINESS LOGIC
# ─────────────────────────────────────────────

def create_punch_item(base_dir: str, job_code: str, created_by: str,
                      title: str, description: str = "", priority: str = PUNCH_PRIORITY_MEDIUM,
                      category: str = PUNCH_CATEGORY_OTHER, item_id: str = "",
                      ship_mark: str = "", load_id: str = "", location: str = "",
                      assigned_to: str = "", photos: list = None) -> PunchListItem:
    """Create a new punch list item."""
    now = datetime.datetime.now()
    punch = PunchListItem(
        punch_id=f"PUNCH-{now.strftime('%Y%m%d')}-{secrets.token_hex(3).upper()}",
        job_code=job_code,
        item_id=item_id,
        ship_mark=ship_mark,
        load_id=load_id,
        status=PUNCH_STATUS_OPEN,
        priority=priority,
        category=category,
        title=title,
        description=description,
        location=location,
        photos=photos or [],
        created_by=created_by,
        created_at=now.isoformat(),
        assigned_to=assigned_to,
    )
    save_punch_item(base_dir, job_code, punch)
    return punch


def transition_punch_status(base_dir: str, job_code: str, punch_id: str,
                            new_status: str, changed_by: str,
                            notes: str = "") -> dict:
    """Transition a punch item through its lifecycle."""
    punch = load_punch_item(base_dir, job_code, punch_id)
    if not punch:
        return {"ok": False, "error": "Punch item not found"}

    if not punch.can_transition_to(new_status):
        allowed = PUNCH_FLOW.get(punch.status, [])
        return {"ok": False, "error": f"Cannot transition from '{punch.status}' to '{new_status}'. Allowed: {allowed}"}

    old_status = punch.status
    punch.status = new_status

    now = datetime.datetime.now().isoformat()
    if new_status == PUNCH_STATUS_RESOLVED:
        punch.resolved_by = changed_by
        punch.resolved_at = now
        if notes:
            punch.resolution_notes = notes
    elif new_status == PUNCH_STATUS_VERIFIED:
        punch.verified_by = changed_by
        punch.verified_at = now

    save_punch_item(base_dir, job_code, punch)
    return {
        "ok": True,
        "old_status": old_status,
        "new_status": new_status,
        "punch": punch.to_dict(),
    }


def confirm_installation(base_dir: str, wo_base_dir: str, job_code: str,
                         item_id: str, installed_by: str,
                         location: str = "", notes: str = "",
                         photos: list = None) -> dict:
    """Confirm that a delivered WO item has been installed.
    Creates an InstallationRecord and transitions the WO item to 'installed'.
    """
    # Find the WO item
    wo, wo_item = _find_wo_item(wo_base_dir, job_code, item_id)
    if not wo or not wo_item:
        return {"ok": False, "error": f"Item {item_id} not found in project {job_code}"}

    # Must be in delivered status
    if wo_item.status != STATUS_DELIVERED:
        return {"ok": False, "error": f"Item status is '{wo_item.status}', must be 'delivered' to confirm installation"}

    now = datetime.datetime.now()

    # Transition WO item to installed
    result = transition_item_status(
        wo_base_dir, job_code, item_id, STATUS_INSTALLED, installed_by,
        notes=f"Installation confirmed: {notes}" if notes else "Installation confirmed"
    )
    if not result.get("ok"):
        return {"ok": False, "error": f"Transition failed: {result.get('error', 'unknown')}"}

    # Create installation record
    record = InstallationRecord(
        record_id=f"INST-{now.strftime('%Y%m%d')}-{secrets.token_hex(3).upper()}",
        job_code=job_code,
        item_id=item_id,
        ship_mark=wo_item.ship_mark,
        installed_by=installed_by,
        installed_at=now.isoformat(),
        location=location,
        photos=photos or [],
        notes=notes,
    )
    save_installation_record(base_dir, job_code, record)

    return {"ok": True, "record": record.to_dict(), "item_status": STATUS_INSTALLED}


def submit_daily_report(base_dir: str, wo_base_dir: str, job_code: str,
                        submitted_by: str, date: str = "",
                        crew_count: int = 0, crew_names: list = None,
                        hours_worked: float = 0.0, work_summary: str = "",
                        items_installed: list = None, equipment_used: list = None,
                        weather: str = "", temperature_f: float = 0.0,
                        delays: str = "", safety_incidents: str = "",
                        photos: list = None, notes: str = "",
                        issues: str = "") -> dict:
    """Submit a daily field report and optionally confirm installations."""
    now = datetime.datetime.now()

    report = DailyFieldReport(
        report_id=f"DFR-{now.strftime('%Y%m%d')}-{secrets.token_hex(3).upper()}",
        job_code=job_code,
        date=date or now.strftime("%Y-%m-%d"),
        submitted_by=submitted_by,
        submitted_at=now.isoformat(),
        crew_count=crew_count,
        crew_names=crew_names or [],
        hours_worked=hours_worked,
        work_summary=work_summary,
        items_installed=items_installed or [],
        equipment_used=equipment_used or [],
        weather=weather,
        temperature_f=temperature_f,
        delays=delays,
        safety_incidents=safety_incidents,
        photos=photos or [],
        notes=notes,
        issues=issues,
    )
    save_daily_report(base_dir, job_code, report)

    # Auto-confirm installations for any items listed
    install_results = []
    for item_id in (items_installed or []):
        result = confirm_installation(
            base_dir, wo_base_dir, job_code, item_id, submitted_by,
            notes=f"Confirmed via daily report {report.report_id}"
        )
        install_results.append({"item_id": item_id, "result": result})

    return {
        "ok": True,
        "report": report.to_dict(),
        "install_results": install_results,
    }


def get_project_completion(wo_base_dir: str, base_dir: str, job_code: str) -> dict:
    """Calculate project completion metrics for a specific project."""
    work_orders = _load_all_work_orders(wo_base_dir, job_code)
    punch_items = load_punch_items(base_dir, job_code)
    daily_reports = load_daily_reports(base_dir, job_code)
    install_records = load_installation_records(base_dir, job_code)

    total_items = 0
    status_counts = {}
    phase_counts = {"prefab": 0, "fabrication": 0, "qc": 0, "shipping": 0, "installed": 0}

    for wo in work_orders:
        for item in wo.items:
            total_items += 1
            status_counts[item.status] = status_counts.get(item.status, 0) + 1
            if item.status in ["queued", "approved", "stickers_printed", "staged"]:
                phase_counts["prefab"] += 1
            elif item.status in ["in_progress", "fabricated"]:
                phase_counts["fabrication"] += 1
            elif item.status in ["qc_pending", "qc_approved", "qc_rejected"]:
                phase_counts["qc"] += 1
            elif item.status in ["ready_to_ship", "shipped", "delivered"]:
                phase_counts["shipping"] += 1
            elif item.status == "installed":
                phase_counts["installed"] += 1

    installed_count = status_counts.get("installed", 0)
    delivered_count = status_counts.get("delivered", 0)
    shipped_count = status_counts.get("shipped", 0)

    # Punch list metrics
    open_punches = len([p for p in punch_items if p.status in [PUNCH_STATUS_OPEN, PUNCH_STATUS_IN_PROGRESS]])
    resolved_punches = len([p for p in punch_items if p.status in [PUNCH_STATUS_RESOLVED, PUNCH_STATUS_VERIFIED]])
    critical_punches = len([p for p in punch_items if p.priority == PUNCH_PRIORITY_CRITICAL and p.status not in [PUNCH_STATUS_VERIFIED]])

    completion_pct = round((installed_count / total_items * 100), 1) if total_items > 0 else 0.0
    field_ready_pct = round(((installed_count + delivered_count) / total_items * 100), 1) if total_items > 0 else 0.0

    # Can close out?
    can_close = (
        total_items > 0 and
        installed_count == total_items and
        open_punches == 0 and
        critical_punches == 0
    )

    return {
        "job_code": job_code,
        "total_items": total_items,
        "status_counts": status_counts,
        "phase_counts": phase_counts,
        "installed_count": installed_count,
        "delivered_count": delivered_count,
        "shipped_count": shipped_count,
        "completion_pct": completion_pct,
        "field_ready_pct": field_ready_pct,
        "total_punch_items": len(punch_items),
        "open_punches": open_punches,
        "resolved_punches": resolved_punches,
        "critical_punches": critical_punches,
        "daily_reports_count": len(daily_reports),
        "installation_records_count": len(install_records),
        "total_work_orders": len(work_orders),
        "can_close": can_close,
    }


def get_field_summary(wo_base_dir: str, base_dir: str) -> dict:
    """Get summary metrics across all projects for the field dashboard."""
    field_root = os.path.join(base_dir, "data", "field_ops")
    projects = []
    if os.path.isdir(field_root):
        projects = [d for d in os.listdir(field_root)
                    if os.path.isdir(os.path.join(field_root, d))]

    # Also include projects that have shipped/delivered items but no field_ops yet
    wo_root = wo_base_dir
    if os.path.isdir(wo_root):
        for proj in os.listdir(wo_root):
            if proj not in projects and os.path.isdir(os.path.join(wo_root, proj)):
                # Check if any items are in shipping/install phase
                wos = _load_all_work_orders(wo_base_dir, proj)
                for wo in wos:
                    if any(i.status in PHASE_SHIPPING or i.status == STATUS_INSTALLED for i in wo.items):
                        projects.append(proj)
                        break

    total_items_field = 0
    total_installed = 0
    total_delivered = 0
    total_open_punches = 0
    total_critical_punches = 0
    project_completions = []

    for proj in sorted(set(projects)):
        comp = get_project_completion(wo_base_dir, base_dir, proj)
        if comp["total_items"] > 0 and (comp["installed_count"] > 0 or comp["delivered_count"] > 0 or comp["shipped_count"] > 0):
            project_completions.append(comp)
            total_items_field += comp["total_items"]
            total_installed += comp["installed_count"]
            total_delivered += comp["delivered_count"]
            total_open_punches += comp["open_punches"]
            total_critical_punches += comp["critical_punches"]

    overall_pct = round((total_installed / total_items_field * 100), 1) if total_items_field > 0 else 0.0

    return {
        "active_projects": len(project_completions),
        "total_items_field": total_items_field,
        "total_installed": total_installed,
        "total_delivered": total_delivered,
        "total_open_punches": total_open_punches,
        "total_critical_punches": total_critical_punches,
        "overall_completion_pct": overall_pct,
        "projects": project_completions,
    }


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _load_all_work_orders(wo_base_dir: str, job_code: str) -> List[WorkOrder]:
    """Load all full WorkOrder objects for a project."""
    wo_dir = os.path.join(wo_base_dir, job_code, "work_orders")
    if not os.path.isdir(wo_dir):
        return []
    results = []
    for fname in os.listdir(wo_dir):
        if not fname.endswith(".json"):
            continue
        wo = load_work_order(wo_base_dir, job_code, fname.replace(".json", ""))
        if wo:
            results.append(wo)
    return results


def _find_wo_item(wo_base_dir: str, job_code: str, item_id: str):
    """Find a WO and item by item_id across all WOs in a project."""
    wo_dir = os.path.join(wo_base_dir, job_code, "work_orders")
    if not os.path.isdir(wo_dir):
        return None, None
    for wo_file in os.listdir(wo_dir):
        if not wo_file.endswith(".json"):
            continue
        wo = load_work_order(wo_base_dir, job_code, wo_file.replace(".json", ""))
        if not wo:
            continue
        for item in wo.items:
            if item.item_id == item_id:
                return wo, item
    return None, None
