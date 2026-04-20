"""
TitanForge — Inventory Management Dashboard
==========================================
Coil inventory tracking, stock levels, allocations, receiving, and alerts.
"""

INVENTORY_DASHBOARD_PAGE_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Inventory Management — TitanForge</title>
<style>
  :root {
    --bg: #0f172a; --surface: #1e293b; --border: #334155;
    --text: #f1f5f9; --muted: #94a3b8; --accent: #3b82f6;
    --green: #22c55e; --yellow: #eab308; --orange: #f97316; --red: #ef4444;
    --purple: #a855f7; --cyan: #06b6d4;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Inter', system-ui, -apple-system, sans-serif;
         background: var(--bg); color: var(--text); line-height: 1.5; }

  .topbar { background: var(--surface); border-bottom: 1px solid var(--border);
            padding: 12px 24px; display: flex; align-items: center; justify-content: space-between; }
  .topbar h1 { font-size: 20px; font-weight: 600; }
  .topbar a { color: var(--accent); text-decoration: none; font-size: 14px; margin-left: 16px; }
  .nav-links { display: flex; gap: 8px; }

  .container { max-width: 1400px; margin: 0 auto; padding: 20px 24px; }

  /* Stat cards */
  .stats-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
               gap: 12px; margin-bottom: 20px; }
  .stat-card { background: var(--surface); border: 1px solid var(--border);
               border-radius: 8px; padding: 16px; text-align: center;
               cursor: pointer; transition: transform 0.15s, border-color 0.15s; }
  .stat-card:hover { transform: translateY(-2px); border-color: var(--accent); }
  .stat-card .value { font-size: 28px; font-weight: 700; }
  .stat-card .label { font-size: 12px; color: var(--muted); margin-top: 4px; }

  /* Tabs */
  .tabs { display: flex; gap: 4px; margin-bottom: 20px; border-bottom: 1px solid var(--border);
          padding-bottom: 0; }
  .tab { padding: 10px 20px; cursor: pointer; border: none; background: none;
         color: var(--muted); font-size: 14px; font-weight: 500; border-bottom: 2px solid transparent;
         transition: all 0.2s; }
  .tab:hover { color: var(--text); }
  .tab.active { color: var(--accent); border-bottom-color: var(--accent); }

  .tab-content { display: none; }
  .tab-content.active { display: block; }

  /* Filters */
  .filter-bar { display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; align-items: center; }
  .filter-bar select, .filter-bar input {
    background: var(--surface); color: var(--text); border: 1px solid var(--border);
    border-radius: 6px; padding: 8px 12px; font-size: 13px; }
  .filter-bar button { background: var(--accent); color: white; border: none;
    border-radius: 6px; padding: 8px 16px; font-size: 13px; cursor: pointer; font-weight: 500; }
  .filter-bar button:hover { opacity: 0.9; }
  .filter-bar button.secondary { background: var(--border); color: var(--text); margin-left: auto; }

  /* Table */
  .data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
  .data-table th { text-align: left; padding: 10px 12px; background: var(--surface);
                   border-bottom: 2px solid var(--border); color: var(--muted);
                   font-weight: 600; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; }
  .data-table td { padding: 10px 12px; border-bottom: 1px solid var(--border); vertical-align: top; }
  .data-table tr:hover { background: rgba(59,130,246,0.05); }
  .text-right { text-align: right; }
  .text-muted { color: var(--muted); font-size: 12px; }

  /* Badges */
  .badge { display: inline-block; padding: 2px 8px; border-radius: 4px;
           font-size: 11px; font-weight: 600; text-transform: uppercase; }
  .badge-active { background: rgba(34,197,94,0.2); color: var(--green); }
  .badge-low_stock { background: rgba(234,179,8,0.2); color: var(--yellow); }
  .badge-depleted { background: rgba(239,68,68,0.2); color: var(--red); }
  .badge-on_hold { background: rgba(148,163,184,0.2); color: var(--muted); }
  .badge-in_transit { background: rgba(6,182,212,0.2); color: var(--cyan); }
  .badge-good { background: rgba(34,197,94,0.2); color: var(--green); }
  .badge-fair { background: rgba(234,179,8,0.2); color: var(--yellow); }
  .badge-damaged { background: rgba(239,68,68,0.2); color: var(--red); }
  .badge-critical { background: rgba(239,68,68,0.2); color: var(--red); }
  .badge-warning { background: rgba(234,179,8,0.2); color: var(--yellow); }
  .badge-info { background: rgba(59,130,246,0.2); color: var(--accent); }

  .btn-sm { padding: 4px 10px; border-radius: 4px; border: none;
            font-size: 11px; cursor: pointer; font-weight: 500; }
  .btn-sm.primary { background: var(--accent); color: white; }
  .btn-sm.secondary { background: var(--border); color: var(--text); }
  .btn-sm.danger { background: var(--red); color: white; }

  /* Modal */
  .modal-overlay { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
                   background: rgba(0,0,0,0.6); z-index: 1000; align-items: center; justify-content: center; }
  .modal-overlay.show { display: flex; }
  .modal { background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
           padding: 24px; max-width: 600px; width: 90%; max-height: 80vh; overflow-y: auto; }
  .modal h3 { margin-bottom: 16px; font-size: 18px; }
  .modal label { display: block; font-size: 12px; color: var(--muted); margin-bottom: 4px; margin-top: 12px; }
  .modal input, .modal select, .modal textarea {
    width: 100%; background: var(--bg); color: var(--text); border: 1px solid var(--border);
    border-radius: 6px; padding: 8px 12px; font-size: 13px; }
  .modal textarea { resize: vertical; min-height: 60px; }
  .modal-actions { display: flex; gap: 8px; margin-top: 20px; justify-content: flex-end; }
  .modal-actions button { padding: 8px 20px; border-radius: 6px; border: none;
                          font-size: 13px; cursor: pointer; font-weight: 500; }
  .btn-primary { background: var(--accent); color: white; }
  .btn-secondary { background: var(--border); color: var(--text); }
  .btn-success { background: var(--green); color: white; }

  .page-layout { display: grid; grid-template-columns: 1fr 280px; gap: 20px; }
  .sidebar { display: flex; flex-direction: column; gap: 16px; }
  .sidebar-card { background: var(--surface); border: 1px solid var(--border);
                  border-radius: 8px; padding: 16px; }
  .sidebar-card h4 { font-size: 13px; color: var(--muted); margin-bottom: 12px;
                     text-transform: uppercase; letter-spacing: 0.5px; }
  .sidebar-item { display: flex; justify-content: space-between; padding: 4px 0; font-size: 13px;
                  cursor: pointer; border-radius: 4px; padding-left: 4px; padding-right: 4px; transition: background 0.15s; }
  .sidebar-item:hover { background: rgba(59,130,246,0.1); }
  .gauge-bar { display: flex; gap: 2px; margin-top: 8px; height: 12px; border-radius: 4px; overflow: hidden; }
  .gauge-segment { flex-shrink: 0; border-radius: 2px; }

  .empty-state { text-align: center; padding: 40px; color: var(--muted); }

  @media (max-width: 1100px) { .page-layout { grid-template-columns: 1fr; } }
</style>
</head>
<body>
  <div class="topbar">
    <h1>Inventory Management</h1>
    <div class="nav-links">
      <button onclick="window.open('/api/inventory/summary/pdf')" style="background:var(--accent);color:#FFF;border:none;padding:6px 16px;border-radius:6px;font-weight:600;font-size:13px;cursor:pointer">Export PDF</button>
      <a href="/dashboard">Dashboard</a>
      <a href="/schedule">Schedule</a>
      <a href="/documents">Documents</a>
    </div>
  </div>

  <div class="container">
    <div class="stats-row" id="statsRow"></div>

    <div class="page-layout">
      <div class="main-content">
        <div class="tabs">
          <button class="tab active" data-tab="coils">Coils</button>
          <button class="tab" data-tab="transactions">Transactions</button>
          <button class="tab" data-tab="allocations">Allocations</button>
          <button class="tab" data-tab="receiving">Receiving</button>
          <button class="tab" data-tab="alerts">Alerts</button>
        </div>

        <!-- Coils Tab -->
        <div class="tab-content active" id="tab-coils">
          <div class="filter-bar">
            <select id="filterGauge"><option value="">All Gauges</option></select>
            <select id="filterGrade"><option value="">All Grades</option></select>
            <select id="filterStatus"><option value="">All Statuses</option></select>
            <button onclick="loadCoils()">Filter</button>
            <button class="secondary" onclick="showNewCoilModal()">+ New Coil</button>
          </div>
          <table class="data-table">
            <thead><tr><th>Coil ID</th><th>Name</th><th>Gauge</th><th>Grade</th><th>Supplier</th>
              <th class="text-right">Stock (lbs)</th><th class="text-right">Committed</th>
              <th class="text-right">Available</th><th>Status</th><th>Actions</th></tr></thead>
            <tbody id="coilsBody"></tbody>
          </table>
        </div>

        <!-- Transactions Tab -->
        <div class="tab-content" id="tab-transactions">
          <div class="filter-bar">
            <select id="filterTxCoil"><option value="">All Coils</option></select>
            <select id="filterTxType"><option value="">All Types</option></select>
            <button onclick="loadTransactions()">Filter</button>
          </div>
          <table class="data-table">
            <thead><tr><th>Transaction ID</th><th>Coil ID</th><th>Type</th><th class="text-right">Quantity (lbs)</th>
              <th>Job Code</th><th>Reference</th><th>Notes</th><th>Date</th></tr></thead>
            <tbody id="transactionsBody"></tbody>
          </table>
        </div>

        <!-- Allocations Tab -->
        <div class="tab-content" id="tab-allocations">
          <div class="filter-bar">
            <button onclick="loadAllocations()">Refresh</button>
            <button class="secondary" onclick="showAllocateModal()">+ New Allocation</button>
          </div>
          <table class="data-table">
            <thead><tr><th>Allocation ID</th><th>Coil ID</th><th>Job Code</th>
              <th class="text-right">Allocated (lbs)</th><th class="text-right">Consumed (lbs)</th>
              <th class="text-right">Remaining</th><th>Status</th><th>Actions</th></tr></thead>
            <tbody id="allocationsBody"></tbody>
          </table>
        </div>

        <!-- Receiving Tab -->
        <div class="tab-content" id="tab-receiving">
          <div class="filter-bar">
            <button onclick="loadReceiving()">Refresh</button>
            <button class="secondary" onclick="showReceiveModal()">+ Receive Stock</button>
          </div>
          <table class="data-table">
            <thead><tr><th>Receiving ID</th><th>Coil ID</th><th>Supplier</th>
              <th class="text-right">Quantity (lbs)</th><th>PO #</th><th>BOL #</th>
              <th>Heat #</th><th>Date</th></tr></thead>
            <tbody id="receivingBody"></tbody>
          </table>
        </div>

        <!-- Alerts Tab -->
        <div class="tab-content" id="tab-alerts">
          <div class="filter-bar">
            <button onclick="loadAlerts()">Refresh</button>
          </div>
          <table class="data-table">
            <thead><tr><th>Alert ID</th><th>Level</th><th>Coil ID</th><th>Message</th><th>Date</th><th>Actions</th></tr></thead>
            <tbody id="alertsBody"></tbody>
          </table>
        </div>
      </div>

      <div class="sidebar" id="sidebar"></div>
    </div>
  </div>

  <!-- New Coil Modal -->
  <div class="modal-overlay" id="newCoilModal"><div class="modal">
    <h3>New Coil</h3>
    <label>Coil ID *</label><input id="ncM_coilId" placeholder="e.g., COIL-2025-001">
    <label>Name *</label><input id="ncM_name" placeholder="e.g., Galvanized Coil">
    <label>Gauge *</label><select id="ncM_gauge"></select>
    <label>Grade *</label><select id="ncM_grade"></select>
    <label>Supplier *</label><input id="ncM_supplier">
    <label>Weight (lbs) *</label><input id="ncM_weight" type="number" step="0.01" value="0">
    <label>Width (in)</label><input id="ncM_width" type="number" step="0.01">
    <label>Stock (lbs)</label><input id="ncM_stock" type="number" step="0.01" value="0">
    <label>Price per lb ($)</label><input id="ncM_price" type="number" step="0.01" value="0">
    <label>Min Order (lbs)</label><input id="ncM_minOrder" type="number" step="0.01" value="0">
    <label>lbs per lft</label><input id="ncM_lbsPerLft" type="number" step="0.01">
    <label>Heat #</label><input id="ncM_heatNum">
    <div class="modal-actions">
      <button class="btn-secondary" onclick="closeModal('newCoilModal')">Cancel</button>
      <button class="btn-primary" onclick="createCoil()">Create</button>
    </div>
  </div></div>

  <!-- Receive Stock Modal -->
  <div class="modal-overlay" id="receiveModal"><div class="modal">
    <h3>Receive Stock</h3>
    <label>Coil ID *</label><select id="rcM_coilId"></select>
    <label>Quantity (lbs) *</label><input id="rcM_qty" type="number" step="0.01" value="0">
    <label>PO #</label><input id="rcM_po">
    <label>BOL #</label><input id="rcM_bol">
    <label>Supplier</label><input id="rcM_supplier">
    <label>Heat #</label><input id="rcM_heat">
    <label>Condition Notes</label><textarea id="rcM_notes"></textarea>
    <div class="modal-actions">
      <button class="btn-secondary" onclick="closeModal('receiveModal')">Cancel</button>
      <button class="btn-primary" onclick="receiveStock()">Receive</button>
    </div>
  </div></div>

  <!-- Allocate Stock Modal -->
  <div class="modal-overlay" id="allocateModal"><div class="modal">
    <h3>Allocate Stock</h3>
    <label>Coil ID *</label><select id="alM_coilId"></select>
    <label>Job Code *</label><input id="alM_jobCode" placeholder="e.g., JOB-2025-001">
    <label>Quantity (lbs) *</label><input id="alM_qty" type="number" step="0.01" value="0">
    <label>Work Order Reference</label><input id="alM_woRef">
    <label>Notes</label><textarea id="alM_notes"></textarea>
    <div class="modal-actions">
      <button class="btn-secondary" onclick="closeModal('allocateModal')">Cancel</button>
      <button class="btn-primary" onclick="allocateStock()">Allocate</button>
    </div>
  </div></div>

  <!-- Adjust Stock Modal -->
  <div class="modal-overlay" id="adjustModal"><div class="modal">
    <h3>Adjust Stock</h3>
    <label>Coil ID *</label><select id="adjM_coilId"></select>
    <label>Quantity Change (lbs) *</label><input id="adjM_qty" type="number" step="0.01" value="0">
    <label>Reason *</label><select id="adjM_reason">
      <option value="">Select reason</option>
      <option value="scrap">Scrap</option>
      <option value="waste">Waste</option>
      <option value="damage">Damage</option>
      <option value="correction">Correction</option>
      <option value="other">Other</option>
    </select>
    <label>Notes</label><textarea id="adjM_notes"></textarea>
    <div class="modal-actions">
      <button class="btn-secondary" onclick="closeModal('adjustModal')">Cancel</button>
      <button class="btn-primary" onclick="adjustStock()">Adjust</button>
    </div>
  </div></div>

<script>
  let CONFIG = {};
  const $ = id => document.getElementById(id);
  const fmtNum = n => Number(n||0).toLocaleString('en-US', {minimumFractionDigits:0, maximumFractionDigits:0});
  const fmtLbs = n => Number(n||0).toLocaleString('en-US', {minimumFractionDigits:2, maximumFractionDigits:2}) + ' lbs';
  const fmtDollars = n => '$' + Number(n||0).toLocaleString('en-US', {minimumFractionDigits:2, maximumFractionDigits:2});

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  async function api(url, method, body) {
    const opts = {method: method||'GET', headers:{'Content-Type':'application/json'}};
    if (body) opts.body = JSON.stringify(body);
    const resp = await fetch(url, opts);
    return resp.json();
  }

  async function loadConfig() {
    CONFIG = await api('/api/inventory/inv-config');

    // Populate gauge filters/dropdowns
    const gauges = CONFIG.coil_gauges || [];
    [filterGauge, ncM_gauge].forEach(sel => {
      gauges.forEach(g => {
        const o = document.createElement('option');
        o.value = g; o.textContent = g;
        sel.appendChild(o);
      });
    });

    // Populate grade filters/dropdowns
    const grades = CONFIG.material_grades || [];
    [filterGrade, ncM_grade].forEach(sel => {
      grades.forEach(g => {
        const o = document.createElement('option');
        o.value = g; o.textContent = g;
        sel.appendChild(o);
      });
    });

    // Populate status filter
    const statuses = CONFIG.inventory_statuses || ['active', 'low_stock', 'depleted', 'on_hold'];
    statuses.forEach(s => {
      const o = document.createElement('option');
      o.value = s; o.textContent = s.replace('_', ' ').toUpperCase();
      filterStatus.appendChild(o);
    });

    // Populate transaction type filter
    const txTypes = ['receive', 'allocate', 'consume', 'release', 'adjust'];
    txTypes.forEach(t => {
      const o = document.createElement('option');
      o.value = t; o.textContent = t.charAt(0).toUpperCase() + t.slice(1);
      filterTxType.appendChild(o);
    });
  }

  function switchTab(name) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');
    $('tab-' + name).classList.add('active');

    if (name === 'coils') loadCoils();
    else if (name === 'transactions') loadTransactions();
    else if (name === 'allocations') loadAllocations();
    else if (name === 'receiving') loadReceiving();
    else if (name === 'alerts') loadAlerts();
  }

  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', function() { switchTab(this.dataset.tab); });
  });

  function closeModal(id) { $(id).classList.remove('show'); }

  function statCard(val, label, color, onclick) {
    var oc = (typeof onclick === 'string') ? onclick : '';
    return '<div class="stat-card"'+(oc ? ' onclick="'+oc+'" style="cursor:pointer"' : '')+'>' +
      '<div class="value" style="color:var('+color+')">'+val+'</div><div class="label">'+label+'</div></div>';
  }

  // Load summary stats
  async function loadSummary() {
    const d = await api('/api/inventory/summary');
    if (!d.ok) return;
    const s = d.summary;
    $('statsRow').innerHTML =
      statCard(fmtNum(s.total_coils), 'Total Coils', '--accent', "filterStatus.value=\\'\\';loadCoils()") +
      statCard(fmtNum(s.total_stock_lbs), 'Total Stock', '--cyan', "filterStatus.value=\\'\\';loadCoils()") +
      statCard(fmtNum(s.total_committed_lbs), 'Committed', '--orange', "document.querySelector(\\'.tab[data-tab=allocations]\\').click()") +
      statCard(fmtNum(s.total_available_lbs), 'Available', '--green', "filterStatus.value=\\'active\\';loadCoils()") +
      statCard(fmtNum(s.low_stock_count), 'Low Stock Alerts', s.low_stock_count > 0 ? '--red' : '--green', "filterStatus.value=\\'low_stock\\';loadCoils()") +
      statCard(fmtDollars(s.total_value), 'Total Value', '--yellow', "filterStatus.value=\\'\\';loadCoils()");

    // Sidebar
    let sb = '<div class="sidebar-card"><h4>Stock by Gauge</h4>';
    const gaugeData = s.stock_by_gauge || {};
    const totalGaugeLbs = Object.values(gaugeData).reduce((a, b) => a + b, 0) || 1;
    sb += '<div class="gauge-bar">';
    Object.entries(gaugeData).forEach(([gauge, lbs]) => {
      const pct = (lbs / totalGaugeLbs) * 100;
      sb += '<div class="gauge-segment" style="width:'+pct+'%;background:var(--accent)" title="' + gauge + ': ' + fmtLbs(lbs) + '"></div>';
    });
    sb += '</div>';
    sb += '</div>';

    sb += '<div class="sidebar-card"><h4>Stock by Status</h4>';
    const statusData = s.stock_by_status || {};
    sb += '<div class="sidebar-item" onclick="filterStatus.value=\'active\';loadCoils()"><span>Active</span><span>' + fmtNum(statusData.active_count || 0) + '</span></div>';
    sb += '<div class="sidebar-item" onclick="filterStatus.value=\'low_stock\';loadCoils()"><span>Low Stock</span><span style="color:var(--yellow)">' + fmtNum(statusData.low_stock_count || 0) + '</span></div>';
    sb += '<div class="sidebar-item" onclick="filterStatus.value=\'depleted\';loadCoils()"><span>Depleted</span><span style="color:var(--red)">' + fmtNum(statusData.depleted_count || 0) + '</span></div>';
    sb += '</div>';
    $('sidebar').innerHTML = sb;
  }

  // Coils Tab
  async function loadCoils() {
    const gauge = $('filterGauge').value;
    const grade = $('filterGrade').value;
    const status = $('filterStatus').value;
    let url = '/api/inventory/coils';
    const params = [];
    if (gauge) params.push('gauge=' + encodeURIComponent(gauge));
    if (grade) params.push('grade=' + encodeURIComponent(grade));
    if (status) params.push('status=' + encodeURIComponent(status));
    if (params.length) url += '?' + params.join('&');

    const d = await api(url);
    const tb = $('coilsBody');
    if (!d.ok || !d.coils || !d.coils.length) {
      tb.innerHTML = '<tr><td colspan="10" class="empty-state">No coils found</td></tr>';
      return;
    }

    tb.innerHTML = d.coils.map(c => '<tr>' +
      '<td><strong>' + escapeHtml(c.coil_id) + '</strong></td>' +
      '<td>' + escapeHtml(c.name) + '</td>' +
      '<td>' + escapeHtml(c.gauge) + '</td>' +
      '<td>' + escapeHtml(c.grade) + '</td>' +
      '<td class="text-muted">' + escapeHtml(c.supplier) + '</td>' +
      '<td class="text-right">' + fmtNum(c.stock_lbs) + '</td>' +
      '<td class="text-right">' + fmtNum(c.committed_lbs) + '</td>' +
      '<td class="text-right" style="color:var(--green)">' + fmtNum(c.available_lbs) + '</td>' +
      '<td><span class="badge badge-' + c.status + '">' + c.status.replace('_', ' ').toUpperCase() + '</span></td>' +
      '<td>' +
        '<button class="btn-sm secondary" onclick="showCoilHistory(\'' + c.coil_id + '\')">History</button> ' +
        '<button class="btn-sm primary" onclick="showReceiveModal(\'' + c.coil_id + '\')">Receive</button> ' +
        '<button class="btn-sm primary" onclick="showAllocateModal(\'' + c.coil_id + '\')">Allocate</button>' +
      '</td>' +
    '</tr>').join('');
  }

  function showNewCoilModal() { $('newCoilModal').classList.add('show'); }
  async function createCoil() {
    const d = await api('/api/inventory/coil/create', 'POST', {
      coil_id: $('ncM_coilId').value,
      name: $('ncM_name').value,
      gauge: $('ncM_gauge').value,
      grade: $('ncM_grade').value,
      supplier: $('ncM_supplier').value,
      weight_lbs: parseFloat($('ncM_weight').value) || 0,
      width_in: parseFloat($('ncM_width').value) || null,
      stock_lbs: parseFloat($('ncM_stock').value) || 0,
      price_per_lb: parseFloat($('ncM_price').value) || 0,
      min_order_lbs: parseFloat($('ncM_minOrder').value) || 0,
      lbs_per_lft: parseFloat($('ncM_lbsPerLft').value) || null,
      heat_num: $('ncM_heatNum').value || null,
    });
    if (d.ok) {
      closeModal('newCoilModal');
      loadCoils();
      loadSummary();
    } else {
      alert('Error: ' + (d.error || 'Unknown error'));
    }
  }

  function showCoilHistory(coilId) {
    alert('History for ' + coilId + ' would load a detailed transaction view');
  }

  // Transactions Tab
  async function loadTransactions() {
    let url = '/api/inventory/transactions';
    const coilId = $('filterTxCoil').value;
    const txType = $('filterTxType').value;
    const params = [];
    if (coilId) params.push('coil_id=' + encodeURIComponent(coilId));
    if (txType) params.push('type=' + encodeURIComponent(txType));
    if (params.length) url += '?' + params.join('&');

    const d = await api(url);
    const tb = $('transactionsBody');
    if (!d.ok || !d.transactions || !d.transactions.length) {
      tb.innerHTML = '<tr><td colspan="8" class="empty-state">No transactions found</td></tr>';
      return;
    }

    tb.innerHTML = d.transactions.map(t => '<tr>' +
      '<td><strong>' + escapeHtml(t.transaction_id) + '</strong></td>' +
      '<td>' + escapeHtml(t.coil_id) + '</td>' +
      '<td><span class="badge badge-info">' + t.type.toUpperCase() + '</span></td>' +
      '<td class="text-right">' + fmtNum(t.quantity_lbs) + '</td>' +
      '<td>' + escapeHtml(t.job_code || '-') + '</td>' +
      '<td class="text-muted">' + escapeHtml(t.reference || '-') + '</td>' +
      '<td class="text-muted">' + escapeHtml(t.notes || '-') + '</td>' +
      '<td class="text-muted">' + (t.date ? t.date.substring(0, 10) : '-') + '</td>' +
    '</tr>').join('');
  }

  // Allocations Tab
  async function loadAllocations() {
    const d = await api('/api/inventory/allocations');
    const tb = $('allocationsBody');
    if (!d.ok || !d.allocations || !d.allocations.length) {
      tb.innerHTML = '<tr><td colspan="8" class="empty-state">No active allocations</td></tr>';
      return;
    }

    tb.innerHTML = d.allocations.map(a => {
      const remaining = (a.quantity_lbs || 0) - (a.consumed_lbs || 0);
      return '<tr>' +
        '<td><strong>' + escapeHtml(a.allocation_id) + '</strong></td>' +
        '<td>' + escapeHtml(a.coil_id) + '</td>' +
        '<td>' + escapeHtml(a.job_code) + '</td>' +
        '<td class="text-right">' + fmtNum(a.quantity_lbs) + '</td>' +
        '<td class="text-right">' + fmtNum(a.consumed_lbs) + '</td>' +
        '<td class="text-right" style="color:' + (remaining > 0 ? 'var(--green)' : 'var(--red)') + '">' + fmtNum(remaining) + '</td>' +
        '<td><span class="badge badge-' + a.status + '">' + a.status.toUpperCase() + '</span></td>' +
        '<td><button class="btn-sm danger" onclick="releaseAllocation(\'' + a.allocation_id + '\')">Release</button></td>' +
      '</tr>';
    }).join('');
  }

  function showAllocateModal(coilId) {
    const sel = $('alM_coilId');
    if (coilId) sel.value = coilId;
    $('allocateModal').classList.add('show');
  }

  async function allocateStock() {
    const d = await api('/api/inventory/allocate', 'POST', {
      coil_id: $('alM_coilId').value,
      job_code: $('alM_jobCode').value,
      quantity_lbs: parseFloat($('alM_qty').value) || 0,
      work_order_ref: $('alM_woRef').value || null,
      notes: $('alM_notes').value || null,
    });
    if (d.ok) {
      closeModal('allocateModal');
      loadAllocations();
      loadSummary();
    } else {
      alert('Error: ' + (d.error || 'Unknown error'));
    }
  }

  async function releaseAllocation(allocId) {
    if (!confirm('Release this allocation?')) return;
    const d = await api('/api/inventory/allocate/release', 'POST', { allocation_id: allocId });
    if (d.ok) {
      loadAllocations();
      loadSummary();
    } else {
      alert('Error: ' + (d.error || 'Unknown error'));
    }
  }

  // Receiving Tab
  async function loadReceiving() {
    const d = await api('/api/inventory/receiving');
    const tb = $('receivingBody');
    if (!d.ok || !d.receiving || !d.receiving.length) {
      tb.innerHTML = '<tr><td colspan="8" class="empty-state">No receiving records</td></tr>';
      return;
    }

    tb.innerHTML = d.receiving.map(r => '<tr>' +
      '<td><strong>' + escapeHtml(r.receiving_id) + '</strong></td>' +
      '<td>' + escapeHtml(r.coil_id) + '</td>' +
      '<td class="text-muted">' + escapeHtml(r.supplier) + '</td>' +
      '<td class="text-right">' + fmtNum(r.quantity_lbs) + '</td>' +
      '<td class="text-muted">' + escapeHtml(r.po_number || '-') + '</td>' +
      '<td class="text-muted">' + escapeHtml(r.bol_number || '-') + '</td>' +
      '<td class="text-muted">' + escapeHtml(r.heat_number || '-') + '</td>' +
      '<td class="text-muted">' + (r.date ? r.date.substring(0, 10) : '-') + '</td>' +
    '</tr>').join('');
  }

  function showReceiveModal(coilId) {
    const sel = $('rcM_coilId');
    if (coilId) sel.value = coilId;
    $('receiveModal').classList.add('show');
  }

  async function populateCoilDropdowns() {
    const d = await api('/api/inventory/coils');
    [rcM_coilId, alM_coilId, adjM_coilId].forEach(sel => {
      sel.innerHTML = '<option value="">Select coil</option>';
      if (d.ok && d.coils) {
        d.coils.forEach(c => {
          const o = document.createElement('option');
          o.value = c.coil_id;
          o.textContent = c.coil_id + ' (' + escapeHtml(c.name) + ')';
          sel.appendChild(o);
        });
      }
    });
    // Also populate transaction filter
    const txSel = $('filterTxCoil');
    txSel.innerHTML = '<option value="">All Coils</option>';
    if (d.ok && d.coils) {
      d.coils.forEach(c => {
        const o = document.createElement('option');
        o.value = c.coil_id;
        o.textContent = c.coil_id;
        txSel.appendChild(o);
      });
    }
  }

  async function receiveStock() {
    const d = await api('/api/inventory/receive', 'POST', {
      coil_id: $('rcM_coilId').value,
      quantity_lbs: parseFloat($('rcM_qty').value) || 0,
      po_number: $('rcM_po').value || null,
      bol_number: $('rcM_bol').value || null,
      supplier: $('rcM_supplier').value || null,
      heat_number: $('rcM_heat').value || null,
      condition_notes: $('rcM_notes').value || null,
    });
    if (d.ok) {
      closeModal('receiveModal');
      loadReceiving();
      loadSummary();
    } else {
      alert('Error: ' + (d.error || 'Unknown error'));
    }
  }

  // Alerts Tab
  async function loadAlerts() {
    const d = await api('/api/inventory/alerts?acknowledged=false');
    const tb = $('alertsBody');
    if (!d.ok || !d.alerts || !d.alerts.length) {
      tb.innerHTML = '<tr><td colspan="6" class="empty-state">No active alerts</td></tr>';
      return;
    }

    tb.innerHTML = d.alerts.map(a => '<tr>' +
      '<td><strong>' + escapeHtml(a.alert_id) + '</strong></td>' +
      '<td><span class="badge badge-' + a.level + '">' + a.level.toUpperCase() + '</span></td>' +
      '<td>' + escapeHtml(a.coil_id) + '</td>' +
      '<td>' + escapeHtml(a.message) + '</td>' +
      '<td class="text-muted">' + (a.date ? a.date.substring(0, 10) : '-') + '</td>' +
      '<td><button class="btn-sm secondary" onclick="acknowledgeAlert(\'' + a.alert_id + '\')">Acknowledge</button></td>' +
    '</tr>').join('');
  }

  async function acknowledgeAlert(alertId) {
    const d = await api('/api/inventory/alerts/acknowledge', 'POST', { alert_id: alertId });
    if (d.ok) {
      loadAlerts();
    } else {
      alert('Error: ' + (d.error || 'Unknown error'));
    }
  }

  // Init
  async function init() {
    await loadConfig();
    await populateCoilDropdowns();
    loadSummary();
    loadCoils();
  }

  init();
  setInterval(loadSummary, 60000);
</script>
</body>
</html>"""
