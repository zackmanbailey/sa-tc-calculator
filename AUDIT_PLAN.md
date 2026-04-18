# TitanForge v5.0 — Comprehensive Audit Plan

**Prepared:** April 17, 2026  
**Target:** calc.titancarports.com (live Railway deployment)  
**Scope:** Every page, API endpoint, button, role boundary, and business rule  
**Source Documents:** RULES.md (§1–§16), TitanForge_Master_Rules.md, auth/roles.py, auth/permissions.py

---

## Audit Philosophy

This plan is organized into 8 phases, each with specific test cases. Every test case has a PASS/FAIL outcome. The audit tests the live site at calc.titancarports.com using the Chrome browser MCP tools, hitting real pages and real API endpoints. Where code-only verification is needed (e.g., checking handler logic), the source code is referenced directly.

**Previous audit findings incorporated:** Reports "undefined" values (fixed), QA Hub em-dash encoding (fixed), sidebar `/profile` 404 (fixed), empty states on Field Ops/Job Costing/QC Dashboard (fixed), Shipping Hub title bug (fixed), WO card "no items" count (fixed).

---

## Phase 1: Authentication & Session Management

**Reference:** RULES.md §13

### 1.1 Login Flow
- [ ] Navigate to `/auth/login` — page loads with no errors
- [ ] Submit valid credentials — redirects to dashboard `/`
- [ ] Submit invalid credentials — shows error message, no redirect
- [ ] Submit 5+ invalid attempts — lockout behavior (15-minute lockout per RULES.md)
- [ ] Verify secure cookie is set after login (check cookie attributes)
- [ ] Session timeout behavior after 8 hours (verify config exists)

### 1.2 Logout
- [ ] Click logout — session destroyed, redirects to login
- [ ] After logout, accessing any protected page redirects to `/auth/login`
- [ ] Back button after logout does NOT re-enter the app

### 1.3 User Management (God Mode only)
- [ ] `/admin` page loads for God Mode user
- [ ] User list displays all users with roles
- [ ] Create new user — all required fields enforced
- [ ] Edit user — roles can be assigned/removed
- [ ] Deactivate user — user can no longer log in
- [ ] Non-God-Mode users are redirected away from `/admin` (not shown 403)
- [ ] Verify force_password_change flag works on first login

---

## Phase 2: Navigation & Layout System

**Reference:** RULES.md §12, shared_nav.py, inject_nav()

### 2.1 Sidebar Navigation
- [ ] Sidebar renders on every authenticated page
- [ ] All sidebar links are clickable and navigate to correct pages
- [ ] No broken links (no 404s from any sidebar item)
- [ ] Sidebar footer user avatar links to `/admin` (not `/profile`)
- [ ] Sidebar collapses/expands correctly on mobile widths
- [ ] Active page is highlighted in sidebar
- [ ] Sidebar sections appear/disappear correctly based on role (see §2.3 below)

### 2.2 Sidebar Section Verification (per RULES.md §12)
Test that each section appears ONLY for roles that should see it:

| Section | Should appear for | Should NOT appear for |
|---------|-------------------|----------------------|
| Dashboard | All roles | — |
| Estimating | God, Admin, PM, Estimator | Sales, Purchasing, Laborer, Field Crew |
| Projects | God, Admin, PM, Estimator, Sales, Foreman, QC, Engineer, Shipping, Field | Roll Op, Welder, Laborer |
| Shop Floor | God, Admin, PM, Foreman | Estimator, Sales, Accounting, Laborer |
| My Station | Roll Op, Welder, Laborer | Estimator, Sales, Accounting |
| Quality | God, Admin, PM, QC, Engineer | Sales, Purchasing, Laborer |
| Inventory | God, Admin, PM, Estimator, Purchasing, Inv Manager, Accounting | Welder, Laborer, Field Crew |
| Customers | God, Admin, PM, Sales | Laborer, Roll Op, Welder |
| Shipping | God, Admin, PM, Shipping, Foreman | Estimator, Sales, Laborer |
| Field | God, Admin, PM, Field Crew, Safety | Estimator, Sales, Laborer |
| Financial | God, Admin, PM, Accounting | Estimator, Sales, Foreman, Laborer |
| Admin | God Mode only | All other roles |

### 2.3 Layout Integrity
- [ ] `render_with_nav()` sets `Content-Type: text/html; charset=utf-8` (encoding fix verified)
- [ ] Old topbar elements are hidden via CSS (`#topbar`, `.topbar`, `.tf-topbar`, `.navbar`, `.ws-topbar`)
- [ ] Page content wrapped in `<div class="tf-main">`
- [ ] No double scrollbars on any page
- [ ] No content hidden behind sidebar on any page

---

## Phase 3: Dashboard & Core Pages

**Reference:** RULES.md §12 (Dashboard Card System)

### 3.1 Dashboard (`/`)
- [ ] Page loads with no JS errors
- [ ] `/api/dashboard/stats` returns valid JSON with project counts, WO stats, QC items, inventory alerts, recent activity
- [ ] Animated counters display correct numbers (cross-check with actual data)
- [ ] Business Overview section shows correct totals
- [ ] Recent Activity feed loads and displays entries
- [ ] System Health section renders
- [ ] Quick Links all navigate to correct pages
- [ ] Role-dynamic sections show/hide based on `data-user-role` attribute

### 3.2 Getting Started (`/getting-started`)
- [ ] Page loads correctly
- [ ] All steps/instructions render

### 3.3 Activity Feed (`/activity`)
- [ ] Page loads, API `/api/activity` returns data
- [ ] Activity entries show correct timestamps, actions, users
- [ ] Filter controls work (if present)

### 3.4 Global Search (`/api/search`)
- [ ] Search returns results for projects, customers, work orders
- [ ] Empty search handled gracefully
- [ ] Special characters don't cause errors

---

## Phase 4: Estimating & Project Lifecycle

**Reference:** RULES.md §4 (Project Lifecycle), §5 (Structural Calculation Rules), §6 (BOM Rules)

### 4.1 SA Calculator (`/sa`)
- [ ] Page loads with all input fields
- [ ] Calculate button triggers `/api/calculate` and returns valid BOM
- [ ] Frame type auto-determination: width ≤45' → TEE, width >45' → multi-column
- [ ] Column placement modes: Auto, Spacing, Manual — all produce valid results
- [ ] P3 constraint enforced: column center ≥13" from rafter ends
- [ ] Column height formula produces correct per-position heights
- [ ] Rafter slope length calculation: `2 * sqrt(half_width² + rise²)`
- [ ] Purlin spacing accepts user input
- [ ] Footing depth is per-building, defaults to 10'
- [ ] Rebar auto-selection based on frame type, width, wind speed, bay size
- [ ] BOM shows all 7 coil types with correct waste factors (10GA/12GA: 3%, 16GA: 2%, 29GA: 5%, rebar: 5%)
- [ ] Purchased items calculated correctly: cap plates (2/column), gussets (4/column), bolts (4/column connection)
- [ ] Consumables default: $300 per 5,000 sqft
- [ ] Labor calculation: daily rate × days based on max(box days, purlin days, panel days, angle days)
- [ ] Markup default 35%, adjustable
- [ ] PDF export via `/api/pdf` — downloads valid PDF
- [ ] Excel export via `/api/excel` — downloads valid XLSX
- [ ] Save project via `/api/project/save` — saves current.json + version history

### 4.2 TC Quote Calculator (`/tc`)
- [ ] Page loads
- [ ] Depends on SA data — blocks access if SA not linked (modal offers to open SA)
- [ ] Save via `/api/tc/save` — versioned saves
- [ ] Load via `/api/tc/load`
- [ ] PDF export via `/tc/export/pdf`
- [ ] Excel export via `/tc/export/excel`

### 4.3 Quote Editor (`/quote/{job_code}`)
- [ ] Page loads for valid job code
- [ ] Quote data from `/api/quote/data` populates correctly
- [ ] Quote PDF generation via `/api/quote/pdf`
- [ ] BOM price overrides: inline edit, gold highlight (#FFF8E0), ⬥ marker, strikethrough original
- [ ] Clearing override resets to calculated value

### 4.4 Project Management
- [ ] Project list (`/api/projects`) returns all projects
- [ ] Enhanced list (`/api/projects/full`) includes detailed data
- [ ] Create project (`/api/project/create`) — generates next code via `/api/project/next-code`
- [ ] Project page (`/project/{code}`) loads with all sections
- [ ] Project status (`/api/project/status`) — returns correct flags
- [ ] Project metadata (`/api/project/metadata`) — editable
- [ ] Project checklist (`/api/project/checklist`) — functional
- [ ] Project next steps (`/api/project/next-steps`) — generates correctly
- [ ] Estimator status (`project_estimator_status()`) — returns correct linked flags: sa_linked, tc_linked, bom_available, quote_linked, shop_linked, wo_count, qc_linked, docs_linked, jc_linked
- [ ] Project timeline (`/api/project/timeline`) — renders
- [ ] Project assets (`/api/project/assets`) — lists all
- [ ] Delete project (`/api/project/delete`) — cascade deletes all: project dir, shop drawings dir, quote file, QC file (God Mode only)
- [ ] Revisions (`/api/project/revisions`) — shows version history
- [ ] Compare (`/api/project/compare`) — diff between versions

### 4.5 Project Documents
- [ ] Upload document (`/api/project/docs/upload`) — file saved
- [ ] List documents (`/api/project/docs`) — returns all
- [ ] Serve document (`/project-files/{code}/{dir}/{file}`) — file downloads
- [ ] Delete document (`/api/project/docs/delete`) — removes file
- [ ] Archive document (`/api/project/docs/archive`) — moves to archive
- [ ] Archived list (`/api/project/docs/archived`) — returns archived docs
- [ ] Document revision system (`/api/documents/revisions`, `/save`, `/approve`) — full lifecycle

---

## Phase 5: Shop Floor & Fabrication

**Reference:** RULES.md §7 (Fabrication Standards), §4 (Work Order Item Lifecycle)

### 5.1 Shop Drawings (`/shop-drawings/{job_code}`)
- [ ] Shop drawings page loads listing all drawing types
- [ ] Config endpoint (`/api/shop-drawings/config`) returns valid config
- [ ] Each drawing type loads its interactive page:
  - [ ] Column (`/shop-drawings/{code}/column`)
  - [ ] Rafter (`/shop-drawings/{code}/rafter`)
  - [ ] Purlin (`/shop-drawings/{code}/purlin`)
  - [ ] Sag Rod (`/shop-drawings/{code}/sagrod`)
  - [ ] Strap (`/shop-drawings/{code}/strap`)
  - [ ] Endcap (`/shop-drawings/{code}/endcap`)
  - [ ] P1 Clip (`/shop-drawings/{code}/p1clip`)
  - [ ] P2 Plate (`/shop-drawings/{code}/p2plate`)
  - [ ] Splice (`/shop-drawings/{code}/splice`)
- [ ] Generate drawings (`/api/shop-drawings/generate`) works
- [ ] Save interactive PDF (`/api/shop-drawings/save-interactive-pdf`)
- [ ] Delete PDF (`/api/shop-drawings/delete-pdf`)
- [ ] Sync BOM (`/api/shop-drawings/sync-bom`)
- [ ] Diff between versions (`/api/shop-drawings/diff`)
- [ ] Download file (`/api/shop-drawings/file`)
- [ ] Download ZIP of all (`/api/shop-drawings/zip`)

### 5.2 Work Orders
- [ ] Global work orders page (`/work-orders`) loads
- [ ] Project work order page (`/work-orders/{code}`) loads
- [ ] Create work order (`/api/work-orders/create`) — generates WO-{code}-{rev}-{hex} ID
- [ ] List work orders (`/api/work-orders/list`, `/api/work-orders/all`) — return data
- [ ] Detail (`/api/work-orders/detail`) — shows all items with statuses
- [ ] Edit work order (`/api/work-orders/edit`)
- [ ] Delete work order (`/api/work-orders/delete`) — permission checked
- [ ] Approve work order (`/api/work-orders/approve`)
- [ ] Mark stickers printed (`/api/work-orders/stickers-printed`)
- [ ] Hold/unhold (`/api/work-orders/hold`)

### 5.3 Work Order Item Lifecycle (12-state machine)
Test the full lifecycle transition: `Queued → Approved → Stickers Printed → Staged → In Progress → Fabricated → QC Pending → QC Approved → Ready to Ship → Shipped → Delivered → Installed`

- [ ] QR scan start/finish (`/api/work-orders/qr-scan`) — transitions item state
- [ ] Batch scan (`/api/work-orders/batch-scan`) — multiple items at once
- [ ] Item notes (`/api/work-orders/item-notes`) — add/view notes
- [ ] Item edit (`/api/work-orders/item-edit`) — edit item details
- [ ] Item checklist (`/api/work-orders/checklist`) — fab step checklist
- [ ] Mobile scan page (`/wo/{code}/{item}`) — loads on mobile
- [ ] QR scanner page (`/scan/{code}`) — camera/scan UI loads
- [ ] Item detail (`/api/work-orders/item-detail`) — returns full item data
- [ ] Verify invalid state transitions are blocked (e.g., can't go from Queued → Fabricated)

### 5.4 Sticker System
**Reference:** RULES.md §7 (Sticker System)

- [ ] Sticker PDF (`/api/work-orders/stickers/pdf`) — generates 4×6 B&W labels
- [ ] Sticker ZPL (`/api/work-orders/stickers/zpl`) — Zebra native format
- [ ] Sticker CSV (`/api/work-orders/stickers/csv`) — NiceLabel/BarTender format with drawing_qr_url
- [ ] Single sticker (`/api/work-orders/stickers/single`)
- [ ] Fab stickers (assembly/material variants for PDF, ZPL, NLBL, CSV):
  - [ ] `/api/work-orders/fab-stickers/assembly-pdf`
  - [ ] `/api/work-orders/fab-stickers/assembly-zpl`
  - [ ] `/api/work-orders/fab-stickers/material-master-pdf`
  - [ ] `/api/work-orders/fab-stickers/material-master-zpl`
  - [ ] `/api/work-orders/fab-stickers/material-sub-pdf`
  - [ ] `/api/work-orders/fab-stickers/material-sub-zpl`
  - [ ] `/api/work-orders/fab-stickers/nlbl/assembly`
  - [ ] `/api/work-orders/fab-stickers/nlbl/material`
  - [ ] `/api/work-orders/fab-stickers/csv/assembly`
  - [ ] `/api/work-orders/fab-stickers/csv/material`
- [ ] Sticker fields verify: ship mark (42pt bold), component type (14pt), dual QR codes (START/FINISH + VIEW SHOP DRAWING), JOB/QTY/MACHINE center column
- [ ] Sticker grouping rules: columns 1/assembly, rafters 1/assembly, purlins 1/group, sag rods 1/10, straps 1/10, panels max 2000 lbs or 50 sheets

### 5.5 Work Order Packet
- [ ] Packet PDF (`/api/work-orders/packet/pdf`) — auto-generated on approval

### 5.6 Shop Floor
- [ ] Shop floor page (`/shop-floor`) loads
- [ ] Shop floor data (`/api/shop-floor/data`) — machine statuses, queues
- [ ] TV dashboard (`/tv-dashboard`) — large-screen display loads

### 5.7 Work Station
- [ ] Work station page (`/work-station/{machine}`) loads per machine
- [ ] Work station data (`/api/work-station/data`)
- [ ] Work station steps (`/api/work-station/steps`, `/steps/override`)
- [ ] My Queue page (`/work-station/mine`) — filtered to assigned items
- [ ] My Queue API (`/api/my-queue`)

### 5.8 Smart Queue & Alerts
- [ ] Smart queue (`/api/smart-queue`) — returns prioritized queue
- [ ] Alerts (`/api/alerts`) — returns system alerts

### 5.9 Gamification
- [ ] Leaderboard (`/api/gamification/leaderboard`)
- [ ] Stats (`/api/gamification/stats`)
- [ ] Targets (`/api/gamification/targets`)
- [ ] Profile (`/api/gamification/profile`)
- [ ] Achievements (`/api/gamification/achievements`)

---

## Phase 6: Quality Assurance & Compliance

**Reference:** RULES.md §9 (QA/QC System Rules)

### 6.1 QC Inspection
- [ ] QC page (`/qc/{job_code}`) loads
- [ ] QC data (`/api/qc/data`) returns inspections for project
- [ ] Inspection types (`/api/qc/types`) — returns all component types with required inspections
- [ ] Create inspection (`/api/qc/inspection/create`)
- [ ] Update inspection (`/api/qc/inspection/update`) — sign-off or reject
- [ ] Item inspect alias (`/api/qc/item-inspect`) — hold point UI
- [ ] QC photo upload (`/api/work-orders/qc-photo`) — attaches to inspection
- [ ] QC photo serve (`/api/work-orders/qc-photo/file`)
- [ ] Inspection requirements (`/api/qc/inspection-requirements`)
- [ ] Inspection reports list (`/api/qc/inspection-reports`)
- [ ] Inspection report PDF (`/api/qc/inspection-report/pdf`)
- [ ] Inspection packet PDF (`/api/qc/inspection-packet/pdf`)
- [ ] Report serve (`/qc-reports/{code}/{file}`)

### 6.2 NCR (Non-Conformance Reports)
- [ ] NCR create (`/api/qc/ncr/create`) — description, root cause, corrective action, responsible party
- [ ] NCR update (`/api/qc/ncr/update`) — track through resolution
- [ ] NCR log page (`/qa/ncr-log`) loads
- [ ] NCR log API (`/api/qa/ncr-log`)

### 6.3 QA Hub (`/qa`)
- [ ] QA Hub page loads with no encoding issues (charset fix verified)
- [ ] QA stats (`/api/qa/stats`)
- [ ] WPS page (`/qa/wps`) + API (`/api/qa/wps`)
- [ ] Welder certs page (`/qa/welder-certs`) + API (`/api/qa/welder-certs`)
- [ ] Procedures page (`/qa/procedures`) + API (`/api/qa/procedures`)
- [ ] Calibration page (`/qa/calibration`) + API (`/api/qa/calibration`)
- [ ] Inspector registry page (`/qa/inspector-registry`) + API (`/api/qa/inspector-registry`)
- [ ] Inspector validate (`/api/qa/inspector-validate`)
- [ ] PQR page (`/qa/pqr`) + API (`/api/qa/pqr`)
- [ ] Audit package export (`/api/qa/audit-package`) — AISC compliance bundle

### 6.4 QC Dashboard
- [ ] QC dashboard page (`/qc-dashboard`) loads
- [ ] QC dashboard API (`/api/qc/dashboard`)

### 6.5 QC Photos
- [ ] Photo upload (`/api/qc/photos/upload`)
- [ ] Photo list (`/api/qc/photos`)
- [ ] Photo delete (`/api/qc/photos/delete`)
- [ ] Photo serve (`/qc-photos/{code}/{dir}/{file}`)

### 6.6 Traceability
- [ ] Traceability page (`/inventory/traceability`) loads
- [ ] Traceability index (`/api/traceability`)
- [ ] Register piece (`/api/traceability/register`) — coil roll → fabrication → QC → project → shipping
- [ ] Assign piece (`/api/traceability/assign`)
- [ ] Traceability report (`/api/traceability/report`)

---

## Phase 7: Inventory, Shipping, Customers & Field

### 7.1 Inventory (`/inventory`)
**Reference:** RULES.md §8 (Inventory System Rules)

- [ ] Inventory page loads
- [ ] Inventory API (`/api/inventory`) returns all tracked items
- [ ] Coils list (`/api/inventory/coils`) — individual coil roll data
- [ ] Coil create (`/api/inventory/coil/create`)
- [ ] Coil edit (`/api/inventory/coil/edit`) — string/numeric fields, status validation
- [ ] Coil delete (`/api/inventory/delete`) — blocks if committed > 0
- [ ] Coil detail page (`/coil/{id}`) loads
- [ ] Coil sticker (`/api/inventory/sticker`)
- [ ] Inventory update (`/api/inventory/update`)
- [ ] Inventory save (`/api/inventory/save`)
- [ ] Cert upload (`/api/inventory/cert/upload`)
- [ ] Cert serve (`/certs/{filename}`)
- [ ] Inventory config (`/api/inventory/inv-config`)
- [ ] Inventory summary (`/api/inventory/summary`)
- [ ] Transactions log (`/api/inventory/transactions`)
- [ ] Allocations (`/api/inventory/allocations`)
- [ ] Allocate stock (`/api/inventory/allocate`)
- [ ] Release allocation (`/api/inventory/allocate/release`)
- [ ] Receiving log (`/api/inventory/receiving`)
- [ ] Receive inventory (`/api/inventory/receive`)
- [ ] Alerts (`/api/inventory/alerts`) — low stock reorder alerts
- [ ] Acknowledge alert (`/api/inventory/alerts/acknowledge`)
- [ ] Edit modal: 2-column grid, all fields editable
- [ ] Delete confirmation: safety check blocks if committed > 0

### 7.2 Shipping & Load Builder
- [ ] Shipping hub page (`/shipping`) loads
- [ ] Load builder page (`/load-builder`) loads
- [ ] Load builder list (`/api/load-builder/loads`)
- [ ] Create load (`/api/load-builder/create`)
- [ ] Add item to load (`/api/load-builder/add-item`)
- [ ] Remove item from load (`/api/load-builder/remove-item`)
- [ ] Finalize load (`/api/load-builder/finalize`)
- [ ] Delete load (`/api/load-builder/delete`)
- [ ] Shipping page per project (`/shipping/{code}`)
- [ ] Packing list (`/api/shipping/packing-list`)
- [ ] BOL generation (`/api/shipping/bol`) — auto-populate from load contents
- [ ] Manifest (`/api/shipping/manifest`)
- [ ] Purchase order (`/api/shipping/purchase-order`)
- [ ] Reorder alerts (`/api/shipping/reorder-alerts`)
- [ ] Shipping docs (`/api/shipping/docs`)
- [ ] Weight totalizer in load builder (DOT compliance)
- [ ] Shipping order: Columns → Rafters → Purlins → Sag Rods/Straps → Decking → Trim

### 7.3 Customers (`/customers`)
- [ ] Customers page loads
- [ ] Customer list (`/api/customers`) — returns all
- [ ] Create customer (`/api/customers/create`)
- [ ] Update customer (`/api/customers/update`) — inline quick edit
- [ ] Delete customer (`/api/customers/delete`) — confirmation dialog
- [ ] Customer detail (`/api/customers/detail`) — drawer with all info
- [ ] Contact management (`/api/customers/contacts`):
  - [ ] Add contact (action: add)
  - [ ] Update contact (action: update)
  - [ ] Delete contact (action: delete)
  - [ ] Set primary contact — backward compat with primary_contact field
- [ ] Customer doc upload (`/api/customers/docs/upload`)
- [ ] Customer doc list (`/api/customers/docs`)
- [ ] Customer file serve (`/customer-files/{cust}/{dir}/{file}`)
- [ ] Edit/delete buttons visible on each customer card
- [ ] Contact drawer inline forms for add/edit

### 7.4 Field Operations (`/field`, `/field-ops`)
- [ ] Field ops page loads
- [ ] Daily reports, JHA, photos, equipment, expenses sections present
- [ ] All buttons functional (or showing correct empty state)

### 7.5 Job Costing (`/job-costing`)
- [ ] Page loads (not empty state bug — verified fix)
- [ ] API (`/api/costing/...`) returns data

### 7.6 Document Management (`/documents`)
- [ ] Page loads
- [ ] API (`/api/documents/...`) returns data

---

## Phase 8: Reports, Scheduling, Labels & Exports

### 8.1 Production Reports (`/reports`, `/reports/production`)
- [ ] Page loads
- [ ] Reports API (`/api/reports/production`) returns data
- [ ] Machine Utilization section: uses `m` as label (not `d.label`), `d.done` (not `d.completed`) — verified fix
- [ ] CSV export (`/api/reports/export`)
- [ ] No "undefined" values anywhere on the page

### 8.2 Production Schedule / Gantt (`/schedule`)
- [ ] Gantt page loads
- [ ] Gantt data (`/api/gantt/data`)
- [ ] Machine utilization (`/api/gantt/machines`)

### 8.3 Labels & Exports
- [ ] Labels generate (`/api/labels`)
- [ ] Labels PDF (`/api/labels/pdf`)
- [ ] Labels CSV (`/api/labels/csv`)

### 8.4 Notifications
- [ ] Notifications API (`/api/notifications`) — returns in-app notifications

### 8.5 PWA / Offline
- [ ] Manifest (`/static/manifest.json`) — valid JSON
- [ ] Service worker (`/static/service-worker.js`) — loads
- [ ] Offline page (`/offline`) — renders

### 8.6 Help Bundle
- [ ] Help bundle (`/api/help-bundle`) — returns help data

---

## Cross-Cutting Concerns (Checked Throughout All Phases)

### C.1 Permission Enforcement
Every handler must check permissions before allowing access. Test pattern:
- API endpoints that require auth return 401 for unauthenticated requests
- Pages for unauthorized roles redirect to dashboard (RULES.md §14: no 403 page shown)
- Delete operations require `can_delete` flag (God Mode only)
- User management requires `can_manage_users` flag (God Mode only)
- Financial data never rendered in HTML for users without financial permissions (not CSS hidden — excluded from response)

### C.2 Data Integrity
- Project cascade delete removes ALL related data (project dir, shop drawings dir, quote file, QC file)
- Coil delete blocked when committed > 0
- Job code sanitization (`_safe_job()` strips to `[a-zA-Z0-9_-]`)
- Version history maintained on SA/TC saves
- BOM auto-saved on calculate (bom_snapshot.json)

### C.3 UI/UX Standards (RULES.md §12)
- Toast notifications (3-second auto-dismiss) for all user actions — no `alert()` dialogs
- All buttons use inline `onclick` handlers (no global click delegation)
- No console errors on any page
- No broken images or missing assets
- Responsive behavior on mobile widths for mobile-first roles
- Dashboard cards grouped by function, group headers only shown if user has cards

### C.4 API Conventions (RULES.md §14)
- All API routes follow `/api/{resource}/{action}` pattern
- Handlers accept JSON and form-encoded POST (JSON first, fallback to form)
- Responses are always JSON
- Dates in ISO 8601 format
- IDs follow prescribed formats (usr_, WO-, LD-, etc.)

### C.5 Error Handling (RULES.md §14)
- 401 → redirect to login
- 403 → redirect to dashboard (user never sees 403)
- 404 → friendly page with nav back to dashboard
- 500 → "something went wrong" with support contact

---

## Execution Order

The audit will be executed in this order to build on verified foundations:

1. **Phase 1** (Auth) — Verify login works so all subsequent testing is valid
2. **Phase 2** (Navigation) — Verify we can reach all pages
3. **Phase 3** (Dashboard/Core) — Verify the landing page and main APIs
4. **Phase 4** (Estimating/Projects) — The heart of the business logic
5. **Phase 5** (Shop Floor) — Fabrication workflow, stickers, work orders
6. **Phase 6** (QA/QC) — Quality system, NCRs, compliance
7. **Phase 7** (Inventory/Shipping/Customers/Field) — Supporting modules
8. **Phase 8** (Reports/Scheduling/Exports) — Output and reporting

Total test cases: ~250+

Each failed test will be logged with: page/endpoint, expected behavior, actual behavior, and severity (Critical / Major / Minor).

---

## Bug Severity Definitions

- **Critical:** Feature completely broken, data loss risk, security vulnerability, or blocks core workflow
- **Major:** Feature partially broken, incorrect data displayed, or significant UX issue
- **Minor:** Cosmetic issue, minor text error, or edge case that doesn't affect core functionality

---

## Previously Fixed Issues (Verify Regression)

These bugs were found and fixed in prior sessions. Verify they remain fixed:

1. ✅ Reports Machine Utilization "undefined" values — `d.label` → `m`, `d.completed` → `d.done`
2. ✅ QA Hub em-dash encoding (`â€"`) — Content-Type charset fix
3. ✅ Sidebar footer `/profile` 404 — Changed to `/admin`
4. ✅ Shipping Hub title bug and empty page
5. ✅ WO card "no items" count on project page
6. ✅ TC Estimator card status on project page
7. ✅ Field Ops, Job Costing, QC Dashboard empty states
8. ✅ Admin page 404 bug

---

*This plan covers every registered route (175+), every API endpoint (120+), all 59 template files, all 18 roles, all 67 permissions, the complete 12-state work order item lifecycle, and all business rules from RULES.md §1–§16 and TitanForge_Master_Rules.md.*
