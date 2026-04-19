"""
TitanForge v4 -- Field Documents Manager
==========================================
RFIs, submittals, change orders, drawing revisions, upload/download, version tracking.
"""

FIELD_DOCS_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a; --tf-card: #1e293b; --tf-text: #e2e8f0;
        --tf-muted: #94a3b8; --tf-gold: #d4a843; --tf-blue: #3b82f6;
        --tf-green: #10b981; --tf-red: #ef4444; --tf-orange: #f59e0b;
    }
    .docs-container {
        max-width: 1400px; margin: 0 auto; padding: 24px 32px;
        font-family: 'Inter', system-ui, -apple-system, sans-serif; color: var(--tf-text);
    }
    .page-header { margin-bottom: 28px; }
    .page-header h1 { font-size: 28px; font-weight: 800; margin: 0 0 6px 0; }
    .page-header p { font-size: 14px; color: var(--tf-muted); margin: 0; }

    .stat-row {
        display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
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

    .tabs {
        display: flex; gap: 0; border-bottom: 2px solid rgba(255,255,255,0.06);
        margin-bottom: 20px;
    }
    .tab-btn {
        padding: 12px 24px; border: none; background: none; color: var(--tf-muted);
        font-size: 14px; font-weight: 600; cursor: pointer; border-bottom: 3px solid transparent;
        margin-bottom: -2px; transition: all 0.2s;
    }
    .tab-btn:hover { color: var(--tf-text); }
    .tab-btn.active { color: var(--tf-gold); border-bottom-color: var(--tf-gold); }
    .tab-panel { display: none; }
    .tab-panel.active { display: block; }

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
    .badge-open { background: rgba(59,130,246,0.15); color: var(--tf-blue); }
    .badge-closed { background: rgba(16,185,129,0.15); color: var(--tf-green); }
    .badge-pending { background: rgba(245,158,11,0.15); color: var(--tf-orange); }
    .badge-urgent { background: rgba(239,68,68,0.15); color: var(--tf-red); }

    .empty-state { text-align: center; padding: 60px 20px; color: var(--tf-muted); }
    .empty-state .icon { font-size: 48px; margin-bottom: 16px; opacity: 0.5; }
    .empty-state h3 { font-size: 18px; color: var(--tf-text); margin-bottom: 8px; }
    .empty-state p { font-size: 14px; max-width: 400px; margin: 0 auto 20px; }

    .version-tag { font-size: 11px; color: var(--tf-blue); background: rgba(59,130,246,0.1); padding: 2px 8px; border-radius: 4px; }

    .modal-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 1000; align-items: center; justify-content: center; }
    .modal-overlay.active { display: flex; }
    .modal { background: var(--tf-card); border-radius: 16px; padding: 32px; width: 90%; max-width: 600px; max-height: 90vh; overflow-y: auto; border: 1px solid rgba(255,255,255,0.08); }
    .modal h2 { font-size: 22px; font-weight: 800; margin: 0 0 24px 0; }
    .modal-close { float: right; background: none; border: none; color: var(--tf-muted); font-size: 24px; cursor: pointer; }
    .form-group { margin-bottom: 16px; }
    .form-group label { display: block; font-size: 13px; font-weight: 600; color: var(--tf-muted); margin-bottom: 6px; }
    .form-group input, .form-group select, .form-group textarea {
        width: 100%; background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px;
    }
    .form-group textarea { min-height: 80px; resize: vertical; }
    .form-group input:focus, .form-group select:focus, .form-group textarea:focus { outline: none; border-color: var(--tf-blue); }
    .modal-actions { display: flex; gap: 10px; justify-content: flex-end; margin-top: 24px; }

/* ── Responsive ── */
@media (max-width: 768px) {
    .page-header h1 { font-size: 22px; }
    .toolbar { flex-direction: column; align-items: stretch; }
    .toolbar input[type="text"] { width: 100%; }
    .stat-row { grid-template-columns: 1fr 1fr; gap: 10px; }
    table { display: block; overflow-x: auto; -webkit-overflow-scrolling: touch; }
    .modal-overlay .modal, .modal { width: 95%; max-width: 95vw; margin: 20px auto; padding: 20px; }
    .tabs { overflow-x: auto; -webkit-overflow-scrolling: touch; flex-wrap: nowrap; }
    .tab-btn { white-space: nowrap; }
}
@media (max-width: 480px) {
    .stat-row { grid-template-columns: 1fr; }
    .toolbar { gap: 8px; }
}
</style>

<div class="docs-container">
    <div class="page-header">
        <h1>Field Documents</h1>
        <p>Manage RFIs, submittals, change orders, and drawing revisions for field operations</p>
    </div>

    <div class="stat-row">
        <div class="stat-card stat-gold"><div class="label">Total Documents</div><div class="value" id="stat-total">0</div></div>
        <div class="stat-card stat-blue"><div class="label">Open RFIs</div><div class="value" id="stat-rfis">0</div></div>
        <div class="stat-card stat-orange"><div class="label">Pending Submittals</div><div class="value" id="stat-submittals">0</div></div>
        <div class="stat-card stat-red"><div class="label">Change Orders</div><div class="value" id="stat-cos">0</div></div>
        <div class="stat-card stat-green"><div class="label">Drawing Revisions</div><div class="value" id="stat-drawings">0</div></div>
    </div>

    <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('rfis')">RFIs</button>
        <button class="tab-btn" onclick="switchTab('submittals')">Submittals</button>
        <button class="tab-btn" onclick="switchTab('change-orders')">Change Orders</button>
        <button class="tab-btn" onclick="switchTab('drawings')">Drawing Revisions</button>
    </div>

    <!-- RFIs Tab -->
    <div class="tab-panel active" id="panel-rfis">
        <div class="toolbar">
            <div class="toolbar-left">
                <input type="text" placeholder="Search RFIs..." oninput="filterDocs('rfis')">
                <select onchange="filterDocs('rfis')"><option value="">All Status</option><option value="open">Open</option><option value="closed">Closed</option></select>
            </div>
            <button class="btn btn-primary" onclick="openDocModal('rfi')">+ New RFI</button>
        </div>
        <table class="data-table"><thead><tr>
            <th>RFI #</th><th>Subject</th><th>Project</th><th>Submitted By</th><th>Date</th><th>Due Date</th><th>Status</th><th>Actions</th>
        </tr></thead><tbody id="rfis-table"></tbody></table>
        <div class="empty-state" id="empty-rfis"><div class="icon">&#128196;</div><h3>No RFIs Found</h3><p>Create a Request for Information to get answers from the design team.</p></div>
    </div>

    <!-- Submittals Tab -->
    <div class="tab-panel" id="panel-submittals">
        <div class="toolbar">
            <div class="toolbar-left">
                <input type="text" placeholder="Search submittals..." oninput="filterDocs('submittals')">
                <select onchange="filterDocs('submittals')"><option value="">All Status</option><option value="pending">Pending</option><option value="approved">Approved</option><option value="rejected">Rejected</option></select>
            </div>
            <button class="btn btn-primary" onclick="openDocModal('submittal')">+ New Submittal</button>
        </div>
        <table class="data-table"><thead><tr>
            <th>Sub #</th><th>Title</th><th>Spec Section</th><th>Submitted</th><th>Due</th><th>Version</th><th>Status</th><th>Actions</th>
        </tr></thead><tbody id="submittals-table"></tbody></table>
        <div class="empty-state" id="empty-submittals"><div class="icon">&#128220;</div><h3>No Submittals</h3><p>Track material and shop drawing submittals for review and approval.</p></div>
    </div>

    <!-- Change Orders Tab -->
    <div class="tab-panel" id="panel-change-orders">
        <div class="toolbar">
            <div class="toolbar-left">
                <input type="text" placeholder="Search change orders..." oninput="filterDocs('change-orders')">
            </div>
            <button class="btn btn-primary" onclick="openDocModal('co')">+ New Change Order</button>
        </div>
        <table class="data-table"><thead><tr>
            <th>CO #</th><th>Description</th><th>Project</th><th>Amount</th><th>Requested</th><th>Status</th><th>Actions</th>
        </tr></thead><tbody id="change-orders-table"></tbody></table>
        <div class="empty-state" id="empty-change-orders"><div class="icon">&#128221;</div><h3>No Change Orders</h3><p>Document scope changes and track their cost impact.</p></div>
    </div>

    <!-- Drawing Revisions Tab -->
    <div class="tab-panel" id="panel-drawings">
        <div class="toolbar">
            <div class="toolbar-left">
                <input type="text" placeholder="Search drawings..." oninput="filterDocs('drawings')">
            </div>
            <button class="btn btn-primary" onclick="openDocModal('drawing')">+ Upload Revision</button>
        </div>
        <table class="data-table"><thead><tr>
            <th>Drawing #</th><th>Title</th><th>Revision</th><th>Revised By</th><th>Date</th><th>Changes</th><th>Actions</th>
        </tr></thead><tbody id="drawings-table"></tbody></table>
        <div class="empty-state" id="empty-drawings"><div class="icon">&#128209;</div><h3>No Drawing Revisions</h3><p>Upload and track drawing revisions with version control.</p></div>
    </div>
</div>

<!-- Document Modal -->
<div class="modal-overlay" id="docModal">
    <div class="modal">
        <button class="modal-close" onclick="closeModal('docModal')">&times;</button>
        <h2 id="docModalTitle">New Document</h2>
        <form id="docForm" onsubmit="saveDoc(event)">
            <input type="hidden" id="docType">
            <div class="form-group"><label>Title / Subject</label><input type="text" id="docTitle" required></div>
            <div class="form-group"><label>Project</label><select id="docProject"><option value="">Select Project</option></select></div>
            <div class="form-group"><label>Description</label><textarea id="docDesc" placeholder="Details..."></textarea></div>
            <div class="form-group"><label>Priority</label>
                <select id="docPriority"><option value="normal">Normal</option><option value="urgent">Urgent</option><option value="low">Low</option></select>
            </div>
            <div class="form-group"><label>Due Date</label><input type="date" id="docDue"></div>
            <div class="form-group"><label>Attachment</label><input type="file" id="docFile" style="padding:8px;"></div>
            <div class="modal-actions">
                <button type="button" class="btn btn-secondary" onclick="closeModal('docModal')">Cancel</button>
                <button type="submit" class="btn btn-primary">Save</button>
            </div>
        </form>
    </div>
</div>

<script>
    let docs = { rfis: [], submittals: [], 'change-orders': [], drawings: [] };
    let activeTab = 'rfis';

    function switchTab(tab) {
        activeTab = tab;
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
        event.target.classList.add('active');
        document.getElementById('panel-' + tab).classList.add('active');
    }

    async function loadDocs() {
        try {
            const resp = await fetch('/api/field/docs');
            const data = await resp.json();
            docs.rfis = data.rfis || [];
            docs.submittals = data.submittals || [];
            docs['change-orders'] = data.change_orders || [];
            docs.drawings = data.drawings || [];
            renderAll();
            updateStats();
        } catch(e) { console.error('Failed to load docs:', e); renderAll(); }
    }

    function renderAll() {
        renderTable('rfis', ['number','subject','project','submitted_by','date','due_date','status']);
        renderTable('submittals', ['number','title','spec_section','submitted_date','due_date','version','status']);
        renderTable('change-orders', ['number','description','project','amount','date','status']);
        renderTable('drawings', ['number','title','revision','revised_by','date','changes']);
    }

    function renderTable(type, fields) {
        const tbody = document.getElementById(type + '-table');
        const empty = document.getElementById('empty-' + type);
        const items = docs[type] || [];
        if (items.length === 0) { tbody.innerHTML = ''; empty.style.display = 'block'; return; }
        empty.style.display = 'none';
        const statusCls = { open: 'badge-open', closed: 'badge-closed', pending: 'badge-pending', urgent: 'badge-urgent', approved: 'badge-closed', rejected: 'badge-urgent' };
        tbody.innerHTML = items.map(item => {
            let cells = fields.map(f => {
                if (f === 'status') return `<td><span class="badge ${statusCls[item[f]] || 'badge-open'}">${item[f] || ''}</span></td>`;
                if (f === 'version') return `<td><span class="version-tag">v${item[f] || '1'}</span></td>`;
                if (f === 'amount') return `<td>$${(item[f] || 0).toLocaleString()}</td>`;
                return `<td>${item[f] || ''}</td>`;
            }).join('');
            cells += `<td><button class="btn btn-sm btn-secondary" onclick="event.stopPropagation()">View</button> <button class="btn btn-sm btn-secondary" onclick="event.stopPropagation()">Download</button></td>`;
            return `<tr>${cells}</tr>`;
        }).join('');
    }

    function updateStats() {
        document.getElementById('stat-total').textContent = Object.values(docs).reduce((s, a) => s + a.length, 0);
        document.getElementById('stat-rfis').textContent = docs.rfis.filter(r => r.status === 'open').length;
        document.getElementById('stat-submittals').textContent = docs.submittals.filter(r => r.status === 'pending').length;
        document.getElementById('stat-cos').textContent = docs['change-orders'].length;
        document.getElementById('stat-drawings').textContent = docs.drawings.length;
    }

    function filterDocs(type) { renderTable(type, []); }

    function openDocModal(type) {
        const titles = { rfi: 'New RFI', submittal: 'New Submittal', co: 'New Change Order', drawing: 'Upload Drawing Revision' };
        document.getElementById('docModalTitle').textContent = titles[type] || 'New Document';
        document.getElementById('docType').value = type;
        document.getElementById('docForm').reset();
        document.getElementById('docModal').classList.add('active');
    }

    async function saveDoc(e) {
        e.preventDefault();
        const payload = {
            type: document.getElementById('docType').value,
            title: document.getElementById('docTitle').value,
            project: document.getElementById('docProject').value,
            description: document.getElementById('docDesc').value,
            priority: document.getElementById('docPriority').value,
            due_date: document.getElementById('docDue').value
        };
        try {
            await fetch('/api/field/docs', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
            closeModal('docModal');
            loadDocs();
        } catch(e) { alert('Error saving document'); }
    }

    function closeModal(id) { document.getElementById(id).classList.remove('active'); }
    window.addEventListener('click', e => { if (e.target.classList.contains('modal-overlay')) e.target.classList.remove('active'); });

    document.addEventListener('DOMContentLoaded', loadDocs);
</script>
"""
