"""
TitanForge v3.0 — Shop Drawings Landing Page
===============================================
Project selector grid at /shop-drawings (no job code).
Fetches all projects from /api/projects/full and displays
cards with drawing counts, status, and search/filter.
"""

from templates.shared_styles import DESIGN_SYSTEM_CSS

SHOP_DRAWINGS_LANDING_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TitanForge — Shop Drawings</title>
    <style>
""" + DESIGN_SYSTEM_CSS + r"""

        /* ── Page Layout ─────────────────────────────────────── */
        .container {
            max-width: 1440px;
            margin: 0 auto;
            padding: 24px 32px;
        }

        /* ── Page Header ─────────────────────────────────────── */
        .page-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 32px;
            flex-wrap: wrap;
            gap: 16px;
        }
        .page-header h1 {
            font-size: 28px;
            font-weight: 700;
            color: #F8FAFC;
            letter-spacing: -0.02em;
            margin: 0;
        }
        .page-header .subtitle {
            color: #94A3B8;
            font-size: 14px;
            margin-top: 4px;
        }

        /* ── Search & Filter Bar ─────────────────────────────── */
        .controls-bar {
            display: flex;
            gap: 12px;
            align-items: center;
            flex-wrap: wrap;
            margin-bottom: 24px;
        }
        .search-box {
            flex: 1;
            min-width: 240px;
            max-width: 420px;
            position: relative;
        }
        .search-box input {
            width: 100%;
            padding: 10px 14px 10px 40px;
            background: #1E293B;
            border: 1px solid #334155;
            border-radius: 8px;
            color: #F8FAFC;
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s;
            box-sizing: border-box;
        }
        .search-box input:focus {
            border-color: #3B82F6;
        }
        .search-box input::placeholder {
            color: #64748B;
        }
        .search-box .search-icon {
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            color: #64748B;
            pointer-events: none;
        }
        .filter-select {
            padding: 10px 14px;
            background: #1E293B;
            border: 1px solid #334155;
            border-radius: 8px;
            color: #F8FAFC;
            font-size: 14px;
            outline: none;
            cursor: pointer;
        }
        .filter-select:focus {
            border-color: #3B82F6;
        }

        /* ── Stats Summary ───────────────────────────────────── */
        .stats-row {
            display: flex;
            gap: 16px;
            margin-bottom: 28px;
            flex-wrap: wrap;
        }
        .stat-chip {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: #1E293B;
            border: 1px solid #334155;
            border-radius: 8px;
            font-size: 13px;
            color: #CBD5E1;
        }
        .stat-chip .stat-value {
            font-weight: 700;
            font-size: 16px;
            color: #F8FAFC;
        }

        /* ── Project Cards Grid ──────────────────────────────── */
        .projects-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 20px;
        }
        .project-card {
            background: #1E293B;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 24px;
            text-decoration: none;
            color: inherit;
            transition: border-color 0.2s, box-shadow 0.2s, transform 0.15s;
            display: flex;
            flex-direction: column;
            gap: 16px;
            cursor: pointer;
        }
        .project-card:hover {
            border-color: #3B82F6;
            box-shadow: 0 0 0 1px #3B82F6, 0 8px 24px rgba(59, 130, 246, 0.10);
            transform: translateY(-2px);
        }
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 12px;
        }
        .card-header h3 {
            margin: 0;
            font-size: 16px;
            font-weight: 600;
            color: #F8FAFC;
            line-height: 1.3;
        }
        .job-code-badge {
            flex-shrink: 0;
            padding: 4px 10px;
            background: rgba(59, 130, 246, 0.15);
            color: #3B82F6;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            font-family: monospace;
            letter-spacing: 0.02em;
        }
        .card-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            font-size: 13px;
            color: #94A3B8;
        }
        .card-meta span {
            display: flex;
            align-items: center;
            gap: 5px;
        }

        /* ── Drawing Status Bar ──────────────────────────────── */
        .drawing-status {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .drawing-count {
            font-size: 13px;
            color: #CBD5E1;
            white-space: nowrap;
        }
        .drawing-count strong {
            color: #F8FAFC;
            font-weight: 700;
        }
        .status-badge {
            padding: 3px 10px;
            border-radius: 9999px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        .status-badge.has-drawings {
            background: rgba(5, 150, 105, 0.15);
            color: #34D399;
        }
        .status-badge.no-drawings {
            background: rgba(148, 163, 184, 0.12);
            color: #94A3B8;
        }
        .status-badge.in-progress {
            background: rgba(245, 158, 11, 0.15);
            color: #FBBF24;
        }

        /* ── Stage indicator ─────────────────────────────────── */
        .stage-pill {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 3px 10px;
            border-radius: 9999px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        .stage-pill.stage-design      { background: rgba(99,102,241,.15); color: #A5B4FC; }
        .stage-pill.stage-engineering  { background: rgba(59,130,246,.15); color: #93C5FD; }
        .stage-pill.stage-shop_drawings,
        .stage-pill.stage-shop-drawings { background: rgba(245,158,11,.15); color: #FBBF24; }
        .stage-pill.stage-production   { background: rgba(16,185,129,.15); color: #6EE7B7; }
        .stage-pill.stage-fabrication  { background: rgba(16,185,129,.15); color: #6EE7B7; }
        .stage-pill.stage-shipping     { background: rgba(139,92,246,.15); color: #C4B5FD; }
        .stage-pill.stage-complete     { background: rgba(5,150,105,.15);  color: #34D399; }
        .stage-pill.stage-default      { background: rgba(148,163,184,.12); color: #94A3B8; }

        /* ── Progress Bar ────────────────────────────────────── */
        .progress-track {
            flex: 1;
            height: 6px;
            background: #334155;
            border-radius: 3px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            border-radius: 3px;
            background: linear-gradient(90deg, #3B82F6, #2563EB);
            transition: width 0.4s ease;
        }
        .progress-fill.complete {
            background: linear-gradient(90deg, #059669, #34D399);
        }

        /* ── Empty State ─────────────────────────────────────── */
        .empty-state {
            text-align: center;
            padding: 80px 20px;
            color: #64748B;
        }
        .empty-state svg {
            width: 64px;
            height: 64px;
            margin-bottom: 16px;
            opacity: 0.5;
        }
        .empty-state h3 {
            color: #94A3B8;
            font-size: 18px;
            margin: 0 0 8px;
        }
        .empty-state p {
            font-size: 14px;
            max-width: 400px;
            margin: 0 auto;
        }

        /* ── Loading Skeleton ────────────────────────────────── */
        .skeleton-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 20px;
        }
        .skeleton-card {
            background: #1E293B;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 24px;
            height: 160px;
        }
        .skeleton-line {
            height: 14px;
            border-radius: 4px;
            background: linear-gradient(90deg, #334155 25%, #3d4f65 50%, #334155 75%);
            background-size: 200% 100%;
            animation: shimmer 1.5s ease-in-out infinite;
            margin-bottom: 12px;
        }
        .skeleton-line.w60 { width: 60%; }
        .skeleton-line.w40 { width: 40%; }
        .skeleton-line.w80 { width: 80%; }
        .skeleton-line.w30 { width: 30%; height: 10px; }
        @keyframes shimmer {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }

        /* ── Responsive ──────────────────────────────────────── */
        @media (max-width: 768px) {
            .container { padding: 16px; }
            .projects-grid { grid-template-columns: 1fr; }
            .page-header { flex-direction: column; align-items: flex-start; }
            .stats-row { gap: 8px; }
        }

        body {
            background: #0F172A;
            color: #F8FAFC;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            margin: 0; padding: 0;
        }
    </style>
</head>
<body>
<div class="container">
    <!-- Header -->
    <div class="page-header">
        <div>
            <h1>Shop Drawings</h1>
            <div class="subtitle">Select a project to view or manage shop drawings</div>
        </div>
    </div>

    <!-- Stats Summary -->
    <div class="stats-row" id="statsRow" style="display:none;">
        <div class="stat-chip">
            <span>Total Projects</span>
            <span class="stat-value" id="statTotal">0</span>
        </div>
        <div class="stat-chip">
            <span>With Drawings</span>
            <span class="stat-value" id="statWithDrawings">0</span>
        </div>
        <div class="stat-chip">
            <span>Total Drawings</span>
            <span class="stat-value" id="statDrawingCount">0</span>
        </div>
    </div>

    <!-- Search & Filter -->
    <div class="controls-bar">
        <div class="search-box">
            <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
            </svg>
            <input type="text" id="searchInput" placeholder="Search by project name, job code, or customer...">
        </div>
        <select class="filter-select" id="stageFilter">
            <option value="">All Stages</option>
            <option value="design">Design</option>
            <option value="engineering">Engineering</option>
            <option value="shop_drawings">Shop Drawings</option>
            <option value="production">Production</option>
            <option value="fabrication">Fabrication</option>
            <option value="shipping">Shipping</option>
            <option value="complete">Complete</option>
        </select>
        <select class="filter-select" id="drawingFilter">
            <option value="">All</option>
            <option value="has">Has Drawings</option>
            <option value="none">No Drawings</option>
        </select>
    </div>

    <!-- Loading State -->
    <div id="loadingState" class="skeleton-grid">
        <div class="skeleton-card"><div class="skeleton-line w60"></div><div class="skeleton-line w40"></div><div class="skeleton-line w80"></div><div class="skeleton-line w30"></div></div>
        <div class="skeleton-card"><div class="skeleton-line w60"></div><div class="skeleton-line w40"></div><div class="skeleton-line w80"></div><div class="skeleton-line w30"></div></div>
        <div class="skeleton-card"><div class="skeleton-line w60"></div><div class="skeleton-line w40"></div><div class="skeleton-line w80"></div><div class="skeleton-line w30"></div></div>
        <div class="skeleton-card"><div class="skeleton-line w60"></div><div class="skeleton-line w40"></div><div class="skeleton-line w80"></div><div class="skeleton-line w30"></div></div>
        <div class="skeleton-card"><div class="skeleton-line w60"></div><div class="skeleton-line w40"></div><div class="skeleton-line w80"></div><div class="skeleton-line w30"></div></div>
        <div class="skeleton-card"><div class="skeleton-line w60"></div><div class="skeleton-line w40"></div><div class="skeleton-line w80"></div><div class="skeleton-line w30"></div></div>
    </div>

    <!-- Projects Grid -->
    <div class="projects-grid" id="projectsGrid" style="display:none;"></div>

    <!-- Empty State -->
    <div class="empty-state" id="emptyState" style="display:none;">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>
        </svg>
        <h3 id="emptyTitle">No projects found</h3>
        <p id="emptyMsg">Try adjusting your search or filter criteria.</p>
    </div>
</div>

<script>
(function() {
    let allProjects = [];

    async function loadProjects() {
        try {
            const resp = await fetch('/api/projects/full');
            const data = await resp.json();
            allProjects = data.projects || data || [];
            document.getElementById('loadingState').style.display = 'none';
            renderStats();
            renderGrid();
        } catch (err) {
            console.error('Failed to load projects:', err);
            document.getElementById('loadingState').style.display = 'none';
            showEmpty('Error loading projects', 'Could not fetch project data. Please try refreshing the page.');
        }
    }

    function getDrawingCount(p) {
        // Check multiple possible locations for drawing count
        if (p.assets && p.assets.shop_drawings) {
            return p.assets.shop_drawings.count || 0;
        }
        if (p.drawing_count !== undefined) return p.drawing_count;
        if (p.shop_drawings_count !== undefined) return p.shop_drawings_count;
        return 0;
    }

    function getDrawingStatus(p) {
        const count = getDrawingCount(p);
        const stage = (p.stage || p.status || '').toLowerCase();
        if (count > 0) return 'has-drawings';
        if (stage === 'shop_drawings' || stage === 'shop-drawings') return 'in-progress';
        return 'no-drawings';
    }

    function renderStats() {
        const total = allProjects.length;
        let withDrawings = 0, totalDrawings = 0;
        allProjects.forEach(p => {
            const c = getDrawingCount(p);
            if (c > 0) withDrawings++;
            totalDrawings += c;
        });
        document.getElementById('statTotal').textContent = total;
        document.getElementById('statWithDrawings').textContent = withDrawings;
        document.getElementById('statDrawingCount').textContent = totalDrawings;
        document.getElementById('statsRow').style.display = 'flex';
    }

    function getFilteredProjects() {
        const query = (document.getElementById('searchInput').value || '').toLowerCase().trim();
        const stageFilter = document.getElementById('stageFilter').value;
        const drawingFilter = document.getElementById('drawingFilter').value;

        return allProjects.filter(p => {
            const name = (p.project_name || p.name || '').toLowerCase();
            const code = (p.job_code || '').toLowerCase();
            const custRaw = p.customer_name || p.customer || '';
            const customer = (typeof custRaw === 'object' ? (custRaw.name || '') : String(custRaw)).toLowerCase();

            // Search filter
            if (query && !name.includes(query) && !code.includes(query) && !customer.includes(query)) {
                return false;
            }
            // Stage filter
            if (stageFilter) {
                const stage = (p.stage || p.status || '').toLowerCase().replace('-', '_');
                if (stage !== stageFilter) return false;
            }
            // Drawing filter
            if (drawingFilter === 'has' && getDrawingCount(p) === 0) return false;
            if (drawingFilter === 'none' && getDrawingCount(p) > 0) return false;

            return true;
        });
    }

    function escapeHtml(str) {
        if (!str) return '';
        return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    }

    function formatStage(stage) {
        if (!stage) return 'Unknown';
        return stage.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
    }

    function stageClass(stage) {
        if (!stage) return 'stage-default';
        const s = stage.toLowerCase().replace(/[-\s]/g, '_');
        return 'stage-' + s;
    }

    function renderGrid() {
        const filtered = getFilteredProjects();
        const grid = document.getElementById('projectsGrid');
        const emptyEl = document.getElementById('emptyState');

        if (filtered.length === 0) {
            grid.style.display = 'none';
            if (allProjects.length === 0) {
                showEmpty('No projects yet', 'Create a project from the dashboard to start generating shop drawings.');
            } else {
                showEmpty('No matching projects', 'Try adjusting your search or filter criteria.');
            }
            return;
        }

        emptyEl.style.display = 'none';
        grid.style.display = 'grid';

        // Sort: projects with drawings first, then by job code descending
        filtered.sort((a, b) => {
            const da = getDrawingCount(a), db = getDrawingCount(b);
            if (da > 0 && db === 0) return -1;
            if (db > 0 && da === 0) return 1;
            return (b.job_code || '').localeCompare(a.job_code || '');
        });

        grid.innerHTML = filtered.map(p => {
            const jobCode = p.job_code || 'UNKNOWN';
            const name = p.project_name || p.name || 'Untitled Project';
            const custRaw2 = p.customer_name || p.customer || '';
            const customer = typeof custRaw2 === 'object' ? (custRaw2.name || '') : String(custRaw2);
            const stage = p.stage || p.status || '';
            const count = getDrawingCount(p);
            const status = getDrawingStatus(p);
            const statusLabel = status === 'has-drawings' ? 'Drawings Ready'
                              : status === 'in-progress' ? 'In Progress'
                              : 'No Drawings';

            const maxDrawings = 9; // column, rafter, purlin, sagrod, strap, endcap, p1clip, p2plate, splice
            const pct = Math.min(100, Math.round((count / maxDrawings) * 100));

            return '<a class="project-card" href="/shop-drawings/' + encodeURIComponent(jobCode) + '">'
                + '<div class="card-header">'
                + '  <h3>' + escapeHtml(name) + '</h3>'
                + '  <span class="job-code-badge">' + escapeHtml(jobCode) + '</span>'
                + '</div>'
                + '<div class="card-meta">'
                + (customer ? '<span><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>' + escapeHtml(customer) + '</span>' : '')
                + '<span class="stage-pill ' + stageClass(stage) + '">' + escapeHtml(formatStage(stage)) + '</span>'
                + '</div>'
                + '<div class="drawing-status">'
                + '  <div class="drawing-count"><strong>' + count + '</strong> drawing' + (count !== 1 ? 's' : '') + '</div>'
                + '  <div class="progress-track"><div class="progress-fill' + (pct === 100 ? ' complete' : '') + '" style="width:' + pct + '%"></div></div>'
                + '  <span class="status-badge ' + status + '">' + statusLabel + '</span>'
                + '</div>'
                + '</a>';
        }).join('');
    }

    function showEmpty(title, msg) {
        document.getElementById('emptyState').style.display = 'block';
        document.getElementById('emptyTitle').textContent = title;
        document.getElementById('emptyMsg').textContent = msg;
    }

    // Wire up filters
    document.getElementById('searchInput').addEventListener('input', renderGrid);
    document.getElementById('stageFilter').addEventListener('change', renderGrid);
    document.getElementById('drawingFilter').addEventListener('change', renderGrid);

    // Load on page ready
    loadProjects();
})();
</script>
</body>
</html>
"""
