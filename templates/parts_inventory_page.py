"""
TitanForge v4 -- Parts Inventory
==================================
Comprehensive inventory page for tracking fabricated parts, fasteners, rebar,
and custom items. Category tabs, stock tracking, fabrication from coil,
quick PO creation, and full CRUD with adjustment history.
"""

PARTS_INVENTORY_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a;
        --tf-card: #1e293b;
        --tf-border: #334155;
        --tf-text: #f1f5f9;
        --tf-muted: #94a3b8;
        --tf-blue: #3b82f6;
        --tf-green: #22c55e;
        --tf-yellow: #eab308;
        --tf-red: #ef4444;
        --tf-gold: #d4a843;
    }

    .pi-container {
        max-width: 1500px; margin: 0 auto; padding: 24px 32px;
        font-family: 'Inter', system-ui, -apple-system, sans-serif; color: var(--tf-text);
    }

    /* Page Header */
    .page-header { margin-bottom: 24px; }
    .page-header h1 { font-size: 28px; font-weight: 800; margin: 0 0 6px 0; }
    .page-header p { font-size: 14px; color: var(--tf-muted); margin: 0; }
    .breadcrumb { font-size: 13px; color: var(--tf-muted); margin-bottom: 4px; }
    .breadcrumb a { color: var(--tf-blue); text-decoration: none; }
    .breadcrumb a:hover { text-decoration: underline; }

    /* Category Tabs */
    .cat-tabs {
        display: flex; gap: 4px; margin-bottom: 24px; flex-wrap: wrap;
        border-bottom: 2px solid var(--tf-border); padding-bottom: 0;
    }
    .cat-tab {
        padding: 10px 20px; font-size: 14px; font-weight: 600; cursor: pointer;
        border: none; background: transparent; color: var(--tf-muted);
        border-bottom: 3px solid transparent; margin-bottom: -2px;
        transition: all 0.2s; border-radius: 8px 8px 0 0;
    }
    .cat-tab:hover { color: var(--tf-text); background: rgba(255,255,255,0.03); }
    .cat-tab.active {
        color: var(--tf-blue); border-bottom-color: var(--tf-blue);
        background: rgba(59,130,246,0.06);
    }
    .cat-tab .tab-count {
        display: inline-block; margin-left: 6px; padding: 1px 7px;
        border-radius: 10px; font-size: 11px; font-weight: 700;
        background: rgba(255,255,255,0.06); color: var(--tf-muted);
    }
    .cat-tab.active .tab-count { background: rgba(59,130,246,0.15); color: var(--tf-blue); }

    /* Stats Row */
    .stat-row {
        display: grid; grid-template-columns: repeat(4, 1fr);
        gap: 16px; margin-bottom: 24px;
    }
    .stat-card {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06);
        padding: 20px 24px; transition: border-color 0.2s, transform 0.15s;
    }
    .stat-card:hover { border-color: var(--tf-gold); transform: translateY(-2px); }
    .stat-card .label {
        font-size: 12px; color: var(--tf-muted); text-transform: uppercase;
        letter-spacing: 0.5px; margin-bottom: 8px;
    }
    .stat-card .value { font-size: 28px; font-weight: 800; }
    .stat-card .sub { font-size: 12px; color: var(--tf-muted); margin-top: 4px; }
    .stat-blue .value { color: var(--tf-blue); }
    .stat-yellow .value { color: var(--tf-yellow); }
    .stat-green .value { color: var(--tf-green); }
    .stat-gold .value { color: var(--tf-gold); }

    /* Main Layout */
    .pi-layout {
        display: grid; grid-template-columns: 1fr 340px; gap: 24px;
    }
    .pi-main { min-width: 0; }
    .pi-sidebar { display: flex; flex-direction: column; gap: 16px; }

    /* Toolbar */
    .toolbar {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 20px; flex-wrap: wrap; gap: 12px;
    }
    .toolbar-left { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
    .toolbar-right { display: flex; gap: 10px; align-items: center; }
    .toolbar input[type="text"], .toolbar select {
        background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06);
        border-radius: 8px; padding: 10px 16px; color: var(--tf-text); font-size: 14px;
        min-width: 0;
    }
    .toolbar input:focus, .toolbar select:focus { outline: none; border-color: var(--tf-blue); }
    .search-input { width: 260px; }

    /* Buttons */
    .btn {
        padding: 10px 20px; border: none; border-radius: 8px; font-size: 14px;
        font-weight: 600; cursor: pointer; transition: all 0.2s;
        display: inline-flex; align-items: center; gap: 6px;
    }
    .btn-primary { background: var(--tf-blue); color: #fff; }
    .btn-primary:hover { background: #2563eb; transform: translateY(-1px); }
    .btn-success { background: var(--tf-green); color: #fff; }
    .btn-success:hover { background: #16a34a; transform: translateY(-1px); }
    .btn-secondary { background: var(--tf-card); color: var(--tf-text); border: 1px solid rgba(255,255,255,0.06); }
    .btn-secondary:hover { border-color: var(--tf-blue); }
    .btn-danger { background: var(--tf-red); color: #fff; }
    .btn-danger:hover { background: #dc2626; }
    .btn-gold { background: var(--tf-gold); color: #0f172a; }
    .btn-gold:hover { background: #e0b44e; }
    .btn-sm { padding: 6px 14px; font-size: 12px; }
    .btn-xs { padding: 4px 10px; font-size: 11px; }
    .btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }

    /* Items Table */
    .items-table-wrap {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06); overflow: hidden;
    }
    .items-table {
        width: 100%; border-collapse: collapse; font-size: 13px;
    }
    .items-table thead th {
        padding: 12px 14px; text-align: left; font-size: 11px;
        text-transform: uppercase; letter-spacing: 0.5px;
        color: var(--tf-muted); background: rgba(0,0,0,0.2);
        border-bottom: 1px solid var(--tf-border); cursor: pointer;
        white-space: nowrap; user-select: none;
    }
    .items-table thead th:hover { color: var(--tf-text); }
    .items-table thead th .sort-icon { margin-left: 4px; font-size: 10px; }
    .items-table tbody tr {
        border-bottom: 1px solid rgba(255,255,255,0.04);
        cursor: pointer; transition: background 0.15s;
    }
    .items-table tbody tr:hover { background: rgba(59,130,246,0.04); }
    .items-table tbody td { padding: 12px 14px; white-space: nowrap; }
    .items-table tbody td.name-cell { white-space: normal; max-width: 200px; }

    /* Expanded detail row */
    .detail-row td { padding: 0 !important; }
    .detail-row .detail-content {
        padding: 16px 20px; background: rgba(0,0,0,0.15);
        border-bottom: 1px solid var(--tf-border);
        display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px;
        font-size: 13px;
    }
    .detail-row .detail-content .detail-group label {
        font-size: 11px; color: var(--tf-muted); text-transform: uppercase;
        letter-spacing: 0.3px; display: block; margin-bottom: 2px;
    }
    .detail-row .detail-content .detail-group span { color: var(--tf-text); }

    /* Badges */
    .badge {
        display: inline-block; padding: 3px 10px; border-radius: 6px;
        font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.3px;
    }
    .badge-instock { background: rgba(34,197,94,0.15); color: var(--tf-green); }
    .badge-lowstock { background: rgba(234,179,8,0.15); color: var(--tf-yellow); }
    .badge-outofstock { background: rgba(239,68,68,0.15); color: var(--tf-red); }

    /* Sidebar panels */
    .side-panel {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06); padding: 20px;
    }
    .side-panel h3 {
        font-size: 14px; font-weight: 700; margin: 0 0 16px 0;
        display: flex; align-items: center; gap: 8px;
    }
    .side-panel h3 .panel-icon { font-size: 16px; }

    /* Category bar chart */
    .cat-bar-list { display: flex; flex-direction: column; gap: 10px; }
    .cat-bar-item { display: flex; align-items: center; gap: 10px; }
    .cat-bar-label { font-size: 12px; color: var(--tf-muted); width: 100px; flex-shrink: 0; text-align: right; }
    .cat-bar-track { flex: 1; height: 20px; background: rgba(0,0,0,0.2); border-radius: 4px; overflow: hidden; }
    .cat-bar-fill { height: 100%; border-radius: 4px; transition: width 0.5s ease; min-width: 2px; }
    .cat-bar-val { font-size: 12px; font-weight: 700; width: 32px; }

    /* Low stock list */
    .low-stock-list { display: flex; flex-direction: column; gap: 8px; }
    .low-stock-item {
        display: flex; justify-content: space-between; align-items: center;
        padding: 8px 12px; background: rgba(0,0,0,0.15); border-radius: 8px;
        border-left: 3px solid var(--tf-yellow); font-size: 12px;
    }
    .low-stock-item .ls-name { font-weight: 600; }
    .low-stock-item .ls-qty { color: var(--tf-yellow); font-weight: 700; }

    /* Activity list */
    .activity-list { display: flex; flex-direction: column; gap: 10px; }
    .activity-item {
        display: flex; gap: 10px; padding: 8px 0;
        border-bottom: 1px solid rgba(255,255,255,0.04); font-size: 12px;
    }
    .activity-item:last-child { border-bottom: none; }
    .activity-icon {
        width: 28px; height: 28px; border-radius: 6px; display: flex;
        align-items: center; justify-content: center; font-size: 13px; flex-shrink: 0;
    }
    .activity-icon.fab { background: rgba(34,197,94,0.15); color: var(--tf-green); }
    .activity-icon.recv { background: rgba(59,130,246,0.15); color: var(--tf-blue); }
    .activity-icon.adj { background: rgba(234,179,8,0.15); color: var(--tf-yellow); }
    .activity-icon.del { background: rgba(239,68,68,0.15); color: var(--tf-red); }
    .activity-text { color: var(--tf-muted); line-height: 1.4; }
    .activity-text strong { color: var(--tf-text); }
    .activity-time { font-size: 11px; color: var(--tf-muted); margin-top: 2px; }

    /* Modals */
    .modal-overlay {
        display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.7);
        z-index: 9000; align-items: center; justify-content: center;
        backdrop-filter: blur(4px);
    }
    .modal-overlay.active { display: flex; }
    .modal {
        background: var(--tf-card); border-radius: 16px;
        border: 1px solid var(--tf-border); width: 600px; max-width: 95vw;
        max-height: 90vh; overflow-y: auto; box-shadow: 0 25px 60px rgba(0,0,0,0.5);
    }
    .modal-header {
        display: flex; justify-content: space-between; align-items: center;
        padding: 20px 24px; border-bottom: 1px solid var(--tf-border);
    }
    .modal-header h2 { font-size: 18px; font-weight: 700; margin: 0; }
    .modal-close {
        background: none; border: none; color: var(--tf-muted); font-size: 22px;
        cursor: pointer; padding: 4px 8px; border-radius: 6px;
    }
    .modal-close:hover { color: var(--tf-text); background: rgba(255,255,255,0.06); }
    .modal-body { padding: 24px; }
    .modal-footer {
        padding: 16px 24px; border-top: 1px solid var(--tf-border);
        display: flex; justify-content: flex-end; gap: 10px;
    }

    /* Form */
    .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .form-group { display: flex; flex-direction: column; }
    .form-group.full { grid-column: 1 / -1; }
    .form-group label {
        font-size: 12px; font-weight: 600; color: var(--tf-muted);
        text-transform: uppercase; letter-spacing: 0.3px; margin-bottom: 6px;
    }
    .form-group input, .form-group select, .form-group textarea {
        background: var(--tf-bg); border: 1px solid var(--tf-border);
        border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px;
        font-family: inherit;
    }
    .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
        outline: none; border-color: var(--tf-blue); box-shadow: 0 0 0 3px rgba(59,130,246,0.15);
    }
    .form-group textarea { resize: vertical; min-height: 60px; }
    .form-group .help { font-size: 11px; color: var(--tf-muted); margin-top: 4px; }
    .form-divider {
        grid-column: 1 / -1; border: none;
        border-top: 1px solid var(--tf-border); margin: 4px 0;
    }

    /* Fab modal green theme */
    .modal-fab .modal-header { background: rgba(34,197,94,0.06); border-bottom-color: rgba(34,197,94,0.2); }
    .modal-fab .modal-header h2 { color: var(--tf-green); }
    .fab-warning {
        background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3);
        border-radius: 8px; padding: 12px 16px; margin-top: 12px;
        font-size: 13px; color: var(--tf-red); display: none;
    }
    .fab-calc {
        background: rgba(34,197,94,0.06); border: 1px solid rgba(34,197,94,0.15);
        border-radius: 8px; padding: 14px 16px; margin-top: 12px;
    }
    .fab-calc .calc-row {
        display: flex; justify-content: space-between; font-size: 13px;
        padding: 4px 0; color: var(--tf-muted);
    }
    .fab-calc .calc-row strong { color: var(--tf-text); }

    /* Loading spinner */
    .spinner {
        display: inline-block; width: 20px; height: 20px;
        border: 2px solid rgba(255,255,255,0.1);
        border-top-color: var(--tf-blue); border-radius: 50%;
        animation: spin 0.7s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }

    .loading-state {
        display: flex; align-items: center; justify-content: center;
        padding: 60px 0; color: var(--tf-muted); gap: 12px; font-size: 14px;
    }

    /* Empty state */
    .empty-state {
        text-align: center; padding: 60px 20px; color: var(--tf-muted);
    }
    .empty-state .empty-icon { font-size: 48px; margin-bottom: 16px; opacity: 0.5; }
    .empty-state h3 { font-size: 18px; color: var(--tf-text); margin-bottom: 8px; }
    .empty-state p { font-size: 14px; margin-bottom: 20px; }

    /* Toast */
    .toast-container {
        position: fixed; top: 24px; right: 24px; z-index: 9500;
        display: flex; flex-direction: column; gap: 8px;
    }
    .toast {
        padding: 14px 20px; border-radius: 10px; font-size: 14px;
        font-weight: 600; box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        animation: slideIn 0.3s ease;
    }
    .toast-success { background: var(--tf-green); color: #fff; }
    .toast-error { background: var(--tf-red); color: #fff; }
    .toast-warning { background: var(--tf-yellow); color: #0f172a; }
    @keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }

    /* Responsive */
    @media (max-width: 768px) {
        .pi-container { padding: 16px; }
        .stat-row { grid-template-columns: repeat(2, 1fr); gap: 10px; }
        .pi-layout { grid-template-columns: 1fr; }
        .pi-sidebar { order: 2; }
        .toolbar { flex-direction: column; align-items: stretch; }
        .toolbar-left, .toolbar-right { width: 100%; }
        .search-input { width: 100% !important; }
        .items-table-wrap { overflow-x: auto; }
        .items-table { min-width: 900px; }
        .cat-tabs { gap: 2px; }
        .cat-tab { padding: 8px 12px; font-size: 12px; }
        .form-grid { grid-template-columns: 1fr; }
        .modal { width: 100%; border-radius: 12px; margin: 8px; }
        .detail-row .detail-content { grid-template-columns: 1fr; }
    }
</style>

<div class="pi-container">
    <!-- Toast container -->
    <div class="toast-container" id="toastContainer"></div>

    <!-- Header -->
    <div class="page-header">
        <div class="breadcrumb"><a href="/">Dashboard</a> &rsaquo; <a href="/inventory">Inventory</a> &rsaquo; Parts</div>
        <h1>Parts Inventory</h1>
        <p>Track fabricated parts, fasteners, rebar, and custom items across all locations.</p>
    </div>

    <!-- Category Tabs -->
    <div class="cat-tabs" id="catTabs">
        <button class="cat-tab active" data-cat="all" onclick="switchCategory('all')">All Items <span class="tab-count" id="countAll">0</span></button>
        <button class="cat-tab" data-cat="fabricated" onclick="switchCategory('fabricated')">Fabricated Parts <span class="tab-count" id="countFabricated">0</span></button>
        <button class="cat-tab" data-cat="fasteners" onclick="switchCategory('fasteners')">Fasteners &amp; Hardware <span class="tab-count" id="countFasteners">0</span></button>
        <button class="cat-tab" data-cat="rebar" onclick="switchCategory('rebar')">Rebar <span class="tab-count" id="countRebar">0</span></button>
        <button class="cat-tab" data-cat="custom" onclick="switchCategory('custom')">Custom Items <span class="tab-count" id="countCustom">0</span></button>
    </div>

    <!-- Stats Row -->
    <div class="stat-row">
        <div class="stat-card stat-blue">
            <div class="label">Total Items</div>
            <div class="value" id="statTotal">--</div>
            <div class="sub" id="statTotalSub">Loading...</div>
        </div>
        <div class="stat-card stat-yellow">
            <div class="label">Low Stock Alerts</div>
            <div class="value" id="statLow">--</div>
            <div class="sub" id="statLowSub">Below minimum</div>
        </div>
        <div class="stat-card stat-green">
            <div class="label">Total Value</div>
            <div class="value" id="statValue">--</div>
            <div class="sub" id="statValueSub">On hand</div>
        </div>
        <div class="stat-card stat-gold">
            <div class="label">Pending POs</div>
            <div class="value" id="statPO">--</div>
            <div class="sub" id="statPOSub">Awaiting delivery</div>
        </div>
    </div>

    <!-- Main Layout -->
    <div class="pi-layout">
        <!-- Left: Table area -->
        <div class="pi-main">
            <!-- Toolbar -->
            <div class="toolbar">
                <div class="toolbar-left">
                    <input type="text" class="search-input" id="searchInput" placeholder="Search name, SKU, category, location..." oninput="debounceSearch()">
                    <select id="filterCategory" onchange="applyFilters()">
                        <option value="">All Categories</option>
                        <option value="P1 Clips">P1 Clips</option>
                        <option value="P2 End Caps">P2 End Caps</option>
                        <option value="P3 Plates">P3 Plates</option>
                        <option value="Splice Plates">Splice Plates</option>
                        <option value="Sag Rods">Sag Rods</option>
                        <option value="Triangles">Triangles</option>
                        <option value="Hurricane Straps">Hurricane Straps</option>
                        <option value="U-Channels">U-Channels</option>
                        <option value="Tek Screws">Tek Screws</option>
                        <option value="Hex Bolts">Hex Bolts</option>
                        <option value="Nuts">Nuts</option>
                        <option value="Washers">Washers</option>
                        <option value="Lag Bolts">Lag Bolts</option>
                        <option value="Anchor Bolts">Anchor Bolts</option>
                        <option value="Rebar Sticks">Rebar Sticks</option>
                        <option value="J-Bolts">J-Bolts</option>
                        <option value="Rebar Chairs">Rebar Chairs</option>
                        <option value="Tie Wire">Tie Wire</option>
                        <option value="Custom">Custom</option>
                    </select>
                    <select id="filterLocation" onchange="applyFilters()">
                        <option value="">All Locations</option>
                    </select>
                    <select id="filterStatus" onchange="applyFilters()">
                        <option value="">All Status</option>
                        <option value="in_stock">In Stock</option>
                        <option value="low_stock">Low Stock</option>
                        <option value="out_of_stock">Out of Stock</option>
                    </select>
                </div>
                <div class="toolbar-right">
                    <button class="btn btn-success" id="btnFabricate" style="display:none;" onclick="openFabModal()">&#9881; Fabricate</button>
                    <button class="btn btn-primary" onclick="openAddModal()">+ Add Item</button>
                </div>
            </div>

            <!-- Items Table -->
            <div class="items-table-wrap">
                <div id="tableLoading" class="loading-state"><div class="spinner"></div> Loading inventory...</div>
                <div id="tableEmpty" class="empty-state" style="display:none;">
                    <div class="empty-icon">&#128230;</div>
                    <h3>No items found</h3>
                    <p>No parts match your current filters. Try adjusting your search or add a new item.</p>
                    <button class="btn btn-primary" onclick="openAddModal()">+ Add First Item</button>
                </div>
                <table class="items-table" id="itemsTable" style="display:none;">
                    <thead>
                        <tr>
                            <th onclick="sortTable('sku')">SKU <span class="sort-icon" id="sort-sku"></span></th>
                            <th onclick="sortTable('name')">Name <span class="sort-icon" id="sort-name"></span></th>
                            <th onclick="sortTable('category')">Category <span class="sort-icon" id="sort-category"></span></th>
                            <th onclick="sortTable('qty_on_hand')">Qty On Hand <span class="sort-icon" id="sort-qty_on_hand"></span></th>
                            <th onclick="sortTable('min_stock')">Min Stock <span class="sort-icon" id="sort-min_stock"></span></th>
                            <th onclick="sortTable('status')">Status <span class="sort-icon" id="sort-status"></span></th>
                            <th onclick="sortTable('location')">Location <span class="sort-icon" id="sort-location"></span></th>
                            <th onclick="sortTable('cost_per_unit')">Cost/Unit <span class="sort-icon" id="sort-cost_per_unit"></span></th>
                            <th onclick="sortTable('total_value')">Total Value <span class="sort-icon" id="sort-total_value"></span></th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="itemsBody"></tbody>
                </table>
            </div>
        </div>

        <!-- Right Sidebar -->
        <div class="pi-sidebar">
            <!-- Stock by Category -->
            <div class="side-panel">
                <h3><span class="panel-icon">&#128202;</span> Stock by Category</h3>
                <div class="cat-bar-list" id="catBarChart">
                    <div class="loading-state" style="padding:20px 0;"><div class="spinner"></div></div>
                </div>
            </div>
            <!-- Low Stock -->
            <div class="side-panel">
                <h3><span class="panel-icon">&#9888;&#65039;</span> Low Stock Items</h3>
                <div class="low-stock-list" id="lowStockList">
                    <div class="loading-state" style="padding:20px 0;"><div class="spinner"></div></div>
                </div>
            </div>
            <!-- Recent Activity -->
            <div class="side-panel">
                <h3><span class="panel-icon">&#128337;</span> Recent Activity</h3>
                <div class="activity-list" id="activityList">
                    <div class="loading-state" style="padding:20px 0;"><div class="spinner"></div></div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Add/Edit Item Modal -->
<div class="modal-overlay" id="modalItem">
    <div class="modal">
        <div class="modal-header">
            <h2 id="modalItemTitle">Add New Item</h2>
            <button class="modal-close" onclick="closeModal('modalItem')">&times;</button>
        </div>
        <div class="modal-body">
            <form id="itemForm" onsubmit="return false;">
                <input type="hidden" id="itemId" value="">
                <div class="form-grid">
                    <div class="form-group">
                        <label>Name *</label>
                        <input type="text" id="itemName" required placeholder="e.g. P1 Interior Clip - 14ga">
                    </div>
                    <div class="form-group">
                        <label>SKU</label>
                        <input type="text" id="itemSku" placeholder="Auto-generated if blank">
                        <span class="help">Leave blank to auto-generate</span>
                    </div>
                    <div class="form-group">
                        <label>Category *</label>
                        <select id="itemCategory" required onchange="onCategoryChange()">
                            <option value="">Select...</option>
                            <optgroup label="Fabricated Parts">
                                <option value="P1 Clips">P1 Clips</option>
                                <option value="P2 End Caps">P2 End Caps</option>
                                <option value="P3 Plates">P3 Plates</option>
                                <option value="Splice Plates">Splice Plates</option>
                                <option value="Sag Rods">Sag Rods</option>
                                <option value="Triangles">Triangles</option>
                                <option value="Hurricane Straps">Hurricane Straps</option>
                                <option value="U-Channels">U-Channels</option>
                            </optgroup>
                            <optgroup label="Fasteners & Hardware">
                                <option value="Tek Screws">Tek Screws</option>
                                <option value="Hex Bolts">Hex Bolts</option>
                                <option value="Nuts">Nuts</option>
                                <option value="Washers">Washers</option>
                                <option value="Lag Bolts">Lag Bolts</option>
                                <option value="Anchor Bolts">Anchor Bolts</option>
                            </optgroup>
                            <optgroup label="Rebar">
                                <option value="Rebar Sticks">Rebar Sticks</option>
                                <option value="J-Bolts">J-Bolts</option>
                                <option value="Rebar Chairs">Rebar Chairs</option>
                                <option value="Tie Wire">Tie Wire</option>
                            </optgroup>
                            <optgroup label="Other">
                                <option value="Custom">Custom</option>
                            </optgroup>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Subcategory</label>
                        <input type="text" id="itemSubcategory" placeholder="e.g. Interior, Exterior">
                    </div>
                    <div class="form-group full">
                        <label>Description</label>
                        <textarea id="itemDescription" placeholder="Optional description..."></textarea>
                    </div>
                    <hr class="form-divider">
                    <div class="form-group">
                        <label>Unit</label>
                        <select id="itemUnit">
                            <option value="ea">Each (ea)</option>
                            <option value="lbs">Pounds (lbs)</option>
                            <option value="ft">Feet (ft)</option>
                            <option value="box">Box</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Qty On Hand</label>
                        <input type="number" id="itemQty" value="0" min="0" step="1">
                    </div>
                    <div class="form-group">
                        <label>Min Stock</label>
                        <input type="number" id="itemMinStock" value="0" min="0" step="1">
                    </div>
                    <div class="form-group">
                        <label>Reorder Qty</label>
                        <input type="number" id="itemReorderQty" value="0" min="0" step="1">
                    </div>
                    <hr class="form-divider">
                    <div class="form-group">
                        <label>Storage Location</label>
                        <input type="text" id="itemLocation" placeholder="e.g. Warehouse A">
                    </div>
                    <div class="form-group">
                        <label>Bin #</label>
                        <input type="text" id="itemBin" placeholder="e.g. A-12">
                    </div>
                    <div class="form-group">
                        <label>Preferred Vendor</label>
                        <input type="text" id="itemVendor" placeholder="Vendor name">
                    </div>
                    <div class="form-group">
                        <label>Cost / Unit ($)</label>
                        <input type="number" id="itemCost" value="0" min="0" step="0.01">
                    </div>
                    <div class="form-group">
                        <label>Sell Price ($)</label>
                        <input type="number" id="itemSellPrice" value="0" min="0" step="0.01">
                    </div>
                    <div class="form-group">
                        <label>Weight (lbs)</label>
                        <input type="number" id="itemWeight" value="0" min="0" step="0.01">
                    </div>
                    <!-- Fabricated-only fields -->
                    <div id="fabFields" style="display:none; grid-column:1/-1;">
                        <hr class="form-divider" style="margin-bottom:16px;">
                        <div style="font-size:12px;font-weight:700;color:var(--tf-green);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:12px;">Fabrication Details</div>
                        <div class="form-grid">
                            <div class="form-group">
                                <label>Coil Gauge</label>
                                <select id="itemCoilGauge">
                                    <option value="">N/A</option>
                                    <option value="26">26 ga</option>
                                    <option value="24">24 ga</option>
                                    <option value="22">22 ga</option>
                                    <option value="20">20 ga</option>
                                    <option value="18">18 ga</option>
                                    <option value="16">16 ga</option>
                                    <option value="14">14 ga</option>
                                    <option value="12">12 ga</option>
                                    <option value="10">10 ga</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Coil Lbs Per Unit</label>
                                <input type="number" id="itemCoilLbsPerUnit" value="0" min="0" step="0.01">
                                <span class="help">Lbs of coil consumed per piece</span>
                            </div>
                        </div>
                    </div>
                    <div class="form-group full">
                        <label>Notes</label>
                        <textarea id="itemNotes" placeholder="Internal notes..."></textarea>
                    </div>
                </div>
            </form>
        </div>
        <div class="modal-footer">
            <button class="btn btn-secondary" onclick="closeModal('modalItem')">Cancel</button>
            <button class="btn btn-primary" id="btnSaveItem" onclick="handleSaveItem()">Save Item</button>
        </div>
    </div>
</div>

<!-- Fabricate Modal -->
<div class="modal-overlay" id="modalFab">
    <div class="modal modal-fab">
        <div class="modal-header">
            <h2>&#9881; Fabricate Parts from Coil Stock</h2>
            <button class="modal-close" onclick="closeModal('modalFab')">&times;</button>
        </div>
        <div class="modal-body">
            <div class="form-grid">
                <div class="form-group full">
                    <label>Part to Fabricate *</label>
                    <select id="fabPart" onchange="onFabPartChange()">
                        <option value="">Select fabricated part...</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Quantity to Fabricate *</label>
                    <input type="number" id="fabQty" min="1" value="1" oninput="onFabQtyChange()">
                </div>
                <div class="form-group">
                    <label>Source Coil</label>
                    <select id="fabCoil" onchange="onFabCoilChange()">
                        <option value="">Select coil...</option>
                    </select>
                </div>
            </div>
            <div class="fab-calc" id="fabCalc" style="display:none;">
                <div class="calc-row"><span>Gauge Required:</span> <strong id="fabCalcGauge">--</strong></div>
                <div class="calc-row"><span>Lbs per Unit:</span> <strong id="fabCalcLbs">--</strong></div>
                <div class="calc-row"><span>Total Material Needed:</span> <strong id="fabCalcTotal">--</strong></div>
                <div class="calc-row"><span>Available Coil Stock:</span> <strong id="fabCalcAvail">--</strong></div>
                <div class="calc-row"><span>Remaining After Fab:</span> <strong id="fabCalcRemain">--</strong></div>
            </div>
            <div class="fab-warning" id="fabWarning">&#9888; Insufficient coil stock for this fabrication run. Reduce quantity or select a different coil.</div>
            <div class="form-grid" style="margin-top:16px;">
                <div class="form-group">
                    <label>Operator</label>
                    <input type="text" id="fabOperator" placeholder="Operator name">
                </div>
                <div class="form-group">
                    <label>Notes</label>
                    <input type="text" id="fabNotes" placeholder="Optional notes">
                </div>
            </div>
        </div>
        <div class="modal-footer">
            <button class="btn btn-secondary" onclick="closeModal('modalFab')">Cancel</button>
            <button class="btn btn-success" id="btnFabSubmit" onclick="handleFabricate()">&#9881; Fabricate</button>
        </div>
    </div>
</div>

<!-- Adjust Stock Modal -->
<div class="modal-overlay" id="modalAdjust">
    <div class="modal">
        <div class="modal-header">
            <h2>Adjust Stock</h2>
            <button class="modal-close" onclick="closeModal('modalAdjust')">&times;</button>
        </div>
        <div class="modal-body">
            <div class="form-grid">
                <div class="form-group full">
                    <label>Item</label>
                    <select id="adjItem">
                        <option value="">Select item...</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Adjustment</label>
                    <select id="adjDirection">
                        <option value="+">+ Add Stock</option>
                        <option value="-">- Remove Stock</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Quantity</label>
                    <input type="number" id="adjQty" min="1" value="1">
                </div>
                <div class="form-group full">
                    <label>Reason</label>
                    <select id="adjReason">
                        <option value="count_correction">Count Correction</option>
                        <option value="received">Received</option>
                        <option value="scrap">Scrap</option>
                        <option value="used_in_production">Used in Production</option>
                        <option value="returned">Returned</option>
                        <option value="other">Other</option>
                    </select>
                </div>
                <div class="form-group full">
                    <label>Notes</label>
                    <textarea id="adjNotes" placeholder="Adjustment notes..."></textarea>
                </div>
            </div>
        </div>
        <div class="modal-footer">
            <button class="btn btn-secondary" onclick="closeModal('modalAdjust')">Cancel</button>
            <button class="btn btn-primary" onclick="handleAdjust()">Apply Adjustment</button>
        </div>
    </div>
</div>

<!-- Quick PO Modal -->
<div class="modal-overlay" id="modalPO">
    <div class="modal">
        <div class="modal-header">
            <h2>Quick Purchase Order</h2>
            <button class="modal-close" onclick="closeModal('modalPO')">&times;</button>
        </div>
        <div class="modal-body">
            <div class="form-grid">
                <div class="form-group full">
                    <label>Item</label>
                    <input type="text" id="poItemName" readonly style="opacity:0.7;">
                    <input type="hidden" id="poItemId">
                </div>
                <div class="form-group">
                    <label>Vendor</label>
                    <input type="text" id="poVendor" placeholder="Vendor name">
                </div>
                <div class="form-group">
                    <label>Quantity</label>
                    <input type="number" id="poQty" min="1" value="1">
                </div>
                <div class="form-group">
                    <label>Unit Cost ($)</label>
                    <input type="number" id="poUnitCost" min="0" step="0.01" value="0">
                </div>
                <div class="form-group full">
                    <label>Notes</label>
                    <textarea id="poNotes" placeholder="PO notes..."></textarea>
                </div>
            </div>
        </div>
        <div class="modal-footer">
            <button class="btn btn-secondary" onclick="closeModal('modalPO')">Cancel</button>
            <button class="btn btn-gold" onclick="handleQuickPO()">Create PO</button>
        </div>
    </div>
</div>

<script>
(function(){
    // === State ===
    let allItems = [];
    let filteredItems = [];
    let currentCategory = 'all';
    let currentSort = { col: 'name', dir: 'asc' };
    let expandedRow = null;
    let searchTimer = null;
    let coilInventory = [];
    let categoryCounts = {};

    const FABRICATED_CATS = ['P1 Clips','P2 End Caps','P3 Plates','Splice Plates','Sag Rods','Triangles','Hurricane Straps','U-Channels'];
    const FASTENER_CATS = ['Tek Screws','Hex Bolts','Nuts','Washers','Lag Bolts','Anchor Bolts'];
    const REBAR_CATS = ['Rebar Sticks','J-Bolts','Rebar Chairs','Tie Wire'];

    // === Init ===
    function init() {
        var params = new URLSearchParams(window.location.search);
        var type = params.get('type');
        if (type === 'coils') {
            window.location.href = '/inventory';
            return;
        }
        if (type === 'rebar') switchCategory('rebar');
        else if (type === 'fasteners') switchCategory('fasteners');
        else if (type === 'fabricated') switchCategory('fabricated');
        else if (type === 'purchased') switchCategory('all');
        else switchCategory('all');

        // Auto-populate catalog on first visit
        fetch('/api/parts-inventory/catalog').then(function(){
            loadItems();
            loadRecentActivity();
            loadCoilInventory();
        }).catch(function(){
            loadItems();
            loadRecentActivity();
            loadCoilInventory();
        });
    }

    // === API Calls ===
    async function loadItems(category, search, status, location) {
        try {
            var params = new URLSearchParams();
            if (category && category !== 'all') params.set('category', category);
            if (search) params.set('search', search);
            if (status) params.set('status', status);
            if (location) params.set('location', location);

            var resp = await fetch('/api/parts-inventory?' + params.toString());
            if (!resp.ok) throw new Error('Failed to load items');
            var data = await resp.json();
            allItems = data.items || data || [];
            computeCategoryCounts();
            applyFiltersInternal();
            computeStats();
            computeLowStock();
        } catch(e) {
            console.error('loadItems error:', e);
            allItems = [];
            filteredItems = [];
            renderItems([]);
        }
    }

    function computeStats() {
        var total = allItems.length;
        var low = allItems.filter(function(i){ return i.status === 'low_stock' || i.status === 'out_of_stock'; }).length;
        var val = allItems.reduce(function(s,i){ return s + (i.qty_on_hand||0)*(i.cost_per_unit||0); }, 0);
        renderStats({total_items: total, low_stock: low, total_value: val, pending_pos: 0});
    }

    function computeLowStock() {
        var low = allItems.filter(function(i){ return i.status === 'low_stock' || i.status === 'out_of_stock'; });
        renderLowStock(low.slice(0, 10));
    }

    async function loadRecentActivity() {
        try {
            var resp = await fetch('/api/parts-inventory/transactions?limit=5');
            if (!resp.ok) throw new Error('Failed');
            var data = await resp.json();
            renderActivity(data.transactions || data || []);
        } catch(e) {
            renderActivity([]);
        }
    }

    async function loadCoilInventory() {
        try {
            var resp = await fetch('/api/inventory?type=coil');
            if (!resp.ok) throw new Error('Failed');
            var data = await resp.json();
            coilInventory = data.items || data || [];
        } catch(e) {
            coilInventory = [];
        }
    }

    async function saveItem(data) {
        var resp = await fetch('/api/parts-inventory', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!resp.ok) {
            var err = await resp.json().catch(function(){ return {}; });
            throw new Error(err.error || 'Failed to save item');
        }
        return resp.json();
    }

    async function deleteItem(id) {
        var resp = await fetch('/api/parts-inventory?id=' + encodeURIComponent(id), {
            method: 'DELETE'
        });
        if (!resp.ok) throw new Error('Failed to delete item');
        return resp.json();
    }

    async function adjustStock(data) {
        var resp = await fetch('/api/parts-inventory/adjust', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!resp.ok) throw new Error('Failed to adjust stock');
        return resp.json();
    }

    async function fabricateParts(data) {
        var resp = await fetch('/api/parts-inventory/fabricate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!resp.ok) throw new Error('Failed to fabricate');
        return resp.json();
    }

    async function createQuickPO(data) {
        var resp = await fetch('/api/parts-inventory/quick-po', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!resp.ok) throw new Error('Failed to create PO');
        return resp.json();
    }

    // === Category helpers ===
    function getCatGroup(cat) {
        if (FABRICATED_CATS.indexOf(cat) !== -1) return 'fabricated';
        if (FASTENER_CATS.indexOf(cat) !== -1) return 'fasteners';
        if (REBAR_CATS.indexOf(cat) !== -1) return 'rebar';
        return 'custom';
    }

    function computeCategoryCounts() {
        categoryCounts = { all: allItems.length, fabricated: 0, fasteners: 0, rebar: 0, custom: 0 };
        allItems.forEach(function(it) {
            var g = getCatGroup(it.category);
            categoryCounts[g] = (categoryCounts[g] || 0) + 1;
        });
        document.getElementById('countAll').textContent = categoryCounts.all;
        document.getElementById('countFabricated').textContent = categoryCounts.fabricated;
        document.getElementById('countFasteners').textContent = categoryCounts.fasteners;
        document.getElementById('countRebar').textContent = categoryCounts.rebar;
        document.getElementById('countCustom').textContent = categoryCounts.custom;
    }

    // === UI Functions ===
    window.switchCategory = function(cat) {
        currentCategory = cat;
        document.querySelectorAll('.cat-tab').forEach(function(t) {
            t.classList.toggle('active', t.dataset.cat === cat);
        });
        // Show/hide fabricate button
        document.getElementById('btnFabricate').style.display = (cat === 'fabricated') ? '' : 'none';
        applyFiltersInternal();
    };

    function applyFiltersInternal() {
        var search = (document.getElementById('searchInput').value || '').toLowerCase();
        var catFilter = document.getElementById('filterCategory').value;
        var locFilter = document.getElementById('filterLocation').value;
        var statusFilter = document.getElementById('filterStatus').value;

        filteredItems = allItems.filter(function(it) {
            // Tab filter
            if (currentCategory !== 'all') {
                var g = getCatGroup(it.category);
                if (g !== currentCategory) return false;
            }
            // Category dropdown
            if (catFilter && it.category !== catFilter) return false;
            // Location
            if (locFilter && it.location !== locFilter) return false;
            // Status
            if (statusFilter) {
                var s = getStatus(it);
                if (s !== statusFilter) return false;
            }
            // Search
            if (search) {
                var hay = [it.name, it.sku, it.category, it.description, it.location, it.subcategory].join(' ').toLowerCase();
                if (hay.indexOf(search) === -1) return false;
            }
            return true;
        });

        // Sort
        sortItems();
        renderItems(filteredItems);
        populateLocationFilter();
    }

    window.applyFilters = function() { applyFiltersInternal(); };

    window.debounceSearch = function() {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(function() { applyFiltersInternal(); }, 250);
    };

    function getStatus(item) {
        var qty = item.qty_on_hand || 0;
        var min = item.min_stock || 0;
        if (qty <= 0) return 'out_of_stock';
        if (min > 0 && qty <= min) return 'low_stock';
        return 'in_stock';
    }

    function statusBadge(status) {
        if (status === 'in_stock') return '<span class="badge badge-instock">In Stock</span>';
        if (status === 'low_stock') return '<span class="badge badge-lowstock">Low Stock</span>';
        return '<span class="badge badge-outofstock">Out of Stock</span>';
    }

    function fmtCurrency(v) {
        return '$' + (parseFloat(v) || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }

    function populateLocationFilter() {
        var locs = {};
        allItems.forEach(function(it) { if (it.location) locs[it.location] = true; });
        var sel = document.getElementById('filterLocation');
        var val = sel.value;
        var opts = '<option value="">All Locations</option>';
        Object.keys(locs).sort().forEach(function(l) {
            opts += '<option value="' + l + '"' + (l === val ? ' selected' : '') + '>' + l + '</option>';
        });
        sel.innerHTML = opts;
    }

    // === Render ===
    function renderItems(items) {
        var loading = document.getElementById('tableLoading');
        var empty = document.getElementById('tableEmpty');
        var table = document.getElementById('itemsTable');

        loading.style.display = 'none';
        if (!items || items.length === 0) {
            empty.style.display = '';
            table.style.display = 'none';
            return;
        }
        empty.style.display = 'none';
        table.style.display = '';

        var html = '';
        items.forEach(function(it) {
            var status = getStatus(it);
            var totalVal = (parseFloat(it.qty_on_hand) || 0) * (parseFloat(it.cost_per_unit) || 0);
            var id = it.id || it._id || '';
            html += '<tr data-id="' + id + '" onclick="toggleDetail(\'' + id + '\')">';
            html += '<td>' + esc(it.sku || '--') + '</td>';
            html += '<td class="name-cell">' + esc(it.name || '') + '</td>';
            html += '<td>' + esc(it.category || '') + '</td>';
            html += '<td style="font-weight:700;">' + (it.qty_on_hand || 0) + ' <span style="color:var(--tf-muted);font-weight:400;font-size:11px;">' + esc(it.unit || 'ea') + '</span></td>';
            html += '<td>' + (it.min_stock || 0) + '</td>';
            html += '<td>' + statusBadge(status) + '</td>';
            html += '<td>' + esc(it.location || '--') + '</td>';
            html += '<td>' + fmtCurrency(it.cost_per_unit) + '</td>';
            html += '<td>' + fmtCurrency(totalVal) + '</td>';
            html += '<td onclick="event.stopPropagation();">';
            html += '<button class="btn btn-secondary btn-xs" onclick="openAddModal(getItemById(\'' + id + '\'))" title="Edit">&#9998;</button> ';
            html += '<button class="btn btn-secondary btn-xs" onclick="openAdjustModal(\'' + id + '\')" title="Adjust Stock">&#177;</button> ';
            html += '<button class="btn btn-secondary btn-xs" onclick="openPOModal(\'' + id + '\')" title="Quick PO">&#128230;</button> ';
            html += '<button class="btn btn-danger btn-xs" onclick="confirmDelete(\'' + id + '\')" title="Delete">&#128465;</button>';
            html += '</td>';
            html += '</tr>';
            // detail row (hidden)
            html += '<tr class="detail-row" id="detail-' + id + '" style="display:none;">';
            html += '<td colspan="10"><div class="detail-content">';
            html += '<div class="detail-group"><label>Last Transaction</label><span>' + esc(it.last_transaction || 'None') + '</span></div>';
            html += '<div class="detail-group"><label>Preferred Vendor</label><span>' + esc(it.vendor || it.preferred_vendor || '--') + '</span></div>';
            html += '<div class="detail-group"><label>Bin / Location</label><span>' + esc((it.location || '--') + (it.bin ? ' / ' + it.bin : '')) + '</span></div>';
            html += '<div class="detail-group"><label>Subcategory</label><span>' + esc(it.subcategory || '--') + '</span></div>';
            html += '<div class="detail-group"><label>Weight</label><span>' + (it.weight ? it.weight + ' lbs' : '--') + '</span></div>';
            html += '<div class="detail-group"><label>Notes</label><span>' + esc(it.notes || '--') + '</span></div>';
            if (FABRICATED_CATS.indexOf(it.category) !== -1) {
                html += '<div class="detail-group"><label>Coil Gauge</label><span>' + (it.coil_gauge ? it.coil_gauge + ' ga' : '--') + '</span></div>';
                html += '<div class="detail-group"><label>Coil Lbs/Unit</label><span>' + (it.coil_lbs_per_unit || '--') + '</span></div>';
            }
            html += '</div></td></tr>';
        });
        document.getElementById('itemsBody').innerHTML = html;
        expandedRow = null;
    }

    function renderStats(data) {
        document.getElementById('statTotal').textContent = data.total_items || allItems.length || '0';
        document.getElementById('statTotalSub').textContent = 'items tracked';
        document.getElementById('statLow').textContent = data.low_stock_count || '0';
        document.getElementById('statValue').textContent = fmtCurrency(data.total_value || 0);
        document.getElementById('statPO').textContent = data.pending_pos || '0';
    }

    function renderLowStock(items) {
        var el = document.getElementById('lowStockList');
        if (!items || items.length === 0) {
            el.innerHTML = '<div style="text-align:center;padding:16px;color:var(--tf-muted);font-size:13px;">All items above minimum stock.</div>';
            return;
        }
        var html = '';
        items.forEach(function(it) {
            html += '<div class="low-stock-item">';
            html += '<div><div class="ls-name">' + esc(it.name) + '</div><div style="font-size:11px;color:var(--tf-muted);">' + esc(it.sku || '') + '</div></div>';
            html += '<div style="display:flex;align-items:center;gap:8px;">';
            html += '<span class="ls-qty">' + (it.qty_on_hand || 0) + '/' + (it.min_stock || 0) + '</span>';
            html += '<button class="btn btn-gold btn-xs" onclick="openPOModal(\'' + (it.id || it._id) + '\')">PO</button>';
            html += '</div></div>';
        });
        el.innerHTML = html;
    }

    function renderActivity(activities) {
        var el = document.getElementById('activityList');
        if (!activities || activities.length === 0) {
            el.innerHTML = '<div style="text-align:center;padding:16px;color:var(--tf-muted);font-size:13px;">No recent activity.</div>';
            return;
        }
        var html = '';
        activities.slice(0, 5).forEach(function(a) {
            var iconClass = 'adj';
            var iconSymbol = '&#8644;';
            if (a.type === 'fabricate' || a.type === 'fab') { iconClass = 'fab'; iconSymbol = '&#9881;'; }
            else if (a.type === 'receive' || a.type === 'received') { iconClass = 'recv'; iconSymbol = '&#128230;'; }
            else if (a.type === 'delete') { iconClass = 'del'; iconSymbol = '&#128465;'; }

            html += '<div class="activity-item">';
            html += '<div class="activity-icon ' + iconClass + '">' + iconSymbol + '</div>';
            html += '<div><div class="activity-text"><strong>' + esc(a.item_name || a.description || '') + '</strong> ' + esc(a.summary || a.action || '') + '</div>';
            html += '<div class="activity-time">' + esc(a.timestamp || a.date || '') + '</div></div>';
            html += '</div>';
        });
        el.innerHTML = html;
    }

    function renderCategoryChart() {
        var cats = {};
        allItems.forEach(function(it) {
            cats[it.category] = (cats[it.category] || 0) + (it.qty_on_hand || 0);
        });
        var el = document.getElementById('catBarChart');
        var entries = Object.entries(cats).sort(function(a, b) { return b[1] - a[1]; });
        if (entries.length === 0) {
            el.innerHTML = '<div style="text-align:center;padding:16px;color:var(--tf-muted);font-size:13px;">No data.</div>';
            return;
        }
        var max = Math.max.apply(null, entries.map(function(e) { return e[1]; })) || 1;
        var colors = ['#3b82f6','#22c55e','#eab308','#ef4444','#d4a843','#06b6d4','#a855f7','#f97316','#ec4899','#14b8a6'];
        var html = '';
        entries.forEach(function(e, i) {
            var pct = Math.round((e[1] / max) * 100);
            html += '<div class="cat-bar-item">';
            html += '<div class="cat-bar-label">' + esc(e[0]) + '</div>';
            html += '<div class="cat-bar-track"><div class="cat-bar-fill" style="width:' + pct + '%;background:' + colors[i % colors.length] + ';"></div></div>';
            html += '<div class="cat-bar-val">' + e[1] + '</div>';
            html += '</div>';
        });
        el.innerHTML = html;
    }

    // === Sorting ===
    function sortItems() {
        var col = currentSort.col;
        var dir = currentSort.dir === 'asc' ? 1 : -1;
        filteredItems.sort(function(a, b) {
            var va = a[col], vb = b[col];
            if (col === 'total_value') {
                va = (parseFloat(a.qty_on_hand) || 0) * (parseFloat(a.cost_per_unit) || 0);
                vb = (parseFloat(b.qty_on_hand) || 0) * (parseFloat(b.cost_per_unit) || 0);
            }
            if (col === 'status') {
                va = getStatus(a);
                vb = getStatus(b);
            }
            if (typeof va === 'string') va = va.toLowerCase();
            if (typeof vb === 'string') vb = vb.toLowerCase();
            if (va == null) va = '';
            if (vb == null) vb = '';
            if (va < vb) return -1 * dir;
            if (va > vb) return 1 * dir;
            return 0;
        });
        // Update sort icons
        document.querySelectorAll('.sort-icon').forEach(function(el) { el.textContent = ''; });
        var icon = document.getElementById('sort-' + col);
        if (icon) icon.textContent = dir === 1 ? '\u25B2' : '\u25BC';
    }

    window.sortTable = function(col) {
        if (currentSort.col === col) {
            currentSort.dir = currentSort.dir === 'asc' ? 'desc' : 'asc';
        } else {
            currentSort = { col: col, dir: 'asc' };
        }
        sortItems();
        renderItems(filteredItems);
    };

    // === Row expand/collapse ===
    window.toggleDetail = function(id) {
        if (expandedRow && expandedRow !== id) {
            var prev = document.getElementById('detail-' + expandedRow);
            if (prev) prev.style.display = 'none';
        }
        var row = document.getElementById('detail-' + id);
        if (!row) return;
        if (row.style.display === 'none') {
            row.style.display = '';
            expandedRow = id;
        } else {
            row.style.display = 'none';
            expandedRow = null;
        }
    };

    // === Helpers ===
    window.getItemById = function(id) {
        return allItems.find(function(it) { return (it.id || it._id) === id; });
    };

    function esc(s) {
        if (!s) return '';
        var d = document.createElement('div');
        d.textContent = s;
        return d.innerHTML;
    }

    function showToast(msg, type) {
        type = type || 'success';
        var c = document.getElementById('toastContainer');
        var t = document.createElement('div');
        t.className = 'toast toast-' + type;
        t.textContent = msg;
        c.appendChild(t);
        setTimeout(function() { t.remove(); }, 4000);
    }

    function closeModal(id) {
        document.getElementById(id).classList.remove('active');
    }

    function openModal(id) {
        document.getElementById(id).classList.add('active');
    }

    // === Modal: Add/Edit ===
    window.openAddModal = function(editData) {
        var isEdit = editData && editData.id;
        document.getElementById('modalItemTitle').textContent = isEdit ? 'Edit Item' : 'Add New Item';
        document.getElementById('itemId').value = isEdit ? (editData.id || editData._id || '') : '';
        document.getElementById('itemName').value = isEdit ? (editData.name || '') : '';
        document.getElementById('itemSku').value = isEdit ? (editData.sku || '') : '';
        document.getElementById('itemCategory').value = isEdit ? (editData.category || '') : '';
        document.getElementById('itemSubcategory').value = isEdit ? (editData.subcategory || '') : '';
        document.getElementById('itemDescription').value = isEdit ? (editData.description || '') : '';
        document.getElementById('itemUnit').value = isEdit ? (editData.unit || 'ea') : 'ea';
        document.getElementById('itemQty').value = isEdit ? (editData.qty_on_hand || 0) : 0;
        document.getElementById('itemMinStock').value = isEdit ? (editData.min_stock || 0) : 0;
        document.getElementById('itemReorderQty').value = isEdit ? (editData.reorder_qty || 0) : 0;
        document.getElementById('itemLocation').value = isEdit ? (editData.location || '') : '';
        document.getElementById('itemBin').value = isEdit ? (editData.bin || '') : '';
        document.getElementById('itemVendor').value = isEdit ? (editData.vendor || editData.preferred_vendor || '') : '';
        document.getElementById('itemCost').value = isEdit ? (editData.cost_per_unit || 0) : 0;
        document.getElementById('itemSellPrice').value = isEdit ? (editData.sell_price || 0) : 0;
        document.getElementById('itemWeight').value = isEdit ? (editData.weight || 0) : 0;
        document.getElementById('itemNotes').value = isEdit ? (editData.notes || '') : '';
        document.getElementById('itemCoilGauge').value = isEdit ? (editData.coil_gauge || '') : '';
        document.getElementById('itemCoilLbsPerUnit').value = isEdit ? (editData.coil_lbs_per_unit || 0) : 0;
        onCategoryChange();
        openModal('modalItem');
    };

    window.onCategoryChange = function() {
        var cat = document.getElementById('itemCategory').value;
        var show = FABRICATED_CATS.indexOf(cat) !== -1;
        document.getElementById('fabFields').style.display = show ? '' : 'none';
    };

    window.handleSaveItem = async function() {
        var name = document.getElementById('itemName').value.trim();
        if (!name) { showToast('Name is required', 'error'); return; }
        var cat = document.getElementById('itemCategory').value;
        if (!cat) { showToast('Category is required', 'error'); return; }

        var data = {
            id: document.getElementById('itemId').value || undefined,
            name: name,
            sku: document.getElementById('itemSku').value.trim() || undefined,
            category: cat,
            subcategory: document.getElementById('itemSubcategory').value.trim(),
            description: document.getElementById('itemDescription').value.trim(),
            unit: document.getElementById('itemUnit').value,
            qty_on_hand: parseInt(document.getElementById('itemQty').value) || 0,
            min_stock: parseInt(document.getElementById('itemMinStock').value) || 0,
            reorder_qty: parseInt(document.getElementById('itemReorderQty').value) || 0,
            location: document.getElementById('itemLocation').value.trim(),
            bin: document.getElementById('itemBin').value.trim(),
            preferred_vendor: document.getElementById('itemVendor').value.trim(),
            cost_per_unit: parseFloat(document.getElementById('itemCost').value) || 0,
            sell_price: parseFloat(document.getElementById('itemSellPrice').value) || 0,
            weight: parseFloat(document.getElementById('itemWeight').value) || 0,
            notes: document.getElementById('itemNotes').value.trim()
        };

        if (FABRICATED_CATS.indexOf(cat) !== -1) {
            data.coil_gauge = document.getElementById('itemCoilGauge').value || null;
            data.coil_lbs_per_unit = parseFloat(document.getElementById('itemCoilLbsPerUnit').value) || 0;
        }

        var btn = document.getElementById('btnSaveItem');
        btn.disabled = true;
        btn.textContent = 'Saving...';

        try {
            await saveItem(data);
            closeModal('modalItem');
            showToast(data.id ? 'Item updated!' : 'Item added!');
            await refreshAll();
        } catch(e) {
            showToast(e.message || 'Save failed', 'error');
        } finally {
            btn.disabled = false;
            btn.textContent = 'Save Item';
        }
    };

    // === Modal: Fabricate ===
    window.openFabModal = function() {
        var sel = document.getElementById('fabPart');
        var opts = '<option value="">Select fabricated part...</option>';
        allItems.filter(function(it) { return FABRICATED_CATS.indexOf(it.category) !== -1; }).forEach(function(it) {
            opts += '<option value="' + (it.id || it._id) + '" data-gauge="' + (it.coil_gauge || '') + '" data-lbs="' + (it.coil_lbs_per_unit || 0) + '">' + esc(it.name) + ' (' + esc(it.sku || '?') + ')</option>';
        });
        sel.innerHTML = opts;

        var coilSel = document.getElementById('fabCoil');
        var coilOpts = '<option value="">Select coil...</option>';
        coilInventory.forEach(function(c) {
            coilOpts += '<option value="' + (c.id || c._id || c.coil_tag) + '" data-weight="' + (c.current_weight || c.weight || 0) + '" data-gauge="' + (c.gauge || '') + '">' + esc(c.coil_tag || c.name || 'Coil') + ' - ' + (c.gauge || '?') + 'ga - ' + (c.current_weight || c.weight || 0) + ' lbs</option>';
        });
        coilSel.innerHTML = coilOpts;

        document.getElementById('fabQty').value = 1;
        document.getElementById('fabOperator').value = '';
        document.getElementById('fabNotes').value = '';
        document.getElementById('fabCalc').style.display = 'none';
        document.getElementById('fabWarning').style.display = 'none';
        openModal('modalFab');
    };

    window.onFabPartChange = function() { updateFabCalc(); };
    window.onFabQtyChange = function() { updateFabCalc(); };
    window.onFabCoilChange = function() { updateFabCalc(); };

    function updateFabCalc() {
        var partSel = document.getElementById('fabPart');
        var opt = partSel.options[partSel.selectedIndex];
        if (!opt || !opt.value) {
            document.getElementById('fabCalc').style.display = 'none';
            return;
        }

        var gauge = opt.getAttribute('data-gauge') || '--';
        var lbsPerUnit = parseFloat(opt.getAttribute('data-lbs')) || 0;
        var qty = parseInt(document.getElementById('fabQty').value) || 0;
        var totalNeeded = lbsPerUnit * qty;

        document.getElementById('fabCalcGauge').textContent = gauge ? gauge + ' ga' : '--';
        document.getElementById('fabCalcLbs').textContent = lbsPerUnit.toFixed(2) + ' lbs';
        document.getElementById('fabCalcTotal').textContent = totalNeeded.toFixed(2) + ' lbs';

        var coilSel = document.getElementById('fabCoil');
        var coilOpt = coilSel.options[coilSel.selectedIndex];
        var avail = coilOpt && coilOpt.value ? (parseFloat(coilOpt.getAttribute('data-weight')) || 0) : 0;
        document.getElementById('fabCalcAvail').textContent = avail.toFixed(2) + ' lbs';
        var remain = avail - totalNeeded;
        document.getElementById('fabCalcRemain').textContent = remain.toFixed(2) + ' lbs';
        document.getElementById('fabCalcRemain').style.color = remain < 0 ? 'var(--tf-red)' : 'var(--tf-green)';

        document.getElementById('fabCalc').style.display = '';
        document.getElementById('fabWarning').style.display = (coilOpt && coilOpt.value && remain < 0) ? '' : 'none';
        document.getElementById('btnFabSubmit').disabled = (coilOpt && coilOpt.value && remain < 0);
    }

    window.handleFabricate = async function() {
        var partId = document.getElementById('fabPart').value;
        if (!partId) { showToast('Select a part to fabricate', 'error'); return; }
        var qty = parseInt(document.getElementById('fabQty').value) || 0;
        if (qty < 1) { showToast('Quantity must be at least 1', 'error'); return; }

        var data = {
            part_id: partId,
            quantity: qty,
            coil_id: document.getElementById('fabCoil').value || null,
            operator: document.getElementById('fabOperator').value.trim(),
            notes: document.getElementById('fabNotes').value.trim()
        };

        var btn = document.getElementById('btnFabSubmit');
        btn.disabled = true;
        btn.innerHTML = '&#9881; Fabricating...';

        try {
            await fabricateParts(data);
            closeModal('modalFab');
            showToast('Fabrication recorded! ' + qty + ' parts added.');
            await refreshAll();
        } catch(e) {
            showToast(e.message || 'Fabrication failed', 'error');
        } finally {
            btn.disabled = false;
            btn.innerHTML = '&#9881; Fabricate';
        }
    };

    // === Modal: Adjust Stock ===
    window.openAdjustModal = function(itemId) {
        var sel = document.getElementById('adjItem');
        var opts = '<option value="">Select item...</option>';
        allItems.forEach(function(it) {
            var id = it.id || it._id;
            opts += '<option value="' + id + '"' + (id === itemId ? ' selected' : '') + '>' + esc(it.name) + ' (' + (it.qty_on_hand || 0) + ' ' + (it.unit || 'ea') + ')</option>';
        });
        sel.innerHTML = opts;
        document.getElementById('adjDirection').value = '+';
        document.getElementById('adjQty').value = 1;
        document.getElementById('adjReason').value = 'count_correction';
        document.getElementById('adjNotes').value = '';
        openModal('modalAdjust');
    };

    window.handleAdjust = async function() {
        var itemId = document.getElementById('adjItem').value;
        if (!itemId) { showToast('Select an item', 'error'); return; }
        var qty = parseInt(document.getElementById('adjQty').value) || 0;
        if (qty < 1) { showToast('Quantity must be at least 1', 'error'); return; }

        var data = {
            item_id: itemId,
            direction: document.getElementById('adjDirection').value,
            quantity: qty,
            reason: document.getElementById('adjReason').value,
            notes: document.getElementById('adjNotes').value.trim()
        };

        try {
            await adjustStock(data);
            closeModal('modalAdjust');
            showToast('Stock adjusted!');
            await refreshAll();
        } catch(e) {
            showToast(e.message || 'Adjustment failed', 'error');
        }
    };

    // === Modal: Quick PO ===
    window.openPOModal = function(itemId) {
        var item = window.getItemById(itemId);
        if (!item) { showToast('Item not found', 'error'); return; }
        document.getElementById('poItemId').value = itemId;
        document.getElementById('poItemName').value = item.name || '';
        document.getElementById('poVendor').value = item.vendor || item.preferred_vendor || '';
        document.getElementById('poQty').value = item.reorder_qty || 1;
        document.getElementById('poUnitCost').value = item.cost_per_unit || 0;
        document.getElementById('poNotes').value = '';
        openModal('modalPO');
    };

    window.handleQuickPO = async function() {
        var itemId = document.getElementById('poItemId').value;
        if (!itemId) { showToast('No item selected', 'error'); return; }

        var data = {
            item_id: itemId,
            vendor: document.getElementById('poVendor').value.trim(),
            quantity: parseInt(document.getElementById('poQty').value) || 1,
            unit_cost: parseFloat(document.getElementById('poUnitCost').value) || 0,
            notes: document.getElementById('poNotes').value.trim()
        };

        try {
            await createQuickPO(data);
            closeModal('modalPO');
            showToast('Purchase Order created!');
            await refreshAll();
        } catch(e) {
            showToast(e.message || 'PO creation failed', 'error');
        }
    };

    // === Delete ===
    window.confirmDelete = async function(id) {
        var item = window.getItemById(id);
        if (!item) return;
        if (!confirm('Delete "' + (item.name || 'this item') + '"? This cannot be undone.')) return;
        try {
            await deleteItem(id);
            showToast('Item deleted.');
            await refreshAll();
        } catch(e) {
            showToast(e.message || 'Delete failed', 'error');
        }
    };

    // === Refresh ===
    async function refreshAll() {
        await loadItems();
        loadRecentActivity();
        renderCategoryChart();
    }

    // === Close modals on overlay click ===
    document.querySelectorAll('.modal-overlay').forEach(function(overlay) {
        overlay.addEventListener('click', function(e) {
            if (e.target === overlay) {
                overlay.classList.remove('active');
            }
        });
    });

    // === Close modals on Escape ===
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal-overlay.active').forEach(function(m) {
                m.classList.remove('active');
            });
        }
    });

    // === Boot ===
    init();
})();
</script>
"""
