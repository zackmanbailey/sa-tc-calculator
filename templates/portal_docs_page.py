"""
TitanForge v4 — Customer Portal Documents
============================================
Shared drawings, specs, approvals, RFI responses, change orders, document status.
"""

PORTAL_DOCS_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a;
        --tf-card: #1e293b;
        --tf-text: #e2e8f0;
        --tf-muted: #94a3b8;
        --tf-gold: #d4a843;
        --tf-blue: #3b82f6;
    }
    .portal-container {
        max-width: 1400px; margin: 0 auto; padding: 24px 32px;
        font-family: 'Inter', 'Segoe UI', sans-serif; color: var(--tf-text);
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
    .badge-approved { background: rgba(34,197,94,0.2); color: #4ade80; }
    .badge-pending { background: rgba(212,168,67,0.2); color: var(--tf-gold); }
    .badge-rejected { background: rgba(239,68,68,0.2); color: #f87171; }
    .badge-shared { background: rgba(59,130,246,0.2); color: #60a5fa; }
    .doc-icon { font-size: 20px; margin-right: 8px; vertical-align: middle; }
    .empty-state { text-align: center; padding: 60px 20px; color: var(--tf-muted); }
    .empty-state h3 { font-size: 18px; margin-bottom: 8px; color: var(--tf-text); }
    .loading { text-align: center; padding: 40px; color: var(--tf-muted); }
    .modal-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 1000; justify-content: center; align-items: center; }
    .modal-overlay.active { display: flex; }
    .modal { background: var(--tf-card); border-radius: 12px; padding: 28px; width: 560px; max-width: 90vw; border: 1px solid rgba(255,255,255,0.1); }
    .modal h2 { font-size: 20px; margin: 0 0 20px 0; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 24px; }
    .form-group { margin-bottom: 16px; }
    .form-group label { display: block; font-size: 13px; font-weight: 600; color: var(--tf-muted); margin-bottom: 6px; }
    .form-group input, .form-group select, .form-group textarea {
        width: 100%; background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px; font-family: inherit; box-sizing: border-box;
    }
</style>

<div class="portal-container">
    <div class="page-header">
        <h1>Portal Documents</h1>
        <p>Manage documents shared with customers: drawings, specs, approvals, and RFI responses</p>
    </div>
    <div class="stats-row">
        <div class="stat-card"><div class="stat-label">Total Documents</div><div class="stat-value" id="statTotal" style="color:var(--tf-text);">--</div></div>
        <div class="stat-card"><div class="stat-label">Pending Approval</div><div class="stat-value" id="statPending" style="color:var(--tf-gold);">--</div></div>
        <div class="stat-card"><div class="stat-label">Approved</div><div class="stat-value" id="statApproved" style="color:#4ade80;">--</div></div>
        <div class="stat-card"><div class="stat-label">Open RFIs</div><div class="stat-value" id="statRFI" style="color:var(--tf-blue);">--</div></div>
    </div>
    <div class="toolbar">
        <div style="display:flex;gap:10px;align-items:center;">
            <input type="text" id="docSearch" placeholder="Search documents..." oninput="filterDocs()">
            <select id="filterType" onchange="filterDocs()">
                <option value="">All Types</option>
                <option value="drawing">Drawings</option>
                <option value="spec">Specifications</option>
                <option value="rfi">RFI</option>
                <option value="change_order">Change Orders</option>
                <option value="approval">Approvals</option>
            </select>
            <select id="filterStatus" onchange="filterDocs()">
                <option value="">All Status</option>
                <option value="approved">Approved</option>
                <option value="pending">Pending</option>
                <option value="rejected">Rejected</option>
            </select>
        </div>
        <button class="btn-gold" onclick="openModal('uploadModal')">+ Upload Document</button>
    </div>
    <div class="data-card">
        <div id="docTableWrap" class="loading">Loading documents...</div>
    </div>
</div>

<div class="modal-overlay" id="uploadModal">
    <div class="modal">
        <h2>Upload Document</h2>
        <div class="form-group"><label>Document Name</label><input type="text" id="docName" placeholder="e.g. Shop Drawing Rev B"></div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div class="form-group"><label>Type</label><select id="docType"><option value="drawing">Drawing</option><option value="spec">Specification</option><option value="rfi">RFI</option><option value="change_order">Change Order</option><option value="approval">Approval</option></select></div>
            <div class="form-group"><label>Project</label><input type="text" id="docProject" placeholder="Job code"></div>
        </div>
        <div class="form-group"><label>File</label><input type="file" id="docFile" style="padding:8px;"></div>
        <div class="form-group"><label>Notes</label><textarea id="docNotes" placeholder="Additional notes..." style="min-height:60px;resize:vertical;"></textarea></div>
        <div class="form-group">
            <label><input type="checkbox" id="docShareWithCustomer" checked style="width:auto;margin-right:8px;">Share with customer immediately</label>
        </div>
        <div class="modal-actions">
            <button class="btn-outline" onclick="closeModal('uploadModal')">Cancel</button>
            <button class="btn-gold" onclick="uploadDoc()">Upload</button>
        </div>
    </div>
</div>

<script>
let allDocs = [];

function openModal(id) { document.getElementById(id).classList.add('active'); }
function closeModal(id) { document.getElementById(id).classList.remove('active'); }
document.querySelectorAll('.modal-overlay').forEach(m => m.addEventListener('click', function(e) { if (e.target === this) closeModal(this.id); }));

function getTypeIcon(type) {
    const icons = { drawing: '\ud83d\udcc0', spec: '\ud83d\udccb', rfi: '\u2753', change_order: '\ud83d\udd04', approval: '\u2705' };
    return icons[type] || '\ud83d\udcc4';
}

function getStatusBadge(status) {
    const cls = status === 'approved' ? 'badge-approved' : (status === 'pending' ? 'badge-pending' : (status === 'rejected' ? 'badge-rejected' : 'badge-shared'));
    return '<span class="badge ' + cls + '">' + (status || 'shared') + '</span>';
}

function renderTable(docs) {
    const wrap = document.getElementById('docTableWrap');
    if (!docs.length) {
        wrap.innerHTML = '<div class="empty-state"><h3>No documents found</h3><p>Upload documents to share with customers.</p></div>';
        return;
    }
    let html = '<table class="data-table"><thead><tr><th>Document</th><th>Type</th><th>Project</th><th>Uploaded</th><th>Status</th><th>Shared</th></tr></thead><tbody>';
    docs.forEach(d => {
        html += '<tr onclick="viewDoc(\'' + (d.id||'') + '\')">' +
            '<td><span class="doc-icon">' + getTypeIcon(d.type) + '</span>' + (d.name || 'Untitled') + '</td>' +
            '<td>' + (d.type || '--') + '</td>' +
            '<td>' + (d.project || '--') + '</td>' +
            '<td>' + (d.uploaded_date || '--') + '</td>' +
            '<td>' + getStatusBadge(d.status) + '</td>' +
            '<td>' + (d.shared ? '<span style="color:#4ade80;">Yes</span>' : '<span style="color:var(--tf-muted);">No</span>') + '</td></tr>';
    });
    html += '</tbody></table>';
    wrap.innerHTML = html;
}

function updateStats(docs) {
    document.getElementById('statTotal').textContent = docs.length;
    document.getElementById('statPending').textContent = docs.filter(d => d.status === 'pending').length;
    document.getElementById('statApproved').textContent = docs.filter(d => d.status === 'approved').length;
    document.getElementById('statRFI').textContent = docs.filter(d => d.type === 'rfi' && d.status !== 'approved').length;
}

function filterDocs() {
    const search = document.getElementById('docSearch').value.toLowerCase();
    const type = document.getElementById('filterType').value;
    const status = document.getElementById('filterStatus').value;
    const filtered = allDocs.filter(d => {
        if (search && !(d.name||'').toLowerCase().includes(search) && !(d.project||'').toLowerCase().includes(search)) return false;
        if (type && d.type !== type) return false;
        if (status && d.status !== status) return false;
        return true;
    });
    renderTable(filtered);
}

function viewDoc(id) { window.location.href = '/portal/docs/' + id; }

async function uploadDoc() {
    const payload = {
        name: document.getElementById('docName').value,
        type: document.getElementById('docType').value,
        project: document.getElementById('docProject').value,
        notes: document.getElementById('docNotes').value,
        shared: document.getElementById('docShareWithCustomer').checked,
        status: 'pending',
        uploaded_date: new Date().toISOString().slice(0,10)
    };
    if (!payload.name) { alert('Document name is required'); return; }
    try {
        await fetch('/api/portal/docs', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
        closeModal('uploadModal');
        loadDocs();
    } catch(e) { alert('Error: ' + e.message); }
}

async function loadDocs() {
    try {
        const resp = await fetch('/api/portal/docs');
        const data = await resp.json();
        allDocs = Array.isArray(data) ? data : (data.documents || []);
        updateStats(allDocs);
        renderTable(allDocs);
    } catch(e) { renderTable([]); }
}

loadDocs();
</script>
"""
