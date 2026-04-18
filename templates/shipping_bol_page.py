"""
TitanForge v4 — Bills of Lading
==================================
BOL list, create BOL, item list, weights, carrier info, PDF generation, signature.
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
    }
    .bol-container {
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
    .btn-blue { background: var(--tf-blue); color: #fff; border: none; border-radius: 8px; padding: 10px 20px; font-weight: 700; font-size: 14px; cursor: pointer; }
    .btn-outline { background: transparent; color: var(--tf-muted); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 10px 20px; font-weight: 600; font-size: 14px; cursor: pointer; }
    .btn-outline:hover { border-color: var(--tf-gold); color: var(--tf-gold); }
    .btn-sm { padding: 6px 14px; font-size: 12px; border-radius: 6px; }
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
    .badge { display: inline-block; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; }
    .badge-draft { background: rgba(148,163,184,0.2); color: #94a3b8; }
    .badge-final { background: rgba(34,197,94,0.2); color: #4ade80; }
    .badge-signed { background: rgba(59,130,246,0.2); color: #60a5fa; }
    .badge-void { background: rgba(239,68,68,0.2); color: #f87171; }
    .empty-state { text-align: center; padding: 60px 20px; color: var(--tf-muted); }
    .empty-state h3 { font-size: 18px; margin-bottom: 8px; color: var(--tf-text); }
    .loading { text-align: center; padding: 40px; color: var(--tf-muted); }
    .modal-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 1000; justify-content: center; align-items: center; }
    .modal-overlay.active { display: flex; }
    .modal { background: var(--tf-card); border-radius: 12px; padding: 28px; width: 640px; max-width: 90vw; border: 1px solid rgba(255,255,255,0.1); max-height: 85vh; overflow-y: auto; }
    .modal h2 { font-size: 20px; margin: 0 0 20px 0; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 24px; }
    .form-group { margin-bottom: 16px; }
    .form-group label { display: block; font-size: 13px; font-weight: 600; color: var(--tf-muted); margin-bottom: 6px; }
    .form-group input, .form-group select, .form-group textarea {
        width: 100%; background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px; font-family: inherit; box-sizing: border-box;
    }
    .form-group textarea { min-height: 60px; resize: vertical; }
    .items-list { margin-top: 8px; }
    .item-row { display: flex; gap: 8px; align-items: center; margin-bottom: 8px; }
    .item-row input { flex: 1; }
    .item-row input.short { width: 80px; flex: none; }
    .btn-remove { background: rgba(239,68,68,0.2); color: #f87171; border: none; border-radius: 6px; padding: 8px 10px; cursor: pointer; font-size: 12px; }
    .sig-canvas { border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; background: #0f172a; cursor: crosshair; }
</style>

<div class="bol-container">
    <div class="page-header">
        <h1>Bills of Lading</h1>
        <p>Create and manage BOLs, generate PDFs, and capture signatures</p>
    </div>
    <div class="stats-row">
        <div class="stat-card"><div class="stat-label">Total BOLs</div><div class="stat-value" id="statTotal" style="color:var(--tf-text);">--</div></div>
        <div class="stat-card"><div class="stat-label">Draft</div><div class="stat-value" id="statDraft" style="color:var(--tf-muted);">--</div></div>
        <div class="stat-card"><div class="stat-label">Finalized</div><div class="stat-value" id="statFinal" style="color:#4ade80;">--</div></div>
        <div class="stat-card"><div class="stat-label">Signed</div><div class="stat-value" id="statSigned" style="color:var(--tf-blue);">--</div></div>
    </div>
    <div class="toolbar">
        <div style="display:flex;gap:10px;align-items:center;">
            <input type="text" id="bolSearch" placeholder="Search BOLs..." oninput="filterBOLs()">
            <select id="filterStatus" onchange="filterBOLs()">
                <option value="">All Status</option>
                <option value="draft">Draft</option>
                <option value="final">Finalized</option>
                <option value="signed">Signed</option>
                <option value="void">Void</option>
            </select>
        </div>
        <button class="btn-gold" onclick="openNewBOL()">+ New BOL</button>
    </div>
    <div class="data-card">
        <div id="bolTableWrap" class="loading">Loading BOLs...</div>
    </div>
</div>

<div class="modal-overlay" id="bolModal">
    <div class="modal">
        <h2 id="bolModalTitle">New Bill of Lading</h2>
        <input type="hidden" id="bolId">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div class="form-group"><label>BOL Number</label><input type="text" id="bolNumber" placeholder="Auto-generated"></div>
            <div class="form-group"><label>Date</label><input type="date" id="bolDate"></div>
        </div>
        <div class="form-group"><label>Project / Job Code</label><input type="text" id="bolProject" placeholder="Job code"></div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div class="form-group"><label>Shipper</label><input type="text" id="bolShipper" value="Titan Carports"></div>
            <div class="form-group"><label>Consignee</label><input type="text" id="bolConsignee" placeholder="Receiving party"></div>
            <div class="form-group"><label>Carrier</label><input type="text" id="bolCarrier" placeholder="Carrier name"></div>
            <div class="form-group"><label>Trailer #</label><input type="text" id="bolTrailer" placeholder="Trailer number"></div>
        </div>
        <div class="form-group">
            <label>Line Items</label>
            <div class="items-list" id="bolItemsList"></div>
            <button class="btn-outline btn-sm" onclick="addBOLItem()" style="margin-top:6px;">+ Add Item</button>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div class="form-group"><label>Total Weight (lbs)</label><input type="number" id="bolWeight" placeholder="0"></div>
            <div class="form-group"><label>Total Pieces</label><input type="number" id="bolPieces" placeholder="0"></div>
        </div>
        <div class="form-group"><label>Notes</label><textarea id="bolNotes" placeholder="Special instructions..."></textarea></div>
        <div class="modal-actions">
            <button class="btn-outline" onclick="closeModal('bolModal')">Cancel</button>
            <button class="btn-blue" onclick="generatePDF()" style="margin-right:auto;">Generate PDF</button>
            <button class="btn-gold" onclick="saveBOL()">Save BOL</button>
        </div>
    </div>
</div>

<script>
let allBOLs = [];
let bolItemCount = 0;

function openModal(id) { document.getElementById(id).classList.add('active'); }
function closeModal(id) { document.getElementById(id).classList.remove('active'); }
document.querySelectorAll('.modal-overlay').forEach(m => m.addEventListener('click', function(e) { if (e.target === this) closeModal(this.id); }));

function addBOLItem(desc, qty, weight) {
    bolItemCount++;
    const div = document.createElement('div');
    div.className = 'item-row';
    div.id = 'bol-item-' + bolItemCount;
    div.innerHTML = '<input type="text" placeholder="Description" value="' + (desc||'') + '">' +
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
    ['bolId','bolProject','bolConsignee','bolCarrier','bolTrailer','bolNotes'].forEach(id => document.getElementById(id).value = '');
    document.getElementById('bolNumber').value = 'BOL-' + Date.now().toString().slice(-6);
    document.getElementById('bolDate').value = new Date().toISOString().slice(0,10);
    document.getElementById('bolShipper').value = 'Titan Carports';
    document.getElementById('bolWeight').value = '';
    document.getElementById('bolPieces').value = '';
    document.getElementById('bolItemsList').innerHTML = '';
    bolItemCount = 0;
    addBOLItem();
    openModal('bolModal');
}

function editBOL(bol) {
    document.getElementById('bolModalTitle').textContent = 'Edit BOL';
    document.getElementById('bolId').value = bol.id || '';
    document.getElementById('bolNumber').value = bol.bol_number || '';
    document.getElementById('bolDate').value = bol.date || '';
    document.getElementById('bolProject').value = bol.project || '';
    document.getElementById('bolShipper').value = bol.shipper || '';
    document.getElementById('bolConsignee').value = bol.consignee || '';
    document.getElementById('bolCarrier').value = bol.carrier || '';
    document.getElementById('bolTrailer').value = bol.trailer || '';
    document.getElementById('bolWeight').value = bol.total_weight || '';
    document.getElementById('bolPieces').value = bol.total_pieces || '';
    document.getElementById('bolNotes').value = bol.notes || '';
    document.getElementById('bolItemsList').innerHTML = '';
    bolItemCount = 0;
    (bol.items || []).forEach(it => addBOLItem(it.description, it.quantity, it.weight));
    openModal('bolModal');
}

function renderTable(bols) {
    const wrap = document.getElementById('bolTableWrap');
    if (!bols.length) {
        wrap.innerHTML = '<div class="empty-state"><h3>No Bills of Lading</h3><p>Create a BOL to document shipment contents.</p></div>';
        return;
    }
    let html = '<table class="data-table"><thead><tr><th>BOL #</th><th>Date</th><th>Project</th><th>Consignee</th><th>Carrier</th><th>Weight</th><th>Pieces</th><th>Status</th></tr></thead><tbody>';
    bols.forEach(b => {
        const stCls = b.status === 'final' ? 'badge-final' : (b.status === 'signed' ? 'badge-signed' : (b.status === 'void' ? 'badge-void' : 'badge-draft'));
        html += '<tr onclick=\'editBOL(' + JSON.stringify(b).replace(/'/g,"&#39;") + ')\'>' +
            '<td style="font-weight:600;color:var(--tf-gold);">' + (b.bol_number || '--') + '</td>' +
            '<td>' + (b.date || '--') + '</td>' +
            '<td>' + (b.project || '--') + '</td>' +
            '<td>' + (b.consignee || '--') + '</td>' +
            '<td>' + (b.carrier || '--') + '</td>' +
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
    document.getElementById('statFinal').textContent = bols.filter(b => b.status === 'final').length;
    document.getElementById('statSigned').textContent = bols.filter(b => b.status === 'signed').length;
}

function filterBOLs() {
    const search = document.getElementById('bolSearch').value.toLowerCase();
    const status = document.getElementById('filterStatus').value;
    const filtered = allBOLs.filter(b => {
        if (search && !(b.bol_number||'').toLowerCase().includes(search) && !(b.project||'').toLowerCase().includes(search) && !(b.consignee||'').toLowerCase().includes(search)) return false;
        if (status && (b.status||'draft') !== status) return false;
        return true;
    });
    renderTable(filtered);
}

function generatePDF() {
    const num = document.getElementById('bolNumber').value;
    window.open('/api/shipping/bol/pdf/' + encodeURIComponent(num), '_blank');
}

async function saveBOL() {
    const items = [];
    document.querySelectorAll('.item-row').forEach(row => {
        const inputs = row.querySelectorAll('input');
        if (inputs[0]?.value) items.push({ description: inputs[0].value, quantity: parseInt(inputs[1]?.value)||0, weight: parseInt(inputs[2]?.value)||0 });
    });
    const payload = {
        id: document.getElementById('bolId').value || undefined,
        bol_number: document.getElementById('bolNumber').value,
        date: document.getElementById('bolDate').value,
        project: document.getElementById('bolProject').value,
        shipper: document.getElementById('bolShipper').value,
        consignee: document.getElementById('bolConsignee').value,
        carrier: document.getElementById('bolCarrier').value,
        trailer: document.getElementById('bolTrailer').value,
        total_weight: parseInt(document.getElementById('bolWeight').value) || 0,
        total_pieces: parseInt(document.getElementById('bolPieces').value) || 0,
        notes: document.getElementById('bolNotes').value,
        items: items,
        status: 'draft'
    };
    if (!payload.bol_number) { alert('BOL number is required'); return; }
    try {
        await fetch('/api/shipping/bol', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
        closeModal('bolModal');
        loadBOLs();
    } catch(e) { alert('Error: ' + e.message); }
}

async function loadBOLs() {
    try {
        const resp = await fetch('/api/shipping/bol');
        const data = await resp.json();
        allBOLs = Array.isArray(data) ? data : (data.bols || []);
        updateStats(allBOLs);
        renderTable(allBOLs);
    } catch(e) { renderTable([]); }
}

loadBOLs();
</script>
"""
