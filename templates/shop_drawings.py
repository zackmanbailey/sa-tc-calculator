"""
TitanForge v3.0 — Shop Drawing Dashboard Template
====================================================
Full-featured shop drawing management page at /shop-drawings/{JOB_CODE} with:
- Project header with quick stats (total drawings, last generated, revision)
- Questionnaire override panel (editable config fields from ShopDrawingConfig)
- Generate All button with real-time progress
- Drawing gallery with PDF preview cards (columns, rafters, purlins, cutlists, stickers, manifest)
- Individual download + Download All ZIP
- Revision history timeline
- BOM sync status indicator (shows if config diverges from BOM)
"""

from templates.shared_styles import DESIGN_SYSTEM_CSS

SHOP_DRAWINGS_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TitanForge — Shop Drawings {{JOB_CODE}}</title>
    <style>
""" + DESIGN_SYSTEM_CSS + r"""

        /* ── Shop Drawing Page Layout ──────────────────────── */
        .container {
            max-width: 1440px;
            margin: 0 auto;
            padding: var(--tf-sp-6) var(--tf-sp-8);
        }

        /* ── Page Header ───────────────────────────────────── */
        .page-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: var(--tf-sp-6);
            gap: var(--tf-sp-4);
            flex-wrap: wrap;
        }

        .page-header h1 {
            font-size: var(--tf-text-2xl);
            font-weight: 700;
            color: var(--tf-gray-900);
            letter-spacing: -0.02em;
        }

        .page-header .subtitle {
            font-size: var(--tf-text-sm);
            color: var(--tf-gray-500);
            margin-top: var(--tf-sp-1);
        }

        .page-header .job-label {
            font-size: var(--tf-text-sm);
            font-weight: 600;
            color: var(--tf-blue);
            text-transform: uppercase;
            letter-spacing: 0.02em;
            margin-bottom: var(--tf-sp-1);
        }

        /* ── Stat Row ──────────────────────────────────────── */
        .stat-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: var(--tf-sp-4);
            margin-bottom: var(--tf-sp-6);
        }

        /* ── Tab Navigation ────────────────────────────────── */
        .tab-content { display: none; }
        .tab-content.active { display: block; }

        /* ── Drawing Gallery ───────────────────────────────── */
        .drawing-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: var(--tf-sp-4);
        }

        .drawing-card {
            background: var(--tf-surface);
            border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-lg);
            overflow: hidden;
            transition: all var(--tf-duration) var(--tf-ease);
        }

        .drawing-card:hover {
            border-color: var(--tf-blue-mid);
            box-shadow: var(--tf-shadow-md);
        }

        .drawing-card .dc-preview {
            height: 180px;
            background: var(--tf-gray-100);
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            overflow: hidden;
        }

        .drawing-card .dc-preview .dc-icon {
            font-size: 3rem;
            color: var(--tf-gray-300);
        }

        .drawing-card .dc-preview .dc-type-badge {
            position: absolute;
            top: var(--tf-sp-2);
            left: var(--tf-sp-2);
            padding: 2px 10px;
            border-radius: 999px;
            font-size: var(--tf-text-xs);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .dc-type-badge.column   { background: #1E3A5F; color: #1E40AF; }
        .dc-type-badge.rafter   { background: #3B2A1A; color: #92400E; }
        .dc-type-badge.purlin   { background: #D1FAE5; color: #065F46; }
        .dc-type-badge.cutlist  { background: #E0E7FF; color: #3730A3; }
        .dc-type-badge.stickers { background: #FCE7F3; color: #9D174D; }
        .dc-type-badge.manifest { background: #F3E8FF; color: #6B21A8; }

        .drawing-card .dc-body {
            padding: var(--tf-sp-3) var(--tf-sp-4);
        }

        .drawing-card .dc-title {
            font-size: var(--tf-text-sm);
            font-weight: 600;
            color: var(--tf-gray-800);
            margin-bottom: var(--tf-sp-1);
        }

        .drawing-card .dc-meta {
            font-size: var(--tf-text-xs);
            color: var(--tf-gray-500);
            display: flex;
            gap: var(--tf-sp-3);
        }

        .drawing-card .dc-actions {
            padding: var(--tf-sp-2) var(--tf-sp-4) var(--tf-sp-3);
            display: flex;
            flex-wrap: wrap;
            gap: var(--tf-sp-2);
            border-top: 1px solid var(--tf-gray-100);
        }
        .drawing-card .dc-actions .dc-delete-btn {
            margin-left: auto;
        }

        /* ── Questionnaire Form ────────────────────────────── */
        .config-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: var(--tf-sp-4);
        }

        .config-section {
            background: var(--tf-surface);
            border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-lg);
            overflow: hidden;
        }

        .config-section-header {
            padding: var(--tf-sp-3) var(--tf-sp-4);
            font-size: var(--tf-text-xs);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            background: var(--tf-gray-50);
            border-bottom: 1px solid var(--tf-border);
            color: var(--tf-gray-700);
            display: flex;
            align-items: center;
            gap: var(--tf-sp-2);
        }

        .config-section-body {
            padding: var(--tf-sp-4);
        }

        .config-section-body .tf-form-group {
            margin-bottom: var(--tf-sp-3);
        }

        .config-section-body .tf-form-group:last-child {
            margin-bottom: 0;
        }

        .config-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: var(--tf-sp-3);
        }

        .config-input-sm {
            width: 100%;
            padding: 8px 10px;
            font-size: var(--tf-text-sm);
            border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-sm);
            outline: none;
            font-family: var(--tf-font-mono);
            background: #1E293B;
            transition: border-color var(--tf-duration) var(--tf-ease);
        }

        .config-input-sm:focus {
            border-color: var(--tf-blue-mid);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }

        .config-input-sm.changed {
            border-color: var(--tf-amber);
            background: var(--tf-amber-light);
        }

        .bom-value {
            font-size: var(--tf-text-xs);
            color: var(--tf-gray-400);
            font-family: var(--tf-font-mono);
        }

        .bom-mismatch {
            color: var(--tf-warning);
            font-weight: 600;
        }

        /* ── Generation Progress ───────────────────────────── */
        .gen-overlay {
            position: fixed;
            inset: 0;
            background: rgba(15, 23, 42, 0.7);
            backdrop-filter: blur(4px);
            z-index: 1000;
            display: none;
            align-items: center;
            justify-content: center;
        }

        .gen-overlay.show { display: flex; }

        .gen-card {
            background: var(--tf-surface);
            border-radius: var(--tf-radius-xl);
            padding: var(--tf-sp-8);
            max-width: 480px;
            width: 90%;
            text-align: center;
            box-shadow: var(--tf-shadow-lg);
        }

        .gen-card h3 {
            font-size: var(--tf-text-lg);
            font-weight: 700;
            color: var(--tf-gray-900);
            margin-bottom: var(--tf-sp-4);
        }

        .gen-progress-bar {
            width: 100%;
            height: 8px;
            background: var(--tf-gray-200);
            border-radius: 999px;
            overflow: hidden;
            margin-bottom: var(--tf-sp-3);
        }

        .gen-progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--tf-blue) 0%, var(--tf-success) 100%);
            border-radius: 999px;
            width: 0%;
            transition: width 400ms var(--tf-ease);
        }

        .gen-step-label {
            font-size: var(--tf-text-sm);
            color: var(--tf-gray-600);
            margin-bottom: var(--tf-sp-2);
        }

        .gen-step-list {
            text-align: left;
            margin-top: var(--tf-sp-4);
        }

        .gen-step-item {
            display: flex;
            align-items: center;
            gap: var(--tf-sp-2);
            padding: var(--tf-sp-1) 0;
            font-size: var(--tf-text-sm);
            color: var(--tf-gray-500);
        }

        .gen-step-item.done { color: var(--tf-success); }
        .gen-step-item.active { color: var(--tf-blue); font-weight: 600; }
        .gen-step-item.error { color: var(--tf-danger); }

        /* ── Revision History ──────────────────────────────── */
        .revision-timeline {
            position: relative;
            padding-left: 24px;
        }

        .revision-timeline::before {
            content: '';
            position: absolute;
            left: 8px;
            top: 4px;
            bottom: 4px;
            width: 2px;
            background: var(--tf-gray-200);
        }

        .revision-item {
            position: relative;
            padding-bottom: var(--tf-sp-4);
        }

        .revision-item::before {
            content: '';
            position: absolute;
            left: -20px;
            top: 5px;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: var(--tf-blue);
            border: 2px solid var(--tf-surface);
            box-shadow: 0 0 0 2px var(--tf-blue-light);
        }

        .revision-item.current::before {
            background: var(--tf-success);
            box-shadow: 0 0 0 2px var(--tf-success-bg);
        }

        .revision-label {
            font-size: var(--tf-text-sm);
            font-weight: 600;
            color: var(--tf-gray-800);
        }

        .revision-date {
            font-size: var(--tf-text-xs);
            color: var(--tf-gray-500);
        }

        .revision-files {
            font-size: var(--tf-text-xs);
            color: var(--tf-gray-400);
            margin-top: 2px;
        }

        /* ── Sync Status Banner ────────────────────────────── */
        .sync-banner {
            display: none;
            padding: var(--tf-sp-3) var(--tf-sp-4);
            border-radius: var(--tf-radius);
            margin-bottom: var(--tf-sp-4);
            font-size: var(--tf-text-sm);
            align-items: center;
            gap: var(--tf-sp-3);
        }

        .sync-banner.show { display: flex; }

        .sync-banner.synced {
            background: var(--tf-success-bg);
            border-left: 4px solid var(--tf-success);
            color: #064E3B;
        }

        .sync-banner.diverged {
            background: var(--tf-warning-bg);
            border-left: 4px solid var(--tf-warning);
            color: #78350F;
        }

        /* ── Conflict Resolution Modal ─────────────────────── */
        .conflict-table {
            width: 100%;
            border-collapse: collapse;
            font-size: var(--tf-text-sm);
            margin-top: var(--tf-sp-3);
        }

        .conflict-table th {
            text-align: left;
            font-size: var(--tf-text-xs);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: var(--tf-gray-500);
            padding: var(--tf-sp-2) var(--tf-sp-3);
            border-bottom: 2px solid var(--tf-border);
        }

        .conflict-table td {
            padding: var(--tf-sp-2) var(--tf-sp-3);
            border-bottom: 1px solid var(--tf-gray-100);
            vertical-align: middle;
        }

        .conflict-table .val-current {
            color: var(--tf-warning);
            font-family: var(--tf-font-mono);
            font-weight: 600;
        }

        .conflict-table .val-bom {
            color: var(--tf-success);
            font-family: var(--tf-font-mono);
            font-weight: 600;
        }

        .conflict-table .val-arrow {
            color: var(--tf-gray-400);
            text-align: center;
        }

        .conflict-table input[type="checkbox"] {
            width: 18px;
            height: 18px;
            cursor: pointer;
            accent-color: var(--tf-blue);
        }

        .conflict-summary {
            padding: var(--tf-sp-3) var(--tf-sp-4);
            background: var(--tf-info-bg);
            border-left: 4px solid var(--tf-info);
            border-radius: var(--tf-radius);
            font-size: var(--tf-text-sm);
            color: #0C4A6E;
            margin-bottom: var(--tf-sp-4);
        }

        .conflict-actions {
            display: flex;
            gap: var(--tf-sp-2);
            justify-content: flex-end;
            padding-top: var(--tf-sp-4);
            border-top: 1px solid var(--tf-border);
            margin-top: var(--tf-sp-4);
        }

        /* ── Empty State ───────────────────────────────────── */
        .empty-state {
            text-align: center;
            padding: var(--tf-sp-12) var(--tf-sp-6);
            color: var(--tf-gray-400);
        }

        .empty-state .empty-icon {
            font-size: 4rem;
            margin-bottom: var(--tf-sp-4);
        }

        .empty-state h3 {
            font-size: var(--tf-text-lg);
            color: var(--tf-gray-600);
            margin-bottom: var(--tf-sp-2);
        }

        .empty-state p {
            font-size: var(--tf-text-sm);
            max-width: 400px;
            margin: 0 auto var(--tf-sp-5);
            line-height: 1.6;
        }

        /* ── Responsive ────────────────────────────────────── */
        @media (max-width: 768px) {
            .container { padding: var(--tf-sp-4); }
            .config-grid { grid-template-columns: 1fr; }
            .drawing-grid { grid-template-columns: 1fr; }
            .stat-row { grid-template-columns: 1fr 1fr; }
            .page-header { flex-direction: column; }
        }
    </style>
</head>
<body>
    <!-- ── Topbar ──────────────────────────────────────────── -->
    <div class="tf-topbar">
        <a href="/" class="tf-logo">
            <div class="tf-logo-icon">T</div>
            TitanForge
        </a>
        <nav>
            <a href="/">Dashboard</a>
            <a href="/sa">SA Estimator</a>
            <a href="/tc">TC Quotes</a>
            <a href="/customers">Customers</a>
            <a href="/shop-floor">Shop Floor</a>
            <a href="/project/{{JOB_CODE}}">Project</a>
            <a class="active" href="#">Shop Drawings</a>
            <a href="/work-orders/{{JOB_CODE}}">Work Orders</a>
        </nav>
        <div class="tf-user">
            <span>{{USER_NAME}}</span>
            <a href="/auth/logout">Sign Out</a>
        </div>
    </div>

    <div class="container">
        <!-- ── Page Header ─────────────────────────────────── -->
        <div class="page-header">
            <div>
                <div class="job-label">{{JOB_CODE}}</div>
                <h1>Shop Drawings</h1>
                <div class="subtitle" id="projectSubtitle">Loading project...</div>
            </div>
            <div class="tf-flex tf-gap-2">
                <a href="/project/{{JOB_CODE}}" class="tf-btn tf-btn-outline tf-btn-sm">
                    Back to Project
                </a>
                <a href="/work-orders/{{JOB_CODE}}" class="tf-btn tf-btn-outline tf-btn-sm" style="border-color:var(--tf-green);color:var(--tf-green);">
                    Work Orders
                </a>
                <button class="tf-btn tf-btn-amber tf-btn-sm" onclick="generateAll()">
                    Collect Drawings
                </button>
                <button class="tf-btn tf-btn-primary tf-btn-sm" onclick="downloadAllZip()" id="btnDownloadAll" disabled>
                    Download ZIP
                </button>
            </div>
        </div>

        <!-- ── BOM Sync Status ─────────────────────────────── -->
        <div class="sync-banner" id="syncBanner">
            <span id="syncIcon"></span>
            <span id="syncText"></span>
            <button class="tf-btn tf-btn-sm tf-btn-ghost" id="syncAction" style="margin-left:auto" onclick="resyncFromBOM()">
                Re-sync from BOM
            </button>
        </div>

        <!-- ── Stat Row ────────────────────────────────────── -->
        <div class="stat-row">
            <div class="tf-stat">
                <div class="tf-stat-icon blue">&#128196;</div>
                <div>
                    <div class="tf-stat-value" id="statFiles">0</div>
                    <div class="tf-stat-label">Drawings</div>
                </div>
            </div>
            <div class="tf-stat">
                <div class="tf-stat-icon amber">&#128203;</div>
                <div>
                    <div class="tf-stat-value" id="statRevision">-</div>
                    <div class="tf-stat-label">Revision</div>
                </div>
            </div>
            <div class="tf-stat">
                <div class="tf-stat-icon green">&#128230;</div>
                <div>
                    <div class="tf-stat-value" id="statSize">-</div>
                    <div class="tf-stat-label">Total Size</div>
                </div>
            </div>
            <div class="tf-stat">
                <div class="tf-stat-icon red">&#128337;</div>
                <div>
                    <div class="tf-stat-value" id="statGenerated">Never</div>
                    <div class="tf-stat-label">Last Generated</div>
                </div>
            </div>
        </div>

        <!-- ── Building Selector ─────────────────────────── -->
        <div id="buildingSelector" style="display:none;margin-bottom:var(--tf-sp-4);">
            <div style="font-size:var(--tf-text-xs);color:var(--tf-gray-500);margin-bottom:6px;font-weight:600;text-transform:uppercase;letter-spacing:0.04em;">
                Select Building
            </div>
            <div id="buildingTabs" style="display:flex;gap:8px;flex-wrap:wrap;"></div>
        </div>

        <!-- ── Tab Bar ─────────────────────────────────────── -->
        <div class="tf-tabs">
            <button class="tf-tab active" onclick="showTab('drawings')">Drawings</button>
            <button class="tf-tab" onclick="showTab('interactive')">Interactive Builder</button>
            <button class="tf-tab" onclick="showTab('config')">Configuration</button>
            <button class="tf-tab" onclick="showTab('history')">Revision History</button>
        </div>

        <!-- ══════════════════════════════════════════════════ -->
        <!--  TAB 1: DRAWING GALLERY                           -->
        <!-- ══════════════════════════════════════════════════ -->
        <div class="tab-content active" id="tab-drawings">
            <div id="drawingsEmpty" class="empty-state">
                <div class="empty-icon">&#128209;</div>
                <h3>No Drawings Yet</h3>
                <p>Use the <strong>Interactive Builder</strong> tab to create shop drawings for all components, then click <strong>Collect Drawings</strong> to package them here.</p>
                <button class="tf-btn tf-btn-primary tf-btn-sm" onclick="showTab('interactive');document.querySelectorAll('.tf-tab')[1].click();" style="margin-right:8px;">
                    Open Interactive Builder
                </button>
                <button class="tf-btn tf-btn-amber" onclick="generateAll()">
                    Collect Drawings
                </button>
            </div>
            <div id="drawingsGrid" class="drawing-grid" style="display:none"></div>
        </div>

        <!-- ══════════════════════════════════════════════════ -->
        <!--  TAB: INTERACTIVE BUILDER                         -->
        <!-- ══════════════════════════════════════════════════ -->
        <div class="tab-content" id="tab-interactive">
            <div style="padding:8px 0;">
                <h3 id="builderTitle" style="font-size:var(--tf-text-md);font-weight:700;color:var(--tf-gray-900);margin-bottom:4px;">
                    Interactive Shop Drawing Builder
                </h3>
                <div id="builderBuildingLabel" style="display:none;font-size:var(--tf-text-xs);font-weight:600;color:var(--tf-blue-600,#2563EB);margin-bottom:4px;padding:4px 10px;background:var(--tf-blue-50,#EFF6FF);border-radius:6px;display:inline-block;"></div>
                <p style="font-size:var(--tf-text-xs);color:var(--tf-gray-500);margin-bottom:20px;">
                    Build detailed, dimensioned shop drawings in-browser. Adjust dimensions, add notes, and save directly as PDF.
                </p>
                <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px;">

                    <!-- Column Drawing Builder -->
                    <div style="background:var(--tf-surface);border:1px solid var(--tf-gray-200);border-radius:12px;padding:24px;transition:box-shadow .2s;">
                        <div style="font-size:2rem;margin-bottom:12px;">&#128295;</div>
                        <h4 style="font-size:var(--tf-text-sm);font-weight:700;color:var(--tf-gray-800);margin-bottom:6px;">Column Drawing</h4>
                        <p style="font-size:var(--tf-text-xs);color:var(--tf-gray-500);margin-bottom:16px;">
                            Interactive column shop drawing with front, side, and top views. Configurable dimensions, base plates, bolt patterns, and cap plates.
                        </p>
                        <a href="/shop-drawings/{{JOB_CODE}}/column" data-drawing-type="column"
                           class="tf-btn tf-btn-primary tf-btn-sm" style="text-decoration:none;display:inline-block;">
                            Open Column Builder
                        </a>
                    </div>

                    <!-- Rafter Drawing Builder -->
                    <div style="background:var(--tf-surface);border:1px solid var(--tf-gray-200);border-radius:12px;padding:24px;transition:box-shadow .2s;">
                        <div style="font-size:2rem;margin-bottom:12px;">&#9650;</div>
                        <h4 style="font-size:var(--tf-text-sm);font-weight:700;color:var(--tf-gray-800);margin-bottom:6px;">Rafter Drawing</h4>
                        <p style="font-size:var(--tf-text-xs);color:var(--tf-gray-500);margin-bottom:16px;">
                            Interactive rafter shop drawing with pitch angles, purlin locations, splice points, and connection details.
                        </p>
                        <a href="/shop-drawings/{{JOB_CODE}}/rafter" data-drawing-type="rafter"
                           class="tf-btn tf-btn-primary tf-btn-sm" style="text-decoration:none;display:inline-block;">
                            Open Rafter Builder
                        </a>
                    </div>

                    <!-- Purlin Drawing Builder -->
                    <div style="background:var(--tf-surface);border:1px solid var(--tf-gray-200);border-radius:12px;padding:24px;transition:box-shadow .2s;">
                        <div style="font-size:2rem;margin-bottom:12px;">&#9552;</div>
                        <h4 style="font-size:var(--tf-text-sm);font-weight:700;color:var(--tf-gray-800);margin-bottom:6px;">Purlin Drawing</h4>
                        <p style="font-size:var(--tf-text-xs);color:var(--tf-gray-500);margin-bottom:16px;">
                            Z-purlin with elevation view, cross-section, P1 clip connection detail, sag rod connection, and lap splice detail.
                        </p>
                        <a href="/shop-drawings/{{JOB_CODE}}/purlin" data-drawing-type="purlin"
                           class="tf-btn tf-btn-primary tf-btn-sm" style="text-decoration:none;display:inline-block;">
                            Open Purlin Builder
                        </a>
                    </div>

                    <!-- Purlin Layout Builder -->
                    <div style="background:var(--tf-surface);border:1px solid var(--tf-gray-200);border-radius:12px;padding:24px;transition:box-shadow .2s;">
                        <div style="font-size:2rem;margin-bottom:12px;">&#9638;</div>
                        <h4 style="font-size:var(--tf-text-sm);font-weight:700;color:var(--tf-gray-800);margin-bottom:6px;">Purlin Layout</h4>
                        <p style="font-size:var(--tf-text-xs);color:var(--tf-gray-500);margin-bottom:16px;">
                            Full building-length purlin layout with C/Z purlin options, solar panel mode, piece breaks, cut list, and 4-option cost comparison.
                        </p>
                        <a href="/shop-drawings/{{JOB_CODE}}/purlin-layout" data-drawing-type="purlin_layout"
                           class="tf-btn tf-btn-primary tf-btn-sm" style="text-decoration:none;display:inline-block;">
                            Open Purlin Layout
                        </a>
                    </div>

                    <!-- Sag Rod Drawing Builder -->
                    <div style="background:var(--tf-surface);border:1px solid var(--tf-gray-200);border-radius:12px;padding:24px;transition:box-shadow .2s;">
                        <div style="font-size:2rem;margin-bottom:12px;">&#128296;</div>
                        <h4 style="font-size:var(--tf-text-sm);font-weight:700;color:var(--tf-gray-800);margin-bottom:6px;">Sag Rod Drawing</h4>
                        <p style="font-size:var(--tf-text-xs);color:var(--tf-gray-500);margin-bottom:16px;">
                            2&quot;x2&quot; angle sag rod with elevation, L-section, purlin connection detail, and angle cut detail.
                        </p>
                        <a href="/shop-drawings/{{JOB_CODE}}/sagrod" data-drawing-type="sagrod"
                           class="tf-btn tf-btn-primary tf-btn-sm" style="text-decoration:none;display:inline-block;">
                            Open Sag Rod Builder
                        </a>
                    </div>

                    <!-- Strap Drawing Builder -->
                    <div style="background:var(--tf-surface);border:1px solid var(--tf-gray-200);border-radius:12px;padding:24px;transition:box-shadow .2s;">
                        <div style="font-size:2rem;margin-bottom:12px;">&#127744;</div>
                        <h4 style="font-size:var(--tf-text-sm);font-weight:700;color:var(--tf-gray-800);margin-bottom:6px;">Hurricane Strap Drawing</h4>
                        <p style="font-size:var(--tf-text-xs);color:var(--tf-gray-500);margin-bottom:16px;">
                            1.5&quot;x10GA flat strap with elevation, cross-section, connection details, and hole pattern.
                        </p>
                        <a href="/shop-drawings/{{JOB_CODE}}/strap" data-drawing-type="strap"
                           class="tf-btn tf-btn-primary tf-btn-sm" style="text-decoration:none;display:inline-block;">
                            Open Strap Builder
                        </a>
                    </div>

                    <!-- Endcap Drawing Builder -->
                    <div style="background:var(--tf-surface);border:1px solid var(--tf-gray-200);border-radius:12px;padding:24px;transition:box-shadow .2s;">
                        <div style="font-size:2rem;margin-bottom:12px;">&#9632;</div>
                        <h4 style="font-size:var(--tf-text-sm);font-weight:700;color:var(--tf-gray-800);margin-bottom:6px;">Endcap Drawing</h4>
                        <p style="font-size:var(--tf-text-xs);color:var(--tf-gray-500);margin-bottom:16px;">
                            U-channel endcap with elevation, U-section, top/bottom connections, and panel termination detail.
                        </p>
                        <a href="/shop-drawings/{{JOB_CODE}}/endcap" data-drawing-type="endcap"
                           class="tf-btn tf-btn-primary tf-btn-sm" style="text-decoration:none;display:inline-block;">
                            Open Endcap Builder
                        </a>
                    </div>

                    <!-- P1 Clip Drawing Builder -->
                    <div style="background:var(--tf-surface);border:1px solid var(--tf-gray-200);border-radius:12px;padding:24px;transition:box-shadow .2s;">
                        <div style="font-size:2rem;margin-bottom:12px;">&#128204;</div>
                        <h4 style="font-size:var(--tf-text-sm);font-weight:700;color:var(--tf-gray-800);margin-bottom:6px;">P1 Clip Drawing</h4>
                        <p style="font-size:var(--tf-text-xs);color:var(--tf-gray-500);margin-bottom:16px;">
                            L-shaped bent clip with front view, side view, hole pattern, and installed assembly view.
                        </p>
                        <a href="/shop-drawings/{{JOB_CODE}}/p1clip" data-drawing-type="p1clip"
                           class="tf-btn tf-btn-primary tf-btn-sm" style="text-decoration:none;display:inline-block;">
                            Open P1 Clip Builder
                        </a>
                    </div>

                    <!-- P2 Plate Drawing Builder -->
                    <div style="background:var(--tf-surface);border:1px solid var(--tf-gray-200);border-radius:12px;padding:24px;transition:box-shadow .2s;">
                        <div style="font-size:2rem;margin-bottom:12px;">&#128207;</div>
                        <h4 style="font-size:var(--tf-text-sm);font-weight:700;color:var(--tf-gray-800);margin-bottom:6px;">P2 Eave Plate Drawing</h4>
                        <p style="font-size:var(--tf-text-xs);color:var(--tf-gray-500);margin-bottom:16px;">
                            9&quot;x24&quot; eave plate with front view, side L-bend view, hole pattern, and installed assembly view.
                        </p>
                        <a href="/shop-drawings/{{JOB_CODE}}/p2plate" data-drawing-type="p2plate"
                           class="tf-btn tf-btn-primary tf-btn-sm" style="text-decoration:none;display:inline-block;">
                            Open P2 Plate Builder
                        </a>
                    </div>

                    <!-- Splice Plate Drawing Builder -->
                    <div style="background:var(--tf-surface);border:1px solid var(--tf-gray-200);border-radius:12px;padding:24px;transition:box-shadow .2s;">
                        <div style="font-size:2rem;margin-bottom:12px;">&#128279;</div>
                        <h4 style="font-size:var(--tf-text-sm);font-weight:700;color:var(--tf-gray-800);margin-bottom:6px;">Splice Plate Drawing</h4>
                        <p style="font-size:var(--tf-text-xs);color:var(--tf-gray-500);margin-bottom:16px;">
                            Beam splice plate with bolt pattern, side assembly view, cross-section, and torque specifications.
                        </p>
                        <a href="/shop-drawings/{{JOB_CODE}}/splice" data-drawing-type="splice"
                           class="tf-btn tf-btn-primary tf-btn-sm" style="text-decoration:none;display:inline-block;">
                            Open Splice Builder
                        </a>
                    </div>

                </div>
            </div>
        </div>

        <!-- ══════════════════════════════════════════════════ -->
        <!--  TAB 2: CONFIGURATION / QUESTIONNAIRE             -->
        <!-- ══════════════════════════════════════════════════ -->
        <div class="tab-content" id="tab-config">
            <div class="tf-flex tf-justify-between tf-items-center tf-mb-4">
                <div>
                    <h3 style="font-size:var(--tf-text-md);font-weight:700;color:var(--tf-gray-900)">
                        Drawing Configuration
                    </h3>
                    <p style="font-size:var(--tf-text-xs);color:var(--tf-gray-500);margin-top:2px">
                        Values auto-populated from BOM. Override any field &mdash; yellow highlight = diverges from BOM.
                    </p>
                </div>
                <div class="tf-flex tf-gap-2">
                    <button class="tf-btn tf-btn-outline tf-btn-sm" onclick="resetToBOM()">
                        Reset to BOM
                    </button>
                    <button class="tf-btn tf-btn-primary tf-btn-sm" onclick="saveConfig()">
                        Save Configuration
                    </button>
                </div>
            </div>

            <div class="config-grid">
                <!-- Project Info Section -->
                <div class="config-section">
                    <div class="config-section-header">
                        &#128196; Project Info
                    </div>
                    <div class="config-section-body">
                        <div class="tf-form-group">
                            <label class="tf-label">Project Name</label>
                            <input class="config-input-sm" data-field="project_name" type="text">
                        </div>
                        <div class="tf-form-group">
                            <label class="tf-label">Customer</label>
                            <input class="config-input-sm" data-field="customer_name" type="text">
                        </div>
                        <div class="tf-form-group">
                            <label class="tf-label">Location</label>
                            <input class="config-input-sm" data-field="project_location" type="text">
                        </div>
                        <div class="config-row">
                            <div class="tf-form-group">
                                <label class="tf-label">Drawn By</label>
                                <input class="config-input-sm" data-field="drawn_by" type="text">
                            </div>
                            <div class="tf-form-group">
                                <label class="tf-label">Checked By</label>
                                <input class="config-input-sm" data-field="checked_by" type="text">
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Building Parameters -->
                <div class="config-section">
                    <div class="config-section-header">
                        &#127970; Building Parameters
                    </div>
                    <div class="config-section-body">
                        <div class="config-row">
                            <div class="tf-form-group">
                                <label class="tf-label">Width (ft)</label>
                                <input class="config-input-sm" data-field="building_width_ft" type="number" step="0.01">
                                <div class="bom-value" data-bom-field="building_width_ft"></div>
                            </div>
                            <div class="tf-form-group">
                                <label class="tf-label">Length (ft)</label>
                                <input class="config-input-sm" data-field="building_length_ft" type="number" step="0.01">
                                <div class="bom-value" data-bom-field="building_length_ft"></div>
                            </div>
                        </div>
                        <div class="config-row">
                            <div class="tf-form-group">
                                <label class="tf-label">Clear Height (ft)</label>
                                <input class="config-input-sm" data-field="clear_height_ft" type="number" step="0.01">
                                <div class="bom-value" data-bom-field="clear_height_ft"></div>
                            </div>
                            <div class="tf-form-group">
                                <label class="tf-label">Roof Pitch (&deg;)</label>
                                <input class="config-input-sm" data-field="roof_pitch_deg" type="number" step="0.01">
                                <div class="bom-value" data-bom-field="roof_pitch_deg"></div>
                            </div>
                        </div>
                        <div class="config-row">
                            <div class="tf-form-group">
                                <label class="tf-label">Frame Type</label>
                                <select class="config-input-sm" data-field="frame_type">
                                    <option value="tee">Tee (Mono-post)</option>
                                    <option value="2post">2-Post</option>
                                </select>
                            </div>
                            <div class="tf-form-group">
                                <label class="tf-label"># Frames</label>
                                <input class="config-input-sm" data-field="n_frames" type="number" step="1">
                                <div class="bom-value" data-bom-field="n_frames"></div>
                            </div>
                        </div>
                        <div class="config-row">
                            <div class="tf-form-group">
                                <label class="tf-label">Embedment (ft)</label>
                                <input class="config-input-sm" data-field="embedment_ft" type="number" step="0.001">
                            </div>
                            <div class="tf-form-group">
                                <label class="tf-label">Column Buffer (ft)</label>
                                <input class="config-input-sm" data-field="column_buffer_ft" type="number" step="0.1">
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Column Config -->
                <div class="config-section">
                    <div class="config-section-header">
                        &#128295; Column Configuration
                    </div>
                    <div class="config-section-body">
                        <div class="tf-form-group">
                            <label class="tf-label">Material Grade</label>
                            <input class="config-input-sm" data-field="col_material_grade" type="text">
                        </div>
                        <div class="config-row">
                            <div class="tf-form-group">
                                <label class="tf-label">Cap Plate Thick</label>
                                <input class="config-input-sm" data-field="col_cap_plate_thickness" type="text">
                            </div>
                            <div class="tf-form-group">
                                <label class="tf-label">Cap Plate W (in)</label>
                                <input class="config-input-sm" data-field="col_cap_plate_width_in" type="number" step="0.5">
                            </div>
                        </div>
                        <div class="config-row">
                            <div class="tf-form-group">
                                <label class="tf-label">Bolt Hole Dia</label>
                                <input class="config-input-sm" data-field="col_bolt_hole_dia" type="text">
                            </div>
                            <div class="tf-form-group">
                                <label class="tf-label">Gusset Thick</label>
                                <input class="config-input-sm" data-field="col_gusset_thickness" type="text">
                            </div>
                        </div>
                        <div class="config-row">
                            <div class="tf-form-group">
                                <label class="tf-label">Rebar Size</label>
                                <select class="config-input-sm" data-field="col_rebar_size">
                                    <option value="#5">#5</option>
                                    <option value="#7">#7</option>
                                    <option value="#9">#9</option>
                                </select>
                            </div>
                            <div class="tf-form-group">
                                <label class="tf-label">Reinforced</label>
                                <select class="config-input-sm" data-field="col_reinforced">
                                    <option value="true">Yes — Rebar Inside</option>
                                    <option value="false">No — Rebar Outside</option>
                                </select>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Rafter Config -->
                <div class="config-section">
                    <div class="config-section-header">
                        &#9650; Rafter Configuration
                    </div>
                    <div class="config-section-body">
                        <div class="config-row">
                            <div class="tf-form-group">
                                <label class="tf-label">Roofing Overhang (ft)</label>
                                <input class="config-input-sm" data-field="raft_roofing_overhang_ft" type="number" step="0.1">
                            </div>
                            <div class="tf-form-group">
                                <label class="tf-label">Purlin Type</label>
                                <select class="config-input-sm" data-field="raft_purlin_type">
                                    <option value="z">Z-Purlin</option>
                                    <option value="c">C-Purlin</option>
                                </select>
                            </div>
                        </div>
                        <div class="config-row">
                            <div class="tf-form-group">
                                <label class="tf-label">P1 Clip (W x L in)</label>
                                <div class="config-row" style="gap:var(--tf-sp-2)">
                                    <input class="config-input-sm" data-field="raft_p1_width_in" type="number" step="0.5" placeholder="W">
                                    <input class="config-input-sm" data-field="raft_p1_length_in" type="number" step="0.5" placeholder="L">
                                </div>
                            </div>
                            <div class="tf-form-group">
                                <label class="tf-label">P2 Cap (W x L in)</label>
                                <div class="config-row" style="gap:var(--tf-sp-2)">
                                    <input class="config-input-sm" data-field="raft_p2_width_in" type="number" step="0.5" placeholder="W">
                                    <input class="config-input-sm" data-field="raft_p2_length_in" type="number" step="0.5" placeholder="L">
                                </div>
                            </div>
                        </div>
                        <div class="config-row">
                            <div class="tf-form-group">
                                <label class="tf-label">Reinforced</label>
                                <select class="config-input-sm" data-field="raft_reinforced">
                                    <option value="true">Yes — Rebar</option>
                                    <option value="false">No — No Rebar</option>
                                </select>
                            </div>
                            <div class="tf-form-group">
                                <label class="tf-label">Rebar Size</label>
                                <select class="config-input-sm" data-field="raft_rebar_size">
                                    <option value="#5">#5</option>
                                    <option value="#7">#7</option>
                                    <option value="#9">#9</option>
                                </select>
                            </div>
                        </div>
                        <div class="config-row">
                            <div class="tf-form-group">
                                <label class="tf-label">Show Purlin Facing on Rafter Drawing</label>
                                <select class="config-input-sm" data-field="raft_show_purlin_facing">
                                    <option value="false">Off</option>
                                    <option value="true">On — Show Z-purlin facing arrows</option>
                                </select>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Purlin Config -->
                <div class="config-section">
                    <div class="config-section-header">
                        &#9644; Purlin Configuration
                    </div>
                    <div class="config-section-body">
                        <div class="config-row">
                            <div class="tf-form-group">
                                <label class="tf-label">Type</label>
                                <select class="config-input-sm" data-field="purlin_type">
                                    <option value="z">Z-Purlin</option>
                                    <option value="c">C-Purlin</option>
                                </select>
                            </div>
                            <div class="tf-form-group">
                                <label class="tf-label">Gauge</label>
                                <select class="config-input-sm" data-field="purlin_gauge">
                                    <option value="12GA">12 GA</option>
                                    <option value="14GA">14 GA</option>
                                    <option value="16GA">16 GA</option>
                                </select>
                            </div>
                        </div>
                        <div class="config-row">
                            <div class="tf-form-group">
                                <label class="tf-label">Spacing (ft)</label>
                                <input class="config-input-sm" data-field="purlin_spacing_ft" type="number" step="0.5">
                                <div class="bom-value" data-bom-field="purlin_spacing_ft"></div>
                            </div>
                            <div class="tf-form-group">
                                <label class="tf-label">Overhang (ft)</label>
                                <input class="config-input-sm" data-field="purlin_overhang_ft" type="number" step="0.5">
                            </div>
                        </div>
                        <div class="config-row">
                            <div class="tf-form-group">
                                <label class="tf-label">Splice Overlap (in)</label>
                                <input class="config-input-sm" data-field="purlin_splice_overlap_in" type="number" step="1">
                            </div>
                            <div class="tf-form-group">
                                <label class="tf-label">End Extension (in)</label>
                                <input class="config-input-sm" data-field="purlin_end_extension_in" type="number" step="1">
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Wall Config -->
                <div class="config-section">
                    <div class="config-section-header">
                        &#127960; Wall Configuration
                    </div>
                    <div class="config-section-body">
                        <div class="config-row">
                            <div class="tf-form-group">
                                <label class="tf-label">Back Wall</label>
                                <select class="config-input-sm" data-field="has_back_wall">
                                    <option value="false">No</option>
                                    <option value="true">Yes</option>
                                </select>
                            </div>
                            <div class="tf-form-group">
                                <label class="tf-label">Side Walls</label>
                                <select class="config-input-sm" data-field="has_side_walls">
                                    <option value="false">No</option>
                                    <option value="true">Yes</option>
                                </select>
                            </div>
                        </div>
                        <div class="config-row">
                            <div class="tf-form-group">
                                <label class="tf-label">Girt Spacing (ft)</label>
                                <input class="config-input-sm" data-field="wall_girt_spacing_ft" type="number" step="0.5">
                            </div>
                            <div class="tf-form-group">
                                <label class="tf-label">Ground Clearance (in)</label>
                                <input class="config-input-sm" data-field="wall_panel_ground_clearance_in" type="number" step="1">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- ══════════════════════════════════════════════════ -->
        <!--  TAB 3: REVISION HISTORY                          -->
        <!-- ══════════════════════════════════════════════════ -->
        <div class="tab-content" id="tab-history">
            <div class="tf-card" style="max-width:640px">
                <div class="tf-card-header accent-blue">
                    Revision History
                </div>
                <div class="tf-card-body">
                    <div id="revisionTimeline" class="revision-timeline">
                        <div class="empty-state" style="padding:var(--tf-sp-6)">
                            <p style="color:var(--tf-gray-500);font-size:var(--tf-text-sm)">
                                No revisions yet. Generate shop drawings to create the first revision.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- ── Generation Progress Overlay ─────────────────────── -->
    <div class="gen-overlay" id="genOverlay">
        <div class="gen-card">
            <h3>Generating Shop Drawings</h3>
            <div class="gen-progress-bar">
                <div class="gen-progress-fill" id="genProgressFill"></div>
            </div>
            <div class="gen-step-label" id="genStepLabel">Initializing...</div>
            <div class="gen-step-list" id="genStepList"></div>
        </div>
    </div>

    <!-- ── Conflict Resolution Modal ──────────────────────── -->
    <div class="tf-modal-overlay" id="conflictOverlay">
        <div class="tf-modal" style="max-width:700px">
            <div class="tf-modal-header">
                <h3>BOM Values Changed</h3>
                <button class="tf-modal-close" onclick="closeConflictModal()">&times;</button>
            </div>
            <div class="tf-modal-body">
                <div class="conflict-summary" id="conflictSummary"></div>
                <div style="margin-bottom:var(--tf-sp-2);display:flex;justify-content:space-between;align-items:center">
                    <label style="font-size:var(--tf-text-xs);font-weight:600;color:var(--tf-gray-600)">
                        Check fields to accept BOM values:
                    </label>
                    <button class="tf-btn tf-btn-ghost tf-btn-sm" onclick="toggleAllConflicts()">
                        Select / Deselect All
                    </button>
                </div>
                <table class="conflict-table">
                    <thead>
                        <tr>
                            <th style="width:30px"></th>
                            <th>Field</th>
                            <th>Your Value</th>
                            <th style="width:30px"></th>
                            <th>BOM Value</th>
                        </tr>
                    </thead>
                    <tbody id="conflictBody"></tbody>
                </table>
                <div class="conflict-actions">
                    <button class="tf-btn tf-btn-outline" onclick="closeConflictModal()">
                        Keep All My Values
                    </button>
                    <button class="tf-btn tf-btn-primary" onclick="applySelectedConflicts()">
                        Accept Selected Changes
                    </button>
                    <button class="tf-btn tf-btn-amber" onclick="acceptAllConflicts()">
                        Accept All BOM Values
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- ══════════════════════════════════════════════════════ -->
    <!--  JAVASCRIPT                                           -->
    <!-- ══════════════════════════════════════════════════════ -->
    <script>
    (function() {
        'use strict';

        // ── State ──
        const JOB_CODE = '{{JOB_CODE}}';
        let config = {};           // Current config (ShopDrawingConfig fields)
        let bomConfig = {};        // Config as last derived from BOM
        let drawings = [];         // Last generation result files
        let revisions = [];        // Revision history
        let generationLog = null;
        let buildings = [];        // Buildings array from BOM
        let selectedBuilding = 'B1';  // Currently selected building ID

        const DRAWING_TYPES = {
            column:   { label: 'Column',   icon: '&#128295;', plural: 'Columns' },
            rafter:   { label: 'Rafter',   icon: '&#9650;',   plural: 'Rafters' },
            other:    { label: 'Drawing',  icon: '&#128196;', plural: 'Drawings' },
        };

        const GEN_STEPS = [
            { key: 'scanning', label: 'Scanning for saved drawings' },
            { key: 'columns',  label: 'Column Drawings' },
            { key: 'rafters',  label: 'Rafter Drawings' },
            { key: 'packaging', label: 'Packaging results' },
        ];

        // ── Project context bar ──
        (function() {
            var ctxBar = document.createElement('div');
            ctxBar.style.cssText = 'background:linear-gradient(135deg,rgba(200,154,46,0.15),rgba(200,154,46,0.05));padding:8px 20px;display:flex;align-items:center;gap:12px;border-bottom:1px solid rgba(200,154,46,0.3);font-size:13px;color:#C89A2E;';
            ctxBar.innerHTML = '<span>\ud83d\udcc1 Project: <strong>' + JOB_CODE + '</strong></span><a href="/project/' + encodeURIComponent(JOB_CODE) + '" style="margin-left:auto;color:#C89A2E;text-decoration:none;font-weight:600;">\u2190 Back to Project</a><a href="/project/' + encodeURIComponent(JOB_CODE) + '/bom" style="color:#C89A2E;text-decoration:none;">\ud83d\udccb BOM</a><a href="/sa?project=' + encodeURIComponent(JOB_CODE) + '" style="color:#C89A2E;text-decoration:none;">\ud83d\udcc8 SA Estimator</a>';
            var target = document.querySelector('.shop-drawings-main') || document.querySelector('.main-content') || document.querySelector('main') || document.body;
            target.prepend(ctxBar);
        })();

        // ── Init ──
        loadState();

        // ── Tab Switching ──
        window.showTab = function(name) {
            document.querySelectorAll('.tf-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            const el = document.getElementById('tab-' + name);
            if (el) el.classList.add('active');
        };

        // ══════════════════════════════════════════════════════
        //  BUILDING SELECTOR
        // ══════════════════════════════════════════════════════

        function renderBuildingSelector() {
            var container = document.getElementById('buildingSelector');
            var tabsEl = document.getElementById('buildingTabs');
            if (!buildings || buildings.length <= 1) {
                container.style.display = 'none';
                return;
            }
            container.style.display = 'block';
            tabsEl.innerHTML = '';
            buildings.forEach(function(b) {
                var btn = document.createElement('button');
                btn.className = 'tf-btn tf-btn-sm ' + (b.building_id === selectedBuilding ? 'tf-btn-primary' : 'tf-btn-outline');
                btn.style.cssText = 'min-width:160px;text-align:center;';
                var w = Math.round(b.width_ft || 0);
                var l = Math.round(b.length_ft || 0);
                btn.innerHTML = '<strong>' + b.building_id.replace('B', 'Building ') + '</strong> (' + w + "'" + ' x ' + l + "'" + ')';
                btn.onclick = function() {
                    selectedBuilding = b.building_id;
                    renderBuildingSelector();
                    updateDrawingLinks();
                    updateBuilderForBuilding();
                    renderDrawings();
                };
                tabsEl.appendChild(btn);
            });
            updateDrawingLinks();
            updateBuilderForBuilding();
        }

        function updateDrawingLinks() {
            var suffix = buildings.length > 1 ? '?building=' + selectedBuilding : '';
            document.querySelectorAll('a[data-drawing-type]').forEach(function(a) {
                var dtype = a.dataset.drawingType;
                a.href = '/shop-drawings/' + JOB_CODE + '/' + dtype + suffix;
            });
        }

        function updateBuilderForBuilding() {
            var lbl = document.getElementById('builderBuildingLabel');
            var title = document.getElementById('builderTitle');
            if (!buildings || buildings.length <= 1) {
                if (lbl) lbl.style.display = 'none';
                return;
            }
            // Find the selected building
            var bldg = null;
            for (var i = 0; i < buildings.length; i++) {
                if (buildings[i].building_id === selectedBuilding) {
                    bldg = buildings[i]; break;
                }
            }
            if (!bldg) return;
            var w = Math.round(bldg.width_ft || 0);
            var l = Math.round(bldg.length_ft || 0);
            var bLabel = selectedBuilding.replace('B', 'Building ');
            var dims = (w && l) ? " (" + w + "' x " + l + "')" : '';
            if (lbl) {
                lbl.textContent = bLabel + dims;
                lbl.style.display = 'inline-block';
            }
            if (title) {
                title.textContent = 'Interactive Shop Drawing Builder — ' + bLabel;
            }
        }

        // ══════════════════════════════════════════════════════
        //  LOAD / SAVE STATE
        // ══════════════════════════════════════════════════════

        function loadState() {
            // Load config from server
            fetch('/api/shop-drawings/config?job_code=' + JOB_CODE)
                .then(r => r.json())
                .then(data => {
                    if (data.ok) {
                        config = data.config || {};
                        bomConfig = data.bom_config || {};
                        buildings = data.buildings || [];
                        drawings = data.drawings || [];
                        revisions = data.revisions || [];
                        generationLog = data.generation_log || null;
                        renderBuildingSelector();
                        renderAll();
                    } else {
                        console.warn('Config load:', data.error);
                        showAlert('Could not load configuration: ' + (data.error || 'unknown error'));
                    }
                })
                .catch(err => {
                    console.error('Config load error:', err);
                    showAlert('Could not connect to server');
                });
        }

        window.saveConfig = function() {
            const cfg = readFormConfig();
            fetch('/api/shop-drawings/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ job_code: JOB_CODE, config: cfg })
            })
            .then(r => r.json())
            .then(data => {
                if (data.ok) {
                    config = cfg;
                    showToast('Configuration saved');
                    renderSyncBanner();
                } else {
                    showAlert('Save failed: ' + (data.error || ''));
                }
            })
            .catch(err => showAlert('Save error: ' + err.message));
        };

        window.resetToBOM = function() {
            if (!confirm('Reset all fields to BOM-derived values? Any manual overrides will be lost.')) return;
            config = JSON.parse(JSON.stringify(bomConfig));
            populateForm(config);
            renderSyncBanner();
            showToast('Reset to BOM values');
        };

        window.resyncFromBOM = function() {
            // First check for diffs — show conflict resolution if there are changes
            fetch('/api/shop-drawings/diff', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ job_code: JOB_CODE })
            })
            .then(r => r.json())
            .then(data => {
                if (!data.ok) {
                    showAlert('Diff check failed: ' + (data.error || ''));
                    return;
                }
                if (!data.has_changes) {
                    showToast('Already in sync — no changes detected');
                    return;
                }
                // Show conflict resolution modal
                showConflictModal(data.diffs);
            })
            .catch(err => showAlert('Sync error: ' + err.message));
        };

        // ══════════════════════════════════════════════════════
        //  CONFLICT RESOLUTION
        // ══════════════════════════════════════════════════════

        let pendingDiffs = [];

        function showConflictModal(diffs) {
            pendingDiffs = diffs;
            const overlay = document.getElementById('conflictOverlay');
            const summary = document.getElementById('conflictSummary');
            const body = document.getElementById('conflictBody');

            summary.textContent = diffs.length + ' field' + (diffs.length > 1 ? 's have' : ' has') +
                ' changed in the BOM since your last sync. Review each change and choose which values to keep.';

            body.innerHTML = '';
            diffs.forEach((d, i) => {
                const tr = document.createElement('tr');
                const curDisplay = formatFieldValue(d.field, d.current_value);
                const bomDisplay = formatFieldValue(d.field, d.bom_value);
                tr.innerHTML =
                    '<td><input type="checkbox" id="conflict-' + i + '" checked></td>' +
                    '<td style="font-weight:500">' + escHtml(d.label) + '</td>' +
                    '<td class="val-current">' + escHtml(curDisplay) + '</td>' +
                    '<td class="val-arrow">&#8594;</td>' +
                    '<td class="val-bom">' + escHtml(bomDisplay) + '</td>';
                body.appendChild(tr);
            });

            overlay.classList.add('show');
        }

        function formatFieldValue(field, val) {
            if (val === true) return 'Yes';
            if (val === false) return 'No';
            if (val === null || val === undefined) return '-';
            if (typeof val === 'number') {
                if (field.includes('_ft') || field.includes('_deg')) return val.toFixed(2);
                return String(val);
            }
            return String(val);
        }

        window.closeConflictModal = function() {
            document.getElementById('conflictOverlay').classList.remove('show');
            pendingDiffs = [];
        };

        window.toggleAllConflicts = function() {
            const boxes = document.querySelectorAll('#conflictBody input[type="checkbox"]');
            const allChecked = Array.from(boxes).every(b => b.checked);
            boxes.forEach(b => b.checked = !allChecked);
        };

        window.applySelectedConflicts = function() {
            const accepted = [];
            pendingDiffs.forEach((d, i) => {
                const cb = document.getElementById('conflict-' + i);
                if (cb && cb.checked) {
                    accepted.push(d.field);
                }
            });

            if (accepted.length === 0) {
                closeConflictModal();
                showToast('No changes accepted');
                return;
            }

            // Partial sync — accept only selected fields
            fetch('/api/shop-drawings/sync-bom', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    job_code: JOB_CODE,
                    mode: 'partial',
                    accept_fields: accepted
                })
            })
            .then(r => r.json())
            .then(data => {
                if (data.ok) {
                    bomConfig = data.bom_config || {};
                    config = data.config || config;
                    populateForm(config);
                    renderSyncBanner();
                    closeConflictModal();
                    showToast('Accepted ' + accepted.length + ' BOM change' +
                              (accepted.length > 1 ? 's' : ''));
                } else {
                    showAlert('Sync failed: ' + (data.error || ''));
                }
            })
            .catch(err => showAlert('Sync error: ' + err.message));
        };

        window.acceptAllConflicts = function() {
            fetch('/api/shop-drawings/sync-bom', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ job_code: JOB_CODE, mode: 'full' })
            })
            .then(r => r.json())
            .then(data => {
                if (data.ok) {
                    bomConfig = data.bom_config || {};
                    config = data.config || config;
                    populateForm(config);
                    renderSyncBanner();
                    closeConflictModal();
                    showToast('All BOM values accepted');
                }
            });
        };

        // ══════════════════════════════════════════════════════
        //  RENDERING
        // ══════════════════════════════════════════════════════

        function renderAll() {
            renderSubtitle();
            populateForm(config);
            renderStats();
            renderSyncBanner();
            renderDrawings();
            renderRevisions();
        }

        function renderSubtitle() {
            const el = document.getElementById('projectSubtitle');
            const name = config.project_name || '';
            const customer = config.customer_name || '';
            el.textContent = [name, customer].filter(Boolean).join(' — ') || JOB_CODE;
        }

        function renderStats() {
            document.getElementById('statFiles').textContent = drawings.length || '0';
            if (generationLog) {
                document.getElementById('statRevision').textContent =
                    generationLog.revision || '-';
                const kb = generationLog.total_bytes
                    ? (generationLog.total_bytes / 1024).toFixed(1) + ' KB'
                    : '-';
                document.getElementById('statSize').textContent = kb;
                if (generationLog.generated_at) {
                    const d = new Date(generationLog.generated_at);
                    document.getElementById('statGenerated').textContent =
                        d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});
                }
            }
            document.getElementById('btnDownloadAll').disabled = drawings.length === 0;
        }

        function renderSyncBanner() {
            const banner = document.getElementById('syncBanner');
            if (!bomConfig || Object.keys(bomConfig).length === 0) {
                banner.classList.remove('show');
                return;
            }
            // Check for divergence
            const bomFields = ['building_width_ft', 'building_length_ft', 'clear_height_ft',
                               'roof_pitch_deg', 'n_frames', 'purlin_spacing_ft', 'frame_type'];
            let diverged = false;
            for (const f of bomFields) {
                if (bomConfig[f] !== undefined && config[f] !== undefined) {
                    if (String(bomConfig[f]) !== String(config[f])) {
                        diverged = true;
                        break;
                    }
                }
            }

            banner.classList.add('show');
            if (diverged) {
                banner.classList.remove('synced');
                banner.classList.add('diverged');
                document.getElementById('syncIcon').innerHTML = '&#9888;';
                document.getElementById('syncText').textContent =
                    'Configuration has been manually overridden and differs from BOM values.';
                document.getElementById('syncAction').style.display = '';
            } else {
                banner.classList.remove('diverged');
                banner.classList.add('synced');
                document.getElementById('syncIcon').innerHTML = '&#10003;';
                document.getElementById('syncText').textContent =
                    'Configuration matches BOM — all values in sync.';
                document.getElementById('syncAction').style.display = 'none';
            }

            // Highlight mismatched fields
            document.querySelectorAll('.bom-value').forEach(el => {
                const field = el.dataset.bomField;
                if (bomConfig[field] !== undefined) {
                    const bomVal = bomConfig[field];
                    const curVal = config[field];
                    el.textContent = 'BOM: ' + bomVal;
                    if (String(bomVal) !== String(curVal)) {
                        el.classList.add('bom-mismatch');
                    } else {
                        el.classList.remove('bom-mismatch');
                    }
                }
            });
        }

        // ── Drawing Gallery ──

        function renderDrawings() {
            const grid = document.getElementById('drawingsGrid');
            const empty = document.getElementById('drawingsEmpty');

            // Filter drawings by selected building (if multi-building project)
            var filtered = drawings;
            if (buildings.length > 1) {
                filtered = drawings.filter(function(d) {
                    return (d.building_id || 'B1') === selectedBuilding;
                });
            }

            if (filtered.length === 0) {
                empty.style.display = '';
                grid.style.display = 'none';
                return;
            }

            empty.style.display = 'none';
            grid.style.display = '';
            grid.innerHTML = '';

            filtered.forEach((d) => {
                // Use the original index in the drawings array for view/download/delete
                const idx = drawings.indexOf(d);
                const typeInfo = DRAWING_TYPES[d.type] || { label: d.type, icon: '&#128196;' };
                const sizeStr = d.size_bytes
                    ? (d.size_bytes < 1024 ? d.size_bytes + ' B' : (d.size_bytes / 1024).toFixed(1) + ' KB')
                    : '';
                // Building label for multi-building projects
                const bldgLabel = (buildings.length > 1 && d.building_id)
                    ? ' <span style="font-size:0.75rem;color:var(--tf-blue-600);font-weight:600;">(' + d.building_id.replace('B', 'Bldg ') + ')</span>'
                    : '';

                const card = document.createElement('div');
                card.className = 'drawing-card';
                card.innerHTML = `
                    <div class="dc-preview">
                        <div class="dc-icon">${typeInfo.icon}</div>
                        <div class="dc-type-badge ${d.type}">${typeInfo.label}</div>
                    </div>
                    <div class="dc-body">
                        <div class="dc-title">${escHtml(d.filename || d.description || typeInfo.label)}${bldgLabel}</div>
                        <div class="dc-meta">
                            <span>${sizeStr}</span>
                            <span>${d.description || ''}</span>
                        </div>
                    </div>
                    <div class="dc-actions">
                        <button class="tf-btn tf-btn-sm tf-btn-primary" onclick="viewDrawing(${idx})">
                            View PDF
                        </button>
                        <button class="tf-btn tf-btn-sm tf-btn-outline" onclick="downloadDrawing(${idx})">
                            Download
                        </button>
                        <button class="tf-btn tf-btn-sm dc-delete-btn" style="background:#DC2626;color:#FFF;" onclick="deleteDrawing(${idx})" title="Delete this drawing">
                            &#128465; Delete
                        </button>
                    </div>
                `;
                grid.appendChild(card);
            });
        }

        window.viewDrawing = function(idx) {
            const d = drawings[idx];
            if (d && d.filename) {
                window.open('/api/shop-drawings/file?job_code=' + JOB_CODE +
                            '&filename=' + encodeURIComponent(d.filename), '_blank');
            }
        };

        window.downloadDrawing = function(idx) {
            const d = drawings[idx];
            if (d && d.filename) {
                const a = document.createElement('a');
                a.href = '/api/shop-drawings/file?job_code=' + JOB_CODE +
                         '&filename=' + encodeURIComponent(d.filename) + '&download=1';
                a.download = d.filename;
                a.click();
            }
        };

        window.deleteDrawing = async function(idx) {
            const d = drawings[idx];
            if (!d || !d.filename) return;
            if (!confirm('Delete "' + d.filename + '"? This cannot be undone.')) return;
            try {
                const resp = await fetch('/api/shop-drawings/delete-pdf', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: 'job_code=' + encodeURIComponent(JOB_CODE) +
                          '&filename=' + encodeURIComponent(d.filename)
                });
                const data = await resp.json();
                if (data.ok) {
                    drawings.splice(idx, 1);
                    renderDrawings();
                    if (typeof showToast === 'function') showToast('Drawing deleted', 'success');
                } else {
                    alert('Delete failed: ' + (data.error || 'unknown error'));
                }
            } catch(err) {
                alert('Delete error: ' + err.message);
            }
        };

        window.downloadAllZip = function() {
            window.location.href = '/api/shop-drawings/zip?job_code=' + JOB_CODE;
        };

        // ── Revision History ──

        function renderRevisions() {
            const timeline = document.getElementById('revisionTimeline');
            if (!revisions || revisions.length === 0) {
                timeline.innerHTML = '<div class="empty-state" style="padding:var(--tf-sp-6)">' +
                    '<p style="color:var(--tf-gray-500);font-size:var(--tf-text-sm)">' +
                    'No revisions yet. Generate shop drawings to create the first revision.</p></div>';
                return;
            }

            timeline.innerHTML = '';
            revisions.forEach((rev, i) => {
                const item = document.createElement('div');
                item.className = 'revision-item' + (i === 0 ? ' current' : '');
                const d = rev.generated_at ? new Date(rev.generated_at) : null;
                const dateStr = d ? d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'}) : '';
                item.innerHTML = `
                    <div class="revision-label">Rev ${rev.revision || '-'}</div>
                    <div class="revision-date">${dateStr}</div>
                    <div class="revision-files">${rev.total_files || 0} files &middot; ${((rev.total_bytes||0)/1024).toFixed(1)} KB</div>
                `;
                timeline.appendChild(item);
            });
        }

        // ══════════════════════════════════════════════════════
        //  FORM POPULATION & READING
        // ══════════════════════════════════════════════════════

        function populateForm(cfg) {
            document.querySelectorAll('[data-field]').forEach(el => {
                const field = el.dataset.field;
                let val = cfg[field];
                if (val === undefined) val = '';

                if (el.tagName === 'SELECT') {
                    // For boolean selects
                    if (val === true) val = 'true';
                    else if (val === false) val = 'false';
                    el.value = String(val);
                } else {
                    el.value = val;
                }

                // Track changes
                el.dataset.original = String(val);
                el.classList.remove('changed');
            });

            // Attach change listeners
            document.querySelectorAll('[data-field]').forEach(el => {
                el.removeEventListener('input', onFieldChange);
                el.removeEventListener('change', onFieldChange);
                el.addEventListener('input', onFieldChange);
                el.addEventListener('change', onFieldChange);
            });
        }

        function onFieldChange(e) {
            const el = e.target;
            if (String(el.value) !== el.dataset.original) {
                el.classList.add('changed');
            } else {
                el.classList.remove('changed');
            }
        }

        function readFormConfig() {
            const cfg = JSON.parse(JSON.stringify(config));
            document.querySelectorAll('[data-field]').forEach(el => {
                const field = el.dataset.field;
                let val = el.value;

                // Type coercion
                if (val === 'true') val = true;
                else if (val === 'false') val = false;
                else if (el.type === 'number' && val !== '') val = parseFloat(val);

                cfg[field] = val;
            });
            return cfg;
        }

        // ══════════════════════════════════════════════════════
        //  GENERATION
        // ══════════════════════════════════════════════════════

        window.generateAll = function() {
            const cfg = readFormConfig();
            showGenOverlay();

            fetch('/api/shop-drawings/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ job_code: JOB_CODE, config: cfg })
            })
            .then(r => r.json())
            .then(data => {
                hideGenOverlay();
                if (data.ok) {
                    config = cfg;
                    drawings = data.files || [];
                    generationLog = data.summary || null;
                    if (data.revision_entry) {
                        revisions.unshift(data.revision_entry);
                    }
                    renderAll();

                    if (data.errors && data.errors.length > 0) {
                        showAlert('Generated with ' + data.errors.length + ' warning(s):\n' +
                                  data.errors.join('\n'));
                    } else {
                        showToast('All drawings generated successfully (' +
                                  drawings.length + ' files)');
                    }
                } else {
                    showAlert('Generation failed: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(err => {
                hideGenOverlay();
                showAlert('Generation error: ' + err.message);
            });
        };

        function showGenOverlay() {
            const overlay = document.getElementById('genOverlay');
            const stepList = document.getElementById('genStepList');
            const fill = document.getElementById('genProgressFill');
            const label = document.getElementById('genStepLabel');

            overlay.classList.add('show');
            fill.style.width = '0%';
            label.textContent = 'Initializing...';

            stepList.innerHTML = '';
            GEN_STEPS.forEach(s => {
                const div = document.createElement('div');
                div.className = 'gen-step-item';
                div.id = 'gen-step-' + s.key;
                div.innerHTML = '<span>&#9675;</span> ' + s.label;
                stepList.appendChild(div);
            });

            // Simulate progress animation
            let progress = 0;
            const interval = setInterval(() => {
                progress += 3;
                if (progress > 95) progress = 95;
                fill.style.width = progress + '%';

                const stepIdx = Math.floor(progress / (100 / GEN_STEPS.length));
                for (let i = 0; i < GEN_STEPS.length; i++) {
                    const el = document.getElementById('gen-step-' + GEN_STEPS[i].key);
                    if (i < stepIdx) {
                        el.className = 'gen-step-item done';
                        el.innerHTML = '<span>&#10003;</span> ' + GEN_STEPS[i].label;
                    } else if (i === stepIdx) {
                        el.className = 'gen-step-item active';
                        el.innerHTML = '<span>&#9654;</span> ' + GEN_STEPS[i].label + '...';
                        label.textContent = 'Generating ' + GEN_STEPS[i].label + '...';
                    }
                }
            }, 300);

            overlay._interval = interval;
        }

        function hideGenOverlay() {
            const overlay = document.getElementById('genOverlay');
            if (overlay._interval) clearInterval(overlay._interval);
            document.getElementById('genProgressFill').style.width = '100%';
            document.getElementById('genStepLabel').textContent = 'Complete!';

            // Mark all done
            GEN_STEPS.forEach(s => {
                const el = document.getElementById('gen-step-' + s.key);
                if (el) {
                    el.className = 'gen-step-item done';
                    el.innerHTML = '<span>&#10003;</span> ' + s.label;
                }
            });

            setTimeout(() => overlay.classList.remove('show'), 800);
        }

        // ══════════════════════════════════════════════════════
        //  UTILITIES
        // ══════════════════════════════════════════════════════

        function escHtml(s) {
            const div = document.createElement('div');
            div.textContent = s;
            return div.innerHTML;
        }

        function showToast(msg) {
            const toast = document.createElement('div');
            toast.style.cssText = 'position:fixed;bottom:24px;right:24px;background:var(--tf-navy);' +
                'color:#fff;padding:12px 20px;border-radius:var(--tf-radius);font-size:var(--tf-text-sm);' +
                'z-index:2000;box-shadow:var(--tf-shadow-lg);animation:fadeIn .2s ease';
            toast.textContent = msg;
            document.body.appendChild(toast);
            setTimeout(() => { toast.style.opacity = '0'; toast.style.transition = 'opacity .3s'; }, 2500);
            setTimeout(() => toast.remove(), 3000);
        }

        function showAlert(msg) {
            alert(msg);
        }

    })();
    </script>
</body>
</html>
"""
