"""
TitanForge v4 -- Safety Training Management
==============================================
Certification tracking, training schedules, completion records, expiring certs alerts, training matrix.
"""

SAFETY_TRAINING_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a; --tf-card: #1e293b; --tf-text: #e2e8f0;
        --tf-muted: #94a3b8; --tf-gold: #d4a843; --tf-blue: #3b82f6;
        --tf-green: #10b981; --tf-red: #ef4444; --tf-orange: #f59e0b;
    }
    .training-container {
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
    .badge-current { background: rgba(16,185,129,0.15); color: var(--tf-green); }
    .badge-expiring { background: rgba(245,158,11,0.15); color: var(--tf-orange); }
    .badge-expired { background: rgba(239,68,68,0.15); color: var(--tf-red); }
    .badge-scheduled { background: rgba(59,130,246,0.15); color: var(--tf-blue); }
    .badge-complete { background: rgba(16,185,129,0.15); color: var(--tf-green); }

    /* Training Matrix */
    .matrix-table { font-size: 12px; }
    .matrix-table th { padding: 10px 8px; font-size: 10px; }
    .matrix-table td { padding: 8px; text-align: center; }
    .matrix-cell { width: 24px; height: 24px; border-radius: 4px; display: inline-block; }
    .matrix-yes { background: var(--tf-green); }
    .matrix-expiring { background: var(--tf-orange); }
    .matrix-no { background: rgba(255,255,255,0.06); }
    .matrix-expired { background: var(--tf-red); }

    /* Alert Cards */
    .alerts-section { margin-bottom: 24px; }
    .alert-card {
        display: flex; align-items: center; gap: 16px;
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06);
        padding: 16px 20px; margin-bottom: 8px;
    }
    .alert-card.urgent { border-left: 4px solid var(--tf-red); }
    .alert-card.warning { border-left: 4px solid var(--tf-orange); }
    .alert-icon { font-size: 24px; }
    .alert-content { flex: 1; }
    .alert-content .title { font-size: 14px; font-weight: 700; }
    .alert-content .desc { font-size: 13px; color: var(--tf-muted); margin-top: 2px; }

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
    .form-grid { grid-template-columns: 1fr; }
    .matrix-table { display: block; overflow-x: auto; -webkit-overflow-scrolling: touch; }
}
@media (max-width: 480px) {
    .stat-row { grid-template-columns: 1fr; }
    .toolbar { gap: 8px; }
}
</style>

<div class="training-container">
    <div class="page-header">
        <h1>Training Management</h1>
        <p>Track certifications, manage training schedules, and monitor compliance across all crew members</p>
    </div>

    <div class="stat-row">
        <div class="stat-card stat-gold"><div class="label">Total Certs</div><div class="value" id="stat-total">0</div></div>
        <div class="stat-card stat-green"><div class="label">Current</div><div class="value" id="stat-current">0</div></div>
        <div class="stat-card stat-orange"><div class="label">Expiring (30d)</div><div class="value" id="stat-expiring">0</div></div>
        <div class="stat-card stat-red"><div class="label">Expired</div><div class="value" id="stat-expired">0</div></div>
        <div class="stat-card stat-blue"><div class="label">Scheduled Training</div><div class="value" id="stat-scheduled">0</div></div>
    </div>

    <!-- Expiring Alerts -->
    <div class="alerts-section" id="alertsSection" style="display:none;">
        <div id="alertsList"></div>
    </div>

    <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('certs', this)">Certifications</button>
        <button class="tab-btn" onclick="switchTab('schedule', this)">Training Schedule</button>
        <button class="tab-btn" onclick="switchTab('matrix', this)">Training Matrix</button>
    </div>

    <!-- Certifications -->
    <div class="tab-panel active" id="panel-certs">
        <div class="toolbar">
            <div class="toolbar-left">
                <input type="text" id="searchCerts" placeholder="Search certifications..." oninput="renderCerts()">
                <select id="filterCertType" onchange="renderCerts()">
                    <option value="">All Types</option>
                    <option value="osha_10">OSHA 10</option>
                    <option value="osha_30">OSHA 30</option>
                    <option value="fall_protection">Fall Protection</option>
                    <option value="welding">Welding Cert</option>
                    <option value="crane_operator">Crane Operator</option>
                    <option value="forklift">Forklift</option>
                    <option value="first_aid">First Aid/CPR</option>
                    <option value="confined_space">Confined Space</option>
                </select>
                <select id="filterCertStatus" onchange="renderCerts()">
                    <option value="">All Status</option>
                    <option value="current">Current</option>
                    <option value="expiring">Expiring Soon</option>
                    <option value="expired">Expired</option>
                </select>
            </div>
            <button class="btn btn-primary" onclick="openCertModal()">+ Add Certification</button>
        </div>
        <table class="data-table">
            <thead><tr><th>Crew Member</th><th>Certification</th><th>Cert Number</th><th>Issued</th><th>Expires</th><th>Status</th><th>Actions</th></tr></thead>
            <tbody id="certsTable"></tbody>
        </table>
        <div class="empty-state" id="emptyCerts"><div class="icon">&#128218;</div><h3>No Certifications</h3><p>Track crew certifications and training completions.</p></div>
    </div>

    <!-- Training Schedule -->
    <div class="tab-panel" id="panel-schedule">
        <div class="toolbar">
            <div class="toolbar-left"><input type="text" placeholder="Search schedule..." oninput="renderSchedule()"></div>
            <button class="btn btn-primary" onclick="openScheduleModal()">+ Schedule Training</button>
        </div>
        <table class="data-table">
            <thead><tr><th>Training</th><th>Instructor</th><th>Date</th><th>Duration</th><th>Attendees</th><th>Status</th><th>Actions</th></tr></thead>
            <tbody id="scheduleTable"></tbody>
        </table>
        <div class="empty-state" id="emptySchedule"><div class="icon">&#128197;</div><h3>No Training Scheduled</h3><p>Schedule training sessions to keep certifications current.</p></div>
    </div>

    <!-- Training Matrix -->
    <div class="tab-panel" id="panel-matrix">
        <div style="overflow-x:auto;">
            <table class="data-table matrix-table" id="matrixTable">
                <thead><tr><th>Crew Member</th></tr></thead>
                <tbody></tbody>
            </table>
        </div>
        <div class="empty-state" id="emptyMatrix"><div class="icon">&#128200;</div><h3>No Matrix Data</h3><p>Add crew members and certifications to build the training matrix.</p></div>
        <div style="margin-top:16px;display:flex;gap:16px;font-size:12px;color:var(--tf-muted);">
            <span><span class="matrix-cell matrix-yes" style="width:12px;height:12px;display:inline-block;vertical-align:middle;margin-right:4px;"></span>Current</span>
            <span><span class="matrix-cell matrix-expiring" style="width:12px;height:12px;display:inline-block;vertical-align:middle;margin-right:4px;"></span>Expiring</span>
            <span><span class="matrix-cell matrix-expired" style="width:12px;height:12px;display:inline-block;vertical-align:middle;margin-right:4px;"></span>Expired</span>
            <span><span class="matrix-cell matrix-no" style="width:12px;height:12px;display:inline-block;vertical-align:middle;margin-right:4px;"></span>Not Required</span>
        </div>
    </div>
</div>

<!-- Certification Modal -->
<div class="modal-overlay" id="certModal">
    <div class="modal">
        <button class="modal-close" onclick="closeModal('certModal')">&times;</button>
        <h2>Add Certification</h2>
        <form id="certForm" onsubmit="saveCert(event)">
            <div class="form-grid">
                <div class="form-group"><label>Crew Member</label><select id="certPerson" required><option value="">Select</option></select></div>
                <div class="form-group"><label>Certification Type</label>
                    <select id="certType" required>
                        <option value="">Select Type</option>
                        <option value="osha_10">OSHA 10</option>
                        <option value="osha_30">OSHA 30</option>
                        <option value="fall_protection">Fall Protection</option>
                        <option value="welding">Welding Certification</option>
                        <option value="crane_operator">Crane Operator</option>
                        <option value="forklift">Forklift Operator</option>
                        <option value="first_aid">First Aid/CPR</option>
                        <option value="confined_space">Confined Space</option>
                    </select>
                </div>
                <div class="form-group"><label>Certificate Number</label><input type="text" id="certNumber"></div>
                <div class="form-group"><label>Issuing Organization</label><input type="text" id="certIssuer"></div>
                <div class="form-group"><label>Issue Date</label><input type="date" id="certIssued" required></div>
                <div class="form-group"><label>Expiration Date</label><input type="date" id="certExpires"></div>
            </div>
            <div class="modal-actions">
                <button type="button" class="btn btn-secondary" onclick="closeModal('certModal')">Cancel</button>
                <button type="submit" class="btn btn-primary">Save Certification</button>
            </div>
        </form>
    </div>
</div>

<!-- Schedule Modal -->
<div class="modal-overlay" id="scheduleModal">
    <div class="modal">
        <button class="modal-close" onclick="closeModal('scheduleModal')">&times;</button>
        <h2>Schedule Training</h2>
        <form id="scheduleForm" onsubmit="saveSchedule(event)">
            <div class="form-grid">
                <div class="form-group form-full"><label>Training Title</label><input type="text" id="schedTitle" required></div>
                <div class="form-group"><label>Instructor</label><input type="text" id="schedInstructor"></div>
                <div class="form-group"><label>Date</label><input type="date" id="schedDate" required></div>
                <div class="form-group"><label>Duration (hours)</label><input type="number" id="schedDuration" min="0.5" step="0.5"></div>
                <div class="form-group"><label>Location</label><input type="text" id="schedLocation"></div>
                <div class="form-group form-full"><label>Attendees (comma-separated)</label><input type="text" id="schedAttendees" placeholder="Names of attendees"></div>
            </div>
            <div class="modal-actions">
                <button type="button" class="btn btn-secondary" onclick="closeModal('scheduleModal')">Cancel</button>
                <button type="submit" class="btn btn-primary">Schedule</button>
            </div>
        </form>
    </div>
</div>

<script>
    let certs = [];
    let schedule = [];
    let matrix = {};

    function switchTab(tab, btn) {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById('panel-' + tab).classList.add('active');
    }

    async function loadTraining() {
        try {
            const resp = await fetch('/api/safety/training');
            const data = await resp.json();
            certs = data.certifications || [];
            schedule = data.schedule || [];
            matrix = data.matrix || {};
            renderCerts();
            renderSchedule();
            renderMatrix();
            renderAlerts();
            updateStats();
        } catch(e) { console.error('Failed to load training data:', e); renderCerts(); renderSchedule(); }
    }

    function getCertStatus(cert) {
        if (!cert.expires) return 'current';
        const now = new Date();
        const exp = new Date(cert.expires);
        const soon = new Date(now.getTime() + 30*24*60*60*1000);
        if (exp < now) return 'expired';
        if (exp < soon) return 'expiring';
        return 'current';
    }

    function renderCerts() {
        const tbody = document.getElementById('certsTable');
        const empty = document.getElementById('emptyCerts');
        const search = (document.getElementById('searchCerts').value || '').toLowerCase();
        const typeFilter = document.getElementById('filterCertType').value;
        const statusFilter = document.getElementById('filterCertStatus').value;

        let filtered = certs.filter(c => {
            if (search && !JSON.stringify(c).toLowerCase().includes(search)) return false;
            if (typeFilter && c.type !== typeFilter) return false;
            if (statusFilter && getCertStatus(c) !== statusFilter) return false;
            return true;
        });

        if (filtered.length === 0) { tbody.innerHTML = ''; empty.style.display = 'block'; return; }
        empty.style.display = 'none';
        const statusCls = { current: 'badge-current', expiring: 'badge-expiring', expired: 'badge-expired' };
        const typeLabels = { osha_10: 'OSHA 10', osha_30: 'OSHA 30', fall_protection: 'Fall Protection', welding: 'Welding', crane_operator: 'Crane Operator', forklift: 'Forklift', first_aid: 'First Aid/CPR', confined_space: 'Confined Space' };

        tbody.innerHTML = filtered.map(c => {
            const st = getCertStatus(c);
            return `<tr>
                <td style="font-weight:600">${c.person_name || ''}</td>
                <td>${typeLabels[c.type] || c.type || ''}</td>
                <td>${c.cert_number || '-'}</td>
                <td>${c.issued || '-'}</td>
                <td>${c.expires || 'No Expiry'}</td>
                <td><span class="badge ${statusCls[st]}">${st}</span></td>
                <td><button class="btn btn-sm btn-secondary" onclick="event.stopPropagation();editCert('${c.id}')">Edit</button></td>
            </tr>`;
        }).join('');
    }

    function renderSchedule() {
        const tbody = document.getElementById('scheduleTable');
        const empty = document.getElementById('emptySchedule');
        if (schedule.length === 0) { tbody.innerHTML = ''; empty.style.display = 'block'; return; }
        empty.style.display = 'none';
        const statusCls = { scheduled: 'badge-scheduled', complete: 'badge-complete' };
        tbody.innerHTML = schedule.map(s => `
            <tr>
                <td style="font-weight:600">${s.title || ''}</td>
                <td>${s.instructor || ''}</td>
                <td>${s.date || ''}</td>
                <td>${s.duration || ''}h</td>
                <td>${(s.attendees || []).length} attendees</td>
                <td><span class="badge ${statusCls[s.status] || 'badge-scheduled'}">${s.status || 'scheduled'}</span></td>
                <td><button class="btn btn-sm btn-secondary" onclick="event.stopPropagation()">Edit</button></td>
            </tr>
        `).join('');
    }

    function renderMatrix() {
        const table = document.getElementById('matrixTable');
        const empty = document.getElementById('emptyMatrix');
        const members = matrix.members || [];
        const types = matrix.cert_types || [];
        if (members.length === 0) { empty.style.display = 'block'; return; }
        empty.style.display = 'none';
        const thead = table.querySelector('thead tr');
        thead.innerHTML = '<th>Crew Member</th>' + types.map(t => `<th>${t}</th>`).join('');
        const tbody = table.querySelector('tbody');
        tbody.innerHTML = members.map(m => {
            const cells = types.map(t => {
                const st = (m.certs || {})[t] || 'none';
                const cls = st === 'current' ? 'matrix-yes' : st === 'expiring' ? 'matrix-expiring' : st === 'expired' ? 'matrix-expired' : 'matrix-no';
                return `<td><span class="matrix-cell ${cls}" title="${st}"></span></td>`;
            }).join('');
            return `<tr><td style="font-weight:600;white-space:nowrap">${m.name}</td>${cells}</tr>`;
        }).join('');
    }

    function renderAlerts() {
        const section = document.getElementById('alertsSection');
        const list = document.getElementById('alertsList');
        const expiring = certs.filter(c => getCertStatus(c) === 'expiring');
        const expired = certs.filter(c => getCertStatus(c) === 'expired');
        if (expiring.length === 0 && expired.length === 0) { section.style.display = 'none'; return; }
        section.style.display = 'block';
        let html = '';
        expired.forEach(c => { html += `<div class="alert-card urgent"><span class="alert-icon">&#9888;</span><div class="alert-content"><div class="title">${c.person_name} - ${c.type} EXPIRED</div><div class="desc">Expired on ${c.expires}. Immediate renewal required.</div></div><button class="btn btn-sm btn-primary" onclick="openCertModal()">Renew</button></div>`; });
        expiring.forEach(c => { html += `<div class="alert-card warning"><span class="alert-icon">&#9888;</span><div class="alert-content"><div class="title">${c.person_name} - ${c.type} Expiring Soon</div><div class="desc">Expires on ${c.expires}. Schedule renewal.</div></div><button class="btn btn-sm btn-secondary" onclick="openScheduleModal()">Schedule</button></div>`; });
        list.innerHTML = html;
    }

    function updateStats() {
        document.getElementById('stat-total').textContent = certs.length;
        document.getElementById('stat-current').textContent = certs.filter(c => getCertStatus(c) === 'current').length;
        document.getElementById('stat-expiring').textContent = certs.filter(c => getCertStatus(c) === 'expiring').length;
        document.getElementById('stat-expired').textContent = certs.filter(c => getCertStatus(c) === 'expired').length;
        document.getElementById('stat-scheduled').textContent = schedule.filter(s => s.status === 'scheduled').length;
    }

    function openCertModal() { document.getElementById('certForm').reset(); document.getElementById('certModal').classList.add('active'); }
    function openScheduleModal() { document.getElementById('scheduleForm').reset(); document.getElementById('scheduleModal').classList.add('active'); }
    function editCert(id) { openCertModal(); }

    async function saveCert(e) {
        e.preventDefault();
        const payload = {
            person_id: document.getElementById('certPerson').value,
            type: document.getElementById('certType').value,
            cert_number: document.getElementById('certNumber').value,
            issuer: document.getElementById('certIssuer').value,
            issued: document.getElementById('certIssued').value,
            expires: document.getElementById('certExpires').value
        };
        try {
            await fetch('/api/safety/training/cert', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
            closeModal('certModal'); loadTraining();
        } catch(e) { alert('Error saving certification'); }
    }

    async function saveSchedule(e) {
        e.preventDefault();
        const payload = {
            title: document.getElementById('schedTitle').value,
            instructor: document.getElementById('schedInstructor').value,
            date: document.getElementById('schedDate').value,
            duration: parseFloat(document.getElementById('schedDuration').value),
            location: document.getElementById('schedLocation').value,
            attendees: document.getElementById('schedAttendees').value.split(',').map(a => a.trim()).filter(Boolean)
        };
        try {
            await fetch('/api/safety/training/schedule', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
            closeModal('scheduleModal'); loadTraining();
        } catch(e) { alert('Error scheduling training'); }
    }

    function closeModal(id) { document.getElementById(id).classList.remove('active'); }
    window.addEventListener('click', e => { if (e.target.classList.contains('modal-overlay')) e.target.classList.remove('active'); });

    document.addEventListener('DOMContentLoaded', loadTraining);
</script>
"""
