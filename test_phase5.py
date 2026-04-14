#!/usr/bin/env python3
"""
TitanForge Phase 5 — Field Operations & Installation Tests
Tests punch list lifecycle, daily reports, installation confirmation,
project completion tracking, handler RBAC, route table, and templates.
"""

import sys, os, json, tempfile, shutil, datetime, secrets
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

passed = 0
failed = 0

def test(name, condition):
    global passed, failed
    if condition:
        print(f"  ✅ {name}")
        passed += 1
    else:
        print(f"  ❌ {name}")
        failed += 1


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 1: Punch List Constants ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.field_ops import (
    PUNCH_STATUS_OPEN, PUNCH_STATUS_IN_PROGRESS,
    PUNCH_STATUS_RESOLVED, PUNCH_STATUS_VERIFIED, PUNCH_STATUS_DEFERRED,
    PUNCH_STATUSES, PUNCH_STATUS_LABELS, PUNCH_STATUS_COLORS, PUNCH_FLOW,
    PUNCH_PRIORITIES, PUNCH_CATEGORIES, PUNCH_CATEGORY_LABELS,
    PUNCH_PRIORITY_CRITICAL, PUNCH_PRIORITY_HIGH,
    PUNCH_PRIORITY_MEDIUM, PUNCH_PRIORITY_LOW,
)

test("5 punch statuses", len(PUNCH_STATUSES) == 5)
test("open status", PUNCH_STATUS_OPEN == "open")
test("in_progress status", PUNCH_STATUS_IN_PROGRESS == "in_progress")
test("resolved status", PUNCH_STATUS_RESOLVED == "resolved")
test("verified status", PUNCH_STATUS_VERIFIED == "verified")
test("deferred status", PUNCH_STATUS_DEFERRED == "deferred")

test("All statuses have labels", all(s in PUNCH_STATUS_LABELS for s in PUNCH_STATUSES))
test("All statuses have colors", all(s in PUNCH_STATUS_COLORS for s in PUNCH_STATUSES))
test("All statuses in PUNCH_FLOW", all(s in PUNCH_FLOW for s in PUNCH_STATUSES))

test("verified is terminal", PUNCH_FLOW[PUNCH_STATUS_VERIFIED] == [])
test("open → in_progress allowed", PUNCH_STATUS_IN_PROGRESS in PUNCH_FLOW[PUNCH_STATUS_OPEN])
test("open → deferred allowed", PUNCH_STATUS_DEFERRED in PUNCH_FLOW[PUNCH_STATUS_OPEN])
test("resolved → verified allowed", PUNCH_STATUS_VERIFIED in PUNCH_FLOW[PUNCH_STATUS_RESOLVED])
test("deferred → open (reopen)", PUNCH_STATUS_OPEN in PUNCH_FLOW[PUNCH_STATUS_DEFERRED])

test("4 priorities", len(PUNCH_PRIORITIES) == 4)
test("critical priority", PUNCH_PRIORITY_CRITICAL == "critical")
test("8 categories", len(PUNCH_CATEGORIES) == 8)
test("All categories have labels", all(c in PUNCH_CATEGORY_LABELS for c in PUNCH_CATEGORIES))


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 2: PunchListItem Data Model ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.field_ops import PunchListItem

p = PunchListItem(
    punch_id="PUNCH-20260414-ABC123", job_code="JOB-500",
    item_id="ITM-C1", ship_mark="C1", load_id="LOAD-001",
    status=PUNCH_STATUS_OPEN, priority=PUNCH_PRIORITY_HIGH,
    category="damaged", title="Column C1 bent on delivery",
    description="Visible bend near base plate", location="Grid A-3",
    created_by="field_lead", created_at="2026-04-14T10:00:00",
)

test("PunchListItem punch_id", p.punch_id == "PUNCH-20260414-ABC123")
test("PunchListItem status", p.status == PUNCH_STATUS_OPEN)
test("PunchListItem priority", p.priority == PUNCH_PRIORITY_HIGH)
test("PunchListItem category", p.category == "damaged")
test("status_label", p.status_label == "Open")
test("status_color", p.status_color == "red")
test("priority_label", p.priority_label == "High")
test("category_label", p.category_label == "Damaged")
test("can_transition open → in_progress", p.can_transition_to(PUNCH_STATUS_IN_PROGRESS))
test("cannot transition open → verified", not p.can_transition_to(PUNCH_STATUS_VERIFIED))

# Round-trip
d = p.to_dict()
test("to_dict has all keys", all(k in d for k in ["punch_id", "job_code", "status", "priority", "category", "title", "description"]))
p2 = PunchListItem.from_dict(d)
test("from_dict round-trip punch_id", p2.punch_id == p.punch_id)
test("from_dict round-trip title", p2.title == p.title)
test("from_dict round-trip location", p2.location == "Grid A-3")


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 3: DailyFieldReport Data Model ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.field_ops import DailyFieldReport

r = DailyFieldReport(
    report_id="DFR-20260414-ABC", job_code="JOB-500",
    date="2026-04-14", submitted_by="field_lead",
    crew_count=4, hours_worked=8.5,
    work_summary="Installed columns A1-A4",
    weather="sunny", temperature_f=78.0,
    items_installed=["ITM-A1", "ITM-A2"],
)
test("DailyFieldReport report_id", r.report_id == "DFR-20260414-ABC")
test("DailyFieldReport crew_count", r.crew_count == 4)
test("DailyFieldReport items_installed", len(r.items_installed) == 2)

d = r.to_dict()
test("to_dict has work_summary", d["work_summary"] == "Installed columns A1-A4")
r2 = DailyFieldReport.from_dict(d)
test("from_dict round-trip weather", r2.weather == "sunny")
test("from_dict round-trip hours", r2.hours_worked == 8.5)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 4: InstallationRecord Data Model ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.field_ops import InstallationRecord

ir = InstallationRecord(
    record_id="INST-20260414-ABC", job_code="JOB-500",
    item_id="ITM-C1", ship_mark="C1",
    installed_by="crew_mike", installed_at="2026-04-14T14:30:00",
    location="Grid A-3", notes="Bolted and torqued",
)
test("InstallationRecord record_id", ir.record_id == "INST-20260414-ABC")
test("InstallationRecord item_id", ir.item_id == "ITM-C1")

d = ir.to_dict()
test("to_dict has location", d["location"] == "Grid A-3")
ir2 = InstallationRecord.from_dict(d)
test("from_dict round-trip installed_by", ir2.installed_by == "crew_mike")


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 5: Punch List Storage ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.field_ops import (
    save_punch_item, load_punch_items, load_punch_item, load_all_punch_items,
)

TEST_DIR = tempfile.mkdtemp(prefix="tf_field_test_")

# Save and load
save_punch_item(TEST_DIR, "JOB-500", p)
items = load_punch_items(TEST_DIR, "JOB-500")
test("Saved punch item persists", len(items) == 1)
test("Loaded punch_id matches", items[0].punch_id == p.punch_id)

# Load specific
loaded = load_punch_item(TEST_DIR, "JOB-500", p.punch_id)
test("load_punch_item returns correct item", loaded is not None and loaded.punch_id == p.punch_id)
test("load_punch_item not found", load_punch_item(TEST_DIR, "JOB-500", "NONEXIST") is None)

# Filter by status
open_items = load_punch_items(TEST_DIR, "JOB-500", status=PUNCH_STATUS_OPEN)
test("Filter by status open: 1 item", len(open_items) == 1)
resolved_items = load_punch_items(TEST_DIR, "JOB-500", status=PUNCH_STATUS_RESOLVED)
test("Filter by status resolved: 0 items", len(resolved_items) == 0)

# Save second item in different project
p2_item = PunchListItem(punch_id="PUNCH-002", job_code="JOB-600", title="Missing bolt")
save_punch_item(TEST_DIR, "JOB-600", p2_item)
all_punches = load_all_punch_items(TEST_DIR)
test("load_all_punch_items returns 2", len(all_punches) == 2)

# Update existing item
p.assigned_to = "crew_bob"
save_punch_item(TEST_DIR, "JOB-500", p)
items = load_punch_items(TEST_DIR, "JOB-500")
test("Update doesn't duplicate", len(items) == 1)
test("Updated assigned_to", items[0].assigned_to == "crew_bob")

shutil.rmtree(TEST_DIR)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 6: Daily Report & Installation Record Storage ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.field_ops import (
    save_daily_report, load_daily_reports,
    save_installation_record, load_installation_records,
)

TEST_DIR = tempfile.mkdtemp(prefix="tf_field_test_")

save_daily_report(TEST_DIR, "JOB-500", r)
reports = load_daily_reports(TEST_DIR, "JOB-500")
test("Daily report persists", len(reports) == 1)
test("Report id matches", reports[0].report_id == r.report_id)

save_installation_record(TEST_DIR, "JOB-500", ir)
records = load_installation_records(TEST_DIR, "JOB-500")
test("Install record persists", len(records) == 1)
test("Record id matches", records[0].record_id == ir.record_id)

# Empty project
empty_reports = load_daily_reports(TEST_DIR, "NONEXIST")
test("Empty project returns 0 reports", len(empty_reports) == 0)

shutil.rmtree(TEST_DIR)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 7: create_punch_item() ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.field_ops import create_punch_item

TEST_DIR = tempfile.mkdtemp(prefix="tf_field_test_")

punch = create_punch_item(
    TEST_DIR, "JOB-700", created_by="field_lead",
    title="Column C3 wrong length",
    description="Column is 2 inches short",
    priority="high", category="fit_issue",
    location="Bay 4", ship_mark="C3",
    assigned_to="shop_foreman"
)
test("create_punch_item returns PunchListItem", isinstance(punch, PunchListItem))
test("punch_id starts with PUNCH-", punch.punch_id.startswith("PUNCH-"))
test("status is open", punch.status == PUNCH_STATUS_OPEN)
test("priority is high", punch.priority == "high")
test("category is fit_issue", punch.category == "fit_issue")
test("created_by set", punch.created_by == "field_lead")
test("created_at set", punch.created_at != "")
test("assigned_to set", punch.assigned_to == "shop_foreman")
test("location set", punch.location == "Bay 4")

# Persisted
items = load_punch_items(TEST_DIR, "JOB-700")
test("create_punch_item persists", len(items) == 1)

shutil.rmtree(TEST_DIR)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 8: Punch Status Transitions ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.field_ops import transition_punch_status

TEST_DIR = tempfile.mkdtemp(prefix="tf_field_test_")

punch = create_punch_item(TEST_DIR, "JOB-800", created_by="field", title="Test issue")

# open → in_progress
result = transition_punch_status(TEST_DIR, "JOB-800", punch.punch_id, PUNCH_STATUS_IN_PROGRESS, "crew_bob")
test("open → in_progress ok", result["ok"])
test("old_status = open", result["old_status"] == PUNCH_STATUS_OPEN)
test("new_status = in_progress", result["new_status"] == PUNCH_STATUS_IN_PROGRESS)

# in_progress → resolved
result = transition_punch_status(TEST_DIR, "JOB-800", punch.punch_id, PUNCH_STATUS_RESOLVED, "crew_bob", notes="Welded patch applied")
test("in_progress → resolved ok", result["ok"])
reloaded = load_punch_item(TEST_DIR, "JOB-800", punch.punch_id)
test("resolved_by set", reloaded.resolved_by == "crew_bob")
test("resolved_at set", reloaded.resolved_at != "")
test("resolution_notes set", reloaded.resolution_notes == "Welded patch applied")

# resolved → verified (PM confirms)
result = transition_punch_status(TEST_DIR, "JOB-800", punch.punch_id, PUNCH_STATUS_VERIFIED, "pm_user")
test("resolved → verified ok", result["ok"])
reloaded = load_punch_item(TEST_DIR, "JOB-800", punch.punch_id)
test("verified_by set", reloaded.verified_by == "pm_user")
test("verified_at set", reloaded.verified_at != "")

# verified is terminal
result = transition_punch_status(TEST_DIR, "JOB-800", punch.punch_id, PUNCH_STATUS_OPEN, "field")
test("verified is terminal", not result["ok"])

# Invalid transitions
punch2 = create_punch_item(TEST_DIR, "JOB-800", created_by="field", title="Second issue")
result = transition_punch_status(TEST_DIR, "JOB-800", punch2.punch_id, PUNCH_STATUS_VERIFIED, "pm")
test("Cannot skip open → verified", not result["ok"])

# Deferred flow
result = transition_punch_status(TEST_DIR, "JOB-800", punch2.punch_id, PUNCH_STATUS_DEFERRED, "pm")
test("open → deferred ok", result["ok"])
result = transition_punch_status(TEST_DIR, "JOB-800", punch2.punch_id, PUNCH_STATUS_OPEN, "pm")
test("deferred → open (reopen) ok", result["ok"])

# Non-existent punch
result = transition_punch_status(TEST_DIR, "JOB-800", "FAKE-ID", PUNCH_STATUS_RESOLVED, "field")
test("Non-existent punch fails", not result["ok"])

shutil.rmtree(TEST_DIR)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 9: confirm_installation() with WO Integration ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.field_ops import confirm_installation
from shop_drawings.work_orders import (
    WorkOrder, WorkOrderItem, save_work_order, load_work_order,
    STATUS_DELIVERED, STATUS_INSTALLED, STATUS_SHIPPED, STATUS_IN_PROGRESS,
)

TEST_DIR = tempfile.mkdtemp(prefix="tf_field_test_")
WO_DIR = os.path.join(TEST_DIR, "data", "shop_drawings")

job = "INST-JOB-01"
wo = WorkOrder(
    work_order_id="WO-INST-001", job_code=job,
    items=[
        WorkOrderItem(item_id="INST-A1", ship_mark="A1", status=STATUS_DELIVERED),
        WorkOrderItem(item_id="INST-A2", ship_mark="A2", status=STATUS_DELIVERED),
        WorkOrderItem(item_id="INST-A3", ship_mark="A3", status=STATUS_SHIPPED),  # Not eligible
    ]
)
os.makedirs(os.path.join(WO_DIR, job, "work_orders"), exist_ok=True)
save_work_order(WO_DIR, wo)

# Confirm installation of INST-A1
result = confirm_installation(
    TEST_DIR, WO_DIR, job, "INST-A1", installed_by="crew_mike",
    location="Grid B-2", notes="Bolted and plumbed"
)
test("confirm_installation ok", result["ok"])
test("record returned", "record" in result)
test("record has record_id", result["record"]["record_id"].startswith("INST-"))
test("record installed_by", result["record"]["installed_by"] == "crew_mike")
test("record location", result["record"]["location"] == "Grid B-2")
test("item_status = installed", result["item_status"] == STATUS_INSTALLED)

# Verify WO item transitioned
wo_r = load_work_order(WO_DIR, job, "WO-INST-001")
a1 = [i for i in wo_r.items if i.item_id == "INST-A1"][0]
test("WO item INST-A1 → installed", a1.status == STATUS_INSTALLED)

# Verify installation record persisted
records = load_installation_records(TEST_DIR, job)
test("Installation record persisted", len(records) == 1)

# Cannot install non-delivered item
result = confirm_installation(TEST_DIR, WO_DIR, job, "INST-A3", installed_by="crew_mike")
test("Cannot install shipped item", not result["ok"])
test("Error mentions status", "shipped" in result.get("error", "").lower() or "status" in result.get("error", "").lower())

# Cannot install nonexistent item
result = confirm_installation(TEST_DIR, WO_DIR, job, "FAKE-ITEM", installed_by="crew_mike")
test("Cannot install nonexistent item", not result["ok"])

shutil.rmtree(TEST_DIR)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 10: submit_daily_report() with Auto-Install ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.field_ops import submit_daily_report

TEST_DIR = tempfile.mkdtemp(prefix="tf_field_test_")
WO_DIR = os.path.join(TEST_DIR, "data", "shop_drawings")

job = "DFR-JOB-01"
wo = WorkOrder(
    work_order_id="WO-DFR-001", job_code=job,
    items=[
        WorkOrderItem(item_id="DFR-A1", ship_mark="A1", status=STATUS_DELIVERED),
        WorkOrderItem(item_id="DFR-A2", ship_mark="A2", status=STATUS_DELIVERED),
    ]
)
os.makedirs(os.path.join(WO_DIR, job, "work_orders"), exist_ok=True)
save_work_order(WO_DIR, wo)

result = submit_daily_report(
    TEST_DIR, WO_DIR, job, submitted_by="field_lead",
    crew_count=3, hours_worked=8.0,
    work_summary="Installed columns A1 and A2",
    items_installed=["DFR-A1", "DFR-A2"],
    weather="sunny", temperature_f=82.0,
)
test("submit_daily_report ok", result["ok"])
test("report returned", "report" in result)
test("report has report_id", result["report"]["report_id"].startswith("DFR-"))
test("install_results returned", len(result.get("install_results", [])) == 2)

# Verify items auto-installed
wo_r = load_work_order(WO_DIR, job, "WO-DFR-001")
a1 = [i for i in wo_r.items if i.item_id == "DFR-A1"][0]
a2 = [i for i in wo_r.items if i.item_id == "DFR-A2"][0]
test("DFR-A1 → installed via daily report", a1.status == STATUS_INSTALLED)
test("DFR-A2 → installed via daily report", a2.status == STATUS_INSTALLED)

# Verify report persisted
reports = load_daily_reports(TEST_DIR, job)
test("Daily report persisted", len(reports) == 1)
test("Report crew_count", reports[0].crew_count == 3)
test("Report weather", reports[0].weather == "sunny")

shutil.rmtree(TEST_DIR)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 11: get_project_completion() ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.field_ops import get_project_completion

TEST_DIR = tempfile.mkdtemp(prefix="tf_field_test_")
WO_DIR = os.path.join(TEST_DIR, "data", "shop_drawings")

job = "COMP-JOB-01"
wo = WorkOrder(
    work_order_id="WO-COMP-001", job_code=job,
    items=[
        WorkOrderItem(item_id="C1", status=STATUS_INSTALLED),
        WorkOrderItem(item_id="C2", status=STATUS_INSTALLED),
        WorkOrderItem(item_id="C3", status=STATUS_DELIVERED),
        WorkOrderItem(item_id="C4", status=STATUS_SHIPPED),
        WorkOrderItem(item_id="C5", status="in_progress"),
    ]
)
os.makedirs(os.path.join(WO_DIR, job, "work_orders"), exist_ok=True)
save_work_order(WO_DIR, wo)

# Add a punch item
create_punch_item(TEST_DIR, job, created_by="field", title="Open issue", priority="high")
create_punch_item(TEST_DIR, job, created_by="field", title="Critical issue", priority="critical")

comp = get_project_completion(WO_DIR, TEST_DIR, job)
test("total_items = 5", comp["total_items"] == 5)
test("installed_count = 2", comp["installed_count"] == 2)
test("delivered_count = 1", comp["delivered_count"] == 1)
test("shipped_count = 1", comp["shipped_count"] == 1)
test("completion_pct = 40.0", comp["completion_pct"] == 40.0)
test("open_punches = 2", comp["open_punches"] == 2)
test("critical_punches = 1", comp["critical_punches"] == 1)
test("can_close = False (not all installed + open punches)", not comp["can_close"])
test("phase_counts has installed", comp["phase_counts"]["installed"] == 2)
test("phase_counts has shipping", comp["phase_counts"]["shipping"] == 2)  # delivered + shipped
test("total_work_orders = 1", comp["total_work_orders"] == 1)

# Test can_close with all installed and no open punches
wo2 = WorkOrder(
    work_order_id="WO-COMP-002", job_code="DONE-JOB",
    items=[
        WorkOrderItem(item_id="D1", status=STATUS_INSTALLED),
        WorkOrderItem(item_id="D2", status=STATUS_INSTALLED),
    ]
)
os.makedirs(os.path.join(WO_DIR, "DONE-JOB", "work_orders"), exist_ok=True)
save_work_order(WO_DIR, wo2)

comp2 = get_project_completion(WO_DIR, TEST_DIR, "DONE-JOB")
test("100% complete project completion_pct = 100.0", comp2["completion_pct"] == 100.0)
test("can_close = True (all installed, no open punches)", comp2["can_close"])

shutil.rmtree(TEST_DIR)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 12: get_field_summary() ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.field_ops import get_field_summary

TEST_DIR = tempfile.mkdtemp(prefix="tf_field_test_")
WO_DIR = os.path.join(TEST_DIR, "data", "shop_drawings")

# Project 1: partially installed
job1 = "SUM-JOB-01"
wo1 = WorkOrder(work_order_id="WO-SUM-1", job_code=job1, items=[
    WorkOrderItem(item_id="S1", status=STATUS_INSTALLED),
    WorkOrderItem(item_id="S2", status=STATUS_DELIVERED),
])
os.makedirs(os.path.join(WO_DIR, job1, "work_orders"), exist_ok=True)
save_work_order(WO_DIR, wo1)

# Project 2: fully installed
job2 = "SUM-JOB-02"
wo2 = WorkOrder(work_order_id="WO-SUM-2", job_code=job2, items=[
    WorkOrderItem(item_id="S3", status=STATUS_INSTALLED),
])
os.makedirs(os.path.join(WO_DIR, job2, "work_orders"), exist_ok=True)
save_work_order(WO_DIR, wo2)

# Add punch to project 1
create_punch_item(TEST_DIR, job1, created_by="field", title="Punch in proj 1", priority="critical")

summary = get_field_summary(WO_DIR, TEST_DIR)
test("active_projects >= 2", summary["active_projects"] >= 2)
test("total_installed >= 2", summary["total_installed"] >= 2)
test("total_delivered >= 1", summary["total_delivered"] >= 1)
test("total_open_punches >= 1", summary["total_open_punches"] >= 1)
test("total_critical_punches >= 1", summary["total_critical_punches"] >= 1)
test("projects list has entries", len(summary["projects"]) >= 2)

shutil.rmtree(TEST_DIR)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 13: Full End-to-End Field Lifecycle ══")
# ═══════════════════════════════════════════════════════════════════

TEST_DIR = tempfile.mkdtemp(prefix="tf_field_e2e_")
WO_DIR = os.path.join(TEST_DIR, "data", "shop_drawings")

job = "E2E-FIELD"
wo = WorkOrder(work_order_id="WO-E2E-F", job_code=job, items=[
    WorkOrderItem(item_id="F1", ship_mark="C1", status=STATUS_DELIVERED),
    WorkOrderItem(item_id="F2", ship_mark="C2", status=STATUS_DELIVERED),
    WorkOrderItem(item_id="F3", ship_mark="R1", status=STATUS_DELIVERED),
])
os.makedirs(os.path.join(WO_DIR, job, "work_orders"), exist_ok=True)
save_work_order(WO_DIR, wo)

# Step 1: Create punch item for F1 (damaged)
punch = create_punch_item(
    TEST_DIR, job, created_by="field_lead",
    title="C1 base plate cracked", priority="critical",
    category="damaged", item_id="F1", ship_mark="C1"
)
test("E2E: Punch created", punch.punch_id != "")

# Step 2: Submit daily report installing F2 and F3
result = submit_daily_report(
    TEST_DIR, WO_DIR, job, submitted_by="field_lead",
    crew_count=5, hours_worked=9.0,
    work_summary="Installed C2 and R1. C1 has damage, punch filed.",
    items_installed=["F2", "F3"],
    weather="cloudy",
)
test("E2E: Daily report submitted", result["ok"])
test("E2E: 2 items auto-installed", len(result["install_results"]) == 2)

# Step 3: Check completion (2/3 installed, 1 open critical punch)
comp = get_project_completion(WO_DIR, TEST_DIR, job)
test("E2E: completion_pct ≈ 66.7", abs(comp["completion_pct"] - 66.7) < 0.1)
test("E2E: open_punches = 1", comp["open_punches"] == 1)
test("E2E: critical_punches = 1", comp["critical_punches"] == 1)
test("E2E: can_close = False", not comp["can_close"])

# Step 4: Resolve punch (shop sends replacement)
transition_punch_status(TEST_DIR, job, punch.punch_id, PUNCH_STATUS_IN_PROGRESS, "shop_foreman")
transition_punch_status(TEST_DIR, job, punch.punch_id, PUNCH_STATUS_RESOLVED, "shop_foreman", notes="Replacement shipped")
transition_punch_status(TEST_DIR, job, punch.punch_id, PUNCH_STATUS_VERIFIED, "pm_user")

# Step 5: Confirm F1 installation
confirm_installation(TEST_DIR, WO_DIR, job, "F1", "crew_mike", location="Grid A-1", notes="Replacement installed")

# Step 6: Check completion — should be 100% and closeable
comp = get_project_completion(WO_DIR, TEST_DIR, job)
test("E2E: completion_pct = 100.0", comp["completion_pct"] == 100.0)
test("E2E: open_punches = 0", comp["open_punches"] == 0)
test("E2E: can_close = True", comp["can_close"])

# Verify all WO items installed
wo_final = load_work_order(WO_DIR, job, "WO-E2E-F")
for item in wo_final.items:
    test(f"E2E: {item.item_id} → installed", item.status == STATUS_INSTALLED)

shutil.rmtree(TEST_DIR)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 14: Handler Classes Exist ══")
# ═══════════════════════════════════════════════════════════════════
import tf_handlers as tfh

handler_classes = [
    "FieldDashboardPageHandler",
    "InstallTrackerPageHandler",
    "ProjectCompletionPageHandler",
    "PunchListAPIHandler",
    "PunchCreateHandler",
    "PunchTransitionHandler",
    "PunchDetailHandler",
    "InstallConfirmHandler",
    "DailyReportSubmitHandler",
    "DailyReportListHandler",
    "InstallationRecordsHandler",
    "ProjectCompletionAPIHandler",
    "FieldSummaryHandler",
    "FieldConfigHandler",
]

for cls_name in handler_classes:
    test(f"{cls_name} exists", hasattr(tfh, cls_name))
    cls = getattr(tfh, cls_name, None)
    if cls:
        test(f"{cls_name} has required_permission", hasattr(cls, "required_permission"))


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 15: RBAC Permission Mapping for Field Ops ══")
# ═══════════════════════════════════════════════════════════════════
from auth.roles import ROLES, P

# Check field_crew role
field_role = ROLES.get("field_crew")
test("field_crew role exists", field_role is not None)
if field_role:
    perms = field_role.permissions
    test("field_crew has create_punch_list", P.CREATE_PUNCH_LIST in perms)
    test("field_crew has submit_daily_report", P.SUBMIT_DAILY_REPORT in perms)
    test("field_crew has view_field_reports", P.VIEW_FIELD_REPORTS in perms)
    test("field_crew has upload_field_photos", P.UPLOAD_FIELD_PHOTOS in perms)

# Handler → permission mapping
permission_map = {
    "FieldDashboardPageHandler": "view_field_reports",
    "InstallTrackerPageHandler": "view_field_reports",
    "ProjectCompletionPageHandler": "view_field_reports",
    "PunchListAPIHandler": "view_field_reports",
    "PunchCreateHandler": "create_punch_list",
    "PunchTransitionHandler": "create_punch_list",
    "PunchDetailHandler": "view_field_reports",
    "InstallConfirmHandler": "create_punch_list",
    "DailyReportSubmitHandler": "submit_daily_report",
    "DailyReportListHandler": "view_field_reports",
    "InstallationRecordsHandler": "view_field_reports",
    "ProjectCompletionAPIHandler": "view_field_reports",
    "FieldSummaryHandler": "view_field_reports",
    "FieldConfigHandler": "view_field_reports",
}

for handler_name, expected_perm in permission_map.items():
    cls = getattr(tfh, handler_name, None)
    if cls:
        actual = getattr(cls, "required_permission", None)
        test(f"{handler_name} → {expected_perm}", actual == expected_perm)

# No old required_roles
for handler_name in handler_classes:
    cls = getattr(tfh, handler_name, None)
    if cls:
        test(f"{handler_name} has NO required_roles",
             not hasattr(cls, "required_roles") or getattr(cls, "required_roles", None) is None)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 16: Route Table (Field Operations Routes) ══")
# ═══════════════════════════════════════════════════════════════════

routes = tfh.get_routes()
route_paths = [r[0] if isinstance(r, (list, tuple)) else r for r in routes]

field_routes = [
    r"/field",
    r"/field/install-tracker",
    r"/field/completion",
    r"/api/field/punch-list",
    r"/api/field/punch-list/create",
    r"/api/field/punch-list/transition",
    r"/api/field/punch-list/detail",
    r"/api/field/confirm-install",
    r"/api/field/daily-report",
    r"/api/field/daily-reports",
    r"/api/field/installations",
    r"/api/field/project-completion",
    r"/api/field/summary",
    r"/api/field/config",
]

for route in field_routes:
    test(f"Route {route} registered", route in route_paths)

test(f"14 field routes total", sum(1 for r in route_paths if "/field" in r) >= 14)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 17: Template Files ══")
# ═══════════════════════════════════════════════════════════════════

from templates.field_ops_page import FIELD_OPS_PAGE_HTML
test("FIELD_OPS_PAGE_HTML is non-empty", len(FIELD_OPS_PAGE_HTML) > 500)
test("Field ops page has project selector", "projectSelect" in FIELD_OPS_PAGE_HTML)
test("Field ops page has punch list tab", "tab-punch" in FIELD_OPS_PAGE_HTML)
test("Field ops page has install queue tab", "tab-install" in FIELD_OPS_PAGE_HTML)
test("Field ops page has daily reports tab", "tab-reports" in FIELD_OPS_PAGE_HTML)
test("Field ops page has punch create modal", "punchModal" in FIELD_OPS_PAGE_HTML)
test("Field ops page has report modal", "reportModal" in FIELD_OPS_PAGE_HTML)
test("Field ops page fetches punch API", "/api/field/punch-list" in FIELD_OPS_PAGE_HTML)
test("Field ops page is mobile-friendly", 'viewport' in FIELD_OPS_PAGE_HTML)

from templates.install_tracker_page import INSTALL_TRACKER_PAGE_HTML
test("INSTALL_TRACKER_PAGE_HTML is non-empty", len(INSTALL_TRACKER_PAGE_HTML) > 500)
test("Install tracker has progress bar", "progressBar" in INSTALL_TRACKER_PAGE_HTML)
test("Install tracker has item grid", "item-grid" in INSTALL_TRACKER_PAGE_HTML)
test("Install tracker fetches completion API", "/api/field/project-completion" in INSTALL_TRACKER_PAGE_HTML)

from templates.project_completion_page import PROJECT_COMPLETION_PAGE_HTML
test("PROJECT_COMPLETION_PAGE_HTML is non-empty", len(PROJECT_COMPLETION_PAGE_HTML) > 500)
test("Completion page has project cards", "project-card" in PROJECT_COMPLETION_PAGE_HTML)
test("Completion page has close-out badge", "closeout-badge" in PROJECT_COMPLETION_PAGE_HTML)
test("Completion page has punch badge", "punch-badge" in PROJECT_COMPLETION_PAGE_HTML)
test("Completion page fetches summary API", "/api/field/summary" in PROJECT_COMPLETION_PAGE_HTML)
test("Completion page has auto-refresh", "setInterval" in PROJECT_COMPLETION_PAGE_HTML)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 18: Punch Resolved → Reopen Flow ══")
# ═══════════════════════════════════════════════════════════════════

TEST_DIR = tempfile.mkdtemp(prefix="tf_field_reopen_")

punch = create_punch_item(TEST_DIR, "REOPEN-JOB", created_by="field", title="Bolt missing")
transition_punch_status(TEST_DIR, "REOPEN-JOB", punch.punch_id, PUNCH_STATUS_IN_PROGRESS, "crew")
transition_punch_status(TEST_DIR, "REOPEN-JOB", punch.punch_id, PUNCH_STATUS_RESOLVED, "crew", notes="Added bolt")

# PM inspects — fix wasn't adequate, reopen
result = transition_punch_status(TEST_DIR, "REOPEN-JOB", punch.punch_id, PUNCH_STATUS_IN_PROGRESS, "pm", notes="Bolt wrong size")
test("resolved → in_progress (reopen) ok", result["ok"])

reloaded = load_punch_item(TEST_DIR, "REOPEN-JOB", punch.punch_id)
test("Reopened status = in_progress", reloaded.status == PUNCH_STATUS_IN_PROGRESS)

# Re-resolve
transition_punch_status(TEST_DIR, "REOPEN-JOB", punch.punch_id, PUNCH_STATUS_RESOLVED, "crew", notes="Correct bolt installed")
transition_punch_status(TEST_DIR, "REOPEN-JOB", punch.punch_id, PUNCH_STATUS_VERIFIED, "pm")

reloaded = load_punch_item(TEST_DIR, "REOPEN-JOB", punch.punch_id)
test("Final status = verified", reloaded.status == PUNCH_STATUS_VERIFIED)

shutil.rmtree(TEST_DIR)


# ═══════════════════════════════════════════════════════════════════
# FINAL REPORT
# ═══════════════════════════════════════════════════════════════════
total = passed + failed
print(f"\n{'='*60}")
print(f"Phase 5 (Field Operations & Installation): {passed}/{total} passed")
if failed:
    print(f"  ⚠️  {failed} FAILURES")
else:
    print(f"  🎉 ALL {total} TESTS PASSED")
print(f"{'='*60}")

sys.exit(0 if failed == 0 else 1)
