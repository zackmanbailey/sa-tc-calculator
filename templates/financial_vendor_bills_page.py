"""
TitanForge v4 — Vendor Bills
==============================
Vendor bill management, payment tracking, and aging report.
"""

FINANCIAL_VENDOR_BILLS_PAGE_HTML = r"""
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
    .vb-container {
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
    .vb-table { width: 100%; border-collapse: collapse; font-size: 14px; }
    .vb-table th {
        text-align: left; padding: 14px 16px; font-size: 11px;
        text-transform: uppercase; letter-spacing: 0.5px; color: var(--tf-muted);
        border-bottom: 1px solid rgba(255,255,255,0.06); font-weight: 600;
    }
    .vb-table td {
        padding: 14px 16px; border-bottom: 1px solid rgba(255,255,255,0.04); vertical-align: middle;
    }
    .vb-table tr:hover { background: rgba(255,255,255,0.02); }
    .vb-table tr:last-child td { border-bottom: none; }

    .badge {
        display: inline-block; padding: 4px 10px; border-radius: 20px;
        font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;
    }
    .badge-unpaid { background: rgba(212,168,67,0.15); color: #d4a843; }
    .badge-paid { background: rgba(16,185,129,0.15); color: #34d399; }
    .badge-overdue { background: rgba(239,68,68,0.15); color: #f87171; }
    .badge-partial { background: rgba(59,130,246,0.15); color: #60a5fa; }

    .aging-cards {
        display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 12px; margin-bottom: 24px;
    }
    .aging-card {
        background: var(--tf-card); border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.06); padding: 16px; text-align: center;
    }
    .aging-card .aging-label { font-size: 11px; color: var(--tf-muted); text-transform: uppercase; margin-bottom: 6px; }
    .aging-card .aging-val { font-size: 20px; font-weight: 800; color: var(--tf-text); }

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
        width: 540px; max-width: 95vw; max-height: 90vh; overflow-y: auto;
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
    .stat-row, .aging-cards { grid-template-columns: 1fr 1fr; gap: 10px; }
    .modal-overlay .modal, .modal { width: 95%; max-width: 95vw; margin: 20px auto; padding: 20px; }
    .form-row { grid-template-columns: 1fr; }
    .vb-table { display: block; overflow-x: auto; -webkit-overflow-scrolling: touch; }
    .aging-cards { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 480px) {
    .stat-row, .aging-cards { grid-template-columns: 1fr; }
    .toolbar { gap: 8px; }
    .aging-cards { grid-template-columns: 1fr; }
}
</style>

<div class="vb-container">
    <div class="page-header">
        <h1>Vendor Bills</h1>
        <p>Manage vendor bills, track payments, and monitor aging balances</p>
    </div>

    <div class="stat-row">
        <div class="stat-card stat-blue" onclick="filterByStatus('')">
            <div class="label">Total Bills</div>
            <div class="value" id="stat-total">--</div>
            <div class="sub">All records</div>
        </div>
        <div class="stat-card stat-gold" onclick="filterByStatus('unpaid')">
            <div class="label">Unpaid</div>
            <div class="value" id="stat-unpaid">$0</div>
            <div class="sub">Outstanding</div>
        </div>
        <div class="stat-card stat-red" onclick="filterByStatus('overdue')">
            <div class="label">Overdue</div>
            <div class="value" id="stat-overdue">$0</div>
            <div class="sub">Past due date</div>
        </div>
        <div class="stat-card stat-green" onclick="filterByStatus('paid')">
            <div class="label">Paid</div>
            <div class="value" id="stat-paid">$0</div>
            <div class="sub">Completed</div>
        </div>
    </div>

    <div class="aging-cards">
        <div class="aging-card"><div class="aging-label">Current</div><div class="aging-val" id="aging-current">$0</div></div>
        <div class="aging-card"><div class="aging-label">1-30 Days</div><div class="aging-val" id="aging-30">$0</div></div>
        <div class="aging-card"><div class="aging-label">31-60 Days</div><div class="aging-val" id="aging-60">$0</div></div>
        <div class="aging-card"><div class="aging-label">61-90 Days</div><div class="aging-val" id="aging-90">$0</div></div>
        <div class="aging-card"><div class="aging-label">90+ Days</div><div class="aging-val" id="aging-90plus" style="color:var(--tf-red)">$0</div></div>
    </div>

    <div class="toolbar">
        <div class="toolbar-left">
            <input type="text" id="searchInput" placeholder="Search vendor bills..." oninput="applyFilters()">
            <select id="statusFilter" onchange="applyFilters()">
                <option value="">All Statuses</option>
                <option value="unpaid">Unpaid</option>
                <option value="paid">Paid</option>
                <option value="overdue">Overdue</option>
                <option value="partial">Partial</option>
            </select>
        </div>
        <button class="btn-gold" onclick="openModal()">+ Add Bill</button>
    </div>

    <div class="table-card">
        <table class="vb-table">
            <thead>
                <tr>
                    <th>Bill #</th>
                    <th>Vendor</th>
                    <th>Description</th>
                    <th>Amount</th>
                    <th>Bill Date</th>
                    <th>Due Date</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody id="billsBody">
                <tr><td colspan="7" class="empty-state">Loading...</td></tr>
            </tbody>
        </table>
    </div>
</div>

<div class="modal-overlay" id="billModal">
    <div class="modal">
        <h2>Add Vendor Bill</h2>
        <form id="billForm" onsubmit="submitBill(event)">
            <div class="form-row">
                <div class="form-group">
                    <label>Vendor Name</label>
                    <input type="text" name="vendor" required placeholder="Vendor or supplier">
                </div>
                <div class="form-group">
                    <label>Bill Number</label>
                    <input type="text" name="bill_number" placeholder="VB-001">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Amount ($)</label>
                    <input type="number" name="amount" required placeholder="0.00" step="0.01">
                </div>
                <div class="form-group">
                    <label>Due Date</label>
                    <input type="date" name="due_date" required>
                </div>
            </div>
            <div class="form-group">
                <label>Description</label>
                <textarea name="description" placeholder="Bill details..."></textarea>
            </div>
            <div class="modal-actions">
                <button type="button" class="btn-secondary" onclick="closeModal()">Cancel</button>
                <button type="submit" class="btn-gold">Add Bill</button>
            </div>
        </form>
    </div>
</div>

<script>
let allBills = [];

function formatCurrency(val) {
    if (val == null) return '$0';
    return '$' + Number(val).toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}
function formatDate(d) {
    if (!d) return '--';
    const dt = new Date(d);
    if (isNaN(dt)) return d;
    return dt.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function statusBadge(status) {
    const s = (status || 'unpaid').toLowerCase();
    const labels = { unpaid:'Unpaid', paid:'Paid', overdue:'Overdue', partial:'Partial' };
    return `<span class="badge badge-${s}">${labels[s] || s}</span>`;
}

function updateStats(bills) {
    document.getElementById('stat-total').textContent = bills.length;
    const unpaid = bills.filter(b => b.status === 'unpaid' || b.status === 'partial');
    document.getElementById('stat-unpaid').textContent = formatCurrency(unpaid.reduce((s, b) => s + (Number(b.amount) || 0), 0));
    const overdue = bills.filter(b => (b.status === 'overdue') || (b.status !== 'paid' && b.due_date && new Date(b.due_date) < new Date()));
    document.getElementById('stat-overdue').textContent = formatCurrency(overdue.reduce((s, b) => s + (Number(b.amount) || 0), 0));
    document.getElementById('stat-paid').textContent = formatCurrency(
        bills.filter(b => b.status === 'paid').reduce((s, b) => s + (Number(b.amount) || 0), 0)
    );
}

function renderTable(bills) {
    const tbody = document.getElementById('billsBody');
    if (!bills.length) {
        tbody.innerHTML = '<tr><td colspan="7" class="empty-state"><h3>No vendor bills found</h3><p>Add your first vendor bill to start tracking</p></td></tr>';
        return;
    }
    tbody.innerHTML = bills.map(b => {
        const isOverdue = b.status !== 'paid' && b.due_date && new Date(b.due_date) < new Date();
        return `<tr>
        <td style="font-weight:700;color:var(--tf-gold);font-family:'JetBrains Mono',monospace">${b.bill_number || b.id || '--'}</td>
        <td style="font-weight:600">${b.vendor || '--'}</td>
        <td style="color:var(--tf-muted);max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${b.description || '--'}</td>
        <td style="font-weight:700">${formatCurrency(b.amount)}</td>
        <td style="color:var(--tf-muted)">${formatDate(b.bill_date || b.created_at)}</td>
        <td style="color:${isOverdue ? 'var(--tf-red);font-weight:600' : 'var(--tf-muted)'}">${formatDate(b.due_date)}</td>
        <td>${statusBadge(isOverdue && b.status !== 'paid' ? 'overdue' : b.status)}</td>
    </tr>`}).join('');
}

function applyFilters() {
    const q = (document.getElementById('searchInput').value || '').toLowerCase();
    const status = document.getElementById('statusFilter').value;
    let filtered = allBills.filter(b => {
        if (q && !(b.vendor||'').toLowerCase().includes(q) && !(b.bill_number||'').toLowerCase().includes(q) && !(b.description||'').toLowerCase().includes(q)) return false;
        if (status && (b.status||'').toLowerCase() !== status) return false;
        return true;
    });
    renderTable(filtered);
}
function filterByStatus(s) { document.getElementById('statusFilter').value = s; applyFilters(); }

function openModal() {
    document.getElementById('billModal').classList.add('active');
    const dd = document.querySelector('#billForm input[name="due_date"]');
    if (dd && !dd.value) { const d = new Date(); d.setDate(d.getDate()+30); dd.value = d.toISOString().split('T')[0]; }
}
function closeModal() { document.getElementById('billModal').classList.remove('active'); }

async function submitBill(e) {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.target));
    data.status = 'unpaid';
    data.created_at = new Date().toISOString();
    data.bill_date = new Date().toISOString().split('T')[0];
    try {
        const res = await fetch('/api/financial/vendor-bills', {
            method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data)
        });
        if (res.ok) { closeModal(); e.target.reset(); loadBills(); }
    } catch(err) { console.error('Failed to add bill:', err); }
}

async function loadBills() {
    try {
        const res = await fetch('/api/financial/vendor-bills');
        if (!res.ok) throw new Error('API error');
        const data = await res.json();
        allBills = Array.isArray(data) ? data : (data.bills || []);
    } catch(err) { console.warn('Could not load bills:', err); allBills = []; }
    updateStats(allBills);
    applyFilters();
}

document.getElementById('billModal').addEventListener('click', function(e) { if (e.target === this) closeModal(); });
loadBills();
</script>
"""
