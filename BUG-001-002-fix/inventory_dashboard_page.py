"""
TitanForge Inventory Dashboard Page Template
Provides the complete HTML interface for inventory management including coils,
receiving, purchase orders, transactions, and alerts.
"""

from templates.shared_styles import DESIGN_SYSTEM_CSS

INVENTORY_DASHBOARD_PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inventory Management - TitanForge</title>
    <style>
        {DESIGN_SYSTEM_CSS}

        /* Page Layout */
        .inventory-page {{
            display: flex;
            flex-direction: column;
            height: 100vh;
            background-color: var(--tf-bg);
        }}

        .inventory-header {{
            padding: 24px;
            background-color: var(--tf-navy);
            border-bottom: 1px solid var(--tf-border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .inventory-header h1 {{
            color: white;
            margin: 0;
            font-size: 24px;
            font-weight: 600;
        }}

        .header-actions {{
            display: flex;
            gap: 12px;
            align-items: center;
        }}

        .notification-badge {{
            position: relative;
            width: 36px;
            height: 36px;
            background-color: var(--tf-blue-mid);
            border: none;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 18px;
        }}

        .notification-badge.has-alerts::after {{
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 10px;
            height: 10px;
            background-color: var(--tf-amber);
            border-radius: 50%;
            border: 2px solid var(--tf-navy);
        }}

        .btn-primary {{
            background-color: var(--tf-blue);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            transition: background-color 0.2s;
        }}

        .btn-primary:hover {{
            background-color: var(--tf-blue-mid);
        }}

        /* Tab Navigation */
        .tab-navigation {{
            display: flex;
            gap: 0;
            border-bottom: 1px solid var(--tf-border);
            background-color: var(--tf-navy);
            padding-left: 24px;
        }}

        .tab-button {{
            padding: 16px 20px;
            background: none;
            border: none;
            color: rgba(255, 255, 255, 0.6);
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            border-bottom: 3px solid transparent;
            transition: all 0.2s;
        }}

        .tab-button.active {{
            color: white;
            border-bottom-color: var(--tf-blue);
        }}

        .tab-button:hover {{
            color: white;
        }}

        /* Tab Content */
        .tab-content {{
            flex: 1;
            overflow-y: auto;
            padding: 24px;
            display: none;
        }}

        .tab-content.active {{
            display: block;
        }}

        /* Metrics Row */
        .metrics-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}

        .metric-card {{
            background-color: var(--tf-slate);
            padding: 20px;
            border-radius: 8px;
            border: 1px solid var(--tf-border);
        }}

        .metric-card h3 {{
            color: rgba(255, 255, 255, 0.7);
            font-size: 12px;
            font-weight: 500;
            text-transform: uppercase;
            margin: 0 0 8px 0;
            letter-spacing: 0.5px;
        }}

        .metric-card .value {{
            color: white;
            font-size: 28px;
            font-weight: 700;
            margin: 0;
        }}

        /* Tables */
        .items-table {{
            width: 100%;
            border-collapse: collapse;
            background-color: var(--tf-slate);
            border: 1px solid var(--tf-border);
            border-radius: 8px;
            overflow: hidden;
        }}

        .items-table thead {{
            background-color: rgba(0, 0, 0, 0.3);
        }}

        .items-table th {{
            padding: 16px;
            text-align: left;
            color: rgba(255, 255, 255, 0.8);
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 1px solid var(--tf-border);
        }}

        .items-table td {{
            padding: 16px;
            color: rgba(255, 255, 255, 0.9);
            border-bottom: 1px solid var(--tf-border);
        }}

        .items-table tbody tr:hover {{
            background-color: rgba(255, 255, 255, 0.05);
        }}

        /* Status Badge */
        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }}

        .status-badge.active {{
            background-color: rgba(34, 197, 94, 0.2);
            color: #22c55e;
        }}

        .status-badge.low_stock {{
            background-color: rgba(251, 146, 60, 0.2);
            color: #fb923c;
        }}

        .status-badge.depleted {{
            background-color: rgba(239, 68, 68, 0.2);
            color: #ef4444;
        }}

        .status-badge.on_order {{
            background-color: rgba(59, 130, 246, 0.2);
            color: #3b82f6;
        }}

        /* Action Buttons */
        .action-buttons {{
            display: flex;
            gap: 8px;
        }}

        .btn-small {{
            padding: 6px 12px;
            font-size: 12px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: 500;
            transition: background-color 0.2s;
        }}

        .btn-view {{
            background-color: var(--tf-blue-mid);
            color: white;
        }}

        .btn-view:hover {{
            background-color: var(--tf-blue);
        }}

        .btn-edit {{
            background-color: var(--tf-blue-mid);
            color: white;
        }}

        .btn-edit:hover {{
            background-color: var(--tf-blue);
        }}

        .btn-danger {{
            background-color: rgba(239, 68, 68, 0.2);
            color: #ef4444;
        }}

        .btn-danger:hover {{
            background-color: rgba(239, 68, 68, 0.3);
        }}

        /* Modal */
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.7);
        }}

        .modal.show {{
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .modal-content {{
            background-color: var(--tf-slate);
            padding: 32px;
            border-radius: 12px;
            width: 90%;
            max-width: 600px;
            max-height: 90vh;
            overflow-y: auto;
            border: 1px solid var(--tf-border);
        }}

        .modal-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
        }}

        .modal-header h2 {{
            margin: 0;
            color: white;
            font-size: 20px;
        }}

        .modal-close {{
            background: none;
            border: none;
            color: rgba(255, 255, 255, 0.6);
            font-size: 24px;
            cursor: pointer;
        }}

        .modal-close:hover {{
            color: white;
        }}

        /* Form */
        .form-group {{
            margin-bottom: 20px;
        }}

        .form-group label {{
            display: block;
            margin-bottom: 8px;
            color: rgba(255, 255, 255, 0.9);
            font-size: 14px;
            font-weight: 500;
        }}

        .form-group input,
        .form-group select,
        .form-group textarea {{
            width: 100%;
            padding: 10px;
            border: 1px solid var(--tf-border);
            border-radius: 6px;
            background-color: rgba(0, 0, 0, 0.3);
            color: white;
            font-size: 14px;
            font-family: inherit;
        }}

        .form-group input::placeholder {{
            color: rgba(255, 255, 255, 0.4);
        }}

        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {{
            outline: none;
            border-color: var(--tf-blue);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }}

        /* Form Row */
        .form-row {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
        }}

        .form-row .form-group {{
            margin-bottom: 0;
        }}

        /* Modal Footer */
        .modal-footer {{
            display: flex;
            gap: 12px;
            justify-content: flex-end;
            margin-top: 24px;
            padding-top: 20px;
            border-top: 1px solid var(--tf-border);
        }}

        .btn-secondary {{
            background-color: rgba(255, 255, 255, 0.1);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            transition: background-color 0.2s;
        }}

        .btn-secondary:hover {{
            background-color: rgba(255, 255, 255, 0.15);
        }}

        /* Toast */
        .toast {{
            position: fixed;
            bottom: 24px;
            right: 24px;
            padding: 16px 20px;
            border-radius: 8px;
            color: white;
            font-size: 14px;
            max-width: 400px;
            z-index: 2000;
            animation: slideIn 0.3s ease-out;
        }}

        .toast.success {{
            background-color: #22c55e;
        }}

        .toast.error {{
            background-color: #ef4444;
        }}

        .toast.info {{
            background-color: var(--tf-blue);
        }}

        @keyframes slideIn {{
            from {{
                transform: translateX(400px);
                opacity: 0;
            }}
            to {{
                transform: translateX(0);
                opacity: 1;
            }}
        }}

        /* Empty State */
        .empty-state {{
            text-align: center;
            padding: 48px 24px;
            color: rgba(255, 255, 255, 0.6);
        }}

        .empty-state h3 {{
            font-size: 18px;
            margin: 0 0 12px 0;
        }}

        .empty-state p {{
            margin: 0;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="inventory-page">
        <!-- Header -->
        <div class="inventory-header">
            <h1>Inventory Management</h1>
            <div class="header-actions">
                <button class="notification-badge" id="notificationBtn" onclick="alert('Notifications')">🔔</button>
                <button class="btn-primary" onclick="showNewCoilModal()">+ New Coil</button>
            </div>
        </div>

        <!-- Tab Navigation -->
        <div class="tab-navigation">
            <button class="tab-button active" onclick="switchTab('coils')">Coils</button>
            <button class="tab-button" onclick="switchTab('receiving')">Receiving</button>
            <button class="tab-button" onclick="switchTab('purchase-orders')">Purchase Orders</button>
            <button class="tab-button" onclick="switchTab('transactions')">Transactions</button>
            <button class="tab-button" onclick="switchTab('alerts')">Alerts</button>
        </div>

        <!-- Coils Tab -->
        <div id="coils" class="tab-content active">
            <div class="metrics-row">
                <div class="metric-card">
                    <h3>Total Coils</h3>
                    <p class="value" id="totalCoils">0</p>
                </div>
                <div class="metric-card">
                    <h3>Total Stock (lbs)</h3>
                    <p class="value" id="totalStock">0</p>
                </div>
                <div class="metric-card">
                    <h3>Low Stock Alerts</h3>
                    <p class="value" id="lowStockCount">0</p>
                </div>
                <div class="metric-card">
                    <h3>Total Value ($)</h3>
                    <p class="value" id="totalValue">$0</p>
                </div>
            </div>

            <table class="items-table">
                <thead>
                    <tr>
                        <th>Coil ID</th>
                        <th>Name</th>
                        <th>Gauge</th>
                        <th>Grade</th>
                        <th>Supplier</th>
                        <th>Stock (lbs)</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="coilsTableBody">
                    <tr>
                        <td colspan="8" style="text-align: center;">Loading coils...</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Receiving Tab -->
        <div id="receiving" class="tab-content">
            <h2 style="color: white; margin-top: 0;">Quick Receive</h2>
            <div style="background-color: var(--tf-slate); padding: 24px; border-radius: 8px; margin-bottom: 24px; border: 1px solid var(--tf-border);">
                <div class="form-row">
                    <div class="form-group">
                        <label>Coil Type</label>
                        <select id="receiveCoilType">
                            <option value="">Select coil...</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Weight (lbs)</label>
                        <input type="number" id="receiveWeight" placeholder="0" step="0.01">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Supplier</label>
                        <input type="text" id="receiveSupplier" placeholder="Supplier name">
                    </div>
                    <div class="form-group">
                        <label>Heat #</label>
                        <input type="text" id="receiveHeatNum" placeholder="Heat number">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>PO # (Optional)</label>
                        <input type="text" id="receivePONum" placeholder="PO number">
                    </div>
                    <div class="form-group">
                        <label>BOL #</label>
                        <input type="text" id="receiveBOL" placeholder="BOL number">
                    </div>
                </div>
                <button class="btn-primary" onclick="submitReceive()" style="width: 100%; margin-top: 12px;">Submit Receive</button>
            </div>

            <h2 style="color: white;">Recent Receiving History</h2>
            <table class="items-table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Coil ID</th>
                        <th>Weight (lbs)</th>
                        <th>Supplier</th>
                        <th>Heat #</th>
                        <th>User</th>
                    </tr>
                </thead>
                <tbody id="receivingTableBody">
                    <tr>
                        <td colspan="6" style="text-align: center;">No receiving history</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Purchase Orders Tab -->
        <div id="purchase-orders" class="tab-content">
            <button class="btn-primary" onclick="showCreatePO()" style="margin-bottom: 24px;">+ Create PO</button>

            <table class="items-table">
                <thead>
                    <tr>
                        <th>PO ID</th>
                        <th>Supplier</th>
                        <th>Items</th>
                        <th>Total (lbs)</th>
                        <th>Received (lbs)</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="poTableBody">
                    <tr>
                        <td colspan="7" style="text-align: center;">No purchase orders</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Transactions Tab -->
        <div id="transactions" class="tab-content">
            <div style="margin-bottom: 24px; display: flex; gap: 12px;">
                <input type="text" id="filterCoil" placeholder="Filter by coil..." style="padding: 10px; border: 1px solid var(--tf-border); border-radius: 6px; background-color: var(--tf-slate); color: white; width: 200px;">
                <select id="filterType" style="padding: 10px; border: 1px solid var(--tf-border); border-radius: 6px; background-color: var(--tf-slate); color: white; width: 150px;">
                    <option value="">All Types</option>
                    <option value="receive">Receive</option>
                    <option value="use">Use</option>
                    <option value="adjust">Adjust</option>
                </select>
            </div>

            <table class="items-table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Type</th>
                        <th>Coil</th>
                        <th>Qty (lbs)</th>
                        <th>Job</th>
                        <th>Reference</th>
                        <th>User</th>
                        <th>Balance After</th>
                    </tr>
                </thead>
                <tbody id="transactionsTableBody">
                    <tr>
                        <td colspan="8" style="text-align: center;">No transactions</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Alerts Tab -->
        <div id="alerts" class="tab-content">
            <div id="alertsContainer"></div>
        </div>
    </div>

    <!-- New Coil Modal -->
    <div id="newCoilModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>Add New Coil</h2>
                <button class="modal-close" onclick="closeNewCoilModal()">&times;</button>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label>Coil ID</label>
                    <input type="text" id="coilId" placeholder="e.g., C-001">
                </div>
                <div class="form-group">
                    <label>Name</label>
                    <input type="text" id="coilName" placeholder="Coil name">
                </div>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label>Gauge</label>
                    <select id="coilGauge">
                        <option value="">Select gauge...</option>
                        <option value="10">10</option>
                        <option value="12">12</option>
                        <option value="14">14</option>
                        <option value="16">16</option>
                        <option value="18">18</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Grade</label>
                    <select id="coilGrade">
                        <option value="">Select grade...</option>
                        <option value="A">A</option>
                        <option value="B">B</option>
                        <option value="C">C</option>
                    </select>
                </div>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label>Supplier</label>
                    <input type="text" id="coilSupplier" placeholder="Supplier name">
                </div>
                <div class="form-group">
                    <label>Weight (lbs)</label>
                    <input type="number" id="coilWeight" placeholder="0" step="0.01">
                </div>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label>Width (in)</label>
                    <input type="number" id="coilWidth" placeholder="0" step="0.01">
                </div>
                <div class="form-group">
                    <label>Price/lb</label>
                    <input type="number" id="coilPrice" placeholder="0.00" step="0.01">
                </div>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label>Min Stock (lbs)</label>
                    <input type="number" id="coilMinStock" placeholder="0" step="0.01">
                </div>
                <div class="form-group">
                    <label>Lead Time (weeks)</label>
                    <input type="number" id="coilLeadTime" placeholder="0" step="1">
                </div>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label>Heat #</label>
                    <input type="text" id="coilHeatNum" placeholder="Heat number">
                </div>
                <div class="form-group">
                    <label>Location</label>
                    <input type="text" id="coilLocation" placeholder="Storage location">
                </div>
            </div>

            <div class="modal-footer">
                <button class="btn-secondary" onclick="closeNewCoilModal()">Cancel</button>
                <button class="btn-primary" onclick="saveNewCoil()">Save Coil</button>
            </div>
        </div>
    </div>

    <script>
        // ===== STATE =====
        let coils = [];
        let transactions = [];
        let alerts = [];
        let purchaseOrders = [];
        let receivingHistory = [];

        // ===== API HELPER =====
        async function apiCall(url, method = 'GET', body = null) {
            const options = {{ method, headers: {{ 'Content-Type': 'application/json' }} }};
            if (body) options.body = JSON.stringify(body);
            try {{
                const response = await fetch(url, options);
                return await response.json();
            }} catch (e) {{
                console.error('API Error:', e);
                showToast('API error: ' + e.message, 'error');
                return null;
            }}
        }}

        // ===== COILS =====
        async function loadCoils() {{
            const data = await apiCall('/api/inventory/coils');
            if (data) {{
                coils = data.coils || [];
                renderCoilsTable();
            }}
        }}

        async function loadSummary() {{
            const data = await apiCall('/api/inventory/summary');
            if (data) {{
                document.getElementById('totalCoils').textContent = data.total_coils || 0;
                document.getElementById('totalStock').textContent = (data.total_stock || 0).toFixed(2);
                document.getElementById('lowStockCount').textContent = data.low_stock_count || 0;
                document.getElementById('totalValue').textContent = '$' + (data.total_value || 0).toFixed(2);
            }}
        }}

        function renderCoilsTable() {{
            const tbody = document.getElementById('coilsTableBody');
            if (coils.length === 0) {{
                tbody.innerHTML = '<tr><td colspan="8" style="text-align: center;">No coils found</td></tr>';
                return;
            }}

            tbody.innerHTML = coils.map(coil => `
                <tr>
                    <td>${{coil.coil_id || '-'}}</td>
                    <td>${{coil.name || '-'}}</td>
                    <td>${{coil.gauge || '-'}}</td>
                    <td>${{coil.grade || '-'}}</td>
                    <td>${{coil.supplier || '-'}}</td>
                    <td>${{(coil.stock || 0).toFixed(2)}}</td>
                    <td><span class="status-badge ${{coil.status}}">${{coil.status || 'unknown'}}</span></td>
                    <td>
                        <div class="action-buttons">
                            <button class="btn-small btn-view" onclick="alert('View coil ${{coil.coil_id}}')">View</button>
                            <button class="btn-small btn-edit" onclick="alert('Edit coil ${{coil.coil_id}}')">Edit</button>
                            <button class="btn-small btn-view" onclick="printCoilLabel('${{coil.coil_id}}')">Label</button>
                        </div>
                    </td>
                </tr>
            `).join('');
        }}

        function showNewCoilModal() {{
            document.getElementById('newCoilModal').classList.add('show');
        }}

        function closeNewCoilModal() {{
            document.getElementById('newCoilModal').classList.remove('show');
            document.getElementById('coilId').value = '';
            document.getElementById('coilName').value = '';
            document.getElementById('coilGauge').value = '';
            document.getElementById('coilGrade').value = '';
            document.getElementById('coilSupplier').value = '';
            document.getElementById('coilWeight').value = '';
            document.getElementById('coilWidth').value = '';
            document.getElementById('coilPrice').value = '';
            document.getElementById('coilMinStock').value = '';
            document.getElementById('coilLeadTime').value = '';
            document.getElementById('coilHeatNum').value = '';
            document.getElementById('coilLocation').value = '';
        }}

        async function saveNewCoil() {{
            const payload = {{
                coil_id: document.getElementById('coilId').value,
                name: document.getElementById('coilName').value,
                gauge: document.getElementById('coilGauge').value,
                grade: document.getElementById('coilGrade').value,
                supplier: document.getElementById('coilSupplier').value,
                weight: parseFloat(document.getElementById('coilWeight').value) || 0,
                width: parseFloat(document.getElementById('coilWidth').value) || 0,
                price_per_lb: parseFloat(document.getElementById('coilPrice').value) || 0,
                min_stock: parseFloat(document.getElementById('coilMinStock').value) || 0,
                lead_time: parseInt(document.getElementById('coilLeadTime').value) || 0,
                heat_num: document.getElementById('coilHeatNum').value,
                location: document.getElementById('coilLocation').value
            }};

            const result = await apiCall('/api/inventory/coil/create', 'POST', payload);
            if (result && result.success) {{
                showToast('Coil created successfully', 'success');
                closeNewCoilModal();
                loadCoils();
                loadSummary();
            }} else {{
                showToast('Failed to create coil', 'error');
            }}
        }}

        function printCoilLabel(coilId) {{
            window.open(`/api/inventory/sticker?coil_id=${{coilId}}&format=zpl`, '_blank');
        }}

        // ===== RECEIVING =====
        async function loadReceiving() {{
            const data = await apiCall('/api/inventory/receiving');
            if (data) {{
                receivingHistory = data.history || [];
                const tbody = document.getElementById('receivingTableBody');
                if (receivingHistory.length === 0) {{
                    tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">No receiving history</td></tr>';
                }} else {{
                    tbody.innerHTML = receivingHistory.map(r => `
                        <tr>
                            <td>${{r.date || '-'}}</td>
                            <td>${{r.coil_id || '-'}}</td>
                            <td>${{(r.weight || 0).toFixed(2)}}</td>
                            <td>${{r.supplier || '-'}}</td>
                            <td>${{r.heat_num || '-'}}</td>
                            <td>${{{r.user || '-'}}</td>
                        </tr>
                    `).join('');
                }}
            }}
        }}

        async function submitReceive() {{
            const payload = {{
                coil_type: document.getElementById('receiveCoilType').value,
                weight: parseFloat(document.getElementById('receiveWeight').value) || 0,
                supplier: document.getElementById('receiveSupplier').value,
                heat_num: document.getElementById('receiveHeatNum').value,
                po_num: document.getElementById('receivePONum').value,
                bol: document.getElementById('receiveBOL').value
            }};

            const result = await apiCall('/api/inventory/receive', 'POST', payload);
            if (result && result.success) {{
                showToast('Receive recorded successfully', 'success');
                document.getElementById('receiveCoilType').value = '';
                document.getElementById('receiveWeight').value = '';
                document.getElementById('receiveSupplier').value = '';
                document.getElementById('receiveHeatNum').value = '';
                document.getElementById('receivePONum').value = '';
                document.getElementById('receiveBOL').value = '';
                loadReceiving();
                loadSummary();
            }} else {{
                showToast('Failed to record receive', 'error');
            }}
        }}

        // ===== PURCHASE ORDERS =====
        async function loadPOs() {{
            const data = await apiCall('/api/inventory/purchase-orders');
            if (data) {{
                purchaseOrders = data.orders || [];
                const tbody = document.getElementById('poTableBody');
                if (purchaseOrders.length === 0) {{
                    tbody.innerHTML = '<tr><td colspan="7" style="text-align: center;">No purchase orders</td></tr>';
                }} else {{
                    tbody.innerHTML = purchaseOrders.map(po => `
                        <tr>
                            <td>${{po.po_id || '-'}}</td>
                            <td>${{po.supplier || '-'}}</td>
                            <td>${{po.items || 0}}</td>
                            <td>${{{(po.total_lbs || 0).toFixed(2)}}}</td>
                            <td>${{{(po.received_lbs || 0).toFixed(2)}}}</td>
                            <td><span class="status-badge ${{po.status}}">${{{po.status || 'unknown'}}}</span></td>
                            <td>
                                <button class="btn-small btn-view" onclick="receiveAgainstPO('${{po.po_id}}')">Receive</button>
                            </td>
                        </tr>
                    `).join('');
                }}
            }}
        }}

        async function receiveAgainstPO(poId) {{
            const weight = prompt('Enter weight received (lbs):');
            if (!weight) return;
            const result = await apiCall(`/api/inventory/receive-against-po`, 'POST', {{ po_id: poId, weight: parseFloat(weight) }});
            if (result && result.success) {{
                showToast('Received against PO successfully', 'success');
                loadPOs();
                loadSummary();
            }}
        }}

        // ===== TRANSACTIONS =====
        async function loadTransactions() {{
            const data = await apiCall('/api/inventory/transactions');
            if (data) {{
                transactions = data.transactions || [];
                renderTransactions();
            }}
        }}

        function renderTransactions() {{
            const tbody = document.getElementById('transactionsTableBody');
            if (transactions.length === 0) {{
                tbody.innerHTML = '<tr><td colspan="8" style="text-align: center;">No transactions</td></tr>';
                return;
            }}
            tbody.innerHTML = transactions.map(t => `
                <tr>
                    <td>${{t.date || '-'}}</td>
                    <td>${{{t.type || '-'}}}</td>
                    <td>${{{t.coil || '-'}}}</td>
                    <td>${{{(t.qty || 0).toFixed(2)}}}</td>
                    <td>${{{t.job || '-'}}}</td>
                    <td>${{{t.reference || '-'}}}</td>
                    <td>${{{t.user || '-'}}}</td>
                    <td>${{{(t.balance_after || 0).toFixed(2)}}}</td>
                </tr>
            `).join('');
        }}

        // ===== ALERTS =====
        async function loadAlerts() {{
            const data = await apiCall('/api/inventory/alerts');
            if (data) {{
                alerts = data.alerts || [];
                renderAlerts();
            }}
        }}

        function renderAlerts() {{
            const container = document.getElementById('alertsContainer');
            if (alerts.length === 0) {{
                container.innerHTML = '<div class="empty-state"><h3>No Active Alerts</h3><p>All clear!</p></div>';
                document.getElementById('notificationBtn').classList.remove('has-alerts');
                return;
            }}

            document.getElementById('notificationBtn').classList.add('has-alerts');
            container.innerHTML = alerts.map(alert => `
                <div style="background-color: var(--tf-slate); padding: 16px; border-radius: 8px; margin-bottom: 12px; border-left: 4px solid ${{alert.type === 'low_stock' ? '#fb923c' : alert.type === 'depleted' ? '#ef4444' : '#3b82f6'}};">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <span class="status-badge ${{alert.type}}">${{{alert.type.replace(/_/g, ' ')}}}</span>
                            <p style="color: rgba(255, 255, 255, 0.9); margin: 12px 0 0 0;">${{{alert.message}}}</p>
                        </div>
                        <button class="btn-small btn-view" onclick="acknowledgeAlert('${{alert.alert_id}}')">Acknowledge</button>
                    </div>
                </div>
            `).join('');
        }}

        async function acknowledgeAlert(alertId) {{
            const result = await apiCall('/api/inventory/alerts/acknowledge', 'POST', {{ alert_id: alertId }});
            if (result && result.success) {{
                loadAlerts();
            }}
        }}

        // ===== TAB SWITCHING =====
        function switchTab(tab) {{
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));

            const tabEl = document.getElementById(tab);
            if (tabEl) tabEl.classList.add('active');
            event.target.classList.add('active');

            if (tab === 'receiving') loadReceiving();
            else if (tab === 'purchase-orders') loadPOs();
            else if (tab === 'transactions') loadTransactions();
            else if (tab === 'alerts') loadAlerts();
        }}

        // ===== TOAST =====
        function showToast(msg, type = 'info') {{
            const toast = document.createElement('div');
            toast.className = `toast ${{type}}`;
            toast.textContent = msg;
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 3000);
        }}

        // ===== INITIALIZATION =====
        document.addEventListener('DOMContentLoaded', () => {{
            loadCoils();
            loadSummary();
            loadAlerts();
        }});

        // Close modal on background click
        document.getElementById('newCoilModal').addEventListener('click', (e) => {{
            if (e.target.id === 'newCoilModal') closeNewCoilModal();
        }});
    </script>
</body>
</html>
""".format(DESIGN_SYSTEM_CSS=DESIGN_SYSTEM_CSS)
