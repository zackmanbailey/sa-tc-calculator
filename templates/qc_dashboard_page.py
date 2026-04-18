"""
TitanForge v4 — QC Dashboard
==============================
Global QC metrics: pass rates, NCR tracking, inspector workload,
inspection-type breakdown. Links to QC Queue and per-project QC pages.
"""
from templates.shared_styles import DESIGN_SYSTEM_CSS

QC_DASHBOARD_PAGE_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TitanForge — QC Dashboard</title>
    <style>
""" + DESIGN_SYSTEM_CSS + r"""

        .container { max-width: 1400px; margin: 0 auto; padding: var(--tf-sp-6) var(--tf-sp-8); }

        /* Metric cards row */
        .metric-row { display: grid; grid-template-columns: repeat(5, 1fr); gap: var(--tf-sp-4); margin-bottom: var(--tf-sp-6); }
        .metric-card {
            background: var(--tf-surface); border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-lg); padding: var(--tf-sp-5);
            text-align: center;
        }
        .metric-card .value { font-size: var(--tf-text-2xl); font-weight: 800; color: var(--tf-gray-900); }
        .metric-card .label { font-size: var(--tf-text-xs); color: var(--tf-gray-500); text-transform: uppercase; letter-spacing: 0.04em; margin-top: 2px; }
        .metric-card .sublabel { font-size: 11px; color: var(--tf-gray-400); margin-top: 4px; }
        .metric-card { cursor: pointer; transition: transform 0.15s, box-shadow 0.15s; }
        .metric-card:hover { transform: translateY(-2px); box-shadow: var(--tf-shadow-md); }
        .metric-card.highlight { border-color: var(--tf-blue); border-width: 2px; }
        .metric-card.danger { border-left: 4px solid var(--tf-danger); }
        .metric-card.success { border-left: 4px solid var(--tf-success); }

        /* Two-column layout */
        .dashboard-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--tf-sp-6); }
        .panel {
            background: var(--tf-surface); border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-lg); overflow: hidden;
        }
        .panel-header {
            padding: var(--tf-sp-4) var(--tf-sp-5); border-bottom: 1px solid var(--tf-border);
            font-weight: 700; font-size: var(--tf-text-md); color: var(--tf-gray-900);
            display: flex; justify-content: space-between; align-items: center;
        }
        .panel-body { padding: var(--tf-sp-5); }

        /* Bar chart */
        .bar-chart { display: flex; flex-direction: column; gap: 8px; }
        .bar-row { display: flex; align-items: center; gap: 10px; cursor: pointer; border-radius: 4px; padding: 2px 0; transition: background 0.15s; }
        .bar-row:hover { background: var(--tf-blue-light); }
        .bar-label { width: 120px; font-size: var(--tf-text-xs); font-weight: 600; color: var(--tf-gray-700); text-align: right; }
        .bar-track { flex: 1; height: 22px; background: var(--tf-gray-100); border-radius: 4px; overflow: hidden; position: relative; }
        .bar-fill { height: 100%; border-radius: 4px; transition: width 0.5s ease; display: flex; align-items: center; justify-content: flex-end; padding-right: 6px; }
        .bar-fill span { font-size: 10px; font-weight: 700; color: #fff; }
        .bar-count { width: 40px; font-size: var(--tf-text-xs); font-weight: 700; color: var(--tf-gray-600); }

        /* Inspector table */
        .insp-table { width: 100%; border-collapse: collapse; font-size: var(--tf-text-sm); }
        .insp-table th { text-align: left; padding: 8px 10px; font-size: var(--tf-text-xs); color: var(--tf-gray-500); text-transform: uppercase; border-bottom: 2px solid var(--tf-border); }
        .insp-table td { padding: 8px 10px; border-bottom: 1px solid var(--tf-border); }
        .insp-table tr:hover td { background: var(--tf-blue-light); }
        .insp-table tbody tr { cursor: pointer; }

        /* Recent list */
        .recent-item {
            padding: 10px 0; border-bottom: 1px solid var(--tf-border);
            display: flex; justify-content: space-between; align-items: center;
        }
        .recent-item:last-child { border-bottom: none; }
        .recent-item .left { display: flex; flex-direction: column; gap: 2px; }
        .recent-item .title { font-size: var(--tf-text-sm); font-weight: 600; color: var(--tf-gray-900); }
        .recent-item { cursor: pointer; transition: background 0.15s; }
        .recent-item:hover { background: var(--tf-blue-light); }
        .recent-item .meta { font-size: 11px; color: var(--tf-gray-500); }

        /* Status badges */
        .status-badge { padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
        .status-badge.passed { background: var(--tf-success-bg); color: var(--tf-success); }
        .status-badge.failed { background: var(--tf-danger-bg); color: var(--tf-danger); }
        .status-badge.in_progress { background: var(--tf-amber-light); color: var(--tf-warning); }
        .status-badge.open { background: var(--tf-danger-bg); color: var(--tf-danger); }
        .status-badge.closed { background: var(--tf-success-bg); color: var(--tf-success); }

        .severity-badge { padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; text-transform: uppercase; }
        .severity-badge.minor { background: var(--tf-amber-light); color: #92400E; }
        .severity-badge.major { background: #FEE2E2; color: #991B1B; }
        .severity-badge.critical { background: #7F1D1D; color: #FEE2E2; }

        /* Pass rate gauge */
        .gauge-container { text-align: center; padding: var(--tf-sp-4); }
        .gauge-ring {
            width: 120px; height: 120px; border-radius: 50%; margin: 0 auto 12px;
            background: conic-gradient(var(--tf-success) 0%, var(--tf-success) var(--pct), var(--tf-gray-200) var(--pct));
            display: flex; align-items: center; justify-content: center;
        }
        .gauge-inner {
            width: 90px; height: 90px; border-radius: 50%; background: var(--tf-surface);
            display: flex; align-items: center; justify-content: center;
            font-size: var(--tf-text-2xl); font-weight: 800; color: var(--tf-gray-900);
        }

        .empty-msg { text-align: center; padding: 30px; color: var(--tf-gray-400); font-size: var(--tf-text-sm); }

        @media (max-width: 768px) {
            .metric-row { grid-template-columns: repeat(2, 1fr); }
            .dashboard-grid { grid-template-columns: 1fr; }
            .container { padding: var(--tf-sp-4); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:var(--tf-sp-5);">
            <div>
                <h1 style="font-size:var(--tf-text-2xl);font-weight:700;color:var(--tf-gray-900);">QC Dashboard</h1>
                <p style="color:var(--tf-gray-500);font-size:var(--tf-text-sm);">Quality control metrics across all projects</p>
            </div>
            <div style="display:flex;gap:var(--tf-sp-3);">
                <a href="/qc-queue" class="btn btn-primary">Inspection Queue</a>
                <button class="btn btn-outline" onclick="loadAll()">&#8635; Refresh</button>
            </div>
        </div>

        <!-- Top metrics -->
        <div class="metric-row" id="metricsRow">
            <div class="metric-card highlight" onclick="window.location.href='/qc-queue'"><div class="value" id="mTotal">—</div><div class="label">Total Inspections</div></div>
            <div class="metric-card success" onclick="window.location.href='/qc-queue?status=passed'"><div class="value" id="mPassed">—</div><div class="label">Passed</div></div>
            <div class="metric-card danger" onclick="window.location.href='/qc-queue?status=failed'"><div class="value" id="mFailed">—</div><div class="label">Failed</div></div>
            <div class="metric-card danger" onclick="window.location.href='/qc-queue?status=open_ncrs'"><div class="value" id="mOpenNCRs">—</div><div class="label">Open NCRs</div><div class="sublabel" id="mCritical"></div></div>
            <div class="metric-card" onclick="window.location.href='/qc-queue?status=fabricated'"><div class="value" id="mAwaiting">—</div><div class="label">Items Awaiting QC</div></div>
        </div>

        <!-- Dashboard grid -->
        <div class="dashboard-grid">
            <!-- Pass Rate + Type Breakdown -->
            <div class="panel">
                <div class="panel-header">Pass Rate & Inspection Types</div>
                <div class="panel-body">
                    <div id="passRateGauge" class="gauge-container">
                        <div class="gauge-ring" style="--pct: 0%;">
                            <div class="gauge-inner">—</div>
                        </div>
                        <div style="font-size:var(--tf-text-xs);color:var(--tf-gray-500);">Overall Pass Rate</div>
                    </div>
                    <div style="margin-top:var(--tf-sp-4);">
                        <div style="font-weight:700;font-size:var(--tf-text-sm);margin-bottom:8px;">Inspections by Type</div>
                        <div id="typeBreakdown" class="bar-chart"></div>
                    </div>
                </div>
            </div>

            <!-- NCR Summary -->
            <div class="panel">
                <div class="panel-header">NCR Summary
                    <div style="display:flex;gap:6px;" id="ncrSeverityBadges"></div>
                </div>
                <div class="panel-body">
                    <div id="ncrByStatus" class="bar-chart" style="margin-bottom:var(--tf-sp-4);"></div>
                    <div style="font-weight:700;font-size:var(--tf-text-sm);margin-bottom:8px;">Recent NCRs</div>
                    <div id="recentNCRs"></div>
                </div>
            </div>

            <!-- Inspector Workload -->
            <div class="panel">
                <div class="panel-header">Inspector Workload</div>
                <div class="panel-body">
                    <div id="inspectorTable"></div>
                </div>
            </div>

            <!-- Recent Inspections -->
            <div class="panel">
                <div class="panel-header">Recent Inspections</div>
                <div class="panel-body">
                    <div id="recentInspections"></div>
                </div>
            </div>
        </div>
    </div>

<script>
let metrics = null;
const TYPE_LABELS = {
    'weld_visual': 'Weld Visual (VT)',
    'bolt_inspection': 'Bolt Inspection',
    'dimensional': 'Dimensional',
    'surface_prep': 'Surface Prep',
    'nde': 'NDE',
    'material_receiving': 'Material Receiving',
};

document.addEventListener('DOMContentLoaded', loadAll);

async function loadAll() {
    try {
        const r = await fetch('/api/qc/dashboard');
        const d = await r.json();
        if (d.ok) { metrics = d.metrics; renderDashboard(); }
    } catch(e) { console.error(e); }
}

function renderDashboard() {
    const m = metrics;

    // Top metrics
    document.getElementById('mTotal').textContent = m.total_inspections;
    document.getElementById('mPassed').textContent = m.passed;
    document.getElementById('mFailed').textContent = m.failed;
    document.getElementById('mOpenNCRs').textContent = m.open_ncrs;
    document.getElementById('mCritical').textContent = m.critical_ncrs ? m.critical_ncrs + ' critical' : '';
    document.getElementById('mAwaiting').textContent = m.items_awaiting_qc;

    // Pass rate gauge
    const pct = m.pass_rate || 0;
    const gauge = document.querySelector('.gauge-ring');
    gauge.style.setProperty('--pct', pct + '%');
    const color = pct >= 90 ? 'var(--tf-success)' : (pct >= 70 ? 'var(--tf-warning)' : 'var(--tf-danger)');
    gauge.style.background = `conic-gradient(${color} 0%, ${color} ${pct}%, var(--tf-gray-200) ${pct}%)`;
    gauge.querySelector('.gauge-inner').textContent = pct + '%';

    // Type breakdown bars
    const types = m.inspections_by_type || {};
    const maxType = Math.max(...Object.values(types), 1);
    const typeColors = { weld_visual: '#3B82F6', bolt_inspection: '#F59E0B', dimensional: '#10B981', surface_prep: '#8B5CF6', nde: '#EF4444', material_receiving: '#6366F1' };
    document.getElementById('typeBreakdown').innerHTML = Object.entries(types)
        .sort((a,b) => b[1]-a[1])
        .map(([k,v]) => {
            const pctW = Math.round(v/maxType*100);
            return `<div class="bar-row" onclick="window.location.href='/qc-queue?type=${encodeURIComponent(k)}'">
                <div class="bar-label">${TYPE_LABELS[k]||k}</div>
                <div class="bar-track"><div class="bar-fill" style="width:${pctW}%;background:${typeColors[k]||'var(--tf-blue)'}"><span>${v}</span></div></div>
                <div class="bar-count">${v}</div>
            </div>`;
        }).join('') || '<div class="empty-msg">No inspections yet</div>';

    // NCR severity badges
    const sev = m.ncrs_by_severity || {};
    document.getElementById('ncrSeverityBadges').innerHTML =
        `<span class="severity-badge minor">${sev.minor||0} Minor</span>
         <span class="severity-badge major">${sev.major||0} Major</span>
         <span class="severity-badge critical">${sev.critical||0} Critical</span>`;

    // NCR by status bars
    const ncrStatus = m.ncrs_by_status || {};
    const maxNCR = Math.max(...Object.values(ncrStatus), 1);
    const statusColors = { open: '#EF4444', under_review: '#F59E0B', corrective_action: '#3B82F6', re_inspect: '#8B5CF6', closed: '#10B981', voided: '#9CA3AF' };
    document.getElementById('ncrByStatus').innerHTML = Object.entries(ncrStatus)
        .sort((a,b) => b[1]-a[1])
        .map(([k,v]) => `<div class="bar-row">
            <div class="bar-label">${k.replace('_',' ')}</div>
            <div class="bar-track"><div class="bar-fill" style="width:${Math.round(v/maxNCR*100)}%;background:${statusColors[k]||'#9CA3AF'}"><span>${v}</span></div></div>
            <div class="bar-count">${v}</div>
        </div>`).join('') || '<div class="empty-msg">No NCRs</div>';

    // Recent NCRs
    const ncrs = m.recent_ncrs || [];
    document.getElementById('recentNCRs').innerHTML = ncrs.slice(0,8).map(n =>
        `<div class="recent-item" onclick="window.location.href='/qc/${encodeURIComponent(n.job_code)}#ncrs'">
            <div class="left">
                <div class="title">${n.id}: ${n.title}</div>
                <div class="meta">${n.job_code} &middot; ${n.reported_by} &middot; ${n.created_at ? new Date(n.created_at).toLocaleDateString() : ''}</div>
            </div>
            <div style="display:flex;gap:6px;">
                <span class="severity-badge ${n.severity}">${n.severity}</span>
                <span class="status-badge ${n.status}">${n.status.replace('_',' ')}</span>
            </div>
        </div>`).join('') || '<div class="empty-msg">No NCRs yet</div>';

    // Inspector workload
    const inspectors = m.inspector_workload || {};
    if (Object.keys(inspectors).length) {
        let html = `<table class="insp-table"><thead><tr><th>Inspector</th><th>Total</th><th>Passed</th><th>Failed</th><th>Rate</th></tr></thead><tbody>`;
        for (const [name, data] of Object.entries(inspectors).sort((a,b) => b[1].total - a[1].total)) {
            const rate = data.total ? Math.round(data.passed / data.total * 100) : 0;
            html += `<tr onclick="window.location.href='/qc-queue?inspector=${encodeURIComponent(name)}'"><td style="font-weight:600;">${name}</td><td>${data.total}</td>
                <td style="color:var(--tf-success);">${data.passed}</td>
                <td style="color:var(--tf-danger);">${data.failed}</td>
                <td><strong>${rate}%</strong></td></tr>`;
        }
        html += '</tbody></table>';
        document.getElementById('inspectorTable').innerHTML = html;
    } else {
        document.getElementById('inspectorTable').innerHTML = '<div class="empty-msg">No inspector data yet</div>';
    }

    // Recent inspections
    const insp = m.recent_inspections || [];
    document.getElementById('recentInspections').innerHTML = insp.slice(0,10).map(i =>
        `<div class="recent-item" onclick="window.location.href='/qc/${encodeURIComponent(i.job_code)}'">
            <div class="left">
                <div class="title">${i.type_label || i.type}</div>
                <div class="meta">${i.job_code} &middot; ${i.inspector} &middot; ${i.created_at ? new Date(i.created_at).toLocaleDateString() : ''}</div>
            </div>
            <span class="status-badge ${i.status}">${i.status.replace('_',' ')}</span>
        </div>`).join('') || '<div class="empty-msg">No inspections yet</div>';
}
</script>
</body>
</html>
"""
