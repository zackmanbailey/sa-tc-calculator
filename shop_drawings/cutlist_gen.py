"""
Cut-List Shop Drawing PDF Generator
Produces 8.5"x11" landscape PDFs for simpler components that don't need
full 4-view engineering drawings — just a cut list table with dimensions,
a simple profile sketch, and the standard title block.

Components covered:
  - Endcaps (U-channel, 2 per building end)
  - Roofing panels (Spartan Rib, split at center purlin)
  - Wall panels (Spartan Rib, vertical)
  - Sag rods (2"x2" angle, bundled per 10)
  - Hurricane straps (1.5"x28" rectangle, bundled per 10)
  - Splice plates (roll formed, shipped per pair)
"""

import math
import io
import os
import datetime
from typing import Dict, List, Optional

from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.units import inch
from reportlab.lib.colors import black, white, HexColor
from reportlab.pdfgen import canvas

from shop_drawings.config import (
    PURLIN_DEFAULTS, ROOFING_DEFAULTS, WALL_DEFAULTS,
    SAG_ROD_DEFAULTS, STRAP_DEFAULTS, RAFTER_DEFAULTS,
    PANEL_STACK_LIMITS, STANDARD_NOTES, TITLE_BLOCK,
    ShopDrawingConfig, calc_wall_panel_length_in,
)
from shop_drawings.column_gen import (
    _fmt_ft_in, draw_dimension_h, draw_dimension_v,
    _draw_standard_notes, _draw_border,
    CLR_OBJECT, CLR_DIM, CLR_HIDDEN, CLR_GRID,
    CLR_TITLE_BG, CLR_TITLE_TEXT,
    PAGE_W, PAGE_H, MARGIN,
    THICK, MEDIUM, THIN, HAIR,
)


# ═══════════════════════════════════════════════════════════════════════════════
# SHARED CUT-LIST TABLE RENDERER
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_cutlist_table(c, items: List[Dict], ox: float, oy: float,
                        w: float, h: float, title: str = "CUT LIST"):
    """
    Generic cut-list table.
    Each item: {mark, qty, description, length, material, notes}
    """
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(THIN)

    headers = ["MARK", "QTY", "DESCRIPTION", "LENGTH", "MATERIAL", "NOTES"]
    col_widths = [w*0.08, w*0.06, w*0.22, w*0.16, w*0.18, w*0.30]

    row_h = 10
    n_rows = len(items) + 1
    table_h = min(n_rows * row_h, h - 15)

    c.rect(ox, oy + h - table_h, w, table_h)

    # Header
    hy = oy + h - row_h
    c.setFillColor(HexColor("#2A2A4A"))
    c.rect(ox, hy, w, row_h, fill=1)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 5)
    x_pos = ox
    for i, hdr in enumerate(headers):
        c.drawCentredString(x_pos + col_widths[i] / 2, hy + 3, hdr)
        x_pos += col_widths[i]

    # Column separators
    x_pos = ox
    for cw in col_widths[:-1]:
        x_pos += cw
        c.setStrokeColor(CLR_GRID)
        c.setLineWidth(HAIR)
        c.line(x_pos, oy + h - table_h, x_pos, oy + h)

    # Data rows
    c.setFillColor(black)
    c.setFont("Helvetica", 4.5)
    for r_idx, item in enumerate(items):
        ry = hy - (r_idx + 1) * row_h
        if ry < oy:
            break
        if r_idx % 2 == 1:
            c.setFillColor(HexColor("#F5F5F5"))
            c.rect(ox, ry, w, row_h, fill=1)
            c.setFillColor(black)
        c.setStrokeColor(CLR_GRID)
        c.setLineWidth(HAIR)
        c.line(ox, ry, ox + w, ry)

        row = [
            item.get("mark", ""),
            str(item.get("qty", "")),
            item.get("description", ""),
            item.get("length", ""),
            item.get("material", ""),
            item.get("notes", ""),
        ]
        x_pos = ox
        for i, cell in enumerate(row):
            # Truncate long notes
            max_chars = int(col_widths[i] / 3.2)
            display = cell[:max_chars] if len(cell) > max_chars else cell
            c.drawCentredString(x_pos + col_widths[i] / 2, ry + 3, display)
            x_pos += col_widths[i]

    # Title
    c.setFont("Helvetica-Bold", 6)
    c.setFillColor(black)
    c.drawCentredString(ox + w / 2, oy + h - table_h - 10, title)


# ═══════════════════════════════════════════════════════════════════════════════
# SHARED TITLE BLOCK
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_cutlist_title_block(c, cfg: ShopDrawingConfig, drawing_title: str,
                              sheet_num: int = 1, total_sheets: int = 1,
                              revision: str = "-"):
    """Reusable title block for cut-list pages."""
    tb_w = 3.2 * inch
    tb_h = 1.3 * inch
    tb_x = PAGE_W - MARGIN - tb_w
    tb_y = MARGIN

    c.setFillColor(CLR_TITLE_BG)
    c.rect(tb_x, tb_y, tb_w, tb_h, fill=1)
    c.setStrokeColor(white)
    c.setLineWidth(MEDIUM)
    c.rect(tb_x, tb_y, tb_w, tb_h)

    fab = TITLE_BLOCK["fabricator"]
    c.setFillColor(CLR_TITLE_TEXT)
    c.setFont("Helvetica-Bold", 7)
    y = tb_y + tb_h - 10
    c.drawCentredString(tb_x + tb_w / 2, y, fab["name"])
    c.setFont("Helvetica", 5)
    y -= 8
    c.drawCentredString(tb_x + tb_w / 2, y, fab["address"])
    y -= 7
    c.drawCentredString(tb_x + tb_w / 2, y, fab["city_state_zip"])
    y -= 7
    c.drawCentredString(tb_x + tb_w / 2, y,
                        f'{fab["phone"]}  |  {fab["website"]}')
    y -= 5
    c.setStrokeColor(HexColor("#444466"))
    c.line(tb_x + 5, y, tb_x + tb_w - 5, y)

    y -= 9
    c.setFont("Helvetica-Bold", 5.5)
    c.drawString(tb_x + 5, y, f'PROJECT: {cfg.project_name}')
    y -= 8
    c.setFont("Helvetica", 5)
    c.drawString(tb_x + 5, y, f'JOB: {cfg.job_code}')
    c.drawString(tb_x + tb_w / 2, y, f'CUSTOMER: {cfg.customer_name}')
    y -= 8
    c.drawString(tb_x + 5, y,
                 f'DATE: {datetime.date.today().strftime("%m/%d/%Y")}')
    c.drawString(tb_x + tb_w / 2, y, f'REV: {revision}')
    y -= 8
    c.drawString(tb_x + 5, y, f'DRAWN: {cfg.drawn_by or "AUTO"}')
    c.drawString(tb_x + tb_w / 2, y,
                 f'SHEET {sheet_num} OF {total_sheets}')
    y -= 10
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(tb_x + tb_w / 2, y, drawing_title)


# ═══════════════════════════════════════════════════════════════════════════════
# SIMPLE PROFILE SKETCHES
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_u_channel_sketch(c, cx: float, cy: float, scale: float = 2.0):
    """U-channel endcap profile (no lips)."""
    inside = 12 * scale
    leg = 4 * scale
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(THICK)
    p = c.beginPath()
    p.moveTo(cx - inside / 2, cy + leg)
    p.lineTo(cx - inside / 2, cy)
    p.lineTo(cx + inside / 2, cy)
    p.lineTo(cx + inside / 2, cy + leg)
    c.drawPath(p, fill=0, stroke=1)

    c.setFont("Helvetica", 4.5)
    c.setFillColor(CLR_DIM)
    c.drawCentredString(cx, cy - 6, f'{12}" INSIDE')
    c.drawString(cx + inside / 2 + 3, cy + leg / 2, f'{4}" LEG')


def _draw_panel_sketch(c, cx: float, cy: float, scale: float = 1.5,
                       label: str = "SPARTAN RIB"):
    """Simplified Spartan Rib panel cross-section with valleys."""
    w = 48 * scale * 0.5  # Half-scale width
    h = 8 * scale
    valleys = 5
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(MEDIUM)
    valley_w = w / valleys
    p = c.beginPath()
    p.moveTo(cx - w / 2, cy)
    for i in range(valleys):
        vx = cx - w / 2 + i * valley_w
        p.lineTo(vx + valley_w * 0.2, cy + h)
        p.lineTo(vx + valley_w * 0.5, cy + h)
        p.lineTo(vx + valley_w * 0.7, cy)
        if i < valleys - 1:
            p.lineTo(vx + valley_w, cy)
    c.drawPath(p, fill=0, stroke=1)

    c.setFont("Helvetica", 4.5)
    c.setFillColor(CLR_DIM)
    c.drawCentredString(cx, cy - 8, label)
    c.drawCentredString(cx, cy - 15, '48" coil → 35.79" coverage')


def _draw_angle_sketch(c, cx: float, cy: float, scale: float = 3.0):
    """2"x2" angle sag rod cross-section."""
    leg = 2 * scale
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(THICK)
    p = c.beginPath()
    p.moveTo(cx, cy + leg)
    p.lineTo(cx, cy)
    p.lineTo(cx + leg, cy)
    c.drawPath(p, fill=0, stroke=1)
    c.setFont("Helvetica", 4.5)
    c.setFillColor(CLR_DIM)
    c.drawCentredString(cx + leg / 2, cy - 6, '2"x2" ANGLE')


def _draw_strap_sketch(c, cx: float, cy: float, scale: float = 2.0):
    """Hurricane strap rectangle."""
    w = 28 * scale * 0.4
    h = 1.5 * scale * 3
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(THICK)
    c.rect(cx - w / 2, cy - h / 2, w, h)
    c.setFont("Helvetica", 4.5)
    c.setFillColor(CLR_DIM)
    c.drawCentredString(cx, cy - h / 2 - 6, '1.5" x 28" STRAP')


# ═══════════════════════════════════════════════════════════════════════════════
# ENDCAP CUT LIST
# ═══════════════════════════════════════════════════════════════════════════════

def _calc_endcap_items(cfg: ShopDrawingConfig) -> List[Dict]:
    """Calculate endcap U-channels for the building."""
    ec = PURLIN_DEFAULTS["endcap"]
    # Building length determines endcap length
    # Endcap spans all purlin lines = building_width
    endcap_length_in = cfg.building_width_ft * 12

    # Check if needs splitting
    max_in = ec["max_length_in"]  # 364" = 30'4"
    items = []

    if endcap_length_in <= max_in:
        items.append({
            "mark": "EC-1",
            "qty": ec["qty_per_building"],
            "description": "Endcap U-Channel",
            "length": _fmt_ft_in(endcap_length_in),
            "material": f'{ec["gauge"]} {ec["material"]}',
            "notes": f'{ec["inside_dim"]}" inside, {ec["leg_height"]}" legs, '
                     f'{ec["tek_screws_per_purlin"]} TEK/purlin, Machine: {ec["machine"]}',
        })
    else:
        # Must split — splice must land on a purlin
        n_pieces = math.ceil(endcap_length_in / max_in)
        piece_len = endcap_length_in / n_pieces
        for i in range(n_pieces):
            items.append({
                "mark": f"EC-{i+1}",
                "qty": ec["qty_per_building"],
                "description": f"Endcap U-Channel (piece {i+1}/{n_pieces})",
                "length": _fmt_ft_in(piece_len),
                "material": f'{ec["gauge"]} {ec["material"]}',
                "notes": f"Splice at purlin, butt joint" if i < n_pieces - 1 else "End piece",
            })

    return items


# ═══════════════════════════════════════════════════════════════════════════════
# ROOFING CUT LIST
# ═══════════════════════════════════════════════════════════════════════════════

def _calc_roofing_items(cfg: ShopDrawingConfig) -> List[Dict]:
    """Calculate roofing panel cut list."""
    coverage_in = ROOFING_DEFAULTS["coverage_in"]
    coverage_ft = coverage_in / 12.0
    overlap_in = cfg.roofing_overlap_in

    # Number of panel runs
    n_runs = math.ceil(cfg.building_length_ft / coverage_ft)

    # Panel split at center purlin
    purlin_sp = cfg.purlin_spacing_ft
    n_purlins = math.floor(cfg.building_width_ft / purlin_sp) + 1
    positions = [i * purlin_sp for i in range(n_purlins)]
    center = cfg.building_width_ft / 2.0
    split_pos = min(positions, key=lambda p: abs(p - center))

    front_in = (split_pos + overlap_in / 12.0) * 12
    back_in = (cfg.building_width_ft - split_pos) * 12

    items = [
        {
            "mark": "RF-1",
            "qty": n_runs,
            "description": "Roof Panel — Front Half",
            "length": _fmt_ft_in(front_in),
            "material": "48\" 29GA G50 Spartan Rib",
            "notes": f"Split @ {split_pos:.1f}' purlin + {overlap_in}\" overlap",
        },
        {
            "mark": "RF-2",
            "qty": n_runs,
            "description": "Roof Panel — Back Half",
            "length": _fmt_ft_in(back_in),
            "material": "48\" 29GA G50 Spartan Rib",
            "notes": f"Split @ {split_pos:.1f}' purlin, no overlap",
        },
    ]

    # Stacking info
    panel_lbs_per_ft = 2.81
    front_wt = front_in / 12 * panel_lbs_per_ft
    back_wt = back_in / 12 * panel_lbs_per_ft

    max_per_stack = min(
        PANEL_STACK_LIMITS["max_sheets"],
        int(PANEL_STACK_LIMITS["max_weight_lbs"] / max(front_wt, back_wt))
    )
    items.append({
        "mark": "—",
        "qty": "—",
        "description": "STACKING RULE",
        "length": "—",
        "material": "—",
        "notes": f"Max {max_per_stack} sheets/stack "
                 f"({PANEL_STACK_LIMITS['max_weight_lbs']} lbs or "
                 f"{PANEL_STACK_LIMITS['max_sheets']} sheets limit)",
    })

    return items


# ═══════════════════════════════════════════════════════════════════════════════
# WALL PANEL CUT LIST
# ═══════════════════════════════════════════════════════════════════════════════

def _calc_wall_items(cfg: ShopDrawingConfig) -> List[Dict]:
    """Calculate wall panel and girt cut list."""
    items = []
    if not cfg.has_back_wall and not cfg.has_side_walls:
        return items

    use_z = cfg.wall_girt_type == "z"
    panel_length_in = calc_wall_panel_length_in(
        cfg.clear_height_ft,
        cfg.wall_panel_ground_clearance_in,
        use_z
    )

    coverage_in = WALL_DEFAULTS["panel_coverage_in"]
    coverage_ft = coverage_in / 12.0

    if cfg.has_back_wall:
        n_panels = math.ceil(cfg.building_length_ft / coverage_ft)
        items.append({
            "mark": "WP-BK",
            "qty": n_panels,
            "description": "Wall Panel — Back Wall (vertical)",
            "length": _fmt_ft_in(panel_length_in),
            "material": "48\" 29GA G50 Spartan Rib",
            "notes": f"{cfg.building_length_ft:.0f}' wall / "
                     f"{coverage_in}\" coverage = {n_panels} panels",
        })

    if cfg.has_side_walls:
        n_panels = math.ceil(cfg.building_length_ft / coverage_ft) * 2
        items.append({
            "mark": "WP-SD",
            "qty": n_panels,
            "description": "Wall Panel — Side Walls x2 (vertical)",
            "length": _fmt_ft_in(panel_length_in),
            "material": "48\" 29GA G50 Spartan Rib",
            "notes": f"2 sides x {cfg.building_length_ft:.0f}' = "
                     f"{n_panels} panels total",
        })

    # Warning if panel > 20'
    if panel_length_in > 20 * 12:
        items.append({
            "mark": "⚠",
            "qty": "—",
            "description": "WARNING",
            "length": "—",
            "material": "—",
            "notes": f"Wall panel {_fmt_ft_in(panel_length_in)} > 20' — proceed with caution",
        })

    return items


# ═══════════════════════════════════════════════════════════════════════════════
# SAG ROD CUT LIST
# ═══════════════════════════════════════════════════════════════════════════════

def _calc_sag_rod_items(cfg: ShopDrawingConfig) -> List[Dict]:
    """Calculate sag rod cut list."""
    # Sag rods split at panel seam, 2 per rafter, 2 pieces each = 4 per rafter
    purlin_sp = cfg.purlin_spacing_ft
    n_purlins = math.floor(cfg.building_width_ft / purlin_sp) + 1
    positions = [i * purlin_sp for i in range(n_purlins)]
    center = cfg.building_width_ft / 2.0
    split_pos = min(positions, key=lambda p: abs(p - center))

    overlap_in = 3.0
    front_in = split_pos * 12 + overlap_in
    back_in = (cfg.building_width_ft - split_pos) * 12

    n_rafters = cfg.n_frames
    n_rods = n_rafters * SAG_ROD_DEFAULTS["qty_per_rafter"]
    n_pieces = n_rods * SAG_ROD_DEFAULTS["pieces_per_rod"]

    items = [
        {
            "mark": "SR-F",
            "qty": n_rods,
            "description": "Sag Rod — Front Half",
            "length": _fmt_ft_in(front_in),
            "material": "4\" 16GA G90 → 2\"x2\" angle",
            "notes": f"Split @ {split_pos:.1f}' purlin + {overlap_in}\" overlap | "
                     f"Machine: ANGLE",
        },
        {
            "mark": "SR-B",
            "qty": n_rods,
            "description": "Sag Rod — Back Half",
            "length": _fmt_ft_in(back_in),
            "material": "4\" 16GA G90 → 2\"x2\" angle",
            "notes": f"Split @ {split_pos:.1f}' purlin | "
                     f"2 TEK per purlin, attach to underside",
        },
    ]

    # Bundle info
    bundle_size = SAG_ROD_DEFAULTS["bundle_size"]
    n_bundles = math.ceil(n_pieces / bundle_size)
    items.append({
        "mark": "—",
        "qty": "—",
        "description": "BUNDLING",
        "length": "—",
        "material": "—",
        "notes": f"{n_pieces} total pieces → {n_bundles} bundles of {bundle_size} "
                 f"(1 sticker per bundle)",
    })

    return items


# ═══════════════════════════════════════════════════════════════════════════════
# HURRICANE STRAP CUT LIST
# ═══════════════════════════════════════════════════════════════════════════════

def _calc_strap_items(cfg: ShopDrawingConfig) -> List[Dict]:
    """Calculate hurricane strap cut list."""
    n_rafters = cfg.n_frames
    n_straps = n_rafters * STRAP_DEFAULTS["qty_per_rafter"]
    length_in = STRAP_DEFAULTS["length_in"]
    bundle_size = STRAP_DEFAULTS["bundle_size"]
    n_bundles = math.ceil(n_straps / bundle_size)

    items = [
        {
            "mark": "HS-1",
            "qty": n_straps,
            "description": "Hurricane Strap",
            "length": f'{length_in}"',
            "material": f'{STRAP_DEFAULTS["width_in"]}" {STRAP_DEFAULTS["gauge"]} '
                        f'{STRAP_DEFAULTS["material"]}',
            "notes": f'{STRAP_DEFAULTS["qty_per_rafter"]}/rafter × '
                     f'{n_rafters} rafters = {n_straps} | Machine: {STRAP_DEFAULTS["machine"]}',
        },
        {
            "mark": "—",
            "qty": "—",
            "description": "BUNDLING",
            "length": "—",
            "material": "—",
            "notes": f"{n_straps} straps → {n_bundles} bundles of {bundle_size}",
        },
    ]
    return items


# ═══════════════════════════════════════════════════════════════════════════════
# SPLICE PLATE CUT LIST (when rafters > 53')
# ═══════════════════════════════════════════════════════════════════════════════

def _calc_splice_items(cfg: ShopDrawingConfig) -> List[Dict]:
    """Calculate splice plate cut list (only if needed)."""
    from shop_drawings.config import calc_rafter_length
    use_z = cfg.raft_purlin_type == "z"
    raft_len = calc_rafter_length(cfg.building_width_ft,
                                  cfg.raft_roofing_overhang_ft, use_z)

    if raft_len <= RAFTER_DEFAULTS["max_rafter_length_ft"]:
        return []  # No splice needed

    sp = RAFTER_DEFAULTS["splice_plate"]
    n_rafters = cfg.n_frames
    n_plates = n_rafters * 2  # 2 per rafter (one each side of web)
    n_pairs = n_rafters  # 1 pair per rafter

    items = [
        {
            "mark": "SP-1",
            "qty": n_plates,
            "description": "Splice Plate (roll formed)",
            "length": sp["length"],
            "material": f'{sp["material"]} {sp["width"]}',
            "notes": f"Machine: {sp['machine']} | {sp['fabrication']} → "
                     f"Field: {sp['field_install']} | 8x #10 TEK",
        },
        {
            "mark": "—",
            "qty": "—",
            "description": "STICKER RULE",
            "length": "—",
            "material": "—",
            "notes": f"1 sticker per pair ({n_pairs} pairs for {n_rafters} rafters)",
        },
    ]
    return items


# ═══════════════════════════════════════════════════════════════════════════════
# COMBINED CUT-LIST PAGE GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

def generate_cutlist_drawing(
    cfg: ShopDrawingConfig,
    output_path: Optional[str] = None,
    revision: str = "-",
) -> bytes:
    """
    Generate a combined cut-list PDF with all simple components.
    May span multiple pages if needed.
    """
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=landscape(letter))
    c.setTitle("Cut Lists — Shop Drawing")

    draw_area_w = PAGE_W - 2 * MARGIN
    draw_area_h = PAGE_H - 2 * MARGIN
    bar_h = 1.5 * inch

    # ── PAGE 1: Endcaps + Roofing ──
    _draw_border(c)

    endcap_items = _calc_endcap_items(cfg)
    roofing_items = _calc_roofing_items(cfg)

    # Top half: Endcap cut list + U-channel sketch
    top_h = (draw_area_h - bar_h) * 0.5
    table_w = draw_area_w * 0.65
    sketch_w = draw_area_w * 0.35

    _draw_cutlist_table(c, endcap_items, MARGIN,
                        MARGIN + bar_h + top_h, table_w, top_h,
                        "ENDCAP CUT LIST")
    _draw_u_channel_sketch(c, MARGIN + table_w + sketch_w / 2,
                           MARGIN + bar_h + top_h + top_h * 0.6, scale=2.5)

    # Label
    c.setFont("Helvetica-Bold", 6)
    c.setFillColor(black)
    c.drawCentredString(MARGIN + table_w + sketch_w / 2,
                        MARGIN + bar_h + top_h + top_h * 0.25,
                        "U-CHANNEL ENDCAP PROFILE")

    # Bottom half: Roofing cut list + panel sketch
    _draw_cutlist_table(c, roofing_items, MARGIN,
                        MARGIN + bar_h, table_w, top_h,
                        "ROOFING CUT LIST")
    _draw_panel_sketch(c, MARGIN + table_w + sketch_w / 2,
                       MARGIN + bar_h + top_h * 0.6, scale=2.0,
                       label="SPARTAN RIB ROOF PANEL")

    # Divider
    c.setStrokeColor(CLR_GRID)
    c.setLineWidth(HAIR)
    c.setDash([4, 4])
    c.line(MARGIN, MARGIN + bar_h + top_h,
           MARGIN + draw_area_w, MARGIN + bar_h + top_h)
    c.setDash([])

    # Bottom bar
    notes_w = draw_area_w * 0.55
    _draw_standard_notes(c, MARGIN, MARGIN, notes_w, bar_h)
    _draw_cutlist_title_block(c, cfg, "ENDCAPS & ROOFING", revision=revision)

    c.showPage()

    # ── PAGE 2: Sag Rods + Straps + Wall Panels + Splice Plates ──
    _draw_border(c)

    sag_items = _calc_sag_rod_items(cfg)
    strap_items = _calc_strap_items(cfg)
    wall_items = _calc_wall_items(cfg)
    splice_items = _calc_splice_items(cfg)

    views_h = draw_area_h - bar_h

    # Combine all items into sections
    all_items = []

    # Sag rods section
    if sag_items:
        all_items.append({"mark": "═══", "qty": "", "description": "SAG RODS",
                          "length": "", "material": "", "notes": ""})
        all_items.extend(sag_items)

    # Straps section
    if strap_items:
        all_items.append({"mark": "═══", "qty": "", "description": "HURRICANE STRAPS",
                          "length": "", "material": "", "notes": ""})
        all_items.extend(strap_items)

    # Wall panels
    if wall_items:
        all_items.append({"mark": "═══", "qty": "", "description": "WALL PANELS",
                          "length": "", "material": "", "notes": ""})
        all_items.extend(wall_items)

    # Splice plates
    if splice_items:
        all_items.append({"mark": "═══", "qty": "", "description": "SPLICE PLATES",
                          "length": "", "material": "", "notes": ""})
        all_items.extend(splice_items)

    # If no items at all, add placeholder
    if not all_items:
        all_items.append({
            "mark": "—", "qty": "—",
            "description": "No additional components for this project",
            "length": "—", "material": "—", "notes": "",
        })

    # Table takes left 65%
    table_w = draw_area_w * 0.65
    sketch_w = draw_area_w * 0.35

    _draw_cutlist_table(c, all_items, MARGIN,
                        MARGIN + bar_h, table_w, views_h,
                        "ADDITIONAL COMPONENTS CUT LIST")

    # Profile sketches on right side
    sketch_cx = MARGIN + table_w + sketch_w / 2
    _draw_angle_sketch(c, sketch_cx, MARGIN + bar_h + views_h * 0.75, scale=4.0)
    c.setFont("Helvetica-Bold", 5)
    c.setFillColor(black)
    c.drawCentredString(sketch_cx, MARGIN + bar_h + views_h * 0.75 - 18,
                        "SAG ROD PROFILE")

    _draw_strap_sketch(c, sketch_cx, MARGIN + bar_h + views_h * 0.45, scale=3.0)
    c.setFont("Helvetica-Bold", 5)
    c.drawCentredString(sketch_cx, MARGIN + bar_h + views_h * 0.45 - 18,
                        "HURRICANE STRAP")

    if wall_items:
        _draw_panel_sketch(c, sketch_cx, MARGIN + bar_h + views_h * 0.2,
                           scale=1.5, label="WALL PANEL (VERTICAL)")

    # Bottom bar
    notes_w = draw_area_w * 0.55
    _draw_standard_notes(c, MARGIN, MARGIN, notes_w, bar_h)
    _draw_cutlist_title_block(c, cfg, "COMPONENTS & HARDWARE",
                              sheet_num=2, total_sheets=2, revision=revision)

    c.save()
    pdf_bytes = buf.getvalue()

    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)

    return pdf_bytes
