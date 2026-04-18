"""
TitanForge v4 -- Safety Metrics Dashboard
============================================
TRIR, DART, EMR rates, days since last incident, trending charts, safety scorecards.
"""

SAFETY_METRICS_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a; --tf-card: #1e293b; --tf-text: #e2e8f0;
        --tf-muted: #94a3b8; --tf-gold: #d4a843; --tf-blue: #3b82f6;
        --tf-green: #10b981; --tf-red: #ef4444; --tf-orange: #f59e0b;
    }
    .metrics-container {
        max-width: 1400px; margin: 0 auto; padding: 24px 32px;
        font-family: 'Inter', 'Segoe UI', sans-serif; color: var(--tf-text);
    }
    .page-header { margin-bottom: 28px; }
    .page-header h1 { font-size: 28px; font-weight: 800; margin: 0 0 6px 0; }
    .page-header p { font-size: 14px; color: var(--tf-muted); margin: 0; }

    .toolbar {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 24px; flex-wrap: wrap; gap: 12px;
    }
    .toolbar select {
        background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06);
        border-radius: 8px; padding: 10px 16px; color: var(--tf-text); font-size: 14px;
    }
    .toolbar select:focus { outline: none; border-color: var(--tf-blue); }
    .btn { padding: 10px 20px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
    .btn-primary { background: var(--tf-gold); color: #0f172a; }
    .btn-secondary { background: var(--tf-card); color: var(--tf-text); border: 1px solid rgba(255,255,255,0.06); }

    /* Big Counter */
    .big-counter-row {
        display: grid; grid-template-columns: 1fr 1fr 1fr;
        gap: 20px; margin-bottom: 24px;
    }
    .days-counter {
        background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(16,185,129,0.03));
        border: 2px solid rgba(16,185,129,0.2); border-radius: 16px;
        padding: 32px; text-align: center;
    }
    .days-counter .big-number { font-size: 72px; font-weight: 900; color: var(--tf-green); line-height: 1; }
    .days-counter .counter-label { font-size: 14px; font-weight: 600; color: var(--tf-green); margin-top: 4px; }
    .days-counter .sub { font-size: 12px; color: var(--tf-muted); margin-top: 8px; }

    /* KPI Cards */
    .kpi-row {
        display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 16px; margin-bottom: 24px;
    }
    .kpi-card {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06);
        padding: 24px; text-align: center;
    }
    .kpi-card .kpi-label { font-size: 12px; color: var(--tf-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px; }
    .kpi-card .kpi-value { font-size: 36px; font-weight: 900; margin-bottom: 4px; }
    .kpi-card .kpi-target { font-size: 12px; color: var(--tf-muted); }
    .kpi-card .kpi-trend { font-size: 13px; font-weight: 700; margin-top: 8px; }
    .trend-up { color: var(--tf-red); }
    .trend-down { color: var(--tf-green); }
    .trend-flat { color: var(--tf-muted); }

    /* Chart Placeholders */
    .charts-row {
        display: grid; grid-template-columns: 1fr 1fr;
        gap: 20px; margin-bottom: 24px;
    }
    .chart-card {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06);
        padding: 24px;
    }
    .chart-card h3 { font-size: 16px; font-weight: 700; margin: 0 0 16px 0; }
    .chart-area {
        height: 220px; background: var(--tf-bg); border-radius: 8px;
        display: flex; align-items: center; justify-content: center;
        color: var(--tf-muted); font-size: 14px; border: 1px solid rgba(255,255,255,0.04);
    }
    .mini-bar-chart { display: flex; align-items: flex-end; gap: 4px; height: 160px; padding-top: 20px; }
    .mini-bar {
        flex: 1; border-radius: 4px 4px 0 0; min-width: 20px;
        transition: height 0.3s; position: relative;
    }
    .mini-bar .bar-label {
        position: absolute; bottom: -20px; left: 50%; transform: translateX(-50%);
        font-size: 10px; color: var(--tf-muted); white-space: nowrap;
    }

    /* Scorecards */
    .scorecard-section { margin-bottom: 24px; }
    .scorecard-section h3 { font-size: 18px; font-weight: 700; margin-bottom: 16px; }
    .scorecards {
        display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 16px;
    }
    .scorecard {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06);
        padding: 20px;
    }
    .scorecard-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
    .scorecard-header h4 { font-size: 14px; font-weight: 700; margin: 0; }
    .score-circle {
        width: 48px; height: 48px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 16px; font-weight: 900;
    }
    .score-good { background: rgba(16,185,129,0.15); color: var(--tf-green); border: 2px solid var(--tf-green); }
    .score-warning { background: rgba(245,158,11,0.15); color: var(--tf-orange); border: 2px solid var(--tf-orange); }
    .score-bad { background: rgba(239,68,68,0.15); color: var(--tf-red); border: 2px solid var(--tf-red); }
    .scorecard-metrics { display: flex; flex-direction: column; gap: 8px; }
    .sc-metric { display: flex; justify-content: space-between; font-size: 13px; }
    .sc-metric .sc-label { color: var(--tf-muted); }
    .sc-metric .sc-value { font-weight: 600; }

    @media (max-width: 900px) {
        .big-counter-row { grid-template-columns: 1fr; }
        .charts-row { grid-template-columns: 1fr; }
    }
</style>

<div class="metrics-container">
    <div class="page-header">
        <h1>Safety Metrics Dashboard</h1>
        <p>Track OSHA rates, safety trends, and performance scorecards across all projects</p>
    </div>

    <div class="toolbar">
        <div style="display:flex;gap:10px;">
            <select id="periodFilter" onchange="loadMetrics()">
                <option value="ytd">Year to Date</option>
                <option value="12m">Last 12 Months</option>
                <option value="6m">Last 6 Months</option>
                <option value="3m">Last 3 Months</option>
            </select>
            <select id="projectFilter" onchange="loadMetrics()">
                <option value="">All Projects</option>
            </select>
        </div>
        <button class="btn btn-secondary" onclick="exportMetrics()">Export Report</button>
    </div>

    <div class="big-counter-row">
        <div class="days-counter">
            <div class="big-number" id="daysSafe">0</div>
            <div class="counter-label">Days Without Recordable</div>
            <div class="sub">Goal: 365 days</div>
        </div>
        <div class="days-counter" style="border-color:rgba(59,130,246,0.2);background:linear-gradient(135deg,rgba(59,130,246,0.1),rgba(59,130,246,0.03))">
            <div class="big-number" style="color:var(--tf-blue)" id="totalHours">0</div>
            <div class="counter-label" style="color:var(--tf-blue)">Total Man-Hours</div>
            <div class="sub">This period</div>
        </div>
        <div class="days-counter" style="border-color:rgba(212,168,67,0.2);background:linear-gradient(135deg,rgba(212,168,67,0.1),rgba(212,168,67,0.03))">
            <div class="big-number" style="color:var(--tf-gold)" id="safetyScore">0</div>
            <div class="counter-label" style="color:var(--tf-gold)">Safety Score</div>
            <div class="sub">Out of 100</div>
        </div>
    </div>

    <div class="kpi-row">
        <div class="kpi-card">
            <div class="kpi-label">TRIR</div>
            <div class="kpi-value" style="color:var(--tf-green)" id="kpi-trir">0.00</div>
            <div class="kpi-target">Target: &lt; 3.0</div>
            <div class="kpi-trend trend-down" id="trend-trir">--</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">DART Rate</div>
            <div class="kpi-value" style="color:var(--tf-blue)" id="kpi-dart">0.00</div>
            <div class="kpi-target">Target: &lt; 2.0</div>
            <div class="kpi-trend trend-down" id="trend-dart">--</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">EMR</div>
            <div class="kpi-value" style="color:var(--tf-gold)" id="kpi-emr">0.00</div>
            <div class="kpi-target">Target: &lt; 1.0</div>
            <div class="kpi-trend trend-flat" id="trend-emr">--</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Near Miss Ratio</div>
            <div class="kpi-value" style="color:var(--tf-orange)" id="kpi-nearmiss">0:0</div>
            <div class="kpi-target">Target: &gt; 10:1</div>
            <div class="kpi-trend trend-flat" id="trend-nearmiss">--</div>
        </div>
    </div>

    <div class="charts-row">
        <div class="chart-card">
            <h3>Incident Trend (Monthly)</h3>
            <div class="mini-bar-chart" id="trendChart"></div>
        </div>
        <div class="chart-card">
            <h3>Incidents by Type</h3>
            <div class="chart-area" id="typeChart">Chart data loading...</div>
        </div>
    </div>

    <div class="charts-row">
        <div class="chart-card">
            <h3>TRIR Trend</h3>
            <div class="chart-area" id="trirChart">TRIR trend loading...</div>
        </div>
        <div class="chart-card">
            <h3>Near Miss vs Recordable</h3>
            <div class="chart-area" id="ratioChart">Ratio data loading...</div>
        </div>
    </div>

    <div class="scorecard-section">
        <h3>Safety Scorecards by Project</h3>
        <div class="scorecards" id="scorecardGrid"></div>
        <div class="empty-state" id="emptyScorecard" style="display:none;">
            <div class="icon">&#128202;</div>
            <h3>No Scorecard Data</h3>
            <p>Safety scorecards will appear as projects accumulate safety data.</p>
        </div>
    </div>
</div>

<script>
    let metrics = {};

    async function loadMetrics() {
        const period = document.getElementById('periodFilter').value;
        const project = document.getElementById('projectFilter').value;
        try {
            const resp = await fetch(`/api/safety/metrics?period=${period}&project=${encodeURIComponent(project)}`);
            metrics = await resp.json();
            renderMetrics();
        } catch(e) {
            console.error('Failed to load metrics:', e);
            metrics = {};
            renderMetrics();
        }
    }

    function renderMetrics() {
        document.getElementById('daysSafe').textContent = metrics.days_since_recordable || 0;
        document.getElementById('totalHours').textContent = (metrics.total_hours || 0).toLocaleString();
        document.getElementById('safetyScore').textContent = metrics.safety_score || 0;

        const trir = metrics.trir || 0;
        document.getElementById('kpi-trir').textContent = trir.toFixed(2);
        document.getElementById('kpi-trir').style.color = trir < 3 ? 'var(--tf-green)' : trir < 5 ? 'var(--tf-orange)' : 'var(--tf-red)';
        document.getElementById('trend-trir').textContent = metrics.trir_trend || '--';

        const dart = metrics.dart || 0;
        document.getElementById('kpi-dart').textContent = dart.toFixed(2);
        document.getElementById('kpi-dart').style.color = dart < 2 ? 'var(--tf-green)' : dart < 4 ? 'var(--tf-orange)' : 'var(--tf-red)';
        document.getElementById('trend-dart').textContent = metrics.dart_trend || '--';

        const emr = metrics.emr || 0;
        document.getElementById('kpi-emr').textContent = emr.toFixed(2);
        document.getElementById('kpi-emr').style.color = emr < 1 ? 'var(--tf-green)' : emr < 1.2 ? 'var(--tf-orange)' : 'var(--tf-red)';
        document.getElementById('trend-emr').textContent = metrics.emr_trend || '--';

        const nmRatio = metrics.near_miss_ratio || '0:0';
        document.getElementById('kpi-nearmiss').textContent = nmRatio;

        renderTrendChart();
        renderScorecards();
    }

    function renderTrendChart() {
        const chart = document.getElementById('trendChart');
        const monthly = metrics.monthly_incidents || [];
        if (monthly.length === 0) { chart.innerHTML = '<div style="color:var(--tf-muted);font-size:13px;width:100%;text-align:center;">No trend data</div>'; return; }
        const maxVal = Math.max(...monthly.map(m => m.count), 1);
        chart.innerHTML = monthly.map(m => {
            const height = Math.max((m.count / maxVal) * 140, 4);
            const color = m.count === 0 ? 'var(--tf-green)' : m.count <= 2 ? 'var(--tf-orange)' : 'var(--tf-red)';
            return `<div class="mini-bar" style="height:${height}px;background:${color}"><span class="bar-label">${m.month || ''}</span></div>`;
        }).join('');
    }

    function renderScorecards() {
        const grid = document.getElementById('scorecardGrid');
        const empty = document.getElementById('emptyScorecard');
        const scorecards = metrics.scorecards || [];
        if (scorecards.length === 0) { grid.innerHTML = ''; empty.style.display = 'block'; return; }
        empty.style.display = 'none';
        grid.innerHTML = scorecards.map(sc => {
            const score = sc.score || 0;
            const scoreCls = score >= 80 ? 'score-good' : score >= 60 ? 'score-warning' : 'score-bad';
            return `
            <div class="scorecard">
                <div class="scorecard-header">
                    <h4>${sc.project_name || ''}</h4>
                    <div class="score-circle ${scoreCls}">${score}</div>
                </div>
                <div class="scorecard-metrics">
                    <div class="sc-metric"><span class="sc-label">Recordables</span><span class="sc-value">${sc.recordables || 0}</span></div>
                    <div class="sc-metric"><span class="sc-label">Near Misses</span><span class="sc-value">${sc.near_misses || 0}</span></div>
                    <div class="sc-metric"><span class="sc-label">Man-Hours</span><span class="sc-value">${(sc.hours || 0).toLocaleString()}</span></div>
                    <div class="sc-metric"><span class="sc-label">TRIR</span><span class="sc-value">${(sc.trir || 0).toFixed(2)}</span></div>
                    <div class="sc-metric"><span class="sc-label">JHA Compliance</span><span class="sc-value">${sc.jha_compliance || 0}%</span></div>
                </div>
            </div>`;
        }).join('');
    }

    function exportMetrics() { window.open('/api/safety/metrics/export?format=pdf', '_blank'); }

    document.addEventListener('DOMContentLoaded', loadMetrics);
</script>
"""
