"""
TitanForge v4 — Completed Work
=================================
Finished items, QC passed, ready for shipping, production stats.
"""

WORKSTATION_COMPLETED_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a;
        --tf-card: #1e293b;
        --tf-text: #e2e8f0;
        --tf-muted: #94a3b8;
        --tf-gold: #d4a843;
        --tf-blue: #3b82f6;
    }
    .comp-container {
        max-width: 1400px; margin: 0 auto; padding: 24px 32px;
        font-family: 'Inter', system-ui, -apple-system, sans-serif; color: var(--tf-text);
    }
    .page-header { margin-bottom: 32px; }
    .page-header h1 { font-size: 28px; font-weight: 800; margin: 0 0 6px 0; }
    .page-header p { font-size: 14px; color: var(--tf-muted); margin: 0; }
    .toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
    .toolbar input[type="text"], .toolbar input[type="date"] { background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px 16px; color: var(--tf-text); font-size: 14px; }
    .toolbar input::placeholder { color: var(--tf-muted); }
    .toolbar select { background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px; }
    .btn-gold { background: var(--tf-gold); color: #0f172a; border: none; border-radius: 8px; padding: 10px 20px; font-weight: 700; font-size: 14px; cursor: pointer; }
    .btn-outline { background: transparent; color: var(--tf-muted); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 10px 20px; font-weight: 600; font-size: 14px; cursor: pointer; }
    .btn-outline:hover { border-color: var(--tf-gold); color: var(--tf-gold); }
    .stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
    @media (max-width: 900px) { .stats-row { grid-template-columns: 1fr 1fr; } }
    .stat-card { background: var(--tf-card); border-radius: 10px; padding: 18px; border: 1px solid rgba(255,255,255,0.06); }
    .stat-card .stat-label { font-size: 12px; color: var(--tf-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
    .stat-card .stat-value { font-size: 24px; font-weight: 800; }
    .data-card { background: var(--tf-card); border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); overflow: hidden; }
    .data-table { width: 100%; border-collapse: collapse; font-size: 14px; }
    .data-table thead th {
        background: #1a2744; padding: 14px 16px; text-align: left; font-weight: 700;
        font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--tf-muted);
        border-bottom: 1px solid rgba(255,255,255,0.06); cursor: pointer;
    }
    .data-table thead th:hover { color: var(--tf-text); }
    .data-table tbody td { padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.04); }
    .data-table tbody tr { transition: background 0.15s; cursor: pointer; }
    .data-table tbody tr:hover { background: rgba(255,255,255,0.04); }
    .badge { display: inline-block; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; }
    .badge-passed { background: rgba(34,197,94,0.2); color: #4ade80; }
    .badge-ready { background: rgba(59,130,246,0.2); color: #60a5fa; }
    .badge-shipped { background: rgba(148,163,184,0.2); color: #94a3b8; }
    .badge-pending { background: rgba(212,168,67,0.2); color: var(--tf-gold); }
    .empty-state { text-align: center; padding: 60px 20px; color: var(--tf-muted); }
    .empty-state h3 { font-size: 18px; margin-bottom: 8px; color: var(--tf-text); }
    .loading { text-align: center; padding: 40px; color: var(--tf-muted); }
</style>

<div class="comp-container">
    <div class="page-header">
        <h1>Completed Work</h1>
        <p>Finished items, QC-passed components, and production output tracking</p>
    </div>
    <div class="stats-row">
        <div class="stat-card"><div class="stat-label">Completed Today</div><div class="stat-value" id="statToday" style="color:#4ade80;">--</div></div>
        <div class="stat-card"><div class="stat-label">This Week</div><div class="stat-value" id="statWeek" style="color:var(--tf-blue);">--</div></div>
        <div class="stat-card"><div class="stat-label">QC Passed</div><div class="stat-value" id="statPassed" style="color:var(--tf-gold);">--</div></div>
        <div class="stat-card"><div class="stat-label">Ready to Ship</div><div class="stat-value" id="statReady" style="color:var(--tf-text);">--</div></div>
    </div>
    <div class="toolbar">
        <div style="display:flex;gap:10px;align-items:center;">
            <input type="text" id="compSearch" placeholder="Search items..." oninput="filterItems()">
            <select id="filterQC" onchange="filterItems()">
                <option value="">All QC Status</option>
                <option value="passed">QC Passed</option>
                <option value="pending">QC Pending</option>
                <option value="ready">Ready to Ship</option>
                <option value="shipped">Shipped</option>
            </select>
            <input type="date" id="filterDate" onchange="filterItems()">
        </div>
        <button class="btn-outline" onclick="exportCompleted()">Export CSV</button>
    </div>
    <div class="data-card">
        <div id="compTableWrap" class="loading">Loading completed work...</div>
    </div>
</div>

<script>
let allItems = [];
let sortCol = 'completed_date';
let sortDir = -1;

function renderTable(items) {
    const wrap = document.getElementById('compTableWrap');
    if (!items.length) {
        wrap.innerHTML = '<div class="empty-state"><h3>No completed items</h3><p>Finished items will appear here automatically.</p></div>';
        return;
    }
    let html = '<table class="data-table"><thead><tr>' +
        '<th onclick="sortBy(\'completed_date\')">Completed</th>' +
        '<th onclick="sortBy(\'job_code\')">Job Code</th>' +
        '<th onclick="sortBy(\'component\')">Component</th>' +
        '<th onclick="sortBy(\'quantity\')">Qty</th>' +
        '<th onclick="sortBy(\'operator\')">Operator</th>' +
        '<th onclick="sortBy(\'machine\')">Machine</th>' +
        '<th onclick="sortBy(\'qc_status\')">QC Status</th>' +
        '</tr></thead><tbody>';
    items.forEach(it => {
        const qcCls = it.qc_status === 'passed' ? 'badge-passed' : (it.qc_status === 'ready' ? 'badge-ready' : (it.qc_status === 'shipped' ? 'badge-shipped' : 'badge-pending'));
        html += '<tr><td>' + (it.completed_date || '--') + '</td>' +
            '<td style="color:var(--tf-blue);font-weight:600;">' + (it.job_code || '--') + '</td>' +
            '<td>' + (it.component || '--') + '</td>' +
            '<td>' + (it.quantity || 0) + '</td>' +
            '<td>' + (it.operator || '--') + '</td>' +
            '<td>' + (it.machine || '--') + '</td>' +
            '<td><span class="badge ' + qcCls + '">' + (it.qc_status || 'pending') + '</span></td></tr>';
    });
    html += '</tbody></table>';
    wrap.innerHTML = html;
}

function updateStats(items) {
    const today = new Date().toISOString().slice(0,10);
    const weekAgo = new Date(Date.now() - 7 * 86400000).toISOString().slice(0,10);
    document.getElementById('statToday').textContent = items.filter(i => (i.completed_date||'') === today).length;
    document.getElementById('statWeek').textContent = items.filter(i => (i.completed_date||'') >= weekAgo).length;
    document.getElementById('statPassed').textContent = items.filter(i => i.qc_status === 'passed').length;
    document.getElementById('statReady').textContent = items.filter(i => i.qc_status === 'ready').length;
}

function filterItems() {
    const search = document.getElementById('compSearch').value.toLowerCase();
    const qc = document.getElementById('filterQC').value;
    const date = document.getElementById('filterDate').value;
    const filtered = allItems.filter(i => {
        if (search && !(i.job_code||'').toLowerCase().includes(search) && !(i.component||'').toLowerCase().includes(search) && !(i.operator||'').toLowerCase().includes(search)) return false;
        if (qc && i.qc_status !== qc) return false;
        if (date && (i.completed_date||'') !== date) return false;
        return true;
    });
    renderTable(filtered);
}

function sortBy(col) {
    if (sortCol === col) sortDir *= -1; else { sortCol = col; sortDir = 1; }
    allItems.sort((a, b) => {
        const va = a[col] || '', vb = b[col] || '';
        if (typeof va === 'number') return (va - vb) * sortDir;
        return va.localeCompare(vb) * sortDir;
    });
    filterItems();
}

function exportCompleted() {
    const rows = [['Completed','Job Code','Component','Qty','Operator','Machine','QC Status']];
    allItems.forEach(i => rows.push([i.completed_date||'',i.job_code||'',i.component||'',i.quantity||0,i.operator||'',i.machine||'',i.qc_status||'']));
    const csv = rows.map(r => r.join(',')).join('\n');
    const blob = new Blob([csv], {type:'text/csv'});
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'completed_work.csv'; a.click();
}

async function loadCompleted() {
    try {
        const resp = await fetch('/api/workstation/completed');
        const data = await resp.json();
        allItems = Array.isArray(data) ? data : (data.items || []);
        updateStats(allItems);
        renderTable(allItems);
    } catch(e) { renderTable([]); }
}

loadCompleted();
</script>
"""
