#!/usr/bin/env python3
"""
TitanForge Phase 4 — Shipping & Load Building Tests
Tests load data model, storage, CRUD, status transitions with WO integration,
BOL generation, shippable items, handler permissions, route table, and templates.
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
print("\n══ TEST 1: Load Status Constants ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.shipping import (
    LOAD_STATUS_BUILDING, LOAD_STATUS_READY, LOAD_STATUS_IN_TRANSIT,
    LOAD_STATUS_DELIVERED, LOAD_STATUS_COMPLETE,
    LOAD_STATUSES, LOAD_STATUS_LABELS, LOAD_STATUS_COLORS, LOAD_FLOW,
)

test("5 load statuses defined", len(LOAD_STATUSES) == 5)
test("building status", LOAD_STATUS_BUILDING == "building")
test("ready status", LOAD_STATUS_READY == "ready")
test("in_transit status", LOAD_STATUS_IN_TRANSIT == "in_transit")
test("delivered status", LOAD_STATUS_DELIVERED == "delivered")
test("complete status", LOAD_STATUS_COMPLETE == "complete")

test("All statuses have labels", all(s in LOAD_STATUS_LABELS for s in LOAD_STATUSES))
test("All statuses have colors", all(s in LOAD_STATUS_COLORS for s in LOAD_STATUSES))
test("All statuses in LOAD_FLOW", all(s in LOAD_FLOW for s in LOAD_STATUSES))

# Verify flow constraints
test("building → ready only", LOAD_FLOW[LOAD_STATUS_BUILDING] == [LOAD_STATUS_READY])
test("ready → in_transit only", LOAD_FLOW[LOAD_STATUS_READY] == [LOAD_STATUS_IN_TRANSIT])
test("in_transit → delivered only", LOAD_FLOW[LOAD_STATUS_IN_TRANSIT] == [LOAD_STATUS_DELIVERED])
test("delivered → complete only", LOAD_FLOW[LOAD_STATUS_DELIVERED] == [LOAD_STATUS_COMPLETE])
test("complete is terminal", LOAD_FLOW[LOAD_STATUS_COMPLETE] == [])


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 2: LoadItem Data Model ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.shipping import LoadItem

li = LoadItem(
    job_code="JOB-100", wo_id="WO-001", item_id="ITM-A1",
    ship_mark="C1", description="Column C1", quantity=2,
    weight_lbs=1500.0, length_ft=24.5, bundle_tag="B-01"
)
test("LoadItem job_code", li.job_code == "JOB-100")
test("LoadItem item_id", li.item_id == "ITM-A1")
test("LoadItem weight", li.weight_lbs == 1500.0)
test("LoadItem length", li.length_ft == 24.5)
test("LoadItem bundle_tag", li.bundle_tag == "B-01")

# to_dict / from_dict round-trip
d = li.to_dict()
test("to_dict has all keys", all(k in d for k in ["job_code", "wo_id", "item_id", "ship_mark", "description", "quantity", "weight_lbs", "length_ft", "bundle_tag"]))
li2 = LoadItem.from_dict(d)
test("from_dict round-trip job_code", li2.job_code == "JOB-100")
test("from_dict round-trip weight", li2.weight_lbs == 1500.0)
test("from_dict round-trip bundle_tag", li2.bundle_tag == "B-01")


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 3: ShippingLoad Data Model ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.shipping import ShippingLoad

sl = ShippingLoad(
    load_id="LOAD-20260414-001", load_number=1, status=LOAD_STATUS_BUILDING,
    job_code="JOB-100", destination="123 Job Site Rd",
    carrier="Acme Trucking", trailer_type="flatbed",
    items=[li],
    created_at=datetime.datetime.now().isoformat(),
    created_by="shipping_coord",
)

test("ShippingLoad load_id", sl.load_id == "LOAD-20260414-001")
test("ShippingLoad status", sl.status == LOAD_STATUS_BUILDING)
test("ShippingLoad carrier", sl.carrier == "Acme Trucking")
test("total_items = 1", sl.total_items == 1)
test("total_weight = 1500", sl.total_weight == 1500.0)
test("total_pieces = 2", sl.total_pieces == 2)
test("status_label = Building", sl.status_label == "Building")
test("status_color = amber", sl.status_color == "amber")
test("job_codes includes JOB-100", "JOB-100" in sl.job_codes)

# can_transition_to
test("building can → ready", sl.can_transition_to(LOAD_STATUS_READY))
test("building cannot → in_transit", not sl.can_transition_to(LOAD_STATUS_IN_TRANSIT))
test("building cannot → delivered", not sl.can_transition_to(LOAD_STATUS_DELIVERED))

# to_dict / from_dict round-trip
d = sl.to_dict()
test("to_dict has items list", isinstance(d["items"], list) and len(d["items"]) == 1)
test("to_dict item has item_id", d["items"][0]["item_id"] == "ITM-A1")
sl2 = ShippingLoad.from_dict(d)
test("from_dict round-trip load_id", sl2.load_id == "LOAD-20260414-001")
test("from_dict round-trip items", len(sl2.items) == 1)
test("from_dict item is LoadItem", isinstance(sl2.items[0], LoadItem))
test("from_dict item_id", sl2.items[0].item_id == "ITM-A1")

# summary()
s = sl.summary()
test("summary has load_id", s["load_id"] == sl.load_id)
test("summary has total_weight", s["total_weight"] == 1500.0)
test("summary has status_label", s["status_label"] == "Building")


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 4: Load Storage (save / load / list) ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.shipping import save_load, load_shipping_load, list_loads, next_load_number

TEST_DIR = tempfile.mkdtemp(prefix="tf_ship_test_")

# Save
save_load(TEST_DIR, sl)
test("Load file created", os.path.isfile(os.path.join(TEST_DIR, "data", "shipping", f"{sl.load_id}.json")))

# Reload
reloaded = load_shipping_load(TEST_DIR, sl.load_id)
test("Reloaded load not None", reloaded is not None)
test("Reloaded load_id matches", reloaded.load_id == sl.load_id)
test("Reloaded items count", len(reloaded.items) == 1)
test("Reloaded total_weight", reloaded.total_weight == 1500.0)

# Load not found
missing = load_shipping_load(TEST_DIR, "NONEXISTENT")
test("Missing load returns None", missing is None)

# List
all_loads = list_loads(TEST_DIR)
test("list_loads returns 1 load", len(all_loads) == 1)

# Save a second load
sl2 = ShippingLoad(
    load_id="LOAD-20260414-002", load_number=2, status=LOAD_STATUS_READY,
    job_code="JOB-200", destination="456 Site Ave",
    created_at=datetime.datetime.now().isoformat(),
)
save_load(TEST_DIR, sl2)
all_loads = list_loads(TEST_DIR)
test("list_loads returns 2 loads", len(all_loads) == 2)

# Filter by status
building_loads = list_loads(TEST_DIR, status=LOAD_STATUS_BUILDING)
test("Filter by building: 1 load", len(building_loads) == 1)
ready_loads = list_loads(TEST_DIR, status=LOAD_STATUS_READY)
test("Filter by ready: 1 load", len(ready_loads) == 1)

# Filter by job_code
job100_loads = list_loads(TEST_DIR, job_code="JOB-100")
test("Filter by JOB-100: 1 load", len(job100_loads) == 1)

# next_load_number
nln = next_load_number(TEST_DIR)
test("next_load_number is 3", nln == 3)

shutil.rmtree(TEST_DIR)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 5: create_load() ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.shipping import create_load

TEST_DIR = tempfile.mkdtemp(prefix="tf_ship_test_")

load = create_load(
    TEST_DIR, "JOB-300", created_by="coord1",
    destination="789 Field Dr", carrier="Self",
    notes="Priority shipment", special_instructions="Crane needed at site"
)
test("create_load returns ShippingLoad", isinstance(load, ShippingLoad))
test("load_id starts with LOAD-", load.load_id.startswith("LOAD-"))
test("load_number is 1", load.load_number == 1)
test("status is building", load.status == LOAD_STATUS_BUILDING)
test("job_code is JOB-300", load.job_code == "JOB-300")
test("destination set", load.destination == "789 Field Dr")
test("carrier set", load.carrier == "Self")
test("notes set", load.notes == "Priority shipment")
test("special_instructions set", load.special_instructions == "Crane needed at site")
test("created_by set", load.created_by == "coord1")
test("created_at set", load.created_at != "")
test("items empty", len(load.items) == 0)

# Persisted
reloaded = load_shipping_load(TEST_DIR, load.load_id)
test("create_load persists to disk", reloaded is not None)
test("Persisted load_id matches", reloaded.load_id == load.load_id)

# Sequential numbering
load2 = create_load(TEST_DIR, "JOB-400", created_by="coord1")
test("Second load number is 2", load2.load_number == 2)

shutil.rmtree(TEST_DIR)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 6: add_items_to_load() with WO Integration ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.shipping import add_items_to_load
from shop_drawings.work_orders import (
    WorkOrder, WorkOrderItem, save_work_order, load_work_order,
    STATUS_QC_APPROVED, STATUS_READY_TO_SHIP, STATUS_IN_PROGRESS,
    transition_item_status,
)

TEST_DIR = tempfile.mkdtemp(prefix="tf_ship_test_")
WO_DIR = os.path.join(TEST_DIR, "data", "shop_drawings")

# Create a project with a WO and QC-approved items
job = "PROJ-SHIP-01"
wo = WorkOrder(
    work_order_id="WO-SHIP-001",
    job_code=job,
    items=[
        WorkOrderItem(item_id="ITM-S1", ship_mark="C1", description="Column 1",
                      quantity=1, status=STATUS_QC_APPROVED),
        WorkOrderItem(item_id="ITM-S2", ship_mark="C2", description="Column 2",
                      quantity=1, status=STATUS_QC_APPROVED),
        WorkOrderItem(item_id="ITM-S3", ship_mark="R1", description="Rafter 1",
                      quantity=1, status=STATUS_IN_PROGRESS),  # Not eligible
    ]
)
os.makedirs(os.path.join(WO_DIR, job, "work_orders"), exist_ok=True)
save_work_order(WO_DIR, wo)

# Create a load
load = create_load(TEST_DIR, job, created_by="coord1")

# Add eligible items
result = add_items_to_load(
    TEST_DIR, WO_DIR, load.load_id,
    [
        {"job_code": job, "item_id": "ITM-S1", "weight_lbs": 800, "length_ft": 20},
        {"job_code": job, "item_id": "ITM-S2", "weight_lbs": 900, "length_ft": 22},
    ],
    added_by="coord1"
)
test("add_items ok", result["ok"])
test("added 2 items", result["added"] == 2)
test("no errors", len(result.get("errors", [])) == 0)

# Verify load now has items
reloaded = load_shipping_load(TEST_DIR, load.load_id)
test("Load has 2 items", len(reloaded.items) == 2)
test("First item is ITM-S1", reloaded.items[0].item_id == "ITM-S1")
test("First item weight", reloaded.items[0].weight_lbs == 800)

# Verify WO items transitioned to ready_to_ship
wo_reloaded = load_work_order(WO_DIR, job, "WO-SHIP-001")
item_s1 = [i for i in wo_reloaded.items if i.item_id == "ITM-S1"][0]
item_s2 = [i for i in wo_reloaded.items if i.item_id == "ITM-S2"][0]
test("ITM-S1 → ready_to_ship", item_s1.status == STATUS_READY_TO_SHIP)
test("ITM-S2 → ready_to_ship", item_s2.status == STATUS_READY_TO_SHIP)

# Verify load_id set on WO items
test("ITM-S1 load_id set", item_s1.load_id == load.load_id)
test("ITM-S2 load_id set", item_s2.load_id == load.load_id)

# Try adding ineligible item (in_progress)
result2 = add_items_to_load(
    TEST_DIR, WO_DIR, load.load_id,
    [{"job_code": job, "item_id": "ITM-S3"}],
    added_by="coord1"
)
test("Ineligible item errors", len(result2.get("errors", [])) > 0)
test("Still added 0", result2.get("added", 0) == 0)

# Try adding duplicate
result3 = add_items_to_load(
    TEST_DIR, WO_DIR, load.load_id,
    [{"job_code": job, "item_id": "ITM-S1"}],
    added_by="coord1"
)
test("Duplicate item errors", len(result3.get("errors", [])) > 0)

# Add to non-existent load
result4 = add_items_to_load(
    TEST_DIR, WO_DIR, "FAKE-LOAD",
    [{"job_code": job, "item_id": "ITM-S1"}],
    added_by="coord1"
)
test("Non-existent load fails", not result4["ok"])


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 7: remove_item_from_load() ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.shipping import remove_item_from_load

result = remove_item_from_load(TEST_DIR, WO_DIR, load.load_id, "ITM-S1", "coord1")
test("remove ok", result["ok"])

reloaded = load_shipping_load(TEST_DIR, load.load_id)
test("Load has 1 item after remove", len(reloaded.items) == 1)
test("Remaining item is ITM-S2", reloaded.items[0].item_id == "ITM-S2")

# Verify load_id cleared on WO item
wo_reloaded = load_work_order(WO_DIR, job, "WO-SHIP-001")
item_s1 = [i for i in wo_reloaded.items if i.item_id == "ITM-S1"][0]
test("ITM-S1 load_id cleared", item_s1.load_id == "")

# Remove non-existent item
result2 = remove_item_from_load(TEST_DIR, WO_DIR, load.load_id, "FAKE-ITEM", "coord1")
test("Remove non-existent fails", not result2["ok"])

# Remove from non-existent load
result3 = remove_item_from_load(TEST_DIR, WO_DIR, "FAKE-LOAD", "ITM-S2", "coord1")
test("Remove from non-existent load fails", not result3["ok"])


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 8: Load Status Transitions with WO Auto-Transition ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.shipping import transition_load_status
from shop_drawings.work_orders import STATUS_SHIPPED, STATUS_DELIVERED, STATUS_INSTALLED

# Re-add item for transition tests
add_items_to_load(
    TEST_DIR, WO_DIR, load.load_id,
    [{"job_code": job, "item_id": "ITM-S1", "weight_lbs": 800}],
    added_by="coord1"
)

# building → ready
result = transition_load_status(TEST_DIR, WO_DIR, load.load_id, LOAD_STATUS_READY, "coord1")
test("building → ready ok", result["ok"])
test("old_status = building", result["old_status"] == LOAD_STATUS_BUILDING)
test("new_status = ready", result["new_status"] == LOAD_STATUS_READY)

# Cannot skip to delivered
result_skip = transition_load_status(TEST_DIR, WO_DIR, load.load_id, LOAD_STATUS_DELIVERED, "coord1")
test("Cannot skip ready → delivered", not result_skip["ok"])

# ready → in_transit (ships the load)
result = transition_load_status(TEST_DIR, WO_DIR, load.load_id, LOAD_STATUS_IN_TRANSIT, "coord1")
test("ready → in_transit ok", result["ok"])
test("item_transitions present", len(result.get("item_transitions", [])) > 0)

# Verify load timestamps
rl = load_shipping_load(TEST_DIR, load.load_id)
test("shipped_at set", rl.shipped_at != "")
test("shipped_by set", rl.shipped_by == "coord1")

# Verify WO items transitioned to shipped
wo_r = load_work_order(WO_DIR, job, "WO-SHIP-001")
s1 = [i for i in wo_r.items if i.item_id == "ITM-S1"][0]
s2 = [i for i in wo_r.items if i.item_id == "ITM-S2"][0]
test("ITM-S1 → shipped", s1.status == STATUS_SHIPPED)
test("ITM-S2 → shipped", s2.status == STATUS_SHIPPED)

# in_transit → delivered
result = transition_load_status(
    TEST_DIR, WO_DIR, load.load_id, LOAD_STATUS_DELIVERED, "field_crew",
    notes="All items accounted for"
)
test("in_transit → delivered ok", result["ok"])
rl = load_shipping_load(TEST_DIR, load.load_id)
test("delivered_at set", rl.delivered_at != "")
test("delivered_by set", rl.delivered_by == "field_crew")
test("delivery_notes set", rl.delivery_notes == "All items accounted for")

wo_r = load_work_order(WO_DIR, job, "WO-SHIP-001")
s1 = [i for i in wo_r.items if i.item_id == "ITM-S1"][0]
test("ITM-S1 → delivered", s1.status == STATUS_DELIVERED)

# delivered → complete
result = transition_load_status(TEST_DIR, WO_DIR, load.load_id, LOAD_STATUS_COMPLETE, "pm_user")
test("delivered → complete ok", result["ok"])

rl = load_shipping_load(TEST_DIR, load.load_id)
test("completed_at set", rl.completed_at != "")
test("status = complete", rl.status == LOAD_STATUS_COMPLETE)

wo_r = load_work_order(WO_DIR, job, "WO-SHIP-001")
s1 = [i for i in wo_r.items if i.item_id == "ITM-S1"][0]
test("ITM-S1 → installed", s1.status == STATUS_INSTALLED)

# complete is terminal
result = transition_load_status(TEST_DIR, WO_DIR, load.load_id, LOAD_STATUS_BUILDING, "coord1")
test("complete is terminal (cannot go back)", not result["ok"])


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 9: Empty Load Validation ══")
# ═══════════════════════════════════════════════════════════════════

empty_load = create_load(TEST_DIR, "JOB-EMPTY", created_by="coord1")
result = transition_load_status(TEST_DIR, WO_DIR, empty_load.load_id, LOAD_STATUS_READY, "coord1")
test("Cannot mark empty load as ready", not result["ok"])
test("Error mentions empty", "empty" in result.get("error", "").lower())

# Cannot add items to non-building load
ready_load = create_load(TEST_DIR, "JOB-READY", created_by="coord1")
# Manually set to ready (with an item so the check passes)
ready_load.status = LOAD_STATUS_READY
ready_load.items = [LoadItem(item_id="FAKE", job_code="JOB-READY")]
save_load(TEST_DIR, ready_load)
result = add_items_to_load(
    TEST_DIR, WO_DIR, ready_load.load_id,
    [{"job_code": "JOB-READY", "item_id": "NEW-ITEM"}],
    added_by="coord1"
)
test("Cannot add items to non-building load", not result["ok"])

# Cannot remove from non-building load
result = remove_item_from_load(TEST_DIR, WO_DIR, ready_load.load_id, "FAKE", "coord1")
test("Cannot remove items from non-building load", not result["ok"])

shutil.rmtree(TEST_DIR)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 10: BOL Generation ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.shipping import generate_bol

TEST_DIR = tempfile.mkdtemp(prefix="tf_ship_test_")

load = create_load(TEST_DIR, "JOB-BOL", created_by="coord1")
# Add a dummy item directly so BOL can generate
load.items = [LoadItem(item_id="BOL-ITEM-1", job_code="JOB-BOL", description="Test item")]
save_load(TEST_DIR, load)

result = generate_bol(TEST_DIR, load.load_id, "office_admin")
test("generate_bol ok", result["ok"])
test("bol_number starts with BOL-", result["bol_number"].startswith("BOL-"))
test("bol_number in result", "bol_number" in result)

# Verify persisted
rl = load_shipping_load(TEST_DIR, load.load_id)
test("bol_generated = True", rl.bol_generated is True)
test("bol_generated_at set", rl.bol_generated_at != "")
test("bol_generated_by set", rl.bol_generated_by == "office_admin")
test("bol_number persisted", rl.bol_number == result["bol_number"])

# BOL on empty load fails
empty_load = create_load(TEST_DIR, "JOB-EMPTY", created_by="coord1")
result2 = generate_bol(TEST_DIR, empty_load.load_id, "admin")
test("BOL on empty building load fails", not result2["ok"])

# BOL on non-existent load
result3 = generate_bol(TEST_DIR, "FAKE-LOAD", "admin")
test("BOL on non-existent load fails", not result3["ok"])

shutil.rmtree(TEST_DIR)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 11: get_shippable_items() ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.shipping import get_shippable_items

TEST_DIR = tempfile.mkdtemp(prefix="tf_ship_test_")
WO_DIR = os.path.join(TEST_DIR, "data", "shop_drawings")

# Create WO with mixed statuses
job = "PROJ-SHIP-02"
wo = WorkOrder(
    work_order_id="WO-SHIP-002",
    job_code=job,
    items=[
        WorkOrderItem(item_id="A1", ship_mark="A1", status=STATUS_QC_APPROVED, description="Approved item"),
        WorkOrderItem(item_id="A2", ship_mark="A2", status=STATUS_READY_TO_SHIP, description="Ready item"),
        WorkOrderItem(item_id="A3", ship_mark="A3", status=STATUS_IN_PROGRESS, description="In progress"),
        WorkOrderItem(item_id="A4", ship_mark="A4", status=STATUS_QC_APPROVED, description="Another approved", load_id="SOME-LOAD"),  # Already on a load
    ]
)
os.makedirs(os.path.join(WO_DIR, job, "work_orders"), exist_ok=True)
save_work_order(WO_DIR, wo)

items = get_shippable_items(WO_DIR)
test("Shippable items found", len(items) > 0)

item_ids = [i["item_id"] for i in items]
test("A1 is shippable (qc_approved, no load)", "A1" in item_ids)
test("A2 is shippable (ready_to_ship, no load)", "A2" in item_ids)
test("A3 NOT shippable (in_progress)", "A3" not in item_ids)
test("A4 NOT shippable (already on a load)", "A4" not in item_ids)

# Filter by job_code
items_filtered = get_shippable_items(WO_DIR, job_code=job)
test("Filtered by job returns results", len(items_filtered) == 2)

items_no_match = get_shippable_items(WO_DIR, job_code="NONEXISTENT")
test("Nonexistent job returns empty", len(items_no_match) == 0)

# Item fields
sample = [i for i in items if i["item_id"] == "A1"][0]
test("Shippable item has job_code", sample["job_code"] == job)
test("Shippable item has wo_id", sample["wo_id"] == "WO-SHIP-002")
test("Shippable item has ship_mark", sample["ship_mark"] == "A1")
test("Shippable item has description", sample["description"] == "Approved item")
test("Shippable item has status", sample["status"] == STATUS_QC_APPROVED)

shutil.rmtree(TEST_DIR)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 12: get_shipping_summary() ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.shipping import get_shipping_summary

TEST_DIR = tempfile.mkdtemp(prefix="tf_ship_test_")

# Create loads in various statuses
loads_data = [
    ("JOB-A", LOAD_STATUS_BUILDING, []),
    ("JOB-A", LOAD_STATUS_READY, []),
    ("JOB-B", LOAD_STATUS_IN_TRANSIT, [LoadItem(weight_lbs=1000, quantity=3)]),
    ("JOB-B", LOAD_STATUS_DELIVERED, [LoadItem(weight_lbs=2000, quantity=5)]),
    ("JOB-C", LOAD_STATUS_COMPLETE, [LoadItem(weight_lbs=1500, quantity=4)]),
]
for i, (jc, st, items) in enumerate(loads_data):
    sl = ShippingLoad(
        load_id=f"LOAD-SUM-{i:03d}", load_number=i+1, status=st,
        job_code=jc, items=items,
        created_at=datetime.datetime.now().isoformat(),
    )
    save_load(TEST_DIR, sl)

summary = get_shipping_summary(TEST_DIR)
test("total_loads = 5", summary["total_loads"] == 5)
test("building = 1", summary["building"] == 1)
test("ready = 1", summary["ready"] == 1)
test("in_transit = 1", summary["in_transit"] == 1)
test("delivered = 1", summary["delivered"] == 1)
test("complete = 1", summary["complete"] == 1)
test("total_items_shipped = 3 (transit + delivered + complete items)",
     summary["total_items_shipped"] == 3)
test("total_weight_shipped = 4500",
     summary["total_weight_shipped"] == 4500.0)
test("recent_loads capped at 20", len(summary["recent_loads"]) <= 20)
test("recent_loads has entries", len(summary["recent_loads"]) == 5)

# Empty directory
EMPTY_DIR = tempfile.mkdtemp(prefix="tf_ship_empty_")
empty_summary = get_shipping_summary(EMPTY_DIR)
test("Empty summary has 0 total", empty_summary["total_loads"] == 0)
shutil.rmtree(EMPTY_DIR)

shutil.rmtree(TEST_DIR)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 13: Full End-to-End Shipping Lifecycle ══")
# ═══════════════════════════════════════════════════════════════════

TEST_DIR = tempfile.mkdtemp(prefix="tf_ship_e2e_")
WO_DIR = os.path.join(TEST_DIR, "data", "shop_drawings")

# Step 1: Set up project with QC-approved items
job = "E2E-JOB"
wo = WorkOrder(
    work_order_id="WO-E2E-001",
    job_code=job,
    items=[
        WorkOrderItem(item_id="E2E-1", ship_mark="C1", description="Col 1",
                      quantity=1, status=STATUS_QC_APPROVED),
        WorkOrderItem(item_id="E2E-2", ship_mark="C2", description="Col 2",
                      quantity=1, status=STATUS_QC_APPROVED),
        WorkOrderItem(item_id="E2E-3", ship_mark="R1", description="Raft 1",
                      quantity=1, status=STATUS_QC_APPROVED),
    ]
)
os.makedirs(os.path.join(WO_DIR, job, "work_orders"), exist_ok=True)
save_work_order(WO_DIR, wo)

# Step 2: Create load
load = create_load(TEST_DIR, job, created_by="ship_coord",
                   destination="100 Job Site Blvd", carrier="Titan Transport",
                   special_instructions="Crane on site")
test("E2E: Load created", load.load_id != "")

# Step 3: Add items
result = add_items_to_load(TEST_DIR, WO_DIR, load.load_id,
    [{"job_code": job, "item_id": "E2E-1", "weight_lbs": 500, "length_ft": 18},
     {"job_code": job, "item_id": "E2E-2", "weight_lbs": 600, "length_ft": 20}],
    added_by="ship_coord")
test("E2E: Items added", result["added"] == 2)

# Step 4: Generate BOL
bol = generate_bol(TEST_DIR, load.load_id, "office")
test("E2E: BOL generated", bol["ok"])

# Step 5: Mark ready
result = transition_load_status(TEST_DIR, WO_DIR, load.load_id, LOAD_STATUS_READY, "ship_coord")
test("E2E: Marked ready", result["ok"])

# Step 6: Ship
result = transition_load_status(TEST_DIR, WO_DIR, load.load_id, LOAD_STATUS_IN_TRANSIT, "ship_coord")
test("E2E: Shipped", result["ok"])

# Verify all items shipped
wo_check = load_work_order(WO_DIR, job, "WO-E2E-001")
shipped_items = [i for i in wo_check.items if i.status == STATUS_SHIPPED]
test("E2E: 2 items shipped", len(shipped_items) == 2)
# E2E-3 should still be qc_approved (not on load)
e2e3 = [i for i in wo_check.items if i.item_id == "E2E-3"][0]
test("E2E: E2E-3 still qc_approved", e2e3.status == STATUS_QC_APPROVED)

# Step 7: Deliver
result = transition_load_status(TEST_DIR, WO_DIR, load.load_id, LOAD_STATUS_DELIVERED,
                                "field_lead", notes="Received in good condition")
test("E2E: Delivered", result["ok"])

# Step 8: Complete (install confirmation)
result = transition_load_status(TEST_DIR, WO_DIR, load.load_id, LOAD_STATUS_COMPLETE, "pm")
test("E2E: Completed", result["ok"])

# Final verification
final_load = load_shipping_load(TEST_DIR, load.load_id)
test("E2E: Final status = complete", final_load.status == LOAD_STATUS_COMPLETE)
test("E2E: BOL number persisted", final_load.bol_number.startswith("BOL-"))
test("E2E: shipped_at set", final_load.shipped_at != "")
test("E2E: delivered_at set", final_load.delivered_at != "")
test("E2E: completed_at set", final_load.completed_at != "")

wo_final = load_work_order(WO_DIR, job, "WO-E2E-001")
e1 = [i for i in wo_final.items if i.item_id == "E2E-1"][0]
e2 = [i for i in wo_final.items if i.item_id == "E2E-2"][0]
test("E2E: E2E-1 → installed", e1.status == STATUS_INSTALLED)
test("E2E: E2E-2 → installed", e2.status == STATUS_INSTALLED)
test("E2E: E2E-1 load_id set", e1.load_id == load.load_id)

shutil.rmtree(TEST_DIR)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 14: Shipping Handler Classes Exist ══")
# ═══════════════════════════════════════════════════════════════════
import tf_handlers as tfh

handler_classes = [
    "ShippingDashboardPageHandler",
    "LoadBuilderPageHandler",
    "ShippingListAPIHandler",
    "ShippingLoadDetailHandler",
    "ShippingCreateLoadHandler",
    "ShippingAddItemsHandler",
    "ShippingRemoveItemHandler",
    "ShippingTransitionHandler",
    "ShippingUpdateLoadHandler",
    "ShippingBOLHandler",
    "ShippableItemsHandler",
    "ShippingSummaryHandler",
    "ShippingConfigHandler",
]

for cls_name in handler_classes:
    test(f"{cls_name} exists", hasattr(tfh, cls_name))
    cls = getattr(tfh, cls_name, None)
    if cls:
        test(f"{cls_name} has required_permission", hasattr(cls, "required_permission"))


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 15: RBAC Permission Mapping for Shipping ══")
# ═══════════════════════════════════════════════════════════════════
from auth.roles import ROLES, P

# Check shipping_coordinator role
ship_role = ROLES.get("shipping_coordinator")
test("shipping_coordinator role exists", ship_role is not None)

if ship_role:
    perms = ship_role.permissions
    test("shipping_coordinator has build_loads", P.BUILD_LOADS in perms)
    test("shipping_coordinator has generate_bol", P.GENERATE_BOL in perms)
    test("shipping_coordinator has mark_shipped", P.MARK_SHIPPED in perms)
    test("shipping_coordinator has view_shipping", P.VIEW_SHIPPING in perms)

# Handler → permission mapping
permission_map = {
    "ShippingDashboardPageHandler": "view_shipping",
    "LoadBuilderPageHandler": "build_loads",
    "ShippingListAPIHandler": "view_shipping",
    "ShippingLoadDetailHandler": "view_shipping",
    "ShippingCreateLoadHandler": "build_loads",
    "ShippingAddItemsHandler": "build_loads",
    "ShippingRemoveItemHandler": "build_loads",
    "ShippingTransitionHandler": "mark_shipped",
    "ShippingUpdateLoadHandler": "build_loads",
    "ShippingBOLHandler": "generate_bol",
    "ShippableItemsHandler": "view_shipping",
    "ShippingSummaryHandler": "view_shipping",
    "ShippingConfigHandler": "view_shipping",
}

for handler_name, expected_perm in permission_map.items():
    cls = getattr(tfh, handler_name, None)
    if cls:
        actual = getattr(cls, "required_permission", None)
        test(f"{handler_name} → {expected_perm}", actual == expected_perm)

# Verify NO shipping handlers use old required_roles
for handler_name in handler_classes:
    cls = getattr(tfh, handler_name, None)
    if cls:
        test(f"{handler_name} has NO required_roles",
             not hasattr(cls, "required_roles") or getattr(cls, "required_roles", None) is None)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 16: Route Table (Shipping Routes) ══")
# ═══════════════════════════════════════════════════════════════════

routes = tfh.get_routes()
route_paths = [r[0] if isinstance(r, (list, tuple)) else r for r in routes]

shipping_routes = [
    r"/shipping",
    r"/shipping/load-builder",
    r"/api/shipping/loads",
    r"/api/shipping/load",
    r"/api/shipping/create",
    r"/api/shipping/add-items",
    r"/api/shipping/remove-item",
    r"/api/shipping/transition",
    r"/api/shipping/update",
    r"/api/shipping/bol",
    r"/api/shipping/shippable-items",
    r"/api/shipping/summary",
    r"/api/shipping/config",
]

for route in shipping_routes:
    test(f"Route {route} registered", route in route_paths)

test(f"13 shipping routes total", sum(1 for r in route_paths if "shipping" in r.lower()) >= 13)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 17: Template Files ══")
# ═══════════════════════════════════════════════════════════════════

# Shipping dashboard page
from templates.shipping_page import SHIPPING_PAGE_HTML
test("SHIPPING_PAGE_HTML is non-empty", len(SHIPPING_PAGE_HTML) > 500)
test("Shipping page has pipeline bar", "pipelineBar" in SHIPPING_PAGE_HTML)
test("Shipping page has metric cards", "metBuilding" in SHIPPING_PAGE_HTML)
test("Shipping page has loads table", "loadsBody" in SHIPPING_PAGE_HTML)
test("Shipping page has detail modal", "detailModal" in SHIPPING_PAGE_HTML)
test("Shipping page links to load builder", "/shipping/load-builder" in SHIPPING_PAGE_HTML)
test("Shipping page has auto-refresh", "setInterval" in SHIPPING_PAGE_HTML)
test("Shipping page fetches summary API", "/api/shipping/summary" in SHIPPING_PAGE_HTML)
test("Shipping page fetches loads API", "/api/shipping/loads" in SHIPPING_PAGE_HTML)

# Load builder page
from templates.load_builder_page import LOAD_BUILDER_PAGE_HTML
test("LOAD_BUILDER_PAGE_HTML is non-empty", len(LOAD_BUILDER_PAGE_HTML) > 500)
test("Load builder has two-panel layout", "builder-grid" in LOAD_BUILDER_PAGE_HTML)
test("Load builder has create load", "createLoad" in LOAD_BUILDER_PAGE_HTML or "create" in LOAD_BUILDER_PAGE_HTML.lower())
test("Load builder has add items", "add-items" in LOAD_BUILDER_PAGE_HTML or "addItem" in LOAD_BUILDER_PAGE_HTML)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 18: WorkOrderItem Shipping Fields ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.work_orders import WorkOrderItem as WOI, PHASE_SHIPPING

item = WOI()
test("WorkOrderItem has load_id field", hasattr(item, "load_id"))
test("WorkOrderItem has shipped_at field", hasattr(item, "shipped_at"))
test("WorkOrderItem has delivered_at field", hasattr(item, "delivered_at"))
test("WorkOrderItem has installed_at field", hasattr(item, "installed_at"))
test("load_id defaults to empty", item.load_id == "")

test("PHASE_SHIPPING includes ready_to_ship", STATUS_READY_TO_SHIP in PHASE_SHIPPING)
test("PHASE_SHIPPING includes shipped", STATUS_SHIPPED in PHASE_SHIPPING)
test("PHASE_SHIPPING includes delivered", STATUS_DELIVERED in PHASE_SHIPPING)
test("PHASE_SHIPPING includes installed", STATUS_INSTALLED in PHASE_SHIPPING)
test("PHASE_SHIPPING has 4 statuses", len(PHASE_SHIPPING) == 4)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 19: Status Flow — Shipping Chain ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.work_orders import STATUS_FLOW

test("qc_approved → ready_to_ship", STATUS_READY_TO_SHIP in STATUS_FLOW[STATUS_QC_APPROVED])
test("ready_to_ship → shipped", STATUS_SHIPPED in STATUS_FLOW[STATUS_READY_TO_SHIP])
test("shipped → delivered", STATUS_DELIVERED in STATUS_FLOW[STATUS_SHIPPED])
test("delivered → installed", STATUS_INSTALLED in STATUS_FLOW[STATUS_DELIVERED])
test("installed is terminal", STATUS_FLOW[STATUS_INSTALLED] == [])

# Cannot skip statuses
test("qc_approved cannot → shipped", STATUS_SHIPPED not in STATUS_FLOW[STATUS_QC_APPROVED])
test("ready_to_ship cannot → delivered", STATUS_DELIVERED not in STATUS_FLOW[STATUS_READY_TO_SHIP])


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 20: Multi-Project Load ══")
# ═══════════════════════════════════════════════════════════════════

TEST_DIR = tempfile.mkdtemp(prefix="tf_ship_multi_")
WO_DIR = os.path.join(TEST_DIR, "data", "shop_drawings")

# Create two projects
for job, wo_id, items in [
    ("MULTI-A", "WO-MA1", [
        WorkOrderItem(item_id="MA-1", ship_mark="A1", status=STATUS_QC_APPROVED),
    ]),
    ("MULTI-B", "WO-MB1", [
        WorkOrderItem(item_id="MB-1", ship_mark="B1", status=STATUS_QC_APPROVED),
    ]),
]:
    wo = WorkOrder(work_order_id=wo_id, job_code=job, items=items)
    os.makedirs(os.path.join(WO_DIR, job, "work_orders"), exist_ok=True)
    save_work_order(WO_DIR, wo)

# Create load for MULTI-A but add items from both
load = create_load(TEST_DIR, "MULTI-A", created_by="coord1")
result = add_items_to_load(TEST_DIR, WO_DIR, load.load_id,
    [{"job_code": "MULTI-A", "item_id": "MA-1"},
     {"job_code": "MULTI-B", "item_id": "MB-1"}],
    added_by="coord1")
test("Multi-project: added 2 items from 2 projects", result["added"] == 2)

rl = load_shipping_load(TEST_DIR, load.load_id)
test("Multi-project: job_codes has both", set(rl.job_codes) == {"MULTI-A", "MULTI-B"})
test("Multi-project: total_items = 2", rl.total_items == 2)

# Filter by job_code should match both via job_codes
loads_a = list_loads(TEST_DIR, job_code="MULTI-A")
loads_b = list_loads(TEST_DIR, job_code="MULTI-B")
test("Multi-project: load appears for MULTI-A", len(loads_a) == 1)
test("Multi-project: load appears for MULTI-B", len(loads_b) == 1)

shutil.rmtree(TEST_DIR)


# ═══════════════════════════════════════════════════════════════════
# FINAL REPORT
# ═══════════════════════════════════════════════════════════════════
total = passed + failed
print(f"\n{'='*60}")
print(f"Phase 4 (Shipping & Load Building): {passed}/{total} passed")
if failed:
    print(f"  ⚠️  {failed} FAILURES")
else:
    print(f"  🎉 ALL {total} TESTS PASSED")
print(f"{'='*60}")

sys.exit(0 if failed == 0 else 1)
