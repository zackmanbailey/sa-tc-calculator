"""
TitanForge — My Station / My Work Template (Phase 2)
=====================================================
Mobile-first operator/welder queue view.
Shows assigned items, scan start/finish, and today's completed work.

Serves both:
  - Roll Forming Operators (My Station) → machine-centric view
  - Welders (My Work) → welding bay view

Reference: RULES.md §3 (Operator/Welder role definitions)
"""

MY_STATION_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>TitanForge — My Station</title>
<style>
:root {
    --tf-navy: #1a1f36;
    --tf-blue: #2563eb;
    --tf-orange: #f97316;
    --tf-green: #22c55e;
    --tf-red: #ef4444;
    --tf-yellow: #eab308;
    --tf-gray-100: #f3f4f6;
    --tf-gray-200: #e5e7eb;
    --tf-gray-300: #d1d5db;
    --tf-gray-400: #9ca3af;
    --tf-gray-600: #4b5563;
    --tf-gray-800: #1f2937;
    --radius: 10px;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--tf-gray-100); color: var(--tf-gray-800);
    -webkit-tap-highlight-color: transparent;
}

/* ── Header ─────────────────────── */
.ms-header {
    background: var(--tf-navy); color: #fff; padding: 14px 16px;
    display: flex; align-items: center; justify-content: space-between;
    position: sticky; top: 0; z-index: 100;
}
.ms-header h1 { font-size: 1.1rem; font-weight: 600; }
.ms-header .sub { font-size: 0.75rem; opacity: 0.6; }

/* ── Stats bar ──────────────────── */
.ms-stats {
    display: flex; gap: 0; background: #fff;
    border-bottom: 1px solid var(--tf-gray-200);
}
.ms-stat {
    flex: 1; text-align: center; padding: 10px 6px;
    border-right: 1px solid var(--tf-gray-200);
}
.ms-stat:last-child { border-right: none; }
.ms-stat .num { font-size: 1.5rem; font-weight: 700; }
.ms-stat .label { font-size: 0.65rem; text-transform: uppercase;
                  color: var(--tf-gray-400); letter-spacing: 0.5px; }
.ms-stat.active .num { color: var(--tf-orange); }
.ms-stat.done .num { color: var(--tf-green); }
.ms-stat.queue .num { color: var(--tf-blue); }

/* ── Active Item (hero card) ────── */
.ms-active-card {
    margin: 12px; background: #fff; border-radius: var(--radius);
    border: 2px solid var(--tf-orange); overflow: hidden;
}
.ms-active-card .tag {
    background: var(--tf-orange); color: #fff; padding: 6px 14px;
    font-size: 0.75rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 1px;
}
.ms-active-body { padding: 14px; }
.ms-active-body .mark { font-size: 1.6rem; font-weight: 700; }
.ms-active-body .desc { font-size: 0.85rem; color: var(--tf-gray-600); margin: 4px 0 8px; }
.ms-active-body .meta {
    display: flex; gap: 16px; font-size: 0.78rem; color: var(--tf-gray-400);
}
.ms-active-body .timer {
    font-size: 2rem; font-weight: 700; font-variant-numeric: tabular-nums;
    color: var(--tf-orange); margin: 10px 0;
}

/* ── Scan Buttons ───────────────── */
.ms-scan-row {
    display: flex; gap: 10px; padding: 0 12px 12px;
}
.ms-scan-btn {
    flex: 1; padding: 14px; border: none; border-radius: var(--radius);
    font-size: 1rem; font-weight: 700; cursor: pointer;
    display: flex; align-items: center; justify-content: center; gap: 8px;
    transition: transform 0.1s;
}
.ms-scan-btn:active { transform: scale(0.97); }
.ms-scan-btn.start { background: var(--tf-green); color: #fff; }
.ms-scan-btn.finish { background: var(--tf-blue); color: #fff; }
.ms-scan-btn.disabled { background: var(--tf-gray-200); color: var(--tf-gray-400);
                        pointer-events: none; }

/* ── Queue List ─────────────────── */
.ms-section-title {
    padding: 10px 16px 6px; font-size: 0.75rem; font-weight: 700;
    text-transform: uppercase; color: var(--tf-gray-400); letter-spacing: 0.5px;
}

.ms-item {
    margin: 0 12px 8px; background: #fff; border-radius: var(--radius);
    padding: 12px 14px; display: flex; align-items: center; gap: 12px;
    border: 1px solid var(--tf-gray-200); transition: all 0.15s;
}
.ms-item:active { background: var(--tf-gray-100); }
.ms-item .priority-dot {
    width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
}
.ms-item .priority-dot.urgent { background: var(--tf-red); }
.ms-item .priority-dot.normal { background: var(--tf-blue); }
.ms-item .priority-dot.low { background: var(--tf-gray-300); }
.ms-item .info { flex: 1; }
.ms-item .mark { font-weight: 700; font-size: 0.95rem; }
.ms-item .type { font-size: 0.75rem; color: var(--tf-gray-400); }
.ms-item .machine-tag {
    font-size: 0.7rem; background: var(--tf-gray-100);
    padding: 2px 8px; border-radius: 4px; color: var(--tf-gray-600);
}

.ms-item.rejected {
    border-color: var(--tf-red); border-left: 3px solid var(--tf-red);
}
.ms-item.rejected .qc-note {
    font-size: 0.75rem; color: var(--tf-red); margin-top: 4px;
}

/* ── Completed items ────────────── */
.ms-done-item {
    margin: 0 12px 6px; background: #fff; border-radius: 8px;
    padding: 10px 14px; display: flex; align-items: center;
    justify-content: space-between; border: 1px solid var(--tf-gray-200);
    opacity: 0.7;
}
.ms-done-item .mark { font-weight: 600; }
.ms-done-item .time { font-size: 0.78rem; color: var(--tf-green); font-weight: 600; }

.ms-empty { text-align: center; padding: 30px; color: var(--tf-gray-400); font-size: 0.9rem; }

/* ── Notes modal ────────────────── */
.ms-modal-overlay {
    display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.5);
    z-index: 500; align-items: flex-end; justify-content: center;
}
.ms-modal-overlay.open { display: flex; }
.ms-modal {
    background: #fff; width: 100%; max-width: 500px; border-radius: 16px 16px 0 0;
    padding: 20px; max-height: 60vh;
}
.ms-modal h3 { margin-bottom: 10px; }
.ms-modal textarea {
    width: 100%; height: 80px; border: 1px solid var(--tf-gray-300);
    border-radius: 8px; padding: 10px; font-size: 0.9rem; resize: none;
}
.ms-modal .actions { display: flex; gap: 10px; margin-top: 12px; }
.ms-modal .actions button {
    flex: 1; padding: 12px; border: none; border-radius: 8px;
    font-weight: 600; cursor: pointer;
}
.ms-modal .btn-save { background: var(--tf-blue); color: #fff; }
.ms-modal .btn-cancel { background: var(--tf-gray-200); color: var(--tf-gray-600); }
</style>
</head>
<body>

<div class="ms-header">
    <div>
        <h1>&#128190; My Station</h1>
        <div class="sub">{{DISPLAY_NAME}}</div>
    </div>
    <div style="text-align:right;">
        <div id="clockDisplay" style="font-size:1.1rem; font-weight:600;"></div>
        <div class="sub" id="dateDisplay"></div>
    </div>
</div>

<div class="ms-stats">
    <div class="ms-stat active"><div class="num" id="statActive">0</div><div class="label">Active</div></div>
    <div class="ms-stat queue"><div class="num" id="statQueue">0</div><div class="label">Queued</div></div>
    <div class="ms-stat done"><div class="num" id="statDone">0</div><div class="label">Done</div></div>
</div>

<!-- Active Item Hero -->
<div id="activeSection"></div>

<!-- Scan Buttons -->
<div class="ms-scan-row" id="scanButtons">
    <button class="ms-scan-btn start" id="btnStart" onclick="scanStart()">
        &#9654; Start Next
    </button>
    <button class="ms-scan-btn finish disabled" id="btnFinish" onclick="scanFinish()">
        &#9632; Finish
    </button>
</div>

<!-- Up Next Queue -->
<div class="ms-section-title" id="queueTitle">UP NEXT</div>
<div id="queueList"></div>

<!-- Completed Today -->
<div class="ms-section-title">COMPLETED TODAY</div>
<div id="doneList"></div>

<!-- Notes Modal -->
<div class="ms-modal-overlay" id="notesModal">
    <div class="ms-modal">
        <h3>&#128221; Add Notes</h3>
        <textarea id="notesInput" placeholder="Observations, issues, coil changeover notes..."></textarea>
        <div class="actions">
            <button class="btn-cancel" onclick="closeNotes()">Cancel</button>
            <button class="btn-save" onclick="saveNotes()">Save Note</button>
        </div>
    </div>
</div>

<script>
const USERNAME = "{{USERNAME}}";
const USER_ROLES = {{USER_ROLES}};
let queueData = {active: [], upcoming: [], completed_today: []};
let activeItem = null;
let timerInterval = null;

// ── Init ──────────────────────────
async function init() {
    updateClock();
    setInterval(updateClock, 1000);
    await loadQueue();
    // Auto-refresh every 30s
    setInterval(loadQueue, 30000);
}

async function loadQueue() {
    try {
        const res = await fetch(`/api/operator/queue?username=${encodeURIComponent(USERNAME)}`);
        const data = await res.json();
        if (!data.ok) return;
        queueData = data;
        renderAll();
    } catch(e) {
        console.error('Queue load failed', e);
    }
}

// ── Render ────────────────────────
function renderAll() {
    const { active, upcoming, completed_today } = queueData;

    document.getElementById('statActive').textContent = active.length;
    document.getElementById('statQueue').textContent = upcoming.length;
    document.getElementById('statDone').textContent = completed_today.length;

    // Active item hero card
    const activeEl = document.getElementById('activeSection');
    if (active.length > 0) {
        activeItem = active[0];
        activeEl.innerHTML = `
            <div class="ms-active-card">
                <div class="tag">&#9888; IN PROGRESS</div>
                <div class="ms-active-body">
                    <div class="mark">${activeItem.ship_mark}</div>
                    <div class="desc">${activeItem.description}</div>
                    <div class="timer" id="activeTimer">00:00</div>
                    <div class="meta">
                        <span>&#128190; ${activeItem.machine}</span>
                        <span>&#128203; ${activeItem.job_code}</span>
                        <span>WO: ${activeItem.work_order_id}</span>
                    </div>
                </div>
            </div>`;
        startTimer(activeItem.started_at);
        document.getElementById('btnStart').classList.add('disabled');
        document.getElementById('btnFinish').classList.remove('disabled');
    } else {
        activeItem = null;
        activeEl.innerHTML = '';
        if (timerInterval) clearInterval(timerInterval);
        document.getElementById('btnStart').classList.remove('disabled');
        document.getElementById('btnFinish').classList.add('disabled');

        if (upcoming.length === 0) {
            document.getElementById('btnStart').classList.add('disabled');
        }
    }

    // Queue
    const queueEl = document.getElementById('queueList');
    document.getElementById('queueTitle').textContent = `UP NEXT (${upcoming.length})`;
    if (!upcoming.length) {
        queueEl.innerHTML = '<div class="ms-empty">No items queued — check with your foreman</div>';
    } else {
        queueEl.innerHTML = upcoming.map(i => {
            const pClass = i.priority <= 10 ? 'urgent' : i.priority >= 80 ? 'low' : 'normal';
            const rejected = i.status === 'qc_rejected';
            return `<div class="ms-item ${rejected ? 'rejected' : ''}">
                <div class="priority-dot ${pClass}"></div>
                <div class="info">
                    <div class="mark">${i.ship_mark}</div>
                    <div class="type">${i.component_type} — ${i.description.substring(0,40)}</div>
                    ${rejected ? `<div class="qc-note">&#9888; QC Rejected: ${i.qc_notes || 'See inspector'}</div>` : ''}
                </div>
                <div class="machine-tag">${i.machine}</div>
            </div>`;
        }).join('');
    }

    // Completed
    const doneEl = document.getElementById('doneList');
    if (!completed_today.length) {
        doneEl.innerHTML = '<div class="ms-empty">Nothing completed yet today</div>';
    } else {
        doneEl.innerHTML = completed_today.map(i => `
            <div class="ms-done-item">
                <div>
                    <span class="mark">${i.ship_mark}</span>
                    <span style="color:var(--tf-gray-400); font-size:0.78rem;"> ${i.component_type}</span>
                </div>
                <div class="time">${i.duration_minutes ? i.duration_minutes.toFixed(1) + ' min' : '—'}</div>
            </div>
        `).join('');
    }
}

// ── Timer ─────────────────────────
function startTimer(startedAt) {
    if (timerInterval) clearInterval(timerInterval);
    const start = new Date(startedAt).getTime();
    function tick() {
        const elapsed = Math.floor((Date.now() - start) / 1000);
        const h = Math.floor(elapsed / 3600);
        const m = Math.floor((elapsed % 3600) / 60);
        const s = elapsed % 60;
        const el = document.getElementById('activeTimer');
        if (el) {
            el.textContent = h > 0
                ? `${h}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`
                : `${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
        }
    }
    tick();
    timerInterval = setInterval(tick, 1000);
}

// ── Scan Actions ──────────────────
async function scanStart() {
    const next = queueData.upcoming[0];
    if (!next) { alert('No items in queue'); return; }

    const res = await fetch('/api/work-orders/qr-scan', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            job_code: next.job_code,
            item_id: next.item_id,
            action: 'start',
            scanned_by: USERNAME
        })
    });
    const result = await res.json();
    if (result.ok) {
        await loadQueue();
    } else {
        alert(result.error || 'Start failed');
    }
}

async function scanFinish() {
    if (!activeItem) return;

    // Show notes prompt (optional)
    document.getElementById('notesModal').classList.add('open');
    document.getElementById('notesInput').value = '';
    document.getElementById('notesInput').focus();

    // Actual finish happens in saveNotes or closeNotes
    window._pendingFinish = true;
}

async function doFinish(notes) {
    if (!activeItem) return;

    // Save notes first if any
    if (notes) {
        await fetch('/api/work-orders/item-notes', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                job_code: activeItem.job_code,
                item_id: activeItem.item_id,
                notes: notes
            })
        });
    }

    const res = await fetch('/api/work-orders/qr-scan', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            job_code: activeItem.job_code,
            item_id: activeItem.item_id,
            action: 'finish',
            scanned_by: USERNAME
        })
    });
    const result = await res.json();
    if (result.ok) {
        if (timerInterval) clearInterval(timerInterval);
        await loadQueue();
    } else {
        alert(result.error || 'Finish failed');
    }
}

function saveNotes() {
    const notes = document.getElementById('notesInput').value.trim();
    document.getElementById('notesModal').classList.remove('open');
    if (window._pendingFinish) {
        window._pendingFinish = false;
        doFinish(notes);
    }
}

function closeNotes() {
    document.getElementById('notesModal').classList.remove('open');
    if (window._pendingFinish) {
        window._pendingFinish = false;
        doFinish('');
    }
}

// ── Clock ─────────────────────────
function updateClock() {
    const now = new Date();
    document.getElementById('clockDisplay').textContent = now.toLocaleTimeString('en-US', {hour:'2-digit', minute:'2-digit'});
    document.getElementById('dateDisplay').textContent = now.toLocaleDateString('en-US', {weekday:'short', month:'short', day:'numeric'});
}

document.addEventListener('DOMContentLoaded', init);
</script>
</body>
</html>
"""
