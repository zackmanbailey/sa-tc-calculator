"""
TitanForge v4 — QC Inspection Queue
=====================================
Inspector workspace: see all WO items needing QC across all projects.
Sign off (approve/reject) with AISC checklist, auto-create NCRs on failure.
"""
from templates.shared_styles import DESIGN_SYSTEM_CSS

QC_QUEUE_PAGE_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TitanForge — QC Inspection Queue</title>
    <style>
""" + DESIGN_SYSTEM_CSS + r"""

        .container { max-width: 1400px; margin: 0 auto; padding: var(--tf-sp-6) var(--tf-sp-8); }

        /* Stats bar */
        .qc-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--tf-sp-4); margin-bottom: var(--tf-sp-6); }
        .qc-stat {
            background: var(--tf-surface); border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-lg); padding: var(--tf-sp-4) var(--tf-sp-5);
            display: flex; align-items: center; gap: var(--tf-sp-4);
        }
        .qc-stat-icon { font-size: 1.5rem; width: 44px; height: 44px; border-radius: 10px; display: flex; align-items: center; justify-content: center; }
        .qc-stat-icon.pending { background: var(--tf-amber-light); }
        .qc-stat-icon.approved { background: var(--tf-success-bg); }
        .qc-stat-icon.rejected { background: var(--tf-danger-bg); }
        .qc-stat-icon.total { background: var(--tf-blue-light); }
        .qc-stat-value { font-size: var(--tf-text-2xl); font-weight: 800; color: var(--tf-gray-900); }
        .qc-stat-label { font-size: var(--tf-text-xs); color: var(--tf-gray-500); text-transform: uppercase; letter-spacing: 0.04em; }
        .qc-stat { cursor: pointer; transition: transform 0.15s, box-shadow 0.15s; }
        .qc-stat:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }

        /* Filter bar */
        .filter-bar {
            display: flex; gap: var(--tf-sp-3); align-items: center;
            margin-bottom: var(--tf-sp-5); flex-wrap: wrap;
        }
        .filter-bar select, .filter-bar input {
            padding: 8px 14px; border: 1px solid var(--tf-border); border-radius: var(--tf-radius);
            font-size: var(--tf-text-sm); background: var(--tf-surface);
        }

        /* Queue table */
        .queue-table { width: 100%; border-collapse: collapse; font-size: var(--tf-text-sm); }
        .queue-table th {
            background: var(--tf-navy); color: #fff; padding: 12px 14px;
            text-align: left; font-size: var(--tf-text-xs); text-transform: uppercase;
            letter-spacing: 0.04em; font-weight: 700; position: sticky; top: 0;
        }
        .queue-table td { padding: 12px 14px; border-bottom: 1px solid var(--tf-border); vertical-align: middle; }
        .queue-table tr:hover td { background: var(--tf-blue-light); }
        .queue-table tr.urgent td { background: #FFF7ED; }

        /* Status badges */
        .status-badge { padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 700; text-transform: uppercase; white-space: nowrap; }
        .status-badge.fabricated { background: #D1FAE5; color: #065F46; }
        .status-badge.qc_pending { background: var(--tf-amber-light); color: #92400E; }

        /* Priority dot */
        .priority-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
        .priority-dot.urgent { background: var(--tf-danger); }
        .priority-dot.normal { background: var(--tf-success); }
        .priority-dot.low { background: var(--tf-gray-300); }

        /* Action buttons */
        .btn-approve { background: var(--tf-success); color: #fff; border: none; padding: 6px 14px; border-radius: var(--tf-radius); font-size: var(--tf-text-xs); font-weight: 700; cursor: pointer; }
        .btn-approve:hover { opacity: 0.9; }
        .btn-reject { background: var(--tf-danger); color: #fff; border: none; padding: 6px 14px; border-radius: var(--tf-radius); font-size: var(--tf-text-xs); font-weight: 700; cursor: pointer; }
        .btn-reject:hover { opacity: 0.9; }
        .btn-inspect { background: var(--tf-blue); color: #fff; border: none; padding: 6px 14px; border-radius: var(--tf-radius); font-size: var(--tf-text-xs); font-weight: 700; cursor: pointer; }
        .btn-inspect:hover { opacity: 0.9; }

        /* Sign-off modal */
        .modal-bg {
            display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(15,23,42,0.5); z-index: 300; align-items: center; justify-content: center;
        }
        .modal-bg.open { display: flex; }
        .modal-box {
            background: var(--tf-surface); border-radius: var(--tf-radius-xl);
            width: 720px; max-width: 95vw; max-height: 90vh; overflow-y: auto;
            box-shadow: var(--tf-shadow-lg);
        }
        .modal-header {
            padding: var(--tf-sp-5) var(--tf-sp-6); border-bottom: 1px solid var(--tf-border);
            display: flex; justify-content: space-between; align-items: center;
        }
        .modal-body { padding: var(--tf-sp-6); }
        .modal-footer {
            padding: var(--tf-sp-4) var(--tf-sp-6); border-top: 1px solid var(--tf-border);
            display: flex; justify-content: flex-end; gap: var(--tf-sp-3);
        }

        /* Checklist in modal */
        .checklist-grid { display: grid; gap: 6px; margin: var(--tf-sp-4) 0; }
        .check-item {
            display: flex; align-items: center; gap: 10px; padding: 8px 12px;
            border: 1px solid var(--tf-border); border-radius: var(--tf-radius); font-size: var(--tf-text-sm);
            background: var(--tf-surface);
        }
        .check-item.checked { background: var(--tf-success-bg); border-color: var(--tf-success); }
        .check-item label { flex: 1; cursor: pointer; }
        .check-item input[type="checkbox"] { width: 18px; height: 18px; cursor: pointer; accent-color: var(--tf-success); }
        .check-item select, .check-item input[type="text"] {
            padding: 4px 8px; border: 1px solid var(--tf-border); border-radius: 4px;
            font-size: var(--tf-text-xs); max-width: 200px;
        }

        /* Empty state */
        .empty-state { text-align: center; padding: 80px 20px; color: var(--tf-gray-400); }
        .empty-state .icon { font-size: 3rem; margin-bottom: 12px; }

        /* Item history panel */
        .history-panel { background: var(--tf-gray-50); border-radius: var(--tf-radius); padding: var(--tf-sp-4); margin-top: var(--tf-sp-4); }
        .history-item { padding: 6px 0; border-bottom: 1px solid var(--tf-border); font-size: var(--tf-text-xs); color: var(--tf-gray-600); }
        .history-item:last-child { border-bottom: none; }

        @media (max-width: 768px) {
            .qc-stats { grid-template-columns: repeat(2, 1fr); }
            .container { padding: var(--tf-sp-4); }
            .queue-table { font-size: var(--tf-text-xs); }
            .queue-table td, .queue-table th { padding: 8px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:var(--tf-sp-5);">
            <div>
                <h1 style="font-size:var(--tf-text-2xl);font-weight:700;color:var(--tf-gray-900);">
                    QC Inspection Queue
                </h1>
                <p style="color:var(--tf-gray-500);font-size:var(--tf-text-sm);">Items awaiting quality control inspection</p>
            </div>
            <div style="display:flex;gap:var(--tf-sp-3);">
                <a href="/qc-dashboard" class="btn btn-outline">QC Dashboard</a>
                <button class="btn btn-outline" onclick="refreshQueue()" title="Refresh">&#8635; Refresh</button>
            </div>
        </div>

        <!-- Stats -->
        <div class="qc-stats">
            <div class="qc-stat" onclick="document.getElementById('filterStatus').value='fabricated';applyFilters();">
                <div class="qc-stat-icon pending">&#9888;</div>
                <div><div class="qc-stat-value" id="statPending">0</div><div class="qc-stat-label">Awaiting QC</div></div>
            </div>
            <div class="qc-stat" onclick="document.getElementById('filterStatus').value='';applyFilters();">
                <div class="qc-stat-icon approved">&#10003;</div>
                <div><div class="qc-stat-value" id="statApprovedToday">0</div><div class="qc-stat-label">Approved Today</div></div>
            </div>
            <div class="qc-stat" onclick="document.getElementById('filterStatus').value='';applyFilters();">
                <div class="qc-stat-icon rejected">&#10007;</div>
                <div><div class="qc-stat-value" id="statRejectedToday">0</div><div class="qc-stat-label">Rejected Today</div></div>
            </div>
            <div class="qc-stat" onclick="document.getElementById('filterStatus').value='';applyFilters();">
                <div class="qc-stat-icon total">&#128203;</div>
                <div><div class="qc-stat-value" id="statPassRate">—</div><div class="qc-stat-label">Pass Rate</div></div>
            </div>
        </div>

        <!-- Filters -->
        <div class="filter-bar">
            <select id="filterProject" onchange="applyFilters()">
                <option value="">All Projects</option>
            </select>
            <select id="filterMachine" onchange="applyFilters()">
                <option value="">All Machine Types</option>
                <option value="WELDING">Welding</option>
                <option value="Z1">Z-Purlin Line 1</option>
                <option value="Z2">Z-Purlin Line 2</option>
                <option value="C1">C-Purlin Line</option>
                <option value="SPARTAN">Spartan</option>
                <option value="P1">Panel Line</option>
                <option value="ANGLE">Angle Line</option>
                <option value="BRAKE">Brake Press</option>
                <option value="TRIM">Trim Line</option>
            </select>
            <select id="filterStatus" onchange="applyFilters()">
                <option value="">All Statuses</option>
                <option value="fabricated">Fabricated (New)</option>
                <option value="qc_pending">QC Pending (In Progress)</option>
            </select>
            <input type="text" id="filterSearch" placeholder="Search ship mark..." oninput="applyFilters()">
            <span id="filterCount" style="font-size:var(--tf-text-xs);color:var(--tf-gray-500);margin-left:auto;"></span>
        </div>

        <!-- Queue Table -->
        <div id="queueContainer">
            <div class="empty-state">
                <div class="icon">&#128203;</div>
                <div>Loading inspection queue...</div>
            </div>
        </div>
    </div>

    <!-- SIGN-OFF MODAL -->
    <div class="modal-bg" id="signOffModal">
        <div class="modal-box">
            <div class="modal-header">
                <h2 id="signOffTitle" style="font-size:var(--tf-text-xl);font-weight:700;">QC Inspection</h2>
                <button onclick="closeModal()" style="background:none;border:none;font-size:1.5rem;cursor:pointer;color:var(--tf-gray-400);">&times;</button>
            </div>
            <div class="modal-body">
                <!-- Item info -->
                <div id="signOffItemInfo" style="margin-bottom:var(--tf-sp-4);padding:var(--tf-sp-4);background:var(--tf-gray-50);border-radius:var(--tf-radius);"></div>

                <!-- Inspection type selector -->
                <div style="margin-bottom:var(--tf-sp-4);">
                    <label class="form-label">Inspection Type</label>
                    <select class="form-input" id="signOffInspType" onchange="renderChecklist()">
                        <option value="weld_visual">Weld Visual Inspection (VT)</option>
                        <option value="dimensional">Dimensional / Fit-Up</option>
                        <option value="bolt_inspection">Bolt Installation</option>
                        <option value="surface_prep">Surface Prep &amp; Coating</option>
                        <option value="nde">Non-Destructive Examination</option>
                        <option value="material_receiving">Material Receiving</option>
                    </select>
                </div>

                <!-- Checklist -->
                <div style="margin-bottom:var(--tf-sp-4);">
                    <label class="form-label">Inspection Checklist</label>
                    <div class="checklist-grid" id="signOffChecklist"></div>
                </div>

                <!-- Notes -->
                <div style="margin-bottom:var(--tf-sp-4);">
                    <label class="form-label">Inspector Notes</label>
                    <textarea class="form-input" id="signOffNotes" rows="3" placeholder="Observations, measurements, deficiencies..."></textarea>
                </div>

                <!-- NCR section (shown on reject) -->
                <div id="ncrSection" style="display:none;padding:var(--tf-sp-4);background:#FEF2F2;border:1px solid #FECACA;border-radius:var(--tf-radius);margin-bottom:var(--tf-sp-4);">
                    <label style="display:flex;align-items:center;gap:8px;font-size:var(--tf-text-sm);font-weight:600;margin-bottom:var(--tf-sp-3);">
                        <input type="checkbox" id="ncrAutoCreate" checked> Auto-create NCR on rejection
                    </label>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:var(--tf-sp-3);">
                        <div>
                            <label class="form-label">NCR Severity</label>
                            <select class="form-input" id="ncrSeverity">
                                <option value="minor">Minor</option>
                                <option value="major" selected>Major</option>
                                <option value="critical">Critical</option>
                            </select>
                        </div>
                        <div>
                            <label class="form-label">Disposition</label>
                            <select class="form-input" id="ncrDisposition">
                                <option value="rework">Rework</option>
                                <option value="repair">Repair</option>
                                <option value="accept-as-is">Accept As-Is</option>
                                <option value="reject">Reject / Scrap</option>
                            </select>
                        </div>
                    </div>
                    <div style="margin-top:var(--tf-sp-3);">
                        <label class="form-label">NCR Title</label>
                        <input type="text" class="form-input" id="ncrTitle" placeholder="Brief description of non-conformance">
                    </div>
                </div>

                <!-- Item history -->
                <div id="signOffHistory"></div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-outline" onclick="closeModal()">Cancel</button>
                <button class="btn-reject" onclick="doSignOff('failed')" style="padding:8px 20px;border-radius:var(--tf-radius);">&#10007; Reject</button>
                <button class="btn-approve" onclick="doSignOff('passed')" style="padding:8px 20px;border-radius:var(--tf-radius);">&#10003; Approve</button>
            </div>
        </div>
    </div>

<script>
let queueItems = [];
let filteredItems = [];
let inspTypes = {};
let currentItem = null;
let dashboardMetrics = null;

document.addEventListener('DOMContentLoaded', () => {
    loadInspTypes();
    refreshQueue();
    loadDashboardStats();
    // Auto-refresh every 30 seconds
    setInterval(refreshQueue, 30000);
});

async function loadInspTypes() {
    const r = await fetch('/api/qc/types');
    const d = await r.json();
    if (d.ok) inspTypes = d.types;
}

async function refreshQueue() {
    try {
        const r = await fetch('/api/qc/queue');
        const d = await r.json();
        if (d.ok) {
            queueItems = d.items;
            buildProjectFilter();
            applyFilters();
            document.getElementById('statPending').textContent = d.total;
        }
    } catch(e) { console.error('Queue load failed:', e); }
}

async function loadDashboardStats() {
    try {
        const r = await fetch('/api/qc/dashboard');
        const d = await r.json();
        if (d.ok) {
            dashboardMetrics = d.metrics;
            document.getElementById('statApprovedToday').textContent = d.metrics.items_approved_today || 0;
            document.getElementById('statRejectedToday').textContent = d.metrics.items_rejected_today || 0;
            document.getElementById('statPassRate').textContent = d.metrics.pass_rate ? d.metrics.pass_rate + '%' : '—';
        }
    } catch(e) {}
}

function buildProjectFilter() {
    const projects = [...new Set(queueItems.map(i => i.job_code))].sort();
    const sel = document.getElementById('filterProject');
    const current = sel.value;
    sel.innerHTML = '<option value="">All Projects</option>' +
        projects.map(p => `<option value="${p}" ${p===current?'selected':''}>${p}</option>`).join('');
}

function applyFilters() {
    const project = document.getElementById('filterProject').value;
    const machine = document.getElementById('filterMachine').value;
    const status = document.getElementById('filterStatus').value;
    const search = document.getElementById('filterSearch').value.toLowerCase();

    filteredItems = queueItems.filter(i => {
        if (project && i.job_code !== project) return false;
        if (machine && i.machine_type !== machine) return false;
        if (status && i.status !== status) return false;
        if (search && !i.ship_mark.toLowerCase().includes(search) &&
            !i.description.toLowerCase().includes(search) &&
            !i.item_id.toLowerCase().includes(search)) return false;
        return true;
    });

    document.getElementById('filterCount').textContent = `${filteredItems.length} items`;
    renderQueue();
}

function renderQueue() {
    const container = document.getElementById('queueContainer');
    if (!filteredItems.length) {
        container.innerHTML = `<div class="empty-state">
            <div class="icon">&#10003;</div>
            <div style="font-size:var(--tf-text-lg);font-weight:600;color:var(--tf-gray-600);">Queue Clear</div>
            <div>No items awaiting QC inspection.</div>
        </div>`;
        return;
    }

    let html = `<table class="queue-table">
        <thead><tr>
            <th style="width:30px;"></th>
            <th>Ship Mark</th>
            <th>Description</th>
            <th>Project</th>
            <th>Machine</th>
            <th>Fabricated By</th>
            <th>Status</th>
            <th style="width:180px;">Actions</th>
        </tr></thead><tbody>`;

    filteredItems.forEach(item => {
        const p = item.priority || 50;
        const pClass = p <= 10 ? 'urgent' : (p >= 80 ? 'low' : 'normal');
        const rowClass = p <= 10 ? 'urgent' : '';
        html += `<tr class="${rowClass}">
            <td><span class="priority-dot ${pClass}" title="Priority: ${p}"></span></td>
            <td style="font-weight:700;font-family:var(--tf-font-mono);">${item.ship_mark}</td>
            <td>${item.description || '—'}</td>
            <td><a href="/qc/${item.job_code}" style="color:var(--tf-blue);text-decoration:none;font-weight:600;">${item.job_code}</a></td>
            <td>${item.machine_type || '—'}</td>
            <td>${item.fabricated_by || '—'}</td>
            <td><span class="status-badge ${item.status}">${item.status_label}</span></td>
            <td>
                <div style="display:flex;gap:6px;">
                    <button class="btn-inspect" onclick="openSignOff('${item.job_code}','${item.item_id}')">Inspect</button>
                    <button class="btn-approve" onclick="quickApprove('${item.job_code}','${item.item_id}')" title="Quick Approve">&#10003;</button>
                    <button class="btn-reject" onclick="quickReject('${item.job_code}','${item.item_id}')" title="Quick Reject">&#10007;</button>
                </div>
            </td>
        </tr>`;
    });

    html += '</tbody></table>';
    container.innerHTML = html;
}

function openSignOff(jobCode, itemId) {
    currentItem = queueItems.find(i => i.job_code === jobCode && i.item_id === itemId);
    if (!currentItem) return;

    document.getElementById('signOffTitle').textContent = `QC Inspection: ${currentItem.ship_mark}`;
    document.getElementById('signOffItemInfo').innerHTML = `
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:var(--tf-sp-3);font-size:var(--tf-text-sm);">
            <div><span style="color:var(--tf-gray-500);">Ship Mark:</span> <strong>${currentItem.ship_mark}</strong></div>
            <div><span style="color:var(--tf-gray-500);">Project:</span> <strong>${currentItem.job_code}</strong></div>
            <div><span style="color:var(--tf-gray-500);">Machine:</span> <strong>${currentItem.machine_type || '—'}</strong></div>
            <div><span style="color:var(--tf-gray-500);">Description:</span> ${currentItem.description || '—'}</div>
            <div><span style="color:var(--tf-gray-500);">Fabricated By:</span> ${currentItem.fabricated_by || '—'}</div>
            <div><span style="color:var(--tf-gray-500);">WO:</span> ${currentItem.wo_name || currentItem.wo_id}</div>
        </div>`;

    // Pick default inspection type based on machine
    const machineInspMap = {
        'WELDING': 'weld_visual',
        'Z1': 'dimensional', 'Z2': 'dimensional', 'C1': 'dimensional',
        'SPARTAN': 'dimensional', 'P1': 'dimensional',
        'ANGLE': 'dimensional', 'BRAKE': 'dimensional', 'TRIM': 'dimensional',
    };
    document.getElementById('signOffInspType').value = machineInspMap[currentItem.machine_type] || 'weld_visual';
    renderChecklist();

    document.getElementById('signOffNotes').value = '';
    document.getElementById('ncrSection').style.display = 'none';
    document.getElementById('ncrTitle').value = '';

    // Load item history
    loadItemHistory(jobCode, itemId);

    document.getElementById('signOffModal').classList.add('open');
}

function renderChecklist() {
    const type = document.getElementById('signOffInspType').value;
    const checklist = inspTypes[type]?.checklist || [];
    const grid = document.getElementById('signOffChecklist');

    if (!checklist.length) {
        grid.innerHTML = '<div style="color:var(--tf-gray-400);font-size:var(--tf-text-sm);">No checklist items for this type.</div>';
        return;
    }

    grid.innerHTML = checklist.map(ci => {
        if (ci.type === 'check') {
            return `<div class="check-item" data-key="${ci.key}">
                <input type="checkbox" id="cl_${ci.key}" onchange="toggleCheckItem(this)">
                <label for="cl_${ci.key}">${ci.label}</label>
            </div>`;
        } else if (ci.type === 'select') {
            return `<div class="check-item" data-key="${ci.key}">
                <label>${ci.label}</label>
                <select id="cl_${ci.key}">
                    <option value="">Select...</option>
                    ${(ci.options||[]).map(o => `<option value="${o}">${o}</option>`).join('')}
                </select>
            </div>`;
        } else {
            return `<div class="check-item" data-key="${ci.key}">
                <label>${ci.label}</label>
                <input type="text" id="cl_${ci.key}" placeholder="Enter value...">
            </div>`;
        }
    }).join('');
}

function toggleCheckItem(el) {
    el.closest('.check-item').classList.toggle('checked', el.checked);
}

async function loadItemHistory(jobCode, itemId) {
    const histDiv = document.getElementById('signOffHistory');
    try {
        const r = await fetch(`/api/qc/item-history?job_code=${encodeURIComponent(jobCode)}&item_id=${encodeURIComponent(itemId)}`);
        const d = await r.json();
        if (d.ok && (d.history.inspections.length || d.history.ncrs.length)) {
            let html = '<div class="history-panel"><div style="font-weight:700;font-size:var(--tf-text-sm);margin-bottom:8px;">Previous QC History</div>';
            d.history.inspections.forEach(i => {
                const statusColor = i.status === 'passed' ? 'var(--tf-success)' : (i.status === 'failed' ? 'var(--tf-danger)' : 'var(--tf-warning)');
                html += `<div class="history-item">
                    <span style="color:${statusColor};font-weight:700;">${i.status.toUpperCase()}</span>
                    ${i.type_label} by ${i.inspector} on ${new Date(i.created_at).toLocaleString()}
                    ${i.notes ? '<br><span style="color:var(--tf-gray-500);">' + i.notes.substring(0,100) + '</span>' : ''}
                </div>`;
            });
            d.history.ncrs.forEach(n => {
                html += `<div class="history-item" style="color:var(--tf-danger);">
                    NCR ${n.id}: ${n.title} (${n.severity}) — ${n.status}
                </div>`;
            });
            html += '</div>';
            histDiv.innerHTML = html;
        } else {
            histDiv.innerHTML = '';
        }
    } catch(e) { histDiv.innerHTML = ''; }
}

function collectChecklist() {
    const items = {};
    document.querySelectorAll('#signOffChecklist .check-item').forEach(div => {
        const key = div.dataset.key;
        const checkbox = div.querySelector('input[type="checkbox"]');
        const select = div.querySelector('select');
        const text = div.querySelector('input[type="text"]');
        if (checkbox) items[key] = checkbox.checked;
        else if (select) items[key] = select.value;
        else if (text) items[key] = text.value;
    });
    return items;
}

async function doSignOff(result) {
    if (!currentItem) return;

    const body = {
        job_code: currentItem.job_code,
        item_id: currentItem.item_id,
        result: result,
        inspection_type: document.getElementById('signOffInspType').value,
        notes: document.getElementById('signOffNotes').value,
        checklist_items: collectChecklist(),
        member_marks: [currentItem.ship_mark],
    };

    if (result === 'failed') {
        body.create_ncr = document.getElementById('ncrAutoCreate').checked;
        body.ncr_severity = document.getElementById('ncrSeverity').value;
        body.ncr_title = document.getElementById('ncrTitle').value || `QC Rejection: ${currentItem.ship_mark}`;
        body.disposition = document.getElementById('ncrDisposition').value;
    }

    try {
        const r = await fetch('/api/qc/sign-off', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(body),
        });
        const d = await r.json();
        if (d.ok) {
            closeModal();
            refreshQueue();
            loadDashboardStats();
            showToast(result === 'passed'
                ? `&#10003; ${currentItem.ship_mark} approved`
                : `&#10007; ${currentItem.ship_mark} rejected` + (d.ncr ? ` — ${d.ncr.id} created` : ''),
                result === 'passed' ? 'success' : 'error');
        } else {
            alert('Error: ' + (d.error || 'Unknown error'));
        }
    } catch(e) { alert('Network error: ' + e.message); }
}

async function quickApprove(jobCode, itemId) {
    if (!confirm('Quick approve this item? (No checklist)')) return;
    try {
        const r = await fetch('/api/qc/sign-off', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                job_code: jobCode, item_id: itemId,
                result: 'passed', notes: 'Quick approval',
                inspection_type: 'weld_visual', checklist_items: {},
            }),
        });
        const d = await r.json();
        if (d.ok) {
            refreshQueue();
            loadDashboardStats();
            showToast('&#10003; Item approved', 'success');
        } else alert(d.error);
    } catch(e) { alert(e.message); }
}

async function quickReject(jobCode, itemId) {
    const reason = prompt('Rejection reason:');
    if (!reason) return;
    try {
        const r = await fetch('/api/qc/sign-off', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                job_code: jobCode, item_id: itemId,
                result: 'failed', notes: reason,
                inspection_type: 'weld_visual', checklist_items: {},
                create_ncr: true, ncr_severity: 'major', disposition: 'rework',
            }),
        });
        const d = await r.json();
        if (d.ok) {
            refreshQueue();
            loadDashboardStats();
            showToast('&#10007; Item rejected' + (d.ncr ? ' — NCR ' + d.ncr.id : ''), 'error');
        } else alert(d.error);
    } catch(e) { alert(e.message); }
}

function closeModal() { document.getElementById('signOffModal').classList.remove('open'); }

// Show NCR section when rejecting
document.querySelector('.btn-reject[onclick*="doSignOff"]')?.addEventListener('mouseenter', () => {
    document.getElementById('ncrSection').style.display = 'block';
});

function showToast(msg, type) {
    const toast = document.createElement('div');
    toast.style.cssText = `position:fixed;top:20px;right:20px;padding:12px 20px;border-radius:8px;font-size:14px;font-weight:600;z-index:500;color:#fff;
        background:${type==='success'?'var(--tf-success)':'var(--tf-danger)'};box-shadow:var(--tf-shadow-lg);`;
    toast.innerHTML = msg;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeModal();
});
</script>
</body>
</html>
"""
