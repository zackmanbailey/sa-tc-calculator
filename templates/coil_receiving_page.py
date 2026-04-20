"""
TitanForge v4 -- Coil Receiving Page
======================================
Log incoming steel coils from vendors. Captures vendor sticker data,
auto-calculates estimated linear footage, and prints receiving stickers.
"""

COIL_RECEIVING_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a;
        --tf-card: #1e293b;
        --tf-border: #334155;
        --tf-text: #e2e8f0;
        --tf-muted: #94a3b8;
        --tf-blue: #3b82f6;
        --tf-green: #10b981;
        --tf-amber: #f59e0b;
        --tf-red: #ef4444;
    }

    .cr-container {
        max-width: 1400px; margin: 0 auto; padding: 24px 32px;
        font-family: 'Inter', 'Segoe UI', sans-serif; color: var(--tf-text);
    }

    /* ---------- Header ---------- */
    .cr-header { margin-bottom: 28px; }
    .cr-header h1 { font-size: 28px; font-weight: 800; margin: 0 0 6px 0; }
    .cr-header p  { font-size: 14px; color: var(--tf-muted); margin: 0; }

    /* ---------- Summary Cards ---------- */
    .cr-summary-row {
        display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 16px; margin-bottom: 28px;
    }
    .cr-summary-card {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid var(--tf-border); padding: 20px 24px;
        transition: border-color .2s, transform .15s;
    }
    .cr-summary-card:hover { border-color: var(--tf-blue); transform: translateY(-2px); }
    .cr-summary-card .label {
        font-size: 12px; color: var(--tf-muted); text-transform: uppercase;
        letter-spacing: .5px; margin-bottom: 8px;
    }
    .cr-summary-card .value { font-size: 28px; font-weight: 800; }
    .cr-summary-card.blue  .value { color: var(--tf-blue); }
    .cr-summary-card.green .value { color: var(--tf-green); }
    .cr-summary-card.amber .value { color: var(--tf-amber); }
    .cr-summary-card.red   .value { color: var(--tf-red); }

    /* ---------- Section Card ---------- */
    .cr-section {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid var(--tf-border); padding: 24px; margin-bottom: 24px;
    }
    .cr-section h2 {
        font-size: 18px; font-weight: 700; margin: 0 0 16px 0;
        display: flex; align-items: center; gap: 8px;
    }
    .cr-section h2 .icon { font-size: 20px; }

    /* ---------- Start Row ---------- */
    .cr-start-row {
        display: flex; align-items: flex-end; gap: 16px; flex-wrap: wrap;
    }
    .cr-start-row .field-group { display: flex; flex-direction: column; gap: 6px; }
    .cr-start-row label {
        font-size: 13px; font-weight: 600; color: var(--tf-muted);
    }

    /* ---------- Form Inputs ---------- */
    .cr-input, .cr-select, .cr-textarea {
        background: var(--tf-bg); border: 1px solid var(--tf-border);
        border-radius: 8px; color: var(--tf-text); padding: 10px 14px;
        font-size: 14px; font-family: inherit; transition: border-color .2s;
        width: 100%; box-sizing: border-box;
    }
    .cr-input:focus, .cr-select:focus, .cr-textarea:focus {
        outline: none; border-color: var(--tf-blue);
        box-shadow: 0 0 0 3px rgba(59,130,246,.15);
    }
    .cr-input::placeholder { color: #475569; }
    .cr-textarea { min-height: 60px; resize: vertical; }
    .cr-select { cursor: pointer; appearance: none;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='%2394a3b8' viewBox='0 0 16 16'%3E%3Cpath d='M8 11L3 6h10z'/%3E%3C/svg%3E");
        background-repeat: no-repeat; background-position: right 12px center;
        padding-right: 32px;
    }
    .cr-select option { background: var(--tf-bg); color: var(--tf-text); }

    /* ---------- Buttons ---------- */
    .btn {
        display: inline-flex; align-items: center; gap: 8px;
        padding: 10px 20px; border-radius: 8px; font-size: 14px;
        font-weight: 600; border: none; cursor: pointer;
        font-family: inherit; transition: background .2s, transform .1s;
    }
    .btn:active { transform: scale(.97); }
    .btn-blue   { background: var(--tf-blue); color: #fff; }
    .btn-blue:hover { background: #2563eb; }
    .btn-green  { background: var(--tf-green); color: #fff; }
    .btn-green:hover { background: #059669; }
    .btn-amber  { background: var(--tf-amber); color: #000; }
    .btn-amber:hover { background: #d97706; }
    .btn-outline {
        background: transparent; border: 1px solid var(--tf-border); color: var(--tf-text);
    }
    .btn-outline:hover { border-color: var(--tf-blue); color: var(--tf-blue); }
    .btn:disabled { opacity: .45; cursor: not-allowed; }

    /* ---------- Coil Entry Forms ---------- */
    .coil-entry {
        background: var(--tf-bg); border: 1px solid var(--tf-border);
        border-radius: 12px; padding: 20px; margin-bottom: 16px;
        position: relative;
    }
    .coil-entry-header {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid var(--tf-border);
    }
    .coil-entry-header h3 {
        font-size: 16px; font-weight: 700; margin: 0;
        display: flex; align-items: center; gap: 8px;
    }
    .coil-entry-num {
        display: inline-flex; align-items: center; justify-content: center;
        width: 28px; height: 28px; border-radius: 50%; background: var(--tf-blue);
        font-size: 13px; font-weight: 700; color: #fff;
    }
    .coil-fields {
        display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;
    }
    .coil-fields .field { display: flex; flex-direction: column; gap: 5px; }
    .coil-fields .field label {
        font-size: 12px; font-weight: 600; color: var(--tf-muted);
        text-transform: uppercase; letter-spacing: .3px;
    }
    .coil-fields .field.full-width { grid-column: 1 / -1; }
    .coil-fields .field.two-col    { grid-column: span 2; }

    /* ---------- Auto-Calc Box ---------- */
    .calc-box {
        margin-top: 16px; padding: 16px; border-radius: 8px;
        background: rgba(59,130,246,.06); border: 1px solid rgba(59,130,246,.15);
        display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px;
    }
    .calc-item .calc-label {
        font-size: 11px; text-transform: uppercase; letter-spacing: .5px;
        color: var(--tf-muted); margin-bottom: 4px;
    }
    .calc-item .calc-value { font-size: 22px; font-weight: 800; color: var(--tf-blue); }
    .calc-warning {
        grid-column: 1 / -1; padding: 10px 14px; border-radius: 8px;
        background: rgba(245,158,11,.1); border: 1px solid rgba(245,158,11,.3);
        color: var(--tf-amber); font-size: 13px; font-weight: 600;
        display: none; align-items: center; gap: 8px;
    }
    .calc-warning.visible { display: flex; }

    /* ---------- Recent Log Table ---------- */
    .cr-table-wrap { overflow-x: auto; }
    .cr-table {
        width: 100%; border-collapse: collapse; font-size: 13px;
    }
    .cr-table th {
        text-align: left; padding: 10px 14px; color: var(--tf-muted);
        font-weight: 600; font-size: 11px; text-transform: uppercase;
        letter-spacing: .5px; border-bottom: 1px solid var(--tf-border);
        white-space: nowrap;
    }
    .cr-table td {
        padding: 10px 14px; border-bottom: 1px solid rgba(51,65,85,.4);
        white-space: nowrap;
    }
    .cr-table tr { cursor: pointer; transition: background .15s; }
    .cr-table tbody tr:hover { background: rgba(59,130,246,.06); }
    .status-badge {
        display: inline-block; padding: 3px 10px; border-radius: 20px;
        font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .3px;
    }
    .status-active   { background: rgba(16,185,129,.15); color: var(--tf-green); }
    .status-in-use   { background: rgba(59,130,246,.15); color: var(--tf-blue); }
    .status-depleted { background: rgba(239,68,68,.15); color: var(--tf-red); }
    .status-received { background: rgba(245,158,11,.15); color: var(--tf-amber); }

    /* ---------- Toast Notifications ---------- */
    .cr-toast-container {
        position: fixed; top: 20px; right: 20px; z-index: 9999;
        display: flex; flex-direction: column; gap: 8px; pointer-events: none;
    }
    .cr-toast {
        pointer-events: auto; min-width: 300px; max-width: 420px;
        padding: 14px 18px; border-radius: 10px; font-size: 14px;
        font-weight: 600; font-family: inherit; color: #fff;
        display: flex; align-items: center; gap: 10px;
        box-shadow: 0 8px 24px rgba(0,0,0,.35);
        animation: crToastIn .3s ease forwards;
    }
    .cr-toast.removing { animation: crToastOut .25s ease forwards; }
    .cr-toast.success { background: #065f46; border: 1px solid var(--tf-green); }
    .cr-toast.error   { background: #7f1d1d; border: 1px solid var(--tf-red); }
    .cr-toast.warning { background: #78350f; border: 1px solid var(--tf-amber); }
    .cr-toast.info    { background: #1e3a5f; border: 1px solid var(--tf-blue); }
    @keyframes crToastIn  { from { opacity: 0; transform: translateX(40px); } to { opacity: 1; transform: translateX(0); } }
    @keyframes crToastOut { from { opacity: 1; transform: translateX(0); } to { opacity: 0; transform: translateX(40px); } }

    /* ---------- Loading Spinner ---------- */
    .cr-spinner {
        display: inline-block; width: 18px; height: 18px;
        border: 2px solid rgba(255,255,255,.2); border-top-color: #fff;
        border-radius: 50%; animation: crSpin .6s linear infinite;
    }
    @keyframes crSpin { to { transform: rotate(360deg); } }

    /* ---------- Empty State ---------- */
    .cr-empty {
        text-align: center; padding: 40px 20px; color: var(--tf-muted);
        font-size: 14px;
    }

    /* ---------- Responsive ---------- */
    @media (max-width: 900px) {
        .cr-container { padding: 16px; }
        .coil-fields { grid-template-columns: 1fr; }
        .coil-fields .field.two-col { grid-column: 1; }
        .cr-summary-row { grid-template-columns: repeat(2, 1fr); }
    }
    @media (max-width: 500px) {
        .cr-summary-row { grid-template-columns: 1fr; }
        .cr-start-row { flex-direction: column; align-items: stretch; }
        .calc-box { grid-template-columns: 1fr; }
    }
</style>

<!-- Toast container -->
<div class="cr-toast-container" id="crToasts"></div>

<div class="cr-container">
    <!-- Header -->
    <div class="cr-header">
        <h1>Coil Receiving</h1>
        <p>Log incoming coils from vendors</p>
    </div>

    <!-- Active Coils Summary -->
    <div class="cr-summary-row" id="crSummary">
        <div class="cr-summary-card blue">
            <div class="label">Total Coils</div>
            <div class="value" id="sumTotal">--</div>
        </div>
        <div class="cr-summary-card green">
            <div class="label">Active</div>
            <div class="value" id="sumActive">--</div>
        </div>
        <div class="cr-summary-card amber">
            <div class="label">In Use</div>
            <div class="value" id="sumInUse">--</div>
        </div>
        <div class="cr-summary-card red">
            <div class="label">Depleted</div>
            <div class="value" id="sumDepleted">--</div>
        </div>
    </div>

    <!-- Receive New Coils -->
    <div class="cr-section">
        <h2><span class="icon">&#128230;</span> Receive New Coils</h2>
        <div class="cr-start-row">
            <div class="field-group">
                <label for="coilCount">How many coils received?</label>
                <input type="number" id="coilCount" class="cr-input" min="1" max="20" value="1" style="width:120px">
            </div>
            <button class="btn btn-blue" id="btnStartReceiving" onclick="startReceiving()">
                Start Receiving
            </button>
        </div>
        <div id="coilFormsContainer" style="margin-top:20px"></div>
        <div id="submitRow" style="margin-top:20px; display:none; text-align:right;">
            <button class="btn btn-green" id="btnReceivePrint" onclick="submitCoils()">
                &#9998; Receive &amp; Print Stickers
            </button>
        </div>
    </div>

    <!-- Recent Receiving Log -->
    <div class="cr-section">
        <h2><span class="icon">&#128203;</span> Recent Receiving Log</h2>
        <div class="cr-table-wrap">
            <table class="cr-table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Coil ID</th>
                        <th>Vendor</th>
                        <th>Material</th>
                        <th>Weight (lbs)</th>
                        <th>Est. LFT</th>
                        <th>Status</th>
                        <th>Mill Cert</th>
                    </tr>
                </thead>
                <tbody id="logTableBody">
                    <tr><td colspan="8" class="cr-empty">Loading...</td></tr>
                </tbody>
            </table>
        </div>
    </div>
</div>

<script>
(function() {
    "use strict";

    // ---- LBS per Linear Foot lookup ----
    const LBS_PER_LFT = {
        '10GA_23':      10.83,
        '12GA_20.125':  7.43,
        '16GA_4':       0.8656,
        '29GA_48':      2.81,
        '10GA_6':       1.04,
        '16GA_2':       0.65,
        '10GA_12':      4.0
    };

    // Gauge thickness in inches for fallback calculation
    const GAUGE_THICKNESS = {
        '10GA': 0.1345, '12GA': 0.1046, '14GA': 0.0747,
        '16GA': 0.0598, '18GA': 0.0478, '20GA': 0.0359,
        '22GA': 0.0299, '24GA': 0.0239, '26GA': 0.0179, '29GA': 0.0149
    };

    const GAUGE_OPTIONS = ['10 GA','12 GA','14 GA','16 GA','18 GA','20 GA','22 GA','24 GA','26 GA','29 GA'];
    const COIL_TYPES = [
        'C-Section (Columns & Rafters)', 'Z-Purlin', 'Angle (Sag Rods)',
        'Spartan Rib Panel', 'Plate (Interior Purlin Plates)',
        'Hurricane Strap', 'Gusset Plate', 'Other'
    ];

    // ---- Toast Notification System ----
    function showToast(msg, type) {
        type = type || 'info';
        var container = document.getElementById('crToasts');
        var toast = document.createElement('div');
        toast.className = 'cr-toast ' + type;
        var icons = { success: '\u2705', error: '\u274C', warning: '\u26A0\uFE0F', info: '\u2139\uFE0F' };
        toast.innerHTML = '<span>' + (icons[type] || '') + '</span><span>' + msg + '</span>';
        container.appendChild(toast);
        setTimeout(function() {
            toast.classList.add('removing');
            setTimeout(function() { toast.remove(); }, 300);
        }, 4000);
    }
    window._crToast = showToast;

    // ---- Fetch Summary ----
    function fetchSummary() {
        fetch('/api/coils/lifecycle/list')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                var coils = data.coils || data || [];
                var total = coils.length;
                var active = 0, inUse = 0, depleted = 0;
                coils.forEach(function(c) {
                    var s = (c.status || '').toLowerCase();
                    if (s === 'active' || s === 'available') active++;
                    else if (s === 'in-use' || s === 'in_use' || s === 'running') inUse++;
                    else if (s === 'depleted' || s === 'empty') depleted++;
                });
                document.getElementById('sumTotal').textContent = total;
                document.getElementById('sumActive').textContent = active;
                document.getElementById('sumInUse').textContent = inUse;
                document.getElementById('sumDepleted').textContent = depleted;
            })
            .catch(function() {
                document.getElementById('sumTotal').textContent = '0';
                document.getElementById('sumActive').textContent = '0';
                document.getElementById('sumInUse').textContent = '0';
                document.getElementById('sumDepleted').textContent = '0';
            });
    }

    // ---- Fetch Recent Log ----
    function fetchRecentLog() {
        fetch('/api/coils/lifecycle/list?status=all&limit=50')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                var coils = data.coils || data || [];
                var tbody = document.getElementById('logTableBody');
                if (!coils.length) {
                    tbody.innerHTML = '<tr><td colspan="8" class="cr-empty">No coils received yet.</td></tr>';
                    return;
                }
                var html = '';
                coils.forEach(function(c) {
                    var dt = c.received_date || c.date || c.created || '--';
                    if (dt && dt.length > 10) dt = dt.substring(0, 10);
                    var status = (c.status || 'received').toLowerCase();
                    var statusClass = 'status-received';
                    if (status === 'active' || status === 'available') statusClass = 'status-active';
                    else if (status === 'in-use' || status === 'in_use' || status === 'running') statusClass = 'status-in-use';
                    else if (status === 'depleted' || status === 'empty') statusClass = 'status-depleted';
                    var estLft = c.estimated_lft || c.est_linear_ft || '--';
                    if (typeof estLft === 'number') estLft = estLft.toLocaleString(undefined, {maximumFractionDigits: 0});
                    var weight = c.weight || c.actual_weight || '--';
                    if (typeof weight === 'number') weight = weight.toLocaleString();
                    html += '<tr onclick="if(\'' + (c.id || c.coil_id || '') + '\')location.href=\'/coils/lifecycle/detail/' + (c.id || c.coil_id || '') + '\'">' +
                        '<td>' + dt + '</td>' +
                        '<td style="font-weight:600;color:var(--tf-blue)">' + (c.coil_id || c.id || '--') + '</td>' +
                        '<td>' + (c.vendor || '--') + '</td>' +
                        '<td>' + (c.material_spec || c.material || '--') + '</td>' +
                        '<td>' + weight + '</td>' +
                        '<td>' + estLft + '</td>' +
                        '<td><span class="status-badge ' + statusClass + '">' + status + '</span></td>' +
                        '<td>' + (c.mill_cert_filename ? '<a href="/api/coils/lifecycle/mill-cert/' + (c.coil_id || c.id) + '" target="_blank" style="color:var(--tf-blue);text-decoration:none" title="View Mill Cert">\uD83D\uDCC4 View</a>' : '<span style="color:var(--tf-muted);font-size:12px">\u2014</span>') + '</td>' +
                        '</tr>';
                });
                tbody.innerHTML = html;
            })
            .catch(function() {
                document.getElementById('logTableBody').innerHTML =
                    '<tr><td colspan="8" class="cr-empty">Unable to load receiving log.</td></tr>';
            });
    }

    // ---- Calculate Estimated LFT ----
    function calcEstLft(gauge, width, weight) {
        if (!gauge || !width || !weight) return null;
        var gaugeKey = gauge.replace(/\s/g, '');
        var lookupKey = gaugeKey + '_' + width;
        var lbsPerLft = LBS_PER_LFT[lookupKey];
        if (!lbsPerLft) {
            // Fallback formula: width_in * thickness_in * 490 / 12
            var thickness = GAUGE_THICKNESS[gaugeKey];
            if (!thickness) return null;
            lbsPerLft = parseFloat(width) * thickness * 490.0 / 12.0;
        }
        if (lbsPerLft <= 0) return null;
        return weight / lbsPerLft;
    }

    // ---- Build Coil Entry Form ----
    function buildCoilForm(index) {
        var n = index + 1;
        var id = 'coil_' + index;

        var gaugeOpts = '<option value="">Select gauge...</option>';
        GAUGE_OPTIONS.forEach(function(g) {
            gaugeOpts += '<option value="' + g + '">' + g + '</option>';
        });

        var typeOpts = '<option value="">Select type...</option>';
        COIL_TYPES.forEach(function(t) {
            typeOpts += '<option value="' + t + '">' + t + '</option>';
        });

        return '<div class="coil-entry" id="' + id + '">' +
            '<div class="coil-entry-header">' +
                '<h3><span class="coil-entry-num">' + n + '</span> Coil ' + n + '</h3>' +
                '<button class="btn btn-outline" style="padding:6px 12px;font-size:12px" onclick="clearCoilForm(' + index + ')">Clear</button>' +
            '</div>' +
            '<div class="coil-fields">' +
                '<div class="field">' +
                    '<label>Vendor</label>' +
                    '<input type="text" class="cr-input" data-field="vendor" value="Klockner Metals Corp">' +
                '</div>' +
                '<div class="field">' +
                    '<label>Serial No</label>' +
                    '<input type="text" class="cr-input" data-field="serial_no" placeholder="e.g. 7026461">' +
                '</div>' +
                '<div class="field">' +
                    '<label>Supplier / Order No</label>' +
                    '<input type="text" class="cr-input" data-field="supplier_order_no" placeholder="e.g. 25295606-1">' +
                '</div>' +
                '<div class="field">' +
                    '<label>Customer Order No</label>' +
                    '<input type="text" class="cr-input" data-field="customer_order_no" placeholder="e.g. 2000811390">' +
                '</div>' +
                '<div class="field">' +
                    '<label>Heat / Process No</label>' +
                    '<input type="text" class="cr-input" data-field="heat_no" placeholder="e.g. 42602298">' +
                '</div>' +
                '<div class="field">' +
                    '<label>Coil #</label>' +
                    '<input type="text" class="cr-input" data-field="coil_number" placeholder="e.g. 26G03958">' +
                '</div>' +
                '<div class="field two-col">' +
                    '<label>Material Spec</label>' +
                    '<input type="text" class="cr-input" data-field="material_spec" placeholder="e.g. Roll Galvanized 10 Ga ASTM A653 HSLA Gr 80 G1">' +
                '</div>' +
                '<div class="field">' +
                    '<label>Gauge</label>' +
                    '<select class="cr-select" data-field="gauge" onchange="window._crRecalc(' + index + ')">' + gaugeOpts + '</select>' +
                '</div>' +
                '<div class="field">' +
                    '<label>Width (inches)</label>' +
                    '<input type="number" class="cr-input" data-field="width" step="0.0001" placeholder="e.g. 23.0000" oninput="window._crRecalc(' + index + ')">' +
                '</div>' +
                '<div class="field">' +
                    '<label>Actual Weight (lbs)</label>' +
                    '<input type="number" class="cr-input" data-field="actual_weight" step="1" placeholder="e.g. 7076" oninput="window._crRecalc(' + index + ')">' +
                '</div>' +
                '<div class="field">' +
                    '<label>Vendor Linear Ft</label>' +
                    '<input type="number" class="cr-input" data-field="vendor_lft" step="0.1" placeholder="Optional" oninput="window._crRecalc(' + index + ')">' +
                '</div>' +
                '<div class="field">' +
                    '<label>Coil Type</label>' +
                    '<select class="cr-select" data-field="coil_type">' + typeOpts + '</select>' +
                '</div>' +
                '<div class="field full-width">' +
                    '<label>Condition Notes</label>' +
                    '<textarea class="cr-textarea" data-field="condition_notes" placeholder="Optional - note any damage, rust, etc."></textarea>' +
                '</div>' +
                '<div class="field full-width">' +
                    '<label>Mill Cert PDF</label>' +
                    '<div style="display:flex;align-items:center;gap:12px">' +
                        '<input type="file" class="cr-input" data-field="mill_cert_file" accept=".pdf" style="padding:8px" onchange="window._crFileSelected(' + index + ', this)">' +
                        '<span class="mill-cert-status" id="millCertStatus_' + index + '" style="font-size:12px;color:var(--tf-muted)">No file selected</span>' +
                    '</div>' +
                '</div>' +
            '</div>' +
            '<!-- Auto-Calc -->' +
            '<div class="calc-box" id="calc_' + index + '">' +
                '<div class="calc-item">' +
                    '<div class="calc-label">Estimated Linear Feet</div>' +
                    '<div class="calc-value" id="estLft_' + index + '">--</div>' +
                '</div>' +
                '<div class="calc-item">' +
                    '<div class="calc-label">Vendor Linear Feet</div>' +
                    '<div class="calc-value" id="vendorLft_' + index + '" style="color:var(--tf-green)">--</div>' +
                '</div>' +
                '<div class="calc-warning" id="calcWarn_' + index + '">' +
                    '<span>\u26A0\uFE0F</span>' +
                    '<span id="calcWarnMsg_' + index + '"></span>' +
                '</div>' +
            '</div>' +
        '</div>';
    }

    // ---- Recalculate for a given coil index ----
    window._crRecalc = function(index) {
        var entry = document.getElementById('coil_' + index);
        if (!entry) return;
        var gauge = entry.querySelector('[data-field="gauge"]').value;
        var width = parseFloat(entry.querySelector('[data-field="width"]').value);
        var weight = parseFloat(entry.querySelector('[data-field="actual_weight"]').value);
        var vendorLftVal = parseFloat(entry.querySelector('[data-field="vendor_lft"]').value);

        var estEl = document.getElementById('estLft_' + index);
        var vendEl = document.getElementById('vendorLft_' + index);
        var warnEl = document.getElementById('calcWarn_' + index);
        var warnMsg = document.getElementById('calcWarnMsg_' + index);

        var est = calcEstLft(gauge, width, weight);
        if (est !== null && est > 0) {
            estEl.textContent = est.toLocaleString(undefined, {maximumFractionDigits: 1}) + ' ft';
        } else {
            estEl.textContent = '--';
        }

        if (!isNaN(vendorLftVal) && vendorLftVal > 0) {
            vendEl.textContent = vendorLftVal.toLocaleString(undefined, {maximumFractionDigits: 1}) + ' ft';
        } else {
            vendEl.textContent = '--';
        }

        // Warning check
        if (est && !isNaN(vendorLftVal) && vendorLftVal > 0) {
            var diff = Math.abs(est - vendorLftVal) / vendorLftVal;
            if (diff > 0.05) {
                warnMsg.textContent = 'Estimated LFT differs from vendor LFT by ' + (diff * 100).toFixed(1) + '%. Verify coil weight and dimensions.';
                warnEl.classList.add('visible');
            } else {
                warnEl.classList.remove('visible');
            }
        } else {
            warnEl.classList.remove('visible');
        }
    };

    // ---- File Selected Handler ----
    window._crFileSelected = function(index, input) {
        var status = document.getElementById('millCertStatus_' + index);
        if (input.files && input.files[0]) {
            var file = input.files[0];
            if (file.type !== 'application/pdf') {
                status.textContent = 'Must be a PDF file';
                status.style.color = 'var(--tf-red)';
                input.value = '';
                return;
            }
            if (file.size > 10 * 1024 * 1024) {
                status.textContent = 'File too large (max 10MB)';
                status.style.color = 'var(--tf-red)';
                input.value = '';
                return;
            }
            status.textContent = file.name + ' (' + (file.size / 1024).toFixed(0) + ' KB)';
            status.style.color = 'var(--tf-green)';
        } else {
            status.textContent = 'No file selected';
            status.style.color = 'var(--tf-muted)';
        }
    };

    // ---- Start Receiving ----
    window.startReceiving = function() {
        var count = parseInt(document.getElementById('coilCount').value) || 1;
        if (count < 1) count = 1;
        if (count > 20) count = 20;
        var container = document.getElementById('coilFormsContainer');
        var html = '';
        for (var i = 0; i < count; i++) {
            html += buildCoilForm(i);
        }
        container.innerHTML = html;
        document.getElementById('submitRow').style.display = 'block';
        showToast(count + ' coil form' + (count > 1 ? 's' : '') + ' ready', 'info');
    };

    // ---- Clear a single coil form ----
    window.clearCoilForm = function(index) {
        var entry = document.getElementById('coil_' + index);
        if (!entry) return;
        var inputs = entry.querySelectorAll('.cr-input, .cr-textarea');
        inputs.forEach(function(el) {
            if (el.dataset.field === 'vendor') {
                el.value = 'Klockner Metals Corp';
            } else {
                el.value = '';
            }
        });
        var selects = entry.querySelectorAll('.cr-select');
        selects.forEach(function(el) { el.selectedIndex = 0; });
        document.getElementById('estLft_' + index).textContent = '--';
        document.getElementById('vendorLft_' + index).textContent = '--';
        document.getElementById('calcWarn_' + index).classList.remove('visible');
        // Reset mill cert file status label
        var mcStatus = document.getElementById('millCertStatus_' + index);
        if (mcStatus) { mcStatus.textContent = 'No file selected'; mcStatus.style.color = 'var(--tf-muted)'; }
    };

    // ---- Collect form data ----
    function collectCoilData() {
        var entries = document.querySelectorAll('.coil-entry');
        var coils = [];
        var valid = true;
        entries.forEach(function(entry, i) {
            var obj = {};
            var fields = entry.querySelectorAll('[data-field]');
            fields.forEach(function(f) {
                if (f.type === 'file') return; // skip file inputs — handled separately
                var key = f.dataset.field;
                var val = f.value ? f.value.trim() : '';
                obj[key] = val;
            });
            // Validate required fields
            if (!obj.serial_no && !obj.coil_number) {
                showToast('Coil ' + (i+1) + ': Serial No or Coil # is required.', 'error');
                valid = false;
            }
            if (!obj.gauge) {
                showToast('Coil ' + (i+1) + ': Gauge is required.', 'error');
                valid = false;
            }
            if (!obj.actual_weight) {
                showToast('Coil ' + (i+1) + ': Actual Weight is required.', 'error');
                valid = false;
            }
            // Add computed estimated lft
            var est = calcEstLft(obj.gauge, parseFloat(obj.width), parseFloat(obj.actual_weight));
            if (est) obj.estimated_lft = Math.round(est * 10) / 10;
            // Convert numeric fields
            if (obj.actual_weight) obj.actual_weight = parseFloat(obj.actual_weight);
            if (obj.width) obj.width = parseFloat(obj.width);
            if (obj.vendor_lft) obj.vendor_lft = parseFloat(obj.vendor_lft);
            coils.push(obj);
        });
        return valid ? coils : null;
    }

    // ---- Submit Coils ----
    window.submitCoils = function() {
        var coilsRaw = collectCoilData();
        if (!coilsRaw) return;

        var btn = document.getElementById('btnReceivePrint');
        var origText = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<span class="cr-spinner"></span> Receiving...';

        var formData = new FormData();
        formData.append('coils_json', JSON.stringify(coilsRaw));

        // Attach mill cert files
        var entries = document.querySelectorAll('.coil-entry');
        entries.forEach(function(entry, i) {
            var fileInput = entry.querySelector('[data-field="mill_cert_file"]');
            if (fileInput && fileInput.files && fileInput.files[0]) {
                formData.append('mill_cert_' + i, fileInput.files[0]);
            }
        });

        fetch('/api/coils/lifecycle/receive', {
            method: 'POST',
            body: formData
        })
        .then(function(r) {
            if (!r.ok) throw new Error('Server returned ' + r.status);
            return r.json();
        })
        .then(function(data) {
            var ids = data.ids || data.coil_ids || [];
            showToast(coilsRaw.length + ' coil' + (coilsRaw.length > 1 ? 's' : '') + ' received successfully!', 'success');
            if (ids.length > 0) {
                var url = '/api/coils/lifecycle/stickers?ids=' + ids.join(',');
                window.open(url, '_blank');
            }
            document.getElementById('coilFormsContainer').innerHTML = '';
            document.getElementById('submitRow').style.display = 'none';
            document.getElementById('coilCount').value = 1;
            fetchSummary();
            fetchRecentLog();
        })
        .catch(function(err) {
            showToast('Error receiving coils: ' + err.message, 'error');
        })
        .finally(function() {
            btn.disabled = false;
            btn.innerHTML = origText;
        });
    };

    // ---- Init ----
    fetchSummary();
    fetchRecentLog();

})();
</script>
"""
