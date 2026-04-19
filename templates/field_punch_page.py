"""
TitanForge v4 — Punch List
=============================
Track field installation punch list items.
"""

FIELD_PUNCH_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a;
        --tf-card: #1e293b;
        --tf-text: #e2e8f0;
        --tf-muted: #94a3b8;
        --tf-gold: #d4a843;
        --tf-blue: #3b82f6;
    }
    .punch-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 24px 32px;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
        color: var(--tf-text);
    }
    .page-header { margin-bottom: 32px; }
    .page-header h1 {
        font-size: 28px; font-weight: 800; margin: 0 0 6px 0; color: var(--tf-text);
    }
    .page-header p { font-size: 14px; color: var(--tf-muted); margin: 0; }
    .toolbar {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 20px; flex-wrap: wrap; gap: 12px;
    }
    .project-select {
        background: var(--tf-card);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 8px;
        padding: 10px 16px;
        color: var(--tf-text);
        font-size: 14px;
        min-width: 260px;
    }
    .project-select option { background: var(--tf-card); color: var(--tf-text); }
    .btn-gold {
        background: var(--tf-gold);
        color: #0f172a;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 700;
        font-size: 14px;
        cursor: pointer;
    }
    .btn-gold:hover { opacity: 0.9; }
    .punch-card {
        background: var(--tf-card);
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06);
        padding: 24px;
    }
    .punch-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
    }
    .punch-table thead th {
        background: #1a2744;
        padding: 14px 16px;
        text-align: left;
        font-weight: 700;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--tf-muted);
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .punch-table tbody td {
        padding: 12px 16px;
        border-bottom: 1px solid rgba(255,255,255,0.04);
        color: var(--tf-text);
    }
    .punch-table tbody tr { cursor: pointer; transition: background 0.15s; }
    .punch-table tbody tr:hover { background: rgba(59,130,246,0.06); }
    .punch-table tbody tr.expanded { background: rgba(59,130,246,0.04); }
    .punch-detail-row td { padding: 16px !important; background: rgba(15,23,42,0.5); }
    .punch-detail-content { font-size: 13px; color: var(--tf-muted); line-height: 1.6; }
    .punch-detail-content strong { color: var(--tf-text); }
    .empty-state {
        text-align: center; padding: 60px 20px; color: var(--tf-muted);
    }
    .empty-state h3 { font-size: 18px; margin-bottom: 8px; color: var(--tf-text); }
    .empty-state p { margin-bottom: 20px; }
    .priority-high { color: #f87171; font-weight: 600; }
    .priority-medium { color: var(--tf-gold); font-weight: 600; }
    .priority-low { color: #4ade80; font-weight: 600; }

/* ── Responsive ── */
@media (max-width: 768px) {
    .page-header h1 { font-size: 22px; }
    .toolbar { flex-direction: column; align-items: stretch; }
    .toolbar input[type="text"] { width: 100%; }
    .punch-table { display: block; overflow-x: auto; -webkit-overflow-scrolling: touch; }
    .punch-card { padding: 12px; }
}
@media (max-width: 480px) {
    .toolbar { gap: 8px; }
    .project-select { width: 100%; }
}
</style>

<div class="punch-container">
    <div class="page-header">
        <h1>Punch List</h1>
        <p>Track field installation punch list items</p>
    </div>
    <div class="toolbar">
        <select id="projectSelector" class="project-select" onchange="filterByProject()">
            <option value="">All Projects</option>
        </select>
        <button class="btn-gold" onclick="addItem()">+ Add Item</button>
    </div>
    <div class="punch-card">
        <div id="punchContent">
            <div class="empty-state">
                <h3>No punch list items yet</h3>
                <p>Punch list items will appear here as they are created during field installation.</p>
                <button class="btn-gold" onclick="addItem()">+ Add Item</button>
            </div>
        </div>
    </div>
</div>

<script>
async function loadProjects() {
    try {
        const resp = await fetch('/api/projects');
        const data = await resp.json();
        const projects = Array.isArray(data) ? data : (data.projects || []);
        const sel = document.getElementById('projectSelector');
        projects.forEach(p => {
            const opt = document.createElement('option');
            opt.value = p.id || p.job_code || '';
            opt.textContent = (p.job_code ? p.job_code + ' — ' : '') + (p.project_name || p.name || 'Unnamed');
            sel.appendChild(opt);
        });
    } catch (err) {
        console.error('Failed to load projects:', err);
    }
}

async function filterByProject() {
    const jobCode = document.getElementById('projectSelector').value;
    await loadPunchItems(jobCode);
}

async function loadPunchItems(jobCode) {
    const wrap = document.getElementById('punchContent');
    try {
        let url = '/api/field/punch-items';
        if (jobCode) url += '?job_code=' + encodeURIComponent(jobCode);
        const resp = await fetch(url);
        const data = await resp.json();
        const items = data.items || [];
        if (!items.length) {
            wrap.innerHTML = '<div class="empty-state"><h3>No punch list items</h3><p>Punch list items will appear here as they are created during field installation.</p><button class="btn-gold" onclick="addItem()">+ Add Item</button></div>';
            return;
        }
        let html = '<table class="punch-table"><thead><tr><th>Title</th><th>Priority</th><th>Category</th><th>Location</th><th>Status</th><th>Created</th></tr></thead><tbody>';
        items.forEach((item, idx) => {
            const priClass = item.priority === 'critical' || item.priority === 'high' ? 'priority-high' : item.priority === 'medium' ? 'priority-medium' : 'priority-low';
            html += '<tr onclick="togglePunchRow(this, ' + idx + ')" data-idx="' + idx + '">' +
                '<td><strong>' + (item.title || '—') + '</strong></td>' +
                '<td class="' + priClass + '">' + (item.priority || '—') + '</td>' +
                '<td>' + (item.category_label || item.category || '—') + '</td>' +
                '<td>' + (item.location || '—') + '</td>' +
                '<td>' + (item.status || '—').replace(/_/g, ' ') + '</td>' +
                '<td style="color:var(--tf-muted);font-size:12px">' + (item.created_at ? new Date(item.created_at).toLocaleDateString() : '—') + '</td>' +
                '</tr>';
            html += '<tr class="punch-detail-row" id="punchDetail' + idx + '" style="display:none"><td colspan="6"><div class="punch-detail-content">' +
                '<strong>Description:</strong> ' + (item.description || 'No description') + '<br>' +
                '<strong>Ship Mark:</strong> ' + (item.ship_mark || '—') + ' · ' +
                '<strong>Created By:</strong> ' + (item.created_by || '—') +
                '</div></td></tr>';
        });
        html += '</tbody></table>';
        wrap.innerHTML = html;
    } catch (e) {
        wrap.innerHTML = '<div class="empty-state"><h3>No punch list items yet</h3><p>Punch list items will appear here as they are created during field installation.</p><button class="btn-gold" onclick="addItem()">+ Add Item</button></div>';
    }
}

function togglePunchRow(tr, idx) {
    const detailRow = document.getElementById('punchDetail' + idx);
    if (!detailRow) return;
    const isExpanded = tr.classList.contains('expanded');
    // Collapse all first
    document.querySelectorAll('.punch-table tbody tr.expanded').forEach(r => r.classList.remove('expanded'));
    document.querySelectorAll('.punch-detail-row').forEach(r => r.style.display = 'none');
    if (!isExpanded) {
        tr.classList.add('expanded');
        detailRow.style.display = '';
    }
}

function addItem() {
    // Build modal overlay
    const overlay = document.createElement('div');
    overlay.id = 'punchModal';
    overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.6);display:flex;align-items:center;justify-content:center;z-index:9999;';
    overlay.innerHTML = '<div style="background:#1e293b;border-radius:16px;border:1px solid rgba(255,255,255,0.08);padding:32px;width:540px;max-height:90vh;overflow-y:auto;color:#e2e8f0;font-family:Inter,system-ui,sans-serif;">'
      + '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:24px;">'
      + '<h2 style="margin:0;font-size:20px;font-weight:800;color:#fff;">New Punch List Item</h2>'
      + '<button onclick="closePunchModal()" style="background:none;border:none;color:#94a3b8;font-size:22px;cursor:pointer;">&times;</button></div>'
      + '<form id="punchForm" onsubmit="submitPunchItem(event)">'
      + '<div style="margin-bottom:16px;">'
      + '<label style="display:block;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;color:#94a3b8;margin-bottom:6px;">Title / Description *</label>'
      + '<textarea id="pi_description" required rows="3" style="width:100%;box-sizing:border-box;background:#0f172a;border:1px solid rgba(255,255,255,0.1);border-radius:8px;padding:10px 14px;color:#e2e8f0;font-size:14px;resize:vertical;" placeholder="Describe the punch list item..."></textarea></div>'
      + '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px;">'
      + '<div><label style="display:block;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;color:#94a3b8;margin-bottom:6px;">Location / Area</label>'
      + '<input id="pi_location" type="text" style="width:100%;box-sizing:border-box;background:#0f172a;border:1px solid rgba(255,255,255,0.1);border-radius:8px;padding:10px 14px;color:#e2e8f0;font-size:14px;" placeholder="e.g. Bay 3, North Wall"></div>'
      + '<div><label style="display:block;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;color:#94a3b8;margin-bottom:6px;">Priority *</label>'
      + '<select id="pi_priority" required style="width:100%;box-sizing:border-box;background:#0f172a;border:1px solid rgba(255,255,255,0.1);border-radius:8px;padding:10px 14px;color:#e2e8f0;font-size:14px;">'
      + '<option value="low">Low</option><option value="medium" selected>Medium</option><option value="high">High</option></select></div></div>'
      + '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px;">'
      + '<div><label style="display:block;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;color:#94a3b8;margin-bottom:6px;">Assigned To</label>'
      + '<input id="pi_assigned" type="text" style="width:100%;box-sizing:border-box;background:#0f172a;border:1px solid rgba(255,255,255,0.1);border-radius:8px;padding:10px 14px;color:#e2e8f0;font-size:14px;" placeholder="Name or crew"></div>'
      + '<div><label style="display:block;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;color:#94a3b8;margin-bottom:6px;">Due Date</label>'
      + '<input id="pi_due" type="date" style="width:100%;box-sizing:border-box;background:#0f172a;border:1px solid rgba(255,255,255,0.1);border-radius:8px;padding:10px 14px;color:#e2e8f0;font-size:14px;"></div></div>'
      + '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px;">'
      + '<div><label style="display:block;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;color:#94a3b8;margin-bottom:6px;">Status</label>'
      + '<select id="pi_status" style="width:100%;box-sizing:border-box;background:#0f172a;border:1px solid rgba(255,255,255,0.1);border-radius:8px;padding:10px 14px;color:#e2e8f0;font-size:14px;">'
      + '<option value="open" selected>Open</option><option value="in-progress">In Progress</option><option value="resolved">Resolved</option></select></div>'
      + '<div><label style="display:block;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;color:#94a3b8;margin-bottom:6px;">Photo Reference</label>'
      + '<input id="pi_photo" type="text" style="width:100%;box-sizing:border-box;background:#0f172a;border:1px solid rgba(255,255,255,0.1);border-radius:8px;padding:10px 14px;color:#e2e8f0;font-size:14px;" placeholder="Photo filename or URL (optional)"></div></div>'
      + '<div style="margin-bottom:20px;">'
      + '<label style="display:block;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;color:#94a3b8;margin-bottom:6px;">Project</label>'
      + '<select id="pi_project" style="width:100%;box-sizing:border-box;background:#0f172a;border:1px solid rgba(255,255,255,0.1);border-radius:8px;padding:10px 14px;color:#e2e8f0;font-size:14px;">'
      + '<option value="">-- No project --</option></select></div>'
      + '<div style="display:flex;justify-content:flex-end;gap:12px;">'
      + '<button type="button" onclick="closePunchModal()" style="background:#334155;color:#e2e8f0;border:none;border-radius:8px;padding:10px 20px;font-weight:600;font-size:14px;cursor:pointer;">Cancel</button>'
      + '<button type="submit" id="punchSubmitBtn" style="background:#d4a843;color:#0f172a;border:none;border-radius:8px;padding:10px 24px;font-weight:700;font-size:14px;cursor:pointer;">Save Item</button></div>'
      + '</form></div>';
    document.body.appendChild(overlay);
    // Populate project dropdown from main selector
    var mainSel = document.getElementById('projectSelector');
    var modalSel = document.getElementById('pi_project');
    for (var i = 1; i < mainSel.options.length; i++) {
        var opt = document.createElement('option');
        opt.value = mainSel.options[i].value;
        opt.textContent = mainSel.options[i].textContent;
        modalSel.appendChild(opt);
    }
    if (mainSel.value) modalSel.value = mainSel.value;
    overlay.addEventListener('click', function(e) { if (e.target === overlay) closePunchModal(); });
}

function closePunchModal() {
    var m = document.getElementById('punchModal');
    if (m) m.remove();
}

async function submitPunchItem(e) {
    e.preventDefault();
    var btn = document.getElementById('punchSubmitBtn');
    btn.disabled = true;
    btn.textContent = 'Saving...';
    var payload = {
        title: document.getElementById('pi_description').value.split('\n')[0].substring(0, 120),
        description: document.getElementById('pi_description').value,
        location: document.getElementById('pi_location').value,
        priority: document.getElementById('pi_priority').value,
        assigned_to: document.getElementById('pi_assigned').value,
        due_date: document.getElementById('pi_due').value,
        status: document.getElementById('pi_status').value,
        photo_ref: document.getElementById('pi_photo').value,
        job_code: document.getElementById('pi_project').value
    };
    try {
        var resp = await fetch('/api/field/punch-items', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        var data = await resp.json();
        if (data.status === 'ok') {
            closePunchModal();
            await loadPunchItems(document.getElementById('projectSelector').value);
        } else {
            alert('Error: ' + (data.error || 'Unknown error'));
            btn.disabled = false;
            btn.textContent = 'Save Item';
        }
    } catch (err) {
        alert('Failed to save: ' + err.message);
        btn.disabled = false;
        btn.textContent = 'Save Item';
    }
}

loadProjects();
loadPunchItems('');
</script>
"""
