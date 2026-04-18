"""
TitanForge v4 -- Field Job Hazard Analysis
=============================================
JHA form builder, hazard identification, control measures, crew sign-off.
"""

FIELD_JHA_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a; --tf-card: #1e293b; --tf-text: #e2e8f0;
        --tf-muted: #94a3b8; --tf-gold: #d4a843; --tf-blue: #3b82f6;
        --tf-green: #10b981; --tf-red: #ef4444; --tf-orange: #f59e0b;
    }
    .jha-container {
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

    .cards-grid {
        display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
        gap: 16px; margin-bottom: 20px;
    }
    .jha-card {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06);
        padding: 24px; transition: border-color 0.2s; cursor: pointer;
    }
    .jha-card:hover { border-color: var(--tf-blue); }
    .jha-card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
    .jha-card-header h3 { font-size: 16px; font-weight: 700; margin: 0; }
    .jha-card-meta { display: flex; gap: 16px; margin-bottom: 12px; font-size: 13px; color: var(--tf-muted); }
    .hazard-list { margin: 12px 0; }
    .hazard-item {
        display: flex; align-items: center; gap: 8px; padding: 8px 12px;
        background: var(--tf-bg); border-radius: 8px; margin-bottom: 6px; font-size: 13px;
    }
    .hazard-item .risk { font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 4px; text-transform: uppercase; }
    .risk-high { background: rgba(239,68,68,0.15); color: var(--tf-red); }
    .risk-medium { background: rgba(245,158,11,0.15); color: var(--tf-orange); }
    .risk-low { background: rgba(16,185,129,0.15); color: var(--tf-green); }
    .signoff-row {
        display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px;
    }
    .signoff-badge {
        display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px;
        border-radius: 6px; font-size: 11px; font-weight: 600;
        background: rgba(16,185,129,0.1); color: var(--tf-green);
    }
    .signoff-pending { background: rgba(245,158,11,0.1); color: var(--tf-orange); }

    .badge { display: inline-block; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
    .badge-active { background: rgba(16,185,129,0.15); color: var(--tf-green); }
    .badge-draft { background: rgba(245,158,11,0.15); color: var(--tf-orange); }
    .badge-expired { background: rgba(239,68,68,0.15); color: var(--tf-red); }

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
    .hazards-builder { margin: 16px 0; }
    .hazards-builder h4 { font-size: 14px; font-weight: 700; margin-bottom: 12px; }
    .hazard-row { display: grid; grid-template-columns: 1fr 100px 1fr 40px; gap: 8px; margin-bottom: 8px; align-items: center; }
    .hazard-row input, .hazard-row select {
        background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 6px; padding: 8px 10px; color: var(--tf-text); font-size: 13px;
    }
    .hazard-remove { background: none; border: none; color: var(--tf-red); font-size: 18px; cursor: pointer; }

/* ── Responsive ── */
@media (max-width: 768px) {
    .page-header h1 { font-size: 22px; }
    .toolbar { flex-direction: column; align-items: stretch; }
    .toolbar input[type="text"] { width: 100%; }
    .stat-row { grid-template-columns: 1fr 1fr; gap: 10px; }
    .modal-overlay .modal, .modal { width: 95%; max-width: 95vw; margin: 20px auto; padding: 20px; }
    .cards-grid { grid-template-columns: 1fr; }
    .form-grid { grid-template-columns: 1fr; }
    .hazard-row { flex-direction: column; gap: 8px; }
}
@media (max-width: 480px) {
    .stat-row { grid-template-columns: 1fr; }
    .toolbar { gap: 8px; }
}
</style>

<div class="jha-container">
    <div class="page-header">
        <h1>Job Hazard Analysis</h1>
        <p>Create and manage JHAs with hazard identification, control measures, and crew sign-off tracking</p>
    </div>

    <div class="stat-row">
        <div class="stat-card stat-gold"><div class="label">Total JHAs</div><div class="value" id="stat-total">0</div></div>
        <div class="stat-card stat-green"><div class="label">Active</div><div class="value" id="stat-active">0</div></div>
        <div class="stat-card stat-orange"><div class="label">Drafts</div><div class="value" id="stat-drafts">0</div></div>
        <div class="stat-card stat-red"><div class="label">Pending Sign-off</div><div class="value" id="stat-signoff">0</div></div>
    </div>

    <div class="toolbar">
        <div class="toolbar-left">
            <input type="text" id="searchInput" placeholder="Search JHAs..." oninput="renderJHAs()">
            <select id="filterStatus" onchange="renderJHAs()">
                <option value="">All Status</option>
                <option value="active">Active</option>
                <option value="draft">Draft</option>
                <option value="expired">Expired</option>
            </select>
            <select id="filterProject" onchange="renderJHAs()">
                <option value="">All Projects</option>
            </select>
        </div>
        <button class="btn btn-primary" onclick="openJHAModal()">+ New JHA</button>
    </div>

    <div class="cards-grid" id="jhaGrid"></div>

    <div class="empty-state" id="emptyState">
        <div class="icon">&#9888;</div>
        <h3>No JHAs Created</h3>
        <p>Job Hazard Analyses help identify risks before work begins. Create your first JHA to keep crews safe.</p>
        <button class="btn btn-primary" onclick="openJHAModal()">+ Create First JHA</button>
    </div>
</div>

<!-- JHA Modal -->
<div class="modal-overlay" id="jhaModal">
    <div class="modal">
        <button class="modal-close" onclick="closeModal('jhaModal')">&times;</button>
        <h2 id="jhaModalTitle">New Job Hazard Analysis</h2>
        <form id="jhaForm" onsubmit="saveJHA(event)">
            <div class="form-grid">
                <div class="form-group"><label>JHA Title</label><input type="text" id="jhaTitle" required placeholder="e.g. Steel Erection - Building A"></div>
                <div class="form-group"><label>Project</label><select id="jhaProject"><option value="">Select Project</option></select></div>
                <div class="form-group"><label>Work Activity</label><input type="text" id="jhaActivity" placeholder="e.g. Overhead lifting"></div>
                <div class="form-group"><label>Location</label><input type="text" id="jhaLocation" placeholder="e.g. Building A, Bay 3"></div>
                <div class="form-group"><label>Date</label><input type="date" id="jhaDate"></div>
                <div class="form-group"><label>Supervisor</label><input type="text" id="jhaSupervisor"></div>
            </div>

            <div class="hazards-builder">
                <h4>Hazards & Controls</h4>
                <div id="hazardRows">
                    <div class="hazard-row">
                        <input type="text" placeholder="Hazard description">
                        <select><option value="high">High</option><option value="medium" selected>Medium</option><option value="low">Low</option></select>
                        <input type="text" placeholder="Control measure">
                        <button type="button" class="hazard-remove" onclick="this.parentElement.remove()">x</button>
                    </div>
                </div>
                <button type="button" class="btn btn-sm btn-secondary" onclick="addHazardRow()" style="margin-top:8px;">+ Add Hazard</button>
            </div>

            <div class="form-group form-full"><label>Additional Notes</label><textarea id="jhaNotes" placeholder="PPE required, special precautions, etc."></textarea></div>

            <div class="modal-actions">
                <button type="button" class="btn btn-secondary" onclick="closeModal('jhaModal')">Cancel</button>
                <button type="submit" class="btn btn-primary">Save JHA</button>
            </div>
        </form>
    </div>
</div>

<script>
    let jhas = [];
    let editingId = null;

    async function loadJHAs() {
        try {
            const resp = await fetch('/api/field/jha');
            const data = await resp.json();
            jhas = data.jhas || [];
            renderJHAs();
            updateStats();
        } catch(e) { console.error('Failed to load JHAs:', e); renderJHAs(); }
    }

    function renderJHAs() {
        const grid = document.getElementById('jhaGrid');
        const empty = document.getElementById('emptyState');
        const search = document.getElementById('searchInput').value.toLowerCase();
        const statusFilter = document.getElementById('filterStatus').value;
        const projectFilter = document.getElementById('filterProject').value;

        let filtered = jhas.filter(j => {
            if (search && !JSON.stringify(j).toLowerCase().includes(search)) return false;
            if (statusFilter && j.status !== statusFilter) return false;
            if (projectFilter && j.project_id !== projectFilter) return false;
            return true;
        });

        if (filtered.length === 0) { grid.innerHTML = ''; empty.style.display = 'block'; return; }
        empty.style.display = 'none';

        const statusCls = { active: 'badge-active', draft: 'badge-draft', expired: 'badge-expired' };
        const riskCls = { high: 'risk-high', medium: 'risk-medium', low: 'risk-low' };

        grid.innerHTML = filtered.map(j => {
            const hazards = (j.hazards || []).slice(0, 3);
            const signoffs = j.signoffs || [];
            const pending = j.crew_count ? j.crew_count - signoffs.length : 0;
            return `
            <div class="jha-card" onclick="viewJHA('${j.id}')">
                <div class="jha-card-header">
                    <h3>${j.title || ''}</h3>
                    <span class="badge ${statusCls[j.status] || 'badge-draft'}">${j.status || 'draft'}</span>
                </div>
                <div class="jha-card-meta">
                    <span>${j.project_name || ''}</span>
                    <span>${j.date || ''}</span>
                    <span>${j.supervisor || ''}</span>
                </div>
                <div class="hazard-list">
                    ${hazards.map(h => `
                        <div class="hazard-item">
                            <span class="risk ${riskCls[h.risk] || 'risk-medium'}">${h.risk || 'med'}</span>
                            <span>${h.description || ''}</span>
                        </div>
                    `).join('')}
                    ${(j.hazards || []).length > 3 ? `<div style="font-size:12px;color:var(--tf-muted);padding:4px 12px">+${j.hazards.length - 3} more hazards</div>` : ''}
                </div>
                <div class="signoff-row">
                    ${signoffs.map(s => `<span class="signoff-badge">${s.name}</span>`).join('')}
                    ${pending > 0 ? `<span class="signoff-badge signoff-pending">${pending} pending</span>` : ''}
                </div>
            </div>`;
        }).join('');
    }

    function updateStats() {
        document.getElementById('stat-total').textContent = jhas.length;
        document.getElementById('stat-active').textContent = jhas.filter(j => j.status === 'active').length;
        document.getElementById('stat-drafts').textContent = jhas.filter(j => j.status === 'draft').length;
        document.getElementById('stat-signoff').textContent = jhas.filter(j => (j.crew_count || 0) > (j.signoffs || []).length).length;
    }

    function openJHAModal() {
        editingId = null;
        document.getElementById('jhaModalTitle').textContent = 'New Job Hazard Analysis';
        document.getElementById('jhaForm').reset();
        document.getElementById('jhaDate').value = new Date().toISOString().split('T')[0];
        document.getElementById('hazardRows').innerHTML = `
            <div class="hazard-row">
                <input type="text" placeholder="Hazard description">
                <select><option value="high">High</option><option value="medium" selected>Medium</option><option value="low">Low</option></select>
                <input type="text" placeholder="Control measure">
                <button type="button" class="hazard-remove" onclick="this.parentElement.remove()">x</button>
            </div>`;
        document.getElementById('jhaModal').classList.add('active');
    }

    function addHazardRow() {
        const row = document.createElement('div');
        row.className = 'hazard-row';
        row.innerHTML = `
            <input type="text" placeholder="Hazard description">
            <select><option value="high">High</option><option value="medium" selected>Medium</option><option value="low">Low</option></select>
            <input type="text" placeholder="Control measure">
            <button type="button" class="hazard-remove" onclick="this.parentElement.remove()">x</button>`;
        document.getElementById('hazardRows').appendChild(row);
    }

    function viewJHA(id) {
        const j = jhas.find(x => x.id === id);
        if (!j) return;
        editingId = id;
        document.getElementById('jhaModalTitle').textContent = 'Edit JHA';
        document.getElementById('jhaTitle').value = j.title || '';
        document.getElementById('jhaProject').value = j.project_id || '';
        document.getElementById('jhaActivity').value = j.activity || '';
        document.getElementById('jhaLocation').value = j.location || '';
        document.getElementById('jhaDate').value = j.date || '';
        document.getElementById('jhaSupervisor').value = j.supervisor || '';
        document.getElementById('jhaNotes').value = j.notes || '';
        const rows = (j.hazards || []).map(h => `
            <div class="hazard-row">
                <input type="text" value="${h.description || ''}" placeholder="Hazard description">
                <select>${['high','medium','low'].map(r => `<option value="${r}" ${r===h.risk?'selected':''}>${r.charAt(0).toUpperCase()+r.slice(1)}</option>`).join('')}</select>
                <input type="text" value="${h.control || ''}" placeholder="Control measure">
                <button type="button" class="hazard-remove" onclick="this.parentElement.remove()">x</button>
            </div>`).join('');
        document.getElementById('hazardRows').innerHTML = rows || '';
        document.getElementById('jhaModal').classList.add('active');
    }

    async function saveJHA(e) {
        e.preventDefault();
        const hazards = [];
        document.querySelectorAll('#hazardRows .hazard-row').forEach(row => {
            const inputs = row.querySelectorAll('input');
            const select = row.querySelector('select');
            if (inputs[0].value) hazards.push({ description: inputs[0].value, risk: select.value, control: inputs[1].value });
        });
        const payload = {
            id: editingId, title: document.getElementById('jhaTitle').value,
            project_id: document.getElementById('jhaProject').value,
            activity: document.getElementById('jhaActivity').value,
            location: document.getElementById('jhaLocation').value,
            date: document.getElementById('jhaDate').value,
            supervisor: document.getElementById('jhaSupervisor').value,
            notes: document.getElementById('jhaNotes').value,
            hazards: hazards
        };
        try {
            await fetch('/api/field/jha', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
            closeModal('jhaModal');
            loadJHAs();
        } catch(e) { alert('Error saving JHA'); }
    }

    function closeModal(id) { document.getElementById(id).classList.remove('active'); }
    window.addEventListener('click', e => { if (e.target.classList.contains('modal-overlay')) e.target.classList.remove('active'); });

    document.addEventListener('DOMContentLoaded', loadJHAs);
</script>
"""
