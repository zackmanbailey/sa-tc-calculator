SA_CALC_HTML = r"""<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>TitanForge — Structures America Estimator</title>
<style>
:root {
  --tf-dark:#0F172A; --tf-blue:#1E40AF; --tf-blue-m:#3B82F6;
  --tf-blue-l:#DBEAFE; --tf-red:#DC2626; --tf-amber:#F59E0B;
  --tf-green:#16A34A; --tf-gray:#475569; --tf-light:#F8FAFC;
  --tf-white:#ffffff; --tf-border:#E2E8F0;
}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',Arial,sans-serif;background:var(--tf-light);color:var(--tf-gray);font-size:13px}
/* Topbar */
#topbar{background:var(--tf-dark);color:#fff;padding:0 20px;display:flex;align-items:center;height:52px;box-shadow:0 2px 8px #0005}
#topbar .logo{font-size:18px;font-weight:700;letter-spacing:1px;color:#fff}
#topbar .logo span{color:var(--tf-red)}
#topbar .subtitle{font-size:11px;color:#aaa;margin-left:16px;margin-top:2px}
#topbar .spacer{flex:1}
#topbar .version{font-size:10px;color:#666}
/* Tabs */
#tabs{background:var(--tf-dark);display:flex;overflow-x:auto}
.tab{padding:10px 20px;color:#aac;cursor:pointer;font-size:12px;font-weight:600;border-bottom:3px solid transparent;white-space:nowrap;transition:all .2s}
.tab:hover{color:#fff;background:rgba(255,255,255,.07)}
.tab.active{color:#fff;border-bottom-color:var(--tf-amber)}
/* Main layout */
#main{display:flex;gap:0;height:calc(100vh - 94px)}
#sidebar{width:310px;min-width:260px;background:#fff;border-right:1px solid var(--tf-border);overflow-y:auto;padding:16px;flex-shrink:0}
#content{flex:1;overflow-y:auto;padding:20px}
/* Cards */
.card{background:#fff;border:1px solid var(--tf-border);border-radius:8px;margin-bottom:16px;overflow:hidden}
.card-hdr{background:var(--tf-blue-m);color:#fff;padding:8px 14px;font-weight:700;font-size:12px;display:flex;align-items:center;gap:8px}
.card-hdr .icon{font-size:15px}
.card-body{padding:14px}
/* Form elements */
.form-group{margin-bottom:12px}
label{display:block;font-size:11px;font-weight:600;color:var(--tf-blue);margin-bottom:4px;text-transform:uppercase;letter-spacing:.4px}
input[type=text],input[type=number],select,textarea{
  width:100%;padding:7px 10px;border:1px solid var(--tf-border);border-radius:4px;
  font-size:13px;color:var(--tf-gray);background:#fff;transition:border .2s}
input:focus,select:focus,textarea:focus{outline:none;border-color:var(--tf-blue-m);box-shadow:0 0 0 3px #2E75B615}
input[type=checkbox]{width:auto;margin-right:6px}
.check-label{display:flex;align-items:center;font-size:12px;font-weight:400;text-transform:none;letter-spacing:0;cursor:pointer}
/* Buttons */
.btn{padding:8px 16px;border:none;border-radius:4px;cursor:pointer;font-size:13px;font-weight:600;transition:all .2s;display:inline-flex;align-items:center;gap:6px}
.btn-primary{background:var(--tf-blue);color:#fff}.btn-primary:hover{background:var(--tf-blue-m)}
.btn-red{background:var(--tf-red);color:#fff}.btn-red:hover{opacity:.9}
.btn-green{background:var(--tf-green);color:#fff}.btn-green:hover{opacity:.9}
.btn-gold{background:var(--tf-amber);color:var(--tf-dark)}.btn-gold:hover{opacity:.9}
.btn-outline{background:transparent;border:1px solid var(--tf-blue-m);color:var(--tf-blue-m)}.btn-outline:hover{background:var(--tf-blue-l)}
.btn-sm{padding:5px 11px;font-size:12px}
.btn-group{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
/* Tables */
.bom-table{width:100%;border-collapse:collapse;font-size:12px}
.bom-table th{background:var(--tf-blue);color:#fff;padding:7px 10px;text-align:left;font-weight:600;font-size:11px;position:sticky;top:0}
.bom-table td{padding:6px 10px;border-bottom:1px solid #EEF0F4}
.bom-table tr:nth-child(even) td{background:#F7F9FC}
.bom-table tr:hover td{background:var(--tf-blue-l)}
.cat-row td{background:var(--tf-blue-l)!important;font-weight:700;color:var(--tf-blue);font-size:11px;text-transform:uppercase;letter-spacing:.4px}
.total-row td{background:var(--tf-green)!important;color:#fff!important;font-weight:700}
.sell-row td{background:var(--tf-red)!important;color:#fff!important;font-weight:700;font-size:13px}
/* Summary stats */
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin-bottom:16px}
.stat-card{background:#fff;border:1px solid var(--tf-border);border-radius:6px;padding:12px 14px;text-align:center}
.stat-label{font-size:10px;color:#888;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px}
.stat-value{font-size:18px;font-weight:700;color:var(--tf-blue)}
.stat-unit{font-size:10px;color:#aaa;margin-top:2px}
/* Building list */
.bldg-item{background:#F7F9FC;border:1px solid var(--tf-border);border-radius:5px;padding:10px 12px;margin-bottom:8px;cursor:pointer;transition:all .2s}
.bldg-item:hover,.bldg-item.active{background:var(--tf-blue-l);border-color:var(--tf-blue-m)}
.bldg-item .bldg-name{font-weight:700;color:var(--tf-blue);font-size:13px}
.bldg-item .bldg-dims{font-size:11px;color:#888;margin-top:2px}
/* Inventory */
.inv-table{width:100%;border-collapse:collapse;font-size:12px}
.inv-table th{background:var(--tf-dark);color:#fff;padding:7px 10px;font-size:11px;text-align:left}
.inv-table td{padding:6px 10px;border-bottom:1px solid #EEF0F4}
.inv-table tr:nth-child(even) td{background:#F7F9FC}
.stock-ok{color:#375623;font-weight:700}
.stock-low{color:orange;font-weight:700}
.stock-out{color:var(--tf-red);font-weight:700}
/* Labels preview */
.labels-wrap{display:flex;flex-wrap:wrap;gap:8px}
/* Alerts */
.alert{padding:10px 14px;border-radius:4px;margin-bottom:12px;font-size:12px}
.alert-info{background:#EEF5FF;border:1px solid #BDD6EE;color:#1F4E79}
.alert-success{background:#E8F5E9;border:1px solid #A5D6A7;color:#2E7D32}
.alert-warn{background:#FFF8E1;border:1px solid #FFE082;color:#E65100}
.alert-error{background:#FFEBEE;border:1px solid #EF9A9A;color:#B71C1C}
/* Section headers */
.section-hdr{font-size:14px;font-weight:700;color:var(--tf-blue);margin-bottom:12px;padding-bottom:6px;border-bottom:2px solid var(--tf-blue-l)}
/* Spinner */
.spinner{display:none;width:20px;height:20px;border:3px solid #ddd;border-top-color:var(--tf-blue-m);border-radius:50%;animation:spin .8s linear infinite;margin:auto}
@keyframes spin{to{transform:rotate(360deg)}}
/* Hidden */
.hidden{display:none}
/* Toast Notifications */
.toast-container{position:fixed;top:60px;right:20px;z-index:10000;display:flex;flex-direction:column;gap:8px;pointer-events:none}
.toast{padding:12px 20px;border-radius:6px;color:#fff;font-size:13px;font-weight:600;box-shadow:0 4px 12px rgba(0,0,0,0.15);animation:toastIn .3s ease;max-width:400px;pointer-events:auto}
.toast-success{background:#16A34A}.toast-error{background:#DC2626}.toast-info{background:#1E40AF}
@keyframes toastIn{from{opacity:0;transform:translateX(40px)}to{opacity:1;transform:translateX(0)}}
/* Responsive tweaks */
@media(max-width:768px){#main{flex-direction:column}#sidebar{width:100%;border-right:none;border-bottom:1px solid var(--tf-border)}}
</style>
</head>
<body>

<!-- Toast Container -->
<div id="toast-container" class="toast-container"></div>

<!-- Topbar -->
<div id="topbar">
  <!-- TitanForge Logo -->
  <div class="logo">TitanForge</div>
  <div style="margin-left:20px;display:flex;gap:16px;align-items:center;flex:1">
    <a href="/" style="color:#fff;text-decoration:none;font-size:12px;font-weight:600">Dashboard</a>
    <a href="/sa" class="nav-active" style="color:#fff;text-decoration:none;font-size:12px;font-weight:600;border-bottom:2px solid var(--tf-amber);padding-bottom:2px">Structures America Estimator</a>
    <a href="/tc" style="color:#fff;text-decoration:none;font-size:12px;font-weight:600">Titan Carports Estimator</a>
    <a href="/customers" style="color:#fff;text-decoration:none;font-size:12px;font-weight:600">Customers</a>
  </div>
  <div class="spacer"></div>
  <button onclick="openGlobalSearch()" style="background:none;border:1px solid rgba(255,255,255,0.2);color:#fff;padding:4px 12px;border-radius:6px;cursor:pointer;font-size:11px;margin-right:8px;display:flex;align-items:center;gap:4px;">&#128269; Search <kbd style="background:rgba(255,255,255,0.15);padding:1px 5px;border-radius:3px;font-size:9px;">Ctrl+K</kbd></button>
  <div class="version" style="margin-right:12px">v3.0</div>
  <div id="auth-controls" style="margin-left:auto;display:flex;gap:8px;align-items:center">
    <a href="/admin" style="color:#C89A2E;font-size:11px;font-weight:700;text-decoration:none" title="User Management">👤 Admin</a>
    <a href="/auth/logout" style="background:rgba(155,28,28,.5);border:1px solid rgba(155,28,28,.7);border-radius:4px;padding:4px 10px;font-size:10px;font-weight:700;color:#ffaaaa;text-decoration:none">Log Out</a>
  </div>
</div>

<!-- Inventory Alert Banner (hidden by default, shown by JS) -->
<div id="inv-alert-banner" style="display:none;background:#FFF3CD;border-bottom:2px solid #FFD43B;padding:8px 20px;font-size:12px;color:#856404;cursor:pointer" onclick="showTab('inventory');document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));document.querySelectorAll('.tab')[4].classList.add('active')">
  <span style="font-weight:700">⚠️ Inventory Alert:</span>
  <span id="inv-alert-text"></span>
  <span style="float:right;color:#666;font-size:11px">Click to view →</span>
</div>

<!-- Tabs -->
<div id="tabs">
  <div class="tab active" onclick="showTab('calc')">⚙️ Calculator</div>
  <div class="tab" onclick="showTab('bom')">📋 Bill of Materials</div>
  <div class="tab" onclick="showTab('pricing')">💰 Price Overrides</div>
  <div class="tab" onclick="showTab('labels')">🏷️ Shop Labels</div>
  <div class="tab" onclick="showTab('inventory')">📦 Inventory <span id="inv-tab-badge" style="display:none;background:#C00000;color:#fff;border-radius:10px;padding:1px 6px;font-size:10px;font-weight:700;margin-left:4px"></span></div>
</div>

<!-- Main -->
<div id="main">

  <!-- SIDEBAR: Project + Building Setup -->
  <div id="sidebar">

    <!-- Recent Projects -->
    <div class="card">
      <div class="card-hdr" style="background:var(--tf-amber);color:var(--tf-dark)"><span class="icon">📂</span>Projects
        <span id="version-badge" style="display:none;margin-left:auto;background:#1F4E79;color:#fff;border-radius:10px;padding:2px 8px;font-size:10px;font-weight:700">v1</span>
      </div>
      <div class="card-body" style="padding:10px 14px">
        <div style="display:flex;gap:6px;align-items:center">
          <select id="recent_projects" style="flex:1;font-size:12px;padding:5px 8px" onchange="loadProject(this.value)">
            <option value="">— Recent Projects —</option>
          </select>
          <button class="btn btn-primary btn-sm" onclick="loadRecentProjects()" title="Refresh list" style="padding:5px 8px">🔄</button>
        </div>
        <div style="display:flex;gap:6px;margin-top:6px">
          <button class="btn btn-green btn-sm" style="flex:1;font-size:11px" onclick="saveProjectManual()">💾 Save (New Revision)</button>
          <button class="btn btn-outline btn-sm" style="font-size:11px" onclick="showRevisionHistory()">📋 History</button>
        </div>
      </div>
    </div>

    <!-- Project Info -->
    <div class="card">
      <div class="card-hdr"><span class="icon">📁</span>Project Info</div>
      <div class="card-body">
        <div class="form-group">
          <label>Project Name</label>
          <input type="text" id="proj_name" placeholder="e.g. Bluegate Boat & RV" oninput="updateJobCode()"/>
        </div>
        <div class="form-group">
          <label>Customer Name</label>
          <input type="text" id="proj_customer" placeholder="Customer / Owner"/>
        </div>
        <div class="form-group">
          <label>Site Address</label>
          <input type="text" id="proj_address" placeholder="123 Main St"/>
        </div>
        <div style="display:grid;grid-template-columns:2fr 1fr 1fr;gap:8px">
          <div class="form-group">
            <label>City</label>
            <input type="text" id="proj_city" placeholder="City" oninput="updateJobCode()"/>
          </div>
          <div class="form-group">
            <label>State</label>
            <select id="proj_state" onchange="onStateChange()">
              <option value="TX" selected>TX</option>
              <option value="NM">NM</option>
              <option value="CO">CO</option>
              <option value="FL">FL</option>
              <option value="CA">CA</option>
              <option value="AZ">AZ</option>
              <option value="NV">NV</option>
              <option value="OK">OK</option>
              <option value="KS">KS</option>
              <option value="NE">NE</option>
              <option value="Other">Other</option>
            </select>
          </div>
          <div class="form-group">
            <label>ZIP</label>
            <input type="text" id="proj_zip" placeholder="77302"/>
          </div>
        </div>
        <div class="form-group">
          <label>Job Code</label>
          <input type="text" id="proj_jobcode" placeholder="e.g. BGATN-24"/>
        </div>
        <div class="form-group">
          <label>Wind Speed (MPH)</label>
          <input type="number" id="proj_wind" value="115" min="90" max="200"/>
        </div>
        <div class="form-group">
          <label>Markup (%)</label>
          <input type="number" id="proj_markup" value="35" min="0" max="100" step="1"/>
        </div>
        <div class="form-group">
          <label>Quote Date</label>
          <input type="text" id="proj_date" placeholder="MM/DD/YYYY"/>
        </div>
      </div>
    </div>

    <!-- Buildings List -->
    <div class="card">
      <div class="card-hdr"><span class="icon">🏗️</span>Buildings</div>
      <div class="card-body">
        <div id="bldg-list"></div>
        <div class="btn-group">
          <button class="btn btn-primary btn-sm" onclick="addBuilding()">➕ Add Building</button>
          <button class="btn btn-outline btn-sm" onclick="removeBuilding()">🗑️ Remove Last</button>
        </div>
      </div>
    </div>

    <!-- Calculate Button -->
    <div style="margin-bottom:16px">
      <button class="btn btn-red" style="width:100%;padding:12px;font-size:14px" onclick="calculate()">
        ⚡ CALCULATE BOM
      </button>
    </div>

  </div>

  <!-- CONTENT AREA -->
  <div id="content">

    <!-- Calculator Tab -->
    <div id="tab-calc" class="tab-content">
      <div class="section-hdr">Building Configuration</div>
      <div id="bldg-forms"></div>
      <div class="alert alert-info">
        Fill in project info and building dimensions in the sidebar, then click <strong>CALCULATE BOM</strong>.
      </div>
    </div>

    <!-- BOM Tab -->
    <div id="tab-bom" class="tab-content hidden">
      <div id="bom-content">
        <div class="alert alert-info">
          Configure your project and click <strong>CALCULATE BOM</strong> to see results.
        </div>
      </div>
    </div>

    <!-- Price Overrides Tab -->
    <div id="tab-pricing" class="tab-content hidden">
      <div class="section-hdr">Price Overrides & Manual Line Items</div>
      <div id="pricing-content">
        <div class="alert alert-info">
          Run <strong>CALCULATE BOM</strong> first, then use this tab to edit prices per line item,
          add manual items (trim, hardware, freight), and see live totals.
        </div>
      </div>
    </div>

    <!-- Labels Tab -->
    <div id="tab-labels" class="tab-content hidden">
      <div class="section-hdr">Shop Fabrication Labels</div>
      <div class="card">
        <div class="card-hdr"><span class="icon">⚙️</span>Label Settings</div>
        <div class="card-body">
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px">
            <div class="form-group">
              <label>Destination Site</label>
              <input type="text" id="lbl_destination" placeholder="e.g. Sanford, FL"/>
            </div>
            <div class="form-group">
              <label>Fabricator Name</label>
              <input type="text" id="lbl_fabricator" placeholder="e.g. J. Smith"/>
            </div>
            <div class="form-group">
              <label>QR Base URL</label>
              <input type="text" id="lbl_qr_url" value="https://structuresamerica.com/shop"/>
            </div>
          </div>
          <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px">
            <div class="form-group">
              <label>Columns/label</label>
              <input type="number" id="grp_column" value="1" min="1"/>
            </div>
            <div class="form-group">
              <label>Rafters/label</label>
              <input type="number" id="grp_rafter" value="1" min="1"/>
            </div>
            <div class="form-group">
              <label>Purlins/label</label>
              <input type="number" id="grp_purlin" value="1" min="1"/>
            </div>
            <div class="form-group">
              <label>Straps/label</label>
              <input type="number" id="grp_strap" value="10" min="1"/>
            </div>
          </div>
          <div class="btn-group">
            <button class="btn btn-primary" onclick="generateLabels()">🏷️ Generate Labels</button>
            <button class="btn btn-green" onclick="downloadZPL()">⬇️ Download ZPL (Zebra)</button>
            <button class="btn btn-red" onclick="downloadLabelsPDF()">📄 Download PDF (4×6 print-ready)</button>
            <button class="btn btn-outline" onclick="downloadLabelsCSV()">📊 Download CSV (NiceLabel / BarTender)</button>
          </div>
        </div>
      </div>
      <div id="labels-preview"></div>
    </div>

    <!-- Inventory Tab -->
    <div id="tab-inventory" class="tab-content hidden">
      <div class="section-hdr">Inventory Management</div>
      <div id="inventory-content">
        <div class="spinner" id="inv-spinner"></div>
      </div>
    </div>

  </div>
</div>

<script>
// ─────────────────────────────────────────────
// TOAST NOTIFICATIONS
// ─────────────────────────────────────────────
function showToast(msg, type='info', duration=3000) {
  let c = document.getElementById('toast-container');
  if (!c) { c = document.createElement('div'); c.id = 'toast-container'; c.className = 'toast-container'; document.body.appendChild(c); }
  const t = document.createElement('div');
  t.className = 'toast toast-' + type;
  t.textContent = msg;
  c.appendChild(t);
  setTimeout(() => { t.style.opacity = '0'; t.style.transition = 'opacity .3s'; setTimeout(() => t.remove(), 300); }, duration);
}

// ─────────────────────────────────────────────
// STATE
// ─────────────────────────────────────────────
let buildings = [];
let currentBOM = null;
let currentLabels = null;

// ── Price Overrides State ──────────────────
// priceOverrides[bldgIdx][lineIdx] = { cost: number, sell: number }
let priceOverrides = {};
// manualItems: array of { category, description, qty, unit, unit_cost, sell_price, notes }
let manualItems = [];
// Auto-save debounce
let _autoSaveTimer = null;

const WIND_BY_STATE = {TX:115,NM:115,CO:115,FL:140,CA:115,AZ:115,NV:115,OK:130,KS:130,NE:130};
const FOOTING_BY_STATE = {TX:10,NM:10,CO:10,FL:12,CA:10,Default:10};

// Initialize with today's date and one building
window.onload = function() {
  const today = new Date();
  const mm = String(today.getMonth()+1).padStart(2,'0');
  const dd = String(today.getDate()).padStart(2,'0');
  const yyyy = today.getFullYear();
  document.getElementById('proj_date').value = `${mm}/${dd}/${yyyy}`;
  addBuilding();
  renderBuildingList();
  loadRecentProjects();
  // Check inventory alerts on page load (runs in background)
  checkInventoryAlerts();
  // Auto-load project from URL param ?project=JOB_CODE
  const urlParams = new URLSearchParams(window.location.search);
  const projectCode = urlParams.get('project');
  if (projectCode) {
    autoLoadFromProject(projectCode);
  }
};

async function autoLoadFromProject(jobCode) {
  try {
    // First try to load existing calc data
    const loadResp = await fetch('/api/project/load', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ job_code: jobCode }),
    });
    const loadResult = await loadResp.json();
    if (loadResult.ok && loadResult.data) {
      // Full project data exists, load it
      loadProject(jobCode);
      return;
    }
  } catch(e) { /* no saved calc data yet */ }

  // No calc data, but try to load metadata to auto-fill customer info
  try {
    const metaResp = await fetch('/api/project/metadata?job_code=' + encodeURIComponent(jobCode));
    const metaResult = await metaResp.json();
    if (metaResult.ok && metaResult.metadata) {
      const m = metaResult.metadata;
      document.getElementById('proj_jobcode').value = m.job_code || jobCode;
      if (m.project_name) document.getElementById('proj_name').value = m.project_name;
      if (m.customer && m.customer.name) document.getElementById('proj_customer').value = m.customer.name;
      if (m.location) {
        if (m.location.street) document.getElementById('proj_address').value = m.location.street;
        if (m.location.city) document.getElementById('proj_city').value = m.location.city;
        if (m.location.state) document.getElementById('proj_state').value = m.location.state;
        if (m.location.zip) document.getElementById('proj_zip').value = m.location.zip;
      }
    }
  } catch(e) { /* silent */ }
}

async function checkInventoryAlerts() {
  try {
    const resp = await fetch('/api/inventory');
    const data = await resp.json();
    let outCount = 0, lowCount = 0;
    for (const [id, coil] of Object.entries(data.coils || {})) {
      const avail = (coil.stock_lbs || 0) - (coil.committed_lbs || 0);
      const minStock = coil.min_stock_lbs || 0;
      if (avail <= 0) outCount++;
      else if (minStock > 0 && avail < minStock) lowCount++;
      else if (avail < 2000) lowCount++;
    }
    updateInventoryAlerts(outCount, lowCount);
  } catch(e) { /* silent */ }
}

// ─────────────────────────────────────────────
// TABS
// ─────────────────────────────────────────────
function showTab(name) {
  document.querySelectorAll('.tab-content').forEach(t => t.classList.add('hidden'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById('tab-' + name).classList.remove('hidden');
  event.target.classList.add('active');
  if (name === 'inventory') loadInventory();
  if (name === 'pricing') renderPricingTab();
}

// ─────────────────────────────────────────────
// PROJECT
// ─────────────────────────────────────────────
function updateJobCode() {
  const city = document.getElementById('proj_city').value.trim().toUpperCase().replace(/\s+/g,'').slice(0,3);
  const state = document.getElementById('proj_state').value.slice(0,2);
  const yr = new Date().getFullYear() % 100;
  if (city && state) document.getElementById('proj_jobcode').value = `${city}${state}-${yr}`;
}

function onStateChange() {
  const st = document.getElementById('proj_state').value;
  if (WIND_BY_STATE[st]) document.getElementById('proj_wind').value = WIND_BY_STATE[st];
  if (FOOTING_BY_STATE[st]) document.getElementById('proj_footing').value = FOOTING_BY_STATE[st];
  updateJobCode();
}

// ─────────────────────────────────────────────
// BUILDINGS
// ─────────────────────────────────────────────
let bldgCounter = 0;

function addBuilding() {
  bldgCounter++;
  buildings.push({
    id: `B${bldgCounter}`,
    building_id: `B${bldgCounter}`,
    building_name: `Building ${bldgCounter}`,
    type: '2post',
    width_ft: 40,
    // Length mode: 'direct' or 'spaces'
    length_mode: 'direct',
    length_ft: 200,
    n_spaces: 0,
    space_width_ft: 12,    // parking stall width; 0 = legacy equal-overhang
    overhang_mode: 'none', // 'none' or '1space'
    clear_height_ft: 14,
    max_bay_ft: 36,
    pitch_key: '1/4:12',
    // Purlin spacing: null = auto-calc
    purlin_spacing_override: null,
    embedment_ft: 4.333,
    column_buffer_ft: 0.5,
    reinforced: true,
    rebar_col_size: 'auto',
    rebar_beam_size: 'auto',
    straps_per_rafter: 4,
    strap_length_in: 28,
    include_back_wall: false,
    include_end_walls: false,
    include_side_walls: false,
    wall_girt_spacing_override: null,
    include_rafter_rebar: false,
    rebar_rafter_size: '#9',
    include_trim: false,
    include_labor: true,
    include_consumables: true,
    welding_cost_per_5000sqft: 300,
    labor_daily_rate: 960,
    coil_prices: {},
    // Per-building footing depth (default 10')
    footing_depth_ft: 10,
    // Rafter Configuration defaults (column placement, angled purlins, rebar, splice)
    column_mode: 'auto',              // "auto" (quarter-point), "spacing", or "manual"
    column_spacing_ft: 25,            // used when column_mode === 'spacing'
    column_count_manual: 1,           // used when column_mode === 'manual'
    column_positions_manual: '',      // comma-separated ft positions for manual mode
    front_col_position_ft: 0,         // front column position when back wall enabled
    angled_purlins: false,            // master toggle for angled purlin mode
    purlin_angle_deg: 15,             // angle from perpendicular (5–45°)
    rebar_max_stick_ft: 20,           // max rebar stick length in rafter
    rebar_end_gap_ft: 5,              // gap from rafter end to first rebar
    splice_location_ft: 0,            // 0 = auto-calculate splice point
    // Rafter/Column drawing fields
    purlin_type: 'Z',                 // Z or C channel purlins
    roofing_overhang_ft: 0.5,         // panel overhang past eave purlin
    above_grade_ft: 8,                // column height above finished grade
    cut_allowance_in: 6,              // extra length for field cuts (inches)
  });
  renderBuildingList();
  renderBuildingForms();
}

function removeLastBuilding() {
  if (buildings.length > 1) {
    buildings.pop();
    // Renumber names if they're still at default
    renderBuildingList();
    renderBuildingForms();
  }
}

function removeBuilding() {
  if (buildings.length > 1) { buildings.pop(); renderBuildingList(); renderBuildingForms(); }
}

function renderBuildingList() {
  const el = document.getElementById('bldg-list');
  el.innerHTML = buildings.map((b,i) => `
    <div class="bldg-item ${i===0?'active':''}" onclick="scrollToBldg('${b.id}')">
      <div class="bldg-name">${b.building_name || b.name || 'Building '+(i+1)}</div>
      <div class="bldg-dims">${b.width_ft <= 45 ? 'TEE' : 'DBL-COL'} · ${b.width_ft}'×${b.length_ft}' · Ht:${b.clear_height_ft}'</div>
    </div>
  `).join('');
}

// Auto-calculate purlin spacing from building width
function autoPurlinSpacing(width_ft) {
  if (width_ft <= 30) return 5.0;
  if (width_ft <= 34.333) return 4.0;
  return 3.5;
}

// Auto-calculate purlin row count
function purlinRowCount(width_ft, spacing_ft) {
  return Math.floor(width_ft / spacing_ft) + 1;
}

// Update purlin display when spacing or width changes
function refreshPurlinDisplay(bid) {
  const b = buildings.find(x => x.id === bid);
  if (!b) return;
  const spacing = b.purlin_spacing_override || autoPurlinSpacing(b.width_ft);
  const rows = purlinRowCount(b.width_ft, spacing);
  const autoEl = document.getElementById(bid+'_purlin_auto');
  const rowEl = document.getElementById(bid+'_purlin_rows');
  if (autoEl) autoEl.textContent = b.purlin_spacing_override
    ? `(manual)`
    : `(auto: ${spacing}' OC for ${b.width_ft}' width)`;
  if (rowEl) rowEl.textContent = `${rows} rows`;
}

// Update length when spaces mode is used
function refreshLength(bid) {
  const b = buildings.find(x => x.id === bid);
  if (!b) return;
  if (b.length_mode === 'spaces' && b.n_spaces > 0 && b.space_width_ft > 0) {
    b.length_ft = b.n_spaces * b.space_width_ft;
    const el = document.getElementById(bid+'_length_calc');
    if (el) el.textContent = `= ${b.length_ft}' total`;
    const lenEl = document.getElementById(bid+'_length_display');
    if (lenEl) lenEl.textContent = b.length_ft + "'";
  }
}

function scrollToBldg(id) {
  const el = document.getElementById('bldg-form-'+id);
  if (el) el.scrollIntoView({behavior:'smooth'});
}

function renderBuildingForms() {
  const container = document.getElementById('bldg-forms');
  container.innerHTML = buildings.map(b => buildingFormHTML(b)).join('');
}

// ─────────────────────────────────────────────
// SPACE-BASED COLUMN LAYOUT PREVIEW
// ─────────────────────────────────────────────
function previewColumnLayout(b) {
  const sw = parseFloat(b.space_width_ft) || 0;
  if (sw <= 0) return { positions: null, warning: null, summary: null };

  const length = parseFloat(b.length_ft) || 0;
  const maxBay = parseFloat(b.max_bay_ft) || 36;
  const maxSpPerBay = Math.min(3, Math.max(1, Math.floor(maxBay / sw)));
  const nTotal = Math.round(length / sw);
  const remainder = length % sw;

  const warning = remainder > 0.01
    ? `⚠ ${length}' ÷ ${sw}' = ${(length/sw).toFixed(2)} spaces (not a whole number). Nearest clean length: ${Math.round(length/sw)*sw}'.`
    : null;

  let interiorSpaces, overhang;
  if (b.overhang_mode === '1space') {
    overhang = sw;
    interiorSpaces = Math.max(1, nTotal - 2);
  } else {
    overhang = 0;
    interiorSpaces = nTotal;
  }

  // Build bays
  const nFull = Math.floor(interiorSpaces / maxSpPerBay);
  const shortSp = interiorSpaces % maxSpPerBay;
  const fullBay = maxSpPerBay * sw;
  let bays = [];
  if (shortSp === 0) {
    bays = Array(nFull).fill(fullBay);
  } else {
    const shortBay = shortSp * sw;
    const total = nFull + 1;
    const ci = Math.floor(total / 2);
    for (let i = 0; i < total; i++) bays.push(i === ci ? shortBay : fullBay);
  }

  // Build positions
  let pos = [overhang];
  for (const bay of bays) pos.push(+(pos[pos.length-1] + bay).toFixed(2));

  const bayDesc = [...new Set(bays)].map(bay => {
    const cnt = bays.filter(x => x === bay).length;
    return `${cnt}×${bay}'`;
  }).join(', ');

  const summary = `${pos.length} frames  ·  ${bays.length} bays (${bayDesc})  ·  overhang ${overhang}' each end`;
  const posStr = pos.map(p => p + "'").join(' — ');

  return { positions: posStr, warning, summary };
}

function buildingFormHTML(b) {
  const autoSpacing = autoPurlinSpacing(b.width_ft);
  const effSpacing = b.purlin_spacing_override || autoSpacing;
  const rows = purlinRowCount(b.width_ft, effSpacing);
  const spacingLabel = b.purlin_spacing_override
    ? `(manual)` : `(auto for ${b.width_ft}' width)`;
  const bname = b.building_name || b.name || b.id;

  return `
  <div class="card" id="bldg-form-${b.id}">
    <div class="card-hdr" style="background:var(--tf-blue)"><span class="icon">🏗️</span>
      <input type="text" id="${b.id}_bname" value="${bname}"
        style="background:transparent;border:none;color:#fff;font-weight:700;font-size:13px;width:200px"
        onchange="updateBldg('${b.id}','building_name',this.value)"/>
      <span style="margin-left:auto;font-size:11px;opacity:.7">${b.id}</span>
    </div>
    <div class="card-body">

      <!-- Row 1: Type, Pitch, Width, Clear Height -->
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:10px;margin-bottom:10px">
        <div class="form-group">
          <label>Frame Type (Auto)</label>
          <div id="${b.id}_frame_type" style="padding:7px 10px;background:#F0F7FF;border:1px solid var(--tf-border);border-radius:4px;font-size:13px;font-weight:600;color:var(--tf-blue)">
            ${b.width_ft <= 45 ? 'Tee (1 col/rafter)' : 'Double Column (2+ cols/rafter)'}
          </div>
          <div style="font-size:10px;color:#888;margin-top:2px">Auto: ≤45' = Tee, >45' = multi-column</div>
        </div>
        <div class="form-group">
          <label>Roof Pitch</label>
          <select onchange="updateBldg('${b.id}','pitch_key',this.value)">
            <option value="1/4:12" ${(b.pitch_key||'1/4:12')==='1/4:12'?'selected':''}>1/4":12 (1.2 deg)</option>
            <option value="5deg" ${b.pitch_key==='5deg'?'selected':''}>5 degrees</option>
            <option value="7.5deg" ${b.pitch_key==='7.5deg'?'selected':''}>7.5 degrees</option>
            <option value="10deg" ${b.pitch_key==='10deg'?'selected':''}>10 degrees</option>
          </select>
        </div>
        <div class="form-group">
          <label>Clear Height (ft)</label>
          <input type="number" value="${b.clear_height_ft}" min="8" max="30" step="0.5"
            onchange="updateBldg('${b.id}','clear_height_ft',parseFloat(this.value))"/>
        </div>
        <div class="form-group">
          <label>Max Bay Size (ft)</label>
          <input type="number" value="${b.max_bay_ft}" min="10" max="60" step="0.5"
            onchange="updateBldg('${b.id}','max_bay_ft',parseFloat(this.value))"/>
        </div>
      </div>

      <!-- Row 2: Width + Length + Column Layout -->
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
        <div class="form-group">
          <label>Building Width (ft)</label>
          <input type="number" value="${b.width_ft}" min="10" max="200" step="0.5"
            onchange="updateBldg('${b.id}','width_ft',parseFloat(this.value));refreshPurlinDisplay('${b.id}')"/>
        </div>

        <!-- Length mode selector -->
        <div class="form-group">
          <label>Building Length</label>
          <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
            <select style="width:110px" onchange="updateBldg('${b.id}','length_mode',this.value);renderBuildingForms()">
              <option value="direct" ${(b.length_mode||'direct')==='direct'?'selected':''}>Direct (ft)</option>
              <option value="spaces" ${b.length_mode==='spaces'?'selected':''}>Spaces</option>
            </select>
            ${b.length_mode==='spaces' ? `
              <input type="number" placeholder="# spaces" value="${b.n_spaces||''}" min="1" max="500" step="1"
                style="width:80px"
                onchange="updateBldg('${b.id}','n_spaces',parseInt(this.value));refreshLength('${b.id}');renderBuildingForms()"/>
              <span style="font-size:11px">×</span>
              <input type="number" placeholder="ft/space" value="${b.space_width_ft||12}" min="1" step="0.5"
                style="width:70px"
                onchange="updateBldg('${b.id}','space_width_ft',parseFloat(this.value));refreshLength('${b.id}');renderBuildingForms()"/>
              <span id="${b.id}_length_calc" style="font-size:11px;color:var(--tf-blue-m);font-weight:700">
                = ${(b.n_spaces||0)*(b.space_width_ft||12)}' total
              </span>
            ` : `
              <input type="number" value="${b.length_ft}" min="10" max="5000" step="1"
                style="width:100px"
                onchange="updateBldg('${b.id}','length_ft',parseFloat(this.value));renderBuildingForms()"/>
              <span style="font-size:11px;color:#888">ft</span>
            `}
          </div>
        </div>
      </div>

      <!-- Rafter Placement (Overhang + Space Width) -->
      ${(() => {
        const sw = parseFloat(b.space_width_ft) || 0;
        const layout = previewColumnLayout(b);
        const showSpaceWidth = b.length_mode === 'spaces' || b.overhang_mode === '1space';
        return `
      <div style="background:#F0F7FF;border:1px solid #BDD6EE;border-radius:6px;padding:10px;margin-bottom:10px">
        <div style="font-size:11px;font-weight:700;color:var(--tf-blue);margin-bottom:8px;text-transform:uppercase;letter-spacing:.4px">
          Rafter Placement
        </div>
        <div style="display:flex;gap:16px;align-items:flex-end;flex-wrap:wrap">
          <div class="form-group" style="margin-bottom:0">
            <label>Overhang Mode</label>
            <select onchange="updateBldg('${b.id}','overhang_mode',this.value);renderBuildingForms()">
              <option value="none" ${(b.overhang_mode||'none')==='none'?'selected':''}>No Overhang</option>
              <option value="1space" ${b.overhang_mode==='1space'?'selected':''}>1 Space Overhang</option>
            </select>
          </div>
          <div class="form-group" style="margin-bottom:0">
            <label>Space Width (ft)</label>
            <input type="number" value="${b.space_width_ft||12}" min="6" max="30" step="0.5"
              style="width:80px"
              onchange="updateBldg('${b.id}','space_width_ft',parseFloat(this.value));renderBuildingForms()"/>
            <div style="font-size:10px;color:#888;margin-top:2px">Parking stall width · 0 = auto</div>
          </div>
        </div>
        ${layout.warning ? `
        <div class="alert alert-warn" style="margin-top:8px;padding:6px 10px;font-size:11px">
          ${layout.warning}
        </div>` : ''}
        ${layout.summary ? `
        <div style="margin-top:8px;font-size:11px;color:var(--tf-blue-m);font-weight:600">
          ${layout.summary}
        </div>
        <div style="font-size:10px;color:#666;margin-top:3px;font-family:monospace;overflow-x:auto;white-space:nowrap">
          Columns: ${layout.positions}
        </div>` : ''}
      </div>`;
      })()}

      <!-- Row 3: Purlin spacing (direct input) -->
      <div style="background:#F0F4FA;border:1px solid var(--tf-border);border-radius:6px;padding:10px;margin-bottom:10px">
        <div class="form-group" style="margin-bottom:0">
          <label>Purlin Spacing (ft)</label>
          <input type="number" value="${effSpacing}" min="1" max="10" step="0.5"
            onchange="updateBldg('${b.id}','purlin_spacing_override',parseFloat(this.value)||null);refreshPurlinDisplay('${b.id}')"/>
          <div style="font-size:10px;color:#888;margin-top:2px">OC (on-center) spacing</div>
        </div>
      </div>

      <!-- Row 4: Column Details -->
      <details style="margin-bottom:8px">
        <summary style="cursor:pointer;font-size:12px;color:var(--tf-blue-m);font-weight:600;padding:4px 0">
          ▸ Column Details
        </summary>
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:10px">
          <div class="form-group">
            <label>Footing Depth (ft)</label>
            <input type="number" value="${b.footing_depth_ft||10}" min="4" max="25" step="0.5"
              onchange="updateBldg('${b.id}','footing_depth_ft',parseFloat(this.value))"/>
            <div style="font-size:10px;color:#888;margin-top:2px">Default: 10 ft</div>
          </div>
          <div class="form-group">
            <label>Embedment (ft)</label>
            <input type="number" value="${b.embedment_ft||4.333}" min="1" max="15" step="0.083"
              onchange="updateBldg('${b.id}','embedment_ft',parseFloat(this.value))"/>
            <div style="font-size:10px;color:#888;margin-top:2px">Default: 4'-4" = 4.333'</div>
          </div>
          <div class="form-group">
            <label>Buffer (ft)</label>
            <input type="number" value="${b.column_buffer_ft||0.5}" min="0" max="2" step="0.083"
              onchange="updateBldg('${b.id}','column_buffer_ft',parseFloat(this.value))"/>
            <div style="font-size:10px;color:#888;margin-top:2px">Default: 6" = 0.5'</div>
          </div>
          <div class="form-group">
            <label>Col Rebar Size</label>
            <select onchange="updateBldg('${b.id}','rebar_col_size',this.value)">
              <option value="auto" ${(!b.rebar_col_size||b.rebar_col_size==='auto')?'selected':''}>Auto</option>
              ${['#5','#6','#7','#8','#9','#10','#11'].map(s=>`<option value="${s}" ${b.rebar_col_size===s?'selected':''}>${s}</option>`).join('')}
            </select>
          </div>
          <div class="form-group">
            <label>Beam Rebar Size</label>
            <select onchange="updateBldg('${b.id}','rebar_beam_size',this.value)">
              <option value="auto" ${(!b.rebar_beam_size||b.rebar_beam_size==='auto')?'selected':''}>Auto</option>
              ${['#5','#6','#7','#8','#9','#10','#11'].map(s=>`<option value="${s}" ${b.rebar_beam_size===s?'selected':''}>${s}</option>`).join('')}
            </select>
          </div>
        </div>
        <div style="margin-top:8px">
          <label class="check-label">
            <input type="checkbox" ${(b.reinforced!==false)?'checked':''}
              onchange="updateBldg('${b.id}','reinforced',this.checked)"/>
            Reinforce Columns (rebar = depth + 8') — default
          </label>
          <div style="font-size:10px;color:#888;margin-top:2px;margin-left:20px">
            Unchecked = standard (rebar = depth − embedment)
          </div>
        </div>
      </details>

      <!-- Row 4b: Rafter Details -->
      ${(() => {
        const slopeDeg = {
          '1/4:12': 1.19, '5deg': 5.0, '7.5deg': 7.5, '10deg': 10.0
        }[b.pitch_key||'1/4:12'] || 1.19;
        const halfW = (b.width_ft||40) / 2;
        const slopeRad = slopeDeg * Math.PI / 180;
        const rise = halfW * Math.tan(slopeRad);
        const rafterSlopeFt = 2 * Math.sqrt(halfW*halfW + rise*rise);
        const spliceNeeded = rafterSlopeFt > 53;
        const nRafters = (b.n_frames || 0);
        const nSplice = spliceNeeded ? nRafters * 2 : 0;
        return `
      <details style="margin-bottom:8px">
        <summary style="cursor:pointer;font-size:12px;color:var(--tf-blue-m);font-weight:600;padding:4px 0">
          ▸ Rafter Details
        </summary>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:10px">
          <div>
            <div style="font-size:11px;font-weight:600;color:var(--tf-blue);text-transform:uppercase;letter-spacing:.4px;margin-bottom:4px">Rafter Slope Length</div>
            <div style="font-size:13px;font-weight:700;color:var(--tf-gray)">${rafterSlopeFt.toFixed(2)} ft</div>
            <div style="font-size:10px;color:#888;margin-top:2px">${b.width_ft||40}' wide @ ${slopeDeg}°</div>
          </div>
          <div>
            <div style="font-size:11px;font-weight:600;color:var(--tf-blue);text-transform:uppercase;letter-spacing:.4px;margin-bottom:4px">Splice Plates</div>
            ${spliceNeeded ? `
            <div style="font-size:12px;font-weight:700;color:var(--tf-red)">AUTO-TRIGGERED</div>
            <div style="font-size:10px;color:#888;margin-top:2px">${rafterSlopeFt.toFixed(1)}' &gt; 53' · ${nSplice} plates (2 per rafter)</div>
            ` : `
            <div style="font-size:12px;color:#4CAF50;font-weight:600">Not needed</div>
            <div style="font-size:10px;color:#888;margin-top:2px">${rafterSlopeFt.toFixed(1)}' ≤ 53'</div>
            `}
          </div>
          <div>
            <div style="font-size:11px;font-weight:600;color:var(--tf-blue);text-transform:uppercase;letter-spacing:.4px;margin-bottom:4px">Rebar Size (auto)</div>
            <div style="font-size:13px;font-weight:700;color:var(--tf-gray)" id="${b.id}_rebar_beam_auto">see below</div>
            <div style="font-size:10px;color:#888;margin-top:2px">Wind speed &amp; bay size driven</div>
          </div>
        </div>
        <div style="margin-top:12px;padding-top:10px;border-top:1px solid var(--tf-border)">
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;align-items:start">
            <div class="form-group" style="margin-bottom:0">
              <label>Beam Rebar Size Override</label>
              <select onchange="updateBldg('${b.id}','rebar_beam_size',this.value)">
                <option value="auto" ${(!b.rebar_beam_size||b.rebar_beam_size==='auto')?'selected':''}>Auto</option>
                ${['#5','#6','#7','#8','#9','#10','#11'].map(s=>`<option value="${s}" ${b.rebar_beam_size===s?'selected':''}>${s}</option>`).join('')}
              </select>
            </div>
            <div style="padding-top:18px">
              <label class="check-label">
                <input type="checkbox" ${b.include_rafter_rebar?'checked':''}
                  onchange="updateBldg('${b.id}','include_rafter_rebar',this.checked);renderBuildingForms()"/>
                Include Rafter Rebar
              </label>
              <div style="font-size:10px;color:#888;margin-top:3px;margin-left:20px">
                Diagonal C-section reinforcement inside rafters
              </div>
            </div>
            ${b.include_rafter_rebar ? `
            <div class="form-group" style="margin-bottom:0">
              <label>Rafter Rebar Size</label>
              <select onchange="updateBldg('${b.id}','rebar_rafter_size',this.value)">
                ${['#5','#6','#7','#8','#9','#10','#11'].map(s=>`<option value="${s}" ${(b.rebar_rafter_size||'#9')===s?'selected':''}>${s}</option>`).join('')}
              </select>
            </div>` : '<div></div>'}
          </div>
        </div>
      </details>`;
      })()}

      <!-- Row 4b: Rafter Configuration (Column Placement, Angled Purlins, Rebar Config) -->
      <details style="margin-bottom:8px" ${(b.angled_purlins||b.column_mode!=='auto')?'open':''}>
        <summary style="cursor:pointer;font-size:12px;color:var(--tf-blue-m);font-weight:600;padding:4px 0">
          ▸ Rafter Configuration
        </summary>
        <div style="font-size:10px;color:#888;margin-bottom:8px;margin-top:6px">
          Column placement on rafter, angled purlin mode, and rebar stick layout.
        </div>

        <!-- Column Mode -->
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:10px">
          <div class="form-group">
            <label>Column Mode</label>
            <select onchange="updateBldg('${b.id}','column_mode',this.value);renderBuildingForms()">
              <option value="auto" ${(b.column_mode||'auto')==='auto'?'selected':''}>Auto (Quarter-Point)</option>
              <option value="spacing" ${b.column_mode==='spacing'?'selected':''}>Spacing</option>
              <option value="manual" ${b.column_mode==='manual'?'selected':''}>Manual</option>
            </select>
            <div style="font-size:10px;color:#888;margin-top:2px">
              Auto: ≤45' = 1 col, >45' = max(2, ceil(W/60))
            </div>
          </div>
          ${b.column_mode==='spacing' ? `
          <div class="form-group">
            <label>Column Spacing (ft)</label>
            <input type="number" value="${b.column_spacing_ft||25}" min="5" max="100" step="0.5"
              onchange="updateBldg('${b.id}','column_spacing_ft',parseFloat(this.value))"/>
          </div>` : b.column_mode==='manual' ? `
          <div class="form-group">
            <label>Column Count</label>
            <input type="number" value="${b.column_count_manual||1}" min="1" max="10" step="1"
              onchange="updateBldg('${b.id}','column_count_manual',parseInt(this.value))"/>
          </div>
          <div class="form-group">
            <label>Positions (ft, comma-sep)</label>
            <input type="text" value="${b.column_positions_manual||''}" placeholder="e.g. 10,30"
              onchange="updateBldg('${b.id}','column_positions_manual',this.value)"/>
          </div>` : '<div></div><div></div>'}
        </div>

        ${b.include_back_wall ? `
        <div class="form-group" style="max-width:220px;margin-bottom:10px">
          <label>Front Column Position (ft from left end)</label>
          <input type="number" value="${b.front_col_position_ft||0}" min="0" max="100" step="0.5"
            onchange="updateBldg('${b.id}','front_col_position_ft',parseFloat(this.value))"/>
          <div style="font-size:10px;color:#888;margin-top:2px">Back col fixed at 19" from right end when back wall enabled</div>
        </div>` : ''}

        <!-- Angled Purlins -->
        <div style="display:flex;gap:20px;margin-bottom:10px;align-items:center">
          <label class="check-label">
            <input type="checkbox" ${b.angled_purlins?'checked':''}
              onchange="updateBldg('${b.id}','angled_purlins',this.checked);renderBuildingForms()"/>
            Angled Purlins
          </label>
          ${b.angled_purlins ? `
          <div class="form-group" style="margin-bottom:0;max-width:160px">
            <label>Purlin Angle (deg)</label>
            <input type="number" value="${b.purlin_angle_deg||15}" min="5" max="45" step="0.5"
              onchange="updateBldg('${b.id}','purlin_angle_deg',parseFloat(this.value))"/>
          </div>
          <div style="font-size:10px;color:#f08c00;background:#fff8e1;padding:4px 8px;border-radius:4px;max-width:280px">
            ⚠ P6 end plates (9"×15") will replace P2 end caps (9"×24"). All clips same angle, no mirroring.
          </div>` : ''}
        </div>

        <!-- Rebar stick config -->
        ${b.include_rafter_rebar ? `
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px;max-width:440px">
          <div class="form-group">
            <label>Max Rebar Stick (ft)</label>
            <input type="number" value="${b.rebar_max_stick_ft||20}" min="5" max="40" step="1"
              onchange="updateBldg('${b.id}','rebar_max_stick_ft',parseFloat(this.value))"/>
            <div style="font-size:10px;color:#888;margin-top:2px">Default: 20'</div>
          </div>
          <div class="form-group">
            <label>End Gap (ft)</label>
            <input type="number" value="${b.rebar_end_gap_ft||5}" min="0" max="20" step="0.5"
              onchange="updateBldg('${b.id}','rebar_end_gap_ft',parseFloat(this.value))"/>
            <div style="font-size:10px;color:#888;margin-top:2px">Gap from rafter end to first rebar</div>
          </div>
        </div>` : ''}

        <!-- Splice override -->
        <div class="form-group" style="max-width:220px;margin-bottom:10px">
          <label>Splice Location Override (ft)</label>
          <input type="number" value="${b.splice_location_ft||0}" min="0" max="100" step="0.5"
            onchange="updateBldg('${b.id}','splice_location_ft',parseFloat(this.value))"/>
          <div style="font-size:10px;color:#888;margin-top:2px">0 = auto-calculate</div>
        </div>

        <!-- Purlin Type, Roofing Overhang, Above Grade, Cut Allowance -->
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:10px;margin-bottom:10px">
          <div class="form-group">
            <label>Purlin Type</label>
            <select onchange="updateBldg('${b.id}','purlin_type',this.value)">
              <option value="Z" ${(b.purlin_type||'Z')==='Z'?'selected':''}>Z-Purlin</option>
              <option value="C" ${b.purlin_type==='C'?'selected':''}>C-Purlin</option>
            </select>
            <div style="font-size:10px;color:#888;margin-top:2px">Z or C channel purlins</div>
          </div>
          <div class="form-group">
            <label>Roofing Overhang (ft)</label>
            <input type="number" value="${b.roofing_overhang_ft||0.5}" min="0" max="5" step="0.25"
              onchange="updateBldg('${b.id}','roofing_overhang_ft',parseFloat(this.value))"/>
            <div style="font-size:10px;color:#888;margin-top:2px">Panel overhang past eave purlin</div>
          </div>
          <div class="form-group">
            <label>Above-Grade Height (ft)</label>
            <input type="number" value="${b.above_grade_ft||8}" min="0" max="20" step="0.5"
              onchange="updateBldg('${b.id}','above_grade_ft',parseFloat(this.value))"/>
            <div style="font-size:10px;color:#888;margin-top:2px">Column height above finished grade</div>
          </div>
          <div class="form-group">
            <label>Cut Allowance (in)</label>
            <input type="number" value="${b.cut_allowance_in||6}" min="0" max="24" step="1"
              onchange="updateBldg('${b.id}','cut_allowance_in',parseFloat(this.value))"/>
            <div style="font-size:10px;color:#888;margin-top:2px">Extra length for field cuts</div>
          </div>
        </div>

      </details>

      <!-- Row 5: Hardware & Connections -->
      <details style="margin-bottom:8px">
        <summary style="cursor:pointer;font-size:12px;color:var(--tf-blue-m);font-weight:600;padding:4px 0">
          ▸ Hardware & Connections
        </summary>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:10px">
          <div class="form-group">
            <label>Rafter-to-Purlin Straps/Rafter</label>
            <input type="number" value="${b.straps_per_rafter||4}" min="0" max="20"
              onchange="updateBldg('${b.id}','straps_per_rafter',parseInt(this.value))"/>
            <div style="font-size:10px;color:#888;margin-top:2px">1 purlin in from each eave × 2 = 4 default</div>
          </div>
          <div class="form-group">
            <label>Strap Length (in)</label>
            <input type="number" value="${b.strap_length_in||28}" min="12" max="60"
              onchange="updateBldg('${b.id}','strap_length_in',parseFloat(this.value))"/>
            <div style="font-size:10px;color:#888;margin-top:2px">Default: 28"</div>
          </div>
          <div class="form-group">
            <label>Welding Consumables ($/5,000 sqft)</label>
            <input type="number" value="${b.welding_cost_per_5000sqft||300}" min="0" step="10"
              onchange="updateBldg('${b.id}','welding_cost_per_5000sqft',parseFloat(this.value))"/>
            <div style="font-size:10px;color:#888;margin-top:2px">Wire, gas, cold galvanize paint</div>
          </div>
        </div>
        <div style="display:flex;gap:20px;margin-top:8px;flex-wrap:wrap">
          <label class="check-label">
            <input type="checkbox" ${b.include_trim?'checked':''}
              onchange="updateBldg('${b.id}','include_trim',this.checked)"/>
            Include Trim (J-Channel)
          </label>
          <label class="check-label">
            <input type="checkbox" ${b.include_consumables?'checked':''}
              onchange="updateBldg('${b.id}','include_consumables',this.checked)"/>
            Include Consumables
          </label>
          <label class="check-label">
            <input type="checkbox" ${b.include_labor?'checked':''}
              onchange="updateBldg('${b.id}','include_labor',this.checked)"/>
            Include Fabrication Labor
          </label>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px">
          <div class="form-group">
            <label>Consumables Rate ($/5,000 sqft)</label>
            <input type="number" value="${b.welding_cost_per_5000sqft||300}" min="0" step="10"
              onchange="updateBldg('${b.id}','welding_cost_per_5000sqft',parseFloat(this.value))"/>
            <div style="font-size:10px;color:#888;margin-top:2px">Wire, gas, cold galvanize paint</div>
          </div>
          <div class="form-group">
            <label>Labor Daily Rate ($)</label>
            <input type="number" value="${b.labor_daily_rate||960}" min="100" step="10"
              onchange="updateBldg('${b.id}','labor_daily_rate',parseFloat(this.value))"/>
            <div style="font-size:10px;color:#888;margin-top:2px">Default: $960/day</div>
          </div>
        </div>
      </details>

      <!-- Row 5b: Wall Options -->
      <details style="margin-bottom:8px">
        <summary style="cursor:pointer;font-size:12px;color:var(--tf-blue-m);font-weight:600;padding:4px 0">
          ▸ Wall Panels & Girts
        </summary>
        <div style="font-size:10px;color:#888;margin-bottom:8px;margin-top:6px">
          Wall height = clear height + 1'-8" (rafter + purlin − ground clearance). End walls use peak height.
          Girt spacing matches roof purlin auto-calc unless overridden.
        </div>
        <div style="display:flex;gap:20px;margin-bottom:10px;flex-wrap:wrap">
          <label class="check-label">
            <input type="checkbox" ${b.include_back_wall?'checked':''}
              onchange="updateBldg('${b.id}','include_back_wall',this.checked)"/>
            Back Wall (1 long rear wall)
          </label>
          <label class="check-label">
            <input type="checkbox" ${b.include_end_walls?'checked':''}
              onchange="updateBldg('${b.id}','include_end_walls',this.checked)"/>
            End Walls (2 short gable ends)
          </label>
          <label class="check-label">
            <input type="checkbox" ${b.include_side_walls?'checked':''}
              onchange="updateBldg('${b.id}','include_side_walls',this.checked)"/>
            Side Walls (both long sides)
          </label>
        </div>
        <div class="form-group" style="max-width:220px">
          <label>Wall Girt Spacing Override (ft OC)</label>
          <input type="number" placeholder="Leave blank = auto (same as roof)" min="1" max="10" step="0.5"
            value="${b.wall_girt_spacing_override||''}"
            onchange="updateBldg('${b.id}','wall_girt_spacing_override',parseFloat(this.value)||null)"/>
        </div>
        </div>
      </details>

      <!-- Row 6: Coil Price Overrides -->
      <details>
        <summary style="cursor:pointer;font-size:12px;color:var(--tf-blue-m);font-weight:600;padding:4px 0">
          ▸ Price/LB Overrides (leave blank to use defaults)
        </summary>
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:10px">
          ${[
            ['c_section_23','C1: 23" 10GA','0.82'],
            ['z_purlin_20','C2: 12GA Purlin','0.82'],
            ['angle_4_16ga','C3: 16GA Angle','0.86'],
            ['spartan_rib_48','C4: 29GA Panel','0.795'],
            ['plate_6_10ga','C5: 10GA Plate 6"','0.82'],
            ['plate_9_10ga','C6: 10GA Plate 9"','0.82'],
            ['strap_15_10ga','C7: 10GA Strap','0.82'],
          ].map(([cid,lbl,def]) => `
          <div class="form-group">
            <label style="font-size:10px">${lbl}</label>
            <div style="display:flex;align-items:center;gap:4px">
              <span style="font-size:11px">$</span>
              <input type="number" placeholder="${def}" min="0" step="0.001"
                value="${(b.coil_prices&&b.coil_prices[cid])||''}"
                style="width:70px"
                onchange="(function(v){if(!b.coil_prices)b.coil_prices={};updateBldgCoilPrice('${b.id}','${cid}',v)})(this.value)"/>
              <span style="font-size:10px;color:#888">/lb</span>
            </div>
          </div>`).join('')}
        </div>
      </details>

    </div>
  </div>`;
}

function updateBldg(id, field, value) {
  const b = buildings.find(x => x.id === id);
  if (b) {
    b[field] = value;
    // Keep legacy 'name' in sync with building_name
    if (field === 'building_name') b.name = value;
  }
  renderBuildingList();
}

function updateBldgCoilPrice(id, coilId, val) {
  const b = buildings.find(x => x.id === id);
  if (!b) return;
  if (!b.coil_prices) b.coil_prices = {};
  if (val === '' || val === null) {
    delete b.coil_prices[coilId];
  } else {
    b.coil_prices[coilId] = parseFloat(val);
  }
}

// ─────────────────────────────────────────────
// CALCULATE
// ─────────────────────────────────────────────
async function calculate() {
  const project = {
    name: document.getElementById('proj_name').value || 'Project',
    job_code: document.getElementById('proj_jobcode').value || 'PROJ-00',
    address: document.getElementById('proj_address').value || '',
    city: document.getElementById('proj_city').value || '',
    state: document.getElementById('proj_state').value,
    zip_code: document.getElementById('proj_zip').value || '',
    customer_name: document.getElementById('proj_customer').value || '',
    quote_date: document.getElementById('proj_date').value || '',
    wind_speed_mph: parseFloat(document.getElementById('proj_wind').value) || 115,
    footing_depth_ft: parseFloat(document.getElementById('proj_footing').value) || 10,
    markup_pct: parseFloat(document.getElementById('proj_markup').value) || 35,
  };

  const payload = { project, buildings };

  try {
    const res = await fetch('/api/calculate', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (data.error) {
      showToast('Calculation error:  + data.error);
      return;
    }
    currentBOM = data;
    priceOverrides = {};  // Reset overrides on new calc
    renderBOM(data);
    renderPricingTab();
    // Switch to BOM tab
    document.querySelectorAll('.tab-content').forEach(t => t.classList.add('hidden'));
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.getElementById('tab-bom').classList.remove('hidden');
    document.querySelectorAll('.tab')[1].classList.add('active');
  } catch(e) {
    showToast('Error: ' + e.message, 'error');
  }
}

// ─────────────────────────────────────────────
// RENDER BOM
// ─────────────────────────────────────────────
function renderBOM(data) {
  const el = document.getElementById('bom-content');

  const totalLaborSell = data.total_labor_sell_price || 0;
  const totalFabDays = data.total_labor_days || 0;
  let html = `
  <div class="stats-grid">
    <div class="stat-card">
      <div class="stat-label">Project</div>
      <div class="stat-value" style="font-size:14px">${data.project.name || '—'}</div>
      <div class="stat-unit">${data.project.job_code || ''}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Total Weight</div>
      <div class="stat-value">${(data.total_weight_lbs||0).toLocaleString()}</div>
      <div class="stat-unit">LBS</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Material Cost</div>
      <div class="stat-value" style="color:var(--tf-green)">$${(data.total_material_cost||0).toLocaleString('en-US',{minimumFractionDigits:2})}</div>
      <div class="stat-unit">before markup</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Total Sell Price</div>
      <div class="stat-value" style="color:var(--tf-red)">$${(data.total_sell_price||0).toLocaleString('en-US',{minimumFractionDigits:2})}</div>
      <div class="stat-unit">materials + labor</div>
    </div>
    ${totalLaborSell > 0 ? `
    <div class="stat-card">
      <div class="stat-label">Fabrication Labor</div>
      <div class="stat-value" style="color:var(--tf-blue)">$${totalLaborSell.toLocaleString('en-US',{minimumFractionDigits:2})}</div>
      <div class="stat-unit">incl. 10% overhead + markup</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Est. Fab Days</div>
      <div class="stat-value" style="color:var(--tf-blue)">${totalFabDays}</div>
      <div class="stat-unit">shop days (4-man crew)</div>
    </div>
    ` : ''}
    <div class="stat-card">
      <div class="stat-label">Buildings</div>
      <div class="stat-value">${data.buildings.length}</div>
      <div class="stat-unit">total structures</div>
    </div>
  </div>

  <div class="btn-group" style="margin-bottom:16px">
    <button class="btn btn-green" onclick="downloadExcel()">📊 Download Excel BOM</button>
    <button class="btn btn-red" onclick="downloadPDF()">📄 Download PDF Quote</button>
    <button class="btn btn-primary" onclick="saveProjectManual()">💾 Save Project</button>
    <button class="btn btn-gold" style="margin-left:auto" onclick="sendToTCQuote()">🏗️ Send to TC Construction Quote →</button>
  </div>
  `;

  // Per building
  for (let bi = 0; bi < data.buildings.length; bi++) {
    const bldg = data.buildings[bi];
    const geo = bldg.geometry || {};
    const bldgLabel = bldg.building_name || ('Building ' + (bi + 1));
    const purlinAuto = geo.purlin_auto ? ' (auto)' : ' (override)';
    html += `
    <div class="card" style="margin-bottom:20px">
      <div class="card-hdr" style="background:var(--tf-blue)">
        <span class="icon">🏗️</span>
        ${bldgLabel} — ${(bldg.type||'').toUpperCase()}
        <span style="margin-left:auto;font-size:11px;opacity:.85">
          ${bldg.width_ft}' × ${bldg.length_ft}' &nbsp;|&nbsp;
          ${geo.n_frames || '—'} frames · ${geo.n_bays || '—'} bays · bay=${geo.bay_size_ft || '—'}' &nbsp;|&nbsp;
          ${geo.n_struct_cols || '—'} cols · ${geo.n_rafters || '—'} rafters &nbsp;|&nbsp;
          Purlin: ${geo.purlin_spacing_ft || '—'}' OC × ${geo.n_purlin_lines || '—'} lines${purlinAuto} &nbsp;|&nbsp;
          Col Ht: ${geo.col_ht_ft || '—'}' · Pitch: ${geo.slope_deg || '—'}°
        </span>
      </div>
      <div class="card-body" style="padding:0">
        <table class="bom-table">
          <thead>
            <tr>
              <th>Category</th>
              <th>Description</th>
              <th style="text-align:right">Qty</th>
              <th>Unit</th>
              <th style="text-align:right">Wt (LBS)</th>
              <th style="text-align:right">Unit Cost</th>
              <th style="text-align:right">Total Cost</th>
              <th>Notes</th>
            </tr>
          </thead>
          <tbody>`;

    let lastCat = null;
    for (const item of bldg.line_items) {
      if (item.category !== lastCat) {
        lastCat = item.category;
        html += `<tr class="cat-row"><td colspan="8">${item.category}</td></tr>`;
      }
      const qty = typeof item.qty === 'number' ? item.qty.toLocaleString('en-US',{maximumFractionDigits:2}) : item.qty;
      const wt = item.total_weight_lbs ? item.total_weight_lbs.toLocaleString('en-US',{maximumFractionDigits:1}) : '—';
      const uc = item.unit_cost ? '$' + item.unit_cost.toFixed(4) : '—';
      const tc = item.total_cost ? '$' + item.total_cost.toLocaleString('en-US',{minimumFractionDigits:2}) : '—';
      html += `
        <tr>
          <td></td>
          <td>${item.description}</td>
          <td style="text-align:right;font-weight:600">${qty}</td>
          <td>${item.unit}</td>
          <td style="text-align:right">${wt}</td>
          <td style="text-align:right">${uc}</td>
          <td style="text-align:right;font-weight:600">${tc}</td>
          <td style="font-size:10px;color:#888">${item.notes||''}</td>
        </tr>`;
    }

    html += `
          <tr class="total-row">
            <td colspan="4">TOTAL MATERIAL COST</td>
            <td style="text-align:right">${(bldg.total_weight_lbs||0).toLocaleString('en-US',{maximumFractionDigits:0})} LBS</td>
            <td></td>
            <td style="text-align:right">$${(bldg.total_material_cost||0).toLocaleString('en-US',{minimumFractionDigits:2})}</td>
            <td></td>
          </tr>
          ${bldg.labor_sell_price > 0 ? `
          <tr style="background:#EEF5FF!important">
            <td colspan="4" style="color:var(--tf-blue);font-weight:700">
              FABRICATION LABOR
              <span style="font-size:10px;font-weight:400;margin-left:8px;color:#666">
                ${(bldg.geometry.labor||{}).total_fab_days||0} shop days ·
                ${(bldg.geometry.labor||{}).days_columns||0}d columns +
                ${(bldg.geometry.labor||{}).days_rafters||0}d rafters /
                ${(bldg.geometry.labor||{}).days_purlins||0}d purlins /
                ${(bldg.geometry.labor||{}).days_panels||0}d panels /
                ${(bldg.geometry.labor||{}).days_angle||0}d angle
                (max stream = ${(bldg.geometry.labor||{}).box_stream_days||0}d box)
              </span>
            </td>
            <td></td><td></td>
            <td style="text-align:right;color:var(--tf-blue);font-weight:700">$${bldg.labor_raw_cost.toLocaleString('en-US',{minimumFractionDigits:2})}</td>
            <td style="font-size:10px;color:#888">raw (before markup)</td>
          </tr>` : ''}
          <tr class="sell-row">
            <td colspan="6" style="text-align:right">SELL PRICE (materials + labor)</td>
            <td style="text-align:right">$${((bldg.total_sell_price||0)+(bldg.labor_sell_price||0)).toLocaleString('en-US',{minimumFractionDigits:2})}</td>
            <td></td>
          </tr>
        </tbody>
        </table>
      </div>
    </div>`;
  }

  el.innerHTML = html;
}

// ─────────────────────────────────────────────
// SEND TO TC QUOTE
// ─────────────────────────────────────────────
function sendToTCQuote() {
  if (!currentBOM) { showToast('Please calculate BOM first.', 'info'); return; }
  // Use adjusted totals if price overrides / manual items exist
  const totals = getAdjustedTotals();
  const sellPrice = (Object.keys(priceOverrides).length > 0 || manualItems.length > 0)
    ? totals.grand : (currentBOM.total_sell_price || 0);
  const nCols = (currentBOM.buildings || []).reduce((s, b) => s + (b.geometry?.n_struct_cols || 0), 0);
  const footingDepth = currentBOM.project?.footing_depth_ft || 10;
  const projName = currentBOM.project?.name || '';
  const projCode = currentBOM.project?.job_code || '';
  const width = (currentBOM.buildings || [])[0]?.width_ft || 40;
  const length = (currentBOM.buildings || [])[0]?.length_ft || 180;
  const saQuoteNum = projCode ? 'SA-' + projCode : '';
  const params = new URLSearchParams({
    sa_cost: sellPrice.toFixed(2),
    n_cols: nCols,
    footing: footingDepth,
    proj_name: projName,
    proj_code: projCode,
    sa_quote: saQuoteNum,
    width: width,
    length: length,
  });
  window.open('/tc?' + params.toString(), '_blank');
}

// ─────────────────────────────────────────────
// PRICE OVERRIDES & MANUAL ITEMS
// ─────────────────────────────────────────────

function getAdjustedTotals() {
  // Calculate totals including price overrides and manual items
  if (!currentBOM) return { material: 0, sell: 0, manual: 0, grand: 0 };
  const markup = (parseFloat(document.getElementById('proj_markup')?.value) || 35) / 100;
  let totalMaterial = 0, totalSell = 0;

  for (let bi = 0; bi < currentBOM.buildings.length; bi++) {
    const bldg = currentBOM.buildings[bi];
    for (let li = 0; li < bldg.line_items.length; li++) {
      const item = bldg.line_items[li];
      const key = bi + '_' + li;
      const ov = (priceOverrides[bi] || {})[li];
      if (ov && ov.cost !== undefined) {
        totalMaterial += ov.cost;
        totalSell += (ov.sell !== undefined) ? ov.sell : ov.cost * (1 + markup);
      } else {
        totalMaterial += item.total_cost || 0;
        totalSell += (item.total_cost || 0) * (1 + markup);
      }
    }
    // Add labor
    totalSell += bldg.labor_sell_price || 0;
  }

  // Manual items
  let manualTotal = 0;
  for (const m of manualItems) {
    manualTotal += (m.qty || 0) * (m.sell_price || 0);
  }

  return {
    material: totalMaterial,
    sell: totalSell,
    manual: manualTotal,
    grand: totalSell + manualTotal,
  };
}

function renderPricingTab() {
  const el = document.getElementById('pricing-content');
  if (!currentBOM) {
    el.innerHTML = '<div class="alert alert-info">Run <strong>CALCULATE BOM</strong> first, then use this tab to edit prices.</div>';
    return;
  }

  const markup = (parseFloat(document.getElementById('proj_markup')?.value) || 35) / 100;
  const totals = getAdjustedTotals();

  let html = `
  <div class="stats-grid" id="pricing-summary">
    <div class="stat-card">
      <div class="stat-label">Calculated Material</div>
      <div class="stat-value" style="color:var(--tf-green)">$${(currentBOM.total_material_cost||0).toLocaleString('en-US',{minimumFractionDigits:2})}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Adjusted Material</div>
      <div class="stat-value" style="color:var(--tf-blue)" id="adj-material">$${totals.material.toLocaleString('en-US',{minimumFractionDigits:2})}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Manual Items</div>
      <div class="stat-value" style="color:#7A5C00" id="adj-manual">$${totals.manual.toLocaleString('en-US',{minimumFractionDigits:2})}</div>
    </div>
    <div class="stat-card" style="border:2px solid var(--tf-red)">
      <div class="stat-label">Grand Total (Sell)</div>
      <div class="stat-value" style="color:var(--tf-red)" id="adj-grand">$${totals.grand.toLocaleString('en-US',{minimumFractionDigits:2})}</div>
      <div class="stat-unit">materials + labor + manual</div>
    </div>
  </div>`;

  // Per-building editable table
  for (let bi = 0; bi < currentBOM.buildings.length; bi++) {
    const bldg = currentBOM.buildings[bi];
    const bldgLabel = bldg.building_name || ('Building ' + (bi + 1));
    html += `
    <div class="card" style="margin-bottom:16px">
      <div class="card-hdr" style="background:var(--tf-blue)">
        <span class="icon">🏗️</span> ${bldgLabel} — Price Overrides
      </div>
      <div class="card-body" style="padding:0">
        <table class="bom-table">
          <thead><tr>
            <th>Category</th><th>Description</th>
            <th style="text-align:right">Qty</th><th>Unit</th>
            <th style="text-align:right">Orig Cost</th>
            <th style="text-align:right">New Cost</th>
            <th style="text-align:right">Sell Price</th>
            <th style="text-align:right">Markup %</th>
            <th></th>
          </tr></thead><tbody>`;

    let lastCat = null;
    for (let li = 0; li < bldg.line_items.length; li++) {
      const item = bldg.line_items[li];
      if (item.category !== lastCat) {
        lastCat = item.category;
        html += '<tr class="cat-row"><td colspan="9">' + item.category + '</td></tr>';
      }
      const origCost = item.total_cost || 0;
      const ov = (priceOverrides[bi] || {})[li];
      const isEdited = ov && ov.cost !== undefined;
      const editCost = isEdited ? ov.cost : origCost;
      const editSell = isEdited && ov.sell !== undefined ? ov.sell : editCost * (1 + markup);
      const markupPct = editCost > 0 ? ((editSell / editCost - 1) * 100).toFixed(1) : '—';
      const qty = typeof item.qty === 'number' ? item.qty.toLocaleString('en-US',{maximumFractionDigits:2}) : item.qty;

      html += `<tr${isEdited?' style="background:#FFF8E0"':''}>
        <td></td>
        <td>${item.description}</td>
        <td style="text-align:right">${qty}</td>
        <td>${item.unit}</td>
        <td style="text-align:right;${isEdited?'text-decoration:line-through;color:#bbb':''}">$${origCost.toLocaleString('en-US',{minimumFractionDigits:2})}</td>
        <td style="text-align:right">
          <input type="number" value="${editCost.toFixed(2)}" step="0.01" style="width:100px;padding:3px 6px;font-size:12px;text-align:right;border:1px solid ${isEdited?'#C89A2E':'#ddd'};border-radius:3px"
            onchange="overrideCost(${bi},${li},parseFloat(this.value))" oninput="liveUpdateTotals()"/>
        </td>
        <td style="text-align:right">
          <input type="number" value="${editSell.toFixed(2)}" step="0.01" style="width:100px;padding:3px 6px;font-size:12px;text-align:right;border:1px solid ${isEdited?'#C89A2E':'#ddd'};border-radius:3px"
            onchange="overrideSell(${bi},${li},parseFloat(this.value))" oninput="liveUpdateTotals()"/>
        </td>
        <td style="text-align:right;font-size:11px;color:#888">${markupPct}%</td>
        <td>${isEdited?'<button style="border:none;background:none;cursor:pointer;font-size:14px" title="Reset to calculated" onclick="resetOverride('+bi+','+li+')">↩</button>':''}</td>
      </tr>`;
    }
    html += '</tbody></table></div></div>';
  }

  // ── Manual Line Items Section ──────────────
  html += `
  <div class="card" style="margin-top:16px">
    <div class="card-hdr" style="background:var(--tf-amber);color:#1C1C2E">
      <span class="icon">➕</span> Manual Line Items (Trim, Hardware, Freight, etc.)
    </div>
    <div class="card-body">
      <table class="bom-table" id="manual-items-table">
        <thead><tr>
          <th>Category</th><th>Description</th>
          <th style="text-align:right">Qty</th><th>Unit</th>
          <th style="text-align:right">Unit Price</th>
          <th style="text-align:right">Extended</th>
          <th></th>
        </tr></thead>
        <tbody>`;

  for (let mi = 0; mi < manualItems.length; mi++) {
    const m = manualItems[mi];
    const ext = (m.qty || 0) * (m.sell_price || 0);
    html += `<tr>
      <td>
        <select style="font-size:11px;padding:3px;border:1px solid #ddd;border-radius:3px" onchange="manualItems[${mi}].category=this.value;scheduleSave()">
          <option value="Trim" ${m.category==='Trim'?'selected':''}>Trim</option>
          <option value="Hardware" ${m.category==='Hardware'?'selected':''}>Hardware</option>
          <option value="Freight" ${m.category==='Freight'?'selected':''}>Freight</option>
          <option value="Fasteners" ${m.category==='Fasteners'?'selected':''}>Fasteners</option>
          <option value="Accessories" ${m.category==='Accessories'?'selected':''}>Accessories</option>
          <option value="Other" ${m.category==='Other'?'selected':''}>Other</option>
        </select>
      </td>
      <td><input type="text" value="${(m.description||'').replace(/"/g,'&quot;')}" style="font-size:12px;padding:3px 6px;border:1px solid #ddd;border-radius:3px;width:100%"
        onchange="manualItems[${mi}].description=this.value;scheduleSave()"/></td>
      <td style="text-align:right"><input type="number" value="${m.qty||0}" step="0.01" style="width:70px;font-size:12px;padding:3px 6px;text-align:right;border:1px solid #ddd;border-radius:3px"
        onchange="manualItems[${mi}].qty=parseFloat(this.value)||0;renderPricingTab()" oninput="liveUpdateTotals()"/></td>
      <td>
        <select style="font-size:11px;padding:3px;border:1px solid #ddd;border-radius:3px" onchange="manualItems[${mi}].unit=this.value;scheduleSave()">
          <option value="EA" ${m.unit==='EA'?'selected':''}>EA</option>
          <option value="LF" ${m.unit==='LF'?'selected':''}>LF</option>
          <option value="SQ" ${m.unit==='SQ'?'selected':''}>SQ</option>
          <option value="LOT" ${m.unit==='LOT'?'selected':''}>LOT</option>
          <option value="LBS" ${m.unit==='LBS'?'selected':''}>LBS</option>
        </select>
      </td>
      <td style="text-align:right"><input type="number" value="${(m.sell_price||0).toFixed(2)}" step="0.01" style="width:90px;font-size:12px;padding:3px 6px;text-align:right;border:1px solid #ddd;border-radius:3px"
        onchange="manualItems[${mi}].sell_price=parseFloat(this.value)||0;renderPricingTab()" oninput="liveUpdateTotals()"/></td>
      <td style="text-align:right;font-weight:600">$${ext.toLocaleString('en-US',{minimumFractionDigits:2})}</td>
      <td><button class="btn btn-red btn-sm" style="padding:2px 8px;font-size:11px" onclick="manualItems.splice(${mi},1);renderPricingTab()">✕</button></td>
    </tr>`;
  }

  html += `</tbody></table>
      <div style="display:flex;gap:8px;margin-top:10px;flex-wrap:wrap">
        <button class="btn btn-gold btn-sm" onclick="addManualItem('Trim','','LF')">+ Trim</button>
        <button class="btn btn-gold btn-sm" onclick="addManualItem('Hardware','','EA')">+ Hardware</button>
        <button class="btn btn-gold btn-sm" onclick="addManualItem('Freight','Freight & Delivery','LOT')">+ Freight</button>
        <button class="btn btn-gold btn-sm" onclick="addManualItem('Fasteners','','EA')">+ Fasteners</button>
        <button class="btn btn-outline btn-sm" onclick="addManualItem('Other','','EA')">+ Other</button>
      </div>
    </div>
  </div>`;

  el.innerHTML = html;
}

function overrideCost(bi, li, val) {
  if (!priceOverrides[bi]) priceOverrides[bi] = {};
  const markup = (parseFloat(document.getElementById('proj_markup')?.value) || 35) / 100;
  const existing = priceOverrides[bi][li] || {};
  priceOverrides[bi][li] = { cost: val, sell: existing.sell !== undefined ? existing.sell : val * (1 + markup) };
  scheduleSave();
  // Don't re-render entire tab to preserve focus — just update totals
  liveUpdateTotals();
}

function overrideSell(bi, li, val) {
  if (!priceOverrides[bi]) priceOverrides[bi] = {};
  const existing = priceOverrides[bi][li] || {};
  const item = currentBOM.buildings[bi].line_items[li];
  const cost = existing.cost !== undefined ? existing.cost : (item.total_cost || 0);
  priceOverrides[bi][li] = { cost: cost, sell: val };
  scheduleSave();
  liveUpdateTotals();
}

function resetOverride(bi, li) {
  if (priceOverrides[bi]) {
    delete priceOverrides[bi][li];
    if (Object.keys(priceOverrides[bi]).length === 0) delete priceOverrides[bi];
  }
  scheduleSave();
  renderPricingTab();
}

function addManualItem(category, description, unit) {
  manualItems.push({
    category: category || 'Other',
    description: description || '',
    qty: 1,
    unit: unit || 'EA',
    sell_price: 0,
    notes: '',
  });
  renderPricingTab();
}

function liveUpdateTotals() {
  const totals = getAdjustedTotals();
  const fmt = (n) => '$' + n.toLocaleString('en-US',{minimumFractionDigits:2});
  const matEl = document.getElementById('adj-material');
  const manEl = document.getElementById('adj-manual');
  const grandEl = document.getElementById('adj-grand');
  if (matEl) matEl.textContent = fmt(totals.material);
  if (manEl) manEl.textContent = fmt(totals.manual);
  if (grandEl) grandEl.textContent = fmt(totals.grand);
}

function scheduleSave() {
  clearTimeout(_autoSaveTimer);
  _autoSaveTimer = setTimeout(autoSaveProject, 2000);
}

let currentVersion = 0;  // Current project version number

async function autoSaveProject() {
  if (!currentBOM) return;
  const jobCode = document.getElementById('proj_jobcode')?.value?.trim();
  if (!jobCode) return;
  const payload = {
    job_code: jobCode,
    project: currentBOM.project,
    buildings: buildings,
    bom_data: currentBOM,
    price_overrides: priceOverrides,
    manual_items: manualItems,
  };
  try {
    const resp = await fetch('/api/project/save', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(payload),
    });
    const result = await resp.json();
    if (result.ok && result.version) {
      currentVersion = result.version;
      updateVersionBadge();
    }
    console.log('[AutoSave] Project saved:', jobCode, 'v' + (result.version || '?'));
  } catch(e) { console.warn('[AutoSave] Failed:', e); }
}

async function saveProjectManual() {
  if (!currentBOM) { showToast('Please calculate BOM first.', 'info'); return; }
  const jobCode = document.getElementById('proj_jobcode')?.value?.trim();
  if (!jobCode) { showToast('Please enter a Job Code first.', 'info'); return; }
  await autoSaveProject();
  showToast('Project saved as v' + currentVersion + ': ' + jobCode, 'success');
  loadRecentProjects();
}

function updateVersionBadge() {
  const badge = document.getElementById('version-badge');
  if (badge && currentVersion > 0) {
    badge.textContent = 'v' + currentVersion;
    badge.style.display = 'inline-block';
  }
}

async function loadRecentProjects() {
  try {
    const resp = await fetch('/api/projects');
    const data = await resp.json();
    const sel = document.getElementById('recent_projects');
    if (!sel) return;
    sel.innerHTML = '<option value="">— Recent Projects —</option>';
    for (const p of (data.projects || [])) {
      const vLabel = p.n_versions > 1 ? ' [' + p.n_versions + ' revisions]' : '';
      const label = p.job_code + (p.project_name ? ' — ' + p.project_name : '') +
                    ' v' + (p.version || 1) + vLabel +
                    (p.saved_at ? ' (' + p.saved_at.slice(0,10) + ')' : '');
      sel.innerHTML += '<option value="' + p.job_code + '">' + label + '</option>';
    }
  } catch(e) { console.warn('Failed to load projects:', e); }
}

async function loadProject(jobCode, version) {
  if (!jobCode) return;
  try {
    const payload = { job_code: jobCode };
    if (version) payload.version = version;
    const resp = await fetch('/api/project/load', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(payload),
    });
    const result = await resp.json();
    if (!result.ok) { showToast('Load failed: ' + (result.error||'unknown'), 'error'); return; }
    const d = result.data;

    // Restore project info fields
    if (d.project) {
      const p = d.project;
      if (p.name) document.getElementById('proj_name').value = p.name;
      if (p.customer_name) document.getElementById('proj_customer').value = p.customer_name;
      if (p.address) document.getElementById('proj_address').value = p.address;
      if (p.city) document.getElementById('proj_city').value = p.city;
      if (p.state) document.getElementById('proj_state').value = p.state;
      if (p.zip_code) document.getElementById('proj_zip').value = p.zip_code;
      if (p.quote_date) document.getElementById('proj_date').value = p.quote_date;
      if (p.wind_speed_mph) document.getElementById('proj_wind').value = p.wind_speed_mph;
      if (p.footing_depth_ft) document.getElementById('proj_footing').value = p.footing_depth_ft;
      if (p.markup_pct) document.getElementById('proj_markup').value = p.markup_pct;
    }
    if (d.job_code) document.getElementById('proj_jobcode').value = d.job_code;

    // Restore buildings
    if (d.buildings && d.buildings.length > 0) {
      buildings = d.buildings;
      bldgCounter = buildings.length;
      renderBuildingList();
      renderBuildingForms();
    }

    // Restore BOM data
    if (d.bom_data) {
      currentBOM = d.bom_data;
      renderBOM(currentBOM);
    }

    // Restore price overrides & manual items
    priceOverrides = d.price_overrides || {};
    manualItems = d.manual_items || [];
    currentVersion = d.version || 1;
    updateVersionBadge();
    if (currentBOM) renderPricingTab();

    showToast('Project loaded: ' + jobCode + ' (v' + currentVersion + ')', 'success');
  } catch(e) { showToast('Load error: ' + e.message, 'error'); }
}

async function showRevisionHistory() {
  const jobCode = document.getElementById('proj_jobcode')?.value?.trim();
  if (!jobCode) { showToast('Enter a Job Code or load a project first.', 'info'); return; }
  try {
    const resp = await fetch('/api/project/revisions', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ job_code: jobCode }),
    });
    const result = await resp.json();
    if (!result.ok || !result.revisions.length) {
      showToast('No revisions found for ' + jobCode, 'info');
      return;
    }
    // Render revision history in a modal-style overlay
    let html = '<div id="revision-overlay" style="position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);z-index:9999;display:flex;align-items:center;justify-content:center" onclick="if(event.target===this)this.remove()">';
    html += '<div style="background:#fff;border-radius:10px;padding:24px;max-width:700px;width:90%;max-height:80vh;overflow-y:auto;box-shadow:0 8px 32px rgba(0,0,0,0.3)">';
    html += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">';
    html += '<h2 style="font-size:16px;color:#1F4E79;margin:0">📋 Revision History — ' + jobCode + '</h2>';
    html += '<button onclick="document.getElementById(\'revision-overlay\').remove()" style="border:none;background:none;font-size:20px;cursor:pointer;color:#888">✕</button>';
    html += '</div>';

    // Compare selector
    html += '<div style="background:#F0F4FA;border-radius:6px;padding:12px;margin-bottom:16px">';
    html += '<div style="font-size:11px;font-weight:700;color:#1F4E79;text-transform:uppercase;margin-bottom:8px">Compare Versions</div>';
    html += '<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">';
    html += '<select id="compare_va" style="padding:5px 8px;font-size:12px;border:1px solid #ccc;border-radius:3px">';
    for (const r of result.revisions) {
      html += '<option value="' + r.version + '"' + (r.version === 1 ? ' selected' : '') + '>v' + r.version + '</option>';
    }
    html += '</select>';
    html += '<span style="font-size:12px;color:#888">vs</span>';
    html += '<select id="compare_vb" style="padding:5px 8px;font-size:12px;border:1px solid #ccc;border-radius:3px">';
    for (const r of result.revisions) {
      html += '<option value="' + r.version + '"' + (r.version === result.revisions[result.revisions.length-1].version ? ' selected' : '') + '>v' + r.version + '</option>';
    }
    html += '</select>';
    html += '<button class="btn btn-primary btn-sm" onclick="compareVersions(\'' + jobCode + '\')">🔍 Compare</button>';
    html += '</div>';
    html += '<div id="compare-results" style="margin-top:12px"></div>';
    html += '</div>';

    // Version list
    html += '<table style="width:100%;border-collapse:collapse;font-size:12px">';
    html += '<tr style="background:#1F4E79;color:#fff"><th style="padding:8px;text-align:left">Version</th><th style="padding:8px">Saved</th><th style="padding:8px">By</th><th style="padding:8px;text-align:right">Sell Total</th><th style="padding:8px;text-align:center">Overrides</th><th style="padding:8px"></th></tr>';
    for (const r of result.revisions.reverse()) {
      const isCurrent = r.version === currentVersion;
      html += '<tr style="border-bottom:1px solid #eee;' + (isCurrent ? 'background:#FFF8E0' : '') + '">';
      html += '<td style="padding:8px;font-weight:700;color:#1F4E79">v' + r.version + (isCurrent ? ' ← current' : '') + '</td>';
      html += '<td style="padding:8px;color:#888">' + (r.saved_at || '').slice(0, 16).replace('T', ' ') + '</td>';
      html += '<td style="padding:8px">' + (r.saved_by || '—') + '</td>';
      html += '<td style="padding:8px;text-align:right;font-weight:600">$' + (r.total_sell || 0).toLocaleString('en-US',{minimumFractionDigits:2}) + '</td>';
      html += '<td style="padding:8px;text-align:center">' + (r.n_overrides > 0 ? r.n_overrides + ' edits' : '—') + (r.n_manual > 0 ? ' + ' + r.n_manual + ' manual' : '') + '</td>';
      html += '<td style="padding:8px"><button class="btn btn-outline btn-sm" style="padding:3px 10px;font-size:11px" onclick="document.getElementById(\'revision-overlay\').remove();loadProject(\'' + jobCode + '\',' + r.version + ')">Load</button></td>';
      html += '</tr>';
    }
    html += '</table>';
    html += '</div></div>';
    document.body.insertAdjacentHTML('beforeend', html);
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
}

async function compareVersions(jobCode) {
  const va = parseInt(document.getElementById('compare_va')?.value);
  const vb = parseInt(document.getElementById('compare_vb')?.value);
  if (!va || !vb || va === vb) { showToast('Select two different versions.', 'info'); return; }
  const el = document.getElementById('compare-results');
  if (el) el.innerHTML = '<div style="color:#888;font-size:12px">Loading comparison...</div>';
  try {
    const resp = await fetch('/api/project/compare', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ job_code: jobCode, version_a: va, version_b: vb }),
    });
    const result = await resp.json();
    if (!result.ok) { el.innerHTML = '<div style="color:red">Error: ' + (result.error||'') + '</div>'; return; }

    let html = '';
    if (result.diffs.length === 0) {
      html = '<div style="color:#2E7D32;font-weight:600;font-size:12px">✅ No price differences between v' + va + ' and v' + vb + '</div>';
    } else {
      html += '<table style="width:100%;border-collapse:collapse;font-size:11px;margin-top:8px">';
      html += '<tr style="background:#555;color:#fff"><th style="padding:5px">Item</th><th style="padding:5px;text-align:right">v' + va + ' Cost</th><th style="padding:5px;text-align:right">v' + vb + ' Cost</th><th style="padding:5px;text-align:right">Diff</th></tr>';
      for (const d of result.diffs) {
        const diff_val = d.type === 'manual'
          ? (d.ext_b - d.ext_a)
          : (d.sell_b || d.cost_b || 0) - (d.sell_a || d.cost_a || 0);
        const diffColor = diff_val > 0 ? '#C00000' : diff_val < 0 ? '#2E7D32' : '#888';
        const diffSign = diff_val > 0 ? '+' : '';
        const label = d.type === 'manual'
          ? '📦 ' + (d.category || '') + ': ' + (d.description || '?') + (d.added ? ' (NEW)' : '') + (d.removed ? ' (REMOVED)' : '')
          : '🏗️ ' + (d.building || '') + ' — ' + (d.description || '?');
        const val_a = d.type === 'manual' ? d.ext_a : (d.sell_a || d.cost_a || 0);
        const val_b = d.type === 'manual' ? d.ext_b : (d.sell_b || d.cost_b || 0);
        html += '<tr style="border-bottom:1px solid #eee">';
        html += '<td style="padding:4px">' + label + '</td>';
        html += '<td style="padding:4px;text-align:right">$' + val_a.toFixed(2) + '</td>';
        html += '<td style="padding:4px;text-align:right">$' + val_b.toFixed(2) + '</td>';
        html += '<td style="padding:4px;text-align:right;font-weight:700;color:' + diffColor + '">' + diffSign + '$' + diff_val.toFixed(2) + '</td>';
        html += '</tr>';
      }
      // Total row
      const totalDiff = (result.total_sell_b||0) - (result.total_sell_a||0);
      const tdColor = totalDiff > 0 ? '#C00000' : totalDiff < 0 ? '#2E7D32' : '#888';
      html += '<tr style="background:#F0F4FA;font-weight:700"><td style="padding:5px">TOTAL (BOM Sell)</td>';
      html += '<td style="padding:5px;text-align:right">$' + (result.total_sell_a||0).toLocaleString('en-US',{minimumFractionDigits:2}) + '</td>';
      html += '<td style="padding:5px;text-align:right">$' + (result.total_sell_b||0).toLocaleString('en-US',{minimumFractionDigits:2}) + '</td>';
      html += '<td style="padding:5px;text-align:right;color:' + tdColor + '">' + (totalDiff>0?'+':'') + '$' + totalDiff.toFixed(2) + '</td>';
      html += '</tr></table>';
    }
    if (el) el.innerHTML = html;
  } catch(e) { if (el) el.innerHTML = '<div style="color:red">Error: ' + e.message + '</div>'; }
}

// ─────────────────────────────────────────────
// DOWNLOADS
// ─────────────────────────────────────────────
async function downloadExcel() {
  if (!currentBOM) { showToast('Please calculate first.', 'info'); return; }
  const res = await fetch('/api/excel', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(currentBOM),
  });
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `SA_BOM_${currentBOM.project.job_code || 'Quote'}.xlsx`;
  a.click();
}

async function downloadPDF() {
  if (!currentBOM) { showToast('Please calculate first.', 'info'); return; }
  const res = await fetch('/api/pdf', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(currentBOM),
  });
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `SA_Quote_${currentBOM.project.job_code || 'Quote'}.pdf`;
  a.click();
}

// ─────────────────────────────────────────────
// LABELS
// ─────────────────────────────────────────────
async function generateLabels() {
  if (!currentBOM) { showToast('Please calculate a BOM first.', 'info'); return; }
  const payload = {
    bom: currentBOM,
    destination: document.getElementById('lbl_destination').value,
    fabricator: document.getElementById('lbl_fabricator').value,
    qr_base_url: document.getElementById('lbl_qr_url').value,
    grouping: {
      column: parseInt(document.getElementById('grp_column').value)||1,
      rafter: parseInt(document.getElementById('grp_rafter').value)||1,
      purlin: parseInt(document.getElementById('grp_purlin').value)||1,
      strap: parseInt(document.getElementById('grp_strap').value)||10,
    },
  };
  const res = await fetch('/api/labels', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (data.error) { showToast(data.error, 'error'); return; }
  currentLabels = data;
  document.getElementById('labels-preview').innerHTML = `
    <div class="alert alert-success">✅ Generated ${data.count} labels. ZPL file ready to print on Zebra ZT411.</div>
    <div class="labels-wrap">${data.html}</div>
  `;
}

async function downloadZPL() {
  if (!currentLabels || !currentLabels.zpl) { showToast('Please generate labels first.', 'info'); return; }
  const blob = new Blob([currentLabels.zpl], {type:'text/plain'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `SA_Labels_${currentBOM?.project?.job_code || 'Job'}.zpl`;
  a.click();
}

async function downloadLabelsPDF() {
  if (!currentBOM) { showToast('Please calculate BOM first, then generate labels.', 'info'); return; }
  const payload = buildLabelsPayload();
  const res = await fetch('/api/labels/pdf', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload)
  });
  if (!res.ok) { showToast('PDF export failed: ' + await res.text(), 'error'); return; }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `SA_Labels_${currentBOM?.project?.job_code || 'Job'}.pdf`;
  a.click();
  URL.revokeObjectURL(url);
}

async function downloadLabelsCSV() {
  if (!currentBOM) { showToast('Please calculate BOM first, then generate labels.', 'info'); return; }
  const payload = buildLabelsPayload();
  const res = await fetch('/api/labels/csv', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload)
  });
  if (!res.ok) { showToast('CSV export failed: ' + await res.text(), 'error'); return; }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `SA_Labels_${currentBOM?.project?.job_code || 'Job'}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

function buildLabelsPayload() {
  return {
    bom: currentBOM,
    destination: document.getElementById('lbl_destination')?.value || '',
    fabricator:  document.getElementById('lbl_fabricator')?.value || '',
    qr_base_url: document.getElementById('lbl_qr_url')?.value || 'https://structuresamerica.com/shop',
    grouping: {
      column: parseInt(document.getElementById('grp_column')?.value) || 1,
      rafter: parseInt(document.getElementById('grp_rafter')?.value) || 1,
      purlin: parseInt(document.getElementById('grp_purlin')?.value) || 1,
      strap:  parseInt(document.getElementById('grp_strap')?.value)  || 10,
    },
  };
}

// ─────────────────────────────────────────────
// INVENTORY
// ─────────────────────────────────────────────
async function loadInventory() {
  const res = await fetch('/api/inventory');
  const data = await res.json();
  renderInventory(data);
}

function renderInventory(data) {
  const el = document.getElementById('inventory-content');
  let html = `
  <div class="alert alert-info">
    Stock levels are tracked per-coil. Update quantities when material arrives.
    Committed quantities are deducted when a project BOM is locked.
  </div>

  <div class="card">
    <div class="card-hdr"><span class="icon">🔩</span>Coil Inventory</div>
    <div class="card-body" style="padding:0">
    <table class="inv-table">
      <thead>
        <tr>
          <th>Material</th><th>Gauge</th>
          <th style="text-align:right">In Stock (LBS)</th>
          <th style="text-align:right">Committed (LBS)</th>
          <th style="text-align:right">Available (LBS)</th>
          <th style="text-align:right">Min Stock</th>
          <th style="text-align:right">Price/LB</th>
          <th>Lead Time</th>
          <th>Status</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>`;

  // Build per-coil cert count map
  const certsByCoil = {};
  for (const c of (data.mill_certs || [])) {
    const key = c.coil_id || c.material || '';
    certsByCoil[key] = (certsByCoil[key] || 0) + 1;
  }

  let alertsOut = 0, alertsLow = 0;
  for (const [id, coil] of Object.entries(data.coils || {})) {
    const avail = (coil.stock_lbs || 0) - (coil.committed_lbs || 0);
    const minStock = coil.min_stock_lbs || 0;
    const status = avail <= 0 ? 'OUT' : (minStock > 0 && avail < minStock) ? 'LOW' : avail < 2000 ? 'LOW' : 'OK';
    if (status === 'OUT') alertsOut++;
    else if (status === 'LOW') alertsLow++;
    const statusClass = status === 'OK' ? 'stock-ok' : status === 'LOW' ? 'stock-low' : 'stock-out';
    const rowBg = status === 'OUT' ? 'background:#FFF0F0' : status === 'LOW' ? 'background:#FFFBE6' : '';
    const nCerts = certsByCoil[id] || 0;
    const certBadge = nCerts > 0
      ? `<span style="background:#E8F5E9;color:#2E7D32;border-radius:10px;padding:2px 7px;font-size:10px;font-weight:700;cursor:pointer;margin-left:4px"
           onclick="filterCerts('${id}')" title="Show certs for this coil">📜 ${nCerts} cert${nCerts>1?'s':''}</span>`
      : `<span style="color:#bbb;font-size:10px;margin-left:4px">no certs</span>`;
    html += `
      <tr style="${rowBg}">
        <td>${coil.name} ${certBadge}</td>
        <td>${coil.gauge}</td>
        <td style="text-align:right">${(coil.stock_lbs||0).toLocaleString()}</td>
        <td style="text-align:right">${(coil.committed_lbs||0).toLocaleString()}</td>
        <td style="text-align:right;font-weight:600">${avail.toLocaleString()}</td>
        <td style="text-align:right">
          <input type="number" value="${minStock}" min="0" step="100" style="width:80px;padding:3px 6px;font-size:11px;text-align:right;border:1px solid ${minStock>0?'#C89A2E':'#ddd'};border-radius:3px"
            onchange="updateMinStock('${id}', parseFloat(this.value)||0)"/>
        </td>
        <td style="text-align:right">$${coil.price_per_lb}</td>
        <td>${coil.lead_time_weeks} wks</td>
        <td><span class="${statusClass}">${status === 'OUT' ? '🔴 OUT' : status === 'LOW' ? '🟡 LOW' : '🟢 OK'}</span></td>
        <td>
          <input type="number" id="inv_${id}" placeholder="Add LBS" style="width:90px;padding:4px 6px;font-size:11px;border:1px solid #ccc;border-radius:3px"/>
          <button class="btn btn-primary btn-sm" style="padding:4px 8px;font-size:11px"
            onclick="updateStock('${id}')">Update</button>
          <button class="btn btn-gold btn-sm" style="padding:4px 7px;font-size:11px;margin-left:4px" title="Print inventory sticker for this coil"
            onclick="quickPrintSticker('${id}', ${JSON.stringify(coil.name||'').replace(/'/g,"\\'")} )">🏷️</button>
          <button class="btn btn-red btn-sm" style="padding:4px 7px;font-size:11px;margin-left:4px" title="Permanently delete this coil + certs"
            onclick="deleteCoil('${id}', ${JSON.stringify(coil.name||id).replace(/'/g,"\\'")})">🗑️</button>
        </td>
      </tr>`;
  }

  html += `</tbody></table></div></div>`;

  // Update alert banner and tab badge
  updateInventoryAlerts(alertsOut, alertsLow);

  // ── Add New Coil Form ──────────────────────────────────────────────────
  html += `
  <div class="card" style="margin-top:16px">
    <div class="card-hdr" style="background:var(--tf-green);color:#fff"><span class="icon">➕</span>Add New Coil to Inventory</div>
    <div class="card-body">
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:10px;margin-bottom:12px">
        <div class="form-group">
          <label>Coil ID *</label>
          <div style="display:flex;gap:4px">
            <input type="text" id="new_coil_id" placeholder="COIL-2026-001" style="font-size:12px;flex:1"/>
            <button class="btn btn-outline btn-sm" style="padding:3px 8px;font-size:10px;white-space:nowrap" onclick="document.getElementById('new_coil_id').value=generateCoilId()">Auto</button>
          </div>
        </div>
        <div class="form-group">
          <label>Material Name *</label>
          <input type="text" id="new_coil_name" placeholder='e.g. 23" 10GA C-Section' style="font-size:12px"/>
        </div>
        <div class="form-group">
          <label>Gauge</label>
          <input type="text" id="new_coil_gauge" placeholder="e.g. 10GA" style="font-size:12px"/>
        </div>
        <div class="form-group">
          <label>Stock (LBS)</label>
          <input type="number" id="new_coil_stock" value="0" style="font-size:12px"/>
        </div>
        <div class="form-group">
          <label>Price / LB ($)</label>
          <input type="number" id="new_coil_price" value="0" step="0.01" style="font-size:12px"/>
        </div>
        <div class="form-group">
          <label>LBS / LFT</label>
          <input type="number" id="new_coil_lbs_lft" value="0" step="0.01" style="font-size:12px"/>
        </div>
        <div class="form-group">
          <label>Lead Time (wks)</label>
          <input type="number" id="new_coil_lead" value="8" style="font-size:12px"/>
        </div>
        <div class="form-group">
          <label>Min Order (LBS)</label>
          <input type="number" id="new_coil_min_order" value="5000" style="font-size:12px"/>
        </div>
      </div>
      <div style="display:flex;gap:8px;align-items:center">
        <button class="btn btn-green" onclick="addNewCoil()">➕ Add Coil</button>
        <div id="new-coil-status" style="font-size:12px;color:#666"></div>
      </div>
    </div>
  </div>`;

  // ── Mill Certificates ──────────────────────────────────────────────────
  const allCerts = data.mill_certs || [];
  const coilOptions = Object.entries(data.coils||{})
    .map(([id,c])=>`<option value="${id}">${c.name.slice(0,35)}</option>`).join('');

  html += `
  <div class="card">
    <div class="card-hdr"><span class="icon">📜</span>Mill Certificates (AISC Compliance)</div>
    <div class="card-body">
      <p style="font-size:12px;color:#666;margin-bottom:12px">
        Per AISC requirements, heat numbers and mill certifications must be tracked for each coil.
        Upload the PDF from the mill — it's stored on the server and linked to the coil permanently.
      </p>

      <!-- Add cert form -->
      <div style="background:#F0F4FA;border-radius:6px;padding:14px;margin-bottom:14px">
        <div style="font-size:11px;font-weight:700;color:var(--tf-blue);text-transform:uppercase;margin-bottom:10px;letter-spacing:.4px">➕ Add New Mill Certificate</div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:10px;margin-bottom:10px">
          <div class="form-group">
            <label>Coil / Material</label>
            <select id="cert_material" style="font-size:12px">${coilOptions}</select>
          </div>
          <div class="form-group">
            <label>Heat Number</label>
            <input type="text" id="cert_heat" placeholder="e.g. 123456A" style="font-size:12px"/>
          </div>
          <div class="form-group">
            <label>Mill / Supplier</label>
            <input type="text" id="cert_mill" placeholder="e.g. Nucor Steel" style="font-size:12px"/>
          </div>
          <div class="form-group">
            <label>Cert Date</label>
            <input type="text" id="cert_date" placeholder="MM/DD/YYYY" style="font-size:12px"/>
          </div>
        </div>
        <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap">
          <div class="form-group" style="margin:0;flex:1;min-width:240px">
            <label>PDF Certificate File</label>
            <input type="file" id="cert_pdf" accept="application/pdf,.pdf"
              style="width:100%;padding:5px 8px;border:1px dashed var(--tf-blue-m);border-radius:4px;background:#fff;font-size:12px;cursor:pointer"/>
          </div>
          <button class="btn btn-primary" style="margin-top:16px;white-space:nowrap"
            onclick="addMillCert()">📜 Add Cert</button>
          <div id="cert-upload-status" style="font-size:12px;color:#666;margin-top:16px"></div>
        </div>
      </div>

      <!-- Cert list with filter -->
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
        <span style="font-size:11px;font-weight:700;color:var(--tf-blue);text-transform:uppercase">Certificate Log</span>
        <select id="cert_filter_coil" style="font-size:11px;padding:3px 6px;border:1px solid #ccc;border-radius:3px;max-width:200px"
          onchange="renderCertList()">
          <option value="">— All Coils —</option>
          ${coilOptions}
        </select>
        <span id="cert-count-badge" style="font-size:11px;color:#888"></span>
      </div>
      <div id="mill-certs-list">`;

  // Render certs inline (all of them; JS filterCerts will re-render)
  if (allCerts.length === 0) {
    html += `<div class="alert alert-info">No mill certificates recorded yet. Upload your first cert above.</div>`;
  }
  for (const cert of allCerts) {
    const coilName = (data.coils||{})[cert.coil_id||cert.material]?.name || cert.coil_id || cert.material || '?';
    const pdfLink = cert.filename
      ? `<a href="/certs/${cert.filename}" target="_blank"
           style="background:var(--tf-red);color:#fff;border-radius:3px;padding:3px 8px;font-size:10px;font-weight:700;text-decoration:none;margin-left:8px">📄 VIEW PDF</a>`
      : `<span style="color:#bbb;font-size:10px;margin-left:8px">no PDF</span>`;
    html += `
      <div class="alert alert-success" style="display:flex;align-items:center;flex-wrap:wrap;gap:6px"
           data-coil-id="${cert.coil_id||cert.material||''}">
        <span style="font-weight:700">${coilName}</span>
        <span style="color:#555">Heat: <b>${cert.heat||'—'}</b></span>
        <span style="color:#555">Mill: ${cert.mill||'—'}</span>
        <span style="color:#555">Date: ${cert.date||'—'}</span>
        <span style="color:#888;font-size:10px">Added: ${cert.added||''}</span>
        ${pdfLink}
      </div>`;
  }

  html += `</div></div></div>`;

  // ── Coil Sticker Section ──────────────────────────────────────────────────
  html += `
  <div class="card" style="margin-top:16px">
    <div class="card-hdr"><span class="icon">🏷️</span>Print Inventory Sticker</div>
    <div class="card-body">
      <p style="font-size:12px;color:#666;margin-bottom:14px">
        Print a 4"×6" sticker for any coil. The sticker includes grade, gauge, heat number,
        supplier, weight, width, received date, and a <strong>QR code</strong> workers can scan
        to instantly see if the coil has been applied to a job.
        You can also create a new coil entry in inventory at the same time.
      </p>

      <div style="background:#FFF8E8;border:1px solid #C89A2E;border-radius:6px;padding:14px;margin-bottom:14px">
        <div style="font-size:11px;font-weight:700;color:#7A5C00;text-transform:uppercase;margin-bottom:10px;letter-spacing:.4px">🏷️ Sticker Details</div>
        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:10px;margin-bottom:10px">
          <div class="form-group">
            <label>Coil / Material *</label>
            <select id="stk_coil_id" style="font-size:12px" onchange="onStickerCoilChange()">
              <option value="">— New coil (fill below) —</option>
              ${coilOptions}
            </select>
          </div>
          <div class="form-group">
            <label>Description</label>
            <input type="text" id="stk_description" placeholder="e.g. G90 Galv 29ga Coil" style="font-size:12px"/>
          </div>
          <div class="form-group">
            <label>Grade</label>
            <input type="text" id="stk_grade" placeholder="e.g. G90" style="font-size:12px"/>
          </div>
          <div class="form-group">
            <label>Gauge</label>
            <input type="text" id="stk_gauge" placeholder="e.g. 29 ga" style="font-size:12px"/>
          </div>
          <div class="form-group">
            <label>Heat Number</label>
            <input type="text" id="stk_heat_num" placeholder="e.g. HT-A12345" style="font-size:12px"/>
          </div>
          <div class="form-group">
            <label>Supplier / Mill</label>
            <input type="text" id="stk_supplier" placeholder="e.g. Nucor Steel" style="font-size:12px"/>
          </div>
          <div class="form-group">
            <label>Weight (lbs)</label>
            <input type="number" id="stk_weight_lbs" placeholder="14500" style="font-size:12px"/>
          </div>
          <div class="form-group">
            <label>Width (in)</label>
            <input type="number" id="stk_width_in" placeholder="48" style="font-size:12px"/>
          </div>
          <div class="form-group">
            <label>Qty On Hand (lbs)</label>
            <input type="number" id="stk_qty_on_hand" placeholder="0" style="font-size:12px"/>
          </div>
          <div class="form-group">
            <label>Received Date</label>
            <input type="text" id="stk_received_date" placeholder="MM/DD/YYYY" style="font-size:12px"/>
          </div>
        </div>

        <!-- New coil creation option -->
        <div id="stk_new_coil_row" style="display:none;background:#fff;border:1px solid #C89A2E;border-radius:5px;padding:10px;margin-bottom:10px">
          <div style="font-size:12px;color:#7A5C00;margin-bottom:6px;font-weight:bold">
            🆕 New Coil Entry
          </div>
          <div style="display:flex;align-items:center;gap:10px">
            <div class="form-group" style="flex:1;margin:0">
              <label>New Coil ID *</label>
              <input type="text" id="stk_new_coil_id" placeholder="e.g. COIL-2026-005"
                style="font-size:12px;width:100%"/>
            </div>
            <label style="font-size:12px;display:flex;align-items:center;gap:5px;margin-top:14px;white-space:nowrap">
              <input type="checkbox" id="stk_create_entry" checked/>
              Add to inventory
            </label>
          </div>
        </div>

        <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">
          <button class="btn btn-gold" onclick="printCoilSticker('pdf')" style="font-size:12px">
            📄 Download PDF Sticker
          </button>
          <button class="btn btn-green" onclick="printCoilSticker('zpl')" style="font-size:12px">
            ⬇️ Download ZPL (Zebra)
          </button>
          <button class="btn btn-outline" onclick="printCoilSticker('csv')" style="font-size:12px">
            📊 Download CSV (NiceLabel)
          </button>
          <div id="stk-status" style="font-size:12px;color:#666"></div>
        </div>
      </div>
    </div>
  </div>`;

  el.innerHTML = html;
}

function updateInventoryAlerts(outCount, lowCount) {
  const banner = document.getElementById('inv-alert-banner');
  const bannerText = document.getElementById('inv-alert-text');
  const tabBadge = document.getElementById('inv-tab-badge');

  if (outCount > 0 || lowCount > 0) {
    let parts = [];
    if (outCount > 0) parts.push(outCount + ' OUT OF STOCK');
    if (lowCount > 0) parts.push(lowCount + ' LOW');
    if (bannerText) bannerText.textContent = parts.join(' · ') + ' — click to manage inventory';

    if (banner) {
      banner.style.display = 'block';
      if (outCount > 0) {
        banner.style.background = '#FFEBEE';
        banner.style.borderBottomColor = '#EF9A9A';
        banner.style.color = '#B71C1C';
      } else {
        banner.style.background = '#FFF3CD';
        banner.style.borderBottomColor = '#FFD43B';
        banner.style.color = '#856404';
      }
    }
    if (tabBadge) {
      tabBadge.textContent = outCount > 0 ? outCount + ' OUT' : lowCount + ' LOW';
      tabBadge.style.display = 'inline';
      tabBadge.style.background = outCount > 0 ? '#C00000' : '#E65100';
    }
  } else {
    if (banner) banner.style.display = 'none';
    if (tabBadge) tabBadge.style.display = 'none';
  }
}

async function updateMinStock(coilId, minLbs) {
  try {
    const resp = await fetch('/api/inventory');
    const inv = await resp.json();
    if (inv.coils && inv.coils[coilId]) {
      inv.coils[coilId].min_stock_lbs = minLbs;
      await fetch('/api/inventory/save', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify(inv),
      });
      // Re-render to update statuses
      renderInventory(inv);
    }
  } catch(e) { console.warn('Failed to update min stock:', e); }
}

async function deleteCoil(coilId, coilName) {
  if (!confirm('⚠️ PERMANENTLY DELETE coil "' + coilName + '" (ID: ' + coilId + ')?\n\nThis will also delete all associated mill certificates and PDF files.\n\nThis cannot be undone.')) return;
  if (!confirm('Are you SURE? Type OK to confirm.\n\nDeleting: ' + coilId)) return;
  try {
    const resp = await fetch('/api/inventory/delete', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ coil_id: coilId }),
    });
    const result = await resp.json();
    if (result.ok) {
      loadInventory();
    } else {
      showToast('Delete failed: ' + (result.error || 'unknown error'), 'error');
    }
  } catch(e) { showToast('Delete error: ' + e.message, 'error'); }
}

function generateCoilId() {
  const year = new Date().getFullYear();
  // Look at existing coil IDs to find the next number
  const existingIds = [...document.querySelectorAll('#inventory-content .inv-table tbody tr')]
    .map(r => r.querySelector('td')?.textContent || '');
  let maxNum = 0;
  const re = /COIL-(\d{4})-(\d+)/;
  for (const id of existingIds) {
    const m = id.match(re);
    if (m && parseInt(m[1]) === year) maxNum = Math.max(maxNum, parseInt(m[2]));
  }
  return 'COIL-' + year + '-' + String(maxNum + 1).padStart(3, '0');
}

function onStickerCoilChange() {
  const sel  = document.getElementById('stk_coil_id');
  const coilId = sel?.value || '';
  const newRow = document.getElementById('stk_new_coil_row');
  if (newRow) newRow.style.display = coilId ? 'none' : 'block';
}

async function printCoilSticker(fmt) {
  const selEl     = document.getElementById('stk_coil_id');
  const existingId = selEl?.value || '';
  const newIdEl   = document.getElementById('stk_new_coil_id');
  const coilId    = existingId || (newIdEl?.value.trim() || '');

  if (!coilId) {
    showToast('Please select an existing coil or enter a New Coil ID.', 'info');
    return;
  }

  const createEntry = !existingId && document.getElementById('stk_create_entry')?.checked;

  const coilData = {
    description:   document.getElementById('stk_description')?.value.trim() || '',
    grade:         document.getElementById('stk_grade')?.value.trim()       || '',
    gauge:         document.getElementById('stk_gauge')?.value.trim()       || '',
    heat_num:      document.getElementById('stk_heat_num')?.value.trim()    || '',
    supplier:      document.getElementById('stk_supplier')?.value.trim()    || '',
    weight_lbs:    parseFloat(document.getElementById('stk_weight_lbs')?.value) || '',
    width_in:      parseFloat(document.getElementById('stk_width_in')?.value)   || '',
    qty_on_hand:   parseFloat(document.getElementById('stk_qty_on_hand')?.value) || '',
    received_date: document.getElementById('stk_received_date')?.value.trim() || '',
    create_entry:  createEntry,
  };

  const status = document.getElementById('stk-status');
  if (status) status.textContent = 'Generating…';

  try {
    const resp = await fetch('/api/inventory/sticker', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ coil_id: coilId, format: fmt, coil: coilData }),
    });
    if (!resp.ok) { showToast('Sticker error: ' + await resp.text(), 'error'); return; }
    const blob = await resp.blob();
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    const exts = {pdf:'pdf', zpl:'zpl', csv:'csv'};
    a.href     = url;
    a.download = `Coil_Sticker_${coilId}.${exts[fmt] || fmt}`;
    a.click();
    URL.revokeObjectURL(url);
    if (status) status.textContent = '✅ Downloaded!';
    if (createEntry) { setTimeout(loadInventory, 800); }
  } catch(e) {
    showToast('Failed: ' + e, 'error');
    if (status) status.textContent = '';
  }
}

function filterCerts(coilId) {
  // Select that coil in the filter dropdown and re-render
  const sel = document.getElementById('cert_filter_coil');
  if (sel) { sel.value = coilId; renderCertList(); }
}

function renderCertList() {
  const filterCoil = document.getElementById('cert_filter_coil')?.value || '';
  const rows = document.querySelectorAll('#mill-certs-list [data-coil-id]');
  let shown = 0;
  rows.forEach(row => {
    const match = !filterCoil || row.dataset.coilId === filterCoil;
    row.style.display = match ? '' : 'none';
    if (match) shown++;
  });
  const badge = document.getElementById('cert-count-badge');
  if (badge) badge.textContent = shown + ' cert' + (shown !== 1 ? 's' : '') + (filterCoil ? ' for this coil' : ' total');
}

async function updateStock(coilId) {
  const input = document.getElementById('inv_' + coilId);
  const lbs = parseFloat(input.value);
  if (isNaN(lbs) || lbs === 0) return;
  await fetch('/api/inventory/update', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({coil_id: coilId, add_lbs: lbs}),
  });
  input.value = '';
  loadInventory();
}

async function quickPrintSticker(coilId, coilName) {
  // One-click PDF sticker from the coil row — uses whatever is in inventory for that coil
  const resp = await fetch('/api/inventory/sticker', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({ coil_id: coilId, format: 'pdf', coil: {} }),
  });
  if (!resp.ok) { showToast('Sticker error: ' + await resp.text(), 'error'); return; }
  const blob = await resp.blob();
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href     = url;
  a.download = `Coil_Sticker_${coilId}.pdf`;
  a.click();
  URL.revokeObjectURL(url);
}

async function addNewCoil() {
  const coilId = document.getElementById('new_coil_id')?.value.trim();
  const name   = document.getElementById('new_coil_name')?.value.trim();
  if (!coilId || !name) { showToast('Coil ID and Material Name are required.', 'info'); return; }

  const statusEl = document.getElementById('new-coil-status');
  if (statusEl) statusEl.textContent = 'Adding...';

  const newCoil = {
    coil_id: coilId,
    format: 'pdf',
    coil: {
      description:   name,
      gauge:         document.getElementById('new_coil_gauge')?.value.trim() || '',
      qty_on_hand:   parseFloat(document.getElementById('new_coil_stock')?.value) || 0,
      create_entry:  true,
    }
  };

  // Use the sticker endpoint to create entry (it handles creation)
  // But we also need price_per_lb etc. so let's use a direct inventory update approach
  try {
    const invResp = await fetch('/api/inventory');
    const inv = await invResp.json();
    if (inv.coils && inv.coils[coilId]) {
      showToast('Coil ID "' + coilId + '" already exists. Choose a different ID.', 'warning');
      if (statusEl) statusEl.textContent = '';
      return;
    }
    inv.coils = inv.coils || {};
    inv.coils[coilId] = {
      name:           name,
      gauge:          document.getElementById('new_coil_gauge')?.value.trim() || '',
      stock_lbs:      parseFloat(document.getElementById('new_coil_stock')?.value) || 0,
      stock_lft:      0,
      committed_lbs:  0,
      min_order_lbs:  parseFloat(document.getElementById('new_coil_min_order')?.value) || 5000,
      lead_time_weeks: parseInt(document.getElementById('new_coil_lead')?.value) || 8,
      price_per_lb:   parseFloat(document.getElementById('new_coil_price')?.value) || 0,
      lbs_per_lft:    parseFloat(document.getElementById('new_coil_lbs_lft')?.value) || 0,
      coil_max_lbs:   8000,
      orders:         [],
    };
    // Save via a direct PUT-style update to inventory
    await fetch('/api/inventory/save', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(inv),
    });
    if (statusEl) statusEl.textContent = '✅ Coil added!';
    // Clear form
    document.getElementById('new_coil_id').value = '';
    document.getElementById('new_coil_name').value = '';
    document.getElementById('new_coil_gauge').value = '';
    document.getElementById('new_coil_stock').value = '0';
    document.getElementById('new_coil_price').value = '0';
    document.getElementById('new_coil_lbs_lft').value = '0';
    setTimeout(() => { if (statusEl) statusEl.textContent = ''; }, 3000);
    loadInventory();
  } catch(e) {
    if (statusEl) statusEl.textContent = '❌ Error: ' + e.message;
  }
}

async function addMillCert() {
  const coilId  = document.getElementById('cert_material').value;
  const heat    = document.getElementById('cert_heat').value.trim();
  const mill    = document.getElementById('cert_mill').value.trim();
  const date    = document.getElementById('cert_date').value.trim();
  const pdfFile = document.getElementById('cert_pdf').files[0];

  if (!heat) { showToast('Please enter a Heat Number.', 'info'); return; }

  const statusEl = document.getElementById('cert-upload-status');
  statusEl.textContent = '⏳ Uploading...';

  // Always use multipart upload so the PDF (if any) goes with the metadata
  const fd = new FormData();
  fd.append('coil_id', coilId);
  fd.append('heat', heat);
  fd.append('mill', mill);
  fd.append('date', date);
  if (pdfFile) fd.append('pdf_file', pdfFile);

  try {
    const resp = await fetch('/api/inventory/cert/upload', { method: 'POST', body: fd });
    const result = await resp.json();
    if (result.ok) {
      statusEl.textContent = result.filename
        ? `✅ Cert + PDF saved (${result.filename})`
        : '✅ Cert saved (no PDF attached)';
      // Clear form
      document.getElementById('cert_heat').value = '';
      document.getElementById('cert_mill').value = '';
      document.getElementById('cert_date').value = '';
      document.getElementById('cert_pdf').value = '';
      setTimeout(() => { statusEl.textContent = ''; }, 4000);
      loadInventory();
    } else {
      statusEl.textContent = '❌ Error: ' + (result.error || 'unknown');
    }
  } catch(e) {
    statusEl.textContent = '❌ Upload failed: ' + e.message;
  }
}

// ─────────────────────────────────────────────
// GLOBAL CLICK HANDLER FOR BUTTONS
// ─────────────────────────────────────────────
document.addEventListener('click', function(e) {
  var btn = e.target.closest('[onclick]');
  if (btn && btn.getAttribute('onclick')) {
    try {
      e.stopPropagation();
      new Function(btn.getAttribute('onclick')).call(btn);
    } catch(err) {
      console.error('onclick handler error:', err);
    }
  }
}, true);
</script>

<!-- Global Search Overlay -->
<div id="globalSearchOverlay" style="display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(15,23,42,0.5);z-index:9999;align-items:flex-start;justify-content:center;padding-top:100px;">
<div style="width:600px;max-width:90vw;background:#fff;border-radius:16px;box-shadow:0 10px 40px rgba(0,0,0,0.2);overflow:hidden;">
<input type="text" id="globalSearchInput" placeholder="Search projects, customers, inventory..." style="width:100%;padding:18px 20px;border:none;font-size:16px;outline:none;border-bottom:1px solid #e2e8f0;" oninput="_doGS(this.value)">
<div id="globalSearchResults" style="max-height:400px;overflow-y:auto;padding:8px;"><div style="padding:20px;text-align:center;color:#94a3b8;font-size:13px;">Type to search...</div></div>
</div></div>
<script>
var _gst=null;
function openGlobalSearch(){document.getElementById('globalSearchOverlay').style.display='flex';document.getElementById('globalSearchInput').value='';document.getElementById('globalSearchInput').focus();}
function _closeGS(){document.getElementById('globalSearchOverlay').style.display='none';}
document.getElementById('globalSearchOverlay').addEventListener('click',function(e){if(e.target.id==='globalSearchOverlay')_closeGS();});
document.addEventListener('keydown',function(e){if((e.ctrlKey||e.metaKey)&&e.key==='k'){e.preventDefault();openGlobalSearch();}if(e.key==='Escape')_closeGS();});
function _doGS(q){clearTimeout(_gst);if(!q||q.length<2){document.getElementById('globalSearchResults').innerHTML='<div style="padding:20px;text-align:center;color:#94a3b8;">Type to search...</div>';return;}
_gst=setTimeout(function(){fetch('/api/search?q='+encodeURIComponent(q)).then(function(r){return r.json();}).then(function(d){var c=document.getElementById('globalSearchResults');if(!d.results||!d.results.length){c.innerHTML='<div style="padding:20px;text-align:center;color:#94a3b8;">No results</div>';return;}
var ic={project:'&#128204;',customer:'&#128100;',inventory:'&#128230;'};c.innerHTML=d.results.map(function(r){return '<a href="'+r.url+'" style="text-decoration:none;color:inherit;"><div style="display:flex;align-items:center;gap:12px;padding:10px 14px;border-radius:8px;cursor:pointer;" onmouseover="this.style.background=\'#DBEAFE\'" onmouseout="this.style.background=\'\'"><div style="width:32px;height:32px;border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:14px;background:#DBEAFE;">'+(ic[r.type]||'')+'</div><div><div style="font-weight:600;font-size:13px;color:#0f172a;">'+r.title+'</div><div style="font-size:11px;color:#94a3b8;">'+(r.subtitle||'')+'</div></div></div></a>';}).join('');});},300);}
</script>
</body>
</html>
"""