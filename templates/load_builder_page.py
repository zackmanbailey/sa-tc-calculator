"""
TitanForge v4 — Load Builder Page
===================================
Shipping coordinator workspace: create loads, drag items onto trucks,
set carrier/destination, generate BOL, mark shipped.
"""
from templates.shared_styles import DESIGN_SYSTEM_CSS

LOAD_BUILDER_PAGE_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TitanForge — Load Builder</title>
    <style>
""" + DESIGN_SYSTEM_CSS + r"""
        .container { max-width: 1400px; margin: 0 auto; padding: var(--tf-sp-6) var(--tf-sp-8); }

        /* Two-panel layout */
        .builder-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--tf-sp-6); }
        .panel {
            background: var(--tf-surface); border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-lg); overflow: hidden;
        }
        .panel-header {
            padding: var(--tf-sp-4) var(--tf-sp-5); border-bottom: 1px solid var(--tf-border);
            display: flex; justify-content: space-between; align-items: center;
            background: var(--tf-gray-50);
        }
        .panel-header h3 { font-size: var(--tf-text-md); font-weight: 700; color: var(--tf-gray-900); margin: 0; }
        .panel-body { padding: var(--tf-sp-4); max-height: 600px; overflow-y: auto; }

        /* Item rows */
        .item-row {
            display: flex; align-items: center; gap: 10px; padding: 10px 12px;
            border: 1px solid var(--tf-border); border-radius: var(--tf-radius);
            margin-bottom: 6px; font-size: var(--tf-text-sm); cursor: pointer;
            transition: all 0.15s ease;
        }
        .item-row:hover { background: var(--tf-blue-light); border-color: var(--tf-blue); }
        .item-row.selected { background: var(--tf-blue-light); border-color: var(--tf-blue); }
        .item-row .mark { font-weight: 700; font-family: var(--tf-font-mono); min-width: 60px; }
        .item-row .desc { flex: 1; color: var(--tf-gray-600); }
        .item-row .proj { font-size: 11px; color: var(--tf-gray-400); }

        /* Load card */
        .load-card {
            background: var(--tf-surface); border: 2px solid var(--tf-border);
            border-radius: var(--tf-radius-lg); margin-bottom: var(--tf-sp-4);
            overflow: hidden;
        }
        .load-card.active { border-color: var(--tf-blue); }
        .load-header {
            padding: var(--tf-sp-3) var(--tf-sp-4); background: var(--tf-navy); color: #fff;
            display: flex; justify-content: space-between; align-items: center;
            cursor: pointer;
        }
        .load-header h4 { margin: 0; font-size: var(--tf-text-sm); font-weight: 700; }
        .load-body { padding: var(--tf-sp-4); }
        .load-items { min-height: 40px; }
        .load-item {
            display: flex; align-items: center; gap: 8px; padding: 6px 10px;
            background: var(--tf-gray-50); border-radius: var(--tf-radius);
            margin-bottom: 4px; font-size: var(--tf-text-xs);
        }
        .load-item .mark { font-weight: 700; font-family: var(--tf-font-mono); }
        .load-item .remove { color: var(--tf-danger); cursor: pointer; margin-left: auto; font-weight: 700; }
        .load-item .remove:hover { text-decoration: underline; }

        /* Status badges */
        .status-badge { padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
        .status-badge.building { background: var(--tf-amber-light); color: #92400E; }
        .status-badge.ready { background: var(--tf-blue-light); color: var(--tf-blue); }
        .status-badge.in_transit { background: #E8DEF8; color: #6B21A8; }
        .status-badge.delivered { background: var(--tf-success-bg); color: var(--tf-success); }
        .status-badge.complete { background: var(--tf-success-bg); color: var(--tf-success); }

        /* Load metadata form */
        .load-meta { display: grid; grid-template-columns: 1fr 1fr; gap: var(--tf-sp-3); margin-top: var(--tf-sp-3); }
        .load-meta label { font-size: var(--tf-text-xs); color: var(--tf-gray-500); font-weight: 600; }
        .load-meta input, .load-meta select {
            width: 100%; padding: 6px 10px; border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius); font-size: var(--tf-text-sm);
        }

        /* Stats bar */
        .stats-bar {
            display: flex; gap: var(--tf-sp-4); margin-bottom: var(--tf-sp-5);
            flex-wrap: wrap;
        }
        .stat-chip {
            padding: 8px 16px; border-radius: var(--tf-radius); font-size: var(--tf-text-sm);
            font-weight: 600; background: var(--tf-surface); border: 1px solid var(--tf-border);
        }
        .stat-chip .num { font-size: var(--tf-text-lg); font-weight: 800; color: var(--tf-gray-900); }

        /* Modal */
        .modal-bg {
            display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(15,23,42,0.5); z-index: 300; align-items: center; justify-content: center;
        }
        .modal-bg.open { display: flex; }
        .modal-box {
            background: var(--tf-surface); border-radius: var(--tf-radius-xl);
            width: 500px; max-width: 95vw; box-shadow: var(--tf-shadow-lg);
        }
        .modal-header { padding: var(--tf-sp-5) var(--tf-sp-6); border-bottom: 1px solid var(--tf-border); display: flex; justify-content: space-between; align-items: center; }
        .modal-body { padding: var(--tf-sp-6); }
        .modal-footer { padding: var(--tf-sp-4) var(--tf-sp-6); border-top: 1px solid var(--tf-border); display: flex; justify-content: flex-end; gap: var(--tf-sp-3); }

        .empty-msg { text-align: center; padding: 30px; color: var(--tf-gray-400); font-size: var(--tf-text-sm); }

        @media (max-width: 768px) {
            .builder-grid { grid-template-columns: 1fr; }
            .container { padding: var(--tf-sp-4); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:var(--tf-sp-5);">
            <div>
                <h1 style="font-size:var(--tf-text-2xl);font-weight:700;color:var(--tf-gray-900);">Load Builder</h1>
                <p style="color:var(--tf-gray-500);font-size:var(--tf-text-sm);">Build truck loads from QC-approved items</p>
            </div>
            <div style="display:flex;gap:var(--tf-sp-3);">
                <a href="/shipping" class="btn btn-outline">Shipping Dashboard</a>
                <button class="btn btn-primary" onclick="openNewLoad()">+ New Load</button>
            </div>
        </div>

        <!-- Stats -->
        <div class="stats-bar">
            <div class="stat-chip"><span class="num" id="statAvailable">0</span> Items Available</div>
            <div class="stat-chip"><span class="num" id="statBuilding">0</span> Loads Building</div>
            <div class="stat-chip"><span class="num" id="statReady">0</span> Ready to Ship</div>
        </div>

        <!-- Two-panel builder -->
        <div class="builder-grid">
            <!-- LEFT: Available items -->
            <div class="panel">
                <div class="panel-header">
                    <h3>Available Items</h3>
                    <div style="display:flex;gap:8px;">
                        <select id="filterProject" onchange="loadShippableItems()" style="padding:4px 8px;border:1px solid var(--tf-border);border-radius:var(--tf-radius);font-size:var(--tf-text-xs);">
                            <option value="">All Projects</option>
                        </select>
                        <button class="btn btn-outline btn-sm" onclick="addSelectedToLoad()" id="btnAddSelected" disabled>Add Selected &rarr;</button>
                    </div>
                </div>
                <div class="panel-body" id="availableItems">
                    <div class="empty-msg">Loading available items...</div>
                </div>
            </div>

            <!-- RIGHT: Active loads -->
            <div class="panel">
                <div class="panel-header">
                    <h3>Active Loads</h3>
                    <button class="btn btn-outline btn-sm" onclick="refreshLoads()">&#8635;</button>
                </div>
                <div class="panel-body" id="activeLoads">
                    <div class="empty-msg">No active loads. Create one to start.</div>
                </div>
            </div>
        </div>
    </div>

    <!-- NEW LOAD MODAL -->
    <div class="modal-bg" id="newLoadModal">
        <div class="modal-box">
            <div class="modal-header">
                <h2 style="font-size:var(--tf-text-xl);font-weight:700;">New Shipping Load</h2>
                <button onclick="closeModal('newLoadModal')" style="background:none;border:none;font-size:1.5rem;cursor:pointer;color:var(--tf-gray-400);">&times;</button>
            </div>
            <div class="modal-body">
                <div style="margin-bottom:var(--tf-sp-4);">
                    <label class="form-label">Project *</label>
                    <select class="form-input" id="newLoadProject"></select>
                </div>
                <div style="margin-bottom:var(--tf-sp-4);">
                    <label class="form-label">Destination Address</label>
                    <input type="text" class="form-input" id="newLoadDest" placeholder="Job site address">
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:var(--tf-sp-3);margin-bottom:var(--tf-sp-4);">
                    <div><label class="form-label">Carrier</label><input type="text" class="form-input" id="newLoadCarrier" placeholder="Trucking company or Self"></div>
                    <div><label class="form-label">Trailer Type</label>
                        <select class="form-input" id="newLoadTrailer">
                            <option value="flatbed">Flatbed</option>
                            <option value="step_deck">Step Deck</option>
                            <option value="lowboy">Lowboy</option>
                            <option value="van">Enclosed Van</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                </div>
                <div><label class="form-label">Special Instructions</label><textarea class="form-input" id="newLoadInstr" rows="2" placeholder="Crane needed, unload from rear, etc."></textarea></div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-outline" onclick="closeModal('newLoadModal')">Cancel</button>
                <button class="btn btn-primary" onclick="createLoad()">Create Load</button>
            </div>
        </div>
    </div>

<script>
let shippableItems = [];
let selectedItems = new Set();
let activeLoads = [];
let activeLoadId = null;

document.addEventListener('DOMContentLoaded', () => {
    loadShippableItems();
    refreshLoads();
});

async function loadShippableItems() {
    const proj = document.getElementById('filterProject').value;
    const url = '/api/shipping/shippable-items' + (proj ? '?job_code=' + encodeURIComponent(proj) : '');
    const r = await fetch(url);
    const d = await r.json();
    if (d.ok) {
        shippableItems = d.items;
        document.getElementById('statAvailable').textContent = d.total;
        buildProjectFilter();
        renderAvailable();
    }
}

function buildProjectFilter() {
    const projects = [...new Set(shippableItems.map(i => i.job_code))].sort();
    const sel = document.getElementById('filterProject');
    const cur = sel.value;
    const projSel = document.getElementById('newLoadProject');
    sel.innerHTML = '<option value="">All Projects</option>' +
        projects.map(p => `<option value="${p}" ${p===cur?'selected':''}>${p}</option>`).join('');
    projSel.innerHTML = projects.map(p => `<option value="${p}">${p}</option>`).join('');
}

function renderAvailable() {
    const container = document.getElementById('availableItems');
    if (!shippableItems.length) {
        container.innerHTML = '<div class="empty-msg">No items ready for shipping. Items must pass QC first.</div>';
        return;
    }
    container.innerHTML = shippableItems.map(i => `
        <div class="item-row ${selectedItems.has(i.item_id)?'selected':''}"
             onclick="toggleSelect('${i.item_id}')">
            <input type="checkbox" ${selectedItems.has(i.item_id)?'checked':''} onclick="event.stopPropagation();toggleSelect('${i.item_id}')">
            <span class="mark">${i.ship_mark}</span>
            <span class="desc">${i.description||'—'}</span>
            <span class="proj">${i.job_code}</span>
        </div>`).join('');
}

function toggleSelect(itemId) {
    if (selectedItems.has(itemId)) selectedItems.delete(itemId);
    else selectedItems.add(itemId);
    renderAvailable();
    document.getElementById('btnAddSelected').disabled = selectedItems.size === 0 || !activeLoadId;
}

async function refreshLoads() {
    const r = await fetch('/api/shipping/loads?status=building');
    const d = await r.json();
    const r2 = await fetch('/api/shipping/loads?status=ready');
    const d2 = await r2.json();
    activeLoads = [...(d.ok ? d.loads : []), ...(d2.ok ? d2.loads : [])];
    document.getElementById('statBuilding').textContent = (d.ok ? d.loads : []).length;
    document.getElementById('statReady').textContent = (d2.ok ? d2.loads : []).length;
    renderLoads();
}

function renderLoads() {
    const container = document.getElementById('activeLoads');
    if (!activeLoads.length) {
        container.innerHTML = '<div class="empty-msg">No active loads. Click "+ New Load" to create one.</div>';
        return;
    }
    container.innerHTML = activeLoads.map(load => {
        const isActive = load.load_id === activeLoadId;
        return `<div class="load-card ${isActive?'active':''}" id="load-${load.load_id}">
            <div class="load-header" onclick="selectLoad('${load.load_id}')">
                <h4>${load.load_id} &middot; ${load.job_code}</h4>
                <span class="status-badge ${load.status}">${load.status.replace('_',' ')}</span>
            </div>
            <div class="load-body" ${isActive?'':'style="display:none;"'}>
                <div style="font-size:var(--tf-text-xs);color:var(--tf-gray-500);margin-bottom:8px;">
                    ${load.destination||'No destination set'} &middot; ${load.carrier||'No carrier'} &middot;
                    <strong>${(load.items||[]).length}</strong> items
                </div>
                <div class="load-items">
                    ${(load.items||[]).length ? (load.items||[]).map(li => `
                        <div class="load-item">
                            <span class="mark">${li.ship_mark}</span>
                            <span>${li.description||''}</span>
                            <span style="color:var(--tf-gray-400);">${li.job_code}</span>
                            ${load.status==='building' ? `<span class="remove" onclick="removeFromLoad('${load.load_id}','${li.item_id}')">&times;</span>` : ''}
                        </div>`).join('') : '<div style="color:var(--tf-gray-300);font-size:var(--tf-text-xs);padding:8px;">Empty — add items from the left panel</div>'}
                </div>
                <div style="display:flex;gap:6px;margin-top:8px;flex-wrap:wrap;">
                    ${load.status==='building' ? `
                        <button class="btn btn-sm btn-primary" onclick="transitionLoad('${load.load_id}','ready')">Mark Ready</button>
                        <button class="btn btn-sm btn-outline" onclick="genBOL('${load.load_id}')">Generate BOL</button>
                    ` : ''}
                    ${load.status==='ready' ? `
                        <button class="btn btn-sm btn-primary" style="background:#7C3AED;" onclick="transitionLoad('${load.load_id}','in_transit')">Ship It</button>
                    ` : ''}
                    ${load.bol_number ? `<span style="font-size:11px;color:var(--tf-gray-500);">BOL: ${load.bol_number}</span>` : ''}
                </div>
            </div>
        </div>`;
    }).join('');
}

function selectLoad(loadId) {
    activeLoadId = (activeLoadId === loadId) ? null : loadId;
    document.getElementById('btnAddSelected').disabled = selectedItems.size === 0 || !activeLoadId;
    renderLoads();
}

async function addSelectedToLoad() {
    if (!activeLoadId || selectedItems.size === 0) return;
    const items = [...selectedItems].map(itemId => {
        const si = shippableItems.find(i => i.item_id === itemId);
        return { job_code: si?.job_code || '', item_id: itemId };
    });
    const r = await fetch('/api/shipping/add-items', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ load_id: activeLoadId, items }),
    });
    const d = await r.json();
    if (d.ok) {
        selectedItems.clear();
        loadShippableItems();
        refreshLoads();
        showToast(`Added ${d.added} items to load`, 'success');
        if (d.errors?.length) showToast(d.errors.join(', '), 'error');
    } else alert(d.error);
}

async function removeFromLoad(loadId, itemId) {
    const r = await fetch('/api/shipping/remove-item', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ load_id: loadId, item_id: itemId }),
    });
    const d = await r.json();
    if (d.ok) { refreshLoads(); loadShippableItems(); }
    else alert(d.error);
}

async function transitionLoad(loadId, newStatus) {
    const msg = newStatus === 'in_transit' ? 'Ship this load? All items will be marked as shipped.' :
                newStatus === 'ready' ? 'Mark this load as ready to ship?' : 'Proceed?';
    if (!confirm(msg)) return;
    const r = await fetch('/api/shipping/transition', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ load_id: loadId, new_status: newStatus }),
    });
    const d = await r.json();
    if (d.ok) {
        refreshLoads();
        loadShippableItems();
        showToast(`Load ${loadId}: ${newStatus.replace('_',' ')}`, 'success');
    } else alert(d.error);
}

async function genBOL(loadId) {
    const r = await fetch('/api/shipping/bol', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ load_id: loadId }),
    });
    const d = await r.json();
    if (d.ok) { refreshLoads(); showToast('BOL generated: ' + d.bol_number, 'success'); }
    else alert(d.error);
}

function openNewLoad() { document.getElementById('newLoadModal').classList.add('open'); }
function closeModal(id) { document.getElementById(id).classList.remove('open'); }

async function createLoad() {
    const proj = document.getElementById('newLoadProject').value;
    if (!proj) { alert('Select a project'); return; }
    const r = await fetch('/api/shipping/create', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            job_code: proj,
            destination: document.getElementById('newLoadDest').value,
            carrier: document.getElementById('newLoadCarrier').value,
            special_instructions: document.getElementById('newLoadInstr').value,
        }),
    });
    const d = await r.json();
    if (d.ok) {
        closeModal('newLoadModal');
        activeLoadId = d.load.load_id;
        refreshLoads();
        showToast('Load created: ' + d.load.load_id, 'success');
    } else alert(d.error);
}

function showToast(msg, type) {
    const t = document.createElement('div');
    t.style.cssText = `position:fixed;top:20px;right:20px;padding:12px 20px;border-radius:8px;font-size:14px;font-weight:600;z-index:500;color:#fff;
        background:${type==='success'?'var(--tf-success)':'var(--tf-danger)'};box-shadow:var(--tf-shadow-lg);`;
    t.innerHTML = msg;
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 3000);
}

document.addEventListener('keydown', e => { if (e.key === 'Escape') { document.querySelectorAll('.modal-bg.open').forEach(m => m.classList.remove('open')); }});
</script>
</body>
</html>
"""
