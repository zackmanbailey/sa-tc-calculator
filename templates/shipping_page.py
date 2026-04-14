"""
TitanForge v4 — Shipping Dashboard
====================================
Overview of all loads: active shipments, delivery tracking,
status pipeline, weight/piece metrics, recent activity.
"""
from templates.shared_styles import DESIGN_SYSTEM_CSS

SHIPPING_PAGE_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TitanForge — Shipping Dashboard</title>
    <style>
""" + DESIGN_SYSTEM_CSS + r"""

        .container { max-width: 1400px; margin: 0 auto; padding: var(--tf-sp-6) var(--tf-sp-8); }

        /* Top actions bar */
        .top-bar {
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: var(--tf-sp-6);
        }
        .top-bar h1 { font-size: var(--tf-text-xl); font-weight: 800; color: var(--tf-gray-900); margin: 0; }
        .top-bar .actions { display: flex; gap: var(--tf-sp-3); }

        /* Metric cards row */
        .metric-row { display: grid; grid-template-columns: repeat(5, 1fr); gap: var(--tf-sp-4); margin-bottom: var(--tf-sp-6); }
        .metric-card {
            background: var(--tf-surface); border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-lg); padding: var(--tf-sp-5);
            text-align: center;
        }
        .metric-card .value { font-size: var(--tf-text-2xl); font-weight: 800; color: var(--tf-gray-900); }
        .metric-card .label {
            font-size: var(--tf-text-xs); color: var(--tf-gray-500);
            text-transform: uppercase; letter-spacing: 0.04em; margin-top: 2px;
        }
        .metric-card .sublabel { font-size: 11px; color: var(--tf-gray-400); margin-top: 4px; }
        .metric-card.building { border-left: 4px solid var(--tf-amber); }
        .metric-card.ready { border-left: 4px solid var(--tf-blue); }
        .metric-card.transit { border-left: 4px solid #8b5cf6; }
        .metric-card.delivered { border-left: 4px solid var(--tf-success); }
        .metric-card.total { border-left: 4px solid var(--tf-gray-600); }

        /* Pipeline bar */
        .pipeline-section { margin-bottom: var(--tf-sp-6); }
        .pipeline-bar {
            display: flex; height: 32px; border-radius: var(--tf-radius-md); overflow: hidden;
            background: var(--tf-gray-100);
        }
        .pipeline-bar .segment {
            display: flex; align-items: center; justify-content: center;
            font-size: 11px; font-weight: 700; color: white;
            min-width: 40px; transition: width 0.4s ease;
        }
        .pipeline-bar .seg-building { background: var(--tf-amber); }
        .pipeline-bar .seg-ready { background: var(--tf-blue); }
        .pipeline-bar .seg-transit { background: #8b5cf6; }
        .pipeline-bar .seg-delivered { background: var(--tf-success); }
        .pipeline-bar .seg-complete { background: var(--tf-gray-400); }
        .pipeline-legend {
            display: flex; gap: var(--tf-sp-5); margin-top: var(--tf-sp-2);
            font-size: var(--tf-text-xs); color: var(--tf-gray-500);
        }
        .pipeline-legend .dot {
            display: inline-block; width: 10px; height: 10px;
            border-radius: 50%; margin-right: 4px; vertical-align: middle;
        }

        /* Filter bar */
        .filter-bar {
            display: flex; gap: var(--tf-sp-3); margin-bottom: var(--tf-sp-4);
            align-items: center;
        }
        .filter-bar select, .filter-bar input {
            padding: var(--tf-sp-2) var(--tf-sp-3); border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-md); font-size: var(--tf-text-sm);
            background: var(--tf-surface);
        }

        /* Loads table */
        .panel {
            background: var(--tf-surface); border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-lg); overflow: hidden; margin-bottom: var(--tf-sp-6);
        }
        .panel-header {
            padding: var(--tf-sp-4) var(--tf-sp-5); border-bottom: 1px solid var(--tf-border);
            font-weight: 700; font-size: var(--tf-text-md); color: var(--tf-gray-900);
            display: flex; justify-content: space-between; align-items: center;
            background: var(--tf-gray-50);
        }
        .panel-body { padding: 0; }

        .loads-table { width: 100%; border-collapse: collapse; }
        .loads-table th {
            padding: var(--tf-sp-3) var(--tf-sp-4); text-align: left;
            font-size: var(--tf-text-xs); font-weight: 600; color: var(--tf-gray-500);
            text-transform: uppercase; letter-spacing: 0.04em;
            border-bottom: 1px solid var(--tf-border); background: var(--tf-gray-50);
        }
        .loads-table td {
            padding: var(--tf-sp-3) var(--tf-sp-4); font-size: var(--tf-text-sm);
            border-bottom: 1px solid var(--tf-border); color: var(--tf-gray-700);
        }
        .loads-table tr:hover { background: var(--tf-gray-50); cursor: pointer; }
        .loads-table .load-number { font-weight: 700; color: var(--tf-blue); }

        /* Status pill */
        .status-pill {
            display: inline-block; padding: 2px 10px; border-radius: 999px;
            font-size: 11px; font-weight: 600; text-transform: capitalize;
        }
        .status-pill.building { background: #fef3c7; color: #92400e; }
        .status-pill.ready { background: #dbeafe; color: #1e40af; }
        .status-pill.in_transit { background: #ede9fe; color: #5b21b6; }
        .status-pill.delivered { background: #d1fae5; color: #065f46; }
        .status-pill.complete { background: var(--tf-gray-100); color: var(--tf-gray-600); }

        /* Load detail modal */
        .modal-backdrop {
            display: none; position: fixed; inset: 0;
            background: rgba(0,0,0,0.4); z-index: 1000;
            justify-content: center; align-items: center;
        }
        .modal-backdrop.active { display: flex; }
        .modal {
            background: var(--tf-surface); border-radius: var(--tf-radius-lg);
            width: 720px; max-height: 85vh; overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0,0,0,0.2);
        }
        .modal-header {
            padding: var(--tf-sp-5) var(--tf-sp-6);
            border-bottom: 1px solid var(--tf-border);
            display: flex; justify-content: space-between; align-items: center;
        }
        .modal-header h2 { font-size: var(--tf-text-lg); font-weight: 700; margin: 0; }
        .modal-body { padding: var(--tf-sp-5) var(--tf-sp-6); }
        .modal-footer {
            padding: var(--tf-sp-4) var(--tf-sp-6);
            border-top: 1px solid var(--tf-border);
            display: flex; justify-content: flex-end; gap: var(--tf-sp-3);
        }

        .detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--tf-sp-3); margin-bottom: var(--tf-sp-4); }
        .detail-item label { display: block; font-size: 11px; color: var(--tf-gray-500); text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 2px; }
        .detail-item span { font-size: var(--tf-text-sm); color: var(--tf-gray-800); font-weight: 500; }

        .item-list-table { width: 100%; border-collapse: collapse; margin-top: var(--tf-sp-3); }
        .item-list-table th {
            padding: 6px 10px; font-size: 11px; font-weight: 600; color: var(--tf-gray-500);
            text-transform: uppercase; border-bottom: 1px solid var(--tf-border);
            text-align: left;
        }
        .item-list-table td {
            padding: 6px 10px; font-size: var(--tf-text-sm); color: var(--tf-gray-700);
            border-bottom: 1px solid var(--tf-gray-100);
        }

        /* Dashboard grid (bottom section) */
        .dashboard-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--tf-sp-6); }

        /* Delivery notes */
        .delivery-card {
            padding: var(--tf-sp-4); border-bottom: 1px solid var(--tf-gray-100);
        }
        .delivery-card:last-child { border-bottom: none; }
        .delivery-card .load-ref { font-weight: 700; color: var(--tf-blue); font-size: var(--tf-text-sm); }
        .delivery-card .timestamp { font-size: 11px; color: var(--tf-gray-400); margin-left: 8px; }
        .delivery-card .dest { font-size: var(--tf-text-sm); color: var(--tf-gray-600); margin-top: 2px; }

        /* Weight chart bars */
        .weight-bar-chart { display: flex; flex-direction: column; gap: 6px; padding: var(--tf-sp-4); }
        .weight-row { display: flex; align-items: center; gap: 10px; }
        .weight-row .project-label { width: 100px; font-size: 12px; font-weight: 600; color: var(--tf-gray-600); text-align: right; }
        .weight-row .bar-track { flex: 1; height: 20px; background: var(--tf-gray-100); border-radius: var(--tf-radius-sm); overflow: hidden; }
        .weight-row .bar-fill { height: 100%; background: var(--tf-blue); border-radius: var(--tf-radius-sm); transition: width 0.4s ease; display: flex; align-items: center; padding-left: 6px; }
        .weight-row .bar-fill span { font-size: 10px; font-weight: 700; color: white; white-space: nowrap; }
        .weight-row .weight-val { width: 80px; font-size: 12px; color: var(--tf-gray-500); }

        /* Toast */
        .toast { position: fixed; bottom: 24px; right: 24px; background: var(--tf-gray-900); color: white; padding: 12px 20px; border-radius: var(--tf-radius-md); font-size: var(--tf-text-sm); z-index: 2000; display: none; }
        .toast.success { background: var(--tf-success); }
        .toast.error { background: var(--tf-danger); }

        /* Empty state */
        .empty-state {
            text-align: center; padding: var(--tf-sp-8) var(--tf-sp-4);
            color: var(--tf-gray-400);
        }
        .empty-state .icon { font-size: 48px; margin-bottom: var(--tf-sp-3); }
        .empty-state p { font-size: var(--tf-text-sm); }

        @media (max-width: 900px) {
            .metric-row { grid-template-columns: repeat(3, 1fr); }
            .dashboard-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Top bar -->
        <div class="top-bar">
            <h1>Shipping Dashboard</h1>
            <div class="actions">
                <a href="/shipping/load-builder" class="btn btn-primary">Open Load Builder</a>
                <button onclick="refreshDashboard()" class="btn btn-secondary">Refresh</button>
            </div>
        </div>

        <!-- Metric cards -->
        <div class="metric-row" id="metricRow">
            <div class="metric-card building">
                <div class="value" id="metBuilding">—</div>
                <div class="label">Building</div>
            </div>
            <div class="metric-card ready">
                <div class="value" id="metReady">—</div>
                <div class="label">Ready to Ship</div>
            </div>
            <div class="metric-card transit">
                <div class="value" id="metTransit">—</div>
                <div class="label">In Transit</div>
            </div>
            <div class="metric-card delivered">
                <div class="value" id="metDelivered">—</div>
                <div class="label">Delivered</div>
            </div>
            <div class="metric-card total">
                <div class="value" id="metTotal">—</div>
                <div class="label">Total Loads</div>
                <div class="sublabel" id="metWeight">—</div>
            </div>
        </div>

        <!-- Pipeline bar -->
        <div class="pipeline-section">
            <div class="pipeline-bar" id="pipelineBar"></div>
            <div class="pipeline-legend">
                <span><span class="dot" style="background:var(--tf-amber)"></span> Building</span>
                <span><span class="dot" style="background:var(--tf-blue)"></span> Ready</span>
                <span><span class="dot" style="background:#8b5cf6"></span> In Transit</span>
                <span><span class="dot" style="background:var(--tf-success)"></span> Delivered</span>
                <span><span class="dot" style="background:var(--tf-gray-400)"></span> Complete</span>
            </div>
        </div>

        <!-- Filter bar -->
        <div class="filter-bar">
            <select id="filterStatus" onchange="applyFilters()">
                <option value="">All Statuses</option>
                <option value="building">Building</option>
                <option value="ready">Ready to Ship</option>
                <option value="in_transit">In Transit</option>
                <option value="delivered">Delivered</option>
                <option value="complete">Complete</option>
            </select>
            <select id="filterProject" onchange="applyFilters()">
                <option value="">All Projects</option>
            </select>
            <input type="text" id="searchInput" placeholder="Search loads..." oninput="applyFilters()">
        </div>

        <!-- Loads table -->
        <div class="panel">
            <div class="panel-header">
                <span>All Loads <span id="loadCount" style="font-weight:400;color:var(--tf-gray-400);margin-left:8px;"></span></span>
            </div>
            <div class="panel-body">
                <table class="loads-table">
                    <thead>
                        <tr>
                            <th>Load #</th>
                            <th>Status</th>
                            <th>Project</th>
                            <th>Destination</th>
                            <th>Items</th>
                            <th>Weight (lbs)</th>
                            <th>Carrier</th>
                            <th>Created</th>
                            <th>Shipped</th>
                        </tr>
                    </thead>
                    <tbody id="loadsBody"></tbody>
                </table>
                <div class="empty-state" id="emptyState" style="display:none;">
                    <div class="icon">&#128666;</div>
                    <p>No loads yet. Open the <a href="/shipping/load-builder">Load Builder</a> to create your first load.</p>
                </div>
            </div>
        </div>

        <!-- Bottom dashboard grid -->
        <div class="dashboard-grid">
            <!-- Recent deliveries -->
            <div class="panel">
                <div class="panel-header">
                    <span>Recent Deliveries</span>
                </div>
                <div class="panel-body" id="recentDeliveries" style="padding:0;max-height:320px;overflow-y:auto;">
                </div>
            </div>

            <!-- Weight by project -->
            <div class="panel">
                <div class="panel-header">
                    <span>Shipped Weight by Project</span>
                </div>
                <div class="panel-body" id="weightByProject" style="padding:0;">
                </div>
            </div>
        </div>
    </div>

    <!-- Load detail modal -->
    <div class="modal-backdrop" id="detailModal">
        <div class="modal">
            <div class="modal-header">
                <h2 id="detailTitle">Load Details</h2>
                <button onclick="closeModal()" style="background:none;border:none;font-size:20px;cursor:pointer;color:var(--tf-gray-400);">&#10005;</button>
            </div>
            <div class="modal-body" id="detailBody"></div>
            <div class="modal-footer" id="detailFooter"></div>
        </div>
    </div>

    <!-- Toast -->
    <div class="toast" id="toast"></div>

    <script>
    let allLoads = [];
    let summaryData = {};

    async function refreshDashboard() {
        try {
            const [summaryRes, loadsRes] = await Promise.all([
                fetch('/api/shipping/summary'),
                fetch('/api/shipping/loads')
            ]);
            summaryData = await summaryRes.json();
            const loadsData = await loadsRes.json();
            allLoads = loadsData.loads || [];

            renderMetrics();
            renderPipeline();
            populateProjectFilter();
            applyFilters();
            renderRecentDeliveries();
            renderWeightByProject();
        } catch (err) {
            showToast('Failed to load shipping data', 'error');
        }
    }

    function renderMetrics() {
        const s = summaryData;
        document.getElementById('metBuilding').textContent = s.building || 0;
        document.getElementById('metReady').textContent = s.ready || 0;
        document.getElementById('metTransit').textContent = s.in_transit || 0;
        document.getElementById('metDelivered').textContent = s.delivered || 0;
        document.getElementById('metTotal').textContent = s.total_loads || 0;
        const w = s.total_weight_shipped || 0;
        document.getElementById('metWeight').textContent = w > 0
            ? `${w.toLocaleString()} lbs shipped`
            : 'No weight data';
    }

    function renderPipeline() {
        const s = summaryData;
        const total = s.total_loads || 1;
        const bar = document.getElementById('pipelineBar');

        const segments = [
            { cls: 'seg-building', count: s.building || 0 },
            { cls: 'seg-ready', count: s.ready || 0 },
            { cls: 'seg-transit', count: s.in_transit || 0 },
            { cls: 'seg-delivered', count: s.delivered || 0 },
            { cls: 'seg-complete', count: s.complete || 0 },
        ];

        bar.innerHTML = segments
            .filter(seg => seg.count > 0)
            .map(seg => {
                const pct = Math.max((seg.count / total) * 100, 5);
                return `<div class="segment ${seg.cls}" style="width:${pct}%">${seg.count}</div>`;
            }).join('');

        if (total <= 1 && !s.total_loads) {
            bar.innerHTML = '<div style="width:100%;text-align:center;color:var(--tf-gray-400);font-size:12px;line-height:32px;">No loads</div>';
        }
    }

    function populateProjectFilter() {
        const projects = new Set();
        allLoads.forEach(l => {
            if (l.job_code) projects.add(l.job_code);
        });
        const sel = document.getElementById('filterProject');
        const current = sel.value;
        sel.innerHTML = '<option value="">All Projects</option>';
        [...projects].sort().forEach(p => {
            sel.innerHTML += `<option value="${p}">${p}</option>`;
        });
        sel.value = current;
    }

    function applyFilters() {
        const statusFilter = document.getElementById('filterStatus').value;
        const projectFilter = document.getElementById('filterProject').value;
        const search = document.getElementById('searchInput').value.toLowerCase();

        let filtered = allLoads;
        if (statusFilter) filtered = filtered.filter(l => l.status === statusFilter);
        if (projectFilter) filtered = filtered.filter(l => l.job_code === projectFilter);
        if (search) {
            filtered = filtered.filter(l =>
                (l.load_id || '').toLowerCase().includes(search) ||
                (l.destination || '').toLowerCase().includes(search) ||
                (l.carrier || '').toLowerCase().includes(search) ||
                (l.job_code || '').toLowerCase().includes(search) ||
                String(l.load_number || '').includes(search)
            );
        }

        renderLoadsTable(filtered);
    }

    function renderLoadsTable(loads) {
        const body = document.getElementById('loadsBody');
        const empty = document.getElementById('emptyState');
        const countEl = document.getElementById('loadCount');

        if (!loads || loads.length === 0) {
            body.innerHTML = '';
            empty.style.display = 'block';
            countEl.textContent = '';
            return;
        }

        empty.style.display = 'none';
        countEl.textContent = `(${loads.length})`;

        body.innerHTML = loads.map(l => {
            const statusCls = (l.status || '').replace(/ /g, '_');
            const statusLabel = {
                building: 'Building', ready: 'Ready to Ship',
                in_transit: 'In Transit', delivered: 'Delivered', complete: 'Complete'
            }[l.status] || l.status;
            const created = l.created_at ? new Date(l.created_at).toLocaleDateString() : '—';
            const shipped = l.shipped_at ? new Date(l.shipped_at).toLocaleDateString() : '—';
            return `<tr onclick="showLoadDetail('${l.load_id}')">
                <td class="load-number">L-${String(l.load_number).padStart(3,'0')}</td>
                <td><span class="status-pill ${statusCls}">${statusLabel}</span></td>
                <td>${l.job_code || '—'}</td>
                <td>${l.destination || '—'}</td>
                <td>${l.total_items || 0}</td>
                <td>${(l.total_weight || 0).toLocaleString()}</td>
                <td>${l.carrier || '—'}</td>
                <td>${created}</td>
                <td>${shipped}</td>
            </tr>`;
        }).join('');
    }

    function renderRecentDeliveries() {
        const container = document.getElementById('recentDeliveries');
        const delivered = allLoads.filter(l =>
            l.status === 'delivered' || l.status === 'complete'
        ).slice(0, 10);

        if (delivered.length === 0) {
            container.innerHTML = '<div class="empty-state"><p>No deliveries yet</p></div>';
            return;
        }

        container.innerHTML = delivered.map(l => {
            const dt = l.delivered_at ? new Date(l.delivered_at).toLocaleString() : 'Pending';
            return `<div class="delivery-card">
                <span class="load-ref">L-${String(l.load_number).padStart(3,'0')}</span>
                <span class="timestamp">${dt}</span>
                <div class="dest">${l.destination || l.job_code || '—'} &mdash; ${l.total_items || 0} items, ${((l.total_weight || 0)).toLocaleString()} lbs</div>
            </div>`;
        }).join('');
    }

    function renderWeightByProject() {
        const container = document.getElementById('weightByProject');
        const shipped = allLoads.filter(l =>
            ['in_transit', 'delivered', 'complete'].includes(l.status)
        );

        const byProject = {};
        shipped.forEach(l => {
            const key = l.job_code || 'Unknown';
            byProject[key] = (byProject[key] || 0) + (l.total_weight || 0);
        });

        const entries = Object.entries(byProject).sort((a, b) => b[1] - a[1]);
        if (entries.length === 0) {
            container.innerHTML = '<div class="empty-state"><p>No shipped weight data</p></div>';
            return;
        }

        const maxWeight = entries[0][1] || 1;
        container.innerHTML = '<div class="weight-bar-chart">' + entries.map(([proj, weight]) => {
            const pct = Math.max((weight / maxWeight) * 100, 3);
            return `<div class="weight-row">
                <span class="project-label">${proj}</span>
                <div class="bar-track"><div class="bar-fill" style="width:${pct}%"><span>${weight.toLocaleString()}</span></div></div>
                <span class="weight-val">${weight.toLocaleString()} lbs</span>
            </div>`;
        }).join('') + '</div>';
    }

    async function showLoadDetail(loadId) {
        try {
            const res = await fetch(`/api/shipping/loads/${loadId}`);
            const load = await res.json();
            renderDetailModal(load);
        } catch (err) {
            showToast('Failed to load detail', 'error');
        }
    }

    function renderDetailModal(load) {
        const statusLabel = {
            building: 'Building', ready: 'Ready to Ship',
            in_transit: 'In Transit', delivered: 'Delivered', complete: 'Complete'
        }[load.status] || load.status;
        const statusCls = (load.status || '').replace(/ /g, '_');

        document.getElementById('detailTitle').innerHTML =
            `Load L-${String(load.load_number).padStart(3,'0')} <span class="status-pill ${statusCls}" style="margin-left:12px;vertical-align:middle;">${statusLabel}</span>`;

        let bodyHtml = `<div class="detail-grid">
            <div class="detail-item"><label>Project</label><span>${load.job_code || '—'}</span></div>
            <div class="detail-item"><label>Destination</label><span>${load.destination || '—'}</span></div>
            <div class="detail-item"><label>Carrier</label><span>${load.carrier || '—'}</span></div>
            <div class="detail-item"><label>Trailer</label><span>${load.trailer_type || '—'}</span></div>
            <div class="detail-item"><label>Driver</label><span>${load.driver_name || '—'} ${load.driver_phone ? '(' + load.driver_phone + ')' : ''}</span></div>
            <div class="detail-item"><label>BOL</label><span>${load.bol_number || 'Not generated'}</span></div>
            <div class="detail-item"><label>Created</label><span>${load.created_at ? new Date(load.created_at).toLocaleString() : '—'}</span></div>
            <div class="detail-item"><label>Shipped</label><span>${load.shipped_at ? new Date(load.shipped_at).toLocaleString() : '—'}</span></div>
        </div>`;

        if (load.special_instructions) {
            bodyHtml += `<div style="margin-bottom:var(--tf-sp-4);padding:var(--tf-sp-3);background:var(--tf-amber-50,#fffbeb);border:1px solid var(--tf-amber);border-radius:var(--tf-radius-md);font-size:var(--tf-text-sm);">
                <strong>Special Instructions:</strong> ${load.special_instructions}
            </div>`;
        }

        if (load.delivery_notes) {
            bodyHtml += `<div style="margin-bottom:var(--tf-sp-4);padding:var(--tf-sp-3);background:#f0fdf4;border:1px solid var(--tf-success);border-radius:var(--tf-radius-md);font-size:var(--tf-text-sm);">
                <strong>Delivery Notes:</strong> ${load.delivery_notes}
            </div>`;
        }

        const items = load.items || [];
        if (items.length > 0) {
            bodyHtml += `<h3 style="font-size:var(--tf-text-sm);font-weight:700;margin-bottom:var(--tf-sp-2);color:var(--tf-gray-700);">Items (${items.length})</h3>`;
            bodyHtml += `<table class="item-list-table">
                <thead><tr><th>Ship Mark</th><th>Description</th><th>Qty</th><th>Weight</th><th>Length</th><th>Bundle</th></tr></thead>
                <tbody>${items.map(i => `<tr>
                    <td style="font-weight:600;">${i.ship_mark || i.item_id}</td>
                    <td>${i.description || '—'}</td>
                    <td>${i.quantity || 1}</td>
                    <td>${i.weight_lbs ? i.weight_lbs.toLocaleString() + ' lbs' : '—'}</td>
                    <td>${i.length_ft ? i.length_ft + "'" : '—'}</td>
                    <td>${i.bundle_tag || '—'}</td>
                </tr>`).join('')}</tbody>
            </table>`;
        } else {
            bodyHtml += '<p style="color:var(--tf-gray-400);font-size:var(--tf-text-sm);">No items on this load.</p>';
        }

        document.getElementById('detailBody').innerHTML = bodyHtml;

        // Footer actions
        let footerHtml = '<button onclick="closeModal()" class="btn btn-secondary">Close</button>';
        if (load.status === 'building') {
            footerHtml = `<button onclick="window.location='/shipping/load-builder'" class="btn btn-primary">Open in Load Builder</button>` + footerHtml;
        }
        if (['ready', 'in_transit'].includes(load.status)) {
            const nextStatus = load.status === 'ready' ? 'in_transit' : 'delivered';
            const nextLabel = load.status === 'ready' ? 'Mark Shipped' : 'Mark Delivered';
            footerHtml = `<button onclick="transitionLoad('${load.load_id}','${nextStatus}')" class="btn btn-primary">${nextLabel}</button>` + footerHtml;
        }
        document.getElementById('detailFooter').innerHTML = footerHtml;

        document.getElementById('detailModal').classList.add('active');
    }

    function closeModal() {
        document.getElementById('detailModal').classList.remove('active');
    }

    async function transitionLoad(loadId, newStatus) {
        try {
            const res = await fetch(`/api/shipping/loads/${loadId}/transition`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ new_status: newStatus })
            });
            const result = await res.json();
            if (result.ok) {
                showToast('Load status updated', 'success');
                closeModal();
                refreshDashboard();
            } else {
                showToast(result.error || 'Transition failed', 'error');
            }
        } catch (err) {
            showToast('Failed to update load', 'error');
        }
    }

    function showToast(msg, type) {
        const t = document.getElementById('toast');
        t.textContent = msg;
        t.className = 'toast ' + (type || '');
        t.style.display = 'block';
        setTimeout(() => { t.style.display = 'none'; }, 3500);
    }

    // ESC to close modal
    document.addEventListener('keydown', e => {
        if (e.key === 'Escape') closeModal();
    });

    // Initial load + auto-refresh
    refreshDashboard();
    setInterval(refreshDashboard, 45000);
    </script>
</body>
</html>
"""
