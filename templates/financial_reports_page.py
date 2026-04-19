"""
TitanForge v4 — Financial Reports
===================================
P&L, balance sheet, and cash flow reports with date range filters.
"""

FINANCIAL_REPORTS_PAGE_HTML = r"""
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
    .fr-container {
        max-width: 1400px; margin: 0 auto; padding: 24px 32px;
        font-family: 'Inter', system-ui, -apple-system, sans-serif; color: var(--tf-text);
    }
    .page-header { margin-bottom: 28px; }
    .page-header h1 { font-size: 28px; font-weight: 800; margin: 0 0 6px 0; }
    .page-header p { font-size: 14px; color: var(--tf-muted); margin: 0; }

    .toolbar {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 24px; flex-wrap: wrap; gap: 12px;
    }
    .toolbar-left { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
    .toolbar select, .toolbar input[type="date"] {
        background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06);
        border-radius: 8px; padding: 10px 16px; color: var(--tf-text); font-size: 14px; cursor: pointer;
    }
    .btn-gold {
        background: var(--tf-gold); color: #0f172a; border: none; border-radius: 8px;
        padding: 10px 20px; font-weight: 700; font-size: 14px; cursor: pointer;
    }
    .btn-gold:hover { opacity: 0.9; }

    .report-tabs {
        display: flex; gap: 4px; margin-bottom: 24px; background: var(--tf-card);
        border-radius: 10px; padding: 4px; width: fit-content;
    }
    .report-tab {
        padding: 10px 20px; border-radius: 8px; cursor: pointer; font-size: 14px;
        font-weight: 600; color: var(--tf-muted); border: none; background: none; transition: all 0.2s;
    }
    .report-tab.active { background: var(--tf-gold); color: #0f172a; }
    .report-tab:hover:not(.active) { color: var(--tf-text); }

    .report-card {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06); overflow: hidden;
    }
    .report-card h3 { margin: 0; padding: 20px 24px 0; font-size: 18px; font-weight: 700; }
    .report-card .report-sub { padding: 4px 24px 16px; font-size: 13px; color: var(--tf-muted); }

    .report-section { padding: 0 24px 24px; }
    .report-section h4 {
        font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px;
        color: var(--tf-muted); margin: 20px 0 12px; padding-bottom: 8px;
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .report-line {
        display: flex; justify-content: space-between; padding: 8px 0;
        font-size: 14px; border-bottom: 1px solid rgba(255,255,255,0.03);
    }
    .report-line:last-child { border-bottom: none; }
    .report-line .rl-label { color: var(--tf-muted); }
    .report-line .rl-value { font-weight: 600; }
    .report-total {
        display: flex; justify-content: space-between; padding: 12px 0;
        font-size: 16px; font-weight: 800; border-top: 2px solid rgba(255,255,255,0.1);
        margin-top: 8px;
    }
    .report-total .positive { color: var(--tf-green); }
    .report-total .negative { color: var(--tf-red); }

    .report-panel { display: none; }
    .report-panel.active { display: block; }

    .empty-state { text-align: center; padding: 60px 20px; color: var(--tf-muted); }
    .empty-state h3 { color: var(--tf-text); margin-bottom: 8px; }

/* ── Responsive ── */
@media (max-width: 768px) {
    .page-header h1 { font-size: 22px; }
    .toolbar { flex-direction: column; align-items: stretch; }
    .toolbar input[type="text"] { width: 100%; }
    .report-tabs { overflow-x: auto; -webkit-overflow-scrolling: touch; flex-wrap: nowrap; }
    .report-tab { white-space: nowrap; }
    .report-panel { padding: 12px; }
    .report-card { padding: 12px; }
}
@media (max-width: 480px) {
    .toolbar { gap: 8px; }
    .btn-gold { width: 100%; text-align: center; }
}
</style>

<div class="fr-container">
    <div class="page-header">
        <h1>Financial Reports</h1>
        <p>Profit & loss, balance sheet, and cash flow analysis</p>
    </div>

    <div class="toolbar">
        <div class="toolbar-left">
            <input type="date" id="dateFrom" onchange="loadReport()">
            <span style="color:var(--tf-muted)">to</span>
            <input type="date" id="dateTo" onchange="loadReport()">
            <select id="periodSelect" onchange="setPeriod()">
                <option value="month">This Month</option>
                <option value="quarter">This Quarter</option>
                <option value="ytd" selected>Year to Date</option>
                <option value="year">Last 12 Months</option>
                <option value="custom">Custom Range</option>
            </select>
        </div>
        <button class="btn-gold" onclick="exportReport()">Export PDF</button>
    </div>

    <div class="report-tabs">
        <button class="report-tab active" onclick="switchTab('pnl')">Profit & Loss</button>
        <button class="report-tab" onclick="switchTab('balance')">Balance Sheet</button>
        <button class="report-tab" onclick="switchTab('cashflow')">Cash Flow</button>
    </div>

    <div class="report-panel active" id="panel-pnl">
        <div class="report-card">
            <h3>Profit & Loss Statement</h3>
            <div class="report-sub" id="pnl-period">Year to Date</div>
            <div class="report-section">
                <h4>Revenue</h4>
                <div id="pnl-revenue">
                    <div class="report-line"><span class="rl-label">Project Revenue</span><span class="rl-value">$0</span></div>
                    <div class="report-line"><span class="rl-label">Service Revenue</span><span class="rl-value">$0</span></div>
                </div>
                <div class="report-total"><span>Total Revenue</span><span class="positive" id="pnl-total-revenue">$0</span></div>

                <h4>Expenses</h4>
                <div id="pnl-expenses">
                    <div class="report-line"><span class="rl-label">Materials</span><span class="rl-value">$0</span></div>
                    <div class="report-line"><span class="rl-label">Labor</span><span class="rl-value">$0</span></div>
                    <div class="report-line"><span class="rl-label">Equipment</span><span class="rl-value">$0</span></div>
                    <div class="report-line"><span class="rl-label">Overhead</span><span class="rl-value">$0</span></div>
                </div>
                <div class="report-total"><span>Total Expenses</span><span class="negative" id="pnl-total-expenses">$0</span></div>

                <div class="report-total" style="font-size:20px;margin-top:16px;border-top:3px solid var(--tf-gold)">
                    <span>Net Income</span><span id="pnl-net-income" class="positive">$0</span>
                </div>
            </div>
        </div>
    </div>

    <div class="report-panel" id="panel-balance">
        <div class="report-card">
            <h3>Balance Sheet</h3>
            <div class="report-sub">As of current date</div>
            <div class="report-section">
                <h4>Assets</h4>
                <div class="report-line"><span class="rl-label">Cash & Equivalents</span><span class="rl-value">$0</span></div>
                <div class="report-line"><span class="rl-label">Accounts Receivable</span><span class="rl-value">$0</span></div>
                <div class="report-line"><span class="rl-label">Inventory</span><span class="rl-value">$0</span></div>
                <div class="report-line"><span class="rl-label">Equipment (net)</span><span class="rl-value">$0</span></div>
                <div class="report-total"><span>Total Assets</span><span class="positive">$0</span></div>

                <h4>Liabilities</h4>
                <div class="report-line"><span class="rl-label">Accounts Payable</span><span class="rl-value">$0</span></div>
                <div class="report-line"><span class="rl-label">Accrued Expenses</span><span class="rl-value">$0</span></div>
                <div class="report-total"><span>Total Liabilities</span><span class="negative">$0</span></div>

                <div class="report-total" style="font-size:20px;margin-top:16px;border-top:3px solid var(--tf-gold)">
                    <span>Owner's Equity</span><span class="positive">$0</span>
                </div>
            </div>
        </div>
    </div>

    <div class="report-panel" id="panel-cashflow">
        <div class="report-card">
            <h3>Cash Flow Statement</h3>
            <div class="report-sub" id="cf-period">Year to Date</div>
            <div class="report-section">
                <h4>Operating Activities</h4>
                <div class="report-line"><span class="rl-label">Cash from customers</span><span class="rl-value">$0</span></div>
                <div class="report-line"><span class="rl-label">Cash paid to vendors</span><span class="rl-value">$0</span></div>
                <div class="report-line"><span class="rl-label">Cash paid for wages</span><span class="rl-value">$0</span></div>
                <div class="report-total"><span>Net Operating Cash Flow</span><span class="positive">$0</span></div>

                <h4>Investing Activities</h4>
                <div class="report-line"><span class="rl-label">Equipment purchases</span><span class="rl-value">$0</span></div>
                <div class="report-total"><span>Net Investing Cash Flow</span><span class="negative">$0</span></div>

                <div class="report-total" style="font-size:20px;margin-top:16px;border-top:3px solid var(--tf-gold)">
                    <span>Net Change in Cash</span><span class="positive">$0</span>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function switchTab(tab) {
    document.querySelectorAll('.report-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.report-panel').forEach(p => p.classList.remove('active'));
    event.target.classList.add('active');
    document.getElementById('panel-' + tab).classList.add('active');
}

function setPeriod() {
    const period = document.getElementById('periodSelect').value;
    const now = new Date();
    const from = document.getElementById('dateFrom');
    const to = document.getElementById('dateTo');
    to.value = now.toISOString().split('T')[0];

    if (period === 'month') {
        from.value = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split('T')[0];
    } else if (period === 'quarter') {
        const qStart = Math.floor(now.getMonth() / 3) * 3;
        from.value = new Date(now.getFullYear(), qStart, 1).toISOString().split('T')[0];
    } else if (period === 'ytd') {
        from.value = new Date(now.getFullYear(), 0, 1).toISOString().split('T')[0];
    } else if (period === 'year') {
        const y = new Date(now); y.setFullYear(y.getFullYear() - 1);
        from.value = y.toISOString().split('T')[0];
    }
    loadReport();
}

function exportReport() {
    alert('PDF export will be available once financial data is connected.');
}

async function loadReport() {
    // Reports are currently placeholder -- will be populated from API data
    console.log('Report loaded for range:', document.getElementById('dateFrom').value, 'to', document.getElementById('dateTo').value);
}

// Initialize dates
setPeriod();
</script>
"""
