"""
TitanForge -- Work Order Fabrication Sticker Generator
======================================================
Generates three types of 6"x4" (landscape) fabrication stickers for
Zebra ZT411 thermal transfer printers (Industrial Wax/Resin ribbon).

Sticker types:
  1. ASSEMBLY STICKERS  -- one per fabricated assembly, shows full cut list / BOM
  2. MATERIAL MASTER     -- one per unique material spec across the entire job
  3. MATERIAL SUB        -- one per material spec per parent assembly type

ALL output is BLACK AND WHITE only (thermal transfer compatible).
Output format: PDF via ReportLab.
"""

import io
import math
import datetime
from typing import List, Dict, Optional

from reportlab.lib.units import inch
from reportlab.lib.colors import black, white
from reportlab.pdfgen.canvas import Canvas
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics import renderPDF

from shop_drawings.column_gen import _fmt_ft_in


# ---------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------

W = 6.0 * inch   # Sticker width  (landscape)
H = 4.0 * inch   # Sticker height (landscape)
M = 0.15 * inch   # Margin

FOOTER_TEXT = "Structures America | 14369 FM 1314, Conroe TX 77302 | TitanForge"

# Steel densities (lbs per cubic inch)
_STEEL_LBS_PER_CUIN = 0.2836

# Gauge -> thickness in inches
_GAUGE_THICKNESS = {
    10: 0.1345,
    12: 0.1046,
    14: 0.0747,
    16: 0.0598,
    18: 0.0478,
    20: 0.0359,
    22: 0.0299,
    24: 0.0239,
    26: 0.0179,
    29: 0.0141,
}

# Rebar weight per foot (lbs/ft)
_REBAR_WEIGHT_PER_FT = {
    "#3": 0.376, "#4": 0.668, "#5": 1.043, "#6": 1.502,
    "#7": 2.044, "#8": 2.670, "#9": 3.400, "#10": 4.303,
}

# Rebar standard stick length (feet)
_REBAR_MAX_STICK_FT = 20


# ---------------------------------------------------------------------------
# QR CODE HELPER
# ---------------------------------------------------------------------------

def _qr_drawing(data: str, size_pts: float) -> Drawing:
    """Generate a ReportLab QR code Drawing at the given point size."""
    qr = QrCodeWidget(data)
    bounds = qr.getBounds()
    qr_w = bounds[2] - bounds[0]
    qr_h = bounds[3] - bounds[1]
    scale = size_pts / max(qr_w, qr_h)
    d = Drawing(size_pts, size_pts)
    d.transform = (scale, 0, 0, scale, 0, 0)
    d.add(qr)
    return d


# ---------------------------------------------------------------------------
# GEOMETRY / MATH HELPERS
# ---------------------------------------------------------------------------

def _col_height_in(cfg: dict) -> float:
    """Total column height in inches = clear_height + embedment + buffer."""
    clear_ft = cfg.get("clear_height_ft", 16)
    embed_ft = cfg.get("embedment_ft", 4.333)
    buf_ft = cfg.get("column_buffer_ft", 0.5)
    return (clear_ft + embed_ft + buf_ft) * 12.0


def _rafter_length_in(cfg: dict) -> float:
    """Single rafter length in inches (half-span along slope)."""
    width_ft = cfg.get("building_width_ft", 50)
    pitch_deg = cfg.get("roof_pitch_deg", 1.19)
    half_span_ft = width_ft / 2.0
    slope_len_ft = half_span_ft / math.cos(math.radians(pitch_deg))
    return slope_len_ft * 12.0


def _n_purlin_lines(cfg: dict) -> int:
    """Number of purlin lines across a single rafter (including eave + ridge)."""
    width_ft = cfg.get("building_width_ft", 50)
    spacing_ft = cfg.get("purlin_spacing_ft", 5.0)
    half_span_ft = width_ft / 2.0
    return max(int(math.ceil(half_span_ft / spacing_ft)) + 1, 3)


def _bay_length_in(cfg: dict) -> float:
    """Bay length in inches (frame spacing)."""
    n_frames = cfg.get("n_frames", 5)
    length_ft = cfg.get("building_length_ft", 150)
    n_bays = max(n_frames - 1, 1)
    return (length_ft / n_bays) * 12.0


def _rebar_sticks(cfg: dict) -> int:
    """Number of rebar sticks per column (4 sticks, length = ceil((footing_depth+8)/max_stick)*sticks)."""
    footing_depth_ft = cfg.get("footing_depth_ft", 10)
    footing_depth_in = footing_depth_ft * 12.0
    total_length_in = footing_depth_in + 8.0  # 8 inches above footing
    total_length_ft = total_length_in / 12.0
    sticks_per_bar = max(1, math.ceil(total_length_ft / _REBAR_MAX_STICK_FT))
    return 4 * sticks_per_bar  # 4 bars per column


def _rebar_stick_length_in(cfg: dict) -> float:
    """Length of each rebar stick in inches."""
    footing_depth_ft = cfg.get("footing_depth_ft", 10)
    footing_depth_in = footing_depth_ft * 12.0
    total_length_in = footing_depth_in + 8.0
    total_length_ft = total_length_in / 12.0
    sticks_per_bar = max(1, math.ceil(total_length_ft / _REBAR_MAX_STICK_FT))
    return total_length_in / sticks_per_bar


def _sheet_weight(width_in: float, length_in: float, gauge: int) -> float:
    """Weight of a flat steel sheet/plate in lbs."""
    t = _GAUGE_THICKNESS.get(gauge, 0.1)
    return width_in * length_in * t * _STEEL_LBS_PER_CUIN


def _plate_weight(thickness_in: float, w_in: float, l_in: float) -> float:
    """Weight of a steel plate in lbs."""
    return w_in * l_in * thickness_in * _STEEL_LBS_PER_CUIN


def _c_section_weight_per_ft(web_in: float, flange_in: float, gauge: int) -> float:
    """Approximate weight per linear foot of a C-section (web + 2 flanges + 2 lips)."""
    t = _GAUGE_THICKNESS.get(gauge, 0.1)
    lip_in = 0.75
    perim_in = web_in + 2 * flange_in + 2 * lip_in
    area_sqin = perim_in * t
    return area_sqin * 12.0 * _STEEL_LBS_PER_CUIN


def _z_section_weight_per_ft(web_in: float, flange_in: float, gauge: int) -> float:
    """Approximate weight per linear foot of a Z-purlin."""
    t = _GAUGE_THICKNESS.get(gauge, 0.1)
    lip_in = 0.75
    perim_in = web_in + 2 * flange_in + 2 * lip_in
    area_sqin = perim_in * t
    return area_sqin * 12.0 * _STEEL_LBS_PER_CUIN


# ---------------------------------------------------------------------------
# COMPONENT TYPE DETECTION
# ---------------------------------------------------------------------------

def _parse_component_type(ship_mark: str) -> str:
    """Determine component type from ship mark prefix."""
    sm = ship_mark.upper().strip()
    if sm.startswith("C") and sm[1:].split("-")[0].isdigit():
        return "column"
    if sm.startswith("B") and sm[1:].split("-")[0].isdigit():
        return "rafter"
    if sm.startswith("PG"):
        return "purlin_group"
    if sm.startswith("SR"):
        return "sag_rod"
    if sm.startswith("HS"):
        return "strap"
    if sm.startswith("EC"):
        return "endcap"
    if sm.upper() == "ROOF":
        return "roofing"
    return "other"


# ============================================================================
# 1. ASSEMBLY CUT LIST
# ============================================================================

def get_assembly_cut_list(config_dict: dict, component_type: str,
                          ship_mark: str) -> list:
    """
    Return list of sub-part dicts for an assembly.

    Each dict: {spec, qty, unit, weight_lbs, length_in (optional)}
    """
    cfg = config_dict
    ctype = component_type.lower()
    parts: List[dict] = []

    # ── COLUMN ──────────────────────────────────────────────────────────
    if ctype == "column":
        col_h_in = _col_height_in(cfg)
        cee_wt_ft = _c_section_weight_per_ft(14, 4, 10)
        parts.append({
            "spec": 'C-Section 14"x4" 10GA',
            "qty": 2,
            "unit": "ea",
            "length_in": col_h_in,
            "weight_lbs": round(2 * cee_wt_ft * (col_h_in / 12.0), 1),
        })
        parts.append({
            "spec": 'Cap Plate PL 3/4"x26"x14"',
            "qty": 2,
            "unit": "ea",
            "length_in": None,
            "weight_lbs": round(2 * _plate_weight(0.75, 26, 14), 1),
        })
        parts.append({
            "spec": 'Gusset PL 3/8"x6"x6"',
            "qty": 4,
            "unit": "ea",
            "length_in": None,
            # Triangle gusset = half of 6x6 plate
            "weight_lbs": round(4 * _plate_weight(0.375, 6, 6) * 0.5, 1),
        })
        parts.append({
            "spec": 'A325 Bolt Assembly 3/4"',
            "qty": 4,
            "unit": "ea",
            "length_in": None,
            "weight_lbs": 0,  # purchased hardware
            "purchased": True,
        })
        # Rebar
        rebar_size = cfg.get("rebar_col_size", "#7")
        n_sticks = _rebar_sticks(cfg)
        stick_len_in = _rebar_stick_length_in(cfg)
        wt_per_ft = _REBAR_WEIGHT_PER_FT.get(rebar_size, 2.044)
        total_rebar_wt = n_sticks * (stick_len_in / 12.0) * wt_per_ft
        parts.append({
            "spec": f"{rebar_size} Rebar",
            "qty": n_sticks,
            "unit": "ea",
            "length_in": stick_len_in,
            "weight_lbs": round(total_rebar_wt, 1),
        })

    # ── RAFTER ──────────────────────────────────────────────────────────
    elif ctype == "rafter":
        raft_len_in = _rafter_length_in(cfg)
        cee_wt_ft = _c_section_weight_per_ft(14, 4, 10)
        needs_splice = raft_len_in > (53 * 12)

        parts.append({
            "spec": 'C-Section 14"x4" 10GA',
            "qty": 2,
            "unit": "ea",
            "length_in": raft_len_in,
            "weight_lbs": round(2 * cee_wt_ft * (raft_len_in / 12.0), 1),
        })
        straps_per_raft = cfg.get("straps_per_rafter", 4)
        strap_len = cfg.get("strap_length_in", 28)
        parts.append({
            "spec": f'Strap 1.5"x{strap_len}" 10GA',
            "qty": straps_per_raft,
            "unit": "ea",
            "length_in": float(strap_len),
            "weight_lbs": round(straps_per_raft * _sheet_weight(1.5, strap_len, 10), 1),
        })
        npl = _n_purlin_lines(cfg)
        n_interior = max(npl - 2, 0)
        if n_interior > 0:
            parts.append({
                "spec": 'P1 Interior Clip 6"x10" 10GA',
                "qty": n_interior,
                "unit": "ea",
                "length_in": None,
                "weight_lbs": round(n_interior * _sheet_weight(6, 10, 10), 1),
            })
        parts.append({
            "spec": 'P2 End Cap 9"x24" 10GA',
            "qty": 2,
            "unit": "ea",
            "length_in": None,
            "weight_lbs": round(2 * _sheet_weight(9, 24, 10), 1),
        })
        if needs_splice:
            parts.append({
                "spec": 'Splice Plate 14"x24" 10GA',
                "qty": 2,
                "unit": "ea",
                "length_in": None,
                "weight_lbs": round(2 * _sheet_weight(14, 24, 10), 1),
            })

    # ── PURLIN GROUP ────────────────────────────────────────────────────
    elif ctype == "purlin_group":
        purlin_type = cfg.get("purlin_type", "Z")
        bay_len_in = _bay_length_in(cfg)
        npl = _n_purlin_lines(cfg)
        gauge = 12
        if purlin_type.upper() == "Z":
            wt_ft = _z_section_weight_per_ft(12, 3.5, gauge)
            spec = 'Z-Purlin 12"x3.5" 12GA'
        else:
            wt_ft = _c_section_weight_per_ft(12, 3.5, gauge)
            spec = 'C-Purlin 12"x3.5" 12GA'
        parts.append({
            "spec": spec,
            "qty": npl,
            "unit": "ea",
            "length_in": bay_len_in,
            "weight_lbs": round(npl * wt_ft * (bay_len_in / 12.0), 1),
        })
        n_interior = max(npl - 2, 0)
        if n_interior > 0:
            parts.append({
                "spec": 'Interior Plate 6" 10GA',
                "qty": n_interior * 2,  # top & bottom per interior purlin
                "unit": "ea",
                "length_in": None,
                "weight_lbs": round(n_interior * 2 * _sheet_weight(6, 6, 10), 1),
            })
        parts.append({
            "spec": 'Eave Plate 9" 10GA',
            "qty": 2,
            "unit": "ea",
            "length_in": None,
            "weight_lbs": round(2 * _sheet_weight(9, 9, 10), 1),
        })

    # ── SAG ROD BUNDLE ──────────────────────────────────────────────────
    elif ctype == "sag_rod":
        npl = _n_purlin_lines(cfg)
        bay_len_in = _bay_length_in(cfg)
        # Sag rods run between purlins at mid-bay; one per purlin line
        parts.append({
            "spec": 'Angle 2"x2" 16GA',
            "qty": npl,
            "unit": "ea",
            "length_in": bay_len_in / 2.0,
            "weight_lbs": round(npl * _sheet_weight(4, bay_len_in / 2.0, 16), 1),
        })

    # ── STRAP BUNDLE ────────────────────────────────────────────────────
    elif ctype == "strap":
        strap_len = cfg.get("strap_length_in", 28)
        n_frames = cfg.get("n_frames", 5)
        straps_per_raft = cfg.get("straps_per_rafter", 4)
        total_straps = (n_frames - 1) * 2 * straps_per_raft  # 2 rafters per bay
        parts.append({
            "spec": f'Flat Strap 1.5"x{strap_len}" 10GA',
            "qty": total_straps,
            "unit": "ea",
            "length_in": float(strap_len),
            "weight_lbs": round(total_straps * _sheet_weight(1.5, strap_len, 10), 1),
        })

    # ── ENDCAP ──────────────────────────────────────────────────────────
    elif ctype == "endcap":
        width_ft = cfg.get("building_width_ft", 50)
        endcap_len_in = width_ft * 12.0
        wt_ft = _c_section_weight_per_ft(12, 4, 12)
        parts.append({
            "spec": 'U-Channel 12"x4" 12GA',
            "qty": 1,
            "unit": "ea",
            "length_in": endcap_len_in,
            "weight_lbs": round(wt_ft * (endcap_len_in / 12.0), 1),
        })

    # ── ROOFING ─────────────────────────────────────────────────────────
    elif ctype == "roofing":
        width_ft = cfg.get("building_width_ft", 50)
        length_ft = cfg.get("building_length_ft", 150)
        overhang_ft = cfg.get("roofing_overhang_ft", 0.5)
        pitch_deg = cfg.get("roof_pitch_deg", 1.19)
        half_span_ft = width_ft / 2.0
        slope_len_ft = half_span_ft / math.cos(math.radians(pitch_deg))
        panel_len_ft = slope_len_ft + overhang_ft
        panel_len_in = panel_len_ft * 12.0
        # Coverage width = 36" effective (48" panel, 12" overlap)
        coverage_in = 36.0
        total_cover_length_in = (length_ft + 2 * overhang_ft) * 12.0
        n_panels_per_side = math.ceil(total_cover_length_in / coverage_in)
        total_panels = n_panels_per_side * 2  # both sides
        # 29GA panel weight ~ 0.848 lbs/ft per ft of width (48" = 4ft)
        panel_wt_per_ft = 4.0 * 12.0 * _GAUGE_THICKNESS.get(29, 0.0141) * _STEEL_LBS_PER_CUIN
        parts.append({
            "spec": 'Spartan Rib 48" 29GA Panel',
            "qty": total_panels,
            "unit": "ea",
            "length_in": panel_len_in,
            "weight_lbs": round(total_panels * panel_wt_per_ft * panel_len_ft, 1),
        })

    return parts


# ============================================================================
# 2. MATERIAL GROUPING
# ============================================================================

def get_material_groups(config_dict: dict, wo_items: list) -> dict:
    """
    Group all materials across the entire job.

    Returns dict keyed by spec string:
        {
            spec_key: {
                "spec": str,
                "total_qty": int,
                "total_weight": float,
                "total_length_in": float or None,
                "unit_length_in": float or None,
                "destinations": {comp_type: qty, ...},
            }
        }
    """
    groups: Dict[str, dict] = {}

    for item in wo_items:
        ship_mark = item.get("ship_mark", "")
        comp_type = item.get("component_type", "") or _parse_component_type(ship_mark)
        cut_list = get_assembly_cut_list(config_dict, comp_type, ship_mark)

        for part in cut_list:
            spec = part["spec"]
            qty = part["qty"]
            wt = part.get("weight_lbs", 0)
            length_in = part.get("length_in")

            if spec not in groups:
                groups[spec] = {
                    "spec": spec,
                    "total_qty": 0,
                    "total_weight": 0.0,
                    "total_length_in": 0.0 if length_in else None,
                    "unit_length_in": length_in,
                    "destinations": {},
                    "dest_lengths": {},   # {dest_label: length_in}
                    "dest_weights": {},   # {dest_label: weight_lbs}
                }

            g = groups[spec]
            g["total_qty"] += qty
            g["total_weight"] += wt
            if length_in is not None and g["total_length_in"] is not None:
                g["total_length_in"] += qty * length_in

            dest_label = comp_type.replace("_", " ").title()
            g["destinations"][dest_label] = g["destinations"].get(dest_label, 0) + qty
            # Track per-destination length and weight
            if length_in is not None:
                g["dest_lengths"][dest_label] = length_in
            g["dest_weights"][dest_label] = g["dest_weights"].get(dest_label, 0.0) + wt

    # Round weights & check if unit_length varies across destinations
    for g in groups.values():
        g["total_weight"] = round(g["total_weight"], 1)
        if g["total_length_in"] is not None:
            g["total_length_in"] = round(g["total_length_in"], 1)
        for dl in g["dest_weights"]:
            g["dest_weights"][dl] = round(g["dest_weights"][dl], 1)
        # If multiple different lengths exist, mark unit_length as "varies"
        unique_lens = set(g["dest_lengths"].values())
        if len(unique_lens) > 1:
            g["unit_length_in"] = None  # varies — show per-dest on master
            g["length_varies"] = True
        else:
            g["length_varies"] = False

    return groups


# ============================================================================
# COMMON DRAWING HELPERS
# ============================================================================

def _draw_header(c: Canvas, title: str, print_date: str):
    """Draw the standard header bar at top of sticker."""
    hdr_h = 0.35 * inch
    c.setStrokeColor(black)
    c.setLineWidth(1.5)
    c.setFillColor(black)
    c.rect(0, H - hdr_h, W, hdr_h, fill=1, stroke=0)

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(M, H - hdr_h + 0.12 * inch, "TITANFORGE")

    c.setFont("Helvetica", 7)
    c.drawString(M + 1.0 * inch, H - hdr_h + 0.13 * inch, title)

    c.setFont("Helvetica", 6.5)
    c.drawRightString(W - M, H - hdr_h + 0.13 * inch, f"Printed: {print_date}")

    # Accent line below header
    c.setStrokeColor(black)
    c.setLineWidth(2)
    c.line(0, H - hdr_h - 1, W, H - hdr_h - 1)

    return H - hdr_h - 3  # y just below accent line


def _draw_footer(c: Canvas):
    """Draw the standard footer bar at bottom of sticker."""
    foot_h = 0.22 * inch
    c.setStrokeColor(black)
    c.setLineWidth(1.5)
    c.line(0, foot_h, W, foot_h)
    c.setFillColor(black)
    c.setFont("Helvetica", 5)
    c.drawCentredString(W / 2, 0.07 * inch, FOOTER_TEXT)
    return foot_h


def _draw_qr(c: Canvas, data: str, x: float, y: float, size: float):
    """Draw a QR code at the given position. Returns True on success."""
    try:
        qr_d = _qr_drawing(data, size)
        renderPDF.draw(qr_d, c, x, y)
        return True
    except Exception:
        c.setStrokeColor(black)
        c.setLineWidth(0.5)
        c.rect(x, y, size, size, fill=0, stroke=1)
        c.setFont("Helvetica", 5)
        c.setFillColor(black)
        c.drawCentredString(x + size / 2, y + size / 2, "QR ERROR")
        return False


def _draw_divider(c: Canvas, y: float, label: str = ""):
    """Draw a horizontal divider with optional centered label."""
    c.setStrokeColor(black)
    c.setLineWidth(0.75)
    if label:
        lbl_w = len(label) * 4.0 + 16
        mid_x = W / 2.0
        c.line(M, y, mid_x - lbl_w / 2, y)
        c.line(mid_x + lbl_w / 2, y, W - M, y)
        c.setFont("Helvetica-Bold", 6)
        c.setFillColor(black)
        c.drawCentredString(mid_x, y - 3, label)
    else:
        c.line(M, y, W - M, y)


def _draw_checkbox_grid(c: Canvas, x: float, y: float,
                        total: int, cols_per_group: int = 10,
                        box_size: float = 10, gap: float = 2,
                        group_gap: float = 8) -> float:
    """
    Draw a grid of empty checkboxes. Returns the y after last row.

    Boxes are drawn in groups of `cols_per_group`, with extra spacing
    between groups.
    """
    c.setStrokeColor(black)
    c.setLineWidth(0.5)

    usable_w = W - 2 * M
    # Calculate how many boxes fit per row (with group gaps)
    boxes_per_row = 0
    test_x = 0
    while True:
        next_w = box_size + gap
        # Add group gap after every cols_per_group boxes
        if boxes_per_row > 0 and boxes_per_row % cols_per_group == 0:
            next_w += group_gap
        if test_x + box_size > usable_w:
            break
        test_x += next_w
        boxes_per_row += 1
    boxes_per_row = max(boxes_per_row, 1)

    n_rows = math.ceil(total / boxes_per_row)
    row_h = box_size + gap

    cur_y = y
    drawn = 0
    for row in range(n_rows):
        cur_x = x
        for col in range(boxes_per_row):
            if drawn >= total:
                break
            # Group gap
            if col > 0 and col % cols_per_group == 0:
                cur_x += group_gap
            c.rect(cur_x, cur_y - box_size, box_size, box_size, fill=0, stroke=1)
            cur_x += box_size + gap
            drawn += 1
        cur_y -= row_h
        if drawn >= total:
            break

    return cur_y


def _format_weight(lbs: float) -> str:
    """Format weight with commas."""
    if lbs <= 0:
        return "N/A"
    return f"{lbs:,.0f} lbs" if lbs >= 1 else f"{lbs:.1f} lbs"


def _format_length_label(length_in: Optional[float]) -> str:
    """Format a length for display on a sticker line."""
    if length_in is None:
        return ""
    return _fmt_ft_in(length_in) + " ea"


# ============================================================================
# 3A. ASSEMBLY STICKER RENDERER
# ============================================================================

def _draw_assembly_sticker(c: Canvas, item: dict, wo_info: dict,
                           config_dict: dict,
                           app_base_url: str = "http://localhost:8888"):
    """Draw a single assembly sticker on the current page."""
    job_code = wo_info.get("job_code", "")
    wo_id = wo_info.get("work_order_id", "")
    ship_mark = item.get("ship_mark", "???")
    comp_type = item.get("component_type", "") or _parse_component_type(ship_mark)
    desc = item.get("description", "")
    machine = item.get("machine", "WELDING")
    # Derive a human-friendly drawing label from the interactive builder route
    _raw_ref = item.get("drawing_ref", "")
    if "/column" in _raw_ref:
        drawing_ref = "Interactive Column Dwg"
    elif "/rafter" in _raw_ref:
        drawing_ref = "Interactive Rafter Dwg"
    elif "/shop-drawings/" in _raw_ref:
        drawing_ref = "Project Drawings"
    else:
        drawing_ref = _raw_ref or f"{job_code}_{ship_mark}"
    print_date = datetime.date.today().strftime("%m/%d/%Y")

    qr_data = f"{app_base_url}/wo/{job_code}/{item.get('item_id', ship_mark)}"

    c.setPageSize((W, H))

    # Header
    y = _draw_header(c, "ASSEMBLY STICKER", print_date)
    foot_h = _draw_footer(c)

    # QR code + identity block
    qr_size = 0.85 * inch
    qr_x = M
    qr_y = y - qr_size - 0.06 * inch
    _draw_qr(c, qr_data, qr_x, qr_y, qr_size)

    text_x = M + qr_size + 0.12 * inch
    ty = y - 0.16 * inch

    # Ship mark (large)
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(text_x, ty, ship_mark)

    # Component type badge
    badge_text = comp_type.upper().replace("_", " ")
    badge_x = text_x + len(ship_mark) * 14 + 8
    c.setFont("Helvetica-Bold", 8)
    badge_w = c.stringWidth(badge_text, "Helvetica-Bold", 8) + 10
    c.setStrokeColor(black)
    c.setLineWidth(0.75)
    c.roundRect(badge_x, ty - 1, badge_w, 14, 3, fill=0, stroke=1)
    c.drawString(badge_x + 5, ty + 2, badge_text)

    ty -= 0.20 * inch
    c.setFont("Helvetica", 7)
    if desc:
        c.drawString(text_x, ty, desc[:55])
        ty -= 0.14 * inch

    # Job / WO / Drawing info
    c.setFont("Helvetica-Bold", 6.5)
    c.drawString(text_x, ty, f"JOB: {job_code}")
    mid_x = text_x + 1.6 * inch
    c.drawString(mid_x, ty, f"WO: {wo_id[:28]}")
    ty -= 0.13 * inch
    c.drawString(text_x, ty, f"Machine: {machine}")
    c.drawString(mid_x, ty, f"Drawing: {drawing_ref[:25]}")

    # Divider: CUT LIST / BOM
    div_y = qr_y - 0.06 * inch
    _draw_divider(c, div_y, "CUT LIST / BOM")

    # Cut list items
    cut_list = get_assembly_cut_list(config_dict, comp_type, ship_mark)
    line_y = div_y - 0.18 * inch
    line_h = 0.135 * inch
    min_y = foot_h + 0.28 * inch  # leave room for footer + accent

    c.setFillColor(black)
    for part in cut_list:
        if line_y < min_y:
            # Overflow indicator
            c.setFont("Helvetica", 5.5)
            c.drawString(M + 0.05 * inch, line_y, "... (see full BOM on shop drawing)")
            break

        spec = part["spec"]
        qty = part["qty"]
        purchased = part.get("purchased", False)
        length_in = part.get("length_in")
        wt = part.get("weight_lbs", 0)

        # Checkbox
        cb_x = M + 0.02 * inch
        cb_size = 8
        c.setStrokeColor(black)
        c.setLineWidth(0.5)
        c.rect(cb_x, line_y - 1, cb_size, cb_size, fill=0, stroke=1)

        # Qty x Spec
        c.setFont("Helvetica-Bold", 7)
        c.setFillColor(black)
        c.drawString(cb_x + cb_size + 4, line_y, f"{qty}x")

        c.setFont("Helvetica", 7)
        c.drawString(cb_x + cb_size + 24, line_y, spec)

        # Right side: length or weight or "purchased"
        if purchased:
            c.setFont("Helvetica-Oblique", 6.5)
            c.drawRightString(W - M, line_y, "purchased")
        elif length_in is not None:
            c.setFont("Helvetica", 6.5)
            c.drawRightString(W - M, line_y, _fmt_ft_in(length_in) + " ea")
        elif wt > 0:
            c.setFont("Helvetica", 6.5)
            c.drawRightString(W - M, line_y, _format_weight(wt))

        line_y -= line_h

    # Bottom accent line
    c.setStrokeColor(black)
    c.setLineWidth(2)
    c.line(0, foot_h + 0.01 * inch, W, foot_h + 0.01 * inch)


def generate_assembly_sticker_pdf(
    wo_dict: dict,
    items: Optional[List[dict]] = None,
    config_dict: Optional[dict] = None,
    app_base_url: str = "http://localhost:8888",
) -> bytes:
    """
    Generate PDF with one 6x4 assembly sticker per item, showing full cut list.

    Args:
        wo_dict: Work order dict (work_order_id, job_code, revision, items)
        items: Optional subset of items. If None, generates for all items.
        config_dict: ShopDrawingConfig as dict (building dimensions, etc.)
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
    cfg = config_dict or {}
    target_items = items or wo_dict.get("items", [])

    for item in target_items:
        _draw_assembly_sticker(c, item, wo_info, cfg, app_base_url)
        c.showPage()

    c.save()
    return buf.getvalue()


# ============================================================================
# 3B. MATERIAL MASTER STICKER RENDERER
# ============================================================================

def _draw_material_master_sticker(c: Canvas, mat_group: dict, job_code: str,
                                  app_base_url: str = "http://localhost:8888"):
    """Draw a single material master sticker on the current page."""
    spec = mat_group["spec"]
    total_qty = mat_group["total_qty"]
    total_weight = mat_group["total_weight"]
    unit_length_in = mat_group.get("unit_length_in")
    destinations = mat_group.get("destinations", {})
    print_date = datetime.date.today().strftime("%m/%d/%Y")

    qr_data = f"{app_base_url}/wo/{job_code}/material/{spec.replace(' ', '_')}"

    c.setPageSize((W, H))

    # Header
    y = _draw_header(c, "MATERIAL STICKER", print_date)
    foot_h = _draw_footer(c)

    # QR code + material info
    qr_size = 0.80 * inch
    qr_x = M
    qr_y = y - qr_size - 0.06 * inch
    _draw_qr(c, qr_data, qr_x, qr_y, qr_size)

    text_x = M + qr_size + 0.12 * inch
    ty = y - 0.16 * inch

    # Material spec (large)
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 11)
    # Truncate if too long
    max_chars = 42
    spec_display = spec if len(spec) <= max_chars else spec[:max_chars - 2] + ".."
    c.drawString(text_x, ty, spec_display)

    ty -= 0.18 * inch
    c.setFont("Helvetica", 7)
    c.drawString(text_x, ty, f"Total: {total_qty} pieces")
    c.drawString(text_x + 1.6 * inch, ty, f"Weight: {_format_weight(total_weight)}")

    ty -= 0.14 * inch
    length_varies = mat_group.get("length_varies", False)
    if length_varies:
        c.drawString(text_x, ty, "Length: varies (see destinations)")
        c.drawString(text_x + 2.2 * inch, ty, f"Job: {job_code}")
    elif unit_length_in is not None:
        c.drawString(text_x, ty, f"Length: {_fmt_ft_in(unit_length_in)} ea")
        c.drawString(text_x + 1.6 * inch, ty, f"Job: {job_code}")
    else:
        c.drawString(text_x, ty, f"Job: {job_code}")

    # Divider: DESTINATIONS
    div_y = qr_y - 0.06 * inch
    _draw_divider(c, div_y, "DESTINATIONS")

    # Destination list — include per-dest lengths when they vary
    dest_lengths = mat_group.get("dest_lengths", {})
    length_varies = mat_group.get("length_varies", False)
    dest_y = div_y - 0.16 * inch
    c.setFont("Helvetica", 7)
    c.setFillColor(black)
    dest_parts = []
    for dest_name, qty in destinations.items():
        part_str = f"{dest_name}: {qty} pcs"
        if length_varies and dest_name in dest_lengths:
            part_str += f" @ {_fmt_ft_in(dest_lengths[dest_name])}"
        dest_parts.append(part_str)
    dest_line = "  |  ".join(dest_parts)
    # Wrap if needed
    if c.stringWidth(dest_line, "Helvetica", 7) > (W - 2 * M):
        # Split into two lines
        mid = len(dest_parts) // 2
        c.drawString(M, dest_y, "  |  ".join(dest_parts[:mid + 1]))
        dest_y -= 0.12 * inch
        c.drawString(M, dest_y, "  |  ".join(dest_parts[mid + 1:]))
    else:
        c.drawString(M, dest_y, dest_line)

    # Divider: PULL CHECKLIST
    dest_y -= 0.10 * inch
    _draw_divider(c, dest_y, "PULL CHECKLIST")

    # Checkbox grid
    grid_y = dest_y - 0.10 * inch
    _draw_checkbox_grid(c, M, grid_y, total_qty,
                        cols_per_group=10, box_size=9, gap=2, group_gap=6)

    # Bottom accent line
    c.setStrokeColor(black)
    c.setLineWidth(2)
    c.line(0, foot_h + 0.01 * inch, W, foot_h + 0.01 * inch)


def generate_material_master_pdf(
    wo_dict: dict,
    config_dict: dict,
    app_base_url: str = "http://localhost:8888",
) -> bytes:
    """
    Generate PDF with one 6x4 material master sticker per unique material spec.

    Args:
        wo_dict: Work order dict (work_order_id, job_code, revision, items)
        config_dict: ShopDrawingConfig as dict
        app_base_url: Base URL for QR code links

    Returns:
        PDF bytes
    """
    buf = io.BytesIO()
    c = Canvas(buf, pagesize=(W, H))

    job_code = wo_dict.get("job_code", "")
    wo_items = wo_dict.get("items", [])
    groups = get_material_groups(config_dict, wo_items)

    for spec_key in sorted(groups.keys()):
        _draw_material_master_sticker(c, groups[spec_key], job_code, app_base_url)
        c.showPage()

    c.save()
    return buf.getvalue()


# ============================================================================
# 3C. MATERIAL SUB-STICKER RENDERER
# ============================================================================

def _draw_material_sub_sticker(c: Canvas, spec: str, dest_name: str,
                               dest_qty: int, total_weight: float,
                               unit_length_in: Optional[float],
                               total_qty_all: int,
                               job_code: str,
                               app_base_url: str = "http://localhost:8888"):
    """Draw a single material sub-sticker on the current page."""
    print_date = datetime.date.today().strftime("%m/%d")

    qr_data = (f"{app_base_url}/wo/{job_code}/material/"
               f"{spec.replace(' ', '_')}/{dest_name.replace(' ', '_')}")

    c.setPageSize((W, H))

    # Header
    title = f"MATERIAL -- FOR {dest_name.upper()}"
    y = _draw_header(c, title, print_date)
    foot_h = _draw_footer(c)

    # QR code + material info
    qr_size = 0.80 * inch
    qr_x = M
    qr_y = y - qr_size - 0.06 * inch
    _draw_qr(c, qr_data, qr_x, qr_y, qr_size)

    text_x = M + qr_size + 0.12 * inch
    ty = y - 0.16 * inch

    # Material spec (large)
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 11)
    max_chars = 42
    spec_display = spec if len(spec) <= max_chars else spec[:max_chars - 2] + ".."
    c.drawString(text_x, ty, spec_display)

    ty -= 0.18 * inch
    c.setFont("Helvetica", 7)
    # Pro-rate weight by destination qty
    if total_qty_all > 0:
        dest_weight = total_weight * (dest_qty / total_qty_all)
    else:
        dest_weight = 0
    c.drawString(text_x, ty, f"Qty: {dest_qty} pieces")
    c.drawString(text_x + 1.6 * inch, ty, f"Weight: {_format_weight(dest_weight)}")

    ty -= 0.14 * inch
    if unit_length_in is not None:
        c.drawString(text_x, ty, f"Length: {_fmt_ft_in(unit_length_in)} ea")
        c.drawString(text_x + 1.6 * inch, ty, f"Job: {job_code}")
    else:
        c.drawString(text_x, ty, f"Job: {job_code}")

    # Divider: PULL CHECKLIST
    div_y = qr_y - 0.06 * inch
    _draw_divider(c, div_y, "PULL CHECKLIST")

    # Checkbox grid
    grid_y = div_y - 0.10 * inch
    _draw_checkbox_grid(c, M, grid_y, dest_qty,
                        cols_per_group=10, box_size=10, gap=2, group_gap=6)

    # Bottom accent line
    c.setStrokeColor(black)
    c.setLineWidth(2)
    c.line(0, foot_h + 0.01 * inch, W, foot_h + 0.01 * inch)


def generate_material_sub_pdf(
    wo_dict: dict,
    config_dict: dict,
    app_base_url: str = "http://localhost:8888",
) -> bytes:
    """
    Generate PDF with one 6x4 sticker per material spec per parent assembly type.

    Args:
        wo_dict: Work order dict (work_order_id, job_code, revision, items)
        config_dict: ShopDrawingConfig as dict
        app_base_url: Base URL for QR code links

    Returns:
        PDF bytes
    """
    buf = io.BytesIO()
    c = Canvas(buf, pagesize=(W, H))

    job_code = wo_dict.get("job_code", "")
    wo_items = wo_dict.get("items", [])
    groups = get_material_groups(config_dict, wo_items)

    for spec_key in sorted(groups.keys()):
        g = groups[spec_key]
        for dest_name in sorted(g["destinations"].keys()):
            dest_qty = g["destinations"][dest_name]
            # Use per-destination length if available, else fall back to group
            dest_len = g.get("dest_lengths", {}).get(dest_name, g.get("unit_length_in"))
            # Use per-destination weight if available
            dest_wt = g.get("dest_weights", {}).get(dest_name, 0.0)
            _draw_material_sub_sticker(
                c,
                spec=g["spec"],
                dest_name=dest_name,
                dest_qty=dest_qty,
                total_weight=dest_wt,
                unit_length_in=dest_len,
                total_qty_all=dest_qty,  # use dest_qty so weight = dest_wt exactly
                job_code=job_code,
                app_base_url=app_base_url,
            )
            c.showPage()

    c.save()
    return buf.getvalue()


# ============================================================================
# 4. ZPL GENERATORS  (Zebra ZT411, 203 DPI, 6"x4" landscape, Wax/Resin)
# ============================================================================

# ZPL constants for 6x4 at 203 DPI
_ZPL_DPI = 203
_ZPL_W = int(6.0 * _ZPL_DPI)   # 1218 dots
_ZPL_H = int(4.0 * _ZPL_DPI)   # 812 dots
_ZPL_M = int(0.15 * _ZPL_DPI)  # ~30 dots margin


def _zpl_header() -> str:
    return (
        "^XA\n"
        f"^PW{_ZPL_W}\n"
        f"^LL{_ZPL_H}\n"
        "^CI28\n"
        "^MD30\n"
        "^PR4,4,4\n"
    )


def _zpl_footer() -> str:
    return "^XZ\n"


def _zpl_text(x: int, y: int, font_h: int, text: str,
              bold: bool = False, right_align: bool = False) -> str:
    font_w = int(font_h * 0.55) if not bold else int(font_h * 0.6)
    if right_align:
        usable = _ZPL_W - x - _ZPL_M
        return f"^FO{x},{y}^A0N,{font_h},{font_w}^FB{usable},1,0,R^FD{text}^FS\n"
    return f"^FO{x},{y}^A0N,{font_h},{font_w}^FD{text}^FS\n"


def _zpl_line(x1: int, y1: int, x2: int, y2: int, thickness: int = 2) -> str:
    if y1 == y2:
        return f"^FO{x1},{y1}^GB{x2 - x1},{thickness},B^FS\n"
    return f"^FO{x1},{y1}^GB{thickness},{y2 - y1},B^FS\n"


def _zpl_rect(x: int, y: int, w: int, h: int, thickness: int = 2) -> str:
    return f"^FO{x},{y}^GB{w},{h},{thickness}^FS\n"


def _zpl_filled_rect(x: int, y: int, w: int, h: int) -> str:
    return f"^FO{x},{y}^GB{w},{h},{h},B^FS\n"


def _zpl_qr(x: int, y: int, data: str, mag: int = 4) -> str:
    return f"^FO{x},{y}^BQN,2,{mag}^FDMM,{data}^FS\n"


def _zpl_checkbox(x: int, y: int, size: int = 18) -> str:
    return _zpl_rect(x, y, size, size, 1)


def generate_assembly_sticker_zpl(
    wo_dict: dict,
    items: Optional[List[dict]] = None,
    config_dict: Optional[dict] = None,
    app_base_url: str = "http://localhost:8888",
) -> str:
    """Generate ZPL commands for assembly stickers (one label per item)."""
    cfg = config_dict or {}
    target_items = items or wo_dict.get("items", [])
    job_code = wo_dict.get("job_code", "")
    wo_id = wo_dict.get("work_order_id", "")
    print_date = datetime.date.today().strftime("%m/%d/%Y")
    zpl_all = ""

    for item in target_items:
        ship_mark = item.get("ship_mark", "???")
        comp_type = item.get("component_type", "") or _parse_component_type(ship_mark)
        desc = item.get("description", "")[:50]
        machine = item.get("machine", "")
        item_id = item.get("item_id", ship_mark)
        qr_data = f"{app_base_url}/wo/{job_code}/{item_id}"

        zpl = _zpl_header()
        hdr_h = 60
        zpl += _zpl_filled_rect(0, 0, _ZPL_W, hdr_h)
        zpl += f"^FO{_ZPL_M},{8}^A0N,24,13^FR^FDTITANFORGE^FS\n"
        zpl += f"^FO{_ZPL_M + 200},{12}^A0N,18,10^FR^FDASSEMBLY STICKER^FS\n"
        zpl += f"^FO{_ZPL_W - _ZPL_M - 220},{12}^A0N,18,10^FR^FDPrinted: {print_date}^FS\n"
        zpl += _zpl_line(_ZPL_M, hdr_h + 4, _ZPL_W - _ZPL_M, hdr_h + 4, 3)

        qr_y = hdr_h + 16
        zpl += _zpl_qr(_ZPL_M, qr_y, qr_data, 4)

        text_x = _ZPL_M + 200
        zpl += _zpl_text(text_x, qr_y + 4, 50, ship_mark, bold=True)
        badge_text = comp_type.upper().replace("_", " ")
        badge_x = text_x + len(ship_mark) * 32 + 16
        zpl += _zpl_rect(badge_x, qr_y + 8, len(badge_text) * 12 + 16, 28, 2)
        zpl += _zpl_text(badge_x + 8, qr_y + 12, 20, badge_text, bold=True)
        zpl += _zpl_text(text_x, qr_y + 60, 18, desc)

        info_y = qr_y + 86
        zpl += _zpl_text(text_x, info_y, 16, f"JOB: {job_code}", bold=True)
        zpl += _zpl_text(text_x + 300, info_y, 16, f"Machine: {machine}", bold=True)

        div_y = qr_y + 180
        zpl += _zpl_line(_ZPL_M, div_y, _ZPL_W - _ZPL_M, div_y, 2)

        cut_list = get_assembly_cut_list(cfg, comp_type, ship_mark)
        line_y = div_y + 10
        for part in cut_list:
            if line_y > _ZPL_H - 70:
                break
            zpl += _zpl_checkbox(_ZPL_M + 4, line_y, 16)
            zpl += _zpl_text(_ZPL_M + 28, line_y, 18, f"{part['qty']}x", bold=True)
            zpl += _zpl_text(_ZPL_M + 64, line_y, 18, part["spec"])
            if part.get("length_in"):
                zpl += _zpl_text(0, line_y, 16,
                                _fmt_ft_in(part["length_in"]) + " ea", right_align=True)
            line_y += 28

        foot_y = _ZPL_H - 38
        zpl += _zpl_line(0, foot_y, _ZPL_W, foot_y, 2)
        zpl += _zpl_text(_ZPL_W // 2 - 280, foot_y + 8, 14, FOOTER_TEXT)
        zpl += _zpl_footer()
        zpl_all += zpl

    return zpl_all


def generate_material_master_zpl(
    wo_dict: dict, config_dict: dict,
    app_base_url: str = "http://localhost:8888",
) -> str:
    """Generate ZPL commands for material master stickers."""
    job_code = wo_dict.get("job_code", "")
    wo_items = wo_dict.get("items", [])
    groups = get_material_groups(config_dict, wo_items)
    print_date = datetime.date.today().strftime("%m/%d/%Y")
    zpl_all = ""

    for spec_key in sorted(groups.keys()):
        g = groups[spec_key]
        qr_data = f"{app_base_url}/wo/{job_code}/material/{g['spec'].replace(' ', '_')}"
        zpl = _zpl_header()

        hdr_h = 60
        zpl += _zpl_filled_rect(0, 0, _ZPL_W, hdr_h)
        zpl += f"^FO{_ZPL_M},{8}^A0N,24,13^FR^FDTITANFORGE^FS\n"
        zpl += f"^FO{_ZPL_M + 200},{12}^A0N,18,10^FR^FDMATERIAL STICKER^FS\n"
        zpl += f"^FO{_ZPL_W - _ZPL_M - 220},{12}^A0N,18,10^FR^FDPrinted: {print_date}^FS\n"
        zpl += _zpl_line(_ZPL_M, hdr_h + 4, _ZPL_W - _ZPL_M, hdr_h + 4, 3)

        qr_y = hdr_h + 16
        zpl += _zpl_qr(_ZPL_M, qr_y, qr_data, 4)

        text_x = _ZPL_M + 200
        zpl += _zpl_text(text_x, qr_y + 4, 28, g["spec"][:40], bold=True)
        zpl += _zpl_text(text_x, qr_y + 40, 20, f"Total: {g['total_qty']} pieces")
        zpl += _zpl_text(text_x + 300, qr_y + 40, 20,
                        f"Weight: {_format_weight(g['total_weight'])}")

        info_y = qr_y + 68
        unit_len = g.get("unit_length_in")
        if unit_len:
            zpl += _zpl_text(text_x, info_y, 18, f"Length: {_fmt_ft_in(unit_len)} ea")
        zpl += _zpl_text(text_x + 300, info_y, 18, f"Job: {job_code}")

        div_y = qr_y + 180
        zpl += _zpl_line(_ZPL_M, div_y, _ZPL_W - _ZPL_M, div_y, 2)
        dest_parts = [f"{k}: {v} pcs" for k, v in g.get("destinations", {}).items()]
        zpl += _zpl_text(_ZPL_M, div_y + 8, 18, " | ".join(dest_parts)[:80])

        check_y = div_y + 36
        zpl += _zpl_line(_ZPL_M, check_y, _ZPL_W - _ZPL_M, check_y, 2)
        cb_y = check_y + 8
        drawn = 0
        while drawn < min(g["total_qty"], 60):
            cx = _ZPL_M + 4
            for _ in range(15):
                if drawn >= min(g["total_qty"], 60):
                    break
                zpl += _zpl_checkbox(cx, cb_y, 18)
                cx += 22
                drawn += 1
            cb_y += 22

        foot_y = _ZPL_H - 38
        zpl += _zpl_line(0, foot_y, _ZPL_W, foot_y, 2)
        zpl += _zpl_text(_ZPL_W // 2 - 280, foot_y + 8, 14, FOOTER_TEXT)
        zpl += _zpl_footer()
        zpl_all += zpl

    return zpl_all


def generate_material_sub_zpl(
    wo_dict: dict, config_dict: dict,
    app_base_url: str = "http://localhost:8888",
) -> str:
    """Generate ZPL commands for material sub-stickers."""
    job_code = wo_dict.get("job_code", "")
    groups = get_material_groups(config_dict, wo_dict.get("items", []))
    zpl_all = ""

    for spec_key in sorted(groups.keys()):
        g = groups[spec_key]
        for dest_name in sorted(g["destinations"].keys()):
            dest_qty = g["destinations"][dest_name]
            dest_wt = (g["total_weight"] * dest_qty / g["total_qty"]
                      if g["total_qty"] > 0 else 0)
            unit_len = g.get("unit_length_in")
            print_date = datetime.date.today().strftime("%m/%d")
            qr_data = (f"{app_base_url}/wo/{job_code}/material/"
                       f"{g['spec'].replace(' ', '_')}/{dest_name.replace(' ', '_')}")

            zpl = _zpl_header()
            hdr_h = 60
            title = f"MATERIAL -- FOR {dest_name.upper()}"
            zpl += _zpl_filled_rect(0, 0, _ZPL_W, hdr_h)
            zpl += f"^FO{_ZPL_M},{8}^A0N,24,13^FR^FDTITANFORGE^FS\n"
            zpl += f"^FO{_ZPL_M + 200},{12}^A0N,16,9^FR^FD{title}^FS\n"
            zpl += _zpl_line(_ZPL_M, hdr_h + 4, _ZPL_W - _ZPL_M, hdr_h + 4, 3)

            qr_y = hdr_h + 16
            zpl += _zpl_qr(_ZPL_M, qr_y, qr_data, 4)

            text_x = _ZPL_M + 200
            zpl += _zpl_text(text_x, qr_y + 4, 28, g["spec"][:40], bold=True)
            zpl += _zpl_text(text_x, qr_y + 40, 20, f"Qty: {dest_qty} pieces")
            zpl += _zpl_text(text_x + 300, qr_y + 40, 20,
                            f"Weight: {_format_weight(dest_wt)}")
            info_y = qr_y + 68
            if unit_len:
                zpl += _zpl_text(text_x, info_y, 18,
                                f"Length: {_fmt_ft_in(unit_len)} ea")
            zpl += _zpl_text(text_x + 300, info_y, 18, f"Job: {job_code}")

            div_y = qr_y + 180
            zpl += _zpl_line(_ZPL_M, div_y, _ZPL_W - _ZPL_M, div_y, 2)
            cb_y = div_y + 8
            drawn = 0
            while drawn < min(dest_qty, 60):
                cx = _ZPL_M + 4
                for _ in range(15):
                    if drawn >= min(dest_qty, 60):
                        break
                    zpl += _zpl_checkbox(cx, cb_y, 20)
                    cx += 24
                    drawn += 1
                cb_y += 24

            foot_y = _ZPL_H - 38
            zpl += _zpl_line(0, foot_y, _ZPL_W, foot_y, 2)
            zpl += _zpl_text(_ZPL_W // 2 - 280, foot_y + 8, 14, FOOTER_TEXT)
            zpl += _zpl_footer()
            zpl_all += zpl

    return zpl_all


# ============================================================================
# 5. NLBL (NiceLabel) TEMPLATE + CSV DATA SOURCE GENERATORS
# ============================================================================

import csv as _csv_mod
import xml.etree.ElementTree as ET
from xml.dom import minidom


def _nlbl_label_xml(width_mm: float, height_mm: float, dpi: int = 203):
    root = ET.Element("NiceLabel")
    root.set("version", "10.0")
    label = ET.SubElement(root, "Label")
    label.set("name", "TitanForge_FabSticker")
    fmt = ET.SubElement(label, "Format")
    ET.SubElement(fmt, "Width").text = str(round(width_mm, 2))
    ET.SubElement(fmt, "Height").text = str(round(height_mm, 2))
    ET.SubElement(fmt, "Orientation").text = "Landscape"
    ET.SubElement(fmt, "Unit").text = "mm"
    printer = ET.SubElement(label, "Printer")
    ET.SubElement(printer, "Name").text = "Zebra ZT411 (203 dpi)"
    ET.SubElement(printer, "DPI").text = str(dpi)
    ET.SubElement(printer, "MediaType").text = "ThermalTransfer"
    ET.SubElement(printer, "RibbonType").text = "WaxResin"
    return root, label


def _nlbl_add_text(objs, name, x, y, size, text="", bold=False, variable=False):
    obj = ET.SubElement(objs, "TextObject")
    obj.set("name", name)
    pos = ET.SubElement(obj, "Position")
    ET.SubElement(pos, "X").text = str(round(x, 2))
    ET.SubElement(pos, "Y").text = str(round(y, 2))
    font = ET.SubElement(obj, "Font")
    ET.SubElement(font, "Name").text = "Arial"
    ET.SubElement(font, "Size").text = str(round(size, 1))
    ET.SubElement(font, "Bold").text = "true" if bold else "false"
    if variable:
        ds = ET.SubElement(obj, "DataSource")
        ET.SubElement(ds, "Type").text = "Variable"
        ET.SubElement(ds, "VariableName").text = name
    else:
        ET.SubElement(obj, "Content").text = text


def _nlbl_add_barcode(objs, name, x, y, size_mm, data="", variable=False):
    obj = ET.SubElement(objs, "BarcodeObject")
    obj.set("name", name)
    pos = ET.SubElement(obj, "Position")
    ET.SubElement(pos, "X").text = str(round(x, 2))
    ET.SubElement(pos, "Y").text = str(round(y, 2))
    bc = ET.SubElement(obj, "Barcode")
    ET.SubElement(bc, "Type").text = "QRCode"
    ET.SubElement(bc, "Size").text = str(round(size_mm, 2))
    if variable:
        ds = ET.SubElement(obj, "DataSource")
        ET.SubElement(ds, "Type").text = "Variable"
        ET.SubElement(ds, "VariableName").text = name
    else:
        ET.SubElement(obj, "Content").text = data


def _nlbl_add_line(objs, name, x1, y1, x2, y2, thickness=0.5):
    obj = ET.SubElement(objs, "LineObject")
    obj.set("name", name)
    start = ET.SubElement(obj, "Start")
    ET.SubElement(start, "X").text = str(round(x1, 2))
    ET.SubElement(start, "Y").text = str(round(y1, 2))
    end = ET.SubElement(obj, "End")
    ET.SubElement(end, "X").text = str(round(x2, 2))
    ET.SubElement(end, "Y").text = str(round(y2, 2))
    ET.SubElement(obj, "Thickness").text = str(round(thickness, 2))


def _nlbl_add_rect(objs, name, x, y, w, h, filled=False):
    obj = ET.SubElement(objs, "RectangleObject")
    obj.set("name", name)
    pos = ET.SubElement(obj, "Position")
    ET.SubElement(pos, "X").text = str(round(x, 2))
    ET.SubElement(pos, "Y").text = str(round(y, 2))
    sz = ET.SubElement(obj, "Size")
    ET.SubElement(sz, "Width").text = str(round(w, 2))
    ET.SubElement(sz, "Height").text = str(round(h, 2))
    ET.SubElement(obj, "FillColor").text = "Black" if filled else "None"


def _nlbl_to_string(root):
    rough = ET.tostring(root, encoding="unicode", xml_declaration=True)
    return minidom.parseString(rough).toprettyxml(indent="  ")


def generate_assembly_sticker_nlbl() -> str:
    """Generate NiceLabel .nlbl template for assembly stickers with variable fields."""
    w_mm, h_mm = 152.4, 101.6
    root, label = _nlbl_label_xml(w_mm, h_mm)

    variables = ET.SubElement(label, "Variables")
    for vn in ["ShipMark", "ComponentType", "Description", "Machine",
               "JobCode", "WorkOrderID", "DrawingRef", "QRData"] + \
              [f"CutList{i}" for i in range(1, 9)]:
        v = ET.SubElement(variables, "Variable")
        ET.SubElement(v, "Name").text = vn
        ET.SubElement(v, "Type").text = "Text"

    objs = ET.SubElement(label, "Objects")
    _nlbl_add_rect(objs, "HeaderBar", 0, 0, w_mm, 9, filled=True)
    _nlbl_add_text(objs, "Hdr", 4, 1.5, 6, "TITANFORGE", bold=True)
    _nlbl_add_line(objs, "AccLine", 0, 9.5, w_mm, 9.5, 0.8)
    _nlbl_add_barcode(objs, "QRData", 4, 12, 20, variable=True)
    _nlbl_add_text(objs, "ShipMark", 50, 12, 14, variable=True, bold=True)
    _nlbl_add_text(objs, "ComponentType", 50, 24, 6, variable=True, bold=True)
    _nlbl_add_text(objs, "Description", 50, 31, 5, variable=True)
    _nlbl_add_text(objs, "JobCode", 50, 38, 5, variable=True, bold=True)
    _nlbl_add_text(objs, "Machine", 100, 38, 5, variable=True, bold=True)
    _nlbl_add_line(objs, "CutDiv", 4, 50, w_mm - 4, 50, 0.5)
    for i in range(1, 9):
        y = 53 + (i - 1) * 5.5
        _nlbl_add_rect(objs, f"CB{i}", 5, y, 3.5, 3.5)
        _nlbl_add_text(objs, f"CutList{i}", 10, y, 5, variable=True)
    _nlbl_add_line(objs, "FootLine", 0, h_mm - 6, w_mm, h_mm - 6, 0.5)
    _nlbl_add_text(objs, "Footer", 15, h_mm - 5.5, 3.5, FOOTER_TEXT)

    return _nlbl_to_string(root)


def generate_material_sticker_nlbl() -> str:
    """Generate NiceLabel .nlbl template for material stickers."""
    w_mm, h_mm = 152.4, 101.6
    root, label = _nlbl_label_xml(w_mm, h_mm)

    variables = ET.SubElement(label, "Variables")
    for vn in ["MaterialSpec", "TotalQty", "TotalWeight", "UnitLength",
               "JobCode", "Destinations", "StickerType", "QRData"]:
        v = ET.SubElement(variables, "Variable")
        ET.SubElement(v, "Name").text = vn
        ET.SubElement(v, "Type").text = "Text"

    objs = ET.SubElement(label, "Objects")
    _nlbl_add_rect(objs, "HeaderBar", 0, 0, w_mm, 9, filled=True)
    _nlbl_add_text(objs, "Hdr", 4, 1.5, 6, "TITANFORGE", bold=True)
    _nlbl_add_text(objs, "StickerType", 30, 2, 5, variable=True)
    _nlbl_add_line(objs, "AccLine", 0, 9.5, w_mm, 9.5, 0.8)
    _nlbl_add_barcode(objs, "QRData", 4, 12, 20, variable=True)
    _nlbl_add_text(objs, "MaterialSpec", 50, 12, 8, variable=True, bold=True)
    _nlbl_add_text(objs, "TotalQty", 50, 22, 5, variable=True)
    _nlbl_add_text(objs, "TotalWeight", 100, 22, 5, variable=True)
    _nlbl_add_text(objs, "UnitLength", 50, 28, 5, variable=True)
    _nlbl_add_text(objs, "JobCode", 100, 28, 5, variable=True)
    _nlbl_add_line(objs, "DestDiv", 4, 36, w_mm - 4, 36, 0.5)
    _nlbl_add_text(objs, "Destinations", 5, 38, 5, variable=True)
    _nlbl_add_line(objs, "CheckDiv", 4, 48, w_mm - 4, 48, 0.5)
    for row in range(6):
        for col in range(15):
            _nlbl_add_rect(objs, f"CB_{row}_{col}", 5 + col * 9.5, 51 + row * 7, 5, 5)
    _nlbl_add_line(objs, "FootLine", 0, h_mm - 6, w_mm, h_mm - 6, 0.5)
    _nlbl_add_text(objs, "Footer", 15, h_mm - 5.5, 3.5, FOOTER_TEXT)

    return _nlbl_to_string(root)


def generate_assembly_sticker_csv(
    wo_dict: dict, items: Optional[List[dict]] = None,
    config_dict: Optional[dict] = None,
    app_base_url: str = "http://localhost:8888",
) -> str:
    """Generate CSV data source for assembly sticker NLBL template."""
    cfg = config_dict or {}
    target_items = items or wo_dict.get("items", [])
    job_code = wo_dict.get("job_code", "")
    wo_id = wo_dict.get("work_order_id", "")

    buf = io.StringIO()
    writer = _csv_mod.writer(buf)
    headers = ["ShipMark", "ComponentType", "Description", "Machine",
               "JobCode", "WorkOrderID", "DrawingRef", "QRData"] + \
              [f"CutList{i}" for i in range(1, 9)]
    writer.writerow(headers)

    for item in target_items:
        ship_mark = item.get("ship_mark", "")
        comp_type = item.get("component_type", "") or _parse_component_type(ship_mark)
        item_id = item.get("item_id", ship_mark)
        cut_list = get_assembly_cut_list(cfg, comp_type, ship_mark)
        cut_strs = []
        for part in cut_list[:8]:
            s = f"{part['qty']}x {part['spec']}"
            if part.get("length_in"):
                s += f" - {_fmt_ft_in(part['length_in'])} ea"
            cut_strs.append(s)
        while len(cut_strs) < 8:
            cut_strs.append("")

        row = [ship_mark, comp_type.upper().replace("_", " "),
               item.get("description", ""), item.get("machine", ""),
               job_code, wo_id, item.get("drawing_ref", ""),
               f"{app_base_url}/wo/{job_code}/{item_id}"] + cut_strs
        writer.writerow(row)

    return buf.getvalue()


def generate_material_sticker_csv(
    wo_dict: dict, config_dict: dict,
    sticker_type: str = "master",
    app_base_url: str = "http://localhost:8888",
) -> str:
    """Generate CSV data source for material sticker NLBL template."""
    job_code = wo_dict.get("job_code", "")
    groups = get_material_groups(config_dict, wo_dict.get("items", []))

    buf = io.StringIO()
    writer = _csv_mod.writer(buf)
    headers = ["MaterialSpec", "TotalQty", "TotalWeight", "UnitLength",
               "JobCode", "Destinations", "StickerType", "QRData"]
    writer.writerow(headers)

    for spec_key in sorted(groups.keys()):
        g = groups[spec_key]
        unit_len = g.get("unit_length_in")
        unit_len_str = _fmt_ft_in(unit_len) + " ea" if unit_len else ""

        if sticker_type == "master":
            dest_str = " | ".join(f"{k}: {v} pcs" for k, v in g["destinations"].items())
            row = [g["spec"], str(g["total_qty"]), _format_weight(g["total_weight"]),
                   unit_len_str, job_code, dest_str, "MATERIAL STICKER",
                   f"{app_base_url}/wo/{job_code}/material/{g['spec'].replace(' ', '_')}"]
            writer.writerow(row)
        else:
            for dest_name, dest_qty in g["destinations"].items():
                dest_wt = (g["total_weight"] * dest_qty / g["total_qty"]
                          if g["total_qty"] > 0 else 0)
                row = [g["spec"], str(dest_qty), _format_weight(dest_wt),
                       unit_len_str, job_code, dest_name,
                       f"MATERIAL -- FOR {dest_name.upper()}",
                       f"{app_base_url}/wo/{job_code}/material/"
                       f"{g['spec'].replace(' ', '_')}/{dest_name.replace(' ', '_')}"]
                writer.writerow(row)

    return buf.getvalue()
