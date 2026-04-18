"""
TitanForge v4 -- Safety Equipment Inventory
=============================================
PPE tracking, inspection dates, replacement schedule, assignment, compliance status.
"""

SAFETY_EQUIPMENT_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a; --tf-card: #1e293b; --tf-text: #e2e8f0;
        --tf-muted: #94a3b8; --tf-gold: #d4a843; --tf-blue: #3b82f6;
        --tf-green: #10b981; --tf-red: #ef4444; --tf-orange: #f59e0b;
    }
    .se-container {
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
    .stat-orange .value { color: var(--tf-orange); }

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

    .data-table {
        width: 100%; border-collapse: collapse; background: var(--tf-card);
        border-radius: 12px; overflow: hidden; border: 1px solid rgba(255,255,255,0.06);
    }
    .data-table th {
        padding: 14px 16px; text-align: left; font-size: 11px; font-weight: 700;
        color: var(--tf-muted); text-transform: uppercase; letter-spacing: 0.5px;
        background: rgba(0,0,0,0.2); border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .data-table td { padding: 14px 16px; font-size: 14px; border-bottom: 1px solid rgba(255,255,255,0.04); }
    .data-table tbody tr { cursor: pointer; transition: background 0.15s; }
    .data-table tbody tr:hover { background: rgba(59,130,246,0.06); }

    .badge { display: inline-block; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
    .badge-compliant { background: rgba(16,185,129,0.15); color: var(--tf-green); }
    .badge-expiring { background: rgba(245,158,11,0.15); color: var(--tf-orange); }
    .badge-expired { background: rgba(239,68,68,0.15); color: var(--tf-red); }
    .badge-assigned { background: rgba(59,130,246,0.15); color: var(--tf-blue); }
    .badge-available { background: rgba(16,185,129,0.15); color: var(--tf-green); }

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
    .form-group input:focus, .form-group select:focus { outline: none; border-color: var(--tf-blue); }
    .form-full { grid-column: 1 / -1; }
    .modal-actions { display: flex; gap: 10px; justify-content: flex-end; margin-top: 24px; }
</style>

<div class="se-container">
    <div class="page-header">
        <h1>Safety Equipment Inventory</h1>
        <p>Track PPE inventory, inspection dates, replacement schedules, and crew assignments for compliance</p>
    </div>

    <div class="stat-row">
        <div class="stat-card stat-gold"><div class="label">Total Items</div><div class="value" id="stat-total">0</div></div>
        <div class="stat-card stat-green"><div class="label">Compliant</div><div class="value" id="stat-compliant">0</div></div>
        <div class="stat-card stat-orange"><div class="label">Expiring Soon</div><div class="value" id="stat-expiring">0</div></div>
        <div class="stat-card stat-red"><div class="label">Expired / Replace</div><div class="value" id="stat-expired">0</div></div>
        <div class="stat-card stat-blue"><div class="label">Assigned</div><div class="value" id="stat-assigned">0</div></div>
    </div>

    <div class="toolbar">
        <div class="toolbar-left">
            <input type="text" id="searchInput" placeholder="Search equipment..." oninput="renderEquipment()">
            <select id="filterType" onchange="renderEquipment()">
                <option value="">All Types</option>
                <option value="hard_hat">Hard Hats</option>
                <option value="harness">Fall Harness</option>
                <option value="gloves">Gloves</option>
                <option value="glasses">Safety Glasses</option>
                <option value="boots">Steel Toe Boots</option>
                <option value="vest">Hi-Vis Vest</option>
                <option value="respirator">Respirator</option>
                <option value="ear_protection">Ear Protection</option>
                <option value="fire_extinguisher">Fire Extinguisher</option>
                <option value="first_aid">First Aid Kit</option>
            </select>
            <select id="filterCompliance" onchange="renderEquipment()">
                <option value="">All Status</option>
                <option value="compliant">Compliant</option>
                <option value="expiring">Expiring Soon</option>
                <option value="expired">Expired</option>
            </select>
        </div>
        <button class="btn btn-primary" onclick="openItemModal()">+ Add Equipment</button>
    </div>

    <table class="data-table">
        <thead>
            <tr>
                <th>Item ID</th>
                <th>Type</th>
                <th>Description</th>
                <th>Assigned To</th>
                <th>Last Inspected</th>
                <th>Next Inspection</th>
                <th>Replace By</th>
                <th>Compliance</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody id="equipTable"></tbody>
    </table>

    <div class="empty-state" id="emptyState">
        <div class="icon">&#129521;</div>
        <h3>No Safety Equipment Tracked</h3>
        <p>Add PPE and safety equipment to track inspections, assignments, and compliance status.</p>
        <button class="btn btn-primary" onclick="openItemModal()">+ Add Equipment</button>
    </div>
</div>

<!-- Equipment Modal -->
<div class="modal-overlay" id="itemModal">
    <div class="modal">
        <button class="modal-close" onclick="closeModal('itemModal')">&times;</button>
        <h2 id="itemModalTitle">Add Safety Equipment</h2>
        <form id="itemForm" onsubmit="saveItem(event)">
            <div class="form-grid">
                <div class="form-group"><label>Equipment Type</label>
                    <select id="itemType" required>
                        <option value="">Select Type</option>
                        <option value="hard_hat">Hard Hat</option>
                        <option value="harness">Fall Harness</option>
                        <option value="gloves">Gloves</option>
                        <option value="glasses">Safety Glasses</option>
                        <option value="boots">Steel Toe Boots</option>
                        <option value="vest">Hi-Vis Vest</option>
                        <option value="respirator">Respirator</option>
                        <option value="ear_protection">Ear Protection</option>
                        <option value="fire_extinguisher">Fire Extinguisher</option>
                        <option value="first_aid">First Aid Kit</option>
                    </select>
                </div>
                <div class="form-group"><label>Item ID / Serial</label><input type="text" id="itemId" placeholder="e.g. PPE-001"></div>
                <div class="form-group form-full"><label>Description</label><input type="text" id="itemDesc" placeholder="Brand, model, size..."></div>
                <div class="form-group"><label>Assigned To</label><input type="text" id="itemAssigned" placeholder="Crew member name"></div>
                <div class="form-group"><label>Quantity</label><input type="number" id="itemQty" value="1" min="1"></div>
                <div class="form-group"><label>Last Inspection Date</label><input type="date" id="itemLastInspect"></div>
                <div class="form-group"><label>Next Inspection Due</label><input type="date" id="itemNextInspect"></div>
                <div class="form-group"><label>Purchase Date</label><input type="date" id="itemPurchaseDate"></div>
                <div class="form-group"><label>Replace By Date</label><input type="date" id="itemReplaceDate"></div>
                <div class="form-group form-full"><label>Notes</label><textarea id="itemNotes" placeholder="Condition notes, inspection results..." style="min-height:60px;resize:vertical;"></textarea></div>
            </div>
            <div class="modal-actions">
                <button type="button" class="btn btn-secondary" onclick="closeModal('itemModal')">Cancel</button>
                <button type="submit" class="btn btn-primary">Save Equipment</button>
            </div>
        </form>
    </div>
</div>

<script>
    let equipment = [];
    let editingId = null;

    async function loadEquipment() {
        try {
            const resp = await fetch('/api/safety/equipment');
            const data = await resp.json();
            equipment = data.equipment || [];
            renderEquipment();
            updateStats();
        } catch(e) { console.error('Failed to load safety equipment:', e); renderEquipment(); }
    }

    function getCompliance(item) {
        if (!item.next_inspection && !item.replace_by) return 'compliant';
        const now = new Date();
        const soon = new Date(now.getTime() + 30*24*60*60*1000);
        const nextInsp = item.next_inspection ? new Date(item.next_inspection) : null;
        const replaceBy = item.replace_by ? new Date(item.replace_by) : null;
        if ((nextInsp && nextInsp < now) || (replaceBy && replaceBy < now)) return 'expired';
        if ((nextInsp && nextInsp < soon) || (replaceBy && replaceBy < soon)) return 'expiring';
        return 'compliant';
    }

    function renderEquipment() {
        const tbody = document.getElementById('equipTable');
        const empty = document.getElementById('emptyState');
        const search = document.getElementById('searchInput').value.toLowerCase();
        const typeFilter = document.getElementById('filterType').value;
        const compFilter = document.getElementById('filterCompliance').value;

        let filtered = equipment.filter(eq => {
            if (search && !JSON.stringify(eq).toLowerCase().includes(search)) return false;
            if (typeFilter && eq.type !== typeFilter) return false;
            if (compFilter && getCompliance(eq) !== compFilter) return false;
            return true;
        });

        if (filtered.length === 0) { tbody.innerHTML = ''; empty.style.display = 'block'; return; }
        empty.style.display = 'none';

        const compCls = { compliant: 'badge-compliant', expiring: 'badge-expiring', expired: 'badge-expired' };
        const typeLabels = { hard_hat: 'Hard Hat', harness: 'Fall Harness', gloves: 'Gloves', glasses: 'Safety Glasses', boots: 'Steel Toe Boots', vest: 'Hi-Vis Vest', respirator: 'Respirator', ear_protection: 'Ear Protection', fire_extinguisher: 'Fire Extinguisher', first_aid: 'First Aid Kit' };

        tbody.innerHTML = filtered.map(eq => {
            const comp = getCompliance(eq);
            return `
            <tr onclick="editItem('${eq.id}')">
                <td style="font-weight:600">${eq.item_id || eq.id || ''}</td>
                <td>${typeLabels[eq.type] || eq.type || ''}</td>
                <td>${eq.description || ''}</td>
                <td>${eq.assigned_to || '<span style="color:var(--tf-muted)">Unassigned</span>'}</td>
                <td>${eq.last_inspection || '-'}</td>
                <td>${eq.next_inspection || '-'}</td>
                <td>${eq.replace_by || '-'}</td>
                <td><span class="badge ${compCls[comp]}">${comp}</span></td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="event.stopPropagation();editItem('${eq.id}')">Edit</button>
                    <button class="btn btn-sm btn-secondary" onclick="event.stopPropagation();inspectItem('${eq.id}')">Inspect</button>
                </td>
            </tr>`;
        }).join('');
    }

    function updateStats() {
        document.getElementById('stat-total').textContent = equipment.length;
        document.getElementById('stat-compliant').textContent = equipment.filter(e => getCompliance(e) === 'compliant').length;
        document.getElementById('stat-expiring').textContent = equipment.filter(e => getCompliance(e) === 'expiring').length;
        document.getElementById('stat-expired').textContent = equipment.filter(e => getCompliance(e) === 'expired').length;
        document.getElementById('stat-assigned').textContent = equipment.filter(e => e.assigned_to).length;
    }

    function openItemModal() {
        editingId = null;
        document.getElementById('itemModalTitle').textContent = 'Add Safety Equipment';
        document.getElementById('itemForm').reset();
        document.getElementById('itemModal').classList.add('active');
    }

    function editItem(id) {
        const eq = equipment.find(e => e.id === id);
        if (!eq) return;
        editingId = id;
        document.getElementById('itemModalTitle').textContent = 'Edit Safety Equipment';
        document.getElementById('itemType').value = eq.type || '';
        document.getElementById('itemId').value = eq.item_id || '';
        document.getElementById('itemDesc').value = eq.description || '';
        document.getElementById('itemAssigned').value = eq.assigned_to || '';
        document.getElementById('itemQty').value = eq.quantity || 1;
        document.getElementById('itemLastInspect').value = eq.last_inspection || '';
        document.getElementById('itemNextInspect').value = eq.next_inspection || '';
        document.getElementById('itemPurchaseDate').value = eq.purchase_date || '';
        document.getElementById('itemReplaceDate').value = eq.replace_by || '';
        document.getElementById('itemNotes').value = eq.notes || '';
        document.getElementById('itemModal').classList.add('active');
    }

    async function inspectItem(id) {
        if (!confirm('Record inspection as passed for today?')) return;
        try {
            await fetch('/api/safety/equipment/inspect', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ id: id, date: new Date().toISOString().split('T')[0] }) });
            loadEquipment();
        } catch(e) { alert('Error recording inspection'); }
    }

    async function saveItem(e) {
        e.preventDefault();
        const payload = {
            id: editingId, type: document.getElementById('itemType').value,
            item_id: document.getElementById('itemId').value,
            description: document.getElementById('itemDesc').value,
            assigned_to: document.getElementById('itemAssigned').value,
            quantity: parseInt(document.getElementById('itemQty').value) || 1,
            last_inspection: document.getElementById('itemLastInspect').value,
            next_inspection: document.getElementById('itemNextInspect').value,
            purchase_date: document.getElementById('itemPurchaseDate').value,
            replace_by: document.getElementById('itemReplaceDate').value,
            notes: document.getElementById('itemNotes').value
        };
        try {
            await fetch('/api/safety/equipment', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
            closeModal('itemModal');
            loadEquipment();
        } catch(e) { alert('Error saving equipment'); }
    }

    function closeModal(id) { document.getElementById(id).classList.remove('active'); }
    window.addEventListener('click', e => { if (e.target.classList.contains('modal-overlay')) e.target.classList.remove('active'); });

    document.addEventListener('DOMContentLoaded', loadEquipment);
</script>
"""
