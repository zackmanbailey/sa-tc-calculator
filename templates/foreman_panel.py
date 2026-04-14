"""
TitanForge — Foreman Assignment Panel Template
================================================
Allows Shop Foreman to:
  - View all unassigned items across projects
  - Assign items to operators/welders
  - Reprioritize queue items (drag or number entry)
  - See machine utilization at a glance
  - Bulk assign multiple items

Reference: RULES.md §3 (Shop Foreman role), §5 (Work Order Item Lifecycle)
"""

FOREMAN_PANEL_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TitanForge — Assignment Panel</title>
<style>
:root {
    --tf-navy: #1a1f36;
    --tf-blue: #2563eb;
    --tf-orange: #f97316;
    --tf-green: #22c55e;
    --tf-red: #ef4444;
    --tf-yellow: #eab308;
    --tf-gray-100: #f3f4f6;
    --tf-gray-200: #e5e7eb;
    --tf-gray-300: #d1d5db;
    --tf-gray-400: #9ca3af;
    --tf-gray-600: #4b5563;
    --tf-gray-800: #1f2937;
    --radius: 8px;
    --shadow: 0 1px 3px rgba(0,0,0,0.12);
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
       background: var(--tf-gray-100); color: var(--tf-gray-800); }

.fp-header {
    background: var(--tf-navy); color: #fff; padding: 16px 24px;
    display: flex; align-items: center; justify-content: space-between;
}
.fp-header h1 { font-size: 1.3rem; font-weight: 600; }
.fp-header .fp-user { font-size: 0.85rem; opacity: 0.7; }

.fp-grid {
    display: grid; grid-template-columns: 1fr 1fr; gap: 16px;
    padding: 16px 24px; max-width: 1400px; margin: 0 auto;
}
@media (max-width: 900px) { .fp-grid { grid-template-columns: 1fr; } }

.fp-card {
    background: #fff; border-radius: var(--radius); box-shadow: var(--shadow);
    overflow: hidden;
}
.fp-card-header {
    padding: 12px 16px; border-bottom: 1px solid var(--tf-gray-200);
    display: flex; align-items: center; justify-content: space-between;
    font-weight: 600; font-size: 0.95rem;
}
.fp-card-body { padding: 12px 16px; }

/* Machine status grid */
.fp-machines {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 10px;
}
.fp-machine {
    border: 1px solid var(--tf-gray-200); border-radius: 6px;
    padding: 10px; text-align: center; cursor: pointer; transition: all 0.15s;
}
.fp-machine:hover { border-color: var(--tf-blue); background: #f0f4ff; }
.fp-machine .name { font-weight: 600; font-size: 0.8rem; margin-bottom: 4px; }
.fp-machine .count { font-size: 1.4rem; font-weight: 700; }
.fp-machine .label { font-size: 0.7rem; color: var(--tf-gray-400); }
.fp-machine.active { border-color: var(--tf-orange); background: #fff7ed; }

/* Unassigned items table */
.fp-table {
    width: 100%; border-collapse: collapse; font-size: 0.85rem;
}
.fp-table th {
    text-align: left; padding: 8px 10px; background: var(--tf-gray-100);
    border-bottom: 2px solid var(--tf-gray-200); font-weight: 600;
    font-size: 0.75rem; text-transform: uppercase; color: var(--tf-gray-600);
}
.fp-table td {
    padding: 8px 10px; border-bottom: 1px solid var(--tf-gray-200);
    vertical-align: middle;
}
.fp-table tr:hover { background: #f8faff; }
.fp-table .status-badge {
    display: inline-block; padding: 2px 8px; border-radius: 12px;
    font-size: 0.72rem; font-weight: 600;
}
.fp-table .status-badge.gray { background: #f3f4f6; color: #6b7280; }
.fp-table .status-badge.blue { background: #dbeafe; color: #1d4ed8; }
.fp-table .status-badge.cyan { background: #cffafe; color: #0891b2; }
.fp-table .status-badge.orange { background: #ffedd5; color: #c2410c; }
.fp-table .status-badge.green { background: #dcfce7; color: #15803d; }
.fp-table .status-badge.red { background: #fee2e2; color: #b91c1c; }
.fp-table .status-badge.yellow { background: #fef9c3; color: #a16207; }
.fp-table .status-badge.purple { background: #f3e8ff; color: #7c3aed; }

/* Assign button */
.fp-assign-btn {
    padding: 4px 12px; border-radius: 4px; border: 1px solid var(--tf-blue);
    background: var(--tf-blue); color: #fff; font-size: 0.78rem;
    cursor: pointer; transition: all 0.15s;
}
.fp-assign-btn:hover { background: #1d4ed8; }
.fp-assign-btn.bulk {
    background: var(--tf-orange); border-color: var(--tf-orange);
    padding: 8px 20px; font-size: 0.85rem;
}

/* Operator selector */
select.fp-select {
    padding: 4px 8px; border-radius: 4px; border: 1px solid var(--tf-gray-300);
    font-size: 0.8rem; min-width: 120px;
}

/* Priority input */
input.fp-priority {
    width: 50px; padding: 4px; border: 1px solid var(--tf-gray-300);
    border-radius: 4px; text-align: center; font-size: 0.8rem;
}

/* Attention items */
.fp-attention {
    background: #fef3c7; border-left: 3px solid var(--tf-yellow);
    padding: 10px 14px; border-radius: 0 6px 6px 0; margin-bottom: 8px;
}
.fp-attention .title { font-weight: 600; font-size: 0.85rem; }
.fp-attention .detail { font-size: 0.78rem; color: var(--tf-gray-600); margin-top: 2px; }

.fp-empty { padding: 24px; text-align: center; color: var(--tf-gray-400); font-size: 0.9rem; }

/* Full-width section */
.fp-full { grid-column: 1 / -1; }

.fp-loader { text-align: center; padding: 40px; color: var(--tf-gray-400); }
</style>
</head>
<body>

<div class="fp-header">
    <h1>&#9881; Assignment Panel</h1>
    <div class="fp-user">{{DISPLAY_NAME}} — Shop Foreman</div>
</div>

<div class="fp-grid">
    <!-- Machine Utilization -->
    <div class="fp-card">
        <div class="fp-card-header">
            <span>&#128190; Machine Status</span>
            <span id="machineCount" style="font-size:0.8rem; color:var(--tf-gray-400);"></span>
        </div>
        <div class="fp-card-body">
            <div class="fp-machines" id="machineGrid">
                <div class="fp-loader">Loading machines...</div>
            </div>
        </div>
    </div>

    <!-- Items Needing Attention -->
    <div class="fp-card">
        <div class="fp-card-header">
            <span>&#9888; Needs Attention</span>
            <span id="attentionCount" style="font-size:0.8rem; color:var(--tf-red);">0</span>
        </div>
        <div class="fp-card-body" id="attentionList">
            <div class="fp-loader">Loading...</div>
        </div>
    </div>

    <!-- Unassigned Items (full width) -->
    <div class="fp-card fp-full">
        <div class="fp-card-header">
            <span>&#128203; Unassigned Items</span>
            <div>
                <select id="machineFilter" class="fp-select" onchange="filterItems()">
                    <option value="">All Machines</option>
                </select>
                <button class="fp-assign-btn bulk" onclick="bulkAssign()">Bulk Assign Selected</button>
            </div>
        </div>
        <div class="fp-card-body" style="max-height:500px; overflow-y:auto;">
            <table class="fp-table">
                <thead>
                    <tr>
                        <th><input type="checkbox" id="selectAll" onchange="toggleSelectAll()"></th>
                        <th>Mark</th>
                        <th>Type</th>
                        <th>Description</th>
                        <th>Job</th>
                        <th>Machine</th>
                        <th>Status</th>
                        <th>Priority</th>
                        <th>Assign To</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody id="unassignedBody">
                    <tr><td colspan="10" class="fp-empty">Loading items...</td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <!-- Active Assignments (full width) -->
    <div class="fp-card fp-full">
        <div class="fp-card-header">
            <span>&#128100; Current Assignments</span>
            <span id="assignedCount" style="font-size:0.8rem; color:var(--tf-gray-400);">0</span>
        </div>
        <div class="fp-card-body" style="max-height:400px; overflow-y:auto;">
            <table class="fp-table">
                <thead>
                    <tr>
                        <th>Mark</th>
                        <th>Type</th>
                        <th>Job</th>
                        <th>Machine</th>
                        <th>Assigned To</th>
                        <th>Priority</th>
                        <th>Status</th>
                        <th>Started</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="assignedBody">
                    <tr><td colspan="9" class="fp-empty">Loading...</td></tr>
                </tbody>
            </table>
        </div>
    </div>
</div>

<script>
const USERNAME = "{{USERNAME}}";
let allItems = [];
let operators = [];
let machineData = {};
let statusConfig = {};

// ── Init ──────────────────────────────────
async function init() {
    // Load status config
    try {
        const cfgRes = await fetch('/api/work-orders/status-config');
        statusConfig = await cfgRes.json();
    } catch(e) { console.error('Status config failed', e); }

    await Promise.all([loadShopFloor(), loadAllItems()]);
}

async function loadShopFloor() {
    try {
        const res = await fetch('/api/shop-floor/summary');
        const data = await res.json();
        if (!data.ok) return;

        machineData = data.machines || {};
        renderMachines(machineData);

        // Populate machine filter
        const filter = document.getElementById('machineFilter');
        Object.entries(machineData).forEach(([id, info]) => {
            const opt = document.createElement('option');
            opt.value = id;
            opt.textContent = info.label || id;
            filter.appendChild(opt);
        });

        // Attention items
        const attn = data.needs_attention || [];
        document.getElementById('attentionCount').textContent = attn.length;
        renderAttention(attn);
    } catch(e) {
        console.error('Shop floor load failed', e);
    }
}

async function loadAllItems() {
    try {
        const res = await fetch('/api/shop-floor/data');
        const data = await res.json();
        if (!data.ok) return;

        // Build operator list from active_items assigned_to fields
        const ops = new Set();
        // Also get from machines active items
        if (data.machines) {
            Object.values(data.machines).forEach(m => {
                (m.active_items || []).forEach(i => { if(i.started_by) ops.add(i.started_by); });
            });
        }

        // Get all items from all active work orders
        allItems = [];
        const wos = data.active_wos || [];
        for (const woSum of wos) {
            try {
                const detRes = await fetch(`/api/work-orders/detail?job_code=${encodeURIComponent(woSum.job_code)}&wo_id=${encodeURIComponent(woSum.work_order_id)}`);
                const detData = await detRes.json();
                if (detData.ok && detData.work_order) {
                    (detData.work_order.items || []).forEach(item => {
                        item._job_code = woSum.job_code;
                        item._wo_id = woSum.work_order_id;
                        allItems.push(item);
                        if (item.assigned_to) ops.add(item.assigned_to);
                        if (item.started_by) ops.add(item.started_by);
                    });
                }
            } catch(e) { /* skip */ }
        }

        operators = [...ops].sort();
        renderUnassigned();
        renderAssigned();
    } catch(e) {
        console.error('All items load failed', e);
    }
}

// ── Render Machines ──────────────────────
function renderMachines(machines) {
    const grid = document.getElementById('machineGrid');
    const entries = Object.entries(machines);
    document.getElementById('machineCount').textContent = entries.length + ' machines';
    grid.innerHTML = entries.map(([id, info]) => {
        const isActive = info.active > 0;
        return `<div class="fp-machine ${isActive ? 'active' : ''}" onclick="filterByMachine('${id}')">
            <div class="name">${info.label || id}</div>
            <div class="count">${info.active}</div>
            <div class="label">active / ${info.queued} queued</div>
        </div>`;
    }).join('');
}

// ── Render Attention ─────────────────────
function renderAttention(items) {
    const el = document.getElementById('attentionList');
    if (!items.length) {
        el.innerHTML = '<div class="fp-empty">All clear — no items need attention</div>';
        return;
    }
    el.innerHTML = items.slice(0, 10).map(i => `
        <div class="fp-attention">
            <div class="title">${i.ship_mark} — ${i.component_type} (${i.job_code})</div>
            <div class="detail">Status: ${statusLabel(i.status)} | Machine: ${i.machine}
                ${i.qc_notes ? ' | QC: ' + i.qc_notes : ''}</div>
        </div>
    `).join('');
}

// ── Render Unassigned ────────────────────
function renderUnassigned() {
    const filter = document.getElementById('machineFilter').value;
    const unassigned = allItems.filter(i => {
        const assignable = ['stickers_printed', 'staged', 'qc_rejected', 'approved'];
        if (!assignable.includes(i.status)) return false;
        if (i.assigned_to) return false;
        if (filter && i.machine !== filter) return false;
        return true;
    });

    const body = document.getElementById('unassignedBody');
    if (!unassigned.length) {
        body.innerHTML = '<tr><td colspan="10" class="fp-empty">No unassigned items</td></tr>';
        return;
    }

    body.innerHTML = unassigned.map(i => `
        <tr data-item='${JSON.stringify({job_code: i._job_code, item_id: i.item_id})}'>
            <td><input type="checkbox" class="item-check" value="${i.item_id}"></td>
            <td><strong>${i.ship_mark}</strong></td>
            <td>${i.component_type}</td>
            <td style="max-width:200px; overflow:hidden; text-overflow:ellipsis;">${i.description}</td>
            <td>${i._job_code}</td>
            <td>${i.machine}</td>
            <td><span class="status-badge ${statusColor(i.status)}">${statusLabel(i.status)}</span></td>
            <td><input class="fp-priority" type="number" value="${i.priority || 50}" min="1" max="99"></td>
            <td><select class="fp-select operator-select">
                <option value="">Select...</option>
                ${operators.map(o => `<option value="${o}">${o}</option>`).join('')}
            </select></td>
            <td><button class="fp-assign-btn" onclick="assignItem(this)">Assign</button></td>
        </tr>
    `).join('');
}

// ── Render Assigned ──────────────────────
function renderAssigned() {
    const assigned = allItems.filter(i => i.assigned_to &&
        ['stickers_printed', 'staged', 'in_progress', 'qc_rejected', 'approved'].includes(i.status));

    document.getElementById('assignedCount').textContent = assigned.length;
    const body = document.getElementById('assignedBody');
    if (!assigned.length) {
        body.innerHTML = '<tr><td colspan="9" class="fp-empty">No active assignments</td></tr>';
        return;
    }

    body.innerHTML = assigned.map(i => `
        <tr>
            <td><strong>${i.ship_mark}</strong></td>
            <td>${i.component_type}</td>
            <td>${i._job_code}</td>
            <td>${i.machine}</td>
            <td>${i.assigned_to}</td>
            <td>${i.priority || 50}</td>
            <td><span class="status-badge ${statusColor(i.status)}">${statusLabel(i.status)}</span></td>
            <td>${i.started_at ? new Date(i.started_at).toLocaleTimeString() : '—'}</td>
            <td>
                <select class="fp-select" onchange="reassignItem('${i._job_code}','${i.item_id}',this.value)">
                    <option value="${i.assigned_to}">${i.assigned_to}</option>
                    ${operators.filter(o=>o!==i.assigned_to).map(o => `<option value="${o}">${o}</option>`).join('')}
                </select>
            </td>
        </tr>
    `).join('');
}

// ── Actions ──────────────────────────────
async function assignItem(btn) {
    const row = btn.closest('tr');
    const data = JSON.parse(row.dataset.item);
    const operator = row.querySelector('.operator-select').value;
    const priority = parseInt(row.querySelector('.fp-priority').value) || 50;
    if (!operator) { alert('Select an operator'); return; }

    const res = await fetch('/api/work-orders/assign', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({...data, assigned_to: operator, priority})
    });
    const result = await res.json();
    if (result.ok) {
        btn.textContent = '✓';
        btn.disabled = true;
        setTimeout(() => loadAllItems(), 500);
    } else {
        alert(result.error || 'Assignment failed');
    }
}

async function reassignItem(jobCode, itemId, newOp) {
    if (!newOp) return;
    const res = await fetch('/api/work-orders/reassign', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({job_code: jobCode, item_id: itemId, new_operator: newOp})
    });
    const result = await res.json();
    if (!result.ok) alert(result.error || 'Reassignment failed');
}

async function bulkAssign() {
    const checked = document.querySelectorAll('.item-check:checked');
    if (!checked.length) { alert('Select items first'); return; }

    const operator = prompt('Assign all selected items to which operator?\\n(' + operators.join(', ') + ')');
    if (!operator) return;

    const assignments = [];
    checked.forEach(cb => {
        const row = cb.closest('tr');
        const data = JSON.parse(row.dataset.item);
        const priority = parseInt(row.querySelector('.fp-priority').value) || 50;
        assignments.push({...data, assigned_to: operator, priority});
    });

    const res = await fetch('/api/work-orders/bulk-assign', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({assignments})
    });
    const result = await res.json();
    alert(`Assigned ${result.success || 0} of ${result.total || 0} items`);
    loadAllItems();
}

function toggleSelectAll() {
    const checked = document.getElementById('selectAll').checked;
    document.querySelectorAll('.item-check').forEach(cb => cb.checked = checked);
}

function filterItems() { renderUnassigned(); }
function filterByMachine(id) {
    document.getElementById('machineFilter').value = id;
    renderUnassigned();
}

// ── Helpers ──────────────────────────────
function statusLabel(s) {
    return (statusConfig.labels || {})[s] || s.replace(/_/g, ' ');
}
function statusColor(s) {
    return (statusConfig.colors || {})[s] || 'gray';
}

// ── Boot ─────────────────────────────────
document.addEventListener('DOMContentLoaded', init);
</script>
</body>
</html>
"""
