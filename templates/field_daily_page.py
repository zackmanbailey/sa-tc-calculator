"""
TitanForge v4 -- Field Daily Reports
======================================
Daily field reports: weather, crew, work performed, hours, safety notes, photos.
"""

FIELD_DAILY_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a;
        --tf-card: #1e293b;
        --tf-text: #e2e8f0;
        --tf-muted: #94a3b8;
        --tf-gold: #d4a843;
        --tf-blue: #3b82f6;
        --tf-green: #10b981;
        --tf-red: #ef4444;
        --tf-orange: #f59e0b;
    }
    .daily-container {
        max-width: 1400px; margin: 0 auto; padding: 24px 32px;
        font-family: 'Inter', 'Segoe UI', sans-serif; color: var(--tf-text);
    }
    .page-header { margin-bottom: 28px; }
    .page-header h1 { font-size: 28px; font-weight: 800; margin: 0 0 6px 0; }
    .page-header p { font-size: 14px; color: var(--tf-muted); margin: 0; }

    .stat-row {
        display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px; margin-bottom: 24px;
    }
    .stat-card {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06);
        padding: 20px 24px; cursor: pointer; transition: border-color 0.2s, transform 0.15s;
    }
    .stat-card:hover { border-color: var(--tf-gold); transform: translateY(-2px); }
    .stat-card .label { font-size: 12px; color: var(--tf-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
    .stat-card .value { font-size: 28px; font-weight: 800; }
    .stat-gold .value { color: var(--tf-gold); }
    .stat-blue .value { color: var(--tf-blue); }
    .stat-green .value { color: var(--tf-green); }
    .stat-red .value { color: var(--tf-red); }

    .toolbar {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 20px; flex-wrap: wrap; gap: 12px;
    }
    .toolbar-left { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
    .toolbar input[type="text"], .toolbar input[type="date"], .toolbar select {
        background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06);
        border-radius: 8px; padding: 10px 16px; color: var(--tf-text); font-size: 14px;
    }
    .toolbar input:focus, .toolbar select:focus { outline: none; border-color: var(--tf-blue); }
    .btn {
        padding: 10px 20px; border: none; border-radius: 8px; font-size: 14px;
        font-weight: 600; cursor: pointer; transition: all 0.2s;
    }
    .btn-primary { background: var(--tf-gold); color: #0f172a; }
    .btn-primary:hover { background: #e0b44e; transform: translateY(-1px); }
    .btn-secondary { background: var(--tf-card); color: var(--tf-text); border: 1px solid rgba(255,255,255,0.06); }
    .btn-secondary:hover { border-color: var(--tf-blue); }
    .btn-sm { padding: 6px 14px; font-size: 12px; }
    .btn-danger { background: var(--tf-red); color: #fff; }

    .data-table {
        width: 100%; border-collapse: collapse; background: var(--tf-card);
        border-radius: 12px; overflow: hidden; border: 1px solid rgba(255,255,255,0.06);
    }
    .data-table th {
        padding: 14px 16px; text-align: left; font-size: 11px; font-weight: 700;
        color: var(--tf-muted); text-transform: uppercase; letter-spacing: 0.5px;
        background: rgba(0,0,0,0.2); border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .data-table td {
        padding: 14px 16px; font-size: 14px; border-bottom: 1px solid rgba(255,255,255,0.04);
    }
    .data-table tbody tr { cursor: pointer; transition: background 0.15s; }
    .data-table tbody tr:hover { background: rgba(59,130,246,0.06); }

    .badge {
        display: inline-block; padding: 4px 10px; border-radius: 6px;
        font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.3px;
    }
    .badge-submitted { background: rgba(16,185,129,0.15); color: var(--tf-green); }
    .badge-draft { background: rgba(245,158,11,0.15); color: var(--tf-orange); }
    .badge-approved { background: rgba(59,130,246,0.15); color: var(--tf-blue); }

    .empty-state {
        text-align: center; padding: 60px 20px; color: var(--tf-muted);
    }
    .empty-state .icon { font-size: 48px; margin-bottom: 16px; opacity: 0.5; }
    .empty-state h3 { font-size: 18px; color: var(--tf-text); margin-bottom: 8px; }
    .empty-state p { font-size: 14px; max-width: 400px; margin: 0 auto 20px; }

    .weather-icons { display: flex; gap: 8px; align-items: center; }
    .weather-badge {
        display: inline-flex; align-items: center; gap: 4px;
        padding: 4px 10px; border-radius: 6px; font-size: 12px;
        background: rgba(59,130,246,0.1); color: var(--tf-blue);
    }

    /* Modal */
    .modal-overlay {
        display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6);
        z-index: 1000; align-items: center; justify-content: center;
    }
    .modal-overlay.active { display: flex; }
    .modal {
        background: var(--tf-card); border-radius: 16px; padding: 32px;
        width: 90%; max-width: 700px; max-height: 90vh; overflow-y: auto;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .modal h2 { font-size: 22px; font-weight: 800; margin: 0 0 24px 0; }
    .modal-close {
        float: right; background: none; border: none; color: var(--tf-muted);
        font-size: 24px; cursor: pointer;
    }
    .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .form-group { margin-bottom: 16px; }
    .form-group label { display: block; font-size: 13px; font-weight: 600; color: var(--tf-muted); margin-bottom: 6px; }
    .form-group input, .form-group select, .form-group textarea {
        width: 100%; background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px;
    }
    .form-group textarea { min-height: 80px; resize: vertical; }
    .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
        outline: none; border-color: var(--tf-blue);
    }
    .form-full { grid-column: 1 / -1; }
    .modal-actions { display: flex; gap: 10px; justify-content: flex-end; margin-top: 24px; }

/* ── Responsive ── */
@media (max-width: 768px) {
    .page-header h1 { font-size: 22px; }
    .toolbar { flex-direction: column; align-items: stretch; }
    .toolbar input[type="text"] { width: 100%; }
    .stat-row { grid-template-columns: 1fr 1fr; gap: 10px; }
    table { display: block; overflow-x: auto; -webkit-overflow-scrolling: touch; }
    .modal-overlay .modal, .modal { width: 95%; max-width: 95vw; margin: 20px auto; padding: 20px; }
    .form-grid { grid-template-columns: 1fr; }
}
@media (max-width: 480px) {
    .stat-row { grid-template-columns: 1fr; }
    .toolbar { gap: 8px; }
}
</style>

<div class="daily-container">
    <div class="page-header">
        <h1>Daily Field Reports</h1>
        <p>Document daily field activities, weather conditions, crew hours, and safety observations</p>
    </div>

    <div class="stat-row">
        <div class="stat-card stat-gold" onclick="filterReports('all')">
            <div class="label">Total Reports</div>
            <div class="value" id="stat-total">0</div>
        </div>
        <div class="stat-card stat-blue" onclick="filterReports('this-week')">
            <div class="label">This Week</div>
            <div class="value" id="stat-week">0</div>
        </div>
        <div class="stat-card stat-green" onclick="filterReports('submitted')">
            <div class="label">Submitted</div>
            <div class="value" id="stat-submitted">0</div>
        </div>
        <div class="stat-card stat-red" onclick="filterReports('draft')">
            <div class="label">Drafts</div>
            <div class="value" id="stat-drafts">0</div>
        </div>
    </div>

    <div class="toolbar">
        <div class="toolbar-left">
            <input type="text" id="searchInput" placeholder="Search reports..." oninput="filterTable()">
            <input type="date" id="filterDate" onchange="filterTable()">
            <select id="filterProject" onchange="filterTable()">
                <option value="">All Projects</option>
            </select>
            <select id="filterStatus" onchange="filterTable()">
                <option value="">All Status</option>
                <option value="draft">Draft</option>
                <option value="submitted">Submitted</option>
                <option value="approved">Approved</option>
            </select>
        </div>
        <button class="btn btn-primary" onclick="openNewReport()">+ New Daily Report</button>
    </div>

    <table class="data-table">
        <thead>
            <tr>
                <th>Date</th>
                <th>Project</th>
                <th>Superintendent</th>
                <th>Weather</th>
                <th>Crew Size</th>
                <th>Hours</th>
                <th>Safety Notes</th>
                <th>Status</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody id="reportsTable">
        </tbody>
    </table>

    <div class="empty-state" id="emptyState">
        <div class="icon">&#128221;</div>
        <h3>No Daily Reports Yet</h3>
        <p>Start documenting daily field activities by creating your first daily report.</p>
        <button class="btn btn-primary" onclick="openNewReport()">+ Create First Report</button>
    </div>
</div>

<!-- New Daily Report Modal -->
<div class="modal-overlay" id="reportModal">
    <div class="modal">
        <button class="modal-close" onclick="closeModal('reportModal')">&times;</button>
        <h2 id="modalTitle">New Daily Report</h2>
        <form id="reportForm" onsubmit="saveReport(event)">
            <div class="form-grid">
                <div class="form-group">
                    <label>Report Date</label>
                    <input type="date" id="reportDate" required>
                </div>
                <div class="form-group">
                    <label>Project</label>
                    <select id="reportProject" required>
                        <option value="">Select Project</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Weather Condition</label>
                    <select id="reportWeather" required>
                        <option value="">Select</option>
                        <option value="clear">Clear / Sunny</option>
                        <option value="cloudy">Cloudy</option>
                        <option value="rain">Rain</option>
                        <option value="snow">Snow</option>
                        <option value="wind">High Wind</option>
                        <option value="storm">Storm</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Temperature (F)</label>
                    <input type="text" id="reportTemp" placeholder="e.g. 85">
                </div>
                <div class="form-group">
                    <label>Crew on Site</label>
                    <input type="number" id="reportCrew" min="0" placeholder="Number of crew">
                </div>
                <div class="form-group">
                    <label>Total Hours Logged</label>
                    <input type="number" id="reportHours" min="0" step="0.5" placeholder="Total man-hours">
                </div>
                <div class="form-group form-full">
                    <label>Work Performed</label>
                    <textarea id="reportWork" placeholder="Describe work completed today..."></textarea>
                </div>
                <div class="form-group form-full">
                    <label>Safety Observations</label>
                    <textarea id="reportSafety" placeholder="Any safety incidents, near-misses, or observations..."></textarea>
                </div>
                <div class="form-group form-full">
                    <label>Delays / Issues</label>
                    <textarea id="reportDelays" placeholder="Weather delays, material shortages, etc."></textarea>
                </div>
                <div class="form-group form-full">
                    <label>Photos (upload)</label>
                    <input type="file" id="reportPhotos" multiple accept="image/*" style="padding:8px;">
                </div>
            </div>
            <div class="modal-actions">
                <button type="button" class="btn btn-secondary" onclick="closeModal('reportModal')">Cancel</button>
                <button type="button" class="btn btn-secondary" onclick="saveDraft()">Save Draft</button>
                <button type="submit" class="btn btn-primary">Submit Report</button>
            </div>
        </form>
    </div>
</div>

<script>
    let reports = [];
    let editingId = null;

    async function loadReports() {
        try {
            const resp = await fetch('/api/field/daily');
            const data = await resp.json();
            reports = data.reports || [];
            renderReports();
            updateStats();
        } catch(e) {
            console.error('Failed to load daily reports:', e);
            reports = [];
            renderReports();
        }
    }

    function renderReports() {
        const tbody = document.getElementById('reportsTable');
        const empty = document.getElementById('emptyState');
        const search = document.getElementById('searchInput').value.toLowerCase();
        const dateFilter = document.getElementById('filterDate').value;
        const projectFilter = document.getElementById('filterProject').value;
        const statusFilter = document.getElementById('filterStatus').value;

        let filtered = reports.filter(r => {
            if (search && !JSON.stringify(r).toLowerCase().includes(search)) return false;
            if (dateFilter && r.date !== dateFilter) return false;
            if (projectFilter && r.project_id !== projectFilter) return false;
            if (statusFilter && r.status !== statusFilter) return false;
            return true;
        });

        if (filtered.length === 0) {
            tbody.innerHTML = '';
            empty.style.display = 'block';
            return;
        }
        empty.style.display = 'none';

        const weatherIcons = { clear: '&#9728;', cloudy: '&#9729;', rain: '&#127783;', snow: '&#10052;', wind: '&#127744;', storm: '&#9889;' };
        const statusClass = { draft: 'badge-draft', submitted: 'badge-submitted', approved: 'badge-approved' };

        tbody.innerHTML = filtered.map(r => `
            <tr onclick="viewReport('${r.id}')">
                <td>${r.date || ''}</td>
                <td>${r.project_name || r.project_id || ''}</td>
                <td>${r.superintendent || ''}</td>
                <td><span class="weather-badge">${weatherIcons[r.weather] || ''} ${r.temperature || ''}F</span></td>
                <td>${r.crew_count || 0}</td>
                <td>${r.total_hours || 0}h</td>
                <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${r.safety_notes || 'None'}</td>
                <td><span class="badge ${statusClass[r.status] || 'badge-draft'}">${r.status || 'draft'}</span></td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="event.stopPropagation();editReport('${r.id}')">Edit</button>
                </td>
            </tr>
        `).join('');
    }

    function updateStats() {
        document.getElementById('stat-total').textContent = reports.length;
        const now = new Date();
        const weekAgo = new Date(now - 7*24*60*60*1000);
        document.getElementById('stat-week').textContent = reports.filter(r => new Date(r.date) >= weekAgo).length;
        document.getElementById('stat-submitted').textContent = reports.filter(r => r.status === 'submitted' || r.status === 'approved').length;
        document.getElementById('stat-drafts').textContent = reports.filter(r => r.status === 'draft').length;
    }

    function filterTable() { renderReports(); }
    function filterReports(type) {
        if (type === 'draft') document.getElementById('filterStatus').value = 'draft';
        else if (type === 'submitted') document.getElementById('filterStatus').value = 'submitted';
        else document.getElementById('filterStatus').value = '';
        renderReports();
    }

    function openNewReport() {
        editingId = null;
        document.getElementById('modalTitle').textContent = 'New Daily Report';
        document.getElementById('reportForm').reset();
        document.getElementById('reportDate').value = new Date().toISOString().split('T')[0];
        document.getElementById('reportModal').classList.add('active');
    }

    function editReport(id) {
        const r = reports.find(x => x.id === id);
        if (!r) return;
        editingId = id;
        document.getElementById('modalTitle').textContent = 'Edit Daily Report';
        document.getElementById('reportDate').value = r.date || '';
        document.getElementById('reportProject').value = r.project_id || '';
        document.getElementById('reportWeather').value = r.weather || '';
        document.getElementById('reportTemp').value = r.temperature || '';
        document.getElementById('reportCrew').value = r.crew_count || '';
        document.getElementById('reportHours').value = r.total_hours || '';
        document.getElementById('reportWork').value = r.work_performed || '';
        document.getElementById('reportSafety').value = r.safety_notes || '';
        document.getElementById('reportDelays').value = r.delays || '';
        document.getElementById('reportModal').classList.add('active');
    }

    function viewReport(id) { editReport(id); }

    async function saveReport(e) {
        e.preventDefault();
        const payload = {
            id: editingId,
            date: document.getElementById('reportDate').value,
            project_id: document.getElementById('reportProject').value,
            weather: document.getElementById('reportWeather').value,
            temperature: document.getElementById('reportTemp').value,
            crew_count: parseInt(document.getElementById('reportCrew').value) || 0,
            total_hours: parseFloat(document.getElementById('reportHours').value) || 0,
            work_performed: document.getElementById('reportWork').value,
            safety_notes: document.getElementById('reportSafety').value,
            delays: document.getElementById('reportDelays').value,
            status: 'submitted'
        };
        try {
            await fetch('/api/field/daily', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
            closeModal('reportModal');
            loadReports();
        } catch(e) { alert('Error saving report'); }
    }

    function saveDraft() {
        const payload = {
            id: editingId,
            date: document.getElementById('reportDate').value,
            project_id: document.getElementById('reportProject').value,
            weather: document.getElementById('reportWeather').value,
            temperature: document.getElementById('reportTemp').value,
            crew_count: parseInt(document.getElementById('reportCrew').value) || 0,
            total_hours: parseFloat(document.getElementById('reportHours').value) || 0,
            work_performed: document.getElementById('reportWork').value,
            safety_notes: document.getElementById('reportSafety').value,
            delays: document.getElementById('reportDelays').value,
            status: 'draft'
        };
        fetch('/api/field/daily', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) })
            .then(() => { closeModal('reportModal'); loadReports(); })
            .catch(() => alert('Error saving draft'));
    }

    function closeModal(id) { document.getElementById(id).classList.remove('active'); }
    window.addEventListener('click', e => { if (e.target.classList.contains('modal-overlay')) e.target.classList.remove('active'); });

    document.addEventListener('DOMContentLoaded', loadReports);
</script>
"""
