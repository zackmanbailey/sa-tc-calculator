"""
Purlin Group Shop Drawing PDF Generator
Produces 8.5"x11" landscape PDF showing purlin groups.

Purlin layout algorithm (Z-purlins with overhang):
  - First/Last purlins: overhang past internal rafters, land on end rafter center
  - Middle purlins: overhang both ends equally past the bays they span
  - End extension: 4" past center of end rafter
  - Z-purlins overhang 6' past internal rafters by default
  - Max individual purlin length: 53' (hard error)
  - Splice: 6' from rafter in mid-span, 6" overlap, 8 tek screws, sits on top

  C-purlins: no overhang, land on center, can span up to 3 rafters if <53'

Groups per building:
  - PG-A (First): end purlin
  - PG-B (Middle): interior purlins (may be different lengths if bays vary)
  - PG-C (Last): end purlin (same length as First, just flipped Z orientation)

Each group drawing shows:
  - 3D profile view of the Z or C purlin cross-section
  - Length dimension with overhang markers
  - Endcap callout
  - Splice location (if needed)
  - Ship mark, BOM table, title block
"""

import math
import io
import os
import datetime
from typing import Dict, List, Optional, Tuple

from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.units import inch
from reportlab.lib.colors import black, white, HexColor
from reportlab.pdfgen import canvas

from shop_drawings.config import (
    PURLIN_DEFAULTS, STANDARD_NOTES, TITLE_BLOCK,
    ABBREVIATIONS, ShopDrawingConfig,
)
from shop_drawings.column_gen import (
    _fmt_ft_in, draw_dimension_h, draw_dimension_v,
    draw_leader, _draw_standard_notes, _draw_abbreviations,
    _draw_border,
    CLR_OBJECT, CLR_DIM, CLR_HIDDEN, CLR_SECTION_CUT,
    CLR_WELD, CLR_REBAR, CLR_NOPAINT, CLR_TITLE_BG, CLR_TITLE_TEXT, CLR_GRID,
    PAGE_W, PAGE_H, MARGIN,
    THICK, MEDIUM, THIN, HAIR,
)


# ═══════════════════════════════════════════════════════════════════════════════
# PURLIN GROUP CALCULATIONS
# ═══════════════════════════════════════════════════════════════════════════════

def calc_purlin_groups(cfg: ShopDrawingConfig) -> List[Dict]:
    """
    Calculate purlin groups for the building.

    Z-purlin overhang algorithm:
      First purlin (PG-A):
        - Left end: extend 4" past center of end rafter (building end)
        - Right end: overhang 6' past the first internal rafter
        - Length = bay_size + 4" + 6' overhang (measured from end rafter center)

      Middle purlin (PG-B):
        - Overhangs 6' past each rafter on both sides
        - But positioned so it covers the bay(s) between two rafters
        - Length = bay_size + 2 * 6' overhang? No — it spans one bay with
          6' overhang each side if possible, but can't exceed 53'
        - Actually: purlin spans from splice-to-splice or rafter-to-rafter
          with 6' overhang past each rafter at the ends of its span

      Last purlin (PG-C):
        - Mirror of First (same length, flipped Z orientation)

    For equal bays (most common case):
      First/Last = bay_size_ft + 4"/12 + overhang_ft
      Middle = bay_size_ft + 2 * overhang_ft

    Splice: if any purlin > 53', it must be spliced.
    Splice location: 6' from rafter toward mid-span.

    C-purlins: no overhang, land on center of each rafter.
      First/Last = bay_size_ft + 4"/12 (end extension)
      Middle = bay_size_ft (exact bay span)
      Can span up to 3 rafters if total < 53'
    """
    # Force all config values to correct numeric types
    cfg.ensure_numeric()

    groups = []
    use_z = cfg.purlin_type == "z"
    overhang_ft = float(cfg.purlin_overhang_ft) if use_z else 0.0
    end_ext_in = float(cfg.purlin_end_extension_in)  # 4"
    end_ext_ft = end_ext_in / 12.0
    max_length_ft = PURLIN_DEFAULTS["max_length_ft"]  # 53'
    bay_sizes = cfg.bay_sizes if cfg.bay_sizes else [30.0]

    # Splice settings
    splice_from_rafter_ft = cfg.purlin_splice_location_ft  # 6'
    splice_overlap_in = cfg.purlin_splice_overlap_in        # 6"

    # ── First purlin (PG-A) ──
    first_bay = bay_sizes[0]
    if use_z:
        # 4" end extension + first bay + 6' overhang past first internal rafter
        first_length_ft = end_ext_ft + first_bay + overhang_ft
    else:
        # C-purlin: end extension + first bay (land on center)
        first_length_ft = end_ext_ft + first_bay

    first_needs_splice = first_length_ft > max_length_ft
    first_splice = None
    if first_needs_splice:
        # Splice 6' from the internal rafter toward the end
        splice_pos_ft = first_length_ft - splice_from_rafter_ft
        first_splice = {
            "position_ft": splice_pos_ft,
            "position_in": splice_pos_ft * 12,
            "overlap_in": splice_overlap_in,
            "tek_screws": PURLIN_DEFAULTS["splice_tek_screws"],
        }

    groups.append({
        "group_id": "PG-A",
        "label": "FIRST PURLIN",
        "length_ft": first_length_ft,
        "length_in": first_length_ft * 12,
        "end_extension_in": end_ext_in,
        "overhang_ft": overhang_ft if use_z else 0,
        "bay_span_ft": first_bay,
        "needs_splice": first_needs_splice,
        "splice": first_splice,
        "purlin_type": cfg.purlin_type,
        "profile": PURLIN_DEFAULTS["profile"],
        "qty_per_building": 1,  # Will be multiplied by purlin lines
        "mirror_of": None,
        "is_first": True,
        "is_last": False,
    })

    # ── Middle purlins (PG-B, PG-B2, etc.) ──
    # For each unique interior bay size, create a group
    unique_bays = {}
    for i, bay in enumerate(bay_sizes):
        if i == 0 or i == len(bay_sizes) - 1:
            continue  # Skip first and last (handled by First/Last groups)
        bay_key = round(bay, 4)
        if bay_key not in unique_bays:
            unique_bays[bay_key] = {"bay_ft": bay, "count": 0}
        unique_bays[bay_key]["count"] += 1

    # If only 1 or 2 bays, middle might use the same bay size
    if len(bay_sizes) == 1:
        # Single bay size for all — middle purlins span 1 bay each
        mid_bay = bay_sizes[0]
        if use_z:
            mid_length_ft = mid_bay + 2 * overhang_ft
        else:
            mid_length_ft = mid_bay

        mid_needs_splice = mid_length_ft > max_length_ft
        mid_splice = None
        if mid_needs_splice:
            splice_pos_ft = mid_length_ft / 2 - splice_from_rafter_ft
            mid_splice = {
                "position_ft": splice_pos_ft,
                "position_in": splice_pos_ft * 12,
                "overlap_in": splice_overlap_in,
                "tek_screws": PURLIN_DEFAULTS["splice_tek_screws"],
            }

        n_middle = max(0, cfg.n_frames - 2)  # Frames minus the two end bays
        if n_middle > 0:
            groups.append({
                "group_id": "PG-B",
                "label": "MIDDLE PURLIN",
                "length_ft": mid_length_ft,
                "length_in": mid_length_ft * 12,
                "end_extension_in": 0,
                "overhang_ft": overhang_ft if use_z else 0,
                "bay_span_ft": mid_bay,
                "needs_splice": mid_needs_splice,
                "splice": mid_splice,
                "purlin_type": cfg.purlin_type,
                "profile": PURLIN_DEFAULTS["profile"],
                "qty_per_building": n_middle,
                "mirror_of": None,
                "is_first": False,
                "is_last": False,
            })
    else:
        # Multiple bay sizes — create groups for each unique interior bay
        group_idx = 0
        for bay_key, info in sorted(unique_bays.items()):
            group_idx += 1
            suffix = f"B{group_idx}" if len(unique_bays) > 1 else "B"
            mid_bay = info["bay_ft"]
            if use_z:
                mid_length_ft = mid_bay + 2 * overhang_ft
            else:
                mid_length_ft = mid_bay

            mid_needs_splice = mid_length_ft > max_length_ft
            mid_splice = None
            if mid_needs_splice:
                splice_pos_ft = mid_length_ft / 2 - splice_from_rafter_ft
                mid_splice = {
                    "position_ft": splice_pos_ft,
                    "position_in": splice_pos_ft * 12,
                    "overlap_in": splice_overlap_in,
                    "tek_screws": PURLIN_DEFAULTS["splice_tek_screws"],
                }

            groups.append({
                "group_id": f"PG-{suffix}",
                "label": f"MIDDLE PURLIN ({mid_bay:.1f}' BAY)",
                "length_ft": mid_length_ft,
                "length_in": mid_length_ft * 12,
                "end_extension_in": 0,
                "overhang_ft": overhang_ft if use_z else 0,
                "bay_span_ft": mid_bay,
                "needs_splice": mid_needs_splice,
                "splice": mid_splice,
                "purlin_type": cfg.purlin_type,
                "profile": PURLIN_DEFAULTS["profile"],
                "qty_per_building": info["count"],
                "mirror_of": None,
                "is_first": False,
                "is_last": False,
            })

    # ── Last purlin (PG-C) — mirror of First ──
    last_bay = bay_sizes[-1] if len(bay_sizes) > 1 else bay_sizes[0]
    if use_z:
        last_length_ft = end_ext_ft + last_bay + overhang_ft
    else:
        last_length_ft = end_ext_ft + last_bay

    last_needs_splice = last_length_ft > max_length_ft
    last_splice = None
    if last_needs_splice:
        splice_pos_ft = last_length_ft - splice_from_rafter_ft
        last_splice = {
            "position_ft": splice_pos_ft,
            "position_in": splice_pos_ft * 12,
            "overlap_in": splice_overlap_in,
            "tek_screws": PURLIN_DEFAULTS["splice_tek_screws"],
        }

    groups.append({
        "group_id": "PG-C",
        "label": "LAST PURLIN (MIRROR OF FIRST)",
        "length_ft": last_length_ft,
        "length_in": last_length_ft * 12,
        "end_extension_in": end_ext_in,
        "overhang_ft": overhang_ft if use_z else 0,
        "bay_span_ft": last_bay,
        "needs_splice": last_needs_splice,
        "splice": last_splice,
        "purlin_type": cfg.purlin_type,
        "profile": PURLIN_DEFAULTS["profile"],
        "qty_per_building": 1,
        "mirror_of": "PG-A",
        "is_first": False,
        "is_last": True,
    })

    # Validate: error if any >53'
    for g in groups:
        if g["length_ft"] > max_length_ft and not g["needs_splice"]:
            g["error"] = f'Length {g["length_ft"]:.1f}\' exceeds max {max_length_ft}\''

    return groups


# ═══════════════════════════════════════════════════════════════════════════════
# Z-PURLIN PROFILE DRAWING
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_z_profile(c, cx: float, cy: float, scale: float = 1.5,
                    flipped: bool = False):
    """
    Draw Z-purlin cross-section profile.
    12" height, 3.5" flanges, 3/4" lips at 45°.
    """
    h = 12 * scale       # Web height
    f = 3.5 * scale      # Flange width
    lip = 0.75 * scale   # Lip height
    t = 1.5              # Line thickness for visibility

    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(THICK)
    c.setFillColor(HexColor("#D8D8E8"))

    direction = -1 if flipped else 1

    # Build path: bottom lip → bottom flange → web → top flange → top lip
    p = c.beginPath()
    # Bottom lip (45° down-left)
    p.moveTo(cx - direction * f, cy - h / 2 - lip * 0.707)
    # Bottom flange
    p.lineTo(cx - direction * f, cy - h / 2)
    p.lineTo(cx, cy - h / 2)
    # Web (vertical)
    p.lineTo(cx, cy + h / 2)
    # Top flange
    p.lineTo(cx + direction * f, cy + h / 2)
    # Top lip (45° up)
    p.lineTo(cx + direction * f, cy + h / 2 + lip * 0.707)
    c.drawPath(p, fill=0, stroke=1)

    # Dimension labels
    c.setFont("Helvetica", 4)
    c.setFillColor(CLR_DIM)
    c.drawCentredString(cx + 8, cy, f'12"')
    c.drawCentredString(cx + direction * f / 2, cy - h / 2 - 8, f'3.5"')
    c.drawCentredString(cx - direction * f - 5, cy - h / 2 - lip * 0.3 - 5,
                        f'3/4" LIP')


def _draw_c_profile(c, cx: float, cy: float, scale: float = 1.5):
    """Draw C-purlin cross-section (variable width, default 12"x3.5")."""
    h = 12 * scale
    f = 3.5 * scale
    lip = 0.75 * scale

    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(THICK)

    p = c.beginPath()
    # Top lip
    p.moveTo(cx - f, cy + h / 2 + lip * 0.707)
    p.lineTo(cx - f, cy + h / 2)
    # Top flange
    p.lineTo(cx, cy + h / 2)
    # Web
    p.lineTo(cx, cy - h / 2)
    # Bottom flange
    p.lineTo(cx - f, cy - h / 2)
    # Bottom lip
    p.lineTo(cx - f, cy - h / 2 - lip * 0.707)
    c.drawPath(p, fill=0, stroke=1)


# ═══════════════════════════════════════════════════════════════════════════════
# PURLIN LENGTH VIEW
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_purlin_length_view(c, group: Dict, ox: float, oy: float,
                             view_w: float, view_h: float):
    """
    Horizontal view of purlin showing total length, rafter positions,
    overhang zones, end extension, and splice location.
    """
    length_in = group["length_in"]

    margin = 35
    avail_w = view_w - 2 * margin
    scale = avail_w / length_in if length_in > 0 else 1.0

    # Purlin bar
    bar_h = 10
    bar_x = ox + margin
    bar_y = oy + view_h / 2
    bar_w = length_in * scale

    # Draw purlin body
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(THICK)
    c.setFillColor(HexColor("#D8D8E8"))
    c.rect(bar_x, bar_y - bar_h / 2, bar_w, bar_h, fill=1)

    # ── Rafter position markers ──
    # For First purlin: end rafter at 4" from left, internal rafter at 4" + bay_size
    # For Middle: rafters at overhang and overhang + bay_size
    # For Last: mirror of first

    end_ext_in = group["end_extension_in"]
    overhang_in = group["overhang_ft"] * 12
    bay_in = group["bay_span_ft"] * 12

    rafter_positions = []
    if group["is_first"]:
        rafter_positions.append({"pos_in": end_ext_in, "label": "END RAFTER"})
        rafter_positions.append({"pos_in": end_ext_in + bay_in, "label": "INT. RAFTER"})
    elif group["is_last"]:
        rafter_positions.append({"pos_in": overhang_in, "label": "INT. RAFTER"})
        rafter_positions.append({"pos_in": overhang_in + bay_in, "label": "END RAFTER"})
    else:
        # Middle
        rafter_positions.append({"pos_in": overhang_in, "label": "RAFTER"})
        rafter_positions.append({"pos_in": overhang_in + bay_in, "label": "RAFTER"})

    # Draw rafter position lines
    for rp in rafter_positions:
        rx = bar_x + rp["pos_in"] * scale
        c.setStrokeColor(HexColor("#666666"))
        c.setLineWidth(MEDIUM)
        c.setDash([4, 2])
        c.line(rx, bar_y - bar_h - 15, rx, bar_y + bar_h + 10)
        c.setDash([])
        c.setFont("Helvetica", 4)
        c.setFillColor(CLR_DIM)
        c.drawCentredString(rx, bar_y + bar_h + 12, rp["label"])

    # ── End extension callout ──
    if end_ext_in > 0:
        ext_x = bar_x + end_ext_in * scale
        if end_ext_in * scale > 5:
            draw_dimension_h(c, bar_x, ext_x, bar_y - bar_h - 5, -10,
                             f'{end_ext_in:.0f}"', font_size=5)

    # ── Overhang zone callout ──
    if overhang_in > 0 and not group["is_first"]:
        oh_x = bar_x + overhang_in * scale
        # Left overhang
        c.setStrokeColor(HexColor("#00AA44"))
        c.setLineWidth(THIN)
        c.setFillColor(HexColor("#EEFFEE"))
        c.rect(bar_x, bar_y - bar_h / 2 - 1, overhang_in * scale, bar_h + 2,
               fill=1)
        c.setFillColor(black)

    if overhang_in > 0 and not group["is_last"]:
        # Right overhang
        oh_start = bar_x + (length_in - overhang_in) * scale
        c.setStrokeColor(HexColor("#00AA44"))
        c.setFillColor(HexColor("#EEFFEE"))
        c.rect(oh_start, bar_y - bar_h / 2 - 1, overhang_in * scale, bar_h + 2,
               fill=1)
        c.setFillColor(black)

    # Redraw purlin outline on top
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(THICK)
    c.rect(bar_x, bar_y - bar_h / 2, bar_w, bar_h)

    # ── Splice location with hole callouts ──
    if group["needs_splice"] and group["splice"]:
        sp = group["splice"]
        sp_x = bar_x + sp["position_in"] * scale
        overlap_px = sp["overlap_in"] * scale

        # Splice overlap zone highlight
        c.setStrokeColor(CLR_SECTION_CUT)
        c.setLineWidth(THIN)
        c.setFillColor(HexColor("#FF6B3520"))
        c.rect(sp_x - overlap_px / 2, bar_y - bar_h / 2 - 1,
               overlap_px, bar_h + 2, fill=1)

        # Center splice line
        c.setStrokeColor(CLR_SECTION_CUT)
        c.setLineWidth(MEDIUM)
        c.line(sp_x, bar_y - bar_h - 20, sp_x, bar_y + bar_h + 5)

        # Splice hole circles (8 tek screws: 4 per side of web)
        hole_r = max(1.0, 1.5 * scale)
        screw_spacing = bar_h / 5
        for si in range(1, 5):
            sy = bar_y - bar_h / 2 + si * screw_spacing
            c.setStrokeColor(CLR_SECTION_CUT)
            c.setFillColor(white)
            c.circle(sp_x - 2, sy, hole_r, fill=1)
            c.circle(sp_x + 2, sy, hole_r, fill=1)

        c.setFont("Helvetica-Bold", 5)
        c.setFillColor(CLR_SECTION_CUT)
        c.drawCentredString(sp_x, bar_y - bar_h - 23,
                            f'SPLICE @ {_fmt_ft_in(sp["position_in"])}')
        c.setFont("Helvetica", 4)
        c.drawCentredString(sp_x, bar_y + bar_h + 18,
                            f'{sp["tek_screws"]}x #10 TEK + {sp["overlap_in"]}" OVERLAP')

    # ── Facing direction indicator ──
    if group["purlin_type"] == "z":
        facing_y = bar_y + bar_h + 30
        c.setStrokeColor(CLR_DIM)
        c.setLineWidth(THIN)
        c.setFont("Helvetica", 4)
        c.setFillColor(CLR_DIM)
        if group["is_first"]:
            # First purlin: top flange RIGHT
            arrow_x = bar_x + bar_w * 0.5
            c.line(arrow_x - 15, facing_y, arrow_x + 15, facing_y)
            c.line(arrow_x + 10, facing_y - 2, arrow_x + 15, facing_y)
            c.line(arrow_x + 10, facing_y + 2, arrow_x + 15, facing_y)
            c.drawCentredString(arrow_x, facing_y - 5,
                                'FACING: TOP FLANGE →')
        elif group["is_last"]:
            # Last purlin: top flange LEFT (mirror)
            arrow_x = bar_x + bar_w * 0.5
            c.line(arrow_x + 15, facing_y, arrow_x - 15, facing_y)
            c.line(arrow_x - 10, facing_y - 2, arrow_x - 15, facing_y)
            c.line(arrow_x - 10, facing_y + 2, arrow_x - 15, facing_y)
            c.drawCentredString(arrow_x, facing_y - 5,
                                'FACING: TOP FLANGE ← (MIRROR)')
        else:
            # Middle: alternating
            c.drawCentredString(bar_x + bar_w * 0.5, facing_y - 5,
                                'FACING: ALTERNATING (INTERIOR)')

    # ── Total length dimension ──
    draw_dimension_h(c, bar_x, bar_x + bar_w,
                     bar_y - bar_h - 30 - (10 if group["needs_splice"] else 0),
                     10,
                     f'TOTAL: {_fmt_ft_in(length_in)}', font_size=6.5)

    # ── Bay span dimension ──
    if group["is_first"]:
        bay_start = bar_x + end_ext_in * scale
        bay_end = bar_x + (end_ext_in + bay_in) * scale
    elif group["is_last"]:
        bay_start = bar_x + overhang_in * scale
        bay_end = bar_x + (overhang_in + bay_in) * scale
    else:
        bay_start = bar_x + overhang_in * scale
        bay_end = bar_x + (overhang_in + bay_in) * scale

    draw_dimension_h(c, bay_start, bay_end, bar_y + bar_h + 20, 10,
                     f'BAY: {_fmt_ft_in(bay_in)}', font_size=5.5)

    # ── Group label ──
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(black)
    c.drawString(bar_x, bar_y + bar_h + 40,
                 f'{group["group_id"]} — {group["label"]}')

    # Material
    prof = group["profile"]
    c.setFont("Helvetica", 5.5)
    c.setFillColor(CLR_DIM)
    type_label = "Z" if group["purlin_type"] == "z" else "C"
    c.drawCentredString(bar_x + bar_w / 2, bar_y + 2,
                        f'{type_label}-{prof["height"]}"x{prof["flange"]}" '
                        f'{prof["gauge"]} {prof["material"]}')


# ═══════════════════════════════════════════════════════════════════════════════
# BOM TABLE (Purlin)
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_purlin_bom(c, groups: List[Dict], ox: float, oy: float,
                     w: float, h: float):
    """BOM table listing all purlin groups."""
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(THIN)

    headers = ["GROUP", "QTY", "LENGTH", "TYPE", "SPLICE"]
    col_widths = [w * 0.12, w * 0.10, w * 0.30, w * 0.25, w * 0.23]

    row_h = 9
    n_rows = len(groups) + 1
    table_h = n_rows * row_h

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

    # Column lines
    x_pos = ox
    for cw_val in col_widths[:-1]:
        x_pos += cw_val
        c.setStrokeColor(CLR_GRID)
        c.setLineWidth(HAIR)
        c.line(x_pos, oy + h - table_h, x_pos, oy + h)

    # Data
    c.setFillColor(black)
    c.setFont("Helvetica", 4.5)
    for r_idx, g in enumerate(groups):
        ry_pos = hy - (r_idx + 1) * row_h
        if r_idx % 2 == 1:
            c.setFillColor(HexColor("#F5F5F5"))
            c.rect(ox, ry_pos, w, row_h, fill=1)
            c.setFillColor(black)
        c.setStrokeColor(CLR_GRID)
        c.setLineWidth(HAIR)
        c.line(ox, ry_pos, ox + w, ry_pos)

        row = [
            g["group_id"],
            str(g["qty_per_building"]),
            _fmt_ft_in(g["length_in"]),
            f'{"Z" if g["purlin_type"] == "z" else "C"}-12"x3.5" 12GA',
            "YES" if g["needs_splice"] else "NO",
        ]
        x_pos = ox
        for i, cell in enumerate(row):
            c.drawCentredString(x_pos + col_widths[i] / 2, ry_pos + 3, cell)
            x_pos += col_widths[i]

    c.setFont("Helvetica-Bold", 5.5)
    c.setFillColor(black)
    c.drawCentredString(ox + w / 2, oy + h - table_h - 8,
                        "PURLIN GROUP SUMMARY")


# ═══════════════════════════════════════════════════════════════════════════════
# TITLE BLOCK (Purlin)
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_purlin_title_block(c, cfg: ShopDrawingConfig,
                             sheet_num: int = 1, total_sheets: int = 1,
                             revision: str = "-"):
    """Title block for purlin drawings."""
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
    type_label = "Z-PURLINS" if cfg.purlin_type == "z" else "C-PURLINS"
    c.drawCentredString(tb_x + tb_w / 2, y, f'{type_label} — GROUPS')


# ═══════════════════════════════════════════════════════════════════════════════
# ENDCAP CALLOUT
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_endcap_note(c, ox: float, oy: float, w: float, h: float):
    """Endcap U-channel reference note."""
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(THIN)
    c.rect(ox, oy, w, h)

    c.setFont("Helvetica-Bold", 5.5)
    c.setFillColor(black)
    y = oy + h - 9
    c.drawString(ox + 3, y, "ENDCAP NOTE:")

    ec = PURLIN_DEFAULTS["endcap"]
    c.setFont("Helvetica", 4.5)
    y -= 8
    c.drawString(ox + 3, y,
                 f'U-Channel: {ec["inside_dim"]}" inside x '
                 f'{ec["leg_height"]}" legs, {ec["gauge"]} {ec["material"]}')
    y -= 7
    c.drawString(ox + 3, y,
                 f'{ec["tek_screws_per_purlin"]} TEK screws per purlin '
                 f'(2 top + 2 bottom)')
    y -= 7
    c.drawString(ox + 3, y,
                 f'Max length: {ec["max_length_ft_in"]} | '
                 f'Machine: {ec["machine"]}')
    y -= 7
    c.drawString(ox + 3, y,
                 f'Qty: {ec["qty_per_building"]} per building end | '
                 f'Ship: {ec["shipping"]}')


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

def generate_purlin_drawing(
    cfg: ShopDrawingConfig,
    output_path: Optional[str] = None,
    revision: str = "-",
) -> bytes:
    """
    Generate a purlin group shop drawing PDF.
    Shows all purlin groups (First/Middle/Last) on one page.
    """
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=landscape(letter))
    c.setTitle("Purlin Groups Shop Drawing")

    groups = calc_purlin_groups(cfg)

    _draw_border(c)

    draw_area_w = PAGE_W - 2 * MARGIN
    draw_area_h = PAGE_H - 2 * MARGIN
    bar_h = 1.5 * inch
    views_h = draw_area_h - bar_h

    # Split views area: left (profile + length views) | right (BOM + endcap)
    left_w = draw_area_w * 0.72
    right_w = draw_area_w * 0.28

    # ── Left side: purlin group length views ──
    n_groups = len(groups)
    group_h = views_h / max(n_groups, 1)

    for i, group in enumerate(groups):
        gy = MARGIN + bar_h + views_h - (i + 1) * group_h
        _draw_purlin_length_view(c, group, MARGIN, gy, left_w, group_h)

        # Separator
        if i < n_groups - 1:
            c.setStrokeColor(CLR_GRID)
            c.setLineWidth(HAIR)
            c.setDash([4, 4])
            c.line(MARGIN, gy, MARGIN + left_w, gy)
            c.setDash([])

    # ── Right side: profile + endcap + details ──
    right_ox = MARGIN + left_w
    profile_h = views_h * 0.45
    endcap_h = views_h * 0.25
    detail_h = views_h * 0.3

    # Z-purlin profile drawing
    profile_cy = MARGIN + bar_h + views_h - profile_h / 2
    if cfg.purlin_type == "z":
        _draw_z_profile(c, right_ox + right_w / 2, profile_cy, scale=2.5)
        c.setFont("Helvetica-Bold", 6)
        c.setFillColor(black)
        c.drawCentredString(right_ox + right_w / 2,
                            profile_cy - 30,
                            "Z-PURLIN PROFILE")
        c.setFont("Helvetica", 5)
        c.setFillColor(CLR_DIM)
        prof = PURLIN_DEFAULTS["profile"]
        c.drawCentredString(right_ox + right_w / 2,
                            profile_cy - 38,
                            f'{prof["height"]}"x{prof["flange"]}" '
                            f'{prof["gauge"]} {prof["material"]}')
        c.drawCentredString(right_ox + right_w / 2,
                            profile_cy - 46,
                            f'Coil: {prof["coil_width"]}" | Machine: {prof["machine"]}')
    else:
        _draw_c_profile(c, right_ox + right_w / 2, profile_cy, scale=2.5)
        c.setFont("Helvetica-Bold", 6)
        c.setFillColor(black)
        c.drawCentredString(right_ox + right_w / 2,
                            profile_cy - 30,
                            "C-PURLIN PROFILE")

    # Endcap note
    _draw_endcap_note(c, right_ox, MARGIN + bar_h + detail_h,
                      right_w, endcap_h)

    # Facing rules note
    foy = MARGIN + bar_h
    c.setStrokeColor(CLR_OBJECT)
    c.setLineWidth(THIN)
    c.rect(right_ox, foy, right_w, detail_h)
    c.setFont("Helvetica-Bold", 5.5)
    c.setFillColor(black)
    y = foy + detail_h - 9
    c.drawString(right_ox + 3, y, "FACING RULES:")
    c.setFont("Helvetica", 4.5)
    y -= 8
    facing = PURLIN_DEFAULTS["facing"]
    c.drawString(right_ox + 3, y,
                 f'Eave: {facing["eave_purlins"].replace("_", " ")}')
    y -= 7
    c.drawString(right_ox + 3, y,
                 f'Interior: {facing["interior_purlins"].replace("_", " ")}')
    y -= 7
    c.drawString(right_ox + 3, y,
                 f'Odd #: {facing["odd_number_rule"].replace("_", " ")}')
    y -= 10
    c.setFont("Helvetica-Bold", 5)
    c.drawString(right_ox + 3, y, "SHIP MARKS:")
    y -= 7
    c.setFont("Helvetica", 4.5)
    c.drawString(right_ox + 3, y,
                 f'Prefix: {PURLIN_DEFAULTS["mark_prefix"]}')
    y -= 7
    c.drawString(right_ox + 3, y,
                 "1 sticker per group per building")

    # ── Vertical divider ──
    c.setStrokeColor(CLR_GRID)
    c.setLineWidth(HAIR)
    c.setDash([4, 4])
    c.line(right_ox, MARGIN + bar_h, right_ox, MARGIN + bar_h + views_h)
    c.setDash([])

    # ── Bottom bar ──
    notes_w = draw_area_w * 0.28
    _draw_standard_notes(c, MARGIN, MARGIN, notes_w, bar_h)

    abbr_w = draw_area_w * 0.12
    _draw_abbreviations(c, MARGIN + notes_w, MARGIN, abbr_w, bar_h)

    bom_w = draw_area_w * 0.28
    _draw_purlin_bom(c, groups, MARGIN + notes_w + abbr_w, MARGIN, bom_w, bar_h)

    _draw_purlin_title_block(c, cfg, revision=revision)

    c.save()
    pdf_bytes = buf.getvalue()

    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)

    return pdf_bytes
