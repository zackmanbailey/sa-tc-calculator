"""
TitanForge v4 — Cut List
===========================
Pending cuts by job, material, length, quantity, priority, waste tracking.
"""

WORKSTATION_CUTS_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a;
        --tf-card: #1e293b;
        --tf-text: #e2e8f0;
        --tf-muted: #94a3b8;
        --tf-gold: #d4a843;
        --tf-blue: #3b82f6;
    }
    .cuts-container {
        max-width: 1400px; margin: 0 auto; padding: 24px 32px;
        font-family: 'Inter', 'Segoe UI', sans-serif; color: var(--tf-text);
    }
    .page-header { margin-bottom: 32px; }
    .page-header h1 { font-size: 28px; font-weight: 800; margin: 0 0 6px 0; }
    .page-header p { font-size: 14px; color: var(--tf-muted); margin: 0; }
    .toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
    .toolbar input[type="text"] { background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px 16px; color: var(--tf-text); font-size: 14px; width: 260px; }
    .toolbar input::placeholder { color: var(--tf-muted); }
    .toolbar select { background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px; }
    .btn-gold { background: var(--tf-gold); color: #0f172a; border: none; border-radius: 8px; padding: 10px 20px; font-weight: 700; font-size: 14px; cursor: pointer; }
    .btn-gold:hover { opacity: 0.9; }
    .btn-outline { background: transparent; color: var(--tf-muted); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 10px 20px; font-weight: 600; font-size: 14px; cursor: pointer; }
    .btn-outline:hover { border-color: var(--tf-gold); color: var(--tf-gold); }
    .btn-sm { padding: 6px 14px; font-size: 12px; border-radius: 6px; }
    .btn-green { background: #22c55e; color: #fff; border: none; border-radius: 6px; padding: 6px 14px; font-size: 12px; font-weight: 600; cursor: pointer; }
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
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .data-table tbody td { padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.04); }
    .data-table tbody tr { transition: background 0.15s; }
    .data-table tbody tr:hover { background: rgba(255,255,255,0.04); }
    .data-table tbody tr.cut-done { opacity: 0.5; }
    .badge { display: inline-block; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; }
    .badge-pending { background: rgba(212,168,67,0.2); color: var(--tf-gold); }
    .badge-cut { background: rgba(34,197,94,0.2); color: #4ade80; }
    .badge-rush { background: rgba(239,68,68,0.2); color: #f87171; }
    .priority-rush { color: #f87171; font-weight: 700; }
    .priority-normal { color: var(--tf-text); }
    .priority-low { color: var(--tf-muted); }
    .empty-state { text-align: center; padding: 60px 20px; color: var(--tf-muted); }
    .empty-state h3 { font-size: 18px; margin-bottom: 8px; color: var(--tf-text); }
    .loading { text-align: center; padding: 40px; color: var(--tf-muted); }
    .waste-bar { display: flex; height: 8px; border-radius: 4px; overflow: hidden; margin-top: 4px; }
    .waste-bar .used { background: var(--tf-blue); }
    .waste-bar .waste { background: #ef4444; }
    .waste-bar .remaining { background: rgba(255,255,255,0.08); }
</style>

<div class="cuts-container">
    <div class="page-header">
        <h1>Cut List</h1>
        <p>Pending cuts by job, material type, length, quantity, and priority order</p>
    </div>
    <div class="stats-row">
        <div class="stat-card"><div class="stat-label">Pending Cuts</div><div class="stat-value" id="statPending" style="color:var(--tf-gold);">--</div></div>
        <div class="stat-card"><div class="stat-label">Completed Today</div><div class="stat-value" id="statDone" style="color:#4ade80;">--</div></div>
        <div class="stat-card"><div class="stat-label">Total Length (ft)</div><div class="stat-value" id="statLength" style="color:var(--tf-blue);">--</div></div>
        <div class="stat-card"><div class="stat-label">Waste Rate</div><div class="stat-value" id="statWaste" style="color:#f87171;">--</div></div>
    </div>
    <div class="toolbar">
        <div style="display:flex;gap:10px;align-items:center;">
            <input type="text" id="cutSearch" placeholder="Search cuts..." oninput="filterCuts()">
            <select id="filterJob" onchange="filterCuts()"><option value="">All Jobs</option></select>
            <select id="filterMaterial" onchange="filterCuts()">
                <option value="">All Materials</option>
                <option value="steel">Steel</option>
                <option value="aluminum">Aluminum</option>
                <option value="trim">Trim</option>
            </select>
            <select id="filterCutStatus" onchange="filterCuts()">
                <option value="">All Status</option>
                <option value="pending">Pending</option>
                <option value="cut">Cut</option>
            </select>
        </div>
        <div style="display:flex;gap:10px;">
            <button class="btn-outline" onclick="exportCuts()">Export</button>
            <button class="btn-gold" onclick="markAllCut()">Mark Selected Cut</button>
        </div>
    </div>
    <div class="data-card">
        <div id="cutTableWrap" class="loading">Loading cut list...</div>
    </div>
</div>

<script>
let allCuts = [];

function renderTable(cuts) {
    const wrap = document.getElementById('cutTableWrap');
    if (!cuts.length) {
        wrap.innerHTML = '<div class="empty-state"><h3>No cuts in queue</h3><p>Cut list items will appear here from work orders.</p></div>';
        return;
    }
    let html = '<table class="data-table"><thead><tr><th style="width:30px;"><input type="checkbox" onchange="toggleAll(this)"></th><th>Priority</th><th>Job</th><th>Component</th><th>Material</th><th>Length</th><th>Qty</th><th>Status</th><th>Action</th></tr></thead><tbody>';
    cuts.forEach((c, i) => {
        const prCls = c.priority === 'rush' ? 'priority-rush' : (c.priority === 'low' ? 'priority-low' : 'priority-normal');
        const stCls = c.status === 'cut' ? 'badge-cut' : (c.priority === 'rush' ? 'badge-rush' : 'badge-pending');
        const rowCls = c.status === 'cut' ? 'cut-done' : '';
        html += '<tr class="' + rowCls + '"><td><input type="checkbox" class="cut-check" data-idx="' + i + '"></td>' +
            '<td><span class="' + prCls + '">' + (c.priority || 'normal').toUpperCase() + '</span></td>' +
            '<td style="color:var(--tf-blue);font-weight:600;">' + (c.job_code || '--') + '</td>' +
            '<td>' + (c.component || '--') + '</td>' +
            '<td>' + (c.material || '--') + '</td>' +
            '<td>' + (c.length || 0) + ' ft</td>' +
            '<td>' + (c.quantity || 0) + '</td>' +
            '<td><span class="badge ' + stCls + '">' + (c.status || 'pending') + '</span></td>' +
            '<td>' + (c.status !== 'cut' ? '<button class="btn-green" onclick="markCut(' + i + ',event)">Cut</button>' : '<span style="color:var(--tf-muted);">Done</span>') + '</td></tr>';
    });
    html += '</tbody></table>';
    wrap.innerHTML = html;
}

function updateStats(cuts) {
    const pending = cuts.filter(c => c.status !== 'cut');
    const done = cuts.filter(c => c.status === 'cut');
    document.getElementById('statPending').textContent = pending.length;
    document.getElementById('statDone').textContent = done.length;
    const totalLen = pending.reduce((s, c) => s + (c.length || 0) * (c.quantity || 1), 0);
    document.getElementById('statLength').textContent = totalLen.toLocaleString();
    const totalCut = done.reduce((s, c) => s + (c.length || 0) * (c.quantity || 1), 0);
    const waste = done.reduce((s, c) => s + (c.waste || 0), 0);
    const rate = totalCut ? Math.round(waste / (totalCut + waste) * 100) : 0;
    document.getElementById('statWaste').textContent = rate + '%';
}

function filterCuts() {
    const search = document.getElementById('cutSearch').value.toLowerCase();
    const job = document.getElementById('filterJob').value;
    const material = document.getElementById('filterMaterial').value;
    const status = document.getElementById('filterCutStatus').value;
    const filtered = allCuts.filter(c => {
        if (search && !(c.job_code||'').toLowerCase().includes(search) && !(c.component||'').toLowerCase().includes(search)) return false;
        if (job && c.job_code !== job) return false;
        if (material && c.material !== material) return false;
        if (status && c.status !== status) return false;
        return true;
    });
    renderTable(filtered);
}

function toggleAll(el) {
    document.querySelectorAll('.cut-check').forEach(cb => cb.checked = el.checked);
}

async function markCut(idx, event) {
    if (event) event.stopPropagation();
    allCuts[idx].status = 'cut';
    updateStats(allCuts);
    filterCuts();
    try {
        await fetch('/api/workstation/cuts/mark', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ id: allCuts[idx].id }) });
    } catch(e) {}
}

function markAllCut() {
    const checks = document.querySelectorAll('.cut-check:checked');
    checks.forEach(cb => {
        const idx = parseInt(cb.dataset.idx);
        if (allCuts[idx]) allCuts[idx].status = 'cut';
    });
    updateStats(allCuts);
    filterCuts();
}

function exportCuts() {
    const rows = [['Priority','Job','Component','Material','Length','Qty','Status']];
    allCuts.forEach(c => rows.push([c.priority||'',c.job_code||'',c.component||'',c.material||'',c.length||0,c.quantity||0,c.status||'']));
    const csv = rows.map(r => r.join(',')).join('\n');
    const blob = new Blob([csv], {type:'text/csv'});
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'cut_list.csv'; a.click();
}

async function loadCuts() {
    try {
        const resp = await fetch('/api/workstation/cuts');
        const data = await resp.json();
        allCuts = Array.isArray(data) ? data : (data.cuts || []);
        const jobs = [...new Set(allCuts.map(c => c.job_code).filter(Boolean))];
        const sel = document.getElementById('filterJob');
        jobs.forEach(j => { const o = document.createElement('option'); o.value = j; o.textContent = j; sel.appendChild(o); });
        updateStats(allCuts);
        renderTable(allCuts);
    } catch(e) { renderTable([]); }
}

loadCuts();
</script>
"""
