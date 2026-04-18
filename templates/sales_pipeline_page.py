"""
TitanForge v4 — Sales Pipeline (Kanban)
=========================================
Visual kanban board for tracking leads through pipeline stages.
"""

SALES_PIPELINE_PAGE_HTML = r"""
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
    .pipeline-container {
        max-width: 1600px;
        margin: 0 auto;
        padding: 24px 32px;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        color: var(--tf-text);
    }
    .page-header { margin-bottom: 28px; }
    .page-header h1 { font-size: 28px; font-weight: 800; margin: 0 0 6px 0; }
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

    /* Toolbar */
    .toolbar {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 20px; flex-wrap: wrap; gap: 12px;
    }
    .toolbar-left { display: flex; gap: 10px; align-items: center; }
    .toolbar input[type="text"] {
        background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06);
        border-radius: 8px; padding: 10px 16px; color: var(--tf-text); font-size: 14px; width: 260px;
    }
    .toolbar input::placeholder { color: var(--tf-muted); }
    .toolbar select {
        background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06);
        border-radius: 8px; padding: 10px 16px; color: var(--tf-text); font-size: 14px; cursor: pointer;
    }

    /* Kanban Board */
    .kanban-board {
        display: flex; gap: 16px; overflow-x: auto;
        padding-bottom: 16px; min-height: 500px;
    }
    .kanban-column {
        min-width: 260px; width: 260px; flex-shrink: 0;
        display: flex; flex-direction: column;
    }
    .column-header {
        display: flex; align-items: center; justify-content: space-between;
        padding: 14px 16px; background: var(--tf-card); border-radius: 12px 12px 0 0;
        border: 1px solid rgba(255,255,255,0.06); border-bottom: none;
    }
    .column-header .col-title {
        font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;
    }
    .column-header .col-count {
        background: rgba(255,255,255,0.06); border-radius: 12px;
        padding: 2px 10px; font-size: 12px; font-weight: 600; color: var(--tf-muted);
    }
    .column-body {
        flex: 1; background: rgba(30,41,59,0.5); border-radius: 0 0 12px 12px;
        border: 1px solid rgba(255,255,255,0.06); border-top: none;
        padding: 10px; display: flex; flex-direction: column; gap: 10px;
        min-height: 200px;
    }
    .column-body.drag-over { background: rgba(212,168,67,0.08); border-color: rgba(212,168,67,0.3); }

    /* Kanban Cards */
    .kanban-card {
        background: var(--tf-card); border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.06);
        padding: 14px 16px; cursor: grab; transition: border-color 0.2s, transform 0.15s;
    }
    .kanban-card:hover { border-color: var(--tf-gold); transform: translateY(-1px); }
    .kanban-card:active { cursor: grabbing; }
    .kanban-card.dragging { opacity: 0.5; }
    .kc-name { font-weight: 600; font-size: 14px; margin-bottom: 4px; }
    .kc-company { font-size: 12px; color: var(--tf-muted); margin-bottom: 10px; }
    .kc-footer { display: flex; justify-content: space-between; align-items: center; }
    .kc-value { font-size: 14px; font-weight: 700; color: var(--tf-gold); }
    .kc-days {
        font-size: 11px; color: var(--tf-muted); background: rgba(255,255,255,0.04);
        padding: 2px 8px; border-radius: 4px;
    }
    .kc-assigned {
        font-size: 11px; color: var(--tf-muted); margin-top: 8px;
        display: flex; align-items: center; gap: 4px;
    }
    .kc-avatar {
        width: 18px; height: 18px; border-radius: 50%;
        background: var(--tf-blue); display: inline-flex; align-items: center;
        justify-content: center; font-size: 9px; font-weight: 700; color: #fff;
    }

    .col-new .column-header { border-left: 3px solid var(--tf-blue); }
    .col-contacted .column-header { border-left: 3px solid var(--tf-gold); }
    .col-qualified .column-header { border-left: 3px solid #a78bfa; }
    .col-proposal .column-header { border-left: 3px solid #fb923c; }
    .col-won .column-header { border-left: 3px solid var(--tf-green); }
    .col-lost .column-header { border-left: 3px solid var(--tf-red); }

    .empty-col {
        text-align: center; padding: 30px 10px; color: var(--tf-muted);
        font-size: 13px; opacity: 0.6;
    }
</style>

<div class="pipeline-container">
    <div class="page-header">
        <h1>Sales Pipeline</h1>
        <p>Drag leads through stages to track progress from first contact to close</p>
    </div>

    <div class="stat-row">
        <div class="stat-card stat-gold">
            <div class="label">Total Pipeline Value</div>
            <div class="value" id="stat-pipeline">--</div>
            <div class="sub">Active leads</div>
        </div>
        <div class="stat-card stat-blue">
            <div class="label">Avg Deal Size</div>
            <div class="value" id="stat-avg-deal">--</div>
            <div class="sub">Across all leads</div>
        </div>
        <div class="stat-card stat-green">
            <div class="label">Avg Time to Close</div>
            <div class="value" id="stat-avg-time">--</div>
            <div class="sub">Won deals</div>
        </div>
        <div class="stat-card stat-green">
            <div class="label">Conversion Rate</div>
            <div class="value" id="stat-conversion">--</div>
            <div class="sub">Lead to Won</div>
        </div>
    </div>

    <div class="toolbar">
        <div class="toolbar-left">
            <input type="text" id="searchInput" placeholder="Search pipeline..." oninput="applyFilter()">
            <select id="assigneeFilter" onchange="applyFilter()">
                <option value="">All Reps</option>
            </select>
        </div>
    </div>

    <div class="kanban-board" id="kanbanBoard">
        <div class="kanban-column col-new" data-stage="new">
            <div class="column-header">
                <span class="col-title">New</span>
                <span class="col-count" id="count-new">0</span>
            </div>
            <div class="column-body" id="col-new"></div>
        </div>
        <div class="kanban-column col-contacted" data-stage="contacted">
            <div class="column-header">
                <span class="col-title">Contacted</span>
                <span class="col-count" id="count-contacted">0</span>
            </div>
            <div class="column-body" id="col-contacted"></div>
        </div>
        <div class="kanban-column col-qualified" data-stage="qualified">
            <div class="column-header">
                <span class="col-title">Qualified</span>
                <span class="col-count" id="count-qualified">0</span>
            </div>
            <div class="column-body" id="col-qualified"></div>
        </div>
        <div class="kanban-column col-proposal" data-stage="proposal">
            <div class="column-header">
                <span class="col-title">Proposal</span>
                <span class="col-count" id="count-proposal">0</span>
            </div>
            <div class="column-body" id="col-proposal"></div>
        </div>
        <div class="kanban-column col-won" data-stage="won">
            <div class="column-header">
                <span class="col-title">Won</span>
                <span class="col-count" id="count-won">0</span>
            </div>
            <div class="column-body" id="col-won"></div>
        </div>
        <div class="kanban-column col-lost" data-stage="lost">
            <div class="column-header">
                <span class="col-title">Lost</span>
                <span class="col-count" id="count-lost">0</span>
            </div>
            <div class="column-body" id="col-lost"></div>
        </div>
    </div>
</div>

<script>
let allLeads = [];
const stages = ['new','contacted','qualified','proposal','won','lost'];

function formatCurrency(val) {
    if (val == null) return '$0';
    return '$' + Number(val).toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}

function daysInStage(lead) {
    const entered = lead.stage_entered_at || lead.last_contact || lead.created_at;
    if (!entered) return 0;
    return Math.max(0, Math.floor((Date.now() - new Date(entered).getTime()) / 86400000));
}

function initials(name) {
    if (!name) return '?';
    return name.split(' ').map(w => w[0]).join('').substring(0, 2).toUpperCase();
}

function updateStats(leads) {
    const active = leads.filter(l => !['won','lost'].includes((l.status||'').toLowerCase()));
    const pipeline = active.reduce((s, l) => s + (Number(l.value) || 0), 0);
    document.getElementById('stat-pipeline').textContent = formatCurrency(pipeline);

    const withValue = leads.filter(l => Number(l.value) > 0);
    const avg = withValue.length ? withValue.reduce((s, l) => s + Number(l.value), 0) / withValue.length : 0;
    document.getElementById('stat-avg-deal').textContent = formatCurrency(avg);

    const won = leads.filter(l => (l.status||'').toLowerCase() === 'won');
    let avgDays = 0;
    if (won.length) {
        const totalDays = won.reduce((s, l) => {
            const created = l.created_at ? new Date(l.created_at) : null;
            const closed = l.closed_at ? new Date(l.closed_at) : new Date();
            if (!created) return s;
            return s + Math.floor((closed - created) / 86400000);
        }, 0);
        avgDays = Math.round(totalDays / won.length);
    }
    document.getElementById('stat-avg-time').textContent = avgDays ? avgDays + 'd' : '--';

    const total = leads.length;
    const wonCount = won.length;
    const rate = total > 0 ? Math.round((wonCount / total) * 100) : 0;
    document.getElementById('stat-conversion').textContent = rate + '%';
}

function buildCard(lead) {
    const days = daysInStage(lead);
    return `<div class="kanban-card" draggable="true" data-id="${lead.id || ''}" data-name="${(lead.name||'').toLowerCase()}" data-assigned="${(lead.assigned_to||'').toLowerCase()}">
        <div class="kc-name">${lead.name || 'Unnamed Lead'}</div>
        <div class="kc-company">${lead.company || 'No company'}</div>
        <div class="kc-footer">
            <span class="kc-value">${formatCurrency(lead.value)}</span>
            <span class="kc-days">${days}d in stage</span>
        </div>
        ${lead.assigned_to ? `<div class="kc-assigned"><span class="kc-avatar">${initials(lead.assigned_to)}</span> ${lead.assigned_to}</div>` : ''}
    </div>`;
}

function renderBoard(leads) {
    stages.forEach(stage => {
        const col = document.getElementById('col-' + stage);
        const stageLeads = leads.filter(l => (l.status||'new').toLowerCase() === stage);
        document.getElementById('count-' + stage).textContent = stageLeads.length;
        if (!stageLeads.length) {
            col.innerHTML = '<div class="empty-col">No leads in this stage</div>';
        } else {
            col.innerHTML = stageLeads.map(buildCard).join('');
        }
    });
    initDragDrop();
}

function populateAssigneeFilter(leads) {
    const reps = [...new Set(leads.map(l => l.assigned_to).filter(Boolean))];
    const sel = document.getElementById('assigneeFilter');
    reps.forEach(r => {
        const opt = document.createElement('option');
        opt.value = r; opt.textContent = r;
        sel.appendChild(opt);
    });
}

function applyFilter() {
    const q = (document.getElementById('searchInput').value || '').toLowerCase();
    const rep = document.getElementById('assigneeFilter').value.toLowerCase();
    let filtered = allLeads.filter(l => {
        if (q && !(l.name||'').toLowerCase().includes(q) && !(l.company||'').toLowerCase().includes(q)) return false;
        if (rep && (l.assigned_to||'').toLowerCase() !== rep) return false;
        return true;
    });
    renderBoard(filtered);
}

function initDragDrop() {
    const cards = document.querySelectorAll('.kanban-card');
    const bodies = document.querySelectorAll('.column-body');

    cards.forEach(card => {
        card.addEventListener('dragstart', e => {
            card.classList.add('dragging');
            e.dataTransfer.setData('text/plain', card.dataset.id);
        });
        card.addEventListener('dragend', () => card.classList.remove('dragging'));
    });

    bodies.forEach(body => {
        body.addEventListener('dragover', e => { e.preventDefault(); body.classList.add('drag-over'); });
        body.addEventListener('dragleave', () => body.classList.remove('drag-over'));
        body.addEventListener('drop', e => {
            e.preventDefault();
            body.classList.remove('drag-over');
            const leadId = e.dataTransfer.getData('text/plain');
            const newStage = body.parentElement.dataset.stage;
            const lead = allLeads.find(l => String(l.id) === leadId);
            if (lead) {
                lead.status = newStage;
                lead.stage_entered_at = new Date().toISOString();
                // Attempt to persist the change
                fetch('/api/sales/leads/' + leadId, {
                    method: 'PATCH',
                    headers: {'Content-Type':'application/json'},
                    body: JSON.stringify({ status: newStage })
                }).catch(() => {});
                applyFilter();
                updateStats(allLeads);
            }
        });
    });
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
    populateAssigneeFilter(allLeads);
    applyFilter();
}

loadLeads();
</script>
"""
