"""
Rafter Shop Drawing PDF Generator
Produces 8.5"x11" landscape PDF with multiple views:
  - Top View: purlin clip layout with spacing dimensions
  - Side View: rafter elevation showing depth, splice location, rebar
  - Section A-A: cross-section through body (box beam + rebar if reinforced)
  - Detail callouts: splice detail, clip details, weld callouts
Plus: title block, revision block, BOM table, WPS callouts, standard notes.

Key differences from column drawings:
  - Rafter is HORIZONTAL (shown from above for purlin layout)
  - Splice logic: rafter >53' triggers splice plates (roll formed, field-installed)
  - Rebar: only if reinforced (non-reinforced = NO rebar at all)
  - P2 cap clip at each end, P1 interior clips evenly spaced
  - Purlin layout always measured from one consistent end
"""

import math
import io
import os
import datetime
from typing import Dict, List, Optional, Tuple

from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.units import inch
from reportlab.lib.colors import (
    black, white, HexColor,
)
from reportlab.pdfgen import canvas

from shop_drawings.config import (
    RAFTER_DEFAULTS, COLUMN_DEFAULTS, WPS_CODES, STANDARD_NOTES,
    TITLE_BLOCK, ABBREVIATIONS, DRAWING_OUTPUT,
    ShopDrawingConfig, calc_rafter_length,
)
from shop_drawings.column_gen import (
    _fmt_ft_in, draw_dimension_h, draw_dimension_v,
    draw_leader, draw_section_marker, draw_weld_symbol,
    _draw_standard_notes, _draw_abbreviations, _draw_title_block as _col_title_block,
    _draw_border,
    CLR_OBJECT, CLR_DIM, CLR_HIDDEN, CLR_SECTION_CUT,
    CLR_WELD, CLR_REBAR, CLR_NOPAINT, CLR_TITLE_BG, CLR_TITLE_TEXT, CLR_GRID,
    PAGE_W, PAGE_H, MARGIN, DRAW_LEFT, DRAW_RIGHT, DRAW_TOP, DRAW_BOTTOM,
    THICK, MEDIUM, THIN, HAIR,
)


# ═══════════════════════════════════════════════════════════════════════════════
# RAFTER CALCULATION
# ═══════════════════════════════════════════════════════════════════════════════

def _calc_rafter_data(cfg: ShopDrawingConfig, rafter_index: int = 0) -> Dict:
    """
    Calculate all rafter dimensions and properties.
    """
    # Force all config values to correct numeric types
    cfg.ensure_numeric()

    slope_deg = float(cfg.roof_pitch_deg)
    use_z = cfg.raft_purlin_type == "z"

    # Rafter cut length:
    # width - 2*roofing_overhang - 7" (if z-purlins, 3.5" per side)
    rafter_length_ft = calc_rafter_length(
        cfg.building_width_ft,
        cfg.raft_roofing_overhang_ft,
        use_z
    )
    rafter_length_in = rafter_length_ft * 12.0

    # Slope length (actual along slope)
    half_w = cfg.building_width_ft / 2.0
    rise = half_w * math.tan(math.radians(slope_deg))
    slope_length_ft = 2.0 * math.sqrt(half_w**2 + rise**2)

    # Splice check
    needs_splice = rafter_length_ft > 53.0
    splice_pieces = []
    if needs_splice:
        # Splice must be within 10' of nearest column
        # For simplicity: split at midpoint or nearest allowed point
        mid = rafter_length_in / 2.0
        # Splice location: 6' from nearest rafter (column line) in mid-span
        splice_from_end_ft = min(rafter_length_ft / 2.0,
                                 RAFTER_DEFAULTS["splice_max_distance_from_column_ft"]
                                 + max(cfg.bay_sizes) / 2.0)
        splice_loc_in = splice_from_end_ft * 12.0

        piece_a = splice_loc_in
        piece_b = rafter_length_in - splice_loc_in
        splice_pieces = [
            {"label": "B1-A", "length_in": piece_a},
            {"label": "B1-B", "length_in": piece_b},
        ]
    else:
        splice_pieces = [
            {"label": "B1", "length_in": rafter_length_in},
        ]

    # Purlin clip layout
    # P2 cap at each end (welded all around), P1 interior clips evenly spaced
    purlin_spacing_in = cfg.purlin_spacing_ft * 12.0
    n_clips_total = max(2, math.floor(rafter_length_in / purlin_spacing_in) + 1)

    # Clip positions measured from left end
    clip_positions = []
    # First clip = P2 cap at position 0 (left end)
    clip_positions.append({"pos_in": 0, "type": "p2", "label": "P2 CAP"})

    # Interior P1 clips evenly spaced
    if n_clips_total > 2:
        actual_spacing = rafter_length_in / (n_clips_total - 1)
        for i in range(1, n_clips_total - 1):
            pos = i * actual_spacing
            clip_positions.append({"pos_in": pos, "type": "p1", "label": "P1"})

    # Last clip = P2 cap at end
    clip_positions.append({
        "pos_in": rafter_length_in, "type": "p2", "label": "P2 CAP"
    })

    # Rebar (only if reinforced)
    rebar_data = None
    if cfg.raft_reinforced:
        # 4 rebars at corners, placement:
        # 20' above each column, 20' between, within 5' of eave
        stick_ft = 40.0  # 40' rebar sticks
        sticks_per_side = max(1, math.ceil(
            max(0.0, rafter_length_ft - 10.0) / 20.0))
        sticks_per_rafter = 4 * sticks_per_side
        rebar_data = {
            "size": cfg.raft_rebar_size,
            "qty": sticks_per_rafter,
            "sticks_per_corner": sticks_per_side,
            "stick_length_ft": stick_ft,
        }

    # Connection plate (same as column cap plate)
    # Weight
    lbs_per_lft = 10.83
    weight_lbs = rafter_length_ft * 2 * lbs_per_lft

    mark = f"B{rafter_index + 1}"

    return {
        "mark": mark,
        "rafter_length_in": rafter_length_in,
        "rafter_length_ft": rafter_length_ft,
        "slope_length_ft": slope_length_ft,
        "building_width_ft": cfg.building_width_ft,
        "roofing_overhang_ft": cfg.raft_roofing_overhang_ft,
        "z_deduction_in": 7.0 if use_z else 0.0,
        "purlin_type": cfg.raft_purlin_type,
        "cee_size": "14x4x10GA",
        "material_grade": cfg.raft_material_grade,
        "box_width": 14.0,
        "box_depth": 8.0,
        "needs_splice": needs_splice,
        "splice_pieces": splice_pieces,
        "splice_plate": RAFTER_DEFAULTS["splice_plate"] if needs_splice else None,
        "n_clips": n_clips_total,
        "clip_positions": clip_positions,
        "purlin_spacing_in": purlin_spacing_in,
        "p1_clip": RAFTER_DEFAULTS["p1_clip"],
        "p2_clip": RAFTER_DEFAULTS["p2_clip"],
        "rebar": rebar_data,
        "reinforced": cfg.raft_reinforced,
        "stitch_weld": COLUMN_DEFAULTS["stitch_weld"],
        "connection_plate": {
            "thickness": "3/4\"",
            "width": 14.0,
            "length": 26.0,
        },
        "connection_bolts": cfg.col_connection_bolts,
        "weight_lbs": weight_lbs,
        "slope_deg": cfg.roof_pitch_deg,
        "frame_type": cfg.frame_type,
        "show_purlin_facing": cfg.raft_show_purlin_facing,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# TOP VIEW (Purlin Layout)
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_top_view(c, data: Dict, ox: float, oy: float,
                   view_w: float, view_h: float):
    """
    Top/plan view showing rafter with purlin clip positions.
    Horizontal orientation, clips shown as rectangles perpendicular to rafter.
    """
    rafter_in = data["rafter_length_in"]

    margin = 30
    avail_w = view_w - 2 * margin
    scale = avail_w / rafter_in

    # Rafter body (horizontal rectangle)
    rw = rafter_in * scale
    rh = data["box_width"] * scale  # 14" wide
    rx = ox + margin
    ry = oy + view_h / 2 - rh / 2

    # Rafter outline
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(THICK)
    c.rect(rx, ry, rw, rh)

    # Center seam (hidden line where two CEEs meet)
    c.setStrokeColor(CLR_HIDDEN)
    c.setLineWidth(THIN)
    c.setDash([3, 2])
    c.line(rx, ry + rh / 2, rx + rw, ry + rh / 2)
    c.setDash([])

    # ── Purlin clips ──
    clip_h_p1 = data["p1_clip"]["length"] * scale   # 10" long
    clip_w_p1 = data["p1_clip"]["width"] * scale     # 6" wide
    clip_h_p2 = data["p2_clip"]["length"] * scale    # 24" long
    clip_w_p2 = data["p2_clip"]["width"] * scale     # 9" wide

    for clip in data["clip_positions"]:
        pos_x = rx + clip["pos_in"] * scale
        if clip["type"] == "p2":
            # P2 cap — wider, shown in orange
            cw = clip_w_p2
            ch = clip_h_p2
            c.setStrokeColor(HexColor("#DD6600"))
            c.setFillColor(HexColor("#FFDDAA"))
            c.setLineWidth(MEDIUM)
            c.rect(pos_x - cw / 2, ry + rh / 2 - ch / 2, cw, ch, fill=1)
            # "WELD ALL AROUND" for P2
            c.setFont("Helvetica", 3.5)
            c.setFillColor(CLR_WELD)
            c.drawCentredString(pos_x, ry + rh / 2 - ch / 2 - 5,
                                "WELD ALL AROUND")
        else:
            # P1 interior clip
            cw = clip_w_p1
            ch = clip_h_p1
            c.setStrokeColor(CLR_OBJECT)
            c.setFillColor(HexColor("#E8E8F0"))
            c.setLineWidth(MEDIUM)
            c.rect(pos_x - cw / 2, ry + rh / 2 - ch / 2, cw, ch, fill=1)

    # ── Purlin facing arrows (when toggled on) ──
    if data.get("show_purlin_facing") and data.get("purlin_type") == "z":
        # Z-purlin facing rules:
        # Eave purlins (P2 caps at ends): top flange faces outward (away from center)
        # Interior purlins: alternate direction
        # Odd number rule: first two on bottom side face same direction
        n_interior = len([cl for cl in data["clip_positions"] if cl["type"] == "p1"])
        arrow_size = max(4, min(8, rh * 0.3))
        facing_y = ry + rh / 2  # center of rafter

        for i, clip in enumerate(data["clip_positions"]):
            pos_x = rx + clip["pos_in"] * scale

            if clip["type"] == "p2":
                # Eave purlins face outward (left end → arrow left, right end → arrow right)
                if clip["pos_in"] < rafter_in / 2:
                    direction = "left"
                else:
                    direction = "right"
            else:
                # Interior purlins alternate, starting from eave side
                # Interior clip index (0-based within interior clips only)
                interior_idx = sum(1 for c2 in data["clip_positions"][:i] if c2["type"] == "p1")
                # Odd number rule: first two face same (toward bottom/left)
                if n_interior % 2 == 1 and interior_idx < 2:
                    direction = "left"
                elif interior_idx % 2 == 0:
                    direction = "left"
                else:
                    direction = "right"

            # Draw facing arrow (small arrow above the clip)
            arrow_y_pos = facing_y + rh / 2 + arrow_size + 3
            c.setStrokeColor(HexColor("#0066CC"))
            c.setFillColor(HexColor("#0066CC"))
            c.setLineWidth(THIN)

            if direction == "left":
                # Arrow pointing left: ←
                c.line(pos_x + arrow_size, arrow_y_pos, pos_x - arrow_size, arrow_y_pos)
                # Arrowhead
                path = c.beginPath()
                path.moveTo(pos_x - arrow_size, arrow_y_pos)
                path.lineTo(pos_x - arrow_size + 3, arrow_y_pos + 2)
                path.lineTo(pos_x - arrow_size + 3, arrow_y_pos - 2)
                path.close()
                c.drawPath(path, fill=1)
            else:
                # Arrow pointing right: →
                c.line(pos_x - arrow_size, arrow_y_pos, pos_x + arrow_size, arrow_y_pos)
                path = c.beginPath()
                path.moveTo(pos_x + arrow_size, arrow_y_pos)
                path.lineTo(pos_x + arrow_size - 3, arrow_y_pos + 2)
                path.lineTo(pos_x + arrow_size - 3, arrow_y_pos - 2)
                path.close()
                c.drawPath(path, fill=1)

        # Legend for facing arrows
        legend_x = rx + rw - 120
        legend_y = ry - (25 if data["needs_splice"] else 15)
        c.setFont("Helvetica-Bold", 4.5)
        c.setFillColor(HexColor("#0066CC"))
        c.drawString(legend_x, legend_y, "PURLIN FACING")
        c.setFont("Helvetica", 4)
        c.drawString(legend_x, legend_y - 7,
                     "Arrows show Z-purlin top flange direction")

    # ── Spacing dimensions ──
    # Show dimensions between clips
    dim_y = ry + rh + 15
    prev_x = rx  # First clip at left edge
    for i, clip in enumerate(data["clip_positions"]):
        curr_x = rx + clip["pos_in"] * scale
        if i > 0:
            spacing_in = clip["pos_in"] - data["clip_positions"][i - 1]["pos_in"]
            if abs(curr_x - prev_x) > 8:  # Only label if enough room
                draw_dimension_h(c, prev_x, curr_x, dim_y, 8,
                                 _fmt_ft_in(spacing_in), font_size=5)
        prev_x = curr_x

    # Total length dimension
    draw_dimension_h(c, rx, rx + rw, dim_y, 25,
                     f'RAFTER: {_fmt_ft_in(rafter_in)}', font_size=6)

    # ── Splice location (if applicable) ──
    if data["needs_splice"]:
        splice_in = data["splice_pieces"][0]["length_in"]
        splice_x = rx + splice_in * scale
        c.setStrokeColor(CLR_SECTION_CUT)
        c.setLineWidth(MEDIUM)
        c.setDash([6, 3])
        c.line(splice_x, ry - 10, splice_x, ry + rh + 10)
        c.setDash([])

        # Splice callout
        c.setFont("Helvetica-Bold", 5)
        c.setFillColor(CLR_SECTION_CUT)
        c.drawCentredString(splice_x, ry - 15,
                            f'SPLICE @ {_fmt_ft_in(splice_in)}')

        # Piece labels
        c.setFont("Helvetica", 5)
        c.setFillColor(CLR_DIM)
        for piece in data["splice_pieces"]:
            px = rx + piece["length_in"] * scale / 2
            if piece == data["splice_pieces"][1]:
                px = splice_x + (rw - splice_in * scale) / 2
            c.drawCentredString(px, ry - 5, piece["label"])

    # ── Clip count callout ──
    n_p1 = sum(1 for cl in data["clip_positions"] if cl["type"] == "p1")
    n_p2 = sum(1 for cl in data["clip_positions"] if cl["type"] == "p2")
    c.setFont("Helvetica", 5)
    c.setFillColor(CLR_DIM)
    c.drawString(rx, ry - 20 - (10 if data["needs_splice"] else 0),
                 f'{n_p2}x P2 CAPS (9"x24" WELDED) + {n_p1}x P1 CLIPS (6"x10" TEK)')

    # ── Material callout (center of rafter) ──
    c.setFont("Helvetica-Bold", 5.5)
    c.setFillColor(CLR_DIM)
    c.drawCentredString(rx + rw / 2, ry + rh / 2 + 2,
                        f'CEE {data["cee_size"]} {data["material_grade"]}')

    # ── WPS callouts ──
    draw_weld_symbol(c, rx + rw * 0.15, ry - 3, "C", size=3)
    c.setFont("Helvetica", 4)
    c.setFillColor(CLR_WELD)
    c.drawString(rx + rw * 0.15 + 8, ry - 5, "(CLIP-TO-RAFTER)")

    # ── "START MEASUREMENTS FROM THIS SIDE" arrow ──
    c.setStrokeColor(CLR_NOPAINT)
    c.setLineWidth(MEDIUM)
    arrow_y = ry + rh + 45
    c.line(rx, arrow_y, rx + 60, arrow_y)
    # Arrowhead
    c.line(rx, arrow_y, rx + 6, arrow_y + 3)
    c.line(rx, arrow_y, rx + 6, arrow_y - 3)
    c.setFont("Helvetica-Bold", 5)
    c.setFillColor(CLR_NOPAINT)
    c.drawString(rx + 62, arrow_y - 2,
                 "START MEASUREMENTS FROM THIS SIDE")

    # View label
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(black)
    c.drawCentredString(ox + view_w / 2, oy + 5, "TOP VIEW — PURLIN LAYOUT")


# ═══════════════════════════════════════════════════════════════════════════════
# SIDE VIEW
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_rafter_side_view(c, data: Dict, ox: float, oy: float,
                           view_w: float, view_h: float):
    """
    Side elevation of rafter showing depth, end plates, rebar, splice.
    """
    rafter_in = data["rafter_length_in"]

    margin = 25
    avail_w = view_w - 2 * margin
    avail_h = view_h - 2 * margin
    scale_h = avail_w / rafter_in
    scale_v = avail_h / 30  # Vertical scale for 14" depth + extras
    scale = min(scale_h, scale_v * 2)

    rw = rafter_in * scale
    rd = data["box_depth"] * scale  # 8" depth
    rx = ox + margin
    ry = oy + view_h / 2 - rd / 2

    # Rafter body
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(THICK)
    c.rect(rx, ry, rw, rd)

    # End plates (connection plates at both ends)
    plate_w = 3 * scale
    c.setFillColor(HexColor("#E0E0E0"))
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(MEDIUM)
    # Left end plate
    c.rect(rx - plate_w, ry - 2, plate_w, rd + 4, fill=1)
    # Right end plate
    c.rect(rx + rw, ry - 2, plate_w, rd + 4, fill=1)
    c.setFillColor(black)

    # Bolt holes on end plates
    c.setFillColor(white)
    for px in [rx - plate_w / 2, rx + rw + plate_w / 2]:
        for by_off in [-rd * 0.25, rd * 0.25]:
            c.circle(px, ry + rd / 2 + by_off, 1.5, fill=1, stroke=1)

    # ── Rebar (if reinforced) ──
    if data["rebar"]:
        c.setStrokeColor(CLR_REBAR)
        c.setLineWidth(MEDIUM)
        c.setDash([4, 3])
        inset = 2.5 * scale
        for ry_off in [ry + inset, ry + rd - inset]:
            c.line(rx + 5, ry_off, rx + rw - 5, ry_off)
        c.setDash([])

        # Rebar callout
        rb = data["rebar"]
        c.setFont("Helvetica", 4.5)
        c.setFillColor(CLR_REBAR)
        c.drawCentredString(rx + rw / 2, ry - 10,
                            f'{rb["size"]} A706 REBAR x {rb["qty"]} EA '
                            f'(INSIDE, {rb["sticks_per_corner"]} STICK/CORNER)')
        draw_weld_symbol(c, rx + rw * 0.3, ry + rd + 3, "D", size=3)

    # ── Splice location ──
    if data["needs_splice"]:
        splice_in = data["splice_pieces"][0]["length_in"]
        splice_x = rx + splice_in * scale
        c.setStrokeColor(CLR_SECTION_CUT)
        c.setLineWidth(MEDIUM)
        c.setDash([4, 2])
        c.line(splice_x, ry - 8, splice_x, ry + rd + 8)
        c.setDash([])

        # Splice plate (sits on top)
        sp_w = 18 * scale  # ~18" splice overlap zone
        c.setStrokeColor(HexColor("#AA4400"))
        c.setFillColor(HexColor("#FFEECC"))
        c.setLineWidth(THIN)
        c.rect(splice_x - sp_w / 2, ry + rd, sp_w, 3, fill=1)
        c.setFont("Helvetica", 4)
        c.setFillColor(HexColor("#AA4400"))
        c.drawCentredString(splice_x, ry + rd + 8,
                            f'SPLICE PL {RAFTER_DEFAULTS["splice_plate"]["material"]} '
                            f'{RAFTER_DEFAULTS["splice_plate"]["width"]} x '
                            f'{RAFTER_DEFAULTS["splice_plate"]["length"]}')

    # ── Stitch weld marks ──
    sw = data["stitch_weld"]
    n_marks = max(3, int(rw / 40))
    c.setStrokeColor(CLR_WELD)
    c.setLineWidth(THIN)
    for i in range(1, n_marks):
        wx = rx + i * (rw / n_marks)
        c.line(wx - 2, ry + rd, wx, ry + rd + 3)
        c.line(wx, ry + rd + 3, wx + 2, ry + rd)

    # Weld callout
    draw_leader(c, rx + rw * 0.7, ry + rd + 2,
                rx + rw * 0.7 + 25, ry + rd + 15,
                f'STITCH WELD {sw["size"]} {sw["pattern"]} WPS-"B"',
                font_size=4.5)

    # End weld
    draw_weld_symbol(c, rx + 5, ry + rd + 3, "F", size=3)

    # ── Dimensions ──
    # Total length
    draw_dimension_h(c, rx, rx + rw, ry - 15 - (8 if data["rebar"] else 0), 8,
                     _fmt_ft_in(rafter_in), font_size=6)

    # Depth
    draw_dimension_v(c, rx + rw, ry, ry + rd, 12 + plate_w,
                     f'{data["box_depth"]:.0f}"', font_size=5.5)

    # ── "DO NOT PAINT" zones at ends ──
    np_w = 6 * scale
    c.setStrokeColor(CLR_NOPAINT)
    c.setLineWidth(THIN)
    c.setDash([2, 2])
    c.rect(rx, ry + 1, np_w, rd - 2)
    c.rect(rx + rw - np_w, ry + 1, np_w, rd - 2)
    c.setDash([])

    # ── Section cut A-A ──
    aa_x = rx + rw * 0.35
    c.setStrokeColor(CLR_SECTION_CUT)
    c.setLineWidth(MEDIUM)
    c.setDash([8, 3, 2, 3])
    c.line(aa_x, ry - 10, aa_x, ry + rd + 10)
    c.setDash([])
    draw_section_marker(c, aa_x, ry - 15, "A", size=7)
    draw_section_marker(c, aa_x, ry + rd + 15, "A", size=7)

    # View label
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(black)
    c.drawCentredString(ox + view_w / 2, oy + 5, "SIDE VIEW")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION A-A (Cross section)
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_rafter_section_aa(c, data: Dict, ox: float, oy: float,
                            view_w: float, view_h: float):
    """
    Cross section through rafter body — same box beam as column
    but with clip attachment shown.
    """
    box_w = data["box_width"]   # 14"
    box_d = data["box_depth"]   # 8"

    margin = 12
    avail = min(view_w, view_h) - 2 * margin
    scale = avail / max(box_w, box_d) * 0.5

    sw = box_w * scale
    sd = box_d * scale
    cx = ox + view_w / 2
    cy = oy + view_h / 2 + 3

    # Box beam outline
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(THICK)
    c.rect(cx - sw / 2, cy - sd / 2, sw, sd)

    # Inner void
    wall_t = 4
    c.setStrokeColor(CLR_HIDDEN)
    c.setLineWidth(THIN)
    c.rect(cx - sw / 2 + wall_t, cy - sd / 2 + wall_t,
           sw - 2 * wall_t, sd - 2 * wall_t)

    # Center seam
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(MEDIUM)
    c.line(cx, cy - sd / 2, cx, cy + sd / 2)

    # WPS weld mark
    draw_weld_symbol(c, cx, cy + sd / 2 + 2, "B", size=3)

    # Rebar (if reinforced)
    if data["reinforced"]:
        c.setFillColor(CLR_REBAR)
        rebar_r = 2.5
        inset = 5
        for rx_s, ry_s in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            c.circle(cx + rx_s * (sw / 2 - inset - rebar_r),
                     cy + ry_s * (sd / 2 - inset - rebar_r),
                     rebar_r, fill=1, stroke=1)
        c.setFont("Helvetica", 4)
        c.setFillColor(CLR_REBAR)
        c.drawCentredString(cx, cy - sd / 2 - 8,
                            f'{data["rebar"]["size"]} REBAR (INSIDE) TYP 4 PL')
    else:
        c.setFont("Helvetica", 4)
        c.setFillColor(CLR_DIM)
        c.drawCentredString(cx, cy - sd / 2 - 8, "NO REBAR (NON-REINFORCED)")

    # P1 clip shown attached to top
    clip_w = data["p1_clip"]["width"] * scale
    clip_h = 2  # Thin in cross-section
    c.setStrokeColor(CLR_OBJECT)
    c.setFillColor(HexColor("#E8E8F0"))
    c.setLineWidth(MEDIUM)
    c.rect(cx - clip_w / 2, cy + sd / 2, clip_w, clip_h * 2, fill=1)
    c.setFont("Helvetica", 3.5)
    c.setFillColor(CLR_DIM)
    c.drawCentredString(cx, cy + sd / 2 + clip_h * 2 + 5, "P1 CLIP")

    # Dimensions
    draw_dimension_h(c, cx - sw / 2, cx + sw / 2,
                     cy + sd / 2 + clip_h * 2 + 8, 8,
                     f'{box_w:.0f}"', font_size=5)
    draw_dimension_v(c, cx + sw / 2, cy - sd / 2, cy + sd / 2, 8,
                     f'{box_d:.0f}"', font_size=5)

    c.setFont("Helvetica-Bold", 6)
    c.setFillColor(black)
    c.drawCentredString(cx, oy + 5, "SECTION A-A")


# ═══════════════════════════════════════════════════════════════════════════════
# SPLICE DETAIL (when applicable)
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_splice_detail(c, data: Dict, ox: float, oy: float,
                        view_w: float, view_h: float):
    """
    Enlarged splice plate detail — shown only when rafter >53'.
    If no splice needed, shows clip detail instead.
    """
    cx = ox + view_w / 2
    cy = oy + view_h / 2

    if data["needs_splice"]:
        sp = data["splice_plate"]

        # Enlarged splice zone
        zoom_scale = 2.0
        rd = data["box_depth"] * zoom_scale
        gap = 3  # Gap between rafter pieces

        # Left rafter piece
        lw = 35
        c.setStrokeColor(CLR_OBJECT)
        c.setLineWidth(THICK)
        c.rect(cx - lw - gap / 2, cy - rd / 2, lw, rd)

        # Right rafter piece
        c.rect(cx + gap / 2, cy - rd / 2, lw, rd)

        # Splice plate on top
        sp_w = lw * 1.5
        sp_h = 4
        c.setFillColor(HexColor("#FFEECC"))
        c.setStrokeColor(HexColor("#AA4400"))
        c.setLineWidth(MEDIUM)
        c.rect(cx - sp_w / 2, cy + rd / 2, sp_w, sp_h, fill=1)

        # Tek screw marks (8 per splice)
        c.setFillColor(CLR_OBJECT)
        for i in range(8):
            sx = cx - sp_w / 2 + (i + 0.5) * (sp_w / 8)
            c.circle(sx, cy + rd / 2 + sp_h / 2, 1, fill=1)

        # Labels
        c.setFont("Helvetica", 4.5)
        c.setFillColor(CLR_DIM)
        c.drawCentredString(cx, cy + rd / 2 + sp_h + 8,
                            f'SPLICE PL {sp["material"]} {sp["width"]} x {sp["length"]}')
        c.drawCentredString(cx, cy + rd / 2 + sp_h + 16,
                            f'8x #10 TEK SCREWS + FIELD WELD')
        c.drawCentredString(cx, cy - rd / 2 - 8,
                            "SPLICE SITS ON TOP OF RAFTER")
        c.drawCentredString(cx, cy - rd / 2 - 16,
                            f'ROLL FORMED IN SHOP ON C1 MACHINE')

        c.setFont("Helvetica-Bold", 6)
        c.setFillColor(black)
        c.drawCentredString(cx, oy + 5, "SPLICE DETAIL")
    else:
        # Show P1 and P2 clip details instead
        # P2 cap
        p2 = data["p2_clip"]
        c.setStrokeColor(CLR_OBJECT)
        c.setFillColor(HexColor("#FFDDAA"))
        c.setLineWidth(MEDIUM)
        p2w = p2["width"] * 2.5
        p2h = p2["length"] * 1.5
        c.rect(cx - p2w - 10, cy - p2h / 2, p2w, p2h, fill=1)

        c.setFont("Helvetica", 4.5)
        c.setFillColor(CLR_DIM)
        c.drawCentredString(cx - p2w / 2 - 10, cy - p2h / 2 - 8,
                            f'P2 CAP: PL 1/8 x {p2["width"]}" x {p2["length"]}"')
        c.drawCentredString(cx - p2w / 2 - 10, cy - p2h / 2 - 16,
                            "WELDED ALL AROUND")

        # P1 clip
        p1 = data["p1_clip"]
        p1w = p1["width"] * 2.5
        p1h = p1["length"] * 1.5
        c.setFillColor(HexColor("#E8E8F0"))
        c.rect(cx + 10, cy - p1h / 2, p1w, p1h, fill=1)

        c.setFillColor(CLR_DIM)
        c.drawCentredString(cx + 10 + p1w / 2, cy - p1h / 2 - 8,
                            f'P1 CLIP: PL 1/8 x {p1["width"]}" x {p1["length"]}"')
        c.drawCentredString(cx + 10 + p1w / 2, cy - p1h / 2 - 16,
                            f'8x TEK SCREWS WPS-"C"')

        c.setFont("Helvetica-Bold", 6)
        c.setFillColor(black)
        c.drawCentredString(cx, oy + 5, "CLIP DETAILS")


# ═══════════════════════════════════════════════════════════════════════════════
# BOM TABLE (Rafter)
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_rafter_bom(c, data: Dict, ox: float, oy: float, w: float, h: float):
    """Mini BOM table for rafter parts."""
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(THIN)

    headers = ["MARK", "QTY", "DESCRIPTION", "SIZE", "MATERIAL"]
    col_widths = [w * 0.09, w * 0.07, w * 0.34, w * 0.24, w * 0.26]

    row_h = 9
    rows_data = [
        [data["mark"], "2", "CEE Section (Box Beam)",
         data["cee_size"], data["material_grade"]],
        [data["mark"], "2", "Connection Plate",
         f'{data["connection_plate"]["thickness"]} x '
         f'{data["connection_plate"]["width"]:.0f}" x '
         f'{data["connection_plate"]["length"]:.0f}"',
         "A572 Gr 50"],
    ]

    # P2 clips
    n_p2 = sum(1 for cl in data["clip_positions"] if cl["type"] == "p2")
    rows_data.append([data["mark"], str(n_p2), "P2 Cap Clip",
                      f'1/8" x {data["p2_clip"]["width"]}" x {data["p2_clip"]["length"]}"',
                      "A572"])

    # P1 clips
    n_p1 = sum(1 for cl in data["clip_positions"] if cl["type"] == "p1")
    if n_p1 > 0:
        rows_data.append([data["mark"], str(n_p1), "P1 Interior Clip",
                          f'1/8" x {data["p1_clip"]["width"]}" x {data["p1_clip"]["length"]}"',
                          "A572"])

    # Rebar (if reinforced)
    if data["rebar"]:
        rb = data["rebar"]
        rows_data.append([data["mark"], str(rb["qty"]),
                          f'Rebar ({rb["sticks_per_corner"]}/corner)',
                          f'{rb["size"]} x 40\'', "A706"])

    # Splice plates
    if data["needs_splice"]:
        rows_data.append([data["mark"], "2", "Splice Plate (FIELD)",
                          f'{data["splice_plate"]["material"]} '
                          f'{data["splice_plate"]["width"]}',
                          "G90"])

    n_rows = len(rows_data) + 1  # +1 for header
    table_h = n_rows * row_h

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

    # Column separators
    x_pos = ox
    for cw_val in col_widths[:-1]:
        x_pos += cw_val
        c.setStrokeColor(CLR_GRID)
        c.setLineWidth(HAIR)
        c.line(x_pos, oy + h - table_h, x_pos, oy + h)

    # Data rows
    c.setFillColor(black)
    c.setFont("Helvetica", 4.5)
    for r_idx, row in enumerate(rows_data):
        ry_pos = hy - (r_idx + 1) * row_h
        if r_idx % 2 == 1:
            c.setFillColor(HexColor("#F5F5F5"))
            c.rect(ox, ry_pos, w, row_h, fill=1)
            c.setFillColor(black)
        c.setStrokeColor(CLR_GRID)
        c.setLineWidth(HAIR)
        c.line(ox, ry_pos, ox + w, ry_pos)
        x_pos = ox
        for i, cell in enumerate(row):
            c.drawCentredString(x_pos + col_widths[i] / 2, ry_pos + 3, str(cell))
            x_pos += col_widths[i]

    c.setFont("Helvetica-Bold", 5.5)
    c.setFillColor(black)
    c.drawCentredString(ox + w / 2, oy + h - table_h - 8, "BILL OF MATERIALS")


# ═══════════════════════════════════════════════════════════════════════════════
# TITLE BLOCK (Rafter version)
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_rafter_title_block(c, cfg: ShopDrawingConfig, data: Dict,
                             sheet_num: int = 1, total_sheets: int = 1,
                             revision: str = "-"):
    """Title block — same layout as column but with rafter title."""
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

    # Drawing title
    y -= 10
    c.setFont("Helvetica-Bold", 8)
    title = f'RAFTER {data["mark"]}'
    if data["needs_splice"]:
        title += " (SPLICED)"
    c.drawCentredString(tb_x + tb_w / 2, y, title)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

def generate_rafter_drawing(
    cfg: ShopDrawingConfig,
    rafter_index: int = 0,
    output_path: Optional[str] = None,
    revision: str = "-",
) -> bytes:
    """
    Generate a complete rafter shop drawing PDF.

    Args:
        cfg: ShopDrawingConfig with all project/building data
        rafter_index: Rafter index (0-based) for mark numbering
        output_path: If given, save PDF to this path
        revision: Revision letter for title block

    Returns:
        PDF bytes
    """
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=landscape(letter))
    c.setTitle(f"Rafter {rafter_index + 1} Shop Drawing")

    data = _calc_rafter_data(cfg, rafter_index)

    _draw_border(c)

    # ── Layout ──
    # Top half: Top View (purlin layout) — full width
    # Bottom half split: Side View (left 55%) | Section A-A (right top) | Detail (right bottom)
    # Bottom bar: Notes + BOM + Title Block

    draw_area_w = PAGE_W - 2 * MARGIN
    draw_area_h = PAGE_H - 2 * MARGIN
    bar_h = 1.5 * inch

    views_h = draw_area_h - bar_h
    top_h = views_h * 0.5
    bot_h = views_h * 0.5

    # Top view = full width, upper half
    _draw_top_view(c, data, MARGIN, MARGIN + bar_h + bot_h,
                   draw_area_w, top_h)

    # Bottom left: Side view (60%)
    side_w = draw_area_w * 0.6
    _draw_rafter_side_view(c, data, MARGIN, MARGIN + bar_h,
                           side_w, bot_h)

    # Bottom right: split into Section A-A (top) and Detail (bottom)
    right_w = draw_area_w * 0.4
    right_ox = MARGIN + side_w
    right_top_h = bot_h * 0.5
    right_bot_h = bot_h * 0.5

    _draw_rafter_section_aa(c, data, right_ox, MARGIN + bar_h + right_bot_h,
                            right_w, right_top_h)
    _draw_splice_detail(c, data, right_ox, MARGIN + bar_h,
                        right_w, right_bot_h)

    # ── View dividers ──
    c.setStrokeColor(CLR_GRID)
    c.setLineWidth(HAIR)
    c.setDash([4, 4])
    # Horizontal between top and bottom views
    c.line(MARGIN, MARGIN + bar_h + bot_h,
           MARGIN + draw_area_w, MARGIN + bar_h + bot_h)
    # Vertical between side and right views
    c.line(right_ox, MARGIN + bar_h, right_ox, MARGIN + bar_h + bot_h)
    # Horizontal split in right column
    c.line(right_ox, MARGIN + bar_h + right_bot_h,
           MARGIN + draw_area_w, MARGIN + bar_h + right_bot_h)
    c.setDash([])

    # ── Bottom bar ──
    notes_w = draw_area_w * 0.28
    _draw_standard_notes(c, MARGIN, MARGIN, notes_w, bar_h)

    abbr_w = draw_area_w * 0.12
    _draw_abbreviations(c, MARGIN + notes_w, MARGIN, abbr_w, bar_h)

    bom_w = draw_area_w * 0.28
    _draw_rafter_bom(c, data, MARGIN + notes_w + abbr_w, MARGIN, bom_w, bar_h)

    _draw_rafter_title_block(c, cfg, data, revision=revision)

    # Weight
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


def generate_all_rafter_drawings(
    cfg: ShopDrawingConfig,
    output_dir: str,
    revision: str = "-",
) -> List[str]:
    """
    Generate shop drawings for all unique rafter types.
    Returns list of output file paths.
    """
    paths = []

    # For symmetric buildings, all rafters are the same
    # Future: handle different building widths per building
    path = os.path.join(output_dir, f"{cfg.job_code}_B1.pdf")
    generate_rafter_drawing(cfg, rafter_index=0, output_path=path, revision=revision)
    paths.append(path)

    return paths
