"""
TitanForge v4 — Sales Lead Tracking (Production)
==================================================
Full lead tracking with pipeline statuses, follow-up reminders,
and convert-to-customer capability.
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
        --tf-purple: #a78bfa;
        --tf-orange: #fb923c;
    }
    .leads-container {
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
    .stat-card .sub { font-size: 12px; color: var(--tf-muted); margin-top: 4px; }
    .stat-gold .value { color: var(--tf-gold); }
    .stat-blue .value { color: var(--tf-blue); }
    .stat-green .value { color: var(--tf-green); }
    .stat-red .value { color: var(--tf-red); }

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
    .btn-sm {
        padding: 5px 12px; font-size: 12px; border-radius: 6px; border: none;
        font-weight: 600; cursor: pointer;
    }
    .btn-convert { background: rgba(16,185,129,0.15); color: #34d399; }
    .btn-advance { background: rgba(59,130,246,0.15); color: #60a5fa; }

    .table-card {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06); overflow: hidden;
    }
    .leads-table { width: 100%; border-collapse: collapse; font-size: 14px; }
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
    .leads-table tr.follow-up-overdue { background: rgba(239,68,68,0.04); }
    .leads-table tr.follow-up-today { background: rgba(212,168,67,0.04); }

    .lead-name { font-weight: 600; color: var(--tf-text); }
    .lead-company { font-size: 12px; color: var(--tf-muted); }
    .lead-contact { font-size: 12px; color: var(--tf-muted); margin-top: 2px; }

    .badge {
        display: inline-block; padding: 4px 10px; border-radius: 20px;
        font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;
        cursor: pointer;
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

    .follow-up-date { font-size: 12px; }
    .follow-up-past { color: var(--tf-red); font-weight: 600; }
    .follow-up-today { color: var(--tf-gold); font-weight: 600; }
    .follow-up-future { color: var(--tf-muted); }

    .empty-state { text-align: center; padding: 60px 20px; color: var(--tf-muted); }
    .empty-state h3 { color: var(--tf-text); margin-bottom: 8px; }

    .modal-overlay {
        display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.6); z-index: 9999; justify-content: center; align-items: center;
    }
    .modal-overlay.active { display: flex; }
    .modal {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.1); padding: 32px;
        width: 580px; max-width: 95vw; max-height: 90vh; overflow-y: auto;
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

    .status-select {
        background: transparent; border: none; color: inherit; font-size: 11px;
        font-weight: 600; cursor: pointer; padding: 4px; border-radius: 4px;
    }

/* Responsive */
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
        <div class="stat-card stat-gold" onclick="filterByStatus('')">
            <div class="label">Pipeline Value</div>
            <div class="value" id="stat-pipeline">--</div>
            <div class="sub">Active leads</div>
        </div>
        <div class="stat-card stat-red" onclick="filterFollowUp()">
            <div class="label">Follow-Up Due</div>
            <div class="value" id="stat-followup">--</div>
            <div class="sub">Need attention</div>
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
                <option value="website">Website</option>
                <option value="referral">Referral</option>
                <option value="cold_call">Cold Call</option>
                <option value="trade_show">Trade Show</option>
            </select>
        </div>
        <button class="btn-gold" onclick="openAddModal()">+ Add Lead</button>
    </div>

    <div class="table-card">
        <table class="leads-table">
            <thead>
                <tr>
                    <th>Lead</th>
                    <th>Source</th>
                    <th>Est. Value</th>
                    <th>Status</th>
                    <th>Follow-Up</th>
                    <th>Last Contact</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody id="leadsTableBody">
                <tr><td colspan="7" class="empty-state">Loading...</td></tr>
            </tbody>
        </table>
    </div>
</div>

<!-- Add/Edit Lead Modal -->
<div class="modal-overlay" id="addLeadModal">
    <div class="modal">
        <h2 id="leadModalTitle">Add New Lead</h2>
        <form id="addLeadForm" onsubmit="submitLead(event)">
            <input type="hidden" id="editLeadId" value="">
            <div class="form-row">
                <div class="form-group">
                    <label>Company Name</label>
                    <input type="text" name="company" required placeholder="Company name">
                </div>
                <div class="form-group">
                    <label>Contact Name</label>
                    <input type="text" name="name" required placeholder="Full name">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Phone</label>
                    <input type="text" name="phone" placeholder="(555) 000-0000">
                </div>
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" name="email" placeholder="email@example.com">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Source</label>
                    <select name="source">
                        <option value="website">Website</option>
                        <option value="referral">Referral</option>
                        <option value="cold_call">Cold Call</option>
                        <option value="trade_show">Trade Show</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Estimated Value ($)</label>
                    <input type="number" name="value" placeholder="0.00" step="0.01">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Next Follow-Up Date</label>
                    <input type="date" name="follow_up_date">
                </div>
                <div class="form-group">
                    <label>Assigned To</label>
                    <input type="text" name="assigned_to" placeholder="Sales rep name">
                </div>
            </div>
            <div class="form-group">
                <label>Notes</label>
                <textarea name="notes" placeholder="Any initial notes about this lead..."></textarea>
            </div>
            <div class="modal-actions">
                <button type="button" class="btn-secondary" onclick="closeAddModal()">Cancel</button>
                <button type="submit" class="btn-gold" id="leadSubmitBtn">Add Lead</button>
            </div>
        </form>
    </div>
</div>

<!-- Convert to Customer Modal -->
<div class="modal-overlay" id="convertModal">
    <div class="modal" style="width:460px;">
        <h2>Convert to Customer</h2>
        <p style="color:var(--tf-muted);font-size:14px;margin-bottom:20px;">This will create a new customer record from this lead.</p>
        <input type="hidden" id="convertLeadId">
        <div class="form-group">
            <label>Company Name</label>
            <input type="text" id="convertCompany" readonly style="opacity:0.7;">
        </div>
        <div class="form-group">
            <label>Contact Name</label>
            <input type="text" id="convertContact" readonly style="opacity:0.7;">
        </div>
        <div class="form-group" style="display:flex;align-items:center;gap:8px;">
            <input type="checkbox" id="convertCreateProject" checked>
            <label style="display:inline;text-transform:none;letter-spacing:0;font-size:14px;color:var(--tf-text);margin:0;cursor:pointer;" for="convertCreateProject">Also create a new project for this customer</label>
        </div>
        <div class="modal-actions">
            <button type="button" class="btn-secondary" onclick="closeConvertModal()">Cancel</button>
            <button type="button" class="btn-gold" onclick="doConvert()">Convert to Customer</button>
        </div>
    </div>
</div>

<script>
let allLeads = [];
const statusOrder = ['new','contacted','qualified','proposal','won','lost'];
const sourceLabels = { website: 'Website', referral: 'Referral', cold_call: 'Cold Call', trade_show: 'Trade Show' };

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
function today() { return new Date().toISOString().split('T')[0]; }

function getFollowUpClass(dateStr) {
    if (!dateStr) return '';
    const diff = Math.floor((new Date(dateStr + 'T23:59:59').getTime() - Date.now()) / 86400000);
    if (diff < 0) return 'follow-up-past';
    if (diff === 0) return 'follow-up-today';
    return 'follow-up-future';
}

function getRowClass(lead) {
    if (!lead.follow_up_date || ['won','lost'].includes(lead.status)) return '';
    const cls = getFollowUpClass(lead.follow_up_date);
    if (cls === 'follow-up-past') return 'follow-up-overdue';
    if (cls === 'follow-up-today') return 'follow-up-today';
    return '';
}

function statusBadge(status) {
    const s = (status || 'new').toLowerCase();
    const labels = { new:'New', contacted:'Contacted', qualified:'Qualified', proposal:'Proposal', won:'Won', lost:'Lost' };
    return '<span class="badge badge-' + s + '" onclick="event.stopPropagation()">' + (labels[s] || s) + '</span>';
}

function nextStatus(current) {
    const idx = statusOrder.indexOf(current);
    if (idx < 0 || idx >= statusOrder.length - 2) return current; // Don't auto-cycle past proposal
    return statusOrder[idx + 1];
}

function updateStats(leads) {
    document.getElementById('stat-total').textContent = leads.length;
    const active = leads.filter(l => !['won','lost'].includes((l.status||'').toLowerCase()));
    const pipelineVal = active.reduce((s, l) => s + (Number(l.value) || 0), 0);
    document.getElementById('stat-pipeline').textContent = formatCurrency(pipelineVal);

    // Follow-up due
    const followUpDue = leads.filter(l => {
        if (!l.follow_up_date || ['won','lost'].includes(l.status)) return false;
        return new Date(l.follow_up_date + 'T23:59:59') <= new Date();
    }).length;
    document.getElementById('stat-followup').textContent = followUpDue;

    const closed = leads.filter(l => ['won','lost'].includes((l.status||'').toLowerCase()));
    const won = leads.filter(l => (l.status||'').toLowerCase() === 'won').length;
    const rate = closed.length > 0 ? Math.round((won / closed.length) * 100) : 0;
    document.getElementById('stat-winrate').textContent = rate + '%';
}

function renderTable(leads) {
    const tbody = document.getElementById('leadsTableBody');
    if (!leads.length) {
        tbody.innerHTML = '<tr><td colspan="7" class="empty-state"><h3>No leads found</h3><p>Add your first lead to get started</p></td></tr>';
        return;
    }
    tbody.innerHTML = leads.map(l => {
        const fuClass = getFollowUpClass(l.follow_up_date);
        const rowClass = getRowClass(l);
        const isActive = !['won','lost'].includes((l.status||'new').toLowerCase());
        return '<tr class="' + rowClass + '">' +
            '<td><div class="lead-name">' + (l.name || '--') + '</div><div class="lead-company">' + (l.company || '') + '</div>' +
            (l.phone || l.email ? '<div class="lead-contact">' + [l.phone, l.email].filter(Boolean).join(' | ') + '</div>' : '') + '</td>' +
            '<td><span class="source-tag">' + (sourceLabels[l.source] || l.source || '--') + '</span></td>' +
            '<td style="font-weight:600">' + formatCurrency(l.value) + '</td>' +
            '<td>' +
                '<select class="status-select badge badge-' + (l.status||'new') + '" onchange="changeStatus(\'' + l.id + '\', this.value)" style="appearance:auto;">' +
                statusOrder.map(s => '<option value="' + s + '"' + ((l.status||'new') === s ? ' selected' : '') + '>' + s.charAt(0).toUpperCase() + s.slice(1) + '</option>').join('') +
                '</select>' +
            '</td>' +
            '<td><span class="follow-up-date ' + fuClass + '">' + (l.follow_up_date ? formatDate(l.follow_up_date) : '--') + '</span></td>' +
            '<td style="color:var(--tf-muted)">' + formatDate(l.last_contact) + '</td>' +
            '<td>' +
                (isActive ? '<button class="btn-sm btn-advance" onclick="advanceStatus(\'' + l.id + '\')" title="Advance to next stage">&#8594;</button> ' : '') +
                (l.status === 'won' || l.status === 'qualified' || l.status === 'proposal' ? '<button class="btn-sm btn-convert" onclick="openConvertModal(\'' + l.id + '\')" title="Convert to Customer">Convert</button>' : '') +
            '</td>' +
            '</tr>';
    }).join('');
}

function applyFilters() {
    const q = (document.getElementById('searchInput').value || '').toLowerCase();
    const status = document.getElementById('statusFilter').value;
    const source = document.getElementById('sourceFilter').value;
    let filtered = allLeads.filter(l => {
        if (q && !(l.name||'').toLowerCase().includes(q) && !(l.company||'').toLowerCase().includes(q) && !(l.email||'').toLowerCase().includes(q)) return false;
        if (status && (l.status||'').toLowerCase() !== status) return false;
        if (source && (l.source||'').toLowerCase() !== source) return false;
        return true;
    });
    renderTable(filtered);
}
function filterByStatus(s) { document.getElementById('statusFilter').value = s; applyFilters(); }
function filterFollowUp() {
    document.getElementById('statusFilter').value = '';
    const q = '';
    document.getElementById('searchInput').value = '';
    let filtered = allLeads.filter(l => {
        if (['won','lost'].includes(l.status)) return false;
        if (!l.follow_up_date) return false;
        return new Date(l.follow_up_date + 'T23:59:59') <= new Date();
    });
    renderTable(filtered);
}

// --- Status Changes ---
async function changeStatus(id, newStatus) {
    try {
        await fetch('/api/sales/leads', {
            method: 'PUT', headers: {'Content-Type':'application/json'},
            body: JSON.stringify({ id, status: newStatus, last_contact: new Date().toISOString() })
        });
        loadLeads();
    } catch(e) { console.error(e); }
}

function advanceStatus(id) {
    const lead = allLeads.find(l => l.id === id);
    if (!lead) return;
    const next = nextStatus(lead.status || 'new');
    if (next !== lead.status) changeStatus(id, next);
}

// --- Add/Edit Modal ---
function openAddModal() {
    document.getElementById('editLeadId').value = '';
    document.getElementById('leadModalTitle').textContent = 'Add New Lead';
    document.getElementById('leadSubmitBtn').textContent = 'Add Lead';
    document.getElementById('addLeadForm').reset();
    // Default follow-up to 3 days from now
    const fu = new Date(); fu.setDate(fu.getDate() + 3);
    document.querySelector('input[name="follow_up_date"]').value = fu.toISOString().split('T')[0];
    document.getElementById('addLeadModal').classList.add('active');
}
function closeAddModal() { document.getElementById('addLeadModal').classList.remove('active'); }

async function submitLead(e) {
    e.preventDefault();
    const form = e.target;
    const data = Object.fromEntries(new FormData(form));
    const editId = document.getElementById('editLeadId').value;

    if (editId) {
        data.id = editId;
        try {
            await fetch('/api/sales/leads', {
                method: 'PUT', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data)
            });
            closeAddModal(); form.reset(); loadLeads();
        } catch(err) { console.error(err); }
    } else {
        data.status = 'new';
        data.created_at = new Date().toISOString();
        data.last_contact = new Date().toISOString();
        try {
            const res = await fetch('/api/sales/leads', {
                method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data)
            });
            if (res.ok) { closeAddModal(); form.reset(); loadLeads(); }
        } catch(err) { console.error(err); }
    }
}

// --- Convert to Customer ---
function openConvertModal(id) {
    const lead = allLeads.find(l => l.id === id);
    if (!lead) return;
    document.getElementById('convertLeadId').value = id;
    document.getElementById('convertCompany').value = lead.company || lead.name || '';
    document.getElementById('convertContact').value = lead.name || '';
    document.getElementById('convertModal').classList.add('active');
}
function closeConvertModal() { document.getElementById('convertModal').classList.remove('active'); }

async function doConvert() {
    const leadId = document.getElementById('convertLeadId').value;
    const lead = allLeads.find(l => l.id === leadId);
    if (!lead) return;

    // Create customer
    try {
        const payload = {
            company: lead.company || lead.name || '',
            primary_contact: { name: lead.name || '', phone: lead.phone || '', email: lead.email || '' },
            tags: [],
            notes: 'Converted from sales lead. Source: ' + (lead.source||'') + '. Value: $' + (lead.value||0),
            payment_terms: 'Net 30',
        };
        const res = await fetch('/api/customers/create', {
            method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload)
        });
        const d = await res.json();
        if (d.ok) {
            // Mark lead as won
            await fetch('/api/sales/leads', {
                method: 'PUT', headers: {'Content-Type':'application/json'},
                body: JSON.stringify({ id: leadId, status: 'won', closed_at: new Date().toISOString() })
            });
            closeConvertModal();
            loadLeads();
            alert('Customer created successfully!' + (document.getElementById('convertCreateProject').checked ? ' Navigate to the customer page to create a project.' : ''));
        } else {
            alert(d.error || 'Failed to create customer');
        }
    } catch(e) {
        console.error(e);
        alert('Error converting lead');
    }
}

// --- Load ---
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

['addLeadModal','convertModal'].forEach(id => {
    document.getElementById(id).addEventListener('click', function(e) { if (e.target === this) this.classList.remove('active'); });
});

loadLeads();
</script>
"""
