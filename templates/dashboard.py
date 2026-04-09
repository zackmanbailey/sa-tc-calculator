from templates.shared_styles import DESIGN_SYSTEM_CSS

DASHBOARD_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TitanForge — Dashboard</title>
    <style>
""" + DESIGN_SYSTEM_CSS + r"""

        /* ── Dashboard-Specific Styles ──────────────────── */
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: var(--tf-sp-6) var(--tf-sp-8);
        }

        /* Page Header */
        .page-header {
            margin-bottom: var(--tf-sp-6);
        }

        .page-title {
            font-size: var(--tf-text-2xl);
            font-weight: 700;
            color: var(--tf-gray-900);
            letter-spacing: -0.02em;
        }

        .page-subtitle {
            color: var(--tf-gray-500);
            font-size: var(--tf-text-base);
            margin-top: var(--tf-sp-1);
        }

        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: var(--tf-sp-4);
            margin-bottom: var(--tf-sp-8);
        }

        .stat-card {
            background: var(--tf-surface);
            border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-lg);
            padding: var(--tf-sp-5);
            display: flex;
            align-items: center;
            gap: var(--tf-sp-4);
            transition: all var(--tf-duration) var(--tf-ease);
        }

        .stat-card:hover {
            box-shadow: var(--tf-shadow-md);
            border-color: var(--tf-blue);
        }

        .stat-icon {
            width: 48px;
            height: 48px;
            border-radius: var(--tf-radius);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
            flex-shrink: 0;
        }

        .stat-icon.blue   { background: var(--tf-blue-light); }
        .stat-icon.amber  { background: var(--tf-amber-light); }
        .stat-icon.green  { background: var(--tf-success-bg); }
        .stat-icon.purple { background: #EDE9FE; }

        .stat-info { flex: 1; }

        .stat-label {
            font-size: var(--tf-text-xs);
            font-weight: 600;
            color: var(--tf-gray-500);
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .stat-value {
            font-size: var(--tf-text-2xl);
            font-weight: 700;
            color: var(--tf-gray-900);
            line-height: 1.2;
            margin-top: 2px;
        }

        /* Quick Actions */
        .quick-actions {
            display: flex;
            gap: var(--tf-sp-3);
            margin-bottom: var(--tf-sp-8);
            flex-wrap: wrap;
        }

        /* Section Headers */
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--tf-sp-5);
        }

        .section-title {
            font-size: var(--tf-text-lg);
            font-weight: 700;
            color: var(--tf-gray-900);
        }

        /* View Toggle */
        .view-toggle {
            display: flex;
            background: var(--tf-gray-100);
            padding: 3px;
            border-radius: var(--tf-radius);
        }

        .toggle-btn {
            background: transparent;
            border: none;
            padding: 8px 16px;
            border-radius: var(--tf-radius-sm);
            cursor: pointer;
            font-size: var(--tf-text-sm);
            font-weight: 600;
            color: var(--tf-gray-500);
            transition: all var(--tf-duration) var(--tf-ease);
        }

        .toggle-btn.active {
            background: var(--tf-surface);
            color: var(--tf-gray-900);
            box-shadow: var(--tf-shadow-sm);
        }

        /* ── Kanban ─────────────────────────────────────── */
        .kanban-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: var(--tf-sp-4);
            margin-bottom: var(--tf-sp-8);
        }

        .kanban-column {
            background: var(--tf-gray-50);
            border-radius: var(--tf-radius-lg);
            padding: var(--tf-sp-4);
            border: 1px solid var(--tf-border);
            min-height: 200px;
        }

        .column-header {
            font-size: var(--tf-text-xs);
            font-weight: 700;
            color: var(--tf-gray-600);
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: var(--tf-sp-3);
            padding-bottom: var(--tf-sp-2);
            border-bottom: 2px solid var(--tf-border);
        }

        /* Project Cards — 4 meaningful colors instead of 8 */
        .project-card {
            background: var(--tf-surface);
            border-left: 4px solid var(--tf-gray-300);
            border-radius: var(--tf-radius);
            padding: var(--tf-sp-4);
            margin-bottom: var(--tf-sp-3);
            cursor: pointer;
            transition: all var(--tf-duration) var(--tf-ease);
            box-shadow: var(--tf-shadow-sm);
        }

        .project-card:hover {
            box-shadow: var(--tf-shadow-md);
            transform: translateY(-1px);
        }

        /* Stage colors: 4 groups instead of 8 */
        .project-card.quote,
        .project-card.contract          { border-left-color: var(--tf-blue); }
        .project-card.engineering,
        .project-card.shop-drawings     { border-left-color: #7C3AED; }
        .project-card.fabrication       { border-left-color: var(--tf-amber); }
        .project-card.shipping,
        .project-card.install           { border-left-color: var(--tf-success); }
        .project-card.complete          { border-left-color: var(--tf-gray-400); }

        .card-job-code {
            font-size: var(--tf-text-xs);
            font-weight: 700;
            color: var(--tf-blue);
            text-transform: uppercase;
            letter-spacing: 0.02em;
        }

        .card-project-name {
            font-size: var(--tf-text-base);
            font-weight: 600;
            color: var(--tf-gray-900);
            margin-top: var(--tf-sp-1);
            line-height: 1.3;
        }

        .card-customer {
            font-size: var(--tf-text-xs);
            color: var(--tf-gray-500);
            margin-top: var(--tf-sp-1);
        }

        .card-price {
            font-size: var(--tf-text-sm);
            font-weight: 700;
            color: var(--tf-success);
            margin-top: var(--tf-sp-3);
            padding-top: var(--tf-sp-2);
            border-top: 1px solid var(--tf-gray-100);
        }

        .card-price.hidden { display: none; }

        /* ── Table View ─────────────────────────────────── */
        .table-container {
            background: var(--tf-surface);
            border-radius: var(--tf-radius-lg);
            border: 1px solid var(--tf-border);
            overflow: hidden;
        }

        .table {
            width: 100%;
            border-collapse: collapse;
        }

        .table thead th {
            background: var(--tf-navy);
            color: #fff;
            font-size: var(--tf-text-xs);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            padding: var(--tf-sp-3) var(--tf-sp-4);
            text-align: left;
            cursor: pointer;
            user-select: none;
            white-space: nowrap;
            transition: background var(--tf-duration) var(--tf-ease);
        }

        .table thead th:hover { background: var(--tf-navy-light); }

        .table td {
            padding: var(--tf-sp-3) var(--tf-sp-4);
            border-bottom: 1px solid var(--tf-gray-100);
            font-size: var(--tf-text-sm);
        }

        .table tbody tr {
            cursor: pointer;
            transition: background var(--tf-duration) var(--tf-ease);
        }

        .table tbody tr:hover td { background: var(--tf-blue-light); }

        .price.hidden { display: none; }

        /* Stage Badges — 4 semantic colors */
        .stage-badge {
            display: inline-flex;
            align-items: center;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: var(--tf-text-xs);
            font-weight: 600;
            white-space: nowrap;
        }

        .stage-quote,
        .stage-contract          { background: var(--tf-blue-light); color: var(--tf-blue); }
        .stage-engineering,
        .stage-shop-drawings     { background: #EDE9FE; color: #6D28D9; }
        .stage-fabrication       { background: var(--tf-amber-light); color: #92400E; }
        .stage-shipping,
        .stage-install           { background: var(--tf-success-bg); color: var(--tf-success); }
        .stage-complete          { background: var(--tf-gray-100); color: var(--tf-gray-600); }

        /* ── Inventory Alerts ───────────────────────────── */
        .alerts-section { display: none; margin-bottom: var(--tf-sp-6); }
        .alerts-section.show { display: block; animation: fadeIn 200ms var(--tf-ease); }

        .alerts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: var(--tf-sp-4);
        }

        .alert-card {
            border-radius: var(--tf-radius);
            padding: var(--tf-sp-4);
            cursor: pointer;
            transition: all var(--tf-duration) var(--tf-ease);
            border-left: 4px solid;
        }

        .alert-card:hover { box-shadow: var(--tf-shadow-md); transform: translateY(-1px); }
        .alert-card.danger  { background: var(--tf-danger-bg); border-left-color: var(--tf-danger); }
        .alert-card.warning { background: var(--tf-warning-bg); border-left-color: var(--tf-warning); }

        .alert-title { font-weight: 700; color: var(--tf-gray-900); font-size: var(--tf-text-sm); margin-bottom: var(--tf-sp-1); }
        .alert-message { color: var(--tf-gray-600); font-size: var(--tf-text-sm); }

        /* Alert bell in topbar */
        .inventory-alert {
            position: relative;
            cursor: pointer;
            transition: color var(--tf-duration) var(--tf-ease);
        }
        .inventory-alert:hover { color: var(--tf-amber); }

        .alert-badge {
            position: absolute;
            top: -8px;
            right: -8px;
            background: var(--tf-danger);
            color: #fff;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 11px;
            font-weight: 700;
        }

        /* ── Modal ──────────────────────────────────────── */
        .modal {
            display: none;
            position: fixed;
            inset: 0;
            z-index: 2000;
            background: rgba(15, 23, 42, 0.6);
            backdrop-filter: blur(4px);
            animation: fadeIn 200ms var(--tf-ease);
        }

        .modal.show {
            display: flex;
            align-items: center;
            justify-content: center;
        }

        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

        .modal-content {
            background: var(--tf-surface);
            border-radius: var(--tf-radius-xl);
            width: 92%;
            max-width: 860px;
            max-height: 85vh;
            overflow-y: auto;
            box-shadow: var(--tf-shadow-lg);
            animation: slideUp 250ms var(--tf-ease);
        }

        @keyframes slideUp {
            from { transform: translateY(20px); opacity: 0; }
            to   { transform: translateY(0); opacity: 1; }
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            padding: var(--tf-sp-6);
            border-bottom: 1px solid var(--tf-border);
        }

        .modal-title {
            font-size: var(--tf-text-lg);
            font-weight: 700;
            color: var(--tf-gray-900);
        }

        .modal-badge-group { display: flex; gap: var(--tf-sp-2); margin-top: var(--tf-sp-2); }

        .modal-badge {
            display: inline-flex;
            align-items: center;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: var(--tf-text-xs);
            font-weight: 600;
            color: #fff;
        }

        .close-btn {
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: var(--tf-gray-400);
            padding: var(--tf-sp-2);
            border-radius: var(--tf-radius-sm);
            transition: all var(--tf-duration) var(--tf-ease);
            line-height: 1;
        }
        .close-btn:hover { background: var(--tf-gray-100); color: var(--tf-gray-800); }

        .modal-body { padding: var(--tf-sp-6); }

        /* Modal Tabs */
        .tab-buttons {
            display: flex;
            gap: var(--tf-sp-1);
            border-bottom: 2px solid var(--tf-border);
            margin-bottom: var(--tf-sp-6);
        }

        .tab-btn {
            background: none;
            border: none;
            padding: var(--tf-sp-3) var(--tf-sp-4);
            font-size: var(--tf-text-sm);
            font-weight: 500;
            color: var(--tf-gray-500);
            cursor: pointer;
            border-bottom: 2px solid transparent;
            margin-bottom: -2px;
            transition: all var(--tf-duration) var(--tf-ease);
        }

        .tab-btn:hover { color: var(--tf-gray-700); }
        .tab-btn.active { color: var(--tf-blue); border-bottom-color: var(--tf-blue); font-weight: 600; }

        .tab-content { display: none; }
        .tab-content.active { display: block; }

        /* Info Grid (Overview) */
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: var(--tf-sp-4);
        }

        .info-item {
            background: var(--tf-gray-50);
            border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius);
            padding: var(--tf-sp-4);
        }

        .info-label {
            font-size: var(--tf-text-xs);
            font-weight: 600;
            color: var(--tf-gray-500);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: var(--tf-sp-1);
        }

        .info-value {
            font-size: var(--tf-text-md);
            font-weight: 600;
            color: var(--tf-gray-900);
        }

        /* Documents */
        .document-categories {
            display: flex;
            gap: var(--tf-sp-2);
            margin-bottom: var(--tf-sp-4);
            flex-wrap: wrap;
        }

        .doc-category-btn {
            background: var(--tf-gray-50);
            border: 1px solid var(--tf-border);
            padding: 8px 16px;
            border-radius: 999px;
            cursor: pointer;
            font-size: var(--tf-text-xs);
            font-weight: 600;
            color: var(--tf-gray-600);
            transition: all var(--tf-duration) var(--tf-ease);
        }

        .doc-category-btn.active {
            background: var(--tf-blue);
            color: #fff;
            border-color: var(--tf-blue);
        }

        .upload-zone {
            border: 2px dashed var(--tf-gray-300);
            border-radius: var(--tf-radius-lg);
            padding: var(--tf-sp-8) var(--tf-sp-6);
            text-align: center;
            cursor: pointer;
            transition: all var(--tf-duration) var(--tf-ease);
            background: var(--tf-gray-50);
            margin-bottom: var(--tf-sp-5);
        }

        .upload-zone:hover {
            border-color: var(--tf-blue-mid);
            background: var(--tf-blue-light);
        }

        .upload-zone.dragover {
            border-color: var(--tf-amber);
            background: var(--tf-amber-light);
        }

        .upload-text { color: var(--tf-gray-500); font-size: var(--tf-text-sm); }
        .upload-highlight { color: var(--tf-blue); font-weight: 600; }

        .file-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
            gap: var(--tf-sp-3);
        }

        .file-card {
            border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius);
            padding: var(--tf-sp-4) var(--tf-sp-3);
            text-align: center;
            transition: all var(--tf-duration) var(--tf-ease);
            position: relative;
            background: var(--tf-surface);
        }

        .file-card:hover { box-shadow: var(--tf-shadow-md); border-color: var(--tf-blue); }

        .file-icon { font-size: 2rem; margin-bottom: var(--tf-sp-2); }
        .file-name { font-size: var(--tf-text-xs); font-weight: 600; color: var(--tf-gray-700); word-break: break-all; }
        .file-delete {
            background: none; border: none; color: var(--tf-gray-400); cursor: pointer;
            font-size: 1rem; padding: var(--tf-sp-1); margin-top: var(--tf-sp-2);
            transition: color var(--tf-duration) var(--tf-ease);
        }
        .file-delete:hover { color: var(--tf-danger); }
        .file-delete.hidden { display: none; }

        /* Revisions Table */
        .revisions-table {
            width: 100%;
            border-collapse: collapse;
            font-size: var(--tf-text-sm);
        }

        .revisions-table thead th {
            background: var(--tf-gray-50);
            font-size: var(--tf-text-xs);
            font-weight: 700;
            color: var(--tf-gray-600);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            padding: var(--tf-sp-3);
            text-align: left;
            border-bottom: 2px solid var(--tf-border);
        }

        .revisions-table td {
            padding: var(--tf-sp-3);
            border-bottom: 1px solid var(--tf-gray-100);
        }

        .revisions-table tbody tr:hover td { background: var(--tf-blue-light); }

        .revision-action-btn {
            padding: 5px 12px;
            font-size: var(--tf-text-xs);
            font-weight: 600;
            background: var(--tf-blue);
            color: #fff;
            border: none;
            border-radius: var(--tf-radius-sm);
            cursor: pointer;
            margin-right: var(--tf-sp-2);
            transition: background var(--tf-duration) var(--tf-ease);
        }

        .revision-action-btn:hover { background: #1D4ED8; }

        /* Navbar extras */
        .user-section {
            display: flex;
            align-items: center;
            gap: var(--tf-sp-3);
        }

        .role-badge {
            background: rgba(245, 158, 11, 0.15);
            color: var(--tf-amber);
            padding: 3px 10px;
            border-radius: 999px;
            font-size: var(--tf-text-xs);
            font-weight: 600;
        }

        .logout-btn {
            background: none;
            color: var(--tf-gray-400);
            border: 1px solid var(--tf-gray-600);
            padding: 6px 14px;
            border-radius: var(--tf-radius-sm);
            cursor: pointer;
            font-size: var(--tf-text-xs);
            font-weight: 500;
            transition: all var(--tf-duration) var(--tf-ease);
        }
        .logout-btn:hover { color: #fff; border-color: var(--tf-gray-400); }

        /* Loading / Empty States */
        .loading { opacity: 0.5; pointer-events: none; }

        .spinner {
            border: 3px solid var(--tf-gray-200);
            border-top: 3px solid var(--tf-blue-mid);
            border-radius: 50%;
            width: 36px;
            height: 36px;
            animation: tf-spin 0.7s ease-in-out infinite;
            margin: var(--tf-sp-8) auto;
        }

        .empty-state {
            text-align: center;
            padding: var(--tf-sp-12) var(--tf-sp-4);
            color: var(--tf-gray-500);
        }

        .empty-state-icon { font-size: 2.5rem; margin-bottom: var(--tf-sp-3); opacity: 0.5; }
        .empty-state-title { font-size: var(--tf-text-md); font-weight: 700; color: var(--tf-gray-700); margin-bottom: var(--tf-sp-2); }

        /* ── Responsive ─────────────────────────────────── */
        @media (max-width: 1280px) {
            .stats-grid { grid-template-columns: repeat(2, 1fr); }
        }

        @media (max-width: 1024px) {
            .container { padding: var(--tf-sp-4); }
            .kanban-container { grid-template-columns: repeat(2, 1fr); }
            .modal-content { width: 95%; max-height: 90vh; }
        }

        @media (max-width: 768px) {
            .tf-topbar nav { display: none; }
            .stats-grid { grid-template-columns: 1fr; }
            .kanban-container { grid-template-columns: 1fr; }
            .quick-actions { flex-direction: column; }
            .page-title { font-size: var(--tf-text-xl); }
            .section-title { font-size: var(--tf-text-md); }
        }
    </style>
</head>
<body>
    <script>
        const USER_ROLE = '{{USER_ROLE}}';
        const USER_NAME = '{{USER_NAME}}';
    </script>

    <!-- TOP NAVIGATION BAR -->
    <div class="tf-topbar">
        <a href="/" class="tf-logo">
            <div class="tf-logo-icon">&#9878;</div>
            TITANFORGE
        </a>

        <nav>
            <a href="/" class="active">Dashboard</a>
            <a href="/sa">SA Calculator</a>
            <a href="/tc">TC Quote</a>
        </nav>

        <div class="tf-user">
            <div class="inventory-alert" id="inventoryAlert" style="display: none;">
                <span style="font-size: 1.2rem;">&#128276;</span>
                <span class="alert-badge" id="alertCount">0</span>
            </div>
            <div class="user-section">
                <span id="userName">User</span>
                <span class="role-badge" id="userRole">USER</span>
                <button class="logout-btn" onclick="handleLogout()">Logout</button>
            </div>
        </div>
    </div>

    <!-- MAIN CONTENT -->
    <div class="container">
        <!-- PAGE HEADER -->
        <div class="page-header">
            <h1 class="page-title">Dashboard</h1>
            <p class="page-subtitle">Steel Fabrication Management</p>
        </div>

        <!-- STATS GRID -->
        <div class="stats-grid" id="statsGrid">
            <div class="stat-card">
                <div class="stat-icon blue">&#128202;</div>
                <div class="stat-info">
                    <div class="stat-label">Active Projects</div>
                    <div class="stat-value" id="activeProjects">&mdash;</div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon amber">&#128295;</div>
                <div class="stat-info">
                    <div class="stat-label">In Fabrication</div>
                    <div class="stat-value" id="inFabrication">&mdash;</div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon green">&#128230;</div>
                <div class="stat-info">
                    <div class="stat-label">Ready to Ship</div>
                    <div class="stat-value" id="readyToShip">&mdash;</div>
                </div>
            </div>
        </div>

        <!-- QUICK ACTIONS -->
        <div class="quick-actions">
            <button class="tf-btn tf-btn-primary" onclick="openNewProjectForm()">+ New Project</button>
            <button class="tf-btn tf-btn-outline" onclick="window.location.href='/sa'">SA Calculator</button>
            <button class="tf-btn tf-btn-outline" onclick="window.location.href='/tc'">TC Quote</button>
        </div>

        <!-- INVENTORY ALERTS -->
        <div class="alerts-section" id="alertsSection">
            <div class="section-header">
                <h2 class="section-title">Inventory Alerts</h2>
            </div>
            <div class="alerts-grid" id="alertsGrid"></div>
        </div>

        <!-- PROJECT PIPELINE -->
        <div class="section-header">
            <h2 class="section-title">Project Pipeline</h2>
            <div class="view-toggle">
                <button class="toggle-btn active" id="kanbanToggle" onclick="switchView('kanban')">Board</button>
                <button class="toggle-btn" id="tableToggle" onclick="switchView('table')">Table</button>
            </div>
        </div>

        <!-- KANBAN VIEW -->
        <div id="kanbanView" class="kanban-container"></div>

        <!-- TABLE VIEW -->
        <div id="tableView" class="table-container" style="display: none;">
            <table class="table">
                <thead>
                    <tr>
                        <th onclick="sortTable('jobCode')">Job Code</th>
                        <th onclick="sortTable('name')">Project</th>
                        <th onclick="sortTable('customer')">Customer</th>
                        <th onclick="sortTable('stage')">Stage</th>
                        <th class="price" onclick="sortTable('price')">Sell Price</th>
                        <th onclick="sortTable('updated')">Updated</th>
                        <th onclick="sortTable('version')">Ver</th>
                    </tr>
                </thead>
                <tbody id="tableBody"></tbody>
            </table>
        </div>
    </div>

    <!-- PROJECT DETAIL MODAL -->
    <div class="modal" id="projectModal">
        <div class="modal-content">
            <div class="modal-header">
                <div>
                    <h2 class="modal-title" id="modalTitle">Project Details</h2>
                    <div class="modal-badge-group" id="modalBadgeGroup"></div>
                </div>
                <button class="close-btn" onclick="closeProjectModal()">&times;</button>
            </div>

            <div class="modal-body">
                <div class="tab-buttons">
                    <button class="tab-btn active" onclick="switchTab('overview')">Overview</button>
                    <button class="tab-btn" onclick="switchTab('documents')">Documents</button>
                    <button class="tab-btn" onclick="switchTab('revisions')">Revisions</button>
                </div>

                <!-- OVERVIEW TAB -->
                <div id="overviewTab" class="tab-content active">
                    <div class="info-grid" id="overviewInfo"></div>
                </div>

                <!-- DOCUMENTS TAB -->
                <div id="documentsTab" class="tab-content">
                    <div class="document-categories" id="docCategories"></div>
                    <div class="upload-zone" id="uploadZone" ondrop="handleDrop(event)" ondragover="handleDragOver(event)" ondragleave="handleDragLeave(event)" onclick="document.getElementById('fileInput').click()">
                        <p class="upload-text">
                            <span class="upload-highlight">Click to upload</span> or drag and drop<br>
                            <span style="font-size: 0.8rem; color: var(--tf-gray-400);">PDF, DOCX, XLSX, Images</span>
                        </p>
                    </div>
                    <input type="file" id="fileInput" style="display: none;" onchange="handleFileSelect(event)" multiple accept=".pdf,.docx,.xlsx,.jpg,.png,.gif">
                    <div class="file-list" id="fileList"></div>
                </div>

                <!-- REVISIONS TAB -->
                <div id="revisionsTab" class="tab-content">
                    <table class="revisions-table">
                        <thead>
                            <tr>
                                <th>Version</th>
                                <th>Date</th>
                                <th>Author</th>
                                <th>Notes</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="revisionsBody"></tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script>
        // ── Global State ──────────────────────────────────
        let allProjects = [];
        let currentView = 'kanban';
        let currentProject = null;
        let currentSortColumn = null;
        let currentSortDirection = 'asc';
        let inventoryAlerts = [];

        document.addEventListener('DOMContentLoaded', function() {
            initializePage();
        });

        function initializePage() {
            if (USER_NAME && USER_NAME !== '{{USER_NAME}}') {
                document.getElementById('userName').textContent = USER_NAME;
            }
            const roleText = USER_ROLE && USER_ROLE !== '{{USER_ROLE}}' ? USER_ROLE : 'User';
            document.getElementById('userRole').textContent = roleText.toUpperCase();

            loadProjects();
            loadInventoryAlerts();
            setupEventListeners();

            if (USER_ROLE === 'shop') {
                document.querySelectorAll('.price').forEach(el => el.classList.add('hidden'));
            }
        }

        function setupEventListeners() {
            document.getElementById('projectModal').addEventListener('click', function(e) {
                if (e.target === this) closeProjectModal();
            });
        }

        function loadProjects() {
            fetch('/api/projects')
                .then(response => response.json())
                .then(data => {
                    allProjects = data.projects || [];
                    updateStats();
                    renderProjects();
                })
                .catch(error => {
                    console.error('Error loading projects:', error);
                    allProjects = generateMockProjects();
                    updateStats();
                    renderProjects();
                });
        }

        function loadInventoryAlerts() {
            fetch('/api/inventory')
                .then(response => response.json())
                .then(data => {
                    inventoryAlerts = data.alerts || [];
                    renderInventoryAlerts();
                })
                .catch(error => {
                    console.error('Error loading inventory:', error);
                });
        }

        function generateMockProjects() {
            const stages = ['quote', 'contract', 'engineering', 'shop-drawings', 'fabrication', 'shipping', 'install', 'complete'];
            const mockProjects = [];
            for (let i = 1; i <= 12; i++) {
                mockProjects.push({
                    id: i,
                    jobCode: 'TF-2026-' + String(i).padStart(4, '0'),
                    name: 'Commercial Steel Structure ' + i,
                    customer: 'Customer ' + i,
                    stage: stages[Math.floor(Math.random() * stages.length)],
                    sellPrice: Math.floor(Math.random() * 100000) + 50000,
                    lastUpdated: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
                    version: '1.' + Math.floor(Math.random() * 5)
                });
            }
            return mockProjects;
        }

        function updateStats() {
            const activeCount = allProjects.filter(p => p.stage !== 'complete').length;
            const fabricatingCount = allProjects.filter(p => p.stage === 'fabrication').length;
            const readyCount = allProjects.filter(p => p.stage === 'shipping').length;
            document.getElementById('activeProjects').textContent = activeCount;
            document.getElementById('inFabrication').textContent = fabricatingCount;
            document.getElementById('readyToShip').textContent = readyCount;
        }

        function renderProjects() {
            if (currentView === 'kanban') renderKanban();
            else renderTable();
        }

        function renderKanban() {
            const stages = ['quote', 'contract', 'engineering', 'shop-drawings', 'fabrication', 'shipping', 'install', 'complete'];
            const kanbanContainer = document.getElementById('kanbanView');
            kanbanContainer.innerHTML = '';

            stages.forEach(stage => {
                const projects = allProjects.filter(p => p.stage === stage);
                const columnHeader = stage.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');

                const column = document.createElement('div');
                column.className = 'kanban-column';

                const header = document.createElement('div');
                header.className = 'column-header';
                header.textContent = columnHeader + ' (' + projects.length + ')';
                column.appendChild(header);

                projects.forEach(project => {
                    const card = createProjectCard(project);
                    column.appendChild(card);
                });

                kanbanContainer.appendChild(column);
            });
        }

        function createProjectCard(project) {
            const card = document.createElement('div');
            card.className = 'project-card ' + project.stage;
            card.onclick = () => openProjectModal(project);

            const jobCode = document.createElement('div');
            jobCode.className = 'card-job-code';
            jobCode.textContent = project.jobCode;

            const name = document.createElement('div');
            name.className = 'card-project-name';
            name.textContent = project.name;

            const customer = document.createElement('div');
            customer.className = 'card-customer';
            customer.textContent = project.customer;

            card.appendChild(jobCode);
            card.appendChild(name);
            card.appendChild(customer);

            if (USER_ROLE !== 'shop') {
                const price = document.createElement('div');
                price.className = 'card-price';
                price.textContent = '$' + project.sellPrice.toLocaleString();
                card.appendChild(price);
            }

            return card;
        }

        function renderTable() {
            const tableBody = document.getElementById('tableBody');
            tableBody.innerHTML = '';

            allProjects.forEach(project => {
                const row = document.createElement('tr');
                row.onclick = () => openProjectModal(project);

                const stageLabel = project.stage.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
                const stageBadgeClass = 'stage-' + project.stage.replace('_', '-');

                row.innerHTML = '<td><strong>' + project.jobCode + '</strong></td>'
                    + '<td>' + project.name + '</td>'
                    + '<td>' + project.customer + '</td>'
                    + '<td><span class="stage-badge ' + stageBadgeClass + '">' + stageLabel + '</span></td>'
                    + '<td class="price">$' + project.sellPrice.toLocaleString() + '</td>'
                    + '<td>' + new Date(project.lastUpdated).toLocaleDateString() + '</td>'
                    + '<td>' + project.version + '</td>';

                tableBody.appendChild(row);
            });
        }

        function renderInventoryAlerts() {
            if (inventoryAlerts.length === 0) {
                document.getElementById('alertsSection').classList.remove('show');
                return;
            }

            document.getElementById('alertsSection').classList.add('show');
            const alertsGrid = document.getElementById('alertsGrid');
            alertsGrid.innerHTML = '';

            inventoryAlerts.forEach(alert => {
                const alertCard = document.createElement('div');
                alertCard.className = 'alert-card ' + (alert.severity === 'danger' ? 'danger' : 'warning');
                alertCard.onclick = () => window.location.href = '/sa';

                const title = document.createElement('div');
                title.className = 'alert-title';
                title.textContent = alert.itemName;

                const message = document.createElement('div');
                message.className = 'alert-message';
                message.textContent = alert.message;

                alertCard.appendChild(title);
                alertCard.appendChild(message);
                alertsGrid.appendChild(alertCard);
            });

            const alertCount = inventoryAlerts.length;
            if (alertCount > 0) {
                document.getElementById('inventoryAlert').style.display = 'block';
                document.getElementById('alertCount').textContent = alertCount;
            }
        }

        function switchView(view) {
            currentView = view;
            document.getElementById('kanbanToggle').classList.toggle('active', view === 'kanban');
            document.getElementById('tableToggle').classList.toggle('active', view === 'table');
            document.getElementById('kanbanView').style.display = view === 'kanban' ? 'grid' : 'none';
            document.getElementById('tableView').style.display = view === 'table' ? 'block' : 'none';
            renderProjects();
        }

        function sortTable(column) {
            if (currentSortColumn === column) {
                currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
            } else {
                currentSortDirection = 'asc';
                currentSortColumn = column;
            }

            allProjects.sort((a, b) => {
                let aVal = a[column];
                let bVal = b[column];
                if (column === 'price') { aVal = a.sellPrice; bVal = b.sellPrice; }
                if (typeof aVal === 'string') { aVal = aVal.toLowerCase(); bVal = bVal.toLowerCase(); }
                const comparison = aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
                return currentSortDirection === 'asc' ? comparison : -comparison;
            });

            renderTable();
        }

        function openProjectModal(project) {
            currentProject = project;
            document.getElementById('modalTitle').textContent = project.jobCode + ' — ' + project.name;
            const badgeGroup = document.getElementById('modalBadgeGroup');
            badgeGroup.innerHTML = '';

            const stageBadge = document.createElement('span');
            stageBadge.className = 'modal-badge';
            stageBadge.style.backgroundColor = '#1E40AF';
            stageBadge.textContent = project.stage.toUpperCase().replace('-', ' ');

            const versionBadge = document.createElement('span');
            versionBadge.className = 'modal-badge';
            versionBadge.style.backgroundColor = '#F59E0B';
            versionBadge.textContent = 'v' + project.version;

            badgeGroup.appendChild(stageBadge);
            badgeGroup.appendChild(versionBadge);

            loadProjectDetails(project.id);
            document.getElementById('projectModal').classList.add('show');
        }

        function closeProjectModal() {
            document.getElementById('projectModal').classList.remove('show');
            currentProject = null;
        }

        function loadProjectDetails(projectId) {
            fetch('/api/project/load', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: projectId })
            })
                .then(response => response.json())
                .then(data => {
                    renderProjectOverview(data.project);
                    loadProjectDocuments(projectId);
                    loadProjectRevisions(projectId);
                })
                .catch(error => {
                    console.error('Error loading project:', error);
                    renderProjectOverview(currentProject);
                });
        }

        function renderProjectOverview(project) {
            const overviewInfo = document.getElementById('overviewInfo');
            overviewInfo.innerHTML = '';

            const infoItems = [
                { label: 'Job Code', value: project.jobCode },
                { label: 'Project Name', value: project.name },
                { label: 'Customer', value: project.customer },
                { label: 'Stage', value: project.stage },
                { label: 'Sell Price', value: '$' + project.sellPrice.toLocaleString(), hidden: USER_ROLE === 'shop' },
                { label: 'Last Updated', value: new Date(project.lastUpdated).toLocaleDateString() },
                { label: 'Version', value: 'v' + project.version }
            ];

            infoItems.forEach(item => {
                if (item.hidden) return;
                const infoItem = document.createElement('div');
                infoItem.className = 'info-item';
                const label = document.createElement('div');
                label.className = 'info-label';
                label.textContent = item.label;
                const value = document.createElement('div');
                value.className = 'info-value';
                value.textContent = item.value;
                infoItem.appendChild(label);
                infoItem.appendChild(value);
                overviewInfo.appendChild(infoItem);
            });
        }

        function loadProjectDocuments(projectId) {
            const categories = ['Quotes', 'Contracts', 'Engineering', 'Shop Drawings', 'Other'];
            const docCategories = document.getElementById('docCategories');
            docCategories.innerHTML = '';

            categories.forEach((cat, idx) => {
                const btn = document.createElement('button');
                btn.className = 'doc-category-btn' + (idx === 0 ? ' active' : '');
                btn.textContent = cat;
                btn.onclick = () => switchDocCategory(cat);
                docCategories.appendChild(btn);
            });

            const mockFiles = [
                { name: 'Quote_v1.pdf', type: 'pdf', category: 'Quotes' },
                { name: 'Contract_signed.docx', type: 'docx', category: 'Contracts' },
                { name: 'BOM.xlsx', type: 'xlsx', category: 'Engineering' },
                { name: 'Drawing_01.pdf', type: 'pdf', category: 'Shop Drawings' }
            ];
            renderDocuments(mockFiles);
        }

        function switchDocCategory(category) {
            document.querySelectorAll('.doc-category-btn').forEach(btn => {
                btn.classList.toggle('active', btn.textContent === category);
            });
        }

        function renderDocuments(files) {
            const fileList = document.getElementById('fileList');
            fileList.innerHTML = '';

            files.forEach(file => {
                const fileCard = document.createElement('div');
                fileCard.className = 'file-card';

                const iconMap = { pdf: '&#128196;', docx: '&#128216;', xlsx: '&#128202;', jpg: '&#128444;', png: '&#128444;', gif: '&#128444;' };
                const icon = document.createElement('div');
                icon.className = 'file-icon';
                icon.innerHTML = iconMap[file.type] || '&#128193;';

                const name = document.createElement('div');
                name.className = 'file-name';
                name.textContent = file.name;

                fileCard.appendChild(icon);
                fileCard.appendChild(name);

                if (USER_ROLE !== 'viewer') {
                    const deleteBtn = document.createElement('button');
                    deleteBtn.className = 'file-delete';
                    deleteBtn.innerHTML = '&#128465;';
                    deleteBtn.onclick = (e) => { e.stopPropagation(); deleteFile(file.name); };
                    fileCard.appendChild(deleteBtn);
                }

                fileList.appendChild(fileCard);
            });
        }

        function handleDragOver(e) { e.preventDefault(); e.stopPropagation(); document.getElementById('uploadZone').classList.add('dragover'); }
        function handleDragLeave(e) { e.preventDefault(); e.stopPropagation(); document.getElementById('uploadZone').classList.remove('dragover'); }
        function handleDrop(e) {
            e.preventDefault(); e.stopPropagation();
            document.getElementById('uploadZone').classList.remove('dragover');
            uploadFiles(e.dataTransfer.files);
        }
        function handleFileSelect(e) { uploadFiles(e.target.files); }

        function uploadFiles(files) {
            if (USER_ROLE === 'viewer') { alert('You do not have permission to upload files.'); return; }
            const formData = new FormData();
            for (let file of files) formData.append('files', file);
            fetch('/api/project/docs/upload', { method: 'POST', body: formData })
                .then(r => r.json())
                .then(data => { console.log('Files uploaded:', data); loadProjectDocuments(currentProject.id); })
                .catch(e => { console.error('Upload error:', e); alert('Failed to upload files.'); });
        }

        function deleteFile(fileName) {
            if (USER_ROLE === 'viewer') return;
            if (confirm('Delete this file?')) {
                fetch('/api/project/docs/delete', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ fileName: fileName }) })
                    .then(r => r.json()).then(data => { console.log('File deleted:', data); loadProjectDocuments(currentProject.id); })
                    .catch(e => console.error('Delete error:', e));
            }
        }

        function loadProjectRevisions(projectId) {
            fetch('/api/project/revisions', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id: projectId }) })
                .then(r => r.json()).then(data => { renderRevisions(data.revisions || []); })
                .catch(e => { console.error('Error loading revisions:', e); renderRevisions([]); });
        }

        function renderRevisions(revisions) {
            const revisionsBody = document.getElementById('revisionsBody');
            revisionsBody.innerHTML = '';
            if (revisions.length === 0) {
                revisionsBody.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:2rem;color:var(--tf-gray-400);">No revisions found</td></tr>';
                return;
            }
            revisions.forEach((rev, idx) => {
                const row = document.createElement('tr');
                row.innerHTML = '<td><strong>v' + rev.version + '</strong></td>'
                    + '<td>' + new Date(rev.date).toLocaleDateString() + '</td>'
                    + '<td>' + rev.author + '</td>'
                    + '<td>' + (rev.notes || '—') + '</td>'
                    + '<td><button class="revision-action-btn" onclick="loadRevision(\'' + rev.version + '\')">Load</button>'
                    + (idx > 0 ? '<button class="revision-action-btn" onclick="compareRevisions(\'' + rev.version + '\')">Compare</button>' : '')
                    + '</td>';
                revisionsBody.appendChild(row);
            });
        }

        function loadRevision(version) { alert('Loading revision ' + version); }
        function compareRevisions(version) { alert('Comparing revisions'); }

        function switchTab(tabName) {
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.toggle('active', btn.textContent.toLowerCase().includes(tabName));
            });
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            document.getElementById(tabName + 'Tab').classList.add('active');
        }

        function openNewProjectForm() { alert('New project form would open here'); }
        function handleLogout() { if (confirm('Are you sure you want to logout?')) window.location.href = '/auth/logout'; }
    </script>
</body>
</html>
"""
