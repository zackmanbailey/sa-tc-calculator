"""
TitanForge v4 — Financial Dashboard
=====================================
Overview of revenue, expenses, profit with recent transactions and charts.
"""

FINANCIAL_DASHBOARD_PAGE_HTML = r"""
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
    .fin-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 24px 32px;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        color: var(--tf-text);
    }
    .page-header { margin-bottom: 28px; }
    .page-header h1 { font-size: 28px; font-weight: 800; margin: 0 0 6px 0; }
    .page-header p { font-size: 14px; color: var(--tf-muted); margin: 0; }

    .stat-row {
        display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
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
    .stat-green .value { color: var(--tf-green); }
    .stat-red .value { color: var(--tf-red); }
    .stat-gold .value { color: var(--tf-gold); }
    .stat-blue .value { color: var(--tf-blue); }

    .toolbar {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 20px; flex-wrap: wrap; gap: 12px;
    }
    .toolbar-left { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
    .toolbar select, .toolbar input[type="date"] {
        background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06);
        border-radius: 8px; padding: 10px 16px; color: var(--tf-text); font-size: 14px; cursor: pointer;
    }

    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }
    @media (max-width: 900px) { .grid-2 { grid-template-columns: 1fr; } }

    .chart-card {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06); padding: 24px;
    }
    .chart-card h3 { margin: 0 0 16px 0; font-size: 16px; font-weight: 700; }
    .chart-placeholder {
        height: 200px; display: flex; align-items: center; justify-content: center;
        border: 1px dashed rgba(255,255,255,0.1); border-radius: 8px; color: var(--tf-muted); font-size: 13px;
    }
    .bar-chart { display: flex; align-items: flex-end; gap: 8px; height: 180px; padding-top: 10px; }
    .bar-group { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4px; }
    .bar { width: 100%; max-width: 40px; border-radius: 4px 4px 0 0; transition: height 0.4s; min-height: 2px; }
    .bar-revenue { background: var(--tf-green); }
    .bar-expense { background: var(--tf-red); opacity: 0.7; }
    .bar-label { font-size: 10px; color: var(--tf-muted); }

    .table-card {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06); overflow: hidden;
    }
    .table-card h3 { margin: 0; padding: 20px 24px 16px; font-size: 16px; font-weight: 700; }
    .fin-table { width: 100%; border-collapse: collapse; font-size: 14px; }
    .fin-table th {
        text-align: left; padding: 12px 16px; font-size: 11px;
        text-transform: uppercase; letter-spacing: 0.5px; color: var(--tf-muted);
        border-bottom: 1px solid rgba(255,255,255,0.06); font-weight: 600;
    }
    .fin-table td {
        padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.04); vertical-align: middle;
    }
    .fin-table tr:hover { background: rgba(255,255,255,0.02); }
    .fin-table tr:last-child td { border-bottom: none; }

    .badge {
        display: inline-block; padding: 4px 10px; border-radius: 20px;
        font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;
    }
    .badge-income { background: rgba(16,185,129,0.15); color: #34d399; }
    .badge-expense { background: rgba(239,68,68,0.15); color: #f87171; }

    .empty-state {
        text-align: center; padding: 60px 20px; color: var(--tf-muted);
    }
    .empty-state h3 { color: var(--tf-text); margin-bottom: 8px; }

    .quick-links { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-top: 24px; }
    .quick-link {
        background: var(--tf-card); border-radius: 10px; border: 1px solid rgba(255,255,255,0.06);
        padding: 16px 20px; text-decoration: none; color: var(--tf-text); font-weight: 600;
        font-size: 14px; transition: border-color 0.2s; display: flex; align-items: center; gap: 10px;
    }
    .quick-link:hover { border-color: var(--tf-gold); }
    .quick-link .ql-icon { font-size: 20px; }
</style>

<div class="fin-container">
    <div class="page-header">
        <h1>Financial Dashboard</h1>
        <p>Overview of revenue, expenses, and profitability across all projects</p>
    </div>

    <div class="stat-row">
        <div class="stat-card stat-green">
            <div class="label">Total Revenue</div>
            <div class="value" id="stat-revenue">$0</div>
            <div class="sub">Year to date</div>
        </div>
        <div class="stat-card stat-red">
            <div class="label">Total Expenses</div>
            <div class="value" id="stat-expenses">$0</div>
            <div class="sub">Year to date</div>
        </div>
        <div class="stat-card stat-gold">
            <div class="label">Net Profit</div>
            <div class="value" id="stat-profit">$0</div>
            <div class="sub">Revenue - Expenses</div>
        </div>
        <div class="stat-card stat-blue">
            <div class="label">Outstanding</div>
            <div class="value" id="stat-outstanding">$0</div>
            <div class="sub">Unpaid invoices</div>
        </div>
    </div>

    <div class="toolbar">
        <div class="toolbar-left">
            <select id="periodFilter" onchange="loadDashboard()">
                <option value="ytd">Year to Date</option>
                <option value="month">This Month</option>
                <option value="quarter">This Quarter</option>
                <option value="all">All Time</option>
            </select>
        </div>
    </div>

    <div class="grid-2">
        <div class="chart-card">
            <h3>Revenue vs Expenses</h3>
            <div class="bar-chart" id="revenueChart">
                <div class="chart-placeholder">No data yet</div>
            </div>
        </div>
        <div class="chart-card">
            <h3>Profit Trend</h3>
            <div class="bar-chart" id="profitChart">
                <div class="chart-placeholder">No data yet</div>
            </div>
        </div>
    </div>

    <div class="table-card">
        <h3>Recent Transactions</h3>
        <table class="fin-table">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Description</th>
                    <th>Category</th>
                    <th>Type</th>
                    <th>Amount</th>
                </tr>
            </thead>
            <tbody id="transactionsBody">
                <tr><td colspan="5" class="empty-state"><h3>No transactions yet</h3><p>Financial data will appear here as invoices and expenses are recorded</p></td></tr>
            </tbody>
        </table>
    </div>

    <div class="quick-links">
        <a class="quick-link" href="/financial/invoices"><span class="ql-icon">&#x1F4C4;</span> Invoices</a>
        <a class="quick-link" href="/financial/expenses"><span class="ql-icon">&#x1F4B3;</span> Expenses</a>
        <a class="quick-link" href="/financial/vendor-bills"><span class="ql-icon">&#x1F9FE;</span> Vendor Bills</a>
        <a class="quick-link" href="/financial/projects"><span class="ql-icon">&#x1F4C1;</span> Project Financials</a>
        <a class="quick-link" href="/financial/equipment"><span class="ql-icon">&#x1F527;</span> Equipment</a>
        <a class="quick-link" href="/financial/reports"><span class="ql-icon">&#x1F4C8;</span> Reports</a>
        <a class="quick-link" href="/budget"><span class="ql-icon">&#x1F4B0;</span> Budget</a>
    </div>
</div>

<script>
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

function renderTransactions(transactions) {
    const tbody = document.getElementById('transactionsBody');
    if (!transactions || !transactions.length) {
        tbody.innerHTML = '<tr><td colspan="5" class="empty-state"><h3>No transactions yet</h3><p>Financial data will appear here as invoices and expenses are recorded</p></td></tr>';
        return;
    }
    tbody.innerHTML = transactions.map(t => `<tr>
        <td style="color:var(--tf-muted)">${formatDate(t.date)}</td>
        <td style="font-weight:600">${t.description || '--'}</td>
        <td style="color:var(--tf-muted)">${t.category || '--'}</td>
        <td><span class="badge badge-${t.type === 'income' ? 'income' : 'expense'}">${t.type || '--'}</span></td>
        <td style="font-weight:700;color:${t.type === 'income' ? 'var(--tf-green)' : 'var(--tf-red)'}">${t.type === 'income' ? '+' : '-'}${formatCurrency(Math.abs(t.amount))}</td>
    </tr>`).join('');
}

async function loadDashboard() {
    try {
        const res = await fetch('/api/financial/summary');
        if (!res.ok) throw new Error('API error');
        const data = await res.json();
        document.getElementById('stat-revenue').textContent = formatCurrency(data.revenue || 0);
        document.getElementById('stat-expenses').textContent = formatCurrency(data.expenses || 0);
        document.getElementById('stat-profit').textContent = formatCurrency(data.profit || 0);
        document.getElementById('stat-outstanding').textContent = formatCurrency(data.outstanding || 0);
        renderTransactions(data.transactions || []);
    } catch(err) {
        console.warn('Could not load financial summary:', err);
    }
}

loadDashboard();
</script>
"""
