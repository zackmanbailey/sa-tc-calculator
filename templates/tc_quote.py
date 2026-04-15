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
body{font-family:'Segoe UI',Arial,sans-serif;background:var(--tf-light);color:var(--tf-gray);font-size:13px}
#topbar{background:var(--tf-dark);color:#fff;padding:0 20px;display:flex;align-items:center;height:52px;box-shadow:0 2px 8px #0005}
#topbar .logo{font-size:17px;font-weight:700;letter-spacing:1px;color:#fff}
#topbar .logo span{color:var(--tf-red)}
#topbar .spacer{flex:1}
#topbar .version{font-size:10px;color:#666}
#tabs{background:var(--tf-blue);display:flex;overflow-x:auto}
.tab{padding:10px 20px;color:#aac;cursor:pointer;font-size:12px;font-weight:600;border-bottom:3px solid transparent;white-space:nowrap;transition:all .2s}
.tab:hover{color:#fff;background:rgba(255,255,255,.07)}
.tab.active{color:#fff;border-bottom-color:var(--tf-amber)}
#main{display:flex;gap:0;height:calc(100vh - 94px)}
#sidebar{width:320px;min-width:270px;background:#fff;border-right:1px solid var(--tf-border);overflow-y:auto;padding:16px;flex-shrink:0}
#content{flex:1;overflow-y:auto;padding:20px}
.card{background:#fff;border:1px solid var(--tf-border);border-radius:8px;margin-bottom:14px;overflow:hidden}
.card-hdr{padding:9px 14px;font-weight:700;font-size:12px;display:flex;align-items:center;gap:8px;text-transform:uppercase;letter-spacing:.4px}
.card-hdr.red{background:var(--tf-red);color:#fff}
.card-hdr.blue{background:var(--tf-blue-m);color:#fff}
.card-hdr.gold{background:var(--tf-amber);color:#0F172A}
.card-hdr.green{background:var(--tf-green);color:#fff}
.card-hdr.gray{background:#555;color:#fff}
.card-hdr.dark{background:var(--tf-dark);color:#fff}
.card-body{padding:14px}
.form-group{margin-bottom:10px}
label{display:block;font-size:11px;font-weight:600;color:var(--tf-blue);margin-bottom:4px;text-transform:uppercase;letter-spacing:.4px}
input[type=text],input[type=number],select,textarea{width:100%;padding:6px 10px;border:1px solid var(--tf-border);border-radius:4px;font-size:13px;color:var(--tf-gray);background:#fff;transition:border .2s}
input:focus,select:focus,textarea:focus{outline:none;border-color:var(--tf-blue-m);box-shadow:0 0 0 3px #2E75B615}
input[type=checkbox]{width:auto;margin-right:6px}
.check-label{display:flex;align-items:center;font-size:12px;font-weight:400;text-transform:none;letter-spacing:0;cursor:pointer}
.btn{padding:7px 14px;border:none;border-radius:4px;cursor:pointer;font-size:12px;font-weight:600;transition:all .2s;display:inline-flex;align-items:center;gap:5px}
.btn-red{background:var(--tf-red);color:#fff}.btn-red:hover{opacity:.9}
.btn-blue{background:var(--tf-blue-m);color:#fff}.btn-blue:hover{opacity:.85}
.btn-gold{background:var(--tf-amber);color:var(--tf-dark)}.btn-gold:hover{opacity:.9}
.btn-green{background:var(--tf-green);color:#fff}.btn-green:hover{opacity:.9}
.btn-outline{background:transparent;border:1px solid var(--tf-border);color:var(--tf-gray)}.btn-outline:hover{background:var(--tf-blue-l)}
.btn-sm{padding:4px 10px;font-size:11px}
.btn-danger{background:#f44;color:#fff}.btn-danger:hover{opacity:.85}
.btn-group{display:flex;gap:8px;flex-wrap:wrap}
.li-table{width:100%;border-collapse:collapse;font-size:12px;margin-top:8px}
.li-table th{background:var(--tf-blue);color:#fff;padding:6px 8px;text-align:left;font-size:11px;font-weight:600}
.li-table td{padding:5px 8px;border-bottom:1px solid #eee;vertical-align:middle}
.li-table tr:hover td{background:#f9f9f9}
.li-table .total-row td{background:#FFF8E1;font-weight:700;border-top:2px solid var(--tf-amber)}
.li-table input{padding:4px 6px;font-size:12px;border:1px solid #ddd;border-radius:3px}
.summary-table{width:100%;border-collapse:collapse;font-size:13px}
.summary-table td{padding:8px 12px;border-bottom:1px solid #eee}
.summary-table .section-lbl td{background:var(--tf-blue-l);font-weight:700;color:var(--tf-blue);font-size:11px;text-transform:uppercase;letter-spacing:.4px}
.summary-table .total-row td{background:var(--tf-red);color:#fff;font-weight:700;font-size:15px}
.summary-table .markup-row td{background:#FFF8E1;font-weight:600}
.summary-table .subtotal-row td{background:#f0f4f0;font-weight:700}
.stat-cards{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:16px}
.stat{background:#fff;border:1px solid var(--tf-border);border-radius:8px;padding:12px 16px;min-width:140px;flex:1}
.stat .val{font-size:20px;font-weight:700;color:var(--tf-blue)}
.stat .lbl{font-size:10px;color:#888;text-transform:uppercase;margin-top:2px}
.alert{border-radius:4px;padding:8px 12px;font-size:12px;margin-bottom:10px}
.alert-info{background:#E3F2FD;border-left:4px solid #2196F3;color:#1565C0}
.alert-warn{background:#FFF8E1;border-left:4px solid var(--tf-amber);color:#795548}
.alert-success{background:#E8F5E9;border-left:4px solid #4CAF50;color:#2E7D32}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px}
.grid4{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:10px}
@media(max-width:768px){#main{flex-direction:column}#sidebar{width:100%}}
/* When wrapped by shared_nav inject_nav(), adjust layout */
.tf-main #main{height:calc(100vh - 84px)}
.tf-main #topbar{display:none}
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
        <div class="alert alert-info" style="font-size:11px">
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
          <div style="background:#F0F4FA;border-radius:6px;padding:10px;display:flex;gap:24px;flex-wrap:wrap">
            <div><span style="font-size:11px;color:#888">Cubic Yards (w/10% waste):</span>
              <span id="conc_qty_display" style="font-weight:700;color:var(--tf-blue);margin-left:6px">—</span></div>
            <div><span style="font-size:11px;color:#888">Material Cost:</span>
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
          <div style="background:#FFF0F0;border-radius:6px;padding:10px;display:flex;gap:24px;flex-wrap:wrap">
            <div><span style="font-size:11px;color:#888">Daily Cost:</span>
              <span id="lab_daily_display" style="font-weight:700;color:var(--tf-blue);margin-left:6px">—</span></div>
            <div><span style="font-size:11px;color:#888">Total Labor Cost:</span>
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
                <option value="per_hole" selected>Per Hole ($/hole)</option>
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
          <div style="background:#F0F4FA;border-radius:6px;padding:10px">
            <span style="font-size:11px;color:#888">Drilling Total:</span>
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
            <div><span style="font-size:11px;color:#888">Loads:</span>
              <input type="number" id="ship_loads" value="1" min="1" max="20"
                style="width:55px;margin-left:6px;padding:3px 6px;font-size:12px;border:1px solid #ddd;border-radius:3px"
                onchange="calcShipping();renderSummary()"/>
            </div>
            <div><span style="font-size:11px;color:#888">Shipping Total:</span>
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
          <div style="background:#FFF8E1;border-radius:6px;padding:10px;display:flex;gap:24px;flex-wrap:wrap">
            <div><span style="font-size:11px;color:#888">Total Gallons:</span>
              <span id="fuel_gal_display" style="font-weight:700;margin-left:6px">—</span></div>
            <div><span style="font-size:11px;color:#888">Fuel Total:</span>
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
          <div style="background:#F0F4FA;border-radius:6px;padding:10px;display:flex;gap:24px;flex-wrap:wrap">
            <div><span style="font-size:11px;color:#888">Room-Nights:</span>
              <span id="hotel_rooms_display" style="font-weight:700;margin-left:6px">—</span></div>
            <div><span style="font-size:11px;color:#888">Hotel Total:</span>
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
          <div style="background:#F0F4FA;border-radius:6px;padding:10px">
            <span style="font-size:11px;color:#888">Per Diem Total:</span>
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
          <div style="background:#F0F4FA;border-radius:6px;padding:10px">
            <span style="font-size:11px;color:#888">Transportation Total:</span>
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

    </div><!-- /tab-quote -->

    <!-- SUMMARY TAB -->
    <div id="tab-summary" style="display:none">
      <div style="display:flex;justify-content:flex-end;gap:8px;margin-bottom:12px">
        <button class="btn btn-green" onclick="tcSaveProject()">💾 Save Quote</button>
        <button class="btn btn-primary" onclick="tcExportPDF()">⬇ Export PDF</button>
      </div>
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

  // Auto-load project data from ?project=JOB_CODE
  // First try to load saved TC data; if none exists, fall back to project metadata
  if (p.has('project')) {
    const projCode = p.get('project');
    tcLoadFromProject(projCode).then(loaded => {
      if (!loaded) autoLoadProjectMetadata(projCode);
    });
  }
}

async function autoLoadProjectMetadata(jobCode) {
  try {
    const resp = await fetch('/api/project/metadata?job_code=' + encodeURIComponent(jobCode));
    const result = await resp.json();
    if (result.ok && result.metadata) {
      const m = result.metadata;
      const projCodeEl = document.getElementById('proj_code');
      if (projCodeEl && !projCodeEl.value) projCodeEl.value = m.job_code || jobCode;
      const projNameEl = document.getElementById('proj_name');
      if (projNameEl && !projNameEl.value) projNameEl.value = m.project_name || '';
      if (m.customer) {
        const custEl = document.getElementById('proj_customer');
        if (custEl && !custEl.value) custEl.value = m.customer.name || '';
      }
      if (m.location) {
        const addrEl = document.getElementById('proj_address');
        if (addrEl && !addrEl.value) addrEl.value = m.location.street || '';
        const cityEl = document.getElementById('proj_city');
        if (cityEl && !cityEl.value) cityEl.value = m.location.city || '';
        const stateEl = document.getElementById('proj_state');
        if (stateEl && !stateEl.value) stateEl.value = m.location.state || '';
      }
    }
  } catch(e) { /* silent */ }
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
        style="width:60px" oninput="equipItems[${idx}].qty=parseFloat(this.value)||0;renderEquipTable();renderSummary()" onchange="equipItems[${idx}].qty=parseFloat(this.value)||0;renderEquipTable();renderSummary()"/></td>
      <td><select onchange="equipItems[${idx}].unit=this.value">
        ${['day','week','trip','ea'].map(u=>`<option${it.unit===u?' selected':''}>${u}</option>`).join('')}
      </select></td>
      <td><input type="number" value="${it.rate}" min="0" step="50"
        style="width:80px" oninput="equipItems[${idx}].rate=parseFloat(this.value)||0;renderEquipTable();renderSummary()" onchange="equipItems[${idx}].rate=parseFloat(this.value)||0;renderEquipTable();renderSummary()"/></td>
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

  html += '<tr style="border-bottom:1px solid #eee;"><td style="padding:8px 0;color:#64748B;font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.4px;">Sell Price</td>';
  html += '<td style="padding:8px 0;text-align:right;font-weight:700;font-size:16px;color:#059669;">' + fmt(q.total) + '</td></tr>';

  if (pricePerSqft > 0) {
    html += '<tr style="border-bottom:1px solid #eee;"><td style="padding:8px 0;color:#64748B;font-weight:600;font-size:11px;text-transform:uppercase;">Price / Sq Ft</td>';
    html += '<td style="padding:8px 0;text-align:right;font-weight:700;font-size:16px;">$' + pricePerSqft.toFixed(2) + '</td></tr>';
  }

  if (sqft > 0) {
    html += '<tr style="border-bottom:1px solid #eee;"><td style="padding:8px 0;color:#64748B;font-weight:600;font-size:11px;text-transform:uppercase;">Square Footage</td>';
    html += '<td style="padding:8px 0;text-align:right;font-weight:700;font-size:16px;">' + sqft.toLocaleString() + ' sq ft</td></tr>';
  }

  if (estWeight > 0) {
    html += '<tr style="border-bottom:1px solid #eee;"><td style="padding:8px 0;color:#64748B;font-weight:600;font-size:11px;text-transform:uppercase;">Est. Steel Weight</td>';
    html += '<td style="padding:8px 0;text-align:right;font-weight:700;font-size:16px;">' + estWeight.toLocaleString() + ' lbs</td></tr>';
  }

  html += '<tr style="border-bottom:1px solid #eee;"><td style="padding:8px 0;color:#64748B;font-weight:600;font-size:11px;text-transform:uppercase;">Cost Categories Used</td>';
  html += '<td style="padding:8px 0;text-align:right;font-weight:700;font-size:16px;">' + activeSections.length + '</td></tr>';

  html += '<tr style="border-bottom:1px solid #eee;"><td style="padding:8px 0;color:#64748B;font-weight:600;font-size:11px;text-transform:uppercase;">Markup</td>';
  html += '<td style="padding:8px 0;text-align:right;font-weight:700;font-size:16px;">' + q.markupPct + '%</td></tr>';

  html += '</table>';

  // Suggestions
  html += '<div style="margin-top:12px;padding-top:12px;border-top:1px solid #E2E8F0;">';
  html += '<div style="font-size:11px;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:.4px;margin-bottom:8px;">Suggested Next Steps</div>';

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
    html += '<div style="display:flex;gap:8px;padding:4px 0;font-size:13px;color:#475569;"><span style="color:#F59E0B;font-weight:700;flex-shrink:0;">&#9658;</span><span>' + s + '</span></div>';
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
      if (p.markup_pct) document.getElementById('proj_markup').value = p.markup_pct;
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
      if (sa.materials_cost) document.getElementById('sa_materials_cost').value = sa.materials_cost;
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

  // Sync crew/days
  document.getElementById('lab_crew').addEventListener('change', function() {
    document.getElementById('hotel_crew').value = this.value;
    document.getElementById('pd_crew').value = this.value;
    document.getElementById('trans_vehicles').value = Math.ceil(parseInt(this.value)/4);
    calcHotels(); calcPerDiem(); calcTransport();
  });
  document.getElementById('lab_days').addEventListener('change', function() {
    const days = parseFloat(this.value) || 0;
    if (days > 1) {
      document.getElementById('hotel_nights').value = Math.ceil(days - 1);
      document.getElementById('pd_days').value = Math.ceil(days);
      calcHotels(); calcPerDiem();
    }
  });
});
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
