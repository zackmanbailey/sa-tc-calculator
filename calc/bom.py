"""
Structures America Material Takeoff Calculator
Core BOM Calculation Engine — v2.3

Key structural logic:
  TEE frame:    1 center column per frame, rafter = full building width
  2-POST frame: 2 columns per frame (at 1/3 and 2/3 of width), rafter = full width
  Column count: n_bays = floor(length / max_bay), n_columns = n_bays + 1
                overhangs are equal at each end = (length - n_bays*max_bay) / 2
  Column height: clear_height + angle_addition + embedment + buffer
  Panels:       eave-to-eave (no ridge), split at nearest purlin to center
  Sag rods:     2 per rafter x 2 pieces each (max 20'3" piece) = 4 pieces/rafter
  Purlins:      floor(width/spacing)+1 lines x building_length
  Trim:         all 4 sides, sticks with 3" overlap
"""

import math
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from calc.defaults import (
    COILS, PURCHASED_ITEMS, REBAR, SCREWS, TRIM,
    WASTE_FACTORS, DEFAULTS, PITCH_OPTIONS, ROOF_SLOPES,
    LABOR, WELDING_CONSUMABLES, BOLT_ASSEMBLIES, ENDCAP_U_CHANNELS,
    get_purlin_spacing, get_rebar_size
)


# ─────────────────────────────────────────────
# INPUT DATA STRUCTURES
# ─────────────────────────────────────────────

@dataclass
class ProjectInfo:
    name: str = ""
    job_code: str = ""
    address: str = ""
    city: str = ""
    state: str = "TX"
    zip_code: str = ""
    customer_name: str = ""
    quote_date: str = ""
    wind_speed_mph: float = 115.0
    footing_depth_ft: float = 10.0
    markup_pct: float = 35.0
    include_trim: bool = False


@dataclass
class BuildingConfig:
    building_id: str = "B1"
    building_name: str = "Building 1"
    type: str = "2post"             # '2post' or 'tee'
    width_ft: float = 40.0          # full building width (eave to eave)
    length_ft: float = 200.0        # total building length
    clear_height_ft: float = 14.0   # clearance height at eave
    max_bay_ft: float = 36.0        # max spacing between column frames
    pitch_key: str = "1/4:12"       # key from PITCH_OPTIONS
    purlin_spacing_override: Optional[float] = None   # None = auto-calc
    embedment_ft: float = 4.333     # 4'-4" default
    column_buffer_ft: float = 0.5   # 6" buffer
    reinforced: bool = True         # True: rebar = depth+8'; False: depth-embedment
    rebar_col_size: Optional[str] = None   # None = auto; "#5" through "#11"
    rebar_beam_size: Optional[str] = None
    # Column placement mode
    overhang_mode: str = "none"        # 'none' or '1space'
    space_width_ft: float = 0.0        # parking stall width; 0 = use legacy equal-overhang
    # Rafter-to-Purlin Straps (merged: was hurricane_straps + bottom_braces)
    straps_per_rafter: int = 4      # 1 purlin in from each eave × 2 straps per position = 4
    strap_length_in: float = 28.0
    # Wall options
    include_back_wall: bool = False     # 1 long rear wall
    include_end_walls: bool = False     # 2 short gable end walls
    include_side_walls: bool = False    # both long side walls (front + back)
    wall_girt_spacing_override: Optional[float] = None  # None = same auto as roof purlins
    # Rafter rebar
    include_rafter_rebar: bool = False
    rebar_rafter_size: Optional[str] = "#9"
    rebar_max_stick_ft: float = 20.0       # max rebar stick length in rafter
    rebar_end_gap_ft: float = 5.0          # gap from rafter end to first rebar
    # Angled purlins
    angled_purlins: bool = False            # master toggle for angled purlin mode
    purlin_angle_deg: float = 15.0          # angle from perpendicular (5–45°)
    # Column placement on rafter
    column_mode: str = "auto"               # "auto", "spacing", or "manual"
    column_spacing_ft: float = 25.0         # used when column_mode == "spacing"
    column_count_manual: int = 1            # used when column_mode == "manual"
    column_positions_manual: str = ""       # comma-separated ft positions for manual mode
    front_col_position_ft: float = 0.0      # front column position when back wall enabled
    splice_location_ft: float = 0.0         # user-specified splice (0 = auto)
    # Purlin & column drawing fields
    purlin_type: str = "Z"                  # "Z" or "C" purlin profile
    roofing_overhang_ft: float = 0.5        # panel overhang past eave purlin
    above_grade_ft: float = 8.0             # column height above finished grade
    cut_allowance_in: float = 6.0           # extra length for field cuts (inches)
    footing_depth_ft: float = 10.0          # per-building footing depth (default 10')
    # Misc
    include_trim: bool = False
    welding_cost_per_5000sqft: float = 300.0
    include_labor: bool = True
    labor_daily_rate: float = 960.0      # adjustable base daily rate (4 crew × $30/hr × 8hrs)
    coil_prices: Optional[Dict] = None   # {"c_section_23": 0.85, ...}
    # Accessories & secondary structural
    include_base_plates: bool = True     # base plates and anchor bolts
    include_x_bracing: bool = True       # rod bracing in end bays + every 4th bay
    include_eave_struts: bool = True     # cee purlin at eave, both sides
    include_ridge_cap: bool = True       # ridge cap flashing
    include_gutters: bool = True         # gutters + downspouts
    include_walk_doors: bool = False     # walk doors
    walk_door_qty: int = 0              # number of walk doors (0 = none)
    include_insulation: bool = False     # roof and wall insulation
    insulation_r_value: str = "R-13"    # R-13, R-19, R-25, etc.
    include_trim_package: bool = True    # full trim package (corners, base, eave, rake)
    column_size: str = "HSS 4x4"        # HSS 4x4 or HSS 6x6 (affects base plate size)


@dataclass
class BOMLineItem:
    category: str
    item_id: str
    description: str
    qty: float
    unit: str
    unit_weight_lbs: float = 0.0
    total_weight_lbs: float = 0.0
    unit_cost: float = 0.0
    total_cost: float = 0.0
    waste_factor: float = 0.0
    notes: str = ""
    piece_count: int = 0
    piece_length_in: float = 0.0


@dataclass
class BuildingBOM:
    building: BuildingConfig
    line_items: List[BOMLineItem] = field(default_factory=list)
    total_weight_lbs: float = 0.0
    total_material_cost: float = 0.0
    total_sell_price: float = 0.0
    geometry: Dict = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


@dataclass
class ProjectBOM:
    project: ProjectInfo
    buildings: List[BuildingBOM] = field(default_factory=list)
    total_material_cost: float = 0.0
    total_sell_price: float = 0.0
    total_weight_lbs: float = 0.0
    summary_by_coil: Dict = field(default_factory=dict)


# ─────────────────────────────────────────────
# GEOMETRY HELPERS
# ─────────────────────────────────────────────

def get_slope_deg(pitch_key: str) -> float:
    po = PITCH_OPTIONS.get(pitch_key)
    if po:
        return po["deg"]
    rs = ROOF_SLOPES.get(pitch_key)
    if rs:
        return rs["deg"]
    return PITCH_OPTIONS["1/4:12"]["deg"]


def calc_column_count(length_ft: float, max_bay_ft: float):
    """
    Equal-overhang column placement (legacy / no space_width set).
    Returns (n_columns, bay_size_ft, overhang_ft).
    n_bays = floor(length/max_bay); n_columns = n_bays+1
    """
    n_bays = max(1, math.floor(length_ft / max_bay_ft))
    n_columns = n_bays + 1
    overhang = (length_ft - n_bays * max_bay_ft) / 2.0
    return n_columns, max_bay_ft, overhang


def _build_bays(n_spaces: int, space_width_ft: float, max_sp_per_bay: int) -> list:
    """
    Fill n_spaces parking stalls into bays of max_sp_per_bay.
    If spaces don't divide evenly, the short bay is placed at the center index.
    Returns list of bay widths in feet.
    """
    if n_spaces <= 0:
        return []
    n_full = n_spaces // max_sp_per_bay
    short_spaces = n_spaces % max_sp_per_bay
    full_bay = max_sp_per_bay * space_width_ft
    if short_spaces == 0:
        return [full_bay] * n_full
    short_bay = short_spaces * space_width_ft
    total_bays = n_full + 1
    center_idx = total_bays // 2
    bays = []
    for i in range(total_bays):
        bays.append(short_bay if i == center_idx else full_bay)
    return bays


def calc_space_based_columns(length_ft: float, space_width_ft: float,
                              max_bay_ft: float, overhang_mode: str = 'none'):
    """
    Space-based column placement for carports / RV storage.

    Parking stalls define the module. Bays hold up to 3 stalls (or
    floor(max_bay / space_width) stalls, whichever is smaller).
    Short bays (when spaces don't divide evenly) are placed at the center.

    overhang_mode:
        'none'   — columns at both building ends, spans the full length
        '1space' — roof cantilevers 1 stall width at each end; first/last
                   columns are set in 1 space_width from the building ends

    Returns
    -------
    n_frames : int
        Number of column frame lines (positions)
    col_positions : list[float]
        Position of each frame in feet from the building start (0 = front face)
    bay_sizes : list[float]
        Width of each bay in feet (len == n_frames - 1)
    overhang_ft : float
        Cantilever length at each end (0 if 'none')
    warning : str or None
        Set if length_ft is not a whole multiple of space_width_ft
    """
    # ── Validate clean multiple ─────────────────────────────────────────
    remainder = length_ft % space_width_ft
    warning = None
    if remainder > 0.01:
        nearest = round(length_ft / space_width_ft) * space_width_ft
        warning = (
            f"Building length {length_ft:.0f}' is not an even multiple of "
            f"{space_width_ft:.1f}' space width ({remainder:.1f}' remainder). "
            f"Nearest clean length: {nearest:.0f}'."
        )

    n_total_spaces = round(length_ft / space_width_ft)

    # max spaces per bay: bounded by max_bay_ft AND hard cap of 3
    max_sp_per_bay = max(1, min(3, math.floor(max_bay_ft / space_width_ft)))

    if overhang_mode == '1space':
        overhang_ft = space_width_ft
        interior_spaces = max(1, n_total_spaces - 2)
    else:
        overhang_ft = 0.0
        interior_spaces = n_total_spaces

    bay_sizes = _build_bays(interior_spaces, space_width_ft, max_sp_per_bay)

    # Build frame positions
    start = overhang_ft
    positions = [round(start, 6)]
    for bay in bay_sizes:
        positions.append(round(positions[-1] + bay, 6))

    n_frames = len(positions)
    return n_frames, positions, bay_sizes, overhang_ft, warning


def calc_rafter_slope_length(width_ft: float, slope_deg: float) -> float:
    """Full rafter slope length eave-to-eave through peak (symmetric gable)."""
    half = width_ft / 2.0
    rise = half * math.tan(math.radians(slope_deg))
    return 2.0 * math.sqrt(half**2 + rise**2)


def calc_column_height(clear_height_ft, width_ft, col_type, slope_deg,
                        embedment_ft, buffer_ft) -> float:
    """
    Physical cut length: clear_height + angle_addition + embedment + buffer
    TEE: column at center (width/2 from eave)
    2-post: columns at 1/3 span from each eave
    """
    tan_s = math.tan(math.radians(slope_deg))
    dist = width_ft / 2.0 if col_type == "tee" else width_ft / 3.0
    return clear_height_ft + dist * tan_s + embedment_ft + buffer_ft


def calc_column_height_at(clear_height_ft, dist_from_eave_ft, slope_deg,
                           embedment_ft, buffer_ft) -> float:
    """
    Column height at a specific distance from the eave.
    Uses the actual distance from the eave rather than frame-type shortcuts.
    """
    tan_s = math.tan(math.radians(slope_deg))
    return clear_height_ft + dist_from_eave_ft * tan_s + embedment_ft + buffer_ft


def calc_rafter_columns(width_ft, column_mode="auto", column_spacing_ft=25.0,
                         column_count_manual=1, column_positions_manual="",
                         include_back_wall=False, front_col_position_ft=0.0):
    """
    Calculate structural column count and positions on a rafter.

    Returns (count, positions_in) where positions_in is a list of column
    positions in inches measured from the left end of the rafter.

    Modes:
      auto    — width <= 45' → 1 col at L/2
                width > 45'  → max(2, ceil(width/60)) at quarter-points
      spacing — columns evenly placed at user-specified spacing, centered
      manual  — user specifies count and optional explicit positions

    Back wall mode adds a rear column at 19" from the right end and a
    configurable front column position.

    All modes enforce P3 constraint: center >= 13" from rafter ends.
    """
    rafter_in = width_ft * 12.0
    p3_edge = 13.0   # P3 center minimum from end
    positions_in = []

    if column_mode == "manual":
        # User-specified positions
        if column_positions_manual and column_positions_manual.strip():
            for s in column_positions_manual.split(","):
                s = s.strip()
                if s:
                    try:
                        pos_in = float(s) * 12.0
                        positions_in.append(pos_in)
                    except ValueError:
                        pass
        else:
            # Manual count but no explicit positions — distribute evenly
            n = max(1, column_count_manual)
            spacing = rafter_in / (n + 1)
            for i in range(1, n + 1):
                positions_in.append(i * spacing)

    elif column_mode == "spacing":
        # Evenly spaced at user-defined interval, centered on rafter
        sp_in = column_spacing_ft * 12.0
        if sp_in <= 0:
            sp_in = 25.0 * 12.0
        n = max(1, math.floor(rafter_in / sp_in))
        total_span = (n - 1) * sp_in if n > 1 else 0
        start = (rafter_in - total_span) / 2.0
        for i in range(n):
            positions_in.append(start + i * sp_in)

    else:
        # Auto mode: width-based formula
        if width_ft <= 45.0:
            n_cols = 1
        else:
            n_cols = max(2, math.ceil(width_ft / 60.0))

        if n_cols == 1:
            positions_in = [rafter_in / 2.0]
        elif n_cols == 2:
            # Quarter-points: L/4 from each end
            positions_in = [rafter_in / 4.0, 3.0 * rafter_in / 4.0]
        else:
            # Outermost at L/4, inner fill evenly in the middle half
            left = rafter_in / 4.0
            right = 3.0 * rafter_in / 4.0
            inner = n_cols - 2
            inner_span = right - left
            inner_gap = inner_span / (inner + 1)
            positions_in = [left]
            for i in range(1, inner + 1):
                positions_in.append(left + i * inner_gap)
            positions_in.append(right)

    # Back wall override: back col at 19" from right end, front at user position
    if include_back_wall:
        back_col_in = rafter_in - 19.0
        if front_col_position_ft > 0:
            front_col_in = front_col_position_ft * 12.0
        else:
            # Default: symmetric — 19" from left end
            front_col_in = 19.0
        positions_in = [front_col_in, back_col_in]

    # Enforce P3 edge constraint
    positions_in = [
        max(p3_edge, min(rafter_in - p3_edge, p))
        for p in positions_in
    ]

    # Sort and deduplicate
    positions_in = sorted(set(round(p, 2) for p in positions_in))

    return len(positions_in), positions_in


def calc_purlin_lines(width_ft: float, spacing_ft: float) -> int:
    return math.floor(width_ft / spacing_ft) + 1


def calc_panel_split(width_ft: float, spacing_ft: float):
    """
    Find nearest purlin to center for panel split.
    Returns (front_piece_ft, back_piece_ft, split_purlin_pos_ft).
    Front piece = split_pos + 3" overlap. Back piece = width - split_pos.
    """
    overlap_ft = 3.0 / 12.0
    center = width_ft / 2.0
    n_lines = calc_purlin_lines(width_ft, spacing_ft)
    positions = [i * spacing_ft for i in range(n_lines)]
    split_pos = min(positions, key=lambda p: abs(p - center))
    return split_pos + overlap_ft, width_ft - split_pos, split_pos


def calc_trim_sticks(length_ft, width_ft, stick_ft=10.0, overlap_in=3.0) -> int:
    """Total trim sticks for all 4 sides with overlap."""
    usable = stick_ft - (overlap_in / 12.0)
    return math.ceil(length_ft / usable) * 2 + math.ceil(width_ft / usable) * 2


def coil_price(coil_id: str, overrides: Optional[Dict]) -> float:
    if overrides and coil_id in overrides:
        return float(overrides[coil_id])
    return COILS[coil_id]["price_per_lb"]


# ─────────────────────────────────────────────
# MAIN BOM CALCULATOR
# ─────────────────────────────────────────────

class BOMCalculator:

    def __init__(self, project: ProjectInfo):
        self.project = project

    # ─────────────────────────────────────────────
    # ACCESSORIES & SECONDARY STRUCTURAL MEMBERS
    # ─────────────────────────────────────────────

    def _generate_accessories(self, bldg: BuildingConfig, items: list,
                              n_struct_cols: int, n_bays: int, n_frames: int,
                              slope_deg: float, tan_slope: float,
                              rafter_slope_ft: float,
                              wall_panel_ht: float, peak_ht: float):
        """
        Append accessories and secondary structural members to the BOM items list.
        Handles: base plates, anchor bolts, X-bracing, eave struts, ridge cap,
        gutters, downspouts, walk doors, insulation, and trim package.
        """

        # ── 1. Base Plates (1 per column) ────────────────────────────────
        if getattr(bldg, 'include_base_plates', True):
            col_size = getattr(bldg, 'column_size', 'HSS 4x4')
            if '6x6' in col_size or '6X6' in col_size:
                bp_desc = "Base Plate 10\"x10\"x3/4\" — HSS 6x6 Column"
                bp_wt = 42.5   # ~10"x10"x0.75" A36 plate
            else:
                bp_desc = "Base Plate 8\"x8\"x3/4\" — HSS 4x4 Column"
                bp_wt = 27.2   # ~8"x8"x0.75" A36 plate

            n_bp = n_struct_cols
            for i in range(1, n_bp + 1):
                pass  # marks generated below as batch
            items.append(BOMLineItem(
                category="Accessories",
                item_id="base_plates",
                description=f"BP — {bp_desc} ({n_bp} pcs)",
                qty=n_bp, unit="EA",
                unit_weight_lbs=bp_wt,
                total_weight_lbs=round(n_bp * bp_wt, 1),
                unit_cost=0.0, total_cost=0.0,
                notes=(f"1 per column × {n_struct_cols} columns | "
                       f"Material: A36 Plate | {col_size} columns | "
                       f"4 anchor bolt holes per plate"),
                piece_count=n_bp,
            ))

            # ── 2. Anchor Bolts (4 per base plate) ──────────────────────────
            n_ab = 4 * n_bp
            ab_wt = 3.8  # typical 3/4"x18" F1554 anchor bolt + nut + washer
            items.append(BOMLineItem(
                category="Accessories",
                item_id="anchor_bolts",
                description=f"AB — 3/4\"x18\" F1554 Gr 36 Anchor Bolt Assembly ({n_ab} pcs)",
                qty=n_ab, unit="EA",
                unit_weight_lbs=ab_wt,
                total_weight_lbs=round(n_ab * ab_wt, 1),
                unit_cost=0.0, total_cost=0.0,
                notes=(f"4 per base plate × {n_bp} base plates = {n_ab} bolts | "
                       f"Material: F1554 Gr 36/55 | "
                       f"Each: bolt + hex nut + plate washer"),
                piece_count=n_ab,
            ))

        # ── 3. X-Bracing (rod bracing in end bays + every 4th bay) ───────
        if getattr(bldg, 'include_x_bracing', True) and n_bays >= 1:
            # Determine which bays get bracing: first bay, last bay, every 4th bay
            braced_bay_indices = set()
            braced_bay_indices.add(0)           # first bay
            braced_bay_indices.add(n_bays - 1)  # last bay
            for b_idx in range(0, n_bays, 4):
                braced_bay_indices.add(b_idx)
            n_braced_bays = len(braced_bay_indices)

            # 4 rods per braced bay (2 per sidewall face × 2 sidewalls)
            n_xb_rods = n_braced_bays * 4
            # Rod length = diagonal of bay rectangle (bay_width × eave_height)
            avg_bay_ft = bldg.length_ft / n_bays if n_bays > 0 else bldg.max_bay_ft
            xb_diag_ft = math.sqrt(avg_bay_ft**2 + bldg.clear_height_ft**2)
            # 5/8" round bar: ~1.04 lbs/ft
            xb_rod_wt_per_ft = 1.04
            xb_wt_each = xb_diag_ft * xb_rod_wt_per_ft
            xb_total_wt = n_xb_rods * xb_wt_each

            items.append(BOMLineItem(
                category="Secondary Structural",
                item_id="x_bracing",
                description=(f"XB — 5/8\" A36 Round Bar X-Bracing "
                             f"({n_xb_rods} rods, {xb_diag_ft:.1f}' ea)"),
                qty=n_xb_rods, unit="EA",
                unit_weight_lbs=round(xb_wt_each, 2),
                total_weight_lbs=round(xb_total_wt, 1),
                unit_cost=0.0, total_cost=0.0,
                notes=(f"{n_braced_bays} braced bays (end bays + every 4th) × "
                       f"4 rods/bay = {n_xb_rods} rods | "
                       f"Diagonal: sqrt({avg_bay_ft:.1f}'^2 + {bldg.clear_height_ft:.1f}'^2) "
                       f"= {xb_diag_ft:.1f}' | Material: A36 Round Bar 5/8\" dia"),
                piece_count=n_xb_rods,
                piece_length_in=round(xb_diag_ft * 12, 1),
            ))

        # ── 4. Eave Struts (2 per building — one each side) ─────────────
        if getattr(bldg, 'include_eave_struts', True):
            es_length_ft = bldg.length_ft
            es_wt_per_ft = 3.5  # Cee purlin at eave, ~3.5 lbs/ft
            n_eave_struts = 2
            es_wt_each = es_length_ft * es_wt_per_ft
            es_total_wt = n_eave_struts * es_wt_each

            items.append(BOMLineItem(
                category="Secondary Structural",
                item_id="eave_struts",
                description=(f"ES — Cee Purlin Eave Strut "
                             f"({n_eave_struts} pcs, {es_length_ft:.0f}' ea)"),
                qty=n_eave_struts, unit="EA",
                unit_weight_lbs=round(es_wt_each, 1),
                total_weight_lbs=round(es_total_wt, 1),
                unit_cost=0.0, total_cost=0.0,
                notes=(f"2 per building (one each eave side) × {es_length_ft:.0f}' = "
                       f"{n_eave_struts * es_length_ft:.0f} LFT | "
                       f"Material: Cee Purlin (eave) @ {es_wt_per_ft} lbs/ft"),
                piece_count=n_eave_struts,
                piece_length_in=round(es_length_ft * 12, 1),
            ))

        # ── 5. Ridge Cap (1 per building) ────────────────────────────────
        if getattr(bldg, 'include_ridge_cap', True):
            rc_length_ft = bldg.length_ft + 2.0  # +2' for overhang
            rc_wt_per_ft = 0.5
            rc_total_wt = rc_length_ft * rc_wt_per_ft

            items.append(BOMLineItem(
                category="Trim & Flashing",
                item_id="ridge_cap",
                description=f"RC-1 — 26ga Galvalume Ridge Cap ({rc_length_ft:.0f}')",
                qty=1, unit="EA",
                unit_weight_lbs=round(rc_total_wt, 2),
                total_weight_lbs=round(rc_total_wt, 1),
                unit_cost=0.0, total_cost=0.0,
                notes=(f"1 per building | Length = {bldg.length_ft:.0f}' + 2' overhang "
                       f"= {rc_length_ft:.0f}' | "
                       f"Material: 26ga Galvalume @ {rc_wt_per_ft} lbs/ft"),
                piece_count=1,
                piece_length_in=round(rc_length_ft * 12, 1),
            ))

        # ── 6. Gutters (2 per building, both eaves) ─────────────────────
        if getattr(bldg, 'include_gutters', True):
            gt_length_ft = bldg.length_ft
            gt_wt_per_ft = 1.2
            n_gutters = 2
            gt_wt_each = gt_length_ft * gt_wt_per_ft
            gt_total_wt = n_gutters * gt_wt_each

            items.append(BOMLineItem(
                category="Trim & Flashing",
                item_id="gutters",
                description=(f"GT — 26ga Galvalume Gutter "
                             f"({n_gutters} pcs, {gt_length_ft:.0f}' ea)"),
                qty=n_gutters, unit="EA",
                unit_weight_lbs=round(gt_wt_each, 1),
                total_weight_lbs=round(gt_total_wt, 1),
                unit_cost=0.0, total_cost=0.0,
                notes=(f"2 per building (both eaves) × {gt_length_ft:.0f}' = "
                       f"{n_gutters * gt_length_ft:.0f} LFT | "
                       f"Material: 26ga Galvalume @ {gt_wt_per_ft} lbs/ft"),
                piece_count=n_gutters,
                piece_length_in=round(gt_length_ft * 12, 1),
            ))

            # ── 7. Downspouts (1 per 40' of gutter, min 2 per side) ─────
            ds_per_side = max(2, math.ceil(gt_length_ft / 40.0))
            n_downspouts = ds_per_side * 2  # both sides
            ds_wt_each = 8.0  # 10' section, 3x4 rectangular
            ds_total_wt = n_downspouts * ds_wt_each

            items.append(BOMLineItem(
                category="Trim & Flashing",
                item_id="downspouts",
                description=(f"DS — 26ga Galvalume 3\"x4\" Downspout "
                             f"({n_downspouts} pcs, 10' sections)"),
                qty=n_downspouts, unit="EA",
                unit_weight_lbs=ds_wt_each,
                total_weight_lbs=round(ds_total_wt, 1),
                unit_cost=0.0, total_cost=0.0,
                notes=(f"{ds_per_side} per side (1 per 40' of gutter, min 2) × "
                       f"2 sides = {n_downspouts} pcs | "
                       f"Material: 26ga Galvalume 3\"x4\" rectangular | "
                       f"10' sections @ {ds_wt_each} lbs each"),
                piece_count=n_downspouts,
                piece_length_in=120.0,  # 10' = 120"
            ))

        # ── 8. Walk Doors (quantity from config or default 0) ────────────
        wd_qty = getattr(bldg, 'walk_door_qty', 0)
        if getattr(bldg, 'include_walk_doors', False) and wd_qty > 0:
            wd_wt_each = 85.0  # 3070 steel walk door w/ frame

            items.append(BOMLineItem(
                category="Doors & Windows",
                item_id="walk_doors",
                description=f"WD — 3070 Steel Walk Door w/ Frame ({wd_qty} pcs)",
                qty=wd_qty, unit="EA",
                unit_weight_lbs=wd_wt_each,
                total_weight_lbs=round(wd_qty * wd_wt_each, 1),
                unit_cost=0.0, total_cost=0.0,
                notes=(f"{wd_qty} walk door(s) | "
                       f"3'-0\" × 7'-0\" steel door with steel frame | "
                       f"Includes hinges, lockset, closer, threshold | "
                       f"@ {wd_wt_each} lbs each"),
                piece_count=wd_qty,
            ))

        # ── 9. Insulation (if enabled) ───────────────────────────────────
        if getattr(bldg, 'include_insulation', False):
            r_value = getattr(bldg, 'insulation_r_value', 'R-13')
            # Weight per sqft varies by R-value
            insulation_weights = {
                "R-13": 0.06, "R-19": 0.08, "R-25": 0.10, "R-30": 0.12,
            }
            ins_wt_per_sqft = insulation_weights.get(r_value, 0.06)

            # Roof insulation: slope area (both sides)
            half_width = bldg.width_ft / 2.0
            slope_len = math.sqrt(half_width**2 + (half_width * tan_slope)**2)
            roof_area_sqft = 2.0 * slope_len * bldg.length_ft
            roof_ins_wt = roof_area_sqft * ins_wt_per_sqft

            items.append(BOMLineItem(
                category="Insulation",
                item_id="insulation_roof",
                description=(f"INS-R — {r_value} Faced Fiberglass Insulation (Roof) "
                             f"({roof_area_sqft:.0f} sqft)"),
                qty=round(roof_area_sqft, 0), unit="SQFT",
                unit_weight_lbs=ins_wt_per_sqft,
                total_weight_lbs=round(roof_ins_wt, 1),
                unit_cost=0.0, total_cost=0.0,
                notes=(f"Roof area: 2 × {slope_len:.1f}' slope × {bldg.length_ft:.0f}' length "
                       f"= {roof_area_sqft:.0f} sqft | "
                       f"Material: {r_value} Faced Fiberglass @ {ins_wt_per_sqft} lbs/sqft"),
                piece_count=1,
            ))

            # Wall insulation: total wall area for enclosed walls only
            wall_area_sqft = 0.0
            wall_note_parts = []
            if bldg.include_back_wall:
                area = bldg.length_ft * wall_panel_ht
                wall_area_sqft += area
                wall_note_parts.append(f"Back wall: {area:.0f} sqft")
            if bldg.include_end_walls:
                area = bldg.width_ft * peak_ht * 2  # both end walls
                wall_area_sqft += area
                wall_note_parts.append(f"End walls (×2): {area:.0f} sqft")
            if bldg.include_side_walls:
                area = bldg.length_ft * wall_panel_ht * 2  # both side walls
                wall_area_sqft += area
                wall_note_parts.append(f"Side walls (×2): {area:.0f} sqft")

            if wall_area_sqft > 0:
                wall_ins_wt = wall_area_sqft * ins_wt_per_sqft
                items.append(BOMLineItem(
                    category="Insulation",
                    item_id="insulation_walls",
                    description=(f"INS-W — {r_value} Faced Fiberglass Insulation (Walls) "
                                 f"({wall_area_sqft:.0f} sqft)"),
                    qty=round(wall_area_sqft, 0), unit="SQFT",
                    unit_weight_lbs=ins_wt_per_sqft,
                    total_weight_lbs=round(wall_ins_wt, 1),
                    unit_cost=0.0, total_cost=0.0,
                    notes=(f"{' | '.join(wall_note_parts)} | "
                           f"Total: {wall_area_sqft:.0f} sqft | "
                           f"Material: {r_value} Faced Fiberglass @ {ins_wt_per_sqft} lbs/sqft"),
                    piece_count=1,
                ))

        # ── 10. Trim Package (1 per building) ────────────────────────────
        if getattr(bldg, 'include_trim_package', True):
            trim_wt_per_ft = 0.8
            # Base trim: full perimeter
            perimeter_ft = 2.0 * (bldg.length_ft + bldg.width_ft)
            # Eave trim: both long sides
            eave_trim_ft = 2.0 * bldg.length_ft
            # Rake trim: both gable ends (slope length × 2 sides × 2 ends)
            half_width = bldg.width_ft / 2.0
            rake_slope_ft = math.sqrt(half_width**2 + (half_width * tan_slope)**2)
            rake_trim_ft = 4.0 * rake_slope_ft  # 2 slopes × 2 ends
            # Corner trim: 4 corners × eave height
            corner_trim_ft = 4.0 * bldg.clear_height_ft

            total_trim_ft = perimeter_ft + eave_trim_ft + rake_trim_ft + corner_trim_ft
            trim_total_wt = total_trim_ft * trim_wt_per_ft

            items.append(BOMLineItem(
                category="Trim & Flashing",
                item_id="trim_package",
                description=(f"TRIM-PKG — 26ga Galvalume Trim Package "
                             f"({total_trim_ft:.0f} LFT)"),
                qty=1, unit="EA",
                unit_weight_lbs=round(trim_total_wt, 1),
                total_weight_lbs=round(trim_total_wt, 1),
                unit_cost=0.0, total_cost=0.0,
                notes=(f"Base: {perimeter_ft:.0f}' (perimeter) | "
                       f"Eave: {eave_trim_ft:.0f}' (both sides) | "
                       f"Rake: {rake_trim_ft:.0f}' (4 gable slopes) | "
                       f"Corner: {corner_trim_ft:.0f}' (4 corners) | "
                       f"Total: {total_trim_ft:.0f} LFT @ {trim_wt_per_ft} lbs/ft | "
                       f"Material: 26ga Galvalume"),
                piece_count=1,
                piece_length_in=round(total_trim_ft * 12, 1),
            ))

    def calculate_building(self, bldg: BuildingConfig) -> BuildingBOM:
        result = BuildingBOM(building=bldg)
        items = []
        cp = bldg.coil_prices

        # ── Auto-determine frame type from width (rafter-first design) ──
        # ≤45' = TEE (1 column per rafter in auto mode)
        # >45' = multi-column (auto places 2+ columns per rafter)
        frame_type = "tee" if bldg.width_ft <= 45.0 else "2post"

        # Slope
        slope_deg = get_slope_deg(bldg.pitch_key)
        tan_slope = math.tan(math.radians(slope_deg))

        # ── Rafter column placement (structural columns per rafter) ──
        # Must be calculated before n_struct_cols since it determines cols/rafter
        raft_n_cols, raft_col_pos_in = calc_rafter_columns(
            bldg.width_ft,
            column_mode=bldg.column_mode,
            column_spacing_ft=bldg.column_spacing_ft,
            column_count_manual=bldg.column_count_manual,
            column_positions_manual=bldg.column_positions_manual,
            include_back_wall=bldg.include_back_wall,
            front_col_position_ft=bldg.front_col_position_ft,
        )

        # Rafter layout along building length (frames / bays)
        col_positions = None
        bay_sizes_list = None
        if bldg.space_width_ft and bldg.space_width_ft > 0:
            n_frames, col_positions, bay_sizes_list, overhang_ft, space_warn = \
                calc_space_based_columns(
                    bldg.length_ft, bldg.space_width_ft,
                    bldg.max_bay_ft, bldg.overhang_mode)
            bay_size_ft = max(bay_sizes_list) if bay_sizes_list else bldg.max_bay_ft
            if space_warn:
                result.errors.append(space_warn)
        else:
            n_frames, bay_size_ft, overhang_ft = calc_column_count(
                bldg.length_ft, bldg.max_bay_ft)
            bay_sizes_list = [bay_size_ft] * (n_frames - 1)

        n_bays = n_frames - 1
        # Structural columns = frames × columns per rafter (from rafter drawing)
        n_struct_cols = n_frames * raft_n_cols

        # Rafter: 1 per frame, full width
        n_rafters = n_frames
        rafter_slope_ft = calc_rafter_slope_length(bldg.width_ft, slope_deg)

        # ── Per-position column heights (variable due to slope) ──
        # Each column position on the rafter has a different height based on
        # its distance from the eave (closer to peak = taller column)
        raft_col_heights_ft = [
            calc_column_height_at(
                bldg.clear_height_ft, p / 12.0, slope_deg,
                bldg.embedment_ft, bldg.column_buffer_ft)
            for p in raft_col_pos_in
        ]
        # For BOM coil calculation, use average column height across positions
        # (each frame has the same set of column heights)
        avg_col_ht_ft = sum(raft_col_heights_ft) / len(raft_col_heights_ft) if raft_col_heights_ft else 0
        col_ht_ft = avg_col_ht_ft
        col_ht_in = col_ht_ft * 12.0
        # Angle addition for display (use max column position from eave)
        max_dist_from_eave = max(p / 12.0 for p in raft_col_pos_in) if raft_col_pos_in else bldg.width_ft / 2.0
        angle_add_in = max_dist_from_eave * tan_slope * 12

        # Purlin spacing
        if bldg.purlin_spacing_override:
            purlin_spacing = bldg.purlin_spacing_override
            purlin_auto = False
        else:
            purlin_spacing = get_purlin_spacing(bldg.width_ft)
            purlin_auto = True
        n_purlin_lines = calc_purlin_lines(bldg.width_ft, purlin_spacing)
        n_interior_lines = max(0, n_purlin_lines - 2)

        # Panel split
        panel_front_ft, panel_back_ft, split_pos_ft = calc_panel_split(
            bldg.width_ft, purlin_spacing)
        panel_coverage_ft = COILS["spartan_rib_48"]["panel_coverage_ft"]
        n_panel_runs = math.ceil(bldg.length_ft / panel_coverage_ft)
        n_panel_pieces = n_panel_runs * 2
        total_panel_net = n_panel_runs * (panel_front_ft + panel_back_ft)

        # Sag rods: 2 rods/rafter x 2 pieces/rod = 4 pieces/rafter
        overlap_ft = DEFAULTS["sag_rod_overlap_in"] / 12.0
        sag_front_ft = split_pos_ft + overlap_ft
        sag_back_ft = bldg.width_ft - split_pos_ft
        n_sag_pieces = n_rafters * 4   # 2 rods x 2 pieces
        total_sag_net = n_rafters * 2 * (sag_front_ft + sag_back_ft)

        # Rebar selection (uses auto-determined frame type)
        auto_rebar = get_rebar_size(frame_type, bldg.width_ft,
                                     self.project.wind_speed_mph, bay_size_ft)
        rebar_col_key = (bldg.rebar_col_size
                         if bldg.rebar_col_size and bldg.rebar_col_size != "auto"
                         else auto_rebar.get("column"))
        rebar_beam_key = (bldg.rebar_beam_size
                          if bldg.rebar_beam_size and bldg.rebar_beam_size != "auto"
                          else auto_rebar.get("beam"))

        # Footing depth: always per-building (default 10' set in BuildingConfig)
        footing_depth = bldg.footing_depth_ft

        # Save geometry for display
        result.geometry = {
            "n_frames": n_frames,
            "n_bays": n_bays,
            "bay_size_ft": round(bay_size_ft, 2),
            "bay_sizes_list": [round(b, 2) for b in bay_sizes_list] if bay_sizes_list else [],
            "col_positions": [round(p, 2) for p in col_positions] if col_positions else [],
            "overhang_ft": round(overhang_ft, 2),
            "overhang_mode": bldg.overhang_mode,
            "space_width_ft": bldg.space_width_ft,
            "n_struct_cols": n_struct_cols,
            "n_rafters": n_rafters,
            "rafter_slope_ft": round(rafter_slope_ft, 2),
            "col_ht_ft": round(col_ht_ft, 2),  # average across positions
            "col_ht_in": round(col_ht_in, 1),
            "angle_add_in": round(angle_add_in, 2),
            "slope_deg": round(slope_deg, 2),
            "purlin_spacing_ft": purlin_spacing,
            "purlin_auto": purlin_auto,
            "n_purlin_lines": n_purlin_lines,
            "n_interior_lines": n_interior_lines,
            "panel_front_ft": round(panel_front_ft, 2),
            "panel_back_ft": round(panel_back_ft, 2),
            "split_pos_ft": round(split_pos_ft, 2),
            "n_panel_runs": n_panel_runs,
            "n_panel_pieces": n_panel_pieces,
            "sag_front_in": round(sag_front_ft * 12, 1),
            "sag_back_in": round(sag_back_ft * 12, 1),
            "rebar_col": rebar_col_key,
            "rebar_beam": rebar_beam_key,
            # Passed to Titan Carports Construction Calc
            "concrete_cy": 0.0,          # filled in after concrete calc below
            "concrete_n_piers": 0,       # filled after concrete calc
            "footing_depth_ft": round(footing_depth, 2),
            # Rafter column placement
            "raft_n_cols": raft_n_cols,
            "raft_col_positions_in": [round(p, 2) for p in raft_col_pos_in],
            "column_mode": bldg.column_mode,
            "angled_purlins": bldg.angled_purlins,
            "purlin_angle_deg": bldg.purlin_angle_deg,
            # Per-position column heights (for variable height due to slope)
            "raft_col_heights_ft": [round(h, 2) for h in raft_col_heights_ft],
            # Drawing-related fields
            "purlin_type": bldg.purlin_type,
            "roofing_overhang_ft": bldg.roofing_overhang_ft,
            "above_grade_ft": bldg.above_grade_ft,
            "cut_allowance_in": bldg.cut_allowance_in,
            "width_ft": bldg.width_ft,
            "clear_height_ft": bldg.clear_height_ft,
            "embedment_ft": bldg.embedment_ft,
            "frame_type": frame_type,  # auto-determined from width
            "reinforced": bldg.reinforced,
            "rebar_rafter_size": bldg.rebar_rafter_size,
            "rebar_max_stick_ft": bldg.rebar_max_stick_ft,
            "rebar_end_gap_ft": bldg.rebar_end_gap_ft,
            "splice_location_ft": bldg.splice_location_ft,
        }

        wf = WASTE_FACTORS["10GA"]
        # ── COIL 1: Columns ──────────────────────────────────────────────
        # With rafter-first design, columns have variable heights per position.
        # Total coil = sum of all per-position heights × n_frames × 2 C-sections
        coil = COILS["c_section_23"]
        ppb = coil_price("c_section_23", cp)
        # Sum of column heights per rafter × number of rafter frames × 2 C-sections
        col_lft_per_frame = sum(raft_col_heights_ft)
        col_net = n_frames * col_lft_per_frame * 2
        col_raw = col_net * (1 + wf)
        col_wt = col_raw * coil["lbs_per_lft"]
        col_cost_v = col_wt * ppb
        ht_summary = "/".join(f"{h:.1f}'" for h in raft_col_heights_ft)
        items.append(BOMLineItem(
            category="Structural Steel - Coil 1",
            item_id="c_section_columns",
            description=(f"23\" 10GA C-Section — Columns "
                         f"({n_struct_cols} pcs, avg {col_ht_ft:.2f}' ea)"),
            qty=round(col_raw, 2), unit="LFT (coil)",
            unit_weight_lbs=coil["lbs_per_lft"],
            total_weight_lbs=round(col_wt, 1),
            unit_cost=ppb, total_cost=round(col_cost_v, 2),
            waste_factor=wf,
            notes=(f"{n_frames} frames × {raft_n_cols} cols/frame = {n_struct_cols} cols | "
                   f"Heights: {ht_summary} | "
                   f"{bldg.clear_height_ft}'clr + slope + "
                   f"{bldg.embedment_ft*12:.0f}\"emb + {bldg.column_buffer_ft*12:.0f}\"buf"
                   f" × 2 C-sections"),
            piece_count=n_struct_cols,
            piece_length_in=round(col_ht_in, 1),
        ))

        # ── COIL 1: Rafters ──────────────────────────────────────────────
        raft_net = n_rafters * rafter_slope_ft * 2
        raft_raw = raft_net * (1 + wf)
        raft_wt = raft_raw * coil["lbs_per_lft"]
        raft_cost_v = raft_wt * ppb
        items.append(BOMLineItem(
            category="Structural Steel - Coil 1",
            item_id="c_section_rafters",
            description=(f"23\" 10GA C-Section — Rafters "
                         f"({n_rafters} pcs, {rafter_slope_ft:.2f}' ea)"),
            qty=round(raft_raw, 2), unit="LFT (coil)",
            unit_weight_lbs=coil["lbs_per_lft"],
            total_weight_lbs=round(raft_wt, 1),
            unit_cost=ppb, total_cost=round(raft_cost_v, 2),
            waste_factor=wf,
            notes=(f"{n_rafters} rafters x {rafter_slope_ft:.2f}' "
                   f"(full {bldg.width_ft}' width along slope) x 2 C-sections"),
            piece_count=n_rafters,
            piece_length_in=round(rafter_slope_ft * 12, 1),
        ))

        # ── COIL 2: Z-Purlins ────────────────────────────────────────────
        coil = COILS["z_purlin_20"]
        wf2 = WASTE_FACTORS["12GA"]
        ppb = coil_price("z_purlin_20", cp)
        purlin_net = n_purlin_lines * bldg.length_ft
        purlin_raw = purlin_net * (1 + wf2)
        purlin_wt = purlin_raw * coil["lbs_per_lft"]
        purlin_cost_v = purlin_wt * ppb
        items.append(BOMLineItem(
            category="Structural Steel - Coil 2",
            item_id="z_purlin",
            description=(f"20.125\" 12GA Z-Purlin "
                         f"({n_purlin_lines} lines x {bldg.length_ft:.0f}', {purlin_spacing}' OC)"),
            qty=round(purlin_raw, 2), unit="LFT (coil)",
            unit_weight_lbs=coil["lbs_per_lft"],
            total_weight_lbs=round(purlin_wt, 1),
            unit_cost=ppb, total_cost=round(purlin_cost_v, 2),
            waste_factor=wf2,
            notes=(f"{n_purlin_lines} lines x {bldg.length_ft:.0f}' = "
                   f"{purlin_net:.0f} LFT net | "
                   f"{'Auto' if purlin_auto else 'Manual'} {purlin_spacing}' OC "
                   f"across {bldg.width_ft}' width"),
            piece_count=n_purlin_lines * n_bays,
            piece_length_in=round(bay_size_ft * 12, 1),
        ))

        # ── COIL 3: Sag Rods ─────────────────────────────────────────────
        coil = COILS["angle_4_16ga"]
        wf3 = WASTE_FACTORS["16GA"]
        ppb = coil_price("angle_4_16ga", cp)
        sag_raw = total_sag_net * (1 + wf3)
        sag_wt = sag_raw * coil["lbs_per_lft"]
        sag_cost_v = sag_wt * ppb
        items.append(BOMLineItem(
            category="Structural Steel - Coil 3",
            item_id="sag_rods",
            description=(f"4\" 16GA Angle — Sag Rods 2\"x2\" "
                         f"({n_sag_pieces} pcs: "
                         f"{n_sag_pieces//2} x {sag_front_ft*12:.1f}\" + "
                         f"{n_sag_pieces//2} x {sag_back_ft*12:.1f}\")"),
            qty=round(sag_raw, 2), unit="LFT (coil)",
            unit_weight_lbs=coil["lbs_per_lft"],
            total_weight_lbs=round(sag_wt, 1),
            unit_cost=ppb, total_cost=round(sag_cost_v, 2),
            waste_factor=wf3,
            notes=(f"{n_rafters} rafters x 2 rods x 2 pcs = {n_sag_pieces} pcs | "
                   f"Split @ {split_pos_ft:.1f}' purlin + 3\" overlap"),
            piece_count=n_sag_pieces,
            piece_length_in=round(sag_front_ft * 12, 1),
        ))

        # ── COIL 4: Spartan Rib Panels ───────────────────────────────────
        coil = COILS["spartan_rib_48"]
        wf4 = WASTE_FACTORS["29GA"]
        ppb = coil_price("spartan_rib_48", cp)
        panel_raw = total_panel_net * (1 + wf4)
        panel_wt = panel_raw * coil["lbs_per_lft"]
        panel_cost_v = panel_wt * ppb
        items.append(BOMLineItem(
            category="Roof Panels - Coil 4",
            item_id="spartan_rib",
            description=(f"48\" 29GA Spartan Rib Panel "
                         f"({n_panel_pieces} pcs: "
                         f"{n_panel_runs} x {panel_front_ft*12:.1f}\" + "
                         f"{n_panel_runs} x {panel_back_ft*12:.1f}\")"),
            qty=round(panel_raw, 2), unit="LFT (coil)",
            unit_weight_lbs=coil["lbs_per_lft"],
            total_weight_lbs=round(panel_wt, 1),
            unit_cost=ppb, total_cost=round(panel_cost_v, 2),
            waste_factor=wf4,
            notes=(f"{bldg.length_ft*12:.0f}\" / {coil['panel_coverage_in']}\" = "
                   f"{n_panel_runs} runs | "
                   f"Split @ {split_pos_ft:.1f}' purlin: "
                   f"{panel_front_ft*12:.1f}\" + {panel_back_ft*12:.1f}\" | "
                   f"Net: {total_panel_net:.0f} LFT"),
            piece_count=n_panel_pieces,
            piece_length_in=round(panel_front_ft * 12, 1),
        ))

        # ── COIL 5: Interior Purlin Plates ───────────────────────────────
        coil = COILS["plate_6_10ga"]
        ppb = coil_price("plate_6_10ga", cp)
        n_int_plates = n_frames * n_interior_lines
        int_plate_raw = n_int_plates * coil["plate_length_ft"] * (1 + wf)
        int_plate_wt = int_plate_raw * coil["lbs_per_lft"]
        int_plate_cost_v = int_plate_wt * ppb
        items.append(BOMLineItem(
            category="Connection Hardware - Coil 5",
            item_id="interior_plates",
            description=(f"6\" 10GA — Interior Purlin Plates 10\"x6\" "
                         f"({n_int_plates} pcs, 8 holes each)"),
            qty=round(int_plate_raw, 2), unit="LFT (coil)",
            unit_weight_lbs=coil["lbs_per_lft"],
            total_weight_lbs=round(int_plate_wt, 1),
            unit_cost=ppb, total_cost=round(int_plate_cost_v, 2),
            waste_factor=wf,
            notes=(f"{n_frames} frames x {n_interior_lines} interior lines "
                   f"({n_purlin_lines} total - 2 eave) = {n_int_plates} plates"),
            piece_count=n_int_plates, piece_length_in=10.0,
        ))

        # ── COIL 6: Exterior/Eave Purlin Plates ──────────────────────────
        coil = COILS["plate_9_10ga"]
        ppb = coil_price("plate_9_10ga", cp)
        n_ext_plates = n_frames * 2
        ext_plate_raw = n_ext_plates * coil["plate_length_ft"] * (1 + wf)
        ext_plate_wt = ext_plate_raw * coil["lbs_per_lft"]
        ext_plate_cost_v = ext_plate_wt * ppb
        items.append(BOMLineItem(
            category="Connection Hardware - Coil 6",
            item_id="exterior_plates",
            description=(f"9\" 10GA — Exterior Purlin Plates 24\"x9\" "
                         f"({n_ext_plates} pcs, 8 holes each)"),
            qty=round(ext_plate_raw, 2), unit="LFT (coil)",
            unit_weight_lbs=coil["lbs_per_lft"],
            total_weight_lbs=round(ext_plate_wt, 1),
            unit_cost=ppb, total_cost=round(ext_plate_cost_v, 2),
            waste_factor=wf,
            notes=f"{n_frames} frames x 2 eave purlins = {n_ext_plates} plates",
            piece_count=n_ext_plates, piece_length_in=24.0,
        ))

        # ── COIL 7: Rafter-to-Purlin Straps ──────────────────────────────
        # 4 per rafter: 1 purlin in from each eave = 2 positions × 2 straps per position
        coil = COILS["strap_15_10ga"]
        ppb = coil_price("strap_15_10ga", cp)
        n_straps = n_rafters * bldg.straps_per_rafter
        strap_raw = (n_straps * bldg.strap_length_in / 12) * (1 + wf)
        strap_wt = strap_raw * coil["lbs_per_lft"]
        strap_cost_v = strap_wt * ppb
        items.append(BOMLineItem(
            category="Connection Hardware - Coil 7",
            item_id="straps_braces",
            description=(f"1.5\" 10GA — Rafter-to-Purlin Straps "
                         f"({n_straps} pcs, {bldg.strap_length_in:.0f}\" ea)"),
            qty=round(strap_raw, 2), unit="LFT (coil)",
            unit_weight_lbs=coil["lbs_per_lft"],
            total_weight_lbs=round(strap_wt, 1),
            unit_cost=ppb, total_cost=round(strap_cost_v, 2),
            waste_factor=wf,
            notes=(f"{n_rafters} rafters × {bldg.straps_per_rafter} straps/rafter "
                   f"(1 purlin in from each eave × 2 per position) = {n_straps} pcs | "
                   f"{bldg.strap_length_in:.0f}\" each"),
            piece_count=n_straps,
            piece_length_in=bldg.strap_length_in,
        ))

        # ── Splice Plates (Coil 1) — triggered when rafter > 53' ─────────
        if rafter_slope_ft > 53.0:
            splice_plate_ft = 118.0 / 12.0   # 9'10" = 118"
            n_splice_plates = n_rafters * 2   # 2 per rafter (one each side of web)
            splice_net = n_splice_plates * splice_plate_ft
            splice_raw = splice_net * (1 + wf)
            splice_coil = COILS["c_section_23"]
            splice_ppb = coil_price("c_section_23", cp)
            splice_wt = splice_raw * splice_coil["lbs_per_lft"]
            splice_cost_v = splice_wt * splice_ppb
            items.append(BOMLineItem(
                category="Structural Steel - Coil 1",
                item_id="splice_plates",
                description=(f"23\" 10GA — Splice Plates "
                             f"({n_splice_plates} pcs, 118\" = 9'10\" ea)"),
                qty=round(splice_raw, 2), unit="LFT (coil)",
                unit_weight_lbs=splice_coil["lbs_per_lft"],
                total_weight_lbs=round(splice_wt, 1),
                unit_cost=splice_ppb, total_cost=round(splice_cost_v, 2),
                waste_factor=wf,
                notes=(f"Rafter slope {rafter_slope_ft:.1f}' > 53' triggers splice | "
                       f"{n_rafters} rafters × 2 plates (one each side of web) = {n_splice_plates} pcs | "
                       f"Position: nearest purlin ≤10' from column end, between two purlins"),
                piece_count=n_splice_plates,
                piece_length_in=118.0,
            ))

        # ── Cap Plates ───────────────────────────────────────────────────
        cap = PURCHASED_ITEMS["cap_plate"]
        n_cap = n_struct_cols * cap["qty_per_column"]
        cap_cost_v = n_cap * cap["price_each"]
        items.append(BOMLineItem(
            category="Purchased Items", item_id="cap_plates",
            description=f"3/4\"x26\"x14\" Cap Plates ({n_cap} pcs)",
            qty=n_cap, unit="EA",
            unit_cost=cap["price_each"], total_cost=cap_cost_v,
            notes=f"{n_struct_cols} columns x 2 per column",
        ))

        # ── Gusset Triangles ─────────────────────────────────────────────
        gusset = PURCHASED_ITEMS["gusset_triangle"]
        n_gussets = n_struct_cols * gusset["qty_per_column"]
        gusset_cost_v = n_gussets * gusset["price_each"]
        slope_key = min(gusset["sizes_by_slope"].keys(), key=lambda k: abs(k - slope_deg))
        gusset_sizes = gusset["sizes_by_slope"][slope_key]
        gusset_size_str = ", ".join([f"{s[1]} pcs @ hyp={s[0]}'" for s in gusset_sizes])
        items.append(BOMLineItem(
            category="Purchased Items", item_id="gusset_triangles",
            description=f"6\"x6\"x3/8\" Gusset Triangles ({n_gussets} pcs)",
            qty=n_gussets, unit="EA",
            unit_cost=gusset["price_each"], total_cost=gusset_cost_v,
            notes=f"{n_struct_cols} cols x 4 per col | {gusset_size_str}",
        ))

        # ── Bolt Assemblies (column-to-rafter connections) ─────────────
        bolt = BOLT_ASSEMBLIES["connection_bolt"]
        # Each column has 1 connection point (top); bolt_qty per connection = 4
        n_connections = n_struct_cols
        bolts_per_conn = bolt["qty_per_connection"]
        n_bolts = n_connections * bolts_per_conn
        bolt_boxes = math.ceil(n_bolts / bolt["box_qty"])
        bolt_cost_v = bolt_boxes * bolt["price_per_box"]
        items.append(BOMLineItem(
            category="Connection Hardware",
            item_id="bolt_assemblies",
            description=(f"3/4\" A325 Bolt Assembly (bolt+nut+washers) "
                         f"({n_bolts} pcs / {bolt_boxes} boxes of {bolt['box_qty']})"),
            qty=bolt_boxes, unit="BOX",
            unit_cost=bolt["price_per_box"],
            total_cost=round(bolt_cost_v, 2),
            notes=(f"{n_connections} column connections × {bolts_per_conn} bolts/connection "
                   f"= {n_bolts} assemblies | "
                   f"Each: 3/4\"×4-1/2\" A325 + nut + flat washer + lock washer"),
            piece_count=n_bolts,
        ))

        # ── Endcap U-Channels (purlin endcaps at building ends) ──────
        endcap = ENDCAP_U_CHANNELS
        # Building length determines endcap length; 2 endcaps per building
        endcap_length_in = bldg.length_ft * 12.0
        endcap_max_in = endcap["max_single_piece_in"]  # 30'4" = 364"
        if endcap_length_in <= endcap_max_in:
            n_endcap_pieces = 2  # 1 piece per end
            endcap_piece_len_in = endcap_length_in
            endcap_split_note = "Single piece per end"
        else:
            # Must split — land on purlin center
            pieces_per_end = math.ceil(endcap_length_in / endcap_max_in)
            n_endcap_pieces = pieces_per_end * 2  # both ends
            endcap_piece_len_in = endcap_length_in / pieces_per_end
            endcap_split_note = (f"Split: {pieces_per_end} pieces per end "
                                 f"({endcap_piece_len_in/12:.1f}' each, must land on purlin)")

        endcap_total_lft = (n_endcap_pieces * endcap_piece_len_in) / 12.0
        # Uses z_purlin_20 coil
        endcap_coil = COILS[endcap["coil_id"]]
        endcap_ppb = coil_price(endcap["coil_id"], cp)
        endcap_raw = endcap_total_lft * (1 + wf2)
        endcap_wt = endcap_raw * endcap_coil["lbs_per_lft"]
        endcap_cost_v = endcap_wt * endcap_ppb
        items.append(BOMLineItem(
            category="Structural Steel - Coil 2",
            item_id="endcap_u_channels",
            description=(f"20.125\" 12GA — Endcap U-Channel 12\"×4\" "
                         f"({n_endcap_pieces} pcs, {endcap_piece_len_in/12:.1f}' ea)"),
            qty=round(endcap_raw, 2), unit="LFT (coil)",
            unit_weight_lbs=endcap_coil["lbs_per_lft"],
            total_weight_lbs=round(endcap_wt, 1),
            unit_cost=endcap_ppb,
            total_cost=round(endcap_cost_v, 2),
            waste_factor=wf2,
            notes=(f"2 building ends × {endcap['qty_per_building_end']} per end | "
                   f"{endcap_split_note} | "
                   f"No lip, roll formed on C1 from Z-purlin coil | "
                   f"Ships nested alternating (U-up/N-down)"),
            piece_count=n_endcap_pieces,
            piece_length_in=round(endcap_piece_len_in, 1),
        ))

        # ── Rebar ────────────────────────────────────────────────────────
        stick_ft = REBAR["stick_length_ft"]
        rebar_ppb = REBAR["price_per_lb"]
        rebar_wf = WASTE_FACTORS["rebar"]

        if rebar_col_key and rebar_col_key in REBAR["sizes"]:
            rb = REBAR["sizes"][rebar_col_key]
            col_rebar_len = (footing_depth + 8.0 if bldg.reinforced
                             else footing_depth - bldg.embedment_ft)
            sticks_per_col = math.ceil(col_rebar_len / stick_ft)
            # 4 sticks per column — one per corner of the C-section box (reinforced or not)
            n_col_sticks = n_struct_cols * sticks_per_col * 4
            col_rebar_lbs = n_col_sticks * stick_ft * rb["lbs_per_lft"] * (1 + rebar_wf)
            col_rebar_cost = col_rebar_lbs * rebar_ppb
            items.append(BOMLineItem(
                category="Rebar",
                item_id=f"rebar_col_{rebar_col_key.replace('#','')}",
                description=(f"A706 {rebar_col_key} Column Rebar, 40' Sticks "
                             f"({n_col_sticks} sticks)"),
                qty=n_col_sticks, unit="EA (sticks)",
                unit_weight_lbs=stick_ft * rb["lbs_per_lft"],
                total_weight_lbs=round(col_rebar_lbs, 1),
                unit_cost=stick_ft * rb["lbs_per_lft"] * rebar_ppb,
                total_cost=round(col_rebar_cost, 2),
                waste_factor=rebar_wf,
                notes=(f"{rebar_col_key} @ {rb['lbs_per_lft']} LBS/LFT | "
                       f"{n_struct_cols} cols × 4 corners × {sticks_per_col} stick(s)/corner = {n_col_sticks} sticks | "
                       f"{'Reinforced: depth+8ft' if bldg.reinforced else 'Standard: depth-embed'}"),
            ))

        if rebar_beam_key and rebar_beam_key in REBAR["sizes"]:
            rb = REBAR["sizes"][rebar_beam_key]
            sticks_per_raft = math.ceil(rafter_slope_ft / stick_ft)
            n_beam_sticks = n_rafters * sticks_per_raft
            beam_rebar_lbs = n_beam_sticks * stick_ft * rb["lbs_per_lft"] * (1 + rebar_wf)
            beam_rebar_cost = beam_rebar_lbs * rebar_ppb
            items.append(BOMLineItem(
                category="Rebar",
                item_id=f"rebar_beam_{rebar_beam_key.replace('#','')}",
                description=(f"A706 {rebar_beam_key} Beam Rebar, 40' Sticks "
                             f"({n_beam_sticks} sticks)"),
                qty=n_beam_sticks, unit="EA (sticks)",
                unit_weight_lbs=stick_ft * rb["lbs_per_lft"],
                total_weight_lbs=round(beam_rebar_lbs, 1),
                unit_cost=stick_ft * rb["lbs_per_lft"] * rebar_ppb,
                total_cost=round(beam_rebar_cost, 2),
                waste_factor=rebar_wf,
                notes=(f"{rebar_beam_key} @ {rb['lbs_per_lft']} LBS/LFT | "
                       f"{n_rafters} rafters x {sticks_per_raft} stick(s)"),
            ))

        # ── Concrete (quantity stored in geometry for Titan Carports calc) ──
        # Concrete is NOT a fabrication item — it is a site/construction cost
        # handled by the Titan Carports Construction Quote Calculator.
        r_ft = (24 / 2.0) / 12.0
        vol_cy = math.pi * r_ft**2 * footing_depth / 27.0
        concrete_net = n_struct_cols * vol_cy
        concrete_wf = WASTE_FACTORS["concrete"]
        concrete_total_cy = round(concrete_net * (1 + concrete_wf), 2)
        # (not appended to items — saved in geometry below for TC import)
        result.geometry["concrete_cy"] = concrete_total_cy
        result.geometry["concrete_n_piers"] = n_struct_cols

        # ── Rafter Rebar (optional toggle) ───────────────────────────────
        if bldg.include_rafter_rebar:
            rebar_rafter_key = (bldg.rebar_rafter_size
                                if bldg.rebar_rafter_size and bldg.rebar_rafter_size != "auto"
                                else "#9")
            if rebar_rafter_key in REBAR["sizes"]:
                rb = REBAR["sizes"][rebar_rafter_key]
                # New configurable stick layout:
                #   available = rafter_slope_ft - 2 * end_gap
                #   sticks = ceil(available / max_stick_length)
                #   actual_stick = available / sticks
                max_stick = bldg.rebar_max_stick_ft   # default 20'
                end_gap = bldg.rebar_end_gap_ft       # default 5'
                available_ft = max(1.0, rafter_slope_ft - 2.0 * end_gap)
                sticks_per_side = max(1, math.ceil(available_ft / max_stick))
                actual_stick_ft = available_ft / sticks_per_side
                sticks_per_rafter = 4 * sticks_per_side   # 4 corners
                n_rafter_rebar_sticks = n_rafters * sticks_per_rafter
                rafter_rebar_lbs = (n_rafter_rebar_sticks * actual_stick_ft
                                    * rb["lbs_per_lft"] * (1 + rebar_wf))
                rafter_rebar_cost = rafter_rebar_lbs * rebar_ppb
                items.append(BOMLineItem(
                    category="Rebar",
                    item_id=f"rebar_rafter_{rebar_rafter_key.replace('#','')}",
                    description=(f"A706 {rebar_rafter_key} Rafter Rebar, "
                                 f"{actual_stick_ft:.1f}' Sticks "
                                 f"({n_rafter_rebar_sticks} sticks)"),
                    qty=n_rafter_rebar_sticks, unit="EA (sticks)",
                    unit_weight_lbs=actual_stick_ft * rb["lbs_per_lft"],
                    total_weight_lbs=round(rafter_rebar_lbs, 1),
                    unit_cost=actual_stick_ft * rb["lbs_per_lft"] * rebar_ppb,
                    total_cost=round(rafter_rebar_cost, 2),
                    waste_factor=rebar_wf,
                    notes=(f"{rebar_rafter_key} @ {rb['lbs_per_lft']} LBS/LFT | "
                           f"avail={available_ft:.1f}' ({rafter_slope_ft:.1f}' - 2×{end_gap:.0f}' gap) | "
                           f"{sticks_per_side} stick(s)/corner × {actual_stick_ft:.1f}' ea | "
                           f"{n_rafters} rafters × 4 corners = "
                           f"{n_rafter_rebar_sticks} sticks"),
                ))

        # ── RAFTER CLIPS & PLATES (P1, P2/P6, P3) ─────────────────────────
        # P1 interior purlin clips: qty = (purlin_lines - 2) per rafter
        n_p1_per_rafter = max(0, n_purlin_lines - 2)
        n_p1_total = n_p1_per_rafter * n_rafters
        p1_w_in = 6.0
        p1_l_in = 10.0
        p1_thk_in = 0.135   # 10GA
        p1_wt_each = p1_w_in * p1_l_in * p1_thk_in * 0.2836  # steel lb/in³
        items.append(BOMLineItem(
            category="Rafter Clips & Plates",
            item_id="p1_clips",
            description=f"P1 Interior Purlin Clips 6\"×10\"×10GA ({n_p1_total} pcs)",
            qty=n_p1_total, unit="EA",
            unit_weight_lbs=round(p1_wt_each, 2),
            total_weight_lbs=round(n_p1_total * p1_wt_each, 1),
            unit_cost=0.0, total_cost=0.0,  # Fabricated in-house, costed via coil
            notes=f"{n_p1_per_rafter} per rafter × {n_rafters} rafters",
            piece_count=n_p1_total,
        ))

        # P2 end caps OR P6 end plates (2 per rafter)
        if bldg.angled_purlins:
            # P6: 9"×15"×10GA, ~5.06 lbs each, no purlin holes
            n_p6_total = 2 * n_rafters
            p6_wt = 5.06
            items.append(BOMLineItem(
                category="Rafter Clips & Plates",
                item_id="p6_end_plates",
                description=f"P6 End Plates 9\"×15\"×10GA ({n_p6_total} pcs)",
                qty=n_p6_total, unit="EA",
                unit_weight_lbs=p6_wt,
                total_weight_lbs=round(n_p6_total * p6_wt, 1),
                unit_cost=0.0, total_cost=0.0,
                notes=f"Angled purlin mode — replaces P2. No purlin holes. "
                      f"2 per rafter × {n_rafters} rafters",
                piece_count=n_p6_total,
            ))
        else:
            # P2: 9"×24"×10GA
            n_p2_total = 2 * n_rafters
            p2_w_in = 9.0
            p2_l_in = 24.0
            p2_wt_each = p2_w_in * p2_l_in * p1_thk_in * 0.2836
            items.append(BOMLineItem(
                category="Rafter Clips & Plates",
                item_id="p2_end_caps",
                description=f"P2 End Caps 9\"×24\"×10GA ({n_p2_total} pcs)",
                qty=n_p2_total, unit="EA",
                unit_weight_lbs=round(p2_wt_each, 2),
                total_weight_lbs=round(n_p2_total * p2_wt_each, 1),
                unit_cost=0.0, total_cost=0.0,
                notes=f"8 purlin holes per cap. 2 per rafter × {n_rafters} rafters",
                piece_count=n_p2_total,
            ))

        # P3 connection plates (one per rafter column position)
        n_p3_per_rafter = raft_n_cols
        n_p3_total = n_p3_per_rafter * n_rafters
        p3_wt_each = 14.0 * 26.0 * 0.75 * 0.2836  # ¾"×14"×26" steel
        items.append(BOMLineItem(
            category="Rafter Clips & Plates",
            item_id="p3_connection_plates",
            description=f"P3 Connection Plates 3/4\"×14\"×26\" ({n_p3_total} pcs)",
            qty=n_p3_total, unit="EA",
            unit_weight_lbs=round(p3_wt_each, 2),
            total_weight_lbs=round(n_p3_total * p3_wt_each, 1),
            unit_cost=PURCHASED_ITEMS["cap_plate"]["price_each"],
            total_cost=round(n_p3_total * PURCHASED_ITEMS["cap_plate"]["price_each"], 2),
            notes=f"{n_p3_per_rafter} per rafter × {n_rafters} rafters | "
                  f"A572 Gr 50, 4 bolt holes at 15/16\"",
            piece_count=n_p3_total,
        ))

        # ── WALL PANELS & GIRTS ───────────────────────────────────────────
        # Wall panel height = clear_height + (14" rafter + 12" purlin - 6" clearance)/12
        wall_panel_ht = bldg.clear_height_ft + (14 + 12 - 6) / 12.0   # +1.6667'
        peak_ht = bldg.clear_height_ft + (bldg.width_ft / 2.0) * tan_slope
        wall_girt_sp = (bldg.wall_girt_spacing_override
                        or get_purlin_spacing(bay_size_ft))
        panel_cov_ft = COILS["spartan_rib_48"]["panel_coverage_ft"]
        wf2_z = WASTE_FACTORS["12GA"]
        wf4_p = WASTE_FACTORS["29GA"]

        def _wall_item(label, wall_length_ft, wall_height_ft):
            """Return (girt_item, panel_item) for a wall section."""
            n_girt_lines = math.floor(wall_height_ft / wall_girt_sp) + 1
            girt_net = n_girt_lines * wall_length_ft
            girt_raw = girt_net * (1 + wf2_z)
            z_coil = COILS["z_purlin_20"]
            z_ppb = coil_price("z_purlin_20", cp)
            girt_wt = girt_raw * z_coil["lbs_per_lft"]
            girt_cost = girt_wt * z_ppb
            girt_item = BOMLineItem(
                category=f"Wall Steel - Coil 2",
                item_id=f"wall_girts_{label.lower().replace(' ','_')}",
                description=(f"20.125\" 12GA Z-Girts — {label} "
                             f"({n_girt_lines} lines × {wall_length_ft:.0f}', {wall_girt_sp:.1f}' OC)"),
                qty=round(girt_raw, 2), unit="LFT (coil)",
                unit_weight_lbs=z_coil["lbs_per_lft"],
                total_weight_lbs=round(girt_wt, 1),
                unit_cost=z_ppb, total_cost=round(girt_cost, 2),
                waste_factor=wf2_z,
                notes=(f"{n_girt_lines} girt lines × {wall_length_ft:.0f}' = "
                       f"{girt_net:.0f} LFT net | {wall_girt_sp:.1f}' OC spacing"),
                piece_count=n_girt_lines * n_bays,
                piece_length_in=round(bay_size_ft * 12, 1),
            )
            n_panel_runs_w = math.ceil(wall_length_ft / panel_cov_ft)
            panel_net_w = n_panel_runs_w * wall_height_ft
            panel_raw_w = panel_net_w * (1 + wf4_p)
            p_coil = COILS["spartan_rib_48"]
            p_ppb = coil_price("spartan_rib_48", cp)
            panel_wt_w = panel_raw_w * p_coil["lbs_per_lft"]
            panel_cost_w = panel_wt_w * p_ppb
            panel_item = BOMLineItem(
                category="Wall Panels - Coil 4",
                item_id=f"wall_panels_{label.lower().replace(' ','_')}",
                description=(f"48\" 29GA Spartan Rib Wall Panel — {label} "
                             f"({n_panel_runs_w} runs × {wall_height_ft:.2f}')"),
                qty=round(panel_raw_w, 2), unit="LFT (coil)",
                unit_weight_lbs=p_coil["lbs_per_lft"],
                total_weight_lbs=round(panel_wt_w, 1),
                unit_cost=p_ppb, total_cost=round(panel_cost_w, 2),
                waste_factor=wf4_p,
                notes=(f"{n_panel_runs_w} runs × {wall_height_ft:.2f}' = "
                       f"{panel_net_w:.0f} LFT net | "
                       f"Coverage {p_coil['panel_coverage_in']}\" per run | "
                       f"Panels run vertically (ribs up/down)"),
                piece_count=n_panel_runs_w,
                piece_length_in=round(wall_height_ft * 12, 1),
            )
            return girt_item, panel_item

        if bldg.include_back_wall:
            g, p = _wall_item("Back Wall", bldg.length_ft, wall_panel_ht)
            items.append(g); items.append(p)

        if bldg.include_end_walls:
            # Two gable end walls — use peak height (panels run to peak)
            g, p = _wall_item("End Walls (×2)", bldg.width_ft * 2, peak_ht)
            items.append(g); items.append(p)

        if bldg.include_side_walls:
            # Both long side walls (front + back, or both open sides)
            g, p = _wall_item("Side Walls (×2)", bldg.length_ft * 2, wall_panel_ht)
            items.append(g); items.append(p)

        # ── TEK Neoprene Screws ──────────────────────────────────────────
        # 3 special rows (eave1, seam, eave2) = 10 each; rest = 5 each
        per_eave = SCREWS["tek_neoprene"]["per_eave_or_seam_row"]   # 10
        per_field = SCREWS["tek_neoprene"]["per_field_row"]          # 5
        n_special = 3
        n_field_rows = max(0, n_purlin_lines - n_special)
        screws_per_run = n_special * per_eave + n_field_rows * per_field
        tek_neo = n_panel_runs * screws_per_run
        tek_neo_ppb = SCREWS["tek_neoprene"]["price_per_box"]
        tek_neo_box_qty = SCREWS["tek_neoprene"]["box_qty"]
        tek_neo_boxes = math.ceil(tek_neo / tek_neo_box_qty)
        tek_neo_cost = tek_neo_boxes * tek_neo_ppb
        items.append(BOMLineItem(
            category="Fasteners", item_id="tek_neoprene",
            description=(f"3/4\" TEK w/ Neoprene Washer — Panel/Wall to Purlin/Girt "
                         f"({tek_neo:,} pcs / {tek_neo_boxes} boxes of {tek_neo_box_qty:,})"),
            qty=tek_neo_boxes, unit="BOX",
            unit_cost=tek_neo_ppb,
            total_cost=round(tek_neo_cost, 2),
            notes=(f"{n_panel_runs} runs × {screws_per_run} screws/run | "
                   f"{n_purlin_lines} rows: 3×{per_eave} (eaves+seam) + "
                   f"{n_field_rows}×{per_field} (field) = {screws_per_run}/run | "
                   f"${tek_neo_ppb:.2f}/box of {tek_neo_box_qty:,}"),
            piece_count=tek_neo,
        ))

        # ── TEK Structural Screws ─────────────────────────────────────────
        n_total_plates = n_int_plates + n_ext_plates
        tek_struct = n_total_plates * SCREWS["tek_structural"]["per_plate"]
        tek_str_ppb = SCREWS["tek_structural"]["price_per_box"]
        tek_str_box_qty = SCREWS["tek_structural"]["box_qty"]
        tek_str_boxes = math.ceil(tek_struct / tek_str_box_qty)
        tek_str_cost = tek_str_boxes * tek_str_ppb
        items.append(BOMLineItem(
            category="Fasteners", item_id="tek_structural",
            description=(f"3/4\" TEK No Washer — Structural "
                         f"({tek_struct:,} pcs / {tek_str_boxes} boxes of {tek_str_box_qty:,})"),
            qty=tek_str_boxes, unit="BOX",
            unit_cost=tek_str_ppb,
            total_cost=round(tek_str_cost, 2),
            notes=(f"{n_total_plates} plates × 8 screws/plate | "
                   f"${tek_str_ppb:.2f}/box of {tek_str_box_qty:,}"),
            piece_count=tek_struct,
        ))

        # ── TEK Screws — Endcap-to-Purlin ────────────────────────────────
        # 4 tek screws per purlin line × 2 endcaps (both building ends)
        tek_end_spec = SCREWS["tek_endcap"]
        n_endcap_tek = n_purlin_lines * tek_end_spec["per_purlin"] * 2  # both ends
        tek_end_box_qty = tek_end_spec["box_qty"]
        tek_end_ppb = tek_end_spec["price_per_box"]
        tek_end_boxes = math.ceil(n_endcap_tek / tek_end_box_qty)
        tek_end_cost = tek_end_boxes * tek_end_ppb
        items.append(BOMLineItem(
            category="Fasteners", item_id="tek_endcap",
            description=(f"#10 TEK — Endcap-to-Purlin "
                         f"({n_endcap_tek:,} pcs / {tek_end_boxes} box(es) of {tek_end_box_qty:,})"),
            qty=tek_end_boxes, unit="BOX",
            unit_cost=tek_end_ppb,
            total_cost=round(tek_end_cost, 2),
            notes=(f"{n_purlin_lines} purlin lines × {tek_end_spec['per_purlin']} screws/purlin "
                   f"× 2 endcaps (both building ends) = {n_endcap_tek} pcs | "
                   f"2 top + 2 bottom per connection"),
            piece_count=n_endcap_tek,
        ))

        # ── TEK Screws — Purlin Splices ───────────────────────────────────
        # Splices occur where purlins span across bays; n_splices depends on bay layout
        # For Z-purlins with overhang: each purlin group has (n_bays - 1) splice points
        # For C-purlins: each line has (n_bays - 1) splice points if spanning
        # In typical Z-purlin setup: splice near mid-bay, 1 per bay boundary per line
        tek_spl_spec = SCREWS["tek_splice"]
        n_splice_points = n_purlin_lines * max(0, n_bays - 1)  # splice at each interior rafter
        n_splice_tek = n_splice_points * tek_spl_spec["per_splice"]
        tek_spl_box_qty = tek_spl_spec["box_qty"]
        tek_spl_ppb = tek_spl_spec["price_per_box"]
        tek_spl_boxes = max(0, math.ceil(n_splice_tek / tek_spl_box_qty)) if n_splice_tek > 0 else 0
        tek_spl_cost = tek_spl_boxes * tek_spl_ppb
        if n_splice_tek > 0:
            items.append(BOMLineItem(
                category="Fasteners", item_id="tek_splice",
                description=(f"#10 TEK — Purlin Splice "
                             f"({n_splice_tek:,} pcs / {tek_spl_boxes} box(es) of {tek_spl_box_qty:,})"),
                qty=tek_spl_boxes, unit="BOX",
                unit_cost=tek_spl_ppb,
                total_cost=round(tek_spl_cost, 2),
                notes=(f"{n_purlin_lines} lines × {max(0, n_bays - 1)} splice points "
                       f"× {tek_spl_spec['per_splice']} screws/splice = {n_splice_tek} pcs | "
                       f"8 screws through 6\" overlap at each splice"),
                piece_count=n_splice_tek,
            ))

        # ── TEK Screws — Sag Rod-to-Purlin ────────────────────────────────
        # Sag rods cross every purlin line; 2 screws per crossing
        tek_sag_spec = SCREWS["tek_sag_rod"]
        n_sag_rods_total = n_rafters * 2  # 2 sag rods per rafter
        n_sag_purlin_crossings = n_sag_rods_total * n_purlin_lines
        n_sag_tek = n_sag_purlin_crossings * tek_sag_spec["per_purlin"]
        tek_sag_box_qty = tek_sag_spec["box_qty"]
        tek_sag_ppb = tek_sag_spec["price_per_box"]
        tek_sag_boxes = math.ceil(n_sag_tek / tek_sag_box_qty)
        tek_sag_cost = tek_sag_boxes * tek_sag_ppb
        items.append(BOMLineItem(
            category="Fasteners", item_id="tek_sag_rod",
            description=(f"#10 TEK — Sag Rod-to-Purlin "
                         f"({n_sag_tek:,} pcs / {tek_sag_boxes} box(es) of {tek_sag_box_qty:,})"),
            qty=tek_sag_boxes, unit="BOX",
            unit_cost=tek_sag_ppb,
            total_cost=round(tek_sag_cost, 2),
            notes=(f"{n_sag_rods_total} sag rods × {n_purlin_lines} purlin lines "
                   f"× {tek_sag_spec['per_purlin']} screws/crossing = {n_sag_tek} pcs | "
                   f"Underside attachment, no pre-punch"),
            piece_count=n_sag_tek,
        ))

        # ── Trim (if enabled) ─────────────────────────────────────────────
        if bldg.include_trim:
            n_trim = calc_trim_sticks(bldg.length_ft, bldg.width_ft,
                                      TRIM["stick_length_ft"], TRIM["overlap_in"])
            stitch_total = n_trim * SCREWS["stitch"]["per_trim_stick"]
            items.append(BOMLineItem(
                category="Fasteners", item_id="stitch_screws",
                description=f"1/4\"-14 x 7/8\" Stitch Screw — Trim ({stitch_total:,} pcs)",
                qty=stitch_total, unit="EA",
                notes=f"{n_trim} sticks x 5 screws/stick",
            ))
            usable = TRIM["stick_length_ft"] - (TRIM["overlap_in"] / 12.0)
            fb = math.ceil(bldg.length_ft / usable) * 2
            ends = math.ceil(bldg.width_ft / usable) * 2
            items.append(BOMLineItem(
                category="Trim", item_id="j_channel_trim",
                description=f"J-Channel Trim, 10' sticks ({n_trim} sticks) — Home Depot",
                qty=n_trim, unit="EA",
                unit_cost=0.0, total_cost=0.0,
                notes=(f"Front+Back: {fb} sticks | Ends: {ends} sticks | "
                       f"All 4 sides with 3\" overlap. Priced separately."),
            ))

        # ── ACCESSORIES & SECONDARY STRUCTURAL ─────────────────────────────
        self._generate_accessories(bldg, items, n_struct_cols, n_bays, n_frames,
                                   slope_deg, tan_slope, rafter_slope_ft,
                                   wall_panel_ht, peak_ht)

        # ── Welding & Finishing Consumables ──────────────────────────────
        sqft = bldg.width_ft * bldg.length_ft
        welding_cost = (sqft / 5000.0) * bldg.welding_cost_per_5000sqft
        items.append(BOMLineItem(
            category="Consumables",
            item_id="welding_consumables",
            description="Welding Wire/Rod, Welding Gas, Cold Galvanized Paint",
            qty=round(sqft, 0), unit="SQFT",
            unit_cost=round(bldg.welding_cost_per_5000sqft / 5000.0, 6),
            total_cost=round(welding_cost, 2),
            notes=(f"${bldg.welding_cost_per_5000sqft:.2f} per 5,000 SQFT | "
                   f"{sqft:.0f} SQFT footprint | "
                   f"Welding wire, welding gas, cold galvanize paint"),
        ))

        # ── Fabrication Labor ─────────────────────────────────────────────
        labor_days_detail = {}
        labor_raw_cost = 0.0
        if bldg.include_labor:
            lr = LABOR["rates"]
            # Use per-building adjustable daily rate + 10% overhead
            overhead_pct = LABOR["overhead_pct"] / 100.0
            effective_daily = bldg.labor_daily_rate * (1 + overhead_pct)

            # Column and rafter days (piece-based, sequential — same equipment)
            days_cols = math.ceil(n_struct_cols / lr["box_pieces_per_day"])
            days_rafts = math.ceil(n_rafters / lr["box_pieces_per_day"])

            # Purlin days (roll-based)
            purlin_roll_wt = COILS["z_purlin_20"]["roll_weight_lbs"]
            purlin_total_wt = sum(i.total_weight_lbs for i in items
                                  if "z_purlin" in i.item_id)
            purlin_rolls = math.ceil(purlin_total_wt / purlin_roll_wt) if purlin_total_wt > 0 else 0
            days_purlins = math.ceil(purlin_rolls / lr["purlin_rolls_per_day"]) if purlin_rolls > 0 else 0

            # Panel days (roll-based)
            panel_roll_wt = COILS["spartan_rib_48"]["roll_weight_lbs"]
            panel_total_wt = sum(i.total_weight_lbs for i in items
                                 if "spartan_rib" in i.item_id)
            panel_rolls = math.ceil(panel_total_wt / panel_roll_wt) if panel_total_wt > 0 else 0
            days_panels = math.ceil(panel_rolls / lr["panel_rolls_per_day"]) if panel_rolls > 0 else 0

            # Angle (sag rod) days (roll-based)
            angle_roll_wt = COILS["angle_4_16ga"]["roll_weight_lbs"]
            angle_total_wt = sum(i.total_weight_lbs for i in items
                                 if "sag_rod" in i.item_id)
            angle_rolls = math.ceil(angle_total_wt / angle_roll_wt) if angle_total_wt > 0 else 0
            days_angle = math.ceil(angle_rolls / lr["angle_rolls_per_day"]) if angle_rolls > 0 else 0

            # Total days = max(cols+rafters stream, purlins, panels, angle)
            box_stream_days = days_cols + days_rafts
            total_fab_days = max(box_stream_days, days_purlins, days_panels, days_angle)

            labor_raw_cost = total_fab_days * effective_daily
            markup = self.project.markup_pct / 100.0
            labor_sell = round(labor_raw_cost * (1 + markup), 2)

            labor_days_detail = {
                "days_columns": days_cols,
                "days_rafters": days_rafts,
                "days_purlins": days_purlins,
                "days_panels": days_panels,
                "days_angle": days_angle,
                "box_stream_days": box_stream_days,
                "total_fab_days": total_fab_days,
                "daily_rate": bldg.labor_daily_rate,  # adjustable per building
                "overhead_pct": LABOR["overhead_pct"],
                "effective_daily_rate": round(effective_daily, 2),
                "labor_raw_cost": round(labor_raw_cost, 2),
                "labor_sell_price": labor_sell,
                "crew_size": LABOR["crew_size"],
            }

        # Totals (materials only — labor is tracked separately in geometry/labor)
        total_wt = sum(i.total_weight_lbs for i in items)
        total_mat = sum(i.total_cost for i in items)
        markup = self.project.markup_pct / 100.0
        result.line_items = items
        result.total_weight_lbs = round(total_wt, 1)
        result.total_material_cost = round(total_mat, 2)
        result.total_sell_price = round(total_mat * (1 + markup), 2)
        result.geometry["labor"] = labor_days_detail
        result.geometry["wall_panel_ht"] = round(wall_panel_ht, 3)
        result.geometry["peak_ht"] = round(peak_ht, 2)

        # ── Coil Inventory Tracking ──────────────────────────────────────
        # Summarize coil consumption per type for inventory deduction & reorder alerts
        coil_usage = {}
        for item in items:
            if item.unit == "LFT (coil)":
                cid = item.item_id
                # Map item_id to coil type
                coil_key = None
                if "c_section" in cid or "splice_plate" in cid:
                    coil_key = "c_section_23"
                elif "z_purlin" in cid or "wall_girt" in cid or "endcap_u" in cid:
                    coil_key = "z_purlin_20"
                elif "sag_rod" in cid:
                    coil_key = "angle_4_16ga"
                elif "spartan_rib" in cid or "wall_panel" in cid:
                    coil_key = "spartan_rib_48"
                elif "interior_plate" in cid:
                    coil_key = "plate_6_10ga"
                elif "exterior_plate" in cid:
                    coil_key = "plate_9_10ga"
                elif "strap" in cid:
                    coil_key = "strap_15_10ga"

                if coil_key:
                    if coil_key not in coil_usage:
                        coil_info = COILS[coil_key]
                        coil_usage[coil_key] = {
                            "coil_name": coil_info["name"],
                            "total_lft": 0.0,
                            "total_lbs": 0.0,
                            "roll_weight_lbs": coil_info.get("roll_weight_lbs", 3000),
                            "rolls_needed": 0,
                        }
                    coil_usage[coil_key]["total_lft"] += item.qty
                    coil_usage[coil_key]["total_lbs"] += item.total_weight_lbs

        # Calculate rolls needed per coil type
        for key, usage in coil_usage.items():
            roll_wt = usage["roll_weight_lbs"]
            usage["rolls_needed"] = math.ceil(usage["total_lbs"] / roll_wt) if roll_wt > 0 else 0
            usage["total_lft"] = round(usage["total_lft"], 2)
            usage["total_lbs"] = round(usage["total_lbs"], 1)

        # Also track purchased items usage
        purchased_usage = {
            "cap_plates": n_cap,
            "gusset_triangles": n_gussets,
            "bolt_assemblies": n_bolts,
        }

        # Rebar usage by size
        rebar_usage = {}
        for item in items:
            if item.category == "Rebar":
                # Extract size from item_id (e.g., "rebar_col_9" → "#9")
                parts = item.item_id.split("_")
                if len(parts) >= 3:
                    size_key = f"#{parts[-1]}"
                    if size_key not in rebar_usage:
                        rebar_usage[size_key] = {"sticks": 0, "lbs": 0.0}
                    rebar_usage[size_key]["sticks"] += item.qty
                    rebar_usage[size_key]["lbs"] += item.total_weight_lbs

        result.geometry["coil_usage"] = coil_usage
        result.geometry["purchased_usage"] = purchased_usage
        result.geometry["rebar_usage"] = rebar_usage

        return result

    def calculate_project(self, buildings: List[BuildingConfig]) -> ProjectBOM:
        proj = ProjectBOM(project=self.project)
        for b in buildings:
            proj.buildings.append(self.calculate_building(b))
        proj.total_weight_lbs = round(sum(b.total_weight_lbs for b in proj.buildings), 1)
        proj.total_material_cost = round(sum(b.total_material_cost for b in proj.buildings), 2)
        # Sell price includes material sell price + all building labor sell prices
        mat_sell = sum(b.total_sell_price for b in proj.buildings)
        labor_sell_total = sum(
            b.geometry.get("labor", {}).get("labor_sell_price", 0.0)
            for b in proj.buildings
        )
        proj.total_sell_price = round(mat_sell + labor_sell_total, 2)

        coil_sum = {}
        for bb in proj.buildings:
            for item in bb.line_items:
                if item.unit == "LFT (coil)":
                    cid = item.item_id
                    if cid not in coil_sum:
                        coil_sum[cid] = {
                            "description": item.description.split("(")[0].strip(),
                            "total_lft": 0.0, "total_lbs": 0.0, "total_cost": 0.0,
                        }
                    coil_sum[cid]["total_lft"] += item.qty
                    coil_sum[cid]["total_lbs"] += item.total_weight_lbs
                    coil_sum[cid]["total_cost"] += item.total_cost
        proj.summary_by_coil = coil_sum
        return proj


# ─────────────────────────────────────────────
# JSON SERIALIZATION
# ─────────────────────────────────────────────

def bom_to_dict(bom: ProjectBOM) -> dict:
    buildings_out = []
    for bb in bom.buildings:
        items_out = [{
            "category": i.category, "item_id": i.item_id,
            "description": i.description, "qty": round(i.qty, 2),
            "unit": i.unit,
            "unit_weight_lbs": round(i.unit_weight_lbs, 4),
            "total_weight_lbs": round(i.total_weight_lbs, 1),
            "unit_cost": round(i.unit_cost, 4),
            "total_cost": round(i.total_cost, 2),
            "waste_factor": round(i.waste_factor, 4),
            "notes": i.notes,
            "piece_count": i.piece_count,
            "piece_length_in": round(i.piece_length_in, 2),
        } for i in bb.line_items]

        labor = bb.geometry.get("labor", {})
        buildings_out.append({
            "building_id": bb.building.building_id,
            "errors": bb.errors,
            "building_name": bb.building.building_name,
            "type": bb.geometry.get("frame_type", bb.building.type),  # auto-determined
            "width_ft": bb.building.width_ft,
            "length_ft": bb.building.length_ft,
            "clear_height_ft": bb.building.clear_height_ft,
            "max_bay_ft": bb.building.max_bay_ft,
            "pitch_key": bb.building.pitch_key,
            "purlin_spacing_override": bb.building.purlin_spacing_override,
            "embedment_ft": bb.building.embedment_ft,
            "column_buffer_ft": bb.building.column_buffer_ft,
            "reinforced": bb.building.reinforced,
            "rebar_col_size": bb.building.rebar_col_size,
            "rebar_beam_size": bb.building.rebar_beam_size,
            "include_rafter_rebar": bb.building.include_rafter_rebar,
            "rebar_rafter_size": bb.building.rebar_rafter_size,
            "include_trim": bb.building.include_trim,
            "include_back_wall": bb.building.include_back_wall,
            "include_end_walls": bb.building.include_end_walls,
            "include_side_walls": bb.building.include_side_walls,
            "include_labor": bb.building.include_labor,
            "geometry": bb.geometry,
            "line_items": items_out,
            "total_weight_lbs": bb.total_weight_lbs,
            "total_material_cost": bb.total_material_cost,
            "total_sell_price": bb.total_sell_price,
            # Labor (separate from material sell price)
            "labor_total_days": labor.get("total_fab_days", 0),
            "labor_raw_cost": labor.get("labor_raw_cost", 0.0),
            "labor_sell_price": labor.get("labor_sell_price", 0.0),
        })

    return {
        "project": {
            "name": bom.project.name, "job_code": bom.project.job_code,
            "address": bom.project.address, "city": bom.project.city,
            "state": bom.project.state, "zip_code": bom.project.zip_code,
            "customer_name": bom.project.customer_name,
            "quote_date": bom.project.quote_date,
            "wind_speed_mph": bom.project.wind_speed_mph,
            "footing_depth_ft": bom.project.footing_depth_ft,
            "markup_pct": bom.project.markup_pct,
        },
        "buildings": buildings_out,
        "total_weight_lbs": bom.total_weight_lbs,
        "total_material_cost": bom.total_material_cost,
        "total_sell_price": bom.total_sell_price,
        "total_labor_sell_price": round(
            sum(b.get("labor_sell_price", 0.0) for b in buildings_out), 2),
        "total_labor_days": sum(b.get("labor_total_days", 0) for b in buildings_out),
        "summary_by_coil": bom.summary_by_coil,
    }
