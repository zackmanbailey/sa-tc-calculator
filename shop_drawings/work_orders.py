"""
TitanForge — Work Order Management System
==========================================
Handles the full lifecycle of fabrication work orders:
  1. Work order creation (from finalized shop drawings)
  2. QR scan start/finish tracking
  3. Duration calculation and fabrication metrics
  4. Status tracking (queued → approved → in_progress → complete)

Data is stored as JSON files per project in data/shop_drawings/{job_code}/work_orders/

Work order flow (from WORK_ORDER_FLOW config):
  shop_drawings_finalized → work_order_created → manual_approval →
  stickers_printed → QR start_job → QR finish_job
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

STATUS_FLOW = {
    STATUS_QUEUED: [STATUS_APPROVED, STATUS_ON_HOLD],
    STATUS_APPROVED: [STATUS_STICKERS_PRINTED, STATUS_ON_HOLD],
    STATUS_STICKERS_PRINTED: [STATUS_IN_PROGRESS],
    STATUS_IN_PROGRESS: [STATUS_COMPLETE, STATUS_ON_HOLD],
    STATUS_COMPLETE: [],
    STATUS_ON_HOLD: [STATUS_QUEUED, STATUS_APPROVED],
}

STATUS_LABELS = {
    STATUS_QUEUED: "Queued",
    STATUS_APPROVED: "Approved",
    STATUS_STICKERS_PRINTED: "Stickers Printed",
    STATUS_IN_PROGRESS: "In Progress",
    STATUS_COMPLETE: "Complete",
    STATUS_ON_HOLD: "On Hold",
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
    # ── Crew / Accountability ──
    assigned_to: str = ""          # Worker assigned to this piece
    weight_lbs: float = 0.0        # Piece weight from BOM
    length_desc: str = ""          # e.g., "21'-1 1/2\""
    # ── QC Tracking ──
    qc_status: str = "pending"     # "pending", "passed", "failed", "n/a"
    qc_inspector: str = ""         # Who inspected
    qc_inspected_at: str = ""      # ISO timestamp
    qc_notes: str = ""             # Inspector notes
    # ── Loading / Shipping ──
    loading_status: str = "not_ready"  # "not_ready", "staged", "loaded", "shipped", "delivered"
    loaded_by: str = ""            # Who loaded it
    loaded_at: str = ""            # ISO timestamp
    truck_number: str = ""         # Truck/trailer ID

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
    # ── Project Info ──
    project_name: str = ""         # e.g., "Dallas Office Park"
    customer_name: str = ""        # e.g., "Lone Star Properties"
    priority: str = "normal"       # "normal", "rush", "hot"
    due_date: str = ""             # Target completion date
    delivery_date: str = ""        # Scheduled delivery
    ship_to: str = ""              # Delivery address
    total_weight_lbs: float = 0.0  # Total weight from BOM
    total_sell: float = 0.0        # Total sell from TC
    building_specs: str = ""       # e.g., "50'x150'x16' DBL-COL"

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
            "project_name": self.project_name,
            "customer_name": self.customer_name,
            "priority": self.priority,
            "due_date": self.due_date,
            "delivery_date": self.delivery_date,
            "ship_to": self.ship_to,
            "total_weight_lbs": self.total_weight_lbs,
            "total_sell": self.total_sell,
            "building_specs": self.building_specs,
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
            "project_name": self.project_name,
            "customer_name": self.customer_name,
            "priority": self.priority,
            "due_date": self.due_date,
            "delivery_date": self.delivery_date,
            "total_weight_lbs": self.total_weight_lbs,
            "building_specs": self.building_specs,
            "qc_pending": sum(1 for i in self.items if i.qc_status == "pending" and i.status == STATUS_COMPLETE),
            "qc_passed": sum(1 for i in self.items if i.qc_status == "passed"),
            "loading_ready": sum(1 for i in self.items if i.loading_status == "staged"),
            "loading_loaded": sum(1 for i in self.items if i.loading_status == "loaded"),
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


def delete_work_order(base_dir: str, job_code: str, wo_id: str) -> bool:
    """Delete a work order from disk. Returns True if deleted."""
    d = _wo_dir(base_dir, job_code)
    path = os.path.join(d, f"{wo_id}.json")
    if os.path.isfile(path):
        os.remove(path)
        return True
    return False


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
                      drawing_files: list, config_dict: dict,
                      project_name: str = "", customer_name: str = "",
                      priority: str = "normal", due_date: str = "",
                      delivery_date: str = "", ship_to: str = "",
                      total_weight_lbs: float = 0.0, total_sell: float = 0.0,
                      building_specs: str = "") -> WorkOrder:
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

    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    wo = WorkOrder(
        work_order_id=f"WO-{job_code}-{revision}-{uuid.uuid4().hex[:6].upper()}",
        job_code=job_code,
        revision=revision,
        created_at=now,
        created_by=created_by,
        status=STATUS_QUEUED,
        project_name=project_name,
        customer_name=customer_name,
        priority=priority,
        due_date=due_date,
        delivery_date=delivery_date,
        ship_to=ship_to,
        total_weight_lbs=total_weight_lbs,
        total_sell=total_sell,
        building_specs=building_specs,
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
            drawing_ref=f"/shop-drawings/{job_code}/column",
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
            drawing_ref=f"/shop-drawings/{job_code}/rafter",
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
            drawing_ref=f"/shop-drawings/{job_code}",
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
            drawing_ref=f"/shop-drawings/{job_code}",
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
            drawing_ref=f"/shop-drawings/{job_code}",
        ))

    # ── Endcap channels ──
    wo.items.append(WorkOrderItem(
        item_id=f"{wo.work_order_id}-EC-1",
        ship_mark="EC-1",
        component_type="endcap",
        description="Endcap U-Channel (Front End)",
        quantity=1,
        machine="C1",
        drawing_ref=f"/shop-drawings/{job_code}",
    ))
    wo.items.append(WorkOrderItem(
        item_id=f"{wo.work_order_id}-EC-2",
        ship_mark="EC-2",
        component_type="endcap",
        description="Endcap U-Channel (Back End)",
        quantity=1,
        machine="C1",
        drawing_ref=f"/shop-drawings/{job_code}",
    ))

    # ── Roofing panels (one item — rolled in bulk) ──
    wo.items.append(WorkOrderItem(
        item_id=f"{wo.work_order_id}-ROOF",
        ship_mark="ROOF",
        component_type="roofing",
        description="Spartan Rib Roofing Panels — full run",
        quantity=1,
        machine="SPARTAN",
        drawing_ref=f"/shop-drawings/{job_code}",
    ))

    return wo


# ─────────────────────────────────────────────
# QR SCAN ACTIONS
# ─────────────────────────────────────────────

def _check_rafter_before_column(wo, item, action: str) -> Optional[dict]:
    """Enforce rule: all rafters must be started/finished BEFORE any column.

    Returns an error dict if the rule is violated, or None if OK.
    """
    if item.component_type.lower() != "column":
        return None  # Only columns are gated

    # Check that ALL rafters in this WO are complete (for start) or at least started
    rafters = [i for i in wo.items if i.component_type.lower() == "rafter"]
    if not rafters:
        return None  # No rafters in this WO, no constraint

    if action == "start":
        # All rafters must be complete before any column can start
        incomplete = [r for r in rafters if r.status != STATUS_COMPLETE]
        if incomplete:
            marks = ", ".join(r.ship_mark for r in incomplete)
            return {
                "ok": False,
                "error": (f"Cannot start column {item.ship_mark} — "
                          f"all rafters must be completed first. "
                          f"Incomplete rafters: {marks}"),
            }
    elif action == "finish":
        # Same rule — all rafters must be complete before column can finish
        incomplete = [r for r in rafters if r.status != STATUS_COMPLETE]
        if incomplete:
            marks = ", ".join(r.ship_mark for r in incomplete)
            return {
                "ok": False,
                "error": (f"Cannot finish column {item.ship_mark} — "
                          f"all rafters must be completed first. "
                          f"Incomplete rafters: {marks}"),
            }
    return None


def _check_rebar_inspection_before_finish(wo, item) -> Optional[dict]:
    """Enforce rule: reinforced members must have rebar inspected (QC passed)
    BEFORE the item can be finished.

    For reinforced rafters and columns, the rebar inside must be inspected
    before the two C-purlins are tack welded and stitch welded together.
    """
    # Only applies to columns and rafters (reinforced members)
    ctype = item.component_type.lower()
    if ctype not in ("column", "rafter"):
        return None

    is_reinforced = False

    # 1) Check the shop drawing config for reinforced flags
    try:
        from shop_drawings.config import ShopDrawingConfig
        base_dir = os.environ.get("TITANFORGE_DATA_DIR",
                                  os.path.join(os.path.dirname(os.path.dirname(__file__)), "data"))
        cfg_path = os.path.join(base_dir, "shop_drawings", wo.job_code, "config.json")
        if os.path.exists(cfg_path):
            with open(cfg_path) as f:
                cfg_data = json.load(f)
            if ctype == "column" and cfg_data.get("col_reinforced", True):
                is_reinforced = True
            elif ctype == "rafter" and cfg_data.get("raft_reinforced", True):
                is_reinforced = True
    except Exception:
        pass  # Fall through to text-based checks

    # 2) Check item description/notes for reinforced indicators
    if not is_reinforced:
        desc_lower = (item.description + " " + item.notes).lower()
        if "reinforced" in desc_lower or "rebar" in desc_lower:
            is_reinforced = True

    # 3) Check drawing_ref
    if not is_reinforced and item.drawing_ref:
        if "reinforced" in item.drawing_ref.lower():
            is_reinforced = True

    # 4) Check WO-level notes
    if not is_reinforced:
        wo_notes = (wo.notes or "").lower()
        if "reinforced" in wo_notes:
            is_reinforced = True

    if not is_reinforced:
        return None  # Non-reinforced member, no inspection gate

    # Reinforced member — require QC inspection passed before finish
    if item.qc_status != "passed":
        return {
            "ok": False,
            "error": (f"Cannot finish reinforced {ctype} {item.ship_mark} — "
                      f"rebar inspection required BEFORE tack welding. "
                      f"Current QC status: {item.qc_status}. "
                      f"Have a QC inspector verify rebar placement first."),
        }
    return None


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

    # ── RULE: Rafters must be completed before columns can start ──
    rafter_check = _check_rafter_before_column(wo, item, "start")
    if rafter_check is not None:
        return rafter_check

    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
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

    # ── RULE: Rafters must be completed before columns can finish ──
    rafter_check = _check_rafter_before_column(wo, item, "finish")
    if rafter_check is not None:
        return rafter_check

    # ── RULE: Reinforced members need rebar inspection before finish ──
    rebar_check = _check_rebar_inspection_before_finish(wo, item)
    if rebar_check is not None:
        return rebar_check

    now = datetime.datetime.now(datetime.timezone.utc)
    item.status = STATUS_COMPLETE
    item.finished_by = scanned_by
    item.finished_at = now.isoformat()

    # Calculate duration
    try:
        start = datetime.datetime.fromisoformat(item.started_at)
        # Handle old timestamps without timezone info — assume UTC
        if start.tzinfo is None:
            start = start.replace(tzinfo=datetime.timezone.utc)
        delta = now - start
        item.duration_minutes = round(delta.total_seconds() / 60.0, 1)
    except Exception:
        item.duration_minutes = 0.0

    # Check if all items are complete → mark WO complete
    if all(i.status == STATUS_COMPLETE for i in wo.items):
        wo.status = STATUS_COMPLETE

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


# ─────────────────────────────────────────────
# QC ACTIONS
# ─────────────────────────────────────────────

def qc_inspect_item(base_dir: str, job_code: str, item_id: str,
                     inspector: str, qc_status: str, qc_notes: str = "") -> dict:
    """Record a QC inspection on a work order item.

    Args:
        qc_status: "passed" or "failed"
    """
    wo, item = find_work_order_by_item(base_dir, job_code, item_id)
    if wo is None or item is None:
        return {"ok": False, "error": "Work order item not found"}

    # Allow QC on in_progress items (e.g., rebar inspection before tack welding)
    # and on complete items (final QC check)
    if item.status not in (STATUS_IN_PROGRESS, STATUS_COMPLETE):
        return {"ok": False, "error": "Item must be in progress or complete before QC inspection"}

    if qc_status not in ("passed", "failed"):
        return {"ok": False, "error": "qc_status must be 'passed' or 'failed'"}

    item.qc_status = qc_status
    item.qc_inspector = inspector
    item.qc_inspected_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    item.qc_notes = qc_notes

    save_work_order(base_dir, wo)

    return {
        "ok": True,
        "item": item.to_dict(),
        "message": f"QC {qc_status.upper()} for {item.ship_mark} by {inspector}",
    }


# ─────────────────────────────────────────────
# LOADING / SHIPPING ACTIONS
# ─────────────────────────────────────────────

LOADING_FLOW = {
    "not_ready": ["staged"],
    "staged": ["loaded", "not_ready"],
    "loaded": ["shipped"],
    "shipped": ["delivered"],
    "delivered": [],
}

LOADING_LABELS = {
    "not_ready": "Not Ready",
    "staged": "Staged",
    "loaded": "Loaded",
    "shipped": "Shipped",
    "delivered": "Delivered",
}


def update_loading_status(base_dir: str, job_code: str, item_id: str,
                           new_status: str, updated_by: str,
                           truck_number: str = "") -> dict:
    """Update the loading/shipping status of a work order item."""
    wo, item = find_work_order_by_item(base_dir, job_code, item_id)
    if wo is None or item is None:
        return {"ok": False, "error": "Work order item not found"}

    if new_status not in LOADING_FLOW:
        return {"ok": False, "error": f"Invalid loading status: {new_status}"}

    allowed = LOADING_FLOW.get(item.loading_status, [])
    if new_status not in allowed:
        return {"ok": False,
                "error": f"Cannot go from '{item.loading_status}' to '{new_status}'. Allowed: {allowed}"}

    item.loading_status = new_status
    if new_status == "loaded":
        item.loaded_by = updated_by
        item.loaded_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        if truck_number:
            item.truck_number = truck_number

    save_work_order(base_dir, wo)

    return {
        "ok": True,
        "item": item.to_dict(),
        "message": f"{item.ship_mark} → {LOADING_LABELS.get(new_status, new_status)}",
    }
