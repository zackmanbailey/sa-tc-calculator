"""
TitanForge v4 — Expense Tracking
==================================
Track expenses with categories, approval workflow, and reporting.
"""

FINANCIAL_EXPENSES_PAGE_HTML = r"""
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
    .exp-container {
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
    .exp-table { width: 100%; border-collapse: collapse; font-size: 14px; }
    .exp-table th {
        text-align: left; padding: 14px 16px; font-size: 11px;
        text-transform: uppercase; letter-spacing: 0.5px; color: var(--tf-muted);
        border-bottom: 1px solid rgba(255,255,255,0.06); font-weight: 600;
    }
    .exp-table td {
        padding: 14px 16px; border-bottom: 1px solid rgba(255,255,255,0.04); vertical-align: middle;
    }
    .exp-table tr:hover { background: rgba(255,255,255,0.02); }
    .exp-table tr:last-child td { border-bottom: none; }

    .badge {
        display: inline-block; padding: 4px 10px; border-radius: 20px;
        font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;
    }
    .badge-pending { background: rgba(212,168,67,0.15); color: #d4a843; }
    .badge-approved { background: rgba(16,185,129,0.15); color: #34d399; }
    .badge-rejected { background: rgba(239,68,68,0.15); color: #f87171; }
    .badge-reimbursed { background: rgba(59,130,246,0.15); color: #60a5fa; }

    .cat-tag {
        font-size: 12px; color: var(--tf-muted); background: rgba(255,255,255,0.04);
        padding: 3px 8px; border-radius: 4px;
    }

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
    .stat-row { grid-template-columns: 1fr 1fr; gap: 10px; }
    .modal-overlay .modal, .modal { width: 95%; max-width: 95vw; margin: 20px auto; padding: 20px; }
    .form-row { grid-template-columns: 1fr; }
    .exp-table { display: block; overflow-x: auto; -webkit-overflow-scrolling: touch; }
}
@media (max-width: 480px) {
    .stat-row { grid-template-columns: 1fr; }
    .toolbar { gap: 8px; }
}
</style>

<div class="exp-container">
    <div class="page-header">
        <h1>Expense Tracking</h1>
        <p>Track, categorize, and approve business expenses across projects</p>
    </div>

    <div class="stat-row">
        <div class="stat-card stat-red" onclick="filterByStatus('')">
            <div class="label">Total Expenses</div>
            <div class="value" id="stat-total">$0</div>
            <div class="sub">All time</div>
        </div>
        <div class="stat-card stat-gold" onclick="filterByStatus('pending')">
            <div class="label">Pending Approval</div>
            <div class="value" id="stat-pending">$0</div>
            <div class="sub">Awaiting review</div>
        </div>
        <div class="stat-card stat-green" onclick="filterByStatus('approved')">
            <div class="label">Approved</div>
            <div class="value" id="stat-approved">$0</div>
            <div class="sub">This month</div>
        </div>
        <div class="stat-card stat-blue" onclick="filterByStatus('reimbursed')">
            <div class="label">Reimbursed</div>
            <div class="value" id="stat-reimbursed">$0</div>
            <div class="sub">Completed</div>
        </div>
    </div>

    <div class="toolbar">
        <div class="toolbar-left">
            <input type="text" id="searchInput" placeholder="Search expenses..." oninput="applyFilters()">
            <select id="statusFilter" onchange="applyFilters()">
                <option value="">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
                <option value="reimbursed">Reimbursed</option>
            </select>
            <select id="categoryFilter" onchange="applyFilters()">
                <option value="">All Categories</option>
                <option value="materials">Materials</option>
                <option value="labor">Labor</option>
                <option value="equipment">Equipment</option>
                <option value="travel">Travel</option>
                <option value="office">Office</option>
                <option value="other">Other</option>
            </select>
        </div>
        <button class="btn-gold" onclick="openModal()">+ Add Expense</button>
    </div>

    <div class="table-card">
        <table class="exp-table">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Description</th>
                    <th>Category</th>
                    <th>Submitted By</th>
                    <th>Amount</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody id="expensesBody">
                <tr><td colspan="6" class="empty-state">Loading...</td></tr>
            </tbody>
        </table>
    </div>
</div>

<div class="modal-overlay" id="expenseModal">
    <div class="modal">
        <h2>Add Expense</h2>
        <form id="expenseForm" onsubmit="submitExpense(event)">
            <div class="form-group">
                <label>Description</label>
                <input type="text" name="description" required placeholder="What was this expense for?">
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Amount ($)</label>
                    <input type="number" name="amount" required placeholder="0.00" step="0.01">
                </div>
                <div class="form-group">
                    <label>Date</label>
                    <input type="date" name="date" required>
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Category</label>
                    <select name="category">
                        <option value="materials">Materials</option>
                        <option value="labor">Labor</option>
                        <option value="equipment">Equipment</option>
                        <option value="travel">Travel</option>
                        <option value="office">Office</option>
                        <option value="other">Other</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Project</label>
                    <input type="text" name="project" placeholder="Associated project">
                </div>
            </div>
            <div class="form-group">
                <label>Notes</label>
                <textarea name="notes" placeholder="Additional details, receipt info..."></textarea>
            </div>
            <div class="modal-actions">
                <button type="button" class="btn-secondary" onclick="closeModal()">Cancel</button>
                <button type="submit" class="btn-gold">Submit Expense</button>
            </div>
        </form>
    </div>
</div>

<script>
let allExpenses = [];

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
    const s = (status || 'pending').toLowerCase();
    const labels = { pending:'Pending', approved:'Approved', rejected:'Rejected', reimbursed:'Reimbursed' };
    return `<span class="badge badge-${s}">${labels[s] || s}</span>`;
}

function updateStats(expenses) {
    const total = expenses.reduce((s, e) => s + (Number(e.amount) || 0), 0);
    document.getElementById('stat-total').textContent = formatCurrency(total);
    document.getElementById('stat-pending').textContent = formatCurrency(
        expenses.filter(e => e.status === 'pending').reduce((s, e) => s + (Number(e.amount) || 0), 0)
    );
    document.getElementById('stat-approved').textContent = formatCurrency(
        expenses.filter(e => e.status === 'approved').reduce((s, e) => s + (Number(e.amount) || 0), 0)
    );
    document.getElementById('stat-reimbursed').textContent = formatCurrency(
        expenses.filter(e => e.status === 'reimbursed').reduce((s, e) => s + (Number(e.amount) || 0), 0)
    );
}

function renderTable(expenses) {
    const tbody = document.getElementById('expensesBody');
    if (!expenses.length) {
        tbody.innerHTML = '<tr><td colspan="6" class="empty-state"><h3>No expenses found</h3><p>Add your first expense to start tracking</p></td></tr>';
        return;
    }
    tbody.innerHTML = expenses.map(e => `<tr>
        <td style="color:var(--tf-muted)">${formatDate(e.date)}</td>
        <td style="font-weight:600">${e.description || '--'}</td>
        <td><span class="cat-tag">${e.category || '--'}</span></td>
        <td style="color:var(--tf-muted)">${e.submitted_by || '--'}</td>
        <td style="font-weight:700;color:var(--tf-red)">${formatCurrency(e.amount)}</td>
        <td>${statusBadge(e.status)}</td>
    </tr>`).join('');
}

function applyFilters() {
    const q = (document.getElementById('searchInput').value || '').toLowerCase();
    const status = document.getElementById('statusFilter').value;
    const cat = document.getElementById('categoryFilter').value;
    let filtered = allExpenses.filter(e => {
        if (q && !(e.description||'').toLowerCase().includes(q) && !(e.project||'').toLowerCase().includes(q)) return false;
        if (status && (e.status||'').toLowerCase() !== status) return false;
        if (cat && (e.category||'').toLowerCase() !== cat) return false;
        return true;
    });
    renderTable(filtered);
}
function filterByStatus(s) { document.getElementById('statusFilter').value = s; applyFilters(); }

function openModal() {
    document.getElementById('expenseModal').classList.add('active');
    const d = document.querySelector('#expenseForm input[name="date"]');
    if (d && !d.value) d.value = new Date().toISOString().split('T')[0];
}
function closeModal() { document.getElementById('expenseModal').classList.remove('active'); }

async function submitExpense(e) {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.target));
    data.status = 'pending';
    data.created_at = new Date().toISOString();
    try {
        const res = await fetch('/api/financial/expenses', {
            method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data)
        });
        if (res.ok) { closeModal(); e.target.reset(); loadExpenses(); }
    } catch(err) { console.error('Failed to add expense:', err); }
}

async function loadExpenses() {
    try {
        const res = await fetch('/api/financial/expenses');
        if (!res.ok) throw new Error('API error');
        const data = await res.json();
        allExpenses = Array.isArray(data) ? data : (data.expenses || []);
    } catch(err) { console.warn('Could not load expenses:', err); allExpenses = []; }
    updateStats(allExpenses);
    applyFilters();
}

document.getElementById('expenseModal').addEventListener('click', function(e) { if (e.target === this) closeModal(); });
loadExpenses();
</script>
"""
