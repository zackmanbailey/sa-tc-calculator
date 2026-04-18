"""
TitanForge v4.0 — Global Work Orders Dashboard
================================================
Cross-project work order management with filtering, search,
QC queue view, and status-based organization.
"""

from templates.shared_styles import DESIGN_SYSTEM_CSS

WORK_ORDERS_GLOBAL_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TitanForge — All Work Orders</title>
<style>
""" + DESIGN_SYSTEM_CSS + """

.wog { max-width: 1400px; margin: 0 auto; padding: 24px; }

.wog-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 24px; flex-wrap: wrap; gap: 12px;
}
.wog-header h1 { font-size: 1.5rem; font-weight: 700; color: var(--tf-navy); margin: 0; }

/* Tabs */
.wog-tabs {
    display: flex; gap: 0; border-bottom: 2px solid var(--tf-border); margin-bottom: 20px;
}
.wog-tab {
    padding: 10px 20px; font-size: 0.9rem; font-weight: 600; color: var(--tf-slate);
    cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -2px;
    transition: all 0.2s; background: none; border-top: none; border-left: none; border-right: none;
}
.wog-tab:hover { color: var(--tf-blue-mid); }
.wog-tab.active { color: var(--tf-blue); border-bottom-color: var(--tf-blue); }
.wog-tab .tab-count {
    display: inline-flex; align-items: center; justify-content: center;
    min-width: 20px; height: 20px; padding: 0 6px; border-radius: 10px;
    font-size: 0.72rem; font-weight: 700; margin-left: 6px;
    background: var(--tf-blue-light); color: var(--tf-blue);
}
.wog-tab.active .tab-count { background: var(--tf-blue); color: white; }
.wog-tab-content { display: none; }
.wog-tab-content.active { display: block; }

/* Filters bar */
.wog-filters {
    display: flex; gap: 12px; align-items: center; margin-bottom: 20px; flex-wrap: wrap;
}
.wog-filters input, .wog-filters select {
    padding: 8px 14px; border: 1px solid var(--tf-border); border-radius: 8px;
    font-size: 0.85rem; font-family: var(--tf-font); background: white; color: var(--tf-navy);
}
.wog-filters input { flex: 1; min-width: 200px; }
.wog-filters input:focus, .wog-filters select:focus {
    outline: none; border-color: var(--tf-blue); box-shadow: 0 0 0 3px rgba(30,64,175,0.08);
}

/* Stats row */
.wog-stats {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 12px; margin-bottom: 24px;
}
.stat-pill {
    background: var(--tf-surface); border: 1px solid var(--tf-border);
    border-radius: 10px; padding: 14px 16px; text-align: center;
    cursor: pointer; transition: transform 0.15s, box-shadow 0.15s;
}
.stat-pill:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.06); }
.stat-pill .stat-val {
    font-size: 1.6rem; font-weight: 800; color: var(--tf-navy);
    font-family: 'SF Mono', monospace;
}
.stat-pill .stat-label {
    font-size: 0.72rem; font-weight: 600; color: var(--tf-slate);
    text-transform: uppercase; letter-spacing: 0.5px; margin-top: 2px;
}

/* WO Table */
.wo-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.wo-table th {
    text-align: left; padding: 10px 12px; font-weight: 600; color: var(--tf-slate);
    background: var(--tf-bg); border-bottom: 2px solid var(--tf-border);
    font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.5px;
}
.wo-table td {
    padding: 12px; border-bottom: 1px solid var(--tf-border); vertical-align: middle;
}
.wo-table tr:hover td { background: #F8FAFC; cursor: pointer; }
.wo-table tr:last-child td { border-bottom: none; }

/* Badges */
.status-badge {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 3px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; white-space: nowrap;
}
.status-badge.queued { background: #F1F5F9; color: #64748B; }
.status-badge.approved { background: #DBEAFE; color: #1E40AF; }
.status-badge.stickers_printed { background: #E0E7FF; color: #4338CA; }
.status-badge.staged { background: #FFF7ED; color: #C2410C; }
.status-badge.in_progress { background: #FEF3C7; color: #92400E; }
.status-badge.fabricated { background: #ECFDF5; color: #065F46; }
.status-badge.qc_pending { background: #FFF7ED; color: #9A3412; }
.status-badge.qc_approved { background: #D1FAE5; color: #065F46; }
.status-badge.qc_rejected { background: #FEE2E2; color: #991B1B; }
.status-badge.ready_to_ship { background: #DBEAFE; color: #1E3A8A; }
.status-badge.shipped { background: #EDE9FE; color: #5B21B6; }
.status-badge.delivered { background: #D1FAE5; color: #047857; }
.status-badge.installed { background: #D1FAE5; color: #064E3B; }
.status-badge.on_hold { background: #FEE2E2; color: #991B1B; }
.status-badge.complete { background: #D1FAE5; color: #065F46; }

.job-code-link {
    font-family: 'SF Mono', monospace; font-weight: 700; color: var(--tf-blue);
    text-decoration: none; font-size: 0.85rem;
}
.job-code-link:hover { text-decoration: underline; }

.wo-id { font-family: 'SF Mono', monospace; font-size: 0.82rem; font-weight: 600; color: var(--tf-navy); }

.progress-bar-mini {
    height: 6px; background: #E2E8F0; border-radius: 4px; overflow: hidden;
    min-width: 80px;
}
.progress-bar-mini .fill {
    height: 100%; border-radius: 4px;
    background: linear-gradient(90deg, var(--tf-blue-mid), var(--tf-green));
}

/* QC Queue specific */
.qc-item-card {
    background: white; border: 1px solid var(--tf-border); border-radius: 10px;
    padding: 16px; margin-bottom: 12px; transition: box-shadow 0.2s;
}
.qc-item-card:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.qc-item-card .qc-header {
    display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;
}
.qc-item-card .qc-meta {
    display: flex; gap: 16px; font-size: 0.82rem; color: var(--tf-slate); margin-bottom: 12px;
}
.qc-actions { display: flex; gap: 8px; }
.btn-qc {
    padding: 8px 18px; border-radius: 8px; border: none;
    font-weight: 600; font-size: 0.85rem; cursor: pointer; transition: all 0.2s;
}
.btn-qc.pass { background: var(--tf-green); color: white; }
.btn-qc.pass:hover { background: #059669; }
.btn-qc.fail { background: #EF4444; color: white; }
.btn-qc.fail:hover { background: #DC2626; }
.btn-qc.notes { background: white; color: var(--tf-navy); border: 1px solid var(--tf-border); }
.btn-qc.notes:hover { background: var(--tf-bg); }

/* Empty */
.empty-state {
    text-align: center; padding: 60px 20px; color: var(--tf-slate);
}
.empty-state .empty-icon { font-size: 3rem; margin-bottom: 12px; opacity: 0.4; }
.empty-state h3 { font-size: 1.1rem; margin: 0 0 8px; color: var(--tf-navy); }
.empty-state p { font-size: 0.9rem; margin: 0; }

/* Toast */
.toast {
    position: fixed; bottom: 24px; right: 24px; padding: 14px 24px; border-radius: 10px;
    font-weight: 600; font-size: 0.9rem; z-index: 9999;
    transform: translateY(100px); opacity: 0; transition: all 0.3s; max-width: 400px;
}
.toast.show { transform: translateY(0); opacity: 1; }
.toast.success { background: #065F46; color: white; }
.toast.error { background: #991B1B; color: white; }
.toast.info { background: var(--tf-blue); color: white; }

/* QC Modal */
.modal-overlay {
    position: fixed; inset: 0; background: rgba(15,23,42,0.5); z-index: 500;
    display: none; align-items: center; justify-content: center;
}
.modal-overlay.show { display: flex; }
.modal-box {
    background: white; border-radius: 12px; padding: 28px; width: 480px; max-width: 95vw;
    box-shadow: 0 20px 60px rgba(0,0,0,0.25);
}
.modal-box h3 { margin: 0 0 16px; font-size: 1.1rem; color: var(--tf-navy); }
.modal-box textarea {
    width: 100%; min-height: 100px; padding: 12px; border: 1px solid var(--tf-border);
    border-radius: 8px; font-family: var(--tf-font); font-size: 0.9rem; resize: vertical;
}
.modal-box textarea:focus { outline: none; border-color: var(--tf-blue); }
.modal-actions { display: flex; gap: 10px; justify-content: flex-end; margin-top: 16px; }

@media (max-width: 768px) {
    .wog { padding: 12px; }
    .wog-stats { grid-template-columns: repeat(2, 1fr); }
    .wo-table { font-size: 0.78rem; }
    .wo-table th:nth-child(n+5), .wo-table td:nth-child(n+5) { display: none; }
}
</style>
</head>
<body>

<div class="wog">
    <div class="wog-header">
        <h1>Work Orders</h1>
        <div style="font-size:0.85rem;color:var(--tf-slate);">All projects &middot; Real-time</div>
    </div>

    <!-- Stats -->
    <div class="wog-stats" id="statsRow"></div>

    <!-- Tabs -->
    <div class="wog-tabs">
        <button class="wog-tab active" data-tab="all" onclick="switchTab('all')">
            All Orders <span class="tab-count" id="countAll">0</span>
        </button>
        <button class="wog-tab" data-tab="active" onclick="switchTab('active')">
            Active <span class="tab-count" id="countActive">0</span>
        </button>
        <button class="wog-tab" data-tab="qc" onclick="switchTab('qc')">
            QC Queue <span class="tab-count" id="countQC">0</span>
        </button>
        <button class="wog-tab" data-tab="shipping" onclick="switchTab('shipping')">
            Shipping <span class="tab-count" id="countShipping">0</span>
        </button>
    </div>

    <!-- Filters -->
    <div class="wog-filters">
        <input type="text" id="searchInput" placeholder="Search by WO ID, job code, or status..." oninput="applyFilters()">
        <select id="statusFilter" onchange="applyFilters()">
            <option value="">All Statuses</option>
            <option value="queued">Queued</option>
            <option value="approved">Approved</option>
            <option value="stickers_printed">Stickers Printed</option>
            <option value="in_progress">In Progress</option>
            <option value="on_hold">On Hold</option>
            <option value="fabricated">Fabricated</option>
            <option value="qc_pending">QC Pending</option>
            <option value="qc_approved">QC Approved</option>
            <option value="ready_to_ship">Ready to Ship</option>
            <option value="shipped">Shipped</option>
            <option value="delivered">Delivered</option>
            <option value="installed">Installed</option>
        </select>
        <select id="projectFilter" onchange="applyFilters()">
            <option value="">All Projects</option>
        </select>
    </div>

    <!-- TAB: ALL -->
    <div class="wog-tab-content active" id="tab-all">
        <div id="allTableArea"></div>
    </div>

    <!-- TAB: ACTIVE -->
    <div class="wog-tab-content" id="tab-active">
        <div id="activeTableArea"></div>
    </div>

    <!-- TAB: QC QUEUE -->
    <div class="wog-tab-content" id="tab-qc">
        <div id="qcArea"></div>
    </div>

    <!-- TAB: SHIPPING -->
    <div class="wog-tab-content" id="tab-shipping">
        <div id="shippingArea"></div>
    </div>
</div>

<!-- QC Decision Modal -->
<div class="modal-overlay" id="qcModal" onclick="if(event.target===this)closeQCModal()">
    <div class="modal-box">
        <h3 id="qcModalTitle">QC Decision</h3>
        <div style="margin-bottom:12px;">
            <div style="font-size:0.85rem;color:var(--tf-slate);margin-bottom:4px;">
                <strong id="qcItemMark"></strong> &middot; <span id="qcItemJob"></span>
            </div>
        </div>
        <label style="font-size:0.85rem;font-weight:600;color:var(--tf-navy);display:block;margin-bottom:6px;">Inspector Notes</label>
        <textarea id="qcNotes" placeholder="Enter inspection notes, defect descriptions, or approval remarks..."></textarea>
        <div class="modal-actions">
            <button class="btn-qc notes" onclick="closeQCModal()">Cancel</button>
            <button class="btn-qc fail" id="qcRejectBtn" onclick="submitQCDecision('qc_rejected')">Reject</button>
            <button class="btn-qc pass" id="qcApproveBtn" onclick="submitQCDecision('qc_approved')">Approve</button>
        </div>
    </div>
</div>

<!-- Toast -->
<div class="toast" id="toast"></div>

<script>
let allWOs = [];
let allItems = [];
let currentTab = 'all';
let qcTarget = null;

document.addEventListener('DOMContentLoaded', () => {
    loadData();
});

async function loadData() {
    const [woResp, itemResp] = await Promise.all([
        fetch('/api/work-orders/all').then(r => r.json()),
        fetch('/api/work-orders/all-items').then(r => r.json())
    ]);
    if (woResp.ok) allWOs = woResp.work_orders || [];
    if (itemResp.ok) allItems = itemResp.items || [];

    populateProjectFilter();
    renderStats();
    updateCounts();
    applyFilters();
}

function populateProjectFilter() {
    const projects = [...new Set(allWOs.map(w => w.job_code))].sort();
    const sel = document.getElementById('projectFilter');
    sel.innerHTML = '<option value="">All Projects</option>';
    projects.forEach(p => {
        sel.innerHTML += `<option value="${p}">${p}</option>`;
    });
}

function renderStats() {
    const total = allWOs.length;
    const active = allWOs.filter(w => !['installed', 'complete'].includes(w.status)).length;
    const qcItems = allItems.filter(i => ['qc_pending', 'fabricated'].includes(i.status)).length;
    const readyToShip = allItems.filter(i => i.status === 'ready_to_ship').length;
    const onHold = allWOs.filter(w => w.status === 'on_hold').length;
    const totalItems = allItems.length;
    const completedItems = allItems.filter(i => ['qc_approved', 'ready_to_ship', 'shipped', 'delivered', 'installed', 'complete'].includes(i.status)).length;

    document.getElementById('statsRow').innerHTML = `
        <div class="stat-pill" onclick="document.getElementById('statusFilter').value='';switchTab('all');applyFilters();"><div class="stat-val">${total}</div><div class="stat-label">Total WOs</div></div>
        <div class="stat-pill" onclick="document.getElementById('statusFilter').value='';switchTab('active');"><div class="stat-val">${active}</div><div class="stat-label">Active</div></div>
        <div class="stat-pill" onclick="switchTab('qc');"><div class="stat-val">${qcItems}</div><div class="stat-label">QC Queue</div></div>
        <div class="stat-pill" onclick="switchTab('shipping');"><div class="stat-val">${readyToShip}</div><div class="stat-label">Ready to Ship</div></div>
        <div class="stat-pill" onclick="document.getElementById('statusFilter').value='on_hold';switchTab('all');applyFilters();"><div class="stat-val">${onHold}</div><div class="stat-label">On Hold</div></div>
        <div class="stat-pill" onclick="document.getElementById('statusFilter').value='';switchTab('all');applyFilters();"><div class="stat-val">${totalItems > 0 ? Math.round(100 * completedItems / totalItems) : 0}%</div><div class="stat-label">Overall Progress</div></div>
    `;
}

function updateCounts() {
    document.getElementById('countAll').textContent = allWOs.length;
    document.getElementById('countActive').textContent = allWOs.filter(w => !['installed', 'complete'].includes(w.status)).length;
    document.getElementById('countQC').textContent = allItems.filter(i => ['qc_pending', 'fabricated'].includes(i.status)).length;
    document.getElementById('countShipping').textContent = allItems.filter(i => ['ready_to_ship', 'shipped', 'delivered'].includes(i.status)).length;
}

function switchTab(tab) {
    currentTab = tab;
    document.querySelectorAll('.wog-tab').forEach(t => t.classList.toggle('active', t.dataset.tab === tab));
    document.querySelectorAll('.wog-tab-content').forEach(c => c.classList.toggle('active', c.id === 'tab-' + tab));
    applyFilters();
}

function applyFilters() {
    const q = document.getElementById('searchInput').value.toLowerCase().trim();
    const statusF = document.getElementById('statusFilter').value;
    const projectF = document.getElementById('projectFilter').value;

    let filtered = allWOs.filter(wo => {
        if (statusF && wo.status !== statusF) return false;
        if (projectF && wo.job_code !== projectF) return false;
        if (q) {
            const haystack = `${wo.work_order_id} ${wo.job_code} ${wo.status} ${wo.status_label || ''}`.toLowerCase();
            if (!haystack.includes(q)) return false;
        }
        return true;
    });

    if (currentTab === 'all') renderAllTable(filtered);
    else if (currentTab === 'active') renderAllTable(filtered.filter(w => !['installed', 'complete'].includes(w.status)));
    else if (currentTab === 'qc') renderQCQueue(q, projectF);
    else if (currentTab === 'shipping') renderShippingQueue(q, projectF);
}

function renderAllTable(wos) {
    if (wos.length === 0) {
        document.getElementById(currentTab === 'active' ? 'activeTableArea' : 'allTableArea').innerHTML =
            '<div class="empty-state"><div class="empty-icon">&#128203;</div><h3>No work orders found</h3><p>Try adjusting your filters.</p></div>';
        return;
    }

    let html = `<table class="wo-table"><thead><tr>
        <th>Work Order</th><th>Project</th><th>Status</th><th>Items</th><th>Progress</th>
        <th>Created</th><th>QC Pending</th></tr></thead><tbody>`;

    wos.forEach(wo => {
        const pct = wo.progress_pct || 0;
        const qcPending = wo.qc_pending_items || 0;
        html += `<tr onclick="window.location.href='/work-orders/${encodeURIComponent(wo.job_code)}'">
            <td><span class="wo-id">${wo.work_order_id}</span></td>
            <td><a class="job-code-link" href="/project/${encodeURIComponent(wo.job_code)}" onclick="event.stopPropagation()">${wo.job_code}</a></td>
            <td><span class="status-badge ${wo.status}">${wo.status_label || wo.status}</span></td>
            <td>${wo.completed_items || 0}/${wo.total_items || 0}</td>
            <td>
                <div style="display:flex;align-items:center;gap:8px;">
                    <div class="progress-bar-mini"><div class="fill" style="width:${pct}%"></div></div>
                    <span style="font-family:'SF Mono',monospace;font-size:0.78rem;font-weight:600;min-width:32px;">${pct}%</span>
                </div>
            </td>
            <td style="font-size:0.82rem;color:var(--tf-slate);">${wo.created_at ? new Date(wo.created_at).toLocaleDateString() : '-'}</td>
            <td>${qcPending > 0 ? '<span class="status-badge qc_pending">' + qcPending + ' items</span>' : '<span style="color:var(--tf-slate);font-size:0.8rem;">-</span>'}</td>
        </tr>`;
    });

    html += '</tbody></table>';
    document.getElementById(currentTab === 'active' ? 'activeTableArea' : 'allTableArea').innerHTML = html;
}

function renderQCQueue(q, projectF) {
    let items = allItems.filter(i => ['qc_pending', 'fabricated'].includes(i.status));
    if (projectF) items = items.filter(i => i.job_code === projectF);
    if (q) items = items.filter(i => `${i.item_id} ${i.ship_mark} ${i.job_code} ${i.work_order_id}`.toLowerCase().includes(q));

    if (items.length === 0) {
        document.getElementById('qcArea').innerHTML =
            '<div class="empty-state"><div class="empty-icon">&#9989;</div><h3>QC Queue Empty</h3><p>No items waiting for quality control inspection.</p></div>';
        return;
    }

    // Helper: build shop drawing URL for an item
    function shopDrawingUrl(item) {
        const comp = (item.component_type || '').toLowerCase();
        const base = '/shop-drawings/' + encodeURIComponent(item.job_code);
        if (comp === 'column') return base + '/column';
        if (comp === 'rafter') return base + '/rafter';
        if (item.drawing_ref) return '/api/shop-drawings/file?job_code=' + encodeURIComponent(item.job_code) + '&filename=' + encodeURIComponent(item.drawing_ref);
        return base;
    }

    let html = '';
    items.forEach(item => {
        const st = item.status === 'fabricated' ? 'Awaiting QC' : 'QC Pending';
        const stClass = item.status === 'fabricated' ? 'fabricated' : 'qc_pending';
        const drawLink = shopDrawingUrl(item);
        html += `
        <div class="qc-item-card">
            <div class="qc-header">
                <div>
                    <span style="font-family:'SF Mono',monospace;font-weight:700;font-size:1.15rem;color:var(--tf-navy);">${item.ship_mark}</span>
                    <span style="font-weight:700;font-size:0.88rem;color:var(--tf-slate);margin-left:6px;text-transform:uppercase;">${(item.component_type || '').replace('_',' ')}</span>
                    <span class="status-badge ${stClass}" style="margin-left:8px;">${st}</span>
                </div>
                <span class="wo-id">${item.work_order_id}</span>
            </div>
            <div style="font-weight:700;font-size:0.95rem;color:var(--tf-navy);padding:6px 0 4px;border-bottom:1px solid #E2E8F0;margin-bottom:8px;">
                ${item.description || 'No description'}
            </div>
            <div class="qc-meta">
                <span>Job: <a class="job-code-link" href="/project/${encodeURIComponent(item.job_code)}">${item.job_code}</a></span>
                <span>Qty: <strong>${item.quantity || 1}</strong></span>
                <span>Machine: <strong>${item.machine || '-'}</strong></span>
                ${item.assigned_to ? '<span>Operator: <strong>' + item.assigned_to + '</strong></span>' : ''}
                ${item.finished_at ? '<span>Finished: ' + new Date(item.finished_at).toLocaleString() + '</span>' : ''}
                <a href="${drawLink}" target="_blank" style="display:inline-flex;align-items:center;gap:3px;padding:3px 10px;background:var(--tf-navy);color:white;border-radius:6px;font-size:0.75rem;font-weight:600;text-decoration:none;">&#128208; View Drawing</a>
            </div>
            ${item.qc_notes ? '<div style="background:#FFF7ED;border:1px solid #FED7AA;border-radius:8px;padding:8px 12px;font-size:0.82rem;margin-bottom:12px;color:#9A3412;">Previous QC Notes: ' + item.qc_notes + '</div>' : ''}
            <div class="qc-actions">
                <button class="btn-qc pass" onclick="openQCModal('${item.item_id}', '${item.ship_mark}', '${item.job_code}', 'approve')">&#10003; Approve</button>
                <button class="btn-qc fail" onclick="openQCModal('${item.item_id}', '${item.ship_mark}', '${item.job_code}', 'reject')">&#10007; Reject</button>
                <button class="btn-qc notes" onclick="openQCModal('${item.item_id}', '${item.ship_mark}', '${item.job_code}', 'notes')">Add Notes</button>
            </div>
        </div>`;
    });
    document.getElementById('qcArea').innerHTML = html;
}

function renderShippingQueue(q, projectF) {
    let items = allItems.filter(i => ['ready_to_ship', 'shipped', 'delivered'].includes(i.status));
    if (projectF) items = items.filter(i => i.job_code === projectF);
    if (q) items = items.filter(i => `${i.item_id} ${i.ship_mark} ${i.job_code}`.toLowerCase().includes(q));

    if (items.length === 0) {
        document.getElementById('shippingArea').innerHTML =
            '<div class="empty-state"><div class="empty-icon">&#128666;</div><h3>No Shipping Items</h3><p>Items will appear here after passing QC.</p></div>';
        return;
    }

    let html = `<table class="wo-table"><thead><tr>
        <th>Part</th><th>What</th><th>Job</th><th>Status</th>
        <th>QC Date</th><th>Shipped</th><th>Drawing</th><th>Actions</th></tr></thead><tbody>`;

    items.forEach(item => {
        const nextStatus = item.status === 'ready_to_ship' ? 'shipped'
            : item.status === 'shipped' ? 'delivered' : null;
        const nextLabel = item.status === 'ready_to_ship' ? 'Mark Shipped'
            : item.status === 'shipped' ? 'Mark Delivered' : null;
        const drawLink = typeof shopDrawingUrl === 'function' ? shopDrawingUrl(item) : '/shop-drawings/' + encodeURIComponent(item.job_code);

        html += `<tr>
            <td>
                <span style="font-family:'SF Mono',monospace;font-weight:700;font-size:1rem;">${item.ship_mark}</span>
                <div style="font-size:0.72rem;color:var(--tf-slate);text-transform:uppercase;">${(item.component_type || '').replace('_',' ')}</div>
            </td>
            <td style="font-weight:600;font-size:0.85rem;max-width:200px;">${item.description || '-'}</td>
            <td><a class="job-code-link" href="/project/${encodeURIComponent(item.job_code)}">${item.job_code}</a></td>
            <td><span class="status-badge ${item.status}">${item.status.replace(/_/g, ' ')}</span></td>
            <td style="font-size:0.82rem;color:var(--tf-slate);">${item.qc_at ? new Date(item.qc_at).toLocaleDateString() : '-'}</td>
            <td style="font-size:0.82rem;color:var(--tf-slate);">${item.shipped_at ? new Date(item.shipped_at).toLocaleDateString() : '-'}</td>
            <td style="text-align:center;"><a href="${drawLink}" target="_blank" style="display:inline-flex;align-items:center;gap:3px;padding:3px 8px;background:var(--tf-navy);color:white;border-radius:5px;font-size:0.72rem;font-weight:600;text-decoration:none;">&#128208;</a></td>
            <td>${nextStatus ? '<button class="btn-qc pass" style="padding:4px 12px;font-size:0.78rem;" onclick="transitionItem(&quot;'+item.item_id+'&quot;, &quot;'+item.job_code+'&quot;, &quot;'+nextStatus+'&quot;)">'+nextLabel+'</button>' : '<span style="color:var(--tf-slate);font-size:0.8rem;">-</span>'}</td>
        </tr>`;
    });

    html += '</tbody></table>';
    document.getElementById('shippingArea').innerHTML = html;
}

// QC Modal
function openQCModal(itemId, shipMark, jobCode, mode) {
    qcTarget = { itemId, shipMark, jobCode, mode };
    document.getElementById('qcItemMark').textContent = shipMark;
    document.getElementById('qcItemJob').textContent = jobCode;
    document.getElementById('qcNotes').value = '';

    if (mode === 'approve') {
        document.getElementById('qcModalTitle').textContent = 'Approve QC — ' + shipMark;
        document.getElementById('qcApproveBtn').style.display = '';
        document.getElementById('qcRejectBtn').style.display = 'none';
    } else if (mode === 'reject') {
        document.getElementById('qcModalTitle').textContent = 'Reject QC — ' + shipMark;
        document.getElementById('qcApproveBtn').style.display = 'none';
        document.getElementById('qcRejectBtn').style.display = '';
    } else {
        document.getElementById('qcModalTitle').textContent = 'QC Decision — ' + shipMark;
        document.getElementById('qcApproveBtn').style.display = '';
        document.getElementById('qcRejectBtn').style.display = '';
    }
    document.getElementById('qcModal').classList.add('show');
    setTimeout(() => document.getElementById('qcNotes').focus(), 100);
}

function closeQCModal() {
    document.getElementById('qcModal').classList.remove('show');
    qcTarget = null;
}

async function submitQCDecision(decision) {
    if (!qcTarget) return;
    const notes = document.getElementById('qcNotes').value.trim();

    // If fabricated, first transition to qc_pending, then decide
    const item = allItems.find(i => i.item_id === qcTarget.itemId);
    if (item && item.status === 'fabricated') {
        await fetch('/api/work-orders/transition', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                job_code: qcTarget.jobCode,
                item_id: qcTarget.itemId,
                new_status: 'qc_pending',
                notes: ''
            })
        });
    }

    const resp = await fetch('/api/work-orders/transition', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            job_code: qcTarget.jobCode,
            item_id: qcTarget.itemId,
            new_status: decision,
            notes: notes
        })
    });
    const data = await resp.json();

    if (data.ok) {
        showToast(decision === 'qc_approved' ? 'Item approved!' : 'Item rejected — returned to operator', decision === 'qc_approved' ? 'success' : 'info');
        closeQCModal();
        await loadData();
    } else {
        showToast(data.error || 'Failed', 'error');
    }
}

async function transitionItem(itemId, jobCode, newStatus) {
    const resp = await fetch('/api/work-orders/transition', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ job_code: jobCode, item_id: itemId, new_status: newStatus, notes: '' })
    });
    const data = await resp.json();
    if (data.ok) {
        showToast('Status updated!', 'success');
        await loadData();
    } else {
        showToast(data.error || 'Failed', 'error');
    }
}

function showToast(msg, type) {
    const toast = document.getElementById('toast');
    toast.textContent = msg;
    toast.className = 'toast ' + (type || 'info') + ' show';
    setTimeout(() => { toast.className = 'toast'; }, 4000);
}
</script>
</body>
</html>
"""
