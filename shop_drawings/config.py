"""
Shop Drawing Configuration & Defaults
Comprehensive data model capturing all fabrication specs from the design questionnaire.
This module is the single source of truth for every default, rule, and constraint
in the shop drawing auto-population system.

Shop address: 14369 FM 1314, Conroe, TX 77302
"""

import math
from dataclasses import dataclass, field
from typing import Optional, List, Dict

# ═══════════════════════════════════════════════════════════════════════════════
# MACHINE DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

MACHINES = {
    "C1": {
        "name": "C1 — Variable C-Purlin Roll Former",
        "location": "Main Warehouse",
        "description": "Variable C-purlin (6\"x2\" to 16\"x4\"), 3/4\" lip or no-lip U-purlin. "
                       "Alignable puncher for holes.",
        "produces": [
            "c_purlins_variable", "u_purlins", "endcaps", "splice_plates",
            "wall_girt_endcaps",
        ],
    },
    "C2": {
        "name": "C2 — Dedicated 14\"x4\" Roll Former",
        "location": "Main Warehouse",
        "description": "Dedicated roll former for 14\"x4\" column and rafter CEE sections.",
        "produces": ["column_cees", "rafter_cees"],
    },
    "Z1": {
        "name": "Z1 — Z-Purlin Roll Former",
        "location": "Main Warehouse",
        "description": "Makes 12\"x3.5\" Z-purlins with 45° lip at 3/4\".",
        "produces": ["z_purlins"],
    },
    "P1": {
        "name": "P1 — Plate Former",
        "location": "Main Warehouse",
        "description": "Makes purlin clips (p1, p2) and hurricane straps.",
        "produces": ["p1_clips", "p2_clips", "hurricane_straps"],
    },
    "ANGLE": {
        "name": "Angle Machine",
        "location": "Main Warehouse",
        "description": "Makes 2\"x2\" sag rods.",
        "produces": ["sag_rods"],
    },
    "SPARTAN": {
        "name": "Spartan Rib Roll Former",
        "location": "Roofing Shop",
        "description": "Makes Spartan Rib roofing and wall panels from 48\" 29GA G50 coil.",
        "produces": ["roofing_panels", "wall_panels"],
    },
    "WELDING": {
        "name": "Welding Bay",
        "location": "Welding Shop",
        "description": "Column/rafter assembly — stitch welding, rebar attachment, clip welding.",
        "produces": ["column_assemblies", "rafter_assemblies"],
    },
    "REBAR": {
        "name": "Rebar Station",
        "location": "Outdoor Rebar Area",
        "description": "Rebar storage and cut-to-length station.",
        "produces": ["rebar_cut"],
    },
    "CLEANING": {
        "name": "Cleaning Station",
        "location": "Outdoor (covered)",
        "description": "Weld cleaning and cold galvanizing station.",
        "produces": ["weld_cleaning", "cold_galv"],
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# WPS CODES (Fixed across all projects)
# ═══════════════════════════════════════════════════════════════════════════════

WPS_CODES = {
    "B": {"label": "WPS-\"B\"", "application": "Stitch welds (CEE-to-CEE body)"},
    "C": {"label": "WPS-\"C\"", "application": "Clip-to-rafter welds"},
    "D": {"label": "WPS-\"D\"", "application": "Rebar attachment welds"},
    "F": {"label": "WPS-\"F\"", "application": "Column/rafter end welds"},
}

# ═══════════════════════════════════════════════════════════════════════════════
# STICKER CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

STICKER_CONFIG = {
    "size_inches": (4, 6),  # width x height
    "material": "Uline wax resin thermal transfer ribbons",
    "weather_resistant": True,
    "printer_location": "Office",
    "fields": [
        "ship_mark", "job_number", "project_name", "quantity",
        "total_weight_lbs", "machine_assignment", "date_fabricated",
        "drawing_reference", "qr_code",
    ],
    "qr_destination": "titanforge_project_context",  # Opens full project in TitanForge
}

# Sticker grouping rules per component type
STICKER_GROUPING = {
    "columns":          {"per": "each", "notes": "1 sticker per column assembly"},
    "rafters":          {"per": "each", "notes": "1 sticker per rafter assembly"},
    "purlins":          {"per": "group", "notes": "1 sticker per purlin group (by building)"},
    "sag_rods":         {"per": 10, "notes": "1 sticker per 10 sag rods"},
    "hurricane_straps": {"per": 10, "notes": "1 sticker per 10 hurricane straps"},
    "p1_clips":         {"per": "batch", "notes": "1 sticker per fabrication batch"},
    "roofing_panels":   {"per": "stack", "notes": "Max 2000 lbs or 50 sheets per stack"},
    "wall_panels":      {"per": "stack", "notes": "Max 2000 lbs or 50 sheets per stack"},
    "endcaps":          {"per": "group", "notes": "Same size per building gets a sticker"},
    "splice_plates":    {"per": "pair", "notes": "1 sticker per pair"},
}

# ═══════════════════════════════════════════════════════════════════════════════
# PANEL STACKING RULES
# ═══════════════════════════════════════════════════════════════════════════════

PANEL_STACK_LIMITS = {
    "max_weight_lbs": 2000,
    "max_sheets": 50,
    "min_sheets_for_separate_stack": 10,  # Below 10, mixed lengths OK
}

# ═══════════════════════════════════════════════════════════════════════════════
# COLUMN DEFAULTS
# ═══════════════════════════════════════════════════════════════════════════════

COLUMN_DEFAULTS = {
    # CEE body
    "cee_size": "14x4x10GA",           # FIXED — never changes
    "cee_size_editable": False,
    "material_grade": "G90 80 KSI",     # Default, editable
    "material_grade_editable": True,

    # Column length — from BOM formula
    # length = clear_height + (distance * tan(slope)) + embedment + buffer
    "length_source": "bom_formula",
    "length_editable": True,

    # Stitch weld — FIXED
    "stitch_weld": {
        "size": "5/16",
        "pattern": "3-36",
        "end_weld": "1\" long @ 6\" O.C. at first 12\" of column ends",
        "wps": "B",
    },
    "stitch_weld_editable": False,

    # Cap plate
    "cap_plate": {
        "thickness": "3/4\"",
        "width": 14,            # inches
        "length": 26,           # inches
        "grade": "A572 Gr 50",
    },
    "cap_plate_editable": True,

    # Bolt holes
    "bolt_holes": {
        "diameter": "15/16\"",
        "pattern": "standard",  # 4 bolts
    },
    "bolt_holes_editable": True,

    # Cap plate angle — auto-calc from roof pitch
    "cap_plate_angle_source": "roof_pitch",
    "cap_plate_angle_editable": True,

    # Triangle gussets
    "gussets": {
        "thickness": "3/8\"",
        "leg_a": 6,             # inches
        "leg_b": 6,             # inches
        "grade": "A572 Gr 50",
        "qty_per_column": 4,    # 2 per side
        "hypotenuse_source": "roof_pitch",  # Auto-calc, uphill=longer, downhill=shorter
    },
    "gussets_editable": True,

    # Rebar
    "rebar": {
        "size": "#9",           # Default
        "grade": "A706",        # Always weldable
        "qty_per_column": 4,    # 1 per corner — FIXED
        "reinforced_default": True,
        # Reinforced: rebar inside corners
        # Non-reinforced: rebar outside corners with 6\" weld
        # Columns ALWAYS have rebar (reinforced or not)
        "length_source": "bom_formula",
        # Reinforced: footing_depth + 8'
        # Non-reinforced: footing_depth - embedment
    },
    "rebar_editable": True,

    # Drawing views — FIXED (always all 4)
    "views": ["front", "side", "section_aa", "section_bb"],

    # BOM table — always shown, auto-populated
    "bom_table": True,

    # Ship/piece marks — auto-sequential
    "mark_prefix": {"ship": "C", "piece": "p", "rebar": "rb"},

    # Grouping — any component difference = new ship mark
    "grouping_rule": "any_difference_new_mark",

    # Coating
    "coating": "Cold Galv All Plain Steel & Welds",
    "coating_note": "Cold galv paint on welds and cut/plain steel edges only",

    # Connection bolts (BOM addition)
    "connection_bolts": {
        "qty_per_connection": 4,
        "editable": True,
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# RAFTER DEFAULTS
# ═══════════════════════════════════════════════════════════════════════════════

RAFTER_DEFAULTS = {
    # CEE body — same as columns
    "cee_size": "14x4x10GA",
    "cee_size_editable": False,
    "material_grade": "G90 80 KSI",
    "material_grade_editable": True,

    # Rafter length formula:
    # rafter_length = building_width - (2 * roofing_overhang) - (7\" if z_purlins)
    "length_formula": "width - 2*overhang - z_purlin_deduction",
    "length_editable": True,
    "roofing_overhang_ft": 1.0,           # Per side, editable
    "roofing_overhang_editable": True,
    "z_purlin_deduction_in": 7.0,         # 3.5\" per side if z-purlins
    "roofing_overhang_max_in": 32.5,      # 2'8.5\" max past rafter, error if exceeded

    # Stitch weld — same as columns, FIXED
    "stitch_weld": COLUMN_DEFAULTS["stitch_weld"],
    "stitch_weld_editable": False,

    # Purlin type
    "purlin_type": "z",                   # Default z-purlin, c-purlin option
    "purlin_type_editable": True,

    # Purlin clips
    "p1_clip": {
        "thickness": "1/8\"",
        "width": 6,             # inches
        "length": 10,           # inches
        "grade": "A572",
        "tek_screws_per": 8,
        "machine": "P1",
    },
    "p1_clip_editable": True,

    "p2_clip": {
        "thickness": "1/8\"",
        "width": 9,             # inches (user corrected from 8 to 9)
        "length": 24,           # inches (2'-0\")
        "grade": "A572",
        "welded_as_cap": True,  # Welded all around at rafter end
        "machine": "P1",
    },
    "p2_clip_editable": True,

    # p1 clip count — auto from purlin spacing, evenly distributed, never exceed max OC
    "p1_count_source": "auto_from_purlin_spacing",
    "purlin_spacing_max_exceed": False,  # Cannot exceed the specified OC distance

    # Splice rule
    "max_rafter_length_ft": 53.0,        # Max shipping/fabrication length
    "splice_max_distance_from_column_ft": 10.0,  # Splice within 10' of column
    "splice_plate": {
        "material": "10GA G90",
        "width": "20-3/4\"",
        "length": "1'-6\"",
        "fabrication": "roll_formed_shop",  # Roll formed in shop with holes punched
        "field_install": "welded_and_tek_screwed",  # Welded + tek screwed in field
        "machine": "C1",
    },

    # Multi-splice — add columns if needed, middle pieces no p2
    "multi_splice_add_columns": True,

    # Connection plate — same as column cap plate
    "connection_plate": COLUMN_DEFAULTS["cap_plate"],
    "connection_plate_editable": True,
    "connection_bolts": COLUMN_DEFAULTS["connection_bolts"],

    # Rebar — different rules from columns!
    "rebar": {
        "size": "#9",
        "grade": "A706",
        "reinforced_default": True,
        # REINFORCED rafter: 4 rebars at corners, welded inside, stitch welded
        #   Placement: 20' above each column, 20' between columns, within 5' of eave
        # NON-REINFORCED rafter: NO REBAR AT ALL
        # (This is different from columns which always have rebar)
        "reinforced_placement": {
            "above_column_ft": 20,
            "between_columns_ft": 20,
            "within_eave_ft": 5,
        },
        "qty_per_rafter_reinforced": 4,   # 1 per corner
        "qty_per_rafter_nonreinforced": 0,  # None!
    },
    "rebar_editable": True,

    # Drawing views — always all 4 + splice callout when applicable
    "views": ["top_purlin_layout", "side", "section_aa", "detail_callouts"],
    "splice_callout_when_applicable": True,

    # Purlin layout on drawing
    "purlin_layout_always_shown": True,
    "purlin_layout_measured_from": "one_consistent_end",
    "first_clip_is_p2_cap": True,

    # Purlin facing toggle on rafter drawing
    "show_purlin_facing_on_rafter": False,  # Default off, toggleable
    "show_purlin_facing_editable": True,

    # Wall panel overhang rules
    "wall_side_overhang_limit_in": 3.5,    # Side with wall: only 3.5\" past rafter
    "no_wall_overhang_default_ft": 1.0,    # Side without wall: user input, default 1'
    "max_overhang_past_rafter_in": 32.5,   # 2'8.5\" absolute max, error if exceeded

    # ── P6 End Plate (replaces P2 when angled purlins enabled) ──
    "p6_plate": {
        "thickness": "10GA",        # 0.135"
        "width": 9,                 # inches
        "length": 15,               # inches
        "grade": "A572",
        "weight_lbs": 5.06,         # each
        "overhang_in": 0.5,         # ½" overhang all around 8"×14" beam
        "purlin_holes": 0,          # no holes — purlins attach to P1 clips only
        "machine": "P1",
    },

    # ── Angled purlin configuration ──
    "angled_purlin_defaults": {
        "enabled": False,
        "default_angle_deg": 15,
        "min_angle_deg": 5,
        "max_angle_deg": 45,
        "all_clips_same_direction": True,   # NO mirroring on last clip
    },

    # ── P1 / P3 clearance constraints ──
    "p1_clearance_in": 0.5,                 # min P1 edge distance from rafter end
    "p3_min_edge_distance_in": 13.0,        # P3 center min from rafter end (½ of 26")
    "splice_p3_clearance_in": 14.0,         # min splice center to P3 center distance

    # ── Rebar stick layout (configurable) ──
    "rebar_max_stick_ft": 20.0,             # max individual stick length
    "rebar_end_gap_ft": 5.0,                # gap from rafter end to first rebar
    "rebar_bars_per_position": 4,           # 1 per corner
}

# ═══════════════════════════════════════════════════════════════════════════════
# PURLIN DEFAULTS
# ═══════════════════════════════════════════════════════════════════════════════

PURLIN_DEFAULTS = {
    # Z-purlin profile
    "type": "z",                           # Default z, c option
    "type_editable": True,
    "profile": {
        "height": 12,                      # inches
        "flange": 3.5,                     # inches
        "gauge": "12GA",
        "lip_angle": 45,                   # degrees (z-purlin)
        "lip_height": 0.75,               # inches (3/4\")
        "material": "G90",
        "coil_width": 20.125,             # inches (roll formed from this coil)
        "machine": "Z1",                   # Z-purlins on Z1; C-purlins on C1
    },
    "gauge_editable": True,

    # Length constraints
    "max_length_ft": 53.0,                # Hard limit — error if exceeded

    # Overhang rules
    "z_overhang_default_ft": 6.0,         # Z-purlins extend 6' past internal rafters
    "z_overhang_editable": True,
    "c_overhang_allowed": False,           # C-purlins: no overhang, land on center
    "c_max_span_rafters": 3,              # C-purlins can span up to 3 rafters if < 53'

    # Splice
    "splice_overlap_in": 6.0,            # 6\" overlap default
    "splice_overlap_editable": True,
    "splice_tek_screws": 8,              # #10 tek screws per splice
    "splice_location_from_rafter_ft": 6.0,  # 6' from rafter in mid-span
    "splice_location_editable": True,
    "splice_piece_length_in": 6.0,        # Splice piece default 6\", editable
    "splice_piece_length_editable": True,
    "splice_piece_sits_on_top": True,

    # End extension
    "end_extension_past_rafter_in": 4.0,  # 4\" past center of end rafter

    # Endcap
    "endcap": {
        "profile": "u_channel",           # No lips (both Z and C purlins)
        "inside_dim": 12,                 # inches
        "leg_height": 4,                  # inches
        "gauge": "12GA",                  # Same as purlin
        "material": "G90",
        "machine": "C1",
        "tek_screws_per_purlin": 4,       # 4 per connection (2 top + 2 bottom)
        "max_length_ft_in": "30'4\"",     # 30'4\" max
        "max_length_in": 364,             # 30*12 + 4 = 364 inches
        "must_land_on_purlin_if_split": True,
        "qty_per_building": 2,            # One per building end
        "shipping": "nested_alternating", # U-up, N-down
    },

    # Facing rules
    "facing": {
        "eave_purlins": "top_flange_faces_outward",
        "interior_purlins": "alternate_direction",
        "odd_number_rule": "first_two_on_bottom_side_face_same",
    },

    # First/Last mirror
    "first_last_same_length": True,       # Same length, just flipped Z orientation
    "first_last_mirror": True,

    # Purlin-to-rafter connection
    "purlin_to_clip_tek_screws": 8,

    # Non-solar: no pre-punched holes
    "solar_prepunch": False,
    "solar_toggle": False,                # Pinned for future

    # Ship marks
    "mark_prefix": "PG",                 # PG-A1, PG-A2, PG-B1...
    "group_per_building": True,

    # Drawing content (non-solar)
    "drawing_content": ["3d_profile_view", "length", "bom", "title_block"],

    # C-purlin splice
    "c_purlin_splice_channel": True,      # Separate U-channel splice piece (rare)

    # Wall girt endcap option
    "wall_girt_endcap_default": False,    # Optional, default NO
    "wall_girt_endcap_length_source": "wall_panel_length",
}

# ═══════════════════════════════════════════════════════════════════════════════
# WALL DEFAULTS
# ═══════════════════════════════════════════════════════════════════════════════

WALL_DEFAULTS = {
    "available_on_tee": False,            # NOT available on TEE carports
    "back_column_offset_in": 19,          # 19\" from center of column to back rafter

    # Wall girts
    "girt_spacing_default_ft": 5.0,       # Default 5' OC, independent of roof purlin spacing
    "girt_spacing_editable": True,
    "girt_type": "z",                     # Same Z-purlin profile as roof
    "girt_same_rules_as_purlins": True,   # Same overhang, splice, 53' max, endcap rules

    # Wall panels
    "panel_material": "spartan_rib",      # Same as roofing
    "panel_orientation": "vertical",      # Top to bottom
    "panel_coverage_in": 35.79,           # From 48\" 29GA G50 coil
    "panel_ground_clearance_in": 6.0,     # Default 6\" off ground, editable
    "panel_ground_clearance_editable": True,
    "panel_max_length_warning_ft": 20.0,  # Warning if > 20'
    "panel_max_length_warning_msg": "Proceed with caution — this may be too tall for wall panels.",

    # Wall panel length formula:
    # panel_length = clear_height + 14\" (rafter) + 3\" (purlin) - ground_clearance
    #                - 3.5\" (if Z girts, NOT if C girts)
    "panel_length_additions": {
        "rafter_depth_in": 14,
        "purlin_clearance_in": 3,
    },
    "panel_length_deductions": {
        "z_girt_in": 3.5,                # Deduct if Z-girts used
        "c_girt_in": 0,                  # No deduction for C-girts
    },

    # No doors, windows, or openings
    "allow_openings": False,
}

# ═══════════════════════════════════════════════════════════════════════════════
# ROOFING DEFAULTS
# ═══════════════════════════════════════════════════════════════════════════════

ROOFING_DEFAULTS = {
    "material": "spartan_rib",
    "coil": "48\" 29GA G50",
    "coverage_in": 35.79,
    "machine": "SPARTAN",

    # Panel split — same logic as BOM (nearest purlin to center)
    "split_at_center": True,
    "overlap_in": 3.0,                    # 3\" overlap at panel split

    # Roofing does NOT extend past end rafters
    "end_rafter_overhang": False,

    # Roofing overhang rules (eave direction)
    # Interacts with wall panels — see RAFTER_DEFAULTS for full rules
    # Side with wall: max 3.5\" past rafter
    # Side without wall: user input, default 1', max 2'8.5\"

    # Stacking
    "stacking": PANEL_STACK_LIMITS,
}

# ═══════════════════════════════════════════════════════════════════════════════
# SAG ROD DEFAULTS
# ═══════════════════════════════════════════════════════════════════════════════

SAG_ROD_DEFAULTS = {
    "profile": "2\"x2\" angle",
    "gauge": "16GA",
    "machine": "ANGLE",
    "qty_per_rafter": 2,                  # 2 rods per rafter
    "pieces_per_rod": 2,                  # Split at panel seam (front + back)
    "tek_screws_per_purlin": 2,           # 2 per purlin connection
    "orientation": "parallel_to_rafters",  # Runs parallel to rafters and endcaps
    "attachment": "underside_of_purlins",
    "no_prepunch": True,
    "bundle_size": 10,                    # Sticker per 10
    "drawing_type": "cut_list",
}

# ═══════════════════════════════════════════════════════════════════════════════
# HURRICANE STRAP DEFAULTS
# ═══════════════════════════════════════════════════════════════════════════════

STRAP_DEFAULTS = {
    "width_in": 1.5,
    "length_in": 24,
    "gauge": "10GA",
    "material": "G90",
    "machine": "P1",
    "shape": "rectangle",                 # Simple rectangle, no bends
    "qty_per_rafter": 4,                  # 2 purlins in from each eave × 2 per position
    "bundle_size": 10,                    # Sticker per 10
    "drawing_type": "cut_list",
    "ships_as_is": True,                  # No additional fabrication
}

# ═══════════════════════════════════════════════════════════════════════════════
# TRIM DEFAULTS
# ═══════════════════════════════════════════════════════════════════════════════

TRIM_DEFAULTS = {
    "profile": "2\"x2\"",
    "source": "purchased",                # From Home Depot, not fabricated
    "stick_length_ft": 10,
    "screws_per_stick": 5,
    "attachment": "spartan_rib_roofing",
    "drawing_needed": False,              # Just BOM line item
}

# ═══════════════════════════════════════════════════════════════════════════════
# TITLE BLOCK DEFAULTS
# ═══════════════════════════════════════════════════════════════════════════════

TITLE_BLOCK = {
    "fabricator": {
        "name": "Structures America",
        "address": "14369 FM 1314",
        "city_state_zip": "Conroe, TX 77302",
        "phone": "505-270-1877",
        "website": "www.StructuresAmerica.com",
    },
    "default_customer": {
        "name": "Titan Carports Inc.",
        "editable": True,  # Can be changed per project from Customer DB
    },
    "fields": [
        "project_name", "job_number", "drawing_number", "date",
        "drawn_by", "checked_by", "revision", "sheet_number",
        "customer_name", "project_location",
    ],
    "revision_block": {
        "columns": ["rev_letter", "date", "description", "approved_by"],
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# STANDARD NOTES (appear on every drawing)
# ═══════════════════════════════════════════════════════════════════════════════

STANDARD_NOTES = {
    "material": "A36 UNO",
    "paint": "Cold Galv All Plain Steel & Welds",
    "holes": "15/16\" UNO",
    "no_paint": "Do Not Paint at the Locations Indicated",
    "tolerance": "All measurements must be +/- 1/16\"",
    "measure_direction": "START MEASUREMENTS FROM THIS SIDE",
    "design_review": (
        "DESIGN/REVIEW AUTHORITY: PLEASE REVIEW THIS DRAWING CAREFULLY. "
        "We assume NO responsibility for the accuracy of the information in "
        "the contract documents including architectural and structural drawings. "
        "This drawing represents our best interpretation of the contract documents. "
        "Unless Noted Otherwise when it is returned from approval it will be assumed "
        "that the design authority confirms that we have correctly interpreted the "
        "contract documents, and we are released to begin fabrication using these drawings."
    ),
}

# ═══════════════════════════════════════════════════════════════════════════════
# SHIPPING ORDER (fixed, always the same)
# ═══════════════════════════════════════════════════════════════════════════════

SHIPPING_ORDER = [
    "Columns",
    "Rafters",
    "Purlins",
    "Sag Rods / Hurricane Straps",
    "Decking / Roofing",
    "Trim",
]

# Shipping note: appears on every drawing AND separate manifest
# Truck-filling rule: if a part is done out of order but fills remaining weight, ship it

# ═══════════════════════════════════════════════════════════════════════════════
# ABBREVIATIONS TABLE (appears on detailed drawings)
# ═══════════════════════════════════════════════════════════════════════════════

ABBREVIATIONS = {
    "O.C.": "On Center Measurements",
    "\"": "Inches",
    "'": "Feet",
    "WPS": "Welding Procedure Specifications",
    "CEE": "C Purlin",
    "ZEE": "Z Purlin",
    "GA": "Gauge",
    "KSI": "One thousand pounds per square inch",
    "PL": "Plate Steel",
    "G90": "Galvanized Coated",
    "UNO": "Unless Noted Otherwise",
    "TYP": "Typical",
}

# ═══════════════════════════════════════════════════════════════════════════════
# DRAWING OUTPUT SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

DRAWING_OUTPUT = {
    "format": "PDF",
    "paper_size": (8.5, 11),              # inches (Letter)
    "orientation": "landscape",
    "vector_quality": True,               # Clean zoom on phone/tablet
    "dpi": 300,
}

# ═══════════════════════════════════════════════════════════════════════════════
# WORK ORDER FLOW
# ═══════════════════════════════════════════════════════════════════════════════

WORK_ORDER_FLOW = {
    "steps": [
        "shop_drawings_finalized",
        "work_order_created",
        "manual_approval",               # Must be manually OK'd
        "stickers_printed",              # Prints from office
    ],
    "unapproved_action": "queued_as_task",  # Goes to task queue if not approved
    "qr_scan_actions": [
        "start_job",                     # Worker scans to start
        "finish_job",                    # Worker scans to finish
    ],
    "tracking": {
        "who_scanned": True,
        "start_time": True,
        "finish_time": True,
        "duration": True,                # Auto-calculated
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# BOM ADDITIONS (from shop drawing Q&A — items to add to BOM calculator)
# ═══════════════════════════════════════════════════════════════════════════════

BOM_ADDITIONS_NEEDED = {
    "bolt_assemblies": {
        "description": "Column/rafter connection bolt assemblies",
        "qty_per_connection": 4,
        "editable": True,
    },
    "endcap_u_channels": {
        "description": "Purlin endcap U-channels",
        "qty_per_building_end": 1,        # 1 piece (may need splitting if > 30'4\")
        "max_length_in": 364,
    },
    "tek_screws_endcaps": {
        "description": "Tek screws for endcap-to-purlin connections",
        "qty_per_purlin": 4,
    },
    "tek_screws_splices": {
        "description": "#10 tek screws for purlin splices",
        "qty_per_splice": 8,
    },
    "tek_screws_sag_rods": {
        "description": "Tek screws for sag rod-to-purlin connections",
        "qty_per_purlin": 2,
    },
    "c_purlin_splice_channels": {
        "description": "U-channel splice pieces for C-purlins (rare)",
        "when": "c_purlin_splice_needed",
    },
    "wall_girt_endcaps": {
        "description": "Wall girt endcaps (optional)",
        "when": "wall_girt_endcap_enabled",
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# INVENTORY TRACKING (items to track with reorder alerts)
# ═══════════════════════════════════════════════════════════════════════════════

INVENTORY_ITEMS = {
    "rebar_by_size": {
        "sizes": ["#5", "#6", "#7", "#8", "#9", "#10", "#11"],
        "unit": "40' sticks",
        "grade": "A706",
        "track_reorder": True,
    },
    "cap_plates": {
        "description": "PL 3/4\" x 14\" x 26\" A572",
        "unit": "EA",
        "track_reorder": True,
    },
    "gusset_triangles": {
        "description": "PL 3/8\" 6\"x6\" A572",
        "unit": "EA",
        "track_reorder": True,
    },
    "coil_stock": {
        "description": "Track linear feet remaining per coil type",
        "types": [
            "c_section_23_10ga",
            "z_purlin_20_12ga",
            "plate_6_10ga",
            "plate_9_10ga",
            "strap_15_10ga",
            "angle_4_16ga",
            "spartan_rib_48_29ga",
        ],
        "unit": "LFT",
        "track_reorder": True,
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# QUESTIONNAIRE DATA MODEL
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ShopDrawingConfig:
    """Complete configuration for generating shop drawings for a project.
    Pre-populated from BOM data, editable by user via questionnaire."""

    # Project info
    job_code: str = ""
    project_name: str = ""
    customer_name: str = "Titan Carports Inc."
    project_location: str = ""
    drawn_by: str = ""
    checked_by: str = ""

    # Building parameters (from BOM)
    building_width_ft: float = 40.0
    building_length_ft: float = 120.0
    clear_height_ft: float = 14.0
    roof_pitch_deg: float = 1.19          # 1/4:12 default
    frame_type: str = "tee"               # "tee" or "2post"
    n_frames: int = 5
    bay_sizes: List[float] = field(default_factory=lambda: [30.0])
    overhang_ft: float = 0.0
    embedment_ft: float = 4.333
    footing_depth_ft: float = 0.0
    column_buffer_ft: float = 0.5

    # Column config
    col_material_grade: str = "G90 80 KSI"
    col_cap_plate_thickness: str = "3/4\""
    col_cap_plate_width_in: float = 14.0
    col_cap_plate_length_in: float = 26.0
    col_bolt_hole_dia: str = "15/16\""
    col_gusset_thickness: str = "3/8\""
    col_gusset_leg_in: float = 6.0
    col_rebar_size: str = "#9"
    col_reinforced: bool = True
    col_connection_bolts: int = 4
    col_pitch_deg: float = 1.19
    col_clear_height_ft: float = 14.0
    col_width_ft: float = 40.0
    col_footing_ft: float = 10.0
    col_above_grade_ft: float = 8.0
    col_cut_allowance_in: float = 6.0

    # Rafter config
    raft_material_grade: str = "G90 80 KSI"
    raft_roofing_overhang_ft: float = 1.0
    raft_purlin_type: str = "z"           # "z" or "c"
    raft_p1_width_in: float = 6.0
    raft_p1_length_in: float = 10.0
    raft_p2_width_in: float = 9.0
    raft_p2_length_in: float = 24.0
    raft_reinforced: bool = True
    raft_rebar_size: str = "#9"
    raft_rebar_max_stick_ft: float = 20.0
    raft_rebar_end_gap_ft: float = 5.0
    raft_show_purlin_facing: bool = False
    raft_angled_purlins: bool = False
    raft_purlin_angle_deg: float = 15.0
    raft_column_mode: str = "auto"          # "auto", "spacing", "manual"
    raft_column_spacing_ft: float = 25.0
    raft_column_count_manual: int = 1
    raft_column_positions_manual: str = ""
    raft_front_col_position_ft: float = 0.0
    raft_splice_location_ft: float = 0.0

    # Purlin config
    purlin_type: str = "z"
    purlin_gauge: str = "12GA"
    purlin_spacing_ft: float = 5.0
    purlin_overhang_ft: float = 6.0
    purlin_splice_overlap_in: float = 6.0
    purlin_splice_location_ft: float = 6.0
    purlin_splice_piece_length_in: float = 6.0
    purlin_end_extension_in: float = 4.0

    # Wall config
    has_back_wall: bool = False
    has_side_walls: bool = False
    wall_girt_spacing_ft: float = 5.0
    wall_girt_type: str = "z"
    wall_panel_ground_clearance_in: float = 6.0
    wall_girt_endcaps: bool = False

    # Roofing config
    roofing_split_at_center: bool = True
    roofing_overlap_in: float = 3.0

    # Solar toggle (future)
    is_solar: bool = False

    def to_dict(self) -> dict:
        """Serialize to JSON-safe dictionary."""
        d = {}
        for k, v in self.__dict__.items():
            if isinstance(v, list):
                d[k] = list(v)
            else:
                d[k] = v
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "ShopDrawingConfig":
        """Deserialize from dictionary."""
        cfg = cls()
        for k, v in data.items():
            if hasattr(cfg, k):
                setattr(cfg, k, v)
        return cfg

    @classmethod
    def from_bom_data(cls, bom_result: dict, project_info: dict = None) -> "ShopDrawingConfig":
        """Create config pre-populated from BOM calculation results."""
        cfg = cls()
        geo = bom_result.get("geometry", {})
        if geo:
            cfg.building_width_ft = geo.get("width_ft", 40.0)
            cfg.building_length_ft = geo.get("length_ft", 120.0)
            cfg.clear_height_ft = geo.get("clear_height_ft", 14.0)
            cfg.roof_pitch_deg = geo.get("slope_deg", 1.19)
            cfg.n_frames = geo.get("n_frames", 5)
            cfg.overhang_ft = geo.get("overhang_ft", 0.0)
            cfg.embedment_ft = geo.get("embedment_ft", 4.333)
            cfg.footing_depth_ft = geo.get("footing_depth_ft", 0.0)
            cfg.purlin_spacing_ft = geo.get("purlin_spacing_ft", 5.0)
            cfg.frame_type = geo.get("frame_type", "tee")
            cfg.raft_purlin_type = geo.get("purlin_type", "z").lower()
            cfg.purlin_type = cfg.raft_purlin_type
            cfg.raft_roofing_overhang_ft = geo.get("roofing_overhang_ft", 1.0)
            cfg.col_above_grade_ft = geo.get("above_grade_ft", 8.0)
            cfg.col_cut_allowance_in = geo.get("cut_allowance_in", 6.0)
            cfg.raft_angled_purlins = geo.get("angled_purlins", False)
            cfg.raft_purlin_angle_deg = geo.get("purlin_angle_deg", 15.0)
            cfg.raft_column_mode = geo.get("column_mode", "auto")
            # Column drawing fields
            cfg.col_pitch_deg = geo.get("slope_deg", 1.19)
            cfg.col_clear_height_ft = geo.get("clear_height_ft", 14.0)
            cfg.col_width_ft = geo.get("width_ft", 40.0)
            cfg.col_footing_ft = geo.get("footing_depth_ft", 10.0)

            col_positions = geo.get("col_positions", [])
            if col_positions:
                # Derive bay sizes from column positions
                bays = []
                for i in range(1, len(col_positions)):
                    bays.append(round(col_positions[i] - col_positions[i - 1], 2))
                cfg.bay_sizes = bays

        if project_info:
            cfg.job_code = project_info.get("job_code", "")
            cfg.project_name = project_info.get("project_name", "")
            cfg.project_location = project_info.get("location", "")

        return cfg


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER: Calculate rafter length
# ═══════════════════════════════════════════════════════════════════════════════

def calc_rafter_length(width_ft: float, overhang_ft: float = 1.0,
                       use_z_purlins: bool = True) -> float:
    """
    Rafter cut length in feet.
    rafter_length = building_width - (2 * overhang) - (7\" if z-purlins)
    """
    deduction_ft = 2.0 * overhang_ft
    if use_z_purlins:
        deduction_ft += 7.0 / 12.0  # 7 inches = 0.583 ft
    return width_ft - deduction_ft


def calc_wall_panel_length_in(clear_height_ft: float, ground_clearance_in: float = 6.0,
                               use_z_girts: bool = True) -> float:
    """
    Wall panel cut length in inches.
    panel = clear_height + 14\"(rafter) + 3\"(purlin) - ground_clearance - 3.5\"(if Z girts)
    """
    length_in = clear_height_ft * 12.0
    length_in += 14.0   # rafter depth
    length_in += 3.0    # purlin clearance
    length_in -= ground_clearance_in
    if use_z_girts:
        length_in -= 3.5
    return length_in


def calc_gusset_hypotenuse(leg_a: float, leg_b: float, pitch_deg: float,
                            side: str = "uphill") -> float:
    """
    Calculate gusset triangle hypotenuse adjusted for roof pitch.
    Uphill side = longer hypotenuse, Downhill side = shorter.
    leg_a and leg_b in inches, returns hypotenuse in inches.
    """
    base_hyp = math.sqrt(leg_a ** 2 + leg_b ** 2)
    angle_rad = math.radians(pitch_deg)
    if side == "uphill":
        # Plate angles away from column face — wider gap
        adjustment = leg_a * math.tan(angle_rad)
        return math.sqrt(leg_a ** 2 + (leg_b + adjustment) ** 2)
    else:
        # Plate angles toward column face — tighter gap
        adjustment = leg_a * math.tan(angle_rad)
        return math.sqrt(leg_a ** 2 + (leg_b - adjustment) ** 2)


def calc_purlin_groups(building_length_ft: float, bay_sizes: List[float],
                       overhang_ft: float, purlin_overhang_ft: float = 6.0,
                       splice_overlap_in: float = 6.0,
                       end_extension_in: float = 4.0,
                       use_overhang: bool = True,
                       max_length_ft: float = 53.0) -> List[dict]:
    """
    Calculate purlin groups (lengths and quantities) for a building.

    Returns list of dicts: [{"group": 1, "length_ft": 46.0, "type": "first"}, ...]
    """
    # Build rafter positions from bay sizes and overhang
    positions = []
    pos = overhang_ft
    positions.append(pos)
    for bay in bay_sizes:
        pos += bay
        positions.append(pos)

    n_rafters = len(positions)
    splice_overlap_ft = splice_overlap_in / 12.0
    end_ext_ft = end_extension_in / 12.0
    groups = []

    if not use_overhang or n_rafters <= 2:
        # Simple: purlins land on center of each rafter
        for i in range(n_rafters - 1):
            span = positions[i + 1] - positions[i]
            length = span
            # Add endcap extension at building ends
            if i == 0:
                length += end_ext_ft
            if i == n_rafters - 2:
                length += end_ext_ft
            g_type = "first" if i == 0 else ("last" if i == n_rafters - 2 else "middle")
            groups.append({
                "group": i + 1,
                "length_ft": round(length, 4),
                "type": g_type,
                "start_pos": positions[i],
                "end_pos": positions[i + 1],
            })
    else:
        # Overhang mode: first and last purlin extend past internal rafters
        # First purlin: from building start, past first internal rafter by overhang
        first_end = positions[1] + purlin_overhang_ft
        first_len = first_end - positions[0] + end_ext_ft
        groups.append({
            "group": 1,
            "length_ft": round(first_len, 4),
            "type": "first",
            "start_pos": positions[0],
            "end_pos": first_end,
        })

        # Last purlin: from overhang before last internal rafter to building end
        last_start = positions[-2] - purlin_overhang_ft
        last_len = positions[-1] - last_start + end_ext_ft
        groups.append({
            "group": 3,  # Will be renumbered
            "length_ft": round(last_len, 4),
            "type": "last",
            "start_pos": last_start,
            "end_pos": positions[-1],
        })

        # Middle purlin(s): fill gaps between first and last with splice overlap
        middle_start = first_end
        middle_end = last_start
        middle_span = middle_end - middle_start
        if middle_span > 0:
            middle_len = middle_span + 2 * splice_overlap_ft
            groups.insert(1, {
                "group": 2,
                "length_ft": round(middle_len, 4),
                "type": "middle",
                "start_pos": middle_start,
                "end_pos": middle_end,
            })

        # Renumber groups
        for i, g in enumerate(groups):
            g["group"] = i + 1

    # Validate max length
    errors = []
    for g in groups:
        if g["length_ft"] > max_length_ft:
            errors.append(
                f"Group {g['group']} ({g['type']}) is {g['length_ft']:.1f}' — "
                f"exceeds {max_length_ft}' max. User must input lengths manually."
            )
            g["error"] = True

    return groups
