"""
TitanForge v3.0 — Projects List Page
======================================
Dedicated page listing all projects in a filterable, sortable table
with status badges, progress indicators, and quick action buttons.
"""
from templates.shared_styles import DESIGN_SYSTEM_CSS

PROJECTS_LIST_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TitanForge — Projects</title>
    <style>
""" + DESIGN_SYSTEM_CSS + r"""

        /* ── Dark theme overrides ─────────────────────────────── */
        :root {
            --pl-bg:       #0F172A;
            --pl-card:     #1E293B;
            --pl-border:   #334155;
            --pl-text:     #E2E8F0;
            --pl-text-dim: #94A3B8;
            --pl-hover:    #263548;
        }

        body {
            background: var(--pl-bg);
            color: var(--pl-text);
            font-family: var(--tf-font);
            margin: 0;
        }

        .container {
            max-width: 1500px;
            margin: 0 auto;
            padding: var(--tf-sp-6) var(--tf-sp-8);
        }

        /* ── Page header ─────────────────────────────────────── */
        .page-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--tf-sp-6);
            flex-wrap: wrap;
            gap: var(--tf-sp-4);
        }
        .page-header h1 {
            font-size: var(--tf-text-2xl);
            font-weight: 800;
            color: #F8FAFC;
            margin: 0;
            display: flex;
            align-items: center;
            gap: var(--tf-sp-3);
        }
        .page-header h1 .icon {
            width: 36px; height: 36px;
            background: linear-gradient(135deg, #F59E0B 0%, #F97316 100%);
            border-radius: 8px;
            display: flex; align-items: center; justify-content: center;
            font-size: 18px;
        }
        .project-count {
            font-size: var(--tf-text-sm);
            color: var(--pl-text-dim);
            font-weight: 400;
            margin-left: var(--tf-sp-2);
        }
        .header-actions {
            display: flex;
            gap: var(--tf-sp-3);
        }
        .btn-new-project {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 10px 20px;
            background: linear-gradient(135deg, #F59E0B 0%, #F97316 100%);
            color: #0F172A;
            border: none;
            border-radius: var(--tf-radius);
            font-size: var(--tf-text-sm);
            font-weight: 700;
            cursor: pointer;
            transition: all var(--tf-duration) var(--tf-ease);
        }
        .btn-new-project:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
        }

        /* ── Toolbar (search + filters) ──────────────────────── */
        .toolbar {
            display: flex;
            gap: var(--tf-sp-3);
            align-items: center;
            margin-bottom: var(--tf-sp-5);
            flex-wrap: wrap;
        }
        .search-wrap {
            position: relative;
            flex: 1;
            min-width: 280px;
        }
        .search-wrap::before {
            content: '\1F50D';
            position: absolute;
            left: 14px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 14px;
            opacity: 0.5;
        }
        .search-box {
            width: 100%;
            padding: 10px 16px 10px 42px;
            border: 1px solid var(--pl-border);
            border-radius: var(--tf-radius);
            font-size: var(--tf-text-base);
            background: var(--pl-card);
            color: var(--pl-text);
            transition: border-color var(--tf-duration) var(--tf-ease);
        }
        .search-box:focus {
            outline: none;
            border-color: var(--tf-amber);
            box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.15);
        }
        .search-box::placeholder {
            color: var(--pl-text-dim);
        }
        .stage-filter {
            padding: 8px 16px;
            border: 1px solid var(--pl-border);
            border-radius: var(--tf-radius);
            background: var(--pl-card);
            color: var(--pl-text-dim);
            font-size: var(--tf-text-sm);
            cursor: pointer;
            transition: all var(--tf-duration) var(--tf-ease);
            font-weight: 600;
        }
        .stage-filter:hover {
            border-color: var(--pl-text-dim);
        }
        .stage-filter.active {
            background: var(--tf-amber);
            color: #0F172A;
            border-color: var(--tf-amber);
        }
        .sort-select {
            padding: 8px 14px;
            border: 1px solid var(--pl-border);
            border-radius: var(--tf-radius);
            background: var(--pl-card);
            color: var(--pl-text);
            font-size: var(--tf-text-sm);
            cursor: pointer;
        }
        .sort-select:focus { outline: none; border-color: var(--tf-amber); }

        /* ── Stats bar ───────────────────────────────────────── */
        .stats-bar {
            display: flex;
            gap: var(--tf-sp-4);
            margin-bottom: var(--tf-sp-5);
            flex-wrap: wrap;
        }
        .stat-card {
            flex: 1;
            min-width: 140px;
            background: var(--pl-card);
            border: 1px solid var(--pl-border);
            border-radius: var(--tf-radius-lg);
            padding: var(--tf-sp-4) var(--tf-sp-5);
            text-align: center;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .stat-card:hover {
            border-color: var(--tf-amber);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(245, 158, 11, 0.15);
        }
        .stat-card .stat-value {
            font-size: var(--tf-text-2xl);
            font-weight: 800;
            color: #F8FAFC;
        }
        .stat-card .stat-label {
            font-size: var(--tf-text-xs);
            color: var(--pl-text-dim);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 2px;
        }

        /* ── Table wrapper ───────────────────────────────────── */
        .table-card {
            background: var(--pl-card);
            border: 1px solid var(--pl-border);
            border-radius: var(--tf-radius-lg);
            overflow: hidden;
        }
        .projects-table {
            width: 100%;
            border-collapse: collapse;
            font-size: var(--tf-text-sm);
        }
        .projects-table thead {
            background: rgba(15, 23, 42, 0.5);
        }
        .projects-table th {
            padding: 12px 16px;
            text-align: left;
            font-weight: 700;
            color: var(--pl-text-dim);
            font-size: var(--tf-text-xs);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border-bottom: 1px solid var(--pl-border);
            cursor: pointer;
            user-select: none;
            white-space: nowrap;
        }
        .projects-table th:hover {
            color: var(--pl-text);
        }
        .projects-table th .sort-arrow {
            display: inline-block;
            margin-left: 4px;
            opacity: 0.3;
            font-size: 10px;
        }
        .projects-table th.sorted .sort-arrow {
            opacity: 1;
            color: var(--tf-amber);
        }
        .projects-table td {
            padding: 14px 16px;
            border-bottom: 1px solid rgba(51, 65, 85, 0.5);
            vertical-align: middle;
        }
        .projects-table tbody tr {
            transition: background var(--tf-duration) var(--tf-ease);
            cursor: pointer;
        }
        .projects-table tbody tr:hover {
            background: var(--pl-hover);
        }
        .projects-table tbody tr:last-child td {
            border-bottom: none;
        }

        /* ── Job code link ───────────────────────────────────── */
        .job-code-link {
            color: var(--tf-amber);
            text-decoration: none;
            font-weight: 700;
            font-family: var(--tf-font-mono);
            font-size: var(--tf-text-sm);
        }
        .job-code-link:hover {
            text-decoration: underline;
        }

        /* ── Project name ────────────────────────────────────── */
        .project-name {
            font-weight: 600;
            color: #F8FAFC;
        }
        .project-name-link {
            color: #F8FAFC;
            text-decoration: none;
            font-weight: 600;
        }
        .project-name-link:hover {
            color: var(--tf-amber);
            text-decoration: underline;
        }
        .project-customer {
            font-size: var(--tf-text-xs);
            color: var(--pl-text-dim);
            margin-top: 2px;
        }
        .customer-link {
            color: var(--pl-text-dim);
            text-decoration: none;
            cursor: pointer;
        }
        .customer-link:hover {
            color: #60A5FA;
            text-decoration: underline;
        }

        /* ── Status badges ───────────────────────────────────── */
        .stage-badge {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            white-space: nowrap;
            cursor: pointer;
            transition: opacity 0.2s ease;
        }
        .stage-badge:hover {
            opacity: 0.8;
        }
        .stage-badge.quote       { background: #1E3A5F; color: #60A5FA; }
        .stage-badge.engineering  { background: #312E81; color: #A78BFA; }
        .stage-badge.fabrication  { background: #78350F; color: #FCD34D; }
        .stage-badge.shipping     { background: #064E3B; color: #6EE7B7; }
        .stage-badge.installed    { background: #14532D; color: #4ADE80; }
        .stage-badge.on_hold      { background: #451A03; color: #FB923C; }
        .stage-badge.cancelled    { background: #450A0A; color: #FCA5A5; }
        .stage-badge .badge-dot {
            width: 6px; height: 6px;
            border-radius: 50%;
            background: currentColor;
        }

        /* ── Progress bar ────────────────────────────────────── */
        .progress-cell {
            min-width: 120px;
        }
        .progress-bar-wrap {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .progress-bar {
            flex: 1;
            height: 6px;
            background: rgba(51, 65, 85, 0.6);
            border-radius: 3px;
            overflow: hidden;
        }
        .progress-bar-fill {
            height: 100%;
            border-radius: 3px;
            transition: width 0.5s ease;
        }
        .progress-bar-fill.low    { background: #EF4444; }
        .progress-bar-fill.mid    { background: #F59E0B; }
        .progress-bar-fill.high   { background: #22C55E; }
        .progress-pct {
            font-size: var(--tf-text-xs);
            font-weight: 700;
            min-width: 32px;
            text-align: right;
            color: var(--pl-text-dim);
        }

        /* ── Action buttons ──────────────────────────────────── */
        .action-btns {
            display: flex;
            gap: 6px;
            opacity: 0;
            transition: opacity var(--tf-duration) var(--tf-ease);
        }
        .projects-table tbody tr:hover .action-btns {
            opacity: 1;
        }
        .action-btn {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 5px 10px;
            border: 1px solid var(--pl-border);
            border-radius: var(--tf-radius-sm);
            background: transparent;
            color: var(--pl-text-dim);
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            white-space: nowrap;
            transition: all var(--tf-duration) var(--tf-ease);
        }
        .action-btn:hover {
            background: rgba(245, 158, 11, 0.1);
            color: var(--tf-amber);
            border-color: var(--tf-amber);
        }
        .action-btn.view-quote:hover {
            background: rgba(96, 165, 250, 0.1);
            color: #60A5FA;
            border-color: #60A5FA;
        }
        .action-btn.view-drawings:hover {
            background: rgba(167, 139, 250, 0.1);
            color: #A78BFA;
            border-color: #A78BFA;
        }

        /* ── Date column ─────────────────────────────────────── */
        .date-cell {
            font-size: var(--tf-text-xs);
            color: var(--pl-text-dim);
            white-space: nowrap;
        }

        /* ── Empty state ─────────────────────────────────────── */
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: var(--pl-text-dim);
        }
        .empty-state .empty-icon {
            font-size: 48px;
            margin-bottom: var(--tf-sp-4);
            opacity: 0.4;
        }
        .empty-state h3 {
            font-size: var(--tf-text-lg);
            color: #F8FAFC;
            margin-bottom: var(--tf-sp-2);
        }
        .empty-state p {
            font-size: var(--tf-text-sm);
            max-width: 400px;
            margin: 0 auto;
        }

        /* ── Loading ─────────────────────────────────────────── */
        .loading-spinner {
            text-align: center;
            padding: 60px 20px;
            color: var(--pl-text-dim);
        }
        .loading-spinner .spin {
            display: inline-block;
            width: 32px;
            height: 32px;
            border: 3px solid var(--pl-border);
            border-top-color: var(--tf-amber);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }

        /* ── Responsive ──────────────────────────────────────── */
        @media (max-width: 900px) {
            .container { padding: var(--tf-sp-4); }
            .stats-bar { display: grid; grid-template-columns: repeat(2, 1fr); }
            .projects-table th:nth-child(6),
            .projects-table td:nth-child(6) { display: none; }
            .action-btns { opacity: 1; flex-wrap: wrap; }
        }
        @media (max-width: 600px) {
            .projects-table th:nth-child(3),
            .projects-table td:nth-child(3),
            .projects-table th:nth-child(5),
            .projects-table td:nth-child(5) { display: none; }
        }
    </style>
</head>
<body>
<div class="container">
    <!-- Page Header -->
    <div class="page-header">
        <h1>
            <span class="icon">&#x1F4CB;</span>
            Projects
            <span class="project-count" id="projectCount"></span>
        </h1>
        <div class="header-actions">
            <button class="btn-new-project" onclick="window.location.href='/sa'">
                &#x2795; New Project
            </button>
        </div>
    </div>

    <!-- Stats Bar -->
    <div class="stats-bar" id="statsBar">
        <div class="stat-card" onclick="clickStatFilter('all')" title="Show all projects"><div class="stat-value" id="statTotal">-</div><div class="stat-label">Total Projects</div></div>
        <div class="stat-card" onclick="clickStatFilter('engineering')" title="Filter to Engineering"><div class="stat-value" id="statEngineering">-</div><div class="stat-label">Engineering</div></div>
        <div class="stat-card" onclick="clickStatFilter('fabrication')" title="Filter to Fabrication"><div class="stat-value" id="statFabrication">-</div><div class="stat-label">Fabrication</div></div>
        <div class="stat-card" onclick="clickStatFilter('shipping')" title="Filter to Shipping"><div class="stat-value" id="statShipping">-</div><div class="stat-label">Shipping</div></div>
        <div class="stat-card" onclick="clickStatFilter('installed')" title="Filter to Installed"><div class="stat-value" id="statInstalled">-</div><div class="stat-label">Installed</div></div>
    </div>

    <!-- Toolbar -->
    <div class="toolbar">
        <div class="search-wrap">
            <input type="text" class="search-box" id="searchInput"
                   placeholder="Search by job code, project name, or customer...">
        </div>
        <button class="stage-filter active" data-stage="all" onclick="filterStage(this)">All</button>
        <button class="stage-filter" data-stage="quote" onclick="filterStage(this)">Quote</button>
        <button class="stage-filter" data-stage="engineering" onclick="filterStage(this)">Engineering</button>
        <button class="stage-filter" data-stage="fabrication" onclick="filterStage(this)">Fabrication</button>
        <button class="stage-filter" data-stage="shipping" onclick="filterStage(this)">Shipping</button>
        <button class="stage-filter" data-stage="installed" onclick="filterStage(this)">Installed</button>
        <button class="stage-filter" data-stage="on_hold" onclick="filterStage(this)">On Hold</button>
        <select class="sort-select" id="sortSelect" onchange="applySort()">
            <option value="created_desc">Newest First</option>
            <option value="created_asc">Oldest First</option>
            <option value="name_asc">Name A-Z</option>
            <option value="name_desc">Name Z-A</option>
            <option value="progress_desc">Progress High-Low</option>
            <option value="progress_asc">Progress Low-High</option>
            <option value="stage_asc">Stage</option>
        </select>
    </div>

    <!-- Table -->
    <div class="table-card">
        <div class="loading-spinner" id="loadingSpinner">
            <div class="spin"></div>
            <p style="margin-top:12px;">Loading projects...</p>
        </div>
        <table class="projects-table" id="projectsTable" style="display:none;">
            <thead>
                <tr>
                    <th onclick="sortColumn('job_code')">Job Code <span class="sort-arrow">&#x25B2;</span></th>
                    <th onclick="sortColumn('project_name')">Project / Customer <span class="sort-arrow">&#x25B2;</span></th>
                    <th onclick="sortColumn('customer')">Customer <span class="sort-arrow">&#x25B2;</span></th>
                    <th onclick="sortColumn('stage')">Stage <span class="sort-arrow">&#x25B2;</span></th>
                    <th onclick="sortColumn('progress')">Progress <span class="sort-arrow">&#x25B2;</span></th>
                    <th onclick="sortColumn('created_at')">Created <span class="sort-arrow">&#x25B2;</span></th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody id="projectsBody"></tbody>
        </table>
        <div class="empty-state" id="emptyState" style="display:none;">
            <div class="empty-icon">&#x1F4C2;</div>
            <h3>No projects found</h3>
            <p>Try adjusting your search or filter criteria, or create a new project to get started.</p>
        </div>
    </div>
</div>

<script>
(function() {
    let allProjects = [];
    let currentFilter = 'all';
    let currentSort = 'created_desc';
    let searchQuery = '';

    // ── Stage config ──────────────────────────────────────
    const stageLabels = {
        quote:        'Quote',
        engineering:  'Engineering',
        fabrication:  'Fabrication',
        shipping:     'Shipping',
        installed:    'Installed',
        on_hold:      'On Hold',
        cancelled:    'Cancelled'
    };
    const stageOrder = ['quote','engineering','fabrication','shipping','installed','on_hold','cancelled'];

    // ── Fetch projects ────────────────────────────────────
    async function loadProjects() {
        try {
            const resp = await fetch('/api/projects/full');
            const data = await resp.json();
            if (data.ok && data.projects) {
                allProjects = data.projects;
                updateStats();
                renderTable();
            } else {
                showEmpty();
            }
        } catch (err) {
            console.error('Failed to load projects:', err);
            showEmpty();
        }
    }

    function showEmpty() {
        document.getElementById('loadingSpinner').style.display = 'none';
        document.getElementById('projectsTable').style.display = 'none';
        document.getElementById('emptyState').style.display = 'block';
    }

    // ── Stats ─────────────────────────────────────────────
    function updateStats() {
        const counts = { total: allProjects.length, engineering: 0, fabrication: 0, shipping: 0, installed: 0 };
        allProjects.forEach(p => {
            const s = (p.stage || 'quote').toLowerCase();
            if (counts[s] !== undefined) counts[s]++;
        });
        document.getElementById('statTotal').textContent = counts.total;
        document.getElementById('statEngineering').textContent = counts.engineering;
        document.getElementById('statFabrication').textContent = counts.fabrication;
        document.getElementById('statShipping').textContent = counts.shipping;
        document.getElementById('statInstalled').textContent = counts.installed;
    }

    // ── Calculate progress ────────────────────────────────
    function calcProgress(p) {
        const checklist = p.checklist || {};
        const keys = Object.keys(checklist);
        if (keys.length === 0) {
            // Infer from stage
            const idx = stageOrder.indexOf((p.stage || 'quote').toLowerCase());
            if (idx < 0) return 0;
            return Math.min(100, Math.round((idx / (stageOrder.length - 2)) * 100));
        }
        let done = 0, total = 0;
        keys.forEach(k => {
            const items = checklist[k];
            if (typeof items === 'object' && items !== null) {
                Object.values(items).forEach(v => {
                    total++;
                    if (v === true || v === 'done' || v === 'complete') done++;
                });
            }
        });
        return total > 0 ? Math.round((done / total) * 100) : 0;
    }

    // ── Filtering ─────────────────────────────────────────
    function getFiltered() {
        let list = allProjects;
        if (currentFilter !== 'all') {
            list = list.filter(p => (p.stage || 'quote').toLowerCase() === currentFilter);
        }
        if (searchQuery) {
            const q = searchQuery.toLowerCase();
            list = list.filter(p => {
                const jc = (p.job_code || '').toLowerCase();
                const pn = (p.project_name || '').toLowerCase();
                const cn = ((p.customer && p.customer.name) || '').toLowerCase();
                return jc.includes(q) || pn.includes(q) || cn.includes(q);
            });
        }
        return sortList(list);
    }

    // ── Sorting ───────────────────────────────────────────
    function sortList(list) {
        const arr = [...list];
        switch (currentSort) {
            case 'created_desc':
                arr.sort((a, b) => (b.created_at || '').localeCompare(a.created_at || ''));
                break;
            case 'created_asc':
                arr.sort((a, b) => (a.created_at || '').localeCompare(b.created_at || ''));
                break;
            case 'name_asc':
                arr.sort((a, b) => (a.project_name || '').localeCompare(b.project_name || ''));
                break;
            case 'name_desc':
                arr.sort((a, b) => (b.project_name || '').localeCompare(a.project_name || ''));
                break;
            case 'progress_desc':
                arr.sort((a, b) => calcProgress(b) - calcProgress(a));
                break;
            case 'progress_asc':
                arr.sort((a, b) => calcProgress(a) - calcProgress(b));
                break;
            case 'stage_asc':
                arr.sort((a, b) => stageOrder.indexOf((a.stage||'quote').toLowerCase()) - stageOrder.indexOf((b.stage||'quote').toLowerCase()));
                break;
        }
        return arr;
    }

    // ── Render ─────────────────────────────────────────────
    function renderTable() {
        const filtered = getFiltered();
        const tbody = document.getElementById('projectsBody');
        const table = document.getElementById('projectsTable');
        const spinner = document.getElementById('loadingSpinner');
        const empty = document.getElementById('emptyState');

        spinner.style.display = 'none';

        if (filtered.length === 0) {
            table.style.display = 'none';
            empty.style.display = 'block';
            document.getElementById('projectCount').textContent = '(0)';
            return;
        }

        table.style.display = 'table';
        empty.style.display = 'none';
        document.getElementById('projectCount').textContent = '(' + filtered.length + ' of ' + allProjects.length + ')';

        tbody.innerHTML = filtered.map(p => {
            const jc = escHtml(p.job_code || '');
            const pn = escHtml(p.project_name || '');
            const cn = escHtml((p.customer && p.customer.name) || '—');
            const stage = (p.stage || 'quote').toLowerCase();
            const stageLabel = stageLabels[stage] || stage;
            const progress = calcProgress(p);
            const barClass = progress < 33 ? 'low' : progress < 66 ? 'mid' : 'high';
            const created = formatDate(p.created_at);

            var projectUrl = '/project/' + encodeURIComponent(p.job_code || '');
            var custId = (p.customer && p.customer.id) || '';

            return '<tr onclick="window.location.href=\'' + projectUrl + '\'" title="Click to view project">' +
                '<td><a class="job-code-link" href="' + projectUrl + '" onclick="event.stopPropagation()">' + jc + '</a></td>' +
                '<td><a class="project-name-link" href="' + projectUrl + '" onclick="event.stopPropagation()">' + (pn || '(Untitled)') + '</a></td>' +
                '<td><span class="customer-link" onclick="event.stopPropagation();' + (custId ? 'window.location.href=\'/customers?id=' + encodeURIComponent(custId) + '\'' : '') + '" title="View customer">' + cn + '</span></td>' +
                '<td><span class="stage-badge ' + escHtml(stage) + '" onclick="event.stopPropagation();clickStatFilter(\'' + escHtml(stage) + '\')" title="Filter by ' + escHtml(stageLabel) + '"><span class="badge-dot"></span> ' + escHtml(stageLabel) + '</span></td>' +
                '<td class="progress-cell"><div class="progress-bar-wrap"><div class="progress-bar"><div class="progress-bar-fill ' + barClass + '" style="width:' + progress + '%"></div></div><span class="progress-pct">' + progress + '%</span></div></td>' +
                '<td class="date-cell">' + created + '</td>' +
                '<td><div class="action-btns">' +
                    '<a class="action-btn" href="' + projectUrl + '" onclick="event.stopPropagation()" title="View Project">&#x1F4CB; View</a>' +
                    '<a class="action-btn view-quote" href="/tc?job=' + encodeURIComponent(p.job_code || '') + '" onclick="event.stopPropagation()" title="View Quote">&#x1F4B0; Quote</a>' +
                    '<a class="action-btn view-drawings" href="/shop-drawings/' + encodeURIComponent(p.job_code || '') + '" onclick="event.stopPropagation()" title="View Shop Drawings">&#x1F4D0; Drawings</a>' +
                '</div></td>' +
            '</tr>';
        }).join('');
    }

    // ── Utilities ──────────────────────────────────────────
    function escHtml(s) {
        const d = document.createElement('div');
        d.textContent = s;
        return d.innerHTML;
    }

    function formatDate(iso) {
        if (!iso) return '—';
        try {
            const d = new Date(iso);
            if (isNaN(d.getTime())) return iso.substring(0, 10);
            return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
        } catch (e) {
            return iso.substring(0, 10);
        }
    }

    // ── Global handlers ───────────────────────────────────
    window.filterStage = function(btn) {
        currentFilter = btn.dataset.stage;
        document.querySelectorAll('.stage-filter').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        renderTable();
    };

    window.clickStatFilter = function(stage) {
        currentFilter = stage;
        document.querySelectorAll('.stage-filter').forEach(b => {
            b.classList.toggle('active', b.dataset.stage === stage);
        });
        renderTable();
        document.getElementById('projectsTable').scrollIntoView({ behavior: 'smooth', block: 'start' });
    };

    window.applySort = function() {
        currentSort = document.getElementById('sortSelect').value;
        renderTable();
    };

    window.sortColumn = function(col) {
        const map = {
            job_code: 'name_asc',
            project_name: 'name_asc',
            customer: 'name_asc',
            stage: 'stage_asc',
            progress: 'progress_desc',
            created_at: 'created_desc'
        };
        const target = map[col] || 'created_desc';
        if (currentSort === target) {
            // Toggle direction
            if (target.endsWith('_asc')) currentSort = target.replace('_asc', '_desc');
            else currentSort = target.replace('_desc', '_asc');
        } else {
            currentSort = target;
        }
        document.getElementById('sortSelect').value = currentSort;
        renderTable();
    };

    // ── Search debounce ───────────────────────────────────
    let searchTimer = null;
    document.getElementById('searchInput').addEventListener('input', function() {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(() => {
            searchQuery = this.value.trim();
            renderTable();
        }, 200);
    });

    // ── Init ──────────────────────────────────────────────
    loadProjects();
})();
</script>
</body>
</html>
"""
