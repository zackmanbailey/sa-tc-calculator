#!/usr/bin/env python3
"""
TitanForge Phase 11 — Inventory Management Tests
=================================================
Comprehensive tests for the inventory management engine:
coil CRUD, receiving, consumption, adjustments, allocations,
mill certs, alerts, analytics, and handlers.
"""

import os, sys, json, shutil, tempfile, unittest, datetime

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shop_drawings.inventory import (
    COIL_STATUSES, COIL_STATUS_LABELS,
    TRANSACTION_TYPES, TRANSACTION_TYPE_LABELS,
    MATERIAL_GRADES, COIL_GAUGES, ALERT_LEVELS,
    InventoryTransaction, StockAlert, Allocation, ReceivingRecord,
    create_coil, get_coil, list_coils, update_coil, delete_coil,
    receive_stock, adjust_stock, consume_stock, list_transactions,
    allocate_stock, release_allocation, list_allocations, get_allocation,
    list_alerts, acknowledge_alert, generate_stock_alerts,
    list_receiving, add_mill_cert, list_mill_certs, delete_mill_cert,
    get_inventory_summary, get_coil_history, get_stock_valuation,
    _load_inventory_main, _save_inventory_main,
)


class TestBase(unittest.TestCase):
    """Base class with temp directory setup/teardown."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        # Create empty inventory.json
        inv_path = os.path.join(self.tmpdir, "inventory.json")
        with open(inv_path, "w") as f:
            json.dump({"coils": {}, "mill_certs": []}, f)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _create_test_coil(self, coil_id="COIL-001", name="10GA Galvalume 48in",
                          gauge="10GA", grade="Galvalume", supplier="Steel Co",
                          stock_lbs=5000, price_per_lb=0.45, **kwargs):
        return create_coil(
            self.tmpdir, coil_id=coil_id, name=name, gauge=gauge,
            grade=grade, supplier=supplier, stock_lbs=stock_lbs,
            price_per_lb=price_per_lb, weight_lbs=kwargs.get("weight_lbs", 8000),
            width_in=kwargs.get("width_in", 48),
            min_order_lbs=kwargs.get("min_order_lbs", 3000),
            lbs_per_lft=kwargs.get("lbs_per_lft", 4.2),
            created_by="test_user",
        )


# ═════════════════════════════════════════════════════════════════════════════
# TEST 1: Constants & Dataclass Basics
# ═════════════════════════════════════════════════════════════════════════════

class Test01_ConstantsAndDataclasses(TestBase):

    def test_01_coil_statuses(self):
        self.assertEqual(len(COIL_STATUSES), 5)
        for s in COIL_STATUSES:
            self.assertIn(s, COIL_STATUS_LABELS)

    def test_02_transaction_types(self):
        self.assertEqual(len(TRANSACTION_TYPES), 6)
        for t in TRANSACTION_TYPES:
            self.assertIn(t, TRANSACTION_TYPE_LABELS)

    def test_03_material_grades(self):
        self.assertIn("A36", MATERIAL_GRADES)
        self.assertIn("A572 Gr 50", MATERIAL_GRADES)
        self.assertIn("Galvalume", MATERIAL_GRADES)
        self.assertGreaterEqual(len(MATERIAL_GRADES), 10)

    def test_04_coil_gauges(self):
        self.assertIn("10GA", COIL_GAUGES)
        self.assertIn("26GA", COIL_GAUGES)
        self.assertGreaterEqual(len(COIL_GAUGES), 14)

    def test_05_inventory_transaction_auto_id(self):
        txn = InventoryTransaction(coil_id="COIL-1", quantity_lbs=1000)
        self.assertTrue(txn.transaction_id.startswith("TXN-"))
        self.assertNotEqual(txn.created_at, "")

    def test_06_inventory_transaction_to_dict(self):
        txn = InventoryTransaction(coil_id="COIL-1", transaction_type="receive",
                                   quantity_lbs=5000, balance_after=5000)
        d = txn.to_dict()
        self.assertEqual(d["coil_id"], "COIL-1")
        self.assertEqual(d["quantity_lbs"], 5000)
        self.assertEqual(d["type_label"], "Received")

    def test_07_inventory_transaction_from_dict(self):
        d = {"transaction_id": "TXN-TEST", "coil_id": "C1",
             "transaction_type": "allocate", "quantity_lbs": 2000}
        txn = InventoryTransaction.from_dict(d)
        self.assertEqual(txn.transaction_id, "TXN-TEST")
        self.assertEqual(txn.transaction_type, "allocate")

    def test_08_stock_alert_auto_id(self):
        alert = StockAlert(coil_id="C1", alert_type="low_stock")
        self.assertTrue(alert.alert_id.startswith("ALT-"))

    def test_09_allocation_remaining(self):
        alloc = Allocation(quantity_lbs=5000, consumed_lbs=2000)
        self.assertEqual(alloc.remaining_lbs, 3000)

    def test_10_allocation_remaining_zero(self):
        alloc = Allocation(quantity_lbs=5000, consumed_lbs=6000)
        self.assertEqual(alloc.remaining_lbs, 0)

    def test_11_receiving_record_auto_id(self):
        rec = ReceivingRecord(coil_id="C1", quantity_lbs=5000)
        self.assertTrue(rec.receiving_id.startswith("RCV-"))

    def test_12_alert_levels(self):
        self.assertEqual(len(ALERT_LEVELS), 3)
        self.assertIn("critical", ALERT_LEVELS)


# ═════════════════════════════════════════════════════════════════════════════
# TEST 2: Coil CRUD
# ═════════════════════════════════════════════════════════════════════════════

class Test02_CoilCRUD(TestBase):

    def test_01_create_coil(self):
        coil = self._create_test_coil()
        self.assertEqual(coil["name"], "10GA Galvalume 48in")
        self.assertEqual(coil["gauge"], "10GA")
        self.assertEqual(coil["stock_lbs"], 5000)
        self.assertEqual(coil["status"], "active")

    def test_02_create_duplicate_raises(self):
        self._create_test_coil()
        with self.assertRaises(ValueError):
            self._create_test_coil()

    def test_03_get_coil(self):
        self._create_test_coil()
        coil = get_coil(self.tmpdir, "COIL-001")
        self.assertIsNotNone(coil)
        self.assertEqual(coil["coil_id"], "COIL-001")
        self.assertEqual(coil["gauge"], "10GA")

    def test_04_get_coil_not_found(self):
        coil = get_coil(self.tmpdir, "NONEXISTENT")
        self.assertIsNone(coil)

    def test_05_list_coils_all(self):
        self._create_test_coil("COIL-001")
        self._create_test_coil("COIL-002", name="14GA A36", gauge="14GA", grade="A36")
        coils = list_coils(self.tmpdir)
        self.assertEqual(len(coils), 2)

    def test_06_list_coils_filter_gauge(self):
        self._create_test_coil("COIL-001", gauge="10GA")
        self._create_test_coil("COIL-002", gauge="14GA")
        coils = list_coils(self.tmpdir, gauge="10GA")
        self.assertEqual(len(coils), 1)
        self.assertEqual(coils[0]["gauge"], "10GA")

    def test_07_list_coils_filter_grade(self):
        self._create_test_coil("COIL-001", grade="Galvalume")
        self._create_test_coil("COIL-002", grade="A36")
        coils = list_coils(self.tmpdir, grade="A36")
        self.assertEqual(len(coils), 1)

    def test_08_list_coils_filter_status(self):
        self._create_test_coil("COIL-001", stock_lbs=5000, min_order_lbs=3000)  # active
        self._create_test_coil("COIL-002", stock_lbs=100, min_order_lbs=3000)   # low_stock
        coils = list_coils(self.tmpdir, status="low_stock")
        self.assertEqual(len(coils), 1)

    def test_09_list_coils_low_stock_only(self):
        self._create_test_coil("COIL-001", stock_lbs=5000, min_order_lbs=3000)
        self._create_test_coil("COIL-002", stock_lbs=100, min_order_lbs=3000)
        self._create_test_coil("COIL-003", stock_lbs=0, min_order_lbs=3000)
        coils = list_coils(self.tmpdir, low_stock_only=True)
        self.assertEqual(len(coils), 2)  # low_stock + depleted

    def test_10_update_coil(self):
        self._create_test_coil()
        coil = update_coil(self.tmpdir, "COIL-001", name="Updated Name",
                           supplier="New Supplier")
        self.assertEqual(coil["name"], "Updated Name")
        self.assertEqual(coil["supplier"], "New Supplier")

    def test_11_update_coil_not_found(self):
        with self.assertRaises(ValueError):
            update_coil(self.tmpdir, "NONEXISTENT", name="X")

    def test_12_delete_coil(self):
        self._create_test_coil()
        ok = delete_coil(self.tmpdir, "COIL-001")
        self.assertTrue(ok)
        self.assertIsNone(get_coil(self.tmpdir, "COIL-001"))

    def test_13_delete_coil_not_found(self):
        ok = delete_coil(self.tmpdir, "NONEXISTENT")
        self.assertFalse(ok)

    def test_14_create_coil_with_initial_stock_logs_transaction(self):
        self._create_test_coil(stock_lbs=5000)
        txns = list_transactions(self.tmpdir, coil_id="COIL-001")
        self.assertEqual(len(txns), 1)
        self.assertEqual(txns[0]["transaction_type"], "receive")
        self.assertEqual(txns[0]["quantity_lbs"], 5000)

    def test_15_create_coil_zero_stock_no_transaction(self):
        self._create_test_coil(stock_lbs=0)
        txns = list_transactions(self.tmpdir, coil_id="COIL-001")
        self.assertEqual(len(txns), 0)

    def test_16_coil_stock_lft_calculated(self):
        coil = self._create_test_coil(stock_lbs=4200, lbs_per_lft=4.2)
        self.assertAlmostEqual(coil["stock_lft"], 1000.0, places=0)


# ═════════════════════════════════════════════════════════════════════════════
# TEST 3: Coil Status Computation
# ═════════════════════════════════════════════════════════════════════════════

class Test03_CoilStatus(TestBase):

    def test_01_active_status(self):
        self._create_test_coil(stock_lbs=5000, min_order_lbs=3000)
        coil = get_coil(self.tmpdir, "COIL-001")
        self.assertEqual(coil["status"], "active")

    def test_02_low_stock_status(self):
        self._create_test_coil(stock_lbs=500, min_order_lbs=3000)
        coil = get_coil(self.tmpdir, "COIL-001")
        self.assertEqual(coil["status"], "low_stock")

    def test_03_depleted_status(self):
        self._create_test_coil(stock_lbs=0, min_order_lbs=3000)
        coil = get_coil(self.tmpdir, "COIL-001")
        self.assertEqual(coil["status"], "depleted")

    def test_04_quarantine_status_overrides(self):
        self._create_test_coil(stock_lbs=5000)
        update_coil(self.tmpdir, "COIL-001", status="quarantine")
        coil = get_coil(self.tmpdir, "COIL-001")
        self.assertEqual(coil["status"], "quarantine")

    def test_05_on_order_status_overrides(self):
        self._create_test_coil(stock_lbs=100, min_order_lbs=3000)
        update_coil(self.tmpdir, "COIL-001", status="on_order")
        coil = get_coil(self.tmpdir, "COIL-001")
        self.assertEqual(coil["status"], "on_order")


# ═════════════════════════════════════════════════════════════════════════════
# TEST 4: Receive Stock
# ═════════════════════════════════════════════════════════════════════════════

class Test04_ReceiveStock(TestBase):

    def test_01_receive_stock_basic(self):
        self._create_test_coil(stock_lbs=3000)
        result = receive_stock(self.tmpdir, "COIL-001", 2000,
                               po_number="PO-100", received_by="admin")
        self.assertEqual(result["old_stock"], 3000)
        self.assertEqual(result["new_stock"], 5000)

    def test_02_receive_updates_coil(self):
        self._create_test_coil(stock_lbs=3000, lbs_per_lft=4.2)
        receive_stock(self.tmpdir, "COIL-001", 2000)
        coil = get_coil(self.tmpdir, "COIL-001")
        self.assertEqual(coil["stock_lbs"], 5000)
        self.assertAlmostEqual(coil["stock_lft"], 1190.5, places=1)

    def test_03_receive_logs_transaction(self):
        self._create_test_coil(stock_lbs=3000)
        receive_stock(self.tmpdir, "COIL-001", 2000, po_number="PO-100")
        txns = list_transactions(self.tmpdir, coil_id="COIL-001",
                                 transaction_type="receive")
        # 1 from creation + 1 from receive
        self.assertEqual(len(txns), 2)

    def test_04_receive_creates_receiving_record(self):
        self._create_test_coil(stock_lbs=3000)
        receive_stock(self.tmpdir, "COIL-001", 2000,
                      po_number="PO-100", bol_number="BOL-50",
                      supplier="Steel Co", heat_number="HT-12345")
        records = list_receiving(self.tmpdir)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["po_number"], "PO-100")
        self.assertEqual(records[0]["heat_number"], "HT-12345")

    def test_05_receive_updates_heat_number(self):
        self._create_test_coil(stock_lbs=3000)
        receive_stock(self.tmpdir, "COIL-001", 2000, heat_number="HT-999")
        coil = get_coil(self.tmpdir, "COIL-001")
        self.assertEqual(coil["heat_num"], "HT-999")

    def test_06_receive_nonexistent_coil(self):
        with self.assertRaises(ValueError):
            receive_stock(self.tmpdir, "NONEXISTENT", 2000)

    def test_07_receive_zero_quantity(self):
        self._create_test_coil(stock_lbs=3000)
        with self.assertRaises(ValueError):
            receive_stock(self.tmpdir, "COIL-001", 0)

    def test_08_receive_negative_quantity(self):
        self._create_test_coil(stock_lbs=3000)
        with self.assertRaises(ValueError):
            receive_stock(self.tmpdir, "COIL-001", -500)

    def test_09_receive_appends_order_history(self):
        self._create_test_coil(stock_lbs=3000)
        receive_stock(self.tmpdir, "COIL-001", 2000, po_number="PO-200")
        coil = get_coil(self.tmpdir, "COIL-001")
        self.assertEqual(len(coil["orders"]), 1)
        self.assertEqual(coil["orders"][0]["po_number"], "PO-200")

    def test_10_receive_returns_receiving_id(self):
        self._create_test_coil(stock_lbs=3000)
        result = receive_stock(self.tmpdir, "COIL-001", 2000)
        self.assertTrue(result["receiving_id"].startswith("RCV-"))


# ═════════════════════════════════════════════════════════════════════════════
# TEST 5: Adjust Stock
# ═════════════════════════════════════════════════════════════════════════════

class Test05_AdjustStock(TestBase):

    def test_01_adjust_positive(self):
        self._create_test_coil(stock_lbs=3000)
        result = adjust_stock(self.tmpdir, "COIL-001", 500, reason="Found extra")
        self.assertEqual(result["new_stock"], 3500)

    def test_02_adjust_negative(self):
        self._create_test_coil(stock_lbs=3000)
        result = adjust_stock(self.tmpdir, "COIL-001", -500, reason="Scrap")
        self.assertEqual(result["new_stock"], 2500)

    def test_03_adjust_cant_go_below_zero(self):
        self._create_test_coil(stock_lbs=100)
        result = adjust_stock(self.tmpdir, "COIL-001", -500)
        self.assertEqual(result["new_stock"], 0)

    def test_04_adjust_logs_transaction(self):
        self._create_test_coil(stock_lbs=3000)
        adjust_stock(self.tmpdir, "COIL-001", -500)
        txns = list_transactions(self.tmpdir, transaction_type="adjust")
        self.assertEqual(len(txns), 1)
        self.assertEqual(txns[0]["quantity_lbs"], -500)

    def test_05_adjust_nonexistent_coil(self):
        with self.assertRaises(ValueError):
            adjust_stock(self.tmpdir, "NONEXISTENT", 500)

    def test_06_adjust_updates_stock_lft(self):
        self._create_test_coil(stock_lbs=4200, lbs_per_lft=4.2)
        adjust_stock(self.tmpdir, "COIL-001", -2100)
        coil = get_coil(self.tmpdir, "COIL-001")
        self.assertAlmostEqual(coil["stock_lft"], 500.0, places=0)


# ═════════════════════════════════════════════════════════════════════════════
# TEST 6: Consume Stock
# ═════════════════════════════════════════════════════════════════════════════

class Test06_ConsumeStock(TestBase):

    def test_01_consume_basic(self):
        self._create_test_coil(stock_lbs=5000)
        result = consume_stock(self.tmpdir, "COIL-001", 1500,
                               job_code="JOB-001", consumed_by="operator")
        self.assertEqual(result["old_stock"], 5000)
        self.assertEqual(result["new_stock"], 3500)

    def test_02_consume_logs_transaction(self):
        self._create_test_coil(stock_lbs=5000)
        consume_stock(self.tmpdir, "COIL-001", 1500, job_code="JOB-001")
        txns = list_transactions(self.tmpdir, transaction_type="consume")
        self.assertEqual(len(txns), 1)
        self.assertEqual(txns[0]["job_code"], "JOB-001")

    def test_03_consume_zero_raises(self):
        self._create_test_coil(stock_lbs=5000)
        with self.assertRaises(ValueError):
            consume_stock(self.tmpdir, "COIL-001", 0)

    def test_04_consume_more_than_stock_floors_zero(self):
        self._create_test_coil(stock_lbs=1000)
        result = consume_stock(self.tmpdir, "COIL-001", 5000)
        self.assertEqual(result["new_stock"], 0)

    def test_05_consume_nonexistent_coil(self):
        with self.assertRaises(ValueError):
            consume_stock(self.tmpdir, "NONEXISTENT", 500)


# ═════════════════════════════════════════════════════════════════════════════
# TEST 7: Transactions
# ═════════════════════════════════════════════════════════════════════════════

class Test07_Transactions(TestBase):

    def test_01_list_all_transactions(self):
        self._create_test_coil("C1", stock_lbs=5000)
        self._create_test_coil("C2", stock_lbs=3000)
        consume_stock(self.tmpdir, "C1", 1000)
        txns = list_transactions(self.tmpdir)
        self.assertGreaterEqual(len(txns), 3)  # 2 receive + 1 consume

    def test_02_filter_by_coil(self):
        self._create_test_coil("C1", stock_lbs=5000)
        self._create_test_coil("C2", stock_lbs=3000)
        txns = list_transactions(self.tmpdir, coil_id="C1")
        self.assertEqual(len(txns), 1)

    def test_03_filter_by_type(self):
        self._create_test_coil("C1", stock_lbs=5000)
        consume_stock(self.tmpdir, "C1", 1000)
        adjust_stock(self.tmpdir, "C1", -200)
        txns = list_transactions(self.tmpdir, transaction_type="consume")
        self.assertEqual(len(txns), 1)

    def test_04_sorted_newest_first(self):
        self._create_test_coil("C1", stock_lbs=5000)
        consume_stock(self.tmpdir, "C1", 100)
        consume_stock(self.tmpdir, "C1", 200)
        txns = list_transactions(self.tmpdir)
        self.assertTrue(txns[0]["created_at"] >= txns[-1]["created_at"])

    def test_05_filter_by_date_range(self):
        self._create_test_coil("C1", stock_lbs=5000)
        now = datetime.datetime.now().isoformat()
        txns = list_transactions(self.tmpdir, date_from=now[:10])
        self.assertGreater(len(txns), 0)


# ═════════════════════════════════════════════════════════════════════════════
# TEST 8: Allocations
# ═════════════════════════════════════════════════════════════════════════════

class Test08_Allocations(TestBase):

    def test_01_allocate_stock_basic(self):
        self._create_test_coil(stock_lbs=5000)
        alloc = allocate_stock(self.tmpdir, "COIL-001", "JOB-001", 2000,
                               allocated_by="admin")
        self.assertTrue(alloc.allocation_id.startswith("ALC-"))
        self.assertEqual(alloc.quantity_lbs, 2000)

    def test_02_allocate_updates_committed(self):
        self._create_test_coil(stock_lbs=5000)
        allocate_stock(self.tmpdir, "COIL-001", "JOB-001", 2000)
        coil = get_coil(self.tmpdir, "COIL-001")
        self.assertEqual(coil["committed_lbs"], 2000)

    def test_03_allocate_exceeds_available_raises(self):
        self._create_test_coil(stock_lbs=5000)
        allocate_stock(self.tmpdir, "COIL-001", "JOB-001", 4000)
        with self.assertRaises(ValueError):
            allocate_stock(self.tmpdir, "COIL-001", "JOB-002", 2000)

    def test_04_allocate_logs_transaction(self):
        self._create_test_coil(stock_lbs=5000)
        allocate_stock(self.tmpdir, "COIL-001", "JOB-001", 2000)
        txns = list_transactions(self.tmpdir, transaction_type="allocate")
        self.assertEqual(len(txns), 1)

    def test_05_list_allocations_all(self):
        self._create_test_coil(stock_lbs=10000)
        allocate_stock(self.tmpdir, "COIL-001", "JOB-001", 2000)
        allocate_stock(self.tmpdir, "COIL-001", "JOB-002", 3000)
        allocs = list_allocations(self.tmpdir)
        self.assertEqual(len(allocs), 2)

    def test_06_list_allocations_by_job(self):
        self._create_test_coil(stock_lbs=10000)
        allocate_stock(self.tmpdir, "COIL-001", "JOB-001", 2000)
        allocate_stock(self.tmpdir, "COIL-001", "JOB-002", 3000)
        allocs = list_allocations(self.tmpdir, job_code="JOB-001")
        self.assertEqual(len(allocs), 1)

    def test_07_release_allocation(self):
        self._create_test_coil(stock_lbs=5000)
        alloc = allocate_stock(self.tmpdir, "COIL-001", "JOB-001", 2000)
        result = release_allocation(self.tmpdir, alloc.allocation_id)
        self.assertEqual(result["released_lbs"], 2000)
        coil = get_coil(self.tmpdir, "COIL-001")
        self.assertEqual(coil["committed_lbs"], 0)

    def test_08_release_logs_return_transaction(self):
        self._create_test_coil(stock_lbs=5000)
        alloc = allocate_stock(self.tmpdir, "COIL-001", "JOB-001", 2000)
        release_allocation(self.tmpdir, alloc.allocation_id)
        txns = list_transactions(self.tmpdir, transaction_type="return")
        self.assertEqual(len(txns), 1)

    def test_09_release_nonexistent_raises(self):
        with self.assertRaises(ValueError):
            release_allocation(self.tmpdir, "NONEXISTENT")

    def test_10_release_already_released_raises(self):
        self._create_test_coil(stock_lbs=5000)
        alloc = allocate_stock(self.tmpdir, "COIL-001", "JOB-001", 2000)
        release_allocation(self.tmpdir, alloc.allocation_id)
        with self.assertRaises(ValueError):
            release_allocation(self.tmpdir, alloc.allocation_id)

    def test_11_get_allocation(self):
        self._create_test_coil(stock_lbs=5000)
        alloc = allocate_stock(self.tmpdir, "COIL-001", "JOB-001", 2000)
        found = get_allocation(self.tmpdir, alloc.allocation_id)
        self.assertIsNotNone(found)
        self.assertEqual(found["job_code"], "JOB-001")

    def test_12_get_allocation_not_found(self):
        found = get_allocation(self.tmpdir, "NONEXISTENT")
        self.assertIsNone(found)

    def test_13_allocate_zero_raises(self):
        self._create_test_coil(stock_lbs=5000)
        with self.assertRaises(ValueError):
            allocate_stock(self.tmpdir, "COIL-001", "JOB-001", 0)

    def test_14_multiple_allocations_same_job(self):
        self._create_test_coil(stock_lbs=10000)
        allocate_stock(self.tmpdir, "COIL-001", "JOB-001", 2000)
        allocate_stock(self.tmpdir, "COIL-001", "JOB-001", 1000)
        allocs = list_allocations(self.tmpdir, job_code="JOB-001")
        self.assertEqual(len(allocs), 2)
        coil = get_coil(self.tmpdir, "COIL-001")
        self.assertEqual(coil["committed_lbs"], 3000)


# ═════════════════════════════════════════════════════════════════════════════
# TEST 9: Alerts
# ═════════════════════════════════════════════════════════════════════════════

class Test09_Alerts(TestBase):

    def test_01_low_stock_generates_alert(self):
        self._create_test_coil(stock_lbs=5000, min_order_lbs=3000)
        consume_stock(self.tmpdir, "COIL-001", 4000)  # stock -> 1000 < 3000
        alerts = list_alerts(self.tmpdir, acknowledged=False)
        self.assertGreater(len(alerts), 0)
        self.assertEqual(alerts[0]["alert_type"], "low_stock")

    def test_02_depleted_generates_critical_alert(self):
        self._create_test_coil(stock_lbs=1000, min_order_lbs=3000)
        consume_stock(self.tmpdir, "COIL-001", 1000)  # stock -> 0
        alerts = list_alerts(self.tmpdir, alert_level="critical")
        self.assertGreater(len(alerts), 0)
        self.assertEqual(alerts[0]["alert_type"], "depleted")

    def test_03_receive_clears_alert(self):
        self._create_test_coil(stock_lbs=500, min_order_lbs=3000)
        # Should have alert from creation
        alerts_before = list_alerts(self.tmpdir, acknowledged=False)
        # Receive enough to be above min
        receive_stock(self.tmpdir, "COIL-001", 5000)
        alerts_after = list_alerts(self.tmpdir, acknowledged=False,
                                   coil_id="COIL-001")
        self.assertEqual(len(alerts_after), 0)

    def test_04_acknowledge_alert(self):
        self._create_test_coil(stock_lbs=500, min_order_lbs=3000)
        alerts = list_alerts(self.tmpdir, acknowledged=False)
        self.assertGreater(len(alerts), 0)
        acknowledge_alert(self.tmpdir, alerts[0]["alert_id"], "admin")
        acked = list_alerts(self.tmpdir, acknowledged=True)
        self.assertGreater(len(acked), 0)

    def test_05_acknowledge_nonexistent_raises(self):
        with self.assertRaises(ValueError):
            acknowledge_alert(self.tmpdir, "NONEXISTENT")

    def test_06_generate_alerts_scan(self):
        self._create_test_coil("C1", stock_lbs=100, min_order_lbs=3000)
        self._create_test_coil("C2", stock_lbs=5000, min_order_lbs=3000)
        result = generate_stock_alerts(self.tmpdir)
        self.assertIn("C1", result)

    def test_07_filter_alerts_by_level(self):
        self._create_test_coil(stock_lbs=0, min_order_lbs=3000)
        critical = list_alerts(self.tmpdir, alert_level="critical")
        warning = list_alerts(self.tmpdir, alert_level="warning")
        self.assertGreater(len(critical), 0)
        self.assertEqual(len(warning), 0)

    def test_08_filter_alerts_by_coil(self):
        self._create_test_coil("C1", stock_lbs=100, min_order_lbs=3000)
        self._create_test_coil("C2", stock_lbs=100, min_order_lbs=3000)
        alerts = list_alerts(self.tmpdir, coil_id="C1")
        for a in alerts:
            self.assertEqual(a["coil_id"], "C1")


# ═════════════════════════════════════════════════════════════════════════════
# TEST 10: Receiving Records
# ═════════════════════════════════════════════════════════════════════════════

class Test10_Receiving(TestBase):

    def test_01_list_receiving_all(self):
        self._create_test_coil(stock_lbs=3000)
        receive_stock(self.tmpdir, "COIL-001", 2000, po_number="PO-1")
        receive_stock(self.tmpdir, "COIL-001", 1000, po_number="PO-2")
        records = list_receiving(self.tmpdir)
        self.assertEqual(len(records), 2)

    def test_02_list_receiving_by_coil(self):
        self._create_test_coil("C1", stock_lbs=3000)
        self._create_test_coil("C2", stock_lbs=3000)
        receive_stock(self.tmpdir, "C1", 2000)
        receive_stock(self.tmpdir, "C2", 1000)
        records = list_receiving(self.tmpdir, coil_id="C1")
        self.assertEqual(len(records), 1)

    def test_03_receiving_record_fields(self):
        self._create_test_coil(stock_lbs=3000)
        receive_stock(self.tmpdir, "COIL-001", 2000,
                      po_number="PO-100", bol_number="BOL-50",
                      supplier="Steel Inc", heat_number="HT-999",
                      condition_notes="Good condition")
        records = list_receiving(self.tmpdir)
        r = records[0]
        self.assertEqual(r["po_number"], "PO-100")
        self.assertEqual(r["bol_number"], "BOL-50")
        self.assertEqual(r["heat_number"], "HT-999")
        self.assertEqual(r["condition_notes"], "Good condition")

    def test_04_receiving_sorted_newest_first(self):
        self._create_test_coil(stock_lbs=3000)
        receive_stock(self.tmpdir, "COIL-001", 1000, po_number="PO-1")
        receive_stock(self.tmpdir, "COIL-001", 2000, po_number="PO-2")
        records = list_receiving(self.tmpdir)
        self.assertTrue(records[0]["received_at"] >= records[1]["received_at"])


# ═════════════════════════════════════════════════════════════════════════════
# TEST 11: Mill Certificates
# ═════════════════════════════════════════════════════════════════════════════

class Test11_MillCerts(TestBase):

    def test_01_add_mill_cert(self):
        self._create_test_coil()
        cert = add_mill_cert(self.tmpdir, "COIL-001",
                             heat_number="HT-123", mill_name="US Steel",
                             material_spec="A572 Gr 50")
        self.assertTrue(cert["cert_id"].startswith("CERT-"))
        self.assertEqual(cert["heat_num"], "HT-123")

    def test_02_add_cert_updates_coil_heat(self):
        self._create_test_coil()
        add_mill_cert(self.tmpdir, "COIL-001", heat_number="HT-456")
        coil = get_coil(self.tmpdir, "COIL-001")
        self.assertEqual(coil["heat_num"], "HT-456")

    def test_03_list_mill_certs_all(self):
        self._create_test_coil("C1")
        self._create_test_coil("C2")
        add_mill_cert(self.tmpdir, "C1", "HT-1")
        add_mill_cert(self.tmpdir, "C2", "HT-2")
        certs = list_mill_certs(self.tmpdir)
        self.assertEqual(len(certs), 2)

    def test_04_list_mill_certs_by_coil(self):
        self._create_test_coil("C1")
        self._create_test_coil("C2")
        add_mill_cert(self.tmpdir, "C1", "HT-1")
        add_mill_cert(self.tmpdir, "C2", "HT-2")
        certs = list_mill_certs(self.tmpdir, coil_id="C1")
        self.assertEqual(len(certs), 1)
        self.assertEqual(certs[0]["heat_num"], "HT-1")

    def test_05_delete_mill_cert(self):
        self._create_test_coil()
        cert = add_mill_cert(self.tmpdir, "COIL-001", "HT-1")
        ok = delete_mill_cert(self.tmpdir, cert["cert_id"])
        self.assertTrue(ok)
        certs = list_mill_certs(self.tmpdir, coil_id="COIL-001")
        self.assertEqual(len(certs), 0)

    def test_06_delete_cert_not_found(self):
        ok = delete_mill_cert(self.tmpdir, "NONEXISTENT")
        self.assertFalse(ok)

    def test_07_add_cert_nonexistent_coil_raises(self):
        with self.assertRaises(ValueError):
            add_mill_cert(self.tmpdir, "NONEXISTENT", "HT-1")

    def test_08_delete_coil_removes_certs(self):
        self._create_test_coil()
        add_mill_cert(self.tmpdir, "COIL-001", "HT-1")
        add_mill_cert(self.tmpdir, "COIL-001", "HT-2")
        delete_coil(self.tmpdir, "COIL-001")
        certs = list_mill_certs(self.tmpdir, coil_id="COIL-001")
        self.assertEqual(len(certs), 0)


# ═════════════════════════════════════════════════════════════════════════════
# TEST 12: Inventory Summary Analytics
# ═════════════════════════════════════════════════════════════════════════════

class Test12_InventorySummary(TestBase):

    def test_01_empty_summary(self):
        summary = get_inventory_summary(self.tmpdir)
        self.assertEqual(summary["total_coils"], 0)
        self.assertEqual(summary["total_stock_lbs"], 0)
        self.assertEqual(summary["total_value"], 0)

    def test_02_summary_with_coils(self):
        self._create_test_coil("C1", stock_lbs=5000, price_per_lb=0.50,
                               gauge="10GA", grade="Galvalume")
        self._create_test_coil("C2", stock_lbs=3000, price_per_lb=0.40,
                               gauge="14GA", grade="A36")
        summary = get_inventory_summary(self.tmpdir)
        self.assertEqual(summary["total_coils"], 2)
        self.assertEqual(summary["total_stock_lbs"], 8000)
        self.assertEqual(summary["total_value"], 3700.0)

    def test_03_summary_by_gauge(self):
        self._create_test_coil("C1", stock_lbs=5000, gauge="10GA")
        self._create_test_coil("C2", stock_lbs=3000, gauge="14GA")
        summary = get_inventory_summary(self.tmpdir)
        self.assertEqual(summary["by_gauge"]["10GA"], 5000)
        self.assertEqual(summary["by_gauge"]["14GA"], 3000)

    def test_04_summary_by_status(self):
        self._create_test_coil("C1", stock_lbs=5000, min_order_lbs=3000)  # active
        self._create_test_coil("C2", stock_lbs=100, min_order_lbs=3000)   # low_stock
        self._create_test_coil("C3", stock_lbs=0, min_order_lbs=3000)     # depleted
        summary = get_inventory_summary(self.tmpdir)
        self.assertEqual(summary["by_status"]["active"], 1)
        self.assertEqual(summary["by_status"]["low_stock"], 1)
        self.assertEqual(summary["by_status"]["depleted"], 1)

    def test_05_summary_low_stock_list(self):
        self._create_test_coil("C1", stock_lbs=100, min_order_lbs=3000)
        summary = get_inventory_summary(self.tmpdir)
        self.assertEqual(len(summary["low_stock_coils"]), 1)
        self.assertEqual(summary["low_stock_coils"][0]["coil_id"], "C1")

    def test_06_summary_committed_and_available(self):
        self._create_test_coil(stock_lbs=5000)
        allocate_stock(self.tmpdir, "COIL-001", "JOB-001", 2000)
        summary = get_inventory_summary(self.tmpdir)
        self.assertEqual(summary["total_committed_lbs"], 2000)
        self.assertEqual(summary["total_available_lbs"], 3000)

    def test_07_summary_alert_count(self):
        self._create_test_coil(stock_lbs=100, min_order_lbs=3000)
        summary = get_inventory_summary(self.tmpdir)
        self.assertGreater(summary["active_alerts"], 0)

    def test_08_summary_mill_cert_count(self):
        self._create_test_coil()
        add_mill_cert(self.tmpdir, "COIL-001", "HT-1")
        add_mill_cert(self.tmpdir, "COIL-001", "HT-2")
        summary = get_inventory_summary(self.tmpdir)
        self.assertEqual(summary["total_mill_certs"], 2)


# ═════════════════════════════════════════════════════════════════════════════
# TEST 13: Coil History
# ═════════════════════════════════════════════════════════════════════════════

class Test13_CoilHistory(TestBase):

    def test_01_coil_history_basic(self):
        self._create_test_coil(stock_lbs=5000)
        receive_stock(self.tmpdir, "COIL-001", 2000)
        consume_stock(self.tmpdir, "COIL-001", 1000)
        add_mill_cert(self.tmpdir, "COIL-001", "HT-1")

        history = get_coil_history(self.tmpdir, "COIL-001")
        self.assertIn("coil", history)
        self.assertIn("transactions", history)
        self.assertIn("allocations", history)
        self.assertIn("mill_certs", history)
        self.assertIn("receiving_records", history)
        self.assertGreater(len(history["transactions"]), 0)
        self.assertEqual(len(history["mill_certs"]), 1)

    def test_02_coil_history_not_found(self):
        with self.assertRaises(ValueError):
            get_coil_history(self.tmpdir, "NONEXISTENT")


# ═════════════════════════════════════════════════════════════════════════════
# TEST 14: Stock Valuation
# ═════════════════════════════════════════════════════════════════════════════

class Test14_StockValuation(TestBase):

    def test_01_valuation_basic(self):
        self._create_test_coil("C1", stock_lbs=5000, price_per_lb=0.50, gauge="10GA")
        self._create_test_coil("C2", stock_lbs=3000, price_per_lb=0.40, gauge="14GA")
        val = get_stock_valuation(self.tmpdir)
        self.assertEqual(val["total_value"], 3700.0)

    def test_02_valuation_by_gauge(self):
        self._create_test_coil("C1", stock_lbs=5000, price_per_lb=0.50, gauge="10GA")
        self._create_test_coil("C2", stock_lbs=3000, price_per_lb=0.40, gauge="14GA")
        val = get_stock_valuation(self.tmpdir)
        self.assertEqual(val["by_gauge"]["10GA"]["value"], 2500.0)
        self.assertEqual(val["by_gauge"]["14GA"]["value"], 1200.0)

    def test_03_valuation_by_grade(self):
        self._create_test_coil("C1", stock_lbs=5000, price_per_lb=0.50,
                               grade="Galvalume")
        val = get_stock_valuation(self.tmpdir)
        self.assertEqual(val["by_grade"]["Galvalume"]["value"], 2500.0)

    def test_04_valuation_empty(self):
        val = get_stock_valuation(self.tmpdir)
        self.assertEqual(val["total_value"], 0)


# ═════════════════════════════════════════════════════════════════════════════
# TEST 15: Handler Existence
# ═════════════════════════════════════════════════════════════════════════════

class Test15_Handlers(TestBase):

    def test_01_all_handlers_exist(self):
        import tf_handlers
        handler_names = [
            "InventoryDashboardPageHandler",
            "CoilListAPIHandler", "CoilDetailAPIHandler",
            "CoilCreateHandler", "CoilUpdateHandler", "CoilDeleteAPIHandler",
            "ReceiveStockHandler", "AdjustStockHandler", "ConsumeStockHandler",
            "TransactionListAPIHandler",
            "AllocateStockHandler", "ReleaseAllocationHandler",
            "AllocationListAPIHandler",
            "AlertListAPIHandler", "AlertAcknowledgeHandler",
            "GenerateAlertsHandler",
            "ReceivingListAPIHandler",
            "MillCertListAPIHandler", "MillCertAddHandler", "MillCertDeleteHandler",
            "InventorySummaryAPIHandler", "CoilHistoryAPIHandler",
            "StockValuationAPIHandler", "InventoryConfigHandler",
        ]
        for name in handler_names:
            self.assertTrue(hasattr(tf_handlers, name), f"Missing handler: {name}")

    def test_02_routes_registered(self):
        import tf_handlers
        routes = tf_handlers.get_routes()
        patterns = [r[0] for r in routes]
        expected = [
            r"/inventory",
            r"/api/inventory/coils",
            r"/api/inventory/coil/detail",
            r"/api/inventory/coil/create",
            r"/api/inventory/coil/update",
            r"/api/inventory/coil/delete",
            r"/api/inventory/receive",
            r"/api/inventory/adjust",
            r"/api/inventory/consume",
            r"/api/inventory/transactions",
            r"/api/inventory/allocate",
            r"/api/inventory/allocate/release",
            r"/api/inventory/allocations",
            r"/api/inventory/alerts",
            r"/api/inventory/alerts/acknowledge",
            r"/api/inventory/alerts/generate",
            r"/api/inventory/receiving",
            r"/api/inventory/mill-certs",
            r"/api/inventory/mill-cert/add",
            r"/api/inventory/mill-cert/delete",
            r"/api/inventory/summary",
            r"/api/inventory/coil/history",
            r"/api/inventory/valuation",
            r"/api/inventory/inv-config",
        ]
        for e in expected:
            self.assertIn(e, patterns, f"Missing route: {e}")

    def test_03_total_route_count(self):
        import tf_handlers
        routes = tf_handlers.get_routes()
        self.assertGreaterEqual(len(routes), 260)

    def test_04_handler_permissions(self):
        import tf_handlers
        # Check specific permission assignments
        self.assertEqual(tf_handlers.CoilCreateHandler.required_permission,
                         "edit_inventory")
        self.assertEqual(tf_handlers.ReceiveStockHandler.required_permission,
                         "receive_inventory")
        self.assertEqual(tf_handlers.AllocateStockHandler.required_permission,
                         "allocate_stock")
        self.assertEqual(tf_handlers.MillCertAddHandler.required_permission,
                         "manage_mill_certs")
        self.assertEqual(tf_handlers.StockValuationAPIHandler.required_permission,
                         "view_inventory_costs")


# ═════════════════════════════════════════════════════════════════════════════
# TEST 16: Template
# ═════════════════════════════════════════════════════════════════════════════

class Test16_Template(TestBase):

    def test_01_template_loads(self):
        from templates.inventory_dashboard_page import INVENTORY_DASHBOARD_PAGE_HTML
        self.assertGreater(len(INVENTORY_DASHBOARD_PAGE_HTML), 10000)

    def test_02_template_has_tabs(self):
        from templates.inventory_dashboard_page import INVENTORY_DASHBOARD_PAGE_HTML
        self.assertIn("tab-coils", INVENTORY_DASHBOARD_PAGE_HTML)
        self.assertIn("tab-transactions", INVENTORY_DASHBOARD_PAGE_HTML)
        self.assertIn("tab-allocations", INVENTORY_DASHBOARD_PAGE_HTML)

    def test_03_template_has_api_endpoints(self):
        from templates.inventory_dashboard_page import INVENTORY_DASHBOARD_PAGE_HTML
        self.assertIn("/api/inventory/coils", INVENTORY_DASHBOARD_PAGE_HTML)
        self.assertIn("/api/inventory/summary", INVENTORY_DASHBOARD_PAGE_HTML)

    def test_04_template_has_modals(self):
        from templates.inventory_dashboard_page import INVENTORY_DASHBOARD_PAGE_HTML
        self.assertIn("modal", INVENTORY_DASHBOARD_PAGE_HTML.lower())


# ═════════════════════════════════════════════════════════════════════════════
# TEST 17: Integration — Full Workflow
# ═════════════════════════════════════════════════════════════════════════════

class Test17_Integration(TestBase):

    def test_01_full_coil_lifecycle(self):
        """Test: create → receive → allocate → consume → adjust → summary."""
        # Create coil
        create_coil(self.tmpdir, "COIL-TEST", "Test Coil", "10GA", "A36",
                     stock_lbs=0, price_per_lb=0.50, min_order_lbs=2000,
                     created_by="admin")

        # Receive material
        receive_stock(self.tmpdir, "COIL-TEST", 5000, po_number="PO-1",
                      heat_number="HT-100", received_by="warehouse")

        # Add mill cert
        add_mill_cert(self.tmpdir, "COIL-TEST", "HT-100",
                      mill_name="US Steel", material_spec="A36")

        # Allocate to job
        alloc = allocate_stock(self.tmpdir, "COIL-TEST", "JOB-001", 2000,
                               allocated_by="pm")

        # Consume material
        consume_stock(self.tmpdir, "COIL-TEST", 1500, job_code="JOB-001",
                      consumed_by="operator")

        # Check state
        coil = get_coil(self.tmpdir, "COIL-TEST")
        self.assertEqual(coil["stock_lbs"], 3500)  # 5000 - 1500
        self.assertEqual(coil["committed_lbs"], 2000)
        self.assertEqual(coil["heat_num"], "HT-100")

        # Adjust for scrap
        adjust_stock(self.tmpdir, "COIL-TEST", -100, reason="Scrap")
        coil = get_coil(self.tmpdir, "COIL-TEST")
        self.assertEqual(coil["stock_lbs"], 3400)

        # Check history
        history = get_coil_history(self.tmpdir, "COIL-TEST")
        self.assertGreater(len(history["transactions"]), 3)
        self.assertEqual(len(history["allocations"]), 1)
        self.assertEqual(len(history["mill_certs"]), 1)
        self.assertEqual(len(history["receiving_records"]), 1)

        # Summary
        summary = get_inventory_summary(self.tmpdir)
        self.assertEqual(summary["total_coils"], 1)
        self.assertEqual(summary["total_stock_lbs"], 3400)
        self.assertEqual(summary["total_value"], 1700.0)

    def test_02_multi_coil_multi_job(self):
        """Test multiple coils allocated across multiple jobs."""
        create_coil(self.tmpdir, "C-10GA", "10GA Steel", "10GA", "A36",
                     stock_lbs=10000, price_per_lb=0.45, created_by="admin")
        create_coil(self.tmpdir, "C-14GA", "14GA Steel", "14GA", "Galvalume",
                     stock_lbs=8000, price_per_lb=0.55, created_by="admin")

        allocate_stock(self.tmpdir, "C-10GA", "JOB-A", 3000)
        allocate_stock(self.tmpdir, "C-10GA", "JOB-B", 2000)
        allocate_stock(self.tmpdir, "C-14GA", "JOB-A", 4000)

        # Check per-coil
        c1 = get_coil(self.tmpdir, "C-10GA")
        self.assertEqual(c1["committed_lbs"], 5000)
        c2 = get_coil(self.tmpdir, "C-14GA")
        self.assertEqual(c2["committed_lbs"], 4000)

        # Check per-job allocations
        job_a = list_allocations(self.tmpdir, job_code="JOB-A")
        self.assertEqual(len(job_a), 2)
        job_b = list_allocations(self.tmpdir, job_code="JOB-B")
        self.assertEqual(len(job_b), 1)

        # Summary
        summary = get_inventory_summary(self.tmpdir)
        self.assertEqual(summary["total_coils"], 2)
        self.assertEqual(summary["total_stock_lbs"], 18000)
        self.assertEqual(summary["total_committed_lbs"], 9000)
        self.assertEqual(summary["total_available_lbs"], 9000)

    def test_03_alert_lifecycle(self):
        """Low stock → alert → acknowledge → receive → alert cleared."""
        create_coil(self.tmpdir, "C1", "Low Coil", "10GA", "A36",
                     stock_lbs=500, min_order_lbs=3000, created_by="admin")

        # Should have alert
        alerts = list_alerts(self.tmpdir, acknowledged=False)
        self.assertGreater(len(alerts), 0)

        # Acknowledge it
        acknowledge_alert(self.tmpdir, alerts[0]["alert_id"], "admin")
        acked = list_alerts(self.tmpdir, acknowledged=True)
        self.assertGreater(len(acked), 0)

        # Consume more to trigger new alert
        consume_stock(self.tmpdir, "C1", 400)
        new_alerts = list_alerts(self.tmpdir, acknowledged=False, coil_id="C1")
        self.assertGreater(len(new_alerts), 0)

        # Receive stock to clear
        receive_stock(self.tmpdir, "C1", 5000)
        cleared = list_alerts(self.tmpdir, acknowledged=False, coil_id="C1")
        self.assertEqual(len(cleared), 0)


# ═════════════════════════════════════════════════════════════════════════════
# TEST 18: Edge Cases
# ═════════════════════════════════════════════════════════════════════════════

class Test18_EdgeCases(TestBase):

    def test_01_empty_inventory(self):
        coils = list_coils(self.tmpdir)
        self.assertEqual(len(coils), 0)

    def test_02_empty_transactions(self):
        txns = list_transactions(self.tmpdir)
        self.assertEqual(len(txns), 0)

    def test_03_empty_allocations(self):
        allocs = list_allocations(self.tmpdir)
        self.assertEqual(len(allocs), 0)

    def test_04_empty_alerts(self):
        alerts = list_alerts(self.tmpdir)
        self.assertEqual(len(alerts), 0)

    def test_05_empty_receiving(self):
        records = list_receiving(self.tmpdir)
        self.assertEqual(len(records), 0)

    def test_06_empty_mill_certs(self):
        certs = list_mill_certs(self.tmpdir)
        self.assertEqual(len(certs), 0)

    def test_07_coil_id_with_special_chars(self):
        coil = create_coil(self.tmpdir, "COIL-10GA-48-001", "Special Coil",
                           "10GA", "A36", created_by="admin")
        self.assertEqual(coil["name"], "Special Coil")
        found = get_coil(self.tmpdir, "COIL-10GA-48-001")
        self.assertIsNotNone(found)

    def test_08_large_quantity_receive(self):
        self._create_test_coil(stock_lbs=0)
        receive_stock(self.tmpdir, "COIL-001", 100000)
        coil = get_coil(self.tmpdir, "COIL-001")
        self.assertEqual(coil["stock_lbs"], 100000)

    def test_09_multiple_adjustments(self):
        self._create_test_coil(stock_lbs=5000)
        for i in range(10):
            adjust_stock(self.tmpdir, "COIL-001", -100)
        coil = get_coil(self.tmpdir, "COIL-001")
        self.assertEqual(coil["stock_lbs"], 4000)

    def test_10_supplier_filter_case_insensitive(self):
        self._create_test_coil(supplier="Steel Corporation")
        coils = list_coils(self.tmpdir, supplier="steel")
        self.assertEqual(len(coils), 1)


# ═════════════════════════════════════════════════════════════════════════════
# TEST 19: Dataclass Round-Trip Serialization
# ═════════════════════════════════════════════════════════════════════════════

class Test19_Serialization(TestBase):

    def test_01_transaction_round_trip(self):
        txn = InventoryTransaction(coil_id="C1", transaction_type="receive",
                                   quantity_lbs=5000, balance_after=5000)
        d = txn.to_dict()
        txn2 = InventoryTransaction.from_dict(d)
        self.assertEqual(txn.transaction_id, txn2.transaction_id)
        self.assertEqual(txn.quantity_lbs, txn2.quantity_lbs)

    def test_02_alert_round_trip(self):
        alert = StockAlert(coil_id="C1", alert_level="critical",
                           alert_type="depleted", message="Depleted!")
        d = alert.to_dict()
        alert2 = StockAlert.from_dict(d)
        self.assertEqual(alert.alert_id, alert2.alert_id)
        self.assertEqual(alert.message, alert2.message)

    def test_03_allocation_round_trip(self):
        alloc = Allocation(coil_id="C1", job_code="JOB-1",
                           quantity_lbs=2000, consumed_lbs=500)
        d = alloc.to_dict()
        alloc2 = Allocation.from_dict(d)
        self.assertEqual(alloc.allocation_id, alloc2.allocation_id)
        self.assertEqual(alloc.remaining_lbs, 1500)

    def test_04_receiving_round_trip(self):
        rec = ReceivingRecord(coil_id="C1", po_number="PO-1",
                              quantity_lbs=5000, heat_number="HT-1")
        d = rec.to_dict()
        rec2 = ReceivingRecord.from_dict(d)
        self.assertEqual(rec.receiving_id, rec2.receiving_id)
        self.assertEqual(rec.po_number, rec2.po_number)


# ═════════════════════════════════════════════════════════════════════════════
# TEST 20: Config Constants Export
# ═════════════════════════════════════════════════════════════════════════════

class Test20_Config(TestBase):

    def test_01_config_has_all_statuses(self):
        self.assertEqual(len(COIL_STATUSES), 5)
        for s in ["active", "low_stock", "depleted", "on_order", "quarantine"]:
            self.assertIn(s, COIL_STATUSES)

    def test_02_config_has_all_txn_types(self):
        self.assertEqual(len(TRANSACTION_TYPES), 6)
        for t in ["receive", "allocate", "consume", "adjust", "return", "transfer"]:
            self.assertIn(t, TRANSACTION_TYPES)

    def test_03_gauges_cover_common_sizes(self):
        for g in ["26GA", "24GA", "22GA", "20GA", "18GA", "16GA", "14GA", "12GA", "10GA"]:
            self.assertIn(g, COIL_GAUGES)

    def test_04_grades_cover_structural_steel(self):
        for g in ["A36", "A572 Gr 50", "A992"]:
            self.assertIn(g, MATERIAL_GRADES)


# ═════════════════════════════════════════════════════════════════════════════
# TEST 21: Sidebar & Module Integration
# ═════════════════════════════════════════════════════════════════════════════

class Test21_SidebarAndModules(TestBase):

    def test_01_shared_nav_has_inventory_link(self):
        """Check that shared_nav source contains /inventory link."""
        import inspect
        from templates import shared_nav
        source = inspect.getsource(shared_nav)
        self.assertIn("/inventory", source)

    def test_02_inventory_module_importable(self):
        from shop_drawings import inventory
        self.assertTrue(hasattr(inventory, "create_coil"))
        self.assertTrue(hasattr(inventory, "get_inventory_summary"))
        self.assertTrue(hasattr(inventory, "allocate_stock"))

    def test_03_all_routes_have_unique_patterns(self):
        import tf_handlers
        routes = tf_handlers.get_routes()
        patterns = [r[0] for r in routes]
        # Check for duplicate patterns (excluding static)
        non_static = [p for p in patterns if "static" not in p]
        self.assertEqual(len(non_static), len(set(non_static)),
                         "Duplicate route patterns found!")


# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    unittest.main(verbosity=2)
