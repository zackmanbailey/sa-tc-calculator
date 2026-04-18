"""
TitanForge — Live TV Production Dashboard
==========================================
Full-screen, auto-refreshing dashboard designed for shop floor TVs.
Shows real-time production metrics, machine gauges, leaderboard, and activity feed.
No interaction needed — pure display. Auto-rotates panels every 15 seconds.
"""

TV_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="300">
<title>TitanForge — Shop Floor Live</title>
<style>
  @keyframes pulse { 0%,100%{ opacity:1 } 50%{ opacity:.6 } }
  @keyframes slideIn { from{ transform:translateY(20px); opacity:0 } to{ transform:translateY(0); opacity:1 } }
  @keyframes fillBar { from{ width:0 } }
  @keyframes confetti { 0%{ transform:translateY(0) rotate(0deg); opacity:1 }
    100%{ transform:translateY(400px) rotate(720deg); opacity:0 } }

  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #0B1120; color: #E2E8F0;
    overflow: hidden; height: 100vh; width: 100vw;
  }

  /* ── TOP BAR ── */
  .top-bar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 24px; background: #111827;
    border-bottom: 3px solid #C89A2E;
    height: 56px;
  }
  .top-bar .brand {
    font-size: 22px; font-weight: 800; letter-spacing: 1px; color: #FFF;
  }
  .top-bar .brand span { color: #C89A2E; }
  .top-bar .live {
    display: flex; align-items: center; gap: 8px;
    font-size: 13px; color: #10B981; font-weight: 600;
  }
  .top-bar .live .dot {
    width: 10px; height: 10px; background: #10B981;
    border-radius: 50%; animation: pulse 1.5s infinite;
  }
  .top-bar .clock { font-size: 22px; font-weight: 300; color: #94A3B8; font-variant-numeric: tabular-nums; }

  /* ── MAIN GRID ── */
  .main { display: grid; grid-template-columns: 1fr 320px;
    grid-template-rows: auto 1fr; height: calc(100vh - 56px); gap: 0; }

  /* ── KPI STRIP ── */
  .kpi-strip {
    grid-column: 1 / -1; display: flex; gap: 0;
    background: #111827; border-bottom: 1px solid #1E293B;
  }
  .kpi {
    flex: 1; padding: 14px 20px; text-align: center;
    border-right: 1px solid #1E293B;
  }
  .kpi:last-child { border-right: none; }
  .kpi .val { font-size: 32px; font-weight: 800; color: #FFF; line-height: 1.1; }
  .kpi .val.green { color: #10B981; }
  .kpi .val.gold { color: #C89A2E; }
  .kpi .val.blue { color: #3B82F6; }
  .kpi .val.amber { color: #F59E0B; }
  .kpi .lbl { font-size: 11px; color: #64748B; text-transform: uppercase;
    letter-spacing: 1px; margin-top: 2px; }

  /* ── LEFT CONTENT AREA ── */
  .left-content { padding: 16px 20px; overflow: hidden; display: flex; flex-direction: column; gap: 16px; }

  /* ── DAILY TARGET BAR ── */
  .target-bar {
    background: #111827; border-radius: 12px; padding: 16px 20px;
    border: 1px solid #1E293B;
  }
  .target-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
  .target-header .title { font-size: 13px; color: #64748B; text-transform: uppercase; letter-spacing: 1px; }
  .target-header .count { font-size: 20px; font-weight: 800; }
  .target-header .count .of { color: #475569; font-weight: 400; }
  .target-track {
    height: 24px; background: #1E293B; border-radius: 12px; overflow: hidden;
    position: relative;
  }
  .target-fill {
    height: 100%; border-radius: 12px;
    background: linear-gradient(90deg, #C89A2E, #F59E0B);
    transition: width 1s ease; animation: fillBar 1s ease;
  }
  .target-fill.done { background: linear-gradient(90deg, #10B981, #34D399); }
  .target-pct {
    position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
    font-size: 12px; font-weight: 700; color: #FFF;
  }

  /* ── MACHINE GAUGES ── */
  .machines-section { flex: 1; overflow: hidden; }
  .machines-section h3 { font-size: 13px; color: #64748B; text-transform: uppercase;
    letter-spacing: 1px; margin-bottom: 10px; }
  .machine-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 10px; }
  .machine-card {
    background: #111827; border-radius: 10px; padding: 14px;
    border: 2px solid #1E293B; transition: all 0.3s;
  }
  .machine-card.active { border-color: #10B981; box-shadow: 0 0 12px rgba(16,185,129,0.15); }
  .machine-card.idle { border-color: #1E293B; opacity: 0.6; }
  .machine-card.queued { border-color: #F59E0B; }
  .mc-name { font-size: 14px; font-weight: 700; margin-bottom: 6px; }
  .mc-stats { display: flex; gap: 12px; }
  .mc-stat { text-align: center; }
  .mc-stat .num { font-size: 20px; font-weight: 800; }
  .mc-stat .num.green { color: #10B981; }
  .mc-stat .num.amber { color: #F59E0B; }
  .mc-stat .num.gray { color: #475569; }
  .mc-stat .slbl { font-size: 9px; color: #64748B; text-transform: uppercase; }
  .mc-bar { height: 4px; background: #1E293B; border-radius: 2px; margin-top: 8px; overflow: hidden; }
  .mc-bar-fill { height: 100%; background: #10B981; border-radius: 2px; transition: width 0.5s; }
  .mc-active-item {
    margin-top: 6px; padding: 4px 8px; background: #0B1120;
    border-radius: 6px; font-size: 11px; color: #94A3B8;
    display: flex; justify-content: space-between;
  }
  .mc-active-item .mark { color: #C89A2E; font-weight: 700; }
  .mc-active-item .timer { color: #10B981; font-variant-numeric: tabular-nums; }

  /* ── IDLE ALERT ── */
  .idle-alert {
    display: none; padding: 10px 16px; background: #7C2D12;
    border-radius: 8px; margin-bottom: 10px;
    font-size: 13px; color: #FED7AA; font-weight: 600;
    animation: pulse 2s infinite;
  }
  .idle-alert.visible { display: flex; align-items: center; gap: 8px; }

  /* ── RIGHT SIDEBAR ── */
  .right-sidebar {
    background: #111827; border-left: 1px solid #1E293B;
    display: flex; flex-direction: column; overflow: hidden;
  }

  /* ── LEADERBOARD ── */
  .leaderboard { padding: 16px; flex: 1; overflow-y: auto; }
  .leaderboard h3 {
    font-size: 13px; color: #64748B; text-transform: uppercase;
    letter-spacing: 1px; margin-bottom: 10px;
    display: flex; align-items: center; gap: 6px;
  }
  .lb-row {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 12px; border-radius: 8px; margin-bottom: 6px;
    background: #0B1120; transition: all 0.3s;
    animation: slideIn 0.3s ease;
  }
  .lb-row.first { background: linear-gradient(135deg, #78350F, #451A03);
    border: 1px solid #C89A2E; }
  .lb-row.second { background: linear-gradient(135deg, #1E293B, #0F172A);
    border: 1px solid #64748B; }
  .lb-row.third { background: linear-gradient(135deg, #1C1917, #0C0A09);
    border: 1px solid #A16207; }
  .lb-rank { font-size: 18px; font-weight: 800; width: 28px; text-align: center; }
  .lb-rank.gold { color: #C89A2E; }
  .lb-rank.silver { color: #94A3B8; }
  .lb-rank.bronze { color: #D97706; }
  .lb-info { flex: 1; }
  .lb-name { font-size: 14px; font-weight: 700; }
  .lb-badges { font-size: 12px; margin-top: 2px; }
  .lb-count { font-size: 22px; font-weight: 800; color: #10B981; }
  .lb-unit { font-size: 10px; color: #64748B; }

  /* ── ACTIVITY FEED ── */
  .activity { padding: 0 16px 16px; max-height: 280px; overflow-y: auto; }
  .activity h3 { font-size: 13px; color: #64748B; text-transform: uppercase;
    letter-spacing: 1px; margin-bottom: 8px; padding-top: 12px;
    border-top: 1px solid #1E293B; }
  .feed-item {
    padding: 8px 0; border-bottom: 1px solid #1E293B;
    font-size: 12px; animation: slideIn 0.4s ease;
  }
  .feed-item:last-child { border-bottom: none; }
  .feed-mark { color: #C89A2E; font-weight: 700; }
  .feed-action { font-weight: 600; }
  .feed-action.started { color: #F59E0B; }
  .feed-action.finished { color: #10B981; }
  .feed-time { color: #475569; float: right; }
  .feed-worker { color: #64748B; }

  /* ── CONFETTI OVERLAY ── */
  .confetti-container {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    pointer-events: none; z-index: 9999; overflow: hidden;
  }
  .confetti-piece {
    position: absolute; top: -20px; width: 10px; height: 10px;
    animation: confetti 3s ease-out forwards;
  }

/* ── Responsive ── */
@media (max-width: 768px) {
    .page-header h1 { font-size: 22px; }
    .kpi-strip { grid-template-columns: 1fr 1fr; gap: 10px; }
    .machine-grid { grid-template-columns: 1fr; }
    .top-bar { flex-direction: column; gap: 8px; }
    .leaderboard { padding: 12px; }
}
@media (max-width: 480px) {
    .kpi-strip { grid-template-columns: 1fr; }
    .kpi-strip { grid-template-columns: 1fr; }
    .machine-grid { grid-template-columns: 1fr; }
}
</style>
</head>
<body>

<!-- TOP BAR -->
<div class="top-bar">
  <div class="brand">TITAN<span>FORGE</span> &nbsp;LIVE</div>
  <div class="live"><div class="dot"></div> LIVE PRODUCTION</div>
  <div class="clock" id="clock"></div>
</div>

<!-- MAIN GRID -->
<div class="main">

  <!-- KPI STRIP -->
  <div class="kpi-strip" id="kpiStrip">
    <div class="kpi"><div class="val green" id="kCompleted">0</div><div class="lbl">Completed Today</div></div>
    <div class="kpi"><div class="val amber" id="kInProgress">0</div><div class="lbl">In Progress</div></div>
    <div class="kpi"><div class="val" id="kQueued">0</div><div class="lbl">Queued</div></div>
    <div class="kpi"><div class="val blue" id="kActiveWO">0</div><div class="lbl">Active WOs</div></div>
    <div class="kpi"><div class="val gold" id="kWorkers">0</div><div class="lbl">Active Workers</div></div>
    <div class="kpi"><div class="val" id="kAvgTime">—</div><div class="lbl">Avg Fab Time</div></div>
  </div>

  <!-- LEFT CONTENT -->
  <div class="left-content">
    <!-- Daily Target -->
    <div class="target-bar">
      <div class="target-header">
        <span class="title">Daily Production Target</span>
        <span class="count"><span id="tDone">0</span> <span class="of">/ <span id="tTarget">15</span></span></span>
      </div>
      <div class="target-track">
        <div class="target-fill" id="tFill" style="width:0%"></div>
        <span class="target-pct" id="tPct">0%</span>
      </div>
    </div>

    <!-- Idle Alert -->
    <div class="idle-alert" id="idleAlert">
      &#x26A0;&#xFE0F; <span id="idleMsg">Machine WELDING has been idle for 15+ minutes</span>
    </div>

    <!-- Machine Gauges -->
    <div class="machines-section">
      <h3>Machine Utilization</h3>
      <div class="machine-grid" id="machineGrid"></div>
    </div>
  </div>

  <!-- RIGHT SIDEBAR -->
  <div class="right-sidebar">
    <div class="leaderboard">
      <h3>&#x1F3C6; Today's Leaderboard</h3>
      <div id="lbList"></div>
    </div>
    <div class="activity">
      <h3>Activity Feed</h3>
      <div id="actFeed"></div>
    </div>
  </div>

</div>

<!-- Confetti container -->
<div class="confetti-container" id="confettiBox"></div>

<script>
(function() {
  var REFRESH_MS = 10000;  // Refresh every 10 seconds

  // ── Clock ──
  function updateClock() {
    var now = new Date();
    document.getElementById('clock').textContent =
      now.toLocaleTimeString('en-US', { hour:'2-digit', minute:'2-digit', second:'2-digit' });
  }
  updateClock();
  setInterval(updateClock, 1000);

  // ── Load Data ──
  var prevCompleted = -1;

  function loadData() {
    Promise.all([
      fetch('/api/shop-floor/data').then(function(r){return r.json()}),
      fetch('/api/gamification/leaderboard?period=today').then(function(r){return r.json()}).catch(function(){return {ok:true,leaderboard:[]}}),
      fetch('/api/gamification/targets').then(function(r){return r.json()}).catch(function(){return {ok:true}})
    ]).then(function(results) {
      var sf = results[0];
      var lb = results[1];
      var tg = results[2];
      if (sf.ok) renderShopFloor(sf);
      if (lb.ok) renderLeaderboard(lb.leaderboard || []);
      if (tg.ok) renderTargets(tg);
    }).catch(function(e) { console.error('Refresh error:', e); });
  }

  function renderShopFloor(data) {
    var s = data.summary || {};
    document.getElementById('kCompleted').textContent = s.today_completed || 0;
    document.getElementById('kInProgress').textContent = s.in_progress_items || 0;
    document.getElementById('kQueued').textContent = s.queued_items || 0;
    document.getElementById('kActiveWO').textContent = s.active_wos || 0;
    document.getElementById('kWorkers').textContent = s.active_workers || 0;
    var avg = s.avg_fab_minutes;
    document.getElementById('kAvgTime').textContent = avg ? avg.toFixed(0) + 'm' : '—';

    // Check for celebration
    var newCompleted = s.today_completed || 0;
    if (prevCompleted >= 0 && newCompleted > prevCompleted) {
      fireConfetti();
    }
    prevCompleted = newCompleted;

    // Machines
    renderMachines(data.machines || {});

    // Activity feed
    renderActivity(data.events || []);
  }

  function renderMachines(machines) {
    var grid = document.getElementById('machineGrid');
    var html = '';
    var idleMachines = [];

    var keys = Object.keys(machines).sort();
    keys.forEach(function(k) {
      var m = machines[k];
      var total = (m.in_progress||0) + (m.queued||0) + (m.completed||0);
      var pct = total > 0 ? Math.round(100 * (m.completed||0) / total) : 0;
      var state = m.in_progress > 0 ? 'active' : (m.queued > 0 ? 'queued' : 'idle');

      if (state === 'idle' && (m.queued||0) > 0) idleMachines.push(m.name || k);

      html += '<div class="machine-card ' + state + '">'
        + '<div class="mc-name">' + (m.name || k) + '</div>'
        + '<div class="mc-stats">'
        + '  <div class="mc-stat"><div class="num green">' + (m.in_progress||0) + '</div><div class="slbl">Active</div></div>'
        + '  <div class="mc-stat"><div class="num amber">' + (m.queued||0) + '</div><div class="slbl">Queue</div></div>'
        + '  <div class="mc-stat"><div class="num gray">' + (m.completed||0) + '</div><div class="slbl">Done</div></div>'
        + '</div>'
        + '<div class="mc-bar"><div class="mc-bar-fill" style="width:' + pct + '%"></div></div>';

      // Show active items
      (m.active_items || []).slice(0,2).forEach(function(ai) {
        html += '<div class="mc-active-item">'
          + '<span class="mark">' + (ai.ship_mark||'—') + '</span>'
          + '<span class="timer">' + (ai.elapsed || '') + '</span>'
          + '</div>';
      });

      html += '</div>';
    });
    grid.innerHTML = html;

    // Idle alert
    var alert = document.getElementById('idleAlert');
    if (idleMachines.length > 0) {
      alert.classList.add('visible');
      document.getElementById('idleMsg').textContent =
        idleMachines.join(', ') + (idleMachines.length === 1 ? ' has' : ' have') + ' queued items but no active work';
    } else {
      alert.classList.remove('visible');
    }
  }

  function renderLeaderboard(lb) {
    var html = '';
    lb.slice(0, 8).forEach(function(e) {
      var cls = e.rank === 1 ? 'first' : (e.rank === 2 ? 'second' : (e.rank === 3 ? 'third' : ''));
      var rankCls = e.rank === 1 ? 'gold' : (e.rank === 2 ? 'silver' : (e.rank === 3 ? 'bronze' : ''));
      var rankIcon = e.rank === 1 ? '&#x1F947;' : (e.rank === 2 ? '&#x1F948;' : (e.rank === 3 ? '&#x1F949;' : e.rank));

      html += '<div class="lb-row ' + cls + '">'
        + '<div class="lb-rank ' + rankCls + '">' + rankIcon + '</div>'
        + '<div class="lb-info">'
        + '  <div class="lb-name">' + e.worker + '</div>'
        + '  <div class="lb-badges">' + (e.badges||[]).map(function(b){return b.icon}).join(' ') + '</div>'
        + '</div>'
        + '<div><div class="lb-count">' + e.completed + '</div><div class="lb-unit">items</div></div>'
        + '</div>';
    });
    if (lb.length === 0) {
      html = '<div style="text-align:center;color:#475569;padding:20px;font-size:13px">No completions yet today.<br>Start scanning!</div>';
    }
    document.getElementById('lbList').innerHTML = html;
  }

  function renderTargets(tg) {
    var done = tg.shop_completed || 0;
    var target = tg.shop_target || 15;
    var pct = Math.min(100, Math.round(100 * done / target));
    document.getElementById('tDone').textContent = done;
    document.getElementById('tTarget').textContent = target;
    document.getElementById('tPct').textContent = pct + '%';
    var fill = document.getElementById('tFill');
    fill.style.width = pct + '%';
    fill.className = 'target-fill' + (pct >= 100 ? ' done' : '');
  }

  function renderActivity(events) {
    var html = '';
    events.slice(0, 15).forEach(function(ev) {
      var action = ev.type === 'started' ? 'STARTED' : 'FINISHED';
      var cls = ev.type === 'started' ? 'started' : 'finished';
      var time = ev.time || '';
      html += '<div class="feed-item">'
        + '<span class="feed-mark">' + (ev.ship_mark||'—') + '</span> '
        + '<span class="feed-action ' + cls + '">' + action + '</span> '
        + '<span class="feed-worker">by ' + (ev.worker||'—') + '</span>'
        + '<span class="feed-time">' + time + '</span>'
        + '</div>';
    });
    document.getElementById('actFeed').innerHTML = html || '<div style="color:#475569;font-size:12px;padding:8px">No activity yet</div>';
  }

  // ── Confetti ──
  function fireConfetti() {
    var box = document.getElementById('confettiBox');
    var colors = ['#C89A2E','#10B981','#3B82F6','#F59E0B','#EC4899','#8B5CF6'];
    for (var i = 0; i < 40; i++) {
      var piece = document.createElement('div');
      piece.className = 'confetti-piece';
      piece.style.left = Math.random() * 100 + '%';
      piece.style.background = colors[Math.floor(Math.random()*colors.length)];
      piece.style.animationDelay = Math.random() * 0.5 + 's';
      piece.style.animationDuration = (2 + Math.random()*2) + 's';
      piece.style.transform = 'rotate(' + Math.random()*360 + 'deg)';
      box.appendChild(piece);
    }
    setTimeout(function() { box.innerHTML = ''; }, 4000);
  }

  // ── WebSocket — Live Updates ──
  var ws = null;
  var wsRetry = 0;
  var pollTimer = null;
  var usePolling = false;

  function connectWebSocket() {
    try {
      var proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
      ws = new WebSocket(proto + '//' + location.host + '/ws/live');

      ws.onopen = function() {
        console.log('[WS] Connected');
        wsRetry = 0;
        // Stop polling if WebSocket is active
        if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
        usePolling = false;
      };

      ws.onmessage = function(evt) {
        try {
          var msg = JSON.parse(evt.data);
          // Any live event triggers a full data refresh
          if (msg.type === 'scan' || msg.type === 'batch_scan' ||
              msg.type === 'wo_status' || msg.type === 'inventory_update') {
            loadData();
          }
        } catch(e) { console.error('[WS] Parse error:', e); }
      };

      ws.onclose = function() {
        console.log('[WS] Disconnected — retrying in', Math.min(5000, 1000 * Math.pow(2, wsRetry)), 'ms');
        ws = null;
        // Fall back to polling while disconnected
        if (!pollTimer) {
          usePolling = true;
          pollTimer = setInterval(loadData, REFRESH_MS);
        }
        // Exponential backoff reconnect (max 30s)
        var delay = Math.min(30000, 1000 * Math.pow(2, wsRetry));
        wsRetry++;
        setTimeout(connectWebSocket, delay);
      };

      ws.onerror = function(err) {
        console.error('[WS] Error:', err);
        if (ws) ws.close();
      };
    } catch(e) {
      console.error('[WS] Failed to connect:', e);
      // Fall back to polling
      usePolling = true;
      if (!pollTimer) { pollTimer = setInterval(loadData, REFRESH_MS); }
    }
  }

  // ── Init ──
  loadData();
  connectWebSocket();
  // Start polling as a safety net; WebSocket onopen will clear it
  pollTimer = setInterval(loadData, REFRESH_MS);

})();
</script>
</body>
</html>
"""
