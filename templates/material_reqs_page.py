"""
TitanForge v4 -- Material Requisitions
========================================
Create MRs, approval workflow, status tracking (pending/approved/ordered/received), link to POs.
"""

MATERIAL_REQS_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a;
        --tf-card: #1e293b;
        --tf-text: #e2e8f0;
        --tf-muted: #94a3b8;
        --tf-gold: #d4a843;
        --tf-blue: #3b82f6;
        --tf-green: #10b981;
        --tf-red: #ef4444;
        --tf-orange: #f59e0b;
    }
    .mr-container {
        max-width: 1400px; margin: 0 auto; padding: 24px 32px;
        font-family: 'Inter', 'Segoe UI', sans-serif; color: var(--tf-text);
    }
    .page-header { margin-bottom: 28px; }
    .page-header h1 { font-size: 28px; font-weight: 800; margin: 0 0 6px 0; }
    .page-header p { font-size: 14px; color: var(--tf-muted); margin: 0; }

    .stat-row {
        display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 16px; margin-bottom: 24px;
    }
    .stat-card {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06);
        padding: 20px 24px; cursor: pointer; transition: border-color 0.2s, transform 0.15s;
    }
    .stat-card:hover { border-color: var(--tf-gold); transform: translateY(-2px); }
    .stat-card .label { font-size: 12px; color: var(--tf-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
    .stat-card .value { font-size: 28px; font-weight: 800; }
    .stat-gold .value { color: var(--tf-gold); }
    .stat-blue .value { color: var(--tf-blue); }
    .stat-green .value { color: var(--tf-green); }
    .stat-red .value { color: var(--tf-red); }
    .stat-orange .value { color: var(--tf-orange); }

    .toolbar {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 20px; flex-wrap: wrap; gap: 12px;
    }
    .toolbar-left { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
    .toolbar input[type="text"], .toolbar select {
        background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06);
        border-radius: 8px; padding: 10px 16px; color: var(--tf-text); font-size: 14px;
    }
    .toolbar input:focus, .toolbar select:focus { outline: none; border-color: var(--tf-blue); }
    .btn {
        padding: 10px 20px; border: none; border-radius: 8px; font-size: 14px;
        font-weight: 600; cursor: pointer; transition: all 0.2s;
    }
    .btn-primary { background: var(--tf-gold); color: #0f172a; }
    .btn-primary:hover { background: #e0b44e; transform: translateY(-1px); }
    .btn-secondary { background: var(--tf-card); color: var(--tf-text); border: 1px solid rgba(255,255,255,0.06); }
    .btn-secondary:hover { border-color: var(--tf-blue); }
    .btn-sm { padding: 6px 14px; font-size: 12px; }
    .btn-success { background: var(--tf-green); color: #fff; }

    .data-table {
        width: 100%; border-collapse: collapse; background: var(--tf-card);
        border-radius: 12px; overflow: hidden; border: 1px solid rgba(255,255,255,0.06);
    }
    .data-table th {
        padding: 14px 16px; text-align: left; font-size: 11px; font-weight: 700;
        color: var(--tf-muted); text-transform: uppercase; letter-spacing: 0.5px;
        background: rgba(0,0,0,0.2); border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .data-table td {
        padding: 14px 16px; font-size: 14px; border-bottom: 1px solid rgba(255,255,255,0.04);
    }
    .data-table tbody tr { cursor: pointer; transition: background 0.15s; }
    .data-table tbody tr:hover { background: rgba(59,130,246,0.06); }

    .badge {
        display: inline-block; padding: 4px 10px; border-radius: 6px;
        font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.3px;
    }
    .badge-pending { background: rgba(245,158,11,0.15); color: var(--tf-orange); }
    .badge-approved { background: rgba(59,130,246,0.15); color: var(--tf-blue); }
    .badge-ordered { background: rgba(16,185,129,0.15); color: var(--tf-green); }
    .badge-received { background: rgba(212,168,67,0.15); color: var(--tf-gold); }
    .badge-rejected { background: rgba(239,68,68,0.15); color: var(--tf-red); }

    .empty-state {
        text-align: center; padding: 60px 20px; color: var(--tf-muted);
    }
    .empty-state .icon { font-size: 48px; margin-bottom: 16px; opacity: 0.5; }
    .empty-state h3 { font-size: 18px; color: var(--tf-text); margin-bottom: 8px; }
    .empty-state p { font-size: 14px; max-width: 400px; margin: 0 auto 20px; }

    .modal-overlay {
        display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6);
        z-index: 1000; justify-content: center; align-items: center;
    }
    .modal-overlay.active { display: flex; }
    .modal {
        background: var(--tf-card); border-radius: 16px; padding: 32px;
        width: 90%; max-width: 700px; border: 1px solid rgba(255,255,255,0.1);
        max-height: 80vh; overflow-y: auto;
    }
    .modal h2 { font-size: 20px; font-weight: 700; margin: 0 0 24px 0; }
    .form-group { margin-bottom: 18px; }
    .form-group label { display: block; font-size: 12px; font-weight: 600; color: var(--tf-muted); text-transform: uppercase; margin-bottom: 6px; }
    .form-group input, .form-group select, .form-group textarea {
        width: 100%; background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px;
    }
    .form-group input:focus, .form-group select:focus { outline: none; border-color: var(--tf-blue); }
    .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .form-row-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 24px; }

    .line-items { margin-top: 12px; }
    .line-item {
        display: grid; grid-template-columns: 2fr 1fr 1fr auto; gap: 10px; align-items: center; margin-bottom: 8px;
    }
    .line-item input { background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 8px 12px; color: var(--tf-text); font-size: 13px; }
</style>

<div class="mr-container">
    <div class="page-header">
        <h1>Material Requisitions</h1>
        <p>Create, track, and approve material requisitions for projects</p>
    </div>

    <div class="stat-row">
        <div class="stat-card stat-gold">
            <div class="label">Total MRs</div>
            <div class="value" id="stat-total">0</div>
        </div>
        <div class="stat-card stat-orange">
            <div class="label">Pending Approval</div>
            <div class="value" id="stat-pending">0</div>
        </div>
        <div class="stat-card stat-blue">
            <div class="label">Approved</div>
            <div class="value" id="stat-approved">0</div>
        </div>
        <div class="stat-card stat-green">
            <div class="label">Ordered</div>
            <div class="value" id="stat-ordered">0</div>
        </div>
        <div class="stat-card stat-gold">
            <div class="label">Received</div>
            <div class="value" id="stat-received">0</div>
        </div>
    </div>

    <div class="toolbar">
        <div class="toolbar-left">
            <input type="text" id="search-input" placeholder="Search MRs..." oninput="filterTable()">
            <select id="status-filter" onchange="filterTable()">
                <option value="">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="ordered">Ordered</option>
                <option value="received">Received</option>
                <option value="rejected">Rejected</option>
            </select>
            <select id="project-filter" onchange="filterTable()">
                <option value="">All Projects</option>
            </select>
        </div>
        <button class="btn btn-primary" onclick="openModal()">+ New Requisition</button>
    </div>

    <div id="table-container">
        <table class="data-table">
            <thead>
                <tr>
                    <th>MR Number</th>
                    <th>Project</th>
                    <th>Requested By</th>
                    <th>Date</th>
                    <th>Items</th>
                    <th>Est. Cost</th>
                    <th>Status</th>
                    <th>Linked PO</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody id="mr-tbody"></tbody>
        </table>
        <div class="empty-state" id="empty-state">
            <div class="icon">&#x1F4CB;</div>
            <h3>No Material Requisitions</h3>
            <p>Create a material requisition to request materials for a project.</p>
            <button class="btn btn-primary" onclick="openModal()">+ New Requisition</button>
        </div>
    </div>
</div>

<!-- MR Modal -->
<div class="modal-overlay" id="mr-modal">
    <div class="modal">
        <h2 id="modal-title">New Material Requisition</h2>
        <div class="form-row">
            <div class="form-group">
                <label>Project</label>
                <select id="mr-project">
                    <option value="">Select project...</option>
                </select>
            </div>
            <div class="form-group">
                <label>Priority</label>
                <select id="mr-priority">
                    <option value="normal">Normal</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                </select>
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Required By Date</label>
                <input type="date" id="mr-date">
            </div>
            <div class="form-group">
                <label>Requested By</label>
                <input type="text" id="mr-requestor" placeholder="Your name">
            </div>
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
        <div class="form-group">
            <label>Justification / Notes</label>
            <textarea id="mr-notes" rows="3" placeholder="Why is this material needed?"></textarea>
        </div>
        <div class="modal-actions">
            <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
            <button class="btn btn-primary" onclick="saveMR()">Submit Requisition</button>
        </div>
    </div>
</div>

<script>
let requisitions = [];

async function loadMRs() {
    try {
        const resp = await fetch('/api/material-reqs');
        const data = await resp.json();
        requisitions = data.requisitions || [];
        renderTable();
        updateStats();
    } catch(e) { console.error('Failed to load MRs:', e); renderTable(); }
}

function updateStats() {
    document.getElementById('stat-total').textContent = requisitions.length;
    document.getElementById('stat-pending').textContent = requisitions.filter(r => r.status === 'pending').length;
    document.getElementById('stat-approved').textContent = requisitions.filter(r => r.status === 'approved').length;
    document.getElementById('stat-ordered').textContent = requisitions.filter(r => r.status === 'ordered').length;
    document.getElementById('stat-received').textContent = requisitions.filter(r => r.status === 'received').length;
}

function renderTable() {
    const tbody = document.getElementById('mr-tbody');
    const empty = document.getElementById('empty-state');
    const filtered = getFiltered();
    if (filtered.length === 0) { tbody.innerHTML = ''; empty.style.display = 'block'; return; }
    empty.style.display = 'none';
    tbody.innerHTML = filtered.map(r => `
        <tr>
            <td><strong>${r.mr_number || '--'}</strong></td>
            <td>${r.project || '--'}</td>
            <td>${r.requested_by || '--'}</td>
            <td>${r.date || '--'}</td>
            <td>${r.item_count || 0}</td>
            <td>$${(r.est_cost || 0).toLocaleString()}</td>
            <td><span class="badge badge-${r.status || 'pending'}">${r.status || 'pending'}</span></td>
            <td>${r.linked_po || '--'}</td>
            <td>
                <button class="btn btn-sm btn-secondary" onclick="viewMR('${r.id}')">View</button>
            </td>
        </tr>
    `).join('');
}

function getFiltered() {
    const search = (document.getElementById('search-input').value || '').toLowerCase();
    const status = document.getElementById('status-filter').value;
    const project = document.getElementById('project-filter').value;
    return requisitions.filter(r => {
        if (search && !JSON.stringify(r).toLowerCase().includes(search)) return false;
        if (status && r.status !== status) return false;
        if (project && r.project !== project) return false;
        return true;
    });
}

function filterTable() { renderTable(); }
function openModal() { document.getElementById('mr-modal').classList.add('active'); }
function closeModal() { document.getElementById('mr-modal').classList.remove('active'); }
function viewMR(id) { openModal(); }

function addLineItem() {
    const container = document.getElementById('line-items');
    const div = document.createElement('div');
    div.className = 'line-item';
    div.innerHTML = '<input type="text" placeholder="Material description"><input type="number" placeholder="Qty"><input type="text" placeholder="Unit (lbs, ft, ea)"><button class="btn btn-sm btn-secondary" onclick="this.parentElement.remove()">x</button>';
    container.appendChild(div);
}

async function saveMR() {
    const payload = {
        project: document.getElementById('mr-project').value,
        priority: document.getElementById('mr-priority').value,
        required_date: document.getElementById('mr-date').value,
        requested_by: document.getElementById('mr-requestor').value,
        notes: document.getElementById('mr-notes').value,
    };
    try {
        await fetch('/api/material-reqs', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
        closeModal();
        loadMRs();
    } catch(e) { console.error('Save failed:', e); }
}

document.addEventListener('DOMContentLoaded', loadMRs);
</script>
"""
