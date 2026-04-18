"""
TitanForge v4 — Material Traceability
=======================================
Heat number lookup, mill cert chain, coil-through-install tracking, compliance.
"""

TRACEABILITY_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a;
        --tf-card: #1e293b;
        --tf-text: #e2e8f0;
        --tf-muted: #94a3b8;
        --tf-gold: #d4a843;
        --tf-blue: #3b82f6;
    }
    .trace-container {
        max-width: 1400px; margin: 0 auto; padding: 24px 32px;
        font-family: 'Inter', 'Segoe UI', sans-serif; color: var(--tf-text);
    }
    .page-header { margin-bottom: 32px; }
    .page-header h1 { font-size: 28px; font-weight: 800; margin: 0 0 6px 0; }
    .page-header p { font-size: 14px; color: var(--tf-muted); margin: 0; }
    .toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
    .toolbar input[type="text"] { background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px 16px; color: var(--tf-text); font-size: 14px; width: 300px; }
    .toolbar input::placeholder { color: var(--tf-muted); }
    .toolbar select { background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px; }
    .btn-gold { background: var(--tf-gold); color: #0f172a; border: none; border-radius: 8px; padding: 10px 20px; font-weight: 700; font-size: 14px; cursor: pointer; }
    .btn-gold:hover { opacity: 0.9; }
    .btn-blue { background: var(--tf-blue); color: #fff; border: none; border-radius: 8px; padding: 10px 20px; font-weight: 700; font-size: 14px; cursor: pointer; }
    .btn-outline { background: transparent; color: var(--tf-muted); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 10px 20px; font-weight: 600; font-size: 14px; cursor: pointer; }
    .btn-outline:hover { border-color: var(--tf-gold); color: var(--tf-gold); }
    .stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
    @media (max-width: 900px) { .stats-row { grid-template-columns: 1fr 1fr; } }
    .stat-card { background: var(--tf-card); border-radius: 10px; padding: 18px; border: 1px solid rgba(255,255,255,0.06); }
    .stat-card .stat-label { font-size: 12px; color: var(--tf-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
    .stat-card .stat-value { font-size: 24px; font-weight: 800; }
    .stat-card .stat-value.gold { color: var(--tf-gold); }
    .stat-card .stat-value.blue { color: var(--tf-blue); }
    .stat-card .stat-value.green { color: #4ade80; }
    .stat-card .stat-value.red { color: #f87171; }
    .data-card {
        background: var(--tf-card); border-radius: 12px; border: 1px solid rgba(255,255,255,0.06);
        padding: 0; overflow: hidden;
    }
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
    .badge-green { background: rgba(34,197,94,0.2); color: #4ade80; }
    .badge-yellow { background: rgba(212,168,67,0.2); color: var(--tf-gold); }
    .badge-red { background: rgba(239,68,68,0.2); color: #f87171; }
    .badge-blue { background: rgba(59,130,246,0.2); color: #60a5fa; }
    .chain-view { padding: 20px; }
    .chain-node { display: inline-flex; align-items: center; gap: 8px; background: var(--tf-bg); border-radius: 8px; padding: 10px 16px; font-size: 13px; }
    .chain-arrow { color: var(--tf-muted); font-size: 18px; margin: 0 8px; }
    .empty-state { text-align: center; padding: 60px 20px; color: var(--tf-muted); }
    .empty-state h3 { font-size: 18px; margin-bottom: 8px; color: var(--tf-text); }
    .loading { text-align: center; padding: 40px; color: var(--tf-muted); }
    .modal-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 1000; justify-content: center; align-items: center; }
    .modal-overlay.active { display: flex; }
    .modal { background: var(--tf-card); border-radius: 12px; padding: 28px; width: 600px; max-width: 90vw; border: 1px solid rgba(255,255,255,0.1); max-height: 80vh; overflow-y: auto; }
    .modal h2 { font-size: 20px; margin: 0 0 20px 0; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 24px; }
    .form-group { margin-bottom: 16px; }
    .form-group label { display: block; font-size: 13px; font-weight: 600; color: var(--tf-muted); margin-bottom: 6px; }
    .form-group input, .form-group select, .form-group textarea {
        width: 100%; background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px; font-family: inherit; box-sizing: border-box;
    }
</style>

<div class="trace-container">
    <div class="page-header">
        <h1>Material Traceability</h1>
        <p>Track materials from coil through fabrication to installation with full chain of custody</p>
    </div>
    <div class="stats-row" id="traceStats">
        <div class="stat-card"><div class="stat-label">Tracked Heats</div><div class="stat-value gold" id="statHeats">--</div></div>
        <div class="stat-card"><div class="stat-label">Active Coils</div><div class="stat-value blue" id="statCoils">--</div></div>
        <div class="stat-card"><div class="stat-label">Mill Certs on File</div><div class="stat-value green" id="statCerts">--</div></div>
        <div class="stat-card"><div class="stat-label">Pending Verification</div><div class="stat-value red" id="statPending">--</div></div>
    </div>
    <div class="toolbar">
        <div style="display:flex;gap:10px;align-items:center;">
            <input type="text" id="traceSearch" placeholder="Search heat number, coil ID, project..." oninput="filterTrace()">
            <select id="filterStatus" onchange="filterTrace()">
                <option value="">All Status</option>
                <option value="verified">Verified</option>
                <option value="pending">Pending</option>
                <option value="in_use">In Use</option>
                <option value="consumed">Consumed</option>
            </select>
        </div>
        <div style="display:flex;gap:10px;">
            <button class="btn-outline" onclick="exportTrace()">Export</button>
            <button class="btn-gold" onclick="openModal('traceModal')">+ Log Material</button>
        </div>
    </div>
    <div class="data-card">
        <div id="traceTableWrap" class="loading">Loading traceability data...</div>
    </div>
</div>

<div class="modal-overlay" id="traceModal">
    <div class="modal">
        <h2>Log Material Entry</h2>
        <div class="form-group"><label>Heat Number</label><input type="text" id="tmHeat" placeholder="e.g. H2024-1234"></div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div class="form-group"><label>Coil ID</label><input type="text" id="tmCoil" placeholder="Coil identifier"></div>
            <div class="form-group"><label>Material Grade</label><select id="tmGrade"><option value="A36">A36</option><option value="A572-50">A572-50</option><option value="A500B">A500B</option><option value="A992">A992</option></select></div>
            <div class="form-group"><label>Supplier</label><input type="text" id="tmSupplier" placeholder="Mill / supplier"></div>
            <div class="form-group"><label>Gauge / Thickness</label><input type="text" id="tmGauge" placeholder="e.g. 14ga"></div>
        </div>
        <div class="form-group"><label>Mill Cert Reference</label><input type="text" id="tmCert" placeholder="Cert document ID"></div>
        <div class="form-group"><label>Assigned Project</label><input type="text" id="tmProject" placeholder="Job code or project"></div>
        <div class="modal-actions">
            <button class="btn-outline" onclick="closeModal('traceModal')">Cancel</button>
            <button class="btn-gold" onclick="saveMaterial()">Save</button>
        </div>
    </div>
</div>

<div class="modal-overlay" id="chainModal">
    <div class="modal" style="width:700px;">
        <h2 id="chainTitle">Traceability Chain</h2>
        <div id="chainContent" class="chain-view"></div>
        <div class="modal-actions"><button class="btn-outline" onclick="closeModal('chainModal')">Close</button></div>
    </div>
</div>

<script>
let allMaterials = [];

function openModal(id) { document.getElementById(id).classList.add('active'); }
function closeModal(id) { document.getElementById(id).classList.remove('active'); }
document.querySelectorAll('.modal-overlay').forEach(m => m.addEventListener('click', function(e) { if (e.target === this) closeModal(this.id); }));

function renderTable(materials) {
    const wrap = document.getElementById('traceTableWrap');
    if (!materials.length) {
        wrap.innerHTML = '<div class="empty-state"><h3>No traceability records</h3><p>Log materials to begin tracking.</p></div>';
        return;
    }
    let html = '<table class="data-table"><thead><tr><th>Heat Number</th><th>Coil ID</th><th>Grade</th><th>Supplier</th><th>Project</th><th>Status</th><th>Mill Cert</th></tr></thead><tbody>';
    materials.forEach(m => {
        const statusCls = m.status === 'verified' ? 'badge-green' : (m.status === 'pending' ? 'badge-yellow' : (m.status === 'consumed' ? 'badge-blue' : 'badge-blue'));
        html += '<tr onclick="showChain(\'' + (m.heat_number||'') + '\')">' +
            '<td style="font-weight:600;color:var(--tf-gold);">' + (m.heat_number || '--') + '</td>' +
            '<td>' + (m.coil_id || '--') + '</td>' +
            '<td>' + (m.grade || '--') + '</td>' +
            '<td>' + (m.supplier || '--') + '</td>' +
            '<td>' + (m.project || '--') + '</td>' +
            '<td><span class="badge ' + statusCls + '">' + (m.status || 'unknown') + '</span></td>' +
            '<td>' + (m.mill_cert ? '<span style="color:var(--tf-blue);cursor:pointer;">View</span>' : '--') + '</td></tr>';
    });
    html += '</tbody></table>';
    wrap.innerHTML = html;
}

function updateStats(materials) {
    const heats = new Set(materials.map(m => m.heat_number).filter(Boolean));
    document.getElementById('statHeats').textContent = heats.size;
    document.getElementById('statCoils').textContent = materials.filter(m => m.status === 'in_use').length;
    document.getElementById('statCerts').textContent = materials.filter(m => m.mill_cert).length;
    document.getElementById('statPending').textContent = materials.filter(m => m.status === 'pending').length;
}

function filterTrace() {
    const search = document.getElementById('traceSearch').value.toLowerCase();
    const status = document.getElementById('filterStatus').value;
    const filtered = allMaterials.filter(m => {
        if (search && !(m.heat_number||'').toLowerCase().includes(search) && !(m.coil_id||'').toLowerCase().includes(search) && !(m.project||'').toLowerCase().includes(search)) return false;
        if (status && m.status !== status) return false;
        return true;
    });
    renderTable(filtered);
}

function showChain(heat) {
    document.getElementById('chainTitle').textContent = 'Chain: ' + heat;
    const steps = ['Mill Origin', 'Coil Receipt', 'QC Inspection', 'Fabrication', 'Assembly', 'Shipping'];
    document.getElementById('chainContent').innerHTML = steps.map(s =>
        '<span class="chain-node">' + s + '</span>'
    ).join('<span class="chain-arrow">&rarr;</span>');
    openModal('chainModal');
}

function exportTrace() {
    const rows = [['Heat Number','Coil ID','Grade','Supplier','Project','Status']];
    allMaterials.forEach(m => rows.push([m.heat_number||'',m.coil_id||'',m.grade||'',m.supplier||'',m.project||'',m.status||'']));
    const csv = rows.map(r => r.join(',')).join('\n');
    const blob = new Blob([csv], {type:'text/csv'});
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'traceability.csv'; a.click();
}

async function saveMaterial() {
    const payload = {
        heat_number: document.getElementById('tmHeat').value,
        coil_id: document.getElementById('tmCoil').value,
        grade: document.getElementById('tmGrade').value,
        supplier: document.getElementById('tmSupplier').value,
        gauge: document.getElementById('tmGauge').value,
        mill_cert: document.getElementById('tmCert').value,
        project: document.getElementById('tmProject').value,
        status: 'pending'
    };
    if (!payload.heat_number) { alert('Heat number is required'); return; }
    try {
        await fetch('/api/traceability', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
        closeModal('traceModal');
        loadTrace();
    } catch(e) { alert('Error: ' + e.message); }
}

async function loadTrace() {
    try {
        const resp = await fetch('/api/traceability');
        const data = await resp.json();
        allMaterials = Array.isArray(data) ? data : (data.materials || []);
        updateStats(allMaterials);
        renderTable(allMaterials);
    } catch(e) { renderTable([]); }
}

loadTrace();
</script>
"""
