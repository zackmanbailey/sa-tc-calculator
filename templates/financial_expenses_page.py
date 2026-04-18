"""
TitanForge v4 — Expense Tracking (Production)
===============================================
Job costing integration with categories, approval workflow,
budget comparison, and CSV export.
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
        --tf-purple: #a78bfa;
        --tf-orange: #fb923c;
    }
    .exp-container {
        max-width: 1400px; margin: 0 auto; padding: 24px 32px;
        font-family: 'Inter', 'Segoe UI', sans-serif; color: var(--tf-text);
    }
    .page-header { margin-bottom: 28px; display: flex; justify-content: space-between; align-items: flex-start; }
    .page-header div h1 { font-size: 28px; font-weight: 800; margin: 0 0 6px 0; }
    .page-header div p { font-size: 14px; color: var(--tf-muted); margin: 0; }

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
    .toolbar-right { display: flex; gap: 10px; }
    .btn-gold {
        background: var(--tf-gold); color: #0f172a; border: none; border-radius: 8px;
        padding: 10px 20px; font-weight: 700; font-size: 14px; cursor: pointer;
    }
    .btn-gold:hover { opacity: 0.9; }
    .btn-outline {
        background: transparent; border: 1px solid rgba(255,255,255,0.15);
        border-radius: 8px; padding: 10px 16px; color: var(--tf-muted);
        font-weight: 600; font-size: 13px; cursor: pointer;
    }
    .btn-outline:hover { color: var(--tf-text); border-color: rgba(255,255,255,0.3); }
    .btn-sm {
        padding: 5px 12px; font-size: 12px; border-radius: 6px; border: none;
        font-weight: 600; cursor: pointer;
    }
    .btn-approve { background: rgba(16,185,129,0.15); color: #34d399; }
    .btn-reject { background: rgba(239,68,68,0.15); color: #f87171; }

    /* Chart Section */
    .chart-section {
        display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-bottom: 24px;
    }
    .chart-card {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06); padding: 24px;
    }
    .chart-card h3 { margin: 0 0 16px 0; font-size: 16px; font-weight: 700; }
    .bar-chart { display: flex; align-items: flex-end; gap: 12px; height: 160px; }
    .bar-group { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4px; }
    .bar { width: 100%; max-width: 50px; border-radius: 4px 4px 0 0; min-height: 2px; transition: height 0.4s; }
    .bar-label { font-size: 10px; color: var(--tf-muted); text-align: center; }
    .bar-value { font-size: 10px; color: var(--tf-text); font-weight: 600; }
    .cat-legend { display: flex; flex-direction: column; gap: 8px; }
    .cat-legend-item { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: rgba(255,255,255,0.02); border-radius: 8px; }
    .cat-legend-label { display: flex; align-items: center; gap: 8px; font-size: 13px; }
    .cat-dot { width: 10px; height: 10px; border-radius: 50%; }
    .cat-legend-value { font-weight: 700; font-size: 14px; }

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
    .badge-submitted { background: rgba(212,168,67,0.15); color: #d4a843; }
    .badge-manager_review { background: rgba(59,130,246,0.15); color: #60a5fa; }
    .badge-approved { background: rgba(16,185,129,0.15); color: #34d399; }
    .badge-rejected { background: rgba(239,68,68,0.15); color: #f87171; }
    .badge-paid { background: rgba(167,139,250,0.15); color: #a78bfa; }

    .cat-tag {
        font-size: 12px; color: var(--tf-muted); background: rgba(255,255,255,0.04);
        padding: 3px 8px; border-radius: 4px;
    }

    .budget-bar { display: flex; align-items: center; gap: 8px; }
    .budget-track { width: 80px; height: 6px; background: rgba(255,255,255,0.06); border-radius: 3px; overflow: hidden; }
    .budget-fill { height: 100%; border-radius: 3px; }
    .budget-ok { background: var(--tf-green); }
    .budget-warn { background: var(--tf-gold); }
    .budget-over { background: var(--tf-red); }

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

/* Responsive */
@media (max-width: 900px) { .chart-section { grid-template-columns: 1fr; } }
@media (max-width: 768px) {
    .page-header { flex-direction: column; gap: 12px; }
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
        <div>
            <h1>Expense Tracking</h1>
            <p>Track, categorize, and approve business expenses across projects</p>
        </div>
    </div>

    <div class="stat-row">
        <div class="stat-card stat-red" onclick="filterByStatus('')">
            <div class="label">Total Expenses</div>
            <div class="value" id="stat-total">$0</div>
            <div class="sub">All time</div>
        </div>
        <div class="stat-card stat-gold" onclick="filterByStatus('submitted')">
            <div class="label">Pending Approval</div>
            <div class="value" id="stat-pending">$0</div>
            <div class="sub">Awaiting review</div>
        </div>
        <div class="stat-card stat-green" onclick="filterByStatus('approved')">
            <div class="label">Approved</div>
            <div class="value" id="stat-approved">$0</div>
            <div class="sub">This month</div>
        </div>
        <div class="stat-card stat-blue" onclick="filterByStatus('')">
            <div class="label">Over Budget</div>
            <div class="value" id="stat-overbudget">0</div>
            <div class="sub">Projects exceeding budget</div>
        </div>
    </div>

    <!-- Category Chart -->
    <div class="chart-section">
        <div class="chart-card">
            <h3>Expenses by Category</h3>
            <div class="bar-chart" id="categoryChart"></div>
        </div>
        <div class="chart-card">
            <h3>Category Breakdown</h3>
            <div class="cat-legend" id="categoryLegend"></div>
        </div>
    </div>

    <div class="toolbar">
        <div class="toolbar-left">
            <input type="text" id="searchInput" placeholder="Search expenses..." oninput="applyFilters()">
            <select id="statusFilter" onchange="applyFilters()">
                <option value="">All Statuses</option>
                <option value="submitted">Submitted</option>
                <option value="manager_review">Manager Review</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
                <option value="paid">Paid</option>
            </select>
            <select id="categoryFilter" onchange="applyFilters()">
                <option value="">All Categories</option>
                <option value="materials">Materials</option>
                <option value="labor">Labor</option>
                <option value="equipment">Equipment</option>
                <option value="subcontractor">Subcontractor</option>
                <option value="overhead">Overhead</option>
                <option value="freight">Freight</option>
                <option value="permits">Permits</option>
            </select>
            <select id="projectFilter" onchange="applyFilters()">
                <option value="">All Projects</option>
            </select>
        </div>
        <div class="toolbar-right">
            <button class="btn-outline" onclick="exportCSV()">Download CSV</button>
            <button class="btn-gold" onclick="openModal()">+ Add Expense</button>
        </div>
    </div>

    <div class="table-card">
        <table class="exp-table">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Description</th>
                    <th>Category</th>
                    <th>Project</th>
                    <th>Amount</th>
                    <th>vs Budget</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody id="expensesBody">
                <tr><td colspan="8" class="empty-state">Loading...</td></tr>
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
                        <option value="subcontractor">Subcontractor</option>
                        <option value="overhead">Overhead</option>
                        <option value="freight">Freight</option>
                        <option value="permits">Permits</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Project / Job Code</label>
                    <select name="job_code" id="expProjectSelect">
                        <option value="">-- Select project --</option>
                    </select>
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Vendor / Supplier</label>
                    <input type="text" name="vendor" placeholder="Vendor name">
                </div>
                <div class="form-group">
                    <label>Receipt / PO #</label>
                    <input type="text" name="receipt_number" placeholder="Optional reference">
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
let projectBudgets = {};
const catColors = {
    materials: '#3b82f6', labor: '#10b981', equipment: '#d4a843',
    subcontractor: '#a78bfa', overhead: '#f87171', freight: '#fb923c', permits: '#38bdf8'
};

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
    const s = (status || 'submitted').toLowerCase();
    const labels = { submitted:'Submitted', manager_review:'In Review', approved:'Approved', rejected:'Rejected', paid:'Paid' };
    return '<span class="badge badge-' + s + '">' + (labels[s] || s) + '</span>';
}

function updateStats(expenses) {
    const total = expenses.reduce((s, e) => s + (Number(e.amount) || 0), 0);
    document.getElementById('stat-total').textContent = formatCurrency(total);
    document.getElementById('stat-pending').textContent = formatCurrency(
        expenses.filter(e => ['submitted','manager_review'].includes(e.status)).reduce((s, e) => s + (Number(e.amount) || 0), 0)
    );
    document.getElementById('stat-approved').textContent = formatCurrency(
        expenses.filter(e => e.status === 'approved').reduce((s, e) => s + (Number(e.amount) || 0), 0)
    );
    // Over budget count
    const byProject = {};
    expenses.filter(e => e.job_code).forEach(e => {
        byProject[e.job_code] = (byProject[e.job_code] || 0) + (Number(e.amount) || 0);
    });
    let overCount = 0;
    Object.entries(byProject).forEach(([code, spent]) => {
        if (projectBudgets[code] && spent > projectBudgets[code]) overCount++;
    });
    document.getElementById('stat-overbudget').textContent = overCount;
}

function renderCategoryChart(expenses) {
    const byCategory = {};
    expenses.forEach(e => {
        const cat = e.category || 'other';
        byCategory[cat] = (byCategory[cat] || 0) + (Number(e.amount) || 0);
    });
    const cats = Object.entries(byCategory).sort((a, b) => b[1] - a[1]);
    const maxVal = Math.max(...cats.map(c => c[1]), 1);

    const chart = document.getElementById('categoryChart');
    if (!cats.length) {
        chart.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:160px;color:var(--tf-muted);font-size:13px;">No expense data yet</div>';
    } else {
        chart.innerHTML = cats.map(([cat, val]) =>
            '<div class="bar-group">' +
            '<div class="bar-value">' + formatCurrency(val) + '</div>' +
            '<div class="bar" style="background:' + (catColors[cat]||'#94a3b8') + ';height:' + Math.max(4, (val/maxVal)*140) + 'px;"></div>' +
            '<div class="bar-label">' + cat.charAt(0).toUpperCase() + cat.slice(1) + '</div>' +
            '</div>'
        ).join('');
    }

    const legend = document.getElementById('categoryLegend');
    legend.innerHTML = cats.map(([cat, val]) =>
        '<div class="cat-legend-item">' +
        '<span class="cat-legend-label"><span class="cat-dot" style="background:' + (catColors[cat]||'#94a3b8') + '"></span>' + cat.charAt(0).toUpperCase() + cat.slice(1) + '</span>' +
        '<span class="cat-legend-value">' + formatCurrency(val) + '</span>' +
        '</div>'
    ).join('');
}

function getBudgetBar(expense) {
    if (!expense.job_code || !projectBudgets[expense.job_code]) return '--';
    const budget = projectBudgets[expense.job_code];
    // Sum all expenses for this project
    const totalSpent = allExpenses.filter(e => e.job_code === expense.job_code).reduce((s, e) => s + (Number(e.amount) || 0), 0);
    const pct = Math.round((totalSpent / budget) * 100);
    const cls = pct > 100 ? 'budget-over' : pct > 80 ? 'budget-warn' : 'budget-ok';
    return '<div class="budget-bar"><div class="budget-track"><div class="budget-fill ' + cls + '" style="width:' + Math.min(pct,100) + '%"></div></div><span style="font-size:11px;color:var(--tf-muted)">' + pct + '%</span></div>';
}

function renderTable(expenses) {
    const tbody = document.getElementById('expensesBody');
    if (!expenses.length) {
        tbody.innerHTML = '<tr><td colspan="8" class="empty-state"><h3>No expenses found</h3><p>Add your first expense to start tracking</p></td></tr>';
        return;
    }
    tbody.innerHTML = expenses.map(e => '<tr>' +
        '<td style="color:var(--tf-muted)">' + formatDate(e.date) + '</td>' +
        '<td style="font-weight:600">' + (e.description || '--') + (e.vendor ? '<div style="font-size:11px;color:var(--tf-muted)">' + e.vendor + '</div>' : '') + '</td>' +
        '<td><span class="cat-tag" style="border-left:3px solid ' + (catColors[e.category]||'#94a3b8') + ';padding-left:8px;">' + (e.category || '--') + '</span></td>' +
        '<td style="color:var(--tf-muted);font-size:13px;">' + (e.job_code || '--') + '</td>' +
        '<td style="font-weight:700;color:var(--tf-red)">' + formatCurrency(e.amount) + '</td>' +
        '<td>' + getBudgetBar(e) + '</td>' +
        '<td>' + statusBadge(e.status) + '</td>' +
        '<td>' + renderExpenseActions(e) + '</td>' +
        '</tr>').join('');
}

function renderExpenseActions(e) {
    if (e.status === 'submitted') {
        return '<button class="btn-sm btn-approve" onclick="updateExpenseStatus(\'' + e.id + '\',\'manager_review\')">Review</button>';
    }
    if (e.status === 'manager_review') {
        return '<button class="btn-sm btn-approve" onclick="updateExpenseStatus(\'' + e.id + '\',\'approved\')">Approve</button> ' +
               '<button class="btn-sm btn-reject" onclick="updateExpenseStatus(\'' + e.id + '\',\'rejected\')">Reject</button>';
    }
    if (e.status === 'approved') {
        return '<button class="btn-sm btn-approve" onclick="updateExpenseStatus(\'' + e.id + '\',\'paid\')">Mark Paid</button>';
    }
    return '';
}

async function updateExpenseStatus(id, newStatus) {
    try {
        await fetch('/api/financial/expenses', {
            method: 'PUT', headers: {'Content-Type':'application/json'},
            body: JSON.stringify({ id, status: newStatus })
        });
        loadExpenses();
    } catch(e) { console.error(e); }
}

function applyFilters() {
    const q = (document.getElementById('searchInput').value || '').toLowerCase();
    const status = document.getElementById('statusFilter').value;
    const cat = document.getElementById('categoryFilter').value;
    const proj = document.getElementById('projectFilter').value;
    let filtered = allExpenses.filter(e => {
        if (q && !(e.description||'').toLowerCase().includes(q) && !(e.vendor||'').toLowerCase().includes(q) && !(e.job_code||'').toLowerCase().includes(q)) return false;
        if (status && (e.status||'').toLowerCase() !== status) return false;
        if (cat && (e.category||'').toLowerCase() !== cat) return false;
        if (proj && (e.job_code||'') !== proj) return false;
        return true;
    });
    renderTable(filtered);
}
function filterByStatus(s) { document.getElementById('statusFilter').value = s; applyFilters(); }

function openModal() {
    document.getElementById('expenseModal').classList.add('active');
    const d = document.querySelector('#expenseForm input[name="date"]');
    if (d && !d.value) d.value = new Date().toISOString().split('T')[0];
    loadProjectsForExpense();
}
function closeModal() { document.getElementById('expenseModal').classList.remove('active'); }

async function loadProjectsForExpense() {
    try {
        const res = await fetch('/api/financial/projects');
        if (!res.ok) return;
        const data = await res.json();
        const projects = data.projects || [];
        const sel = document.getElementById('expProjectSelect');
        const filterSel = document.getElementById('projectFilter');
        sel.innerHTML = '<option value="">-- Select project --</option>';
        projects.forEach(p => {
            sel.innerHTML += '<option value="' + p.job_code + '">' + p.job_code + ' - ' + (p.project_name||'') + '</option>';
            if (p.material_cost) projectBudgets[p.job_code] = p.material_cost;
        });
        // Populate filter too
        if (filterSel.options.length <= 1) {
            projects.forEach(p => {
                filterSel.innerHTML += '<option value="' + p.job_code + '">' + p.job_code + '</option>';
            });
        }
    } catch(e) {}
}

async function submitExpense(e) {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.target));
    data.status = 'submitted';
    data.submitted_by = 'Current User';
    data.created_at = new Date().toISOString();
    try {
        const res = await fetch('/api/financial/expenses', {
            method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data)
        });
        if (res.ok) { closeModal(); e.target.reset(); loadExpenses(); }
    } catch(err) { console.error('Failed to add expense:', err); }
}

function exportCSV() {
    if (!allExpenses.length) { alert('No expenses to export'); return; }
    const headers = ['Date','Description','Category','Project','Vendor','Amount','Status','Notes'];
    const rows = allExpenses.map(e => [
        e.date || '', (e.description||'').replace(/,/g,';'), e.category||'', e.job_code||'',
        (e.vendor||'').replace(/,/g,';'), e.amount||0, e.status||'', (e.notes||'').replace(/,/g,';').replace(/\n/g,' ')
    ]);
    let csv = headers.join(',') + '\n' + rows.map(r => r.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = 'titanforge_expenses_' + new Date().toISOString().split('T')[0] + '.csv';
    a.click(); URL.revokeObjectURL(url);
}

async function loadExpenses() {
    // Load projects first for budget data
    try {
        const pres = await fetch('/api/financial/projects');
        if (pres.ok) {
            const pd = await pres.json();
            (pd.projects||[]).forEach(p => { if (p.material_cost) projectBudgets[p.job_code] = p.material_cost; });
            // Populate project filter
            const filterSel = document.getElementById('projectFilter');
            if (filterSel.options.length <= 1) {
                (pd.projects||[]).forEach(p => {
                    filterSel.innerHTML += '<option value="' + p.job_code + '">' + p.job_code + '</option>';
                });
            }
        }
    } catch(e) {}

    try {
        const res = await fetch('/api/financial/expenses');
        if (!res.ok) throw new Error('API error');
        const data = await res.json();
        allExpenses = Array.isArray(data) ? data : (data.expenses || []);
    } catch(err) { console.warn('Could not load expenses:', err); allExpenses = []; }
    updateStats(allExpenses);
    renderCategoryChart(allExpenses);
    applyFilters();
}

document.getElementById('expenseModal').addEventListener('click', function(e) { if (e.target === this) closeModal(); });
loadExpenses();
</script>
"""
