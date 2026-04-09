"""
TitanForge v3.0 — Project Page Template
=========================================
Full project page at /project/{JOB_CODE} with:
- Project header with stage badge & completion bar
- Customer & location info cards
- Card grid document system with categories
- Archive system (old versions hidden, expandable)
- Stage-aware Next Steps checklist
- Project Intelligence Panel
- Quick actions (Open in SA Calc, Open in TC Quote, Duplicate, Archive)
"""

from templates.shared_styles import DESIGN_SYSTEM_CSS

PROJECT_PAGE_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TitanForge — Project {{JOB_CODE}}</title>
    <style>
""" + DESIGN_SYSTEM_CSS + r"""

        /* ── Project Page Layout ───────────────────────────── */
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: var(--tf-sp-6) var(--tf-sp-8);
        }

        /* Project Header */
        .project-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: var(--tf-sp-6);
            gap: var(--tf-sp-4);
            flex-wrap: wrap;
        }

        .project-title-area h1 {
            font-size: var(--tf-text-2xl);
            font-weight: 700;
            color: var(--tf-gray-900);
            letter-spacing: -0.02em;
        }

        .project-title-area .job-code {
            font-size: var(--tf-text-sm);
            font-weight: 600;
            color: var(--tf-blue);
            text-transform: uppercase;
            letter-spacing: 0.02em;
            margin-bottom: var(--tf-sp-1);
        }

        .project-meta {
            display: flex;
            gap: var(--tf-sp-3);
            margin-top: var(--tf-sp-2);
            align-items: center;
            flex-wrap: wrap;
        }

        .stage-select {
            padding: 4px 12px;
            border-radius: 999px;
            font-size: var(--tf-text-xs);
            font-weight: 600;
            border: 2px solid var(--tf-blue);
            background: var(--tf-blue-light);
            color: var(--tf-blue);
            cursor: pointer;
            outline: none;
        }

        .created-info {
            font-size: var(--tf-text-xs);
            color: var(--tf-gray-500);
        }

        .header-actions {
            display: flex;
            gap: var(--tf-sp-2);
            flex-wrap: wrap;
        }

        /* Completion Bar */
        .completion-section {
            background: var(--tf-surface);
            border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-lg);
            padding: var(--tf-sp-4) var(--tf-sp-5);
            margin-bottom: var(--tf-sp-6);
            display: flex;
            align-items: center;
            gap: var(--tf-sp-4);
        }

        .completion-label {
            font-size: var(--tf-text-sm);
            font-weight: 600;
            color: var(--tf-gray-700);
            white-space: nowrap;
        }

        .completion-bar-track {
            flex: 1;
            height: 10px;
            background: var(--tf-gray-200);
            border-radius: 999px;
            overflow: hidden;
        }

        .completion-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--tf-blue) 0%, var(--tf-success) 100%);
            border-radius: 999px;
            transition: width 500ms var(--tf-ease);
        }

        .completion-pct {
            font-size: var(--tf-text-lg);
            font-weight: 700;
            color: var(--tf-gray-900);
            white-space: nowrap;
            min-width: 48px;
            text-align: right;
        }

        /* Two Column Layout */
        .main-grid {
            display: grid;
            grid-template-columns: 1fr 380px;
            gap: var(--tf-sp-6);
        }

        /* Info Cards Row */
        .info-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: var(--tf-sp-4);
            margin-bottom: var(--tf-sp-6);
        }

        .info-card {
            background: var(--tf-surface);
            border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-lg);
            padding: var(--tf-sp-5);
        }

        .info-card h3 {
            font-size: var(--tf-text-xs);
            font-weight: 700;
            color: var(--tf-gray-500);
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: var(--tf-sp-3);
        }

        .info-row {
            display: flex;
            justify-content: space-between;
            padding: var(--tf-sp-2) 0;
            border-bottom: 1px solid var(--tf-gray-100);
            font-size: var(--tf-text-sm);
        }

        .info-row:last-child { border-bottom: none; }

        .info-row .label {
            color: var(--tf-gray-500);
            font-weight: 500;
        }

        .info-row .value {
            color: var(--tf-gray-900);
            font-weight: 600;
            text-align: right;
        }

        .info-row .value a {
            color: var(--tf-blue);
            text-decoration: none;
        }
        .info-row .value a:hover { text-decoration: underline; }

        /* Document Card Grid */
        .docs-section {
            margin-bottom: var(--tf-sp-6);
        }

        .docs-section h2 {
            font-size: var(--tf-text-lg);
            font-weight: 700;
            color: var(--tf-gray-900);
            margin-bottom: var(--tf-sp-4);
        }

        .doc-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
            gap: var(--tf-sp-4);
        }

        .doc-category-card {
            background: var(--tf-surface);
            border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-lg);
            padding: var(--tf-sp-5) var(--tf-sp-4);
            text-align: center;
            cursor: pointer;
            transition: all var(--tf-duration) var(--tf-ease);
            position: relative;
        }

        .doc-category-card:hover {
            box-shadow: var(--tf-shadow-md);
            border-color: var(--tf-blue);
            transform: translateY(-2px);
        }

        .doc-category-card.active {
            border-color: var(--tf-blue);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
        }

        .doc-cat-icon {
            font-size: 2rem;
            margin-bottom: var(--tf-sp-2);
        }

        .doc-cat-label {
            font-size: var(--tf-text-sm);
            font-weight: 600;
            color: var(--tf-gray-800);
        }

        .doc-cat-count {
            font-size: var(--tf-text-xs);
            color: var(--tf-gray-500);
            margin-top: var(--tf-sp-1);
        }

        .doc-cat-badge {
            position: absolute;
            top: -6px;
            right: -6px;
            background: var(--tf-blue);
            color: #fff;
            border-radius: 50%;
            width: 22px;
            height: 22px;
            font-size: 11px;
            font-weight: 700;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .doc-cat-badge.empty { display: none; }

        /* Files Panel (expanded) */
        .files-panel {
            display: none;
            background: var(--tf-surface);
            border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-lg);
            padding: var(--tf-sp-5);
            margin-top: var(--tf-sp-4);
            animation: fadeIn 200ms var(--tf-ease);
        }

        .files-panel.show { display: block; }

        @keyframes fadeIn { from { opacity: 0; transform: translateY(-8px); } to { opacity: 1; transform: translateY(0); } }

        .files-panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--tf-sp-4);
        }

        .files-panel-header h3 {
            font-size: var(--tf-text-md);
            font-weight: 700;
            color: var(--tf-gray-900);
        }

        .upload-drop {
            border: 2px dashed var(--tf-gray-300);
            border-radius: var(--tf-radius);
            padding: var(--tf-sp-4);
            text-align: center;
            cursor: pointer;
            transition: all var(--tf-duration) var(--tf-ease);
            background: var(--tf-gray-50);
            margin-bottom: var(--tf-sp-4);
            font-size: var(--tf-text-sm);
            color: var(--tf-gray-500);
        }

        .upload-drop:hover { border-color: var(--tf-blue-mid); background: var(--tf-blue-light); }
        .upload-drop.dragover { border-color: var(--tf-amber); background: var(--tf-amber-light); }

        .file-list-table {
            width: 100%;
            border-collapse: collapse;
            font-size: var(--tf-text-sm);
        }

        .file-list-table th {
            text-align: left;
            font-size: var(--tf-text-xs);
            font-weight: 700;
            color: var(--tf-gray-500);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            padding: var(--tf-sp-2) var(--tf-sp-3);
            border-bottom: 2px solid var(--tf-border);
        }

        .file-list-table td {
            padding: var(--tf-sp-2) var(--tf-sp-3);
            border-bottom: 1px solid var(--tf-gray-100);
        }

        .file-list-table tr:hover td { background: var(--tf-blue-light); }

        .file-link {
            color: var(--tf-blue);
            text-decoration: none;
            font-weight: 600;
        }
        .file-link:hover { text-decoration: underline; }

        .archive-toggle {
            background: none;
            border: none;
            color: var(--tf-gray-400);
            cursor: pointer;
            font-size: var(--tf-text-xs);
            font-weight: 600;
            padding: var(--tf-sp-2) 0;
            margin-top: var(--tf-sp-2);
            transition: color var(--tf-duration) var(--tf-ease);
        }
        .archive-toggle:hover { color: var(--tf-gray-700); }

        .archived-files { display: none; }
        .archived-files.show { display: table-row-group; }
        .archived-files td { background: var(--tf-gray-50); color: var(--tf-gray-500); font-style: italic; }

        /* Right Sidebar */
        .sidebar { display: flex; flex-direction: column; gap: var(--tf-sp-5); }

        /* Next Steps Checklist */
        .next-steps-card {
            background: var(--tf-surface);
            border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-lg);
            overflow: hidden;
        }

        .next-steps-header {
            background: var(--tf-navy);
            color: #fff;
            padding: var(--tf-sp-3) var(--tf-sp-4);
            font-size: var(--tf-text-sm);
            font-weight: 700;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .next-steps-header .stage-label {
            background: rgba(245, 158, 11, 0.2);
            color: var(--tf-amber);
            padding: 2px 10px;
            border-radius: 999px;
            font-size: var(--tf-text-xs);
            font-weight: 600;
        }

        .next-steps-body { padding: var(--tf-sp-4); }

        .step-item {
            display: flex;
            align-items: flex-start;
            gap: var(--tf-sp-3);
            padding: var(--tf-sp-3) 0;
            border-bottom: 1px solid var(--tf-gray-100);
        }

        .step-item:last-child { border-bottom: none; }

        .step-checkbox {
            width: 20px;
            height: 20px;
            border-radius: var(--tf-radius-sm);
            border: 2px solid var(--tf-gray-300);
            cursor: pointer;
            flex-shrink: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all var(--tf-duration) var(--tf-ease);
            margin-top: 1px;
            background: #fff;
        }

        .step-checkbox:hover { border-color: var(--tf-blue); }

        .step-checkbox.checked {
            background: var(--tf-success);
            border-color: var(--tf-success);
            color: #fff;
        }

        .step-text {
            font-size: var(--tf-text-sm);
            color: var(--tf-gray-700);
            line-height: 1.4;
        }

        .step-text.completed {
            text-decoration: line-through;
            color: var(--tf-gray-400);
        }

        .step-meta {
            font-size: var(--tf-text-xs);
            color: var(--tf-gray-400);
            margin-top: 2px;
        }

        /* Intelligence Panel */
        .intel-card {
            background: var(--tf-surface);
            border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-lg);
            overflow: hidden;
        }

        .intel-header {
            background: linear-gradient(135deg, var(--tf-navy) 0%, #1E3A5F 100%);
            color: #fff;
            padding: var(--tf-sp-3) var(--tf-sp-4);
            font-size: var(--tf-text-sm);
            font-weight: 700;
        }

        .intel-body { padding: var(--tf-sp-4); }

        .intel-stat {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: var(--tf-sp-3) 0;
            border-bottom: 1px solid var(--tf-gray-100);
        }

        .intel-stat:last-child { border-bottom: none; }

        .intel-stat-label {
            font-size: var(--tf-text-xs);
            font-weight: 600;
            color: var(--tf-gray-500);
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .intel-stat-value {
            font-size: var(--tf-text-md);
            font-weight: 700;
            color: var(--tf-gray-900);
        }

        .intel-stat-value.highlight { color: var(--tf-success); }
        .intel-stat-value.warning { color: var(--tf-warning); }

        .intel-suggestions {
            margin-top: var(--tf-sp-3);
            padding-top: var(--tf-sp-3);
            border-top: 1px solid var(--tf-border);
        }

        .intel-suggestions h4 {
            font-size: var(--tf-text-xs);
            font-weight: 700;
            color: var(--tf-gray-600);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: var(--tf-sp-2);
        }

        .suggestion-item {
            display: flex;
            align-items: flex-start;
            gap: var(--tf-sp-2);
            padding: var(--tf-sp-2) 0;
            font-size: var(--tf-text-sm);
            color: var(--tf-gray-600);
        }

        .suggestion-bullet {
            color: var(--tf-amber);
            font-weight: 700;
            flex-shrink: 0;
        }

        /* Notes Section */
        .notes-card {
            background: var(--tf-surface);
            border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-lg);
            padding: var(--tf-sp-4);
        }

        .notes-card h3 {
            font-size: var(--tf-text-xs);
            font-weight: 700;
            color: var(--tf-gray-500);
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: var(--tf-sp-3);
        }

        .notes-textarea {
            width: 100%;
            min-height: 100px;
            padding: var(--tf-sp-3);
            font-family: var(--tf-font);
            font-size: var(--tf-text-sm);
            color: var(--tf-gray-700);
            background: var(--tf-gray-50);
            border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius);
            resize: vertical;
            outline: none;
            transition: border-color var(--tf-duration) var(--tf-ease);
        }

        .notes-textarea:focus {
            border-color: var(--tf-blue-mid);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
        }

        /* ── Responsive ────────────────────────────────────── */
        @media (max-width: 1200px) {
            .main-grid { grid-template-columns: 1fr; }
            .sidebar { order: -1; }
        }

        @media (max-width: 768px) {
            .container { padding: var(--tf-sp-4); }
            .project-header { flex-direction: column; }
            .header-actions { width: 100%; }
            .info-cards { grid-template-columns: 1fr; }
            .doc-grid { grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); }
        }
    </style>
</head>
<body>
    <script>
        const JOB_CODE = '{{JOB_CODE}}';
        const USER_ROLE = '{{USER_ROLE}}';
        const USER_NAME = '{{USER_NAME}}';
        const METADATA = {{METADATA_JSON}};
        const STAGES = {{STAGES_JSON}};
        const NEXT_STEPS = {{NEXT_STEPS_JSON}};
        const DOC_CATEGORIES = {{DOC_CATEGORIES_JSON}};
    </script>

    <!-- TOP NAVIGATION BAR -->
    <div class="tf-topbar">
        <a href="/" class="tf-logo">
            <div class="tf-logo-icon">&#9878;</div>
            TITANFORGE
        </a>
        <nav>
            <a href="/">Dashboard</a>
            <a href="/sa">SA Calculator</a>
            <a href="/tc">TC Quote</a>
        </nav>
        <div class="tf-user">
            <span id="userName">User</span>
            <a href="/auth/logout" onclick="return confirm('Are you sure you want to logout?')">Logout</a>
        </div>
    </div>

    <!-- MAIN CONTENT -->
    <div class="container">
        <!-- PROJECT HEADER -->
        <div class="project-header">
            <div class="project-title-area">
                <div class="job-code" id="jobCodeLabel"></div>
                <h1 id="projectTitle">Project</h1>
                <div class="project-meta">
                    <select class="stage-select" id="stageSelect" onchange="updateStage(this.value)"></select>
                    <span class="created-info" id="createdInfo"></span>
                </div>
            </div>
            <div class="header-actions">
                <button class="tf-btn tf-btn-primary tf-btn-sm" onclick="openInSACalc()">Open in SA Calc</button>
                <button class="tf-btn tf-btn-amber tf-btn-sm" onclick="openInTCQuote()">Open in TC Quote</button>
                <button class="tf-btn tf-btn-outline tf-btn-sm" onclick="duplicateProject()">Duplicate</button>
                <button class="tf-btn tf-btn-ghost tf-btn-sm" onclick="archiveProject()" id="archiveBtn">Archive</button>
            </div>
        </div>

        <!-- COMPLETION BAR -->
        <div class="completion-section">
            <span class="completion-label">Stage Progress</span>
            <div class="completion-bar-track">
                <div class="completion-bar-fill" id="completionFill" style="width: 0%"></div>
            </div>
            <span class="completion-pct" id="completionPct">0%</span>
        </div>

        <!-- INFO CARDS ROW -->
        <div class="info-cards">
            <div class="info-card" id="customerCard">
                <h3>Customer</h3>
                <div id="customerInfo"></div>
            </div>
            <div class="info-card" id="locationCard">
                <h3>Location</h3>
                <div id="locationInfo"></div>
            </div>
            <div class="info-card" id="projectStatsCard">
                <h3>Project Stats</h3>
                <div id="projectStats"></div>
            </div>
        </div>

        <!-- TWO COLUMN LAYOUT -->
        <div class="main-grid">
            <!-- LEFT: Documents + Notes -->
            <div class="main-content">
                <!-- DOCUMENTS SECTION -->
                <div class="docs-section">
                    <h2>Documents</h2>
                    <div class="doc-grid" id="docGrid"></div>
                    <div class="files-panel" id="filesPanel"></div>
                </div>

                <!-- NOTES -->
                <div class="notes-card">
                    <h3>Project Notes</h3>
                    <textarea class="notes-textarea" id="notesArea" placeholder="Add project notes..." onblur="saveNotes()"></textarea>
                </div>
            </div>

            <!-- RIGHT: Sidebar -->
            <div class="sidebar">
                <!-- NEXT STEPS CHECKLIST -->
                <div class="next-steps-card">
                    <div class="next-steps-header">
                        <span>Next Steps</span>
                        <span class="stage-label" id="stepsStageLabel">QUOTE</span>
                    </div>
                    <div class="next-steps-body" id="nextStepsBody"></div>
                </div>

                <!-- INTELLIGENCE PANEL -->
                <div class="intel-card">
                    <div class="intel-header">Project Intelligence</div>
                    <div class="intel-body" id="intelBody">
                        <div style="text-align: center; padding: var(--tf-sp-4); color: var(--tf-gray-400); font-size: var(--tf-text-sm);">
                            Run a calculation in SA Calc or TC Quote to populate intelligence data.
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <input type="file" id="fileInput" style="display: none;" multiple accept=".pdf,.docx,.xlsx,.jpg,.png,.gif,.dwg,.dxf">

    <script>
        // ── Globals ───────────────────────────────────────
        let activeCategory = null;
        let archivedVisible = {};

        const ICON_MAP = {
            doc_quote: '&#128196;',
            doc_contract: '&#128221;',
            doc_engineering: '&#128208;',
            doc_calcs: '&#129518;',
            doc_shop: '&#128209;',
            doc_certs: '&#128203;',
            doc_photos: '&#128247;',
            doc_other: '&#128193;',
        };

        const FILE_ICONS = {
            pdf: '&#128196;', docx: '&#128216;', xlsx: '&#128202;',
            jpg: '&#128444;', png: '&#128444;', gif: '&#128444;',
            dwg: '&#128208;', dxf: '&#128208;',
        };

        // ── Init ──────────────────────────────────────────
        document.addEventListener('DOMContentLoaded', function() {
            initProjectPage();
        });

        function initProjectPage() {
            // Set user name
            if (USER_NAME && USER_NAME !== '{{USER_NAME}}') {
                document.getElementById('userName').textContent = USER_NAME;
            }

            // Header
            document.getElementById('jobCodeLabel').textContent = METADATA.job_code || JOB_CODE;
            document.getElementById('projectTitle').textContent = METADATA.project_name || 'Untitled Project';

            // Created info
            var created = METADATA.created_at ? new Date(METADATA.created_at).toLocaleDateString() : '';
            var creator = METADATA.created_by || '';
            document.getElementById('createdInfo').textContent = 'Created ' + created + (creator ? ' by ' + creator : '');

            // Stage select
            populateStageSelect();

            // Info cards
            renderCustomerCard();
            renderLocationCard();
            renderProjectStats();

            // Notes
            document.getElementById('notesArea').value = METADATA.notes || '';

            // Documents
            renderDocGrid();

            // Next steps
            loadNextSteps();

            // Intelligence (try to load calc data)
            loadIntelligence();

            // Restrict actions by role
            if (USER_ROLE === 'viewer' || USER_ROLE === 'tc_limited') {
                document.querySelectorAll('.header-actions .tf-btn').forEach(function(btn) {
                    if (btn.textContent.includes('Duplicate') || btn.textContent.includes('Archive')) {
                        btn.style.display = 'none';
                    }
                });
            }
        }

        function populateStageSelect() {
            var sel = document.getElementById('stageSelect');
            sel.innerHTML = '';
            STAGES.forEach(function(s) {
                var opt = document.createElement('option');
                opt.value = s;
                opt.textContent = s.replace(/_/g, ' ').replace(/\b\w/g, function(c) { return c.toUpperCase(); });
                if (s === METADATA.stage) opt.selected = true;
                sel.appendChild(opt);
            });
        }

        // ── Customer & Location Cards ─────────────────────
        function renderCustomerCard() {
            var c = METADATA.customer || {};
            var html = '';
            if (c.name) html += '<div class="info-row"><span class="label">Name</span><span class="value">' + esc(c.name) + '</span></div>';
            if (c.phone) html += '<div class="info-row"><span class="label">Phone</span><span class="value"><a href="tel:' + esc(c.phone) + '">' + esc(c.phone) + '</a></span></div>';
            if (c.email) html += '<div class="info-row"><span class="label">Email</span><span class="value"><a href="mailto:' + esc(c.email) + '">' + esc(c.email) + '</a></span></div>';
            if (!html) html = '<div style="color: var(--tf-gray-400); font-size: var(--tf-text-sm);">No customer info yet</div>';
            document.getElementById('customerInfo').innerHTML = html;
        }

        function renderLocationCard() {
            var loc = METADATA.location || {};
            var html = '';
            if (loc.street) html += '<div class="info-row"><span class="label">Street</span><span class="value">' + esc(loc.street) + '</span></div>';
            if (loc.city || loc.state || loc.zip) {
                var csz = [loc.city, loc.state].filter(Boolean).join(', ');
                if (loc.zip) csz += ' ' + loc.zip;
                html += '<div class="info-row"><span class="label">City/State</span><span class="value">' + esc(csz) + '</span></div>';
            }
            if (!html) html = '<div style="color: var(--tf-gray-400); font-size: var(--tf-text-sm);">No location info yet</div>';
            document.getElementById('locationInfo').innerHTML = html;
        }

        function renderProjectStats() {
            var html = '';
            html += '<div class="info-row"><span class="label">Stage</span><span class="value">' + formatStage(METADATA.stage) + '</span></div>';
            html += '<div class="info-row"><span class="label">Created</span><span class="value">' + formatDate(METADATA.created_at) + '</span></div>';
            html += '<div class="info-row"><span class="label">Updated</span><span class="value">' + formatDate(METADATA.updated_at) + '</span></div>';
            html += '<div class="info-row"><span class="label">Created By</span><span class="value">' + esc(METADATA.created_by || '-') + '</span></div>';
            document.getElementById('projectStats').innerHTML = html;
        }

        // ── Document Grid ─────────────────────────────────
        function renderDocGrid() {
            var grid = document.getElementById('docGrid');
            grid.innerHTML = '';
            var cats = METADATA.doc_categories || DOC_CATEGORIES;

            cats.forEach(function(cat) {
                var card = document.createElement('div');
                card.className = 'doc-category-card';
                card.setAttribute('data-cat', cat.key);
                card.onclick = function() { toggleCategory(cat.key, cat.label); };

                var icon = document.createElement('div');
                icon.className = 'doc-cat-icon';
                icon.innerHTML = ICON_MAP[cat.icon] || '&#128193;';

                var label = document.createElement('div');
                label.className = 'doc-cat-label';
                label.textContent = cat.label;

                var count = document.createElement('div');
                count.className = 'doc-cat-count';
                count.id = 'count-' + cat.key;
                count.textContent = 'Loading...';

                var badge = document.createElement('div');
                badge.className = 'doc-cat-badge empty';
                badge.id = 'badge-' + cat.key;

                card.appendChild(badge);
                card.appendChild(icon);
                card.appendChild(label);
                card.appendChild(count);
                grid.appendChild(card);
            });

            // Load counts
            loadDocCounts();
        }

        function loadDocCounts() {
            var cats = METADATA.doc_categories || DOC_CATEGORIES;
            cats.forEach(function(cat) {
                fetch('/api/project/docs', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ job_code: JOB_CODE, category: cat.key })
                })
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    var files = data.files || [];
                    var el = document.getElementById('count-' + cat.key);
                    if (el) el.textContent = files.length + ' file' + (files.length !== 1 ? 's' : '');
                    var badge = document.getElementById('badge-' + cat.key);
                    if (badge) {
                        if (files.length > 0) {
                            badge.textContent = files.length;
                            badge.classList.remove('empty');
                        } else {
                            badge.classList.add('empty');
                        }
                    }
                })
                .catch(function() {
                    var el = document.getElementById('count-' + cat.key);
                    if (el) el.textContent = '0 files';
                });
            });
        }

        function toggleCategory(catKey, catLabel) {
            var panel = document.getElementById('filesPanel');
            var allCards = document.querySelectorAll('.doc-category-card');

            if (activeCategory === catKey) {
                // Close
                activeCategory = null;
                panel.classList.remove('show');
                allCards.forEach(function(c) { c.classList.remove('active'); });
                return;
            }

            activeCategory = catKey;
            allCards.forEach(function(c) {
                c.classList.toggle('active', c.getAttribute('data-cat') === catKey);
            });

            loadCategoryFiles(catKey, catLabel);
        }

        function loadCategoryFiles(catKey, catLabel) {
            var panel = document.getElementById('filesPanel');
            panel.classList.add('show');
            panel.innerHTML = '<div style="text-align:center;padding:var(--tf-sp-4);color:var(--tf-gray-400);">Loading...</div>';

            fetch('/api/project/docs', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ job_code: JOB_CODE, category: catKey })
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                renderFilesPanel(catKey, catLabel, data.files || []);
            })
            .catch(function() {
                renderFilesPanel(catKey, catLabel, []);
            });
        }

        function renderFilesPanel(catKey, catLabel, files) {
            var panel = document.getElementById('filesPanel');
            var canEdit = (USER_ROLE === 'admin' || USER_ROLE === 'estimator' || USER_ROLE === 'shop');

            var html = '<div class="files-panel-header">';
            html += '<h3>' + esc(catLabel) + '</h3>';
            if (canEdit) {
                html += '<button class="tf-btn tf-btn-primary tf-btn-sm" onclick="triggerUpload(\'' + catKey + '\')">Upload File</button>';
            }
            html += '</div>';

            // Upload zone
            if (canEdit) {
                html += '<div class="upload-drop" id="uploadDrop-' + catKey + '" onclick="triggerUpload(\'' + catKey + '\')">';
                html += 'Drop files here or click to upload';
                html += '</div>';
            }

            if (files.length === 0) {
                html += '<div style="text-align:center;padding:var(--tf-sp-6);color:var(--tf-gray-400);font-size:var(--tf-text-sm);">No files in this category yet</div>';
            } else {
                html += '<table class="file-list-table"><thead><tr>';
                html += '<th>File</th><th>Size</th><th>Uploaded</th>';
                if (canEdit) html += '<th>Actions</th>';
                html += '</tr></thead><tbody>';

                files.forEach(function(f) {
                    var ext = (f.filename || '').split('.').pop().toLowerCase();
                    var icon = FILE_ICONS[ext] || '&#128193;';
                    var size = formatSize(f.size || 0);
                    var date = f.uploaded_at ? new Date(f.uploaded_at).toLocaleDateString() : '';

                    html += '<tr>';
                    html += '<td><span style="margin-right:8px;">' + icon + '</span><a href="' + esc(f.url || '#') + '" class="file-link" target="_blank">' + esc(f.filename) + '</a></td>';
                    html += '<td>' + size + '</td>';
                    html += '<td>' + date + '</td>';
                    if (canEdit) {
                        html += '<td>';
                        html += '<button class="tf-btn tf-btn-ghost tf-btn-sm" onclick="archiveDoc(\'' + catKey + '\', \'' + esc(f.filename) + '\')">Archive</button>';
                        html += '</td>';
                    }
                    html += '</tr>';
                });

                html += '</tbody></table>';
            }

            // Archived toggle
            html += '<button class="archive-toggle" id="archToggle-' + catKey + '" onclick="toggleArchived(\'' + catKey + '\', \'' + esc(catLabel) + '\')">Show archived files</button>';
            html += '<div id="archivedList-' + catKey + '" style="display:none;margin-top:var(--tf-sp-2);"></div>';

            panel.innerHTML = html;

            // Setup drag/drop on upload zone
            if (canEdit) {
                var dropZone = document.getElementById('uploadDrop-' + catKey);
                if (dropZone) {
                    dropZone.addEventListener('dragover', function(e) { e.preventDefault(); e.stopPropagation(); this.classList.add('dragover'); });
                    dropZone.addEventListener('dragleave', function(e) { e.preventDefault(); e.stopPropagation(); this.classList.remove('dragover'); });
                    dropZone.addEventListener('drop', function(e) {
                        e.preventDefault(); e.stopPropagation();
                        this.classList.remove('dragover');
                        uploadFilesToCategory(catKey, e.dataTransfer.files);
                    });
                }
            }
        }

        function triggerUpload(catKey) {
            var input = document.getElementById('fileInput');
            input.setAttribute('data-category', catKey);
            input.value = '';
            input.onchange = function(e) {
                uploadFilesToCategory(catKey, e.target.files);
            };
            input.click();
        }

        function uploadFilesToCategory(catKey, files) {
            if (!files || files.length === 0) return;

            var formData = new FormData();
            formData.append('job_code', JOB_CODE);
            formData.append('category', catKey);
            for (var i = 0; i < files.length; i++) {
                formData.append('files', files[i]);
            }

            fetch('/api/project/docs/upload', { method: 'POST', body: formData })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.ok || data.uploaded) {
                    var cats = METADATA.doc_categories || DOC_CATEGORIES;
                    var catObj = cats.find(function(c) { return c.key === catKey; });
                    loadCategoryFiles(catKey, catObj ? catObj.label : catKey);
                    loadDocCounts();
                } else {
                    alert('Upload error: ' + (data.error || 'Unknown'));
                }
            })
            .catch(function(e) { alert('Upload failed: ' + e.message); });
        }

        function archiveDoc(catKey, filename) {
            if (!confirm('Archive "' + filename + '"? It can still be viewed under archived files.')) return;

            fetch('/api/project/docs/archive', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ job_code: JOB_CODE, category: catKey, filename: filename })
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.ok) {
                    var cats = METADATA.doc_categories || DOC_CATEGORIES;
                    var catObj = cats.find(function(c) { return c.key === catKey; });
                    loadCategoryFiles(catKey, catObj ? catObj.label : catKey);
                    loadDocCounts();
                } else {
                    alert('Archive error: ' + (data.error || 'Unknown'));
                }
            });
        }

        function toggleArchived(catKey, catLabel) {
            var container = document.getElementById('archivedList-' + catKey);
            var toggle = document.getElementById('archToggle-' + catKey);

            if (container.style.display !== 'none') {
                container.style.display = 'none';
                toggle.textContent = 'Show archived files';
                return;
            }

            container.innerHTML = '<div style="color:var(--tf-gray-400);font-size:var(--tf-text-sm);padding:var(--tf-sp-2);">Loading...</div>';
            container.style.display = 'block';
            toggle.textContent = 'Hide archived files';

            fetch('/api/project/docs/archived', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ job_code: JOB_CODE, category: catKey })
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                var files = data.files || [];
                if (files.length === 0) {
                    container.innerHTML = '<div style="color:var(--tf-gray-400);font-size:var(--tf-text-sm);font-style:italic;padding:var(--tf-sp-2);">No archived files</div>';
                    return;
                }
                var html = '<table class="file-list-table" style="opacity:0.7"><thead><tr><th>Archived File</th><th>Size</th><th>Archived</th></tr></thead><tbody>';
                files.forEach(function(f) {
                    html += '<tr>';
                    html += '<td><a href="' + esc(f.url || '#') + '" class="file-link" target="_blank" style="color:var(--tf-gray-500);">' + esc(f.filename) + '</a></td>';
                    html += '<td>' + formatSize(f.size || 0) + '</td>';
                    html += '<td>' + (f.archived_at ? new Date(f.archived_at).toLocaleDateString() : '') + '</td>';
                    html += '</tr>';
                });
                html += '</tbody></table>';
                container.innerHTML = html;
            })
            .catch(function() {
                container.innerHTML = '<div style="color:var(--tf-danger);font-size:var(--tf-text-sm);">Error loading archived files</div>';
            });
        }

        // ── Next Steps ────────────────────────────────────
        function loadNextSteps() {
            fetch('/api/project/next-steps?job_code=' + encodeURIComponent(JOB_CODE))
            .then(function(r) { return r.json(); })
            .then(function(data) {
                renderNextSteps(data);
            })
            .catch(function() {
                // Fallback: use embedded data
                var stage = METADATA.stage || 'quote';
                var steps = NEXT_STEPS[stage] || NEXT_STEPS['quote'] || [];
                var checklist = METADATA.checklist || {};
                renderNextSteps({
                    stage: stage,
                    steps: steps.map(function(s) {
                        return {
                            text: s.text, key: s.key,
                            completed: s.key in checklist
                        };
                    }),
                    completion_pct: 0
                });
            });
        }

        function renderNextSteps(data) {
            var body = document.getElementById('nextStepsBody');
            var label = document.getElementById('stepsStageLabel');
            label.textContent = formatStage(data.stage);

            // Update completion bar
            var pct = data.completion_pct || 0;
            document.getElementById('completionFill').style.width = pct + '%';
            document.getElementById('completionPct').textContent = pct + '%';

            var steps = data.steps || [];
            if (steps.length === 0) {
                body.innerHTML = '<div style="padding:var(--tf-sp-4);color:var(--tf-gray-400);text-align:center;font-size:var(--tf-text-sm);">No steps for this stage</div>';
                return;
            }

            body.innerHTML = '';
            steps.forEach(function(step) {
                var item = document.createElement('div');
                item.className = 'step-item';

                var checkbox = document.createElement('div');
                checkbox.className = 'step-checkbox' + (step.completed ? ' checked' : '');
                checkbox.innerHTML = step.completed ? '&#10003;' : '';
                checkbox.onclick = function() { toggleStep(step.key, !step.completed); };

                var textArea = document.createElement('div');
                var textEl = document.createElement('div');
                textEl.className = 'step-text' + (step.completed ? ' completed' : '');
                textEl.textContent = step.text;
                textArea.appendChild(textEl);

                if (step.completed && step.completed_by) {
                    var meta = document.createElement('div');
                    meta.className = 'step-meta';
                    meta.textContent = 'by ' + step.completed_by;
                    if (step.completed_at) meta.textContent += ' on ' + new Date(step.completed_at).toLocaleDateString();
                    textArea.appendChild(meta);
                }

                item.appendChild(checkbox);
                item.appendChild(textArea);
                body.appendChild(item);
            });
        }

        function toggleStep(itemKey, checked) {
            fetch('/api/project/checklist', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ job_code: JOB_CODE, item_key: itemKey, checked: checked })
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.ok) {
                    METADATA.checklist = data.checklist;
                    loadNextSteps();
                }
            });
        }

        // ── Stage Update ──────────────────────────────────
        function updateStage(newStage) {
            fetch('/api/project/metadata', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ job_code: JOB_CODE, updates: { stage: newStage } })
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.ok) {
                    METADATA.stage = newStage;
                    loadNextSteps();
                    renderProjectStats();
                }
            });
        }

        // ── Notes Save ────────────────────────────────────
        function saveNotes() {
            var notes = document.getElementById('notesArea').value;
            if (notes === (METADATA.notes || '')) return;

            fetch('/api/project/metadata', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ job_code: JOB_CODE, updates: { notes: notes } })
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.ok) METADATA.notes = notes;
            });
        }

        // ── Intelligence Panel ────────────────────────────
        function loadIntelligence() {
            // Try to load from project calc data
            fetch('/api/project/load', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: JOB_CODE })
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.data) {
                    renderIntelligence(data.data);
                }
            })
            .catch(function() { /* Leave default message */ });
        }

        function renderIntelligence(calcData) {
            var body = document.getElementById('intelBody');
            var project = calcData.project || {};
            var totals = calcData.totals || {};
            var tc = calcData.tc_data || {};

            var html = '';

            // Price per sq/ft
            var sellPrice = totals.sellPrice || totals.sell_price || tc.total_price || 0;
            var sqft = project.width && project.length ? (parseFloat(project.width) * parseFloat(project.length)) : 0;
            var pricePerSqft = sqft > 0 ? (sellPrice / sqft) : 0;

            if (sellPrice > 0) {
                html += '<div class="intel-stat"><span class="intel-stat-label">Sell Price</span><span class="intel-stat-value highlight">$' + Number(sellPrice).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) + '</span></div>';
            }

            if (pricePerSqft > 0) {
                html += '<div class="intel-stat"><span class="intel-stat-label">Price / Sq Ft</span><span class="intel-stat-value">$' + pricePerSqft.toFixed(2) + '</span></div>';
            }

            // Steel weight
            var steelWeight = totals.totalWeight || totals.total_weight || 0;
            if (steelWeight > 0) {
                html += '<div class="intel-stat"><span class="intel-stat-label">Steel Weight</span><span class="intel-stat-value">' + Number(steelWeight).toLocaleString() + ' lbs</span></div>';
            }

            // Sq footage
            if (sqft > 0) {
                html += '<div class="intel-stat"><span class="intel-stat-label">Square Footage</span><span class="intel-stat-value">' + Number(sqft).toLocaleString() + ' sq ft</span></div>';
            }

            // Options checked
            var options = calcData.options || tc.options || {};
            var checkedOpts = Object.keys(options).filter(function(k) { return options[k] === true || options[k] === 'yes'; });
            if (checkedOpts.length > 0) {
                html += '<div class="intel-stat"><span class="intel-stat-label">Options Selected</span><span class="intel-stat-value">' + checkedOpts.length + '</span></div>';
            }

            if (!html) {
                html = '<div style="text-align:center;padding:var(--tf-sp-4);color:var(--tf-gray-400);font-size:var(--tf-text-sm);">Run a calculation in SA Calc or TC Quote to populate intelligence data.</div>';
            } else {
                // Add suggestions
                html += '<div class="intel-suggestions"><h4>Suggestions</h4>';
                var stage = METADATA.stage || 'quote';
                var suggestions = getStageSuggestions(stage, sellPrice, steelWeight, sqft);
                suggestions.forEach(function(s) {
                    html += '<div class="suggestion-item"><span class="suggestion-bullet">&#9658;</span><span>' + s + '</span></div>';
                });
                html += '</div>';
            }

            body.innerHTML = html;
        }

        function getStageSuggestions(stage, price, weight, sqft) {
            var s = [];
            if (stage === 'quote') {
                if (price > 0) s.push('Quote is ready — send to customer for review');
                s.push('Double-check material availability before finalizing');
                if (weight > 10000) s.push('Heavy project — consider delivery logistics early');
            } else if (stage === 'contract') {
                s.push('Get signed contract before ordering materials');
                s.push('Confirm customer deposit received');
            } else if (stage === 'engineering') {
                s.push('Verify structural calculations with PE stamp');
                s.push('Check local building code requirements');
            } else if (stage === 'fabrication') {
                s.push('Confirm all materials are in stock');
                if (weight > 0) s.push('Estimated ' + Math.ceil(weight / 2000) + ' man-hours at current rate');
            } else if (stage === 'shipping' || stage === 'install') {
                s.push('Confirm delivery address and site access');
                s.push('Schedule installation crew');
            } else if (stage === 'complete') {
                s.push('Send final invoice and collect payment');
                s.push('Archive project when fully closed');
            }
            if (s.length === 0) s.push('Keep project details up to date');
            return s;
        }

        // ── Quick Actions ─────────────────────────────────
        function openInSACalc() {
            window.location.href = '/sa?project=' + encodeURIComponent(JOB_CODE);
        }

        function openInTCQuote() {
            window.location.href = '/tc?project=' + encodeURIComponent(JOB_CODE);
        }

        function duplicateProject() {
            if (!confirm('Create a duplicate of this project with a new job code?')) return;

            fetch('/api/project/next-code')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                var newCode = data.job_code;
                var payload = {
                    job_code: newCode,
                    project_name: (METADATA.project_name || '') + ' (Copy)',
                    customer_name: (METADATA.customer || {}).name || '',
                    customer_phone: (METADATA.customer || {}).phone || '',
                    customer_email: (METADATA.customer || {}).email || '',
                    location_street: (METADATA.location || {}).street || '',
                    location_city: (METADATA.location || {}).city || '',
                    location_state: (METADATA.location || {}).state || '',
                    location_zip: (METADATA.location || {}).zip || '',
                    stage: 'quote',
                    notes: 'Duplicated from ' + JOB_CODE,
                };
                return fetch('/api/project/create', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.ok) {
                    alert('Project duplicated as ' + data.job_code);
                    window.location.href = '/project/' + data.job_code;
                } else {
                    alert('Error: ' + (data.error || 'Unknown'));
                }
            })
            .catch(function(e) { alert('Error: ' + e.message); });
        }

        function archiveProject() {
            if (!confirm('Archive this project? It will be hidden from the active dashboard.')) return;

            fetch('/api/project/metadata', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ job_code: JOB_CODE, updates: { archived: true } })
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.ok) {
                    alert('Project archived');
                    window.location.href = '/';
                }
            });
        }

        // ── Helpers ───────────────────────────────────────
        function esc(s) {
            var d = document.createElement('div');
            d.textContent = s || '';
            return d.innerHTML;
        }

        function formatStage(s) {
            if (!s) return '';
            return s.replace(/_/g, ' ').replace(/\b\w/g, function(c) { return c.toUpperCase(); });
        }

        function formatDate(iso) {
            if (!iso) return '-';
            return new Date(iso).toLocaleDateString();
        }

        function formatSize(bytes) {
            if (bytes < 1024) return bytes + ' B';
            if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
            return (bytes / 1048576).toFixed(1) + ' MB';
        }
    </script>
</body>
</html>
"""
