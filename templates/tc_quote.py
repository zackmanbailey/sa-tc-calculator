"""TC Quote HTML Templates - TitanForge Branded"""

TC_QUOTE_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>TitanForge — Titan Carports Estimator</title>
<style>
:root {
  --tf-dark:#0F172A; --tf-blue:#1E40AF; --tf-blue-m:#3B82F6;
  --tf-blue-l:#DBEAFE; --tf-red:#DC2626; --tf-amber:#F59E0B;
  --tf-green:#16A34A; --tf-gray:#475569; --tf-light:#F8FAFC;
  --tf-white:#ffffff; --tf-border:#E2E8F0;
}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Inter',system-ui,sans-serif;background:#0F172A;color:#E2E8F0;font-size:13px}
#topbar{background:var(--tf-dark);color:#fff;padding:0 20px;display:flex;align-items:center;height:52px;box-shadow:0 2px 8px #0005}
#topbar .logo{font-size:17px;font-weight:700;letter-spacing:1px;color:#fff}
#topbar .logo span{color:var(--tf-red)}
#topbar .spacer{flex:1}
#topbar .version{font-size:10px;color:#666}
#tabs{background:#1E293B;display:flex;overflow-x:auto;border-bottom:1px solid #334155}
.tab{padding:10px 20px;color:#aac;cursor:pointer;font-size:12px;font-weight:600;border-bottom:3px solid transparent;white-space:nowrap;transition:all .2s}
.tab:hover{color:#fff;background:rgba(255,255,255,.07)}
.tab.active{color:#fff;border-bottom-color:var(--tf-amber)}
#main{display:flex;gap:0;height:calc(100vh - 94px)}
#sidebar{width:320px;min-width:270px;background:#1E293B;border-right:1px solid #334155;overflow-y:auto;padding:16px;flex-shrink:0}
#content{flex:1;overflow-y:auto;padding:20px 20px 80px 20px;background:#0F172A}
.card{background:#1E293B;border:1px solid #334155;border-radius:8px;margin-bottom:14px;overflow:hidden}
.card-hdr{padding:9px 14px;font-weight:700;font-size:12px;display:flex;align-items:center;gap:8px;text-transform:uppercase;letter-spacing:.4px}
.card-hdr.red{background:var(--tf-red);color:#fff}
.card-hdr.blue{background:var(--tf-blue-m);color:#fff}
.card-hdr.gold{background:var(--tf-amber);color:#0F172A}
.card-hdr.green{background:var(--tf-green);color:#fff}
.card-hdr.gray{background:#555;color:#fff}
.card-hdr.dark{background:var(--tf-dark);color:#fff}
.card-body{padding:14px}
.form-group{margin-bottom:10px}
label{display:block;font-size:11px;font-weight:600;color:#93C5FD;margin-bottom:4px;text-transform:uppercase;letter-spacing:.4px}
input[type=text],input[type=number],select,textarea{width:100%;padding:6px 10px;border:1px solid #334155;border-radius:4px;font-size:13px;color:#E2E8F0;background:#0F172A;transition:border .2s}
input:focus,select:focus,textarea:focus{outline:none;border-color:var(--tf-blue-m);box-shadow:0 0 0 3px rgba(59,130,246,0.15)}
input[type=checkbox]{width:auto;margin-right:6px}
.check-label{display:flex;align-items:center;font-size:12px;font-weight:400;text-transform:none;letter-spacing:0;cursor:pointer}
.btn{padding:7px 14px;border:none;border-radius:4px;cursor:pointer;font-size:12px;font-weight:600;transition:all .2s;display:inline-flex;align-items:center;gap:5px}
.btn-red{background:var(--tf-red);color:#fff}.btn-red:hover{opacity:.9}
.btn-blue{background:var(--tf-blue-m);color:#fff}.btn-blue:hover{opacity:.85}
.btn-gold{background:var(--tf-amber);color:var(--tf-dark)}.btn-gold:hover{opacity:.9}
.btn-green{background:var(--tf-green);color:#fff}.btn-green:hover{opacity:.9}
.btn-outline{background:transparent;border:1px solid #334155;color:#E2E8F0}.btn-outline:hover{background:#334155}
.btn-sm{padding:4px 10px;font-size:11px}
.btn-danger{background:#f44;color:#fff}.btn-danger:hover{opacity:.85}
.btn-group{display:flex;gap:8px;flex-wrap:wrap}
.li-table{width:100%;border-collapse:collapse;font-size:12px;margin-top:8px}
.li-table th{background:var(--tf-blue);color:#fff;padding:6px 8px;text-align:left;font-size:11px;font-weight:600}
.li-table td{padding:5px 8px;border-bottom:1px solid #334155;vertical-align:middle}
.li-table tr:hover td{background:#334155}
.li-table .total-row td{background:#1a2332;font-weight:700;border-top:2px solid var(--tf-amber)}
.li-table input{padding:4px 6px;font-size:12px;border:1px solid #334155;border-radius:3px;background:#0F172A;color:#E2E8F0}
.summary-table{width:100%;border-collapse:collapse;font-size:13px}
.summary-table td{padding:8px 12px;border-bottom:1px solid #334155;color:#E2E8F0}
.summary-table .section-lbl td{background:#1a2332;font-weight:700;color:#93C5FD;font-size:11px;text-transform:uppercase;letter-spacing:.4px}
.summary-table .total-row td{background:var(--tf-red);color:#fff;font-weight:700;font-size:15px}
.summary-table .markup-row td{background:#1a2332;font-weight:600;color:#F59E0B}
.summary-table .subtotal-row td{background:#0F172A;font-weight:700}
.stat-cards{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:16px}
.stat{background:#1E293B;border:1px solid #334155;border-radius:8px;padding:12px 16px;min-width:140px;flex:1}
.stat .val{font-size:20px;font-weight:700;color:#93C5FD}
.stat .lbl{font-size:10px;color:#94A3B8;text-transform:uppercase;margin-top:2px}
.alert{border-radius:4px;padding:8px 12px;font-size:12px;margin-bottom:10px}
.alert-info{background:rgba(33,150,243,0.1);border-left:4px solid #2196F3;color:#93C5FD}
.alert-warn{background:rgba(245,158,11,0.1);border-left:4px solid var(--tf-amber);color:#FCD34D}
.alert-success{background:rgba(76,175,80,0.1);border-left:4px solid #4CAF50;color:#6EE7B7}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px}
.grid4{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:10px}
@media(max-width:768px){#main{flex-direction:column}#sidebar{width:100%}}
/* When wrapped by shared_nav inject_nav(), adjust layout */
.tf-main #main{height:calc(100vh - 84px)}
.tf-main #topbar{display:none}
/* Progressive disclosure - collapsible sections */
.tc-section-toggle { cursor:pointer; user-select:none; display:flex; align-items:center; justify-content:space-between; }
.tc-section-toggle::after { content:'▼'; font-size:10px; color:var(--tf-muted,#94a3b8); transition:transform .2s; margin-left:8px; }
.tc-section-toggle.collapsed::after { transform:rotate(-90deg); }
.tc-section-body { transition: max-height .3s ease, opacity .2s ease; overflow:hidden; }
.tc-section-body.collapsed { max-height:0 !important; opacity:0; padding-top:0 !important; padding-bottom:0 !important; margin-top:0 !important; }
/* Sticky running total */
.tc-sticky-total {
    position:fixed; bottom:0; left:0; right:0; z-index:900;
    background:linear-gradient(180deg, rgba(15,23,42,0.0) 0%, rgba(15,23,42,0.95) 20%, #0f172a 40%);
    padding:12px 32px 16px; display:flex; align-items:center; justify-content:center; gap:24px;
    font-family:'Inter','Segoe UI',sans-serif; pointer-events:none;
    transition: opacity .3s;
}
.tc-sticky-total.hidden { opacity:0; }
.tc-sticky-total-inner {
    pointer-events:auto; background:rgba(30,41,59,0.95); border:1px solid rgba(59,130,246,0.3);
    border-radius:12px; padding:10px 28px; display:flex; align-items:center; gap:20px;
    backdrop-filter:blur(12px); box-shadow:0 -4px 24px rgba(0,0,0,0.4);
}
.tc-sticky-item { text-align:center; }
.tc-sticky-item .label { font-size:10px; text-transform:uppercase; letter-spacing:.5px; color:#94a3b8; }
.tc-sticky-item .val { font-size:18px; font-weight:800; color:#F1F5F9; }
.tc-sticky-item .val.highlight { color:#10b981; font-size:22px; }
.tc-sticky-sep { width:1px; height:32px; background:rgba(148,163,184,0.2); }
/* Gold flash for auto-filled fields */
@keyframes tcGoldFlash {
    0% { box-shadow: 0 0 0 3px rgba(200,154,46,0.5); background: rgba(200,154,46,0.08); }
    100% { box-shadow: 0 0 0 0 rgba(200,154,46,0); background: transparent; }
}
.tc-field-flash { animation: tcGoldFlash 1.5s ease forwards; }
/* Quick Quote Mode */
.qq-overlay {
    display:none; position:fixed; top:0; left:0; right:0; bottom:0;
    background:rgba(0,0,0,0.7); z-index:1000; align-items:center; justify-content:center;
    backdrop-filter:blur(4px);
}
.qq-overlay.active { display:flex; }
.qq-modal {
    background:#1e293b; border:1px solid #334155; border-radius:16px;
    padding:32px; max-width:600px; width:90%; max-height:85vh; overflow-y:auto;
    box-shadow:0 20px 60px rgba(0,0,0,.5);
}
.qq-modal h2 { font-size:20px; font-weight:800; color:#F1F5F9; margin:0 0 6px; }
.qq-modal p { font-size:13px; color:#94a3b8; margin:0 0 24px; }
.qq-grid { display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:24px; }
.qq-field label { display:block; font-size:12px; font-weight:600; color:#94a3b8; text-transform:uppercase; letter-spacing:.3px; margin-bottom:6px; }
.qq-field input, .qq-field select {
    width:100%; box-sizing:border-box; background:#0f172a; border:1px solid #334155;
    border-radius:8px; color:#e2e8f0; padding:10px 14px; font-size:14px; font-family:inherit;
}
.qq-field input:focus, .qq-field select:focus { outline:none; border-color:#3b82f6; }
.qq-actions { display:flex; gap:12px; justify-content:flex-end; margin-top:24px; }
.qq-btn {
    padding:10px 24px; border-radius:8px; font-size:14px; font-weight:600;
    border:none; cursor:pointer; font-family:inherit;
}
.qq-btn-primary { background:#3b82f6; color:#fff; }
.qq-btn-primary:hover { background:#2563eb; }
.qq-btn-outline { background:transparent; border:1px solid #334155; color:#e2e8f0; }
.qq-btn-outline:hover { border-color:#3b82f6; color:#3b82f6; }
.btn-amber{background:var(--tf-amber);color:#0F172A;font-weight:700}.btn-amber:hover{opacity:.9}
</style>
</head>
<body>

<!-- Topbar -->
<div id="topbar">
  <div style="display:flex;align-items:center;gap:12px">
    <div style="font-size:16px;font-weight:700;color:var(--tf-white);letter-spacing:1px">TitanForge</div>
  </div>
  <div style="display:flex;gap:20px;align-items:center;margin-left:30px">
    <a href="/" style="color:#aaa;text-decoration:none;font-size:12px;font-weight:600">Dashboard</a>
    <a href="/sa" style="color:#aaa;text-decoration:none;font-size:12px;font-weight:600">Structures America Estimator</a>
    <a href="/tc" style="color:var(--tf-white);text-decoration:none;font-size:12px;font-weight:600;border-bottom:2px solid var(--tf-amber);padding-bottom:2px">Titan Carports Estimator</a>
    <a href="/customers" style="color:#aaa;text-decoration:none;font-size:12px;font-weight:600">Customers</a>
  </div>
  <div class="spacer"></div>
  <button onclick="openGlobalSearch()" style="background:none;border:1px solid rgba(255,255,255,0.2);color:#fff;padding:4px 12px;border-radius:6px;cursor:pointer;font-size:11px;margin-right:8px;display:flex;align-items:center;gap:4px;">&#128269; Search <kbd style="background:rgba(255,255,255,0.15);padding:1px 5px;border-radius:3px;font-size:9px;">Ctrl+K</kbd></button>
  <div style="display:flex;gap:16px;align-items:center;font-size:11px;color:#aaa">
    <a href="/admin" style="color:#aaa;text-decoration:none;cursor:pointer">👤 Admin</a>
    <a href="/auth/logout" style="color:#aaa;text-decoration:none;cursor:pointer" onclick="return confirm('Are you sure you want to logout?')">🚪 Logout</a>
  </div>
  <div class="version">v3.0</div>
</div>

<!-- Tabs -->
<div id="tabs">
  <div class="tab active" onclick="showTab('quote')">📋 Quote Builder</div>
  <div class="tab" onclick="showTab('summary')">💰 Summary</div>
</div>

<!-- Main -->
<div id="main">
  <!-- LEFT SIDEBAR -->
  <div id="sidebar">

    <!-- Salesperson -->
    <div class="card">
      <div class="card-hdr dark"><span>👤</span>Salesperson</div>
      <div class="card-body">
        <div class="grid2">
          <div class="form-group">
            <label>Name</label>
            <input type="text" id="sp_name" value="Brad Spence"/>
          </div>
          <div class="form-group">
            <label>Title</label>
            <input type="text" id="sp_title" value="Sales Manager"/>
          </div>
        </div>
        <div class="grid2">
          <div class="form-group">
            <label>Phone</label>
            <input type="text" id="sp_phone" value="(303) 909-5698"/>
          </div>
          <div class="form-group">
            <label>Email</label>
            <input type="text" id="sp_email" value="brad@titancarports.com"/>
          </div>
        </div>
      </div>
    </div>

    <!-- Project Info -->
    <div class="card">
      <div class="card-hdr red"><span>📁</span>Project Info</div>
      <div class="card-body">
        <button class="btn btn-amber" onclick="openQuickQuote()" style="margin-bottom:16px">⚡ Quick Quote</button>
        <div class="form-group">
          <label>Project / Job Name</label>
          <input type="text" id="proj_name" value="" placeholder="e.g. Smith RV Canopy"/>
        </div>
        <div class="form-group">
          <label>Job Code</label>
          <input type="text" id="proj_code" value="" placeholder="TC-2026-001"/>
        </div>
        <div class="form-group">
          <label>Customer Name</label>
          <input type="text" id="proj_customer" value=""/>
        </div>
        <div class="form-group">
          <label>Street Address</label>
          <input type="text" id="proj_address" value=""/>
        </div>
        <div class="grid2">
          <div class="form-group">
            <label>City</label>
            <input type="text" id="proj_city" value=""/>
          </div>
          <div class="form-group">
            <label>State</label>
            <select id="proj_state">
              <option>TX</option><option>FL</option><option>CA</option><option>AZ</option>
              <option>NM</option><option>NV</option><option>CO</option><option>OK</option>
              <option>KS</option><option>MO</option><option>AR</option><option>TN</option>
              <option>LA</option><option>MS</option><option>AL</option><option>GA</option>
              <option>SC</option><option>NC</option><option>VA</option><option>MD</option>
              <option>Other</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label>Quote Date</label>
          <input type="text" id="proj_date" value=""/>
        </div>
        <div class="form-group">
          <label>Markup %</label>
          <input type="number" id="proj_markup" value="35" min="0" max="200" step="0.5"
            onchange="renderSummary()"/>
        </div>
      </div>
    </div>

    <!-- SA Materials Import -->
    <div class="card">
      <div class="card-hdr blue"><span>🔗</span>Materials (from SA)</div>
      <div class="card-body">
        <div id="sa-import-banner" style="display:none;background:rgba(76,175,80,0.1);border:1px solid #334155;border-radius:4px;padding:8px 12px;margin-bottom:10px;font-size:12px;color:#6EE7B7;display:none">
          <span style="font-weight:700">SA Estimate imported</span> — Material cost: <span id="sa-import-cost-lbl">$0</span>
          <span id="sa-import-date-lbl" style="margin-left:8px;font-size:10px;color:#888"></span>
          <button class="btn btn-outline btn-sm" style="float:right;font-size:10px;padding:2px 8px" onclick="refreshSAImport()">&#8635; Refresh from SA</button>
        </div>
        <div class="alert alert-info" style="font-size:11px" id="sa-import-hint">
          Enter SA fabrication quote total. Use the "Send to TC Quote" button on the SA BOM page to auto-fill.
        </div>
        <div class="form-group">
          <label>SA Quote #</label>
          <input type="text" id="sa_quote_num" placeholder="e.g. SA-2026-042"/>
        </div>
        <div class="form-group">
          <label>SA Materials Sell Price ($)</label>
          <input type="number" id="sa_materials_cost" value="0" min="0" step="100"
            onchange="renderSummary()"/>
        </div>
        <div class="grid2">
          <div class="form-group">
            <label># Columns (piers)</label>
            <input type="number" id="sa_n_cols" value="0" min="0"
              onchange="syncConcreteFromSA();renderSummary()"/>
          </div>
          <div class="form-group">
            <label>Footing Depth (ft)</label>
            <input type="number" id="sa_footing_depth" value="10" min="4" max="25" step="0.5"
              onchange="syncConcreteFromSA();renderSummary()"/>
          </div>
        </div>
        <div class="grid2">
          <div class="form-group">
            <label>Building Width (ft)</label>
            <input type="number" id="sa_width" value="40" min="10"
              onchange="renderSummary()"/>
          </div>
          <div class="form-group">
            <label>Building Length (ft)</label>
            <input type="number" id="sa_length" value="180" min="10"
              onchange="renderSummary()"/>
          </div>
        </div>
        <button class="btn btn-blue btn-sm" style="width:100%;margin-top:4px"
          onclick="syncConcreteFromSA()">↻ Sync Concrete from SA Values</button>
      </div>
    </div>

    <div class="btn-group" style="margin-top:8px">
      <button class="btn btn-gold" onclick="showTab('summary')">💰 View Summary</button>
      <button class="btn btn-outline btn-sm" onclick="tcExportPDF()">⬇ PDF</button>
      <button class="btn btn-outline btn-sm" onclick="tcExportExcel()">⬇ Excel</button>
    </div>
    <div class="btn-group" style="margin-top:6px">
      <button class="btn btn-sm" style="background:#10B981;color:#fff;font-weight:700;" onclick="tcSaveProject()">&#128190; Save to Project</button>
    </div>
    <div id="tc-save-status" style="font-size:11px;color:#64748B;margin-top:4px;"></div>

  </div><!-- /sidebar -->

  <!-- CONTENT AREA -->
  <div id="content">

    <!-- QUOTE TAB -->
    <div id="tab-quote">

      <!-- Concrete -->
      <div class="card" id="card-concrete">
        <div class="card-hdr gray"><span>🪨</span>Concrete — Pier Footings</div>
        <div class="card-body">
          <div class="grid4" style="margin-bottom:10px">
            <div class="form-group">
              <label># Piers</label>
              <input type="number" id="conc_n_piers" value="0" min="0"
                onchange="calcConcrete();renderSummary()"/>
            </div>
            <div class="form-group">
              <label>Hole Dia (in)</label>
              <input type="number" id="conc_dia_in" value="24" min="6" max="60"
                onchange="calcConcrete();renderSummary()"/>
            </div>
            <div class="form-group">
              <label>Depth (ft)</label>
              <input type="number" id="conc_depth_ft" value="10" min="4" max="25" step="0.5"
                onchange="calcConcrete();renderSummary()"/>
            </div>
            <div class="form-group">
              <label>Price ($/CY)</label>
              <input type="number" id="conc_price_cy" value="165" min="0" step="5"
                onchange="calcConcrete();renderSummary()"/>
            </div>
          </div>
          <div style="background:#0F172A;border-radius:6px;padding:10px;display:flex;gap:24px;flex-wrap:wrap">
            <div><span style="font-size:11px;color:#94A3B8">Cubic Yards (w/10% waste):</span>
              <span id="conc_qty_display" style="font-weight:700;color:var(--tf-blue);margin-left:6px">—</span></div>
            <div><span style="font-size:11px;color:#94A3B8">Material Cost:</span>
              <span id="conc_cost_display" style="font-weight:700;color:var(--tf-red);margin-left:6px">—</span></div>
          </div>
        </div>
      </div>

      <!-- Labor Installation -->
      <div class="card" id="card-labor">
        <div class="card-hdr red"><span>👷</span>Labor — Installation</div>
        <div class="card-body">
          <div class="grid4" style="margin-bottom:10px">
            <div class="form-group">
              <label>Crew Size</label>
              <input type="number" id="lab_crew" value="4" min="1" max="50"
                onchange="calcLabor();renderSummary()"/>
            </div>
            <div class="form-group">
              <label>Days On Site</label>
              <input type="number" id="lab_days" value="1" min="0" step="0.5"
                onchange="calcLabor();renderSummary()"/>
            </div>
            <div class="form-group">
              <label>Rate ($/hr/person)</label>
              <input type="number" id="lab_rate_hr" value="30" min="0" step="1"
                onchange="calcLabor();renderSummary()"/>
            </div>
            <div class="form-group">
              <label>Hours/Day</label>
              <input type="number" id="lab_hrs_day" value="8" min="1" max="24"
                onchange="calcLabor();renderSummary()"/>
            </div>
          </div>
          <div style="background:#1a1a2e;border-radius:6px;padding:10px;display:flex;gap:24px;flex-wrap:wrap">
            <div><span style="font-size:11px;color:#94A3B8">Daily Cost:</span>
              <span id="lab_daily_display" style="font-weight:700;color:var(--tf-blue);margin-left:6px">—</span></div>
            <div><span style="font-size:11px;color:#94A3B8">Total Labor Cost:</span>
              <span id="lab_total_display" style="font-weight:700;color:var(--tf-red);margin-left:6px">—</span></div>
          </div>
          <div class="form-group" style="margin-top:10px">
            <label>Notes</label>
            <input type="text" id="lab_notes" placeholder="e.g. Steel erection + welding crew"/>
          </div>
        </div>
      </div>

      <!-- Equipment Rental -->
      <div class="card" id="card-equip">
        <div class="card-hdr blue"><span>🏗️</span>Equipment Rental</div>
        <div class="card-body">
          <table class="li-table">
            <thead><tr><th>Description</th><th>Qty</th><th>Unit</th><th>Rate ($)</th><th>Total</th><th></th></tr></thead>
            <tbody id="equip_tbody"></tbody>
          </table>
          <button class="btn btn-outline btn-sm" style="margin-top:8px"
            onclick="addEquipItem()">+ Add Equipment</button>
        </div>
      </div>

      <!-- Drilling -->
      <div class="card" id="card-drill">
        <div class="card-hdr gray"><span>⚙️</span>Drilling</div>
        <div class="card-body">
          <div class="grid3" style="margin-bottom:10px">
            <div class="form-group">
              <label>Drilling Method</label>
              <select id="drill_method" onchange="calcDrilling();renderSummary()">
                <option value="per_hole">Per Hole ($/hole)</option>
                <option value="rental">Rig Rental + Operator</option>
              </select>
            </div>
            <div class="form-group" id="drill_holes_grp">
              <label># Holes</label>
              <input type="number" id="drill_n_holes" value="0" min="0"
                onchange="calcDrilling();renderSummary()"/>
            </div>
            <div class="form-group" id="drill_rate_grp">
              <label id="drill_rate_lbl">Rate ($/hole)</label>
              <input type="number" id="drill_rate" value="50" min="0" step="5"
                onchange="calcDrilling();renderSummary()"/>
            </div>
          </div>
          <div id="drill_rental_row" style="display:none;margin-bottom:10px">
            <div class="grid3">
              <div class="form-group">
                <label>Rig Rental ($/day)</label>
                <input type="number" id="drill_rig_day" value="0" min="0"
                  onchange="calcDrilling();renderSummary()"/>
              </div>
              <div class="form-group">
                <label>Operator ($/day)</label>
                <input type="number" id="drill_op_day" value="0" min="0"
                  onchange="calcDrilling();renderSummary()"/>
              </div>
              <div class="form-group">
                <label>Days</label>
                <input type="number" id="drill_days" value="1" min="1"
                  onchange="calcDrilling();renderSummary()"/>
              </div>
            </div>
          </div>
          <div style="background:#0F172A;border-radius:6px;padding:10px">
            <span style="font-size:11px;color:#94A3B8">Drilling Total:</span>
            <span id="drill_total_display" style="font-weight:700;color:var(--tf-red);margin-left:6px">—</span>
          </div>
        </div>
      </div>

      <!-- Shipping -->
      <div class="card" id="card-shipping">
        <div class="card-hdr blue"><span>🚛</span>Shipping &amp; Freight</div>
        <div class="card-body">
          <div class="grid3" style="margin-bottom:10px">
            <div class="form-group">
              <label>Method</label>
              <select id="ship_method" onchange="calcShipping();renderSummary()">
                <option value="per_mile">Per Mile (flatbed)</option>
                <option value="flat">Flat Rate</option>
              </select>
            </div>
            <div class="form-group">
              <label>Miles from Factory</label>
              <input type="number" id="ship_miles" value="0" min="0"
                onchange="calcShipping();renderSummary()"/>
            </div>
            <div class="form-group" id="ship_rate_grp">
              <label>Rate ($/mile)</label>
              <input type="number" id="ship_rate" value="4.50" min="0" step="0.10"
                onchange="calcShipping();renderSummary()"/>
            </div>
          </div>
          <div id="ship_flat_row" style="display:none;margin-bottom:10px">
            <div class="form-group" style="max-width:220px">
              <label>Flat Shipping Amount ($)</label>
              <input type="number" id="ship_flat_amt" value="0" min="0"
                onchange="calcShipping();renderSummary()"/>
            </div>
          </div>
          <div style="display:flex;gap:24px;flex-wrap:wrap;margin-bottom:8px">
            <div><span style="font-size:11px;color:#94A3B8">Loads:</span>
              <input type="number" id="ship_loads" value="1" min="1" max="20"
                style="width:55px;margin-left:6px;padding:3px 6px;font-size:12px;border:1px solid #334155;border-radius:3px;background:#0F172A;color:#E2E8F0"
                onchange="calcShipping();renderSummary()"/>
            </div>
            <div><span style="font-size:11px;color:#94A3B8">Shipping Total:</span>
              <span id="ship_total_display" style="font-weight:700;color:var(--tf-red);margin-left:6px">—</span></div>
          </div>
          <div class="form-group">
            <label>Notes</label>
            <input type="text" id="ship_notes" placeholder="e.g. 2 flatbeds, Conroe TX to Lubbock TX"/>
          </div>
        </div>
      </div>

      <!-- Fuel -->
      <div class="card" id="card-fuel">
        <div class="card-hdr gold"><span>⛽</span>Fuel &amp; Gas</div>
        <div class="card-body">
          <div class="grid4" style="margin-bottom:10px">
            <div class="form-group">
              <label># Vehicles</label>
              <input type="number" id="fuel_vehicles" value="1" min="0"
                onchange="calcFuel();renderSummary()"/>
            </div>
            <div class="form-group">
              <label>Round-Trip Miles</label>
              <input type="number" id="fuel_miles" value="0" min="0"
                onchange="calcFuel();renderSummary()"/>
            </div>
            <div class="form-group">
              <label>Avg MPG</label>
              <input type="number" id="fuel_mpg" value="12" min="1" step="0.5"
                onchange="calcFuel();renderSummary()"/>
            </div>
            <div class="form-group">
              <label>Gas Price ($/gal)</label>
              <input type="number" id="fuel_price_gal" value="3.50" min="0" step="0.05"
                onchange="calcFuel();renderSummary()"/>
            </div>
          </div>
          <div style="background:#1a2332;border-radius:6px;padding:10px;display:flex;gap:24px;flex-wrap:wrap">
            <div><span style="font-size:11px;color:#94A3B8">Total Gallons:</span>
              <span id="fuel_gal_display" style="font-weight:700;margin-left:6px">—</span></div>
            <div><span style="font-size:11px;color:#94A3B8">Fuel Total:</span>
              <span id="fuel_total_display" style="font-weight:700;color:var(--tf-red);margin-left:6px">—</span></div>
          </div>
        </div>
      </div>

      <!-- Hotels -->
      <div class="card" id="card-hotels">
        <div class="card-hdr blue"><span>🏨</span>Hotels</div>
        <div class="card-body">
          <div class="grid3" style="margin-bottom:10px">
            <div class="form-group">
              <label># Crew</label>
              <input type="number" id="hotel_crew" value="4" min="0"
                onchange="calcHotels();renderSummary()"/>
            </div>
            <div class="form-group">
              <label># Nights</label>
              <input type="number" id="hotel_nights" value="0" min="0"
                onchange="calcHotels();renderSummary()"/>
            </div>
            <div class="form-group">
              <label>Rate ($/night/room)</label>
              <input type="number" id="hotel_rate" value="110" min="0" step="5"
                onchange="calcHotels();renderSummary()"/>
            </div>
          </div>
          <div style="background:#0F172A;border-radius:6px;padding:10px;display:flex;gap:24px;flex-wrap:wrap">
            <div><span style="font-size:11px;color:#94A3B8">Room-Nights:</span>
              <span id="hotel_rooms_display" style="font-weight:700;margin-left:6px">—</span></div>
            <div><span style="font-size:11px;color:#94A3B8">Hotel Total:</span>
              <span id="hotel_total_display" style="font-weight:700;color:var(--tf-red);margin-left:6px">—</span></div>
          </div>
        </div>
      </div>

      <!-- Per Diem -->
      <div class="card" id="card-perdiem">
        <div class="card-hdr green"><span>🍽️</span>Per Diem</div>
        <div class="card-body">
          <div class="grid3" style="margin-bottom:10px">
            <div class="form-group">
              <label># Crew</label>
              <input type="number" id="pd_crew" value="4" min="0"
                onchange="calcPerDiem();renderSummary()"/>
            </div>
            <div class="form-group">
              <label># Days</label>
              <input type="number" id="pd_days" value="0" min="0"
                onchange="calcPerDiem();renderSummary()"/>
            </div>
            <div class="form-group">
              <label>Rate ($/day/person)</label>
              <input type="number" id="pd_rate" value="75" min="0" step="5"
                onchange="calcPerDiem();renderSummary()"/>
            </div>
          </div>
          <div style="background:#0F172A;border-radius:6px;padding:10px">
            <span style="font-size:11px;color:#94A3B8">Per Diem Total:</span>
            <span id="pd_total_display" style="font-weight:700;color:var(--tf-red);margin-left:6px">—</span>
          </div>
        </div>
      </div>

      <!-- Transportation of Crew -->
      <div class="card" id="card-transport">
        <div class="card-hdr gray"><span>🚐</span>Transportation of Crew</div>
        <div class="card-body">
          <div class="grid4" style="margin-bottom:10px">
            <div class="form-group">
              <label># Vehicles</label>
              <input type="number" id="trans_vehicles" value="1" min="0"
                onchange="calcTransport();renderSummary()"/>
            </div>
            <div class="form-group">
              <label>Round-Trip Miles</label>
              <input type="number" id="trans_miles" value="0" min="0"
                onchange="calcTransport();renderSummary()"/>
            </div>
            <div class="form-group">
              <label>Mileage Rate ($/mi)</label>
              <input type="number" id="trans_rate" value="0.67" min="0" step="0.01"
                onchange="calcTransport();renderSummary()"/>
            </div>
            <div class="form-group">
              <label>Trips</label>
              <input type="number" id="trans_trips" value="1" min="1"
                onchange="calcTransport();renderSummary()"/>
            </div>
          </div>
          <div style="background:#0F172A;border-radius:6px;padding:10px">
            <span style="font-size:11px;color:#94A3B8">Transportation Total:</span>
            <span id="trans_total_display" style="font-weight:700;color:var(--tf-red);margin-left:6px">—</span>
          </div>
          <div class="form-group" style="margin-top:10px">
            <label>Notes</label>
            <input type="text" id="trans_notes" placeholder="e.g. 3 trucks × 400 mi round trip to Austin"/>
          </div>
        </div>
      </div>

      <!-- Miscellaneous -->
      <div class="card" id="card-misc">
        <div class="card-hdr gold"><span>📦</span>Miscellaneous / Other</div>
        <div class="card-body">
          <table class="li-table">
            <thead><tr><th>Description</th><th>Amount ($)</th><th></th></tr></thead>
            <tbody id="misc_tbody"></tbody>
          </table>
          <button class="btn btn-outline btn-sm" style="margin-top:8px"
            onclick="addMiscItem()">+ Add Item</button>
        </div>
      </div>

      <!-- BOM Detail Breakdown (auto-populated from SA BOM) -->
      <div class="card" id="card-bom-detail" style="display:none">
        <div class="card-hdr" style="background:linear-gradient(135deg,#1E40AF 0%,#7C3AED 100%);color:#fff;cursor:pointer;"
          onclick="var b=document.getElementById('bom-detail-body');b.style.display=b.style.display==='none'?'block':'none'">
          <span>&#128203;</span>SA BOM Detail Breakdown
          <span style="margin-left:auto;font-size:10px;font-weight:400;opacity:0.8">Click to expand/collapse</span>
        </div>
        <div class="card-body" id="bom-detail-body" style="display:none;padding:0;">
          <div id="bom-detail-content" style="max-height:600px;overflow-y:auto;"></div>
        </div>
      </div>

    </div><!-- /tab-quote -->

    <!-- SUMMARY TAB -->
    <div id="tab-summary" style="display:none">
      <div class="stat-cards" id="stat-cards-summary"></div>
      <div class="card">
        <div class="card-hdr blue"><span>💰</span>Construction Quote Summary</div>
        <div class="card-body">
          <table class="summary-table" id="summary-table"></table>
        </div>
      </div>

      <!-- PROJECT INTELLIGENCE PANEL -->
      <div class="card" id="intelPanel" style="margin-top:16px;">
        <div class="card-hdr" style="background:linear-gradient(135deg,#0F172A 0%,#1E3A5F 100%);color:#fff;"><span>📊</span>Project Intelligence</div>
        <div class="card-body" id="intelBody">
          <div style="text-align:center;color:#94A3B8;font-size:13px;padding:12px;">Run a quote calculation to see project intelligence.</div>
        </div>
      </div>
    </div>

  </div><!-- /content -->
</div><!-- /main -->

<script>
// ─────────────────────────────────────────────
// STATE
// ─────────────────────────────────────────────
const equipItems = [];
const miscItems = [];
let concreteCost = 0, laborCost = 0, drillingCost = 0,
    shippingCost = 0, fuelCost = 0, hotelCost = 0,
    perDiemCost = 0, transportCost = 0;

function fmt(v) {
  return '$' + (v||0).toLocaleString('en-US', {minimumFractionDigits:2, maximumFractionDigits:2});
}
function numVal(id) { return parseFloat(document.getElementById(id)?.value) || 0; }
function strVal(id) { return (document.getElementById(id)?.value||'').trim(); }

function _flashField(el) {
    if (!el) return;
    el.classList.remove('tc-field-flash');
    void el.offsetWidth; // force reflow
    el.classList.add('tc-field-flash');
}

function _crToast(msg, type) {
    var t = document.createElement('div');
    t.style.cssText = 'position:fixed;top:20px;right:20px;z-index:9999;padding:12px 20px;border-radius:8px;font-size:13px;font-weight:600;color:#fff;box-shadow:0 4px 20px rgba(0,0,0,0.4);transition:opacity .5s;';
    t.style.background = type === 'success' ? '#16A34A' : type === 'error' ? '#DC2626' : '#3B82F6';
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(function(){ t.style.opacity = '0'; }, 2500);
    setTimeout(function(){ t.remove(); }, 3000);
}

// ─────────────────────────────────────────────
// URL PARAM PRE-FILL (from "Send to TC Quote" button on SA page)
// ─────────────────────────────────────────────
function prefillFromURL() {
  const p = new URLSearchParams(window.location.search);
  if (p.has('sa_cost')) {
    document.getElementById('sa_materials_cost').value = p.get('sa_cost');
  }
  if (p.has('n_cols')) {
    document.getElementById('sa_n_cols').value = p.get('n_cols');
    document.getElementById('conc_n_piers').value = p.get('n_cols');
    document.getElementById('drill_n_holes').value = p.get('n_cols');
  }
  if (p.has('footing')) {
    document.getElementById('sa_footing_depth').value = p.get('footing');
    document.getElementById('conc_depth_ft').value = p.get('footing');
  }
  if (p.has('proj_name')) document.getElementById('proj_name').value = p.get('proj_name');
  if (p.has('proj_code')) {
    document.getElementById('proj_code').value = 'TC-' + p.get('proj_code');
  }
  if (p.has('sa_quote')) document.getElementById('sa_quote_num').value = p.get('sa_quote');
  if (p.has('width')) document.getElementById('sa_width').value = p.get('width');
  if (p.has('length')) document.getElementById('sa_length').value = p.get('length');
  if (p.has('customer')) document.getElementById('proj_customer').value = p.get('customer');

  // Auto-load project data from ?project=JOB_CODE or ?proj_code=JOB_CODE
  // ALWAYS load metadata first (has customer name, project name from CRM)
  // Then: 1) Saved TC data  2) Full BOM  3) tc_import.json
  const resolvedProjectCode = p.get('project') || p.get('proj_code') || '';
  if (resolvedProjectCode) {
    const projCode = resolvedProjectCode;
    // Always load metadata FIRST — this has the canonical customer name
    autoLoadProjectMetadata(projCode, true).then(() => {
      tcLoadFromProject(projCode).then(loaded => {
        // After TC load, re-apply metadata to fill any gaps (customer name)
        autoLoadProjectMetadata(projCode, false);
        if (!loaded) {
          // No saved TC data — try full BOM auto-populate
          autoLoadFromBOM(projCode).then(bomLoaded => {
            if (!bomLoaded) {
              // Fall back to tc_import.json
              checkSAImport();
            }
          });
        }
      });
    });
  }
}

async function autoLoadProjectMetadata(jobCode, forceOverwrite) {
  try {
    const resp = await fetch('/api/project/metadata?job_code=' + encodeURIComponent(jobCode));
    const result = await resp.json();
    if (result.ok && result.metadata) {
      const m = result.metadata;
      // Always set project code and name from metadata
      const projCodeEl = document.getElementById('proj_code');
      if (projCodeEl) { projCodeEl.value = m.job_code || jobCode; _flashField(projCodeEl); }
      const projNameEl = document.getElementById('proj_name');
      if (projNameEl && (forceOverwrite || !projNameEl.value)) { projNameEl.value = m.project_name || ''; _flashField(projNameEl); }
      // Always set customer from metadata (this is the canonical source)
      if (m.customer && m.customer.name) {
        const custEl = document.getElementById('proj_customer');
        if (custEl) { custEl.value = m.customer.name; _flashField(custEl); }
      }
      if (m.location) {
        const addrEl = document.getElementById('proj_address');
        if (addrEl && (forceOverwrite || !addrEl.value)) { addrEl.value = m.location.street || ''; _flashField(addrEl); }
        const cityEl = document.getElementById('proj_city');
        if (cityEl && (forceOverwrite || !cityEl.value)) { cityEl.value = m.location.city || ''; _flashField(cityEl); }
        const stateEl = document.getElementById('proj_state');
        if (stateEl && (forceOverwrite || !stateEl.value)) { stateEl.value = m.location.state || ''; _flashField(stateEl); }
      }
      // Store project code for context bar
      window._tcProjectCode = jobCode;
      window._tcProjectName = m.project_name || jobCode;
    }
  } catch(e) { console.error('Metadata load failed:', e); }

  // Fetch real coil costs for this project
  try {
    const costResp = await fetch('/api/coils/lifecycle/cost-summary?job_code=' + encodeURIComponent(jobCode));
    const costData = await costResp.json();
    if (costData.ok && costData.summary && costData.summary.total_material_cost > 0) {
      // Show real coil cost banner
      var banner = document.getElementById('coil-cost-banner');
      if (!banner) {
        banner = document.createElement('div');
        banner.id = 'coil-cost-banner';
        banner.style.cssText = 'background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.3);border-radius:8px;padding:12px 16px;margin:12px 0;font-size:13px;color:#10b981;display:flex;align-items:center;gap:12px;flex-wrap:wrap;';
        var saSection = document.getElementById('sa_materials_cost');
        if (saSection && saSection.parentNode) {
          saSection.parentNode.insertBefore(banner, saSection.parentNode.firstChild);
        }
      }
      var realCost = costData.summary.total_material_cost;
      var perLft = costData.summary.cost_per_lft;
      var coilCount = costData.summary.coil_count;
      banner.innerHTML = '<span style="font-size:16px">&#x1F4CA;</span>' +
        '<span><strong>Real Coil Cost Data:</strong> $' + realCost.toLocaleString(undefined,{minimumFractionDigits:2}) + ' from ' + coilCount + ' coil' + (coilCount!==1?'s':'') + ' ($' + perLft.toFixed(2) + '/LFT)</span>' +
        '<button onclick="document.getElementById(\'sa_materials_cost\').value=' + realCost.toFixed(2) + ';if(typeof _flashField===\'function\')_flashField(document.getElementById(\'sa_materials_cost\'));if(typeof renderSummary===\'function\')renderSummary();" style="margin-left:auto;background:#10b981;color:#fff;border:none;border-radius:6px;padding:6px 14px;font-size:12px;font-weight:600;cursor:pointer">Use Real Cost</button>';
    }
  } catch(e) { console.warn('Coil cost fetch failed:', e); }
}

// ─────────────────────────────────────────────
// TAB SWITCHING
// ─────────────────────────────────────────────
function showTab(t) {
  document.getElementById('tab-quote').style.display = t==='quote' ? '' : 'none';
  document.getElementById('tab-summary').style.display = t==='summary' ? '' : 'none';
  document.querySelectorAll('#tabs .tab').forEach((el,i) => {
    el.classList.toggle('active', (t==='quote' && i===0) || (t==='summary' && i===1));
  });
  if (t === 'summary') renderSummary();
}

// ─────────────────────────────────────────────
// SYNC FROM SA VALUES
// ─────────────────────────────────────────────
function syncConcreteFromSA() {
  const nCols = numVal('sa_n_cols');
  const depth = numVal('sa_footing_depth');
  if (nCols > 0) {
    document.getElementById('conc_n_piers').value = nCols;
  }
  if (depth > 0) document.getElementById('conc_depth_ft').value = depth;
  calcConcrete();
  renderSummary();
}

// ─────────────────────────────────────────────
// CALCULATIONS
// ─────────────────────────────────────────────
function calcConcrete() {
  const n = numVal('conc_n_piers');
  const dia = numVal('conc_dia_in');
  const depth = numVal('conc_depth_ft');
  const priceCY = numVal('conc_price_cy');
  const rFt = (dia / 2) / 12;
  const volCY = Math.PI * rFt * rFt * depth / 27;
  const totalCY = n * volCY * 1.10;
  concreteCost = totalCY * priceCY;
  document.getElementById('conc_qty_display').textContent = totalCY.toFixed(2) + ' CY';
  document.getElementById('conc_cost_display').textContent = fmt(concreteCost);
  renderSummary();
}

function calcLabor() {
  const crew = numVal('lab_crew');
  const days = numVal('lab_days');
  const rate = numVal('lab_rate_hr');
  const hrs = numVal('lab_hrs_day');
  const daily = crew * rate * hrs;
  laborCost = daily * days;
  document.getElementById('lab_daily_display').textContent = fmt(daily) + '/day';
  document.getElementById('lab_total_display').textContent = fmt(laborCost);
  renderSummary();
}

function calcDrilling() {
  const method = document.getElementById('drill_method').value;
  const isRental = method === 'rental';
  document.getElementById('drill_rental_row').style.display = isRental ? '' : 'none';
  if (isRental) {
    drillingCost = (numVal('drill_rig_day') + numVal('drill_op_day')) * numVal('drill_days');
  } else {
    drillingCost = numVal('drill_n_holes') * numVal('drill_rate');
  }
  document.getElementById('drill_total_display').textContent = fmt(drillingCost);
  renderSummary();
}

function calcShipping() {
  const method = document.getElementById('ship_method').value;
  const isFlat = method === 'flat';
  document.getElementById('ship_flat_row').style.display = isFlat ? '' : 'none';
  document.getElementById('ship_rate_grp').style.display = isFlat ? 'none' : '';
  const loads = numVal('ship_loads') || 1;
  if (isFlat) {
    shippingCost = numVal('ship_flat_amt');
  } else {
    shippingCost = numVal('ship_miles') * numVal('ship_rate') * loads;
  }
  document.getElementById('ship_total_display').textContent = fmt(shippingCost);
  renderSummary();
}

function calcFuel() {
  const vehicles = numVal('fuel_vehicles');
  const miles = numVal('fuel_miles');
  const mpg = numVal('fuel_mpg') || 1;
  const priceGal = numVal('fuel_price_gal');
  const totalGal = vehicles * miles / mpg;
  fuelCost = totalGal * priceGal;
  document.getElementById('fuel_gal_display').textContent = totalGal.toFixed(1) + ' gal';
  document.getElementById('fuel_total_display').textContent = fmt(fuelCost);
  renderSummary();
}

function calcHotels() {
  const crew = numVal('hotel_crew');
  const nights = numVal('hotel_nights');
  const rate = numVal('hotel_rate');
  hotelCost = crew * nights * rate;
  document.getElementById('hotel_rooms_display').textContent = (crew * nights) + ' room-nights';
  document.getElementById('hotel_total_display').textContent = fmt(hotelCost);
  renderSummary();
}

function calcPerDiem() {
  const crew = numVal('pd_crew');
  const days = numVal('pd_days');
  const rate = numVal('pd_rate');
  perDiemCost = crew * days * rate;
  document.getElementById('pd_total_display').textContent = fmt(perDiemCost);
  renderSummary();
}

function calcTransport() {
  const vehicles = numVal('trans_vehicles');
  const miles = numVal('trans_miles');
  const rate = numVal('trans_rate');
  const trips = numVal('trans_trips') || 1;
  transportCost = vehicles * miles * rate * trips;
  document.getElementById('trans_total_display').textContent = fmt(transportCost);
  renderSummary();
}

function equipTotal() { return equipItems.reduce((s, i) => s + (i.qty * i.rate), 0); }
function miscTotal()  { return miscItems.reduce((s, i) => s + i.amount, 0); }

// ─────────────────────────────────────────────
// LINE ITEM TABLES
// ─────────────────────────────────────────────
function addEquipItem() {
  equipItems.push({ desc: '', qty: 1, unit: 'day', rate: 0 });
  renderEquipTable();
}
function removeEquipItem(idx) {
  equipItems.splice(idx, 1); renderEquipTable(); renderSummary();
}
function renderEquipTable() {
  const tbody = document.getElementById('equip_tbody');
  tbody.innerHTML = '';
  if (equipItems.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" style="color:#aaa;text-align:center;padding:10px">No equipment added.</td></tr>';
    renderSummary(); return;
  }
  equipItems.forEach((it, idx) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><input type="text" value="${it.desc}" placeholder="e.g. 40-ton Crane"
        style="width:100%" onchange="equipItems[${idx}].desc=this.value;renderSummary()"/></td>
      <td><input type="number" value="${it.qty}" min="0" step="0.5"
        style="width:60px" onchange="equipItems[${idx}].qty=parseFloat(this.value)||0;renderEquipTable();renderSummary()"/></td>
      <td><select onchange="equipItems[${idx}].unit=this.value">
        ${['day','week','trip','ea'].map(u=>`<option${it.unit===u?' selected':''}>${u}</option>`).join('')}
      </select></td>
      <td><input type="number" value="${it.rate}" min="0" step="50"
        style="width:80px" onchange="equipItems[${idx}].rate=parseFloat(this.value)||0;renderEquipTable();renderSummary()"/></td>
      <td style="font-weight:700">${fmt(it.qty * it.rate)}</td>
      <td><button class="btn btn-danger btn-sm" onclick="removeEquipItem(${idx})">✕</button></td>`;
    tbody.appendChild(tr);
  });
  const totalTr = document.createElement('tr');
  totalTr.className = 'total-row';
  totalTr.innerHTML = `<td colspan="4" style="text-align:right">Equipment Total:</td><td colspan="2">${fmt(equipTotal())}</td>`;
  tbody.appendChild(totalTr);
}

function addMiscItem() {
  miscItems.push({ desc: '', amount: 0 }); renderMiscTable();
}
function removeMiscItem(idx) {
  miscItems.splice(idx, 1); renderMiscTable(); renderSummary();
}
function renderMiscTable() {
  const tbody = document.getElementById('misc_tbody');
  tbody.innerHTML = '';
  if (miscItems.length === 0) {
    tbody.innerHTML = '<tr><td colspan="3" style="color:#aaa;text-align:center;padding:10px">No misc items.</td></tr>';
    renderSummary(); return;
  }
  miscItems.forEach((it, idx) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><input type="text" value="${it.desc}" placeholder="Description"
        style="width:100%" onchange="miscItems[${idx}].desc=this.value;renderSummary()"/></td>
      <td><input type="number" value="${it.amount}" min="0" step="100"
        style="width:120px" onchange="miscItems[${idx}].amount=parseFloat(this.value)||0;renderSummary()"/></td>
      <td><button class="btn btn-danger btn-sm" onclick="removeMiscItem(${idx})">✕</button></td>`;
    tbody.appendChild(tr);
  });
  const totalTr = document.createElement('tr');
  totalTr.className = 'total-row';
  totalTr.innerHTML = `<td style="text-align:right">Misc Total:</td><td colspan="2">${fmt(miscTotal())}</td>`;
  tbody.appendChild(totalTr);
}

// ─────────────────────────────────────────────
// SUMMARY
// ─────────────────────────────────────────────
function buildQuoteData() {
  const markup = numVal('proj_markup') / 100;
  const mats = numVal('sa_materials_cost');
  const equip = equipTotal();
  const misc = miscTotal();
  const sections = [
    { label: 'Materials (SA Fabrication)', cost: mats, key: 'materials' },
    { label: 'Concrete (Pier Footings)', cost: concreteCost, key: 'concrete' },
    { label: 'Labor — Installation', cost: laborCost, key: 'labor' },
    { label: 'Equipment Rental', cost: equip, key: 'equipment' },
    { label: 'Drilling', cost: drillingCost, key: 'drilling' },
    { label: 'Shipping & Freight', cost: shippingCost, key: 'shipping' },
    { label: 'Fuel & Gas', cost: fuelCost, key: 'fuel' },
    { label: 'Hotels', cost: hotelCost, key: 'hotels' },
    { label: 'Per Diem', cost: perDiemCost, key: 'perdiem' },
    { label: 'Transportation of Crew', cost: transportCost, key: 'transport' },
    { label: 'Miscellaneous', cost: misc, key: 'misc' },
  ];
  const subtotal = sections.reduce((s, x) => s + x.cost, 0);
  const markupAmt = subtotal * markup;
  const total = subtotal + markupAmt;
  return { sections, subtotal, markupAmt, total, markup, markupPct: numVal('proj_markup') };
}

function renderSummary() {
  const q = buildQuoteData();
  const sc = document.getElementById('stat-cards-summary');
  if (sc) sc.innerHTML = `
    <div class="stat"><div class="val">${fmt(q.subtotal)}</div><div class="lbl">Subtotal (cost)</div></div>
    <div class="stat"><div class="val">${fmt(q.markupAmt)}</div><div class="lbl">Markup (${q.markupPct}%)</div></div>
    <div class="stat" style="border-color:var(--tf-red)"><div class="val" style="color:var(--tf-red)">${fmt(q.total)}</div><div class="lbl">Total Sell Price</div></div>
    <div class="stat"><div class="val">${q.sections.filter(s=>s.cost>0).length}</div><div class="lbl">Cost Categories</div></div>`;
  const tbl = document.getElementById('summary-table');
  if (!tbl) return;
  let rows = '';
  q.sections.forEach(s => {
    if (s.cost === 0) return;
    rows += `<tr><td>${s.label}</td><td style="text-align:right;font-weight:600">${fmt(s.cost)}</td></tr>`;
  });
  rows += `
    <tr class="subtotal-row"><td><strong>SUBTOTAL</strong></td><td style="text-align:right"><strong>${fmt(q.subtotal)}</strong></td></tr>
    <tr class="markup-row"><td>Markup (${q.markupPct}%)</td><td style="text-align:right">${fmt(q.markupAmt)}</td></tr>
    <tr class="total-row"><td>TOTAL SELL PRICE</td><td style="text-align:right">${fmt(q.total)}</td></tr>`;
  tbl.innerHTML = rows;

  // Render Intelligence Panel
  renderIntelligence(q);

  // Update sticky total
  var stickyM = document.getElementById('stickyMaterials');
  var stickyI = document.getElementById('stickyInstall');
  var stickyG = document.getElementById('stickyGrand');
  var stickySF = document.getElementById('stickyPerSqFt');
  var materials = numVal('sa_materials_cost');
  var install = q.subtotal - materials;
  var grand = q.total;
  if (stickyM) stickyM.textContent = '$' + materials.toLocaleString(undefined, {minimumFractionDigits:0, maximumFractionDigits:0});
  if (stickyI) stickyI.textContent = '$' + install.toLocaleString(undefined, {minimumFractionDigits:0, maximumFractionDigits:0});
  if (stickyG) stickyG.textContent = '$' + grand.toLocaleString(undefined, {minimumFractionDigits:0, maximumFractionDigits:0});
  var sqft = numVal('sa_width') * numVal('sa_length');
  if (stickySF) stickySF.textContent = (sqft > 0 && grand > 0) ? ('$' + (grand / sqft).toFixed(2)) : '--';
}

function renderIntelligence(q) {
  const body = document.getElementById('intelBody');
  if (!body) return;
  if (q.total <= 0) {
    body.innerHTML = '<div style="text-align:center;color:#94A3B8;font-size:13px;padding:12px;">Run a quote calculation to see project intelligence.</div>';
    return;
  }

  const w = numVal('sa_width') || 0;
  const l = numVal('sa_length') || 0;
  const sqft = w * l;
  const pricePerSqft = sqft > 0 ? (q.total / sqft) : 0;

  // Estimate steel weight from SA materials cost (~$0.50/lb typical)
  const saMat = numVal('sa_materials_cost') || 0;
  const estWeight = saMat > 0 ? Math.round(saMat / 0.50) : 0;

  // Gather checked options/sections
  const activeSections = q.sections.filter(s => s.cost > 0).map(s => s.label);

  let html = '<table style="width:100%;font-size:13px;border-collapse:collapse;">';

  html += '<tr style="border-bottom:1px solid #334155;"><td style="padding:8px 0;color:#64748B;font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.4px;">Sell Price</td>';
  html += '<td style="padding:8px 0;text-align:right;font-weight:700;font-size:16px;color:#059669;">' + fmt(q.total) + '</td></tr>';

  if (pricePerSqft > 0) {
    html += '<tr style="border-bottom:1px solid #334155;"><td style="padding:8px 0;color:#64748B;font-weight:600;font-size:11px;text-transform:uppercase;">Price / Sq Ft</td>';
    html += '<td style="padding:8px 0;text-align:right;font-weight:700;font-size:16px;">$' + pricePerSqft.toFixed(2) + '</td></tr>';
  }

  if (sqft > 0) {
    html += '<tr style="border-bottom:1px solid #334155;"><td style="padding:8px 0;color:#64748B;font-weight:600;font-size:11px;text-transform:uppercase;">Square Footage</td>';
    html += '<td style="padding:8px 0;text-align:right;font-weight:700;font-size:16px;">' + sqft.toLocaleString() + ' sq ft</td></tr>';
  }

  if (estWeight > 0) {
    html += '<tr style="border-bottom:1px solid #334155;"><td style="padding:8px 0;color:#64748B;font-weight:600;font-size:11px;text-transform:uppercase;">Est. Steel Weight</td>';
    html += '<td style="padding:8px 0;text-align:right;font-weight:700;font-size:16px;">' + estWeight.toLocaleString() + ' lbs</td></tr>';
  }

  html += '<tr style="border-bottom:1px solid #334155;"><td style="padding:8px 0;color:#64748B;font-weight:600;font-size:11px;text-transform:uppercase;">Cost Categories Used</td>';
  html += '<td style="padding:8px 0;text-align:right;font-weight:700;font-size:16px;">' + activeSections.length + '</td></tr>';

  html += '<tr style="border-bottom:1px solid #334155;"><td style="padding:8px 0;color:#64748B;font-weight:600;font-size:11px;text-transform:uppercase;">Markup</td>';
  html += '<td style="padding:8px 0;text-align:right;font-weight:700;font-size:16px;">' + q.markupPct + '%</td></tr>';

  html += '</table>';

  // Suggestions
  html += '<div style="margin-top:12px;padding-top:12px;border-top:1px solid #334155;">';
  html += '<div style="font-size:11px;font-weight:700;color:#94A3B8;text-transform:uppercase;letter-spacing:.4px;margin-bottom:8px;">Suggested Next Steps</div>';

  const suggestions = [];
  if (saMat <= 0) suggestions.push('Add SA materials cost from the Structures America Estimator for a complete quote');
  if (sqft <= 0) suggestions.push('Add structure width and length for price/sq ft analysis');
  if (q.markupPct < 10) suggestions.push('Markup seems low — consider increasing for overhead and profit');
  if (q.markupPct > 50) suggestions.push('Markup is high — verify this is competitive for the market');
  const crewDays = numVal('lab_days') || 0;
  if (crewDays > 5) suggestions.push('Long install duration — consider travel cost optimization');
  if (activeSections.length < 3) suggestions.push('Several cost categories have $0 — review before sending quote');
  if (suggestions.length === 0) suggestions.push('Quote looks complete — generate PDF and send to customer');

  suggestions.forEach(s => {
    html += '<div style="display:flex;gap:8px;padding:4px 0;font-size:13px;color:#94A3B8;"><span style="color:#F59E0B;font-weight:700;flex-shrink:0;">&#9658;</span><span>' + s + '</span></div>';
  });

  html += '</div>';
  body.innerHTML = html;
}

// ─────────────────────────────────────────────
// EXPORT PAYLOAD
// ─────────────────────────────────────────────
function buildPayload() {
  const q = buildQuoteData();
  return {
    project: {
      name: strVal('proj_name'), job_code: strVal('proj_code'),
      customer_name: strVal('proj_customer'), address: strVal('proj_address'),
      city: strVal('proj_city'), state: strVal('proj_state'),
      quote_date: strVal('proj_date'), markup_pct: numVal('proj_markup'),
    },
    salesperson: {
      name: strVal('sp_name'), title: strVal('sp_title'),
      phone: strVal('sp_phone'), email: strVal('sp_email'),
    },
    sa: {
      quote_num: strVal('sa_quote_num'), materials_cost: numVal('sa_materials_cost'),
      n_cols: numVal('sa_n_cols'), footing_depth: numVal('sa_footing_depth'),
      width_ft: numVal('sa_width'), length_ft: numVal('sa_length'),
    },
    costs: {
      concrete: { n_piers: numVal('conc_n_piers'), dia_in: numVal('conc_dia_in'),
        depth_ft: numVal('conc_depth_ft'), price_cy: numVal('conc_price_cy'), total: concreteCost },
      labor: { crew: numVal('lab_crew'), days: numVal('lab_days'),
        rate_hr: numVal('lab_rate_hr'), hrs_day: numVal('lab_hrs_day'),
        notes: strVal('lab_notes'), total: laborCost },
      equipment: { items: equipItems, total: equipTotal() },
      drilling: { method: document.getElementById('drill_method').value,
        n_holes: numVal('drill_n_holes'), rate: numVal('drill_rate'),
        rig_day: numVal('drill_rig_day'), op_day: numVal('drill_op_day'),
        days: numVal('drill_days'), total: drillingCost },
      shipping: { method: document.getElementById('ship_method').value,
        miles: numVal('ship_miles'), rate: numVal('ship_rate'),
        flat_amt: numVal('ship_flat_amt'), loads: numVal('ship_loads'),
        notes: strVal('ship_notes'), total: shippingCost },
      fuel: { vehicles: numVal('fuel_vehicles'), miles: numVal('fuel_miles'),
        mpg: numVal('fuel_mpg'), price_gal: numVal('fuel_price_gal'), total: fuelCost },
      hotels: { crew: numVal('hotel_crew'), nights: numVal('hotel_nights'),
        rate: numVal('hotel_rate'), total: hotelCost },
      per_diem: { crew: numVal('pd_crew'), days: numVal('pd_days'),
        rate: numVal('pd_rate'), total: perDiemCost },
      transport: { vehicles: numVal('trans_vehicles'), miles: numVal('trans_miles'),
        rate: numVal('trans_rate'), trips: numVal('trans_trips'),
        notes: strVal('trans_notes'), total: transportCost },
      misc: { items: miscItems, total: miscTotal() },
    },
    summary: q,
  };
}

// ─────────────────────────────────────────────
// EXPORTS
// ─────────────────────────────────────────────
async function tcExportPDF() {
  try {
    const resp = await fetch('/tc/export/pdf', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify(buildPayload())
    });
    if (!resp.ok) { alert('PDF failed: ' + await resp.text()); return; }
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = (strVal('proj_code') || 'TC-Quote') + '.pdf';
    a.click();
  } catch(e) { alert('Error: ' + e.message); }
}

async function tcExportExcel() {
  try {
    const resp = await fetch('/tc/export/excel', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify(buildPayload())
    });
    if (!resp.ok) { alert('Excel failed: ' + await resp.text()); return; }
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = (strVal('proj_code') || 'TC-Quote') + '.xlsx';
    a.click();
  } catch(e) { alert('Error: ' + e.message); }
}

// ─────────────────────────────────────────────
// TC SAVE / LOAD PER PROJECT
// ─────────────────────────────────────────────
async function tcSaveProject() {
  const payload = buildPayload();
  const jobCode = payload.project.job_code || '';
  if (!jobCode) {
    alert('Cannot save: no Job Code set. Fill in the Job Code field first.');
    return;
  }
  // Strip TC- prefix if present for storage
  payload.job_code = jobCode.replace(/^TC-/i, '');
  const statusEl = document.getElementById('tc-save-status');
  statusEl.textContent = 'Saving...';
  try {
    const resp = await fetch('/api/tc/save', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
    const data = await resp.json();
    if (data.ok) {
      statusEl.textContent = 'Saved v' + data.version + ' at ' + new Date().toLocaleTimeString();
      statusEl.style.color = '#10B981';
    } else {
      statusEl.textContent = 'Save failed: ' + (data.error || 'Unknown error');
      statusEl.style.color = '#EF4444';
    }
  } catch(e) {
    statusEl.textContent = 'Save error: ' + e.message;
    statusEl.style.color = '#EF4444';
  }
}

async function tcLoadFromProject(jobCode) {
  try {
    const resp = await fetch('/api/tc/load', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ job_code: jobCode })
    });
    const result = await resp.json();
    if (!result.ok || !result.data) return false;
    const d = result.data;

    // Populate project fields
    if (d.project) {
      const p = d.project;
      if (p.job_code) document.getElementById('proj_code').value = p.job_code;
      if (p.name) document.getElementById('proj_name').value = p.name;
      if (p.customer_name) document.getElementById('proj_customer').value = p.customer_name;
      if (p.address) document.getElementById('proj_address').value = p.address;
      if (p.city) document.getElementById('proj_city').value = p.city;
      if (p.state) document.getElementById('proj_state').value = p.state;
      if (p.quote_date) document.getElementById('proj_date').value = p.quote_date;
      if (p.markup_pct != null) document.getElementById('proj_markup').value = p.markup_pct;
    }
    // Populate salesperson
    if (d.salesperson) {
      const s = d.salesperson;
      if (s.name) document.getElementById('sp_name').value = s.name;
      if (s.title) document.getElementById('sp_title').value = s.title;
      if (s.phone) document.getElementById('sp_phone').value = s.phone;
      if (s.email) document.getElementById('sp_email').value = s.email;
    }
    // Populate SA import fields
    if (d.sa) {
      const sa = d.sa;
      if (sa.quote_num) document.getElementById('sa_quote_num').value = sa.quote_num;
      if (sa.materials_cost != null) document.getElementById('sa_materials_cost').value = sa.materials_cost;
      if (sa.n_cols) { document.getElementById('sa_n_cols').value = sa.n_cols; document.getElementById('conc_n_piers').value = sa.n_cols; document.getElementById('drill_n_holes').value = sa.n_cols; }
      if (sa.footing_depth) { document.getElementById('sa_footing_depth').value = sa.footing_depth; document.getElementById('conc_depth_ft').value = sa.footing_depth; }
      if (sa.width_ft) document.getElementById('sa_width').value = sa.width_ft;
      if (sa.length_ft) document.getElementById('sa_length').value = sa.length_ft;
    }
    // Populate cost fields
    if (d.costs) {
      const c = d.costs;
      if (c.concrete) {
        if (c.concrete.dia_in) document.getElementById('conc_dia_in').value = c.concrete.dia_in;
        if (c.concrete.price_cy) document.getElementById('conc_price_cy').value = c.concrete.price_cy;
      }
      if (c.labor) {
        if (c.labor.crew) document.getElementById('lab_crew').value = c.labor.crew;
        if (c.labor.days) document.getElementById('lab_days').value = c.labor.days;
        if (c.labor.rate_hr) document.getElementById('lab_rate_hr').value = c.labor.rate_hr;
        if (c.labor.hrs_day) document.getElementById('lab_hrs_day').value = c.labor.hrs_day;
        if (c.labor.notes) document.getElementById('lab_notes').value = c.labor.notes;
      }
      if (c.drilling) {
        if (c.drilling.method) document.getElementById('drill_method').value = c.drilling.method;
        if (c.drilling.rate) document.getElementById('drill_rate').value = c.drilling.rate;
        if (c.drilling.rig_day) document.getElementById('drill_rig_day').value = c.drilling.rig_day;
        if (c.drilling.op_day) document.getElementById('drill_op_day').value = c.drilling.op_day;
        if (c.drilling.days) document.getElementById('drill_days').value = c.drilling.days;
      }
      if (c.shipping) {
        if (c.shipping.method) document.getElementById('ship_method').value = c.shipping.method;
        if (c.shipping.miles) document.getElementById('ship_miles').value = c.shipping.miles;
        if (c.shipping.rate) document.getElementById('ship_rate').value = c.shipping.rate;
        if (c.shipping.flat_amt) document.getElementById('ship_flat_amt').value = c.shipping.flat_amt;
        if (c.shipping.loads) document.getElementById('ship_loads').value = c.shipping.loads;
        if (c.shipping.notes) document.getElementById('ship_notes').value = c.shipping.notes;
      }
      if (c.fuel) {
        if (c.fuel.vehicles) document.getElementById('fuel_vehicles').value = c.fuel.vehicles;
        if (c.fuel.miles) document.getElementById('fuel_miles').value = c.fuel.miles;
        if (c.fuel.mpg) document.getElementById('fuel_mpg').value = c.fuel.mpg;
        if (c.fuel.price_gal) document.getElementById('fuel_price_gal').value = c.fuel.price_gal;
      }
      if (c.hotels) {
        if (c.hotels.crew) document.getElementById('hotel_crew').value = c.hotels.crew;
        if (c.hotels.nights) document.getElementById('hotel_nights').value = c.hotels.nights;
        if (c.hotels.rate) document.getElementById('hotel_rate').value = c.hotels.rate;
      }
      if (c.per_diem) {
        if (c.per_diem.crew) document.getElementById('pd_crew').value = c.per_diem.crew;
        if (c.per_diem.days) document.getElementById('pd_days').value = c.per_diem.days;
        if (c.per_diem.rate) document.getElementById('pd_rate').value = c.per_diem.rate;
      }
      if (c.transport) {
        if (c.transport.vehicles) document.getElementById('trans_vehicles').value = c.transport.vehicles;
        if (c.transport.miles) document.getElementById('trans_miles').value = c.transport.miles;
        if (c.transport.rate) document.getElementById('trans_rate').value = c.transport.rate;
        if (c.transport.trips) document.getElementById('trans_trips').value = c.transport.trips;
        if (c.transport.notes) document.getElementById('trans_notes').value = c.transport.notes;
      }
    }
    // Recalculate all after loading
    calcConcrete(); calcLabor(); calcDrilling();
    calcShipping(); calcFuel(); calcHotels();
    calcPerDiem(); calcTransport(); renderSummary();

    const statusEl = document.getElementById('tc-save-status');
    if (statusEl) {
      statusEl.textContent = 'Loaded v' + (d.version || '?') + ' (saved ' + (d.saved_at || '').substring(0, 10) + ')';
      statusEl.style.color = '#1E40AF';
    }
    return true;
  } catch(e) { return false; }
}

// ─────────────────────────────────────────────
// FULL BOM AUTO-LOAD
// ─────────────────────────────────────────────
async function autoLoadFromBOM(jobCode) {
  try {
    const resp = await fetch('/api/project/' + encodeURIComponent(jobCode) + '/bom');
    const result = await resp.json();
    if (!result.ok || !result.has_bom) return false;

    // Populate project info from metadata
    await autoLoadProjectMetadata(jobCode);

    // Set the total materials cost
    if (result.total_sell_price && numVal('sa_materials_cost') === 0) {
      document.getElementById('sa_materials_cost').value = result.total_sell_price;
    }

    // Build BOM detail breakdown
    const detailCard = document.getElementById('card-bom-detail');
    const detailContent = document.getElementById('bom-detail-content');
    if (!detailCard || !detailContent) return false;

    let totalWeight = result.total_weight_lbs || 0;
    let totalCost = result.total_material_cost || 0;
    let totalSell = result.total_sell_price || 0;
    let nColumns = 0;

    let html = '';
    const buildings = result.buildings || [];

    buildings.forEach(function(bldg, bIdx) {
      const bName = bldg.building_name || ('Building ' + (bIdx + 1));
      const bW = Math.round(bldg.width_ft || 0);
      const bL = Math.round(bldg.length_ft || 0);

      html += '<div style="border-bottom:1px solid #334155;padding:12px 14px;">';
      html += '<div style="font-weight:700;color:#93C5FD;font-size:13px;margin-bottom:8px;">';
      html += bName + (bW && bL ? " (" + bW + "' x " + bL + "')" : '') + '</div>';

      // Group line items by category
      var categories = {};
      (bldg.line_items || []).forEach(function(item) {
        var cat = item.category || 'Other';
        if (!categories[cat]) categories[cat] = [];
        categories[cat].push(item);
      });

      // Count columns
      Object.keys(categories).forEach(function(cat) {
        if (cat.toLowerCase().indexOf('column') >= 0) {
          categories[cat].forEach(function(item) {
            nColumns += (item.qty || item.piece_count || 0);
          });
        }
      });

      html += '<table style="width:100%;border-collapse:collapse;font-size:12px;">';
      html += '<thead><tr style="background:#1E293B;color:#94A3B8;">';
      html += '<th style="text-align:left;padding:6px 8px;">Category</th>';
      html += '<th style="text-align:left;padding:6px 8px;">Description</th>';
      html += '<th style="text-align:right;padding:6px 8px;">Qty</th>';
      html += '<th style="text-align:left;padding:6px 8px;">Unit</th>';
      html += '<th style="text-align:right;padding:6px 8px;">Weight (lbs)</th>';
      if (result.show_costs) {
        html += '<th style="text-align:right;padding:6px 8px;">Unit Cost</th>';
        html += '<th style="text-align:right;padding:6px 8px;">Ext Cost</th>';
      }
      html += '</tr></thead><tbody>';

      var catColors = {
        'Structural Steel': '#EF4444', 'Columns': '#EF4444', 'Rafters': '#EF4444',
        'Panels': '#3B82F6', 'Wall Panels': '#3B82F6', 'Roof Panels': '#3B82F6',
        'Trim': '#F59E0B', 'Fasteners': '#8B5CF6', 'Accessories': '#10B981',
        'Purlins': '#EC4899', 'Foundation': '#6B7280', 'Girts': '#14B8A6',
      };

      Object.keys(categories).forEach(function(cat) {
        var items = categories[cat];
        var catTotal = 0;
        var catWeight = 0;
        var catColor = catColors[cat] || '#6B7280';

        items.forEach(function(item) {
          catWeight += (item.total_weight_lbs || 0);
          catTotal += (item.total_cost || 0);
          html += '<tr style="border-bottom:1px solid #1E293B;">';
          html += '<td style="padding:4px 8px;"><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:' + catColor + ';margin-right:6px;"></span>' + cat + '</td>';
          html += '<td style="padding:4px 8px;color:#E2E8F0;">' + (item.description || '') + '</td>';
          html += '<td style="padding:4px 8px;text-align:right;color:#E2E8F0;">' + (item.qty || item.piece_count || 0) + '</td>';
          html += '<td style="padding:4px 8px;color:#94A3B8;">' + (item.unit || 'ea') + '</td>';
          html += '<td style="padding:4px 8px;text-align:right;color:#E2E8F0;">' + Math.round(item.total_weight_lbs || 0).toLocaleString() + '</td>';
          if (result.show_costs) {
            html += '<td style="padding:4px 8px;text-align:right;color:#93C5FD;">$' + (item.unit_cost || 0).toFixed(2) + '</td>';
            html += '<td style="padding:4px 8px;text-align:right;color:#6EE7B7;">$' + (item.total_cost || 0).toFixed(2) + '</td>';
          }
          html += '</tr>';
        });

        // Category subtotal row
        html += '<tr style="background:#0F172A;font-weight:600;">';
        html += '<td colspan="4" style="padding:4px 8px;text-align:right;color:#94A3B8;font-size:11px;">' + cat + ' Subtotal:</td>';
        html += '<td style="padding:4px 8px;text-align:right;color:#F6AE2D;">' + Math.round(catWeight).toLocaleString() + '</td>';
        if (result.show_costs) {
          html += '<td style="padding:4px 8px;"></td>';
          html += '<td style="padding:4px 8px;text-align:right;color:#F6AE2D;">$' + catTotal.toFixed(2) + '</td>';
        }
        html += '</tr>';
      });

      html += '</tbody></table>';

      // Building totals
      html += '<div style="display:flex;gap:16px;flex-wrap:wrap;padding:8px 0;font-size:11px;color:#94A3B8;">';
      html += '<span>Weight: <strong style="color:#E2E8F0;">' + Math.round(bldg.total_weight_lbs || 0).toLocaleString() + ' lbs</strong></span>';
      if (result.show_costs && bldg.total_sell_price) {
        html += '<span>Material Sell: <strong style="color:#6EE7B7;">$' + (bldg.total_sell_price || 0).toFixed(2) + '</strong></span>';
      }
      html += '</div>';
      html += '</div>';
    });

    // Grand totals banner
    html += '<div style="padding:12px 14px;background:#0F172A;display:flex;gap:24px;flex-wrap:wrap;font-size:12px;">';
    html += '<div><span style="color:#94A3B8;">Total Weight:</span> <strong style="color:#E2E8F0;">' + Math.round(totalWeight).toLocaleString() + ' lbs</strong></div>';
    if (result.show_costs) {
      html += '<div><span style="color:#94A3B8;">Material Cost:</span> <strong style="color:#93C5FD;">$' + totalCost.toFixed(2) + '</strong></div>';
      html += '<div><span style="color:#94A3B8;">Sell Price:</span> <strong style="color:#6EE7B7;">$' + totalSell.toFixed(2) + '</strong></div>';
    }
    html += '<div><span style="color:#94A3B8;">Buildings:</span> <strong style="color:#E2E8F0;">' + buildings.length + '</strong></div>';
    html += '</div>';

    detailContent.innerHTML = html;
    detailCard.style.display = '';

    // Auto-fill column count for concrete/drilling
    if (nColumns > 0 && numVal('sa_n_cols') === 0) {
      document.getElementById('sa_n_cols').value = nColumns;
      document.getElementById('conc_n_piers').value = nColumns;
      document.getElementById('drill_n_holes').value = nColumns;
    }

    // Auto-fill building dimensions from first building
    if (buildings.length > 0) {
      var b0 = buildings[0];
      if (b0.width_ft && numVal('sa_width') <= 40) document.getElementById('sa_width').value = b0.width_ft;
      if (b0.length_ft && numVal('sa_length') <= 180) document.getElementById('sa_length').value = b0.length_ft;
    }

    // Show SA import banner
    var banner = document.getElementById('sa-import-banner');
    if (banner && totalSell > 0) {
      banner.style.display = 'block';
      document.getElementById('sa-import-cost-lbl').textContent = fmt(totalSell);
      var dateLbl = document.getElementById('sa-import-date-lbl');
      if (dateLbl) dateLbl.textContent = '(auto-populated from BOM)';
      var hint = document.getElementById('sa-import-hint');
      if (hint) hint.style.display = 'none';
    }

    syncConcreteFromSA();
    calcConcrete(); calcDrilling();
    renderSummary();
    return true;
  } catch(e) {
    console.warn('BOM auto-load failed:', e);
    return false;
  }
}

// ─────────────────────────────────────────────
// SA IMPORT AUTO-LOAD
// ─────────────────────────────────────────────
async function checkSAImport() {
  // Get job code from URL or form field
  const p = new URLSearchParams(window.location.search);
  let jobCode = p.get('project') || p.get('proj_code') || '';
  if (!jobCode) {
    const codeEl = document.getElementById('proj_code');
    jobCode = (codeEl ? codeEl.value : '').replace(/^TC-/i, '').trim();
  }
  if (!jobCode) return;

  try {
    const resp = await fetch('/api/sa/tc-import?job_code=' + encodeURIComponent(jobCode));
    const result = await resp.json();
    if (result.ok && result.data) {
      applySAImport(result.data);
    }
  } catch(e) { /* silent */ }
}

function applySAImport(data) {
  // Only auto-fill if SA materials cost is currently 0 (don't overwrite user edits)
  const currentCost = numVal('sa_materials_cost');
  if (currentCost > 0 && data.total_sell_price > 0 && currentCost !== data.total_sell_price) {
    // Already has a value, just show the banner
  }

  if (data.total_sell_price && (currentCost === 0 || currentCost === data.total_sell_price)) {
    document.getElementById('sa_materials_cost').value = data.total_sell_price;
    _flashField(document.getElementById('sa_materials_cost'));
  }
  if (data.n_columns && numVal('sa_n_cols') === 0) {
    document.getElementById('sa_n_cols').value = data.n_columns; _flashField(document.getElementById('sa_n_cols'));
    document.getElementById('conc_n_piers').value = data.n_columns; _flashField(document.getElementById('conc_n_piers'));
    document.getElementById('drill_n_holes').value = data.n_columns; _flashField(document.getElementById('drill_n_holes'));
  }
  if (data.footing_depth_ft) {
    document.getElementById('sa_footing_depth').value = data.footing_depth_ft; _flashField(document.getElementById('sa_footing_depth'));
    document.getElementById('conc_depth_ft').value = data.footing_depth_ft; _flashField(document.getElementById('conc_depth_ft'));
  }
  if (data.width_ft) { document.getElementById('sa_width').value = data.width_ft; _flashField(document.getElementById('sa_width')); }
  if (data.length_ft) { document.getElementById('sa_length').value = data.length_ft; _flashField(document.getElementById('sa_length')); }
  if (data.sa_quote_num) { document.getElementById('sa_quote_num').value = data.sa_quote_num; _flashField(document.getElementById('sa_quote_num')); }
  if (data.project_name && !strVal('proj_name')) { document.getElementById('proj_name').value = data.project_name; _flashField(document.getElementById('proj_name')); }

  // Show banner
  const banner = document.getElementById('sa-import-banner');
  if (banner && data.total_sell_price > 0) {
    banner.style.display = 'block';
    document.getElementById('sa-import-cost-lbl').textContent = fmt(data.total_sell_price);
    const dateLbl = document.getElementById('sa-import-date-lbl');
    if (dateLbl && data.transferred_at) {
      dateLbl.textContent = '(imported ' + data.transferred_at.substring(0, 10) + ')';
    }
    // Hide the hint
    const hint = document.getElementById('sa-import-hint');
    if (hint) hint.style.display = 'none';
  }

  // Recalculate
  syncConcreteFromSA();
  calcConcrete(); calcDrilling();
  renderSummary();
}

async function refreshSAImport() {
  const p = new URLSearchParams(window.location.search);
  let jobCode = p.get('project') || p.get('proj_code') || '';
  if (!jobCode) {
    const codeEl = document.getElementById('proj_code');
    jobCode = (codeEl ? codeEl.value : '').replace(/^TC-/i, '').trim();
  }
  if (!jobCode) { alert('No project code to refresh from.'); return; }

  try {
    const resp = await fetch('/api/sa/tc-import?job_code=' + encodeURIComponent(jobCode));
    const result = await resp.json();
    if (result.ok && result.data) {
      // Force update even if values exist
      const data = result.data;
      if (data.total_sell_price) document.getElementById('sa_materials_cost').value = data.total_sell_price;
      if (data.n_columns) {
        document.getElementById('sa_n_cols').value = data.n_columns;
        document.getElementById('conc_n_piers').value = data.n_columns;
        document.getElementById('drill_n_holes').value = data.n_columns;
      }
      if (data.footing_depth_ft) {
        document.getElementById('sa_footing_depth').value = data.footing_depth_ft;
        document.getElementById('conc_depth_ft').value = data.footing_depth_ft;
      }
      if (data.width_ft) document.getElementById('sa_width').value = data.width_ft;
      if (data.length_ft) document.getElementById('sa_length').value = data.length_ft;
      if (data.sa_quote_num) document.getElementById('sa_quote_num').value = data.sa_quote_num;

      // Update banner
      const banner = document.getElementById('sa-import-banner');
      if (banner) {
        banner.style.display = 'block';
        document.getElementById('sa-import-cost-lbl').textContent = fmt(data.total_sell_price || 0);
        const dateLbl = document.getElementById('sa-import-date-lbl');
        if (dateLbl && data.transferred_at) {
          dateLbl.textContent = '(refreshed ' + data.transferred_at.substring(0, 10) + ')';
        }
      }

      syncConcreteFromSA();
      calcConcrete(); calcDrilling();
      renderSummary();
      alert('SA data refreshed successfully!');
    } else {
      alert('No SA import data found for project: ' + jobCode);
    }
  } catch(e) {
    alert('Error refreshing: ' + e.message);
  }
}

// ─────────────────────────────────────────────
// INIT
// ─────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  // Set today's date
  const today = new Date();
  document.getElementById('proj_date').value =
    String(today.getMonth()+1).padStart(2,'0') + '/' +
    String(today.getDate()).padStart(2,'0') + '/' + today.getFullYear();

  renderEquipTable();
  renderMiscTable();
  prefillFromURL();  // pre-fill from SA "Send to TC Quote" button
  calcConcrete(); calcLabor(); calcDrilling();
  calcShipping(); calcFuel(); calcHotels();
  calcPerDiem(); calcTransport(); renderSummary();

  // Check for SA import after URL prefill completes
  setTimeout(checkSAImport, 800);

  // Project context bar — show immediately if ?project= in URL, or show after data loads
  function showProjectContextBar(projCode, projName) {
    if (document.getElementById('tc-project-ctx-bar')) return; // already shown
    var ctxBar = document.createElement('div');
    ctxBar.id = 'tc-project-ctx-bar';
    ctxBar.style.cssText = 'background:linear-gradient(135deg,rgba(200,154,46,0.15),rgba(200,154,46,0.05));padding:10px 20px;display:flex;align-items:center;gap:16px;border-bottom:1px solid rgba(200,154,46,0.3);font-size:13px;color:#C89A2E;flex-wrap:wrap;';
    var label = projName || projCode;
    ctxBar.innerHTML = '<span style="font-size:15px;">\ud83d\udcc1 <strong>' + label + '</strong> <span style="opacity:0.6;font-size:11px;">(' + projCode + ')</span></span>'
      + '<a href="/project/' + encodeURIComponent(projCode) + '" style="margin-left:auto;color:#C89A2E;text-decoration:none;font-weight:600;padding:4px 12px;border:1px solid rgba(200,154,46,0.4);border-radius:6px;font-size:12px;">\u2190 Back to Project</a>'
      + '<a href="/project/' + encodeURIComponent(projCode) + '/bom" style="color:#C89A2E;text-decoration:none;padding:4px 12px;border:1px solid rgba(200,154,46,0.3);border-radius:6px;font-size:12px;">\ud83d\udccb BOM</a>'
      + '<a href="/sa?project=' + encodeURIComponent(projCode) + '" style="color:#C89A2E;text-decoration:none;padding:4px 12px;border:1px solid rgba(200,154,46,0.3);border-radius:6px;font-size:12px;">\ud83d\udcd0 SA Estimator</a>'
      + '<a href="/shop-drawings/' + encodeURIComponent(projCode) + '" style="color:#C89A2E;text-decoration:none;padding:4px 12px;border:1px solid rgba(200,154,46,0.3);border-radius:6px;font-size:12px;">\ud83d\udcd0 Shop Drawings</a>';
    var target = document.querySelector('.tf-main') || document.querySelector('.tc-main') || document.querySelector('.main-content') || document.querySelector('main') || document.body;
    if (target) {
      // Insert after the contextbar div if it exists (breadcrumb area), otherwise prepend
      var contextBar = target.querySelector('.tf-contextbar');
      if (contextBar && contextBar.nextSibling) {
        target.insertBefore(ctxBar, contextBar.nextSibling);
      } else {
        target.prepend(ctxBar);
      }
    }
  }
  // Show from URL param — support both ?project= and ?proj_code=
  const tcSearchParams = new URLSearchParams(window.location.search);
  const tcProjParam = tcSearchParams.get('project') || tcSearchParams.get('proj_code');
  if (tcProjParam) {
    showProjectContextBar(tcProjParam, tcSearchParams.get('proj_name') || tcProjParam);
  }
  // Also show after metadata loads (picks up project name) — self-clearing interval
  var _origAutoLoad = window._tcProjectCode;
  var _ctxBarInterval = setInterval(function() {
    if (window._tcProjectCode && !document.getElementById('tc-project-ctx-bar')) {
      showProjectContextBar(window._tcProjectCode, window._tcProjectName || window._tcProjectCode);
    } else if (window._tcProjectCode && window._tcProjectName && document.getElementById('tc-project-ctx-bar')) {
      // Update label with project name once loaded
      var bar = document.getElementById('tc-project-ctx-bar');
      var span = bar.querySelector('span');
      if (span && span.textContent.indexOf(window._tcProjectName) < 0) {
        span.innerHTML = '\ud83d\udcc1 <strong>' + window._tcProjectName + '</strong> <span style="opacity:0.6;font-size:11px;">(' + window._tcProjectCode + ')</span>';
      }
      // Context bar is set up with correct name — clear the interval
      clearInterval(_ctxBarInterval);
    }
  }, 1000);

  // Sync crew/days
  document.getElementById('lab_crew').addEventListener('change', function() {
    document.getElementById('hotel_crew').value = this.value;
    document.getElementById('pd_crew').value = this.value;
    document.getElementById('trans_vehicles').value = Math.ceil(parseInt(this.value)/4);
    _flashField(document.getElementById('hotel_crew'));
    _flashField(document.getElementById('pd_crew'));
    _flashField(document.getElementById('trans_vehicles'));
    calcHotels(); calcPerDiem(); calcTransport();
  });
  document.getElementById('lab_days').addEventListener('change', function() {
    const days = parseFloat(this.value) || 0;
    document.getElementById('hotel_nights').value = Math.max(0, Math.ceil(days - 1));
    document.getElementById('pd_days').value = Math.max(0, Math.ceil(days));
    _flashField(document.getElementById('hotel_nights'));
    _flashField(document.getElementById('pd_days'));
    calcHotels(); calcPerDiem();
  });

  // Smart field sync — columns -> piers -> drill holes
  ['sa_n_cols'].forEach(function(id) {
    var el = document.getElementById(id);
    if (el) el.addEventListener('change', function() {
        var v = parseInt(this.value) || 0;
        var piers = document.getElementById('conc_n_piers');
        var holes = document.getElementById('drill_n_holes');
        if (piers && (parseInt(piers.value) === 0 || !piers.value)) piers.value = v;
        if (holes && (parseInt(holes.value) === 0 || !holes.value)) holes.value = v;
        calcConcrete(); calcDrilling();
        _flashField(piers); _flashField(holes);
    });
  });

  // Progressive disclosure - collapsible sections (targets .card-hdr elements)
  document.querySelectorAll('.card-hdr').forEach(function(hdr) {
    // Skip Project Info, SA Import, Salesperson, Summary, and BOM Detail sections
    var text = hdr.textContent || '';
    if (text.match(/project info|sa import|summary|salesperson|bom detail/i)) return;
    // Skip headers that already have an inline onclick (like BOM detail toggle)
    if (hdr.getAttribute('onclick')) return;

    hdr.classList.add('tc-section-toggle');

    // Find the card-body sibling (next element after card-hdr)
    var cardBody = hdr.nextElementSibling;
    if (!cardBody) return;

    // Measure scrollHeight BEFORE collapsing so we get the real height
    var fullHeight = cardBody.scrollHeight;

    hdr.classList.add('collapsed');
    cardBody.classList.add('tc-section-body');
    cardBody.classList.add('collapsed');

    hdr.addEventListener('click', function() {
        var isCollapsed = this.classList.toggle('collapsed');
        cardBody.classList.toggle('collapsed', isCollapsed);
        if (!isCollapsed) {
            // Re-measure now that content may have changed
            cardBody.style.maxHeight = 'none';
            var h = cardBody.scrollHeight;
            cardBody.style.maxHeight = '0px';
            // Force reflow then animate open
            void cardBody.offsetHeight;
            cardBody.style.maxHeight = h + 100 + 'px';
        } else {
            cardBody.style.maxHeight = '0px';
        }
    });
  });

  // Quick Quote functions
  window.openQuickQuote = function() {
    document.getElementById('qqOverlay').classList.add('active');
  };
  window.closeQuickQuote = function() {
    document.getElementById('qqOverlay').classList.remove('active');
  };
  window.applyQuickQuote = function() {
    var w = parseInt(document.getElementById('qqWidth').value) || 30;
    var l = parseInt(document.getElementById('qqLength').value) || 40;
    var cols = parseInt(document.getElementById('qqCols').value) || 8;
    var footing = parseFloat(document.getElementById('qqFooting').value) || 10;
    var crew = parseInt(document.getElementById('qqCrew').value) || 4;
    var days = parseInt(document.getElementById('qqDays').value) || 3;
    var dist = parseInt(document.getElementById('qqDistance').value) || 100;
    var type = document.getElementById('qqType').value;

    // Fill SA dimensions
    var widthEl = document.getElementById('sa_width');
    var lengthEl = document.getElementById('sa_length');
    if (widthEl) { widthEl.value = w; _flashField(widthEl); }
    if (lengthEl) { lengthEl.value = l; _flashField(lengthEl); }

    // Columns
    var colsEl = document.getElementById('sa_n_cols');
    if (colsEl) { colsEl.value = cols; _flashField(colsEl); }

    // Footing
    var footEl = document.getElementById('sa_footing_depth');
    if (footEl) { footEl.value = footing; _flashField(footEl); }
    var concFootEl = document.getElementById('conc_depth_ft');
    if (concFootEl) { concFootEl.value = footing; _flashField(concFootEl); }

    // Concrete — piers, diameter based on type
    var piersEl = document.getElementById('conc_n_piers');
    if (piersEl) { piersEl.value = cols; _flashField(piersEl); }
    var diamEl = document.getElementById('conc_dia_in');
    if (diamEl) { diamEl.value = type === 'commercial' ? 30 : 24; _flashField(diamEl); }

    // Labor
    var crewEl = document.getElementById('lab_crew');
    if (crewEl) { crewEl.value = crew; _flashField(crewEl); }
    var daysEl = document.getElementById('lab_days');
    if (daysEl) { daysEl.value = days; _flashField(daysEl); }
    var rateEl = document.getElementById('lab_rate_hr');
    if (rateEl && (!rateEl.value || rateEl.value == '0')) { rateEl.value = type === 'commercial' ? 45 : 35; _flashField(rateEl); }

    // Drilling
    var drillHoles = document.getElementById('drill_n_holes');
    if (drillHoles) { drillHoles.value = cols; _flashField(drillHoles); }

    // Shipping — estimate based on distance
    var shipDist = document.getElementById('ship_miles');
    if (shipDist) { shipDist.value = dist; _flashField(shipDist); }

    // Fuel — round trip x 2 (crew vehicles + material truck)
    var fuelDist = document.getElementById('fuel_miles');
    if (fuelDist) { fuelDist.value = dist * 2; _flashField(fuelDist); }

    // Hotels
    var hotelCrew = document.getElementById('hotel_crew');
    var hotelNights = document.getElementById('hotel_nights');
    if (dist > 80) {
        if (hotelCrew) { hotelCrew.value = crew; _flashField(hotelCrew); }
        if (hotelNights) { hotelNights.value = Math.max(0, days - 1); _flashField(hotelNights); }
    }

    // Per Diem
    var pdCrew = document.getElementById('pd_crew');
    var pdDays = document.getElementById('pd_days');
    if (pdCrew) { pdCrew.value = crew; _flashField(pdCrew); }
    if (pdDays) { pdDays.value = days; _flashField(pdDays); }

    // Transport
    var transVeh = document.getElementById('trans_vehicles');
    if (transVeh) { transVeh.value = Math.ceil(crew / 4); _flashField(transVeh); }
    var transDist = document.getElementById('trans_miles');
    if (transDist) { transDist.value = dist * 2; _flashField(transDist); }

    // Recalculate all
    if (typeof calcConcrete === 'function') calcConcrete();
    if (typeof calcLabor === 'function') calcLabor();
    if (typeof calcDrilling === 'function') calcDrilling();
    if (typeof calcShipping === 'function') calcShipping();
    if (typeof calcFuel === 'function') calcFuel();
    if (typeof calcHotels === 'function') calcHotels();
    if (typeof calcPerDiem === 'function') calcPerDiem();
    if (typeof calcTransport === 'function') calcTransport();
    if (typeof renderSummary === 'function') renderSummary();

    closeQuickQuote();
    if (typeof _crToast === 'function') _crToast('Quick quote applied! Review and adjust values.', 'success');
  };
});
</script>

<!-- Global Search Overlay -->
<div id="globalSearchOverlay" style="display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(15,23,42,0.5);z-index:9999;align-items:flex-start;justify-content:center;padding-top:100px;">
<div style="width:600px;max-width:90vw;background:#1E293B;border:1px solid #334155;border-radius:16px;box-shadow:0 10px 40px rgba(0,0,0,0.5);overflow:hidden;">
<input type="text" id="globalSearchInput" placeholder="Search projects, customers, inventory..." style="width:100%;padding:18px 20px;border:none;font-size:16px;outline:none;border-bottom:1px solid #334155;background:#1E293B;color:#E2E8F0;" oninput="_doGS(this.value)">
<div id="globalSearchResults" style="max-height:400px;overflow-y:auto;padding:8px;"><div style="padding:20px;text-align:center;color:#94a3b8;font-size:13px;">Type to search...</div></div>
</div></div>
<script>
var _gst=null;
if(!window.TFNav||!window.TFNav.openGlobalSearch){function openGlobalSearch(){document.getElementById('globalSearchOverlay').style.display='flex';document.getElementById('globalSearchInput').value='';document.getElementById('globalSearchInput').focus();}}
function _closeGS(){document.getElementById('globalSearchOverlay').style.display='none';}
document.getElementById('globalSearchOverlay').addEventListener('click',function(e){if(e.target.id==='globalSearchOverlay')_closeGS();});
document.addEventListener('keydown',function(e){if((e.ctrlKey||e.metaKey)&&e.key==='k'){e.preventDefault();openGlobalSearch();}if(e.key==='Escape')_closeGS();});
function _doGS(q){clearTimeout(_gst);if(!q||q.length<2){document.getElementById('globalSearchResults').innerHTML='<div style="padding:20px;text-align:center;color:#94a3b8;">Type to search...</div>';return;}
_gst=setTimeout(function(){fetch('/api/search?q='+encodeURIComponent(q)).then(function(r){return r.json();}).then(function(d){var c=document.getElementById('globalSearchResults');if(!d.results||!d.results.length){c.innerHTML='<div style="padding:20px;text-align:center;color:#94a3b8;">No results</div>';return;}
var ic={project:'&#128204;',customer:'&#128100;',inventory:'&#128230;'};c.innerHTML=d.results.map(function(r){return '<a href="'+r.url+'" style="text-decoration:none;color:inherit;"><div style="display:flex;align-items:center;gap:12px;padding:10px 14px;border-radius:8px;cursor:pointer;" onmouseover="this.style.background=\'#334155\'" onmouseout="this.style.background=\'\'"><div style="width:32px;height:32px;border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:14px;background:#334155;">'+(ic[r.type]||'')+'</div><div><div style="font-weight:600;font-size:13px;color:#E2E8F0;">'+r.title+'</div><div style="font-size:11px;color:#94a3b8;">'+(r.subtitle||'')+'</div></div></div></a>';}).join('');});},300);}
</script>

<!-- Sticky Running Total -->
<div class="tc-sticky-total" id="tcStickyTotal">
    <div class="tc-sticky-total-inner">
        <div class="tc-sticky-item">
            <div class="label">SA Materials</div>
            <div class="val" id="stickyMaterials">$0</div>
        </div>
        <div class="tc-sticky-sep"></div>
        <div class="tc-sticky-item">
            <div class="label">Install Costs</div>
            <div class="val" id="stickyInstall">$0</div>
        </div>
        <div class="tc-sticky-sep"></div>
        <div class="tc-sticky-item">
            <div class="label">Grand Total</div>
            <div class="val highlight" id="stickyGrand">$0</div>
        </div>
        <div class="tc-sticky-sep"></div>
        <div class="tc-sticky-item">
            <div class="label">Per Sq Ft</div>
            <div class="val" id="stickyPerSqFt">$0</div>
        </div>
    </div>
</div>

<!-- Quick Quote Modal -->
<div class="qq-overlay" id="qqOverlay" onclick="if(event.target===this)closeQuickQuote()">
    <div class="qq-modal">
        <h2>⚡ Quick Quote</h2>
        <p>Enter basic project details and we'll fill reasonable defaults for a fast estimate.</p>
        <div class="qq-grid">
            <div class="qq-field">
                <label>Building Width (ft)</label>
                <input type="number" id="qqWidth" value="30">
            </div>
            <div class="qq-field">
                <label>Building Length (ft)</label>
                <input type="number" id="qqLength" value="40">
            </div>
            <div class="qq-field">
                <label>Number of Columns</label>
                <input type="number" id="qqCols" value="8">
            </div>
            <div class="qq-field">
                <label>Footing Depth (ft)</label>
                <input type="number" id="qqFooting" value="10" step="0.5">
            </div>
            <div class="qq-field">
                <label>Crew Size</label>
                <input type="number" id="qqCrew" value="4">
            </div>
            <div class="qq-field">
                <label>Install Days</label>
                <input type="number" id="qqDays" value="3">
            </div>
            <div class="qq-field">
                <label>Distance (miles one-way)</label>
                <input type="number" id="qqDistance" value="100">
            </div>
            <div class="qq-field">
                <label>Building Type</label>
                <select id="qqType">
                    <option value="standard">Standard Carport</option>
                    <option value="commercial">Commercial Building</option>
                    <option value="warehouse">Warehouse / Ag</option>
                    <option value="residential">Residential Garage</option>
                </select>
            </div>
        </div>
        <div class="qq-actions">
            <button class="qq-btn qq-btn-outline" onclick="closeQuickQuote()">Cancel</button>
            <button class="qq-btn qq-btn-primary" onclick="applyQuickQuote()">⚡ Generate Estimate</button>
        </div>
    </div>
</div>

</body>
</html>"""

COIL_DETAIL_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Coil Status — Structures America</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: Arial, sans-serif; background: #f4f6f9; color: #222; }
  .topbar { background: #003A6E; color: #fff; padding: 14px 20px;
            display: flex; align-items: center; gap: 12px; }
  .topbar h1 { font-size: 18px; }
  .topbar .sub { font-size: 12px; color: #aac4e0; margin-top: 2px; }
  .badge { background: #C89A2E; color: #fff; border-radius: 4px;
           padding: 3px 10px; font-size: 12px; font-weight: bold; }
  .card { background: #fff; border-radius: 8px; box-shadow: 0 2px 8px #0001;
          margin: 16px; padding: 18px; }
  .card h2 { font-size: 14px; color: #003A6E; text-transform: uppercase;
             letter-spacing: 0.04em; margin-bottom: 12px;
             border-bottom: 2px solid #C89A2E; padding-bottom: 6px; }
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  .field label { font-size: 11px; color: #888; text-transform: uppercase;
                 font-weight: bold; display: block; margin-bottom: 2px; }
  .field span { font-size: 15px; font-weight: bold; color: #222; }
  .status-pill { display: inline-block; border-radius: 20px;
                 padding: 5px 16px; font-size: 13px; font-weight: bold; }
  .status-available { background: #d4edda; color: #155724; }
  .status-committed  { background: #fff3cd; color: #856404; }
  .status-out        { background: #f8d7da; color: #721c24; }
  .job-row { display: flex; justify-content: space-between; align-items: center;
             padding: 8px 0; border-bottom: 1px solid #eee; font-size: 14px; }
  .job-row:last-child { border-bottom: none; }
  .cert-row { padding: 8px 0; border-bottom: 1px solid #eee; font-size: 13px; }
  .cert-row a { color: #003A6E; text-decoration: none; font-weight: bold; }
  .cert-row a:hover { text-decoration: underline; }
  .empty { color: #aaa; font-style: italic; font-size: 13px; }
  .back-btn { display: inline-block; margin: 16px; padding: 9px 18px;
              background: #003A6E; color: #fff; border-radius: 5px;
              text-decoration: none; font-size: 13px; font-weight: bold; }
</style>
</head>
<body>
<div class="topbar">
  <div>
    <h1>Coil Status — {{coil_id}}</h1>
    <div class="sub">Structures America · Inventory Tracking</div>
  </div>
  <div style="margin-left:auto">
    <span class="badge">{{status_label}}</span>
  </div>
</div>

<div class="card">
  <h2>Coil Details</h2>
  <div class="grid">
    <div class="field"><label>Coil ID</label><span>{{coil_id}}</span></div>
    <div class="field"><label>Description</label><span>{{description}}</span></div>
    <div class="field"><label>Grade</label><span>{{grade}}</span></div>
    <div class="field"><label>Gauge</label><span>{{gauge}}</span></div>
    <div class="field"><label>Heat #</label><span>{{heat_num}}</span></div>
    <div class="field"><label>Supplier</label><span>{{supplier}}</span></div>
    <div class="field"><label>Weight (lbs)</label><span>{{weight_lbs}}</span></div>
    <div class="field"><label>Width (in)</label><span>{{width_in}}</span></div>
    <div class="field"><label>Received</label><span>{{received_date}}</span></div>
  </div>
</div>

<div class="card">
  <h2>Stock Status</h2>
  <div style="margin-bottom:12px">
    <span class="status-pill {{status_class}}">{{status_label}}</span>
  </div>
  <div class="grid">
    <div class="field"><label>On Hand (lbs)</label><span>{{stock_lbs}}</span></div>
    <div class="field"><label>Committed (lbs)</label><span>{{committed_lbs}}</span></div>
    <div class="field"><label>Available (lbs)</label><span style="color:{{avail_color}}">{{available_lbs}}</span></div>
    <div class="field"><label>Min Order (lbs)</label><span>{{min_order_lbs}}</span></div>
  </div>
</div>

<div class="card">
  <h2>Assigned to Jobs</h2>
  {{jobs_html}}
</div>

<div class="card">
  <h2>Mill Certificates</h2>
  {{certs_html}}
</div>

<a class="back-btn" href="/">← Back to Calculator</a>
</body>
</html>"""
