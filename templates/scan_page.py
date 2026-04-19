"""
TitanForge v4 — QR/Barcode Scanner
=====================================
Camera-based scan, manual entry fallback, scan history, quick actions.
"""

SCAN_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a;
        --tf-card: #1e293b;
        --tf-text: #e2e8f0;
        --tf-muted: #94a3b8;
        --tf-gold: #d4a843;
        --tf-blue: #3b82f6;
    }
    .scan-container {
        max-width: 1000px; margin: 0 auto; padding: 24px 32px;
        font-family: 'Inter', system-ui, -apple-system, sans-serif; color: var(--tf-text);
    }
    .page-header { margin-bottom: 32px; }
    .page-header h1 { font-size: 28px; font-weight: 800; margin: 0 0 6px 0; }
    .page-header p { font-size: 14px; color: var(--tf-muted); margin: 0; }
    .scan-area {
        background: var(--tf-card); border-radius: 12px; border: 1px solid rgba(255,255,255,0.06);
        padding: 32px; text-align: center; margin-bottom: 24px;
    }
    .camera-box {
        width: 100%; max-width: 500px; height: 300px; margin: 0 auto 20px;
        background: #000; border-radius: 12px; position: relative; overflow: hidden;
        display: flex; align-items: center; justify-content: center;
    }
    .camera-box video { width: 100%; height: 100%; object-fit: cover; }
    .camera-box canvas { display: none; }
    .camera-placeholder { color: var(--tf-muted); font-size: 14px; }
    .scan-crosshair {
        position: absolute; width: 200px; height: 200px; border: 2px solid var(--tf-gold);
        top: 50%; left: 50%; transform: translate(-50%, -50%); border-radius: 12px;
        box-shadow: 0 0 0 9999px rgba(0,0,0,0.4);
    }
    .scan-result {
        background: var(--tf-bg); border-radius: 10px; padding: 20px; margin-top: 20px;
        display: none; text-align: left;
    }
    .scan-result.visible { display: block; }
    .scan-result h3 { font-size: 16px; font-weight: 700; margin: 0 0 12px 0; }
    .scan-result .result-code { font-family: monospace; font-size: 18px; color: var(--tf-gold); margin-bottom: 12px; }
    .scan-actions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 12px; }
    .btn-gold { background: var(--tf-gold); color: #0f172a; border: none; border-radius: 8px; padding: 10px 20px; font-weight: 700; font-size: 14px; cursor: pointer; }
    .btn-gold:hover { opacity: 0.9; }
    .btn-blue { background: var(--tf-blue); color: #fff; border: none; border-radius: 8px; padding: 10px 20px; font-weight: 700; font-size: 14px; cursor: pointer; }
    .btn-blue:hover { opacity: 0.9; }
    .btn-outline { background: transparent; color: var(--tf-muted); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 10px 20px; font-weight: 600; font-size: 14px; cursor: pointer; }
    .btn-outline:hover { border-color: var(--tf-gold); color: var(--tf-gold); }
    .manual-input { display: flex; gap: 10px; max-width: 500px; margin: 0 auto; }
    .manual-input input {
        flex: 1; background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px; padding: 12px 16px; color: var(--tf-text); font-size: 16px; font-family: monospace;
    }
    .manual-input input::placeholder { color: var(--tf-muted); }
    .section-title { font-size: 16px; font-weight: 700; margin: 28px 0 16px 0; }
    .history-card { background: var(--tf-card); border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); overflow: hidden; }
    .data-table { width: 100%; border-collapse: collapse; font-size: 14px; }
    .data-table thead th {
        background: #1a2744; padding: 12px 14px; text-align: left; font-weight: 700;
        font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--tf-muted);
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .data-table tbody td { padding: 10px 14px; border-bottom: 1px solid rgba(255,255,255,0.04); }
    .data-table tbody tr { transition: background 0.15s; cursor: pointer; }
    .data-table tbody tr:hover { background: rgba(255,255,255,0.04); }
    .badge { display: inline-block; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; }
    .badge-green { background: rgba(34,197,94,0.2); color: #4ade80; }
    .badge-blue { background: rgba(59,130,246,0.2); color: #60a5fa; }
    .badge-gold { background: rgba(212,168,67,0.2); color: var(--tf-gold); }
    .empty-state { text-align: center; padding: 40px 20px; color: var(--tf-muted); }
    .empty-state h3 { font-size: 18px; margin-bottom: 8px; color: var(--tf-text); }
    .camera-controls { display: flex; gap: 10px; justify-content: center; margin-bottom: 16px; }

/* ── Responsive ── */
@media (max-width: 768px) {
    .page-header h1 { font-size: 22px; }
    table { display: block; overflow-x: auto; -webkit-overflow-scrolling: touch; }
    .scan-container { padding: 12px; }
    .camera-box { max-width: 100%; }
    .manual-input { flex-direction: column; gap: 8px; }
    .manual-input input { width: 100%; }
}
@media (max-width: 480px) {
    .btn-gold, .btn-blue { width: 100%; text-align: center; }
}
</style>

<div class="scan-container">
    <div class="page-header">
        <h1>Scanner</h1>
        <p>Scan QR codes and barcodes to quickly look up items, update status, or log movements</p>
    </div>

    <div class="scan-area">
        <div class="camera-controls">
            <button class="btn-gold" id="btnStartCam" onclick="startCamera()">Start Camera</button>
            <button class="btn-outline" id="btnStopCam" onclick="stopCamera()" style="display:none;">Stop Camera</button>
        </div>
        <div class="camera-box" id="cameraBox">
            <div class="camera-placeholder" id="camPlaceholder">Camera preview will appear here</div>
            <video id="camVideo" autoplay playsinline style="display:none;"></video>
            <canvas id="camCanvas"></canvas>
            <div class="scan-crosshair" id="crosshair" style="display:none;"></div>
        </div>

        <div style="margin:20px 0 10px;color:var(--tf-muted);font-size:13px;">Or enter code manually:</div>
        <div class="manual-input">
            <input type="text" id="manualCode" placeholder="Enter barcode or QR code..." onkeydown="if(event.key==='Enter')lookupCode()">
            <button class="btn-blue" onclick="lookupCode()">Look Up</button>
        </div>

        <div class="scan-result" id="scanResult">
            <h3>Scan Result</h3>
            <div class="result-code" id="resultCode"></div>
            <div id="resultDetails"></div>
            <div class="scan-actions">
                <button class="btn-blue" onclick="viewItem()">View Item</button>
                <button class="btn-outline" onclick="updateStatus()">Update Status</button>
                <button class="btn-outline" onclick="logMovement()">Log Movement</button>
                <button class="btn-outline" onclick="clearResult()">Clear</button>
            </div>
        </div>
    </div>

    <h3 class="section-title">Scan History</h3>
    <div class="history-card">
        <div id="historyWrap"></div>
    </div>
</div>

<script>
let scanHistory = [];
let cameraStream = null;
let lastScannedCode = '';

async function startCamera() {
    try {
        const video = document.getElementById('camVideo');
        cameraStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
        video.srcObject = cameraStream;
        video.style.display = 'block';
        document.getElementById('camPlaceholder').style.display = 'none';
        document.getElementById('crosshair').style.display = 'block';
        document.getElementById('btnStartCam').style.display = 'none';
        document.getElementById('btnStopCam').style.display = 'inline-block';
        scanLoop();
    } catch(e) {
        alert('Camera not available: ' + e.message);
    }
}

function stopCamera() {
    if (cameraStream) { cameraStream.getTracks().forEach(t => t.stop()); cameraStream = null; }
    document.getElementById('camVideo').style.display = 'none';
    document.getElementById('camPlaceholder').style.display = 'block';
    document.getElementById('crosshair').style.display = 'none';
    document.getElementById('btnStartCam').style.display = 'inline-block';
    document.getElementById('btnStopCam').style.display = 'none';
}

function scanLoop() {
    if (!cameraStream) return;
    // In production, integrate a barcode scanning library (e.g., ZXing, QuaggaJS)
    // For now, placeholder loop
    setTimeout(scanLoop, 1000);
}

function lookupCode() {
    const code = document.getElementById('manualCode').value.trim();
    if (!code) return;
    processCode(code);
}

async function processCode(code) {
    lastScannedCode = code;
    document.getElementById('resultCode').textContent = code;
    const entry = { code: code, timestamp: new Date().toLocaleString(), type: 'manual' };

    try {
        const resp = await fetch('/api/scan/lookup', {
            method: 'POST', headers: {'Content-Type':'application/json'},
            body: JSON.stringify({ code: code })
        });
        const data = await resp.json();
        entry.result = data.item_type || 'Found';
        document.getElementById('resultDetails').innerHTML =
            '<div style="font-size:14px;margin-top:8px;">' +
            (data.item_type ? '<div><strong>Type:</strong> ' + data.item_type + '</div>' : '') +
            (data.project ? '<div><strong>Project:</strong> ' + data.project + '</div>' : '') +
            (data.description ? '<div><strong>Description:</strong> ' + data.description + '</div>' : '') +
            (data.status ? '<div><strong>Status:</strong> ' + data.status + '</div>' : '') +
            (data.location ? '<div><strong>Location:</strong> ' + data.location + '</div>' : '') +
            '</div>';
    } catch(e) {
        entry.result = 'Not found';
        document.getElementById('resultDetails').innerHTML = '<div style="color:var(--tf-muted);font-size:14px;margin-top:8px;">Item not found in system. Code may be external.</div>';
    }

    document.getElementById('scanResult').classList.add('visible');
    scanHistory.unshift(entry);
    renderHistory();
}

function clearResult() {
    document.getElementById('scanResult').classList.remove('visible');
    document.getElementById('manualCode').value = '';
    lastScannedCode = '';
}

function viewItem() {
    if (lastScannedCode) window.location.href = '/scan/item/' + encodeURIComponent(lastScannedCode);
}

async function updateStatus() {
    if (!lastScannedCode) return;
    const newStatus = prompt('Enter new status:');
    if (!newStatus) return;
    try {
        await fetch('/api/scan/update-status', {
            method: 'POST', headers: {'Content-Type':'application/json'},
            body: JSON.stringify({ code: lastScannedCode, status: newStatus })
        });
        alert('Status updated');
    } catch(e) { alert('Error: ' + e.message); }
}

async function logMovement() {
    if (!lastScannedCode) return;
    const location = prompt('Enter new location:');
    if (!location) return;
    try {
        await fetch('/api/scan/log-movement', {
            method: 'POST', headers: {'Content-Type':'application/json'},
            body: JSON.stringify({ code: lastScannedCode, location: location })
        });
        alert('Movement logged');
    } catch(e) { alert('Error: ' + e.message); }
}

function renderHistory() {
    const wrap = document.getElementById('historyWrap');
    if (!scanHistory.length) {
        wrap.innerHTML = '<div class="empty-state"><h3>No scan history</h3><p>Scanned items will appear here.</p></div>';
        return;
    }
    let html = '<table class="data-table"><thead><tr><th>Time</th><th>Code</th><th>Method</th><th>Result</th></tr></thead><tbody>';
    scanHistory.slice(0, 50).forEach(s => {
        html += '<tr onclick="document.getElementById(\'manualCode\').value=\'' + (s.code||'') + '\';lookupCode();">' +
            '<td>' + s.timestamp + '</td>' +
            '<td style="font-family:monospace;color:var(--tf-gold);">' + s.code + '</td>' +
            '<td><span class="badge badge-blue">' + (s.type || 'manual') + '</span></td>' +
            '<td>' + (s.result || '--') + '</td></tr>';
    });
    html += '</tbody></table>';
    wrap.innerHTML = html;
}

// Load saved history
async function loadHistory() {
    try {
        const resp = await fetch('/api/scan/history');
        const data = await resp.json();
        scanHistory = Array.isArray(data) ? data : (data.history || []);
    } catch(e) {}
    renderHistory();
}

loadHistory();
</script>
"""
