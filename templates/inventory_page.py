INVENTORY_PAGE_HTML = r'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inventory Management - TitanForge</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #0F172A;
            --surface: #1E293B;
            --border: #334155;
            --text: #F1F5F9;
            --text-muted: #94A3B8;
            --accent: #F6AE2D;
            --cyan: #06B6D4;
            --green: #10B981;
            --red: #EF4444;
            --orange: #F59E0B;
            --yellow: #EAB308;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', system-ui, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            line-height: 1.5;
        }

        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }

        /* Title Bar */
        .title-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--border);
        }

        .title-section h1 {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 8px;
            color: var(--text);
        }

        .breadcrumb {
            font-size: 13px;
            color: var(--text-muted);
        }

        .breadcrumb a {
            color: var(--cyan);
            text-decoration: none;
        }

        .breadcrumb a:hover {
            text-decoration: underline;
        }

        /* Stats Row */
        .stats-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }

        .stat-card {
            background-color: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 16px;
            text-align: center;
            cursor: pointer;
            transition: transform 0.15s, border-color 0.15s;
        }

        .stat-card:hover {
            transform: translateY(-2px);
            border-color: var(--cyan);
        }

        .stat-label {
            font-size: 12px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }

        .stat-value {
            font-size: 24px;
            font-weight: 700;
            color: var(--accent);
        }

        /* Main Layout */
        .main-layout {
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }

        /* Sidebar */
        .sidebar {
            background-color: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 20px;
        }

        .sidebar-section {
            margin-bottom: 25px;
        }

        .sidebar-section:last-child {
            margin-bottom: 0;
        }

        .sidebar-title {
            font-size: 12px;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 12px;
        }

        .chart-placeholder {
            width: 100%;
            height: 180px;
            background-color: var(--bg);
            border: 1px solid var(--border);
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--text-muted);
            font-size: 13px;
        }

        .status-summary {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .status-item {
            display: flex;
            justify-content: space-between;
            font-size: 13px;
            padding: 8px;
            background-color: var(--bg);
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.15s;
        }

        .status-item:hover {
            background-color: var(--surface);
        }

        .status-label {
            color: var(--text-muted);
        }

        .status-value {
            font-weight: 600;
            color: var(--text);
        }

        /* Tabs */
        .tabs-container {
            background-color: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
        }

        .tabs-header {
            display: flex;
            border-bottom: 1px solid var(--border);
            background-color: var(--bg);
        }

        .tab-button {
            flex: 1;
            padding: 16px;
            background: none;
            border: none;
            color: var(--text-muted);
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .tab-button:hover {
            background-color: var(--surface);
            color: var(--text);
        }

        .tab-button.active {
            color: var(--accent);
            border-bottom: 3px solid var(--accent);
            background-color: var(--surface);
        }

        .tab-content {
            padding: 20px;
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        /* Filters */
        .filters {
            display: flex;
            gap: 12px;
            margin-bottom: 20px;
            flex-wrap: wrap;
            align-items: center;
        }

        .filter-group {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            align-items: center;
        }

        select, input[type="text"], input[type="number"], input[type="date"] {
            background-color: var(--bg);
            color: var(--text);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 13px;
            font-family: 'Inter', system-ui, sans-serif;
        }

        select:focus, input:focus {
            outline: none;
            border-color: var(--cyan);
            box-shadow: 0 0 0 2px rgba(6, 182, 212, 0.1);
        }

        /* Buttons */
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            font-family: 'Inter', system-ui, sans-serif;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .btn-primary {
            background-color: var(--accent);
            color: var(--bg);
        }

        .btn-primary:hover {
            background-color: #F4A000;
            transform: translateY(-1px);
        }

        .btn-secondary {
            background-color: var(--surface);
            color: var(--text);
            border: 1px solid var(--border);
        }

        .btn-secondary:hover {
            background-color: var(--border);
        }

        .btn-small {
            padding: 6px 12px;
            font-size: 12px;
        }

        .btn-danger {
            background-color: var(--red);
            color: white;
        }

        .btn-danger:hover {
            background-color: #DC2626;
        }

        /* Tables */
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }

        thead {
            background-color: var(--bg);
        }

        th {
            padding: 12px;
            text-align: left;
            font-size: 12px;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 1px solid var(--border);
        }

        td {
            padding: 12px;
            border-bottom: 1px solid var(--border);
            font-size: 13px;
        }

        tbody tr:hover {
            background-color: rgba(30, 41, 59, 0.5);
        }

        /* Status Badges */
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .badge-available {
            background-color: rgba(16, 185, 129, 0.2);
            color: var(--green);
        }

        .badge-committed {
            background-color: rgba(249, 158, 11, 0.2);
            color: var(--orange);
        }

        .badge-low {
            background-color: rgba(239, 68, 68, 0.2);
            color: var(--red);
        }

        .badge-pending {
            background-color: rgba(6, 182, 212, 0.2);
            color: var(--cyan);
        }

        /* Modal */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(15, 23, 42, 0.8);
            overflow: auto;
        }

        .modal.show {
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .modal-content {
            background-color: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 30px;
            max-width: 500px;
            width: 90%;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
        }

        .modal-header {
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .modal-header h2 {
            font-size: 20px;
            font-weight: 700;
            color: var(--text);
        }

        .modal-close {
            background: none;
            border: none;
            color: var(--text-muted);
            font-size: 24px;
            cursor: pointer;
            padding: 0;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .modal-close:hover {
            color: var(--text);
        }

        .form-group {
            margin-bottom: 16px;
        }

        .form-group label {
            display: block;
            margin-bottom: 6px;
            font-size: 13px;
            font-weight: 600;
            color: var(--text);
        }

        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
        }

        .form-group textarea {
            resize: vertical;
            min-height: 80px;
            padding: 8px 12px;
        }

        .modal-footer {
            display: flex;
            gap: 10px;
            margin-top: 24px;
            justify-content: flex-end;
        }

        /* Empty State */
        .empty-state {
            text-align: center;
            padding: 40px 20px;
            color: var(--text-muted);
        }

        .empty-state p {
            margin: 10px 0;
        }

        /* Responsive */
        @media (max-width: 1024px) {
            .main-layout {
                grid-template-columns: 1fr;
            }

            .stats-row {
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            }

            .tabs-header {
                flex-wrap: wrap;
            }

            .tab-button {
                flex: 1 1 auto;
                min-width: 100px;
            }
        }

        @media (max-width: 768px) {
            .container {
                padding: 15px;
            }

            .title-bar {
                flex-direction: column;
                align-items: flex-start;
            }

            .modal-content {
                max-width: 100%;
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Title Bar -->
        <div class="title-bar">
            <div class="title-section">
                <h1>Inventory Management</h1>
                <div class="breadcrumb">
                    <a href="#">Dashboard</a> &gt;
                    <a href="#">Schedule</a> &gt;
                    <a href="#">Documents</a>
                </div>
            </div>
        </div>

        <!-- Stats Row -->
        <div class="stats-row">
            <div class="stat-card" onclick="document.getElementById('filter-status').value='';loadCoils();">
                <div class="stat-label">Total Coils</div>
                <div class="stat-value" id="stat-total-coils">0</div>
            </div>
            <div class="stat-card" onclick="document.getElementById('filter-status').value='';loadCoils();">
                <div class="stat-label">Total Stock</div>
                <div class="stat-value" id="stat-total-stock">0 lbs</div>
            </div>
            <div class="stat-card" onclick="switchToTab('allocations');">
                <div class="stat-label">Committed</div>
                <div class="stat-value" id="stat-committed">0 lbs</div>
            </div>
            <div class="stat-card" onclick="document.getElementById('filter-status').value='active';loadCoils();">
                <div class="stat-label">Available</div>
                <div class="stat-value" id="stat-available">0 lbs</div>
            </div>
            <div class="stat-card" onclick="document.getElementById('filter-status').value='low_stock';loadCoils();">
                <div class="stat-label">Low Stock</div>
                <div class="stat-value" id="stat-low-stock">0</div>
            </div>
            <div class="stat-card" onclick="document.getElementById('filter-status').value='';loadCoils();">
                <div class="stat-label">Total Value</div>
                <div class="stat-value" id="stat-total-value">$0</div>
            </div>
        </div>

        <!-- Main Layout -->
        <div class="main-layout">
            <!-- Sidebar -->
            <div class="sidebar">
                <div class="sidebar-section">
                    <div class="sidebar-title">Stock by Gauge</div>
                    <div class="chart-placeholder" id="gauge-chart">Chart will load here</div>
                </div>
                <div class="sidebar-section">
                    <div class="sidebar-title">Stock by Status</div>
                    <div class="status-summary">
                        <div class="status-item" onclick="document.getElementById('filter-status').value='active';loadCoils();">
                            <span class="status-label">Available</span>
                            <span class="status-value" id="status-available">0</span>
                        </div>
                        <div class="status-item" onclick="switchToTab('allocations');">
                            <span class="status-label">Committed</span>
                            <span class="status-value" id="status-committed">0</span>
                        </div>
                        <div class="status-item" onclick="switchToTab('receiving');">
                            <span class="status-label">Pending</span>
                            <span class="status-value" id="status-pending">0</span>
                        </div>
                        <div class="status-item" onclick="document.getElementById('filter-status').value='low_stock';loadCoils();">
                            <span class="status-label">Low Stock</span>
                            <span class="status-value" id="status-low">0</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Tabs Container -->
            <div class="tabs-container">
                <div class="tabs-header">
                    <button class="tab-button active" data-tab="coils">Coils</button>
                    <button class="tab-button" data-tab="transactions">Transactions</button>
                    <button class="tab-button" data-tab="allocations">Allocations</button>
                    <button class="tab-button" data-tab="receiving">Receiving</button>
                    <button class="tab-button" data-tab="alerts">Alerts</button>
                </div>

                <!-- Coils Tab -->
                <div class="tab-content active" id="coils-tab">
                    <div class="filters">
                        <div class="filter-group">
                            <select id="filter-gauge">
                                <option value="">All Gauges</option>
                            </select>
                            <select id="filter-grade">
                                <option value="">All Grades</option>
                            </select>
                            <select id="filter-status">
                                <option value="">All Statuses</option>
                            </select>
                        </div>
                        <button class="btn btn-secondary btn-small" onclick="loadCoils()">Filter</button>
                        <button class="btn btn-primary btn-small" onclick="showNewCoilModal()">+ New Coil</button>
                    </div>
                    <table>
                        <thead>
                            <tr>
                                <th>Coil ID</th>
                                <th>Name</th>
                                <th>Gauge</th>
                                <th>Grade</th>
                                <th>Supplier</th>
                                <th>Stock (lbs)</th>
                                <th>Committed</th>
                                <th>Available</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="coils-table">
                            <tr><td colspan="10" class="empty-state">Loading...</td></tr>
                        </tbody>
                    </table>
                </div>

                <!-- Transactions Tab -->
                <div class="tab-content" id="transactions-tab">
                    <div class="filters">
                        <div class="filter-group">
                            <select id="filter-coil-trans">
                                <option value="">All Coils</option>
                            </select>
                            <select id="filter-type">
                                <option value="">All Types</option>
                                <option value="receive">Receive</option>
                                <option value="allocate">Allocate</option>
                                <option value="consume">Consume</option>
                                <option value="adjust">Adjust</option>
                            </select>
                        </div>
                        <button class="btn btn-secondary btn-small" onclick="loadTransactions()">Filter</button>
                    </div>
                    <table>
                        <thead>
                            <tr>
                                <th>Transaction ID</th>
                                <th>Coil ID</th>
                                <th>Type</th>
                                <th>Quantity (lbs)</th>
                                <th>Job Code</th>
                                <th>Reference</th>
                                <th>Notes</th>
                                <th>Date</th>
                            </tr>
                        </thead>
                        <tbody id="transactions-table">
                            <tr><td colspan="8" class="empty-state">Loading...</td></tr>
                        </tbody>
                    </table>
                </div>

                <!-- Allocations Tab -->
                <div class="tab-content" id="allocations-tab">
                    <div class="filters">
                        <button class="btn btn-primary btn-small" onclick="showAllocateModal()">+ Allocate Stock</button>
                    </div>
                    <table>
                        <thead>
                            <tr>
                                <th>Allocation ID</th>
                                <th>Coil ID</th>
                                <th>Job Code</th>
                                <th>Allocated (lbs)</th>
                                <th>Consumed (lbs)</th>
                                <th>Remaining</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="allocations-table">
                            <tr><td colspan="8" class="empty-state">Loading...</td></tr>
                        </tbody>
                    </table>
                </div>

                <!-- Receiving Tab -->
                <div class="tab-content" id="receiving-tab">
                    <div class="filters">
                        <button class="btn btn-primary btn-small" onclick="showReceiveModal()">+ Receive Stock</button>
                    </div>
                    <table>
                        <thead>
                            <tr>
                                <th>Receiving ID</th>
                                <th>Coil ID</th>
                                <th>Supplier</th>
                                <th>Quantity (lbs)</th>
                                <th>PO #</th>
                                <th>BOL #</th>
                                <th>Heat #</th>
                                <th>Date</th>
                            </tr>
                        </thead>
                        <tbody id="receiving-table">
                            <tr><td colspan="8" class="empty-state">Loading...</td></tr>
                        </tbody>
                    </table>
                </div>

                <!-- Alerts Tab -->
                <div class="tab-content" id="alerts-tab">
                    <table>
                        <thead>
                            <tr>
                                <th>Level</th>
                                <th>Type</th>
                                <th>Coil ID</th>
                                <th>Message</th>
                                <th>Date</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="alerts-table">
                            <tr><td colspan="6" class="empty-state">Loading...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <!-- New Coil Modal -->
    <div class="modal" id="newCoilModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>Create New Coil</h2>
                <button class="modal-close" onclick="closeModal('newCoilModal')">&times;</button>
            </div>
            <form id="newCoilForm">
                <div class="form-group">
                    <label>Coil ID</label>
                    <input type="text" id="coil-id" placeholder="e.g., C-001" required>
                </div>
                <div class="form-group">
                    <label>Name</label>
                    <input type="text" id="coil-name" placeholder="Coil Name" required>
                </div>
                <div class="form-group">
                    <label>Gauge</label>
                    <select id="coil-gauge" required></select>
                </div>
                <div class="form-group">
                    <label>Grade</label>
                    <select id="coil-grade" required></select>
                </div>
                <div class="form-group">
                    <label>Supplier</label>
                    <input type="text" id="coil-supplier" placeholder="Supplier Name" required>
                </div>
                <div class="form-group">
                    <label>Weight (lbs)</label>
                    <input type="number" id="coil-weight" placeholder="Total weight" min="0" step="0.01" required>
                </div>
                <div class="form-group">
                    <label>Width (inches)</label>
                    <input type="number" id="coil-width" placeholder="Width in inches" min="0" step="0.01" required>
                </div>
                <div class="form-group">
                    <label>Stock (lbs)</label>
                    <input type="number" id="coil-stock" placeholder="Stock available" min="0" step="0.01" required>
                </div>
                <div class="form-group">
                    <label>Price per Lb</label>
                    <input type="number" id="coil-price" placeholder="Price per pound" min="0" step="0.01" required>
                </div>
                <div class="form-group">
                    <label>Min Order (lbs)</label>
                    <input type="number" id="coil-min-order" placeholder="Minimum order quantity" min="0" step="0.01" required>
                </div>
                <div class="form-group">
                    <label>Lbs per Linear Foot</label>
                    <input type="number" id="coil-lbs-per-lft" placeholder="Linear feet to lbs conversion" min="0" step="0.01" required>
                </div>
                <div class="form-group">
                    <label>Heat Number</label>
                    <input type="text" id="coil-heat-num" placeholder="Heat number (optional)">
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="closeModal('newCoilModal')">Cancel</button>
                    <button type="submit" class="btn btn-primary">Create Coil</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Receive Stock Modal -->
    <div class="modal" id="receiveModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>Receive Stock</h2>
                <button class="modal-close" onclick="closeModal('receiveModal')">&times;</button>
            </div>
            <form id="receiveForm">
                <div class="form-group">
                    <label>Coil ID</label>
                    <select id="receive-coil-id" required></select>
                </div>
                <div class="form-group">
                    <label>Quantity (lbs)</label>
                    <input type="number" id="receive-quantity" placeholder="Quantity" min="0" step="0.01" required>
                </div>
                <div class="form-group">
                    <label>PO Number</label>
                    <input type="text" id="receive-po" placeholder="Purchase Order number">
                </div>
                <div class="form-group">
                    <label>BOL Number</label>
                    <input type="text" id="receive-bol" placeholder="Bill of Lading number">
                </div>
                <div class="form-group">
                    <label>Supplier</label>
                    <input type="text" id="receive-supplier" placeholder="Supplier name">
                </div>
                <div class="form-group">
                    <label>Heat Number</label>
                    <input type="text" id="receive-heat" placeholder="Heat number (optional)">
                </div>
                <div class="form-group">
                    <label>Condition Notes</label>
                    <textarea id="receive-notes" placeholder="Any notes about condition or damage"></textarea>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="closeModal('receiveModal')">Cancel</button>
                    <button type="submit" class="btn btn-primary">Receive Stock</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Allocate Stock Modal -->
    <div class="modal" id="allocateModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>Allocate Stock</h2>
                <button class="modal-close" onclick="closeModal('allocateModal')">&times;</button>
            </div>
            <form id="allocateForm">
                <div class="form-group">
                    <label>Coil ID</label>
                    <select id="allocate-coil-id" required></select>
                </div>
                <div class="form-group">
                    <label>Job Code</label>
                    <input type="text" id="allocate-job-code" placeholder="Job code" required>
                </div>
                <div class="form-group">
                    <label>Quantity (lbs)</label>
                    <input type="number" id="allocate-quantity" placeholder="Quantity to allocate" min="0" step="0.01" required>
                </div>
                <div class="form-group">
                    <label>Work Order Reference</label>
                    <input type="text" id="allocate-wo-ref" placeholder="Work order reference (optional)">
                </div>
                <div class="form-group">
                    <label>Notes</label>
                    <textarea id="allocate-notes" placeholder="Allocation notes (optional)"></textarea>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="closeModal('allocateModal')">Cancel</button>
                    <button type="submit" class="btn btn-primary">Allocate Stock</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Adjust Stock Modal -->
    <div class="modal" id="adjustModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>Adjust Stock</h2>
                <button class="modal-close" onclick="closeModal('adjustModal')">&times;</button>
            </div>
            <form id="adjustForm">
                <div class="form-group">
                    <label>Coil ID</label>
                    <select id="adjust-coil-id" required></select>
                </div>
                <div class="form-group">
                    <label>Quantity Change (lbs)</label>
                    <input type="number" id="adjust-quantity" placeholder="Positive to add, negative to remove" required>
                </div>
                <div class="form-group">
                    <label>Reason</label>
                    <select id="adjust-reason" required>
                        <option value="">Select reason</option>
                        <option value="scrap">Scrap</option>
                        <option value="waste">Waste</option>
                        <option value="damage">Damage</option>
                        <option value="correction">Correction</option>
                        <option value="other">Other</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Notes</label>
                    <textarea id="adjust-notes" placeholder="Adjustment notes (optional)"></textarea>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="closeModal('adjustModal')">Cancel</button>
                    <button type="submit" class="btn btn-primary">Adjust Stock</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Edit Coil Modal -->
    <div class="modal" id="editCoilModal">
        <div class="modal-content" style="max-width:560px">
            <div class="modal-header">
                <h2>Edit Coil</h2>
                <button class="modal-close" onclick="closeModal('editCoilModal')">&times;</button>
            </div>
            <form id="editCoilForm">
                <input type="hidden" id="edit-coil-id">
                <div class="form-group">
                    <label>Coil ID</label>
                    <input type="text" id="edit-coil-id-display" disabled style="opacity:0.6;cursor:not-allowed">
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
                    <div class="form-group">
                        <label>Name / Description</label>
                        <input type="text" id="edit-coil-name" placeholder="Coil name">
                    </div>
                    <div class="form-group">
                        <label>Supplier</label>
                        <input type="text" id="edit-coil-supplier" placeholder="Supplier">
                    </div>
                    <div class="form-group">
                        <label>Gauge</label>
                        <select id="edit-coil-gauge"></select>
                    </div>
                    <div class="form-group">
                        <label>Grade</label>
                        <select id="edit-coil-grade"></select>
                    </div>
                    <div class="form-group">
                        <label>Stock Weight (lbs)</label>
                        <input type="number" id="edit-coil-stock" min="0" step="0.01">
                    </div>
                    <div class="form-group">
                        <label>Cost per Lb ($)</label>
                        <input type="number" id="edit-coil-price" min="0" step="0.01">
                    </div>
                    <div class="form-group">
                        <label>Min Order (lbs)</label>
                        <input type="number" id="edit-coil-min-order" min="0" step="0.01">
                    </div>
                    <div class="form-group">
                        <label>Lbs per Linear Ft</label>
                        <input type="number" id="edit-coil-lbs-per-lft" min="0" step="0.01">
                    </div>
                    <div class="form-group">
                        <label>Width (inches)</label>
                        <input type="number" id="edit-coil-width" min="0" step="0.01">
                    </div>
                    <div class="form-group">
                        <label>Max Coil Weight (lbs)</label>
                        <input type="number" id="edit-coil-max-lbs" min="0" step="0.01">
                    </div>
                    <div class="form-group">
                        <label>Status</label>
                        <select id="edit-coil-status">
                            <option value="">Auto (computed)</option>
                            <option value="active">Active</option>
                            <option value="low_stock">Low Stock</option>
                            <option value="depleted">Depleted</option>
                            <option value="on_hold">On Hold</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Heat Number</label>
                        <input type="text" id="edit-coil-heat-num" placeholder="Heat number">
                    </div>
                </div>
                <div class="form-group">
                    <label>Notes</label>
                    <textarea id="edit-coil-notes" placeholder="Additional notes..." style="background-color:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:6px;font-family:'Inter',system-ui,sans-serif;font-size:13px"></textarea>
                </div>
                <div style="padding:8px 12px;background:rgba(6,182,212,0.1);border:1px solid rgba(6,182,212,0.2);border-radius:6px;font-size:12px;color:#06B6D4;margin-bottom:8px">
                    Committed stock is managed by allocations and cannot be edited here.
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="closeModal('editCoilModal')">Cancel</button>
                    <button type="submit" class="btn btn-primary">Save Changes</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div class="modal" id="deleteCoilModal">
        <div class="modal-content" style="max-width:440px">
            <div class="modal-header">
                <h2 style="color:var(--red)">Delete Coil</h2>
                <button class="modal-close" onclick="closeModal('deleteCoilModal')">&times;</button>
            </div>
            <p id="delete-confirm-msg" style="margin-bottom:16px;font-size:14px;line-height:1.6"></p>
            <div id="delete-committed-warning" style="display:none;padding:10px 14px;background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);border-radius:6px;margin-bottom:16px;font-size:13px;color:var(--red)">
                This coil has committed/allocated stock and cannot be deleted. Release all allocations first.
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" onclick="closeModal('deleteCoilModal')">Cancel</button>
                <button type="button" class="btn btn-danger" id="delete-confirm-btn" onclick="confirmDeleteCoil()">Delete Permanently</button>
            </div>
        </div>
    </div>

    <script>
        const $ = id => document.getElementById(id);
        let configData = {};
        let currentTab = 'coils';

        // Tab switching
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.addEventListener('click', e => {
                const tabName = e.target.getAttribute('data-tab');
                switchTab(tabName);
            });
        });

        function switchToTab(tabName) {
            document.querySelectorAll('.tab-button').forEach(btn => {
                btn.classList.toggle('active', btn.getAttribute('data-tab') === tabName);
            });
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            $(`${tabName}-tab`).classList.add('active');
            currentTab = tabName;
            if (tabName === 'coils') loadCoils();
            else if (tabName === 'transactions') loadTransactions();
            else if (tabName === 'allocations') loadAllocations();
            else if (tabName === 'receiving') loadReceiving();
            else if (tabName === 'alerts') loadAlerts();
        }

        function switchTab(tabName) {
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

            event.target.classList.add('active');
            $(`${tabName}-tab`).classList.add('active');
            currentTab = tabName;

            if (tabName === 'coils') loadCoils();
            else if (tabName === 'transactions') loadTransactions();
            else if (tabName === 'allocations') loadAllocations();
            else if (tabName === 'receiving') loadReceiving();
            else if (tabName === 'alerts') loadAlerts();
        }

        // Modal functions
        function showNewCoilModal() {
            $('newCoilModal').classList.add('show');
            populateSelectFromConfig('coil-gauge', 'coil_gauges', 'Gauges');
            populateSelectFromConfig('coil-grade', 'material_grades', 'Grades');
        }

        function showReceiveModal() {
            $('receiveModal').classList.add('show');
            populateCoilSelects('receive-coil-id');
        }

        function showAllocateModal() {
            $('allocateModal').classList.add('show');
            populateCoilSelects('allocate-coil-id');
        }

        function showAdjustModal() {
            $('adjustModal').classList.add('show');
            populateCoilSelects('adjust-coil-id');
        }

        function closeModal(modalId) {
            $(modalId).classList.remove('show');
        }

        window.onclick = e => {
            if (e.target.classList.contains('modal')) {
                e.target.classList.remove('show');
            }
        };

        // Form submissions
        $('newCoilForm').addEventListener('submit', e => {
            e.preventDefault();
            submitNewCoil();
        });

        $('receiveForm').addEventListener('submit', e => {
            e.preventDefault();
            submitReceiveStock();
        });

        $('allocateForm').addEventListener('submit', e => {
            e.preventDefault();
            submitAllocateStock();
        });

        $('adjustForm').addEventListener('submit', e => {
            e.preventDefault();
            submitAdjustStock();
        });

        // API functions
        async function loadConfig() {
            try {
                const response = await fetch('/api/inventory/inv-config');
                configData = await response.json();
                populateFilterSelects();
            } catch (err) {
                console.error('Failed to load config:', err);
            }
        }

        async function loadSummary() {
            try {
                const response = await fetch('/api/inventory/summary');
                if (!response.ok) { console.error('Summary API error:', response.status); return; }
                const result = await response.json();
                const data = result.summary || result;
                $('stat-total-coils').textContent = data.total_coils || 0;
                $('stat-total-stock').textContent = `${(data.total_stock_lbs || 0).toFixed(0)} lbs`;
                $('stat-committed').textContent = `${(data.total_committed_lbs || 0).toFixed(0)} lbs`;
                $('stat-available').textContent = `${(data.total_available_lbs || 0).toFixed(0)} lbs`;
                $('stat-low-stock').textContent = data.low_stock_count || 0;
                $('stat-total-value').textContent = `$${(data.total_value || 0).toFixed(2)}`;

                const byStatus = data.stock_by_status || {};
                $('status-available').textContent = byStatus.active_count || 0;
                $('status-committed').textContent = byStatus.depleted_count || 0;
                $('status-pending').textContent = 0;
                $('status-low').textContent = byStatus.low_stock_count || 0;
            } catch (err) {
                console.error('Failed to load summary:', err);
            }
        }

        async function loadCoils() {
            const gauge = $('filter-gauge').value;
            const grade = $('filter-grade').value;
            const status = $('filter-status').value;
            const url = `/api/inventory/coils?gauge=${encodeURIComponent(gauge)}&grade=${encodeURIComponent(grade)}&status=${encodeURIComponent(status)}`;

            try {
                const response = await fetch(url);
                if (!response.ok) throw new Error('API error ' + response.status);
                const result = await response.json();
                const coils = result.coils || [];
                const tbody = $('coils-table');

                if (coils.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="10" class="empty-state"><p>No coils found</p></td></tr>';
                    return;
                }

                tbody.innerHTML = coils.map(c => `
                    <tr>
                        <td>${c.coil_id}</td>
                        <td>${c.name || ''}</td>
                        <td>${c.gauge || ''}</td>
                        <td>${c.grade || ''}</td>
                        <td>${c.supplier || ''}</td>
                        <td>${(c.stock_lbs || 0).toFixed(2)}</td>
                        <td>${(c.committed_lbs || 0).toFixed(2)}</td>
                        <td>${(c.available_lbs || 0).toFixed(2)}</td>
                        <td><span class="badge badge-available">${c.status || ''}</span></td>
                        <td>
                            <button class="btn btn-small btn-secondary" onclick="showCoilHistory('${c.coil_id}')">History</button>
                            <button class="btn btn-small btn-secondary" onclick="showReceiveModal()">Receive</button>
                            <button class="btn btn-small btn-secondary" onclick="showAllocateModal()">Allocate</button>
                            <button class="btn btn-small btn-secondary" onclick="showEditCoilModal('${c.coil_id}')" style="background:#1E40AF;color:#93C5FD;border-color:#2563EB">Edit</button>
                            <button class="btn btn-small btn-danger" onclick="deleteCoil('${c.coil_id}', '${(c.name || c.coil_id).replace(/'/g, "\\\\'")}', ${c.committed_lbs || 0})" style="font-size:11px;padding:4px 8px">Delete</button>
                        </td>
                    </tr>
                `).join('');
            } catch (err) {
                console.error('Failed to load coils:', err);
                $('coils-table').innerHTML = '<tr><td colspan="10" class="empty-state"><p>Error loading coils</p></td></tr>';
            }
        }

        async function loadTransactions() {
            const coilId = $('filter-coil-trans').value;
            const type = $('filter-type').value;
            const url = `/api/inventory/transactions?coil_id=${encodeURIComponent(coilId)}&type=${encodeURIComponent(type)}`;

            try {
                const response = await fetch(url);
                if (!response.ok) throw new Error('API error ' + response.status);
                const result = await response.json();
                const transactions = result.transactions || [];
                const tbody = $('transactions-table');

                if (transactions.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="8" class="empty-state"><p>No transactions found</p></td></tr>';
                    return;
                }

                tbody.innerHTML = transactions.map(t => `
                    <tr>
                        <td>${t.transaction_id || ''}</td>
                        <td>${t.coil_id || ''}</td>
                        <td><span class="badge badge-pending">${t.type || ''}</span></td>
                        <td>${(t.quantity_lbs || t.quantity || 0).toFixed(2)}</td>
                        <td>${t.job_code || '—'}</td>
                        <td>${t.reference || '—'}</td>
                        <td>${t.notes || '—'}</td>
                        <td>${t.date || ''}</td>
                    </tr>
                `).join('');
            } catch (err) {
                console.error('Failed to load transactions:', err);
                $('transactions-table').innerHTML = '<tr><td colspan="8" class="empty-state"><p>Error loading transactions</p></td></tr>';
            }
        }

        async function loadAllocations() {
            try {
                const response = await fetch('/api/inventory/allocations');
                if (!response.ok) throw new Error('API error ' + response.status);
                const result = await response.json();
                const allocations = result.allocations || [];
                const tbody = $('allocations-table');

                if (allocations.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="8" class="empty-state"><p>No allocations found</p></td></tr>';
                    return;
                }

                tbody.innerHTML = allocations.map(a => {
                    const allocated = a.quantity_lbs || a.allocated || 0;
                    const consumed = a.consumed_lbs || a.consumed || 0;
                    const remaining = allocated - consumed;
                    return `
                    <tr>
                        <td>${a.allocation_id || ''}</td>
                        <td>${a.coil_id || ''}</td>
                        <td>${a.job_code || ''}</td>
                        <td>${allocated.toFixed(2)}</td>
                        <td>${consumed.toFixed(2)}</td>
                        <td>${remaining.toFixed(2)}</td>
                        <td><span class="badge badge-committed">${a.status || ''}</span></td>
                        <td><button class="btn btn-small btn-danger" onclick="releaseAllocation('${a.allocation_id}')">Release</button></td>
                    </tr>`;
                }).join('');
            } catch (err) {
                console.error('Failed to load allocations:', err);
                $('allocations-table').innerHTML = '<tr><td colspan="8" class="empty-state"><p>Error loading allocations</p></td></tr>';
            }
        }

        async function loadReceiving() {
            try {
                const response = await fetch('/api/inventory/receiving');
                if (!response.ok) throw new Error('API error ' + response.status);
                const result = await response.json();
                const receiving = result.receiving || [];
                const tbody = $('receiving-table');

                if (receiving.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="8" class="empty-state"><p>No receiving records found</p></td></tr>';
                    return;
                }

                tbody.innerHTML = receiving.map(r => `
                    <tr>
                        <td>${r.receiving_id || ''}</td>
                        <td>${r.coil_id || ''}</td>
                        <td>${r.supplier || ''}</td>
                        <td>${(r.quantity_lbs || r.quantity || 0).toFixed(2)}</td>
                        <td>${r.po_number || '—'}</td>
                        <td>${r.bol_number || '—'}</td>
                        <td>${r.heat_number || '—'}</td>
                        <td>${r.date || ''}</td>
                    </tr>
                `).join('');
            } catch (err) {
                console.error('Failed to load receiving:', err);
                $('receiving-table').innerHTML = '<tr><td colspan="8" class="empty-state"><p>Error loading receiving</p></td></tr>';
            }
        }

        async function loadAlerts() {
            try {
                const response = await fetch('/api/inventory/alerts?acknowledged=false');
                if (!response.ok) throw new Error('API error ' + response.status);
                const result = await response.json();
                const alerts = result.alerts || [];
                const tbody = $('alerts-table');

                if (alerts.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="6" class="empty-state"><p>No alerts</p></td></tr>';
                    return;
                }

                tbody.innerHTML = alerts.map(a => {
                    const levelColor = a.level === 'critical' ? '#EF4444' : '#F59E0B';
                    const levelBg = a.level === 'critical' ? 'rgba(239,68,68,0.15)' : 'rgba(245,158,11,0.15)';
                    const typeLabel = (a.type || 'stock').replace(/_/g, ' ').toUpperCase();
                    return `<tr style="border-left:3px solid ${levelColor}">
                        <td><span style="background:${levelBg};color:${levelColor};padding:2px 8px;border-radius:4px;font-size:0.75rem;font-weight:600">${a.level.toUpperCase()}</span></td>
                        <td><span style="color:#94A3B8;font-size:0.7rem">${typeLabel}</span></td>
                        <td>${a.coil_id}</td>
                        <td>${a.message}</td>
                        <td>${(a.date || '').slice(0,10)}</td>
                        <td>
                            <button class="btn btn-small btn-secondary" onclick="acknowledgeAlert('${a.alert_id}')" style="margin-right:4px;">Acknowledge</button>
                            <button class="btn btn-small" style="background:#d4a843;color:#0f172a;font-weight:600;padding:4px 10px;border:none;border-radius:6px;font-size:0.75rem;cursor:pointer;" onclick="createMRFromAlert('${a.coil_id}')">Create MR</button>
                        </td>
                    </tr>`;
                }).join('');
            } catch (err) {
                console.error('Failed to load alerts:', err);
                $('alerts-table').innerHTML = '<tr><td colspan="6" class="empty-state"><p>Error loading alerts</p></td></tr>';
            }
        }

        async function submitNewCoil() {
            const payload = {
                coil_id: $('coil-id').value,
                name: $('coil-name').value,
                gauge: $('coil-gauge').value,
                grade: $('coil-grade').value,
                supplier: $('coil-supplier').value,
                weight_lbs: parseFloat($('coil-weight').value),
                width_in: parseFloat($('coil-width').value),
                stock_lbs: parseFloat($('coil-stock').value),
                price_per_lb: parseFloat($('coil-price').value),
                min_order_lbs: parseFloat($('coil-min-order').value),
                lbs_per_lft: parseFloat($('coil-lbs-per-lft').value),
                heat_num: $('coil-heat-num').value || null
            };

            try {
                const response = await fetch('/api/inventory/coil/create', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (response.ok) {
                    closeModal('newCoilModal');
                    $('newCoilForm').reset();
                    loadCoils();
                    loadSummary();
                    alert('Coil created successfully');
                } else {
                    alert('Error creating coil');
                }
            } catch (err) {
                console.error('Error:', err);
                alert('Error creating coil');
            }
        }

        async function submitReceiveStock() {
            const payload = {
                coil_id: $('receive-coil-id').value,
                quantity_lbs: parseFloat($('receive-quantity').value),
                po_number: $('receive-po').value,
                bol_number: $('receive-bol').value,
                supplier: $('receive-supplier').value,
                heat_number: $('receive-heat').value || null,
                condition_notes: $('receive-notes').value
            };

            try {
                const response = await fetch('/api/inventory/receive', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (response.ok) {
                    closeModal('receiveModal');
                    $('receiveForm').reset();
                    loadCoils();
                    loadReceiving();
                    loadSummary();
                    alert('Stock received successfully');
                } else {
                    alert('Error receiving stock');
                }
            } catch (err) {
                console.error('Error:', err);
                alert('Error receiving stock');
            }
        }

        async function submitAllocateStock() {
            const payload = {
                coil_id: $('allocate-coil-id').value,
                job_code: $('allocate-job-code').value,
                quantity_lbs: parseFloat($('allocate-quantity').value),
                work_order_ref: $('allocate-wo-ref').value || null,
                notes: $('allocate-notes').value
            };

            try {
                const response = await fetch('/api/inventory/allocate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const result = await response.json();
                if (result.ok) {
                    closeModal('allocateModal');
                    $('allocateForm').reset();
                    loadCoils();
                    loadAllocations();
                    loadSummary();
                    if (result.warnings && result.warnings.length > 0) {
                        alert('Stock allocated successfully.\\n\\n⚠️ Warnings:\\n' + result.warnings.join('\\n'));
                    } else {
                        alert('Stock allocated successfully');
                    }
                } else {
                    alert('Error: ' + (result.error || 'Allocation failed'));
                }
            } catch (err) {
                console.error('Error:', err);
                alert('Error allocating stock');
            }
        }

        async function submitAdjustStock() {
            const payload = {
                coil_id: $('adjust-coil-id').value,
                quantity_change: parseFloat($('adjust-quantity').value),
                reason: $('adjust-reason').value,
                notes: $('adjust-notes').value
            };

            try {
                const response = await fetch('/api/inventory/adjust', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (response.ok) {
                    closeModal('adjustModal');
                    $('adjustForm').reset();
                    loadCoils();
                    loadSummary();
                    alert('Stock adjusted successfully');
                } else {
                    alert('Error adjusting stock');
                }
            } catch (err) {
                console.error('Error:', err);
                alert('Error adjusting stock');
            }
        }

        async function releaseAllocation(allocationId) {
            if (!confirm('Release this allocation?')) return;

            try {
                const response = await fetch('/api/inventory/allocate/release', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ allocation_id: allocationId })
                });

                if (response.ok) {
                    loadAllocations();
                    loadSummary();
                    alert('Allocation released');
                } else {
                    alert('Error releasing allocation');
                }
            } catch (err) {
                console.error('Error:', err);
                alert('Error releasing allocation');
            }
        }

        async function acknowledgeAlert(alertId) {
            try {
                const response = await fetch('/api/inventory/alerts/acknowledge', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ alert_id: alertId })
                });

                if (response.ok) {
                    loadAlerts();
                    alert('Alert acknowledged');
                } else {
                    alert('Error acknowledging alert');
                }
            } catch (err) {
                console.error('Error:', err);
                alert('Error acknowledging alert');
            }
        }

        function showCoilHistory(coilId) {
            alert(`History for coil ${coilId} would open here`);
        }

        async function createMRFromAlert(coilId) {
            try {
                const response = await fetch('/api/inventory/alerts/auto-mr', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ coil_id: coilId })
                });
                const data = await response.json();
                if (response.ok && !data.error) {
                    alert('Material Requisition created: ' + (data.mr_number || 'MR created'));
                    loadAlerts();
                } else {
                    alert('Error: ' + (data.error || 'Failed to create MR'));
                }
            } catch (err) {
                console.error('Error:', err);
                alert('Error creating material requisition');
            }
        }

        // ── Edit Coil ──────────────────────────────────────────
        async function showEditCoilModal(coilId) {
            try {
                const response = await fetch('/api/inventory');
                const inv = await response.json();
                const coil = (inv.coils || {})[coilId];
                if (!coil) { alert('Coil not found'); return; }

                $('edit-coil-id').value = coilId;
                $('edit-coil-id-display').value = coilId;
                $('edit-coil-name').value = coil.name || '';
                $('edit-coil-supplier').value = coil.supplier || '';
                $('edit-coil-stock').value = coil.stock_lbs || 0;
                $('edit-coil-price').value = coil.price_per_lb || 0;
                $('edit-coil-min-order').value = coil.min_order_lbs || coil.min_stock_lbs || 2000;
                $('edit-coil-lbs-per-lft').value = coil.lbs_per_lft || 0;
                $('edit-coil-width').value = coil.width_in || 0;
                $('edit-coil-max-lbs').value = coil.coil_max_lbs || 0;
                $('edit-coil-heat-num').value = coil.heat_num || '';
                $('edit-coil-notes').value = coil.notes || '';
                $('edit-coil-status').value = coil.status || '';

                // Populate gauge/grade selects
                populateSelectFromConfig('edit-coil-gauge', 'coil_gauges', 'Gauges');
                populateSelectFromConfig('edit-coil-grade', 'material_grades', 'Grades');

                // Set current values after populating
                setTimeout(() => {
                    $('edit-coil-gauge').value = coil.gauge || '';
                    $('edit-coil-grade').value = coil.grade || '';
                }, 50);

                $('editCoilModal').classList.add('show');
            } catch (err) {
                console.error('Failed to load coil for editing:', err);
                alert('Error loading coil data');
            }
        }

        $('editCoilForm').addEventListener('submit', async e => {
            e.preventDefault();
            const coilId = $('edit-coil-id').value;
            const payload = {
                coil_id: coilId,
                name: $('edit-coil-name').value,
                gauge: $('edit-coil-gauge').value,
                grade: $('edit-coil-grade').value,
                supplier: $('edit-coil-supplier').value,
                stock_lbs: parseFloat($('edit-coil-stock').value) || 0,
                price_per_lb: parseFloat($('edit-coil-price').value) || 0,
                min_order_lbs: parseFloat($('edit-coil-min-order').value) || 2000,
                min_stock_lbs: parseFloat($('edit-coil-min-order').value) || 2000,
                lbs_per_lft: parseFloat($('edit-coil-lbs-per-lft').value) || 0,
                width_in: parseFloat($('edit-coil-width').value) || 0,
                coil_max_lbs: parseFloat($('edit-coil-max-lbs').value) || 0,
                heat_num: $('edit-coil-heat-num').value,
                notes: $('edit-coil-notes').value,
                status: $('edit-coil-status').value || null,
            };

            try {
                const response = await fetch('/api/inventory/coil/edit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const result = await response.json();
                if (result.ok) {
                    closeModal('editCoilModal');
                    loadCoils();
                    loadSummary();
                    alert('Coil updated successfully');
                } else {
                    alert('Error: ' + (result.error || 'Update failed'));
                }
            } catch (err) {
                console.error('Error updating coil:', err);
                alert('Error updating coil');
            }
        });

        // ── Delete Coil ────────────────────────────────────────
        let pendingDeleteCoilId = null;

        function deleteCoil(coilId, coilName, committedLbs) {
            pendingDeleteCoilId = coilId;
            $('delete-confirm-msg').textContent = 'Are you sure you want to delete coil "' + coilName + '"? This cannot be undone.';

            if (committedLbs > 0) {
                $('delete-committed-warning').style.display = 'block';
                $('delete-confirm-btn').disabled = true;
                $('delete-confirm-btn').style.opacity = '0.5';
                $('delete-confirm-btn').style.cursor = 'not-allowed';
            } else {
                $('delete-committed-warning').style.display = 'none';
                $('delete-confirm-btn').disabled = false;
                $('delete-confirm-btn').style.opacity = '1';
                $('delete-confirm-btn').style.cursor = 'pointer';
            }

            $('deleteCoilModal').classList.add('show');
        }

        async function confirmDeleteCoil() {
            if (!pendingDeleteCoilId) return;

            try {
                const response = await fetch('/api/inventory/delete', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ coil_id: pendingDeleteCoilId })
                });
                const result = await response.json();
                if (result.ok) {
                    closeModal('deleteCoilModal');
                    pendingDeleteCoilId = null;
                    loadCoils();
                    loadSummary();
                    alert('Coil deleted successfully');
                } else {
                    alert('Error: ' + (result.error || 'Delete failed'));
                }
            } catch (err) {
                console.error('Error deleting coil:', err);
                alert('Error deleting coil');
            }
        }

        // Helper functions
        function populateFilterSelects() {
            populateSelectFromConfig('filter-gauge', 'coil_gauges', 'Gauges');
            populateSelectFromConfig('filter-grade', 'material_grades', 'Grades');
            populateSelectFromConfig('filter-status', 'inventory_statuses', 'Statuses');
            populateCoilSelects('filter-coil-trans');
        }

        function populateSelectFromConfig(selectId, configKey, displayLabel) {
            const select = $(selectId);
            if (!select) return;

            const items = configData[configKey] || [];
            const currentValue = select.value;
            const label = displayLabel || configKey.charAt(0).toUpperCase() + configKey.slice(1);

            const options = ['<option value="">All ' + label + '</option>'];
            items.forEach(item => {
                options.push(`<option value="${item}">${item}</option>`);
            });

            select.innerHTML = options.join('');
            if (currentValue) select.value = currentValue;
        }

        async function populateCoilSelects(selectId) {
            const select = $(selectId);
            if (!select) return;

            try {
                const response = await fetch('/api/inventory/coils');
                const result = await response.json();
                const coils = result.coils || [];

                const options = ['<option value="">Select Coil</option>'];
                coils.forEach(c => {
                    options.push(`<option value="${c.coil_id}">${c.coil_id} - ${c.name}</option>`);
                });

                select.innerHTML = options.join('');
            } catch (err) {
                console.error('Failed to load coils for select:', err);
            }
        }

        // Initialize on page load
        document.addEventListener('DOMContentLoaded', () => {
            loadConfig();
            loadSummary();
            loadCoils();
        });
    </script>
</body>
</html>
'''
