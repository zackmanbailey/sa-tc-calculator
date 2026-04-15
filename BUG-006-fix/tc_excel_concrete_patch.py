"""
BUG-006 FIX — Patch for outputs/tc_excel_gen.py
=================================================

INSTRUCTIONS:
In outputs/tc_excel_gen.py, after the equipment detail section (around line 235),
add the concrete per-building detail rendering.

ADD THIS CODE after the equipment detail block and before the final save:
"""

# --- ADD this block in generate_construction_quote_excel() after equipment detail ---

"""
    # ── Concrete Per-Building Detail (BUG-006) ─────────────────────────
    concrete_data = costs.get("concrete", {})
    concrete_bldgs = concrete_data.get("buildings", [])
    if len(concrete_bldgs) > 1:
        row += 1  # blank spacer row

        # Section header
        ws.row_dimensions[row].height = 18
        conc_headers = ["BUILDING", "# PIERS", "DIA (IN)", "DEPTH (FT)", "CU. YARDS", "COST"]
        for ci, hdr in enumerate(conc_headers):
            c = ws.cell(row, ci + 1, hdr)
            c.font = font(bold=True, size=8, color=TC_WHITE)
            c.fill = fill(TC_BLUE)
            c.alignment = center()
            c.border = border_thin()
        row += 1

        total_cy = 0
        total_cost_conc = 0
        alt = True
        for b in concrete_bldgs:
            cy = float(b.get("cubic_yards", 0))
            cost_val = float(b.get("cost", 0))
            total_cy += cy
            total_cost_conc += cost_val
            row_fill = fill("FFFFFFFF") if alt else fill(TC_LIGHT)

            ws.cell(row, 1, b.get("building_name", "")).font = font(size=8)
            ws.cell(row, 1).fill = row_fill
            ws.cell(row, 1).border = border_thin()

            ws.cell(row, 2, int(b.get("n_piers", 0))).font = font(size=8)
            ws.cell(row, 2).fill = row_fill
            ws.cell(row, 2).alignment = center()
            ws.cell(row, 2).border = border_thin()

            ws.cell(row, 3, int(b.get("dia_in", 24))).font = font(size=8)
            ws.cell(row, 3).fill = row_fill
            ws.cell(row, 3).alignment = center()
            ws.cell(row, 3).border = border_thin()

            ws.cell(row, 4, float(b.get("depth_ft", 10))).font = font(size=8)
            ws.cell(row, 4).fill = row_fill
            ws.cell(row, 4).alignment = center()
            ws.cell(row, 4).border = border_thin()

            ws.cell(row, 5, cy).font = font(size=8)
            ws.cell(row, 5).fill = row_fill
            ws.cell(row, 5).number_format = '0.00'
            ws.cell(row, 5).alignment = center()
            ws.cell(row, 5).border = border_thin()

            ws.cell(row, 6, cost_val).font = font(size=8)
            ws.cell(row, 6).fill = row_fill
            ws.cell(row, 6).number_format = FMT_DOLLAR
            ws.cell(row, 6).alignment = right()
            ws.cell(row, 6).border = border_thin()

            alt = not alt
            row += 1

        # Total row
        ws.cell(row, 1, "TOTAL").font = font(bold=True, size=8)
        ws.cell(row, 1).fill = fill(TC_LIGHT)
        ws.cell(row, 1).border = border_thin()
        for ci in range(2, 5):
            ws.cell(row, ci).fill = fill(TC_LIGHT)
            ws.cell(row, ci).border = border_thin()
        ws.cell(row, 5, total_cy).font = font(bold=True, size=8)
        ws.cell(row, 5).fill = fill(TC_LIGHT)
        ws.cell(row, 5).number_format = '0.00'
        ws.cell(row, 5).alignment = center()
        ws.cell(row, 5).border = border_thin()
        ws.cell(row, 6, total_cost_conc).font = font(bold=True, size=8)
        ws.cell(row, 6).fill = fill(TC_LIGHT)
        ws.cell(row, 6).number_format = FMT_DOLLAR
        ws.cell(row, 6).alignment = right()
        ws.cell(row, 6).border = border_thin()
        row += 1
"""
