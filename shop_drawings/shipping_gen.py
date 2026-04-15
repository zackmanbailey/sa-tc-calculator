"""
Shipping Manifest PDF Generator
Produces a loading order manifest following the fixed shipping sequence:
  1. Columns
  2. Rafters
  3. Purlins
  4. Sag Rods / Hurricane Straps
  5. Decking / Roofing
  6. Trim

Rule: If a part is done out of order but fills remaining truck weight, ship it.
This manifest provides the ideal loading order and weight breakdown.
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
    SHIPPING_ORDER, PANEL_STACK_LIMITS,
    ShopDrawingConfig, calc_rafter_length, calc_wall_panel_length_in,
)
from shop_drawings.column_gen import (
    _fmt_ft_in, _draw_border,
    CLR_OBJECT, CLR_DIM, CLR_GRID, CLR_TITLE_BG, CLR_TITLE_TEXT,
    PAGE_W, PAGE_H, MARGIN,
    THICK, MEDIUM, THIN, HAIR,
)
from shop_drawings.cutlist_gen import _draw_cutlist_title_block


# ═══════════════════════════════════════════════════════════════════════════════
# MANIFEST CALCULATION
# ═══════════════════════════════════════════════════════════════════════════════

def _calc_manifest(cfg: ShopDrawingConfig) -> List[Dict]:
    """
    Calculate shipping manifest line items in the standard shipping order.
    Returns list of dicts with: category, items (list of pieces), total_weight.
    """
    # Force all config values to correct numeric types
    cfg.ensure_numeric()

    manifest = []
    n_frames = int(cfg.n_frames)
    n_struct_cols = n_frames if cfg.frame_type == "tee" else n_frames * 2

    # Coil weights
    lbs_lft_cee = 10.83
    lbs_lft_purlin = 7.43
    lbs_lft_angle = 0.8656
    lbs_lft_strap = 0.706
    lbs_lft_panel = 2.81

    slope_deg = float(cfg.roof_pitch_deg)
    tan_slope = math.tan(math.radians(slope_deg))
    dist = float(cfg.building_width_ft) / (2 if cfg.frame_type == "tee" else 3)

    # ── 1. Columns ──
    col_len_ft = (cfg.clear_height_ft + dist * tan_slope
                  + cfg.embedment_ft + cfg.column_buffer_ft)
    col_wt_ea = col_len_ft * 2 * lbs_lft_cee
    # Add cap plates (~50 lbs ea), gussets (~20 lbs set), rebar
    col_wt_ea += 70  # Approximate hardware per column
    col_total = col_wt_ea * n_struct_cols

    manifest.append({
        "category": "Columns",
        "order": 1,
        "items": [{
            "description": f"Box Columns ({n_struct_cols} pcs)",
            "mark": "C1-C{n}".format(n=n_struct_cols),
            "qty": n_struct_cols,
            "unit_wt": col_wt_ea,
            "total_wt": col_total,
            "notes": f'{_fmt_ft_in(col_len_ft * 12)} each, CEE 14x4x10GA',
        }],
        "total_weight": col_total,
    })

    # ── 2. Rafters ──
    use_z = cfg.raft_purlin_type == "z"
    raft_len = calc_rafter_length(cfg.building_width_ft,
                                  cfg.raft_roofing_overhang_ft, use_z)
    raft_wt_ea = raft_len * 2 * lbs_lft_cee
    raft_wt_ea += 100  # Clips, connection plates, rebar estimate
    raft_total = raft_wt_ea * n_frames

    manifest.append({
        "category": "Rafters",
        "order": 2,
        "items": [{
            "description": f"Box Rafters ({n_frames} pcs)",
            "mark": f"B1-B{n_frames}",
            "qty": n_frames,
            "unit_wt": raft_wt_ea,
            "total_wt": raft_total,
            "notes": f'{_fmt_ft_in(raft_len * 12)} each + clips attached',
        }],
        "total_weight": raft_total,
    })

    # ── 3. Purlins ──
    n_purlin_lines = math.floor(cfg.building_width_ft / cfg.purlin_spacing_ft) + 1
    purlin_total_lft = n_purlin_lines * cfg.building_length_ft
    purlin_wt = purlin_total_lft * lbs_lft_purlin

    # Endcaps
    endcap_wt = cfg.building_width_ft * 2 * lbs_lft_purlin * 0.8  # Approximate

    purlin_items = [{
        "description": f"Z-Purlins ({n_purlin_lines} lines x {cfg.building_length_ft:.0f}')",
        "mark": "PG-A/B/C",
        "qty": n_purlin_lines,
        "unit_wt": cfg.building_length_ft * lbs_lft_purlin,
        "total_wt": purlin_wt,
        "notes": f'{cfg.purlin_spacing_ft}\' OC, 12"x3.5" 12GA G90',
    }, {
        "description": "Endcap U-Channels (2 pcs)",
        "mark": "EC",
        "qty": 2,
        "unit_wt": endcap_wt / 2,
        "total_wt": endcap_wt,
        "notes": "12\" inside x 4\" legs, nested alternating",
    }]

    manifest.append({
        "category": "Purlins",
        "order": 3,
        "items": purlin_items,
        "total_weight": purlin_wt + endcap_wt,
    })

    # ── 4. Sag Rods / Hurricane Straps ──
    n_sag_pieces = n_frames * 4
    sag_avg_len = cfg.building_width_ft / 2  # Approximate average piece
    sag_wt = n_sag_pieces * sag_avg_len * lbs_lft_angle

    n_straps = n_frames * 4
    strap_wt = n_straps * 28 / 12 * lbs_lft_strap

    manifest.append({
        "category": "Sag Rods / Hurricane Straps",
        "order": 4,
        "items": [{
            "description": f"Sag Rods ({n_sag_pieces} pcs)",
            "mark": "SR",
            "qty": n_sag_pieces,
            "unit_wt": sag_avg_len * lbs_lft_angle,
            "total_wt": sag_wt,
            "notes": '2"x2" angle, 16GA G90',
        }, {
            "description": f"Hurricane Straps ({n_straps} pcs)",
            "mark": "HS",
            "qty": n_straps,
            "unit_wt": 28 / 12 * lbs_lft_strap,
            "total_wt": strap_wt,
            "notes": '1.5"x28" 10GA G90',
        }],
        "total_weight": sag_wt + strap_wt,
    })

    # ── 5. Decking / Roofing ──
    coverage_ft = 35.79 / 12
    n_runs = math.ceil(cfg.building_length_ft / coverage_ft)
    panel_total_ft = n_runs * cfg.building_width_ft  # Approximate
    panel_wt = panel_total_ft * lbs_lft_panel

    # Wall panels
    wall_wt = 0
    if cfg.has_back_wall:
        wall_panel_in = calc_wall_panel_length_in(
            cfg.clear_height_ft, cfg.wall_panel_ground_clearance_in,
            cfg.wall_girt_type == "z")
        n_wall_panels = math.ceil(cfg.building_length_ft / coverage_ft)
        wall_wt += n_wall_panels * (wall_panel_in / 12) * lbs_lft_panel
    if cfg.has_side_walls:
        wall_panel_in = calc_wall_panel_length_in(
            cfg.clear_height_ft, cfg.wall_panel_ground_clearance_in,
            cfg.wall_girt_type == "z")
        n_wall_panels = math.ceil(cfg.building_length_ft / coverage_ft) * 2
        wall_wt += n_wall_panels * (wall_panel_in / 12) * lbs_lft_panel

    deck_items = [{
        "description": f"Roof Panels ({n_runs * 2} pcs, 2-piece split)",
        "mark": "RF",
        "qty": n_runs * 2,
        "unit_wt": (cfg.building_width_ft / 2) * lbs_lft_panel,
        "total_wt": panel_wt,
        "notes": "48\" 29GA G50 Spartan Rib",
    }]
    if wall_wt > 0:
        deck_items.append({
            "description": "Wall Panels",
            "mark": "WP",
            "qty": 0,
            "unit_wt": 0,
            "total_wt": wall_wt,
            "notes": "Spartan Rib, vertical orientation",
        })

    manifest.append({
        "category": "Decking / Roofing",
        "order": 5,
        "items": deck_items,
        "total_weight": panel_wt + wall_wt,
    })

    # ── 6. Trim ──
    manifest.append({
        "category": "Trim",
        "order": 6,
        "items": [{
            "description": "J-Channel Trim (if applicable)",
            "mark": "TR",
            "qty": 0,
            "unit_wt": 0,
            "total_wt": 0,
            "notes": "Purchased from Home Depot, ship separately if needed",
        }],
        "total_weight": 0,
    })

    return manifest


# ═══════════════════════════════════════════════════════════════════════════════
# MANIFEST PDF RENDERER
# ═══════════════════════════════════════════════════════════════════════════════

def generate_shipping_manifest(
    cfg: ShopDrawingConfig,
    output_path: Optional[str] = None,
    revision: str = "-",
) -> bytes:
    """Generate shipping manifest PDF."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=landscape(letter))
    c.setTitle(f"Shipping Manifest — {cfg.job_code}")

    manifest = _calc_manifest(cfg)
    grand_total = sum(m["total_weight"] for m in manifest)

    _draw_border(c)

    draw_area_w = PAGE_W - 2 * MARGIN
    draw_area_h = PAGE_H - 2 * MARGIN
    bar_h = 1.5 * inch
    content_h = draw_area_h - bar_h

    # ── Header ──
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(black)
    c.drawCentredString(PAGE_W / 2, PAGE_H - MARGIN - 20,
                        "SHIPPING MANIFEST — LOADING ORDER")

    c.setFont("Helvetica", 8)
    c.setFillColor(CLR_DIM)
    c.drawCentredString(PAGE_W / 2, PAGE_H - MARGIN - 32,
                        f'{cfg.job_code} | {cfg.project_name} | '
                        f'{cfg.customer_name}')

    # ── Manifest table ──
    table_ox = MARGIN + 10
    table_oy = MARGIN + bar_h + 10
    table_w = draw_area_w - 20
    table_top = PAGE_H - MARGIN - 42

    headers = ["#", "CATEGORY", "DESCRIPTION", "QTY", "UNIT WT (LBS)",
               "TOTAL WT (LBS)", "NOTES"]
    col_widths = [table_w * 0.04, table_w * 0.12, table_w * 0.22,
                  table_w * 0.06, table_w * 0.10, table_w * 0.10,
                  table_w * 0.36]

    row_h = 12
    y = table_top

    # Header row
    c.setFillColor(HexColor("#2A2A4A"))
    c.rect(table_ox, y - row_h, table_w, row_h, fill=1)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 5.5)
    x = table_ox
    for i, hdr in enumerate(headers):
        c.drawCentredString(x + col_widths[i] / 2, y - row_h + 3.5, hdr)
        x += col_widths[i]

    y -= row_h
    running_weight = 0

    # Data rows
    for cat in manifest:
        # Category separator
        c.setFillColor(HexColor("#E8E8F0"))
        c.rect(table_ox, y - row_h, table_w, row_h, fill=1)
        c.setFillColor(black)
        c.setFont("Helvetica-Bold", 6)
        c.drawString(table_ox + col_widths[0] + 5, y - row_h + 3.5,
                     f'{cat["order"]}. {cat["category"].upper()}')
        c.setFont("Helvetica-Bold", 5.5)
        c.drawRightString(table_ox + sum(col_widths[:6]), y - row_h + 3.5,
                          f'{cat["total_weight"]:,.0f}')
        y -= row_h

        for item in cat["items"]:
            if y - row_h < table_oy:
                break  # Would overflow

            c.setStrokeColor(CLR_GRID)
            c.setLineWidth(HAIR)
            c.line(table_ox, y - row_h, table_ox + table_w, y - row_h)

            c.setFillColor(black)
            c.setFont("Helvetica", 5)
            row_data = [
                str(cat["order"]),
                item.get("mark", ""),
                item["description"],
                str(item["qty"]) if item["qty"] else "",
                f'{item["unit_wt"]:,.0f}' if item["unit_wt"] else "",
                f'{item["total_wt"]:,.0f}' if item["total_wt"] else "",
                item.get("notes", ""),
            ]

            x = table_ox
            for i, cell in enumerate(row_data):
                max_chars = int(col_widths[i] / 3.2)
                display = cell[:max_chars] if len(cell) > max_chars else cell
                c.drawCentredString(x + col_widths[i] / 2, y - row_h + 3.5,
                                    display)
                x += col_widths[i]
            y -= row_h

            running_weight += item.get("total_wt", 0)

    # ── Grand total row ──
    c.setFillColor(HexColor("#1A1A2E"))
    c.rect(table_ox, y - row_h * 1.3, table_w, row_h * 1.3, fill=1)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(table_ox + 10, y - row_h + 1, "GRAND TOTAL:")
    c.drawRightString(table_ox + sum(col_widths[:6]), y - row_h + 1,
                      f'{grand_total:,.0f} LBS')
    c.setFont("Helvetica", 6)
    c.drawRightString(table_ox + table_w - 5, y - row_h + 1,
                      f'({grand_total / 2000:,.1f} TONS)')

    # ── Truck note ──
    c.setFont("Helvetica", 6)
    c.setFillColor(CLR_DIM)
    c.drawString(table_ox, y - row_h * 1.3 - 12,
                 "NOTE: If a part is complete out of sequence but fills remaining "
                 "truck weight capacity, it may be shipped early.")

    # ── Bottom bar ──
    _draw_cutlist_title_block(c, cfg, "SHIPPING MANIFEST", revision=revision)

    # Shipping order legend in bottom-left
    leg_x = MARGIN + 5
    leg_y = MARGIN + bar_h - 10
    c.setFont("Helvetica-Bold", 6)
    c.setFillColor(black)
    c.drawString(leg_x, leg_y, "STANDARD LOADING ORDER:")
    c.setFont("Helvetica", 5.5)
    for i, item in enumerate(SHIPPING_ORDER):
        leg_y -= 9
        c.drawString(leg_x, leg_y, f'{i + 1}. {item}')

    c.save()
    pdf_bytes = buf.getvalue()

    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)

    return pdf_bytes
