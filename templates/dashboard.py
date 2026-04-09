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

        /* New Project Form */
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: var(--tf-sp-4);
        }

        .form-group {
            margin-bottom: var(--tf-sp-4);
        }

        .form-group label {
            display: block;
            font-size: var(--tf-text-xs);
            font-weight: 600;
            color: var(--tf-gray-600);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: var(--tf-sp-1);
        }

        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 10px 12px;
            font-family: var(--tf-font);
            font-size: var(--tf-text-base);
            color: var(--tf-gray-800);
            background: #fff;
            border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius);
            outline: none;
            transition: all var(--tf-duration) var(--tf-ease);
        }

        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            border-color: var(--tf-blue-mid);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
        }

        .form-section-title {
            font-size: var(--tf-text-sm);
            font-weight: 700;
            color: var(--tf-gray-700);
            margin-top: var(--tf-sp-4);
            margin-bottom: var(--tf-sp-3);
            padding-bottom: var(--tf-sp-2);
            border-bottom: 1px solid var(--tf-border);
        }

        .form-actions {
            display: flex;
            justify-content: flex-end;
            gap: var(--tf-sp-3);
            margin-top: var(--tf-sp-6);
            padding-top: var(--tf-sp-4);
            border-top: 1px solid var(--tf-border);
        }

        /* Filter toggle */
        .filter-toggle {
            display: flex;
            align-items: center;
            gap: var(--tf-sp-2);
            font-size: var(--tf-text-sm);
            color: var(--tf-gray-500);
            cursor: pointer;
        }

        .filter-toggle input[type="checkbox"] {
            width: 16px;
            height: 16px;
            accent-color: var(--tf-blue);
        }

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
            <button class="tf-btn tf-btn-primary" onclick="openNewProjectForm()" id="newProjectBtn">+ New Project</button>
            <button class="tf-btn tf-btn-outline" onclick="window.location.href='/sa'">SA Calculator</button>
            <button class="tf-btn tf-btn-outline" onclick="window.location.href='/tc'">TC Quote</button>
            <label class="filter-toggle" style="margin-left: auto;">
                <input type="checkbox" id="showCompletedToggle" onchange="toggleCompleted()">
                Show completed
            </label>
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

    <!-- NEW PROJECT MODAL -->
    <div class="modal" id="newProjectModal">
        <div class="modal-content">
            <div class="modal-header">
                <div>
                    <h2 class="modal-title">New Project</h2>
                    <div class="modal-badge-group">
                        <span class="modal-badge" style="background: var(--tf-blue);" id="newJobCodeBadge">Loading...</span>
                    </div>
                </div>
                <button class="close-btn" onclick="closeNewProjectModal()">&times;</button>
            </div>
            <div class="modal-body">
                <form id="newProjectForm" onsubmit="return submitNewProject(event)">
                    <!-- Project Info -->
                    <div class="form-group">
                        <label>Job Code (auto-generated)</label>
                        <input type="text" id="npJobCode" readonly style="background: var(--tf-gray-50); font-weight: 700; color: var(--tf-blue);">
                    </div>
                    <div class="form-group">
                        <label>Project Name *</label>
                        <input type="text" id="npProjectName" placeholder="e.g. Smith Residence Carport" required>
                    </div>

                    <div class="form-section-title">Customer Information</div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Customer Name</label>
                            <input type="text" id="npCustomerName" placeholder="Full name">
                        </div>
                        <div class="form-group">
                            <label>Phone</label>
                            <input type="tel" id="npCustomerPhone" placeholder="(555) 555-5555">
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" id="npCustomerEmail" placeholder="customer@email.com">
                    </div>

                    <div class="form-section-title">Project Location</div>
                    <div class="form-group">
                        <label>Street Address</label>
                        <input type="text" id="npStreet" placeholder="123 Main St">
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>City</label>
                            <input type="text" id="npCity" placeholder="City">
                        </div>
                        <div class="form-group" style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--tf-sp-2);">
                            <div>
                                <label>State</label>
                                <input type="text" id="npState" placeholder="TX" maxlength="2" style="text-transform: uppercase;">
                            </div>
                            <div>
                                <label>Zip</label>
                                <input type="text" id="npZip" placeholder="75001" maxlength="10">
                            </div>
                        </div>
                    </div>

                    <div class="form-section-title">Project Details</div>
                    <div class="form-group">
                        <label>Starting Stage</label>
                        <select id="npStage">
                            <option value="quote" selected>Quote</option>
                            <option value="contract">Contract</option>
                            <option value="engineering">Engineering</option>
                            <option value="shop_drawings">Shop Drawings</option>
                            <option value="fabrication">Fabrication</option>
                            <option value="shipping">Shipping</option>
                            <option value="install">Install</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Notes</label>
                        <textarea id="npNotes" rows="3" placeholder="Any initial notes about this project..."></textarea>
                    </div>

                    <div class="form-actions">
                        <button type="button" class="tf-btn tf-btn-outline" onclick="closeNewProjectModal()">Cancel</button>
                        <button type="submit" class="tf-btn tf-btn-primary" id="npSubmitBtn">Create Project</button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <!-- QUICK PEEK MODAL (for viewing project details from dashboard) -->
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
                <div class="info-grid" id="overviewInfo"></div>
                <div style="margin-top: var(--tf-sp-5); display: flex; gap: var(--tf-sp-3);">
                    <button class="tf-btn tf-btn-primary" id="openFullPageBtn" onclick="">Open Full Project</button>
                    <button class="tf-btn tf-btn-outline" onclick="closeProjectModal()">Close</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // ── Global State ──────────────────────────────────
        var allProjects = [];
        var filteredProjects = [];
        var currentView = 'kanban';
        var currentProject = null;
        var currentSortColumn = null;
        var currentSortDirection = 'asc';
        var inventoryAlerts = [];
        var showCompleted = false;

        document.addEventListener('DOMContentLoaded', function() {
            initializePage();
        });

        function initializePage() {
            if (USER_NAME && USER_NAME !== '{{USER_NAME}}') {
                document.getElementById('userName').textContent = USER_NAME;
            }
            var roleText = USER_ROLE && USER_ROLE !== '{{USER_ROLE}}' ? USER_ROLE : 'User';
            document.getElementById('userRole').textContent = roleText.toUpperCase();

            // Only admin + estimator can create projects
            if (USER_ROLE !== 'admin' && USER_ROLE !== 'estimator') {
                document.getElementById('newProjectBtn').style.display = 'none';
            }

            loadProjects();
            loadInventoryAlerts();
            setupEventListeners();

            if (USER_ROLE === 'shop') {
                document.querySelectorAll('.price').forEach(function(el) { el.classList.add('hidden'); });
            }
        }

        function setupEventListeners() {
            document.getElementById('projectModal').addEventListener('click', function(e) {
                if (e.target === this) closeProjectModal();
            });
            document.getElementById('newProjectModal').addEventListener('click', function(e) {
                if (e.target === this) closeNewProjectModal();
            });
        }

        // ── Load Projects (Enhanced API) ──────────────────
        function loadProjects() {
            fetch('/api/projects/full')
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    allProjects = (data.projects || []).map(normalizeProject);
                    applyFilters();
                })
                .catch(function(err) {
                    console.error('Error loading projects:', err);
                    // Fallback to old API
                    fetch('/api/projects')
                        .then(function(r) { return r.json(); })
                        .then(function(data) {
                            allProjects = (data.projects || []).map(normalizeProject);
                            applyFilters();
                        })
                        .catch(function() {
                            allProjects = [];
                            applyFilters();
                        });
                });
        }

        function normalizeProject(p) {
            // Handle both old format (from /api/projects) and new format (from /api/projects/full)
            return {
                job_code: p.job_code || p.jobCode || '',
                project_name: p.project_name || p.name || '',
                customer_name: (p.customer && p.customer.name) ? p.customer.name : (p.customer || ''),
                customer: p.customer || {},
                location: p.location || {},
                stage: (p.stage || 'quote').replace(/_/g, '-'),
                created_at: p.created_at || p.saved_at || '',
                updated_at: p.updated_at || p.saved_at || '',
                archived: p.archived || false,
                n_versions: p.n_versions || 0,
                doc_count: p.doc_count || 0,
                notes: p.notes || '',
            };
        }

        function applyFilters() {
            filteredProjects = allProjects.filter(function(p) {
                if (!showCompleted && p.stage === 'complete') return false;
                if (p.archived) return false;
                return true;
            });
            updateStats();
            renderProjects();
        }

        function toggleCompleted() {
            showCompleted = document.getElementById('showCompletedToggle').checked;
            applyFilters();
        }

        function loadInventoryAlerts() {
            fetch('/api/inventory')
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    inventoryAlerts = data.alerts || [];
                    renderInventoryAlerts();
                })
                .catch(function() {});
        }

        function updateStats() {
            var activeCount = allProjects.filter(function(p) { return p.stage !== 'complete' && !p.archived; }).length;
            var fabricatingCount = allProjects.filter(function(p) { return p.stage === 'fabrication'; }).length;
            var readyCount = allProjects.filter(function(p) { return p.stage === 'shipping'; }).length;
            document.getElementById('activeProjects').textContent = activeCount;
            document.getElementById('inFabrication').textContent = fabricatingCount;
            document.getElementById('readyToShip').textContent = readyCount;
        }

        function renderProjects() {
            if (currentView === 'kanban') renderKanban();
            else renderTable();
        }

        // ── Kanban View ───────────────────────────────────
        function renderKanban() {
            var stages = ['quote', 'contract', 'engineering', 'shop-drawings', 'fabrication', 'shipping', 'install'];
            if (showCompleted) stages.push('complete');

            var kanbanContainer = document.getElementById('kanbanView');
            kanbanContainer.innerHTML = '';

            stages.forEach(function(stage) {
                var projects = filteredProjects.filter(function(p) { return p.stage === stage; });
                var columnHeader = stage.split('-').map(function(w) { return w.charAt(0).toUpperCase() + w.slice(1); }).join(' ');

                var column = document.createElement('div');
                column.className = 'kanban-column';

                var header = document.createElement('div');
                header.className = 'column-header';
                header.textContent = columnHeader + ' (' + projects.length + ')';
                column.appendChild(header);

                projects.forEach(function(project) {
                    column.appendChild(createProjectCard(project));
                });

                kanbanContainer.appendChild(column);
            });
        }

        function createProjectCard(project) {
            var card = document.createElement('div');
            card.className = 'project-card ' + project.stage;
            card.onclick = function() { openProjectModal(project); };

            var jobCode = document.createElement('div');
            jobCode.className = 'card-job-code';
            jobCode.textContent = project.job_code;

            var name = document.createElement('div');
            name.className = 'card-project-name';
            name.textContent = project.project_name || 'Untitled';

            var customer = document.createElement('div');
            customer.className = 'card-customer';
            customer.textContent = project.customer_name || '';

            card.appendChild(jobCode);
            card.appendChild(name);
            card.appendChild(customer);

            // Doc count + version info
            var meta = document.createElement('div');
            meta.style.cssText = 'display:flex;justify-content:space-between;margin-top:var(--tf-sp-2);font-size:var(--tf-text-xs);color:var(--tf-gray-400);';
            meta.innerHTML = '<span>' + (project.doc_count || 0) + ' docs</span><span>v' + (project.n_versions || 1) + '</span>';
            card.appendChild(meta);

            return card;
        }

        // ── Table View ────────────────────────────────────
        function renderTable() {
            var tableBody = document.getElementById('tableBody');
            tableBody.innerHTML = '';

            filteredProjects.forEach(function(project) {
                var row = document.createElement('tr');
                row.onclick = function() { openProjectModal(project); };

                var stageLabel = project.stage.split('-').map(function(w) { return w.charAt(0).toUpperCase() + w.slice(1); }).join(' ');
                var stageBadgeClass = 'stage-' + project.stage;
                var updated = project.updated_at ? new Date(project.updated_at).toLocaleDateString() : '';

                row.innerHTML = '<td><strong>' + esc(project.job_code) + '</strong></td>'
                    + '<td>' + esc(project.project_name) + '</td>'
                    + '<td>' + esc(project.customer_name) + '</td>'
                    + '<td><span class="stage-badge ' + stageBadgeClass + '">' + stageLabel + '</span></td>'
                    + '<td class="price">' + (project.doc_count || 0) + ' docs</td>'
                    + '<td>' + updated + '</td>'
                    + '<td>v' + (project.n_versions || 1) + '</td>';

                tableBody.appendChild(row);
            });
        }

        function renderInventoryAlerts() {
            if (inventoryAlerts.length === 0) {
                document.getElementById('alertsSection').classList.remove('show');
                return;
            }
            document.getElementById('alertsSection').classList.add('show');
            var alertsGrid = document.getElementById('alertsGrid');
            alertsGrid.innerHTML = '';

            inventoryAlerts.forEach(function(a) {
                var alertCard = document.createElement('div');
                alertCard.className = 'alert-card ' + (a.severity === 'danger' ? 'danger' : 'warning');
                alertCard.onclick = function() { window.location.href = '/sa'; };
                alertCard.innerHTML = '<div class="alert-title">' + esc(a.itemName || a.item_name || '') + '</div>'
                    + '<div class="alert-message">' + esc(a.message || '') + '</div>';
                alertsGrid.appendChild(alertCard);
            });

            document.getElementById('inventoryAlert').style.display = 'block';
            document.getElementById('alertCount').textContent = inventoryAlerts.length;
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
            filteredProjects.sort(function(a, b) {
                var aVal, bVal;
                if (column === 'jobCode') { aVal = a.job_code; bVal = b.job_code; }
                else if (column === 'name') { aVal = a.project_name; bVal = b.project_name; }
                else if (column === 'customer') { aVal = a.customer_name; bVal = b.customer_name; }
                else if (column === 'stage') { aVal = a.stage; bVal = b.stage; }
                else if (column === 'updated') { aVal = a.updated_at; bVal = b.updated_at; }
                else { aVal = a[column]; bVal = b[column]; }
                if (typeof aVal === 'string') { aVal = (aVal || '').toLowerCase(); bVal = (bVal || '').toLowerCase(); }
                var cmp = aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
                return currentSortDirection === 'asc' ? cmp : -cmp;
            });
            renderTable();
        }

        // ── Quick Peek Modal ──────────────────────────────
        function openProjectModal(project) {
            currentProject = project;
            document.getElementById('modalTitle').textContent = project.job_code + ' — ' + (project.project_name || 'Untitled');

            var badgeGroup = document.getElementById('modalBadgeGroup');
            badgeGroup.innerHTML = '';
            var stageBadge = document.createElement('span');
            stageBadge.className = 'modal-badge';
            stageBadge.style.backgroundColor = '#1E40AF';
            stageBadge.textContent = project.stage.toUpperCase().replace(/-/g, ' ');
            badgeGroup.appendChild(stageBadge);

            if (project.n_versions > 0) {
                var vBadge = document.createElement('span');
                vBadge.className = 'modal-badge';
                vBadge.style.backgroundColor = '#F59E0B';
                vBadge.textContent = 'v' + project.n_versions;
                badgeGroup.appendChild(vBadge);
            }

            // Overview info
            var info = document.getElementById('overviewInfo');
            info.innerHTML = '';
            var items = [
                { label: 'Job Code', value: project.job_code },
                { label: 'Project Name', value: project.project_name },
                { label: 'Customer', value: project.customer_name },
                { label: 'Stage', value: project.stage.replace(/-/g, ' ').replace(/\b\w/g, function(c) { return c.toUpperCase(); }) },
                { label: 'Documents', value: (project.doc_count || 0) + ' files' },
                { label: 'Updated', value: project.updated_at ? new Date(project.updated_at).toLocaleDateString() : '-' },
            ];
            items.forEach(function(item) {
                var div = document.createElement('div');
                div.className = 'info-item';
                div.innerHTML = '<div class="info-label">' + item.label + '</div><div class="info-value">' + esc(item.value || '-') + '</div>';
                info.appendChild(div);
            });

            // "Open Full Project" button
            document.getElementById('openFullPageBtn').onclick = function() {
                window.location.href = '/project/' + encodeURIComponent(project.job_code);
            };

            document.getElementById('projectModal').classList.add('show');
        }

        function closeProjectModal() {
            document.getElementById('projectModal').classList.remove('show');
            currentProject = null;
        }

        // ── New Project Modal ─────────────────────────────
        function openNewProjectForm() {
            // Fetch next available job code
            fetch('/api/project/next-code')
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    var code = data.job_code || '';
                    document.getElementById('npJobCode').value = code;
                    document.getElementById('newJobCodeBadge').textContent = code;
                })
                .catch(function() {
                    document.getElementById('npJobCode').value = 'ERROR';
                    document.getElementById('newJobCodeBadge').textContent = 'ERROR';
                });

            // Reset form
            document.getElementById('npProjectName').value = '';
            document.getElementById('npCustomerName').value = '';
            document.getElementById('npCustomerPhone').value = '';
            document.getElementById('npCustomerEmail').value = '';
            document.getElementById('npStreet').value = '';
            document.getElementById('npCity').value = '';
            document.getElementById('npState').value = '';
            document.getElementById('npZip').value = '';
            document.getElementById('npStage').value = 'quote';
            document.getElementById('npNotes').value = '';
            document.getElementById('npSubmitBtn').disabled = false;
            document.getElementById('npSubmitBtn').textContent = 'Create Project';

            document.getElementById('newProjectModal').classList.add('show');
            setTimeout(function() { document.getElementById('npProjectName').focus(); }, 200);
        }

        function closeNewProjectModal() {
            document.getElementById('newProjectModal').classList.remove('show');
        }

        function submitNewProject(e) {
            e.preventDefault();

            var jobCode = document.getElementById('npJobCode').value.trim();
            var projectName = document.getElementById('npProjectName').value.trim();
            if (!projectName) { alert('Please enter a project name.'); return false; }

            var submitBtn = document.getElementById('npSubmitBtn');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Creating...';

            var payload = {
                job_code: jobCode,
                project_name: projectName,
                customer_name: document.getElementById('npCustomerName').value.trim(),
                customer_phone: document.getElementById('npCustomerPhone').value.trim(),
                customer_email: document.getElementById('npCustomerEmail').value.trim(),
                location_street: document.getElementById('npStreet').value.trim(),
                location_city: document.getElementById('npCity').value.trim(),
                location_state: document.getElementById('npState').value.trim().toUpperCase(),
                location_zip: document.getElementById('npZip').value.trim(),
                stage: document.getElementById('npStage').value,
                notes: document.getElementById('npNotes').value.trim(),
            };

            fetch('/api/project/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.ok) {
                    closeNewProjectModal();
                    // Navigate to the new project page
                    window.location.href = '/project/' + encodeURIComponent(data.job_code);
                } else {
                    alert('Error creating project: ' + (data.error || 'Unknown error'));
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Create Project';
                }
            })
            .catch(function(err) {
                alert('Error: ' + err.message);
                submitBtn.disabled = false;
                submitBtn.textContent = 'Create Project';
            });

            return false;
        }

        // ── Helpers ───────────────────────────────────────
        function esc(s) {
            var d = document.createElement('div');
            d.textContent = s || '';
            return d.innerHTML;
        }

        function handleLogout() {
            if (confirm('Are you sure you want to logout?')) window.location.href = '/auth/logout';
        }
    </script>
</body>
</html>
"""
