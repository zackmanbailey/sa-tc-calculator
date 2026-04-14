"""
TitanForge v4 — Production Metrics Dashboard
===============================================
Plant manager / PM view of production throughput, cycle times,
machine utilization, bottleneck detection, and phase distribution.
"""
from templates.shared_styles import DESIGN_SYSTEM_CSS

PRODUCTION_METRICS_PAGE_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TitanForge — Production Metrics</title>
    <style>
""" + DESIGN_SYSTEM_CSS + r"""

        .container { max-width: 1400px; margin: 0 auto; padding: var(--tf-sp-6) var(--tf-sp-8); }

        .top-bar {
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: var(--tf-sp-6);
        }
        .top-bar h1 { font-size: var(--tf-text-xl); font-weight: 800; margin: 0; }
        .top-bar .actions { display: flex; gap: var(--tf-sp-3); align-items: center; }

        .period-select {
            padding: var(--tf-sp-2) var(--tf-sp-3); border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-md); font-size: var(--tf-text-sm);
        }

        /* KPI cards row */
        .kpi-row { display: grid; grid-template-columns: repeat(5, 1fr); gap: var(--tf-sp-4); margin-bottom: var(--tf-sp-6); }
        .kpi-card {
            background: var(--tf-surface); border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-lg); padding: var(--tf-sp-5); text-align: center;
        }
        .kpi-card .val { font-size: var(--tf-text-2xl); font-weight: 800; color: var(--tf-gray-900); }
        .kpi-card .lbl { font-size: var(--tf-text-xs); color: var(--tf-gray-500); text-transform: uppercase; letter-spacing: 0.04em; margin-top: 2px; }
        .kpi-card.blue { border-left: 4px solid var(--tf-blue); }
        .kpi-card.green { border-left: 4px solid var(--tf-success); }
        .kpi-card.amber { border-left: 4px solid var(--tf-amber); }
        .kpi-card.purple { border-left: 4px solid #8b5cf6; }
        .kpi-card.red { border-left: 4px solid var(--tf-danger); }

        /* 2-col layout */
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: var(--tf-sp-6); margin-bottom: var(--tf-sp-6); }
        .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: var(--tf-sp-6); margin-bottom: var(--tf-sp-6); }

        /* Panels */
        .panel {
            background: var(--tf-surface); border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-lg); overflow: hidden;
        }
        .panel-header {
            padding: var(--tf-sp-3) var(--tf-sp-5); border-bottom: 1px solid var(--tf-border);
            font-weight: 700; font-size: var(--tf-text-sm); background: var(--tf-gray-50);
        }
        .panel-body { padding: var(--tf-sp-5); }

        /* Throughput chart (simple bar chart via CSS) */
        .chart-container { height: 180px; display: flex; align-items: flex-end; gap: 2px; padding-top: var(--tf-sp-3); }
        .chart-bar {
            flex: 1; background: var(--tf-blue-mid); border-radius: 2px 2px 0 0;
            min-height: 2px; position: relative; transition: all 0.3s;
        }
        .chart-bar:hover { background: var(--tf-blue); }
        .chart-bar .tooltip {
            display: none; position: absolute; bottom: 100%; left: 50%; transform: translateX(-50%);
            background: var(--tf-gray-800); color: white; padding: 4px 8px; border-radius: 4px;
            font-size: 11px; white-space: nowrap; margin-bottom: 4px;
        }
        .chart-bar:hover .tooltip { display: block; }

        /* Machine utilization cards */
        .machine-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: var(--tf-sp-3); }
        .machine-card {
            border: 1px solid var(--tf-border); border-radius: var(--tf-radius-md);
            padding: var(--tf-sp-3); text-align: center;
        }
        .machine-card .name { font-weight: 700; font-size: var(--tf-text-sm); margin-bottom: 4px; }
        .machine-card .stat-row { display: flex; justify-content: space-between; font-size: 12px; color: var(--tf-gray-500); }
        .machine-card .stat-row .v { font-weight: 600; color: var(--tf-gray-800); }
        .machine-card.has-active { border-left: 3px solid var(--tf-success); }

        /* Phase bar */
        .phase-bar {
            height: 32px; border-radius: var(--tf-radius-md); overflow: hidden;
            display: flex; margin-bottom: var(--tf-sp-2);
        }
        .phase-seg {
            height: 100%; display: flex; align-items: center; justify-content: center;
            font-size: 11px; font-weight: 700; color: white; min-width: 24px;
            transition: width 0.4s;
        }
        .phase-seg.prefab { background: var(--tf-gray-400); }
        .phase-seg.fab { background: var(--tf-amber); }
        .phase-seg.qc { background: #8b5cf6; }
        .phase-seg.shipping { background: var(--tf-blue); }
        .phase-seg.installed { background: var(--tf-success); }
        .phase-seg.hold { background: var(--tf-danger); }

        .phase-legend {
            display: flex; gap: var(--tf-sp-5); font-size: var(--tf-text-xs); color: var(--tf-gray-500);
        }
        .phase-legend .dot {
            display: inline-block; width: 10px; height: 10px;
            border-radius: 50%; margin-right: 4px; vertical-align: middle;
        }

        /* Bottleneck alerts */
        .bottleneck-list { list-style: none; padding: 0; margin: 0; }
        .bottleneck-item {
            display: flex; justify-content: space-between; align-items: center;
            padding: var(--tf-sp-2) var(--tf-sp-3); border-bottom: 1px solid var(--tf-gray-100);
            font-size: var(--tf-text-sm);
        }
        .bottleneck-item:last-child { border-bottom: none; }
        .severity-badge {
            display: inline-block; padding: 2px 8px; border-radius: 999px;
            font-size: 11px; font-weight: 600;
        }
        .severity-badge.high { background: #fee2e2; color: #991b1b; }
        .severity-badge.medium { background: #fef3c7; color: #92400e; }
        .severity-badge.low { background: #dbeafe; color: #1e40af; }

        .empty-state { text-align: center; padding: var(--tf-sp-6); color: var(--tf-gray-400); font-size: var(--tf-text-sm); }

        @media (max-width: 1000px) {
            .kpi-row { grid-template-columns: repeat(3, 1fr); }
            .grid-2, .grid-3 { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="top-bar">
            <h1>Production Metrics</h1>
            <div class="actions">
                <select class="period-select" id="periodSelect" onchange="loadReport()">
                    <option value="7">Last 7 Days</option>
                    <option value="14">Last 14 Days</option>
                    <option value="30" selected>Last 30 Days</option>
                    <option value="60">Last 60 Days</option>
                    <option value="90">Last 90 Days</option>
                </select>
                <a href="/reports/executive" class="btn btn-secondary">Executive Summary</a>
                <button onclick="loadReport()" class="btn btn-primary">Refresh</button>
            </div>
        </div>

        <!-- KPI cards -->
        <div class="kpi-row">
            <div class="kpi-card blue"><div class="val" id="kpiTotal">—</div><div class="lbl">Total Items</div></div>
            <div class="kpi-card green"><div class="val" id="kpiCompleted">—</div><div class="lbl">Completed (Period)</div></div>
            <div class="kpi-card amber"><div class="val" id="kpiThroughput">—</div><div class="lbl">Avg Daily Throughput</div></div>
            <div class="kpi-card purple"><div class="val" id="kpiCycleTime">—</div><div class="lbl">Avg Cycle Time (min)</div></div>
            <div class="kpi-card red"><div class="val" id="kpiAttention">—</div><div class="lbl">Needs Attention</div></div>
        </div>

        <!-- Phase Distribution -->
        <div class="panel" style="margin-bottom:var(--tf-sp-6);">
            <div class="panel-header">Phase Distribution</div>
            <div class="panel-body">
                <div class="phase-bar" id="phaseBar"></div>
                <div class="phase-legend">
                    <span><span class="dot" style="background:var(--tf-gray-400)"></span> Pre-Fab</span>
                    <span><span class="dot" style="background:var(--tf-amber)"></span> Fabrication</span>
                    <span><span class="dot" style="background:#8b5cf6"></span> QC</span>
                    <span><span class="dot" style="background:var(--tf-blue)"></span> Shipping</span>
                    <span><span class="dot" style="background:var(--tf-success)"></span> Installed</span>
                    <span><span class="dot" style="background:var(--tf-danger)"></span> On Hold</span>
                </div>
            </div>
        </div>

        <!-- Throughput Chart + Bottlenecks -->
        <div class="grid-2">
            <div class="panel">
                <div class="panel-header">Daily Throughput (Items Completed)</div>
                <div class="panel-body">
                    <div class="chart-container" id="throughputChart"></div>
                </div>
            </div>
            <div class="panel">
                <div class="panel-header">Bottleneck Alerts</div>
                <div class="panel-body">
                    <ul class="bottleneck-list" id="bottleneckList">
                        <li class="empty-state">No bottlenecks detected</li>
                    </ul>
                </div>
            </div>
        </div>

        <!-- Machine Utilization -->
        <div class="panel" style="margin-bottom:var(--tf-sp-6);">
            <div class="panel-header">Machine Utilization</div>
            <div class="panel-body">
                <div class="machine-grid" id="machineGrid">
                    <div class="empty-state">Loading machine data...</div>
                </div>
            </div>
        </div>

        <!-- Cycle Times by Machine -->
        <div class="panel">
            <div class="panel-header">Average Cycle Time by Machine (minutes)</div>
            <div class="panel-body">
                <div class="machine-grid" id="cycleTimeGrid">
                    <div class="empty-state">Loading cycle time data...</div>
                </div>
            </div>
        </div>
    </div>

    <script>
    async function loadReport() {
        const days = document.getElementById('periodSelect').value;
        try {
            const res = await fetch(`/api/reports/production?days_back=${days}`);
            const data = await res.json();
            if (!data.ok) return;
            renderReport(data.report);
        } catch (e) {
            console.error('Failed to load report', e);
        }
    }

    function renderReport(r) {
        // KPIs
        document.getElementById('kpiTotal').textContent = r.total_items || 0;
        document.getElementById('kpiCompleted').textContent = r.throughput?.total_completed || 0;
        document.getElementById('kpiThroughput').textContent = r.throughput?.avg_daily || 0;
        document.getElementById('kpiCycleTime').textContent = r.cycle_times?.avg_minutes || 0;
        document.getElementById('kpiAttention').textContent = r.needs_attention_count || 0;

        // Phase bar
        const pd = r.phase_distribution || {};
        const total = r.total_items || 1;
        const phases = [
            { cls: 'prefab', count: pd.prefab || 0 },
            { cls: 'fab', count: pd.fabrication || 0 },
            { cls: 'qc', count: pd.qc || 0 },
            { cls: 'shipping', count: pd.shipping || 0 },
            { cls: 'installed', count: pd.installed || 0 },
            { cls: 'hold', count: pd.on_hold || 0 },
        ];
        document.getElementById('phaseBar').innerHTML = phases
            .filter(p => p.count > 0)
            .map(p => {
                const pct = Math.max((p.count / total) * 100, 3);
                return `<div class="phase-seg ${p.cls}" style="width:${pct}%">${p.count}</div>`;
            }).join('');

        // Throughput chart
        const series = r.throughput?.series || [];
        const maxCount = Math.max(...series.map(s => s.count), 1);
        document.getElementById('throughputChart').innerHTML = series.map(s => {
            const h = Math.max((s.count / maxCount) * 160, 2);
            return `<div class="chart-bar" style="height:${h}px">
                <div class="tooltip">${s.date}: ${s.count}</div>
            </div>`;
        }).join('');

        // Bottlenecks
        const bl = r.bottlenecks || [];
        if (bl.length === 0) {
            document.getElementById('bottleneckList').innerHTML =
                '<li class="empty-state">No bottlenecks detected</li>';
        } else {
            document.getElementById('bottleneckList').innerHTML = bl.map(b =>
                `<li class="bottleneck-item">
                    <span>${b.label} <strong>(${b.count})</strong></span>
                    <span class="severity-badge ${b.severity}">${b.severity}</span>
                </li>`
            ).join('');
        }

        // Machine utilization
        const mu = r.machine_utilization || {};
        const mKeys = Object.keys(mu);
        if (mKeys.length === 0) {
            document.getElementById('machineGrid').innerHTML = '<div class="empty-state">No machine data</div>';
        } else {
            document.getElementById('machineGrid').innerHTML = mKeys.map(m => {
                const d = mu[m];
                const cls = d.active > 0 ? 'has-active' : '';
                return `<div class="machine-card ${cls}">
                    <div class="name">${d.label}</div>
                    <div class="stat-row"><span>Active</span><span class="v">${d.active}</span></div>
                    <div class="stat-row"><span>Queued</span><span class="v">${d.queued}</span></div>
                    <div class="stat-row"><span>Completed</span><span class="v">${d.completed}</span></div>
                    <div class="stat-row"><span>Total Min</span><span class="v">${d.total_minutes}</span></div>
                </div>`;
            }).join('');
        }

        // Cycle times by machine
        const ct = r.cycle_times?.by_machine || {};
        const cKeys = Object.keys(ct);
        if (cKeys.length === 0) {
            document.getElementById('cycleTimeGrid').innerHTML = '<div class="empty-state">No cycle time data</div>';
        } else {
            document.getElementById('cycleTimeGrid').innerHTML = cKeys.map(m => {
                const mins = ct[m];
                const label = mu[m]?.label || m;
                return `<div class="machine-card">
                    <div class="name">${label}</div>
                    <div style="font-size:var(--tf-text-2xl);font-weight:800;color:${mins > 60 ? 'var(--tf-amber)' : 'var(--tf-success)'};">${mins}</div>
                    <div style="font-size:11px;color:var(--tf-gray-500);">avg minutes</div>
                </div>`;
            }).join('');
        }
    }

    loadReport();
    setInterval(loadReport, 60000);
    </script>
</body>
</html>
"""
