"""
TitanForge -- Titan Carports Branding Module
=============================================
Reusable branding constants and PDF helper functions for all document outputs.
Provides consistent header/footer, colors, and company info across:
  - TC Quote PDFs (reportlab)
  - Packing Lists, BOLs, Manifests (JSON templates)
  - Shop Drawing PDFs (jsPDF client-side)
"""

import datetime

# ─────────────────────────────────────────────
# BRANDING CONSTANTS
# ─────────────────────────────────────────────

TITAN_BRANDING = {
    "company": "Titan Carports",
    "address": "710 Honea Egypt Rd",
    "city": "Conroe",
    "state": "TX",
    "zip": "77385",
    "phone": "(303) 909-5698",
    "email": "info@titancarports.com",
    "website": "www.titancarports.com",
    "tagline": "Quality Steel Structures",
    "primary_color": "#1E40AF",
    "accent_color": "#D4A843",
    "red": "#C00000",
    "full_address": "710 Honea Egypt Rd, Conroe, TX 77385",
}


def get_branding():
    """Return a copy of the branding dict."""
    return dict(TITAN_BRANDING)


# ─────────────────────────────────────────────
# REPORTLAB PDF HELPERS
# ─────────────────────────────────────────────

def add_pdf_header(story, styles, job_code="", doc_title="Document", quote_date=None):
    """Add a branded Titan Carports header to a reportlab story list.

    Args:
        story: list to append flowables to
        styles: getSampleStyleSheet() result
        job_code: job/project code
        doc_title: e.g. "Construction Quote", "Packing List"
        quote_date: date string or None (defaults to today)
    """
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import Table, TableStyle, Paragraph, HRFlowable
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_RIGHT

    if quote_date is None:
        quote_date = datetime.date.today().strftime("%m/%d/%Y")

    TC_RED = colors.HexColor("#C00000")
    TC_BLUE = colors.HexColor("#1F4E79")

    hdr_data = [[
        Paragraph(
            '<font color="#C00000"><b>TITAN CARPORTS</b></font><br/>'
            '<font size="8" color="#888888">Quality Steel Structures</font><br/>'
            '<font size="7" color="#999999">710 Honea Egypt Rd, Conroe, TX 77385</font><br/>'
            '<font size="7" color="#999999">(303) 909-5698 | info@titancarports.com</font>',
            ParagraphStyle("titan_hdr", fontName="Helvetica-Bold", fontSize=18, leading=14)
        ),
        Paragraph(
            f'<b>{doc_title.upper()}</b><br/>'
            f'<font size="9">Job: {job_code}</font><br/>'
            f'<font size="8" color="#888888">Date: {quote_date}</font>',
            ParagraphStyle("titan_hdr_right", fontName="Helvetica-Bold", fontSize=13,
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


def add_pdf_footer(story, salesperson_name="", salesperson_phone="", salesperson_email="",
                   custom_message=None):
    """Add a branded footer to a reportlab story list.

    Args:
        story: list to append flowables to
        salesperson_name, phone, email: optional salesperson info
        custom_message: optional footer text override
    """
    from reportlab.lib import colors
    from reportlab.platypus import Spacer, HRFlowable, Paragraph
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER

    TC_RED = colors.HexColor("#C00000")

    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=1, color=TC_RED, spaceAfter=6))

    if custom_message:
        footer_text = custom_message
    else:
        parts = [f"\u00a9 {datetime.date.today().year} Titan Carports",
                 "Conroe, TX",
                 "www.titancarports.com"]
        if salesperson_name:
            parts.append(salesperson_name)
        if salesperson_phone:
            parts.append(salesperson_phone)
        if salesperson_email:
            parts.append(salesperson_email)
        footer_text = " \u00b7 ".join(parts)
        footer_text += "   |   Thank you for your business!"

    story.append(Paragraph(
        footer_text,
        ParagraphStyle("titan_footer", fontName="Helvetica", fontSize=7,
                       textColor=colors.gray, alignment=TA_CENTER)
    ))


def add_terms_and_signature(story):
    """Add terms & conditions and signature lines to a quote PDF."""
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import Spacer, Paragraph, Table, TableStyle
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_LEFT

    TC_BLUE = colors.HexColor("#1F4E79")
    TC_BLUE_L = colors.HexColor("#DEEAF1")

    story.append(Spacer(1, 12))

    # Terms and Conditions
    terms_style = ParagraphStyle("terms_hdr", fontName="Helvetica-Bold", fontSize=10,
                                 textColor=TC_BLUE, spaceBefore=4, spaceAfter=4)
    story.append(Paragraph("TERMS AND CONDITIONS", terms_style))

    terms_text = ParagraphStyle("terms_body", fontName="Helvetica", fontSize=7,
                                textColor=colors.HexColor("#444444"), leading=10,
                                alignment=TA_LEFT)

    terms = [
        "1. This quote is valid for 30 days from the date above.",
        "2. A 50% deposit is required to begin fabrication. Balance due upon completion.",
        "3. Prices are based on current material costs and are subject to change after quote expiration.",
        "4. Permit acquisition is the responsibility of the customer unless otherwise specified.",
        "5. Titan Carports warrants all structural steel against manufacturing defects for a period of one (1) year.",
        "6. Installation timeline is weather-dependent. Titan Carports is not liable for delays due to weather.",
        "7. Site must be level, accessible, and free of obstructions for installation crew.",
        "8. Customer is responsible for verifying property lines, setback requirements, and HOA restrictions.",
        "9. Any changes to the scope of work after acceptance may result in additional charges.",
        "10. Payment terms: Net 30 from invoice date. Late payments subject to 1.5% monthly finance charge.",
    ]
    for t in terms:
        story.append(Paragraph(t, terms_text))

    story.append(Spacer(1, 16))

    # Payment Terms Box
    story.append(Paragraph("PAYMENT TERMS", terms_style))
    pay_data = [
        ["Deposit (50%)", "Due upon acceptance"],
        ["Progress Payment", "Due at material delivery"],
        ["Final Payment", "Due upon completion of installation"],
    ]
    pay_tbl = Table(pay_data, colWidths=[2.5 * inch, 4.3 * inch])
    pay_tbl.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BACKGROUND", (0, 0), (0, -1), TC_BLUE_L),
        ("TEXTCOLOR", (0, 0), (0, -1), TC_BLUE),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#D0D7E2")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(pay_tbl)

    story.append(Spacer(1, 20))

    # Acceptance / Signature Block
    story.append(Paragraph("ACCEPTANCE", terms_style))
    sig_data = [
        ["By signing below, the customer acknowledges and accepts this quote and the terms above.", ""],
        ["", ""],
        ["Customer Signature: ________________________________", "Date: ________________"],
        ["", ""],
        ["Printed Name: ________________________________", "Title: ________________"],
        ["", ""],
        ["Titan Carports Representative: ________________________________", "Date: ________________"],
    ]
    sig_tbl = Table(sig_data, colWidths=[4.5 * inch, 2.3 * inch])
    sig_tbl.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(sig_tbl)
