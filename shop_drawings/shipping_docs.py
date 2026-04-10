"""
TitanForge — Document Generation Pipeline for Shipping & Procurement
=====================================================================
Generates packing lists, bills of lading, shipping manifests, and purchase orders
for metal building fabrication projects. All data is JSON-serializable dicts for
template rendering and archival.

Key functions:
  - generate_packing_list(job_code, work_order_dict, ...) → packing list dict
  - generate_bill_of_lading(job_code, work_order_dict, ...) → BOL dict
  - generate_shipping_manifest(job_code, loads) → manifest dict
  - generate_purchase_order(po_number, vendor, line_items, ...) → PO dict
  - check_reorder_points(inventory_data, reorder_config) → list of low-stock items
  - save_shipping_doc(base_dir, job_code, doc_type, doc_data) → file path
  - load_shipping_docs(base_dir, job_code, doc_type) → list of docs
"""

import os
import json
import datetime
import uuid
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field, asdict


# ─────────────────────────────────────────────
# COMPONENT WEIGHTS (pounds per unit)
# ─────────────────────────────────────────────

COMPONENT_WEIGHTS = {
    "column": 850,
    "rafter": 650,
    "purlin": 45,
    "sag_rod": 15,
    "clip": 5,
    "panel": 85,
    "trim": 12,
    "strap": 2,
    "endcap": 120,
    "roofing": 95,
}


# ─────────────────────────────────────────────
# PACKING LIST GENERATION
# ─────────────────────────────────────────────

def generate_packing_list(
    job_code: str,
    work_order_dict: dict,
    items_filter: Optional[List[str]] = None,
    ship_date: Optional[str] = None,
    truck_info: Optional[dict] = None,
) -> dict:
    """
    Generate a packing list from a work order.

    Args:
        job_code: Project code
        work_order_dict: WorkOrder.to_dict() result
        items_filter: List of item_ids to include; if None, include all completed items
        ship_date: ISO date string; if None, use today
        truck_info: Dict with truck_number, trailer_number, driver_name (optional)

    Returns:
        Dict with packing list structure ready for template/printing
    """
    if ship_date is None:
        ship_date = datetime.date.today().isoformat()

    truck_info = truck_info or {}

    # Filter items: completed or in filter list
    items = work_order_dict.get("items", [])
    if items_filter:
        items = [i for i in items if i.get("item_id") in items_filter]
    else:
        items = [i for i in items if i.get("status") == "complete"]

    # Group items by component_type
    grouped = {}
    for item in items:
        comp_type = item.get("component_type", "unknown")
        if comp_type not in grouped:
            grouped[comp_type] = []
        grouped[comp_type].append(item)

    # Build line items with weight calculations
    line_items = []
    total_pieces = 0
    total_weight_lbs = 0.0
    total_bundles = 0

    for comp_type, type_items in sorted(grouped.items()):
        weight_per_unit = COMPONENT_WEIGHTS.get(comp_type, 50)
        for item in type_items:
            qty = item.get("quantity", 1)
            item_weight = qty * weight_per_unit
            # Estimate bundles: typical bundle = 10 pieces for sag rods, straps, etc.
            bundle_count = max(1, -(-qty // 10)) if comp_type in ["sag_rod", "strap", "clip"] else 1

            line_items.append({
                "ship_mark": item.get("ship_mark", ""),
                "component_type": comp_type,
                "description": item.get("description", ""),
                "quantity": qty,
                "weight_lbs": round(item_weight, 1),
                "bundle_count": bundle_count,
            })

            total_pieces += qty
            total_weight_lbs += item_weight
            total_bundles += bundle_count

    packing_list = {
        "packing_list_id": f"PL-{job_code}-{uuid.uuid4().hex[:6].upper()}",
        "job_code": job_code,
        "ship_date": ship_date,
        "items": line_items,
        "totals": {
            "total_pieces": total_pieces,
            "total_weight_lbs": round(total_weight_lbs, 1),
            "total_bundles": total_bundles,
        },
        "signatures": {
            "prepared_by": "",
            "prepared_date": "",
            "loaded_by": "",
            "loaded_date": "",
            "received_by": "",
            "received_date": "",
        },
        "truck_info": {
            "truck_number": truck_info.get("truck_number", ""),
            "trailer_number": truck_info.get("trailer_number", ""),
            "driver_name": truck_info.get("driver_name", ""),
        },
    }

    return packing_list


# ─────────────────────────────────────────────
# BILL OF LADING GENERATION
# ─────────────────────────────────────────────

def generate_bill_of_lading(
    job_code: str,
    work_order_dict: dict,
    carrier_info: Optional[dict] = None,
    consignee: Optional[dict] = None,
) -> dict:
    """
    Generate a bill of lading for shipment of fabricated components.

    Args:
        job_code: Project code
        work_order_dict: WorkOrder.to_dict()
        carrier_info: Dict with carrier_name, driver, truck_number, trailer_number
        consignee: Dict with name, address, city, state, zip, phone, contact

    Returns:
        Dict with BOL structure (NMFC codes, freight class, etc.)
    """
    carrier_info = carrier_info or {}
    consignee = consignee or {}

    # Shipper: Structures America
    shipper = {
        "company": "Structures America",
        "address": "710 Honea Egypt Rd",
        "city": "Conroe",
        "state": "TX",
        "zip": "77385",
        "phone": "",
        "contact": "Shop",
    }

    # Consignee details (fallback to shipper if not provided)
    if not consignee:
        consignee = shipper.copy()

    consignee.setdefault("company", "")
    consignee.setdefault("address", "")
    consignee.setdefault("city", "")
    consignee.setdefault("state", "")
    consignee.setdefault("zip", "")
    consignee.setdefault("phone", "")
    consignee.setdefault("contact", "")

    # Generate BOL number: BOL-YYYYMMDD-NNNNN
    now = datetime.datetime.now()
    bol_suffix = uuid.uuid4().hex[:5].upper()
    bol_number = f"BOL-{now.strftime('%Y%m%d')}-{bol_suffix}"

    # Process items into freight items (grouped by type)
    items = work_order_dict.get("items", [])
    completed_items = [i for i in items if i.get("status") == "complete"]

    freight_items = []
    total_weight = 0.0
    total_pieces = 0

    # Group by component type
    grouped = {}
    for item in completed_items:
        comp_type = item.get("component_type", "unknown")
        if comp_type not in grouped:
            grouped[comp_type] = []
        grouped[comp_type].append(item)

    for comp_type, type_items in sorted(grouped.items()):
        weight_per_unit = COMPONENT_WEIGHTS.get(comp_type, 50)
        qty_total = sum(i.get("quantity", 1) for i in type_items)
        weight_total = qty_total * weight_per_unit

        freight_items.append({
            "description": f"{comp_type.title()} Components",
            "nmfc_code": "48620",  # Structural steel
            "weight_lbs": round(weight_total, 1),
            "piece_count": qty_total,
            "freight_class": 65,  # Structural steel class
        })

        total_weight += weight_total
        total_pieces += qty_total

    bol = {
        "bol_number": bol_number,
        "bol_date": datetime.date.today().isoformat(),
        "job_code": job_code,
        "shipper": shipper,
        "consignee": consignee,
        "carrier": {
            "name": carrier_info.get("carrier_name", ""),
            "driver": carrier_info.get("driver", ""),
            "truck_number": carrier_info.get("truck_number", ""),
            "trailer_number": carrier_info.get("trailer_number", ""),
        },
        "freight_items": freight_items,
        "totals": {
            "total_weight_lbs": round(total_weight, 1),
            "total_pieces": total_pieces,
            "freight_class": 65,
        },
        "special_instructions": "",
        "signatures": {
            "shipper_name": "",
            "shipper_title": "Shop Manager",
            "shipper_date": "",
            "carrier_name": "",
            "carrier_date": "",
            "consignee_name": "",
            "consignee_date": "",
        },
    }

    return bol


# ─────────────────────────────────────────────
# SHIPPING MANIFEST GENERATION
# ─────────────────────────────────────────────

def generate_shipping_manifest(
    job_code: str,
    loads: Optional[List[dict]] = None,
) -> dict:
    """
    Generate a shipping manifest for multiple truck loads.

    Args:
        job_code: Project code
        loads: List of load dicts, each with items, truck_number, trailer_number

    Returns:
        Dict with multi-load manifest with per-truck totals and loading sequence
    """
    loads = loads or []

    manifest_id = f"MANIFEST-{job_code}-{uuid.uuid4().hex[:6].upper()}"
    manifest_date = datetime.date.today().isoformat()

    processed_loads = []
    total_weight_all = 0.0
    total_pieces_all = 0

    for load_idx, load in enumerate(loads):
        items = load.get("items", [])
        weight_sum = 0.0
        piece_sum = 0

        for item in items:
            comp_type = item.get("component_type", "unknown")
            qty = item.get("quantity", 1)
            weight_per_unit = COMPONENT_WEIGHTS.get(comp_type, 50)
            weight_sum += qty * weight_per_unit
            piece_sum += qty

        processed_loads.append({
            "load_number": load_idx + 1,
            "truck_number": load.get("truck_number", ""),
            "trailer_number": load.get("trailer_number", ""),
            "weight_lbs": round(weight_sum, 1),
            "piece_count": piece_sum,
            "item_count": len(items),
            "items": items,
        })

        total_weight_all += weight_sum
        total_pieces_all += piece_sum

    # Sort by weight descending (heaviest first) for loading sequence
    processed_loads.sort(key=lambda x: x["weight_lbs"], reverse=True)

    manifest = {
        "manifest_id": manifest_id,
        "job_code": job_code,
        "manifest_date": manifest_date,
        "loads": processed_loads,
        "totals": {
            "total_loads": len(processed_loads),
            "total_weight_lbs": round(total_weight_all, 1),
            "total_pieces": total_pieces_all,
        },
        "loading_sequence": "Heaviest loads first (top of manifest)",
        "signatures": {
            "prepared_by": "",
            "prepared_date": "",
            "verified_by": "",
            "verified_date": "",
        },
    }

    return manifest


# ─────────────────────────────────────────────
# PURCHASE ORDER GENERATION
# ─────────────────────────────────────────────

def generate_purchase_order(
    po_number: Optional[str] = None,
    vendor: Optional[dict] = None,
    line_items: Optional[List[dict]] = None,
    delivery_date: Optional[str] = None,
    notes: Optional[str] = None,
) -> dict:
    """
    Generate a purchase order for material procurement.

    Args:
        po_number: PO number; if None, auto-generated as PO-YYYYMMDD-NNN
        vendor: Dict with name, address, city, state, zip, phone, contact
        line_items: List of dicts with description, gauge, width, weight_lbs, unit_price
        delivery_date: ISO date string for requested delivery
        notes: Special instructions

    Returns:
        Dict with PO structure including tax calculation
    """
    if po_number is None:
        now = datetime.datetime.now()
        po_suffix = uuid.uuid4().hex[:3].upper()
        po_number = f"PO-{now.strftime('%Y%m%d')}-{po_suffix}"

    if vendor is None:
        vendor = {}
    vendor.setdefault("name", "")
    vendor.setdefault("address", "")
    vendor.setdefault("city", "")
    vendor.setdefault("state", "")
    vendor.setdefault("zip", "")
    vendor.setdefault("phone", "")
    vendor.setdefault("contact", "")

    if delivery_date is None:
        # Default to 2 weeks out
        delivery_date = (datetime.date.today() + datetime.timedelta(days=14)).isoformat()

    line_items = line_items or []

    # Calculate totals
    subtotal = 0.0
    processed_items = []
    for item in line_items:
        unit_price = float(item.get("unit_price", 0.0))
        weight_lbs = float(item.get("weight_lbs", 0.0))
        total_price = weight_lbs * unit_price
        subtotal += total_price

        processed_items.append({
            "description": item.get("description", ""),
            "gauge": item.get("gauge", ""),
            "width": item.get("width", ""),
            "weight_lbs": round(weight_lbs, 2),
            "unit_price": round(unit_price, 4),
            "total": round(total_price, 2),
        })

    # Texas tax rate: 8.25%
    tax_rate = 0.0825
    tax_amount = subtotal * tax_rate
    total = subtotal + tax_amount

    po = {
        "po_number": po_number,
        "po_date": datetime.date.today().isoformat(),
        "delivery_date": delivery_date,
        "vendor": vendor,
        "ship_to": {
            "company": "Structures America",
            "address": "710 Honea Egypt Rd",
            "city": "Conroe",
            "state": "TX",
            "zip": "77385",
        },
        "line_items": processed_items,
        "financial": {
            "subtotal": round(subtotal, 2),
            "tax_rate": tax_rate,
            "tax_amount": round(tax_amount, 2),
            "total": round(total, 2),
        },
        "notes": notes or "",
        "authorized_by": "",
        "authorized_date": "",
    }

    return po


# ─────────────────────────────────────────────
# INVENTORY REORDER POINT CHECKING
# ─────────────────────────────────────────────

def check_reorder_points(
    inventory_data: dict,
    reorder_config: Optional[dict] = None,
) -> List[dict]:
    """
    Check inventory coils against reorder thresholds.

    Args:
        inventory_data: Full inventory dict from load_inventory()
        reorder_config: Dict with coil_id -> reorder_point_lbs mappings
                        If not provided, uses default 5000 lbs per coil

    Returns:
        List of items below threshold with reorder quantities
    """
    reorder_config = reorder_config or {}

    # Default reorder point: 5000 lbs per coil
    default_reorder_point = 5000

    coils = inventory_data.get("coils", {})
    below_threshold = []

    for coil_id, coil_data in coils.items():
        reorder_point = reorder_config.get(coil_id, default_reorder_point)
        stock_lbs = coil_data.get("stock_lbs", 0)
        committed_lbs = coil_data.get("committed_lbs", 0)
        available_lbs = stock_lbs - committed_lbs

        if available_lbs < reorder_point:
            # Suggest ordering enough to reach 80% of coil max
            coil_max = coil_data.get("coil_max_lbs", 8000)
            target_lbs = int(coil_max * 0.8)
            suggested_qty = max(coil_data.get("min_order_lbs", 2000), target_lbs - available_lbs)

            below_threshold.append({
                "coil_id": coil_id,
                "name": coil_data.get("name", ""),
                "gauge": coil_data.get("gauge", ""),
                "current_stock_lbs": stock_lbs,
                "committed_lbs": committed_lbs,
                "available_lbs": max(0, available_lbs),
                "reorder_point_lbs": reorder_point,
                "suggested_order_qty": suggested_qty,
                "min_order_lbs": coil_data.get("min_order_lbs", 2000),
                "price_per_lb": coil_data.get("price_per_lb", 0.0),
                "estimated_cost": round(suggested_qty * coil_data.get("price_per_lb", 0.0), 2),
                "lead_time_weeks": coil_data.get("lead_time_weeks", 8),
            })

    # Sort by urgency: lowest available stock first
    below_threshold.sort(key=lambda x: x["available_lbs"])

    return below_threshold


# ─────────────────────────────────────────────
# SHIPPING DOCUMENT STORAGE & RETRIEVAL
# ─────────────────────────────────────────────

def _shipping_doc_dir(base_dir: str, job_code: str) -> str:
    """Get shipping documents directory for a project."""
    import re
    safe = re.sub(r"[^a-zA-Z0-9_-]", "_", job_code)
    d = os.path.join(base_dir, "data", "shipping", safe)
    os.makedirs(d, exist_ok=True)
    return d


def save_shipping_doc(
    base_dir: str,
    job_code: str,
    doc_type: str,
    doc_data: dict,
) -> str:
    """
    Save a shipping document (packing list, BOL, manifest, PO, etc.) to disk.

    Args:
        base_dir: Base directory (containing data/ subdirectory)
        job_code: Project code
        doc_type: 'packing_list', 'bill_of_lading', 'shipping_manifest', 'purchase_order'
        doc_data: Document dict (result from generate_* function)

    Returns:
        Full path to saved file
    """
    d = _shipping_doc_dir(base_dir, job_code)

    # Use doc ID if present, otherwise create one
    doc_id = doc_data.get("packing_list_id") or \
             doc_data.get("bol_number") or \
             doc_data.get("manifest_id") or \
             doc_data.get("po_number") or \
             f"doc_{uuid.uuid4().hex[:8]}"

    filename = f"{doc_type}_{doc_id}.json"
    path = os.path.join(d, filename)

    with open(path, "w") as f:
        json.dump(doc_data, f, indent=2, default=str)

    return path


def load_shipping_docs(
    base_dir: str,
    job_code: str,
    doc_type: Optional[str] = None,
) -> List[dict]:
    """
    Load shipping documents for a project.

    Args:
        base_dir: Base directory
        job_code: Project code
        doc_type: Filter by type (e.g., 'packing_list'); if None, load all

    Returns:
        List of document dicts
    """
    d = _shipping_doc_dir(base_dir, job_code)
    results = []

    if not os.path.isdir(d):
        return results

    for fname in sorted(os.listdir(d), reverse=True):
        if not fname.endswith(".json"):
            continue

        # Filter by type if specified
        if doc_type and not fname.startswith(f"{doc_type}_"):
            continue

        try:
            with open(os.path.join(d, fname)) as f:
                doc = json.load(f)
            doc["_filename"] = fname
            results.append(doc)
        except Exception:
            continue

    return results
