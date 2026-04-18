"""
TitanForge v4 -- Field Equipment Tracker
==========================================
Equipment checkin/checkout, location tracking, maintenance due dates, utilization stats.
"""

FIELD_EQUIPMENT_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a; --tf-card: #1e293b; --tf-text: #e2e8f0;
        --tf-muted: #94a3b8; --tf-gold: #d4a843; --tf-blue: #3b82f6;
        --tf-green: #10b981; --tf-red: #ef4444; --tf-orange: #f59e0b;
    }
    .equip-container {
        max-width: 1400px; margin: 0 auto; padding: 24px 32px;
        font-family: 'Inter', 'Segoe UI', sans-serif; color: var(--tf-text);
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

    .toolbar {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 20px; flex-wrap: wrap; gap: 12px;
    }
    .toolbar-left { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
    .toolbar input[type="text"], .toolbar select {
        background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06);
        border-radius: 8px; padding: 10px 16px; color: var(--tf-text); font-size: 14px;
    }
    .toolbar input:focus, .toolbar select:focus { outline: none; border-color: var(--tf-blue); }
    .btn { padding: 10px 20px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
    .btn-primary { background: var(--tf-gold); color: #0f172a; }
    .btn-primary:hover { background: #e0b44e; }
    .btn-secondary { background: var(--tf-card); color: var(--tf-text); border: 1px solid rgba(255,255,255,0.06); }
    .btn-sm { padding: 6px 14px; font-size: 12px; }
    .btn-success { background: var(--tf-green); color: #fff; }
    .btn-danger { background: var(--tf-red); color: #fff; }

    .cards-grid {
        display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
        gap: 16px; margin-bottom: 20px;
    }
    .equip-card {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06);
        padding: 24px; transition: border-color 0.2s, transform 0.15s; cursor: pointer;
    }
    .equip-card:hover { border-color: var(--tf-blue); transform: translateY(-2px); }
    .equip-card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
    .equip-card-header h3 { font-size: 16px; font-weight: 700; margin: 0; }
    .equip-card-header .id { font-size: 12px; color: var(--tf-muted); margin-top: 2px; }
    .equip-meta { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; }
    .equip-meta-item .meta-label { font-size: 11px; color: var(--tf-muted); text-transform: uppercase; letter-spacing: 0.3px; }
    .equip-meta-item .meta-value { font-size: 14px; font-weight: 600; margin-top: 2px; }
    .equip-card-actions { display: flex; gap: 8px; }

    .badge { display: inline-block; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
    .badge-available { background: rgba(16,185,129,0.15); color: var(--tf-green); }
    .badge-checked-out { background: rgba(59,130,246,0.15); color: var(--tf-blue); }
    .badge-maintenance { background: rgba(245,158,11,0.15); color: var(--tf-orange); }
    .badge-retired { background: rgba(239,68,68,0.15); color: var(--tf-red); }

    .utilization-bar {
        height: 6px; background: rgba(255,255,255,0.06); border-radius: 3px;
        overflow: hidden; margin-top: 8px;
    }
    .utilization-bar .fill { height: 100%; border-radius: 3px; transition: width 0.3s; }

    .empty-state { text-align: center; padding: 60px 20px; color: var(--tf-muted); }
    .empty-state .icon { font-size: 48px; margin-bottom: 16px; opacity: 0.5; }
    .empty-state h3 { font-size: 18px; color: var(--tf-text); margin-bottom: 8px; }
    .empty-state p { font-size: 14px; max-width: 400px; margin: 0 auto 20px; }

    .modal-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 1000; align-items: center; justify-content: center; }
    .modal-overlay.active { display: flex; }
    .modal { background: var(--tf-card); border-radius: 16px; padding: 32px; width: 90%; max-width: 600px; max-height: 90vh; overflow-y: auto; border: 1px solid rgba(255,255,255,0.08); }
    .modal h2 { font-size: 22px; font-weight: 800; margin: 0 0 24px 0; }
    .modal-close { float: right; background: none; border: none; color: var(--tf-muted); font-size: 24px; cursor: pointer; }
    .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .form-group { margin-bottom: 16px; }
    .form-group label { display: block; font-size: 13px; font-weight: 600; color: var(--tf-muted); margin-bottom: 6px; }
    .form-group input, .form-group select, .form-group textarea {
        width: 100%; background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px;
    }
    .form-group textarea { min-height: 60px; resize: vertical; }
    .form-group input:focus, .form-group select:focus { outline: none; border-color: var(--tf-blue); }
    .form-full { grid-column: 1 / -1; }
    .modal-actions { display: flex; gap: 10px; justify-content: flex-end; margin-top: 24px; }

/* ── Responsive ── */
@media (max-width: 768px) {
    .page-header h1 { font-size: 22px; }
    .toolbar { flex-direction: column; align-items: stretch; }
    .toolbar input[type="text"] { width: 100%; }
    .stat-row { grid-template-columns: 1fr 1fr; gap: 10px; }
    .modal-overlay .modal, .modal { width: 95%; max-width: 95vw; margin: 20px auto; padding: 20px; }
    .cards-grid { grid-template-columns: 1fr; }
    .form-grid { grid-template-columns: 1fr; }
}
@media (max-width: 480px) {
    .stat-row { grid-template-columns: 1fr; }
    .toolbar { gap: 8px; }
}
</style>

<div class="equip-container">
    <div class="page-header">
        <h1>Field Equipment Tracker</h1>
        <p>Track equipment checkout, location, maintenance schedules, and utilization rates</p>
    </div>

    <div class="stat-row">
        <div class="stat-card stat-gold"><div class="label">Total Equipment</div><div class="value" id="stat-total">0</div></div>
        <div class="stat-card stat-green"><div class="label">Available</div><div class="value" id="stat-available">0</div></div>
        <div class="stat-card stat-blue"><div class="label">Checked Out</div><div class="value" id="stat-out">0</div></div>
        <div class="stat-card stat-red"><div class="label">Maintenance Due</div><div class="value" id="stat-maint">0</div></div>
    </div>

    <div class="toolbar">
        <div class="toolbar-left">
            <input type="text" id="searchInput" placeholder="Search equipment..." oninput="renderEquipment()">
            <select id="filterStatus" onchange="renderEquipment()">
                <option value="">All Status</option>
                <option value="available">Available</option>
                <option value="checked_out">Checked Out</option>
                <option value="maintenance">In Maintenance</option>
                <option value="retired">Retired</option>
            </select>
            <select id="filterCategory" onchange="renderEquipment()">
                <option value="">All Categories</option>
                <option value="crane">Cranes</option>
                <option value="welding">Welding</option>
                <option value="power_tools">Power Tools</option>
                <option value="hand_tools">Hand Tools</option>
                <option value="vehicles">Vehicles</option>
                <option value="safety">Safety Equipment</option>
            </select>
        </div>
        <div style="display:flex;gap:10px;">
            <button class="btn btn-secondary" onclick="toggleView()">Toggle View</button>
            <button class="btn btn-primary" onclick="openEquipModal()">+ Add Equipment</button>
        </div>
    </div>

    <div class="cards-grid" id="equipGrid"></div>

    <div class="empty-state" id="emptyState">
        <div class="icon">&#128295;</div>
        <h3>No Equipment Tracked</h3>
        <p>Add field equipment to start tracking checkout status, location, and maintenance schedules.</p>
        <button class="btn btn-primary" onclick="openEquipModal()">+ Add Equipment</button>
    </div>
</div>

<!-- Equipment Modal -->
<div class="modal-overlay" id="equipModal">
    <div class="modal">
        <button class="modal-close" onclick="closeModal('equipModal')">&times;</button>
        <h2 id="equipModalTitle">Add Equipment</h2>
        <form id="equipForm" onsubmit="saveEquipment(event)">
            <div class="form-grid">
                <div class="form-group"><label>Equipment Name</label><input type="text" id="equipName" required></div>
                <div class="form-group"><label>Equipment ID / Tag</label><input type="text" id="equipId" placeholder="e.g. EQ-001"></div>
                <div class="form-group"><label>Category</label>
                    <select id="equipCategory">
                        <option value="crane">Crane</option><option value="welding">Welding</option>
                        <option value="power_tools">Power Tools</option><option value="hand_tools">Hand Tools</option>
                        <option value="vehicles">Vehicle</option><option value="safety">Safety</option>
                    </select>
                </div>
                <div class="form-group"><label>Serial Number</label><input type="text" id="equipSerial"></div>
                <div class="form-group"><label>Location / Job Site</label><input type="text" id="equipLocation"></div>
                <div class="form-group"><label>Assigned To</label><input type="text" id="equipAssigned"></div>
                <div class="form-group"><label>Last Maintenance</label><input type="date" id="equipLastMaint"></div>
                <div class="form-group"><label>Next Maintenance Due</label><input type="date" id="equipNextMaint"></div>
                <div class="form-group form-full"><label>Notes</label><textarea id="equipNotes"></textarea></div>
            </div>
            <div class="modal-actions">
                <button type="button" class="btn btn-secondary" onclick="closeModal('equipModal')">Cancel</button>
                <button type="submit" class="btn btn-primary">Save Equipment</button>
            </div>
        </form>
    </div>
</div>

<!-- Checkout Modal -->
<div class="modal-overlay" id="checkoutModal">
    <div class="modal">
        <button class="modal-close" onclick="closeModal('checkoutModal')">&times;</button>
        <h2>Check Out Equipment</h2>
        <form id="checkoutForm" onsubmit="processCheckout(event)">
            <input type="hidden" id="checkoutEquipId">
            <div class="form-group"><label>Checked Out To</label><input type="text" id="checkoutPerson" required></div>
            <div class="form-group"><label>Job Site / Location</label><input type="text" id="checkoutLocation" required></div>
            <div class="form-group"><label>Expected Return Date</label><input type="date" id="checkoutReturn"></div>
            <div class="form-group"><label>Notes</label><textarea id="checkoutNotes"></textarea></div>
            <div class="modal-actions">
                <button type="button" class="btn btn-secondary" onclick="closeModal('checkoutModal')">Cancel</button>
                <button type="submit" class="btn btn-primary">Check Out</button>
            </div>
        </form>
    </div>
</div>

<script>
    let equipment = [];
    let editingId = null;

    async function loadEquipment() {
        try {
            const resp = await fetch('/api/field/equipment');
            const data = await resp.json();
            equipment = data.equipment || [];
            renderEquipment();
            updateStats();
        } catch(e) { console.error('Failed to load equipment:', e); renderEquipment(); }
    }

    function renderEquipment() {
        const grid = document.getElementById('equipGrid');
        const empty = document.getElementById('emptyState');
        const search = document.getElementById('searchInput').value.toLowerCase();
        const statusFilter = document.getElementById('filterStatus').value;
        const catFilter = document.getElementById('filterCategory').value;

        let filtered = equipment.filter(e => {
            if (search && !JSON.stringify(e).toLowerCase().includes(search)) return false;
            if (statusFilter && e.status !== statusFilter) return false;
            if (catFilter && e.category !== catFilter) return false;
            return true;
        });

        if (filtered.length === 0) { grid.innerHTML = ''; empty.style.display = 'block'; return; }
        empty.style.display = 'none';

        const statusCls = { available: 'badge-available', checked_out: 'badge-checked-out', maintenance: 'badge-maintenance', retired: 'badge-retired' };
        const statusLabel = { available: 'Available', checked_out: 'Checked Out', maintenance: 'Maintenance', retired: 'Retired' };
        const utilColors = { high: '#10b981', medium: '#f59e0b', low: '#ef4444' };

        grid.innerHTML = filtered.map(eq => {
            const util = eq.utilization || 0;
            const utilLevel = util > 70 ? 'high' : util > 40 ? 'medium' : 'low';
            return `
            <div class="equip-card" onclick="viewEquipment('${eq.id}')">
                <div class="equip-card-header">
                    <div><h3>${eq.name || ''}</h3><div class="id">${eq.equipment_id || eq.id || ''}</div></div>
                    <span class="badge ${statusCls[eq.status] || 'badge-available'}">${statusLabel[eq.status] || eq.status}</span>
                </div>
                <div class="equip-meta">
                    <div class="equip-meta-item"><div class="meta-label">Category</div><div class="meta-value">${eq.category || ''}</div></div>
                    <div class="equip-meta-item"><div class="meta-label">Location</div><div class="meta-value">${eq.location || 'N/A'}</div></div>
                    <div class="equip-meta-item"><div class="meta-label">Assigned To</div><div class="meta-value">${eq.assigned_to || 'Unassigned'}</div></div>
                    <div class="equip-meta-item"><div class="meta-label">Next Maintenance</div><div class="meta-value">${eq.next_maintenance || 'N/A'}</div></div>
                </div>
                <div style="font-size:12px;color:var(--tf-muted)">Utilization: ${util}%</div>
                <div class="utilization-bar"><div class="fill" style="width:${util}%;background:${utilColors[utilLevel]}"></div></div>
                <div class="equip-card-actions" style="margin-top:12px;">
                    ${eq.status === 'available' ? `<button class="btn btn-sm btn-success" onclick="event.stopPropagation();openCheckout('${eq.id}')">Check Out</button>` : ''}
                    ${eq.status === 'checked_out' ? `<button class="btn btn-sm btn-secondary" onclick="event.stopPropagation();checkinEquip('${eq.id}')">Check In</button>` : ''}
                    <button class="btn btn-sm btn-secondary" onclick="event.stopPropagation();editEquipment('${eq.id}')">Edit</button>
                </div>
            </div>`;
        }).join('');
    }

    function updateStats() {
        document.getElementById('stat-total').textContent = equipment.length;
        document.getElementById('stat-available').textContent = equipment.filter(e => e.status === 'available').length;
        document.getElementById('stat-out').textContent = equipment.filter(e => e.status === 'checked_out').length;
        document.getElementById('stat-maint').textContent = equipment.filter(e => e.status === 'maintenance').length;
    }

    function openEquipModal() {
        editingId = null;
        document.getElementById('equipModalTitle').textContent = 'Add Equipment';
        document.getElementById('equipForm').reset();
        document.getElementById('equipModal').classList.add('active');
    }

    function editEquipment(id) {
        const eq = equipment.find(e => e.id === id);
        if (!eq) return;
        editingId = id;
        document.getElementById('equipModalTitle').textContent = 'Edit Equipment';
        document.getElementById('equipName').value = eq.name || '';
        document.getElementById('equipId').value = eq.equipment_id || '';
        document.getElementById('equipCategory').value = eq.category || '';
        document.getElementById('equipSerial').value = eq.serial_number || '';
        document.getElementById('equipLocation').value = eq.location || '';
        document.getElementById('equipAssigned').value = eq.assigned_to || '';
        document.getElementById('equipLastMaint').value = eq.last_maintenance || '';
        document.getElementById('equipNextMaint').value = eq.next_maintenance || '';
        document.getElementById('equipNotes').value = eq.notes || '';
        document.getElementById('equipModal').classList.add('active');
    }

    function viewEquipment(id) { editEquipment(id); }

    function openCheckout(id) {
        document.getElementById('checkoutEquipId').value = id;
        document.getElementById('checkoutForm').reset();
        document.getElementById('checkoutEquipId').value = id;
        document.getElementById('checkoutModal').classList.add('active');
    }

    async function saveEquipment(e) {
        e.preventDefault();
        const payload = {
            id: editingId, name: document.getElementById('equipName').value,
            equipment_id: document.getElementById('equipId').value,
            category: document.getElementById('equipCategory').value,
            serial_number: document.getElementById('equipSerial').value,
            location: document.getElementById('equipLocation').value,
            assigned_to: document.getElementById('equipAssigned').value,
            last_maintenance: document.getElementById('equipLastMaint').value,
            next_maintenance: document.getElementById('equipNextMaint').value,
            notes: document.getElementById('equipNotes').value
        };
        try {
            await fetch('/api/field/equipment', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
            closeModal('equipModal');
            loadEquipment();
        } catch(e) { alert('Error saving equipment'); }
    }

    async function processCheckout(e) {
        e.preventDefault();
        const payload = {
            equipment_id: document.getElementById('checkoutEquipId').value,
            checked_out_to: document.getElementById('checkoutPerson').value,
            location: document.getElementById('checkoutLocation').value,
            expected_return: document.getElementById('checkoutReturn').value,
            notes: document.getElementById('checkoutNotes').value
        };
        try {
            await fetch('/api/field/equipment/checkout', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
            closeModal('checkoutModal');
            loadEquipment();
        } catch(e) { alert('Error checking out equipment'); }
    }

    async function checkinEquip(id) {
        if (!confirm('Check in this equipment?')) return;
        try {
            await fetch('/api/field/equipment/checkin', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ equipment_id: id }) });
            loadEquipment();
        } catch(e) { alert('Error checking in equipment'); }
    }

    function toggleView() { /* toggle between card and table view */ }
    function closeModal(id) { document.getElementById(id).classList.remove('active'); }
    window.addEventListener('click', e => { if (e.target.classList.contains('modal-overlay')) e.target.classList.remove('active'); });

    document.addEventListener('DOMContentLoaded', loadEquipment);
</script>
"""
