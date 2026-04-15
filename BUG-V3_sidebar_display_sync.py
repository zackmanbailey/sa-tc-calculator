"""
BUG-V3 FIX: Building Sidebar Display Not Synced After JS Update
================================================================
File: combined_calc/templates/sa_calc.py
Severity: LOW (cosmetic)
Discovered: Post-patch verification, April 15, 2026

PROBLEM:
  When building configuration values (like space_width_ft) are updated
  programmatically via JavaScript (e.g., buildings[n].space_width_ft = 0),
  the sidebar building cards and form fields continue to display the old
  values. The underlying data is correct and BOM calculations use the
  right values, but the UI display is stale.

  This only affects programmatic updates — manual user input via the
  form fields works correctly because the onchange handlers call
  renderBuildingForms().

ROOT CAUSE:
  The updateBldg() function updates the data model but the sidebar
  re-render (renderBuildingForms()) is not automatically called when
  values are set directly on the buildings[] array.

FIX:
  This is a low-priority cosmetic issue. Two approaches:

  OPTION A (Simple — recommended):
  After any programmatic update to buildings[], call renderBuildingForms()
  to refresh the UI. This is already the pattern used by onchange handlers.

  In sa_calc.py, find any code that directly modifies buildings[]:
    buildings[n].space_width_ft = 0;
  And add:
    renderBuildingForms();
  After the modification.

  OPTION B (Reactive — future improvement):
  Use a Proxy or setter pattern on the buildings array so that any
  property change automatically triggers a UI refresh. This is a larger
  refactor and not recommended for a patch.

VERIFICATION:
  After applying Option A:
  1. Open the SA Calculator
  2. Set space_width_ft to 0 via the browser console:
     buildings[0].space_width_ft = 0; renderBuildingForms();
  3. The sidebar should now show the updated value
"""
