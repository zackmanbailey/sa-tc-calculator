# BUG-001 + BUG-002 Fix: Inventory Module Overhaul

## What This Fixes
- **BUG-001**: "Add New Coil" button now works — `showNewCoilModal()` is properly defined in the template
- **BUG-002**: All inventory API endpoints return proper responses (no more 405 errors)
- **BUG-003**: Resolved automatically — inventory alerts and low-stock warnings now functional
- **Auto-deduct on fabrication**: When a shop item starts via QR scan, material is automatically consumed from inventory
- **QR codes on coils**: Each coil gets a QR sticker (Zebra ZT411, 4x6 labels, 203 DPI) linking to mill cert viewer and job assignment info
- **Purchase Order management**: Full PO lifecycle — draft, submit, confirm, receive against PO
- **Receiving workflow**: Receive stock standalone or against an existing PO with weight verification

## Files

### 1. `shop_drawings/inventory.py` (FULL REPLACEMENT)
**Replace**: `combined_calc/shop_drawings/inventory.py`
**With**: `BUG-001-002-fix/inventory.py`

New/enhanced features:
- `get_coil_qr_data()` — Returns QR URL, coil details, mill certs, job assignments
- `generate_coil_sticker_zpl()` — ZPL for Zebra ZT411 (4x6 thermal transfer labels, 203 DPI)
- `auto_deduct_for_fabrication()` — Called on QR scan start, deducts based on MATERIAL_USAGE per component type
- `MATERIAL_USAGE` dict — Maps component types to coil types and estimated weights:
  - column → c_section_23: 450 lbs
  - rafter → c_section_23: 380 lbs
  - purlin → z_purlin_20: 120 lbs
  - sag_rod → angle_4_16ga: 15 lbs
  - strap → strap_16ga: 25 lbs
  - endcap → c_section_23: 85 lbs
  - roofing → spartan_rib_48: 200 lbs
  - gusset → gusset_10ga: 35 lbs
  - base_plate → plate_6_10ga: 60 lbs
- Purchase Order system: `create_purchase_order()`, `list_purchase_orders()`, `update_purchase_order()`, `receive_against_po()`
- PO statuses: draft → submitted → confirmed → partially_received → received (+ cancelled)
- All existing inventory functions preserved unchanged

### 2. `templates/inventory_dashboard_page.py` (NEW FILE)
**Add**: `combined_calc/templates/inventory_dashboard_page.py`
**From**: `BUG-001-002-fix/inventory_dashboard_page.py`

This is a NEW template file for the full inventory dashboard. Features:
- 5 tabs: Coils, Receiving, Purchase Orders, Transactions, Alerts
- Summary metrics cards (total stock, committed, available, alerts)
- `showNewCoilModal()` — PROPERLY DEFINED (this was the BUG-001 root cause)
- Filterable/searchable tables for all data views
- Modal forms for add coil, receive stock, create PO
- QR sticker print buttons per coil
- Alert acknowledgment workflow

### 3. `tf_handlers.py` (PATCH — add new handlers)
**File**: `combined_calc/tf_handlers.py`
**Reference**: `BUG-001-002-fix/tf_handlers_inventory_patch.py`

Steps:

1. **Add INVENTORY_DIR constant** near the top of tf_handlers.py where other directory constants are defined (around line 20-30, near SHOP_DRAWINGS_DIR):
```python
INVENTORY_DIR = os.path.join(BASE_DIR, "data")
```

2. **Add imports** near top where other inventory imports are:
```python
from shop_drawings.inventory import (
    load_inventory, save_inventory, get_all_coils, get_coil, add_coil, update_coil, delete_coil,
    receive_stock, adjust_stock, consume_stock, get_transactions, allocate_stock, get_allocations,
    get_alerts, acknowledge_alert, generate_alerts, get_mill_certs, add_mill_cert,
    get_inventory_summary, get_coil_history, get_stock_valuation,
    create_purchase_order, list_purchase_orders, receive_against_po,
    get_coil_qr_data, generate_coil_sticker_zpl
)
from templates.inventory_dashboard_page import get_inventory_dashboard_html
```

3. **Copy ALL handler classes** from `tf_handlers_inventory_patch.py` and paste them AFTER the existing inventory handlers (~after line 1103). The 26 handler classes are:
   - `InventoryDashboardPageHandler` — serves the new dashboard page
   - `CoilListAPIHandler` / `CoilCreateAPIHandler`
   - `CoilDetailAPIHandler` / `CoilUpdateAPIHandler` / `CoilDeleteAPIHandler`
   - `ReceiveStockAPIHandler` / `AdjustStockAPIHandler` / `ConsumeStockAPIHandler`
   - `TransactionListAPIHandler`
   - `AllocateStockAPIHandler` / `AllocationListAPIHandler`
   - `AlertListAPIHandler` / `AlertAcknowledgeAPIHandler` / `GenerateAlertsAPIHandler`
   - `MillCertListAPIHandler` / `MillCertAddAPIHandler`
   - `InventorySummaryAPIHandler` / `CoilHistoryAPIHandler` / `StockValuationAPIHandler`
   - `PurchaseOrderListAPIHandler` / `PurchaseOrderCreateAPIHandler` / `ReceiveAgainstPOAPIHandler`
   - `CoilQRDataAPIHandler` / `CoilStickerZPLAPIHandler`
   - `ReceivingHistoryAPIHandler`

4. **Add these routes** to `get_routes()` function at the bottom of tf_handlers.py:
```python
# Inventory Dashboard (new full page)
(r"/inventory-dashboard", InventoryDashboardPageHandler),

# Inventory API v2 — Coil CRUD
(r"/api/v2/inventory/coils", CoilListAPIHandler),
(r"/api/v2/inventory/coils/create", CoilCreateAPIHandler),
(r"/api/v2/inventory/coils/([^/]+)", CoilDetailAPIHandler),
(r"/api/v2/inventory/coils/([^/]+)/update", CoilUpdateAPIHandler),
(r"/api/v2/inventory/coils/([^/]+)/delete", CoilDeleteAPIHandler),

# Inventory API v2 — Stock Operations
(r"/api/v2/inventory/receive", ReceiveStockAPIHandler),
(r"/api/v2/inventory/adjust", AdjustStockAPIHandler),
(r"/api/v2/inventory/consume", ConsumeStockAPIHandler),
(r"/api/v2/inventory/transactions", TransactionListAPIHandler),

# Inventory API v2 — Allocations
(r"/api/v2/inventory/allocate", AllocateStockAPIHandler),
(r"/api/v2/inventory/allocations", AllocationListAPIHandler),

# Inventory API v2 — Alerts
(r"/api/v2/inventory/alerts", AlertListAPIHandler),
(r"/api/v2/inventory/alerts/acknowledge", AlertAcknowledgeAPIHandler),
(r"/api/v2/inventory/alerts/generate", GenerateAlertsAPIHandler),

# Inventory API v2 — Mill Certs
(r"/api/v2/inventory/mill-certs", MillCertListAPIHandler),
(r"/api/v2/inventory/mill-certs/add", MillCertAddAPIHandler),

# Inventory API v2 — Reports
(r"/api/v2/inventory/summary", InventorySummaryAPIHandler),
(r"/api/v2/inventory/coils/([^/]+)/history", CoilHistoryAPIHandler),
(r"/api/v2/inventory/valuation", StockValuationAPIHandler),

# Inventory API v2 — Purchase Orders
(r"/api/v2/inventory/purchase-orders", PurchaseOrderListAPIHandler),
(r"/api/v2/inventory/purchase-orders/create", PurchaseOrderCreateAPIHandler),
(r"/api/v2/inventory/purchase-orders/receive", ReceiveAgainstPOAPIHandler),

# Inventory API v2 — QR & Stickers
(r"/api/v2/inventory/coils/([^/]+)/qr", CoilQRDataAPIHandler),
(r"/api/v2/inventory/coils/([^/]+)/sticker-zpl", CoilStickerZPLAPIHandler),

# Inventory API v2 — Receiving History
(r"/api/v2/inventory/receiving-history", ReceivingHistoryAPIHandler),
```

### 4. Hook Auto-Deduct into QR Scan Start
**File**: `combined_calc/shop_drawings/work_orders.py`

In the `qr_scan_start()` function (around line 450-491), add the auto-deduct call after the item status is set to IN_PROGRESS:

```python
# After: item.status = STATUS_IN_PROGRESS
# Add:
try:
    from shop_drawings.inventory import auto_deduct_for_fabrication
    auto_deduct_for_fabrication(
        coil_type=None,  # auto-detected from component_type
        component_type=item.component_type,
        quantity=item.quantity,
        job_code=wo.job_code,
        work_order_id=wo.work_order_id,
        item_id=item.item_id
    )
except ImportError:
    pass  # Inventory module not available
except Exception as e:
    import logging
    logging.warning(f"Auto-deduct failed for {item.item_id}: {e}")
```

## API Endpoints Added

| Method | Endpoint | Purpose |
|--------|---------|---------|
| GET | `/inventory-dashboard` | Full inventory dashboard page |
| GET | `/api/v2/inventory/coils` | List all coils |
| POST | `/api/v2/inventory/coils/create` | Add new coil |
| GET | `/api/v2/inventory/coils/:id` | Get coil details |
| POST | `/api/v2/inventory/coils/:id/update` | Update coil |
| POST | `/api/v2/inventory/coils/:id/delete` | Delete coil |
| POST | `/api/v2/inventory/receive` | Receive stock (standalone) |
| POST | `/api/v2/inventory/adjust` | Manual stock adjustment |
| POST | `/api/v2/inventory/consume` | Consume stock for fabrication |
| GET | `/api/v2/inventory/transactions` | Transaction history |
| POST | `/api/v2/inventory/allocate` | Allocate stock to job |
| GET | `/api/v2/inventory/allocations` | List allocations |
| GET | `/api/v2/inventory/alerts` | Active alerts |
| POST | `/api/v2/inventory/alerts/acknowledge` | Acknowledge alert |
| POST | `/api/v2/inventory/alerts/generate` | Regenerate alerts |
| GET | `/api/v2/inventory/mill-certs` | Mill cert list |
| POST | `/api/v2/inventory/mill-certs/add` | Add mill cert |
| GET | `/api/v2/inventory/summary` | Inventory summary stats |
| GET | `/api/v2/inventory/coils/:id/history` | Coil transaction history |
| GET | `/api/v2/inventory/valuation` | Stock valuation report |
| GET | `/api/v2/inventory/purchase-orders` | List POs |
| POST | `/api/v2/inventory/purchase-orders/create` | Create PO |
| POST | `/api/v2/inventory/purchase-orders/receive` | Receive against PO |
| GET | `/api/v2/inventory/coils/:id/qr` | QR code data for coil |
| GET | `/api/v2/inventory/coils/:id/sticker-zpl` | ZPL sticker for Zebra ZT411 |
| GET | `/api/v2/inventory/receiving-history` | Receiving log |

## Coil QR Code Flow
1. Scan QR on coil sticker → opens `/api/v2/inventory/coils/:id/qr`
2. Returns: coil details, current stock, mill cert links, job assignments
3. If coil is allocated to a job, shows job code and work order info
4. Mill cert viewer accessible via linked URL

## Testing
1. Navigate to `/inventory-dashboard`
2. Click "Add New Coil" → modal should appear (BUG-001 fix)
3. Fill in coil details → Submit → coil appears in table
4. Click QR icon on a coil → should return QR data with mill cert links
5. Click ZPL icon → should generate Zebra ZT411-compatible sticker
6. Test receiving: click "Receive Stock" → enter weight → verify stock updates
7. Test PO workflow: Create PO → Submit → Receive against PO
8. Go to Work Orders → Start an item via QR scan → verify inventory auto-deducts
9. Check Alerts tab → should show low-stock warnings for any coils below minimum
