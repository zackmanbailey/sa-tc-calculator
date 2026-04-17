"""
TitanForge — AISC Inspection Report PDF Generator
====================================================
Generates printable, signable inspection report PDFs that:
  - Auto-populate from app data (job info, BOM, member marks, WPS refs, heat numbers)
  - Tell the inspector exactly what to check with action items
  - Track required inspections per component type (column, rafter, etc.)
  - Produce a paper trail matching what the app recorded

Each component type has required inspection stages. Each inspection stage
generates a report with:
  - Header block (job, date, report #, inspector, standard ref)
  - Member info (mark, type, dimensions, weight, heat number)
  - Checklist of action items with checkboxes + measurement fields
  - Witness mark / stamp instructions
  - Disposition section (accept / reject / rework)
  - Signature lines (Inspector + QC Manager)
  - Notes area
"""

import os
import io
import json
import datetime
import uuid
from typing import Dict, List, Optional, Tuple

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import (
    HexColor, black, white, Color
)
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Frame, PageTemplate, BaseDocTemplate
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


# ═══════════════════════════════════════════════════════════════
# COLOR PALETTE (matches TitanForge brand)
# ═══════════════════════════════════════════════════════════════
NAVY       = HexColor("#0F172A")
DARK_NAVY  = HexColor("#020617")
GOLD       = HexColor("#C89A2E")
BLUE       = HexColor("#3B82F6")
GREEN      = HexColor("#10B981")
RED        = HexColor("#DC2626")
AMBER      = HexColor("#F59E0B")
GRAY_100   = HexColor("#F1F5F9")
GRAY_200   = HexColor("#E2E8F0")
GRAY_300   = HexColor("#CBD5E1")
GRAY_500   = HexColor("#64748B")
GRAY_700   = HexColor("#334155")
GRAY_900   = HexColor("#0F172A")
WHITE      = white
BLACK      = black


# ═══════════════════════════════════════════════════════════════
# COMPONENT INSPECTION REQUIREMENTS
# ═══════════════════════════════════════════════════════════════
# Each component type maps to a list of required inspection stages.
# Each stage has the inspection type, when it's required, and
# specific action items for the inspector.

COMPONENT_INSPECTION_REQUIREMENTS = {
    "column": {
        "label": "Structural Column (Box Beam)",
        "inspections": [
            {
                "stage": "material_receiving",
                "when": "Before fabrication begins",
                "required": True,
                "action_items": [
                    {"action": "Verify MTR (Mill Test Report) matches coil tag on material", "type": "check"},
                    {"action": "Record heat number from coil/member", "type": "text", "field": "heat_number"},
                    {"action": "Verify material grade matches BOM specification (A572 Gr 50)", "type": "check"},
                    {"action": "Measure material thickness with calibrated micrometer", "type": "measurement", "field": "thickness_actual", "unit": "in", "spec": "Per BOM gauge"},
                    {"action": "Inspect surface for excessive rust, pitting, or mill defects", "type": "check"},
                    {"action": "Verify coil width matches cut list requirements", "type": "check"},
                    {"action": "Place MATERIAL ACCEPTED stamp/witness mark on member end", "type": "witness", "mark": "MA"},
                ],
            },
            {
                "stage": "dimensional",
                "when": "After roll-forming and cutting to length, before welding",
                "required": True,
                "action_items": [
                    {"action": "Measure overall column length", "type": "measurement", "field": "length_actual", "unit": "ft-in", "spec": "Per shop drawing"},
                    {"action": "Measure column cross-section width (box beam)", "type": "measurement", "field": "width_actual", "unit": "in", "spec": "Per BOM"},
                    {"action": "Measure column cross-section depth (box beam)", "type": "measurement", "field": "depth_actual", "unit": "in", "spec": "Per BOM"},
                    {"action": "Verify squareness — measure diagonals of box beam end", "type": "measurement", "field": "diagonal_diff", "unit": "in", "spec": "< 1/8 in difference"},
                    {"action": "Verify end plates are square to column axis within 1/16 in", "type": "check"},
                    {"action": "Verify base plate hole pattern matches anchor bolt layout", "type": "check"},
                    {"action": "Check cap plate angle matches roof pitch from drawing", "type": "check"},
                    {"action": "Verify rebar is centered in box beam cavity (if reinforced)", "type": "check"},
                    {"action": "Place DIM CHECKED witness mark near mid-height of column", "type": "witness", "mark": "DC"},
                ],
            },
            {
                "stage": "weld_visual",
                "when": "After all welding is complete",
                "required": True,
                "action_items": [
                    {"action": "Verify WPS posted at weld station and followed (WPS-B for stitch, WPS-F for end plates)", "type": "check"},
                    {"action": "Confirm welder qualification is current for this joint type", "type": "check"},
                    {"action": "Check stitch weld pattern: 2 in weld @ 12 in O.C. both sides", "type": "check"},
                    {"action": "Measure fillet weld size with calibrated fillet gauge", "type": "measurement", "field": "fillet_size_actual", "unit": "in", "spec": "3/16 in min"},
                    {"action": "Inspect all welds for cracks — REJECT if any found", "type": "check"},
                    {"action": "Inspect for incomplete fusion at weld toes", "type": "check"},
                    {"action": "Check undercut does not exceed 1/32 in", "type": "check"},
                    {"action": "Inspect for porosity — no pores exceeding 3/32 in diameter", "type": "check"},
                    {"action": "Verify no arc strikes on base metal outside weld zone", "type": "check"},
                    {"action": "Inspect end plate weld: continuous 360 deg fillet, no starts/stops on corners", "type": "check"},
                    {"action": "Measure end plate fillet weld size", "type": "measurement", "field": "endplate_weld_size", "unit": "in", "spec": "1/4 in continuous"},
                    {"action": "Inspect rebar welds per WPS-D (if reinforced column)", "type": "check"},
                    {"action": "Clean spatter from all weld areas", "type": "check"},
                    {"action": "Place VT PASSED witness mark (or VT FAILED + NCR #)", "type": "witness", "mark": "VT"},
                ],
            },
            {
                "stage": "surface_prep",
                "when": "After welding, before paint/coating",
                "required": False,
                "action_items": [
                    {"action": "Verify surface prep meets SSPC specification", "type": "select", "field": "sspc_level",
                     "options": ["SSPC-SP6 (Commercial)", "SSPC-SP10 (Near-White)", "N/A — Galvanized"]},
                    {"action": "Measure primer dry film thickness (DFT)", "type": "measurement", "field": "primer_dft", "unit": "mils", "spec": "Per coating spec"},
                    {"action": "Check full coverage — no holidays or bare spots", "type": "check"},
                    {"action": "Verify coating cure time before handling", "type": "check"},
                    {"action": "Place COAT INSPECTED mark on member", "type": "witness", "mark": "CI"},
                ],
            },
            {
                "stage": "final_inspection",
                "when": "Before releasing to shipping/staging area",
                "required": True,
                "action_items": [
                    {"action": "Verify ALL prior inspections passed (Material, Dimensional, Weld VT)", "type": "check"},
                    {"action": "Verify ship mark is clearly stenciled/tagged on member", "type": "check"},
                    {"action": "Verify member matches shop drawing — final visual comparison", "type": "check"},
                    {"action": "Check for shipping damage, handling marks, or missed defects", "type": "check"},
                    {"action": "Verify all bolt holes are deburred", "type": "check"},
                    {"action": "Confirm member is ready for loading (clips attached, hardware bagged)", "type": "check"},
                    {"action": "Place FINAL QC RELEASE stamp on member", "type": "witness", "mark": "QC"},
                ],
            },
        ],
    },

    "rafter": {
        "label": "Structural Rafter (Box Beam)",
        "inspections": [
            {
                "stage": "material_receiving",
                "when": "Before fabrication begins",
                "required": True,
                "action_items": [
                    {"action": "Verify MTR (Mill Test Report) matches coil tag on material", "type": "check"},
                    {"action": "Record heat number from coil/member", "type": "text", "field": "heat_number"},
                    {"action": "Verify material grade matches BOM specification (A572 Gr 50)", "type": "check"},
                    {"action": "Measure material thickness with calibrated micrometer", "type": "measurement", "field": "thickness_actual", "unit": "in", "spec": "Per BOM gauge"},
                    {"action": "Inspect surface for excessive rust, pitting, or mill defects", "type": "check"},
                    {"action": "Place MATERIAL ACCEPTED stamp/witness mark on member end", "type": "witness", "mark": "MA"},
                ],
            },
            {
                "stage": "dimensional",
                "when": "After roll-forming and cutting, before welding",
                "required": True,
                "action_items": [
                    {"action": "Measure overall rafter length (slope length)", "type": "measurement", "field": "length_actual", "unit": "ft-in", "spec": "Per shop drawing"},
                    {"action": "Measure rafter cross-section width", "type": "measurement", "field": "width_actual", "unit": "in", "spec": "Per BOM"},
                    {"action": "Measure rafter cross-section depth", "type": "measurement", "field": "depth_actual", "unit": "in", "spec": "Per BOM"},
                    {"action": "Verify cap plate angle matches roof pitch", "type": "check"},
                    {"action": "Verify eave end plate is perpendicular to rafter axis", "type": "check"},
                    {"action": "Check purlin clip locations match drawing dimensions", "type": "check"},
                    {"action": "Verify clip spacing from eave and ridge per shop drawing", "type": "check"},
                    {"action": "Measure diagonals of box beam end for squareness", "type": "measurement", "field": "diagonal_diff", "unit": "in", "spec": "< 1/8 in"},
                    {"action": "Place DIM CHECKED witness mark on rafter", "type": "witness", "mark": "DC"},
                ],
            },
            {
                "stage": "weld_visual",
                "when": "After all welding is complete (body stitches + clips + end plates)",
                "required": True,
                "action_items": [
                    {"action": "Verify WPS posted at weld station and followed", "type": "check"},
                    {"action": "Confirm welder qualification is current for this joint type", "type": "check"},
                    {"action": "Check body stitch weld pattern: 2 in weld @ 12 in O.C. per WPS-B", "type": "check"},
                    {"action": "Measure body fillet weld size", "type": "measurement", "field": "body_fillet_size", "unit": "in", "spec": "3/16 in min"},
                    {"action": "Inspect clip-to-rafter welds per WPS-C: continuous both sides", "type": "check"},
                    {"action": "Measure clip fillet weld size", "type": "measurement", "field": "clip_fillet_size", "unit": "in", "spec": "1/8 in min"},
                    {"action": "Inspect end plate welds per WPS-F: continuous 360 deg", "type": "check"},
                    {"action": "Measure end plate fillet weld size", "type": "measurement", "field": "endplate_weld_size", "unit": "in", "spec": "1/4 in continuous"},
                    {"action": "Inspect ALL welds for cracks — REJECT if any found", "type": "check"},
                    {"action": "Check undercut does not exceed 1/32 in on any weld", "type": "check"},
                    {"action": "Inspect for porosity — no pores exceeding 3/32 in dia", "type": "check"},
                    {"action": "Verify no arc strikes on base metal", "type": "check"},
                    {"action": "Clean spatter from all weld areas", "type": "check"},
                    {"action": "Place VT PASSED witness mark (or VT FAILED + NCR #)", "type": "witness", "mark": "VT"},
                ],
            },
            {
                "stage": "surface_prep",
                "when": "After welding, before paint/coating",
                "required": False,
                "action_items": [
                    {"action": "Verify surface prep meets SSPC specification", "type": "select", "field": "sspc_level",
                     "options": ["SSPC-SP6 (Commercial)", "SSPC-SP10 (Near-White)", "N/A — Galvanized"]},
                    {"action": "Measure primer DFT", "type": "measurement", "field": "primer_dft", "unit": "mils", "spec": "Per coating spec"},
                    {"action": "Check full coverage — no holidays or bare spots", "type": "check"},
                    {"action": "Place COAT INSPECTED mark on member", "type": "witness", "mark": "CI"},
                ],
            },
            {
                "stage": "final_inspection",
                "when": "Before releasing to shipping/staging",
                "required": True,
                "action_items": [
                    {"action": "Verify ALL prior inspections passed (Material, Dimensional, Weld VT)", "type": "check"},
                    {"action": "Verify ship mark is clearly stenciled/tagged", "type": "check"},
                    {"action": "Verify member matches shop drawing — final visual", "type": "check"},
                    {"action": "Check all purlin clips are at correct locations and fully welded", "type": "check"},
                    {"action": "Verify hardware bag is attached (bolts, nuts, washers for connections)", "type": "check"},
                    {"action": "Place FINAL QC RELEASE stamp on member", "type": "witness", "mark": "QC"},
                ],
            },
        ],
    },

    "purlin": {
        "label": "Purlin (Z-Section / C-Section)",
        "inspections": [
            {
                "stage": "material_receiving",
                "when": "Before fabrication",
                "required": True,
                "action_items": [
                    {"action": "Verify MTR matches coil tag", "type": "check"},
                    {"action": "Record heat number", "type": "text", "field": "heat_number"},
                    {"action": "Verify material grade (A572 Gr 50 or per spec)", "type": "check"},
                    {"action": "Measure material thickness", "type": "measurement", "field": "thickness_actual", "unit": "in", "spec": "Per BOM gauge"},
                    {"action": "Place MATERIAL ACCEPTED mark", "type": "witness", "mark": "MA"},
                ],
            },
            {
                "stage": "dimensional",
                "when": "After roll-forming and cutting",
                "required": True,
                "action_items": [
                    {"action": "Measure purlin length", "type": "measurement", "field": "length_actual", "unit": "ft-in", "spec": "Per shop drawing"},
                    {"action": "Measure flange width", "type": "measurement", "field": "flange_width", "unit": "in", "spec": "Per section spec"},
                    {"action": "Measure web depth", "type": "measurement", "field": "web_depth", "unit": "in", "spec": "Per section spec"},
                    {"action": "Verify hole pattern for sag rod and clip connections", "type": "check"},
                    {"action": "Check straightness — no visible bow or twist", "type": "check"},
                    {"action": "Place DIM CHECKED mark", "type": "witness", "mark": "DC"},
                ],
            },
            {
                "stage": "final_inspection",
                "when": "Before bundling for shipment",
                "required": True,
                "action_items": [
                    {"action": "Verify all purlins in group match required quantity", "type": "check"},
                    {"action": "Verify ship mark tags on bundle", "type": "check"},
                    {"action": "Check for damage from handling", "type": "check"},
                    {"action": "Place QC RELEASE mark on bundle tag", "type": "witness", "mark": "QC"},
                ],
            },
        ],
    },

    "sag_rod": {
        "label": "Sag Rod Assembly",
        "inspections": [
            {
                "stage": "material_receiving",
                "when": "Before fabrication",
                "required": True,
                "action_items": [
                    {"action": "Verify material specification (A36 angle / threaded rod)", "type": "check"},
                    {"action": "Record heat number", "type": "text", "field": "heat_number"},
                    {"action": "Measure angle leg dimensions", "type": "measurement", "field": "angle_size", "unit": "in", "spec": "Per BOM"},
                    {"action": "Place MATERIAL ACCEPTED mark", "type": "witness", "mark": "MA"},
                ],
            },
            {
                "stage": "dimensional",
                "when": "After cutting to length",
                "required": True,
                "action_items": [
                    {"action": "Measure sag rod length", "type": "measurement", "field": "length_actual", "unit": "ft-in", "spec": "Per shop drawing"},
                    {"action": "Verify hole locations for purlin attachment", "type": "check"},
                    {"action": "Place DIM CHECKED mark", "type": "witness", "mark": "DC"},
                ],
            },
        ],
    },

    "strap": {
        "label": "Hurricane Strap",
        "inspections": [
            {
                "stage": "material_receiving",
                "when": "Before fabrication",
                "required": True,
                "action_items": [
                    {"action": "Verify material specification", "type": "check"},
                    {"action": "Measure material thickness", "type": "measurement", "field": "thickness_actual", "unit": "in", "spec": "Per BOM gauge"},
                    {"action": "Place MATERIAL ACCEPTED mark", "type": "witness", "mark": "MA"},
                ],
            },
            {
                "stage": "dimensional",
                "when": "After forming/cutting",
                "required": True,
                "action_items": [
                    {"action": "Measure strap overall length", "type": "measurement", "field": "length_actual", "unit": "in", "spec": "Per drawing"},
                    {"action": "Verify hole pattern", "type": "check"},
                    {"action": "Check bend radius and angle", "type": "check"},
                    {"action": "Place DIM CHECKED mark", "type": "witness", "mark": "DC"},
                ],
            },
        ],
    },

    "endcap": {
        "label": "Endcap U-Channel",
        "inspections": [
            {
                "stage": "material_receiving",
                "when": "Before fabrication",
                "required": True,
                "action_items": [
                    {"action": "Verify material specification", "type": "check"},
                    {"action": "Measure material thickness", "type": "measurement", "field": "thickness_actual", "unit": "in", "spec": "Per BOM gauge"},
                    {"action": "Place MATERIAL ACCEPTED mark", "type": "witness", "mark": "MA"},
                ],
            },
            {
                "stage": "dimensional",
                "when": "After forming",
                "required": True,
                "action_items": [
                    {"action": "Measure endcap height to match column depth", "type": "measurement", "field": "height_actual", "unit": "in", "spec": "Per drawing"},
                    {"action": "Verify channel profile dimensions", "type": "check"},
                    {"action": "Place DIM CHECKED mark", "type": "witness", "mark": "DC"},
                ],
            },
        ],
    },

    "p1clip": {
        "label": "P1 Interior Purlin Clip",
        "inspections": [
            {
                "stage": "material_receiving",
                "when": "Before fabrication",
                "required": True,
                "action_items": [
                    {"action": "Verify material specification (A572 Gr 50)", "type": "check"},
                    {"action": "Measure material thickness", "type": "measurement", "field": "thickness_actual", "unit": "in", "spec": "12GA (0.105 in)"},
                    {"action": "Place MATERIAL ACCEPTED mark on batch", "type": "witness", "mark": "MA"},
                ],
            },
            {
                "stage": "dimensional",
                "when": "After shearing/punching",
                "required": True,
                "action_items": [
                    {"action": "Measure clip height", "type": "measurement", "field": "clip_height", "unit": "in", "spec": "Per drawing"},
                    {"action": "Measure clip width", "type": "measurement", "field": "clip_width", "unit": "in", "spec": "Per drawing"},
                    {"action": "Verify bolt hole size and location", "type": "check"},
                    {"action": "Place DIM CHECKED mark on batch", "type": "witness", "mark": "DC"},
                ],
            },
        ],
    },

    "p2plate": {
        "label": "P2 Eave Plate",
        "inspections": [
            {
                "stage": "material_receiving",
                "when": "Before fabrication",
                "required": True,
                "action_items": [
                    {"action": "Verify material specification", "type": "check"},
                    {"action": "Measure plate thickness", "type": "measurement", "field": "thickness_actual", "unit": "in", "spec": "Per BOM"},
                    {"action": "Place MATERIAL ACCEPTED mark", "type": "witness", "mark": "MA"},
                ],
            },
            {
                "stage": "dimensional",
                "when": "After cutting/punching",
                "required": True,
                "action_items": [
                    {"action": "Measure plate dimensions (L x W)", "type": "measurement", "field": "plate_dims", "unit": "in", "spec": "Per drawing"},
                    {"action": "Verify hole pattern for purlin bolt connections", "type": "check"},
                    {"action": "Place DIM CHECKED mark", "type": "witness", "mark": "DC"},
                ],
            },
        ],
    },

    "splice": {
        "label": "Splice Plate",
        "inspections": [
            {
                "stage": "material_receiving",
                "when": "Before fabrication",
                "required": True,
                "action_items": [
                    {"action": "Verify material specification (A36 or A572)", "type": "check"},
                    {"action": "Measure plate thickness", "type": "measurement", "field": "thickness_actual", "unit": "in", "spec": "Per BOM"},
                    {"action": "Place MATERIAL ACCEPTED mark", "type": "witness", "mark": "MA"},
                ],
            },
            {
                "stage": "dimensional",
                "when": "After cutting/punching",
                "required": True,
                "action_items": [
                    {"action": "Measure plate dimensions", "type": "measurement", "field": "plate_dims", "unit": "in", "spec": "Per drawing"},
                    {"action": "Verify bolt hole pattern and spacing", "type": "check"},
                    {"action": "Verify bolt holes are deburred", "type": "check"},
                    {"action": "Place DIM CHECKED mark", "type": "witness", "mark": "DC"},
                ],
            },
        ],
    },
}

# Map short names to full component types (aliases used in WO items)
COMPONENT_TYPE_ALIASES = {
    "col": "column", "columns": "column",
    "raft": "rafter", "rafters": "rafter",
    "purl": "purlin", "purlins": "purlin", "purlin_group": "purlin",
    "sagrod": "sag_rod", "sag_rods": "sag_rod", "sag rod": "sag_rod",
    "straps": "strap", "hurricane_strap": "strap",
    "endcaps": "endcap", "end_cap": "endcap",
    "p1_clip": "p1clip", "p1clips": "p1clip", "p1 clip": "p1clip",
    "p2_plate": "p2plate", "p2plates": "p2plate", "p2 plate": "p2plate", "eave_plate": "p2plate",
    "splice_plate": "splice", "splices": "splice",
}


def normalize_component_type(ctype: str) -> str:
    """Normalize a component type string to its canonical form."""
    ct = ctype.strip().lower().replace("-", "_")
    if ct in COMPONENT_INSPECTION_REQUIREMENTS:
        return ct
    return COMPONENT_TYPE_ALIASES.get(ct, ct)


def get_required_inspections(component_type: str) -> dict:
    """Get the required inspections for a component type."""
    ct = normalize_component_type(component_type)
    return COMPONENT_INSPECTION_REQUIREMENTS.get(ct, {})


def get_all_component_requirements() -> dict:
    """Return the full requirements dictionary."""
    return COMPONENT_INSPECTION_REQUIREMENTS


# ═══════════════════════════════════════════════════════════════
# INSPECTION STAGE LABELS
# ═══════════════════════════════════════════════════════════════
STAGE_LABELS = {
    "material_receiving": "Material Receiving Inspection",
    "dimensional":        "Dimensional / Fit-Up Inspection",
    "weld_visual":        "Weld Visual Inspection (VT)",
    "surface_prep":       "Surface Preparation & Coating Inspection",
    "nde":                "Non-Destructive Examination (NDE)",
    "bolt_inspection":    "Bolt Installation Inspection",
    "final_inspection":   "Final QC Release Inspection",
}

STAGE_STANDARDS = {
    "material_receiving": "AISC 360 Ch. A3 / ASTM Standards",
    "dimensional":        "AISC 303 (COSP) Sec 6.4 / AISC 360",
    "weld_visual":        "AWS D1.1 Table 6.1 / AISC 360 Ch. J2",
    "surface_prep":       "SSPC Standards / AISC 360 Ch. M3",
    "nde":                "AWS D1.1 Ch. 6 / AISC 341 (Seismic)",
    "bolt_inspection":    "AISC 360 Sec J3 / RCSC Specification",
    "final_inspection":   "AISC Quality Manual / Company QMS",
}


# ═══════════════════════════════════════════════════════════════
# PDF GENERATION
# ═══════════════════════════════════════════════════════════════

def _draw_header(c, width, height, report_data):
    """Draw the report header block."""
    y = height - 0.5 * inch

    # Navy header bar
    c.setFillColor(NAVY)
    c.rect(0.5 * inch, y - 50, width - 1 * inch, 55, fill=1, stroke=0)

    # Company name
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(0.75 * inch, y - 18, "TITANFORGE")

    # Gold accent
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.75 * inch, y - 35, "AISC QUALITY CONTROL")

    # Report type on right
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 11)
    report_title = report_data.get("report_title", "INSPECTION REPORT")
    c.drawRightString(width - 0.75 * inch, y - 18, report_title)

    # Standard reference
    c.setFillColor(GRAY_300)
    c.setFont("Helvetica", 8)
    standard = report_data.get("standard", "")
    c.drawRightString(width - 0.75 * inch, y - 32, f"Standard: {standard}")

    # Report # and date
    c.setFont("Helvetica", 7)
    c.drawRightString(width - 0.75 * inch, y - 44, f"Report: {report_data.get('report_number', '')}")

    return y - 60


def _draw_info_block(c, y, width, report_data):
    """Draw the project / member info block."""
    left = 0.5 * inch
    right = width - 0.5 * inch
    box_h = 85

    # Light background box
    c.setFillColor(GRAY_100)
    c.setStrokeColor(GRAY_300)
    c.setLineWidth(0.5)
    c.rect(left, y - box_h, right - left, box_h, fill=1, stroke=1)

    # Two-column layout
    mid = width / 2
    lx = left + 10
    rx = mid + 10

    cy = y - 14
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(NAVY)
    c.drawString(lx, cy, "PROJECT INFORMATION")
    c.drawString(rx, cy, "MEMBER INFORMATION")

    c.setLineWidth(0.3)
    c.setStrokeColor(GRAY_300)
    c.line(mid, y - 5, mid, y - box_h + 5)

    cy -= 16
    c.setFont("Helvetica", 8)
    c.setFillColor(GRAY_700)

    fields_left = [
        ("Job Code:", report_data.get("job_code", "")),
        ("Project:", report_data.get("project_name", "")),
        ("Customer:", report_data.get("customer_name", "")),
        ("Location:", report_data.get("location", "")),
    ]
    fields_right = [
        ("Ship Mark:", report_data.get("ship_mark", "")),
        ("Component:", report_data.get("component_label", "")),
        ("Description:", report_data.get("description", "")),
        ("Heat No.:", report_data.get("heat_number", "___________")),
    ]

    for i, (label, value) in enumerate(fields_left):
        py = cy - i * 14
        c.setFont("Helvetica-Bold", 8)
        c.drawString(lx, py, label)
        c.setFont("Helvetica", 8)
        c.drawString(lx + 55, py, str(value)[:45])

    for i, (label, value) in enumerate(fields_right):
        py = cy - i * 14
        c.setFont("Helvetica-Bold", 8)
        c.drawString(rx, py, label)
        c.setFont("Helvetica", 8)
        c.drawString(rx + 65, py, str(value)[:45])

    return y - box_h - 10


def _draw_inspection_info_row(c, y, width, report_data):
    """Draw inspector / date / stage row."""
    left = 0.5 * inch
    right = width - 0.5 * inch

    c.setFillColor(NAVY)
    c.rect(left, y - 22, right - left, 22, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 8)

    stage_label = report_data.get("stage_label", "")
    c.drawString(left + 8, y - 15, f"INSPECTION STAGE: {stage_label}")

    c.setFont("Helvetica", 8)
    date_str = report_data.get("date", datetime.date.today().strftime("%Y-%m-%d"))
    c.drawString(left + 350, y - 15, f"Date: {date_str}")

    inspector = report_data.get("inspector", "")
    c.drawRightString(right - 8, y - 15, f"Inspector: {inspector}")

    return y - 30


def _draw_when_note(c, y, width, when_text):
    """Draw the 'When to perform' note."""
    left = 0.5 * inch
    c.setFillColor(AMBER)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(left + 4, y - 10, "TIMING:")
    c.setFillColor(GRAY_700)
    c.setFont("Helvetica-Oblique", 7)
    c.drawString(left + 48, y - 10, when_text)
    return y - 18


def _draw_action_items(c, y, width, action_items, start_num=1):
    """Draw the checklist of action items with checkboxes, measurement fields, etc."""
    left = 0.5 * inch + 4
    right = width - 0.5 * inch - 4
    item_height = 22
    num = start_num

    for item in action_items:
        if y - item_height < 1.2 * inch:
            # Need a new page
            c.showPage()
            y = letter[1] - 0.5 * inch
            # Continuation header
            c.setFillColor(GRAY_500)
            c.setFont("Helvetica-Oblique", 8)
            c.drawString(left, y - 10, "(continued from previous page)")
            y -= 22

        action_type = item.get("type", "check")
        action_text = item.get("action", "")

        # Alternating row background
        if num % 2 == 0:
            c.setFillColor(HexColor("#F8FAFC"))
            c.rect(left - 2, y - item_height + 2, right - left + 4, item_height, fill=1, stroke=0)

        # Row number
        c.setFillColor(GRAY_500)
        c.setFont("Helvetica", 7)
        c.drawString(left, y - 12, f"{num}.")

        # Checkbox (for all types)
        box_x = left + 16
        box_y = y - 16
        c.setStrokeColor(GRAY_500)
        c.setLineWidth(0.8)
        c.rect(box_x, box_y, 12, 12, fill=0, stroke=1)

        # Action text
        c.setFillColor(GRAY_900)
        c.setFont("Helvetica", 8)
        text_x = box_x + 18
        # Truncate if needed
        max_chars = 75 if action_type == "check" else 55
        display_text = action_text[:max_chars]
        if len(action_text) > max_chars:
            display_text += "..."
        c.drawString(text_x, y - 12, display_text)

        # Type-specific fields on the right side
        field_x = right - 150

        if action_type == "measurement":
            # Draw measurement field: [_________] unit  (Spec: xxx)
            spec = item.get("spec", "")
            unit = item.get("unit", "")
            c.setStrokeColor(GRAY_300)
            c.setLineWidth(0.5)
            c.rect(field_x, y - 16, 60, 14, fill=0, stroke=1)
            c.setFillColor(GRAY_500)
            c.setFont("Helvetica", 7)
            c.drawString(field_x + 63, y - 12, unit)
            if spec:
                c.setFont("Helvetica-Oblique", 6)
                c.setFillColor(BLUE)
                c.drawString(field_x, y - 2, f"Spec: {spec}")

        elif action_type == "text":
            # Draw text input field
            c.setStrokeColor(GRAY_300)
            c.setLineWidth(0.5)
            c.rect(field_x, y - 16, 100, 14, fill=0, stroke=1)

        elif action_type == "select":
            # Draw dropdown hint
            options = item.get("options", [])
            c.setFillColor(GRAY_500)
            c.setFont("Helvetica", 6)
            opt_text = " / ".join(options[:3])
            if len(opt_text) > 40:
                opt_text = opt_text[:37] + "..."
            c.drawString(field_x, y - 12, f"Circle one: {opt_text}")

        elif action_type == "witness":
            # Highlight witness mark instruction
            mark = item.get("mark", "")
            c.setFillColor(RED)
            c.setFont("Helvetica-Bold", 8)
            c.drawString(field_x + 10, y - 12, f"MARK: [{mark}]")

        y -= item_height
        num += 1

    return y, num


def _draw_disposition_block(c, y, width):
    """Draw the disposition section."""
    left = 0.5 * inch
    right = width - 0.5 * inch

    if y < 2.5 * inch:
        c.showPage()
        y = letter[1] - 0.5 * inch

    y -= 8
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(left + 4, y - 12, "DISPOSITION")
    c.setStrokeColor(NAVY)
    c.setLineWidth(0.5)
    c.line(left, y - 16, right, y - 16)

    y -= 28

    # Three disposition boxes
    box_w = (right - left - 30) / 3
    dispositions = [
        ("ACCEPT", GREEN, "Member meets all acceptance criteria"),
        ("REJECT", RED, "Non-conformance found — issue NCR"),
        ("REWORK", AMBER, "Rework required — re-inspect after"),
    ]

    for i, (label, color, desc) in enumerate(dispositions):
        bx = left + i * (box_w + 15)
        # Checkbox
        c.setStrokeColor(color)
        c.setLineWidth(1.5)
        c.rect(bx, y - 2, 16, 16, fill=0, stroke=1)

        c.setFillColor(GRAY_900)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(bx + 22, y + 2, label)

        c.setFillColor(GRAY_500)
        c.setFont("Helvetica", 6)
        c.drawString(bx + 22, y - 8, desc)

    y -= 28

    # NCR reference field
    c.setFillColor(GRAY_700)
    c.setFont("Helvetica", 8)
    c.drawString(left + 4, y, "If REJECTED, NCR #: ___________________________    Rework description: _______________________________________")
    y -= 16
    c.drawString(left + 4, y, "Notes: ______________________________________________________________________________________________________")
    y -= 14
    c.drawString(left + 4, y, "_____________________________________________________________________________________________________________")

    return y - 10


def _draw_signature_block(c, y, width):
    """Draw signature lines."""
    left = 0.5 * inch
    right = width - 0.5 * inch

    if y < 1.8 * inch:
        c.showPage()
        y = letter[1] - 0.5 * inch

    y -= 10
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(left + 4, y, "SIGNATURES")
    c.setStrokeColor(NAVY)
    c.setLineWidth(0.5)
    c.line(left, y - 4, right, y - 4)

    y -= 35

    mid = width / 2
    sig_w = (mid - left - 30)

    # Inspector signature
    c.setStrokeColor(GRAY_500)
    c.setLineWidth(0.5)
    c.line(left + 4, y, left + 4 + sig_w, y)
    c.setFillColor(GRAY_700)
    c.setFont("Helvetica", 7)
    c.drawString(left + 4, y - 10, "Inspector Signature")

    # Date
    c.line(left + 4 + sig_w + 15, y, left + 4 + sig_w + 85, y)
    c.drawString(left + 4 + sig_w + 15, y - 10, "Date")

    # QC Manager signature
    c.line(mid + 20, y, mid + 20 + sig_w, y)
    c.drawString(mid + 20, y - 10, "QC Manager Signature (Verification)")

    # Date
    c.line(mid + 20 + sig_w + 15, y, mid + 20 + sig_w + 85, y)
    c.drawString(mid + 20 + sig_w + 15, y - 10, "Date")

    # CWI number for weld inspections
    y -= 28
    c.setFont("Helvetica", 7)
    c.drawString(left + 4, y, "Inspector Cert #: ________________  (CWI / ASNT Level: _______)     Calibrated Tool IDs Used: _________________________")

    return y - 10


def _draw_footer(c, width, report_data, page_num=1):
    """Draw page footer."""
    y = 0.4 * inch
    left = 0.5 * inch
    right = width - 0.5 * inch

    c.setStrokeColor(GRAY_300)
    c.setLineWidth(0.3)
    c.line(left, y + 8, right, y + 8)

    c.setFillColor(GRAY_500)
    c.setFont("Helvetica", 6)
    c.drawString(left, y, f"TitanForge QC Report | {report_data.get('job_code', '')} | {report_data.get('report_number', '')} | Generated {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    c.drawRightString(right, y, f"Page {page_num}")
    c.setFont("Helvetica-Oblique", 5)
    c.drawCentredString(width / 2, y - 8, "This document is a controlled quality record. Unauthorized alterations void this report.")


def generate_inspection_report_pdf(
    job_code: str,
    ship_mark: str,
    component_type: str,
    stage: str,
    report_number: str = "",
    inspector: str = "",
    project_name: str = "",
    customer_name: str = "",
    location: str = "",
    description: str = "",
    heat_number: str = "",
    existing_inspection: dict = None,
) -> bytes:
    """
    Generate a single inspection report PDF for one member at one inspection stage.

    Args:
        job_code: Project job code
        ship_mark: Member mark (e.g., "C1", "B1")
        component_type: Component type (e.g., "column", "rafter")
        stage: Inspection stage (e.g., "weld_visual", "dimensional")
        report_number: Report number (auto-generated if empty)
        inspector: Inspector name
        project_name: Project name
        customer_name: Customer name
        location: Project location
        description: Member description (e.g., "14x4x10GA, 19'-6 3/8\"")
        heat_number: Heat number if known
        existing_inspection: If provided, pre-fill with existing inspection data

    Returns:
        PDF file bytes
    """
    ct = normalize_component_type(component_type)
    requirements = COMPONENT_INSPECTION_REQUIREMENTS.get(ct)
    if not requirements:
        raise ValueError(f"Unknown component type: {component_type}")

    # Find the matching inspection stage
    stage_data = None
    for insp in requirements["inspections"]:
        if insp["stage"] == stage:
            stage_data = insp
            break
    if not stage_data:
        raise ValueError(f"Stage '{stage}' not found for component type '{ct}'")

    # Generate report number if not provided
    if not report_number:
        now = datetime.datetime.now()
        report_number = f"IR-{now.strftime('%Y')}-{now.strftime('%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"

    # Build report data
    report_data = {
        "report_number": report_number,
        "report_title": STAGE_LABELS.get(stage, stage.replace("_", " ").title()).upper(),
        "standard": STAGE_STANDARDS.get(stage, ""),
        "job_code": job_code,
        "project_name": project_name,
        "customer_name": customer_name,
        "location": location,
        "ship_mark": ship_mark,
        "component_label": requirements["label"],
        "description": description,
        "heat_number": heat_number,
        "stage_label": STAGE_LABELS.get(stage, stage),
        "date": datetime.date.today().strftime("%Y-%m-%d"),
        "inspector": inspector,
    }

    # If we have existing inspection data, pre-populate some fields
    if existing_inspection:
        if existing_inspection.get("inspector"):
            report_data["inspector"] = existing_inspection["inspector"]
        if existing_inspection.get("created_at"):
            try:
                dt = datetime.datetime.fromisoformat(existing_inspection["created_at"])
                report_data["date"] = dt.strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                pass

    # Create PDF
    buf = io.BytesIO()
    width, height = letter
    c = canvas.Canvas(buf, pagesize=letter)
    c.setTitle(f"Inspection Report - {ship_mark} - {stage}")
    c.setAuthor("TitanForge QC System")
    c.setSubject(f"AISC Inspection Report {report_number}")

    # Page 1
    y = _draw_header(c, width, height, report_data)
    y = _draw_info_block(c, y, width, report_data)
    y = _draw_inspection_info_row(c, y, width, report_data)
    y = _draw_when_note(c, y, width, stage_data["when"])

    # Section header: ACTION ITEMS
    y -= 4
    left = 0.5 * inch
    right = width - 0.5 * inch
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(left + 4, y - 10, "INSPECTOR ACTION ITEMS")
    c.setFont("Helvetica", 7)
    c.setFillColor(GRAY_500)
    c.drawString(left + 140, y - 10, "Check each box as completed. Record measurements in the fields provided.")
    c.setStrokeColor(NAVY)
    c.setLineWidth(0.5)
    c.line(left, y - 14, right, y - 14)
    y -= 22

    # Draw action items
    y, _ = _draw_action_items(c, y, width, stage_data["action_items"])

    # Disposition
    y = _draw_disposition_block(c, y, width)

    # Signatures
    y = _draw_signature_block(c, y, width)

    # Footer
    _draw_footer(c, width, report_data)

    c.save()
    return buf.getvalue()


def generate_full_inspection_packet(
    job_code: str,
    ship_mark: str,
    component_type: str,
    inspector: str = "",
    project_name: str = "",
    customer_name: str = "",
    location: str = "",
    description: str = "",
    heat_number: str = "",
    required_only: bool = True,
) -> bytes:
    """
    Generate a FULL inspection packet for a member — all required inspection
    stages in one PDF. This is the print-and-go packet an inspector takes
    to the shop floor.

    Returns:
        Combined PDF bytes with all inspection report pages
    """
    from pypdf import PdfWriter, PdfReader

    ct = normalize_component_type(component_type)
    requirements = COMPONENT_INSPECTION_REQUIREMENTS.get(ct)
    if not requirements:
        raise ValueError(f"Unknown component type: {component_type}")

    writer = PdfWriter()
    now = datetime.datetime.now()
    base_number = f"IR-{now.strftime('%Y%m%d%H%M%S')}"

    for idx, insp in enumerate(requirements["inspections"]):
        if required_only and not insp.get("required", True):
            continue

        report_number = f"{base_number}-{idx+1:02d}"
        pdf_bytes = generate_inspection_report_pdf(
            job_code=job_code,
            ship_mark=ship_mark,
            component_type=component_type,
            stage=insp["stage"],
            report_number=report_number,
            inspector=inspector,
            project_name=project_name,
            customer_name=customer_name,
            location=location,
            description=description,
            heat_number=heat_number,
        )
        reader = PdfReader(io.BytesIO(pdf_bytes))
        for page in reader.pages:
            writer.add_page(page)

    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


def generate_job_inspection_summary(
    job_code: str,
    work_order_items: List[dict],
    project_name: str = "",
    customer_name: str = "",
) -> dict:
    """
    Analyze a work order and return a summary of all required inspections
    for every member in the job. Used by the UI to show inspection status.

    Returns dict with:
      - total_inspections: int
      - by_component: {component_type: [{ship_mark, stage, required, label}]}
      - summary_table: flat list for rendering
    """
    summary = {
        "total_inspections": 0,
        "by_component": {},
        "summary_table": [],
    }

    for item in work_order_items:
        ct = normalize_component_type(item.get("component_type", ""))
        reqs = COMPONENT_INSPECTION_REQUIREMENTS.get(ct)
        if not reqs:
            continue

        ship_mark = item.get("ship_mark", "?")
        qty = item.get("quantity", 1)

        if ct not in summary["by_component"]:
            summary["by_component"][ct] = []

        for insp in reqs["inspections"]:
            if insp.get("required", True):
                entry = {
                    "ship_mark": ship_mark,
                    "component_type": ct,
                    "component_label": reqs["label"],
                    "stage": insp["stage"],
                    "stage_label": STAGE_LABELS.get(insp["stage"], insp["stage"]),
                    "when": insp["when"],
                    "required": insp["required"],
                    "quantity": qty,
                    "action_count": len(insp["action_items"]),
                }
                summary["by_component"][ct].append(entry)
                summary["summary_table"].append(entry)
                summary["total_inspections"] += qty

    return summary
