"""
TitanForge v4 -- Receiving Dock
=================================
Expected deliveries from open POs, check-in workflow with PO matching, damage inspection,
weight verification, discrepancy detection, inventory auto-update, put-away assignment.
"""

RECEIVING_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a;
        --tf-card: #1e293b;
        --tf-text: #e2e8f0;
        --tf-muted: #94a3b8;
        --tf-gold: #d4a843;
        --tf-blue: #3b82f6;
        --tf-green: #10b981;
        --tf-red: #ef4444;
        --tf-orange: #f59e0b;
    }
    .recv-container {
        max-width: 1400px; margin: 0 auto; padding: 24px 32px;
        font-family: 'Inter', system-ui, -apple-system, sans-serif; color: var(--tf-text);
    }
    .page-header { margin-bottom: 28px; }
    .page-header h1 { font-size: 28px; font-weight: 800; margin: 0 0 6px 0; }
    .page-header p { font-size: 14px; color: var(--tf-muted); margin: 0; }

    .stat-row {
        display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px; margin-bottom: 24px;
    }
    .stat-card {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06);
        padding: 20px 24px; cursor: pointer; transition: border-color 0.2s, transform 0.15s;
    }
    .stat-card:hover { border-color: var(--tf-gold); transform: translateY(-2px); }
    .stat-card .label { font-size: 12px; color: var(--tf-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
    .stat-card .value { font-size: 28px; font-weight: 800; }
    .stat-gold .value { color: var(--tf-gold); }
    .stat-blue .value { color: var(--tf-blue); }
    .stat-green .value { color: var(--tf-green); }
    .stat-red .value { color: var(--tf-red); }
    .stat-orange .value { color: var(--tf-orange); }

    .toolbar {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 20px; flex-wrap: wrap; gap: 12px;
    }
    .toolbar-left { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
    .toolbar input[type="text"], .toolbar input[type="date"], .toolbar select {
        background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06);
        border-radius: 8px; padding: 10px 16px; color: var(--tf-text); font-size: 14px;
    }
    .toolbar input:focus, .toolbar select:focus { outline: none; border-color: var(--tf-blue); }
    .btn {
        padding: 10px 20px; border: none; border-radius: 8px; font-size: 14px;
        font-weight: 600; cursor: pointer; transition: all 0.2s;
    }
    .btn-primary { background: var(--tf-gold); color: #0f172a; }
    .btn-primary:hover { background: #e0b44e; transform: translateY(-1px); }
    .btn-secondary { background: var(--tf-card); color: var(--tf-text); border: 1px solid rgba(255,255,255,0.06); }
    .btn-secondary:hover { border-color: var(--tf-blue); }
    .btn-sm { padding: 6px 14px; font-size: 12px; }
    .btn-success { background: var(--tf-green); color: #fff; }
    .btn-success:hover { background: #0ea572; }
    .btn-danger { background: var(--tf-red); color: #fff; }

    /* Expected deliveries from POs */
    .section-title { font-size: 16px; font-weight: 700; margin: 24px 0 12px 0; display: flex; align-items: center; gap: 8px; }
    .section-title .count { background: rgba(59,130,246,0.15); color: var(--tf-blue); padding: 2px 10px; border-radius: 10px; font-size: 12px; }

    .delivery-cards {
        display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
        gap: 16px; margin-bottom: 24px;
    }
    .delivery-card {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06); padding: 20px 24px;
        transition: border-color 0.2s, transform 0.15s;
    }
    .delivery-card:hover { border-color: var(--tf-blue); transform: translateY(-2px); }
    .delivery-card.from-po { border-left: 3px solid var(--tf-blue); }
    .delivery-card .card-header {
        display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;
    }
    .delivery-card .card-header h3 { font-size: 16px; font-weight: 700; margin: 0; }
    .delivery-card .card-detail { font-size: 13px; color: var(--tf-muted); margin-bottom: 6px; }
    .delivery-card .card-detail strong { color: var(--tf-text); }
    .delivery-card .card-actions { display: flex; gap: 8px; margin-top: 14px; }
    .delivery-card .po-items { margin-top: 8px; padding: 8px 12px; background: rgba(0,0,0,0.15); border-radius: 8px; font-size: 12px; }
    .delivery-card .po-items .item-line { display: flex; justify-content: space-between; padding: 3px 0; border-bottom: 1px solid rgba(255,255,255,0.04); }
    .delivery-card .po-items .item-line:last-child { border-bottom: none; }

    .badge {
        display: inline-block; padding: 4px 10px; border-radius: 6px;
        font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.3px;
    }
    .badge-expected { background: rgba(59,130,246,0.15); color: var(--tf-blue); }
    .badge-arrived { background: rgba(245,158,11,0.15); color: var(--tf-orange); }
    .badge-inspecting { background: rgba(212,168,67,0.15); color: var(--tf-gold); }
    .badge-checked-in { background: rgba(16,185,129,0.15); color: var(--tf-green); }
    .badge-rejected { background: rgba(239,68,68,0.15); color: var(--tf-red); }
    .badge-put-away { background: rgba(148,163,184,0.15); color: var(--tf-muted); }
    .badge-open { background: rgba(59,130,246,0.15); color: var(--tf-blue); }

    .data-table {
        width: 100%; border-collapse: collapse; background: var(--tf-card);
        border-radius: 12px; overflow: hidden; border: 1px solid rgba(255,255,255,0.06);
    }
    .data-table th {
        padding: 14px 16px; text-align: left; font-size: 11px; font-weight: 700;
        color: var(--tf-muted); text-transform: uppercase; letter-spacing: 0.5px;
        background: rgba(0,0,0,0.2); border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .data-table td {
        padding: 14px 16px; font-size: 14px; border-bottom: 1px solid rgba(255,255,255,0.04);
    }
    .data-table tbody tr { cursor: pointer; transition: background 0.15s; }
    .data-table tbody tr:hover { background: rgba(59,130,246,0.06); }

    .empty-state {
        text-align: center; padding: 60px 20px; color: var(--tf-muted);
    }
    .empty-state .icon { font-size: 48px; margin-bottom: 16px; opacity: 0.5; }
    .empty-state h3 { font-size: 18px; color: var(--tf-text); margin-bottom: 8px; }
    .empty-state p { font-size: 14px; max-width: 400px; margin: 0 auto 20px; }

    .modal-overlay {
        display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6);
        z-index: 1000; justify-content: center; align-items: center;
    }
    .modal-overlay.active { display: flex; }
    .modal {
        background: var(--tf-card); border-radius: 16px; padding: 32px;
        width: 90%; max-width: 700px; border: 1px solid rgba(255,255,255,0.1);
        max-height: 85vh; overflow-y: auto;
    }
    .modal h2 { font-size: 20px; font-weight: 700; margin: 0 0 24px 0; }
    .form-group { margin-bottom: 18px; }
    .form-group label { display: block; font-size: 12px; font-weight: 600; color: var(--tf-muted); text-transform: uppercase; margin-bottom: 6px; }
    .form-group input, .form-group select, .form-group textarea {
        width: 100%; background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px;
    }
    .form-group input:focus, .form-group select:focus { outline: none; border-color: var(--tf-blue); }
    .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 24px; }

    .checklist { list-style: none; padding: 0; margin: 12px 0; }
    .checklist li {
        padding: 10px 14px; background: var(--tf-bg); border-radius: 8px; margin-bottom: 6px;
        display: flex; align-items: center; gap: 10px; font-size: 14px;
        border: 1px solid rgba(255,255,255,0.06);
    }
    .checklist li input[type="checkbox"] { width: 18px; height: 18px; accent-color: var(--tf-green); }

    /* Receive items table in modal */
    .receive-items-table { width: 100%; border-collapse: collapse; margin-top: 8px; }
    .receive-items-table th { padding: 8px 10px; font-size: 11px; color: var(--tf-muted); text-transform: uppercase; text-align: left; background: rgba(0,0,0,0.15); }
    .receive-items-table td { padding: 8px 10px; font-size: 13px; border-bottom: 1px solid rgba(255,255,255,0.04); }
    .receive-items-table input { background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08); border-radius: 6px; padding: 6px 8px; color: var(--tf-text); font-size: 13px; width: 80px; }
    .discrepancy-flag { color: var(--tf-red); font-weight: 700; font-size: 12px; }

/* Responsive */
@media (max-width: 768px) {
    .page-header h1 { font-size: 22px; }
    .toolbar { flex-direction: column; align-items: stretch; }
    .toolbar input[type="text"] { width: 100%; }
    .stat-row, .delivery-cards { grid-template-columns: 1fr 1fr; gap: 10px; }
    table { display: block; overflow-x: auto; -webkit-overflow-scrolling: touch; }
    .modal-overlay .modal, .modal { width: 95%; max-width: 95vw; margin: 20px auto; padding: 20px; }
    .form-row { grid-template-columns: 1fr; }
    .delivery-cards { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 480px) {
    .stat-row, .delivery-cards { grid-template-columns: 1fr; }
    .toolbar { gap: 8px; }
    .delivery-cards { grid-template-columns: 1fr; }
}
</style>

<div class="recv-container">
    <div class="page-header">
        <h1>Receiving Dock</h1>
        <p>Expected deliveries from open POs, check-in workflow, inspection, and put-away</p>
    </div>

    <div class="stat-row">
        <div class="stat-card stat-blue">
            <div class="label">Expected from POs</div>
            <div class="value" id="stat-expected">0</div>
        </div>
        <div class="stat-card stat-orange">
            <div class="label">Arrived Today</div>
            <div class="value" id="stat-arrived">0</div>
        </div>
        <div class="stat-card stat-green">
            <div class="label">Checked In</div>
            <div class="value" id="stat-checkedin">0</div>
        </div>
        <div class="stat-card stat-red">
            <div class="label">Discrepancies</div>
            <div class="value" id="stat-issues">0</div>
        </div>
    </div>

    <div class="toolbar">
        <div class="toolbar-left">
            <input type="text" id="search-input" placeholder="Search deliveries..." oninput="filterData()">
            <select id="status-filter" onchange="filterData()">
                <option value="">All Statuses</option>
                <option value="expected">Expected</option>
                <option value="arrived">Arrived</option>
                <option value="inspecting">Inspecting</option>
                <option value="checked-in">Checked In</option>
                <option value="put-away">Put Away</option>
                <option value="rejected">Rejected</option>
            </select>
        </div>
        <button class="btn btn-primary" onclick="openNewDelivery()">+ Log Delivery</button>
    </div>

    <!-- Expected Deliveries from Open POs -->
    <div class="section-title" id="expected-title" style="display:none;">
        Expected Deliveries (from Open POs) <span class="count" id="expected-count">0</span>
    </div>
    <div class="delivery-cards" id="expected-cards"></div>

    <!-- Recent Deliveries -->
    <div class="section-title">
        Receiving Log <span class="count" id="log-count">0</span>
    </div>
    <div id="table-container">
        <table class="data-table">
            <thead>
                <tr>
                    <th>Delivery #</th>
                    <th>PO Number</th>
                    <th>Vendor</th>
                    <th>Date</th>
                    <th>Items</th>
                    <th>Discrepancies</th>
                    <th>Status</th>
                    <th>Location</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody id="recv-tbody"></tbody>
        </table>
        <div class="empty-state" id="empty-state">
            <div class="icon">&#x1F69B;</div>
            <h3>No Deliveries Recorded</h3>
            <p>Log incoming deliveries and match them against open purchase orders.</p>
            <button class="btn btn-primary" onclick="openNewDelivery()">+ Log Delivery</button>
        </div>
    </div>
</div>

<!-- Check-In Modal -->
<div class="modal-overlay" id="recv-modal">
    <div class="modal">
        <h2 id="modal-title">Log Delivery</h2>
        <input type="hidden" id="recv-edit-id" value="">

        <div class="form-row">
            <div class="form-group">
                <label>PO Number</label>
                <select id="recv-po" onchange="onPOSelect()">
                    <option value="">Select PO (optional)...</option>
                </select>
            </div>
            <div class="form-group">
                <label>Vendor</label>
                <input type="text" id="recv-vendor" placeholder="Vendor name">
            </div>
        </div>

        <!-- PO Line Items for receiving -->
        <div id="po-items-section" style="display:none;">
            <div class="form-group">
                <label>Receive Items (from PO)</label>
                <table class="receive-items-table" id="recv-items-table">
                    <thead><tr><th>Item</th><th>Ordered</th><th>Received</th><th>This Delivery</th><th>Discrepancy</th></tr></thead>
                    <tbody id="recv-items-body"></tbody>
                </table>
            </div>
        </div>

        <div class="form-row">
            <div class="form-group">
                <label>Carrier</label>
                <input type="text" id="recv-carrier" placeholder="Trucking company">
            </div>
            <div class="form-group">
                <label>BOL Number</label>
                <input type="text" id="recv-bol" placeholder="Bill of lading #">
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Expected Weight (lbs)</label>
                <input type="number" id="recv-exp-weight" placeholder="0">
            </div>
            <div class="form-group">
                <label>Actual Weight (lbs)</label>
                <input type="number" id="recv-act-weight" placeholder="Weigh on arrival">
            </div>
        </div>
        <div class="form-group">
            <label>Inspection Checklist</label>
            <ul class="checklist">
                <li><input type="checkbox" id="chk-1"><span>Packing slip matches PO</span></li>
                <li><input type="checkbox" id="chk-2"><span>Material matches description</span></li>
                <li><input type="checkbox" id="chk-3"><span>No visible damage</span></li>
                <li><input type="checkbox" id="chk-4"><span>Weight verified (within 2%)</span></li>
                <li><input type="checkbox" id="chk-5"><span>MTR / Mill Certs received</span></li>
                <li><input type="checkbox" id="chk-6"><span>Heat numbers recorded</span></li>
            </ul>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Put-Away Location</label>
                <input type="text" id="recv-location" placeholder="e.g., Bay 3, Rack A-2">
            </div>
            <div class="form-group">
                <label>Heat Number (if applicable)</label>
                <input type="text" id="recv-heat" placeholder="e.g., H-84729">
            </div>
        </div>
        <div class="form-group">
            <label>Notes / Discrepancy Details</label>
            <textarea id="recv-notes" rows="3" placeholder="Inspection notes, damage details, discrepancies..."></textarea>
        </div>
        <div class="modal-actions">
            <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
            <button class="btn btn-danger" id="btn-reject" style="display:none;" onclick="rejectDelivery()">Reject</button>
            <button class="btn btn-success" onclick="checkInDelivery()">Check In &amp; Update Inventory</button>
        </div>
    </div>
</div>

<!-- Detail Modal -->
<div class="modal-overlay" id="detail-modal">
    <div class="modal" style="max-width:750px;">
        <h2 id="detail-title">Delivery Details</h2>
        <div id="detail-content"></div>
        <div class="modal-actions">
            <button class="btn btn-secondary" onclick="document.getElementById('detail-modal').classList.remove('active')">Close</button>
        </div>
    </div>
</div>

<script>
let deliveries = [];
let expectedDeliveries = [];
let openPOs = [];

async function loadData() {
    try {
        const resp = await fetch('/api/receiving');
        const data = await resp.json();
        deliveries = data.deliveries || data.receiving_records || [];
        expectedDeliveries = data.expected_deliveries || [];
        renderExpectedCards();
        renderTable();
        updateStats();
        loadOpenPOs();
    } catch(e) { console.error('Failed to load deliveries:', e); renderTable(); }
}

async function loadOpenPOs() {
    try {
        const resp = await fetch('/api/pos');
        const data = await resp.json();
        openPOs = (data.purchase_orders || []).filter(p => ['sent','acknowledged','partial'].includes(p.status));
        const sel = document.getElementById('recv-po');
        const first = sel.options[0].outerHTML;
        sel.innerHTML = first + openPOs.map(p =>
            `<option value="${p.po_number || p.id}">${p.po_number || p.id} - ${p.vendor || 'Unknown'} ($${(parseFloat(p.total) || parseFloat(p.grand_total) || 0).toFixed(2)})</option>`
        ).join('');
    } catch(e) { console.error('Failed to load POs:', e); }
}

function updateStats() {
    document.getElementById('stat-expected').textContent = expectedDeliveries.length;
    document.getElementById('stat-arrived').textContent = deliveries.filter(d => {
        const date = (d.received_date || d.arrived_date || d.created || '').slice(0,10);
        const today = new Date().toISOString().slice(0,10);
        return date === today;
    }).length;
    document.getElementById('stat-checkedin').textContent = deliveries.filter(d => d.status === 'checked-in' || d.status === 'put-away').length;
    document.getElementById('stat-issues').textContent = deliveries.filter(d => (d.discrepancies || []).length > 0).length;
}

function renderExpectedCards() {
    const container = document.getElementById('expected-cards');
    const title = document.getElementById('expected-title');
    const countEl = document.getElementById('expected-count');
    if (expectedDeliveries.length === 0) { container.innerHTML = ''; title.style.display = 'none'; return; }
    title.style.display = 'flex';
    countEl.textContent = expectedDeliveries.length;
    container.innerHTML = expectedDeliveries.map(d => {
        const items = d.line_items || d.items || [];
        let itemsHtml = '';
        if (items.length > 0) {
            itemsHtml = `<div class="po-items">${items.slice(0,4).map(it =>
                `<div class="item-line"><span>${it.description || '--'}</span><span>${it.quantity || 0} ${it.unit || 'ea'}</span></div>`
            ).join('')}${items.length > 4 ? `<div style="color:var(--tf-muted);font-style:italic;padding-top:4px">+${items.length-4} more items</div>` : ''}</div>`;
        }
        return `<div class="delivery-card from-po">
            <div class="card-header">
                <h3>${d.po_number || 'No PO'}</h3>
                <span class="badge badge-open">Expected</span>
            </div>
            <div class="card-detail"><strong>Vendor:</strong> ${d.vendor || '--'}</div>
            <div class="card-detail"><strong>Delivery Date:</strong> ${d.delivery_date || '--'}</div>
            <div class="card-detail"><strong>Total:</strong> $${(parseFloat(d.total) || parseFloat(d.grand_total) || 0).toLocaleString()}</div>
            ${itemsHtml}
            <div class="card-actions">
                <button class="btn btn-sm btn-success" onclick="beginCheckIn('${d.po_number || ''}')">Receive Delivery</button>
            </div>
        </div>`;
    }).join('');
}

function renderTable() {
    const tbody = document.getElementById('recv-tbody');
    const empty = document.getElementById('empty-state');
    const filtered = getFiltered();
    document.getElementById('log-count').textContent = filtered.length;
    if (filtered.length === 0) { tbody.innerHTML = ''; empty.style.display = 'block'; return; }
    empty.style.display = 'none';
    tbody.innerHTML = filtered.map(d => {
        const discCount = (d.discrepancies || []).length;
        const itemCount = (d.items_received || d.line_items || []).length;
        return `<tr onclick="viewDelivery('${d.id}')">
            <td><strong>${d.delivery_number || d.id || '--'}</strong></td>
            <td>${d.po_number || '--'}</td>
            <td>${d.vendor || '--'}</td>
            <td>${(d.received_date || d.arrived_date || d.created || '').slice(0,10)}</td>
            <td>${itemCount}</td>
            <td>${discCount > 0 ? `<span class="discrepancy-flag">${discCount} issue${discCount > 1 ? 's' : ''}</span>` : '<span style="color:var(--tf-green)">None</span>'}</td>
            <td><span class="badge badge-${(d.status || 'checked-in').replace(' ','-')}">${(d.status || 'checked-in').replace(/-/g,' ')}</span></td>
            <td>${d.location || d.put_away_location || '--'}</td>
            <td><button class="btn btn-sm btn-secondary" onclick="event.stopPropagation();viewDelivery('${d.id}')">View</button></td>
        </tr>`;
    }).join('');
}

function getFiltered() {
    const search = (document.getElementById('search-input').value || '').toLowerCase();
    const status = document.getElementById('status-filter').value;
    return deliveries.filter(d => {
        if (search && !JSON.stringify(d).toLowerCase().includes(search)) return false;
        if (status && d.status !== status) return false;
        return true;
    });
}

function filterData() { renderTable(); }

function openNewDelivery() {
    document.getElementById('modal-title').textContent = 'Log Delivery';
    document.getElementById('recv-edit-id').value = '';
    document.getElementById('recv-po').value = '';
    document.getElementById('recv-vendor').value = '';
    document.getElementById('recv-carrier').value = '';
    document.getElementById('recv-bol').value = '';
    document.getElementById('recv-exp-weight').value = '';
    document.getElementById('recv-act-weight').value = '';
    document.getElementById('recv-location').value = '';
    document.getElementById('recv-heat').value = '';
    document.getElementById('recv-notes').value = '';
    document.getElementById('po-items-section').style.display = 'none';
    document.querySelectorAll('.checklist input[type=checkbox]').forEach(c => c.checked = false);
    document.getElementById('btn-reject').style.display = 'none';
    document.getElementById('recv-modal').classList.add('active');
}

function closeModal() { document.getElementById('recv-modal').classList.remove('active'); }

function beginCheckIn(poNumber) {
    openNewDelivery();
    document.getElementById('modal-title').textContent = 'Receive Delivery - ' + poNumber;
    document.getElementById('btn-reject').style.display = 'inline-block';
    // Select the PO
    const sel = document.getElementById('recv-po');
    for (let i = 0; i < sel.options.length; i++) {
        if (sel.options[i].value === poNumber) { sel.selectedIndex = i; break; }
    }
    onPOSelect();
}

function onPOSelect() {
    const poNum = document.getElementById('recv-po').value;
    const section = document.getElementById('po-items-section');
    if (!poNum) { section.style.display = 'none'; return; }

    const po = openPOs.find(p => (p.po_number || p.id) === poNum);
    if (!po) { section.style.display = 'none'; return; }

    // Auto-fill vendor
    if (po.vendor) document.getElementById('recv-vendor').value = po.vendor;

    const items = po.line_items || po.items || [];
    if (items.length === 0) { section.style.display = 'none'; return; }

    section.style.display = 'block';
    const tbody = document.getElementById('recv-items-body');
    tbody.innerHTML = items.map((item, i) => {
        const ordered = item.quantity || item.qty || 0;
        const prevReceived = item.received || 0;
        return `<tr>
            <td>${item.description || '--'}</td>
            <td>${ordered} ${item.unit || 'ea'}</td>
            <td>${prevReceived}</td>
            <td><input type="number" class="recv-qty" data-idx="${i}" data-ordered="${ordered}" placeholder="0" oninput="checkDiscrepancy(this)"></td>
            <td class="disc-cell" id="disc-${i}"></td>
        </tr>`;
    }).join('');
}

function checkDiscrepancy(el) {
    const idx = el.dataset.idx;
    const ordered = parseFloat(el.dataset.ordered) || 0;
    const received = parseFloat(el.value) || 0;
    const cell = document.getElementById('disc-' + idx);
    if (received > 0 && received !== ordered) {
        const diff = received - ordered;
        cell.innerHTML = `<span class="discrepancy-flag">${diff > 0 ? '+' : ''}${diff}</span>`;
    } else {
        cell.innerHTML = '';
    }
}

async function checkInDelivery() {
    const poNumber = document.getElementById('recv-po').value;
    const vendor = document.getElementById('recv-vendor').value;

    // Collect received items
    const receivedItems = [];
    const discrepancies = [];
    document.querySelectorAll('#recv-items-body tr').forEach(row => {
        const input = row.querySelector('.recv-qty');
        if (!input) return;
        const idx = parseInt(input.dataset.idx);
        const ordered = parseFloat(input.dataset.ordered) || 0;
        const qty = parseFloat(input.value) || 0;
        const desc = row.querySelector('td').textContent;
        if (qty > 0) {
            receivedItems.push({ description: desc, quantity_received: qty, quantity_ordered: ordered });
            if (qty !== ordered) {
                discrepancies.push({
                    item: desc,
                    ordered: ordered,
                    received: qty,
                    difference: qty - ordered,
                    type: qty < ordered ? 'short' : 'over'
                });
            }
        }
    });

    // Collect checklist
    const inspection = {};
    ['chk-1','chk-2','chk-3','chk-4','chk-5','chk-6'].forEach(id => {
        inspection[id] = document.getElementById(id).checked;
    });

    const payload = {
        po_number: poNumber,
        vendor: vendor,
        carrier: document.getElementById('recv-carrier').value,
        bol_number: document.getElementById('recv-bol').value,
        expected_weight: parseFloat(document.getElementById('recv-exp-weight').value) || 0,
        actual_weight: parseFloat(document.getElementById('recv-act-weight').value) || 0,
        location: document.getElementById('recv-location').value,
        heat_number: document.getElementById('recv-heat').value,
        notes: document.getElementById('recv-notes').value,
        items_received: receivedItems,
        discrepancies: discrepancies,
        inspection: inspection,
        status: 'checked-in',
    };

    try {
        const resp = await fetch('/api/receiving', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify(payload)
        });
        const data = await resp.json();
        if (data.error) { showToast(data.error, 'error'); return; }
        closeModal();
        const msg = discrepancies.length > 0
            ? 'Delivery checked in with ' + discrepancies.length + ' discrepanc' + (discrepancies.length > 1 ? 'ies' : 'y')
            : 'Delivery checked in successfully';
        showToast(msg, discrepancies.length > 0 ? 'warning' : 'success');
        loadData();
    } catch(e) { showToast('Check-in failed', 'error'); }
}

async function rejectDelivery() {
    const payload = {
        po_number: document.getElementById('recv-po').value,
        vendor: document.getElementById('recv-vendor').value,
        notes: document.getElementById('recv-notes').value || 'Delivery rejected',
        status: 'rejected',
        discrepancies: [{ type: 'rejected', reason: document.getElementById('recv-notes').value || 'Rejected on inspection' }],
    };
    try {
        await fetch('/api/receiving', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
        closeModal();
        showToast('Delivery rejected', 'error');
        loadData();
    } catch(e) { showToast('Reject failed', 'error'); }
}

function viewDelivery(id) {
    const d = deliveries.find(x => x.id === id);
    if (!d) return;
    const items = d.items_received || d.line_items || [];
    const discs = d.discrepancies || [];

    let html = `
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px;">
            <div><span style="font-size:11px;color:var(--tf-muted);text-transform:uppercase">Delivery #</span><div style="font-weight:700">${d.delivery_number || d.id}</div></div>
            <div><span style="font-size:11px;color:var(--tf-muted);text-transform:uppercase">PO Number</span><div style="font-weight:700">${d.po_number || '--'}</div></div>
            <div><span style="font-size:11px;color:var(--tf-muted);text-transform:uppercase">Vendor</span><div>${d.vendor || '--'}</div></div>
            <div><span style="font-size:11px;color:var(--tf-muted);text-transform:uppercase">Date</span><div>${(d.received_date || d.arrived_date || d.created || '').slice(0,10)}</div></div>
            <div><span style="font-size:11px;color:var(--tf-muted);text-transform:uppercase">Carrier</span><div>${d.carrier || '--'}</div></div>
            <div><span style="font-size:11px;color:var(--tf-muted);text-transform:uppercase">Location</span><div>${d.location || d.put_away_location || '--'}</div></div>
            <div><span style="font-size:11px;color:var(--tf-muted);text-transform:uppercase">Exp. Weight</span><div>${(d.expected_weight || 0).toLocaleString()} lbs</div></div>
            <div><span style="font-size:11px;color:var(--tf-muted);text-transform:uppercase">Act. Weight</span><div>${(d.actual_weight || 0).toLocaleString()} lbs</div></div>
        </div>`;

    if (items.length > 0) {
        html += `<div style="margin-bottom:16px;"><div style="font-size:12px;font-weight:700;color:var(--tf-gold);text-transform:uppercase;margin-bottom:8px;">Items Received</div>
            <table class="receive-items-table" style="border-radius:8px;overflow:hidden;border:1px solid rgba(255,255,255,0.06);">
                <thead><tr><th>Item</th><th>Ordered</th><th>Received</th></tr></thead>
                <tbody>${items.map(it => `<tr><td>${it.description || '--'}</td><td>${it.quantity_ordered || '--'}</td><td>${it.quantity_received || '--'}</td></tr>`).join('')}</tbody>
            </table></div>`;
    }

    if (discs.length > 0) {
        html += `<div style="margin-bottom:16px;"><div style="font-size:12px;font-weight:700;color:var(--tf-red);text-transform:uppercase;margin-bottom:8px;">Discrepancies</div>
            <div style="background:rgba(239,68,68,0.08);border-radius:8px;padding:12px;border:1px solid rgba(239,68,68,0.2);">
            ${discs.map(disc => `<div style="margin-bottom:6px;font-size:13px;">
                <strong>${disc.item || disc.type || '--'}:</strong> ${disc.type === 'short' ? 'Short ' + Math.abs(disc.difference) : disc.type === 'over' ? 'Over ' + disc.difference : disc.reason || JSON.stringify(disc)}
            </div>`).join('')}</div></div>`;
    }

    if (d.notes) {
        html += `<div><div style="font-size:12px;font-weight:700;color:var(--tf-muted);text-transform:uppercase;margin-bottom:4px;">Notes</div><p style="color:var(--tf-muted);font-size:14px;">${d.notes}</p></div>`;
    }

    document.getElementById('detail-title').innerHTML = `Delivery ${d.delivery_number || d.id} <span class="badge badge-${(d.status || 'checked-in').replace(' ','-')}" style="font-size:12px;vertical-align:middle;margin-left:8px;">${(d.status || 'checked-in').replace(/-/g,' ')}</span>`;
    document.getElementById('detail-content').innerHTML = html;
    document.getElementById('detail-modal').classList.add('active');
}

function showToast(msg, type) {
    const existing = document.querySelector('.toast-notification');
    if (existing) existing.remove();
    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    const bg = type === 'error' ? 'var(--tf-red)' : type === 'success' ? 'var(--tf-green)' : type === 'warning' ? 'var(--tf-orange)' : 'var(--tf-blue)';
    toast.style.cssText = `position:fixed;top:20px;right:20px;z-index:9999;background:${bg};color:#fff;padding:14px 24px;border-radius:10px;font-size:14px;font-weight:600;box-shadow:0 4px 20px rgba(0,0,0,0.3);transition:opacity 0.3s;`;
    toast.textContent = msg;
    document.body.appendChild(toast);
    setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 300); }, 3000);
}

document.addEventListener('DOMContentLoaded', loadData);
</script>
"""
