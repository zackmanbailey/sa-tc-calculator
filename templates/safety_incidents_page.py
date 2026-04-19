"""
TitanForge v4 -- Safety Incident Reporting
=============================================
OSHA recordable tracking, near-miss reports, investigation forms, corrective actions.
"""

SAFETY_INCIDENTS_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a; --tf-card: #1e293b; --tf-text: #e2e8f0;
        --tf-muted: #94a3b8; --tf-gold: #d4a843; --tf-blue: #3b82f6;
        --tf-green: #10b981; --tf-red: #ef4444; --tf-orange: #f59e0b;
    }
    .incidents-container {
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

    .days-counter {
        background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(16,185,129,0.05));
        border: 2px solid rgba(16,185,129,0.2); border-radius: 16px;
        padding: 24px; text-align: center; margin-bottom: 24px;
    }
    .days-counter .big-number { font-size: 64px; font-weight: 900; color: var(--tf-green); line-height: 1; }
    .days-counter .days-label { font-size: 16px; font-weight: 600; color: var(--tf-green); margin-top: 4px; }
    .days-counter .sub { font-size: 13px; color: var(--tf-muted); margin-top: 8px; }

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
    .btn-danger { background: var(--tf-red); color: #fff; }

    .timeline {
        position: relative; padding-left: 30px; margin-bottom: 20px;
    }
    .timeline::before {
        content: ''; position: absolute; left: 10px; top: 0; bottom: 0;
        width: 2px; background: rgba(255,255,255,0.06);
    }
    .timeline-item {
        position: relative; background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06); padding: 20px 24px;
        margin-bottom: 16px; cursor: pointer; transition: border-color 0.2s;
    }
    .timeline-item:hover { border-color: var(--tf-blue); }
    .timeline-item::before {
        content: ''; position: absolute; left: -24px; top: 24px;
        width: 10px; height: 10px; border-radius: 50%;
    }
    .timeline-item.recordable::before { background: var(--tf-red); }
    .timeline-item.near-miss::before { background: var(--tf-orange); }
    .timeline-item.first-aid::before { background: var(--tf-blue); }

    .incident-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
    .incident-header h3 { font-size: 16px; font-weight: 700; margin: 0; }
    .incident-meta { display: flex; gap: 16px; font-size: 13px; color: var(--tf-muted); margin-bottom: 12px; }
    .incident-desc { font-size: 14px; color: var(--tf-muted); line-height: 1.5; }

    .corrective-actions { margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.04); }
    .corrective-actions h5 { font-size: 12px; font-weight: 700; color: var(--tf-muted); text-transform: uppercase; margin-bottom: 8px; }
    .action-item {
        display: flex; align-items: center; gap: 8px; font-size: 13px; margin-bottom: 4px;
    }
    .action-check { color: var(--tf-green); }
    .action-pending { color: var(--tf-orange); }

    .badge { display: inline-block; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
    .badge-recordable { background: rgba(239,68,68,0.15); color: var(--tf-red); }
    .badge-near-miss { background: rgba(245,158,11,0.15); color: var(--tf-orange); }
    .badge-first-aid { background: rgba(59,130,246,0.15); color: var(--tf-blue); }
    .badge-open { background: rgba(239,68,68,0.15); color: var(--tf-red); }
    .badge-investigating { background: rgba(245,158,11,0.15); color: var(--tf-orange); }
    .badge-closed { background: rgba(16,185,129,0.15); color: var(--tf-green); }

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
    .form-group textarea { min-height: 80px; resize: vertical; }
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
    .form-grid { grid-template-columns: 1fr; }
    .days-counter { font-size: 36px; }
}
@media (max-width: 480px) {
    .stat-row { grid-template-columns: 1fr; }
    .toolbar { gap: 8px; }
}
</style>

<div class="incidents-container">
    <div class="page-header">
        <h1>Incident Reporting</h1>
        <p>OSHA recordable tracking, near-miss reports, investigations, and corrective actions</p>
    </div>

    <div class="days-counter">
        <div class="big-number" id="daysSafe">0</div>
        <div class="days-label">Days Without a Recordable Incident</div>
        <div class="sub">Last incident: <span id="lastIncidentDate">N/A</span></div>
    </div>

    <div class="stat-row">
        <div class="stat-card stat-gold"><div class="label">Total Incidents</div><div class="value" id="stat-total">0</div></div>
        <div class="stat-card stat-red"><div class="label">OSHA Recordable</div><div class="value" id="stat-recordable">0</div></div>
        <div class="stat-card stat-orange"><div class="label">Near Misses</div><div class="value" id="stat-nearmiss">0</div></div>
        <div class="stat-card stat-blue"><div class="label">First Aid Only</div><div class="value" id="stat-firstaid">0</div></div>
        <div class="stat-card stat-green"><div class="label">Open Investigations</div><div class="value" id="stat-open">0</div></div>
    </div>

    <div class="toolbar">
        <div class="toolbar-left">
            <input type="text" id="searchInput" placeholder="Search incidents..." oninput="renderIncidents()">
            <select id="filterType" onchange="renderIncidents()">
                <option value="">All Types</option>
                <option value="recordable">OSHA Recordable</option>
                <option value="near_miss">Near Miss</option>
                <option value="first_aid">First Aid</option>
            </select>
            <select id="filterStatus" onchange="renderIncidents()">
                <option value="">All Status</option>
                <option value="open">Open</option>
                <option value="investigating">Investigating</option>
                <option value="closed">Closed</option>
            </select>
        </div>
        <button class="btn btn-danger" onclick="openIncidentModal()">+ Report Incident</button>
    </div>

    <div class="timeline" id="incidentTimeline"></div>

    <div class="empty-state" id="emptyState">
        <div class="icon">&#128994;</div>
        <h3>No Incidents Reported</h3>
        <p>A clean safety record! Continue to report any incidents or near-misses to maintain a safe work environment.</p>
        <button class="btn btn-primary" onclick="openIncidentModal()">+ Report Incident</button>
    </div>
</div>

<!-- Incident Modal -->
<div class="modal-overlay" id="incidentModal">
    <div class="modal">
        <button class="modal-close" onclick="closeModal('incidentModal')">&times;</button>
        <h2 id="incidentModalTitle">Report Incident</h2>
        <form id="incidentForm" onsubmit="saveIncident(event)">
            <div class="form-grid">
                <div class="form-group"><label>Incident Type</label>
                    <select id="incType" required>
                        <option value="">Select Type</option>
                        <option value="recordable">OSHA Recordable</option>
                        <option value="near_miss">Near Miss</option>
                        <option value="first_aid">First Aid Only</option>
                    </select>
                </div>
                <div class="form-group"><label>Date &amp; Time</label><input type="datetime-local" id="incDate" required></div>
                <div class="form-group form-full"><label>Title / Brief Description</label><input type="text" id="incTitle" required placeholder="What happened?"></div>
                <div class="form-group"><label>Location</label><input type="text" id="incLocation" placeholder="Where did it occur?"></div>
                <div class="form-group"><label>Project</label><select id="incProject"><option value="">Select Project</option></select></div>
                <div class="form-group"><label>Persons Involved</label><input type="text" id="incPersons" placeholder="Names (comma-separated)"></div>
                <div class="form-group"><label>Severity</label>
                    <select id="incSeverity">
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                        <option value="critical">Critical</option>
                    </select>
                </div>
                <div class="form-group form-full"><label>Detailed Description</label><textarea id="incDesc" placeholder="Full details of the incident..."></textarea></div>
                <div class="form-group form-full"><label>Immediate Actions Taken</label><textarea id="incActions" placeholder="What was done immediately after?"></textarea></div>
                <div class="form-group form-full"><label>Root Cause (if known)</label><textarea id="incCause" placeholder="Preliminary root cause analysis..." style="min-height:60px;"></textarea></div>
                <div class="form-group form-full"><label>Corrective Actions Required</label><textarea id="incCorrective" placeholder="List corrective actions needed..." style="min-height:60px;"></textarea></div>
                <div class="form-group form-full"><label>Photos / Evidence</label><input type="file" id="incPhotos" multiple accept="image/*" style="padding:8px;"></div>
            </div>
            <div class="modal-actions">
                <button type="button" class="btn btn-secondary" onclick="closeModal('incidentModal')">Cancel</button>
                <button type="submit" class="btn btn-danger">Submit Report</button>
            </div>
        </form>
    </div>
</div>

<script>
    let incidents = [];

    async function loadIncidents() {
        try {
            const resp = await fetch('/api/safety/incidents');
            const data = await resp.json();
            incidents = data.incidents || [];
            renderIncidents();
            updateStats();
            updateDaysCounter();
        } catch(e) { console.error('Failed to load incidents:', e); renderIncidents(); }
    }

    function renderIncidents() {
        const timeline = document.getElementById('incidentTimeline');
        const empty = document.getElementById('emptyState');
        const search = document.getElementById('searchInput').value.toLowerCase();
        const typeFilter = document.getElementById('filterType').value;
        const statusFilter = document.getElementById('filterStatus').value;

        let filtered = incidents.filter(i => {
            if (search && !JSON.stringify(i).toLowerCase().includes(search)) return false;
            if (typeFilter && i.type !== typeFilter) return false;
            if (statusFilter && i.status !== statusFilter) return false;
            return true;
        });

        if (filtered.length === 0) { timeline.innerHTML = ''; empty.style.display = 'block'; return; }
        empty.style.display = 'none';

        const typeCls = { recordable: 'recordable', near_miss: 'near-miss', first_aid: 'first-aid' };
        const typeBadge = { recordable: 'badge-recordable', near_miss: 'badge-near-miss', first_aid: 'badge-first-aid' };
        const typeLabel = { recordable: 'OSHA Recordable', near_miss: 'Near Miss', first_aid: 'First Aid' };
        const statusBadge = { open: 'badge-open', investigating: 'badge-investigating', closed: 'badge-closed' };

        timeline.innerHTML = filtered.map(i => {
            const actions = i.corrective_actions || [];
            return `
            <div class="timeline-item ${typeCls[i.type] || ''}" onclick="editIncident('${i.id}')">
                <div class="incident-header">
                    <h3>${i.title || ''}</h3>
                    <div style="display:flex;gap:8px;">
                        <span class="badge ${typeBadge[i.type] || ''}">${typeLabel[i.type] || i.type}</span>
                        <span class="badge ${statusBadge[i.status] || 'badge-open'}">${i.status || 'open'}</span>
                    </div>
                </div>
                <div class="incident-meta">
                    <span>${i.date || ''}</span>
                    <span>${i.location || ''}</span>
                    <span>${i.project_name || ''}</span>
                    <span>${i.persons || ''}</span>
                </div>
                <div class="incident-desc">${i.description || ''}</div>
                ${actions.length > 0 ? `
                <div class="corrective-actions">
                    <h5>Corrective Actions</h5>
                    ${actions.map(a => `<div class="action-item"><span class="${a.complete ? 'action-check' : 'action-pending'}">${a.complete ? '&#10003;' : '&#9675;'}</span>${a.description || ''}</div>`).join('')}
                </div>` : ''}
            </div>`;
        }).join('');
    }

    function updateStats() {
        document.getElementById('stat-total').textContent = incidents.length;
        document.getElementById('stat-recordable').textContent = incidents.filter(i => i.type === 'recordable').length;
        document.getElementById('stat-nearmiss').textContent = incidents.filter(i => i.type === 'near_miss').length;
        document.getElementById('stat-firstaid').textContent = incidents.filter(i => i.type === 'first_aid').length;
        document.getElementById('stat-open').textContent = incidents.filter(i => i.status !== 'closed').length;
    }

    function updateDaysCounter() {
        const recordables = incidents.filter(i => i.type === 'recordable').sort((a, b) => new Date(b.date) - new Date(a.date));
        if (recordables.length > 0) {
            const lastDate = new Date(recordables[0].date);
            const days = Math.floor((Date.now() - lastDate.getTime()) / (1000*60*60*24));
            document.getElementById('daysSafe').textContent = days;
            document.getElementById('lastIncidentDate').textContent = lastDate.toLocaleDateString();
        } else {
            document.getElementById('daysSafe').textContent = '365+';
            document.getElementById('lastIncidentDate').textContent = 'No recordable incidents';
        }
    }

    function openIncidentModal() {
        document.getElementById('incidentModalTitle').textContent = 'Report Incident';
        document.getElementById('incidentForm').reset();
        document.getElementById('incidentModal').classList.add('active');
    }

    function editIncident(id) {
        const i = incidents.find(x => x.id === id);
        if (!i) return;
        document.getElementById('incidentModalTitle').textContent = 'Edit Incident Report';
        document.getElementById('incType').value = i.type || '';
        document.getElementById('incDate').value = i.date || '';
        document.getElementById('incTitle').value = i.title || '';
        document.getElementById('incLocation').value = i.location || '';
        document.getElementById('incProject').value = i.project_id || '';
        document.getElementById('incPersons').value = i.persons || '';
        document.getElementById('incSeverity').value = i.severity || 'medium';
        document.getElementById('incDesc').value = i.description || '';
        document.getElementById('incActions').value = i.immediate_actions || '';
        document.getElementById('incCause').value = i.root_cause || '';
        document.getElementById('incCorrective').value = (i.corrective_actions || []).map(a => a.description).join('\n');
        document.getElementById('incidentModal').classList.add('active');
    }

    async function saveIncident(e) {
        e.preventDefault();
        const payload = {
            type: document.getElementById('incType').value,
            date: document.getElementById('incDate').value,
            title: document.getElementById('incTitle').value,
            location: document.getElementById('incLocation').value,
            project_id: document.getElementById('incProject').value,
            persons: document.getElementById('incPersons').value,
            severity: document.getElementById('incSeverity').value,
            description: document.getElementById('incDesc').value,
            immediate_actions: document.getElementById('incActions').value,
            root_cause: document.getElementById('incCause').value,
            corrective_actions_text: document.getElementById('incCorrective').value
        };
        try {
            await fetch('/api/safety/incidents', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
            closeModal('incidentModal');
            loadIncidents();
        } catch(e) { alert('Error saving incident'); }
    }

    function closeModal(id) { document.getElementById(id).classList.remove('active'); }
    window.addEventListener('click', e => { if (e.target.classList.contains('modal-overlay')) e.target.classList.remove('active'); });

    document.addEventListener('DOMContentLoaded', loadIncidents);
</script>
"""
