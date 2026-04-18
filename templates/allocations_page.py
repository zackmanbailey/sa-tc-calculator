"""
TitanForge v4 -- Material Allocations
=======================================
Allocate coils/material to projects, allocation status, reserved vs available, project breakdown.
"""

ALLOCATIONS_PAGE_HTML = r"""
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
    .alloc-container {
        max-width: 1400px; margin: 0 auto; padding: 24px 32px;
        font-family: 'Inter', 'Segoe UI', sans-serif; color: var(--tf-text);
    }
    .page-header { margin-bottom: 28px; }
    .page-header h1 { font-size: 28px; font-weight: 800; margin: 0 0 6px 0; }
    .page-header p { font-size: 14px; color: var(--tf-muted); margin: 0; }

    .stat-row {
        display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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
    .badge-reserved { background: rgba(59,130,246,0.15); color: var(--tf-blue); }
    .badge-allocated { background: rgba(16,185,129,0.15); color: var(--tf-green); }
    .badge-pending { background: rgba(245,158,11,0.15); color: var(--tf-orange); }
    .badge-released { background: rgba(148,163,184,0.15); color: var(--tf-muted); }

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
        width: 90%; max-width: 600px; border: 1px solid rgba(255,255,255,0.1);
        max-height: 80vh; overflow-y: auto;
    }
    .modal h2 { font-size: 20px; font-weight: 700; margin: 0 0 24px 0; }
    .form-group { margin-bottom: 18px; }
    .form-group label { display: block; font-size: 12px; font-weight: 600; color: var(--tf-muted); text-transform: uppercase; margin-bottom: 6px; }
    .form-group input, .form-group select, .form-group textarea {
        width: 100%; background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px;
    }
    .form-group input:focus, .form-group select:focus, .form-group textarea:focus { outline: none; border-color: var(--tf-blue); }
    .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 24px; }

    .progress-bar { height: 8px; border-radius: 4px; background: rgba(255,255,255,0.06); overflow: hidden; }
    .progress-bar .fill { height: 100%; border-radius: 4px; transition: width 0.3s; }

/* ── Responsive ── */
@media (max-width: 768px) {
    .page-header h1 { font-size: 22px; }
    .toolbar { flex-direction: column; align-items: stretch; }
    .toolbar input[type="text"] { width: 100%; }
    .stat-row { grid-template-columns: 1fr 1fr; gap: 10px; }
    table { display: block; overflow-x: auto; -webkit-overflow-scrolling: touch; }
    .modal-overlay .modal, .modal { width: 95%; max-width: 95vw; margin: 20px auto; padding: 20px; }
    .form-row { grid-template-columns: 1fr; }
}
@media (max-width: 480px) {
    .stat-row { grid-template-columns: 1fr; }
    .toolbar { gap: 8px; }
}
</style>

<div class="alloc-container">
    <div class="page-header">
        <h1>Material Allocations</h1>
        <p>Allocate coils and materials to projects -- track reserved vs available inventory</p>
    </div>

    <div class="stat-row">
        <div class="stat-card stat-gold">
            <div class="label">Total Allocations</div>
            <div class="value" id="stat-total">0</div>
        </div>
        <div class="stat-card stat-blue">
            <div class="label">Reserved</div>
            <div class="value" id="stat-reserved">0</div>
        </div>
        <div class="stat-card stat-green">
            <div class="label">Fulfilled</div>
            <div class="value" id="stat-fulfilled">0</div>
        </div>
        <div class="stat-card stat-red">
            <div class="label">Shortages</div>
            <div class="value" id="stat-shortages">0</div>
        </div>
    </div>

    <div class="toolbar">
        <div class="toolbar-left">
            <input type="text" id="search-input" placeholder="Search allocations..." oninput="filterTable()">
            <select id="status-filter" onchange="filterTable()">
                <option value="">All Statuses</option>
                <option value="reserved">Reserved</option>
                <option value="allocated">Allocated</option>
                <option value="pending">Pending</option>
                <option value="released">Released</option>
            </select>
            <select id="project-filter" onchange="filterTable()">
                <option value="">All Projects</option>
            </select>
        </div>
        <button class="btn btn-primary" onclick="openModal()">+ New Allocation</button>
    </div>

    <div id="table-container">
        <table class="data-table">
            <thead>
                <tr>
                    <th>Allocation ID</th>
                    <th>Material</th>
                    <th>Coil / Stock</th>
                    <th>Project</th>
                    <th>Qty Reserved</th>
                    <th>Qty Available</th>
                    <th>Status</th>
                    <th>Allocated By</th>
                    <th>Date</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody id="alloc-tbody"></tbody>
        </table>
        <div class="empty-state" id="empty-state">
            <div class="icon">&#x1F4E6;</div>
            <h3>No Allocations Yet</h3>
            <p>Create your first material allocation to reserve inventory for a project.</p>
            <button class="btn btn-primary" onclick="openModal()">+ New Allocation</button>
        </div>
    </div>
</div>

<!-- Allocation Modal -->
<div class="modal-overlay" id="alloc-modal">
    <div class="modal">
        <h2 id="modal-title">New Material Allocation</h2>
        <div class="form-row">
            <div class="form-group">
                <label>Material Type</label>
                <select id="alloc-material">
                    <option value="">Select material...</option>
                    <option value="coil-29ga">29ga Coil</option>
                    <option value="coil-26ga">26ga Coil</option>
                    <option value="coil-24ga">24ga Coil</option>
                    <option value="tube-steel">Tube Steel</option>
                    <option value="angle-iron">Angle Iron</option>
                    <option value="purlin">Purlin (Z/C)</option>
                </select>
            </div>
            <div class="form-group">
                <label>Coil / Stock ID</label>
                <input type="text" id="alloc-stock" placeholder="e.g., COIL-2026-0042">
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Project</label>
                <select id="alloc-project">
                    <option value="">Select project...</option>
                </select>
            </div>
            <div class="form-group">
                <label>Quantity to Reserve</label>
                <input type="number" id="alloc-qty" placeholder="Enter quantity (lbs or ft)">
            </div>
        </div>
        <div class="form-group">
            <label>Priority</label>
            <select id="alloc-priority">
                <option value="normal">Normal</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
            </select>
        </div>
        <div class="form-group">
            <label>Notes</label>
            <textarea id="alloc-notes" rows="3" placeholder="Allocation notes..."></textarea>
        </div>
        <div class="modal-actions">
            <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
            <button class="btn btn-primary" onclick="saveAllocation()">Save Allocation</button>
        </div>
    </div>
</div>

<script>
let allocations = [];

async function loadAllocations() {
    try {
        const resp = await fetch('/api/allocations');
        const data = await resp.json();
        allocations = data.allocations || [];
        renderTable();
        updateStats();
    } catch(e) {
        console.error('Failed to load allocations:', e);
        renderTable();
    }
}

function updateStats() {
    document.getElementById('stat-total').textContent = allocations.length;
    document.getElementById('stat-reserved').textContent = allocations.filter(a => a.status === 'reserved').length;
    document.getElementById('stat-fulfilled').textContent = allocations.filter(a => a.status === 'allocated').length;
    document.getElementById('stat-shortages').textContent = allocations.filter(a => a.status === 'pending').length;
}

function renderTable() {
    const tbody = document.getElementById('alloc-tbody');
    const empty = document.getElementById('empty-state');
    const filtered = getFiltered();

    if (filtered.length === 0) {
        tbody.innerHTML = '';
        empty.style.display = 'block';
        return;
    }
    empty.style.display = 'none';
    tbody.innerHTML = filtered.map(a => `
        <tr>
            <td><strong>${a.id || '--'}</strong></td>
            <td>${a.material || '--'}</td>
            <td>${a.stock_id || '--'}</td>
            <td>${a.project || '--'}</td>
            <td>${a.qty_reserved || 0}</td>
            <td>${a.qty_available || 0}</td>
            <td><span class="badge badge-${a.status || 'pending'}">${a.status || 'pending'}</span></td>
            <td>${a.allocated_by || '--'}</td>
            <td>${a.date || '--'}</td>
            <td><button class="btn btn-sm btn-secondary" onclick="editAllocation('${a.id}')">Edit</button></td>
        </tr>
    `).join('');
}

function getFiltered() {
    const search = (document.getElementById('search-input').value || '').toLowerCase();
    const status = document.getElementById('status-filter').value;
    const project = document.getElementById('project-filter').value;
    return allocations.filter(a => {
        if (search && !JSON.stringify(a).toLowerCase().includes(search)) return false;
        if (status && a.status !== status) return false;
        if (project && a.project !== project) return false;
        return true;
    });
}

function filterTable() { renderTable(); }

function openModal() {
    document.getElementById('modal-title').textContent = 'New Material Allocation';
    document.getElementById('alloc-modal').classList.add('active');
}

function closeModal() {
    document.getElementById('alloc-modal').classList.remove('active');
}

function editAllocation(id) {
    document.getElementById('modal-title').textContent = 'Edit Allocation';
    document.getElementById('alloc-modal').classList.add('active');
}

async function saveAllocation() {
    const payload = {
        material: document.getElementById('alloc-material').value,
        stock_id: document.getElementById('alloc-stock').value,
        project: document.getElementById('alloc-project').value,
        qty_reserved: document.getElementById('alloc-qty').value,
        priority: document.getElementById('alloc-priority').value,
        notes: document.getElementById('alloc-notes').value,
    };
    try {
        await fetch('/api/allocations', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
        closeModal();
        loadAllocations();
    } catch(e) { console.error('Save failed:', e); }
}

document.addEventListener('DOMContentLoaded', loadAllocations);
</script>
"""
