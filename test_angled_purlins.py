#!/usr/bin/env python3
"""
TitanForge Phase 4 — Angled Purlins End-to-End Test
=====================================================
Tests angled purlin visualization, BOM integration (P6 vs P2 plates),
length adjustment (divide by cos(angle)), and standard mode regression.
"""

import sys, os, math, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

passed = 0
failed = 0

def test(name, condition):
    global passed, failed
    if condition:
        print(f"  PASS {name}")
        passed += 1
    else:
        print(f"  FAIL {name}")
        failed += 1


# ===================================================================
print("\n== TEST 1: Purlin Drawing V2 Template Compiles ==")
# ===================================================================
from templates.purlin_drawing_v2 import PURLIN_DRAWING_V2_HTML

test("purlin_drawing_v2 HTML generated", len(PURLIN_DRAWING_V2_HTML) > 1000)
test("Contains PURLIN_CONFIG placeholder", "PURLIN_CONFIG" in PURLIN_DRAWING_V2_HTML)
test("Contains SVG element", "<svg" in PURLIN_DRAWING_V2_HTML.lower())


# ===================================================================
print("\n== TEST 2: Angled Purlin JS Variables Present ==")
# ===================================================================
test("angledPurlins state var in JS", "var angledPurlins = false" in PURLIN_DRAWING_V2_HTML)
test("purlinAngleDeg state var in JS", "var purlinAngleDeg = 90" in PURLIN_DRAWING_V2_HTML)
test("toggleAngled function defined", "function toggleAngled()" in PURLIN_DRAWING_V2_HTML)
test("onAngleChange function defined", "function onAngleChange()" in PURLIN_DRAWING_V2_HTML)


# ===================================================================
print("\n== TEST 3: Angled Purlin UI Controls Present ==")
# ===================================================================
test("Angled toggle button in HTML", 'id="btnAngled"' in PURLIN_DRAWING_V2_HTML)
test("Angle input in HTML", 'id="inpPurlinAngle"' in PURLIN_DRAWING_V2_HTML)
test("Angle input min=5", 'min="5"' in PURLIN_DRAWING_V2_HTML)
test("Angle input max=45", 'max="45"' in PURLIN_DRAWING_V2_HTML)


# ===================================================================
print("\n== TEST 4: Angled Purlin Length Calculation (Math) ==")
# ===================================================================
# The drawing JS computes: cutLen = spanIn / cos(angleFromPerp)
# where angleFromPerp = 90 - purlinAngleDeg
# For purlinAngleDeg = 45: angleFromPerp = 45 degrees
# cos(45) = 0.7071, so length multiplier = 1.4142

span_in = 25 * 12  # 25 ft span = 300 inches

# Standard (90 degrees = perpendicular)
angle_std = 90
angle_from_perp_std = 90 - angle_std  # 0 degrees
cos_std = math.cos(math.radians(angle_from_perp_std))
cut_len_std = span_in / cos_std
test("Standard (90deg): cut length = span", abs(cut_len_std - span_in) < 0.001)

# Angled at 45 degrees from aisle
angle_45 = 45
angle_from_perp_45 = 90 - angle_45  # 45 degrees
cos_45 = math.cos(math.radians(angle_from_perp_45))
cut_len_45 = span_in / cos_45
expected_multiplier = 1.0 / cos_45  # ~1.4142
test("45deg: multiplier is ~1.414", abs(expected_multiplier - math.sqrt(2)) < 0.001)
test("45deg: cut length > standard", cut_len_45 > cut_len_std)
test("45deg: cut length = span * 1.414", abs(cut_len_45 - span_in * math.sqrt(2)) < 0.1)
test("45deg: cut length ~424.26 inches", abs(cut_len_45 - 424.264) < 0.1)

# Angled at 15 degrees from aisle
angle_15 = 15
angle_from_perp_15 = 90 - angle_15  # 75 degrees
cos_15 = math.cos(math.radians(angle_from_perp_15))
cut_len_15 = span_in / cos_15
test("15deg: cut length > standard", cut_len_15 > cut_len_std)
test("15deg: cut length ~1158 inches", abs(cut_len_15 - span_in / math.cos(math.radians(75))) < 0.1)

# Angled at 75 degrees from aisle (close to perpendicular)
angle_75 = 75
angle_from_perp_75 = 90 - angle_75  # 15 degrees
cos_75 = math.cos(math.radians(angle_from_perp_75))
cut_len_75 = span_in / cos_75
test("75deg: cut length slightly > standard", cut_len_75 > cut_len_std)
test("75deg: multiplier ~1.035", abs(1.0/cos_75 - 1.0353) < 0.001)


# ===================================================================
print("\n== TEST 5: P6 vs P2 Plate Logic ==")
# ===================================================================
# P6: 9"x15" flat plate (angled purlins)
# P2: 9"x24" end cap (standard purlins)
p6_width = 9
p6_height = 15
p2_width = 9
p2_height = 24
p6_gauge_thick = 0.135  # 10GA
steel_density = 0.2836  # lbs per cubic inch

p6_weight = p6_width * p6_height * p6_gauge_thick * steel_density
p2_weight = p2_width * p2_height * p6_gauge_thick * steel_density

test("P6 weight ~5.17 lbs", abs(p6_weight - 5.17) < 0.1)
test("P2 weight ~8.27 lbs", abs(p2_weight - 8.27) < 0.1)
test("P6 lighter than P2", p6_weight < p2_weight)

# Verify the JS contains P6 plate references
test("P6 plate drawing in elevation view", "P6 PLATE (TYP)" in PURLIN_DRAWING_V2_HTML)
test("P6 end plate size shown", 'endPlateSize' in PURLIN_DRAWING_V2_HTML)
test("endPlateType computed in JS", "endPlateType" in PURLIN_DRAWING_V2_HTML)
test("P6 in BOM side panel", "'P6'" in PURLIN_DRAWING_V2_HTML)


# ===================================================================
print("\n== TEST 6: Endcap Plates in BOM ==")
# ===================================================================
# When angled, BOM should include P6 entries
test("P6 BOM row logic present", "End Plate (Angled)" in PURLIN_DRAWING_V2_HTML)
test("P6 qty = qty * 2", "p6Qty = p.qty * 2" in PURLIN_DRAWING_V2_HTML)
test("P6 weight calculation", "p6Wt = 9 * 15 * 0.135 * 0.2836" in PURLIN_DRAWING_V2_HTML)


# ===================================================================
print("\n== TEST 7: Standard Mode Unaffected ==")
# ===================================================================
# When angledPurlins is false, angleFromPerp = 0, cos(0) = 1, so cutLen = spanIn unchanged
angle_from_perp_0 = 0
cos_0 = math.cos(math.radians(angle_from_perp_0))
test("cos(0) = 1.0", abs(cos_0 - 1.0) < 0.0001)
test("Standard mode: no length change", abs(span_in / cos_0 - span_in) < 0.001)

# Verify JS logic: when angledPurlins is false, angleFromPerp = 0
test("JS: angleFromPerp = 0 when not angled",
     "var angleFromPerp = angledPurlins ? (90 - purlinAngleDeg) : 0" in PURLIN_DRAWING_V2_HTML)
test("JS: P2 when not angled",
     "var endPlateType = angledPurlins ? 'P6' : 'P2'" in PURLIN_DRAWING_V2_HTML)

# Standard mode should still have P1 clips
test("P1 clips shown in standard mode", "P1 CLIP (TYP)" in PURLIN_DRAWING_V2_HTML)


# ===================================================================
print("\n== TEST 8: Angle Visualization Elements ==")
# ===================================================================
# Angled mode should rotate the purlin group
test("SVG rotation transform", "rotate(" in PURLIN_DRAWING_V2_HTML)
test("Angle arc indicator (path)", "arcPath" in PURLIN_DRAWING_V2_HTML)
test("Angle label with degree symbol", "from \\u22A5" in PURLIN_DRAWING_V2_HTML)
test("Elevation title shows angle", "FROM AISLE" in PURLIN_DRAWING_V2_HTML)


# ===================================================================
print("\n== TEST 9: Config Application ==")
# ===================================================================
test("applyComponentConfig reads angled_purlins", "cfg.angled_purlins" in PURLIN_DRAWING_V2_HTML)
test("applyComponentConfig reads purlin_angle_deg", "cfg.purlin_angle_deg" in PURLIN_DRAWING_V2_HTML)


# ===================================================================
print("\n== TEST 10: Specs Panel Shows Angled Info ==")
# ===================================================================
test("Specs panel shows ANGLE when angled", "'ANGLE:'" in PURLIN_DRAWING_V2_HTML)
test("Specs panel shows CUT LEN when angled", "'CUT LEN:'" in PURLIN_DRAWING_V2_HTML)
test("Specs panel shows END PLATE when angled", "'END PLATE:'" in PURLIN_DRAWING_V2_HTML)


# ===================================================================
print("\n== TEST 11: Title Block Notes ==")
# ===================================================================
test("Title block includes angled purlin note", "ANGLED PURLINS" in PURLIN_DRAWING_V2_HTML)
test("Title block includes end plate note", "END PLATES" in PURLIN_DRAWING_V2_HTML)


# ===================================================================
print("\n== TEST 12: Rafter Drawing P6 Integration (Cross-check) ==")
# ===================================================================
try:
    from templates.rafter_drawing import RAFTER_DRAWING_HTML
    test("Rafter drawing compiles", len(RAFTER_DRAWING_HTML) > 1000)
    test("Rafter drawing has P6 logic", "P6" in RAFTER_DRAWING_HTML)
    test("Rafter drawing has angled_purlins", "angled_purlins" in RAFTER_DRAWING_HTML or "angledPurlins" in RAFTER_DRAWING_HTML)
except Exception as e:
    test(f"Rafter drawing import (got {e})", False)


# ===================================================================
print("\n== TEST 13: Purlin Layout Template Compiles ==")
# ===================================================================
try:
    from templates.purlin_layout import PURLIN_LAYOUT_HTML
    test("Purlin layout compiles", len(PURLIN_LAYOUT_HTML) > 1000)
    test("Purlin layout has computeLayout", "computeLayout" in PURLIN_LAYOUT_HTML)
except Exception as e:
    test(f"Purlin layout import (got {e})", False)


# ===================================================================
print("\n== TEST 14: End-to-End Building Scenario ==")
# ===================================================================
# Simulate a 40' wide x 60' long building, 5' purlin spacing
# Angled purlins at 45 degrees

bldg_width_ft = 40
bldg_length_ft = 60
purlin_spacing_ft = 5
n_purlin_lines = int(bldg_width_ft / purlin_spacing_ft) + 1  # 9 lines
n_frames = 4
bays = 3  # n_frames - 1
bay_length_ft = bldg_length_ft / bays  # 20 ft

# Standard purlin: span = bay length = 20 ft = 240 inches
std_span_in = bay_length_ft * 12

# Angled at 45 deg from aisle: angleFromPerp = 45 degrees
angled_cut_in = std_span_in / math.cos(math.radians(45))

test("Building: 9 purlin lines", n_purlin_lines == 9)
test("Building: 3 bays of 20ft", bay_length_ft == 20.0)
test("Building: std span = 240 inches", std_span_in == 240)
test("Building: angled cut length ~339.4 inches", abs(angled_cut_in - 339.411) < 0.1)
test("Building: angled is 1.414x longer", abs(angled_cut_in / std_span_in - math.sqrt(2)) < 0.001)

# BOM: P6 plates = 2 per purlin line * 9 lines = 18 plates
p6_count = 2 * n_purlin_lines
p6_total_wt = p6_count * p6_weight
test("Building: 18 P6 plates", p6_count == 18)
test("Building: P6 total ~93 lbs", abs(p6_total_wt - 93.03) < 1.0)

# Standard mode: P2 plates = 2 per purlin line * 9 lines = 18 plates
p2_count = 2 * n_purlin_lines
p2_total_wt = p2_count * p2_weight
test("Building: P2 total ~148.9 lbs (for comparison)", abs(p2_total_wt - 148.86) < 1.0)
test("Building: P6 lighter total than P2", p6_total_wt < p2_total_wt)


# ===================================================================
# SUMMARY
# ===================================================================
print(f"\n{'='*60}")
print(f"  RESULTS: {passed} passed, {failed} failed, {passed+failed} total")
print(f"{'='*60}")

if failed > 0:
    print("\n  SOME TESTS FAILED!")
    sys.exit(1)
else:
    print("\n  ALL TESTS PASSED!")
    sys.exit(0)
