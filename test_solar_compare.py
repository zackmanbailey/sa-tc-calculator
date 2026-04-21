"""
Test Phase 3: Solar Cost Comparison & Optimization

Tests:
1. Compare mode through the BOM engine (orientation="compare")
2. Verify the best option is selected (lowest purlin LF)
3. Verify all 4 results are stored in geometry
4. Verify standard mode (non-solar) still works
5. Verify single-orientation solar mode still works
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from calc.bom import BOMCalculator, ProjectInfo, BuildingConfig
from calc.solar_layout import (
    SolarPanelSpec, SolarLayoutConfig, calc_solar_comparison
)


def make_project():
    return ProjectInfo(
        name="Solar Compare Test",
        job_code="TEST-SC-01",
        wind_speed_mph=115,
        markup_pct=35,
    )


def make_solar_building(orientation="landscape"):
    """Create a building config with solar mode enabled."""
    bldg = BuildingConfig()
    bldg.width_ft = 40.0
    bldg.length_ft = 180.0
    bldg.clear_height_ft = 12.0
    bldg.solar_mode = True
    bldg.solar_orientation = orientation
    bldg.solar_panels_across = 5
    bldg.solar_panels_along = 20
    bldg.solar_panel_width_mm = 992.0
    bldg.solar_panel_length_mm = 2108.0
    bldg.solar_mount_hole_edge_mm = 20.0
    bldg.solar_mount_hole_inset_mm = 250.0
    bldg.solar_gap_width_in = 0.25
    bldg.solar_gap_length_in = 0.25
    bldg.solar_edge_clearance_in = 4.0
    bldg.solar_dim_mode = "panel_count"
    return bldg


def test_compare_mode_bom():
    """Test that orientation='compare' runs all 4 combos and picks the best."""
    print("=" * 60)
    print("TEST 1: Compare mode through BOM engine")
    print("=" * 60)

    project = make_project()
    bldg = make_solar_building(orientation="compare")
    calc = BOMCalculator(project)
    proj_bom = calc.calculate_project([bldg])

    bldg_result = proj_bom.buildings[0]
    geo = bldg_result.geometry

    # Check that solar_comparison is present
    assert "solar_comparison" in geo, "solar_comparison missing from geometry"
    assert "solar_best_option" in geo, "solar_best_option missing from geometry"

    comparison = geo["solar_comparison"]
    results = comparison["results"]

    # All 4 combos should be present
    assert len(results) == 4, f"Expected 4 comparison results, got {len(results)}"

    labels = {r["label"] for r in results}
    expected_labels = {
        "Landscape + C-purlin",
        "Landscape + Z-purlin",
        "Portrait + C-purlin",
        "Portrait + Z-purlin",
    }
    assert labels == expected_labels, f"Labels mismatch: {labels} != {expected_labels}"

    # Results should be sorted by purlin_total_lf ascending
    lf_values = [r["purlin_total_lf"] for r in results]
    assert lf_values == sorted(lf_values), f"Results not sorted by purlin LF: {lf_values}"

    # Best option should match first result
    best_label = geo["solar_best_option"]
    assert best_label == results[0]["label"], (
        f"Best option '{best_label}' != first result '{results[0]['label']}'"
    )

    # solar_layout should also be present (the chosen layout)
    assert "solar_layout" in geo, "solar_layout missing - best option not applied"
    sl = geo["solar_layout"]
    best_layout = results[0]["layout"]
    assert abs(sl["purlin_spacing_ft"] - best_layout["purlin_spacing_ft"]) < 0.001, (
        "solar_layout purlin spacing doesn't match best option"
    )

    print(f"  Best option: {best_label}")
    print(f"  Purlin LF values: {lf_values}")
    print(f"  Building dims: {sl['building_width_ft']}' x {sl['building_length_ft']}'")
    for r in results:
        marker = " <<< BEST" if r["label"] == best_label else ""
        print(f"    {r['label']:25s}  purlin_lf={r['purlin_total_lf']:>10.2f}  "
              f"lines={r['layout']['n_purlin_lines']}  "
              f"spacing={r['layout']['purlin_spacing_ft']:.4f}'{marker}")
    print("  PASSED\n")


def test_standard_mode():
    """Test that non-solar standard mode still works (no solar fields)."""
    print("=" * 60)
    print("TEST 2: Standard mode (non-solar) still works")
    print("=" * 60)

    project = make_project()
    bldg = BuildingConfig()
    bldg.width_ft = 40.0
    bldg.length_ft = 180.0
    bldg.clear_height_ft = 12.0
    # solar_mode defaults to False

    calc = BOMCalculator(project)
    proj_bom = calc.calculate_project([bldg])
    bldg_result = proj_bom.buildings[0]
    geo = bldg_result.geometry

    assert "solar_comparison" not in geo, "solar_comparison should not be in standard mode"
    assert "solar_best_option" not in geo, "solar_best_option should not be in standard mode"
    assert "solar_layout" not in geo, "solar_layout should not be in standard mode"
    assert geo["purlin_auto"] is True, "purlin_auto should be True in standard mode"
    assert geo["n_purlin_lines"] > 0, "Should have purlin lines"

    print(f"  Purlin spacing: {geo['purlin_spacing_ft']}' (auto)")
    print(f"  Purlin lines: {geo['n_purlin_lines']}")
    print("  PASSED\n")


def test_single_orientation_solar():
    """Test that solar mode with explicit orientation (not 'compare') still works."""
    print("=" * 60)
    print("TEST 3: Single-orientation solar mode (landscape)")
    print("=" * 60)

    project = make_project()
    bldg = make_solar_building(orientation="landscape")

    calc = BOMCalculator(project)
    proj_bom = calc.calculate_project([bldg])
    bldg_result = proj_bom.buildings[0]
    geo = bldg_result.geometry

    assert "solar_layout" in geo, "solar_layout should be present"
    assert "solar_comparison" not in geo, "solar_comparison should NOT be present for single orientation"
    assert "solar_best_option" not in geo, "solar_best_option should NOT be present for single orientation"

    sl = geo["solar_layout"]
    assert sl["orientation"] == "landscape", f"Expected landscape, got {sl['orientation']}"
    assert sl["n_purlin_lines"] > 0, "Should have purlin lines"

    print(f"  Orientation: {sl['orientation']}")
    print(f"  Purlin spacing: {sl['purlin_spacing_ft']}' ft")
    print(f"  Purlin lines: {sl['n_purlin_lines']}")
    print(f"  Building: {sl['building_width_ft']}' x {sl['building_length_ft']}'")
    print("  PASSED\n")


def test_portrait_solar():
    """Test portrait orientation solar mode."""
    print("=" * 60)
    print("TEST 4: Single-orientation solar mode (portrait)")
    print("=" * 60)

    project = make_project()
    bldg = make_solar_building(orientation="portrait")

    calc = BOMCalculator(project)
    proj_bom = calc.calculate_project([bldg])
    bldg_result = proj_bom.buildings[0]
    geo = bldg_result.geometry

    assert "solar_layout" in geo, "solar_layout should be present"
    assert "solar_comparison" not in geo, "solar_comparison should NOT be present"

    sl = geo["solar_layout"]
    assert sl["orientation"] == "portrait", f"Expected portrait, got {sl['orientation']}"

    print(f"  Orientation: {sl['orientation']}")
    print(f"  Purlin spacing: {sl['purlin_spacing_ft']}' ft")
    print(f"  Purlin lines: {sl['n_purlin_lines']}")
    print(f"  Building: {sl['building_width_ft']}' x {sl['building_length_ft']}'")
    print("  PASSED\n")


def test_standalone_comparison():
    """Test calc_solar_comparison directly (what /api/solar-compare uses)."""
    print("=" * 60)
    print("TEST 5: Standalone calc_solar_comparison()")
    print("=" * 60)

    cfg = SolarLayoutConfig(
        panel=SolarPanelSpec(),
        orientation="compare",
        panels_across=5,
        panels_along=20,
        mode="panel_count",
    )
    result = calc_solar_comparison(cfg)

    assert "results" in result, "Missing 'results' key"
    assert "best" in result, "Missing 'best' key"
    assert "config_used" in result, "Missing 'config_used' key"
    assert len(result["results"]) == 4, f"Expected 4 results, got {len(result['results'])}"

    # Each result should have required fields
    for r in result["results"]:
        assert "label" in r
        assert "orientation" in r
        assert "purlin_type" in r
        assert "layout" in r
        assert "purlin_total_lf" in r
        assert r["purlin_total_lf"] > 0, f"purlin_total_lf should be > 0 for {r['label']}"

    # Best should be the first (lowest purlin LF)
    assert result["best"] == result["results"][0]["label"]

    print(f"  Best: {result['best']}")
    for r in result["results"]:
        print(f"    {r['label']:25s}  LF={r['purlin_total_lf']:>10.2f}")
    print("  PASSED\n")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("SOLAR COST COMPARISON — PHASE 3 TESTS")
    print("=" * 60 + "\n")

    test_compare_mode_bom()
    test_standard_mode()
    test_single_orientation_solar()
    test_portrait_solar()
    test_standalone_comparison()

    print("=" * 60)
    print("ALL 5 TESTS PASSED")
    print("=" * 60)
