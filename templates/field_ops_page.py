"""
TitanForge v4 — Field Operations Dashboard
=============================================
Mobile-friendly field crew workspace: punch list, daily reports,
installation confirmations, delivered items queue. Designed for
phone/tablet use on the job site.
"""
from templates.shared_styles import DESIGN_SYSTEM_CSS

FIELD_OPS_PAGE_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TitanForge — Field Operations</title>
    <style>
""" + DESIGN_SYSTEM_CSS + r"""

        .container { max-width: 800px; margin: 0 auto; padding: var(--tf-sp-4); }

        /* Mobile-first: bigger touch targets, larger text */
        .top-bar {
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: var(--tf-sp-4);
        }
        .top-bar h1 { font-size: var(--tf-text-lg); font-weight: 800; margin: 0; }

        /* Project selector */
        .project-selector {
            width: 100%; padding: var(--tf-sp-3); border: 2px solid var(--tf-blue);
            border-radius: var(--tf-radius-md); font-size: var(--tf-text-md);
            font-weight: 600; background: var(--tf-surface); margin-bottom: var(--tf-sp-4);
        }

        /* Quick action cards */
        .action-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--tf-sp-3); margin-bottom: var(--tf-sp-5); }
        .action-card {
            background: var(--tf-surface); border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-lg); padding: var(--tf-sp-4);
            text-align: center; cursor: pointer; transition: all 0.15s;
            min-height: 80px; display: flex; flex-direction: column;
            align-items: center; justify-content: center;
        }
        .action-card:active { transform: scale(0.97); }
        .action-card .icon { font-size: 28px; margin-bottom: 4px; }
        .action-card .label { font-size: var(--tf-text-sm); font-weight: 600; color: var(--tf-gray-700); }
        .action-card .count { font-size: 11px; color: var(--tf-gray-400); margin-top: 2px; }
        .action-card.punch { border-left: 4px solid var(--tf-danger); }
        .action-card.install { border-left: 4px solid var(--tf-success); }
        .action-card.report { border-left: 4px solid var(--tf-blue); }
        .action-card.tracker { border-left: 4px solid #8b5cf6; }

        /* Stats strip */
        .stats-strip {
            display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--tf-sp-2);
            margin-bottom: var(--tf-sp-5);
        }
        .stat-box {
            background: var(--tf-surface); border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-md); padding: var(--tf-sp-3); text-align: center;
        }
        .stat-box .val { font-size: var(--tf-text-lg); font-weight: 800; color: var(--tf-gray-900); }
        .stat-box .lbl { font-size: 10px; color: var(--tf-gray-500); text-transform: uppercase; letter-spacing: 0.04em; }

        /* Tab bar */
        .tab-bar {
            display: flex; border-bottom: 2px solid var(--tf-border);
            margin-bottom: var(--tf-sp-4); overflow-x: auto;
        }
        .tab-bar button {
            padding: var(--tf-sp-3) var(--tf-sp-4); border: none; background: none;
            font-size: var(--tf-text-sm); font-weight: 600; color: var(--tf-gray-500);
            cursor: pointer; white-space: nowrap; border-bottom: 3px solid transparent;
            margin-bottom: -2px;
        }
        .tab-bar button.active { color: var(--tf-blue); border-bottom-color: var(--tf-blue); }

        /* Tab content */
        .tab-content { display: none; }
        .tab-content.active { display: block; }

        /* Punch list cards */
        .punch-card {
            background: var(--tf-surface); border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-md); padding: var(--tf-sp-3) var(--tf-sp-4);
            margin-bottom: var(--tf-sp-3); position: relative;
        }
        .punch-card .priority-dot {
            width: 10px; height: 10px; border-radius: 50%;
            position: absolute; top: 14px; left: 10px;
        }
        .punch-card .priority-dot.critical { background: #dc2626; }
        .punch-card .priority-dot.high { background: #f59e0b; }
        .punch-card .priority-dot.medium { background: var(--tf-blue); }
        .punch-card .priority-dot.low { background: var(--tf-gray-400); }
        .punch-card .punch-title { font-weight: 700; font-size: var(--tf-text-sm); padding-left: 16px; }
        .punch-card .punch-meta { font-size: 11px; color: var(--tf-gray-500); padding-left: 16px; margin-top: 2px; }

        /* Status pill */
        .status-pill {
            display: inline-block; padding: 2px 8px; border-radius: 999px;
            font-size: 10px; font-weight: 600; text-transform: capitalize;
        }
        .status-pill.open { background: #fee2e2; color: #991b1b; }
        .status-pill.in_progress { background: #fef3c7; color: #92400e; }
        .status-pill.resolved { background: #dbeafe; color: #1e40af; }
        .status-pill.verified { background: #d1fae5; color: #065f46; }
        .status-pill.deferred { background: var(--tf-gray-100); color: var(--tf-gray-600); }

        /* Delivered items list */
        .delivered-item {
            display: flex; justify-content: space-between; align-items: center;
            padding: var(--tf-sp-3); border-bottom: 1px solid var(--tf-gray-100);
        }
        .delivered-item .item-info { flex: 1; }
        .delivered-item .item-mark { font-weight: 700; font-size: var(--tf-text-sm); }
        .delivered-item .item-desc { font-size: 12px; color: var(--tf-gray-500); }
        .delivered-item .confirm-btn {
            padding: var(--tf-sp-2) var(--tf-sp-3); background: var(--tf-success);
            color: white; border: none; border-radius: var(--tf-radius-md);
            font-weight: 600; font-size: 12px; cursor: pointer;
        }

        /* Daily report cards */
        .report-card {
            background: var(--tf-surface); border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-md); padding: var(--tf-sp-3) var(--tf-sp-4);
            margin-bottom: var(--tf-sp-3);
        }
        .report-card .date { font-weight: 700; font-size: var(--tf-text-sm); }
        .report-card .crew-info { font-size: 12px; color: var(--tf-gray-500); margin-top: 2px; }
        .report-card .summary { font-size: var(--tf-text-sm); margin-top: var(--tf-sp-2); color: var(--tf-gray-700); }

        /* Modals */
        .modal-backdrop {
            display: none; position: fixed; inset: 0;
            background: rgba(0,0,0,0.4); z-index: 1000;
            justify-content: center; align-items: flex-end;
        }
        .modal-backdrop.active { display: flex; }
        .modal {
            background: var(--tf-surface); border-radius: var(--tf-radius-lg) var(--tf-radius-lg) 0 0;
            width: 100%; max-width: 600px; max-height: 85vh; overflow-y: auto;
            box-shadow: 0 -10px 40px rgba(0,0,0,0.2); padding: var(--tf-sp-5);
        }
        .modal h2 { font-size: var(--tf-text-lg); font-weight: 700; margin: 0 0 var(--tf-sp-4) 0; }
        .form-group { margin-bottom: var(--tf-sp-3); }
        .form-group label { display: block; font-size: 12px; font-weight: 600; color: var(--tf-gray-600); margin-bottom: 4px; }
        .form-group input, .form-group select, .form-group textarea {
            width: 100%; padding: var(--tf-sp-2) var(--tf-sp-3);
            border: 1px solid var(--tf-border); border-radius: var(--tf-radius-md);
            font-size: var(--tf-text-sm);
        }
        .form-group textarea { min-height: 80px; resize: vertical; }
        .form-actions { display: flex; gap: var(--tf-sp-3); margin-top: var(--tf-sp-4); }
        .form-actions .btn { flex: 1; padding: var(--tf-sp-3); font-weight: 600; }

        /* Toast */
        .toast { position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%); background: var(--tf-gray-900); color: white; padding: 12px 20px; border-radius: var(--tf-radius-md); font-size: var(--tf-text-sm); z-index: 2000; display: none; }
        .toast.success { background: var(--tf-success); }
        .toast.error { background: var(--tf-danger); }

        @media (min-width: 768px) {
            .container { max-width: 900px; padding: var(--tf-sp-6); }
            .modal-backdrop { align-items: center; }
            .modal { border-radius: var(--tf-radius-lg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="top-bar">
            <h1>Field Operations</h1>
            <button onclick="refreshAll()" class="btn btn-secondary" style="font-size:12px;">Refresh</button>
        </div>

        <!-- Project selector -->
        <select class="project-selector" id="projectSelect" onchange="onProjectChange()">
            <option value="">Select a Project...</option>
        </select>

        <!-- Stats strip -->
        <div class="stats-strip" id="statsStrip">
            <div class="stat-box"><div class="val" id="statDelivered">—</div><div class="lbl">Delivered</div></div>
            <div class="stat-box"><div class="val" id="statInstalled">—</div><div class="lbl">Installed</div></div>
            <div class="stat-box"><div class="val" id="statPunchOpen">—</div><div class="lbl">Open Punch</div></div>
            <div class="stat-box"><div class="val" id="statCompletion">—</div><div class="lbl">Complete</div></div>
        </div>

        <!-- Quick actions -->
        <div class="action-grid">
            <div class="action-card punch" onclick="openPunchModal()">
                <div class="icon">&#128204;</div>
                <div class="label">New Punch Item</div>
            </div>
            <div class="action-card install" onclick="switchTab('install')">
                <div class="icon">&#9989;</div>
                <div class="label">Confirm Install</div>
                <div class="count" id="installableCount"></div>
            </div>
            <div class="action-card report" onclick="openReportModal()">
                <div class="icon">&#128221;</div>
                <div class="label">Daily Report</div>
            </div>
            <div class="action-card tracker" onclick="window.location='/field/install-tracker'">
                <div class="icon">&#128200;</div>
                <div class="label">Install Tracker</div>
            </div>
        </div>

        <!-- Tab bar -->
        <div class="tab-bar">
            <button class="active" onclick="switchTab('punch')">Punch List</button>
            <button onclick="switchTab('install')">Install Queue</button>
            <button onclick="switchTab('reports')">Daily Reports</button>
        </div>

        <!-- Punch list tab -->
        <div class="tab-content active" id="tab-punch">
            <div id="punchList"></div>
        </div>

        <!-- Install queue tab -->
        <div class="tab-content" id="tab-install">
            <div id="installQueue"></div>
        </div>

        <!-- Daily reports tab -->
        <div class="tab-content" id="tab-reports">
            <div id="reportsList"></div>
        </div>
    </div>

    <!-- Punch create modal -->
    <div class="modal-backdrop" id="punchModal">
        <div class="modal">
            <h2>New Punch Item</h2>
            <div class="form-group"><label>Title *</label><input id="punchTitle" placeholder="Short description of the issue"></div>
            <div class="form-group"><label>Priority</label>
                <select id="punchPriority"><option value="critical">Critical (Safety/Structural)</option><option value="high">High</option><option value="medium" selected>Medium</option><option value="low">Low (Cosmetic)</option></select>
            </div>
            <div class="form-group"><label>Category</label>
                <select id="punchCategory"><option value="missing_item">Missing Item</option><option value="damaged">Damaged</option><option value="wrong_item">Wrong Item</option><option value="fit_issue">Fit / Tolerance</option><option value="alignment">Alignment</option><option value="finish_defect">Finish Defect</option><option value="missing_hardware">Missing Hardware</option><option value="other" selected>Other</option></select>
            </div>
            <div class="form-group"><label>Location</label><input id="punchLocation" placeholder="Grid ref, bay, area..."></div>
            <div class="form-group"><label>Ship Mark (optional)</label><input id="punchShipMark" placeholder="e.g., C1, R3"></div>
            <div class="form-group"><label>Description</label><textarea id="punchDesc" placeholder="Detailed description..."></textarea></div>
            <div class="form-actions">
                <button class="btn btn-secondary" onclick="closePunchModal()">Cancel</button>
                <button class="btn btn-primary" onclick="submitPunch()">Create Punch Item</button>
            </div>
        </div>
    </div>

    <!-- Daily report modal -->
    <div class="modal-backdrop" id="reportModal">
        <div class="modal">
            <h2>Daily Field Report</h2>
            <div class="form-group"><label>Date</label><input type="date" id="reportDate"></div>
            <div class="form-group"><label>Crew Count</label><input type="number" id="reportCrewCount" min="0" value="0"></div>
            <div class="form-group"><label>Hours Worked</label><input type="number" id="reportHours" min="0" step="0.5" value="0"></div>
            <div class="form-group"><label>Weather</label>
                <select id="reportWeather"><option value="sunny">Sunny</option><option value="cloudy">Cloudy</option><option value="rain">Rain</option><option value="wind">High Wind</option><option value="snow">Snow</option><option value="extreme_heat">Extreme Heat</option></select>
            </div>
            <div class="form-group"><label>Work Summary *</label><textarea id="reportSummary" placeholder="What was accomplished today..."></textarea></div>
            <div class="form-group"><label>Delays</label><textarea id="reportDelays" placeholder="Any delays and reasons..." style="min-height:50px;"></textarea></div>
            <div class="form-group"><label>Issues</label><textarea id="reportIssues" placeholder="Problems encountered..." style="min-height:50px;"></textarea></div>
            <div class="form-actions">
                <button class="btn btn-secondary" onclick="closeReportModal()">Cancel</button>
                <button class="btn btn-primary" onclick="submitReport()">Submit Report</button>
            </div>
        </div>
    </div>

    <div class="toast" id="toast"></div>

    <script>
    let currentProject = '';
    let completionData = {};

    async function loadProjects() {
        try {
            const res = await fetch('/api/field/summary');
            const data = await res.json();
            if (!data.ok) return;
            const sel = document.getElementById('projectSelect');
            const projects = data.summary.projects || [];
            sel.innerHTML = '<option value="">Select a Project...</option>';
            projects.forEach(p => {
                sel.innerHTML += `<option value="${p.job_code}">${p.job_code} — ${p.completion_pct}% complete</option>`;
            });
            // Auto-select first project if available
            if (projects.length > 0 && !currentProject) {
                sel.value = projects[0].job_code;
                onProjectChange();
            }
        } catch (e) {}
    }

    function onProjectChange() {
        currentProject = document.getElementById('projectSelect').value;
        if (currentProject) refreshProjectData();
    }

    async function refreshProjectData() {
        if (!currentProject) return;
        await Promise.all([loadCompletion(), loadPunchList(), loadInstallQueue(), loadReports()]);
    }

    async function loadCompletion() {
        try {
            const res = await fetch(`/api/field/project-completion?job_code=${currentProject}`);
            const data = await res.json();
            if (data.ok) {
                completionData = data.completion;
                document.getElementById('statDelivered').textContent = completionData.delivered_count || 0;
                document.getElementById('statInstalled').textContent = completionData.installed_count || 0;
                document.getElementById('statPunchOpen').textContent = completionData.open_punches || 0;
                document.getElementById('statCompletion').textContent = (completionData.completion_pct || 0) + '%';
            }
        } catch (e) {}
    }

    async function loadPunchList() {
        try {
            const res = await fetch(`/api/field/punch-list?job_code=${currentProject}`);
            const data = await res.json();
            const container = document.getElementById('punchList');
            if (!data.ok || !data.items.length) {
                container.innerHTML = '<p style="text-align:center;color:var(--tf-gray-400);padding:20px;">No punch items</p>';
                return;
            }
            container.innerHTML = data.items.map(p => `<div class="punch-card">
                <div class="priority-dot ${p.priority}"></div>
                <div class="punch-title">${p.title} <span class="status-pill ${p.status}">${p.status.replace('_',' ')}</span></div>
                <div class="punch-meta">${p.category_label || p.category} · ${p.location || 'No location'} · ${p.created_by} · ${p.created_at ? new Date(p.created_at).toLocaleDateString() : ''}</div>
            </div>`).join('');
        } catch (e) {}
    }

    async function loadInstallQueue() {
        try {
            // Get delivered items from shipping that need install confirmation
            const res = await fetch(`/api/shipping/loads?status=delivered&job_code=${currentProject}`);
            const data = await res.json();
            const container = document.getElementById('installQueue');
            let deliveredItems = [];
            (data.loads || []).forEach(l => {
                (l.items || []).forEach(i => { deliveredItems.push({...i, load_id: l.load_id}); });
            });
            document.getElementById('installableCount').textContent = deliveredItems.length > 0 ? `${deliveredItems.length} pending` : '';
            if (!deliveredItems.length) {
                container.innerHTML = '<p style="text-align:center;color:var(--tf-gray-400);padding:20px;">No items awaiting installation</p>';
                return;
            }
            container.innerHTML = deliveredItems.map(i => `<div class="delivered-item">
                <div class="item-info">
                    <div class="item-mark">${i.ship_mark || i.item_id}</div>
                    <div class="item-desc">${i.description || '—'}</div>
                </div>
                <button class="confirm-btn" onclick="confirmInstall('${i.item_id}','${i.job_code || currentProject}')">Confirm Install</button>
            </div>`).join('');
        } catch (e) {
            document.getElementById('installQueue').innerHTML = '<p style="text-align:center;color:var(--tf-gray-400);padding:20px;">No items awaiting installation</p>';
        }
    }

    async function loadReports() {
        try {
            const res = await fetch(`/api/field/daily-reports?job_code=${currentProject}`);
            const data = await res.json();
            const container = document.getElementById('reportsList');
            if (!data.ok || !data.reports.length) {
                container.innerHTML = '<p style="text-align:center;color:var(--tf-gray-400);padding:20px;">No daily reports yet</p>';
                return;
            }
            container.innerHTML = data.reports.slice(0, 20).map(r => `<div class="report-card">
                <div class="date">${r.date} <span style="font-weight:400;color:var(--tf-gray-400);font-size:11px;">${r.submitted_by}</span></div>
                <div class="crew-info">${r.crew_count} crew · ${r.hours_worked}h · ${r.weather || 'N/A'}</div>
                <div class="summary">${r.work_summary || 'No summary'}</div>
            </div>`).join('');
        } catch (e) {}
    }

    function switchTab(tabId) {
        document.querySelectorAll('.tab-bar button').forEach((b, i) => {
            const tabs = ['punch', 'install', 'reports'];
            b.classList.toggle('active', tabs[i] === tabId);
        });
        document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
        document.getElementById(`tab-${tabId}`).classList.add('active');
    }

    function openPunchModal() { document.getElementById('punchModal').classList.add('active'); }
    function closePunchModal() { document.getElementById('punchModal').classList.remove('active'); }
    function openReportModal() {
        document.getElementById('reportDate').value = new Date().toISOString().slice(0,10);
        document.getElementById('reportModal').classList.add('active');
    }
    function closeReportModal() { document.getElementById('reportModal').classList.remove('active'); }

    async function submitPunch() {
        if (!currentProject) { showToast('Select a project first', 'error'); return; }
        const title = document.getElementById('punchTitle').value.trim();
        if (!title) { showToast('Title is required', 'error'); return; }
        try {
            const res = await fetch('/api/field/punch-list/create', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    job_code: currentProject, title,
                    priority: document.getElementById('punchPriority').value,
                    category: document.getElementById('punchCategory').value,
                    location: document.getElementById('punchLocation').value,
                    ship_mark: document.getElementById('punchShipMark').value,
                    description: document.getElementById('punchDesc').value,
                })
            });
            const data = await res.json();
            if (data.ok) {
                showToast('Punch item created', 'success');
                closePunchModal();
                document.getElementById('punchTitle').value = '';
                document.getElementById('punchDesc').value = '';
                loadPunchList(); loadCompletion();
            } else { showToast(data.error || 'Failed', 'error'); }
        } catch (e) { showToast('Error creating punch item', 'error'); }
    }

    async function confirmInstall(itemId, jobCode) {
        try {
            const res = await fetch('/api/field/confirm-install', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ job_code: jobCode, item_id: itemId })
            });
            const data = await res.json();
            if (data.ok) {
                showToast('Installation confirmed', 'success');
                refreshProjectData();
            } else { showToast(data.error || 'Failed', 'error'); }
        } catch (e) { showToast('Error confirming installation', 'error'); }
    }

    async function submitReport() {
        if (!currentProject) { showToast('Select a project first', 'error'); return; }
        const summary = document.getElementById('reportSummary').value.trim();
        if (!summary) { showToast('Work summary is required', 'error'); return; }
        try {
            const res = await fetch('/api/field/daily-report', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    job_code: currentProject,
                    date: document.getElementById('reportDate').value,
                    crew_count: parseInt(document.getElementById('reportCrewCount').value) || 0,
                    hours_worked: parseFloat(document.getElementById('reportHours').value) || 0,
                    weather: document.getElementById('reportWeather').value,
                    work_summary: summary,
                    delays: document.getElementById('reportDelays').value,
                    issues: document.getElementById('reportIssues').value,
                })
            });
            const data = await res.json();
            if (data.ok) {
                showToast('Daily report submitted', 'success');
                closeReportModal();
                loadReports();
            } else { showToast(data.error || 'Failed', 'error'); }
        } catch (e) { showToast('Error submitting report', 'error'); }
    }

    function showToast(msg, type) {
        const t = document.getElementById('toast');
        t.textContent = msg; t.className = 'toast ' + (type || '');
        t.style.display = 'block';
        setTimeout(() => { t.style.display = 'none'; }, 3500);
    }

    function refreshAll() { loadProjects(); if (currentProject) refreshProjectData(); }

    document.addEventListener('keydown', e => {
        if (e.key === 'Escape') { closePunchModal(); closeReportModal(); }
    });

    loadProjects();
    </script>
</body>
</html>
"""
