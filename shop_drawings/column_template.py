"""
Column Shop Drawing — Template Overlay Approach
Uses the Skyline Steel SF21-464-C1 PDF as a base template.
White-boxes dynamic text regions and stamps new values on top.

Template PDF: Stored as 792×1224 (portrait) with Rotate=270 to display as landscape.
pdfplumber coordinates are in the DISPLAYED space (1224×792, y=0 at top).

COORDINATE TRANSFORM:
  The raw PDF is 792×1224 with 270° rotation.
  To convert pdfplumber coords → raw canvas coords:
    raw_x = pdfplumber_top
    raw_y = pdfplumber_x
  Text must be drawn rotated 90° CCW on the raw canvas so it appears
  horizontal after the page's 270° rotation is applied.
"""

import io
import os
import math
import datetime
from typing import Dict, Optional

from pypdf import PdfReader, PdfWriter
from reportlab.lib.units import inch
from reportlab.lib.colors import black, white, HexColor
from reportlab.pdfgen import canvas

from shop_drawings.config import WPS_CODES

TEMPLATE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PDF = os.path.join(TEMPLATE_DIR, "templates", "skyline_c1_template.pdf")

# Pitch-variant templates
PITCH_TEMPLATES = {
    1.2: os.path.join(TEMPLATE_DIR, "templates", "skyline_c1_template.pdf"),
    5:   os.path.join(TEMPLATE_DIR, "templates", "skyline_c1_template_5deg.pdf"),
    10:  os.path.join(TEMPLATE_DIR, "templates", "skyline_c1_template_10deg.pdf"),
    15:  os.path.join(TEMPLATE_DIR, "templates", "skyline_c1_template_15deg.pdf"),
}

def _select_template(pitch_deg):
    """Select the closest pitch template for the given roof pitch."""
    available = sorted(PITCH_TEMPLATES.keys())
    closest = min(available, key=lambda p: abs(p - pitch_deg))
    return PITCH_TEMPLATES[closest]

# Raw page dimensions (before rotation)
RAW_W = 792.0
RAW_H = 1224.0

# Display dimensions (after 270° rotation)
DISP_W = 1224.0
DISP_H = 792.0


def _fmt_ft_in(total_inches: float) -> str:
    """Format total inches as ft'-in" string."""
    ft = int(total_inches // 12)
    inch_val = total_inches - ft * 12
    eighths = round(inch_val * 8) / 8
    if eighths >= 12:
        ft += 1
        eighths -= 12
    if eighths == int(eighths):
        return f"{ft}'-{int(eighths)}\""
    num = int(eighths * 8)
    den = 8
    while num % 2 == 0 and den > 1:
        num //= 2
        den //= 2
    whole = int(eighths)
    frac_num = num - whole * den if whole else num
    if whole:
        return f"{ft}'-{whole} {frac_num}/{den}\""
    return f"{ft}'-{frac_num}/{den}\""


# ═══════════════════════════════════════════════════════════════════════════════
# COORDINATE TRANSFORMS
# ═══════════════════════════════════════════════════════════════════════════════

def _pdfp_to_raw(pdfp_x, pdfp_top):
    """Convert pdfplumber display coords to raw PDF canvas coords.

    PDF Rotate=270 means 270° CLOCKWISE for display.
    Raw page is 792×1224 (W×H).
    Display: 1224×792.

    Forward (raw → display):
      display_x = RAW_H - raw_y
      display_y = raw_x
      pdfp_x   = RAW_H - raw_y
      pdfp_top  = DISP_H - raw_x  = RAW_W - raw_x

    Inverse (pdfplumber → raw):
      raw_x = RAW_W  - pdfp_top
      raw_y = RAW_H  - pdfp_x
    """
    raw_x = RAW_W - pdfp_top
    raw_y = RAW_H - pdfp_x
    return raw_x, raw_y


# ═══════════════════════════════════════════════════════════════════════════════
# WHITEBOX REGIONS — defined in pdfplumber coords (x0, y_top, x1, y_bottom)
# ═══════════════════════════════════════════════════════════════════════════════

REGIONS = {
    # ── Title line: "35 - COLUMNS - C1 (CP-1,CP-2A,...)" ──
    "title_line": (305, 290, 760, 315),

    # ── Column descriptions (upper area near front/side views) ──
    "col_desc_main": (435, 102, 620, 125),
    "col_desc_secondary": (475, 134, 582, 155),

    # ── Rebar callout: "#9 REBAR 24'-6"" ──
    "dim_rebar_callout": (875, 148, 980, 170),

    # ── Side view "rb7" label ──
    "pm_rb_sideview": (1028, 178, 1050, 196),

    # ── ENTIRE BOTTOM-RIGHT + TITLE BLOCK (one big region) ──
    # Covers BOM area through the right margin title block strip
    "bottom_right_all": (655, 482, 1220, 795),

    # ── Piece mark "rb7" near B-B section ──
    "pm_rb_bb": (110, 594, 148, 620),

    # ── "rb7" and "TYP" text below B-B (just the label area) ──
    "pm_rb_bb_typ": (85, 610, 148, 638),
}


# ═══════════════════════════════════════════════════════════════════════════════
# DRAWING HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

class TemplateOverlay:
    """Helper to draw on the raw canvas with pdfplumber-coord convenience."""

    def __init__(self, canvas_obj):
        self.c = canvas_obj

    def whitebox(self, region_name):
        """White out a region defined in pdfplumber coords."""
        if region_name not in REGIONS:
            return
        px0, py_top, px1, py_bot = REGIONS[region_name]
        # Convert all four corners to raw, then take the bounding box
        raw_x = RAW_W - py_bot      # min raw_x  (bottom of region → smaller raw_x)
        raw_y = RAW_H - px1         # min raw_y  (right edge → smaller raw_y)
        raw_w = py_bot - py_top     # width in raw space
        raw_h = px1 - px0           # height in raw space
        self.c.setFillColor(white)
        self.c.setStrokeColor(white)
        self.c.rect(raw_x, raw_y, raw_w, raw_h, fill=1, stroke=0)

    def text(self, region_name, text_str, font="Helvetica", size=10,
             bold=False, centered=False, x_offset=0, y_offset=0):
        """Stamp horizontal text in a region (appears horizontal in display).

        After rotate(270) on the raw canvas:
          local +x  →  raw -y  →  display right   (text reading direction)
          local +y  →  raw +x  →  display up       (ascender direction)
        Combined with page Rotate=270 CW, text appears at 0° in display.
        """
        if region_name not in REGIONS:
            return
        px0, py_top, px1, py_bot = REGIONS[region_name]

        # Text anchor in pdfplumber coords
        if centered:
            pdfp_x = (px0 + px1) / 2
        else:
            pdfp_x = px0 + 2
        # Vertical center of region, shifted down by ~half ascent for baseline
        pdfp_top = (py_top + py_bot) / 2 + size * 0.35

        pdfp_x += x_offset
        pdfp_top += y_offset

        # Convert to raw coords
        raw_x, raw_y = _pdfp_to_raw(pdfp_x, pdfp_top)

        # Draw text rotated 270° CCW to cancel page's 270° CW rotation
        fname = f"{font}-Bold" if bold else font
        self.c.saveState()
        self.c.translate(raw_x, raw_y)
        self.c.rotate(270)
        self.c.setFont(fname, size)
        self.c.setFillColor(black)
        if centered:
            self.c.drawCentredString(0, 0, text_str)
        else:
            self.c.drawString(0, 0, text_str)
        self.c.restoreState()

    def text_at(self, pdfp_x, pdfp_top, text_str, font="Helvetica", size=8,
                bold=False, color=black):
        """Stamp text at exact pdfplumber coordinates."""
        raw_x, raw_y = _pdfp_to_raw(pdfp_x, pdfp_top)
        fname = f"{font}-Bold" if bold else font
        self.c.saveState()
        self.c.translate(raw_x, raw_y)
        self.c.rotate(270)
        self.c.setFont(fname, size)
        self.c.setFillColor(color)
        self.c.drawString(0, 0, text_str)
        self.c.restoreState()

    def text_rotated_90cw(self, region_name, text_str, font="Helvetica",
                          size=8, bold=False):
        """Stamp text that reads bottom-to-top in display (title block style)."""
        if region_name not in REGIONS:
            return
        px0, py_top, px1, py_bot = REGIONS[region_name]
        pdfp_x = (px0 + px1) / 2
        pdfp_top = py_bot - 2
        raw_x, raw_y = _pdfp_to_raw(pdfp_x, pdfp_top)
        fname = f"{font}-Bold" if bold else font
        self.c.saveState()
        self.c.translate(raw_x, raw_y)
        self.c.setFont(fname, size)
        self.c.setFillColor(black)
        self.c.drawString(0, 0, text_str)
        self.c.restoreState()

    # ── Drawing primitives in pdfplumber coords ──

    def whitebox_at(self, px0, py_top, px1, py_bot):
        """White out an arbitrary rectangle given pdfplumber coords."""
        raw_x = RAW_W - py_bot
        raw_y = RAW_H - px1
        raw_w = py_bot - py_top
        raw_h = px1 - px0
        self.c.setFillColor(white)
        self.c.setStrokeColor(white)
        self.c.rect(raw_x, raw_y, raw_w, raw_h, fill=1, stroke=0)

    def line_at(self, px0, pt0, px1, pt1, width=0.5, color=black):
        """Draw a line between two pdfplumber points."""
        rx0, ry0 = _pdfp_to_raw(px0, pt0)
        rx1, ry1 = _pdfp_to_raw(px1, pt1)
        self.c.saveState()
        self.c.setStrokeColor(color)
        self.c.setLineWidth(width)
        self.c.line(rx0, ry0, rx1, ry1)
        self.c.restoreState()

    def rect_at(self, px, py_top, pw, ph, fill_color=None, stroke_color=black,
                stroke_width=0.5):
        """Draw a rectangle. px,py_top = top-left in display, pw=width, ph=height."""
        # Bottom-right in pdfplumber: (px+pw, py_top+ph)
        raw_x = RAW_W - (py_top + ph)
        raw_y = RAW_H - (px + pw)
        raw_w = ph       # display height → raw width
        raw_h = pw       # display width → raw height
        self.c.saveState()
        if fill_color:
            self.c.setFillColor(fill_color)
        self.c.setStrokeColor(stroke_color)
        self.c.setLineWidth(stroke_width)
        if fill_color:
            self.c.rect(raw_x, raw_y, raw_w, raw_h, fill=1, stroke=1)
        else:
            self.c.rect(raw_x, raw_y, raw_w, raw_h, fill=0, stroke=1)
        self.c.restoreState()

    def text_centered_at(self, pdfp_x, pdfp_top, text_str,
                         font="Helvetica", size=8, bold=False, color=black):
        """Draw centered text at exact pdfplumber coordinates."""
        raw_x, raw_y = _pdfp_to_raw(pdfp_x, pdfp_top)
        fname = f"{font}-Bold" if bold else font
        self.c.saveState()
        self.c.translate(raw_x, raw_y)
        self.c.rotate(270)
        self.c.setFont(fname, size)
        self.c.setFillColor(color)
        self.c.drawCentredString(0, 0, text_str)
        self.c.restoreState()

    def text_right_at(self, pdfp_x, pdfp_top, text_str,
                      font="Helvetica", size=8, bold=False, color=black):
        """Draw right-aligned text at exact pdfplumber coordinates."""
        raw_x, raw_y = _pdfp_to_raw(pdfp_x, pdfp_top)
        fname = f"{font}-Bold" if bold else font
        self.c.saveState()
        self.c.translate(raw_x, raw_y)
        self.c.rotate(270)
        self.c.setFont(fname, size)
        self.c.setFillColor(color)
        self.c.drawRightString(0, 0, text_str)
        self.c.restoreState()

    def text_btop_at(self, pdfp_x, pdfp_top, text_str,
                     font="Helvetica", size=8, bold=False, color=black):
        """Draw bottom-to-top text at exact coordinates.
        Text starts at (pdfp_x, pdfp_top) and reads upward (toward smaller y).
        No rotation on raw canvas — page's 270° CW makes +raw_x = display up.
        """
        raw_x, raw_y = _pdfp_to_raw(pdfp_x, pdfp_top)
        fname = f"{font}-Bold" if bold else font
        self.c.saveState()
        self.c.translate(raw_x, raw_y)
        self.c.setFont(fname, size)
        self.c.setFillColor(color)
        self.c.drawString(0, 0, text_str)
        self.c.restoreState()

    def text_btop_centered_at(self, pdfp_x, pdfp_top, text_str,
                              font="Helvetica", size=8, bold=False, color=black):
        """Draw bottom-to-top text, centered at the given point.
        Useful for centering vertically-oriented text in a cell.
        """
        raw_x, raw_y = _pdfp_to_raw(pdfp_x, pdfp_top)
        fname = f"{font}-Bold" if bold else font
        self.c.saveState()
        self.c.translate(raw_x, raw_y)
        self.c.setFont(fname, size)
        self.c.setFillColor(color)
        self.c.drawCentredString(0, 0, text_str)
        self.c.restoreState()


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN GENERATION FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════════════
# BOTTOM-RIGHT SECTION: BOM TABLE + NOTES + DATES + DESIGN AUTHORITY
# Drawn entirely from scratch on the overlay canvas.
# All coordinates are in pdfplumber display space (1224×792, y=0 at top).
# ═══════════════════════════════════════════════════════════════════════════════

# Colors
CLR_HEADER_BG = HexColor("#333333")    # Dark header row
CLR_ROW_ALT = HexColor("#F0F0F0")      # Alternating row fill
CLR_GRID = HexColor("#999999")          # Grid lines

def _draw_bottom_right(ov, cfg, data, mark, total_cols, cee_size,
                       cee_qty, cap_qty, gusset_qty, rebar_total,
                       pm_cap, pm_gusset_up, pm_gusset_dn, pm_rebar,
                       cee_ft, cee_in, cap_plate_ft, cap_plate_in, gusset_leg,
                       cee_weight_total, cap_weight_total,
                       gusset_weight_total, rebar_weight_total,
                       total_weight, rebar_ft, rebar_in):
    """Draw the entire bottom-right block.

    Layout (pdfplumber coords, all horizontal text):
      ┌─────────────────────────────────────────────────────────────────┐
      │  BIG BANNER: Job Name + "15 - Columns - C1" (full width)       │
      ├───────────────────────┬─────────────────────────────────────────┤
      │  Notes (left)         │  BOM Table (right)                     │
      │  PROJECT SPECIFIC     │  BILL OF MATERIALS                     │
      │  NOTES + WPS CODES    │  ┌ headers + data rows ──────────────┐ │
      │                       │  └────────────────────────────────────┘ │
      ├───────────────────────┴─────────────────────────────────────────┤
      │  Title Block (full width: x=658..1214)                          │
      │  Company | Project Info | COLUMN C1 | Rev History               │
      └────────────────────────────────────────────────────────────────┘
    """

    today = datetime.date.today().strftime("%m/%d/%Y")
    project_name = getattr(cfg, 'project_name', 'Project').upper()
    customer_name = getattr(cfg, 'customer_name', 'Customer')
    job_code = getattr(cfg, 'job_code', '0000-0000')

    # Overall bounds of the whiteboxed region
    BL = 658;  BR = 1214
    BT = 488;  BB = 793
    BW = BR - BL   # 556
    BM = (BL + BR) / 2  # horizontal center

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TOP BANNER: Job name + column description (full width, big text)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    BANNER_H = 38
    BANNER_BOT = BT + BANNER_H

    ov.rect_at(BL, BT, BW, BANNER_H, stroke_color=black, stroke_width=0.8)

    # Job name on top line
    ov.text_centered_at(BM, BT + 13, project_name, size=12, bold=True)
    # Column description on second line
    col_title = f"{total_cols} - Columns - {mark}"
    ov.text_centered_at(BM, BT + 28, col_title, size=12, bold=True)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # MIDDLE: Notes (left) + BOM (right)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    SPLIT_X = 830
    TOP_BOT = 645   # Where the notes+BOM ends and title block begins

    # ── Notes (left: x=658..830) ──
    NL = BL;  NR = SPLIT_X
    NT = BANNER_BOT;  NB_notes = TOP_BOT
    NW = NR - NL
    NX = NL + 4
    ny = NT + 10

    ov.rect_at(NL, NT, NW, NB_notes - NT, stroke_color=black, stroke_width=0.5)
    ov.text_at(NX, ny, "PROJECT SPECIFIC NOTES (UNO):", size=5, bold=True)
    ny += 7
    ov.text_at(NX + 2, ny, cfg.col_material_grade, size=4)

    ny += 10
    ov.text_at(NX, ny, "MATERIAL:", size=5, bold=True)
    ov.text_at(NX + 44, ny, "A36 UNO", size=5, bold=True)

    ny += 9
    ov.text_at(NX, ny, "PAINT:", size=4.5)
    ov.text_at(NX + 28, ny, "COLD GALV ALL PLAIN", size=4)
    ny += 5
    ov.text_at(NX + 28, ny, "STEEL & WELDS", size=4)

    ny += 9
    ov.text_at(NX, ny, "HOLES:", size=4.5)
    ov.text_at(NX + 28, ny, f"{cfg.col_bolt_hole_dia} - UNO", size=4.5)

    ny += 9
    ov.text_at(NX, ny, "DO NOT PAINT AT THE", size=4, bold=True)
    ny += 5
    ov.text_at(NX, ny, "LOCATIONS INDICATED", size=4, bold=True)

    # WPS Codes
    ny += 10
    ov.text_at(NX, ny, "WPS CODES:", size=4.5, bold=True)
    ny += 7
    for code, info in WPS_CODES.items():
        ov.text_at(NX + 2, ny, f'WPS-"{code}":', size=3.5, bold=True)
        ov.text_at(NX + 32, ny, info["application"], size=3.5)
        ny += 6

    # ── BOM (right: x=830..1214) ──
    BOM_L = SPLIT_X;  BOM_R = BR
    BOM_T = BANNER_BOT;  BOM_B = TOP_BOT
    BOM_W = BOM_R - BOM_L

    ov.rect_at(BOM_L, BOM_T, BOM_W, BOM_B - BOM_T,
               stroke_color=black, stroke_width=0.5)

    ov.text_centered_at((BOM_L + BOM_R) / 2, BOM_T + 10,
                        "BILL OF MATERIALS", size=7, bold=True)

    bom_cols = [
        ("MARK", 0.08), ("QTY", 0.06), ("DESCRIPTION", 0.28),
        ("SIZE", 0.22), ("MATERIAL", 0.20), ("WT.", 0.10),
    ]
    col_xs = []
    x_acc = BOM_L
    for _, rw in bom_cols:
        col_xs.append(x_acc)
        x_acc += rw * BOM_W
    col_xs.append(BOM_R)

    ROW_H = 13
    HDR_H = 14
    hdr_top = BOM_T + 16
    data_top = hdr_top + HDR_H

    # Header row
    ov.rect_at(BOM_L, hdr_top, BOM_W, HDR_H,
               fill_color=CLR_HEADER_BG, stroke_color=black, stroke_width=0.5)
    for i, (hdr, _) in enumerate(bom_cols):
        cx = (col_xs[i] + col_xs[i + 1]) / 2
        ov.text_centered_at(cx, hdr_top + HDR_H / 2 + 2,
                            hdr, size=5.5, bold=True, color=white)

    # Data rows
    cee_size_short = f"{int(data['box_width'])}x{int(data['box_depth'])}x10GA"
    bom_data = [
        (mark, str(cee_qty), "CEE Section (Box Beam)",
         cee_size_short, cfg.col_material_grade, str(cee_weight_total)),
        (mark, str(cap_qty), "Cap Plate",
         f"{cfg.col_cap_plate_thickness} x {int(data['cap_plate_width_in'])}\" x {int(data['cap_plate_length_in'])}\"",
         "A572 Gr 50", str(cap_weight_total)),
        (mark, str(gusset_qty), "Triangle Gusset",
         f"{cfg.col_gusset_thickness} x {int(gusset_leg)}\"x{int(gusset_leg)}\"",
         "A572 Gr 50", str(gusset_weight_total)),
        (mark, str(rebar_total), "Rebar",
         f"{data['rebar_size']} x {_fmt_ft_in(data['rebar_length_in'])}",
         "A706", str(rebar_weight_total)),
        (mark, str(total_cols * data.get('connection_bolts', 4)), "Connection Bolts",
         f"{cfg.col_bolt_hole_dia} DIA", "A325", ""),
    ]

    for r_idx, row in enumerate(bom_data):
        ry = data_top + r_idx * ROW_H
        ov.line_at(BOM_L, ry, BOM_R, ry, width=0.25, color=CLR_GRID)
        for ci, val in enumerate(row):
            if not val:
                continue
            if ci in (0, 1):
                ov.text_centered_at((col_xs[ci] + col_xs[ci+1])/2,
                                    ry + ROW_H/2 + 2, val, size=5)
            else:
                ov.text_at(col_xs[ci] + 2, ry + ROW_H/2 + 2, val, size=5)

    # Total row
    bom_bot = data_top + len(bom_data) * ROW_H
    ov.line_at(BOM_L, bom_bot, BOM_R, bom_bot, width=1.0)
    wt_cx = (col_xs[5] + col_xs[6]) / 2
    ov.text_centered_at(wt_cx, bom_bot + 8, str(total_weight), size=6, bold=True)
    bom_end = bom_bot + ROW_H

    # BOM inner border (around table only)
    ov.rect_at(BOM_L, hdr_top, BOM_W, bom_end - hdr_top,
               stroke_color=black, stroke_width=0.8)
    for xi in col_xs[1:-1]:
        ov.line_at(xi, hdr_top, xi, bom_end, width=0.25, color=CLR_GRID)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # BOTTOM HALF: Title Block (full width: x=658..1214)
    # Horizontal bar layout: Company | Project Info | Mark | DA+Rev
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    TT = TOP_BOT + 2   # title block top
    TB = BB             # title block bottom (793)
    TH = TB - TT        # ~151px tall
    TX_margin = 4

    # Divide into 4 columns:
    #   Company:  658..808  (150px)
    #   Project:  808..968  (160px)
    #   Mark:     968..1068 (100px)
    #   DA+Rev:   1068..1214 (146px)
    C1L = BL;       C1R = 808
    C2L = C1R;      C2R = 968
    C3L = C2R;      C3R = 1068
    C4L = C3R;      C4R = BR

    # ── Column 1: Company name ──
    ov.rect_at(C1L, TT, C1R - C1L, TH, stroke_color=black, stroke_width=0.8)
    cm = (C1L + C1R) / 2
    ov.text_centered_at(cm, TT + 22, "Structures America", size=11, bold=True)
    ov.text_centered_at(cm, TT + 38, "14369 FM 1314", size=6)
    ov.text_centered_at(cm, TT + 49, "Conroe, TX 77302", size=6)
    ov.text_centered_at(cm, TT + 60, "505-270-1877", size=5.5)
    ov.text_centered_at(cm, TT + 70, "www.StructuresAmerica.com", size=4.5)

    # Design authority disclaimer (lower portion of company column)
    da_y = TT + 84
    ov.line_at(C1L, da_y, C1R, da_y, width=0.3, color=CLR_GRID)
    da_y += 5
    ov.text_at(C1L + TX_margin, da_y, "DESIGN/REVIEW AUTHORITY:", size=3.5, bold=True)
    da_y += 5.5
    ov.text_at(C1L + TX_margin, da_y, "PLEASE REVIEW THIS DRAWING CAREFULLY", size=3, bold=True)
    da_y += 5
    disclaimer = [
        "We assume NO responsibility for the accuracy of the",
        "information in the contract documents including",
        "architectural and structural drawings. This drawing",
        "represents our best interpretation of the contract",
        "documents. Unless Noted Otherwise when it is returned",
        "from approval it will be assumed that the design",
        "authority confirms that we have correctly interpreted",
        "the contract documents and we are released to begin",
        "fabrication.",
    ]
    for line in disclaimer:
        ov.text_at(C1L + TX_margin, da_y, line, size=2.5)
        da_y += 4

    # ── Column 2: Project Info ──
    ov.rect_at(C2L, TT, C2R - C2L, TH, stroke_color=black, stroke_width=0.8)
    px = C2L + TX_margin
    py = TT + 12
    row_gap = 13

    ov.text_at(px, py, "PROJECT:", size=5, bold=True)
    ov.text_at(px + 40, py, project_name, size=5)
    py += row_gap
    ov.line_at(C2L, py - 3, C2R, py - 3, width=0.25, color=CLR_GRID)

    ov.text_at(px, py, "CUSTOMER:", size=5, bold=True)
    ov.text_at(px + 46, py, customer_name, size=4.5)
    py += row_gap
    ov.line_at(C2L, py - 3, C2R, py - 3, width=0.25, color=CLR_GRID)

    ov.text_at(px, py, "JOB:", size=5, bold=True)
    ov.text_at(px + 22, py, job_code, size=5.5, bold=True)
    py += row_gap
    ov.line_at(C2L, py - 3, C2R, py - 3, width=0.25, color=CLR_GRID)

    ov.text_at(px, py, "DATE:", size=5, bold=True)
    ov.text_at(px + 26, py, today, size=5)
    py += row_gap
    ov.line_at(C2L, py - 3, C2R, py - 3, width=0.25, color=CLR_GRID)

    ov.text_at(px, py, "DRAWN:", size=5, bold=True)
    ov.text_at(px + 32, py, "AUTO", size=5)
    py += row_gap
    ov.line_at(C2L, py - 3, C2R, py - 3, width=0.25, color=CLR_GRID)

    ov.text_at(px, py, "CHECKED:", size=5, bold=True)
    ov.text_at(px + 42, py, "—", size=5)
    py += row_gap
    ov.line_at(C2L, py - 3, C2R, py - 3, width=0.25, color=CLR_GRID)

    ov.text_at(px, py, "SHEET:", size=5, bold=True)
    ov.text_at(px + 30, py, "1 OF 1", size=5)
    py += row_gap
    ov.line_at(C2L, py - 3, C2R, py - 3, width=0.25, color=CLR_GRID)

    ov.text_at(px, py, "REV:", size=5, bold=True)
    ov.text_at(px + 22, py, "-", size=5)

    # ── Column 3: Big mark ──
    ov.rect_at(C3L, TT, C3R - C3L, TH, stroke_color=black, stroke_width=0.8)
    mk_cx = (C3L + C3R) / 2
    mk_cy = TT + TH / 2
    ov.text_centered_at(mk_cx, mk_cy - 4, "COLUMN", size=12, bold=True)
    ov.text_centered_at(mk_cx, mk_cy + 12, mark, size=18, bold=True)

    # ── Column 4: Date/Rev rows ──
    ov.rect_at(C4L, TT, C4R - C4L, TH, stroke_color=black, stroke_width=0.8)
    rx = C4L + TX_margin

    # Header row
    rev_hdr_h = 14
    ov.rect_at(C4L, TT, C4R - C4L, rev_hdr_h,
               fill_color=CLR_HEADER_BG, stroke_color=black, stroke_width=0.5)
    ov.text_at(rx, TT + 9, "DATE", size=4.5, bold=True, color=white)
    ov.text_at(rx + 40, TT + 9, "REV", size=4.5, bold=True, color=white)
    ov.text_at(rx + 60, TT + 9, "DESCRIPTION", size=4.5, bold=True, color=white)

    rev_y = TT + rev_hdr_h
    rev_row_h = 11

    # Rev row 0
    ov.text_at(rx, rev_y + 7, today, size=4)
    ov.text_at(rx + 42, rev_y + 7, "0", size=4)
    ov.text_at(rx + 60, rev_y + 7, "FOR FABRICATION", size=4)
    rev_y += rev_row_h
    ov.line_at(C4L, rev_y, C4R, rev_y, width=0.25, color=CLR_GRID)

    # Rev row A
    ov.text_at(rx, rev_y + 7, today, size=4)
    ov.text_at(rx + 42, rev_y + 7, "A", size=4)
    ov.text_at(rx + 60, rev_y + 7, "FOR APPROVAL", size=4)
    rev_y += rev_row_h
    ov.line_at(C4L, rev_y, C4R, rev_y, width=0.25, color=CLR_GRID)

    # Empty rev rows for future use
    for _ in range(4):
        rev_y += rev_row_h
        ov.line_at(C4L, rev_y, C4R, rev_y, width=0.25, color=CLR_GRID)


def generate_column_from_template(
    cfg,
    data: Dict,
    template_path: str = None,
    output_path: str = None,
) -> bytes:
    """Generate column shop drawing by overlaying on the Skyline template."""

    if template_path is None:
        # Auto-select template based on roof pitch
        pitch = getattr(cfg, 'roof_pitch', 1.2)
        template_path = _select_template(pitch)

    reader = PdfReader(template_path)
    template_page = reader.pages[0]

    # Create overlay at RAW page size (792×1224)
    overlay_buf = io.BytesIO()
    c = canvas.Canvas(overlay_buf, pagesize=(RAW_W, RAW_H))
    ov = TemplateOverlay(c)

    # ── Compute dynamic values ──
    mark = data["mark"]
    n_frames = cfg.n_frames
    total_cols = n_frames * 2 if cfg.frame_type == "tee" else n_frames * 3
    cee_size = data["cee_size"]
    total_length_in = data["total_length_in"]

    pm_cap = "p3"
    pm_gusset_up = "p4"
    pm_gusset_dn = "p5"
    pm_rebar = "rb2" if data["rebar_reinforced"] else "rb1"

    cee_qty = total_cols * 2
    cap_qty = total_cols
    gusset_qty = total_cols * 2
    rebar_total = total_cols * data["rebar_qty"]

    cee_ft = int(total_length_in // 12)
    cee_in = round(total_length_in % 12, 1)
    if cee_in == int(cee_in):
        cee_in = int(cee_in)

    rebar_ft = int(data["rebar_length_in"] // 12)
    rebar_in = round(data["rebar_length_in"] % 12, 1)
    if rebar_in == int(rebar_in):
        rebar_in = int(rebar_in)

    cap_plate_ft = int(data["cap_plate_length_in"] // 12)
    cap_plate_in = int(data["cap_plate_length_in"] % 12)
    gusset_leg = data["gusset_leg_in"]

    # Weights
    cee_lbs_per_ft = 10.83
    cee_weight_total = int(data["total_length_ft"] * cee_lbs_per_ft * cee_qty)
    cap_weight_each = data["cap_plate_width_in"] * data["cap_plate_length_in"] * 0.75 * 0.2836
    cap_weight_total = int(cap_weight_each * cap_qty)
    gusset_weight_each = 0.5 * gusset_leg * gusset_leg * 0.375 * 0.2836
    gusset_weight_total = int(gusset_weight_each * gusset_qty)
    rebar_wt_map = {"#5": 1.043, "#7": 2.044, "#9": 3.40}
    rebar_wt_per_ft = rebar_wt_map.get(data["rebar_size"], 3.40)
    rebar_weight_total = int(data["rebar_length_ft"] * rebar_wt_per_ft * rebar_total)
    total_weight = cee_weight_total + cap_weight_total + gusset_weight_total + rebar_weight_total

    col_desc = f"{_fmt_ft_in(total_length_in)} (C{cee_size}x{_fmt_ft_in(total_length_in)})"
    col_desc_short = f"C{cee_size}x{_fmt_ft_in(total_length_in)}"
    rebar_callout = f"{data['rebar_size']} Rebar {_fmt_ft_in(data['rebar_length_in'])}"

    # ──────────────────────────────────────────────
    # STEP 1: White out dynamic regions
    # ──────────────────────────────────────────────
    for region_name in REGIONS:
        ov.whitebox(region_name)

    # ──────────────────────────────────────────────
    # STEP 2: Stamp text overlays on the drawing views
    # ──────────────────────────────────────────────

    # Title line (centered below front/side views)
    title = f"{total_cols} - Columns - {mark}"
    ov.text("title_line", title, size=11, bold=True, centered=True)

    # Column descriptions (near front/side views at top)
    ov.text("col_desc_main", col_desc, size=10)
    ov.text("col_desc_secondary", col_desc_short, size=10)

    # Rebar callout (near side view)
    ov.text("dim_rebar_callout", rebar_callout, size=10)

    # Piece mark labels
    ov.text("pm_rb_bb", pm_rebar, size=9, bold=True)
    ov.text("pm_rb_bb_typ", "TYP", size=8, bold=True, x_offset=5)
    ov.text("pm_rb_sideview", pm_rebar, size=8)

    # ──────────────────────────────────────────────
    # STEP 3: Draw entire bottom-right section from scratch
    #   (BOM, notes, AND title block — all unified)
    #   (BOM table, notes, dates, design authority)
    # ──────────────────────────────────────────────
    _draw_bottom_right(ov, cfg, data, mark, total_cols, cee_size,
                       cee_qty, cap_qty, gusset_qty, rebar_total,
                       pm_cap, pm_gusset_up, pm_gusset_dn, pm_rebar,
                       cee_ft, cee_in, cap_plate_ft, cap_plate_in, gusset_leg,
                       cee_weight_total, cap_weight_total,
                       gusset_weight_total, rebar_weight_total,
                       total_weight, rebar_ft, rebar_in)

    # ── Save and merge ──
    c.save()
    overlay_buf.seek(0)

    overlay_reader = PdfReader(overlay_buf)
    overlay_page = overlay_reader.pages[0]

    writer = PdfWriter()
    template_page.merge_page(overlay_page)
    writer.add_page(template_page)

    output_buf = io.BytesIO()
    writer.write(output_buf)
    result = output_buf.getvalue()

    if output_path:
        with open(output_path, 'wb') as f:
            f.write(result)

    return result
