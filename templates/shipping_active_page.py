"""
TitanForge v4 — Active Shipments
===================================
Active shipment cards with status tracking, delivery confirmation,
status update buttons (departed, in-transit, delivered).
Wired to ShippingActiveAPIHandler.
"""

SHIPPING_ACTIVE_PAGE_HTML = r"""
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
    .ship-container {
        max-width: 1400px; margin: 0 auto; padding: 24px 32px;
        font-family: 'Inter', system-ui, -apple-system, sans-serif; color: var(--tf-text);
    }
    .page-header { margin-bottom: 32px; }
    .page-header h1 { font-size: 28px; font-weight: 800; margin: 0 0 6px 0; }
    .page-header p { font-size: 14px; color: var(--tf-muted); margin: 0; }
    .toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
    .toolbar input[type="text"] { background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px 16px; color: var(--tf-text); font-size: 14px; width: 260px; }
    .toolbar input::placeholder { color: var(--tf-muted); }
    .toolbar select { background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px; }
    .btn-gold { background: var(--tf-gold); color: #0f172a; border: none; border-radius: 8px; padding: 10px 20px; font-weight: 700; font-size: 14px; cursor: pointer; }
    .btn-gold:hover { opacity: 0.9; }
    .btn-blue { background: var(--tf-blue); color: #fff; border: none; border-radius: 8px; padding: 10px 20px; font-weight: 700; font-size: 14px; cursor: pointer; }
    .btn-green { background: var(--tf-green); color: #fff; border: none; border-radius: 8px; padding: 10px 20px; font-weight: 700; font-size: 14px; cursor: pointer; }
    .btn-outline { background: transparent; color: var(--tf-muted); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 10px 20px; font-weight: 600; font-size: 14px; cursor: pointer; }
    .btn-outline:hover { border-color: var(--tf-gold); color: var(--tf-gold); }
    .btn-sm { padding: 6px 14px; font-size: 12px; border-radius: 6px; }
    .stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
    @media (max-width: 900px) { .stats-row { grid-template-columns: 1fr 1fr; } }
    .stat-card { background: var(--tf-card); border-radius: 10px; padding: 18px; border: 1px solid rgba(255,255,255,0.06); }
    .stat-card .stat-label { font-size: 12px; color: var(--tf-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
    .stat-card .stat-value { font-size: 24px; font-weight: 800; }
    .shipment-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); gap: 16px; }
    .shipment-card {
        background: var(--tf-card); border-radius: 12px; border: 1px solid rgba(255,255,255,0.06);
        padding: 20px; transition: border-color 0.2s;
    }
    .shipment-card:hover { border-color: var(--tf-blue); }
    .shipment-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
    .shipment-header h3 { font-size: 16px; font-weight: 700; margin: 0; }
    .shipment-route { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; font-size: 13px; }
    .route-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
    .route-dot.origin { background: var(--tf-blue); }
    .route-dot.dest { background: #4ade80; }
    .route-line { flex: 1; height: 2px; background: linear-gradient(90deg, var(--tf-blue), #4ade80); }
    .shipment-details { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 13px; margin-bottom: 12px; }
    .shipment-details .detail-label { color: var(--tf-muted); }
    .shipment-details .detail-value { font-weight: 600; text-align: right; }
    .badge { display: inline-block; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
    .badge-loading { background: rgba(212,168,67,0.2); color: var(--tf-gold); }
    .badge-departed { background: rgba(245,158,11,0.2); color: var(--tf-orange); }
    .badge-in_transit { background: rgba(59,130,246,0.2); color: #60a5fa; }
    .badge-delivered { background: rgba(34,197,94,0.2); color: #4ade80; }
    .badge-delayed { background: rgba(239,68,68,0.2); color: #f87171; }
    .progress-bar { height: 4px; background: rgba(255,255,255,0.08); border-radius: 2px; margin-bottom: 12px; }
    .progress-fill { height: 100%; border-radius: 2px; background: var(--tf-blue); }
    .card-actions { display: flex; gap: 8px; flex-wrap: wrap; }
    .empty-state { text-align: center; padding: 60px 20px; color: var(--tf-muted); grid-column: 1 / -1; }
    .empty-state h3 { font-size: 18px; margin-bottom: 8px; color: var(--tf-text); }
    .loading { text-align: center; padding: 40px; color: var(--tf-muted); grid-column: 1 / -1; }

    /* Modal */
    .modal-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 1000; justify-content: center; align-items: center; }
    .modal-overlay.active { display: flex; }
    .modal { background: var(--tf-card); border-radius: 12px; padding: 28px; width: 560px; max-width: 90vw; border: 1px solid rgba(255,255,255,0.1); max-height: 85vh; overflow-y: auto; }
    .modal h2 { font-size: 20px; margin: 0 0 20px 0; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 24px; }
    .form-group { margin-bottom: 16px; }
    .form-group label { display: block; font-size: 13px; font-weight: 600; color: var(--tf-muted); margin-bottom: 6px; }
    .form-group input, .form-group select, .form-group textarea {
        width: 100%; background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px; font-family: inherit; box-sizing: border-box;
    }
    .form-group textarea { min-height: 60px; resize: vertical; }
    .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .delivery-confirm {
        background: rgba(34,197,94,0.08); border: 1px solid rgba(34,197,94,0.2); border-radius: 12px;
        padding: 20px; margin-top: 16px;
    }
    .delivery-confirm h4 { font-size: 15px; font-weight: 700; color: var(--tf-green); margin: 0 0 12px 0; }

    @media (max-width: 768px) {
        .ship-container { padding: 16px; }
        .toolbar { flex-direction: column; align-items: stretch; }
        .toolbar input[type="text"] { width: 100%; }
        .shipment-grid { grid-template-columns: 1fr; }
        .form-row { grid-template-columns: 1fr; }
    }
</style>

<div class="ship-container">
    <div class="page-header">
        <h1>Active Shipments</h1>
        <p>Track in-transit loads, update delivery status, confirm deliveries, and manage carrier info</p>
    </div>
    <div class="stats-row">
        <div class="stat-card"><div class="stat-label">Loading</div><div class="stat-value" id="statLoading" style="color:var(--tf-gold);">--</div></div>
        <div class="stat-card"><div class="stat-label">In Transit</div><div class="stat-value" id="statTransit" style="color:var(--tf-blue);">--</div></div>
        <div class="stat-card"><div class="stat-label">Delivered Today</div><div class="stat-value" id="statDelivered" style="color:#4ade80;">--</div></div>
        <div class="stat-card"><div class="stat-label">Delayed</div><div class="stat-value" id="statDelayed" style="color:#f87171;">--</div></div>
    </div>
    <div class="toolbar">
        <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
            <input type="text" id="shipSearch" placeholder="Search shipments..." oninput="filterShipments()">
            <select id="filterStatus" onchange="filterShipments()">
                <option value="">All Status</option>
                <option value="loading">Loading</option>
                <option value="departed">Departed</option>
                <option value="in_transit">In Transit</option>
                <option value="delivered">Delivered</option>
                <option value="delayed">Delayed</option>
            </select>
        </div>
        <button class="btn-gold" onclick="openModal('shipModal')">+ New Shipment</button>
    </div>
    <div class="shipment-grid" id="shipmentGrid">
        <div class="loading">Loading shipments...</div>
    </div>
</div>

<!-- New Shipment Modal -->
<div class="modal-overlay" id="shipModal">
    <div class="modal">
        <h2>New Shipment</h2>
        <div class="form-group"><label>Load ID</label>
            <select id="shipLoadId">
                <option value="">Select a load or enter manually</option>
            </select>
        </div>
        <div class="form-group"><label>Project / Job Code</label><input type="text" id="shipProject" placeholder="Job code"></div>
        <div class="form-row">
            <div class="form-group"><label>Origin</label><input type="text" id="shipOrigin" value="Titan Carports HQ" placeholder="Pickup location"></div>
            <div class="form-group"><label>Destination</label><input type="text" id="shipDest" placeholder="Delivery location"></div>
        </div>
        <div class="form-row">
            <div class="form-group"><label>Carrier</label><input type="text" id="shipCarrier" placeholder="Carrier name"></div>
            <div class="form-group"><label>Driver</label><input type="text" id="shipDriver" placeholder="Driver name"></div>
        </div>
        <div class="form-row">
            <div class="form-group"><label>Truck #</label><input type="text" id="shipTruck" placeholder="Truck number"></div>
            <div class="form-group"><label>Trailer #</label><input type="text" id="shipTrailerNum" placeholder="Trailer number"></div>
        </div>
        <div class="form-row">
            <div class="form-group"><label>Departure Date</label><input type="date" id="shipDepart"></div>
            <div class="form-group"><label>ETA</label><input type="date" id="shipETA"></div>
        </div>
        <div class="modal-actions">
            <button class="btn-outline" onclick="closeModal('shipModal')">Cancel</button>
            <button class="btn-gold" onclick="saveShipment()">Create Shipment</button>
        </div>
    </div>
</div>

<!-- Delivery Confirmation Modal -->
<div class="modal-overlay" id="deliverModal">
    <div class="modal">
        <h2>Confirm Delivery</h2>
        <input type="hidden" id="deliverShipId">
        <div class="delivery-confirm">
            <h4>Delivery Confirmation</h4>
            <div class="form-group"><label>Delivery Date</label><input type="date" id="deliverDate"></div>
            <div class="form-group"><label>Received By</label><input type="text" id="deliverReceivedBy" placeholder="Name of person receiving"></div>
            <div class="form-group"><label>Condition Notes</label><textarea id="deliverNotes" placeholder="Condition of shipment, any damage noted..."></textarea></div>
        </div>
        <div class="modal-actions">
            <button class="btn-outline" onclick="closeModal('deliverModal')">Cancel</button>
            <button class="btn-green" onclick="confirmDelivery()">Confirm Delivery</button>
        </div>
    </div>
</div>

<script>
let allShipments = [];

function openModal(id) { document.getElementById(id).classList.add('active'); }
function closeModal(id) { document.getElementById(id).classList.remove('active'); }
document.querySelectorAll('.modal-overlay').forEach(m => m.addEventListener('click', function(e) { if (e.target === this) closeModal(this.id); }));

function getStatusBadge(status) {
    const cls = { loading: 'badge-loading', departed: 'badge-departed', in_transit: 'badge-in_transit', delivered: 'badge-delivered', delayed: 'badge-delayed' };
    return '<span class="badge ' + (cls[status] || 'badge-loading') + '">' + (status || 'unknown').replace(/_/g, ' ') + '</span>';
}

function getProgress(s) {
    const map = { loading: 10, departed: 30, in_transit: 60, delayed: 50, delivered: 100 };
    return map[s.status] || 0;
}

function renderShipments(shipments) {
    const grid = document.getElementById('shipmentGrid');
    if (!shipments.length) {
        grid.innerHTML = '<div class="empty-state"><h3>No active shipments</h3><p>Create a shipment from a finalized load to begin tracking.</p></div>';
        return;
    }
    grid.innerHTML = shipments.map(s => {
        const progress = s.progress || getProgress(s);
        const isDelivered = s.status === 'delivered';
        return '<div class="shipment-card">' +
            '<div class="shipment-header"><h3>' + (s.load_id || s.id || 'Shipment') + '</h3>' + getStatusBadge(s.status) + '</div>' +
            '<div class="shipment-route">' +
            '<span class="route-dot origin"></span><span style="color:var(--tf-muted);font-size:12px;">' + (s.origin || 'Titan HQ') + '</span>' +
            '<span class="route-line"></span>' +
            '<span style="color:var(--tf-muted);font-size:12px;">' + (s.destination || '--') + '</span><span class="route-dot dest"></span></div>' +
            '<div class="shipment-details">' +
            '<span class="detail-label">Project</span><span class="detail-value">' + (s.project || '--') + '</span>' +
            '<span class="detail-label">Carrier</span><span class="detail-value">' + (s.carrier || '--') + '</span>' +
            '<span class="detail-label">Driver</span><span class="detail-value">' + (s.driver || '--') + '</span>' +
            '<span class="detail-label">Truck #</span><span class="detail-value">' + (s.truck || '--') + '</span>' +
            '<span class="detail-label">ETA</span><span class="detail-value" style="color:var(--tf-gold);">' + (s.eta || '--') + '</span>' +
            (isDelivered && s.delivered_date ? '<span class="detail-label">Delivered</span><span class="detail-value" style="color:var(--tf-green);">' + s.delivered_date + '</span>' : '') +
            '</div>' +
            '<div class="progress-bar"><div class="progress-fill" style="width:' + progress + '%;' + (isDelivered ? 'background:var(--tf-green);' : '') + '"></div></div>' +
            (isDelivered ? '' :
            '<div class="card-actions">' +
            (s.status === 'loading' ? '<button class="btn-blue btn-sm" onclick="updateStatus(\'' + (s.id||'') + '\', \'departed\')">Mark Departed</button>' : '') +
            (s.status === 'departed' ? '<button class="btn-blue btn-sm" onclick="updateStatus(\'' + (s.id||'') + '\', \'in_transit\')">Mark In Transit</button>' : '') +
            (s.status === 'in_transit' || s.status === 'departed' ? '<button class="btn-green btn-sm" onclick="openDeliverModal(\'' + (s.id||'') + '\')">Mark Delivered</button>' : '') +
            '<button class="btn-outline btn-sm" style="background:rgba(239,68,68,0.1);color:#f87171;border-color:rgba(239,68,68,0.3);" onclick="updateStatus(\'' + (s.id||'') + '\', \'delayed\')">Flag Delayed</button>' +
            '</div>') +
            '</div>';
    }).join('');
}

function updateStats(shipments) {
    document.getElementById('statLoading').textContent = shipments.filter(s => s.status === 'loading').length;
    document.getElementById('statTransit').textContent = shipments.filter(s => s.status === 'in_transit' || s.status === 'departed').length;
    const today = new Date().toISOString().slice(0, 10);
    document.getElementById('statDelivered').textContent = shipments.filter(s => s.status === 'delivered' && (s.delivered_date || '').startsWith(today)).length;
    document.getElementById('statDelayed').textContent = shipments.filter(s => s.status === 'delayed').length;
}

function filterShipments() {
    const search = document.getElementById('shipSearch').value.toLowerCase();
    const status = document.getElementById('filterStatus').value;
    const filtered = allShipments.filter(s => {
        if (search && !(s.load_id||s.id||'').toLowerCase().includes(search) && !(s.project||'').toLowerCase().includes(search) && !(s.carrier||'').toLowerCase().includes(search) && !(s.driver||'').toLowerCase().includes(search)) return false;
        if (status && s.status !== status) return false;
        return true;
    });
    renderShipments(filtered);
}

function openDeliverModal(id) {
    document.getElementById('deliverShipId').value = id;
    document.getElementById('deliverDate').value = new Date().toISOString().slice(0, 10);
    document.getElementById('deliverReceivedBy').value = '';
    document.getElementById('deliverNotes').value = '';
    openModal('deliverModal');
}

async function updateStatus(id, newStatus) {
    try {
        await fetch('/api/shipping/active', {
            method: 'POST', headers: {'Content-Type':'application/json'},
            body: JSON.stringify({ id: id, status: newStatus, action: 'update_status' })
        });
        loadShipments();
    } catch(e) { alert('Error updating status'); }
}

async function confirmDelivery() {
    const id = document.getElementById('deliverShipId').value;
    try {
        await fetch('/api/shipping/active', {
            method: 'POST', headers: {'Content-Type':'application/json'},
            body: JSON.stringify({
                id: id,
                status: 'delivered',
                action: 'deliver',
                delivered_date: document.getElementById('deliverDate').value,
                received_by: document.getElementById('deliverReceivedBy').value,
                delivery_notes: document.getElementById('deliverNotes').value
            })
        });
        closeModal('deliverModal');
        loadShipments();
    } catch(e) { alert('Error confirming delivery'); }
}

async function saveShipment() {
    const payload = {
        load_id: document.getElementById('shipLoadId').value || ('SHIP-' + Date.now().toString().slice(-6)),
        project: document.getElementById('shipProject').value,
        origin: document.getElementById('shipOrigin').value,
        destination: document.getElementById('shipDest').value,
        carrier: document.getElementById('shipCarrier').value,
        driver: document.getElementById('shipDriver').value,
        truck: document.getElementById('shipTruck').value,
        trailer: document.getElementById('shipTrailerNum').value,
        departure: document.getElementById('shipDepart').value,
        eta: document.getElementById('shipETA').value,
        status: 'loading',
        action: 'create'
    };
    if (!payload.load_id) { alert('Load ID is required'); return; }
    try {
        await fetch('/api/shipping/active', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
        closeModal('shipModal');
        loadShipments();
    } catch(e) { alert('Error: ' + e.message); }
}

async function loadShipments() {
    try {
        const resp = await fetch('/api/shipping/active');
        const data = await resp.json();
        allShipments = Array.isArray(data) ? data : (data.shipments || data.data || []);
        updateStats(allShipments);
        renderShipments(allShipments);
    } catch(e) { renderShipments([]); }
}

async function loadLoadsForDropdown() {
    try {
        const resp = await fetch('/api/load-builder/loads');
        const data = await resp.json();
        const loads = (data.loads || []).filter(l => l.status === 'ready');
        const sel = document.getElementById('shipLoadId');
        loads.forEach(l => {
            const o = document.createElement('option');
            o.value = l.load_id;
            o.textContent = l.load_id + ' - ' + (l.job_code || '') + ' (' + (l.items || []).length + ' items)';
            sel.appendChild(o);
        });
    } catch(e) {}
}

loadShipments();
loadLoadsForDropdown();
</script>
"""
