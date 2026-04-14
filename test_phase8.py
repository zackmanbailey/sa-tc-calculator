#!/usr/bin/env python3
"""
TitanForge Phase 8 Tests — Scheduling & Production Planning
=============================================================
Tests scheduling data models, CRUD, capacity planning,
auto-scheduling, analytics, handlers, RBAC, and routes.
"""

import os, sys, json, shutil, tempfile, datetime

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

passed = 0
failed = 0
def test(label, condition):
    global passed, failed
    if condition:
        passed += 1
        print(f"  \u2705 {label}")
    else:
        failed += 1
        print(f"  \u274c {label}")

tmp = tempfile.mkdtemp()

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 1: Schedule Status & Priority Constants ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.scheduling import (
    SCHED_STATUSES, SCHED_STATUS_LABELS,
    SCHED_STATUS_DRAFT, SCHED_STATUS_ACTIVE,
    SCHED_STATUS_COMPLETED, SCHED_STATUS_CANCELLED,
    PRIORITY_LABELS, PRIORITY_COLORS,
    PRIORITY_URGENT, PRIORITY_HIGH, PRIORITY_NORMAL, PRIORITY_LOW,
)

test("4 schedule statuses", len(SCHED_STATUSES) == 4)
test("Draft status", SCHED_STATUS_DRAFT == "draft")
test("Active status", SCHED_STATUS_ACTIVE == "active")
test("Completed status", SCHED_STATUS_COMPLETED == "completed")
test("Cancelled status", SCHED_STATUS_CANCELLED == "cancelled")
test("All statuses have labels", all(s in SCHED_STATUS_LABELS for s in SCHED_STATUSES))
test("4 priority levels", len(PRIORITY_LABELS) == 4)
test("Urgent is 1", PRIORITY_URGENT == 1)
test("High is 2", PRIORITY_HIGH == 2)
test("Normal is 3", PRIORITY_NORMAL == 3)
test("Low is 4", PRIORITY_LOW == 4)
test("All priorities have colors", all(p in PRIORITY_COLORS for p in PRIORITY_LABELS))

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 2: ScheduleEntry Data Model ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.scheduling import ScheduleEntry

entry = ScheduleEntry(
    job_code="JOB-100",
    work_order_id="WO-001",
    item_id="ITM-C1",
    machine="WELDING",
    scheduled_date="2026-04-15",
    estimated_minutes=90,
    priority=PRIORITY_URGENT,
    ship_mark="C1",
    component_type="column",
)

test("Entry ID auto-generated", entry.entry_id.startswith("SCHED-"))
test("Entry job_code", entry.job_code == "JOB-100")
test("Entry machine", entry.machine == "WELDING")
test("Entry scheduled_date", entry.scheduled_date == "2026-04-15")
test("Entry estimated_minutes", entry.estimated_minutes == 90)
test("Entry priority", entry.priority == PRIORITY_URGENT)
test("Entry status default", entry.status == "pending")
test("Entry created_at set", entry.created_at != "")
test("priority_label property", entry.priority_label == "Urgent")
test("priority_color property", entry.priority_color == "red")

# is_overdue: past date + pending status
past_entry = ScheduleEntry(scheduled_date="2020-01-01", status="pending")
test("Past pending entry is overdue", past_entry.is_overdue)
future_entry = ScheduleEntry(scheduled_date="2099-12-31", status="pending")
test("Future pending entry not overdue", not future_entry.is_overdue)
done_entry = ScheduleEntry(scheduled_date="2020-01-01", status="completed")
test("Completed entry not overdue", not done_entry.is_overdue)

# to_dict / from_dict
d = entry.to_dict()
test("to_dict has entry_id", "entry_id" in d)
test("to_dict has machine", d["machine"] == "WELDING")
entry2 = ScheduleEntry.from_dict(d)
test("from_dict roundtrip entry_id", entry2.entry_id == entry.entry_id)
test("from_dict roundtrip machine", entry2.machine == "WELDING")
test("from_dict roundtrip priority", entry2.priority == PRIORITY_URGENT)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 3: ProductionSchedule Data Model ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.scheduling import ProductionSchedule

ps = ProductionSchedule(
    name="Week 16 Schedule",
    start_date="2026-04-13",
    end_date="2026-04-17",
    created_by="foreman1",
    job_codes=["JOB-100", "JOB-200"],
)

test("Schedule ID auto-generated", ps.schedule_id.startswith("PS-"))
test("Schedule name", ps.name == "Week 16 Schedule")
test("Schedule status default draft", ps.status == SCHED_STATUS_DRAFT)
test("Schedule created_at set", ps.created_at != "")
test("Schedule job_codes", ps.job_codes == ["JOB-100", "JOB-200"])
test("status_label property", ps.status_label == "Draft")

d2 = ps.to_dict()
test("ProductionSchedule to_dict", d2["name"] == "Week 16 Schedule")
ps2 = ProductionSchedule.from_dict(d2)
test("ProductionSchedule from_dict roundtrip", ps2.schedule_id == ps.schedule_id)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 4: Machine Capacity Configuration ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.scheduling import (
    get_machine_capacity, update_machine_capacity,
    DEFAULT_SHIFT_HOURS, DEFAULT_EFFICIENCY_FACTOR,
    _default_machine_capacity,
)
from shop_drawings.work_orders import MACHINE_TYPES

cap = get_machine_capacity(tmp)
test("Capacity has all machines", all(m in cap for m in MACHINE_TYPES))
test("WELDING capacity exists", "WELDING" in cap)
test("Default shift hours", cap["WELDING"]["shift_hours"] == DEFAULT_SHIFT_HOURS)
test("Default efficiency", cap["WELDING"]["efficiency_factor"] == DEFAULT_EFFICIENCY_FACTOR)
test("Available minutes calculated",
     cap["WELDING"]["available_minutes_per_day"] == round(DEFAULT_SHIFT_HOURS * 60 * DEFAULT_EFFICIENCY_FACTOR))
test("Machine enabled by default", cap["WELDING"]["enabled"] is True)

# Update capacity
updated = update_machine_capacity(tmp, "WELDING", shift_hours=12, shifts_per_day=2)
test("Update returns dict", updated is not None)
test("Updated shift hours", updated["shift_hours"] == 12)
test("Updated shifts_per_day", updated["shifts_per_day"] == 2)
test("Recalculated available minutes",
     updated["available_minutes_per_day"] == round(12 * 60 * 2 * DEFAULT_EFFICIENCY_FACTOR))

# Update non-existent machine
bad = update_machine_capacity(tmp, "NONEXISTENT", shift_hours=8)
test("Update bad machine returns None", bad is None)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 5: Schedule CRUD ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.scheduling import (
    create_schedule, get_schedule, list_schedules,
    update_schedule, delete_schedule,
)

s1 = create_schedule(tmp, "Week 16", "2026-04-13", "2026-04-17",
                     created_by="pm1", job_codes=["JOB-100"])
test("Create schedule returns PS", isinstance(s1, ProductionSchedule))
test("Schedule ID set", s1.schedule_id.startswith("PS-"))
test("Schedule name", s1.name == "Week 16")

s2 = create_schedule(tmp, "Rush Order", "2026-04-14", "2026-04-15",
                     created_by="pm1", description="Emergency schedule")
test("Second schedule created", s2.schedule_id != s1.schedule_id)

# List
all_sched = list_schedules(tmp)
test("2 schedules listed", len(all_sched) == 2)

# Get
fetched = get_schedule(tmp, s1.schedule_id)
test("Get schedule by ID", fetched is not None)
test("Fetched name matches", fetched.name == "Week 16")

# Update
updated_s = update_schedule(tmp, s1.schedule_id, status=SCHED_STATUS_ACTIVE)
test("Update schedule returns PS", updated_s is not None)
test("Status updated to active", updated_s.status == SCHED_STATUS_ACTIVE)

# Update non-existent
bad_u = update_schedule(tmp, "PS-NONEXIST", name="Bad")
test("Update bad schedule returns None", bad_u is None)

# Delete
ok = delete_schedule(tmp, s2.schedule_id)
test("Delete schedule ok", ok is True)
test("1 schedule remaining", len(list_schedules(tmp)) == 1)

# Delete non-existent
bad_d = delete_schedule(tmp, "PS-NONEXIST")
test("Delete bad schedule fails", bad_d is False)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 6: Schedule Entry CRUD ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.scheduling import (
    add_schedule_entry, get_schedule_entry,
    update_schedule_entry, delete_schedule_entry,
)

e1 = add_schedule_entry(tmp, "JOB-100", "WO-001", "ITM-C1", "WELDING",
                        "2026-04-15", 90, "foreman1",
                        priority=PRIORITY_HIGH, ship_mark="C1",
                        component_type="column")
test("Entry created", isinstance(e1, ScheduleEntry))
test("Entry ID set", e1.entry_id.startswith("SCHED-"))
test("Entry sequence auto-set", e1.sequence == 1)

e2 = add_schedule_entry(tmp, "JOB-100", "WO-001", "ITM-C2", "WELDING",
                        "2026-04-15", 60, "foreman1",
                        ship_mark="C2", component_type="column")
test("Second entry sequence incremented", e2.sequence == 2)

# Get
fetched_e = get_schedule_entry(tmp, e1.entry_id)
test("Get entry by ID", fetched_e is not None)
test("Fetched entry machine", fetched_e.machine == "WELDING")

# Update
updated_e = update_schedule_entry(tmp, e1.entry_id,
                                   status="in_progress", assigned_to="welder1")
test("Update entry returns ScheduleEntry", updated_e is not None)
test("Entry status updated", updated_e.status == "in_progress")
test("Entry assigned_to updated", updated_e.assigned_to == "welder1")
test("Entry updated_at set", updated_e.updated_at != "")

# Update non-existent
bad_ue = update_schedule_entry(tmp, "SCHED-NONE", status="completed")
test("Update bad entry returns None", bad_ue is None)

# Delete
ok_de = delete_schedule_entry(tmp, e2.entry_id)
test("Delete entry ok", ok_de is True)
bad_de = delete_schedule_entry(tmp, "SCHED-NONE")
test("Delete bad entry fails", bad_de is False)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 7: Query Entries by Date and Range ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.scheduling import (
    get_entries_for_date, get_entries_for_range, get_entries_for_job,
)

# Add more entries across dates
add_schedule_entry(tmp, "JOB-100", "WO-001", "ITM-R1", "WELDING",
                   "2026-04-16", 120, "foreman1", ship_mark="R1")
add_schedule_entry(tmp, "JOB-200", "WO-002", "ITM-P1", "Z1",
                   "2026-04-15", 45, "foreman1", ship_mark="P1")
add_schedule_entry(tmp, "JOB-200", "WO-002", "ITM-P2", "Z1",
                   "2026-04-16", 45, "foreman1", ship_mark="P2")

# By date
day_entries = get_entries_for_date(tmp, "2026-04-15")
test("Date query returns 2 entries for 4/15", len(day_entries) == 2)

# By date + machine filter
welding_entries = get_entries_for_date(tmp, "2026-04-15", machine="WELDING")
test("Date+machine filter: 1 WELDING on 4/15", len(welding_entries) == 1)

z1_entries = get_entries_for_date(tmp, "2026-04-15", machine="Z1")
test("Date+machine filter: 1 Z1 on 4/15", len(z1_entries) == 1)

# By range
range_entries = get_entries_for_range(tmp, "2026-04-15", "2026-04-16")
test("Range query 4/15-4/16: 4 entries", len(range_entries) == 4)

range_welding = get_entries_for_range(tmp, "2026-04-15", "2026-04-16", machine="WELDING")
test("Range+machine WELDING: 2 entries", len(range_welding) == 2)

range_job = get_entries_for_range(tmp, "2026-04-15", "2026-04-16", job_code="JOB-200")
test("Range+job JOB-200: 2 entries", len(range_job) == 2)

# By job
job_entries = get_entries_for_job(tmp, "JOB-100")
test("Job query JOB-100: 2 entries", len(job_entries) == 2)

job_entries_200 = get_entries_for_job(tmp, "JOB-200")
test("Job query JOB-200: 2 entries", len(job_entries_200) == 2)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 8: Daily Capacity Usage ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.scheduling import get_daily_capacity_usage

usage = get_daily_capacity_usage(tmp, "2026-04-15")
test("Usage has WELDING", "WELDING" in usage)
test("Usage has Z1", "Z1" in usage)

# WELDING on 4/15: e1 was updated to in_progress but is still 90 min
test("WELDING scheduled minutes > 0", usage["WELDING"]["scheduled_minutes"] > 0)
test("WELDING has entry_count", usage["WELDING"]["entry_count"] >= 1)
test("WELDING has remaining_minutes", usage["WELDING"]["remaining_minutes"] >= 0)
test("WELDING has utilization_pct", usage["WELDING"]["utilization_pct"] >= 0)

# Z1 on 4/15: 45 min
test("Z1 scheduled 45 min", usage["Z1"]["scheduled_minutes"] == 45)
test("Z1 entry_count 1", usage["Z1"]["entry_count"] == 1)

# Empty date
usage_empty = get_daily_capacity_usage(tmp, "2099-01-01")
test("Empty date: 0 scheduled", all(m["scheduled_minutes"] == 0 for m in usage_empty.values()))


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 9: Capacity Forecast ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.scheduling import get_capacity_forecast

forecast = get_capacity_forecast(tmp, days_ahead=7)
test("Forecast has 7 days", len(forecast) == 7)
test("Each day has date", all("date" in d for d in forecast))
test("Each day has weekday", all("weekday" in d for d in forecast))
test("Each day has machines", all("machines" in d for d in forecast))
test("Each day has overall utilization", all("overall_utilization_pct" in d for d in forecast))
test("Each day has entry_count", all("entry_count" in d for d in forecast))

# Check that the day with our entries shows utilization > 0
# Note: dates are relative to today so we just check structure
first_day = forecast[0]
test("First day has total_available_minutes", first_day["total_available_minutes"] > 0)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 10: Schedule Summary ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.scheduling import get_schedule_summary

summary = get_schedule_summary(tmp)
test("Summary total_entries >= 4", summary["total_entries"] >= 4)
test("Summary has pending count", "pending" in summary)
test("Summary has in_progress count", "in_progress" in summary)
test("Summary has completed count", "completed" in summary)
test("Summary has overdue count", "overdue" in summary)
test("Summary has by_machine_minutes", "by_machine_minutes" in summary)
test("Summary has by_job", "by_job" in summary)
test("Summary has today", "today" in summary)
test("Summary has this_week", "this_week" in summary)
test("Summary by_job has JOB-100", "JOB-100" in summary["by_job"])
test("Summary by_job has JOB-200", "JOB-200" in summary["by_job"])
test("Summary job_estimated_completion", "job_estimated_completion" in summary)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 11: Job Timeline ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.scheduling import get_job_timeline

timeline = get_job_timeline(tmp, "JOB-100")
test("Timeline job_code", timeline["job_code"] == "JOB-100")
test("Timeline total_entries >= 2", timeline["total_entries"] >= 2)
test("Timeline has machines", "machines" in timeline)
test("Timeline has WELDING", "WELDING" in timeline["machines"])
test("Timeline WELDING has dates", len(timeline["machines"]["WELDING"]["dates"]) >= 1)
test("Timeline has start_date", timeline["start_date"] != "")
test("Timeline has end_date", timeline["end_date"] != "")
test("Timeline has entries list", len(timeline["entries"]) >= 2)

# Empty job
empty_tl = get_job_timeline(tmp, "JOB-NONE")
test("Empty job timeline", len(empty_tl["entries"]) == 0)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 12: Machine Schedule ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.scheduling import get_machine_schedule

ms = get_machine_schedule(tmp, "WELDING", days_ahead=5)
test("Machine schedule has machine", ms["machine"] == "WELDING")
test("Machine schedule has label", ms["label"] != "")
test("Machine schedule has 5 days", len(ms["days"]) == 5)
test("Each day has entries list", all("entries" in d for d in ms["days"]))
test("Each day has utilization_pct", all("utilization_pct" in d for d in ms["days"]))
test("Each day has over_capacity flag", all("over_capacity" in d for d in ms["days"]))


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 13: Bottleneck Forecast ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.scheduling import get_bottleneck_forecast

# First let's create an over-capacity situation
# WELDING was updated to 12h * 2 shifts * 0.8 = 1152 min
# Add enough entries on one day to exceed
for i in range(15):
    add_schedule_entry(tmp, "JOB-STRESS", "WO-S", f"ITM-S{i}", "WELDING",
                       "2026-04-20", 100, "foreman1")

bottlenecks = get_bottleneck_forecast(tmp, days_ahead=14)
test("Bottleneck list is list", isinstance(bottlenecks, list))

# Find our over-capacity day
bn_dates = [b["date"] for b in bottlenecks if b.get("over_by_minutes", 0) > 0]
test("Over-capacity detected on 2026-04-20", "2026-04-20" in bn_dates)

if bottlenecks:
    bn = bottlenecks[0]
    test("Bottleneck has date", "date" in bn)
    test("Bottleneck has machine", "machine" in bn)
    test("Bottleneck has recommendation", "recommendation" in bn)
    test("Bottleneck has utilization_pct", "utilization_pct" in bn)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 14: Overdue Entries ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.scheduling import get_overdue_entries

# Add a past-date pending entry
add_schedule_entry(tmp, "JOB-OLD", "WO-OLD", "ITM-OLD", "BRAKE",
                   "2020-01-01", 30, "foreman1")

overdue = get_overdue_entries(tmp)
test("Overdue list is list", isinstance(overdue, list))
test("At least 1 overdue entry", len(overdue) >= 1)
test("Overdue entry is past date", overdue[0].scheduled_date < datetime.date.today().isoformat())
test("Overdue entry is pending", overdue[0].status == "pending")


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 15: Auto-Schedule Engine ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.scheduling import auto_schedule_job, _estimate_item_minutes
from shop_drawings.work_orders import (
    WorkOrder, WorkOrderItem, save_work_order,
    STATUS_QUEUED, STATUS_APPROVED, STATUS_IN_PROGRESS,
)

# Create a fresh tmp for auto-schedule testing
tmp2 = tempfile.mkdtemp()
wo_base = os.path.join(tmp2, "shop_drawings")
os.makedirs(os.path.join(wo_base, "JOB-AUTO", "work_orders"), exist_ok=True)

# Create a WO with items in schedulable statuses
wo = WorkOrder(
    work_order_id="WO-AUTO-1",
    job_code="JOB-AUTO",
    created_by="pm1",
)
wo.items = [
    WorkOrderItem(item_id="A1", ship_mark="C1", component_type="column",
                  machine="WELDING", status=STATUS_QUEUED, priority=50),
    WorkOrderItem(item_id="A2", ship_mark="C2", component_type="column",
                  machine="WELDING", status=STATUS_APPROVED, priority=50),
    WorkOrderItem(item_id="A3", ship_mark="P1", component_type="purlin",
                  machine="Z1", status=STATUS_QUEUED, priority=50),
    WorkOrderItem(item_id="A4", ship_mark="R1", component_type="rafter",
                  machine="WELDING", status=STATUS_IN_PROGRESS, priority=50),  # Not schedulable
]
save_work_order(wo_base, wo)

# Test _estimate_item_minutes
test_item = WorkOrderItem(component_type="column", duration_minutes=45)
test("Estimate uses duration_minutes when set", _estimate_item_minutes(test_item) == 45)

test_item2 = WorkOrderItem(component_type="column", duration_minutes=0)
est = _estimate_item_minutes(test_item2, wo_base, "JOB-AUTO")
test("Estimate from fab steps > 0", est > 0)

# Run auto-schedule
entries = auto_schedule_job(tmp2, wo_base, "JOB-AUTO", "2026-04-21", "foreman1")
test("Auto-schedule created entries", len(entries) >= 2)  # A1, A2, A3 (not A4)
test("Auto-schedule skipped in_progress item",
     not any(e.item_id == "A4" for e in entries))
test("Auto-schedule included queued items",
     any(e.item_id == "A1" for e in entries))
test("Auto-schedule included approved items",
     any(e.item_id == "A2" for e in entries))

# All entries should have scheduled_date >= start_date
test("All entries on or after start_date",
     all(e.scheduled_date >= "2026-04-21" for e in entries))

# Running again should not create duplicates
entries2 = auto_schedule_job(tmp2, wo_base, "JOB-AUTO", "2026-04-21", "foreman1")
test("Re-run auto-schedule: 0 new entries (already scheduled)", len(entries2) == 0)

# Cleanup
shutil.rmtree(tmp2, ignore_errors=True)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 16: Schedule + Entries Linked Deletion ══")
# ═══════════════════════════════════════════════════════════════════

tmp3 = tempfile.mkdtemp()
from shop_drawings.scheduling import _load_entries_file

sched = create_schedule(tmp3, "DeleteTest", "2026-04-20", "2026-04-22", "pm1")
add_schedule_entry(tmp3, "JOB-X", "WO-X", "ITM-X1", "WELDING", "2026-04-20",
                   60, "pm1", schedule_id=sched.schedule_id)
add_schedule_entry(tmp3, "JOB-X", "WO-X", "ITM-X2", "WELDING", "2026-04-21",
                   60, "pm1", schedule_id=sched.schedule_id)

test("2 entries before delete", len(_load_entries_file(tmp3)) == 2)

delete_schedule(tmp3, sched.schedule_id)
test("0 schedules after delete", len(list_schedules(tmp3)) == 0)
test("0 entries after schedule delete", len(_load_entries_file(tmp3)) == 0)

shutil.rmtree(tmp3, ignore_errors=True)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 17: RBAC Permissions ══")
# ═══════════════════════════════════════════════════════════════════

from auth.roles import P, ROLES

test("MANAGE_SCHEDULE permission exists", hasattr(P, "MANAGE_SCHEDULE"))
test("VIEW_SCHEDULE permission exists", hasattr(P, "VIEW_SCHEDULE"))
test("MANAGE_SCHEDULE value", P.MANAGE_SCHEDULE == "manage_schedule")
test("VIEW_SCHEDULE value", P.VIEW_SCHEDULE == "view_schedule")

# Check roles with manage_schedule
manage_roles = [r for r, rd in ROLES.items() if P.MANAGE_SCHEDULE in rd.permissions]
test("god_mode has manage_schedule", "god_mode" in manage_roles)
test("admin has manage_schedule", "admin" in manage_roles)
test("project_manager has manage_schedule", "project_manager" in manage_roles)
test("shop_foreman has manage_schedule", "shop_foreman" in manage_roles)

# Check roles with view_schedule
view_roles = [r for r, rd in ROLES.items() if P.VIEW_SCHEDULE in rd.permissions]
test("god_mode has view_schedule", "god_mode" in view_roles)
test("admin has view_schedule", "admin" in view_roles)
test("project_manager has view_schedule", "project_manager" in view_roles)
test("shop_foreman has view_schedule", "shop_foreman" in view_roles)
test("welder has view_schedule", "welder" in view_roles)
test("roll_forming_operator has view_schedule", "roll_forming_operator" in view_roles)
test("shipping_coordinator has view_schedule", "shipping_coordinator" in view_roles)

# Roles that should NOT have manage_schedule
test("welder does NOT have manage_schedule", "welder" not in manage_roles)
test("laborer does NOT have manage_schedule", "laborer" not in manage_roles)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 18: Handler Classes Exist ══")
# ═══════════════════════════════════════════════════════════════════

import tf_handlers as tfh

handler_classes = [
    "ProductionSchedulePageHandler",
    "ScheduleListAPIHandler",
    "ScheduleCreateHandler",
    "ScheduleUpdateHandler",
    "ScheduleDeleteHandler",
    "ScheduleEntryAddHandler",
    "ScheduleEntryUpdateHandler",
    "ScheduleEntryDeleteHandler",
    "ScheduleDateAPIHandler",
    "ScheduleRangeAPIHandler",
    "CapacityAPIHandler",
    "CapacityUpdateHandler",
    "CapacityUsageAPIHandler",
    "CapacityForecastAPIHandler",
    "AutoScheduleHandler",
    "ScheduleSummaryAPIHandler",
    "JobTimelineAPIHandler",
    "MachineScheduleAPIHandler",
    "BottleneckForecastAPIHandler",
    "OverdueEntriesAPIHandler",
    "ScheduleConfigHandler",
]

for cls_name in handler_classes:
    test(f"{cls_name} exists", hasattr(tfh, cls_name))

for cls_name in handler_classes:
    cls = getattr(tfh, cls_name, None)
    if cls:
        test(f"{cls_name} is BaseHandler subclass",
             issubclass(cls, tfh.BaseHandler))


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 19: Handler RBAC Permissions ══")
# ═══════════════════════════════════════════════════════════════════

# manage_schedule handlers
manage_handlers = [
    "ScheduleCreateHandler",
    "ScheduleUpdateHandler",
    "ScheduleDeleteHandler",
    "ScheduleEntryAddHandler",
    "ScheduleEntryUpdateHandler",
    "ScheduleEntryDeleteHandler",
    "CapacityUpdateHandler",
    "AutoScheduleHandler",
]
for cls_name in manage_handlers:
    cls = getattr(tfh, cls_name, None)
    if cls:
        test(f"{cls_name} requires manage_schedule",
             cls.required_permission == "manage_schedule")

# view_schedule handlers
view_handlers = [
    "ProductionSchedulePageHandler",
    "ScheduleListAPIHandler",
    "ScheduleDateAPIHandler",
    "ScheduleRangeAPIHandler",
    "CapacityAPIHandler",
    "CapacityUsageAPIHandler",
    "CapacityForecastAPIHandler",
    "ScheduleSummaryAPIHandler",
    "JobTimelineAPIHandler",
    "MachineScheduleAPIHandler",
    "BottleneckForecastAPIHandler",
    "OverdueEntriesAPIHandler",
    "ScheduleConfigHandler",
]
for cls_name in view_handlers:
    cls = getattr(tfh, cls_name, None)
    if cls:
        test(f"{cls_name} requires view_schedule",
             cls.required_permission == "view_schedule")


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 20: Route Table ══")
# ═══════════════════════════════════════════════════════════════════

routes = tfh.get_routes()
route_map = {}
for entry in routes:
    if len(entry) >= 2:
        route_map[entry[0]] = entry[1]

expected_routes = {
    r"/schedule":                        "ProductionSchedulePageHandler",
    r"/api/schedule/list":               "ScheduleListAPIHandler",
    r"/api/schedule/create":             "ScheduleCreateHandler",
    r"/api/schedule/update":             "ScheduleUpdateHandler",
    r"/api/schedule/delete":             "ScheduleDeleteHandler",
    r"/api/schedule/entry/add":          "ScheduleEntryAddHandler",
    r"/api/schedule/entry/update":       "ScheduleEntryUpdateHandler",
    r"/api/schedule/entry/delete":       "ScheduleEntryDeleteHandler",
    r"/api/schedule/date":               "ScheduleDateAPIHandler",
    r"/api/schedule/range":              "ScheduleRangeAPIHandler",
    r"/api/schedule/capacity":           "CapacityAPIHandler",
    r"/api/schedule/capacity/update":    "CapacityUpdateHandler",
    r"/api/schedule/capacity/usage":     "CapacityUsageAPIHandler",
    r"/api/schedule/capacity/forecast":  "CapacityForecastAPIHandler",
    r"/api/schedule/auto":               "AutoScheduleHandler",
    r"/api/schedule/summary":            "ScheduleSummaryAPIHandler",
    r"/api/schedule/job-timeline":       "JobTimelineAPIHandler",
    r"/api/schedule/machine":            "MachineScheduleAPIHandler",
    r"/api/schedule/bottlenecks":        "BottleneckForecastAPIHandler",
    r"/api/schedule/overdue":            "OverdueEntriesAPIHandler",
    r"/api/schedule/config":             "ScheduleConfigHandler",
}

for pattern, expected in expected_routes.items():
    handler = route_map.get(pattern)
    handler_name = handler.__name__ if handler else "NOT FOUND"
    test(f"Route {pattern} → {expected}", handler_name == expected)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 21: Template File ══")
# ═══════════════════════════════════════════════════════════════════

from templates.production_schedule_page import PRODUCTION_SCHEDULE_PAGE_HTML

test("Schedule template exists", isinstance(PRODUCTION_SCHEDULE_PAGE_HTML, str))
test("Schedule template is HTML", "<!DOCTYPE html>" in PRODUCTION_SCHEDULE_PAGE_HTML)
test("Schedule template has title", "Production Schedule" in PRODUCTION_SCHEDULE_PAGE_HTML)
test("Schedule template has capacity API", "/api/schedule/capacity" in PRODUCTION_SCHEDULE_PAGE_HTML)
test("Schedule template has date API", "/api/schedule/date" in PRODUCTION_SCHEDULE_PAGE_HTML)
test("Schedule template has summary API", "/api/schedule/summary" in PRODUCTION_SCHEDULE_PAGE_HTML)
test("Schedule template has bottleneck API", "/api/schedule/bottlenecks" in PRODUCTION_SCHEDULE_PAGE_HTML)
test("Schedule template has overdue API", "/api/schedule/overdue" in PRODUCTION_SCHEDULE_PAGE_HTML)
test("Schedule template has capacity grid", "capacityGrid" in PRODUCTION_SCHEDULE_PAGE_HTML)
test("Schedule template has day schedule", "daySchedule" in PRODUCTION_SCHEDULE_PAGE_HTML)
test("Schedule template links to shop-floor", "/shop-floor" in PRODUCTION_SCHEDULE_PAGE_HTML)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 22: Full E2E — Create, Schedule, Query, Forecast ══")
# ═══════════════════════════════════════════════════════════════════

tmp4 = tempfile.mkdtemp()

# 1. Create a schedule
sched_e2e = create_schedule(tmp4, "E2E Test", "2026-04-21", "2026-04-25",
                            created_by="pm_zack", job_codes=["JOB-E2E"])

# 2. Add entries
for i in range(5):
    add_schedule_entry(
        tmp4, "JOB-E2E", "WO-E2E", f"ITM-E{i+1}", "WELDING",
        f"2026-04-{21+i}", 90, "pm_zack",
        priority=PRIORITY_NORMAL if i > 0 else PRIORITY_URGENT,
        ship_mark=f"C{i+1}",
        component_type="column",
        schedule_id=sched_e2e.schedule_id,
    )
add_schedule_entry(
    tmp4, "JOB-E2E", "WO-E2E", "ITM-P1", "Z1",
    "2026-04-21", 60, "pm_zack",
    ship_mark="PG-A1", component_type="purlin",
    schedule_id=sched_e2e.schedule_id,
)

# 3. Verify summary
s_e2e = get_schedule_summary(tmp4)
test("E2E: 6 entries total", s_e2e["total_entries"] == 6)
test("E2E: by_job has JOB-E2E", "JOB-E2E" in s_e2e["by_job"])

# 4. Verify timeline
tl_e2e = get_job_timeline(tmp4, "JOB-E2E")
test("E2E: timeline 6 entries", tl_e2e["total_entries"] == 6)
test("E2E: timeline has WELDING", "WELDING" in tl_e2e["machines"])
test("E2E: timeline has Z1", "Z1" in tl_e2e["machines"])

# 5. Verify capacity usage on 4/21 (90 WELDING + 60 Z1)
usage_e2e = get_daily_capacity_usage(tmp4, "2026-04-21")
test("E2E: WELDING 90 min on 4/21", usage_e2e["WELDING"]["scheduled_minutes"] == 90)
test("E2E: Z1 60 min on 4/21", usage_e2e["Z1"]["scheduled_minutes"] == 60)

# 6. Verify date query with priority sorting
day_e2e = get_entries_for_date(tmp4, "2026-04-21")
test("E2E: 2 entries on 4/21", len(day_e2e) == 2)
# Urgent (priority 1) should come before Normal (priority 3)
test("E2E: urgent entry first", day_e2e[0].priority == PRIORITY_URGENT)

# 7. Activate schedule
update_schedule(tmp4, sched_e2e.schedule_id, status=SCHED_STATUS_ACTIVE)
active_sched = get_schedule(tmp4, sched_e2e.schedule_id)
test("E2E: schedule now active", active_sched.status == SCHED_STATUS_ACTIVE)

# 8. Forecast
fc = get_capacity_forecast(tmp4, days_ahead=14)
test("E2E: forecast has 14 days", len(fc) == 14)

# Cleanup
shutil.rmtree(tmp4, ignore_errors=True)
shutil.rmtree(tmp, ignore_errors=True)

# ═══════════════════════════════════════════════════════════════════
print(f"\n{'='*60}")
print(f"Phase 8 Results: {passed} passed, {failed} failed, {passed+failed} total")
print(f"{'='*60}")

if failed > 0:
    sys.exit(1)
