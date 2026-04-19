"""
TitanForge v4 — AISC Compliance Dashboard
============================================
Certification status, documentation, audit readiness, QA/QC compliance, ITP tracking.
"""

AISC_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a;
        --tf-card: #1e293b;
        --tf-text: #e2e8f0;
        --tf-muted: #94a3b8;
        --tf-gold: #d4a843;
        --tf-blue: #3b82f6;
    }
    .aisc-container {
        max-width: 1400px; margin: 0 auto; padding: 24px 32px;
        font-family: 'Inter', system-ui, -apple-system, sans-serif; color: var(--tf-text);
    }
    .page-header { margin-bottom: 32px; }
    .page-header h1 { font-size: 28px; font-weight: 800; margin: 0 0 6px 0; }
    .page-header p { font-size: 14px; color: var(--tf-muted); margin: 0; }
    .toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
    .toolbar input[type="text"] { background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px 16px; color: var(--tf-text); font-size: 14px; width: 260px; }
    .toolbar input::placeholder { color: var(--tf-muted); }
    .btn-gold { background: var(--tf-gold); color: #0f172a; border: none; border-radius: 8px; padding: 10px 20px; font-weight: 700; font-size: 14px; cursor: pointer; }
    .btn-gold:hover { opacity: 0.9; }
    .btn-outline { background: transparent; color: var(--tf-muted); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 10px 20px; font-weight: 600; font-size: 14px; cursor: pointer; }
    .btn-outline:hover { border-color: var(--tf-gold); color: var(--tf-gold); }
    .stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
    @media (max-width: 900px) { .stats-row { grid-template-columns: 1fr 1fr; } }
    .stat-card { background: var(--tf-card); border-radius: 10px; padding: 18px; border: 1px solid rgba(255,255,255,0.06); }
    .stat-card .stat-label { font-size: 12px; color: var(--tf-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
    .stat-card .stat-value { font-size: 24px; font-weight: 800; }
    .section-title { font-size: 18px; font-weight: 700; margin: 28px 0 16px 0; }
    .checklist-card { background: var(--tf-card); border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); padding: 20px; margin-bottom: 20px; }
    .checklist-card h3 { font-size: 16px; font-weight: 700; margin: 0 0 16px 0; display: flex; justify-content: space-between; align-items: center; }
    .checklist-progress { font-size: 13px; color: var(--tf-muted); font-weight: 400; }
    .checklist-item { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.04); }
    .checklist-item:last-child { border-bottom: none; }
    .check-box { width: 22px; height: 22px; border-radius: 6px; border: 2px solid rgba(255,255,255,0.15); display: flex; align-items: center; justify-content: center; cursor: pointer; flex-shrink: 0; transition: all 0.2s; }
    .check-box.checked { background: var(--tf-blue); border-color: var(--tf-blue); }
    .check-box.checked::after { content: '\2713'; color: #fff; font-size: 13px; font-weight: 700; }
    .check-text { font-size: 14px; flex: 1; }
    .check-text.done { text-decoration: line-through; color: var(--tf-muted); }
    .check-due { font-size: 12px; color: var(--tf-muted); white-space: nowrap; }
    .check-due.overdue { color: #f87171; }
    .progress-bar { height: 6px; background: rgba(255,255,255,0.08); border-radius: 3px; margin-bottom: 16px; overflow: hidden; }
    .progress-fill { height: 100%; border-radius: 3px; transition: width 0.3s; }
    .progress-fill.green { background: #4ade80; }
    .progress-fill.gold { background: var(--tf-gold); }
    .progress-fill.blue { background: var(--tf-blue); }
    .itp-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 16px; }
    .itp-card { background: var(--tf-card); border-radius: 10px; border: 1px solid rgba(255,255,255,0.06); padding: 16px; cursor: pointer; transition: border-color 0.2s; }
    .itp-card:hover { border-color: var(--tf-blue); }
    .itp-card h4 { font-size: 14px; font-weight: 700; margin: 0 0 8px 0; }
    .itp-card p { font-size: 13px; color: var(--tf-muted); margin: 0 0 10px 0; }
    .itp-meta { display: flex; justify-content: space-between; font-size: 12px; color: var(--tf-muted); }
    .badge { display: inline-block; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; }
    .badge-green { background: rgba(34,197,94,0.2); color: #4ade80; }
    .badge-yellow { background: rgba(212,168,67,0.2); color: var(--tf-gold); }
    .badge-red { background: rgba(239,68,68,0.2); color: #f87171; }
    .badge-blue { background: rgba(59,130,246,0.2); color: #60a5fa; }
    .empty-state { text-align: center; padding: 60px 20px; color: var(--tf-muted); }
    .empty-state h3 { font-size: 18px; margin-bottom: 8px; color: var(--tf-text); }
    .loading { text-align: center; padding: 40px; color: var(--tf-muted); }
</style>

<div class="aisc-container">
    <div class="page-header">
        <h1>AISC Compliance</h1>
        <p>Certification status, audit readiness, QA/QC program compliance, and ITP tracking</p>
    </div>
    <div class="stats-row">
        <div class="stat-card"><div class="stat-label">Certification Status</div><div class="stat-value" id="statCert" style="color:#4ade80;">--</div></div>
        <div class="stat-card"><div class="stat-label">Audit Readiness</div><div class="stat-value" id="statReady" style="color:var(--tf-gold);">--</div></div>
        <div class="stat-card"><div class="stat-label">Open Items</div><div class="stat-value" id="statOpen" style="color:var(--tf-blue);">--</div></div>
        <div class="stat-card"><div class="stat-label">Next Audit</div><div class="stat-value" id="statNext" style="color:var(--tf-muted);font-size:16px;">--</div></div>
    </div>

    <div class="section-title">Audit Readiness Checklist</div>
    <div id="checklistArea" class="loading">Loading checklist...</div>

    <div class="section-title">Inspection & Test Plans (ITP)</div>
    <div class="toolbar" style="margin-top:0;">
        <input type="text" id="itpSearch" placeholder="Search ITPs..." oninput="filterITPs()">
        <button class="btn-gold" onclick="openNewITP()">+ New ITP</button>
    </div>
    <div class="itp-grid" id="itpGrid">
        <div class="loading">Loading ITPs...</div>
    </div>
</div>

<script>
let allChecklists = [];
let allITPs = [];

const defaultChecklists = [
    {
        name: 'Quality Manual',
        items: [
            { text: 'Quality manual current and approved', checked: true, due: '' },
            { text: 'Organizational chart updated', checked: true, due: '' },
            { text: 'Quality objectives documented', checked: false, due: '2026-05-01' },
            { text: 'Management review completed', checked: false, due: '2026-04-30' }
        ]
    },
    {
        name: 'Document Control',
        items: [
            { text: 'Controlled document register current', checked: true, due: '' },
            { text: 'Obsolete documents removed', checked: false, due: '2026-04-25' },
            { text: 'Revision history maintained', checked: true, due: '' },
            { text: 'Document approval process followed', checked: true, due: '' }
        ]
    },
    {
        name: 'Welding & Fabrication',
        items: [
            { text: 'WPS/PQR documentation current', checked: true, due: '' },
            { text: 'Welder certifications valid', checked: false, due: '2026-05-15' },
            { text: 'NDT procedures documented', checked: true, due: '' },
            { text: 'Calibration records current', checked: false, due: '2026-04-20' },
            { text: 'Material traceability maintained', checked: true, due: '' }
        ]
    }
];

function renderChecklists(lists) {
    const area = document.getElementById('checklistArea');
    let totalItems = 0, checkedItems = 0;
    lists.forEach(cl => { cl.items.forEach(it => { totalItems++; if (it.checked) checkedItems++; }); });
    const pct = totalItems ? Math.round(checkedItems / totalItems * 100) : 0;
    document.getElementById('statReady').textContent = pct + '%';
    document.getElementById('statOpen').textContent = totalItems - checkedItems;

    area.innerHTML = lists.map((cl, ci) => {
        const done = cl.items.filter(i => i.checked).length;
        const total = cl.items.length;
        const pctCl = total ? Math.round(done / total * 100) : 0;
        const barColor = pctCl === 100 ? 'green' : (pctCl >= 50 ? 'gold' : 'blue');
        return '<div class="checklist-card"><h3>' + cl.name + '<span class="checklist-progress">' + done + '/' + total + '</span></h3>' +
            '<div class="progress-bar"><div class="progress-fill ' + barColor + '" style="width:' + pctCl + '%;"></div></div>' +
            cl.items.map((it, ii) => {
                const today = new Date().toISOString().slice(0,10);
                const overdue = it.due && !it.checked && it.due < today;
                return '<div class="checklist-item">' +
                    '<div class="check-box ' + (it.checked ? 'checked' : '') + '" onclick="toggleCheck(' + ci + ',' + ii + ')"></div>' +
                    '<span class="check-text ' + (it.checked ? 'done' : '') + '">' + it.text + '</span>' +
                    (it.due ? '<span class="check-due ' + (overdue ? 'overdue' : '') + '">' + it.due + '</span>' : '') + '</div>';
            }).join('') + '</div>';
    }).join('');
}

function toggleCheck(ci, ii) {
    allChecklists[ci].items[ii].checked = !allChecklists[ci].items[ii].checked;
    renderChecklists(allChecklists);
    fetch('/api/aisc/checklist', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(allChecklists) }).catch(() => {});
}

function renderITPs(itps) {
    const grid = document.getElementById('itpGrid');
    if (!itps.length) {
        grid.innerHTML = '<div class="empty-state" style="grid-column:1/-1;"><h3>No ITPs found</h3><p>Create an Inspection & Test Plan to get started.</p></div>';
        return;
    }
    grid.innerHTML = itps.map(itp => {
        const statusCls = itp.status === 'approved' ? 'badge-green' : (itp.status === 'draft' ? 'badge-yellow' : 'badge-blue');
        return '<div class="itp-card"><h4>' + (itp.name || 'Unnamed ITP') + '</h4>' +
            '<p>' + (itp.description || 'No description') + '</p>' +
            '<div class="itp-meta"><span class="badge ' + statusCls + '">' + (itp.status || 'draft') + '</span>' +
            '<span>' + (itp.project || '') + '</span></div></div>';
    }).join('');
}

function filterITPs() {
    const search = document.getElementById('itpSearch').value.toLowerCase();
    const filtered = allITPs.filter(i => !search || (i.name||'').toLowerCase().includes(search));
    renderITPs(filtered);
}

function openNewITP() {
    const name = prompt('ITP Name:');
    if (!name) return;
    const itp = { name, status: 'draft', description: '', project: '' };
    fetch('/api/aisc/itp', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(itp) })
        .then(() => loadData()).catch(e => alert(e.message));
}

async function loadData() {
    try {
        const resp = await fetch('/api/aisc');
        const data = await resp.json();
        allChecklists = data.checklists || defaultChecklists;
        allITPs = data.itps || [];
        document.getElementById('statCert').textContent = data.cert_status || 'Active';
        document.getElementById('statNext').textContent = data.next_audit || 'TBD';
        renderChecklists(allChecklists);
        renderITPs(allITPs);
    } catch(e) {
        allChecklists = defaultChecklists;
        document.getElementById('statCert').textContent = 'Active';
        renderChecklists(allChecklists);
        renderITPs([]);
    }
}

loadData();
</script>
"""
