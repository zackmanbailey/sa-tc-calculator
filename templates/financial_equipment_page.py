"""
TitanForge v4 — Equipment Cost Tracking
=========================================
Equipment cost tracking, depreciation, and maintenance costs.
"""

FINANCIAL_EQUIPMENT_PAGE_HTML = r"""
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
    }
    .eq-container {
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
        padding: 20px 24px; transition: border-color 0.2s, transform 0.15s;
    }
    .stat-card:hover { border-color: var(--tf-gold); transform: translateY(-2px); }
    .stat-card .label { font-size: 12px; color: var(--tf-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
    .stat-card .value { font-size: 28px; font-weight: 800; }
    .stat-card .sub { font-size: 12px; color: var(--tf-muted); margin-top: 4px; }
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
    .toolbar input[type="text"] { width: 260px; }
    .toolbar input::placeholder { color: var(--tf-muted); }
    .toolbar select { cursor: pointer; }
    .btn-gold {
        background: var(--tf-gold); color: #0f172a; border: none; border-radius: 8px;
        padding: 10px 20px; font-weight: 700; font-size: 14px; cursor: pointer;
    }
    .btn-gold:hover { opacity: 0.9; }

    .table-card {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06); overflow: hidden;
    }
    .eq-table { width: 100%; border-collapse: collapse; font-size: 14px; }
    .eq-table th {
        text-align: left; padding: 14px 16px; font-size: 11px;
        text-transform: uppercase; letter-spacing: 0.5px; color: var(--tf-muted);
        border-bottom: 1px solid rgba(255,255,255,0.06); font-weight: 600;
    }
    .eq-table td {
        padding: 14px 16px; border-bottom: 1px solid rgba(255,255,255,0.04); vertical-align: middle;
    }
    .eq-table tr:hover { background: rgba(255,255,255,0.02); }
    .eq-table tr:last-child td { border-bottom: none; }

    .badge {
        display: inline-block; padding: 4px 10px; border-radius: 20px;
        font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;
    }
    .badge-active { background: rgba(16,185,129,0.15); color: #34d399; }
    .badge-maintenance { background: rgba(212,168,67,0.15); color: #d4a843; }
    .badge-retired { background: rgba(148,163,184,0.15); color: #94a3b8; }

    .depreciation-bar {
        height: 6px; background: rgba(255,255,255,0.06); border-radius: 3px; overflow: hidden; width: 100px;
    }
    .depreciation-fill { height: 100%; border-radius: 3px; background: var(--tf-blue); }

    .empty-state { text-align: center; padding: 60px 20px; color: var(--tf-muted); }
    .empty-state h3 { color: var(--tf-text); margin-bottom: 8px; }

    .modal-overlay {
        display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.6); z-index: 9999; justify-content: center; align-items: center;
    }
    .modal-overlay.active { display: flex; }
    .modal {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.1); padding: 32px;
        width: 580px; max-width: 95vw; max-height: 90vh; overflow-y: auto;
    }
    .modal h2 { margin: 0 0 24px 0; font-size: 20px; font-weight: 700; }
    .form-group { margin-bottom: 16px; }
    .form-group label {
        display: block; font-size: 12px; color: var(--tf-muted);
        text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; font-weight: 600;
    }
    .form-group input, .form-group select, .form-group textarea {
        width: 100%; background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px;
        font-family: inherit; box-sizing: border-box;
    }
    .form-group textarea { resize: vertical; min-height: 80px; }
    .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 24px; }
    .btn-secondary {
        background: transparent; border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px; padding: 10px 20px; color: var(--tf-muted);
        font-weight: 600; font-size: 14px; cursor: pointer;
    }
    .btn-secondary:hover { color: var(--tf-text); border-color: rgba(255,255,255,0.2); }

/* ── Responsive ── */
@media (max-width: 768px) {
    .page-header h1 { font-size: 22px; }
    .toolbar { flex-direction: column; align-items: stretch; }
    .toolbar input[type="text"] { width: 100%; }
    .stat-row { grid-template-columns: 1fr 1fr; gap: 10px; }
    .modal-overlay .modal, .modal { width: 95%; max-width: 95vw; margin: 20px auto; padding: 20px; }
    .form-row { grid-template-columns: 1fr; }
    .eq-table { display: block; overflow-x: auto; -webkit-overflow-scrolling: touch; }
}
@media (max-width: 480px) {
    .stat-row { grid-template-columns: 1fr; }
    .toolbar { gap: 8px; }
}
</style>

<div class="eq-container">
    <div class="page-header">
        <h1>Equipment Costs</h1>
        <p>Track equipment purchases, depreciation, and maintenance expenses</p>
    </div>

    <div class="stat-row">
        <div class="stat-card stat-gold">
            <div class="label">Total Asset Value</div>
            <div class="value" id="stat-value">$0</div>
            <div class="sub">Original cost</div>
        </div>
        <div class="stat-card stat-blue">
            <div class="label">Current Book Value</div>
            <div class="value" id="stat-book">$0</div>
            <div class="sub">After depreciation</div>
        </div>
        <div class="stat-card stat-red">
            <div class="label">Maintenance Costs</div>
            <div class="value" id="stat-maintenance">$0</div>
            <div class="sub">Year to date</div>
        </div>
        <div class="stat-card stat-green">
            <div class="label">Active Equipment</div>
            <div class="value" id="stat-active">0</div>
            <div class="sub">In service</div>
        </div>
    </div>

    <div class="toolbar">
        <div class="toolbar-left">
            <input type="text" id="searchInput" placeholder="Search equipment..." oninput="applyFilters()">
            <select id="statusFilter" onchange="applyFilters()">
                <option value="">All Status</option>
                <option value="active">Active</option>
                <option value="maintenance">In Maintenance</option>
                <option value="retired">Retired</option>
            </select>
        </div>
        <button class="btn-gold" onclick="openModal()">+ Add Equipment</button>
    </div>

    <div class="table-card">
        <table class="eq-table">
            <thead>
                <tr>
                    <th>Equipment</th>
                    <th>Category</th>
                    <th>Purchase Cost</th>
                    <th>Book Value</th>
                    <th>Depreciation</th>
                    <th>Maintenance YTD</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody id="equipmentBody">
                <tr><td colspan="7" class="empty-state">Loading...</td></tr>
            </tbody>
        </table>
    </div>
</div>

<div class="modal-overlay" id="equipmentModal">
    <div class="modal">
        <h2>Add Equipment</h2>
        <form id="equipmentForm" onsubmit="submitEquipment(event)">
            <div class="form-group">
                <label>Equipment Name</label>
                <input type="text" name="name" required placeholder="e.g., CNC Plasma Cutter">
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Category</label>
                    <select name="category">
                        <option value="fabrication">Fabrication</option>
                        <option value="welding">Welding</option>
                        <option value="cutting">Cutting</option>
                        <option value="transport">Transport</option>
                        <option value="safety">Safety</option>
                        <option value="other">Other</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Purchase Cost ($)</label>
                    <input type="number" name="purchase_cost" required placeholder="0.00" step="0.01">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Purchase Date</label>
                    <input type="date" name="purchase_date" required>
                </div>
                <div class="form-group">
                    <label>Useful Life (years)</label>
                    <input type="number" name="useful_life" placeholder="10" min="1">
                </div>
            </div>
            <div class="form-group">
                <label>Notes</label>
                <textarea name="notes" placeholder="Serial number, location, maintenance schedule..."></textarea>
            </div>
            <div class="modal-actions">
                <button type="button" class="btn-secondary" onclick="closeModal()">Cancel</button>
                <button type="submit" class="btn-gold">Add Equipment</button>
            </div>
        </form>
    </div>
</div>

<script>
let allEquipment = [];

function formatCurrency(val) {
    if (val == null) return '$0';
    return '$' + Number(val).toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}

function statusBadge(status) {
    const s = (status || 'active').toLowerCase();
    const labels = { active:'Active', maintenance:'Maintenance', retired:'Retired' };
    return `<span class="badge badge-${s}">${labels[s] || s}</span>`;
}

function calcDepreciation(item) {
    if (!item.purchase_cost || !item.purchase_date || !item.useful_life) return { bookValue: item.purchase_cost || 0, pct: 0 };
    const years = (Date.now() - new Date(item.purchase_date).getTime()) / (365.25 * 86400000);
    const annual = item.purchase_cost / item.useful_life;
    const totalDep = Math.min(annual * years, item.purchase_cost);
    return { bookValue: Math.max(0, item.purchase_cost - totalDep), pct: Math.min(100, (totalDep / item.purchase_cost) * 100) };
}

function updateStats(items) {
    const totalVal = items.reduce((s, e) => s + (Number(e.purchase_cost) || 0), 0);
    document.getElementById('stat-value').textContent = formatCurrency(totalVal);
    const bookVal = items.reduce((s, e) => s + calcDepreciation(e).bookValue, 0);
    document.getElementById('stat-book').textContent = formatCurrency(bookVal);
    document.getElementById('stat-maintenance').textContent = formatCurrency(
        items.reduce((s, e) => s + (Number(e.maintenance_ytd) || 0), 0)
    );
    document.getElementById('stat-active').textContent = items.filter(e => (e.status||'active') === 'active').length;
}

function renderTable(items) {
    const tbody = document.getElementById('equipmentBody');
    if (!items.length) {
        tbody.innerHTML = '<tr><td colspan="7" class="empty-state"><h3>No equipment found</h3><p>Add equipment to track costs and depreciation</p></td></tr>';
        return;
    }
    tbody.innerHTML = items.map(e => {
        const dep = calcDepreciation(e);
        return `<tr>
        <td style="font-weight:600">${e.name || '--'}</td>
        <td style="color:var(--tf-muted)">${e.category || '--'}</td>
        <td style="font-weight:700">${formatCurrency(e.purchase_cost)}</td>
        <td style="font-weight:600;color:var(--tf-blue)">${formatCurrency(dep.bookValue)}</td>
        <td><div class="depreciation-bar"><div class="depreciation-fill" style="width:${dep.pct}%"></div></div>
            <span style="font-size:11px;color:var(--tf-muted)">${Math.round(dep.pct)}%</span></td>
        <td style="color:var(--tf-red)">${formatCurrency(e.maintenance_ytd)}</td>
        <td>${statusBadge(e.status)}</td>
    </tr>`}).join('');
}

function applyFilters() {
    const q = (document.getElementById('searchInput').value || '').toLowerCase();
    const status = document.getElementById('statusFilter').value;
    let filtered = allEquipment.filter(e => {
        if (q && !(e.name||'').toLowerCase().includes(q) && !(e.category||'').toLowerCase().includes(q)) return false;
        if (status && (e.status||'active').toLowerCase() !== status) return false;
        return true;
    });
    renderTable(filtered);
}

function openModal() { document.getElementById('equipmentModal').classList.add('active'); }
function closeModal() { document.getElementById('equipmentModal').classList.remove('active'); }

async function submitEquipment(e) {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.target));
    data.status = 'active';
    data.maintenance_ytd = 0;
    data.created_at = new Date().toISOString();
    try {
        const res = await fetch('/api/financial/equipment', {
            method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data)
        });
        if (res.ok) { closeModal(); e.target.reset(); loadEquipment(); }
    } catch(err) { console.error('Failed to add equipment:', err); }
}

async function loadEquipment() {
    try {
        const res = await fetch('/api/financial/equipment');
        if (!res.ok) throw new Error('API error');
        const data = await res.json();
        allEquipment = Array.isArray(data) ? data : (data.equipment || []);
    } catch(err) { console.warn('Could not load equipment:', err); allEquipment = []; }
    updateStats(allEquipment);
    applyFilters();
}

document.getElementById('equipmentModal').addEventListener('click', function(e) { if (e.target === this) closeModal(); });
loadEquipment();
</script>
"""
