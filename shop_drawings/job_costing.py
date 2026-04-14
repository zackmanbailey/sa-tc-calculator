"""
TitanForge v4 — Job Costing & Financial Tracking
==================================================
Material costs, labor tracking, cost estimates vs actuals,
profit margins, change order impacts, and financial reporting
for steel fabrication projects.

Covers:
  - Cost estimates (budgets) per job with line items
  - Actual cost entries (material, labor, equipment, subcontract, overhead)
  - Labor time tracking per work order item
  - Change order financial impact tracking
  - Job P&L summaries and margin analysis
  - Cost variance reporting (estimate vs actual)

Permissions (reuses existing):
  - VIEW_FINANCIALS: read-only access to all cost data and reports
  - VIEW_PROJECT_PNL: view per-project profit/loss
  - PROCESS_EXPENSES: create/edit cost entries, labor records, estimates

Reference: RULES.md §3 (Role Definitions)
"""

import os
import json
import uuid
import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from collections import defaultdict


# ─────────────────────────────────────────────
# COST CATEGORY CONSTANTS
# ─────────────────────────────────────────────

COST_CAT_MATERIAL = "material"
COST_CAT_LABOR = "labor"
COST_CAT_EQUIPMENT = "equipment"
COST_CAT_SUBCONTRACT = "subcontract"
COST_CAT_OVERHEAD = "overhead"
COST_CAT_FREIGHT = "freight"

COST_CATEGORIES = [
    COST_CAT_MATERIAL, COST_CAT_LABOR, COST_CAT_EQUIPMENT,
    COST_CAT_SUBCONTRACT, COST_CAT_OVERHEAD, COST_CAT_FREIGHT,
]

COST_CATEGORY_LABELS = {
    COST_CAT_MATERIAL: "Material",
    COST_CAT_LABOR: "Labor",
    COST_CAT_EQUIPMENT: "Equipment",
    COST_CAT_SUBCONTRACT: "Subcontract",
    COST_CAT_OVERHEAD: "Overhead",
    COST_CAT_FREIGHT: "Freight",
}

# ─────────────────────────────────────────────
# ESTIMATE STATUS CONSTANTS
# ─────────────────────────────────────────────

EST_STATUS_DRAFT = "draft"
EST_STATUS_APPROVED = "approved"
EST_STATUS_REVISED = "revised"
EST_STATUS_FINAL = "final"

EST_STATUSES = [EST_STATUS_DRAFT, EST_STATUS_APPROVED,
                EST_STATUS_REVISED, EST_STATUS_FINAL]

EST_STATUS_LABELS = {
    EST_STATUS_DRAFT: "Draft",
    EST_STATUS_APPROVED: "Approved",
    EST_STATUS_REVISED: "Revised",
    EST_STATUS_FINAL: "Final",
}

# ─────────────────────────────────────────────
# LABOR RATE DEFAULTS
# ─────────────────────────────────────────────

DEFAULT_LABOR_RATES = {
    "welder": 35.00,
    "fitter": 30.00,
    "operator": 28.00,
    "helper": 22.00,
    "foreman": 45.00,
    "painter": 27.00,
    "inspector": 40.00,
}

DEFAULT_LABOR_RATE_LABELS = {
    "welder": "Welder",
    "fitter": "Fitter",
    "operator": "Machine Operator",
    "helper": "Helper",
    "foreman": "Foreman",
    "painter": "Painter",
    "inspector": "QC Inspector",
}

# ─────────────────────────────────────────────
# DATA MODELS
# ─────────────────────────────────────────────

@dataclass
class CostEstimate:
    """Budget estimate for a job — the target to compare actuals against."""
    estimate_id: str = ""
    job_code: str = ""
    name: str = ""                       # "Original Estimate", "Rev 1", etc.
    status: str = EST_STATUS_DRAFT
    total_amount: float = 0.0            # Auto-calculated from line items
    contract_value: float = 0.0          # What the customer is paying
    line_items: List[Dict[str, Any]] = field(default_factory=list)
    # Each line_item: {category, description, quantity, unit, unit_cost, total, notes}
    notes: str = ""
    created_by: str = ""
    created_at: str = ""
    approved_by: str = ""
    approved_at: str = ""

    def __post_init__(self):
        if not self.estimate_id:
            self.estimate_id = f"EST-{uuid.uuid4().hex[:8].upper()}"
        if not self.created_at:
            self.created_at = datetime.datetime.now().isoformat()

    def recalculate_total(self):
        """Recalculate total from line items."""
        self.total_amount = sum(
            float(item.get("total", 0)) for item in self.line_items
        )

    @property
    def estimated_margin(self) -> float:
        """Estimated margin (contract - estimate)."""
        return self.contract_value - self.total_amount

    @property
    def estimated_margin_pct(self) -> float:
        """Estimated margin percentage."""
        if self.contract_value <= 0:
            return 0.0
        return round((self.estimated_margin / self.contract_value) * 100, 1)

    @property
    def status_label(self) -> str:
        return EST_STATUS_LABELS.get(self.status, self.status)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["estimated_margin"] = self.estimated_margin
        d["estimated_margin_pct"] = self.estimated_margin_pct
        d["status_label"] = self.status_label
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "CostEstimate":
        obj = cls()
        for k, v in d.items():
            if hasattr(obj, k) and k not in ("estimated_margin", "estimated_margin_pct", "status_label"):
                setattr(obj, k, v)
        return obj


@dataclass
class CostEntry:
    """An actual cost incurred on a job."""
    entry_id: str = ""
    job_code: str = ""
    category: str = COST_CAT_MATERIAL
    description: str = ""
    quantity: float = 1.0
    unit: str = ""                       # "lbs", "hrs", "ea", "sqft", etc.
    unit_cost: float = 0.0
    total: float = 0.0                   # quantity * unit_cost
    vendor: str = ""
    po_number: str = ""                  # Purchase order reference
    invoice_number: str = ""
    work_order_ref: str = ""             # Related WO ID
    date: str = ""                       # Date cost was incurred
    notes: str = ""
    created_by: str = ""
    created_at: str = ""

    def __post_init__(self):
        if not self.entry_id:
            self.entry_id = f"COST-{uuid.uuid4().hex[:8].upper()}"
        if not self.created_at:
            self.created_at = datetime.datetime.now().isoformat()
        if not self.date:
            self.date = datetime.date.today().isoformat()
        if self.total == 0 and self.quantity and self.unit_cost:
            self.total = round(self.quantity * self.unit_cost, 2)

    @property
    def category_label(self) -> str:
        return COST_CATEGORY_LABELS.get(self.category, self.category)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["category_label"] = self.category_label
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "CostEntry":
        obj = cls()
        for k, v in d.items():
            if hasattr(obj, k) and k != "category_label":
                setattr(obj, k, v)
        return obj


@dataclass
class LaborEntry:
    """Time tracking for labor on a job."""
    labor_id: str = ""
    job_code: str = ""
    work_order_ref: str = ""
    item_ref: str = ""                   # Ship mark or item ID
    worker: str = ""                     # Username
    labor_type: str = "welder"           # Maps to rate table
    date: str = ""
    hours: float = 0.0
    rate: float = 0.0                    # $/hr at time of entry
    total: float = 0.0                   # hours * rate
    overtime: bool = False
    overtime_multiplier: float = 1.5
    description: str = ""
    created_by: str = ""
    created_at: str = ""

    def __post_init__(self):
        if not self.labor_id:
            self.labor_id = f"LAB-{uuid.uuid4().hex[:8].upper()}"
        if not self.created_at:
            self.created_at = datetime.datetime.now().isoformat()
        if not self.date:
            self.date = datetime.date.today().isoformat()
        if self.rate == 0:
            self.rate = DEFAULT_LABOR_RATES.get(self.labor_type, 30.0)
        if self.total == 0 and self.hours and self.rate:
            mult = self.overtime_multiplier if self.overtime else 1.0
            self.total = round(self.hours * self.rate * mult, 2)

    @property
    def effective_rate(self) -> float:
        mult = self.overtime_multiplier if self.overtime else 1.0
        return round(self.rate * mult, 2)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["effective_rate"] = self.effective_rate
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "LaborEntry":
        obj = cls()
        for k, v in d.items():
            if hasattr(obj, k) and k != "effective_rate":
                setattr(obj, k, v)
        return obj


@dataclass
class ChangeOrderCost:
    """Financial impact of a change order."""
    co_id: str = ""
    job_code: str = ""
    change_order_number: int = 0         # Sequential per job
    description: str = ""
    material_impact: float = 0.0
    labor_impact: float = 0.0
    other_impact: float = 0.0
    total_impact: float = 0.0            # Auto-calculated
    approved: bool = False
    approved_by: str = ""
    approved_at: str = ""
    created_by: str = ""
    created_at: str = ""

    def __post_init__(self):
        if not self.co_id:
            self.co_id = f"CO-{uuid.uuid4().hex[:8].upper()}"
        if not self.created_at:
            self.created_at = datetime.datetime.now().isoformat()
        if self.total_impact == 0:
            self.total_impact = round(
                self.material_impact + self.labor_impact + self.other_impact, 2
            )

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "ChangeOrderCost":
        obj = cls()
        for k, v in d.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        return obj


# ─────────────────────────────────────────────
# FILE STORAGE
# ─────────────────────────────────────────────

def _costing_dir(base_dir: str) -> str:
    d = os.path.join(base_dir, "_job_costing")
    os.makedirs(d, exist_ok=True)
    return d

def _load_json(base_dir: str, filename: str) -> list:
    path = os.path.join(_costing_dir(base_dir), filename)
    if not os.path.isfile(path):
        return []
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return []

def _save_json(base_dir: str, filename: str, data: list):
    path = os.path.join(_costing_dir(base_dir), filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def _load_estimates(base_dir: str) -> list:
    return _load_json(base_dir, "estimates.json")

def _save_estimates(base_dir: str, data: list):
    _save_json(base_dir, "estimates.json", data)

def _load_cost_entries(base_dir: str) -> list:
    return _load_json(base_dir, "cost_entries.json")

def _save_cost_entries(base_dir: str, data: list):
    _save_json(base_dir, "cost_entries.json", data)

def _load_labor_entries(base_dir: str) -> list:
    return _load_json(base_dir, "labor_entries.json")

def _save_labor_entries(base_dir: str, data: list):
    _save_json(base_dir, "labor_entries.json", data)

def _load_change_orders(base_dir: str) -> list:
    return _load_json(base_dir, "change_orders.json")

def _save_change_orders(base_dir: str, data: list):
    _save_json(base_dir, "change_orders.json", data)

def _load_labor_rates(base_dir: str) -> dict:
    path = os.path.join(_costing_dir(base_dir), "labor_rates.json")
    if os.path.isfile(path):
        try:
            with open(path) as f:
                return json.load(f)
        except Exception:
            pass
    return dict(DEFAULT_LABOR_RATES)

def _save_labor_rates(base_dir: str, rates: dict):
    path = os.path.join(_costing_dir(base_dir), "labor_rates.json")
    with open(path, "w") as f:
        json.dump(rates, f, indent=2)


# ─────────────────────────────────────────────
# COST ESTIMATE CRUD
# ─────────────────────────────────────────────

def create_estimate(base_dir: str, job_code: str, name: str,
                    created_by: str, contract_value: float = 0.0,
                    line_items: Optional[list] = None,
                    notes: str = "") -> CostEstimate:
    """Create a new cost estimate for a job."""
    est = CostEstimate(
        job_code=job_code, name=name, created_by=created_by,
        contract_value=contract_value,
        line_items=line_items or [], notes=notes,
    )
    est.recalculate_total()

    data = _load_estimates(base_dir)
    data.append(est.to_dict())
    _save_estimates(base_dir, data)
    return est


def get_estimate(base_dir: str, estimate_id: str) -> Optional[CostEstimate]:
    """Get a single estimate by ID."""
    data = _load_estimates(base_dir)
    for d in data:
        if d.get("estimate_id") == estimate_id:
            return CostEstimate.from_dict(d)
    return None


def list_estimates(base_dir: str, job_code: str = "",
                   status: str = "") -> List[CostEstimate]:
    """List estimates with optional filters."""
    data = _load_estimates(base_dir)
    result = []
    for d in data:
        if job_code and d.get("job_code") != job_code:
            continue
        if status and d.get("status") != status:
            continue
        result.append(CostEstimate.from_dict(d))
    result.sort(key=lambda e: e.created_at, reverse=True)
    return result


def update_estimate(base_dir: str, estimate_id: str,
                    **kwargs) -> Optional[CostEstimate]:
    """Update an estimate's fields."""
    data = _load_estimates(base_dir)
    for i, d in enumerate(data):
        if d.get("estimate_id") == estimate_id:
            est = CostEstimate.from_dict(d)
            for k, v in kwargs.items():
                if hasattr(est, k) and k != "estimate_id":
                    setattr(est, k, v)
            if "line_items" in kwargs:
                est.recalculate_total()
            data[i] = est.to_dict()
            _save_estimates(base_dir, data)
            return est
    return None


def approve_estimate(base_dir: str, estimate_id: str,
                     approved_by: str) -> Optional[CostEstimate]:
    """Approve a cost estimate."""
    return update_estimate(
        base_dir, estimate_id,
        status=EST_STATUS_APPROVED,
        approved_by=approved_by,
        approved_at=datetime.datetime.now().isoformat(),
    )


def delete_estimate(base_dir: str, estimate_id: str) -> bool:
    """Delete an estimate. Returns True if found and deleted."""
    data = _load_estimates(base_dir)
    new_data = [d for d in data if d.get("estimate_id") != estimate_id]
    if len(new_data) == len(data):
        return False
    _save_estimates(base_dir, new_data)
    return True


# ─────────────────────────────────────────────
# COST ENTRY CRUD
# ─────────────────────────────────────────────

def add_cost_entry(base_dir: str, job_code: str, category: str,
                   description: str, created_by: str,
                   quantity: float = 1.0, unit: str = "",
                   unit_cost: float = 0.0,
                   vendor: str = "", po_number: str = "",
                   invoice_number: str = "",
                   work_order_ref: str = "",
                   date: str = "", notes: str = "") -> CostEntry:
    """Record an actual cost entry."""
    entry = CostEntry(
        job_code=job_code, category=category,
        description=description, quantity=quantity,
        unit=unit, unit_cost=unit_cost,
        vendor=vendor, po_number=po_number,
        invoice_number=invoice_number,
        work_order_ref=work_order_ref,
        date=date, notes=notes, created_by=created_by,
    )

    data = _load_cost_entries(base_dir)
    data.append(entry.to_dict())
    _save_cost_entries(base_dir, data)
    return entry


def get_cost_entry(base_dir: str, entry_id: str) -> Optional[CostEntry]:
    """Get a single cost entry by ID."""
    data = _load_cost_entries(base_dir)
    for d in data:
        if d.get("entry_id") == entry_id:
            return CostEntry.from_dict(d)
    return None


def list_cost_entries(base_dir: str, job_code: str = "",
                      category: str = "",
                      date_from: str = "",
                      date_to: str = "") -> List[CostEntry]:
    """List cost entries with optional filters."""
    data = _load_cost_entries(base_dir)
    result = []
    for d in data:
        if job_code and d.get("job_code") != job_code:
            continue
        if category and d.get("category") != category:
            continue
        if date_from and d.get("date", "") < date_from:
            continue
        if date_to and d.get("date", "") > date_to:
            continue
        result.append(CostEntry.from_dict(d))
    result.sort(key=lambda e: e.date, reverse=True)
    return result


def delete_cost_entry(base_dir: str, entry_id: str) -> bool:
    """Delete a cost entry."""
    data = _load_cost_entries(base_dir)
    new_data = [d for d in data if d.get("entry_id") != entry_id]
    if len(new_data) == len(data):
        return False
    _save_cost_entries(base_dir, new_data)
    return True


# ─────────────────────────────────────────────
# LABOR ENTRY CRUD
# ─────────────────────────────────────────────

def add_labor_entry(base_dir: str, job_code: str, worker: str,
                    hours: float, created_by: str,
                    labor_type: str = "welder",
                    work_order_ref: str = "", item_ref: str = "",
                    date: str = "", rate: float = 0.0,
                    overtime: bool = False,
                    overtime_multiplier: float = 1.5,
                    description: str = "") -> LaborEntry:
    """Record a labor time entry."""
    if rate == 0:
        rates = _load_labor_rates(base_dir)
        rate = rates.get(labor_type, DEFAULT_LABOR_RATES.get(labor_type, 30.0))

    entry = LaborEntry(
        job_code=job_code, worker=worker, hours=hours,
        labor_type=labor_type, rate=rate,
        work_order_ref=work_order_ref, item_ref=item_ref,
        date=date, overtime=overtime,
        overtime_multiplier=overtime_multiplier,
        description=description, created_by=created_by,
    )

    data = _load_labor_entries(base_dir)
    data.append(entry.to_dict())
    _save_labor_entries(base_dir, data)
    return entry


def get_labor_entry(base_dir: str, labor_id: str) -> Optional[LaborEntry]:
    """Get a single labor entry."""
    data = _load_labor_entries(base_dir)
    for d in data:
        if d.get("labor_id") == labor_id:
            return LaborEntry.from_dict(d)
    return None


def list_labor_entries(base_dir: str, job_code: str = "",
                       worker: str = "",
                       date_from: str = "",
                       date_to: str = "") -> List[LaborEntry]:
    """List labor entries with optional filters."""
    data = _load_labor_entries(base_dir)
    result = []
    for d in data:
        if job_code and d.get("job_code") != job_code:
            continue
        if worker and d.get("worker") != worker:
            continue
        if date_from and d.get("date", "") < date_from:
            continue
        if date_to and d.get("date", "") > date_to:
            continue
        result.append(LaborEntry.from_dict(d))
    result.sort(key=lambda e: e.date, reverse=True)
    return result


def delete_labor_entry(base_dir: str, labor_id: str) -> bool:
    """Delete a labor entry."""
    data = _load_labor_entries(base_dir)
    new_data = [d for d in data if d.get("labor_id") != labor_id]
    if len(new_data) == len(data):
        return False
    _save_labor_entries(base_dir, new_data)
    return True


# ─────────────────────────────────────────────
# LABOR RATE MANAGEMENT
# ─────────────────────────────────────────────

def get_labor_rates(base_dir: str) -> dict:
    """Get current labor rates."""
    return _load_labor_rates(base_dir)


def update_labor_rates(base_dir: str, rates: dict) -> dict:
    """Update labor rates. Merges with existing."""
    current = _load_labor_rates(base_dir)
    current.update(rates)
    _save_labor_rates(base_dir, current)
    return current


# ─────────────────────────────────────────────
# CHANGE ORDER COST CRUD
# ─────────────────────────────────────────────

def create_change_order(base_dir: str, job_code: str,
                        description: str, created_by: str,
                        material_impact: float = 0.0,
                        labor_impact: float = 0.0,
                        other_impact: float = 0.0) -> ChangeOrderCost:
    """Create a change order with financial impact."""
    data = _load_change_orders(base_dir)

    # Auto-number per job
    job_cos = [d for d in data if d.get("job_code") == job_code]
    next_num = max((d.get("change_order_number", 0) for d in job_cos), default=0) + 1

    co = ChangeOrderCost(
        job_code=job_code, change_order_number=next_num,
        description=description, created_by=created_by,
        material_impact=material_impact,
        labor_impact=labor_impact,
        other_impact=other_impact,
    )

    data.append(co.to_dict())
    _save_change_orders(base_dir, data)
    return co


def get_change_order(base_dir: str, co_id: str) -> Optional[ChangeOrderCost]:
    """Get a single change order."""
    data = _load_change_orders(base_dir)
    for d in data:
        if d.get("co_id") == co_id:
            return ChangeOrderCost.from_dict(d)
    return None


def list_change_orders(base_dir: str, job_code: str = "",
                       approved_only: bool = False) -> List[ChangeOrderCost]:
    """List change orders with optional filters."""
    data = _load_change_orders(base_dir)
    result = []
    for d in data:
        if job_code and d.get("job_code") != job_code:
            continue
        if approved_only and not d.get("approved"):
            continue
        result.append(ChangeOrderCost.from_dict(d))
    result.sort(key=lambda c: c.change_order_number)
    return result


def approve_change_order(base_dir: str, co_id: str,
                         approved_by: str) -> Optional[ChangeOrderCost]:
    """Approve a change order."""
    data = _load_change_orders(base_dir)
    for i, d in enumerate(data):
        if d.get("co_id") == co_id:
            d["approved"] = True
            d["approved_by"] = approved_by
            d["approved_at"] = datetime.datetime.now().isoformat()
            data[i] = d
            _save_change_orders(base_dir, data)
            return ChangeOrderCost.from_dict(d)
    return None


# ─────────────────────────────────────────────
# JOB P&L / COST ANALYSIS
# ─────────────────────────────────────────────

def get_job_cost_summary(base_dir: str, job_code: str) -> dict:
    """Comprehensive cost summary for a single job."""
    # Estimates
    estimates = list_estimates(base_dir, job_code=job_code)
    approved_est = None
    for e in estimates:
        if e.status in (EST_STATUS_APPROVED, EST_STATUS_FINAL):
            approved_est = e
            break
    if not approved_est and estimates:
        approved_est = estimates[0]  # Use latest if none approved

    # Actuals
    cost_entries = list_cost_entries(base_dir, job_code=job_code)
    labor_entries = list_labor_entries(base_dir, job_code=job_code)
    change_orders = list_change_orders(base_dir, job_code=job_code)

    # Sum actuals by category
    actual_by_category = defaultdict(float)
    for ce in cost_entries:
        actual_by_category[ce.category] += ce.total

    # Labor totals
    total_labor_hours = sum(le.hours for le in labor_entries)
    total_labor_cost = sum(le.total for le in labor_entries)
    actual_by_category[COST_CAT_LABOR] += total_labor_cost

    total_actual = sum(actual_by_category.values())

    # Change orders
    approved_cos = [co for co in change_orders if co.approved]
    total_co_impact = sum(co.total_impact for co in approved_cos)
    pending_cos = [co for co in change_orders if not co.approved]
    pending_co_impact = sum(co.total_impact for co in pending_cos)

    # Estimate data
    estimated_total = approved_est.total_amount if approved_est else 0
    contract_value = approved_est.contract_value if approved_est else 0

    # Adjusted budget = original estimate + approved change orders
    adjusted_budget = estimated_total + total_co_impact
    adjusted_contract = contract_value + total_co_impact

    # Variance
    cost_variance = adjusted_budget - total_actual  # positive = under budget
    variance_pct = round((cost_variance / adjusted_budget * 100), 1) if adjusted_budget else 0

    # Margins
    actual_margin = adjusted_contract - total_actual
    actual_margin_pct = round((actual_margin / adjusted_contract * 100), 1) if adjusted_contract else 0

    # Estimate by category (from line items)
    est_by_category = defaultdict(float)
    if approved_est:
        for item in approved_est.line_items:
            est_by_category[item.get("category", "other")] += float(item.get("total", 0))

    # Labor by worker
    labor_by_worker = defaultdict(lambda: {"hours": 0, "cost": 0})
    for le in labor_entries:
        labor_by_worker[le.worker]["hours"] += le.hours
        labor_by_worker[le.worker]["cost"] += le.total

    # Labor by type
    labor_by_type = defaultdict(lambda: {"hours": 0, "cost": 0})
    for le in labor_entries:
        labor_by_type[le.labor_type]["hours"] += le.hours
        labor_by_type[le.labor_type]["cost"] += le.total

    return {
        "job_code": job_code,
        "contract_value": contract_value,
        "adjusted_contract": adjusted_contract,
        "estimated_total": estimated_total,
        "adjusted_budget": adjusted_budget,
        "total_actual": round(total_actual, 2),
        "cost_variance": round(cost_variance, 2),
        "variance_pct": variance_pct,
        "actual_margin": round(actual_margin, 2),
        "actual_margin_pct": actual_margin_pct,
        "actual_by_category": {k: round(v, 2) for k, v in actual_by_category.items()},
        "estimated_by_category": {k: round(v, 2) for k, v in est_by_category.items()},
        "total_labor_hours": round(total_labor_hours, 1),
        "total_labor_cost": round(total_labor_cost, 2),
        "labor_by_worker": {k: {"hours": round(v["hours"], 1), "cost": round(v["cost"], 2)}
                            for k, v in labor_by_worker.items()},
        "labor_by_type": {k: {"hours": round(v["hours"], 1), "cost": round(v["cost"], 2)}
                          for k, v in labor_by_type.items()},
        "change_orders_approved": len(approved_cos),
        "change_orders_pending": len(pending_cos),
        "total_co_impact": round(total_co_impact, 2),
        "pending_co_impact": round(pending_co_impact, 2),
        "cost_entry_count": len(cost_entries),
        "labor_entry_count": len(labor_entries),
        "has_estimate": approved_est is not None,
        "estimate_id": approved_est.estimate_id if approved_est else "",
    }


def get_cost_variance_report(base_dir: str, job_code: str) -> dict:
    """Detailed variance report comparing estimate to actual by category."""
    summary = get_job_cost_summary(base_dir, job_code)
    est_by_cat = summary["estimated_by_category"]
    act_by_cat = summary["actual_by_category"]

    all_cats = set(list(est_by_cat.keys()) + list(act_by_cat.keys()))
    variances = []
    for cat in sorted(all_cats):
        estimated = est_by_cat.get(cat, 0)
        actual = act_by_cat.get(cat, 0)
        variance = estimated - actual
        pct = round((variance / estimated * 100), 1) if estimated else 0
        variances.append({
            "category": cat,
            "category_label": COST_CATEGORY_LABELS.get(cat, cat),
            "estimated": estimated,
            "actual": actual,
            "variance": round(variance, 2),
            "variance_pct": pct,
            "over_budget": actual > estimated if estimated > 0 else False,
        })

    return {
        "job_code": job_code,
        "variances": variances,
        "total_estimated": summary["estimated_total"],
        "total_actual": summary["total_actual"],
        "total_variance": summary["cost_variance"],
        "total_variance_pct": summary["variance_pct"],
    }


def get_financial_overview(base_dir: str) -> dict:
    """Cross-job financial overview for executives."""
    estimates = _load_estimates(base_dir)
    cost_entries = _load_cost_entries(base_dir)
    labor_entries = _load_labor_entries(base_dir)
    change_orders = _load_change_orders(base_dir)

    # Get unique job codes
    job_codes = set()
    for d in estimates:
        job_codes.add(d.get("job_code", ""))
    for d in cost_entries:
        job_codes.add(d.get("job_code", ""))
    for d in labor_entries:
        job_codes.add(d.get("job_code", ""))
    job_codes.discard("")

    # Aggregate
    total_contract = 0
    total_estimated = 0
    total_actual = 0
    total_co_impact = 0
    jobs_over_budget = 0
    jobs_data = []

    for jc in sorted(job_codes):
        summary = get_job_cost_summary(base_dir, jc)
        total_contract += summary["contract_value"]
        total_estimated += summary["estimated_total"]
        total_actual += summary["total_actual"]
        total_co_impact += summary["total_co_impact"]
        if summary["cost_variance"] < 0:
            jobs_over_budget += 1
        jobs_data.append({
            "job_code": jc,
            "contract_value": summary["contract_value"],
            "estimated_total": summary["estimated_total"],
            "total_actual": summary["total_actual"],
            "actual_margin_pct": summary["actual_margin_pct"],
            "cost_variance": summary["cost_variance"],
            "variance_pct": summary["variance_pct"],
        })

    # Category totals across all jobs
    all_costs_by_cat = defaultdict(float)
    for d in cost_entries:
        all_costs_by_cat[d.get("category", "other")] += float(d.get("total", 0))
    for d in labor_entries:
        all_costs_by_cat[COST_CAT_LABOR] += float(d.get("total", 0))

    total_margin = total_contract - total_actual
    margin_pct = round((total_margin / total_contract * 100), 1) if total_contract else 0

    return {
        "total_jobs": len(job_codes),
        "total_contract_value": round(total_contract, 2),
        "total_estimated": round(total_estimated, 2),
        "total_actual": round(total_actual, 2),
        "total_margin": round(total_margin, 2),
        "margin_pct": margin_pct,
        "total_co_impact": round(total_co_impact, 2),
        "jobs_over_budget": jobs_over_budget,
        "costs_by_category": {k: round(v, 2) for k, v in all_costs_by_cat.items()},
        "jobs": jobs_data,
    }
