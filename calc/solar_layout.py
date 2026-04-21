"""
Solar Panel Layout Engine — Structures America Carports

Calculates building dimensions from solar panel arrays and determines
purlin spacing dictated by panel mounting requirements.

Two modes:
  panel_count  — user specifies panels_across x panels_along, engine returns
                 building width/length and purlin layout
  fit_to_dims  — user specifies available W x L in feet, engine calculates
                 how many panels fit and reports coverage

Purlin spacing in solar mode is DICTATED by the panels (not user input):
  Landscape: one purlin per panel edge, N+1 purlin lines for N panels across
  Portrait:  purlins at mounting-hole positions within each panel pair,
             2N purlin lines for N panels across

All internal math uses mm for precision; output converted to ft/in.
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

MM_PER_INCH = 25.4
MM_PER_FOOT = 304.8
SQFT_PER_SQMM = 1.0 / (MM_PER_FOOT ** 2)

# Purlin geometry (12" Z-purlin, from defaults.py: Z-12"x3.5"x12GA)
PURLIN_TOP_FLANGE_IN = 3.5          # top flange width in inches
PURLIN_TOP_FLANGE_MM = PURLIN_TOP_FLANGE_IN * MM_PER_INCH   # ~88.9 mm
MIN_BOLT_EDGE_CLEARANCE_IN = 0.5    # minimum from bolt center to purlin edge
MIN_BOLT_EDGE_CLEARANCE_MM = MIN_BOLT_EDGE_CLEARANCE_IN * MM_PER_INCH  # 12.7 mm

# C-purlin butt joint zone: 4" each side of rafter center
C_PURLIN_JOINT_ZONE_MM = 4.0 * MM_PER_INCH  # 101.6 mm

# Z-purlin overlap zone: 6" splice overlap
Z_PURLIN_OVERLAP_ZONE_MM = 6.0 * MM_PER_INCH  # 152.4 mm

# Bolt stacks per panel (4 mounting points)
BOLT_STACKS_PER_PANEL = 4


# ─────────────────────────────────────────────────────────────────────────────
# DATA STRUCTURES
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class SolarPanelSpec:
    """Physical dimensions of a solar panel (mm).

    Defaults are for the Canadian Solar CS3K-P series, one of the most
    common utility-scale panels used on carport structures.
    """
    width_mm: float = 992.0
    length_mm: float = 2108.0
    mount_hole_from_edge_mm: float = 20.0    # mounting hole distance from panel long edge
    mount_hole_inset_mm: float = 250.0       # mounting hole inset from panel short edge


@dataclass
class SolarLayoutConfig:
    """Input configuration for solar layout calculation."""
    panel: SolarPanelSpec = field(default_factory=SolarPanelSpec)
    orientation: str = "landscape"   # "landscape", "portrait", or "compare"
    panels_across: int = 5           # panels across building width
    panels_along: int = 20           # panels along building length
    gap_width_in: float = 0.25       # gap between panels across (width direction)
    gap_length_in: float = 0.25      # gap between panels along (length direction)
    edge_clearance_in: float = 4.0   # clearance at building edges (width sides)
    endcap_clearance_in: float = 4.0 # clearance at building ends (length sides)
    mode: str = "panel_count"        # "panel_count" or "fit_to_dims"
    available_width_ft: float = 0.0  # only used in fit_to_dims mode
    available_length_ft: float = 0.0 # only used in fit_to_dims mode
    purlin_type: str = "Z"           # "Z" or "C" — needed for bolt hole validation


@dataclass
class SolarLayoutResult:
    """Output of solar layout calculation."""
    building_width_ft: float = 0.0
    building_length_ft: float = 0.0
    panels_across: int = 0
    panels_along: int = 0
    total_panels: int = 0
    purlin_spacing_ft: float = 0.0
    n_purlin_lines: int = 0
    orientation: str = "landscape"
    bolt_stacks: int = 0             # 4 per panel
    dummy_panels: int = 0            # fit-to-dims only
    bolt_hole_warnings: List[str] = field(default_factory=list)
    panel_coverage_sqft: float = 0.0
    building_area_sqft: float = 0.0
    # Extra detail fields for integration with BOM
    purlin_spacing_mm: float = 0.0
    building_width_mm: float = 0.0
    building_length_mm: float = 0.0
    purlin_positions_mm: List[float] = field(default_factory=list)
    bolt_positions_mm: List[float] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for JSON / UI consumption."""
        return {
            "building_width_ft": round(self.building_width_ft, 4),
            "building_length_ft": round(self.building_length_ft, 4),
            "panels_across": self.panels_across,
            "panels_along": self.panels_along,
            "total_panels": self.total_panels,
            "purlin_spacing_ft": round(self.purlin_spacing_ft, 4),
            "n_purlin_lines": self.n_purlin_lines,
            "orientation": self.orientation,
            "bolt_stacks": self.bolt_stacks,
            "dummy_panels": self.dummy_panels,
            "bolt_hole_warnings": self.bolt_hole_warnings,
            "panel_coverage_sqft": round(self.panel_coverage_sqft, 2),
            "building_area_sqft": round(self.building_area_sqft, 2),
        }


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _mm_to_ft(mm: float) -> float:
    """Convert millimeters to feet."""
    return mm / MM_PER_FOOT


def _ft_to_mm(ft: float) -> float:
    """Convert feet to millimeters."""
    return ft * MM_PER_FOOT


def _in_to_mm(inches: float) -> float:
    """Convert inches to millimeters."""
    return inches * MM_PER_INCH


def _mm_to_in(mm: float) -> float:
    """Convert millimeters to inches."""
    return mm / MM_PER_INCH


def _panel_dims_mm(panel: SolarPanelSpec, orientation: str):
    """Return (dim_across, dim_along) in mm based on orientation.

    Landscape: panel width goes across the building, length goes along.
    Portrait:  panel length goes across the building, width goes along.
    """
    if orientation == "landscape":
        return panel.width_mm, panel.length_mm
    else:  # portrait
        return panel.length_mm, panel.width_mm


# ─────────────────────────────────────────────────────────────────────────────
# BUILDING DIMENSIONS FROM PANEL COUNT
# ─────────────────────────────────────────────────────────────────────────────

def _calc_building_dims_mm(
    panels_across: int,
    panels_along: int,
    panel: SolarPanelSpec,
    orientation: str,
    gap_width_in: float,
    gap_length_in: float,
    edge_clearance_in: float,
    endcap_clearance_in: float,
) -> tuple:
    """Calculate building width and length in mm from panel array.

    Returns:
        (width_mm, length_mm, dim_across_mm, dim_along_mm)
    """
    dim_across, dim_along = _panel_dims_mm(panel, orientation)
    gap_across_mm = _in_to_mm(gap_width_in)
    gap_along_mm = _in_to_mm(gap_length_in)
    edge_mm = _in_to_mm(edge_clearance_in)
    endcap_mm = _in_to_mm(endcap_clearance_in)

    width_mm = (
        panels_across * dim_across
        + (panels_across - 1) * gap_across_mm
        + 2 * edge_mm
    )
    length_mm = (
        panels_along * dim_along
        + (panels_along - 1) * gap_along_mm
        + 2 * endcap_mm
    )
    return width_mm, length_mm, dim_across, dim_along


# ─────────────────────────────────────────────────────────────────────────────
# FIT-TO-DIMENSIONS MODE
# ─────────────────────────────────────────────────────────────────────────────

def _fit_panels_to_dims(
    available_width_mm: float,
    available_length_mm: float,
    panel: SolarPanelSpec,
    orientation: str,
    gap_width_in: float,
    gap_length_in: float,
    edge_clearance_in: float,
    endcap_clearance_in: float,
) -> tuple:
    """Calculate how many panels fit in available dimensions.

    Returns:
        (panels_across, panels_along, dummy_panels)
        where dummy_panels = number of panels that would hang off the edge
        if rounding up to next whole panel.
    """
    dim_across, dim_along = _panel_dims_mm(panel, orientation)
    gap_across_mm = _in_to_mm(gap_width_in)
    gap_along_mm = _in_to_mm(gap_length_in)
    edge_mm = _in_to_mm(edge_clearance_in)
    endcap_mm = _in_to_mm(endcap_clearance_in)

    # Usable space after edge clearances
    usable_w = available_width_mm - 2 * edge_mm
    usable_l = available_length_mm - 2 * endcap_mm

    if usable_w <= 0 or usable_l <= 0:
        return 0, 0, 0

    # panels_across = floor((usable_w + gap) / (panel_dim + gap))
    panels_across = int((usable_w + gap_across_mm) / (dim_across + gap_across_mm))
    panels_along = int((usable_l + gap_along_mm) / (dim_along + gap_along_mm))

    panels_across = max(panels_across, 0)
    panels_along = max(panels_along, 0)

    if panels_across == 0 or panels_along == 0:
        return panels_across, panels_along, 0

    # Calculate how much space is left over and report dummy panels
    used_w = panels_across * dim_across + (panels_across - 1) * gap_across_mm
    used_l = panels_along * dim_along + (panels_along - 1) * gap_along_mm
    leftover_w = usable_w - used_w
    leftover_l = usable_l - used_l

    # A "dummy panel" is one more panel in each direction that doesn't fit
    dummy_across = 1 if leftover_w > dim_across * 0.1 else 0
    dummy_along = 1 if leftover_l > dim_along * 0.1 else 0

    # Dummy panels = panels that would exist in the next row/column
    dummy_panels = 0
    if dummy_across:
        dummy_panels += panels_along  # one extra column
    if dummy_along:
        dummy_panels += panels_across  # one extra row
    if dummy_across and dummy_along:
        dummy_panels += 1  # corner panel

    return panels_across, panels_along, dummy_panels


# ─────────────────────────────────────────────────────────────────────────────
# PURLIN SPACING (DICTATED BY PANELS)
# ─────────────────────────────────────────────────────────────────────────────

def _calc_purlin_layout(
    panels_across: int,
    panel: SolarPanelSpec,
    orientation: str,
    gap_width_in: float,
    edge_clearance_in: float,
) -> tuple:
    """Calculate purlin spacing and positions for solar mounting.

    Landscape: one purlin at each panel edge across the width.
               N+1 purlin lines for N panels across.
               Spacing = panel_width_mm (uniform).

    Portrait:  purlins at mounting-hole positions within each panel.
               2 purlin lines per panel (at the two long-edge mount holes).
               2N purlin lines for N panels across.
               Spacing alternates: intra-panel and inter-panel.

    Returns:
        (spacing_mm, n_purlin_lines, purlin_positions_mm)
        spacing_mm is the representative/primary spacing value.
        purlin_positions_mm is the list of all purlin Y-positions from
        building edge (position 0 = start of building width).
    """
    dim_across, _ = _panel_dims_mm(panel, orientation)
    gap_mm = _in_to_mm(gap_width_in)
    edge_mm = _in_to_mm(edge_clearance_in)

    positions = []

    if orientation == "landscape":
        # N+1 purlin lines: one at each panel edge
        n_purlin_lines = panels_across + 1
        # First purlin at start of first panel (after edge clearance)
        for i in range(n_purlin_lines):
            pos = edge_mm + i * dim_across
            if i > 0:
                pos += i * gap_mm  # add accumulated gaps
            # Correction: gap is between panels, so gap count = i for purlin i
            # Actually let's recalculate cleanly
            pass

        # Recalculate positions cleanly
        positions = []
        pos = edge_mm  # first purlin at left edge of first panel
        positions.append(pos)
        for i in range(panels_across):
            pos += dim_across  # right edge of panel i
            if i < panels_across - 1:
                # There's a gap before the next panel, but purlin is at the
                # right edge of this panel (= left edge of gap)
                # Actually, purlin lines are AT the panel edges, and the gap
                # is between. So next purlin = pos + gap_mm
                pass
            positions.append(pos)
            if i < panels_across - 1:
                pos += gap_mm  # skip the gap to reach next panel left edge

        spacing_mm = dim_across  # uniform spacing (the primary one)

    else:  # portrait
        # 2 purlin lines per panel, positioned at mounting holes
        # Mounting holes are mount_hole_from_edge_mm from each long edge
        # In portrait, the long edge runs along the building length,
        # and the panel's length dimension goes across the building.
        #
        # The two mounting rails are at:
        #   mount_hole_from_edge_mm from left long edge
        #   panel_width_mm - mount_hole_from_edge_mm from left long edge
        # But in portrait, dim_across = panel.length_mm and the "long edge"
        # is the width edge. The mounting holes are offset from the
        # panel's width edges (the short dimension in portrait = panel.width_mm).
        #
        # Actually, mount holes are always referenced to the physical panel:
        #   - mount_hole_from_edge_mm: distance from panel LONG edge (length side)
        #   - In portrait, panel long edges run along building length direction
        #   - Across the building (portrait), the dimension is panel.length_mm
        #   - The two purlin lines per panel are at:
        #     panel_start + mount_hole_from_edge_mm  (near left long edge)
        #     panel_start + (panel.width_mm - mount_hole_from_edge_mm)
        #       ... but wait, in portrait the ACROSS dimension is length_mm,
        #       and the purlin rails sit at the mount_hole_from_edge positions
        #       measured from the long edges (which in portrait run along length).
        #
        # Let's be precise:
        # Physical panel: width_mm (short side), length_mm (long side)
        # Mounting holes: from_edge_mm from each LONG edge (length edge)
        # Portrait orientation: length_mm goes across building width
        #   The two long edges are at the "top" and "bottom" of the panel
        #   as viewed across the building width.
        #   Purlin rail 1: mount_hole_from_edge_mm from the "top" long edge
        #   Purlin rail 2: mount_hole_from_edge_mm from the "bottom" long edge
        #   Distance between rails = length_mm - 2 * mount_hole_from_edge_mm

        intra_panel_mm = panel.length_mm - 2 * panel.mount_hole_from_edge_mm
        n_purlin_lines = 2 * panels_across

        positions = []
        pos = edge_mm + panel.mount_hole_from_edge_mm  # first mount hole
        for i in range(panels_across):
            panel_start = edge_mm + i * (panel.length_mm + gap_mm)
            rail_1 = panel_start + panel.mount_hole_from_edge_mm
            rail_2 = panel_start + panel.length_mm - panel.mount_hole_from_edge_mm
            positions.append(rail_1)
            positions.append(rail_2)

        # Primary spacing = intra-panel distance (the more critical one)
        spacing_mm = intra_panel_mm

    return spacing_mm, n_purlin_lines, positions


# ─────────────────────────────────────────────────────────────────────────────
# BOLT HOLE VALIDATION
# ─────────────────────────────────────────────────────────────────────────────

def _validate_bolt_holes(
    purlin_positions_mm: List[float],
    panel: SolarPanelSpec,
    orientation: str,
    panels_across: int,
    gap_width_in: float,
    edge_clearance_in: float,
    purlin_type: str,
) -> List[str]:
    """Validate that mounting bolt holes fall on the purlin top flange.

    Checks:
    1. Bolt center is within the purlin top flange (not in web or lip).
    2. At least 0.5" clearance from bolt center to purlin flange edge.
    3. Bolt hole not within C-purlin butt joint zone or Z-purlin overlap zone.

    Returns list of warning strings (empty = all clear).
    """
    warnings = []
    gap_mm = _in_to_mm(gap_width_in)
    edge_mm = _in_to_mm(edge_clearance_in)
    dim_across, _ = _panel_dims_mm(panel, orientation)
    half_flange = PURLIN_TOP_FLANGE_MM / 2.0

    # Build list of bolt hole positions across the building width.
    # Each panel has 4 bolt holes: 2 on each purlin rail.
    # The bolt positions along the building width depend on orientation.

    bolt_across_positions = []  # position of bolt center across building width

    if orientation == "landscape":
        # Bolt holes are at mount_hole_from_edge_mm from each panel LONG edge.
        # In landscape, long edges run across the building (dim_across = width_mm).
        # Wait — long edge = length_mm edge. In landscape:
        #   across = width_mm, along = length_mm
        #   The panel's long edges (length sides) run ALONG the building.
        #   The panel's short edges (width sides) run ACROSS the building.
        #   Mount holes are from the LONG edge, which runs along building length.
        #   So across the building, bolt positions are at:
        #     panel_left + mount_hole_from_edge_mm
        #     panel_left + (width_mm - mount_hole_from_edge_mm)
        #   These should align with the purlin lines at panel edges? No —
        #   In landscape, purlins are at panel EDGES (left/right of each panel).
        #   The bolts are inset from the long edges (top/bottom of panel).
        #   The bolts attach to the purlins that run under the panel edges.
        #
        # Actually, the purlins run along the building LENGTH (perpendicular to
        # rafters in a standard layout). In a solar carport the purlins run
        # across the BUILDING WIDTH (parallel to rafters would be wrong).
        #
        # Standard carport: purlins span between rafters along building length.
        # The "purlin lines" are positions across the building width.
        # In landscape solar:
        #   Purlin lines are at each panel width-edge across the building.
        #   Bolts connect panel to purlin. The bolt across-position must be
        #   AT the purlin line (on the flange). The bolt along-position is at
        #   mount_hole_inset_mm from the panel short edge.
        #
        # So for landscape, bolt across-positions ARE the purlin positions,
        # and the check is that the bolt is centered on the flange. Since
        # the purlin IS placed at the panel edge, by definition the bolt is
        # at mount_hole_from_edge_mm OFFSET from the purlin center.

        for i in range(panels_across):
            panel_left = edge_mm + i * (panel.width_mm + gap_mm)
            # Left purlin is at panel_left (purlin center aligned with panel left edge)
            # Bolt is at panel_left + mount_hole_from_edge_mm from the long edge
            # But "from_edge" means from the long (length) edge, which in landscape
            # runs along the building. The bolt's across-position is:
            #   purlin_center ± some offset
            # If purlin is at panel left edge and bolt is mount_hole_from_edge from
            # the adjacent long edge, the bolt IS on the purlin.
            # The offset from purlin center = mount_hole_from_edge_mm (bolt is inset
            # from the panel edge by this amount, and the purlin IS at the panel edge).
            bolt_offset = panel.mount_hole_from_edge_mm
            # Left edge bolts
            bolt_across_positions.append(
                (panel_left + bolt_offset, i, "left"))
            # Right edge bolts
            bolt_across_positions.append(
                (panel_left + panel.width_mm - bolt_offset, i, "right"))

    else:  # portrait
        # In portrait: across = length_mm, along = width_mm
        # Purlin lines are at mounting hole positions.
        # Bolts are ON the purlin lines, so offset = 0 by definition.
        for i in range(panels_across):
            panel_left = edge_mm + i * (panel.length_mm + gap_mm)
            bolt_across_positions.append(
                (panel_left + panel.mount_hole_from_edge_mm, i, "rail1"))
            bolt_across_positions.append(
                (panel_left + panel.length_mm - panel.mount_hole_from_edge_mm,
                 i, "rail2"))

    # Now validate each bolt against the nearest purlin
    for bolt_pos, panel_idx, side in bolt_across_positions:
        # Find nearest purlin
        if not purlin_positions_mm:
            warnings.append(
                f"Panel {panel_idx+1} ({side}): no purlin positions to validate against")
            continue

        nearest_purlin = min(purlin_positions_mm, key=lambda p: abs(p - bolt_pos))
        offset = abs(bolt_pos - nearest_purlin)

        # Check 1: bolt must be within the purlin top flange
        if offset > half_flange:
            warnings.append(
                f"Panel {panel_idx+1} ({side}): bolt center is {_mm_to_in(offset):.2f}\" "
                f"from purlin center — outside the {PURLIN_TOP_FLANGE_IN}\" flange "
                f"(max {_mm_to_in(half_flange):.2f}\")")

        # Check 2: minimum edge clearance
        elif (half_flange - offset) < MIN_BOLT_EDGE_CLEARANCE_MM:
            clearance_in = _mm_to_in(half_flange - offset)
            warnings.append(
                f"Panel {panel_idx+1} ({side}): bolt is {clearance_in:.2f}\" from "
                f"purlin flange edge — less than {MIN_BOLT_EDGE_CLEARANCE_IN}\" minimum")

    # Check 3: bolt holes vs joint/overlap zones
    # This is an along-the-building check. Bolt inset from short edge:
    bolt_inset_mm = panel.mount_hole_inset_mm
    if purlin_type.upper() == "C":
        if bolt_inset_mm < C_PURLIN_JOINT_ZONE_MM:
            warnings.append(
                f"Bolt inset ({_mm_to_in(bolt_inset_mm):.1f}\") is within the "
                f"C-purlin butt joint zone ({_mm_to_in(C_PURLIN_JOINT_ZONE_MM):.1f}\"). "
                f"Verify bolts do not land on a purlin splice.")
    else:  # Z-purlin
        if bolt_inset_mm < Z_PURLIN_OVERLAP_ZONE_MM:
            warnings.append(
                f"Bolt inset ({_mm_to_in(bolt_inset_mm):.1f}\") is within the "
                f"Z-purlin overlap zone ({_mm_to_in(Z_PURLIN_OVERLAP_ZONE_MM):.1f}\"). "
                f"Verify bolts do not land on a purlin splice.")

    return warnings


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def calc_solar_layout(config: SolarLayoutConfig) -> SolarLayoutResult:
    """Calculate solar panel layout and building dimensions.

    This is the primary entry point for solar carport design. It:
      1. Determines building dimensions from the panel array (or fits panels
         into given dimensions).
      2. Computes purlin spacing dictated by the panel mounting requirements.
      3. Validates bolt hole positions against purlin geometry.
      4. Returns the complete layout including BOM-relevant quantities.

    Parameters:
        config: SolarLayoutConfig with panel specs, orientation, counts or
                available dimensions, and gap/clearance settings.

    Returns:
        SolarLayoutResult with building dims, purlin layout, bolt stacks,
        coverage, and any bolt hole validation warnings.

    Example:
        >>> cfg = SolarLayoutConfig(panels_across=5, panels_along=20)
        >>> result = calc_solar_layout(cfg)
        >>> print(f"{result.building_width_ft:.1f}' x {result.building_length_ft:.1f}'")
    """
    result = SolarLayoutResult()
    panel = config.panel
    orientation = config.orientation

    # Handle "compare" mode — delegate to comparison function
    if orientation == "compare":
        # For compare mode, default to landscape for the single-result return
        orientation = "landscape"

    result.orientation = orientation

    # ── Determine panel counts ──
    if config.mode == "fit_to_dims":
        avail_w_mm = _ft_to_mm(config.available_width_ft)
        avail_l_mm = _ft_to_mm(config.available_length_ft)

        panels_across, panels_along, dummy = _fit_panels_to_dims(
            avail_w_mm, avail_l_mm, panel, orientation,
            config.gap_width_in, config.gap_length_in,
            config.edge_clearance_in, config.endcap_clearance_in,
        )
        result.dummy_panels = dummy

        if panels_across == 0 or panels_along == 0:
            result.bolt_hole_warnings.append(
                "Available dimensions too small to fit any panels "
                f"in {orientation} orientation.")
            return result
    else:
        panels_across = config.panels_across
        panels_along = config.panels_along

    result.panels_across = panels_across
    result.panels_along = panels_along
    result.total_panels = panels_across * panels_along

    # ── Building dimensions ──
    width_mm, length_mm, dim_across, dim_along = _calc_building_dims_mm(
        panels_across, panels_along, panel, orientation,
        config.gap_width_in, config.gap_length_in,
        config.edge_clearance_in, config.endcap_clearance_in,
    )

    result.building_width_mm = width_mm
    result.building_length_mm = length_mm
    result.building_width_ft = _mm_to_ft(width_mm)
    result.building_length_ft = _mm_to_ft(length_mm)

    # ── Panel coverage ──
    panel_area_mm2 = panel.width_mm * panel.length_mm
    result.panel_coverage_sqft = result.total_panels * panel_area_mm2 * SQFT_PER_SQMM
    result.building_area_sqft = result.building_width_ft * result.building_length_ft

    # ── Purlin layout ──
    spacing_mm, n_purlin_lines, purlin_positions = _calc_purlin_layout(
        panels_across, panel, orientation,
        config.gap_width_in, config.edge_clearance_in,
    )

    result.purlin_spacing_mm = spacing_mm
    result.purlin_spacing_ft = _mm_to_ft(spacing_mm)
    result.n_purlin_lines = n_purlin_lines
    result.purlin_positions_mm = purlin_positions

    # ── Bolt stacks ──
    result.bolt_stacks = BOLT_STACKS_PER_PANEL * result.total_panels

    # ── Bolt hole validation ──
    result.bolt_hole_warnings = _validate_bolt_holes(
        purlin_positions, panel, orientation, panels_across,
        config.gap_width_in, config.edge_clearance_in,
        config.purlin_type,
    )

    return result


# ─────────────────────────────────────────────────────────────────────────────
# COMPARISON: ALL 4 COMBOS (L+C, L+Z, P+C, P+Z)
# ─────────────────────────────────────────────────────────────────────────────

def calc_solar_comparison(config: SolarLayoutConfig) -> Dict[str, Any]:
    """Run all 4 orientation+purlin-type combinations and rank by purlin LF.

    Combinations:
      - Landscape + C-purlin
      - Landscape + Z-purlin
      - Portrait  + C-purlin
      - Portrait  + Z-purlin

    Each combination produces a SolarLayoutResult. The results are sorted
    by total purlin linear feet (cheapest first, since purlin LF drives
    material cost).

    Parameters:
        config: SolarLayoutConfig. The orientation and purlin_type fields
                are overridden for each combination; all other fields are
                used as-is.

    Returns:
        dict with keys:
            "results": list of dicts, each containing:
                "label":        e.g. "Landscape + Z-purlin"
                "orientation":  "landscape" or "portrait"
                "purlin_type":  "C" or "Z"
                "layout":       SolarLayoutResult.to_dict()
                "purlin_total_lf": float  (n_purlin_lines * building_length_ft)
            "best": label of the cheapest option
            "config_used": summary of input config
    """
    combos = [
        ("Landscape + C-purlin", "landscape", "C"),
        ("Landscape + Z-purlin", "landscape", "Z"),
        ("Portrait + C-purlin",  "portrait",  "C"),
        ("Portrait + Z-purlin",  "portrait",  "Z"),
    ]

    results = []

    for label, orient, ptype in combos:
        # Build a per-combo config
        combo_cfg = SolarLayoutConfig(
            panel=config.panel,
            orientation=orient,
            panels_across=config.panels_across,
            panels_along=config.panels_along,
            gap_width_in=config.gap_width_in,
            gap_length_in=config.gap_length_in,
            edge_clearance_in=config.edge_clearance_in,
            endcap_clearance_in=config.endcap_clearance_in,
            mode=config.mode,
            available_width_ft=config.available_width_ft,
            available_length_ft=config.available_length_ft,
            purlin_type=ptype,
        )

        layout = calc_solar_layout(combo_cfg)

        # Total purlin LF = n_purlin_lines * building_length_ft
        # (each purlin line runs the full building length)
        purlin_total_lf = layout.n_purlin_lines * layout.building_length_ft

        results.append({
            "label": label,
            "orientation": orient,
            "purlin_type": ptype,
            "layout": layout.to_dict(),
            "purlin_total_lf": round(purlin_total_lf, 2),
        })

    # Sort by purlin total LF ascending (cheapest first)
    results.sort(key=lambda r: r["purlin_total_lf"])

    best_label = results[0]["label"] if results else "N/A"

    return {
        "results": results,
        "best": best_label,
        "config_used": {
            "mode": config.mode,
            "panels_across": config.panels_across,
            "panels_along": config.panels_along,
            "panel_width_mm": config.panel.width_mm,
            "panel_length_mm": config.panel.length_mm,
            "gap_width_in": config.gap_width_in,
            "gap_length_in": config.gap_length_in,
            "edge_clearance_in": config.edge_clearance_in,
            "endcap_clearance_in": config.endcap_clearance_in,
            "available_width_ft": config.available_width_ft,
            "available_length_ft": config.available_length_ft,
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# SOLAR HARDWARE BOM
# ─────────────────────────────────────────────────────────────────────────────

def solar_hardware_bom(layout: SolarLayoutResult) -> List[Dict[str, Any]]:
    """Generate solar-specific hardware BOM lines from a layout result.

    Returns a list of BOM line-item dicts ready for integration with
    calc/bom.py. Solar panels themselves are customer-supplied and appear
    as an informational line (zero material cost).

    Each bolt stack = 1 SS bolt + 1 flat washer + 1 star washer +
                      1 lock washer + 1 SS nut.
    """
    items = []

    # Solar panels — informational only
    items.append({
        "category": "solar",
        "item": "Solar Panels (customer-supplied)",
        "description": (
            f"{layout.total_panels} panels "
            f"({layout.panels_across} across x {layout.panels_along} along), "
            f"{layout.orientation} orientation"
        ),
        "qty": layout.total_panels,
        "unit": "ea",
        "unit_cost": 0.0,
        "total_cost": 0.0,
        "note": "Customer-supplied — not included in material cost",
    })

    # Stainless steel bolt stacks
    items.append({
        "category": "solar",
        "item": "SS Panel Mounting Bolt Stack",
        "description": (
            "Stainless steel bolt + flat washer + star washer + "
            "lock washer + nut (per mounting point)"
        ),
        "qty": layout.bolt_stacks,
        "unit": "ea",
        "unit_cost": 0.0,  # pricing TBD — to be set in defaults.py
        "total_cost": 0.0,
        "note": f"4 bolt stacks per panel x {layout.total_panels} panels",
    })

    return items
