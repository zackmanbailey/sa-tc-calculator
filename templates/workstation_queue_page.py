"""
TitanForge v4 — Work Queue
==============================
Jobs waiting to be processed, priority ordering, estimated time, assign to machine.
"""

WORKSTATION_QUEUE_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a;
        --tf-card: #1e293b;
        --tf-text: #e2e8f0;
        --tf-muted: #94a3b8;
        --tf-gold: #d4a843;
        --tf-blue: #3b82f6;
    }
    .queue-container {
        max-width: 1400px; margin: 0 auto; padding: 24px 32px;
        font-family: 'Inter', system-ui, -apple-system, sans-serif; color: var(--tf-text);
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
    .stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
    @media (max-width: 900px) { .stats-row { grid-template-columns: 1fr 1fr; } }
    .stat-card { background: var(--tf-card); border-radius: 10px; padding: 18px; border: 1px solid rgba(255,255,255,0.06); }
    .stat-card .stat-label { font-size: 12px; color: var(--tf-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
    .stat-card .stat-value { font-size: 24px; font-weight: 800; }
    .queue-list { display: flex; flex-direction: column; gap: 8px; }
    .queue-item {
        background: var(--tf-card); border-radius: 10px; border: 1px solid rgba(255,255,255,0.06);
        padding: 16px 20px; display: flex; align-items: center; gap: 16px;
        cursor: grab; transition: border-color 0.2s, background 0.2s;
    }
    .queue-item:hover { border-color: var(--tf-blue); background: rgba(30,41,59,0.9); }
    .queue-item.dragging { opacity: 0.5; border-color: var(--tf-gold); }
    .queue-pos { font-size: 20px; font-weight: 800; color: var(--tf-muted); width: 36px; text-align: center; flex-shrink: 0; }
    .queue-grip { color: var(--tf-muted); cursor: grab; flex-shrink: 0; font-size: 18px; letter-spacing: 2px; }
    .queue-info { flex: 1; }
    .queue-info h4 { font-size: 15px; font-weight: 700; margin: 0 0 4px 0; }
    .queue-info .queue-meta { font-size: 13px; color: var(--tf-muted); display: flex; gap: 16px; flex-wrap: wrap; }
    .queue-actions { display: flex; gap: 8px; align-items: center; flex-shrink: 0; }
    .badge { display: inline-block; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; }
    .badge-rush { background: rgba(239,68,68,0.2); color: #f87171; }
    .badge-normal { background: rgba(59,130,246,0.2); color: #60a5fa; }
    .badge-low { background: rgba(148,163,184,0.2); color: #94a3b8; }
    .badge-queued { background: rgba(212,168,67,0.2); color: var(--tf-gold); }
    .badge-running { background: rgba(34,197,94,0.2); color: #4ade80; }
    .time-est { font-size: 13px; color: var(--tf-blue); font-weight: 600; }
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
    .form-group input, .form-group select {
        width: 100%; background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px; box-sizing: border-box;
    }
</style>

<div class="queue-container">
    <div class="page-header">
        <h1>Work Queue</h1>
        <p>Jobs waiting to be processed, ordered by priority. Drag to reorder.</p>
    </div>
    <div class="stats-row">
        <div class="stat-card"><div class="stat-label">In Queue</div><div class="stat-value" id="statQueue" style="color:var(--tf-gold);">--</div></div>
        <div class="stat-card"><div class="stat-label">Running Now</div><div class="stat-value" id="statRunning" style="color:#4ade80;">--</div></div>
        <div class="stat-card"><div class="stat-label">Est. Total Time</div><div class="stat-value" id="statTime" style="color:var(--tf-blue);">--</div></div>
        <div class="stat-card"><div class="stat-label">Rush Orders</div><div class="stat-value" id="statRush" style="color:#f87171;">--</div></div>
    </div>
    <div class="toolbar">
        <div style="display:flex;gap:10px;align-items:center;">
            <input type="text" id="queueSearch" placeholder="Search queue..." oninput="filterQueue()">
            <select id="filterMachine" onchange="filterQueue()">
                <option value="">All Machines</option>
                <option value="machine-1">Machine 1</option>
                <option value="machine-2">Machine 2</option>
                <option value="machine-3">Machine 3</option>
                <option value="unassigned">Unassigned</option>
            </select>
        </div>
        <button class="btn-gold" onclick="openModal('addModal')">+ Add to Queue</button>
    </div>
    <div class="queue-list" id="queueList">
        <div class="loading">Loading queue...</div>
    </div>
</div>

<div class="modal-overlay" id="addModal">
    <div class="modal">
        <h2>Add to Queue</h2>
        <div class="form-group"><label>Job Code</label><input type="text" id="addJob" placeholder="e.g. 2026-0015"></div>
        <div class="form-group"><label>Description</label><input type="text" id="addDesc" placeholder="What needs to be done"></div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div class="form-group"><label>Priority</label><select id="addPriority"><option value="normal">Normal</option><option value="rush">Rush</option><option value="low">Low</option></select></div>
            <div class="form-group"><label>Est. Time (hrs)</label><input type="number" id="addTime" value="1" step="0.5"></div>
        </div>
        <div class="form-group"><label>Assign to Machine</label><select id="addMachine"><option value="">Unassigned</option><option value="machine-1">Machine 1</option><option value="machine-2">Machine 2</option><option value="machine-3">Machine 3</option></select></div>
        <div class="modal-actions">
            <button class="btn-outline" onclick="closeModal('addModal')">Cancel</button>
            <button class="btn-gold" onclick="addToQueue()">Add</button>
        </div>
    </div>
</div>

<script>
let allQueue = [];
let dragIdx = null;

function openModal(id) { document.getElementById(id).classList.add('active'); }
function closeModal(id) { document.getElementById(id).classList.remove('active'); }
document.querySelectorAll('.modal-overlay').forEach(m => m.addEventListener('click', function(e) { if (e.target === this) closeModal(this.id); }));

function renderQueue(items) {
    const list = document.getElementById('queueList');
    if (!items.length) {
        list.innerHTML = '<div class="empty-state"><h3>Queue is empty</h3><p>Add jobs to the queue to get started.</p></div>';
        return;
    }
    list.innerHTML = items.map((q, i) => {
        const prBadge = q.priority === 'rush' ? 'badge-rush' : (q.priority === 'low' ? 'badge-low' : 'badge-normal');
        const stBadge = q.status === 'running' ? 'badge-running' : 'badge-queued';
        return '<div class="queue-item" draggable="true" data-idx="' + i + '" ondragstart="dragStart(event,' + i + ')" ondragover="dragOver(event)" ondrop="drop(event,' + i + ')" ondragend="dragEnd(event)">' +
            '<span class="queue-grip">\u2261</span>' +
            '<span class="queue-pos">#' + (i+1) + '</span>' +
            '<div class="queue-info"><h4>' + (q.job_code || 'Unnamed') + ' &mdash; ' + (q.description || '') + '</h4>' +
            '<div class="queue-meta"><span class="badge ' + prBadge + '">' + (q.priority || 'normal') + '</span>' +
            '<span class="badge ' + stBadge + '">' + (q.status || 'queued') + '</span>' +
            '<span class="time-est">' + (q.est_hours || '?') + 'h est.</span>' +
            '<span>' + (q.machine || 'Unassigned') + '</span></div></div>' +
            '<div class="queue-actions">' +
            (q.status !== 'running' ? '<button class="btn-outline btn-sm" onclick="startJob(' + i + ',event)">Start</button>' : '<button class="btn-outline btn-sm" onclick="completeJob(' + i + ',event)">Done</button>') +
            '<button class="btn-outline btn-sm" onclick="removeJob(' + i + ',event)" style="color:#f87171;border-color:rgba(239,68,68,0.3);">X</button></div></div>';
    }).join('');
}

function updateStats(items) {
    document.getElementById('statQueue').textContent = items.filter(i => i.status !== 'running').length;
    document.getElementById('statRunning').textContent = items.filter(i => i.status === 'running').length;
    const totalHrs = items.reduce((s, i) => s + (i.est_hours || 0), 0);
    document.getElementById('statTime').textContent = totalHrs.toFixed(1) + 'h';
    document.getElementById('statRush').textContent = items.filter(i => i.priority === 'rush').length;
}

function filterQueue() {
    const search = document.getElementById('queueSearch').value.toLowerCase();
    const machine = document.getElementById('filterMachine').value;
    const filtered = allQueue.filter(q => {
        if (search && !(q.job_code||'').toLowerCase().includes(search) && !(q.description||'').toLowerCase().includes(search)) return false;
        if (machine === 'unassigned' && q.machine) return false;
        if (machine && machine !== 'unassigned' && q.machine !== machine) return false;
        return true;
    });
    renderQueue(filtered);
}

function dragStart(e, idx) { dragIdx = idx; e.target.classList.add('dragging'); }
function dragOver(e) { e.preventDefault(); }
function dragEnd(e) { e.target.classList.remove('dragging'); }
function drop(e, targetIdx) {
    e.preventDefault();
    if (dragIdx === null || dragIdx === targetIdx) return;
    const item = allQueue.splice(dragIdx, 1)[0];
    allQueue.splice(targetIdx, 0, item);
    dragIdx = null;
    renderQueue(allQueue);
    saveOrder();
}

async function saveOrder() {
    const order = allQueue.map((q, i) => ({ id: q.id, position: i }));
    try { await fetch('/api/workstation/queue/reorder', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(order) }); } catch(e) {}
}

function startJob(idx, event) {
    event.stopPropagation();
    allQueue[idx].status = 'running';
    updateStats(allQueue);
    renderQueue(allQueue);
    fetch('/api/workstation/queue/start', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ id: allQueue[idx].id }) }).catch(() => {});
}

function completeJob(idx, event) {
    event.stopPropagation();
    allQueue.splice(idx, 1);
    updateStats(allQueue);
    renderQueue(allQueue);
}

function removeJob(idx, event) {
    event.stopPropagation();
    if (!confirm('Remove this job from the queue?')) return;
    allQueue.splice(idx, 1);
    updateStats(allQueue);
    renderQueue(allQueue);
}

async function addToQueue() {
    const payload = {
        job_code: document.getElementById('addJob').value,
        description: document.getElementById('addDesc').value,
        priority: document.getElementById('addPriority').value,
        est_hours: parseFloat(document.getElementById('addTime').value) || 1,
        machine: document.getElementById('addMachine').value || null,
        status: 'queued'
    };
    if (!payload.job_code) { alert('Job code is required'); return; }
    try {
        await fetch('/api/workstation/queue', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
        closeModal('addModal');
        loadQueue();
    } catch(e) { alert('Error: ' + e.message); }
}

async function loadQueue() {
    try {
        const resp = await fetch('/api/workstation/queue');
        const data = await resp.json();
        allQueue = Array.isArray(data) ? data : (data.queue || []);
        updateStats(allQueue);
        renderQueue(allQueue);
    } catch(e) { renderQueue([]); }
}

loadQueue();
</script>
"""
