#!/usr/bin/env python3
"""
TitanForge Phase 2 — Work Order System Tests
Tests the full 12-step lifecycle, assignment, queue helpers,
status transitions, and RBAC integration.
"""

import sys, os, json, tempfile, shutil, datetime
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


# Create a temp directory for test data
TEST_DIR = tempfile.mkdtemp(prefix="tf_wo_test_")


# ─────────────────────────────────────────────────────────────────────────────
print("\n══ TEST 1: Status Constants & Flow ══")
# ─────────────────────────────────────────────────────────────────────────────
from shop_drawings.work_orders import (
    STATUS_QUEUED, STATUS_APPROVED, STATUS_STICKERS_PRINTED, STATUS_STAGED,
    STATUS_IN_PROGRESS, STATUS_FABRICATED, STATUS_QC_PENDING, STATUS_QC_APPROVED,
    STATUS_QC_REJECTED, STATUS_READY_TO_SHIP, STATUS_SHIPPED, STATUS_DELIVERED,
    STATUS_INSTALLED, STATUS_ON_HOLD,
    STATUS_FLOW, STATUS_LABELS, STATUS_COLORS, VALID_STATUSES,
    MACHINE_TYPES,
    WorkOrder, WorkOrderItem,
    save_work_order, load_work_order, find_work_order_by_item,
    assign_item, reassign_item, reprioritize_item, stage_item,
    transition_item_status,
    qr_scan_start, qr_scan_finish,
    get_operator_queue, get_machine_queue, get_shop_floor_summary,
)

test("14 valid statuses defined", len(VALID_STATUSES) == 14)
test("All statuses have labels", all(s in STATUS_LABELS for s in VALID_STATUSES))
test("All statuses have colors", all(s in STATUS_COLORS for s in VALID_STATUSES))
test("All statuses have flow entries", all(s in STATUS_FLOW for s in VALID_STATUSES))
test("Installed is terminal (no transitions)", STATUS_FLOW[STATUS_INSTALLED] == [])
test("On Hold can go to queued/approved/in_progress",
     set(STATUS_FLOW[STATUS_ON_HOLD]) == {STATUS_QUEUED, STATUS_APPROVED, STATUS_IN_PROGRESS})
test("QC Rejected goes back to in_progress", STATUS_FLOW[STATUS_QC_REJECTED] == [STATUS_IN_PROGRESS])
test("9 machine types defined", len(MACHINE_TYPES) >= 9)
test("WELDING is a welder machine", MACHINE_TYPES["WELDING"]["operator_type"] == "welder")
test("Z1 is roll forming", MACHINE_TYPES["Z1"]["operator_type"] == "roll_forming_operator")


# ─────────────────────────────────────────────────────────────────────────────
print("\n══ TEST 2: WorkOrderItem — New Fields ══")
# ─────────────────────────────────────────────────────────────────────────────

item = WorkOrderItem(
    item_id="TEST-C1", ship_mark="C1", component_type="column",
    description="Test Column", machine="WELDING", status=STATUS_QUEUED,
)
test("Item has assigned_to field", hasattr(item, 'assigned_to') and item.assigned_to == "")
test("Item has assigned_by field", hasattr(item, 'assigned_by'))
test("Item has priority field (default 50)", item.priority == 50)
test("Item has staged_by field", hasattr(item, 'staged_by'))
test("Item has qc_inspector field", hasattr(item, 'qc_inspector'))
test("Item has qc_result field", hasattr(item, 'qc_result'))
test("Item has load_id field", hasattr(item, 'load_id'))
test("Item has shipped_at field", hasattr(item, 'shipped_at'))

# Status helpers
test("can_transition_to works (queued → approved)", item.can_transition_to(STATUS_APPROVED))
test("can_transition_to rejects invalid (queued → fabricated)", not item.can_transition_to(STATUS_FABRICATED))
test("status_label returns human label", item.status_label == "Queued")
test("status_color returns color", item.status_color == "gray")
test("is_active is False for queued", not item.is_active)
test("is_done is False for queued", not item.is_done)
test("needs_attention is False for queued", not item.needs_attention)

# Serialization
d = item.to_dict()
test("to_dict has assigned_to", "assigned_to" in d)
test("to_dict has priority", "priority" in d)
test("to_dict has qc_inspector", "qc_inspector" in d)
item2 = WorkOrderItem.from_dict(d)
test("from_dict round-trips", item2.item_id == "TEST-C1" and item2.priority == 50)


# ─────────────────────────────────────────────────────────────────────────────
print("\n══ TEST 3: WorkOrder — New Properties ══")
# ─────────────────────────────────────────────────────────────────────────────

wo = WorkOrder(
    work_order_id="WO-TEST-001", job_code="TEST-001", revision="A",
    created_at=datetime.datetime.now().isoformat(), created_by="test",
)
wo.items = [
    WorkOrderItem(item_id="T-C1", ship_mark="C1", component_type="column",
                  machine="WELDING", status=STATUS_IN_PROGRESS),
    WorkOrderItem(item_id="T-C2", ship_mark="C2", component_type="column",
                  machine="WELDING", status=STATUS_FABRICATED),
    WorkOrderItem(item_id="T-P1", ship_mark="P1", component_type="purlin",
                  machine="Z1", status=STATUS_QC_APPROVED),
    WorkOrderItem(item_id="T-P2", ship_mark="P2", component_type="purlin",
                  machine="Z1", status=STATUS_QUEUED),
]

test("total_items = 4", wo.total_items == 4)
test("completed_items = 2 (fabricated + qc_approved)", wo.completed_items == 2)
test("in_progress_items = 1", wo.in_progress_items == 1)
test("qc_pending_items = 0", wo.qc_pending_items == 0)

# Status breakdown
bd = wo.status_breakdown()
test("status_breakdown has in_progress", bd.get(STATUS_IN_PROGRESS) == 1)
test("status_breakdown has fabricated", bd.get(STATUS_FABRICATED) == 1)
test("status_breakdown has qc_approved", bd.get(STATUS_QC_APPROVED) == 1)

# Queue helpers
test("items_for_machine WELDING returns 2", len(wo.items_for_machine("WELDING")) == 2)
test("items_for_machine Z1 returns 2", len(wo.items_for_machine("Z1")) == 2)
test("unassigned_items returns 0 (none in assignable status + no assigned_to)",
     len(wo.unassigned_items()) == 0)

# items_needing_qc
wo.items[1].status = STATUS_QC_PENDING  # Change fabricated → qc_pending for test
test("items_needing_qc returns 1", len(wo.items_needing_qc()) == 1)
wo.items[1].status = STATUS_FABRICATED  # Reset

# recompute_status
wo.recompute_status()
test("recompute_status with mixed items → in_progress", wo.status == STATUS_IN_PROGRESS)


# ─────────────────────────────────────────────────────────────────────────────
print("\n══ TEST 4: Full Lifecycle — Item Assignment ══")
# ─────────────────────────────────────────────────────────────────────────────

# Create a work order for testing
test_wo = WorkOrder(
    work_order_id="WO-LIFE-001", job_code="LIFE-001", revision="A",
    created_at=datetime.datetime.now().isoformat(), created_by="test",
    status=STATUS_APPROVED,
)
test_wo.items = [
    WorkOrderItem(item_id="LIFE-C1", ship_mark="C1", component_type="column",
                  machine="WELDING", status=STATUS_STICKERS_PRINTED),
    WorkOrderItem(item_id="LIFE-P1", ship_mark="P1", component_type="purlin",
                  machine="Z1", status=STATUS_STICKERS_PRINTED),
]
save_work_order(TEST_DIR, test_wo)

# Assign items
result = assign_item(TEST_DIR, "LIFE-001", "LIFE-C1", "mike", "foreman_bob", 10)
test("assign_item succeeds", result["ok"])
test("assign_item sets assigned_to", result["item"]["assigned_to"] == "mike")
test("assign_item sets priority", result["item"]["priority"] == 10)
test("assign_item sets assigned_by", result["item"]["assigned_by"] == "foreman_bob")

# Reassign
result = reassign_item(TEST_DIR, "LIFE-001", "LIFE-C1", "dave", "foreman_bob")
test("reassign_item succeeds", result["ok"])
test("reassign shows old operator", result["old_operator"] == "mike")
test("reassign sets new operator", result["item"]["assigned_to"] == "dave")

# Reprioritize
result = reprioritize_item(TEST_DIR, "LIFE-001", "LIFE-C1", 1, "foreman_bob")
test("reprioritize succeeds", result["ok"])
test("reprioritize sets priority to 1", result["item"]["priority"] == 1)

# Priority bounds
result = reprioritize_item(TEST_DIR, "LIFE-001", "LIFE-C1", 150, "foreman_bob")
test("reprioritize clamps to 99", result["item"]["priority"] == 99)


# ─────────────────────────────────────────────────────────────────────────────
print("\n══ TEST 5: Full Lifecycle — Stage → Start → Finish ══")
# ─────────────────────────────────────────────────────────────────────────────

# Stage the purlin
result = stage_item(TEST_DIR, "LIFE-001", "LIFE-P1", "laborer_juan")
test("stage_item succeeds", result["ok"])
test("stage_item sets status to staged", result["item"]["status"] == STATUS_STAGED)
test("stage_item sets staged_by", result["item"]["staged_by"] == "laborer_juan")

# Can't stage twice
result = stage_item(TEST_DIR, "LIFE-001", "LIFE-P1", "laborer_juan")
test("stage_item rejects double staging", not result["ok"])

# QR scan start
result = qr_scan_start(TEST_DIR, "LIFE-001", "LIFE-P1", "operator_dave")
test("scan_start succeeds on staged item", result["ok"])
test("scan_start sets in_progress", result["item"]["status"] == STATUS_IN_PROGRESS)
test("scan_start sets started_by", result["item"]["started_by"] == "operator_dave")

# Can't start twice
result = qr_scan_start(TEST_DIR, "LIFE-001", "LIFE-P1", "operator_dave")
test("scan_start rejects double start", not result["ok"])

# QR scan finish → now goes to FABRICATED (not COMPLETE)
result = qr_scan_finish(TEST_DIR, "LIFE-001", "LIFE-P1", "operator_dave")
test("scan_finish succeeds", result["ok"])
test("scan_finish sets FABRICATED (not complete)", result["item"]["status"] == STATUS_FABRICATED)
test("scan_finish calculates duration", result["duration_minutes"] >= 0)


# ─────────────────────────────────────────────────────────────────────────────
print("\n══ TEST 6: Status Transitions (QC → Ship → Deliver → Install) ══")
# ─────────────────────────────────────────────────────────────────────────────

# Fabricated → QC Pending
result = transition_item_status(TEST_DIR, "LIFE-001", "LIFE-P1",
                                 STATUS_QC_PENDING, "qc_inspector_bob")
test("fabricated → qc_pending succeeds", result["ok"])
test("transition returns old_status", result["old_status"] == STATUS_FABRICATED)

# QC Pending → QC Approved
result = transition_item_status(TEST_DIR, "LIFE-001", "LIFE-P1",
                                 STATUS_QC_APPROVED, "qc_inspector_bob",
                                 notes="Passed visual + dimensional")
test("qc_pending → qc_approved succeeds", result["ok"])
test("QC sets inspector", result["item"]["qc_inspector"] == "qc_inspector_bob")
test("QC sets result to approved", result["item"]["qc_result"] == "approved")
test("QC stores notes", "Passed" in result["item"]["qc_notes"])

# QC Approved → Ready to Ship
result = transition_item_status(TEST_DIR, "LIFE-001", "LIFE-P1",
                                 STATUS_READY_TO_SHIP, "shipping_coord")
test("qc_approved → ready_to_ship succeeds", result["ok"])

# Ready to Ship → Shipped
result = transition_item_status(TEST_DIR, "LIFE-001", "LIFE-P1",
                                 STATUS_SHIPPED, "shipping_coord")
test("ready_to_ship → shipped succeeds", result["ok"])
test("shipped_at is set", result["item"]["shipped_at"] != "")

# Shipped → Delivered
result = transition_item_status(TEST_DIR, "LIFE-001", "LIFE-P1",
                                 STATUS_DELIVERED, "field_crew")
test("shipped → delivered succeeds", result["ok"])
test("delivered_at is set", result["item"]["delivered_at"] != "")

# Delivered → Installed
result = transition_item_status(TEST_DIR, "LIFE-001", "LIFE-P1",
                                 STATUS_INSTALLED, "field_crew")
test("delivered → installed succeeds", result["ok"])
test("installed_at is set", result["item"]["installed_at"] != "")

# Can't go past installed
result = transition_item_status(TEST_DIR, "LIFE-001", "LIFE-P1",
                                 STATUS_SHIPPED, "system")
test("installed → shipped rejected (terminal)", not result["ok"])


# ─────────────────────────────────────────────────────────────────────────────
print("\n══ TEST 7: QC Rejection Flow ══")
# ─────────────────────────────────────────────────────────────────────────────

# Set up a new item for rejection testing
test_wo2 = WorkOrder(
    work_order_id="WO-REJ-001", job_code="REJ-001", revision="A",
    created_at=datetime.datetime.now().isoformat(), created_by="test",
    status=STATUS_IN_PROGRESS,
)
test_wo2.items = [
    WorkOrderItem(item_id="REJ-C1", ship_mark="C1", component_type="column",
                  machine="WELDING", status=STATUS_FABRICATED),
]
save_work_order(TEST_DIR, test_wo2)

# Fabricated → QC Pending
transition_item_status(TEST_DIR, "REJ-001", "REJ-C1", STATUS_QC_PENDING, "inspector")

# QC Rejected
result = transition_item_status(TEST_DIR, "REJ-001", "REJ-C1",
                                 STATUS_QC_REJECTED, "inspector",
                                 notes="Weld porosity on flange")
test("qc_pending → qc_rejected succeeds", result["ok"])
test("QC rejection sets result", result["item"]["qc_result"] == "rejected")
test("QC rejection stores notes", "porosity" in result["item"]["qc_notes"])

# QC Rejected → In Progress (back to operator for rework)
result = transition_item_status(TEST_DIR, "REJ-001", "REJ-C1",
                                 STATUS_IN_PROGRESS, "operator_dave")
test("qc_rejected → in_progress succeeds (rework)", result["ok"])

# Re-assign after rejection — item is now in_progress after transition,
# so we test that it's back in a workable state
wo_rej, item_rej = find_work_order_by_item(TEST_DIR, "REJ-001", "REJ-C1")
test("after rework transition, item is in_progress", item_rej.status == STATUS_IN_PROGRESS)


# ─────────────────────────────────────────────────────────────────────────────
print("\n══ TEST 8: Invalid Transitions ══")
# ─────────────────────────────────────────────────────────────────────────────

test_wo3 = WorkOrder(
    work_order_id="WO-INV-001", job_code="INV-001", revision="A",
    created_at=datetime.datetime.now().isoformat(), created_by="test",
    status=STATUS_QUEUED,
)
test_wo3.items = [
    WorkOrderItem(item_id="INV-C1", ship_mark="C1", status=STATUS_QUEUED, machine="WELDING"),
]
save_work_order(TEST_DIR, test_wo3)

# Can't go from queued to fabricated
result = transition_item_status(TEST_DIR, "INV-001", "INV-C1",
                                 STATUS_FABRICATED, "system")
test("queued → fabricated rejected", not result["ok"])
test("error message mentions allowed transitions", "Allowed" in result.get("error", ""))

# Can't go from queued to shipped
result = transition_item_status(TEST_DIR, "INV-001", "INV-C1",
                                 STATUS_SHIPPED, "system")
test("queued → shipped rejected", not result["ok"])


# ─────────────────────────────────────────────────────────────────────────────
print("\n══ TEST 9: Operator Queue Helpers ══")
# ─────────────────────────────────────────────────────────────────────────────

# Use isolated dir to avoid cross-contamination from other tests
QUEUE_DIR = tempfile.mkdtemp(prefix="tf_queue_test_")

test_wo4 = WorkOrder(
    work_order_id="WO-Q-001", job_code="Q-001", revision="A",
    created_at=datetime.datetime.now().isoformat(), created_by="test",
    status=STATUS_IN_PROGRESS,
)
test_wo4.items = [
    WorkOrderItem(item_id="Q-C1", ship_mark="C1", machine="WELDING",
                  status=STATUS_IN_PROGRESS, assigned_to="dave", priority=1),
    WorkOrderItem(item_id="Q-C2", ship_mark="C2", machine="WELDING",
                  status=STATUS_STAGED, assigned_to="dave", priority=50),
    WorkOrderItem(item_id="Q-P1", ship_mark="P1", machine="Z1",
                  status=STATUS_STAGED, assigned_to="mike", priority=10),
    WorkOrderItem(item_id="Q-P2", ship_mark="P2", machine="Z1",
                  status=STATUS_QUEUED, assigned_to="", priority=50),
]
save_work_order(QUEUE_DIR, test_wo4)

# Operator queue
dave_queue = get_operator_queue(QUEUE_DIR, "dave")
test("Dave has 2 items", len(dave_queue) == 2)
test("Dave's items sorted by priority (1 first)", dave_queue[0]["priority"] == 1)

mike_queue = get_operator_queue(QUEUE_DIR, "mike")
test("Mike has 1 item", len(mike_queue) == 1)

nobody_queue = get_operator_queue(QUEUE_DIR, "nobody")
test("Unknown user has 0 items", len(nobody_queue) == 0)

# Machine queue
welding_q = get_machine_queue(QUEUE_DIR, "WELDING")
test("WELDING machine has 2 items", len(welding_q) == 2)

z1_q = get_machine_queue(QUEUE_DIR, "Z1")
test("Z1 machine has 2 items", len(z1_q) == 2)

shutil.rmtree(QUEUE_DIR, ignore_errors=True)


# ─────────────────────────────────────────────────────────────────────────────
print("\n══ TEST 10: Shop Floor Summary ══")
# ─────────────────────────────────────────────────────────────────────────────

summary = get_shop_floor_summary(TEST_DIR)
test("Summary has machines dict", "machines" in summary)
test("Summary has status_counts", "status_counts" in summary)
test("Summary has needs_attention", "needs_attention" in summary)
test("Summary has total_items", summary["total_items"] > 0)
test("WELDING in machines", "WELDING" in summary["machines"])


# ─────────────────────────────────────────────────────────────────────────────
print("\n══ TEST 11: WO recompute_status — all items installed ══")
# ─────────────────────────────────────────────────────────────────────────────

all_done_wo = WorkOrder(work_order_id="WO-DONE", job_code="DONE", status=STATUS_IN_PROGRESS)
all_done_wo.items = [
    WorkOrderItem(item_id="D1", status=STATUS_INSTALLED),
    WorkOrderItem(item_id="D2", status=STATUS_INSTALLED),
]
all_done_wo.recompute_status()
test("All installed → WO status is installed", all_done_wo.status == STATUS_INSTALLED)

# All shipped
all_ship = WorkOrder(work_order_id="WO-SHIP", job_code="SHIP", status=STATUS_IN_PROGRESS)
all_ship.items = [
    WorkOrderItem(item_id="S1", status=STATUS_SHIPPED),
    WorkOrderItem(item_id="S2", status=STATUS_DELIVERED),
]
all_ship.recompute_status()
test("All shipped/delivered → WO status is shipped", all_ship.status == STATUS_SHIPPED)

# Mixed → in_progress
mixed = WorkOrder(work_order_id="WO-MIX", job_code="MIX", status=STATUS_QUEUED)
mixed.items = [
    WorkOrderItem(item_id="M1", status=STATUS_IN_PROGRESS),
    WorkOrderItem(item_id="M2", status=STATUS_QC_APPROVED),
]
mixed.recompute_status()
test("Mixed with in_progress → WO is in_progress", mixed.status == STATUS_IN_PROGRESS)


# ─────────────────────────────────────────────────────────────────────────────
print("\n══ TEST 12: RBAC Integration — Handler Permissions ══")
# ─────────────────────────────────────────────────────────────────────────────
from auth.roles import P
from auth.permissions import merge_permissions

# God Mode can do everything
god = merge_permissions(["god_mode"])
test("God Mode can assign_operators", god.can("assign_operators"))
test("God Mode can reprioritize_queue", god.can("reprioritize_queue"))
test("God Mode can scan_start_finish", god.can("scan_start_finish"))
test("God Mode can view_work_orders", god.can("view_work_orders"))
test("God Mode can edit_work_orders", god.can("edit_work_orders"))

# Foreman can assign and reprioritize
foreman = merge_permissions(["shop_foreman"])
test("Foreman can assign_operators", foreman.can("assign_operators"))
test("Foreman can reprioritize_queue", foreman.can("reprioritize_queue"))
test("Foreman can scan_start_finish", foreman.can("scan_start_finish"))
test("Foreman can create_work_orders", foreman.can("create_work_orders"))
test("Foreman can edit_work_orders", foreman.can("edit_work_orders"))

# Operator can scan but NOT assign
operator = merge_permissions(["roll_forming_operator"])
test("Operator can scan_start_finish", operator.can("scan_start_finish"))
test("Operator can view_own_work_items", operator.can("view_own_work_items"))
test("Operator canNOT assign_operators", not operator.can("assign_operators"))
test("Operator canNOT reprioritize_queue", not operator.can("reprioritize_queue"))
test("Operator canNOT create_work_orders", not operator.can("create_work_orders"))

# Welder can scan but NOT assign
welder = merge_permissions(["welder"])
test("Welder can scan_start_finish", welder.can("scan_start_finish"))
test("Welder can view_own_work_items", welder.can("view_own_work_items"))
test("Welder canNOT assign_operators", not welder.can("assign_operators"))

# Laborer can scan (for staging)
laborer = merge_permissions(["laborer"])
test("Laborer can scan_start_finish", laborer.can("scan_start_finish"))
test("Laborer canNOT view_work_orders", not laborer.can("view_work_orders"))
test("Laborer canNOT assign_operators", not laborer.can("assign_operators"))

# QC Inspector can view but not assign
qc = merge_permissions(["qc_inspector"])
test("QC can perform_inspections", qc.can("perform_inspections"))
test("QC can sign_off_qc", qc.can("sign_off_qc"))
test("QC canNOT assign_operators", not qc.can("assign_operators"))

# Customer cannot access any shop floor
customer = merge_permissions(["customer"])
test("Customer canNOT view_work_orders", not customer.can("view_work_orders"))
test("Customer canNOT scan_start_finish", not customer.can("scan_start_finish"))


# ─────────────────────────────────────────────────────────────────────────────
print("\n══ TEST 13: Backward Compatibility ══")
# ─────────────────────────────────────────────────────────────────────────────

# Old-format work order (6-status) should load fine
old_wo_data = {
    "work_order_id": "WO-OLD-001",
    "job_code": "OLD-001",
    "revision": "A",
    "created_at": "2024-01-01T00:00:00",
    "created_by": "old_system",
    "status": "complete",
    "items": [
        {
            "item_id": "OLD-C1",
            "ship_mark": "C1",
            "component_type": "column",
            "status": "complete",  # Old status
            "machine": "WELDING",
            "started_by": "user1",
            "finished_by": "user1",
            "duration_minutes": 45.0,
        }
    ]
}
old_wo = WorkOrder.from_dict(old_wo_data)
test("Old WO loads without error", old_wo.work_order_id == "WO-OLD-001")
test("Old item loads with 'complete' status", old_wo.items[0].status == "complete")
test("Old item has new fields (assigned_to defaults)", old_wo.items[0].assigned_to == "")
test("Old item has new fields (qc_inspector defaults)", old_wo.items[0].qc_inspector == "")
test("to_dict includes new fields", "assigned_to" in old_wo.to_dict()["items"][0])
test("summary still works with old data", old_wo.summary()["total_items"] == 1)


# ─────────────────────────────────────────────────────────────────────────────
# Cleanup
# ─────────────────────────────────────────────────────────────────────────────
shutil.rmtree(TEST_DIR, ignore_errors=True)

# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{'═'*60}")
print(f"Phase 2 Work Order Tests: {passed} passed, {failed} failed out of {passed + failed}")
print(f"{'═'*60}")

if failed > 0:
    print("\n⚠️  Some tests failed! Review above.")
    sys.exit(1)
else:
    print("\n✅ All Phase 2 tests passed!")
    sys.exit(0)
