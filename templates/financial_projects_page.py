"""
TitanForge v4 — Project Financials (Production)
=================================================
Per-project profitability view with budget vs actual,
expandable details, and visual indicators.
"""

FINANCIAL_PROJECTS_PAGE_HTML = r"""
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
    .pf-container {
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

    /* Project Cards */
    .project-list { display: flex; flex-direction: column; gap: 12px; }
    .project-row {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06);
        overflow: hidden; transition: border-color 0.2s;
    }
    .project-row:hover { border-color: rgba(255,255,255,0.12); }
    .project-summary {
        display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr 1fr 80px;
        align-items: center; padding: 16px 20px; cursor: pointer; gap: 12px;
    }
    .project-summary:hover { background: rgba(255,255,255,0.02); }
    .ps-name { font-weight: 700; font-size: 14px; }
    .ps-code { font-size: 11px; color: var(--tf-muted); }
    .ps-customer { font-size: 13px; color: var(--tf-muted); }
    .ps-val { font-weight: 700; font-size: 14px; }
    .ps-val.green { color: var(--tf-green); }
    .ps-val.red { color: var(--tf-red); }
    .ps-val.gold { color: var(--tf-gold); }

    .budget-bar-container { display: flex; align-items: center; gap: 8px; }
    .budget-bar {
        flex: 1; height: 8px; background: rgba(255,255,255,0.06); border-radius: 4px; overflow: hidden; max-width: 100px;
    }
    .budget-fill { height: 100%; border-radius: 4px; transition: width 0.3s; }
    .budget-ok { background: var(--tf-green); }
    .budget-warn { background: var(--tf-gold); }
    .budget-over { background: var(--tf-red); }
    .budget-pct { font-size: 12px; color: var(--tf-muted); min-width: 35px; }

    .profit-indicator {
        display: inline-flex; align-items: center; gap: 4px; padding: 3px 10px;
        border-radius: 16px; font-size: 12px; font-weight: 700;
    }
    .profit-pos { background: rgba(16,185,129,0.12); color: #34d399; }
    .profit-neg { background: rgba(239,68,68,0.12); color: #f87171; }

    .expand-btn {
        background: none; border: none; color: var(--tf-muted); cursor: pointer;
        font-size: 16px; padding: 4px; transition: transform 0.2s;
    }
    .expand-btn.open { transform: rotate(180deg); }

    /* Expanded detail */
    .project-detail {
        display: none; padding: 0 20px 20px; border-top: 1px solid rgba(255,255,255,0.04);
    }
    .project-detail.open { display: block; }
    .detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 16px; }
    .detail-card {
        background: rgba(255,255,255,0.02); border-radius: 8px; padding: 16px;
    }
    .detail-card h4 { font-size: 12px; color: var(--tf-muted); text-transform: uppercase; letter-spacing: 0.5px; margin: 0 0 12px 0; }
    .cost-row { display: flex; justify-content: space-between; padding: 6px 0; font-size: 13px; border-bottom: 1px solid rgba(255,255,255,0.03); }
    .cost-row:last-child { border-bottom: none; }
    .cost-label { color: var(--tf-muted); }
    .cost-value { font-weight: 600; }

    .visual-bar-container { margin-top: 12px; }
    .visual-bar-label { display: flex; justify-content: space-between; font-size: 11px; color: var(--tf-muted); margin-bottom: 4px; }
    .visual-bar { height: 20px; background: rgba(255,255,255,0.04); border-radius: 4px; overflow: hidden; position: relative; }
    .visual-bar-fill { height: 100%; border-radius: 4px; transition: width 0.4s; }
    .visual-bar-text { position: absolute; left: 8px; top: 50%; transform: translateY(-50%); font-size: 10px; font-weight: 600; color: #fff; }

    .col-header {
        display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr 1fr 80px;
        padding: 10px 20px; font-size: 11px; color: var(--tf-muted);
        text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;
    }

    .empty-state { text-align: center; padding: 60px 20px; color: var(--tf-muted); }
    .empty-state h3 { color: var(--tf-text); margin-bottom: 8px; }

/* Responsive */
@media (max-width: 768px) {
    .page-header h1 { font-size: 22px; }
    .toolbar { flex-direction: column; align-items: stretch; }
    .toolbar input[type="text"] { width: 100%; }
    .stat-row { grid-template-columns: 1fr 1fr; gap: 10px; }
    .project-summary, .col-header { grid-template-columns: 1fr 1fr; gap: 8px; }
    .detail-grid { grid-template-columns: 1fr; }
}
@media (max-width: 480px) {
    .stat-row { grid-template-columns: 1fr; }
}
</style>

<div class="pf-container">
    <div class="page-header">
        <h1>Project Financials</h1>
        <p>Track budget vs actual spending and profitability per project</p>
    </div>

    <div class="stat-row">
        <div class="stat-card stat-blue">
            <div class="label">Active Projects</div>
            <div class="value" id="stat-active">0</div>
            <div class="sub">With financial data</div>
        </div>
        <div class="stat-card stat-gold">
            <div class="label">Total Revenue</div>
            <div class="value" id="stat-revenue">$0</div>
            <div class="sub">Sum of sell prices</div>
        </div>
        <div class="stat-card stat-red">
            <div class="label">Total Costs</div>
            <div class="value" id="stat-costs">$0</div>
            <div class="sub">Material costs</div>
        </div>
        <div class="stat-card stat-green">
            <div class="label">Avg Margin</div>
            <div class="value" id="stat-margin">--%</div>
            <div class="sub">Across projects</div>
        </div>
    </div>

    <div class="toolbar">
        <div class="toolbar-left">
            <input type="text" id="searchInput" placeholder="Search projects..." oninput="applyFilters()">
            <select id="statusFilter" onchange="applyFilters()">
                <option value="">All Projects</option>
                <option value="profitable">Profitable</option>
                <option value="over-budget">Over Budget</option>
            </select>
            <select id="sortBy" onchange="applyFilters()">
                <option value="revenue">Sort: Revenue</option>
                <option value="margin">Sort: Margin</option>
                <option value="name">Sort: Name</option>
                <option value="profit">Sort: Profit</option>
            </select>
        </div>
    </div>

    <div class="col-header">
        <span>Project</span><span>Budget (Cost)</span><span>Revenue</span><span>Expenses</span><span>Profit</span><span>Margin</span><span></span>
    </div>
    <div class="project-list" id="projectsList">
        <div class="empty-state">Loading...</div>
    </div>
</div>

<script>
let allProjects = [];
let expensesByProject = {};

function formatCurrency(val) {
    if (val == null) return '$0';
    const n = Number(val);
    if (Math.abs(n) >= 1000000) return '$' + (n/1000000).toFixed(1) + 'M';
    if (Math.abs(n) >= 1000) return '$' + (n/1000).toFixed(1) + 'K';
    return '$' + n.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}
function formatCurrencyFull(val) {
    if (val == null) return '$0.00';
    return '$' + Number(val).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function updateStats(projects) {
    const withData = projects.filter(p => p.sell_price || p.material_cost);
    document.getElementById('stat-active').textContent = withData.length;
    const totalRev = withData.reduce((s, p) => s + (Number(p.sell_price) || 0), 0);
    const totalCost = withData.reduce((s, p) => s + (Number(p.material_cost) || 0), 0);
    document.getElementById('stat-revenue').textContent = formatCurrency(totalRev);
    document.getElementById('stat-costs').textContent = formatCurrency(totalCost);
    const withMargin = withData.filter(p => p.margin != null);
    if (withMargin.length) {
        const avg = withMargin.reduce((s, p) => s + (Number(p.margin) || 0), 0) / withMargin.length;
        document.getElementById('stat-margin').textContent = Math.round(avg) + '%';
    }
}

function getProjectExpenses(jobCode) {
    return expensesByProject[jobCode] || 0;
}

function renderProjects(projects) {
    const container = document.getElementById('projectsList');
    if (!projects.length) {
        container.innerHTML = '<div class="empty-state"><h3>No projects found</h3><p>Project financial data will appear here</p></div>';
        return;
    }
    container.innerHTML = projects.map(p => {
        const budget = Number(p.material_cost) || 0;
        const revenue = Number(p.sell_price) || 0;
        const expenses = getProjectExpenses(p.job_code) || budget;
        const profit = revenue - expenses;
        const margin = p.margin != null ? Number(p.margin) : (revenue > 0 ? Math.round((profit / revenue) * 100) : 0);
        const budgetPct = budget > 0 ? Math.round((expenses / budget) * 100) : 0;
        const barClass = budgetPct > 100 ? 'budget-over' : budgetPct > 80 ? 'budget-warn' : 'budget-ok';

        // Overhead estimate (15% of material)
        const overhead = budget * 0.15;
        const labor = budget * 0.25;
        const materialActual = budget * 0.60;

        return '<div class="project-row" id="proj-' + p.job_code + '">' +
            '<div class="project-summary" onclick="toggleDetail(\'' + p.job_code + '\')">' +
                '<div><div class="ps-name">' + (p.project_name || p.job_code) + '</div><div class="ps-code">' + p.job_code + ' <span class="ps-customer">' + (p.customer ? '| ' + p.customer : '') + '</span></div></div>' +
                '<div class="ps-val">' + formatCurrency(budget) + '</div>' +
                '<div class="ps-val green">' + formatCurrency(revenue) + '</div>' +
                '<div class="ps-val red">' + formatCurrency(expenses) + '</div>' +
                '<div><span class="profit-indicator ' + (profit >= 0 ? 'profit-pos' : 'profit-neg') + '">' + (profit >= 0 ? '+' : '') + formatCurrency(profit) + '</span></div>' +
                '<div class="budget-bar-container"><div class="budget-bar"><div class="budget-fill ' + barClass + '" style="width:' + Math.min(budgetPct, 100) + '%"></div></div><span class="budget-pct">' + margin + '%</span></div>' +
                '<button class="expand-btn" id="expand-' + p.job_code + '">&#9660;</button>' +
            '</div>' +
            '<div class="project-detail" id="detail-' + p.job_code + '">' +
                '<div class="detail-grid">' +
                    '<div class="detail-card">' +
                        '<h4>Cost Breakdown</h4>' +
                        '<div class="cost-row"><span class="cost-label">Materials</span><span class="cost-value">' + formatCurrencyFull(materialActual) + '</span></div>' +
                        '<div class="cost-row"><span class="cost-label">Labor (est.)</span><span class="cost-value">' + formatCurrencyFull(labor) + '</span></div>' +
                        '<div class="cost-row"><span class="cost-label">Overhead (est.)</span><span class="cost-value">' + formatCurrencyFull(overhead) + '</span></div>' +
                        '<div class="cost-row" style="border-top:1px solid rgba(255,255,255,0.06);padding-top:8px;margin-top:4px;"><span class="cost-label" style="font-weight:700;">Total Cost</span><span class="cost-value" style="color:var(--tf-red)">' + formatCurrencyFull(expenses) + '</span></div>' +
                    '</div>' +
                    '<div class="detail-card">' +
                        '<h4>Revenue Summary</h4>' +
                        '<div class="cost-row"><span class="cost-label">Sell Price / Quote</span><span class="cost-value" style="color:var(--tf-green)">' + formatCurrencyFull(revenue) + '</span></div>' +
                        '<div class="cost-row"><span class="cost-label">Total Costs</span><span class="cost-value" style="color:var(--tf-red)">' + formatCurrencyFull(expenses) + '</span></div>' +
                        '<div class="cost-row" style="border-top:1px solid rgba(255,255,255,0.06);padding-top:8px;margin-top:4px;"><span class="cost-label" style="font-weight:700;">Net Profit</span><span class="cost-value" style="color:' + (profit >= 0 ? 'var(--tf-green)' : 'var(--tf-red)') + '">' + (profit >= 0 ? '+' : '') + formatCurrencyFull(profit) + '</span></div>' +
                        '<div class="cost-row"><span class="cost-label">Profit Margin</span><span class="cost-value">' + margin + '%</span></div>' +
                    '</div>' +
                '</div>' +
                '<div class="visual-bar-container" style="margin-top:16px;">' +
                    '<div class="visual-bar-label"><span>Budget vs Actual</span><span>' + formatCurrency(expenses) + ' of ' + formatCurrency(budget) + '</span></div>' +
                    '<div class="visual-bar"><div class="visual-bar-fill ' + barClass + '" style="width:' + Math.min(budgetPct, 100) + '%"></div><span class="visual-bar-text">' + budgetPct + '%</span></div>' +
                '</div>' +
                '<div class="visual-bar-container" style="margin-top:10px;">' +
                    '<div class="visual-bar-label"><span>Revenue vs Cost</span><span>' + formatCurrency(revenue) + ' revenue</span></div>' +
                    '<div class="visual-bar"><div class="visual-bar-fill" style="width:' + (revenue > 0 ? Math.min(100, Math.round((expenses/revenue)*100)) : 0) + '%;background:var(--tf-green);opacity:0.6"></div><span class="visual-bar-text">' + (revenue > 0 ? (100 - Math.round((expenses/revenue)*100)) : 0) + '% profit</span></div>' +
                '</div>' +
            '</div>' +
        '</div>';
    }).join('');
}

function toggleDetail(jobCode) {
    const detail = document.getElementById('detail-' + jobCode);
    const btn = document.getElementById('expand-' + jobCode);
    if (detail) {
        detail.classList.toggle('open');
        btn.classList.toggle('open');
    }
}

function applyFilters() {
    const q = (document.getElementById('searchInput').value || '').toLowerCase();
    const status = document.getElementById('statusFilter').value;
    const sortBy = document.getElementById('sortBy').value;
    let filtered = allProjects.filter(p => {
        if (q && !(p.project_name||'').toLowerCase().includes(q) && !(p.job_code||'').toLowerCase().includes(q) && !(p.customer||'').toLowerCase().includes(q)) return false;
        if (status === 'profitable') {
            const rev = Number(p.sell_price) || 0;
            const cost = Number(p.material_cost) || 0;
            if (rev <= cost) return false;
        }
        if (status === 'over-budget') {
            const budget = Number(p.material_cost) || 0;
            const exp = getProjectExpenses(p.job_code) || budget;
            if (budget <= 0 || exp <= budget) return false;
        }
        return true;
    });
    // Sort
    filtered.sort((a, b) => {
        if (sortBy === 'revenue') return (Number(b.sell_price)||0) - (Number(a.sell_price)||0);
        if (sortBy === 'margin') return (Number(b.margin)||0) - (Number(a.margin)||0);
        if (sortBy === 'profit') {
            const pa = (Number(a.sell_price)||0) - (Number(a.material_cost)||0);
            const pb = (Number(b.sell_price)||0) - (Number(b.material_cost)||0);
            return pb - pa;
        }
        return (a.project_name||'').localeCompare(b.project_name||'');
    });
    renderProjects(filtered);
}

async function loadProjects() {
    // Load expenses to know actual spend per project
    try {
        const eres = await fetch('/api/financial/expenses');
        if (eres.ok) {
            const ed = await eres.json();
            (ed.expenses || []).forEach(e => {
                if (e.job_code) {
                    expensesByProject[e.job_code] = (expensesByProject[e.job_code] || 0) + (Number(e.amount) || 0);
                }
            });
        }
    } catch(e) {}

    try {
        const res = await fetch('/api/financial/projects');
        if (!res.ok) throw new Error('API error');
        const data = await res.json();
        allProjects = Array.isArray(data) ? data : (data.projects || []);
    } catch(err) { console.warn('Could not load projects:', err); allProjects = []; }
    updateStats(allProjects);
    applyFilters();
}

loadProjects();
</script>
"""
