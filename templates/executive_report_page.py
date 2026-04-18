"""
TitanForge v4 — Executive Summary
=====================================
High-level business performance metrics and pipeline overview.
"""

EXECUTIVE_REPORT_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a;
        --tf-card: #1e293b;
        --tf-text: #e2e8f0;
        --tf-muted: #94a3b8;
        --tf-gold: #d4a843;
        --tf-blue: #3b82f6;
    }
    .exec-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 24px 32px;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        color: var(--tf-text);
    }
    .page-header { margin-bottom: 32px; }
    .page-header h1 {
        font-size: 28px; font-weight: 800; margin: 0 0 6px 0; color: var(--tf-text);
    }
    .page-header p { font-size: 14px; color: var(--tf-muted); margin: 0; }
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 20px;
        margin-bottom: 32px;
    }
    .kpi-card {
        background: var(--tf-card);
        border-radius: 12px;
        padding: 24px;
        border: 1px solid rgba(255,255,255,0.06);
        text-align: center;
        cursor: pointer;
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    .kpi-card:hover { border-color: rgba(212,168,67,0.3); box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
    .kpi-value {
        font-size: 36px; font-weight: 800; color: var(--tf-gold); margin-bottom: 6px;
    }
    .kpi-label {
        font-size: 13px; font-weight: 600; color: var(--tf-muted); text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .section-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
    }
    @media (max-width: 900px) { .section-grid { grid-template-columns: 1fr; } }
    .section-card {
        background: var(--tf-card);
        border-radius: 12px;
        padding: 24px;
        border: 1px solid rgba(255,255,255,0.06);
    }
    .section-card h2 {
        font-size: 16px; font-weight: 700; margin: 0 0 20px 0; color: var(--tf-text);
    }
    .stat-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.04);
        font-size: 14px; cursor: pointer; border-radius: 6px; padding: 10px 8px;
        transition: background 0.15s;
    }
    .stat-row:hover { background: rgba(255,255,255,0.04); }
    .stat-row:last-child { border-bottom: none; }
    .stat-label { color: var(--tf-muted); }
    .stat-value { font-weight: 700; color: var(--tf-text); }
    .pipeline-table {
        width: 100%; border-collapse: collapse; font-size: 14px;
    }
    .pipeline-table thead th {
        background: #1a2744;
        padding: 12px 14px;
        text-align: left;
        font-weight: 700;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--tf-muted);
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .pipeline-table tbody tr {
        cursor: pointer;
        transition: background 0.15s;
    }
    .pipeline-table tbody tr:hover { background: rgba(255,255,255,0.04); }
    .pipeline-table tbody td {
        padding: 10px 14px;
        border-bottom: 1px solid rgba(255,255,255,0.04);
    }
    .stage-badge {
        display: inline-block; padding: 3px 8px; border-radius: 6px;
        font-size: 11px; font-weight: 600;
    }
    .stage-active { background: rgba(59,130,246,0.2); color: #60a5fa; }
    .stage-complete { background: rgba(34,197,94,0.2); color: #4ade80; }
    .stage-pending { background: rgba(212,168,67,0.2); color: #d4a843; }
    .loading { text-align: center; padding: 40px; color: var(--tf-muted); }
</style>

<div class="exec-container">
    <div class="page-header">
        <h1>Executive Summary</h1>
        <p>High-level business performance metrics</p>
    </div>

    <div class="kpi-grid">
        <div class="kpi-card" onclick="window.location.href='/projects'">
            <div class="kpi-value" id="kpiActiveProjects">—</div>
            <div class="kpi-label">Active Projects</div>
        </div>
        <div class="kpi-card" onclick="window.location.href='/projects'">
            <div class="kpi-value" id="kpiRevenue">—</div>
            <div class="kpi-label">Revenue Pipeline</div>
        </div>
        <div class="kpi-card" onclick="window.location.href='/reports/production'">
            <div class="kpi-value" id="kpiCycleTime">—</div>
            <div class="kpi-label">Avg Cycle Time</div>
        </div>
        <div class="kpi-card" onclick="window.location.href='/shipping'">
            <div class="kpi-value" id="kpiOnTime">—</div>
            <div class="kpi-label">On-Time Delivery %</div>
        </div>
    </div>

    <div class="section-grid">
        <div class="section-card">
            <h2>Production Stats</h2>
            <div id="productionStats" class="loading">Loading...</div>
        </div>
        <div class="section-card">
            <h2>Project Pipeline</h2>
            <div id="pipelineSummary" class="loading">Loading...</div>
        </div>
    </div>
</div>

<script>
function fmtCurrency(v) {
    if (v == null) return '$0';
    if (v >= 1000000) return '$' + (v / 1000000).toFixed(1) + 'M';
    if (v >= 1000) return '$' + (v / 1000).toFixed(0) + 'K';
    return '$' + Number(v).toLocaleString();
}

async function loadData() {
    // Load projects
    let projects = [];
    try {
        const resp = await fetch('/api/projects/full');
        const data = await resp.json();
        projects = Array.isArray(data) ? data : (data.projects || []);
    } catch (e) { console.error('projects error', e); }

    // KPIs from projects
    const active = projects.filter(p => {
        const s = (p.stage || p.status || '').toLowerCase();
        return !s.includes('complete') && !s.includes('cancel');
    });
    document.getElementById('kpiActiveProjects').textContent = active.length;

    const revenue = projects.reduce((sum, p) => sum + (p.sell_price || p.sellPrice || p.total_price || 0), 0);
    document.getElementById('kpiRevenue').textContent = fmtCurrency(revenue);

    // Cycle time and on-time — calculated or from production stats
    let prodData = null;
    try {
        const resp2 = await fetch('/api/reports/production');
        prodData = await resp2.json();
    } catch (e) { console.error('production error', e); }

    if (prodData) {
        const ct = prodData.avg_cycle_time || prodData.avgCycleTime;
        document.getElementById('kpiCycleTime').textContent = ct != null ? ct + 'd' : '—';
        const ot = prodData.on_time_pct || prodData.onTimeDelivery;
        document.getElementById('kpiOnTime').textContent = ot != null ? Math.round(ot) + '%' : '—';

        // Production stats section
        let statsHtml = '';
        const statsMap = {
            'Total WOs': prodData.total_work_orders || prodData.totalWOs,
            'Completed Today': prodData.completed_today || prodData.completedToday,
            'In Progress': prodData.in_progress || prodData.inProgress,
            'Avg Throughput': prodData.avg_throughput || prodData.avgThroughput,
            'Defect Rate': prodData.defect_rate != null ? prodData.defect_rate + '%' : (prodData.defectRate != null ? prodData.defectRate + '%' : null),
        };
        for (const [label, val] of Object.entries(statsMap)) {
            if (val != null) {
                statsHtml += '<div class="stat-row" onclick="window.location.href=\'/reports/production\'"><span class="stat-label">' + label + '</span><span class="stat-value">' + val + '</span></div>';
            }
        }
        document.getElementById('productionStats').innerHTML = statsHtml || '<div style="color:var(--tf-muted);text-align:center;padding:20px">No production data available</div>';
    } else {
        document.getElementById('kpiCycleTime').textContent = '—';
        document.getElementById('kpiOnTime').textContent = '—';
        document.getElementById('productionStats').innerHTML = '<div style="color:var(--tf-muted);text-align:center;padding:20px">Unable to load production stats</div>';
    }

    // Pipeline summary
    if (projects.length) {
        const stages = {};
        projects.forEach(p => {
            const s = p.stage || p.status || 'Unknown';
            if (!stages[s]) stages[s] = { count: 0, value: 0 };
            stages[s].count++;
            stages[s].value += (p.sell_price || p.sellPrice || p.total_price || 0);
        });
        let html = '<table class="pipeline-table"><thead><tr><th>Stage</th><th>Projects</th><th>Value</th></tr></thead><tbody>';
        for (const [stage, info] of Object.entries(stages)) {
            const cls = stage.toLowerCase().includes('complete') ? 'stage-complete' :
                        stage.toLowerCase().includes('draft') || stage.toLowerCase().includes('quote') ? 'stage-pending' : 'stage-active';
            html += '<tr onclick="window.location.href=\'/projects?stage=' + encodeURIComponent(stage) + '\'"><td><span class="stage-badge ' + cls + '">' + stage + '</span></td>' +
                '<td>' + info.count + '</td><td>' + fmtCurrency(info.value) + '</td></tr>';
        }
        html += '</tbody></table>';
        document.getElementById('pipelineSummary').innerHTML = html;
    } else {
        document.getElementById('pipelineSummary').innerHTML = '<div style="color:var(--tf-muted);text-align:center;padding:20px">No projects found</div>';
    }
}

loadData();
</script>
"""
