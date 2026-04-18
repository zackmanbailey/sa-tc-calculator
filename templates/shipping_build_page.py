"""
TitanForge v4 — Build Loads
==============================
Load builder, select items by project, weight/dimension constraints, optimize loading.
"""

SHIPPING_BUILD_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a;
        --tf-card: #1e293b;
        --tf-text: #e2e8f0;
        --tf-muted: #94a3b8;
        --tf-gold: #d4a843;
        --tf-blue: #3b82f6;
    }
    .build-container {
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
    .btn-blue { background: var(--tf-blue); color: #fff; border: none; border-radius: 8px; padding: 10px 20px; font-weight: 700; font-size: 14px; cursor: pointer; }
    .btn-outline { background: transparent; color: var(--tf-muted); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 10px 20px; font-weight: 600; font-size: 14px; cursor: pointer; }
    .btn-outline:hover { border-color: var(--tf-gold); color: var(--tf-gold); }
    .btn-sm { padding: 6px 14px; font-size: 12px; border-radius: 6px; }
    .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    @media (max-width: 1000px) { .two-col { grid-template-columns: 1fr; } }
    .panel {
        background: var(--tf-card); border-radius: 12px; border: 1px solid rgba(255,255,255,0.06);
        padding: 20px; min-height: 400px;
    }
    .panel h3 { font-size: 16px; font-weight: 700; margin: 0 0 16px 0; }
    .capacity-bar { margin-bottom: 20px; }
    .capacity-label { display: flex; justify-content: space-between; font-size: 13px; color: var(--tf-muted); margin-bottom: 6px; }
    .capacity-track { height: 10px; background: rgba(255,255,255,0.08); border-radius: 5px; overflow: hidden; }
    .capacity-fill { height: 100%; border-radius: 5px; transition: width 0.3s; }
    .capacity-fill.ok { background: linear-gradient(90deg, #22c55e, #4ade80); }
    .capacity-fill.warn { background: linear-gradient(90deg, var(--tf-gold), #f59e0b); }
    .capacity-fill.over { background: linear-gradient(90deg, #ef4444, #f87171); }
    .item-list { max-height: 350px; overflow-y: auto; }
    .avail-item {
        display: flex; align-items: center; gap: 10px; padding: 10px; margin-bottom: 6px;
        background: var(--tf-bg); border-radius: 8px; cursor: pointer; transition: background 0.15s;
        border: 1px solid transparent;
    }
    .avail-item:hover { background: rgba(255,255,255,0.04); border-color: var(--tf-blue); }
    .avail-item.selected { border-color: var(--tf-gold); background: rgba(212,168,67,0.1); }
    .avail-item .item-name { flex: 1; font-size: 14px; font-weight: 600; }
    .avail-item .item-meta { font-size: 12px; color: var(--tf-muted); }
    .load-item {
        display: flex; align-items: center; gap: 10px; padding: 10px; margin-bottom: 6px;
        background: var(--tf-bg); border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);
    }
    .load-item .item-name { flex: 1; font-size: 14px; font-weight: 600; }
    .load-item .item-weight { font-size: 13px; color: var(--tf-gold); font-weight: 600; }
    .btn-remove-sm { background: rgba(239,68,68,0.2); color: #f87171; border: none; border-radius: 4px; padding: 4px 8px; cursor: pointer; font-size: 11px; }
    .load-summary {
        display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin-top: 16px;
        padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.06);
    }
    .summary-item { text-align: center; }
    .summary-value { font-size: 20px; font-weight: 800; }
    .summary-label { font-size: 11px; color: var(--tf-muted); text-transform: uppercase; }
    .trailer-config { margin-bottom: 16px; }
    .trailer-config select, .trailer-config input {
        background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px; padding: 8px 12px; color: var(--tf-text); font-size: 14px;
        margin-right: 8px;
    }
    .empty-state { text-align: center; padding: 40px 20px; color: var(--tf-muted); }
    .empty-state h3 { font-size: 16px; margin-bottom: 6px; color: var(--tf-text); }
    .badge { display: inline-block; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; }
    .badge-blue { background: rgba(59,130,246,0.2); color: #60a5fa; }
</style>

<div class="build-container">
    <div class="page-header">
        <h1>Build Loads</h1>
        <p>Select items by project, manage weight/dimension constraints, and optimize loading order</p>
    </div>
    <div class="toolbar">
        <div style="display:flex;gap:10px;align-items:center;">
            <select id="projectFilter" onchange="loadAvailableItems()">
                <option value="">All Projects</option>
            </select>
            <input type="text" id="itemSearch" placeholder="Search items..." oninput="filterAvailable()">
        </div>
        <div style="display:flex;gap:10px;">
            <button class="btn-outline" onclick="optimizeLoad()">Auto-Optimize</button>
            <button class="btn-gold" onclick="createBOL()">Create BOL from Load</button>
        </div>
    </div>

    <div class="two-col">
        <div class="panel">
            <h3>Available Items <span id="availCount" style="font-weight:400;color:var(--tf-muted);font-size:13px;"></span></h3>
            <div class="item-list" id="availableList">
                <div class="empty-state"><h3>No items available</h3><p>Ready-to-ship items will appear here.</p></div>
            </div>
        </div>
        <div class="panel">
            <h3>Current Load <span id="loadCount" style="font-weight:400;color:var(--tf-muted);font-size:13px;"></span></h3>
            <div class="trailer-config">
                <select id="trailerType" onchange="updateCapacity()">
                    <option value="flatbed" data-max="48000" data-len="48">Flatbed (48ft, 48,000 lbs)</option>
                    <option value="stepdeck" data-max="44000" data-len="48">Step Deck (48ft, 44,000 lbs)</option>
                    <option value="hotshot" data-max="16000" data-len="40">Hotshot (40ft, 16,000 lbs)</option>
                </select>
            </div>
            <div class="capacity-bar">
                <div class="capacity-label"><span>Weight Capacity</span><span id="weightLabel">0 / 48,000 lbs</span></div>
                <div class="capacity-track"><div class="capacity-fill ok" id="weightBar" style="width:0%;"></div></div>
            </div>
            <div class="capacity-bar">
                <div class="capacity-label"><span>Length Capacity</span><span id="lengthLabel">0 / 48 ft</span></div>
                <div class="capacity-track"><div class="capacity-fill ok" id="lengthBar" style="width:0%;"></div></div>
            </div>
            <div class="item-list" id="loadList">
                <div class="empty-state"><h3>Load is empty</h3><p>Click items on the left to add them.</p></div>
            </div>
            <div class="load-summary">
                <div class="summary-item"><div class="summary-value" id="sumWeight">0</div><div class="summary-label">Total LBS</div></div>
                <div class="summary-item"><div class="summary-value" id="sumPieces">0</div><div class="summary-label">Pieces</div></div>
                <div class="summary-item"><div class="summary-value" id="sumLength">0</div><div class="summary-label">Linear FT</div></div>
            </div>
        </div>
    </div>
</div>

<script>
let availableItems = [];
let loadItems = [];

function getTrailerMax() {
    const sel = document.getElementById('trailerType');
    const opt = sel.options[sel.selectedIndex];
    return { weight: parseInt(opt.dataset.max) || 48000, length: parseInt(opt.dataset.len) || 48 };
}

function updateCapacity() {
    const max = getTrailerMax();
    const totalWeight = loadItems.reduce((s, i) => s + (i.weight || 0), 0);
    const totalLength = loadItems.reduce((s, i) => s + (i.length || 0), 0);
    const wPct = Math.min(100, Math.round(totalWeight / max.weight * 100));
    const lPct = Math.min(100, Math.round(totalLength / max.length * 100));
    document.getElementById('weightBar').style.width = wPct + '%';
    document.getElementById('weightBar').className = 'capacity-fill ' + (wPct > 95 ? 'over' : (wPct > 80 ? 'warn' : 'ok'));
    document.getElementById('weightLabel').textContent = totalWeight.toLocaleString() + ' / ' + max.weight.toLocaleString() + ' lbs';
    document.getElementById('lengthBar').style.width = lPct + '%';
    document.getElementById('lengthBar').className = 'capacity-fill ' + (lPct > 95 ? 'over' : (lPct > 80 ? 'warn' : 'ok'));
    document.getElementById('lengthLabel').textContent = totalLength + ' / ' + max.length + ' ft';
    document.getElementById('sumWeight').textContent = totalWeight.toLocaleString();
    document.getElementById('sumPieces').textContent = loadItems.length;
    document.getElementById('sumLength').textContent = totalLength;
}

function renderAvailable(items) {
    const list = document.getElementById('availableList');
    document.getElementById('availCount').textContent = '(' + items.length + ')';
    if (!items.length) {
        list.innerHTML = '<div class="empty-state"><h3>No items available</h3><p>Ready-to-ship items will appear here.</p></div>';
        return;
    }
    list.innerHTML = items.map((it, i) => {
        const inLoad = loadItems.some(l => l.id === it.id);
        return '<div class="avail-item ' + (inLoad ? 'selected' : '') + '" onclick="toggleItem(' + i + ')">' +
            '<div class="item-name">' + (it.description || it.component || 'Item') + '</div>' +
            '<div class="item-meta">' + (it.job_code || '') + ' | ' + (it.weight || 0) + ' lbs | ' + (it.length || 0) + ' ft</div></div>';
    }).join('');
}

function renderLoad() {
    const list = document.getElementById('loadList');
    document.getElementById('loadCount').textContent = '(' + loadItems.length + ')';
    if (!loadItems.length) {
        list.innerHTML = '<div class="empty-state"><h3>Load is empty</h3><p>Click items on the left to add them.</p></div>';
        updateCapacity(); return;
    }
    list.innerHTML = loadItems.map((it, i) =>
        '<div class="load-item"><div class="item-name">' + (it.description || it.component || 'Item') + '</div>' +
        '<div class="item-weight">' + (it.weight || 0) + ' lbs</div>' +
        '<span class="badge badge-blue">' + (it.job_code || '') + '</span>' +
        '<button class="btn-remove-sm" onclick="removeFromLoad(' + i + ')">Remove</button></div>'
    ).join('');
    updateCapacity();
}

function toggleItem(idx) {
    const item = availableItems[idx];
    if (!item) return;
    const existIdx = loadItems.findIndex(l => l.id === item.id);
    if (existIdx >= 0) {
        loadItems.splice(existIdx, 1);
    } else {
        loadItems.push({ ...item });
    }
    renderAvailable(availableItems);
    renderLoad();
}

function removeFromLoad(idx) {
    loadItems.splice(idx, 1);
    renderAvailable(availableItems);
    renderLoad();
}

function filterAvailable() {
    const search = document.getElementById('itemSearch').value.toLowerCase();
    const filtered = availableItems.filter(i =>
        !search || (i.description||'').toLowerCase().includes(search) || (i.component||'').toLowerCase().includes(search) || (i.job_code||'').toLowerCase().includes(search)
    );
    renderAvailable(filtered);
}

function optimizeLoad() {
    const max = getTrailerMax();
    loadItems = [];
    const sorted = [...availableItems].sort((a, b) => (b.weight || 0) - (a.weight || 0));
    let totalWeight = 0, totalLength = 0;
    for (const item of sorted) {
        if (totalWeight + (item.weight || 0) <= max.weight && totalLength + (item.length || 0) <= max.length) {
            loadItems.push({ ...item });
            totalWeight += item.weight || 0;
            totalLength += item.length || 0;
        }
    }
    renderAvailable(availableItems);
    renderLoad();
}

function createBOL() {
    if (!loadItems.length) { alert('Add items to the load first'); return; }
    const items = loadItems.map(i => ({ description: i.description || i.component, quantity: 1, weight: i.weight || 0 }));
    sessionStorage.setItem('bol_items', JSON.stringify(items));
    sessionStorage.setItem('bol_weight', loadItems.reduce((s, i) => s + (i.weight || 0), 0));
    window.location.href = '/shipping/bol';
}

async function loadAvailableItems() {
    const project = document.getElementById('projectFilter').value;
    try {
        const url = project ? '/api/shipping/available?project=' + encodeURIComponent(project) : '/api/shipping/available';
        const resp = await fetch(url);
        const data = await resp.json();
        availableItems = Array.isArray(data) ? data : (data.items || []);
        renderAvailable(availableItems);
    } catch(e) { renderAvailable([]); }
}

async function loadProjects() {
    try {
        const resp = await fetch('/api/projects/full');
        const data = await resp.json();
        const projects = Array.isArray(data) ? data : (data.projects || []);
        const sel = document.getElementById('projectFilter');
        projects.forEach(p => {
            const o = document.createElement('option');
            o.value = p.id || p.job_code || '';
            o.textContent = (p.job_code || '') + ' - ' + (p.project_name || p.name || '');
            sel.appendChild(o);
        });
    } catch(e) {}
}

loadProjects();
loadAvailableItems();
</script>
"""
