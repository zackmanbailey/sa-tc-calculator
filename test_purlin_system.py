#!/usr/bin/env python3
"""
TitanForge — COMPREHENSIVE PURLIN INTEGRATION SYSTEM TEST
==========================================================
Tests the ENTIRE purlin pipeline end-to-end across all 5 phases,
with special attention to bugs and regressions caught during development.

Coverage:
  Phase 0-1: Piece-break engine, BOM integration, P1/P2 plates
  Phase 2:   Solar mode — layout engine, hardware BOM, TC estimator wiring
  Phase 3:   4-way comparison engine, auto-select best
  Phase 4:   Angled purlins — cos(angle) length, P6 plates, visualization
  Phase 5:   Splice callouts, facing indicators, cut list, PDF generators

Known bugs tested (regressions):
  BUG-1: Geometry dict overwrite — solar_layout stored before geometry dict reset
  BUG-2: Solar bolt stack qty must be panels × 4
  BUG-3: Angled P6 replaces P2 only (not P1), and P2 count drops to 0
  BUG-4: Piece-break cos_factor applied to wrong dimension
  BUG-5: Compare mode must store results AFTER geometry dict init
  BUG-6: C-purlin should have NO extension past rafter (only Z gets 6')
  BUG-7: Single-bay building should not crash piece-break engine
  BUG-8: purlin_angle_deg=90 should produce zero adjustment (standard mode)
"""

import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ─────────────────────────────────────────────────────────────
# Test framework
# ─────────────────────────────────────────────────────────────
_pass = 0
_fail = 0
_section = ""

def section(name):
    global _section
    _section = name
    print(f"\n{'─'*60}")
    print(f"  {name}")
    print(f"{'─'*60}")

def check(name, condition, detail=""):
    global _pass, _fail
    if condition:
        print(f"  ✓ {name}")
        _pass += 1
    else:
        msg = f"  ✗ FAIL: {name}"
        if detail:
            msg += f"  ({detail})"
        print(msg)
        _fail += 1


# =================================================================
# SECTION 1: PIECE-BREAK ENGINE (Phase 0-1)
# =================================================================
section("1. PIECE-BREAK ENGINE — Z-Purlin")

from calc.purlin_layout import calc_purlin_pieces, PurlinLayoutResult

# Standard Z-purlin, 4 equal bays of 30'
r = calc_purlin_pieces([30.0, 30.0, 30.0, 30.0], n_purlin_lines=9, purlin_type="Z")
check("Returns PurlinLayoutResult", isinstance(r, PurlinLayoutResult))
check("Has pieces", len(r.pieces) > 0)
check("Total LF > 0", r.total_lf > 0, f"got {r.total_lf}")
check("Total pieces > 0", r.total_pieces > 0, f"got {r.total_pieces}")
check("No errors", len(r.errors) == 0, str(r.errors))
check("No warnings", len(r.warnings) == 0, str(r.warnings))

# P1/P2 plate counts for standard perpendicular Z-purlin
check("P1 per rafter = n_purlin_lines - 2 = 7", r.p1_per_rafter == 7,
      f"got {r.p1_per_rafter}")
check("P2 per rafter = 2", r.p2_per_rafter == 2,
      f"got {r.p2_per_rafter}")
check("Endcap plates = 0 (perpendicular)", r.endcap_plates_total == 0)
check("P1 total = 7 × 5 rafters = 35", r.p1_total == 35,
      f"got {r.p1_total}")
check("P2 total = 2 × 5 = 10", r.p2_total == 10,
      f"got {r.p2_total}")

# Each piece should have valid fields
for p in r.pieces:
    check(f"Piece '{p.label}' length > 0", p.length_in > 0)
    check(f"Piece '{p.label}' total_qty > 0", p.total_qty > 0)


section("1b. PIECE-BREAK ENGINE — C-Purlin")

# BUG-6: C-purlin should NOT extend past rafter (only Z gets 6' extension)
# C-purlins CAN span multiple bays (up to max length), so 2x20' + 2x8" end ext = 41'-4" is valid
rc = calc_purlin_pieces([20.0, 20.0], n_purlin_lines=7, purlin_type="C")
check("C-purlin returns pieces", len(rc.pieces) > 0)
check("C-purlin no errors", len(rc.errors) == 0)
# C-purlin should NOT have Z-purlin's 6' extension (72") on each end
# Max for 2 bays: 2×20'=480" + 2×8" end_ext = 496" — that's fine (spans both bays)
# But it should NOT be 480 + 2×72" = 624" (that would be Z-extension leaking in)
for p in rc.pieces:
    z_extension_inflated = (20.0 * 2 * 12) + (72 * 2)  # 624" if Z-ext leaked
    check(f"C-purlin piece not inflated by Z-extension (6' each side)",
          p.length_in < z_extension_inflated,
          f"got {p.length_in}in, Z-inflated would be {z_extension_inflated}in")


section("1c. PIECE-BREAK ENGINE — Error Conditions")

# Bay too large
r_big = calc_purlin_pieces([55.0], n_purlin_lines=5, purlin_type="Z")
check("Bay > max length produces error", len(r_big.errors) > 0)
check("Error mentions 'exceeds'", "exceeds" in r_big.errors[0].lower())

# No bays (empty list)
r_empty = calc_purlin_pieces([], n_purlin_lines=5, purlin_type="Z")
check("Empty bays produces error", len(r_empty.errors) > 0)
check("Error mentions 'at least'", "at least" in r_empty.errors[0].lower())

# BUG-7: Single-bay building should NOT crash
r_single = calc_purlin_pieces([25.0], n_purlin_lines=6, purlin_type="Z")
check("Single bay: no crash", True)  # If we got here, it didn't crash
check("Single bay: has pieces", len(r_single.pieces) > 0)
check("Single bay: no errors", len(r_single.errors) == 0)
check("Single bay: total LF > 0", r_single.total_lf > 0)


# =================================================================
# SECTION 2: BOM CALCULATOR (Phases 1-2)
# =================================================================
section("2. BOM CALCULATOR — Standard Building")

from calc.bom import BOMCalculator, ProjectInfo, BuildingConfig

proj = ProjectInfo(name="SystemTest", job_code="SYS-001", wind_speed_mph=115)
calc = BOMCalculator(proj)

cfg = BuildingConfig()
cfg.width_ft = 40.0
cfg.length_ft = 120.0
cfg.n_frames = 5
cfg.frame_type = "tee"
cfg.purlin_type = "Z"
cfg.purlin_spacing_ft = 5.0
cfg.purlin_gauge = "12GA"
cfg.solar_mode = False

result = calc.calculate_building(cfg)
check("BOM returns items", len(result.line_items) > 0, f"got {len(result.line_items)}")
check("Sell total > $0", result.total_sell_price > 0, f"${result.total_sell_price:,.2f}")
check("Geometry dict populated", len(result.geometry) > 0)
check("Geometry has n_purlin_lines", "n_purlin_lines" in result.geometry)
check("Geometry has purlin_spacing_ft", "purlin_spacing_ft" in result.geometry)

# Standard mode should NOT have solar keys
check("No solar_layout in standard mode", "solar_layout" not in result.geometry)
check("No solar_comparison in standard mode", "solar_comparison" not in result.geometry)

# Purlin line items exist
purlin_items = [i for i in result.line_items if "purlin" in i.description.lower()]
check("Has purlin line items", len(purlin_items) > 0, f"got {len(purlin_items)}")

# P1 and P2 plate items exist
p1_items = [i for i in result.line_items if "P1" in i.description]
p2_items = [i for i in result.line_items if "P2" in i.description]
check("Has P1 plate items", len(p1_items) > 0)
check("Has P2 plate items (standard mode)", len(p2_items) > 0)


# =================================================================
# SECTION 3: SOLAR MODE (Phase 2)
# =================================================================
section("3. SOLAR MODE — Landscape")

cfg_sol = BuildingConfig()
cfg_sol.width_ft = 30.0
cfg_sol.length_ft = 90.0
cfg_sol.n_frames = 4
cfg_sol.frame_type = "tee"
cfg_sol.purlin_type = "Z"
cfg_sol.purlin_spacing_ft = 5.0
cfg_sol.purlin_gauge = "12GA"
cfg_sol.solar_mode = True
cfg_sol.solar_panel_width_mm = 1134.0
cfg_sol.solar_panel_length_mm = 2278.0
cfg_sol.solar_orientation = "landscape"
cfg_sol.solar_panels_across = 6
cfg_sol.solar_panels_along = 8
cfg_sol.solar_dim_mode = "panel_count"
cfg_sol.solar_install_per_panel = 125.0

res_sol = calc.calculate_building(cfg_sol)
geo_sol = res_sol.geometry

# BUG-1 REGRESSION: solar_layout must survive geometry dict init
check("solar_layout present (BUG-1 regression)",
      "solar_layout" in geo_sol and len(geo_sol["solar_layout"]) > 0,
      f"keys: {sorted(geo_sol.keys())}")

check("solar_total_panels in geometry", "solar_total_panels" in geo_sol)
check("solar_install_per_panel in geometry", "solar_install_per_panel" in geo_sol)

total_panels = geo_sol.get("solar_total_panels", 0)
check("Total panels = 6 × 8 = 48", total_panels == 48, f"got {total_panels}")

# BUG-2: Bolt stack qty = panels × 4
bolt_items = [i for i in res_sol.line_items if "Bolt Stack" in i.description]
check("Has bolt stack line item", len(bolt_items) > 0)
if bolt_items:
    bolt_qty = bolt_items[0].qty
    check(f"Bolt stacks = 48 × 4 = 192", bolt_qty == 192, f"got {bolt_qty}")

# Solar hardware categories exist
solar_hw = [i for i in res_sol.line_items
            if "Solar" in i.category or "solar" in i.category.lower()]
check("Has solar hardware items", len(solar_hw) > 0, f"got {len(solar_hw)}")

# TC estimator data: install_per_panel should be passed through
check("Install per panel = 125",
      geo_sol.get("solar_install_per_panel") == 125.0,
      f"got {geo_sol.get('solar_install_per_panel')}")


section("3b. SOLAR MODE — Portrait")

cfg_port = BuildingConfig()
cfg_port.width_ft = 30.0
cfg_port.length_ft = 90.0
cfg_port.n_frames = 4
cfg_port.frame_type = "tee"
cfg_port.purlin_type = "Z"
cfg_port.purlin_spacing_ft = 5.0
cfg_port.purlin_gauge = "12GA"
cfg_port.solar_mode = True
cfg_port.solar_panel_width_mm = 1134.0
cfg_port.solar_panel_length_mm = 2278.0
cfg_port.solar_orientation = "portrait"
cfg_port.solar_panels_across = 6
cfg_port.solar_panels_along = 8
cfg_port.solar_dim_mode = "panel_count"

res_port = calc.calculate_building(cfg_port)
geo_port = res_port.geometry

check("Portrait: solar_layout present", "solar_layout" in geo_port)
sl_port = geo_port.get("solar_layout", {})
check("Portrait: orientation = portrait",
      sl_port.get("orientation") == "portrait",
      f"got {sl_port.get('orientation')}")

# Portrait and landscape should produce DIFFERENT building dims
sl_land = geo_sol.get("solar_layout", {})
if sl_land and sl_port:
    check("Portrait vs Landscape: different purlin spacing",
          abs(sl_land.get("purlin_spacing_ft", 0) - sl_port.get("purlin_spacing_ft", 0)) > 0.01,
          f"land={sl_land.get('purlin_spacing_ft')}, port={sl_port.get('purlin_spacing_ft')}")


# =================================================================
# SECTION 4: COMPARISON ENGINE (Phase 3)
# =================================================================
section("4. 4-WAY COMPARISON ENGINE")

from calc.solar_layout import SolarPanelSpec, SolarLayoutConfig, calc_solar_comparison

# Standalone comparison
comp_cfg = SolarLayoutConfig(
    panel=SolarPanelSpec(),
    orientation="compare",
    panels_across=5,
    panels_along=20,
    mode="panel_count",
)
comp = calc_solar_comparison(comp_cfg)

check("Has 'results' key", "results" in comp)
check("Has 'best' key", "best" in comp)
check("4 results", len(comp["results"]) == 4, f"got {len(comp['results'])}")

labels = {r["label"] for r in comp["results"]}
expected = {"Landscape + C-purlin", "Landscape + Z-purlin",
            "Portrait + C-purlin", "Portrait + Z-purlin"}
check("All 4 labels present", labels == expected, f"got {labels}")

# Results sorted by purlin LF ascending (best first)
lf_vals = [r["purlin_total_lf"] for r in comp["results"]]
check("Results sorted by purlin LF", lf_vals == sorted(lf_vals),
      f"got {lf_vals}")

check("Best = first result", comp["best"] == comp["results"][0]["label"])

# Each result has required keys
for r in comp["results"]:
    check(f"  {r['label']}: has layout", "layout" in r)
    check(f"  {r['label']}: purlin_total_lf > 0", r["purlin_total_lf"] > 0)


section("4b. COMPARISON VIA BOM ENGINE")

cfg_cmp = BuildingConfig()
cfg_cmp.width_ft = 40.0
cfg_cmp.length_ft = 180.0
cfg_cmp.clear_height_ft = 12.0
cfg_cmp.solar_mode = True
cfg_cmp.solar_orientation = "compare"
cfg_cmp.solar_panels_across = 5
cfg_cmp.solar_panels_along = 20
cfg_cmp.solar_panel_width_mm = 992.0
cfg_cmp.solar_panel_length_mm = 2108.0
cfg_cmp.solar_dim_mode = "panel_count"

res_cmp = calc.calculate_building(cfg_cmp)
geo_cmp = res_cmp.geometry

# BUG-5 REGRESSION: comparison data stored AFTER geometry dict init
check("solar_comparison present (BUG-5 regression)",
      "solar_comparison" in geo_cmp)
check("solar_best_option present",
      "solar_best_option" in geo_cmp)
check("solar_layout present (from best option)",
      "solar_layout" in geo_cmp and len(geo_cmp.get("solar_layout", {})) > 0)

if "solar_comparison" in geo_cmp:
    cmp_results = geo_cmp["solar_comparison"]["results"]
    check("BOM comparison has 4 results", len(cmp_results) == 4)
    best_label = geo_cmp.get("solar_best_option", "")
    check("Best option stored", len(best_label) > 0, f"'{best_label}'")


# =================================================================
# SECTION 5: ANGLED PURLINS (Phase 4)
# =================================================================
section("5. ANGLED PURLINS — Length Adjustment")

# BUG-4: cos_factor must be applied correctly
# angle_deg = 45 from aisle → angle_from_perp = 45° → cos(45) = 0.7071
r_std = calc_purlin_pieces([30.0, 30.0, 30.0], n_purlin_lines=8, purlin_type="Z")
r_45 = calc_purlin_pieces([30.0, 30.0, 30.0], n_purlin_lines=8, purlin_type="Z",
                           angled_purlins=True, purlin_angle_deg=45.0)

ratio_45 = r_45.total_lf / r_std.total_lf
expected_ratio = 1.0 / math.cos(math.radians(45))  # 1.4142
check(f"45° angle: LF ratio ~1.414", abs(ratio_45 - expected_ratio) < 0.01,
      f"got {ratio_45:.4f}, expected {expected_ratio:.4f}")
check("45° angle: angled flag set", r_45.angled is True)
check("45° angle: angle_from_perp = 45", r_45.angle_from_perpendicular_deg == 45.0)

# BUG-3: Angled → P2 drops to 0, endcap plates appear
check("Angled: P2 per rafter = 0 (BUG-3)", r_45.p2_per_rafter == 0,
      f"got {r_45.p2_per_rafter}")
check("Angled: P1 per rafter = n_purlin_lines = 8", r_45.p1_per_rafter == 8,
      f"got {r_45.p1_per_rafter}")
check("Angled: endcap plates per rafter = 2", r_45.endcap_plates_per_rafter == 2,
      f"got {r_45.endcap_plates_per_rafter}")
n_rafters_angled = len([30.0, 30.0, 30.0]) + 1  # 4 rafters
check(f"Angled: endcap total = 2 × {n_rafters_angled} = {2 * n_rafters_angled}",
      r_45.endcap_plates_total == 2 * n_rafters_angled)


section("5b. ANGLED PURLINS — BOM P6 Plates")

cfg_ang = BuildingConfig()
cfg_ang.width_ft = 40.0
cfg_ang.length_ft = 120.0
cfg_ang.n_frames = 5
cfg_ang.frame_type = "tee"
cfg_ang.purlin_type = "Z"
cfg_ang.purlin_spacing_ft = 5.0
cfg_ang.purlin_gauge = "12GA"
cfg_ang.solar_mode = False
cfg_ang.angled_purlins = True
cfg_ang.purlin_angle_deg = 60  # 30° from perpendicular

res_ang = calc.calculate_building(cfg_ang)
p6_items = [i for i in res_ang.line_items if "P6" in i.description]
p2_items_ang = [i for i in res_ang.line_items if "P2" in i.description
                and "End Cap" in i.description]

check("Angled BOM: has P6 plates", len(p6_items) > 0, f"got {len(p6_items)}")
check("Angled BOM: P2 end caps absent or qty=0",
      len(p2_items_ang) == 0 or all(i.qty == 0 for i in p2_items_ang),
      f"P2 items: {[(i.description, i.qty) for i in p2_items_ang]}")

# Angled BOM should cost MORE than standard (longer purlins + plates)
check("Angled sell > standard sell",
      res_ang.total_sell_price > result.total_sell_price,
      f"angled=${res_ang.total_sell_price:,.2f} vs std=${result.total_sell_price:,.2f}")


section("5c. ANGLED PURLINS — Edge Case: 90° (standard)")

# BUG-8: purlin_angle_deg=90 means perpendicular = NO adjustment
r_90 = calc_purlin_pieces([30.0, 30.0], n_purlin_lines=6, purlin_type="Z",
                           angled_purlins=True, purlin_angle_deg=90.0)
r_normal = calc_purlin_pieces([30.0, 30.0], n_purlin_lines=6, purlin_type="Z",
                               angled_purlins=False)

check("90° angle: NOT flagged as angled", r_90.angled is False,
      f"angled={r_90.angled}")
check("90° angle: LF same as standard",
      abs(r_90.total_lf - r_normal.total_lf) < 0.01,
      f"90°={r_90.total_lf} vs normal={r_normal.total_lf}")
check("90° angle: P2 same as standard",
      r_90.p2_per_rafter == r_normal.p2_per_rafter)


section("5d. ANGLED PURLINS — Various Angles Monotonic")

# LF should increase as angle deviates more from perpendicular
angles = [85, 75, 60, 45, 30, 15]
prev_lf = 0
for ang in angles:
    ra = calc_purlin_pieces([25.0, 25.0], n_purlin_lines=6, purlin_type="Z",
                             angled_purlins=True, purlin_angle_deg=ang)
    check(f"  {ang}°: LF={ra.total_lf:.1f} > prev={prev_lf:.1f}",
          ra.total_lf > prev_lf)
    prev_lf = ra.total_lf


# =================================================================
# SECTION 6: TEMPLATE COMPILATION (Phase 5)
# =================================================================
section("6. TEMPLATE & GENERATOR COMPILATION")

from templates.purlin_drawing_v2 import PURLIN_DRAWING_V2_HTML
check("purlin_drawing_v2 compiles", len(PURLIN_DRAWING_V2_HTML) > 1000)
check("Has splice-zone group", "splice-zone" in PURLIN_DRAWING_V2_HTML)
check("Has facing group", "'facing'" in PURLIN_DRAWING_V2_HTML)
check("Has needsSplice param", "needsSplice" in PURLIN_DRAWING_V2_HTML)
check("Has splicePositionFt param", "splicePositionFt" in PURLIN_DRAWING_V2_HTML)
check("Has facing param", "facing:" in PURLIN_DRAWING_V2_HTML)
check("Has P6 plate drawing", "P6 PLATE" in PURLIN_DRAWING_V2_HTML)
check("Has P1 clip drawing", "P1 CLIP" in PURLIN_DRAWING_V2_HTML)
check("Has solar hole spec", "SOLAR_SPEC" in PURLIN_DRAWING_V2_HTML)
check("Has angle toggle", "toggleAngled" in PURLIN_DRAWING_V2_HTML)
check("Has solar toggle", "toggleSolar" in PURLIN_DRAWING_V2_HTML)

try:
    from shop_drawings.purlin_gen import generate_purlin_drawing
    check("purlin_gen imports OK", True)
except Exception as e:
    check(f"purlin_gen imports OK", False, str(e))

try:
    from shop_drawings.cutlist_gen import generate_cutlist_drawing, _calc_purlin_cutlist_items
    check("cutlist_gen imports OK", True)
except Exception as e:
    check(f"cutlist_gen imports OK", False, str(e))

try:
    from templates.sa_calc import SA_CALC_HTML
    check("sa_calc compiles", len(SA_CALC_HTML) > 1000)
    check("SA calc has solar_mode toggle", "solar_mode" in SA_CALC_HTML)
except Exception as e:
    check(f"sa_calc compiles", False, str(e))

try:
    from templates.tc_quote import TC_QUOTE_HTML
    check("tc_quote compiles", len(TC_QUOTE_HTML) > 1000)
    check("TC quote has solar install", "solar" in TC_QUOTE_HTML.lower())
except Exception as e:
    check(f"tc_quote compiles", False, str(e))


# =================================================================
# SECTION 7: CUT LIST GENERATOR (Phase 5)
# =================================================================
section("7. PURLIN CUT LIST GENERATOR")

from shop_drawings.config import ShopDrawingConfig

scfg = ShopDrawingConfig()
scfg.building_width_ft = 40
scfg.building_length_ft = 120
scfg.n_frames = 5
scfg.purlin_type = "Z"
scfg.purlin_spacing_ft = 5
scfg.purlin_gauge = "12GA"

items = _calc_purlin_cutlist_items(scfg)
check("Cut list returns items", len(items) > 0, f"got {len(items)}")

# Should have a TOTAL summary row
total_rows = [i for i in items if i["mark"] == "TOTAL"]
check("Has TOTAL summary row", len(total_rows) == 1)
if total_rows:
    check("TOTAL description includes LF",
          "LF" in total_rows[0]["description"],
          total_rows[0]["description"])

# No error rows
err_rows = [i for i in items if i["mark"] in ("⛔", "⚠")]
check("No error/warning rows", len(err_rows) == 0,
      f"got {len(err_rows)}: {[i['description'] for i in err_rows]}")


section("7b. CUT LIST — Multi-Bay Building")

scfg2 = ShopDrawingConfig()
scfg2.building_width_ft = 50
scfg2.building_length_ft = 200
scfg2.n_frames = 8
scfg2.purlin_type = "Z"
scfg2.purlin_spacing_ft = 4
scfg2.purlin_gauge = "12GA"

items2 = _calc_purlin_cutlist_items(scfg2)
check("Multi-bay: returns items", len(items2) > 0)
check("Multi-bay: more pieces than single-bay", len(items2) >= len(items))


# =================================================================
# SECTION 8: SOLAR + ANGLED COMBO
# =================================================================
section("8. SOLAR + ANGLED COMBINED")

cfg_combo = BuildingConfig()
cfg_combo.width_ft = 30.0
cfg_combo.length_ft = 90.0
cfg_combo.n_frames = 4
cfg_combo.frame_type = "tee"
cfg_combo.purlin_type = "Z"
cfg_combo.purlin_spacing_ft = 5.0
cfg_combo.purlin_gauge = "12GA"
cfg_combo.solar_mode = True
cfg_combo.solar_panel_width_mm = 1134.0
cfg_combo.solar_panel_length_mm = 2278.0
cfg_combo.solar_orientation = "landscape"
cfg_combo.solar_panels_across = 6
cfg_combo.solar_panels_along = 8
cfg_combo.solar_dim_mode = "panel_count"
cfg_combo.angled_purlins = True
cfg_combo.purlin_angle_deg = 60

res_combo = calc.calculate_building(cfg_combo)
geo_combo = res_combo.geometry

check("Solar+Angled: has solar_layout", "solar_layout" in geo_combo)
check("Solar+Angled: has items", len(res_combo.line_items) > 0)
check("Solar+Angled: sell > 0", res_combo.total_sell_price > 0)

# Should have BOTH solar hardware AND P6 plates
solar_hw_combo = [i for i in res_combo.line_items
                  if "Bolt Stack" in i.description]
p6_combo = [i for i in res_combo.line_items if "P6" in i.description]
check("Combo: has bolt stacks", len(solar_hw_combo) > 0)
check("Combo: has P6 plates", len(p6_combo) > 0)


# =================================================================
# SECTION 9: HANDLER DATA FLOW (Phase 5)
# =================================================================
section("9. HANDLER — Splice & Facing Data Passthrough")

# Verify tf_handlers.py passes splice and facing data
try:
    with open("tf_handlers.py", "r") as f:
        handler_src = f.read()

    check("Handler passes needs_splice", "needs_splice" in handler_src)
    check("Handler passes splice_position_ft", "splice_position_ft" in handler_src)
    check("Handler passes splice_overlap_in", "splice_overlap_in" in handler_src)
    check("Handler passes splice_tek_screws", "splice_tek_screws" in handler_src)
    check("Handler passes facing", "'facing'" in handler_src)
    check("Handler passes is_first", "'is_first'" in handler_src)
    check("Handler passes is_last", "'is_last'" in handler_src)
except Exception as e:
    check(f"Handler file readable", False, str(e))


# =================================================================
# SECTION 10: GEOMETRY DICT INTEGRITY (Regression)
# =================================================================
section("10. GEOMETRY DICT INTEGRITY — All Modes")

# Standard mode
check("Standard: geometry is a dict", isinstance(result.geometry, dict))
check("Standard: n_purlin_lines > 0",
      result.geometry.get("n_purlin_lines", 0) > 0)

# Solar mode
check("Solar: geometry has solar_layout",
      "solar_layout" in geo_sol and isinstance(geo_sol["solar_layout"], dict))
check("Solar: solar_layout not empty",
      len(geo_sol.get("solar_layout", {})) > 0)
check("Solar: n_purlin_lines > 0",
      geo_sol.get("n_purlin_lines", 0) > 0)

# Compare mode
check("Compare: geometry has solar_comparison",
      "solar_comparison" in geo_cmp)
check("Compare: solar_layout not empty (from best)",
      len(geo_cmp.get("solar_layout", {})) > 0)

# Angled mode
check("Angled: geometry is a dict", isinstance(res_ang.geometry, dict))
check("Angled: n_purlin_lines > 0",
      res_ang.geometry.get("n_purlin_lines", 0) > 0)


# =================================================================
# SECTION 11: PURLIN PDF GENERATOR (Phase 5)
# =================================================================
section("11. PURLIN PDF GENERATOR — Source Code Checks")

try:
    with open("shop_drawings/purlin_gen.py", "r") as f:
        pg_src = f.read()

    check("PDF gen: has splice hole circles", "circle" in pg_src)
    check("PDF gen: has splice overlap zone", "overlap" in pg_src.lower())
    check("PDF gen: has facing direction indicator", "FACING" in pg_src)
    check("PDF gen: facing right for first", "is_first" in pg_src)
    check("PDF gen: facing left for last", "is_last" in pg_src)
    check("PDF gen: alternating for middle", "ALTERNATING" in pg_src)
except Exception as e:
    check(f"PDF gen source readable", False, str(e))


# =================================================================
# SECTION 12: CROSS-MODE CONSISTENCY
# =================================================================
section("12. CROSS-MODE CONSISTENCY CHECKS")

# Standard and solar should produce different purlin spacing
std_spacing = result.geometry.get("purlin_spacing_ft", 0)
sol_spacing = geo_sol.get("purlin_spacing_ft", 0)
check("Solar purlin spacing differs from standard (solar overrides dims)",
      abs(std_spacing - sol_spacing) > 0.001 or std_spacing == 0 or sol_spacing == 0,
      f"std={std_spacing}, sol={sol_spacing}")

# Angled building should have same n_purlin_lines as standard (angle doesn't change count)
std_lines = result.geometry.get("n_purlin_lines", 0)
ang_lines = res_ang.geometry.get("n_purlin_lines", 0)
check("Angled same purlin line count as standard",
      std_lines == ang_lines,
      f"std={std_lines}, angled={ang_lines}")


# =================================================================
# SUMMARY
# =================================================================
print(f"\n{'═'*60}")
print(f"  FINAL RESULTS: {_pass} passed, {_fail} failed, {_pass + _fail} total")
print(f"{'═'*60}")

if _fail > 0:
    print(f"\n  ⚠ {_fail} TESTS FAILED — investigate above\n")
    sys.exit(1)
else:
    print(f"\n  ✓ ALL {_pass} TESTS PASSED — system is solid\n")
    sys.exit(0)
