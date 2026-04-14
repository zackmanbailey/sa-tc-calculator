"""
TitanForge Phase 11 — Inventory Management Engine
===================================================
Coil inventory tracking, receiving, allocation, mill cert management,
low-stock alerts, and inventory analytics.

Works alongside the existing inventory.json storage in tf_handlers.py
but adds structured operations, history tracking, and analytics.
"""

from __future__ import annotations
import os, json, datetime, uuid
from dataclasses import dataclass, field as dc_field
from typing import List, Dict, Optional, Any


# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

COIL_STATUSES = ["active", "low_stock", "depleted", "on_order", "quarantine"]
COIL_STATUS_LABELS = {
    "active": "Active", "low_stock": "Low Stock", "depleted": "Depleted",
    "on_order": "On Order", "quarantine": "Quarantine",
}

TRANSACTION_TYPES = ["receive", "allocate", "consume", "adjust", "return", "transfer"]
TRANSACTION_TYPE_LABELS = {
    "receive": "Received", "allocate": "Allocated", "consume": "Consumed",
    "adjust": "Adjustment", "return": "Returned", "transfer": "Transfer",
}

MATERIAL_GRADES = [
    "A36", "A572 Gr 50", "A992", "A500 Gr B", "A500 Gr C",
    "A513", "A1011", "A653", "Galvalume", "Galvanized",
]

COIL_GAUGES = [
    "26GA", "24GA", "22GA", "20GA", "18GA", "16GA", "14GA",
    "12GA", "11GA", "10GA", "3/16", "1/4", "5/16", "3/8",
]

ALERT_LEVELS = ["info", "warning", "critical"]


# ─────────────────────────────────────────────────────────────────────────────
# DATACLASSES
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class InventoryTransaction:
    """A single stock movement event."""
    transaction_id: str = ""
    coil_id: str = ""
    transaction_type: str = "receive"  # one of TRANSACTION_TYPES
    quantity_lbs: float = 0.0
    job_code: str = ""
    work_order_ref: str = ""
    reference: str = ""               # PO number, BOL, etc.
    notes: str = ""
    created_by: str = ""
    created_at: str = ""
    # balance after transaction
    balance_after: float = 0.0

    def __post_init__(self):
        if not self.transaction_id:
            self.transaction_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
        if not self.created_at:
            self.created_at = datetime.datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "transaction_id": self.transaction_id,
            "coil_id": self.coil_id,
            "transaction_type": self.transaction_type,
            "quantity_lbs": self.quantity_lbs,
            "job_code": self.job_code,
            "work_order_ref": self.work_order_ref,
            "reference": self.reference,
            "notes": self.notes,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "balance_after": self.balance_after,
            "type_label": TRANSACTION_TYPE_LABELS.get(self.transaction_type, self.transaction_type),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "InventoryTransaction":
        return cls(
            transaction_id=d.get("transaction_id", ""),
            coil_id=d.get("coil_id", ""),
            transaction_type=d.get("transaction_type", "receive"),
            quantity_lbs=d.get("quantity_lbs", 0.0),
            job_code=d.get("job_code", ""),
            work_order_ref=d.get("work_order_ref", ""),
            reference=d.get("reference", ""),
            notes=d.get("notes", ""),
            created_by=d.get("created_by", ""),
            created_at=d.get("created_at", ""),
            balance_after=d.get("balance_after", 0.0),
        )


@dataclass
class StockAlert:
    """A low-stock or other inventory alert."""
    alert_id: str = ""
    coil_id: str = ""
    alert_level: str = "warning"  # info, warning, critical
    alert_type: str = ""          # low_stock, depleted, expiring_cert, etc.
    message: str = ""
    acknowledged: bool = False
    acknowledged_by: str = ""
    acknowledged_at: str = ""
    created_at: str = ""

    def __post_init__(self):
        if not self.alert_id:
            self.alert_id = f"ALT-{uuid.uuid4().hex[:8].upper()}"
        if not self.created_at:
            self.created_at = datetime.datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "alert_id": self.alert_id,
            "coil_id": self.coil_id,
            "alert_level": self.alert_level,
            "alert_type": self.alert_type,
            "message": self.message,
            "acknowledged": self.acknowledged,
            "acknowledged_by": self.acknowledged_by,
            "acknowledged_at": self.acknowledged_at,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "StockAlert":
        return cls(
            alert_id=d.get("alert_id", ""),
            coil_id=d.get("coil_id", ""),
            alert_level=d.get("alert_level", "warning"),
            alert_type=d.get("alert_type", ""),
            message=d.get("message", ""),
            acknowledged=d.get("acknowledged", False),
            acknowledged_by=d.get("acknowledged_by", ""),
            acknowledged_at=d.get("acknowledged_at", ""),
            created_at=d.get("created_at", ""),
        )


@dataclass
class Allocation:
    """Stock allocated to a specific job/work order."""
    allocation_id: str = ""
    coil_id: str = ""
    job_code: str = ""
    work_order_ref: str = ""
    quantity_lbs: float = 0.0
    consumed_lbs: float = 0.0
    status: str = "active"        # active, consumed, released
    notes: str = ""
    created_by: str = ""
    created_at: str = ""

    def __post_init__(self):
        if not self.allocation_id:
            self.allocation_id = f"ALC-{uuid.uuid4().hex[:8].upper()}"
        if not self.created_at:
            self.created_at = datetime.datetime.now().isoformat()

    @property
    def remaining_lbs(self) -> float:
        return max(0, self.quantity_lbs - self.consumed_lbs)

    def to_dict(self) -> dict:
        return {
            "allocation_id": self.allocation_id,
            "coil_id": self.coil_id,
            "job_code": self.job_code,
            "work_order_ref": self.work_order_ref,
            "quantity_lbs": self.quantity_lbs,
            "consumed_lbs": self.consumed_lbs,
            "remaining_lbs": self.remaining_lbs,
            "status": self.status,
            "notes": self.notes,
            "created_by": self.created_by,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Allocation":
        return cls(
            allocation_id=d.get("allocation_id", ""),
            coil_id=d.get("coil_id", ""),
            job_code=d.get("job_code", ""),
            work_order_ref=d.get("work_order_ref", ""),
            quantity_lbs=d.get("quantity_lbs", 0.0),
            consumed_lbs=d.get("consumed_lbs", 0.0),
            status=d.get("status", "active"),
            notes=d.get("notes", ""),
            created_by=d.get("created_by", ""),
            created_at=d.get("created_at", ""),
        )


@dataclass
class ReceivingRecord:
    """Record of material received into inventory."""
    receiving_id: str = ""
    coil_id: str = ""
    po_number: str = ""
    bol_number: str = ""
    supplier: str = ""
    quantity_lbs: float = 0.0
    heat_number: str = ""
    mill_cert_attached: bool = False
    condition_notes: str = ""
    received_by: str = ""
    received_at: str = ""

    def __post_init__(self):
        if not self.receiving_id:
            self.receiving_id = f"RCV-{uuid.uuid4().hex[:8].upper()}"
        if not self.received_at:
            self.received_at = datetime.datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "receiving_id": self.receiving_id,
            "coil_id": self.coil_id,
            "po_number": self.po_number,
            "bol_number": self.bol_number,
            "supplier": self.supplier,
            "quantity_lbs": self.quantity_lbs,
            "heat_number": self.heat_number,
            "mill_cert_attached": self.mill_cert_attached,
            "condition_notes": self.condition_notes,
            "received_by": self.received_by,
            "received_at": self.received_at,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ReceivingRecord":
        return cls(
            receiving_id=d.get("receiving_id", ""),
            coil_id=d.get("coil_id", ""),
            po_number=d.get("po_number", ""),
            bol_number=d.get("bol_number", ""),
            supplier=d.get("supplier", ""),
            quantity_lbs=d.get("quantity_lbs", 0.0),
            heat_number=d.get("heat_number", ""),
            mill_cert_attached=d.get("mill_cert_attached", False),
            condition_notes=d.get("condition_notes", ""),
            received_by=d.get("received_by", ""),
            received_at=d.get("received_at", ""),
        )


# ─────────────────────────────────────────────────────────────────────────────
# STORAGE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _inv_dir(base_dir: str) -> str:
    d = os.path.join(base_dir, "inventory_mgmt")
    os.makedirs(d, exist_ok=True)
    return d


def _load_json(path: str) -> Any:
    if os.path.isfile(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}


def _save_json(path: str, data: Any):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _load_transactions(base_dir: str) -> list:
    d = _load_json(os.path.join(_inv_dir(base_dir), "transactions.json"))
    return d.get("transactions", [])


def _save_transactions(base_dir: str, txns: list):
    _save_json(os.path.join(_inv_dir(base_dir), "transactions.json"),
               {"transactions": txns})


def _load_allocations(base_dir: str) -> list:
    d = _load_json(os.path.join(_inv_dir(base_dir), "allocations.json"))
    return d.get("allocations", [])


def _save_allocations(base_dir: str, allocs: list):
    _save_json(os.path.join(_inv_dir(base_dir), "allocations.json"),
               {"allocations": allocs})


def _load_alerts(base_dir: str) -> list:
    d = _load_json(os.path.join(_inv_dir(base_dir), "alerts.json"))
    return d.get("alerts", [])


def _save_alerts(base_dir: str, alerts: list):
    _save_json(os.path.join(_inv_dir(base_dir), "alerts.json"),
               {"alerts": alerts})


def _load_receiving(base_dir: str) -> list:
    d = _load_json(os.path.join(_inv_dir(base_dir), "receiving.json"))
    return d.get("records", [])


def _save_receiving(base_dir: str, records: list):
    _save_json(os.path.join(_inv_dir(base_dir), "receiving.json"),
               {"records": records})


def _load_inventory_main(base_dir: str) -> dict:
    """Load the main inventory.json (coils + mill_certs)."""
    path = os.path.join(base_dir, "inventory.json")
    if os.path.isfile(path):
        with open(path, "r") as f:
            return json.load(f)
    return {"coils": {}, "mill_certs": []}


def _save_inventory_main(base_dir: str, data: dict):
    path = os.path.join(base_dir, "inventory.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# ─────────────────────────────────────────────────────────────────────────────
# COIL CRUD
# ─────────────────────────────────────────────────────────────────────────────

def create_coil(base_dir: str, coil_id: str, name: str, gauge: str, grade: str,
                supplier: str = "", weight_lbs: float = 0, width_in: float = 0,
                stock_lbs: float = 0, price_per_lb: float = 0,
                min_order_lbs: float = 5000, lead_time_weeks: int = 8,
                lbs_per_lft: float = 0, heat_num: str = "",
                created_by: str = "") -> dict:
    """Create a new coil entry in inventory."""
    inv = _load_inventory_main(base_dir)
    coils = inv.get("coils", {})

    if coil_id in coils:
        raise ValueError(f"Coil '{coil_id}' already exists")

    now = datetime.datetime.now().isoformat()
    coil = {
        "name": name,
        "gauge": gauge,
        "grade": grade,
        "supplier": supplier,
        "weight_lbs": weight_lbs,
        "width_in": width_in,
        "stock_lbs": stock_lbs,
        "stock_lft": round(stock_lbs / lbs_per_lft, 1) if lbs_per_lft > 0 else 0,
        "committed_lbs": 0,
        "min_order_lbs": min_order_lbs,
        "lead_time_weeks": lead_time_weeks,
        "price_per_lb": price_per_lb,
        "lbs_per_lft": lbs_per_lft,
        "coil_max_lbs": weight_lbs or 8000,
        "received_date": now[:10],
        "heat_num": heat_num,
        "sticker_printed": False,
        "status": "active",
        "orders": [],
        "created_by": created_by,
        "created_at": now,
    }

    coils[coil_id] = coil
    inv["coils"] = coils
    _save_inventory_main(base_dir, inv)

    # Log receiving transaction if stock_lbs > 0
    if stock_lbs > 0:
        _log_transaction(base_dir, coil_id, "receive", stock_lbs,
                         notes=f"Initial stock for new coil {coil_id}",
                         created_by=created_by, balance_after=stock_lbs)

    # Check for low-stock alerts on newly created coil
    _check_alerts(base_dir, coil_id, coil)

    return coil


def get_coil(base_dir: str, coil_id: str) -> Optional[dict]:
    """Get a single coil by ID."""
    inv = _load_inventory_main(base_dir)
    coil = inv.get("coils", {}).get(coil_id)
    if coil:
        coil["coil_id"] = coil_id
        coil["status"] = _compute_coil_status(coil)
    return coil


def list_coils(base_dir: str, gauge: str = "", grade: str = "",
               supplier: str = "", status: str = "",
               low_stock_only: bool = False) -> list:
    """List coils with optional filters."""
    inv = _load_inventory_main(base_dir)
    coils = inv.get("coils", {})
    result = []

    for cid, coil in coils.items():
        coil["coil_id"] = cid
        coil["status"] = _compute_coil_status(coil)

        if gauge and coil.get("gauge", "") != gauge:
            continue
        if grade and coil.get("grade", "") != grade:
            continue
        if supplier and supplier.lower() not in coil.get("supplier", "").lower():
            continue
        if status and coil.get("status") != status:
            continue
        if low_stock_only:
            stock = coil.get("stock_lbs", 0)
            min_order = coil.get("min_order_lbs", 5000)
            if stock >= min_order:
                continue

        result.append(coil)

    result.sort(key=lambda c: c.get("name", ""))
    return result


def update_coil(base_dir: str, coil_id: str, **kwargs) -> dict:
    """Update coil fields."""
    inv = _load_inventory_main(base_dir)
    coils = inv.get("coils", {})

    if coil_id not in coils:
        raise ValueError(f"Coil '{coil_id}' not found")

    coil = coils[coil_id]
    allowed = {"name", "gauge", "grade", "supplier", "width_in",
               "price_per_lb", "min_order_lbs", "lead_time_weeks",
               "lbs_per_lft", "heat_num", "status"}
    for k, v in kwargs.items():
        if k in allowed:
            coil[k] = v

    coils[coil_id] = coil
    inv["coils"] = coils
    _save_inventory_main(base_dir, inv)
    coil["coil_id"] = coil_id
    return coil


def delete_coil(base_dir: str, coil_id: str) -> bool:
    """Delete a coil from inventory."""
    inv = _load_inventory_main(base_dir)
    coils = inv.get("coils", {})
    if coil_id not in coils:
        return False

    del coils[coil_id]
    # Also remove associated mill certs
    inv["mill_certs"] = [c for c in inv.get("mill_certs", [])
                         if c.get("coil_id") != coil_id]
    inv["coils"] = coils
    _save_inventory_main(base_dir, inv)
    return True


def _compute_coil_status(coil: dict) -> str:
    """Compute status based on stock levels."""
    stock = coil.get("stock_lbs", 0)
    min_order = coil.get("min_order_lbs", 5000)
    explicit = coil.get("status", "")
    if explicit == "quarantine":
        return "quarantine"
    if explicit == "on_order":
        return "on_order"
    if stock <= 0:
        return "depleted"
    if stock < min_order:
        return "low_stock"
    return "active"


# ─────────────────────────────────────────────────────────────────────────────
# TRANSACTIONS (stock movements)
# ─────────────────────────────────────────────────────────────────────────────

def _log_transaction(base_dir: str, coil_id: str, txn_type: str,
                     quantity_lbs: float, job_code: str = "",
                     work_order_ref: str = "", reference: str = "",
                     notes: str = "", created_by: str = "",
                     balance_after: float = 0.0) -> InventoryTransaction:
    """Log a stock movement transaction."""
    txn = InventoryTransaction(
        coil_id=coil_id,
        transaction_type=txn_type,
        quantity_lbs=quantity_lbs,
        job_code=job_code,
        work_order_ref=work_order_ref,
        reference=reference,
        notes=notes,
        created_by=created_by,
        balance_after=balance_after,
    )
    txns = _load_transactions(base_dir)
    txns.append(txn.to_dict())
    _save_transactions(base_dir, txns)
    return txn


def receive_stock(base_dir: str, coil_id: str, quantity_lbs: float,
                  po_number: str = "", bol_number: str = "",
                  supplier: str = "", heat_number: str = "",
                  condition_notes: str = "", received_by: str = "") -> dict:
    """Receive stock into a coil. Updates stock_lbs and logs transaction."""
    inv = _load_inventory_main(base_dir)
    coils = inv.get("coils", {})

    if coil_id not in coils:
        raise ValueError(f"Coil '{coil_id}' not found")
    if quantity_lbs <= 0:
        raise ValueError("Quantity must be positive")

    coil = coils[coil_id]
    old_stock = coil.get("stock_lbs", 0)
    new_stock = old_stock + quantity_lbs
    coil["stock_lbs"] = new_stock

    # Recalculate linear feet if conversion factor exists
    lbs_per_lft = coil.get("lbs_per_lft", 0)
    if lbs_per_lft > 0:
        coil["stock_lft"] = round(new_stock / lbs_per_lft, 1)

    # Update received_date
    coil["received_date"] = datetime.datetime.now().strftime("%Y-%m-%d")

    # Append to order history
    coil.setdefault("orders", []).append({
        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "lbs_added": quantity_lbs,
        "po_number": po_number,
        "bol_number": bol_number,
    })

    if heat_number:
        coil["heat_num"] = heat_number

    coils[coil_id] = coil
    inv["coils"] = coils
    _save_inventory_main(base_dir, inv)

    # Log transaction
    _log_transaction(base_dir, coil_id, "receive", quantity_lbs,
                     reference=po_number or bol_number,
                     notes=condition_notes, created_by=received_by,
                     balance_after=new_stock)

    # Log receiving record
    rec = ReceivingRecord(
        coil_id=coil_id, po_number=po_number, bol_number=bol_number,
        supplier=supplier or coil.get("supplier", ""),
        quantity_lbs=quantity_lbs, heat_number=heat_number,
        condition_notes=condition_notes, received_by=received_by,
    )
    records = _load_receiving(base_dir)
    records.append(rec.to_dict())
    _save_receiving(base_dir, records)

    # Check alerts
    _check_and_clear_alerts(base_dir, coil_id, coil)

    return {"coil_id": coil_id, "old_stock": old_stock, "new_stock": new_stock,
            "receiving_id": rec.receiving_id}


def adjust_stock(base_dir: str, coil_id: str, quantity_lbs: float,
                 reason: str = "", adjusted_by: str = "") -> dict:
    """Adjust stock (positive = add, negative = subtract). For corrections."""
    inv = _load_inventory_main(base_dir)
    coils = inv.get("coils", {})

    if coil_id not in coils:
        raise ValueError(f"Coil '{coil_id}' not found")

    coil = coils[coil_id]
    old_stock = coil.get("stock_lbs", 0)
    new_stock = max(0, old_stock + quantity_lbs)
    coil["stock_lbs"] = new_stock

    lbs_per_lft = coil.get("lbs_per_lft", 0)
    if lbs_per_lft > 0:
        coil["stock_lft"] = round(new_stock / lbs_per_lft, 1)

    coils[coil_id] = coil
    inv["coils"] = coils
    _save_inventory_main(base_dir, inv)

    _log_transaction(base_dir, coil_id, "adjust", quantity_lbs,
                     notes=reason, created_by=adjusted_by,
                     balance_after=new_stock)

    _check_alerts(base_dir, coil_id, coil)

    return {"coil_id": coil_id, "old_stock": old_stock, "new_stock": new_stock}


def consume_stock(base_dir: str, coil_id: str, quantity_lbs: float,
                  job_code: str = "", work_order_ref: str = "",
                  consumed_by: str = "") -> dict:
    """Record stock consumption (material used in fabrication)."""
    inv = _load_inventory_main(base_dir)
    coils = inv.get("coils", {})

    if coil_id not in coils:
        raise ValueError(f"Coil '{coil_id}' not found")
    if quantity_lbs <= 0:
        raise ValueError("Quantity must be positive")

    coil = coils[coil_id]
    old_stock = coil.get("stock_lbs", 0)
    new_stock = max(0, old_stock - quantity_lbs)
    coil["stock_lbs"] = new_stock

    lbs_per_lft = coil.get("lbs_per_lft", 0)
    if lbs_per_lft > 0:
        coil["stock_lft"] = round(new_stock / lbs_per_lft, 1)

    coils[coil_id] = coil
    inv["coils"] = coils
    _save_inventory_main(base_dir, inv)

    _log_transaction(base_dir, coil_id, "consume", quantity_lbs,
                     job_code=job_code, work_order_ref=work_order_ref,
                     created_by=consumed_by, balance_after=new_stock)

    _check_alerts(base_dir, coil_id, coil)

    return {"coil_id": coil_id, "old_stock": old_stock, "new_stock": new_stock}


def list_transactions(base_dir: str, coil_id: str = "",
                      transaction_type: str = "",
                      date_from: str = "", date_to: str = "") -> list:
    """List transactions with optional filters."""
    txns = _load_transactions(base_dir)
    result = []
    for t in txns:
        if coil_id and t.get("coil_id") != coil_id:
            continue
        if transaction_type and t.get("transaction_type") != transaction_type:
            continue
        if date_from and t.get("created_at", "") < date_from:
            continue
        if date_to and t.get("created_at", "") > date_to:
            continue
        result.append(t)
    result.sort(key=lambda t: t.get("created_at", ""), reverse=True)
    return result


# ─────────────────────────────────────────────────────────────────────────────
# ALLOCATIONS
# ─────────────────────────────────────────────────────────────────────────────

def allocate_stock(base_dir: str, coil_id: str, job_code: str,
                   quantity_lbs: float, work_order_ref: str = "",
                   notes: str = "", allocated_by: str = "") -> Allocation:
    """Allocate stock from a coil to a job."""
    inv = _load_inventory_main(base_dir)
    coils = inv.get("coils", {})

    if coil_id not in coils:
        raise ValueError(f"Coil '{coil_id}' not found")
    if quantity_lbs <= 0:
        raise ValueError("Quantity must be positive")

    coil = coils[coil_id]
    stock = coil.get("stock_lbs", 0)
    committed = coil.get("committed_lbs", 0)
    available = stock - committed

    if quantity_lbs > available:
        raise ValueError(f"Insufficient stock. Available: {available:.0f} lbs, Requested: {quantity_lbs:.0f} lbs")

    # Update committed
    coil["committed_lbs"] = committed + quantity_lbs
    coils[coil_id] = coil
    inv["coils"] = coils
    _save_inventory_main(base_dir, inv)

    # Create allocation record
    alloc = Allocation(
        coil_id=coil_id, job_code=job_code, quantity_lbs=quantity_lbs,
        work_order_ref=work_order_ref, notes=notes, created_by=allocated_by,
    )
    allocs = _load_allocations(base_dir)
    allocs.append(alloc.to_dict())
    _save_allocations(base_dir, allocs)

    # Log transaction
    _log_transaction(base_dir, coil_id, "allocate", quantity_lbs,
                     job_code=job_code, work_order_ref=work_order_ref,
                     notes=notes, created_by=allocated_by,
                     balance_after=stock)

    return alloc


def release_allocation(base_dir: str, allocation_id: str,
                       released_by: str = "") -> dict:
    """Release (cancel) an allocation, returning committed stock."""
    allocs = _load_allocations(base_dir)
    found = None
    for a in allocs:
        if a.get("allocation_id") == allocation_id:
            found = a
            break

    if not found:
        raise ValueError(f"Allocation '{allocation_id}' not found")
    if found.get("status") != "active":
        raise ValueError(f"Allocation is not active (status: {found.get('status')})")

    # Release the committed lbs
    remaining = found.get("quantity_lbs", 0) - found.get("consumed_lbs", 0)
    coil_id = found.get("coil_id")

    inv = _load_inventory_main(base_dir)
    coils = inv.get("coils", {})
    if coil_id in coils:
        coils[coil_id]["committed_lbs"] = max(0,
            coils[coil_id].get("committed_lbs", 0) - remaining)
        inv["coils"] = coils
        _save_inventory_main(base_dir, inv)

    found["status"] = "released"
    _save_allocations(base_dir, allocs)

    _log_transaction(base_dir, coil_id, "return", remaining,
                     job_code=found.get("job_code", ""),
                     notes=f"Allocation {allocation_id} released",
                     created_by=released_by,
                     balance_after=coils.get(coil_id, {}).get("stock_lbs", 0))

    return {"allocation_id": allocation_id, "released_lbs": remaining}


def list_allocations(base_dir: str, coil_id: str = "",
                     job_code: str = "", status: str = "") -> list:
    """List allocations with optional filters."""
    allocs = _load_allocations(base_dir)
    result = []
    for a in allocs:
        if coil_id and a.get("coil_id") != coil_id:
            continue
        if job_code and a.get("job_code") != job_code:
            continue
        if status and a.get("status") != status:
            continue
        result.append(a)
    result.sort(key=lambda a: a.get("created_at", ""), reverse=True)
    return result


def get_allocation(base_dir: str, allocation_id: str) -> Optional[dict]:
    """Get a single allocation by ID."""
    allocs = _load_allocations(base_dir)
    for a in allocs:
        if a.get("allocation_id") == allocation_id:
            return a
    return None


# ─────────────────────────────────────────────────────────────────────────────
# ALERTS
# ─────────────────────────────────────────────────────────────────────────────

def _check_alerts(base_dir: str, coil_id: str, coil: dict):
    """Check if a coil needs low-stock or depleted alerts."""
    stock = coil.get("stock_lbs", 0)
    min_order = coil.get("min_order_lbs", 5000)
    alerts = _load_alerts(base_dir)

    # Remove existing unacknowledged alerts for this coil
    alerts = [a for a in alerts
              if not (a.get("coil_id") == coil_id and not a.get("acknowledged"))]

    name = coil.get("name", coil_id)

    if stock <= 0:
        alert = StockAlert(
            coil_id=coil_id, alert_level="critical",
            alert_type="depleted",
            message=f"DEPLETED: {name} ({coil_id}) has 0 lbs remaining",
        )
        alerts.append(alert.to_dict())
    elif stock < min_order:
        alert = StockAlert(
            coil_id=coil_id, alert_level="warning",
            alert_type="low_stock",
            message=f"LOW STOCK: {name} ({coil_id}) at {stock:,.0f} lbs (min: {min_order:,.0f})",
        )
        alerts.append(alert.to_dict())

    _save_alerts(base_dir, alerts)


def _check_and_clear_alerts(base_dir: str, coil_id: str, coil: dict):
    """After receiving stock, clear alerts if stock is now sufficient."""
    stock = coil.get("stock_lbs", 0)
    min_order = coil.get("min_order_lbs", 5000)
    alerts = _load_alerts(base_dir)

    if stock >= min_order:
        # Clear unacknowledged low_stock/depleted alerts
        alerts = [a for a in alerts
                  if not (a.get("coil_id") == coil_id
                          and a.get("alert_type") in ("low_stock", "depleted")
                          and not a.get("acknowledged"))]
        _save_alerts(base_dir, alerts)
    else:
        _check_alerts(base_dir, coil_id, coil)


def list_alerts(base_dir: str, acknowledged: Optional[bool] = None,
                alert_level: str = "", coil_id: str = "") -> list:
    """List alerts with optional filters."""
    alerts = _load_alerts(base_dir)
    result = []
    for a in alerts:
        if acknowledged is not None and a.get("acknowledged") != acknowledged:
            continue
        if alert_level and a.get("alert_level") != alert_level:
            continue
        if coil_id and a.get("coil_id") != coil_id:
            continue
        result.append(a)
    result.sort(key=lambda a: a.get("created_at", ""), reverse=True)
    return result


def acknowledge_alert(base_dir: str, alert_id: str,
                      acknowledged_by: str = "") -> dict:
    """Acknowledge an alert."""
    alerts = _load_alerts(base_dir)
    for a in alerts:
        if a.get("alert_id") == alert_id:
            a["acknowledged"] = True
            a["acknowledged_by"] = acknowledged_by
            a["acknowledged_at"] = datetime.datetime.now().isoformat()
            _save_alerts(base_dir, alerts)
            return a
    raise ValueError(f"Alert '{alert_id}' not found")


# ─────────────────────────────────────────────────────────────────────────────
# RECEIVING RECORDS
# ─────────────────────────────────────────────────────────────────────────────

def list_receiving(base_dir: str, coil_id: str = "",
                   date_from: str = "", date_to: str = "") -> list:
    """List receiving records."""
    records = _load_receiving(base_dir)
    result = []
    for r in records:
        if coil_id and r.get("coil_id") != coil_id:
            continue
        if date_from and r.get("received_at", "") < date_from:
            continue
        if date_to and r.get("received_at", "") > date_to:
            continue
        result.append(r)
    result.sort(key=lambda r: r.get("received_at", ""), reverse=True)
    return result


# ─────────────────────────────────────────────────────────────────────────────
# MILL CERT MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────

def add_mill_cert(base_dir: str, coil_id: str, heat_number: str,
                  mill_name: str = "", material_spec: str = "",
                  filename: str = "", created_by: str = "") -> dict:
    """Add a mill certificate record to a coil."""
    inv = _load_inventory_main(base_dir)
    coils = inv.get("coils", {})

    if coil_id not in coils:
        raise ValueError(f"Coil '{coil_id}' not found")

    now = datetime.datetime.now().isoformat()
    cert = {
        "cert_id": f"CERT-{uuid.uuid4().hex[:8].upper()}",
        "coil_id": coil_id,
        "heat_num": heat_number,
        "mill_name": mill_name,
        "material_spec": material_spec,
        "filename": filename,
        "uploaded_at": now,
        "uploaded_by": created_by,
    }

    inv.setdefault("mill_certs", []).append(cert)

    # Update coil heat number
    if heat_number:
        coils[coil_id]["heat_num"] = heat_number

    inv["coils"] = coils
    _save_inventory_main(base_dir, inv)
    return cert


def list_mill_certs(base_dir: str, coil_id: str = "") -> list:
    """List mill certs, optionally filtered by coil."""
    inv = _load_inventory_main(base_dir)
    certs = inv.get("mill_certs", [])
    if isinstance(certs, dict):
        certs = list(certs.values())
    if coil_id:
        certs = [c for c in certs if c.get("coil_id") == coil_id]
    return certs


def delete_mill_cert(base_dir: str, cert_id: str) -> bool:
    """Delete a mill cert by cert_id."""
    inv = _load_inventory_main(base_dir)
    certs = inv.get("mill_certs", [])
    original_len = len(certs)
    inv["mill_certs"] = [c for c in certs if c.get("cert_id") != cert_id]
    if len(inv["mill_certs"]) < original_len:
        _save_inventory_main(base_dir, inv)
        return True
    return False


# ─────────────────────────────────────────────────────────────────────────────
# ANALYTICS
# ─────────────────────────────────────────────────────────────────────────────

def get_inventory_summary(base_dir: str) -> dict:
    """Get comprehensive inventory summary."""
    inv = _load_inventory_main(base_dir)
    coils = inv.get("coils", {})
    certs = inv.get("mill_certs", [])
    if isinstance(certs, dict):
        certs = list(certs.values())

    alerts = _load_alerts(base_dir)
    active_alerts = [a for a in alerts if not a.get("acknowledged")]

    total_coils = len(coils)
    total_stock_lbs = 0
    total_committed_lbs = 0
    total_value = 0.0
    by_gauge = {}
    by_grade = {}
    by_status = {}
    low_stock_coils = []

    for cid, coil in coils.items():
        stock = coil.get("stock_lbs", 0)
        committed = coil.get("committed_lbs", 0)
        price = coil.get("price_per_lb", 0)
        status = _compute_coil_status(coil)

        total_stock_lbs += stock
        total_committed_lbs += committed
        total_value += stock * price

        gauge = coil.get("gauge", "Unknown")
        by_gauge[gauge] = by_gauge.get(gauge, 0) + stock

        grade = coil.get("grade", "Unknown")
        by_grade[grade] = by_grade.get(grade, 0) + stock

        by_status[status] = by_status.get(status, 0) + 1

        if status in ("low_stock", "depleted"):
            low_stock_coils.append({
                "coil_id": cid,
                "name": coil.get("name", cid),
                "gauge": gauge,
                "stock_lbs": stock,
                "min_order_lbs": coil.get("min_order_lbs", 5000),
                "status": status,
            })

    return {
        "total_coils": total_coils,
        "total_stock_lbs": total_stock_lbs,
        "total_committed_lbs": total_committed_lbs,
        "total_available_lbs": total_stock_lbs - total_committed_lbs,
        "total_value": round(total_value, 2),
        "by_gauge": by_gauge,
        "by_grade": by_grade,
        "by_status": by_status,
        "low_stock_coils": low_stock_coils,
        "total_mill_certs": len(certs),
        "active_alerts": len(active_alerts),
        "critical_alerts": len([a for a in active_alerts if a.get("alert_level") == "critical"]),
    }


def get_coil_history(base_dir: str, coil_id: str) -> dict:
    """Get full history for a coil: transactions, allocations, certs."""
    coil = get_coil(base_dir, coil_id)
    if not coil:
        raise ValueError(f"Coil '{coil_id}' not found")

    txns = list_transactions(base_dir, coil_id=coil_id)
    allocs = list_allocations(base_dir, coil_id=coil_id)
    certs = list_mill_certs(base_dir, coil_id=coil_id)
    receiving = list_receiving(base_dir, coil_id=coil_id)

    return {
        "coil": coil,
        "transactions": txns,
        "allocations": allocs,
        "mill_certs": certs,
        "receiving_records": receiving,
    }


def get_stock_valuation(base_dir: str) -> dict:
    """Get inventory valuation breakdown."""
    inv = _load_inventory_main(base_dir)
    coils = inv.get("coils", {})

    by_gauge = {}
    by_grade = {}
    total = 0.0

    for cid, coil in coils.items():
        stock = coil.get("stock_lbs", 0)
        price = coil.get("price_per_lb", 0)
        value = stock * price
        total += value

        gauge = coil.get("gauge", "Unknown")
        if gauge not in by_gauge:
            by_gauge[gauge] = {"lbs": 0, "value": 0.0, "coils": 0}
        by_gauge[gauge]["lbs"] += stock
        by_gauge[gauge]["value"] += value
        by_gauge[gauge]["coils"] += 1

        grade = coil.get("grade", "Unknown")
        if grade not in by_grade:
            by_grade[grade] = {"lbs": 0, "value": 0.0, "coils": 0}
        by_grade[grade]["lbs"] += stock
        by_grade[grade]["value"] += value
        by_grade[grade]["coils"] += 1

    return {
        "total_value": round(total, 2),
        "by_gauge": {k: {**v, "value": round(v["value"], 2)} for k, v in by_gauge.items()},
        "by_grade": {k: {**v, "value": round(v["value"], 2)} for k, v in by_grade.items()},
    }


def generate_stock_alerts(base_dir: str) -> list:
    """Scan all coils and generate alerts for low-stock / depleted items."""
    inv = _load_inventory_main(base_dir)
    coils = inv.get("coils", {})
    new_alerts = []

    for cid, coil in coils.items():
        status = _compute_coil_status(coil)
        if status in ("low_stock", "depleted"):
            _check_alerts(base_dir, cid, coil)
            new_alerts.append(cid)

    return new_alerts
