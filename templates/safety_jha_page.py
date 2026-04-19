"""
TitanForge v4 -- Safety JHA Management
=========================================
JHA template library, risk matrix, control hierarchy, approval workflow, active JHA dashboard.
"""

SAFETY_JHA_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a; --tf-card: #1e293b; --tf-text: #e2e8f0;
        --tf-muted: #94a3b8; --tf-gold: #d4a843; --tf-blue: #3b82f6;
        --tf-green: #10b981; --tf-red: #ef4444; --tf-orange: #f59e0b;
    }
    .sjha-container {
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

    .risk-matrix {
        display: grid; grid-template-columns: auto repeat(5, 1fr); gap: 2px;
        background: var(--tf-card); border-radius: 12px; border: 1px solid rgba(255,255,255,0.06);
        overflow: hidden; margin-bottom: 24px; padding: 16px;
    }
    .risk-cell {
        padding: 12px; text-align: center; font-size: 12px; font-weight: 700;
        border-radius: 4px;
    }
    .risk-header { color: var(--tf-muted); font-size: 11px; text-transform: uppercase; padding: 8px; }
    .risk-extreme { background: rgba(239,68,68,0.3); color: var(--tf-red); }
    .risk-high { background: rgba(239,68,68,0.15); color: var(--tf-red); }
    .risk-medium { background: rgba(245,158,11,0.15); color: var(--tf-orange); }
    .risk-low { background: rgba(16,185,129,0.15); color: var(--tf-green); }

    .template-grid {
        display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
        gap: 16px; margin-bottom: 20px;
    }
    .template-card {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06);
        padding: 20px; transition: border-color 0.2s; cursor: pointer;
    }
    .template-card:hover { border-color: var(--tf-blue); }
    .template-card h4 { font-size: 15px; font-weight: 700; margin: 0 0 8px 0; }
    .template-card p { font-size: 13px; color: var(--tf-muted); margin: 0 0 12px 0; }
    .template-card .meta { font-size: 12px; color: var(--tf-muted); }

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
    .badge-active { background: rgba(16,185,129,0.15); color: var(--tf-green); }
    .badge-pending { background: rgba(245,158,11,0.15); color: var(--tf-orange); }
    .badge-expired { background: rgba(239,68,68,0.15); color: var(--tf-red); }
    .badge-approved { background: rgba(59,130,246,0.15); color: var(--tf-blue); }

    .control-hierarchy {
        display: flex; flex-direction: column; gap: 4px; margin-bottom: 24px;
    }
    .control-level {
        display: flex; align-items: center; gap: 12px; padding: 12px 16px;
        background: var(--tf-card); border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);
    }
    .control-rank { font-size: 20px; font-weight: 900; width: 36px; text-align: center; }
    .control-name { font-size: 14px; font-weight: 700; }
    .control-desc { font-size: 12px; color: var(--tf-muted); }

    .empty-state { text-align: center; padding: 60px 20px; color: var(--tf-muted); }
    .empty-state .icon { font-size: 48px; margin-bottom: 16px; opacity: 0.5; }
    .empty-state h3 { font-size: 18px; color: var(--tf-text); margin-bottom: 8px; }
    .empty-state p { font-size: 14px; max-width: 400px; margin: 0 auto 20px; }

    .modal-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 1000; align-items: center; justify-content: center; }
    .modal-overlay.active { display: flex; }
    .modal { background: var(--tf-card); border-radius: 16px; padding: 32px; width: 90%; max-width: 700px; max-height: 90vh; overflow-y: auto; border: 1px solid rgba(255,255,255,0.08); }
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
    table { display: block; overflow-x: auto; -webkit-overflow-scrolling: touch; }
    .modal-overlay .modal, .modal { width: 95%; max-width: 95vw; margin: 20px auto; padding: 20px; }
    .template-grid { grid-template-columns: 1fr; }
    .tabs { overflow-x: auto; -webkit-overflow-scrolling: touch; flex-wrap: nowrap; }
    .tab-btn { white-space: nowrap; }
    .form-grid { grid-template-columns: 1fr; }
    .risk-matrix { overflow-x: auto; -webkit-overflow-scrolling: touch; }
}
@media (max-width: 480px) {
    .stat-row { grid-template-columns: 1fr; }
    .toolbar { gap: 8px; }
    .template-grid { grid-template-columns: 1fr; }
}
</style>

<div class="sjha-container">
    <div class="page-header">
        <h1>JHA Management</h1>
        <p>Job Hazard Analysis templates, risk assessment, control hierarchy, and approval workflow</p>
    </div>

    <div class="stat-row">
        <div class="stat-card stat-gold"><div class="label">Total JHAs</div><div class="value" id="stat-total">0</div></div>
        <div class="stat-card stat-green"><div class="label">Active</div><div class="value" id="stat-active">0</div></div>
        <div class="stat-card stat-orange"><div class="label">Pending Approval</div><div class="value" id="stat-pending">0</div></div>
        <div class="stat-card stat-blue"><div class="label">Templates</div><div class="value" id="stat-templates">0</div></div>
        <div class="stat-card stat-red"><div class="label">Expired</div><div class="value" id="stat-expired">0</div></div>
    </div>

    <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('dashboard', this)">Active JHAs</button>
        <button class="tab-btn" onclick="switchTab('templates', this)">Templates</button>
        <button class="tab-btn" onclick="switchTab('risk-matrix', this)">Risk Matrix</button>
        <button class="tab-btn" onclick="switchTab('controls', this)">Control Hierarchy</button>
    </div>

    <!-- Active JHAs -->
    <div class="tab-panel active" id="panel-dashboard">
        <div class="toolbar">
            <div class="toolbar-left">
                <input type="text" id="searchJHA" placeholder="Search JHAs..." oninput="renderJHAs()">
                <select id="filterStatus" onchange="renderJHAs()"><option value="">All Status</option><option value="active">Active</option><option value="pending">Pending</option><option value="expired">Expired</option></select>
            </div>
            <button class="btn btn-primary" onclick="openJHAModal()">+ New JHA</button>
        </div>
        <table class="data-table">
            <thead><tr><th>JHA #</th><th>Title</th><th>Project</th><th>Risk Level</th><th>Approver</th><th>Valid Until</th><th>Status</th><th>Actions</th></tr></thead>
            <tbody id="jhaTable"></tbody>
        </table>
        <div class="empty-state" id="emptyJHA"><div class="icon">&#9888;</div><h3>No Active JHAs</h3><p>Create a new JHA from a template or from scratch.</p></div>
    </div>

    <!-- Templates -->
    <div class="tab-panel" id="panel-templates">
        <div class="toolbar">
            <div class="toolbar-left"><input type="text" placeholder="Search templates..." oninput="renderTemplates()"></div>
            <button class="btn btn-primary" onclick="openTemplateModal()">+ New Template</button>
        </div>
        <div class="template-grid" id="templateGrid"></div>
        <div class="empty-state" id="emptyTemplates"><div class="icon">&#128203;</div><h3>No Templates</h3><p>Create reusable JHA templates for common work activities.</p></div>
    </div>

    <!-- Risk Matrix -->
    <div class="tab-panel" id="panel-risk-matrix">
        <h3 style="margin-bottom:16px;font-size:18px;">Risk Assessment Matrix</h3>
        <div class="risk-matrix">
            <div class="risk-header"></div>
            <div class="risk-header">Negligible</div><div class="risk-header">Minor</div><div class="risk-header">Moderate</div><div class="risk-header">Major</div><div class="risk-header">Catastrophic</div>
            <div class="risk-header">Almost Certain</div><div class="risk-cell risk-medium">Medium</div><div class="risk-cell risk-high">High</div><div class="risk-cell risk-extreme">Extreme</div><div class="risk-cell risk-extreme">Extreme</div><div class="risk-cell risk-extreme">Extreme</div>
            <div class="risk-header">Likely</div><div class="risk-cell risk-low">Low</div><div class="risk-cell risk-medium">Medium</div><div class="risk-cell risk-high">High</div><div class="risk-cell risk-extreme">Extreme</div><div class="risk-cell risk-extreme">Extreme</div>
            <div class="risk-header">Possible</div><div class="risk-cell risk-low">Low</div><div class="risk-cell risk-medium">Medium</div><div class="risk-cell risk-high">High</div><div class="risk-cell risk-high">High</div><div class="risk-cell risk-extreme">Extreme</div>
            <div class="risk-header">Unlikely</div><div class="risk-cell risk-low">Low</div><div class="risk-cell risk-low">Low</div><div class="risk-cell risk-medium">Medium</div><div class="risk-cell risk-high">High</div><div class="risk-cell risk-high">High</div>
            <div class="risk-header">Rare</div><div class="risk-cell risk-low">Low</div><div class="risk-cell risk-low">Low</div><div class="risk-cell risk-low">Low</div><div class="risk-cell risk-medium">Medium</div><div class="risk-cell risk-high">High</div>
        </div>
    </div>

    <!-- Control Hierarchy -->
    <div class="tab-panel" id="panel-controls">
        <h3 style="margin-bottom:16px;font-size:18px;">Hierarchy of Controls (Most to Least Effective)</h3>
        <div class="control-hierarchy">
            <div class="control-level"><span class="control-rank" style="color:var(--tf-green)">1</span><div><div class="control-name">Elimination</div><div class="control-desc">Physically remove the hazard entirely</div></div></div>
            <div class="control-level"><span class="control-rank" style="color:var(--tf-green)">2</span><div><div class="control-name">Substitution</div><div class="control-desc">Replace the hazard with something less dangerous</div></div></div>
            <div class="control-level"><span class="control-rank" style="color:var(--tf-blue)">3</span><div><div class="control-name">Engineering Controls</div><div class="control-desc">Isolate people from the hazard (guardrails, ventilation, barriers)</div></div></div>
            <div class="control-level"><span class="control-rank" style="color:var(--tf-orange)">4</span><div><div class="control-name">Administrative Controls</div><div class="control-desc">Change the way people work (training, procedures, signage)</div></div></div>
            <div class="control-level"><span class="control-rank" style="color:var(--tf-red)">5</span><div><div class="control-name">PPE</div><div class="control-desc">Personal Protective Equipment (last resort)</div></div></div>
        </div>
    </div>
</div>

<!-- JHA Modal -->
<div class="modal-overlay" id="jhaModal">
    <div class="modal">
        <button class="modal-close" onclick="closeModal('jhaModal')">&times;</button>
        <h2>New JHA</h2>
        <form id="jhaForm" onsubmit="saveJHA(event)">
            <div class="form-grid">
                <div class="form-group"><label>Title</label><input type="text" id="jhaTitle" required></div>
                <div class="form-group"><label>Template</label><select id="jhaTemplate"><option value="">From Scratch</option></select></div>
                <div class="form-group"><label>Project</label><select id="jhaProject"><option value="">Select</option></select></div>
                <div class="form-group"><label>Risk Level</label><select id="jhaRisk"><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option><option value="extreme">Extreme</option></select></div>
                <div class="form-group"><label>Valid Until</label><input type="date" id="jhaValid"></div>
                <div class="form-group"><label>Approver</label><input type="text" id="jhaApprover"></div>
                <div class="form-group form-full"><label>Hazards &amp; Controls</label><textarea id="jhaHazards" placeholder="List hazards and controls..."></textarea></div>
            </div>
            <div class="modal-actions">
                <button type="button" class="btn btn-secondary" onclick="closeModal('jhaModal')">Cancel</button>
                <button type="submit" class="btn btn-primary">Save JHA</button>
            </div>
        </form>
    </div>
</div>

<script>
    let jhas = [];
    let templates = [];

    function switchTab(tab, btn) {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById('panel-' + tab).classList.add('active');
    }

    async function loadJHAs() {
        try {
            const resp = await fetch('/api/safety/jha');
            const data = await resp.json();
            jhas = data.jhas || [];
            templates = data.templates || [];
            renderJHAs();
            renderTemplates();
            updateStats();
        } catch(e) { console.error('Failed to load JHAs:', e); renderJHAs(); renderTemplates(); }
    }

    function renderJHAs() {
        const tbody = document.getElementById('jhaTable');
        const empty = document.getElementById('emptyJHA');
        const search = (document.getElementById('searchJHA').value || '').toLowerCase();
        const statusFilter = document.getElementById('filterStatus').value;

        let filtered = jhas.filter(j => {
            if (search && !JSON.stringify(j).toLowerCase().includes(search)) return false;
            if (statusFilter && j.status !== statusFilter) return false;
            return true;
        });

        if (filtered.length === 0) { tbody.innerHTML = ''; empty.style.display = 'block'; return; }
        empty.style.display = 'none';

        const statusCls = { active: 'badge-active', pending: 'badge-pending', expired: 'badge-expired', approved: 'badge-approved' };
        const riskStyle = { low: 'color:var(--tf-green)', medium: 'color:var(--tf-orange)', high: 'color:var(--tf-red)', extreme: 'color:var(--tf-red);font-weight:900' };

        tbody.innerHTML = filtered.map(j => `
            <tr>
                <td style="font-weight:600">${j.number || j.id || ''}</td>
                <td>${j.title || ''}</td>
                <td>${j.project_name || ''}</td>
                <td><span style="${riskStyle[j.risk_level] || ''};text-transform:uppercase;font-weight:700;font-size:12px;">${j.risk_level || ''}</span></td>
                <td>${j.approver || ''}</td>
                <td>${j.valid_until || ''}</td>
                <td><span class="badge ${statusCls[j.status] || 'badge-pending'}">${j.status || ''}</span></td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="event.stopPropagation()">View</button>
                    ${j.status === 'pending' ? `<button class="btn btn-sm btn-primary" onclick="event.stopPropagation();approveJHA('${j.id}')">Approve</button>` : ''}
                </td>
            </tr>
        `).join('');
    }

    function renderTemplates() {
        const grid = document.getElementById('templateGrid');
        const empty = document.getElementById('emptyTemplates');
        if (templates.length === 0) { grid.innerHTML = ''; empty.style.display = 'block'; return; }
        empty.style.display = 'none';
        grid.innerHTML = templates.map(t => `
            <div class="template-card" onclick="useTemplate('${t.id}')">
                <h4>${t.title || ''}</h4>
                <p>${t.description || ''}</p>
                <div class="meta">${t.hazard_count || 0} hazards defined - Used ${t.use_count || 0} times</div>
            </div>
        `).join('');
    }

    function updateStats() {
        document.getElementById('stat-total').textContent = jhas.length;
        document.getElementById('stat-active').textContent = jhas.filter(j => j.status === 'active').length;
        document.getElementById('stat-pending').textContent = jhas.filter(j => j.status === 'pending').length;
        document.getElementById('stat-templates').textContent = templates.length;
        document.getElementById('stat-expired').textContent = jhas.filter(j => j.status === 'expired').length;
    }

    function openJHAModal() { document.getElementById('jhaForm').reset(); document.getElementById('jhaModal').classList.add('active'); }
    function openTemplateModal() { openJHAModal(); }
    function useTemplate(id) { openJHAModal(); document.getElementById('jhaTemplate').value = id; }

    async function saveJHA(e) {
        e.preventDefault();
        const payload = {
            title: document.getElementById('jhaTitle').value,
            template_id: document.getElementById('jhaTemplate').value,
            project_id: document.getElementById('jhaProject').value,
            risk_level: document.getElementById('jhaRisk').value,
            valid_until: document.getElementById('jhaValid').value,
            approver: document.getElementById('jhaApprover').value,
            hazards_text: document.getElementById('jhaHazards').value
        };
        try {
            await fetch('/api/safety/jha', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
            closeModal('jhaModal');
            loadJHAs();
        } catch(e) { alert('Error saving JHA'); }
    }

    async function approveJHA(id) {
        try {
            await fetch('/api/safety/jha/approve', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ id: id }) });
            loadJHAs();
        } catch(e) { alert('Error approving JHA'); }
    }

    function closeModal(id) { document.getElementById(id).classList.remove('active'); }
    window.addEventListener('click', e => { if (e.target.classList.contains('modal-overlay')) e.target.classList.remove('active'); });

    document.addEventListener('DOMContentLoaded', loadJHAs);
</script>
"""
