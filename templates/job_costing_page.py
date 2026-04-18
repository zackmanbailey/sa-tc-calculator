"""
TitanForge — Job Costing & Financial Tracking Dashboard
========================================================
Cost estimates, actuals, labor tracking, change orders,
variance analysis, and cross-job financial overview.
"""

JOB_COSTING_PAGE_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Job Costing — TitanForge</title>
<style>
  :root {
    --bg: #0f172a; --surface: #1e293b; --border: #334155;
    --text: #f1f5f9; --muted: #94a3b8; --accent: #3b82f6;
    --green: #22c55e; --yellow: #eab308; --orange: #f97316; --red: #ef4444;
    --purple: #a855f7; --cyan: #06b6d4;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: var(--bg); color: var(--text); line-height: 1.5; }

  .topbar { background: var(--surface); border-bottom: 1px solid var(--border);
            padding: 12px 24px; display: flex; align-items: center; justify-content: space-between; }
  .topbar h1 { font-size: 20px; font-weight: 600; }
  .topbar a { color: var(--accent); text-decoration: none; font-size: 14px; margin-left: 16px; }
  .nav-links { display: flex; gap: 8px; }

  .container { max-width: 1400px; margin: 0 auto; padding: 20px 24px; }

  .stats-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
               gap: 12px; margin-bottom: 20px; }
  .stat-card { background: var(--surface); border: 1px solid var(--border);
               border-radius: 8px; padding: 16px; text-align: center; }
  .stat-card .value { font-size: 24px; font-weight: 700; }
  .stat-card .label { font-size: 12px; color: var(--muted); margin-top: 4px; }

  .tabs { display: flex; gap: 4px; margin-bottom: 20px; border-bottom: 1px solid var(--border); }
  .tab { padding: 10px 20px; cursor: pointer; border: none; background: none;
         color: var(--muted); font-size: 14px; font-weight: 500; border-bottom: 2px solid transparent; }
  .tab:hover { color: var(--text); }
  .tab.active { color: var(--accent); border-bottom-color: var(--accent); }

  .tab-content { display: none; }
  .tab-content.active { display: block; }

  .filter-bar { display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; align-items: center; }
  .filter-bar select, .filter-bar input {
    background: var(--surface); color: var(--text); border: 1px solid var(--border);
    border-radius: 6px; padding: 8px 12px; font-size: 13px; }
  .filter-bar button { background: var(--accent); color: white; border: none;
    border-radius: 6px; padding: 8px 16px; font-size: 13px; cursor: pointer; font-weight: 500; }

  .data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
  .data-table th { text-align: left; padding: 10px 12px; background: var(--surface);
                   border-bottom: 2px solid var(--border); color: var(--muted);
                   font-weight: 600; font-size: 11px; text-transform: uppercase; }
  .data-table td { padding: 10px 12px; border-bottom: 1px solid var(--border); }
  .data-table tr:hover { background: rgba(59,130,246,0.05); }
  .text-right { text-align: right; }
  .text-muted { color: var(--muted); font-size: 12px; }
  .text-green { color: var(--green); }
  .text-red { color: var(--red); }
  .text-yellow { color: var(--yellow); }

  .badge { display: inline-block; padding: 2px 8px; border-radius: 4px;
           font-size: 11px; font-weight: 600; text-transform: uppercase; }
  .badge-draft { background: rgba(148,163,184,0.2); color: var(--muted); }
  .badge-approved { background: rgba(34,197,94,0.2); color: var(--green); }
  .badge-revised { background: rgba(234,179,8,0.2); color: var(--yellow); }
  .badge-final { background: rgba(59,130,246,0.2); color: var(--accent); }

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

  .page-layout { display: grid; grid-template-columns: 1fr 300px; gap: 20px; }
  .sidebar { display: flex; flex-direction: column; gap: 16px; }
  .sidebar-card { background: var(--surface); border: 1px solid var(--border);
                  border-radius: 8px; padding: 16px; }
  .sidebar-card h4 { font-size: 13px; color: var(--muted); margin-bottom: 12px;
                     text-transform: uppercase; letter-spacing: 0.5px; }
  .sidebar-item { display: flex; justify-content: space-between; padding: 4px 0; font-size: 13px; }

  .empty-state { text-align: center; padding: 40px; color: var(--muted); }

  .margin-bar { height: 8px; border-radius: 4px; background: var(--border); margin-top: 6px; overflow: hidden; }
  .margin-fill { height: 100%; border-radius: 4px; transition: width 0.3s; }

  @media (max-width: 1100px) { .page-layout { grid-template-columns: 1fr; } }
</style>
</head>
<body>
  <div class="topbar">
    <h1>Job Costing & Financials</h1>
    <div class="nav-links">
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
          <button class="tab active" onclick="switchTab('overview')">Overview</button>
          <button class="tab" onclick="switchTab('estimates')">Estimates</button>
          <button class="tab" onclick="switchTab('costs')">Cost Entries</button>
          <button class="tab" onclick="switchTab('labor')">Labor</button>
          <button class="tab" onclick="switchTab('changes')">Change Orders</button>
        </div>

        <!-- Overview Tab -->
        <div class="tab-content active" id="tab-overview">
          <div class="filter-bar">
            <input type="text" id="ovJobFilter" placeholder="Job Code" style="width:140px">
            <button onclick="loadJobSummary()">Load Job P&L</button>
          </div>
          <div id="jobSummaryContent"><div class="empty-state">Enter a job code to view P&L</div></div>
        </div>

        <!-- Estimates Tab -->
        <div class="tab-content" id="tab-estimates">
          <div class="filter-bar">
            <input type="text" id="estJobFilter" placeholder="Job Code" style="width:140px">
            <button onclick="loadEstimates()">Filter</button>
            <button onclick="showEstimateModal()" style="margin-left:auto">+ New Estimate</button>
          </div>
          <table class="data-table">
            <thead><tr><th>Name</th><th>Job</th><th>Status</th><th class="text-right">Estimate</th>
              <th class="text-right">Contract</th><th class="text-right">Margin</th><th>Actions</th></tr></thead>
            <tbody id="estimatesBody"></tbody>
          </table>
        </div>

        <!-- Costs Tab -->
        <div class="tab-content" id="tab-costs">
          <div class="filter-bar">
            <input type="text" id="costJobFilter" placeholder="Job Code" style="width:140px">
            <select id="costCatFilter"><option value="">All Categories</option></select>
            <button onclick="loadCosts()">Filter</button>
            <button onclick="showCostModal()" style="margin-left:auto">+ Add Cost</button>
          </div>
          <table class="data-table">
            <thead><tr><th>Description</th><th>Category</th><th>Qty</th><th class="text-right">Unit Cost</th>
              <th class="text-right">Total</th><th>Vendor</th><th>Job</th><th>Date</th></tr></thead>
            <tbody id="costsBody"></tbody>
          </table>
        </div>

        <!-- Labor Tab -->
        <div class="tab-content" id="tab-labor">
          <div class="filter-bar">
            <input type="text" id="labJobFilter" placeholder="Job Code" style="width:140px">
            <input type="text" id="labWorkerFilter" placeholder="Worker" style="width:120px">
            <button onclick="loadLabor()">Filter</button>
            <button onclick="showLaborModal()" style="margin-left:auto">+ Log Labor</button>
          </div>
          <table class="data-table">
            <thead><tr><th>Worker</th><th>Type</th><th class="text-right">Hours</th>
              <th class="text-right">Rate</th><th class="text-right">Total</th>
              <th>Job</th><th>WO Ref</th><th>Date</th><th>OT</th></tr></thead>
            <tbody id="laborBody"></tbody>
          </table>
        </div>

        <!-- Change Orders Tab -->
        <div class="tab-content" id="tab-changes">
          <div class="filter-bar">
            <input type="text" id="coJobFilter" placeholder="Job Code" style="width:140px">
            <button onclick="loadChangeOrders()">Filter</button>
            <button onclick="showCOModal()" style="margin-left:auto">+ New Change Order</button>
          </div>
          <table class="data-table">
            <thead><tr><th>CO #</th><th>Description</th><th class="text-right">Material</th>
              <th class="text-right">Labor</th><th class="text-right">Total</th>
              <th>Job</th><th>Status</th><th>Actions</th></tr></thead>
            <tbody id="coBody"></tbody>
          </table>
        </div>
      </div>

      <div class="sidebar" id="sidebar"></div>
    </div>
  </div>

  <!-- Modals -->
  <div class="modal-overlay" id="estimateModal"><div class="modal">
    <h3>New Cost Estimate</h3>
    <label>Job Code *</label><input id="estM_job">
    <label>Name *</label><input id="estM_name" placeholder="e.g., Original Estimate">
    <label>Contract Value ($)</label><input id="estM_contract" type="number" step="0.01" value="0">
    <label>Notes</label><textarea id="estM_notes"></textarea>
    <div class="modal-actions">
      <button class="btn-secondary" onclick="closeModal('estimateModal')">Cancel</button>
      <button class="btn-primary" onclick="createEstimate()">Create</button>
    </div>
  </div></div>

  <div class="modal-overlay" id="costModal"><div class="modal">
    <h3>Add Cost Entry</h3>
    <label>Job Code *</label><input id="costM_job">
    <label>Category *</label><select id="costM_cat"></select>
    <label>Description *</label><input id="costM_desc">
    <label>Quantity</label><input id="costM_qty" type="number" step="0.01" value="1">
    <label>Unit</label><input id="costM_unit" placeholder="lbs, ea, sqft">
    <label>Unit Cost ($)</label><input id="costM_ucost" type="number" step="0.01" value="0">
    <label>Vendor</label><input id="costM_vendor">
    <label>PO #</label><input id="costM_po">
    <label>Date</label><input id="costM_date" type="date">
    <div class="modal-actions">
      <button class="btn-secondary" onclick="closeModal('costModal')">Cancel</button>
      <button class="btn-primary" onclick="createCost()">Add</button>
    </div>
  </div></div>

  <div class="modal-overlay" id="laborModal"><div class="modal">
    <h3>Log Labor Entry</h3>
    <label>Job Code *</label><input id="labM_job">
    <label>Worker *</label><input id="labM_worker">
    <label>Labor Type</label><select id="labM_type"></select>
    <label>Hours *</label><input id="labM_hours" type="number" step="0.25" value="0">
    <label>Rate Override ($/hr, 0=default)</label><input id="labM_rate" type="number" step="0.01" value="0">
    <label>Overtime</label><select id="labM_ot"><option value="false">No</option><option value="true">Yes</option></select>
    <label>WO Reference</label><input id="labM_wo">
    <label>Date</label><input id="labM_date" type="date">
    <label>Description</label><input id="labM_desc">
    <div class="modal-actions">
      <button class="btn-secondary" onclick="closeModal('laborModal')">Cancel</button>
      <button class="btn-primary" onclick="createLabor()">Log</button>
    </div>
  </div></div>

  <div class="modal-overlay" id="coModal"><div class="modal">
    <h3>New Change Order</h3>
    <label>Job Code *</label><input id="coM_job">
    <label>Description *</label><textarea id="coM_desc"></textarea>
    <label>Material Impact ($)</label><input id="coM_mat" type="number" step="0.01" value="0">
    <label>Labor Impact ($)</label><input id="coM_lab" type="number" step="0.01" value="0">
    <label>Other Impact ($)</label><input id="coM_other" type="number" step="0.01" value="0">
    <div class="modal-actions">
      <button class="btn-secondary" onclick="closeModal('coModal')">Cancel</button>
      <button class="btn-primary" onclick="createCO()">Create</button>
    </div>
  </div></div>

<script>
  let CONFIG = {};
  const $ = id => document.getElementById(id);
  const fmt = n => '$' + Number(n||0).toLocaleString('en-US', {minimumFractionDigits:2, maximumFractionDigits:2});
  const fmtPct = n => (n||0).toFixed(1) + '%';

  async function api(url, method, body) {
    const opts = {method: method||'GET', headers:{'Content-Type':'application/json'}};
    if (body) opts.body = JSON.stringify(body);
    return (await fetch(url, opts)).json();
  }

  async function loadConfig() {
    CONFIG = await api('/api/costing/config');
    const catSel = $('costM_cat');
    (CONFIG.cost_categories||[]).forEach(c => {
      const o = document.createElement('option'); o.value=c;
      o.textContent=(CONFIG.cost_category_labels||{})[c]||c; catSel.appendChild(o);
    });
    const costCat = $('costCatFilter');
    (CONFIG.cost_categories||[]).forEach(c => {
      const o = document.createElement('option'); o.value=c;
      o.textContent=(CONFIG.cost_category_labels||{})[c]||c; costCat.appendChild(o);
    });
    const labType = $('labM_type');
    Object.entries(CONFIG.labor_rate_labels||{}).forEach(([k,v]) => {
      const o = document.createElement('option'); o.value=k; o.textContent=v+' ('+fmt((CONFIG.default_labor_rates||{})[k])+'/hr)';
      labType.appendChild(o);
    });
  }

  function switchTab(name) {
    document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(t=>t.classList.remove('active'));
    event.target.classList.add('active');
    $('tab-'+name).classList.add('active');
  }

  function closeModal(id) { $(id).classList.remove('show'); }

  function statCard(val, label, color) {
    return '<div class="stat-card"><div class="value" style="color:var('+color+')">'+val+'</div><div class="label">'+label+'</div></div>';
  }

  // Overview
  async function loadOverview() {
    const d = await api('/api/costing/overview');
    if (!d.ok) return;
    const o = d.overview;
    $('statsRow').innerHTML =
      statCard(o.total_jobs, 'Active Jobs', '--accent') +
      statCard(fmt(o.total_contract_value), 'Total Contract', '--cyan') +
      statCard(fmt(o.total_actual), 'Total Actual', '--orange') +
      statCard(fmt(o.total_margin), 'Total Margin', o.total_margin>=0?'--green':'--red') +
      statCard(fmtPct(o.margin_pct), 'Margin %', o.margin_pct>=15?'--green':'--yellow') +
      statCard(o.jobs_over_budget, 'Over Budget', o.jobs_over_budget>0?'--red':'--green');

    // Sidebar
    let sb = '<div class="sidebar-card"><h4>Costs by Category</h4>';
    for (const [k,v] of Object.entries(o.costs_by_category||{}))
      sb += '<div class="sidebar-item"><span>'+((CONFIG.cost_category_labels||{})[k]||k)+'</span><span>'+fmt(v)+'</span></div>';
    sb += '</div>';

    sb += '<div class="sidebar-card"><h4>Jobs</h4>';
    (o.jobs||[]).forEach(j => {
      const cls = j.cost_variance<0?'text-red':'text-green';
      sb += '<div class="sidebar-item"><span>'+j.job_code+'</span><span class="'+cls+'">'+fmtPct(j.actual_margin_pct)+'</span></div>';
    });
    sb += '</div>';
    $('sidebar').innerHTML = sb;
  }

  async function loadJobSummary() {
    const jc = $('ovJobFilter').value.trim();
    if (!jc) return;
    const d = await api('/api/costing/job-summary?job_code='+encodeURIComponent(jc));
    if (!d.ok) { $('jobSummaryContent').innerHTML='<div class="empty-state">'+d.error+'</div>'; return; }
    const s = d.summary;
    const marginCls = s.actual_margin>=0?'text-green':'text-red';
    const varCls = s.cost_variance>=0?'text-green':'text-red';
    let h = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">';
    h += '<div class="sidebar-card"><h4>Contract & Budget</h4>';
    h += '<div class="sidebar-item"><span>Contract Value</span><span>'+fmt(s.contract_value)+'</span></div>';
    h += '<div class="sidebar-item"><span>Estimated Cost</span><span>'+fmt(s.estimated_total)+'</span></div>';
    h += '<div class="sidebar-item"><span>Change Orders</span><span>'+fmt(s.total_co_impact)+'</span></div>';
    h += '<div class="sidebar-item"><span>Adjusted Budget</span><span><strong>'+fmt(s.adjusted_budget)+'</strong></span></div>';
    h += '</div>';
    h += '<div class="sidebar-card"><h4>Actuals & Margin</h4>';
    h += '<div class="sidebar-item"><span>Total Actual</span><span>'+fmt(s.total_actual)+'</span></div>';
    h += '<div class="sidebar-item"><span>Variance</span><span class="'+varCls+'">'+fmt(s.cost_variance)+' ('+fmtPct(s.variance_pct)+')</span></div>';
    h += '<div class="sidebar-item"><span>Margin</span><span class="'+marginCls+'"><strong>'+fmt(s.actual_margin)+' ('+fmtPct(s.actual_margin_pct)+')</strong></span></div>';
    h += '<div class="sidebar-item"><span>Labor Hours</span><span>'+s.total_labor_hours+'</span></div>';
    h += '</div></div>';

    // Category breakdown
    h += '<div style="margin-top:16px"><table class="data-table"><thead><tr><th>Category</th><th class="text-right">Estimated</th><th class="text-right">Actual</th><th class="text-right">Variance</th></tr></thead><tbody>';
    const allCats = new Set([...Object.keys(s.estimated_by_category||{}), ...Object.keys(s.actual_by_category||{})]);
    allCats.forEach(cat => {
      const est = (s.estimated_by_category||{})[cat]||0;
      const act = (s.actual_by_category||{})[cat]||0;
      const v = est-act;
      h += '<tr><td>'+((CONFIG.cost_category_labels||{})[cat]||cat)+'</td><td class="text-right">'+fmt(est)+'</td><td class="text-right">'+fmt(act)+'</td><td class="text-right '+(v>=0?'text-green':'text-red')+'">'+fmt(v)+'</td></tr>';
    });
    h += '</tbody></table></div>';
    $('jobSummaryContent').innerHTML = h;
  }

  // Estimates
  async function loadEstimates() {
    const d = await api('/api/costing/estimates?job_code='+encodeURIComponent($('estJobFilter').value));
    const tb = $('estimatesBody');
    if (!d.ok||!d.estimates.length) { tb.innerHTML='<tr><td colspan="7" class="empty-state">No estimates</td></tr>'; return; }
    tb.innerHTML = d.estimates.map(e => '<tr>'+
      '<td><strong>'+e.name+'</strong></td>'+
      '<td>'+e.job_code+'</td>'+
      '<td><span class="badge badge-'+e.status+'">'+e.status_label+'</span></td>'+
      '<td class="text-right">'+fmt(e.total_amount)+'</td>'+
      '<td class="text-right">'+fmt(e.contract_value)+'</td>'+
      '<td class="text-right '+(e.estimated_margin>=0?'text-green':'text-red')+'">'+fmt(e.estimated_margin)+' ('+fmtPct(e.estimated_margin_pct)+')</td>'+
      '<td>'+(e.status==='draft'?'<button class="btn-success" style="padding:3px 8px;font-size:11px" onclick="approveEst(\\''+e.estimate_id+'\\')">Approve</button>':'-')+'</td>'+
    '</tr>').join('');
  }

  function showEstimateModal() { $('estimateModal').classList.add('show'); }
  async function createEstimate() {
    const d = await api('/api/costing/estimate/create','POST',{
      job_code:$('estM_job').value, name:$('estM_name').value,
      contract_value:parseFloat($('estM_contract').value)||0,
      notes:$('estM_notes').value,
    });
    if (d.ok) { closeModal('estimateModal'); loadEstimates(); loadOverview(); } else alert(d.error);
  }
  async function approveEst(id) {
    const d = await api('/api/costing/estimate/approve','POST',{estimate_id:id});
    if (d.ok) loadEstimates(); else alert(d.error);
  }

  // Cost entries
  async function loadCosts() {
    const d = await api('/api/costing/costs?job_code='+encodeURIComponent($('costJobFilter').value)+'&category='+$('costCatFilter').value);
    const tb = $('costsBody');
    if (!d.ok||!d.entries.length) { tb.innerHTML='<tr><td colspan="8" class="empty-state">No cost entries</td></tr>'; return; }
    tb.innerHTML = d.entries.map(e => '<tr>'+
      '<td>'+e.description+'</td>'+
      '<td>'+e.category_label+'</td>'+
      '<td class="text-right">'+e.quantity+(e.unit?' '+e.unit:'')+'</td>'+
      '<td class="text-right">'+fmt(e.unit_cost)+'</td>'+
      '<td class="text-right"><strong>'+fmt(e.total)+'</strong></td>'+
      '<td class="text-muted">'+(e.vendor||'-')+'</td>'+
      '<td>'+e.job_code+'</td>'+
      '<td class="text-muted">'+e.date+'</td>'+
    '</tr>').join('') +
    '<tr style="font-weight:700"><td colspan="4">Total</td><td class="text-right">'+fmt(d.total)+'</td><td colspan="3"></td></tr>';
  }
  function showCostModal() { $('costModal').classList.add('show'); }
  async function createCost() {
    const d = await api('/api/costing/cost/create','POST',{
      job_code:$('costM_job').value, category:$('costM_cat').value,
      description:$('costM_desc').value,
      quantity:parseFloat($('costM_qty').value)||1,
      unit:$('costM_unit').value,
      unit_cost:parseFloat($('costM_ucost').value)||0,
      vendor:$('costM_vendor').value, po_number:$('costM_po').value,
      date:$('costM_date').value,
    });
    if (d.ok) { closeModal('costModal'); loadCosts(); loadOverview(); } else alert(d.error);
  }

  // Labor
  async function loadLabor() {
    const d = await api('/api/costing/labor?job_code='+encodeURIComponent($('labJobFilter').value)+'&worker='+encodeURIComponent($('labWorkerFilter').value));
    const tb = $('laborBody');
    if (!d.ok||!d.entries.length) { tb.innerHTML='<tr><td colspan="9" class="empty-state">No labor entries</td></tr>'; return; }
    tb.innerHTML = d.entries.map(e => '<tr>'+
      '<td><strong>'+e.worker+'</strong></td>'+
      '<td>'+((CONFIG.labor_rate_labels||{})[e.labor_type]||e.labor_type)+'</td>'+
      '<td class="text-right">'+e.hours.toFixed(1)+'</td>'+
      '<td class="text-right">'+fmt(e.effective_rate)+'/hr</td>'+
      '<td class="text-right"><strong>'+fmt(e.total)+'</strong></td>'+
      '<td>'+e.job_code+'</td>'+
      '<td class="text-muted">'+(e.work_order_ref||'-')+'</td>'+
      '<td class="text-muted">'+e.date+'</td>'+
      '<td>'+(e.overtime?'<span class="badge badge-revised">OT</span>':'-')+'</td>'+
    '</tr>').join('') +
    '<tr style="font-weight:700"><td colspan="2">Total</td><td class="text-right">'+d.total_hours.toFixed(1)+'</td><td></td><td class="text-right">'+fmt(d.total_cost)+'</td><td colspan="4"></td></tr>';
  }
  function showLaborModal() { $('laborModal').classList.add('show'); }
  async function createLabor() {
    const d = await api('/api/costing/labor/create','POST',{
      job_code:$('labM_job').value, worker:$('labM_worker').value,
      hours:parseFloat($('labM_hours').value)||0,
      labor_type:$('labM_type').value,
      rate:parseFloat($('labM_rate').value)||0,
      overtime:$('labM_ot').value==='true',
      work_order_ref:$('labM_wo').value,
      date:$('labM_date').value,
      description:$('labM_desc').value,
    });
    if (d.ok) { closeModal('laborModal'); loadLabor(); loadOverview(); } else alert(d.error);
  }

  // Change Orders
  async function loadChangeOrders() {
    const d = await api('/api/costing/change-orders?job_code='+encodeURIComponent($('coJobFilter').value));
    const tb = $('coBody');
    if (!d.ok||!d.change_orders.length) { tb.innerHTML='<tr><td colspan="8" class="empty-state">No change orders</td></tr>'; return; }
    tb.innerHTML = d.change_orders.map(c => '<tr>'+
      '<td><strong>CO-'+c.change_order_number+'</strong></td>'+
      '<td>'+c.description+'</td>'+
      '<td class="text-right">'+fmt(c.material_impact)+'</td>'+
      '<td class="text-right">'+fmt(c.labor_impact)+'</td>'+
      '<td class="text-right"><strong>'+fmt(c.total_impact)+'</strong></td>'+
      '<td>'+c.job_code+'</td>'+
      '<td>'+(c.approved?'<span class="badge badge-approved">Approved</span>':'<span class="badge badge-draft">Pending</span>')+'</td>'+
      '<td>'+(!c.approved?'<button class="btn-success" style="padding:3px 8px;font-size:11px" onclick="approveCO(\\''+c.co_id+'\\')">Approve</button>':'-')+'</td>'+
    '</tr>').join('');
  }
  function showCOModal() { $('coModal').classList.add('show'); }
  async function createCO() {
    const d = await api('/api/costing/change-order/create','POST',{
      job_code:$('coM_job').value, description:$('coM_desc').value,
      material_impact:parseFloat($('coM_mat').value)||0,
      labor_impact:parseFloat($('coM_lab').value)||0,
      other_impact:parseFloat($('coM_other').value)||0,
    });
    if (d.ok) { closeModal('coModal'); loadChangeOrders(); loadOverview(); } else alert(d.error);
  }
  async function approveCO(id) {
    const d = await api('/api/costing/change-order/approve','POST',{co_id:id});
    if (d.ok) { loadChangeOrders(); loadOverview(); } else alert(d.error);
  }

  // Init
  loadConfig().then(() => {
    loadOverview(); loadEstimates(); loadCosts(); loadLabor(); loadChangeOrders();
  });
  setInterval(loadOverview, 60000);
</script>
</body>
</html>"""
