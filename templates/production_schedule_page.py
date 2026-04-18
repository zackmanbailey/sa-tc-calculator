"""
TitanForge — Production Schedule Dashboard Template
=====================================================
Calendar view of scheduled work, capacity bars per machine,
bottleneck alerts, and job timeline overview.
"""

PRODUCTION_SCHEDULE_PAGE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Production Schedule — TitanForge</title>
<style>
  :root {
    --bg: #0f172a; --surface: #1e293b; --border: #334155;
    --text: #f1f5f9; --muted: #94a3b8; --accent: #3b82f6;
    --green: #22c55e; --yellow: #eab308; --orange: #f97316; --red: #ef4444;
    --purple: #a855f7; --cyan: #06b6d4;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: var(--bg); color: var(--text); line-height: 1.5; }

  .topbar { background: var(--surface); border-bottom: 1px solid var(--border);
            padding: 12px 24px; display: flex; align-items: center; justify-content: space-between; }
  .topbar h1 { font-size: 20px; font-weight: 600; }
  .topbar a { color: var(--accent); text-decoration: none; font-size: 14px; margin-left: 16px; }
  .nav-links { display: flex; gap: 8px; }

  .container { max-width: 1400px; margin: 0 auto; padding: 20px 24px; }

  /* Stat cards */
  .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
           gap: 12px; margin-bottom: 20px; }
  .stat-card { background: var(--surface); border: 1px solid var(--border);
               border-radius: 8px; padding: 16px; cursor: pointer;
               transition: border-color 0.2s, box-shadow 0.2s; }
  .stat-card:hover { border-color: var(--accent); box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
  .stat-card .label { font-size: 12px; color: var(--muted); text-transform: uppercase;
                      letter-spacing: 0.05em; }
  .stat-card .value { font-size: 28px; font-weight: 700; margin-top: 4px; }
  .stat-card .sub { font-size: 12px; color: var(--muted); margin-top: 2px; }
  .val-green { color: var(--green); } .val-orange { color: var(--orange); }
  .val-red { color: var(--red); } .val-blue { color: var(--accent); }
  .val-yellow { color: var(--yellow); }

  /* Controls */
  .controls { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; align-items: center; }
  .controls select, .controls input, .controls button {
    background: var(--surface); border: 1px solid var(--border); color: var(--text);
    padding: 8px 12px; border-radius: 6px; font-size: 14px; }
  .controls button { cursor: pointer; }
  .controls button:hover { border-color: var(--accent); }
  .btn-primary { background: var(--accent) !important; border-color: var(--accent) !important;
                 color: #fff !important; font-weight: 600; }
  .btn-primary:hover { background: #2563eb !important; }

  /* Two-column layout */
  .layout { display: grid; grid-template-columns: 1fr 340px; gap: 20px; }
  @media (max-width: 1024px) { .layout { grid-template-columns: 1fr; } }

  /* Capacity grid */
  .section-title { font-size: 16px; font-weight: 600; margin-bottom: 12px; }
  .capacity-grid { display: grid; gap: 10px; margin-bottom: 20px; }
  .cap-row { background: var(--surface); border: 1px solid var(--border);
             border-radius: 8px; padding: 12px 16px; cursor: pointer;
             transition: border-color 0.2s; }
  .cap-row:hover { border-color: var(--accent); }
  .cap-header { display: flex; justify-content: space-between; align-items: center;
                margin-bottom: 8px; }
  .cap-label { font-weight: 600; font-size: 14px; }
  .cap-pct { font-size: 13px; font-weight: 600; }
  .cap-bar { height: 8px; background: #1e293b; border-radius: 4px; overflow: hidden; }
  .cap-fill { height: 100%; border-radius: 4px; transition: width 0.3s; }
  .cap-details { display: flex; gap: 16px; margin-top: 6px; font-size: 12px; color: var(--muted); }

  /* Day schedule */
  .day-schedule { margin-bottom: 20px; }
  .day-header { font-size: 15px; font-weight: 600; margin-bottom: 8px;
                padding-bottom: 6px; border-bottom: 1px solid var(--border); }
  .entry-list { display: grid; gap: 8px; }
  .entry-card { background: var(--surface); border: 1px solid var(--border);
                border-radius: 8px; padding: 12px; border-left: 3px solid var(--accent);
                cursor: pointer; transition: border-color 0.2s; }
  .entry-card:hover { border-color: var(--accent); }
  .entry-card.priority-1 { border-left-color: var(--red); }
  .entry-card.priority-2 { border-left-color: var(--orange); }
  .entry-card.priority-4 { border-left-color: var(--muted); }
  .entry-top { display: flex; justify-content: space-between; align-items: center; }
  .entry-mark { font-weight: 700; font-size: 14px; }
  .entry-time { font-size: 12px; color: var(--muted); }
  .entry-meta { font-size: 12px; color: var(--muted); margin-top: 4px; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 4px;
           font-size: 11px; font-weight: 600; }
  .badge-red { background: rgba(239,68,68,0.15); color: var(--red); }
  .badge-orange { background: rgba(249,115,22,0.15); color: var(--orange); }
  .badge-green { background: rgba(34,197,94,0.15); color: var(--green); }
  .badge-blue { background: rgba(59,130,246,0.15); color: var(--accent); }
  .badge-gray { background: rgba(148,163,184,0.15); color: var(--muted); }

  /* Sidebar panels */
  .side-panel { background: var(--surface); border: 1px solid var(--border);
                border-radius: 8px; padding: 16px; margin-bottom: 16px; }
  .side-panel h3 { font-size: 14px; font-weight: 600; margin-bottom: 12px; }
  .bottleneck-item { padding: 8px 0; border-bottom: 1px solid var(--border);
                     font-size: 13px; cursor: pointer; border-radius: 4px;
                     padding: 8px 6px; transition: background 0.15s; }
  .bottleneck-item:hover { background: rgba(255,255,255,0.04); }
  .bottleneck-item:last-child { border-bottom: none; }
  .bn-label { font-weight: 600; }
  .bn-detail { color: var(--muted); font-size: 12px; margin-top: 2px; }

  .job-item { display: flex; justify-content: space-between; padding: 6px 4px;
              border-bottom: 1px solid var(--border); font-size: 13px;
              cursor: pointer; border-radius: 4px; transition: background 0.15s; }
  .job-item:hover { background: rgba(255,255,255,0.04); }
  .job-item:last-child { border-bottom: none; }

  .overdue-item { padding: 8px 6px; border-bottom: 1px solid var(--border); font-size: 13px;
                  cursor: pointer; border-radius: 4px; transition: background 0.15s; }
  .overdue-item:hover { background: rgba(255,255,255,0.04); }
  .overdue-item:last-child { border-bottom: none; }
  .overdue-mark { font-weight: 600; color: var(--red); }

  .empty-msg { color: var(--muted); font-size: 13px; text-align: center; padding: 20px; }
</style>
</head>
<body>
<div class="topbar">
  <h1>Production Schedule</h1>
  <div class="nav-links">
    <a href="/dashboard">Dashboard</a>
    <a href="/shop-floor">Shop Floor</a>
    <a href="/reports/production">Production Metrics</a>
    <a href="/reports/executive">Executive Summary</a>
    <a href="/activity">Activity Feed</a>
  </div>
</div>

<div class="container">
  <!-- Stats -->
  <div class="stats">
    <div class="stat-card" onclick="window.location.href='/shop-floor'"><div class="label">Scheduled Today</div>
      <div class="value val-blue" id="statTodayCount">—</div>
      <div class="sub" id="statTodayMinutes"></div></div>
    <div class="stat-card" onclick="window.location.href='/reports/production'"><div class="label">This Week</div>
      <div class="value" id="statWeekCount">—</div>
      <div class="sub" id="statWeekMinutes"></div></div>
    <div class="stat-card" onclick="window.location.href='/shop-floor'"><div class="label">Pending</div>
      <div class="value val-orange" id="statPending">—</div></div>
    <div class="stat-card" onclick="document.getElementById('overdueList').scrollIntoView({behavior:'smooth'})"><div class="label">Overdue</div>
      <div class="value val-red" id="statOverdue">—</div></div>
    <div class="stat-card" onclick="window.location.href='/reports/production'"><div class="label">Completed</div>
      <div class="value val-green" id="statCompleted">—</div></div>
    <div class="stat-card" onclick="window.location.href='/reports/production'"><div class="label">All Entries</div>
      <div class="value" id="statTotal">—</div></div>
  </div>

  <!-- Controls -->
  <div class="controls">
    <input type="date" id="dateSelect" />
    <select id="machineFilter">
      <option value="">All Machines</option>
    </select>
    <button onclick="loadDay()">View Day</button>
    <button onclick="prevDay()">← Prev</button>
    <button onclick="nextDay()">Next →</button>
    <button class="btn-primary" onclick="loadForecast()">Capacity Forecast</button>
  </div>

  <div class="layout">
    <!-- Main content -->
    <div class="main">
      <!-- Capacity bars -->
      <div class="section-title">Machine Capacity — <span id="capacityDate"></span></div>
      <div class="capacity-grid" id="capacityGrid"></div>

      <!-- Day entries -->
      <div class="section-title">Scheduled Work — <span id="dayLabel"></span></div>
      <div class="day-schedule" id="daySchedule"></div>
    </div>

    <!-- Sidebar -->
    <div class="sidebar">
      <div class="side-panel">
        <h3>Bottleneck Alerts</h3>
        <div id="bottleneckList"><div class="empty-msg">Loading...</div></div>
      </div>

      <div class="side-panel">
        <h3>Overdue Items</h3>
        <div id="overdueList"><div class="empty-msg">Loading...</div></div>
      </div>

      <div class="side-panel">
        <h3>Jobs in Schedule</h3>
        <div id="jobList"><div class="empty-msg">Loading...</div></div>
      </div>
    </div>
  </div>
</div>

<script>
let currentDate = new Date().toISOString().slice(0, 10);
document.getElementById('dateSelect').value = currentDate;

async function fetchJSON(url) {
  const r = await fetch(url);
  return r.json();
}

function prevDay() {
  const d = new Date(currentDate);
  d.setDate(d.getDate() - 1);
  currentDate = d.toISOString().slice(0, 10);
  document.getElementById('dateSelect').value = currentDate;
  loadDay();
}

function nextDay() {
  const d = new Date(currentDate);
  d.setDate(d.getDate() + 1);
  currentDate = d.toISOString().slice(0, 10);
  document.getElementById('dateSelect').value = currentDate;
  loadDay();
}

function priorityBadge(p) {
  const map = {1: ['Urgent', 'red'], 2: ['High', 'orange'], 3: ['Normal', 'blue'], 4: ['Low', 'gray']};
  const [label, color] = map[p] || ['Normal', 'blue'];
  return `<span class="badge badge-${color}">${label}</span>`;
}

function statusBadge(s) {
  const map = {pending: 'blue', in_progress: 'orange', completed: 'green', skipped: 'gray'};
  return `<span class="badge badge-${map[s]||'gray'}">${s}</span>`;
}

async function loadSummary() {
  const data = await fetchJSON('/api/schedule/summary');
  if (!data.ok) return;
  const s = data.summary;
  document.getElementById('statTodayCount').textContent = s.today.entry_count;
  document.getElementById('statTodayMinutes').textContent = s.today.total_minutes + ' min';
  document.getElementById('statWeekCount').textContent = s.this_week.entry_count;
  document.getElementById('statWeekMinutes').textContent = s.this_week.total_minutes + ' min';
  document.getElementById('statPending').textContent = s.pending;
  document.getElementById('statOverdue').textContent = s.overdue;
  document.getElementById('statCompleted').textContent = s.completed;
  document.getElementById('statTotal').textContent = s.total_entries;

  // Jobs list
  const jobDiv = document.getElementById('jobList');
  const jobs = Object.entries(s.by_job);
  if (jobs.length === 0) {
    jobDiv.innerHTML = '<div class="empty-msg">No jobs scheduled</div>';
  } else {
    jobDiv.innerHTML = jobs.map(([jc, d]) =>
      `<div class="job-item" onclick="window.location.href='/work-orders/${encodeURIComponent(jc)}'"><span>${jc}</span><span>${d.count} items · ${d.minutes} min</span></div>`
    ).join('');
  }
}

async function loadCapacity() {
  currentDate = document.getElementById('dateSelect').value || currentDate;
  document.getElementById('capacityDate').textContent = currentDate;
  const data = await fetchJSON('/api/schedule/capacity/usage?date=' + currentDate);
  if (!data.ok) return;
  const grid = document.getElementById('capacityGrid');
  const machines = Object.values(data.usage);
  if (machines.length === 0) {
    grid.innerHTML = '<div class="empty-msg">No machines configured</div>';
    return;
  }
  grid.innerHTML = machines.map(m => {
    const pct = m.utilization_pct;
    const color = m.over_capacity ? 'var(--red)' : pct > 80 ? 'var(--orange)' : pct > 50 ? 'var(--yellow)' : 'var(--green)';
    const pctColor = m.over_capacity ? 'color:var(--red)' : pct > 80 ? 'color:var(--orange)' : '';
    return `<div class="cap-row" onclick="window.location.href='/work-station/${encodeURIComponent(m.machine || m.label)}'">
      <div class="cap-header">
        <span class="cap-label">${m.label}</span>
        <span class="cap-pct" style="${pctColor}">${pct}%${m.over_capacity ? ' OVER' : ''}</span>
      </div>
      <div class="cap-bar"><div class="cap-fill" style="width:${Math.min(pct,100)}%;background:${color}"></div></div>
      <div class="cap-details">
        <span>${m.scheduled_minutes} / ${m.available_minutes} min</span>
        <span>${m.entry_count} items</span>
        <span>${m.remaining_minutes} min remaining</span>
      </div>
    </div>`;
  }).join('');

  // Populate machine filter
  const sel = document.getElementById('machineFilter');
  if (sel.options.length <= 1) {
    machines.forEach(m => {
      const opt = document.createElement('option');
      opt.value = m.machine;
      opt.textContent = m.label;
      sel.appendChild(opt);
    });
  }
}

async function loadDay() {
  currentDate = document.getElementById('dateSelect').value || currentDate;
  const machine = document.getElementById('machineFilter').value;
  document.getElementById('dayLabel').textContent = currentDate;

  const url = '/api/schedule/date?date=' + currentDate + (machine ? '&machine=' + machine : '');
  const data = await fetchJSON(url);
  if (!data.ok) return;

  const div = document.getElementById('daySchedule');
  if (data.entries.length === 0) {
    div.innerHTML = '<div class="empty-msg">No items scheduled for this date</div>';
  } else {
    div.innerHTML = '<div class="entry-list">' + data.entries.map(e =>
      `<div class="entry-card priority-${e.priority}" onclick="window.location.href='/work-orders/${encodeURIComponent(e.job_code)}'">
        <div class="entry-top">
          <span class="entry-mark">${e.ship_mark || e.item_id}</span>
          <span>${priorityBadge(e.priority)} ${statusBadge(e.status)}</span>
        </div>
        <div class="entry-meta">
          ${e.component_type || ''} · ${e.machine} · ${e.estimated_minutes} min
          ${e.assigned_to ? ' · ' + e.assigned_to : ''} · ${e.job_code}
        </div>
        ${e.notes ? '<div class="entry-meta" style="margin-top:2px">' + e.notes + '</div>' : ''}
      </div>`
    ).join('') + '</div>';
  }

  loadCapacity();
  loadSummary();
}

async function loadBottlenecks() {
  const data = await fetchJSON('/api/schedule/bottlenecks?days=14');
  if (!data.ok) return;
  const div = document.getElementById('bottleneckList');
  if (data.bottlenecks.length === 0) {
    div.innerHTML = '<div class="empty-msg">No bottlenecks detected</div>';
    return;
  }
  div.innerHTML = data.bottlenecks.slice(0, 8).map(b =>
    `<div class="bottleneck-item" onclick="window.location.href='/work-station/${encodeURIComponent(b.machine || b.label)}'">
      <div class="bn-label" style="color:${b.over_by_minutes > 0 ? 'var(--red)' : 'var(--orange)'}">
        ${b.label} — ${b.date}
      </div>
      <div class="bn-detail">${b.utilization_pct}% · ${b.recommendation.slice(0, 80)}...</div>
    </div>`
  ).join('');
}

async function loadOverdue() {
  const data = await fetchJSON('/api/schedule/overdue');
  if (!data.ok) return;
  const div = document.getElementById('overdueList');
  if (data.overdue.length === 0) {
    div.innerHTML = '<div class="empty-msg">No overdue items</div>';
    return;
  }
  div.innerHTML = data.overdue.slice(0, 8).map(e =>
    `<div class="overdue-item" onclick="window.location.href='/work-station/${encodeURIComponent(e.machine)}'">
      <span class="overdue-mark">${e.ship_mark || e.item_id}</span>
      <span style="color:var(--muted);font-size:12px"> · ${e.machine} · due ${e.scheduled_date}</span>
    </div>`
  ).join('');
}

async function loadForecast() {
  const data = await fetchJSON('/api/schedule/capacity/forecast?days=14');
  if (!data.ok) return;
  const div = document.getElementById('daySchedule');
  div.innerHTML = '<div class="section-title">14-Day Capacity Forecast</div>' +
    data.forecast.filter(d => !d.is_weekend).map(d => {
      const pct = d.overall_utilization_pct;
      const color = pct > 100 ? 'var(--red)' : pct > 80 ? 'var(--orange)' : pct > 50 ? 'var(--yellow)' : 'var(--green)';
      const over = d.over_capacity_machines.length > 0;
      return `<div class="cap-row">
        <div class="cap-header">
          <span class="cap-label">${d.weekday} — ${d.date}</span>
          <span class="cap-pct" style="color:${color}">${pct}%${over ? ' ⚠' : ''}</span>
        </div>
        <div class="cap-bar"><div class="cap-fill" style="width:${Math.min(pct,100)}%;background:${color}"></div></div>
        <div class="cap-details">
          <span>${d.entry_count} items</span>
          <span>${d.total_scheduled_minutes} / ${d.total_available_minutes} min</span>
          ${over ? '<span style="color:var(--red)">Over: ' + d.over_capacity_machines.join(', ') + '</span>' : ''}
        </div>
      </div>`;
    }).join('');
}

// Init
loadDay();
loadBottlenecks();
loadOverdue();

// Auto-refresh every 60 seconds
setInterval(() => { loadDay(); loadBottlenecks(); loadOverdue(); }, 60000);
</script>
</body>
</html>"""
