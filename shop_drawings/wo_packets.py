"""
TitanForge — Work Order Packet PDF Generator
=============================================
Generates printable work order packets containing:
  - Cover sheet with job info, WO summary, and status
  - Item checklist pages with step-by-step fabrication instructions
  - QR codes for each item (scan to start/finish)

Uses ReportLab for PDF generation with the TitanForge design system.
Output: 8.5" x 11" portrait PDF.
"""

import io
import datetime
from typing import List, Optional

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF


# ─────────────────────────────────────────────
# COLORS (TitanForge design system)
# ─────────────────────────────────────────────

NAVY = HexColor("#0A1628")
BLUE = HexColor("#1E40AF")
GOLD = HexColor("#D4A843")
DARK_GRAY = HexColor("#1E293B")
MED_GRAY = HexColor("#64748B")
LIGHT_GRAY = HexColor("#E2E8F0")
WHITE = HexColor("#FFFFFF")
GREEN = HexColor("#059669")
AMBER = HexColor("#D97706")
RED = HexColor("#DC2626")

PAGE_W, PAGE_H = letter  # 612 x 792 points
MARGIN = 0.6 * inch


def generate_wo_packet_pdf(work_order_dict: dict,
                            steps_by_item: dict,
                            base_url: str = "http://localhost:8080") -> bytes:
    """Generate a complete work order packet PDF.

    Args:
        work_order_dict: WorkOrder.to_dict() result
        steps_by_item: Dict mapping item_id -> list of step dicts
        base_url: Base URL for QR codes

    Returns:
        PDF bytes
    """
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.setTitle(f"Work Order Packet — {work_order_dict.get('work_order_id', '')}")
    c.setAuthor("TitanForge")

    # ── Page 1: Cover Sheet ──
    _draw_cover_sheet(c, work_order_dict)

    # ── Item Pages: One page per item with steps ──
    items = work_order_dict.get("items", [])
    for idx, item in enumerate(items):
        c.showPage()
        item_steps = steps_by_item.get(item.get("item_id", ""), [])
        _draw_item_page(c, work_order_dict, item, item_steps, idx + 1,
                        len(items), base_url)

    c.save()
    return buf.getvalue()


# ─────────────────────────────────────────────
# COVER SHEET
# ─────────────────────────────────────────────

def _draw_cover_sheet(c, wo: dict):
    """Draw the work order cover sheet (page 1)."""
    y = PAGE_H - MARGIN

    # ── Header banner ──
    c.setFillColor(NAVY)
    c.rect(0, PAGE_H - 90, PAGE_W, 90, fill=True, stroke=False)

    # Gold accent bar
    c.setFillColor(GOLD)
    c.rect(0, PAGE_H - 94, PAGE_W, 4, fill=True, stroke=False)

    # Title
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(MARGIN, PAGE_H - 40, "WORK ORDER PACKET")

    c.setFont("Helvetica", 12)
    c.drawString(MARGIN, PAGE_H - 60, wo.get("work_order_id", ""))

    c.setFont("Helvetica", 10)
    c.drawRightString(PAGE_W - MARGIN, PAGE_H - 40,
                      f"Job: {wo.get('job_code', '')}")
    c.drawRightString(PAGE_W - MARGIN, PAGE_H - 56,
                      f"Revision: {wo.get('revision', '')}")
    c.drawRightString(PAGE_W - MARGIN, PAGE_H - 72,
                      f"Generated: {datetime.datetime.now().strftime('%m/%d/%Y %I:%M %p')}")

    y = PAGE_H - 130

    # ── Status badge ──
    status = wo.get("status", "queued").upper()
    status_color = {
        "QUEUED": MED_GRAY, "APPROVED": BLUE, "STICKERS_PRINTED": AMBER,
        "IN_PROGRESS": GREEN, "COMPLETE": GREEN, "ON_HOLD": RED,
    }.get(status, MED_GRAY)

    c.setFillColor(status_color)
    c.roundRect(MARGIN, y - 25, 140, 28, 4, fill=True, stroke=False)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGIN + 10, y - 18, f"STATUS: {status}")

    y -= 55

    # ── Job Info Table ──
    c.setFillColor(DARK_GRAY)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(MARGIN, y, "Job Information")
    y -= 5

    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    c.line(MARGIN, y, MARGIN + 160, y)
    y -= 20

    info_rows = [
        ("Job Code:", wo.get("job_code", "")),
        ("Work Order ID:", wo.get("work_order_id", "")),
        ("Revision:", wo.get("revision", "")),
        ("Created By:", wo.get("created_by", "")),
        ("Created At:", _format_dt(wo.get("created_at", ""))),
        ("Approved By:", wo.get("approved_by", "") or "—"),
        ("Approved At:", _format_dt(wo.get("approved_at", "")) or "—"),
    ]

    for label, value in info_rows:
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(MED_GRAY)
        c.drawString(MARGIN, y, label)
        c.setFont("Helvetica", 10)
        c.setFillColor(DARK_GRAY)
        c.drawString(MARGIN + 120, y, str(value))
        y -= 18

    y -= 15

    # ── Item Summary ──
    items = wo.get("items", [])
    c.setFillColor(DARK_GRAY)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(MARGIN, y, f"Items ({len(items)} total)")
    y -= 5
    c.setStrokeColor(GOLD)
    c.line(MARGIN, y, MARGIN + 160, y)
    y -= 20

    # Count by component type
    type_counts = {}
    for item in items:
        ct = item.get("component_type", "other")
        type_counts[ct] = type_counts.get(ct, 0) + 1

    # Count by status
    status_counts = {}
    for item in items:
        s = item.get("status", "queued")
        status_counts[s] = status_counts.get(s, 0) + 1

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(MED_GRAY)
    c.drawString(MARGIN, y, "By Type:")
    c.setFont("Helvetica", 10)
    c.setFillColor(DARK_GRAY)
    type_str = ", ".join(f"{v}x {k}" for k, v in sorted(type_counts.items()))
    c.drawString(MARGIN + 80, y, type_str)
    y -= 18

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(MED_GRAY)
    c.drawString(MARGIN, y, "By Status:")
    c.setFont("Helvetica", 10)
    c.setFillColor(DARK_GRAY)
    status_str = ", ".join(f"{v} {k}" for k, v in sorted(status_counts.items()))
    c.drawString(MARGIN + 80, y, status_str)
    y -= 30

    # ── Item Table ──
    # Header
    c.setFillColor(NAVY)
    c.rect(MARGIN, y - 2, PAGE_W - 2 * MARGIN, 18, fill=True, stroke=False)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 8)

    cols = [MARGIN + 5, MARGIN + 40, MARGIN + 110, MARGIN + 240,
            MARGIN + 340, MARGIN + 410]
    headers = ["#", "Ship Mark", "Type", "Machine", "Status", "Drawing"]
    for col, hdr in zip(cols, headers):
        c.drawString(col, y + 3, hdr)
    y -= 18

    # Rows
    for idx, item in enumerate(items):
        if y < MARGIN + 40:
            # Not enough room — note continuation
            c.setFillColor(MED_GRAY)
            c.setFont("Helvetica-Oblique", 9)
            c.drawString(MARGIN, y, f"... and {len(items) - idx} more items (see individual pages)")
            break

        bg = LIGHT_GRAY if idx % 2 == 0 else WHITE
        c.setFillColor(bg)
        c.rect(MARGIN, y - 2, PAGE_W - 2 * MARGIN, 16, fill=True, stroke=False)

        c.setFillColor(DARK_GRAY)
        c.setFont("Helvetica", 8)
        row_data = [
            str(idx + 1),
            item.get("ship_mark", ""),
            item.get("component_type", ""),
            item.get("machine", ""),
            item.get("status", "queued"),
            item.get("drawing_ref", ""),
        ]
        for col, val in zip(cols, row_data):
            c.drawString(col, y + 2, str(val)[:25])
        y -= 16

    # ── Footer ──
    _draw_footer(c, 1, "Cover")


# ─────────────────────────────────────────────
# ITEM PAGE WITH STEP-BY-STEP INSTRUCTIONS
# ─────────────────────────────────────────────

def _draw_item_page(c, wo: dict, item: dict, steps: list,
                     item_num: int, total_items: int, base_url: str):
    """Draw an item detail page with fabrication steps."""
    y = PAGE_H - MARGIN

    # ── Header ──
    c.setFillColor(NAVY)
    c.rect(0, PAGE_H - 70, PAGE_W, 70, fill=True, stroke=False)
    c.setFillColor(GOLD)
    c.rect(0, PAGE_H - 73, PAGE_W, 3, fill=True, stroke=False)

    # Ship mark (big)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 28)
    c.drawString(MARGIN, PAGE_H - 48, item.get("ship_mark", ""))

    # Component type badge
    c.setFont("Helvetica", 11)
    comp_type = item.get("component_type", "").upper()
    c.drawString(MARGIN + 100, PAGE_H - 45, comp_type)

    # Right side info
    c.setFont("Helvetica", 9)
    c.drawRightString(PAGE_W - MARGIN, PAGE_H - 25,
                      f"WO: {wo.get('work_order_id', '')}")
    c.drawRightString(PAGE_W - MARGIN, PAGE_H - 38,
                      f"Job: {wo.get('job_code', '')}")
    c.drawRightString(PAGE_W - MARGIN, PAGE_H - 51,
                      f"Item {item_num} of {total_items}")
    c.drawRightString(PAGE_W - MARGIN, PAGE_H - 64,
                      f"Machine: {item.get('machine', '')}")

    y = PAGE_H - 95

    # ── Description line ──
    c.setFillColor(DARK_GRAY)
    c.setFont("Helvetica", 10)
    desc = item.get("description", "")
    if len(desc) > 90:
        desc = desc[:87] + "..."
    c.drawString(MARGIN, y, desc)
    y -= 8

    # Drawing ref
    dref = item.get("drawing_ref", "")
    if dref:
        c.setFillColor(MED_GRAY)
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(MARGIN, y, f"Drawing: {dref}")
    y -= 20

    # ── QR Code (right side, below header) ──
    qr_url = f"{base_url}/work-orders/{wo.get('job_code', '')}?scan={item.get('item_id', '')}"
    qr = QrCodeWidget(qr_url)
    qr.barWidth = 80
    qr.barHeight = 80
    d = Drawing(80, 80)
    d.add(qr)
    renderPDF.draw(d, c, PAGE_W - MARGIN - 85, PAGE_H - 165)

    c.setFillColor(MED_GRAY)
    c.setFont("Helvetica", 7)
    c.drawCentredString(PAGE_W - MARGIN - 45, PAGE_H - 172, "Scan to Start/Finish")

    # ── Step-by-Step Instructions ──
    c.setFillColor(DARK_GRAY)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(MARGIN, y, "Fabrication Steps")
    y -= 4
    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    c.line(MARGIN, y, MARGIN + 140, y)
    y -= 15

    total_est = sum(s.get("estimated_minutes", 0) for s in steps)
    c.setFillColor(MED_GRAY)
    c.setFont("Helvetica", 9)
    c.drawString(MARGIN, y, f"{len(steps)} steps | Est. {total_est} min total")
    y -= 18

    for step in steps:
        needed = 65  # Min height per step
        if y < MARGIN + 50:
            # Continue on next page
            _draw_footer(c, item_num + 1, item.get("ship_mark", ""))
            c.showPage()
            y = PAGE_H - MARGIN

            # Mini header on continuation
            c.setFillColor(NAVY)
            c.rect(0, PAGE_H - 35, PAGE_W, 35, fill=True, stroke=False)
            c.setFillColor(WHITE)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(MARGIN, PAGE_H - 24,
                         f"{item.get('ship_mark', '')} — Steps (continued)")
            c.setFont("Helvetica", 9)
            c.drawRightString(PAGE_W - MARGIN, PAGE_H - 24,
                              f"WO: {wo.get('work_order_id', '')}")
            y = PAGE_H - 55

        y = _draw_step(c, step, y)
        y -= 8

    # ── Sign-off area ──
    if y > MARGIN + 80:
        y -= 10
        c.setStrokeColor(LIGHT_GRAY)
        c.setLineWidth(0.5)
        c.line(MARGIN, y, PAGE_W - MARGIN, y)
        y -= 20

        c.setFillColor(DARK_GRAY)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(MARGIN, y, "Completion Sign-off")
        y -= 20

        # Two columns
        mid = PAGE_W / 2
        c.setFont("Helvetica", 9)
        c.setFillColor(MED_GRAY)

        c.drawString(MARGIN, y, "Fabricator:")
        c.setStrokeColor(MED_GRAY)
        c.setLineWidth(0.5)
        c.line(MARGIN + 60, y - 2, mid - 20, y - 2)

        c.drawString(mid, y, "Date/Time:")
        c.line(mid + 60, y - 2, PAGE_W - MARGIN, y - 2)
        y -= 22

        c.drawString(MARGIN, y, "QC Inspector:")
        c.line(MARGIN + 75, y - 2, mid - 20, y - 2)

        c.drawString(mid, y, "Pass / Fail:")
        # Draw checkbox squares
        c.rect(mid + 65, y - 3, 12, 12, fill=False, stroke=True)
        c.drawString(mid + 80, y, "Pass")
        c.rect(mid + 115, y - 3, 12, 12, fill=False, stroke=True)
        c.drawString(mid + 130, y, "Fail")

    _draw_footer(c, item_num + 1, item.get("ship_mark", ""))


def _draw_step(c, step: dict, y: float) -> float:
    """Draw a single fabrication step. Returns new y position."""
    step_num = step.get("step_num", 0)
    is_checkpoint = step.get("checkpoint", False)

    # Step number circle
    circle_r = 12
    circle_x = MARGIN + circle_r
    circle_y = y - 2

    if is_checkpoint:
        c.setFillColor(GOLD)
    else:
        c.setFillColor(BLUE)
    c.circle(circle_x, circle_y, circle_r, fill=True, stroke=False)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(circle_x, circle_y - 4, str(step_num))

    # Step title
    title_x = MARGIN + 32
    c.setFillColor(DARK_GRAY)
    c.setFont("Helvetica-Bold", 11)
    title = step.get("title", "")
    if is_checkpoint:
        title += "  [CHECKPOINT]"
    c.drawString(title_x, y, title)

    # Est time badge
    est_min = step.get("estimated_minutes", 0)
    if est_min:
        c.setFillColor(LIGHT_GRAY)
        badge_w = 55
        c.roundRect(PAGE_W - MARGIN - badge_w, y - 3, badge_w, 16, 3,
                    fill=True, stroke=False)
        c.setFillColor(MED_GRAY)
        c.setFont("Helvetica", 8)
        c.drawCentredString(PAGE_W - MARGIN - badge_w / 2, y, f"~{est_min} min")

    y -= 16

    # Instruction text (wrapped)
    instruction = step.get("instruction", "")
    c.setFillColor(DARK_GRAY)
    c.setFont("Helvetica", 9)
    y = _draw_wrapped_text(c, instruction, title_x, y,
                           PAGE_W - MARGIN - title_x - 10, 11)

    # Tool
    tool = step.get("tool", "")
    if tool:
        y -= 3
        c.setFillColor(MED_GRAY)
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(title_x, y, f"Tools: {tool}")
        y -= 11

    # Safety note
    safety = step.get("safety", "")
    if safety:
        y -= 2
        c.setFillColor(RED)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(title_x, y, "SAFETY:")
        c.setFont("Helvetica", 8)
        c.setFillColor(HexColor("#B91C1C"))
        c.drawString(title_x + 48, y, safety[:80])
        y -= 11

    # Completion checkbox
    y -= 2
    c.setStrokeColor(MED_GRAY)
    c.setLineWidth(0.5)
    c.rect(title_x, y - 1, 10, 10, fill=False, stroke=True)
    c.setFillColor(MED_GRAY)
    c.setFont("Helvetica", 8)
    c.drawString(title_x + 14, y + 1, "Done")

    # Separator line
    y -= 6
    c.setStrokeColor(LIGHT_GRAY)
    c.setLineWidth(0.3)
    c.line(title_x, y, PAGE_W - MARGIN, y)

    return y


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _draw_wrapped_text(c, text: str, x: float, y: float,
                        max_width: float, line_height: float) -> float:
    """Draw text with word wrapping. Returns final y position."""
    words = text.split()
    line = ""
    for word in words:
        test_line = f"{line} {word}".strip()
        if c.stringWidth(test_line, c._fontname, c._fontsize) > max_width:
            c.drawString(x, y, line)
            y -= line_height
            line = word
        else:
            line = test_line
    if line:
        c.drawString(x, y, line)
        y -= line_height
    return y


def _draw_footer(c, page_num: int, section: str):
    """Draw page footer."""
    c.setFillColor(LIGHT_GRAY)
    c.rect(0, 0, PAGE_W, 25, fill=True, stroke=False)

    c.setFillColor(MED_GRAY)
    c.setFont("Helvetica", 7)
    c.drawString(MARGIN, 8,
                 f"TitanForge Work Order Packet | {section} | "
                 f"Generated {datetime.datetime.now().strftime('%m/%d/%Y')}")
    c.drawRightString(PAGE_W - MARGIN, 8, f"Page {page_num}")


def _format_dt(iso_str: str) -> str:
    """Format ISO timestamp to readable string."""
    if not iso_str:
        return ""
    try:
        dt = datetime.datetime.fromisoformat(iso_str)
        return dt.strftime("%m/%d/%Y %I:%M %p")
    except Exception:
        return iso_str
