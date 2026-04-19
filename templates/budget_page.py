"""
TitanForge v4 — Budget Overview
=================================
Budget management with category breakdowns, actual vs planned, and forecasting.
"""

BUDGET_PAGE_HTML = r"""
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
    .budget-container {
        max-width: 1400px; margin: 0 auto; padding: 24px 32px;
        font-family: 'Inter', system-ui, -apple-system, sans-serif; color: var(--tf-text);
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
    .toolbar select {
        background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06);
        border-radius: 8px; padding: 10px 16px; color: var(--tf-text); font-size: 14px; cursor: pointer;
    }
    .btn-gold {
        background: var(--tf-gold); color: #0f172a; border: none; border-radius: 8px;
        padding: 10px 20px; font-weight: 700; font-size: 14px; cursor: pointer;
    }
    .btn-gold:hover { opacity: 0.9; }

    .budget-grid {
        display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px;
    }
    @media (max-width: 900px) { .budget-grid { grid-template-columns: 1fr; } }

    .card {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06); padding: 24px;
    }
    .card h3 { margin: 0 0 16px 0; font-size: 16px; font-weight: 700; }

    .category-row {
        display: flex; align-items: center; gap: 12px; padding: 12px 0;
        border-bottom: 1px solid rgba(255,255,255,0.04);
    }
    .category-row:last-child { border-bottom: none; }
    .cat-name { flex: 1; font-size: 14px; font-weight: 600; }
    .cat-amounts { display: flex; gap: 20px; align-items: center; font-size: 13px; }
    .cat-planned { color: var(--tf-muted); }
    .cat-actual { font-weight: 700; }
    .cat-bar-wrap { width: 120px; }
    .cat-bar { height: 6px; background: rgba(255,255,255,0.06); border-radius: 3px; overflow: hidden; }
    .cat-bar-fill { height: 100%; border-radius: 3px; transition: width 0.3s; }
    .cat-ok { background: var(--tf-green); }
    .cat-warn { background: var(--tf-gold); }
    .cat-over { background: var(--tf-red); }
    .cat-pct { font-size: 11px; color: var(--tf-muted); margin-top: 2px; }

    .forecast-item {
        display: flex; justify-content: space-between; padding: 10px 0;
        border-bottom: 1px solid rgba(255,255,255,0.04); font-size: 14px;
    }
    .forecast-item:last-child { border-bottom: none; }

    .table-card {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06); overflow: hidden;
    }
    .table-card h3 { margin: 0; padding: 20px 24px 16px; font-size: 16px; font-weight: 700; }
    .budget-table { width: 100%; border-collapse: collapse; font-size: 14px; }
    .budget-table th {
        text-align: left; padding: 12px 16px; font-size: 11px;
        text-transform: uppercase; letter-spacing: 0.5px; color: var(--tf-muted);
        border-bottom: 1px solid rgba(255,255,255,0.06); font-weight: 600;
    }
    .budget-table td {
        padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.04); vertical-align: middle;
    }
    .budget-table tr:hover { background: rgba(255,255,255,0.02); }
    .budget-table tr:last-child td { border-bottom: none; }

    .variance-positive { color: var(--tf-green); font-weight: 600; }
    .variance-negative { color: var(--tf-red); font-weight: 600; }

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
        width: 480px; max-width: 95vw; max-height: 90vh; overflow-y: auto;
    }
    .modal h2 { margin: 0 0 24px 0; font-size: 20px; font-weight: 700; }
    .form-group { margin-bottom: 16px; }
    .form-group label {
        display: block; font-size: 12px; color: var(--tf-muted);
        text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; font-weight: 600;
    }
    .form-group input, .form-group select {
        width: 100%; background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px;
        box-sizing: border-box;
    }
    .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 24px; }
    .btn-secondary {
        background: transparent; border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px; padding: 10px 20px; color: var(--tf-muted);
        font-weight: 600; font-size: 14px; cursor: pointer;
    }
    .btn-secondary:hover { color: var(--tf-text); border-color: rgba(255,255,255,0.2); }
</style>

<div class="budget-container">
    <div class="page-header">
        <h1>Budget Overview</h1>
        <p>Track planned versus actual spending with category breakdowns and forecasting</p>
    </div>

    <div class="stat-row">
        <div class="stat-card stat-gold">
            <div class="label">Total Budget</div>
            <div class="value" id="stat-budget">$0</div>
            <div class="sub">Annual planned</div>
        </div>
        <div class="stat-card stat-red">
            <div class="label">Actual Spend</div>
            <div class="value" id="stat-actual">$0</div>
            <div class="sub">Year to date</div>
        </div>
        <div class="stat-card stat-green">
            <div class="label">Remaining</div>
            <div class="value" id="stat-remaining">$0</div>
            <div class="sub">Available budget</div>
        </div>
        <div class="stat-card stat-blue">
            <div class="label">Budget Used</div>
            <div class="value" id="stat-pct">0%</div>
            <div class="sub">Of total allocation</div>
        </div>
    </div>

    <div class="toolbar">
        <div class="toolbar-left">
            <select id="yearFilter" onchange="loadBudget()">
                <option value="2026">2026</option>
                <option value="2025">2025</option>
            </select>
        </div>
        <button class="btn-gold" onclick="openModal()">+ Set Budget</button>
    </div>

    <div class="budget-grid">
        <div class="card">
            <h3>Budget by Category</h3>
            <div id="categoryBreakdown">
                <div class="empty-state"><p>No budget categories defined yet</p></div>
            </div>
        </div>
        <div class="card">
            <h3>Forecast</h3>
            <div id="forecastSection">
                <div class="forecast-item">
                    <span style="color:var(--tf-muted)">Projected Year-End Spend</span>
                    <span style="font-weight:700" id="forecast-yearend">$0</span>
                </div>
                <div class="forecast-item">
                    <span style="color:var(--tf-muted)">Monthly Burn Rate</span>
                    <span style="font-weight:700" id="forecast-burn">$0</span>
                </div>
                <div class="forecast-item">
                    <span style="color:var(--tf-muted)">Months of Budget Left</span>
                    <span style="font-weight:700" id="forecast-months">--</span>
                </div>
                <div class="forecast-item">
                    <span style="color:var(--tf-muted)">Variance from Plan</span>
                    <span style="font-weight:700" id="forecast-variance">$0</span>
                </div>
            </div>
        </div>
    </div>

    <div class="table-card">
        <h3>Monthly Breakdown</h3>
        <table class="budget-table">
            <thead>
                <tr>
                    <th>Month</th>
                    <th>Planned</th>
                    <th>Actual</th>
                    <th>Variance</th>
                    <th>Cumulative</th>
                </tr>
            </thead>
            <tbody id="monthlyBody">
                <tr><td colspan="5" class="empty-state"><h3>No budget data yet</h3><p>Set your annual budget to see monthly breakdowns</p></td></tr>
            </tbody>
        </table>
    </div>
</div>

<div class="modal-overlay" id="budgetModal">
    <div class="modal">
        <h2>Set Budget</h2>
        <form id="budgetForm" onsubmit="submitBudget(event)">
            <div class="form-row">
                <div class="form-group">
                    <label>Category</label>
                    <select name="category">
                        <option value="materials">Materials</option>
                        <option value="labor">Labor</option>
                        <option value="equipment">Equipment</option>
                        <option value="overhead">Overhead</option>
                        <option value="subcontractors">Subcontractors</option>
                        <option value="other">Other</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Annual Budget ($)</label>
                    <input type="number" name="amount" required placeholder="0.00" step="0.01">
                </div>
            </div>
            <div class="form-group">
                <label>Year</label>
                <select name="year">
                    <option value="2026">2026</option>
                    <option value="2025">2025</option>
                </select>
            </div>
            <div class="modal-actions">
                <button type="button" class="btn-secondary" onclick="closeModal()">Cancel</button>
                <button type="submit" class="btn-gold">Save Budget</button>
            </div>
        </form>
    </div>
</div>

<script>
const defaultCategories = [
    { name: 'Materials', planned: 0, actual: 0 },
    { name: 'Labor', planned: 0, actual: 0 },
    { name: 'Equipment', planned: 0, actual: 0 },
    { name: 'Overhead', planned: 0, actual: 0 },
    { name: 'Subcontractors', planned: 0, actual: 0 }
];

function formatCurrency(val) {
    if (val == null) return '$0';
    return '$' + Number(val).toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}

function renderCategories(categories) {
    const el = document.getElementById('categoryBreakdown');
    if (!categories || !categories.length) {
        el.innerHTML = '<div class="empty-state"><p>No budget categories defined yet</p></div>';
        return;
    }
    el.innerHTML = categories.map(c => {
        const pct = c.planned > 0 ? Math.round((c.actual / c.planned) * 100) : 0;
        const barClass = pct > 100 ? 'cat-over' : pct > 80 ? 'cat-warn' : 'cat-ok';
        return `<div class="category-row">
            <span class="cat-name">${c.name}</span>
            <div class="cat-amounts">
                <span class="cat-planned">${formatCurrency(c.planned)}</span>
                <span class="cat-actual">${formatCurrency(c.actual)}</span>
            </div>
            <div class="cat-bar-wrap">
                <div class="cat-bar"><div class="cat-bar-fill ${barClass}" style="width:${Math.min(pct, 100)}%"></div></div>
                <div class="cat-pct">${pct}% used</div>
            </div>
        </div>`;
    }).join('');
}

function updateStats(budget, actual) {
    document.getElementById('stat-budget').textContent = formatCurrency(budget);
    document.getElementById('stat-actual').textContent = formatCurrency(actual);
    document.getElementById('stat-remaining').textContent = formatCurrency(Math.max(0, budget - actual));
    document.getElementById('stat-pct').textContent = budget > 0 ? Math.round((actual / budget) * 100) + '%' : '0%';

    // Forecast
    const now = new Date();
    const monthsElapsed = now.getMonth() + 1;
    const monthlyBurn = monthsElapsed > 0 ? actual / monthsElapsed : 0;
    const projected = monthlyBurn * 12;
    const remaining = budget - actual;
    const monthsLeft = monthlyBurn > 0 ? Math.round(remaining / monthlyBurn) : '--';

    document.getElementById('forecast-burn').textContent = formatCurrency(monthlyBurn);
    document.getElementById('forecast-yearend').textContent = formatCurrency(projected);
    document.getElementById('forecast-months').textContent = monthsLeft;
    const variance = budget - projected;
    const varEl = document.getElementById('forecast-variance');
    varEl.textContent = (variance >= 0 ? '+' : '') + formatCurrency(variance);
    varEl.style.color = variance >= 0 ? 'var(--tf-green)' : 'var(--tf-red)';
}

function openModal() { document.getElementById('budgetModal').classList.add('active'); }
function closeModal() { document.getElementById('budgetModal').classList.remove('active'); }

async function submitBudget(e) {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.target));
    console.log('Budget saved:', data);
    closeModal();
    e.target.reset();
    alert('Budget entry saved. Data will persist once the backend is connected.');
}

async function loadBudget() {
    renderCategories(defaultCategories);
    updateStats(0, 0);
}

document.getElementById('budgetModal').addEventListener('click', function(e) { if (e.target === this) closeModal(); });
loadBudget();
</script>
"""
