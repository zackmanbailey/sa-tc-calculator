"""
TitanForge v4 -- Field Projects Overview
==========================================
Active installs, crew assignments, completion percentages, schedule, weather delays.
"""

FIELD_PROJECTS_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a; --tf-card: #1e293b; --tf-text: #e2e8f0;
        --tf-muted: #94a3b8; --tf-gold: #d4a843; --tf-blue: #3b82f6;
        --tf-green: #10b981; --tf-red: #ef4444; --tf-orange: #f59e0b;
    }
    .fp-container {
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

    .project-cards {
        display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
        gap: 20px; margin-bottom: 20px;
    }
    .proj-card {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06);
        padding: 24px; transition: border-color 0.2s; cursor: pointer;
    }
    .proj-card:hover { border-color: var(--tf-blue); }
    .proj-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
    .proj-header h3 { font-size: 18px; font-weight: 700; margin: 0; }
    .proj-header .code { font-size: 12px; color: var(--tf-muted); margin-top: 2px; }

    .progress-section { margin-bottom: 16px; }
    .progress-label { display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 6px; }
    .progress-bar { height: 8px; background: rgba(255,255,255,0.06); border-radius: 4px; overflow: hidden; }
    .progress-bar .fill { height: 100%; border-radius: 4px; transition: width 0.4s; }

    .proj-meta {
        display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px;
    }
    .proj-meta-item .meta-label { font-size: 11px; color: var(--tf-muted); text-transform: uppercase; letter-spacing: 0.3px; }
    .proj-meta-item .meta-value { font-size: 14px; font-weight: 600; margin-top: 2px; }

    .crew-badges { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px; }
    .crew-badge {
        display: inline-flex; align-items: center; gap: 4px;
        padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 600;
        background: rgba(59,130,246,0.1); color: var(--tf-blue);
    }

    .delay-tag {
        display: inline-flex; align-items: center; gap: 4px;
        padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 600;
        background: rgba(239,68,68,0.1); color: var(--tf-red);
    }

    .badge { display: inline-block; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
    .badge-active { background: rgba(16,185,129,0.15); color: var(--tf-green); }
    .badge-scheduled { background: rgba(59,130,246,0.15); color: var(--tf-blue); }
    .badge-delayed { background: rgba(239,68,68,0.15); color: var(--tf-red); }
    .badge-complete { background: rgba(212,168,67,0.15); color: var(--tf-gold); }

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
    .modal-overlay .modal, .modal { width: 95%; max-width: 95vw; margin: 20px auto; padding: 20px; }
    .project-cards { grid-template-columns: 1fr; }
    .form-grid { grid-template-columns: 1fr; }
}
@media (max-width: 480px) {
    .stat-row { grid-template-columns: 1fr; }
    .toolbar { gap: 8px; }
}
</style>

<div class="fp-container">
    <div class="page-header">
        <h1>Field Projects</h1>
        <p>Overview of active field installations, crew assignments, and project progress</p>
    </div>

    <div class="stat-row">
        <div class="stat-card stat-gold"><div class="label">Active Installs</div><div class="value" id="stat-active">0</div></div>
        <div class="stat-card stat-blue"><div class="label">Crew Deployed</div><div class="value" id="stat-crew">0</div></div>
        <div class="stat-card stat-green"><div class="label">Avg Completion</div><div class="value" id="stat-completion">0%</div></div>
        <div class="stat-card stat-red"><div class="label">Delayed</div><div class="value" id="stat-delayed">0</div></div>
    </div>

    <div class="toolbar">
        <div class="toolbar-left">
            <input type="text" id="searchInput" placeholder="Search projects..." oninput="renderProjects()">
            <select id="filterStatus" onchange="renderProjects()">
                <option value="">All Status</option>
                <option value="active">Active</option>
                <option value="scheduled">Scheduled</option>
                <option value="delayed">Delayed</option>
                <option value="complete">Complete</option>
            </select>
        </div>
        <button class="btn btn-primary" onclick="openAssignModal()">+ Assign Crew</button>
    </div>

    <div class="project-cards" id="projectGrid"></div>

    <div class="empty-state" id="emptyState">
        <div class="icon">&#127959;</div>
        <h3>No Field Projects</h3>
        <p>Active field installations will appear here with crew assignments and progress tracking.</p>
    </div>
</div>

<!-- Assign Crew Modal -->
<div class="modal-overlay" id="assignModal">
    <div class="modal">
        <button class="modal-close" onclick="closeModal('assignModal')">&times;</button>
        <h2>Assign Crew to Project</h2>
        <form id="assignForm" onsubmit="saveAssignment(event)">
            <div class="form-grid">
                <div class="form-group"><label>Project</label><select id="assignProject" required><option value="">Select Project</option></select></div>
                <div class="form-group"><label>Crew Lead</label><input type="text" id="assignLead" placeholder="Crew lead name"></div>
                <div class="form-group form-full"><label>Crew Members (comma-separated)</label><input type="text" id="assignMembers" placeholder="e.g. John, Mike, Sarah"></div>
                <div class="form-group"><label>Start Date</label><input type="date" id="assignStart"></div>
                <div class="form-group"><label>Est. End Date</label><input type="date" id="assignEnd"></div>
                <div class="form-group form-full"><label>Notes</label><textarea id="assignNotes" placeholder="Special instructions, equipment needs..."></textarea></div>
            </div>
            <div class="modal-actions">
                <button type="button" class="btn btn-secondary" onclick="closeModal('assignModal')">Cancel</button>
                <button type="submit" class="btn btn-primary">Assign Crew</button>
            </div>
        </form>
    </div>
</div>

<script>
    let projects = [];

    async function loadProjects() {
        try {
            const resp = await fetch('/api/field/projects');
            const data = await resp.json();
            projects = data.projects || [];
            renderProjects();
            updateStats();
        } catch(e) { console.error('Failed to load field projects:', e); renderProjects(); }
    }

    function renderProjects() {
        const grid = document.getElementById('projectGrid');
        const empty = document.getElementById('emptyState');
        const search = document.getElementById('searchInput').value.toLowerCase();
        const statusFilter = document.getElementById('filterStatus').value;

        let filtered = projects.filter(p => {
            if (search && !JSON.stringify(p).toLowerCase().includes(search)) return false;
            if (statusFilter && p.status !== statusFilter) return false;
            return true;
        });

        if (filtered.length === 0) { grid.innerHTML = ''; empty.style.display = 'block'; return; }
        empty.style.display = 'none';

        const statusCls = { active: 'badge-active', scheduled: 'badge-scheduled', delayed: 'badge-delayed', complete: 'badge-complete' };
        const progressColors = pct => pct >= 75 ? '#10b981' : pct >= 40 ? '#3b82f6' : pct >= 10 ? '#f59e0b' : '#94a3b8';

        grid.innerHTML = filtered.map(p => {
            const pct = p.completion_pct || 0;
            const crew = p.crew || [];
            const delays = p.delays || [];
            return `
            <div class="proj-card" onclick="viewProject('${p.id}')">
                <div class="proj-header">
                    <div>
                        <h3>${p.name || p.project_name || ''}</h3>
                        <div class="code">${p.project_code || p.id || ''}</div>
                    </div>
                    <span class="badge ${statusCls[p.status] || 'badge-active'}">${p.status || 'active'}</span>
                </div>
                <div class="progress-section">
                    <div class="progress-label">
                        <span>Completion</span><span style="font-weight:700;color:${progressColors(pct)}">${pct}%</span>
                    </div>
                    <div class="progress-bar"><div class="fill" style="width:${pct}%;background:${progressColors(pct)}"></div></div>
                </div>
                <div class="proj-meta">
                    <div class="proj-meta-item"><div class="meta-label">Location</div><div class="meta-value">${p.location || 'TBD'}</div></div>
                    <div class="proj-meta-item"><div class="meta-label">Start Date</div><div class="meta-value">${p.start_date || 'TBD'}</div></div>
                    <div class="proj-meta-item"><div class="meta-label">Est. Completion</div><div class="meta-value">${p.end_date || 'TBD'}</div></div>
                    <div class="proj-meta-item"><div class="meta-label">Crew Size</div><div class="meta-value">${crew.length} members</div></div>
                </div>
                <div class="crew-badges">
                    ${crew.slice(0,5).map(c => `<span class="crew-badge">${c.name || c}</span>`).join('')}
                    ${crew.length > 5 ? `<span class="crew-badge">+${crew.length - 5}</span>` : ''}
                </div>
                ${delays.length > 0 ? delays.map(d => `<span class="delay-tag">${d.reason || d}: ${d.days || '?'} days</span>`).join(' ') : ''}
            </div>`;
        }).join('');
    }

    function updateStats() {
        document.getElementById('stat-active').textContent = projects.filter(p => p.status === 'active').length;
        const totalCrew = projects.reduce((s, p) => s + (p.crew || []).length, 0);
        document.getElementById('stat-crew').textContent = totalCrew;
        const active = projects.filter(p => p.status !== 'complete');
        const avgPct = active.length ? Math.round(active.reduce((s, p) => s + (p.completion_pct || 0), 0) / active.length) : 0;
        document.getElementById('stat-completion').textContent = avgPct + '%';
        document.getElementById('stat-delayed').textContent = projects.filter(p => p.status === 'delayed').length;
    }

    function viewProject(id) {
        const p = projects.find(x => x.id === id);
        if (p && p.project_code) window.location.href = '/project/' + p.project_code;
    }

    function openAssignModal() {
        document.getElementById('assignForm').reset();
        document.getElementById('assignModal').classList.add('active');
    }

    async function saveAssignment(e) {
        e.preventDefault();
        const payload = {
            project_id: document.getElementById('assignProject').value,
            crew_lead: document.getElementById('assignLead').value,
            members: document.getElementById('assignMembers').value.split(',').map(m => m.trim()).filter(Boolean),
            start_date: document.getElementById('assignStart').value,
            end_date: document.getElementById('assignEnd').value,
            notes: document.getElementById('assignNotes').value
        };
        try {
            await fetch('/api/field/projects/assign', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
            closeModal('assignModal');
            loadProjects();
        } catch(e) { alert('Error saving assignment'); }
    }

    function closeModal(id) { document.getElementById(id).classList.remove('active'); }
    window.addEventListener('click', e => { if (e.target.classList.contains('modal-overlay')) e.target.classList.remove('active'); });

    document.addEventListener('DOMContentLoaded', loadProjects);
</script>
"""
