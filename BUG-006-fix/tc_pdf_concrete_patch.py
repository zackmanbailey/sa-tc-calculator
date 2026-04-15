"""
BUG-006 FIX — Patch for outputs/tc_pdf_gen.py
===============================================

INSTRUCTIONS:
In outputs/tc_pdf_gen.py, find the Cost Breakdown section (around line 101-162).

REPLACE the single concrete line:
    ("Concrete — Pier Footings",    costs.get("concrete", {}).get("total", 0)),

WITH the code below that checks for per-building concrete data and renders
a detail sub-table when multiple buildings exist.

SPECIFICALLY:
1. After `story.append(Spacer(1, 10))` (line 99), add the concrete detail table function
2. In sections_config, keep the concrete line as-is (it still shows the total in the summary)
3. After the main cost table (after line 162), add the concrete detail rendering

ADD THIS FUNCTION before generate_construction_quote_pdf():
"""

# --- ADD this helper function BEFORE generate_construction_quote_pdf() ---

def _render_concrete_detail(story, concrete_data, styles):
    """Render per-building concrete breakdown table in PDF.

    Args:
        story: ReportLab story list to append to
        concrete_data: dict with 'buildings' list and 'total' value
        styles: ReportLab styles
    """
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import ParagraphStyle

    buildings = concrete_data.get("buildings", [])
    if len(buildings) <= 1:
        return  # Skip detail table for single building

    TC_BLUE = colors.HexColor("#1E3A5F")
    TC_LIGHT = colors.HexColor("#F0F4FA")
    TC_WHITE = colors.white

    story.append(Spacer(1, 8))
    story.append(Paragraph("Concrete — Per-Building Detail", ParagraphStyle(
        "concHdr", fontName="Helvetica-Bold", fontSize=10, textColor=TC_BLUE,
        spaceBefore=4, spaceAfter=4,
    )))

    rows = [["BUILDING", "# PIERS", "DIA (IN)", "DEPTH (FT)", "CU. YARDS", "COST"]]
    total_cy = 0
    total_cost = 0

    for b in buildings:
        cy = float(b.get("cubic_yards", 0))
        cost = float(b.get("cost", 0))
        total_cy += cy
        total_cost += cost
        rows.append([
            b.get("building_name", ""),
            str(int(b.get("n_piers", 0))),
            str(int(b.get("dia_in", 24))),
            str(float(b.get("depth_ft", 10))),
            f"{cy:.2f}",
            f"${cost:,.2f}",
        ])

    rows.append(["TOTAL", "", "", "", f"{total_cy:.2f}", f"${total_cost:,.2f}"])

    col_widths = [1.8*inch, 0.7*inch, 0.7*inch, 0.8*inch, 0.9*inch, 1.1*inch]
    tbl = Table(rows, colWidths=col_widths)
    tbl.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("BACKGROUND", (0, 0), (-1, 0), TC_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), TC_WHITE),
        ("FONTNAME", (0, 1), (-1, -2), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("ALIGN", (-1, 0), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -2), 0.5, colors.HexColor("#D0D7E2")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [TC_WHITE, TC_LIGHT]),
        # Total row
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, -1), (-1, -1), TC_LIGHT),
        ("LINEABOVE", (0, -1), (-1, -1), 1.5, TC_BLUE),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 6))


# --- THEN, in generate_construction_quote_pdf(), after the equipment detail section,
#     add this block (around line 185, after the equipment detail rendering): ---

"""
    # ── Concrete per-building detail (BUG-006) ─────────────────────────
    concrete_data = costs.get("concrete", {})
    if concrete_data.get("buildings") and len(concrete_data.get("buildings", [])) > 1:
        _render_concrete_detail(story, concrete_data, None)
"""
