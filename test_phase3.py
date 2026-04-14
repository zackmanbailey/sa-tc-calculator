#!/usr/bin/env python3
"""
TitanForge Phase 3 — QC Module Tests
Tests RBAC migration, QC data model, sign-off workflow with WO integration,
NCR creation/management, item history, dashboard metrics, and traceability.
"""

import sys, os, json, tempfile, shutil, datetime, secrets
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

passed = 0
failed = 0

def test(name, condition):
    global passed, failed
    if condition:
        print(f"  \u2705 {name}")
        passed += 1
    else:
        print(f"  \u274c {name}")
        failed += 1


# ═══════════════════════════════════════════════════════════════════
print("\n\u2550\u2550 TEST 1: AISC Inspection Types \u2550\u2550")
# ═══════════════════════════════════════════════════════════════════
from tf_handlers import AISC_INSPECTION_TYPES, NCR_SEVERITY, NCR_STATUS

test("6 inspection types defined", len(AISC_INSPECTION_TYPES) == 6)
test("bolt_inspection exists", "bolt_inspection" in AISC_INSPECTION_TYPES)
test("weld_visual exists", "weld_visual" in AISC_INSPECTION_TYPES)
test("dimensional exists", "dimensional" in AISC_INSPECTION_TYPES)
test("surface_prep exists", "surface_prep" in AISC_INSPECTION_TYPES)
test("nde exists", "nde" in AISC_INSPECTION_TYPES)
test("material_receiving exists", "material_receiving" in AISC_INSPECTION_TYPES)

# Each type has label, standard, checklist
for itype, idata in AISC_INSPECTION_TYPES.items():
    test(f"{itype} has label", "label" in idata)
    test(f"{itype} has standard", "standard" in idata)
    test(f"{itype} has checklist", "checklist" in idata and len(idata["checklist"]) > 0)
    for ci in idata["checklist"]:
        test(f"  {itype}/{ci['key']} has key, label, type", all(k in ci for k in ["key", "label", "type"]))

test("NCR severities: minor/major/critical", NCR_SEVERITY == ["minor", "major", "critical"])
test("NCR statuses include open/closed/voided",
     all(s in NCR_STATUS for s in ["open", "closed", "voided"]))


# ═══════════════════════════════════════════════════════════════════
print("\n\u2550\u2550 TEST 2: QC Data Storage (load/save) \u2550\u2550")
# ═══════════════════════════════════════════════════════════════════
import tf_handlers as tfh

# Override QC_DIR to use temp
ORIG_QC_DIR = tfh.QC_DIR
TEST_QC_DIR = tempfile.mkdtemp(prefix="tf_qc_test_")
tfh.QC_DIR = TEST_QC_DIR

qc_data = tfh.load_project_qc("TEST-001")
test("Empty project returns default structure", qc_data == {"inspections": [], "ncrs": [], "traceability": []})

# Save and reload
qc_data["inspections"].append({"id": "INS-TEST-001", "type": "weld_visual", "status": "in_progress"})
tfh.save_project_qc("TEST-001", qc_data)
reloaded = tfh.load_project_qc("TEST-001")
test("Saved QC data persists", len(reloaded["inspections"]) == 1)
test("Inspection ID correct", reloaded["inspections"][0]["id"] == "INS-TEST-001")
test("save adds updated_at", "updated_at" in reloaded)


# ═══════════════════════════════════════════════════════════════════
print("\n\u2550\u2550 TEST 3: RBAC Permission Mapping \u2550\u2550")
# ═══════════════════════════════════════════════════════════════════
from auth.roles import ROLES, P

# Find QC inspector role
qc_role = ROLES.get("qc_inspector")

test("qc_inspector role exists", qc_role is not None)
if qc_role:
    perms = [p.value if hasattr(p, 'value') else p for p in qc_role.permissions]
    test("qc_inspector has view_qc", "view_qc" in perms)
    test("qc_inspector has perform_inspections", "perform_inspections" in perms)
    test("qc_inspector has sign_off_qc", "sign_off_qc" in perms)
    test("qc_inspector has reject_qc_items", "reject_qc_items" in perms)
    test("qc_inspector has create_ncr", "create_ncr" in perms)
    test("qc_inspector has view_aisc_library", "view_aisc_library" in perms)
    test("qc_inspector has manage_mill_certs", "manage_mill_certs" in perms)
    test("qc_inspector is mobile_first", qc_role.mobile_first)

# Check that relevant handlers use required_permission (not required_roles)
test("QCInspectionCreateHandler uses required_permission",
     getattr(tfh.QCInspectionCreateHandler, 'required_permission', None) == "perform_inspections")
test("QCInspectionUpdateHandler uses required_permission",
     getattr(tfh.QCInspectionUpdateHandler, 'required_permission', None) == "perform_inspections")
test("NCRCreateHandler uses required_permission",
     getattr(tfh.NCRCreateHandler, 'required_permission', None) == "create_ncr")
test("NCRUpdateHandler uses required_permission",
     getattr(tfh.NCRUpdateHandler, 'required_permission', None) == "create_ncr")
test("TraceabilityRegisterHandler uses required_permission",
     getattr(tfh.TraceabilityRegisterHandler, 'required_permission', None) == "manage_mill_certs")
test("TraceabilityAssignHandler uses required_permission",
     getattr(tfh.TraceabilityAssignHandler, 'required_permission', None) == "manage_mill_certs")
test("QCPageHandler uses required_permission",
     getattr(tfh.QCPageHandler, 'required_permission', None) == "view_qc")
test("QCInspectionQueuePageHandler uses required_permission",
     getattr(tfh.QCInspectionQueuePageHandler, 'required_permission', None) == "perform_inspections")
test("QCDashboardPageHandler uses required_permission",
     getattr(tfh.QCDashboardPageHandler, 'required_permission', None) == "view_qc")
test("QCSignOffHandler uses required_permission",
     getattr(tfh.QCSignOffHandler, 'required_permission', None) == "sign_off_qc")
test("QCDashboardAPIHandler uses required_permission",
     getattr(tfh.QCDashboardAPIHandler, 'required_permission', None) == "view_qc")
test("QCItemHistoryHandler uses required_permission",
     getattr(tfh.QCItemHistoryHandler, 'required_permission', None) == "view_qc")
test("NCRDetailHandler uses required_permission",
     getattr(tfh.NCRDetailHandler, 'required_permission', None) == "view_qc")

# Verify NO old required_roles on QC handlers
for cls_name in ["QCInspectionCreateHandler", "QCInspectionUpdateHandler",
                  "NCRCreateHandler", "NCRUpdateHandler",
                  "TraceabilityRegisterHandler", "TraceabilityAssignHandler",
                  "QCPageHandler"]:
    cls = getattr(tfh, cls_name)
    old_roles = getattr(cls, 'required_roles', None)
    test(f"{cls_name} has NO old required_roles", old_roles is None)


# ═══════════════════════════════════════════════════════════════════
print("\n\u2550\u2550 TEST 4: Inspection CRUD \u2550\u2550")
# ═══════════════════════════════════════════════════════════════════
JOB = "QC-TEST-PROJECT"

# Create fresh QC data
tfh.save_project_qc(JOB, {"inspections": [], "ncrs": [], "traceability": []})

# Simulate creating an inspection
now = datetime.datetime.now()
inspection = {
    "id": "INS-" + now.strftime("%Y%m%d%H%M%S") + "-" + secrets.token_hex(3).upper(),
    "type": "weld_visual",
    "type_label": AISC_INSPECTION_TYPES["weld_visual"]["label"],
    "standard": AISC_INSPECTION_TYPES["weld_visual"]["standard"],
    "status": "in_progress",
    "inspector": "testuser",
    "location": "Bay 3",
    "member_marks": ["C1", "B2"],
    "items": {},
    "notes": "Initial weld check",
    "photos": [],
    "created_at": now.isoformat(),
    "completed_at": None,
}

qc = tfh.load_project_qc(JOB)
qc["inspections"].append(inspection)
tfh.save_project_qc(JOB, qc)

reloaded = tfh.load_project_qc(JOB)
test("Inspection was saved", len(reloaded["inspections"]) == 1)
test("Inspection ID starts with INS-", reloaded["inspections"][0]["id"].startswith("INS-"))
test("Inspection type is weld_visual", reloaded["inspections"][0]["type"] == "weld_visual")
test("Inspection has AISC standard", "AISC 360" in reloaded["inspections"][0]["standard"] or "AWS D1.1" in reloaded["inspections"][0]["standard"])
test("Inspection has member_marks", reloaded["inspections"][0]["member_marks"] == ["C1", "B2"])
test("Inspection status is in_progress", reloaded["inspections"][0]["status"] == "in_progress")

# Update inspection (simulate checklist fill)
reloaded["inspections"][0]["items"] = {
    "wps_available": True,
    "welder_qualified": True,
    "weld_size": True,
    "weld_length": True,
    "cracks": True,
}
reloaded["inspections"][0]["status"] = "passed"
reloaded["inspections"][0]["completed_at"] = datetime.datetime.now().isoformat()
reloaded["inspections"][0]["signed_off_by"] = "qc_inspector_1"
tfh.save_project_qc(JOB, reloaded)

final = tfh.load_project_qc(JOB)
test("Checklist items saved", len(final["inspections"][0]["items"]) == 5)
test("Status changed to passed", final["inspections"][0]["status"] == "passed")
test("completed_at was set", final["inspections"][0]["completed_at"] is not None)
test("signed_off_by recorded", final["inspections"][0]["signed_off_by"] == "qc_inspector_1")


# ═══════════════════════════════════════════════════════════════════
print("\n\u2550\u2550 TEST 5: NCR CRUD \u2550\u2550")
# ═══════════════════════════════════════════════════════════════════
qc = tfh.load_project_qc(JOB)
ncr_num = len(qc["ncrs"]) + 1
ncr = {
    "id": f"NCR-{JOB}-{ncr_num:03d}",
    "number": ncr_num,
    "severity": "major",
    "status": "open",
    "title": "Weld crack detected on C1",
    "description": "Visible crack at flange-web junction, approx 2 inches",
    "member_marks": ["C1"],
    "inspection_id": inspection["id"],
    "root_cause": "",
    "corrective_action": "",
    "preventive_action": "",
    "disposition": "rework",
    "reported_by": "testuser",
    "assigned_to": "shop_foreman",
    "photos": [],
    "created_at": now.isoformat(),
    "closed_at": None,
    "history": [
        {"action": "created", "by": "testuser", "at": now.isoformat()}
    ],
}

qc["ncrs"].append(ncr)
tfh.save_project_qc(JOB, qc)

reloaded = tfh.load_project_qc(JOB)
test("NCR saved", len(reloaded["ncrs"]) == 1)
test("NCR ID format correct", reloaded["ncrs"][0]["id"] == f"NCR-{JOB}-001")
test("NCR severity is major", reloaded["ncrs"][0]["severity"] == "major")
test("NCR status is open", reloaded["ncrs"][0]["status"] == "open")
test("NCR links to inspection", reloaded["ncrs"][0]["inspection_id"] == inspection["id"])
test("NCR has member_marks", reloaded["ncrs"][0]["member_marks"] == ["C1"])
test("NCR has history", len(reloaded["ncrs"][0]["history"]) == 1)
test("NCR disposition is rework", reloaded["ncrs"][0]["disposition"] == "rework")

# Update NCR: add corrective action
reloaded["ncrs"][0]["corrective_action"] = "Gouge out crack, re-weld per WPS"
reloaded["ncrs"][0]["status"] = "corrective_action"
reloaded["ncrs"][0]["history"].append({
    "action": "updated (corrective_action, status)",
    "by": "shop_foreman",
    "at": datetime.datetime.now().isoformat(),
})
tfh.save_project_qc(JOB, reloaded)

final = tfh.load_project_qc(JOB)
test("NCR corrective action saved", "Gouge out" in final["ncrs"][0]["corrective_action"])
test("NCR status is corrective_action", final["ncrs"][0]["status"] == "corrective_action")
test("NCR history has 2 entries", len(final["ncrs"][0]["history"]) == 2)

# Close NCR
final["ncrs"][0]["status"] = "closed"
final["ncrs"][0]["closed_at"] = datetime.datetime.now().isoformat()
final["ncrs"][0]["closed_by"] = "qc_inspector_1"
final["ncrs"][0]["history"].append({
    "action": "closed", "by": "qc_inspector_1",
    "at": datetime.datetime.now().isoformat(),
})
tfh.save_project_qc(JOB, final)

closed = tfh.load_project_qc(JOB)
test("NCR closed successfully", closed["ncrs"][0]["status"] == "closed")
test("NCR closed_at set", closed["ncrs"][0]["closed_at"] is not None)
test("NCR closed_by recorded", closed["ncrs"][0]["closed_by"] == "qc_inspector_1")


# ═══════════════════════════════════════════════════════════════════
print("\n\u2550\u2550 TEST 6: WO Integration — QC Items Needing Inspection \u2550\u2550")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.work_orders import (
    WorkOrder, WorkOrderItem, STATUS_QUEUED, STATUS_APPROVED,
    STATUS_STICKERS_PRINTED, STATUS_STAGED, STATUS_IN_PROGRESS,
    STATUS_FABRICATED, STATUS_QC_PENDING, STATUS_QC_APPROVED,
    STATUS_QC_REJECTED, STATUS_READY_TO_SHIP,
    save_work_order, load_work_order,
    assign_item, transition_item_status,
    PHASE_QC,
)

WO_TEST_DIR = tempfile.mkdtemp(prefix="tf_wo_qc_test_")
WO_JOB = "QC-WO-TEST"

# Create a WO with items at various stages
wo = WorkOrder(
    work_order_id="WO-QC-001",
    job_code=WO_JOB,
    items=[
        WorkOrderItem(item_id="QC-1", ship_mark="C1", component_type="column",
                      description="Column 1", machine="WELDING", status=STATUS_FABRICATED),
        WorkOrderItem(item_id="QC-2", ship_mark="B2", component_type="beam",
                      description="Beam 2", machine="Z1", status=STATUS_QC_PENDING),
        WorkOrderItem(item_id="QC-3", ship_mark="W3", component_type="weld",
                      description="Weld 3", machine="WELDING", status=STATUS_IN_PROGRESS),
        WorkOrderItem(item_id="QC-4", ship_mark="P4", component_type="panel",
                      description="Panel 4", machine="P1", status=STATUS_QC_APPROVED),
    ],
)
save_work_order(WO_TEST_DIR, wo)

# Test items_needing_qc
loaded_wo = load_work_order(WO_TEST_DIR, WO_JOB, "WO-QC-001")
qc_items = loaded_wo.items_needing_qc()
test("2 items need QC (fabricated + qc_pending)", len(qc_items) == 2)
qc_item_ids = [i.item_id for i in qc_items]
test("QC-1 (fabricated) needs QC", "QC-1" in qc_item_ids)
test("QC-2 (qc_pending) needs QC", "QC-2" in qc_item_ids)
test("QC-3 (in_progress) does NOT need QC", "QC-3" not in qc_item_ids)
test("QC-4 (qc_approved) does NOT need QC", "QC-4" not in qc_item_ids)

# Test PHASE_QC constant
test("PHASE_QC includes qc_pending", STATUS_QC_PENDING in PHASE_QC)
test("PHASE_QC includes qc_approved", STATUS_QC_APPROVED in PHASE_QC)
test("PHASE_QC includes qc_rejected", STATUS_QC_REJECTED in PHASE_QC)


# ═══════════════════════════════════════════════════════════════════
print("\n\u2550\u2550 TEST 7: WO Status Transitions — QC Flow \u2550\u2550")
# ═══════════════════════════════════════════════════════════════════

# fabricated → qc_pending
result = transition_item_status(WO_TEST_DIR, WO_JOB, "QC-1", STATUS_QC_PENDING, "inspector1")
test("fabricated → qc_pending succeeds", result.get("ok") == True)

wo_check = load_work_order(WO_TEST_DIR, WO_JOB, "WO-QC-001")
item_1 = next(i for i in wo_check.items if i.item_id == "QC-1")
test("Item QC-1 is now qc_pending", item_1.status == STATUS_QC_PENDING)

# qc_pending → qc_approved
result = transition_item_status(WO_TEST_DIR, WO_JOB, "QC-1", STATUS_QC_APPROVED, "inspector1",
                                notes="All weld checks passed")
test("qc_pending → qc_approved succeeds", result.get("ok") == True)

wo_check = load_work_order(WO_TEST_DIR, WO_JOB, "WO-QC-001")
item_1 = next(i for i in wo_check.items if i.item_id == "QC-1")
test("Item QC-1 is now qc_approved", item_1.status == STATUS_QC_APPROVED)
test("QC inspector recorded", item_1.qc_inspector == "inspector1")
test("QC result is approved", item_1.qc_result == "approved")

# qc_pending → qc_rejected
result = transition_item_status(WO_TEST_DIR, WO_JOB, "QC-2", STATUS_QC_REJECTED, "inspector1",
                                notes="Weld crack at junction")
test("qc_pending → qc_rejected succeeds", result.get("ok") == True)

wo_check = load_work_order(WO_TEST_DIR, WO_JOB, "WO-QC-001")
item_2 = next(i for i in wo_check.items if i.item_id == "QC-2")
test("Item QC-2 is now qc_rejected", item_2.status == STATUS_QC_REJECTED)
test("QC result is rejected", item_2.qc_result == "rejected")
test("QC notes saved", item_2.qc_notes == "Weld crack at junction")

# qc_rejected → in_progress (rework)
result = transition_item_status(WO_TEST_DIR, WO_JOB, "QC-2", STATUS_IN_PROGRESS, "operator1",
                                notes="Rework started")
test("qc_rejected → in_progress succeeds (rework)", result.get("ok") == True)

wo_check = load_work_order(WO_TEST_DIR, WO_JOB, "WO-QC-001")
item_2 = next(i for i in wo_check.items if i.item_id == "QC-2")
test("Item QC-2 back to in_progress for rework", item_2.status == STATUS_IN_PROGRESS)

# Invalid: try to go from qc_approved → in_progress (not allowed)
result = transition_item_status(WO_TEST_DIR, WO_JOB, "QC-1", STATUS_IN_PROGRESS, "someone")
test("qc_approved → in_progress is blocked", result.get("ok") == False)

# qc_approved → ready_to_ship
result = transition_item_status(WO_TEST_DIR, WO_JOB, "QC-1", STATUS_READY_TO_SHIP, "shipper1")
test("qc_approved → ready_to_ship succeeds", result.get("ok") == True)


# ═══════════════════════════════════════════════════════════════════
print("\n\u2550\u2550 TEST 8: WO Auto-Status Recompute with QC \u2550\u2550")
# ═══════════════════════════════════════════════════════════════════

# Create a WO where all items are qc_approved
wo2 = WorkOrder(
    work_order_id="WO-QC-002",
    job_code=WO_JOB,
    items=[
        WorkOrderItem(item_id="R1", ship_mark="R1", component_type="column",
                      description="R1", machine="Z1", status=STATUS_QC_APPROVED),
        WorkOrderItem(item_id="R2", ship_mark="R2", component_type="beam",
                      description="R2", machine="Z1", status=STATUS_QC_APPROVED),
    ],
)
wo2.recompute_status()
test("All qc_approved → WO status is qc_approved", wo2.status == STATUS_QC_APPROVED)

# Mix of fabricated and qc_pending
wo3 = WorkOrder(
    work_order_id="WO-QC-003",
    job_code=WO_JOB,
    items=[
        WorkOrderItem(item_id="M1", ship_mark="M1", component_type="column",
                      description="M1", machine="Z1", status=STATUS_FABRICATED),
        WorkOrderItem(item_id="M2", ship_mark="M2", component_type="beam",
                      description="M2", machine="Z1", status=STATUS_QC_PENDING),
        WorkOrderItem(item_id="M3", ship_mark="M3", component_type="beam",
                      description="M3", machine="Z1", status=STATUS_QC_APPROVED),
    ],
)
wo3.recompute_status()
test("Mixed fabricated/qc states → WO status is fabricated", wo3.status == STATUS_FABRICATED)

# Items needing QC count
test("WO3 has 2 items needing QC", len(wo3.items_needing_qc()) == 2)
test("WO3 qc_pending_items is 1", wo3.qc_pending_items == 1)


# ═══════════════════════════════════════════════════════════════════
print("\n\u2550\u2550 TEST 9: Material Traceability \u2550\u2550")
# ═══════════════════════════════════════════════════════════════════

# Override traceability paths
ORIG_BASE = tfh.BASE_DIR
TRACE_DIR = tempfile.mkdtemp(prefix="tf_trace_test_")
tfh.BASE_DIR = TRACE_DIR
os.makedirs(os.path.join(TRACE_DIR, "data"), exist_ok=True)

idx = tfh.load_traceability_index()
test("Empty traceability index", idx == {"heat_numbers": {}})

# Register heat number
result = tfh.register_heat_number("H-12345", "COIL-A001", "A572 Gr 50", "Nucor", "")
test("Heat number registered", "material_spec" in result)
test("Coil tracked", len(result["coils"]) == 1)
test("Coil tag correct", result["coils"][0]["coil_tag"] == "COIL-A001")

# Register same heat with different coil
result = tfh.register_heat_number("H-12345", "COIL-A002", "A572 Gr 50", "Nucor", "")
test("Second coil added to same heat", len(result["coils"]) == 2)

# Don't duplicate coil
result = tfh.register_heat_number("H-12345", "COIL-A001", "A572 Gr 50", "Nucor", "")
test("Duplicate coil NOT added", len(result["coils"]) == 2)

# Assign member to heat (need QC_DIR set for the project QC side)
tfh.QC_DIR = TEST_QC_DIR
tfh.save_project_qc("TRACE-JOB", {"inspections": [], "ncrs": [], "traceability": []})
tfh.assign_member_to_heat("H-12345", "TRACE-JOB", "C1", "W12x26 column")

idx = tfh.load_traceability_index()
test("Member assigned in traceability index", len(idx["heat_numbers"]["H-12345"]["members"]) == 1)
test("Member mark correct", idx["heat_numbers"]["H-12345"]["members"][0]["member_mark"] == "C1")
test("Job code tracked", idx["heat_numbers"]["H-12345"]["members"][0]["job_code"] == "TRACE-JOB")

# Check project QC also updated
qc = tfh.load_project_qc("TRACE-JOB")
test("Traceability added to project QC", len(qc["traceability"]) == 1)
test("Project trace has heat number", qc["traceability"][0]["heat_number"] == "H-12345")

# Restore
tfh.BASE_DIR = ORIG_BASE


# ═══════════════════════════════════════════════════════════════════
print("\n\u2550\u2550 TEST 10: Inspection Types — Checklist Completeness \u2550\u2550")
# ═══════════════════════════════════════════════════════════════════

# Verify checklist items have valid types
VALID_TYPES = {"check", "select", "text"}
for itype, idata in AISC_INSPECTION_TYPES.items():
    for ci in idata["checklist"]:
        test(f"{itype}/{ci['key']} type is valid ({ci['type']})", ci["type"] in VALID_TYPES)
        if ci["type"] == "select":
            test(f"  {ci['key']} has options", "options" in ci and len(ci["options"]) > 0)

# Weld visual has critical checks
wv = AISC_INSPECTION_TYPES["weld_visual"]
wv_keys = [ci["key"] for ci in wv["checklist"]]
test("Weld visual checks WPS", "wps_available" in wv_keys)
test("Weld visual checks cracks", "cracks" in wv_keys)
test("Weld visual checks porosity", "porosity" in wv_keys)
test("Weld visual checks welder qual", "welder_qualified" in wv_keys)

# Bolt inspection has RCSC checks
bi = AISC_INSPECTION_TYPES["bolt_inspection"]
bi_keys = [ci["key"] for ci in bi["checklist"]]
test("Bolt inspection checks grade", "bolt_grade" in bi_keys)
test("Bolt inspection checks snug tight", "snug_tight" in bi_keys)
test("Bolt inspection checks pretension method", "pretension_method" in bi_keys)


# ═══════════════════════════════════════════════════════════════════
print("\n\u2550\u2550 TEST 11: Multiple Inspections per Project \u2550\u2550")
# ═══════════════════════════════════════════════════════════════════
MULTI_JOB = "MULTI-INSP-TEST"
tfh.save_project_qc(MULTI_JOB, {"inspections": [], "ncrs": [], "traceability": []})

# Add multiple inspections
for i, itype in enumerate(["weld_visual", "dimensional", "bolt_inspection"]):
    qc = tfh.load_project_qc(MULTI_JOB)
    insp = {
        "id": f"INS-MULTI-{i:03d}",
        "type": itype,
        "type_label": AISC_INSPECTION_TYPES[itype]["label"],
        "standard": AISC_INSPECTION_TYPES[itype]["standard"],
        "status": "passed" if i < 2 else "failed",
        "inspector": f"inspector_{i}",
        "location": f"Bay {i+1}",
        "member_marks": [f"M{i+1}"],
        "items": {},
        "notes": f"Test inspection {i}",
        "photos": [],
        "created_at": datetime.datetime.now().isoformat(),
        "completed_at": datetime.datetime.now().isoformat(),
    }
    qc["inspections"].append(insp)
    tfh.save_project_qc(MULTI_JOB, qc)

final = tfh.load_project_qc(MULTI_JOB)
test("3 inspections in project", len(final["inspections"]) == 3)
test("2 passed inspections", sum(1 for i in final["inspections"] if i["status"] == "passed") == 2)
test("1 failed inspection", sum(1 for i in final["inspections"] if i["status"] == "failed") == 1)
test("Inspections have different types",
     len(set(i["type"] for i in final["inspections"])) == 3)


# ═══════════════════════════════════════════════════════════════════
print("\n\u2550\u2550 TEST 12: NCR Severity Levels & Disposition \u2550\u2550")
# ═══════════════════════════════════════════════════════════════════
NCR_JOB = "NCR-SEV-TEST"
tfh.save_project_qc(NCR_JOB, {"inspections": [], "ncrs": [], "traceability": []})

for sev in ["minor", "major", "critical"]:
    qc = tfh.load_project_qc(NCR_JOB)
    ncr = {
        "id": f"NCR-{NCR_JOB}-{len(qc['ncrs'])+1:03d}",
        "number": len(qc["ncrs"]) + 1,
        "severity": sev,
        "status": "open",
        "title": f"Test {sev} NCR",
        "description": f"Description for {sev} NCR",
        "member_marks": [],
        "inspection_id": "",
        "root_cause": "",
        "corrective_action": "",
        "preventive_action": "",
        "disposition": "rework" if sev != "critical" else "reject",
        "reported_by": "tester",
        "assigned_to": "",
        "photos": [],
        "created_at": datetime.datetime.now().isoformat(),
        "closed_at": None,
        "history": [{"action": "created", "by": "tester", "at": datetime.datetime.now().isoformat()}],
    }
    qc["ncrs"].append(ncr)
    tfh.save_project_qc(NCR_JOB, qc)

final = tfh.load_project_qc(NCR_JOB)
test("3 NCRs created", len(final["ncrs"]) == 3)
test("Minor NCR exists", any(n["severity"] == "minor" for n in final["ncrs"]))
test("Major NCR exists", any(n["severity"] == "major" for n in final["ncrs"]))
test("Critical NCR exists", any(n["severity"] == "critical" for n in final["ncrs"]))
test("Critical disposition is reject",
     next(n for n in final["ncrs"] if n["severity"] == "critical")["disposition"] == "reject")
test("Minor disposition is rework",
     next(n for n in final["ncrs"] if n["severity"] == "minor")["disposition"] == "rework")


# ═══════════════════════════════════════════════════════════════════
print("\n\u2550\u2550 TEST 13: NCR Status Workflow \u2550\u2550")
# ═══════════════════════════════════════════════════════════════════
FLOW_JOB = "NCR-FLOW-TEST"
tfh.save_project_qc(FLOW_JOB, {"inspections": [], "ncrs": [], "traceability": []})

ncr = {
    "id": f"NCR-{FLOW_JOB}-001",
    "number": 1,
    "severity": "major",
    "status": "open",
    "title": "Dimension out of tolerance",
    "description": "Member B3 is 1/4\" short",
    "member_marks": ["B3"],
    "inspection_id": "",
    "root_cause": "",
    "corrective_action": "",
    "preventive_action": "",
    "disposition": "",
    "reported_by": "inspector_1",
    "assigned_to": "shop_foreman",
    "photos": [],
    "created_at": datetime.datetime.now().isoformat(),
    "closed_at": None,
    "history": [{"action": "created", "by": "inspector_1", "at": datetime.datetime.now().isoformat()}],
}
qc = {"inspections": [], "ncrs": [ncr], "traceability": []}
tfh.save_project_qc(FLOW_JOB, qc)

# Walk through NCR lifecycle
statuses = ["under_review", "corrective_action", "re_inspect", "closed"]
for new_status in statuses:
    qc = tfh.load_project_qc(FLOW_JOB)
    qc["ncrs"][0]["status"] = new_status
    if new_status == "corrective_action":
        qc["ncrs"][0]["corrective_action"] = "Re-cut member to correct length"
        qc["ncrs"][0]["root_cause"] = "Programming error in CNC"
    if new_status == "closed":
        qc["ncrs"][0]["closed_at"] = datetime.datetime.now().isoformat()
        qc["ncrs"][0]["disposition"] = "rework"
        qc["ncrs"][0]["preventive_action"] = "Add dimensional check to CNC output"
    qc["ncrs"][0]["history"].append({
        "action": f"status changed to {new_status}",
        "by": "test_user",
        "at": datetime.datetime.now().isoformat(),
    })
    tfh.save_project_qc(FLOW_JOB, qc)

final = tfh.load_project_qc(FLOW_JOB)
ncr_final = final["ncrs"][0]
test("NCR ended at closed", ncr_final["status"] == "closed")
test("NCR has root_cause", ncr_final["root_cause"] == "Programming error in CNC")
test("NCR has corrective_action", "Re-cut" in ncr_final["corrective_action"])
test("NCR has preventive_action", "dimensional check" in ncr_final["preventive_action"])
test("NCR has disposition", ncr_final["disposition"] == "rework")
test("NCR closed_at set", ncr_final["closed_at"] is not None)
test("NCR history has 5 entries (create + 4 status changes)", len(ncr_final["history"]) == 5)


# ═══════════════════════════════════════════════════════════════════
print("\n\u2550\u2550 TEST 14: New Handler Classes Exist \u2550\u2550")
# ═══════════════════════════════════════════════════════════════════

test("QCInspectionQueuePageHandler exists", hasattr(tfh, 'QCInspectionQueuePageHandler'))
test("QCInspectionQueueAPIHandler exists", hasattr(tfh, 'QCInspectionQueueAPIHandler'))
test("QCSignOffHandler exists", hasattr(tfh, 'QCSignOffHandler'))
test("QCDashboardAPIHandler exists", hasattr(tfh, 'QCDashboardAPIHandler'))
test("QCDashboardPageHandler exists", hasattr(tfh, 'QCDashboardPageHandler'))
test("QCItemHistoryHandler exists", hasattr(tfh, 'QCItemHistoryHandler'))
test("NCRDetailHandler exists", hasattr(tfh, 'NCRDetailHandler'))


# ═══════════════════════════════════════════════════════════════════
print("\n\u2550\u2550 TEST 15: Route Table — New QC Routes \u2550\u2550")
# ═══════════════════════════════════════════════════════════════════
routes = tfh.get_routes()
route_paths = [r[0] if isinstance(r, tuple) else r.regex.pattern for r in routes]

test("/qc-queue route exists", any("/qc-queue" in p for p in route_paths))
test("/qc-dashboard route exists", any("/qc-dashboard" in p for p in route_paths))
test("/api/qc/queue route exists", any("/api/qc/queue" in p for p in route_paths))
test("/api/qc/sign-off route exists", any("/api/qc/sign-off" in p for p in route_paths))
test("/api/qc/dashboard route exists", any("/api/qc/dashboard" in p for p in route_paths))
test("/api/qc/item-history route exists", any("/api/qc/item-history" in p for p in route_paths))
test("/api/qc/ncr/detail route exists", any("/api/qc/ncr/detail" in p for p in route_paths))
# Original routes still present
test("/qc/{job_code} route exists", any(r"/qc/([^/]+)" in p for p in route_paths))
test("/api/qc/types route exists", any("/api/qc/types" in p for p in route_paths))
test("/api/qc/data route exists", any("/api/qc/data" in p for p in route_paths))
test("/api/qc/inspection/create route exists", any("/api/qc/inspection/create" in p for p in route_paths))
test("/api/qc/inspection/update route exists", any("/api/qc/inspection/update" in p for p in route_paths))
test("/api/qc/ncr/create route exists", any("/api/qc/ncr/create" in p for p in route_paths))
test("/api/qc/ncr/update route exists", any("/api/qc/ncr/update" in p for p in route_paths))


# ═══════════════════════════════════════════════════════════════════
print("\n\u2550\u2550 TEST 16: Template Files Exist \u2550\u2550")
# ═══════════════════════════════════════════════════════════════════
from templates.qc_queue_page import QC_QUEUE_PAGE_HTML
from templates.qc_dashboard_page import QC_DASHBOARD_PAGE_HTML
from templates.qc_page import QC_PAGE_HTML

test("QC_QUEUE_PAGE_HTML is non-empty", len(QC_QUEUE_PAGE_HTML) > 100)
test("QC_DASHBOARD_PAGE_HTML is non-empty", len(QC_DASHBOARD_PAGE_HTML) > 100)
test("QC_PAGE_HTML is non-empty (existing)", len(QC_PAGE_HTML) > 100)

# Check key content in templates
test("Queue page has sign-off modal", "signOffModal" in QC_QUEUE_PAGE_HTML)
test("Queue page calls /api/qc/queue", "/api/qc/queue" in QC_QUEUE_PAGE_HTML)
test("Queue page calls /api/qc/sign-off", "/api/qc/sign-off" in QC_QUEUE_PAGE_HTML)
test("Queue page has AISC inspection types", "weld_visual" in QC_QUEUE_PAGE_HTML)
test("Queue page has NCR auto-create", "ncrAutoCreate" in QC_QUEUE_PAGE_HTML)
test("Queue page has checklist grid", "signOffChecklist" in QC_QUEUE_PAGE_HTML)
test("Queue page has machine filter", "filterMachine" in QC_QUEUE_PAGE_HTML)

test("Dashboard page calls /api/qc/dashboard", "/api/qc/dashboard" in QC_DASHBOARD_PAGE_HTML)
test("Dashboard page has pass rate gauge", "gauge-ring" in QC_DASHBOARD_PAGE_HTML)
test("Dashboard page has NCR severity", "severity-badge" in QC_DASHBOARD_PAGE_HTML)
test("Dashboard page has inspector workload", "inspectorTable" in QC_DASHBOARD_PAGE_HTML)
test("Dashboard page links to queue", "/qc-queue" in QC_DASHBOARD_PAGE_HTML)


# ═══════════════════════════════════════════════════════════════════
print("\n\u2550\u2550 TEST 17: WorkOrderItem QC Fields \u2550\u2550")
# ═══════════════════════════════════════════════════════════════════

item = WorkOrderItem(
    item_id="QC-FIELD-TEST", ship_mark="T1", component_type="test",
    description="Field test", machine="Z1", status=STATUS_FABRICATED,
)

test("qc_inspector defaults empty", item.qc_inspector == "")
test("qc_at defaults empty", item.qc_at == "")
test("qc_result defaults empty", item.qc_result == "")
test("qc_notes defaults empty", item.qc_notes == "")

# After QC approval transition
item.status = STATUS_QC_APPROVED
item.qc_inspector = "inspector_joe"
item.qc_at = datetime.datetime.now().isoformat()
item.qc_result = "approved"
item.qc_notes = "All checks passed"

d = item.to_dict()
test("to_dict includes qc_inspector", d["qc_inspector"] == "inspector_joe")
test("to_dict includes qc_result", d["qc_result"] == "approved")
test("to_dict includes qc_notes", d["qc_notes"] == "All checks passed")

# Rebuild from dict
from shop_drawings.work_orders import WorkOrderItem
item2 = WorkOrderItem.from_dict(d)
test("from_dict preserves qc_inspector", item2.qc_inspector == "inspector_joe")
test("from_dict preserves qc_result", item2.qc_result == "approved")


# ═══════════════════════════════════════════════════════════════════
print("\n\u2550\u2550 TEST 18: QC Rejection → Rework Flow (Full Cycle) \u2550\u2550")
# ═══════════════════════════════════════════════════════════════════

REWORK_DIR = tempfile.mkdtemp(prefix="tf_rework_test_")
REWORK_JOB = "REWORK-TEST"

wo_rework = WorkOrder(
    work_order_id="WO-REWORK-001",
    job_code=REWORK_JOB,
    items=[
        WorkOrderItem(item_id="RW-1", ship_mark="RW1", component_type="column",
                      description="Rework Column", machine="WELDING", status=STATUS_FABRICATED),
    ],
)
save_work_order(REWORK_DIR, wo_rework)

# Step 1: fabricated → qc_pending
r = transition_item_status(REWORK_DIR, REWORK_JOB, "RW-1", STATUS_QC_PENDING, "inspector1")
test("Step 1: fabricated → qc_pending", r.get("ok"))

# Step 2: qc_pending → qc_rejected
r = transition_item_status(REWORK_DIR, REWORK_JOB, "RW-1", STATUS_QC_REJECTED, "inspector1",
                           notes="Weld defect")
test("Step 2: qc_pending → qc_rejected", r.get("ok"))

# Step 3: qc_rejected → in_progress (rework)
r = transition_item_status(REWORK_DIR, REWORK_JOB, "RW-1", STATUS_IN_PROGRESS, "welder1",
                           notes="Rework started")
test("Step 3: qc_rejected → in_progress (rework)", r.get("ok"))

# Step 4: in_progress → fabricated (re-done)
r = transition_item_status(REWORK_DIR, REWORK_JOB, "RW-1", STATUS_FABRICATED, "welder1")
test("Step 4: in_progress → fabricated", r.get("ok"))

# Step 5: fabricated → qc_pending (re-inspect)
r = transition_item_status(REWORK_DIR, REWORK_JOB, "RW-1", STATUS_QC_PENDING, "inspector1")
test("Step 5: fabricated → qc_pending (re-inspect)", r.get("ok"))

# Step 6: qc_pending → qc_approved (passes this time)
r = transition_item_status(REWORK_DIR, REWORK_JOB, "RW-1", STATUS_QC_APPROVED, "inspector1",
                           notes="Rework acceptable")
test("Step 6: qc_pending → qc_approved", r.get("ok"))

# Final check
wo_final = load_work_order(REWORK_DIR, REWORK_JOB, "WO-REWORK-001")
rw_item = wo_final.items[0]
test("Final status is qc_approved", rw_item.status == STATUS_QC_APPROVED)
test("Can now go to ready_to_ship", rw_item.can_transition_to(STATUS_READY_TO_SHIP))


# ═══════════════════════════════════════════════════════════════════
print("\n\u2550\u2550 TEST 19: Needs Attention Flags \u2550\u2550")
# ═══════════════════════════════════════════════════════════════════

item_rejected = WorkOrderItem(
    item_id="ATT-1", ship_mark="A1", component_type="test",
    description="Test", machine="Z1", status=STATUS_QC_REJECTED,
)
test("QC rejected item needs attention", item_rejected.needs_attention)

item_ok = WorkOrderItem(
    item_id="ATT-2", ship_mark="A2", component_type="test",
    description="Test", machine="Z1", status=STATUS_QC_APPROVED,
)
test("QC approved item does NOT need attention", not item_ok.needs_attention)

item_pending = WorkOrderItem(
    item_id="ATT-3", ship_mark="A3", component_type="test",
    description="Test", machine="Z1", status=STATUS_QC_PENDING,
)
test("QC pending item is NOT done", not item_pending.is_done)
test("QC pending item is NOT active (not in fabrication)", not item_pending.is_active)


# ═══════════════════════════════════════════════════════════════════
# CLEANUP
# ═══════════════════════════════════════════════════════════════════
tfh.QC_DIR = ORIG_QC_DIR  # Restore

try:
    shutil.rmtree(TEST_QC_DIR, ignore_errors=True)
    shutil.rmtree(WO_TEST_DIR, ignore_errors=True)
    shutil.rmtree(TRACE_DIR, ignore_errors=True)
    shutil.rmtree(REWORK_DIR, ignore_errors=True)
except:
    pass


# ═══════════════════════════════════════════════════════════════════
print(f"\n{'='*60}")
print(f"Phase 3 QC Module Tests: {passed} passed, {failed} failed out of {passed+failed}")
if failed == 0:
    print("\u2705 ALL PHASE 3 TESTS PASSED")
else:
    print(f"\u274c {failed} TESTS FAILED")
print(f"{'='*60}")

sys.exit(0 if failed == 0 else 1)
