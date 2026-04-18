"""
TitanForge v4 — Activity Feed & Audit Trail Dashboard
=======================================================
Filterable timeline of all system events. Shows recent activity,
category breakdowns, user activity, and pagination.
"""
from templates.shared_styles import DESIGN_SYSTEM_CSS

ACTIVITY_FEED_PAGE_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TitanForge — Activity Feed</title>
    <style>
""" + DESIGN_SYSTEM_CSS + r"""

        .container { max-width: 1400px; margin: 0 auto; padding: var(--tf-sp-6) var(--tf-sp-8); }

        .top-bar {
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: var(--tf-sp-6);
        }
        .top-bar h1 { font-size: var(--tf-text-xl); font-weight: 800; margin: 0; }
        .top-bar .actions { display: flex; gap: var(--tf-sp-3); align-items: center; }

        /* Stat cards */
        .stat-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--tf-sp-4); margin-bottom: var(--tf-sp-6); }
        .stat-card {
            background: var(--tf-surface); border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-lg); padding: var(--tf-sp-4); text-align: center;
            cursor: pointer; transition: transform 0.15s, box-shadow 0.15s;
        }
        .stat-card:hover { transform: translateY(-2px); box-shadow: var(--tf-shadow-md); }
        .stat-card .val { font-size: var(--tf-text-2xl); font-weight: 800; }
        .stat-card .lbl { font-size: var(--tf-text-xs); color: var(--tf-gray-500); text-transform: uppercase; letter-spacing: 0.04em; margin-top: 2px; }
        .stat-card.blue .val { color: var(--tf-blue); }
        .stat-card.green .val { color: var(--tf-success); }
        .stat-card.amber .val { color: var(--tf-amber); }
        .stat-card.purple .val { color: #8b5cf6; }

        /* Layout */
        .main-grid { display: grid; grid-template-columns: 1fr 320px; gap: var(--tf-sp-6); }

        /* Filter bar */
        .filter-bar {
            display: flex; gap: var(--tf-sp-3); margin-bottom: var(--tf-sp-4);
            flex-wrap: wrap; align-items: center;
        }
        .filter-bar select, .filter-bar input {
            padding: var(--tf-sp-2) var(--tf-sp-3); border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-md); font-size: var(--tf-text-sm);
            background: var(--tf-surface); color: var(--tf-gray-900);
        }

        /* Event list */
        .event-list { list-style: none; padding: 0; margin: 0; }
        .event-item {
            display: flex; gap: var(--tf-sp-3); padding: var(--tf-sp-3) var(--tf-sp-4);
            border-bottom: 1px solid var(--tf-gray-100); background: var(--tf-surface);
            transition: background 0.1s;
        }
        .event-item:first-child { border-radius: var(--tf-radius-lg) var(--tf-radius-lg) 0 0; }
        .event-item:last-child { border-radius: 0 0 var(--tf-radius-lg) var(--tf-radius-lg); border-bottom: none; }
        .event-item { cursor: pointer; }
        .event-item:hover { background: var(--tf-gray-50); }

        .event-icon {
            width: 36px; height: 36px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-size: 14px; font-weight: 700; flex-shrink: 0;
        }
        .event-icon.blue { background: #dbeafe; color: #1e40af; }
        .event-icon.purple { background: #ede9fe; color: #7c3aed; }
        .event-icon.amber { background: #fef3c7; color: #92400e; }
        .event-icon.green { background: #d1fae5; color: #065f46; }
        .event-icon.red { background: #fee2e2; color: #991b1b; }
        .event-icon.gray { background: var(--tf-gray-100); color: var(--tf-gray-600); }

        .event-body { flex: 1; min-width: 0; }
        .event-title { font-size: var(--tf-text-sm); font-weight: 600; color: var(--tf-gray-900); }
        .event-desc { font-size: 12px; color: var(--tf-gray-500); margin-top: 2px; }
        .event-meta { display: flex; gap: var(--tf-sp-3); margin-top: 4px; font-size: 11px; color: var(--tf-gray-400); }

        .event-badge {
            display: inline-block; padding: 1px 6px; border-radius: 999px;
            font-size: 10px; font-weight: 600;
        }
        .event-badge.user { background: #dbeafe; color: #1e40af; }
        .event-badge.coil { background: #fef3c7; color: #92400e; }
        .event-badge.project { background: #ede9fe; color: #7c3aed; }
        .event-badge.customer { background: #d1fae5; color: #065f46; }
        .event-badge.quote { background: #fce7f3; color: #9d174d; }
        .event-badge.allocation { background: #e0e7ff; color: #3730a3; }

        /* Side panel */
        .panel {
            background: var(--tf-surface); border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-lg); overflow: hidden; margin-bottom: var(--tf-sp-4);
        }
        .panel-header {
            padding: var(--tf-sp-3) var(--tf-sp-4); border-bottom: 1px solid var(--tf-border);
            font-weight: 700; font-size: var(--tf-text-sm); background: var(--tf-gray-50);
        }
        .panel-body { padding: var(--tf-sp-4); }

        .cat-row { display: flex; justify-content: space-between; padding: 4px 0; font-size: 13px; }
        .cat-row .v { font-weight: 600; }

        .cat-dot {
            display: inline-block; width: 8px; height: 8px; border-radius: 50%;
            margin-right: 6px; vertical-align: middle;
        }

        /* Pagination */
        .pagination {
            display: flex; justify-content: center; gap: var(--tf-sp-2);
            margin-top: var(--tf-sp-4);
        }
        .pagination button {
            padding: var(--tf-sp-2) var(--tf-sp-4); border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-md); background: var(--tf-surface);
            cursor: pointer; font-size: var(--tf-text-sm);
        }
        .pagination button:hover { background: var(--tf-gray-50); }
        .pagination button:disabled { opacity: 0.4; cursor: default; }
        .pagination .info { padding: var(--tf-sp-2); font-size: var(--tf-text-sm); color: var(--tf-gray-500); }

        .empty-state { text-align: center; padding: var(--tf-sp-8); color: var(--tf-gray-400); }

        @media (max-width: 1000px) {
            .stat-row { grid-template-columns: repeat(2, 1fr); }
            .main-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="top-bar">
            <h1>Activity Feed</h1>
            <div class="actions">
                <button onclick="loadAll()" class="btn btn-primary">Refresh</button>
            </div>
        </div>

        <!-- Stat cards -->
        <div class="stat-row">
            <div class="stat-card blue" onclick="document.getElementById('filterEntityType').value='';resetAndLoad();"><div class="val" id="statTotal">--</div><div class="lbl">Total Events</div></div>
            <div class="stat-card green" onclick="document.getElementById('filterEntityType').value='';resetAndLoad();"><div class="val" id="statToday">--</div><div class="lbl">Today</div></div>
            <div class="stat-card amber" onclick="document.getElementById('filterEntityType').value='';resetAndLoad();"><div class="val" id="statTypes">--</div><div class="lbl">Entity Types</div></div>
            <div class="stat-card purple" onclick="document.getElementById('filterEntityType').value='user';resetAndLoad();"><div class="val" id="statUsers">--</div><div class="lbl">Active Users</div></div>
        </div>

        <div class="main-grid">
            <!-- Main: filter bar + event list -->
            <div>
                <div class="filter-bar">
                    <select id="filterEntityType" onchange="resetAndLoad()">
                        <option value="">All Types</option>
                        <option value="user">Users</option>
                        <option value="coil">Inventory</option>
                        <option value="project">Projects</option>
                        <option value="customer">Customers</option>
                        <option value="quote">Quotes</option>
                        <option value="work_order">Work Orders</option>
                        <option value="work_order_item">WO Items</option>
                        <option value="inspection">Inspections</option>
                        <option value="ncr">NCRs</option>
                        <option value="traceability">Traceability</option>
                        <option value="shipping">Shipping</option>
                        <option value="shop_drawing">Shop Drawings</option>
                    </select>
                    <input type="text" id="filterUser" placeholder="Filter by user..." style="width:160px;">
                    <button onclick="resetAndLoad()" class="btn btn-secondary" style="padding:6px 12px;">Apply</button>
                </div>

                <div class="event-list-wrapper" style="border:1px solid var(--tf-border);border-radius:var(--tf-radius-lg);">
                    <ul class="event-list" id="eventList">
                        <li class="empty-state">Loading events...</li>
                    </ul>
                </div>

                <div class="pagination" id="pagination"></div>
            </div>

            <!-- Sidebar -->
            <div>
                <div class="panel">
                    <div class="panel-header">Events by Type</div>
                    <div class="panel-body" id="typeBreakdown">
                        <div class="empty-state" style="padding:var(--tf-sp-3)">Loading...</div>
                    </div>
                </div>

                <div class="panel">
                    <div class="panel-header">Top Users</div>
                    <div class="panel-body" id="topUsers">
                        <div class="empty-state" style="padding:var(--tf-sp-3)">Loading...</div>
                    </div>
                </div>

                <div class="panel">
                    <div class="panel-header">Recent Actions</div>
                    <div class="panel-body" id="recentActions">
                        <div class="empty-state" style="padding:var(--tf-sp-3)">Loading...</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
    let currentOffset = 0;
    const PAGE_SIZE = 50;
    let totalEvents = 0;
    let allEntries = [];

    const typeColors = {
        user: 'blue', coil: 'amber', project: 'purple', customer: 'green',
        quote: 'red', allocation: 'blue', system: 'gray'
    };
    const typeIcons = {
        user: 'US', coil: 'IN', project: 'PR', customer: 'CU',
        quote: 'QT', allocation: 'AL', system: 'SY',
        work_order: 'WO', work_order_item: 'WI', inspection: 'QC',
        ncr: 'NC', traceability: 'TR', welder: 'WE', inspector: 'IQ',
        calibration: 'CA', wps: 'WP', shop_drawing: 'SD', load: 'LD',
        shipping: 'SH', tc_quote: 'TC', qc: 'QC'
    };
    const actionLabels = {
        login: 'Logged in', logout: 'Logged out',
        created_user: 'Created user', updated_user: 'Updated user', deleted_user: 'Deleted user',
        created_coil: 'Created coil', updated_coil: 'Updated coil', deleted_coil: 'Deleted coil',
        allocated_inventory: 'Allocated inventory', released_allocation: 'Released allocation',
        received_inventory: 'Received inventory',
        created_customer: 'Created customer', updated_customer: 'Updated customer', deleted_customer: 'Deleted customer',
        saved_quote: 'Saved quote', saved_tc_quote: 'Saved TC quote',
        created_project: 'Created project', updated_project: 'Updated project', deleted_project: 'Deleted project',
        updated_project_status: 'Updated project status',
        uploaded_project_doc: 'Uploaded project doc', deleted_project_doc: 'Deleted project doc',
        uploaded_customer_doc: 'Uploaded customer doc',
        created_work_order: 'Created work order', approved_work_order: 'Approved work order',
        deleted_work_order: 'Deleted work order', edited_work_order: 'Edited work order',
        stickers_printed: 'Stickers printed',
        work_order_hold: 'Put WO on hold', work_order_resume: 'Resumed WO',
        qr_scan_start: 'Started item (QR scan)', qr_scan_finish: 'Finished item (QR scan)',
        batch_scan: 'Batch scan',
        edited_work_order_item: 'Edited WO item',
        qc_inspection: 'QC inspection', created_inspection: 'Created inspection',
        created_ncr: 'Created NCR', updated_ncr: 'Updated NCR',
        loading_update: 'Updated loading status',
        picked_purchased_item: 'Picked purchased item',
        registered_heat_number: 'Registered heat number', assigned_member: 'Assigned member to heat',
        saved_welder_cert: 'Saved welder cert', saved_inspector_qual: 'Saved inspector qualification',
        saved_calibration: 'Saved calibration record', saved_wps: 'Saved WPS',
        deleted_shop_drawing: 'Deleted shop drawing', generated_shop_drawings: 'Generated shop drawings',
        created_load: 'Created load', finalized_load: 'Finalized load',
        generated_packing_list: 'Generated packing list', generated_bol: 'Generated BOL',
        generated_manifest: 'Generated manifest', generated_inspection_report: 'Generated inspection report',
    };

    async function loadAll() {
        await loadEvents();
        computeSidebar();
    }

    function resetAndLoad() {
        currentOffset = 0;
        loadAll();
    }

    async function loadEvents() {
        const entityType = document.getElementById('filterEntityType').value;
        const userFilter = document.getElementById('filterUser').value.trim();

        let url = `/api/activity?limit=${PAGE_SIZE}&offset=${currentOffset}`;
        if (entityType) url += `&entity_type=${encodeURIComponent(entityType)}`;
        if (userFilter) url += `&user=${encodeURIComponent(userFilter)}`;

        try {
            const res = await fetch(url);
            const data = await res.json();
            if (!data.ok) { showEmpty('Failed to load'); return; }
            totalEvents = data.total;
            allEntries = data.entries || [];
            renderEvents(allEntries);
            renderPagination();
            updateStats();
        } catch (e) {
            showEmpty('Failed to load events');
        }
    }

    function showEmpty(msg) {
        document.getElementById('eventList').innerHTML = `<li class="empty-state">${msg}</li>`;
    }

    function formatTime(ts) {
        if (!ts) return '';
        const d = new Date(ts);
        const now = new Date();
        const diff = (now - d) / 1000;
        if (diff < 60) return 'Just now';
        if (diff < 3600) return Math.floor(diff / 60) + 'm ago';
        if (diff < 86400) return Math.floor(diff / 3600) + 'h ago';
        if (diff < 604800) return Math.floor(diff / 86400) + 'd ago';
        return d.toLocaleDateString();
    }

    function renderEvents(entries) {
        const list = document.getElementById('eventList');
        if (!entries.length) { showEmpty('No activity yet'); return; }

        list.innerHTML = entries.map(e => {
            const color = typeColors[e.entity_type] || 'gray';
            const icon = typeIcons[e.entity_type] || '?';
            const label = actionLabels[e.action] || e.action.replace(/_/g, ' ');
            const details = e.details || {};
            let desc = '';
            if (e.entity_id) desc += e.entity_id;
            if (details.name) desc += (desc ? ' - ' : '') + details.name;
            if (details.job_code) desc += (desc ? ' | ' : '') + details.job_code;
            if (details.role) desc += (desc ? ' | role: ' : '') + details.role;
            if (details.quantity) desc += (desc ? ' | ' : '') + details.quantity + ' lbs';

            return `<li class="event-item" onclick="navigateToEntity('${e.entity_type || ''}', '${(e.entity_id || '').replace(/'/g, "\\'")}', ${JSON.stringify(details).replace(/"/g, '&quot;')})">
                <div class="event-icon ${color}">${icon}</div>
                <div class="event-body">
                    <div class="event-title">${label}</div>
                    ${desc ? `<div class="event-desc">${desc}</div>` : ''}
                    <div class="event-meta">
                        <span class="event-badge ${e.entity_type || 'system'}">${e.entity_type || 'system'}</span>
                        <span>${e.user}</span>
                        <span>${formatTime(e.timestamp)}</span>
                        ${e.ip_address ? `<span>${e.ip_address}</span>` : ''}
                    </div>
                </div>
            </li>`;
        }).join('');
    }

    function renderPagination() {
        const pg = document.getElementById('pagination');
        const pages = Math.ceil(totalEvents / PAGE_SIZE);
        const current = Math.floor(currentOffset / PAGE_SIZE);
        pg.innerHTML = `
            <button onclick="goPage(${current - 1})" ${current === 0 ? 'disabled' : ''}>Prev</button>
            <span class="info">Page ${current + 1} of ${Math.max(pages, 1)} (${totalEvents} events)</span>
            <button onclick="goPage(${current + 1})" ${current >= pages - 1 ? 'disabled' : ''}>Next</button>
        `;
    }

    function goPage(page) {
        currentOffset = Math.max(0, page * PAGE_SIZE);
        loadEvents();
    }

    function updateStats() {
        document.getElementById('statTotal').textContent = totalEvents;
        const today = new Date().toISOString().split('T')[0];
        const todayCount = allEntries.filter(e => e.timestamp && e.timestamp.startsWith(today)).length;
        document.getElementById('statToday').textContent = todayCount;

        const types = new Set(allEntries.map(e => e.entity_type).filter(Boolean));
        document.getElementById('statTypes').textContent = types.size;

        const users = new Set(allEntries.map(e => e.user).filter(Boolean));
        document.getElementById('statUsers').textContent = users.size;
    }

    function computeSidebar() {
        // Type breakdown
        const typeCounts = {};
        const userCounts = {};
        const actionCounts = {};
        allEntries.forEach(e => {
            const t = e.entity_type || 'system';
            typeCounts[t] = (typeCounts[t] || 0) + 1;
            userCounts[e.user] = (userCounts[e.user] || 0) + 1;
            actionCounts[e.action] = (actionCounts[e.action] || 0) + 1;
        });

        const typeEl = document.getElementById('typeBreakdown');
        const typeEntries = Object.entries(typeCounts).sort((a,b) => b[1] - a[1]);
        if (typeEntries.length) {
            typeEl.innerHTML = typeEntries.map(([t, c]) => {
                const color = typeColors[t] || '#94a3b8';
                return `<div class="cat-row"><span><span class="cat-dot" style="background:${color === 'blue' ? '#3b82f6' : color === 'amber' ? '#f59e0b' : color === 'green' ? '#10b981' : color === 'purple' ? '#8b5cf6' : color === 'red' ? '#ef4444' : '#94a3b8'}"></span>${t}</span><span class="v">${c}</span></div>`;
            }).join('');
        } else {
            typeEl.innerHTML = '<div class="empty-state" style="padding:var(--tf-sp-3)">No data</div>';
        }

        const userEl = document.getElementById('topUsers');
        const userEntries = Object.entries(userCounts).sort((a,b) => b[1] - a[1]).slice(0, 10);
        if (userEntries.length) {
            userEl.innerHTML = userEntries.map(([u, c]) =>
                `<div class="cat-row"><span>${u}</span><span class="v">${c}</span></div>`
            ).join('');
        } else {
            userEl.innerHTML = '<div class="empty-state" style="padding:var(--tf-sp-3)">No users</div>';
        }

        const actEl = document.getElementById('recentActions');
        const actEntries = Object.entries(actionCounts).sort((a,b) => b[1] - a[1]).slice(0, 10);
        if (actEntries.length) {
            actEl.innerHTML = actEntries.map(([a, c]) => {
                const label = actionLabels[a] || a.replace(/_/g, ' ');
                return `<div class="cat-row"><span>${label}</span><span class="v">${c}</span></div>`;
            }).join('');
        } else {
            actEl.innerHTML = '<div class="empty-state" style="padding:var(--tf-sp-3)">No actions</div>';
        }
    }

    function navigateToEntity(type, id, details) {
        const jc = details && details.job_code ? details.job_code : '';
        const routes = {
            project: '/project/' + encodeURIComponent(id || jc),
            customer: '/customers/' + encodeURIComponent(id),
            coil: '/inventory',
            quote: jc ? '/project/' + encodeURIComponent(jc) : '/projects',
            work_order: jc ? '/work-orders/' + encodeURIComponent(jc) : '/work-orders',
            work_order_item: jc ? '/work-orders/' + encodeURIComponent(jc) : '/work-orders',
            inspection: jc ? '/qc/' + encodeURIComponent(jc) : '/qc-dashboard',
            ncr: jc ? '/qc/' + encodeURIComponent(jc) + '#ncrs' : '/qc-dashboard',
            traceability: jc ? '/qc/' + encodeURIComponent(jc) : '/inventory/traceability',
            shipping: jc ? '/project/' + encodeURIComponent(jc) : '/shipping',
            shop_drawing: jc ? '/shop-drawings/' + encodeURIComponent(jc) : '/shop-drawings',
            user: '/admin/users',
            welder: '/qa/welder-certs',
            inspector: '/qa/inspector-registry',
            calibration: '/qa/calibration',
            wps: '/qa/wps',
        };
        const url = routes[type];
        if (url) window.location.href = url;
    }

    loadAll();
    setInterval(loadAll, 30000);
    </script>
</body>
</html>
"""
