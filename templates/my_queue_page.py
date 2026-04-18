"""
TitanForge — My Queue Page
===========================
Shows work items assigned to the current user across all jobs.
Sections: In Progress, Up Next, Recently Completed.
"""

MY_QUEUE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Queue — TitanForge</title>
    <style>
        :root {
            --tf-navy: #0F172A;
            --tf-card: #1E293B;
            --tf-border: #334155;
            --tf-blue: #3B82F6;
            --tf-green: #22C55E;
            --tf-amber: #F59E0B;
            --tf-red: #EF4444;
            --tf-gray-300: #CBD5E1;
            --tf-gray-400: #94A3B8;
            --tf-gray-500: #64748B;
            --tf-gray-800: #1E293B;
            --tf-font: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: var(--tf-font);
            background: var(--tf-navy);
            color: #E2E8F0;
            min-height: 100vh;
        }
        .mq-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 24px;
        }
        .mq-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 24px;
        }
        .mq-header h1 {
            font-size: 1.6rem;
            font-weight: 700;
            color: #F8FAFC;
        }
        .mq-header h1 span { color: var(--tf-amber); }
        .mq-stats {
            display: flex;
            gap: 12px;
        }
        .mq-stat {
            background: var(--tf-card);
            border: 1px solid var(--tf-border);
            border-radius: 10px;
            padding: 10px 18px;
            text-align: center;
        }
        .mq-stat-val {
            font-size: 1.4rem;
            font-weight: 800;
        }
        .mq-stat-label {
            font-size: 0.7rem;
            color: var(--tf-gray-400);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .mq-section {
            margin-bottom: 28px;
        }
        .mq-section-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid var(--tf-border);
        }
        .mq-section-icon {
            font-size: 1.2rem;
        }
        .mq-section-title {
            font-size: 1.05rem;
            font-weight: 700;
            color: #F8FAFC;
        }
        .mq-section-count {
            background: rgba(255,255,255,0.08);
            color: var(--tf-gray-400);
            font-size: 0.75rem;
            font-weight: 600;
            padding: 2px 10px;
            border-radius: 10px;
        }
        .mq-empty {
            text-align: center;
            color: var(--tf-gray-500);
            padding: 32px;
            font-size: 0.9rem;
        }
        .mq-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 12px;
        }
        .mq-card {
            background: var(--tf-card);
            border: 1px solid var(--tf-border);
            border-radius: 10px;
            padding: 16px;
            transition: border-color 0.15s, box-shadow 0.15s;
        }
        .mq-card:hover {
            border-color: var(--tf-blue);
            box-shadow: 0 2px 12px rgba(59,130,246,0.12);
        }
        .mq-card-top {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            margin-bottom: 8px;
        }
        .mq-card-mark {
            font-size: 1.1rem;
            font-weight: 800;
            color: var(--tf-amber);
        }
        .mq-card-status {
            font-size: 0.7rem;
            font-weight: 600;
            padding: 2px 10px;
            border-radius: 10px;
            text-transform: uppercase;
        }
        .status-in_progress { background: rgba(59,130,246,0.15); color: #60A5FA; }
        .status-queued { background: rgba(148,163,184,0.15); color: #94A3B8; }
        .status-complete { background: rgba(34,197,94,0.15); color: #4ADE80; }
        .mq-card-desc {
            font-size: 0.85rem;
            color: #CBD5E1;
            margin-bottom: 8px;
            line-height: 1.4;
        }
        .mq-card-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            font-size: 0.75rem;
            color: var(--tf-gray-500);
            margin-bottom: 10px;
        }
        .mq-card-meta span {
            display: flex;
            align-items: center;
            gap: 4px;
        }
        .mq-card-actions {
            display: flex;
            gap: 6px;
            margin-top: 8px;
            padding-top: 10px;
            border-top: 1px solid var(--tf-border);
        }
        .mq-btn {
            padding: 6px 14px;
            border-radius: 6px;
            font-size: 0.78rem;
            font-weight: 600;
            border: none;
            cursor: pointer;
            transition: all 0.15s;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }
        .mq-btn-primary {
            background: var(--tf-blue);
            color: #fff;
        }
        .mq-btn-primary:hover { background: #2563EB; }
        .mq-btn-success {
            background: var(--tf-green);
            color: #fff;
        }
        .mq-btn-success:hover { background: #16A34A; }
        .mq-btn-ghost {
            background: rgba(255,255,255,0.06);
            color: var(--tf-gray-400);
            border: 1px solid var(--tf-border);
        }
        .mq-btn-ghost:hover { background: rgba(255,255,255,0.1); color: #E2E8F0; }
        .mq-loading {
            text-align: center;
            padding: 60px;
            color: var(--tf-gray-500);
        }
        .mq-loading .spinner {
            display: inline-block;
            width: 32px;
            height: 32px;
            border: 3px solid var(--tf-border);
            border-top-color: var(--tf-blue);
            border-radius: 50%;
            animation: mqSpin 0.7s linear infinite;
            margin-bottom: 12px;
        }
        @keyframes mqSpin { to { transform: rotate(360deg); } }
        @media (max-width: 600px) {
            .mq-grid { grid-template-columns: 1fr; }
            .mq-header { flex-direction: column; gap: 12px; align-items: flex-start; }
            .mq-stats { flex-wrap: wrap; }
        }
    </style>
</head>
<body>
<div class="mq-container">
    <div class="mq-header">
        <h1>&#128190; My <span>Queue</span></h1>
        <div class="mq-stats">
            <div class="mq-stat">
                <div class="mq-stat-val" id="statActive" style="color:#60A5FA;">-</div>
                <div class="mq-stat-label">Active</div>
            </div>
            <div class="mq-stat">
                <div class="mq-stat-val" id="statQueued" style="color:#F59E0B;">-</div>
                <div class="mq-stat-label">Up Next</div>
            </div>
            <div class="mq-stat">
                <div class="mq-stat-val" id="statDone" style="color:#4ADE80;">-</div>
                <div class="mq-stat-label">Done (7d)</div>
            </div>
        </div>
    </div>

    <div id="mqContent">
        <div class="mq-loading">
            <div class="spinner"></div>
            <div>Loading your work queue...</div>
        </div>
    </div>
</div>

<script>
(function(){
    async function loadQueue() {
        try {
            const resp = await fetch('/api/my-queue');
            const data = await resp.json();
            if (!data.ok) throw new Error(data.error || 'Failed to load');
            renderQueue(data);
        } catch(e) {
            document.getElementById('mqContent').innerHTML =
                '<div class="mq-empty">Failed to load queue: ' + escHtml(e.message) + '</div>';
        }
    }

    function renderQueue(data) {
        const inProgress = data.in_progress || [];
        const upNext = data.up_next || [];
        const completed = data.recently_completed || [];

        document.getElementById('statActive').textContent = inProgress.length;
        document.getElementById('statQueued').textContent = upNext.length;
        document.getElementById('statDone').textContent = completed.length;

        let html = '';

        // In Progress
        html += renderSection('&#9881;', 'In Progress', inProgress, 'in_progress');
        // Up Next
        html += renderSection('&#128205;', 'Up Next', upNext, 'queued');
        // Recently Completed
        html += renderSection('&#9989;', 'Recently Completed', completed, 'complete');

        document.getElementById('mqContent').innerHTML = html;
    }

    function renderSection(icon, title, items, statusClass) {
        let html = '<div class="mq-section">';
        html += '<div class="mq-section-header">';
        html += '<span class="mq-section-icon">' + icon + '</span>';
        html += '<span class="mq-section-title">' + title + '</span>';
        html += '<span class="mq-section-count">' + items.length + '</span>';
        html += '</div>';

        if (items.length === 0) {
            html += '<div class="mq-empty">No items in this section</div>';
        } else {
            html += '<div class="mq-grid">';
            for (const item of items) {
                html += renderCard(item, statusClass);
            }
            html += '</div>';
        }
        html += '</div>';
        return html;
    }

    function renderCard(item, statusClass) {
        const sc = item.status || statusClass;
        const estMin = item.estimated_minutes ? (Math.round(item.estimated_minutes) + ' min est') : '';
        const jobCode = item.job_code || '';
        const woId = item.work_order_id || '';

        let html = '<div class="mq-card">';
        html += '<div class="mq-card-top">';
        html += '<span class="mq-card-mark">' + escHtml(item.ship_mark || item.item_id || 'Item') + '</span>';
        html += '<span class="mq-card-status status-' + sc + '">' + sc.replace(/_/g, ' ') + '</span>';
        html += '</div>';

        html += '<div class="mq-card-desc">' + escHtml(item.description || item.component_type || '') + '</div>';

        html += '<div class="mq-card-meta">';
        if (jobCode) html += '<span>&#128194; ' + escHtml(jobCode) + '</span>';
        if (woId) html += '<span>&#128203; ' + escHtml(woId.substring(0,8)) + '</span>';
        if (item.machine) html += '<span>&#9881; ' + escHtml(item.machine) + '</span>';
        if (estMin) html += '<span>&#9201; ' + estMin + '</span>';
        if (item.quantity > 1) html += '<span>&#215; ' + item.quantity + '</span>';
        html += '</div>';

        html += '<div class="mq-card-actions">';
        if (sc === 'queued') {
            html += '<button class="mq-btn mq-btn-primary" onclick="startItem(\\x27' + escAttr(jobCode) + '\\x27,\\x27' + escAttr(woId) + '\\x27,\\x27' + escAttr(item.item_id) + '\\x27)">&#9654; Start</button>';
        }
        if (sc === 'in_progress') {
            html += '<button class="mq-btn mq-btn-success" onclick="completeItem(\\x27' + escAttr(jobCode) + '\\x27,\\x27' + escAttr(woId) + '\\x27,\\x27' + escAttr(item.item_id) + '\\x27)">&#10003; Complete</button>';
        }
        if (jobCode && item.drawing_ref) {
            html += '<a class="mq-btn mq-btn-ghost" href="/shop-drawings/' + encodeURIComponent(jobCode) + '" target="_blank">&#128208; Drawing</a>';
        }
        if (jobCode) {
            html += '<a class="mq-btn mq-btn-ghost" href="/work-station/' + encodeURIComponent(jobCode) + '" target="_blank">&#128241; Station</a>';
        }
        html += '</div>';
        html += '</div>';
        return html;
    }

    window.startItem = async function(jobCode, woId, itemId) {
        try {
            const resp = await fetch('/api/work-station/scan', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({job_code: jobCode, work_order_id: woId, item_id: itemId, action: 'start'})
            });
            const data = await resp.json();
            if (data.ok) {
                loadQueue();
                if (window.showXPToast && data.xp) window.showXPToast(data.xp, 'start_item', false, []);
            } else {
                alert('Failed: ' + (data.error || 'Unknown error'));
            }
        } catch(e) { alert('Error: ' + e.message); }
    };

    window.completeItem = async function(jobCode, woId, itemId) {
        try {
            const resp = await fetch('/api/work-station/scan', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({job_code: jobCode, work_order_id: woId, item_id: itemId, action: 'finish'})
            });
            const data = await resp.json();
            if (data.ok) {
                loadQueue();
                if (window.showXPToast && data.xp) window.showXPToast(data.xp, 'complete_item', false, []);
            } else {
                alert('Failed: ' + (data.error || 'Unknown error'));
            }
        } catch(e) { alert('Error: ' + e.message); }
    };

    function escHtml(s) {
        const d = document.createElement('div');
        d.textContent = s || '';
        return d.innerHTML;
    }
    function escAttr(s) {
        return (s || '').replace(/'/g, "\\\\'").replace(/"/g, '&quot;');
    }

    loadQueue();
    // Auto-refresh every 30 seconds
    setInterval(loadQueue, 30000);
})();
</script>
</body>
</html>
"""
