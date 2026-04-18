"""
TitanForge v3.0 — Digital Work Station Template
================================================
Tablet/phone-friendly interface for shop floor workers.
Features:
  - Machine-based queue (primary): select your machine, see your items
  - All Items tab: browse all items across all machines
  - Step-by-step guided fabrication with progress tracking
  - QR scan start/finish integration
  - Large touch-friendly UI elements for gloved hands
"""

from templates.shared_styles import DESIGN_SYSTEM_CSS

WORK_STATION_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>TitanForge — Work Station</title>
<style>
""" + DESIGN_SYSTEM_CSS + r"""

/* ── Work Station — Touch-Optimized ─── */
* { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }

body {
    margin: 0;
    font-family: var(--tf-font);
    background: var(--tf-bg);
    color: var(--tf-navy);
    overflow-x: hidden;
}

.ws-container {
    max-width: 900px;
    margin: 0 auto;
    padding: 12px;
}

/* ── Top Bar ─── */
.ws-topbar {
    background: var(--tf-navy);
    color: #fff;
    padding: 12px 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: sticky;
    top: 0;
    z-index: 100;
}

.ws-topbar-left {
    display: flex;
    align-items: center;
    gap: 12px;
}

.ws-topbar h1 {
    margin: 0;
    font-size: 1.2rem;
    font-weight: 700;
}

.ws-topbar .job-badge {
    background: var(--tf-gold);
    color: var(--tf-navy);
    padding: 3px 10px;
    border-radius: 4px;
    font-size: 0.85rem;
    font-weight: 600;
}

.ws-topbar-right {
    display: flex;
    align-items: center;
    gap: 10px;
}

.ws-topbar-right a {
    color: rgba(255,255,255,0.7);
    text-decoration: none;
    font-size: 0.8rem;
}

.ws-worker-name {
    font-size: 0.85rem;
    color: var(--tf-gold);
    font-weight: 600;
}

/* ── View Tabs ─── */
.ws-tabs {
    display: flex;
    gap: 0;
    background: #fff;
    border-radius: 10px;
    overflow: hidden;
    margin: 12px 0;
    box-shadow: var(--tf-shadow);
}

.ws-tab {
    flex: 1;
    padding: 14px 8px;
    text-align: center;
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
    border: none;
    background: #fff;
    color: var(--tf-gray);
    transition: all 0.2s;
    border-bottom: 3px solid transparent;
}

.ws-tab.active {
    color: var(--tf-blue);
    border-bottom-color: var(--tf-blue);
    background: #EFF6FF;
}

.ws-tab:active { background: #DBEAFE; }

/* ── Machine Selector ─── */
.machine-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 10px;
    margin-bottom: 16px;
}

.machine-card {
    background: #fff;
    border: 2px solid var(--tf-border);
    border-radius: 10px;
    padding: 16px 12px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s;
}

.machine-card:active { transform: scale(0.97); }

.machine-card.selected {
    border-color: var(--tf-blue);
    background: #EFF6FF;
    box-shadow: 0 0 0 3px rgba(30,64,175,0.15);
}

.machine-card.has-active {
    border-color: var(--tf-green);
}

.machine-card .machine-icon {
    font-size: 1.8rem;
    margin-bottom: 6px;
}

.machine-card .machine-name {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--tf-navy);
    line-height: 1.2;
}

.machine-card .machine-count {
    font-size: 0.75rem;
    color: var(--tf-gray);
    margin-top: 4px;
}

.machine-card .machine-count .active-dot {
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--tf-green);
    margin-right: 3px;
    animation: pulse-dot 1.5s infinite;
}

@keyframes pulse-dot {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

/* ── Item Queue ─── */
.queue-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.queue-header h2 {
    margin: 0;
    font-size: 1.1rem;
    color: var(--tf-navy);
}

.queue-count {
    background: var(--tf-blue);
    color: #fff;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
}

.item-card {
    background: #fff;
    border-radius: 10px;
    border: 2px solid var(--tf-border);
    margin-bottom: 10px;
    overflow: hidden;
    cursor: pointer;
    transition: all 0.2s;
}

.item-card:active { transform: scale(0.99); }

.item-card.in-progress {
    border-color: var(--tf-green);
    box-shadow: 0 0 0 2px rgba(5,150,105,0.12);
}

.item-card.complete {
    opacity: 0.6;
    border-color: var(--tf-border);
}

.item-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 16px 8px;
}

.item-ship-mark {
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--tf-navy);
}

.item-status-badge {
    padding: 4px 12px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
}

.badge-queued { background: #F1F5F9; color: #64748B; }
.badge-approved { background: #EFF6FF; color: #1E40AF; }
.badge-stickers_printed { background: #FEF3C7; color: #92400E; }
.badge-in_progress { background: #D1FAE5; color: #065F46; }
.badge-complete { background: #F0FDF4; color: #166534; }

.item-card-body {
    padding: 0 16px 14px;
}

.item-desc {
    font-size: 0.85rem;
    color: var(--tf-gray);
    margin-bottom: 6px;
}

.item-meta {
    display: flex;
    gap: 12px;
    font-size: 0.75rem;
    color: var(--tf-gray);
}

.item-meta span { display: flex; align-items: center; gap: 3px; }

/* ── Step-by-Step View ─── */
.step-view {
    display: none;
}

.step-view.active { display: block; }

.step-back-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    background: none;
    border: none;
    color: var(--tf-blue);
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
    padding: 8px 0;
    margin-bottom: 8px;
}

.step-item-header {
    background: var(--tf-navy);
    color: #fff;
    padding: 16px;
    border-radius: 10px;
    margin-bottom: 14px;
}

.step-item-header h2 {
    margin: 0 0 4px;
    font-size: 1.4rem;
}

.step-item-header .step-desc {
    color: rgba(255,255,255,0.7);
    font-size: 0.85rem;
}

.step-progress {
    display: flex;
    align-items: center;
    gap: 4px;
    margin-top: 10px;
}

.step-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: rgba(255,255,255,0.25);
    transition: all 0.3s;
}

.step-dot.done { background: var(--tf-green); }
.step-dot.current { background: var(--tf-gold); width: 14px; height: 14px; }

.step-progress-text {
    margin-left: 8px;
    font-size: 0.8rem;
    color: rgba(255,255,255,0.6);
}

/* Current step card */
.current-step-card {
    background: #fff;
    border-radius: 12px;
    box-shadow: var(--tf-shadow-lg);
    overflow: hidden;
    margin-bottom: 14px;
}

.step-number-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    background: var(--tf-blue);
    color: #fff;
}

.step-number-bar .step-num {
    font-size: 1rem;
    font-weight: 700;
}

.step-number-bar .step-est {
    font-size: 0.8rem;
    opacity: 0.8;
}

.step-title {
    font-size: 1.15rem;
    font-weight: 700;
    padding: 16px 16px 8px;
    color: var(--tf-navy);
}

.step-instruction {
    padding: 0 16px 12px;
    font-size: 0.95rem;
    line-height: 1.55;
    color: #334155;
}

.step-tool {
    padding: 0 16px 10px;
    font-size: 0.85rem;
    color: var(--tf-gray);
}

.step-tool strong { color: var(--tf-navy); }

.step-safety {
    margin: 0 16px 12px;
    padding: 10px 14px;
    background: #FEF2F2;
    border-left: 4px solid #DC2626;
    border-radius: 6px;
    font-size: 0.85rem;
    color: #991B1B;
}

.step-safety strong { color: #DC2626; }

.step-checkpoint {
    margin: 0 16px 12px;
    padding: 10px 14px;
    background: #FFFBEB;
    border-left: 4px solid var(--tf-gold);
    border-radius: 6px;
    font-size: 0.85rem;
    color: #92400E;
}

/* Step navigation buttons */
.step-nav {
    display: flex;
    gap: 10px;
    padding: 0 16px 16px;
}

.step-nav button {
    flex: 1;
    padding: 16px;
    border: none;
    border-radius: 10px;
    font-size: 1rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.15s;
}

.step-nav button:active { transform: scale(0.97); }

.btn-prev {
    background: #F1F5F9;
    color: #64748B;
}

.btn-next {
    background: var(--tf-blue);
    color: #fff;
}

.btn-complete-step {
    background: var(--tf-green);
    color: #fff;
}

/* ── Action buttons (Start / Finish) ─── */
.action-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #fff;
    border-top: 2px solid var(--tf-border);
    padding: 12px 16px;
    display: flex;
    gap: 10px;
    z-index: 50;
    max-width: 900px;
    margin: 0 auto;
}

.action-bar button {
    flex: 1;
    padding: 18px;
    border: none;
    border-radius: 10px;
    font-size: 1.1rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.15s;
}

.action-bar button:active { transform: scale(0.97); }

.btn-start {
    background: var(--tf-green);
    color: #fff;
}

.btn-finish {
    background: var(--tf-blue);
    color: #fff;
}

.btn-start:disabled, .btn-finish:disabled {
    opacity: 0.4;
    cursor: not-allowed;
}

/* ── Timer ─── */
.active-timer {
    background: #D1FAE5;
    border: 2px solid var(--tf-green);
    border-radius: 10px;
    padding: 12px 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.timer-label {
    font-size: 0.85rem;
    color: #065F46;
    font-weight: 600;
}

.timer-value {
    font-size: 1.4rem;
    font-weight: 700;
    color: #065F46;
    font-variant-numeric: tabular-nums;
}

/* ── Empty state ─── */
.empty-state {
    text-align: center;
    padding: 40px 20px;
    color: var(--tf-gray);
}

.empty-state .empty-icon { font-size: 3rem; margin-bottom: 10px; }
.empty-state h3 { margin: 0 0 6px; color: var(--tf-navy); }
.empty-state p { font-size: 0.9rem; }

/* ── Toast ─── */
.ws-toast {
    position: fixed;
    top: 60px;
    left: 50%;
    transform: translateX(-50%) translateY(-100px);
    background: var(--tf-navy);
    color: #fff;
    padding: 14px 24px;
    border-radius: 10px;
    font-weight: 600;
    z-index: 200;
    transition: transform 0.3s ease;
    max-width: 90%;
    text-align: center;
}

.ws-toast.show { transform: translateX(-50%) translateY(0); }
.ws-toast.success { background: var(--tf-green); }
.ws-toast.error { background: #DC2626; }

/* Fix bottom padding for action bar */
.ws-content { padding-bottom: 90px; }

/* ── Responsive ─── */
@media (max-width: 600px) {
    .machine-grid { grid-template-columns: repeat(2, 1fr); }
    .ws-topbar h1 { font-size: 1rem; }
}
</style>
<!-- html5-qrcode CDN for camera scanning -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/html5-qrcode/2.3.8/html5-qrcode.min.js"></script>
</head>
<body>

<!-- Top Bar -->
<div class="ws-topbar">
    <div class="ws-topbar-left">
        <h1>Work Station</h1>
        <span class="job-badge">{{JOB_CODE}}</span>
    </div>
    <div class="ws-topbar-right">
        <span class="ws-worker-name" id="workerName">{{USER_NAME}}</span>
        <a href="/work-orders/{{JOB_CODE}}">WO Manager</a>
        <a href="/shop-floor">Shop Floor</a>
    </div>
</div>

<div class="ws-container">

    <!-- View Tabs -->
    <div class="ws-tabs">
        <button class="ws-tab active" onclick="switchTab('machine')" id="tabMachine">My Machine</button>
        <button class="ws-tab" onclick="switchTab('all')" id="tabAll">All Items</button>
        <button class="ws-tab" onclick="switchTab('scan')" id="tabScan">QR Scan</button>
    </div>

    <div class="ws-content">

        <!-- Machine Queue View (default) -->
        <div id="machineView">
            <div class="machine-grid" id="machineGrid"></div>
            <div id="machineQueue"></div>
        </div>

        <!-- All Items View -->
        <div id="allView" style="display:none;">
            <div id="allItemsList"></div>
        </div>

        <!-- QR Scan View -->
        <div id="scanView" style="display:none;">
            <div style="text-align:center;padding:20px;">
                <!-- Camera viewfinder -->
                <div id="qrReaderBox" style="width:100%;max-width:400px;margin:0 auto 12px;
                    border-radius:12px;overflow:hidden;background:#000;min-height:200px;display:none;">
                    <div id="qr-reader" style="width:100%;"></div>
                </div>

                <!-- Camera controls -->
                <div id="camControls" style="margin-bottom:16px;">
                    <button id="btnStartCam" onclick="startCameraScanner()"
                        style="padding:14px 28px;font-size:1.1rem;font-weight:600;
                        background:var(--tf-gold,#F6AE2D);color:#0F172A;border:none;
                        border-radius:10px;cursor:pointer;">
                        &#128247; Open Camera
                    </button>
                    <button id="btnStopCam" onclick="stopCameraScanner()"
                        style="padding:10px 20px;font-size:0.95rem;background:#DC2626;color:#fff;
                        border:none;border-radius:8px;cursor:pointer;display:none;margin-left:8px;">
                        &#9632; Stop
                    </button>
                    <button id="btnFlipCam" onclick="flipCamera()"
                        style="padding:10px 20px;font-size:0.95rem;background:var(--tf-border,#334155);
                        color:#F1F5F9;border:none;border-radius:8px;cursor:pointer;display:none;margin-left:8px;">
                        &#128260; Flip
                    </button>
                </div>

                <div id="camStatus" style="color:var(--tf-gray);font-size:0.85rem;margin-bottom:12px;"></div>

                <!-- Fallback text input for hardware scanners -->
                <details style="margin-top:12px;max-width:400px;margin-left:auto;margin-right:auto;">
                    <summary style="color:var(--tf-gray);font-size:0.85rem;cursor:pointer;
                        padding:8px;">Or type / use barcode gun</summary>
                    <input type="text" id="scanInput" placeholder="Type item ID and press Enter..."
                        style="width:100%;padding:14px;font-size:1rem;margin-top:8px;
                        border:2px solid var(--tf-border);border-radius:10px;text-align:center;
                        background:var(--tf-card,#1E293B);color:#F1F5F9;">
                </details>

                <div id="scanResult" style="margin-top:16px;"></div>
            </div>
        </div>

        <!-- Step-by-Step Detail View -->
        <div class="step-view" id="stepView">
            <button class="step-back-btn" onclick="exitStepView()">&#8592; Back to Queue</button>

            <div class="step-item-header" id="stepItemHeader">
                <h2 id="stepShipMark"></h2>
                <div class="step-desc" id="stepDesc"></div>
                <div class="step-progress" id="stepProgress"></div>
            </div>

            <!-- Timer (shown when item is in progress) -->
            <div class="active-timer" id="activeTimer" style="display:none;">
                <span class="timer-label">Fabrication Time</span>
                <span class="timer-value" id="timerValue">00:00:00</span>
            </div>

            <!-- Current Step -->
            <div id="currentStepContainer"></div>
        </div>
    </div>
</div>

<!-- Action Bar (fixed bottom) -->
<div class="action-bar" id="actionBar" style="display:none;">
    <button class="btn-start" id="btnStart" onclick="startItem()">
        &#9654; START FABRICATION
    </button>
    <button class="btn-finish" id="btnFinish" onclick="finishItem()" style="display:none;">
        &#9632; FINISH &amp; COMPLETE
    </button>
</div>

<!-- Toast -->
<div class="ws-toast" id="wsToast"></div>

<script>
const JOB_CODE = "{{JOB_CODE}}";
const USER_NAME = "{{USER_NAME}}";

let workOrderData = null;
let allItems = [];
let selectedMachine = null;
let currentItem = null;
let currentSteps = [];
let currentStepIdx = 0;
let completedSteps = new Set();
let timerInterval = null;

// ── Init ──
document.addEventListener('DOMContentLoaded', loadWorkStation);

async function loadWorkStation() {
    try {
        const resp = await fetch('/api/work-station/data?job_code=' + encodeURIComponent(JOB_CODE));
        const data = await resp.json();
        if (!data.ok) { showToast('Error: ' + (data.error || 'Failed to load'), 'error'); return; }

        workOrderData = data;
        allItems = data.items || [];

        renderMachineGrid(data.machines || {});
        renderAllItems();

        // Auto-select machine if only one has items
        const machinesWithItems = Object.entries(data.machines || {}).filter(([k,v]) => v.item_count > 0);
        if (machinesWithItems.length === 1) {
            selectMachine(machinesWithItems[0][0]);
        }
    } catch (e) {
        showToast('Failed to connect: ' + e.message, 'error');
    }
}

// ── Machine Grid ──
function renderMachineGrid(machines) {
    const grid = document.getElementById('machineGrid');
    const icons = {
        'C1': '&#9881;', 'C2': '&#9881;', 'Z1': '&#9881;', 'P1': '&#9881;',
        'ANGLE': '&#128295;', 'SPARTAN': '&#127968;', 'WELDING': '&#128293;',
        'REBAR': '&#9881;', 'CLEANING': '&#10024;'
    };

    let html = '';
    const sorted = Object.entries(machines).sort((a,b) => b[1].item_count - a[1].item_count);

    for (const [mId, mInfo] of sorted) {
        if (mInfo.item_count === 0) continue;
        const hasActive = mInfo.in_progress > 0;
        html += '<div class="machine-card ' + (hasActive ? 'has-active ' : '') +
                (selectedMachine === mId ? 'selected' : '') +
                '" onclick="selectMachine(\\''+mId+'\\')">' +
                '<div class="machine-icon">' + (icons[mId] || '&#9881;') + '</div>' +
                '<div class="machine-name">' + escHtml(mInfo.name || mId) + '</div>' +
                '<div class="machine-count">' +
                (hasActive ? '<span class="active-dot"></span>' + mInfo.in_progress + ' active, ' : '') +
                mInfo.item_count + ' total</div></div>';
    }

    if (!html) {
        html = '<div class="empty-state"><div class="empty-icon">&#128230;</div>' +
               '<h3>No Items Assigned</h3><p>No work order items are assigned to machines yet.</p></div>';
    }
    grid.innerHTML = html;
}

function selectMachine(machineId) {
    selectedMachine = machineId;
    // Re-render grid to show selection
    renderMachineGrid(workOrderData.machines || {});
    renderMachineQueue();
}

function renderMachineQueue() {
    const container = document.getElementById('machineQueue');
    if (!selectedMachine) {
        container.innerHTML = '<div class="empty-state"><div class="empty-icon">&#128073;</div>' +
            '<h3>Select a Machine</h3><p>Tap a machine above to see its item queue.</p></div>';
        return;
    }

    const items = allItems.filter(i => i.machine === selectedMachine);
    // Sort: in_progress first, then queued/approved, then complete
    const order = {'in_progress': 0, 'approved': 1, 'stickers_printed': 1, 'queued': 2, 'complete': 3};
    items.sort((a,b) => (order[a.status] || 2) - (order[b.status] || 2));

    const machineInfo = (workOrderData.machines || {})[selectedMachine] || {};
    let html = '<div class="queue-header"><h2>' + escHtml(machineInfo.name || selectedMachine) + '</h2>' +
               '<span class="queue-count">' + items.length + ' items</span></div>';

    if (items.length === 0) {
        html += '<div class="empty-state"><h3>Queue Empty</h3><p>No items in this machine\\'s queue.</p></div>';
    } else {
        for (const item of items) {
            html += renderItemCard(item);
        }
    }
    container.innerHTML = html;
}

function renderAllItems() {
    const container = document.getElementById('allItemsList');
    const items = [...allItems];
    const order = {'in_progress': 0, 'approved': 1, 'stickers_printed': 1, 'queued': 2, 'complete': 3};
    items.sort((a,b) => (order[a.status] || 2) - (order[b.status] || 2));

    let html = '<div class="queue-header"><h2>All Items</h2>' +
               '<span class="queue-count">' + items.length + ' items</span></div>';

    for (const item of items) {
        html += renderItemCard(item);
    }
    container.innerHTML = html;
}

function renderItemCard(item) {
    const statusClass = 'badge-' + item.status;
    const cardClass = item.status === 'in_progress' ? 'in-progress' :
                      item.status === 'complete' ? 'complete' : '';
    return '<div class="item-card ' + cardClass + '" onclick="openItem(\\''+item.item_id+'\\')">' +
        '<div class="item-card-header">' +
            '<span class="item-ship-mark">' + escHtml(item.ship_mark) + '</span>' +
            '<span class="item-status-badge ' + statusClass + '">' + item.status.replace('_',' ') + '</span>' +
        '</div>' +
        '<div class="item-card-body">' +
            '<div class="item-desc">' + escHtml(item.description || '') + '</div>' +
            '<div class="item-meta">' +
                '<span>&#9881; ' + escHtml(item.machine || '—') + '</span>' +
                '<span>&#128196; ' + escHtml(item.drawing_ref || '') + '</span>' +
                (item.started_at ? '<span>&#9200; Started ' + formatTime(item.started_at) + '</span>' : '') +
                (item.duration_minutes ? '<span>&#9201; ' + item.duration_minutes.toFixed(1) + ' min</span>' : '') +
            '</div>' +
        '</div></div>';
}

// ── Step-by-Step View ──
async function openItem(itemId) {
    const item = allItems.find(i => i.item_id === itemId);
    if (!item) return;
    currentItem = item;
    currentStepIdx = 0;
    completedSteps = new Set();

    // Load steps
    try {
        const resp = await fetch('/api/work-station/steps?job_code=' + encodeURIComponent(JOB_CODE) +
                                 '&item_id=' + encodeURIComponent(itemId));
        const data = await resp.json();
        currentSteps = data.steps || [];
    } catch(e) {
        currentSteps = [];
    }

    // Show step view
    document.getElementById('machineView').style.display = 'none';
    document.getElementById('allView').style.display = 'none';
    document.getElementById('scanView').style.display = 'none';
    document.getElementById('stepView').className = 'step-view active';

    // Action bar
    const actionBar = document.getElementById('actionBar');
    const btnStart = document.getElementById('btnStart');
    const btnFinish = document.getElementById('btnFinish');
    actionBar.style.display = 'flex';

    if (item.status === 'in_progress') {
        btnStart.style.display = 'none';
        btnFinish.style.display = 'block';
        startTimer(item.started_at);
    } else if (item.status === 'complete') {
        btnStart.style.display = 'none';
        btnFinish.style.display = 'none';
    } else {
        btnStart.style.display = 'block';
        btnFinish.style.display = 'none';
    }

    renderStepView();
}

function renderStepView() {
    const item = currentItem;
    if (!item) return;

    // Header
    document.getElementById('stepShipMark').textContent = item.ship_mark;
    document.getElementById('stepDesc').textContent = item.description || '';

    // Progress dots
    let dotsHtml = '';
    for (let i = 0; i < currentSteps.length; i++) {
        const cls = completedSteps.has(i) ? 'done' : (i === currentStepIdx ? 'current' : '');
        dotsHtml += '<div class="step-dot ' + cls + '"></div>';
    }
    dotsHtml += '<span class="step-progress-text">Step ' + (currentStepIdx + 1) + ' of ' + currentSteps.length + '</span>';
    document.getElementById('stepProgress').innerHTML = dotsHtml;

    // Timer
    const timerDiv = document.getElementById('activeTimer');
    if (item.status === 'in_progress') {
        timerDiv.style.display = 'flex';
    } else {
        timerDiv.style.display = 'none';
    }

    // Current step
    const container = document.getElementById('currentStepContainer');
    if (currentSteps.length === 0) {
        container.innerHTML = '<div class="empty-state"><h3>No Steps Defined</h3>' +
            '<p>No fabrication steps are configured for this component type.</p></div>';
        return;
    }

    const step = currentSteps[currentStepIdx];
    let html = '<div class="current-step-card">' +
        '<div class="step-number-bar">' +
            '<span class="step-num">Step ' + step.step_num + ' of ' + currentSteps.length + '</span>' +
            (step.estimated_minutes ? '<span class="step-est">~' + step.estimated_minutes + ' min</span>' : '') +
        '</div>' +
        '<div class="step-title">' + escHtml(step.title) + '</div>' +
        '<div class="step-instruction">' + escHtml(step.instruction) + '</div>';

    if (step.tool) {
        html += '<div class="step-tool"><strong>Tools needed:</strong> ' + escHtml(step.tool) + '</div>';
    }

    if (step.safety) {
        html += '<div class="step-safety"><strong>SAFETY:</strong> ' + escHtml(step.safety) + '</div>';
    }

    if (step.checkpoint) {
        html += '<div class="step-checkpoint"><strong>QUALITY CHECKPOINT:</strong> ' +
                'This step requires inspection before proceeding. Verify quality and dimensions.</div>';
    }

    // Nav buttons
    html += '<div class="step-nav">';
    if (currentStepIdx > 0) {
        html += '<button class="btn-prev" onclick="prevStep()">&#8592; Previous</button>';
    }
    if (currentStepIdx < currentSteps.length - 1) {
        html += '<button class="btn-next" onclick="nextStep()">Next Step &#8594;</button>';
    } else {
        html += '<button class="btn-complete-step" onclick="allStepsDone()">&#10003; All Steps Done</button>';
    }
    html += '</div></div>';

    container.innerHTML = html;
}

function nextStep() {
    completedSteps.add(currentStepIdx);
    if (currentStepIdx < currentSteps.length - 1) {
        currentStepIdx++;
        renderStepView();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

function prevStep() {
    if (currentStepIdx > 0) {
        currentStepIdx--;
        renderStepView();
    }
}

function allStepsDone() {
    completedSteps.add(currentStepIdx);
    renderStepView();
    showToast('All steps complete! Tap FINISH to complete this item.', 'success');
    // Show finish button
    document.getElementById('btnStart').style.display = 'none';
    document.getElementById('btnFinish').style.display = 'block';
}

function exitStepView() {
    document.getElementById('stepView').className = 'step-view';
    document.getElementById('actionBar').style.display = 'none';
    stopTimer();
    currentItem = null;
    currentSteps = [];

    // Show the previous tab
    const activeTab = document.querySelector('.ws-tab.active');
    if (activeTab) switchTab(activeTab.id.replace('tab','').toLowerCase());
}

// ── Start / Finish ──
async function startItem() {
    if (!currentItem) return;
    try {
        const resp = await fetch('/api/work-orders/qr-scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                job_code: JOB_CODE,
                item_id: currentItem.item_id,
                action: 'start',
                scanned_by: USER_NAME
            })
        });
        const data = await resp.json();
        if (data.ok) {
            showToast('Started: ' + currentItem.ship_mark, 'success');
            currentItem.status = 'in_progress';
            currentItem.started_at = new Date().toISOString();
            document.getElementById('btnStart').style.display = 'none';
            document.getElementById('btnFinish').style.display = 'block';
            startTimer(currentItem.started_at);
            renderStepView();
            // Update lists
            updateItemInList(currentItem);
        } else {
            showToast(data.error || 'Failed to start', 'error');
        }
    } catch(e) {
        showToast('Network error: ' + e.message, 'error');
    }
}

async function finishItem() {
    if (!currentItem) return;
    if (!confirm('Complete fabrication for ' + currentItem.ship_mark + '?')) return;
    try {
        const resp = await fetch('/api/work-orders/qr-scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                job_code: JOB_CODE,
                item_id: currentItem.item_id,
                action: 'finish',
                scanned_by: USER_NAME
            })
        });
        const data = await resp.json();
        if (data.ok) {
            const dur = data.duration_minutes ? data.duration_minutes.toFixed(1) + ' min' : '';
            showToast('Completed: ' + currentItem.ship_mark + ' (' + dur + ')', 'success');
            stopTimer();
            currentItem.status = 'complete';
            currentItem.duration_minutes = data.duration_minutes || 0;
            document.getElementById('btnFinish').style.display = 'none';
            updateItemInList(currentItem);

            // Auto-advance to next item in queue after 2 seconds
            setTimeout(() => {
                exitStepView();
                if (data.wo_complete) {
                    showToast('WORK ORDER COMPLETE! All items finished.', 'success');
                }
            }, 2000);
        } else {
            showToast(data.error || 'Failed to finish', 'error');
        }
    } catch(e) {
        showToast('Network error: ' + e.message, 'error');
    }
}

function updateItemInList(item) {
    const idx = allItems.findIndex(i => i.item_id === item.item_id);
    if (idx >= 0) allItems[idx] = {...allItems[idx], ...item};
    renderAllItems();
    if (selectedMachine) renderMachineQueue();
}

// ── Timer ──
function startTimer(startedAt) {
    stopTimer();
    const start = new Date(startedAt).getTime();
    const timerEl = document.getElementById('timerValue');
    document.getElementById('activeTimer').style.display = 'flex';

    timerInterval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - start) / 1000);
        const h = Math.floor(elapsed / 3600);
        const m = Math.floor((elapsed % 3600) / 60);
        const s = elapsed % 60;
        timerEl.textContent = String(h).padStart(2,'0') + ':' +
                              String(m).padStart(2,'0') + ':' +
                              String(s).padStart(2,'0');
    }, 1000);
}

function stopTimer() {
    if (timerInterval) { clearInterval(timerInterval); timerInterval = null; }
}

// ── Tab Switching ──
function switchTab(tab) {
    document.querySelectorAll('.ws-tab').forEach(t => t.classList.remove('active'));

    document.getElementById('machineView').style.display = 'none';
    document.getElementById('allView').style.display = 'none';
    document.getElementById('scanView').style.display = 'none';
    document.getElementById('stepView').className = 'step-view';
    document.getElementById('actionBar').style.display = 'none';

    // Stop camera when leaving QR tab
    if (tab !== 'scan' && qrScanning) { stopCameraScanner(); }

    if (tab === 'machine') {
        document.getElementById('tabMachine').classList.add('active');
        document.getElementById('machineView').style.display = 'block';
    } else if (tab === 'all') {
        document.getElementById('tabAll').classList.add('active');
        document.getElementById('allView').style.display = 'block';
    } else if (tab === 'scan') {
        document.getElementById('tabScan').classList.add('active');
        document.getElementById('scanView').style.display = 'block';
        setTimeout(() => document.getElementById('scanInput').focus(), 100);
    }
}

// ── QR Scan (Camera + Text Input) ──
let qrScanner = null;
let qrCameras = [];
let qrCurrentCamIdx = 0;
let qrScanning = false;
let qrLastScanned = '';
let qrCooldown = null;

document.addEventListener('DOMContentLoaded', () => {
    const scanInput = document.getElementById('scanInput');
    if (scanInput) {
        scanInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                processWorkStationScan(scanInput.value.trim());
                scanInput.value = '';
            }
        });
    }
});

async function startCameraScanner() {
    const statusEl = document.getElementById('camStatus');
    const readerBox = document.getElementById('qrReaderBox');
    const btnStart = document.getElementById('btnStartCam');
    const btnStop = document.getElementById('btnStopCam');
    const btnFlip = document.getElementById('btnFlipCam');

    try {
        btnStart.disabled = true;
        btnStart.innerHTML = '&#8987; Opening camera...';
        statusEl.textContent = 'Requesting camera access...';

        if (!qrScanner) {
            qrScanner = new Html5Qrcode('qr-reader');
        }

        qrCameras = await Html5Qrcode.getCameras();
        if (!qrCameras || qrCameras.length === 0) {
            throw new Error('No cameras found on this device.');
        }

        // Prefer back/rear camera
        qrCurrentCamIdx = qrCameras.findIndex(c => /back|rear|environment/i.test(c.label));
        if (qrCurrentCamIdx < 0) qrCurrentCamIdx = 0;

        readerBox.style.display = 'block';

        await qrScanner.start(
            qrCameras[qrCurrentCamIdx].id,
            {
                fps: 10,
                qrbox: function(vw, vh) {
                    var s = Math.min(vw, vh) * 0.75;
                    return { width: Math.floor(s), height: Math.floor(s) };
                },
                aspectRatio: 1.0
            },
            onQrScanSuccess,
            function() {} // ignore scan misses
        );

        qrScanning = true;
        btnStart.style.display = 'none';
        btnStop.style.display = 'inline-block';
        btnFlip.style.display = qrCameras.length > 1 ? 'inline-block' : 'none';
        statusEl.textContent = 'Camera active — point at a QR sticker';
        statusEl.style.color = '#22C55E';

    } catch(e) {
        btnStart.disabled = false;
        btnStart.innerHTML = '&#128247; Open Camera';
        statusEl.textContent = 'Camera error: ' + (e.message || e);
        statusEl.style.color = '#DC2626';
        readerBox.style.display = 'none';
        console.error('QR camera error:', e);
    }
}

async function stopCameraScanner() {
    try {
        if (qrScanner && qrScanning) {
            await qrScanner.stop();
        }
    } catch(e) { console.warn('Stop error:', e); }
    qrScanning = false;
    document.getElementById('qrReaderBox').style.display = 'none';
    document.getElementById('btnStartCam').style.display = 'inline-block';
    document.getElementById('btnStartCam').disabled = false;
    document.getElementById('btnStartCam').innerHTML = '&#128247; Open Camera';
    document.getElementById('btnStopCam').style.display = 'none';
    document.getElementById('btnFlipCam').style.display = 'none';
    document.getElementById('camStatus').textContent = '';
}

async function flipCamera() {
    if (qrCameras.length <= 1) return;
    qrCurrentCamIdx = (qrCurrentCamIdx + 1) % qrCameras.length;
    try {
        if (qrScanner && qrScanning) await qrScanner.stop();
        await qrScanner.start(
            qrCameras[qrCurrentCamIdx].id,
            { fps: 10, qrbox: function(vw,vh){ var s=Math.min(vw,vh)*0.75; return {width:Math.floor(s),height:Math.floor(s)}; }, aspectRatio:1.0 },
            onQrScanSuccess, function(){}
        );
        document.getElementById('camStatus').textContent = 'Camera: ' + (qrCameras[qrCurrentCamIdx].label || 'Camera ' + (qrCurrentCamIdx+1));
    } catch(e) {
        console.error('Flip error:', e);
        document.getElementById('camStatus').textContent = 'Flip failed: ' + e.message;
    }
}

function onQrScanSuccess(decodedText) {
    // Cooldown to prevent rapid duplicate scans
    if (decodedText === qrLastScanned && qrCooldown) return;
    qrLastScanned = decodedText;
    clearTimeout(qrCooldown);
    qrCooldown = setTimeout(() => { qrLastScanned = ''; qrCooldown = null; }, 3000);

    // Vibrate for feedback if supported
    if (navigator.vibrate) navigator.vibrate(200);

    processWorkStationScan(decodedText);
}

async function processWorkStationScan(rawInput) {
    const resultDiv = document.getElementById('scanResult');
    if (!rawInput) return;

    // Extract item_id from QR URL or use raw input
    let itemId = rawInput;
    const scanMatch = rawInput.match(/[?&]scan=([^&]+)/);
    if (scanMatch) itemId = decodeURIComponent(scanMatch[1]);

    const item = allItems.find(i => i.item_id === itemId);
    if (item) {
        resultDiv.innerHTML = '<div style="color:var(--tf-green,#22C55E);font-weight:600;font-size:1.1rem;">' +
            '&#9989; Found: ' + escHtml(item.ship_mark) + ' — ' + escHtml(item.description) + '</div>';
        // Stop camera before navigating to item
        if (qrScanning) await stopCameraScanner();
        setTimeout(() => openItem(itemId), 500);
    } else {
        resultDiv.innerHTML = '<div style="color:#DC2626;font-weight:600;">' +
            '&#10060; Item not found: ' + escHtml(itemId) + '</div>';
    }
}

// ── Helpers ──
function showToast(msg, type) {
    const toast = document.getElementById('wsToast');
    toast.textContent = msg;
    toast.className = 'ws-toast show ' + (type || '');
    setTimeout(() => { toast.className = 'ws-toast'; }, 3500);
}

function escHtml(s) {
    const d = document.createElement('div');
    d.textContent = s || '';
    return d.innerHTML;
}

function formatTime(iso) {
    if (!iso) return '';
    try {
        const d = new Date(iso);
        return d.toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});
    } catch(e) { return iso; }
}
</script>
</body>
</html>
"""
