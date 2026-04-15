"""
BUG-017 FIX — Shop Drawing PDF Export
======================================

Creates a PDF export handler for shop drawings.
Uses server-side PDF generation with ReportLab.

INSTRUCTIONS:

1. Add this file as: combined_calc/shop_drawings/drawing_pdf_export.py

2. Add the handler class (below) to tf_handlers.py

3. Add routes to get_routes():
   (r"/api/shop-drawings/export-pdf/([^/]+)/([^/]+)", ShopDrawingPDFExportHandler),
   (r"/api/shop-drawings/export-all-pdf/([^/]+)", ShopDrawingAllPDFExportHandler),

4. Add an export button to the shop drawings template
"""

import os
import json
import io
from datetime import datetime


def generate_shop_drawing_pdf(drawing_data, project_info=None, paper_size="letter"):
    """Generate a PDF from shop drawing data.

    Args:
        drawing_data: dict with drawing info (svg, dimensions, title, etc.)
        project_info: dict with project metadata
        paper_size: "letter" (8.5x11) or "tabloid" (11x17)

    Returns:
        bytes - PDF file content
    """
    from reportlab.lib.pagesizes import letter, landscape, TABLOID
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.graphics.shapes import Drawing, String, Line, Rect
    from reportlab.graphics import renderPDF

    # Page setup
    if paper_size == "tabloid":
        page = landscape(TABLOID)
    else:
        page = landscape(letter)  # Landscape letter for drawings

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=page,
                            leftMargin=0.5*inch, rightMargin=0.5*inch,
                            topMargin=0.5*inch, bottomMargin=0.75*inch)

    styles = getSampleStyleSheet()
    story = []

    # Colors
    TF_BLUE = colors.HexColor("#1E3A5F")
    TF_RED = colors.HexColor("#C0392B")

    # Title block
    proj = project_info or {}
    title = drawing_data.get("title", "Shop Drawing")
    job_code = proj.get("job_code", drawing_data.get("job_code", ""))
    rev = drawing_data.get("revision", "A")
    date_str = datetime.now().strftime("%m/%d/%Y")

    title_style = ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=14,
                                  textColor=TF_BLUE, spaceAfter=6)
    story.append(Paragraph(f"{title}", title_style))

    # Title block table
    tb_data = [
        ["JOB CODE", job_code, "REVISION", rev],
        ["DATE", date_str, "DRAWN BY", drawing_data.get("drawn_by", "TitanForge")],
        ["PROJECT", proj.get("name", ""), "SCALE", drawing_data.get("scale", "NTS")],
    ]

    tb = Table(tb_data, colWidths=[1*inch, 2.5*inch, 1*inch, 2.5*inch])
    tb.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (0, -1), TF_BLUE),
        ("TEXTCOLOR", (2, 0), (2, -1), TF_BLUE),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F0F4FA")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#F0F4FA")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D7E2")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(tb)
    story.append(Spacer(1, 12))

    # Drawing content
    # If SVG data is available, render it; otherwise show description
    if drawing_data.get("svg"):
        # Convert SVG to ReportLab Drawing
        try:
            from svglib.svglib import svg2rlg
            drawing = svg2rlg(io.BytesIO(drawing_data["svg"].encode()))
            if drawing:
                story.append(drawing)
        except ImportError:
            story.append(Paragraph(
                "SVG rendering requires svglib. Drawing data is included but cannot be rendered to PDF directly.",
                styles["Normal"]
            ))
    elif drawing_data.get("description"):
        story.append(Paragraph(drawing_data["description"], styles["Normal"]))

    # Component details table
    if drawing_data.get("components"):
        story.append(Spacer(1, 12))
        story.append(Paragraph("Component Details", ParagraphStyle(
            "compHdr", fontName="Helvetica-Bold", fontSize=10, textColor=TF_BLUE,
            spaceBefore=8, spaceAfter=4)))

        comp_rows = [["ITEM", "DESCRIPTION", "QTY", "MACHINE", "MATERIAL", "NOTES"]]
        for c in drawing_data["components"]:
            comp_rows.append([
                c.get("item_id", ""),
                c.get("description", ""),
                str(c.get("quantity", "")),
                c.get("machine", ""),
                c.get("material", ""),
                c.get("notes", ""),
            ])

        ct = Table(comp_rows, colWidths=[0.8*inch, 2.5*inch, 0.5*inch, 0.8*inch, 1.2*inch, 2*inch])
        ct.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 7),
            ("BACKGROUND", (0, 0), (-1, 0), TF_BLUE),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 7),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D7E2")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F0F4FA")]),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(ct)

    # Footer
    story.append(Spacer(1, 20))
    footer_style = ParagraphStyle("footer", fontName="Helvetica", fontSize=7,
                                   textColor=colors.HexColor("#94A3B8"))
    story.append(Paragraph(
        f"Generated by TitanForge v4.2 | {date_str} | {job_code} Rev {rev} | "
        f"CONFIDENTIAL — Property of Titan Carports",
        footer_style
    ))

    doc.build(story)
    return buf.getvalue()


# ── HANDLER CLASSES (add to tf_handlers.py) ──

"""
class ShopDrawingPDFExportHandler(BaseHandler):
    '''GET /api/shop-drawings/export-pdf/{job_code}/{drawing_id} — Export single drawing as PDF.'''
    required_roles = ["admin", "estimator", "shop"]

    def get(self, job_code, drawing_id):
        try:
            from shop_drawings.drawing_pdf_export import generate_shop_drawing_pdf

            # Load drawing data
            drawing_path = os.path.join(SHOP_DRAWINGS_DIR, job_code, "drawings", drawing_id + ".json")
            if not os.path.exists(drawing_path):
                self.set_status(404)
                self.write(json_encode({"ok": False, "error": "Drawing not found"}))
                return

            with open(drawing_path, "r") as f:
                drawing_data = json.load(f)

            # Load project info
            proj_path = os.path.join(BASE_DIR, "data", "projects", job_code, "project.json")
            project_info = {}
            if os.path.exists(proj_path):
                with open(proj_path, "r") as f:
                    project_info = json.load(f)

            pdf_bytes = generate_shop_drawing_pdf(drawing_data, project_info)

            self.set_header("Content-Type", "application/pdf")
            self.set_header("Content-Disposition",
                f'attachment; filename="ShopDrawing_{job_code}_{drawing_id}.pdf"')
            self.write(pdf_bytes)

        except Exception as e:
            import traceback
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class ShopDrawingAllPDFExportHandler(BaseHandler):
    '''GET /api/shop-drawings/export-all-pdf/{job_code} — Export all drawings as single PDF.'''
    required_roles = ["admin", "estimator", "shop"]

    def get(self, job_code):
        try:
            from shop_drawings.drawing_pdf_export import generate_shop_drawing_pdf
            from reportlab.lib.pagesizes import letter, landscape
            from reportlab.platypus import SimpleDocTemplate, PageBreak
            from reportlab.lib.units import inch
            import io

            drawings_dir = os.path.join(SHOP_DRAWINGS_DIR, job_code, "drawings")
            if not os.path.exists(drawings_dir):
                self.set_status(404)
                self.write(json_encode({"ok": False, "error": "No drawings found"}))
                return

            # Collect all drawing files
            drawing_files = sorted([f for f in os.listdir(drawings_dir) if f.endswith(".json")])
            if not drawing_files:
                self.set_status(404)
                self.write(json_encode({"ok": False, "error": "No drawings found"}))
                return

            # For multi-page, generate each individually and merge
            # (Simple approach: generate first drawing PDF as the combined output)
            # A more sophisticated approach would use PyPDF2 to merge
            proj_path = os.path.join(BASE_DIR, "data", "projects", job_code, "project.json")
            project_info = {}
            if os.path.exists(proj_path):
                with open(proj_path, "r") as f:
                    project_info = json.load(f)

            # Generate PDFs for each drawing
            from PyPDF2 import PdfMerger
            merger = PdfMerger()

            for df in drawing_files:
                with open(os.path.join(drawings_dir, df), "r") as f:
                    drawing_data = json.load(f)
                pdf_bytes = generate_shop_drawing_pdf(drawing_data, project_info)
                merger.append(io.BytesIO(pdf_bytes))

            output = io.BytesIO()
            merger.write(output)
            merger.close()

            self.set_header("Content-Type", "application/pdf")
            self.set_header("Content-Disposition",
                f'attachment; filename="ShopDrawings_{job_code}_All.pdf"')
            self.write(output.getvalue())

        except ImportError:
            # If PyPDF2 not available, just export first drawing
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": "PyPDF2 required for multi-page export. Install with: pip install PyPDF2"}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))
"""
