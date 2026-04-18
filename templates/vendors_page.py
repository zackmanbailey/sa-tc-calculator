"""
TitanForge v4 -- Vendor Management
=====================================
Vendor directory, contact info, rating/scoring, payment terms, active POs, performance metrics.
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

    .perf-bar { display: flex; align-items: center; gap: 8px; }
    .perf-bar .bar { flex: 1; height: 8px; background: rgba(255,255,255,0.06); border-radius: 4px; overflow: hidden; }
    .perf-bar .fill { height: 100%; border-radius: 4px; }
    .perf-bar .pct { font-size: 12px; font-weight: 700; min-width: 40px; text-align: right; }

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
            <div class="label">Active POs</div>
            <div class="value" id="stat-pos">0</div>
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
        <button class="btn btn-primary" onclick="openModal()">+ Add Vendor</button>
    </div>

    <div id="table-container">
        <table class="data-table">
            <thead>
                <tr>
                    <th>Vendor</th>
                    <th>Category</th>
                    <th>Contact</th>
                    <th>Phone</th>
                    <th>Payment Terms</th>
                    <th>Rating</th>
                    <th>On-Time %</th>
                    <th>Active POs</th>
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
            <button class="btn btn-primary" onclick="openModal()">+ Add Vendor</button>
        </div>
    </div>
</div>

<!-- Vendor Modal -->
<div class="modal-overlay" id="vendor-modal">
    <div class="modal">
        <h2 id="modal-title">Add New Vendor</h2>
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
            <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
            <button class="btn btn-primary" onclick="saveVendor()">Save Vendor</button>
        </div>
    </div>
</div>

<script>
let vendors = [];

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
    document.getElementById('stat-pos').textContent = vendors.reduce((s, v) => s + (v.active_pos || 0), 0);
}

function renderStars(rating) {
    const r = parseInt(rating) || 0;
    return '<span class="rating-stars">' + '&#9733;'.repeat(r) + '&#9734;'.repeat(5 - r) + '</span>';
}

function renderTable() {
    const tbody = document.getElementById('vendors-tbody');
    const empty = document.getElementById('empty-state');
    const filtered = getFiltered();
    if (filtered.length === 0) { tbody.innerHTML = ''; empty.style.display = 'block'; return; }
    empty.style.display = 'none';
    tbody.innerHTML = filtered.map(v => {
        const onTime = v.on_time_pct || 0;
        const barColor = onTime >= 90 ? 'var(--tf-green)' : onTime >= 70 ? 'var(--tf-orange)' : 'var(--tf-red)';
        return `<tr>
            <td><strong>${v.name || '--'}</strong></td>
            <td>${v.category || '--'}</td>
            <td>${v.contact || '--'}</td>
            <td>${v.phone || '--'}</td>
            <td>${v.payment_terms || '--'}</td>
            <td>${renderStars(v.rating)}</td>
            <td><div class="perf-bar"><div class="bar"><div class="fill" style="width:${onTime}%;background:${barColor}"></div></div><span class="pct">${onTime}%</span></div></td>
            <td>${v.active_pos || 0}</td>
            <td><span class="badge badge-${v.status || 'active'}">${v.status || 'active'}</span></td>
            <td><button class="btn btn-sm btn-secondary" onclick="editVendor('${v.id}')">Edit</button></td>
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
function openModal() { document.getElementById('vendor-modal').classList.add('active'); }
function closeModal() { document.getElementById('vendor-modal').classList.remove('active'); }
function editVendor(id) { document.getElementById('modal-title').textContent = 'Edit Vendor'; openModal(); }

async function saveVendor() {
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
    try {
        await fetch('/api/vendors', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
        closeModal();
        loadVendors();
    } catch(e) { console.error('Save failed:', e); }
}

document.addEventListener('DOMContentLoaded', loadVendors);
</script>
"""
