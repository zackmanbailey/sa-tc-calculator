"""
TitanForge v4 -- Receiving Dock
=================================
Expected deliveries, check-in workflow, damage inspection, weight verification, put-away assignment.
"""

RECEIVING_PAGE_HTML = r"""
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
    .recv-container {
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
    .toolbar input[type="text"], .toolbar input[type="date"], .toolbar select {
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

    .delivery-cards {
        display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
        gap: 16px; margin-bottom: 24px;
    }
    .delivery-card {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06); padding: 20px 24px;
        transition: border-color 0.2s, transform 0.15s;
    }
    .delivery-card:hover { border-color: var(--tf-blue); transform: translateY(-2px); }
    .delivery-card .card-header {
        display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;
    }
    .delivery-card .card-header h3 { font-size: 16px; font-weight: 700; margin: 0; }
    .delivery-card .card-detail { font-size: 13px; color: var(--tf-muted); margin-bottom: 6px; }
    .delivery-card .card-detail strong { color: var(--tf-text); }
    .delivery-card .card-actions { display: flex; gap: 8px; margin-top: 14px; }

    .badge {
        display: inline-block; padding: 4px 10px; border-radius: 6px;
        font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.3px;
    }
    .badge-expected { background: rgba(59,130,246,0.15); color: var(--tf-blue); }
    .badge-arrived { background: rgba(245,158,11,0.15); color: var(--tf-orange); }
    .badge-inspecting { background: rgba(212,168,67,0.15); color: var(--tf-gold); }
    .badge-checked-in { background: rgba(16,185,129,0.15); color: var(--tf-green); }
    .badge-rejected { background: rgba(239,68,68,0.15); color: var(--tf-red); }
    .badge-put-away { background: rgba(148,163,184,0.15); color: var(--tf-muted); }

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
        width: 90%; max-width: 650px; border: 1px solid rgba(255,255,255,0.1);
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
    .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 24px; }

    .checklist { list-style: none; padding: 0; margin: 12px 0; }
    .checklist li {
        padding: 10px 14px; background: var(--tf-bg); border-radius: 8px; margin-bottom: 6px;
        display: flex; align-items: center; gap: 10px; font-size: 14px;
        border: 1px solid rgba(255,255,255,0.06);
    }
    .checklist li input[type="checkbox"] { width: 18px; height: 18px; accent-color: var(--tf-green); }
</style>

<div class="recv-container">
    <div class="page-header">
        <h1>Receiving Dock</h1>
        <p>Expected deliveries, check-in workflow, damage inspection, and put-away assignment</p>
    </div>

    <div class="stat-row">
        <div class="stat-card stat-blue">
            <div class="label">Expected Today</div>
            <div class="value" id="stat-expected">0</div>
        </div>
        <div class="stat-card stat-orange">
            <div class="label">Arrived</div>
            <div class="value" id="stat-arrived">0</div>
        </div>
        <div class="stat-card stat-green">
            <div class="label">Checked In</div>
            <div class="value" id="stat-checkedin">0</div>
        </div>
        <div class="stat-card stat-red">
            <div class="label">Issues</div>
            <div class="value" id="stat-issues">0</div>
        </div>
    </div>

    <div class="toolbar">
        <div class="toolbar-left">
            <input type="text" id="search-input" placeholder="Search deliveries..." oninput="filterData()">
            <select id="status-filter" onchange="filterData()">
                <option value="">All Statuses</option>
                <option value="expected">Expected</option>
                <option value="arrived">Arrived</option>
                <option value="inspecting">Inspecting</option>
                <option value="checked-in">Checked In</option>
                <option value="put-away">Put Away</option>
                <option value="rejected">Rejected</option>
            </select>
            <input type="date" id="date-filter" onchange="filterData()">
        </div>
        <button class="btn btn-primary" onclick="openModal()">+ Expected Delivery</button>
    </div>

    <!-- Delivery Cards (for today's expected) -->
    <div class="delivery-cards" id="delivery-cards"></div>

    <!-- Full History Table -->
    <div id="table-container">
        <table class="data-table">
            <thead>
                <tr>
                    <th>Delivery #</th>
                    <th>PO Number</th>
                    <th>Vendor</th>
                    <th>Expected</th>
                    <th>Arrived</th>
                    <th>Exp. Weight</th>
                    <th>Act. Weight</th>
                    <th>Status</th>
                    <th>Put-Away</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody id="recv-tbody"></tbody>
        </table>
        <div class="empty-state" id="empty-state">
            <div class="icon">&#x1F69B;</div>
            <h3>No Deliveries Scheduled</h3>
            <p>Add expected deliveries to track incoming materials through check-in and put-away.</p>
            <button class="btn btn-primary" onclick="openModal()">+ Expected Delivery</button>
        </div>
    </div>
</div>

<!-- Check-In Modal -->
<div class="modal-overlay" id="recv-modal">
    <div class="modal">
        <h2 id="modal-title">Expected Delivery</h2>
        <div class="form-row">
            <div class="form-group">
                <label>PO Number</label>
                <select id="recv-po">
                    <option value="">Select PO...</option>
                </select>
            </div>
            <div class="form-group">
                <label>Expected Date</label>
                <input type="date" id="recv-date">
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Vendor</label>
                <input type="text" id="recv-vendor" placeholder="Vendor name">
            </div>
            <div class="form-group">
                <label>Carrier</label>
                <input type="text" id="recv-carrier" placeholder="Trucking company">
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Expected Weight (lbs)</label>
                <input type="number" id="recv-exp-weight" placeholder="0">
            </div>
            <div class="form-group">
                <label>Actual Weight (lbs)</label>
                <input type="number" id="recv-act-weight" placeholder="Weigh on arrival">
            </div>
        </div>
        <div class="form-group">
            <label>Inspection Checklist</label>
            <ul class="checklist">
                <li><input type="checkbox" id="chk-1"><span>Packing slip matches PO</span></li>
                <li><input type="checkbox" id="chk-2"><span>Material matches description</span></li>
                <li><input type="checkbox" id="chk-3"><span>No visible damage</span></li>
                <li><input type="checkbox" id="chk-4"><span>Weight verified</span></li>
                <li><input type="checkbox" id="chk-5"><span>MTR / Certs received</span></li>
            </ul>
        </div>
        <div class="form-group">
            <label>Put-Away Location</label>
            <input type="text" id="recv-location" placeholder="e.g., Bay 3, Rack A-2">
        </div>
        <div class="form-group">
            <label>Notes</label>
            <textarea id="recv-notes" rows="3" placeholder="Inspection notes, damage details..."></textarea>
        </div>
        <div class="modal-actions">
            <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
            <button class="btn btn-success" onclick="checkIn()">Check In</button>
            <button class="btn btn-primary" onclick="saveDelivery()">Save</button>
        </div>
    </div>
</div>

<script>
let deliveries = [];

async function loadDeliveries() {
    try {
        const resp = await fetch('/api/receiving');
        const data = await resp.json();
        deliveries = data.deliveries || [];
        renderCards();
        renderTable();
        updateStats();
    } catch(e) { console.error('Failed to load deliveries:', e); renderTable(); }
}

function updateStats() {
    document.getElementById('stat-expected').textContent = deliveries.filter(d => d.status === 'expected').length;
    document.getElementById('stat-arrived').textContent = deliveries.filter(d => d.status === 'arrived').length;
    document.getElementById('stat-checkedin').textContent = deliveries.filter(d => d.status === 'checked-in').length;
    document.getElementById('stat-issues').textContent = deliveries.filter(d => d.status === 'rejected').length;
}

function renderCards() {
    const container = document.getElementById('delivery-cards');
    const today = deliveries.filter(d => ['expected','arrived','inspecting'].includes(d.status));
    if (today.length === 0) { container.innerHTML = ''; return; }
    container.innerHTML = today.map(d => `
        <div class="delivery-card">
            <div class="card-header">
                <h3>${d.po_number || 'No PO'}</h3>
                <span class="badge badge-${d.status}">${d.status}</span>
            </div>
            <div class="card-detail"><strong>Vendor:</strong> ${d.vendor || '--'}</div>
            <div class="card-detail"><strong>Expected:</strong> ${d.expected_date || '--'}</div>
            <div class="card-detail"><strong>Weight:</strong> ${(d.expected_weight || 0).toLocaleString()} lbs</div>
            <div class="card-detail"><strong>Carrier:</strong> ${d.carrier || '--'}</div>
            <div class="card-actions">
                <button class="btn btn-sm btn-success" onclick="beginCheckIn('${d.id}')">Check In</button>
                <button class="btn btn-sm btn-secondary" onclick="viewDelivery('${d.id}')">Details</button>
            </div>
        </div>
    `).join('');
}

function renderTable() {
    const tbody = document.getElementById('recv-tbody');
    const empty = document.getElementById('empty-state');
    const filtered = getFiltered();
    if (filtered.length === 0) { tbody.innerHTML = ''; empty.style.display = 'block'; return; }
    empty.style.display = 'none';
    tbody.innerHTML = filtered.map(d => `
        <tr>
            <td><strong>${d.delivery_number || '--'}</strong></td>
            <td>${d.po_number || '--'}</td>
            <td>${d.vendor || '--'}</td>
            <td>${d.expected_date || '--'}</td>
            <td>${d.arrived_date || '--'}</td>
            <td>${(d.expected_weight || 0).toLocaleString()}</td>
            <td>${(d.actual_weight || 0).toLocaleString()}</td>
            <td><span class="badge badge-${d.status || 'expected'}">${(d.status || 'expected').replace('-',' ')}</span></td>
            <td>${d.location || '--'}</td>
            <td><button class="btn btn-sm btn-secondary" onclick="viewDelivery('${d.id}')">View</button></td>
        </tr>
    `).join('');
}

function getFiltered() {
    const search = (document.getElementById('search-input').value || '').toLowerCase();
    const status = document.getElementById('status-filter').value;
    return deliveries.filter(d => {
        if (search && !JSON.stringify(d).toLowerCase().includes(search)) return false;
        if (status && d.status !== status) return false;
        return true;
    });
}

function filterData() { renderCards(); renderTable(); }
function openModal() { document.getElementById('modal-title').textContent = 'Expected Delivery'; document.getElementById('recv-modal').classList.add('active'); }
function closeModal() { document.getElementById('recv-modal').classList.remove('active'); }
function viewDelivery(id) { openModal(); }
function beginCheckIn(id) { document.getElementById('modal-title').textContent = 'Check In Delivery'; openModal(); }

async function checkIn() {
    await saveDelivery();
}

async function saveDelivery() {
    const payload = {
        po_number: document.getElementById('recv-po').value,
        expected_date: document.getElementById('recv-date').value,
        vendor: document.getElementById('recv-vendor').value,
        carrier: document.getElementById('recv-carrier').value,
        expected_weight: document.getElementById('recv-exp-weight').value,
        actual_weight: document.getElementById('recv-act-weight').value,
        location: document.getElementById('recv-location').value,
        notes: document.getElementById('recv-notes').value,
    };
    try {
        await fetch('/api/receiving', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
        closeModal();
        loadDeliveries();
    } catch(e) { console.error('Save failed:', e); }
}

document.addEventListener('DOMContentLoaded', loadDeliveries);
</script>
"""
