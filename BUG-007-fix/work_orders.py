"""
TitanForge — Work Order Management System
==========================================
Handles the full lifecycle of fabrication work orders:
  1. Work order creation (from finalized shop drawings)
  2. QR scan start/finish tracking
  3. Duration calculation and fabrication metrics
  4. Status tracking (queued → approved → in_progress → complete)
  5. Rollback support (any status can move backward)
  6. Role-based status transitions
  7. Notification hooks for status changes

Data is stored as JSON files per project in data/shop_drawings/{job_code}/work_orders/

Work order flow (from WORK_ORDER_FLOW config):
  shop_drawings_finalized → work_order_created → manual_approval →
  stickers_printed → QR start_job → QR finish_job

BUG-007 FIX: Added rollback support, role-based transitions, notification system
"""

import os
import json
import datetime
import uuid
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict


# ─────────────────────────────────────────────
# WORK ORDER STATUSES
# ─────────────────────────────────────────────

STATUS_QUEUED = "queued"
STATUS_APPROVED = "approved"
STATUS_STICKERS_PRINTED = "stickers_printed"
STATUS_IN_PROGRESS = "in_progress"
STATUS_COMPLETE = "complete"
STATUS_ON_HOLD = "on_hold"

VALID_STATUSES = [
    STATUS_QUEUED, STATUS_APPROVED, STATUS_STICKERS_PRINTED,
    STATUS_IN_PROGRESS, STATUS_COMPLETE, STATUS_ON_HOLD,
]

# Forward transitions (normal workflow)
STATUS_FLOW = {
    STATUS_QUEUED: [STATUS_APPROVED, STATUS_ON_HOLD],
    STATUS_APPROVED: [STATUS_STICKERS_PRINTED, STATUS_ON_HOLD],
    STATUS_STICKERS_PRINTED: [STATUS_IN_PROGRESS],
    STATUS_IN_PROGRESS: [STATUS_COMPLETE, STATUS_ON_HOLD],
    STATUS_COMPLETE: [],
    STATUS_ON_HOLD: [STATUS_QUEUED, STATUS_APPROVED],
}

# BUG-007 FIX: Rollback transitions (moving backward in the pipeline)
# Anyone can rollback to any previous status
STATUS_ROLLBACK = {
    STATUS_APPROVED: [STATUS_QUEUED],
    STATUS_STICKERS_PRINTED: [STATUS_QUEUED, STATUS_APPROVED],
    STATUS_IN_PROGRESS: [STATUS_QUEUED, STATUS_APPROVED, STATUS_STICKERS_PRINTED],
    STATUS_COMPLETE: [STATUS_QUEUED, STATUS_APPROVED, STATUS_STICKERS_PRINTED, STATUS_IN_PROGRESS],
    STATUS_ON_HOLD: [STATUS_QUEUED, STATUS_APPROVED, STATUS_STICKERS_PRINTED, STATUS_IN_PROGRESS],
}

# Pipeline order for comparison
STATUS_ORDER = [STATUS_QUEUED, STATUS_APPROVED, STATUS_STICKERS_PRINTED,
                STATUS_IN_PROGRESS, STATUS_COMPLETE]

STATUS_LABELS = {
    STATUS_QUEUED: "Queued",
    STATUS_APPROVED: "Approved",
    STATUS_STICKERS_PRINTED: "Stickers Printed",
    STATUS_IN_PROGRESS: "In Progress",
    STATUS_COMPLETE: "Complete",
    STATUS_ON_HOLD: "On Hold",
}

# BUG-007 FIX: Role-based access for each transition
# Admin approves, Shop Foreman starts/completes, QC signs off
STATUS_TRANSITION_ROLES = {
    # (from_status, to_status): list of allowed roles
    (STATUS_QUEUED, STATUS_APPROVED): ["admin", "estimator"],
    (STATUS_APPROVED, STATUS_STICKERS_PRINTED): ["admin", "estimator", "shop"],
    (STATUS_STICKERS_PRINTED, STATUS_IN_PROGRESS): ["admin", "shop"],
    (STATUS_IN_PROGRESS, STATUS_COMPLETE): ["admin", "shop", "qc"],
    # Hold/resume — admin and estimator
    (STATUS_QUEUED, STATUS_ON_HOLD): ["admin", "estimator"],
    (STATUS_APPROVED, STATUS_ON_HOLD): ["admin", "estimator"],
    (STATUS_STICKERS_PRINTED, STATUS_ON_HOLD): ["admin", "estimator", "shop"],
    (STATUS_IN_PROGRESS, STATUS_ON_HOLD): ["admin", "estimator", "shop"],
    (STATUS_ON_HOLD, STATUS_QUEUED): ["admin", "estimator"],
    (STATUS_ON_HOLD, STATUS_APPROVED): ["admin", "estimator"],
    # Rollback — any authenticated user can rollback
    "rollback_default": ["admin", "estimator", "shop", "qc"],
}

# BUG-007 FIX: Notification targets for each status change
STATUS_NOTIFICATIONS = {
    STATUS_APPROVED: {
        "message": "Work order {wo_id} has been approved and is ready for sticker printing.",
        "notify_roles": ["shop"],
    },
    STATUS_STICKERS_PRINTED: {
        "message": "Stickers printed for work order {wo_id}. Fabrication can begin.",
        "notify_roles": ["shop"],
    },
    STATUS_IN_PROGRESS: {
        "message": "Fabrication started on work order {wo_id}.",
        "notify_roles": ["admin", "estimator"],
    },
    STATUS_COMPLETE: {
        "message": "Work order {wo_id} is COMPLETE. Ready for QC inspection.",
        "notify_roles": ["admin", "qc"],
    },
    STATUS_ON_HOLD: {
        "message": "Work order {wo_id} has been placed ON HOLD.",
        "notify_roles": ["admin", "estimator", "shop"],
    },
}


# ─────────────────────────────────────────────
# NOTIFICATION SYSTEM
# ─────────────────────────────────────────────

# In-memory notification store (persists per server session)
_notifications = []  # list of notification dicts
_MAX_NOTIFICATIONS = 500


def create_notification(wo_id: str, job_code: str, from_status: str,
                       to_status: str, changed_by: str) -> dict:
    """Create a notification record for a status change."""
    template = STATUS_NOTIFICATIONS.get(to_status, {})
    message = template.get("message", f"Work order {wo_id} status changed to {STATUS_LABELS.get(to_status, to_status)}.")
    message = message.format(wo_id=wo_id, job_code=job_code)

    notif = {
        "id": uuid.uuid4().hex[:8],
        "timestamp": datetime.datetime.now().isoformat(),
        "wo_id": wo_id,
        "job_code": job_code,
        "from_status": from_status,
        "to_status": to_status,
        "changed_by": changed_by,
        "message": message,
        "notify_roles": template.get("notify_roles", ["admin"]),
        "read_by": [],
    }

    _notifications.insert(0, notif)
    # Trim old notifications
    if len(_notifications) > _MAX_NOTIFICATIONS:
        _notifications[:] = _notifications[:_MAX_NOTIFICATIONS]

    return notif


def get_notifications(role: str = None, limit: int = 50, unread_only: bool = False,
                     user: str = None) -> List[dict]:
    """Get notifications, optionally filtered by role."""
    results = []
    for n in _notifications:
        if role and role not in n.get("notify_roles", []):
            continue
        if unread_only and user and user in n.get("read_by", []):
            continue
        results.append(n)
        if len(results) >= limit:
            break
    return results


def mark_notification_read(notif_id: str, user: str):
    """Mark a notification as read by a user."""
    for n in _notifications:
        if n["id"] == notif_id:
            if user not in n.get("read_by", []):
                n.setdefault("read_by", []).append(user)
            return True
    return False


def get_unread_count(role: str = None, user: str = None) -> int:
    """Get count of unread notifications for a role/user."""
    count = 0
    for n in _notifications:
        if role and role not in n.get("notify_roles", []):
            continue
        if user and user in n.get("read_by", []):
            continue
        count += 1
    return count


# ─────────────────────────────────────────────
# STATUS CHANGE LOGIC (BUG-007 FIX)
# ─────────────────────────────────────────────

def get_valid_transitions(current_status: str, include_rollback: bool = True) -> List[str]:
    """Get all valid next statuses from current status, including rollback options."""
    forward = STATUS_FLOW.get(current_status, [])
    if include_rollback:
        backward = STATUS_ROLLBACK.get(current_status, [])
        return list(dict.fromkeys(forward + backward))  # deduplicated, order preserved
    return forward


def is_rollback(from_status: str, to_status: str) -> bool:
    """Check if a transition is a rollback (moving backward in the pipeline)."""
    if from_status == STATUS_ON_HOLD or to_status == STATUS_ON_HOLD:
        return False  # Hold transitions aren't rollbacks
    from_idx = STATUS_ORDER.index(from_status) if from_status in STATUS_ORDER else -1
    to_idx = STATUS_ORDER.index(to_status) if to_status in STATUS_ORDER else -1
    return to_idx < from_idx


def can_transition(from_status: str, to_status: str, user_role: str = None) -> dict:
    """Check if a status transition is valid and authorized.

    Returns dict with 'allowed' bool and 'reason' string.
    """
    if from_status == to_status:
        return {"allowed": False, "reason": "Already in this status"}

    if to_status not in VALID_STATUSES:
        return {"allowed": False, "reason": f"Invalid status: {to_status}"}

    # Check if it's a valid forward transition
    forward = STATUS_FLOW.get(from_status, [])
    backward = STATUS_ROLLBACK.get(from_status, [])

    if to_status not in forward and to_status not in backward:
        return {"allowed": False,
                "reason": f"Cannot transition from {STATUS_LABELS.get(from_status)} to {STATUS_LABELS.get(to_status)}"}

    # Check role authorization
    if user_role:
        transition_key = (from_status, to_status)
        allowed_roles = STATUS_TRANSITION_ROLES.get(
            transition_key,
            STATUS_TRANSITION_ROLES.get("rollback_default", ["admin"])
        )
        if user_role not in allowed_roles:
            return {"allowed": False,
                    "reason": f"Role '{user_role}' not authorized for this transition. Required: {', '.join(allowed_roles)}"}

    return {"allowed": True, "reason": "OK"}


def change_work_order_status(base_dir: str, job_code: str, wo_id: str,
                             new_status: str, changed_by: str = "system",
                             user_role: str = None, notes: str = "") -> dict:
    """Change a work order's status with validation, rollback support, and notifications.

    This is the unified status change function that handles both forward
    transitions and rollbacks.

    Returns dict with ok, work_order, notification, etc.
    """
    wo = load_work_order(base_dir, job_code, wo_id)
    if wo is None:
        return {"ok": False, "error": "Work order not found"}

    old_status = wo.status

    # Validate the transition
    check = can_transition(old_status, new_status, user_role)
    if not check["allowed"]:
        return {"ok": False, "error": check["reason"]}

    rollback = is_rollback(old_status, new_status)
    now = datetime.datetime.now().isoformat()

    # Apply the status change
    wo.status = new_status

    # Set metadata based on target status
    if new_status == STATUS_APPROVED:
        wo.approved_at = now
        wo.approved_by = changed_by
    elif new_status == STATUS_STICKERS_PRINTED:
        wo.stickers_printed_at = now
    elif new_status == STATUS_ON_HOLD:
        wo.notes = f"[ON HOLD at {now}] Previous: {STATUS_LABELS.get(old_status, old_status)}. {changed_by}. " + (notes or wo.notes)

    # If rolling back, reset item statuses that are ahead of the new WO status
    if rollback:
        new_idx = STATUS_ORDER.index(new_status) if new_status in STATUS_ORDER else 0
        for item in wo.items:
            item_idx = STATUS_ORDER.index(item.status) if item.status in STATUS_ORDER else 0
            if item_idx > new_idx:
                # Reset item to queued (items follow their own QR-based flow)
                item.status = STATUS_QUEUED
                item.started_by = ""
                item.started_at = ""
                item.finished_by = ""
                item.finished_at = ""
                item.duration_minutes = 0.0

    # Add rollback note
    if rollback:
        rollback_note = f"[ROLLBACK at {now}] {STATUS_LABELS.get(old_status)} -> {STATUS_LABELS.get(new_status)} by {changed_by}"
        if notes:
            rollback_note += f". Reason: {notes}"
        wo.notes = rollback_note + ". " + wo.notes

    save_work_order(base_dir, wo)

    # Create notification
    notif = create_notification(wo_id, job_code, old_status, new_status, changed_by)

    return {
        "ok": True,
        "work_order": wo.to_dict(),
        "summary": wo.summary(),
        "notification": notif,
        "rollback": rollback,
        "from_status": old_status,
        "to_status": new_status,
        "message": f"Status changed: {STATUS_LABELS.get(old_status)} -> {STATUS_LABELS.get(new_status)}"
            + (" (ROLLBACK)" if rollback else ""),
    }


# ─────────────────────────────────────────────
# WORK ORDER ITEM (one per component)
# ─────────────────────────────────────────────

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
    # QR tracking
    started_by: str = ""           # Username who scanned start
    started_at: str = ""           # ISO timestamp
    finished_by: str = ""          # Username who scanned finish
    finished_at: str = ""          # ISO timestamp
    duration_minutes: float = 0.0  # Auto-calculated
    # Notes
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


# ─────────────────────────────────────────────
# WORK ORDER (one per project generation)
# ─────────────────────────────────────────────

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

    @property
    def total_items(self) -> int:
        return len(self.items)

    @property
    def completed_items(self) -> int:
        return sum(1 for i in self.items if i.status == STATUS_COMPLETE)

    @property
    def in_progress_items(self) -> int:
        return sum(1 for i in self.items if i.status == STATUS_IN_PROGRESS)

    @property
    def progress_pct(self) -> float:
        if self.total_items == 0:
            return 0.0
        return round(100.0 * self.completed_items / self.total_items, 1)

    @property
    def total_fab_minutes(self) -> float:
        return sum(i.duration_minutes for i in self.items if i.status == STATUS_COMPLETE)

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
            "progress_pct": self.progress_pct,
            "total_fab_minutes": round(self.total_fab_minutes, 1),
        }


# ─────────────────────────────────────────────
# WORK ORDER STORAGE
# ─────────────────────────────────────────────

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
    # Sort by created_at descending
    results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return results


def load_all_active_items(base_dir: str) -> List[dict]:
    """Load all items from active (non-complete) work orders across all projects.
    Returns flat list of item dicts with wo_id and job_code added.
    Used for shop floor dashboard machine utilization."""
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


# ─────────────────────────────────────────────
# WORK ORDER CREATION
# ─────────────────────────────────────────────

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
    n_sag_rods = n_frames * 2  # 2 per rafter
    n_sag_pieces = n_sag_rods * 2  # 2 pieces per rod
    n_sag_bundles = max(1, -(-n_sag_pieces // 10))  # ceil div by 10
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
    n_straps = n_frames * 4  # 4 per rafter
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


# ─────────────────────────────────────────────
# QR SCAN ACTIONS
# ─────────────────────────────────────────────

def qr_scan_start(base_dir: str, job_code: str, item_id: str,
                   scanned_by: str) -> dict:
    """Process a QR 'start_job' scan.

    Returns dict with status and updated item info.
    """
    wo, item = find_work_order_by_item(base_dir, job_code, item_id)
    if wo is None or item is None:
        return {"ok": False, "error": "Work order item not found"}

    if item.status == STATUS_COMPLETE:
        return {"ok": False, "error": "Item already complete",
                "item": item.to_dict()}

    if item.status == STATUS_IN_PROGRESS:
        return {"ok": False, "error": "Item already in progress",
                "started_by": item.started_by,
                "started_at": item.started_at,
                "item": item.to_dict()}

    # Must be in approved or stickers_printed state at minimum
    if wo.status not in [STATUS_APPROVED, STATUS_STICKERS_PRINTED, STATUS_IN_PROGRESS]:
        return {"ok": False, "error": f"Work order not ready (status: {wo.status})"}

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

    Calculates duration and marks item complete.
    Returns dict with status and updated item info.
    """
    wo, item = find_work_order_by_item(base_dir, job_code, item_id)
    if wo is None or item is None:
        return {"ok": False, "error": "Work order item not found"}

    if item.status == STATUS_COMPLETE:
        return {"ok": False, "error": "Item already complete",
                "item": item.to_dict()}

    if item.status != STATUS_IN_PROGRESS:
        return {"ok": False, "error": "Item not started yet — scan Start first",
                "item": item.to_dict()}

    now = datetime.datetime.now()
    item.status = STATUS_COMPLETE
    item.finished_by = scanned_by
    item.finished_at = now.isoformat()

    # Calculate duration
    try:
        start = datetime.datetime.fromisoformat(item.started_at)
        delta = now - start
        item.duration_minutes = round(delta.total_seconds() / 60.0, 1)
    except Exception:
        item.duration_minutes = 0.0

    # Check if all items are complete → mark WO complete
    if all(i.status == STATUS_COMPLETE for i in wo.items):
        wo.status = STATUS_COMPLETE
        # Create notification for WO completion
        create_notification(wo.work_order_id, wo.job_code,
                          STATUS_IN_PROGRESS, STATUS_COMPLETE, scanned_by)

    save_work_order(base_dir, wo)

    return {
        "ok": True,
        "action": "finished",
        "item": item.to_dict(),
        "work_order_id": wo.work_order_id,
        "duration_minutes": item.duration_minutes,
        "message": (f"Finished {item.ship_mark}: {item.description} "
                    f"({item.duration_minutes:.1f} min)"),
        "wo_complete": wo.status == STATUS_COMPLETE,
        "progress": wo.summary(),
    }
