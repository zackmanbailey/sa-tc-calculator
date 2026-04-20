"""
TitanForge — Coil Mobile Scan Page
====================================
Mobile-friendly page shown when shop floor workers scan a QR code
on a coil sticker.

URL: /coil-scan/{coil_lifecycle_id}

Shows:
  1. Coil header with status badge
  2. Coil details (vendor sticker info)
  3. Usage summary with progress bar
  4. Action buttons (start use, log pieces, return, deplete)
  5. Usage history log
  6. Assigned work orders
"""

COIL_MOBILE_HTML = r"""
<style>
    :root {
        --cm-bg: #0f172a;
        --cm-card: #1e293b;
        --cm-border: #334155;
        --cm-text: #e2e8f0;
        --cm-muted: #94a3b8;
        --cm-blue: #3b82f6;
        --cm-green: #10b981;
        --cm-amber: #f59e0b;
        --cm-red: #ef4444;
        --cm-radius: 12px;
    }

    .cm-wrap {
        max-width: 480px;
        margin: 0 auto;
        padding: 12px;
        font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
        color: var(--cm-text);
        font-size: 16px;
        -webkit-tap-highlight-color: transparent;
        user-select: none;
        min-height: 100vh;
    }

    /* ── Pull-to-refresh cue ── */
    .cm-pull-cue {
        text-align: center;
        font-size: 12px;
        color: var(--cm-muted);
        padding: 8px 0 4px;
        opacity: 0.6;
        transition: opacity 0.3s;
    }
    .cm-pull-cue.active { opacity: 1; }

    /* ── Cards ── */
    .cm-card {
        background: var(--cm-card);
        border: 1px solid var(--cm-border);
        border-radius: var(--cm-radius);
        padding: 16px;
        margin-bottom: 12px;
    }
    .cm-card-title {
        font-size: 13px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--cm-muted);
        margin-bottom: 12px;
    }

    /* ── Header Card ── */
    .cm-header-card {
        text-align: center;
        padding: 20px 16px;
    }
    .cm-coil-id {
        font-size: 24px;
        font-weight: 800;
        line-height: 1.2;
        margin-bottom: 10px;
        word-break: break-all;
    }
    .cm-status-badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .cm-status-available { background: rgba(16,185,129,0.2); color: #34d399; }
    .cm-status-in_use    { background: rgba(245,158,11,0.2); color: #fbbf24; }
    .cm-status-depleted  { background: rgba(239,68,68,0.2); color: #f87171; }
    .cm-status-returned  { background: rgba(59,130,246,0.2); color: #60a5fa; }

    /* ── Details Grid ── */
    .cm-detail-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
    }
    .cm-detail-item {
        padding: 8px 0;
    }
    .cm-detail-label {
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--cm-muted);
        margin-bottom: 2px;
    }
    .cm-detail-value {
        font-size: 15px;
        font-weight: 600;
    }
    .cm-detail-full {
        grid-column: 1 / -1;
    }

    /* ── Progress Bar ── */
    .cm-progress-wrap {
        margin: 12px 0;
    }
    .cm-progress-bar-bg {
        width: 100%;
        height: 12px;
        background: rgba(255,255,255,0.08);
        border-radius: 6px;
        overflow: hidden;
    }
    .cm-progress-bar-fill {
        height: 100%;
        border-radius: 6px;
        transition: width 0.5s ease;
        background: var(--cm-green);
    }
    .cm-progress-bar-fill.warn { background: var(--cm-amber); }
    .cm-progress-bar-fill.crit { background: var(--cm-red); }
    .cm-progress-labels {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        color: var(--cm-muted);
        margin-top: 4px;
    }

    /* ── Usage Summary Stats ── */
    .cm-usage-stats {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        margin-top: 12px;
    }
    .cm-usage-stat {
        text-align: center;
        padding: 10px 4px;
        background: rgba(255,255,255,0.03);
        border-radius: 8px;
    }
    .cm-usage-stat-value {
        font-size: 22px;
        font-weight: 800;
    }
    .cm-usage-stat-label {
        font-size: 11px;
        color: var(--cm-muted);
        margin-top: 2px;
    }

    /* ── Action Buttons ── */
    .cm-actions {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-bottom: 12px;
    }
    .cm-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        width: 100%;
        min-height: 52px;
        border: none;
        border-radius: var(--cm-radius);
        font-size: 16px;
        font-weight: 700;
        cursor: pointer;
        transition: opacity 0.15s, transform 0.1s;
        -webkit-tap-highlight-color: transparent;
    }
    .cm-btn:active { transform: scale(0.97); }
    .cm-btn:disabled { opacity: 0.4; pointer-events: none; }
    .cm-btn-green  { background: var(--cm-green); color: #022c22; }
    .cm-btn-blue   { background: var(--cm-blue);  color: #fff; }
    .cm-btn-amber  { background: var(--cm-amber); color: #422006; }
    .cm-btn-red    { background: var(--cm-red);   color: #fff; }

    /* ── Modal ── */
    .cm-modal-overlay {
        display: none;
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.7);
        z-index: 2000;
        justify-content: center;
        align-items: flex-end;
        padding: 0;
    }
    .cm-modal-overlay.active { display: flex; }
    .cm-modal {
        background: var(--cm-card);
        border-radius: 16px 16px 0 0;
        padding: 24px 20px 32px;
        width: 100%;
        max-width: 480px;
        border-top: 1px solid var(--cm-border);
        animation: cm-slide-up 0.25s ease-out;
    }
    @keyframes cm-slide-up {
        from { transform: translateY(100%); }
        to   { transform: translateY(0); }
    }
    .cm-modal h3 {
        font-size: 20px;
        font-weight: 700;
        margin: 0 0 16px;
    }
    .cm-modal-handle {
        width: 40px;
        height: 4px;
        background: var(--cm-border);
        border-radius: 2px;
        margin: 0 auto 16px;
    }
    .cm-form-group {
        margin-bottom: 14px;
    }
    .cm-form-group label {
        display: block;
        font-size: 13px;
        font-weight: 600;
        color: var(--cm-muted);
        margin-bottom: 6px;
    }
    .cm-form-group input {
        width: 100%;
        background: var(--cm-bg);
        border: 1px solid var(--cm-border);
        border-radius: 8px;
        padding: 12px 14px;
        color: var(--cm-text);
        font-size: 16px;
        box-sizing: border-box;
    }
    .cm-form-group input:focus {
        outline: none;
        border-color: var(--cm-blue);
    }
    .cm-modal-actions {
        display: flex;
        gap: 10px;
        margin-top: 18px;
    }
    .cm-modal-actions .cm-btn { flex: 1; }
    .cm-btn-cancel {
        background: transparent;
        border: 1px solid var(--cm-border);
        color: var(--cm-muted);
        min-height: 48px;
        border-radius: var(--cm-radius);
        font-size: 15px;
        font-weight: 600;
        cursor: pointer;
    }

    /* ── History List ── */
    .cm-history-list {
        max-height: 300px;
        overflow-y: auto;
        -webkit-overflow-scrolling: touch;
    }
    .cm-history-item {
        padding: 12px 0;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        font-size: 14px;
    }
    .cm-history-item:last-child { border-bottom: none; }
    .cm-history-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 4px;
    }
    .cm-history-operator { font-weight: 600; }
    .cm-history-date { font-size: 12px; color: var(--cm-muted); }
    .cm-history-detail { font-size: 13px; color: var(--cm-muted); }

    /* ── Work Orders ── */
    .cm-wo-item {
        padding: 12px 0;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    .cm-wo-item:last-child { border-bottom: none; }
    .cm-wo-job {
        font-weight: 700;
        color: var(--cm-blue);
        font-size: 15px;
    }
    .cm-wo-desc {
        font-size: 13px;
        color: var(--cm-muted);
        margin-top: 2px;
    }
    .cm-wo-pieces {
        font-size: 13px;
        margin-top: 2px;
    }

    /* ── Empty / Loading ── */
    .cm-empty {
        text-align: center;
        padding: 24px 12px;
        color: var(--cm-muted);
        font-size: 14px;
    }
    .cm-loading {
        text-align: center;
        padding: 40px 12px;
        color: var(--cm-muted);
        font-size: 15px;
    }
    .cm-spinner {
        display: inline-block;
        width: 28px; height: 28px;
        border: 3px solid rgba(255,255,255,0.1);
        border-top-color: var(--cm-blue);
        border-radius: 50%;
        animation: cm-spin 0.7s linear infinite;
        margin-bottom: 10px;
    }
    @keyframes cm-spin { to { transform: rotate(360deg); } }

    /* ── Auto-refresh indicator ── */
    .cm-refresh-dot {
        position: fixed;
        top: 8px;
        right: 12px;
        width: 8px; height: 8px;
        border-radius: 50%;
        background: var(--cm-green);
        opacity: 0;
        transition: opacity 0.3s;
        z-index: 100;
    }
    .cm-refresh-dot.blink { opacity: 1; }
</style>

<div class="cm-wrap" id="cmWrap">
    <div class="cm-refresh-dot" id="cmRefreshDot"></div>

    <!-- Pull-to-refresh cue -->
    <div class="cm-pull-cue" id="cmPullCue">&#8595; Pull down to refresh</div>

    <!-- Loading state -->
    <div class="cm-loading" id="cmLoading">
        <div class="cm-spinner"></div>
        <div>Loading coil data...</div>
    </div>

    <!-- Main content (hidden until loaded) -->
    <div id="cmContent" style="display:none;">

        <!-- 1. Coil Header Card -->
        <div class="cm-card cm-header-card">
            <div class="cm-coil-id" id="cmCoilId">--</div>
            <div id="cmStatusBadge" class="cm-status-badge cm-status-available">AVAILABLE</div>
        </div>

        <!-- 2. Coil Details Card -->
        <div class="cm-card">
            <div class="cm-card-title">Coil Details</div>
            <div class="cm-detail-grid">
                <div class="cm-detail-item">
                    <div class="cm-detail-label">Material Spec</div>
                    <div class="cm-detail-value" id="cmMaterial">--</div>
                </div>
                <div class="cm-detail-item">
                    <div class="cm-detail-label">Gauge</div>
                    <div class="cm-detail-value" id="cmGauge">--</div>
                </div>
                <div class="cm-detail-item">
                    <div class="cm-detail-label">Width</div>
                    <div class="cm-detail-value" id="cmWidth">--</div>
                </div>
                <div class="cm-detail-item">
                    <div class="cm-detail-label">Weight (Original)</div>
                    <div class="cm-detail-value" id="cmWeightOrig">--</div>
                </div>
                <div class="cm-detail-item">
                    <div class="cm-detail-label">Vendor LFT</div>
                    <div class="cm-detail-value" id="cmVendorLft">--</div>
                </div>
                <div class="cm-detail-item">
                    <div class="cm-detail-label">Heat / Process No</div>
                    <div class="cm-detail-value" id="cmHeatNo">--</div>
                </div>
                <div class="cm-detail-item">
                    <div class="cm-detail-label">Serial No</div>
                    <div class="cm-detail-value" id="cmSerialNo">--</div>
                </div>
                <div class="cm-detail-item">
                    <div class="cm-detail-label">Coil #</div>
                    <div class="cm-detail-value" id="cmCoilNum">--</div>
                </div>
                <div class="cm-detail-item cm-detail-full">
                    <div class="cm-detail-label">Date Received</div>
                    <div class="cm-detail-value" id="cmDateReceived">--</div>
                </div>
                <div class="cm-detail-item">
                    <div class="cm-detail-label">Remaining Weight</div>
                    <div class="cm-detail-value" id="cmWeightRemain" style="color:var(--cm-green);">--</div>
                </div>
                <div class="cm-detail-item">
                    <div class="cm-detail-label">Est. Remaining LFT</div>
                    <div class="cm-detail-value" id="cmLftRemain" style="color:var(--cm-green);">--</div>
                </div>
            </div>
        </div>

        <!-- 3. Usage Summary Card -->
        <div class="cm-card">
            <div class="cm-card-title">Usage Summary</div>
            <div class="cm-progress-wrap">
                <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px;">
                    <span>Remaining: <strong id="cmProgRemain">0</strong> lbs</span>
                    <span>Original: <strong id="cmProgOrig">0</strong> lbs</span>
                </div>
                <div class="cm-progress-bar-bg">
                    <div class="cm-progress-bar-fill" id="cmProgressFill" style="width:0%;"></div>
                </div>
                <div class="cm-progress-labels">
                    <span id="cmProgPct">0% remaining</span>
                    <span id="cmProgUsed">0 lbs used</span>
                </div>
            </div>
            <div class="cm-usage-stats">
                <div class="cm-usage-stat">
                    <div class="cm-usage-stat-value" id="cmPiecesRolled" style="color:var(--cm-blue);">0</div>
                    <div class="cm-usage-stat-label">Pieces Rolled</div>
                </div>
                <div class="cm-usage-stat">
                    <div class="cm-usage-stat-value" id="cmPiecesRemain" style="color:var(--cm-amber);">0</div>
                    <div class="cm-usage-stat-label">Est. Pieces Left</div>
                </div>
                <div class="cm-usage-stat">
                    <div class="cm-usage-stat-value" id="cmYield" style="color:var(--cm-green);">0%</div>
                    <div class="cm-usage-stat-label">Yield</div>
                </div>
                <div class="cm-usage-stat">
                    <div class="cm-usage-stat-value" id="cmTotalUsedLft" style="color:var(--cm-muted);">0</div>
                    <div class="cm-usage-stat-label">Total LFT Used</div>
                </div>
            </div>
        </div>

        <!-- 4. Action Buttons -->
        <div class="cm-actions" id="cmActions">
            <button class="cm-btn cm-btn-green" id="btnStartUse" onclick="startUseCoil()">
                <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
                Start Using This Coil
            </button>
            <button class="cm-btn cm-btn-blue" id="btnLogPieces" onclick="openModal('logPiecesModal')">
                <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg>
                Log Pieces Rolled
            </button>
            <button class="cm-btn cm-btn-amber" id="btnReturn" onclick="openModal('returnModal')">
                <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M3 10h13a4 4 0 010 8H9M3 10l4-4M3 10l4 4"/></svg>
                Return to Inventory
            </button>
            <button class="cm-btn cm-btn-red" id="btnDeplete" onclick="confirmDeplete()">
                <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M18 6L6 18M6 6l12 12"/></svg>
                Mark Depleted
            </button>
        </div>

        <!-- 5. Usage History -->
        <div class="cm-card">
            <div class="cm-card-title">Usage History</div>
            <div class="cm-history-list" id="cmHistory">
                <div class="cm-empty">No usage history yet.</div>
            </div>
        </div>

        <!-- 6. Assigned Work Orders -->
        <div class="cm-card">
            <div class="cm-card-title">Assigned Work Orders</div>
            <div id="cmWorkOrders">
                <div class="cm-empty">No work orders assigned.</div>
            </div>
        </div>
    </div>
</div>

<!-- Log Pieces Modal -->
<div class="cm-modal-overlay" id="logPiecesModal">
    <div class="cm-modal">
        <div class="cm-modal-handle"></div>
        <h3>Log Pieces Rolled</h3>
        <div class="cm-form-group">
            <label>How many pieces did you roll?</label>
            <input type="number" id="logPieceCount" inputmode="numeric" placeholder="e.g. 12" min="1">
        </div>
        <div class="cm-form-group">
            <label>Piece length (ft)</label>
            <input type="number" id="logPieceLength" inputmode="decimal" placeholder="e.g. 21.5" min="0" step="0.1">
        </div>
        <div class="cm-modal-actions">
            <button class="cm-btn-cancel" onclick="closeModal('logPiecesModal')">Cancel</button>
            <button class="cm-btn cm-btn-blue" onclick="submitLogPieces()">Log Pieces</button>
        </div>
    </div>
</div>

<!-- Return Modal -->
<div class="cm-modal-overlay" id="returnModal">
    <div class="cm-modal">
        <div class="cm-modal-handle"></div>
        <h3>Return to Inventory</h3>
        <div class="cm-form-group">
            <label>Estimated remaining weight (lbs)</label>
            <input type="number" id="returnWeight" inputmode="numeric" placeholder="e.g. 1500" min="0">
        </div>
        <div class="cm-form-group">
            <label>Location</label>
            <input type="text" id="returnLocation" placeholder="e.g. Bay 3, Rack 2">
        </div>
        <div class="cm-modal-actions">
            <button class="cm-btn-cancel" onclick="closeModal('returnModal')">Cancel</button>
            <button class="cm-btn cm-btn-amber" onclick="submitReturn()">Return Coil</button>
        </div>
    </div>
</div>

<!-- Start Use Modal (operator prompt) -->
<div class="cm-modal-overlay" id="startUseModal">
    <div class="cm-modal">
        <div class="cm-modal-handle"></div>
        <h3>Start Using Coil</h3>
        <div class="cm-form-group">
            <label>Your name (operator)</label>
            <input type="text" id="startOperator" placeholder="e.g. John D.">
        </div>
        <div class="cm-modal-actions">
            <button class="cm-btn-cancel" onclick="closeModal('startUseModal')">Cancel</button>
            <button class="cm-btn cm-btn-green" onclick="submitStartUse()">Start</button>
        </div>
    </div>
</div>

<script>
(function() {
    const COIL_ID = '{{COIL_ID}}';
    const API_BASE = '/api/coils/lifecycle/' + COIL_ID;
    let coilData = null;
    let refreshTimer = null;

    /* ── Helpers ── */
    function $(id) { return document.getElementById(id); }

    function fmt(n) {
        if (n == null) return '--';
        return Number(n).toLocaleString(undefined, { maximumFractionDigits: 1 });
    }

    function fmtDate(d) {
        if (!d) return '--';
        try {
            var dt = new Date(d);
            return dt.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
        } catch(e) { return d; }
    }

    function fmtDateTime(d) {
        if (!d) return '--';
        try {
            var dt = new Date(d);
            return dt.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) + ' ' +
                   dt.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
        } catch(e) { return d; }
    }

    /* ── Modal helpers ── */
    window.openModal = function(id) { $(id).classList.add('active'); };
    window.closeModal = function(id) { $(id).classList.remove('active'); };

    document.querySelectorAll('.cm-modal-overlay').forEach(function(m) {
        m.addEventListener('click', function(e) {
            if (e.target === this) closeModal(this.id);
        });
    });

    /* ── Status mapping ── */
    function statusClass(s) {
        if (!s) return 'cm-status-available';
        var lower = s.toLowerCase().replace(/[\s-]/g, '_');
        if (lower === 'in_use' || lower === 'inuse') return 'cm-status-in_use';
        if (lower === 'depleted') return 'cm-status-depleted';
        if (lower === 'returned') return 'cm-status-returned';
        return 'cm-status-available';
    }

    function statusLabel(s) {
        if (!s) return 'AVAILABLE';
        return s.toUpperCase().replace(/_/g, ' ');
    }

    /* ── Update UI ── */
    function updateUI(data) {
        coilData = data;

        // Header
        $('cmCoilId').textContent = data.coil_tag || data.coil_id || data.id || '--';
        var badge = $('cmStatusBadge');
        badge.className = 'cm-status-badge ' + statusClass(data.status);
        badge.textContent = statusLabel(data.status);

        // Details
        $('cmMaterial').textContent = data.material_spec || data.material || '--';
        $('cmGauge').textContent = data.gauge || '--';
        $('cmWidth').textContent = data.width ? (data.width + '"') : '--';
        $('cmWeightOrig').textContent = data.original_weight ? (fmt(data.original_weight) + ' lbs') : '--';
        $('cmVendorLft').textContent = data.vendor_lft ? (fmt(data.vendor_lft) + ' ft') : '--';
        $('cmHeatNo').textContent = data.heat_number || data.process_number || '--';
        $('cmSerialNo').textContent = data.serial_number || '--';
        $('cmCoilNum').textContent = data.coil_number || '--';
        $('cmDateReceived').textContent = fmtDate(data.date_received);

        var remainW = data.remaining_weight || 0;
        var origW = data.original_weight || 1;
        var remainLft = data.remaining_lft || data.estimated_remaining_lft || 0;

        $('cmWeightRemain').textContent = fmt(remainW) + ' lbs';
        $('cmLftRemain').textContent = fmt(remainLft) + ' ft';

        // Usage summary
        var pct = Math.round((remainW / origW) * 100);
        var usedW = origW - remainW;
        $('cmProgRemain').textContent = fmt(remainW);
        $('cmProgOrig').textContent = fmt(origW);
        $('cmProgPct').textContent = pct + '% remaining';
        $('cmProgUsed').textContent = fmt(usedW) + ' lbs used';

        var fill = $('cmProgressFill');
        fill.style.width = pct + '%';
        fill.className = 'cm-progress-bar-fill' + (pct <= 10 ? ' crit' : pct <= 25 ? ' warn' : '');

        $('cmPiecesRolled').textContent = fmt(data.pieces_rolled || 0);
        $('cmPiecesRemain').textContent = fmt(data.estimated_pieces_remaining || 0);
        $('cmYield').textContent = (data.yield_percentage != null ? fmt(data.yield_percentage) : '0') + '%';
        $('cmTotalUsedLft').textContent = fmt(data.total_lft_used || 0);

        // Action button visibility based on status
        var st = (data.status || '').toLowerCase().replace(/[\s-]/g, '_');
        $('btnStartUse').style.display  = (st === 'available') ? 'flex' : 'none';
        $('btnLogPieces').style.display  = (st === 'in_use' || st === 'inuse') ? 'flex' : 'none';
        $('btnReturn').style.display     = (st === 'in_use' || st === 'inuse') ? 'flex' : 'none';
        $('btnDeplete').style.display    = (st !== 'depleted') ? 'flex' : 'none';

        // Usage history
        renderHistory(data.usage_history || data.usage_logs || []);

        // Work orders
        renderWorkOrders(data.work_orders || data.assigned_work_orders || []);
    }

    function renderHistory(logs) {
        var container = $('cmHistory');
        if (!logs.length) {
            container.innerHTML = '<div class="cm-empty">No usage history yet.</div>';
            return;
        }
        var html = '';
        logs.forEach(function(log) {
            html += '<div class="cm-history-item">' +
                '<div class="cm-history-top">' +
                    '<span class="cm-history-operator">' + (log.operator || 'Unknown') + '</span>' +
                    '<span class="cm-history-date">' + fmtDateTime(log.date || log.timestamp || log.created_at) + '</span>' +
                '</div>' +
                '<div class="cm-history-detail">' +
                    (log.pieces ? log.pieces + ' pcs' : '') +
                    (log.piece_length ? ' x ' + log.piece_length + ' ft' : '') +
                    (log.weight_used ? ' &mdash; ' + fmt(log.weight_used) + ' lbs used' : '') +
                '</div>' +
            '</div>';
        });
        container.innerHTML = html;
    }

    function renderWorkOrders(orders) {
        var container = $('cmWorkOrders');
        if (!orders.length) {
            container.innerHTML = '<div class="cm-empty">No work orders assigned.</div>';
            return;
        }
        var html = '';
        orders.forEach(function(wo) {
            html += '<div class="cm-wo-item">' +
                '<div class="cm-wo-job">' + (wo.job_code || wo.work_order_id || '--') + '</div>' +
                '<div class="cm-wo-desc">' + (wo.item_description || wo.description || '') + '</div>' +
                '<div class="cm-wo-pieces">Required: <strong>' + (wo.required_pieces || wo.pieces || '--') + '</strong> pieces</div>' +
            '</div>';
        });
        container.innerHTML = html;
    }

    /* ── Data Loading ── */
    function loadData() {
        var dot = $('cmRefreshDot');
        dot.classList.add('blink');
        setTimeout(function() { dot.classList.remove('blink'); }, 600);

        fetch(API_BASE)
            .then(function(r) {
                if (!r.ok) throw new Error('HTTP ' + r.status);
                return r.json();
            })
            .then(function(resp) {
                var data = resp.data || resp;
                updateUI(data);
                $('cmLoading').style.display = 'none';
                $('cmContent').style.display = 'block';
            })
            .catch(function(err) {
                console.error('Failed to load coil data:', err);
                $('cmLoading').innerHTML = '<div style="color:var(--cm-red);font-size:16px;font-weight:600;">Failed to load coil data</div>' +
                    '<div style="color:var(--cm-muted);font-size:13px;margin-top:8px;">' + err.message + '</div>' +
                    '<button class="cm-btn cm-btn-blue" style="margin:16px auto 0;width:auto;padding:0 24px;" onclick="location.reload()">Retry</button>';
            });
    }

    /* ── API actions ── */
    function apiPost(endpoint, body) {
        return fetch(API_BASE + endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        }).then(function(r) {
            if (!r.ok) return r.json().then(function(d) { throw new Error(d.error || d.message || 'Request failed'); });
            return r.json();
        });
    }

    window.startUseCoil = function() {
        openModal('startUseModal');
        setTimeout(function() { $('startOperator').focus(); }, 300);
    };

    window.submitStartUse = function() {
        var operator = $('startOperator').value.trim();
        if (!operator) { $('startOperator').style.borderColor = 'var(--cm-red)'; return; }
        $('startOperator').style.borderColor = '';
        closeModal('startUseModal');
        apiPost('/start-use', { operator: operator })
            .then(function() { loadData(); })
            .catch(function(err) { alert('Error: ' + err.message); });
    };

    window.submitLogPieces = function() {
        var count = parseInt($('logPieceCount').value, 10);
        var length = parseFloat($('logPieceLength').value);
        var valid = true;
        if (!count || count < 1) { $('logPieceCount').style.borderColor = 'var(--cm-red)'; valid = false; }
        else { $('logPieceCount').style.borderColor = ''; }
        if (!length || length <= 0) { $('logPieceLength').style.borderColor = 'var(--cm-red)'; valid = false; }
        else { $('logPieceLength').style.borderColor = ''; }
        if (!valid) return;
        closeModal('logPiecesModal');
        apiPost('/log-usage', { pieces: count, piece_length: length })
            .then(function() {
                $('logPieceCount').value = '';
                $('logPieceLength').value = '';
                loadData();
            })
            .catch(function(err) { alert('Error: ' + err.message); });
    };

    window.submitReturn = function() {
        var weight = parseFloat($('returnWeight').value);
        var location = $('returnLocation').value.trim();
        var valid = true;
        if (!weight || weight < 0) { $('returnWeight').style.borderColor = 'var(--cm-red)'; valid = false; }
        else { $('returnWeight').style.borderColor = ''; }
        if (!location) { $('returnLocation').style.borderColor = 'var(--cm-red)'; valid = false; }
        else { $('returnLocation').style.borderColor = ''; }
        if (!valid) return;
        closeModal('returnModal');
        apiPost('/return', { remaining_weight: weight, location: location })
            .then(function() {
                $('returnWeight').value = '';
                $('returnLocation').value = '';
                loadData();
            })
            .catch(function(err) { alert('Error: ' + err.message); });
    };

    window.confirmDeplete = function() {
        if (confirm('Mark this coil as DEPLETED? This cannot be undone.')) {
            apiPost('/deplete', {})
                .then(function() { loadData(); })
                .catch(function(err) { alert('Error: ' + err.message); });
        }
    };

    /* ── Pull-to-refresh ── */
    var startY = 0;
    var pulling = false;
    var cue = $('cmPullCue');

    document.addEventListener('touchstart', function(e) {
        if (window.scrollY === 0) {
            startY = e.touches[0].clientY;
            pulling = true;
        }
    }, { passive: true });

    document.addEventListener('touchmove', function(e) {
        if (!pulling) return;
        var dy = e.touches[0].clientY - startY;
        if (dy > 30) {
            cue.classList.add('active');
            cue.textContent = dy > 80 ? 'Release to refresh' : '\u2193 Pull down to refresh';
        }
    }, { passive: true });

    document.addEventListener('touchend', function(e) {
        if (!pulling) return;
        pulling = false;
        if (cue.classList.contains('active') && cue.textContent.indexOf('Release') !== -1) {
            cue.textContent = 'Refreshing...';
            loadData();
            setTimeout(function() {
                cue.classList.remove('active');
                cue.textContent = '\u2193 Pull down to refresh';
            }, 1000);
        } else {
            cue.classList.remove('active');
            cue.textContent = '\u2193 Pull down to refresh';
        }
    }, { passive: true });

    /* ── Auto-refresh (30s) ── */
    function startAutoRefresh() {
        if (refreshTimer) clearInterval(refreshTimer);
        refreshTimer = setInterval(loadData, 30000);
    }

    // Pause auto-refresh when tab not visible
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            if (refreshTimer) clearInterval(refreshTimer);
        } else {
            loadData();
            startAutoRefresh();
        }
    });

    /* ── Init ── */
    loadData();
    startAutoRefresh();
})();
</script>
"""
