"""
TitanForge — Work Order Management System (Phase 2)
=====================================================
Full 12-step fabrication lifecycle with operator assignment,
foreman queue management, and role-gated views.

Item Lifecycle (from RULES.md):
  Queued → Approved → Stickers Printed → Staged (Laborer)
  → In Progress (Operator/Welder) → Fabricated
  → QC Pending → QC Approved (or Rejected → back to operator)
  → Ready to Ship → Shipped → Delivered → Installed

Data stored as JSON: data/shop_drawings/{job_code}/work_orders/{wo_id}.json

Reference: RULES.md §5 (Work Order Item Lifecycle), §3 (Role Definitions)
"""

import os
import json
import datetime
import uuid
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Tuple


# ─────────────────────────────────────────────────────────────────────────────
# WORK ORDER ITEM STATUSES — full 12-step lifecycle
# ─────────────────────────────────────────────────────────────────────────────

STATUS_QUEUED = "queued"
STATUS_APPROVED = "approved"
STATUS_STICKERS_PRINTED = "stickers_printed"
STATUS_STAGED = "staged"                    # NEW: Laborer confirmed staged
STATUS_IN_PROGRESS = "in_progress"
STATUS_FABRICATED = "fabricated"             # NEW: Operator finished, awaiting QC
STATUS_QC_PENDING = "qc_pending"            # NEW: In QC queue
STATUS_QC_APPROVED = "qc_approved"          # NEW: Passed QC
STATUS_QC_REJECTED = "qc_rejected"          # NEW: Failed QC → returns to operator
STATUS_READY_TO_SHIP = "ready_to_ship"      # NEW: QC passed, staged for shipping
STATUS_SHIPPED = "shipped"                  # NEW: On a truck
STATUS_DELIVERED = "delivered"              # NEW: Arrived at site
STATUS_INSTALLED = "installed"              # NEW: Installed in field
STATUS_COMPLETE = "complete"                # Legacy alias → maps to fabricated
STATUS_ON_HOLD = "on_hold"

VALID_STATUSES = [
    STATUS_QUEUED, STATUS_APPROVED, STATUS_STICKERS_PRINTED, STATUS_STAGED,
    STATUS_IN_PROGRESS, STATUS_FABRICATED, STATUS_QC_PENDING, STATUS_QC_APPROVED,
    STATUS_QC_REJECTED, STATUS_READY_TO_SHIP, STATUS_SHIPPED, STATUS_DELIVERED,
    STATUS_INSTALLED, STATUS_ON_HOLD,
]

# ── Status flow: which transitions are legal ────────────────────────────────

STATUS_FLOW = {
    STATUS_QUEUED:          [STATUS_APPROVED, STATUS_ON_HOLD],
    STATUS_APPROVED:        [STATUS_STICKERS_PRINTED, STATUS_ON_HOLD],
    STATUS_STICKERS_PRINTED:[STATUS_STAGED, STATUS_IN_PROGRESS],   # Can skip staged
    STATUS_STAGED:          [STATUS_IN_PROGRESS],
    STATUS_IN_PROGRESS:     [STATUS_FABRICATED, STATUS_ON_HOLD],
    STATUS_FABRICATED:      [STATUS_QC_PENDING],
    STATUS_QC_PENDING:      [STATUS_QC_APPROVED, STATUS_QC_REJECTED],
    STATUS_QC_APPROVED:     [STATUS_READY_TO_SHIP],
    STATUS_QC_REJECTED:     [STATUS_IN_PROGRESS],                  # Back to operator
    STATUS_READY_TO_SHIP:   [STATUS_SHIPPED],
    STATUS_SHIPPED:         [STATUS_DELIVERED],
    STATUS_DELIVERED:       [STATUS_INSTALLED],
    STATUS_INSTALLED:       [],                                     # Terminal state
    STATUS_ON_HOLD:         [STATUS_QUEUED, STATUS_APPROVED, STATUS_IN_PROGRESS],
}

STATUS_LABELS = {
    STATUS_QUEUED:          "Queued",
    STATUS_APPROVED:        "Approved",
    STATUS_STICKERS_PRINTED:"Stickers Printed",
    STATUS_STAGED:          "Staged",
    STATUS_IN_PROGRESS:     "In Progress",
    STATUS_FABRICATED:      "Fabricated",
    STATUS_QC_PENDING:      "QC Pending",
    STATUS_QC_APPROVED:     "QC Approved",
    STATUS_QC_REJECTED:     "QC Rejected",
    STATUS_READY_TO_SHIP:   "Ready to Ship",
    STATUS_SHIPPED:         "Shipped",
    STATUS_DELIVERED:       "Delivered",
    STATUS_INSTALLED:       "Installed",
    STATUS_ON_HOLD:         "On Hold",
}

# Status color classes for UI
STATUS_COLORS = {
    STATUS_QUEUED:          "gray",
    STATUS_APPROVED:        "blue",
    STATUS_STICKERS_PRINTED:"blue",
    STATUS_STAGED:          "cyan",
    STATUS_IN_PROGRESS:     "orange",
    STATUS_FABRICATED:      "green",
    STATUS_QC_PENDING:      "yellow",
    STATUS_QC_APPROVED:     "green",
    STATUS_QC_REJECTED:     "red",
    STATUS_READY_TO_SHIP:   "green",
    STATUS_SHIPPED:         "purple",
    STATUS_DELIVERED:       "purple",
    STATUS_INSTALLED:       "green",
    STATUS_ON_HOLD:         "red",
}

# ── Phase groupings (which statuses belong to which phase of work) ──────────

PHASE_PREFAB = [STATUS_QUEUED, STATUS_APPROVED, STATUS_STICKERS_PRINTED, STATUS_STAGED]
PHASE_FABRICATION = [STATUS_IN_PROGRESS, STATUS_FABRICATED]
PHASE_QC = [STATUS_QC_PENDING, STATUS_QC_APPROVED, STATUS_QC_REJECTED]
PHASE_SHIPPING = [STATUS_READY_TO_SHIP, STATUS_SHIPPED, STATUS_DELIVERED, STATUS_INSTALLED]


# ─────────────────────────────────────────────────────────────────────────────
# MACHINE TYPES (for operator assignment filtering)
# ─────────────────────────────────────────────────────────────────────────────

MACHINE_TYPES = {
    "WELDING":  {"label": "Welding Bay",       "operator_type": "welder"},
    "Z1":       {"label": "Z-Purlin Line #1",  "operator_type": "roll_forming_operator"},
    "Z2":       {"label": "Z-Purlin Line #2",  "operator_type": "roll_forming_operator"},
    "C1":       {"label": "C-Channel Line #1", "operator_type": "roll_forming_operator"},
    "SPARTAN":  {"label": "Spartan Rib Line",  "operator_type": "roll_forming_operator"},
    "P1":       {"label": "Panel Line #1",     "operator_type": "roll_forming_operator"},
    "ANGLE":    {"label": "Angle Line",        "operator_type": "roll_forming_operator"},
    "BRAKE":    {"label": "Press Brake",       "operator_type": "roll_forming_operator"},
    "TRIM":     {"label": "Trim Table",        "operator_type": "roll_forming_operator"},
}


# ─────────────────────────────────────────────────────────────────────────────
# WORK ORDER ITEM (one per component)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class WorkOrderItem:
    """A single fabrication task within a work order."""
    item_id: str = ""              # Unique ID (auto-generated)
    ship_mark: str = ""            # e.g., "C1", "B1", "PG-A1"
    component_type: str = ""       # "column", "rafter", "purlin", "sag_rod", etc.
    description: str = ""          # e.g., "Column C1 — 14x4x10GA, 19'-6 3/8\""
    quantity: int = 1
    machine: str = ""              # Machine assignment from config
    drawing_ref: str = ""          # PDF filename reference
    status: str = STATUS_QUEUED

    # ── Assignment (Phase 2) ────────────────────
    assigned_to: str = ""          # Username of operator/welder assigned
    assigned_by: str = ""          # Foreman who assigned
    assigned_at: str = ""          # ISO timestamp
    priority: int = 50             # 1=urgent, 50=normal, 99=low (foreman sets)

    # ── QR tracking ─────────────────────────────
    started_by: str = ""           # Username who scanned start
    started_at: str = ""           # ISO timestamp
    finished_by: str = ""          # Username who scanned finish
    finished_at: str = ""          # ISO timestamp
    duration_minutes: float = 0.0  # Auto-calculated

    # ── Staging (Laborer) ───────────────────────
    staged_by: str = ""            # Laborer who staged
    staged_at: str = ""            # ISO timestamp

    # ── QC (Phase 3 will expand) ────────────────
    qc_inspector: str = ""         # Inspector username
    qc_at: str = ""                # ISO timestamp
    qc_result: str = ""            # "approved" or "rejected"
    qc_notes: str = ""             # Inspector notes / rejection reason

    # ── Shipping ────────────────────────────────
    load_id: str = ""              # Which shipping load this item is on
    shipped_at: str = ""
    delivered_at: str = ""
    installed_at: str = ""

    # ── Notes ───────────────────────────────────
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "WorkOrderItem":
        item = cls()
        for k, v in d.items():
            if hasattr(item, k):
                setattr(item, k, v)
        return item

    def can_transition_to(self, new_status: str) -> bool:
        """Check if this item can legally move to new_status."""
        allowed = STATUS_FLOW.get(self.status, [])
        return new_status in allowed

    @property
    def status_label(self) -> str:
        return STATUS_LABELS.get(self.status, self.status)

    @property
    def status_color(self) -> str:
        return STATUS_COLORS.get(self.status, "gray")

    @property
    def is_active(self) -> bool:
        """Item is in an active fabrication phase."""
        return self.status in [STATUS_IN_PROGRESS, STATUS_FABRICATED]

    @property
    def is_done(self) -> bool:
        """Item has passed QC and is in shipping/delivery pipeline."""
        return self.status in PHASE_SHIPPING + [STATUS_QC_APPROVED]

    @property
    def needs_attention(self) -> bool:
        """Item needs action (rejected, on hold, or unassigned but staged)."""
        if self.status == STATUS_QC_REJECTED:
            return True
        if self.status == STATUS_ON_HOLD:
            return True
        if self.status == STATUS_STAGED and not self.assigned_to:
            return True
        return False


# ─────────────────────────────────────────────────────────────────────────────
# WORK ORDER (one per project generation)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class WorkOrder:
    """A complete work order for a project's fabrication run."""
    work_order_id: str = ""        # Unique ID
    job_code: str = ""
    revision: str = ""             # Drawing revision this WO is for
    created_at: str = ""           # ISO timestamp
    created_by: str = ""           # Username
    status: str = STATUS_QUEUED
    approved_at: str = ""
    approved_by: str = ""
    stickers_printed_at: str = ""
    items: List[WorkOrderItem] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict:
        d = {
            "work_order_id": self.work_order_id,
            "job_code": self.job_code,
            "revision": self.revision,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "status": self.status,
            "approved_at": self.approved_at,
            "approved_by": self.approved_by,
            "stickers_printed_at": self.stickers_printed_at,
            "notes": self.notes,
            "items": [item.to_dict() for item in self.items],
        }
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "WorkOrder":
        wo = cls()
        for k, v in d.items():
            if k == "items":
                wo.items = [WorkOrderItem.from_dict(i) for i in v]
            elif hasattr(wo, k):
                setattr(wo, k, v)
        return wo

    # ── Computed properties ──────────────────────────────────────────────

    @property
    def total_items(self) -> int:
        return len(self.items)

    @property
    def completed_items(self) -> int:
        """Items that have passed the fabrication phase (fabricated or beyond)."""
        done_statuses = [STATUS_FABRICATED, STATUS_QC_PENDING, STATUS_QC_APPROVED,
                         STATUS_READY_TO_SHIP, STATUS_SHIPPED, STATUS_DELIVERED,
                         STATUS_INSTALLED, STATUS_COMPLETE]
        return sum(1 for i in self.items if i.status in done_statuses)

    @property
    def in_progress_items(self) -> int:
        return sum(1 for i in self.items if i.status == STATUS_IN_PROGRESS)

    @property
    def qc_pending_items(self) -> int:
        return sum(1 for i in self.items if i.status in [STATUS_QC_PENDING, STATUS_FABRICATED])

    @property
    def rejected_items(self) -> int:
        return sum(1 for i in self.items if i.status == STATUS_QC_REJECTED)

    @property
    def shipped_items(self) -> int:
        return sum(1 for i in self.items if i.status in
                   [STATUS_SHIPPED, STATUS_DELIVERED, STATUS_INSTALLED])

    @property
    def ready_to_ship_items(self) -> int:
        return sum(1 for i in self.items if i.status == STATUS_READY_TO_SHIP)

    @property
    def progress_pct(self) -> float:
        if self.total_items == 0:
            return 0.0
        return round(100.0 * self.completed_items / self.total_items, 1)

    @property
    def total_fab_minutes(self) -> float:
        return sum(i.duration_minutes for i in self.items
                   if i.status not in [STATUS_QUEUED, STATUS_APPROVED,
                                        STATUS_STICKERS_PRINTED, STATUS_STAGED])

    def summary(self) -> dict:
        return {
            "work_order_id": self.work_order_id,
            "job_code": self.job_code,
            "revision": self.revision,
            "status": self.status,
            "status_label": STATUS_LABELS.get(self.status, self.status),
            "created_at": self.created_at,
            "total_items": self.total_items,
            "completed_items": self.completed_items,
            "in_progress_items": self.in_progress_items,
            "qc_pending_items": self.qc_pending_items,
            "rejected_items": self.rejected_items,
            "ready_to_ship_items": self.ready_to_ship_items,
            "shipped_items": self.shipped_items,
            "progress_pct": self.progress_pct,
            "total_fab_minutes": round(self.total_fab_minutes, 1),
        }

    def status_breakdown(self) -> dict:
        """Count items by status — for dashboard visualizations."""
        counts = {}
        for item in self.items:
            counts[item.status] = counts.get(item.status, 0) + 1
        return counts

    # ── Auto-compute WO-level status from item statuses ─────────────────

    def recompute_status(self):
        """Update WO status based on aggregate item statuses.
        Does NOT save — caller must save after."""
        if not self.items:
            return

        statuses = set(i.status for i in self.items)

        # All items installed → WO is installed
        if all(i.status == STATUS_INSTALLED for i in self.items):
            self.status = STATUS_INSTALLED
        # All items delivered or beyond
        elif all(i.status in [STATUS_DELIVERED, STATUS_INSTALLED] for i in self.items):
            self.status = STATUS_DELIVERED
        # All items shipped or beyond
        elif all(i.status in [STATUS_SHIPPED, STATUS_DELIVERED, STATUS_INSTALLED]
                 for i in self.items):
            self.status = STATUS_SHIPPED
        # All items QC approved or beyond
        elif all(i.status in [STATUS_QC_APPROVED, STATUS_READY_TO_SHIP,
                               STATUS_SHIPPED, STATUS_DELIVERED, STATUS_INSTALLED]
                 for i in self.items):
            self.status = STATUS_QC_APPROVED
        # Any item in progress → WO is in progress
        elif STATUS_IN_PROGRESS in statuses:
            self.status = STATUS_IN_PROGRESS
        # All fabricated/QC → WO marks fabrication done
        elif all(i.status in [STATUS_FABRICATED, STATUS_QC_PENDING,
                               STATUS_QC_APPROVED, STATUS_QC_REJECTED,
                               STATUS_READY_TO_SHIP, STATUS_SHIPPED,
                               STATUS_DELIVERED, STATUS_INSTALLED]
                 for i in self.items):
            self.status = STATUS_FABRICATED

    # ── Queue helpers (Phase 2) ─────────────────────────────────────────

    def items_for_operator(self, username: str) -> List[WorkOrderItem]:
        """Get items assigned to a specific operator/welder."""
        return [i for i in self.items if i.assigned_to == username]

    def items_for_machine(self, machine: str) -> List[WorkOrderItem]:
        """Get all items queued/assigned to a specific machine."""
        return [i for i in self.items if i.machine == machine]

    def unassigned_items(self) -> List[WorkOrderItem]:
        """Items that need operator assignment."""
        assignable = [STATUS_STICKERS_PRINTED, STATUS_STAGED, STATUS_QC_REJECTED]
        return [i for i in self.items
                if i.status in assignable and not i.assigned_to]

    def items_needing_staging(self) -> List[WorkOrderItem]:
        """Items ready for laborer staging."""
        return [i for i in self.items
                if i.status == STATUS_STICKERS_PRINTED]

    def items_needing_qc(self) -> List[WorkOrderItem]:
        """Items waiting for QC inspection."""
        return [i for i in self.items
                if i.status in [STATUS_FABRICATED, STATUS_QC_PENDING]]


# ─────────────────────────────────────────────────────────────────────────────
# WORK ORDER STORAGE
# ─────────────────────────────────────────────────────────────────────────────

def _wo_dir(base_dir: str, job_code: str) -> str:
    """Get work order directory for a project."""
    import re
    safe = re.sub(r"[^a-zA-Z0-9_-]", "_", job_code)
    d = os.path.join(base_dir, safe, "work_orders")
    os.makedirs(d, exist_ok=True)
    return d


def save_work_order(base_dir: str, wo: WorkOrder):
    """Save a work order to disk."""
    d = _wo_dir(base_dir, wo.job_code)
    path = os.path.join(d, f"{wo.work_order_id}.json")
    with open(path, "w") as f:
        json.dump(wo.to_dict(), f, indent=2, default=str)
    return path


def load_work_order(base_dir: str, job_code: str, wo_id: str) -> Optional[WorkOrder]:
    """Load a specific work order."""
    d = _wo_dir(base_dir, job_code)
    path = os.path.join(d, f"{wo_id}.json")
    if not os.path.isfile(path):
        return None
    with open(path) as f:
        return WorkOrder.from_dict(json.load(f))


def list_work_orders(base_dir: str, job_code: str) -> List[dict]:
    """List all work orders for a project (summary only)."""
    d = _wo_dir(base_dir, job_code)
    results = []
    if not os.path.isdir(d):
        return results
    for fname in sorted(os.listdir(d), reverse=True):
        if not fname.endswith(".json"):
            continue
        try:
            with open(os.path.join(d, fname)) as f:
                data = json.load(f)
            wo = WorkOrder.from_dict(data)
            results.append(wo.summary())
        except Exception:
            continue
    return results


def list_all_work_orders(base_dir: str) -> List[dict]:
    """List ALL work orders across all projects (for shop floor dashboard).
    Returns list of summary dicts with job_code included."""
    results = []
    if not os.path.isdir(base_dir):
        return results
    for project_dir in os.listdir(base_dir):
        wo_dir = os.path.join(base_dir, project_dir, "work_orders")
        if not os.path.isdir(wo_dir):
            continue
        for fname in os.listdir(wo_dir):
            if not fname.endswith(".json"):
                continue
            try:
                with open(os.path.join(wo_dir, fname)) as f:
                    data = json.load(f)
                wo = WorkOrder.from_dict(data)
                results.append(wo.summary())
            except Exception:
                continue
    results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return results


def load_all_active_items(base_dir: str) -> List[dict]:
    """Load all items from active (non-terminal) work orders across all projects.
    Returns flat list of item dicts with wo_id and job_code added.
    Used for shop floor dashboard machine utilization."""
    terminal = [STATUS_INSTALLED]
    results = []
    if not os.path.isdir(base_dir):
        return results
    for project_dir in os.listdir(base_dir):
        wo_dir = os.path.join(base_dir, project_dir, "work_orders")
        if not os.path.isdir(wo_dir):
            continue
        for fname in os.listdir(wo_dir):
            if not fname.endswith(".json"):
                continue
            try:
                with open(os.path.join(wo_dir, fname)) as f:
                    data = json.load(f)
                wo = WorkOrder.from_dict(data)
                if wo.status in terminal:
                    continue
                for item in wo.items:
                    d = item.to_dict()
                    d["work_order_id"] = wo.work_order_id
                    d["job_code"] = wo.job_code
                    d["wo_status"] = wo.status
                    results.append(d)
            except Exception:
                continue
    return results


def find_work_order_by_item(base_dir: str, job_code: str, item_id: str):
    """Find the work order containing a specific item (for QR scan lookup).
    Returns (WorkOrder, WorkOrderItem) or (None, None)."""
    d = _wo_dir(base_dir, job_code)
    if not os.path.isdir(d):
        return None, None
    for fname in os.listdir(d):
        if not fname.endswith(".json"):
            continue
        try:
            with open(os.path.join(d, fname)) as f:
                data = json.load(f)
            wo = WorkOrder.from_dict(data)
            for item in wo.items:
                if item.item_id == item_id:
                    return wo, item
        except Exception:
            continue
    return None, None


# ─────────────────────────────────────────────────────────────────────────────
# OPERATOR QUEUE HELPERS (Phase 2)
# ─────────────────────────────────────────────────────────────────────────────

def get_operator_queue(base_dir: str, username: str) -> List[dict]:
    """Get all items assigned to a specific operator across all projects.
    Returns sorted by priority (1=urgent first), then assignment time.
    Used for My Station / My Work views."""
    results = []
    if not os.path.isdir(base_dir):
        return results
    for project_dir in os.listdir(base_dir):
        wo_dir = os.path.join(base_dir, project_dir, "work_orders")
        if not os.path.isdir(wo_dir):
            continue
        for fname in os.listdir(wo_dir):
            if not fname.endswith(".json"):
                continue
            try:
                with open(os.path.join(wo_dir, fname)) as f:
                    data = json.load(f)
                wo = WorkOrder.from_dict(data)
                for item in wo.items:
                    if item.assigned_to == username:
                        d = item.to_dict()
                        d["work_order_id"] = wo.work_order_id
                        d["job_code"] = wo.job_code
                        d["wo_revision"] = wo.revision
                        results.append(d)
            except Exception:
                continue
    # Sort: priority asc (1=urgent first), then assigned_at asc
    results.sort(key=lambda x: (x.get("priority", 50), x.get("assigned_at", "")))
    return results


def get_machine_queue(base_dir: str, machine: str) -> List[dict]:
    """Get all items queued for a specific machine across all projects.
    Used for machine status dashboards."""
    results = []
    if not os.path.isdir(base_dir):
        return results
    for project_dir in os.listdir(base_dir):
        wo_dir = os.path.join(base_dir, project_dir, "work_orders")
        if not os.path.isdir(wo_dir):
            continue
        for fname in os.listdir(wo_dir):
            if not fname.endswith(".json"):
                continue
            try:
                with open(os.path.join(wo_dir, fname)) as f:
                    data = json.load(f)
                wo = WorkOrder.from_dict(data)
                for item in wo.items:
                    if item.machine == machine and item.status not in PHASE_SHIPPING:
                        d = item.to_dict()
                        d["work_order_id"] = wo.work_order_id
                        d["job_code"] = wo.job_code
                        results.append(d)
            except Exception:
                continue
    results.sort(key=lambda x: (x.get("priority", 50), x.get("assigned_at", "")))
    return results


def get_shop_floor_summary(base_dir: str) -> dict:
    """Build a shop floor overview for the foreman dashboard.
    Returns machine utilization, status counts, and items needing attention."""
    machines = {m: {"label": info["label"], "active": 0, "queued": 0,
                     "done_today": 0, "items": []}
                for m, info in MACHINE_TYPES.items()}
    status_counts = {s: 0 for s in VALID_STATUSES}
    needs_attention = []
    today = datetime.date.today().isoformat()
    total_items = 0
    total_fab_minutes = 0.0

    if not os.path.isdir(base_dir):
        return {"machines": machines, "status_counts": status_counts,
                "needs_attention": [], "total_items": 0, "total_fab_minutes": 0}

    for project_dir in os.listdir(base_dir):
        wo_dir = os.path.join(base_dir, project_dir, "work_orders")
        if not os.path.isdir(wo_dir):
            continue
        for fname in os.listdir(wo_dir):
            if not fname.endswith(".json"):
                continue
            try:
                with open(os.path.join(wo_dir, fname)) as f:
                    data = json.load(f)
                wo = WorkOrder.from_dict(data)
                for item in wo.items:
                    total_items += 1
                    status_counts[item.status] = status_counts.get(item.status, 0) + 1
                    total_fab_minutes += item.duration_minutes

                    m = item.machine
                    if m in machines:
                        if item.status == STATUS_IN_PROGRESS:
                            machines[m]["active"] += 1
                        elif item.status in PHASE_PREFAB:
                            machines[m]["queued"] += 1
                        if (item.finished_at and item.finished_at.startswith(today)):
                            machines[m]["done_today"] += 1

                    if item.needs_attention:
                        d = item.to_dict()
                        d["work_order_id"] = wo.work_order_id
                        d["job_code"] = wo.job_code
                        needs_attention.append(d)
            except Exception:
                continue

    return {
        "machines": machines,
        "status_counts": status_counts,
        "needs_attention": needs_attention,
        "total_items": total_items,
        "total_fab_minutes": round(total_fab_minutes, 1),
    }


# ─────────────────────────────────────────────────────────────────────────────
# ITEM ACTIONS (Phase 2 — extended beyond QR scan)
# ─────────────────────────────────────────────────────────────────────────────

def assign_item(base_dir: str, job_code: str, item_id: str,
                assigned_to: str, assigned_by: str,
                priority: int = 50) -> dict:
    """Assign a work order item to an operator/welder.
    Called by foreman from the assignment panel."""
    wo, item = find_work_order_by_item(base_dir, job_code, item_id)
    if wo is None or item is None:
        return {"ok": False, "error": "Work order item not found"}

    # Can assign if item is in stickers_printed, staged, or qc_rejected (re-assign after rejection)
    assignable = [STATUS_STICKERS_PRINTED, STATUS_STAGED, STATUS_QC_REJECTED,
                  STATUS_APPROVED]
    if item.status not in assignable and not item.assigned_to:
        return {"ok": False, "error": f"Cannot assign — item status is '{item.status_label}'"}

    now = datetime.datetime.now().isoformat()
    item.assigned_to = assigned_to
    item.assigned_by = assigned_by
    item.assigned_at = now
    item.priority = priority

    # If re-assigning after QC rejection, reset status to in_progress-ready
    if item.status == STATUS_QC_REJECTED:
        item.status = STATUS_IN_PROGRESS
        item.qc_result = ""
        item.qc_notes = f"[Re-assigned after rejection] {item.qc_notes}"

    save_work_order(base_dir, wo)
    return {
        "ok": True,
        "action": "assigned",
        "item": item.to_dict(),
        "message": f"Assigned {item.ship_mark} to {assigned_to} (priority {priority})",
    }


def reassign_item(base_dir: str, job_code: str, item_id: str,
                  new_operator: str, reassigned_by: str) -> dict:
    """Reassign an item to a different operator. Foreman action."""
    wo, item = find_work_order_by_item(base_dir, job_code, item_id)
    if wo is None or item is None:
        return {"ok": False, "error": "Work order item not found"}

    old_operator = item.assigned_to
    now = datetime.datetime.now().isoformat()
    item.assigned_to = new_operator
    item.assigned_by = reassigned_by
    item.assigned_at = now

    save_work_order(base_dir, wo)
    return {
        "ok": True,
        "action": "reassigned",
        "item": item.to_dict(),
        "old_operator": old_operator,
        "message": f"Reassigned {item.ship_mark} from {old_operator} to {new_operator}",
    }


def reprioritize_item(base_dir: str, job_code: str, item_id: str,
                      new_priority: int, changed_by: str) -> dict:
    """Change an item's priority in the queue. Foreman action."""
    wo, item = find_work_order_by_item(base_dir, job_code, item_id)
    if wo is None or item is None:
        return {"ok": False, "error": "Work order item not found"}

    old_priority = item.priority
    item.priority = max(1, min(99, new_priority))

    save_work_order(base_dir, wo)
    return {
        "ok": True,
        "action": "reprioritized",
        "item": item.to_dict(),
        "old_priority": old_priority,
        "message": f"Priority for {item.ship_mark}: {old_priority} → {item.priority}",
    }


def stage_item(base_dir: str, job_code: str, item_id: str,
               staged_by: str) -> dict:
    """Mark an item as staged (laborer scanned/confirmed). Laborer action."""
    wo, item = find_work_order_by_item(base_dir, job_code, item_id)
    if wo is None or item is None:
        return {"ok": False, "error": "Work order item not found"}

    if item.status != STATUS_STICKERS_PRINTED:
        return {"ok": False,
                "error": f"Cannot stage — status is '{item.status_label}' (need Stickers Printed)"}

    now = datetime.datetime.now().isoformat()
    item.status = STATUS_STAGED
    item.staged_by = staged_by
    item.staged_at = now

    save_work_order(base_dir, wo)
    return {
        "ok": True,
        "action": "staged",
        "item": item.to_dict(),
        "message": f"Staged {item.ship_mark} at machine {item.machine}",
    }


def transition_item_status(base_dir: str, job_code: str, item_id: str,
                           new_status: str, changed_by: str,
                           notes: str = "") -> dict:
    """Generic status transition for items. Validates against STATUS_FLOW.
    Used for QC, shipping, delivery, and install transitions."""
    wo, item = find_work_order_by_item(base_dir, job_code, item_id)
    if wo is None or item is None:
        return {"ok": False, "error": "Work order item not found"}

    if not item.can_transition_to(new_status):
        allowed = STATUS_FLOW.get(item.status, [])
        labels = [STATUS_LABELS.get(s, s) for s in allowed]
        return {"ok": False,
                "error": f"Cannot move from '{item.status_label}' to "
                         f"'{STATUS_LABELS.get(new_status, new_status)}'. "
                         f"Allowed: {', '.join(labels) if labels else 'none'}"}

    now = datetime.datetime.now().isoformat()
    old_status = item.status
    item.status = new_status

    # Status-specific field updates
    if new_status == STATUS_FABRICATED:
        item.finished_by = changed_by
        item.finished_at = now
        if item.started_at:
            try:
                start = datetime.datetime.fromisoformat(item.started_at)
                delta = datetime.datetime.now() - start
                item.duration_minutes = round(delta.total_seconds() / 60.0, 1)
            except Exception:
                pass

    elif new_status == STATUS_QC_PENDING:
        item.qc_inspector = ""
        item.qc_at = ""
        item.qc_result = ""

    elif new_status == STATUS_QC_APPROVED:
        item.qc_inspector = changed_by
        item.qc_at = now
        item.qc_result = "approved"
        item.qc_notes = notes

    elif new_status == STATUS_QC_REJECTED:
        item.qc_inspector = changed_by
        item.qc_at = now
        item.qc_result = "rejected"
        item.qc_notes = notes

    elif new_status == STATUS_SHIPPED:
        item.shipped_at = now

    elif new_status == STATUS_DELIVERED:
        item.delivered_at = now

    elif new_status == STATUS_INSTALLED:
        item.installed_at = now

    if notes and new_status not in [STATUS_QC_APPROVED, STATUS_QC_REJECTED]:
        item.notes = f"[{STATUS_LABELS.get(new_status, new_status)}] {notes}\n" + item.notes

    # Recompute WO-level status
    wo.recompute_status()
    save_work_order(base_dir, wo)

    return {
        "ok": True,
        "action": "status_changed",
        "old_status": old_status,
        "new_status": new_status,
        "item": item.to_dict(),
        "progress": wo.summary(),
        "message": f"{item.ship_mark}: {STATUS_LABELS.get(old_status, old_status)} → "
                   f"{STATUS_LABELS.get(new_status, new_status)}",
    }


# ─────────────────────────────────────────────────────────────────────────────
# QR SCAN ACTIONS (updated for Phase 2 lifecycle)
# ─────────────────────────────────────────────────────────────────────────────

def qr_scan_start(base_dir: str, job_code: str, item_id: str,
                   scanned_by: str) -> dict:
    """Process a QR 'start_job' scan.
    Returns dict with status and updated item info."""
    wo, item = find_work_order_by_item(base_dir, job_code, item_id)
    if wo is None or item is None:
        return {"ok": False, "error": "Work order item not found"}

    if item.status in [STATUS_FABRICATED, STATUS_QC_PENDING, STATUS_QC_APPROVED,
                        STATUS_READY_TO_SHIP, STATUS_SHIPPED, STATUS_DELIVERED,
                        STATUS_INSTALLED]:
        return {"ok": False, "error": f"Item already past fabrication (status: {item.status_label})",
                "item": item.to_dict()}

    if item.status == STATUS_IN_PROGRESS:
        return {"ok": False, "error": "Item already in progress",
                "started_by": item.started_by,
                "started_at": item.started_at,
                "item": item.to_dict()}

    # Must be in staged, stickers_printed, or qc_rejected (rework) state at minimum
    startable = [STATUS_STAGED, STATUS_STICKERS_PRINTED, STATUS_QC_REJECTED]
    if item.status not in startable:
        # Also check WO-level approval
        if wo.status not in [STATUS_APPROVED, STATUS_STICKERS_PRINTED, STATUS_IN_PROGRESS]:
            return {"ok": False, "error": f"Work order not ready (status: {wo.status})"}
        if item.status not in [STATUS_APPROVED]:
            return {"ok": False,
                    "error": f"Item not ready to start (status: {item.status_label})"}

    now = datetime.datetime.now().isoformat()
    item.status = STATUS_IN_PROGRESS
    item.started_by = scanned_by
    item.started_at = now

    # If this is the first item started, update WO status
    if wo.status != STATUS_IN_PROGRESS:
        wo.status = STATUS_IN_PROGRESS

    save_work_order(base_dir, wo)

    return {
        "ok": True,
        "action": "started",
        "item": item.to_dict(),
        "work_order_id": wo.work_order_id,
        "message": f"Started {item.ship_mark}: {item.description}",
    }


def qr_scan_finish(base_dir: str, job_code: str, item_id: str,
                    scanned_by: str) -> dict:
    """Process a QR 'finish_job' scan.
    Now transitions to 'fabricated' instead of legacy 'complete'.
    Calculates duration and updates WO status."""
    wo, item = find_work_order_by_item(base_dir, job_code, item_id)
    if wo is None or item is None:
        return {"ok": False, "error": "Work order item not found"}

    if item.status in [STATUS_FABRICATED, STATUS_QC_PENDING, STATUS_QC_APPROVED,
                        STATUS_READY_TO_SHIP, STATUS_SHIPPED, STATUS_DELIVERED,
                        STATUS_INSTALLED]:
        return {"ok": False, "error": f"Item already finished (status: {item.status_label})",
                "item": item.to_dict()}

    if item.status != STATUS_IN_PROGRESS:
        return {"ok": False, "error": "Item not started yet — scan Start first",
                "item": item.to_dict()}

    now = datetime.datetime.now()
    item.status = STATUS_FABRICATED  # Phase 2: goes to fabricated, then QC
    item.finished_by = scanned_by
    item.finished_at = now.isoformat()

    # Calculate duration
    try:
        start = datetime.datetime.fromisoformat(item.started_at)
        delta = now - start
        item.duration_minutes = round(delta.total_seconds() / 60.0, 1)
    except Exception:
        item.duration_minutes = 0.0

    # Recompute WO status
    wo.recompute_status()
    save_work_order(base_dir, wo)

    return {
        "ok": True,
        "action": "finished",
        "item": item.to_dict(),
        "work_order_id": wo.work_order_id,
        "duration_minutes": item.duration_minutes,
        "message": (f"Finished {item.ship_mark}: {item.description} "
                    f"({item.duration_minutes:.1f} min)"),
        "wo_complete": wo.status == STATUS_FABRICATED,
        "progress": wo.summary(),
    }


# ─────────────────────────────────────────────────────────────────────────────
# WORK ORDER CREATION
# ─────────────────────────────────────────────────────────────────────────────

def create_work_order(job_code: str, revision: str, created_by: str,
                      drawing_files: list, config_dict: dict) -> WorkOrder:
    """Create a work order from shop drawing generation results.

    Args:
        job_code: Project job code
        revision: Drawing revision letter
        created_by: Username creating the WO
        drawing_files: List of file dicts from generate_all_shop_drawings()
        config_dict: ShopDrawingConfig.to_dict()

    Returns:
        WorkOrder with items for each fabrication component
    """
    from shop_drawings.config import MACHINES

    now = datetime.datetime.now().isoformat()
    wo = WorkOrder(
        work_order_id=f"WO-{job_code}-{revision}-{uuid.uuid4().hex[:6].upper()}",
        job_code=job_code,
        revision=revision,
        created_at=now,
        created_by=created_by,
        status=STATUS_QUEUED,
    )

    n_frames = config_dict.get("n_frames", 1)
    frame_type = config_dict.get("frame_type", "tee")
    n_columns = n_frames if frame_type == "tee" else n_frames * 2

    # ── Column items ──
    for i in range(n_columns):
        mark = f"C{i+1}"
        wo.items.append(WorkOrderItem(
            item_id=f"{wo.work_order_id}-{mark}",
            ship_mark=mark,
            component_type="column",
            description=f"Column {mark} — 14x4x10GA box beam",
            quantity=1,
            machine="WELDING",
            drawing_ref=f"{job_code}_C1.pdf",
        ))

    # ── Rafter items ──
    for i in range(n_frames):
        mark = f"B{i+1}"
        wo.items.append(WorkOrderItem(
            item_id=f"{wo.work_order_id}-{mark}",
            ship_mark=mark,
            component_type="rafter",
            description=f"Rafter {mark} — 14x4x10GA box beam",
            quantity=1,
            machine="WELDING",
            drawing_ref=f"{job_code}_B1.pdf",
        ))

    # ── Purlin groups (one item per group) ──
    n_bays = max(1, n_frames - 1)
    for i, label in enumerate(["First", "Middle", "Last"][:min(3, n_bays)]):
        mark = f"PG-{chr(65+i)}1"
        wo.items.append(WorkOrderItem(
            item_id=f"{wo.work_order_id}-{mark}",
            ship_mark=mark,
            component_type="purlin",
            description=f"Purlin Group {label} — Z-12x3.5x12GA",
            quantity=1,
            machine="Z1",
            drawing_ref=f"{job_code}_PURLINS.pdf",
        ))

    # ── Sag rods (bundled per sticker grouping = per 10) ──
    n_sag_rods = n_frames * 2
    n_sag_pieces = n_sag_rods * 2
    n_sag_bundles = max(1, -(-n_sag_pieces // 10))
    for i in range(n_sag_bundles):
        mark = f"SR-{i+1}"
        bundle_qty = min(10, n_sag_pieces - i * 10)
        wo.items.append(WorkOrderItem(
            item_id=f"{wo.work_order_id}-{mark}",
            ship_mark=mark,
            component_type="sag_rod",
            description=f"Sag Rod Bundle {i+1} — 2x2 angle, {bundle_qty} pcs",
            quantity=bundle_qty,
            machine="ANGLE",
            drawing_ref=f"{job_code}_CUTLISTS.pdf",
        ))

    # ── Hurricane straps (bundled per 10) ──
    n_straps = n_frames * 4
    n_strap_bundles = max(1, -(-n_straps // 10))
    for i in range(n_strap_bundles):
        mark = f"HS-{i+1}"
        bundle_qty = min(10, n_straps - i * 10)
        wo.items.append(WorkOrderItem(
            item_id=f"{wo.work_order_id}-{mark}",
            ship_mark=mark,
            component_type="strap",
            description=f"Strap Bundle {i+1} — 1.5x10GA, {bundle_qty} pcs",
            quantity=bundle_qty,
            machine="P1",
            drawing_ref=f"{job_code}_CUTLISTS.pdf",
        ))

    # ── Endcap channels ──
    wo.items.append(WorkOrderItem(
        item_id=f"{wo.work_order_id}-EC-1",
        ship_mark="EC-1",
        component_type="endcap",
        description="Endcap U-Channel (Front End)",
        quantity=1,
        machine="C1",
        drawing_ref=f"{job_code}_CUTLISTS.pdf",
    ))
    wo.items.append(WorkOrderItem(
        item_id=f"{wo.work_order_id}-EC-2",
        ship_mark="EC-2",
        component_type="endcap",
        description="Endcap U-Channel (Back End)",
        quantity=1,
        machine="C1",
        drawing_ref=f"{job_code}_CUTLISTS.pdf",
    ))

    # ── Roofing panels (one item — rolled in bulk) ──
    wo.items.append(WorkOrderItem(
        item_id=f"{wo.work_order_id}-ROOF",
        ship_mark="ROOF",
        component_type="roofing",
        description="Spartan Rib Roofing Panels — full run",
        quantity=1,
        machine="SPARTAN",
        drawing_ref=f"{job_code}_CUTLISTS.pdf",
    ))

    return wo
