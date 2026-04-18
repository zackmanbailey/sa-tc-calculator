"""
TitanForge — Document Management Dashboard Template
=====================================================
Drawing revisions, RFIs, transmittals, and BOM change tracking.
"""

DOCUMENT_MANAGEMENT_PAGE_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Document Management — TitanForge</title>
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

  /* Stat cards */
  .stats-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
               gap: 12px; margin-bottom: 20px; }
  .stat-card { background: var(--surface); border: 1px solid var(--border);
               border-radius: 8px; padding: 16px; text-align: center; }
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

  /* Table */
  .data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
  .data-table th { text-align: left; padding: 10px 12px; background: var(--surface);
                   border-bottom: 2px solid var(--border); color: var(--muted);
                   font-weight: 600; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; }
  .data-table td { padding: 10px 12px; border-bottom: 1px solid var(--border); vertical-align: top; }
  .data-table tr:hover { background: rgba(59,130,246,0.05); }

  /* Badges */
  .badge { display: inline-block; padding: 2px 8px; border-radius: 4px;
           font-size: 11px; font-weight: 600; text-transform: uppercase; }
  .badge-draft { background: rgba(148,163,184,0.2); color: var(--muted); }
  .badge-submitted { background: rgba(59,130,246,0.2); color: var(--accent); }
  .badge-in_review { background: rgba(234,179,8,0.2); color: var(--yellow); }
  .badge-approved { background: rgba(34,197,94,0.2); color: var(--green); }
  .badge-rejected { background: rgba(239,68,68,0.2); color: var(--red); }
  .badge-superseded { background: rgba(148,163,184,0.15); color: #64748b; }
  .badge-open { background: rgba(59,130,246,0.2); color: var(--accent); }
  .badge-pending { background: rgba(234,179,8,0.2); color: var(--yellow); }
  .badge-answered { background: rgba(34,197,94,0.2); color: var(--green); }
  .badge-closed { background: rgba(148,163,184,0.2); color: var(--muted); }
  .badge-void { background: rgba(239,68,68,0.15); color: #f87171; }
  .badge-sent { background: rgba(6,182,212,0.2); color: var(--cyan); }
  .badge-acknowledged { background: rgba(34,197,94,0.2); color: var(--green); }
  .badge-critical { background: rgba(239,68,68,0.2); color: var(--red); }
  .badge-high { background: rgba(249,115,22,0.2); color: var(--orange); }
  .badge-normal { background: rgba(59,130,246,0.2); color: var(--accent); }
  .badge-low { background: rgba(148,163,184,0.2); color: var(--muted); }

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
  .modal textarea { resize: vertical; min-height: 80px; }
  .modal-actions { display: flex; gap: 8px; margin-top: 20px; justify-content: flex-end; }
  .modal-actions button { padding: 8px 20px; border-radius: 6px; border: none;
                          font-size: 13px; cursor: pointer; font-weight: 500; }
  .btn-primary { background: var(--accent); color: white; }
  .btn-secondary { background: var(--border); color: var(--text); }
  .btn-danger { background: var(--red); color: white; }
  .btn-success { background: var(--green); color: white; }

  .empty-state { text-align: center; padding: 40px; color: var(--muted); }
  .text-muted { color: var(--muted); font-size: 12px; }
  .text-overdue { color: var(--red); font-weight: 600; }

  /* Sidebar summary */
  .page-layout { display: grid; grid-template-columns: 1fr 300px; gap: 20px; }
  .sidebar { display: flex; flex-direction: column; gap: 16px; }
  .sidebar-card { background: var(--surface); border: 1px solid var(--border);
                  border-radius: 8px; padding: 16px; }
  .sidebar-card h4 { font-size: 13px; color: var(--muted); margin-bottom: 12px;
                     text-transform: uppercase; letter-spacing: 0.5px; }
  .sidebar-item { display: flex; justify-content: space-between; padding: 4px 0;
                  font-size: 13px; }

  @media (max-width: 1100px) {
    .page-layout { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>
  <div class="topbar">
    <h1>Document Management</h1>
    <div class="nav-links">
      <a href="/dashboard">Dashboard</a>
      <a href="/schedule">Schedule</a>
      <a href="/work-orders/all">Work Orders</a>
    </div>
  </div>

  <div class="container">
    <div class="stats-row" id="statsRow"></div>

    <div class="page-layout">
      <div class="main-content">
        <div class="tabs">
          <button class="tab active" onclick="switchTab('revisions')">Drawing Revisions</button>
          <button class="tab" onclick="switchTab('rfis')">RFIs</button>
          <button class="tab" onclick="switchTab('transmittals')">Transmittals</button>
          <button class="tab" onclick="switchTab('bom')">BOM Changes</button>
        </div>

        <!-- Revisions Tab -->
        <div class="tab-content active" id="tab-revisions">
          <div class="filter-bar">
            <input type="text" id="revJobFilter" placeholder="Job Code" style="width:120px">
            <select id="revStatusFilter"><option value="">All Statuses</option></select>
            <select id="revCategoryFilter"><option value="">All Categories</option></select>
            <button onclick="loadRevisions()">Filter</button>
            <button onclick="showRevisionModal()" style="margin-left:auto">+ New Revision</button>
          </div>
          <table class="data-table">
            <thead><tr>
              <th>Drawing #</th><th>Title</th><th>Rev</th><th>Category</th>
              <th>Status</th><th>Job</th><th>Created</th><th>Actions</th>
            </tr></thead>
            <tbody id="revisionsBody"></tbody>
          </table>
        </div>

        <!-- RFIs Tab -->
        <div class="tab-content" id="tab-rfis">
          <div class="filter-bar">
            <input type="text" id="rfiJobFilter" placeholder="Job Code" style="width:120px">
            <select id="rfiStatusFilter"><option value="">All Statuses</option></select>
            <button onclick="loadRFIs()">Filter</button>
            <button onclick="showRFIModal()" style="margin-left:auto">+ New RFI</button>
          </div>
          <table class="data-table">
            <thead><tr>
              <th>RFI #</th><th>Subject</th><th>Priority</th><th>Status</th>
              <th>Job</th><th>Due</th><th>Created</th><th>Actions</th>
            </tr></thead>
            <tbody id="rfisBody"></tbody>
          </table>
        </div>

        <!-- Transmittals Tab -->
        <div class="tab-content" id="tab-transmittals">
          <div class="filter-bar">
            <input type="text" id="xmitJobFilter" placeholder="Job Code" style="width:120px">
            <select id="xmitStatusFilter"><option value="">All Statuses</option></select>
            <button onclick="loadTransmittals()">Filter</button>
            <button onclick="showTransmittalModal()" style="margin-left:auto">+ New Transmittal</button>
          </div>
          <table class="data-table">
            <thead><tr>
              <th>XMIT #</th><th>Recipient</th><th>Purpose</th><th>Status</th>
              <th>Job</th><th>Sent</th><th>Actions</th>
            </tr></thead>
            <tbody id="transmittalsBody"></tbody>
          </table>
        </div>

        <!-- BOM Changes Tab -->
        <div class="tab-content" id="tab-bom">
          <div class="filter-bar">
            <input type="text" id="bomJobFilter" placeholder="Job Code" style="width:120px">
            <button onclick="loadBOMChanges()">Filter</button>
            <button onclick="showBOMChangeModal()" style="margin-left:auto">+ Log Change</button>
          </div>
          <table class="data-table">
            <thead><tr>
              <th>Change ID</th><th>Type</th><th>Component</th><th>Field</th>
              <th>Old</th><th>New</th><th>Job</th><th>By</th><th>Date</th>
            </tr></thead>
            <tbody id="bomBody"></tbody>
          </table>
        </div>
      </div>

      <div class="sidebar" id="sidebar"></div>
    </div>
  </div>

  <!-- Modals -->
  <div class="modal-overlay" id="revisionModal">
    <div class="modal">
      <h3>New Drawing Revision</h3>
      <label>Job Code *</label><input id="revM_job" placeholder="e.g., JOB-001">
      <label>Drawing Number *</label><input id="revM_number" placeholder="e.g., SD-001">
      <label>Title *</label><input id="revM_title" placeholder="Drawing title">
      <label>Category</label>
      <select id="revM_category"></select>
      <label>Revision</label><input id="revM_rev" placeholder="e.g., A, B, 01">
      <label>Filename</label><input id="revM_filename" placeholder="drawing-file.pdf">
      <label>Description</label><textarea id="revM_desc"></textarea>
      <div class="modal-actions">
        <button class="btn-secondary" onclick="closeModal('revisionModal')">Cancel</button>
        <button class="btn-primary" onclick="createRevision()">Create</button>
      </div>
    </div>
  </div>

  <div class="modal-overlay" id="rfiModal">
    <div class="modal">
      <h3>New RFI</h3>
      <label>Job Code *</label><input id="rfiM_job" placeholder="e.g., JOB-001">
      <label>Subject *</label><input id="rfiM_subject" placeholder="RFI subject">
      <label>Question *</label><textarea id="rfiM_question" placeholder="Describe the question"></textarea>
      <label>Priority</label>
      <select id="rfiM_priority">
        <option value="normal">Normal</option>
        <option value="high">High</option>
        <option value="critical">Critical</option>
        <option value="low">Low</option>
      </select>
      <label>Drawing Reference</label><input id="rfiM_drawref" placeholder="SD-001">
      <label>Due Date</label><input id="rfiM_due" type="date">
      <div class="modal-actions">
        <button class="btn-secondary" onclick="closeModal('rfiModal')">Cancel</button>
        <button class="btn-primary" onclick="createRFI()">Create</button>
      </div>
    </div>
  </div>

  <div class="modal-overlay" id="transmittalModal">
    <div class="modal">
      <h3>New Transmittal</h3>
      <label>Job Code *</label><input id="xmitM_job" placeholder="e.g., JOB-001">
      <label>Recipient *</label><input id="xmitM_recipient" placeholder="Recipient name">
      <label>Recipient Email</label><input id="xmitM_email" placeholder="email@example.com">
      <label>Purpose *</label>
      <select id="xmitM_purpose"></select>
      <label>Subject</label><input id="xmitM_subject" placeholder="Transmittal subject">
      <label>Notes</label><textarea id="xmitM_notes"></textarea>
      <div class="modal-actions">
        <button class="btn-secondary" onclick="closeModal('transmittalModal')">Cancel</button>
        <button class="btn-primary" onclick="createTransmittal()">Create</button>
      </div>
    </div>
  </div>

  <div class="modal-overlay" id="bomModal">
    <div class="modal">
      <h3>Log BOM Change</h3>
      <label>Job Code *</label><input id="bomM_job" placeholder="e.g., JOB-001">
      <label>Change Type *</label>
      <select id="bomM_type"></select>
      <label>Component *</label><input id="bomM_component" placeholder="e.g., Rafter R1">
      <label>Field Changed</label><input id="bomM_field" placeholder="e.g., length">
      <label>Old Value</label><input id="bomM_old" placeholder="Previous value">
      <label>New Value</label><input id="bomM_new" placeholder="New value">
      <label>Reason</label><textarea id="bomM_reason"></textarea>
      <div class="modal-actions">
        <button class="btn-secondary" onclick="closeModal('bomModal')">Cancel</button>
        <button class="btn-primary" onclick="createBOMChange()">Log Change</button>
      </div>
    </div>
  </div>

  <div class="modal-overlay" id="respondModal">
    <div class="modal">
      <h3>Respond to RFI</h3>
      <input type="hidden" id="respondM_id">
      <label>Response *</label><textarea id="respondM_response" placeholder="Enter response"></textarea>
      <div class="modal-actions">
        <button class="btn-secondary" onclick="closeModal('respondModal')">Cancel</button>
        <button class="btn-success" onclick="respondRFI()">Submit Response</button>
      </div>
    </div>
  </div>

  <div class="modal-overlay" id="transitionModal">
    <div class="modal">
      <h3>Change Revision Status</h3>
      <input type="hidden" id="transM_id">
      <label>New Status</label>
      <select id="transM_status"></select>
      <label>Rejection Reason (if rejecting)</label>
      <textarea id="transM_reason" placeholder="Reason for rejection"></textarea>
      <div class="modal-actions">
        <button class="btn-secondary" onclick="closeModal('transitionModal')">Cancel</button>
        <button class="btn-primary" onclick="transitionRevision()">Update Status</button>
      </div>
    </div>
  </div>

<script>
  let CONFIG = {};

  async function api(url, method, body) {
    const opts = { method: method || 'GET', headers: {'Content-Type':'application/json'} };
    if (body) opts.body = JSON.stringify(body);
    const r = await fetch(url, opts);
    return r.json();
  }

  async function loadConfig() {
    CONFIG = await api('/api/documents/config');
    // Populate filter dropdowns
    const revStat = document.getElementById('revStatusFilter');
    (CONFIG.revision_statuses||[]).forEach(s => {
      const o = document.createElement('option'); o.value = s;
      o.textContent = (CONFIG.revision_status_labels||{})[s]||s; revStat.appendChild(o);
    });
    const revCat = document.getElementById('revCategoryFilter');
    (CONFIG.document_categories||[]).forEach(c => {
      const o = document.createElement('option'); o.value = c;
      o.textContent = (CONFIG.document_category_labels||{})[c]||c; revCat.appendChild(o);
    });
    const rfiStat = document.getElementById('rfiStatusFilter');
    (CONFIG.rfi_statuses||[]).forEach(s => {
      const o = document.createElement('option'); o.value = s;
      o.textContent = (CONFIG.rfi_status_labels||{})[s]||s; rfiStat.appendChild(o);
    });
    const xmitStat = document.getElementById('xmitStatusFilter');
    (CONFIG.transmittal_statuses||[]).forEach(s => {
      const o = document.createElement('option'); o.value = s;
      o.textContent = (CONFIG.transmittal_status_labels||{})[s]||s; xmitStat.appendChild(o);
    });
    // Modal dropdowns
    const catSel = document.getElementById('revM_category');
    (CONFIG.document_categories||[]).forEach(c => {
      const o = document.createElement('option'); o.value = c;
      o.textContent = (CONFIG.document_category_labels||{})[c]||c; catSel.appendChild(o);
    });
    const purSel = document.getElementById('xmitM_purpose');
    (CONFIG.transmittal_purposes||[]).forEach(p => {
      const o = document.createElement('option'); o.value = p;
      o.textContent = (CONFIG.transmittal_purpose_labels||{})[p]||p; purSel.appendChild(o);
    });
    const bomType = document.getElementById('bomM_type');
    (CONFIG.bom_change_types||[]).forEach(t => {
      const o = document.createElement('option'); o.value = t;
      o.textContent = (CONFIG.bom_change_type_labels||{})[t]||t; bomType.appendChild(o);
    });
  }

  function switchTab(name) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');
    document.getElementById('tab-'+name).classList.add('active');
  }

  function badge(status) {
    return '<span class="badge badge-'+status+'">'+
      ((CONFIG.revision_status_labels||{})[status] ||
       (CONFIG.rfi_status_labels||{})[status] ||
       (CONFIG.transmittal_status_labels||{})[status] || status) +'</span>';
  }
  function priBadge(p) {
    return '<span class="badge badge-'+p+'">'+ ((CONFIG.rfi_priority_labels||{})[p]||p) +'</span>';
  }
  function fmtDate(d) { return d ? d.substring(0,10) : '-'; }

  // ── Revisions ──
  async function loadRevisions() {
    const j = document.getElementById('revJobFilter').value;
    const s = document.getElementById('revStatusFilter').value;
    const c = document.getElementById('revCategoryFilter').value;
    let url = '/api/documents/revisions?job_code='+encodeURIComponent(j)+'&status='+s+'&category='+c;
    const data = await api(url);
    const tb = document.getElementById('revisionsBody');
    if (!data.ok || !data.revisions.length) { tb.innerHTML='<tr><td colspan="8" class="empty-state">No revisions found</td></tr>'; return; }
    tb.innerHTML = data.revisions.map(r => '<tr>'+
      '<td><strong>'+r.drawing_number+'</strong></td>'+
      '<td>'+r.title+'</td>'+
      '<td>'+(r.revision||'-')+'</td>'+
      '<td>'+((CONFIG.document_category_labels||{})[r.category]||r.category)+'</td>'+
      '<td>'+badge(r.status)+'</td>'+
      '<td>'+r.job_code+'</td>'+
      '<td class="text-muted">'+fmtDate(r.created_at)+'</td>'+
      '<td><button class="btn-primary" style="padding:3px 8px;font-size:11px" '+
        'onclick="showTransition(\\''+r.revision_id+'\\',\\''+r.status+'\\')">Status</button></td>'+
    '</tr>').join('');
  }

  function showRevisionModal() { document.getElementById('revisionModal').classList.add('show'); }
  async function createRevision() {
    const d = await api('/api/documents/revision/create','POST',{
      job_code: document.getElementById('revM_job').value,
      drawing_number: document.getElementById('revM_number').value,
      title: document.getElementById('revM_title').value,
      category: document.getElementById('revM_category').value,
      revision: document.getElementById('revM_rev').value,
      filename: document.getElementById('revM_filename').value,
      description: document.getElementById('revM_desc').value,
    });
    if (d.ok) { closeModal('revisionModal'); loadRevisions(); loadSummary(); }
    else alert(d.error||'Error');
  }

  function showTransition(id, current) {
    document.getElementById('transM_id').value = id;
    const sel = document.getElementById('transM_status');
    sel.innerHTML = '';
    const flow = (CONFIG.revision_status_flow||{})[current]||[];
    flow.forEach(s => {
      const o = document.createElement('option'); o.value = s;
      o.textContent = (CONFIG.revision_status_labels||{})[s]||s; sel.appendChild(o);
    });
    document.getElementById('transitionModal').classList.add('show');
  }
  async function transitionRevision() {
    const d = await api('/api/documents/revision/transition','POST',{
      revision_id: document.getElementById('transM_id').value,
      status: document.getElementById('transM_status').value,
      rejection_reason: document.getElementById('transM_reason').value,
    });
    if (d.ok) { closeModal('transitionModal'); loadRevisions(); loadSummary(); }
    else alert(d.error||'Error');
  }

  // ── RFIs ──
  async function loadRFIs() {
    const j = document.getElementById('rfiJobFilter').value;
    const s = document.getElementById('rfiStatusFilter').value;
    const data = await api('/api/documents/rfis?job_code='+encodeURIComponent(j)+'&status='+s);
    const tb = document.getElementById('rfisBody');
    if (!data.ok || !data.rfis.length) { tb.innerHTML='<tr><td colspan="8" class="empty-state">No RFIs found</td></tr>'; return; }
    tb.innerHTML = data.rfis.map(r => '<tr>'+
      '<td><strong>RFI-'+r.rfi_number+'</strong></td>'+
      '<td>'+r.subject+'</td>'+
      '<td>'+priBadge(r.priority)+'</td>'+
      '<td>'+badge(r.status)+'</td>'+
      '<td>'+r.job_code+'</td>'+
      '<td class="'+(r.is_overdue?'text-overdue':'text-muted')+'">'+fmtDate(r.due_date)+'</td>'+
      '<td class="text-muted">'+fmtDate(r.created_at)+'</td>'+
      '<td>'+rfiActions(r)+'</td>'+
    '</tr>').join('');
  }
  function rfiActions(r) {
    let btns = '';
    if (r.status==='open'||r.status==='pending')
      btns += '<button class="btn-success" style="padding:3px 8px;font-size:11px;margin:1px" onclick="showRespondModal(\\''+r.rfi_id+'\\')">Respond</button>';
    if (r.status==='answered')
      btns += '<button class="btn-primary" style="padding:3px 8px;font-size:11px;margin:1px" onclick="closeRFI(\\''+r.rfi_id+'\\')">Close</button>';
    if (r.status!=='void'&&r.status!=='closed')
      btns += '<button class="btn-danger" style="padding:3px 8px;font-size:11px;margin:1px" onclick="voidRFI(\\''+r.rfi_id+'\\')">Void</button>';
    return btns || '-';
  }
  function showRFIModal() { document.getElementById('rfiModal').classList.add('show'); }
  async function createRFI() {
    const d = await api('/api/documents/rfi/create','POST',{
      job_code: document.getElementById('rfiM_job').value,
      subject: document.getElementById('rfiM_subject').value,
      question: document.getElementById('rfiM_question').value,
      priority: document.getElementById('rfiM_priority').value,
      drawing_ref: document.getElementById('rfiM_drawref').value,
      due_date: document.getElementById('rfiM_due').value,
    });
    if (d.ok) { closeModal('rfiModal'); loadRFIs(); loadSummary(); }
    else alert(d.error||'Error');
  }
  function showRespondModal(id) {
    document.getElementById('respondM_id').value = id;
    document.getElementById('respondModal').classList.add('show');
  }
  async function respondRFI() {
    const d = await api('/api/documents/rfi/respond','POST',{
      rfi_id: document.getElementById('respondM_id').value,
      response: document.getElementById('respondM_response').value,
    });
    if (d.ok) { closeModal('respondModal'); loadRFIs(); loadSummary(); }
    else alert(d.error||'Error');
  }
  async function closeRFI(id) {
    if (!confirm('Close this RFI?')) return;
    const d = await api('/api/documents/rfi/close','POST',{rfi_id:id});
    if (d.ok) { loadRFIs(); loadSummary(); } else alert(d.error||'Error');
  }
  async function voidRFI(id) {
    if (!confirm('Void this RFI?')) return;
    const d = await api('/api/documents/rfi/void','POST',{rfi_id:id});
    if (d.ok) { loadRFIs(); loadSummary(); } else alert(d.error||'Error');
  }

  // ── Transmittals ──
  async function loadTransmittals() {
    const j = document.getElementById('xmitJobFilter').value;
    const s = document.getElementById('xmitStatusFilter').value;
    const data = await api('/api/documents/transmittals?job_code='+encodeURIComponent(j)+'&status='+s);
    const tb = document.getElementById('transmittalsBody');
    if (!data.ok || !data.transmittals.length) { tb.innerHTML='<tr><td colspan="7" class="empty-state">No transmittals found</td></tr>'; return; }
    tb.innerHTML = data.transmittals.map(x => '<tr>'+
      '<td><strong>XMIT-'+x.transmittal_number+'</strong></td>'+
      '<td>'+x.recipient+'</td>'+
      '<td>'+((CONFIG.transmittal_purpose_labels||{})[x.purpose]||x.purpose)+'</td>'+
      '<td>'+badge(x.status)+'</td>'+
      '<td>'+x.job_code+'</td>'+
      '<td class="text-muted">'+fmtDate(x.sent_at)+'</td>'+
      '<td>'+xmitActions(x)+'</td>'+
    '</tr>').join('');
  }
  function xmitActions(x) {
    let btns = '';
    if (x.status==='draft')
      btns += '<button class="btn-primary" style="padding:3px 8px;font-size:11px;margin:1px" onclick="sendXmit(\\''+x.transmittal_id+'\\')">Send</button>';
    if (x.status==='sent')
      btns += '<button class="btn-success" style="padding:3px 8px;font-size:11px;margin:1px" onclick="ackXmit(\\''+x.transmittal_id+'\\')">Acknowledge</button>';
    return btns || '-';
  }
  function showTransmittalModal() { document.getElementById('transmittalModal').classList.add('show'); }
  async function createTransmittal() {
    const d = await api('/api/documents/transmittal/create','POST',{
      job_code: document.getElementById('xmitM_job').value,
      recipient: document.getElementById('xmitM_recipient').value,
      recipient_email: document.getElementById('xmitM_email').value,
      purpose: document.getElementById('xmitM_purpose').value,
      subject: document.getElementById('xmitM_subject').value,
      notes: document.getElementById('xmitM_notes').value,
    });
    if (d.ok) { closeModal('transmittalModal'); loadTransmittals(); loadSummary(); }
    else alert(d.error||'Error');
  }
  async function sendXmit(id) {
    const d = await api('/api/documents/transmittal/send','POST',{transmittal_id:id});
    if (d.ok) loadTransmittals(); else alert(d.error||'Error');
  }
  async function ackXmit(id) {
    const d = await api('/api/documents/transmittal/acknowledge','POST',{transmittal_id:id});
    if (d.ok) loadTransmittals(); else alert(d.error||'Error');
  }

  // ── BOM Changes ──
  async function loadBOMChanges() {
    const j = document.getElementById('bomJobFilter').value;
    const data = await api('/api/documents/bom-changes?job_code='+encodeURIComponent(j));
    const tb = document.getElementById('bomBody');
    if (!data.ok || !data.changes.length) { tb.innerHTML='<tr><td colspan="9" class="empty-state">No BOM changes found</td></tr>'; return; }
    tb.innerHTML = data.changes.map(c => '<tr>'+
      '<td class="text-muted">'+c.change_id+'</td>'+
      '<td>'+((CONFIG.bom_change_type_labels||{})[c.change_type]||c.change_type)+'</td>'+
      '<td><strong>'+c.component+'</strong></td>'+
      '<td>'+(c.field_changed||'-')+'</td>'+
      '<td>'+(c.old_value||'-')+'</td>'+
      '<td>'+(c.new_value||'-')+'</td>'+
      '<td>'+c.job_code+'</td>'+
      '<td class="text-muted">'+c.created_by+'</td>'+
      '<td class="text-muted">'+fmtDate(c.created_at)+'</td>'+
    '</tr>').join('');
  }
  function showBOMChangeModal() { document.getElementById('bomModal').classList.add('show'); }
  async function createBOMChange() {
    const d = await api('/api/documents/bom-change/log','POST',{
      job_code: document.getElementById('bomM_job').value,
      change_type: document.getElementById('bomM_type').value,
      component: document.getElementById('bomM_component').value,
      field_changed: document.getElementById('bomM_field').value,
      old_value: document.getElementById('bomM_old').value,
      new_value: document.getElementById('bomM_new').value,
      reason: document.getElementById('bomM_reason').value,
    });
    if (d.ok) { closeModal('bomModal'); loadBOMChanges(); loadSummary(); }
    else alert(d.error||'Error');
  }

  // ── Summary ──
  async function loadSummary() {
    const data = await api('/api/documents/summary');
    if (!data.ok) return;
    const s = data.summary;
    document.getElementById('statsRow').innerHTML =
      statCard(s.total_revisions||0, 'Total Revisions', '--accent') +
      statCard(s.revisions_by_status?.approved||0, 'Approved', '--green') +
      statCard(s.revisions_by_status?.in_review||0, 'In Review', '--yellow') +
      statCard(s.rfi_stats?.open||0, 'Open RFIs', '--orange') +
      statCard(s.rfi_stats?.overdue||0, 'Overdue RFIs', '--red') +
      statCard(s.transmittal_stats?.total||0, 'Transmittals', '--cyan');

    // Sidebar
    let sb = '<div class="sidebar-card"><h4>Revisions by Status</h4>';
    for (const [k,v] of Object.entries(s.revisions_by_status||{}))
      sb += '<div class="sidebar-item"><span>'+((CONFIG.revision_status_labels||{})[k]||k)+'</span><span>'+v+'</span></div>';
    sb += '</div>';
    sb += '<div class="sidebar-card"><h4>By Category</h4>';
    for (const [k,v] of Object.entries(s.revisions_by_category||{}))
      sb += '<div class="sidebar-item"><span>'+((CONFIG.document_category_labels||{})[k]||k)+'</span><span>'+v+'</span></div>';
    sb += '</div>';
    sb += '<div class="sidebar-card"><h4>RFI Summary</h4>';
    const rs = s.rfi_stats||{};
    sb += '<div class="sidebar-item"><span>Total</span><span>'+(rs.total||0)+'</span></div>';
    sb += '<div class="sidebar-item"><span>Open</span><span>'+(rs.open||0)+'</span></div>';
    sb += '<div class="sidebar-item"><span>Overdue</span><span class="'+(rs.overdue?'text-overdue':'')+'">'+(rs.overdue||0)+'</span></div>';
    sb += '<div class="sidebar-item"><span>Answered</span><span>'+(rs.answered||0)+'</span></div>';
    sb += '</div>';
    document.getElementById('sidebar').innerHTML = sb;
  }
  function statCard(val, label, color) {
    return '<div class="stat-card"><div class="value" style="color:var('+color+')">'+val+'</div><div class="label">'+label+'</div></div>';
  }

  function closeModal(id) { document.getElementById(id).classList.remove('show'); }

  // Init
  loadConfig().then(() => { loadRevisions(); loadRFIs(); loadTransmittals(); loadBOMChanges(); loadSummary(); });
  setInterval(() => { loadSummary(); }, 60000);
</script>
</body>
</html>"""
