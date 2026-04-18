"""
TitanForge v4 — Work Log
===========================
Operator activity log, start/stop times, pieces produced, downtime, shift summary.
"""

WORKSTATION_LOG_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a;
        --tf-card: #1e293b;
        --tf-text: #e2e8f0;
        --tf-muted: #94a3b8;
        --tf-gold: #d4a843;
        --tf-blue: #3b82f6;
    }
    .log-container {
        max-width: 1400px; margin: 0 auto; padding: 24px 32px;
        font-family: 'Inter', 'Segoe UI', sans-serif; color: var(--tf-text);
    }
    .page-header { margin-bottom: 32px; }
    .page-header h1 { font-size: 28px; font-weight: 800; margin: 0 0 6px 0; }
    .page-header p { font-size: 14px; color: var(--tf-muted); margin: 0; }
    .toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
    .toolbar input[type="text"], .toolbar input[type="date"] { background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px 16px; color: var(--tf-text); font-size: 14px; }
    .toolbar input::placeholder { color: var(--tf-muted); }
    .toolbar select { background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px; }
    .btn-gold { background: var(--tf-gold); color: #0f172a; border: none; border-radius: 8px; padding: 10px 20px; font-weight: 700; font-size: 14px; cursor: pointer; }
    .btn-gold:hover { opacity: 0.9; }
    .btn-outline { background: transparent; color: var(--tf-muted); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 10px 20px; font-weight: 600; font-size: 14px; cursor: pointer; }
    .btn-outline:hover { border-color: var(--tf-gold); color: var(--tf-gold); }
    .stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
    @media (max-width: 900px) { .stats-row { grid-template-columns: 1fr 1fr; } }
    .stat-card { background: var(--tf-card); border-radius: 10px; padding: 18px; border: 1px solid rgba(255,255,255,0.06); }
    .stat-card .stat-label { font-size: 12px; color: var(--tf-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
    .stat-card .stat-value { font-size: 24px; font-weight: 800; }
    .shift-summary { background: var(--tf-card); border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); padding: 20px; margin-bottom: 24px; }
    .shift-summary h3 { font-size: 16px; font-weight: 700; margin: 0 0 16px 0; }
    .shift-bars { display: flex; gap: 4px; height: 32px; border-radius: 6px; overflow: hidden; }
    .shift-bar { display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 600; color: #fff; min-width: 20px; }
    .shift-bar.productive { background: #22c55e; }
    .shift-bar.downtime { background: #ef4444; }
    .shift-bar.idle { background: rgba(255,255,255,0.1); color: var(--tf-muted); }
    .shift-legend { display: flex; gap: 20px; margin-top: 10px; font-size: 12px; color: var(--tf-muted); }
    .shift-legend-dot { width: 10px; height: 10px; border-radius: 3px; display: inline-block; margin-right: 4px; }
    .data-card { background: var(--tf-card); border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); overflow: hidden; }
    .data-table { width: 100%; border-collapse: collapse; font-size: 14px; }
    .data-table thead th {
        background: #1a2744; padding: 14px 16px; text-align: left; font-weight: 700;
        font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--tf-muted);
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .data-table tbody td { padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.04); }
    .data-table tbody tr { transition: background 0.15s; cursor: pointer; }
    .data-table tbody tr:hover { background: rgba(255,255,255,0.04); }
    .badge { display: inline-block; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; }
    .badge-running { background: rgba(34,197,94,0.2); color: #4ade80; }
    .badge-stopped { background: rgba(148,163,184,0.2); color: #94a3b8; }
    .badge-downtime { background: rgba(239,68,68,0.2); color: #f87171; }
    .badge-break { background: rgba(212,168,67,0.2); color: var(--tf-gold); }
    .empty-state { text-align: center; padding: 60px 20px; color: var(--tf-muted); }
    .empty-state h3 { font-size: 18px; margin-bottom: 8px; color: var(--tf-text); }
    .loading { text-align: center; padding: 40px; color: var(--tf-muted); }
    .modal-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 1000; justify-content: center; align-items: center; }
    .modal-overlay.active { display: flex; }
    .modal { background: var(--tf-card); border-radius: 12px; padding: 28px; width: 520px; max-width: 90vw; border: 1px solid rgba(255,255,255,0.1); }
    .modal h2 { font-size: 20px; margin: 0 0 20px 0; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 24px; }
    .form-group { margin-bottom: 16px; }
    .form-group label { display: block; font-size: 13px; font-weight: 600; color: var(--tf-muted); margin-bottom: 6px; }
    .form-group input, .form-group select, .form-group textarea {
        width: 100%; background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px; font-family: inherit; box-sizing: border-box;
    }
    .form-group textarea { min-height: 60px; resize: vertical; }
</style>

<div class="log-container">
    <div class="page-header">
        <h1>Work Log</h1>
        <p>Operator activity, start/stop times, production counts, and shift summaries</p>
    </div>
    <div class="stats-row">
        <div class="stat-card"><div class="stat-label">Productive Hours</div><div class="stat-value" id="statProductive" style="color:#4ade80;">--</div></div>
        <div class="stat-card"><div class="stat-label">Downtime</div><div class="stat-value" id="statDowntime" style="color:#f87171;">--</div></div>
        <div class="stat-card"><div class="stat-label">Pieces Produced</div><div class="stat-value" id="statPieces" style="color:var(--tf-blue);">--</div></div>
        <div class="stat-card"><div class="stat-label">Efficiency</div><div class="stat-value" id="statEfficiency" style="color:var(--tf-gold);">--</div></div>
    </div>

    <div class="shift-summary">
        <h3>Today's Shift Timeline</h3>
        <div class="shift-bars" id="shiftBars"></div>
        <div class="shift-legend">
            <span><span class="shift-legend-dot" style="background:#22c55e;"></span> Productive</span>
            <span><span class="shift-legend-dot" style="background:#ef4444;"></span> Downtime</span>
            <span><span class="shift-legend-dot" style="background:rgba(255,255,255,0.1);"></span> Idle / Break</span>
        </div>
    </div>

    <div class="toolbar">
        <div style="display:flex;gap:10px;align-items:center;">
            <input type="text" id="logSearch" placeholder="Search logs..." oninput="filterLogs()">
            <select id="filterOperator" onchange="filterLogs()"><option value="">All Operators</option></select>
            <input type="date" id="filterDate" onchange="filterLogs()">
        </div>
        <div style="display:flex;gap:10px;">
            <button class="btn-outline" onclick="exportLogs()">Export</button>
            <button class="btn-gold" onclick="openModal('logModal')">+ Log Entry</button>
        </div>
    </div>
    <div class="data-card">
        <div id="logTableWrap" class="loading">Loading work log...</div>
    </div>
</div>

<div class="modal-overlay" id="logModal">
    <div class="modal">
        <h2>New Log Entry</h2>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div class="form-group"><label>Operator</label><input type="text" id="logOperator" placeholder="Name"></div>
            <div class="form-group"><label>Machine</label><select id="logMachine"><option value="machine-1">Machine 1</option><option value="machine-2">Machine 2</option><option value="machine-3">Machine 3</option></select></div>
            <div class="form-group"><label>Start Time</label><input type="time" id="logStart"></div>
            <div class="form-group"><label>End Time</label><input type="time" id="logEnd"></div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div class="form-group"><label>Type</label><select id="logType"><option value="production">Production</option><option value="downtime">Downtime</option><option value="setup">Setup</option><option value="break">Break</option></select></div>
            <div class="form-group"><label>Pieces Produced</label><input type="number" id="logPieces" value="0"></div>
        </div>
        <div class="form-group"><label>Job Code</label><input type="text" id="logJob" placeholder="Job code"></div>
        <div class="form-group"><label>Notes</label><textarea id="logNotes" placeholder="Notes about this entry..."></textarea></div>
        <div class="modal-actions">
            <button class="btn-outline" onclick="closeModal('logModal')">Cancel</button>
            <button class="btn-gold" onclick="saveLog()">Save Entry</button>
        </div>
    </div>
</div>

<script>
let allLogs = [];

function openModal(id) { document.getElementById(id).classList.add('active'); }
function closeModal(id) { document.getElementById(id).classList.remove('active'); }
document.querySelectorAll('.modal-overlay').forEach(m => m.addEventListener('click', function(e) { if (e.target === this) closeModal(this.id); }));

function renderTable(logs) {
    const wrap = document.getElementById('logTableWrap');
    if (!logs.length) {
        wrap.innerHTML = '<div class="empty-state"><h3>No log entries</h3><p>Add work log entries to track production activity.</p></div>';
        return;
    }
    let html = '<table class="data-table"><thead><tr><th>Date</th><th>Operator</th><th>Machine</th><th>Start</th><th>End</th><th>Type</th><th>Pieces</th><th>Job</th></tr></thead><tbody>';
    logs.forEach(l => {
        const typeCls = l.type === 'production' ? 'badge-running' : (l.type === 'downtime' ? 'badge-downtime' : (l.type === 'break' ? 'badge-break' : 'badge-stopped'));
        html += '<tr><td>' + (l.date||'--') + '</td><td>' + (l.operator||'--') + '</td><td>' + (l.machine||'--') + '</td>' +
            '<td>' + (l.start_time||'--') + '</td><td>' + (l.end_time||'--') + '</td>' +
            '<td><span class="badge ' + typeCls + '">' + (l.type||'--') + '</span></td>' +
            '<td>' + (l.pieces||0) + '</td><td style="color:var(--tf-blue);">' + (l.job_code||'--') + '</td></tr>';
    });
    html += '</tbody></table>';
    wrap.innerHTML = html;
}

function renderShiftBars(logs) {
    const bars = document.getElementById('shiftBars');
    const today = logs.filter(l => l.date === new Date().toISOString().slice(0,10));
    if (!today.length) {
        bars.innerHTML = '<div class="shift-bar idle" style="flex:1;">No data today</div>';
        return;
    }
    const prod = today.filter(l => l.type === 'production').length;
    const down = today.filter(l => l.type === 'downtime').length;
    const other = today.length - prod - down;
    const total = today.length || 1;
    bars.innerHTML = (prod ? '<div class="shift-bar productive" style="flex:' + prod + ';">' + Math.round(prod/total*100) + '%</div>' : '') +
        (down ? '<div class="shift-bar downtime" style="flex:' + down + ';">' + Math.round(down/total*100) + '%</div>' : '') +
        (other ? '<div class="shift-bar idle" style="flex:' + other + ';">' + Math.round(other/total*100) + '%</div>' : '');
}

function updateStats(logs) {
    const today = logs.filter(l => l.date === new Date().toISOString().slice(0,10));
    const prodHrs = today.filter(l => l.type === 'production').reduce((s, l) => {
        if (l.start_time && l.end_time) {
            const [sh,sm] = l.start_time.split(':').map(Number);
            const [eh,em] = l.end_time.split(':').map(Number);
            return s + ((eh*60+em) - (sh*60+sm)) / 60;
        }
        return s;
    }, 0);
    const downHrs = today.filter(l => l.type === 'downtime').reduce((s, l) => {
        if (l.start_time && l.end_time) {
            const [sh,sm] = l.start_time.split(':').map(Number);
            const [eh,em] = l.end_time.split(':').map(Number);
            return s + ((eh*60+em) - (sh*60+sm)) / 60;
        }
        return s;
    }, 0);
    document.getElementById('statProductive').textContent = prodHrs.toFixed(1) + 'h';
    document.getElementById('statDowntime').textContent = downHrs.toFixed(1) + 'h';
    const pieces = today.reduce((s, l) => s + (l.pieces || 0), 0);
    document.getElementById('statPieces').textContent = pieces;
    const eff = (prodHrs + downHrs) > 0 ? Math.round(prodHrs / (prodHrs + downHrs) * 100) : 0;
    document.getElementById('statEfficiency').textContent = eff + '%';
}

function filterLogs() {
    const search = document.getElementById('logSearch').value.toLowerCase();
    const operator = document.getElementById('filterOperator').value;
    const date = document.getElementById('filterDate').value;
    const filtered = allLogs.filter(l => {
        if (search && !(l.operator||'').toLowerCase().includes(search) && !(l.job_code||'').toLowerCase().includes(search)) return false;
        if (operator && l.operator !== operator) return false;
        if (date && l.date !== date) return false;
        return true;
    });
    renderTable(filtered);
}

function exportLogs() {
    const rows = [['Date','Operator','Machine','Start','End','Type','Pieces','Job','Notes']];
    allLogs.forEach(l => rows.push([l.date||'',l.operator||'',l.machine||'',l.start_time||'',l.end_time||'',l.type||'',l.pieces||0,l.job_code||'',l.notes||'']));
    const csv = rows.map(r => r.map(c => '"' + (c+'').replace(/"/g,'""') + '"').join(',')).join('\n');
    const blob = new Blob([csv], {type:'text/csv'});
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'work_log.csv'; a.click();
}

async function saveLog() {
    const payload = {
        operator: document.getElementById('logOperator').value,
        machine: document.getElementById('logMachine').value,
        start_time: document.getElementById('logStart').value,
        end_time: document.getElementById('logEnd').value,
        type: document.getElementById('logType').value,
        pieces: parseInt(document.getElementById('logPieces').value) || 0,
        job_code: document.getElementById('logJob').value,
        notes: document.getElementById('logNotes').value,
        date: new Date().toISOString().slice(0,10)
    };
    if (!payload.operator) { alert('Operator is required'); return; }
    try {
        await fetch('/api/workstation/log', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
        closeModal('logModal');
        loadLogs();
    } catch(e) { alert('Error: ' + e.message); }
}

async function loadLogs() {
    try {
        const resp = await fetch('/api/workstation/log');
        const data = await resp.json();
        allLogs = Array.isArray(data) ? data : (data.entries || []);
        const ops = [...new Set(allLogs.map(l => l.operator).filter(Boolean))];
        const sel = document.getElementById('filterOperator');
        if (sel.options.length <= 1) ops.forEach(o => { const opt = document.createElement('option'); opt.value = o; opt.textContent = o; sel.appendChild(opt); });
        updateStats(allLogs);
        renderShiftBars(allLogs);
        renderTable(allLogs);
    } catch(e) { renderTable([]); }
}

loadLogs();
</script>
"""
