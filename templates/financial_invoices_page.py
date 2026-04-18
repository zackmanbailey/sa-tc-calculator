"""
TitanForge v4 — Invoice Management
====================================
Invoice list with status tracking, creation, and filtering.
"""

FINANCIAL_INVOICES_PAGE_HTML = r"""
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
    .inv-container {
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
    .inv-table { width: 100%; border-collapse: collapse; font-size: 14px; }
    .inv-table th {
        text-align: left; padding: 14px 16px; font-size: 11px;
        text-transform: uppercase; letter-spacing: 0.5px; color: var(--tf-muted);
        border-bottom: 1px solid rgba(255,255,255,0.06); font-weight: 600;
    }
    .inv-table td {
        padding: 14px 16px; border-bottom: 1px solid rgba(255,255,255,0.04); vertical-align: middle;
    }
    .inv-table tr:hover { background: rgba(255,255,255,0.02); }
    .inv-table tr:last-child td { border-bottom: none; }

    .inv-num { font-weight: 700; color: var(--tf-gold); font-family: 'JetBrains Mono', monospace; }

    .badge {
        display: inline-block; padding: 4px 10px; border-radius: 20px;
        font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;
    }
    .badge-draft { background: rgba(148,163,184,0.15); color: #94a3b8; }
    .badge-sent { background: rgba(59,130,246,0.15); color: #60a5fa; }
    .badge-paid { background: rgba(16,185,129,0.15); color: #34d399; }
    .badge-overdue { background: rgba(239,68,68,0.15); color: #f87171; }

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
    .inv-table { display: block; overflow-x: auto; -webkit-overflow-scrolling: touch; }
}
@media (max-width: 480px) {
    .stat-row { grid-template-columns: 1fr; }
    .toolbar { gap: 8px; }
}
</style>

<div class="inv-container">
    <div class="page-header">
        <h1>Invoices</h1>
        <p>Create, send, and track invoices for customers and projects</p>
    </div>

    <div class="stat-row">
        <div class="stat-card stat-blue" onclick="filterByStatus('')">
            <div class="label">Total Invoices</div>
            <div class="value" id="stat-total">--</div>
            <div class="sub">All time</div>
        </div>
        <div class="stat-card stat-gold" onclick="filterByStatus('sent')">
            <div class="label">Pending</div>
            <div class="value" id="stat-pending">--</div>
            <div class="sub">Awaiting payment</div>
        </div>
        <div class="stat-card stat-green" onclick="filterByStatus('paid')">
            <div class="label">Paid</div>
            <div class="value" id="stat-paid">--</div>
            <div class="sub">Collected</div>
        </div>
        <div class="stat-card stat-red" onclick="filterByStatus('overdue')">
            <div class="label">Overdue</div>
            <div class="value" id="stat-overdue">--</div>
            <div class="sub">Past due date</div>
        </div>
    </div>

    <div class="toolbar">
        <div class="toolbar-left">
            <input type="text" id="searchInput" placeholder="Search invoices..." oninput="applyFilters()">
            <select id="statusFilter" onchange="applyFilters()">
                <option value="">All Statuses</option>
                <option value="draft">Draft</option>
                <option value="sent">Sent</option>
                <option value="paid">Paid</option>
                <option value="overdue">Overdue</option>
            </select>
        </div>
        <button class="btn-gold" onclick="openModal()">+ Create Invoice</button>
    </div>

    <div class="table-card">
        <table class="inv-table">
            <thead>
                <tr>
                    <th>Invoice #</th>
                    <th>Customer</th>
                    <th>Project</th>
                    <th>Amount</th>
                    <th>Date</th>
                    <th>Due Date</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody id="invoicesBody">
                <tr><td colspan="7" class="empty-state">Loading...</td></tr>
            </tbody>
        </table>
    </div>
</div>

<div class="modal-overlay" id="invoiceModal">
    <div class="modal">
        <h2>Create Invoice</h2>
        <form id="invoiceForm" onsubmit="submitInvoice(event)">
            <div class="form-row">
                <div class="form-group">
                    <label>Customer Name</label>
                    <input type="text" name="customer" required placeholder="Customer or company">
                </div>
                <div class="form-group">
                    <label>Project</label>
                    <input type="text" name="project" placeholder="Project name">
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
                <textarea name="description" placeholder="Invoice details and line items..."></textarea>
            </div>
            <div class="form-group">
                <label>Status</label>
                <select name="status">
                    <option value="draft">Draft</option>
                    <option value="sent">Sent</option>
                </select>
            </div>
            <div class="modal-actions">
                <button type="button" class="btn-secondary" onclick="closeModal()">Cancel</button>
                <button type="submit" class="btn-gold">Create Invoice</button>
            </div>
        </form>
    </div>
</div>

<script>
let allInvoices = [];

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
    const s = (status || 'draft').toLowerCase();
    const labels = { draft:'Draft', sent:'Sent', paid:'Paid', overdue:'Overdue' };
    return `<span class="badge badge-${s}">${labels[s] || s}</span>`;
}

function updateStats(invoices) {
    document.getElementById('stat-total').textContent = invoices.length;
    document.getElementById('stat-pending').textContent = formatCurrency(
        invoices.filter(i => i.status === 'sent').reduce((s, i) => s + (Number(i.amount) || 0), 0)
    );
    document.getElementById('stat-paid').textContent = formatCurrency(
        invoices.filter(i => i.status === 'paid').reduce((s, i) => s + (Number(i.amount) || 0), 0)
    );
    const overdue = invoices.filter(i => i.status === 'overdue' || (i.status === 'sent' && i.due_date && new Date(i.due_date) < new Date()));
    document.getElementById('stat-overdue').textContent = formatCurrency(
        overdue.reduce((s, i) => s + (Number(i.amount) || 0), 0)
    );
}

function renderTable(invoices) {
    const tbody = document.getElementById('invoicesBody');
    if (!invoices.length) {
        tbody.innerHTML = '<tr><td colspan="7" class="empty-state"><h3>No invoices found</h3><p>Create your first invoice to start tracking payments</p></td></tr>';
        return;
    }
    tbody.innerHTML = invoices.map(i => `<tr>
        <td><span class="inv-num">${i.invoice_number || i.id || '--'}</span></td>
        <td style="font-weight:600">${i.customer || '--'}</td>
        <td style="color:var(--tf-muted)">${i.project || '--'}</td>
        <td style="font-weight:700">${formatCurrency(i.amount)}</td>
        <td style="color:var(--tf-muted)">${formatDate(i.created_at || i.date)}</td>
        <td style="color:${i.due_date && new Date(i.due_date) < new Date() && i.status !== 'paid' ? 'var(--tf-red);font-weight:600' : 'var(--tf-muted)'}">${formatDate(i.due_date)}</td>
        <td>${statusBadge(i.status)}</td>
    </tr>`).join('');
}

function applyFilters() {
    const q = (document.getElementById('searchInput').value || '').toLowerCase();
    const status = document.getElementById('statusFilter').value;
    let filtered = allInvoices.filter(i => {
        if (q && !(i.customer||'').toLowerCase().includes(q) && !(i.invoice_number||'').toLowerCase().includes(q) && !(i.project||'').toLowerCase().includes(q)) return false;
        if (status && (i.status||'').toLowerCase() !== status) return false;
        return true;
    });
    renderTable(filtered);
}
function filterByStatus(s) { document.getElementById('statusFilter').value = s; applyFilters(); }

function openModal() {
    document.getElementById('invoiceModal').classList.add('active');
    const dd = document.querySelector('input[name="due_date"]');
    if (dd && !dd.value) { const d = new Date(); d.setDate(d.getDate()+30); dd.value = d.toISOString().split('T')[0]; }
}
function closeModal() { document.getElementById('invoiceModal').classList.remove('active'); }

async function submitInvoice(e) {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.target));
    data.created_at = new Date().toISOString();
    try {
        const res = await fetch('/api/financial/invoices', {
            method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data)
        });
        if (res.ok) { closeModal(); e.target.reset(); loadInvoices(); }
    } catch(err) { console.error('Failed to create invoice:', err); }
}

async function loadInvoices() {
    try {
        const res = await fetch('/api/financial/invoices');
        if (!res.ok) throw new Error('API error');
        const data = await res.json();
        allInvoices = Array.isArray(data) ? data : (data.invoices || []);
    } catch(err) { console.warn('Could not load invoices:', err); allInvoices = []; }
    updateStats(allInvoices);
    applyFilters();
}

document.getElementById('invoiceModal').addEventListener('click', function(e) { if (e.target === this) closeModal(); });
loadInvoices();
</script>
"""
