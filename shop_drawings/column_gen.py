"""
Column Shop Drawing PDF Generator
Produces 8.5"x11" landscape PDF with 4 views:
  - Front View: full column elevation with dimensions
  - Side View: 90° rotation showing depth
  - Section A-A: cross-section through body (box beam + rebar)
  - Section B-B: cross-section at cap plate (bolt holes + gussets)
Plus: title block, revision block, BOM table, WPS callouts, standard notes.
"""

import math
import io
import os
import datetime
from typing import Dict, List, Optional, Tuple

from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.units import inch
from reportlab.lib.colors import (
    black, white, Color, HexColor,
    lightgrey, grey, red, blue
)
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

from shop_drawings.config import (
    COLUMN_DEFAULTS, WPS_CODES, STANDARD_NOTES,
    TITLE_BLOCK, ABBREVIATIONS, DRAWING_OUTPUT,
    ShopDrawingConfig,
)


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

PAGE_W = 11 * inch
PAGE_H = 8.5 * inch
MARGIN = 0.4 * inch

# Drawing area bounds
DRAW_LEFT = MARGIN
DRAW_RIGHT = PAGE_W - MARGIN
DRAW_TOP = PAGE_H - MARGIN
DRAW_BOTTOM = MARGIN + 1.6 * inch  # Leave room for title block

# Line weights
THICK = 1.5       # Object outlines
MEDIUM = 0.8      # Dimension lines, section cuts
THIN = 0.4        # Hidden lines, hatching
HAIR = 0.25       # Leaders, text lines

# Colors
CLR_OBJECT = black
CLR_DIM = HexColor("#333333")
CLR_HIDDEN = HexColor("#888888")
CLR_SECTION_CUT = red
CLR_WELD = HexColor("#0055AA")
CLR_REBAR = HexColor("#CC4400")
CLR_NOPAINT = HexColor("#FF6600")
CLR_TITLE_BG = HexColor("#1A1A2E")
CLR_TITLE_TEXT = white
CLR_GRID = HexColor("#CCCCCC")


# ═══════════════════════════════════════════════════════════════════════════════
# DRAWING PRIMITIVES
# ═══════════════════════════════════════════════════════════════════════════════

def draw_dimension_h(c, x1, x2, y, offset, label, font_size=6):
    """Horizontal dimension line with arrows and centered label."""
    dy = y + offset
    c.setStrokeColor(CLR_DIM)
    c.setLineWidth(HAIR)
    # Extension lines
    c.line(x1, y, x1, dy + 3)
    c.line(x2, y, x2, dy + 3)
    # Dimension line
    c.line(x1, dy, x2, dy)
    # Arrows (simple tick marks)
    _draw_tick(c, x1, dy, "right")
    _draw_tick(c, x2, dy, "left")
    # Label
    mid = (x1 + x2) / 2
    c.setFillColor(CLR_DIM)
    c.setFont("Helvetica", font_size)
    c.drawCentredString(mid, dy + 2, label)


def draw_dimension_v(c, x, y1, y2, offset, label, font_size=6):
    """Vertical dimension line with arrows and centered label."""
    dx = x + offset
    c.setStrokeColor(CLR_DIM)
    c.setLineWidth(HAIR)
    # Extension lines
    c.line(x, y1, dx + 3, y1)
    c.line(x, y2, dx + 3, y2)
    # Dimension line
    c.line(dx, y1, dx, y2)
    # Arrows
    _draw_tick_v(c, dx, y1, "up")
    _draw_tick_v(c, dx, y2, "down")
    # Label (rotated)
    mid = (y1 + y2) / 2
    c.saveState()
    c.translate(dx - 3, mid)
    c.rotate(90)
    c.setFillColor(CLR_DIM)
    c.setFont("Helvetica", font_size)
    c.drawCentredString(0, 0, label)
    c.restoreState()


def _draw_tick(c, x, y, direction):
    """Small arrowhead tick on dimension line."""
    c.setLineWidth(THIN)
    L = 4
    if direction == "right":
        c.line(x, y, x + L, y + 2)
        c.line(x, y, x + L, y - 2)
    else:
        c.line(x, y, x - L, y + 2)
        c.line(x, y, x - L, y - 2)


def _draw_tick_v(c, x, y, direction):
    """Vertical arrowhead tick."""
    c.setLineWidth(THIN)
    L = 4
    if direction == "up":
        c.line(x, y, x - 2, y + L)
        c.line(x, y, x + 2, y + L)
    else:
        c.line(x, y, x - 2, y - L)
        c.line(x, y, x + 2, y - L)


def draw_leader(c, x1, y1, x2, y2, label, font_size=5.5, align="left"):
    """Leader line from a point to a label."""
    c.setStrokeColor(CLR_DIM)
    c.setLineWidth(HAIR)
    c.line(x1, y1, x2, y2)
    # Small dot at origin
    c.setFillColor(CLR_DIM)
    c.circle(x1, y1, 1.2, fill=1, stroke=0)
    c.setFont("Helvetica", font_size)
    if align == "left":
        c.drawString(x2 + 2, y2 - 2, label)
    else:
        c.drawRightString(x2 - 2, y2 - 2, label)


def draw_section_marker(c, x, y, label, size=10):
    """Section cut circle marker (like A-A)."""
    c.setStrokeColor(CLR_SECTION_CUT)
    c.setLineWidth(MEDIUM)
    c.circle(x, y, size, fill=0)
    c.setFillColor(CLR_SECTION_CUT)
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(x, y - 2.5, label)


def draw_weld_symbol(c, x, y, wps_code, size=5):
    """Simplified weld symbol with WPS code."""
    c.setStrokeColor(CLR_WELD)
    c.setFillColor(CLR_WELD)
    c.setLineWidth(THIN)
    # Small V symbol
    c.line(x - size, y, x, y - size)
    c.line(x, y - size, x + size, y)
    c.setFont("Helvetica", 4.5)
    c.drawCentredString(x, y + 2, f'WPS-"{wps_code}"')


# ═══════════════════════════════════════════════════════════════════════════════
# COLUMN DRAWING DATA
# ═══════════════════════════════════════════════════════════════════════════════

def _fmt_ft_in(total_inches: float) -> str:
    """Format inches as X'-Y  Z/16\" fractional."""
    neg = total_inches < 0
    total_inches = abs(total_inches)
    feet = int(total_inches // 12)
    remain = total_inches - feet * 12
    whole_in = int(remain)
    frac = remain - whole_in
    # Round to nearest 1/16
    sixteenths = round(frac * 16)
    if sixteenths == 16:
        whole_in += 1
        sixteenths = 0
    if whole_in >= 12:
        feet += 1
        whole_in -= 12

    prefix = "-" if neg else ""
    if sixteenths == 0:
        if whole_in == 0 and feet > 0:
            return f'{prefix}{feet}\'-0"'
        elif feet == 0:
            return f'{prefix}{whole_in}"'
        else:
            return f'{prefix}{feet}\'-{whole_in}"'
    else:
        # Simplify fraction by GCD
        num, den = sixteenths, 16
        from math import gcd
        g = gcd(num, den)
        num, den = num // g, den // g
        if feet == 0:
            return f'{prefix}{whole_in}-{num}/{den}"'
        else:
            return f'{prefix}{feet}\'-{whole_in} {num}/{den}"'


def _calc_column_data(cfg: ShopDrawingConfig, col_index: int = 0) -> Dict:
    """
    Calculate all column dimensions and properties for drawing.
    Returns dict with all values needed to render.

    Updated: uses calc_rafter_columns() for column position when available,
    falling back to legacy tee/2post calculation for backward compatibility.
    """
    slope_deg = cfg.roof_pitch_deg
    tan_slope = math.tan(math.radians(slope_deg))

    # Column height: use rafter column positions if available, else legacy
    column_mode = getattr(cfg, 'raft_column_mode', None)
    if column_mode and column_mode != '':
        # New mode: use calc_rafter_columns() for accurate per-position heights
        from calc.bom import calc_rafter_columns, calc_column_height_at
        _n_cols, col_positions_in = calc_rafter_columns(
            cfg.building_width_ft,
            column_mode=column_mode,
            column_spacing_ft=getattr(cfg, 'raft_column_spacing_ft', 25.0),
            column_count_manual=getattr(cfg, 'raft_column_count_manual', 1),
            column_positions_manual=getattr(cfg, 'raft_column_positions_manual', ''),
            include_back_wall=cfg.has_back_wall,
            front_col_position_ft=getattr(cfg, 'raft_front_col_position_ft', 0.0),
        )
        # Use the position for this specific column index
        if col_index < len(col_positions_in):
            dist_ft = col_positions_in[col_index] / 12.0
        else:
            dist_ft = col_positions_in[-1] / 12.0 if col_positions_in else cfg.building_width_ft / 2.0
    else:
        # Legacy fallback
        if cfg.frame_type == "tee":
            dist_ft = cfg.building_width_ft / 2.0
        else:
            dist_ft = cfg.building_width_ft / 3.0

    angle_add_ft = dist_ft * tan_slope
    total_length_ft = (cfg.clear_height_ft + angle_add_ft
                       + cfg.embedment_ft + cfg.column_buffer_ft)
    total_length_in = total_length_ft * 12.0

    # Cap plate angle from roof pitch
    cap_angle_deg = slope_deg

    # Rebar length
    if cfg.col_reinforced:
        rebar_length_ft = cfg.footing_depth_ft + 8.0
    else:
        rebar_length_ft = cfg.footing_depth_ft - cfg.embedment_ft

    rebar_length_in = rebar_length_ft * 12.0

    # Gusset hypotenuse (approximate from 6x6 triangle + pitch adjustment)
    # uphill = longer, downhill = shorter
    gusset_leg = cfg.col_gusset_leg_in
    base_hyp = math.sqrt(2) * gusset_leg  # 8.485" for 6x6
    # Adjust by pitch
    uphill_hyp = base_hyp * (1 + math.sin(math.radians(slope_deg)) * 0.3)
    downhill_hyp = base_hyp * (1 - math.sin(math.radians(slope_deg)) * 0.3)

    # Column weight (2 CEE sections welded)
    lbs_per_lft = 10.83  # From COILS c_section_23
    weight_lbs = total_length_ft * 2 * lbs_per_lft

    # Generate ship mark
    mark = f"C{col_index + 1}"

    return {
        "mark": mark,
        "total_length_in": total_length_in,
        "total_length_ft": total_length_ft,
        "clear_height_ft": cfg.clear_height_ft,
        "clear_height_in": cfg.clear_height_ft * 12,
        "angle_add_in": angle_add_ft * 12,
        "embedment_in": cfg.embedment_ft * 12,
        "buffer_in": cfg.column_buffer_ft * 12,
        "cap_angle_deg": cap_angle_deg,
        "slope_deg": slope_deg,
        "cee_size": "14x4x10GA",
        "material_grade": cfg.col_material_grade,
        "cap_plate_thickness": cfg.col_cap_plate_thickness,
        "cap_plate_width_in": cfg.col_cap_plate_width_in,
        "cap_plate_length_in": cfg.col_cap_plate_length_in,
        "bolt_hole_dia": cfg.col_bolt_hole_dia,
        "gusset_thickness": cfg.col_gusset_thickness,
        "gusset_leg_in": gusset_leg,
        "uphill_hyp_in": uphill_hyp,
        "downhill_hyp_in": downhill_hyp,
        "rebar_size": cfg.col_rebar_size,
        "rebar_reinforced": cfg.col_reinforced,
        "rebar_length_in": rebar_length_in,
        "rebar_qty": 4,  # Always 4 per column
        "stitch_weld": COLUMN_DEFAULTS["stitch_weld"],
        "connection_bolts": cfg.col_connection_bolts,
        "weight_lbs": weight_lbs,
        "dist_from_eave_ft": dist_ft,
        "frame_type": cfg.frame_type,
        "column_mode": getattr(cfg, 'raft_column_mode', 'auto'),
        "width_in": 14.0,   # Box beam width
        "depth_in": 4.0,    # CEE flange depth (becomes box depth)
        # Actually width is 14" and box is 14x~8" (two 4" flanges)
        # The box is formed by two 14x4 CEEs back to back = 14" wide x 8" deep
        "box_width": 14.0,
        "box_depth": 8.0,   # Two 4" flanges
    }


# ═══════════════════════════════════════════════════════════════════════════════
# FRONT VIEW
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_front_view(c, data: Dict, ox: float, oy: float,
                     view_w: float, view_h: float):
    """
    Draw front elevation of column.
    ox, oy = origin (bottom-left of view area)
    view_w, view_h = available space
    """
    total_in = data["total_length_in"]

    # Scale: fit column in view with margins
    col_margin = 25  # pts margin inside view
    avail_h = view_h - 2 * col_margin
    avail_w = view_w - 2 * col_margin
    scale = min(avail_h / total_in, avail_w / 40)  # 40" gives room for 14" beam + dims

    # Column drawing dimensions
    col_w = data["box_width"] * scale
    col_h = total_in * scale

    # Center column in view
    cx = ox + view_w / 2
    col_left = cx - col_w / 2
    col_right = cx + col_w / 2
    col_bottom = oy + col_margin
    col_top = col_bottom + col_h

    # ── Column body outline ──
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(THICK)
    c.rect(col_left, col_bottom, col_w, col_h)

    # ── Cap plate at top ──
    cap_w = data["cap_plate_length_in"] * scale  # 26" plate wider than column
    cap_h = 4 * scale  # Exaggerated thickness for visibility
    cap_left = cx - cap_w / 2
    c.setFillColor(HexColor("#E8E8E8"))
    c.rect(cap_left, col_top - 1, cap_w, cap_h, fill=1)
    c.setFillColor(black)

    # Cap plate label
    c.setFont("Helvetica", 5)
    c.setFillColor(CLR_DIM)
    c.drawCentredString(cx, col_top + cap_h + 3,
                        f'PL {data["cap_plate_thickness"]} x '
                        f'{data["cap_plate_width_in"]:.0f}" x '
                        f'{data["cap_plate_length_in"]:.0f}" A572 Gr 50')

    # ── Bolt holes (4 dots on cap plate) ──
    c.setFillColor(CLR_OBJECT)
    bolt_spacing_x = 8 * scale  # approximate bolt pattern
    bolt_spacing_y = 2 * scale
    bolt_cy = col_top + cap_h / 2
    for bx in [-bolt_spacing_x/2, bolt_spacing_x/2]:
        c.circle(cx + bx, bolt_cy, 1.5, fill=1)

    # ── Gusset triangles (2 per side visible in front view) ──
    gusset_h = data["gusset_leg_in"] * scale
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(MEDIUM)

    # Left gussets (uphill side — longer hypotenuse)
    gx1 = col_left
    gy1 = col_top
    c.line(gx1, gy1, gx1 - gusset_h * 0.7, gy1)
    c.line(gx1, gy1, gx1, gy1 - gusset_h)
    c.line(gx1 - gusset_h * 0.7, gy1, gx1, gy1 - gusset_h)

    # Right gussets (downhill side — shorter hypotenuse)
    gx2 = col_right
    c.line(gx2, gy1, gx2 + gusset_h * 0.7, gy1)
    c.line(gx2, gy1, gx2, gy1 - gusset_h)
    c.line(gx2 + gusset_h * 0.7, gy1, gx2, gy1 - gusset_h)

    # Gusset labels
    c.setFont("Helvetica", 4.5)
    c.setFillColor(CLR_DIM)
    draw_leader(c, gx1 - gusset_h * 0.35, gy1 - gusset_h * 0.3,
                gx1 - gusset_h - 8, gy1 - gusset_h * 0.3,
                f'PL {data["gusset_thickness"]} GUSSET (TYP)', align="right")

    # ── Stitch weld pattern ──
    sw = data["stitch_weld"]
    weld_spacing = 36 * scale  # 36" OC pattern spacing
    n_welds = max(2, int(col_h / weld_spacing))
    c.setStrokeColor(CLR_WELD)
    c.setLineWidth(THIN)
    for i in range(1, n_welds):
        wy = col_bottom + i * (col_h / n_welds)
        # Small weld marks on both sides
        for wx in [col_left, col_right]:
            c.line(wx - 3, wy - 2, wx, wy + 2)
            c.line(wx, wy + 2, wx + 3, wy - 2)

    # Stitch weld callout
    sw_y = col_bottom + col_h * 0.6
    draw_leader(c, col_right + 2, sw_y,
                col_right + col_margin + 15, sw_y + 10,
                f'STITCH WELD {sw["size"]} {sw["pattern"]} WPS-"B"',
                font_size=5)

    # End weld callout
    ew_y = col_bottom + 12 * scale
    draw_leader(c, col_right + 2, ew_y,
                col_right + col_margin + 15, ew_y - 8,
                f'{sw["end_weld"]} WPS-"B"',
                font_size=4.5)

    # ── Rebar ──
    rebar_len_scaled = data["rebar_length_in"] * scale
    rebar_start = col_bottom  # Starts at bottom (embedded in footing)
    rebar_end = min(rebar_start + rebar_len_scaled, col_top)

    c.setStrokeColor(CLR_REBAR)
    c.setLineWidth(MEDIUM)
    c.setLineCap(1)  # Round cap
    c.setDash([4, 3])

    rebar_inset = 3 * scale if data["rebar_reinforced"] else -3 * scale
    for rx in [col_left + rebar_inset, col_right - rebar_inset]:
        c.line(rx, rebar_start, rx, rebar_end)
    c.setDash([])

    # Rebar callout
    rb_label = (f'{data["rebar_size"]} A706 REBAR x 4 EA '
                f'({_fmt_ft_in(data["rebar_length_in"])} LONG)')
    if data["rebar_reinforced"]:
        rb_label += " — INSIDE"
    else:
        rb_label += " — OUTSIDE w/ 6\" WELD"

    draw_leader(c, col_left + rebar_inset, rebar_end - 10,
                col_left - col_margin - 20, rebar_end + 5,
                rb_label, font_size=4.5, align="right")

    # Rebar WPS callout
    draw_weld_symbol(c, col_left + rebar_inset + 8, rebar_end - 3, "D")

    # ── Column body material callout ──
    mat_y = col_bottom + col_h * 0.45
    c.setFillColor(CLR_DIM)
    c.setFont("Helvetica-Bold", 5.5)
    c.saveState()
    c.translate(cx, mat_y)
    c.rotate(90)
    c.drawCentredString(0, 3, f'CEE {data["cee_size"]} {data["material_grade"]}')
    c.restoreState()

    # ── DO NOT PAINT zones at ends ──
    nopaint_h = 6 * scale  # 6" at each end
    c.setStrokeColor(CLR_NOPAINT)
    c.setLineWidth(THIN)
    c.setDash([2, 2])
    # Bottom
    c.rect(col_left + 1, col_bottom, col_w - 2, nopaint_h)
    # Top
    c.rect(col_left + 1, col_top - nopaint_h, col_w - 2, nopaint_h)
    c.setDash([])

    # "DO NOT PAINT" label
    c.setFont("Helvetica", 3.5)
    c.setFillColor(CLR_NOPAINT)
    c.drawCentredString(cx, col_bottom + nopaint_h + 2, "DO NOT PAINT")
    c.drawCentredString(cx, col_top - nopaint_h - 5, "DO NOT PAINT")

    # ── Embedment line ──
    embed_y = col_bottom + data["embedment_in"] * scale
    c.setStrokeColor(CLR_DIM)
    c.setLineWidth(THIN)
    c.setDash([6, 3])
    c.line(col_left - 10, embed_y, col_right + 10, embed_y)
    c.setDash([])
    c.setFont("Helvetica", 4.5)
    c.setFillColor(CLR_DIM)
    c.drawString(col_right + 12, embed_y - 2, "GRADE LINE")

    # ── Section cut markers ──
    # A-A at mid-height
    aa_y = col_bottom + col_h * 0.4
    c.setStrokeColor(CLR_SECTION_CUT)
    c.setLineWidth(MEDIUM)
    c.setDash([8, 3, 2, 3])
    c.line(col_left - 15, aa_y, col_right + 15, aa_y)
    c.setDash([])
    draw_section_marker(c, col_left - 20, aa_y, "A")
    draw_section_marker(c, col_right + 20, aa_y, "A")

    # B-B at cap plate
    bb_y = col_top + 1
    c.setStrokeColor(CLR_SECTION_CUT)
    c.setLineWidth(MEDIUM)
    c.setDash([8, 3, 2, 3])
    c.line(col_left - 15, bb_y, col_right + 15, bb_y)
    c.setDash([])
    draw_section_marker(c, col_left - 20, bb_y, "B")
    draw_section_marker(c, col_right + 20, bb_y, "B")

    # ── DIMENSIONS ──

    # Total length (left side)
    draw_dimension_v(c, col_left, col_bottom, col_top, -35,
                     f'TOTAL: {_fmt_ft_in(data["total_length_in"])}',
                     font_size=6)

    # Breakdown dimensions (far left, stacked)
    # Embedment
    embed_top = col_bottom + data["embedment_in"] * scale
    draw_dimension_v(c, col_left, col_bottom, embed_top, -55,
                     f'{_fmt_ft_in(data["embedment_in"])} EMBED',
                     font_size=5)

    # Clear height
    clear_top = embed_top + data["clear_height_in"] * scale
    draw_dimension_v(c, col_left, embed_top, clear_top, -55,
                     f'{_fmt_ft_in(data["clear_height_in"])} CLR',
                     font_size=5)

    # Angle addition + buffer
    ang_buf = data["angle_add_in"] + data["buffer_in"]
    draw_dimension_v(c, col_left, clear_top, col_top, -55,
                     f'{_fmt_ft_in(ang_buf)} ANG+BUF',
                     font_size=5)

    # Width dimension (top)
    draw_dimension_h(c, col_left, col_right, col_top + cap_h + 8, 12,
                     f'{data["box_width"]:.0f}"', font_size=6)

    # ── View label ──
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(black)
    c.drawCentredString(cx, oy + 5, "FRONT VIEW")

    # ── Cold Galv note ──
    c.setFont("Helvetica", 4.5)
    c.setFillColor(CLR_WELD)
    cg_y = col_bottom + col_h * 0.25
    draw_leader(c, col_left + col_w * 0.5, cg_y,
                col_right + col_margin + 15, cg_y - 15,
                "COLD GALV ALL PLAIN STEEL & WELDS", font_size=4.5)

    # Cap plate end weld
    draw_weld_symbol(c, cx - 10, col_top + 2, "F")


def _draw_side_view(c, data: Dict, ox: float, oy: float,
                    view_w: float, view_h: float):
    """
    Side elevation (90° rotation) showing box depth.
    """
    total_in = data["total_length_in"]

    col_margin = 20
    avail_h = view_h - 2 * col_margin
    scale = min(avail_h / total_in, (view_w - 2 * col_margin) / 30)

    col_w = data["box_depth"] * scale  # 8" depth shown
    col_h = total_in * scale

    cx = ox + view_w / 2
    col_left = cx - col_w / 2
    col_right = cx + col_w / 2
    col_bottom = oy + col_margin
    col_top = col_bottom + col_h

    # Column body
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(THICK)
    c.rect(col_left, col_bottom, col_w, col_h)

    # Center stitch line (hidden — shows inner seam)
    c.setStrokeColor(CLR_HIDDEN)
    c.setLineWidth(THIN)
    c.setDash([3, 2])
    c.line(cx, col_bottom + 5, cx, col_top - 5)
    c.setDash([])

    # Cap plate (side view — thin rectangle)
    cap_h = 4 * scale
    cap_w_side = data["cap_plate_width_in"] * scale
    c.setStrokeColor(CLR_OBJECT)
    c.setFillColor(HexColor("#E8E8E8"))
    c.setLineWidth(MEDIUM)
    cap_left = cx - cap_w_side / 2
    c.rect(cap_left, col_top - 1, cap_w_side, cap_h, fill=1)
    c.setFillColor(black)

    # Gussets (side view — appear as rectangles)
    gusset_h = data["gusset_leg_in"] * scale
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(MEDIUM)
    gw = 2 * scale  # gusset plate thickness
    # Left gusset
    c.rect(col_left - gw, col_top - gusset_h, gw, gusset_h)
    # Right gusset
    c.rect(col_right, col_top - gusset_h, gw, gusset_h)

    # Depth dimension
    draw_dimension_h(c, col_left, col_right, col_top + cap_h + 5, 10,
                     f'{data["box_depth"]:.0f}"', font_size=5.5)

    # Total length (right side)
    draw_dimension_v(c, col_right, col_bottom, col_top, 20,
                     _fmt_ft_in(data["total_length_in"]), font_size=5.5)

    # Embedment line
    embed_y = col_bottom + data["embedment_in"] * scale
    c.setStrokeColor(CLR_DIM)
    c.setLineWidth(THIN)
    c.setDash([6, 3])
    c.line(col_left - 8, embed_y, col_right + 8, embed_y)
    c.setDash([])

    # Rebar (hidden lines in side view)
    rebar_len_scaled = data["rebar_length_in"] * scale
    rebar_end = min(col_bottom + rebar_len_scaled, col_top)
    c.setStrokeColor(CLR_REBAR)
    c.setLineWidth(THIN)
    c.setDash([3, 2])
    inset = 2.5 * scale
    for rx in [col_left + inset, col_right - inset]:
        c.line(rx, col_bottom, rx, rebar_end)
    c.setDash([])

    # View label
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(black)
    c.drawCentredString(cx, oy + 5, "SIDE VIEW")


def _draw_section_aa(c, data: Dict, ox: float, oy: float,
                     view_w: float, view_h: float):
    """
    Section A-A: Cross section through column body.
    Shows two C-sections welded into box beam with rebar in corners.
    """
    # Cross section dimensions
    box_w = data["box_width"]   # 14"
    box_d = data["box_depth"]   # 8"

    margin = 15
    avail = min(view_w, view_h) - 2 * margin
    scale = avail / max(box_w, box_d) * 0.6

    sw = box_w * scale
    sd = box_d * scale
    cx = ox + view_w / 2
    cy = oy + view_h / 2 + 5

    # Outer rectangle (box beam outline)
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(THICK)
    c.rect(cx - sw / 2, cy - sd / 2, sw, sd)

    # Inner void (the hollow interior)
    wall_t = 0.135 * scale * 12  # 10GA ≈ 0.135", scaled
    inner_w = sw - 2 * wall_t * 3  # Exaggerate for visibility
    inner_d = sd - 2 * wall_t * 3
    c.setStrokeColor(CLR_HIDDEN)
    c.setLineWidth(THIN)
    c.rect(cx - inner_w / 2, cy - inner_d / 2, inner_w, inner_d)

    # Center seam line (where two CEEs meet)
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(MEDIUM)
    c.line(cx, cy - sd / 2, cx, cy + sd / 2)

    # Stitch weld marks on seam
    draw_weld_symbol(c, cx, cy + sd / 2 + 2, "B", size=3)

    # Rebar dots (4 corners)
    rebar_r = 2.5  # visual radius
    c.setFillColor(CLR_REBAR)
    inset = 5 if data["rebar_reinforced"] else -5
    corners = [
        (cx - sw / 2 + inset + rebar_r, cy - sd / 2 + inset + rebar_r),
        (cx + sw / 2 - inset - rebar_r, cy - sd / 2 + inset + rebar_r),
        (cx - sw / 2 + inset + rebar_r, cy + sd / 2 - inset - rebar_r),
        (cx + sw / 2 - inset - rebar_r, cy + sd / 2 - inset - rebar_r),
    ]
    for rx, ry in corners:
        c.circle(rx, ry, rebar_r, fill=1, stroke=1)

    # Rebar label
    c.setFont("Helvetica", 4.5)
    c.setFillColor(CLR_REBAR)
    pos_label = "INSIDE" if data["rebar_reinforced"] else "OUTSIDE"
    c.drawCentredString(cx, cy - sd / 2 - 10,
                        f'{data["rebar_size"]} REBAR ({pos_label}) TYP 4 PL')

    # Dimension labels
    draw_dimension_h(c, cx - sw / 2, cx + sw / 2,
                     cy + sd / 2, 10,
                     f'{box_w:.0f}"', font_size=5.5)
    draw_dimension_v(c, cx + sw / 2, cy - sd / 2, cy + sd / 2, 10,
                     f'{box_d:.0f}"', font_size=5.5)

    # Material callout
    c.setFont("Helvetica", 4.5)
    c.setFillColor(CLR_DIM)
    c.drawCentredString(cx, cy + sd / 2 + 22,
                        f'2x CEE {data["cee_size"]} WELDED BOX')

    # View label
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(black)
    c.drawCentredString(cx, oy + 5, "SECTION A-A")


def _draw_section_bb(c, data: Dict, ox: float, oy: float,
                     view_w: float, view_h: float):
    """
    Section B-B: Cross section at cap plate level.
    Shows cap plate, bolt hole pattern, gusset positions.
    """
    cap_w = data["cap_plate_length_in"]  # 26"
    cap_d = data["cap_plate_width_in"]   # 14"

    margin = 15
    avail = min(view_w, view_h) - 2 * margin
    scale = avail / max(cap_w, cap_d) * 0.5

    sw = cap_w * scale
    sd = cap_d * scale
    cx = ox + view_w / 2
    cy = oy + view_h / 2 + 5

    # Cap plate (filled rectangle)
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(THICK)
    c.setFillColor(HexColor("#E0E0E0"))
    c.rect(cx - sw / 2, cy - sd / 2, sw, sd, fill=1)

    # Column outline on plate (hidden)
    col_sw = data["box_width"] * scale
    col_sd = data["box_depth"] * scale
    c.setStrokeColor(CLR_HIDDEN)
    c.setLineWidth(THIN)
    c.setDash([3, 2])
    c.rect(cx - col_sw / 2, cy - col_sd / 2, col_sw, col_sd)
    c.setDash([])

    # Bolt holes (4)
    c.setStrokeColor(CLR_OBJECT)
    c.setFillColor(white)
    c.setLineWidth(MEDIUM)
    bolt_sp_x = 9 * scale
    bolt_sp_y = 4 * scale
    bolt_r = 2.5
    for bx in [-bolt_sp_x / 2, bolt_sp_x / 2]:
        for by in [-bolt_sp_y / 2, bolt_sp_y / 2]:
            c.circle(cx + bx, cy + by, bolt_r, fill=1, stroke=1)

    # Bolt hole callout
    c.setFont("Helvetica", 4.5)
    c.setFillColor(CLR_DIM)
    c.drawCentredString(cx, cy - sd / 2 - 8,
                        f'4x {data["bolt_hole_dia"]} HOLES')

    # Gusset outlines (triangles at corners)
    g_size = data["gusset_leg_in"] * scale
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(MEDIUM)
    c.setFillColor(HexColor("#D0D0D0"))
    # Show gusset footprint as small triangles at 4 corners of column
    for gx_sign, gy_sign in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        gx = cx + gx_sign * col_sw / 2
        gy = cy + gy_sign * col_sd / 2
        p = c.beginPath()
        p.moveTo(gx, gy)
        p.lineTo(gx + gx_sign * g_size * 0.4, gy)
        p.lineTo(gx, gy + gy_sign * g_size * 0.4)
        p.close()
        c.drawPath(p, fill=1)

    # Dimensions
    draw_dimension_h(c, cx - sw / 2, cx + sw / 2,
                     cy + sd / 2, 10,
                     f'{cap_w:.0f}"', font_size=5.5)
    draw_dimension_v(c, cx + sw / 2, cy - sd / 2, cy + sd / 2, 10,
                     f'{cap_d:.0f}"', font_size=5.5)

    # Material
    c.setFont("Helvetica", 4.5)
    c.setFillColor(CLR_DIM)
    c.drawCentredString(cx, cy + sd / 2 + 20,
                        f'PL {data["cap_plate_thickness"]} x {cap_d:.0f}" x {cap_w:.0f}" A572')

    # View label
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(black)
    c.drawCentredString(cx, oy + 5, "SECTION B-B")


# ═══════════════════════════════════════════════════════════════════════════════
# BOM TABLE
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_bom_table(c, data: Dict, ox: float, oy: float, w: float, h: float):
    """Mini BOM table listing column parts."""
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(THIN)

    # Headers
    headers = ["MARK", "QTY", "DESCRIPTION", "SIZE", "MATERIAL"]
    col_widths = [w * 0.09, w * 0.07, w * 0.34, w * 0.24, w * 0.26]

    row_h = 9
    n_rows = 6  # Header + 5 data rows
    table_h = n_rows * row_h

    # Table outline
    c.rect(ox, oy + h - table_h, w, table_h)

    # Header row
    hy = oy + h - row_h
    c.setFillColor(HexColor("#2A2A4A"))
    c.rect(ox, hy, w, row_h, fill=1)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 5)

    x_pos = ox
    for i, hdr in enumerate(headers):
        c.drawCentredString(x_pos + col_widths[i] / 2, hy + 3, hdr)
        x_pos += col_widths[i]

    # Draw column lines
    x_pos = ox
    for cw in col_widths[:-1]:
        x_pos += cw
        c.setStrokeColor(CLR_GRID)
        c.setLineWidth(HAIR)
        c.line(x_pos, oy + h - table_h, x_pos, oy + h)

    # Data rows
    rows = [
        [data["mark"], "2", "CEE Section (Box Beam)",
         f'{data["cee_size"]}',
         data["material_grade"]],
        [data["mark"], "1", "Cap Plate",
         f'{data["cap_plate_thickness"]} x {data["cap_plate_width_in"]:.0f}" x {data["cap_plate_length_in"]:.0f}"',
         "A572 Gr 50"],
        [data["mark"], "4", "Triangle Gusset",
         f'{data["gusset_thickness"]} x {data["gusset_leg_in"]:.0f}"x{data["gusset_leg_in"]:.0f}"',
         "A572 Gr 50"],
        [data["mark"], "4", "Rebar",
         f'{data["rebar_size"]} x {_fmt_ft_in(data["rebar_length_in"])}',
         "A706"],
        [data["mark"], f'{data["connection_bolts"]}', "Connection Bolts",
         f'{data["bolt_hole_dia"]} DIA',
         "A325"],
    ]

    c.setFillColor(black)
    c.setFont("Helvetica", 4.5)
    for r_idx, row in enumerate(rows):
        ry = hy - (r_idx + 1) * row_h
        # Alternate row bg
        if r_idx % 2 == 1:
            c.setFillColor(HexColor("#F5F5F5"))
            c.rect(ox, ry, w, row_h, fill=1)
            c.setFillColor(black)
        # Row separator
        c.setStrokeColor(CLR_GRID)
        c.setLineWidth(HAIR)
        c.line(ox, ry, ox + w, ry)
        # Cell text
        x_pos = ox
        for i, cell in enumerate(row):
            c.drawCentredString(x_pos + col_widths[i] / 2, ry + 3, str(cell))
            x_pos += col_widths[i]

    # "BILL OF MATERIALS" label
    c.setFont("Helvetica-Bold", 5.5)
    c.setFillColor(black)
    c.drawCentredString(ox + w / 2, oy + h - table_h - 8, "BILL OF MATERIALS")


# ═══════════════════════════════════════════════════════════════════════════════
# TITLE BLOCK
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_title_block(c, cfg: ShopDrawingConfig, data: Dict,
                      sheet_num: int = 1, total_sheets: int = 1,
                      revision: str = "-"):
    """
    Title block in bottom-right corner.
    """
    tb_w = 3.2 * inch
    tb_h = 1.3 * inch
    tb_x = PAGE_W - MARGIN - tb_w
    tb_y = MARGIN

    # Background
    c.setFillColor(CLR_TITLE_BG)
    c.rect(tb_x, tb_y, tb_w, tb_h, fill=1)

    # Borders
    c.setStrokeColor(white)
    c.setLineWidth(MEDIUM)
    c.rect(tb_x, tb_y, tb_w, tb_h)

    # Fabricator info (top section)
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

    # Divider
    y -= 5
    c.setStrokeColor(HexColor("#444466"))
    c.line(tb_x + 5, y, tb_x + tb_w - 5, y)

    # Project info
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

    # Drawing title
    y -= 10
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(tb_x + tb_w / 2, y,
                        f'COLUMN {data["mark"]}')


# ═══════════════════════════════════════════════════════════════════════════════
# STANDARD NOTES
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_standard_notes(c, ox: float, oy: float, w: float, h: float):
    """Standard notes block."""
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(THIN)
    c.rect(ox, oy, w, h)

    c.setFont("Helvetica-Bold", 5.5)
    c.setFillColor(black)
    y = oy + h - 9
    c.drawString(ox + 3, y, "GENERAL NOTES:")

    c.setFont("Helvetica", 4.5)
    y -= 8
    notes_list = [
        f'1. MATERIAL: {STANDARD_NOTES["material"]}',
        f'2. PAINT: {STANDARD_NOTES["paint"]}',
        f'3. HOLES: {STANDARD_NOTES["holes"]}',
        f'4. {STANDARD_NOTES["no_paint"]}',
        f'5. TOLERANCE: {STANDARD_NOTES["tolerance"]}',
        f'6. {STANDARD_NOTES["measure_direction"]}',
    ]
    for note in notes_list:
        c.drawString(ox + 3, y, note)
        y -= 7

    # WPS legend
    y -= 3
    c.setFont("Helvetica-Bold", 4.5)
    c.drawString(ox + 3, y, "WPS CODES:")
    y -= 7
    c.setFont("Helvetica", 4.5)
    for code, info in WPS_CODES.items():
        c.drawString(ox + 3, y, f'WPS-"{code}": {info["application"]}')
        y -= 7


# ═══════════════════════════════════════════════════════════════════════════════
# ABBREVIATIONS TABLE
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_abbreviations(c, ox: float, oy: float, w: float, h: float):
    """Small abbreviations reference."""
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(THIN)
    c.rect(ox, oy, w, h)

    c.setFont("Helvetica-Bold", 5)
    c.setFillColor(black)
    y = oy + h - 8
    c.drawString(ox + 3, y, "ABBREVIATIONS:")

    c.setFont("Helvetica", 4)
    y -= 7
    for abbr, meaning in ABBREVIATIONS.items():
        if y < oy + 3:
            break
        c.drawString(ox + 3, y, f'{abbr} = {meaning}')
        y -= 6


# ═══════════════════════════════════════════════════════════════════════════════
# BORDER & FRAME
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_border(c):
    """Page border with margin lines."""
    # Outer border
    c.setStrokeColor(black)
    c.setLineWidth(2.0)
    c.rect(MARGIN * 0.5, MARGIN * 0.5,
           PAGE_W - MARGIN, PAGE_H - MARGIN)
    # Inner border
    c.setLineWidth(0.5)
    c.rect(MARGIN, MARGIN, PAGE_W - 2 * MARGIN, PAGE_H - 2 * MARGIN)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

def generate_column_drawing(
    cfg: ShopDrawingConfig,
    col_index: int = 0,
    output_path: Optional[str] = None,
    revision: str = "-",
) -> bytes:
    """
    Generate a complete column shop drawing PDF.

    Args:
        cfg: ShopDrawingConfig with all project/building data
        col_index: Column index (0-based) for mark numbering
        output_path: If given, save PDF to this path
        revision: Revision letter for title block

    Returns:
        PDF bytes
    """
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=landscape(letter))
    c.setTitle(f"Column {col_index + 1} Shop Drawing")

    data = _calc_column_data(cfg, col_index)

    # ── Draw border ──
    _draw_border(c)

    # ── Layout zones ──
    # Main drawing area is divided into a 2x2 grid for the 4 views
    # Top row: Front View (wide) + Section A-A
    # Bottom half: Side View + Section B-B
    # Bottom bar: Notes + BOM + Title Block

    draw_area_w = PAGE_W - 2 * MARGIN
    draw_area_h = PAGE_H - 2 * MARGIN

    # Bottom bar height for notes/title
    bar_h = 1.5 * inch
    views_h = draw_area_h - bar_h

    # Split views: Front (60%) | Right column (40%)
    front_w = draw_area_w * 0.55
    right_w = draw_area_w * 0.45

    # Split right column: top (Section A-A) | bottom (Section B-B)
    right_top_h = views_h * 0.5
    right_bot_h = views_h * 0.5

    # Front view and side view share the left column
    # Front view takes 70% of left, Side view 30%
    front_actual_w = front_w * 0.65
    side_w = front_w * 0.35

    # Origins
    front_ox = MARGIN
    front_oy = MARGIN + bar_h
    side_ox = MARGIN + front_actual_w
    side_oy = front_oy
    sec_aa_ox = MARGIN + front_w
    sec_aa_oy = front_oy + right_bot_h
    sec_bb_ox = MARGIN + front_w
    sec_bb_oy = front_oy

    # ── Draw 4 views ──
    _draw_front_view(c, data, front_ox, front_oy, front_actual_w, views_h)
    _draw_side_view(c, data, side_ox, side_oy, side_w, views_h)
    _draw_section_aa(c, data, sec_aa_ox, sec_aa_oy, right_w, right_top_h)
    _draw_section_bb(c, data, sec_bb_ox, sec_bb_oy, right_w, right_bot_h)

    # ── View area separators (light grid) ──
    c.setStrokeColor(CLR_GRID)
    c.setLineWidth(HAIR)
    c.setDash([4, 4])
    # Vertical divider between left and right
    c.line(MARGIN + front_w, front_oy, MARGIN + front_w, front_oy + views_h)
    # Horizontal divider in right column
    c.line(MARGIN + front_w, front_oy + right_bot_h,
           MARGIN + draw_area_w, front_oy + right_bot_h)
    # Divider between front and side
    c.line(side_ox, front_oy, side_ox, front_oy + views_h)
    c.setDash([])

    # ── Bottom bar ──
    # Notes (left)
    notes_w = draw_area_w * 0.3
    _draw_standard_notes(c, MARGIN, MARGIN, notes_w, bar_h)

    # Abbreviations (center-left)
    abbr_w = draw_area_w * 0.15
    _draw_abbreviations(c, MARGIN + notes_w, MARGIN, abbr_w, bar_h)

    # BOM table (center)
    bom_w = draw_area_w * 0.25
    bom_ox = MARGIN + notes_w + abbr_w
    _draw_bom_table(c, data, bom_ox, MARGIN, bom_w, bar_h)

    # Title block (right)
    _draw_title_block(c, cfg, data, revision=revision)

    # ── Weight callout (bottom of front view, above notes bar) ──
    c.setFont("Helvetica-Bold", 6)
    c.setFillColor(CLR_DIM)
    c.drawString(MARGIN + 5, MARGIN + bar_h + 5,
                 f'APPROX WEIGHT: {data["weight_lbs"]:.0f} LBS')

    c.save()
    pdf_bytes = buf.getvalue()

    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)

    return pdf_bytes


def generate_all_column_drawings(
    cfg: ShopDrawingConfig,
    output_dir: str,
    revision: str = "-",
) -> List[str]:
    """
    Generate shop drawings for all unique column types in the project.
    Returns list of output file paths.

    For now, generates one drawing per unique column configuration.
    With 2-post frames, columns at different positions may have different
    heights due to roof slope — each unique height gets its own drawing.
    """
    paths = []

    if cfg.frame_type == "tee":
        # TEE: 1 column type per frame (all same height)
        path = os.path.join(output_dir, f"{cfg.job_code}_C1.pdf")
        generate_column_drawing(cfg, col_index=0, output_path=path, revision=revision)
        paths.append(path)
    else:
        # 2-POST: 2 columns per frame — but symmetric, so typically 1 unique type
        # In the symmetric case, left and right columns are the same height
        path = os.path.join(output_dir, f"{cfg.job_code}_C1.pdf")
        generate_column_drawing(cfg, col_index=0, output_path=path, revision=revision)
        paths.append(path)

    return paths
