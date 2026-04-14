"""
TitanForge v4 — Installation Tracker
======================================
Visual tracker for per-item installation status across a project.
Color-coded grid view showing which items are delivered, installed,
or have punch items. Links to field ops page for actions.
"""
from templates.shared_styles import DESIGN_SYSTEM_CSS

INSTALL_TRACKER_PAGE_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TitanForge — Installation Tracker</title>
    <style>
""" + DESIGN_SYSTEM_CSS + r"""

        .container { max-width: 1200px; margin: 0 auto; padding: var(--tf-sp-6) var(--tf-sp-8); }

        .top-bar {
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: var(--tf-sp-5);
        }
        .top-bar h1 { font-size: var(--tf-text-xl); font-weight: 800; margin: 0; }
        .top-bar .actions { display: flex; gap: var(--tf-sp-3); align-items: center; }

        /* Project selector */
        .project-select {
            padding: var(--tf-sp-2) var(--tf-sp-3); border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-md); font-size: var(--tf-text-sm); min-width: 200px;
        }

        /* Progress bar */
        .progress-section { margin-bottom: var(--tf-sp-6); }
        .progress-header { display: flex; justify-content: space-between; margin-bottom: var(--tf-sp-2); }
        .progress-header .pct { font-size: var(--tf-text-2xl); font-weight: 800; }
        .progress-header .detail { font-size: var(--tf-text-sm); color: var(--tf-gray-500); }
        .progress-bar {
            height: 24px; background: var(--tf-gray-100); border-radius: var(--tf-radius-md);
            overflow: hidden; display: flex;
        }
        .progress-bar .seg {
            height: 100%; transition: width 0.4s ease; display: flex;
            align-items: center; justify-content: center;
            font-size: 10px; font-weight: 700; color: white; min-width: 20px;
        }
        .seg-installed { background: #059669; }
        .seg-delivered { background: #8b5cf6; }
        .seg-shipped { background: var(--tf-blue); }
        .seg-fab { background: var(--tf-amber); }
        .seg-other { background: var(--tf-gray-300); }

        .progress-legend {
            display: flex; gap: var(--tf-sp-5); margin-top: var(--tf-sp-2);
            font-size: var(--tf-text-xs); color: var(--tf-gray-500);
        }
        .progress-legend .dot {
            display: inline-block; width: 10px; height: 10px;
            border-radius: 50%; margin-right: 4px; vertical-align: middle;
        }

        /* Status grid */
        .grid-section { margin-bottom: var(--tf-sp-6); }
        .grid-section h2 {
            font-size: var(--tf-text-md); font-weight: 700; margin-bottom: var(--tf-sp-3);
            padding-bottom: var(--tf-sp-2); border-bottom: 1px solid var(--tf-border);
        }
        .item-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: var(--tf-sp-2); }
        .item-tile {
            border: 1px solid var(--tf-border); border-radius: var(--tf-radius-md);
            padding: var(--tf-sp-2) var(--tf-sp-3); text-align: center;
            font-size: var(--tf-text-sm); cursor: pointer; transition: all 0.15s;
            position: relative;
        }
        .item-tile:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .item-tile .mark { font-weight: 700; }
        .item-tile .sub { font-size: 10px; color: var(--tf-gray-500); }

        .item-tile.installed { background: #d1fae5; border-color: #059669; }
        .item-tile.delivered { background: #ede9fe; border-color: #8b5cf6; }
        .item-tile.shipped { background: #dbeafe; border-color: var(--tf-blue); }
        .item-tile.ready_to_ship { background: #e0f2fe; border-color: #0ea5e9; }
        .item-tile.qc_approved { background: #ecfdf5; border-color: #10b981; }
        .item-tile.in_progress { background: #fef3c7; border-color: var(--tf-amber); }
        .item-tile.other { background: var(--tf-gray-50); }

        .item-tile .punch-badge {
            position: absolute; top: -4px; right: -4px;
            width: 16px; height: 16px; border-radius: 50%;
            background: #dc2626; color: white; font-size: 9px;
            font-weight: 700; display: flex; align-items: center;
            justify-content: center;
        }

        /* Panel (recent activity, punch summary) */
        .dashboard-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--tf-sp-6); }
        .panel {
            background: var(--tf-surface); border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-lg); overflow: hidden;
        }
        .panel-header {
            padding: var(--tf-sp-3) var(--tf-sp-4); border-bottom: 1px solid var(--tf-border);
            font-weight: 700; font-size: var(--tf-text-sm); background: var(--tf-gray-50);
        }
        .panel-body { padding: var(--tf-sp-4); max-height: 300px; overflow-y: auto; }

        .activity-item { padding: 6px 0; border-bottom: 1px solid var(--tf-gray-100); font-size: var(--tf-text-sm); }
        .activity-item:last-child { border-bottom: none; }
        .activity-item .ts { font-size: 11px; color: var(--tf-gray-400); }

        .empty-state { text-align: center; padding: var(--tf-sp-6); color: var(--tf-gray-400); font-size: var(--tf-text-sm); }

        @media (max-width: 900px) {
            .dashboard-grid { grid-template-columns: 1fr; }
            .item-grid { grid-template-columns: repeat(auto-fill, minmax(90px, 1fr)); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="top-bar">
            <h1>Installation Tracker</h1>
            <div class="actions">
                <select class="project-select" id="projectSelect" onchange="onProjectChange()">
                    <option value="">Select Project...</option>
                </select>
                <a href="/field" class="btn btn-secondary">Field Ops</a>
                <a href="/field/completion" class="btn btn-secondary">Completion</a>
            </div>
        </div>

        <!-- Progress bar -->
        <div class="progress-section">
            <div class="progress-header">
                <div>
                    <span class="pct" id="completionPct">0%</span>
                    <span class="detail" id="completionDetail">— / — items installed</span>
                </div>
            </div>
            <div class="progress-bar" id="progressBar"></div>
            <div class="progress-legend">
                <span><span class="dot" style="background:#059669"></span> Installed</span>
                <span><span class="dot" style="background:#8b5cf6"></span> Delivered</span>
                <span><span class="dot" style="background:var(--tf-blue)"></span> Shipped</span>
                <span><span class="dot" style="background:var(--tf-amber)"></span> Fabrication</span>
                <span><span class="dot" style="background:var(--tf-gray-300)"></span> Other</span>
            </div>
        </div>

        <!-- Item grid -->
        <div class="grid-section" id="gridSection">
            <div class="empty-state">Select a project to view installation status</div>
        </div>

        <!-- Bottom panels -->
        <div class="dashboard-grid">
            <div class="panel">
                <div class="panel-header">Recent Installations</div>
                <div class="panel-body" id="recentInstalls">
                    <div class="empty-state">No installations recorded</div>
                </div>
            </div>
            <div class="panel">
                <div class="panel-header">Punch List Summary</div>
                <div class="panel-body" id="punchSummary">
                    <div class="empty-state">No punch items</div>
                </div>
            </div>
        </div>
    </div>

    <script>
    let currentProject = '';
    let completionData = {};

    async function loadProjects() {
        try {
            const res = await fetch('/api/field/summary');
            const data = await res.json();
            if (!data.ok) return;
            const sel = document.getElementById('projectSelect');
            sel.innerHTML = '<option value="">Select Project...</option>';
            (data.summary.projects || []).forEach(p => {
                sel.innerHTML += `<option value="${p.job_code}">${p.job_code} (${p.completion_pct}%)</option>`;
            });
        } catch (e) {}
    }

    function onProjectChange() {
        currentProject = document.getElementById('projectSelect').value;
        if (currentProject) loadProjectData();
    }

    async function loadProjectData() {
        const [compRes, punchRes, installRes] = await Promise.all([
            fetch(`/api/field/project-completion?job_code=${currentProject}`),
            fetch(`/api/field/punch-list?job_code=${currentProject}`),
            fetch(`/api/field/installations?job_code=${currentProject}`),
        ]);
        const comp = await compRes.json();
        const punches = await punchRes.json();
        const installs = await installRes.json();

        if (comp.ok) {
            completionData = comp.completion;
            renderProgress();
            renderGrid();
        }
        if (punches.ok) renderPunchSummary(punches.items);
        if (installs.ok) renderRecentInstalls(installs.records);
    }

    function renderProgress() {
        const c = completionData;
        const total = c.total_items || 1;
        document.getElementById('completionPct').textContent = c.completion_pct + '%';
        document.getElementById('completionDetail').textContent =
            `${c.installed_count} / ${c.total_items} items installed`;

        const phases = c.phase_counts || {};
        const segments = [
            { cls: 'seg-installed', count: phases.installed || 0 },
            { cls: 'seg-delivered', count: c.delivered_count || 0 },
            { cls: 'seg-shipped', count: c.shipped_count || 0 },
            { cls: 'seg-fab', count: (phases.fabrication || 0) + (phases.qc || 0) },
            { cls: 'seg-other', count: phases.prefab || 0 },
        ];
        const bar = document.getElementById('progressBar');
        bar.innerHTML = segments.filter(s => s.count > 0).map(s => {
            const pct = Math.max((s.count / total) * 100, 3);
            return `<div class="seg ${s.cls}" style="width:${pct}%">${s.count}</div>`;
        }).join('');
    }

    function renderGrid() {
        const c = completionData;
        const counts = c.status_counts || {};
        const section = document.getElementById('gridSection');

        // We need to fetch actual items — use the completion data to show status distribution
        // For now, show a summary grid grouped by status
        let html = '<h2>Items by Status</h2>';
        const statusOrder = ['installed', 'delivered', 'shipped', 'ready_to_ship', 'qc_approved',
                            'qc_pending', 'fabricated', 'in_progress', 'staged', 'approved', 'queued'];
        const statusLabels = {
            installed: 'Installed', delivered: 'Delivered', shipped: 'Shipped',
            ready_to_ship: 'Ready to Ship', qc_approved: 'QC Approved', qc_pending: 'QC Pending',
            fabricated: 'Fabricated', in_progress: 'In Progress', staged: 'Staged',
            approved: 'Approved', queued: 'Queued', qc_rejected: 'QC Rejected', on_hold: 'On Hold'
        };

        const hasItems = Object.values(counts).some(v => v > 0);
        if (!hasItems) {
            section.innerHTML = '<div class="empty-state">No work order items in this project</div>';
            return;
        }

        html += '<div class="item-grid">';
        statusOrder.forEach(status => {
            const count = counts[status] || 0;
            if (count > 0) {
                const cls = ['installed','delivered','shipped','ready_to_ship','qc_approved','in_progress'].includes(status) ? status : 'other';
                html += `<div class="item-tile ${cls}">
                    <div class="mark">${count}</div>
                    <div class="sub">${statusLabels[status] || status}</div>
                </div>`;
            }
        });
        // Also show any remaining statuses
        Object.entries(counts).forEach(([status, count]) => {
            if (!statusOrder.includes(status) && count > 0) {
                html += `<div class="item-tile other">
                    <div class="mark">${count}</div>
                    <div class="sub">${statusLabels[status] || status}</div>
                </div>`;
            }
        });
        html += '</div>';

        section.innerHTML = html;
    }

    function renderRecentInstalls(records) {
        const container = document.getElementById('recentInstalls');
        if (!records || !records.length) {
            container.innerHTML = '<div class="empty-state">No installations recorded</div>';
            return;
        }
        container.innerHTML = records.slice(0, 15).map(r =>
            `<div class="activity-item">
                <strong>${r.ship_mark || r.item_id}</strong> installed by ${r.installed_by}
                ${r.location ? ' at ' + r.location : ''}
                <div class="ts">${r.installed_at ? new Date(r.installed_at).toLocaleString() : ''}</div>
            </div>`
        ).join('');
    }

    function renderPunchSummary(items) {
        const container = document.getElementById('punchSummary');
        if (!items || !items.length) {
            container.innerHTML = '<div class="empty-state">No punch items</div>';
            return;
        }
        const byStat = {};
        items.forEach(p => { byStat[p.status] = (byStat[p.status] || 0) + 1; });
        const byPri = {};
        items.filter(p => !['verified'].includes(p.status)).forEach(p => {
            byPri[p.priority] = (byPri[p.priority] || 0) + 1;
        });

        let html = '<div style="margin-bottom:12px;">';
        Object.entries(byStat).forEach(([status, count]) => {
            html += `<div style="display:flex;justify-content:space-between;padding:4px 0;font-size:13px;">
                <span style="text-transform:capitalize;">${status.replace('_',' ')}</span>
                <strong>${count}</strong>
            </div>`;
        });
        html += '</div>';
        if (Object.keys(byPri).length > 0) {
            html += '<div style="border-top:1px solid var(--tf-gray-100);padding-top:8px;font-size:12px;color:var(--tf-gray-500);">';
            html += 'Active by priority: ';
            html += Object.entries(byPri).map(([p, c]) => `${p}: ${c}`).join(', ');
            html += '</div>';
        }
        container.innerHTML = html;
    }

    loadProjects();
    </script>
</body>
</html>
"""
