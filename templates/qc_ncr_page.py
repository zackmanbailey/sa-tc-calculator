"""
TitanForge v4 — NCR Management
=================================
Non-conformance reports, disposition workflow, root cause analysis, corrective actions.
"""

QC_NCR_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a;
        --tf-card: #1e293b;
        --tf-text: #e2e8f0;
        --tf-muted: #94a3b8;
        --tf-gold: #d4a843;
        --tf-blue: #3b82f6;
    }
    .ncr-container {
        max-width: 1400px; margin: 0 auto; padding: 24px 32px;
        font-family: 'Inter', system-ui, -apple-system, sans-serif; color: var(--tf-text);
    }
    .page-header { margin-bottom: 32px; }
    .page-header h1 { font-size: 28px; font-weight: 800; margin: 0 0 6px 0; }
    .page-header p { font-size: 14px; color: var(--tf-muted); margin: 0; }
    .toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
    .toolbar input[type="text"] { background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px 16px; color: var(--tf-text); font-size: 14px; width: 260px; }
    .toolbar input::placeholder { color: var(--tf-muted); }
    .toolbar select { background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px; }
    .btn-gold { background: var(--tf-gold); color: #0f172a; border: none; border-radius: 8px; padding: 10px 20px; font-weight: 700; font-size: 14px; cursor: pointer; }
    .btn-gold:hover { opacity: 0.9; }
    .btn-outline { background: transparent; color: var(--tf-muted); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 10px 20px; font-weight: 600; font-size: 14px; cursor: pointer; }
    .btn-outline:hover { border-color: var(--tf-gold); color: var(--tf-gold); }
    .stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
    @media (max-width: 900px) { .stats-row { grid-template-columns: 1fr 1fr; } }
    .stat-card { background: var(--tf-card); border-radius: 10px; padding: 18px; border: 1px solid rgba(255,255,255,0.06); }
    .stat-card .stat-label { font-size: 12px; color: var(--tf-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
    .stat-card .stat-value { font-size: 24px; font-weight: 800; }
    .data-card { background: var(--tf-card); border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); overflow: hidden; }
    .data-table { width: 100%; border-collapse: collapse; font-size: 14px; }
    .data-table thead th {
        background: #1a2744; padding: 14px 16px; text-align: left; font-weight: 700;
        font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--tf-muted);
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .data-table tbody td { padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.04); }
    .data-table tbody tr { transition: background 0.15s; cursor: pointer; }
    .data-table tbody tr:hover { background: rgba(255,255,255,0.04); }
    .badge { display: inline-block; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; }
    .badge-open { background: rgba(239,68,68,0.2); color: #f87171; }
    .badge-review { background: rgba(212,168,67,0.2); color: var(--tf-gold); }
    .badge-rework { background: rgba(59,130,246,0.2); color: #60a5fa; }
    .badge-closed { background: rgba(34,197,94,0.2); color: #4ade80; }
    .badge-scrap { background: rgba(148,163,184,0.2); color: #94a3b8; }
    .severity-high { color: #f87171; font-weight: 700; }
    .severity-medium { color: var(--tf-gold); font-weight: 600; }
    .severity-low { color: var(--tf-muted); }
    .empty-state { text-align: center; padding: 60px 20px; color: var(--tf-muted); }
    .empty-state h3 { font-size: 18px; margin-bottom: 8px; color: var(--tf-text); }
    .loading { text-align: center; padding: 40px; color: var(--tf-muted); }
    .modal-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 1000; justify-content: center; align-items: center; }
    .modal-overlay.active { display: flex; }
    .modal { background: var(--tf-card); border-radius: 12px; padding: 28px; width: 640px; max-width: 90vw; border: 1px solid rgba(255,255,255,0.1); max-height: 85vh; overflow-y: auto; }
    .modal h2 { font-size: 20px; margin: 0 0 20px 0; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 24px; }
    .form-group { margin-bottom: 16px; }
    .form-group label { display: block; font-size: 13px; font-weight: 600; color: var(--tf-muted); margin-bottom: 6px; }
    .form-group input, .form-group select, .form-group textarea {
        width: 100%; background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px; font-family: inherit; box-sizing: border-box;
    }
    .form-group textarea { min-height: 70px; resize: vertical; }
    .disposition-btns { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; }
    .disposition-btns button { padding: 8px 16px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); background: var(--tf-bg); color: var(--tf-text); font-size: 13px; font-weight: 600; cursor: pointer; }
    .disposition-btns button:hover { border-color: var(--tf-blue); }
    .disposition-btns button.active { background: var(--tf-blue); border-color: var(--tf-blue); color: #fff; }
</style>

<div class="ncr-container">
    <div class="page-header">
        <h1>NCR Management</h1>
        <p>Non-conformance reports with disposition workflow and corrective actions</p>
    </div>
    <div class="stats-row">
        <div class="stat-card"><div class="stat-label">Open NCRs</div><div class="stat-value" id="statOpen" style="color:#f87171;">--</div></div>
        <div class="stat-card"><div class="stat-label">In Review</div><div class="stat-value" id="statReview" style="color:var(--tf-gold);">--</div></div>
        <div class="stat-card"><div class="stat-label">Rework In Progress</div><div class="stat-value" id="statRework" style="color:var(--tf-blue);">--</div></div>
        <div class="stat-card"><div class="stat-label">Closed This Month</div><div class="stat-value" id="statClosed" style="color:#4ade80;">--</div></div>
    </div>
    <div class="toolbar">
        <div style="display:flex;gap:10px;align-items:center;">
            <input type="text" id="ncrSearch" placeholder="Search NCRs..." oninput="filterNCRs()">
            <select id="filterStatus" onchange="filterNCRs()">
                <option value="">All Status</option>
                <option value="open">Open</option>
                <option value="review">In Review</option>
                <option value="rework">Rework</option>
                <option value="closed">Closed</option>
                <option value="scrap">Scrap</option>
            </select>
            <select id="filterSeverity" onchange="filterNCRs()">
                <option value="">All Severity</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
            </select>
        </div>
        <div style="display:flex;gap:10px;">
            <button class="btn-outline" onclick="exportNCRs()">Export</button>
            <button class="btn-gold" onclick="openNewNCR()">+ New NCR</button>
        </div>
    </div>
    <div class="data-card">
        <div id="ncrTableWrap" class="loading">Loading NCRs...</div>
    </div>
</div>

<div class="modal-overlay" id="ncrModal">
    <div class="modal">
        <h2 id="ncrModalTitle">New NCR</h2>
        <input type="hidden" id="ncrId">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div class="form-group"><label>NCR Number</label><input type="text" id="ncrNumber" placeholder="Auto-generated" readonly></div>
            <div class="form-group"><label>Date</label><input type="date" id="ncrDate"></div>
        </div>
        <div class="form-group"><label>Project / Job Code</label><input type="text" id="ncrProject" placeholder="Job code"></div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div class="form-group"><label>Component</label><input type="text" id="ncrComponent" placeholder="e.g. Rafter R1"></div>
            <div class="form-group"><label>Severity</label><select id="ncrSeverity"><option value="low">Low</option><option value="medium" selected>Medium</option><option value="high">High</option></select></div>
        </div>
        <div class="form-group"><label>Description of Non-Conformance</label><textarea id="ncrDescription" placeholder="Describe the issue in detail..."></textarea></div>
        <div class="form-group"><label>Root Cause Analysis</label><textarea id="ncrRootCause" placeholder="Identify root cause..."></textarea></div>
        <div class="form-group">
            <label>Disposition</label>
            <div class="disposition-btns" id="dispBtns">
                <button onclick="setDisp(this,'accept')" data-val="accept">Accept As-Is</button>
                <button onclick="setDisp(this,'rework')" data-val="rework">Rework</button>
                <button onclick="setDisp(this,'reject')" data-val="reject">Reject</button>
                <button onclick="setDisp(this,'scrap')" data-val="scrap">Scrap</button>
            </div>
            <input type="hidden" id="ncrDisposition">
        </div>
        <div class="form-group"><label>Corrective Action</label><textarea id="ncrCorrectiveAction" placeholder="Describe corrective action plan..."></textarea></div>
        <div class="form-group"><label>Assigned To</label><input type="text" id="ncrAssignee" placeholder="Person responsible"></div>
        <div class="modal-actions">
            <button class="btn-outline" onclick="closeModal('ncrModal')">Cancel</button>
            <button class="btn-gold" onclick="saveNCR()">Save NCR</button>
        </div>
    </div>
</div>

<script>
let allNCRs = [];

function openModal(id) { document.getElementById(id).classList.add('active'); }
function closeModal(id) { document.getElementById(id).classList.remove('active'); }
document.querySelectorAll('.modal-overlay').forEach(m => m.addEventListener('click', function(e) { if (e.target === this) closeModal(this.id); }));

function setDisp(btn, val) {
    document.querySelectorAll('.disposition-btns button').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('ncrDisposition').value = val;
}

function openNewNCR() {
    document.getElementById('ncrModalTitle').textContent = 'New NCR';
    ['ncrId','ncrProject','ncrComponent','ncrDescription','ncrRootCause','ncrCorrectiveAction','ncrAssignee','ncrDisposition'].forEach(id => document.getElementById(id).value = '');
    document.getElementById('ncrNumber').value = 'NCR-' + Date.now().toString().slice(-6);
    document.getElementById('ncrDate').value = new Date().toISOString().slice(0,10);
    document.getElementById('ncrSeverity').value = 'medium';
    document.querySelectorAll('.disposition-btns button').forEach(b => b.classList.remove('active'));
    openModal('ncrModal');
}

function editNCR(ncr) {
    document.getElementById('ncrModalTitle').textContent = 'Edit NCR';
    document.getElementById('ncrId').value = ncr.id || '';
    document.getElementById('ncrNumber').value = ncr.ncr_number || '';
    document.getElementById('ncrDate').value = ncr.date || '';
    document.getElementById('ncrProject').value = ncr.project || '';
    document.getElementById('ncrComponent').value = ncr.component || '';
    document.getElementById('ncrSeverity').value = ncr.severity || 'medium';
    document.getElementById('ncrDescription').value = ncr.description || '';
    document.getElementById('ncrRootCause').value = ncr.root_cause || '';
    document.getElementById('ncrCorrectiveAction').value = ncr.corrective_action || '';
    document.getElementById('ncrAssignee').value = ncr.assignee || '';
    document.getElementById('ncrDisposition').value = ncr.disposition || '';
    document.querySelectorAll('.disposition-btns button').forEach(b => { b.classList.toggle('active', b.dataset.val === ncr.disposition); });
    openModal('ncrModal');
}

function getStatusBadge(ncr) {
    const s = ncr.status || 'open';
    const cls = s === 'open' ? 'badge-open' : (s === 'review' ? 'badge-review' : (s === 'rework' ? 'badge-rework' : (s === 'scrap' ? 'badge-scrap' : 'badge-closed')));
    return '<span class="badge ' + cls + '">' + s + '</span>';
}

function renderTable(ncrs) {
    const wrap = document.getElementById('ncrTableWrap');
    if (!ncrs.length) {
        wrap.innerHTML = '<div class="empty-state"><h3>No NCRs found</h3><p>Create a non-conformance report when issues are identified.</p></div>';
        return;
    }
    let html = '<table class="data-table"><thead><tr><th>NCR #</th><th>Date</th><th>Project</th><th>Component</th><th>Severity</th><th>Status</th><th>Disposition</th></tr></thead><tbody>';
    ncrs.forEach(n => {
        const sevCls = n.severity === 'high' ? 'severity-high' : (n.severity === 'medium' ? 'severity-medium' : 'severity-low');
        html += '<tr onclick=\'editNCR(' + JSON.stringify(n).replace(/'/g,"&#39;") + ')\'>' +
            '<td style="font-weight:600;">' + (n.ncr_number || '--') + '</td>' +
            '<td>' + (n.date || '--') + '</td>' +
            '<td>' + (n.project || '--') + '</td>' +
            '<td>' + (n.component || '--') + '</td>' +
            '<td><span class="' + sevCls + '">' + (n.severity || '--') + '</span></td>' +
            '<td>' + getStatusBadge(n) + '</td>' +
            '<td>' + (n.disposition || '--') + '</td></tr>';
    });
    html += '</tbody></table>';
    wrap.innerHTML = html;
}

function updateStats(ncrs) {
    document.getElementById('statOpen').textContent = ncrs.filter(n => n.status === 'open').length;
    document.getElementById('statReview').textContent = ncrs.filter(n => n.status === 'review').length;
    document.getElementById('statRework').textContent = ncrs.filter(n => n.status === 'rework').length;
    const thisMonth = new Date().toISOString().slice(0,7);
    document.getElementById('statClosed').textContent = ncrs.filter(n => n.status === 'closed' && (n.closed_date||'').startsWith(thisMonth)).length;
}

function filterNCRs() {
    const search = document.getElementById('ncrSearch').value.toLowerCase();
    const status = document.getElementById('filterStatus').value;
    const severity = document.getElementById('filterSeverity').value;
    const filtered = allNCRs.filter(n => {
        if (search && !(n.ncr_number||'').toLowerCase().includes(search) && !(n.project||'').toLowerCase().includes(search) && !(n.component||'').toLowerCase().includes(search)) return false;
        if (status && n.status !== status) return false;
        if (severity && n.severity !== severity) return false;
        return true;
    });
    renderTable(filtered);
}

function exportNCRs() {
    const rows = [['NCR#','Date','Project','Component','Severity','Status','Disposition','Description']];
    allNCRs.forEach(n => rows.push([n.ncr_number||'',n.date||'',n.project||'',n.component||'',n.severity||'',n.status||'',n.disposition||'',n.description||'']));
    const csv = rows.map(r => r.map(c => '"' + (c||'').replace(/"/g,'""') + '"').join(',')).join('\n');
    const blob = new Blob([csv], {type:'text/csv'});
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'ncr_report.csv'; a.click();
}

async function saveNCR() {
    const payload = {
        id: document.getElementById('ncrId').value || undefined,
        ncr_number: document.getElementById('ncrNumber').value,
        date: document.getElementById('ncrDate').value,
        project: document.getElementById('ncrProject').value,
        component: document.getElementById('ncrComponent').value,
        severity: document.getElementById('ncrSeverity').value,
        description: document.getElementById('ncrDescription').value,
        root_cause: document.getElementById('ncrRootCause').value,
        disposition: document.getElementById('ncrDisposition').value,
        corrective_action: document.getElementById('ncrCorrectiveAction').value,
        assignee: document.getElementById('ncrAssignee').value
    };
    if (!payload.description) { alert('Description is required'); return; }
    try {
        await fetch('/api/qc/ncr', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
        closeModal('ncrModal');
        loadNCRs();
    } catch(e) { alert('Error: ' + e.message); }
}

async function loadNCRs() {
    try {
        const resp = await fetch('/api/qc/ncr');
        const data = await resp.json();
        allNCRs = Array.isArray(data) ? data : (data.ncrs || []);
        updateStats(allNCRs);
        renderTable(allNCRs);
    } catch(e) { renderTable([]); }
}

loadNCRs();
</script>
"""
