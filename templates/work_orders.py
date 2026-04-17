"""
TitanForge v3.0 — Work Order Tracking Template
================================================
Full work order management page with:
  - Work order list and creation
  - Status pipeline visualization
  - QR scan start/finish workflow
  - Item-level progress tracking
  - Fabrication time metrics
"""

from templates.shared_styles import DESIGN_SYSTEM_CSS

WORK_ORDERS_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TitanForge — Work Orders</title>
<style>
""" + DESIGN_SYSTEM_CSS + """

/* ── Work Order Specific Styles ─── */
.wo-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 24px;
}

.wo-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 24px;
}

.wo-header h1 {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--tf-navy);
    margin: 0;
}

.wo-header .job-badge {
    background: var(--tf-blue);
    color: white;
    padding: 4px 14px;
    border-radius: 6px;
    font-family: 'SF Mono', monospace;
    font-size: 0.9rem;
    margin-left: 12px;
}

.wo-breadcrumb {
    font-size: 0.85rem;
    color: var(--tf-slate);
    margin-bottom: 16px;
}

.wo-breadcrumb a {
    color: var(--tf-blue-mid);
    text-decoration: none;
}

.wo-breadcrumb a:hover {
    text-decoration: underline;
}

/* ── Tabs ─── */
.wo-tabs {
    display: flex;
    gap: 0;
    border-bottom: 2px solid var(--tf-border);
    margin-bottom: 24px;
}

.wo-tab {
    padding: 10px 20px;
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--tf-slate);
    cursor: pointer;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
    transition: all 0.2s;
    background: none;
    border-top: none;
    border-left: none;
    border-right: none;
}

.wo-tab:hover {
    color: var(--tf-blue-mid);
}

.wo-tab.active {
    color: var(--tf-blue);
    border-bottom-color: var(--tf-blue);
}

.wo-tab-content {
    display: none;
}

.wo-tab-content.active {
    display: block;
}

/* ── Pipeline status bar ─── */
.status-pipeline {
    display: flex;
    align-items: center;
    gap: 0;
    margin-bottom: 24px;
    background: var(--tf-bg);
    border-radius: 10px;
    padding: 12px 16px;
    border: 1px solid var(--tf-border);
}

.pipeline-step {
    flex: 1;
    text-align: center;
    padding: 8px 4px;
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--tf-slate);
    position: relative;
    opacity: 0.5;
    transition: all 0.3s;
}

.pipeline-step.reached {
    opacity: 1;
    color: var(--tf-navy);
}

.pipeline-step.current {
    opacity: 1;
    color: var(--tf-blue);
}

.pipeline-step .step-dot {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: var(--tf-border);
    margin: 0 auto 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.7rem;
    color: white;
    transition: all 0.3s;
}

.pipeline-step.reached .step-dot {
    background: var(--tf-green);
}

.pipeline-step.current .step-dot {
    background: var(--tf-blue);
    box-shadow: 0 0 0 4px rgba(30, 64, 175, 0.15);
}

.pipeline-step.hold .step-dot {
    background: var(--tf-amber);
}

.pipeline-connector {
    width: 40px;
    height: 2px;
    background: var(--tf-border);
    flex-shrink: 0;
}

.pipeline-connector.reached {
    background: var(--tf-green);
}

/* ── Cards ─── */
.wo-card {
    background: white;
    border: 1px solid var(--tf-border);
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 16px;
    transition: box-shadow 0.2s;
}

.wo-card:hover {
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.wo-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
}

.wo-card-header h3 {
    font-size: 1.05rem;
    font-weight: 700;
    margin: 0;
    color: var(--tf-navy);
}

/* ── Status badges ─── */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    white-space: nowrap;
}

.status-badge.queued {
    background: #F1F5F9;
    color: #64748B;
}

.status-badge.approved {
    background: #DBEAFE;
    color: #1E40AF;
}

.status-badge.stickers_printed {
    background: #E0E7FF;
    color: #4338CA;
}

.status-badge.in_progress {
    background: #FEF3C7;
    color: #92400E;
}

.status-badge.complete {
    background: #D1FAE5;
    color: #065F46;
}

.status-badge.on_hold {
    background: #FEE2E2;
    color: #991B1B;
}

/* ── Progress bar ─── */
.progress-bar-wrap {
    background: #E2E8F0;
    border-radius: 8px;
    height: 10px;
    overflow: hidden;
    margin: 8px 0;
}

.progress-bar-fill {
    height: 100%;
    border-radius: 8px;
    background: linear-gradient(90deg, var(--tf-blue-mid), var(--tf-green));
    transition: width 0.5s ease;
}

/* ── Items table ─── */
.items-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
}

.items-table th {
    text-align: left;
    padding: 10px 12px;
    font-weight: 600;
    color: var(--tf-slate);
    background: var(--tf-bg);
    border-bottom: 2px solid var(--tf-border);
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.items-table td {
    padding: 10px 12px;
    border-bottom: 1px solid var(--tf-border);
    vertical-align: middle;
}

.items-table tr:last-child td {
    border-bottom: none;
}

.items-table tr:hover td {
    background: #F8FAFC;
}

.ship-mark {
    font-family: 'SF Mono', monospace;
    font-weight: 700;
    color: var(--tf-navy);
    font-size: 0.9rem;
}

.component-type-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}

.component-type-badge.column { background: #DBEAFE; color: #1E40AF; }
.component-type-badge.rafter { background: #E0E7FF; color: #4338CA; }
.component-type-badge.purlin { background: #D1FAE5; color: #065F46; }
.component-type-badge.sag_rod { background: #FEF3C7; color: #92400E; }
.component-type-badge.strap { background: #FCE7F3; color: #9D174D; }
.component-type-badge.endcap { background: #F3E8FF; color: #6B21A8; }
.component-type-badge.roofing { background: #CCFBF1; color: #0F766E; }

.machine-badge {
    font-family: 'SF Mono', monospace;
    font-size: 0.78rem;
    background: var(--tf-navy);
    color: white;
    padding: 2px 8px;
    border-radius: 4px;
}

.duration-cell {
    font-family: 'SF Mono', monospace;
    font-weight: 600;
}

/* ── QR Scan Panel ─── */
.qr-panel {
    background: linear-gradient(135deg, #1E293B, #0F172A);
    border-radius: 12px;
    padding: 24px;
    color: white;
    margin-bottom: 24px;
}

.qr-panel h3 {
    font-size: 1.1rem;
    margin: 0 0 16px;
    font-weight: 700;
}

.qr-input-row {
    display: flex;
    gap: 12px;
    align-items: center;
}

.qr-input-row input {
    flex: 1;
    padding: 12px 16px;
    border-radius: 8px;
    border: 2px solid rgba(255,255,255,0.2);
    background: rgba(255,255,255,0.1);
    color: white;
    font-size: 1rem;
    font-family: 'SF Mono', monospace;
}

.qr-input-row input::placeholder {
    color: rgba(255,255,255,0.4);
}

.qr-input-row input:focus {
    outline: none;
    border-color: var(--tf-blue-mid);
    background: rgba(255,255,255,0.15);
}

.btn-qr-start {
    padding: 12px 24px;
    border-radius: 8px;
    border: none;
    font-weight: 700;
    font-size: 0.9rem;
    cursor: pointer;
    background: var(--tf-green);
    color: white;
    transition: all 0.2s;
}

.btn-qr-start:hover {
    background: #059669;
    transform: translateY(-1px);
}

.btn-qr-finish {
    padding: 12px 24px;
    border-radius: 8px;
    border: none;
    font-weight: 700;
    font-size: 0.9rem;
    cursor: pointer;
    background: var(--tf-blue-mid);
    color: white;
    transition: all 0.2s;
}

.btn-qr-finish:hover {
    background: #1D4ED8;
    transform: translateY(-1px);
}

.qr-result {
    margin-top: 16px;
    padding: 12px 16px;
    border-radius: 8px;
    font-size: 0.9rem;
    display: none;
}

.qr-result.success {
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.3);
    display: block;
}

.qr-result.error {
    background: rgba(239, 68, 68, 0.15);
    border: 1px solid rgba(239, 68, 68, 0.3);
    display: block;
}

/* ── Metrics row ─── */
.metrics-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}

.metric-card {
    background: white;
    border: 1px solid var(--tf-border);
    border-radius: 10px;
    padding: 16px;
    text-align: center;
}

.metric-value {
    font-size: 1.8rem;
    font-weight: 800;
    color: var(--tf-navy);
    font-family: 'SF Mono', monospace;
}

.metric-label {
    font-size: 0.78rem;
    color: var(--tf-slate);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 4px;
}

/* ── Action buttons ─── */
.wo-actions {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.btn-wo {
    padding: 8px 18px;
    border-radius: 8px;
    border: none;
    font-weight: 600;
    font-size: 0.85rem;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-wo.primary {
    background: var(--tf-blue);
    color: white;
}

.btn-wo.primary:hover {
    background: var(--tf-blue-mid);
}

.btn-wo.success {
    background: var(--tf-green);
    color: white;
}

.btn-wo.success:hover {
    background: #059669;
}

.btn-wo.warning {
    background: var(--tf-amber);
    color: white;
}

.btn-wo.warning:hover {
    background: #D97706;
}

.btn-wo.danger {
    background: #EF4444;
    color: white;
}

.btn-wo.danger:hover {
    background: #DC2626;
}

.btn-wo.outline {
    background: white;
    color: var(--tf-navy);
    border: 1px solid var(--tf-border);
}

.btn-wo.outline:hover {
    background: var(--tf-bg);
}

[id^="fabMenu_"] a:hover {
    background: var(--tf-bg);
}

.btn-wo:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

/* ── Empty state ─── */
.empty-state {
    text-align: center;
    padding: 60px 20px;
    color: var(--tf-slate);
}

.empty-state .empty-icon {
    font-size: 3rem;
    margin-bottom: 12px;
    opacity: 0.4;
}

.empty-state h3 {
    font-size: 1.1rem;
    margin: 0 0 8px;
    color: var(--tf-navy);
}

.empty-state p {
    font-size: 0.9rem;
    margin: 0 0 20px;
}

/* ── Toast notification ─── */
.toast {
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

.toast.show {
    transform: translateY(0);
    opacity: 1;
}

.toast.success {
    background: #065F46;
    color: white;
}

.toast.error {
    background: #991B1B;
    color: white;
}

.toast.info {
    background: var(--tf-blue);
    color: white;
}

/* ── Item row action buttons ─── */
.item-actions {
    display: flex;
    gap: 6px;
}

.btn-item {
    padding: 4px 10px;
    border-radius: 6px;
    border: none;
    font-size: 0.75rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s;
}

.btn-item.start {
    background: var(--tf-green);
    color: white;
}

.btn-item.finish {
    background: var(--tf-blue-mid);
    color: white;
}

.btn-item:disabled {
    opacity: 0.3;
    cursor: not-allowed;
}

.checklist-panel { background: rgba(0,0,0,0.3); border-radius: 0 0 8px 8px; margin: 0; }
.checklist-step:hover { background: rgba(255,255,255,0.03); }

/* ── Responsive ─── */
@media (max-width: 768px) {
    .wo-container { padding: 12px; }
    .metrics-row { grid-template-columns: repeat(2, 1fr); }
    .wo-header { flex-wrap: wrap; gap: 8px; }
    .qr-input-row { flex-direction: column; }
    .items-table { font-size: 0.78rem; }
    .items-table th, .items-table td { padding: 6px 8px; }
}
</style>
</head>
<body>

<div class="wo-container">

    <!-- Breadcrumb -->
    <div class="wo-breadcrumb" style="display:flex;justify-content:space-between;align-items:center;">
        <div>
            <a href="/">Dashboard</a> &nbsp;/&nbsp;
            <a href="/project/{{JOB_CODE}}">{{JOB_CODE}}</a> &nbsp;/&nbsp;
            <a href="/shop-drawings/{{JOB_CODE}}">Shop Drawings</a> &nbsp;/&nbsp;
            <strong>Work Orders</strong>
        </div>
        <a href="/shop-floor" style="color:var(--tf-blue);font-size:0.85rem;text-decoration:none;display:flex;align-items:center;gap:4px;">&#9881; Shop Floor Dashboard</a>
    </div>

    <!-- Header -->
    <div class="wo-header">
        <div style="display:flex;align-items:center;">
            <h1>Work Orders</h1>
            <span class="job-badge">{{JOB_CODE}}</span>
        </div>
        <div class="wo-actions">
            <button class="btn-wo primary" onclick="createWorkOrder()">+ New Work Order</button>
            <a href="/work-station/{{JOB_CODE}}" class="btn-wo outline" style="text-decoration:none;display:inline-flex;align-items:center;gap:4px;">&#128241; Work Station</a>
            <button class="btn-wo outline" onclick="refreshAll()">Refresh</button>
        </div>
    </div>

    <!-- Tabs -->
    <div class="wo-tabs">
        <button class="wo-tab active" data-tab="overview" onclick="switchTab('overview')">Overview</button>
        <button class="wo-tab" data-tab="items" onclick="switchTab('items')">Items</button>
        <button class="wo-tab" data-tab="scan" onclick="switchTab('scan')">QR Scan</button>
    </div>

    <!-- TAB 1: OVERVIEW -->
    <div class="wo-tab-content active" id="tab-overview">
        <div id="wo-list-area">
            <div class="empty-state" id="empty-state">
                <div class="empty-icon">📋</div>
                <h3>No Work Orders Yet</h3>
                <p>Generate shop drawings first, then create a work order to track fabrication.</p>
                <button class="btn-wo primary" onclick="createWorkOrder()">Create Work Order</button>
            </div>
        </div>
    </div>

    <!-- TAB 2: ITEMS (detail view) -->
    <div class="wo-tab-content" id="tab-items">
        <div id="wo-detail-area">
            <div class="empty-state">
                <p>Select a work order from the Overview tab to view items.</p>
            </div>
        </div>
    </div>

    <!-- TAB 3: QR SCAN -->
    <div class="wo-tab-content" id="tab-scan">
        <div class="qr-panel">
            <h3>QR Code Scanner</h3>
            <p style="opacity:0.7;font-size:0.85rem;margin:0 0 16px;">
                Scan a sticker QR code or type the item ID to start/finish a fabrication task.
            </p>
            <div class="qr-input-row">
                <input type="text" id="qr-input" placeholder="Scan or type item ID (e.g., WO-SA2401-A-3F1C2E-C1)"
                       onkeydown="if(event.key==='Enter')processQRScan()">
                <button class="btn-qr-start" onclick="processQRScan('start')">Start</button>
                <button class="btn-qr-finish" onclick="processQRScan('finish')">Finish</button>
            </div>
            <div class="qr-result" id="qr-result"></div>
            <div style="margin-top:16px;padding:12px;background:rgba(0,0,0,0.2);border-radius:8px;">
              <h4 style="color:var(--tf-gold);margin:0 0 8px;">Batch Scan by Group</h4>
              <div style="display:flex;gap:6px;flex-wrap:wrap;">
                <button class="btn-qr-start" onclick="batchScan('PG','start')">Start All Purlins</button>
                <button class="btn-qr-finish" onclick="batchScan('PG','finish')">Finish All Purlins</button>
                <button class="btn-qr-start" onclick="batchScan('SR','start')">Start All Sag Rods</button>
                <button class="btn-qr-finish" onclick="batchScan('SR','finish')">Finish All Sag Rods</button>
                <button class="btn-qr-start" onclick="batchScan('HS','start')">Start All Straps</button>
                <button class="btn-qr-finish" onclick="batchScan('HS','finish')">Finish All Straps</button>
                <button class="btn-qr-start" onclick="batchScan('EC','start')">Start All Endcaps</button>
                <button class="btn-qr-finish" onclick="batchScan('EC','finish')">Finish All Endcaps</button>
              </div>
            </div>
        </div>

        <!-- Recent scan activity -->
        <div class="wo-card">
            <div class="wo-card-header">
                <h3>Recent Scan Activity</h3>
            </div>
            <div id="scan-history">
                <p style="color:var(--tf-slate);font-size:0.85rem;">No scans yet this session.</p>
            </div>
        </div>
    </div>
</div>

<!-- Toast -->
<div class="toast" id="toast"></div>

<script>
const JOB_CODE = '{{JOB_CODE}}';
let workOrders = [];
let currentWO = null;
let scanHistory = [];

// ── INIT ──
document.addEventListener('DOMContentLoaded', () => {
    refreshAll();
});

async function refreshAll() {
    await loadWorkOrders();
    renderOverview();
}

// ── API CALLS ──
async function apiCall(url, method, body) {
    const opts = { method, headers: {'Content-Type': 'application/json'} };
    if (body) opts.body = JSON.stringify(body);
    const resp = await fetch(url, opts);
    return resp.json();
}

async function loadWorkOrders() {
    const data = await apiCall(`/api/work-orders/list?job_code=${JOB_CODE}`, 'GET');
    if (data.ok) {
        workOrders = data.work_orders || [];
    }
}

async function loadWODetail(woId) {
    const data = await apiCall(`/api/work-orders/detail?job_code=${JOB_CODE}&wo_id=${woId}`, 'GET');
    if (data.ok) {
        currentWO = data.work_order;
        renderDetail();
        switchTab('items');
    } else {
        showToast(data.error || 'Failed to load work order', 'error');
    }
}

async function createWorkOrder() {
    const data = await apiCall('/api/work-orders/create', 'POST', { job_code: JOB_CODE });
    if (data.ok) {
        showToast('Work order created!', 'success');
        await refreshAll();
        // Auto-open the new one
        if (data.work_order) {
            currentWO = data.work_order;
            renderDetail();
            switchTab('items');
        }
    } else {
        showToast(data.error || 'Failed to create work order', 'error');
    }
}

async function approveWO(woId) {
    const data = await apiCall('/api/work-orders/approve', 'POST', { job_code: JOB_CODE, wo_id: woId });
    if (data.ok) {
        showToast('Work order approved!', 'success');
        currentWO = data.work_order;
        await refreshAll();
        renderDetail();
    } else {
        showToast(data.error || 'Failed to approve', 'error');
    }
}

async function markStickersPrinted(woId) {
    const data = await apiCall('/api/work-orders/stickers-printed', 'POST', { job_code: JOB_CODE, wo_id: woId });
    if (data.ok) {
        showToast('Stickers marked as printed!', 'success');
        currentWO = data.work_order;
        await refreshAll();
        renderDetail();
    } else {
        showToast(data.error || 'Failed', 'error');
    }
}

async function holdWO(woId, action) {
    const data = await apiCall('/api/work-orders/hold', 'POST', { job_code: JOB_CODE, wo_id: woId, action });
    if (data.ok) {
        showToast(action === 'hold' ? 'Work order on hold' : 'Work order resumed', 'info');
        currentWO = data.work_order;
        await refreshAll();
        renderDetail();
    } else {
        showToast(data.error || 'Failed', 'error');
    }
}

async function scanItem(itemId, action) {
    const data = await apiCall('/api/work-orders/qr-scan', 'POST', {
        job_code: JOB_CODE, item_id: itemId, action
    });
    if (data.ok) {
        showToast(data.message || `Item ${action}ed`, 'success');
        scanHistory.unshift({
            time: new Date().toLocaleTimeString(),
            item_id: itemId,
            action: data.action,
            message: data.message,
        });
        // Reload detail
        if (currentWO) {
            await loadWODetail(currentWO.work_order_id);
        }
        renderScanHistory();
    } else {
        showToast(data.error || 'Scan failed', 'error');
    }
    return data;
}

async function toggleChecklist(itemId, compType) {
    const rowId = 'checklist-' + itemId.replace(/[^a-zA-Z0-9]/g, '_');
    let existing = document.getElementById(rowId);
    if (existing) {
        existing.remove();
        return;
    }

    // Fetch/init checklist
    const data = await apiCall('/api/work-orders/checklist?job_code=' + JOB_CODE + '&item_id=' + encodeURIComponent(itemId), 'GET');
    if (!data.ok) { showToast(data.error, 'error'); return; }

    const checklist = data.checklist;
    const btn = event.target;
    const row = btn.closest('tr');
    const newRow = document.createElement('tr');
    newRow.id = rowId;
    newRow.innerHTML = '<td colspan="10" style="padding:0;"><div class="checklist-panel">' +
        '<h4 style="margin:8px 12px 4px;color:var(--tf-gold);">Fabrication Steps</h4>' +
        '<div class="checklist-steps">' +
        checklist.map(s => {
            const icon = s.checked ? '&#9745;' : (s.checkpoint ? '&#9888;' : '&#9744;');
            const style = s.checked ? 'opacity:0.6;text-decoration:line-through;' : '';
            const cpBadge = s.checkpoint ? '<span style="background:var(--tf-gold);color:#111;padding:1px 5px;border-radius:3px;font-size:0.65rem;margin-left:4px;">QC CHECKPOINT</span>' : '';
            return '<div class="checklist-step" style="' + style + 'padding:6px 12px;border-bottom:1px solid rgba(255,255,255,0.05);display:flex;align-items:center;gap:8px;cursor:' + (s.checked ? 'default' : 'pointer') + ';" ' +
                (s.checked ? '' : 'onclick="checkStep(\\\'' + itemId + '\\\',' + s.step_num + ',this)"') + '>' +
                '<span style="font-size:1.2rem;">' + icon + '</span>' +
                '<span><strong>Step ' + s.step_num + ':</strong> ' + s.title + cpBadge + '</span>' +
                '<span style="margin-left:auto;font-size:0.7rem;color:#888;">' + (s.checked ? s.checked_by + ' ' + new Date(s.checked_at).toLocaleTimeString() : s.estimated_minutes + ' min est.') + '</span>' +
                '</div>';
        }).join('') +
        '</div></div></td>';
    row.after(newRow);
}

async function checkStep(itemId, stepNum, el) {
    const data = await apiCall('/api/work-orders/checklist', 'POST', {
        job_code: JOB_CODE, item_id: itemId, step_num: stepNum
    });
    if (data.ok) {
        showToast(data.message, 'success');
        // Re-render checklist
        const rowId = 'checklist-' + itemId.replace(/[^a-zA-Z0-9]/g, '_');
        document.getElementById(rowId)?.remove();
        toggleChecklist(itemId, '');
    } else {
        showToast(data.error, 'error');
    }
}

async function processQRScan(action) {
    const input = document.getElementById('qr-input');
    const itemId = input.value.trim();
    if (!itemId) {
        showToast('Enter or scan an item ID', 'error');
        return;
    }

    const resultEl = document.getElementById('qr-result');

    // If no action specified, try to auto-detect
    if (!action) {
        action = 'start';  // default
    }

    const data = await scanItem(itemId, action);
    if (data.ok) {
        resultEl.className = 'qr-result success';
        resultEl.innerHTML = data.message || 'Scan processed';
        input.value = '';
        input.focus();
    } else {
        resultEl.className = 'qr-result error';
        resultEl.innerHTML = data.error || 'Scan failed';
    }
}

async function batchScan(prefix, action) {
    const data = await apiCall('/api/work-orders/batch-scan', 'POST', {
        job_code: JOB_CODE, prefix, action
    });
    if (data.ok) {
        showToast(data.message, 'success');
        if (currentWO) await loadWODetail(currentWO.work_order_id);
        renderDetail();
    } else {
        showToast(data.error || 'Batch scan failed', 'error');
    }
}

// ── RENDERING ──
function switchTab(tab) {
    document.querySelectorAll('.wo-tab').forEach(t => {
        t.classList.toggle('active', t.dataset.tab === tab);
    });
    document.querySelectorAll('.wo-tab-content').forEach(c => {
        c.classList.toggle('active', c.id === `tab-${tab}`);
    });
}

function renderOverview() {
    const area = document.getElementById('wo-list-area');
    const emptyState = document.getElementById('empty-state');

    if (workOrders.length === 0) {
        area.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📋</div>
                <h3>No Work Orders Yet</h3>
                <p>Generate shop drawings first, then create a work order to track fabrication.</p>
                <button class="btn-wo primary" onclick="createWorkOrder()">Create Work Order</button>
            </div>`;
        return;
    }

    let html = '';
    workOrders.forEach(wo => {
        const statusClass = wo.status.replace(/ /g, '_');
        html += `
        <div class="wo-card" style="cursor:pointer" onclick="loadWODetail('${wo.work_order_id}')">
            <div class="wo-card-header">
                <h3 style="font-family:'SF Mono',monospace;">${wo.work_order_id}</h3>
                <span class="status-badge ${statusClass}">${wo.status_label}</span>
            </div>
            <div style="display:flex;gap:24px;font-size:0.85rem;color:var(--tf-slate);margin-bottom:10px;">
                <span>Rev: <strong>${wo.revision}</strong></span>
                <span>Created: ${new Date(wo.created_at).toLocaleDateString()}</span>
                <span>Items: <strong>${wo.completed_items}/${wo.total_items}</strong></span>
                ${wo.total_fab_minutes > 0 ? `<span>Fab Time: <strong>${wo.total_fab_minutes} min</strong></span>` : ''}
            </div>
            <div class="progress-bar-wrap">
                <div class="progress-bar-fill" style="width:${wo.progress_pct}%"></div>
            </div>
            <div style="font-size:0.78rem;color:var(--tf-slate);text-align:right;">${wo.progress_pct}% complete</div>
        </div>`;
    });

    area.innerHTML = html;
}

function renderDetail() {
    if (!currentWO) return;
    const area = document.getElementById('wo-detail-area');
    const wo = currentWO;
    const statusClass = wo.status.replace(/ /g, '_');

    // Pipeline
    const steps = ['queued', 'approved', 'stickers_printed', 'in_progress', 'complete'];
    const stepLabels = ['Queued', 'Approved', 'Stickers Printed', 'In Progress', 'Complete'];
    const currentIdx = steps.indexOf(wo.status);
    const isOnHold = wo.status === 'on_hold';

    let pipelineHtml = '<div class="status-pipeline">';
    steps.forEach((step, i) => {
        let cls = '';
        if (isOnHold) {
            cls = 'hold';
        } else if (i < currentIdx) {
            cls = 'reached';
        } else if (i === currentIdx) {
            cls = 'current';
        }

        if (i > 0) {
            pipelineHtml += `<div class="pipeline-connector ${i <= currentIdx && !isOnHold ? 'reached' : ''}"></div>`;
        }
        pipelineHtml += `
            <div class="pipeline-step ${cls}">
                <div class="step-dot">${i < currentIdx && !isOnHold ? '&#10003;' : (i + 1)}</div>
                ${stepLabels[i]}
            </div>`;
    });
    pipelineHtml += '</div>';

    // Metrics
    const items = wo.items || [];
    const completedItems = items.filter(i => i.status === 'complete').length;
    const inProgressItems = items.filter(i => i.status === 'in_progress').length;
    const totalFabMin = items.reduce((s, i) => s + (i.duration_minutes || 0), 0);
    const totalEstimated = items.reduce((s, i) => s + (i.estimated_minutes || 0), 0);
    const pct = items.length > 0 ? Math.round(100 * completedItems / items.length) : 0;

    // Sticker download buttons (available once approved)
    const stickerBtns = (wo.status !== 'queued')
        ? `<div class="btn-group" style="display:inline-flex;gap:0;border:1px solid var(--tf-border);border-radius:8px;overflow:hidden;">
               <button class="btn-wo outline" style="border:none;border-radius:0;border-right:1px solid var(--tf-border);" onclick="printStickers('${wo.work_order_id}','pdf')">WO Stickers</button>
               <button class="btn-wo outline" style="border:none;border-radius:0;border-right:1px solid var(--tf-border);" onclick="printStickers('${wo.work_order_id}','zpl')">ZPL</button>
               <button class="btn-wo outline" style="border:none;border-radius:0;" onclick="printStickers('${wo.work_order_id}','csv')">CSV</button>
           </div>
           <div style="position:relative;display:inline-block;margin-left:6px;">
               <button class="btn-wo outline" onclick="toggleFabMenu('${wo.work_order_id}')">&#127991; Fab Stickers &#9662;</button>
               <div id="fabMenu_${wo.work_order_id}" style="display:none;position:absolute;top:100%;left:0;z-index:999;background:var(--tf-bg);border:1px solid var(--tf-border);border-radius:8px;box-shadow:0 4px 16px rgba(0,0,0,0.15);min-width:220px;padding:6px 0;margin-top:4px;">
                   <div style="padding:4px 12px;font-size:11px;color:var(--tf-muted);font-weight:600;">ASSEMBLY STICKERS</div>
                   <a href="#" onclick="fabSticker('${wo.work_order_id}','assembly-pdf');return false;" style="display:block;padding:6px 12px;color:var(--tf-fg);text-decoration:none;">&#128196; Assembly PDF</a>
                   <a href="#" onclick="fabSticker('${wo.work_order_id}','assembly-zpl');return false;" style="display:block;padding:6px 12px;color:var(--tf-fg);text-decoration:none;">&#9000; Assembly ZPL</a>
                   <div style="border-top:1px solid var(--tf-border);margin:4px 0;"></div>
                   <div style="padding:4px 12px;font-size:11px;color:var(--tf-muted);font-weight:600;">MATERIAL STICKERS</div>
                   <a href="#" onclick="fabSticker('${wo.work_order_id}','material-master-pdf');return false;" style="display:block;padding:6px 12px;color:var(--tf-fg);text-decoration:none;">&#128196; Material Master PDF</a>
                   <a href="#" onclick="fabSticker('${wo.work_order_id}','material-master-zpl');return false;" style="display:block;padding:6px 12px;color:var(--tf-fg);text-decoration:none;">&#9000; Material Master ZPL</a>
                   <a href="#" onclick="fabSticker('${wo.work_order_id}','material-sub-pdf');return false;" style="display:block;padding:6px 12px;color:var(--tf-fg);text-decoration:none;">&#128196; Material Sub PDF</a>
                   <a href="#" onclick="fabSticker('${wo.work_order_id}','material-sub-zpl');return false;" style="display:block;padding:6px 12px;color:var(--tf-fg);text-decoration:none;">&#9000; Material Sub ZPL</a>
                   <div style="border-top:1px solid var(--tf-border);margin:4px 0;"></div>
                   <div style="padding:4px 12px;font-size:11px;color:var(--tf-muted);font-weight:600;">NICELABEL / CSV</div>
                   <a href="#" onclick="fabSticker('${wo.work_order_id}','nlbl/assembly');return false;" style="display:block;padding:6px 12px;color:var(--tf-fg);text-decoration:none;">&#128196; Assembly NLBL Template</a>
                   <a href="#" onclick="fabSticker('${wo.work_order_id}','nlbl/material');return false;" style="display:block;padding:6px 12px;color:var(--tf-fg);text-decoration:none;">&#128196; Material NLBL Template</a>
                   <a href="#" onclick="fabSticker('${wo.work_order_id}','csv/assembly');return false;" style="display:block;padding:6px 12px;color:var(--tf-fg);text-decoration:none;">&#128462; Assembly CSV Data</a>
                   <a href="#" onclick="fabSticker('${wo.work_order_id}','csv/material');return false;" style="display:block;padding:6px 12px;color:var(--tf-fg);text-decoration:none;">&#128462; Material CSV Data</a>
               </div>
           </div>
           <button class="btn-wo outline" onclick="downloadPacketPDF('${wo.work_order_id}')" style="margin-left:6px;">&#128196; Packet PDF</button>`
        : '';

    // Action buttons based on status
    let actionsHtml = '';
    if (wo.status === 'queued') {
        actionsHtml = `<button class="btn-wo success" onclick="approveWO('${wo.work_order_id}')">Approve</button>
                       <button class="btn-wo warning" onclick="holdWO('${wo.work_order_id}','hold')">Hold</button>`;
    } else if (wo.status === 'approved') {
        actionsHtml = `${stickerBtns}
                       <button class="btn-wo primary" onclick="printAndMark('${wo.work_order_id}')">Print Stickers &amp; Mark Printed</button>
                       <button class="btn-wo warning" onclick="holdWO('${wo.work_order_id}','hold')">Hold</button>`;
    } else if (wo.status === 'on_hold') {
        actionsHtml = `<button class="btn-wo success" onclick="holdWO('${wo.work_order_id}','resume')">Resume</button>`;
    } else if (wo.status === 'stickers_printed' || wo.status === 'in_progress') {
        actionsHtml = `${stickerBtns}
                       <button class="btn-wo warning" onclick="holdWO('${wo.work_order_id}','hold')">Hold</button>`;
    } else if (wo.status === 'complete') {
        actionsHtml = stickerBtns;
    }

    // Always add edit & delete (delete disabled for in_progress)
    const canDelete = wo.status !== 'in_progress';
    actionsHtml += `
        <button class="btn-wo outline" onclick="editWO('${wo.work_order_id}')" style="margin-left:4px;">&#9998; Edit</button>
        <button class="btn-wo" style="background:#dc3545;color:#fff;margin-left:4px;${canDelete?'':'opacity:0.4;pointer-events:none;'}" onclick="deleteWO('${wo.work_order_id}')">&#128465; Delete</button>
    `;

    // Items table
    let itemsHtml = `
    <table class="items-table">
    <thead>
        <tr>
            <th>Ship Mark</th>
            <th>Type</th>
            <th>Description</th>
            <th>Qty</th>
            <th>Machine</th>
            <th>Status</th>
            <th>QC</th>
            <th>Loading</th>
            <th>Duration</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>`;

    items.forEach(item => {
        const iStatus = item.status || 'queued';
        const iStatusClass = iStatus.replace(/ /g, '_');
        const canStart = (wo.status === 'stickers_printed' || wo.status === 'in_progress')
                         && iStatus !== 'in_progress' && iStatus !== 'complete';
        const canFinish = iStatus === 'in_progress';
        const est = item.estimated_minutes > 0 ? item.estimated_minutes.toFixed(0) : '-';
        const dur = item.duration_minutes > 0 ? `${item.duration_minutes.toFixed(1)}/${est} min` : (est !== '-' ? `—/${est} min` : '—');

        itemsHtml += `
        <tr>
            <td><span class="ship-mark">${item.ship_mark}</span></td>
            <td><span class="component-type-badge ${item.component_type}">${item.component_type}</span></td>
            <td>${item.description}</td>
            <td>${item.quantity}</td>
            <td><span class="machine-badge">${item.machine}</span></td>
            <td><span class="status-badge ${iStatusClass}">${item.status === 'in_progress' ? 'In Progress' : (item.status === 'stickers_printed' ? 'Ready' : item.status.charAt(0).toUpperCase() + item.status.slice(1))}</span></td>
            <td><span class="status-badge ${item.qc_status === 'passed' ? 'complete' : (item.qc_status === 'failed' ? 'on_hold' : 'queued')}" style="font-size:0.7rem;">${(item.qc_status||'pending').toUpperCase()}</span></td>
            <td><span style="font-size:0.75rem;">${(item.loading_status||'not_ready').replace(/_/g,' ')}</span></td>
            <td class="duration-cell">${dur}</td>
            <td class="item-actions">
                <button class="btn-item start" ${canStart ? '' : 'disabled'}
                        onclick="scanItem('${item.item_id}','start')">Start</button>
                <button class="btn-item finish" ${canFinish ? '' : 'disabled'}
                        onclick="scanItem('${item.item_id}','finish')">Finish</button>
                <button class="btn-item" style="background:var(--tf-navy);color:white;"
                        onclick="printSingleSticker('${item.item_id}')" title="Print sticker">QR</button>
                <a href="/wo/${JOB_CODE}/${item.item_id}" target="_blank" class="btn-item" style="background:var(--tf-blue);color:white;text-decoration:none;display:inline-block;text-align:center;" title="Mobile scan page">&#128241;</a>
                <button class="btn-item" style="background:var(--tf-gold);color:#111;"
        onclick="toggleChecklist('${item.item_id}','${item.component_type}')" title="Fab Steps">&#9776;</button>
            </td>
        </tr>`;
    });
    itemsHtml += '</tbody></table>';

    area.innerHTML = `
        <div class="wo-card-header" style="margin-bottom:16px;">
            <div>
                <h3 style="font-family:'SF Mono',monospace;font-size:1.1rem;">${wo.work_order_id}</h3>
                <div style="font-size:0.82rem;color:var(--tf-slate);margin-top:4px;">
                    Rev ${wo.revision} &bull; Created ${new Date(wo.created_at).toLocaleString()}
                    ${wo.approved_by ? ` &bull; Approved by ${wo.approved_by}` : ''}
                    ${wo.project_name ? ` &bull; ${wo.project_name}` : ''}
                    ${wo.customer_name ? ` &mdash; ${wo.customer_name}` : ''}
                </div>
                ${wo.building_specs ? `<div style="font-size:0.8rem;color:var(--tf-blue);margin-top:2px;font-weight:600;">${wo.building_specs}${wo.priority && wo.priority !== 'normal' ? ' &bull; <span style="color:#dc3545;">'+wo.priority.toUpperCase()+'</span>' : ''}</div>` : ''}
            </div>
            <div style="display:flex;gap:8px;align-items:center;">
                ${isOnHold ? '<span class="status-badge on_hold">ON HOLD</span>' : ''}
                ${actionsHtml}
            </div>
        </div>

        ${pipelineHtml}

        <div class="metrics-row">
            <div class="metric-card">
                <div class="metric-value">${items.length}</div>
                <div class="metric-label">Total Items</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${completedItems}</div>
                <div class="metric-label">Completed</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${inProgressItems}</div>
                <div class="metric-label">In Progress</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${pct}%</div>
                <div class="metric-label">Progress</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${totalFabMin > 0 ? totalFabMin.toFixed(1) : '—'} / ${totalEstimated > 0 ? totalEstimated.toFixed(1) : '—'}</div>
                <div class="metric-label">Actual / Est. Minutes</div>
            </div>
        </div>

        <div class="progress-bar-wrap" style="height:14px;margin-bottom:24px;">
            <div class="progress-bar-fill" style="width:${pct}%"></div>
        </div>

        <div class="wo-card">
            <div class="wo-card-header">
                <h3>Fabrication Items</h3>
                <span style="font-size:0.82rem;color:var(--tf-slate);">${completedItems} of ${items.length} complete</span>
            </div>
            ${itemsHtml}
        </div>
    `;
}

function renderScanHistory() {
    const el = document.getElementById('scan-history');
    if (scanHistory.length === 0) {
        el.innerHTML = '<p style="color:var(--tf-slate);font-size:0.85rem;">No scans yet this session.</p>';
        return;
    }
    let html = '<table class="items-table"><thead><tr><th>Time</th><th>Item</th><th>Action</th><th>Result</th></tr></thead><tbody>';
    scanHistory.forEach(s => {
        const actionBadge = s.action === 'started'
            ? '<span class="status-badge in_progress">Started</span>'
            : '<span class="status-badge complete">Finished</span>';
        html += `<tr>
            <td style="font-family:'SF Mono',monospace;">${s.time}</td>
            <td style="font-family:'SF Mono',monospace;font-size:0.78rem;">${s.item_id}</td>
            <td>${actionBadge}</td>
            <td>${s.message}</td>
        </tr>`;
    });
    html += '</tbody></table>';
    el.innerHTML = html;
}

// ── TOAST ──
// ── STICKER FUNCTIONS ──
function printStickers(woId, format) {
    const url = `/api/work-orders/stickers/${format}?job_code=${JOB_CODE}&wo_id=${woId}`;
    window.open(url, '_blank');
}

function printSingleSticker(itemId) {
    const url = `/api/work-orders/stickers/single?job_code=${JOB_CODE}&item_id=${itemId}`;
    window.open(url, '_blank');
}

function fabSticker(woId, type) {
    const url = `/api/work-orders/fab-stickers/${type}?job_code=${JOB_CODE}&wo_id=${woId}`;
    window.open(url, '_blank');
    // Close menu after click
    const menu = document.getElementById('fabMenu_' + woId);
    if (menu) menu.style.display = 'none';
}

function toggleFabMenu(woId) {
    // Close any other open menus first
    document.querySelectorAll('[id^="fabMenu_"]').forEach(m => {
        if (m.id !== 'fabMenu_' + woId) m.style.display = 'none';
    });
    const menu = document.getElementById('fabMenu_' + woId);
    if (menu) menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
}

// Close fab menus when clicking outside
document.addEventListener('click', function(e) {
    if (!e.target.closest('[id^="fabMenu_"]') && !e.target.textContent.includes('Fab Stickers')) {
        document.querySelectorAll('[id^="fabMenu_"]').forEach(m => m.style.display = 'none');
    }
});

async function printAndMark(woId) {
    // Open sticker PDF in new tab
    printStickers(woId, 'pdf');
    // Mark stickers as printed
    await markStickersPrinted(woId);
}

function downloadPacketPDF(woId) {
    const url = `/api/work-orders/packet/pdf?job_code=${JOB_CODE}&wo_id=${woId}`;
    window.open(url, '_blank');
}

async function editWO(woId) {
    if (!currentWO) return;
    const priority = prompt('Priority (normal / rush / hot):', currentWO.priority || 'normal');
    if (priority === null) return;
    const dueDate = prompt('Due date (YYYY-MM-DD or leave empty):', currentWO.due_date || '');
    if (dueDate === null) return;
    const deliveryDate = prompt('Delivery date (YYYY-MM-DD or leave empty):', currentWO.delivery_date || '');
    if (deliveryDate === null) return;
    const notes = prompt('Notes:', currentWO.notes || '');
    if (notes === null) return;

    const data = await apiCall('/api/work-orders/edit', 'POST', {
        job_code: JOB_CODE, wo_id: woId,
        priority, due_date: dueDate, delivery_date: deliveryDate, notes
    });
    if (data.ok) {
        showToast('Work order updated!', 'success');
        currentWO = data.work_order;
        await refreshAll();
        renderDetail();
    } else {
        showToast(data.error || 'Failed to edit', 'error');
    }
}

async function deleteWO(woId) {
    if (!confirm('Are you sure you want to delete this work order? This cannot be undone.')) return;
    const data = await apiCall('/api/work-orders/delete', 'POST', { job_code: JOB_CODE, wo_id: woId });
    if (data.ok) {
        showToast('Work order deleted', 'info');
        currentWO = null;
        await refreshAll();
        switchTab('overview');
    } else {
        showToast(data.error || 'Failed to delete', 'error');
    }
}

function showToast(msg, type) {
    const toast = document.getElementById('toast');
    toast.textContent = msg;
    toast.className = `toast ${type || 'info'} show`;
    setTimeout(() => { toast.className = 'toast'; }, 4000);
}

// Auto-refresh work order detail every 30 seconds (Rec 8)
setInterval(async () => {
    if (currentWO) {
        await loadWODetail(currentWO.work_order_id);
        renderDetail();
    }
}, 30000);
</script>
</body>
</html>
"""
