"""
Structures America — Label Generator for Zebra ZT411 (203 DPI)
Generates fabrication stickers in ZPL, PDF (4×6), and CSV formats.
"""

import io
import csv
import datetime
from typing import List, Dict, Optional


# ─────────────────────────────────────────────
# STICKER GROUPING DEFAULTS
# ─────────────────────────────────────────────
DEFAULT_GROUPING = {
    "column":         1,   # 1 sticker per piece
    "rafter":         1,   # 1 sticker per piece
    "purlin":         1,   # 1 per bay-group (configurable)
    "sag_rod":        10,  # 1 sticker per 10 pieces
    "hurricane_strap":10,
    "brace":          10,
    "plate":          10,
    "gusset":         10,
}

ORIGIN = "Conroe, TX"


# ─────────────────────────────────────────────
# PART CODE FORMAT: [qty]-[PartName]-[TypeCode]
# JOB CODE: [cityabbrev][stateabbrev]-[year]
# ─────────────────────────────────────────────

def make_job_code(city: str, state: str, year: Optional[int] = None) -> str:
    """Generate job code: e.g. SANFL-24"""
    if not year:
        year = datetime.date.today().year % 100
    city_abbr = city.strip().replace(" ", "")[:3].upper()
    state_abbr = state.strip()[:2].upper()
    return f"{city_abbr}{state_abbr}-{year:02d}"


def make_part_code(qty: int, part_name: str, type_code: str) -> str:
    """Generate part code: e.g. 39-Columns-C2"""
    return f"{qty}-{part_name}-{type_code}"


# ─────────────────────────────────────────────
# ZPL LABEL TEMPLATE (Zebra ZT411, 203 DPI)
# Label size: 4" x 6" = 812 x 1218 dots at 203 DPI
# ─────────────────────────────────────────────

def _zpl_label(
    tag_num: int,
    part_code: str,
    job_code: str,
    canopy_num: str,
    description: str,
    length_in: float,
    quantity: int,
    weight_lbs: float,
    destination: str,
    manufacture_date: str,
    fabricator: str,
    heat_num: str,
    qr_url: str = "",
    label_width_dots: int = 812,
    label_height_dots: int = 1218,
) -> str:
    """Generate ZPL code for a single fabrication label."""

    # Truncate long strings
    def trunc(s, n): return str(s)[:n] if s else ""

    tag_str = f"TAG #{tag_num:04d}"
    weight_str = f"{weight_lbs:.1f} LBS" if weight_lbs else "— LBS"
    len_str = f"{length_in:.2f}\""

    zpl = []
    zpl.append("^XA")  # Start label

    # ── Label settings ───────────────────────
    zpl.append(f"^PW{label_width_dots}")    # Print width
    zpl.append(f"^LL{label_height_dots}")    # Label length
    zpl.append("^CI28")                       # UTF-8 encoding

    # ── Outer border ─────────────────────────
    zpl.append(f"^FO5,5^GB{label_width_dots-10},{label_height_dots-10},3^FS")

    # ── Header: dark background bar ──────────
    zpl.append(f"^FO5,5^GB{label_width_dots-10},70,70^FS")

    # Company name (white text)
    zpl.append("^FO15,15^A0N,28,28^FR^FD STRUCTURES AMERICA ^FS")

    # Tag number (right side of header)
    zpl.append(f"^FO{label_width_dots-220},18^A0N,22,22^FR^FD{tag_str}^FS")

    # ── Job Code & Canopy # ──────────────────
    zpl.append("^FO15,82^A0N,18,18^FDJob:^FS")
    zpl.append(f"^FO70,82^A0N,20,20^FD{trunc(job_code,12)}^FS")
    zpl.append(f"^FO{label_width_dots//2},82^A0N,18,18^FDCanopy #: {trunc(canopy_num,8)}^FS")

    # ── Part Code ────────────────────────────
    zpl.append("^FO15,108^A0N,16,16^FDPart Code:^FS")
    zpl.append(f"^FO120,105^A0N,20,20^FD{trunc(part_code,20)}^FS")

    # ── Description ──────────────────────────
    zpl.append("^FO15,135^A0N,16,16^FDDesc:^FS")
    zpl.append(f"^FO80,132^A0N,19,19^FD{trunc(description,28)}^FS")

    # ── Horizontal rule ──────────────────────
    zpl.append(f"^FO10,162^GB{label_width_dots-20},2,2^FS")

    # ── Dimensions & Quantity ─────────────────
    zpl.append("^FO15,170^A0N,16,16^FDLength:^FS")
    zpl.append(f"^FO90,167^A0N,22,22^FD{len_str}^FS")

    zpl.append(f"^FO{label_width_dots//2},170^A0N,16,16^FDQty:^FS")
    zpl.append(f"^FO{label_width_dots//2+50},167^A0N,22,22^FD{quantity}^FS")

    # ── Weight ───────────────────────────────
    zpl.append("^FO15,200^A0N,16,16^FDWeight:^FS")
    zpl.append(f"^FO90,197^A0N,22,22^FD{weight_str}^FS")

    # ── Horizontal rule ──────────────────────
    zpl.append(f"^FO10,228^GB{label_width_dots-20},2,2^FS")

    # ── Origin / Destination ─────────────────
    zpl.append("^FO15,236^A0N,15,15^FDOrigin:^FS")
    zpl.append(f"^FO80,234^A0N,17,17^FD{trunc(ORIGIN,22)}^FS")

    zpl.append(f"^FO{label_width_dots//2},236^A0N,15,15^FDDest:^FS")
    zpl.append(f"^FO{label_width_dots//2+50},234^A0N,17,17^FD{trunc(destination,16)}^FS")

    # ── Manufacture Date ─────────────────────
    zpl.append("^FO15,260^A0N,14,14^FDMfg Date:^FS")
    zpl.append(f"^FO100,258^A0N,16,16^FD{trunc(manufacture_date,14)}^FS")

    # ── Fabricator ───────────────────────────
    zpl.append(f"^FO{label_width_dots//2},260^A0N,14,14^FDFabricator:^FS")
    zpl.append(f"^FO{label_width_dots//2+100},258^A0N,16,16^FD{trunc(fabricator,14)}^FS")

    # ── Heat # ───────────────────────────────
    zpl.append("^FO15,282^A0N,14,14^FDHeat #:^FS")
    zpl.append(f"^FO85,280^A0N,16,16^FD{trunc(heat_num,20)}^FS")

    # ── Horizontal rule ──────────────────────
    zpl.append(f"^FO10,305^GB{label_width_dots-20},2,2^FS")

    # ── Barcode (Code 128) ───────────────────
    barcode_str = f"{job_code}-{part_code}"[:20]
    zpl.append(f"^FO15,315")
    zpl.append(f"^BCN,55,Y,N,N")
    zpl.append(f"^FD{barcode_str}^FS")

    # ── QR Code (if URL provided) ─────────────
    if qr_url:
        # QR code at right side
        qr_x = label_width_dots - 180
        zpl.append(f"^FO{qr_x},305")
        zpl.append("^BQN,2,3")
        zpl.append(f"^FDM,A{qr_url}^FS")

    # ── Bottom note ───────────────────────────
    zpl.append(f"^FO15,{label_height_dots-28}^A0N,13,13^FDStructures America · 14369 FM 1314 · Conroe TX 77302^FS")

    zpl.append("^XZ")  # End label
    return "\n".join(zpl)


# ─────────────────────────────────────────────
# STICKER GENERATION FROM BOM
# ─────────────────────────────────────────────

def generate_labels_from_bom(
    bom_data: dict,
    building_id: str = None,
    destination: str = "",
    fabricator: str = "",
    heat_nums: dict = None,
    qr_base_url: str = "https://structuresamerica.com/shop",
    grouping: dict = None,
) -> List[Dict]:
    """
    Generate label data for all parts in a BOM.
    Returns list of label dicts and ZPL strings.
    """
    if grouping is None:
        grouping = DEFAULT_GROUPING.copy()
    if heat_nums is None:
        heat_nums = {}

    proj = bom_data["project"]
    job_code = proj.get("job_code", "")
    mfg_date = datetime.date.today().strftime("%m/%d/%Y")

    # Filter buildings
    buildings = bom_data.get("buildings", [])
    if building_id:
        buildings = [b for b in buildings if b["id"] == building_id]

    labels = []
    tag_counter = 1

    for bldg in buildings:
        canopy_num = bldg.get("id", "B1")
        geo = bldg.get("geometry", {})

        # Items to skip (bulk fasteners, concrete, trim)
        SKIP_IDS = {
            "concrete_footings", "j_channel_trim",
            "tek_neoprene", "tek_structural", "stitch_screws",
        }

        for item in bldg.get("line_items", []):
            if item["unit"] not in ("LFT (coil)", "EA", "EA (sticks)"):
                continue
            if item["item_id"] in SKIP_IDS:
                continue

            part_labels = _make_labels_for_item(
                item, job_code, canopy_num, geo, destination,
                mfg_date, fabricator, heat_nums, qr_base_url,
                grouping, tag_counter
            )
            labels.extend(part_labels)
            tag_counter += len(part_labels)

    return labels


def _make_labels_for_item(
    item: dict,
    job_code: str,
    canopy_num: str,
    geo: dict,
    destination: str,
    mfg_date: str,
    fabricator: str,
    heat_nums: dict,
    qr_base_url: str,
    grouping: dict,
    start_tag: int,
) -> List[Dict]:
    """Create labels for a single BOM line item."""
    labels = []
    item_id = item["item_id"]
    desc = item["description"]
    qty = item["qty"]
    total_wt = item.get("total_weight_lbs", 0)
    heat = heat_nums.get(item_id, "")

    # Determine grouping size
    group_size = 1
    for key, size in grouping.items():
        if key in item_id:
            group_size = size
            break

    # Use piece_count if available (physical pieces), else fall back to qty
    piece_count = item.get("piece_count", 0)
    length_in = item.get("piece_length_in") or _extract_length(item, geo)
    part_name, type_code = _get_part_name_code(item_id, geo)

    if piece_count and piece_count > 0:
        # Physical piece-based labeling
        n_pieces = piece_count
        n_labels = max(1, (n_pieces + group_size - 1) // group_size)
        qty_per_label = min(group_size, n_pieces)
        unit_wt = total_wt / n_pieces if total_wt and n_pieces else 0
        wt_per_label = round(unit_wt * qty_per_label, 1)
    elif isinstance(qty, float) and qty > 0:
        # Coil items without piece count: 1 label per 500 LFT
        coil_group = max(1, round(qty / 500))
        n_labels = coil_group
        qty_per_label = round(qty / n_labels, 1)
        wt_per_label = round(total_wt / n_labels, 1) if total_wt else 0
    else:
        n_pieces = max(1, int(qty))
        n_labels = max(1, (n_pieces + group_size - 1) // group_size)
        qty_per_label = min(group_size, n_pieces)
        unit_wt = total_wt / n_pieces if total_wt else 0
        wt_per_label = round(unit_wt * qty_per_label, 1)

    tag = start_tag
    for i in range(n_labels):
        actual_qty = qty_per_label
        if i == n_labels - 1 and piece_count:
            # Last label gets remainder
            leftover = piece_count - qty_per_label * (n_labels - 1)
            actual_qty = max(1, leftover)

        part_code = make_part_code(int(actual_qty), part_name, type_code)
        qr_url = f"{qr_base_url}/{job_code}/{item_id}"

        zpl = _zpl_label(
            tag_num=tag,
            part_code=part_code,
            job_code=job_code,
            canopy_num=canopy_num,
            description=desc[:32],
            length_in=length_in,
            quantity=int(actual_qty),
            weight_lbs=round(wt_per_label, 1),
            destination=destination,
            manufacture_date=mfg_date,
            fabricator=fabricator,
            heat_num=heat,
            qr_url=qr_url,
        )

        labels.append({
            "tag_num": tag,
            "part_code": part_code,
            "job_code": job_code,
            "canopy_num": canopy_num,
            "description": desc[:50],
            "length_in": length_in,
            "quantity": int(actual_qty),
            "weight_lbs": round(wt_per_label, 1),
            "destination": destination,
            "manufacture_date": mfg_date,
            "fabricator": fabricator,
            "heat_num": heat,
            "zpl": zpl,
            "item_id": item_id,
        })
        tag += 1

    return labels


def _extract_length(item: dict, geo: dict) -> float:
    """Try to extract a meaningful length for the label."""
    item_id = item["item_id"]
    if "column" in item_id:
        return round(geo.get("low_col_ht_ft", 14) * 12, 2)
    elif "rafter" in item_id:
        return round(geo.get("rafter_half_length_ft", 20) * 12, 2)
    elif "purlin" in item_id and "plate" not in item_id:
        bays = geo.get("bays", [36])
        return round(max(bays) * 12, 2)
    elif "interior_plate" in item_id:
        return 10.0  # 10" plate
    elif "exterior_plate" in item_id:
        return 24.0  # 24" plate
    elif "strap" in item_id or "brace" in item_id:
        return 28.0  # 28" default
    elif "sag_rod" in item_id:
        return round(geo.get("width_ft", 40) / 2 * 12, 2)
    elif "rebar" in item_id:
        return 40 * 12  # 40' sticks
    return 0.0


def _get_part_name_code(item_id: str, geo: dict) -> tuple:
    """Return (part_name, type_code) for part code generation."""
    mapping = {
        "c_section_columns":  ("Columns",      "C14"),
        "c_section_rafters":  ("Rafters",       "R14"),
        "z_purlin":            ("Purlins",       "ZP"),
        "sag_rods":            ("SagRods",       "SR"),
        "spartan_rib":         ("RoofPanels",    "SP"),
        "interior_plates":     ("IntPlates",     "IP"),
        "exterior_plates":     ("ExtPlates",     "EP"),
        "straps_braces":       ("StrapsBreces",  "SB"),
        "cap_plates":          ("CapPlates",     "CP"),
        "gusset_triangles":    ("Gussets",       "GT"),
        "rebar_col_6":         ("ColRebar6",     "RC6"),
        "rebar_col_7":         ("ColRebar7",     "RC7"),
        "rebar_col_8":         ("ColRebar8",     "RC8"),
        "rebar_col_9":         ("ColRebar9",     "RC9"),
        "rebar_beam_6":        ("BeamRebar6",    "RB6"),
        "rebar_beam_7":        ("BeamRebar7",    "RB7"),
        "rebar_beam_8":        ("BeamRebar8",    "RB8"),
        "tek_neoprene":        ("TekNeo",        "TN"),
        "tek_structural":      ("TekStruct",     "TS"),
        "stitch_screws":       ("StitchScrew",   "SS"),
    }
    for key, val in mapping.items():
        if item_id.startswith(key) or item_id == key:
            return val
    return (item_id[:12], "XX")


def labels_to_zpl(labels: List[Dict]) -> str:
    """Concatenate all ZPL strings for printing."""
    return "\n\n".join(label["zpl"] for label in labels)


def labels_to_csv(labels: List[Dict]) -> bytes:
    """
    Export label data as CSV — import this into NiceLabel, BarTender,
    or any label software as a 'data source' for a template.

    Columns map directly to the label fields so no remapping is needed.
    """
    FIELDS = [
        "tag_num",        # e.g. 1, 2, 3
        "part_code",      # e.g. 39-Columns-C14
        "job_code",       # e.g. SANFL-24
        "canopy_num",     # e.g. B1
        "description",    # e.g. "C-Section Column 23\" 10GA"
        "length_in",      # e.g. 192.0
        "quantity",       # e.g. 2
        "weight_lbs",     # e.g. 88.4
        "destination",
        "manufacture_date",
        "fabricator",
        "heat_num",
        "item_id",        # internal ID for template logic
    ]
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=FIELDS, extrasaction="ignore",
                            lineterminator="\r\n")
    writer.writeheader()
    for lbl in labels:
        writer.writerow({k: lbl.get(k, "") for k in FIELDS})
    return buf.getvalue().encode("utf-8")


def labels_to_pdf(labels: List[Dict]) -> bytes:
    """
    Generate a PDF with one 4×6 inch label per page.
    Compatible with NiceLabel, ZebraDesigner, BarTender, or any PDF-capable
    label printer (send the PDF directly to the printer queue).

    Layout (4" × 6" = 288 × 432 points at 72 DPI):
      ┌──────────────────────────────────────────┐
      │ STRUCTURES AMERICA     TAG #0001   [job] │  ← dark header
      │                                          │
      │  Description text (large)                │
      │                                          │
      │  Part Code: 39-Columns-C14               │
      │  ─────────────────────────────────────   │
      │  Length    Qty       Weight              │
      │  192.0"    2         88.4 LBS            │
      │  ─────────────────────────────────────   │
      │  Origin: Conroe TX   Dest: Sanford FL    │
      │  Fabricator: J. Smith   Date: 04/07/26   │
      │  Heat #:  123456A                        │
      │  Canopy / Building: B1                   │
      └──────────────────────────────────────────┘
    """
    try:
        from reportlab.lib.pagesizes import landscape
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from reportlab.pdfgen import canvas as rl_canvas
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.platypus import Paragraph
        from reportlab.lib.enums import TA_LEFT, TA_CENTER
    except ImportError:
        raise ImportError("reportlab is required for PDF label export. "
                          "Run: pip install reportlab")

    # 4" × 6"  (width × height in points)
    W = 4 * inch
    H = 6 * inch
    M = 0.15 * inch   # margin

    SA_DARK  = colors.HexColor("#1A1A2E")
    SA_BLUE  = colors.HexColor("#1F4E79")
    SA_RED   = colors.HexColor("#C00000")
    SA_GOLD  = colors.HexColor("#FFC000")
    SA_LIGHT = colors.HexColor("#EEF3FA")
    WHITE    = colors.white
    GRAY     = colors.HexColor("#555555")

    buf = io.BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=(W, H))

    def draw_label(lbl: dict):
        c.setPageSize((W, H))

        # ── Dark header bar ──────────────────────────────────────────────
        hdr_h = 0.55 * inch
        c.setFillColor(SA_DARK)
        c.rect(0, H - hdr_h, W, hdr_h, fill=1, stroke=0)

        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(M, H - hdr_h + 0.20 * inch, "STRUCTURES AMERICA")
        c.setFont("Helvetica", 7)
        c.drawString(M, H - hdr_h + 0.07 * inch, f"Origin: Conroe, TX  ·  {lbl['job_code']}")

        # Tag number — right aligned
        _tn = lbl['tag_num']
        tag_str = f"TAG #{int(_tn):04d}" if str(_tn).isdigit() else f"TAG #{_tn}"
        c.setFont("Helvetica-Bold", 9)
        c.drawRightString(W - M, H - hdr_h + 0.13 * inch, tag_str)

        # ── Gold accent line ─────────────────────────────────────────────
        c.setStrokeColor(SA_GOLD)
        c.setLineWidth(2)
        c.line(0, H - hdr_h - 2, W, H - hdr_h - 2)

        # ── Description (large) ──────────────────────────────────────────
        y = H - hdr_h - 0.10 * inch
        desc = lbl.get("description", "")[:55]
        c.setFillColor(SA_BLUE)
        c.setFont("Helvetica-Bold", 11)
        # Wrap long descriptions
        if len(desc) > 30:
            mid = desc[:30].rfind(" ")
            if mid < 20: mid = 30
            line1, line2 = desc[:mid], desc[mid:].strip()
            c.drawString(M, y - 0.18 * inch, line1)
            c.drawString(M, y - 0.34 * inch, line2)
            y -= 0.38 * inch
        else:
            c.drawString(M, y - 0.20 * inch, desc)
            y -= 0.24 * inch

        # ── Part Code ────────────────────────────────────────────────────
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(M, y - 0.14 * inch, "PART CODE:")
        c.setFont("Courier-Bold", 10)
        c.setFillColor(SA_DARK)
        c.drawString(M + 0.70 * inch, y - 0.14 * inch, lbl.get("part_code", ""))
        y -= 0.18 * inch

        # ── Divider ──────────────────────────────────────────────────────
        c.setStrokeColor(colors.HexColor("#CCCCCC"))
        c.setLineWidth(0.5)
        c.line(M, y - 0.04 * inch, W - M, y - 0.04 * inch)
        y -= 0.12 * inch

        # ── Length / Qty / Weight grid ────────────────────────────────────
        col_w = (W - 2 * M) / 3
        labels_row = [
            ("LENGTH", f'{lbl.get("length_in", 0):.2f}"'),
            ("QTY",    str(lbl.get("quantity", ""))),
            ("WEIGHT", f'{lbl.get("weight_lbs", 0):.1f} LBS'),
        ]
        for i, (k, v) in enumerate(labels_row):
            cx = M + i * col_w + col_w / 2
            c.setFillColor(SA_LIGHT)
            c.rect(M + i * col_w + 2, y - 0.40 * inch, col_w - 4, 0.40 * inch, fill=1, stroke=0)
            c.setFillColor(GRAY)
            c.setFont("Helvetica", 7)
            c.drawCentredString(cx, y - 0.14 * inch, k)
            c.setFillColor(SA_DARK)
            c.setFont("Helvetica-Bold", 11)
            c.drawCentredString(cx, y - 0.33 * inch, v)
        y -= 0.46 * inch

        # ── Divider ──────────────────────────────────────────────────────
        c.setStrokeColor(colors.HexColor("#CCCCCC"))
        c.setLineWidth(0.5)
        c.line(M, y - 0.04 * inch, W - M, y - 0.04 * inch)
        y -= 0.12 * inch

        # ── Destination / Origin ─────────────────────────────────────────
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(M, y - 0.12 * inch, "DEST:")
        c.setFont("Helvetica", 8)
        dest = lbl.get("destination") or "—"
        c.drawString(M + 0.38 * inch, y - 0.12 * inch, dest[:30])
        y -= 0.16 * inch

        # ── Fabricator + Date ─────────────────────────────────────────────
        fab = lbl.get("fabricator") or "—"
        dt  = lbl.get("manufacture_date", "")
        c.setFont("Helvetica-Bold", 7)
        c.drawString(M, y - 0.12 * inch, "FABRICATOR:")
        c.setFont("Helvetica", 7)
        c.drawString(M + 0.66 * inch, y - 0.12 * inch, fab[:22])
        c.setFont("Helvetica-Bold", 7)
        c.drawRightString(W - M, y - 0.12 * inch, dt)
        y -= 0.16 * inch

        # ── Heat Number ───────────────────────────────────────────────────
        heat = lbl.get("heat_num") or ""
        c.setFillColor(SA_RED if heat else GRAY)
        c.setFont("Helvetica-Bold", 7)
        heat_label = "HEAT #:"
        c.drawString(M, y - 0.12 * inch, heat_label)
        c.setFont("Courier-Bold" if heat else "Helvetica", 9 if heat else 7)
        c.drawString(M + 0.46 * inch, y - 0.12 * inch, heat if heat else "— not assigned —")
        y -= 0.16 * inch

        # ── Canopy / Building ─────────────────────────────────────────────
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 7)
        c.drawString(M, y - 0.12 * inch,
                     f"Building: {lbl.get('canopy_num','—')}   ·   Item ID: {lbl.get('item_id','—')}")

        # ── Bottom barcode strip ──────────────────────────────────────────
        # Code128 barcode using ReportLab's built-in barcode module
        try:
            from reportlab.graphics.barcode import code128
            _tn2 = lbl['tag_num']
            _tn2_str = f"{int(_tn2):04d}" if str(_tn2).isdigit() else str(_tn2)
            barcode_val = f"{lbl['job_code']}-{_tn2_str}"
            bc = code128.Code128(barcode_val,
                                 barHeight=0.30 * inch,
                                 barWidth=0.018 * inch,
                                 humanReadable=True,
                                 fontSize=5)
            bc_w = bc.width
            bc_x = (W - bc_w) / 2
            bc_y = 0.06 * inch
            bc.drawOn(c, bc_x, bc_y)
        except Exception:
            # Barcode unavailable — just print the value as text
            _tn3 = lbl['tag_num']
            _tn3_str = f"{int(_tn3):04d}" if str(_tn3).isdigit() else str(_tn3)
            c.setFont("Courier", 7)
            c.setFillColor(GRAY)
            c.drawCentredString(W / 2, 0.10 * inch,
                                f"{lbl['job_code']}-{_tn3_str}")

    for lbl in labels:
        draw_label(lbl)
        c.showPage()

    c.save()
    return buf.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
# INVENTORY COIL STICKER  (4" × 6"  PDF / ZPL / CSV)
# ─────────────────────────────────────────────────────────────────────────────

def _coil_qr_drawing(url: str, size_pts: float):
    """Return a ReportLab Drawing containing a QR code for *url*."""
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.barcode.qr import QrCodeWidget
    from reportlab.graphics import renderPDF

    qr_widget = QrCodeWidget(url)
    bounds = qr_widget.getBounds()
    qr_w = bounds[2] - bounds[0]
    qr_h = bounds[3] - bounds[1]
    scale = size_pts / max(qr_w, qr_h)

    d = Drawing(size_pts, size_pts)
    d.transform = (scale, 0, 0, scale, 0, 0)
    d.add(qr_widget)
    return d


def coil_sticker_to_pdf(coil: dict, app_base_url: str = "http://localhost:8888") -> bytes:
    """
    Generate a 4"×6" inventory sticker PDF for a single coil.

    coil keys used:
      coil_id, description, grade, gauge, heat_num, supplier,
      weight_lbs, width_in, qty_on_hand, received_date
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.pdfgen.canvas import Canvas
    from reportlab.lib.colors import HexColor, white, black

    SA_NAVY  = HexColor('#003A6E')
    SA_GOLD  = HexColor('#C89A2E')
    GRAY_LT  = HexColor('#F5F5F5')
    GRAY_MID = HexColor('#606060')
    WHITE    = white

    W = 4.0 * inch
    H = 6.0 * inch
    M = 0.18 * inch          # margin

    buf = io.BytesIO()
    c = Canvas(buf, pagesize=(W, H))

    coil_id   = str(coil.get("coil_id", "—"))
    desc      = str(coil.get("description", ""))[:60]
    grade     = str(coil.get("grade", "—"))
    gauge     = str(coil.get("gauge", "—"))
    heat_num  = str(coil.get("heat_num", "—"))
    supplier  = str(coil.get("supplier", "—"))
    weight    = coil.get("weight_lbs", "—")
    width     = coil.get("width_in", "—")
    qty       = coil.get("qty_on_hand", "—")
    rx_date   = str(coil.get("received_date", datetime.date.today().strftime("%m/%d/%Y")))
    print_date = datetime.date.today().strftime("%m/%d/%Y")

    qr_url = f"{app_base_url}/coil/{coil_id}"

    # ── Header bar ──────────────────────────────────────────────────────────
    hdr_h = 0.65 * inch
    c.setFillColor(SA_NAVY)
    c.rect(0, H - hdr_h, W, hdr_h, fill=1, stroke=0)

    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(M, H - hdr_h + 0.22 * inch, "STRUCTURES AMERICA")
    c.setFont("Helvetica", 7)
    c.drawString(M, H - hdr_h + 0.07 * inch, "Inventory · Conroe, TX")

    c.setFont("Helvetica-Bold", 8)
    c.drawRightString(W - M, H - hdr_h + 0.22 * inch, "COIL STICKER")
    c.setFont("Helvetica", 7)
    c.drawRightString(W - M, H - hdr_h + 0.07 * inch, f"Printed: {print_date}")

    # ── Gold accent line ─────────────────────────────────────────────────────
    c.setStrokeColor(SA_GOLD)
    c.setLineWidth(2)
    c.line(0, H - hdr_h - 2, W, H - hdr_h - 2)

    # ── Coil ID (large) ──────────────────────────────────────────────────────
    y = H - hdr_h - 0.12 * inch
    c.setFillColor(SA_NAVY)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(M, y - 0.28 * inch, coil_id)

    # ── Description ──────────────────────────────────────────────────────────
    c.setFont("Helvetica", 9)
    c.setFillColor(GRAY_MID)
    if len(desc) > 35:
        mid = desc[:35].rfind(" ")
        if mid < 20: mid = 35
        c.drawString(M, y - 0.46 * inch, desc[:mid])
        c.drawString(M, y - 0.58 * inch, desc[mid:].strip())
        y_after_desc = y - 0.72 * inch
    else:
        c.drawString(M, y - 0.46 * inch, desc)
        y_after_desc = y - 0.60 * inch

    # ── Divider ───────────────────────────────────────────────────────────────
    c.setStrokeColor(SA_GOLD)
    c.setLineWidth(1)
    c.line(M, y_after_desc, W - M, y_after_desc)

    # ── Two-column info grid (left) + QR (right) ─────────────────────────────
    qr_size = 1.35 * inch
    qr_x    = W - M - qr_size
    qr_y    = y_after_desc - qr_size - 0.08 * inch

    # Draw QR code
    try:
        qr_drawing = _coil_qr_drawing(qr_url, qr_size)
        from reportlab.graphics import renderPDF
        renderPDF.draw(qr_drawing, c, qr_x, qr_y)
    except Exception:
        # Fallback: text URL if QR fails
        c.setFont("Helvetica", 6)
        c.setFillColor(GRAY_MID)
        c.drawString(qr_x, qr_y + qr_size / 2, qr_url[:30])

    # Info grid (left side, beside QR)
    info_w = qr_x - M - 0.1 * inch
    def info_row(label, value, iy):
        c.setFont("Helvetica-Bold", 7)
        c.setFillColor(GRAY_MID)
        c.drawString(M, iy, label.upper())
        c.setFont("Helvetica", 9)
        c.setFillColor(black)
        c.drawString(M, iy - 0.13 * inch, str(value)[:22])

    row_h = 0.30 * inch
    iy = y_after_desc - 0.20 * inch
    info_row("Grade",    grade,   iy);              iy -= row_h
    info_row("Gauge",    gauge,   iy);              iy -= row_h
    info_row("Heat #",   heat_num, iy);             iy -= row_h
    info_row("Supplier", supplier, iy)

    # ── Second divider ────────────────────────────────────────────────────────
    div2_y = qr_y - 0.12 * inch
    c.setStrokeColor(HexColor('#CCCCCC'))
    c.setLineWidth(0.5)
    c.line(M, div2_y, W - M, div2_y)

    # ── Bottom stats row ──────────────────────────────────────────────────────
    stats_y = div2_y - 0.14 * inch
    col_w = (W - 2 * M) / 3

    stats = [
        ("Weight (lbs)", f"{weight}" if weight != "—" else "—"),
        ("Width (in)",   f"{width}"  if width  != "—" else "—"),
        ("Qty On Hand",  str(qty)),
    ]
    for i, (lbl, val) in enumerate(stats):
        bx = M + i * col_w
        # Shaded cell
        fill_hex = '#E8EEF8' if i % 2 == 0 else '#F5F5F5'
        c.setFillColor(HexColor(fill_hex))
        c.rect(bx, stats_y - 0.30 * inch, col_w - 0.04 * inch, 0.46 * inch, fill=1, stroke=0)
        c.setFont("Helvetica-Bold", 7)
        c.setFillColor(SA_NAVY)
        c.drawCentredString(bx + col_w / 2 - 0.02 * inch, stats_y + 0.06 * inch, lbl.upper())
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(black)
        c.drawCentredString(bx + col_w / 2 - 0.02 * inch, stats_y - 0.20 * inch, str(val))

    # ── Received date + scan prompt ───────────────────────────────────────────
    foot_y = stats_y - 0.50 * inch
    c.setFont("Helvetica", 7)
    c.setFillColor(GRAY_MID)
    c.drawString(M, foot_y, f"Received: {rx_date}")
    c.drawRightString(W - M, foot_y, "Scan QR to view job status →")

    # ── Footer bar ────────────────────────────────────────────────────────────
    foot_bar_h = 0.22 * inch
    c.setFillColor(SA_NAVY)
    c.rect(0, 0, W, foot_bar_h, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica", 6)
    c.drawCentredString(W / 2, 0.07 * inch, qr_url)

    c.save()
    return buf.getvalue()


def coil_sticker_to_zpl(coil: dict, app_base_url: str = "http://localhost:8888",
                         dpi: int = 203) -> str:
    """
    Generate ZPL II for a 4"×6" coil inventory sticker.
    Compatible with Zebra ZT411 / ZT230 at 203 or 300 DPI.
    """
    def d(inches): return int(inches * dpi)

    coil_id   = str(coil.get("coil_id", ""))
    desc      = str(coil.get("description", ""))[:40]
    grade     = str(coil.get("grade", ""))
    gauge     = str(coil.get("gauge", ""))
    heat_num  = str(coil.get("heat_num", ""))
    supplier  = str(coil.get("supplier", ""))
    weight    = str(coil.get("weight_lbs", ""))
    width_in  = str(coil.get("width_in", ""))
    qty       = str(coil.get("qty_on_hand", ""))
    rx_date   = str(coil.get("received_date", datetime.date.today().strftime("%m/%d/%Y")))
    print_date = datetime.date.today().strftime("%m/%d/%Y")
    qr_url    = f"{app_base_url}/coil/{coil_id}"

    W = d(4.0)   # label width dots
    H = d(6.0)   # label height dots

    lines = [
        "^XA",
        f"^PW{W}",
        f"^LL{H}",
        "^CI28",   # UTF-8

        # ── Header bar ──────────────────────────────────────────────────
        f"^FO0,0^GB{W},{d(0.6)},40^FS",
        f"^FO{d(0.15)},{d(0.06)}^A0N,20,20^FH^FDSTRUCTURES AMERICA^FS",
        f"^FO{d(0.15)},{d(0.32)}^A0N,14,14^FH^FDInventory  Conroe TX^FS",
        f"^FO{d(2.5)},{d(0.06)}^A0N,18,18^FH^FDCOIL STICKER^FS",
        f"^FO{d(2.5)},{d(0.30)}^A0N,13,13^FH^FDPrinted: {print_date}^FS",

        # ── Gold accent line (dashed via graphic box) ─────────────────
        f"^FO0,{d(0.62)}^GB{W},3,3^FS",

        # ── Coil ID large ─────────────────────────────────────────────
        f"^FO{d(0.15)},{d(0.70)}^A0N,42,36^FH^FD{coil_id}^FS",
        f"^FO{d(0.15)},{d(1.18)}^A0N,16,16^FH^FD{desc}^FS",

        # ── Divider ────────────────────────────────────────────────────
        f"^FO0,{d(1.42)}^GB{W},2,2^FS",

        # ── Info rows (left) ───────────────────────────────────────────
        f"^FO{d(0.15)},{d(1.48)}^A0N,13,13^FH^FDGRADE^FS",
        f"^FO{d(0.15)},{d(1.62)}^A0N,18,18^FH^FD{grade}^FS",
        f"^FO{d(0.15)},{d(1.90)}^A0N,13,13^FH^FDGAUGE^FS",
        f"^FO{d(0.15)},{d(2.04)}^A0N,18,18^FH^FD{gauge}^FS",
        f"^FO{d(0.15)},{d(2.32)}^A0N,13,13^FH^FDHEAT #^FS",
        f"^FO{d(0.15)},{d(2.46)}^A0N,18,18^FH^FD{heat_num}^FS",
        f"^FO{d(0.15)},{d(2.74)}^A0N,13,13^FH^FDSUPPLIER^FS",
        f"^FO{d(0.15)},{d(2.88)}^A0N,18,18^FH^FD{supplier[:20]}^FS",

        # ── QR code (right side) ───────────────────────────────────────
        f"^FO{d(2.4)},{d(1.50)}^BQN,2,5^FDQA,{qr_url}^FS",

        # ── Stats row ─────────────────────────────────────────────────
        f"^FO0,{d(3.42)}^GB{W},2,2^FS",
        # Weight cell
        f"^FO{d(0.05)},{d(3.50)}^GB{d(1.27)},{d(0.70)},1^FS",
        f"^FO{d(0.15)},{d(3.54)}^A0N,13,13^FH^FDWEIGHT (LBS)^FS",
        f"^FO{d(0.28)},{d(3.72)}^A0N,24,22^FH^FD{weight}^FS",
        # Width cell
        f"^FO{d(1.38)},{d(3.50)}^GB{d(1.27)},{d(0.70)},1^FS",
        f"^FO{d(1.48)},{d(3.54)}^A0N,13,13^FH^FDWIDTH (IN)^FS",
        f"^FO{d(1.61)},{d(3.72)}^A0N,24,22^FH^FD{width_in}^FS",
        # Qty cell
        f"^FO{d(2.70)},{d(3.50)}^GB{d(1.24)},{d(0.70)},1^FS",
        f"^FO{d(2.80)},{d(3.54)}^A0N,13,13^FH^FDQTY ON HAND^FS",
        f"^FO{d(3.00)},{d(3.72)}^A0N,24,22^FH^FD{qty}^FS",

        # ── Received date + scan prompt ───────────────────────────────
        f"^FO{d(0.15)},{d(4.34)}^A0N,13,13^FH^FDReceived: {rx_date}^FS",
        f"^FO{d(1.80)},{d(4.34)}^A0N,13,13^FH^FDScan QR to view job status^FS",

        # ── Footer bar with URL ────────────────────────────────────────
        f"^FO0,{d(5.76)}^GB{W},{d(0.24)},40^FS",
        f"^FO{d(0.15)},{d(5.80)}^A0N,12,12^FR^FH^FD{qr_url}^FS",

        "^XZ",
    ]
    return "\n".join(lines)


def coil_stickers_to_csv(coils: List[dict]) -> bytes:
    """
    Export coil sticker data as CSV for NiceLabel / BarTender import.
    One row per coil.
    """
    fields = [
        "coil_id", "description", "grade", "gauge", "heat_num",
        "supplier", "weight_lbs", "width_in", "qty_on_hand",
        "received_date", "print_date", "qr_url",
    ]
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fields, extrasaction='ignore')
    writer.writeheader()
    today = datetime.date.today().strftime("%m/%d/%Y")
    for coil in coils:
        row = {f: coil.get(f, "") for f in fields}
        row["print_date"] = today
        row["qr_url"] = f"http://localhost:8888/coil/{coil.get('coil_id','')}"
        writer.writerow(row)
    return buf.getvalue().encode("utf-8")


def labels_to_preview_html(labels: List[Dict]) -> str:
    """Generate HTML preview of label data (not ZPL rendering)."""
    rows = []
    rows.append("""
    <style>
    .label-card {
        border: 2px solid #1F4E79; border-radius: 6px;
        padding: 10px 14px; margin: 8px; display: inline-block;
        width: 320px; vertical-align: top; font-family: monospace; font-size: 11px;
        background: #fff; box-shadow: 2px 2px 5px #ccc;
    }
    .label-header { background: #1A1A2E; color: #fff; padding: 5px 8px;
        font-weight: bold; margin: -10px -14px 8px; border-radius: 4px 4px 0 0; }
    .label-row { display: flex; justify-content: space-between; margin: 2px 0; }
    .label-key { color: #666; font-weight: bold; }
    .label-val { color: #222; }
    .label-divider { border-top: 1px dashed #ccc; margin: 5px 0; }
    </style>
    """)

    for lbl in labels:
        rows.append(f"""
        <div class="label-card">
          <div class="label-header">STRUCTURES AMERICA &nbsp;|&nbsp; TAG #{lbl['tag_num']:04d}</div>
          <div class="label-row"><span class="label-key">Job:</span><span class="label-val">{lbl['job_code']}</span>
            <span class="label-key">Canopy:</span><span class="label-val">{lbl['canopy_num']}</span></div>
          <div class="label-row"><span class="label-key">Part Code:</span><span class="label-val">{lbl['part_code']}</span></div>
          <div class="label-row"><span class="label-key">Desc:</span><span class="label-val">{lbl['description'][:40]}</span></div>
          <div class="label-divider"></div>
          <div class="label-row">
            <span class="label-key">Length:</span><span class="label-val">{lbl['length_in']:.2f}"</span>
            <span class="label-key">Qty:</span><span class="label-val">{lbl['quantity']}</span>
            <span class="label-key">Wt:</span><span class="label-val">{lbl['weight_lbs']:.1f} LBS</span>
          </div>
          <div class="label-divider"></div>
          <div class="label-row"><span class="label-key">Origin:</span><span class="label-val">Conroe, TX</span>
            <span class="label-key">Dest:</span><span class="label-val">{lbl['destination'] or '—'}</span></div>
          <div class="label-row"><span class="label-key">Mfg Date:</span><span class="label-val">{lbl['manufacture_date']}</span></div>
          <div class="label-row"><span class="label-key">Fabricator:</span><span class="label-val">{lbl['fabricator'] or '—'}</span></div>
          <div class="label-row"><span class="label-key">Heat #:</span><span class="label-val">{lbl['heat_num'] or '—'}</span></div>
        </div>
        """)

    return "\n".join(rows)
