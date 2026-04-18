"""
TitanForge v4 — Build Loads
==============================
Load builder, select items by project, weight/dimension constraints, optimize loading.
Wired to LoadBuilder API endpoints for persistent load management.
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
        --tf-green: #10b981;
        --tf-red: #ef4444;
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
    .btn-blue:hover { opacity: 0.9; }
    .btn-green { background: var(--tf-green); color: #fff; border: none; border-radius: 8px; padding: 10px 20px; font-weight: 700; font-size: 14px; cursor: pointer; }
    .btn-green:hover { opacity: 0.9; }
    .btn-outline { background: transparent; color: var(--tf-muted); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 10px 20px; font-weight: 600; font-size: 14px; cursor: pointer; }
    .btn-outline:hover { border-color: var(--tf-gold); color: var(--tf-gold); }
    .btn-sm { padding: 6px 14px; font-size: 12px; border-radius: 6px; }
    .btn-danger { background: var(--tf-red); color: #fff; border: none; border-radius: 8px; padding: 6px 14px; font-size: 12px; cursor: pointer; }

    /* Existing loads strip */
    .loads-strip { display: flex; gap: 12px; margin-bottom: 20px; overflow-x: auto; padding-bottom: 8px; }
    .load-chip {
        background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px;
        padding: 12px 18px; min-width: 200px; cursor: pointer; transition: border-color 0.2s;
        flex-shrink: 0;
    }
    .load-chip:hover { border-color: var(--tf-blue); }
    .load-chip.active { border-color: var(--tf-gold); background: rgba(212,168,67,0.08); }
    .load-chip h4 { font-size: 14px; font-weight: 700; margin: 0 0 4px 0; }
    .load-chip .chip-meta { font-size: 12px; color: var(--tf-muted); }
    .load-chip .chip-status { font-size: 11px; font-weight: 700; text-transform: uppercase; margin-top: 4px; }
    .load-chip .chip-status.building { color: var(--tf-gold); }
    .load-chip .chip-status.ready { color: var(--tf-green); }

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
    .item-list { max-height: 400px; overflow-y: auto; }
    .avail-item {
        display: flex; align-items: center; gap: 10px; padding: 10px 12px; margin-bottom: 6px;
        background: var(--tf-bg); border-radius: 8px; cursor: pointer; transition: background 0.15s;
        border: 1px solid transparent;
    }
    .avail-item:hover { background: rgba(255,255,255,0.04); border-color: var(--tf-blue); }
    .avail-item.selected { border-color: var(--tf-gold); background: rgba(212,168,67,0.1); }
    .avail-item .item-mark { font-size: 13px; font-weight: 700; color: var(--tf-gold); min-width: 60px; }
    .avail-item .item-name { flex: 1; font-size: 14px; font-weight: 600; }
    .avail-item .item-meta { font-size: 12px; color: var(--tf-muted); text-align: right; }
    .avail-item .item-dims { font-size: 11px; color: var(--tf-muted); }
    .project-group-header {
        font-size: 12px; font-weight: 700; color: var(--tf-gold); text-transform: uppercase;
        letter-spacing: 0.5px; padding: 8px 12px; margin-top: 8px;
        border-bottom: 1px solid rgba(212,168,67,0.2);
    }
    .load-item {
        display: flex; align-items: center; gap: 10px; padding: 10px 12px; margin-bottom: 6px;
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
    .trailer-config { margin-bottom: 16px; display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
    .trailer-config select, .trailer-config input {
        background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px; padding: 8px 12px; color: var(--tf-text); font-size: 14px;
    }
    .empty-state { text-align: center; padding: 40px 20px; color: var(--tf-muted); }
    .empty-state h3 { font-size: 16px; margin-bottom: 6px; color: var(--tf-text); }
    .badge { display: inline-block; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; }
    .badge-blue { background: rgba(59,130,246,0.2); color: #60a5fa; }
    .badge-green { background: rgba(34,197,94,0.2); color: #4ade80; }
    .badge-gold { background: rgba(212,168,67,0.2); color: var(--tf-gold); }

    /* Finalize modal */
    .modal-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 1000; justify-content: center; align-items: center; }
    .modal-overlay.active { display: flex; }
    .modal { background: var(--tf-card); border-radius: 12px; padding: 28px; width: 480px; max-width: 90vw; border: 1px solid rgba(255,255,255,0.1); }
    .modal h2 { font-size: 20px; margin: 0 0 20px 0; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 24px; }
    .form-group { margin-bottom: 16px; }
    .form-group label { display: block; font-size: 13px; font-weight: 600; color: var(--tf-muted); margin-bottom: 6px; }
    .form-group input, .form-group select {
        width: 100%; background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px; box-sizing: border-box;
    }

    @media (max-width: 768px) {
        .build-container { padding: 16px; }
        .toolbar { flex-direction: column; align-items: stretch; }
        .toolbar input[type="text"] { width: 100%; }
        .two-col { grid-template-columns: 1fr; }
        .loads-strip { flex-direction: column; }
    }
</style>

<div class="build-container">
    <div class="page-header">
        <h1>Build Loads</h1>
        <p>Select items by project, manage weight/dimension constraints, and optimize loading order</p>
    </div>

    <!-- Existing Loads Strip -->
    <div class="loads-strip" id="loadsStrip">
        <div class="load-chip" onclick="createNewLoad()" style="border-style:dashed;border-color:var(--tf-gold);text-align:center;display:flex;align-items:center;justify-content:center;">
            <div>
                <h4 style="color:var(--tf-gold);">+ New Load</h4>
                <div class="chip-meta">Create a new load</div>
            </div>
        </div>
    </div>

    <div class="toolbar">
        <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
            <select id="projectFilter" onchange="loadAvailableItems()">
                <option value="">All Projects</option>
            </select>
            <input type="text" id="itemSearch" placeholder="Search items..." oninput="filterAvailable()">
        </div>
        <div style="display:flex;gap:10px;flex-wrap:wrap;">
            <button class="btn-outline" onclick="optimizeLoad()">Auto-Optimize</button>
            <button class="btn-green" onclick="openFinalizeModal()" id="btnFinalize" style="display:none;">Finalize Load</button>
            <button class="btn-gold" onclick="createBOL()">Create BOL from Load</button>
        </div>
    </div>

    <div class="two-col">
        <div class="panel">
            <h3>Available Items <span id="availCount" style="font-weight:400;color:var(--tf-muted);font-size:13px;"></span></h3>
            <div class="item-list" id="availableList">
                <div class="empty-state"><h3>No items available</h3><p>Ready-to-ship items from completed work orders will appear here.</p></div>
            </div>
        </div>
        <div class="panel">
            <h3>Current Load <span id="loadLabel" style="font-weight:400;color:var(--tf-gold);font-size:13px;"></span> <span id="loadCount" style="font-weight:400;color:var(--tf-muted);font-size:13px;"></span></h3>
            <div class="trailer-config">
                <select id="trailerType" onchange="updateCapacity()">
                    <option value="flatbed" data-max="48000" data-len="48">Flatbed (48ft, 48,000 lbs)</option>
                    <option value="stepdeck" data-max="44000" data-len="48">Step Deck (48ft, 44,000 lbs)</option>
                    <option value="hotshot" data-max="16000" data-len="40">Hotshot (40ft, 16,000 lbs)</option>
                    <option value="custom" data-max="45000" data-len="53">Custom (53ft, 45,000 lbs)</option>
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
                <div class="empty-state"><h3>Load is empty</h3><p>Click items on the left to add them, or use Auto-Optimize.</p></div>
            </div>
            <div class="load-summary">
                <div class="summary-item"><div class="summary-value" id="sumWeight">0</div><div class="summary-label">Total LBS</div></div>
                <div class="summary-item"><div class="summary-value" id="sumPieces">0</div><div class="summary-label">Pieces</div></div>
                <div class="summary-item"><div class="summary-value" id="sumLength">0</div><div class="summary-label">Linear FT</div></div>
            </div>
        </div>
    </div>
</div>

<!-- Create Load Modal -->
<div class="modal-overlay" id="createModal">
    <div class="modal">
        <h2>Create New Load</h2>
        <div class="form-group"><label>Project / Job Code</label>
            <select id="newLoadProject"></select>
        </div>
        <div class="form-group"><label>Truck Number (optional)</label>
            <input type="text" id="newLoadTruck" placeholder="e.g. TRK-042">
        </div>
        <div class="form-group"><label>Driver (optional)</label>
            <input type="text" id="newLoadDriver" placeholder="Driver name">
        </div>
        <div class="modal-actions">
            <button class="btn-outline" onclick="closeModal('createModal')">Cancel</button>
            <button class="btn-gold" onclick="submitNewLoad()">Create Load</button>
        </div>
    </div>
</div>

<!-- Finalize Modal -->
<div class="modal-overlay" id="finalizeModal">
    <div class="modal">
        <h2>Finalize Load</h2>
        <p style="color:var(--tf-muted);font-size:14px;margin-bottom:16px;">Once finalized, this load will be locked and a load number generated. You can then create a BOL from it.</p>
        <div id="finalizeSummary" style="background:var(--tf-bg);border-radius:8px;padding:16px;margin-bottom:16px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:8px;"><span style="color:var(--tf-muted)">Items:</span><span id="fPieces" style="font-weight:700;">0</span></div>
            <div style="display:flex;justify-content:space-between;margin-bottom:8px;"><span style="color:var(--tf-muted)">Total Weight:</span><span id="fWeight" style="font-weight:700;">0 lbs</span></div>
            <div style="display:flex;justify-content:space-between;"><span style="color:var(--tf-muted)">Linear Feet:</span><span id="fLength" style="font-weight:700;">0 ft</span></div>
        </div>
        <div class="modal-actions">
            <button class="btn-outline" onclick="closeModal('finalizeModal')">Cancel</button>
            <button class="btn-green" onclick="finalizeCurrentLoad()">Finalize & Lock</button>
        </div>
    </div>
</div>

<script>
let availableItems = [];
let loadItems = [];
let allLoads = [];
let currentLoadId = null;
let projects = [];

function openModal(id) { document.getElementById(id).classList.add('active'); }
function closeModal(id) { document.getElementById(id).classList.remove('active'); }
document.querySelectorAll('.modal-overlay').forEach(m => m.addEventListener('click', function(e) { if (e.target === this) closeModal(this.id); }));

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
    // Show/hide finalize button
    document.getElementById('btnFinalize').style.display = loadItems.length > 0 && currentLoadId ? '' : 'none';
}

function renderAvailable(items) {
    const list = document.getElementById('availableList');
    document.getElementById('availCount').textContent = '(' + items.length + ')';
    if (!items.length) {
        list.innerHTML = '<div class="empty-state"><h3>No items available</h3><p>Ready-to-ship items from completed work orders will appear here.</p></div>';
        return;
    }
    // Group by project
    const grouped = {};
    items.forEach(it => {
        const key = it.project_name || it.job_code || 'Unassigned';
        if (!grouped[key]) grouped[key] = [];
        grouped[key].push(it);
    });

    let html = '';
    for (const [proj, projItems] of Object.entries(grouped)) {
        html += '<div class="project-group-header">' + proj + ' (' + projItems.length + ' items)</div>';
        projItems.forEach((it, i) => {
            const globalIdx = items.indexOf(it);
            const inLoad = loadItems.some(l => l.id === it.id);
            const mark = it.mark || it.item_id || '';
            const desc = it.description || it.component || 'Item';
            const dims = it.dimensions || ((it.width ? it.width + '" x ' : '') + (it.height ? it.height + '"' : ''));
            html += '<div class="avail-item ' + (inLoad ? 'selected' : '') + '" onclick="toggleItem(' + globalIdx + ')">' +
                (mark ? '<div class="item-mark">' + mark + '</div>' : '') +
                '<div style="flex:1;"><div class="item-name">' + desc + '</div>' +
                (dims ? '<div class="item-dims">' + dims + '</div>' : '') +
                '</div>' +
                '<div class="item-meta">' +
                '<div>Qty: ' + (it.quantity || 1) + '</div>' +
                '<div>' + (it.weight || 0) + ' lbs</div>' +
                '<div>' + (it.length || 0) + ' ft</div></div></div>';
        });
    }
    list.innerHTML = html;
}

function renderLoad() {
    const list = document.getElementById('loadList');
    document.getElementById('loadCount').textContent = '(' + loadItems.length + ')';
    if (!loadItems.length) {
        list.innerHTML = '<div class="empty-state"><h3>Load is empty</h3><p>Click items on the left to add them, or use Auto-Optimize.</p></div>';
        updateCapacity(); return;
    }
    const currentLoad = allLoads.find(l => l.load_id === currentLoadId);
    const isFinalized = currentLoad && currentLoad.status === 'ready';
    list.innerHTML = loadItems.map((it, i) => {
        const mark = it.mark || it.item_id || '';
        return '<div class="load-item">' +
            (mark ? '<span style="font-size:12px;font-weight:700;color:var(--tf-gold);min-width:55px;">' + mark + '</span>' : '') +
            '<div class="item-name">' + (it.description || it.component || 'Item') + '</div>' +
            '<div class="item-weight">' + (it.weight || 0) + ' lbs</div>' +
            '<span class="badge badge-blue">' + (it.job_code || '') + '</span>' +
            (isFinalized ? '' : '<button class="btn-remove-sm" onclick="removeFromLoad(' + i + ')">Remove</button>') +
            '</div>';
    }).join('');
    updateCapacity();
}

function toggleItem(idx) {
    const item = availableItems[idx];
    if (!item) return;
    const existIdx = loadItems.findIndex(l => l.id === item.id);
    if (existIdx >= 0) {
        removeFromLoadByItem(item);
    } else {
        addToLoad(item);
    }
}

async function addToLoad(item) {
    if (!currentLoadId) {
        alert('Create or select a load first.');
        return;
    }
    const currentLoad = allLoads.find(l => l.load_id === currentLoadId);
    if (currentLoad && currentLoad.status === 'ready') {
        alert('This load is finalized. Create a new load to add items.');
        return;
    }
    loadItems.push({ ...item });
    renderAvailable(availableItems);
    renderLoad();
    // Persist to backend
    try {
        await fetch('/api/load-builder/add-item', {
            method: 'POST', headers: {'Content-Type':'application/json'},
            body: JSON.stringify({ load_id: currentLoadId, item: item })
        });
    } catch(e) { console.error('Failed to persist add-item:', e); }
}

async function removeFromLoad(idx) {
    const item = loadItems[idx];
    loadItems.splice(idx, 1);
    renderAvailable(availableItems);
    renderLoad();
    // Persist
    if (item && currentLoadId) {
        try {
            await fetch('/api/load-builder/remove-item', {
                method: 'POST', headers: {'Content-Type':'application/json'},
                body: JSON.stringify({ load_id: currentLoadId, item_id: item.id || item.item_id || '' })
            });
        } catch(e) { console.error('Failed to persist remove-item:', e); }
    }
}

async function removeFromLoadByItem(item) {
    const idx = loadItems.findIndex(l => l.id === item.id);
    if (idx >= 0) removeFromLoad(idx);
}

function filterAvailable() {
    const search = document.getElementById('itemSearch').value.toLowerCase();
    const filtered = availableItems.filter(i =>
        !search || (i.description||'').toLowerCase().includes(search) || (i.component||'').toLowerCase().includes(search) ||
        (i.job_code||'').toLowerCase().includes(search) || (i.mark||'').toLowerCase().includes(search)
    );
    renderAvailable(filtered);
}

function optimizeLoad() {
    if (!currentLoadId) { alert('Create or select a load first.'); return; }
    const currentLoad = allLoads.find(l => l.load_id === currentLoadId);
    if (currentLoad && currentLoad.status === 'ready') { alert('Cannot modify a finalized load.'); return; }
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
    const items = loadItems.map(i => ({ description: i.description || i.component, quantity: i.quantity || 1, weight: i.weight || 0 }));
    sessionStorage.setItem('bol_items', JSON.stringify(items));
    sessionStorage.setItem('bol_weight', loadItems.reduce((s, i) => s + (i.weight || 0), 0));
    sessionStorage.setItem('bol_load_id', currentLoadId || '');
    window.location.href = '/shipping/bol';
}

// Load management
function createNewLoad() {
    // Populate project dropdown
    const sel = document.getElementById('newLoadProject');
    sel.innerHTML = '<option value="">Select Project</option>';
    projects.forEach(p => {
        const o = document.createElement('option');
        o.value = p.id || p.job_code || '';
        o.textContent = (p.job_code || '') + ' - ' + (p.project_name || p.name || '');
        sel.appendChild(o);
    });
    openModal('createModal');
}

async function submitNewLoad() {
    const jobCode = document.getElementById('newLoadProject').value;
    if (!jobCode) { alert('Please select a project.'); return; }
    try {
        const resp = await fetch('/api/load-builder/create', {
            method: 'POST', headers: {'Content-Type':'application/json'},
            body: JSON.stringify({
                job_code: jobCode,
                truck_number: document.getElementById('newLoadTruck').value,
                driver: document.getElementById('newLoadDriver').value,
                date: new Date().toISOString().split('T')[0]
            })
        });
        const data = await resp.json();
        if (data.ok && data.load) {
            allLoads.push(data.load);
            selectLoad(data.load.load_id);
            renderLoadsStrip();
        }
        closeModal('createModal');
    } catch(e) { alert('Error creating load: ' + e.message); }
}

function selectLoad(loadId) {
    currentLoadId = loadId;
    const load = allLoads.find(l => l.load_id === loadId);
    if (load) {
        loadItems = [...(load.items || [])];
        document.getElementById('loadLabel').textContent = loadId;
    } else {
        loadItems = [];
        document.getElementById('loadLabel').textContent = '';
    }
    renderLoadsStrip();
    renderLoad();
    renderAvailable(availableItems);
}

function renderLoadsStrip() {
    const strip = document.getElementById('loadsStrip');
    let html = '<div class="load-chip" onclick="createNewLoad()" style="border-style:dashed;border-color:var(--tf-gold);text-align:center;display:flex;align-items:center;justify-content:center;">' +
        '<div><h4 style="color:var(--tf-gold);">+ New Load</h4><div class="chip-meta">Create a new load</div></div></div>';

    allLoads.forEach(load => {
        const active = load.load_id === currentLoadId ? ' active' : '';
        const itemCount = (load.items || []).length;
        const totalWt = (load.items || []).reduce((s, i) => s + (i.weight || 0), 0);
        html += '<div class="load-chip' + active + '" onclick="selectLoad(\'' + load.load_id + '\')">' +
            '<h4>' + load.load_id + '</h4>' +
            '<div class="chip-meta">' + (load.job_code || '') + ' | ' + itemCount + ' items | ' + totalWt.toLocaleString() + ' lbs</div>' +
            '<div class="chip-status ' + (load.status || 'building') + '">' + (load.status || 'building') + '</div></div>';
    });
    strip.innerHTML = html;
}

function openFinalizeModal() {
    if (!currentLoadId || !loadItems.length) return;
    document.getElementById('fPieces').textContent = loadItems.length;
    document.getElementById('fWeight').textContent = loadItems.reduce((s, i) => s + (i.weight || 0), 0).toLocaleString() + ' lbs';
    document.getElementById('fLength').textContent = loadItems.reduce((s, i) => s + (i.length || 0), 0) + ' ft';
    openModal('finalizeModal');
}

async function finalizeCurrentLoad() {
    if (!currentLoadId) return;
    try {
        const resp = await fetch('/api/load-builder/finalize', {
            method: 'POST', headers: {'Content-Type':'application/json'},
            body: JSON.stringify({ load_id: currentLoadId })
        });
        const data = await resp.json();
        if (data.ok) {
            const load = allLoads.find(l => l.load_id === currentLoadId);
            if (load) load.status = 'ready';
            renderLoadsStrip();
            renderLoad();
            closeModal('finalizeModal');
        }
    } catch(e) { alert('Error finalizing load: ' + e.message); }
}

async function loadAvailableItems() {
    const project = document.getElementById('projectFilter').value;
    try {
        const url = project ? '/api/shipping/available?project=' + encodeURIComponent(project) : '/api/shipping/available';
        const resp = await fetch(url);
        const data = await resp.json();
        availableItems = Array.isArray(data) ? data : (data.items || []);
        // Add id if missing
        availableItems.forEach((it, i) => { if (!it.id) it.id = 'avail-' + i; });
        renderAvailable(availableItems);
    } catch(e) {
        // Fall back to generating sample items from work orders
        availableItems = [];
        renderAvailable(availableItems);
    }
}

async function loadExistingLoads() {
    try {
        const resp = await fetch('/api/load-builder/loads');
        const data = await resp.json();
        allLoads = data.loads || [];
        renderLoadsStrip();
        // Auto-select first building load
        const building = allLoads.find(l => l.status === 'building');
        if (building) selectLoad(building.load_id);
    } catch(e) { console.error('Failed to load existing loads:', e); }
}

async function loadProjects() {
    try {
        const resp = await fetch('/api/projects/full');
        const data = await resp.json();
        projects = Array.isArray(data) ? data : (data.projects || []);
        const sel = document.getElementById('projectFilter');
        projects.forEach(p => {
            const o = document.createElement('option');
            o.value = p.id || p.job_code || '';
            o.textContent = (p.job_code || '') + ' - ' + (p.project_name || p.name || '');
            sel.appendChild(o);
        });
    } catch(e) {}
}

// Init
loadProjects();
loadAvailableItems();
loadExistingLoads();
</script>
"""
