"""
TitanForge v4 -- Vendor Management
=====================================
Vendor directory with performance metrics, PO history, vendor comparison,
on-time delivery %, quality score, avg lead time, edit with pre-fill.
"""

VENDORS_PAGE_HTML = r"""
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
    .vendors-container {
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
    .badge-active { background: rgba(16,185,129,0.15); color: var(--tf-green); }
    .badge-inactive { background: rgba(148,163,184,0.15); color: var(--tf-muted); }
    .badge-preferred { background: rgba(212,168,67,0.15); color: var(--tf-gold); }
    .badge-warning { background: rgba(239,68,68,0.15); color: var(--tf-red); }

    .rating-stars { color: var(--tf-gold); font-size: 14px; letter-spacing: 2px; }

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

    .perf-bar { display: flex; align-items: center; gap: 8px; }
    .perf-bar .bar { flex: 1; height: 8px; background: rgba(255,255,255,0.06); border-radius: 4px; overflow: hidden; }
    .perf-bar .fill { height: 100%; border-radius: 4px; }
    .perf-bar .pct { font-size: 12px; font-weight: 700; min-width: 40px; text-align: right; }

    /* Vendor detail view */
    .vendor-detail-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
    .vendor-detail-header h3 { font-size: 22px; font-weight: 800; margin: 0 0 4px 0; }
    .vendor-detail-header .subtitle { font-size: 13px; color: var(--tf-muted); }
    .metrics-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; }
    .metric-card { background: var(--tf-bg); border-radius: 10px; padding: 16px; text-align: center; border: 1px solid rgba(255,255,255,0.06); }
    .metric-card .metric-value { font-size: 24px; font-weight: 800; margin-bottom: 4px; }
    .metric-card .metric-label { font-size: 11px; color: var(--tf-muted); text-transform: uppercase; }
    .detail-section { margin-bottom: 20px; }
    .detail-section h4 { font-size: 13px; font-weight: 700; color: var(--tf-gold); text-transform: uppercase; letter-spacing: 0.5px; margin: 0 0 10px 0; padding-bottom: 6px; border-bottom: 1px solid rgba(255,255,255,0.06); }
    .detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    .detail-item { font-size: 13px; }
    .detail-item .dl { color: var(--tf-muted); font-size: 11px; text-transform: uppercase; }
    .detail-item .dv { font-weight: 600; }

    .po-history-table { width: 100%; border-collapse: collapse; }
    .po-history-table th { padding: 8px 10px; font-size: 11px; color: var(--tf-muted); text-transform: uppercase; text-align: left; background: rgba(0,0,0,0.15); }
    .po-history-table td { padding: 8px 10px; font-size: 13px; border-bottom: 1px solid rgba(255,255,255,0.04); }

    /* Compare */
    .compare-section { margin-top: 16px; }
    .compare-check { display: inline-flex; align-items: center; gap: 6px; margin-right: 12px; font-size: 13px; cursor: pointer; }
    .compare-check input { accent-color: var(--tf-gold); width: 16px; height: 16px; }
    .compare-bar { display: flex; justify-content: flex-end; margin-bottom: 12px; }

/* Responsive */
@media (max-width: 768px) {
    .page-header h1 { font-size: 22px; }
    .toolbar { flex-direction: column; align-items: stretch; }
    .toolbar input[type="text"] { width: 100%; }
    .stat-row { grid-template-columns: 1fr 1fr; gap: 10px; }
    table { display: block; overflow-x: auto; -webkit-overflow-scrolling: touch; }
    .modal-overlay .modal, .modal { width: 95%; max-width: 95vw; margin: 20px auto; padding: 20px; }
    .form-row { grid-template-columns: 1fr; }
    .metrics-row { grid-template-columns: 1fr 1fr; }
    .detail-grid { grid-template-columns: 1fr; }
}
@media (max-width: 480px) {
    .stat-row { grid-template-columns: 1fr; }
    .toolbar { gap: 8px; }
    .metrics-row { grid-template-columns: 1fr; }
}
</style>

<div class="vendors-container">
    <div class="page-header">
        <h1>Vendor Management</h1>
        <p>Vendor directory, performance metrics, ratings, and procurement history</p>
    </div>

    <div class="stat-row">
        <div class="stat-card stat-gold">
            <div class="label">Total Vendors</div>
            <div class="value" id="stat-total">0</div>
        </div>
        <div class="stat-card stat-green">
            <div class="label">Active</div>
            <div class="value" id="stat-active">0</div>
        </div>
        <div class="stat-card stat-blue">
            <div class="label">Preferred</div>
            <div class="value" id="stat-preferred">0</div>
        </div>
        <div class="stat-card stat-gold">
            <div class="label">Total Spend</div>
            <div class="value" id="stat-spend">$0</div>
        </div>
    </div>

    <div class="toolbar">
        <div class="toolbar-left">
            <input type="text" id="search-input" placeholder="Search vendors..." oninput="filterTable()">
            <select id="status-filter" onchange="filterTable()">
                <option value="">All Statuses</option>
                <option value="active">Active</option>
                <option value="preferred">Preferred</option>
                <option value="inactive">Inactive</option>
                <option value="warning">Under Review</option>
            </select>
            <select id="category-filter" onchange="filterTable()">
                <option value="">All Categories</option>
                <option value="steel">Steel Supplier</option>
                <option value="hardware">Hardware</option>
                <option value="coatings">Coatings/Paint</option>
                <option value="accessories">Accessories</option>
                <option value="services">Services</option>
            </select>
        </div>
        <div style="display:flex;gap:10px;">
            <button class="btn btn-secondary" id="compare-btn" style="display:none;" onclick="compareVendors()">Compare Selected</button>
            <button class="btn btn-primary" onclick="openAddModal()">+ Add Vendor</button>
        </div>
    </div>

    <div id="table-container">
        <table class="data-table">
            <thead>
                <tr>
                    <th style="width:30px;"><input type="checkbox" id="select-all" onchange="toggleSelectAll(this)" style="accent-color:var(--tf-gold);width:16px;height:16px;"></th>
                    <th>Vendor</th>
                    <th>Category</th>
                    <th>Contact</th>
                    <th>Rating</th>
                    <th>On-Time %</th>
                    <th>Quality</th>
                    <th>Avg Lead Time</th>
                    <th>Active POs</th>
                    <th>Total Spend</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody id="vendors-tbody"></tbody>
        </table>
        <div class="empty-state" id="empty-state">
            <div class="icon">&#x1F3ED;</div>
            <h3>No Vendors Found</h3>
            <p>Add your material suppliers and service vendors to track performance and manage procurement.</p>
            <button class="btn btn-primary" onclick="openAddModal()">+ Add Vendor</button>
        </div>
    </div>
</div>

<!-- Add/Edit Vendor Modal -->
<div class="modal-overlay" id="vendor-modal">
    <div class="modal">
        <h2 id="modal-title">Add New Vendor</h2>
        <input type="hidden" id="vendor-edit-id" value="">
        <div class="form-row">
            <div class="form-group">
                <label>Company Name</label>
                <input type="text" id="vendor-name" placeholder="Vendor company name">
            </div>
            <div class="form-group">
                <label>Category</label>
                <select id="vendor-category">
                    <option value="">Select...</option>
                    <option value="steel">Steel Supplier</option>
                    <option value="hardware">Hardware</option>
                    <option value="coatings">Coatings/Paint</option>
                    <option value="accessories">Accessories</option>
                    <option value="services">Services</option>
                </select>
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Primary Contact</label>
                <input type="text" id="vendor-contact" placeholder="Contact name">
            </div>
            <div class="form-group">
                <label>Email</label>
                <input type="email" id="vendor-email" placeholder="email@vendor.com">
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Phone</label>
                <input type="tel" id="vendor-phone" placeholder="(555) 123-4567">
            </div>
            <div class="form-group">
                <label>Payment Terms</label>
                <select id="vendor-terms">
                    <option value="net30">Net 30</option>
                    <option value="net15">Net 15</option>
                    <option value="net45">Net 45</option>
                    <option value="net60">Net 60</option>
                    <option value="cod">COD</option>
                    <option value="prepaid">Prepaid</option>
                </select>
            </div>
        </div>
        <div class="form-group">
            <label>Address</label>
            <textarea id="vendor-address" rows="2" placeholder="Full address"></textarea>
        </div>
        <div class="form-row-3">
            <div class="form-group">
                <label>Rating (1-5)</label>
                <select id="vendor-rating">
                    <option value="5">5 - Excellent</option>
                    <option value="4">4 - Good</option>
                    <option value="3">3 - Average</option>
                    <option value="2">2 - Below Average</option>
                    <option value="1">1 - Poor</option>
                </select>
            </div>
            <div class="form-group">
                <label>Status</label>
                <select id="vendor-status">
                    <option value="active">Active</option>
                    <option value="preferred">Preferred</option>
                    <option value="inactive">Inactive</option>
                    <option value="warning">Under Review</option>
                </select>
            </div>
            <div class="form-group">
                <label>Tax ID / EIN</label>
                <input type="text" id="vendor-tax" placeholder="XX-XXXXXXX">
            </div>
        </div>
        <div class="form-group">
            <label>Notes</label>
            <textarea id="vendor-notes" rows="3" placeholder="Vendor notes, specialties, etc."></textarea>
        </div>
        <div class="modal-actions">
            <button class="btn btn-secondary" onclick="closeModal('vendor-modal')">Cancel</button>
            <button class="btn btn-primary" id="vendor-save-btn" onclick="saveVendor()">Save Vendor</button>
        </div>
    </div>
</div>

<!-- Vendor Detail Modal -->
<div class="modal-overlay" id="detail-modal">
    <div class="modal" style="max-width:850px;">
        <div id="detail-content"></div>
        <div class="modal-actions">
            <button class="btn btn-secondary" onclick="closeModal('detail-modal')">Close</button>
        </div>
    </div>
</div>

<!-- Compare Modal -->
<div class="modal-overlay" id="compare-modal">
    <div class="modal" style="max-width:900px;">
        <h2>Vendor Comparison</h2>
        <div id="compare-content"></div>
        <div class="modal-actions">
            <button class="btn btn-secondary" onclick="closeModal('compare-modal')">Close</button>
        </div>
    </div>
</div>

<script>
let vendors = [];
let selectedForCompare = new Set();

async function loadVendors() {
    try {
        const resp = await fetch('/api/vendors');
        const data = await resp.json();
        vendors = data.vendors || [];
        renderTable();
        updateStats();
    } catch(e) { console.error('Failed to load vendors:', e); renderTable(); }
}

function updateStats() {
    document.getElementById('stat-total').textContent = vendors.length;
    document.getElementById('stat-active').textContent = vendors.filter(v => v.status === 'active' || v.status === 'preferred').length;
    document.getElementById('stat-preferred').textContent = vendors.filter(v => v.status === 'preferred').length;
    const totalSpend = vendors.reduce((s, v) => s + (parseFloat(v.total_spend) || 0), 0);
    document.getElementById('stat-spend').textContent = '$' + totalSpend.toLocaleString(undefined, {minimumFractionDigits:0, maximumFractionDigits:0});
}

function renderStars(rating) {
    const r = parseInt(rating) || 0;
    return '<span class="rating-stars">' + '&#9733;'.repeat(r) + '&#9734;'.repeat(5 - r) + '</span>';
}

function qualityColor(score) {
    const s = parseFloat(score) || 0;
    if (s >= 90) return 'var(--tf-green)';
    if (s >= 70) return 'var(--tf-orange)';
    return 'var(--tf-red)';
}

function renderTable() {
    const tbody = document.getElementById('vendors-tbody');
    const empty = document.getElementById('empty-state');
    const filtered = getFiltered();
    if (filtered.length === 0) { tbody.innerHTML = ''; empty.style.display = 'block'; return; }
    empty.style.display = 'none';
    tbody.innerHTML = filtered.map(v => {
        const onTime = parseFloat(v.on_time_pct) || 0;
        const quality = parseFloat(v.quality_score) || 0;
        const leadTime = v.avg_lead_time || '--';
        const barColor = onTime >= 90 ? 'var(--tf-green)' : onTime >= 70 ? 'var(--tf-orange)' : 'var(--tf-red)';
        const checked = selectedForCompare.has(v.id) ? 'checked' : '';
        return `<tr>
            <td onclick="event.stopPropagation()"><input type="checkbox" ${checked} onchange="toggleCompare('${v.id}', this.checked)" style="accent-color:var(--tf-gold);width:16px;height:16px;"></td>
            <td onclick="viewVendor('${v.id}')"><strong>${v.name || '--'}</strong></td>
            <td>${v.category || '--'}</td>
            <td>${v.contact || '--'}<br><span style="font-size:11px;color:var(--tf-muted)">${v.phone || ''}</span></td>
            <td>${renderStars(v.rating)}</td>
            <td><div class="perf-bar"><div class="bar"><div class="fill" style="width:${onTime}%;background:${barColor}"></div></div><span class="pct">${onTime}%</span></div></td>
            <td><span style="color:${qualityColor(quality)};font-weight:700">${quality > 0 ? quality.toFixed(0) + '%' : '--'}</span></td>
            <td>${leadTime !== '--' ? leadTime + ' days' : '--'}</td>
            <td>${v.active_pos || 0}</td>
            <td style="font-weight:600">$${(parseFloat(v.total_spend) || 0).toLocaleString()}</td>
            <td><span class="badge badge-${v.status || 'active'}">${v.status || 'active'}</span></td>
            <td>
                <button class="btn btn-sm btn-secondary" onclick="event.stopPropagation();editVendor('${v.id}')" style="margin-right:4px;">Edit</button>
                <button class="btn btn-sm btn-primary" onclick="event.stopPropagation();newPOForVendor('${v.name}')" style="font-size:11px;">New PO</button>
            </td>
        </tr>`;
    }).join('');
}

function getFiltered() {
    const search = (document.getElementById('search-input').value || '').toLowerCase();
    const status = document.getElementById('status-filter').value;
    const cat = document.getElementById('category-filter').value;
    return vendors.filter(v => {
        if (search && !JSON.stringify(v).toLowerCase().includes(search)) return false;
        if (status && v.status !== status) return false;
        if (cat && v.category !== cat) return false;
        return true;
    });
}

function filterTable() { renderTable(); }

function openAddModal() {
    document.getElementById('modal-title').textContent = 'Add New Vendor';
    document.getElementById('vendor-save-btn').textContent = 'Save Vendor';
    document.getElementById('vendor-edit-id').value = '';
    ['vendor-name','vendor-contact','vendor-email','vendor-phone','vendor-address','vendor-tax','vendor-notes'].forEach(id => {
        document.getElementById(id).value = '';
    });
    document.getElementById('vendor-category').value = '';
    document.getElementById('vendor-terms').value = 'net30';
    document.getElementById('vendor-rating').value = '5';
    document.getElementById('vendor-status').value = 'active';
    document.getElementById('vendor-modal').classList.add('active');
}

function closeModal(id) { document.getElementById(id).classList.remove('active'); }

function editVendor(id) {
    const v = vendors.find(x => x.id === id);
    if (!v) return;
    document.getElementById('modal-title').textContent = 'Edit Vendor';
    document.getElementById('vendor-save-btn').textContent = 'Update Vendor';
    document.getElementById('vendor-edit-id').value = id;
    document.getElementById('vendor-name').value = v.name || '';
    document.getElementById('vendor-category').value = v.category || '';
    document.getElementById('vendor-contact').value = v.contact || '';
    document.getElementById('vendor-email').value = v.email || '';
    document.getElementById('vendor-phone').value = v.phone || '';
    document.getElementById('vendor-terms').value = v.payment_terms || 'net30';
    document.getElementById('vendor-address').value = v.address || '';
    document.getElementById('vendor-rating').value = v.rating || '5';
    document.getElementById('vendor-status').value = v.status || 'active';
    document.getElementById('vendor-tax').value = v.tax_id || '';
    document.getElementById('vendor-notes').value = v.notes || '';
    document.getElementById('vendor-modal').classList.add('active');
}

async function saveVendor() {
    const editId = document.getElementById('vendor-edit-id').value;
    const payload = {
        name: document.getElementById('vendor-name').value,
        category: document.getElementById('vendor-category').value,
        contact: document.getElementById('vendor-contact').value,
        email: document.getElementById('vendor-email').value,
        phone: document.getElementById('vendor-phone').value,
        payment_terms: document.getElementById('vendor-terms').value,
        address: document.getElementById('vendor-address').value,
        rating: document.getElementById('vendor-rating').value,
        status: document.getElementById('vendor-status').value,
        tax_id: document.getElementById('vendor-tax').value,
        notes: document.getElementById('vendor-notes').value,
    };
    if (!payload.name) { showToast('Vendor name is required', 'error'); return; }

    if (editId) {
        payload.action = 'edit';
        payload.vendor_id = editId;
    }

    try {
        const resp = await fetch('/api/vendors', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
        const data = await resp.json();
        if (data.error) { showToast(data.error, 'error'); return; }
        closeModal('vendor-modal');
        showToast(editId ? 'Vendor updated' : 'Vendor added', 'success');
        loadVendors();
    } catch(e) { showToast('Save failed', 'error'); }
}

function viewVendor(id) {
    const v = vendors.find(x => x.id === id);
    if (!v) return;

    const onTime = parseFloat(v.on_time_pct) || 0;
    const quality = parseFloat(v.quality_score) || 0;
    const leadTime = v.avg_lead_time || '--';
    const totalSpend = parseFloat(v.total_spend) || 0;

    // PO history
    const poHistory = v.po_history || [];
    let poHistoryHtml = '';
    if (poHistory.length > 0) {
        poHistoryHtml = `<table class="po-history-table" style="border-radius:8px;overflow:hidden;border:1px solid rgba(255,255,255,0.06);">
            <thead><tr><th>PO #</th><th>Date</th><th>Total</th><th>Status</th></tr></thead>
            <tbody>${poHistory.map(po => `
                <tr>
                    <td><strong>${po.po_number || '--'}</strong></td>
                    <td>${(po.created || '').slice(0,10)}</td>
                    <td>$${(parseFloat(po.total) || parseFloat(po.grand_total) || 0).toLocaleString()}</td>
                    <td><span class="badge badge-${po.status || 'draft'}">${po.status || 'draft'}</span></td>
                </tr>`).join('')}
            </tbody>
        </table>`;
    } else {
        poHistoryHtml = '<p style="color:var(--tf-muted);font-size:13px;">No purchase order history</p>';
    }

    document.getElementById('detail-content').innerHTML = `
        <div class="vendor-detail-header">
            <div>
                <h3>${v.name || 'Vendor'}</h3>
                <div class="subtitle">${v.category || '--'} &bull; ${renderStars(v.rating)} &bull; <span class="badge badge-${v.status || 'active'}">${v.status || 'active'}</span></div>
            </div>
            <div style="display:flex;gap:8px;">
                <button class="btn btn-sm btn-secondary" onclick="closeModal('detail-modal');editVendor('${id}')">Edit</button>
                <button class="btn btn-sm btn-primary" onclick="closeModal('detail-modal');newPOForVendor('${v.name}')">New PO</button>
            </div>
        </div>

        <div class="metrics-row">
            <div class="metric-card">
                <div class="metric-value" style="color:${onTime >= 90 ? 'var(--tf-green)' : onTime >= 70 ? 'var(--tf-orange)' : 'var(--tf-red)'}">${onTime}%</div>
                <div class="metric-label">On-Time Delivery</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color:${qualityColor(quality)}">${quality > 0 ? quality.toFixed(0) + '%' : '--'}</div>
                <div class="metric-label">Quality Score</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color:var(--tf-blue)">${leadTime !== '--' ? leadTime : '--'}</div>
                <div class="metric-label">Avg Lead Time (days)</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color:var(--tf-gold)">$${totalSpend.toLocaleString()}</div>
                <div class="metric-label">Total Spend</div>
            </div>
        </div>

        <div class="detail-section">
            <h4>Contact Information</h4>
            <div class="detail-grid">
                <div class="detail-item"><div class="dl">Contact</div><div class="dv">${v.contact || '--'}</div></div>
                <div class="detail-item"><div class="dl">Email</div><div class="dv">${v.email || '--'}</div></div>
                <div class="detail-item"><div class="dl">Phone</div><div class="dv">${v.phone || '--'}</div></div>
                <div class="detail-item"><div class="dl">Payment Terms</div><div class="dv">${v.payment_terms || '--'}</div></div>
                <div class="detail-item"><div class="dl">Address</div><div class="dv">${v.address || '--'}</div></div>
                <div class="detail-item"><div class="dl">Tax ID</div><div class="dv">${v.tax_id || '--'}</div></div>
            </div>
        </div>

        <div class="detail-section">
            <h4>Purchase Order History (${poHistory.length})</h4>
            ${poHistoryHtml}
        </div>

        ${v.notes ? `<div class="detail-section"><h4>Notes</h4><p style="color:var(--tf-muted);font-size:14px;">${v.notes}</p></div>` : ''}`;

    document.getElementById('detail-modal').classList.add('active');
}

// Compare vendors
function toggleCompare(id, checked) {
    if (checked) selectedForCompare.add(id);
    else selectedForCompare.delete(id);
    document.getElementById('compare-btn').style.display = selectedForCompare.size >= 2 ? 'inline-block' : 'none';
}

function toggleSelectAll(el) {
    const checkboxes = document.querySelectorAll('#vendors-tbody input[type=checkbox]');
    checkboxes.forEach(cb => { cb.checked = el.checked; });
    if (el.checked) {
        getFiltered().forEach(v => selectedForCompare.add(v.id));
    } else {
        selectedForCompare.clear();
    }
    document.getElementById('compare-btn').style.display = selectedForCompare.size >= 2 ? 'inline-block' : 'none';
}

function compareVendors() {
    const selected = vendors.filter(v => selectedForCompare.has(v.id));
    if (selected.length < 2) { showToast('Select at least 2 vendors to compare', 'error'); return; }

    const metrics = ['on_time_pct', 'quality_score', 'avg_lead_time', 'total_spend', 'rating', 'active_pos'];
    const labels = { on_time_pct: 'On-Time %', quality_score: 'Quality Score', avg_lead_time: 'Avg Lead Time (days)', total_spend: 'Total Spend', rating: 'Rating', active_pos: 'Active POs' };

    let html = `<table class="po-history-table" style="border-radius:8px;overflow:hidden;border:1px solid rgba(255,255,255,0.06);width:100%;">
        <thead><tr><th>Metric</th>${selected.map(v => `<th>${v.name}</th>`).join('')}</tr></thead>
        <tbody>`;

    metrics.forEach(m => {
        const values = selected.map(v => parseFloat(v[m]) || 0);
        const best = m === 'avg_lead_time' ? Math.min(...values.filter(x => x > 0)) : Math.max(...values);
        html += `<tr><td style="font-weight:700">${labels[m]}</td>`;
        selected.forEach(v => {
            const val = parseFloat(v[m]) || 0;
            const isBest = val === best && val > 0;
            const display = m === 'total_spend' ? '$' + val.toLocaleString() : m === 'on_time_pct' || m === 'quality_score' ? val + '%' : val;
            html += `<td style="${isBest ? 'color:var(--tf-green);font-weight:700' : ''}">${display}</td>`;
        });
        html += '</tr>';
    });

    // Stars row
    html += `<tr><td style="font-weight:700">Rating</td>`;
    selected.forEach(v => { html += `<td>${renderStars(v.rating)}</td>`; });
    html += '</tr>';

    html += `<tr><td style="font-weight:700">Status</td>`;
    selected.forEach(v => { html += `<td><span class="badge badge-${v.status}">${v.status}</span></td>`; });
    html += '</tr></tbody></table>';

    document.getElementById('compare-content').innerHTML = html;
    document.getElementById('compare-modal').classList.add('active');
}

function newPOForVendor(vendorName) {
    window.location.href = '/purchase-orders';
    // Store in sessionStorage so PO page can pick it up
    sessionStorage.setItem('prefill_po_vendor', vendorName);
}

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

document.addEventListener('DOMContentLoaded', loadVendors);
</script>
"""
