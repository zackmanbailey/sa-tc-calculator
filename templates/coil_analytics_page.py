"""
TitanForge v4 -- Coil Yield Analytics Dashboard
=================================================
Comprehensive analytics for coil yield tracking, waste trends,
operator accuracy rankings, and cost impact analysis.
"""

COIL_ANALYTICS_HTML = r"""
<style>
    :root {
        --ca-bg: #0f172a;
        --ca-card: #1e293b;
        --ca-border: #334155;
        --ca-text: #e2e8f0;
        --ca-muted: #94a3b8;
        --ca-blue: #3b82f6;
        --ca-green: #10b981;
        --ca-amber: #f59e0b;
        --ca-red: #ef4444;
    }

    .ca-container {
        max-width: 1440px; margin: 0 auto; padding: 24px 32px;
        font-family: 'Inter', 'Segoe UI', sans-serif; color: var(--ca-text);
    }

    /* ---------- Header ---------- */
    .ca-header {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 28px; flex-wrap: wrap; gap: 16px;
    }
    .ca-header h1 { font-size: 28px; font-weight: 800; margin: 0; }
    .ca-header-actions { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }

    .ca-range-btn {
        padding: 7px 16px; border: 1px solid var(--ca-border); border-radius: 8px;
        background: transparent; color: var(--ca-muted); font-size: 13px;
        cursor: pointer; transition: all .2s; font-family: inherit;
    }
    .ca-range-btn:hover { border-color: var(--ca-blue); color: var(--ca-text); }
    .ca-range-btn.active { background: var(--ca-blue); color: #fff; border-color: var(--ca-blue); }

    .ca-export-btn {
        padding: 8px 18px; border: none; border-radius: 8px;
        background: var(--ca-green); color: #fff; font-size: 13px; font-weight: 600;
        cursor: pointer; transition: opacity .2s; font-family: inherit;
    }
    .ca-export-btn:hover { opacity: .85; }

    /* ---------- KPI Cards ---------- */
    .ca-kpi-row {
        display: grid; grid-template-columns: repeat(4, 1fr);
        gap: 16px; margin-bottom: 28px;
    }
    .ca-kpi-card {
        background: var(--ca-card); border: 1px solid var(--ca-border);
        border-radius: 12px; padding: 20px 24px;
        transition: border-color .2s, transform .15s;
    }
    .ca-kpi-card:hover { border-color: var(--ca-blue); transform: translateY(-2px); }
    .ca-kpi-card .ca-kpi-label {
        font-size: 12px; color: var(--ca-muted); text-transform: uppercase;
        letter-spacing: .5px; margin-bottom: 8px;
    }
    .ca-kpi-card .ca-kpi-value { font-size: 28px; font-weight: 800; }
    .ca-kpi-card .ca-kpi-sub { font-size: 12px; color: var(--ca-muted); margin-top: 4px; }
    .ca-kpi-card.blue .ca-kpi-value { color: var(--ca-blue); }
    .ca-kpi-card.green .ca-kpi-value { color: var(--ca-green); }
    .ca-kpi-card.amber .ca-kpi-value { color: var(--ca-amber); }
    .ca-kpi-card.red .ca-kpi-value { color: var(--ca-red); }

    /* ---------- Two-Column Layout ---------- */
    .ca-grid-2 {
        display: grid; grid-template-columns: 1fr 1fr;
        gap: 20px; margin-bottom: 28px;
    }

    /* ---------- Panels / Cards ---------- */
    .ca-panel {
        background: var(--ca-card); border: 1px solid var(--ca-border);
        border-radius: 12px; overflow: hidden;
    }
    .ca-panel-header {
        padding: 16px 24px; border-bottom: 1px solid var(--ca-border);
        font-weight: 700; font-size: 15px; display: flex;
        justify-content: space-between; align-items: center;
    }
    .ca-panel-body { padding: 20px 24px; }

    /* ---------- Bar Chart (Yield by Coil Type) ---------- */
    .ca-bar-chart { display: flex; align-items: flex-end; gap: 24px; height: 220px; padding-top: 12px; }
    .ca-bar-group { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6px; height: 100%; justify-content: flex-end; }
    .ca-bar-pair { display: flex; gap: 4px; align-items: flex-end; width: 100%; justify-content: center; }
    .ca-bar {
        width: 28px; border-radius: 4px 4px 0 0; min-height: 4px;
        transition: opacity .2s; position: relative; cursor: pointer;
    }
    .ca-bar:hover { opacity: .8; }
    .ca-bar.estimated { background: var(--ca-blue); }
    .ca-bar.actual { background: var(--ca-green); }
    .ca-bar-label { font-size: 11px; color: var(--ca-muted); text-align: center; white-space: nowrap; }
    .ca-bar-tooltip {
        display: none; position: absolute; bottom: 100%; left: 50%; transform: translateX(-50%);
        background: #0f172a; color: var(--ca-text); padding: 4px 10px; border-radius: 6px;
        font-size: 11px; white-space: nowrap; margin-bottom: 6px; border: 1px solid var(--ca-border);
        z-index: 10;
    }
    .ca-bar:hover .ca-bar-tooltip { display: block; }
    .ca-chart-legend { display: flex; gap: 20px; margin-top: 12px; justify-content: center; }
    .ca-legend-item { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--ca-muted); }
    .ca-legend-dot { width: 10px; height: 10px; border-radius: 3px; }

    /* ---------- SVG Line Chart (Waste Trends) ---------- */
    .ca-line-chart-wrap { position: relative; }
    .ca-line-chart-wrap svg { width: 100%; height: 200px; }
    .ca-line-chart-wrap .grid-line { stroke: var(--ca-border); stroke-width: 0.5; }
    .ca-line-chart-wrap .trend-line { fill: none; stroke: var(--ca-amber); stroke-width: 2.5; stroke-linecap: round; stroke-linejoin: round; }
    .ca-line-chart-wrap .trend-area { fill: url(#wasteGradient); opacity: 0.3; }
    .ca-line-chart-wrap .dot { fill: var(--ca-amber); cursor: pointer; transition: r .15s; }
    .ca-line-chart-wrap .dot:hover { r: 6; }
    .ca-line-chart-wrap .axis-label { fill: var(--ca-muted); font-size: 10px; font-family: 'Inter', sans-serif; }
    .ca-svg-tooltip {
        display: none; position: absolute; background: #0f172a; color: var(--ca-text);
        padding: 6px 12px; border-radius: 6px; font-size: 12px; border: 1px solid var(--ca-border);
        pointer-events: none; z-index: 20;
    }

    /* ---------- Tables ---------- */
    .ca-table { width: 100%; border-collapse: collapse; font-size: 13px; }
    .ca-table th {
        text-align: left; padding: 10px 14px; border-bottom: 2px solid var(--ca-border);
        color: var(--ca-muted); font-weight: 600; font-size: 11px; text-transform: uppercase;
        letter-spacing: .5px; cursor: pointer; user-select: none; white-space: nowrap;
    }
    .ca-table th:hover { color: var(--ca-text); }
    .ca-table th .sort-arrow { margin-left: 4px; font-size: 10px; }
    .ca-table td { padding: 10px 14px; border-bottom: 1px solid var(--ca-border); vertical-align: middle; }
    .ca-table tr:hover { background: rgba(59,130,246,0.05); }

    /* ---------- Badges ---------- */
    .ca-badge {
        display: inline-block; padding: 2px 10px; border-radius: 6px;
        font-size: 11px; font-weight: 600; text-transform: uppercase;
    }
    .ca-badge-green { background: rgba(16,185,129,0.15); color: var(--ca-green); }
    .ca-badge-amber { background: rgba(245,158,11,0.15); color: var(--ca-amber); }
    .ca-badge-red { background: rgba(239,68,68,0.15); color: var(--ca-red); }
    .ca-badge-blue { background: rgba(59,130,246,0.15); color: var(--ca-blue); }
    .ca-badge-muted { background: rgba(148,163,184,0.15); color: var(--ca-muted); }

    .ca-yield-green { color: var(--ca-green); }
    .ca-yield-amber { color: var(--ca-amber); }
    .ca-yield-red { color: var(--ca-red); }

    .ca-trend-up { color: var(--ca-green); }
    .ca-trend-down { color: var(--ca-red); }
    .ca-trend-flat { color: var(--ca-muted); }

    .ca-gold-star { color: #f59e0b; margin-left: 6px; }

    /* ---------- Search / Filter ---------- */
    .ca-search-bar {
        display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; align-items: center;
    }
    .ca-search-input {
        flex: 1; min-width: 200px; padding: 9px 14px; border: 1px solid var(--ca-border);
        border-radius: 8px; background: var(--ca-bg); color: var(--ca-text);
        font-size: 13px; font-family: inherit;
    }
    .ca-search-input::placeholder { color: var(--ca-muted); }
    .ca-search-input:focus { outline: none; border-color: var(--ca-blue); }

    /* ---------- Cost Impact ---------- */
    .ca-cost-grid {
        display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;
    }
    .ca-cost-item { text-align: center; }
    .ca-cost-item .ca-cost-val { font-size: 24px; font-weight: 800; margin-bottom: 4px; }
    .ca-cost-item .ca-cost-lbl { font-size: 12px; color: var(--ca-muted); }

    /* ---------- Toast ---------- */
    .ca-toast-container {
        position: fixed; bottom: 24px; right: 24px; z-index: 9999;
        display: flex; flex-direction: column; gap: 8px;
    }
    .ca-toast {
        padding: 12px 20px; border-radius: 10px; font-size: 13px; font-weight: 500;
        color: #fff; box-shadow: 0 8px 24px rgba(0,0,0,.3);
        animation: caToastIn .3s ease-out;
        display: flex; align-items: center; gap: 8px;
    }
    .ca-toast.success { background: var(--ca-green); }
    .ca-toast.error { background: var(--ca-red); }
    .ca-toast.info { background: var(--ca-blue); }
    @keyframes caToastIn { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
    @keyframes caToastOut { from { opacity: 1; } to { opacity: 0; transform: translateY(-10px); } }

    /* ---------- Loading Skeleton ---------- */
    .ca-skeleton {
        background: linear-gradient(90deg, var(--ca-card) 25%, #263450 50%, var(--ca-card) 75%);
        background-size: 200% 100%; animation: caShimmer 1.5s infinite; border-radius: 8px;
    }
    @keyframes caShimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }

    /* ---------- Responsive ---------- */
    @media (max-width: 1024px) {
        .ca-kpi-row { grid-template-columns: repeat(2, 1fr); }
        .ca-grid-2 { grid-template-columns: 1fr; }
        .ca-cost-grid { grid-template-columns: 1fr; gap: 12px; }
    }
    @media (max-width: 640px) {
        .ca-container { padding: 16px; }
        .ca-header { flex-direction: column; align-items: flex-start; }
        .ca-kpi-row { grid-template-columns: 1fr 1fr; }
        .ca-bar-chart { gap: 12px; }
        .ca-bar { width: 18px; }
        .ca-table { font-size: 12px; }
        .ca-table th, .ca-table td { padding: 8px 8px; }
        .ca-cost-grid { grid-template-columns: 1fr; }
    }

    /* Scrollable table wrapper */
    .ca-table-wrap { overflow-x: auto; }
</style>

<div class="ca-container" id="caApp">

    <!-- ========== HEADER ========== -->
    <div class="ca-header">
        <h1>Coil Analytics</h1>
        <div class="ca-header-actions">
            <button class="ca-range-btn active" data-range="7" onclick="caSetRange(7)">Last 7 Days</button>
            <button class="ca-range-btn" data-range="30" onclick="caSetRange(30)">Last 30 Days</button>
            <button class="ca-range-btn" data-range="90" onclick="caSetRange(90)">Last 90 Days</button>
            <button class="ca-range-btn" data-range="0" onclick="caSetRange(0)">All Time</button>
            <button class="ca-export-btn" onclick="caExportCSV()">&#x2B07; Export CSV</button>
        </div>
    </div>

    <!-- ========== KPI SUMMARY CARDS ========== -->
    <div class="ca-kpi-row" id="caKpiRow">
        <div class="ca-kpi-card blue">
            <div class="ca-kpi-label">Total Coils Received</div>
            <div class="ca-kpi-value" id="kpiTotalCoils">--</div>
            <div class="ca-kpi-sub" id="kpiTotalWeight">-- lbs total</div>
        </div>
        <div class="ca-kpi-card" id="kpiYieldCard">
            <div class="ca-kpi-label">Average Yield %</div>
            <div class="ca-kpi-value" id="kpiAvgYield">--%</div>
            <div class="ca-kpi-sub">actual / estimated LFT</div>
        </div>
        <div class="ca-kpi-card red">
            <div class="ca-kpi-label">Total Waste %</div>
            <div class="ca-kpi-value" id="kpiWaste">--%</div>
            <div class="ca-kpi-sub" id="kpiWasteLft">-- LFT wasted</div>
        </div>
        <div class="ca-kpi-card blue">
            <div class="ca-kpi-label">Active Coils</div>
            <div class="ca-kpi-value" id="kpiActive">--</div>
            <div class="ca-kpi-sub">currently in inventory</div>
        </div>
    </div>

    <!-- ========== CHARTS ROW ========== -->
    <div class="ca-grid-2">

        <!-- Yield by Coil Type (Bar Chart) -->
        <div class="ca-panel">
            <div class="ca-panel-header">
                Yield by Coil Type
                <span style="font-size:12px;color:var(--ca-muted);font-weight:400;">Estimated vs Actual LFT</span>
            </div>
            <div class="ca-panel-body">
                <div class="ca-bar-chart" id="caBarChart"></div>
                <div class="ca-chart-legend">
                    <span class="ca-legend-item"><span class="ca-legend-dot" style="background:var(--ca-blue)"></span> Estimated LFT</span>
                    <span class="ca-legend-item"><span class="ca-legend-dot" style="background:var(--ca-green)"></span> Actual LFT</span>
                </div>
            </div>
        </div>

        <!-- Waste Trends Over Time (SVG Line Chart) -->
        <div class="ca-panel">
            <div class="ca-panel-header">
                Waste Trends Over Time
                <span style="font-size:12px;color:var(--ca-muted);font-weight:400;">% by period</span>
            </div>
            <div class="ca-panel-body">
                <div class="ca-line-chart-wrap" id="caLineChartWrap">
                    <div class="ca-svg-tooltip" id="caSvgTooltip"></div>
                    <svg id="caLineChart" viewBox="0 0 600 200" preserveAspectRatio="xMidYMid meet">
                        <defs>
                            <linearGradient id="wasteGradient" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="0%" stop-color="#f59e0b" stop-opacity="0.4"/>
                                <stop offset="100%" stop-color="#f59e0b" stop-opacity="0"/>
                            </linearGradient>
                        </defs>
                    </svg>
                </div>
            </div>
        </div>
    </div>

    <!-- ========== OPERATOR ACCURACY RANKINGS ========== -->
    <div class="ca-panel" style="margin-bottom:28px;">
        <div class="ca-panel-header">
            Operator Accuracy Rankings
            <span style="font-size:12px;color:var(--ca-muted);font-weight:400;">sorted by avg yield</span>
        </div>
        <div class="ca-panel-body">
            <div class="ca-table-wrap">
                <table class="ca-table" id="caOperatorTable">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Operator</th>
                            <th>Coils Processed</th>
                            <th>Avg Yield %</th>
                            <th>Best Yield %</th>
                            <th>Worst Yield %</th>
                            <th>Trend</th>
                        </tr>
                    </thead>
                    <tbody id="caOperatorBody"></tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- ========== COIL DETAIL TABLE ========== -->
    <div class="ca-panel" style="margin-bottom:28px;">
        <div class="ca-panel-header">
            Coil Detail
            <span style="font-size:12px;color:var(--ca-muted);font-weight:400;" id="caCoilCount"></span>
        </div>
        <div class="ca-panel-body">
            <div class="ca-search-bar">
                <input class="ca-search-input" id="caCoilSearch" type="text"
                       placeholder="Search by Coil ID, material, vendor..." oninput="caFilterCoils()">
            </div>
            <div class="ca-table-wrap">
                <table class="ca-table" id="caCoilTable">
                    <thead>
                        <tr>
                            <th data-col="coil_id" onclick="caSortCoils('coil_id')">Coil ID <span class="sort-arrow"></span></th>
                            <th data-col="material" onclick="caSortCoils('material')">Material <span class="sort-arrow"></span></th>
                            <th data-col="gauge" onclick="caSortCoils('gauge')">Gauge <span class="sort-arrow"></span></th>
                            <th data-col="width" onclick="caSortCoils('width')">Width <span class="sort-arrow"></span></th>
                            <th data-col="original_weight" onclick="caSortCoils('original_weight')">Orig Wt (lbs) <span class="sort-arrow"></span></th>
                            <th data-col="vendor_lft" onclick="caSortCoils('vendor_lft')">Vendor LFT <span class="sort-arrow"></span></th>
                            <th data-col="estimated_lft" onclick="caSortCoils('estimated_lft')">Est LFT <span class="sort-arrow"></span></th>
                            <th data-col="actual_lft" onclick="caSortCoils('actual_lft')">Actual LFT <span class="sort-arrow"></span></th>
                            <th data-col="yield_pct" onclick="caSortCoils('yield_pct')">Yield % <span class="sort-arrow"></span></th>
                            <th data-col="waste_pct" onclick="caSortCoils('waste_pct')">Waste % <span class="sort-arrow"></span></th>
                            <th data-col="status" onclick="caSortCoils('status')">Status <span class="sort-arrow"></span></th>
                            <th data-col="date_received" onclick="caSortCoils('date_received')">Date Received <span class="sort-arrow"></span></th>
                        </tr>
                    </thead>
                    <tbody id="caCoilBody"></tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- ========== COST IMPACT ========== -->
    <div class="ca-panel" style="margin-bottom:28px;">
        <div class="ca-panel-header">
            Cost Impact Analysis
            <span style="font-size:12px;color:var(--ca-muted);font-weight:400;">material cost & savings</span>
        </div>
        <div class="ca-panel-body">
            <div class="ca-cost-grid">
                <div class="ca-cost-item">
                    <div class="ca-cost-val" id="caCostTotal" style="color:var(--ca-blue);">$--</div>
                    <div class="ca-cost-lbl">Total Material Cost</div>
                </div>
                <div class="ca-cost-item">
                    <div class="ca-cost-val" id="caCostWaste" style="color:var(--ca-red);">$--</div>
                    <div class="ca-cost-lbl">Estimated Waste Cost</div>
                </div>
                <div class="ca-cost-item">
                    <div class="ca-cost-val" id="caCostSavings" style="color:var(--ca-green);">$--</div>
                    <div class="ca-cost-lbl">Savings Opportunity (at 98% yield)</div>
                </div>
            </div>
        </div>
    </div>

</div>

<!-- Toast container -->
<div class="ca-toast-container" id="caToastContainer"></div>

<script>
(function() {
    "use strict";

    /* ------------------------------------------------------------------ */
    /*  STATE                                                              */
    /* ------------------------------------------------------------------ */
    let caData = { coils: [], operator_stats: [], waste_trend: [], summary: {} };
    let caRange = 7;
    let caSortCol = 'date_received';
    let caSortAsc = false;
    let caFilteredCoils = [];

    /* ------------------------------------------------------------------ */
    /*  TOAST NOTIFICATIONS                                                */
    /* ------------------------------------------------------------------ */
    window.caToast = function(msg, type) {
        type = type || 'info';
        var container = document.getElementById('caToastContainer');
        var toast = document.createElement('div');
        toast.className = 'ca-toast ' + type;
        toast.innerHTML = (type === 'success' ? '&#x2714; ' : type === 'error' ? '&#x2716; ' : '&#x2139; ') + msg;
        container.appendChild(toast);
        setTimeout(function() {
            toast.style.animation = 'caToastOut .3s ease-in forwards';
            setTimeout(function() { toast.remove(); }, 300);
        }, 3000);
    };

    /* ------------------------------------------------------------------ */
    /*  DATE RANGE FILTER                                                  */
    /* ------------------------------------------------------------------ */
    window.caSetRange = function(days) {
        caRange = days;
        document.querySelectorAll('.ca-range-btn').forEach(function(b) {
            b.classList.toggle('active', parseInt(b.getAttribute('data-range')) === days);
        });
        caFetchData();
    };

    /* ------------------------------------------------------------------ */
    /*  FETCH DATA                                                         */
    /* ------------------------------------------------------------------ */
    function caFetchData() {
        var url = '/api/coils/lifecycle/analytics';
        if (caRange > 0) url += '?days=' + caRange;

        fetch(url)
            .then(function(r) { return r.json(); })
            .then(function(data) {
                caData = data;
                caRenderAll();
            })
            .catch(function(err) {
                console.error('Analytics fetch error:', err);
                caToast('Failed to load analytics data', 'error');
            });
    }

    /* ------------------------------------------------------------------ */
    /*  RENDER ALL                                                         */
    /* ------------------------------------------------------------------ */
    function caRenderAll() {
        caRenderKPIs();
        caRenderBarChart();
        caRenderLineChart();
        caRenderOperators();
        caRenderCoils();
        caRenderCostImpact();
    }

    /* ------------------------------------------------------------------ */
    /*  KPI CARDS                                                          */
    /* ------------------------------------------------------------------ */
    function caRenderKPIs() {
        var s = caData.summary || {};
        document.getElementById('kpiTotalCoils').textContent = caFmtNum(s.total_coils || 0);
        document.getElementById('kpiTotalWeight').textContent = caFmtNum(s.total_weight || 0) + ' lbs total';
        document.getElementById('kpiActive').textContent = caFmtNum(s.active_coils || 0);

        var avgY = s.avg_yield || 0;
        document.getElementById('kpiAvgYield').textContent = avgY.toFixed(1) + '%';
        var yieldCard = document.getElementById('kpiYieldCard');
        yieldCard.className = 'ca-kpi-card';
        if (avgY >= 95) yieldCard.classList.add('green');
        else if (avgY >= 90) yieldCard.classList.add('amber');
        else yieldCard.classList.add('red');

        var wasteP = s.total_waste_pct || 0;
        document.getElementById('kpiWaste').textContent = wasteP.toFixed(1) + '%';
        document.getElementById('kpiWasteLft').textContent = caFmtNum(s.total_waste_lft || 0) + ' LFT wasted';
    }

    /* ------------------------------------------------------------------ */
    /*  BAR CHART — Yield by Coil Type                                     */
    /* ------------------------------------------------------------------ */
    function caRenderBarChart() {
        var container = document.getElementById('caBarChart');
        container.innerHTML = '';

        /* Aggregate by coil type */
        var types = {};
        (caData.coils || []).forEach(function(c) {
            var t = c.material || 'Unknown';
            if (!types[t]) types[t] = { est: 0, act: 0 };
            types[t].est += (c.estimated_lft || 0);
            types[t].act += (c.actual_lft || 0);
        });

        var keys = Object.keys(types);
        if (keys.length === 0) {
            container.innerHTML = '<div style="color:var(--ca-muted);font-size:13px;text-align:center;width:100%;padding:40px 0;">No coil data available</div>';
            return;
        }

        var maxVal = 0;
        keys.forEach(function(k) { maxVal = Math.max(maxVal, types[k].est, types[k].act); });
        if (maxVal === 0) maxVal = 1;

        keys.forEach(function(k) {
            var group = document.createElement('div');
            group.className = 'ca-bar-group';

            var pair = document.createElement('div');
            pair.className = 'ca-bar-pair';

            var estBar = document.createElement('div');
            estBar.className = 'ca-bar estimated';
            estBar.style.height = Math.max((types[k].est / maxVal) * 180, 4) + 'px';
            estBar.innerHTML = '<span class="ca-bar-tooltip">Est: ' + caFmtNum(Math.round(types[k].est)) + ' LFT</span>';

            var actBar = document.createElement('div');
            actBar.className = 'ca-bar actual';
            actBar.style.height = Math.max((types[k].act / maxVal) * 180, 4) + 'px';
            actBar.innerHTML = '<span class="ca-bar-tooltip">Actual: ' + caFmtNum(Math.round(types[k].act)) + ' LFT</span>';

            pair.appendChild(estBar);
            pair.appendChild(actBar);
            group.appendChild(pair);

            var label = document.createElement('div');
            label.className = 'ca-bar-label';
            label.textContent = k;
            group.appendChild(label);

            container.appendChild(group);
        });
    }

    /* ------------------------------------------------------------------ */
    /*  LINE CHART — Waste Trends (SVG)                                    */
    /* ------------------------------------------------------------------ */
    function caRenderLineChart() {
        var svg = document.getElementById('caLineChart');
        /* Clear existing elements except defs */
        var defs = svg.querySelector('defs');
        svg.innerHTML = '';
        svg.appendChild(defs);

        var trend = caData.waste_trend || [];
        if (trend.length === 0) {
            var noData = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            noData.setAttribute('x', '300'); noData.setAttribute('y', '105');
            noData.setAttribute('text-anchor', 'middle');
            noData.setAttribute('class', 'axis-label');
            noData.setAttribute('font-size', '13');
            noData.textContent = 'No waste trend data available';
            svg.appendChild(noData);
            return;
        }

        var pad = { top: 20, right: 20, bottom: 30, left: 50 };
        var w = 600 - pad.left - pad.right;
        var h = 200 - pad.top - pad.bottom;

        var maxW = 0;
        trend.forEach(function(d) { if (d.waste_pct > maxW) maxW = d.waste_pct; });
        maxW = Math.max(maxW * 1.15, 1);

        /* Grid lines */
        for (var g = 0; g <= 4; g++) {
            var gy = pad.top + (h - (h * (g / 4)));
            var line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', pad.left); line.setAttribute('x2', 600 - pad.right);
            line.setAttribute('y1', gy); line.setAttribute('y2', gy);
            line.setAttribute('class', 'grid-line');
            svg.appendChild(line);

            var lbl = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            lbl.setAttribute('x', pad.left - 8); lbl.setAttribute('y', gy + 3);
            lbl.setAttribute('text-anchor', 'end'); lbl.setAttribute('class', 'axis-label');
            lbl.textContent = (maxW * g / 4).toFixed(1) + '%';
            svg.appendChild(lbl);
        }

        /* Build points */
        var points = [];
        trend.forEach(function(d, i) {
            var x = pad.left + (i / Math.max(trend.length - 1, 1)) * w;
            var y = pad.top + h - (d.waste_pct / maxW) * h;
            points.push({ x: x, y: y, data: d });
        });

        /* Area fill */
        var areaPath = 'M' + points[0].x + ',' + points[0].y;
        for (var a = 1; a < points.length; a++) areaPath += ' L' + points[a].x + ',' + points[a].y;
        areaPath += ' L' + points[points.length - 1].x + ',' + (pad.top + h);
        areaPath += ' L' + points[0].x + ',' + (pad.top + h) + ' Z';

        var area = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        area.setAttribute('d', areaPath);
        area.setAttribute('class', 'trend-area');
        svg.appendChild(area);

        /* Line */
        var linePath = 'M' + points[0].x + ',' + points[0].y;
        for (var l = 1; l < points.length; l++) linePath += ' L' + points[l].x + ',' + points[l].y;

        var trendLine = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        trendLine.setAttribute('d', linePath);
        trendLine.setAttribute('class', 'trend-line');
        svg.appendChild(trendLine);

        /* Dots + x-axis labels */
        var tooltip = document.getElementById('caSvgTooltip');
        points.forEach(function(p, i) {
            var dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            dot.setAttribute('cx', p.x); dot.setAttribute('cy', p.y); dot.setAttribute('r', 4);
            dot.setAttribute('class', 'dot');
            dot.addEventListener('mouseenter', function(e) {
                tooltip.style.display = 'block';
                tooltip.innerHTML = '<strong>' + (p.data.period || '') + '</strong><br>Waste: ' + p.data.waste_pct.toFixed(1) + '%';
                var rect = document.getElementById('caLineChartWrap').getBoundingClientRect();
                tooltip.style.left = (e.clientX - rect.left + 12) + 'px';
                tooltip.style.top = (e.clientY - rect.top - 40) + 'px';
            });
            dot.addEventListener('mouseleave', function() { tooltip.style.display = 'none'; });
            svg.appendChild(dot);

            /* X-axis label (show every other if many) */
            if (trend.length <= 12 || i % Math.ceil(trend.length / 10) === 0) {
                var xLbl = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                xLbl.setAttribute('x', p.x); xLbl.setAttribute('y', pad.top + h + 18);
                xLbl.setAttribute('text-anchor', 'middle'); xLbl.setAttribute('class', 'axis-label');
                xLbl.textContent = p.data.period || '';
                svg.appendChild(xLbl);
            }
        });
    }

    /* ------------------------------------------------------------------ */
    /*  OPERATOR RANKINGS TABLE                                            */
    /* ------------------------------------------------------------------ */
    function caRenderOperators() {
        var tbody = document.getElementById('caOperatorBody');
        tbody.innerHTML = '';

        var ops = (caData.operator_stats || []).slice();
        ops.sort(function(a, b) { return (b.avg_yield || 0) - (a.avg_yield || 0); });

        if (ops.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:var(--ca-muted);padding:24px;">No operator data available</td></tr>';
            return;
        }

        ops.forEach(function(op, idx) {
            var yieldClass = (op.avg_yield || 0) >= 95 ? 'ca-yield-green' : (op.avg_yield || 0) >= 90 ? 'ca-yield-amber' : 'ca-yield-red';
            var trendHtml = '';
            if (op.trend === 'up') trendHtml = '<span class="ca-trend-up">&#x25B2; Up</span>';
            else if (op.trend === 'down') trendHtml = '<span class="ca-trend-down">&#x25BC; Down</span>';
            else trendHtml = '<span class="ca-trend-flat">&#x25AC; Flat</span>';

            var star = idx === 0 ? '<span class="ca-gold-star" title="Top Performer">&#x2B50;</span>' : '';

            var tr = document.createElement('tr');
            tr.innerHTML =
                '<td>' + (idx + 1) + '</td>' +
                '<td><strong>' + caEsc(op.operator || 'Unknown') + '</strong>' + star + '</td>' +
                '<td>' + (op.coils_processed || 0) + '</td>' +
                '<td class="' + yieldClass + '" style="font-weight:700;">' + (op.avg_yield || 0).toFixed(1) + '%</td>' +
                '<td>' + (op.best_yield || 0).toFixed(1) + '%</td>' +
                '<td>' + (op.worst_yield || 0).toFixed(1) + '%</td>' +
                '<td>' + trendHtml + '</td>';
            tbody.appendChild(tr);
        });
    }

    /* ------------------------------------------------------------------ */
    /*  COIL DETAIL TABLE                                                  */
    /* ------------------------------------------------------------------ */
    function caRenderCoils() {
        caFilteredCoils = (caData.coils || []).slice();
        caApplySortAndFilter();
    }

    function caApplySortAndFilter() {
        var q = (document.getElementById('caCoilSearch').value || '').toLowerCase();
        var filtered = caFilteredCoils;

        if (q) {
            filtered = (caData.coils || []).filter(function(c) {
                return (c.coil_id || '').toLowerCase().indexOf(q) >= 0 ||
                       (c.material || '').toLowerCase().indexOf(q) >= 0 ||
                       (c.vendor || '').toLowerCase().indexOf(q) >= 0 ||
                       (c.status || '').toLowerCase().indexOf(q) >= 0;
            });
        } else {
            filtered = (caData.coils || []).slice();
        }

        /* Sort */
        filtered.sort(function(a, b) {
            var av = a[caSortCol], bv = b[caSortCol];
            if (av == null) av = '';
            if (bv == null) bv = '';
            if (typeof av === 'string') av = av.toLowerCase();
            if (typeof bv === 'string') bv = bv.toLowerCase();
            if (av < bv) return caSortAsc ? -1 : 1;
            if (av > bv) return caSortAsc ? 1 : -1;
            return 0;
        });

        document.getElementById('caCoilCount').textContent = filtered.length + ' coil' + (filtered.length !== 1 ? 's' : '');

        var tbody = document.getElementById('caCoilBody');
        tbody.innerHTML = '';

        if (filtered.length === 0) {
            tbody.innerHTML = '<tr><td colspan="12" style="text-align:center;color:var(--ca-muted);padding:24px;">No coils match the filter</td></tr>';
            return;
        }

        filtered.forEach(function(c) {
            var yp = c.yield_pct || 0;
            var yieldClass = yp >= 95 ? 'ca-yield-green' : yp >= 90 ? 'ca-yield-amber' : 'ca-yield-red';
            var wp = c.waste_pct || 0;
            var wasteClass = wp > 10 ? 'ca-yield-red' : wp > 5 ? 'ca-yield-amber' : 'ca-yield-green';

            var statusBadge = 'ca-badge-muted';
            var st = (c.status || '').toLowerCase();
            if (st === 'active' || st === 'in_use') statusBadge = 'ca-badge-green';
            else if (st === 'depleted' || st === 'consumed') statusBadge = 'ca-badge-red';
            else if (st === 'received' || st === 'available') statusBadge = 'ca-badge-blue';
            else if (st === 'on_hold') statusBadge = 'ca-badge-amber';

            var tr = document.createElement('tr');
            tr.innerHTML =
                '<td><strong>' + caEsc(c.coil_id || '--') + '</strong></td>' +
                '<td>' + caEsc(c.material || '--') + '</td>' +
                '<td>' + caEsc(c.gauge != null ? String(c.gauge) : '--') + '</td>' +
                '<td>' + (c.width != null ? c.width + '"' : '--') + '</td>' +
                '<td>' + caFmtNum(c.original_weight || 0) + '</td>' +
                '<td>' + caFmtNum(c.vendor_lft || 0) + '</td>' +
                '<td>' + caFmtNum(c.estimated_lft || 0) + '</td>' +
                '<td>' + caFmtNum(c.actual_lft || 0) + '</td>' +
                '<td class="' + yieldClass + '" style="font-weight:700;">' + yp.toFixed(1) + '%</td>' +
                '<td class="' + wasteClass + '">' + wp.toFixed(1) + '%</td>' +
                '<td><span class="ca-badge ' + statusBadge + '">' + caEsc(c.status || '--') + '</span></td>' +
                '<td>' + caEsc(c.date_received || '--') + '</td>';
            tbody.appendChild(tr);
        });

        /* Update sort arrows */
        document.querySelectorAll('#caCoilTable th[data-col]').forEach(function(th) {
            var arrow = th.querySelector('.sort-arrow');
            if (th.getAttribute('data-col') === caSortCol) {
                arrow.textContent = caSortAsc ? '\u25B2' : '\u25BC';
            } else {
                arrow.textContent = '';
            }
        });
    }

    window.caSortCoils = function(col) {
        if (caSortCol === col) { caSortAsc = !caSortAsc; }
        else { caSortCol = col; caSortAsc = true; }
        caApplySortAndFilter();
    };

    window.caFilterCoils = function() {
        caApplySortAndFilter();
    };

    /* ------------------------------------------------------------------ */
    /*  COST IMPACT                                                        */
    /* ------------------------------------------------------------------ */
    function caRenderCostImpact() {
        var s = caData.summary || {};
        document.getElementById('caCostTotal').textContent = '$' + caFmtNum(Math.round(s.total_material_cost || 0));
        document.getElementById('caCostWaste').textContent = '$' + caFmtNum(Math.round(s.estimated_waste_cost || 0));
        document.getElementById('caCostSavings').textContent = '$' + caFmtNum(Math.round(s.savings_opportunity || 0));
    }

    /* ------------------------------------------------------------------ */
    /*  EXPORT CSV                                                         */
    /* ------------------------------------------------------------------ */
    window.caExportCSV = function() {
        var coils = caData.coils || [];
        if (coils.length === 0) { caToast('No data to export', 'error'); return; }

        var headers = ['Coil ID','Material','Gauge','Width','Orig Weight (lbs)','Vendor LFT','Estimated LFT','Actual LFT','Yield %','Waste %','Status','Date Received'];
        var rows = [headers.join(',')];
        coils.forEach(function(c) {
            rows.push([
                '"' + (c.coil_id || '') + '"',
                '"' + (c.material || '') + '"',
                c.gauge || '',
                c.width || '',
                c.original_weight || 0,
                c.vendor_lft || 0,
                c.estimated_lft || 0,
                c.actual_lft || 0,
                (c.yield_pct || 0).toFixed(1),
                (c.waste_pct || 0).toFixed(1),
                '"' + (c.status || '') + '"',
                '"' + (c.date_received || '') + '"'
            ].join(','));
        });

        var blob = new Blob([rows.join('\n')], { type: 'text/csv' });
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url; a.download = 'coil_analytics_' + new Date().toISOString().slice(0, 10) + '.csv';
        document.body.appendChild(a); a.click(); a.remove();
        URL.revokeObjectURL(url);
        caToast('CSV exported successfully', 'success');
    };

    /* ------------------------------------------------------------------ */
    /*  HELPERS                                                            */
    /* ------------------------------------------------------------------ */
    function caFmtNum(n) {
        if (n == null) return '0';
        return Number(n).toLocaleString('en-US');
    }

    function caEsc(s) {
        if (!s) return '';
        var d = document.createElement('div');
        d.textContent = s;
        return d.innerHTML;
    }

    /* ------------------------------------------------------------------ */
    /*  INIT                                                               */
    /* ------------------------------------------------------------------ */
    document.addEventListener('DOMContentLoaded', function() {
        caFetchData();
    });
    /* Also fire immediately in case DOM is already ready */
    if (document.readyState !== 'loading') { caFetchData(); }

})();
</script>
"""
