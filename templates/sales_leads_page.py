"""
TitanForge v4 — Sales Lead Tracking
=====================================
Track and manage sales leads through the pipeline.
"""

SALES_LEADS_PAGE_HTML = r"""
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
    }
    .leads-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 24px 32px;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        color: var(--tf-text);
    }
    .page-header { margin-bottom: 28px; }
    .page-header h1 {
        font-size: 28px; font-weight: 800; margin: 0 0 6px 0; color: var(--tf-text);
    }
    .page-header p { font-size: 14px; color: var(--tf-muted); margin: 0; }

    /* Stat Cards */
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
    .stat-card .sub { font-size: 12px; color: var(--tf-muted); margin-top: 4px; }
    .stat-gold .value { color: var(--tf-gold); }
    .stat-blue .value { color: var(--tf-blue); }
    .stat-green .value { color: var(--tf-green); }
    .stat-red .value { color: var(--tf-red); }

    /* Toolbar */
    .toolbar {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 20px; flex-wrap: wrap; gap: 12px;
    }
    .toolbar-left { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
    .toolbar input[type="text"], .toolbar select {
        background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06);
        border-radius: 8px; padding: 10px 16px; color: var(--tf-text); font-size: 14px;
    }
    .toolbar input[type="text"] { width: 260px; }
    .toolbar input::placeholder { color: var(--tf-muted); }
    .toolbar select { cursor: pointer; }
    .btn-gold {
        background: var(--tf-gold); color: #0f172a; border: none; border-radius: 8px;
        padding: 10px 20px; font-weight: 700; font-size: 14px; cursor: pointer;
    }
    .btn-gold:hover { opacity: 0.9; }

    /* Table */
    .table-card {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06); overflow: hidden;
    }
    .leads-table {
        width: 100%; border-collapse: collapse; font-size: 14px;
    }
    .leads-table th {
        text-align: left; padding: 14px 16px; font-size: 11px;
        text-transform: uppercase; letter-spacing: 0.5px; color: var(--tf-muted);
        border-bottom: 1px solid rgba(255,255,255,0.06); font-weight: 600;
    }
    .leads-table td {
        padding: 14px 16px; border-bottom: 1px solid rgba(255,255,255,0.04);
        vertical-align: middle;
    }
    .leads-table tr:hover { background: rgba(255,255,255,0.02); }
    .leads-table tr:last-child td { border-bottom: none; }

    .lead-name { font-weight: 600; color: var(--tf-text); }
    .lead-company { font-size: 12px; color: var(--tf-muted); }

    .badge {
        display: inline-block; padding: 4px 10px; border-radius: 20px;
        font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;
    }
    .badge-new { background: rgba(59,130,246,0.15); color: #60a5fa; }
    .badge-contacted { background: rgba(212,168,67,0.15); color: #d4a843; }
    .badge-qualified { background: rgba(139,92,246,0.15); color: #a78bfa; }
    .badge-proposal { background: rgba(249,115,22,0.15); color: #fb923c; }
    .badge-won { background: rgba(16,185,129,0.15); color: #34d399; }
    .badge-lost { background: rgba(239,68,68,0.15); color: #f87171; }

    .source-tag {
        font-size: 12px; color: var(--tf-muted); background: rgba(255,255,255,0.04);
        padding: 3px 8px; border-radius: 4px;
    }

    .empty-state {
        text-align: center; padding: 60px 20px; color: var(--tf-muted);
    }
    .empty-state svg { margin-bottom: 16px; opacity: 0.4; }
    .empty-state h3 { color: var(--tf-text); margin-bottom: 8px; }

    /* Modal */
    .modal-overlay {
        display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.6); z-index: 9999; justify-content: center; align-items: center;
    }
    .modal-overlay.active { display: flex; }
    .modal {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.1); padding: 32px;
        width: 540px; max-width: 95vw; max-height: 90vh; overflow-y: auto;
    }
    .modal h2 { margin: 0 0 24px 0; font-size: 20px; font-weight: 700; }
    .form-group { margin-bottom: 16px; }
    .form-group label {
        display: block; font-size: 12px; color: var(--tf-muted);
        text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; font-weight: 600;
    }
    .form-group input, .form-group select, .form-group textarea {
        width: 100%; background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px;
        font-family: inherit; box-sizing: border-box;
    }
    .form-group textarea { resize: vertical; min-height: 80px; }
    .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 24px; }
    .btn-secondary {
        background: transparent; border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px; padding: 10px 20px; color: var(--tf-muted);
        font-weight: 600; font-size: 14px; cursor: pointer;
    }
    .btn-secondary:hover { color: var(--tf-text); border-color: rgba(255,255,255,0.2); }

/* ── Responsive ── */
@media (max-width: 768px) {
    .page-header h1 { font-size: 22px; }
    .toolbar { flex-direction: column; align-items: stretch; }
    .toolbar input[type="text"] { width: 100%; }
    .stat-row { grid-template-columns: 1fr 1fr; gap: 10px; }
    .modal-overlay .modal, .modal { width: 95%; max-width: 95vw; margin: 20px auto; padding: 20px; }
    .form-row { grid-template-columns: 1fr; }
    .leads-table { display: block; overflow-x: auto; -webkit-overflow-scrolling: touch; }
}
@media (max-width: 480px) {
    .stat-row { grid-template-columns: 1fr; }
    .toolbar { gap: 8px; }
}
</style>

<div class="leads-container">
    <div class="page-header">
        <h1>Sales Leads</h1>
        <p>Track and manage prospective customers through the sales pipeline</p>
    </div>

    <div class="stat-row">
        <div class="stat-card stat-blue" onclick="filterByStatus('')">
            <div class="label">Total Leads</div>
            <div class="value" id="stat-total">--</div>
            <div class="sub">All time</div>
        </div>
        <div class="stat-card stat-green" onclick="filterByStatus('new')">
            <div class="label">New This Week</div>
            <div class="value" id="stat-new">--</div>
            <div class="sub">Last 7 days</div>
        </div>
        <div class="stat-card stat-gold" onclick="filterByStatus('')">
            <div class="label">Pipeline Value</div>
            <div class="value" id="stat-pipeline">--</div>
            <div class="sub">Active leads</div>
        </div>
        <div class="stat-card stat-green" onclick="filterByStatus('won')">
            <div class="label">Win Rate</div>
            <div class="value" id="stat-winrate">--</div>
            <div class="sub">Closed deals</div>
        </div>
    </div>

    <div class="toolbar">
        <div class="toolbar-left">
            <input type="text" id="searchInput" placeholder="Search leads..." oninput="applyFilters()">
            <select id="statusFilter" onchange="applyFilters()">
                <option value="">All Statuses</option>
                <option value="new">New</option>
                <option value="contacted">Contacted</option>
                <option value="qualified">Qualified</option>
                <option value="proposal">Proposal</option>
                <option value="won">Won</option>
                <option value="lost">Lost</option>
            </select>
            <select id="sourceFilter" onchange="applyFilters()">
                <option value="">All Sources</option>
                <option value="referral">Referral</option>
                <option value="website">Website</option>
                <option value="cold call">Cold Call</option>
            </select>
        </div>
        <button class="btn-gold" onclick="openAddModal()">+ Add Lead</button>
    </div>

    <div class="table-card">
        <table class="leads-table">
            <thead>
                <tr>
                    <th>Lead Name</th>
                    <th>Company</th>
                    <th>Source</th>
                    <th>Status</th>
                    <th>Value</th>
                    <th>Assigned To</th>
                    <th>Last Contact</th>
                </tr>
            </thead>
            <tbody id="leadsTableBody">
                <tr><td colspan="7" class="empty-state">Loading...</td></tr>
            </tbody>
        </table>
    </div>
</div>

<!-- Add Lead Modal -->
<div class="modal-overlay" id="addLeadModal">
    <div class="modal">
        <h2>Add New Lead</h2>
        <form id="addLeadForm" onsubmit="submitLead(event)">
            <div class="form-row">
                <div class="form-group">
                    <label>Lead Name</label>
                    <input type="text" name="name" required placeholder="Full name">
                </div>
                <div class="form-group">
                    <label>Company</label>
                    <input type="text" name="company" placeholder="Company name">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" name="email" placeholder="email@example.com">
                </div>
                <div class="form-group">
                    <label>Phone</label>
                    <input type="text" name="phone" placeholder="(555) 000-0000">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Source</label>
                    <select name="source">
                        <option value="referral">Referral</option>
                        <option value="website">Website</option>
                        <option value="cold call">Cold Call</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Estimated Value ($)</label>
                    <input type="number" name="value" placeholder="0.00" step="0.01">
                </div>
            </div>
            <div class="form-group">
                <label>Assigned To</label>
                <input type="text" name="assigned_to" placeholder="Sales rep name">
            </div>
            <div class="form-group">
                <label>Notes</label>
                <textarea name="notes" placeholder="Any initial notes about this lead..."></textarea>
            </div>
            <div class="modal-actions">
                <button type="button" class="btn-secondary" onclick="closeAddModal()">Cancel</button>
                <button type="submit" class="btn-gold">Add Lead</button>
            </div>
        </form>
    </div>
</div>

<script>
let allLeads = [];

function formatCurrency(val) {
    if (val == null) return '$0';
    return '$' + Number(val).toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}

function formatDate(d) {
    if (!d) return '--';
    const dt = new Date(d);
    if (isNaN(dt)) return d;
    return dt.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function statusBadge(status) {
    const s = (status || 'new').toLowerCase();
    const labels = { new:'New', contacted:'Contacted', qualified:'Qualified', proposal:'Proposal', won:'Won', lost:'Lost' };
    return `<span class="badge badge-${s}">${labels[s] || s}</span>`;
}

function updateStats(leads) {
    document.getElementById('stat-total').textContent = leads.length;
    const weekAgo = Date.now() - 7 * 86400000;
    const newThisWeek = leads.filter(l => l.created_at && new Date(l.created_at) >= weekAgo).length;
    document.getElementById('stat-new').textContent = newThisWeek;
    const active = leads.filter(l => !['won','lost'].includes((l.status||'').toLowerCase()));
    const pipelineVal = active.reduce((s, l) => s + (Number(l.value) || 0), 0);
    document.getElementById('stat-pipeline').textContent = formatCurrency(pipelineVal);
    const closed = leads.filter(l => ['won','lost'].includes((l.status||'').toLowerCase()));
    const won = leads.filter(l => (l.status||'').toLowerCase() === 'won').length;
    const rate = closed.length > 0 ? Math.round((won / closed.length) * 100) : 0;
    document.getElementById('stat-winrate').textContent = rate + '%';
}

function renderTable(leads) {
    const tbody = document.getElementById('leadsTableBody');
    if (!leads.length) {
        tbody.innerHTML = `<tr><td colspan="7" class="empty-state">
            <svg width="48" height="48" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" stroke-width="1.5" d="M12 6v6l4 2m6-2a10 10 0 11-20 0 10 10 0 0120 0z"/></svg>
            <h3>No leads found</h3><p>Add your first lead to get started</p></td></tr>`;
        return;
    }
    tbody.innerHTML = leads.map(l => `<tr>
        <td><div class="lead-name">${l.name || '--'}</div></td>
        <td><span class="lead-company">${l.company || '--'}</span></td>
        <td><span class="source-tag">${l.source || '--'}</span></td>
        <td>${statusBadge(l.status)}</td>
        <td style="font-weight:600">${formatCurrency(l.value)}</td>
        <td>${l.assigned_to || '--'}</td>
        <td style="color:var(--tf-muted)">${formatDate(l.last_contact)}</td>
    </tr>`).join('');
}

function applyFilters() {
    const q = (document.getElementById('searchInput').value || '').toLowerCase();
    const status = document.getElementById('statusFilter').value;
    const source = document.getElementById('sourceFilter').value;
    let filtered = allLeads.filter(l => {
        if (q && !(l.name||'').toLowerCase().includes(q) && !(l.company||'').toLowerCase().includes(q)) return false;
        if (status && (l.status||'').toLowerCase() !== status) return false;
        if (source && (l.source||'').toLowerCase() !== source) return false;
        return true;
    });
    renderTable(filtered);
}

function filterByStatus(s) {
    document.getElementById('statusFilter').value = s;
    applyFilters();
}

function openAddModal() { document.getElementById('addLeadModal').classList.add('active'); }
function closeAddModal() { document.getElementById('addLeadModal').classList.remove('active'); }

async function submitLead(e) {
    e.preventDefault();
    const form = e.target;
    const data = Object.fromEntries(new FormData(form));
    data.status = 'new';
    data.created_at = new Date().toISOString();
    data.last_contact = new Date().toISOString();
    try {
        const res = await fetch('/api/sales/leads', {
            method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data)
        });
        if (res.ok) {
            closeAddModal();
            form.reset();
            loadLeads();
        }
    } catch(err) {
        console.error('Failed to add lead:', err);
    }
}

async function loadLeads() {
    try {
        const res = await fetch('/api/sales/leads');
        if (!res.ok) throw new Error('API error');
        const data = await res.json();
        allLeads = Array.isArray(data) ? data : (data.leads || data.data || []);
    } catch(err) {
        console.warn('Could not load leads:', err);
        allLeads = [];
    }
    updateStats(allLeads);
    applyFilters();
}

// Close modal on overlay click
document.getElementById('addLeadModal').addEventListener('click', function(e) {
    if (e.target === this) closeAddModal();
});

loadLeads();
</script>
"""
