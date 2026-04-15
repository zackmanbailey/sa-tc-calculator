"""
BUG-001 + BUG-002 FIX — Inventory Handler Patches for tf_handlers.py
=====================================================================

These handlers replace/supplement the existing inventory handlers in tf_handlers.py.
They connect to the new inventory.py engine for full CRUD, receiving, PO management,
alerts, and QR/ZPL sticker generation.

INSTRUCTIONS:
1. Add this import near the top of tf_handlers.py:

   from shop_drawings.inventory import (
       create_coil, get_coil, list_coils, update_coil, delete_coil,
       receive_stock, adjust_stock, consume_stock, list_transactions,
       allocate_stock, release_allocation, list_allocations,
       add_mill_cert, list_mill_certs, delete_mill_cert,
       generate_stock_alerts, list_alerts, acknowledge_alert,
       get_inventory_summary, get_coil_history, get_stock_valuation,
       get_coil_qr_data, generate_coil_sticker_zpl, auto_deduct_for_fabrication,
       create_purchase_order, list_purchase_orders, update_purchase_order,
       receive_against_po, list_receiving,
   )

2. Replace the InventoryPageHandler with InventoryDashboardPageHandler

3. Add all handler classes below AFTER the existing inventory handlers

4. Add these routes to get_routes():

   # Inventory Dashboard (replaces old /inventory route)
   (r"/inventory", InventoryDashboardPageHandler),

   # Coil CRUD API
   (r"/api/inventory/coils", CoilListAPIHandler),
   (r"/api/inventory/coil/create", CoilCreateAPIHandler),
   (r"/api/inventory/coil/detail", CoilDetailAPIHandler),
   (r"/api/inventory/coil/update", CoilUpdateAPIHandler),
   (r"/api/inventory/coil/delete", CoilDeleteAPIHandler),

   # Stock movements
   (r"/api/inventory/receive", ReceiveStockAPIHandler),
   (r"/api/inventory/adjust", AdjustStockAPIHandler),
   (r"/api/inventory/consume", ConsumeStockAPIHandler),

   # Transactions
   (r"/api/inventory/transactions", TransactionListAPIHandler),

   # Allocations
   (r"/api/inventory/allocate", AllocateStockAPIHandler),
   (r"/api/inventory/allocations", AllocationListAPIHandler),

   # Alerts
   (r"/api/inventory/alerts", AlertListAPIHandler),
   (r"/api/inventory/alerts/acknowledge", AlertAcknowledgeAPIHandler),
   (r"/api/inventory/alerts/generate", GenerateAlertsAPIHandler),

   # Mill certs
   (r"/api/inventory/mill-certs", MillCertListAPIHandler),
   (r"/api/inventory/mill-cert/add", MillCertAddAPIHandler),

   # Analytics
   (r"/api/inventory/summary", InventorySummaryAPIHandler),
   (r"/api/inventory/coil/history", CoilHistoryAPIHandler),
   (r"/api/inventory/valuation", StockValuationAPIHandler),

   # Purchase orders
   (r"/api/inventory/purchase-orders", PurchaseOrderListAPIHandler),
   (r"/api/inventory/purchase-order/create", PurchaseOrderCreateAPIHandler),
   (r"/api/inventory/receive-against-po", ReceiveAgainstPOAPIHandler),

   # Coil QR/Sticker
   (r"/api/inventory/coil/qr", CoilQRDataAPIHandler),
   (r"/api/inventory/coil/sticker-zpl", CoilStickerZPLAPIHandler),

   # Receiving history
   (r"/api/inventory/receiving", ReceivingHistoryAPIHandler),
"""


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD PAGE
# ─────────────────────────────────────────────────────────────────────────────

class InventoryDashboardPageHandler(BaseHandler):
    """GET /inventory — Full inventory management dashboard."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        from templates.inventory_dashboard_page import INVENTORY_DASHBOARD_PAGE_HTML
        self.render_with_nav(INVENTORY_DASHBOARD_PAGE_HTML, active_page="inventory")


# ─────────────────────────────────────────────────────────────────────────────
# COIL CRUD
# ─────────────────────────────────────────────────────────────────────────────

class CoilListAPIHandler(BaseHandler):
    """GET /api/inventory/coils — List all coils with filters."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        try:
            gauge = self.get_query_argument("gauge", "")
            grade = self.get_query_argument("grade", "")
            supplier = self.get_query_argument("supplier", "")
            status = self.get_query_argument("status", "")
            low_stock = self.get_query_argument("low_stock", "false") == "true"

            coils = list_coils(INVENTORY_DIR, gauge=gauge, grade=grade,
                              supplier=supplier, status=status, low_stock_only=low_stock)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "coils": coils}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class CoilCreateAPIHandler(BaseHandler):
    """POST /api/inventory/coil/create — Create a new coil."""
    required_roles = ["admin", "estimator"]

    def post(self):
        try:
            body = json_decode(self.request.body)
            coil = create_coil(
                INVENTORY_DIR,
                coil_id=body.get("coil_id", "").strip(),
                name=body.get("name", "").strip(),
                gauge=body.get("gauge", ""),
                grade=body.get("grade", ""),
                supplier=body.get("supplier", ""),
                weight_lbs=float(body.get("weight_lbs", 0)),
                width_in=float(body.get("width_in", 0)),
                stock_lbs=float(body.get("stock_lbs", 0)),
                price_per_lb=float(body.get("price_per_lb", 0)),
                min_order_lbs=float(body.get("min_order_lbs", 5000)),
                lead_time_weeks=int(body.get("lead_time_weeks", 8)),
                lbs_per_lft=float(body.get("lbs_per_lft", 0)),
                heat_num=body.get("heat_num", ""),
                created_by=self.get_current_user() or "system",
            )
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "coil": coil}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class CoilDetailAPIHandler(BaseHandler):
    """GET /api/inventory/coil/detail?coil_id=X — Get single coil."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        try:
            coil_id = self.get_query_argument("coil_id", "").strip()
            coil = get_coil(INVENTORY_DIR, coil_id)
            if not coil:
                self.set_status(404)
                self.write(json_encode({"ok": False, "error": "Coil not found"}))
                return
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "coil": coil}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class CoilUpdateAPIHandler(BaseHandler):
    """POST /api/inventory/coil/update — Update coil fields."""
    required_roles = ["admin", "estimator"]

    def post(self):
        try:
            body = json_decode(self.request.body)
            coil_id = body.pop("coil_id", "").strip()
            coil = update_coil(INVENTORY_DIR, coil_id, **body)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "coil": coil}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class CoilDeleteAPIHandler(BaseHandler):
    """POST /api/inventory/coil/delete — Delete a coil."""
    required_roles = ["admin"]

    def post(self):
        try:
            body = json_decode(self.request.body)
            coil_id = body.get("coil_id", "").strip()
            success = delete_coil(INVENTORY_DIR, coil_id)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": success}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


# ─────────────────────────────────────────────────────────────────────────────
# STOCK MOVEMENTS
# ─────────────────────────────────────────────────────────────────────────────

class ReceiveStockAPIHandler(BaseHandler):
    """POST /api/inventory/receive — Receive stock into a coil."""
    required_roles = ["admin", "estimator", "shop"]

    def post(self):
        try:
            body = json_decode(self.request.body)
            result = receive_stock(
                INVENTORY_DIR,
                coil_id=body.get("coil_id", "").strip(),
                quantity_lbs=float(body.get("quantity_lbs", 0)),
                po_number=body.get("po_number", ""),
                bol_number=body.get("bol_number", ""),
                heat_number=body.get("heat_number", ""),
                supplier=body.get("supplier", ""),
                condition_notes=body.get("condition_notes", ""),
                received_by=self.get_current_user() or "system",
            )
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, **result}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class AdjustStockAPIHandler(BaseHandler):
    """POST /api/inventory/adjust — Adjust stock (correction)."""
    required_roles = ["admin"]

    def post(self):
        try:
            body = json_decode(self.request.body)
            result = adjust_stock(
                INVENTORY_DIR,
                coil_id=body.get("coil_id", "").strip(),
                quantity_lbs=float(body.get("quantity_lbs", 0)),
                notes=body.get("notes", ""),
                adjusted_by=self.get_current_user() or "system",
            )
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, **result}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class ConsumeStockAPIHandler(BaseHandler):
    """POST /api/inventory/consume — Consume stock for a job."""
    required_roles = ["admin", "estimator", "shop"]

    def post(self):
        try:
            body = json_decode(self.request.body)
            result = consume_stock(
                INVENTORY_DIR,
                coil_id=body.get("coil_id", "").strip(),
                quantity_lbs=float(body.get("quantity_lbs", 0)),
                job_code=body.get("job_code", ""),
                work_order_ref=body.get("work_order_ref", ""),
                notes=body.get("notes", ""),
                consumed_by=self.get_current_user() or "system",
            )
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, **result}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


# ─────────────────────────────────────────────────────────────────────────────
# TRANSACTIONS, ALLOCATIONS, ALERTS
# ─────────────────────────────────────────────────────────────────────────────

class TransactionListAPIHandler(BaseHandler):
    """GET /api/inventory/transactions — List transactions."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        try:
            coil_id = self.get_query_argument("coil_id", "")
            txn_type = self.get_query_argument("type", "")
            limit = int(self.get_query_argument("limit", "100"))
            txns = list_transactions(INVENTORY_DIR, coil_id=coil_id,
                                   txn_type=txn_type, limit=limit)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "transactions": txns}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class AllocateStockAPIHandler(BaseHandler):
    """POST /api/inventory/allocate — Allocate stock to a job."""
    required_roles = ["admin", "estimator"]

    def post(self):
        try:
            body = json_decode(self.request.body)
            result = allocate_stock(
                INVENTORY_DIR,
                coil_id=body.get("coil_id", "").strip(),
                job_code=body.get("job_code", ""),
                quantity_lbs=float(body.get("quantity_lbs", 0)),
                work_order_ref=body.get("work_order_ref", ""),
                allocated_by=self.get_current_user() or "system",
            )
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, **result}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class AllocationListAPIHandler(BaseHandler):
    """GET /api/inventory/allocations — List allocations."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        try:
            coil_id = self.get_query_argument("coil_id", "")
            job_code = self.get_query_argument("job_code", "")
            allocs = list_allocations(INVENTORY_DIR, coil_id=coil_id, job_code=job_code)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "allocations": allocs}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class AlertListAPIHandler(BaseHandler):
    """GET /api/inventory/alerts — List alerts."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        try:
            acknowledged = self.get_query_argument("acknowledged", None)
            if acknowledged is not None:
                acknowledged = acknowledged == "true"
            alerts = list_alerts(INVENTORY_DIR, acknowledged=acknowledged)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "alerts": alerts}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class AlertAcknowledgeAPIHandler(BaseHandler):
    """POST /api/inventory/alerts/acknowledge — Acknowledge an alert."""
    required_roles = ["admin", "estimator"]

    def post(self):
        try:
            body = json_decode(self.request.body)
            result = acknowledge_alert(
                INVENTORY_DIR,
                alert_id=body.get("alert_id", ""),
                acknowledged_by=self.get_current_user() or "system",
            )
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, **result}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class GenerateAlertsAPIHandler(BaseHandler):
    """POST /api/inventory/alerts/generate — Scan and generate alerts."""
    required_roles = ["admin"]

    def post(self):
        try:
            new_alerts = generate_stock_alerts(INVENTORY_DIR)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "new_alert_coils": new_alerts}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


# ─────────────────────────────────────────────────────────────────────────────
# MILL CERTS
# ─────────────────────────────────────────────────────────────────────────────

class MillCertListAPIHandler(BaseHandler):
    """GET /api/inventory/mill-certs — List mill certificates."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        try:
            coil_id = self.get_query_argument("coil_id", "")
            certs = list_mill_certs(INVENTORY_DIR, coil_id=coil_id)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "mill_certs": certs}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class MillCertAddAPIHandler(BaseHandler):
    """POST /api/inventory/mill-cert/add — Add a mill certificate."""
    required_roles = ["admin", "estimator"]

    def post(self):
        try:
            body = json_decode(self.request.body)
            result = add_mill_cert(
                INVENTORY_DIR,
                coil_id=body.get("coil_id", ""),
                heat_number=body.get("heat_number", ""),
                mill_name=body.get("mill_name", ""),
                cert_date=body.get("cert_date", ""),
                filename=body.get("filename", ""),
                added_by=self.get_current_user() or "system",
            )
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, **result}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


# ─────────────────────────────────────────────────────────────────────────────
# ANALYTICS
# ─────────────────────────────────────────────────────────────────────────────

class InventorySummaryAPIHandler(BaseHandler):
    """GET /api/inventory/summary — Dashboard summary metrics."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        try:
            summary = get_inventory_summary(INVENTORY_DIR)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, **summary}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class CoilHistoryAPIHandler(BaseHandler):
    """GET /api/inventory/coil/history?coil_id=X — Full coil history."""
    required_roles = ["admin", "estimator"]

    def get(self):
        try:
            coil_id = self.get_query_argument("coil_id", "").strip()
            history = get_coil_history(INVENTORY_DIR, coil_id)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, **history}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class StockValuationAPIHandler(BaseHandler):
    """GET /api/inventory/valuation — Stock valuation report."""
    required_roles = ["admin"]

    def get(self):
        try:
            valuation = get_stock_valuation(INVENTORY_DIR)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, **valuation}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


# ─────────────────────────────────────────────────────────────────────────────
# PURCHASE ORDERS
# ─────────────────────────────────────────────────────────────────────────────

class PurchaseOrderListAPIHandler(BaseHandler):
    """GET /api/inventory/purchase-orders — List POs."""
    required_roles = ["admin", "estimator"]

    def get(self):
        try:
            status = self.get_query_argument("status", "")
            pos = list_purchase_orders(INVENTORY_DIR, status=status)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "purchase_orders": pos}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class PurchaseOrderCreateAPIHandler(BaseHandler):
    """POST /api/inventory/purchase-order/create — Create a PO."""
    required_roles = ["admin", "estimator"]

    def post(self):
        try:
            body = json_decode(self.request.body)
            po = create_purchase_order(
                INVENTORY_DIR,
                supplier=body.get("supplier", ""),
                items=body.get("items", []),
                notes=body.get("notes", ""),
                created_by=self.get_current_user() or "system",
            )
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "purchase_order": po}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class ReceiveAgainstPOAPIHandler(BaseHandler):
    """POST /api/inventory/receive-against-po — Receive stock against a PO."""
    required_roles = ["admin", "estimator", "shop"]

    def post(self):
        try:
            body = json_decode(self.request.body)
            result = receive_against_po(
                INVENTORY_DIR,
                po_id=body.get("po_id", ""),
                coil_id=body.get("coil_id", ""),
                quantity_lbs=float(body.get("quantity_lbs", 0)),
                heat_number=body.get("heat_number", ""),
                bol_number=body.get("bol_number", ""),
                condition_notes=body.get("condition_notes", ""),
                received_by=self.get_current_user() or "system",
            )
            self.set_header("Content-Type", "application/json")
            self.write(json_encode(result))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


# ─────────────────────────────────────────────────────────────────────────────
# QR CODE & STICKERS
# ─────────────────────────────────────────────────────────────────────────────

class CoilQRDataAPIHandler(BaseHandler):
    """GET /api/inventory/coil/qr?coil_id=X — Get coil QR code data."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        try:
            coil_id = self.get_query_argument("coil_id", "").strip()
            app_base_url = f"{self.request.protocol}://{self.request.host}"
            data = get_coil_qr_data(INVENTORY_DIR, coil_id, app_base_url)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode(data))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class CoilStickerZPLAPIHandler(BaseHandler):
    """GET /api/inventory/coil/sticker-zpl?coil_id=X — Generate ZPL sticker for Zebra ZT411."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        try:
            coil_id = self.get_query_argument("coil_id", "").strip()
            app_base_url = f"{self.request.protocol}://{self.request.host}"
            zpl = generate_coil_sticker_zpl(INVENTORY_DIR, coil_id, app_base_url)
            if not zpl:
                self.set_status(404)
                self.write("Coil not found")
                return
            filename = f"{coil_id}_label.zpl"
            self.set_header("Content-Type", "text/plain")
            self.set_header("Content-Disposition", f'attachment; filename="{filename}"')
            self.write(zpl)
        except Exception as e:
            self.set_status(500)
            self.write(str(e))


# ─────────────────────────────────────────────────────────────────────────────
# RECEIVING HISTORY
# ─────────────────────────────────────────────────────────────────────────────

class ReceivingHistoryAPIHandler(BaseHandler):
    """GET /api/inventory/receiving — List receiving records."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        try:
            coil_id = self.get_query_argument("coil_id", "")
            records = list_receiving(INVENTORY_DIR, coil_id=coil_id)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "records": records}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))
