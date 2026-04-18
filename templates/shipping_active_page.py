"""
TitanForge v4 — Active Shipments
===================================
In-transit loads, tracking info, ETA, delivery status, driver/carrier info.
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
    }
    .ship-container {
        max-width: 1400px; margin: 0 auto; padding: 24px 32px;
        font-family: 'Inter', 'Segoe UI', sans-serif; color: var(--tf-text);
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
    .btn-outline { background: transparent; color: var(--tf-muted); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 10px 20px; font-weight: 600; font-size: 14px; cursor: pointer; }
    .btn-outline:hover { border-color: var(--tf-gold); color: var(--tf-gold); }
    .stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
    @media (max-width: 900px) { .stats-row { grid-template-columns: 1fr 1fr; } }
    .stat-card { background: var(--tf-card); border-radius: 10px; padding: 18px; border: 1px solid rgba(255,255,255,0.06); }
    .stat-card .stat-label { font-size: 12px; color: var(--tf-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
    .stat-card .stat-value { font-size: 24px; font-weight: 800; }
    .map-placeholder {
        background: var(--tf-card); border-radius: 12px; border: 1px solid rgba(255,255,255,0.06);
        height: 250px; display: flex; align-items: center; justify-content: center;
        color: var(--tf-muted); font-size: 16px; margin-bottom: 24px;
    }
    .shipment-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); gap: 16px; }
    .shipment-card {
        background: var(--tf-card); border-radius: 12px; border: 1px solid rgba(255,255,255,0.06);
        padding: 20px; cursor: pointer; transition: border-color 0.2s;
    }
    .shipment-card:hover { border-color: var(--tf-blue); }
    .shipment-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
    .shipment-header h3 { font-size: 16px; font-weight: 700; margin: 0; }
    .shipment-route { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; font-size: 13px; }
    .route-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
    .route-dot.origin { background: var(--tf-blue); }
    .route-dot.dest { background: #4ade80; }
    .route-line { flex: 1; height: 2px; background: linear-gradient(90deg, var(--tf-blue), #4ade80); }
    .shipment-details { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 13px; }
    .shipment-details .detail-label { color: var(--tf-muted); }
    .shipment-details .detail-value { font-weight: 600; text-align: right; }
    .badge { display: inline-block; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; }
    .badge-transit { background: rgba(59,130,246,0.2); color: #60a5fa; }
    .badge-delivered { background: rgba(34,197,94,0.2); color: #4ade80; }
    .badge-delayed { background: rgba(239,68,68,0.2); color: #f87171; }
    .badge-loading { background: rgba(212,168,67,0.2); color: var(--tf-gold); }
    .progress-bar { height: 4px; background: rgba(255,255,255,0.08); border-radius: 2px; margin-top: 12px; }
    .progress-fill { height: 100%; border-radius: 2px; background: var(--tf-blue); }
    .empty-state { text-align: center; padding: 60px 20px; color: var(--tf-muted); grid-column: 1 / -1; }
    .empty-state h3 { font-size: 18px; margin-bottom: 8px; color: var(--tf-text); }
    .loading { text-align: center; padding: 40px; color: var(--tf-muted); grid-column: 1 / -1; }
    .modal-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 1000; justify-content: center; align-items: center; }
    .modal-overlay.active { display: flex; }
    .modal { background: var(--tf-card); border-radius: 12px; padding: 28px; width: 560px; max-width: 90vw; border: 1px solid rgba(255,255,255,0.1); max-height: 80vh; overflow-y: auto; }
    .modal h2 { font-size: 20px; margin: 0 0 20px 0; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 24px; }
    .form-group { margin-bottom: 16px; }
    .form-group label { display: block; font-size: 13px; font-weight: 600; color: var(--tf-muted); margin-bottom: 6px; }
    .form-group input, .form-group select, .form-group textarea {
        width: 100%; background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px; font-family: inherit; box-sizing: border-box;
    }
</style>

<div class="ship-container">
    <div class="page-header">
        <h1>Active Shipments</h1>
        <p>Track in-transit loads, delivery status, carrier info, and ETAs</p>
    </div>
    <div class="stats-row">
        <div class="stat-card"><div class="stat-label">In Transit</div><div class="stat-value" id="statTransit" style="color:var(--tf-blue);">--</div></div>
        <div class="stat-card"><div class="stat-label">Delivered Today</div><div class="stat-value" id="statDelivered" style="color:#4ade80;">--</div></div>
        <div class="stat-card"><div class="stat-label">Delayed</div><div class="stat-value" id="statDelayed" style="color:#f87171;">--</div></div>
        <div class="stat-card"><div class="stat-label">Loading</div><div class="stat-value" id="statLoading" style="color:var(--tf-gold);">--</div></div>
    </div>
    <div class="map-placeholder" id="mapArea">Map view -- integrate with mapping service for live tracking</div>
    <div class="toolbar">
        <div style="display:flex;gap:10px;align-items:center;">
            <input type="text" id="shipSearch" placeholder="Search shipments..." oninput="filterShipments()">
            <select id="filterStatus" onchange="filterShipments()">
                <option value="">All Status</option>
                <option value="in_transit">In Transit</option>
                <option value="delivered">Delivered</option>
                <option value="delayed">Delayed</option>
                <option value="loading">Loading</option>
            </select>
        </div>
        <button class="btn-gold" onclick="openModal('shipModal')">+ New Shipment</button>
    </div>
    <div class="shipment-grid" id="shipmentGrid">
        <div class="loading">Loading shipments...</div>
    </div>
</div>

<div class="modal-overlay" id="shipModal">
    <div class="modal">
        <h2>New Shipment</h2>
        <div class="form-group"><label>Load / Shipment ID</label><input type="text" id="shipId" placeholder="e.g. LOAD-2026-042"></div>
        <div class="form-group"><label>Project / Job Code</label><input type="text" id="shipProject" placeholder="Job code"></div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div class="form-group"><label>Origin</label><input type="text" id="shipOrigin" placeholder="Pickup location"></div>
            <div class="form-group"><label>Destination</label><input type="text" id="shipDest" placeholder="Delivery location"></div>
            <div class="form-group"><label>Carrier</label><input type="text" id="shipCarrier" placeholder="Carrier name"></div>
            <div class="form-group"><label>Driver</label><input type="text" id="shipDriver" placeholder="Driver name"></div>
            <div class="form-group"><label>Departure Date</label><input type="date" id="shipDepart"></div>
            <div class="form-group"><label>ETA</label><input type="date" id="shipETA"></div>
        </div>
        <div class="form-group"><label>Tracking Number</label><input type="text" id="shipTracking" placeholder="Tracking #"></div>
        <div class="modal-actions">
            <button class="btn-outline" onclick="closeModal('shipModal')">Cancel</button>
            <button class="btn-gold" onclick="saveShipment()">Create Shipment</button>
        </div>
    </div>
</div>

<script>
let allShipments = [];

function openModal(id) { document.getElementById(id).classList.add('active'); }
function closeModal(id) { document.getElementById(id).classList.remove('active'); }
document.querySelectorAll('.modal-overlay').forEach(m => m.addEventListener('click', function(e) { if (e.target === this) closeModal(this.id); }));

function getStatusBadge(status) {
    const map = { in_transit: 'badge-transit', delivered: 'badge-delivered', delayed: 'badge-delayed', loading: 'badge-loading' };
    return '<span class="badge ' + (map[status] || 'badge-transit') + '">' + (status || 'unknown').replace(/_/g, ' ') + '</span>';
}

function renderShipments(shipments) {
    const grid = document.getElementById('shipmentGrid');
    if (!shipments.length) {
        grid.innerHTML = '<div class="empty-state"><h3>No active shipments</h3><p>Create a shipment to begin tracking.</p></div>';
        return;
    }
    grid.innerHTML = shipments.map(s => {
        const progress = s.progress || 0;
        return '<div class="shipment-card" onclick="viewShipment(\'' + (s.id||'') + '\')">' +
            '<div class="shipment-header"><h3>' + (s.load_id || s.id || 'Load') + '</h3>' + getStatusBadge(s.status) + '</div>' +
            '<div class="shipment-route">' +
            '<span class="route-dot origin"></span><span style="color:var(--tf-muted);font-size:12px;">' + (s.origin || '--') + '</span>' +
            '<span class="route-line"></span>' +
            '<span style="color:var(--tf-muted);font-size:12px;">' + (s.destination || '--') + '</span><span class="route-dot dest"></span></div>' +
            '<div class="shipment-details">' +
            '<span class="detail-label">Project</span><span class="detail-value">' + (s.project || '--') + '</span>' +
            '<span class="detail-label">Carrier</span><span class="detail-value">' + (s.carrier || '--') + '</span>' +
            '<span class="detail-label">Driver</span><span class="detail-value">' + (s.driver || '--') + '</span>' +
            '<span class="detail-label">ETA</span><span class="detail-value" style="color:var(--tf-gold);">' + (s.eta || '--') + '</span></div>' +
            '<div class="progress-bar"><div class="progress-fill" style="width:' + progress + '%;"></div></div></div>';
    }).join('');
}

function updateStats(shipments) {
    document.getElementById('statTransit').textContent = shipments.filter(s => s.status === 'in_transit').length;
    document.getElementById('statDelivered').textContent = shipments.filter(s => s.status === 'delivered').length;
    document.getElementById('statDelayed').textContent = shipments.filter(s => s.status === 'delayed').length;
    document.getElementById('statLoading').textContent = shipments.filter(s => s.status === 'loading').length;
}

function filterShipments() {
    const search = document.getElementById('shipSearch').value.toLowerCase();
    const status = document.getElementById('filterStatus').value;
    const filtered = allShipments.filter(s => {
        if (search && !(s.load_id||s.id||'').toLowerCase().includes(search) && !(s.project||'').toLowerCase().includes(search) && !(s.carrier||'').toLowerCase().includes(search)) return false;
        if (status && s.status !== status) return false;
        return true;
    });
    renderShipments(filtered);
}

function viewShipment(id) { window.location.href = '/shipping/detail/' + encodeURIComponent(id); }

async function saveShipment() {
    const payload = {
        load_id: document.getElementById('shipId').value,
        project: document.getElementById('shipProject').value,
        origin: document.getElementById('shipOrigin').value,
        destination: document.getElementById('shipDest').value,
        carrier: document.getElementById('shipCarrier').value,
        driver: document.getElementById('shipDriver').value,
        departure: document.getElementById('shipDepart').value,
        eta: document.getElementById('shipETA').value,
        tracking: document.getElementById('shipTracking').value,
        status: 'loading'
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
        allShipments = Array.isArray(data) ? data : (data.shipments || []);
        updateStats(allShipments);
        renderShipments(allShipments);
    } catch(e) { renderShipments([]); }
}

loadShipments();
</script>
"""
