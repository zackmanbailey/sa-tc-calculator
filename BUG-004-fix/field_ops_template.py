"""
BUG-004 FIX — Field Operations Page Template
==============================================

ADD this file as: combined_calc/templates/field_ops.py

Full-page template for Field Operations hub with three tabs:
1. Installation Tracking (CORE — fully functional)
2. Crew Dispatch (placeholder)
3. Inspections & Punch List (placeholder)
"""


def get_field_ops_html():
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Field Operations — TitanForge</title>
<style>
:root {
  --tf-blue: #1E3A5F;
  --tf-blue-l: #2C5282;
  --tf-red: #C0392B;
  --tf-green: #22C55E;
  --tf-orange: #F59E0B;
  --tf-bg: #F1F5F9;
  --tf-card: #FFFFFF;
  --tf-border: #E2E8F0;
  --tf-text: #1E293B;
  --tf-muted: #64748B;
}
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Segoe UI',system-ui,sans-serif; background:var(--tf-bg); color:var(--tf-text); }

/* Header */
.fo-header {
  background:linear-gradient(135deg, var(--tf-blue), var(--tf-blue-l));
  color:white; padding:20px 32px; display:flex; align-items:center; justify-content:space-between;
}
.fo-header h1 { font-size:1.5rem; font-weight:700; }
.fo-header .subtitle { font-size:0.85rem; opacity:0.8; margin-top:2px; }

/* Tabs */
.fo-tabs {
  display:flex; gap:0; background:white; border-bottom:2px solid var(--tf-border);
  padding:0 32px;
}
.fo-tab {
  padding:12px 24px; font-size:0.9rem; font-weight:600; cursor:pointer;
  border-bottom:3px solid transparent; color:var(--tf-muted); transition:all 0.2s;
}
.fo-tab:hover { color:var(--tf-blue); }
.fo-tab.active { color:var(--tf-blue); border-bottom-color:var(--tf-blue); }
.fo-tab .badge {
  display:inline-block; background:var(--tf-blue); color:white; font-size:0.7rem;
  padding:1px 6px; border-radius:8px; margin-left:6px; vertical-align:middle;
}
.fo-tab .coming-soon {
  display:inline-block; background:#F59E0B; color:white; font-size:0.6rem;
  padding:1px 5px; border-radius:4px; margin-left:4px; vertical-align:middle;
  text-transform:uppercase; letter-spacing:0.5px;
}

/* Content */
.fo-content { padding:24px 32px; max-width:1400px; }
.tab-panel { display:none; }
.tab-panel.active { display:block; }

/* Summary Cards */
.summary-row {
  display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr));
  gap:16px; margin-bottom:24px;
}
.summary-card {
  background:white; border-radius:10px; padding:16px 20px;
  border-left:4px solid var(--tf-blue); box-shadow:0 1px 3px rgba(0,0,0,0.08);
}
.summary-card .label { font-size:0.75rem; color:var(--tf-muted); text-transform:uppercase; letter-spacing:0.5px; }
.summary-card .value { font-size:1.8rem; font-weight:700; color:var(--tf-blue); margin-top:4px; }
.summary-card.green { border-left-color:var(--tf-green); }
.summary-card.green .value { color:var(--tf-green); }
.summary-card.orange { border-left-color:var(--tf-orange); }
.summary-card.orange .value { color:var(--tf-orange); }
.summary-card.red { border-left-color:var(--tf-red); }
.summary-card.red .value { color:var(--tf-red); }

/* Installation Cards */
.install-grid {
  display:grid; grid-template-columns:repeat(auto-fill, minmax(380px, 1fr));
  gap:20px;
}
.install-card {
  background:white; border-radius:10px; overflow:hidden;
  box-shadow:0 1px 4px rgba(0,0,0,0.08); border:1px solid var(--tf-border);
}
.install-card-header {
  padding:14px 18px; display:flex; justify-content:space-between; align-items:center;
  border-bottom:1px solid var(--tf-border);
}
.install-card-header h3 { font-size:0.95rem; font-weight:700; }
.status-badge {
  padding:3px 10px; border-radius:12px; font-size:0.7rem; font-weight:600;
  color:white; text-transform:uppercase; letter-spacing:0.5px;
}
.install-card-body { padding:14px 18px; }
.install-info { display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:12px; }
.install-info .fi-label { font-size:0.7rem; color:var(--tf-muted); text-transform:uppercase; }
.install-info .fi-value { font-size:0.85rem; font-weight:600; }

/* Progress bar */
.progress-bar-container {
  background:#E2E8F0; border-radius:6px; height:10px; overflow:hidden; margin:8px 0;
}
.progress-bar-fill {
  height:100%; border-radius:6px; transition:width 0.4s ease;
  background:linear-gradient(90deg, var(--tf-blue), var(--tf-green));
}

/* Action buttons */
.install-actions {
  display:flex; gap:8px; margin-top:12px; flex-wrap:wrap;
}
.btn-fo {
  padding:6px 14px; border-radius:6px; font-size:0.8rem; font-weight:600;
  border:none; cursor:pointer; transition:all 0.15s;
}
.btn-fo.primary { background:var(--tf-blue); color:white; }
.btn-fo.primary:hover { background:var(--tf-blue-l); }
.btn-fo.success { background:var(--tf-green); color:white; }
.btn-fo.warning { background:var(--tf-orange); color:white; }
.btn-fo.danger { background:var(--tf-red); color:white; }
.btn-fo.outline { background:white; color:var(--tf-blue); border:1.5px solid var(--tf-blue); }
.btn-fo.outline:hover { background:var(--tf-blue); color:white; }

/* Status select */
.status-select {
  padding:5px 10px; border-radius:6px; border:1.5px solid var(--tf-border);
  font-size:0.8rem; font-weight:500; cursor:pointer;
}

/* Daily Log */
.log-entry {
  padding:10px 14px; border-left:3px solid var(--tf-blue); margin-bottom:8px;
  background:#F8FAFC; border-radius:0 6px 6px 0;
}
.log-entry .log-date { font-size:0.75rem; color:var(--tf-muted); font-weight:600; }
.log-entry .log-text { font-size:0.85rem; margin-top:4px; }

/* Modal */
.modal-overlay {
  display:none; position:fixed; top:0; left:0; right:0; bottom:0;
  background:rgba(0,0,0,0.5); z-index:1000; align-items:center; justify-content:center;
}
.modal-overlay.active { display:flex; }
.modal {
  background:white; border-radius:12px; padding:24px; width:500px; max-width:90vw;
  max-height:85vh; overflow-y:auto; box-shadow:0 20px 60px rgba(0,0,0,0.2);
}
.modal h2 { font-size:1.1rem; margin-bottom:16px; color:var(--tf-blue); }
.modal label { display:block; font-size:0.8rem; font-weight:600; color:var(--tf-muted); margin:10px 0 4px; }
.modal input, .modal select, .modal textarea {
  width:100%; padding:8px 12px; border:1.5px solid var(--tf-border); border-radius:6px;
  font-size:0.9rem; font-family:inherit;
}
.modal textarea { min-height:80px; resize:vertical; }
.modal-actions { display:flex; gap:10px; justify-content:flex-end; margin-top:16px; }

/* Placeholder */
.placeholder-tab {
  text-align:center; padding:60px 40px;
}
.placeholder-tab .icon { font-size:3rem; margin-bottom:16px; }
.placeholder-tab h2 { color:var(--tf-blue); margin-bottom:8px; }
.placeholder-tab p { color:var(--tf-muted); max-width:500px; margin:0 auto; }

/* Toast */
.toast-container { position:fixed; top:20px; right:20px; z-index:9999; }
.toast {
  padding:12px 20px; border-radius:8px; color:white; font-size:0.85rem; font-weight:500;
  margin-bottom:8px; animation:slideIn 0.3s ease; min-width:250px;
  box-shadow:0 4px 12px rgba(0,0,0,0.15);
}
.toast.success { background:var(--tf-green); }
.toast.error { background:var(--tf-red); }
.toast.info { background:var(--tf-blue); }
@keyframes slideIn { from { transform:translateX(100%); opacity:0; } to { transform:translateX(0); opacity:1; } }

/* Job selector */
.job-selector {
  display:flex; gap:12px; align-items:center; margin-bottom:20px;
  background:white; padding:12px 18px; border-radius:8px; border:1px solid var(--tf-border);
}
.job-selector label { font-size:0.85rem; font-weight:600; white-space:nowrap; }
.job-selector select { flex:1; max-width:300px; padding:8px 12px; border:1.5px solid var(--tf-border); border-radius:6px; }
</style>
</head>
<body>

<!-- Header -->
<div class="fo-header">
  <div>
    <h1>&#127959; Field Operations</h1>
    <div class="subtitle">Installation tracking, crew dispatch & field inspections</div>
  </div>
  <div style="display:flex;gap:10px">
    <button class="btn-fo outline" onclick="window.location.href='/'">&#8592; Dashboard</button>
  </div>
</div>

<!-- Tabs -->
<div class="fo-tabs">
  <div class="fo-tab active" onclick="switchTab('installations')">
    Installations <span class="badge" id="install-count">0</span>
  </div>
  <div class="fo-tab" onclick="switchTab('dispatch')">
    Crew Dispatch <span class="coming-soon">Soon</span>
  </div>
  <div class="fo-tab" onclick="switchTab('inspections')">
    Inspections & Punch List <span class="coming-soon">Soon</span>
  </div>
</div>

<!-- Content -->
<div class="fo-content">

  <!-- Job Selector -->
  <div class="job-selector">
    <label>Project:</label>
    <select id="job-select" onchange="loadFieldOps()">
      <option value="">Select a project...</option>
    </select>
    <button class="btn-fo primary" onclick="loadFieldOps()">Load</button>
    <button class="btn-fo outline" onclick="autoCreateFromBOM()">Auto-Create from BOM</button>
    <button class="btn-fo outline" onclick="showCreateInstallModal()">+ Add Installation</button>
  </div>

  <!-- TAB: Installations (CORE) -->
  <div id="tab-installations" class="tab-panel active">
    <div class="summary-row" id="install-summary">
      <div class="summary-card"><div class="label">Total Buildings</div><div class="value" id="sum-total">0</div></div>
      <div class="summary-card green"><div class="label">Complete</div><div class="value" id="sum-complete">0</div></div>
      <div class="summary-card"><div class="label">In Progress</div><div class="value" id="sum-progress">0</div></div>
      <div class="summary-card orange"><div class="label">Avg Progress</div><div class="value" id="sum-avg">0%</div></div>
      <div class="summary-card red"><div class="label">Delays</div><div class="value" id="sum-delays">0</div></div>
    </div>

    <div class="install-grid" id="install-grid">
      <div style="grid-column:1/-1;text-align:center;padding:40px;color:var(--tf-muted)">
        Select a project to view installations
      </div>
    </div>
  </div>

  <!-- TAB: Crew Dispatch (placeholder) -->
  <div id="tab-dispatch" class="tab-panel">
    <div class="placeholder-tab">
      <div class="icon">&#128666;</div>
      <h2>Crew Dispatch & Scheduling</h2>
      <p>Assign crews to jobs, manage travel schedules, track equipment checked out to field crews, and coordinate with shop production timeline.</p>
      <div style="margin-top:20px;padding:16px;background:#FFF8E1;border-radius:8px;display:inline-block">
        <strong>Coming in Phase 14</strong> — This module will integrate with Work Orders and the Shop Floor schedule.
      </div>
    </div>
  </div>

  <!-- TAB: Inspections (placeholder) -->
  <div id="tab-inspections" class="tab-panel">
    <div class="placeholder-tab">
      <div class="icon">&#128203;</div>
      <h2>Inspections & Punch List</h2>
      <p>Site inspection checklists, punch list items that need fixing, photo documentation, and customer sign-off on completed work.</p>
      <div style="margin-top:20px;padding:16px;background:#FFF8E1;border-radius:8px;display:inline-block">
        <strong>Coming in Phase 14</strong> — This module will include photo uploads, digital signatures, and PDF report generation.
      </div>
    </div>
  </div>

</div>

<!-- Create Installation Modal -->
<div class="modal-overlay" id="modal-create-install">
  <div class="modal">
    <h2>&#128506; New Installation</h2>
    <label>Building Name</label>
    <input type="text" id="new-inst-name" placeholder="e.g., Building A - 40x60 Tee"/>
    <label>Scheduled Start</label>
    <input type="date" id="new-inst-start"/>
    <label>Scheduled End</label>
    <input type="date" id="new-inst-end"/>
    <label>Notes</label>
    <textarea id="new-inst-notes" placeholder="Any special requirements, access notes, etc."></textarea>
    <div class="modal-actions">
      <button class="btn-fo outline" onclick="closeModal('modal-create-install')">Cancel</button>
      <button class="btn-fo primary" onclick="createInstallation()">Create</button>
    </div>
  </div>
</div>

<!-- Daily Log Modal -->
<div class="modal-overlay" id="modal-daily-log">
  <div class="modal">
    <h2>&#128221; Daily Log Entry</h2>
    <input type="hidden" id="log-install-id"/>
    <label>Date</label>
    <input type="date" id="log-date"/>
    <label>Crew Count</label>
    <input type="number" id="log-crew" value="4" min="1"/>
    <label>Hours Worked</label>
    <input type="number" id="log-hours" value="8" min="0" step="0.5"/>
    <label>Weather</label>
    <select id="log-weather">
      <option>Clear</option><option>Partly Cloudy</option><option>Overcast</option>
      <option>Rain</option><option>Wind</option><option>Extreme Heat</option>
    </select>
    <label>Work Performed</label>
    <textarea id="log-work" placeholder="Describe work completed today..."></textarea>
    <label>Issues (optional)</label>
    <textarea id="log-issues" placeholder="Any problems or concerns..."></textarea>
    <div class="modal-actions">
      <button class="btn-fo outline" onclick="closeModal('modal-daily-log')">Cancel</button>
      <button class="btn-fo primary" onclick="submitDailyLog()">Submit Log</button>
    </div>
  </div>
</div>

<!-- Delay Modal -->
<div class="modal-overlay" id="modal-delay">
  <div class="modal">
    <h2>&#9888;&#65039; Report Delay</h2>
    <input type="hidden" id="delay-install-id"/>
    <label>Reason</label>
    <select id="delay-reason">
      <option>Weather - Rain</option><option>Weather - Wind</option><option>Weather - Extreme Heat</option>
      <option>Material Delay</option><option>Equipment Issue</option><option>Crew Shortage</option>
      <option>Site Access Issue</option><option>Customer Request</option><option>Permit/Inspection Wait</option>
      <option>Safety Concern</option><option>Other</option>
    </select>
    <label>Description</label>
    <textarea id="delay-desc" placeholder="Details about the delay..."></textarea>
    <label>Estimated Days Impacted</label>
    <input type="number" id="delay-days" value="1" min="0"/>
    <div class="modal-actions">
      <button class="btn-fo outline" onclick="closeModal('modal-delay')">Cancel</button>
      <button class="btn-fo danger" onclick="submitDelay()">Report Delay</button>
    </div>
  </div>
</div>

<div class="toast-container" id="toast-container"></div>

<script>
// ─────────────────────────────────────────────
// STATE
// ─────────────────────────────────────────────
let currentJobCode = '';
let installations = [];

const STATUS_LABELS = {
  not_started:'Not Started', mobilizing:'Mobilizing', site_prep:'Site Prep',
  foundations:'Foundations', erection:'Steel Erection', roofing:'Roofing & Trim',
  punch_list:'Punch List', complete:'Complete', on_hold:'On Hold'
};
const STATUS_COLORS = {
  not_started:'#94A3B8', mobilizing:'#F59E0B', site_prep:'#8B5CF6',
  foundations:'#6366F1', erection:'#3B82F6', roofing:'#10B981',
  punch_list:'#F97316', complete:'#22C55E', on_hold:'#EF4444'
};
const STATUS_ORDER = ['not_started','mobilizing','site_prep','foundations','erection','roofing','punch_list','complete'];

// ─────────────────────────────────────────────
// API
// ─────────────────────────────────────────────
async function apiCall(url, method='GET', body=null) {
  const opts = { method, headers:{'Content-Type':'application/json'} };
  if (body) opts.body = JSON.stringify(body);
  const resp = await fetch(url, opts);
  return resp.json();
}

// ─────────────────────────────────────────────
// TABS
// ─────────────────────────────────────────────
function switchTab(tab) {
  document.querySelectorAll('.fo-tab').forEach((el,i) => {
    el.classList.toggle('active',
      (tab==='installations'&&i===0)||(tab==='dispatch'&&i===1)||(tab==='inspections'&&i===2));
  });
  document.querySelectorAll('.tab-panel').forEach(el => el.classList.remove('active'));
  document.getElementById('tab-'+tab).classList.add('active');
}

// ─────────────────────────────────────────────
// LOAD PROJECTS & FIELD OPS
// ─────────────────────────────────────────────
async function loadProjects() {
  try {
    const result = await apiCall('/api/projects');
    if (result.ok) {
      const select = document.getElementById('job-select');
      (result.projects || []).forEach(p => {
        const opt = document.createElement('option');
        opt.value = p.job_code;
        opt.textContent = p.job_code + ' — ' + (p.project_name || p.name || 'Unnamed');
        select.appendChild(opt);
      });
    }
  } catch(e) { console.warn('Could not load projects:', e); }
}

async function loadFieldOps() {
  currentJobCode = document.getElementById('job-select').value;
  if (!currentJobCode) { showToast('Select a project first','error'); return; }

  try {
    const result = await apiCall('/api/field-ops?job_code=' + encodeURIComponent(currentJobCode));
    if (result.ok) {
      installations = result.summary.installations || [];
      renderSummary(result.summary);
      renderInstallations();
    } else {
      // No field ops data yet — show empty state
      installations = [];
      renderSummary({total:0, by_status:{}, avg_progress:0, total_delays:0});
      renderInstallations();
    }
  } catch(e) {
    showToast('Error loading field ops: ' + e.message, 'error');
  }
}

// ─────────────────────────────────────────────
// RENDER
// ─────────────────────────────────────────────
function renderSummary(s) {
  document.getElementById('sum-total').textContent = s.total || 0;
  document.getElementById('sum-complete').textContent = (s.by_status||{}).complete || 0;
  const inProgress = Object.entries(s.by_status||{})
    .filter(([k,v])=>k!=='complete'&&k!=='not_started')
    .reduce((a,[k,v])=>a+v, 0);
  document.getElementById('sum-progress').textContent = inProgress;
  document.getElementById('sum-avg').textContent = (s.avg_progress||0) + '%';
  document.getElementById('sum-delays').textContent = s.total_delays || 0;
  document.getElementById('install-count').textContent = s.total || 0;
}

function renderInstallations() {
  const grid = document.getElementById('install-grid');
  if (!installations.length) {
    grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:40px;color:var(--tf-muted)">No installations found. Click "Auto-Create from BOM" or "+ Add Installation" to get started.</div>';
    return;
  }

  grid.innerHTML = installations.map((inst, i) => {
    const color = STATUS_COLORS[inst.status] || '#94A3B8';
    const label = STATUS_LABELS[inst.status] || inst.status;
    const progress = inst.progress_pct || 0;
    const delayCount = (inst.delays||[]).length;
    const logCount = (inst.daily_logs||[]).length;

    // Next status options
    const currentIdx = STATUS_ORDER.indexOf(inst.status);
    let statusOptions = '';
    if (inst.status !== 'complete') {
      statusOptions = STATUS_ORDER.filter((s,si) => si > currentIdx || s === 'on_hold')
        .map(s => '<option value="'+s+'"'+(s===inst.status?' selected':'')+'>'+STATUS_LABELS[s]+'</option>')
        .join('');
      // Add on_hold if not already there
      if (inst.status !== 'on_hold') {
        statusOptions += '<option value="on_hold">On Hold</option>';
      }
    }

    return '<div class="install-card">' +
      '<div class="install-card-header">' +
        '<h3>' + inst.building_name + '</h3>' +
        '<span class="status-badge" style="background:'+color+'">'+label+'</span>' +
      '</div>' +
      '<div class="install-card-body">' +
        '<div class="install-info">' +
          '<div><div class="fi-label">Scheduled Start</div><div class="fi-value">'+(inst.scheduled_start||'TBD')+'</div></div>' +
          '<div><div class="fi-label">Scheduled End</div><div class="fi-value">'+(inst.scheduled_end||'TBD')+'</div></div>' +
          '<div><div class="fi-label">Daily Logs</div><div class="fi-value">'+logCount+'</div></div>' +
          '<div><div class="fi-label">Delays</div><div class="fi-value" style="color:'+(delayCount?'var(--tf-red)':'inherit')+'">'+delayCount+'</div></div>' +
        '</div>' +
        (inst.notes ? '<div style="font-size:0.8rem;color:var(--tf-muted);margin-bottom:8px">'+inst.notes+'</div>' : '') +
        '<div style="display:flex;align-items:center;gap:8px">' +
          '<div style="flex:1"><div class="progress-bar-container"><div class="progress-bar-fill" style="width:'+progress+'%"></div></div></div>' +
          '<span style="font-size:0.8rem;font-weight:700;color:var(--tf-blue)">'+progress+'%</span>' +
        '</div>' +
        '<div class="install-actions">' +
          (inst.status !== 'complete' ?
            '<select class="status-select" onchange="changeInstallStatus(\''+inst.install_id+'\',this.value)">' +
              '<option value="">Advance Status...</option>' + statusOptions +
            '</select>' : '') +
          '<button class="btn-fo outline" onclick="showDailyLogModal(\''+inst.install_id+'\')">+ Log</button>' +
          '<button class="btn-fo warning" onclick="showDelayModal(\''+inst.install_id+'\')">Delay</button>' +
        '</div>' +
      '</div>' +
    '</div>';
  }).join('');
}

// ─────────────────────────────────────────────
// ACTIONS
// ─────────────────────────────────────────────
async function changeInstallStatus(installId, newStatus) {
  if (!newStatus || !currentJobCode) return;
  const notes = prompt('Notes for this status change (optional):') || '';
  const result = await apiCall('/api/field-ops/status', 'POST', {
    job_code: currentJobCode, install_id: installId, new_status: newStatus, notes: notes
  });
  if (result.ok) {
    showToast('Status updated to ' + STATUS_LABELS[newStatus], 'success');
    loadFieldOps();
  } else {
    showToast('Error: ' + (result.error||'Unknown'), 'error');
  }
}

async function createInstallation() {
  if (!currentJobCode) { showToast('Select a project first','error'); return; }
  const name = document.getElementById('new-inst-name').value.trim();
  if (!name) { showToast('Building name required','error'); return; }

  const result = await apiCall('/api/field-ops/install', 'POST', {
    job_code: currentJobCode,
    building_name: name,
    scheduled_start: document.getElementById('new-inst-start').value || null,
    scheduled_end: document.getElementById('new-inst-end').value || null,
    notes: document.getElementById('new-inst-notes').value.trim(),
  });
  if (result.ok) {
    showToast('Installation created', 'success');
    closeModal('modal-create-install');
    loadFieldOps();
  } else {
    showToast('Error: ' + (result.error||'Unknown'), 'error');
  }
}

async function autoCreateFromBOM() {
  if (!currentJobCode) { showToast('Select a project first','error'); return; }
  const result = await apiCall('/api/field-ops/auto-create', 'POST', { job_code: currentJobCode });
  if (result.ok) {
    showToast(result.message || 'Created installations from BOM', 'success');
    loadFieldOps();
  } else {
    showToast('Error: ' + (result.error||'No BOM data found'), 'error');
  }
}

async function submitDailyLog() {
  const installId = document.getElementById('log-install-id').value;
  if (!installId || !currentJobCode) return;

  const result = await apiCall('/api/field-ops/daily-log', 'POST', {
    job_code: currentJobCode,
    install_id: installId,
    log_date: document.getElementById('log-date').value,
    crew_count: parseInt(document.getElementById('log-crew').value) || 4,
    hours_worked: parseFloat(document.getElementById('log-hours').value) || 8,
    weather: document.getElementById('log-weather').value,
    work_performed: document.getElementById('log-work').value.trim(),
    issues: document.getElementById('log-issues').value.trim(),
  });
  if (result.ok) {
    showToast('Daily log submitted', 'success');
    closeModal('modal-daily-log');
    loadFieldOps();
  } else {
    showToast('Error: ' + (result.error||'Unknown'), 'error');
  }
}

async function submitDelay() {
  const installId = document.getElementById('delay-install-id').value;
  if (!installId || !currentJobCode) return;

  const result = await apiCall('/api/field-ops/delay', 'POST', {
    job_code: currentJobCode,
    install_id: installId,
    reason: document.getElementById('delay-reason').value,
    description: document.getElementById('delay-desc').value.trim(),
    estimated_days: parseInt(document.getElementById('delay-days').value) || 1,
  });
  if (result.ok) {
    showToast('Delay reported', 'success');
    closeModal('modal-delay');
    loadFieldOps();
  } else {
    showToast('Error: ' + (result.error||'Unknown'), 'error');
  }
}

// ─────────────────────────────────────────────
// MODALS & UI
// ─────────────────────────────────────────────
function showCreateInstallModal() {
  if (!currentJobCode) { showToast('Select a project first','error'); return; }
  document.getElementById('new-inst-name').value = '';
  document.getElementById('new-inst-start').value = '';
  document.getElementById('new-inst-end').value = '';
  document.getElementById('new-inst-notes').value = '';
  document.getElementById('modal-create-install').classList.add('active');
}

function showDailyLogModal(installId) {
  document.getElementById('log-install-id').value = installId;
  document.getElementById('log-date').value = new Date().toISOString().split('T')[0];
  document.getElementById('log-work').value = '';
  document.getElementById('log-issues').value = '';
  document.getElementById('modal-daily-log').classList.add('active');
}

function showDelayModal(installId) {
  document.getElementById('delay-install-id').value = installId;
  document.getElementById('delay-desc').value = '';
  document.getElementById('delay-days').value = '1';
  document.getElementById('modal-delay').classList.add('active');
}

function closeModal(id) {
  document.getElementById(id).classList.remove('active');
}

function showToast(msg, type) {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = 'toast ' + (type||'info');
  toast.textContent = msg;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}

// ─────────────────────────────────────────────
// INIT
// ─────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  loadProjects();
  // Check URL params
  const p = new URLSearchParams(window.location.search);
  if (p.has('project')) {
    setTimeout(() => {
      document.getElementById('job-select').value = p.get('project');
      loadFieldOps();
    }, 500);
  }
});
</script>
</body>
</html>"""
