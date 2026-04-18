"""
TitanForge v4 — Audit Trail
==============================
System activity log, user actions, data changes, filterable and exportable.
"""

AUDIT_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a;
        --tf-card: #1e293b;
        --tf-text: #e2e8f0;
        --tf-muted: #94a3b8;
        --tf-gold: #d4a843;
        --tf-blue: #3b82f6;
    }
    .audit-container {
        max-width: 1400px; margin: 0 auto; padding: 24px 32px;
        font-family: 'Inter', 'Segoe UI', sans-serif; color: var(--tf-text);
    }
    .page-header { margin-bottom: 32px; }
    .page-header h1 { font-size: 28px; font-weight: 800; margin: 0 0 6px 0; }
    .page-header p { font-size: 14px; color: var(--tf-muted); margin: 0; }
    .toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
    .toolbar input[type="text"], .toolbar input[type="date"] { background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px 16px; color: var(--tf-text); font-size: 14px; }
    .toolbar input::placeholder { color: var(--tf-muted); }
    .toolbar select { background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px; }
    .btn-gold { background: var(--tf-gold); color: #0f172a; border: none; border-radius: 8px; padding: 10px 20px; font-weight: 700; font-size: 14px; cursor: pointer; }
    .btn-gold:hover { opacity: 0.9; }
    .btn-outline { background: transparent; color: var(--tf-muted); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 10px 20px; font-weight: 600; font-size: 14px; cursor: pointer; }
    .btn-outline:hover { border-color: var(--tf-gold); color: var(--tf-gold); }
    .stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
    @media (max-width: 900px) { .stats-row { grid-template-columns: 1fr 1fr; } }
    .stat-card { background: var(--tf-card); border-radius: 10px; padding: 18px; border: 1px solid rgba(255,255,255,0.06); }
    .stat-card .stat-label { font-size: 12px; color: var(--tf-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
    .stat-card .stat-value { font-size: 24px; font-weight: 800; }
    .data-card { background: var(--tf-card); border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); overflow: hidden; }
    .data-table { width: 100%; border-collapse: collapse; font-size: 14px; }
    .data-table thead th {
        background: #1a2744; padding: 14px 16px; text-align: left; font-weight: 700;
        font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--tf-muted);
        border-bottom: 1px solid rgba(255,255,255,0.06); cursor: pointer;
    }
    .data-table thead th:hover { color: var(--tf-text); }
    .data-table tbody td { padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.04); }
    .data-table tbody tr { transition: background 0.15s; cursor: pointer; }
    .data-table tbody tr:hover { background: rgba(255,255,255,0.04); }
    .action-badge { display: inline-block; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; }
    .action-create { background: rgba(34,197,94,0.2); color: #4ade80; }
    .action-update { background: rgba(59,130,246,0.2); color: #60a5fa; }
    .action-delete { background: rgba(239,68,68,0.2); color: #f87171; }
    .action-login { background: rgba(212,168,67,0.2); color: var(--tf-gold); }
    .action-view { background: rgba(148,163,184,0.2); color: #94a3b8; }
    .pagination { display: flex; justify-content: center; align-items: center; gap: 8px; padding: 16px; }
    .pagination button { background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08); border-radius: 6px; padding: 8px 14px; color: var(--tf-text); cursor: pointer; font-size: 13px; }
    .pagination button:hover { border-color: var(--tf-blue); }
    .pagination button.active { background: var(--tf-blue); border-color: var(--tf-blue); font-weight: 700; }
    .pagination span { color: var(--tf-muted); font-size: 13px; }
    .empty-state { text-align: center; padding: 60px 20px; color: var(--tf-muted); }
    .empty-state h3 { font-size: 18px; margin-bottom: 8px; color: var(--tf-text); }
    .loading { text-align: center; padding: 40px; color: var(--tf-muted); }
    .modal-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 1000; justify-content: center; align-items: center; }
    .modal-overlay.active { display: flex; }
    .modal { background: var(--tf-card); border-radius: 12px; padding: 28px; width: 600px; max-width: 90vw; border: 1px solid rgba(255,255,255,0.1); max-height: 80vh; overflow-y: auto; }
    .modal h2 { font-size: 20px; margin: 0 0 20px 0; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 24px; }
    .detail-row { display: flex; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.04); font-size: 14px; }
    .detail-label { width: 120px; color: var(--tf-muted); font-weight: 600; flex-shrink: 0; }
    .detail-value { flex: 1; }
    .diff-block { background: var(--tf-bg); border-radius: 8px; padding: 12px; font-family: monospace; font-size: 12px; margin-top: 12px; white-space: pre-wrap; max-height: 200px; overflow-y: auto; }
    .diff-add { color: #4ade80; }
    .diff-remove { color: #f87171; }
</style>

<div class="audit-container">
    <div class="page-header">
        <h1>Audit Trail</h1>
        <p>Complete log of system activity, user actions, and data changes</p>
    </div>
    <div class="stats-row">
        <div class="stat-card"><div class="stat-label">Today's Events</div><div class="stat-value" id="statToday" style="color:var(--tf-blue);">--</div></div>
        <div class="stat-card"><div class="stat-label">Active Users</div><div class="stat-value" id="statUsers" style="color:var(--tf-gold);">--</div></div>
        <div class="stat-card"><div class="stat-label">Data Changes</div><div class="stat-value" id="statChanges" style="color:#4ade80;">--</div></div>
        <div class="stat-card"><div class="stat-label">Alerts</div><div class="stat-value" id="statAlerts" style="color:#f87171;">--</div></div>
    </div>
    <div class="toolbar">
        <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
            <input type="text" id="auditSearch" placeholder="Search actions, users, resources..." oninput="filterAudit()" style="width:260px;">
            <select id="filterAction" onchange="filterAudit()">
                <option value="">All Actions</option>
                <option value="create">Create</option>
                <option value="update">Update</option>
                <option value="delete">Delete</option>
                <option value="login">Login</option>
                <option value="view">View</option>
            </select>
            <select id="filterUser" onchange="filterAudit()"><option value="">All Users</option></select>
            <input type="date" id="filterDateFrom" onchange="filterAudit()">
            <input type="date" id="filterDateTo" onchange="filterAudit()">
        </div>
        <button class="btn-outline" onclick="exportAudit()">Export CSV</button>
    </div>
    <div class="data-card">
        <div id="auditTableWrap" class="loading">Loading audit log...</div>
    </div>
    <div class="pagination" id="pagination"></div>
</div>

<div class="modal-overlay" id="detailModal">
    <div class="modal">
        <h2>Event Details</h2>
        <div id="detailContent"></div>
        <div class="modal-actions"><button class="btn-outline" onclick="closeModal('detailModal')">Close</button></div>
    </div>
</div>

<script>
let allEntries = [];
let currentPage = 1;
const perPage = 50;

function openModal(id) { document.getElementById(id).classList.add('active'); }
function closeModal(id) { document.getElementById(id).classList.remove('active'); }
document.querySelectorAll('.modal-overlay').forEach(m => m.addEventListener('click', function(e) { if (e.target === this) closeModal(this.id); }));

function getActionClass(action) {
    if (!action) return 'action-view';
    const a = action.toLowerCase();
    if (a.includes('create') || a.includes('add')) return 'action-create';
    if (a.includes('update') || a.includes('edit') || a.includes('change')) return 'action-update';
    if (a.includes('delete') || a.includes('remove')) return 'action-delete';
    if (a.includes('login') || a.includes('auth')) return 'action-login';
    return 'action-view';
}

function renderTable(entries) {
    const wrap = document.getElementById('auditTableWrap');
    if (!entries.length) {
        wrap.innerHTML = '<div class="empty-state"><h3>No audit entries</h3><p>System activity will appear here automatically.</p></div>';
        renderPagination(0); return;
    }
    const start = (currentPage - 1) * perPage;
    const page = entries.slice(start, start + perPage);
    let html = '<table class="data-table"><thead><tr><th>Timestamp</th><th>User</th><th>Action</th><th>Resource</th><th>Details</th></tr></thead><tbody>';
    page.forEach((e, i) => {
        html += '<tr onclick="showDetail(' + (start + i) + ')">' +
            '<td style="white-space:nowrap;">' + (e.timestamp || '--') + '</td>' +
            '<td>' + (e.user || '--') + '</td>' +
            '<td><span class="action-badge ' + getActionClass(e.action) + '">' + (e.action || '--') + '</span></td>' +
            '<td>' + (e.resource || '--') + '</td>' +
            '<td style="color:var(--tf-muted);max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">' + (e.details || '--') + '</td></tr>';
    });
    html += '</tbody></table>';
    wrap.innerHTML = html;
    renderPagination(entries.length);
}

function renderPagination(total) {
    const pages = Math.ceil(total / perPage);
    const el = document.getElementById('pagination');
    if (pages <= 1) { el.innerHTML = ''; return; }
    let html = '<button onclick="goPage(' + Math.max(1, currentPage-1) + ')">&laquo;</button>';
    for (let i = 1; i <= Math.min(pages, 7); i++) {
        html += '<button class="' + (i === currentPage ? 'active' : '') + '" onclick="goPage(' + i + ')">' + i + '</button>';
    }
    if (pages > 7) html += '<span>...</span><button onclick="goPage(' + pages + ')">' + pages + '</button>';
    html += '<button onclick="goPage(' + Math.min(pages, currentPage+1) + ')">&raquo;</button>';
    el.innerHTML = html;
}

function goPage(p) { currentPage = p; filterAudit(); }

function showDetail(idx) {
    const e = allEntries[idx];
    if (!e) return;
    let html = '<div class="detail-row"><div class="detail-label">Timestamp</div><div class="detail-value">' + (e.timestamp || '--') + '</div></div>' +
        '<div class="detail-row"><div class="detail-label">User</div><div class="detail-value">' + (e.user || '--') + '</div></div>' +
        '<div class="detail-row"><div class="detail-label">Action</div><div class="detail-value"><span class="action-badge ' + getActionClass(e.action) + '">' + (e.action || '--') + '</span></div></div>' +
        '<div class="detail-row"><div class="detail-label">Resource</div><div class="detail-value">' + (e.resource || '--') + '</div></div>' +
        '<div class="detail-row"><div class="detail-label">IP Address</div><div class="detail-value">' + (e.ip || '--') + '</div></div>' +
        '<div class="detail-row"><div class="detail-label">Details</div><div class="detail-value">' + (e.details || '--') + '</div></div>';
    if (e.changes) {
        html += '<div class="diff-block">';
        if (typeof e.changes === 'object') {
            Object.keys(e.changes).forEach(k => {
                const c = e.changes[k];
                html += '<div><span class="diff-remove">- ' + k + ': ' + (c.old || '') + '</span></div>';
                html += '<div><span class="diff-add">+ ' + k + ': ' + (c.new || '') + '</span></div>';
            });
        } else { html += e.changes; }
        html += '</div>';
    }
    document.getElementById('detailContent').innerHTML = html;
    openModal('detailModal');
}

function filterAudit() {
    const search = document.getElementById('auditSearch').value.toLowerCase();
    const action = document.getElementById('filterAction').value;
    const user = document.getElementById('filterUser').value;
    const from = document.getElementById('filterDateFrom').value;
    const to = document.getElementById('filterDateTo').value;
    const filtered = allEntries.filter(e => {
        if (search && !(e.user||'').toLowerCase().includes(search) && !(e.action||'').toLowerCase().includes(search) && !(e.resource||'').toLowerCase().includes(search) && !(e.details||'').toLowerCase().includes(search)) return false;
        if (action && !(e.action||'').toLowerCase().includes(action)) return false;
        if (user && e.user !== user) return false;
        if (from && (e.timestamp||'') < from) return false;
        if (to && (e.timestamp||'').slice(0,10) > to) return false;
        return true;
    });
    renderTable(filtered);
}

function exportAudit() {
    const rows = [['Timestamp','User','Action','Resource','Details']];
    allEntries.forEach(e => rows.push([e.timestamp||'',e.user||'',e.action||'',e.resource||'',e.details||'']));
    const csv = rows.map(r => r.map(c => '"' + (c||'').replace(/"/g,'""') + '"').join(',')).join('\n');
    const blob = new Blob([csv], {type:'text/csv'});
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'audit_trail.csv'; a.click();
}

async function loadAudit() {
    try {
        const resp = await fetch('/api/audit');
        const data = await resp.json();
        allEntries = Array.isArray(data) ? data : (data.entries || []);
        const users = [...new Set(allEntries.map(e => e.user).filter(Boolean))];
        const sel = document.getElementById('filterUser');
        users.forEach(u => { const o = document.createElement('option'); o.value = u; o.textContent = u; sel.appendChild(o); });
        const today = new Date().toISOString().slice(0,10);
        document.getElementById('statToday').textContent = allEntries.filter(e => (e.timestamp||'').startsWith(today)).length;
        document.getElementById('statUsers').textContent = users.length;
        document.getElementById('statChanges').textContent = allEntries.filter(e => ['create','update','delete'].some(a => (e.action||'').toLowerCase().includes(a))).length;
        document.getElementById('statAlerts').textContent = allEntries.filter(e => e.alert).length;
        renderTable(allEntries);
    } catch(e) { renderTable([]); }
}

loadAudit();
</script>
"""
