"""
TitanForge v4 -- Material Requisitions
========================================
Create MRs, approval workflow, status tracking, link to POs, convert to PO action.
"""

MATERIAL_REQS_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a; --tf-card: #1e293b; --tf-text: #e2e8f0; --tf-muted: #94a3b8;
        --tf-gold: #d4a843; --tf-blue: #3b82f6; --tf-green: #10b981; --tf-red: #ef4444; --tf-orange: #f59e0b;
    }
    .mr-container { max-width: 1400px; margin: 0 auto; padding: 24px 32px; font-family: 'Inter', system-ui, -apple-system, sans-serif; color: var(--tf-text); }
    .page-header { margin-bottom: 28px; }
    .page-header h1 { font-size: 28px; font-weight: 800; margin: 0 0 6px 0; }
    .page-header p { font-size: 14px; color: var(--tf-muted); margin: 0; }
    .stat-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 24px; }
    .stat-card { background: var(--tf-card); border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); padding: 20px 24px; cursor: pointer; transition: border-color 0.2s, transform 0.15s; }
    .stat-card:hover { border-color: var(--tf-gold); transform: translateY(-2px); }
    .stat-card .label { font-size: 12px; color: var(--tf-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
    .stat-card .value { font-size: 28px; font-weight: 800; }
    .stat-gold .value { color: var(--tf-gold); } .stat-blue .value { color: var(--tf-blue); }
    .stat-green .value { color: var(--tf-green); } .stat-red .value { color: var(--tf-red); }
    .stat-orange .value { color: var(--tf-orange); }
    .toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
    .toolbar-left { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
    .toolbar input[type="text"], .toolbar select { background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px 16px; color: var(--tf-text); font-size: 14px; }
    .toolbar input:focus, .toolbar select:focus { outline: none; border-color: var(--tf-blue); }
    .btn { padding: 10px 20px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
    .btn-primary { background: var(--tf-gold); color: #0f172a; } .btn-primary:hover { background: #e0b44e; }
    .btn-secondary { background: var(--tf-card); color: var(--tf-text); border: 1px solid rgba(255,255,255,0.06); }
    .btn-secondary:hover { border-color: var(--tf-blue); }
    .btn-sm { padding: 6px 14px; font-size: 12px; }
    .btn-success { background: var(--tf-green); color: #fff; }
    .btn-blue { background: var(--tf-blue); color: #fff; }
    .btn-danger { background: var(--tf-red); color: #fff; }
    .data-table { width: 100%; border-collapse: collapse; background: var(--tf-card); border-radius: 12px; overflow: hidden; border: 1px solid rgba(255,255,255,0.06); }
    .data-table th { padding: 14px 16px; text-align: left; font-size: 11px; font-weight: 700; color: var(--tf-muted); text-transform: uppercase; letter-spacing: 0.5px; background: rgba(0,0,0,0.2); border-bottom: 1px solid rgba(255,255,255,0.06); }
    .data-table td { padding: 14px 16px; font-size: 14px; border-bottom: 1px solid rgba(255,255,255,0.04); }
    .data-table tbody tr { cursor: pointer; transition: background 0.15s; }
    .data-table tbody tr:hover { background: rgba(59,130,246,0.06); }
    .badge { display: inline-block; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.3px; }
    .badge-draft { background: rgba(148,163,184,0.15); color: var(--tf-muted); }
    .badge-submitted { background: rgba(245,158,11,0.15); color: var(--tf-orange); }
    .badge-pending { background: rgba(245,158,11,0.15); color: var(--tf-orange); }
    .badge-approved { background: rgba(59,130,246,0.15); color: var(--tf-blue); }
    .badge-ordered { background: rgba(16,185,129,0.15); color: var(--tf-green); }
    .badge-received { background: rgba(212,168,67,0.15); color: var(--tf-gold); }
    .badge-rejected { background: rgba(239,68,68,0.15); color: var(--tf-red); }
    /* Status Pipeline */
    .pipeline { display: flex; gap: 4px; margin: 8px 0; }
    .pipeline .step { flex: 1; height: 6px; border-radius: 3px; background: rgba(255,255,255,0.06); }
    .pipeline .step.done { background: var(--tf-green); }
    .pipeline .step.current { background: var(--tf-gold); }
    .empty-state { text-align: center; padding: 60px 20px; color: var(--tf-muted); }
    .empty-state .icon { font-size: 48px; margin-bottom: 16px; opacity: 0.5; }
    .empty-state h3 { font-size: 18px; color: var(--tf-text); margin-bottom: 8px; }
    .empty-state p { font-size: 14px; max-width: 400px; margin: 0 auto 20px; }
    .modal-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 1000; justify-content: center; align-items: center; }
    .modal-overlay.active { display: flex; }
    .modal { background: var(--tf-card); border-radius: 16px; padding: 32px; width: 90%; max-width: 700px; border: 1px solid rgba(255,255,255,0.1); max-height: 80vh; overflow-y: auto; }
    .modal h2 { font-size: 20px; font-weight: 700; margin: 0 0 24px 0; }
    .form-group { margin-bottom: 18px; }
    .form-group label { display: block; font-size: 12px; font-weight: 600; color: var(--tf-muted); text-transform: uppercase; margin-bottom: 6px; }
    .form-group input, .form-group select, .form-group textarea { width: 100%; background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px; }
    .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 24px; }
    .line-items { margin-top: 12px; }
    .line-item { display: grid; grid-template-columns: 2fr 1fr 1fr auto; gap: 10px; align-items: center; margin-bottom: 8px; }
    .line-item input { background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 8px 12px; color: var(--tf-text); font-size: 13px; }
    @media (max-width: 768px) {
        .toolbar { flex-direction: column; align-items: stretch; }
        .stat-row { grid-template-columns: 1fr 1fr; }
        table { display: block; overflow-x: auto; }
        .modal { width: 95%; max-width: 95vw; padding: 20px; }
        .form-row { grid-template-columns: 1fr; }
    }
</style>

<div class="mr-container">
    <div class="page-header">
        <h1>Material Requisitions</h1>
        <p>Create, track, and approve material requisitions for projects</p>
    </div>
    <div class="stat-row">
        <div class="stat-card stat-gold"><div class="label">Total MRs</div><div class="value" id="stat-total">0</div></div>
        <div class="stat-card stat-orange"><div class="label">Pending Approval</div><div class="value" id="stat-pending">0</div></div>
        <div class="stat-card stat-blue"><div class="label">Approved</div><div class="value" id="stat-approved">0</div></div>
        <div class="stat-card stat-green"><div class="label">Ordered</div><div class="value" id="stat-ordered">0</div></div>
        <div class="stat-card stat-gold"><div class="label">Received</div><div class="value" id="stat-received">0</div></div>
    </div>
    <div class="toolbar">
        <div class="toolbar-left">
            <input type="text" id="search-input" placeholder="Search MRs..." oninput="filterTable()">
            <select id="status-filter" onchange="filterTable()">
                <option value="">All Statuses</option>
                <option value="draft">Draft</option>
                <option value="submitted">Submitted</option>
                <option value="approved">Approved</option>
                <option value="ordered">Ordered</option>
                <option value="received">Received</option>
                <option value="rejected">Rejected</option>
            </select>
        </div>
        <button class="btn btn-primary" onclick="openCreateModal()">+ New Requisition</button>
    </div>
    <div id="table-container">
        <table class="data-table">
            <thead><tr><th>MR Number</th><th>Project</th><th>Requested By</th><th>Priority</th><th>Date</th><th>Items</th><th>Status</th><th>Linked PO</th><th>Actions</th></tr></thead>
            <tbody id="mr-tbody"></tbody>
        </table>
        <div class="empty-state" id="empty-state">
            <div class="icon">&#x1F4CB;</div>
            <h3>No Material Requisitions</h3>
            <p>Create a material requisition to request materials for a project.</p>
            <button class="btn btn-primary" onclick="openCreateModal()">+ New Requisition</button>
        </div>
    </div>
</div>

<!-- Create MR Modal -->
<div class="modal-overlay" id="mr-modal">
    <div class="modal">
        <h2>New Material Requisition</h2>
        <div class="form-row">
            <div class="form-group"><label>Project</label><input type="text" id="mr-project" placeholder="Job code or project name"></div>
            <div class="form-group"><label>Priority</label><select id="mr-priority"><option value="normal">Normal</option><option value="high">High</option><option value="urgent">Urgent</option></select></div>
        </div>
        <div class="form-row">
            <div class="form-group"><label>Required By Date</label><input type="date" id="mr-date"></div>
            <div class="form-group"><label>Requested By</label><input type="text" id="mr-requestor" placeholder="Your name"></div>
        </div>
        <div class="form-group">
            <label>Line Items</label>
            <div class="line-items" id="line-items">
                <div class="line-item">
                    <input type="text" placeholder="Material description">
                    <input type="number" placeholder="Qty">
                    <input type="text" placeholder="Unit (lbs, ft, ea)">
                    <button class="btn btn-sm btn-secondary" onclick="addLineItem()">+</button>
                </div>
            </div>
        </div>
        <div class="form-group"><label>Justification / Notes</label><textarea id="mr-notes" rows="3" placeholder="Why is this material needed?"></textarea></div>
        <div class="modal-actions">
            <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
            <button class="btn btn-primary" onclick="saveMR()">Submit Requisition</button>
        </div>
    </div>
</div>

<!-- Detail/Action Modal -->
<div class="modal-overlay" id="detail-modal">
    <div class="modal">
        <h2 id="detail-title">MR Details</h2>
        <div id="detail-content"></div>
        <div class="modal-actions" id="detail-actions"></div>
    </div>
</div>

<script>
let requisitions = [];

async function loadMRs() {
    try {
        const resp = await fetch('/api/material-reqs');
        const data = await resp.json();
        requisitions = data.requisitions || [];
        renderTable(); updateStats();
    } catch(e) { console.error('Failed to load MRs:', e); renderTable(); }
}

function updateStats() {
    document.getElementById('stat-total').textContent = requisitions.length;
    document.getElementById('stat-pending').textContent = requisitions.filter(r => r.status === 'submitted' || r.status === 'pending').length;
    document.getElementById('stat-approved').textContent = requisitions.filter(r => r.status === 'approved').length;
    document.getElementById('stat-ordered').textContent = requisitions.filter(r => r.status === 'ordered').length;
    document.getElementById('stat-received').textContent = requisitions.filter(r => r.status === 'received').length;
}

function statusPipeline(status) {
    const steps = ['draft','submitted','approved','ordered','received'];
    const idx = steps.indexOf(status);
    return '<div class="pipeline">' + steps.map((s, i) =>
        '<div class="step ' + (i < idx ? 'done' : i === idx ? 'current' : '') + '" title="' + s + '"></div>'
    ).join('') + '</div>';
}

function renderTable() {
    const tbody = document.getElementById('mr-tbody');
    const empty = document.getElementById('empty-state');
    const filtered = getFiltered();
    if (filtered.length === 0) { tbody.innerHTML = ''; empty.style.display = 'block'; return; }
    empty.style.display = 'none';
    const prioColors = {urgent: 'var(--tf-red)', high: 'var(--tf-orange)', normal: 'var(--tf-muted)'};
    tbody.innerHTML = filtered.map(r => `
        <tr onclick="viewMR('${r.id || r.mr_number}')">
            <td><strong>${r.mr_number || r.id || '--'}</strong>${statusPipeline(r.status)}</td>
            <td>${r.project || '--'}</td>
            <td>${r.requested_by || '--'}</td>
            <td><span style="color:${prioColors[r.priority]||'var(--tf-muted)'};font-weight:600;text-transform:uppercase;font-size:11px">${r.priority || 'normal'}</span></td>
            <td>${(r.date || r.created_at || '--').substring(0,10)}</td>
            <td>${r.item_count || (r.items||[]).length || 0}</td>
            <td><span class="badge badge-${r.status || 'draft'}">${r.status || 'draft'}</span></td>
            <td>${r.linked_po ? '<a href="/pos" style="color:var(--tf-blue)">' + r.linked_po + '</a>' : '--'}</td>
            <td>
                ${r.status === 'submitted' ? '<button class="btn btn-sm btn-success" onclick="event.stopPropagation();updateStatus(\'' + (r.id||r.mr_number) + '\',\'approved\')">Approve</button>' : ''}
                ${r.status === 'approved' ? '<button class="btn btn-sm btn-blue" onclick="event.stopPropagation();convertToPO(\'' + (r.id||r.mr_number) + '\')">Convert to PO</button>' : ''}
            </td>
        </tr>
    `).join('');
}

function getFiltered() {
    const search = (document.getElementById('search-input').value || '').toLowerCase();
    const status = document.getElementById('status-filter').value;
    return requisitions.filter(r => {
        if (search && !JSON.stringify(r).toLowerCase().includes(search)) return false;
        if (status && r.status !== status) return false;
        return true;
    });
}

function filterTable() { renderTable(); }
function openCreateModal() { document.getElementById('mr-modal').classList.add('active'); }
function closeModal() { document.querySelectorAll('.modal-overlay').forEach(m => m.classList.remove('active')); }

function viewMR(id) {
    const mr = requisitions.find(r => r.id === id || r.mr_number === id);
    if (!mr) return;
    const content = document.getElementById('detail-content');
    let html = '<div style="margin-bottom:16px"><strong>MR:</strong> ' + (mr.mr_number || mr.id) + ' | <strong>Status:</strong> <span class="badge badge-' + mr.status + '">' + mr.status + '</span></div>';
    html += '<div style="margin-bottom:8px"><strong>Project:</strong> ' + (mr.project || '--') + ' | <strong>Priority:</strong> ' + (mr.priority || 'normal') + '</div>';
    html += '<div style="margin-bottom:8px"><strong>Requested By:</strong> ' + (mr.requested_by || '--') + ' | <strong>Date:</strong> ' + (mr.date || '--') + '</div>';
    if (mr.justification) html += '<div style="margin-bottom:12px"><strong>Justification:</strong> ' + mr.justification + '</div>';
    if (mr.items && mr.items.length) {
        html += '<table class="data-table" style="margin-top:12px"><thead><tr><th>Description</th><th>Qty</th><th>Unit</th></tr></thead><tbody>';
        mr.items.forEach(it => { html += '<tr><td>' + (it.description||'--') + '</td><td>' + (it.qty||0) + '</td><td>' + (it.unit||'ea') + '</td></tr>'; });
        html += '</tbody></table>';
    }
    if (mr.linked_po) html += '<div style="margin-top:12px"><strong>Linked PO:</strong> <a href="/pos" style="color:var(--tf-blue)">' + mr.linked_po + '</a></div>';
    content.innerHTML = html;
    let actions = '<button class="btn btn-secondary" onclick="closeModal()">Close</button>';
    if (mr.status === 'draft') actions += ' <button class="btn btn-primary" onclick="updateStatus(\'' + id + '\',\'submitted\');closeModal()">Submit</button>';
    if (mr.status === 'submitted') {
        actions += ' <button class="btn btn-success" onclick="updateStatus(\'' + id + '\',\'approved\');closeModal()">Approve</button>';
        actions += ' <button class="btn btn-danger" onclick="updateStatus(\'' + id + '\',\'rejected\');closeModal()">Reject</button>';
    }
    if (mr.status === 'approved') actions += ' <button class="btn btn-blue" onclick="convertToPO(\'' + id + '\');closeModal()">Convert to PO</button>';
    document.getElementById('detail-actions').innerHTML = actions;
    document.getElementById('detail-title').textContent = 'MR: ' + (mr.mr_number || mr.id);
    document.getElementById('detail-modal').classList.add('active');
}

async function updateStatus(id, status) {
    try {
        await fetch('/api/material-reqs', { method: 'POST', headers: {'Content-Type':'application/json'},
            body: JSON.stringify({action: 'update_status', id: id, status: status}) });
        loadMRs();
    } catch(e) { alert('Error: ' + e.message); }
}

async function convertToPO(mrId) {
    try {
        const resp = await fetch('/api/pos', { method: 'POST', headers: {'Content-Type':'application/json'},
            body: JSON.stringify({action: 'create_from_mr', mr_id: mrId}) });
        const data = await resp.json();
        if (data.ok) {
            alert('PO ' + data.po_number + ' created from MR ' + mrId);
            loadMRs();
        } else { alert('Error: ' + (data.error || 'Failed')); }
    } catch(e) { alert('Error: ' + e.message); }
}

function addLineItem() {
    const container = document.getElementById('line-items');
    const div = document.createElement('div');
    div.className = 'line-item';
    div.innerHTML = '<input type="text" placeholder="Material description"><input type="number" placeholder="Qty"><input type="text" placeholder="Unit (lbs, ft, ea)"><button class="btn btn-sm btn-secondary" onclick="this.parentElement.remove()">x</button>';
    container.appendChild(div);
}

async function saveMR() {
    const lineEls = document.querySelectorAll('#line-items .line-item');
    const items = [];
    lineEls.forEach(el => {
        const inputs = el.querySelectorAll('input');
        const desc = inputs[0]?.value || '';
        const qty = parseFloat(inputs[1]?.value) || 0;
        const unit = inputs[2]?.value || 'ea';
        if (desc) items.push({description: desc, qty: qty, unit: unit});
    });
    const payload = {
        project: document.getElementById('mr-project').value,
        priority: document.getElementById('mr-priority').value,
        required_date: document.getElementById('mr-date').value,
        requested_by: document.getElementById('mr-requestor').value,
        justification: document.getElementById('mr-notes').value,
        items: items,
        status: 'draft',
    };
    try {
        await fetch('/api/material-reqs', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
        closeModal(); loadMRs();
    } catch(e) { console.error('Save failed:', e); }
}

document.addEventListener('DOMContentLoaded', loadMRs);
</script>
"""
