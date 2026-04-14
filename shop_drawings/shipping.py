"""
TitanForge v4 — Shipping & Load Management
=============================================
Data model, storage, and business logic for:
  - Load building (grouping QC-approved items into truck loads)
  - Shipping manifest / BOL generation
  - Delivery tracking
  - Installation confirmation
"""

import os
import json
import datetime
import secrets
from dataclasses import dataclass, field
from typing import List, Optional, Dict

from shop_drawings.work_orders import (
    WorkOrder, WorkOrderItem,
    STATUS_QC_APPROVED, STATUS_READY_TO_SHIP, STATUS_SHIPPED,
    STATUS_DELIVERED, STATUS_INSTALLED,
    load_work_order, save_work_order,
    transition_item_status,
    PHASE_SHIPPING,
)


# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────

LOAD_STATUS_BUILDING = "building"       # Load is being assembled
LOAD_STATUS_READY = "ready"             # All items staged, ready to ship
LOAD_STATUS_IN_TRANSIT = "in_transit"   # On the truck
LOAD_STATUS_DELIVERED = "delivered"     # Arrived at site
LOAD_STATUS_COMPLETE = "complete"       # All items confirmed installed

LOAD_STATUSES = [
    LOAD_STATUS_BUILDING, LOAD_STATUS_READY, LOAD_STATUS_IN_TRANSIT,
    LOAD_STATUS_DELIVERED, LOAD_STATUS_COMPLETE,
]

LOAD_STATUS_LABELS = {
    LOAD_STATUS_BUILDING: "Building",
    LOAD_STATUS_READY: "Ready to Ship",
    LOAD_STATUS_IN_TRANSIT: "In Transit",
    LOAD_STATUS_DELIVERED: "Delivered",
    LOAD_STATUS_COMPLETE: "Complete",
}

LOAD_STATUS_COLORS = {
    LOAD_STATUS_BUILDING: "amber",
    LOAD_STATUS_READY: "blue",
    LOAD_STATUS_IN_TRANSIT: "purple",
    LOAD_STATUS_DELIVERED: "green",
    LOAD_STATUS_COMPLETE: "green",
}

LOAD_FLOW = {
    LOAD_STATUS_BUILDING:   [LOAD_STATUS_READY],
    LOAD_STATUS_READY:      [LOAD_STATUS_IN_TRANSIT],
    LOAD_STATUS_IN_TRANSIT: [LOAD_STATUS_DELIVERED],
    LOAD_STATUS_DELIVERED:  [LOAD_STATUS_COMPLETE],
    LOAD_STATUS_COMPLETE:   [],
}


# ─────────────────────────────────────────────
# DATA MODEL
# ─────────────────────────────────────────────

@dataclass
class LoadItem:
    """An item on a shipping load (references a WO item)."""
    job_code: str = ""
    wo_id: str = ""
    item_id: str = ""
    ship_mark: str = ""
    description: str = ""
    quantity: int = 1
    weight_lbs: float = 0.0
    length_ft: float = 0.0
    bundle_tag: str = ""         # Bundle/group tag for field sorting

    def to_dict(self) -> dict:
        return {
            "job_code": self.job_code,
            "wo_id": self.wo_id,
            "item_id": self.item_id,
            "ship_mark": self.ship_mark,
            "description": self.description,
            "quantity": self.quantity,
            "weight_lbs": self.weight_lbs,
            "length_ft": self.length_ft,
            "bundle_tag": self.bundle_tag,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "LoadItem":
        li = cls()
        for k, v in d.items():
            if hasattr(li, k):
                setattr(li, k, v)
        return li


@dataclass
class ShippingLoad:
    """A truck load containing items from one or more work orders/projects."""
    load_id: str = ""
    load_number: int = 0
    status: str = LOAD_STATUS_BUILDING

    # Destination
    job_code: str = ""               # Primary project (can be multi-project)
    destination: str = ""            # Delivery address
    site_contact: str = ""           # Who to call on arrival
    site_phone: str = ""

    # Truck
    carrier: str = ""                # Trucking company or "Self"
    truck_number: str = ""
    trailer_type: str = ""           # flatbed, step_deck, lowboy, van, etc.
    driver_name: str = ""
    driver_phone: str = ""

    # Items
    items: List[LoadItem] = field(default_factory=list)

    # BOL
    bol_number: str = ""
    bol_generated: bool = False
    bol_generated_at: str = ""
    bol_generated_by: str = ""

    # Timestamps
    created_at: str = ""
    created_by: str = ""
    shipped_at: str = ""
    shipped_by: str = ""
    delivered_at: str = ""
    delivered_by: str = ""            # Field crew who confirmed
    delivery_notes: str = ""
    delivery_photos: list = field(default_factory=list)
    completed_at: str = ""

    # Notes
    notes: str = ""
    special_instructions: str = ""    # Crane needed, unload instructions, etc.

    def to_dict(self) -> dict:
        return {
            "load_id": self.load_id,
            "load_number": self.load_number,
            "status": self.status,
            "job_code": self.job_code,
            "destination": self.destination,
            "site_contact": self.site_contact,
            "site_phone": self.site_phone,
            "carrier": self.carrier,
            "truck_number": self.truck_number,
            "trailer_type": self.trailer_type,
            "driver_name": self.driver_name,
            "driver_phone": self.driver_phone,
            "items": [i.to_dict() for i in self.items],
            "bol_number": self.bol_number,
            "bol_generated": self.bol_generated,
            "bol_generated_at": self.bol_generated_at,
            "bol_generated_by": self.bol_generated_by,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "shipped_at": self.shipped_at,
            "shipped_by": self.shipped_by,
            "delivered_at": self.delivered_at,
            "delivered_by": self.delivered_by,
            "delivery_notes": self.delivery_notes,
            "delivery_photos": self.delivery_photos,
            "completed_at": self.completed_at,
            "notes": self.notes,
            "special_instructions": self.special_instructions,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ShippingLoad":
        load = cls()
        for k, v in d.items():
            if k == "items":
                load.items = [LoadItem.from_dict(i) for i in v]
            elif hasattr(load, k):
                setattr(load, k, v)
        return load

    # ── Computed properties ──

    @property
    def total_items(self) -> int:
        return len(self.items)

    @property
    def total_weight(self) -> float:
        return sum(i.weight_lbs for i in self.items)

    @property
    def total_pieces(self) -> int:
        return sum(i.quantity for i in self.items)

    @property
    def status_label(self) -> str:
        return LOAD_STATUS_LABELS.get(self.status, self.status)

    @property
    def status_color(self) -> str:
        return LOAD_STATUS_COLORS.get(self.status, "gray")

    @property
    def job_codes(self) -> List[str]:
        """All unique job codes on this load."""
        return list(set(i.job_code for i in self.items if i.job_code))

    def can_transition_to(self, new_status: str) -> bool:
        return new_status in LOAD_FLOW.get(self.status, [])

    def summary(self) -> dict:
        return {
            "load_id": self.load_id,
            "load_number": self.load_number,
            "status": self.status,
            "status_label": self.status_label,
            "job_code": self.job_code,
            "destination": self.destination,
            "total_items": self.total_items,
            "total_weight": self.total_weight,
            "total_pieces": self.total_pieces,
            "carrier": self.carrier,
            "created_at": self.created_at,
            "shipped_at": self.shipped_at,
            "delivered_at": self.delivered_at,
        }


# ─────────────────────────────────────────────
# STORAGE
# ─────────────────────────────────────────────

def _loads_dir(base_dir: str) -> str:
    d = os.path.join(base_dir, "data", "shipping")
    os.makedirs(d, exist_ok=True)
    return d


def save_load(base_dir: str, load: ShippingLoad):
    """Save a shipping load to disk."""
    d = _loads_dir(base_dir)
    path = os.path.join(d, f"{load.load_id}.json")
    with open(path, "w") as f:
        json.dump(load.to_dict(), f, indent=2)


def load_shipping_load(base_dir: str, load_id: str) -> Optional[ShippingLoad]:
    """Load a specific shipping load."""
    d = _loads_dir(base_dir)
    path = os.path.join(d, f"{load_id}.json")
    if not os.path.isfile(path):
        return None
    with open(path) as f:
        data = json.load(f)
    return ShippingLoad.from_dict(data)


def list_loads(base_dir: str, status: str = "", job_code: str = "") -> List[ShippingLoad]:
    """List all shipping loads, optionally filtered by status or job code."""
    d = _loads_dir(base_dir)
    loads = []
    for fname in os.listdir(d):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(d, fname)
        try:
            with open(path) as f:
                data = json.load(f)
            sl = ShippingLoad.from_dict(data)
            if status and sl.status != status:
                continue
            if job_code and sl.job_code != job_code and job_code not in sl.job_codes:
                continue
            loads.append(sl)
        except Exception:
            continue
    loads.sort(key=lambda x: x.created_at or "", reverse=True)
    return loads


def next_load_number(base_dir: str) -> int:
    """Get the next sequential load number."""
    loads = list_loads(base_dir)
    if not loads:
        return 1
    return max(sl.load_number for sl in loads) + 1


# ─────────────────────────────────────────────
# BUSINESS LOGIC
# ─────────────────────────────────────────────

def create_load(base_dir: str, job_code: str, created_by: str,
                destination: str = "", carrier: str = "",
                notes: str = "", special_instructions: str = "") -> ShippingLoad:
    """Create a new shipping load."""
    now = datetime.datetime.now()
    load_num = next_load_number(base_dir)
    load = ShippingLoad(
        load_id=f"LOAD-{now.strftime('%Y%m%d')}-{load_num:03d}",
        load_number=load_num,
        status=LOAD_STATUS_BUILDING,
        job_code=job_code,
        destination=destination,
        carrier=carrier,
        notes=notes,
        special_instructions=special_instructions,
        created_at=now.isoformat(),
        created_by=created_by,
    )
    save_load(base_dir, load)
    return load


def add_items_to_load(base_dir: str, wo_base_dir: str, load_id: str,
                      items: List[dict], added_by: str) -> dict:
    """Add work order items to a load.
    items: list of {"job_code": str, "item_id": str, "weight_lbs": float, "length_ft": float, "bundle_tag": str}
    Returns {"ok": bool, "added": int, "errors": list}
    """
    load = load_shipping_load(base_dir, load_id)
    if not load:
        return {"ok": False, "error": "Load not found"}
    if load.status != LOAD_STATUS_BUILDING:
        return {"ok": False, "error": f"Cannot add items to load in '{load.status_label}' status"}

    added = 0
    errors = []
    existing_item_ids = {i.item_id for i in load.items}

    for item_spec in items:
        job_code = item_spec.get("job_code", load.job_code)
        item_id = item_spec.get("item_id", "")

        if item_id in existing_item_ids:
            errors.append(f"{item_id}: already on this load")
            continue

        # Find the WO item
        wo, wo_item = _find_wo_item(wo_base_dir, job_code, item_id)
        if not wo or not wo_item:
            errors.append(f"{item_id}: not found in project {job_code}")
            continue

        # Must be qc_approved or ready_to_ship
        if wo_item.status not in [STATUS_QC_APPROVED, STATUS_READY_TO_SHIP]:
            errors.append(f"{item_id}: status is '{wo_item.status}', must be qc_approved or ready_to_ship")
            continue

        # Transition to ready_to_ship if still qc_approved
        if wo_item.status == STATUS_QC_APPROVED:
            result = transition_item_status(wo_base_dir, job_code, item_id,
                                            STATUS_READY_TO_SHIP, added_by,
                                            notes=f"Added to load {load_id}")
            if not result.get("ok"):
                errors.append(f"{item_id}: transition failed — {result.get('error', 'unknown')}")
                continue

        # Set load_id on the WO item
        wo = _reload_wo_for_item(wo_base_dir, job_code, item_id)
        if wo:
            for i in wo.items:
                if i.item_id == item_id:
                    i.load_id = load_id
                    break
            save_work_order(wo_base_dir, wo)

        load_item = LoadItem(
            job_code=job_code,
            wo_id=wo.work_order_id if wo else "",
            item_id=item_id,
            ship_mark=wo_item.ship_mark,
            description=wo_item.description,
            quantity=wo_item.quantity,
            weight_lbs=item_spec.get("weight_lbs", 0.0),
            length_ft=item_spec.get("length_ft", 0.0),
            bundle_tag=item_spec.get("bundle_tag", ""),
        )
        load.items.append(load_item)
        existing_item_ids.add(item_id)
        added += 1

    save_load(base_dir, load)
    return {"ok": True, "added": added, "errors": errors, "load": load.to_dict()}


def remove_item_from_load(base_dir: str, wo_base_dir: str, load_id: str,
                          item_id: str, removed_by: str) -> dict:
    """Remove an item from a load (only while building)."""
    load = load_shipping_load(base_dir, load_id)
    if not load:
        return {"ok": False, "error": "Load not found"}
    if load.status != LOAD_STATUS_BUILDING:
        return {"ok": False, "error": "Cannot remove items from a shipped/in-transit load"}

    found = False
    job_code = ""
    for i, li in enumerate(load.items):
        if li.item_id == item_id:
            job_code = li.job_code
            load.items.pop(i)
            found = True
            break

    if not found:
        return {"ok": False, "error": f"Item {item_id} not on this load"}

    # Clear load_id from WO item
    if job_code:
        wo = _reload_wo_for_item(wo_base_dir, job_code, item_id)
        if wo:
            for it in wo.items:
                if it.item_id == item_id:
                    it.load_id = ""
                    break
            save_work_order(wo_base_dir, wo)

    save_load(base_dir, load)
    return {"ok": True, "load": load.to_dict()}


def transition_load_status(base_dir: str, wo_base_dir: str, load_id: str,
                           new_status: str, changed_by: str,
                           notes: str = "") -> dict:
    """Move a load through its lifecycle. Also transitions WO items."""
    load = load_shipping_load(base_dir, load_id)
    if not load:
        return {"ok": False, "error": "Load not found"}

    if not load.can_transition_to(new_status):
        allowed = LOAD_FLOW.get(load.status, [])
        return {"ok": False, "error": f"Cannot transition from '{load.status}' to '{new_status}'. Allowed: {allowed}"}

    if new_status == LOAD_STATUS_READY and len(load.items) == 0:
        return {"ok": False, "error": "Cannot mark empty load as ready"}

    now = datetime.datetime.now().isoformat()
    old_status = load.status
    load.status = new_status

    # Status-specific updates
    item_target_status = None

    if new_status == LOAD_STATUS_IN_TRANSIT:
        load.shipped_at = now
        load.shipped_by = changed_by
        item_target_status = STATUS_SHIPPED

    elif new_status == LOAD_STATUS_DELIVERED:
        load.delivered_at = now
        load.delivered_by = changed_by
        if notes:
            load.delivery_notes = notes
        item_target_status = STATUS_DELIVERED

    elif new_status == LOAD_STATUS_COMPLETE:
        load.completed_at = now
        item_target_status = STATUS_INSTALLED

    # Transition all WO items on this load
    item_results = []
    if item_target_status:
        for li in load.items:
            result = transition_item_status(
                wo_base_dir, li.job_code, li.item_id,
                item_target_status, changed_by,
                notes=f"Load {load_id}: {LOAD_STATUS_LABELS.get(new_status, new_status)}")
            item_results.append({"item_id": li.item_id, "result": result})

    if notes:
        load.notes = f"[{LOAD_STATUS_LABELS.get(new_status, new_status)}] {notes}\n" + load.notes

    save_load(base_dir, load)

    return {
        "ok": True,
        "old_status": old_status,
        "new_status": new_status,
        "load": load.summary(),
        "item_transitions": item_results,
    }


def generate_bol(base_dir: str, load_id: str, generated_by: str) -> dict:
    """Generate a BOL number for a load."""
    load = load_shipping_load(base_dir, load_id)
    if not load:
        return {"ok": False, "error": "Load not found"}
    if load.status == LOAD_STATUS_BUILDING and len(load.items) == 0:
        return {"ok": False, "error": "Cannot generate BOL for empty load"}

    now = datetime.datetime.now()
    load.bol_number = f"BOL-{now.strftime('%Y%m%d')}-{load.load_number:03d}"
    load.bol_generated = True
    load.bol_generated_at = now.isoformat()
    load.bol_generated_by = generated_by
    save_load(base_dir, load)

    return {"ok": True, "bol_number": load.bol_number, "load": load.to_dict()}


def get_shippable_items(wo_base_dir: str, job_code: str = "") -> List[dict]:
    """Get all WO items that are ready to be added to a load (qc_approved or ready_to_ship)."""
    results = []
    if not os.path.isdir(wo_base_dir):
        return results

    projects = [job_code] if job_code else os.listdir(wo_base_dir)
    for proj in projects:
        wo_dir = os.path.join(wo_base_dir, proj, "work_orders")
        if not os.path.isdir(wo_dir):
            continue
        for wo_file in os.listdir(wo_dir):
            if not wo_file.endswith(".json"):
                continue
            wo = load_work_order(wo_base_dir, proj, wo_file.replace(".json", ""))
            if not wo:
                continue
            for item in wo.items:
                if item.status in [STATUS_QC_APPROVED, STATUS_READY_TO_SHIP] and not item.load_id:
                    results.append({
                        "job_code": proj,
                        "wo_id": wo.work_order_id,
                        "item_id": item.item_id,
                        "ship_mark": item.ship_mark,
                        "description": item.description,
                        "quantity": item.quantity,
                        "machine": item.machine,
                        "status": item.status,
                        "qc_result": item.qc_result,
                    })

    results.sort(key=lambda x: (x["job_code"], x["ship_mark"]))
    return results


def get_shipping_summary(base_dir: str) -> dict:
    """Get summary metrics for the shipping dashboard."""
    loads = list_loads(base_dir)
    summary = {
        "total_loads": len(loads),
        "building": 0,
        "ready": 0,
        "in_transit": 0,
        "delivered": 0,
        "complete": 0,
        "total_items_shipped": 0,
        "total_weight_shipped": 0,
        "recent_loads": [],
    }

    for sl in loads:
        if sl.status in summary:
            summary[sl.status] += 1
        if sl.status in [LOAD_STATUS_IN_TRANSIT, LOAD_STATUS_DELIVERED, LOAD_STATUS_COMPLETE]:
            summary["total_items_shipped"] += sl.total_items
            summary["total_weight_shipped"] += sl.total_weight
        summary["recent_loads"].append(sl.summary())

    summary["recent_loads"] = summary["recent_loads"][:20]
    return summary


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

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


def _reload_wo_for_item(wo_base_dir: str, job_code: str, item_id: str):
    """Reload the WO containing a specific item (fresh from disk)."""
    wo, _ = _find_wo_item(wo_base_dir, job_code, item_id)
    return wo
