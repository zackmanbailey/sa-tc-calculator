"""
TitanForge v4 -- Purchase Orders
==================================
PO list with status, create PO from MR, vendor selection, line items, total tracking, approval.
"""

PURCHASE_ORDERS_PAGE_HTML = r"""
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
    .po-container {
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
    .badge-draft { background: rgba(148,163,184,0.15); color: var(--tf-muted); }
    .badge-pending { background: rgba(245,158,11,0.15); color: var(--tf-orange); }
    .badge-approved { background: rgba(59,130,246,0.15); color: var(--tf-blue); }
    .badge-sent { background: rgba(16,185,129,0.15); color: var(--tf-green); }
    .badge-partial { background: rgba(212,168,67,0.15); color: var(--tf-gold); }
    .badge-received { background: rgba(16,185,129,0.15); color: var(--tf-green); }
    .badge-cancelled { background: rgba(239,68,68,0.15); color: var(--tf-red); }

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
        width: 90%; max-width: 750px; border: 1px solid rgba(255,255,255,0.1);
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

    .line-items-table { width: 100%; border-collapse: collapse; margin-top: 8px; }
    .line-items-table th { padding: 8px; font-size: 11px; color: var(--tf-muted); text-transform: uppercase; text-align: left; }
    .line-items-table td { padding: 4px 8px; }
    .line-items-table input { background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08); border-radius: 6px; padding: 8px 10px; color: var(--tf-text); font-size: 13px; width: 100%; }
    .po-total { font-size: 18px; font-weight: 700; color: var(--tf-gold); text-align: right; margin-top: 12px; }

/* ── Responsive ── */
@media (max-width: 768px) {
    .page-header h1 { font-size: 22px; }
    .toolbar { flex-direction: column; align-items: stretch; }
    .toolbar input[type="text"] { width: 100%; }
    .stat-row { grid-template-columns: 1fr 1fr; gap: 10px; }
    table { display: block; overflow-x: auto; -webkit-overflow-scrolling: touch; }
    .modal-overlay .modal, .modal { width: 95%; max-width: 95vw; margin: 20px auto; padding: 20px; }
    .form-row { grid-template-columns: 1fr; }
    .line-items-table { display: block; overflow-x: auto; -webkit-overflow-scrolling: touch; }
}
@media (max-width: 480px) {
    .stat-row { grid-template-columns: 1fr; }
    .toolbar { gap: 8px; }
}
</style>

<div class="po-container">
    <div class="page-header">
        <h1>Purchase Orders</h1>
        <p>Create, track, and manage purchase orders for material procurement</p>
    </div>

    <div class="stat-row">
        <div class="stat-card stat-gold">
            <div class="label">Total POs</div>
            <div class="value" id="stat-total">0</div>
        </div>
        <div class="stat-card stat-blue">
            <div class="label">Open POs</div>
            <div class="value" id="stat-open">0</div>
        </div>
        <div class="stat-card stat-green">
            <div class="label">Received</div>
            <div class="value" id="stat-received">0</div>
        </div>
        <div class="stat-card stat-gold">
            <div class="label">Total Value</div>
            <div class="value" id="stat-value">$0</div>
        </div>
    </div>

    <div class="toolbar">
        <div class="toolbar-left">
            <input type="text" id="search-input" placeholder="Search POs..." oninput="filterTable()">
            <select id="status-filter" onchange="filterTable()">
                <option value="">All Statuses</option>
                <option value="draft">Draft</option>
                <option value="pending">Pending Approval</option>
                <option value="approved">Approved</option>
                <option value="sent">Sent to Vendor</option>
                <option value="partial">Partially Received</option>
                <option value="received">Fully Received</option>
                <option value="cancelled">Cancelled</option>
            </select>
            <select id="vendor-filter" onchange="filterTable()">
                <option value="">All Vendors</option>
            </select>
        </div>
        <button class="btn btn-primary" onclick="openModal()">+ New PO</button>
    </div>

    <div id="table-container">
        <table class="data-table">
            <thead>
                <tr>
                    <th>PO Number</th>
                    <th>Vendor</th>
                    <th>Project</th>
                    <th>Created</th>
                    <th>Items</th>
                    <th>Total</th>
                    <th>Status</th>
                    <th>From MR</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody id="po-tbody"></tbody>
        </table>
        <div class="empty-state" id="empty-state">
            <div class="icon">&#x1F4E6;</div>
            <h3>No Purchase Orders</h3>
            <p>Create a purchase order to procure materials from vendors.</p>
            <button class="btn btn-primary" onclick="openModal()">+ New PO</button>
        </div>
    </div>
</div>

<!-- PO Modal -->
<div class="modal-overlay" id="po-modal">
    <div class="modal">
        <h2 id="modal-title">New Purchase Order</h2>
        <div class="form-row">
            <div class="form-group">
                <label>Vendor</label>
                <select id="po-vendor">
                    <option value="">Select vendor...</option>
                </select>
            </div>
            <div class="form-group">
                <label>Project</label>
                <select id="po-project">
                    <option value="">Select project...</option>
                </select>
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>From MR #</label>
                <input type="text" id="po-mr" placeholder="Optional - link to MR">
            </div>
            <div class="form-group">
                <label>Delivery Date</label>
                <input type="date" id="po-delivery">
            </div>
        </div>
        <div class="form-group">
            <label>Line Items</label>
            <table class="line-items-table" id="po-lines">
                <thead><tr><th>Description</th><th>Qty</th><th>Unit Price</th><th>Total</th><th></th></tr></thead>
                <tbody>
                    <tr>
                        <td><input type="text" placeholder="Item description"></td>
                        <td><input type="number" placeholder="0" style="width:80px" oninput="calcLineTotal(this)"></td>
                        <td><input type="number" placeholder="0.00" style="width:100px" oninput="calcLineTotal(this)"></td>
                        <td class="line-total">$0.00</td>
                        <td><button class="btn btn-sm btn-secondary" onclick="addPOLine()">+</button></td>
                    </tr>
                </tbody>
            </table>
            <div class="po-total">Total: <span id="po-grand-total">$0.00</span></div>
        </div>
        <div class="form-group">
            <label>Notes / Special Instructions</label>
            <textarea id="po-notes" rows="3" placeholder="Shipping instructions, special terms..."></textarea>
        </div>
        <div class="modal-actions">
            <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
            <button class="btn btn-primary" onclick="savePO()">Create PO</button>
        </div>
    </div>
</div>

<script>
let purchaseOrders = [];

async function loadPOs() {
    try {
        const resp = await fetch('/api/pos');
        const data = await resp.json();
        purchaseOrders = data.purchase_orders || [];
        renderTable();
        updateStats();
    } catch(e) { console.error('Failed to load POs:', e); renderTable(); }
}

function updateStats() {
    document.getElementById('stat-total').textContent = purchaseOrders.length;
    document.getElementById('stat-open').textContent = purchaseOrders.filter(p => ['draft','pending','approved','sent','partial'].includes(p.status)).length;
    document.getElementById('stat-received').textContent = purchaseOrders.filter(p => p.status === 'received').length;
    const total = purchaseOrders.reduce((s, p) => s + (p.total || 0), 0);
    document.getElementById('stat-value').textContent = '$' + total.toLocaleString();
}

function renderTable() {
    const tbody = document.getElementById('po-tbody');
    const empty = document.getElementById('empty-state');
    const filtered = getFiltered();
    if (filtered.length === 0) { tbody.innerHTML = ''; empty.style.display = 'block'; return; }
    empty.style.display = 'none';
    tbody.innerHTML = filtered.map(p => `
        <tr>
            <td><strong>${p.po_number || '--'}</strong></td>
            <td>${p.vendor || '--'}</td>
            <td>${p.project || '--'}</td>
            <td>${p.created || '--'}</td>
            <td>${p.item_count || 0}</td>
            <td>$${(p.total || 0).toLocaleString()}</td>
            <td><span class="badge badge-${p.status || 'draft'}">${p.status || 'draft'}</span></td>
            <td>${p.from_mr || '--'}</td>
            <td><button class="btn btn-sm btn-secondary" onclick="viewPO('${p.id}')">View</button></td>
        </tr>
    `).join('');
}

function getFiltered() {
    const search = (document.getElementById('search-input').value || '').toLowerCase();
    const status = document.getElementById('status-filter').value;
    const vendor = document.getElementById('vendor-filter').value;
    return purchaseOrders.filter(p => {
        if (search && !JSON.stringify(p).toLowerCase().includes(search)) return false;
        if (status && p.status !== status) return false;
        if (vendor && p.vendor !== vendor) return false;
        return true;
    });
}

function filterTable() { renderTable(); }
function openModal() { document.getElementById('po-modal').classList.add('active'); }
function closeModal() { document.getElementById('po-modal').classList.remove('active'); }
function viewPO(id) { openModal(); }

function addPOLine() {
    const tbody = document.getElementById('po-lines').querySelector('tbody');
    const tr = document.createElement('tr');
    tr.innerHTML = '<td><input type="text" placeholder="Item description"></td><td><input type="number" placeholder="0" style="width:80px" oninput="calcLineTotal(this)"></td><td><input type="number" placeholder="0.00" style="width:100px" oninput="calcLineTotal(this)"></td><td class="line-total">$0.00</td><td><button class="btn btn-sm btn-secondary" onclick="this.closest(\'tr\').remove();calcGrandTotal()">x</button></td>';
    tbody.appendChild(tr);
}

function calcLineTotal(el) {
    const row = el.closest('tr');
    const inputs = row.querySelectorAll('input[type=number]');
    const qty = parseFloat(inputs[0].value) || 0;
    const price = parseFloat(inputs[1].value) || 0;
    row.querySelector('.line-total').textContent = '$' + (qty * price).toFixed(2);
    calcGrandTotal();
}

function calcGrandTotal() {
    let total = 0;
    document.querySelectorAll('.line-total').forEach(el => {
        total += parseFloat(el.textContent.replace('$','').replace(',','')) || 0;
    });
    document.getElementById('po-grand-total').textContent = '$' + total.toFixed(2);
}

async function savePO() {
    const payload = {
        vendor: document.getElementById('po-vendor').value,
        project: document.getElementById('po-project').value,
        from_mr: document.getElementById('po-mr').value,
        delivery_date: document.getElementById('po-delivery').value,
        notes: document.getElementById('po-notes').value,
    };
    try {
        await fetch('/api/pos', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
        closeModal();
        loadPOs();
    } catch(e) { console.error('Save failed:', e); }
}

document.addEventListener('DOMContentLoaded', loadPOs);
</script>
"""
