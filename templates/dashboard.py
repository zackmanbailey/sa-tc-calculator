DASHBOARD_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TitanForge - Dashboard</title>
    <style>
        :root {
            --color-navy: #0F172A;
            --color-steel-blue: #1E40AF;
            --color-orange: #F59E0B;
            --color-white: #F8FAFC;
            --color-dark-gray: #1F2937;
            --color-light-gray: #E5E7EB;
            --color-border: #D1D5DB;
            --color-text: #111827;
            --color-text-light: #6B7280;
            --color-success: #10B981;
            --color-danger: #EF4444;
            --color-warning: #F59E0B;
            --color-info: #3B82F6;
            --border-radius-sm: 6px;
            --border-radius-md: 8px;
            --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.1);
            --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
            --transition: all 0.3s ease;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: var(--color-white);
            color: var(--color-text);
            line-height: 1.6;
        }

        /* TOP NAVIGATION BAR */
        .navbar {
            position: sticky;
            top: 0;
            z-index: 1000;
            background-color: var(--color-navy);
            color: white;
            padding: 1rem 2rem;
            box-shadow: var(--shadow-md);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 2rem;
        }

        .navbar-brand {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-weight: 700;
            font-size: 1.25rem;
        }

        .navbar-logo {
            width: 32px;
            height: 32px;
        }

        .navbar-nav {
            display: flex;
            gap: 2rem;
            align-items: center;
            flex: 1;
            justify-content: center;
        }

        .navbar-nav a {
            color: white;
            text-decoration: none;
            font-size: 0.95rem;
            transition: var(--transition);
            padding: 0.5rem 1rem;
            border-radius: var(--border-radius-sm);
        }

        .navbar-nav a:hover,
        .navbar-nav a.active {
            background-color: var(--color-steel-blue);
            color: var(--color-orange);
        }

        .navbar-right {
            display: flex;
            align-items: center;
            gap: 1.5rem;
        }

        .inventory-alert {
            position: relative;
            cursor: pointer;
            transition: var(--transition);
        }

        .inventory-alert:hover {
            color: var(--color-orange);
        }

        .alert-badge {
            position: absolute;
            top: -8px;
            right: -8px;
            background-color: var(--color-danger);
            color: white;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
            font-weight: 700;
        }

        .user-section {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .role-badge {
            background-color: var(--color-steel-blue);
            padding: 0.25rem 0.75rem;
            border-radius: var(--border-radius-sm);
            font-size: 0.8rem;
            font-weight: 600;
        }

        .logout-btn {
            background-color: var(--color-danger);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: var(--border-radius-sm);
            cursor: pointer;
            font-size: 0.9rem;
            transition: var(--transition);
        }

        .logout-btn:hover {
            background-color: #DC2626;
        }

        /* MAIN CONTAINER */
        .container {
            max-width: 1920px;
            margin: 0 auto;
            padding: 2rem;
        }

        /* HEADER */
        .page-header {
            margin-bottom: 2rem;
        }

        .page-title {
            font-size: 2rem;
            font-weight: 700;
            color: var(--color-navy);
            margin-bottom: 0.5rem;
        }

        .page-subtitle {
            color: var(--color-text-light);
            font-size: 1rem;
        }

        /* STATS GRID */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .stat-card {
            background-color: white;
            border: 1px solid var(--color-border);
            border-radius: var(--border-radius-md);
            padding: 1.5rem;
            box-shadow: var(--shadow-sm);
            transition: var(--transition);
        }

        .stat-card:hover {
            box-shadow: var(--shadow-md);
            border-color: var(--color-steel-blue);
        }

        .stat-label {
            color: var(--color-text-light);
            font-size: 0.9rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }

        .stat-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--color-navy);
        }

        .stat-icon {
            width: 48px;
            height: 48px;
            background-color: var(--color-steel-blue);
            border-radius: var(--border-radius-md);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.5rem;
            margin-bottom: 1rem;
        }

        /* SECTION HEADERS */
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            margin-top: 2rem;
        }

        .section-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--color-navy);
        }

        .view-toggle {
            display: flex;
            gap: 0.5rem;
            background-color: var(--color-light-gray);
            padding: 0.25rem;
            border-radius: var(--border-radius-sm);
        }

        .toggle-btn {
            background-color: transparent;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: var(--border-radius-sm);
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 600;
            transition: var(--transition);
            color: var(--color-text-light);
        }

        .toggle-btn.active {
            background-color: white;
            color: var(--color-navy);
            box-shadow: var(--shadow-sm);
        }

        /* QUICK ACTIONS */
        .quick-actions {
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
            flex-wrap: wrap;
        }

        .btn {
            background-color: var(--color-steel-blue);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: var(--border-radius-sm);
            cursor: pointer;
            font-size: 0.95rem;
            font-weight: 600;
            transition: var(--transition);
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }

        .btn:hover {
            background-color: #1e3a8a;
            box-shadow: var(--shadow-md);
        }

        .btn-primary {
            background-color: var(--color-steel-blue);
        }

        .btn-primary:hover {
            background-color: #1e3a8a;
        }

        .btn-secondary {
            background-color: var(--color-orange);
            color: white;
        }

        .btn-secondary:hover {
            background-color: #D97706;
        }

        .btn-sm {
            padding: 0.5rem 1rem;
            font-size: 0.85rem;
        }

        .btn-icon {
            width: 20px;
            height: 20px;
        }

        /* KANBAN VIEW */
        .kanban-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .kanban-column {
            background-color: var(--color-light-gray);
            border-radius: var(--border-radius-md);
            padding: 1rem;
        }

        .column-header {
            font-weight: 700;
            color: var(--color-navy);
            margin-bottom: 1rem;
            font-size: 0.95rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .project-card {
            background-color: white;
            border-left: 4px solid var(--color-steel-blue);
            border-radius: var(--border-radius-md);
            padding: 1rem;
            margin-bottom: 1rem;
            cursor: pointer;
            transition: var(--transition);
            box-shadow: var(--shadow-sm);
        }

        .project-card:hover {
            box-shadow: var(--shadow-md);
            transform: translateY(-2px);
        }

        .project-card.quote { border-left-color: #94A3B8; }
        .project-card.contract { border-left-color: #3B82F6; }
        .project-card.engineering { border-left-color: #8B5CF6; }
        .project-card.shop-drawings { border-left-color: #EC4899; }
        .project-card.fabrication { border-left-color: #F59E0B; }
        .project-card.shipping { border-left-color: #10B981; }
        .project-card.install { border-left-color: #06B6D4; }
        .project-card.complete { border-left-color: #14B8A6; }

        .card-job-code {
            font-weight: 700;
            color: var(--color-navy);
            font-size: 0.9rem;
        }

        .card-project-name {
            font-weight: 600;
            color: var(--color-text);
            margin-top: 0.5rem;
            font-size: 0.95rem;
        }

        .card-customer {
            color: var(--color-text-light);
            font-size: 0.85rem;
            margin-top: 0.25rem;
        }

        .card-price {
            color: var(--color-steel-blue);
            font-weight: 700;
            margin-top: 0.75rem;
            font-size: 0.9rem;
        }

        .card-price.hidden {
            display: none;
        }

        /* TABLE VIEW */
        .table-container {
            background-color: white;
            border-radius: var(--border-radius-md);
            box-shadow: var(--shadow-sm);
            overflow-x: auto;
        }

        .table {
            width: 100%;
            border-collapse: collapse;
        }

        .table thead {
            background-color: var(--color-light-gray);
            border-bottom: 2px solid var(--color-border);
        }

        .table th {
            padding: 1rem;
            text-align: left;
            font-weight: 700;
            color: var(--color-navy);
            font-size: 0.9rem;
            cursor: pointer;
            user-select: none;
            transition: var(--transition);
        }

        .table th:hover {
            background-color: var(--color-border);
        }

        .table td {
            padding: 1rem;
            border-bottom: 1px solid var(--color-border);
        }

        .table tbody tr {
            transition: var(--transition);
            cursor: pointer;
        }

        .table tbody tr:hover {
            background-color: #F9FAFB;
        }

        .stage-badge {
            display: inline-block;
            padding: 0.375rem 0.75rem;
            border-radius: var(--border-radius-sm);
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: capitalize;
        }

        .stage-quote { background-color: #E2E8F0; color: #334155; }
        .stage-contract { background-color: #DBEAFE; color: #1E40AF; }
        .stage-engineering { background-color: #EDE9FE; color: #6D28D9; }
        .stage-shop-drawings { background-color: #FCE7F3; color: #BE185D; }
        .stage-fabrication { background-color: #FEF3C7; color: #92400E; }
        .stage-shipping { background-color: #DCFCE7; color: #166534; }
        .stage-install { background-color: #CFFAFE; color: #164E63; }
        .stage-complete { background-color: #CCFBF1; color: #134E4A; }

        .price.hidden {
            display: none;
        }

        /* INVENTORY ALERTS */
        .alerts-section {
            display: none;
        }

        .alerts-section.show {
            display: block;
        }

        .alerts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .alert-card {
            border-radius: var(--border-radius-md);
            padding: 1.5rem;
            box-shadow: var(--shadow-sm);
            cursor: pointer;
            transition: var(--transition);
            border-left: 4px solid;
        }

        .alert-card:hover {
            box-shadow: var(--shadow-md);
            transform: translateY(-2px);
        }

        .alert-card.danger {
            background-color: #FEE2E2;
            border-left-color: var(--color-danger);
        }

        .alert-card.warning {
            background-color: #FEF3C7;
            border-left-color: var(--color-warning);
        }

        .alert-title {
            font-weight: 700;
            color: var(--color-navy);
            margin-bottom: 0.5rem;
        }

        .alert-message {
            color: var(--color-text);
            font-size: 0.9rem;
        }

        /* MODAL */
        .modal {
            display: none;
            position: fixed;
            z-index: 2000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            animation: fadeIn 0.3s ease;
        }

        .modal.show {
            display: flex;
            align-items: center;
            justify-content: center;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        .modal-content {
            background-color: white;
            border-radius: var(--border-radius-md);
            width: 90%;
            max-width: 900px;
            max-height: 85vh;
            overflow-y: auto;
            box-shadow: var(--shadow-lg);
            animation: slideUp 0.3s ease;
        }

        @keyframes slideUp {
            from {
                transform: translateY(50px);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1.5rem;
            border-bottom: 1px solid var(--color-border);
            background-color: var(--color-light-gray);
        }

        .modal-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--color-navy);
        }

        .modal-badge-group {
            display: flex;
            gap: 0.75rem;
            margin-top: 0.5rem;
        }

        .modal-badge {
            display: inline-block;
            padding: 0.375rem 0.75rem;
            background-color: var(--color-steel-blue);
            color: white;
            border-radius: var(--border-radius-sm);
            font-size: 0.8rem;
            font-weight: 600;
        }

        .close-btn {
            background: none;
            border: none;
            font-size: 2rem;
            cursor: pointer;
            color: var(--color-text-light);
            transition: var(--transition);
        }

        .close-btn:hover {
            color: var(--color-navy);
        }

        .modal-body {
            padding: 2rem;
        }

        .tab-buttons {
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
            border-bottom: 2px solid var(--color-border);
        }

        .tab-btn {
            background: none;
            border: none;
            padding: 1rem 0;
            font-size: 1rem;
            font-weight: 600;
            color: var(--color-text-light);
            cursor: pointer;
            transition: var(--transition);
            border-bottom: 3px solid transparent;
            margin-bottom: -2px;
        }

        .tab-btn.active {
            color: var(--color-steel-blue);
            border-bottom-color: var(--color-steel-blue);
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .info-item {
            border: 1px solid var(--color-border);
            border-radius: var(--border-radius-md);
            padding: 1rem;
            background-color: var(--color-white);
        }

        .info-label {
            color: var(--color-text-light);
            font-size: 0.9rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }

        .info-value {
            color: var(--color-navy);
            font-size: 1rem;
            font-weight: 600;
        }

        /* DOCUMENTS SECTION */
        .document-categories {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
        }

        .doc-category-btn {
            background-color: var(--color-light-gray);
            border: 1px solid var(--color-border);
            padding: 0.5rem 1rem;
            border-radius: var(--border-radius-sm);
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 600;
            transition: var(--transition);
        }

        .doc-category-btn.active {
            background-color: var(--color-steel-blue);
            color: white;
            border-color: var(--color-steel-blue);
        }

        .upload-zone {
            border: 2px dashed var(--color-border);
            border-radius: var(--border-radius-md);
            padding: 2rem;
            text-align: center;
            cursor: pointer;
            transition: var(--transition);
            background-color: var(--color-white);
            margin-bottom: 1.5rem;
        }

        .upload-zone:hover {
            border-color: var(--color-steel-blue);
            background-color: #F0F9FF;
        }

        .upload-zone.dragover {
            border-color: var(--color-orange);
            background-color: #FFFBEB;
        }

        .upload-text {
            color: var(--color-text-light);
            font-size: 0.95rem;
        }

        .upload-highlight {
            color: var(--color-steel-blue);
            font-weight: 600;
        }

        .file-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 1rem;
        }

        .file-card {
            border: 1px solid var(--color-border);
            border-radius: var(--border-radius-md);
            padding: 1rem;
            text-align: center;
            transition: var(--transition);
            position: relative;
        }

        .file-card:hover {
            box-shadow: var(--shadow-md);
            border-color: var(--color-steel-blue);
        }

        .file-icon {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }

        .file-name {
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--color-text);
            word-break: break-all;
            margin-bottom: 0.5rem;
        }

        .file-delete {
            background: none;
            border: none;
            color: var(--color-danger);
            cursor: pointer;
            font-size: 1.2rem;
            padding: 0.25rem;
            transition: var(--transition);
        }

        .file-delete:hover {
            color: #DC2626;
        }

        .file-delete.hidden {
            display: none;
        }

        /* REVISIONS TABLE */
        .revisions-table {
            width: 100%;
            border-collapse: collapse;
        }

        .revisions-table thead {
            background-color: var(--color-light-gray);
        }

        .revisions-table th,
        .revisions-table td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid var(--color-border);
        }

        .revisions-table th {
            font-weight: 700;
            color: var(--color-navy);
            font-size: 0.9rem;
        }

        .revisions-table tbody tr:hover {
            background-color: #F9FAFB;
        }

        .revision-action-btn {
            background-color: var(--color-steel-blue);
            color: white;
            border: none;
            padding: 0.375rem 0.75rem;
            border-radius: var(--border-radius-sm);
            cursor: pointer;
            font-size: 0.8rem;
            transition: var(--transition);
            margin-right: 0.5rem;
        }

        .revision-action-btn:hover {
            background-color: #1e3a8a;
        }

        /* RESPONSIVE */
        @media (max-width: 1024px) {
            .navbar {
                flex-direction: column;
                gap: 1rem;
                padding: 1rem;
            }

            .navbar-nav {
                flex-direction: column;
                gap: 0.5rem;
                justify-content: flex-start;
            }

            .navbar-right {
                flex-direction: column;
                width: 100%;
            }

            .container {
                padding: 1rem;
            }

            .stats-grid {
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            }

            .kanban-container {
                grid-template-columns: 1fr;
            }

            .modal-content {
                width: 95%;
                max-height: 90vh;
            }
        }

        @media (max-width: 768px) {
            .navbar-nav {
                display: none;
            }

            .page-title {
                font-size: 1.5rem;
            }

            .section-title {
                font-size: 1.25rem;
            }

            .quick-actions {
                flex-direction: column;
            }

            .btn {
                width: 100%;
                justify-content: center;
            }

            .stats-grid {
                grid-template-columns: 1fr;
            }

            .file-list {
                grid-template-columns: 1fr;
            }
        }

        /* LOADING STATE */
        .loading {
            opacity: 0.6;
            pointer-events: none;
        }

        .spinner {
            border: 4px solid var(--color-light-gray);
            border-top: 4px solid var(--color-steel-blue);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 2rem auto;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .empty-state {
            text-align: center;
            padding: 3rem 1rem;
            color: var(--color-text-light);
        }

        .empty-state-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
        }

        .empty-state-title {
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--color-navy);
            margin-bottom: 0.5rem;
        }
    </style>
</head>
<body>
    <script>
        // Role-based access control
        const USER_ROLE = '{{USER_ROLE}}';
        const USER_NAME = '{{USER_NAME}}';
    </script>

    <!-- TOP NAVIGATION BAR -->
    <nav class="navbar">
        <div class="navbar-brand">
            <svg class="navbar-logo" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
                <!-- Anvil Icon -->
                <rect x="8" y="20" width="24" height="15" fill="none" stroke="#F59E0B" stroke-width="2" rx="2"/>
                <rect x="10" y="18" width="20" height="3" fill="#F59E0B"/>
                <circle cx="12" cy="14" r="2" fill="#F59E0B"/>
                <circle cx="28" cy="14" r="2" fill="#F59E0B"/>
                <line x1="12" y1="16" x2="12" y2="18" stroke="#F59E0B" stroke-width="1.5"/>
                <line x1="28" y1="16" x2="28" y2="18" stroke="#F59E0B" stroke-width="1.5"/>
            </svg>
            TITANFORGE
        </div>

        <div class="navbar-nav">
            <a href="#" class="nav-link active" data-section="dashboard">Dashboard</a>
            <a href="#" class="nav-link" data-section="calculator">SA Calculator</a>
            <a href="#" class="nav-link" data-section="quote">TC Quote</a>
            <a href="#" class="nav-link" data-section="inventory">Inventory</a>
        </div>

        <div class="navbar-right">
            <div class="inventory-alert" id="inventoryAlert" style="display: none;">
                <span>🔔</span>
                <span class="alert-badge" id="alertCount">0</span>
            </div>
            <div class="user-section">
                <span id="userName">User</span>
                <span class="role-badge" id="userRole">User</span>
                <button class="logout-btn" onclick="handleLogout()">Logout</button>
            </div>
        </div>
    </nav>

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
                <div class="stat-icon">📊</div>
                <div class="stat-label">Active Projects</div>
                <div class="stat-value" id="activeProjects">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">🔧</div>
                <div class="stat-label">In Fabrication</div>
                <div class="stat-value" id="inFabrication">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📦</div>
                <div class="stat-label">Ready to Ship</div>
                <div class="stat-value" id="readyToShip">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">💰</div>
                <div class="stat-label">Pipeline Value</div>
                <div class="stat-value" id="pipelineValue">-</div>
            </div>
        </div>

        <!-- QUICK ACTIONS -->
        <div class="quick-actions">
            <button class="btn btn-primary" onclick="openNewProjectForm()">
                <span>+</span> New Project
            </button>
            <button class="btn btn-secondary" onclick="navigateTo('calculator')">
                Open SA Calculator
            </button>
            <button class="btn btn-secondary" onclick="navigateTo('quote')">
                Open TC Quote
            </button>
            <button class="btn btn-secondary" onclick="navigateTo('inventory')">
                View Inventory
            </button>
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
                <button class="toggle-btn active" id="kanbanToggle" onclick="switchView('kanban')">
                    Kanban View
                </button>
                <button class="toggle-btn" id="tableToggle" onclick="switchView('table')">
                    Table View
                </button>
            </div>
        </div>

        <!-- KANBAN VIEW -->
        <div id="kanbanView" class="kanban-container"></div>

        <!-- TABLE VIEW -->
        <div id="tableView" class="table-container" style="display: none;">
            <table class="table">
                <thead>
                    <tr>
                        <th onclick="sortTable('jobCode')">Job Code ↕</th>
                        <th onclick="sortTable('name')">Project Name ↕</th>
                        <th onclick="sortTable('customer')">Customer ↕</th>
                        <th onclick="sortTable('stage')">Stage ↕</th>
                        <th class="price" onclick="sortTable('price')">Sell Price ↕</th>
                        <th onclick="sortTable('updated')">Last Updated ↕</th>
                        <th onclick="sortTable('version')">Version ↕</th>
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
                            <span style="font-size: 0.85rem;">PDF, DOCX, XLSX, Images</span>
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
        // Global state
        let allProjects = [];
        let currentView = 'kanban';
        let currentProject = null;
        let currentSortColumn = null;
        let currentSortDirection = 'asc';
        let inventoryAlerts = [];

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            initializePage();
        });

        function initializePage() {
            // Set user info
            if (USER_NAME && USER_NAME !== '{{USER_NAME}}') {
                document.getElementById('userName').textContent = USER_NAME;
            }

            const roleText = USER_ROLE && USER_ROLE !== '{{USER_ROLE}}' ? USER_ROLE : 'User';
            document.getElementById('userRole').textContent = roleText.toUpperCase();

            // Load data
            loadProjects();
            loadInventoryAlerts();
            setupEventListeners();

            // Hide pricing for certain roles
            if (USER_ROLE === 'shop') {
                document.querySelectorAll('.price').forEach(el => el.classList.add('hidden'));
            }
        }

        function setupEventListeners() {
            // Modal close on background click
            document.getElementById('projectModal').addEventListener('click', function(e) {
                if (e.target === this) {
                    closeProjectModal();
                }
            });
        }

        function loadProjects() {
            // Simulate API call - replace with actual fetch
            fetch('/api/projects')
                .then(response => response.json())
                .then(data => {
                    allProjects = data.projects || [];
                    updateStats();
                    renderProjects();
                })
                .catch(error => {
                    console.error('Error loading projects:', error);
                    // Fallback mock data
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
                    // No alerts if API fails
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
            const totalValue = allProjects.reduce((sum, p) => sum + (p.sellPrice || 0), 0);

            document.getElementById('activeProjects').textContent = activeCount;
            document.getElementById('inFabrication').textContent = fabricatingCount;
            document.getElementById('readyToShip').textContent = readyCount;
            document.getElementById('pipelineValue').textContent = '$' + totalValue.toLocaleString();
        }

        function renderProjects() {
            if (currentView === 'kanban') {
                renderKanban();
            } else {
                renderTable();
            }
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
            card.className = 'project-card ' + project.stage.replace('-', '-');
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

                row.innerHTML = `
                    <td>${project.jobCode}</td>
                    <td><strong>${project.name}</strong></td>
                    <td>${project.customer}</td>
                    <td><span class="stage-badge ${stageBadgeClass}">${stageLabel}</span></td>
                    <td class="price">$${project.sellPrice.toLocaleString()}</td>
                    <td>${new Date(project.lastUpdated).toLocaleDateString()}</td>
                    <td>${project.version}</td>
                `;

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
                alertCard.onclick = () => navigateTo('inventory');

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

            // Update alert badge
            const alertCount = inventoryAlerts.length;
            if (alertCount > 0) {
                document.getElementById('inventoryAlert').style.display = 'block';
                document.getElementById('alertCount').textContent = alertCount;
            }
        }

        function switchView(view) {
            currentView = view;

            // Update toggle buttons
            document.getElementById('kanbanToggle').classList.toggle('active', view === 'kanban');
            document.getElementById('tableToggle').classList.toggle('active', view === 'table');

            // Update visibility
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

                if (column === 'price') {
                    aVal = a.sellPrice;
                    bVal = b.sellPrice;
                }

                if (typeof aVal === 'string') {
                    aVal = aVal.toLowerCase();
                    bVal = bVal.toLowerCase();
                }

                const comparison = aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
                return currentSortDirection === 'asc' ? comparison : -comparison;
            });

            renderTable();
        }

        function openProjectModal(project) {
            currentProject = project;

            // Set title and badges
            document.getElementById('modalTitle').textContent = project.jobCode + ' - ' + project.name;
            const badgeGroup = document.getElementById('modalBadgeGroup');
            badgeGroup.innerHTML = '';

            const stageBadge = document.createElement('span');
            stageBadge.className = 'modal-badge';
            stageBadge.style.backgroundColor = '#1E40AF';
            stageBadge.textContent = project.stage.toUpperCase();

            const versionBadge = document.createElement('span');
            versionBadge.className = 'modal-badge';
            versionBadge.style.backgroundColor = '#F59E0B';
            versionBadge.textContent = 'v' + project.version;

            badgeGroup.appendChild(stageBadge);
            badgeGroup.appendChild(versionBadge);

            // Load project details
            loadProjectDetails(project.id);

            // Show modal
            document.getElementById('projectModal').classList.add('show');
        }

        function closeProjectModal() {
            document.getElementById('projectModal').classList.remove('show');
            currentProject = null;
        }

        function loadProjectDetails(projectId) {
            // Simulate API call
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
                    // Use current project data
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
            // Mock document categories
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

            // Mock files
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

                const iconMap = {
                    pdf: '📄',
                    docx: '📘',
                    xlsx: '📊',
                    jpg: '🖼️',
                    png: '🖼️',
                    gif: '🖼️'
                };

                const icon = document.createElement('div');
                icon.className = 'file-icon';
                icon.textContent = iconMap[file.type] || '📁';

                const name = document.createElement('div');
                name.className = 'file-name';
                name.textContent = file.name;

                fileCard.appendChild(icon);
                fileCard.appendChild(name);

                if (USER_ROLE !== 'viewer') {
                    const deleteBtn = document.createElement('button');
                    deleteBtn.className = 'file-delete';
                    deleteBtn.textContent = '🗑️';
                    deleteBtn.onclick = () => deleteFile(file.name);
                    fileCard.appendChild(deleteBtn);
                }

                fileList.appendChild(fileCard);
            });
        }

        function handleDragOver(e) {
            e.preventDefault();
            e.stopPropagation();
            document.getElementById('uploadZone').classList.add('dragover');
        }

        function handleDragLeave(e) {
            e.preventDefault();
            e.stopPropagation();
            document.getElementById('uploadZone').classList.remove('dragover');
        }

        function handleDrop(e) {
            e.preventDefault();
            e.stopPropagation();
            document.getElementById('uploadZone').classList.remove('dragover');

            const files = e.dataTransfer.files;
            uploadFiles(files);
        }

        function handleFileSelect(e) {
            const files = e.target.files;
            uploadFiles(files);
        }

        function uploadFiles(files) {
            if (USER_ROLE === 'viewer') {
                alert('You do not have permission to upload files.');
                return;
            }

            const formData = new FormData();
            for (let file of files) {
                formData.append('files', file);
            }

            fetch('/api/project/docs/upload', {
                method: 'POST',
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    console.log('Files uploaded:', data);
                    loadProjectDocuments(currentProject.id);
                })
                .catch(error => {
                    console.error('Upload error:', error);
                    alert('Failed to upload files.');
                });
        }

        function deleteFile(fileName) {
            if (USER_ROLE === 'viewer') return;

            if (confirm('Delete this file?')) {
                fetch('/api/project/docs/delete', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ fileName: fileName })
                })
                    .then(response => response.json())
                    .then(data => {
                        console.log('File deleted:', data);
                        loadProjectDocuments(currentProject.id);
                    })
                    .catch(error => console.error('Delete error:', error));
            }
        }

        function loadProjectRevisions(projectId) {
            fetch('/api/project/revisions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: projectId })
            })
                .then(response => response.json())
                .then(data => {
                    renderRevisions(data.revisions || []);
                })
                .catch(error => {
                    console.error('Error loading revisions:', error);
                    renderRevisions([]);
                });
        }

        function renderRevisions(revisions) {
            const revisionsBody = document.getElementById('revisionsBody');
            revisionsBody.innerHTML = '';

            if (revisions.length === 0) {
                revisionsBody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 2rem; color: #6B7280;">No revisions found</td></tr>';
                return;
            }

            revisions.forEach((rev, idx) => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td><strong>v${rev.version}</strong></td>
                    <td>${new Date(rev.date).toLocaleDateString()}</td>
                    <td>${rev.author}</td>
                    <td>${rev.notes || '-'}</td>
                    <td>
                        <button class="revision-action-btn" onclick="loadRevision('${rev.version}')">Load</button>
                        ${idx > 0 ? '<button class="revision-action-btn" onclick="compareRevisions(\'${rev.version}\')">Compare</button>' : ''}
                    </td>
                `;
                revisionsBody.appendChild(row);
            });
        }

        function loadRevision(version) {
            alert('Loading revision ' + version);
            // TODO: Implement revision loading
        }

        function compareRevisions(version) {
            alert('Comparing revisions');
            // TODO: Implement revision comparison
        }

        function switchTab(tabName) {
            // Update buttons
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.toggle('active', btn.textContent.toLowerCase().includes(tabName));
            });

            // Update content
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });

            if (tabName === 'overview') {
                document.getElementById('overviewTab').classList.add('active');
            } else if (tabName === 'documents') {
                document.getElementById('documentsTab').classList.add('active');
            } else if (tabName === 'revisions') {
                document.getElementById('revisionsTab').classList.add('active');
            }
        }

        // Navigation functions
        function navigateTo(section) {
            console.log('Navigate to:', section);
            // TODO: Implement navigation to other sections
        }

        function openNewProjectForm() {
            alert('New project form would open here');
            // TODO: Implement new project form
        }

        function handleLogout() {
            if (confirm('Are you sure you want to logout?')) {
                window.location.href = '/logout';
            }
        }
    </script>
</body>
</html>
"""
