"""
TitanForge v4 — QC Dashboard
===============================
Inspection summary, pass/fail rates, open NCRs, hold points, inspector workload.
"""

QC_MAIN_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a;
        --tf-card: #1e293b;
        --tf-text: #e2e8f0;
        --tf-muted: #94a3b8;
        --tf-gold: #d4a843;
        --tf-blue: #3b82f6;
    }
    .qc-container {
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
    .stats-row { display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; margin-bottom: 24px; }
    @media (max-width: 1000px) { .stats-row { grid-template-columns: repeat(3, 1fr); } }
    .stat-card { background: var(--tf-card); border-radius: 10px; padding: 18px; border: 1px solid rgba(255,255,255,0.06); cursor: pointer; transition: border-color 0.2s; }
    .stat-card:hover { border-color: var(--tf-blue); }
    .stat-card .stat-label { font-size: 12px; color: var(--tf-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
    .stat-card .stat-value { font-size: 24px; font-weight: 800; }
    .two-col { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }
    @media (max-width: 900px) { .two-col { grid-template-columns: 1fr; } }
    .section-title { font-size: 16px; font-weight: 700; margin: 0 0 16px 0; }
    .data-card { background: var(--tf-card); border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); overflow: hidden; }
    .data-table { width: 100%; border-collapse: collapse; font-size: 14px; }
    .data-table thead th {
        background: #1a2744; padding: 12px 14px; text-align: left; font-weight: 700;
        font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--tf-muted);
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .data-table tbody td { padding: 10px 14px; border-bottom: 1px solid rgba(255,255,255,0.04); }
    .data-table tbody tr { transition: background 0.15s; cursor: pointer; }
    .data-table tbody tr:hover { background: rgba(255,255,255,0.04); }
    .badge { display: inline-block; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; }
    .badge-pass { background: rgba(34,197,94,0.2); color: #4ade80; }
    .badge-fail { background: rgba(239,68,68,0.2); color: #f87171; }
    .badge-hold { background: rgba(212,168,67,0.2); color: var(--tf-gold); }
    .badge-pending { background: rgba(59,130,246,0.2); color: #60a5fa; }
    .inspector-card { background: var(--tf-bg); border-radius: 8px; padding: 14px; margin-bottom: 10px; }
    .inspector-name { font-size: 14px; font-weight: 600; margin-bottom: 6px; }
    .inspector-stats { display: flex; gap: 16px; font-size: 12px; color: var(--tf-muted); }
    .workload-bar { height: 4px; background: rgba(255,255,255,0.08); border-radius: 2px; margin-top: 8px; }
    .workload-fill { height: 100%; border-radius: 2px; background: var(--tf-blue); }
    .rate-ring { width: 80px; height: 80px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 800; margin: 0 auto 8px; }
    .empty-state { text-align: center; padding: 60px 20px; color: var(--tf-muted); }
    .empty-state h3 { font-size: 18px; margin-bottom: 8px; color: var(--tf-text); }
    .loading { text-align: center; padding: 40px; color: var(--tf-muted); }
    .modal-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 1000; justify-content: center; align-items: center; }
    .modal-overlay.active { display: flex; }
    .modal { background: var(--tf-card); border-radius: 12px; padding: 28px; width: 560px; max-width: 90vw; border: 1px solid rgba(255,255,255,0.1); max-height: 80vh; overflow-y: auto; }
    .modal h2 { font-size: 20px; margin: 0 0 20px 0; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 24px; }
    .form-group { margin-bottom: 16px; }
    .form-group label { display: block; font-size: 13px; font-weight: 600; color: var(--tf-muted); margin-bottom: 6px; }
    .form-group input, .form-group select, .form-group textarea {
        width: 100%; background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px; font-family: inherit; box-sizing: border-box;
    }
</style>

<div class="qc-container">
    <div class="page-header">
        <h1>Quality Control</h1>
        <p>Inspection dashboard, pass/fail metrics, NCRs, and inspector workload</p>
    </div>
    <div class="stats-row">
        <div class="stat-card" onclick="window.location.href='#inspections'"><div class="stat-label">Total Inspections</div><div class="stat-value" id="statTotal" style="color:var(--tf-text);">--</div></div>
        <div class="stat-card" onclick="filterByResult('pass')"><div class="stat-label">Pass Rate</div><div class="stat-value" id="statPass" style="color:#4ade80;">--</div></div>
        <div class="stat-card" onclick="filterByResult('fail')"><div class="stat-label">Failures</div><div class="stat-value" id="statFail" style="color:#f87171;">--</div></div>
        <div class="stat-card" onclick="window.location.href='/qc/ncr'"><div class="stat-label">Open NCRs</div><div class="stat-value" id="statNCR" style="color:var(--tf-gold);">--</div></div>
        <div class="stat-card"><div class="stat-label">Hold Points</div><div class="stat-value" id="statHold" style="color:var(--tf-blue);">--</div></div>
    </div>
    <div class="toolbar">
        <div style="display:flex;gap:10px;align-items:center;">
            <input type="text" id="qcSearch" placeholder="Search inspections..." oninput="filterInspections()">
            <select id="filterResult" onchange="filterInspections()">
                <option value="">All Results</option>
                <option value="pass">Pass</option>
                <option value="fail">Fail</option>
                <option value="hold">Hold</option>
                <option value="pending">Pending</option>
            </select>
        </div>
        <div style="display:flex;gap:10px;">
            <a href="/qc/ncr" class="btn-outline">NCR Manager</a>
            <button class="btn-gold" onclick="openModal('inspModal')">+ New Inspection</button>
        </div>
    </div>
    <div class="two-col">
        <div>
            <div class="data-card" id="inspections">
                <div id="inspTableWrap" class="loading">Loading inspections...</div>
            </div>
        </div>
        <div>
            <h3 class="section-title">Inspector Workload</h3>
            <div id="inspectorList"></div>
        </div>
    </div>
</div>

<div class="modal-overlay" id="inspModal">
    <div class="modal">
        <h2>New Inspection</h2>
        <div class="form-group"><label>Project / Job</label><input type="text" id="inspProject" placeholder="Job code"></div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div class="form-group"><label>Type</label><select id="inspType"><option value="visual">Visual</option><option value="dimensional">Dimensional</option><option value="weld">Weld</option><option value="coating">Coating</option><option value="final">Final</option></select></div>
            <div class="form-group"><label>Inspector</label><input type="text" id="inspInspector" placeholder="Name"></div>
        </div>
        <div class="form-group"><label>Component</label><input type="text" id="inspComponent" placeholder="e.g. Rafter R1"></div>
        <div class="form-group"><label>Notes</label><textarea id="inspNotes" placeholder="Inspection notes..." style="min-height:60px;resize:vertical;"></textarea></div>
        <div class="form-group"><label>Result</label><select id="inspResult"><option value="pending">Pending</option><option value="pass">Pass</option><option value="fail">Fail</option><option value="hold">Hold</option></select></div>
        <div class="modal-actions">
            <button class="btn-outline" onclick="closeModal('inspModal')">Cancel</button>
            <button class="btn-gold" onclick="saveInspection()">Save</button>
        </div>
    </div>
</div>

<script>
let allInspections = [];

function openModal(id) { document.getElementById(id).classList.add('active'); }
function closeModal(id) { document.getElementById(id).classList.remove('active'); }
document.querySelectorAll('.modal-overlay').forEach(m => m.addEventListener('click', function(e) { if (e.target === this) closeModal(this.id); }));

function filterByResult(r) { document.getElementById('filterResult').value = r; filterInspections(); }

function renderTable(items) {
    const wrap = document.getElementById('inspTableWrap');
    if (!items.length) {
        wrap.innerHTML = '<div class="empty-state"><h3>No inspections found</h3><p>Create an inspection to get started.</p></div>';
        return;
    }
    let html = '<table class="data-table"><thead><tr><th>Date</th><th>Project</th><th>Type</th><th>Component</th><th>Inspector</th><th>Result</th></tr></thead><tbody>';
    items.forEach(i => {
        const cls = i.result === 'pass' ? 'badge-pass' : (i.result === 'fail' ? 'badge-fail' : (i.result === 'hold' ? 'badge-hold' : 'badge-pending'));
        html += '<tr><td>' + (i.date || '--') + '</td><td>' + (i.project || '--') + '</td>' +
            '<td>' + (i.type || '--') + '</td><td>' + (i.component || '--') + '</td>' +
            '<td>' + (i.inspector || '--') + '</td>' +
            '<td><span class="badge ' + cls + '">' + (i.result || 'pending') + '</span></td></tr>';
    });
    html += '</tbody></table>';
    wrap.innerHTML = html;
}

function renderInspectors(inspections) {
    const byInsp = {};
    inspections.forEach(i => {
        const name = i.inspector || 'Unassigned';
        if (!byInsp[name]) byInsp[name] = { total: 0, pass: 0, fail: 0 };
        byInsp[name].total++;
        if (i.result === 'pass') byInsp[name].pass++;
        if (i.result === 'fail') byInsp[name].fail++;
    });
    const el = document.getElementById('inspectorList');
    const names = Object.keys(byInsp);
    if (!names.length) { el.innerHTML = '<div style="color:var(--tf-muted);font-size:13px;padding:20px;text-align:center;">No inspector data</div>'; return; }
    const maxTotal = Math.max(...names.map(n => byInsp[n].total));
    el.innerHTML = names.map(n => {
        const d = byInsp[n];
        const pct = maxTotal ? Math.round(d.total / maxTotal * 100) : 0;
        return '<div class="inspector-card"><div class="inspector-name">' + n + '</div>' +
            '<div class="inspector-stats"><span>' + d.total + ' inspections</span><span style="color:#4ade80;">' + d.pass + ' pass</span><span style="color:#f87171;">' + d.fail + ' fail</span></div>' +
            '<div class="workload-bar"><div class="workload-fill" style="width:' + pct + '%;"></div></div></div>';
    }).join('');
}

function updateStats(items) {
    document.getElementById('statTotal').textContent = items.length;
    const passed = items.filter(i => i.result === 'pass').length;
    const failed = items.filter(i => i.result === 'fail').length;
    const rate = items.length ? Math.round(passed / items.length * 100) : 0;
    document.getElementById('statPass').textContent = rate + '%';
    document.getElementById('statFail').textContent = failed;
    document.getElementById('statHold').textContent = items.filter(i => i.result === 'hold').length;
}

function filterInspections() {
    const search = document.getElementById('qcSearch').value.toLowerCase();
    const result = document.getElementById('filterResult').value;
    const filtered = allInspections.filter(i => {
        if (search && !(i.project||'').toLowerCase().includes(search) && !(i.component||'').toLowerCase().includes(search) && !(i.inspector||'').toLowerCase().includes(search)) return false;
        if (result && i.result !== result) return false;
        return true;
    });
    renderTable(filtered);
}

async function saveInspection() {
    const payload = {
        project: document.getElementById('inspProject').value,
        type: document.getElementById('inspType').value,
        inspector: document.getElementById('inspInspector').value,
        component: document.getElementById('inspComponent').value,
        notes: document.getElementById('inspNotes').value,
        result: document.getElementById('inspResult').value,
        date: new Date().toISOString().slice(0,10)
    };
    if (!payload.project) { alert('Project is required'); return; }
    try {
        await fetch('/api/qc/inspections', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
        closeModal('inspModal');
        loadQC();
    } catch(e) { alert('Error: ' + e.message); }
}

async function loadQC() {
    try {
        const resp = await fetch('/api/qc');
        const data = await resp.json();
        allInspections = Array.isArray(data) ? data : (data.inspections || []);
        document.getElementById('statNCR').textContent = data.open_ncrs || 0;
        updateStats(allInspections);
        renderTable(allInspections);
        renderInspectors(allInspections);
    } catch(e) { renderTable([]); renderInspectors([]); }
}

loadQC();
</script>
"""
