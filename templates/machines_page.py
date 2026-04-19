"""
TitanForge v4 — Machine Dashboard
====================================
Monitor machine utilization, queue status, and active jobs.
"""

MACHINES_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a;
        --tf-card: #1e293b;
        --tf-text: #e2e8f0;
        --tf-muted: #94a3b8;
        --tf-gold: #d4a843;
        --tf-blue: #3b82f6;
    }
    .machines-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 24px 32px;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
        color: var(--tf-text);
    }
    .page-header { margin-bottom: 32px; }
    .page-header h1 {
        font-size: 28px; font-weight: 800; margin: 0 0 6px 0; color: var(--tf-text);
    }
    .page-header p { font-size: 14px; color: var(--tf-muted); margin: 0; }
    .toolbar {
        display: flex; justify-content: flex-end; margin-bottom: 20px;
    }
    .btn-outline {
        background: transparent;
        border: 1px solid var(--tf-gold);
        color: var(--tf-gold);
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 700;
        font-size: 14px;
        cursor: pointer;
        text-decoration: none;
    }
    .btn-outline:hover { background: rgba(212,168,67,0.1); }
    .machine-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
        gap: 20px;
    }
    .machine-card {
        background: var(--tf-card);
        border-radius: 12px;
        padding: 24px;
        border: 1px solid rgba(255,255,255,0.06);
        transition: border-color 0.2s;
        cursor: pointer;
    }
    .machine-card:hover { border-color: rgba(212,168,67,0.3); box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
    .machine-name {
        font-size: 18px; font-weight: 700; margin: 0 0 16px 0; color: var(--tf-text);
    }
    .stat-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid rgba(255,255,255,0.04);
        font-size: 14px;
    }
    .stat-row:last-child { border-bottom: none; }
    .stat-label { color: var(--tf-muted); }
    .stat-value { font-weight: 600; color: var(--tf-text); }
    .utilization-bar {
        width: 100%; height: 8px; background: rgba(255,255,255,0.06);
        border-radius: 4px; margin-top: 16px; overflow: hidden;
    }
    .utilization-fill {
        height: 100%; border-radius: 4px; transition: width 0.5s;
    }
    .util-high { background: #22c55e; }
    .util-mid { background: var(--tf-gold); }
    .util-low { background: #ef4444; }
    .loading { text-align: center; padding: 60px; color: var(--tf-muted); }
    .empty-state {
        text-align: center; padding: 60px 20px; color: var(--tf-muted);
    }
    .empty-state h3 { font-size: 18px; margin-bottom: 8px; color: var(--tf-text); }

/* ── Responsive ── */
@media (max-width: 768px) {
    .page-header h1 { font-size: 22px; }
    .toolbar { flex-direction: column; align-items: stretch; }
    .toolbar input[type="text"] { width: 100%; }
    .stat-row { grid-template-columns: 1fr 1fr; gap: 10px; }
    .machine-grid { grid-template-columns: 1fr; }
}
@media (max-width: 480px) {
    .stat-row { grid-template-columns: 1fr; }
    .toolbar { gap: 8px; }
    .machine-grid { grid-template-columns: 1fr; }
}
</style>

<div class="machines-container">
    <div class="page-header">
        <h1>Machine Dashboard</h1>
        <p>Monitor machine utilization and queue status</p>
    </div>
    <div class="toolbar">
        <a href="/schedule" class="btn-outline">View Schedule</a>
    </div>
    <div id="machineGrid" class="loading">Loading machines...</div>
</div>

<script>
async function loadMachines() {
    const wrap = document.getElementById('machineGrid');
    try {
        const resp = await fetch('/api/gantt/machines');
        const data = await resp.json();
        const machines = Array.isArray(data) ? data : (data.machines || []);
        if (!machines.length) {
            wrap.innerHTML = '<div class="empty-state"><h3>No machines configured</h3><p>Machine data will appear here once configured.</p></div>';
            wrap.className = '';
            return;
        }
        wrap.className = 'machine-grid';
        wrap.innerHTML = machines.map(m => {
            const util = m.utilization != null ? Math.round(m.utilization) : 0;
            const utilClass = util >= 70 ? 'util-high' : util >= 40 ? 'util-mid' : 'util-low';
            var machineName = m.name || m.machine_name || 'Unknown';
            return '<div class="machine-card" onclick="window.location.href=\'/work-station/' + encodeURIComponent(machineName) + '\'">' +
                '<h3 class="machine-name">' + machineName + '</h3>' +
                '<div class="stat-row"><span class="stat-label">Active Jobs</span><span class="stat-value">' + (m.active_jobs || m.active || 0) + '</span></div>' +
                '<div class="stat-row"><span class="stat-label">Queued</span><span class="stat-value">' + (m.queued || m.queue_count || 0) + '</span></div>' +
                '<div class="stat-row"><span class="stat-label">Completed</span><span class="stat-value">' + (m.completed || m.completed_count || 0) + '</span></div>' +
                '<div class="stat-row"><span class="stat-label">Utilization</span><span class="stat-value">' + util + '%</span></div>' +
                '<div class="utilization-bar"><div class="utilization-fill ' + utilClass + '" style="width:' + util + '%"></div></div>' +
                '</div>';
        }).join('');
    } catch (err) {
        wrap.innerHTML = '<div class="empty-state"><h3>Unable to load machines</h3><p>' + err.message + '</p></div>';
        wrap.className = '';
    }
}

loadMachines();
</script>
"""
