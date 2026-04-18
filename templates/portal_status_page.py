"""
TitanForge v4 — Customer Portal Status
=========================================
Project progress overview, milestone status, upcoming deliveries, open items.
"""

PORTAL_STATUS_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a;
        --tf-card: #1e293b;
        --tf-text: #e2e8f0;
        --tf-muted: #94a3b8;
        --tf-gold: #d4a843;
        --tf-blue: #3b82f6;
    }
    .portal-container {
        max-width: 1400px; margin: 0 auto; padding: 24px 32px;
        font-family: 'Inter', 'Segoe UI', sans-serif; color: var(--tf-text);
    }
    .page-header { margin-bottom: 32px; }
    .page-header h1 { font-size: 28px; font-weight: 800; margin: 0 0 6px 0; }
    .page-header p { font-size: 14px; color: var(--tf-muted); margin: 0; }
    .toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
    .toolbar select { background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px; }
    .btn-outline { background: transparent; color: var(--tf-muted); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 10px 20px; font-weight: 600; font-size: 14px; cursor: pointer; }
    .btn-outline:hover { border-color: var(--tf-gold); color: var(--tf-gold); }
    .stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
    @media (max-width: 900px) { .stats-row { grid-template-columns: 1fr 1fr; } }
    .stat-card { background: var(--tf-card); border-radius: 10px; padding: 18px; border: 1px solid rgba(255,255,255,0.06); }
    .stat-card .stat-label { font-size: 12px; color: var(--tf-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
    .stat-card .stat-value { font-size: 24px; font-weight: 800; }
    .section-title { font-size: 18px; font-weight: 700; margin: 28px 0 16px 0; }
    .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    @media (max-width: 900px) { .two-col { grid-template-columns: 1fr; } }
    .card { background: var(--tf-card); border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); padding: 20px; }
    .card h3 { font-size: 16px; font-weight: 700; margin: 0 0 16px 0; }
    .progress-bar-lg { height: 12px; background: rgba(255,255,255,0.08); border-radius: 6px; overflow: hidden; margin: 12px 0; }
    .progress-fill { height: 100%; border-radius: 6px; transition: width 0.5s; }
    .progress-fill.green { background: linear-gradient(90deg, #22c55e, #4ade80); }
    .progress-fill.blue { background: linear-gradient(90deg, var(--tf-blue), #60a5fa); }
    .progress-fill.gold { background: linear-gradient(90deg, #b8941f, var(--tf-gold)); }
    .milestone-list { list-style: none; padding: 0; margin: 0; }
    .milestone-item { display: flex; align-items: center; gap: 12px; padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.04); }
    .milestone-item:last-child { border-bottom: none; }
    .milestone-dot { width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }
    .milestone-dot.done { background: #4ade80; }
    .milestone-dot.active { background: var(--tf-blue); box-shadow: 0 0 8px rgba(59,130,246,0.4); }
    .milestone-dot.upcoming { background: rgba(255,255,255,0.15); }
    .milestone-text { flex: 1; font-size: 14px; }
    .milestone-text.done { color: var(--tf-muted); text-decoration: line-through; }
    .milestone-date { font-size: 12px; color: var(--tf-muted); white-space: nowrap; }
    .delivery-item { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.04); }
    .delivery-item:last-child { border-bottom: none; }
    .delivery-info { font-size: 14px; }
    .delivery-info small { display: block; font-size: 12px; color: var(--tf-muted); }
    .badge { display: inline-block; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; }
    .badge-green { background: rgba(34,197,94,0.2); color: #4ade80; }
    .badge-blue { background: rgba(59,130,246,0.2); color: #60a5fa; }
    .badge-gold { background: rgba(212,168,67,0.2); color: var(--tf-gold); }
    .open-item { display: flex; gap: 10px; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.04); font-size: 14px; }
    .open-item:last-child { border-bottom: none; }
    .open-num { color: var(--tf-blue); font-weight: 600; white-space: nowrap; }
    .contact-row { display: flex; gap: 12px; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.04); align-items: center; font-size: 14px; }
    .contact-row:last-child { border-bottom: none; }
    .contact-avatar { width: 36px; height: 36px; border-radius: 50%; background: var(--tf-blue); display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 700; color: #fff; flex-shrink: 0; }
    .contact-info small { display: block; color: var(--tf-muted); font-size: 12px; }
    .empty-state { text-align: center; padding: 40px 20px; color: var(--tf-muted); }
    .empty-state h3 { font-size: 18px; margin-bottom: 8px; color: var(--tf-text); }
    .loading { text-align: center; padding: 40px; color: var(--tf-muted); }
</style>

<div class="portal-container">
    <div class="page-header">
        <h1>Project Status</h1>
        <p>Customer-facing project progress overview and milestone tracking</p>
    </div>
    <div class="toolbar">
        <select id="projectSelect" onchange="loadProjectStatus()">
            <option value="">Select a project...</option>
        </select>
        <button class="btn-outline" onclick="refreshStatus()">Refresh</button>
    </div>
    <div id="statusContent">
        <div class="empty-state"><h3>Select a project</h3><p>Choose a project from the dropdown to view its status.</p></div>
    </div>
</div>

<script>
let projectData = null;

function renderStatus(data) {
    const el = document.getElementById('statusContent');
    if (!data) { el.innerHTML = '<div class="empty-state"><h3>No project data</h3></div>'; return; }
    const progress = data.progress || 0;
    const barColor = progress >= 80 ? 'green' : (progress >= 40 ? 'blue' : 'gold');
    let html = '<div class="stats-row">' +
        '<div class="stat-card"><div class="stat-label">Overall Progress</div><div class="stat-value" style="color:#4ade80;">' + progress + '%</div></div>' +
        '<div class="stat-card"><div class="stat-label">Phase</div><div class="stat-value" style="color:var(--tf-blue);font-size:16px;">' + (data.current_phase || 'N/A') + '</div></div>' +
        '<div class="stat-card"><div class="stat-label">Est. Completion</div><div class="stat-value" style="color:var(--tf-gold);font-size:16px;">' + (data.est_completion || 'TBD') + '</div></div>' +
        '<div class="stat-card"><div class="stat-label">Open Items</div><div class="stat-value" style="color:var(--tf-text);">' + (data.open_items ? data.open_items.length : 0) + '</div></div>' +
        '</div>';
    html += '<div class="card" style="margin-bottom:20px;"><h3>Project Progress</h3>' +
        '<div class="progress-bar-lg"><div class="progress-fill ' + barColor + '" style="width:' + progress + '%;"></div></div>' +
        '<div style="display:flex;justify-content:space-between;font-size:12px;color:var(--tf-muted);"><span>Started: ' + (data.start_date || '--') + '</span><span>Target: ' + (data.est_completion || '--') + '</span></div></div>';

    html += '<div class="two-col">';
    // Milestones
    html += '<div class="card"><h3>Milestones</h3><ul class="milestone-list">';
    const milestones = data.milestones || [
        { name: 'Quote Approved', status: 'done', date: '' },
        { name: 'Shop Drawings Approved', status: 'done', date: '' },
        { name: 'Fabrication Complete', status: 'active', date: '' },
        { name: 'Shipping', status: 'upcoming', date: '' },
        { name: 'Installation', status: 'upcoming', date: '' }
    ];
    milestones.forEach(m => {
        html += '<li class="milestone-item"><div class="milestone-dot ' + m.status + '"></div>' +
            '<span class="milestone-text ' + (m.status==='done'?'done':'') + '">' + m.name + '</span>' +
            '<span class="milestone-date">' + (m.date || '') + '</span></li>';
    });
    html += '</ul></div>';

    // Deliveries
    html += '<div class="card"><h3>Upcoming Deliveries</h3>';
    const deliveries = data.deliveries || [];
    if (deliveries.length) {
        deliveries.forEach(d => {
            html += '<div class="delivery-item"><div class="delivery-info">' + (d.description || 'Delivery') +
                '<small>' + (d.carrier || '') + '</small></div><span class="badge badge-blue">' + (d.date || 'TBD') + '</span></div>';
        });
    } else { html += '<div style="color:var(--tf-muted);font-size:13px;padding:12px 0;">No upcoming deliveries scheduled.</div>'; }
    html += '</div></div>';

    // Open items and contacts
    html += '<div class="two-col" style="margin-top:20px;">';
    html += '<div class="card"><h3>Open Items</h3>';
    const items = data.open_items || [];
    if (items.length) {
        items.forEach(it => {
            html += '<div class="open-item"><span class="open-num">#' + (it.id || '--') + '</span><span>' + (it.description || '') + '</span></div>';
        });
    } else { html += '<div style="color:var(--tf-muted);font-size:13px;padding:12px 0;">No open items. All clear!</div>'; }
    html += '</div>';

    html += '<div class="card"><h3>Your Contacts</h3>';
    const contacts = data.contacts || [{ name: 'Project Manager', role: 'PM', email: '' }];
    contacts.forEach(c => {
        const init = (c.name||'?').split(' ').map(w=>w[0]).join('').substring(0,2).toUpperCase();
        html += '<div class="contact-row"><div class="contact-avatar">' + init + '</div><div class="contact-info">' + c.name + '<small>' + (c.role||'') + ' &bull; ' + (c.email||'') + '</small></div></div>';
    });
    html += '</div></div>';

    el.innerHTML = html;
}

async function loadProjects() {
    try {
        const resp = await fetch('/api/projects/full');
        const data = await resp.json();
        const projects = Array.isArray(data) ? data : (data.projects || []);
        const sel = document.getElementById('projectSelect');
        projects.forEach(p => {
            const o = document.createElement('option');
            o.value = p.id || p.job_code || '';
            o.textContent = (p.job_code || '') + ' - ' + (p.project_name || p.name || 'Unnamed');
            sel.appendChild(o);
        });
    } catch(e) {}
}

async function loadProjectStatus() {
    const id = document.getElementById('projectSelect').value;
    if (!id) { document.getElementById('statusContent').innerHTML = '<div class="empty-state"><h3>Select a project</h3><p>Choose a project from the dropdown to view its status.</p></div>'; return; }
    try {
        const resp = await fetch('/api/portal/status/' + encodeURIComponent(id));
        projectData = await resp.json();
        renderStatus(projectData);
    } catch(e) {
        renderStatus({ progress: 0, current_phase: 'Unknown' });
    }
}

function refreshStatus() { loadProjectStatus(); }

loadProjects();
</script>
"""
