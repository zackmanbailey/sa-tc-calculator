"""
TitanForge v4 -- Purchase Orders
==================================
PO list with status pipeline, create PO from MR, vendor selection, line items, total tracking, approval.
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
    .btn-success { background: var(--tf-green); color: #fff; }
    .btn-success:hover { background: #0ea572; }
    .btn-danger { background: var(--tf-red); color: #fff; }
    .btn-danger:hover { background: #dc2626; }
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
    .badge-acknowledged { background: rgba(212,168,67,0.15); color: var(--tf-gold); }
    .badge-partial { background: rgba(212,168,67,0.15); color: var(--tf-gold); }
    .badge-received { background: rgba(16,185,129,0.25); color: var(--tf-green); }
    .badge-closed { background: rgba(148,163,184,0.15); color: var(--tf-muted); }
    .badge-cancelled { background: rgba(239,68,68,0.15); color: var(--tf-red); }

    .empty-state {
        text-align: center; padding: 60px 20px; color: var(--tf-muted);
    }
    .empty-state .icon { font-size: 48px; margin-bottom: 16px; opacity: 0.5; }
    .empty-state h3 { font-size: 18px; color: var(--tf-text); margin-bottom: 8px; }
    .empty-state p { font-size: 14px; max-width: 400px; margin: 0 auto 20px; }

    /* Status Pipeline */
    .status-pipeline {
        display: flex; align-items: center; gap: 0; margin-bottom: 24px;
        background: var(--tf-card); border-radius: 12px; padding: 16px 20px;
        border: 1px solid rgba(255,255,255,0.06); overflow-x: auto;
    }
    .pipeline-step {
        display: flex; align-items: center; gap: 8px; padding: 8px 16px;
        border-radius: 8px; font-size: 12px; font-weight: 600;
        white-space: nowrap; color: var(--tf-muted); transition: all 0.2s;
        cursor: pointer;
    }
    .pipeline-step:hover { background: rgba(255,255,255,0.04); }
    .pipeline-step.active { background: rgba(59,130,246,0.15); color: var(--tf-blue); }
    .pipeline-step .step-count {
        background: rgba(255,255,255,0.08); padding: 2px 8px; border-radius: 10px;
        font-size: 11px; min-width: 20px; text-align: center;
    }
    .pipeline-step.active .step-count { background: rgba(59,130,246,0.3); }
    .pipeline-arrow { color: rgba(255,255,255,0.15); font-size: 16px; margin: 0 4px; flex-shrink: 0; }

    .modal-overlay {
        display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6);
        z-index: 1000; justify-content: center; align-items: center;
    }
    .modal-overlay.active { display: flex; }
    .modal {
        background: var(--tf-card); border-radius: 16px; padding: 32px;
        width: 90%; max-width: 800px; border: 1px solid rgba(255,255,255,0.1);
        max-height: 85vh; overflow-y: auto;
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

    /* Detail view */
    .detail-section { margin-bottom: 20px; }
    .detail-section h3 { font-size: 14px; font-weight: 700; color: var(--tf-gold); text-transform: uppercase; letter-spacing: 0.5px; margin: 0 0 12px 0; padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.06); }
    .detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .detail-item .detail-label { font-size: 11px; color: var(--tf-muted); text-transform: uppercase; margin-bottom: 2px; }
    .detail-item .detail-value { font-size: 14px; font-weight: 600; }
    .detail-line-items { width: 100%; border-collapse: collapse; margin-top: 8px; }
    .detail-line-items th { padding: 10px 12px; font-size: 11px; color: var(--tf-muted); text-transform: uppercase; text-align: left; background: rgba(0,0,0,0.2); }
    .detail-line-items td { padding: 10px 12px; font-size: 14px; border-bottom: 1px solid rgba(255,255,255,0.04); }
    .detail-actions { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 16px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.06); }

/* Responsive */
@media (max-width: 768px) {
    .page-header h1 { font-size: 22px; }
    .toolbar { flex-direction: column; align-items: stretch; }
    .toolbar input[type="text"] { width: 100%; }
    .stat-row { grid-template-columns: 1fr 1fr; gap: 10px; }
    table { display: block; overflow-x: auto; -webkit-overflow-scrolling: touch; }
    .modal-overlay .modal, .modal { width: 95%; max-width: 95vw; margin: 20px auto; padding: 20px; }
    .form-row { grid-template-columns: 1fr; }
    .line-items-table { display: block; overflow-x: auto; -webkit-overflow-scrolling: touch; }
    .status-pipeline { padding: 12px; }
    .detail-grid { grid-template-columns: 1fr; }
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
        <div class="stat-card stat-gold" onclick="setPipelineFilter('')">
            <div class="label">Total POs</div>
            <div class="value" id="stat-total">0</div>
        </div>
        <div class="stat-card stat-blue" onclick="setPipelineFilter('open')">
            <div class="label">Open POs</div>
            <div class="value" id="stat-open">0</div>
        </div>
        <div class="stat-card stat-green" onclick="setPipelineFilter('received')">
            <div class="label">Received</div>
            <div class="value" id="stat-received">0</div>
        </div>
        <div class="stat-card stat-gold">
            <div class="label">Total Value</div>
            <div class="value" id="stat-value">$0</div>
        </div>
    </div>

    <!-- Status Pipeline -->
    <div class="status-pipeline" id="status-pipeline">
        <div class="pipeline-step active" onclick="setPipelineFilter('')">
            <span>All</span><span class="step-count" id="pipe-all">0</span>
        </div>
        <span class="pipeline-arrow">&#x276F;</span>
        <div class="pipeline-step" onclick="setPipelineFilter('draft')">
            <span>Draft</span><span class="step-count" id="pipe-draft">0</span>
        </div>
        <span class="pipeline-arrow">&#x276F;</span>
        <div class="pipeline-step" onclick="setPipelineFilter('sent')">
            <span>Sent</span><span class="step-count" id="pipe-sent">0</span>
        </div>
        <span class="pipeline-arrow">&#x276F;</span>
        <div class="pipeline-step" onclick="setPipelineFilter('acknowledged')">
            <span>Acknowledged</span><span class="step-count" id="pipe-acknowledged">0</span>
        </div>
        <span class="pipeline-arrow">&#x276F;</span>
        <div class="pipeline-step" onclick="setPipelineFilter('partial')">
            <span>Partial</span><span class="step-count" id="pipe-partial">0</span>
        </div>
        <span class="pipeline-arrow">&#x276F;</span>
        <div class="pipeline-step" onclick="setPipelineFilter('received')">
            <span>Received</span><span class="step-count" id="pipe-received">0</span>
        </div>
        <span class="pipeline-arrow">&#x276F;</span>
        <div class="pipeline-step" onclick="setPipelineFilter('closed')">
            <span>Closed</span><span class="step-count" id="pipe-closed">0</span>
        </div>
    </div>

    <div class="toolbar">
        <div class="toolbar-left">
            <input type="text" id="search-input" placeholder="Search POs..." oninput="filterTable()">
            <select id="vendor-filter" onchange="filterTable()">
                <option value="">All Vendors</option>
            </select>
        </div>
        <div style="display:flex;gap:10px;">
            <button class="btn btn-secondary" onclick="openCreateFromMR()">Create from MR</button>
            <button class="btn btn-primary" onclick="openCreateModal()">+ New PO</button>
        </div>
    </div>

    <div id="table-container">
        <table class="data-table">
            <thead>
                <tr>
                    <th>PO Number</th>
                    <th>Vendor</th>
                    <th>Project</th>
                    <th>Created</th>
                    <th>Delivery</th>
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
            <button class="btn btn-primary" onclick="openCreateModal()">+ New PO</button>
        </div>
    </div>
</div>

<!-- Create/Edit PO Modal -->
<div class="modal-overlay" id="po-modal">
    <div class="modal">
        <h2 id="modal-title">New Purchase Order</h2>
        <input type="hidden" id="po-edit-id" value="">
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
                <thead><tr><th>Description</th><th>Qty</th><th>Unit</th><th>Unit Price</th><th>Total</th><th></th></tr></thead>
                <tbody id="line-items-body">
                    <tr>
                        <td><input type="text" class="li-desc" placeholder="Item description"></td>
                        <td><input type="number" class="li-qty" placeholder="0" style="width:80px" oninput="calcLineTotal(this)"></td>
                        <td><input type="text" class="li-unit" placeholder="ea" style="width:60px"></td>
                        <td><input type="number" class="li-price" placeholder="0.00" style="width:100px" step="0.01" oninput="calcLineTotal(this)"></td>
                        <td class="line-total" style="white-space:nowrap">$0.00</td>
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
            <button class="btn btn-secondary" onclick="closeModal('po-modal')">Cancel</button>
            <button class="btn btn-primary" id="modal-save-btn" onclick="savePO()">Create PO</button>
        </div>
    </div>
</div>

<!-- PO Detail Modal -->
<div class="modal-overlay" id="detail-modal">
    <div class="modal" style="max-width:850px;">
        <h2 id="detail-title">PO Details</h2>
        <div id="detail-content"></div>
    </div>
</div>

<!-- Create from MR Modal -->
<div class="modal-overlay" id="mr-modal">
    <div class="modal" style="max-width:600px;">
        <h2>Create PO from Material Requisition</h2>
        <div class="form-group">
            <label>Select Approved MR</label>
            <select id="mr-select">
                <option value="">Loading MRs...</option>
            </select>
        </div>
        <div id="mr-preview" style="display:none;">
            <div class="detail-section">
                <h3>MR Details</h3>
                <div id="mr-preview-content"></div>
            </div>
        </div>
        <div class="form-group">
            <label>Vendor</label>
            <select id="mr-vendor">
                <option value="">Select vendor...</option>
            </select>
        </div>
        <div class="modal-actions">
            <button class="btn btn-secondary" onclick="closeModal('mr-modal')">Cancel</button>
            <button class="btn btn-primary" onclick="convertMRtoPO()">Create PO from MR</button>
        </div>
    </div>
</div>

<script>
let purchaseOrders = [];
let pipelineFilter = '';
let vendorsList = [];
let mrList = [];

async function loadPOs() {
    try {
        const resp = await fetch('/api/pos');
        const data = await resp.json();
        purchaseOrders = data.purchase_orders || [];
        renderTable();
        updateStats();
        updatePipeline();
    } catch(e) { console.error('Failed to load POs:', e); renderTable(); }
}

async function loadVendors() {
    try {
        const resp = await fetch('/api/vendors');
        const data = await resp.json();
        vendorsList = data.vendors || [];
        const selects = ['po-vendor', 'vendor-filter', 'mr-vendor'];
        selects.forEach(id => {
            const el = document.getElementById(id);
            if (!el) return;
            const first = el.options[0].outerHTML;
            el.innerHTML = first + vendorsList.map(v => `<option value="${v.name || v.id}">${v.name || v.id}</option>`).join('');
        });
    } catch(e) { console.error('Failed to load vendors:', e); }
}

async function loadProjects() {
    try {
        const resp = await fetch('/api/projects');
        const data = await resp.json();
        const projects = data.projects || [];
        const sel = document.getElementById('po-project');
        if (!sel) return;
        const first = sel.options[0].outerHTML;
        sel.innerHTML = first + projects.map(p => `<option value="${p.job_number || p.name}">${p.job_number || ''} - ${p.name || 'Unnamed'}</option>`).join('');
    } catch(e) { console.error('Failed to load projects:', e); }
}

function updateStats() {
    document.getElementById('stat-total').textContent = purchaseOrders.length;
    const openStatuses = ['draft','sent','acknowledged','partial'];
    document.getElementById('stat-open').textContent = purchaseOrders.filter(p => openStatuses.includes(p.status)).length;
    document.getElementById('stat-received').textContent = purchaseOrders.filter(p => p.status === 'received' || p.status === 'closed').length;
    const total = purchaseOrders.reduce((s, p) => s + (parseFloat(p.total) || parseFloat(p.grand_total) || 0), 0);
    document.getElementById('stat-value').textContent = '$' + total.toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 0});
}

function updatePipeline() {
    const counts = {};
    purchaseOrders.forEach(p => { counts[p.status] = (counts[p.status] || 0) + 1; });
    document.getElementById('pipe-all').textContent = purchaseOrders.length;
    ['draft','sent','acknowledged','partial','received','closed'].forEach(s => {
        const el = document.getElementById('pipe-' + s);
        if (el) el.textContent = counts[s] || 0;
    });
    // Highlight active step
    document.querySelectorAll('.pipeline-step').forEach(el => el.classList.remove('active'));
    const steps = document.querySelectorAll('.pipeline-step');
    if (!pipelineFilter) { steps[0].classList.add('active'); }
    else {
        steps.forEach(s => { if (s.textContent.trim().toLowerCase().startsWith(pipelineFilter)) s.classList.add('active'); });
    }
}

function setPipelineFilter(status) {
    if (status === 'open') {
        pipelineFilter = '';
        document.getElementById('search-input').value = '';
        // Filter to open statuses only
        pipelineFilter = '__open__';
    } else {
        pipelineFilter = status;
    }
    renderTable();
    updatePipeline();
}

function renderTable() {
    const tbody = document.getElementById('po-tbody');
    const empty = document.getElementById('empty-state');
    const filtered = getFiltered();
    if (filtered.length === 0) { tbody.innerHTML = ''; empty.style.display = 'block'; return; }
    empty.style.display = 'none';
    tbody.innerHTML = filtered.map(p => {
        const total = parseFloat(p.total) || parseFloat(p.grand_total) || 0;
        const itemCount = (p.line_items || p.items || []).length || p.item_count || 0;
        return `<tr onclick="viewPO('${p.id}')">
            <td><strong>${p.po_number || '--'}</strong></td>
            <td>${p.vendor || '--'}</td>
            <td>${p.project || '--'}</td>
            <td>${(p.created || '').slice(0,10)}</td>
            <td>${p.delivery_date || '--'}</td>
            <td>${itemCount}</td>
            <td style="font-weight:700">$${total.toLocaleString(undefined, {minimumFractionDigits:2})}</td>
            <td><span class="badge badge-${p.status || 'draft'}">${(p.status || 'draft').replace(/_/g,' ')}</span></td>
            <td>${p.from_mr || '--'}</td>
            <td>
                <button class="btn btn-sm btn-secondary" onclick="event.stopPropagation();viewPO('${p.id}')">View</button>
            </td>
        </tr>`;
    }).join('');
}

function getFiltered() {
    const search = (document.getElementById('search-input').value || '').toLowerCase();
    const vendor = document.getElementById('vendor-filter').value;
    const openStatuses = ['draft','sent','acknowledged','partial'];
    return purchaseOrders.filter(p => {
        if (search && !JSON.stringify(p).toLowerCase().includes(search)) return false;
        if (pipelineFilter === '__open__' && !openStatuses.includes(p.status)) return false;
        else if (pipelineFilter && pipelineFilter !== '__open__' && p.status !== pipelineFilter) return false;
        if (vendor && p.vendor !== vendor) return false;
        return true;
    });
}

function filterTable() { renderTable(); }

function openCreateModal() {
    document.getElementById('modal-title').textContent = 'New Purchase Order';
    document.getElementById('modal-save-btn').textContent = 'Create PO';
    document.getElementById('po-edit-id').value = '';
    // Reset form
    ['po-vendor','po-project','po-mr','po-delivery','po-notes'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });
    // Reset line items to single empty row
    document.getElementById('line-items-body').innerHTML = `
        <tr>
            <td><input type="text" class="li-desc" placeholder="Item description"></td>
            <td><input type="number" class="li-qty" placeholder="0" style="width:80px" oninput="calcLineTotal(this)"></td>
            <td><input type="text" class="li-unit" placeholder="ea" style="width:60px"></td>
            <td><input type="number" class="li-price" placeholder="0.00" style="width:100px" step="0.01" oninput="calcLineTotal(this)"></td>
            <td class="line-total" style="white-space:nowrap">$0.00</td>
            <td><button class="btn btn-sm btn-secondary" onclick="addPOLine()">+</button></td>
        </tr>`;
    document.getElementById('po-grand-total').textContent = '$0.00';
    document.getElementById('po-modal').classList.add('active');
}

function closeModal(id) { document.getElementById(id).classList.remove('active'); }

function addPOLine() {
    const tbody = document.getElementById('line-items-body');
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td><input type="text" class="li-desc" placeholder="Item description"></td>
        <td><input type="number" class="li-qty" placeholder="0" style="width:80px" oninput="calcLineTotal(this)"></td>
        <td><input type="text" class="li-unit" placeholder="ea" style="width:60px"></td>
        <td><input type="number" class="li-price" placeholder="0.00" style="width:100px" step="0.01" oninput="calcLineTotal(this)"></td>
        <td class="line-total" style="white-space:nowrap">$0.00</td>
        <td><button class="btn btn-sm btn-secondary" onclick="this.closest('tr').remove();calcGrandTotal()">x</button></td>`;
    tbody.appendChild(tr);
}

function calcLineTotal(el) {
    const row = el.closest('tr');
    const qty = parseFloat(row.querySelector('.li-qty').value) || 0;
    const price = parseFloat(row.querySelector('.li-price').value) || 0;
    row.querySelector('.line-total').textContent = '$' + (qty * price).toFixed(2);
    calcGrandTotal();
}

function calcGrandTotal() {
    let total = 0;
    document.querySelectorAll('#line-items-body .line-total').forEach(el => {
        total += parseFloat(el.textContent.replace('$','').replace(',','')) || 0;
    });
    document.getElementById('po-grand-total').textContent = '$' + total.toFixed(2);
}

function collectLineItems() {
    const rows = document.querySelectorAll('#line-items-body tr');
    const items = [];
    rows.forEach(row => {
        const desc = (row.querySelector('.li-desc') || {}).value || '';
        const qty = parseFloat((row.querySelector('.li-qty') || {}).value) || 0;
        const unit = (row.querySelector('.li-unit') || {}).value || 'ea';
        const price = parseFloat((row.querySelector('.li-price') || {}).value) || 0;
        if (desc || qty > 0) {
            items.push({ description: desc, quantity: qty, unit: unit, unit_price: price, line_total: qty * price });
        }
    });
    return items;
}

async function savePO() {
    const lineItems = collectLineItems();
    const payload = {
        vendor: document.getElementById('po-vendor').value,
        project: document.getElementById('po-project').value,
        from_mr: document.getElementById('po-mr').value,
        delivery_date: document.getElementById('po-delivery').value,
        notes: document.getElementById('po-notes').value,
        line_items: lineItems,
    };
    if (!payload.vendor) { showToast('Please select a vendor', 'error'); return; }

    try {
        const resp = await fetch('/api/pos', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
        const data = await resp.json();
        if (data.error) { showToast(data.error, 'error'); return; }
        closeModal('po-modal');
        showToast('Purchase order created: ' + (data.po_number || ''), 'success');
        loadPOs();
    } catch(e) { console.error('Save failed:', e); showToast('Failed to save PO', 'error'); }
}

async function viewPO(id) {
    const po = purchaseOrders.find(p => p.id === id);
    if (!po) return;
    const total = parseFloat(po.total) || parseFloat(po.grand_total) || 0;
    const items = po.line_items || po.items || [];

    let itemsHtml = '';
    if (items.length > 0) {
        itemsHtml = `<table class="detail-line-items" style="border-radius:8px;overflow:hidden;border:1px solid rgba(255,255,255,0.06);">
            <thead><tr><th>#</th><th>Description</th><th>Qty</th><th>Unit</th><th>Unit Price</th><th>Total</th></tr></thead>
            <tbody>${items.map((item, i) => `
                <tr>
                    <td>${i+1}</td>
                    <td>${item.description || '--'}</td>
                    <td>${item.quantity || item.qty || 0}</td>
                    <td>${item.unit || 'ea'}</td>
                    <td>$${(parseFloat(item.unit_price) || 0).toFixed(2)}</td>
                    <td style="font-weight:700">$${(parseFloat(item.line_total) || 0).toFixed(2)}</td>
                </tr>`).join('')}
            </tbody>
        </table>
        <div class="po-total">Grand Total: $${total.toLocaleString(undefined, {minimumFractionDigits:2})}</div>`;
    } else {
        itemsHtml = '<p style="color:var(--tf-muted)">No line items</p>';
    }

    // Build status actions
    let actionsHtml = '';
    const s = po.status || 'draft';
    if (s === 'draft') {
        actionsHtml += `<button class="btn btn-sm btn-success" onclick="updatePOStatus('${id}','sent')">Send to Vendor</button>`;
        actionsHtml += `<button class="btn btn-sm btn-danger" onclick="updatePOStatus('${id}','cancelled')">Cancel PO</button>`;
    } else if (s === 'sent') {
        actionsHtml += `<button class="btn btn-sm btn-primary" onclick="updatePOStatus('${id}','acknowledged')">Mark Acknowledged</button>`;
        actionsHtml += `<button class="btn btn-sm btn-danger" onclick="updatePOStatus('${id}','cancelled')">Cancel PO</button>`;
    } else if (s === 'acknowledged') {
        actionsHtml += `<button class="btn btn-sm btn-primary" onclick="updatePOStatus('${id}','partial')">Partial Receipt</button>`;
        actionsHtml += `<button class="btn btn-sm btn-success" onclick="updatePOStatus('${id}','received')">Mark Fully Received</button>`;
    } else if (s === 'partial') {
        actionsHtml += `<button class="btn btn-sm btn-success" onclick="updatePOStatus('${id}','received')">Mark Fully Received</button>`;
    } else if (s === 'received') {
        actionsHtml += `<button class="btn btn-sm btn-secondary" onclick="updatePOStatus('${id}','closed')">Close PO</button>`;
    }
    actionsHtml += `<button class="btn btn-sm btn-secondary" onclick="closeModal('detail-modal')">Close</button>`;

    document.getElementById('detail-title').innerHTML = `${po.po_number || 'PO'} <span class="badge badge-${s}" style="font-size:12px;vertical-align:middle;margin-left:8px;">${s}</span>`;
    document.getElementById('detail-content').innerHTML = `
        <div class="detail-section">
            <h3>Order Information</h3>
            <div class="detail-grid">
                <div class="detail-item"><div class="detail-label">PO Number</div><div class="detail-value">${po.po_number || '--'}</div></div>
                <div class="detail-item"><div class="detail-label">Vendor</div><div class="detail-value">${po.vendor || '--'}</div></div>
                <div class="detail-item"><div class="detail-label">Project</div><div class="detail-value">${po.project || '--'}</div></div>
                <div class="detail-item"><div class="detail-label">Created</div><div class="detail-value">${(po.created || '').slice(0,10)}</div></div>
                <div class="detail-item"><div class="detail-label">Delivery Date</div><div class="detail-value">${po.delivery_date || '--'}</div></div>
                <div class="detail-item"><div class="detail-label">From MR</div><div class="detail-value">${po.from_mr || '--'}</div></div>
            </div>
        </div>
        <div class="detail-section">
            <h3>Line Items</h3>
            ${itemsHtml}
        </div>
        ${po.notes ? `<div class="detail-section"><h3>Notes</h3><p style="color:var(--tf-muted);font-size:14px;">${po.notes}</p></div>` : ''}
        <div class="detail-actions">${actionsHtml}</div>`;
    document.getElementById('detail-modal').classList.add('active');
}

async function updatePOStatus(id, newStatus) {
    try {
        const resp = await fetch('/api/pos', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({ action: 'update_status', po_id: id, status: newStatus })
        });
        const data = await resp.json();
        if (data.error) { showToast(data.error, 'error'); return; }
        closeModal('detail-modal');
        showToast('PO status updated to ' + newStatus, 'success');
        loadPOs();
    } catch(e) { showToast('Failed to update status', 'error'); }
}

// -- Create from MR --
async function openCreateFromMR() {
    try {
        const resp = await fetch('/api/mrs');
        const data = await resp.json();
        mrList = (data.material_reqs || []).filter(m => m.status === 'approved');
        const sel = document.getElementById('mr-select');
        if (mrList.length === 0) {
            sel.innerHTML = '<option value="">No approved MRs available</option>';
        } else {
            sel.innerHTML = '<option value="">Select an MR...</option>' + mrList.map(m =>
                `<option value="${m.id}">${m.mr_number || m.id} - ${m.project || 'No project'} (${(m.items || []).length} items)</option>`
            ).join('');
        }
        document.getElementById('mr-preview').style.display = 'none';
        sel.onchange = function() { previewMR(this.value); };
        document.getElementById('mr-modal').classList.add('active');
    } catch(e) { showToast('Failed to load MRs', 'error'); }
}

function previewMR(mrId) {
    const mr = mrList.find(m => m.id === mrId);
    const preview = document.getElementById('mr-preview');
    if (!mr) { preview.style.display = 'none'; return; }
    preview.style.display = 'block';
    const items = mr.items || [];
    document.getElementById('mr-preview-content').innerHTML = `
        <div class="detail-grid" style="margin-bottom:12px;">
            <div class="detail-item"><div class="detail-label">MR Number</div><div class="detail-value">${mr.mr_number || mr.id}</div></div>
            <div class="detail-item"><div class="detail-label">Project</div><div class="detail-value">${mr.project || '--'}</div></div>
            <div class="detail-item"><div class="detail-label">Priority</div><div class="detail-value">${mr.priority || 'normal'}</div></div>
            <div class="detail-item"><div class="detail-label">Items</div><div class="detail-value">${items.length}</div></div>
        </div>
        ${items.length > 0 ? `<table class="detail-line-items" style="border-radius:8px;overflow:hidden;border:1px solid rgba(255,255,255,0.06);">
            <thead><tr><th>Item</th><th>Qty</th><th>Unit</th></tr></thead>
            <tbody>${items.map(it => `<tr><td>${it.description || it.material || '--'}</td><td>${it.quantity || it.qty || 0}</td><td>${it.unit || 'ea'}</td></tr>`).join('')}</tbody>
        </table>` : ''}`;
}

async function convertMRtoPO() {
    const mrId = document.getElementById('mr-select').value;
    const vendor = document.getElementById('mr-vendor').value;
    if (!mrId) { showToast('Select an MR first', 'error'); return; }
    if (!vendor) { showToast('Select a vendor', 'error'); return; }
    try {
        const resp = await fetch('/api/pos', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({ action: 'create_from_mr', mr_id: mrId, vendor: vendor })
        });
        const data = await resp.json();
        if (data.error) { showToast(data.error, 'error'); return; }
        closeModal('mr-modal');
        showToast('PO created from MR: ' + (data.po_number || ''), 'success');
        loadPOs();
    } catch(e) { showToast('Failed to create PO from MR', 'error'); }
}

// Toast notification
function showToast(msg, type) {
    const existing = document.querySelector('.toast-notification');
    if (existing) existing.remove();
    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    const bg = type === 'error' ? 'var(--tf-red)' : type === 'success' ? 'var(--tf-green)' : 'var(--tf-blue)';
    toast.style.cssText = `position:fixed;top:20px;right:20px;z-index:9999;background:${bg};color:#fff;padding:14px 24px;border-radius:10px;font-size:14px;font-weight:600;box-shadow:0 4px 20px rgba(0,0,0,0.3);transition:opacity 0.3s;`;
    toast.textContent = msg;
    document.body.appendChild(toast);
    setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 300); }, 3000);
}

document.addEventListener('DOMContentLoaded', function() {
    loadPOs();
    loadVendors();
    loadProjects();
});
</script>
"""
