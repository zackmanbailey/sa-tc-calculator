LOAD_BUILDER_HTML = r'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Load Builder - TitanForge</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

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
        }

        body {
            background-color: var(--bg);
            color: var(--text);
            font-family: 'Inter', system-ui, sans-serif;
            line-height: 1.6;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 24px;
        }

        /* Header */
        .header {
            margin-bottom: 32px;
        }

        .breadcrumb {
            font-size: 12px;
            color: var(--text-muted);
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .breadcrumb span {
            margin: 0 8px;
        }

        h1 {
            font-size: 32px;
            font-weight: 700;
            color: var(--text);
        }

        /* New Load Panel */
        .new-load-panel {
            background-color: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 32px;
        }

        .panel-title {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 20px;
            color: var(--accent);
        }

        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 16px;
        }

        .form-group {
            display: flex;
            flex-direction: column;
        }

        label {
            font-size: 12px;
            font-weight: 600;
            color: var(--text-muted);
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        input, select {
            background-color: var(--bg);
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 10px 12px;
            color: var(--text);
            font-family: 'Inter', system-ui, sans-serif;
            font-size: 14px;
            transition: border-color 0.2s;
        }

        input:focus, select:focus {
            outline: none;
            border-color: var(--cyan);
            box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.1);
        }

        .button-group {
            display: flex;
            gap: 12px;
            justify-content: flex-start;
        }

        button {
            padding: 10px 20px;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 600;
            border: none;
            cursor: pointer;
            transition: all 0.2s;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .btn-primary {
            background-color: var(--accent);
            color: var(--bg);
        }

        .btn-primary:hover {
            background-color: #F5C260;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(246, 174, 45, 0.3);
        }

        .btn-secondary {
            background-color: transparent;
            color: var(--cyan);
            border: 1px solid var(--cyan);
        }

        .btn-secondary:hover {
            background-color: rgba(6, 182, 212, 0.1);
        }

        .btn-danger {
            background-color: var(--red);
            color: white;
            font-size: 12px;
            padding: 6px 12px;
        }

        .btn-danger:hover {
            background-color: #DC2626;
        }

        .btn-success {
            background-color: var(--green);
            color: white;
            font-size: 12px;
            padding: 6px 12px;
        }

        .btn-success:hover {
            background-color: #059669;
        }

        /* Section Headers */
        .section {
            margin-bottom: 40px;
        }

        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            border-bottom: 2px solid var(--border);
            padding-bottom: 12px;
        }

        .section-title {
            font-size: 20px;
            font-weight: 700;
            color: var(--cyan);
        }

        /* Active Loads */
        .loads-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 32px;
        }

        .load-card {
            background-color: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 20px;
            transition: all 0.2s;
        }

        .load-card:hover {
            border-color: var(--cyan);
            box-shadow: 0 4px 12px rgba(6, 182, 212, 0.15);
        }

        .load-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 16px;
        }

        .load-title {
            font-size: 16px;
            font-weight: 700;
        }

        .load-status {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 11px;
            font-weight: 600;
            padding: 4px 8px;
            border-radius: 3px;
            text-transform: uppercase;
        }

        .status-building {
            background-color: rgba(245, 158, 11, 0.2);
            color: var(--orange);
        }

        .status-ready {
            background-color: rgba(16, 185, 129, 0.2);
            color: var(--green);
        }

        .status-shipped {
            background-color: rgba(6, 182, 212, 0.2);
            color: var(--cyan);
        }

        .status-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background-color: currentColor;
        }

        .load-details {
            background-color: var(--bg);
            border-radius: 4px;
            padding: 12px;
            margin-bottom: 16px;
            font-size: 13px;
        }

        .detail-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
        }

        .detail-row:last-child {
            margin-bottom: 0;
        }

        .detail-label {
            color: var(--text-muted);
        }

        .detail-value {
            color: var(--text);
            font-weight: 500;
        }

        .load-items {
            margin-bottom: 16px;
        }

        .items-title {
            font-size: 12px;
            font-weight: 600;
            color: var(--text-muted);
            margin-bottom: 8px;
            text-transform: uppercase;
        }

        .item-list {
            list-style: none;
            background-color: var(--bg);
            border-radius: 4px;
            max-height: 200px;
            overflow-y: auto;
        }

        .item-list-item {
            padding: 8px 10px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 13px;
        }

        .item-list-item:last-child {
            border-bottom: none;
        }

        .item-info {
            flex: 1;
        }

        .item-name {
            font-weight: 500;
        }

        .item-weight {
            font-size: 12px;
            color: var(--text-muted);
        }

        .remove-item-btn {
            background-color: transparent;
            color: var(--red);
            border: none;
            padding: 4px 8px;
            font-size: 12px;
            cursor: pointer;
            border-radius: 3px;
            transition: all 0.2s;
        }

        .remove-item-btn:hover {
            background-color: rgba(239, 68, 68, 0.1);
        }

        .load-weight {
            background-color: var(--bg);
            border-radius: 4px;
            padding: 12px;
            margin-bottom: 16px;
            text-align: center;
        }

        .weight-label {
            font-size: 11px;
            color: var(--text-muted);
            text-transform: uppercase;
            margin-bottom: 4px;
        }

        .weight-value {
            font-size: 24px;
            font-weight: 700;
            color: var(--accent);
        }

        .load-actions {
            display: flex;
            gap: 8px;
        }

        .load-actions button {
            flex: 1;
            padding: 8px 12px;
            font-size: 12px;
        }

        /* Available Items */
        .available-items {
            margin-bottom: 32px;
        }

        .items-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 16px;
        }

        .item-card {
            background-color: var(--surface);
            border: 2px solid var(--border);
            border-radius: 8px;
            padding: 16px;
            cursor: grab;
            transition: all 0.2s;
        }

        .item-card:hover {
            border-color: var(--cyan);
            box-shadow: 0 4px 12px rgba(6, 182, 212, 0.15);
        }

        .item-card.dragging {
            opacity: 0.5;
            cursor: grabbing;
        }

        .item-card-header {
            margin-bottom: 12px;
        }

        .item-card-name {
            font-size: 14px;
            font-weight: 600;
            color: var(--text);
            margin-bottom: 4px;
        }

        .item-card-id {
            font-size: 12px;
            color: var(--text-muted);
        }

        .item-card-details {
            font-size: 13px;
            color: var(--text-muted);
            margin-bottom: 12px;
        }

        .item-card-detail {
            display: flex;
            justify-content: space-between;
            margin-bottom: 4px;
        }

        .item-card-detail:last-child {
            margin-bottom: 0;
        }

        .item-card-actions {
            display: flex;
            gap: 8px;
        }

        .item-card-actions button {
            flex: 1;
            padding: 6px 12px;
            font-size: 12px;
        }

        /* Empty States */
        .empty-state {
            text-align: center;
            padding: 40px 20px;
            color: var(--text-muted);
        }

        .empty-state-icon {
            font-size: 48px;
            margin-bottom: 16px;
            opacity: 0.5;
        }

        .empty-state-text {
            font-size: 14px;
        }

        /* Alerts */
        .alert {
            padding: 12px 16px;
            border-radius: 4px;
            margin-bottom: 16px;
            font-size: 14px;
            border-left: 4px solid;
        }

        .alert-success {
            background-color: rgba(16, 185, 129, 0.1);
            border-left-color: var(--green);
            color: var(--green);
        }

        .alert-error {
            background-color: rgba(239, 68, 68, 0.1);
            border-left-color: var(--red);
            color: var(--red);
        }

        .alert-info {
            background-color: rgba(6, 182, 212, 0.1);
            border-left-color: var(--cyan);
            color: var(--cyan);
        }

        /* Loading Spinner */
        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid var(--border);
            border-top-color: var(--cyan);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        /* Responsive */
        @media (max-width: 768px) {
            .form-grid {
                grid-template-columns: 1fr;
            }

            .loads-grid {
                grid-template-columns: 1fr;
            }

            .items-grid {
                grid-template-columns: 1fr;
            }

            .button-group {
                flex-direction: column;
            }

            .button-group button {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <div class="breadcrumb">
                Dashboard <span>/</span> Load Builder
            </div>
            <h1>Load Builder</h1>
        </div>

        <!-- Alerts Container -->
        <div id="alerts-container"></div>

        <!-- New Load Panel -->
        <div class="new-load-panel">
            <div class="panel-title">Create New Load</div>
            <div class="form-grid">
                <div class="form-group">
                    <label for="project-dropdown">Project</label>
                    <select id="project-dropdown">
                        <option value="">Select Project...</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="load-number">Load #</label>
                    <input type="text" id="load-number" placeholder="Auto-generated" disabled>
                </div>
                <div class="form-group">
                    <label for="truck-number">Truck #</label>
                    <input type="text" id="truck-number" placeholder="e.g., TR-001">
                </div>
                <div class="form-group">
                    <label for="trailer-number">Trailer #</label>
                    <input type="text" id="trailer-number" placeholder="e.g., TRL-001">
                </div>
                <div class="form-group">
                    <label for="driver">Driver</label>
                    <input type="text" id="driver" placeholder="Driver name">
                </div>
                <div class="form-group">
                    <label for="load-date">Date</label>
                    <input type="date" id="load-date">
                </div>
            </div>
            <div class="button-group">
                <button class="btn-primary" onclick="createLoad()">Create Load</button>
                <button class="btn-secondary" onclick="resetLoadForm()">Reset</button>
            </div>
        </div>

        <!-- Active Loads Section -->
        <div class="section">
            <div class="section-header">
                <div class="section-title">Active Loads</div>
            </div>
            <div id="active-loads-container" class="loads-grid"></div>
        </div>

        <!-- Available Items Section -->
        <div class="section">
            <div class="section-header">
                <div class="section-title">Available Items</div>
                <div id="items-loading-indicator" style="display: none;">
                    <div class="spinner"></div>
                </div>
            </div>
            <div id="available-items-container" class="items-grid"></div>
        </div>
    </div>

    <script>
        // Initialize page on load
        document.addEventListener('DOMContentLoaded', function() {
            loadProjects();
            loadActiveLoads();
            setTodayDate();
        });

        // Set today's date as default
        function setTodayDate() {
            const today = new Date().toISOString().split('T')[0];
            document.getElementById('load-date').value = today;
        }

        // Load projects from API
        async function loadProjects() {
            try {
                const response = await fetch('/api/projects');
                const data = await response.json();
                const projectDropdown = document.getElementById('project-dropdown');

                projectDropdown.innerHTML = '<option value="">Select Project...</option>';

                if (data.projects && Array.isArray(data.projects)) {
                    data.projects.forEach(project => {
                        const option = document.createElement('option');
                        option.value = project.job_code;
                        option.textContent = `${project.job_code} - ${project.project_name}`;
                        projectDropdown.appendChild(option);
                    });
                }

                // Load available items when project changes
                projectDropdown.addEventListener('change', function() {
                    if (this.value) {
                        loadAvailableItems(this.value);
                    } else {
                        document.getElementById('available-items-container').innerHTML = '';
                    }
                });
            } catch (error) {
                showAlert('Failed to load projects', 'error');
                console.error('Error loading projects:', error);
            }
        }

        // Create a new load
        async function createLoad() {
            const jobCode = document.getElementById('project-dropdown').value;
            const truckNumber = document.getElementById('truck-number').value;
            const trailerNumber = document.getElementById('trailer-number').value;
            const driver = document.getElementById('driver').value;
            const date = document.getElementById('load-date').value;

            if (!jobCode || !truckNumber || !trailerNumber || !driver || !date) {
                showAlert('Please fill in all required fields', 'error');
                return;
            }

            try {
                const response = await fetch('/api/load-builder/create', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        job_code: jobCode,
                        truck_number: truckNumber,
                        trailer_number: trailerNumber,
                        driver: driver,
                        date: date
                    })
                });

                const data = await response.json();

                if (response.ok && data.ok) {
                    showAlert('Load created successfully', 'success');
                    resetLoadForm();
                    loadActiveLoads();
                } else {
                    showAlert(data.error || 'Failed to create load', 'error');
                }
            } catch (error) {
                showAlert('Error creating load', 'error');
                console.error('Error:', error);
            }
        }

        // Reset the load creation form
        function resetLoadForm() {
            document.getElementById('project-dropdown').value = '';
            document.getElementById('load-number').value = '';
            document.getElementById('truck-number').value = '';
            document.getElementById('trailer-number').value = '';
            document.getElementById('driver').value = '';
            setTodayDate();
            document.getElementById('available-items-container').innerHTML = '';
        }

        // Load active loads
        async function loadActiveLoads() {
            try {
                const response = await fetch('/api/load-builder/loads');
                const data = await response.json();
                const container = document.getElementById('active-loads-container');

                if (!data.ok || !data.loads || data.loads.length === 0) {
                    container.innerHTML = `
                        <div class="empty-state">
                            <div class="empty-state-icon">📦</div>
                            <div class="empty-state-text">No active loads. Create one to get started.</div>
                        </div>
                    `;
                    return;
                }

                container.innerHTML = '';
                data.loads.forEach(load => {
                    const loadCard = createLoadCard(load);
                    container.appendChild(loadCard);
                });
            } catch (error) {
                console.error('Error loading active loads:', error);
                showAlert('Failed to load active loads', 'error');
            }
        }

        // Create a load card element
        function createLoadCard(load) {
            const card = document.createElement('div');
            card.className = 'load-card';
            card.id = `load-${load.id}`;

            const statusClass = load.status === 'building' ? 'status-building' :
                               load.status === 'ready' ? 'status-ready' : 'status-shipped';

            const statusText = load.status.charAt(0).toUpperCase() + load.status.slice(1);

            const itemsHtml = load.items && load.items.length > 0
                ? load.items.map(item => `
                    <li class="item-list-item">
                        <div class="item-info">
                            <div class="item-name">${item.name || item.id}</div>
                            <div class="item-weight">${item.weight || 0} lbs</div>
                        </div>
                        <button class="remove-item-btn" onclick="removeItemFromLoad('${load.id}', '${item.id}')">×</button>
                    </li>
                `).join('')
                : '<li class="item-list-item" style="text-align: center; color: var(--text-muted);">No items</li>';

            const totalWeight = load.items ? load.items.reduce((sum, item) => sum + (item.weight || 0), 0) : 0;

            card.innerHTML = `
                <div class="load-header">
                    <div class="load-title">Load #${load.load_number}</div>
                    <div class="load-status ${statusClass}">
                        <span class="status-dot"></span>
                        ${statusText}
                    </div>
                </div>

                <div class="load-details">
                    <div class="detail-row">
                        <span class="detail-label">Truck:</span>
                        <span class="detail-value">${load.truck_number}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Trailer:</span>
                        <span class="detail-value">${load.trailer_number}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Driver:</span>
                        <span class="detail-value">${load.driver}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Date:</span>
                        <span class="detail-value">${load.date}</span>
                    </div>
                </div>

                <div class="load-items">
                    <div class="items-title">Items (${load.items ? load.items.length : 0})</div>
                    <ul class="item-list">
                        ${itemsHtml}
                    </ul>
                </div>

                <div class="load-weight">
                    <div class="weight-label">Total Weight</div>
                    <div class="weight-value">${totalWeight.toLocaleString()} lbs</div>
                </div>

                <div class="load-actions">
                    ${load.status === 'building' ? `
                        <button class="btn-success" onclick="finalizeLoad('${load.id}')">Ready</button>
                        <button class="btn-danger" onclick="deleteLoad('${load.id}')">Delete</button>
                    ` : ''}
                </div>
            `;

            return card;
        }

        // Load available items from work orders
        async function loadAvailableItems(jobCode) {
            const indicator = document.getElementById('items-loading-indicator');
            indicator.style.display = 'inline-block';

            try {
                const response = await fetch(`/api/work-orders/list?job_code=${jobCode}`);
                const data = await response.json();
                const container = document.getElementById('available-items-container');

                indicator.style.display = 'none';

                if (!data.items || data.items.length === 0) {
                    container.innerHTML = `
                        <div class="empty-state" style="grid-column: 1 / -1;">
                            <div class="empty-state-icon">📋</div>
                            <div class="empty-state-text">No items available for this project.</div>
                        </div>
                    `;
                    return;
                }

                container.innerHTML = '';
                data.items.forEach(item => {
                    const itemCard = createItemCard(item, jobCode);
                    container.appendChild(itemCard);
                });
            } catch (error) {
                indicator.style.display = 'none';
                console.error('Error loading available items:', error);
                showAlert('Failed to load available items', 'error');
            }
        }

        // Create an available item card
        function createItemCard(item, jobCode) {
            const card = document.createElement('div');
            card.className = 'item-card';
            card.draggable = true;
            card.dataset.itemId = item.id;
            card.dataset.jobCode = jobCode;

            card.innerHTML = `
                <div class="item-card-header">
                    <div class="item-card-name">${item.name || item.id}</div>
                    <div class="item-card-id">ID: ${item.id}</div>
                </div>

                <div class="item-card-details">
                    <div class="item-card-detail">
                        <span>Weight:</span>
                        <span>${item.weight || 0} lbs</span>
                    </div>
                    <div class="item-card-detail">
                        <span>Dimensions:</span>
                        <span>${item.dimensions || 'N/A'}</span>
                    </div>
                    ${item.description ? `
                        <div class="item-card-detail">
                            <span>Description:</span>
                            <span>${item.description}</span>
                        </div>
                    ` : ''}
                </div>

                <div class="item-card-actions">
                    <button class="btn-secondary" onclick="addItemToActiveLoad('${item.id}')">Add to Load</button>
                </div>
            `;

            // Drag and drop support
            card.addEventListener('dragstart', function(e) {
                card.classList.add('dragging');
                e.dataTransfer.effectAllowed = 'copy';
                e.dataTransfer.setData('itemId', item.id);
                e.dataTransfer.setData('itemData', JSON.stringify(item));
            });

            card.addEventListener('dragend', function(e) {
                card.classList.remove('dragging');
            });

            return card;
        }

        // Add item to active load (requires user to select a load)
        function addItemToActiveLoad(itemId) {
            const loads = document.querySelectorAll('[id^="load-"]');

            if (loads.length === 0) {
                showAlert('Create a load first', 'error');
                return;
            }

            if (loads.length === 1) {
                const loadId = loads[0].id.replace('load-', '');
                addItemToLoad(loadId, itemId);
                return;
            }

            // Show load selection (simple approach - show alert with first load)
            showAlert('Multiple loads exist. Implement load selection UI.', 'info');
        }

        // Add item to a specific load
        async function addItemToLoad(loadId, itemId) {
            try {
                const response = await fetch('/api/load-builder/add-item', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        load_id: loadId,
                        item_id: itemId
                    })
                });

                const data = await response.json();

                if (response.ok && data.ok) {
                    showAlert('Item added to load', 'success');
                    loadActiveLoads();
                } else {
                    showAlert(data.error || 'Failed to add item', 'error');
                }
            } catch (error) {
                showAlert('Error adding item', 'error');
                console.error('Error:', error);
            }
        }

        // Remove item from load
        async function removeItemFromLoad(loadId, itemId) {
            if (!confirm('Remove this item from the load?')) {
                return;
            }

            try {
                const response = await fetch('/api/load-builder/remove-item', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        load_id: loadId,
                        item_id: itemId
                    })
                });

                const data = await response.json();

                if (response.ok && data.ok) {
                    showAlert('Item removed', 'success');
                    loadActiveLoads();
                } else {
                    showAlert(data.error || 'Failed to remove item', 'error');
                }
            } catch (error) {
                showAlert('Error removing item', 'error');
                console.error('Error:', error);
            }
        }

        // Finalize a load
        async function finalizeLoad(loadId) {
            if (!confirm('Mark this load as ready to ship?')) {
                return;
            }

            try {
                const response = await fetch('/api/load-builder/finalize', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ load_id: loadId })
                });

                const data = await response.json();

                if (response.ok && data.ok) {
                    showAlert('Load marked as ready', 'success');
                    loadActiveLoads();
                } else {
                    showAlert(data.error || 'Failed to finalize load', 'error');
                }
            } catch (error) {
                showAlert('Error finalizing load', 'error');
                console.error('Error:', error);
            }
        }

        // Delete a load
        async function deleteLoad(loadId) {
            if (!confirm('Delete this load? This action cannot be undone.')) {
                return;
            }

            try {
                const response = await fetch('/api/load-builder/delete', {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ load_id: loadId })
                });

                const data = await response.json();

                if (response.ok && data.ok) {
                    showAlert('Load deleted', 'success');
                    loadActiveLoads();
                } else {
                    showAlert(data.error || 'Failed to delete load', 'error');
                }
            } catch (error) {
                showAlert('Error deleting load', 'error');
                console.error('Error:', error);
            }
        }

        // Show alert messages
        function showAlert(message, type = 'info') {
            const container = document.getElementById('alerts-container');
            const alert = document.createElement('div');
            alert.className = `alert alert-${type}`;
            alert.textContent = message;

            container.appendChild(alert);

            setTimeout(() => {
                alert.remove();
            }, 5000);
        }

        // Drag and drop support for load cards
        document.addEventListener('dragover', function(e) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'copy';
        });

        document.addEventListener('drop', function(e) {
            e.preventDefault();
            const loadCard = e.target.closest('.load-card');
            if (loadCard) {
                const itemId = e.dataTransfer.getData('itemId');
                const loadId = loadCard.id.replace('load-', '');
                if (itemId && loadId) {
                    addItemToLoad(loadId, itemId);
                }
            }
        });
    </script>
</body>
</html>
'''
