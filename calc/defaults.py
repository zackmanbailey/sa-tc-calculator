"""
Structures America Material Takeoff Calculator
Default values, material specs, and pricing.
"""

import math

# ─────────────────────────────────────────────
# COMPANY INFO
# ─────────────────────────────────────────────
COMPANY = {
    "name": "Structures America",
    "address": "14369 FM 1314",
    "city_state_zip": "Conroe, TX 77302",
    "contact_name": "Haley McClendon",
    "contact_phone": "(832) 791-8965",
    "contact_email": "haley@structuresamerica.com",
    "origin": "Conroe, TX",
}

# ─────────────────────────────────────────────
# 7 PRE-SLIT COIL TYPES
# price_per_lb is user-editable per project/coil
# ─────────────────────────────────────────────
COILS = {
    "c_section_23": {
        "id": "c_section_23",
        "name": "23\" 10GA C-Section (Columns & Rafters)",
        "width_in": 23,
        "gauge": "10GA",
        "coating": "G90",
        "lbs_per_lft": 10.83,
        "price_per_lb": 0.82,
        "roll_weight_lbs": 5000,
        "use": "C-14\"x4\"x10GA box beam/column",
        "note": "TWO C-sections welded to make one box beam or column",
    },
    "z_purlin_20": {
        "id": "z_purlin_20",
        "name": "20.125\" 12GA Z-Purlin",
        "width_in": 20.125,
        "gauge": "12GA",
        "coating": "G90",
        "lbs_per_lft": 7.43,
        "price_per_lb": 0.82,
        "roll_weight_lbs": 5000,
        "use": "Z-12\"x3.5\"x12GA purlins",
        "note": "Roll-formed in-house",
    },
    "angle_4_16ga": {
        "id": "angle_4_16ga",
        "name": "4\" 16GA Angle (Sag Rods)",
        "width_in": 4,
        "gauge": "16GA",
        "coating": "G90",
        "lbs_per_lft": 0.8656,
        "price_per_lb": 0.86,
        "roll_weight_lbs": 4000,
        "use": "2\"x2\" angle sag rods",
        "note": "Max piece length 20'-3\"",
    },
    "spartan_rib_48": {
        "id": "spartan_rib_48",
        "name": "48\" 29GA Spartan Rib Panel",
        "width_in": 48,
        "gauge": "29GA",
        "coating": "G50",
        "lbs_per_lft": 2.81,
        "price_per_lb": 0.7950,
        "roll_weight_lbs": 7500,
        "use": "Spartan Rib roof panels",
        "panel_coverage_in": 35.79,
        "panel_coverage_ft": 35.79 / 12,
        "valleys_per_panel": 5,
        "note": "35.79\" coverage width, 5 valleys per panel, coil rolled to panel in shop",
    },
    "plate_6_10ga": {
        "id": "plate_6_10ga",
        "name": "6\" 10GA Plate (Interior Purlin Plates)",
        "width_in": 6,
        "gauge": "10GA",
        "coating": "G90",
        "lbs_per_lft": 2.83,
        "price_per_lb": 0.82,
        "roll_weight_lbs": 3000,
        "use": "10\"x6\" interior purlin-to-rafter plates",
        "plate_length_in": 10,
        "plate_length_ft": 10 / 12,
        "holes": 8,
    },
    "plate_9_10ga": {
        "id": "plate_9_10ga",
        "name": "9\" 10GA Plate (Exterior/Eave Purlin Plates)",
        "width_in": 9,
        "gauge": "10GA",
        "coating": "G90",
        "lbs_per_lft": 4.24,
        "price_per_lb": 0.82,
        "roll_weight_lbs": 3000,
        "use": "24\"x9\" exterior purlin-to-rafter plates",
        "plate_length_in": 24,
        "plate_length_ft": 24 / 12,
        "holes": 8,
    },
    "strap_15_10ga": {
        "id": "strap_15_10ga",
        "name": "1.5\" 10GA Strap (Hurricane Straps & Sag Braces)",
        "width_in": 1.5,
        "gauge": "10GA",
        "coating": "G90",
        "lbs_per_lft": 0.706,
        "price_per_lb": 0.82,
        "roll_weight_lbs": 3000,
        "use": "Hurricane straps & bottom flange braces (1.5\"x28\")",
        "default_length_in": 28,
    },
}

# ─────────────────────────────────────────────
# PURCHASED / OUTSIDE VENDOR ITEMS
# ─────────────────────────────────────────────
PURCHASED_ITEMS = {
    "cap_plate": {
        "id": "cap_plate",
        "name": "3/4\"x26\"x14\" Cap Plate",
        "description": "Column cap / rafter end plate, 3/4\" steel",
        "price_each": 95.00,
        "qty_per_column": 2,   # 1 for column top, 1 for rafter connection
    },
    "gusset_triangle": {
        "id": "gusset_triangle",
        "name": "6\"x6\"x3/8\" Gusset Triangle",
        "description": "Column gusset triangle (slope-dependent hypotenuse)",
        "price_each": 13.00,
        "qty_per_column": 4,   # 2 sizes x 2 pcs each
        # Gusset hypotenuse (ft) values vary by roof slope.
        # Two sizes per column — one for each angle of the joint.
        # Key = slope degrees, value = [(hyp_ft, qty), ...]
        "sizes_by_slope": {
            1.2:  [(8.3960, 2), (8.5737, 2)],
            5.0:  [(8.1071, 2), (8.8473, 2)],
            7.5:  [(7.9103, 2), (9.0199, 2)],   # interpolated — confirm with field
            10.0: [(7.7135, 2), (9.1925, 2)],
        },
    },
}

# ─────────────────────────────────────────────
# REBAR SPECS (Katy Steel Co.)
# Size selected via dropdown #5-#11 per building
# ─────────────────────────────────────────────
REBAR = {
    "supplier": "Katy Steel Co., Katy TX",
    "grade": "A706 Black Rebar",
    "stick_length_ft": 40,
    "price_per_lb": 0.62,
    "sizes": {
        "#5":  {"lbs_per_lft": 1.043, "dia_in": 0.625},
        "#6":  {"lbs_per_lft": 1.502, "dia_in": 0.75},
        "#7":  {"lbs_per_lft": 2.044, "dia_in": 0.875},
        "#8":  {"lbs_per_lft": 2.670, "dia_in": 1.0},
        "#9":  {"lbs_per_lft": 3.400, "dia_in": 1.128},
        "#10": {"lbs_per_lft": 4.303, "dia_in": 1.27},
        "#11": {"lbs_per_lft": 5.313, "dia_in": 1.41},
    },
    "embedment_ft": 4.333,   # 4'-4" standard
}

# ─────────────────────────────────────────────
# REBAR AUTO-SELECTION (used when user picks "Auto")
# ─────────────────────────────────────────────
def get_rebar_size(column_type, building_width_ft, wind_mph, bay_size_ft):
    """
    Auto-select rebar size. Returns {"column": "#6", "beam": "#7"} etc.
    column_type: '2post' or 'tee'
    """
    result = {"column": None, "beam": None}
    if column_type == "2post":
        if wind_mph >= 139 and building_width_ft >= 45:
            result["column"] = "#6"; result["beam"] = "#8"
        elif wind_mph >= 130 and building_width_ft >= 40:
            result["column"] = "#6"; result["beam"] = "#7"
        elif building_width_ft >= 35:
            result["column"] = "#6"; result["beam"] = "#7"
    else:  # tee
        if building_width_ft >= 45:
            result["column"] = "#9"; result["beam"] = "#8"
        elif building_width_ft >= 35:
            result["column"] = "#6"; result["beam"] = "#7"
        else:
            result["column"] = "#6"; result["beam"] = "#6"
    return result

# ─────────────────────────────────────────────
# PURLIN SPACING AUTO-CALCULATION
# Default based on max bay span; user can override
# ─────────────────────────────────────────────
def get_purlin_spacing(bay_size_ft):
    """Return default purlin spacing (ft OC) based on bay/rafter span."""
    if bay_size_ft <= 30.0:
        return 5.0
    elif bay_size_ft <= 34.333:   # 34'-4"
        return 4.0
    else:
        return 3.5

# ─────────────────────────────────────────────
# ROOF PITCH OPTIONS
# ─────────────────────────────────────────────
PITCH_OPTIONS = {
    "1/4:12": {"label": "1/4\":12  (1.2 deg)", "deg": math.degrees(math.atan(0.25/12))},
    "5deg":   {"label": "5 degrees",            "deg": 5.0},
    "7.5deg": {"label": "7.5 degrees",          "deg": 7.5},
    "10deg":  {"label": "10 degrees",           "deg": 10.0},
}

ROOF_SLOPES = {
    "rv_storage": {"deg": math.degrees(math.atan(0.25/12)), "ratio": "1/4:12"},
    "solar":      {"deg": 5.0,                               "ratio": "5 deg"},
}

# ─────────────────────────────────────────────
# SCREWS
# ─────────────────────────────────────────────
SCREWS = {
    "tek_neoprene": {
        "id": "tek_neoprene",
        "name": "3/4\" TEK w/ Neoprene Washer",
        "description": "Roof panel + wall panels to purlin/girt — 3/4\" length",
        # Screws per panel per purlin row:
        #   eave rows (row 1 & last) + panel seam overlap row = 10 (5 valleys x 2 screws)
        #   all other interior rows = 5 (5 valleys x 1 screw)
        "per_eave_or_seam_row": 10,
        "per_field_row": 5,
        "valleys_per_panel": 5,
        "box_qty": 3000,            # screws per box
        "price_per_box": 383.22,    # $ per 3,000-count box
        "price_per_screw": 383.22 / 3000,   # ≈ $0.12774 each
    },
    "tek_structural": {
        "id": "tek_structural",
        "name": "3/4\" TEK No Washer",
        "description": "Structural connections (purlin-to-rafter plates) — 3/4\" length",
        "per_plate": 8,
        "box_qty": 4000,            # screws per box
        "price_per_box": 19.55,     # $ per 4,000-count box
        "price_per_screw": 19.55 / 4000,    # ≈ $0.0048875 each
    },
    "tek_endcap": {
        "id": "tek_endcap",
        "name": "#10 TEK — Endcap-to-Purlin",
        "description": "Endcap U-channel to purlin connections — 4 per purlin (2 top + 2 bottom)",
        "per_purlin": 4,
        "box_qty": 4000,
        "price_per_box": 19.55,
        "price_per_screw": 19.55 / 4000,
    },
    "tek_splice": {
        "id": "tek_splice",
        "name": "#10 TEK — Purlin Splice",
        "description": "Purlin splice overlap connections — 8 per splice",
        "per_splice": 8,
        "box_qty": 4000,
        "price_per_box": 19.55,
        "price_per_screw": 19.55 / 4000,
    },
    "tek_sag_rod": {
        "id": "tek_sag_rod",
        "name": "#10 TEK — Sag Rod-to-Purlin",
        "description": "Sag rod to purlin connections — 2 per purlin crossing",
        "per_purlin": 2,
        "box_qty": 4000,
        "price_per_box": 19.55,
        "price_per_screw": 19.55 / 4000,
    },
    "stitch": {
        "id": "stitch",
        "name": "1/4\"-14 x 7/8\" Stitch Screw",
        "description": "Trim connections",
        "per_trim_stick": 5,
        "price_per_screw": 0.05,    # placeholder — update when known
    },
}

# ─────────────────────────────────────────────
# BOLT ASSEMBLIES (Column-to-Rafter connections)
# ─────────────────────────────────────────────
BOLT_ASSEMBLIES = {
    "connection_bolt": {
        "id": "connection_bolt",
        "name": "3/4\" A325 Bolt Assembly",
        "description": "3/4\" x 4-1/2\" A325 bolt w/ nut + 2 washers (connection bolt)",
        "bolt_dia": "3/4\"",
        "bolt_length": "4-1/2\"",
        "grade": "A325",
        "components": ["bolt", "nut", "flat_washer", "lock_washer"],
        "qty_per_connection": 4,      # 4 bolts per column-to-rafter connection
        "price_per_assembly": 3.75,   # bolt + nut + 2 washers
        "box_qty": 50,
        "price_per_box": 187.50,      # 50 × $3.75
    },
}

# ─────────────────────────────────────────────
# ENDCAP U-CHANNELS (purlin endcaps at building ends)
# ─────────────────────────────────────────────
ENDCAP_U_CHANNELS = {
    "profile": "12\"x4\" U-Channel (no lip)",
    "inside_dim_in": 12,
    "leg_height_in": 4,
    "gauge": "12GA",
    "material": "G90",
    "lbs_per_lft": 7.43,             # Same as Z-purlin coil
    "coil_id": "z_purlin_20",        # Roll formed from same 20.125\" coil on C1 machine
    "max_single_piece_in": 364,      # 30'4\" max before needing splice
    "qty_per_building_end": 1,       # 1 continuous piece (or spliced) per end
    "tek_screws_per_purlin": 4,      # 4 tek screws per purlin connection (2 top + 2 bottom)
    "shipping": "nested_alternating",
}

# ─────────────────────────────────────────────
# TRIM (OPTIONAL) — all 4 sides with 3" overlap
# ─────────────────────────────────────────────
TRIM = {
    "supplier": "Home Depot",
    "type": "J-channel",
    "stick_length_ft": 10,
    "overlap_in": 3,
    "screws_per_stick": 5,
    "sides": "All 4 sides (front, back, and both gable ends)",
}

# ─────────────────────────────────────────────
# WASTE FACTORS
# ─────────────────────────────────────────────
WASTE_FACTORS = {
    "10GA": 0.03,
    "12GA": 0.03,
    "16GA": 0.02,
    "29GA": 0.05,
    "rebar": 0.05,
    "concrete": 0.05,
}

# ─────────────────────────────────────────────
# WELDING & FINISHING CONSUMABLES
# ─────────────────────────────────────────────
WELDING_CONSUMABLES = {
    "description": "Welding Wire/Rod, Welding Gas, Cold Galvanized Paint",
    "cost_per_5000_sqft": 300.0,
    "note": "Combined consumables per 5,000 sq ft of building footprint",
}

# ─────────────────────────────────────────────
# FABRICATION LABOR
# Fabrication only — not installation (install happens on-site)
# No labor applied to: hardware, screws, trim (purchased/pre-made)
# ─────────────────────────────────────────────
LABOR = {
    "crew_size": 4,
    "hourly_rate": 30.0,          # blended average $/hr
    "hours_per_day": 8,
    "daily_rate": 960.0,          # 4 crew × $30 × 8 hrs
    "overhead_pct": 10.0,         # supervision, insurance, equipment wear
    "effective_daily_rate": 1056.0,  # $960 × 1.10
    "rates": {
        # Columns and rafters: full assembly (roll-form, tack, cap plates,
        # gussets, finish weld, QA/QC, cold galvanize)
        "box_pieces_per_day": 5,
        # Roll-based rates (full crew, per day):
        "purlin_rolls_per_day": 5,    # roll_weight = 5,000 lbs
        "panel_rolls_per_day": 3,     # roll_weight = 7,500 lbs
        "angle_rolls_per_day": 2,     # roll_weight = 4,000 lbs
    },
    "note": (
        "Total days = max(col_days + rafter_days, purlin_days, panel_days, angle_days). "
        "Labor marked up at same % as materials on customer quote."
    ),
}

# ─────────────────────────────────────────────
# PROJECT DEFAULTS
# ─────────────────────────────────────────────
DEFAULTS = {
    "clear_height_ft": 14.0,
    "max_bay_ft": 36.0,
    "markup_pct": 35.0,
    "footing_dia_in": 24,
    "footing_depth_ft": 10.0,
    # Rafter-to-Purlin Straps (merged: was hurricane_straps + bottom_braces)
    "straps_per_rafter": 4,           # 4 per rafter (1 purlin in from each eave × 2 per position)
    "strap_length_in": 28,
    # Sag rods
    "sag_rod_max_length_ft": 20.25,   # 20'-3"
    "sag_rod_overlap_in": 3,
    # Options
    "include_trim": False,
    "include_back_wall": False,
    "include_end_walls": False,
    "include_side_walls": False,
    "include_rafter_rebar": False,
    "include_labor": True,
    # Project
    "wind_speed_mph": 115,
    "building_type": "2post",
    "pitch_key": "1/4:12",
    "embedment_ft": 4.333,            # 4'-4"
    "column_buffer_ft": 0.5,          # 6"
    "reinforced": True,
    "rebar_col_size": "auto",
    "rebar_beam_size": "auto",
    "rebar_rafter_size": "#9",        # default for rafter rebar
    "welding_cost_per_5000sqft": 300.0,
}

# Wind speed defaults by state
WIND_SPEEDS_BY_STATE = {
    "TX": 115, "NM": 115, "CO": 115, "FL": 140,
    "CA": 115, "AZ": 115, "NV": 115, "OK": 130,
    "KS": 130, "NE": 130, "Default": 115,
}

# Footing depth by state
FOOTING_DEPTHS_BY_STATE = {
    "TX": 10.0, "NM": 10.0, "CO": 10.0, "FL": 12.0,
    "CA": 10.0, "Default": 10.0,
}
