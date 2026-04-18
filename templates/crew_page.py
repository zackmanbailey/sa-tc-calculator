"""
TitanForge v4 -- Crew Management
==================================
Crew roster, certifications, availability, project assignments, skill matrix, add/edit crew.
"""

CREW_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a; --tf-card: #1e293b; --tf-text: #e2e8f0;
        --tf-muted: #94a3b8; --tf-gold: #d4a843; --tf-blue: #3b82f6;
        --tf-green: #10b981; --tf-red: #ef4444; --tf-orange: #f59e0b;
    }
    .crew-container {
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
    .btn-danger { background: var(--tf-red); color: #fff; }

    .crew-grid {
        display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
        gap: 16px; margin-bottom: 20px;
    }
    .crew-card {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06);
        padding: 24px; transition: border-color 0.2s; cursor: pointer;
    }
    .crew-card:hover { border-color: var(--tf-blue); }
    .crew-card-top { display: flex; gap: 16px; align-items: center; margin-bottom: 16px; }
    .crew-avatar {
        width: 48px; height: 48px; border-radius: 50%;
        background: linear-gradient(135deg, var(--tf-blue), var(--tf-gold));
        display: flex; align-items: center; justify-content: center;
        font-size: 18px; font-weight: 800; color: #fff; flex-shrink: 0;
    }
    .crew-name { font-size: 16px; font-weight: 700; }
    .crew-role { font-size: 13px; color: var(--tf-muted); }

    .crew-meta {
        display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 12px;
    }
    .crew-meta-item .meta-label { font-size: 11px; color: var(--tf-muted); text-transform: uppercase; letter-spacing: 0.3px; }
    .crew-meta-item .meta-value { font-size: 13px; font-weight: 600; margin-top: 2px; }

    .skill-tags { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px; }
    .skill-tag {
        display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 11px;
        font-weight: 600; background: rgba(59,130,246,0.1); color: var(--tf-blue);
    }
    .cert-tags { display: flex; gap: 6px; flex-wrap: wrap; }
    .cert-tag {
        display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 11px;
        font-weight: 600;
    }
    .cert-current { background: rgba(16,185,129,0.1); color: var(--tf-green); }
    .cert-expiring { background: rgba(245,158,11,0.1); color: var(--tf-orange); }
    .cert-expired { background: rgba(239,68,68,0.1); color: var(--tf-red); }

    .badge { display: inline-block; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
    .badge-available { background: rgba(16,185,129,0.15); color: var(--tf-green); }
    .badge-assigned { background: rgba(59,130,246,0.15); color: var(--tf-blue); }
    .badge-off { background: rgba(148,163,184,0.15); color: var(--tf-muted); }
    .badge-leave { background: rgba(245,158,11,0.15); color: var(--tf-orange); }

    /* Skill Matrix Table */
    .matrix-table { font-size: 12px; }
    .matrix-table th { padding: 10px 8px; font-size: 10px; }
    .matrix-table td { padding: 8px; text-align: center; }
    .skill-level { display: inline-block; width: 20px; height: 20px; border-radius: 4px; font-size: 10px; font-weight: 800; line-height: 20px; text-align: center; }
    .skill-expert { background: var(--tf-green); color: #fff; }
    .skill-proficient { background: var(--tf-blue); color: #fff; }
    .skill-basic { background: var(--tf-orange); color: #fff; }
    .skill-none { background: rgba(255,255,255,0.06); color: var(--tf-muted); }

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

    .empty-state { text-align: center; padding: 60px 20px; color: var(--tf-muted); }
    .empty-state .icon { font-size: 48px; margin-bottom: 16px; opacity: 0.5; }
    .empty-state h3 { font-size: 18px; color: var(--tf-text); margin-bottom: 8px; }
    .empty-state p { font-size: 14px; max-width: 400px; margin: 0 auto 20px; }

    .modal-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 1000; align-items: center; justify-content: center; }
    .modal-overlay.active { display: flex; }
    .modal { background: var(--tf-card); border-radius: 16px; padding: 32px; width: 90%; max-width: 650px; max-height: 90vh; overflow-y: auto; border: 1px solid rgba(255,255,255,0.08); }
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
    .crew-grid { grid-template-columns: 1fr; }
    .tabs { overflow-x: auto; -webkit-overflow-scrolling: touch; flex-wrap: nowrap; }
    .tab-btn { white-space: nowrap; }
    .form-grid { grid-template-columns: 1fr; }
}
@media (max-width: 480px) {
    .stat-row { grid-template-columns: 1fr; }
    .toolbar { gap: 8px; }
}
</style>

<div class="crew-container">
    <div class="page-header">
        <h1>Crew Management</h1>
        <p>Manage crew roster, track certifications, availability, skills, and project assignments</p>
    </div>

    <div class="stat-row">
        <div class="stat-card stat-gold"><div class="label">Total Crew</div><div class="value" id="stat-total">0</div></div>
        <div class="stat-card stat-green"><div class="label">Available</div><div class="value" id="stat-available">0</div></div>
        <div class="stat-card stat-blue"><div class="label">Assigned</div><div class="value" id="stat-assigned">0</div></div>
        <div class="stat-card stat-orange"><div class="label">On Leave</div><div class="value" id="stat-leave">0</div></div>
        <div class="stat-card stat-red"><div class="label">Expiring Certs</div><div class="value" id="stat-expiring">0</div></div>
    </div>

    <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('roster', this)">Roster</button>
        <button class="tab-btn" onclick="switchTab('assignments', this)">Assignments</button>
        <button class="tab-btn" onclick="switchTab('skills', this)">Skill Matrix</button>
    </div>

    <!-- Roster Tab -->
    <div class="tab-panel active" id="panel-roster">
        <div class="toolbar">
            <div class="toolbar-left">
                <input type="text" id="searchCrew" placeholder="Search crew..." oninput="renderCrew()">
                <select id="filterRole" onchange="renderCrew()">
                    <option value="">All Roles</option>
                    <option value="foreman">Foreman</option>
                    <option value="lead">Lead</option>
                    <option value="welder">Welder</option>
                    <option value="fitter">Fitter</option>
                    <option value="helper">Helper</option>
                    <option value="operator">Operator</option>
                    <option value="driver">Driver</option>
                </select>
                <select id="filterAvail" onchange="renderCrew()">
                    <option value="">All Status</option>
                    <option value="available">Available</option>
                    <option value="assigned">Assigned</option>
                    <option value="off">Off</option>
                    <option value="leave">On Leave</option>
                </select>
            </div>
            <button class="btn btn-primary" onclick="openCrewModal()">+ Add Crew Member</button>
        </div>

        <div class="crew-grid" id="crewGrid"></div>

        <div class="empty-state" id="emptyRoster">
            <div class="icon">&#128119;</div>
            <h3>No Crew Members</h3>
            <p>Add crew members to manage assignments, certifications, and skills.</p>
            <button class="btn btn-primary" onclick="openCrewModal()">+ Add First Crew Member</button>
        </div>
    </div>

    <!-- Assignments Tab -->
    <div class="tab-panel" id="panel-assignments">
        <table class="data-table">
            <thead><tr><th>Crew Member</th><th>Role</th><th>Project</th><th>Start</th><th>End</th><th>Status</th></tr></thead>
            <tbody id="assignmentsTable"></tbody>
        </table>
        <div class="empty-state" id="emptyAssignments"><div class="icon">&#128203;</div><h3>No Assignments</h3><p>Assign crew members to field projects.</p></div>
    </div>

    <!-- Skill Matrix Tab -->
    <div class="tab-panel" id="panel-skills">
        <div style="overflow-x:auto;">
            <table class="data-table matrix-table" id="skillMatrix">
                <thead><tr><th>Crew Member</th></tr></thead>
                <tbody></tbody>
            </table>
        </div>
        <div class="empty-state" id="emptySkills"><div class="icon">&#128200;</div><h3>No Skill Data</h3><p>Add crew members and their skills to build the matrix.</p></div>
        <div style="margin-top:16px;display:flex;gap:16px;font-size:12px;color:var(--tf-muted);">
            <span><span class="skill-level skill-expert" style="width:12px;height:12px;display:inline-block;vertical-align:middle;margin-right:4px;">E</span>Expert</span>
            <span><span class="skill-level skill-proficient" style="width:12px;height:12px;display:inline-block;vertical-align:middle;margin-right:4px;">P</span>Proficient</span>
            <span><span class="skill-level skill-basic" style="width:12px;height:12px;display:inline-block;vertical-align:middle;margin-right:4px;">B</span>Basic</span>
            <span><span class="skill-level skill-none" style="width:12px;height:12px;display:inline-block;vertical-align:middle;margin-right:4px;">-</span>None</span>
        </div>
    </div>
</div>

<!-- Crew Member Modal -->
<div class="modal-overlay" id="crewModal">
    <div class="modal">
        <button class="modal-close" onclick="closeModal('crewModal')">&times;</button>
        <h2 id="crewModalTitle">Add Crew Member</h2>
        <form id="crewForm" onsubmit="saveCrew(event)">
            <div class="form-grid">
                <div class="form-group"><label>First Name</label><input type="text" id="crewFirst" required></div>
                <div class="form-group"><label>Last Name</label><input type="text" id="crewLast" required></div>
                <div class="form-group"><label>Role</label>
                    <select id="crewRole" required>
                        <option value="">Select Role</option>
                        <option value="foreman">Foreman</option>
                        <option value="lead">Lead</option>
                        <option value="welder">Welder</option>
                        <option value="fitter">Fitter</option>
                        <option value="helper">Helper</option>
                        <option value="operator">Operator</option>
                        <option value="driver">Driver</option>
                    </select>
                </div>
                <div class="form-group"><label>Phone</label><input type="tel" id="crewPhone"></div>
                <div class="form-group"><label>Email</label><input type="email" id="crewEmail"></div>
                <div class="form-group"><label>Hire Date</label><input type="date" id="crewHire"></div>
                <div class="form-group form-full"><label>Skills (comma-separated)</label><input type="text" id="crewSkills" placeholder="e.g. MIG welding, rigging, crane signals"></div>
                <div class="form-group form-full"><label>Certifications (comma-separated)</label><input type="text" id="crewCerts" placeholder="e.g. OSHA 10, Fall Protection"></div>
                <div class="form-group form-full"><label>Emergency Contact</label><input type="text" id="crewEmergency" placeholder="Name - Phone"></div>
                <div class="form-group form-full"><label>Notes</label><textarea id="crewNotes" placeholder="Additional information..."></textarea></div>
            </div>
            <div class="modal-actions">
                <button type="button" class="btn btn-secondary" onclick="closeModal('crewModal')">Cancel</button>
                <button type="submit" class="btn btn-primary">Save Crew Member</button>
            </div>
        </form>
    </div>
</div>

<script>
    let crew = [];
    let assignments = [];
    let editingId = null;

    function switchTab(tab, btn) {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById('panel-' + tab).classList.add('active');
    }

    async function loadCrew() {
        try {
            const resp = await fetch('/api/crew');
            const data = await resp.json();
            crew = data.members || [];
            assignments = data.assignments || [];
            renderCrew();
            renderAssignments();
            renderSkillMatrix();
            updateStats();
        } catch(e) { console.error('Failed to load crew:', e); renderCrew(); }
    }

    function renderCrew() {
        const grid = document.getElementById('crewGrid');
        const empty = document.getElementById('emptyRoster');
        const search = (document.getElementById('searchCrew').value || '').toLowerCase();
        const roleFilter = document.getElementById('filterRole').value;
        const availFilter = document.getElementById('filterAvail').value;

        let filtered = crew.filter(c => {
            if (search && !JSON.stringify(c).toLowerCase().includes(search)) return false;
            if (roleFilter && c.role !== roleFilter) return false;
            if (availFilter && c.availability !== availFilter) return false;
            return true;
        });

        if (filtered.length === 0) { grid.innerHTML = ''; empty.style.display = 'block'; return; }
        empty.style.display = 'none';

        const availCls = { available: 'badge-available', assigned: 'badge-assigned', off: 'badge-off', leave: 'badge-leave' };
        const roleLabels = { foreman: 'Foreman', lead: 'Lead', welder: 'Welder', fitter: 'Fitter', helper: 'Helper', operator: 'Operator', driver: 'Driver' };

        grid.innerHTML = filtered.map(c => {
            const initials = ((c.first_name || '')[0] || '') + ((c.last_name || '')[0] || '');
            const skills = c.skills || [];
            const certs = c.certifications || [];
            return `
            <div class="crew-card" onclick="editCrew('${c.id}')">
                <div class="crew-card-top">
                    <div class="crew-avatar">${initials}</div>
                    <div>
                        <div class="crew-name">${c.first_name || ''} ${c.last_name || ''}</div>
                        <div class="crew-role">${roleLabels[c.role] || c.role || ''}</div>
                    </div>
                    <span class="badge ${availCls[c.availability] || 'badge-available'}" style="margin-left:auto;">${c.availability || 'available'}</span>
                </div>
                <div class="crew-meta">
                    <div class="crew-meta-item"><div class="meta-label">Phone</div><div class="meta-value">${c.phone || '-'}</div></div>
                    <div class="crew-meta-item"><div class="meta-label">Current Project</div><div class="meta-value">${c.current_project || 'Unassigned'}</div></div>
                    <div class="crew-meta-item"><div class="meta-label">Hire Date</div><div class="meta-value">${c.hire_date || '-'}</div></div>
                    <div class="crew-meta-item"><div class="meta-label">Years</div><div class="meta-value">${c.years_experience || '-'}</div></div>
                </div>
                ${skills.length > 0 ? `<div class="skill-tags">${skills.slice(0,4).map(s => `<span class="skill-tag">${s}</span>`).join('')}${skills.length > 4 ? `<span class="skill-tag">+${skills.length-4}</span>` : ''}</div>` : ''}
                ${certs.length > 0 ? `<div class="cert-tags">${certs.slice(0,3).map(c => `<span class="cert-tag cert-current">${c.name || c}</span>`).join('')}</div>` : ''}
            </div>`;
        }).join('');
    }

    function renderAssignments() {
        const tbody = document.getElementById('assignmentsTable');
        const empty = document.getElementById('emptyAssignments');
        if (assignments.length === 0) { tbody.innerHTML = ''; empty.style.display = 'block'; return; }
        empty.style.display = 'none';
        const statusCls = { active: 'badge-available', complete: 'badge-assigned', upcoming: 'badge-off' };
        tbody.innerHTML = assignments.map(a => `
            <tr>
                <td style="font-weight:600">${a.crew_name || ''}</td>
                <td>${a.role || ''}</td>
                <td>${a.project_name || ''}</td>
                <td>${a.start_date || ''}</td>
                <td>${a.end_date || ''}</td>
                <td><span class="badge ${statusCls[a.status] || ''}">${a.status || ''}</span></td>
            </tr>
        `).join('');
    }

    function renderSkillMatrix() {
        const table = document.getElementById('skillMatrix');
        const empty = document.getElementById('emptySkills');
        if (crew.length === 0) { empty.style.display = 'block'; return; }
        empty.style.display = 'none';

        const allSkills = [...new Set(crew.flatMap(c => (c.skills || []).map(s => typeof s === 'string' ? s : s.name)))];
        if (allSkills.length === 0) { empty.style.display = 'block'; return; }

        const thead = table.querySelector('thead tr');
        thead.innerHTML = '<th>Crew Member</th>' + allSkills.map(s => `<th>${s}</th>`).join('');
        const tbody = table.querySelector('tbody');
        tbody.innerHTML = crew.map(c => {
            const memberSkills = (c.skills || []).map(s => typeof s === 'string' ? s : s.name);
            const skillLevels = {};
            (c.skills || []).forEach(s => {
                if (typeof s === 'object') skillLevels[s.name] = s.level;
                else skillLevels[s] = 'proficient';
            });
            const cells = allSkills.map(s => {
                const level = skillLevels[s] || (memberSkills.includes(s) ? 'proficient' : 'none');
                const cls = level === 'expert' ? 'skill-expert' : level === 'proficient' ? 'skill-proficient' : level === 'basic' ? 'skill-basic' : 'skill-none';
                const label = level === 'expert' ? 'E' : level === 'proficient' ? 'P' : level === 'basic' ? 'B' : '-';
                return `<td><span class="skill-level ${cls}">${label}</span></td>`;
            }).join('');
            return `<tr><td style="font-weight:600;white-space:nowrap">${c.first_name || ''} ${c.last_name || ''}</td>${cells}</tr>`;
        }).join('');
    }

    function updateStats() {
        document.getElementById('stat-total').textContent = crew.length;
        document.getElementById('stat-available').textContent = crew.filter(c => c.availability === 'available').length;
        document.getElementById('stat-assigned').textContent = crew.filter(c => c.availability === 'assigned').length;
        document.getElementById('stat-leave').textContent = crew.filter(c => c.availability === 'leave').length;
        const expiring = crew.reduce((count, c) => count + (c.certifications || []).filter(cert => cert.status === 'expiring').length, 0);
        document.getElementById('stat-expiring').textContent = expiring;
    }

    function openCrewModal() {
        editingId = null;
        document.getElementById('crewModalTitle').textContent = 'Add Crew Member';
        document.getElementById('crewForm').reset();
        document.getElementById('crewModal').classList.add('active');
    }

    function editCrew(id) {
        const c = crew.find(x => x.id === id);
        if (!c) return;
        editingId = id;
        document.getElementById('crewModalTitle').textContent = 'Edit Crew Member';
        document.getElementById('crewFirst').value = c.first_name || '';
        document.getElementById('crewLast').value = c.last_name || '';
        document.getElementById('crewRole').value = c.role || '';
        document.getElementById('crewPhone').value = c.phone || '';
        document.getElementById('crewEmail').value = c.email || '';
        document.getElementById('crewHire').value = c.hire_date || '';
        document.getElementById('crewSkills').value = (c.skills || []).map(s => typeof s === 'string' ? s : s.name).join(', ');
        document.getElementById('crewCerts').value = (c.certifications || []).map(c => c.name || c).join(', ');
        document.getElementById('crewEmergency').value = c.emergency_contact || '';
        document.getElementById('crewNotes').value = c.notes || '';
        document.getElementById('crewModal').classList.add('active');
    }

    async function saveCrew(e) {
        e.preventDefault();
        const payload = {
            id: editingId,
            first_name: document.getElementById('crewFirst').value,
            last_name: document.getElementById('crewLast').value,
            role: document.getElementById('crewRole').value,
            phone: document.getElementById('crewPhone').value,
            email: document.getElementById('crewEmail').value,
            hire_date: document.getElementById('crewHire').value,
            skills: document.getElementById('crewSkills').value.split(',').map(s => s.trim()).filter(Boolean),
            certifications: document.getElementById('crewCerts').value.split(',').map(c => c.trim()).filter(Boolean),
            emergency_contact: document.getElementById('crewEmergency').value,
            notes: document.getElementById('crewNotes').value
        };
        try {
            await fetch('/api/crew', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
            closeModal('crewModal');
            loadCrew();
        } catch(e) { alert('Error saving crew member'); }
    }

    function closeModal(id) { document.getElementById(id).classList.remove('active'); }
    window.addEventListener('click', e => { if (e.target.classList.contains('modal-overlay')) e.target.classList.remove('active'); });

    document.addEventListener('DOMContentLoaded', loadCrew);
</script>
"""
