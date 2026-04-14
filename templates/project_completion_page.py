"""
TitanForge v4 — Project Completion Dashboard
===============================================
Cross-project view of completion metrics: percentage complete,
punch list health, close-out readiness. PM-focused dashboard
showing which projects are ready to close and which need attention.
"""
from templates.shared_styles import DESIGN_SYSTEM_CSS

PROJECT_COMPLETION_PAGE_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TitanForge — Project Completion</title>
    <style>
""" + DESIGN_SYSTEM_CSS + r"""

        .container { max-width: 1400px; margin: 0 auto; padding: var(--tf-sp-6) var(--tf-sp-8); }

        .top-bar {
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: var(--tf-sp-6);
        }
        .top-bar h1 { font-size: var(--tf-text-xl); font-weight: 800; margin: 0; }

        /* Summary cards */
        .summary-row { display: grid; grid-template-columns: repeat(5, 1fr); gap: var(--tf-sp-4); margin-bottom: var(--tf-sp-6); }
        .summary-card {
            background: var(--tf-surface); border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-lg); padding: var(--tf-sp-5); text-align: center;
        }
        .summary-card .val { font-size: var(--tf-text-2xl); font-weight: 800; color: var(--tf-gray-900); }
        .summary-card .lbl { font-size: var(--tf-text-xs); color: var(--tf-gray-500); text-transform: uppercase; letter-spacing: 0.04em; margin-top: 2px; }
        .summary-card.green { border-left: 4px solid var(--tf-success); }
        .summary-card.purple { border-left: 4px solid #8b5cf6; }
        .summary-card.red { border-left: 4px solid var(--tf-danger); }
        .summary-card.blue { border-left: 4px solid var(--tf-blue); }
        .summary-card.amber { border-left: 4px solid var(--tf-amber); }

        /* Project cards */
        .projects-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); gap: var(--tf-sp-4); }
        .project-card {
            background: var(--tf-surface); border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-lg); overflow: hidden;
            transition: box-shadow 0.15s;
        }
        .project-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
        .project-card-header {
            padding: var(--tf-sp-4) var(--tf-sp-5);
            display: flex; justify-content: space-between; align-items: center;
            border-bottom: 1px solid var(--tf-border);
        }
        .project-card-header .job { font-weight: 800; font-size: var(--tf-text-md); color: var(--tf-gray-900); }
        .project-card-header .pct {
            font-size: var(--tf-text-lg); font-weight: 800;
        }
        .pct.high { color: #059669; }
        .pct.mid { color: var(--tf-amber); }
        .pct.low { color: var(--tf-gray-500); }

        .project-card-body { padding: var(--tf-sp-4) var(--tf-sp-5); }

        /* Mini progress bar */
        .mini-progress {
            height: 8px; background: var(--tf-gray-100); border-radius: 4px;
            overflow: hidden; margin-bottom: var(--tf-sp-3);
        }
        .mini-progress .fill {
            height: 100%; border-radius: 4px; transition: width 0.4s ease;
        }
        .mini-progress .fill.green { background: #059669; }
        .mini-progress .fill.amber { background: var(--tf-amber); }
        .mini-progress .fill.gray { background: var(--tf-gray-400); }

        /* Stat row inside card */
        .card-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--tf-sp-2); margin-bottom: var(--tf-sp-3); }
        .card-stat { text-align: center; }
        .card-stat .v { font-size: var(--tf-text-md); font-weight: 700; }
        .card-stat .l { font-size: 10px; color: var(--tf-gray-500); text-transform: uppercase; }

        /* Punch badge */
        .punch-row {
            display: flex; justify-content: space-between; align-items: center;
            padding: var(--tf-sp-2) 0; font-size: var(--tf-text-sm);
        }
        .punch-badge {
            display: inline-flex; align-items: center; gap: 4px;
            padding: 2px 8px; border-radius: 999px; font-size: 11px; font-weight: 600;
        }
        .punch-badge.danger { background: #fee2e2; color: #991b1b; }
        .punch-badge.warning { background: #fef3c7; color: #92400e; }
        .punch-badge.ok { background: #d1fae5; color: #065f46; }

        /* Close-out badge */
        .closeout-badge {
            display: inline-block; padding: 3px 10px; border-radius: 999px;
            font-size: 11px; font-weight: 700;
        }
        .closeout-badge.ready { background: #d1fae5; color: #065f46; }
        .closeout-badge.not-ready { background: #fee2e2; color: #991b1b; }
        .closeout-badge.in-progress { background: #fef3c7; color: #92400e; }

        .card-actions {
            display: flex; gap: var(--tf-sp-2); margin-top: var(--tf-sp-3);
            padding-top: var(--tf-sp-3); border-top: 1px solid var(--tf-gray-100);
        }
        .card-actions a {
            font-size: 12px; font-weight: 600; color: var(--tf-blue);
            text-decoration: none;
        }
        .card-actions a:hover { text-decoration: underline; }

        .empty-state { text-align: center; padding: var(--tf-sp-8); color: var(--tf-gray-400); }

        @media (max-width: 900px) {
            .summary-row { grid-template-columns: repeat(3, 1fr); }
            .projects-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="top-bar">
            <h1>Project Completion</h1>
            <div style="display:flex;gap:var(--tf-sp-3);">
                <a href="/field" class="btn btn-secondary">Field Ops</a>
                <a href="/field/install-tracker" class="btn btn-secondary">Install Tracker</a>
                <button onclick="loadDashboard()" class="btn btn-primary">Refresh</button>
            </div>
        </div>

        <!-- Summary cards -->
        <div class="summary-row" id="summaryRow">
            <div class="summary-card blue"><div class="val" id="sumProjects">—</div><div class="lbl">Active Projects</div></div>
            <div class="summary-card green"><div class="val" id="sumInstalled">—</div><div class="lbl">Items Installed</div></div>
            <div class="summary-card purple"><div class="val" id="sumDelivered">—</div><div class="lbl">Items Delivered</div></div>
            <div class="summary-card red"><div class="val" id="sumPunches">—</div><div class="lbl">Open Punch Items</div></div>
            <div class="summary-card amber"><div class="val" id="sumCompletion">—</div><div class="lbl">Overall Completion</div></div>
        </div>

        <!-- Project cards -->
        <div class="projects-grid" id="projectsGrid">
            <div class="empty-state">Loading project data...</div>
        </div>
    </div>

    <script>
    async function loadDashboard() {
        try {
            const res = await fetch('/api/field/summary');
            const data = await res.json();
            if (!data.ok) return;

            const s = data.summary;
            document.getElementById('sumProjects').textContent = s.active_projects || 0;
            document.getElementById('sumInstalled').textContent = s.total_installed || 0;
            document.getElementById('sumDelivered').textContent = s.total_delivered || 0;
            document.getElementById('sumPunches').textContent = s.total_open_punches || 0;
            document.getElementById('sumCompletion').textContent = (s.overall_completion_pct || 0) + '%';

            renderProjects(s.projects || []);
        } catch (e) {
            document.getElementById('projectsGrid').innerHTML =
                '<div class="empty-state">Failed to load project data</div>';
        }
    }

    function renderProjects(projects) {
        const grid = document.getElementById('projectsGrid');
        if (!projects.length) {
            grid.innerHTML = '<div class="empty-state">No projects with field activity yet</div>';
            return;
        }

        // Sort: incomplete first (by completion %), then complete
        projects.sort((a, b) => {
            if (a.can_close && !b.can_close) return 1;
            if (!a.can_close && b.can_close) return -1;
            return (b.completion_pct || 0) - (a.completion_pct || 0);
        });

        grid.innerHTML = projects.map(p => {
            const pct = p.completion_pct || 0;
            const pctClass = pct >= 90 ? 'high' : pct >= 50 ? 'mid' : 'low';
            const barClass = pct >= 90 ? 'green' : pct >= 50 ? 'amber' : 'gray';

            let closeoutHtml = '';
            if (p.can_close) {
                closeoutHtml = '<span class="closeout-badge ready">Ready to Close</span>';
            } else if (pct >= 80) {
                closeoutHtml = '<span class="closeout-badge in-progress">Nearing Completion</span>';
            } else {
                closeoutHtml = '<span class="closeout-badge not-ready">In Progress</span>';
            }

            let punchHtml = '';
            if (p.critical_punches > 0) {
                punchHtml = `<span class="punch-badge danger">${p.critical_punches} Critical</span>`;
            } else if (p.open_punches > 0) {
                punchHtml = `<span class="punch-badge warning">${p.open_punches} Open</span>`;
            } else {
                punchHtml = '<span class="punch-badge ok">Clear</span>';
            }

            return `<div class="project-card">
                <div class="project-card-header">
                    <span class="job">${p.job_code}</span>
                    <span class="pct ${pctClass}">${pct}%</span>
                </div>
                <div class="project-card-body">
                    <div class="mini-progress"><div class="fill ${barClass}" style="width:${pct}%"></div></div>
                    <div class="card-stats">
                        <div class="card-stat"><div class="v">${p.total_items || 0}</div><div class="l">Total</div></div>
                        <div class="card-stat"><div class="v">${p.installed_count || 0}</div><div class="l">Installed</div></div>
                        <div class="card-stat"><div class="v">${p.delivered_count || 0}</div><div class="l">Delivered</div></div>
                    </div>
                    <div class="punch-row">
                        <span>Punch List</span> ${punchHtml}
                    </div>
                    <div class="punch-row">
                        <span>Close-out</span> ${closeoutHtml}
                    </div>
                    <div class="punch-row" style="font-size:12px;color:var(--tf-gray-400);">
                        ${p.daily_reports_count || 0} daily reports · ${p.total_work_orders || 0} work orders
                    </div>
                    <div class="card-actions">
                        <a href="/field/install-tracker?project=${p.job_code}">Install Tracker</a>
                        <a href="/field?project=${p.job_code}">Field Ops</a>
                    </div>
                </div>
            </div>`;
        }).join('');
    }

    loadDashboard();
    setInterval(loadDashboard, 60000);
    </script>
</body>
</html>
"""
