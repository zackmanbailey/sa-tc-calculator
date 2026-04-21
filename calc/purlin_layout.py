"""
Purlin Piece-Break Engine — Shared by BOM and Interactive Builder
Implements PURLIN_RULES.md §2 (Piece Lengths), §7 (Angled), §8 (P1/P2 Plates)

Key rules:
  C-purlin: butt-joint at rafter center (4" each side), NO extension past rafter
  Z-purlin: 6' extension past rafter, 6" splice overlap, 8 tek screws per splice
  End pieces: 8" past end rafter center (4" endcap + 4" half-rafter) when no overhang
  Angled: adjusted_length = perpendicular_length / cos(angle_from_perpendicular)
  P1 plates: n_purlin_lines - 2 per rafter (perpendicular), n_purlin_lines (angled)
  P2 plates: 2 per rafter (perpendicular only), 0 if angled
"""

import math
from typing import List, Dict, Any, Optional, Tuple


# ─────────────────────────────────────────────────────────────────────────────
# DATA STRUCTURES
# ─────────────────────────────────────────────────────────────────────────────

class PurlinPieceGroup:
    """One group of identical purlin pieces."""
    __slots__ = ('label', 'length_in', 'qty_per_line', 'n_lines', 'total_qty',
                 'total_lf', 'is_end_piece', 'has_splice_holes')

    def __init__(self, label: str, length_in: float, qty_per_line: int,
                 n_lines: int, is_end_piece: bool = False,
                 has_splice_holes: bool = False):
        self.label = label
        self.length_in = round(length_in, 2)
        self.qty_per_line = qty_per_line
        self.n_lines = n_lines
        self.total_qty = qty_per_line * n_lines
        self.total_lf = round(self.total_qty * length_in / 12.0, 2)
        self.is_end_piece = is_end_piece
        self.has_splice_holes = has_splice_holes

    def to_dict(self) -> Dict[str, Any]:
        return {
            'label': self.label,
            'length_in': self.length_in,
            'length_ft_in': _fmt_ft_in(self.length_in),
            'qty_per_line': self.qty_per_line,
            'n_lines': self.n_lines,
            'total_qty': self.total_qty,
            'total_lf': self.total_lf,
            'is_end_piece': self.is_end_piece,
            'has_splice_holes': self.has_splice_holes,
        }


class PurlinLayoutResult:
    """Complete purlin layout for one building."""
    __slots__ = ('pieces', 'n_purlin_lines', 'purlin_type', 'total_lf',
                 'total_pieces', 'p1_per_rafter', 'p2_per_rafter',
                 'p1_total', 'p2_total', 'endcap_plates_per_rafter',
                 'endcap_plates_total', 'n_rafters', 'warnings', 'errors',
                 'angled', 'angle_from_perpendicular_deg')

    def __init__(self):
        self.pieces: List[PurlinPieceGroup] = []
        self.n_purlin_lines = 0
        self.purlin_type = "Z"
        self.total_lf = 0.0
        self.total_pieces = 0
        self.p1_per_rafter = 0
        self.p2_per_rafter = 0
        self.p1_total = 0
        self.p2_total = 0
        self.endcap_plates_per_rafter = 0
        self.endcap_plates_total = 0
        self.n_rafters = 0
        self.warnings: List[str] = []
        self.errors: List[str] = []
        self.angled = False
        self.angle_from_perpendicular_deg = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'pieces': [p.to_dict() for p in self.pieces],
            'n_purlin_lines': self.n_purlin_lines,
            'purlin_type': self.purlin_type,
            'total_lf': round(self.total_lf, 2),
            'total_pieces': self.total_pieces,
            'p1_per_rafter': self.p1_per_rafter,
            'p2_per_rafter': self.p2_per_rafter,
            'p1_total': self.p1_total,
            'p2_total': self.p2_total,
            'endcap_plates_per_rafter': self.endcap_plates_per_rafter,
            'endcap_plates_total': self.endcap_plates_total,
            'n_rafters': self.n_rafters,
            'warnings': self.warnings,
            'errors': self.errors,
            'angled': self.angled,
            'angle_from_perpendicular_deg': self.angle_from_perpendicular_deg,
        }


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _fmt_ft_in(total_in: float) -> str:
    """Format inches as ft'-in\" string, e.g. 224.0 → \"18'-8\\\"\"."""
    ft = int(total_in // 12)
    inches = total_in - ft * 12
    if abs(inches) < 0.01:
        return f"{ft}'-0\""
    return f"{ft}'-{inches:.1f}\"".rstrip('0').rstrip('.')  + '"' if '"' not in f"{inches:.1f}" else f"{ft}'-{inches:.1f}\""


def _fmt_ft_in(total_in: float) -> str:
    """Format inches as ft'-in\" string, e.g. 224.0 → \"18'-8\\\"\"."""
    ft = int(total_in // 12)
    inches = round(total_in - ft * 12, 2)
    if abs(inches) < 0.01:
        return f"{ft}'-0\""
    # Clean trailing zeros
    in_str = f"{inches:g}"
    return f"{ft}'-{in_str}\""


def _rafter_positions_in(bay_sizes_ft: List[float]) -> List[float]:
    """
    Convert bay sizes to rafter center positions in INCHES from building start.
    First rafter is at position 0.
    """
    positions = [0.0]
    cumulative = 0.0
    for bay_ft in bay_sizes_ft:
        cumulative += bay_ft * 12.0
        positions.append(round(cumulative, 4))
    return positions


# ─────────────────────────────────────────────────────────────────────────────
# MAIN PIECE-BREAK ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def calc_purlin_pieces(
    bay_sizes_ft: List[float],
    n_purlin_lines: int,
    purlin_type: str = "Z",
    max_purlin_length_ft: float = 45.0,
    z_extension_ft: float = 6.0,
    splice_overlap_in: float = 6.0,
    end_extension_in: float = 8.0,
    overhang_ft: float = 0.0,
    angled_purlins: bool = False,
    purlin_angle_deg: float = 90.0,
    n_rafters: int = 0,
    has_rafter_splice: bool = False,
) -> PurlinLayoutResult:
    """
    Calculate purlin piece breaks for a building.

    Parameters:
        bay_sizes_ft: List of bay sizes in feet (e.g., [18.0, 18.0, 18.0])
        n_purlin_lines: Number of purlin lines across the building width
        purlin_type: "Z" or "C"
        max_purlin_length_ft: Maximum single piece length (default 45', hard cap 53')
        z_extension_ft: Z-purlin extension past rafter (default 6')
        splice_overlap_in: Z-purlin overlap at splice (default 6")
        end_extension_in: End piece extension past end rafter center (default 8")
        overhang_ft: Overhang distance past end rafters (0 = none)
        angled_purlins: Whether purlins are angled
        purlin_angle_deg: Angle from drive aisle (90 = perpendicular to rafter)
        n_rafters: Number of rafters (if 0, calculated from bay_sizes)
        has_rafter_splice: Whether rafter is spliced (affects P2 plate count)

    Returns:
        PurlinLayoutResult with piece groups, plate counts, and warnings
    """
    result = PurlinLayoutResult()
    result.purlin_type = purlin_type.upper()
    result.n_purlin_lines = n_purlin_lines

    # Clamp max length to hard cap
    max_purlin_length_ft = min(max_purlin_length_ft, 53.0)
    max_length_in = max_purlin_length_ft * 12.0

    # Rafter positions
    rafter_pos_in = _rafter_positions_in(bay_sizes_ft)
    n_rft = len(rafter_pos_in)
    result.n_rafters = n_rafters if n_rafters > 0 else n_rft
    n_bays = n_rft - 1

    if n_bays < 1:
        result.errors.append("Need at least 2 rafters (1 bay)")
        return result

    # Validate bay sizes vs max purlin length
    for i, bay_ft in enumerate(bay_sizes_ft):
        if bay_ft * 12.0 > max_length_in:
            result.errors.append(
                f"Bay {i+1} ({bay_ft:.1f}') exceeds max purlin length "
                f"({max_purlin_length_ft:.0f}'). Add intermediate rafters.")
            return result

    # Calculate angle adjustment
    angle_from_perp = 0.0
    if angled_purlins and purlin_angle_deg != 90.0:
        # purlin_angle_deg is from drive aisle (which is along building length)
        # angle from perpendicular = 90 - purlin_angle_deg
        angle_from_perp = abs(90.0 - purlin_angle_deg)
        result.angled = True
        result.angle_from_perpendicular_deg = angle_from_perp

    cos_factor = math.cos(math.radians(angle_from_perp)) if angle_from_perp > 0 else 1.0

    # ── Determine piece-break pattern ──
    if result.purlin_type == "C":
        pieces = _calc_c_purlin_pieces(
            bay_sizes_ft, rafter_pos_in, max_length_in,
            end_extension_in, overhang_ft, cos_factor, n_purlin_lines)
    else:
        pieces = _calc_z_purlin_pieces(
            bay_sizes_ft, rafter_pos_in, max_length_in,
            z_extension_ft, splice_overlap_in, end_extension_in,
            overhang_ft, cos_factor, n_purlin_lines)

    result.pieces = pieces

    # Sum totals
    result.total_lf = sum(p.total_lf for p in pieces)
    result.total_pieces = sum(p.total_qty for p in pieces)

    # ── P1 / P2 Plate Counts (per PURLIN_RULES.md §8) ──
    if angled_purlins and purlin_angle_deg != 90.0:
        # Angled: ALL positions get P1, no P2. Plus 2 endcap plates per rafter.
        result.p1_per_rafter = n_purlin_lines
        result.p2_per_rafter = 0
        result.endcap_plates_per_rafter = 2
    else:
        # Perpendicular: P1 at interior, P2 at eave
        result.p1_per_rafter = max(0, n_purlin_lines - 2)
        result.p2_per_rafter = 2
        # Exception: no P2 where rafter splice plate exists
        if has_rafter_splice:
            result.p2_per_rafter = max(0, result.p2_per_rafter - 1)
        result.endcap_plates_per_rafter = 0

    result.p1_total = result.p1_per_rafter * result.n_rafters
    result.p2_total = result.p2_per_rafter * result.n_rafters
    result.endcap_plates_total = result.endcap_plates_per_rafter * result.n_rafters

    # ── Warnings ──
    for p in pieces:
        if p.length_in < 96.0:  # 8' minimum
            result.warnings.append(
                f"Purlin piece '{p.label}' is {_fmt_ft_in(p.length_in)} "
                f"(less than 8'). Consider adjusting bay sizes.")

    return result


# ─────────────────────────────────────────────────────────────────────────────
# C-PURLIN PIECE BREAK
# ─────────────────────────────────────────────────────────────────────────────

def _calc_c_purlin_pieces(
    bay_sizes_ft: List[float],
    rafter_pos_in: List[float],
    max_length_in: float,
    end_extension_in: float,
    overhang_ft: float,
    cos_factor: float,
    n_purlin_lines: int,
) -> List[PurlinPieceGroup]:
    """
    C-purlin piece breaks. Butt-joint at rafter centers.
    Each piece sits 4" on each rafter at a joint.
    End pieces: +8" past end rafter center (4" endcap + 4" half-rafter).
    """
    n_bays = len(bay_sizes_ft)

    # Figure out how many bays each piece can span
    # Try to maximize piece length, breaking symmetrically
    piece_pattern = _find_optimal_piece_pattern(bay_sizes_ft, max_length_in)

    pieces = []
    bay_idx = 0

    for i, n_span_bays in enumerate(piece_pattern):
        is_first = (i == 0)
        is_last = (i == len(piece_pattern) - 1)

        # Base length = sum of bays this piece spans
        span_in = sum(bay_sizes_ft[bay_idx:bay_idx + n_span_bays]) * 12.0

        # End extensions
        if is_first:
            if overhang_ft > 0:
                span_in += overhang_ft * 12.0
            else:
                span_in += end_extension_in  # 8" past end rafter center
        if is_last:
            if overhang_ft > 0:
                span_in += overhang_ft * 12.0
            else:
                span_in += end_extension_in  # 8" past end rafter center

        # Apply angle adjustment
        adjusted_in = span_in / cos_factor if cos_factor < 1.0 else span_in

        is_end = is_first or is_last
        label = "End Piece" if is_end else "Middle Piece"
        if len(piece_pattern) == 1:
            label = "Full Length"

        pieces.append(PurlinPieceGroup(
            label=f"{label} ({_fmt_ft_in(adjusted_in)})",
            length_in=adjusted_in,
            qty_per_line=1,
            n_lines=n_purlin_lines,
            is_end_piece=is_end,
        ))

        bay_idx += n_span_bays

    # Merge identical pieces (same length within 0.1")
    return _merge_piece_groups(pieces)


# ─────────────────────────────────────────────────────────────────────────────
# Z-PURLIN PIECE BREAK
# ─────────────────────────────────────────────────────────────────────────────

def _calc_z_purlin_pieces(
    bay_sizes_ft: List[float],
    rafter_pos_in: List[float],
    max_length_in: float,
    z_extension_ft: float,
    splice_overlap_in: float,
    end_extension_in: float,
    overhang_ft: float,
    cos_factor: float,
    n_purlin_lines: int,
) -> List[PurlinPieceGroup]:
    """
    Z-purlin piece breaks. Pieces extend past rafter by z_extension.
    6" overlap where two Z-purlins meet (boxed beam splice).
    End pieces: +8" past end rafter center.
    """
    z_ext_in = z_extension_ft * 12.0
    n_bays = len(bay_sizes_ft)

    # For Z-purlins, each piece spans some bays plus extensions on each side
    # The extension counts toward the total piece length
    piece_pattern = _find_optimal_piece_pattern_z(
        bay_sizes_ft, max_length_in, z_ext_in, splice_overlap_in,
        end_extension_in, overhang_ft)

    pieces = []
    bay_idx = 0

    for i, n_span_bays in enumerate(piece_pattern):
        is_first = (i == 0)
        is_last = (i == len(piece_pattern) - 1)

        # Base span = sum of bays
        span_in = sum(bay_sizes_ft[bay_idx:bay_idx + n_span_bays]) * 12.0

        # Add extensions
        if is_first and is_last:
            # Single piece spans entire building — end extension both sides
            if overhang_ft > 0:
                span_in += overhang_ft * 12.0 * 2
            else:
                span_in += end_extension_in * 2  # 8" each end
        elif is_first:
            # Left end: endcap extension or overhang
            if overhang_ft > 0:
                span_in += overhang_ft * 12.0
            else:
                span_in += end_extension_in
            # Right side: Z-extension past the last rafter this piece touches
            span_in += z_ext_in
        elif is_last:
            # Left side: Z-extension past the first rafter this piece touches
            span_in += z_ext_in
            # Right end: endcap extension or overhang
            if overhang_ft > 0:
                span_in += overhang_ft * 12.0
            else:
                span_in += end_extension_in
        else:
            # Middle piece: Z-extension on both sides
            span_in += 2 * z_ext_in

        # Apply angle adjustment
        adjusted_in = span_in / cos_factor if cos_factor < 1.0 else span_in

        has_splice = not is_first and not is_last
        is_end = is_first or is_last
        label = "End Piece" if is_end else "Middle Piece"
        if len(piece_pattern) == 1:
            label = "Full Length"

        pieces.append(PurlinPieceGroup(
            label=f"{label} ({_fmt_ft_in(adjusted_in)})",
            length_in=adjusted_in,
            qty_per_line=1,
            n_lines=n_purlin_lines,
            is_end_piece=is_end,
            has_splice_holes=not is_first,  # all but first have splice on left
        ))

        bay_idx += n_span_bays

    return _merge_piece_groups(pieces)


# ─────────────────────────────────────────────────────────────────────────────
# OPTIMAL PIECE PATTERN FINDING
# ─────────────────────────────────────────────────────────────────────────────

def _find_optimal_piece_pattern(
    bay_sizes_ft: List[float],
    max_length_in: float,
) -> List[int]:
    """
    Find optimal piece-break pattern for C-purlins.
    Returns list of how many bays each piece spans.
    Tries to maximize piece length while keeping under max_length_in.
    Prefers symmetric patterns (same end pieces).
    """
    n_bays = len(bay_sizes_ft)

    if n_bays == 0:
        return []

    # Check if single piece works (all bays in one)
    total_in = sum(b * 12 for b in bay_sizes_ft) + 16.0  # +16" for both end extensions
    if total_in <= max_length_in:
        return [n_bays]

    # Greedy from both ends toward center
    # Try to make symmetric end pieces
    best_pattern = _greedy_piece_pattern(bay_sizes_ft, max_length_in)
    return best_pattern


def _greedy_piece_pattern(
    bay_sizes_ft: List[float],
    max_length_in: float,
) -> List[int]:
    """Greedy left-to-right piece allocation for C-purlins."""
    n_bays = len(bay_sizes_ft)
    pattern = []
    idx = 0

    while idx < n_bays:
        is_first = (idx == 0)
        # How many bays can this piece span?
        span = 0
        running_in = 0.0

        for j in range(idx, n_bays):
            add_in = bay_sizes_ft[j] * 12.0
            candidate_in = running_in + add_in

            # Always add left-end extension for first piece
            total_test = candidate_in
            if is_first:
                total_test += 8.0  # left end extension always present
            # Add right-end extension if this would be the last bay in the building
            remaining_after = n_bays - (j + 1)
            if remaining_after == 0:
                total_test += 8.0  # right end extension

            if span > 0 and total_test > max_length_in:
                break
            running_in += add_in
            span += 1
            # Also check if taking this bay already exceeds (for span==1 case)
            if total_test > max_length_in and span == 1:
                break  # forced to take 1 bay even if over max

        if span == 0:
            span = 1  # Must take at least 1 bay

        pattern.append(span)
        idx += span

    return pattern


def _find_optimal_piece_pattern_z(
    bay_sizes_ft: List[float],
    max_length_in: float,
    z_ext_in: float,
    splice_overlap_in: float,
    end_extension_in: float,
    overhang_ft: float,
) -> List[int]:
    """
    Find optimal piece-break pattern for Z-purlins.
    Z-purlins extend past rafters, so total piece length includes extensions.
    """
    n_bays = len(bay_sizes_ft)
    if n_bays == 0:
        return []

    # Check if single piece works
    ovh_in = overhang_ft * 12.0 if overhang_ft > 0 else end_extension_in
    total_in = sum(b * 12 for b in bay_sizes_ft) + ovh_in * 2
    if total_in <= max_length_in:
        return [n_bays]

    # Greedy allocation considering Z-extensions
    pattern = []
    idx = 0

    while idx < n_bays:
        is_first = (idx == 0)
        span = 0
        running_in = 0.0

        for j in range(idx, n_bays):
            add_in = bay_sizes_ft[j] * 12.0
            test_in = running_in + add_in

            # Left end
            if is_first and span == 0:
                left_ext = ovh_in
            else:
                left_ext = z_ext_in

            # Right end
            if j == n_bays - 1:
                right_ext = ovh_in
            else:
                right_ext = z_ext_in

            test_total = test_in + left_ext + right_ext

            if span > 0 and test_total > max_length_in:
                break
            running_in += add_in
            span += 1

        if span == 0:
            span = 1

        pattern.append(span)
        idx += span

    return pattern


# ─────────────────────────────────────────────────────────────────────────────
# MERGE IDENTICAL PIECES
# ─────────────────────────────────────────────────────────────────────────────

def _merge_piece_groups(pieces: List[PurlinPieceGroup]) -> List[PurlinPieceGroup]:
    """
    Merge pieces with identical lengths into single groups.
    This is what turns "End Piece x1, Middle Piece x1, End Piece x1"
    into "End Piece x2, Middle Piece x1" for BOM display.
    """
    if not pieces:
        return []

    merged = {}
    for p in pieces:
        key = round(p.length_in, 1)
        if key in merged:
            existing = merged[key]
            existing.qty_per_line += p.qty_per_line
            existing.total_qty = existing.qty_per_line * existing.n_lines
            existing.total_lf = round(existing.total_qty * existing.length_in / 12.0, 2)
            if p.has_splice_holes:
                existing.has_splice_holes = True
        else:
            merged[key] = PurlinPieceGroup(
                label=p.label,
                length_in=p.length_in,
                qty_per_line=p.qty_per_line,
                n_lines=p.n_lines,
                is_end_piece=p.is_end_piece,
                has_splice_holes=p.has_splice_holes,
            )

    # Sort by length descending
    return sorted(merged.values(), key=lambda x: -x.length_in)


# ─────────────────────────────────────────────────────────────────────────────
# RAFTER LENGTH ADJUSTMENT FOR Z-PURLINS
# ─────────────────────────────────────────────────────────────────────────────

def calc_rafter_cut_length(
    width_ft: float,
    roofing_overhang_ft: float = 0.5,
    purlin_type: str = "Z",
    z_eave_overhang_in: float = 3.5,
) -> float:
    """
    Rafter cut length in feet, accounting for purlin type.
    C-purlin: rafter = building width - 2 × roofing_overhang
    Z-purlin: rafter = building width - 2 × roofing_overhang - 2 × z_eave_overhang
    """
    cut_ft = width_ft - 2.0 * roofing_overhang_ft
    if purlin_type.upper() == "Z":
        cut_ft -= 2.0 * z_eave_overhang_in / 12.0
    return round(cut_ft, 4)


# ─────────────────────────────────────────────────────────────────────────────
# BOM SUMMARY HELPER
# ─────────────────────────────────────────────────────────────────────────────

def purlin_bom_summary(layout: PurlinLayoutResult, lbs_per_ft: float = 7.43,
                       cost_per_lb: float = 0.82) -> Dict[str, Any]:
    """
    Generate BOM-ready summary from a PurlinLayoutResult.
    Returns dict with line items for each piece length group plus plates.
    """
    cost_per_ft = lbs_per_ft * cost_per_lb
    items = []

    for pg in layout.pieces:
        items.append({
            'description': f"Purlin {pg.label}",
            'length_ft_in': _fmt_ft_in(pg.length_in),
            'length_ft': round(pg.length_in / 12.0, 2),
            'qty': pg.total_qty,
            'total_lf': pg.total_lf,
            'weight_lbs': round(pg.total_lf * lbs_per_ft, 1),
            'cost': round(pg.total_lf * cost_per_ft, 2),
            'has_splice_holes': pg.has_splice_holes,
        })

    return {
        'purlin_items': items,
        'total_lf': layout.total_lf,
        'total_pieces': layout.total_pieces,
        'total_weight_lbs': round(layout.total_lf * lbs_per_ft, 1),
        'total_cost': round(layout.total_lf * cost_per_ft, 2),
        'p1_plates': layout.p1_total,
        'p2_plates': layout.p2_total,
        'endcap_plates': layout.endcap_plates_total,
    }
