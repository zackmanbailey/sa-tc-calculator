"""
TitanForge v4 — Coil Work Station
====================================
Active coil on machine, remaining footage, job assignment, coil swap, utilization.
"""

WORKSTATION_COIL_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a;
        --tf-card: #1e293b;
        --tf-text: #e2e8f0;
        --tf-muted: #94a3b8;
        --tf-gold: #d4a843;
        --tf-blue: #3b82f6;
    }
    .ws-container {
        max-width: 1400px; margin: 0 auto; padding: 24px 32px;
        font-family: 'Inter', system-ui, -apple-system, sans-serif; color: var(--tf-text);
    }
    .page-header { margin-bottom: 32px; }
    .page-header h1 { font-size: 28px; font-weight: 800; margin: 0 0 6px 0; }
    .page-header p { font-size: 14px; color: var(--tf-muted); margin: 0; }
    .toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
    .toolbar select { background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px; }
    .btn-gold { background: var(--tf-gold); color: #0f172a; border: none; border-radius: 8px; padding: 10px 20px; font-weight: 700; font-size: 14px; cursor: pointer; }
    .btn-gold:hover { opacity: 0.9; }
    .btn-blue { background: var(--tf-blue); color: #fff; border: none; border-radius: 8px; padding: 10px 20px; font-weight: 700; font-size: 14px; cursor: pointer; }
    .btn-outline { background: transparent; color: var(--tf-muted); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 10px 20px; font-weight: 600; font-size: 14px; cursor: pointer; }
    .btn-outline:hover { border-color: var(--tf-gold); color: var(--tf-gold); }
    .coil-hero {
        background: var(--tf-card); border-radius: 12px; border: 1px solid rgba(255,255,255,0.06);
        padding: 28px; margin-bottom: 24px;
    }
    .coil-hero-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 24px; }
    @media (max-width: 900px) { .coil-hero-grid { grid-template-columns: 1fr; } }
    .coil-info h2 { font-size: 22px; font-weight: 800; margin: 0 0 4px 0; }
    .coil-info .coil-id { font-size: 14px; color: var(--tf-gold); margin-bottom: 16px; }
    .coil-detail { font-size: 14px; margin-bottom: 8px; }
    .coil-detail span { color: var(--tf-muted); }
    .gauge-container { text-align: center; }
    .gauge-ring {
        width: 140px; height: 140px; border-radius: 50%; margin: 0 auto 12px;
        background: conic-gradient(var(--tf-blue) 0deg, var(--tf-blue) var(--pct-deg), rgba(255,255,255,0.08) var(--pct-deg));
        display: flex; align-items: center; justify-content: center;
    }
    .gauge-inner { width: 110px; height: 110px; border-radius: 50%; background: var(--tf-card); display: flex; flex-direction: column; align-items: center; justify-content: center; }
    .gauge-pct { font-size: 28px; font-weight: 800; }
    .gauge-label { font-size: 12px; color: var(--tf-muted); }
    .footage-info { text-align: center; }
    .footage-big { font-size: 36px; font-weight: 800; color: var(--tf-gold); }
    .footage-label { font-size: 13px; color: var(--tf-muted); margin-top: 4px; }
    .footage-sub { font-size: 14px; color: var(--tf-muted); margin-top: 12px; }
    .stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
    @media (max-width: 900px) { .stats-row { grid-template-columns: 1fr 1fr; } }
    .stat-card { background: var(--tf-card); border-radius: 10px; padding: 18px; border: 1px solid rgba(255,255,255,0.06); }
    .stat-card .stat-label { font-size: 12px; color: var(--tf-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
    .stat-card .stat-value { font-size: 24px; font-weight: 800; }
    .section-title { font-size: 16px; font-weight: 700; margin: 0 0 16px 0; }
    .data-card { background: var(--tf-card); border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); overflow: hidden; }
    .data-table { width: 100%; border-collapse: collapse; font-size: 14px; }
    .data-table thead th {
        background: #1a2744; padding: 12px 14px; text-align: left; font-weight: 700;
        font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--tf-muted);
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .data-table tbody td { padding: 10px 14px; border-bottom: 1px solid rgba(255,255,255,0.04); }
    .data-table tbody tr { transition: background 0.15s; }
    .data-table tbody tr:hover { background: rgba(255,255,255,0.04); }
    .badge { display: inline-block; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; }
    .badge-active { background: rgba(34,197,94,0.2); color: #4ade80; }
    .badge-low { background: rgba(239,68,68,0.2); color: #f87171; }
    .badge-standby { background: rgba(148,163,184,0.2); color: #94a3b8; }
    .empty-state { text-align: center; padding: 40px 20px; color: var(--tf-muted); }
    .empty-state h3 { font-size: 18px; margin-bottom: 8px; color: var(--tf-text); }
    .loading { text-align: center; padding: 40px; color: var(--tf-muted); }
    .modal-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 1000; justify-content: center; align-items: center; }
    .modal-overlay.active { display: flex; }
    .modal { background: var(--tf-card); border-radius: 12px; padding: 28px; width: 520px; max-width: 90vw; border: 1px solid rgba(255,255,255,0.1); }
    .modal h2 { font-size: 20px; margin: 0 0 20px 0; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 24px; }
    .form-group { margin-bottom: 16px; }
    .form-group label { display: block; font-size: 13px; font-weight: 600; color: var(--tf-muted); margin-bottom: 6px; }
    .form-group input, .form-group select {
        width: 100%; background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px; box-sizing: border-box;
    }
</style>

<div class="ws-container">
    <div class="page-header">
        <h1>Coil Work Station</h1>
        <p>Active coil monitoring, remaining footage, job assignment, and swap workflow</p>
    </div>
    <div class="toolbar">
        <select id="machineSelect" onchange="loadCoilData()">
            <option value="machine-1">Machine 1 - Roll Former</option>
            <option value="machine-2">Machine 2 - Panel Line</option>
            <option value="machine-3">Machine 3 - Trim Line</option>
        </select>
        <div style="display:flex;gap:10px;">
            <button class="btn-outline" onclick="openModal('swapModal')">Swap Coil</button>
            <button class="btn-gold" onclick="openModal('assignModal')">Assign Job</button>
        </div>
    </div>

    <div class="coil-hero" id="coilHero">
        <div class="coil-hero-grid">
            <div class="coil-info">
                <h2 id="coilTag">--</h2>
                <div class="coil-id" id="coilIdLabel">No coil loaded</div>
                <div class="coil-detail"><span>Material: </span><span id="coilMaterial">--</span></div>
                <div class="coil-detail"><span>Gauge: </span><span id="coilGauge">--</span></div>
                <div class="coil-detail"><span>Width: </span><span id="coilWidth">--</span></div>
                <div class="coil-detail"><span>Color: </span><span id="coilColor">--</span></div>
                <div class="coil-detail"><span>Heat #: </span><span id="coilHeat">--</span></div>
            </div>
            <div class="gauge-container">
                <div class="gauge-ring" id="gaugeRing" style="--pct-deg:0deg;">
                    <div class="gauge-inner">
                        <div class="gauge-pct" id="gaugePct">0%</div>
                        <div class="gauge-label">Remaining</div>
                    </div>
                </div>
                <div style="font-size:13px;color:var(--tf-muted);margin-top:8px;">Utilization</div>
            </div>
            <div class="footage-info">
                <div class="footage-big" id="footageRemain">0</div>
                <div class="footage-label">Feet Remaining</div>
                <div class="footage-sub">Original: <span id="footageOriginal">0</span> ft</div>
                <div class="footage-sub">Used: <span id="footageUsed">0</span> ft</div>
                <div class="footage-sub" style="margin-top:8px;">Current Job: <strong id="currentJob">--</strong></div>
            </div>
        </div>
    </div>

    <div class="stats-row">
        <div class="stat-card"><div class="stat-label">Today's Output</div><div class="stat-value" id="statOutput" style="color:var(--tf-blue);">--</div></div>
        <div class="stat-card"><div class="stat-label">Coil Swaps Today</div><div class="stat-value" id="statSwaps" style="color:var(--tf-gold);">--</div></div>
        <div class="stat-card"><div class="stat-label">Waste %</div><div class="stat-value" id="statWaste" style="color:#f87171;">--</div></div>
        <div class="stat-card"><div class="stat-label">Machine Status</div><div class="stat-value" id="statStatus" style="color:#4ade80;">--</div></div>
    </div>

    <h3 class="section-title">Recent Coil History</h3>
    <div class="data-card">
        <div id="historyWrap" class="loading">Loading history...</div>
    </div>
</div>

<div class="modal-overlay" id="swapModal">
    <div class="modal">
        <h2>Swap Coil</h2>
        <div class="form-group"><label>New Coil Tag</label><input type="text" id="swapCoilTag" placeholder="Scan or enter coil tag"></div>
        <div class="form-group"><label>Reason for Swap</label><select id="swapReason"><option value="empty">Coil Empty</option><option value="job_change">Job Change</option><option value="defect">Material Defect</option><option value="color_change">Color Change</option></select></div>
        <div class="form-group"><label>Remaining on Current (ft)</label><input type="number" id="swapRemaining" placeholder="0"></div>
        <div class="modal-actions">
            <button class="btn-outline" onclick="closeModal('swapModal')">Cancel</button>
            <button class="btn-gold" onclick="performSwap()">Swap Coil</button>
        </div>
    </div>
</div>

<div class="modal-overlay" id="assignModal">
    <div class="modal">
        <h2>Assign Job</h2>
        <div class="form-group"><label>Job Code</label><input type="text" id="assignJob" placeholder="e.g. 2026-0015"></div>
        <div class="form-group"><label>Run Length (ft)</label><input type="number" id="assignLength" placeholder="Total footage needed"></div>
        <div class="form-group"><label>Priority</label><select id="assignPriority"><option value="normal">Normal</option><option value="rush">Rush</option><option value="hold">Hold</option></select></div>
        <div class="modal-actions">
            <button class="btn-outline" onclick="closeModal('assignModal')">Cancel</button>
            <button class="btn-gold" onclick="assignJob()">Assign</button>
        </div>
    </div>
</div>

<script>
function openModal(id) { document.getElementById(id).classList.add('active'); }
function closeModal(id) { document.getElementById(id).classList.remove('active'); }
document.querySelectorAll('.modal-overlay').forEach(m => m.addEventListener('click', function(e) { if (e.target === this) closeModal(this.id); }));

function updateCoilDisplay(data) {
    document.getElementById('coilTag').textContent = data.coil_tag || '--';
    document.getElementById('coilIdLabel').textContent = data.coil_id || 'No coil loaded';
    document.getElementById('coilMaterial').textContent = data.material || '--';
    document.getElementById('coilGauge').textContent = data.gauge || '--';
    document.getElementById('coilWidth').textContent = data.width || '--';
    document.getElementById('coilColor').textContent = data.color || '--';
    document.getElementById('coilHeat').textContent = data.heat_number || '--';
    const remain = data.remaining_feet || 0;
    const original = data.original_feet || 1;
    const used = original - remain;
    const pct = Math.round((remain / original) * 100);
    document.getElementById('footageRemain').textContent = remain.toLocaleString();
    document.getElementById('footageOriginal').textContent = original.toLocaleString();
    document.getElementById('footageUsed').textContent = used.toLocaleString();
    document.getElementById('gaugePct').textContent = pct + '%';
    document.getElementById('gaugeRing').style.setProperty('--pct-deg', (pct * 3.6) + 'deg');
    document.getElementById('currentJob').textContent = data.current_job || '--';
    document.getElementById('statOutput').textContent = (data.today_output || 0) + ' ft';
    document.getElementById('statSwaps').textContent = data.swaps_today || 0;
    document.getElementById('statWaste').textContent = (data.waste_pct || 0) + '%';
    document.getElementById('statStatus').textContent = data.machine_status || 'Idle';
}

function renderHistory(history) {
    const wrap = document.getElementById('historyWrap');
    if (!history || !history.length) {
        wrap.innerHTML = '<div class="empty-state"><h3>No coil history</h3><p>Coil swaps and usage will appear here.</p></div>';
        return;
    }
    let html = '<table class="data-table"><thead><tr><th>Date</th><th>Coil Tag</th><th>Material</th><th>Footage Used</th><th>Job</th><th>Reason</th></tr></thead><tbody>';
    history.forEach(h => {
        html += '<tr><td>' + (h.date||'--') + '</td><td style="color:var(--tf-gold);font-weight:600;">' + (h.coil_tag||'--') + '</td>' +
            '<td>' + (h.material||'--') + '</td><td>' + (h.footage_used||0) + ' ft</td>' +
            '<td>' + (h.job||'--') + '</td><td>' + (h.reason||'--') + '</td></tr>';
    });
    html += '</tbody></table>';
    wrap.innerHTML = html;
}

async function loadCoilData() {
    const machine = document.getElementById('machineSelect').value;
    try {
        const resp = await fetch('/api/workstation/coil?machine=' + machine);
        const data = await resp.json();
        updateCoilDisplay(data);
        renderHistory(data.history || []);
    } catch(e) {
        updateCoilDisplay({});
        renderHistory([]);
    }
}

async function performSwap() {
    const payload = {
        machine: document.getElementById('machineSelect').value,
        new_coil_tag: document.getElementById('swapCoilTag').value,
        reason: document.getElementById('swapReason').value,
        remaining: parseFloat(document.getElementById('swapRemaining').value) || 0
    };
    if (!payload.new_coil_tag) { alert('Enter new coil tag'); return; }
    try {
        await fetch('/api/workstation/coil/swap', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
        closeModal('swapModal');
        loadCoilData();
    } catch(e) { alert('Error: ' + e.message); }
}

async function assignJob() {
    const payload = {
        machine: document.getElementById('machineSelect').value,
        job_code: document.getElementById('assignJob').value,
        run_length: parseFloat(document.getElementById('assignLength').value) || 0,
        priority: document.getElementById('assignPriority').value
    };
    if (!payload.job_code) { alert('Enter job code'); return; }
    try {
        await fetch('/api/workstation/coil/assign', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
        closeModal('assignModal');
        loadCoilData();
    } catch(e) { alert('Error: ' + e.message); }
}

loadCoilData();
</script>
"""
