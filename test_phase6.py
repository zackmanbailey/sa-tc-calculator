#!/usr/bin/env python3
"""
TitanForge Phase 6 — Reporting & Analytics Tests
Tests report constants, aggregation engine, all 6 report types,
handler RBAC, route table, and template files.
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
print("\n══ TEST 1: Report Constants ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.reporting import (
    REPORT_TYPES, REPORT_LABELS,
    REPORT_PRODUCTION_METRICS, REPORT_EXECUTIVE_SUMMARY,
    REPORT_OPERATOR_PERFORMANCE, REPORT_PROJECT_STATUS,
    REPORT_DELIVERY_ANALYSIS, REPORT_QC_ANALYSIS,
    list_available_reports, generate_report,
)

test("6 report types", len(REPORT_TYPES) == 6)
test("production_metrics type", REPORT_PRODUCTION_METRICS == "production_metrics")
test("executive_summary type", REPORT_EXECUTIVE_SUMMARY == "executive_summary")
test("operator_performance type", REPORT_OPERATOR_PERFORMANCE == "operator_performance")
test("project_status type", REPORT_PROJECT_STATUS == "project_status")
test("delivery_analysis type", REPORT_DELIVERY_ANALYSIS == "delivery_analysis")
test("qc_analysis type", REPORT_QC_ANALYSIS == "qc_analysis")
test("All types have labels", all(t in REPORT_LABELS for t in REPORT_TYPES))
test("Labels are strings", all(isinstance(REPORT_LABELS[t], str) for t in REPORT_TYPES))

avail = list_available_reports()
test("list_available_reports returns 6", len(avail) == 6)
test("Each has type and label", all("type" in a and "label" in a for a in avail))
test("Types match REPORT_TYPES", [a["type"] for a in avail] == REPORT_TYPES)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 2: Time Helpers ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.reporting import (
    _today, _days_ago, _this_week_start, _this_month_start,
    _parse_iso, _date_from_iso,
)

today = _today()
test("_today returns ISO date", len(today) == 10 and today[4] == '-')
test("_days_ago(0) == today", _days_ago(0) == today)
test("_days_ago(7) is 7 days before", _days_ago(7) < today)
test("_this_week_start <= today", _this_week_start() <= today)
test("_this_month_start starts with day 01",_this_month_start().endswith("-01"))

test("_parse_iso valid", _parse_iso("2026-04-14T10:00:00") is not None)
test("_parse_iso invalid", _parse_iso("not-a-date") is None)
test("_parse_iso empty", _parse_iso("") is None)
test("_date_from_iso extracts date", _date_from_iso("2026-04-14T10:00:00") == "2026-04-14")
test("_date_from_iso empty", _date_from_iso("") is None)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 3: _load_all_wo_items (empty) ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.reporting import _load_all_wo_items

tmp = tempfile.mkdtemp()
wo_dir = os.path.join(tmp, "shop_drawings")
ship_dir = os.path.join(tmp, "data")
field_dir = tmp
os.makedirs(wo_dir, exist_ok=True)
os.makedirs(ship_dir, exist_ok=True)

items = _load_all_wo_items(wo_dir)
test("Empty base returns empty list", items == [])
test("Non-existent dir returns empty", _load_all_wo_items("/nonexistent/path") == [])


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 4: Production Metrics (empty data) ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.reporting import get_production_metrics

pm = get_production_metrics(wo_dir, ship_dir, field_dir, days_back=7)
test("Has report_type", pm["report_type"] == REPORT_PRODUCTION_METRICS)
test("Has generated_at", "generated_at" in pm)
test("Has period_days", pm["period_days"] == 7)
test("total_items is 0", pm["total_items"] == 0)
test("throughput has avg_daily", "avg_daily" in pm["throughput"])
test("throughput has series", isinstance(pm["throughput"]["series"], list))
test("series has 8 days (7+today)", len(pm["throughput"]["series"]) == 8)
test("cycle_times has avg_minutes", "avg_minutes" in pm["cycle_times"])
test("machine_utilization is dict", isinstance(pm["machine_utilization"], dict))
test("bottlenecks is list", isinstance(pm["bottlenecks"], list))
test("phase_distribution present", "phase_distribution" in pm)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 5: Executive Summary (empty data) ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.reporting import get_executive_summary

es = get_executive_summary(wo_dir, ship_dir, field_dir)
test("Has report_type", es["report_type"] == REPORT_EXECUTIVE_SUMMARY)
test("Has generated_at", "generated_at" in es)
test("kpis present", "kpis" in es)
test("kpis.active_projects", "active_projects" in es["kpis"])
test("kpis.total_items", "total_items" in es["kpis"])
test("kpis.fabrication_complete_pct", "fabrication_complete_pct" in es["kpis"])
test("kpis.qc_pass_rate", "qc_pass_rate" in es["kpis"])
test("kpis.on_time_delivery_pct", "on_time_delivery_pct" in es["kpis"])
test("kpis.field_completion_pct", "field_completion_pct" in es["kpis"])
test("kpis.open_punch_items", "open_punch_items" in es["kpis"])
test("today section", "today" in es)
test("this_week section", "this_week" in es)
test("shop_floor section", "shop_floor" in es)
test("shipping section", "shipping" in es)
test("field section", "field" in es)
test("shop_floor has machines", "machines" in es["shop_floor"])
test("shipping has total_loads", "total_loads" in es["shipping"])
test("field has active_projects", "active_projects" in es["field"])


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 6: Operator Performance (empty data) ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.reporting import get_operator_performance

op = get_operator_performance(wo_dir, days_back=30)
test("Has report_type", op["report_type"] == REPORT_OPERATOR_PERFORMANCE)
test("Has period_days", op["period_days"] == 30)
test("total_operators is 0", op["total_operators"] == 0)
test("operators is empty list", op["operators"] == [])


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 7: Project Status Report (empty data) ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.reporting import get_project_status_report

ps = get_project_status_report(wo_dir, ship_dir, field_dir)
test("Has report_type", ps["report_type"] == REPORT_PROJECT_STATUS)
test("total_projects is 0", ps["total_projects"] == 0)
test("projects is empty list", ps["projects"] == [])


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 8: Delivery Analysis (empty data) ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.reporting import get_delivery_analysis

da = get_delivery_analysis(ship_dir, field_dir, wo_dir)
test("Has report_type", da["report_type"] == REPORT_DELIVERY_ANALYSIS)
test("total_loads is 0", da["total_loads"] == 0)
test("status_counts is dict", isinstance(da["status_counts"], dict))
test("avg_items_per_load", "avg_items_per_load" in da)
test("avg_weight_per_load", "avg_weight_per_load" in da)
test("delivery_times", "delivery_times" in da)
test("delivery_times.avg_hours", "avg_hours" in da["delivery_times"])
test("shipments_by_project", isinstance(da["shipments_by_project"], list))
test("recent_deliveries", isinstance(da["recent_deliveries"], list))


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 9: QC Analysis (empty data) ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.reporting import get_qc_analysis

qc = get_qc_analysis(wo_dir)
test("Has report_type", qc["report_type"] == REPORT_QC_ANALYSIS)
test("total_inspected is 0", qc["total_inspected"] == 0)
test("approved is 0", qc["approved"] == 0)
test("rejected is 0", qc["rejected"] == 0)
test("pass_rate is 0", qc["pass_rate"] == 0.0)
test("awaiting_qc is 0", qc["awaiting_qc"] == 0)
test("needs_rework is 0", qc["needs_rework"] == 0)
test("by_inspector is list", isinstance(qc["by_inspector"], list))
test("by_machine is list", isinstance(qc["by_machine"], list))


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 10: generate_report() Dispatcher ══")
# ═══════════════════════════════════════════════════════════════════

# Valid report types
for rt in REPORT_TYPES:
    result = generate_report(rt, wo_dir, ship_dir, field_dir)
    test(f"generate_report({rt}) ok", result.get("ok") == True)
    test(f"generate_report({rt}) has report", "report" in result)

# Invalid type
result = generate_report("not_a_type", wo_dir, ship_dir, field_dir)
test("Invalid type returns error", result.get("ok") == False)
test("Error mentions unknown type", "Unknown report type" in result.get("error", ""))


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 11: Production Metrics with Data ══")
# ═══════════════════════════════════════════════════════════════════

# Create WO data
from shop_drawings.work_orders import (
    WorkOrder, WorkOrderItem, save_work_order,
    STATUS_QUEUED, STATUS_IN_PROGRESS, STATUS_FABRICATED,
    STATUS_QC_PENDING, STATUS_QC_APPROVED, STATUS_QC_REJECTED,
    STATUS_READY_TO_SHIP, STATUS_SHIPPED, STATUS_DELIVERED,
    STATUS_INSTALLED, STATUS_ON_HOLD,
)

now = datetime.datetime.now()
today_str = now.strftime("%Y-%m-%d")

wo = WorkOrder(
    work_order_id="WO-RPT-001",
    job_code="JOB-REPORT-1",
    revision="A",
    created_by="test_pm",
)

# Create items at various stages
wo.items = [
    WorkOrderItem(item_id="RPT-1", ship_mark="C1", status=STATUS_QUEUED, machine="WELDING"),
    WorkOrderItem(item_id="RPT-2", ship_mark="C2", status=STATUS_IN_PROGRESS, machine="WELDING",
                  assigned_to="welder1", started_at=now.isoformat()),
    WorkOrderItem(item_id="RPT-3", ship_mark="B1", status=STATUS_FABRICATED, machine="Z1",
                  assigned_to="op1",
                  started_at=(now - datetime.timedelta(hours=2)).isoformat(),
                  finished_at=now.isoformat(), duration_minutes=120.0),
    WorkOrderItem(item_id="RPT-4", ship_mark="B2", status=STATUS_QC_APPROVED, machine="Z1",
                  assigned_to="op1", qc_result="approved", qc_inspector="qc1",
                  started_at=(now - datetime.timedelta(hours=1)).isoformat(),
                  finished_at=(now - datetime.timedelta(minutes=30)).isoformat(),
                  duration_minutes=30.0),
    WorkOrderItem(item_id="RPT-5", ship_mark="B3", status=STATUS_QC_REJECTED, machine="C1",
                  assigned_to="op2", qc_result="rejected", qc_inspector="qc1",
                  qc_notes="Weld defect at joint",
                  started_at=(now - datetime.timedelta(hours=3)).isoformat(),
                  finished_at=(now - datetime.timedelta(hours=2)).isoformat(),
                  duration_minutes=60.0),
    WorkOrderItem(item_id="RPT-6", ship_mark="P1", status=STATUS_SHIPPED, machine="P1",
                  assigned_to="op3",
                  started_at=(now - datetime.timedelta(days=2)).isoformat(),
                  finished_at=(now - datetime.timedelta(days=1)).isoformat(),
                  duration_minutes=45.0),
    WorkOrderItem(item_id="RPT-7", ship_mark="P2", status=STATUS_INSTALLED, machine="P1",
                  assigned_to="op3",
                  started_at=(now - datetime.timedelta(days=3)).isoformat(),
                  finished_at=(now - datetime.timedelta(days=2)).isoformat(),
                  duration_minutes=55.0),
    WorkOrderItem(item_id="RPT-8", ship_mark="T1", status=STATUS_ON_HOLD, machine="TRIM"),
]

save_work_order(wo_dir, wo)

pm2 = get_production_metrics(wo_dir, ship_dir, field_dir, days_back=7)
test("total_items is 8", pm2["total_items"] == 8)
test("status_counts has queued", pm2["status_counts"].get("queued") == 1)
test("status_counts has in_progress", pm2["status_counts"].get("in_progress") == 1)
test("status_counts has on_hold", pm2["status_counts"].get("on_hold") == 1)
test("phase_distribution prefab > 0", pm2["phase_distribution"]["prefab"] >= 1)
test("phase_distribution fabrication > 0", pm2["phase_distribution"]["fabrication"] >= 1)
test("phase_distribution on_hold > 0", pm2["phase_distribution"]["on_hold"] >= 1)
test("cycle_times tracked > 0", pm2["cycle_times"]["total_tracked"] > 0)
test("cycle_times avg > 0", pm2["cycle_times"]["avg_minutes"] > 0)
test("machine utilization has WELDING", "WELDING" in pm2["machine_utilization"])
test("WELDING has 1 active", pm2["machine_utilization"]["WELDING"]["active"] == 1)
test("WELDING has 1 queued", pm2["machine_utilization"]["WELDING"]["queued"] == 1)

# Bottlenecks: should detect on_hold and qc_rejected
has_hold_bottleneck = any(b["type"] == "on_hold" for b in pm2["bottlenecks"])
has_qc_bottleneck = any(b["type"] == "qc_rejected" for b in pm2["bottlenecks"])
test("Bottleneck: on_hold detected", has_hold_bottleneck)
test("Bottleneck: qc_rejected detected", has_qc_bottleneck)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 12: Operator Performance with Data ══")
# ═══════════════════════════════════════════════════════════════════

op2 = get_operator_performance(wo_dir, days_back=30)
test("total_operators > 0", op2["total_operators"] > 0)
test("operators list populated", len(op2["operators"]) > 0)

# Find welder1
welder1 = next((o for o in op2["operators"] if o["username"] == "welder1"), None)
test("welder1 found", welder1 is not None)
if welder1:
    test("welder1 items_assigned >= 1", welder1["items_assigned"] >= 1)
    test("welder1 items_in_progress >= 1", welder1["items_in_progress"] >= 1)
    test("welder1 machines_used has WELDING", "WELDING" in welder1["machines_used"])

# Find op1 — completed items with cycle times
op1_data = next((o for o in op2["operators"] if o["username"] == "op1"), None)
test("op1 found", op1_data is not None)
if op1_data:
    test("op1 items_assigned >= 2", op1_data["items_assigned"] >= 2)
    test("op1 avg_cycle_minutes > 0", op1_data["avg_cycle_minutes"] > 0)
    test("op1 qc_approved >= 1", op1_data["qc_approved"] >= 1)

# Find op2 — QC rejected
op2_data = next((o for o in op2["operators"] if o["username"] == "op2"), None)
test("op2 found", op2_data is not None)
if op2_data:
    test("op2 qc_rejected >= 1", op2_data["qc_rejected"] >= 1)
    test("op2 pass_rate < 100", op2_data["qc_pass_rate"] < 100 or op2_data["qc_rejected"] > 0)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 13: Executive Summary with Data ══")
# ═══════════════════════════════════════════════════════════════════

es2 = get_executive_summary(wo_dir, ship_dir, field_dir)
test("active_projects >= 1", es2["kpis"]["active_projects"] >= 1)
test("total_items >= 8", es2["kpis"]["total_items"] >= 8)
test("fabrication_complete_pct > 0", es2["kpis"]["fabrication_complete_pct"] > 0)
test("shop_floor status_counts populated", len(es2["shop_floor"]["status_counts"]) > 0)
test("shop_floor machines has entries", len(es2["shop_floor"]["machines"]) > 0)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 14: Project Status with Data ══")
# ═══════════════════════════════════════════════════════════════════

ps2 = get_project_status_report(wo_dir, ship_dir, field_dir)
test("total_projects >= 1", ps2["total_projects"] >= 1)
test("projects list not empty", len(ps2["projects"]) > 0)

proj = ps2["projects"][0]
test("Project has job_code", "job_code" in proj)
test("Project has total_items", proj["total_items"] >= 1)
test("Project has status_counts", isinstance(proj["status_counts"], dict))
test("Project has phases", "phases" in proj)
test("Project has fabrication_complete_pct", "fabrication_complete_pct" in proj)
test("Project has field_complete_pct", "field_complete_pct" in proj)
test("Project phases has prefab", "prefab" in proj["phases"])
test("Project phases has fabrication", "fabrication" in proj["phases"])
test("Project phases has installed", "installed" in proj["phases"])
test("Project has qc_approved", "qc_approved" in proj)
test("Project has qc_rejected", "qc_rejected" in proj)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 15: QC Analysis with Data ══")
# ═══════════════════════════════════════════════════════════════════

qc2 = get_qc_analysis(wo_dir)
test("total_inspected >= 2", qc2["total_inspected"] >= 2)
test("approved >= 1", qc2["approved"] >= 1)
test("rejected >= 1", qc2["rejected"] >= 1)
test("pass_rate > 0 and < 100", 0 < qc2["pass_rate"] < 100)
test("by_inspector has entries", len(qc2["by_inspector"]) > 0)
test("by_machine has entries", len(qc2["by_machine"]) > 0)

# Find inspector qc1
qc1_stats = next((i for i in qc2["by_inspector"] if i["inspector"] == "qc1"), None)
test("Inspector qc1 found", qc1_stats is not None)
if qc1_stats:
    test("qc1 total >= 2", qc1_stats["total_inspections"] >= 2)
    test("qc1 approved >= 1", qc1_stats["approved"] >= 1)
    test("qc1 rejected >= 1", qc1_stats["rejected"] >= 1)
    test("qc1 pass_rate between 0 and 100", 0 < qc1_stats["pass_rate"] < 100)

# Machine QC stats
z1_qc = next((m for m in qc2["by_machine"] if m["machine"] == "Z1"), None)
test("Z1 machine in QC stats", z1_qc is not None)
if z1_qc:
    test("Z1 approved >= 1", z1_qc["approved"] >= 1)

c1_qc = next((m for m in qc2["by_machine"] if m["machine"] == "C1"), None)
test("C1 machine in QC stats", c1_qc is not None)
if c1_qc:
    test("C1 rejected >= 1", c1_qc["rejected"] >= 1)
    test("C1 rejection_rate > 0", c1_qc["rejection_rate"] > 0)

test("needs_rework >= 1", qc2["needs_rework"] >= 1)
test("awaiting_qc >= 1", qc2["awaiting_qc"] >= 1)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 16: Multi-Project Reporting ══")
# ═══════════════════════════════════════════════════════════════════

# Create a second project
wo2 = WorkOrder(
    work_order_id="WO-RPT-002",
    job_code="JOB-REPORT-2",
    revision="A",
    created_by="test_pm",
)
wo2.items = [
    WorkOrderItem(item_id="RPT-21", ship_mark="A1", status=STATUS_INSTALLED, machine="WELDING",
                  assigned_to="welder1", qc_result="approved", qc_inspector="qc2",
                  started_at=(now - datetime.timedelta(days=5)).isoformat(),
                  finished_at=(now - datetime.timedelta(days=4)).isoformat(),
                  duration_minutes=90.0),
    WorkOrderItem(item_id="RPT-22", ship_mark="A2", status=STATUS_DELIVERED, machine="Z2",
                  assigned_to="op4", qc_result="approved", qc_inspector="qc2",
                  started_at=(now - datetime.timedelta(days=4)).isoformat(),
                  finished_at=(now - datetime.timedelta(days=3)).isoformat(),
                  duration_minutes=75.0),
    WorkOrderItem(item_id="RPT-23", ship_mark="A3", status=STATUS_IN_PROGRESS, machine="SPARTAN",
                  assigned_to="op5"),
]
save_work_order(wo_dir, wo2)

# Now test cross-project
pm3 = get_production_metrics(wo_dir, ship_dir, field_dir, days_back=30)
test("Multi-project total >= 11", pm3["total_items"] >= 11)

ps3 = get_project_status_report(wo_dir, ship_dir, field_dir)
test("Multi-project total_projects >= 2", ps3["total_projects"] >= 2)
job_codes = [p["job_code"] for p in ps3["projects"]]
test("JOB-REPORT-1 in projects", "JOB-REPORT-1" in job_codes)
test("JOB-REPORT-2 in projects", "JOB-REPORT-2" in job_codes)

es3 = get_executive_summary(wo_dir, ship_dir, field_dir)
test("Exec summary active_projects >= 2", es3["kpis"]["active_projects"] >= 2)
test("Exec summary total_items >= 11", es3["kpis"]["total_items"] >= 11)

op3 = get_operator_performance(wo_dir, days_back=30)
usernames = [o["username"] for o in op3["operators"]]
test("welder1 in operator report", "welder1" in usernames)
test("op4 in operator report", "op4" in usernames)
test("op5 in operator report", "op5" in usernames)

qc3 = get_qc_analysis(wo_dir)
test("QC total_inspected >= 4", qc3["total_inspected"] >= 4)
inspectors = [i["inspector"] for i in qc3["by_inspector"]]
test("qc1 inspector present", "qc1" in inspectors)
test("qc2 inspector present", "qc2" in inspectors)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 17: Handler Classes Exist ══")
# ═══════════════════════════════════════════════════════════════════

import tf_handlers as tfh

handler_classes = [
    "ProductionMetricsPageHandler",
    "ExecutiveSummaryPageHandler",
    "ReportListHandler",
    "ReportGenerateHandler",
    "ProductionMetricsAPIHandler",
    "ExecutiveSummaryAPIHandler",
    "OperatorPerformanceAPIHandler",
    "ProjectStatusReportAPIHandler",
    "DeliveryAnalysisAPIHandler",
    "QCAnalysisAPIHandler",
    "ReportConfigHandler",
]

for cls_name in handler_classes:
    test(f"{cls_name} exists", hasattr(tfh, cls_name))

# Check they're subclasses of BaseHandler
for cls_name in handler_classes:
    cls = getattr(tfh, cls_name, None)
    if cls:
        test(f"{cls_name} is BaseHandler subclass",
             issubclass(cls, tfh.BaseHandler))


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 18: RBAC Permissions ══")
# ═══════════════════════════════════════════════════════════════════

from auth.roles import P, ROLES, get_role

# All reporting handlers require view_financials or view_project_pnl
financial_handlers = [
    "ProductionMetricsPageHandler",
    "ExecutiveSummaryPageHandler",
    "ReportListHandler",
    "ReportGenerateHandler",
    "ProductionMetricsAPIHandler",
    "ExecutiveSummaryAPIHandler",
    "OperatorPerformanceAPIHandler",
    "DeliveryAnalysisAPIHandler",
    "QCAnalysisAPIHandler",
    "ReportConfigHandler",
]

for cls_name in financial_handlers:
    cls = getattr(tfh, cls_name, None)
    if cls:
        perm = getattr(cls, 'required_permission', None)
        test(f"{cls_name} requires view_financials",
             perm == "view_financials")

# ProjectStatusReportAPIHandler uses view_project_pnl
cls = getattr(tfh, "ProjectStatusReportAPIHandler", None)
if cls:
    test("ProjectStatusReportAPIHandler requires view_project_pnl",
         cls.required_permission == "view_project_pnl")

# Check that the right roles have view_financials
roles_with_financials = []
for role_name, role_def in ROLES.items():
    if P.VIEW_FINANCIALS in role_def.permissions:
        roles_with_financials.append(role_name)

test("god_mode has view_financials", "god_mode" in roles_with_financials)
test("admin has view_financials", "admin" in roles_with_financials)
test("project_manager has view_financials", "project_manager" in roles_with_financials)
test("accounting has view_financials", "accounting" in roles_with_financials)
test("welder does NOT have view_financials", "welder" not in roles_with_financials)
test("operator does NOT have view_financials", "roll_forming_operator" not in roles_with_financials)
test("field_crew does NOT have view_financials", "field_crew" not in roles_with_financials)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 19: Route Table ══")
# ═══════════════════════════════════════════════════════════════════

routes = tfh.get_routes()
route_map = {}
for entry in routes:
    if len(entry) >= 2:
        route_map[entry[0]] = entry[1]

expected_routes = {
    r"/reports/production":          "ProductionMetricsPageHandler",
    r"/reports/executive":           "ExecutiveSummaryPageHandler",
    r"/api/reports":                 "ReportListHandler",
    r"/api/reports/generate":        "ReportGenerateHandler",
    r"/api/reports/production":      "ProductionMetricsAPIHandler",
    r"/api/reports/executive":       "ExecutiveSummaryAPIHandler",
    r"/api/reports/operators":       "OperatorPerformanceAPIHandler",
    r"/api/reports/project-status":  "ProjectStatusReportAPIHandler",
    r"/api/reports/delivery":        "DeliveryAnalysisAPIHandler",
    r"/api/reports/qc":             "QCAnalysisAPIHandler",
    r"/api/reports/config":          "ReportConfigHandler",
}

for pattern, expected_handler in expected_routes.items():
    handler = route_map.get(pattern)
    handler_name = handler.__name__ if handler else "NOT FOUND"
    test(f"Route {pattern} → {expected_handler}",
         handler_name == expected_handler)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 20: Template Files ══")
# ═══════════════════════════════════════════════════════════════════

from templates.production_metrics_page import PRODUCTION_METRICS_PAGE_HTML
from templates.executive_summary_page import EXECUTIVE_SUMMARY_PAGE_HTML

test("Production Metrics template exists", isinstance(PRODUCTION_METRICS_PAGE_HTML, str))
test("Production Metrics is HTML", "<!DOCTYPE html>" in PRODUCTION_METRICS_PAGE_HTML)
test("Production Metrics has title", "Production Metrics" in PRODUCTION_METRICS_PAGE_HTML)
test("Production Metrics has API call", "/api/reports/production" in PRODUCTION_METRICS_PAGE_HTML)
test("Production Metrics has KPI cards", "kpiTotal" in PRODUCTION_METRICS_PAGE_HTML)
test("Production Metrics has machine grid", "machineGrid" in PRODUCTION_METRICS_PAGE_HTML)
test("Production Metrics has throughput chart", "throughputChart" in PRODUCTION_METRICS_PAGE_HTML)
test("Production Metrics has bottleneck list", "bottleneckList" in PRODUCTION_METRICS_PAGE_HTML)
test("Production Metrics has phase bar", "phaseBar" in PRODUCTION_METRICS_PAGE_HTML)
test("Production Metrics has period selector", "periodSelect" in PRODUCTION_METRICS_PAGE_HTML)

test("Executive Summary template exists", isinstance(EXECUTIVE_SUMMARY_PAGE_HTML, str))
test("Executive Summary is HTML", "<!DOCTYPE html>" in EXECUTIVE_SUMMARY_PAGE_HTML)
test("Executive Summary has title", "Executive Summary" in EXECUTIVE_SUMMARY_PAGE_HTML)
test("Executive Summary has API call", "/api/reports/executive" in EXECUTIVE_SUMMARY_PAGE_HTML)
test("Executive Summary has hero KPIs", "heroProjects" in EXECUTIVE_SUMMARY_PAGE_HTML)
test("Executive Summary has shipping section", "pipelineBar" in EXECUTIVE_SUMMARY_PAGE_HTML)
test("Executive Summary has field stats", "fieldStats" in EXECUTIVE_SUMMARY_PAGE_HTML)
test("Executive Summary has machine grid", "machineGrid" in EXECUTIVE_SUMMARY_PAGE_HTML)
test("Executive Summary has today strip", "todayStrip" in EXECUTIVE_SUMMARY_PAGE_HTML)
test("Executive Summary links to production", "/reports/production" in EXECUTIVE_SUMMARY_PAGE_HTML)
test("Executive Summary links to shop-floor", "/shop-floor" in EXECUTIVE_SUMMARY_PAGE_HTML)
test("Executive Summary links to shipping", "/shipping" in EXECUTIVE_SUMMARY_PAGE_HTML)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 21: Cycle Time Calculations ══")
# ═══════════════════════════════════════════════════════════════════

# Verify per-machine cycle times
pm_ct = get_production_metrics(wo_dir, ship_dir, field_dir, days_back=30)
by_machine = pm_ct["cycle_times"]["by_machine"]

# Z1 had two items: 120 min and 30 min → avg = 75
test("Z1 avg cycle time calculated", by_machine.get("Z1", 0) > 0)

# P1 had two items: 45 min and 55 min → avg = 50
test("P1 avg cycle time calculated", by_machine.get("P1", 0) > 0)

# C1 had one item: 60 min
test("C1 avg cycle time = 60", by_machine.get("C1", 0) == 60.0)

# Overall avg should be positive
test("Overall avg cycle time > 0", pm_ct["cycle_times"]["avg_minutes"] > 0)

# Throughput: at least some items finished in period
test("Throughput total_completed > 0", pm_ct["throughput"]["total_completed"] > 0)
test("Throughput avg_daily > 0", pm_ct["throughput"]["avg_daily"] > 0)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 22: Phase Distribution Accuracy ══")
# ═══════════════════════════════════════════════════════════════════

pd = pm_ct["phase_distribution"]
total_in_phases = sum(pd.values())
test("Phase distribution sums to total_items", total_in_phases == pm_ct["total_items"])

# From our test data:
# JOB-REPORT-1: queued(1) + in_progress(1) + fabricated(1) + qc(2) + shipping(1) + installed(1) + hold(1) = 8
# JOB-REPORT-2: installed(1) + shipping(1) + fabrication(1) = 3
# Total = 11
test("Total items is 11", pm_ct["total_items"] == 11)
test("Prefab >= 1", pd["prefab"] >= 1)
test("Fabrication >= 2", pd["fabrication"] >= 2)
test("QC >= 2", pd["qc"] >= 2)
test("Shipping >= 2", pd["shipping"] >= 2)
test("Installed >= 2", pd["installed"] >= 2)
test("On hold >= 1", pd["on_hold"] >= 1)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 23: generate_report with days_back kwarg ══")
# ═══════════════════════════════════════════════════════════════════

r7 = generate_report(REPORT_PRODUCTION_METRICS, wo_dir, ship_dir, field_dir, days_back=7)
test("7-day report ok", r7.get("ok") == True)
test("7-day report period is 7", r7["report"]["period_days"] == 7)
test("7-day series length is 8", len(r7["report"]["throughput"]["series"]) == 8)

r90 = generate_report(REPORT_PRODUCTION_METRICS, wo_dir, ship_dir, field_dir, days_back=90)
test("90-day report ok", r90.get("ok") == True)
test("90-day report period is 90", r90["report"]["period_days"] == 90)
test("90-day series length is 91", len(r90["report"]["throughput"]["series"]) == 91)

r_op = generate_report(REPORT_OPERATOR_PERFORMANCE, wo_dir, ship_dir, field_dir, days_back=7)
test("Op performance 7-day ok", r_op.get("ok") == True)
test("Op performance period is 7", r_op["report"]["period_days"] == 7)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 24: Delivery Analysis with Shipping Data ══")
# ═══════════════════════════════════════════════════════════════════

# Create shipping load data
from shop_drawings.shipping import (
    ShippingLoad, LoadItem, save_load,
    LOAD_STATUS_BUILDING, LOAD_STATUS_DELIVERED, LOAD_STATUS_COMPLETE,
)

load1 = ShippingLoad(
    load_id="LOAD-RPT-001", load_number=1, status=LOAD_STATUS_DELIVERED,
    shipped_at=(now - datetime.timedelta(days=2)).isoformat(),
    delivered_at=(now - datetime.timedelta(days=1)).isoformat(),
    shipped_by="shipper1", delivered_by="driver1",
)
load1.items = [
    LoadItem(item_id="RPT-6", job_code="JOB-REPORT-1", ship_mark="P1",
             description="Panel P1", weight_lbs=500),
    LoadItem(item_id="RPT-7", job_code="JOB-REPORT-1", ship_mark="P2",
             description="Panel P2", weight_lbs=450),
]

load2 = ShippingLoad(
    load_id="LOAD-RPT-002", load_number=2, status=LOAD_STATUS_BUILDING,
)
load2.items = [
    LoadItem(item_id="RPT-21", job_code="JOB-REPORT-2", ship_mark="A1",
             description="Angle A1", weight_lbs=200),
]

# Save loads to shipping dir
load_dir = os.path.join(ship_dir, "shipping_loads")
os.makedirs(load_dir, exist_ok=True)
save_load(ship_dir, load1)
save_load(ship_dir, load2)

da2 = get_delivery_analysis(ship_dir, field_dir, wo_dir)
test("Delivery total_loads >= 2", da2["total_loads"] >= 2)
test("Status counts has delivered", da2["status_counts"].get("delivered", 0) >= 1)
test("Status counts has building", da2["status_counts"].get("building", 0) >= 1)
test("avg_items_per_load > 0", da2["avg_items_per_load"] > 0)
test("avg_weight_per_load > 0", da2["avg_weight_per_load"] > 0)
test("delivery_times tracked >= 1", da2["delivery_times"]["total_tracked"] >= 1)
test("delivery_times avg_hours > 0", da2["delivery_times"]["avg_hours"] > 0)
test("recent_deliveries >= 1", len(da2["recent_deliveries"]) >= 1)
test("shipments_by_project has entries", len(da2["shipments_by_project"]) >= 1)

# Check shipments by project
jrp1 = next((s for s in da2["shipments_by_project"] if s["job_code"] == "JOB-REPORT-1"), None)
test("JOB-REPORT-1 in shipments", jrp1 is not None)
if jrp1:
    test("JOB-REPORT-1 items >= 2", jrp1["items"] >= 2)
    test("JOB-REPORT-1 weight >= 950", jrp1["weight"] >= 950)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 25: Full E2E — All Reports from Same Data ══")
# ═══════════════════════════════════════════════════════════════════

# All 6 reports should work with the same data set
all_ok = True
for rt in REPORT_TYPES:
    result = generate_report(rt, wo_dir, ship_dir, field_dir, days_back=30)
    if not result.get("ok"):
        all_ok = False
        test(f"E2E {rt} FAILED: {result.get('error')}", False)
    else:
        test(f"E2E {rt} succeeds", True)
        test(f"E2E {rt} has generated_at",
             "generated_at" in result["report"])

# Cross-check: exec summary should reflect shipping data
es_final = get_executive_summary(wo_dir, ship_dir, field_dir)
test("E2E exec total_loads > 0", es_final["shipping"]["total_loads"] > 0)
test("E2E exec total_items >= 11", es_final["kpis"]["total_items"] >= 11)

# Cross-check: QC analysis should reflect both projects
qc_final = get_qc_analysis(wo_dir)
test("E2E QC total_inspected >= 4", qc_final["total_inspected"] >= 4)


# ═══════════════════════════════════════════════════════════════════
# CLEANUP
# ═══════════════════════════════════════════════════════════════════
shutil.rmtree(tmp, ignore_errors=True)


# ═══════════════════════════════════════════════════════════════════
print(f"\n{'='*60}")
print(f"Phase 6 Results: {passed} passed, {failed} failed, {passed + failed} total")
print(f"{'='*60}")
if failed > 0:
    sys.exit(1)
