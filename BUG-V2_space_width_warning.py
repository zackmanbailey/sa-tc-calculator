"""
BUG-V2 FIX: Space Width Default Causes Confusing Warning
==========================================================
File: combined_calc/calc/bom.py
Severity: LOW (cosmetic/UX)
Discovered: Post-patch verification, April 15, 2026

PROBLEM:
  When space_width_ft is left at the default value of 12, the BOM calculator
  may emit a warning like "Length 180.0' is not an exact multiple of 12.0'
  space width (0.0' remainder)" when the length IS actually a multiple.
  This is confusing to users even though calculations proceed correctly.

  The warning triggers because of floating-point remainder comparisons.

ROOT CAUSE:
  In bom.py calc_space_based_columns(), line ~200:
    remainder = length_ft % space_width_ft

  Floating-point modulo can return tiny non-zero values (e.g., 1e-10)
  which triggers the warning even when the division is mathematically exact.

FIX:
  Add a tolerance check for the remainder. In combined_calc/calc/bom.py,
  find the calc_space_based_columns() function (around line 172).

  Change the remainder check from:
    remainder = length_ft % space_width_ft
    if remainder > 0:

  To:
    remainder = length_ft % space_width_ft
    # Treat near-zero remainders as exact (floating point tolerance)
    if remainder > 0.01 and (space_width_ft - remainder) > 0.01:

  This ensures that values like 180.0 % 12.0 = 0.0000000001 (float error)
  won't trigger the warning, while genuinely non-exact values like
  185.0 % 12.0 = 5.0 still will.

VERIFICATION:
  After applying:
  1. Calculate BOM for a building with length=180, space_width=12
  2. Should produce NO warning about non-exact multiple
  3. Calculate BOM for length=185, space_width=12
  4. Should still warn about 5' remainder
"""
