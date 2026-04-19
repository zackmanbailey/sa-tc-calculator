"""
TitanForge v4 — Bills of Lading
==================================
BOL list with status badges, create BOL from load, full form fields,
PDF generation, signature capture. Wired to ShippingBOLHandler.
"""

SHIPPING_BOL_PAGE_HTML = r"""
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
    }
    .bol-container {
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
    .btn-blue:hover { opacity: 0.9; }
    .btn-green { background: var(--tf-green); color: #fff; border: none; border-radius: 8px; padding: 10px 20px; font-weight: 700; font-size: 14px; cursor: pointer; }
    .btn-outline { background: transparent; color: var(--tf-muted); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 10px 20px; font-weight: 600; font-size: 14px; cursor: pointer; }
    .btn-outline:hover { border-color: var(--tf-gold); color: var(--tf-gold); }
    .btn-sm { padding: 6px 14px; font-size: 12px; border-radius: 6px; }
    .btn-danger { background: var(--tf-red); color: #fff; border: none; border-radius: 8px; padding: 6px 14px; font-weight: 600; font-size: 12px; cursor: pointer; }
    .stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
    @media (max-width: 900px) { .stats-row { grid-template-columns: 1fr 1fr; } }
    .stat-card { background: var(--tf-card); border-radius: 10px; padding: 18px; border: 1px solid rgba(255,255,255,0.06); }
    .stat-card .stat-label { font-size: 12px; color: var(--tf-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
    .stat-card .stat-value { font-size: 24px; font-weight: 800; }
    .data-card { background: var(--tf-card); border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); overflow: hidden; }
    .data-table { width: 100%; border-collapse: collapse; font-size: 14px; }
    .data-table thead th {
        background: #1a2744; padding: 14px 16px; text-align: left; font-weight: 700;
        font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--tf-muted);
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .data-table tbody td { padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.04); }
    .data-table tbody tr { transition: background 0.15s; cursor: pointer; }
    .data-table tbody tr:hover { background: rgba(255,255,255,0.04); }
    .badge { display: inline-block; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
    .badge-draft { background: rgba(148,163,184,0.2); color: #94a3b8; }
    .badge-final { background: rgba(34,197,94,0.2); color: #4ade80; }
    .badge-signed { background: rgba(59,130,246,0.2); color: #60a5fa; }
    .badge-delivered { background: rgba(212,168,67,0.2); color: var(--tf-gold); }
    .badge-void { background: rgba(239,68,68,0.2); color: #f87171; }
    .empty-state { text-align: center; padding: 60px 20px; color: var(--tf-muted); }
    .empty-state h3 { font-size: 18px; margin-bottom: 8px; color: var(--tf-text); }
    .loading { text-align: center; padding: 40px; color: var(--tf-muted); }
    .modal-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 1000; justify-content: center; align-items: center; }
    .modal-overlay.active { display: flex; }
    .modal { background: var(--tf-card); border-radius: 12px; padding: 28px; width: 720px; max-width: 95vw; border: 1px solid rgba(255,255,255,0.1); max-height: 90vh; overflow-y: auto; }
    .modal h2 { font-size: 20px; margin: 0 0 20px 0; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 24px; flex-wrap: wrap; }
    .form-group { margin-bottom: 16px; }
    .form-group label { display: block; font-size: 13px; font-weight: 600; color: var(--tf-muted); margin-bottom: 6px; }
    .form-group input, .form-group select, .form-group textarea {
        width: 100%; background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px; font-family: inherit; box-sizing: border-box;
    }
    .form-group textarea { min-height: 60px; resize: vertical; }
    .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .form-row-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }
    .items-list { margin-top: 8px; }
    .item-row { display: flex; gap: 8px; align-items: center; margin-bottom: 8px; }
    .item-row input { flex: 1; }
    .item-row input.short { width: 80px; flex: none; }
    .btn-remove { background: rgba(239,68,68,0.2); color: #f87171; border: none; border-radius: 6px; padding: 8px 10px; cursor: pointer; font-size: 12px; }
    .section-divider { border-top: 1px solid rgba(255,255,255,0.06); margin: 20px 0; padding-top: 16px; }
    .section-label { font-size: 14px; font-weight: 700; margin-bottom: 12px; color: var(--tf-gold); }
    .checkbox-group { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
    .checkbox-group input[type="checkbox"] { width: auto; }
    .checkbox-group label { margin-bottom: 0; }

    /* Signature */
    .sig-area { margin-top: 16px; }
    .sig-canvas { border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; background: #0f172a; cursor: crosshair; display: block; }
    .sig-signed-badge { background: rgba(34,197,94,0.15); color: #4ade80; padding: 12px 20px; border-radius: 8px; font-weight: 700; text-align: center; }
    .sig-actions { display: flex; gap: 8px; margin-top: 8px; }

    @media (max-width: 768px) {
        .bol-container { padding: 16px; }
        .toolbar { flex-direction: column; align-items: stretch; }
        .toolbar input[type="text"] { width: 100%; }
        .form-row, .form-row-3 { grid-template-columns: 1fr; }
        .stats-row { grid-template-columns: 1fr 1fr; }
        .modal { padding: 20px; }
    }
</style>

<div class="bol-container">
    <div class="page-header">
        <h1>Bills of Lading</h1>
        <p>Create and manage BOLs, generate PDFs, capture driver signatures, and track delivery status</p>
    </div>
    <div class="stats-row">
        <div class="stat-card"><div class="stat-label">Total BOLs</div><div class="stat-value" id="statTotal" style="color:var(--tf-text);">--</div></div>
        <div class="stat-card"><div class="stat-label">Draft</div><div class="stat-value" id="statDraft" style="color:var(--tf-muted);">--</div></div>
        <div class="stat-card"><div class="stat-label">Signed</div><div class="stat-value" id="statSigned" style="color:var(--tf-blue);">--</div></div>
        <div class="stat-card"><div class="stat-label">Delivered</div><div class="stat-value" id="statDelivered" style="color:#4ade80;">--</div></div>
    </div>
    <div class="toolbar">
        <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
            <input type="text" id="bolSearch" placeholder="Search BOLs..." oninput="filterBOLs()">
            <select id="filterStatus" onchange="filterBOLs()">
                <option value="">All Status</option>
                <option value="draft">Draft</option>
                <option value="final">Finalized</option>
                <option value="signed">Signed</option>
                <option value="delivered">Delivered</option>
                <option value="void">Void</option>
            </select>
        </div>
        <div style="display:flex;gap:10px;flex-wrap:wrap;">
            <button class="btn-blue" onclick="openFromLoad()">Create from Load</button>
            <button class="btn-gold" onclick="openNewBOL()">+ New BOL</button>
        </div>
    </div>
    <div class="data-card">
        <div id="bolTableWrap" class="loading">Loading BOLs...</div>
    </div>
</div>

<!-- BOL Form Modal -->
<div class="modal-overlay" id="bolModal">
    <div class="modal">
        <h2 id="bolModalTitle">New Bill of Lading</h2>
        <input type="hidden" id="bolId">
        <input type="hidden" id="bolLoadId">

        <div class="section-label">BOL Information</div>
        <div class="form-row">
            <div class="form-group"><label>BOL Number</label><input type="text" id="bolNumber" placeholder="Auto-generated"></div>
            <div class="form-group"><label>Date</label><input type="date" id="bolDate"></div>
        </div>
        <div class="form-group"><label>Project / Job Code</label>
            <select id="bolProject"><option value="">Select Project</option></select>
        </div>

        <div class="section-divider"></div>
        <div class="section-label">Shipper / Consignee</div>
        <div class="form-row">
            <div class="form-group"><label>Shipper Name</label><input type="text" id="bolShipper" value="Titan Carports"></div>
            <div class="form-group"><label>Shipper Address</label><input type="text" id="bolShipperAddr" placeholder="123 Factory Rd"></div>
        </div>
        <div class="form-row">
            <div class="form-group"><label>Consignee Name</label><input type="text" id="bolConsignee" placeholder="Receiving party name"></div>
            <div class="form-group"><label>Consignee Address</label><input type="text" id="bolConsigneeAddr" placeholder="Delivery address"></div>
        </div>

        <div class="section-divider"></div>
        <div class="section-label">Carrier Information</div>
        <div class="form-row">
            <div class="form-group"><label>Carrier Name</label><input type="text" id="bolCarrier" placeholder="Carrier company"></div>
            <div class="form-group"><label>Driver Name</label><input type="text" id="bolDriver" placeholder="Driver name"></div>
        </div>
        <div class="form-row">
            <div class="form-group"><label>Truck #</label><input type="text" id="bolTruck" placeholder="Truck number"></div>
            <div class="form-group"><label>Trailer #</label><input type="text" id="bolTrailer" placeholder="Trailer number"></div>
        </div>

        <div class="section-divider"></div>
        <div class="section-label">Line Items</div>
        <div class="items-list" id="bolItemsList"></div>
        <button class="btn-outline btn-sm" onclick="addBOLItem()" style="margin-top:6px;">+ Add Item</button>

        <div class="section-divider"></div>
        <div class="form-row-3">
            <div class="form-group"><label>Total Weight (lbs)</label><input type="number" id="bolWeight" placeholder="0"></div>
            <div class="form-group"><label>Total Pieces</label><input type="number" id="bolPieces" placeholder="0"></div>
            <div class="form-group"><label>Freight Class</label><input type="text" id="bolFreight" placeholder="e.g. 85"></div>
        </div>

        <div class="section-divider"></div>
        <div class="section-label">Special Instructions</div>
        <div class="form-group"><textarea id="bolNotes" placeholder="Special handling, delivery instructions, etc."></textarea></div>
        <div class="checkbox-group">
            <input type="checkbox" id="bolHazmat">
            <label for="bolHazmat" style="color:var(--tf-red);font-weight:600;font-size:13px;">Contains Hazardous Materials</label>
        </div>

        <div class="section-divider"></div>
        <div class="section-label">Driver Signature</div>
        <div class="sig-area" id="sigArea">
            <canvas class="sig-canvas" id="sigCanvas" width="660" height="120"></canvas>
            <div class="sig-actions">
                <button class="btn-outline btn-sm" onclick="clearSignature()">Clear</button>
                <button class="btn-blue btn-sm" onclick="markSigned()">Accept Signature</button>
            </div>
        </div>
        <div class="sig-signed-badge" id="sigBadge" style="display:none;">Signed by Driver</div>

        <div class="modal-actions">
            <button class="btn-outline" onclick="closeModal('bolModal')">Cancel</button>
            <button class="btn-danger btn-sm" id="btnVoid" onclick="voidBOL()" style="display:none;">Void</button>
            <button class="btn-blue" onclick="generatePDF()">Generate PDF</button>
            <button class="btn-gold" onclick="saveBOL('draft')">Save Draft</button>
            <button class="btn-green" onclick="saveBOL('final')">Finalize</button>
        </div>
    </div>
</div>

<!-- Load Selector Modal -->
<div class="modal-overlay" id="loadModal">
    <div class="modal" style="width:500px;">
        <h2>Create BOL from Finalized Load</h2>
        <div class="form-group"><label>Select a Load</label>
            <select id="loadSelect" onchange="previewLoad()">
                <option value="">Select a finalized load...</option>
            </select>
        </div>
        <div id="loadPreview" style="background:var(--tf-bg);border-radius:8px;padding:16px;display:none;">
            <div style="display:flex;justify-content:space-between;margin-bottom:8px;"><span style="color:var(--tf-muted)">Job Code:</span><span id="lpJob" style="font-weight:700;"></span></div>
            <div style="display:flex;justify-content:space-between;margin-bottom:8px;"><span style="color:var(--tf-muted)">Items:</span><span id="lpItems" style="font-weight:700;"></span></div>
            <div style="display:flex;justify-content:space-between;margin-bottom:8px;"><span style="color:var(--tf-muted)">Total Weight:</span><span id="lpWeight" style="font-weight:700;"></span></div>
            <div style="display:flex;justify-content:space-between;"><span style="color:var(--tf-muted)">Driver:</span><span id="lpDriver" style="font-weight:700;"></span></div>
        </div>
        <div class="modal-actions">
            <button class="btn-outline" onclick="closeModal('loadModal')">Cancel</button>
            <button class="btn-gold" onclick="createFromSelectedLoad()">Create BOL</button>
        </div>
    </div>
</div>

<script>
let allBOLs = [];
let bolItemCount = 0;
let loads = [];
let projects = [];
let sigCtx = null;
let sigDrawing = false;
let sigData = null;

function openModal(id) { document.getElementById(id).classList.add('active'); }
function closeModal(id) { document.getElementById(id).classList.remove('active'); }
document.querySelectorAll('.modal-overlay').forEach(m => m.addEventListener('click', function(e) { if (e.target === this) closeModal(this.id); }));

// Signature canvas
function initSignature() {
    const canvas = document.getElementById('sigCanvas');
    sigCtx = canvas.getContext('2d');
    sigCtx.strokeStyle = '#e2e8f0';
    sigCtx.lineWidth = 2;
    sigCtx.lineCap = 'round';

    canvas.addEventListener('mousedown', e => { sigDrawing = true; sigCtx.beginPath(); sigCtx.moveTo(e.offsetX, e.offsetY); });
    canvas.addEventListener('mousemove', e => { if (sigDrawing) { sigCtx.lineTo(e.offsetX, e.offsetY); sigCtx.stroke(); } });
    canvas.addEventListener('mouseup', () => sigDrawing = false);
    canvas.addEventListener('mouseleave', () => sigDrawing = false);
    // Touch
    canvas.addEventListener('touchstart', e => { e.preventDefault(); const t = e.touches[0]; const r = canvas.getBoundingClientRect(); sigDrawing = true; sigCtx.beginPath(); sigCtx.moveTo(t.clientX - r.left, t.clientY - r.top); });
    canvas.addEventListener('touchmove', e => { e.preventDefault(); if (sigDrawing) { const t = e.touches[0]; const r = canvas.getBoundingClientRect(); sigCtx.lineTo(t.clientX - r.left, t.clientY - r.top); sigCtx.stroke(); } });
    canvas.addEventListener('touchend', () => sigDrawing = false);
}

function clearSignature() {
    const canvas = document.getElementById('sigCanvas');
    sigCtx.clearRect(0, 0, canvas.width, canvas.height);
    sigData = null;
    document.getElementById('sigArea').style.display = '';
    document.getElementById('sigBadge').style.display = 'none';
}

function markSigned() {
    const canvas = document.getElementById('sigCanvas');
    sigData = canvas.toDataURL('image/png');
    document.getElementById('sigArea').style.display = 'none';
    document.getElementById('sigBadge').style.display = '';
}

function addBOLItem(desc, qty, weight) {
    bolItemCount++;
    const div = document.createElement('div');
    div.className = 'item-row';
    div.id = 'bol-item-' + bolItemCount;
    div.innerHTML = '<input type="text" placeholder="Description" value="' + (desc||'').replace(/"/g, '&quot;') + '">' +
        '<input type="number" class="short" placeholder="Qty" value="' + (qty||'') + '">' +
        '<input type="number" class="short" placeholder="Lbs" value="' + (weight||'') + '">' +
        '<button class="btn-remove" onclick="this.parentElement.remove();calcTotals();">X</button>';
    div.querySelectorAll('input').forEach(inp => inp.addEventListener('input', calcTotals));
    document.getElementById('bolItemsList').appendChild(div);
}

function calcTotals() {
    let totalQty = 0, totalWeight = 0;
    document.querySelectorAll('.item-row').forEach(row => {
        const inputs = row.querySelectorAll('input');
        totalQty += parseInt(inputs[1]?.value) || 0;
        totalWeight += parseInt(inputs[2]?.value) || 0;
    });
    document.getElementById('bolPieces').value = totalQty;
    document.getElementById('bolWeight').value = totalWeight;
}

function openNewBOL() {
    document.getElementById('bolModalTitle').textContent = 'New Bill of Lading';
    ['bolId','bolLoadId','bolConsignee','bolConsigneeAddr','bolCarrier','bolDriver','bolTruck','bolTrailer','bolNotes','bolFreight'].forEach(id => document.getElementById(id).value = '');
    document.getElementById('bolNumber').value = 'BOL-' + new Date().getFullYear() + '-' + String(allBOLs.length + 1).padStart(4, '0');
    document.getElementById('bolDate').value = new Date().toISOString().slice(0,10);
    document.getElementById('bolShipper').value = 'Titan Carports';
    document.getElementById('bolShipperAddr').value = '';
    document.getElementById('bolWeight').value = '';
    document.getElementById('bolPieces').value = '';
    document.getElementById('bolHazmat').checked = false;
    document.getElementById('bolProject').value = '';
    document.getElementById('bolItemsList').innerHTML = '';
    document.getElementById('btnVoid').style.display = 'none';
    bolItemCount = 0;
    addBOLItem();
    clearSignature();
    sigData = null;

    // Check for items from build page
    const storedItems = sessionStorage.getItem('bol_items');
    if (storedItems) {
        document.getElementById('bolItemsList').innerHTML = '';
        bolItemCount = 0;
        let items;
        try { items = JSON.parse(storedItems); } catch(e) { console.error('Bad bol_items JSON:', e); items = []; }
        items.forEach(it => addBOLItem(it.description, it.quantity, it.weight));
        calcTotals();
        sessionStorage.removeItem('bol_items');
        sessionStorage.removeItem('bol_weight');
        const loadId = sessionStorage.getItem('bol_load_id');
        if (loadId) { document.getElementById('bolLoadId').value = loadId; sessionStorage.removeItem('bol_load_id'); }
    }
    openModal('bolModal');
}

function editBOL(bol) {
    document.getElementById('bolModalTitle').textContent = 'Edit BOL - ' + (bol.bol_number || '');
    document.getElementById('bolId').value = bol.id || '';
    document.getElementById('bolLoadId').value = bol.load_id || '';
    document.getElementById('bolNumber').value = bol.bol_number || '';
    document.getElementById('bolDate').value = bol.date || '';
    document.getElementById('bolProject').value = bol.project || '';
    document.getElementById('bolShipper').value = bol.shipper || 'Titan Carports';
    document.getElementById('bolShipperAddr').value = bol.shipper_address || '';
    document.getElementById('bolConsignee').value = bol.consignee || '';
    document.getElementById('bolConsigneeAddr').value = bol.consignee_address || '';
    document.getElementById('bolCarrier').value = bol.carrier || '';
    document.getElementById('bolDriver').value = bol.driver || '';
    document.getElementById('bolTruck').value = bol.truck || '';
    document.getElementById('bolTrailer').value = bol.trailer || '';
    document.getElementById('bolWeight').value = bol.total_weight || '';
    document.getElementById('bolPieces').value = bol.total_pieces || '';
    document.getElementById('bolFreight').value = bol.freight_class || '';
    document.getElementById('bolNotes').value = bol.notes || '';
    document.getElementById('bolHazmat').checked = bol.hazmat || false;
    document.getElementById('btnVoid').style.display = bol.status !== 'void' ? '' : 'none';
    document.getElementById('bolItemsList').innerHTML = '';
    bolItemCount = 0;
    (bol.items || []).forEach(it => addBOLItem(it.description, it.quantity, it.weight));

    // Signature state
    if (bol.signature || bol.status === 'signed' || bol.status === 'delivered') {
        sigData = bol.signature || 'signed';
        document.getElementById('sigArea').style.display = 'none';
        document.getElementById('sigBadge').style.display = '';
    } else {
        clearSignature();
    }
    openModal('bolModal');
}

function renderTable(bols) {
    const wrap = document.getElementById('bolTableWrap');
    if (!bols.length) {
        wrap.innerHTML = '<div class="empty-state"><h3>No Bills of Lading</h3><p>Create a BOL to document shipment contents and generate shipping documents.</p></div>';
        return;
    }
    let html = '<table class="data-table"><thead><tr><th>BOL #</th><th>Date</th><th>Project</th><th>Consignee</th><th>Carrier</th><th>Driver</th><th>Truck #</th><th>Weight</th><th>Pieces</th><th>Status</th></tr></thead><tbody>';
    bols.forEach(b => {
        const stCls = { final: 'badge-final', signed: 'badge-signed', delivered: 'badge-delivered', void: 'badge-void' }[b.status] || 'badge-draft';
        html += '<tr onclick=\'editBOL(' + JSON.stringify(b).replace(/'/g,"&#39;") + ')\'>' +
            '<td style="font-weight:600;color:var(--tf-gold);">' + (b.bol_number || '--') + '</td>' +
            '<td>' + (b.date || '--') + '</td>' +
            '<td>' + (b.project || '--') + '</td>' +
            '<td>' + (b.consignee || '--') + '</td>' +
            '<td>' + (b.carrier || '--') + '</td>' +
            '<td>' + (b.driver || '--') + '</td>' +
            '<td>' + (b.truck || '--') + '</td>' +
            '<td>' + (b.total_weight ? b.total_weight.toLocaleString() + ' lbs' : '--') + '</td>' +
            '<td>' + (b.total_pieces || '--') + '</td>' +
            '<td><span class="badge ' + stCls + '">' + (b.status || 'draft') + '</span></td></tr>';
    });
    html += '</tbody></table>';
    wrap.innerHTML = html;
}

function updateStats(bols) {
    document.getElementById('statTotal').textContent = bols.length;
    document.getElementById('statDraft').textContent = bols.filter(b => b.status === 'draft' || !b.status).length;
    document.getElementById('statSigned').textContent = bols.filter(b => b.status === 'signed').length;
    document.getElementById('statDelivered').textContent = bols.filter(b => b.status === 'final' || b.status === 'delivered').length;
}

function filterBOLs() {
    const search = document.getElementById('bolSearch').value.toLowerCase();
    const status = document.getElementById('filterStatus').value;
    const filtered = allBOLs.filter(b => {
        if (search && !(b.bol_number||'').toLowerCase().includes(search) && !(b.project||'').toLowerCase().includes(search) && !(b.consignee||'').toLowerCase().includes(search) && !(b.carrier||'').toLowerCase().includes(search)) return false;
        if (status && (b.status||'draft') !== status) return false;
        return true;
    });
    renderTable(filtered);
}

function generatePDF() {
    const bolId = document.getElementById('bolId').value;
    const num = document.getElementById('bolNumber').value;
    const id = bolId || num;
    if (id) {
        window.open('/api/shipping/bol/pdf/' + encodeURIComponent(id), '_blank');
    }
}

async function saveBOL(status) {
    const items = [];
    document.querySelectorAll('.item-row').forEach(row => {
        const inputs = row.querySelectorAll('input');
        if (inputs[0]?.value) items.push({ description: inputs[0].value, quantity: parseInt(inputs[1]?.value)||0, weight: parseInt(inputs[2]?.value)||0 });
    });
    const payload = {
        id: document.getElementById('bolId').value || undefined,
        load_id: document.getElementById('bolLoadId').value || undefined,
        bol_number: document.getElementById('bolNumber').value,
        date: document.getElementById('bolDate').value,
        project: document.getElementById('bolProject').value,
        shipper: document.getElementById('bolShipper').value,
        shipper_address: document.getElementById('bolShipperAddr').value,
        consignee: document.getElementById('bolConsignee').value,
        consignee_address: document.getElementById('bolConsigneeAddr').value,
        carrier: document.getElementById('bolCarrier').value,
        driver: document.getElementById('bolDriver').value,
        truck: document.getElementById('bolTruck').value,
        trailer: document.getElementById('bolTrailer').value,
        total_weight: parseInt(document.getElementById('bolWeight').value) || 0,
        total_pieces: parseInt(document.getElementById('bolPieces').value) || 0,
        freight_class: document.getElementById('bolFreight').value,
        notes: document.getElementById('bolNotes').value,
        hazmat: document.getElementById('bolHazmat').checked,
        items: items,
        status: sigData ? 'signed' : (status || 'draft'),
        signature: sigData || null
    };
    if (!payload.bol_number) { alert('BOL number is required'); return; }
    try {
        await fetch('/api/shipping/bol-data', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
        closeModal('bolModal');
        loadBOLs();
    } catch(e) { alert('Error: ' + e.message); }
}

async function voidBOL() {
    const bolId = document.getElementById('bolId').value;
    if (!bolId || !confirm('Void this BOL? This cannot be undone.')) return;
    try {
        await fetch('/api/shipping/bol-data', {
            method: 'POST', headers: {'Content-Type':'application/json'},
            body: JSON.stringify({ id: bolId, status: 'void', action: 'void' })
        });
        closeModal('bolModal');
        loadBOLs();
    } catch(e) { alert('Error voiding BOL'); }
}

// Load selector
async function openFromLoad() {
    try {
        const resp = await fetch('/api/load-builder/loads');
        const data = await resp.json();
        loads = (data.loads || []).filter(l => l.status === 'ready');
        const sel = document.getElementById('loadSelect');
        sel.innerHTML = '<option value="">Select a finalized load...</option>';
        loads.forEach(l => {
            const o = document.createElement('option');
            o.value = l.load_id;
            o.textContent = l.load_id + ' - ' + (l.job_code || '') + ' (' + (l.items || []).length + ' items)';
            sel.appendChild(o);
        });
        document.getElementById('loadPreview').style.display = 'none';
        openModal('loadModal');
    } catch(e) { alert('Could not load loads'); }
}

function previewLoad() {
    const loadId = document.getElementById('loadSelect').value;
    const load = loads.find(l => l.load_id === loadId);
    if (!load) { document.getElementById('loadPreview').style.display = 'none'; return; }
    document.getElementById('loadPreview').style.display = '';
    document.getElementById('lpJob').textContent = load.job_code || '';
    document.getElementById('lpItems').textContent = (load.items || []).length;
    document.getElementById('lpWeight').textContent = (load.items || []).reduce((s, i) => s + (i.weight || 0), 0).toLocaleString() + ' lbs';
    document.getElementById('lpDriver').textContent = load.driver || 'Not assigned';
}

function createFromSelectedLoad() {
    const loadId = document.getElementById('loadSelect').value;
    const load = loads.find(l => l.load_id === loadId);
    if (!load) { alert('Select a load first'); return; }
    closeModal('loadModal');
    // Open BOL modal pre-filled
    openNewBOL();
    document.getElementById('bolLoadId').value = load.load_id;
    document.getElementById('bolProject').value = load.job_code || '';
    if (load.driver) document.getElementById('bolDriver').value = load.driver;
    if (load.truck_number) document.getElementById('bolTruck').value = load.truck_number;
    if (load.trailer_number) document.getElementById('bolTrailer').value = load.trailer_number;
    // Add items
    document.getElementById('bolItemsList').innerHTML = '';
    bolItemCount = 0;
    (load.items || []).forEach(it => addBOLItem(it.description || it.component || '', it.quantity || 1, it.weight || 0));
    calcTotals();
}

async function loadBOLs() {
    try {
        const resp = await fetch('/api/shipping/bol-data');
        const data = await resp.json();
        allBOLs = Array.isArray(data) ? data : (data.bols || data.data || []);
        updateStats(allBOLs);
        renderTable(allBOLs);
    } catch(e) { renderTable([]); }
}

async function loadProjectList() {
    try {
        const resp = await fetch('/api/projects/full');
        const data = await resp.json();
        projects = Array.isArray(data) ? data : (data.projects || []);
        const sel = document.getElementById('bolProject');
        sel.innerHTML = '<option value="">Select Project</option>';
        projects.forEach(p => {
            const o = document.createElement('option');
            o.value = p.id || p.job_code || '';
            o.textContent = (p.job_code || '') + ' - ' + (p.project_name || p.name || '');
            sel.appendChild(o);
        });
    } catch(e) {}
}

document.addEventListener('DOMContentLoaded', function() {
    initSignature();
    loadBOLs();
    loadProjectList();
});
</script>
"""
