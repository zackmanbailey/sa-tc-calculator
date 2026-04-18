"""
TitanForge v4 -- Price Lists
==============================
Material pricing, vendor price comparison, price history, markup calculator, bulk update.
"""

PRICES_PAGE_HTML = r"""
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
    .prices-container {
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
    .form-row-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 24px; }

    .price-change { font-size: 12px; font-weight: 600; }
    .price-up { color: var(--tf-red); }
    .price-down { color: var(--tf-green); }
    .price-flat { color: var(--tf-muted); }

    .markup-calc {
        background: var(--tf-bg); border-radius: 12px; padding: 20px; margin-top: 16px;
        border: 1px solid rgba(255,255,255,0.06);
    }
    .markup-calc h3 { font-size: 14px; font-weight: 700; margin: 0 0 12px 0; color: var(--tf-gold); }
    .markup-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; align-items: end; }
    .markup-result { font-size: 24px; font-weight: 800; color: var(--tf-gold); }

/* ── Responsive ── */
@media (max-width: 768px) {
    .page-header h1 { font-size: 22px; }
    .toolbar { flex-direction: column; align-items: stretch; }
    .toolbar input[type="text"] { width: 100%; }
    .stat-row { grid-template-columns: 1fr 1fr; gap: 10px; }
    table { display: block; overflow-x: auto; -webkit-overflow-scrolling: touch; }
    .modal-overlay .modal, .modal { width: 95%; max-width: 95vw; margin: 20px auto; padding: 20px; }
    .form-row { grid-template-columns: 1fr; }
    .markup-row { flex-direction: column; gap: 8px; }
}
@media (max-width: 480px) {
    .stat-row { grid-template-columns: 1fr; }
    .toolbar { gap: 8px; }
}
</style>

<div class="prices-container">
    <div class="page-header">
        <h1>Price Lists</h1>
        <p>Material pricing, vendor comparisons, price history, and markup calculations</p>
    </div>

    <div class="stat-row">
        <div class="stat-card stat-gold">
            <div class="label">Materials Tracked</div>
            <div class="value" id="stat-total">0</div>
        </div>
        <div class="stat-card stat-blue">
            <div class="label">Vendors</div>
            <div class="value" id="stat-vendors">0</div>
        </div>
        <div class="stat-card stat-green">
            <div class="label">Prices Down</div>
            <div class="value" id="stat-down">0</div>
        </div>
        <div class="stat-card stat-red">
            <div class="label">Prices Up</div>
            <div class="value" id="stat-up">0</div>
        </div>
    </div>

    <div class="toolbar">
        <div class="toolbar-left">
            <input type="text" id="search-input" placeholder="Search materials..." oninput="filterTable()">
            <select id="category-filter" onchange="filterTable()">
                <option value="">All Categories</option>
                <option value="coil">Coil Steel</option>
                <option value="structural">Structural Steel</option>
                <option value="hardware">Hardware</option>
                <option value="accessories">Accessories</option>
                <option value="paint">Paint / Coatings</option>
            </select>
            <select id="vendor-filter" onchange="filterTable()">
                <option value="">All Vendors</option>
            </select>
        </div>
        <div style="display:flex;gap:10px;">
            <button class="btn btn-secondary" onclick="openMarkupCalc()">Markup Calculator</button>
            <button class="btn btn-primary" onclick="openModal()">+ Add Price</button>
        </div>
    </div>

    <div id="table-container">
        <table class="data-table">
            <thead>
                <tr>
                    <th>Material</th>
                    <th>Category</th>
                    <th>Unit</th>
                    <th>Base Price</th>
                    <th>Vendor</th>
                    <th>Last Updated</th>
                    <th>Trend</th>
                    <th>Markup %</th>
                    <th>Sell Price</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody id="prices-tbody"></tbody>
        </table>
        <div class="empty-state" id="empty-state">
            <div class="icon">&#x1F4B2;</div>
            <h3>No Price Data</h3>
            <p>Add material pricing to track costs, compare vendors, and calculate markups.</p>
            <button class="btn btn-primary" onclick="openModal()">+ Add Price</button>
        </div>
    </div>

    <!-- Markup Calculator -->
    <div class="markup-calc" id="markup-calc" style="display:none;">
        <h3>Quick Markup Calculator</h3>
        <div class="markup-row">
            <div class="form-group">
                <label>Cost Price ($)</label>
                <input type="number" id="calc-cost" placeholder="0.00" oninput="calculateMarkup()">
            </div>
            <div class="form-group">
                <label>Markup %</label>
                <input type="number" id="calc-markup" placeholder="25" value="25" oninput="calculateMarkup()">
            </div>
            <div class="form-group">
                <label>Sell Price</label>
                <div class="markup-result" id="calc-result">$0.00</div>
            </div>
        </div>
    </div>
</div>

<!-- Price Modal -->
<div class="modal-overlay" id="price-modal">
    <div class="modal">
        <h2 id="modal-title">Add Material Price</h2>
        <div class="form-row">
            <div class="form-group">
                <label>Material</label>
                <input type="text" id="price-material" placeholder="e.g., 26ga Galvalume Coil">
            </div>
            <div class="form-group">
                <label>Category</label>
                <select id="price-category">
                    <option value="">Select...</option>
                    <option value="coil">Coil Steel</option>
                    <option value="structural">Structural Steel</option>
                    <option value="hardware">Hardware</option>
                    <option value="accessories">Accessories</option>
                    <option value="paint">Paint / Coatings</option>
                </select>
            </div>
        </div>
        <div class="form-row-3">
            <div class="form-group">
                <label>Base Price ($)</label>
                <input type="number" id="price-base" placeholder="0.00" step="0.01">
            </div>
            <div class="form-group">
                <label>Unit</label>
                <select id="price-unit">
                    <option value="lb">Per Pound</option>
                    <option value="ft">Per Foot</option>
                    <option value="ea">Each</option>
                    <option value="ton">Per Ton</option>
                    <option value="sqft">Per Sq Ft</option>
                </select>
            </div>
            <div class="form-group">
                <label>Default Markup %</label>
                <input type="number" id="price-markup" placeholder="25" value="25">
            </div>
        </div>
        <div class="form-group">
            <label>Vendor</label>
            <input type="text" id="price-vendor" placeholder="Vendor name">
        </div>
        <div class="form-group">
            <label>Notes</label>
            <textarea id="price-notes" rows="2" placeholder="Price notes, min order qty, etc."></textarea>
        </div>
        <div class="modal-actions">
            <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
            <button class="btn btn-primary" onclick="savePrice()">Save Price</button>
        </div>
    </div>
</div>

<script>
let prices = [];

async function loadPrices() {
    try {
        const resp = await fetch('/api/prices');
        const data = await resp.json();
        prices = data.prices || [];
        renderTable();
        updateStats();
    } catch(e) { console.error('Failed to load prices:', e); renderTable(); }
}

function updateStats() {
    document.getElementById('stat-total').textContent = prices.length;
    const vendors = new Set(prices.map(p => p.vendor)).size;
    document.getElementById('stat-vendors').textContent = vendors;
    document.getElementById('stat-up').textContent = prices.filter(p => p.trend === 'up').length;
    document.getElementById('stat-down').textContent = prices.filter(p => p.trend === 'down').length;
}

function renderTable() {
    const tbody = document.getElementById('prices-tbody');
    const empty = document.getElementById('empty-state');
    const filtered = getFiltered();
    if (filtered.length === 0) { tbody.innerHTML = ''; empty.style.display = 'block'; return; }
    empty.style.display = 'none';
    tbody.innerHTML = filtered.map(p => {
        const sell = (p.base_price || 0) * (1 + (p.markup || 25) / 100);
        const trendClass = p.trend === 'up' ? 'price-up' : p.trend === 'down' ? 'price-down' : 'price-flat';
        const trendIcon = p.trend === 'up' ? '&#9650;' : p.trend === 'down' ? '&#9660;' : '&#9644;';
        return `<tr>
            <td><strong>${p.material || '--'}</strong></td>
            <td>${p.category || '--'}</td>
            <td>${p.unit || '--'}</td>
            <td>$${(p.base_price || 0).toFixed(2)}</td>
            <td>${p.vendor || '--'}</td>
            <td>${p.last_updated || '--'}</td>
            <td><span class="price-change ${trendClass}">${trendIcon} ${p.change || '0%'}</span></td>
            <td>${p.markup || 25}%</td>
            <td style="color:var(--tf-gold);font-weight:700">$${sell.toFixed(2)}</td>
            <td><button class="btn btn-sm btn-secondary" onclick="editPrice('${p.id}')">Edit</button></td>
        </tr>`;
    }).join('');
}

function getFiltered() {
    const search = (document.getElementById('search-input').value || '').toLowerCase();
    const cat = document.getElementById('category-filter').value;
    const vendor = document.getElementById('vendor-filter').value;
    return prices.filter(p => {
        if (search && !JSON.stringify(p).toLowerCase().includes(search)) return false;
        if (cat && p.category !== cat) return false;
        if (vendor && p.vendor !== vendor) return false;
        return true;
    });
}

function filterTable() { renderTable(); }
function openModal() { document.getElementById('price-modal').classList.add('active'); }
function closeModal() { document.getElementById('price-modal').classList.remove('active'); }
function editPrice(id) { openModal(); }

function openMarkupCalc() {
    const el = document.getElementById('markup-calc');
    el.style.display = el.style.display === 'none' ? 'block' : 'none';
}

function calculateMarkup() {
    const cost = parseFloat(document.getElementById('calc-cost').value) || 0;
    const markup = parseFloat(document.getElementById('calc-markup').value) || 0;
    const sell = cost * (1 + markup / 100);
    document.getElementById('calc-result').textContent = '$' + sell.toFixed(2);
}

async function savePrice() {
    const payload = {
        material: document.getElementById('price-material').value,
        category: document.getElementById('price-category').value,
        base_price: document.getElementById('price-base').value,
        unit: document.getElementById('price-unit').value,
        markup: document.getElementById('price-markup').value,
        vendor: document.getElementById('price-vendor').value,
        notes: document.getElementById('price-notes').value,
    };
    try {
        await fetch('/api/prices', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
        closeModal();
        loadPrices();
    } catch(e) { console.error('Save failed:', e); }
}

document.addEventListener('DOMContentLoaded', loadPrices);
</script>
"""
