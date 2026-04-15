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
    """
    # Force all config values to correct numeric types
    cfg.ensure_numeric()

    slope_deg = float(cfg.roof_pitch_deg)
    tan_slope = math.tan(math.radians(slope_deg))

    # Column height formula: clear_height + distance*tan(slope) + embedment + buffer
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
        "rebar_length_ft": rebar_length_ft,
        "rebar_qty": 4,  # Always 4 per column
        "stitch_weld": COLUMN_DEFAULTS["stitch_weld"],
        "connection_bolts": cfg.col_connection_bolts,
        "weight_lbs": weight_lbs,
        "frame_type": cfg.frame_type,
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
                     view_w: float, view_h: float, cfg=None):
    """
    Draw front elevation of column HORIZONTALLY (pixel-perfect precision).
    Left = bottom of column (footing end), Right = top with cap plate.
    Shows:
    - Full column length with HEAVY rebar lines extending 15-20% past left end
    - Column body rectangle (thick outline)
    - Cap plate at right end (thin vertical, angled at roof pitch)
    - Gussets p4 (above) and p5 (below) as triangles
    - Stitch weld marks (X pattern) at 3" OC ends, 36" OC body
    - Section B-B cut line (dashed red, vertical near left end)
    - Complete dimension set (above: CEE length, below: total/split/rebar)
    - Weld callout (3/16 TYP)
    - Column count header
    """
    total_in = data["total_length_in"]

    # Scale to fit view with margins for rebar extension
    col_margin = 20
    avail_h = view_h - 2 * col_margin
    avail_w = view_w - 2 * col_margin
    scale = min(avail_w / (total_in + 60), avail_h / 35)

    # Column dimensions (horizontal layout)
    col_w = total_in * scale
    col_h = data["box_width"] * scale  # 14" becomes 30-40 pts

    # Position column centered vertically
    col_left = ox + col_margin + 40
    col_right = col_left + col_w
    cy = oy + (view_h / 2)
    col_bottom = cy - col_h / 2
    col_top = cy + col_h / 2

    # ── REBAR: 4 solid lines extending past left end ──
    rebar_extend_pct = 0.175  # 15-20% extension
    rebar_extend = total_in * scale * rebar_extend_pct
    rebar_past_left = col_left - rebar_extend

    c.setStrokeColor(CLR_REBAR)
    c.setLineWidth(THICK)  # Make rebar VISIBLE
    c.setLineCap(1)  # Round line caps

    # 4 rebar positions: 2 near top, 2 near bottom
    rebar_inset = 2.5 * scale
    rebar_y_positions = [
        col_bottom + rebar_inset,
        col_bottom + col_h * 0.33,
        col_bottom + col_h * 0.67,
        col_top - rebar_inset,
    ]
    for ry in rebar_y_positions:
        c.line(rebar_past_left, ry, col_right, ry)  # Extend through entire column

    # ── COLUMN BODY: thick rectangle outline ──
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(THICK)
    c.rect(col_left, col_bottom, col_w, col_h)

    # ── CAP PLATE: thin vertical line at right, rotated at pitch angle ──
    cap_angle = data["cap_angle_deg"]
    cap_thick = 0.75 * scale * 8  # 3/4" thick, rendered as wider for visibility
    cap_plate_len = data["cap_plate_length_in"] * scale

    c.saveState()
    c.translate(col_right, cy)
    c.rotate(-cap_angle)
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(THICK)
    c.setFillColor(HexColor("#E8E8E8"))
    c.rect(-cap_thick/2, -col_h/2 - 5, cap_thick, col_h + 10, fill=1)
    c.setFont("Helvetica", 4.5)
    c.setFillColor(CLR_DIM)
    c.drawCentredString(0, -col_h/2 - 12,
                        f'PL {data["cap_plate_thickness"]} x {data["cap_plate_width_in"]:.0f}"')
    c.drawCentredString(0, -col_h/2 - 18, f'@ {cap_angle:.0f}°')
    c.restoreState()

    # ── GUSSETS: p4 (above) and p5 (below) as right triangles ──
    gusset_leg = data["gusset_leg_in"] * scale

    # p4 (uphill, above cap plate)
    gx = col_right + 1
    gy_top = col_top
    gy_bottom = col_top - gusset_leg * 0.75
    p = c.beginPath()
    p.moveTo(gx, gy_top)
    p.lineTo(gx + gusset_leg * 0.6, gy_top)
    p.lineTo(gx, gy_bottom)
    p.close()
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(MEDIUM)
    c.setFillColor(HexColor("#D8D8D8"))
    c.drawPath(p, fill=1, stroke=1)

    # p5 (downhill, below cap plate)
    gy_bottom = col_bottom
    gy_top = col_bottom + gusset_leg * 0.6
    p = c.beginPath()
    p.moveTo(gx, gy_bottom)
    p.lineTo(gx + gusset_leg * 0.5, gy_bottom)
    p.lineTo(gx, gy_top)
    p.close()
    c.setFillColor(HexColor("#D8D8D8"))
    c.drawPath(p, fill=1, stroke=1)

    # ── SECTION B-B CUT LINE: dashed red vertical near left end ──
    cut_x = col_left + (data["embedment_in"] * 0.15) * scale  # 10-15% from left
    c.setStrokeColor(CLR_SECTION_CUT)
    c.setLineWidth(MEDIUM)
    c.setDash([8, 3, 2, 3])  # Specific dash pattern
    c.line(cut_x, col_bottom, cut_x, col_top)
    c.setDash([])

    # Section marker circle at bottom of cut line
    draw_section_marker(c, cut_x, col_bottom - 8, "B", size=8)

    # ── PIECE MARK LABELS with leaders ──
    c.setFont("Helvetica", 5)
    c.setFillColor(CLR_DIM)

    # p3 on cap plate
    draw_leader(c, col_right + 2, cy, col_right + 35, cy + 10, "p3", font_size=5.5)

    # p4 on uphill gusset
    draw_leader(c, gx + gusset_leg * 0.3, col_top - gusset_leg * 0.4,
                gx + 50, col_top, "p4", font_size=5.5)

    # p5 on downhill gusset
    draw_leader(c, gx + gusset_leg * 0.2, col_bottom + gusset_leg * 0.3,
                gx + 40, col_bottom - 10, "p5", font_size=5.5)

    # ── STITCH WELD MARKS: X pattern on top and bottom edges ──
    end_length = 12 * scale
    c.setStrokeColor(CLR_WELD)
    c.setLineWidth(THIN)

    # End pattern (3" OC, first 12" of each end)
    end_spacing = 3 * scale
    x = col_left
    while x < col_left + end_length:
        for yy in [col_top, col_bottom]:
            c.line(x - 1.5, yy + 1, x + 1.5, yy - 1)
            c.line(x - 1.5, yy - 1, x + 1.5, yy + 1)
        x += end_spacing

    # Body pattern (36" OC, middle section)
    body_spacing = 36 * scale
    x = col_left + end_length + body_spacing
    while x < col_right - end_length:
        for yy in [col_top, col_bottom]:
            c.line(x - 2, yy + 1, x + 2, yy - 1)
            c.line(x - 2, yy - 1, x + 2, yy + 1)
        x += body_spacing

    # Right end pattern (3" OC)
    x = col_right - end_length
    while x < col_right:
        for yy in [col_top, col_bottom]:
            c.line(x - 1.5, yy + 1, x + 1.5, yy - 1)
            c.line(x - 1.5, yy - 1, x + 1.5, yy + 1)
        x += end_spacing

    # ── REBAR WELD CALLOUTS: 3/16 TYP at 4 corners ──
    c.setFont("Helvetica-Bold", 4.5)
    c.setFillColor(CLR_WELD)
    c.drawString(col_left - 5, col_top + 3, "3/16 TYP")
    c.drawString(col_left - 5, col_bottom - 3, "3/16 TYP")
    c.drawString(col_right - 15, col_top + 3, "3/16 TYP")
    c.drawString(col_right - 15, col_bottom - 3, "3/16 TYP")

    # ── DIMENSIONS ──
    # Above column: CEE length with size notation
    cee_label = f'{_fmt_ft_in(data["total_length_in"])} (C{data["cee_size"]})'
    draw_dimension_h(c, col_left, col_right, col_top, 18, cee_label, font_size=5.5)

    # Below column row 1: Total length
    draw_dimension_h(c, col_left, col_right, col_bottom - 20, -18,
                    f'{_fmt_ft_in(data["total_length_in"])}', font_size=5.5)

    # Below column row 2: Split (embedment | above-grade)
    embed_x = col_left + data["embedment_in"] * scale
    draw_dimension_h(c, col_left, embed_x, col_bottom - 40, -12,
                    f'{_fmt_ft_in(data["embedment_in"])}', font_size=5)
    draw_dimension_h(c, embed_x, col_right, col_bottom - 40, -12,
                    f'{_fmt_ft_in(data["total_length_in"] - data["embedment_in"])}', font_size=5)

    # Rebar length dimension (below split row)
    if data["rebar_length_in"] > 0:
        rebar_end_x = col_left + data["rebar_length_in"] * scale
        rb_label = f'{data["rebar_size"]} Rebar {_fmt_ft_in(data["rebar_length_in"])}'
        draw_dimension_h(c, rebar_past_left, rebar_end_x, col_bottom - 60, -12,
                        rb_label, font_size=5)

    # Cap plate width dimension (1'-2" at right end)
    cap_plate_width = data["cap_plate_length_in"]
    draw_dimension_h(c, col_right, col_right + (cap_plate_width * scale * 0.3),
                    col_bottom - 80, -12,
                    f'{_fmt_ft_in(cap_plate_width)}', font_size=5)

    # ── COLUMN COUNT and VIEW LABEL ──
    if cfg:
        col_count = cfg.n_frames if cfg.frame_type == "tee" else cfg.n_frames * 2
    else:
        col_count = 1

    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(black)
    c.drawCentredString(col_left + col_w/2, oy + view_h - 8,
                       f'{col_count} - Columns - {data["mark"]}')

    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(col_left + col_w/2, oy + 3, "FRONT VIEW")


def _draw_side_view(c, data: Dict, ox: float, oy: float,
                    view_w: float, view_h: float):
    """
    Side View: Cap plate assembly shown from the FRONT face.
    Displays TWO overlapping rectangles:
    1. Front face: 2'-2" tall (26") x 14" wide with 4 bolt holes
    2. Side face: 1'-2" wide showing depth view
    Complete with bolt hole pattern, gussets p4 and p5, and all dimensions.
    """
    total_in = data["total_length_in"]

    col_margin = 20
    avail_h = view_h - 2 * col_margin
    avail_w = view_w - 2 * col_margin
    scale = min(avail_w / (total_in * 0.8), avail_h / 40)

    cap_w = data["cap_plate_width_in"] * scale  # 14"
    cap_h = data["cap_plate_length_in"] * scale  # 26" = 2'-2"

    # Horizontal center, slightly below vertical center
    cx = ox + avail_w / 2
    cy = oy + avail_h / 2 + 10

    # ── FRONT FACE: main rectangle 14" wide x 26" tall ──
    front_left = cx - cap_w / 2
    front_right = cx + cap_w / 2
    front_bottom = cy - cap_h / 2
    front_top = cy + cap_h / 2

    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(THICK)
    c.setFillColor(HexColor("#E8E8E8"))
    c.rect(front_left, front_bottom, cap_w, cap_h, fill=1)

    # ── 4 BOLT HOLES (13/16" diameter, 1-1/2" edge distance) ──
    edge_dist = 1.5 * scale
    bolt_dia = 0.9375 * scale
    bolt_r = bolt_dia / 2

    bolt_y_top = front_top - edge_dist
    bolt_y_bottom = front_bottom + edge_dist
    bolt_x_left = front_left + edge_dist
    bolt_x_right = front_right - edge_dist

    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(MEDIUM)
    c.setFillColor(white)
    for bx in [bolt_x_left, bolt_x_right]:
        for by in [bolt_y_bottom, bolt_y_top]:
            c.circle(bx, by, bolt_r, fill=1, stroke=1)

    # ── GUSSETS p4 (left) and p5 (right) ──
    gusset_leg = data["gusset_leg_in"] * scale
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(MEDIUM)
    c.setFillColor(HexColor("#D8D8D8"))

    # p4: left gusset extending upper-left from top-left corner
    p4_base_x = front_left
    p4_base_y = front_top
    p4_tip_x = front_left - gusset_leg
    p4_tip_y = front_top + gusset_leg
    p = c.beginPath()
    p.moveTo(p4_base_x, p4_base_y)
    p.lineTo(p4_tip_x, p4_tip_y)
    p.lineTo(p4_base_x, p4_base_y - gusset_leg)
    p.close()
    c.drawPath(p, fill=1, stroke=1)

    # p5: right gusset extending upper-right from top-right corner
    p5_base_x = front_right
    p5_base_y = front_top
    p5_tip_x = front_right + gusset_leg
    p5_tip_y = front_top + gusset_leg
    p = c.beginPath()
    p.moveTo(p5_base_x, p5_base_y)
    p.lineTo(p5_tip_x, p5_tip_y)
    p.lineTo(p5_base_x, p5_base_y - gusset_leg)
    p.close()
    c.drawPath(p, fill=1, stroke=1)

    # ── DIMENSIONS on front face ──
    # Vertical: 1-1/2" + 1'-11" (bolt spacing) + 1-1/2" = 2'-2"
    draw_dimension_v(c, front_left - 15, front_bottom, front_bottom + edge_dist,
                    -10, '1-1/2"', font_size=4.5)
    draw_dimension_v(c, front_left - 15, front_bottom + edge_dist, front_top - edge_dist,
                    -10, '1\'-11"', font_size=5)
    draw_dimension_v(c, front_left - 15, front_top - edge_dist, front_top,
                    -10, '1-1/2"', font_size=4.5)

    # Horizontal: edge distances and bolt spacing
    draw_dimension_h(c, front_left, front_left + edge_dist, front_bottom - 12, -8,
                    '1-1/2"', font_size=4.5)
    draw_dimension_h(c, front_left + edge_dist, front_right - edge_dist, front_bottom - 12, -8,
                    '11"', font_size=5)
    draw_dimension_h(c, front_right - edge_dist, front_right, front_bottom - 12, -8,
                    '1-1/2"', font_size=4.5)

    # Overall width (14")
    draw_dimension_h(c, front_left, front_right, front_top + 12, 8,
                    f'{data["cap_plate_width_in"]:.0f}"', font_size=5.5)

    # Overall height (2'-2")
    draw_dimension_v(c, front_right + 15, front_bottom, front_top, 10,
                    f'{_fmt_ft_in(data["cap_plate_length_in"])}', font_size=5.5)

    # ── SIDE FACE: smaller rectangle to the right showing 1'-2" width ──
    side_w = data["cap_plate_length_in"] * scale * 0.4  # 1'-2" scaled down
    side_h = data["box_depth"] * scale * 0.5  # 8" scaled down
    side_left = front_right + 20
    side_bottom = cy - side_h / 2
    side_top = cy + side_h / 2

    c.setFillColor(HexColor("#E8E8E8"))
    c.rect(side_left, side_bottom, side_w, side_h, fill=1)

    # ── Piece marks with leaders ──
    c.setFont("Helvetica", 5)
    c.setFillColor(CLR_DIM)

    # p3 on front face (center)
    draw_leader(c, cx, cy, cx + 40, cy - 15, "p3", font_size=5.5)

    # p4 on left gusset
    draw_leader(c, p4_tip_x, p4_tip_y, p4_tip_x - 20, p4_tip_y + 10, "p4", font_size=5.5)

    # p5 on right gusset
    draw_leader(c, p5_tip_x, p5_tip_y, p5_tip_x + 20, p5_tip_y + 10, "p5", font_size=5.5)

    # ── 5° angle label ──
    c.setFont("Helvetica", 5)
    c.setFillColor(CLR_DIM)
    c.drawString(cx - 10, front_bottom - 25, "5°")

    # ── VIEW LABEL ──
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(black)
    c.drawCentredString(cx, oy + 3, "SIDE VIEW")


def _draw_section_aa(c, data: Dict, ox: float, oy: float,
                     view_w: float, view_h: float):
    """
    Section A-A: End view of cap plate assembly (pixel-perfect).
    Shows:
    - Cap plate standing VERTICALLY (14" wide x 26" tall = 2'-2")
    - Column box beam profile inside (14" x 8", dashed hidden line)
    - Gussets p4 (left) and p5 (right) as RIGHT TRIANGLES extending upward
    - 4 bolt holes with 1-1/2" edge distances
    - All dimensions including gusset legs (6"), hypotenuses, and angles (85°, 95°)
    """
    cap_w = data["cap_plate_width_in"]   # 14"
    cap_h = data["cap_plate_length_in"]  # 26" = 2'-2"
    gusset_leg = data["gusset_leg_in"]   # 6"
    uphill_hyp = data["uphill_hyp_in"]
    downhill_hyp = data["downhill_hyp_in"]
    edge_dist = 1.5

    margin = 10
    avail_w = view_w - 2 * margin
    avail_h = view_h - 2 * margin
    scale = min(avail_w / (cap_w + 2 * gusset_leg), avail_h / cap_h) * 0.55

    sw = cap_w * scale
    sh = cap_h * scale

    cx = ox + (view_w - sw) / 2
    cy = oy + (view_h - sh) / 2 + margin

    plate_left = cx
    plate_right = cx + sw
    plate_bottom = cy
    plate_top = cy + sh

    # ── CAP PLATE: standing vertically ──
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(THICK)
    c.setFillColor(HexColor("#E8E8E8"))
    c.rect(plate_left, plate_bottom, sw, sh, fill=1)

    # ── COLUMN BOX outline (dashed, centered inside plate) ──
    col_w = data["box_width"] * scale
    col_h = data["box_depth"] * scale
    col_left = cx + (sw - col_w) / 2
    col_bottom = cy + (sh - col_h) / 2
    c.setStrokeColor(CLR_HIDDEN)
    c.setLineWidth(THIN)
    c.setDash([3, 2])
    c.rect(col_left, col_bottom, col_w, col_h)
    c.setDash([])

    # ── BOLT HOLES: 4 circles with 1-1/2" edge distance ──
    edge_scaled = edge_dist * scale
    bolt_r = max(0.9375 * scale / 2, 2.0)

    bolt_y_bottom = plate_bottom + edge_scaled
    bolt_y_top = plate_top - edge_scaled
    bolt_x_left = plate_left + edge_scaled
    bolt_x_right = plate_right - edge_scaled

    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(MEDIUM)
    c.setFillColor(white)
    for bx in [bolt_x_left, bolt_x_right]:
        for by in [bolt_y_bottom, bolt_y_top]:
            c.circle(bx, by, bolt_r, fill=1, stroke=1)

    # ── GUSSETS: RIGHT TRIANGLES extending UPWARD from plate top ──
    # p4: upper-left (85° angle), p5: upper-right (95° angle)
    g_leg = gusset_leg * scale

    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(MEDIUM)
    c.setFillColor(HexColor("#D8D8D8"))

    # p4 (LEFT gusset): vertical leg down left edge (6"), horizontal leg left (6")
    p4_base_x = plate_left
    p4_base_y_top = plate_top
    p4_base_y_down = plate_top - g_leg
    p4_tip_x = plate_left - g_leg
    p4_tip_y = plate_top

    p = c.beginPath()
    p.moveTo(p4_base_x, p4_base_y_top)
    p.lineTo(p4_tip_x, p4_tip_y)
    p.lineTo(p4_base_x, p4_base_y_down)
    p.close()
    c.drawPath(p, fill=1, stroke=1)

    # p5 (RIGHT gusset): vertical leg down right edge (6"), horizontal leg right (6")
    p5_base_x = plate_right
    p5_base_y_top = plate_top
    p5_base_y_down = plate_top - g_leg
    p5_tip_x = plate_right + g_leg
    p5_tip_y = plate_top

    p = c.beginPath()
    p.moveTo(p5_base_x, p5_base_y_top)
    p.lineTo(p5_tip_x, p5_tip_y)
    p.lineTo(p5_base_x, p5_base_y_down)
    p.close()
    c.drawPath(p, fill=1, stroke=1)

    # ── PIECE MARK LABELS ──
    c.setFont("Helvetica", 5)
    c.setFillColor(CLR_DIM)

    draw_leader(c, (plate_left + plate_right) / 2, cy + sh / 2,
                (plate_left + plate_right) / 2 + 35, cy + sh / 2 - 20, "p3", font_size=5.5)
    draw_leader(c, p4_tip_x, p4_tip_y, p4_tip_x - 25, p4_tip_y + 12, "p4", font_size=5.5)
    draw_leader(c, p5_tip_x, p5_tip_y, p5_tip_x + 25, p5_tip_y + 12, "p5", font_size=5.5)

    # ── DIMENSIONS ──
    # Vertical: plate height (2'-2")
    draw_dimension_v(c, plate_left - 18, plate_bottom, plate_top, -18,
                    f'{_fmt_ft_in(cap_h)}', font_size=5.5)

    # Horizontal: plate width (14")
    draw_dimension_h(c, plate_left, plate_right, plate_top + 12, 10,
                    f'{cap_w:.0f}"', font_size=5.5)

    # Vertical bolt row spacing (1'-11")
    draw_dimension_v(c, plate_right + 15, bolt_y_bottom, bolt_y_top, 12,
                    f'1\'-11"', font_size=5)

    # Bolt hole diameter callout
    c.setFont("Helvetica", 4.5)
    c.setFillColor(CLR_DIM)
    c.drawCentredString(bolt_x_left - 8, bolt_y_bottom - 10, '13/16"')

    # Gusset leg dimensions (6")
    draw_dimension_h(c, p4_tip_x, p4_base_x, p4_tip_y + 8, 8, '6"', font_size=4.5)
    draw_dimension_v(c, p4_tip_x - 8, p4_base_y_down, p4_base_y_top, -8, '6"', font_size=4.5)

    draw_dimension_h(c, p5_base_x, p5_tip_x, p5_tip_y + 8, 8, '6"', font_size=4.5)
    draw_dimension_v(c, p5_tip_x + 8, p5_base_y_down, p5_base_y_top, 8, '6"', font_size=4.5)

    # Hypotenuse lengths
    c.setFont("Helvetica", 4.5)
    c.drawCentredString((p4_tip_x + p4_base_x) / 2 - 8, (p4_tip_y + p4_base_y_down) / 2,
                       f'{uphill_hyp:.1f}"')
    c.drawCentredString((p5_tip_x + p5_base_x) / 2 + 8, (p5_tip_y + p5_base_y_down) / 2,
                       f'{downhill_hyp:.1f}"')

    # Angle labels (85° and 95°)
    c.setFont("Helvetica", 4.5)
    c.drawString(p4_base_x - 20, p4_base_y_down + 5, "85°")
    c.drawString(p5_base_x + 5, p5_base_y_down + 5, "95°")

    # Column depth label
    c.setFont("Helvetica", 4.5)
    c.drawString(col_left + col_w / 2 - 4, col_bottom - 8, '8"')

    # ── VIEW LABEL and ANGLE ──
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(black)
    c.drawString(ox + 5, oy + 5, "A-A")
    c.setFont("Helvetica", 5)
    c.drawString(ox + 5, oy - 5, "5°")


def _draw_section_bb(c, data: Dict, ox: float, oy: float,
                     view_w: float, view_h: float):
    """
    Section B-B: Cross-section through column body.
    Shows box beam (14" x 8") formed by two CEE sections,
    with 4 rebar dots at corners (TYP) and material callout.
    """
    box_w = data["box_width"]   # 14"
    box_d = data["box_depth"]   # 8"

    margin = 10
    avail = min(view_w, view_h) - 2 * margin
    scale = avail / max(box_w, box_d) * 0.7

    sw = box_w * scale
    sd = box_d * scale
    cx = ox + view_w / 2
    cy = oy + view_h / 2 + 5

    # ── BOX OUTLINE (14" x 8") ──
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(THICK)
    c.rect(cx - sw/2, cy - sd/2, sw, sd)

    # ── CENTER SEAM LINE (dashed, represents weld seam) ──
    c.setStrokeColor(CLR_HIDDEN)
    c.setLineWidth(THIN)
    c.setDash([3, 2])
    c.line(cx - sw/2, cy, cx + sw/2, cy)
    c.setDash([])

    # ── REBAR DOTS: 4 filled circles at corners (TYP) ──
    if data["rebar_reinforced"]:
        rebar_r = 2.5
        c.setFillColor(CLR_REBAR)
        c.setLineWidth(THIN)
        c.setStrokeColor(CLR_REBAR)

        inset = 4 * scale
        corners = [
            (cx - sw/2 + inset, cy - sd/2 + inset),
            (cx + sw/2 - inset, cy - sd/2 + inset),
            (cx - sw/2 + inset, cy + sd/2 - inset),
            (cx + sw/2 - inset, cy + sd/2 - inset),
        ]
        for rx, ry in corners:
            c.circle(rx, ry, rebar_r, fill=1, stroke=1)

    # ── REBAR LABEL ──
    c.setFont("Helvetica", 4.5)
    c.setFillColor(CLR_REBAR)
    c.drawCentredString(cx, cy - sd/2 - 12, f'{data["rebar_size"]} REBAR TYP')

    # ── PIECE MARK: rb2 ──
    c.setFont("Helvetica", 5)
    c.setFillColor(CLR_DIM)
    draw_leader(c, cx - 5, cy, cx - 30, cy - 18, "rb2", font_size=5.5)

    # ── DIMENSIONS ──
    draw_dimension_h(c, cx - sw/2, cx + sw/2, cy + sd/2 + 10, 10,
                    f'{box_w:.0f}"', font_size=5.5)
    draw_dimension_v(c, cx + sw/2 + 10, cy - sd/2, cy + sd/2, 12,
                    f'{box_d:.0f}"', font_size=5.5)

    # ── MATERIAL CALLOUT ──
    c.setFont("Helvetica", 4.5)
    c.setFillColor(CLR_DIM)
    c.drawCentredString(cx, cy + sd/2 + 18,
                       f'2x CEE {data["cee_size"]} WELDED BOX')

    # ── VIEW LABEL ──
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(black)
    c.drawCentredString(cx, oy + 3, "SECTION B-B")


# ═══════════════════════════════════════════════════════════════════════════════
# BOM TABLE
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_bom_table(c, cfg: ShopDrawingConfig, data: Dict, ox: float, oy: float, w: float, h: float):
    """
    Bill of Materials table with headers and data rows for all components.
    Displays ship mark, piece mark, quantity, description, dimensions, grade, remarks, weight.
    """
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(THIN)

    headers = ["Ship", "Piece", "QTY", "Description", "FT", "IN", "GR.", "Remarks", "WT."]
    col_widths = [w*0.10, w*0.09, w*0.06, w*0.32, w*0.06, w*0.06, w*0.08, w*0.12, w*0.11]

    row_h = 7
    n_rows = 8
    table_h = n_rows * row_h

    # Table outline
    c.rect(ox, oy + h - table_h, w, table_h)

    # Header row
    hy = oy + h - row_h
    c.setFillColor(HexColor("#333333"))
    c.rect(ox, hy, w, row_h, fill=1)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 5)

    x_pos = ox
    for i, hdr in enumerate(headers):
        c.drawCentredString(x_pos + col_widths[i] / 2, hy + 1.5, hdr)
        x_pos += col_widths[i]

    # Column separators
    x_pos = ox
    for cw in col_widths[:-1]:
        x_pos += cw
        c.setStrokeColor(CLR_GRID)
        c.setLineWidth(HAIR)
        c.line(x_pos, oy + h - table_h, x_pos, oy + h)

    col_count = cfg.n_frames if cfg.frame_type == "tee" else cfg.n_frames * 2
    cee_total_wt = data["weight_lbs"] * col_count

    rows = [
        ["C1", "", str(col_count), "Columns", "", "", "", "", ""],
        ["C1", "", str(col_count * 2), f'CEE {data["cee_size"]}',
         f'{data["total_length_ft"]:.0f}', f'{int(data["total_length_in"] % 12)}',
         "80", f'G90', f'{cee_total_wt:.0f}'],
        ["", "p3", str(col_count),
         f'PL {data["cap_plate_thickness"]} x {data["cap_plate_width_in"]:.0f}" x {data["cap_plate_length_in"]:.0f}"',
         f'{int(data["cap_plate_length_in"]//12)}', f'{int(data["cap_plate_length_in"]%12)}',
         "", "A572", f'{col_count*10:.0f}'],
        ["", "p4", str(col_count * 2),
         f'PL {data["gusset_thickness"]} x {data["gusset_leg_in"]:.0f}" x {data["uphill_hyp_in"]:.1f}"',
         "0", f'{int(data["gusset_leg_in"])}', "", "A572", f'{col_count*2*5:.0f}'],
        ["", "p5", str(col_count * 2),
         f'PL {data["gusset_thickness"]} x {data["gusset_leg_in"]:.0f}" x {data["downhill_hyp_in"]:.0f}"',
         "0", f'{int(data["gusset_leg_in"])}', "", "A572", f'{col_count*2*4:.0f}'],
        ["", "rb2", str(4*col_count),
         f'{data["rebar_size"]} Rebar',
         f'{data["rebar_length_ft"]:.0f}', f'{int(data["rebar_length_in"] % 12)}',
         "60", "A706", f'{4*col_count*3:.0f}'],
    ]

    for r_idx, row in enumerate(rows):
        ry = hy - (r_idx + 1) * row_h

        if r_idx == 0:
            c.setFillColor(HexColor("#E0E0E0"))
            c.rect(ox, ry, w, row_h, fill=1)
            c.setFillColor(black)
            c.setFont("Helvetica-Bold", 5)
        else:
            c.setFillColor(black)
            c.setFont("Helvetica", 4.5)

        c.setStrokeColor(CLR_OBJECT)
        c.setLineWidth(HAIR)
        c.line(ox, ry, ox + w, ry)

        x_pos = ox
        for i, cell in enumerate(row):
            if cell == "":
                x_pos += col_widths[i]
                continue
            if i in [0, 3]:
                c.drawString(x_pos + 2, ry + 1.5, str(cell))
            else:
                c.drawCentredString(x_pos + col_widths[i] / 2, ry + 1.5, str(cell))
            x_pos += col_widths[i]

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
    Vertical title block strip along the right edge (Taos Sheriff style).
    Runs full height of page, ~1" wide. Text is rotated 90° to read sideways.
    """
    tb_w = 1.0 * inch
    tb_h = PAGE_H - 2 * MARGIN
    tb_x = PAGE_W - MARGIN - tb_w
    tb_y = MARGIN

    # Background
    c.setFillColor(CLR_TITLE_BG)
    c.rect(tb_x, tb_y, tb_w, tb_h, fill=1)

    # Outer border
    c.setStrokeColor(white)
    c.setLineWidth(MEDIUM)
    c.rect(tb_x, tb_y, tb_w, tb_h)

    fab = TITLE_BLOCK["fabricator"]
    mid_x = tb_x + tb_w / 2

    # ── Rotated text (read from bottom to top) ──
    c.saveState()
    c.translate(mid_x, tb_y + tb_h / 2)
    c.rotate(90)

    # Now we draw text along the rotated axis
    # x = position along the strip height, y = left/right within strip
    strip_len = tb_h
    half = strip_len / 2

    # Company info (top of strip = rightmost when rotated)
    c.setFillColor(CLR_TITLE_TEXT)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(half - 15, 4, fab["name"])
    c.setFont("Helvetica", 5)
    c.drawCentredString(half - 15, -4, f'{fab["address"]}')
    c.drawCentredString(half - 15, -10, f'{fab["city_state_zip"]}')
    c.setFont("Helvetica", 4.5)
    c.drawCentredString(half - 15, -17, f'Phone: {fab["phone"]}')
    c.drawCentredString(half - 15, -23, f'{fab["website"]}')

    # Project info
    c.setFont("Helvetica", 5)
    c.drawString(half - 80, 12, f'PROJECT: {cfg.project_name}')
    c.drawString(half - 80, 4, f'Customer: {cfg.customer_name}')

    # Drawing title (prominent, centered)
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(HexColor("#FFCC00"))
    c.drawCentredString(0, -2, f'{cfg.job_code}')
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(0, -14, f'A1 Column')

    # Bottom section (left of strip when rotated)
    c.setFillColor(CLR_TITLE_TEXT)
    c.setFont("Helvetica", 4.5)
    c.drawString(-half + 10, 12, f'Drafting Service: Structures America')
    c.drawString(-half + 10, 5, f'Drawn: {cfg.drawn_by or "AUTO"}')
    c.drawString(-half + 10, -2, f'Date: {datetime.date.today().strftime("%m/%d/%Y")}')
    c.setFont("Helvetica", 4)
    c.drawString(-half + 10, -9, f'Rev. No {revision}')
    c.drawString(-half + 10, -16, f'DWG. NO A1 Column')

    c.restoreState()


def _draw_project_notes(c, cfg, ox, oy, w, h, revision="-"):
    """
    Project-specific notes, revision table, and design authority disclaimer.
    Positioned in the bottom bar.
    """
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(THIN)
    c.rect(ox, oy, w, h)

    y = oy + h - 9
    c.setFont("Helvetica-Bold", 5)
    c.setFillColor(black)
    c.drawString(ox + 3, y, "Project Specific Notes (UNO): G90")

    c.setFont("Helvetica", 4.5)
    y -= 7
    c.drawString(ox + 3, y, "Material: A36 UNO")
    y -= 6
    c.drawString(ox + 3, y, "Paint: Cold Galv All Plain")
    y -= 6
    c.drawString(ox + 3, y, "Steel and Welds")
    y -= 6
    c.drawString(ox + 3, y, "Do Not Paint at the")
    y -= 6
    c.drawString(ox + 3, y, "location Indicated")

    # Revision table
    y -= 10
    c.setFont("Helvetica-Bold", 4.5)
    c.drawString(ox + 3, y, "Date       REV  Revision Description")
    y -= 6
    c.setFont("Helvetica", 4)
    c.drawString(ox + 3, y, f'{datetime.date.today().strftime("%m-%d-%y")}   {revision}    For Fabrication')
    y -= 6
    c.drawString(ox + 3, y, "                    For Approval")

    # Design/Review Authority
    y -= 10
    c.setFont("Helvetica-Bold", 4)
    c.drawString(ox + 3, y, "Design/Review Authority:")
    y -= 5
    c.setFont("Helvetica", 3.5)
    disclaimer = [
        "Please Review this Drawing Carefully.",
        "We assume NO responsibility for the",
        "accuracy of the information in the",
        "contract documents. This drawing",
        "represents our best interpretation.",
    ]
    for line in disclaimer:
        c.drawString(ox + 3, y, line)
        y -= 5


# ═══════════════════════════════════════════════════════════════════════════════
# STITCH WELD DETAIL CALLOUT
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_stitch_weld_detail(c, ox: float, oy: float, w: float, h: float):
    """
    Stitch weld detail callout graphic showing the weld pattern.
    5/16" size, 3-36 body pattern, 3-3 end pattern @ 6" O.C.
    """
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(THIN)
    c.rect(ox, oy, w, h)

    c.setFont("Helvetica-Bold", 5)
    c.setFillColor(CLR_DIM)
    c.drawString(ox + 3, oy + h - 8, "STITCH WELD DETAIL:")

    c.setFont("Helvetica", 4)
    c.setFillColor(black)
    y = oy + h - 14
    c.drawString(ox + 5, y, "5/16 size weld")
    y -= 6
    c.drawString(ox + 5, y, "3-36 body pattern")
    y -= 6
    c.drawString(ox + 5, y, "3-3 @ 6 OC first 12\" ends")


def _draw_weld_callout_graphic(c, ox: float, oy: float, w: float, h: float):
    """
    Graphic representation of the stitch weld pattern with arrows.
    """
    pass  # Simplified version inline in generate_column_drawing


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
    Generate a complete column shop drawing PDF with pixel-perfect layout.

    Page (11" x 8.5" landscape):
    - RIGHT STRIP (1" wide): vertical title block
    - CONTENT AREA: 4 views in structured zones
      - TOP ROW: Section A-A (left 35%), BOM table (right 45%)
      - MIDDLE ROW: Front View (full width, dominant 38% height)
      - BOTTOM ROW: Section B-B (left 22%), stitch weld detail (center), Side View (right 50%)
      - BOTTOM BAR (1.5" height): General Notes | Abbreviations | Project Notes

    Args:
        cfg: ShopDrawingConfig with project data
        col_index: Column index (0-based)
        output_path: Optional file path to save PDF
        revision: Revision letter/number

    Returns:
        PDF bytes
    """
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=landscape(letter))
    c.setTitle(f"Column {col_index + 1} Shop Drawing")

    data = _calc_column_data(cfg, col_index)

    # ── PAGE BORDER ──
    _draw_border(c)

    # ── LAYOUT ZONES ──
    draw_area_w = PAGE_W - 2 * MARGIN
    draw_area_h = PAGE_H - 2 * MARGIN

    title_strip_w = 1.0 * inch
    content_w = draw_area_w - title_strip_w

    bar_h = 1.5 * inch
    views_h = draw_area_h - bar_h

    # Top region: Section A-A (left) + BOM (right)
    sec_a_w = content_w * 0.28
    sec_a_h = views_h * 0.32
    sec_a_ox = MARGIN
    sec_a_oy = MARGIN + bar_h + views_h - sec_a_h

    bom_w = content_w * 0.42
    bom_h = views_h * 0.22
    bom_ox = MARGIN + content_w - bom_w
    bom_oy = MARGIN + bar_h + views_h - bom_h

    # Middle: Front View (dominant, full width)
    front_w = content_w
    front_h = views_h * 0.38
    front_ox = MARGIN
    front_oy = MARGIN + bar_h + views_h * 0.30

    # Bottom region: Section B-B (left) + stitch weld detail (center) + Side View (right)
    sec_b_w = content_w * 0.22
    sec_b_h = views_h * 0.30
    sec_b_ox = MARGIN
    sec_b_oy = MARGIN + bar_h

    side_w = content_w * 0.50
    side_h = views_h * 0.30
    side_ox = MARGIN + content_w - side_w
    side_oy = MARGIN + bar_h

    # Stitch weld detail (between B-B and Side View)
    weld_ox = sec_b_ox + sec_b_w + 5
    weld_oy = sec_b_oy + 2
    weld_box_w = (side_ox - weld_ox) - 10
    weld_box_h = sec_b_h * 0.6

    # ── DRAW ALL VIEWS ──
    _draw_front_view(c, data, front_ox, front_oy, front_w, front_h, cfg)
    _draw_side_view(c, data, side_ox, side_oy, side_w, side_h)
    _draw_section_aa(c, data, sec_a_ox, sec_a_oy, sec_a_w, sec_a_h)
    _draw_section_bb(c, data, sec_b_ox, sec_b_oy, sec_b_w, sec_b_h)

    # ── BOM TABLE ──
    _draw_bom_table(c, cfg, data, bom_ox, bom_oy, bom_w, bom_h)

    # ── STITCH WELD DETAIL ──
    if weld_box_w > 50:
        c.setStrokeColor(CLR_OBJECT)
        c.setLineWidth(THIN)
        c.rect(weld_ox, weld_oy, weld_box_w, weld_box_h)

        c.setFont("Helvetica-Bold", 5)
        c.setFillColor(CLR_DIM)
        c.drawString(weld_ox + 3, weld_oy + weld_box_h - 8, "STITCH WELD DETAIL:")

        c.setFont("Helvetica", 4)
        c.setFillColor(black)
        wy = weld_oy + weld_box_h - 16
        c.drawString(weld_ox + 5, wy, "5/16 weld  3-36 OC body")
        wy -= 7
        c.drawString(weld_ox + 5, wy, "3-3 @ 6 OC first 12\" ends")
        wy -= 7
        c.drawString(weld_ox + 5, wy, "All per WPS-\"B\"")

    # ── TITLE BLOCK (right vertical strip) ──
    _draw_title_block(c, cfg, data, revision=revision)

    # ── BOTTOM BAR: Notes sections ──
    notes_w = content_w * 0.35
    _draw_standard_notes(c, MARGIN, MARGIN, notes_w, bar_h)

    abbr_w = content_w * 0.30
    _draw_abbreviations(c, MARGIN + notes_w, MARGIN, abbr_w, bar_h)

    pn_ox = MARGIN + notes_w + abbr_w
    pn_w = content_w - notes_w - abbr_w
    _draw_project_notes(c, cfg, pn_ox, MARGIN, pn_w, bar_h, revision)

    # ── WEIGHT CALLOUT ──
    c.setFont("Helvetica-Bold", 5)
    c.setFillColor(CLR_DIM)
    c.drawString(sec_b_ox + 5, sec_b_oy + sec_b_h + 3,
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
