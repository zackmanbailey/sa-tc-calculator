======================================================
  STRUCTURES AMERICA Material Takeoff Calculator
  Version 1.0 - Phase 1
  Titan Carports Inc. / Structures America
  14369 FM 1314, Conroe, TX 77302
======================================================

QUICK START
-----------
Windows:  Double-click  START_CALCULATOR.bat
Mac/Linux: Run          ./start_calculator.sh  (or: python3 app.py)

The calculator opens in your web browser at:
  http://localhost:8888

REQUIREMENTS
------------
Python 3.8 or higher
Python packages: tornado, openpyxl, reportlab, pillow
  (install with: pip install tornado openpyxl reportlab pillow)

FEATURES (Phase 1)
------------------
✅ Multi-building project setup
✅ Automatic bay layout (symmetric, max 36' default)
✅ BOM calculation for all 7 coil types:
    1. 23" 10GA — Columns & Rafters (C-14"×4"×10GA)
    2. 20.125" 12GA — Z-Purlins (Z-12"×3.5"×12GA)
    3. 4" 16GA — Sag Rods (2"×2" angle)
    4. 48" 29GA G50 — Spartan Rib Roof Panels
    5. 6" 10GA — Interior Purlin-to-Rafter Plates
    6. 9" 10GA — Exterior Purlin-to-Rafter Plates
    7. 1.5" 10GA — Hurricane Straps & Bottom Braces
✅ Purchased items (cap plates, gusset triangles)
✅ Rebar auto-selection (A706, Katy Steel)
✅ Concrete footing quantity
✅ Screw counts (TEK w/neoprene, TEK structural, stitch)
✅ Optional J-channel trim
✅ Variable purlin spacing rule (5'@≤30'bay, 4'@30-34', 3.5'@35-40')
✅ Waste factors (10GA=3%, 12GA=3%, 16GA=2%, 29GA=5%, Rebar=5%)
✅ 35% markup (editable)
✅ Excel BOM export (branded, multi-tab)
✅ PDF Quote export (signature line, Structures America branding)
✅ ZPL sticker generation (Zebra ZT411, 203 DPI)
✅ Shop label preview
✅ Inventory management (stock levels, mill cert tracking)

COIL SPECIFICATIONS
-------------------
All 7 coils come PRE-SLIT from supplier in specific widths.
Box beams and columns require TWO C-sections welded together per piece.

PURLIN SPACING RULES
--------------------
Bay size ≤ 30'-0"   → Purlins at 5'-0" OC
Bay size 30'-1" to 34'-4" → 4'-0" OC
Bay size 34'-5" to 40'-0" → 3'-6" OC

REBAR AUTO-SELECTION
--------------------
2-post columns (55 KSI): #6 or higher for wide spans
Tee columns (75 KSI): #6-#9 based on width + wind speed
Beams: #7 or #8 based on width + wind speed

WIND SPEED DEFAULTS BY STATE
-----------------------------
TX: 115 MPH  FL: 140 MPH  OK/KS/NE: 130 MPH  Others: 115 MPH

LABEL SYSTEM (Zebra ZT411)
---------------------------
- 4"×3" labels at 203 DPI
- TAG #, Part Code, Job Code, Canopy #, Description
- Length (inches), Qty, Weight, Origin (Conroe TX), Destination
- Manufacture Date, Fabricator, Heat # fields
- Code 128 barcode + QR code for shop drawing link
- ZPL file downloads directly for printing

INVENTED FILES
--------------
data/inventory.json  — Persists inventory between sessions

FUTURE PHASES
-------------
Phase 2: Bill of lading, production schedule, truck count
Phase 3: AI site plan reader (automatic takeoff from PDF/image)
Phase 4: Engineering report PDF (no costs, for engineer)
Phase 5: Shop drawings generator

CONTACT
-------
Haley McClendon
(832) 791-8965
haley@structuresamerica.com
======================================================
