"""
TitanForge — Mobile Work Order Scan Page
=========================================
Landing page when a QR sticker is scanned on ANY piece in the shop.
Works for: Fab workers, QC inspectors, loaders, and field crews.

URL: /wo/{job_code}/{item_id}

Shows:
  1. Piece identity & status at a glance
  2. Shop drawings (view PDF inline)
  3. Fab tracking (start/finish with accountability)
  4. QC inspection (pass/fail with notes)
  5. Loading/shipping status
  6. Activity log (who did what when)
  7. All work order items for this job (sibling pieces)
"""

WO_MOBILE_SCAN_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<title>TitanForge — Scan</title>
<style>
:root {
  --navy: #1a2332;
  --navy-light: #243044;
  --gold: #d4a843;
  --gold-dim: #b8922e;
  --green: #22c55e;
  --red: #ef4444;
  --amber: #f59e0b;
  --blue: #3b82f6;
  --gray-100: #f8f9fa;
  --gray-200: #e9ecef;
  --gray-300: #dee2e6;
  --gray-500: #6c757d;
  --gray-700: #495057;
  --gray-900: #212529;
  --radius: 10px;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--gray-100);
  color: var(--gray-900);
  min-height: 100vh;
  -webkit-tap-highlight-color: transparent;
}

/* ── Top Header ── */
.header {
  background: var(--navy);
  color: #fff;
  padding: 14px 16px;
  position: sticky; top: 0; z-index: 100;
}
.header-top {
  display: flex; align-items: center; justify-content: space-between;
}
.header .logo { font-weight: 700; font-size: 14px; color: var(--gold); }
.header .user-badge {
  background: var(--navy-light); color: var(--gray-300);
  padding: 4px 10px; border-radius: 12px; font-size: 12px;
}

/* ── Piece Identity Card ── */
.piece-card {
  background: #fff; margin: 12px; border-radius: var(--radius);
  box-shadow: 0 2px 8px rgba(0,0,0,0.08); overflow: hidden;
}
.piece-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px; border-bottom: 1px solid var(--gray-200);
}
.piece-mark {
  font-size: 32px; font-weight: 800; color: var(--navy);
  line-height: 1;
}
.piece-type {
  display: inline-block; padding: 4px 12px; border-radius: 6px;
  font-size: 12px; font-weight: 700; text-transform: uppercase;
  background: var(--navy); color: var(--gold);
}
.piece-status {
  display: flex; gap: 6px; align-items: center;
}
.status-badge {
  padding: 5px 12px; border-radius: 16px; font-size: 12px;
  font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;
}
.status-queued { background: var(--gray-200); color: var(--gray-700); }
.status-in_progress { background: #dbeafe; color: #1d4ed8; }
.status-complete { background: #dcfce7; color: #166534; }
.status-on_hold { background: #fef3c7; color: #92400e; }

.piece-details {
  padding: 12px 16px; display: grid;
  grid-template-columns: 1fr 1fr; gap: 8px;
}
.detail-row { display: flex; flex-direction: column; }
.detail-label { font-size: 10px; text-transform: uppercase; color: var(--gray-500); font-weight: 600; letter-spacing: 0.5px; }
.detail-value { font-size: 14px; font-weight: 600; color: var(--gray-900); }

.piece-desc {
  padding: 8px 16px 14px; font-size: 13px; color: var(--gray-700);
  border-top: 1px solid var(--gray-200);
}

/* ── Tab Navigation ── */
.tabs {
  display: flex; background: #fff; margin: 0 12px;
  border-radius: var(--radius); box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  overflow-x: auto; -webkit-overflow-scrolling: touch;
}
.tab {
  flex: 1; min-width: 0; padding: 12px 8px; text-align: center;
  font-size: 12px; font-weight: 600; color: var(--gray-500);
  border: none; background: none; cursor: pointer;
  border-bottom: 3px solid transparent; white-space: nowrap;
  transition: all 0.2s;
}
.tab.active { color: var(--gold); border-bottom-color: var(--gold); }
.tab-icon { display: block; font-size: 18px; margin-bottom: 2px; }

/* ── Tab Panels ── */
.panel { display: none; margin: 12px; }
.panel.active { display: block; }

/* ── Action Buttons ── */
.action-btn {
  display: flex; align-items: center; justify-content: center; gap: 8px;
  width: 100%; padding: 16px; border: none; border-radius: var(--radius);
  font-size: 16px; font-weight: 700; cursor: pointer;
  transition: all 0.2s; text-transform: uppercase; letter-spacing: 1px;
}
.action-btn:active { transform: scale(0.97); }
.btn-start { background: var(--green); color: #fff; }
.btn-finish { background: var(--blue); color: #fff; }
.btn-disabled { background: var(--gray-300); color: var(--gray-500); pointer-events: none; }
.btn-qc-pass { background: var(--green); color: #fff; }
.btn-qc-fail { background: var(--red); color: #fff; }
.btn-loading { background: var(--amber); color: #fff; }
.btn-secondary {
  background: var(--navy-light); color: #fff;
  padding: 12px; font-size: 14px;
}

/* ── Cards ── */
.card {
  background: #fff; border-radius: var(--radius);
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  margin-bottom: 12px; overflow: hidden;
}
.card-header {
  padding: 12px 16px; font-weight: 700; font-size: 14px;
  border-bottom: 1px solid var(--gray-200);
  display: flex; align-items: center; justify-content: space-between;
}

/* ── Activity Log ── */
.activity-item {
  display: flex; gap: 12px; padding: 10px 16px;
  border-bottom: 1px solid var(--gray-200);
  font-size: 13px;
}
.activity-item:last-child { border-bottom: none; }
.activity-icon {
  width: 32px; height: 32px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; flex-shrink: 0;
}
.activity-icon.start { background: #dbeafe; }
.activity-icon.finish { background: #dcfce7; }
.activity-icon.qc { background: #fef3c7; }
.activity-icon.load { background: #ede9fe; }
.activity-text { flex: 1; }
.activity-who { font-weight: 600; }
.activity-when { color: var(--gray-500); font-size: 11px; }

/* ── QC Section ── */
.qc-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 16px; }
.qc-notes-input {
  width: 100%; padding: 10px; border: 1px solid var(--gray-300);
  border-radius: 8px; font-size: 14px; resize: vertical; min-height: 60px;
  margin: 0 16px 16px; width: calc(100% - 32px);
}
.qc-badge {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: 600;
}
.qc-passed { background: #dcfce7; color: #166534; }
.qc-failed { background: #fecaca; color: #991b1b; }
.qc-pending { background: var(--gray-200); color: var(--gray-700); }

/* ── Loading Section ── */
.loading-pipeline {
  display: flex; align-items: center; padding: 16px;
  gap: 4px; overflow-x: auto;
}
.pipeline-step {
  flex: 1; min-width: 60px; text-align: center; padding: 8px 4px;
  border-radius: 8px; font-size: 11px; font-weight: 600;
  background: var(--gray-200); color: var(--gray-500);
  transition: all 0.3s;
}
.pipeline-step.current { background: var(--gold); color: var(--navy); }
.pipeline-step.done { background: var(--green); color: #fff; }
.pipeline-arrow { font-size: 16px; color: var(--gray-300); flex-shrink: 0; }

/* ── Drawings Section ── */
.drawing-card {
  display: flex; align-items: center; gap: 12px; padding: 14px 16px;
  border-bottom: 1px solid var(--gray-200); cursor: pointer;
}
.drawing-card:last-child { border-bottom: none; }
.drawing-icon { font-size: 28px; }
.drawing-info { flex: 1; }
.drawing-name { font-weight: 600; font-size: 14px; }
.drawing-size { font-size: 12px; color: var(--gray-500); }
.drawing-action { color: var(--blue); font-weight: 600; font-size: 13px; }

/* ── Sibling Items ── */
.sibling-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 16px; border-bottom: 1px solid var(--gray-200);
  text-decoration: none; color: inherit;
}
.sibling-item:last-child { border-bottom: none; }
.sibling-mark { font-weight: 700; font-size: 16px; color: var(--navy); min-width: 50px; }
.sibling-desc { flex: 1; font-size: 13px; color: var(--gray-700); }
.sibling-item.current { background: #fffbeb; border-left: 3px solid var(--gold); }

/* ── Timer ── */
.timer-display {
  text-align: center; padding: 20px;
  font-size: 48px; font-weight: 800; font-family: 'SF Mono', monospace;
  color: var(--blue); letter-spacing: 2px;
}
.timer-label { font-size: 12px; color: var(--gray-500); text-transform: uppercase; font-weight: 600; }

/* ── Project Info Bar ── */
.project-bar {
  background: var(--navy-light); color: var(--gray-300);
  padding: 8px 16px; font-size: 12px;
  display: flex; justify-content: space-between;
}

/* ── Toast ── */
.toast {
  position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
  background: var(--navy); color: #fff; padding: 12px 24px;
  border-radius: 8px; font-size: 14px; font-weight: 600;
  z-index: 1000; opacity: 0; transition: opacity 0.3s;
  max-width: 90vw; text-align: center;
}
.toast.show { opacity: 1; }
.toast.success { background: #166534; }
.toast.error { background: #991b1b; }

/* ── Truck Number Input ── */
.truck-input-row {
  display: flex; gap: 8px; padding: 0 16px 16px; align-items: center;
}
.truck-input {
  flex: 1; padding: 10px; border: 1px solid var(--gray-300);
  border-radius: 8px; font-size: 14px;
}
</style>
</head>
<body>

<!-- Header -->
<div class="header">
  <div class="header-top">
    <span class="logo">TITANFORGE</span>
    <span class="user-badge" id="userBadge">{{USER_NAME}}</span>
  </div>
  <div class="project-bar" id="projectBar" style="margin: 8px -16px -14px; padding: 6px 16px;">
    <span id="projectInfo">Loading...</span>
    <span id="woInfo"></span>
  </div>
</div>

<!-- Piece Identity Card -->
<div class="piece-card" id="pieceCard">
  <div class="piece-header">
    <div>
      <div class="piece-mark" id="pieceMark">...</div>
      <div style="margin-top:4px"><span class="piece-type" id="pieceType">...</span></div>
    </div>
    <div class="piece-status">
      <span class="status-badge" id="pieceStatus">...</span>
    </div>
  </div>
  <div class="piece-details">
    <div class="detail-row"><span class="detail-label">Job Code</span><span class="detail-value" id="dJobCode">{{JOB_CODE}}</span></div>
    <div class="detail-row"><span class="detail-label">Quantity</span><span class="detail-value" id="dQty">-</span></div>
    <div class="detail-row"><span class="detail-label">Machine</span><span class="detail-value" id="dMachine">-</span></div>
    <div class="detail-row"><span class="detail-label">Assigned To</span><span class="detail-value" id="dAssigned">-</span></div>
  </div>
  <div class="piece-desc" id="pieceDesc">Loading piece information...</div>
</div>

<!-- Tabs -->
<div class="tabs">
  <button class="tab active" onclick="switchTab('fab')" id="tabFab"><span class="tab-icon">&#9881;</span>Fab</button>
  <button class="tab" onclick="switchTab('drawings')" id="tabDrawings"><span class="tab-icon">&#128196;</span>Drawings</button>
  <button class="tab" onclick="switchTab('qc')" id="tabQc"><span class="tab-icon">&#9989;</span>QC</button>
  <button class="tab" onclick="switchTab('loading')" id="tabLoading"><span class="tab-icon">&#128666;</span>Loading</button>
  <button class="tab" onclick="switchTab('log')" id="tabLog"><span class="tab-icon">&#128203;</span>Log</button>
  <button class="tab" onclick="switchTab('all')" id="tabAll"><span class="tab-icon">&#128230;</span>All</button>
</div>

<!-- TAB: Fabrication -->
<div class="panel active" id="panelFab">
  <!-- Timer (shown when in progress) -->
  <div class="card" id="timerCard" style="display:none;">
    <div class="timer-label" style="text-align:center;padding-top:10px;">Time Elapsed</div>
    <div class="timer-display" id="timerDisplay">00:00:00</div>
  </div>

  <!-- Duration (shown when complete) -->
  <div class="card" id="durationCard" style="display:none;">
    <div style="text-align:center;padding:16px;">
      <div class="timer-label">Fabrication Time</div>
      <div style="font-size:36px;font-weight:800;color:var(--green);" id="durationDisplay">-</div>
    </div>
  </div>

  <!-- Action Buttons -->
  <div id="fabActions" style="display:flex;flex-direction:column;gap:10px;">
    <button class="action-btn btn-start" id="btnStart" onclick="fabAction('start')">
      &#9654; Start Fabrication
    </button>
    <button class="action-btn btn-finish" id="btnFinish" onclick="fabAction('finish')" style="display:none;">
      &#9632; Finish &amp; Complete
    </button>
  </div>

  <!-- Notes -->
  <div class="card" style="margin-top:12px;">
    <div class="card-header">Notes</div>
    <textarea class="qc-notes-input" id="itemNotes" placeholder="Add notes about this piece..." style="margin:12px 16px;width:calc(100% - 32px);"></textarea>
    <div style="padding:0 16px 12px;">
      <button class="action-btn btn-secondary" onclick="saveNotes()" style="padding:10px;font-size:13px;">Save Notes</button>
    </div>
  </div>
</div>

<!-- TAB: Drawings -->
<div class="panel" id="panelDrawings">
  <div class="card">
    <div class="card-header">Shop Drawings</div>
    <div id="drawingsList">
      <div style="padding:20px;text-align:center;color:var(--gray-500);">Loading drawings...</div>
    </div>
  </div>
  <div style="margin-top:8px;">
    <a id="allDrawingsLink" href="/shop-drawings/{{JOB_CODE}}" class="action-btn btn-secondary" style="text-decoration:none;font-size:13px;padding:12px;">
      View All Project Drawings
    </a>
  </div>
</div>

<!-- TAB: QC Inspection -->
<div class="panel" id="panelQc">
  <div class="card">
    <div class="card-header">
      Quality Control
      <span class="qc-badge" id="qcBadge">...</span>
    </div>
    <!-- QC Info (shown after inspection) -->
    <div id="qcInfo" style="display:none;padding:16px;">
      <div class="detail-row" style="margin-bottom:8px;"><span class="detail-label">Inspector</span><span class="detail-value" id="qcInspector">-</span></div>
      <div class="detail-row" style="margin-bottom:8px;"><span class="detail-label">Inspected At</span><span class="detail-value" id="qcInspectedAt">-</span></div>
      <div class="detail-row"><span class="detail-label">Notes</span><span class="detail-value" id="qcNotesDisplay">-</span></div>
    </div>
    <!-- QC Actions (shown when pending) -->
    <div id="qcActions">
      <textarea class="qc-notes-input" id="qcNotesInput" placeholder="Inspector notes (welds, dimensions, finish...)"></textarea>
      <div class="qc-actions">
        <button class="action-btn btn-qc-pass" onclick="qcAction('passed')">&#10004; Pass</button>
        <button class="action-btn btn-qc-fail" onclick="qcAction('failed')">&#10008; Fail</button>
      </div>
    </div>
    <div id="qcNotReady" style="display:none;padding:20px;text-align:center;color:var(--gray-500);font-size:14px;">
      Piece must be fabrication-complete before QC inspection.
    </div>
  </div>
</div>

<!-- TAB: Loading -->
<div class="panel" id="panelLoading">
  <div class="card">
    <div class="card-header">Loading &amp; Shipping</div>
    <div class="loading-pipeline" id="loadingPipeline">
      <!-- Rendered by JS -->
    </div>
    <div class="truck-input-row" id="truckRow" style="display:none;">
      <input type="text" class="truck-input" id="truckNumber" placeholder="Truck/Trailer #">
    </div>
    <div style="padding:0 16px 16px;">
      <button class="action-btn btn-loading" id="btnNextLoading" onclick="advanceLoading()">
        Next Step
      </button>
    </div>
    <div id="loadingNotReady" style="display:none;padding:20px;text-align:center;color:var(--gray-500);font-size:14px;">
      Piece must pass QC before it can be staged for loading.
    </div>
  </div>
</div>

<!-- TAB: Activity Log -->
<div class="panel" id="panelLog">
  <div class="card">
    <div class="card-header">Activity Log</div>
    <div id="activityLog">
      <div style="padding:20px;text-align:center;color:var(--gray-500);">No activity yet</div>
    </div>
  </div>
</div>

<!-- TAB: All Items -->
<div class="panel" id="panelAll">
  <div class="card">
    <div class="card-header">All Items in Work Order <span id="allItemsCount" style="color:var(--gray-500);font-weight:400;font-size:12px;"></span></div>
    <div id="allItemsList">
      <div style="padding:20px;text-align:center;color:var(--gray-500);">Loading...</div>
    </div>
  </div>
</div>

<!-- Toast -->
<div class="toast" id="toast"></div>

<script>
const JOB_CODE = '{{JOB_CODE}}';
const ITEM_ID = '{{ITEM_ID}}';
const USER_NAME = '{{USER_NAME}}';
let ITEM = null;
let WO = null;
let timerInterval = null;

const LOADING_ORDER = ['not_ready','staged','loaded','shipped','delivered'];
const LOADING_LABELS = {
  not_ready:'Not Ready', staged:'Staged', loaded:'Loaded',
  shipped:'Shipped', delivered:'Delivered'
};

// ── Init ──
document.addEventListener('DOMContentLoaded', loadItem);

async function loadItem() {
  try {
    // Load item detail
    const r = await fetch(`/api/work-orders/item-detail?job_code=${JOB_CODE}&item_id=${ITEM_ID}`);
    const d = await r.json();
    if (!d.ok) { showToast(d.error || 'Item not found', 'error'); return; }
    ITEM = d.item;
    WO = d.work_order || {};

    // Also load full WO for sibling items
    if (WO.work_order_id) {
      const r2 = await fetch(`/api/work-orders/detail?job_code=${JOB_CODE}&wo_id=${WO.work_order_id}`);
      const d2 = await r2.json();
      if (d2.ok) WO = d2.work_order;
    }

    renderPiece();
    renderFabTab();
    renderQCTab();
    renderLoadingTab();
    renderActivityLog();
    renderAllItems();
    loadDrawings();
    renderProjectBar();
  } catch(e) {
    showToast('Error loading item: ' + e.message, 'error');
  }
}

function renderProjectBar() {
  const pn = WO.project_name || JOB_CODE;
  const cn = WO.customer_name ? ` — ${WO.customer_name}` : '';
  document.getElementById('projectInfo').textContent = pn + cn;
  const bs = WO.building_specs || '';
  document.getElementById('woInfo').textContent = bs;
}

function renderPiece() {
  document.getElementById('pieceMark').textContent = ITEM.ship_mark;
  document.getElementById('pieceType').textContent = ITEM.component_type.replace(/_/g,' ');
  document.getElementById('pieceDesc').textContent = ITEM.description;
  document.getElementById('dQty').textContent = ITEM.quantity;
  document.getElementById('dMachine').textContent = ITEM.machine || '-';
  document.getElementById('dAssigned').textContent = ITEM.assigned_to || 'Unassigned';

  const badge = document.getElementById('pieceStatus');
  badge.textContent = ITEM.status.replace(/_/g,' ');
  badge.className = 'status-badge status-' + ITEM.status;
}

function renderFabTab() {
  const btnStart = document.getElementById('btnStart');
  const btnFinish = document.getElementById('btnFinish');
  const timerCard = document.getElementById('timerCard');
  const durationCard = document.getElementById('durationCard');

  if (ITEM.status === 'queued' || ITEM.status === 'approved' || ITEM.status === 'stickers_printed') {
    btnStart.style.display = 'flex';
    btnFinish.style.display = 'none';
  } else if (ITEM.status === 'in_progress') {
    btnStart.style.display = 'none';
    btnFinish.style.display = 'flex';
    timerCard.style.display = 'block';
    startTimer();
  } else if (ITEM.status === 'complete') {
    btnStart.style.display = 'none';
    btnFinish.style.display = 'none';
    durationCard.style.display = 'block';
    const mins = ITEM.duration_minutes || 0;
    const h = Math.floor(mins / 60);
    const m = Math.floor(mins % 60);
    document.getElementById('durationDisplay').textContent =
      h > 0 ? `${h}h ${m}m` : `${m} min`;
  }

  document.getElementById('itemNotes').value = ITEM.notes || '';
}

function startTimer() {
  if (timerInterval) clearInterval(timerInterval);
  const startTime = new Date(ITEM.started_at).getTime();
  function update() {
    const elapsed = Date.now() - startTime;
    const h = Math.floor(elapsed / 3600000);
    const m = Math.floor((elapsed % 3600000) / 60000);
    const s = Math.floor((elapsed % 60000) / 1000);
    document.getElementById('timerDisplay').textContent =
      `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
  }
  update();
  timerInterval = setInterval(update, 1000);
}

async function fabAction(action) {
  const btn = action === 'start' ? document.getElementById('btnStart') : document.getElementById('btnFinish');
  btn.disabled = true;
  btn.textContent = action === 'start' ? 'Starting...' : 'Finishing...';
  try {
    const r = await fetch('/api/work-orders/qr-scan', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        job_code: JOB_CODE, item_id: ITEM_ID,
        action: action, scanned_by: USER_NAME
      })
    });
    const d = await r.json();
    if (d.ok) {
      showToast(d.message, 'success');
      ITEM = d.item;
      renderPiece();
      renderFabTab();
      renderQCTab();
      renderActivityLog();
    } else {
      showToast(d.error, 'error');
    }
  } catch(e) {
    showToast('Error: ' + e.message, 'error');
  }
  btn.disabled = false;
}

async function saveNotes() {
  const notes = document.getElementById('itemNotes').value;
  try {
    const r = await fetch('/api/work-orders/item-notes', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ job_code: JOB_CODE, item_id: ITEM_ID, notes: notes })
    });
    const d = await r.json();
    if (d.ok) showToast('Notes saved', 'success');
    else showToast(d.error, 'error');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
}

// ── QC Tab ──
function renderQCTab() {
  const qcActions = document.getElementById('qcActions');
  const qcInfo = document.getElementById('qcInfo');
  const qcNotReady = document.getElementById('qcNotReady');
  const qcBadge = document.getElementById('qcBadge');

  if (ITEM.status !== 'complete') {
    qcActions.style.display = 'none';
    qcInfo.style.display = 'none';
    qcNotReady.style.display = 'block';
    qcBadge.className = 'qc-badge qc-pending';
    qcBadge.textContent = 'Waiting';
    return;
  }

  qcNotReady.style.display = 'none';
  const qs = ITEM.qc_status || 'pending';

  if (qs === 'pending') {
    qcActions.style.display = 'block';
    qcInfo.style.display = 'none';
    qcBadge.className = 'qc-badge qc-pending';
    qcBadge.textContent = 'Pending';
  } else {
    qcActions.style.display = 'none';
    qcInfo.style.display = 'block';
    qcBadge.className = 'qc-badge qc-' + qs;
    qcBadge.textContent = qs === 'passed' ? 'PASSED' : 'FAILED';
    document.getElementById('qcInspector').textContent = ITEM.qc_inspector || '-';
    document.getElementById('qcInspectedAt').textContent = formatTime(ITEM.qc_inspected_at);
    document.getElementById('qcNotesDisplay').textContent = ITEM.qc_notes || '-';
  }
}

async function qcAction(status) {
  const notes = document.getElementById('qcNotesInput').value;
  try {
    const r = await fetch('/api/work-orders/qc', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        job_code: JOB_CODE, item_id: ITEM_ID,
        qc_status: status, inspector: USER_NAME, qc_notes: notes
      })
    });
    const d = await r.json();
    if (d.ok) {
      showToast(d.message, 'success');
      ITEM = d.item;
      renderQCTab();
      renderLoadingTab();
      renderActivityLog();
    } else {
      showToast(d.error, 'error');
    }
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
}

// ── Loading Tab ──
function renderLoadingTab() {
  const pipeline = document.getElementById('loadingPipeline');
  const btnNext = document.getElementById('btnNextLoading');
  const notReady = document.getElementById('loadingNotReady');
  const truckRow = document.getElementById('truckRow');
  const ls = ITEM.loading_status || 'not_ready';
  const currentIdx = LOADING_ORDER.indexOf(ls);

  // Must be QC passed (or QC pending + complete) to be loadable
  const qcOk = ITEM.qc_status === 'passed' || ITEM.qc_status === 'n/a';
  if (ITEM.status !== 'complete' || (!qcOk && ls === 'not_ready')) {
    pipeline.style.display = 'none';
    btnNext.style.display = 'none';
    truckRow.style.display = 'none';
    notReady.style.display = 'block';
    notReady.textContent = ITEM.status !== 'complete'
      ? 'Piece must be fabrication-complete before loading.'
      : 'Piece must pass QC before it can be staged for loading.';
    return;
  }

  notReady.style.display = 'none';
  pipeline.style.display = 'flex';

  // Render pipeline steps
  let html = '';
  LOADING_ORDER.forEach((step, i) => {
    if (i > 0) html += '<span class="pipeline-arrow">&#9654;</span>';
    let cls = 'pipeline-step';
    if (i < currentIdx) cls += ' done';
    else if (i === currentIdx) cls += ' current';
    html += `<div class="${cls}">${LOADING_LABELS[step]}</div>`;
  });
  pipeline.innerHTML = html;

  // Next step button
  const nextIdx = currentIdx + 1;
  if (nextIdx < LOADING_ORDER.length) {
    const nextStatus = LOADING_ORDER[nextIdx];
    btnNext.style.display = 'flex';
    btnNext.textContent = 'Move to: ' + LOADING_LABELS[nextStatus];
    truckRow.style.display = nextStatus === 'loaded' ? 'flex' : 'none';
  } else {
    btnNext.style.display = 'none';
    truckRow.style.display = 'none';
  }

  // Show truck info if already loaded
  if (ITEM.truck_number && ls !== 'not_ready') {
    const info = document.createElement('div');
    info.style.cssText = 'padding:0 16px 12px;font-size:13px;color:var(--gray-700);';
    info.innerHTML = `<strong>Truck:</strong> ${ITEM.truck_number} &nbsp; <strong>Loaded by:</strong> ${ITEM.loaded_by || '-'} &nbsp; <strong>At:</strong> ${formatTime(ITEM.loaded_at)}`;
    // Check if already rendered
    if (!document.getElementById('truckInfoDisplay')) {
      info.id = 'truckInfoDisplay';
      pipeline.parentNode.insertBefore(info, btnNext.parentNode);
    }
  }
}

async function advanceLoading() {
  const ls = ITEM.loading_status || 'not_ready';
  const currentIdx = LOADING_ORDER.indexOf(ls);
  const nextStatus = LOADING_ORDER[currentIdx + 1];
  if (!nextStatus) return;

  const truck = document.getElementById('truckNumber').value.trim();

  try {
    const r = await fetch('/api/work-orders/loading', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        job_code: JOB_CODE, item_id: ITEM_ID,
        loading_status: nextStatus, updated_by: USER_NAME,
        truck_number: truck
      })
    });
    const d = await r.json();
    if (d.ok) {
      showToast(d.message, 'success');
      ITEM = d.item;
      renderLoadingTab();
      renderActivityLog();
    } else {
      showToast(d.error, 'error');
    }
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
}

// ── Drawings Tab ──
async function loadDrawings() {
  const container = document.getElementById('drawingsList');
  try {
    const ctype = (ITEM.component_type || '').toLowerCase();
    let html = '';

    // Map component type to the correct interactive builder page
    const drawingMap = {
      column:  { url: `/shop-drawings/${JOB_CODE}/column`, label: 'Column Drawing', icon: '&#128736;' },
      rafter:  { url: `/shop-drawings/${JOB_CODE}/rafter`, label: 'Rafter Drawing', icon: '&#128736;' },
    };

    // Show the drawing that matches THIS item's component type first
    if (drawingMap[ctype]) {
      const d = drawingMap[ctype];
      html += drawingCard(d.label, 'Primary — tap to open interactive drawing', d.url, d.icon);
    }

    // Show other interactive drawings for reference
    for (const [type, d] of Object.entries(drawingMap)) {
      if (type !== ctype) {
        html += drawingCard(d.label, 'Reference drawing', d.url, d.icon);
      }
    }

    // Always link to the full project drawings page
    html += drawingCard('All Project Drawings', 'View complete drawing set', `/shop-drawings/${JOB_CODE}`, '&#128209;');

    container.innerHTML = html || '<div style="padding:20px;text-align:center;color:var(--gray-500);">No drawings available</div>';
  } catch(e) {
    container.innerHTML = '<div style="padding:20px;text-align:center;color:var(--red);">Error loading drawings</div>';
  }
}

function drawingCard(title, subtitle, url, icon) {
  return `<a href="${url}" target="_blank" class="drawing-card" style="text-decoration:none;color:inherit;">
    <span class="drawing-icon">${icon || '&#128196;'}</span>
    <div class="drawing-info">
      <div class="drawing-name">${title}</div>
      <div class="drawing-size">${subtitle}</div>
    </div>
    <span class="drawing-action">Open &#8594;</span>
  </a>`;
}

// ── Activity Log ──
function renderActivityLog() {
  const container = document.getElementById('activityLog');
  const events = [];

  if (ITEM.started_at) {
    events.push({ icon: 'start', emoji: '&#9654;', who: ITEM.started_by || '?', what: 'Started fabrication', when: ITEM.started_at });
  }
  if (ITEM.finished_at) {
    const dur = ITEM.duration_minutes ? ` (${ITEM.duration_minutes.toFixed(1)} min)` : '';
    events.push({ icon: 'finish', emoji: '&#9632;', who: ITEM.finished_by || '?', what: 'Finished fabrication' + dur, when: ITEM.finished_at });
  }
  if (ITEM.qc_inspected_at) {
    const qs = ITEM.qc_status === 'passed' ? 'QC PASSED' : 'QC FAILED';
    events.push({ icon: 'qc', emoji: '&#9989;', who: ITEM.qc_inspector || '?', what: qs + (ITEM.qc_notes ? ': ' + ITEM.qc_notes : ''), when: ITEM.qc_inspected_at });
  }
  if (ITEM.loaded_at) {
    const truck = ITEM.truck_number ? ` (Truck: ${ITEM.truck_number})` : '';
    events.push({ icon: 'load', emoji: '&#128666;', who: ITEM.loaded_by || '?', what: 'Loaded' + truck, when: ITEM.loaded_at });
  }

  if (events.length === 0) {
    container.innerHTML = '<div style="padding:20px;text-align:center;color:var(--gray-500);">No activity recorded yet</div>';
    return;
  }

  // Sort newest first
  events.sort((a,b) => new Date(b.when) - new Date(a.when));

  container.innerHTML = events.map(e => `
    <div class="activity-item">
      <div class="activity-icon ${e.icon}">${e.emoji}</div>
      <div class="activity-text">
        <div><span class="activity-who">${e.who}</span> &mdash; ${e.what}</div>
        <div class="activity-when">${formatTime(e.when)}</div>
      </div>
    </div>
  `).join('');
}

// ── All Items ──
function renderAllItems() {
  const container = document.getElementById('allItemsList');
  const items = WO.items || [];
  document.getElementById('allItemsCount').textContent = `(${items.length} items)`;

  if (items.length === 0) {
    container.innerHTML = '<div style="padding:20px;text-align:center;color:var(--gray-500);">No items</div>';
    return;
  }

  container.innerHTML = items.map(it => {
    const isCurrent = it.item_id === ITEM_ID;
    const statusCls = 'status-badge status-' + it.status;
    return `<a href="/wo/${JOB_CODE}/${it.item_id}" class="sibling-item${isCurrent ? ' current' : ''}">
      <span class="sibling-mark">${it.ship_mark}</span>
      <span class="sibling-desc">${it.description}</span>
      <span class="${statusCls}" style="font-size:10px;padding:2px 8px;">${it.status.replace(/_/g,' ')}</span>
    </a>`;
  }).join('');
}

// ── Tab Switching ──
function switchTab(tab) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.getElementById('tab' + tab.charAt(0).toUpperCase() + tab.slice(1)).classList.add('active');
  document.getElementById('panel' + tab.charAt(0).toUpperCase() + tab.slice(1)).classList.add('active');
}

// ── Helpers ──
function formatTime(iso) {
  if (!iso) return '-';
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', {month:'short', day:'numeric'}) + ' ' +
         d.toLocaleTimeString('en-US', {hour:'numeric', minute:'2-digit'});
}

function showToast(msg, type) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = 'toast show ' + (type || '');
  setTimeout(() => t.className = 'toast', 3000);
}
</script>
</body>
</html>"""
