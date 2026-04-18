"""
TitanForge v4 — Financial Dashboard (Production)
==================================================
Real financial overview with KPI cards, revenue by month,
top projects, recent transactions, and quick links.
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
        max-width: 1400px; margin: 0 auto; padding: 24px 32px;
        font-family: 'Inter', 'Segoe UI', sans-serif; color: var(--tf-text);
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
        cursor: pointer;
    }
    .stat-card:hover { border-color: var(--tf-gold); transform: translateY(-2px); }
    .stat-card .label { font-size: 12px; color: var(--tf-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
    .stat-card .value { font-size: 28px; font-weight: 800; }
    .stat-card .sub { font-size: 12px; color: var(--tf-muted); margin-top: 4px; }
    .stat-green .value { color: var(--tf-green); }
    .stat-red .value { color: var(--tf-red); }
    .stat-gold .value { color: var(--tf-gold); }
    .stat-blue .value { color: var(--tf-blue); }

    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }
    .grid-3-1 { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-bottom: 24px; }

    .chart-card {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06); padding: 24px;
    }
    .chart-card h3 { margin: 0 0 16px 0; font-size: 16px; font-weight: 700; }
    .bar-chart { display: flex; align-items: flex-end; gap: 8px; height: 180px; padding-top: 10px; }
    .bar-group { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4px; }
    .bar-pair { display: flex; gap: 2px; align-items: flex-end; width: 100%; justify-content: center; }
    .bar { width: 16px; border-radius: 3px 3px 0 0; transition: height 0.4s; min-height: 2px; }
    .bar-revenue { background: var(--tf-green); }
    .bar-expense { background: var(--tf-red); opacity: 0.7; }
    .bar-profit { background: var(--tf-gold); }
    .bar-label { font-size: 10px; color: var(--tf-muted); }
    .bar-value { font-size: 9px; color: var(--tf-text); font-weight: 600; text-align: center; }

    .chart-legend { display: flex; gap: 16px; margin-top: 12px; justify-content: center; }
    .chart-legend span { font-size: 11px; color: var(--tf-muted); display: flex; align-items: center; gap: 6px; }
    .chart-legend .dot { width: 8px; height: 8px; border-radius: 50%; }

    .top-projects { list-style: none; padding: 0; margin: 0; }
    .top-projects li {
        display: flex; justify-content: space-between; align-items: center;
        padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.04);
    }
    .top-projects li:last-child { border-bottom: none; }
    .tp-rank { width: 24px; height: 24px; background: rgba(212,168,67,0.15); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; color: var(--tf-gold); margin-right: 12px; flex-shrink: 0; }
    .tp-info { flex: 1; }
    .tp-name { font-weight: 600; font-size: 14px; }
    .tp-code { font-size: 11px; color: var(--tf-muted); }
    .tp-value { font-weight: 700; color: var(--tf-green); font-size: 14px; }
    .tp-margin { font-size: 11px; color: var(--tf-muted); text-align: right; }

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

    /* Overdue Alert Bar */
    .alert-bar {
        background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.2);
        border-radius: 10px; padding: 14px 20px; margin-bottom: 20px;
        display: none; align-items: center; gap: 12px; font-size: 14px;
    }
    .alert-bar.visible { display: flex; }
    .alert-bar .alert-icon { font-size: 20px; }
    .alert-bar .alert-text { flex: 1; }
    .alert-bar .alert-text strong { color: var(--tf-red); }
    .alert-bar a { color: var(--tf-red); font-weight: 600; text-decoration: none; }

@media (max-width: 900px) { .grid-2, .grid-3-1 { grid-template-columns: 1fr; } }
@media (max-width: 768px) {
    .page-header h1 { font-size: 22px; }
    .stat-row { grid-template-columns: 1fr 1fr; }
    .fin-table { display: block; overflow-x: auto; }
}
@media (max-width: 480px) { .stat-row { grid-template-columns: 1fr; } }
</style>

<div class="fin-container">
    <div class="page-header">
        <h1>Financial Dashboard</h1>
        <p>Overview of revenue, expenses, and profitability across all projects</p>
    </div>

    <!-- Overdue Alert -->
    <div class="alert-bar" id="overdueAlert">
        <span class="alert-icon">&#9888;</span>
        <span class="alert-text" id="overdueAlertText"></span>
        <a href="/financial/invoices">View Invoices &rarr;</a>
    </div>

    <div class="stat-row">
        <div class="stat-card stat-green" onclick="location.href='/financial/invoices'">
            <div class="label">Total Revenue</div>
            <div class="value" id="stat-revenue">$0</div>
            <div class="sub" id="stat-revenue-sub">Sum of all invoiced amounts</div>
        </div>
        <div class="stat-card stat-red" onclick="location.href='/financial/expenses'">
            <div class="label">Total Expenses</div>
            <div class="value" id="stat-expenses">$0</div>
            <div class="sub">Material + operational costs</div>
        </div>
        <div class="stat-card stat-gold">
            <div class="label">Net Profit</div>
            <div class="value" id="stat-profit">$0</div>
            <div class="sub" id="stat-margin-sub">--% margin</div>
        </div>
        <div class="stat-card stat-blue" onclick="location.href='/financial/invoices'">
            <div class="label">Outstanding</div>
            <div class="value" id="stat-outstanding">$0</div>
            <div class="sub" id="stat-outstanding-sub">Unpaid invoices</div>
        </div>
        <div class="stat-card stat-red" onclick="location.href='/financial/invoices'" id="overdueCard" style="display:none;">
            <div class="label">Overdue</div>
            <div class="value" id="stat-overdue">$0</div>
            <div class="sub" id="stat-overdue-sub">0 invoices</div>
        </div>
    </div>

    <div class="grid-3-1">
        <div class="chart-card">
            <h3>Revenue vs Expenses by Month</h3>
            <div class="bar-chart" id="monthlyChart"></div>
            <div class="chart-legend">
                <span><span class="dot" style="background:var(--tf-green)"></span> Revenue</span>
                <span><span class="dot" style="background:var(--tf-red);opacity:0.7"></span> Expenses</span>
                <span><span class="dot" style="background:var(--tf-gold)"></span> Profit</span>
            </div>
        </div>
        <div class="chart-card">
            <h3>Top 5 Projects by Revenue</h3>
            <ul class="top-projects" id="topProjectsList">
                <li style="justify-content:center;color:var(--tf-muted);font-size:13px;">Loading...</li>
            </ul>
        </div>
    </div>

    <div class="table-card">
        <h3>Recent Transactions</h3>
        <table class="fin-table">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Description</th>
                    <th>Project</th>
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
    const n = Number(val);
    if (Math.abs(n) >= 1000000) return '$' + (n/1000000).toFixed(1) + 'M';
    if (Math.abs(n) >= 1000) return '$' + (n/1000).toFixed(1) + 'K';
    return '$' + n.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}
function formatCurrencyFull(val) {
    if (val == null) return '$0';
    return '$' + Number(val).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
function formatDate(d) {
    if (!d) return '--';
    const dt = new Date(d);
    if (isNaN(dt)) return d;
    return dt.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}
function monthLabel(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    if (isNaN(d)) return '';
    return d.toLocaleDateString('en-US', { month: 'short' });
}

function renderMonthlyChart(transactions) {
    const monthly = {};
    transactions.forEach(t => {
        const d = t.date || t.created_at || '';
        if (!d) return;
        const key = d.substring(0, 7); // YYYY-MM
        if (!monthly[key]) monthly[key] = { revenue: 0, expenses: 0 };
        const sell = Number(t.sell_price) || 0;
        const cost = Number(t.material_cost) || 0;
        monthly[key].revenue += sell;
        monthly[key].expenses += cost;
    });

    const months = Object.entries(monthly).sort((a, b) => a[0].localeCompare(b[0])).slice(-12);
    const chart = document.getElementById('monthlyChart');
    if (!months.length) {
        chart.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:180px;color:var(--tf-muted);font-size:13px;">No monthly data yet</div>';
        return;
    }
    const maxVal = Math.max(...months.map(([_, v]) => Math.max(v.revenue, v.expenses)), 1);
    chart.innerHTML = months.map(([key, v]) => {
        const profit = v.revenue - v.expenses;
        const revH = Math.max(2, (v.revenue / maxVal) * 150);
        const expH = Math.max(2, (v.expenses / maxVal) * 150);
        const profH = Math.max(2, (Math.abs(profit) / maxVal) * 150);
        const mLabel = new Date(key + '-01').toLocaleDateString('en-US', { month: 'short' });
        return '<div class="bar-group">' +
            '<div class="bar-pair">' +
            '<div class="bar bar-revenue" style="height:' + revH + 'px" title="Revenue: ' + formatCurrencyFull(v.revenue) + '"></div>' +
            '<div class="bar bar-expense" style="height:' + expH + 'px" title="Expenses: ' + formatCurrencyFull(v.expenses) + '"></div>' +
            '</div>' +
            '<div class="bar-label">' + mLabel + '</div>' +
            '</div>';
    }).join('');
}

function renderTopProjects(transactions) {
    const list = document.getElementById('topProjectsList');
    const sorted = [...transactions].filter(t => Number(t.sell_price) > 0)
        .sort((a, b) => (Number(b.sell_price)||0) - (Number(a.sell_price)||0))
        .slice(0, 5);
    if (!sorted.length) {
        list.innerHTML = '<li style="justify-content:center;color:var(--tf-muted);font-size:13px;">No project revenue data yet</li>';
        return;
    }
    list.innerHTML = sorted.map((t, i) => {
        const sell = Number(t.sell_price) || 0;
        const cost = Number(t.material_cost) || 0;
        const margin = sell > 0 ? Math.round(((sell - cost) / sell) * 100) : 0;
        return '<li>' +
            '<span class="tp-rank">' + (i+1) + '</span>' +
            '<div class="tp-info"><div class="tp-name">' + (t.project_name || t.job_code) + '</div><div class="tp-code">' + (t.job_code||'') + '</div></div>' +
            '<div style="text-align:right"><div class="tp-value">' + formatCurrency(sell) + '</div><div class="tp-margin">' + margin + '% margin</div></div>' +
            '</li>';
    }).join('');
}

function renderTransactions(transactions, invoices, expenses) {
    const tbody = document.getElementById('transactionsBody');
    // Combine invoices and expenses into a unified feed
    let feed = [];

    // Add invoices as income
    (invoices || []).forEach(inv => {
        feed.push({
            date: inv.invoice_date || inv.created_at || inv.date || '',
            description: (inv.invoice_number || inv.id || '') + ' - ' + (inv.customer || 'Invoice'),
            project: inv.project_name || inv.project || '',
            type: 'income',
            amount: Number(inv.amount) || 0,
        });
    });

    // Add expenses
    (expenses || []).forEach(exp => {
        feed.push({
            date: exp.date || exp.created_at || '',
            description: exp.description || 'Expense',
            project: exp.job_code || '',
            type: 'expense',
            amount: Number(exp.amount) || 0,
        });
    });

    // If no invoices/expenses yet, use transaction data from summary
    if (!feed.length && transactions && transactions.length) {
        transactions.forEach(t => {
            if (t.sell_price) {
                feed.push({
                    date: t.date || '', description: (t.project_name || t.job_code) + ' - Revenue',
                    project: t.job_code || '', type: 'income', amount: Number(t.sell_price) || 0
                });
            }
        });
    }

    // Sort by date descending, take 20
    feed.sort((a, b) => (b.date || '').localeCompare(a.date || ''));
    feed = feed.slice(0, 20);

    if (!feed.length) {
        tbody.innerHTML = '<tr><td colspan="5" class="empty-state"><h3>No transactions yet</h3><p>Financial data will appear here as invoices and expenses are recorded</p></td></tr>';
        return;
    }
    tbody.innerHTML = feed.map(t => '<tr>' +
        '<td style="color:var(--tf-muted)">' + formatDate(t.date) + '</td>' +
        '<td style="font-weight:600">' + t.description + '</td>' +
        '<td style="color:var(--tf-muted)">' + (t.project || '--') + '</td>' +
        '<td><span class="badge badge-' + t.type + '">' + (t.type === 'income' ? 'Income' : 'Expense') + '</span></td>' +
        '<td style="font-weight:700;color:' + (t.type === 'income' ? 'var(--tf-green)' : 'var(--tf-red)') + '">' + (t.type === 'income' ? '+' : '-') + formatCurrencyFull(Math.abs(t.amount)) + '</td>' +
        '</tr>').join('');
}

async function loadDashboard() {
    let summaryData = null, invoicesData = [], expensesData = [];
    try {
        const [sumRes, invRes, expRes] = await Promise.all([
            fetch('/api/financial/summary'),
            fetch('/api/financial/invoices'),
            fetch('/api/financial/expenses')
        ]);
        if (sumRes.ok) summaryData = await sumRes.json();
        if (invRes.ok) {
            const id = await invRes.json();
            invoicesData = id.invoices || (Array.isArray(id) ? id : []);
        }
        if (expRes.ok) {
            const ed = await expRes.json();
            expensesData = ed.expenses || (Array.isArray(ed) ? ed : []);
        }
    } catch(err) {
        console.warn('Could not load financial data:', err);
        return;
    }

    if (summaryData) {
        const revenue = summaryData.revenue || 0;
        const expenses = summaryData.expenses || 0;
        const profit = summaryData.profit || 0;
        const outstanding = summaryData.outstanding || 0;
        const margin = revenue > 0 ? Math.round((profit / revenue) * 100) : 0;

        document.getElementById('stat-revenue').textContent = formatCurrency(revenue);
        document.getElementById('stat-expenses').textContent = formatCurrency(expenses);
        document.getElementById('stat-profit').textContent = formatCurrency(profit);
        document.getElementById('stat-margin-sub').textContent = margin + '% margin';
        document.getElementById('stat-outstanding').textContent = formatCurrency(outstanding);

        // Count overdue invoices
        const overdueInvs = invoicesData.filter(inv => {
            const s = (inv.status || 'draft').toLowerCase();
            return ['sent','viewed'].includes(s) && inv.due_date && new Date(inv.due_date) < new Date();
        });
        const overdueAmt = overdueInvs.reduce((s, i) => s + (Number(i.amount) || 0), 0);
        if (overdueInvs.length > 0) {
            document.getElementById('overdueCard').style.display = '';
            document.getElementById('stat-overdue').textContent = formatCurrency(overdueAmt);
            document.getElementById('stat-overdue-sub').textContent = overdueInvs.length + ' invoice' + (overdueInvs.length !== 1 ? 's' : '');
            const alertBar = document.getElementById('overdueAlert');
            alertBar.classList.add('visible');
            document.getElementById('overdueAlertText').innerHTML = '<strong>' + overdueInvs.length + ' overdue invoice' + (overdueInvs.length !== 1 ? 's' : '') + '</strong> totaling ' + formatCurrencyFull(overdueAmt) + ' require attention.';
        }

        document.getElementById('stat-outstanding-sub').textContent = invoicesData.filter(i => ['sent','viewed','draft'].includes((i.status||'draft').toLowerCase())).length + ' unpaid invoices';

        renderMonthlyChart(summaryData.transactions || []);
        renderTopProjects(summaryData.transactions || []);
    }

    renderTransactions(summaryData ? summaryData.transactions : [], invoicesData, expensesData);
}

loadDashboard();
</script>
"""
