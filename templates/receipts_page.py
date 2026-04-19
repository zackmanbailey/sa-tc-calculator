"""
TitanForge v4 -- Receipts
===========================
Receipt management: receipt log, link to POs, discrepancy tracking, receipt images, auto-update inventory.
"""

RECEIPTS_PAGE_HTML = r"""
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
    .receipts-container {
        max-width: 1400px; margin: 0 auto; padding: 24px 32px;
        font-family: 'Inter', system-ui, -apple-system, sans-serif; color: var(--tf-text);
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
    .badge-complete { background: rgba(16,185,129,0.15); color: var(--tf-green); }
    .badge-partial { background: rgba(245,158,11,0.15); color: var(--tf-orange); }
    .badge-discrepancy { background: rgba(239,68,68,0.15); color: var(--tf-red); }
    .badge-pending { background: rgba(59,130,246,0.15); color: var(--tf-blue); }

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

    .upload-zone {
        border: 2px dashed rgba(255,255,255,0.1); border-radius: 12px;
        padding: 24px; text-align: center; cursor: pointer; transition: border-color 0.2s;
    }
    .upload-zone:hover { border-color: var(--tf-gold); }

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

<div class="receipts-container">
    <div class="page-header">
        <h1>Receipt Management</h1>
        <p>Track material receipts, link to purchase orders, and manage discrepancies</p>
    </div>

    <div class="stat-row">
        <div class="stat-card stat-gold">
            <div class="label">Total Receipts</div>
            <div class="value" id="stat-total">0</div>
        </div>
        <div class="stat-card stat-green">
            <div class="label">Complete</div>
            <div class="value" id="stat-complete">0</div>
        </div>
        <div class="stat-card stat-orange">
            <div class="label">Partial</div>
            <div class="value" id="stat-partial">0</div>
        </div>
        <div class="stat-card stat-red">
            <div class="label">Discrepancies</div>
            <div class="value" id="stat-discrepancy">0</div>
        </div>
    </div>

    <div class="toolbar">
        <div class="toolbar-left">
            <input type="text" id="search-input" placeholder="Search receipts..." oninput="filterTable()">
            <select id="status-filter" onchange="filterTable()">
                <option value="">All Statuses</option>
                <option value="complete">Complete</option>
                <option value="partial">Partial</option>
                <option value="discrepancy">Discrepancy</option>
                <option value="pending">Pending</option>
            </select>
            <input type="date" id="date-filter" onchange="filterTable()">
        </div>
        <button class="btn btn-primary" onclick="openModal()">+ Log Receipt</button>
    </div>

    <div id="table-container">
        <table class="data-table">
            <thead>
                <tr>
                    <th>Receipt #</th>
                    <th>PO Number</th>
                    <th>Vendor</th>
                    <th>Received Date</th>
                    <th>Items</th>
                    <th>Weight (lbs)</th>
                    <th>Status</th>
                    <th>Received By</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody id="receipts-tbody"></tbody>
        </table>
        <div class="empty-state" id="empty-state">
            <div class="icon">&#x1F9FE;</div>
            <h3>No Receipts Logged</h3>
            <p>Log material receipts as deliveries arrive to keep inventory accurate.</p>
            <button class="btn btn-primary" onclick="openModal()">+ Log Receipt</button>
        </div>
    </div>
</div>

<!-- Receipt Modal -->
<div class="modal-overlay" id="receipt-modal">
    <div class="modal">
        <h2 id="modal-title">Log Material Receipt</h2>
        <div class="form-row">
            <div class="form-group">
                <label>PO Number</label>
                <select id="rcpt-po">
                    <option value="">Select PO...</option>
                </select>
            </div>
            <div class="form-group">
                <label>Received Date</label>
                <input type="date" id="rcpt-date">
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Vendor</label>
                <input type="text" id="rcpt-vendor" placeholder="Auto-fill from PO">
            </div>
            <div class="form-group">
                <label>Received By</label>
                <input type="text" id="rcpt-by" placeholder="Your name">
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Items Received</label>
                <input type="number" id="rcpt-items" placeholder="Number of items">
            </div>
            <div class="form-group">
                <label>Weight (lbs)</label>
                <input type="number" id="rcpt-weight" placeholder="Total weight">
            </div>
        </div>
        <div class="form-group">
            <label>Condition</label>
            <select id="rcpt-condition">
                <option value="good">Good - No Issues</option>
                <option value="minor">Minor Damage</option>
                <option value="damaged">Damaged - Needs Review</option>
                <option value="wrong">Wrong Material</option>
                <option value="short">Short Shipment</option>
            </select>
        </div>
        <div class="form-group">
            <label>Receipt Photo</label>
            <div class="upload-zone" onclick="document.getElementById('rcpt-photo').click()">
                <div style="font-size:28px;opacity:0.5;">&#x1F4F7;</div>
                <p style="margin:8px 0 0;font-size:13px;color:var(--tf-muted)">Click to upload delivery photo</p>
                <input type="file" id="rcpt-photo" style="display:none" accept="image/*">
            </div>
        </div>
        <div class="form-group">
            <label>Notes / Discrepancies</label>
            <textarea id="rcpt-notes" rows="3" placeholder="Note any discrepancies, damage, or short items..."></textarea>
        </div>
        <div class="modal-actions">
            <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
            <button class="btn btn-primary" onclick="saveReceipt()">Save Receipt</button>
        </div>
    </div>
</div>

<script>
let receipts = [];

async function loadReceipts() {
    try {
        const resp = await fetch('/api/receipts');
        const data = await resp.json();
        receipts = data.receipts || [];
        renderTable();
        updateStats();
    } catch(e) { console.error('Failed to load receipts:', e); renderTable(); }
}

function updateStats() {
    document.getElementById('stat-total').textContent = receipts.length;
    document.getElementById('stat-complete').textContent = receipts.filter(r => r.status === 'complete').length;
    document.getElementById('stat-partial').textContent = receipts.filter(r => r.status === 'partial').length;
    document.getElementById('stat-discrepancy').textContent = receipts.filter(r => r.status === 'discrepancy').length;
}

function renderTable() {
    const tbody = document.getElementById('receipts-tbody');
    const empty = document.getElementById('empty-state');
    const filtered = getFiltered();
    if (filtered.length === 0) { tbody.innerHTML = ''; empty.style.display = 'block'; return; }
    empty.style.display = 'none';
    tbody.innerHTML = filtered.map(r => `
        <tr>
            <td><strong>${r.receipt_number || '--'}</strong></td>
            <td>${r.po_number || '--'}</td>
            <td>${r.vendor || '--'}</td>
            <td>${r.received_date || '--'}</td>
            <td>${r.items || 0}</td>
            <td>${(r.weight || 0).toLocaleString()}</td>
            <td><span class="badge badge-${r.status || 'pending'}">${r.status || 'pending'}</span></td>
            <td>${r.received_by || '--'}</td>
            <td><button class="btn btn-sm btn-secondary" onclick="viewReceipt('${r.id}')">View</button></td>
        </tr>
    `).join('');
}

function getFiltered() {
    const search = (document.getElementById('search-input').value || '').toLowerCase();
    const status = document.getElementById('status-filter').value;
    return receipts.filter(r => {
        if (search && !JSON.stringify(r).toLowerCase().includes(search)) return false;
        if (status && r.status !== status) return false;
        return true;
    });
}

function filterTable() { renderTable(); }
function openModal() { document.getElementById('receipt-modal').classList.add('active'); }
function closeModal() { document.getElementById('receipt-modal').classList.remove('active'); }
function viewReceipt(id) { openModal(); }

async function saveReceipt() {
    const payload = {
        po_number: document.getElementById('rcpt-po').value,
        received_date: document.getElementById('rcpt-date').value,
        vendor: document.getElementById('rcpt-vendor').value,
        received_by: document.getElementById('rcpt-by').value,
        items: document.getElementById('rcpt-items').value,
        weight: document.getElementById('rcpt-weight').value,
        condition: document.getElementById('rcpt-condition').value,
        notes: document.getElementById('rcpt-notes').value,
    };
    try {
        await fetch('/api/receipts', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
        closeModal();
        loadReceipts();
    } catch(e) { console.error('Save failed:', e); }
}

document.addEventListener('DOMContentLoaded', loadReceipts);
</script>
"""
