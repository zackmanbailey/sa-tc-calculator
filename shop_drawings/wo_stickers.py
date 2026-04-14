"""
TitanForge — Work Order QR Sticker Generator
=============================================
Generates 4"x6" stickers for fabrication tracking.
BLACK & WHITE ONLY — designed for Industrial Thermal Transfer
Ribbon (Wax/Resin) printers (e.g. Zebra ZT411).

Each sticker has TWO QR codes:
  1. Work Order QR — links to the WO scan endpoint (start/finish tracking)
  2. Shop Drawing QR — links directly to the shop drawing for this part

Output formats:
  - PDF: One sticker per page, 4"×6", monochrome
  - ZPL: Raw ZPL commands for direct Zebra printer communication
  - CSV: Data export for third-party label systems

Sticker layout (4" x 6"):
  ┌──────────────────────────────────────────┐
  │ ▓▓ TITANFORGE WORK ORDER ▓▓▓▓▓▓▓▓▓▓▓▓  │  ← black header
  │──────────────────────────────────────────│
  │                                          │
  │      ██  C1  ──  COLUMN  ██              │  ← LARGE ship mark + type
  │                                          │
  │  WHAT: Column C1 — 14x4x10GA            │
  │        box beam, 19'-6 3/8" tall         │
  │                                          │
  │  ┌─────┐              ┌─────┐            │
  │  │ WO  │  JOB: SA2401 │DRAW │            │
  │  │ QR  │  QTY: 4      │ QR  │            │
  │  │CODE │  MCH: WELD   │CODE │            │
  │  └─────┘              └─────┘            │
  │  SCAN TO              VIEW SHOP          │
  │  START/FINISH         DRAWING            │
  │──────────────────────────────────────────│
  │  WO: WO-SA2401-A-3F1C  Rev: A           │
  │  START:_________ FINISH:__________       │
  │  ═══════════════════════════════════════  │
  │  Structures America | Conroe TX          │
  └──────────────────────────────────────────┘
"""

import io
import csv
import math
import datetime
from typing import List, Dict, Optional

from reportlab.lib.units import inch
from reportlab.lib.colors import black, white
from reportlab.pdfgen.canvas import Canvas
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics import renderPDF


# ─────────────────────────────────────────────
# CONSTANTS — BLACK & WHITE ONLY
# ─────────────────────────────────────────────

W = 4.0 * inch   # Sticker width
H = 6.0 * inch   # Sticker height
M = 0.15 * inch   # Margin

BLACK = black
WHITE = white
LIGHT_GRAY = black  # For thermal: everything prints as black


# ─────────────────────────────────────────────
# QR CODE DRAWING
# ─────────────────────────────────────────────

def _qr_drawing(data: str, size_pts: float) -> Drawing:
    """Generate a ReportLab QR code Drawing (black on white)."""
    qr = QrCodeWidget(data)
    qr.barFillColor = black
    qr.barStrokeColor = black
    bounds = qr.getBounds()
    qr_w = bounds[2] - bounds[0]
    qr_h = bounds[3] - bounds[1]
    scale = size_pts / max(qr_w, qr_h)
    d = Drawing(size_pts, size_pts)
    d.transform = (scale, 0, 0, scale, 0, 0)
    d.add(qr)
    return d


# ─────────────────────────────────────────────
# SHOP DRAWING URL BUILDER
# ─────────────────────────────────────────────

def _shop_drawing_url(app_base_url: str, job_code: str, item: dict) -> str:
    """
    Build the URL that links to the shop drawing for a specific part.
    Routes:
      - column  → /shop-drawings/{job_code}/column
      - rafter  → /shop-drawings/{job_code}/rafter
      - other   → /shop-drawings/{job_code} (dashboard with file list)
    """
    comp = item.get("component_type", "").lower()
    base = f"{app_base_url}/shop-drawings/{job_code}"
    if comp == "column":
        return f"{base}/column"
    elif comp == "rafter":
        return f"{base}/rafter"
    else:
        # For purlins, sag rods, straps, endcaps — link to drawing dashboard
        # with the drawing_ref as a hint
        drawing_ref = item.get("drawing_ref", "")
        if drawing_ref:
            return f"{app_base_url}/api/shop-drawings/file?job_code={job_code}&filename={drawing_ref}"
        return base


# ─────────────────────────────────────────────
# SINGLE STICKER RENDERER — BLACK & WHITE
# ─────────────────────────────────────────────

def _draw_wo_sticker(c: Canvas, item: dict, wo_info: dict,
                     app_base_url: str = "http://localhost:8888"):
    """
    Draw a single work order QR sticker — BLACK & WHITE ONLY.

    item keys: item_id, ship_mark, component_type, description,
               quantity, machine, drawing_ref, status
    wo_info keys: work_order_id, job_code, revision
    """
    job_code = wo_info.get("job_code", "")
    wo_id = wo_info.get("work_order_id", "")
    revision = wo_info.get("revision", "-")
    item_id = item.get("item_id", "")
    mark = item.get("ship_mark", "???")
    comp_type = item.get("component_type", "")
    desc = item.get("description", "")
    qty = item.get("quantity", 1)
    machine = item.get("machine", "")
    drawing_ref = item.get("drawing_ref", "")
    print_date = datetime.date.today().strftime("%m/%d/%Y")

    # QR data URLs
    wo_qr_data = f"{app_base_url}/work-orders/{job_code}?scan={item_id}"
    drawing_qr_data = _shop_drawing_url(app_base_url, job_code, item)

    c.setPageSize((W, H))

    # ── Black header bar ──
    hdr_h = 0.50 * inch
    c.setFillColor(BLACK)
    c.rect(0, H - hdr_h, W, hdr_h, fill=1, stroke=0)

    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(M + 0.04 * inch, H - hdr_h + 0.20 * inch, "TITANFORGE")
    c.setFont("Helvetica-Bold", 8)
    c.drawString(M + 0.04 * inch, H - hdr_h + 0.06 * inch, "WORK ORDER")

    c.setFont("Helvetica-Bold", 7)
    c.drawRightString(W - M, H - hdr_h + 0.20 * inch, print_date)
    c.setFont("Helvetica", 6)
    c.drawRightString(W - M, H - hdr_h + 0.06 * inch, f"Rev {revision}")

    # ── Thick divider ──
    y = H - hdr_h
    c.setStrokeColor(BLACK)
    c.setLineWidth(2)
    c.line(0, y, W, y)

    # ══════════════════════════════════════════════
    # PART IDENTIFICATION — THE MAIN EVENT
    # ══════════════════════════════════════════════

    # Ship mark — HUGE, centered, unmissable
    y -= 0.12 * inch
    c.setFillColor(BLACK)
    c.setFont("Helvetica-Bold", 42)
    mark_display = mark.upper()
    c.drawCentredString(W / 2, y - 0.42 * inch, mark_display)

    # Component type — large, right under the mark
    y -= 0.50 * inch
    comp_display = comp_type.upper().replace("_", " ")
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(W / 2, y - 0.18 * inch, comp_display)

    # Black rule under the part ID section
    y -= 0.30 * inch
    c.setLineWidth(1.5)
    c.line(M, y, W - M, y)

    # ══════════════════════════════════════════════
    # DESCRIPTION — "WHAT ARE WE MAKING?"
    # ══════════════════════════════════════════════

    y -= 0.06 * inch
    c.setFont("Helvetica-Bold", 8)
    c.drawString(M, y - 0.12 * inch, "FABRICATE:")

    # Break description into lines that fit
    c.setFont("Helvetica-Bold", 9)
    max_chars = 38
    desc_lines = []
    if len(desc) <= max_chars:
        desc_lines = [desc]
    else:
        # Word-wrap
        words = desc.split()
        line = ""
        for word in words:
            test = (line + " " + word).strip()
            if len(test) <= max_chars:
                line = test
            else:
                if line:
                    desc_lines.append(line)
                line = word
        if line:
            desc_lines.append(line)

    desc_y = y - 0.28 * inch
    for dl in desc_lines[:3]:  # Max 3 lines
        c.drawString(M + 0.08 * inch, desc_y, dl)
        desc_y -= 0.16 * inch

    # ── Thin rule ──
    y = desc_y - 0.04 * inch
    c.setLineWidth(0.5)
    c.line(M, y, W - M, y)

    # ══════════════════════════════════════════════
    # TWO QR CODES + JOB INFO
    # ══════════════════════════════════════════════

    qr_size = 1.15 * inch
    qr_row_y = y - 0.08 * inch

    # ── Left QR: Work Order scan ──
    qr1_x = M + 0.05 * inch
    qr1_y = qr_row_y - qr_size
    try:
        qr_wo = _qr_drawing(wo_qr_data, qr_size)
        renderPDF.draw(qr_wo, c, qr1_x, qr1_y)
    except Exception:
        c.setStrokeColor(BLACK)
        c.setLineWidth(0.5)
        c.rect(qr1_x, qr1_y, qr_size, qr_size)
        c.setFont("Helvetica", 6)
        c.setFillColor(BLACK)
        c.drawCentredString(qr1_x + qr_size / 2, qr1_y + qr_size / 2, "QR ERROR")

    # Label under left QR
    c.setFont("Helvetica-Bold", 6)
    c.setFillColor(BLACK)
    c.drawCentredString(qr1_x + qr_size / 2, qr1_y - 10, "SCAN: START / FINISH")

    # ── Right QR: Shop Drawing ──
    qr2_x = W - M - qr_size - 0.05 * inch
    qr2_y = qr1_y
    try:
        qr_dwg = _qr_drawing(drawing_qr_data, qr_size)
        renderPDF.draw(qr_dwg, c, qr2_x, qr2_y)
    except Exception:
        c.setStrokeColor(BLACK)
        c.setLineWidth(0.5)
        c.rect(qr2_x, qr2_y, qr_size, qr_size)
        c.setFont("Helvetica", 6)
        c.setFillColor(BLACK)
        c.drawCentredString(qr2_x + qr_size / 2, qr2_y + qr_size / 2, "QR ERROR")

    # Label under right QR
    c.setFont("Helvetica-Bold", 6)
    c.drawCentredString(qr2_x + qr_size / 2, qr2_y - 10, "VIEW SHOP DRAWING")

    # ── Center column: Job info between the QR codes ──
    info_x = W / 2
    info_y = qr_row_y - 0.10 * inch

    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(info_x, info_y, "JOB")
    c.setFont("Courier-Bold", 12)
    info_y -= 0.18 * inch
    job_display = job_code[:10] if len(job_code) > 10 else job_code
    c.drawCentredString(info_x, info_y, job_display)

    info_y -= 0.24 * inch
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(info_x, info_y, "QTY")
    c.setFont("Courier-Bold", 16)
    info_y -= 0.22 * inch
    c.drawCentredString(info_x, info_y, str(qty))

    info_y -= 0.22 * inch
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(info_x, info_y, "MACHINE")
    c.setFont("Courier-Bold", 10)
    info_y -= 0.16 * inch
    mach_display = machine[:8] if len(machine) > 8 else machine
    c.drawCentredString(info_x, info_y, mach_display)

    # ── Divider above WO info ──
    wo_info_y = qr1_y - 0.22 * inch
    c.setLineWidth(1)
    c.line(M, wo_info_y, W - M, wo_info_y)

    # ══════════════════════════════════════════════
    # WORK ORDER REFERENCE + START/FINISH
    # ══════════════════════════════════════════════

    wo_info_y -= 0.14 * inch
    c.setFont("Helvetica-Bold", 6.5)
    c.drawString(M, wo_info_y, "WO:")
    c.setFont("Courier-Bold", 6.5)
    wo_display = wo_id if len(wo_id) <= 28 else wo_id[:28]
    c.drawString(M + 0.28 * inch, wo_info_y, wo_display)

    c.setFont("Helvetica-Bold", 6.5)
    c.drawRightString(W - M, wo_info_y, f"Rev {revision}")

    wo_info_y -= 0.14 * inch
    c.setFont("Helvetica", 6)
    c.drawString(M, wo_info_y, f"Drawing: {drawing_ref}")

    # Start / Finish fields
    wo_info_y -= 0.22 * inch
    c.setFont("Helvetica-Bold", 7)
    c.drawString(M, wo_info_y, "START:")
    c.setLineWidth(0.5)
    c.line(M + 0.45 * inch, wo_info_y - 1, W / 2 - 0.08 * inch, wo_info_y - 1)

    c.drawString(W / 2 + 0.05 * inch, wo_info_y, "FINISH:")
    c.line(W / 2 + 0.52 * inch, wo_info_y - 1, W - M, wo_info_y - 1)

    # ── Footer bar ──
    foot_h = 0.20 * inch
    c.setFillColor(BLACK)
    c.rect(0, 0, W, foot_h, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 5)
    c.drawCentredString(W / 2, 0.06 * inch,
                        "Structures America | 14369 FM 1314, Conroe TX 77302 | TitanForge")


# ─────────────────────────────────────────────
# PDF GENERATOR
# ─────────────────────────────────────────────

def generate_wo_sticker_pdf(
    wo_dict: dict,
    items: Optional[List[dict]] = None,
    app_base_url: str = "http://localhost:8888",
) -> bytes:
    """
    Generate a PDF with one 4x6" sticker per page for work order items.
    Pure black & white for thermal transfer printing.

    Args:
        wo_dict: Work order dict (work_order_id, job_code, revision, items)
        items: Optional subset of items. If None, generates for all items.
        app_base_url: Base URL for QR code links

    Returns:
        PDF bytes
    """
    buf = io.BytesIO()
    c = Canvas(buf, pagesize=(W, H))

    wo_info = {
        "work_order_id": wo_dict.get("work_order_id", ""),
        "job_code": wo_dict.get("job_code", ""),
        "revision": wo_dict.get("revision", "-"),
    }

    target_items = items or wo_dict.get("items", [])

    for item in target_items:
        _draw_wo_sticker(c, item, wo_info, app_base_url)
        c.showPage()

    c.save()
    return buf.getvalue()


# ─────────────────────────────────────────────
# ZPL GENERATOR (Zebra ZT411, 203 DPI)
# BLACK & WHITE — native thermal transfer
# ─────────────────────────────────────────────

def generate_wo_sticker_zpl(
    wo_dict: dict,
    items: Optional[List[dict]] = None,
    app_base_url: str = "http://localhost:8888",
) -> str:
    """
    Generate ZPL commands for work order stickers.
    4"x6" label at 203 DPI = 812 x 1218 dots.
    Pure black & white with dual QR codes.
    """
    label_w = 812
    label_h = 1218

    wo_id = wo_dict.get("work_order_id", "")
    job_code = wo_dict.get("job_code", "")
    revision = wo_dict.get("revision", "-")
    target_items = items or wo_dict.get("items", [])

    zpl_parts = []

    for item in target_items:
        item_id = item.get("item_id", "")
        mark = item.get("ship_mark", "???")
        comp_type = item.get("component_type", "").upper().replace("_", " ")
        desc = item.get("description", "")[:50]
        qty = str(item.get("quantity", 1))
        machine = item.get("machine", "")
        drawing_ref = item.get("drawing_ref", "")
        wo_qr_data = f"{app_base_url}/work-orders/{job_code}?scan={item_id}"
        drawing_qr_data = _shop_drawing_url(app_base_url, job_code, item)
        print_date = datetime.date.today().strftime("%m/%d/%Y")

        zpl = []
        zpl.append("^XA")
        zpl.append(f"^PW{label_w}")
        zpl.append(f"^LL{label_h}")

        # Black header bar
        zpl.append("^FO0,0^GB812,80,80,,^FS")
        zpl.append("^FO20,15^A0N,30,30^FR^FDTITANFORGE^FS")
        zpl.append("^FO20,50^A0N,20,20^FR^FDWORK ORDER^FS")
        zpl.append(f"^FO580,15^A0N,22,22^FR^FD{print_date}^FS")
        zpl.append(f"^FO650,50^A0N,18,18^FR^FDRev {revision}^FS")

        # Thick divider
        zpl.append("^FO0,82^GB812,4,4,,^FS")

        # Ship mark — LARGE centered
        mark_x = (label_w - len(mark) * 40) // 2
        zpl.append(f"^FO{mark_x},100^A0N,80,80^FD{mark}^FS")

        # Component type — centered
        type_x = (label_w - len(comp_type) * 18) // 2
        zpl.append(f"^FO{type_x},190^A0N,32,32^FD{comp_type}^FS")

        # Rule
        zpl.append("^FO20,230^GB772,2,2,,^FS")

        # FABRICATE: description
        zpl.append("^FO30,245^A0N,20,20^FDFABRICATE:^FS")
        zpl.append(f"^FO30,275^A0N,24,24^FD{desc}^FS")

        # Rule
        zpl.append("^FO20,310^GB772,1,1,,^FS")

        # Left QR: Work Order scan
        zpl.append(f"^FO30,330^BQN,2,5^FDMM,{wo_qr_data}^FS")

        # Right QR: Shop Drawing
        zpl.append(f"^FO560,330^BQN,2,5^FDMM,{drawing_qr_data}^FS")

        # Center info between QRs
        zpl.append(f"^FO320,340^A0N,18,18^FDJOB^FS")
        zpl.append(f"^FO290,365^A0N,32,32^FD{job_code}^FS")
        zpl.append(f"^FO320,410^A0N,18,18^FDQTY^FS")
        zpl.append(f"^FO330,435^A0N,40,40^FD{qty}^FS")
        zpl.append(f"^FO305,490^A0N,18,18^FDMACHINE^FS")
        zpl.append(f"^FO310,515^A0N,28,28^FD{machine}^FS")

        # QR labels
        zpl.append("^FO40,580^A0N,16,16^FDSCAN: START/FINISH^FS")
        zpl.append("^FO565,580^A0N,16,16^FDVIEW SHOP DRAWING^FS")

        # Divider
        zpl.append("^FO20,610^GB772,2,2,,^FS")

        # WO info
        zpl.append(f"^FO30,625^A0N,18,18^FDWO: {wo_id[:28]}^FS")
        zpl.append(f"^FO600,625^A0N,18,18^FDRev {revision}^FS")
        zpl.append(f"^FO30,650^A0N,16,16^FDDrawing: {drawing_ref}^FS")

        # Start/Finish
        zpl.append("^FO30,690^A0N,20,20^FDSTART: _______________^FS")
        zpl.append("^FO430,690^A0N,20,20^FDFINISH: ______________^FS")

        # Footer bar
        zpl.append(f"^FO0,{label_h - 35}^GB812,35,35,,^FS")
        zpl.append(f"^FO130,{label_h - 25}^A0N,16,16^FR^FDStructures America | Conroe TX | TitanForge^FS")

        zpl.append("^XZ")
        zpl_parts.append("\n".join(zpl))

    return "\n\n".join(zpl_parts)


# ─────────────────────────────────────────────
# CSV EXPORT
# ─────────────────────────────────────────────

def generate_wo_sticker_csv(
    wo_dict: dict,
    items: Optional[List[dict]] = None,
    app_base_url: str = "http://localhost:8888",
) -> bytes:
    """
    Generate a CSV export of work order sticker data.
    Compatible with BarTender, NiceLabel, or any label printing software.
    Now includes shop drawing URL column.
    """
    wo_id = wo_dict.get("work_order_id", "")
    job_code = wo_dict.get("job_code", "")
    revision = wo_dict.get("revision", "-")
    target_items = items or wo_dict.get("items", [])

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "item_id", "ship_mark", "component_type", "description",
        "quantity", "machine", "drawing_ref", "work_order_id",
        "job_code", "revision", "wo_qr_url", "drawing_qr_url",
    ])

    for item in target_items:
        item_id = item.get("item_id", "")
        wo_qr_url = f"{app_base_url}/work-orders/{job_code}?scan={item_id}"
        drawing_qr_url = _shop_drawing_url(app_base_url, job_code, item)
        writer.writerow([
            item_id,
            item.get("ship_mark", ""),
            item.get("component_type", ""),
            item.get("description", ""),
            item.get("quantity", 1),
            item.get("machine", ""),
            item.get("drawing_ref", ""),
            wo_id,
            job_code,
            revision,
            wo_qr_url,
            drawing_qr_url,
        ])

    return buf.getvalue().encode("utf-8")
