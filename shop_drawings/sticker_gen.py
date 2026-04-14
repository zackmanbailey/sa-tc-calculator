"""
Sticker / Label Generator for Shop Fabrication Tracking
Generates 4"x6" sticker layouts as PDF for thermal transfer printing.

Each sticker contains:
  - Ship mark / group ID
  - Job number and project name
  - Quantity
  - Total weight (auto-calculated)
  - Machine assignment
  - Date fabricated (blank — filled by worker)
  - Drawing reference
  - QR code placeholder (links to TitanForge project context)

Sticker grouping rules:
  - Columns: 1 per column assembly
  - Rafters: 1 per rafter assembly
  - Purlins: 1 per purlin group per building
  - Sag rods: 1 per 10
  - Hurricane straps: 1 per 10
  - P1 clips: 1 per fabrication batch
  - Panels: 1 per stack (max 2000 lbs or 50 sheets)
  - Endcaps: 1 per group per building
  - Splice plates: 1 per pair
"""

import math
import io
import os
import datetime
from typing import Dict, List, Optional

from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import inch
from reportlab.lib.colors import black, white, HexColor
from reportlab.pdfgen import canvas

from shop_drawings.config import (
    STICKER_CONFIG, STICKER_GROUPING, MACHINES,
    COLUMN_DEFAULTS, RAFTER_DEFAULTS, PURLIN_DEFAULTS,
    SAG_ROD_DEFAULTS, STRAP_DEFAULTS, PANEL_STACK_LIMITS,
    ShopDrawingConfig,
)
from shop_drawings.column_gen import _fmt_ft_in


# ═══════════════════════════════════════════════════════════════════════════════
# STICKER DIMENSIONS
# ═══════════════════════════════════════════════════════════════════════════════

STICKER_W = 6 * inch   # Width
STICKER_H = 4 * inch   # Height
STICKER_MARGIN = 0.2 * inch

# How many stickers fit per 8.5x11 page (landscape)?
# 11" wide / 6" = 1 per row, 8.5" tall / 4" = 2 per column = 2 per page
# Actually let's print 1 per page for clarity, or tile them
PAGE_W = 11 * inch
PAGE_H = 8.5 * inch
STICKERS_PER_ROW = 1
STICKERS_PER_COL = 2


# ═══════════════════════════════════════════════════════════════════════════════
# QR CODE PLACEHOLDER
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_qr_placeholder(c, x: float, y: float, size: float,
                         url_hint: str = ""):
    """Draw a QR code placeholder square with crosshairs."""
    c.setStrokeColor(black)
    c.setLineWidth(0.5)
    c.rect(x, y, size, size)

    # Crosshairs
    cx, cy = x + size / 2, y + size / 2
    c.setStrokeColor(HexColor("#CCCCCC"))
    c.line(x + 3, cy, x + size - 3, cy)
    c.line(cx, y + 3, cx, y + size - 3)

    # Corner squares (QR finder patterns)
    corner_size = size * 0.2
    for ox_off, oy_off in [(0, 0), (size - corner_size, 0),
                            (0, size - corner_size)]:
        c.setFillColor(black)
        c.rect(x + ox_off + 2, y + oy_off + 2,
               corner_size - 4, corner_size - 4, fill=1)
        c.setFillColor(white)
        c.rect(x + ox_off + 5, y + oy_off + 5,
               corner_size - 10, corner_size - 10, fill=1)
        c.setFillColor(black)
        c.rect(x + ox_off + 7, y + oy_off + 7,
               corner_size - 14, corner_size - 14, fill=1)

    # "QR" label
    c.setFillColor(HexColor("#999999"))
    c.setFont("Helvetica", 5)
    c.drawCentredString(cx, y - 5, "SCAN FOR PROJECT")


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLE STICKER RENDERER
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_sticker(c, data: Dict, ox: float, oy: float):
    """
    Draw a single 4"x6" sticker at position (ox, oy).
    data keys: mark, job_code, project_name, qty, weight_lbs,
               machine, drawing_ref, component_type, description
    """
    m = STICKER_MARGIN
    w = STICKER_W
    h = STICKER_H

    # Outer border (cut line)
    c.setStrokeColor(HexColor("#AAAAAA"))
    c.setLineWidth(0.3)
    c.setDash([3, 3])
    c.rect(ox, oy, w, h)
    c.setDash([])

    # Inner content area
    c.setStrokeColor(black)
    c.setLineWidth(1.0)
    c.rect(ox + m, oy + m, w - 2 * m, h - 2 * m)

    # ── Header bar ──
    header_h = 0.5 * inch
    hx = ox + m
    hy = oy + h - m - header_h
    c.setFillColor(HexColor("#1A1A2E"))
    c.rect(hx, hy, w - 2 * m, header_h, fill=1)

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(hx + 8, hy + header_h * 0.35, data.get("mark", "???"))

    c.setFont("Helvetica-Bold", 8)
    c.drawRightString(hx + w - 2 * m - 8, hy + header_h * 0.55,
                      data.get("component_type", "").upper())
    c.setFont("Helvetica", 7)
    c.drawRightString(hx + w - 2 * m - 8, hy + header_h * 0.2,
                      data.get("job_code", ""))

    # ── Content rows ──
    content_x = hx + 8
    content_w = w - 2 * m - 16
    qr_size = 1.0 * inch
    text_w = content_w - qr_size - 10

    row_h = 0.28 * inch
    y = hy - 5

    fields = [
        ("PROJECT:", data.get("project_name", "")),
        ("QTY:", str(data.get("qty", ""))),
        ("WEIGHT:", f'{data.get("weight_lbs", 0):.0f} LBS'),
        ("MACHINE:", data.get("machine", "")),
        ("DRAWING:", data.get("drawing_ref", "")),
        ("DESCRIPTION:", data.get("description", "")),
    ]

    c.setFillColor(black)
    for label, value in fields:
        y -= row_h
        if y < oy + m + 8:
            break
        c.setFont("Helvetica-Bold", 7)
        c.drawString(content_x, y, label)
        c.setFont("Helvetica", 7)
        # Truncate long values
        max_chars = int(text_w / 4.2)
        display = value[:max_chars] if len(value) > max_chars else value
        c.drawString(content_x + 55, y, display)

    # ── Date fabricated (blank line) ──
    y -= row_h
    c.setFont("Helvetica-Bold", 7)
    c.drawString(content_x, y, "DATE FAB:")
    c.setStrokeColor(HexColor("#CCCCCC"))
    c.setLineWidth(0.5)
    c.line(content_x + 55, y - 1, content_x + text_w, y - 1)

    # ── QR Code ──
    qr_x = hx + w - 2 * m - qr_size - 5
    qr_y = hy - qr_size - 15
    url = f"titanforge://project/{data.get('job_code', '')}?mark={data.get('mark', '')}"
    _draw_qr_placeholder(c, qr_x, qr_y, qr_size, url)

    # ── Footer ──
    c.setFont("Helvetica", 5)
    c.setFillColor(HexColor("#888888"))
    c.drawCentredString(ox + w / 2, oy + m + 3,
                        "Structures America | 14369 FM 1314, Conroe TX 77302 | TitanForge")


# ═══════════════════════════════════════════════════════════════════════════════
# STICKER DATA GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

def _generate_sticker_data(cfg: ShopDrawingConfig) -> List[Dict]:
    """
    Generate all sticker data for a project based on grouping rules.
    Returns list of dicts, one per sticker to print.
    """
    stickers = []
    lbs_per_lft_cee = 10.83
    n_frames = cfg.n_frames
    n_struct_cols = n_frames if cfg.frame_type == "tee" else n_frames * 2

    # ── Column stickers (1 per column) ──
    import math as m
    slope_deg = cfg.roof_pitch_deg
    tan_slope = m.tan(m.radians(slope_deg))
    dist = cfg.building_width_ft / (2 if cfg.frame_type == "tee" else 3)
    col_len_ft = (cfg.clear_height_ft + dist * tan_slope
                  + cfg.embedment_ft + cfg.column_buffer_ft)
    col_weight = col_len_ft * 2 * lbs_per_lft_cee

    for i in range(n_struct_cols):
        stickers.append({
            "mark": f"C{i + 1}",
            "job_code": cfg.job_code,
            "project_name": cfg.project_name,
            "qty": 1,
            "weight_lbs": col_weight,
            "machine": "C2 → WELDING → CLEANING",
            "drawing_ref": f"{cfg.job_code}_C1",
            "component_type": "Column",
            "description": f"CEE 14x4x10GA Box Column, {_fmt_ft_in(col_len_ft * 12)}",
        })

    # ── Rafter stickers (1 per rafter) ──
    from shop_drawings.config import calc_rafter_length
    use_z = cfg.raft_purlin_type == "z"
    raft_len = calc_rafter_length(cfg.building_width_ft,
                                  cfg.raft_roofing_overhang_ft, use_z)
    raft_weight = raft_len * 2 * lbs_per_lft_cee

    for i in range(n_frames):
        stickers.append({
            "mark": f"B{i + 1}",
            "job_code": cfg.job_code,
            "project_name": cfg.project_name,
            "qty": 1,
            "weight_lbs": raft_weight,
            "machine": "C2 → WELDING → CLEANING",
            "drawing_ref": f"{cfg.job_code}_B1",
            "component_type": "Rafter",
            "description": f"CEE 14x4x10GA Box Rafter, {_fmt_ft_in(raft_len * 12)}",
        })

    # ── Purlin stickers (1 per group per building) ──
    from shop_drawings.purlin_gen import calc_purlin_groups
    groups = calc_purlin_groups(cfg)
    lbs_per_lft_purlin = 7.43
    for g in groups:
        n_purlin_lines = m.floor(cfg.building_width_ft / cfg.purlin_spacing_ft) + 1
        total_qty = g["qty_per_building"] * n_purlin_lines
        group_weight = g["length_ft"] * lbs_per_lft_purlin * total_qty
        stickers.append({
            "mark": g["group_id"],
            "job_code": cfg.job_code,
            "project_name": cfg.project_name,
            "qty": total_qty,
            "weight_lbs": group_weight,
            "machine": "Z1" if cfg.purlin_type == "z" else "C1",
            "drawing_ref": f"{cfg.job_code}_PURLINS",
            "component_type": f"Purlin Group",
            "description": (f'{g["group_id"]} {g["label"]}, '
                            f'{_fmt_ft_in(g["length_in"])} ea'),
        })

    # ── Sag rod stickers (1 per 10) ──
    n_rods = n_frames * SAG_ROD_DEFAULTS["qty_per_rafter"]
    n_pieces = n_rods * SAG_ROD_DEFAULTS["pieces_per_rod"]
    bundle_size = SAG_ROD_DEFAULTS["bundle_size"]
    n_bundles = m.ceil(n_pieces / bundle_size)
    for i in range(n_bundles):
        qty_in_bundle = min(bundle_size, n_pieces - i * bundle_size)
        stickers.append({
            "mark": f"SR-{i+1}",
            "job_code": cfg.job_code,
            "project_name": cfg.project_name,
            "qty": qty_in_bundle,
            "weight_lbs": qty_in_bundle * 0.8656 * 20,  # Approximate
            "machine": "ANGLE",
            "drawing_ref": f"{cfg.job_code}_CUTLIST",
            "component_type": "Sag Rods",
            "description": f'2"x2" Angle Sag Rods, bundle {i+1}/{n_bundles}',
        })

    # ── Hurricane strap stickers (1 per 10) ──
    n_straps = n_frames * STRAP_DEFAULTS["qty_per_rafter"]
    n_strap_bundles = m.ceil(n_straps / STRAP_DEFAULTS["bundle_size"])
    for i in range(n_strap_bundles):
        qty = min(STRAP_DEFAULTS["bundle_size"],
                  n_straps - i * STRAP_DEFAULTS["bundle_size"])
        stickers.append({
            "mark": f"HS-{i+1}",
            "job_code": cfg.job_code,
            "project_name": cfg.project_name,
            "qty": qty,
            "weight_lbs": qty * 0.706 * STRAP_DEFAULTS["length_in"] / 12,
            "machine": "P1",
            "drawing_ref": f"{cfg.job_code}_CUTLIST",
            "component_type": "Hurricane Straps",
            "description": f'1.5"x{STRAP_DEFAULTS["length_in"]}" straps, '
                           f'bundle {i+1}/{n_strap_bundles}',
        })

    return stickers


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

def generate_sticker_pdf(
    cfg: ShopDrawingConfig,
    output_path: Optional[str] = None,
) -> bytes:
    """
    Generate a multi-page PDF with all project stickers.
    2 stickers per page (6"x4" on 8.5"x11" landscape).
    """
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=landscape((8.5 * inch, 11 * inch)))
    c.setTitle(f"Stickers — {cfg.job_code}")

    stickers = _generate_sticker_data(cfg)

    # Layout: 2 stickers per page, centered
    page_w = 11 * inch
    page_h = 8.5 * inch
    stickers_per_page = 2
    x_offset = (page_w - STICKER_W) / 2
    y_positions = [
        page_h / 2 + 0.1 * inch,   # Top sticker
        page_h / 2 - STICKER_H - 0.1 * inch,  # Bottom sticker
    ]

    for idx, sticker_data in enumerate(stickers):
        slot = idx % stickers_per_page
        if slot == 0 and idx > 0:
            c.showPage()

        _draw_sticker(c, sticker_data, x_offset, y_positions[slot])

    c.save()
    pdf_bytes = buf.getvalue()

    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)

    return pdf_bytes
