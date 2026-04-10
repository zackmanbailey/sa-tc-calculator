"""
TitanForge — Mobile QR Scanner Page
====================================
Lightweight, mobile-optimized page for shop floor tablets and phones.
Workers scan QR stickers with their device camera to start/finish items.

Uses html5-qrcode library (MIT) loaded from CDN for camera-based QR scanning.
"""

QR_SCANNER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<title>TitanForge Scanner</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #0F172A; color: #F1F5F9;
    min-height: 100vh; overflow-x: hidden;
    -webkit-tap-highlight-color: transparent;
  }

  /* ── Top bar ── */
  .top-bar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 16px; background: #1E293B;
    border-bottom: 2px solid #C89A2E;
  }
  .top-bar h1 { font-size: 18px; font-weight: 700; letter-spacing: 0.5px; }
  .top-bar .user-badge {
    font-size: 12px; background: #334155; padding: 4px 10px;
    border-radius: 12px; color: #94A3B8;
  }

  /* ── Status banner ── */
  .status-banner {
    padding: 10px 16px; text-align: center;
    font-size: 13px; font-weight: 600;
    transition: all 0.3s ease;
  }
  .status-banner.ready { background: #1E40AF; color: #BFDBFE; }
  .status-banner.scanning { background: #065F46; color: #A7F3D0; }
  .status-banner.success { background: #166534; color: #BBF7D0; }
  .status-banner.error { background: #991B1B; color: #FECACA; }

  /* ── Scanner area ── */
  .scanner-wrap {
    padding: 16px; display: flex; flex-direction: column;
    align-items: center; gap: 12px;
  }
  #qr-reader {
    width: 100%; max-width: 400px;
    border-radius: 12px; overflow: hidden;
    border: 2px solid #334155;
  }
  #qr-reader video { border-radius: 12px; }

  /* ── Camera controls ── */
  .cam-controls {
    display: flex; gap: 10px; flex-wrap: wrap; justify-content: center;
  }
  .cam-btn {
    padding: 10px 20px; border-radius: 8px; border: none;
    font-size: 15px; font-weight: 600; cursor: pointer;
    transition: all 0.2s; min-width: 120px;
    display: flex; align-items: center; justify-content: center; gap: 6px;
  }
  .cam-btn.primary { background: #C89A2E; color: #0F172A; }
  .cam-btn.primary:active { background: #A67C1A; transform: scale(0.97); }
  .cam-btn.secondary { background: #334155; color: #CBD5E1; }
  .cam-btn.secondary:active { background: #475569; }
  .cam-btn.danger { background: #DC2626; color: #FFF; }
  .cam-btn.danger:active { background: #B91C1C; }
  .cam-btn:disabled { opacity: 0.5; pointer-events: none; }

  /* ── Scan result card ── */
  .result-card {
    display: none; margin: 16px; padding: 20px;
    background: #1E293B; border-radius: 12px;
    border: 1px solid #334155;
  }
  .result-card.visible { display: block; }
  .result-card .mark {
    font-size: 32px; font-weight: 800; color: #C89A2E;
  }
  .result-card .desc {
    font-size: 14px; color: #94A3B8; margin: 4px 0 16px;
  }
  .info-grid {
    display: grid; grid-template-columns: 1fr 1fr; gap: 8px;
    margin-bottom: 16px;
  }
  .info-cell {
    background: #0F172A; padding: 10px 12px; border-radius: 8px;
  }
  .info-cell .label { font-size: 10px; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px; }
  .info-cell .value { font-size: 16px; font-weight: 700; color: #F1F5F9; margin-top: 2px; }

  .status-row {
    display: flex; align-items: center; gap: 8px;
    margin-bottom: 16px; padding: 10px 12px;
    background: #0F172A; border-radius: 8px;
  }
  .status-dot { width: 10px; height: 10px; border-radius: 50%; }
  .status-dot.queued { background: #64748B; }
  .status-dot.in_progress { background: #F59E0B; }
  .status-dot.complete { background: #10B981; }
  .status-label { font-size: 14px; font-weight: 600; }

  /* ── Action buttons ── */
  .action-row {
    display: flex; gap: 10px;
  }
  .action-btn {
    flex: 1; padding: 16px; border: none; border-radius: 10px;
    font-size: 16px; font-weight: 700; cursor: pointer;
    transition: all 0.2s; text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  .action-btn:active { transform: scale(0.97); }
  .action-btn.start { background: #10B981; color: #FFF; }
  .action-btn.start:active { background: #059669; }
  .action-btn.finish { background: #3B82F6; color: #FFF; }
  .action-btn.finish:active { background: #2563EB; }
  .action-btn:disabled { opacity: 0.4; pointer-events: none; }

  /* ── History list ── */
  .history { margin: 16px; }
  .history h3 { font-size: 14px; color: #64748B; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; }
  .history-item {
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 12px; background: #1E293B; border-radius: 8px;
    margin-bottom: 6px; font-size: 13px;
  }
  .history-item .hi-mark { font-weight: 700; color: #C89A2E; }
  .history-item .hi-action { color: #10B981; font-weight: 600; }
  .history-item .hi-time { color: #64748B; }

  /* ── Manual entry fallback ── */
  .manual-entry {
    margin: 16px; padding: 16px; background: #1E293B;
    border-radius: 12px; border: 1px solid #334155;
  }
  .manual-entry h3 { font-size: 13px; color: #64748B; margin-bottom: 10px; }
  .manual-input {
    width: 100%; padding: 12px; background: #0F172A;
    border: 1px solid #475569; border-radius: 8px;
    color: #F1F5F9; font-size: 16px; font-family: 'Courier New', monospace;
  }
  .manual-input:focus { outline: none; border-color: #C89A2E; }
  .manual-input::placeholder { color: #475569; }

  /* ── Toast ── */
  .toast {
    position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
    padding: 12px 24px; border-radius: 10px; font-size: 14px;
    font-weight: 600; z-index: 9999; opacity: 0;
    transition: opacity 0.3s; pointer-events: none;
  }
  .toast.show { opacity: 1; }
  .toast.ok { background: #166534; color: #BBF7D0; }
  .toast.err { background: #991B1B; color: #FECACA; }

  /* ── Loading spinner ── */
  .spinner {
    display: inline-block; width: 18px; height: 18px;
    border: 2px solid rgba(255,255,255,0.3);
    border-top-color: #FFF; border-radius: 50%;
    animation: spin 0.6s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  @media (min-width: 600px) {
    .scanner-wrap { max-width: 500px; margin: 0 auto; }
    .result-card, .history, .manual-entry { max-width: 500px; margin-left: auto; margin-right: auto; }
  }
</style>
</head>
<body>

<!-- Top bar -->
<div class="top-bar">
  <h1>TITANFORGE SCANNER</h1>
  <span class="user-badge" id="userBadge">{{USER_NAME}}</span>
</div>

<!-- Status banner -->
<div class="status-banner ready" id="statusBanner">
  Point your camera at a QR sticker or enter item ID below
</div>

<!-- Scanner -->
<div class="scanner-wrap">
  <div id="qr-reader"></div>
  <div class="cam-controls">
    <button class="cam-btn primary" id="btnStartCam" onclick="startCamera()">
      &#x1F4F7; Start Camera
    </button>
    <button class="cam-btn secondary" id="btnStopCam" onclick="stopCamera()" disabled>
      Stop Camera
    </button>
    <button class="cam-btn secondary" id="btnFlipCam" onclick="flipCamera()" disabled>
      &#x1F504; Flip
    </button>
  </div>
</div>

<!-- Manual entry -->
<div class="manual-entry">
  <h3>Or type / paste item ID manually</h3>
  <input class="manual-input" id="manualInput" type="text"
         placeholder="e.g. ITM-C1-001" autocomplete="off" autocorrect="off"
         onkeydown="if(event.key==='Enter') manualLookup()">
  <button class="cam-btn primary" style="margin-top:10px;width:100%"
          onclick="manualLookup()">Look Up</button>
</div>

<!-- Scan result -->
<div class="result-card" id="resultCard">
  <div class="mark" id="rMark">C1</div>
  <div class="desc" id="rDesc">Column C1 — 14x4x10GA box beam</div>
  <div class="info-grid">
    <div class="info-cell">
      <div class="label">Job Code</div>
      <div class="value" id="rJob">SA2401-A</div>
    </div>
    <div class="info-cell">
      <div class="label">Quantity</div>
      <div class="value" id="rQty">4</div>
    </div>
    <div class="info-cell">
      <div class="label">Machine</div>
      <div class="value" id="rMachine">WELDING</div>
    </div>
    <div class="info-cell">
      <div class="label">Work Order</div>
      <div class="value" id="rWO" style="font-size:12px">WO-...</div>
    </div>
  </div>
  <div class="status-row">
    <div class="status-dot" id="rDot"></div>
    <span class="status-label" id="rStatus">Queued</span>
  </div>
  <div class="action-row">
    <button class="action-btn start" id="btnStart" onclick="doAction('start')">
      &#x25B6; Start
    </button>
    <button class="action-btn finish" id="btnFinish" onclick="doAction('finish')">
      &#x2713; Finish
    </button>
  </div>
</div>

<!-- Scan history -->
<div class="history" id="historySection" style="display:none">
  <h3>Recent Scans</h3>
  <div id="historyList"></div>
</div>

<!-- Toast -->
<div class="toast" id="toast"></div>

<!-- html5-qrcode from CDN -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/html5-qrcode/2.3.8/html5-qrcode.min.js"></script>
<script>
(function() {
  // ── State ──
  let scanner = null;
  let scanning = false;
  let currentCamIdx = 0;
  let cameras = [];
  let lastScannedCode = '';
  let cooldownTimer = null;
  const scanHistory = [];
  const JOB_CODE = '{{JOB_CODE}}';
  const USER_NAME = '{{USER_NAME}}';

  // ── Elements ──
  const statusBanner = document.getElementById('statusBanner');
  const resultCard   = document.getElementById('resultCard');
  const btnStartCam  = document.getElementById('btnStartCam');
  const btnStopCam   = document.getElementById('btnStopCam');
  const btnFlipCam   = document.getElementById('btnFlipCam');

  // ── Camera ──
  window.startCamera = async function() {
    try {
      btnStartCam.disabled = true;
      btnStartCam.innerHTML = '<span class="spinner"></span> Opening...';
      setStatus('scanning', 'Starting camera...');

      if (!scanner) {
        scanner = new Html5Qrcode('qr-reader');
      }

      // Get available cameras
      cameras = await Html5Qrcode.getCameras();
      if (!cameras || cameras.length === 0) {
        throw new Error('No cameras found on this device.');
      }

      // Prefer back camera
      currentCamIdx = cameras.findIndex(c =>
        /back|rear|environment/i.test(c.label)
      );
      if (currentCamIdx < 0) currentCamIdx = 0;

      await scanner.start(
        cameras[currentCamIdx].id,
        {
          fps: 10,
          qrbox: function(vw, vh) {
            var s = Math.min(vw, vh) * 0.75;
            return { width: Math.floor(s), height: Math.floor(s) };
          },
          aspectRatio: 1.0,
        },
        onScanSuccess,
        function() {} // ignore scan failures
      );

      scanning = true;
      btnStartCam.style.display = 'none';
      btnStopCam.disabled = false;
      btnFlipCam.disabled = cameras.length <= 1;
      setStatus('scanning', 'Camera active — point at a QR sticker');

    } catch(e) {
      btnStartCam.disabled = false;
      btnStartCam.innerHTML = '&#x1F4F7; Start Camera';
      setStatus('error', 'Camera error: ' + (e.message || e));
      console.error('Camera error:', e);
    }
  };

  window.stopCamera = async function() {
    if (scanner && scanning) {
      try { await scanner.stop(); } catch(e) {}
      scanning = false;
    }
    btnStartCam.style.display = '';
    btnStartCam.disabled = false;
    btnStartCam.innerHTML = '&#x1F4F7; Start Camera';
    btnStopCam.disabled = true;
    btnFlipCam.disabled = true;
    setStatus('ready', 'Camera stopped — tap Start Camera to scan again');
  };

  window.flipCamera = async function() {
    if (!scanning || cameras.length <= 1) return;
    await scanner.stop();
    scanning = false;
    currentCamIdx = (currentCamIdx + 1) % cameras.length;
    await scanner.start(
      cameras[currentCamIdx].id,
      { fps: 10, qrbox: function(vw,vh){ var s=Math.min(vw,vh)*0.75; return {width:Math.floor(s),height:Math.floor(s)}; } },
      onScanSuccess,
      function(){}
    );
    scanning = true;
    toast('Switched to ' + (cameras[currentCamIdx].label || 'Camera ' + (currentCamIdx+1)), 'ok');
  };

  // ── Scan handler ──
  function onScanSuccess(decodedText) {
    // Prevent rapid re-scans of same code
    if (decodedText === lastScannedCode && cooldownTimer) return;
    lastScannedCode = decodedText;
    if (cooldownTimer) clearTimeout(cooldownTimer);
    cooldownTimer = setTimeout(function(){ lastScannedCode = ''; cooldownTimer = null; }, 3000);

    // Vibrate feedback
    if (navigator.vibrate) navigator.vibrate(100);

    // Parse the QR URL: .../work-orders/{job_code}?scan={item_id}
    var parsed = parseQRData(decodedText);
    if (parsed) {
      lookupItem(parsed.job_code, parsed.item_id);
    } else {
      // Maybe it's a raw item_id
      lookupItem(JOB_CODE, decodedText.trim());
    }
  }

  function parseQRData(text) {
    try {
      var url = new URL(text);
      var parts = url.pathname.split('/');
      var woIdx = parts.indexOf('work-orders');
      if (woIdx >= 0 && parts[woIdx+1]) {
        var jobCode = decodeURIComponent(parts[woIdx+1]);
        var itemId = url.searchParams.get('scan');
        if (jobCode && itemId) return { job_code: jobCode, item_id: itemId };
      }
    } catch(e) {}
    return null;
  }

  // ── Manual entry ──
  window.manualLookup = function() {
    var val = document.getElementById('manualInput').value.trim();
    if (!val) return;
    lookupItem(JOB_CODE, val);
    document.getElementById('manualInput').value = '';
  };

  // ── Item lookup ──
  function lookupItem(jobCode, itemId) {
    setStatus('scanning', 'Looking up ' + itemId + '...');

    fetch('/api/work-orders/detail?job_code=' + encodeURIComponent(jobCode) + '&item_id=' + encodeURIComponent(itemId))
      .then(function(r) { return r.json(); })
      .then(function(data) {
        if (!data.ok || !data.item) {
          setStatus('error', 'Item not found: ' + itemId);
          toast('Item not found', 'err');
          return;
        }
        showResult(data, jobCode);
        setStatus('success', 'Found: ' + (data.item.ship_mark || itemId));
      })
      .catch(function(e) {
        // If the detail endpoint doesn't exist yet, show a simulated result
        setStatus('error', 'Lookup failed: ' + e.message);
        toast('Network error', 'err');
      });
  }

  // ── Show result ──
  window._currentItem = null;
  function showResult(data, jobCode) {
    var item = data.item;
    window._currentItem = { job_code: jobCode, item: item, wo: data.work_order || {} };

    document.getElementById('rMark').textContent = item.ship_mark || '—';
    document.getElementById('rDesc').textContent = item.description || '';
    document.getElementById('rJob').textContent = jobCode;
    document.getElementById('rQty').textContent = item.quantity || '—';
    document.getElementById('rMachine').textContent = item.machine || '—';
    document.getElementById('rWO').textContent = (data.work_order || {}).work_order_id || '—';

    var st = (item.status || 'queued').toLowerCase();
    var dot = document.getElementById('rDot');
    dot.className = 'status-dot ' + st;
    document.getElementById('rStatus').textContent = st.replace('_', ' ').toUpperCase();

    // Enable/disable action buttons based on status
    document.getElementById('btnStart').disabled = (st === 'in_progress' || st === 'complete');
    document.getElementById('btnFinish').disabled = (st !== 'in_progress');

    resultCard.classList.add('visible');
    resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  // ── Start / Finish action ──
  window.doAction = function(action) {
    if (!window._currentItem) return;
    var ci = window._currentItem;
    var btn = action === 'start' ? document.getElementById('btnStart') : document.getElementById('btnFinish');
    var origHTML = btn.innerHTML;
    btn.innerHTML = '<span class="spinner"></span>';
    btn.disabled = true;

    fetch('/api/work-orders/qr-scan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        job_code: ci.job_code,
        item_id: ci.item.item_id,
        action: action,
        scanned_by: USER_NAME
      })
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
      if (data.ok) {
        toast((action === 'start' ? 'Started' : 'Finished') + ' ' + ci.item.ship_mark, 'ok');
        // Update card status
        var newStatus = action === 'start' ? 'in_progress' : 'complete';
        ci.item.status = newStatus;
        showResult({ item: ci.item, work_order: ci.wo }, ci.job_code);
        addToHistory(ci.item.ship_mark, action);
        setStatus('success', (action === 'start' ? 'Started' : 'Finished') + ': ' + ci.item.ship_mark);
      } else {
        toast(data.error || 'Action failed', 'err');
        btn.innerHTML = origHTML;
        btn.disabled = false;
      }
    })
    .catch(function(e) {
      toast('Network error: ' + e.message, 'err');
      btn.innerHTML = origHTML;
      btn.disabled = false;
    });
  };

  // ── History ──
  function addToHistory(mark, action) {
    scanHistory.unshift({
      mark: mark,
      action: action,
      time: new Date().toLocaleTimeString()
    });
    if (scanHistory.length > 20) scanHistory.pop();
    renderHistory();
  }

  function renderHistory() {
    if (scanHistory.length === 0) {
      document.getElementById('historySection').style.display = 'none';
      return;
    }
    document.getElementById('historySection').style.display = '';
    var html = '';
    scanHistory.forEach(function(h) {
      html += '<div class="history-item">'
        + '<span class="hi-mark">' + h.mark + '</span>'
        + '<span class="hi-action">' + h.action.toUpperCase() + '</span>'
        + '<span class="hi-time">' + h.time + '</span>'
        + '</div>';
    });
    document.getElementById('historyList').innerHTML = html;
  }

  // ── Helpers ──
  function setStatus(type, msg) {
    statusBanner.className = 'status-banner ' + type;
    statusBanner.textContent = msg;
  }

  function toast(msg, type) {
    var t = document.getElementById('toast');
    t.textContent = msg;
    t.className = 'toast ' + (type || 'ok') + ' show';
    setTimeout(function(){ t.classList.remove('show'); }, 2500);
  }
  window.toast = toast;

})();
</script>
</body>
</html>
"""
