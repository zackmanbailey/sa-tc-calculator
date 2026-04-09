"""
TitanForge Shop Drawing System
Auto-populating shop drawings for steel fabrication.
Components: Columns, Rafters, Purlins, Endcaps, Roofing, Wall Panels,
            Wall Girts, Sag Rods, Hurricane Straps, Splice Plates.

Modules:
  config.py      - All defaults, rules, constraints, ShopDrawingConfig dataclass
  column_gen.py  - Column 4-view shop drawing PDF
  rafter_gen.py  - Rafter shop drawing with purlin layout
  purlin_gen.py  - Purlin group drawings (First/Middle/Last)
  cutlist_gen.py - Cut lists for endcaps, roofing, walls, sag rods, straps
  sticker_gen.py - 4"x6" fabrication sticker/label generator
  shipping_gen.py - Shipping manifest with loading order
  master.py      - Orchestrator that generates all drawings for a project
"""
