"""
Structures America — PDF Quote Generator
Produces a professional customer-facing quote PDF with branding.
"""

import io
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus.flowables import Flowable

from calc.defaults import COMPANY

# ─────────────────────────────────────────────
# BRAND COLORS (reportlab uses 0–1 scale)
# ─────────────────────────────────────────────
def _hex(h):
    h = h.lstrip("#")
    return colors.Color(int(h[0:2],16)/255, int(h[2:4],16)/255, int(h[4:6],16)/255)

SA_DARK    = _hex("1A1A2E")
SA_BLUE    = _hex("1F4E79")
SA_BLUE_M  = _hex("2E75B6")
SA_BLUE_L  = _hex("DEEAF1")
SA_RED     = _hex("C00000")
SA_GOLD    = _hex("FFC000")
SA_GRAY    = _hex("404040")
SA_GRAY_L  = _hex("F2F2F2")
SA_GREEN   = _hex("375623")
SA_WHITE   = colors.white
SA_BLACK   = colors.black


# ─────────────────────────────────────────────
# PAGE TEMPLATE WITH HEADER/FOOTER
# ─────────────────────────────────────────────

class NumberedCanvas(rl_canvas.Canvas):
    def __init__(self, *args, **kwargs):
        self._doc = kwargs.pop("doc", None)
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_page(num_pages)
            super().showPage()
        super().save()

    def _draw_page(self, num_pages):
        self.saveState()
        w, h = letter
        # Footer
        self.setFont("Helvetica", 7)
        self.setFillColor(SA_GRAY)
        self.drawString(0.75*inch, 0.4*inch,
                        f"{COMPANY['name']}  ·  {COMPANY['address']}, {COMPANY['city_state_zip']}  "
                        f"·  {COMPANY['contact_phone']}  ·  {COMPANY['contact_email']}")
        self.drawRightString(w - 0.75*inch, 0.4*inch,
                             f"Page {self._pageNumber} of {num_pages}")
        # Thin accent line at top
        self.setStrokeColor(SA_RED)
        self.setLineWidth(3)
        self.line(0.75*inch, h - 0.5*inch, w - 0.75*inch, h - 0.5*inch)
        self.restoreState()


# ─────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────

def _get_styles():
    # Return a plain dict of ParagraphStyles (avoids StyleSheet name collision)
    return {
        "title": ParagraphStyle("sa_title", fontName="Helvetica-Bold", fontSize=20,
                                textColor=SA_WHITE, alignment=TA_LEFT,
                                spaceAfter=2, leading=24),
        "subtitle": ParagraphStyle("sa_subtitle", fontName="Helvetica", fontSize=9,
                                   textColor=colors.HexColor(0xAAAAAA), alignment=TA_LEFT,
                                   leading=12),
        "section_hdr": ParagraphStyle("sa_section_hdr", fontName="Helvetica-Bold", fontSize=10,
                                      textColor=SA_WHITE, alignment=TA_LEFT,
                                      leading=14, leftIndent=6),
        "body": ParagraphStyle("sa_body", fontName="Helvetica", fontSize=9,
                               textColor=SA_GRAY, leading=13),
        "body_bold": ParagraphStyle("sa_body_bold", fontName="Helvetica-Bold", fontSize=9,
                                    textColor=SA_GRAY, leading=13),
        "small": ParagraphStyle("sa_small", fontName="Helvetica", fontSize=7.5,
                                textColor=colors.HexColor(0x777777), leading=10),
        "total": ParagraphStyle("sa_total", fontName="Helvetica-Bold", fontSize=11,
                                textColor=SA_WHITE, alignment=TA_RIGHT, leading=14),
        "note_italic": ParagraphStyle("sa_note_italic", fontName="Helvetica-Oblique", fontSize=8,
                                      textColor=colors.HexColor(0x888888), leading=11),
    }


# ─────────────────────────────────────────────
# MAIN GENERATOR
# ─────────────────────────────────────────────

def generate_quote_pdf(bom_data: dict) -> bytes:
    buf = io.BytesIO()

    doc = SimpleDocTemplate(
        buf, pagesize=letter,
        leftMargin=0.75*inch, rightMargin=0.75*inch,
        topMargin=0.7*inch, bottomMargin=0.65*inch,
        title=f"Quote {bom_data['project'].get('job_code','')}"
    )

    styles = _get_styles()
    story = []
    proj = bom_data["project"]

    # ── Cover Header Block ────────────────────
    story += _build_header(proj, styles)
    story.append(Spacer(1, 0.15*inch))

    # ── Project Info Table ────────────────────
    story += _build_project_info(proj, styles)
    story.append(Spacer(1, 0.15*inch))

    # ── Buildings Summary ─────────────────────
    story += _build_buildings_summary(bom_data, styles)

    # ── Per Building Detail ───────────────────
    for bldg in bom_data.get("buildings", []):
        story.append(PageBreak())
        story += _build_building_detail(bldg, proj, styles)

    # ── Signature Block ───────────────────────
    story.append(Spacer(1, 0.25*inch))
    story += _build_signature_block(styles)

    doc.build(story, canvasmaker=lambda *a, **k: NumberedCanvas(*a, doc=doc, **k))
    buf.seek(0)
    return buf.read()


def _build_header(proj, styles):
    elements = []

    # Dark header background
    header_data = [[
        Paragraph("STRUCTURES AMERICA", styles["title"]),
        Paragraph(
            f"<b>MATERIAL QUOTE</b><br/>{COMPANY['address']}<br/>{COMPANY['city_state_zip']}<br/>"
            f"{COMPANY['contact_name']} · {COMPANY['contact_phone']}<br/>{COMPANY['contact_email']}",
            styles["subtitle"]
        ),
    ]]
    tbl = Table(header_data, colWidths=[3.8*inch, 3.2*inch])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), SA_DARK),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING",(0,0), (-1,-1), 12),
        ("RIGHTPADDING",(0,0),(-1,-1), 12),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING",(0,0),(-1,-1), 10),
        ("ALIGN",      (1,0), (1,-1), "RIGHT"),
    ]))
    elements.append(tbl)
    return elements


def _build_project_info(proj, styles):
    elements = []

    # Section header
    hdr = Table([[Paragraph("PROJECT INFORMATION", styles["section_hdr"])]],
                colWidths=[7*inch])
    hdr.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), SA_BLUE_M),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [SA_BLUE_M]),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    elements.append(hdr)

    # Info pairs in two columns
    date_str = proj.get("quote_date", datetime.date.today().strftime("%m/%d/%Y"))
    info = [
        ("Project Name", proj.get("name",""),         "Quote #",     proj.get("job_code","")),
        ("Customer",     proj.get("customer_name",""), "Date",        date_str),
        ("Address",      f"{proj.get('address','')} {proj.get('city','')} {proj.get('state','')} {proj.get('zip_code','')}".strip(),
                         "Wind Speed",    f"{proj.get('wind_speed_mph',115)} MPH"),
        ("Footing",      f"24\" DIA × {proj.get('footing_depth_ft',10):.0f}' Deep",
                         "Buildings",     str(len(proj.get("buildings_summary", [])))),
    ]

    data = []
    for l1, v1, l2, v2 in info:
        data.append([
            Paragraph(f"<b>{l1}:</b>", styles["body"]),
            Paragraph(v1, styles["body"]),
            Paragraph(f"<b>{l2}:</b>", styles["body"]),
            Paragraph(v2, styles["body"]),
        ])
    tbl = Table(data, colWidths=[1.2*inch, 2.3*inch, 1.2*inch, 2.3*inch])
    tbl.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [SA_WHITE, SA_GRAY_L]),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    elements.append(tbl)
    return elements


def _build_buildings_summary(bom_data, styles):
    elements = []
    elements.append(Spacer(1, 0.1*inch))

    hdr = Table([[Paragraph("BUILDINGS SUMMARY", styles["section_hdr"])]],
                colWidths=[7*inch])
    hdr.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), SA_BLUE_M),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    elements.append(hdr)

    data = [["Building", "Type", "Dimensions", "Bays", "Weight (LBS)", "Material Cost", "Fab Labor", "Sell Price"]]
    for bldg in bom_data.get("buildings", []):
        geo = bldg.get("geometry", {})
        bname = bldg.get("building_name", bldg.get("name", "Building"))
        labor_sell = bldg.get("labor_sell_price", 0.0)
        total_sell = bldg.get("total_sell_price", 0.0) + labor_sell
        data.append([
            bname,
            bldg["type"].upper(),
            f"{bldg['width_ft']:.0f}' × {bldg['length_ft']:.0f}'",
            str(geo.get("n_bays", "")),
            f"{bldg.get('total_weight_lbs', 0):,.0f}",
            f"${bldg.get('total_material_cost', 0):,.2f}",
            f"${labor_sell:,.2f}" if labor_sell > 0 else "—",
            f"${total_sell:,.2f}",
        ])

    # Totals
    data.append([
        "TOTAL", "", "", "",
        f"{bom_data.get('total_weight_lbs', 0):,.0f}",
        f"${bom_data.get('total_material_cost', 0):,.2f}",
        f"${bom_data.get('total_labor_sell_price', 0):,.2f}",
        f"${bom_data.get('total_sell_price', 0):,.2f}",
    ])

    colw = [1.4*inch, 0.6*inch, 1.0*inch, 0.4*inch, 0.8*inch, 1.0*inch, 0.8*inch, 1.0*inch]
    tbl = Table(data, colWidths=colw, repeatRows=1)
    n = len(data)
    tbl.setStyle(TableStyle([
        # Header
        ("BACKGROUND", (0,0), (-1,0), SA_BLUE),
        ("TEXTCOLOR",  (0,0), (-1,0), SA_WHITE),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,0), 8.5),
        # Body
        ("FONTSIZE",   (0,1), (-1,-2), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-2), [SA_WHITE, SA_GRAY_L]),
        # Total row
        ("BACKGROUND", (0,-1), (-1,-1), SA_GREEN),
        ("TEXTCOLOR",  (0,-1), (-1,-1), SA_WHITE),
        ("FONTNAME",   (0,-1), (-1,-1), "Helvetica-Bold"),
        # Alignment
        ("ALIGN",      (0,0), (-1,-1), "LEFT"),
        ("ALIGN",      (3,0), (-1,-1), "RIGHT"),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("GRID",       (0,0), (-1,-1), 0.5, colors.HexColor(0xCCCCCC)),
    ]))
    elements.append(tbl)
    return elements


def _build_building_detail(bldg, proj, styles):
    elements = []
    geo = bldg.get("geometry", {})

    # Title
    bname = bldg.get("building_name", bldg.get("name", "Building"))
    hdr = Table([[Paragraph(f"BILL OF MATERIALS — {bname.upper()}", styles["section_hdr"])]],
                colWidths=[7*inch])
    hdr.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), SA_BLUE),
        ("TOPPADDING", (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
    ]))
    elements.append(hdr)

    # Geometry info
    purlin_lbl = f"{geo.get('purlin_spacing_ft',5):.1f}' OC × {geo.get('n_purlin_lines','')} lines"
    purlin_lbl += " (auto)" if geo.get("purlin_auto") else " (override)"
    geo_text = (
        f"Type: {bldg['type'].upper()}  ·  "
        f"W: {bldg['width_ft']:.0f}'  ×  L: {bldg['length_ft']:.0f}'  ·  "
        f"Clear Ht: {bldg['clear_height_ft']:.1f}'  ·  "
        f"Frames: {geo.get('n_frames','')}  ·  "
        f"Bays: {geo.get('n_bays','')} @ {geo.get('bay_size_ft',0):.2f}'  ·  Overhang: {geo.get('overhang_ft',0):.2f}'  ·  "
        f"Cols: {geo.get('n_struct_cols','')}  ·  Col Ht: {geo.get('col_ht_ft',0):.2f}'  ·  "
        f"Purlins: {purlin_lbl}  ·  "
        f"Rebar Col: {geo.get('rebar_col','—')} / Beam: {geo.get('rebar_beam','—')}"
    )
    elements.append(Paragraph(geo_text, styles["small"]))
    elements.append(Spacer(1, 0.08*inch))

    # BOM table
    data = [["Category", "Description", "Qty", "Unit", "Total Wt\n(LBS)", "Unit Cost", "Total Cost"]]
    current_cat = None
    for item in bldg.get("line_items", []):
        if item["category"] != current_cat:
            current_cat = item["category"]
            data.append([
                Paragraph(f"<b>{current_cat}</b>", styles["small"]),
                "", "", "", "", "", ""
            ])

        qty_str = f"{item['qty']:,.2f}" if isinstance(item['qty'], float) else str(item['qty'])
        wt_str = f"{item['total_weight_lbs']:,.1f}" if item.get('total_weight_lbs') else "—"
        uc_str = f"${item['unit_cost']:.4f}" if item.get('unit_cost') else "—"
        tc_str = f"${item['total_cost']:,.2f}" if item.get('total_cost') else "—"

        data.append([
            "",
            Paragraph(item["description"], styles["small"]),
            qty_str,
            item["unit"],
            wt_str,
            uc_str,
            tc_str,
        ])

    colw = [1.1*inch, 2.4*inch, 0.65*inch, 0.75*inch, 0.65*inch, 0.75*inch, 0.7*inch]
    tbl = Table(data, colWidths=colw, repeatRows=1)
    n = len(data)

    style_cmds = [
        # Header
        ("BACKGROUND", (0,0), (-1,0), SA_BLUE_M),
        ("TEXTCOLOR",  (0,0), (-1,0), SA_WHITE),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,0), 7.5),
        # Body
        ("FONTSIZE",   (0,1), (-1,-1), 7.5),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [SA_WHITE, SA_GRAY_L]),
        # Alignment
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("ALIGN",      (2,0), (-1,-1), "RIGHT"),
        ("GRID",       (0,0), (-1,-1), 0.3, colors.HexColor(0xDDDDDD)),
    ]

    # Highlight category rows
    for ri, row in enumerate(data):
        if ri > 0 and isinstance(row[0], Paragraph):
            style_cmds.append(("BACKGROUND", (0,ri), (-1,ri), SA_BLUE_L))
            style_cmds.append(("SPAN", (0,ri), (-1,ri)))
            style_cmds.append(("FONTNAME", (0,ri), (-1,ri), "Helvetica-Bold"))

    tbl.setStyle(TableStyle(style_cmds))
    elements.append(tbl)

    # Totals block
    elements.append(Spacer(1, 0.08*inch))
    SA_GREEN_L = colors.HexColor(0xE2EFDA)
    SA_BLUE_L2 = colors.HexColor(0xDEEAF1)

    labor_sell = bldg.get("labor_sell_price", 0.0)
    labor_days = bldg.get("labor_total_days", 0)
    labor_raw  = bldg.get("labor_raw_cost", 0.0)
    total_sell = bldg.get("total_sell_price", 0.0) + labor_sell

    tot_rows = [
        ["", "", "", "", f"{bldg.get('total_weight_lbs', 0):,.0f} LBS",
         "Material Cost:", f"${bldg.get('total_material_cost', 0):,.2f}"],
    ]
    if labor_sell > 0:
        tot_rows.append([
            "", "", "", "", "",
            f"Fabrication Labor ({labor_days} shop days):",
            f"${labor_raw:,.2f}",
        ])

    tot_rows.append([
        "", "", "", "", "",
        "SELL PRICE:",
        f"${total_sell:,.2f}",
    ])

    tot_tbl = Table(tot_rows, colWidths=colw)
    n_rows = len(tot_rows)
    style_cmds_tot = [
        ("FONTNAME",        (0,0), (-1,-1), "Helvetica-Bold"),
        ("FONTSIZE",        (0,0), (-1,-1), 9),
        ("ALIGN",           (4,0), (-1,-1), "RIGHT"),
        ("VALIGN",          (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",      (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",   (0,0), (-1,-1), 4),
        ("BACKGROUND",      (4,0), (-1,0), SA_GREEN_L),
    ]
    if labor_sell > 0:
        style_cmds_tot.append(("BACKGROUND", (4,1), (-1,1), SA_BLUE_L2))
        style_cmds_tot.append(("TEXTCOLOR",  (4,1), (-1,1), SA_BLUE))
    style_cmds_tot.append(("BACKGROUND", (4, n_rows-1), (-1, n_rows-1), SA_RED))
    style_cmds_tot.append(("TEXTCOLOR",  (4, n_rows-1), (-1, n_rows-1), SA_WHITE))

    tot_tbl.setStyle(TableStyle(style_cmds_tot))
    elements.append(tot_tbl)
    return elements


def _build_signature_block(styles):
    elements = []
    elements.append(HRFlowable(width="100%", thickness=1, color=SA_GRAY))
    elements.append(Spacer(1, 0.1*inch))

    sig_data = [
        [
            Paragraph("Customer Acceptance:", styles["body_bold"]),
            Paragraph("_" * 35, styles["body"]),
            Spacer(1, 0.1*inch),
            Paragraph("Date:", styles["body_bold"]),
            Paragraph("_" * 20, styles["body"]),
        ],
        [
            Paragraph("Print Name:", styles["body_bold"]),
            Paragraph("_" * 35, styles["body"]),
            Spacer(1, 0.1*inch),
            Paragraph("Title:", styles["body_bold"]),
            Paragraph("_" * 20, styles["body"]),
        ],
    ]
    tbl = Table(sig_data, colWidths=[1.3*inch, 2.5*inch, 0.2*inch, 0.7*inch, 2.3*inch])
    tbl.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "BOTTOM"),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    elements.append(tbl)
    elements.append(Spacer(1, 0.05*inch))
    elements.append(Paragraph(
        f"This quote is valid for 30 days from the date issued. Pricing is subject to material market conditions. "
        f"This document constitutes the complete scope of materials quoted. Installation, permits, freight, and "
        f"foundation work not included unless specifically noted above. "
        f"© {datetime.date.today().year} {COMPANY['name']} · {COMPANY['city_state_zip']}",
        styles["note_italic"]
    ))
    return elements
