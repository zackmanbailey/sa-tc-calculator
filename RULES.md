# TitanForge v5.0 — Master Rules & Reference

**System:** TitanForge Mission Control
**Companies:** Titan Carports Inc. / Structures America
**Shop Address:** 14369 FM 1314, Conroe, TX 77302
**Last Updated:** April 14, 2026

---

## 1. System Overview

TitanForge is an end-to-end steel fabrication management platform covering estimating, BOM calculation, shop drawing generation, work order management, inventory control, QA/QC, shipping, and field operations. The system is built on Python/Tornado with a role-based access control (RBAC) system that presents a tailored experience to each user based on their assigned roles.

### Core Engines (Do Not Rewrite)

These modules contain validated math and fabrication logic. They are extended, never replaced:

- `calc/bom.py` — BOM calculation engine (rafter-first design, 7 coil types, variable column heights)
- `calc/defaults.py` — Material specs, pricing, waste factors, labor rates, rebar selection
- `shop_drawings/config.py` — Fabrication defaults, machine definitions, WPS codes, drawing specs
- `shop_drawings/*.py` — Drawing generation logic (column, rafter, purlin, cut list, stickers)
- `outputs/*.py` — PDF and Excel export generation

### Architecture Principles

- **Rafter-first design:** Frame type is auto-determined from building width (<=45' = TEE, >45' = multi-column). The rafter shop drawing is the source of truth for column placement.
- **Role-merged UI:** Each user sees a unified dashboard assembled from cards contributed by their assigned roles. The app feels purpose-built for each person.
- **Financial data isolation:** Dollar amounts are never rendered in HTML for users without financial permissions. Not hidden with CSS — actually excluded from the response.
- **Permission middleware:** Every request passes through role/permission checks before reaching the handler. Unauthorized URLs redirect to the user's dashboard, not a 403 page.
- **Shared layout system:** One base template with dynamic sidebar. Pages only define their content area.

---

## 2. Roles & Permissions

### 2.1 Role List

| # | Role | Financial Access | Can Delete | Can Manage Users |
|---|------|-----------------|------------|------------------|
| 0 | God Mode | Full | Yes | Yes |
| 1 | Admin | Full | No | No |
| 2 | Project Manager | Full | No | No |
| 3 | Estimator | Quoting costs & pricing | No | No |
| 4 | Sales / Business Dev | Quote totals only | No | No |
| 5 | Purchasing / Procurement | Vendor costs & PO pricing | No | No |
| 6 | Inventory Manager | No (quantities only) | No | No |
| 7 | Accounting / Bookkeeper | Full | No | No |
| 8 | Shop Foreman | No (can submit receipts) | No | No |
| 9 | QA/QC Inspector | No | No | No |
| 10 | Engineer / Detailer | No | No | No |
| 11 | Roll Forming Operator | No | No | No |
| 12 | Welder | No | No | No |
| 13 | Shipping Coordinator | No (weights & counts only) | No | No |
| 14 | Laborer | No | No | No |
| 15 | Field Crew | No (can submit expenses) | No | No |
| 16 | Safety Officer | No | No | No |
| 17 | Customer (External) | Their quote/invoice only | No | No |

### 2.2 Multi-Role Rules

- Users can be assigned multiple roles simultaneously.
- Dashboard cards are the union of all assigned role cards, grouped by function.
- Sidebar sections are the union of all role sidebars.
- Financial visibility: granted only if at least one assigned role explicitly allows it AND the current page context is appropriate.
- Access permissions are additive (union of all roles).
- Destructive permissions (delete) require explicit role grant — not inherited from additive access.
- The UI must feel like a single cohesive app for any role combination, not a collection of tabs.

### 2.3 Role Details

#### God Mode
- **Sees:** Everything in the system.
- **Can do:** Everything Admin can do, plus: create/deactivate users, assign/remove roles, delete projects/files/data (with confirmation), view audit logs, configure system settings (defaults, pricing, company info), manage AISC document library.
- **Dashboard cards:** Business Summary, All Projects, User Management, System Health, Audit Log.
- **Sidebar:** All sections visible.

#### Admin
- **Sees:** Everything in the system.
- **Can do:** Interact with all features — run calculations, create projects, manage work orders, view financials, approve items. Cannot: delete anything, create/remove users, assign roles, access user management.
- **Dashboard cards:** Business Summary, All Projects (with financials), Recent Activity (company-wide).
- **Sidebar:** All sections except User Management.

#### Project Manager
- **Sees:** All project data including financials, shop/field status, customer info. Full cross-functional visibility.
- **Can do:** Convert quotes to active projects, set timelines/milestones, track budget vs. actual, coordinate between shop and field, communicate with customers. Cannot: edit shop drawings, sign off QC, manage users.
- **Dashboard cards:** Active Projects (with budget/timeline), Milestones, Shop Progress Summary, Field Status, Customer Communications.
- **Sidebar:** Projects, Timeline, Budget, Shop Status, Field Status, Shipping, Reports.

#### Estimator
- **Sees:** SA Calculator (full access), BOM with full pricing, inventory levels (read-only, quantities only), quote pipeline.
- **Can do:** Run calculations, generate BOM, save projects, create quote versions, export PDF/Excel quotes. View project status (percentage only, no details). Cannot: access shop drawings, work orders, manufacturing, QC, shipping, or field.
- **Dashboard cards:** Active Quotes (pipeline), Quick Calculator shortcut, Inventory Stock Summary (read-only).
- **Sidebar:** Calculator, My Projects, Quotes, Inventory Levels.

#### Sales / Business Development
- **Sees:** Customer contact info, quote pipeline (totals only, not line-item BOM), project status summaries, lead tracking.
- **Can do:** Manage leads, follow up on quotes, track win/loss, view customer history. Cannot: see BOM details, shop drawings, manufacturing, or detailed pricing.
- **Dashboard cards:** Sales Pipeline, Active Leads, Recent Quote Activity, Win/Loss.
- **Sidebar:** Pipeline, Leads, Customers, Quote Status.

#### Purchasing / Procurement
- **Sees:** Vendor pricing, PO history, cost comparisons, inventory levels, material requirements from active BOMs.
- **Can do:** Create and manage purchase orders, track PO status, negotiate/update vendor pricing, view cost trends. Cannot: see customer pricing, markup, or sell prices.
- **Dashboard cards:** Open POs, Pending Deliveries, Price Alerts, Vendor Summary.
- **Sidebar:** Purchase Orders, Vendors, Price History, Material Requirements.

#### Inventory Manager
- **Sees:** Full inventory across all types (coils, purchased items, rebar, fasteners, consumables), allocation status (which items assigned to which project), receiving logs. No pricing or costs.
- **Can do:** Receive and scan incoming inventory, link mill certs, assign storage locations, allocate stock to projects, flag reorder alerts, track coil identity (heat number, weight remaining). Cannot: see costs, create POs (that's Purchasing), or modify projects.
- **Dashboard cards:** Inventory Alerts (low stock), Incoming Deliveries, Allocation Summary, Recent Receiving.
- **Sidebar:** Coil Inventory, Purchased Items, Rebar Stock, Fasteners, Receiving, Allocations, Mill Certs.

#### Accounting / Bookkeeper
- **Sees:** All financial data — BOM costs, sell prices, margins, labor costs, consumable receipts (submitted by Shop Foreman), field expense reports, equipment rental costs, vendor POs/bills, customer invoices.
- **Can do:** View/export financial reports, process expense reports, generate project P&L, track revenue. Cannot: modify projects, edit work orders, approve QC, or interact with manufacturing.
- **Dashboard cards:** Revenue Summary, Pending Expense Reports, Project P&L, Vendor Bills Due.
- **Sidebar:** Financial Dashboard, Project Costs, Expense Reports, Equipment Costs, Vendor Bills, Invoices, Reports.

#### Shop Foreman
- **Sees:** All project files EXCEPT financial data. Work orders, shop drawings, machine queues, crew assignments, fabrication progress, QC status (read-only). Can see his own consumable receipt submissions but not project cost totals.
- **Can do:** Create/manage work orders, assign items to machines and operators, reprioritize queues, edit workflows, start/finish items (act as any operator if needed), submit consumable purchase receipts (photo + amount + category). Cannot: see any costs/prices/margins, sign off QC, manage users, delete anything.
- **Dashboard cards:** Shop Floor Overview (machines), Active Projects (progress bars, no costs), Today's Priorities, Crew Status, Consumable Receipt Log (own submissions).
- **Sidebar:** Shop Floor, Work Orders, Workflows, Machine Queues, Crew, Consumable Receipts, Shop Drawings.
- **Special:** Consumable receipt submission flow: photo upload, amount entry, category select (welding wire, gas, grinding discs, paint, other). Foreman sees a running total of his own submissions for the month but never project-level costs.

#### QA/QC Inspector
- **Sees:** All shop drawings and plans, inspection queues, NCR log, traceability chain, AISC document library, mill certs, fabrication notes from operators. No financial data.
- **Can do:** Inspect completed items, create/complete checklists, sign off (digital signature = item passes), reject items with notes (sends back to operator queue), create Non-Conformance Reports (NCR), upload inspection photos, manage traceability records, access AISC reference documents. Cannot: edit workflows, modify work orders, see costs.
- **Dashboard cards:** Inspection Queue, Open NCRs, Recent Sign-offs, AISC Library shortcut.
- **Sidebar:** Inspection Queue, NCR Log, Shop Drawings, Plans, Mill Certs, AISC Library, Traceability, Audit Log.

#### Engineer / Detailer
- **Sees:** Shop drawings (with edit access), plans, calculator outputs, structural details, connection details. No financial data.
- **Can do:** Upload and manage engineered/stamped drawings, review calculator outputs for non-standard configurations, modify shop drawing details, approve structural details before fabrication, stamp drawings. Cannot: manage work orders, approve QC, see costs.
- **Dashboard cards:** Drawings Pending Review, Recent Uploads, Project Drawing Sets.
- **Sidebar:** Shop Drawings (edit), Plans, Calculator Review, Drawing Upload, Approvals.

#### Roll Forming Operator
- **Sees:** Work order items assigned to their machine(s), coil information (type, gauge, width), run lengths, production queue. No financial data, no full project details.
- **Can do:** Scan QR to Start/Finish roll-formed items (purlins, panels, sag rods, plates, straps, endcaps), view run queue, log coil changeovers (which coil consumed, new roll loaded), see coil remaining estimate. Cannot: edit work orders, see costs, access drawings beyond their item details.
- **Dashboard cards:** Machine Status (coil loaded, remaining), Run Queue, Production Log (today's output).
- **Sidebar:** My Machine, Run Queue, Production Log, Coil Status.

#### Welder
- **Sees:** Assigned work order items, all shop drawings (column, rafter, connection details), cut lists, sticker details. No financial data.
- **Can do:** Scan QR to Start/Finish fabrication items, view shop drawings (zoom, pan, dimensions), log notes on items (feeds into QC), see QC status of completed items (Pending/Approved/Rejected with notes). Cannot: edit work orders, see costs, modify drawings.
- **Dashboard cards:** My Queue (assigned items), Active Item (with inline shop drawing), Recently Completed (with QC status).
- **Sidebar:** My Queue, Shop Drawings, Cut List, Completed Items.

#### Shipping Coordinator
- **Sees:** Work order item statuses (done/in-progress/queued), estimated completion, manifest, BOM item list (quantities and dimensions, no pricing), load history, delivery addresses.
- **Can do:** Build shipping loads (select completed items, group into loads, see running weight total), generate Bill of Lading (BOL), mark items as Shipped, track loads in transit. Cannot: see costs, modify work orders, interact with fabrication.
- **Dashboard cards:** Ready to Ship (QC-approved items by project), Active Loads, Fabrication Progress (percentage bars).
- **Sidebar:** Dashboard, Build Load, Active Shipments, BOL History, Project Status.
- **Special:** Load builder must include weight totalizer (running sum from BOM item weights) for DOT compliance. BOL auto-populates from load contents.

#### Laborer
- **Sees:** Assigned staging/moving tasks from active work orders. Item ID, description, destination machine. No project details, no drawings, no financial data.
- **Can do:** Scan QR to confirm item staged/moved, view item status and destination. Cannot: Start/Finish fabrication items, see drawings, access any other pages.
- **Dashboard cards:** Today's Tasks (staging checklist), Quick Scan button, Recent Activity (own scans).
- **Sidebar:** My Tasks, Scan. That's it.
- **Special:** Mobile-first, minimal UI. Consider "Material Staging" status before "In Progress" so laborer contributes to tracking without touching fabrication workflow.

#### Field Crew
- **Sees:** Shop drawings and plans (all PDFs), shipping manifest/packing list, project progress (percentage), delivery status. No financial data (but can submit expenses).
- **Can do:** View/download shop drawings (offline capable), submit Field Daily Reports, complete Field Hazard Analysis (JHA), upload photos (tagged to project/date/category), track rented equipment (name, company, rate, dates), upload receipt photos and fill expense reports, create punch list items. Cannot: see costs, interact with shop floor, modify work orders.
- **Dashboard cards:** Active Project selector, Project Documents, Daily Actions (3 buttons: Daily Report, Hazard Analysis, Upload Photos), Equipment & Expenses, Deliveries.
- **Sidebar:** My Projects, Documents, Daily Reports, Hazard Analysis, Photos, Equipment, Expenses, Punch List.
- **Special:** Mobile-first. Offline capability for drawings and report submission (sync when connected). Field Daily Report includes: date, crew present (names + hours), weather, work completed, issues/delays, photo attachments. JHA includes: job tasks, hazards per task, controls, PPE required, crew sign-off.

#### Safety Officer
- **Sees:** All Field Hazard Analyses across all projects, incident/near-miss reports, safety training records, equipment inspection logs. No financial data.
- **Can do:** Review JHAs, file incident reports, track safety metrics, flag stop-work conditions (alerts PM and God Mode), manage safety program documentation. Cannot: modify projects, interact with fabrication or shipping.
- **Dashboard cards:** Open JHAs (across all projects), Incident Log, Safety Metrics, Stop-Work Alerts.
- **Sidebar:** JHA Review, Incidents, Safety Metrics, Training Records, Equipment Inspections.

#### Customer (External Portal — Future)
- **Sees:** Their project(s) only. Project status (progress bar), estimated dates, curated field photos (PM-approved), quote/invoice documents. No internal data whatsoever.
- **Can do:** View project status, download their documents, view shared photos. Cannot: see costs, shop operations, other customers, or any internal data.
- **Dashboard cards:** My Project Status, Upcoming Dates, Recent Photos, Documents.
- **Sidebar:** Project Status, Photos, Documents.

---

## 3. Page Access Matrix

Legend: **F** = Full access, **R** = Read-only, **E** = Edit, **-** = No access, **$** = With financial data, **!$** = Without financial data

| Page | God | Admin | PM | Est | Sales | Purch | Inv | Acct | Foreman | QC | Eng | RollOp | Weld | Ship | Labor | Field | Safety | Cust |
|------|-----|-------|----|-----|-------|-------|-----|------|---------|----|-----|--------|------|------|-------|-------|--------|------|
| Dashboard | F$ | F$ | F$ | F$ | F | F$ | F!$ | F$ | F!$ | F!$ | F!$ | F!$ | F!$ | F!$ | F!$ | F!$ | F!$ | F!$ |
| User Management | F | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - |
| System Settings | F | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - |
| SA Calculator | F$ | F$ | F$ | F$ | - | - | - | - | - | - | R!$ | - | - | - | - | - | - | - |
| Project List | F$ | F$ | F$ | F$ | R | - | - | F$ | F!$ | R!$ | R!$ | - | - | R!$ | - | R!$ | - | R!$ |
| Shop Drawings | F | F | F | - | - | - | - | - | F | F | E | - | R | - | - | R | - | - |
| Work Orders | F | F | F | - | - | - | - | - | E | R | - | R* | R* | R | R* | - | - | - |
| Work Station | F | F | F | - | - | - | - | - | F | R | - | F* | F* | - | R* | - | - | - |
| QC / Inspection | F | F | R | - | - | - | - | - | R | F | R | - | - | - | - | - | - | - |
| AISC Library | F | F | R | - | - | - | - | - | - | F | F | - | - | - | - | - | - | - |
| Inventory | F$ | F$ | R$ | R!$ | - | R$ | F!$ | R$ | - | - | - | - | - | - | - | - | - | - |
| Purchase Orders | F$ | F$ | R$ | - | - | F$ | R!$ | R$ | - | - | - | - | - | - | - | - | - | - |
| Shipping / BOL | F | F | F | - | - | - | - | - | R | - | - | - | - | F | - | - | - | - |
| Field Reports | F | F | F | - | - | - | - | - | - | - | - | - | - | - | - | F | R | - |
| Hazard Analysis | F | F | F | - | - | - | - | - | - | - | - | - | - | - | - | F | F | - |
| Photos | F | F | F | - | - | - | - | - | - | R | - | - | - | - | - | F | R | R** |
| Equipment Track | F | F | F | - | - | - | - | R$ | - | - | - | - | - | - | - | F | - | - |
| Expense Reports | F | F | F | - | - | - | - | F$ | - | - | - | - | - | - | - | F | - | - |
| Punch List | F | F | F | - | - | - | - | - | R | R | - | - | - | - | - | F | - | - |
| Financial Reports | F | F | F | - | - | - | - | F | - | - | - | - | - | - | - | - | - | - |
| Sales Pipeline | F | F | R | - | F | - | - | - | - | - | - | - | - | - | - | - | - | - |
| Audit Log | F | R | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - |
| Consumable Receipts | F | F | R | - | - | - | - | F$ | F*** | - | - | - | - | - | - | - | - | - |

*R\* = filtered to assigned items only*
*F\* = filtered to assigned machine/items only*
*R\*\* = PM-curated photos only*
*F\*\*\* = Submit own receipts, see own history, no project totals*

---

## 4. Project Lifecycle & Handoff Chain

### Standard Flow

```
1. ESTIMATOR      → Calculates BOM, generates quote, saves project
2. SALES (opt)    → Manages customer relationship, follows up on quote
3. PM / ADMIN     → Customer signs → approves project to proceed
4. PURCHASING     → Creates POs for materials not in stock
5. INVENTORY MGR  → Receives material, scans in, links mill certs, allocates to project
6. SHOP FOREMAN   → Creates work order, assigns items to machines/operators, sets schedule
7. ROLL FORM OP   → Runs purlins, panels, sag rods, plates, straps, endcaps
8. WELDER         → Fabricates columns & rafters (cap plates, gussets, rebar)
9. LABORER        → Stages material, moves pieces between stations
10. QA/QC         → Inspects each completed piece, signs off or rejects
11. SHOP FOREMAN  → Monitors progress, adjusts workflows as needed
12. SHIPPING COORD → Builds loads from completed items, generates BOL, marks shipped
13. FIELD CREW    → Receives shipment, verifies manifest, installs
14. FIELD CREW    → Daily reports, photos, JHA, equipment tracking, expenses
15. SAFETY (opt)  → Reviews JHAs, tracks safety metrics
16. QA/QC (opt)   → Final field inspection if applicable
17. PM / ADMIN    → Project closeout, final review
18. ACCOUNTING    → Final P&L, invoice, expense processing
```

### Work Order Item Lifecycle

```
Queued → Approved → Stickers Printed → Staged (Laborer) → In Progress (Operator/Welder)
→ Fabricated → QC Pending → QC Approved (or Rejected → back to operator)
→ Ready to Ship → Shipped → Delivered → Installed
```

### Key Handoff Points

- **Estimator → PM:** Quote signed by customer. PM takes ownership of project execution.
- **PM → Shop Foreman:** Project approved for fabrication. Foreman receives notification.
- **Inventory → Shop Floor:** Material allocated and received. Foreman can see stock is available.
- **Shop Floor → QC:** Item marked "Fabricated." QC receives inspection notification.
- **QC → Shipping:** Item marked "QC Approved." Shipping coordinator sees it in Ready to Ship.
- **Shipping → Field:** Load dispatched. Field crew sees delivery notification with manifest.
- **Field → PM:** Daily reports and punch list items visible to PM for tracking.

---

## 5. Structural Calculation Rules

### Frame Type Auto-Determination

- Building width <= 45' → TEE frame (1 column per rafter in auto mode)
- Building width > 45' → Multi-column frame (2+ columns per rafter)
- Frame type is never a user input — it is derived from width

### Column Placement (on Rafter)

Three modes, set per building:

- **Auto:** width <= 45' → 1 column at rafter center (L/2). Width > 45' → max(2, ceil(width/60)) columns at quarter-points.
- **Spacing:** Columns evenly placed at user-specified spacing, centered on rafter.
- **Manual:** User specifies count and optional explicit positions (feet from left end).

Back wall mode overrides: rear column at 19" from right end, configurable front column position.

All modes enforce P3 constraint: column center >= 13" from rafter ends.

### Column Height Formula

```
height = clear_height + (distance_from_eave * tan(pitch)) + embedment + buffer
```

Each column position has a different height because distance from eave varies. The BOM uses the sum of all per-position heights for coil footage, not a single average.

### Rafter Layout (Along Building Length)

- Number of bays = floor(length / max_bay)
- Number of frames (rafters) = bays + 1
- Overhang at each end = (length - bays * max_bay) / 2

Space-based mode: parking stall width drives module. Bays hold up to 3 stalls. Short bays placed at center. 1-space overhang option cantilevering roof past end columns.

### Rafter Slope Length

```
half_width = width / 2
rise = half_width * tan(pitch)
slope_length = 2 * sqrt(half_width^2 + rise^2)
```

### Purlin Spacing

User input directly (no auto-calc). Default guidance:
- Bay <= 30' → 5' OC
- Bay 30'-34'4" → 4' OC
- Bay 34'5"-40' → 3.5' OC

### Footing Depth

Per-building input, default 10'. Not project-level.

### Rebar Auto-Selection

Based on frame type, building width, wind speed, and bay size. User can override with manual size (#5 through #11).

---

## 6. BOM Rules

### 7 Coil Types

1. **23" 10GA C-Section** — Columns & Rafters (two C-sections per box beam). $0.82/lb, 10.83 lbs/LFT, 5,000 lb rolls.
2. **20.125" 12GA Z-Purlin** — Roof purlins, wall girts, endcap U-channels. $0.82/lb, 7.43 lbs/LFT, 5,000 lb rolls.
3. **4" 16GA Angle** — Sag rods (2"x2"). $0.86/lb, 0.8656 lbs/LFT, 4,000 lb rolls.
4. **48" 29GA Spartan Rib** — Roof and wall panels. $0.795/lb, 2.81 lbs/LFT, 7,500 lb rolls. 35.79" coverage width.
5. **6" 10GA Plate** — Interior purlin-to-rafter plates (10"x6", 8 holes). $0.82/lb, 2.83 lbs/LFT, 3,000 lb rolls.
6. **9" 10GA Plate** — Exterior/eave purlin plates (24"x9", 8 holes). $0.82/lb, 4.24 lbs/LFT, 3,000 lb rolls.
7. **1.5" 10GA Strap** — Hurricane straps & sag braces (1.5"x28"). $0.82/lb, 0.706 lbs/LFT, 3,000 lb rolls.

### Waste Factors

- 10GA: 3%
- 12GA: 3%
- 16GA: 2%
- 29GA: 5%
- Rebar: 5%

### Purchased Items

- Cap plates: 3/4"x26"x14" A572 Gr 50, $95 each, 2 per column
- Gusset triangles: 6"x6"x3/8" A572, $13 each, 4 per column (2 sizes based on slope)
- Bolt assemblies: 3/4" A325 (bolt+nut+washers), $3.75 each, 4 per column connection

### Consumables

Adjustable rate, default $300 per 5,000 sqft of building footprint. Covers welding wire/rod, welding gas, cold galvanized paint.

### Labor

Adjustable daily rate, default $960/day (4 crew x $30/hr x 8 hrs) + 10% overhead = $1,056 effective.
- Box pieces (columns/rafters): 5 per day
- Purlin rolls: 5 per day (5,000 lb rolls)
- Panel rolls: 3 per day (7,500 lb rolls)
- Angle rolls: 2 per day (4,000 lb rolls)

Total days = max(column+rafter days, purlin days, panel days, angle days).

### Concrete

NOT included in SA BOM. Stored in geometry for Titan Carports Construction Quote Calculator import only. Footing diameter: 24" (fixed). Volume: pi * r^2 * depth / 27 (cubic yards).

### Markup

Default 35%, adjustable per project. Applied to both materials and labor on customer quote.

---

## 7. Fabrication Standards

### Machines

- **C1** — Variable C-Purlin Roll Former (6"x2" to 16"x4", lip or no-lip U-purlin)
- **C2** — Dedicated 14"x4" Roll Former (column and rafter CEE sections)
- **Z1** — Z-Purlin Roll Former (12"x3.5" Z-purlins with 45-degree lip)
- **P1** — Plate Former (purlin clips P1/P2, hurricane straps)
- **ANGLE** — Angle Machine (2"x2" sag rods)
- **SPARTAN** — Spartan Rib Roll Former (roof and wall panels)
- **WELDING** — Welding Bay (column/rafter assembly)
- **REBAR** — Rebar Station (cut-to-length)
- **CLEANING** — Cleaning Station (weld cleaning, cold galvanizing)

### WPS Codes

- **B** — Stitch welds (CEE-to-CEE body): 5/16, 3-36 pattern
- **C** — Clip-to-rafter welds
- **D** — Rebar attachment welds
- **F** — Column/rafter end welds

### Sticker System

- Printer: Zebra ZT411, 203 DPI
- Label: 4"x6", wax resin thermal transfer, weather resistant
- Fields: ship mark, job number, project name, quantity, total weight, machine assignment, date fabricated, drawing reference, QR code
- QR destination: TitanForge project context (opens full project)

### Sticker Grouping

- Columns: 1 per assembly
- Rafters: 1 per assembly
- Purlins: 1 per group (by building)
- Sag rods: 1 per 10
- Hurricane straps: 1 per 10
- P1 clips: 1 per batch
- Roofing/wall panels: 1 per stack (max 2,000 lbs or 50 sheets)
- Endcaps: 1 per group (same size per building)
- Splice plates: 1 per pair

### Panel Stacking

- Max weight: 2,000 lbs per stack
- Max sheets: 50 per stack
- Below 10 sheets: mixed lengths OK

### Shipping Order (Fixed)

1. Columns
2. Rafters
3. Purlins
4. Sag Rods / Hurricane Straps
5. Decking / Roofing
6. Trim

### Standard Drawing Notes

- Material: A36 UNO
- Paint: Cold Galv All Plain Steel & Welds
- Holes: 15/16" UNO
- Tolerance: +/- 1/16"
- Design review disclaimer included on all drawings

---

## 8. Inventory System Rules

### Tracked Items

- 7 coil types (by linear feet and weight remaining per roll)
- Rebar by size (#5 through #11, count of 40' sticks)
- Cap plates (count)
- Gusset triangles (count)
- Bolt assemblies (count/boxes)
- Fastener boxes (TEK neoprene, TEK structural, endcap TEK, splice TEK, sag rod TEK, stitch)

### Coil Identity

Each coil roll tracked individually: coil type, heat number, weight at receiving, weight remaining (decremented by fabrication), mill cert attachment, vendor/PO reference.

### Allocation

When a project BOM is calculated, the system shows what's in stock vs. what needs ordering. Inventory or PM can allocate specific stock to a project. Fabrication consumption decrements allocated inventory.

### Reorder Alerts

Configurable thresholds per item type. When stock drops below threshold, alert appears on Inventory Manager and Purchasing dashboards.

---

## 9. QA/QC System Rules

### Inspection Flow

Item marked "Fabricated" → appears in QC Inspection Queue → Inspector checks against shop drawing and checklist → Sign off (digital) or Reject with notes.

### Non-Conformance Reports (NCR)

Rejection creates formal NCR: issue description, root cause, corrective action required, responsible party, re-inspection requirement. NCR tracks through resolution.

### Traceability Chain

Full chain for any piece: coil roll (heat number, mill cert) → fabrication (who, when, machine) → QC inspection (who, when, pass/fail) → project assignment → shipping (load, BOL).

### AISC Document Library

Centralized repository: WPS/PQR documents, mill certs, welder certifications, calibration records, inspection procedures, code references. Managed by QA/QC or God Mode.

---

## 10. Field Operations Rules

### Field Daily Report (Required Daily)

- Date, project, weather conditions
- Crew present: names and hours worked
- Work completed (checklist + free text)
- Issues/delays
- Photo attachments (built-in, not separate upload)

### Field Hazard Analysis / JHA (Required Before Work Starts)

- Job tasks identified
- Hazards per task
- Controls in place
- PPE required
- Crew sign-off (each person)
- Must be completed before work begins each day or when conditions change

### Photo Management

- Tagged to: project, date, category (progress, delivery, issue, safety)
- Optional description/notes
- PM can mark photos as "share with customer" for external portal

### Equipment Tracking

- Name, rental company, daily/weekly rate, date on rent, date off rent
- Running cost total per item and per project
- Feeds into project cost tracking for Accounting

### Expense Reports

- Receipt photo upload (required)
- Amount, category (fuel, materials, meals, tools, other), date, notes
- Submitted by Field Crew
- Approved by PM
- Processed by Accounting

### Punch List

- Created by Field Crew
- Description, photo, severity (critical/minor), status (open/in-progress/resolved)
- Notifications to PM and Shop Foreman
- Tracked through resolution

---

## 11. Technical Architecture

### Stack

- **Backend:** Python 3.8+ / Tornado web framework
- **Auth:** bcrypt password hashing, cookie-based sessions
- **Data:** JSON file storage (per-user, per-project directories)
- **Frontend:** Server-rendered HTML/JS templates with shared layout system
- **Exports:** ReportLab (PDF), OpenPyXL (Excel), ZPL (Zebra labels)
- **Deployment:** Railway (railway.json) or local (localhost:8888)

### File Structure

```
app.py                  — Tornado server, route registration
tf_handlers.py          — All route handlers (with permission middleware)
calc/
  bom.py                — BOM calculation engine
  defaults.py           — Material specs, pricing, defaults
shop_drawings/
  config.py             — Fabrication defaults, machine defs, drawing specs
  *.py                  — Drawing generation modules
templates/
  shared_nav.py         — Dynamic sidebar (role-aware)
  shared_styles.py      — Common CSS
  *.py                  — Page templates (content only, inherits layout)
outputs/
  *.py                  — PDF, Excel, ZPL export generators
data/
  users/                — User JSON files (one per user)
  roles.json            — Role definitions and permissions
  projects/             — Project data directories
  shop_drawings/        — Shop drawing configs and work orders
  inventory/            — Inventory records
  qc/                   — QA/QC records
  field/                — Field reports, JHAs, photos, expenses
  audit/                — Audit log entries
static/
  *.svg                 — Logos and static assets
```

### User Data Model

```json
{
  "user_id": "usr_abc123",
  "username": "brad",
  "display_name": "Brad Johnson",
  "email": "brad@structuresamerica.com",
  "password_hash": "$2b$12$...",
  "roles": ["shop_foreman", "qc_inspector"],
  "active": true,
  "created_at": "2026-01-15T08:00:00Z",
  "last_login": "2026-04-14T07:30:00Z",
  "force_password_change": false
}
```

### Permission Check Pattern

```python
# In handler:
if not self.current_user.can("view_shop_drawings"):
    return self.redirect("/dashboard")

# In template:
if user.can("view_financials"):
    render_cost_column()

# In API:
@require_permission("manage_work_orders")
def post(self):
    ...
```

---

## 12. UI/UX Rules

### Dashboard Card System

Each role contributes cards. Cards are modular components with:
- Title
- Summary stat or count
- Action button (optional)
- "See all" link to full page

Cards are assembled by the dashboard page based on user's role set. Grouped by function (Shop Floor, Quality, Inventory, Field, etc.). Group headers only shown if user has cards in that group.

### Sidebar Sections

Sections appear/disappear based on roles. Standard section order:
1. Dashboard (always)
2. Estimating (Calculator, Quotes)
3. Projects
4. Shop Floor (Work Orders, Workflows, Machines, Crew)
5. Quality (Inspections, NCRs, AISC, Traceability)
6. Inventory (Stock, Receiving, Allocations)
7. Purchasing (POs, Vendors)
8. Shipping (Loads, BOL)
9. Field (Reports, JHA, Photos, Equipment, Expenses)
10. Safety (JHA Review, Incidents)
11. Financial (Reports, P&L, Invoices)
12. Sales (Pipeline, Leads)
13. Administration (Users, Settings, Audit — God Mode only)

### Mobile-First Roles

These roles are primarily used on phones/tablets and must be optimized for touch:
- Laborer
- Field Crew
- Roll Forming Operator
- Welder
- Shipping Coordinator
- QA/QC Inspector (on the floor)

### Toast Notifications

All user actions confirmed with toast notifications (3-second auto-dismiss). No native alert() dialogs anywhere in the system.

### Global Click Delegation

All onclick handlers use event delegation on the document body to prevent click-blocking from overlays or z-index issues.

---

## 13. Authentication & Security

### Password Rules

- bcrypt hashed (cost factor 12)
- First login: forced password change from temporary password
- Failed login lockout: 5 attempts, 15-minute lockout
- Passwords never stored in plaintext, never logged

### Session Management

- Cookie-based sessions (Tornado secure cookies)
- Session timeout: 8 hours (configurable)
- Single session per user (new login invalidates old session)

### Audit Logging

Every significant action logged:
- User created/deactivated/role changed
- Project saved/deleted
- Work order created/approved
- QC sign-off/rejection
- Item Start/Finish
- Inventory received/allocated
- File uploaded/deleted
- Login/logout/failed login

Log entry: timestamp, user_id, action, target (project/item/user), details, IP address.

---

## 14. Data & API Conventions

### API Endpoints

All API routes follow the pattern: `/api/{resource}/{action}`

Handlers accept both JSON and form-encoded POST data (try JSON first, fall back to form-encoded). Responses are always JSON.

### Date Format

ISO 8601 everywhere: `2026-04-14T12:30:00Z`

### ID Format

- Users: `usr_{random}`
- Projects: user-defined job code (e.g., `BVR-2026`)
- Work orders: `WO-{job_code}-{rev}-{hex}`
- Items: `WO-{job_code}-{hex}-{mark}` (e.g., `WO-BVR-2026-A1B2C3-C1`)
- Loads: `LD-{job_code}-{seq}` (e.g., `LD-BVR-2026-01`)

### Error Handling

- 401: Not authenticated → redirect to login
- 403: Not authorized → redirect to dashboard (user never sees 403 page)
- 404: Not found → friendly "page not found" with nav back to dashboard
- 500: Server error → logged, user sees "something went wrong" with support contact

---

## 15. Contacts

### Structures America

- Haley McClendon — (832) 791-8965 — haley@structuresamerica.com
- Shop: 14369 FM 1314, Conroe, TX 77302

### Titan Carports

- Zack — zack@titancarports.com

---

## 16. Companion Reference Documents

This file covers **system architecture, RBAC, permissions, UI/UX rules, and operational workflows.** For deep fabrication specs and interactive drawing architecture, see these companion documents in the same directory:

| Document | Purpose |
|----------|---------|
| `TitanForge_Master_Rules.md` | **Fabrication Bible** — Column specs (profiles, gauge, spacing, height formulas, cap plates, gussets, rebar), rafter specs (CEE anatomy, box beam assembly, stitch welds, P1/P2/P3 plates, splice plates, rebar placement), purlin specs (Z vs C, spacing rules, overhang/splice, facing direction, endcaps), roofing, sag rods, hurricane straps, welding standards (WPS codes, wire specs, sequences), and full QA/QC inspection criteria. |
| `RAFTER_SESSION_STATE.md` | **Rafter Drawing Architecture** — JavaScript state variables, input controls, `calc()` return object structure, SVG drawing zone layout (Elevation, Plan Views, Details, BOM Table, Title Block), function catalog, and 3D viewer specs for the interactive rafter shop drawing HTML. |

**Rule of thumb:** If you need to know *how the app works* or *who can do what*, read this file. If you need to know *how to build the steel*, read `TitanForge_Master_Rules.md`. If you need to know *how the rafter drawing code works*, read `RAFTER_SESSION_STATE.md`.
