"""
TitanForge v4 — Scheduling & Production Planning Engine
=========================================================
Production calendar, capacity planning per machine, job sequencing,
estimated completion dates, and bottleneck forecasting.

Integrates with:
  - work_orders.py for item/machine data, statuses, durations
  - fab_steps.py for estimated_minutes per component type
  - reporting.py for throughput metrics (historical basis for forecasts)

Permissions (new):
  - MANAGE_SCHEDULE: create/edit schedule entries, set priorities, adjust capacity
  - VIEW_SCHEDULE: read-only access to production calendar & forecasts

Reference: RULES.md §5 (Work Order Item Lifecycle), §3 (Role Definitions)
"""

import os
import json
import uuid
import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any, Tuple
from collections import defaultdict

from shop_drawings.work_orders import (
    WorkOrder, WorkOrderItem,
    VALID_STATUSES, STATUS_LABELS,
    STATUS_QUEUED, STATUS_APPROVED, STATUS_STICKERS_PRINTED, STATUS_STAGED,
    STATUS_IN_PROGRESS, STATUS_FABRICATED, STATUS_ON_HOLD,
    STATUS_QC_PENDING, STATUS_QC_APPROVED, STATUS_QC_REJECTED,
    STATUS_READY_TO_SHIP, STATUS_SHIPPED, STATUS_DELIVERED, STATUS_INSTALLED,
    MACHINE_TYPES,
    load_work_order, list_work_orders, list_all_work_orders,
)
from shop_drawings.fab_steps import get_steps_for_item, COMPONENT_TYPE_MAP


# ─────────────────────────────────────────────
# SCHEDULE STATUS CONSTANTS
# ─────────────────────────────────────────────

SCHED_STATUS_DRAFT = "draft"           # Schedule created but not committed
SCHED_STATUS_ACTIVE = "active"         # Live production schedule
SCHED_STATUS_COMPLETED = "completed"   # All items in schedule are done
SCHED_STATUS_CANCELLED = "cancelled"   # Schedule cancelled

SCHED_STATUSES = [SCHED_STATUS_DRAFT, SCHED_STATUS_ACTIVE,
                  SCHED_STATUS_COMPLETED, SCHED_STATUS_CANCELLED]

SCHED_STATUS_LABELS = {
    SCHED_STATUS_DRAFT: "Draft",
    SCHED_STATUS_ACTIVE: "Active",
    SCHED_STATUS_COMPLETED: "Completed",
    SCHED_STATUS_CANCELLED: "Cancelled",
}

# ── Priority levels for scheduling ──
PRIORITY_URGENT = 1
PRIORITY_HIGH = 2
PRIORITY_NORMAL = 3
PRIORITY_LOW = 4

PRIORITY_LABELS = {
    PRIORITY_URGENT: "Urgent",
    PRIORITY_HIGH: "High",
    PRIORITY_NORMAL: "Normal",
    PRIORITY_LOW: "Low",
}

PRIORITY_COLORS = {
    PRIORITY_URGENT: "red",
    PRIORITY_HIGH: "orange",
    PRIORITY_NORMAL: "blue",
    PRIORITY_LOW: "gray",
}


# ─────────────────────────────────────────────
# MACHINE CAPACITY CONFIGURATION
# ─────────────────────────────────────────────

# Default shift configuration
DEFAULT_SHIFT_HOURS = 10          # 10-hour day (standard for fab shops)
DEFAULT_SHIFT_MINUTES = DEFAULT_SHIFT_HOURS * 60
DEFAULT_SHIFTS_PER_DAY = 1        # Single shift default
DEFAULT_EFFICIENCY_FACTOR = 0.80  # 80% — accounts for breaks, setup, cleanup

# Default capacity per machine (minutes available per day)
def _default_machine_capacity() -> Dict[str, dict]:
    """Build default machine capacity map from MACHINE_TYPES."""
    capacity = {}
    for m_key, m_info in MACHINE_TYPES.items():
        capacity[m_key] = {
            "machine": m_key,
            "label": m_info["label"],
            "shift_hours": DEFAULT_SHIFT_HOURS,
            "shifts_per_day": DEFAULT_SHIFTS_PER_DAY,
            "efficiency_factor": DEFAULT_EFFICIENCY_FACTOR,
            "available_minutes_per_day": round(
                DEFAULT_SHIFT_MINUTES * DEFAULT_SHIFTS_PER_DAY * DEFAULT_EFFICIENCY_FACTOR
            ),
            "enabled": True,
        }
    return capacity


# ─────────────────────────────────────────────
# DATA MODELS
# ─────────────────────────────────────────────

@dataclass
class ScheduleEntry:
    """A single scheduled item — one WO item assigned to a machine on a date."""
    entry_id: str = ""
    job_code: str = ""
    work_order_id: str = ""
    item_id: str = ""
    ship_mark: str = ""
    component_type: str = ""
    machine: str = ""
    scheduled_date: str = ""         # YYYY-MM-DD
    estimated_minutes: int = 0
    priority: int = PRIORITY_NORMAL
    sequence: int = 0                # Order within the day for that machine
    assigned_to: str = ""            # Operator
    status: str = "pending"          # pending, in_progress, completed, skipped
    actual_start: str = ""           # ISO timestamp
    actual_end: str = ""             # ISO timestamp
    actual_minutes: float = 0.0
    notes: str = ""
    created_by: str = ""
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if not self.entry_id:
            self.entry_id = f"SCHED-{uuid.uuid4().hex[:8].upper()}"
        if not self.created_at:
            self.created_at = datetime.datetime.now().isoformat()

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "ScheduleEntry":
        entry = cls.__new__(cls)
        for f in cls.__dataclass_fields__:
            setattr(entry, f, d.get(f, cls.__dataclass_fields__[f].default
                    if cls.__dataclass_fields__[f].default is not dataclass
                    else ""))
        # Safer approach
        entry2 = cls()
        for k, v in d.items():
            if hasattr(entry2, k):
                setattr(entry2, k, v)
        return entry2

    @property
    def priority_label(self) -> str:
        return PRIORITY_LABELS.get(self.priority, "Normal")

    @property
    def priority_color(self) -> str:
        return PRIORITY_COLORS.get(self.priority, "blue")

    @property
    def is_overdue(self) -> bool:
        """Entry is overdue if scheduled date is past and status is still pending."""
        if self.status != "pending":
            return False
        if not self.scheduled_date:
            return False
        today = datetime.date.today().isoformat()
        return self.scheduled_date < today


@dataclass
class ProductionSchedule:
    """A named production schedule (e.g., weekly schedule, rush order schedule)."""
    schedule_id: str = ""
    name: str = ""
    description: str = ""
    status: str = SCHED_STATUS_DRAFT
    start_date: str = ""             # YYYY-MM-DD
    end_date: str = ""               # YYYY-MM-DD
    job_codes: List[str] = field(default_factory=list)  # Projects included
    created_by: str = ""
    created_at: str = ""
    updated_at: str = ""
    entry_count: int = 0

    def __post_init__(self):
        if not self.schedule_id:
            self.schedule_id = f"PS-{uuid.uuid4().hex[:8].upper()}"
        if not self.created_at:
            self.created_at = datetime.datetime.now().isoformat()

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "ProductionSchedule":
        ps = cls()
        for k, v in d.items():
            if hasattr(ps, k):
                setattr(ps, k, v)
        return ps

    @property
    def status_label(self) -> str:
        return SCHED_STATUS_LABELS.get(self.status, self.status)


# ─────────────────────────────────────────────
# FILE STORAGE
# ─────────────────────────────────────────────

def _schedule_dir(base_dir: str) -> str:
    """Directory for scheduling data."""
    d = os.path.join(base_dir, "_scheduling")
    os.makedirs(d, exist_ok=True)
    return d


def _load_schedules_file(base_dir: str) -> List[dict]:
    """Load the schedules index."""
    path = os.path.join(_schedule_dir(base_dir), "schedules.json")
    if not os.path.isfile(path):
        return []
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return []


def _save_schedules_file(base_dir: str, data: List[dict]):
    """Save the schedules index."""
    path = os.path.join(_schedule_dir(base_dir), "schedules.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _load_entries_file(base_dir: str) -> List[dict]:
    """Load all schedule entries."""
    path = os.path.join(_schedule_dir(base_dir), "entries.json")
    if not os.path.isfile(path):
        return []
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return []


def _save_entries_file(base_dir: str, data: List[dict]):
    """Save all schedule entries."""
    path = os.path.join(_schedule_dir(base_dir), "entries.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _load_capacity_config(base_dir: str) -> Dict[str, dict]:
    """Load machine capacity configuration."""
    path = os.path.join(_schedule_dir(base_dir), "capacity.json")
    if not os.path.isfile(path):
        return _default_machine_capacity()
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return _default_machine_capacity()


def _save_capacity_config(base_dir: str, config: Dict[str, dict]):
    """Save machine capacity configuration."""
    path = os.path.join(_schedule_dir(base_dir), "capacity.json")
    with open(path, "w") as f:
        json.dump(config, f, indent=2)


# ─────────────────────────────────────────────
# SCHEDULE CRUD
# ─────────────────────────────────────────────

def create_schedule(base_dir: str, name: str, start_date: str,
                    end_date: str, created_by: str,
                    description: str = "",
                    job_codes: Optional[List[str]] = None) -> ProductionSchedule:
    """Create a new production schedule."""
    ps = ProductionSchedule(
        name=name,
        description=description,
        start_date=start_date,
        end_date=end_date,
        created_by=created_by,
        job_codes=job_codes or [],
    )

    schedules = _load_schedules_file(base_dir)
    schedules.append(ps.to_dict())
    _save_schedules_file(base_dir, schedules)

    return ps


def get_schedule(base_dir: str, schedule_id: str) -> Optional[ProductionSchedule]:
    """Load a single schedule by ID."""
    schedules = _load_schedules_file(base_dir)
    for s in schedules:
        if s.get("schedule_id") == schedule_id:
            ps = ProductionSchedule.from_dict(s)
            # Enrich with entry count
            entries = _load_entries_file(base_dir)
            ps.entry_count = len([e for e in entries
                                  if e.get("schedule_id") == schedule_id])
            return ps
    return None


def list_schedules(base_dir: str) -> List[ProductionSchedule]:
    """List all production schedules."""
    raw = _load_schedules_file(base_dir)
    entries = _load_entries_file(base_dir)
    result = []
    for s in raw:
        ps = ProductionSchedule.from_dict(s)
        ps.entry_count = len([e for e in entries
                              if e.get("schedule_id") == s.get("schedule_id")])
        result.append(ps)
    return result


def update_schedule(base_dir: str, schedule_id: str,
                    **kwargs) -> Optional[ProductionSchedule]:
    """Update schedule fields. Returns updated schedule or None."""
    schedules = _load_schedules_file(base_dir)
    for i, s in enumerate(schedules):
        if s.get("schedule_id") == schedule_id:
            for k, v in kwargs.items():
                if k in ProductionSchedule.__dataclass_fields__ and k != "schedule_id":
                    s[k] = v
            s["updated_at"] = datetime.datetime.now().isoformat()
            schedules[i] = s
            _save_schedules_file(base_dir, schedules)
            return ProductionSchedule.from_dict(s)
    return None


def delete_schedule(base_dir: str, schedule_id: str) -> bool:
    """Delete a schedule and all its entries."""
    schedules = _load_schedules_file(base_dir)
    new_schedules = [s for s in schedules if s.get("schedule_id") != schedule_id]
    if len(new_schedules) == len(schedules):
        return False
    _save_schedules_file(base_dir, new_schedules)

    # Also remove entries for this schedule
    entries = _load_entries_file(base_dir)
    new_entries = [e for e in entries if e.get("schedule_id") != schedule_id]
    _save_entries_file(base_dir, new_entries)

    return True


# ─────────────────────────────────────────────
# SCHEDULE ENTRY CRUD
# ─────────────────────────────────────────────

def add_schedule_entry(base_dir: str, job_code: str, work_order_id: str,
                       item_id: str, machine: str, scheduled_date: str,
                       estimated_minutes: int, created_by: str,
                       priority: int = PRIORITY_NORMAL,
                       assigned_to: str = "",
                       ship_mark: str = "",
                       component_type: str = "",
                       notes: str = "",
                       schedule_id: str = "") -> ScheduleEntry:
    """Add a single entry to the schedule."""
    entry = ScheduleEntry(
        job_code=job_code,
        work_order_id=work_order_id,
        item_id=item_id,
        machine=machine,
        scheduled_date=scheduled_date,
        estimated_minutes=estimated_minutes,
        priority=priority,
        assigned_to=assigned_to,
        ship_mark=ship_mark,
        component_type=component_type,
        notes=notes,
        created_by=created_by,
    )

    entries = _load_entries_file(base_dir)

    # Auto-sequence: find max sequence for that machine+date
    same_slot = [e for e in entries
                 if e.get("machine") == machine
                 and e.get("scheduled_date") == scheduled_date]
    max_seq = max((e.get("sequence", 0) for e in same_slot), default=0)
    entry.sequence = max_seq + 1

    d = entry.to_dict()
    if schedule_id:
        d["schedule_id"] = schedule_id
    entries.append(d)
    _save_entries_file(base_dir, entries)

    return entry


def get_schedule_entry(base_dir: str, entry_id: str) -> Optional[ScheduleEntry]:
    """Load a single schedule entry."""
    entries = _load_entries_file(base_dir)
    for e in entries:
        if e.get("entry_id") == entry_id:
            return ScheduleEntry.from_dict(e)
    return None


def update_schedule_entry(base_dir: str, entry_id: str,
                          **kwargs) -> Optional[ScheduleEntry]:
    """Update a schedule entry. Returns updated entry or None."""
    entries = _load_entries_file(base_dir)
    for i, e in enumerate(entries):
        if e.get("entry_id") == entry_id:
            for k, v in kwargs.items():
                if k in ScheduleEntry.__dataclass_fields__ and k != "entry_id":
                    e[k] = v
            e["updated_at"] = datetime.datetime.now().isoformat()
            entries[i] = e
            _save_entries_file(base_dir, entries)
            return ScheduleEntry.from_dict(e)
    return None


def delete_schedule_entry(base_dir: str, entry_id: str) -> bool:
    """Delete a schedule entry."""
    entries = _load_entries_file(base_dir)
    new_entries = [e for e in entries if e.get("entry_id") != entry_id]
    if len(new_entries) == len(entries):
        return False
    _save_entries_file(base_dir, new_entries)
    return True


def get_entries_for_date(base_dir: str, date: str,
                         machine: str = "") -> List[ScheduleEntry]:
    """Get all schedule entries for a date, optionally filtered by machine."""
    entries = _load_entries_file(base_dir)
    result = []
    for e in entries:
        if e.get("scheduled_date") != date:
            continue
        if machine and e.get("machine") != machine:
            continue
        result.append(ScheduleEntry.from_dict(e))

    # Sort by priority (urgent first), then sequence
    result.sort(key=lambda x: (x.priority, x.sequence))
    return result


def get_entries_for_range(base_dir: str, start_date: str,
                          end_date: str, machine: str = "",
                          job_code: str = "") -> List[ScheduleEntry]:
    """Get schedule entries within a date range."""
    entries = _load_entries_file(base_dir)
    result = []
    for e in entries:
        sd = e.get("scheduled_date", "")
        if not sd or sd < start_date or sd > end_date:
            continue
        if machine and e.get("machine") != machine:
            continue
        if job_code and e.get("job_code") != job_code:
            continue
        result.append(ScheduleEntry.from_dict(e))

    result.sort(key=lambda x: (x.scheduled_date, x.machine, x.priority, x.sequence))
    return result


def get_entries_for_job(base_dir: str, job_code: str) -> List[ScheduleEntry]:
    """Get all schedule entries for a project."""
    entries = _load_entries_file(base_dir)
    result = [ScheduleEntry.from_dict(e) for e in entries
              if e.get("job_code") == job_code]
    result.sort(key=lambda x: (x.scheduled_date, x.machine, x.sequence))
    return result


# ─────────────────────────────────────────────
# CAPACITY MANAGEMENT
# ─────────────────────────────────────────────

def get_machine_capacity(base_dir: str) -> Dict[str, dict]:
    """Get current machine capacity configuration."""
    return _load_capacity_config(base_dir)


def update_machine_capacity(base_dir: str, machine: str,
                            **kwargs) -> Optional[dict]:
    """Update capacity for a specific machine."""
    config = _load_capacity_config(base_dir)
    if machine not in config:
        return None

    for k, v in kwargs.items():
        if k in config[machine]:
            config[machine][k] = v

    # Recalculate available minutes
    c = config[machine]
    c["available_minutes_per_day"] = round(
        c["shift_hours"] * 60 * c["shifts_per_day"] * c["efficiency_factor"]
    )

    _save_capacity_config(base_dir, config)
    return config[machine]


def get_daily_capacity_usage(base_dir: str, date: str) -> Dict[str, dict]:
    """Calculate capacity usage for each machine on a given date.

    Returns dict keyed by machine with:
      - available_minutes: total capacity
      - scheduled_minutes: minutes already scheduled
      - remaining_minutes: capacity remaining
      - utilization_pct: percentage used
      - entry_count: number of entries
    """
    capacity = _load_capacity_config(base_dir)
    entries = _load_entries_file(base_dir)

    # Filter entries for this date
    day_entries = [e for e in entries if e.get("scheduled_date") == date]

    result = {}
    for m_key, m_cap in capacity.items():
        if not m_cap.get("enabled", True):
            continue

        avail = m_cap["available_minutes_per_day"]
        m_entries = [e for e in day_entries if e.get("machine") == m_key]
        scheduled = sum(e.get("estimated_minutes", 0) for e in m_entries)

        result[m_key] = {
            "machine": m_key,
            "label": m_cap.get("label", m_key),
            "available_minutes": avail,
            "scheduled_minutes": scheduled,
            "remaining_minutes": max(avail - scheduled, 0),
            "utilization_pct": round(scheduled / max(avail, 1) * 100, 1),
            "entry_count": len(m_entries),
            "over_capacity": scheduled > avail,
        }

    return result


def get_capacity_forecast(base_dir: str, days_ahead: int = 14) -> List[dict]:
    """Get capacity utilization forecast for the next N days.

    Returns a list of daily summaries with per-machine utilization.
    """
    today = datetime.date.today()
    forecast = []

    for i in range(days_ahead):
        d = today + datetime.timedelta(days=i)
        date_str = d.isoformat()
        weekday = d.strftime("%A")
        is_weekend = d.weekday() >= 5

        usage = get_daily_capacity_usage(base_dir, date_str)

        total_avail = sum(m["available_minutes"] for m in usage.values())
        total_sched = sum(m["scheduled_minutes"] for m in usage.values())
        total_entries = sum(m["entry_count"] for m in usage.values())
        over_capacity_machines = [m_key for m_key, m in usage.items()
                                  if m["over_capacity"]]

        forecast.append({
            "date": date_str,
            "weekday": weekday,
            "is_weekend": is_weekend,
            "total_available_minutes": total_avail,
            "total_scheduled_minutes": total_sched,
            "total_remaining_minutes": max(total_avail - total_sched, 0),
            "overall_utilization_pct": round(
                total_sched / max(total_avail, 1) * 100, 1
            ),
            "entry_count": total_entries,
            "machines": usage,
            "over_capacity_machines": over_capacity_machines,
        })

    return forecast


# ─────────────────────────────────────────────
# AUTO-SCHEDULING ENGINE
# ─────────────────────────────────────────────

def _estimate_item_minutes(item: WorkOrderItem, wo_base_dir: str = "",
                           job_code: str = "") -> int:
    """Estimate fabrication time for an item.

    Priority:
      1. item.duration_minutes (if set from actual fab time)
      2. Sum of fab step estimated_minutes
      3. Default 60 minutes
    """
    if item.duration_minutes and item.duration_minutes > 0:
        return int(item.duration_minutes)

    item_dict = item.to_dict()
    steps = get_steps_for_item(item_dict, wo_base_dir, job_code)
    if steps:
        total = sum(s.get("estimated_minutes", 0) for s in steps)
        if total > 0:
            return total

    return 60  # Default fallback


def auto_schedule_job(base_dir: str, wo_base_dir: str, job_code: str,
                      start_date: str, created_by: str,
                      priority: int = PRIORITY_NORMAL) -> List[ScheduleEntry]:
    """Auto-schedule all unscheduled items for a job.

    Algorithm:
      1. Load all WO items for the job that are in schedulable statuses
      2. Group by machine
      3. For each machine, fill days starting from start_date
         respecting daily capacity limits
      4. Higher priority items go first

    Returns list of created schedule entries.
    """
    # Load all WOs for the job
    wo_summaries = list_work_orders(wo_base_dir, job_code)
    if not wo_summaries:
        return []

    # Get existing scheduled item_ids to avoid duplicates
    existing_entries = _load_entries_file(base_dir)
    already_scheduled = set(e.get("item_id") for e in existing_entries
                           if e.get("job_code") == job_code)

    # Collect schedulable items
    schedulable_statuses = [
        STATUS_QUEUED, STATUS_APPROVED, STATUS_STICKERS_PRINTED, STATUS_STAGED,
    ]

    items_to_schedule = []
    for wo_summary in wo_summaries:
        wo_id = wo_summary.get("work_order_id", "")
        if not wo_id:
            continue
        wo = load_work_order(wo_base_dir, job_code, wo_id)
        if not wo:
            continue
        for item in wo.items:
            if item.item_id in already_scheduled:
                continue
            if item.status not in schedulable_statuses:
                continue
            if not item.machine:
                continue
            est_mins = _estimate_item_minutes(item, wo_base_dir, job_code)
            items_to_schedule.append({
                "item": item,
                "wo_id": wo_id,
                "est_minutes": est_mins,
            })

    if not items_to_schedule:
        return []

    # Sort: priority first (lower = higher), then by item_id for determinism
    items_to_schedule.sort(key=lambda x: (x["item"].priority, x["item"].item_id))

    # Group by machine
    by_machine = defaultdict(list)
    for entry in items_to_schedule:
        by_machine[entry["item"].machine].append(entry)

    # Get capacity config
    capacity = _load_capacity_config(base_dir)

    # Schedule each machine's items starting from start_date
    created = []
    for machine, machine_items in by_machine.items():
        m_cap = capacity.get(machine, {})
        daily_capacity = m_cap.get("available_minutes_per_day",
                                    round(DEFAULT_SHIFT_MINUTES * DEFAULT_EFFICIENCY_FACTOR))

        current_date = datetime.date.fromisoformat(start_date)
        day_used = 0

        # Account for existing entries on start date
        for e in existing_entries:
            if (e.get("machine") == machine
                    and e.get("scheduled_date") == current_date.isoformat()):
                day_used += e.get("estimated_minutes", 0)

        for item_data in machine_items:
            item = item_data["item"]
            est = item_data["est_minutes"]

            # If this item won't fit today, advance to next day
            while day_used + est > daily_capacity:
                current_date += datetime.timedelta(days=1)
                # Skip weekends
                while current_date.weekday() >= 5:
                    current_date += datetime.timedelta(days=1)
                day_used = 0
                # Check existing entries on this new date
                for e in existing_entries:
                    if (e.get("machine") == machine
                            and e.get("scheduled_date") == current_date.isoformat()):
                        day_used += e.get("estimated_minutes", 0)

            entry = add_schedule_entry(
                base_dir,
                job_code=job_code,
                work_order_id=item_data["wo_id"],
                item_id=item.item_id,
                machine=machine,
                scheduled_date=current_date.isoformat(),
                estimated_minutes=est,
                created_by=created_by,
                priority=priority,
                assigned_to=item.assigned_to,
                ship_mark=item.ship_mark,
                component_type=item.component_type,
            )
            created.append(entry)
            day_used += est

    return created


# ─────────────────────────────────────────────
# SCHEDULING ANALYTICS
# ─────────────────────────────────────────────

def get_schedule_summary(base_dir: str) -> dict:
    """Overall scheduling summary across all schedules."""
    entries = _load_entries_file(base_dir)
    schedules = _load_schedules_file(base_dir)

    today = datetime.date.today().isoformat()

    total = len(entries)
    pending = len([e for e in entries if e.get("status") == "pending"])
    in_progress = len([e for e in entries if e.get("status") == "in_progress"])
    completed = len([e for e in entries if e.get("status") == "completed"])
    skipped = len([e for e in entries if e.get("status") == "skipped"])
    overdue = len([e for e in entries
                   if e.get("status") == "pending"
                   and e.get("scheduled_date", "") < today
                   and e.get("scheduled_date", "")])

    # By machine
    by_machine = defaultdict(int)
    for e in entries:
        m = e.get("machine", "unknown")
        by_machine[m] += e.get("estimated_minutes", 0)

    # By job
    by_job = defaultdict(lambda: {"count": 0, "minutes": 0})
    for e in entries:
        jc = e.get("job_code", "UNKNOWN")
        by_job[jc]["count"] += 1
        by_job[jc]["minutes"] += e.get("estimated_minutes", 0)

    # Today's work
    today_entries = [e for e in entries if e.get("scheduled_date") == today]
    today_minutes = sum(e.get("estimated_minutes", 0) for e in today_entries)

    # This week
    week_start = datetime.date.today() - datetime.timedelta(
        days=datetime.date.today().weekday()
    )
    week_end = week_start + datetime.timedelta(days=4)
    week_entries = [e for e in entries
                    if week_start.isoformat() <= e.get("scheduled_date", "")
                    <= week_end.isoformat()]
    week_minutes = sum(e.get("estimated_minutes", 0) for e in week_entries)

    # Estimated completion dates by job
    job_completion = {}
    for e in entries:
        jc = e.get("job_code", "")
        sd = e.get("scheduled_date", "")
        if jc and sd:
            if jc not in job_completion or sd > job_completion[jc]:
                job_completion[jc] = sd

    return {
        "total_entries": total,
        "pending": pending,
        "in_progress": in_progress,
        "completed": completed,
        "skipped": skipped,
        "overdue": overdue,
        "total_schedules": len(schedules),
        "by_machine_minutes": dict(by_machine),
        "by_job": {k: dict(v) for k, v in by_job.items()},
        "today": {
            "entry_count": len(today_entries),
            "total_minutes": today_minutes,
        },
        "this_week": {
            "entry_count": len(week_entries),
            "total_minutes": week_minutes,
        },
        "job_estimated_completion": job_completion,
    }


def get_job_timeline(base_dir: str, job_code: str) -> dict:
    """Get a timeline view for a specific job showing scheduled dates per machine."""
    entries = _load_entries_file(base_dir)
    job_entries = [e for e in entries if e.get("job_code") == job_code]

    if not job_entries:
        return {"job_code": job_code, "entries": [], "machines": {},
                "start_date": "", "end_date": "", "total_minutes": 0}

    # Find date range
    dates = [e["scheduled_date"] for e in job_entries if e.get("scheduled_date")]
    start = min(dates) if dates else ""
    end = max(dates) if dates else ""

    # Group by machine
    by_machine = defaultdict(list)
    for e in job_entries:
        by_machine[e.get("machine", "unknown")].append(e)

    machine_summary = {}
    for m, m_entries in by_machine.items():
        m_dates = sorted(set(e["scheduled_date"] for e in m_entries
                             if e.get("scheduled_date")))
        total_mins = sum(e.get("estimated_minutes", 0) for e in m_entries)
        machine_summary[m] = {
            "entry_count": len(m_entries),
            "total_minutes": total_mins,
            "dates": m_dates,
            "start_date": m_dates[0] if m_dates else "",
            "end_date": m_dates[-1] if m_dates else "",
        }

    total_mins = sum(e.get("estimated_minutes", 0) for e in job_entries)

    return {
        "job_code": job_code,
        "total_entries": len(job_entries),
        "total_minutes": total_mins,
        "start_date": start,
        "end_date": end,
        "machines": machine_summary,
        "entries": [ScheduleEntry.from_dict(e).to_dict() for e in
                    sorted(job_entries, key=lambda x: (
                        x.get("scheduled_date", ""), x.get("machine", ""),
                        x.get("sequence", 0)))],
    }


def get_machine_schedule(base_dir: str, machine: str,
                         days_ahead: int = 7) -> dict:
    """Get the detailed schedule for a specific machine over N days."""
    today = datetime.date.today()
    entries = _load_entries_file(base_dir)
    capacity = _load_capacity_config(base_dir)

    m_cap = capacity.get(machine, {})
    daily_cap = m_cap.get("available_minutes_per_day",
                          round(DEFAULT_SHIFT_MINUTES * DEFAULT_EFFICIENCY_FACTOR))

    days = []
    for i in range(days_ahead):
        d = today + datetime.timedelta(days=i)
        date_str = d.isoformat()
        is_weekend = d.weekday() >= 5

        day_entries = [ScheduleEntry.from_dict(e) for e in entries
                       if e.get("machine") == machine
                       and e.get("scheduled_date") == date_str]
        day_entries.sort(key=lambda x: (x.priority, x.sequence))

        sched_mins = sum(e.estimated_minutes for e in day_entries)

        days.append({
            "date": date_str,
            "weekday": d.strftime("%A"),
            "is_weekend": is_weekend,
            "entries": [e.to_dict() for e in day_entries],
            "entry_count": len(day_entries),
            "scheduled_minutes": sched_mins,
            "available_minutes": daily_cap,
            "remaining_minutes": max(daily_cap - sched_mins, 0),
            "utilization_pct": round(sched_mins / max(daily_cap, 1) * 100, 1),
            "over_capacity": sched_mins > daily_cap,
        })

    return {
        "machine": machine,
        "label": m_cap.get("label", machine),
        "daily_capacity_minutes": daily_cap,
        "days_ahead": days_ahead,
        "days": days,
    }


def get_bottleneck_forecast(base_dir: str, days_ahead: int = 14) -> List[dict]:
    """Identify machines that are over-capacity in the upcoming schedule.

    Returns a list of bottleneck alerts with recommendations.
    """
    forecast = get_capacity_forecast(base_dir, days_ahead)
    bottlenecks = []

    for day in forecast:
        if day["is_weekend"]:
            continue
        for m_key, m_data in day["machines"].items():
            if m_data["over_capacity"]:
                bottlenecks.append({
                    "date": day["date"],
                    "weekday": day["weekday"],
                    "machine": m_key,
                    "label": m_data["label"],
                    "scheduled_minutes": m_data["scheduled_minutes"],
                    "available_minutes": m_data["available_minutes"],
                    "over_by_minutes": m_data["scheduled_minutes"] - m_data["available_minutes"],
                    "utilization_pct": m_data["utilization_pct"],
                    "recommendation": _bottleneck_recommendation(
                        m_key, m_data, day["date"]
                    ),
                })

    # Also flag high utilization (>90%) as warnings
    for day in forecast:
        if day["is_weekend"]:
            continue
        for m_key, m_data in day["machines"].items():
            if not m_data["over_capacity"] and m_data["utilization_pct"] > 90:
                bottlenecks.append({
                    "date": day["date"],
                    "weekday": day["weekday"],
                    "machine": m_key,
                    "label": m_data["label"],
                    "scheduled_minutes": m_data["scheduled_minutes"],
                    "available_minutes": m_data["available_minutes"],
                    "over_by_minutes": 0,
                    "utilization_pct": m_data["utilization_pct"],
                    "recommendation": f"{m_data['label']} at {m_data['utilization_pct']}% — consider spreading load",
                })

    bottlenecks.sort(key=lambda x: (x["date"], -x["utilization_pct"]))
    return bottlenecks


def _bottleneck_recommendation(machine: str, m_data: dict, date: str) -> str:
    """Generate a recommendation for a bottleneck."""
    over = m_data["scheduled_minutes"] - m_data["available_minutes"]
    label = m_data["label"]
    return (f"{label} is over-capacity by {over} min on {date}. "
            f"Consider moving {over} min of work to adjacent days "
            f"or adding overtime/second shift.")


def get_overdue_entries(base_dir: str) -> List[ScheduleEntry]:
    """Get all schedule entries that are past their scheduled date and still pending."""
    entries = _load_entries_file(base_dir)
    today = datetime.date.today().isoformat()

    overdue = []
    for e in entries:
        if (e.get("status") == "pending"
                and e.get("scheduled_date", "")
                and e.get("scheduled_date") < today):
            overdue.append(ScheduleEntry.from_dict(e))

    overdue.sort(key=lambda x: x.scheduled_date)
    return overdue
