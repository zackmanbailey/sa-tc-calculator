#!/usr/bin/env python3
"""
TitanForge Phase 10 Tests — Job Costing & Financial Tracking
==============================================================
Tests cost estimates, actuals, labor entries, change orders,
job P&L, variance analysis, handlers, RBAC, and routes.
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
print("\n══ TEST 1: Cost Category Constants ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.job_costing import (
    COST_CATEGORIES, COST_CATEGORY_LABELS,
    COST_CAT_MATERIAL, COST_CAT_LABOR, COST_CAT_EQUIPMENT,
    COST_CAT_SUBCONTRACT, COST_CAT_OVERHEAD, COST_CAT_FREIGHT,
)

test("6 cost categories", len(COST_CATEGORIES) == 6)
test("Material category", COST_CAT_MATERIAL == "material")
test("Labor category", COST_CAT_LABOR == "labor")
test("Equipment category", COST_CAT_EQUIPMENT == "equipment")
test("Subcontract category", COST_CAT_SUBCONTRACT == "subcontract")
test("Overhead category", COST_CAT_OVERHEAD == "overhead")
test("Freight category", COST_CAT_FREIGHT == "freight")
test("All categories have labels", all(c in COST_CATEGORY_LABELS for c in COST_CATEGORIES))

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 2: Estimate Status Constants ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.job_costing import (
    EST_STATUSES, EST_STATUS_LABELS,
    EST_STATUS_DRAFT, EST_STATUS_APPROVED, EST_STATUS_REVISED, EST_STATUS_FINAL,
)

test("4 estimate statuses", len(EST_STATUSES) == 4)
test("Draft status", EST_STATUS_DRAFT == "draft")
test("Approved status", EST_STATUS_APPROVED == "approved")
test("Revised status", EST_STATUS_REVISED == "revised")
test("Final status", EST_STATUS_FINAL == "final")
test("All statuses have labels", all(s in EST_STATUS_LABELS for s in EST_STATUSES))

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 3: Labor Rate Constants ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.job_costing import DEFAULT_LABOR_RATES, DEFAULT_LABOR_RATE_LABELS

test("7 default labor rates", len(DEFAULT_LABOR_RATES) == 7)
test("Welder rate exists", "welder" in DEFAULT_LABOR_RATES)
test("Welder rate is numeric", isinstance(DEFAULT_LABOR_RATES["welder"], (int, float)))
test("All rates have labels", all(k in DEFAULT_LABOR_RATE_LABELS for k in DEFAULT_LABOR_RATES))
test("Foreman rate > helper rate", DEFAULT_LABOR_RATES["foreman"] > DEFAULT_LABOR_RATES["helper"])

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 4: CostEstimate Data Model ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.job_costing import CostEstimate

est = CostEstimate(
    job_code="JOB-100", name="Original Estimate",
    contract_value=100000.0, created_by="pm1",
    line_items=[
        {"category": "material", "description": "Steel", "total": 40000},
        {"category": "labor", "description": "Fabrication", "total": 30000},
        {"category": "overhead", "description": "Shop overhead", "total": 10000},
    ],
)
est.recalculate_total()

test("Estimate ID auto-generated", est.estimate_id.startswith("EST-"))
test("Created_at auto-set", len(est.created_at) > 0)
test("Job code stored", est.job_code == "JOB-100")
test("Default status is draft", est.status == EST_STATUS_DRAFT)
test("Total recalculated", est.total_amount == 80000.0)
test("Contract value stored", est.contract_value == 100000.0)
test("Estimated margin", est.estimated_margin == 20000.0)
test("Estimated margin pct", est.estimated_margin_pct == 20.0)
test("status_label property", est.status_label == "Draft")

d = est.to_dict()
test("to_dict returns dict", isinstance(d, dict))
test("to_dict has margin fields", "estimated_margin" in d)
est2 = CostEstimate.from_dict(d)
test("from_dict preserves id", est2.estimate_id == est.estimate_id)
test("from_dict preserves line_items", len(est2.line_items) == 3)
test("from_dict preserves contract_value", est2.contract_value == 100000.0)

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 5: CostEntry Data Model ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.job_costing import CostEntry

ce = CostEntry(
    job_code="JOB-100", category="material",
    description="Steel plate 1/2in", quantity=500, unit="lbs",
    unit_cost=1.25, vendor="Steel Supply Co", created_by="buyer1",
)

test("CostEntry ID auto-generated", ce.entry_id.startswith("COST-"))
test("Created_at auto-set", len(ce.created_at) > 0)
test("Total auto-calculated", ce.total == 625.0)
test("Date auto-set", len(ce.date) > 0)
test("category_label property", ce.category_label == "Material")

d = ce.to_dict()
test("CostEntry to_dict", isinstance(d, dict))
ce2 = CostEntry.from_dict(d)
test("CostEntry from_dict preserves id", ce2.entry_id == ce.entry_id)
test("CostEntry from_dict preserves total", ce2.total == 625.0)

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 6: LaborEntry Data Model ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.job_costing import LaborEntry

le = LaborEntry(
    job_code="JOB-100", worker="welder1", labor_type="welder",
    hours=8.0, created_by="foreman1",
)

test("LaborEntry ID auto-generated", le.labor_id.startswith("LAB-"))
test("Created_at auto-set", len(le.created_at) > 0)
test("Rate auto-set from defaults", le.rate == DEFAULT_LABOR_RATES["welder"])
test("Total auto-calculated", le.total == 8.0 * DEFAULT_LABOR_RATES["welder"])
test("Date auto-set", len(le.date) > 0)
test("Overtime default false", not le.overtime)
test("effective_rate normal", le.effective_rate == le.rate)

# Overtime entry
le_ot = LaborEntry(
    job_code="JOB-100", worker="welder1", labor_type="welder",
    hours=4.0, overtime=True, created_by="foreman1",
)
test("OT effective_rate", le_ot.effective_rate == le_ot.rate * 1.5)
test("OT total includes multiplier", le_ot.total == 4.0 * DEFAULT_LABOR_RATES["welder"] * 1.5)

d = le.to_dict()
test("LaborEntry to_dict has effective_rate", "effective_rate" in d)
le2 = LaborEntry.from_dict(d)
test("LaborEntry from_dict preserves id", le2.labor_id == le.labor_id)

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 7: ChangeOrderCost Data Model ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.job_costing import ChangeOrderCost

co = ChangeOrderCost(
    job_code="JOB-100", change_order_number=1,
    description="Add stiffener plates",
    material_impact=2500.0, labor_impact=1500.0, other_impact=200.0,
    created_by="pm1",
)

test("CO ID auto-generated", co.co_id.startswith("CO-"))
test("Created_at auto-set", len(co.created_at) > 0)
test("Total auto-calculated", co.total_impact == 4200.0)
test("Default not approved", not co.approved)

d = co.to_dict()
test("CO to_dict", isinstance(d, dict))
co2 = ChangeOrderCost.from_dict(d)
test("CO from_dict preserves id", co2.co_id == co.co_id)
test("CO from_dict preserves total", co2.total_impact == 4200.0)

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 8: Cost Estimate CRUD ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.job_costing import (
    create_estimate, get_estimate, list_estimates,
    update_estimate, approve_estimate, delete_estimate,
)

t8 = tempfile.mkdtemp()

e1 = create_estimate(t8, "JOB-A", "Original Budget", "pm1",
                      contract_value=200000,
                      line_items=[
                          {"category": "material", "total": 80000},
                          {"category": "labor", "total": 60000},
                      ])
test("Estimate created", e1.estimate_id.startswith("EST-"))
test("Estimate total calculated", e1.total_amount == 140000)
test("Status is draft", e1.status == EST_STATUS_DRAFT)

# Get
got = get_estimate(t8, e1.estimate_id)
test("Get estimate by ID", got is not None)
test("Get estimate matches", got.name == "Original Budget")

test("Get missing estimate returns None", get_estimate(t8, "EST-FAKE") is None)

# List
e2 = create_estimate(t8, "JOB-A", "Rev 1", "pm1", contract_value=210000)
e3 = create_estimate(t8, "JOB-B", "Budget", "pm2", contract_value=150000)

all_ests = list_estimates(t8)
test("List all estimates returns 3", len(all_ests) == 3)

job_a = list_estimates(t8, job_code="JOB-A")
test("Filter by job_code", len(job_a) == 2)

# Update
updated = update_estimate(t8, e1.estimate_id, contract_value=220000,
                            line_items=[{"category": "material", "total": 90000},
                                        {"category": "labor", "total": 65000}])
test("Update estimate", updated is not None)
test("Updated contract value", updated.contract_value == 220000)
test("Updated total recalculated", updated.total_amount == 155000)

# Approve
approved = approve_estimate(t8, e1.estimate_id, "exec1")
test("Approve estimate", approved is not None)
test("Status is approved", approved.status == EST_STATUS_APPROVED)
test("Approved by recorded", approved.approved_by == "exec1")

# Delete
test("Delete estimate", delete_estimate(t8, e2.estimate_id))
test("Delete non-existent returns False", not delete_estimate(t8, "EST-FAKE"))
test("List after delete", len(list_estimates(t8)) == 2)

shutil.rmtree(t8)

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 9: Cost Entry CRUD ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.job_costing import (
    add_cost_entry, get_cost_entry, list_cost_entries, delete_cost_entry,
)

t9 = tempfile.mkdtemp()

c1 = add_cost_entry(t9, "JOB-A", "material", "Steel beams W14x90", "buyer1",
                     quantity=50, unit="ea", unit_cost=450.0,
                     vendor="Steel Depot", po_number="PO-001",
                     date="2026-04-01")
test("Cost entry created", c1.entry_id.startswith("COST-"))
test("Total calculated", c1.total == 22500.0)

c2 = add_cost_entry(t9, "JOB-A", "freight", "Delivery", "buyer1",
                     quantity=1, unit_cost=1200, date="2026-04-02")
c3 = add_cost_entry(t9, "JOB-B", "material", "Bolts", "buyer2",
                     quantity=200, unit="ea", unit_cost=2.50, date="2026-04-03")

# Get
got = get_cost_entry(t9, c1.entry_id)
test("Get cost entry", got is not None)
test("Get cost entry matches", got.vendor == "Steel Depot")

# List
all_costs = list_cost_entries(t9)
test("List all returns 3", len(all_costs) == 3)

job_a_costs = list_cost_entries(t9, job_code="JOB-A")
test("Filter by job_code", len(job_a_costs) == 2)

mat_costs = list_cost_entries(t9, category="material")
test("Filter by category", len(mat_costs) == 2)

date_costs = list_cost_entries(t9, date_from="2026-04-02", date_to="2026-04-03")
test("Filter by date range", len(date_costs) == 2)

# Delete
test("Delete cost entry", delete_cost_entry(t9, c2.entry_id))
test("List after delete", len(list_cost_entries(t9)) == 2)

shutil.rmtree(t9)

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 10: Labor Entry CRUD ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.job_costing import (
    add_labor_entry, get_labor_entry, list_labor_entries, delete_labor_entry,
)

t10 = tempfile.mkdtemp()

l1 = add_labor_entry(t10, "JOB-A", "welder1", 8.0, "foreman1",
                      labor_type="welder", work_order_ref="WO-001",
                      date="2026-04-01")
test("Labor entry created", l1.labor_id.startswith("LAB-"))
test("Rate auto-set", l1.rate == DEFAULT_LABOR_RATES["welder"])
test("Total calculated", l1.total == 8.0 * DEFAULT_LABOR_RATES["welder"])

l2 = add_labor_entry(t10, "JOB-A", "fitter1", 6.0, "foreman1",
                      labor_type="fitter", date="2026-04-01")
l3 = add_labor_entry(t10, "JOB-A", "welder1", 4.0, "foreman1",
                      labor_type="welder", overtime=True, date="2026-04-01")
test("OT labor total", l3.total == 4.0 * DEFAULT_LABOR_RATES["welder"] * 1.5)

l4 = add_labor_entry(t10, "JOB-B", "helper1", 8.0, "foreman2",
                      labor_type="helper", date="2026-04-02")

# Get
got = get_labor_entry(t10, l1.labor_id)
test("Get labor entry", got is not None)
test("Get labor matches worker", got.worker == "welder1")

# List
all_labor = list_labor_entries(t10)
test("List all returns 4", len(all_labor) == 4)

worker_labor = list_labor_entries(t10, worker="welder1")
test("Filter by worker", len(worker_labor) == 2)

job_a_labor = list_labor_entries(t10, job_code="JOB-A")
test("Filter by job_code", len(job_a_labor) == 3)

# Delete
test("Delete labor entry", delete_labor_entry(t10, l4.labor_id))
test("List after delete", len(list_labor_entries(t10)) == 3)

shutil.rmtree(t10)

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 11: Labor Rate Management ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.job_costing import get_labor_rates, update_labor_rates

t11 = tempfile.mkdtemp()

rates = get_labor_rates(t11)
test("Default rates returned", "welder" in rates)
test("Default welder rate", rates["welder"] == DEFAULT_LABOR_RATES["welder"])

# Update
updated = update_labor_rates(t11, {"welder": 40.0, "custom_role": 50.0})
test("Updated welder rate", updated["welder"] == 40.0)
test("Custom rate added", updated["custom_role"] == 50.0)
test("Other rates preserved", updated["fitter"] == DEFAULT_LABOR_RATES["fitter"])

# Verify persistence
rates2 = get_labor_rates(t11)
test("Rates persisted", rates2["welder"] == 40.0)

shutil.rmtree(t11)

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 12: Change Order CRUD ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.job_costing import (
    create_change_order, get_change_order, list_change_orders,
    approve_change_order,
)

t12 = tempfile.mkdtemp()

co1 = create_change_order(t12, "JOB-A", "Add stiffener plates", "pm1",
                           material_impact=3000, labor_impact=2000, other_impact=500)
test("CO created", co1.co_id.startswith("CO-"))
test("CO number is 1", co1.change_order_number == 1)
test("CO total", co1.total_impact == 5500.0)
test("CO not approved", not co1.approved)

co2 = create_change_order(t12, "JOB-A", "Design revision", "pm1",
                           material_impact=1000)
test("CO2 number is 2", co2.change_order_number == 2)

co3 = create_change_order(t12, "JOB-B", "Foundation change", "pm2",
                           labor_impact=5000)
test("Different job CO number is 1", co3.change_order_number == 1)

# Get
got = get_change_order(t12, co1.co_id)
test("Get CO by ID", got is not None)
test("Get CO matches", got.description == "Add stiffener plates")

# List
all_cos = list_change_orders(t12)
test("List all COs returns 3", len(all_cos) == 3)

job_a_cos = list_change_orders(t12, job_code="JOB-A")
test("Filter by job_code", len(job_a_cos) == 2)

# Approve
approved = approve_change_order(t12, co1.co_id, "exec1")
test("Approve CO", approved is not None)
test("CO is approved", approved.approved)
test("Approved by recorded", approved.approved_by == "exec1")
test("Approved at set", len(approved.approved_at) > 0)

# Filter approved only
approved_cos = list_change_orders(t12, approved_only=True)
test("Filter approved only", len(approved_cos) == 1)

shutil.rmtree(t12)

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 13: Job Cost Summary / P&L ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.job_costing import get_job_cost_summary

t13 = tempfile.mkdtemp()

# Setup: estimate + actuals + labor + change order
create_estimate(t13, "JOB-PNL", "Budget", "pm1", contract_value=100000,
                line_items=[
                    {"category": "material", "total": 40000},
                    {"category": "labor", "total": 30000},
                    {"category": "overhead", "total": 10000},
                ])
approve_estimate(t13, list_estimates(t13, job_code="JOB-PNL")[0].estimate_id, "exec1")

# Actual costs
add_cost_entry(t13, "JOB-PNL", "material", "Steel", "buyer1",
               quantity=1, unit_cost=35000, date="2026-04-01")
add_cost_entry(t13, "JOB-PNL", "overhead", "Shop costs", "acct1",
               quantity=1, unit_cost=12000, date="2026-04-01")

# Labor
add_labor_entry(t13, "JOB-PNL", "welder1", 100, "foreman1",
                labor_type="welder", date="2026-04-01")
add_labor_entry(t13, "JOB-PNL", "fitter1", 80, "foreman1",
                labor_type="fitter", date="2026-04-01")

# Change order (approved)
co = create_change_order(t13, "JOB-PNL", "Extra bracing", "pm1",
                          material_impact=5000, labor_impact=3000)
approve_change_order(t13, co.co_id, "exec1")

# Pending CO
create_change_order(t13, "JOB-PNL", "Possible addon", "pm1",
                     material_impact=2000)

summary = get_job_cost_summary(t13, "JOB-PNL")

test("Summary has job_code", summary["job_code"] == "JOB-PNL")
test("Contract value", summary["contract_value"] == 100000)
test("Estimated total", summary["estimated_total"] == 80000)
test("Adjusted budget includes CO", summary["adjusted_budget"] == 80000 + 8000)
test("Adjusted contract includes CO", summary["adjusted_contract"] == 100000 + 8000)

# Actual material
mat_actual = summary["actual_by_category"].get("material", 0)
test("Material actual", mat_actual == 35000)

# Actual labor (from labor entries)
labor_cost = 100 * DEFAULT_LABOR_RATES["welder"] + 80 * DEFAULT_LABOR_RATES["fitter"]
lab_actual = summary["actual_by_category"].get("labor", 0)
test("Labor actual from entries", lab_actual == labor_cost)

test("Total labor hours", summary["total_labor_hours"] == 180)
test("Has labor_by_worker", "welder1" in summary["labor_by_worker"])
test("Has labor_by_type", "welder" in summary["labor_by_type"])

test("Change orders approved count", summary["change_orders_approved"] == 1)
test("Change orders pending count", summary["change_orders_pending"] == 1)
test("Total CO impact", summary["total_co_impact"] == 8000)

test("Has estimate", summary["has_estimate"])
test("Variance calculated", isinstance(summary["cost_variance"], (int, float)))
test("Margin calculated", isinstance(summary["actual_margin"], (int, float)))

shutil.rmtree(t13)

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 14: Cost Variance Report ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.job_costing import get_cost_variance_report

t14 = tempfile.mkdtemp()

create_estimate(t14, "JOB-VAR", "Budget", "pm1", contract_value=50000,
                line_items=[
                    {"category": "material", "total": 20000},
                    {"category": "labor", "total": 15000},
                ])
approve_estimate(t14, list_estimates(t14)[0].estimate_id, "exec1")

add_cost_entry(t14, "JOB-VAR", "material", "Steel", "buyer1",
               quantity=1, unit_cost=22000)  # Over budget
add_cost_entry(t14, "JOB-VAR", "freight", "Delivery", "buyer1",
               quantity=1, unit_cost=800)  # No estimate for freight

report = get_cost_variance_report(t14, "JOB-VAR")

test("Variance report has job_code", report["job_code"] == "JOB-VAR")
test("Variance report has variances list", len(report["variances"]) > 0)
test("Total estimated", report["total_estimated"] == 35000)

# Find material variance
mat_var = None
for v in report["variances"]:
    if v["category"] == "material":
        mat_var = v
        break
test("Material variance found", mat_var is not None)
test("Material over budget", mat_var["over_budget"] == True)
test("Material variance negative", mat_var["variance"] == -2000)

# Freight has no estimate
freight_var = None
for v in report["variances"]:
    if v["category"] == "freight":
        freight_var = v
        break
test("Freight variance found", freight_var is not None)
test("Freight actual", freight_var["actual"] == 800)

shutil.rmtree(t14)

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 15: Financial Overview ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.job_costing import get_financial_overview

t15 = tempfile.mkdtemp()

# Job A — under budget
create_estimate(t15, "JOB-A", "Budget", "pm1", contract_value=100000,
                line_items=[{"category": "material", "total": 60000}])
approve_estimate(t15, list_estimates(t15)[0].estimate_id, "exec1")
add_cost_entry(t15, "JOB-A", "material", "Steel", "buyer1",
               quantity=1, unit_cost=50000)

# Job B — over budget
create_estimate(t15, "JOB-B", "Budget", "pm2", contract_value=50000,
                line_items=[{"category": "material", "total": 30000}])
approve_estimate(t15, list_estimates(t15, job_code="JOB-B")[0].estimate_id, "exec1")
add_cost_entry(t15, "JOB-B", "material", "Steel", "buyer2",
               quantity=1, unit_cost=55000)

overview = get_financial_overview(t15)

test("Overview total jobs", overview["total_jobs"] == 2)
test("Overview total contract", overview["total_contract_value"] == 150000)
test("Overview total actual", overview["total_actual"] == 105000)
test("Overview total margin", overview["total_margin"] == 45000)
test("Overview margin pct", overview["margin_pct"] == 30.0)
test("Overview jobs over budget", overview["jobs_over_budget"] == 1)
test("Overview has costs_by_category", "material" in overview["costs_by_category"])
test("Overview has jobs list", len(overview["jobs"]) == 2)

shutil.rmtree(t15)

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 16: RBAC Permissions ══")
# ═══════════════════════════════════════════════════════════════════

from auth.roles import P, get_role

test("VIEW_FINANCIALS exists", hasattr(P, "VIEW_FINANCIALS"))
test("VIEW_PROJECT_PNL exists", hasattr(P, "VIEW_PROJECT_PNL"))
test("PROCESS_EXPENSES exists", hasattr(P, "PROCESS_EXPENSES"))

god = get_role("god_mode")
test("god_mode has VIEW_FINANCIALS", P.VIEW_FINANCIALS in god.permissions)
test("god_mode has VIEW_PROJECT_PNL", P.VIEW_PROJECT_PNL in god.permissions)
test("god_mode has PROCESS_EXPENSES", P.PROCESS_EXPENSES in god.permissions)

admin = get_role("admin")
test("admin has VIEW_FINANCIALS", P.VIEW_FINANCIALS in admin.permissions)

pm = get_role("project_manager")
test("pm has VIEW_FINANCIALS", P.VIEW_FINANCIALS in pm.permissions)
test("pm has VIEW_PROJECT_PNL", P.VIEW_PROJECT_PNL in pm.permissions)

# Shop floor should NOT have financial access
foreman = get_role("shop_foreman")
test("foreman no VIEW_FINANCIALS", P.VIEW_FINANCIALS not in foreman.permissions)

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 17: Handler Classes Exist ══")
# ═══════════════════════════════════════════════════════════════════

import tf_handlers as tfh

handler_names = [
    "JobCostingPageHandler",
    "EstimateListAPIHandler", "EstimateDetailAPIHandler",
    "EstimateCreateHandler", "EstimateUpdateHandler",
    "EstimateApproveHandler", "EstimateDeleteHandler",
    "CostEntryListAPIHandler", "CostEntryCreateHandler", "CostEntryDeleteHandler",
    "LaborEntryListAPIHandler", "LaborEntryCreateHandler", "LaborEntryDeleteHandler",
    "LaborRatesAPIHandler", "LaborRatesUpdateHandler",
    "ChangeOrderListAPIHandler", "ChangeOrderCreateHandler", "ChangeOrderApproveHandler",
    "JobCostSummaryAPIHandler", "CostVarianceAPIHandler",
    "FinancialOverviewAPIHandler", "CostingConfigHandler",
]

for name in handler_names:
    test(f"Handler {name} exists", hasattr(tfh, name))

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 18: Handler RBAC Permissions ══")
# ═══════════════════════════════════════════════════════════════════

# view_financials handlers
view_fin = [
    "JobCostingPageHandler",
    "EstimateListAPIHandler", "EstimateDetailAPIHandler",
    "EstimateApproveHandler",
    "CostEntryListAPIHandler",
    "LaborEntryListAPIHandler",
    "LaborRatesAPIHandler",
    "ChangeOrderListAPIHandler", "ChangeOrderApproveHandler",
    "FinancialOverviewAPIHandler", "CostingConfigHandler",
]
for name in view_fin:
    cls = getattr(tfh, name)
    test(f"{name} requires view_financials",
         getattr(cls, "required_permission", "") == "view_financials")

# process_expenses handlers
process_exp = [
    "EstimateCreateHandler", "EstimateUpdateHandler", "EstimateDeleteHandler",
    "CostEntryCreateHandler", "CostEntryDeleteHandler",
    "LaborEntryCreateHandler", "LaborEntryDeleteHandler",
    "LaborRatesUpdateHandler",
    "ChangeOrderCreateHandler",
]
for name in process_exp:
    cls = getattr(tfh, name)
    test(f"{name} requires process_expenses",
         getattr(cls, "required_permission", "") == "process_expenses")

# view_project_pnl handlers
pnl_handlers = ["JobCostSummaryAPIHandler", "CostVarianceAPIHandler"]
for name in pnl_handlers:
    cls = getattr(tfh, name)
    test(f"{name} requires view_project_pnl",
         getattr(cls, "required_permission", "") == "view_project_pnl")

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 19: Route Table ══")
# ═══════════════════════════════════════════════════════════════════

routes = tfh.get_routes()
route_map = {}
for r in routes:
    route_map[r[0]] = r[1] if len(r) >= 2 else None

expected_routes = {
    r"/job-costing": "JobCostingPageHandler",
    r"/api/costing/estimates": "EstimateListAPIHandler",
    r"/api/costing/estimate": "EstimateDetailAPIHandler",
    r"/api/costing/estimate/create": "EstimateCreateHandler",
    r"/api/costing/estimate/update": "EstimateUpdateHandler",
    r"/api/costing/estimate/approve": "EstimateApproveHandler",
    r"/api/costing/estimate/delete": "EstimateDeleteHandler",
    r"/api/costing/costs": "CostEntryListAPIHandler",
    r"/api/costing/cost/create": "CostEntryCreateHandler",
    r"/api/costing/cost/delete": "CostEntryDeleteHandler",
    r"/api/costing/labor": "LaborEntryListAPIHandler",
    r"/api/costing/labor/create": "LaborEntryCreateHandler",
    r"/api/costing/labor/delete": "LaborEntryDeleteHandler",
    r"/api/costing/labor-rates": "LaborRatesAPIHandler",
    r"/api/costing/labor-rates/update": "LaborRatesUpdateHandler",
    r"/api/costing/change-orders": "ChangeOrderListAPIHandler",
    r"/api/costing/change-order/create": "ChangeOrderCreateHandler",
    r"/api/costing/change-order/approve": "ChangeOrderApproveHandler",
    r"/api/costing/job-summary": "JobCostSummaryAPIHandler",
    r"/api/costing/variance": "CostVarianceAPIHandler",
    r"/api/costing/overview": "FinancialOverviewAPIHandler",
    r"/api/costing/config": "CostingConfigHandler",
}

for pattern, handler_name in expected_routes.items():
    handler = route_map.get(pattern)
    test(f"Route {pattern} -> {handler_name}",
         handler is not None and handler.__name__ == handler_name)

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 20: Template File ══")
# ═══════════════════════════════════════════════════════════════════

from templates.job_costing_page import JOB_COSTING_PAGE_HTML

test("Template var exists", JOB_COSTING_PAGE_HTML is not None)
test("Template is HTML", "<!DOCTYPE html>" in JOB_COSTING_PAGE_HTML)
test("Template has title", "Job Costing" in JOB_COSTING_PAGE_HTML)
test("Template has estimates tab", "Estimates" in JOB_COSTING_PAGE_HTML)
test("Template has costs tab", "Cost Entries" in JOB_COSTING_PAGE_HTML)
test("Template has labor tab", "Labor" in JOB_COSTING_PAGE_HTML)
test("Template has change orders tab", "Change Orders" in JOB_COSTING_PAGE_HTML)
test("Template has overview tab", "Overview" in JOB_COSTING_PAGE_HTML)
test("Template has config API", "/api/costing/config" in JOB_COSTING_PAGE_HTML)
test("Template has overview API", "/api/costing/overview" in JOB_COSTING_PAGE_HTML)
test("Template has estimate modal", "estimateModal" in JOB_COSTING_PAGE_HTML)
test("Template has cost modal", "costModal" in JOB_COSTING_PAGE_HTML)
test("Template has labor modal", "laborModal" in JOB_COSTING_PAGE_HTML)

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 21: Full E2E — Job Costing Lifecycle ══")
# ═══════════════════════════════════════════════════════════════════

t21 = tempfile.mkdtemp()

# 1. Create estimate
est = create_estimate(t21, "JOB-E2E", "Project Budget", "pm1",
                       contract_value=250000,
                       line_items=[
                           {"category": "material", "description": "Steel", "total": 100000},
                           {"category": "labor", "description": "Fab labor", "total": 80000},
                           {"category": "freight", "description": "Shipping", "total": 15000},
                           {"category": "overhead", "description": "Overhead", "total": 20000},
                       ])
test("E2E: Estimate created", est.total_amount == 215000)
test("E2E: Margin 14%", est.estimated_margin_pct == 14.0)

# 2. Approve estimate
approve_estimate(t21, est.estimate_id, "exec1")

# 3. Record material costs
add_cost_entry(t21, "JOB-E2E", "material", "Steel beams", "buyer1",
               quantity=100, unit="ea", unit_cost=800, date="2026-04-01")
add_cost_entry(t21, "JOB-E2E", "material", "Steel plate", "buyer1",
               quantity=2000, unit="lbs", unit_cost=1.10, date="2026-04-02")
add_cost_entry(t21, "JOB-E2E", "freight", "Truck delivery", "buyer1",
               quantity=3, unit="loads", unit_cost=4500, date="2026-04-03")

# 4. Log labor
add_labor_entry(t21, "JOB-E2E", "welder1", 160, "foreman1",
                labor_type="welder", work_order_ref="WO-001", date="2026-04-01")
add_labor_entry(t21, "JOB-E2E", "fitter1", 120, "foreman1",
                labor_type="fitter", date="2026-04-01")
add_labor_entry(t21, "JOB-E2E", "welder1", 20, "foreman1",
                labor_type="welder", overtime=True, date="2026-04-05")

# 5. Change order
co = create_change_order(t21, "JOB-E2E", "Additional bracing for wind load", "pm1",
                          material_impact=8000, labor_impact=5000, other_impact=1000)
approve_change_order(t21, co.co_id, "exec1")

# 6. Check P&L
summary = get_job_cost_summary(t21, "JOB-E2E")
test("E2E: Has estimate", summary["has_estimate"])
test("E2E: Contract value", summary["contract_value"] == 250000)
test("E2E: Adjusted contract includes CO", summary["adjusted_contract"] == 264000)
test("E2E: Material costs tracked", summary["actual_by_category"]["material"] > 0)
test("E2E: Labor costs tracked", summary["actual_by_category"]["labor"] > 0)
test("E2E: Total labor hours", summary["total_labor_hours"] == 300)
test("E2E: Labor by worker tracked", "welder1" in summary["labor_by_worker"])
test("E2E: CO impact", summary["total_co_impact"] == 14000)

# 7. Variance report
var_report = get_cost_variance_report(t21, "JOB-E2E")
test("E2E: Variance has categories", len(var_report["variances"]) > 0)

# 8. Financial overview
overview = get_financial_overview(t21)
test("E2E: Overview shows 1 job", overview["total_jobs"] == 1)
test("E2E: Overview contract", overview["total_contract_value"] == 250000)

shutil.rmtree(t21)

# ═══════════════════════════════════════════════════════════════════
# CLEANUP & FINAL REPORT
# ═══════════════════════════════════════════════════════════════════

shutil.rmtree(tmp, ignore_errors=True)

print(f"\n{'='*60}")
print(f"Phase 10 Results: {passed} passed, {failed} failed, {passed+failed} total")
print(f"{'='*60}")
if failed:
    sys.exit(1)
