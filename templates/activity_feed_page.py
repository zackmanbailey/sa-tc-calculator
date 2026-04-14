"""
TitanForge v4 — Activity Feed & Audit Trail Dashboard
=======================================================
Filterable timeline of all system events. Shows recent activity,
category/severity breakdowns, event statistics, and alert rule management.
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
        .stat-row { display: grid; grid-template-columns: repeat(5, 1fr); gap: var(--tf-sp-4); margin-bottom: var(--tf-sp-6); }
        .stat-card {
            background: var(--tf-surface); border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-lg); padding: var(--tf-sp-4); text-align: center;
        }
        .stat-card .val { font-size: var(--tf-text-2xl); font-weight: 800; }
        .stat-card .lbl { font-size: var(--tf-text-xs); color: var(--tf-gray-500); text-transform: uppercase; letter-spacing: 0.04em; margin-top: 2px; }
        .stat-card.blue .val { color: var(--tf-blue); }
        .stat-card.green .val { color: var(--tf-success); }
        .stat-card.amber .val { color: var(--tf-amber); }
        .stat-card.red .val { color: var(--tf-danger); }
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
        .event-badge.info { background: #dbeafe; color: #1e40af; }
        .event-badge.warning { background: #fef3c7; color: #92400e; }
        .event-badge.critical { background: #fee2e2; color: #991b1b; }
        .event-badge.success { background: #d1fae5; color: #065f46; }

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
            .stat-row { grid-template-columns: repeat(3, 1fr); }
            .main-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="top-bar">
            <h1>Activity Feed</h1>
            <div class="actions">
                <a href="/reports/executive" class="btn btn-secondary">Executive Summary</a>
                <button onclick="loadAll()" class="btn btn-primary">Refresh</button>
            </div>
        </div>

        <!-- Stat cards -->
        <div class="stat-row">
            <div class="stat-card blue"><div class="val" id="statTotal">—</div><div class="lbl">Events (Period)</div></div>
            <div class="stat-card green"><div class="val" id="statSuccess">—</div><div class="lbl">Success</div></div>
            <div class="stat-card amber"><div class="val" id="statWarning">—</div><div class="lbl">Warnings</div></div>
            <div class="stat-card red"><div class="val" id="statCritical">—</div><div class="lbl">Critical</div></div>
            <div class="stat-card purple"><div class="val" id="statAllTime">—</div><div class="lbl">All-Time Events</div></div>
        </div>

        <div class="main-grid">
            <!-- Main: filter bar + event list -->
            <div>
                <div class="filter-bar">
                    <select id="filterCategory" onchange="loadEvents()">
                        <option value="">All Categories</option>
                    </select>
                    <select id="filterSeverity" onchange="loadEvents()">
                        <option value="">All Severities</option>
                        <option value="info">Info</option>
                        <option value="success">Success</option>
                        <option value="warning">Warning</option>
                        <option value="critical">Critical</option>
                    </select>
                    <select id="filterProject" onchange="loadEvents()">
                        <option value="">All Projects</option>
                    </select>
                    <input type="text" id="filterActor" placeholder="Filter by user..." onchange="loadEvents()">
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
                    <div class="panel-header">Events by Category</div>
                    <div class="panel-body" id="catBreakdown">
                        <div class="empty-state" style="padding:var(--tf-sp-3)">Loading...</div>
                    </div>
                </div>

                <div class="panel">
                    <div class="panel-header">Top Users (Period)</div>
                    <div class="panel-body" id="topUsers">
                        <div class="empty-state" style="padding:var(--tf-sp-3)">Loading...</div>
                    </div>
                </div>

                <div class="panel">
                    <div class="panel-header">Events per Day</div>
                    <div class="panel-body" id="dailyChart">
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

    const catColors = {
        work_order: 'blue', qc: 'purple', shipping: 'amber', field: 'green',
        punch: 'red', project: 'blue', user: 'gray', system: 'gray', inventory: 'amber'
    };
    const catLabels = {
        work_order: 'Work Order', qc: 'Quality Control', shipping: 'Shipping',
        field: 'Field Ops', punch: 'Punch List', project: 'Project',
        user: 'User', system: 'System', inventory: 'Inventory'
    };
    const iconMap = {
        work_order: 'WO', qc: 'QC', shipping: 'SH', field: 'FD',
        punch: 'PL', project: 'PR', user: 'US', system: 'SY', inventory: 'IN'
    };

    async function loadAll() {
        await Promise.all([loadEvents(), loadStats()]);
    }

    async function loadEvents() {
        const cat = document.getElementById('filterCategory').value;
        const sev = document.getElementById('filterSeverity').value;
        const proj = document.getElementById('filterProject').value;
        const actor = document.getElementById('filterActor').value;

        let url = `/api/activity/events?limit=${PAGE_SIZE}&offset=${currentOffset}`;
        if (cat) url += `&category=${cat}`;
        if (sev) url += `&severity=${sev}`;
        if (proj) url += `&job_code=${proj}`;
        if (actor) url += `&actor=${actor}`;

        try {
            const res = await fetch(url);
            const data = await res.json();
            if (!data.ok) return;
            totalEvents = data.total;
            renderEvents(data.events);
            renderPagination();
        } catch (e) {
            document.getElementById('eventList').innerHTML =
                '<li class="empty-state">Failed to load events</li>';
        }
    }

    async function loadStats() {
        try {
            const res = await fetch('/api/activity/stats?days=7');
            const data = await res.json();
            if (!data.ok) return;
            renderStats(data.stats);
        } catch (e) {}
    }

    function renderEvents(events) {
        const list = document.getElementById('eventList');
        if (!events.length) {
            list.innerHTML = '<li class="empty-state">No events found</li>';
            return;
        }

        list.innerHTML = events.map(e => {
            const color = catColors[e.category] || 'gray';
            const icon = iconMap[e.category] || '?';
            const ts = e.timestamp ? new Date(e.timestamp).toLocaleString() : '';
            return `<li class="event-item">
                <div class="event-icon ${color}">${icon}</div>
                <div class="event-body">
                    <div class="event-title">${e.title || e.event_type}</div>
                    ${e.description ? `<div class="event-desc">${e.description}</div>` : ''}
                    <div class="event-meta">
                        <span class="event-badge ${e.severity}">${e.severity}</span>
                        <span>${catLabels[e.category] || e.category}</span>
                        ${e.job_code ? `<span>${e.job_code}</span>` : ''}
                        <span>${e.actor || ''}</span>
                        <span>${ts}</span>
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

    function renderStats(stats) {
        document.getElementById('statTotal').textContent = stats.total_events || 0;
        document.getElementById('statAllTime').textContent = stats.total_all_time || 0;
        document.getElementById('statSuccess').textContent = stats.by_severity?.success || 0;
        document.getElementById('statWarning').textContent = stats.by_severity?.warning || 0;
        document.getElementById('statCritical').textContent = stats.by_severity?.critical || 0;

        // Category breakdown
        const cats = stats.by_category || {};
        if (Object.keys(cats).length > 0) {
            document.getElementById('catBreakdown').innerHTML = Object.entries(cats)
                .sort((a, b) => b[1] - a[1])
                .map(([cat, count]) => {
                    const color = catColors[cat] || 'gray';
                    const label = catLabels[cat] || cat;
                    return `<div class="cat-row">
                        <span><span class="cat-dot" style="background:var(--tf-${color === 'gray' ? 'gray-400' : color})"></span>${label}</span>
                        <span class="v">${count}</span>
                    </div>`;
                }).join('');
        } else {
            document.getElementById('catBreakdown').innerHTML =
                '<div class="empty-state" style="padding:var(--tf-sp-3)">No events yet</div>';
        }

        // Top users
        const users = stats.by_actor || {};
        if (Object.keys(users).length > 0) {
            document.getElementById('topUsers').innerHTML = Object.entries(users)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 10)
                .map(([user, count]) =>
                    `<div class="cat-row"><span>${user}</span><span class="v">${count}</span></div>`
                ).join('');
        } else {
            document.getElementById('topUsers').innerHTML =
                '<div class="empty-state" style="padding:var(--tf-sp-3)">No user data</div>';
        }

        // Daily chart (simple bars)
        const days = stats.by_day || {};
        const dayEntries = Object.entries(days).sort();
        if (dayEntries.length > 0) {
            const maxDay = Math.max(...dayEntries.map(d => d[1]), 1);
            document.getElementById('dailyChart').innerHTML =
                '<div style="display:flex;align-items:flex-end;gap:2px;height:80px;">' +
                dayEntries.map(([day, count]) => {
                    const h = Math.max((count / maxDay) * 70, 2);
                    return `<div style="flex:1;height:${h}px;background:var(--tf-blue-mid);border-radius:2px 2px 0 0;" title="${day}: ${count}"></div>`;
                }).join('') + '</div>';
        } else {
            document.getElementById('dailyChart').innerHTML =
                '<div class="empty-state" style="padding:var(--tf-sp-3)">No daily data</div>';
        }

        // Populate category filter
        const catSelect = document.getElementById('filterCategory');
        if (catSelect.options.length <= 1) {
            Object.entries(catLabels).forEach(([k, v]) => {
                catSelect.innerHTML += `<option value="${k}">${v}</option>`;
            });
        }
    }

    loadAll();
    setInterval(loadAll, 30000);
    </script>
</body>
</html>
"""
