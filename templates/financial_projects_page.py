"""
TitanForge v4 — Project Financials
====================================
Per-project financial breakdown with budget vs actual and profitability.
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

    .table-card {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06); overflow: hidden;
    }
    .pf-table { width: 100%; border-collapse: collapse; font-size: 14px; }
    .pf-table th {
        text-align: left; padding: 14px 16px; font-size: 11px;
        text-transform: uppercase; letter-spacing: 0.5px; color: var(--tf-muted);
        border-bottom: 1px solid rgba(255,255,255,0.06); font-weight: 600;
    }
    .pf-table td {
        padding: 14px 16px; border-bottom: 1px solid rgba(255,255,255,0.04); vertical-align: middle;
    }
    .pf-table tr:hover { background: rgba(255,255,255,0.02); }
    .pf-table tr:last-child td { border-bottom: none; }

    .badge {
        display: inline-block; padding: 4px 10px; border-radius: 20px;
        font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;
    }
    .badge-active { background: rgba(16,185,129,0.15); color: #34d399; }
    .badge-completed { background: rgba(59,130,246,0.15); color: #60a5fa; }
    .badge-over-budget { background: rgba(239,68,68,0.15); color: #f87171; }

    .progress-bar {
        height: 6px; background: rgba(255,255,255,0.06); border-radius: 3px; overflow: hidden; width: 120px;
    }
    .progress-fill { height: 100%; border-radius: 3px; transition: width 0.3s; }
    .progress-ok { background: var(--tf-green); }
    .progress-warn { background: var(--tf-gold); }
    .progress-over { background: var(--tf-red); }

    .profit-positive { color: var(--tf-green); font-weight: 700; }
    .profit-negative { color: var(--tf-red); font-weight: 700; }

    .empty-state { text-align: center; padding: 60px 20px; color: var(--tf-muted); }
    .empty-state h3 { color: var(--tf-text); margin-bottom: 8px; }

/* ── Responsive ── */
@media (max-width: 768px) {
    .page-header h1 { font-size: 22px; }
    .toolbar { flex-direction: column; align-items: stretch; }
    .toolbar input[type="text"] { width: 100%; }
    .stat-row { grid-template-columns: 1fr 1fr; gap: 10px; }
    .pf-table { display: block; overflow-x: auto; -webkit-overflow-scrolling: touch; }
}
@media (max-width: 480px) {
    .stat-row { grid-template-columns: 1fr; }
    .toolbar { gap: 8px; }
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
            <div class="sub">In progress</div>
        </div>
        <div class="stat-card stat-gold">
            <div class="label">Total Budget</div>
            <div class="value" id="stat-budget">$0</div>
            <div class="sub">All active projects</div>
        </div>
        <div class="stat-card stat-red">
            <div class="label">Total Spent</div>
            <div class="value" id="stat-spent">$0</div>
            <div class="sub">Actual costs</div>
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
                <option value="">All Status</option>
                <option value="active">Active</option>
                <option value="completed">Completed</option>
                <option value="over-budget">Over Budget</option>
            </select>
        </div>
    </div>

    <div class="table-card">
        <table class="pf-table">
            <thead>
                <tr>
                    <th>Project</th>
                    <th>Client</th>
                    <th>Budget</th>
                    <th>Actual Spend</th>
                    <th>Budget Used</th>
                    <th>Revenue</th>
                    <th>Profit/Loss</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody id="projectsBody">
                <tr><td colspan="8" class="empty-state">Loading...</td></tr>
            </tbody>
        </table>
    </div>
</div>

<script>
let allProjects = [];

function formatCurrency(val) {
    if (val == null) return '$0';
    return '$' + Number(val).toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}

function updateStats(projects) {
    const active = projects.filter(p => (p.status||'active') === 'active');
    document.getElementById('stat-active').textContent = active.length;
    document.getElementById('stat-budget').textContent = formatCurrency(
        active.reduce((s, p) => s + (Number(p.budget) || 0), 0)
    );
    document.getElementById('stat-spent').textContent = formatCurrency(
        active.reduce((s, p) => s + (Number(p.actual_spend) || 0), 0)
    );
    const withRev = projects.filter(p => Number(p.revenue) > 0);
    if (withRev.length) {
        const avgMargin = withRev.reduce((s, p) => {
            const rev = Number(p.revenue) || 0;
            const spend = Number(p.actual_spend) || 0;
            return s + (rev > 0 ? ((rev - spend) / rev) * 100 : 0);
        }, 0) / withRev.length;
        document.getElementById('stat-margin').textContent = Math.round(avgMargin) + '%';
    }
}

function renderTable(projects) {
    const tbody = document.getElementById('projectsBody');
    if (!projects.length) {
        tbody.innerHTML = '<tr><td colspan="8" class="empty-state"><h3>No projects found</h3><p>Project financial data will appear here</p></td></tr>';
        return;
    }
    tbody.innerHTML = projects.map(p => {
        const budget = Number(p.budget) || 0;
        const spent = Number(p.actual_spend) || 0;
        const revenue = Number(p.revenue) || 0;
        const profit = revenue - spent;
        const pct = budget > 0 ? Math.round((spent / budget) * 100) : 0;
        const barClass = pct > 100 ? 'progress-over' : pct > 80 ? 'progress-warn' : 'progress-ok';
        const isOver = pct > 100;
        const status = isOver ? 'over-budget' : (p.status || 'active');
        const statusLabel = { active:'Active', completed:'Completed', 'over-budget':'Over Budget' };
        const badgeClass = { active:'badge-active', completed:'badge-completed', 'over-budget':'badge-over-budget' };
        return `<tr>
        <td style="font-weight:600">${p.name || '--'}</td>
        <td style="color:var(--tf-muted)">${p.client || '--'}</td>
        <td style="font-weight:600">${formatCurrency(budget)}</td>
        <td style="font-weight:600">${formatCurrency(spent)}</td>
        <td>
            <div class="progress-bar"><div class="progress-fill ${barClass}" style="width:${Math.min(pct,100)}%"></div></div>
            <span style="font-size:11px;color:var(--tf-muted)">${pct}%</span>
        </td>
        <td style="font-weight:600;color:var(--tf-green)">${formatCurrency(revenue)}</td>
        <td><span class="${profit >= 0 ? 'profit-positive' : 'profit-negative'}">${profit >= 0 ? '+' : ''}${formatCurrency(profit)}</span></td>
        <td><span class="badge ${badgeClass[status] || 'badge-active'}">${statusLabel[status] || status}</span></td>
    </tr>`}).join('');
}

function applyFilters() {
    const q = (document.getElementById('searchInput').value || '').toLowerCase();
    const status = document.getElementById('statusFilter').value;
    let filtered = allProjects.filter(p => {
        if (q && !(p.name||'').toLowerCase().includes(q) && !(p.client||'').toLowerCase().includes(q)) return false;
        if (status === 'over-budget') {
            const budget = Number(p.budget) || 0;
            const spent = Number(p.actual_spend) || 0;
            if (budget <= 0 || spent <= budget) return false;
        } else if (status && (p.status||'active').toLowerCase() !== status) return false;
        return true;
    });
    renderTable(filtered);
}

async function loadProjects() {
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
