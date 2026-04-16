"""
TitanForge — Work Order QR Sticker Generator
=============================================
Generates 4"x6" stickers with real QR codes for fabrication tracking.
Each sticker encodes the item_id for QR scan start/finish workflow.

Output formats:
  - PDF: One sticker per page, ready for thermal transfer printers (Zebra ZT411)
  - ZPL: Raw ZPL commands for direct Zebra printer communication
  - CSV: Data export for third-party label systems

Sticker layout (4" x 6"):
  ┌──────────────────────────────────────────┐
  │ TITANFORGE  WORK ORDER    [status badge] │  ← navy header
  │ ═══════════ gold accent ═══════════════  │
  │                                          │
  │  ┌─────┐   C1  COLUMN                   │
  │  │ QR  │   Column C1 — 14x4x10GA        │
  │  │CODE │   box beam                      │
  │  └─────┘                                 │
  │  ─────────────────────────────────────   │
  │  JOB CODE    QTY       MACHINE          │
  │  SA2401-A     1        WELDING           │
  │  ─────────────────────────────────────   │
  │  WO: WO-SA2401-A-3F1C2E                 │
  │  Rev: A  •  Drawing: SA2401_C1.pdf       │
  │                                          │
  │  [scan start]          [scan finish]     │
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
from reportlab.lib.colors import black, white, HexColor
from reportlab.pdfgen.canvas import Canvas
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics import renderPDF


# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────

W = 4.0 * inch   # Sticker width
H = 6.0 * inch   # Sticker height
M = 0.18 * inch   # Margin

# ── Thermal-transfer safe: black on white only ──
TF_NAVY = black
TF_BLUE = black
TF_GOLD = black
TF_GREEN = black
TF_AMBER = black
GRAY_LT = white
GRAY_MID = black
GRAY_DK = black
WHITE = white

# All component badges: black text, white fill (outlined)
COMPONENT_COLORS = {k: white for k in
    ("column", "rafter", "purlin", "sag_rod", "strap", "endcap", "roofing")}
COMPONENT_TEXT_COLORS = {k: black for k in COMPONENT_COLORS}


# ─────────────────────────────────────────────
# QR CODE DRAWING
# ─────────────────────────────────────────────

def _qr_drawing(data: str, size_pts: float) -> Drawing:
    """Generate a ReportLab QR code Drawing."""
    qr = QrCodeWidget(data)
    bounds = qr.getBounds()
    qr_w = bounds[2] - bounds[0]
    qr_h = bounds[3] - bounds[1]
    scale = size_pts / max(qr_w, qr_h)
    d = Drawing(size_pts, size_pts)
    d.transform = (scale, 0, 0, scale, 0, 0)
    d.add(qr)
    return d


# ─────────────────────────────────────────────
# SINGLE STICKER RENDERER
# ─────────────────────────────────────────────

def _draw_wo_sticker(c: Canvas, item: dict, wo_info: dict,
                     app_base_url: str = "http://localhost:8888"):
    """
    Draw a single work order QR sticker.

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
    desc = item.get("description", "")[:60]
    qty = item.get("quantity", 1)
    machine = item.get("machine", "")
    drawing_ref = item.get("drawing_ref", "")
    status = item.get("status", "queued")
    print_date = datetime.date.today().strftime("%m/%d/%Y")

    # QR data: direct link to mobile scan page for this specific item
    qr_data = f"{app_base_url}/wo/{job_code}/{item_id}"

    c.setPageSize((W, H))

    # ── Header bar (black outline, white fill) ──
    hdr_h = 0.58 * inch
    c.setStrokeColor(black)
    c.setLineWidth(1)
    c.rect(0, H - hdr_h, W, hdr_h, fill=0, stroke=1)

    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(M, H - hdr_h + 0.24 * inch, "TITANFORGE")
    c.setFont("Helvetica", 7)
    c.drawString(M, H - hdr_h + 0.08 * inch, "WORK ORDER STICKER")

    c.setFont("Helvetica-Bold", 7)
    c.drawRightString(W - M, H - hdr_h + 0.24 * inch, f"Printed: {print_date}")
    c.setFont("Helvetica", 6)
    c.drawRightString(W - M, H - hdr_h + 0.08 * inch, f"Rev {revision}")

    # ── Accent line ──
    c.setStrokeColor(black)
    c.setLineWidth(1.5)
    c.line(0, H - hdr_h - 2, W, H - hdr_h - 2)

    # ── Ship mark + component type (large) ──
    y = H - hdr_h - 0.08 * inch
    qr_size = 1.4 * inch
    text_x = M + qr_size + 0.15 * inch

    # QR Code (left side)
    qr_y = y - qr_size - 0.02 * inch
    try:
        qr_d = _qr_drawing(qr_data, qr_size)
        renderPDF.draw(qr_d, c, M, qr_y)
    except Exception:
        c.setStrokeColor(GRAY_MID)
        c.setLineWidth(0.5)
        c.rect(M, qr_y, qr_size, qr_size)
        c.setFont("Helvetica", 6)
        c.setFillColor(GRAY_MID)
        c.drawCentredString(M + qr_size / 2, qr_y + qr_size / 2, "QR ERROR")

    # "Scan to Start/Finish" under QR
    c.setFont("Helvetica-Bold", 5.5)
    c.setFillColor(TF_BLUE)
    c.drawCentredString(M + qr_size / 2, qr_y - 8, "SCAN TO START / FINISH")

    # Ship mark (large, right of QR)
    c.setFillColor(TF_NAVY)
    c.setFont("Helvetica-Bold", 28)
    c.drawString(text_x, y - 0.38 * inch, mark)

    # Component type badge (outlined, no fill)
    badge_text = comp_type.upper().replace("_", " ")
    badge_w = max(len(badge_text) * 5.5 + 12, 50)
    badge_x = text_x
    badge_y = y - 0.52 * inch
    c.setStrokeColor(black)
    c.setLineWidth(0.75)
    c.roundRect(badge_x, badge_y, badge_w, 14, 3, fill=0, stroke=1)
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(badge_x + 6, badge_y + 3, badge_text)

    # Description (under badge)
    c.setFillColor(GRAY_DK)
    c.setFont("Helvetica", 8)
    max_w = W - text_x - M
    max_chars = int(max_w / 4.5)
    if len(desc) > max_chars:
        line1 = desc[:max_chars]
        line2 = desc[max_chars:max_chars * 2]
        c.drawString(text_x, y - 0.72 * inch, line1)
        c.drawString(text_x, y - 0.86 * inch, line2)
    else:
        c.drawString(text_x, y - 0.72 * inch, desc)

    # ── Divider ──
    div_y = qr_y - 0.18 * inch
    c.setStrokeColor(TF_GOLD)
    c.setLineWidth(1)
    c.line(M, div_y, W - M, div_y)

    # ── Info grid (3 columns) ──
    grid_top = div_y - 0.10 * inch
    box_h = 0.50 * inch
    gap = 0.06 * inch  # gap between boxes
    num_cols = 3
    usable_w = W - 2 * M - (num_cols - 1) * gap
    box_w = usable_w / num_cols

    grid_data = [
        ("JOB CODE", job_code),
        ("QTY", str(qty)),
        ("MACHINE", machine),
    ]

    for i, (label, val) in enumerate(grid_data):
        bx = M + i * (box_w + gap)
        by = grid_top - box_h
        cx = bx + box_w / 2  # true center of box

        c.setStrokeColor(black)
        c.setLineWidth(0.5)
        c.rect(bx, by, box_w, box_h, fill=0, stroke=1)

        # Label in upper third
        c.setFont("Helvetica-Bold", 6.5)
        c.setFillColor(black)
        c.drawCentredString(cx, by + box_h - 14, label)

        # Divider line under label
        c.setLineWidth(0.3)
        c.line(bx + 3, by + box_h - 17, bx + box_w - 3, by + box_h - 17)

        # Value centered in lower two-thirds
        c.setFont("Helvetica-Bold", 11)
        display_val = val[:10] if len(val) > 10 else val
        c.drawCentredString(cx, by + (box_h - 17) / 2 - 4, display_val)

    grid_y = grid_top - box_h  # for positioning below

    # ── Work order info ──
    info_y = grid_y - 0.52 * inch
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(GRAY_MID)
    c.drawString(M, info_y, "WORK ORDER:")
    c.setFont("Courier-Bold", 7)
    c.setFillColor(black)
    wo_display = wo_id if len(wo_id) <= 30 else wo_id[:30]
    c.drawString(M + 0.75 * inch, info_y, wo_display)

    info_y -= 0.16 * inch
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(GRAY_MID)
    c.drawString(M, info_y, "ITEM ID:")
    c.setFont("Courier", 6)
    c.setFillColor(black)
    id_display = item_id if len(item_id) <= 36 else item_id[:36]
    c.drawString(M + 0.55 * inch, info_y, id_display)

    info_y -= 0.16 * inch
    c.setFont("Helvetica", 7)
    c.setFillColor(GRAY_MID)
    c.drawString(M, info_y, f"Drawing: {drawing_ref}")
    c.drawRightString(W - M, info_y, f"Rev {revision}")

    # ── Start/Finish fields (blank lines for manual use) ──
    info_y -= 0.28 * inch
    c.setStrokeColor(HexColor('#CCCCCC'))
    c.setLineWidth(0.5)

    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(black)
    c.drawString(M, info_y, "START:")
    c.setStrokeColor(black)
    c.setLineWidth(0.5)
    c.line(M + 0.42 * inch, info_y - 1, W / 2 - 0.1 * inch, info_y - 1)

    c.setFillColor(black)
    c.drawString(W / 2 + 0.05 * inch, info_y, "FINISH:")
    c.line(W / 2 + 0.50 * inch, info_y - 1, W - M, info_y - 1)

    # ── Footer bar (outlined) ──
    foot_h = 0.22 * inch
    c.setStrokeColor(black)
    c.setLineWidth(0.75)
    c.rect(0, 0, W, foot_h, fill=0, stroke=1)
    c.setFillColor(black)
    c.setFont("Helvetica", 5.5)
    c.drawCentredString(W / 2, 0.07 * inch,
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
    Generate a PDF with one 4×6" sticker per page for work order items.

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
# ─────────────────────────────────────────────

def generate_wo_sticker_zpl(
    wo_dict: dict,
    items: Optional[List[dict]] = None,
    app_base_url: str = "http://localhost:8888",
) -> str:
    """
    Generate ZPL commands for work order stickers.
    4"x6" label at 203 DPI = 812 x 1218 dots.
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
        comp_type = item.get("component_type", "").upper()
        desc = item.get("description", "")[:45]
        qty = str(item.get("quantity", 1))
        machine = item.get("machine", "")
        drawing_ref = item.get("drawing_ref", "")
        qr_data = f"{app_base_url}/wo/{job_code}/{item_id}"
        print_date = datetime.date.today().strftime("%m/%d/%Y")

        zpl = []
        zpl.append("^XA")
        zpl.append(f"^PW{label_w}")
        zpl.append(f"^LL{label_h}")

        # Header
        zpl.append("^FO0,0^GB812,90,90,,^FS")  # Navy header bar
        zpl.append("^FO20,20^A0N,28,28^FR^FDTITANFORGE^FS")
        zpl.append("^FO20,55^A0N,20,20^FR^FDWORK ORDER STICKER^FS")
        zpl.append(f"^FO550,20^A0N,22,22^FR^FDPrinted: {print_date}^FS")
        zpl.append(f"^FO650,55^A0N,18,18^FR^FDRev {revision}^FS")

        # Gold line
        zpl.append("^FO0,92^GB812,4,4,,^FS")

        # QR Code (left side)
        zpl.append(f"^FO30,120^BQN,2,6^FDMM,{qr_data}^FS")

        # Ship mark (large, right of QR)
        zpl.append(f"^FO340,130^A0N,72,72^FD{mark}^FS")

        # Component type
        zpl.append(f"^FO340,215^A0N,24,24^FD{comp_type}^FS")

        # Description
        zpl.append(f"^FO340,260^A0N,22,22^FD{desc}^FS")

        # "SCAN TO START / FINISH"
        zpl.append("^FO50,420^A0N,18,18^FDSCAN TO START / FINISH^FS")

        # Divider
        zpl.append("^FO20,460^GB772,2,2,,^FS")

        # Info grid
        grid_y = 480
        zpl.append(f"^FO30,{grid_y}^A0N,18,18^FDJOB CODE^FS")
        zpl.append(f"^FO30,{grid_y+25}^A0N,28,28^FD{job_code}^FS")
        zpl.append(f"^FO300,{grid_y}^A0N,18,18^FDQTY^FS")
        zpl.append(f"^FO300,{grid_y+25}^A0N,28,28^FD{qty}^FS")
        zpl.append(f"^FO530,{grid_y}^A0N,18,18^FDMACHINE^FS")
        zpl.append(f"^FO530,{grid_y+25}^A0N,28,28^FD{machine}^FS")

        # WO ID and Item ID
        wo_y = grid_y + 80
        zpl.append(f"^FO20,{wo_y}^GB772,2,2,,^FS")
        zpl.append(f"^FO30,{wo_y+15}^A0N,20,20^FDWO: {wo_id}^FS")
        zpl.append(f"^FO30,{wo_y+42}^A0N,18,18^FDITEM: {item_id}^FS")
        zpl.append(f"^FO30,{wo_y+68}^A0N,18,18^FDDrawing: {drawing_ref}^FS")

        # Start/Finish fields
        sf_y = wo_y + 110
        zpl.append(f"^FO30,{sf_y}^A0N,22,22^FDSTART: _______________^FS")
        zpl.append(f"^FO430,{sf_y}^A0N,22,22^FDFINISH: ______________^FS")

        # Footer
        zpl.append(f"^FO0,{label_h-40}^GB812,40,40,,^FS")
        zpl.append(f"^FO150,{label_h-30}^A0N,18,18^FR^FDStructures America | Conroe TX | TitanForge^FS")

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
        "job_code", "revision", "qr_url",
    ])

    for item in target_items:
        item_id = item.get("item_id", "")
        qr_url = f"{app_base_url}/wo/{job_code}/{item_id}"
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
            qr_url,
        ])

    return buf.getvalue().encode("utf-8")
