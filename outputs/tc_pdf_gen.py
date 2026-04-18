"""
Titan Carports — Construction Quote PDF Generator  (v2.4)
Includes: salesperson block, Brad Spence default, TC branding.
"""

import io, datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

# Titan Carports brand colors
TC_DARK   = colors.HexColor("#1C1C2E")
TC_RED    = colors.HexColor("#C00000")
TC_BLUE   = colors.HexColor("#1F4E79")
TC_BLUE_M = colors.HexColor("#2E75B6")
TC_BLUE_L = colors.HexColor("#DEEAF1")
TC_GOLD   = colors.HexColor("#FFC000")
TC_WHITE  = colors.white
TC_LIGHT  = colors.HexColor("#F5F7FA")
TC_GREEN  = colors.HexColor("#375623")


def fmt_dollar(v):
    return f"${float(v or 0):,.2f}"


def generate_construction_quote_pdf(data: dict) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=letter,
        leftMargin=0.6 * inch, rightMargin=0.6 * inch,
        topMargin=0.6 * inch, bottomMargin=0.6 * inch
    )

    styles = getSampleStyleSheet()
    story = []

    proj = data.get("project", {})
    sa   = data.get("sa", {})
    summary = data.get("summary", {})
    sp   = data.get("salesperson", {})
    sp_name  = sp.get("name", "Brad Spence") or "Brad Spence"
    sp_title = sp.get("title", "Sales Manager") or "Sales Manager"
    sp_phone = sp.get("phone", "(303) 909-5698") or "(303) 909-5698"
    sp_email = sp.get("email", "brad@titancarports.com") or "brad@titancarports.com"

    # ── Header ────────────────────────────────────────────────────────────
    hdr_data = [[
        Paragraph(
            '<font color="#C00000"><b>TITAN CARPORTS</b></font><br/>'
            '<font size="8" color="#888888">Quality Steel Structures</font><br/>'
            '<font size="7" color="#999999">710 Honea Egypt Rd, Conroe, TX 77385</font><br/>'
            '<font size="7" color="#999999">(303) 909-5698 | info@titancarports.com | www.titancarports.com</font>',
            ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=18, leading=14)
        ),
        Paragraph(
            f'<b>CONSTRUCTION QUOTE</b><br/>'
            f'<font size="9">Job: {proj.get("job_code", "")}</font><br/>'
            f'<font size="8" color="#888888">Date: {proj.get("quote_date", datetime.date.today().strftime("%m/%d/%Y"))}</font>',
            ParagraphStyle("hr", fontName="Helvetica-Bold", fontSize=13,
                           alignment=TA_RIGHT, textColor=TC_BLUE)
        )
    ]]
    hdr_tbl = Table(hdr_data, colWidths=[4 * inch, 3 * inch])
    hdr_tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(hdr_tbl)
    story.append(HRFlowable(width="100%", thickness=2, color=TC_RED, spaceAfter=8))

    # ── Project + Salesperson Info ─────────────────────────────────────────
    pdata = [
        ["PROJECT", proj.get("name", ""), "SALESPERSON", sp_name],
        ["CUSTOMER", proj.get("customer_name", ""), "TITLE", sp_title],
        ["ADDRESS", f"{proj.get('address', '')} {proj.get('city', '')} {proj.get('state', '')}".strip(),
         "PHONE", sp_phone],
        ["SA QUOTE #", sa.get("quote_num", ""), "EMAIL", sp_email],
    ]
    ptbl = Table(pdata, colWidths=[1.1 * inch, 2.3 * inch, 1.1 * inch, 2.3 * inch])
    ptbl.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BACKGROUND", (0, 0), (0, -1), TC_BLUE_L),
        ("BACKGROUND", (2, 0), (2, -1), TC_BLUE_L),
        ("TEXTCOLOR", (0, 0), (0, -1), TC_BLUE),
        ("TEXTCOLOR", (2, 0), (2, -1), TC_BLUE),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D7E2")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(ptbl)
    story.append(Spacer(1, 10))

    # ── Cost Breakdown ─────────────────────────────────────────────────────
    costs = data.get("costs", {})
    sections_config = [
        ("Materials (SA Fabrication)",  sa.get("materials_cost", 0)),
        ("Concrete — Pier Footings",    costs.get("concrete", {}).get("total", 0)),
        ("Labor — Installation",        costs.get("labor", {}).get("total", 0)),
        ("Equipment Rental",            costs.get("equipment", {}).get("total", 0)),
        ("Drilling",                    costs.get("drilling", {}).get("total", 0)),
        ("Shipping & Freight",          costs.get("shipping", {}).get("total", 0)),
        ("Fuel & Gas",                  costs.get("fuel", {}).get("total", 0)),
        ("Hotels",                      costs.get("hotels", {}).get("total", 0)),
        ("Per Diem",                    costs.get("per_diem", {}).get("total", 0)),
        ("Transportation of Crew",      costs.get("transport", {}).get("total", 0)),
        ("Miscellaneous",               costs.get("misc", {}).get("total", 0)),
    ]

    rows = [["COST CATEGORY", "AMOUNT"]]
    subtotal = 0
    for label, amt in sections_config:
        amt = float(amt or 0)
        if amt == 0:
            continue
        rows.append([label, fmt_dollar(amt)])
        subtotal += amt

    markup_pct = float(proj.get("markup_pct", 35))
    markup_amt = subtotal * markup_pct / 100
    total = subtotal + markup_amt

    rows.append(["SUBTOTAL", fmt_dollar(subtotal)])
    rows.append([f"MARKUP ({markup_pct:.0f}%)", fmt_dollar(markup_amt)])
    rows.append(["TOTAL SELL PRICE", fmt_dollar(total)])

    col_widths = [5 * inch, 1.8 * inch]
    ctbl = Table(rows, colWidths=col_widths)
    ts = TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("BACKGROUND", (0, 0), (-1, 0), TC_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), TC_WHITE),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -4), 0.5, colors.HexColor("#D0D7E2")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -4), [TC_WHITE, TC_LIGHT]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        # Subtotal row
        ("BACKGROUND", (0, -3), (-1, -3), TC_LIGHT),
        ("FONTNAME", (0, -3), (-1, -3), "Helvetica-Bold"),
        ("LINEABOVE", (0, -3), (-1, -3), 1.5, TC_BLUE),
        # Markup row
        ("BACKGROUND", (0, -2), (-1, -2), colors.HexColor("#FFF8E1")),
        # Total row
        ("BACKGROUND", (0, -1), (-1, -1), TC_RED),
        ("TEXTCOLOR", (0, -1), (-1, -1), TC_WHITE),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, -1), (-1, -1), 12),
        ("LINEABOVE", (0, -1), (-1, -1), 1.5, TC_RED),
    ])
    ctbl.setStyle(ts)
    story.append(ctbl)
    story.append(Spacer(1, 12))

    # ── Equipment detail ───────────────────────────────────────────────────
    equip_items = costs.get("equipment", {}).get("items", [])
    if equip_items:
        story.append(Paragraph("Equipment Detail", ParagraphStyle(
            "sh", fontName="Helvetica-Bold", fontSize=10, textColor=TC_BLUE,
            spaceBefore=4, spaceAfter=4)))
        eq_rows = [["Description", "Qty", "Unit", "Rate", "Total"]]
        for it in equip_items:
            eq_rows.append([
                it.get("desc", ""), str(it.get("qty", 1)),
                it.get("unit", "day"), fmt_dollar(it.get("rate", 0)),
                fmt_dollar(float(it.get("qty", 0)) * float(it.get("rate", 0)))
            ])
        eqtbl = Table(eq_rows, colWidths=[2.8 * inch, .6 * inch, .6 * inch, 1 * inch, .8 * inch])
        eqtbl.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BACKGROUND", (0, 0), (-1, 0), TC_BLUE_L),
            ("TEXTCOLOR", (0, 0), (-1, 0), TC_BLUE),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#D0D7E2")),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(eqtbl)
        story.append(Spacer(1, 8))

    # ── Misc detail ────────────────────────────────────────────────────────
    misc_items = costs.get("misc", {}).get("items", [])
    if misc_items:
        story.append(Paragraph("Miscellaneous Detail", ParagraphStyle(
            "sh2", fontName="Helvetica-Bold", fontSize=10, textColor=TC_BLUE,
            spaceBefore=4, spaceAfter=4)))
        mc_rows = [["Description", "Amount"]]
        for it in misc_items:
            mc_rows.append([it.get("desc", ""), fmt_dollar(it.get("amount", 0))])
        mctbl = Table(mc_rows, colWidths=[5 * inch, 1.8 * inch])
        mctbl.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BACKGROUND", (0, 0), (-1, 0), TC_BLUE_L),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#D0D7E2")),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(mctbl)

    # ── Terms and Conditions + Signature Block ──────────────────────────────
    try:
        from outputs.titan_branding import add_terms_and_signature, add_pdf_footer
        add_terms_and_signature(story)
        add_pdf_footer(story, salesperson_name=sp_name, salesperson_phone=sp_phone,
                       salesperson_email=sp_email)
    except ImportError:
        # Fallback if branding module not available
        story.append(Spacer(1, 12))
        terms_style = ParagraphStyle("terms", fontName="Helvetica-Bold", fontSize=10,
                                     textColor=TC_BLUE, spaceBefore=4, spaceAfter=4)
        story.append(Paragraph("TERMS AND CONDITIONS", terms_style))
        terms_body = ParagraphStyle("tb", fontName="Helvetica", fontSize=7,
                                    textColor=colors.HexColor("#444444"), leading=10)
        story.append(Paragraph("1. This quote is valid for 30 days from the date above.", terms_body))
        story.append(Paragraph("2. A 50% deposit is required to begin fabrication. Balance due upon completion.", terms_body))
        story.append(Paragraph("3. Prices are based on current material costs and are subject to change.", terms_body))
        story.append(Spacer(1, 16))
        story.append(Paragraph("ACCEPTANCE", terms_style))
        story.append(Paragraph("Customer Signature: ________________________________  Date: ________________", terms_body))
        story.append(Spacer(1, 8))
        story.append(Paragraph("Printed Name: ________________________________  Title: ________________", terms_body))

        # Footer
        story.append(Spacer(1, 16))
        story.append(HRFlowable(width="100%", thickness=1, color=TC_RED, spaceAfter=6))
        story.append(Paragraph(
            f'\u00a9 {datetime.date.today().year} Titan Carports \u00b7 Conroe, TX \u00b7 www.titancarports.com  \u00b7  '
            f'{sp_name} \u00b7 {sp_phone} \u00b7 {sp_email}   |   '
            f'Thank you for your business!',
            ParagraphStyle("footer", fontName="Helvetica", fontSize=7,
                           textColor=colors.gray, alignment=TA_CENTER)
        ))

    doc.build(story)
    return buf.getvalue()
