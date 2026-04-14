"""
TitanForge v4 — Executive Summary Dashboard
==============================================
C-suite / owner view of the entire operation: KPIs, shop floor status,
shipping pipeline, field progress, QC health — all in one page.
"""
from templates.shared_styles import DESIGN_SYSTEM_CSS

EXECUTIVE_SUMMARY_PAGE_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TitanForge — Executive Summary</title>
    <style>
""" + DESIGN_SYSTEM_CSS + r"""

        .container { max-width: 1400px; margin: 0 auto; padding: var(--tf-sp-6) var(--tf-sp-8); }

        .top-bar {
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: var(--tf-sp-6);
        }
        .top-bar h1 { font-size: var(--tf-text-xl); font-weight: 800; margin: 0; }
        .top-bar .actions { display: flex; gap: var(--tf-sp-3); align-items: center; }

        /* Hero KPI row */
        .hero-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--tf-sp-4); margin-bottom: var(--tf-sp-6); }
        .hero-card {
            background: var(--tf-surface); border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-lg); padding: var(--tf-sp-5);
            text-align: center; position: relative;
        }
        .hero-card .val { font-size: 36px; font-weight: 800; line-height: 1; }
        .hero-card .lbl { font-size: var(--tf-text-xs); color: var(--tf-gray-500); text-transform: uppercase; letter-spacing: 0.04em; margin-top: 4px; }
        .hero-card .sub { font-size: var(--tf-text-xs); color: var(--tf-gray-400); margin-top: 2px; }
        .hero-card.green .val { color: var(--tf-success); }
        .hero-card.blue .val { color: var(--tf-blue); }
        .hero-card.amber .val { color: var(--tf-amber); }
        .hero-card.red .val { color: var(--tf-danger); }

        /* Secondary KPIs */
        .kpi-row { display: grid; grid-template-columns: repeat(7, 1fr); gap: var(--tf-sp-3); margin-bottom: var(--tf-sp-6); }
        .kpi-card {
            background: var(--tf-surface); border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-md); padding: var(--tf-sp-3) var(--tf-sp-4); text-align: center;
        }
        .kpi-card .val { font-size: var(--tf-text-lg); font-weight: 800; color: var(--tf-gray-900); }
        .kpi-card .lbl { font-size: 10px; color: var(--tf-gray-500); text-transform: uppercase; }

        /* Sections grid */
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: var(--tf-sp-6); margin-bottom: var(--tf-sp-6); }
        .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: var(--tf-sp-6); margin-bottom: var(--tf-sp-6); }

        .panel {
            background: var(--tf-surface); border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-lg); overflow: hidden;
        }
        .panel-header {
            padding: var(--tf-sp-3) var(--tf-sp-5); border-bottom: 1px solid var(--tf-border);
            font-weight: 700; font-size: var(--tf-text-sm); background: var(--tf-gray-50);
            display: flex; justify-content: space-between; align-items: center;
        }
        .panel-header a { font-size: 12px; color: var(--tf-blue); text-decoration: none; }
        .panel-header a:hover { text-decoration: underline; }
        .panel-body { padding: var(--tf-sp-5); }

        /* Shipping pipeline */
        .pipeline-bar {
            height: 36px; border-radius: var(--tf-radius-md); overflow: hidden;
            display: flex; margin-bottom: var(--tf-sp-3);
        }
        .pipe-seg {
            height: 100%; display: flex; align-items: center; justify-content: center;
            font-size: 11px; font-weight: 700; color: white; min-width: 30px;
            transition: width 0.4s;
        }
        .pipe-seg.building { background: var(--tf-amber); }
        .pipe-seg.ready { background: var(--tf-blue); }
        .pipe-seg.transit { background: #8b5cf6; }
        .pipe-seg.delivered { background: var(--tf-success); }
        .pipe-seg.complete { background: #059669; }

        .pipe-legend {
            display: flex; gap: var(--tf-sp-4); font-size: var(--tf-text-xs); color: var(--tf-gray-500);
        }
        .pipe-legend .dot {
            display: inline-block; width: 10px; height: 10px;
            border-radius: 50%; margin-right: 4px; vertical-align: middle;
        }

        /* Machine mini-cards */
        .machine-mini-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--tf-sp-2); }
        .machine-mini {
            border: 1px solid var(--tf-border); border-radius: var(--tf-radius-sm);
            padding: var(--tf-sp-2); text-align: center; font-size: 12px;
        }
        .machine-mini .name { font-weight: 700; font-size: 11px; margin-bottom: 2px; }
        .machine-mini .active-dot {
            display: inline-block; width: 8px; height: 8px; border-radius: 50%;
            margin-right: 3px; vertical-align: middle;
        }

        /* Today strip */
        .today-strip {
            display: flex; gap: var(--tf-sp-6); padding: var(--tf-sp-3) var(--tf-sp-5);
            background: var(--tf-info-bg); border-radius: var(--tf-radius-md);
            font-size: var(--tf-text-sm); margin-bottom: var(--tf-sp-6);
            align-items: center;
        }
        .today-strip .label { font-weight: 700; color: var(--tf-info); }
        .today-strip .stat { color: var(--tf-gray-700); }
        .today-strip .stat strong { color: var(--tf-gray-900); }

        /* Status dots */
        .status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
        .status-dot.green { background: var(--tf-success); }
        .status-dot.amber { background: var(--tf-amber); }
        .status-dot.red { background: var(--tf-danger); }

        .empty-state { text-align: center; padding: var(--tf-sp-6); color: var(--tf-gray-400); font-size: var(--tf-text-sm); }

        /* Stat list */
        .stat-list { list-style: none; padding: 0; margin: 0; }
        .stat-list li {
            display: flex; justify-content: space-between; padding: 6px 0;
            border-bottom: 1px solid var(--tf-gray-100); font-size: var(--tf-text-sm);
        }
        .stat-list li:last-child { border-bottom: none; }
        .stat-list li .v { font-weight: 700; }

        @media (max-width: 1000px) {
            .hero-row { grid-template-columns: repeat(2, 1fr); }
            .kpi-row { grid-template-columns: repeat(4, 1fr); }
            .grid-2, .grid-3 { grid-template-columns: 1fr; }
            .machine-mini-grid { grid-template-columns: repeat(2, 1fr); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="top-bar">
            <h1>Executive Summary</h1>
            <div class="actions">
                <a href="/reports/production" class="btn btn-secondary">Production Metrics</a>
                <a href="/shop-floor" class="btn btn-secondary">Shop Floor</a>
                <a href="/shipping" class="btn btn-secondary">Shipping</a>
                <a href="/field/completion" class="btn btn-secondary">Field</a>
                <button onclick="loadDashboard()" class="btn btn-primary">Refresh</button>
            </div>
        </div>

        <!-- Today strip -->
        <div class="today-strip" id="todayStrip">
            <span class="label">Today</span>
            <span class="stat">Started: <strong id="todayStarted">—</strong></span>
            <span class="stat">Completed: <strong id="todayCompleted">—</strong></span>
            <span class="stat">This Week: <strong id="weekCompleted">—</strong> completed</span>
        </div>

        <!-- Hero KPIs -->
        <div class="hero-row">
            <div class="hero-card blue">
                <div class="val" id="heroProjects">—</div>
                <div class="lbl">Active Projects</div>
            </div>
            <div class="hero-card green">
                <div class="val" id="heroFabPct">—</div>
                <div class="lbl">Fabrication Complete</div>
            </div>
            <div class="hero-card amber">
                <div class="val" id="heroQCRate">—</div>
                <div class="lbl">QC Pass Rate</div>
            </div>
            <div class="hero-card" id="heroPunchCard">
                <div class="val" id="heroPunches">—</div>
                <div class="lbl">Open Punch Items</div>
            </div>
        </div>

        <!-- Secondary KPIs -->
        <div class="kpi-row" id="secondaryKpis">
            <div class="kpi-card"><div class="val" id="kpiTotalItems">—</div><div class="lbl">Total Items</div></div>
            <div class="kpi-card"><div class="val" id="kpiShipped">—</div><div class="lbl">Items Shipped</div></div>
            <div class="kpi-card"><div class="val" id="kpiInstalled">—</div><div class="lbl">Installed</div></div>
            <div class="kpi-card"><div class="val" id="kpiFieldPct">—</div><div class="lbl">Field Complete</div></div>
            <div class="kpi-card"><div class="val" id="kpiLoads">—</div><div class="lbl">Total Loads</div></div>
            <div class="kpi-card"><div class="val" id="kpiWeight">—</div><div class="lbl">Lbs Shipped</div></div>
            <div class="kpi-card"><div class="val" id="kpiAttention">—</div><div class="lbl">Needs Attention</div></div>
        </div>

        <!-- Shop Floor + Shipping -->
        <div class="grid-2">
            <!-- Shop Floor -->
            <div class="panel">
                <div class="panel-header">
                    <span>Shop Floor</span>
                    <a href="/shop-floor">View Details</a>
                </div>
                <div class="panel-body">
                    <div class="machine-mini-grid" id="machineGrid">
                        <div class="empty-state">Loading...</div>
                    </div>
                    <div style="margin-top:var(--tf-sp-3);font-size:12px;color:var(--tf-gray-500);">
                        Total fab time: <strong id="totalFabTime">—</strong> min
                    </div>
                </div>
            </div>

            <!-- Shipping Pipeline -->
            <div class="panel">
                <div class="panel-header">
                    <span>Shipping Pipeline</span>
                    <a href="/shipping">View Details</a>
                </div>
                <div class="panel-body">
                    <div class="pipeline-bar" id="pipelineBar"></div>
                    <div class="pipe-legend">
                        <span><span class="dot" style="background:var(--tf-amber)"></span> Building</span>
                        <span><span class="dot" style="background:var(--tf-blue)"></span> Ready</span>
                        <span><span class="dot" style="background:#8b5cf6"></span> In Transit</span>
                        <span><span class="dot" style="background:var(--tf-success)"></span> Delivered</span>
                        <span><span class="dot" style="background:#059669"></span> Complete</span>
                    </div>
                    <ul class="stat-list" style="margin-top:var(--tf-sp-3);" id="shippingStats">
                    </ul>
                </div>
            </div>
        </div>

        <!-- Field Progress + QC Health -->
        <div class="grid-2">
            <div class="panel">
                <div class="panel-header">
                    <span>Field Progress</span>
                    <a href="/field/completion">View Details</a>
                </div>
                <div class="panel-body">
                    <ul class="stat-list" id="fieldStats">
                        <li class="empty-state">Loading...</li>
                    </ul>
                </div>
            </div>

            <div class="panel">
                <div class="panel-header">
                    <span>Status Breakdown</span>
                    <a href="/reports/production">Production Metrics</a>
                </div>
                <div class="panel-body">
                    <ul class="stat-list" id="statusBreakdown">
                        <li class="empty-state">Loading...</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <script>
    async function loadDashboard() {
        try {
            const res = await fetch('/api/reports/executive');
            const data = await res.json();
            if (!data.ok) return;
            renderDashboard(data.report);
        } catch (e) {
            console.error('Failed to load executive summary', e);
        }
    }

    function renderDashboard(r) {
        const kpis = r.kpis || {};

        // Today
        document.getElementById('todayStarted').textContent = r.today?.items_started || 0;
        document.getElementById('todayCompleted').textContent = r.today?.items_completed || 0;
        document.getElementById('weekCompleted').textContent = r.this_week?.items_completed || 0;

        // Hero KPIs
        document.getElementById('heroProjects').textContent = kpis.active_projects || 0;
        document.getElementById('heroFabPct').textContent = (kpis.fabrication_complete_pct || 0) + '%';
        document.getElementById('heroQCRate').textContent = (kpis.qc_pass_rate || 0) + '%';
        const punches = kpis.open_punch_items || 0;
        document.getElementById('heroPunches').textContent = punches;
        const punchCard = document.getElementById('heroPunchCard');
        punchCard.className = 'hero-card ' + (punches === 0 ? 'green' : punches > 5 ? 'red' : 'amber');

        // Secondary KPIs
        document.getElementById('kpiTotalItems').textContent = kpis.total_items || 0;
        document.getElementById('kpiShipped').textContent = r.shipping?.total_items_shipped || 0;
        document.getElementById('kpiInstalled').textContent = r.field?.total_installed || 0;
        document.getElementById('kpiFieldPct').textContent = (kpis.field_completion_pct || 0) + '%';
        document.getElementById('kpiLoads').textContent = r.shipping?.total_loads || 0;
        document.getElementById('kpiWeight').textContent = (r.shipping?.total_weight_shipped || 0).toLocaleString();
        document.getElementById('kpiAttention').textContent = r.shop_floor?.needs_attention || 0;

        // Machine grid
        const machines = r.shop_floor?.machines || {};
        const mKeys = Object.keys(machines);
        if (mKeys.length > 0) {
            document.getElementById('machineGrid').innerHTML = mKeys.map(m => {
                const d = machines[m];
                const dot = d.active > 0 ? 'green' : d.queued > 0 ? 'amber' : 'red';
                return `<div class="machine-mini">
                    <div class="name">${d.label || m}</div>
                    <span class="active-dot" style="background:var(--tf-${dot === 'green' ? 'success' : dot === 'amber' ? 'amber' : 'gray-300'})"></span>
                    ${d.active} active · ${d.queued} queued
                </div>`;
            }).join('');
        }
        document.getElementById('totalFabTime').textContent = (r.shop_floor?.total_fab_minutes || 0).toLocaleString();

        // Shipping pipeline
        const ship = r.shipping || {};
        const totalLoads = ship.total_loads || 1;
        const segments = [
            { cls: 'building', count: ship.building || 0 },
            { cls: 'ready', count: ship.ready || 0 },
            { cls: 'transit', count: ship.in_transit || 0 },
            { cls: 'delivered', count: ship.delivered || 0 },
            { cls: 'complete', count: ship.complete || 0 },
        ];
        document.getElementById('pipelineBar').innerHTML = segments
            .filter(s => s.count > 0)
            .map(s => {
                const pct = Math.max((s.count / totalLoads) * 100, 5);
                return `<div class="pipe-seg ${s.cls}" style="width:${pct}%">${s.count}</div>`;
            }).join('');

        document.getElementById('shippingStats').innerHTML = `
            <li><span>On-Time Delivery</span><span class="v">${kpis.on_time_delivery_pct || 0}%</span></li>
            <li><span>Items Shipped</span><span class="v">${(ship.total_items_shipped || 0).toLocaleString()}</span></li>
            <li><span>Weight Shipped</span><span class="v">${(ship.total_weight_shipped || 0).toLocaleString()} lbs</span></li>
        `;

        // Field progress
        const f = r.field || {};
        document.getElementById('fieldStats').innerHTML = `
            <li><span>Active Field Projects</span><span class="v">${f.active_projects || 0}</span></li>
            <li><span>Items Installed</span><span class="v">${f.total_installed || 0}</span></li>
            <li><span>Items Delivered (awaiting install)</span><span class="v">${f.total_delivered || 0}</span></li>
            <li><span>Open Punches</span><span class="v" style="color:${(f.open_punches || 0) > 0 ? 'var(--tf-danger)' : 'inherit'}">${f.open_punches || 0}</span></li>
            <li><span>Critical Punches</span><span class="v" style="color:${(f.critical_punches || 0) > 0 ? 'var(--tf-danger)' : 'inherit'}">${f.critical_punches || 0}</span></li>
            <li><span>Field Completion</span><span class="v">${kpis.field_completion_pct || 0}%</span></li>
        `;

        // Status breakdown
        const sc = r.shop_floor?.status_counts || {};
        const statusLabels = {
            queued: 'Queued', approved: 'Approved', stickers_printed: 'Stickers Printed',
            staged: 'Staged', in_progress: 'In Progress', fabricated: 'Fabricated',
            qc_pending: 'QC Pending', qc_approved: 'QC Approved', qc_rejected: 'QC Rejected',
            ready_to_ship: 'Ready to Ship', shipped: 'Shipped', delivered: 'Delivered',
            installed: 'Installed', on_hold: 'On Hold',
        };
        const statusOrder = Object.keys(statusLabels);
        document.getElementById('statusBreakdown').innerHTML = statusOrder
            .filter(s => (sc[s] || 0) > 0)
            .map(s => `<li><span>${statusLabels[s]}</span><span class="v">${sc[s]}</span></li>`)
            .join('') || '<li class="empty-state">No items yet</li>';
    }

    loadDashboard();
    setInterval(loadDashboard, 60000);
    </script>
</body>
</html>
"""
