"""
TitanForge v3.0 — Shop Floor Dashboard Template
=================================================
Real-time fabrication dashboard showing:
  - KPI metrics (active WOs, items in progress, throughput)
  - Machine utilization cards with active items
  - Active work order list with progress bars
  - Live activity feed
  - Auto-refresh every 30 seconds
"""

from templates.shared_styles import DESIGN_SYSTEM_CSS

SHOP_FLOOR_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TitanForge — Shop Floor</title>
<style>
""" + DESIGN_SYSTEM_CSS + """

/* ── Shop Floor Dashboard ─── */
.sf-container {
    max-width: 1500px;
    margin: 0 auto;
    padding: 20px;
}

.sf-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
}

.sf-header h1 {
    font-size: 1.5rem;
    font-weight: 800;
    color: var(--tf-navy);
    margin: 0;
}

.sf-header-right {
    display: flex;
    align-items: center;
    gap: 12px;
}

.live-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: var(--tf-green);
    animation: pulse 2s infinite;
    display: inline-block;
}

@keyframes pulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(16,185,129,0.4); }
    50% { opacity: 0.7; box-shadow: 0 0 0 6px rgba(16,185,129,0); }
}

.refresh-label {
    font-size: 0.78rem;
    color: var(--tf-slate);
}

.nav-links {
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
}

.nav-links a {
    font-size: 0.82rem;
    color: var(--tf-blue-mid);
    text-decoration: none;
    padding: 4px 12px;
    border-radius: 6px;
    background: var(--tf-bg);
}

.nav-links a:hover {
    background: var(--tf-blue-light);
}

/* ── KPI Row ─── */
.kpi-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 14px;
    margin-bottom: 24px;
}

.kpi-card {
    background: #1E293B;
    border: 1px solid var(--tf-border);
    border-radius: 10px;
    padding: 16px;
    text-align: center;
    transition: box-shadow 0.2s;
    cursor: pointer;
}

.kpi-card:hover {
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    border-color: var(--tf-blue-mid);
}

.kpi-value {
    font-size: 2rem;
    font-weight: 800;
    font-family: 'SF Mono', monospace;
    color: var(--tf-navy);
    line-height: 1;
}

.kpi-value.green { color: var(--tf-green); }
.kpi-value.blue { color: var(--tf-blue); }
.kpi-value.amber { color: var(--tf-amber); }

.kpi-label {
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--tf-slate);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 6px;
}

/* ── Two-column layout ─── */
.sf-grid {
    display: grid;
    grid-template-columns: 1fr 380px;
    gap: 20px;
}

@media (max-width: 1024px) {
    .sf-grid { grid-template-columns: 1fr; }
}

/* ── Machine Cards ─── */
.machines-section h2 {
    font-size: 1.1rem;
    font-weight: 700;
    margin: 0 0 14px;
    color: var(--tf-navy);
}

.machines-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 12px;
    margin-bottom: 24px;
}

.machine-card {
    background: #1E293B;
    border: 1px solid var(--tf-border);
    border-radius: 10px;
    padding: 14px;
    transition: all 0.2s;
    position: relative;
    overflow: hidden;
    cursor: pointer;
}

.machine-card:hover {
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    border-color: var(--tf-blue-mid);
}

.machine-card.busy {
    border-left: 4px solid var(--tf-green);
}

.machine-card.idle {
    border-left: 4px solid var(--tf-border);
    opacity: 0.7;
}

.machine-card.queued-work {
    border-left: 4px solid var(--tf-amber);
}

.machine-name {
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--tf-navy);
    margin-bottom: 2px;
}

.machine-location {
    font-size: 0.72rem;
    color: var(--tf-slate);
    margin-bottom: 8px;
}

.machine-stats {
    display: flex;
    gap: 12px;
    font-size: 0.78rem;
}

.machine-stat {
    text-align: center;
}

.machine-stat-val {
    font-weight: 800;
    font-family: 'SF Mono', monospace;
    font-size: 1.1rem;
}

.machine-stat-val.active { color: var(--tf-green); }
.machine-stat-val.queued { color: var(--tf-amber); }
.machine-stat-val.done { color: var(--tf-blue); }

.machine-stat-label {
    font-size: 0.65rem;
    color: var(--tf-slate);
    text-transform: uppercase;
    letter-spacing: 0.3px;
}

.machine-active-items {
    margin-top: 8px;
    border-top: 1px solid var(--tf-border);
    padding-top: 8px;
}

.machine-active-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 4px 0;
    font-size: 0.75rem;
    cursor: pointer;
    border-radius: 4px;
    padding: 4px 4px;
}

.machine-active-item:hover {
    background: var(--tf-bg);
}

.machine-active-item .mark {
    font-family: 'SF Mono', monospace;
    font-weight: 700;
    color: var(--tf-navy);
}

.machine-active-item .job {
    color: var(--tf-blue-mid);
    font-size: 0.7rem;
}

.machine-active-item .elapsed {
    font-family: 'SF Mono', monospace;
    color: var(--tf-green);
    font-size: 0.72rem;
}

/* ── Active WO List ─── */
.wo-list-section {
    margin-bottom: 24px;
}

.wo-list-section h2 {
    font-size: 1.1rem;
    font-weight: 700;
    margin: 0 0 14px;
    color: var(--tf-navy);
}

.wo-mini-card {
    background: #1E293B;
    border: 1px solid var(--tf-border);
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: all 0.2s;
}

.wo-mini-card:hover {
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    border-color: var(--tf-blue-mid);
}

.wo-mini-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
}

.wo-mini-id {
    font-family: 'SF Mono', monospace;
    font-size: 0.78rem;
    font-weight: 700;
    color: var(--tf-navy);
}

.wo-mini-status {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 0.68rem;
    font-weight: 600;
}

.wo-mini-status.approved { background: #1E3A5F; color: #1E40AF; }
.wo-mini-status.stickers_printed { background: #E0E7FF; color: #4338CA; }
.wo-mini-status.in_progress { background: #3B2A1A; color: #92400E; }
.wo-mini-status.queued { background: #0F172A; color: #64748B; }
.wo-mini-status.on_hold { background: #3B1A1A; color: #991B1B; }

.wo-mini-progress {
    background: #E2E8F0;
    border-radius: 4px;
    height: 6px;
    overflow: hidden;
    margin-top: 6px;
}

.wo-mini-progress-fill {
    height: 100%;
    border-radius: 4px;
    background: linear-gradient(90deg, var(--tf-blue-mid), var(--tf-green));
    transition: width 0.5s;
}

.wo-mini-meta {
    display: flex;
    justify-content: space-between;
    font-size: 0.72rem;
    color: var(--tf-slate);
    margin-top: 4px;
}

/* ── Activity Feed ─── */
.feed-section h2 {
    font-size: 1.1rem;
    font-weight: 700;
    margin: 0 0 14px;
    color: var(--tf-navy);
}

.feed-list {
    max-height: 500px;
    overflow-y: auto;
}

.feed-item {
    display: flex;
    gap: 10px;
    padding: 8px 4px;
    border-bottom: 1px solid var(--tf-border);
    font-size: 0.8rem;
    cursor: pointer;
    border-radius: 6px;
}

.feed-item:hover {
    background: var(--tf-bg);
}

.feed-item:last-child {
    border-bottom: none;
}

.feed-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-top: 5px;
    flex-shrink: 0;
}

.feed-dot.started { background: var(--tf-green); }
.feed-dot.finished { background: var(--tf-blue); }

.feed-content {
    flex: 1;
}

.feed-action {
    font-weight: 600;
    color: var(--tf-navy);
}

.feed-detail {
    color: var(--tf-slate);
    font-size: 0.75rem;
}

.feed-time {
    font-family: 'SF Mono', monospace;
    font-size: 0.7rem;
    color: var(--tf-slate);
    white-space: nowrap;
}

/* ── Status distribution bar ─── */
.status-bar {
    display: flex;
    height: 8px;
    border-radius: 4px;
    overflow: hidden;
    margin: 12px 0;
    background: var(--tf-border);
}

.status-bar-segment {
    height: 100%;
    transition: width 0.5s;
}

.status-bar-segment.complete { background: var(--tf-green); }
.status-bar-segment.in_progress { background: var(--tf-amber); }
.status-bar-segment.queued { background: var(--tf-border); }

/* ── Empty state ─── */
.sf-empty {
    text-align: center;
    padding: 60px 20px;
    color: var(--tf-slate);
}

.sf-empty h3 {
    color: var(--tf-navy);
    margin: 12px 0 8px;
}

/* ── Dispatch Section ─── */
.dispatch-section {
    background: #FFFBEB;
    border: 1px solid #FDE68A;
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 24px;
}
.dispatch-section h2 {
    font-size: 1rem;
    font-weight: 700;
    color: #92400E;
    margin: 0 0 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.dispatch-card {
    background: #1E293B;
    border: 1px solid var(--tf-border);
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.dispatch-card-info {
    flex: 1;
}
.dispatch-card-id {
    font-family: 'SF Mono', monospace;
    font-size: 0.82rem;
    font-weight: 700;
    color: var(--tf-navy);
}
.dispatch-card-detail {
    font-size: 0.75rem;
    color: var(--tf-slate);
    margin-top: 2px;
}
.dispatch-assign {
    display: flex;
    gap: 6px;
    align-items: center;
}
.dispatch-assign select {
    padding: 6px 10px;
    border: 1px solid var(--tf-border);
    border-radius: 6px;
    font-size: 0.78rem;
    background: #1E293B;
}
.dispatch-assign button {
    padding: 6px 14px;
    border: none;
    border-radius: 6px;
    font-size: 0.78rem;
    font-weight: 600;
    cursor: pointer;
    background: var(--tf-blue);
    color: white;
}
.dispatch-assign button:hover { background: var(--tf-blue-mid); }

/* ── Machine Status Indicator ─── */
.machine-status-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    display: inline-block;
    cursor: pointer;
    position: relative;
}
.machine-status-dot.running { background: #22C55E; box-shadow: 0 0 6px rgba(34,197,94,0.5); }
.machine-status-dot.idle { background: #FBBF24; }
.machine-status-dot.down { background: #EF4444; }

.machine-extra {
    font-size: 0.72rem;
    color: var(--tf-slate);
    margin-top: 4px;
}

/* ── Toast ─── */
.sf-toast {
    position: fixed;
    bottom: 24px;
    right: 24px;
    padding: 14px 24px;
    border-radius: 10px;
    font-weight: 600;
    font-size: 0.9rem;
    z-index: 9999;
    transform: translateY(100px);
    opacity: 0;
    transition: all 0.3s;
    max-width: 400px;
}
.sf-toast.show { transform: translateY(0); opacity: 1; }
.sf-toast.success { background: #065F46; color: white; }
.sf-toast.error { background: #991B1B; color: white; }

@media (max-width: 768px) {
    .sf-container { padding: 12px; }
    .kpi-row { grid-template-columns: repeat(2, 1fr); }
    .machines-grid { grid-template-columns: 1fr; }
}
</style>
</head>
<body>

<div class="sf-container">

    <!-- Nav links -->
    <div class="nav-links">
        <a href="/">Dashboard</a>
        <a href="/sa">SA Estimator</a>
        <a href="/customers">Customers</a>
    </div>

    <!-- Header -->
    <div class="sf-header">
        <h1>Shop Floor</h1>
        <div class="sf-header-right">
            <span class="live-dot"></span>
            <span class="refresh-label" id="lastRefresh">Refreshing...</span>
            <button onclick="loadData()" style="background:none;border:1px solid var(--tf-border);border-radius:6px;padding:6px 12px;font-size:0.8rem;cursor:pointer;">Refresh</button>
        </div>
    </div>

    <!-- KPI Row -->
    <div class="kpi-row" id="kpiRow">
        <div class="kpi-card" onclick="window.location.href='/reports/production'"><div class="kpi-value" id="kpiActiveWOs">-</div><div class="kpi-label">Active Work Orders</div></div>
        <div class="kpi-card" onclick="window.location.href='/reports/production'"><div class="kpi-value amber" id="kpiInProgress">-</div><div class="kpi-label">Items In Progress</div></div>
        <div class="kpi-card" onclick="window.location.href='/reports/production'"><div class="kpi-value green" id="kpiTodayCompleted">-</div><div class="kpi-label">Completed Today</div></div>
        <div class="kpi-card" onclick="window.location.href='/qc-dashboard'"><div class="kpi-value blue" id="kpiTotalCompleted">-</div><div class="kpi-label">Total Completed</div></div>
        <div class="kpi-card" onclick="window.location.href='/reports/production'"><div class="kpi-value" id="kpiTotalItems">-</div><div class="kpi-label">Total Items</div></div>
        <div class="kpi-card" onclick="window.location.href='/reports/production'"><div class="kpi-value green" id="kpiAvgFab">-</div><div class="kpi-label">Avg Fab Time (min)</div></div>
        <div class="kpi-card" onclick="window.location.href='/reports/production'"><div class="kpi-value blue" id="kpiTotalFab">-</div><div class="kpi-label">Total Fab Time (hr)</div></div>
    </div>

    <!-- Status distribution -->
    <div class="status-bar" id="statusBar"></div>

    <!-- Dispatch Section (unassigned WOs) -->
    <div class="dispatch-section" id="dispatchSection" style="display:none;">
        <h2>Dispatch &mdash; Unassigned Work Orders</h2>
        <div id="dispatchList"></div>
    </div>

    <!-- Main grid -->
    <div class="sf-grid">
        <div>
            <!-- Machines Section -->
            <div class="machines-section">
                <h2>Machine Utilization</h2>
                <div class="machines-grid" id="machinesGrid"></div>
            </div>

            <!-- Active Work Orders -->
            <div class="wo-list-section">
                <h2>Active Work Orders</h2>
                <div id="activeWOList"></div>
            </div>
        </div>

        <!-- Right column: Activity Feed -->
        <div class="feed-section">
            <h2>Activity Feed</h2>
            <div class="feed-list" id="activityFeed">
                <div class="sf-empty" style="padding:30px;">
                    <p>No activity yet.</p>
                </div>
            </div>
        </div>
    </div>
</div>
<div class="sf-toast" id="sfToast"></div>

<script>
let refreshTimer = null;

document.addEventListener('DOMContentLoaded', () => {
    loadData();
    // Auto-refresh every 30 seconds
    refreshTimer = setInterval(loadData, 30000);
});

async function loadData() {
    try {
        const resp = await fetch('/api/shop-floor/data');
        const data = await resp.json();
        if (data.ok) {
            renderDashboard(data);
            document.getElementById('lastRefresh').textContent =
                'Updated ' + new Date().toLocaleTimeString();
        }
    } catch (e) {
        console.error('Shop floor data load failed:', e);
    }
}

let machineKeys = [];

function renderDashboard(data) {
    const s = data.summary;
    const machines = data.machines;
    const activeWOs = data.active_wos;
    const events = data.events;
    const unassignedWOs = data.unassigned_wos || [];

    // ── KPIs ──
    document.getElementById('kpiActiveWOs').textContent = s.active_work_orders;
    document.getElementById('kpiInProgress').textContent = s.in_progress_items;
    document.getElementById('kpiTodayCompleted').textContent = s.today_completed;
    document.getElementById('kpiTotalCompleted').textContent = s.completed_items;
    document.getElementById('kpiTotalItems').textContent = s.total_items;
    document.getElementById('kpiAvgFab').textContent = s.avg_fab_minutes > 0 ? s.avg_fab_minutes.toFixed(1) : '-';
    document.getElementById('kpiTotalFab').textContent = s.total_fab_minutes > 0 ? (s.total_fab_minutes / 60).toFixed(1) : '-';

    // ── Dispatch Section ──
    const dispatchSection = document.getElementById('dispatchSection');
    if (unassignedWOs.length > 0) {
        dispatchSection.style.display = 'block';
        machineKeys = Object.keys(machines);
        let dHtml = '';
        for (const wo of unassignedWOs) {
            const machineOpts = machineKeys.map(m =>
                '<option value="' + m + '">' + (machines[m].name || m) + '</option>'
            ).join('');
            dHtml += '<div class="dispatch-card">' +
                '<div class="dispatch-card-info">' +
                    '<div class="dispatch-card-id">' + wo.work_order_id + '</div>' +
                    '<div class="dispatch-card-detail">' + wo.job_code + ' &bull; ' +
                        (wo.project_name || '') + ' &bull; ' + wo.total_items + ' items' +
                        (wo.priority && wo.priority !== 'normal' ? ' &bull; <strong style="color:#DC2626;">' + wo.priority.toUpperCase() + '</strong>' : '') +
                    '</div>' +
                '</div>' +
                '<div class="dispatch-assign">' +
                    '<select id="assign_' + wo.work_order_id + '">' +
                        '<option value="">-- Machine --</option>' +
                        machineOpts +
                    '</select>' +
                    '<button onclick="quickAssign(\'' + wo.job_code + '\', \'' + wo.work_order_id + '\')">Assign</button>' +
                '</div>' +
            '</div>';
        }
        document.getElementById('dispatchList').innerHTML = dHtml;
    } else {
        dispatchSection.style.display = 'none';
    }

    // ── Status bar ──
    const total = s.total_items || 1;
    const statusBar = document.getElementById('statusBar');
    statusBar.innerHTML = `
        <div class="status-bar-segment complete" style="width:${100*s.completed_items/total}%"></div>
        <div class="status-bar-segment in_progress" style="width:${100*s.in_progress_items/total}%"></div>
        <div class="status-bar-segment queued" style="width:${100*s.queued_items/total}%"></div>
    `;

    // ── Machines ──
    const machinesGrid = document.getElementById('machinesGrid');
    let mHtml = '';
    const mKeys = Object.keys(machines).sort((a, b) => {
        const ma = machines[a], mb = machines[b];
        return (mb.in_progress + mb.queued) - (ma.in_progress + ma.queued);
    });

    for (const mId of mKeys) {
        const m = machines[mId];
        const isBusy = m.in_progress > 0;
        const hasQueue = m.queued > 0 && !isBusy;
        const cls = isBusy ? 'busy' : (hasQueue ? 'queued-work' : 'idle');

        let activeItemsHtml = '';
        if (m.active_items && m.active_items.length > 0) {
            activeItemsHtml = '<div class="machine-active-items">';
            for (const item of m.active_items.slice(0, 3)) {
                const elapsed = item.started_at ? getElapsed(item.started_at) : '';
                activeItemsHtml += `
                    <div class="machine-active-item" onclick="event.stopPropagation(); window.location.href='/work-station/${encodeURIComponent(mId)}'">
                        <span class="mark">${item.ship_mark}</span>
                        <span class="job">${item.job_code}</span>
                        <span class="elapsed">${elapsed}</span>
                    </div>`;
            }
            if (m.active_items.length > 3) {
                activeItemsHtml += `<div style="font-size:0.7rem;color:var(--tf-slate);text-align:center;">+${m.active_items.length - 3} more</div>`;
            }
            activeItemsHtml += '</div>';
        }

        const avgTime = m.completed > 0 ? (m.total_fab_minutes / m.completed).toFixed(1) : '-';

        const statusDot = isBusy ? 'running' : (hasQueue ? 'idle' : 'idle');
        const estRemaining = m.est_remaining_minutes || 0;
        const estStr = estRemaining > 0 ? (estRemaining < 60 ? Math.round(estRemaining) + 'm' : (estRemaining / 60).toFixed(1) + 'h') : '-';
        const operatorName = m.operator || '';

        mHtml += `
        <div class="machine-card ${cls}" onclick="window.location.href='/work-station/${encodeURIComponent(mId)}'">
            <div style="display:flex;align-items:center;justify-content:space-between;">
                <div class="machine-name">${mId}</div>
                <span class="machine-status-dot ${statusDot}" title="${statusDot}" onclick="event.stopPropagation(); toggleMachineStatus('${mId}')"></span>
            </div>
            <div class="machine-location">${m.name}</div>
            ${operatorName ? '<div class="machine-extra">Operator: <strong>' + operatorName + '</strong></div>' : ''}
            <div class="machine-stats">
                <div class="machine-stat">
                    <div class="machine-stat-val active">${m.in_progress}</div>
                    <div class="machine-stat-label">Active</div>
                </div>
                <div class="machine-stat">
                    <div class="machine-stat-val queued">${m.queued}</div>
                    <div class="machine-stat-label">Queue</div>
                </div>
                <div class="machine-stat">
                    <div class="machine-stat-val done">${m.completed}</div>
                    <div class="machine-stat-label">Done</div>
                </div>
            </div>
            <div class="machine-extra">Est remaining: <strong>${estStr}</strong></div>
            ${activeItemsHtml}
        </div>`;
    }
    machinesGrid.innerHTML = mHtml || '<div class="sf-empty"><p>No machines with assigned work.</p></div>';

    // ── Active WOs ──
    const woList = document.getElementById('activeWOList');
    if (activeWOs.length === 0) {
        woList.innerHTML = '<div class="sf-empty" style="padding:30px;"><h3>No Active Work Orders</h3><p>Create work orders from the Shop Drawings page.</p></div>';
    } else {
        let woHtml = '';
        for (const wo of activeWOs) {
            const statusCls = wo.status.replace(/ /g, '_');
            const label = wo.status_label || wo.status;
            const priorityBadge = wo.priority && wo.priority !== 'normal'
                ? '<span style="background:#3B1A1A;color:#991B1B;padding:2px 6px;border-radius:4px;font-size:0.68rem;font-weight:600;margin-left:6px;">' + wo.priority.toUpperCase() + '</span>'
                : '';
            woHtml += `
            <div class="wo-mini-card" onclick="window.location.href='/work-orders/${wo.job_code}'">
                <div class="wo-mini-header">
                    <span class="wo-mini-id">${wo.work_order_id}${priorityBadge}</span>
                    <span class="wo-mini-status ${statusCls}">${label}</span>
                </div>
                <div class="wo-mini-meta">
                    <span>${wo.job_code} &bull; Rev ${wo.revision}</span>
                    <span>${wo.completed_items}/${wo.total_items} items</span>
                </div>
                <div class="wo-mini-meta" style="margin-top:2px;">
                    ${wo.machine_id ? '<span>Machine: <strong>' + wo.machine_id + '</strong></span>' : '<span style="color:#F59E0B;">Unassigned</span>'}
                    ${wo.operator ? '<span>Op: ' + wo.operator + '</span>' : ''}
                    ${wo.estimated_hours ? '<span>Est: ' + wo.estimated_hours + 'h</span>' : ''}
                </div>
                <div class="wo-mini-progress">
                    <div class="wo-mini-progress-fill" style="width:${wo.progress_pct}%"></div>
                </div>
            </div>`;
        }
        woList.innerHTML = woHtml;
    }

    // ── Activity Feed ──
    const feedEl = document.getElementById('activityFeed');
    if (events.length === 0) {
        feedEl.innerHTML = '<div class="sf-empty" style="padding:30px;"><p>No activity yet. Start scanning items to see the feed.</p></div>';
    } else {
        let feedHtml = '';
        for (const evt of events) {
            const isFinished = evt.type === 'finished';
            const time = evt.time ? new Date(evt.time).toLocaleTimeString() : '';
            const date = evt.time ? new Date(evt.time).toLocaleDateString() : '';
            const durStr = isFinished && evt.duration > 0 ? ` (${evt.duration.toFixed(1)} min)` : '';

            feedHtml += `
            <div class="feed-item" onclick="window.location.href='/work-station/${encodeURIComponent(evt.machine)}'">
                <div class="feed-dot ${evt.type}"></div>
                <div class="feed-content">
                    <div class="feed-action">${evt.ship_mark} ${isFinished ? 'finished' : 'started'} on ${evt.machine}${durStr}</div>
                    <div class="feed-detail">${evt.job_code} &bull; by ${evt.by || 'system'}</div>
                </div>
                <div class="feed-time">${time}<br>${date}</div>
            </div>`;
        }
        feedEl.innerHTML = feedHtml;
    }
}

function getElapsed(isoStr) {
    try {
        const start = new Date(isoStr);
        const now = new Date();
        const diffMin = Math.round((now - start) / 60000);
        if (diffMin < 60) return diffMin + 'm';
        const hrs = Math.floor(diffMin / 60);
        const mins = diffMin % 60;
        return hrs + 'h ' + mins + 'm';
    } catch (e) {
        return '';
    }
}

async function quickAssign(jobCode, woId) {
    const sel = document.getElementById('assign_' + woId);
    if (!sel || !sel.value) {
        showSFToast('Select a machine first', 'error');
        return;
    }
    try {
        const resp = await fetch('/api/work-orders/assign', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ job_code: jobCode, wo_id: woId, machine_id: sel.value })
        });
        const data = await resp.json();
        if (data.ok) {
            showSFToast('Assigned ' + woId + ' to ' + sel.value, 'success');
            loadData();
        } else {
            showSFToast(data.error || 'Failed', 'error');
        }
    } catch (e) {
        showSFToast('Network error: ' + e.message, 'error');
    }
}

function toggleMachineStatus(machineId) {
    // Cycle through: running -> idle -> down -> running
    const dot = event.target;
    const states = ['running', 'idle', 'down'];
    let current = 'idle';
    for (const s of states) {
        if (dot.classList.contains(s)) { current = s; break; }
    }
    const nextIdx = (states.indexOf(current) + 1) % states.length;
    const next = states[nextIdx];
    dot.className = 'machine-status-dot ' + next;
    dot.title = next;
}

function showSFToast(msg, type) {
    const toast = document.getElementById('sfToast');
    toast.textContent = msg;
    toast.className = 'sf-toast ' + (type || 'success') + ' show';
    setTimeout(() => { toast.className = 'sf-toast'; }, 4000);
}
</script>
</body>
</html>
"""
