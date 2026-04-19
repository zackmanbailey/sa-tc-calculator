"""
TitanForge v4 — Sales Quotes (Production)
===========================================
Quote management with status tracking, revision history,
accept/reject actions, and sent tracking.
"""

SALES_QUOTES_PAGE_HTML = r"""
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
        --tf-orange: #fb923c;
    }
    .quotes-container {
        max-width: 1400px; margin: 0 auto; padding: 24px 32px;
        font-family: 'Inter', system-ui, -apple-system, sans-serif; color: var(--tf-text);
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
    .stat-orange .value { color: var(--tf-orange); }

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
        font-weight: 600; cursor: pointer; transition: opacity 0.15s;
    }
    .btn-sm:hover { opacity: 0.8; }
    .btn-send { background: rgba(59,130,246,0.15); color: #60a5fa; }
    .btn-accept { background: rgba(16,185,129,0.15); color: #34d399; }
    .btn-reject { background: rgba(239,68,68,0.15); color: #f87171; }
    .btn-revise { background: rgba(212,168,67,0.15); color: #d4a843; }

    .table-card {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06); overflow: hidden;
    }
    .sq-table { width: 100%; border-collapse: collapse; font-size: 14px; }
    .sq-table th {
        text-align: left; padding: 14px 16px; font-size: 11px;
        text-transform: uppercase; letter-spacing: 0.5px; color: var(--tf-muted);
        border-bottom: 1px solid rgba(255,255,255,0.06); font-weight: 600;
    }
    .sq-table td {
        padding: 14px 16px; border-bottom: 1px solid rgba(255,255,255,0.04);
        vertical-align: middle;
    }
    .sq-table tr:hover { background: rgba(255,255,255,0.02); }
    .sq-table tr:last-child td { border-bottom: none; }

    .quote-num { font-weight: 700; color: var(--tf-gold); font-family: 'JetBrains Mono', monospace; }

    .badge {
        display: inline-block; padding: 4px 10px; border-radius: 20px;
        font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;
    }
    .badge-draft { background: rgba(148,163,184,0.15); color: #94a3b8; }
    .badge-sent { background: rgba(59,130,246,0.15); color: #60a5fa; }
    .badge-revised { background: rgba(212,168,67,0.15); color: #d4a843; }
    .badge-accepted { background: rgba(16,185,129,0.15); color: #34d399; }
    .badge-rejected { background: rgba(239,68,68,0.15); color: #f87171; }
    .badge-expired { background: rgba(249,115,22,0.15); color: #fb923c; }

    .revision-tag { font-size: 10px; color: var(--tf-muted); margin-left: 6px; }
    .expiry-warn { color: var(--tf-red); font-weight: 600; }

    .empty-state { text-align: center; padding: 60px 20px; color: var(--tf-muted); }
    .empty-state h3 { color: var(--tf-text); margin-bottom: 8px; }

    .sent-info { font-size: 11px; color: var(--tf-muted); margin-top: 4px; }

    /* Modal */
    .modal-overlay {
        display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.6); z-index: 9999; justify-content: center; align-items: center;
    }
    .modal-overlay.active { display: flex; }
    .modal {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.1); padding: 32px;
        width: 680px; max-width: 95vw; max-height: 90vh; overflow-y: auto;
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

    .line-items { margin-bottom: 16px; }
    .line-item {
        display: grid; grid-template-columns: 2fr 1fr 1fr 1fr auto; gap: 8px;
        align-items: center; margin-bottom: 8px;
    }
    .line-item input {
        background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px; padding: 8px 12px; color: var(--tf-text); font-size: 13px;
        box-sizing: border-box;
    }
    .line-item .li-total { font-size: 13px; font-weight: 600; color: var(--tf-gold); padding: 0 4px; }
    .btn-remove { background: none; border: none; color: var(--tf-red); cursor: pointer; font-size: 18px; padding: 4px; line-height: 1; }
    .btn-add-line {
        background: none; border: 1px dashed rgba(255,255,255,0.1);
        border-radius: 8px; padding: 8px 16px; color: var(--tf-muted);
        font-size: 13px; cursor: pointer; width: 100%;
    }
    .btn-add-line:hover { color: var(--tf-text); border-color: rgba(255,255,255,0.2); }

    /* Revision History */
    .revision-list { margin-top: 16px; }
    .revision-item {
        display: flex; justify-content: space-between; align-items: center;
        padding: 10px 14px; background: rgba(255,255,255,0.02); border-radius: 8px;
        margin-bottom: 6px; font-size: 13px;
    }
    .revision-item .rev-version { font-weight: 700; color: var(--tf-gold); }
    .revision-item .rev-amount { font-weight: 600; }
    .revision-item .rev-date { color: var(--tf-muted); font-size: 12px; }

    /* Send Tracking */
    .send-modal-group { background: rgba(255,255,255,0.02); border-radius: 8px; padding: 16px; margin-bottom: 16px; }

/* Responsive */
@media (max-width: 768px) {
    .page-header h1 { font-size: 22px; }
    .toolbar { flex-direction: column; align-items: stretch; }
    .toolbar input[type="text"] { width: 100%; }
    .stat-row { grid-template-columns: 1fr 1fr; gap: 10px; }
    .modal-overlay .modal, .modal { width: 95%; max-width: 95vw; margin: 20px auto; padding: 20px; }
    .form-row { grid-template-columns: 1fr; }
    .sq-table { display: block; overflow-x: auto; -webkit-overflow-scrolling: touch; }
    .line-item { grid-template-columns: 1fr 1fr auto; }
}
@media (max-width: 480px) {
    .stat-row { grid-template-columns: 1fr; }
}
</style>

<div class="quotes-container">
    <div class="page-header">
        <h1>Sales Quotes</h1>
        <p>Create and manage pre-project sales quotes for prospective customers</p>
    </div>

    <div class="stat-row">
        <div class="stat-card stat-blue" onclick="filterByStatus('')">
            <div class="label">Total Quotes</div>
            <div class="value" id="stat-total">--</div>
            <div class="sub">All time</div>
        </div>
        <div class="stat-card stat-orange" onclick="filterByStatus('sent')">
            <div class="label">Pending</div>
            <div class="value" id="stat-pending">--</div>
            <div class="sub">Awaiting response</div>
        </div>
        <div class="stat-card stat-green" onclick="filterByStatus('accepted')">
            <div class="label">Accepted</div>
            <div class="value" id="stat-accepted">--</div>
            <div class="sub">Converted to projects</div>
        </div>
        <div class="stat-card stat-gold" onclick="filterByStatus('')">
            <div class="label">Total Value</div>
            <div class="value" id="stat-value">--</div>
            <div class="sub">All quotes</div>
        </div>
    </div>

    <div class="toolbar">
        <div class="toolbar-left">
            <input type="text" id="searchInput" placeholder="Search quotes..." oninput="applyFilters()">
            <select id="statusFilter" onchange="applyFilters()">
                <option value="">All Statuses</option>
                <option value="draft">Draft</option>
                <option value="sent">Sent</option>
                <option value="revised">Revised</option>
                <option value="accepted">Accepted</option>
                <option value="rejected">Rejected</option>
            </select>
        </div>
        <button class="btn-gold" onclick="openCreateModal()">+ Create Quote</button>
    </div>

    <div class="table-card">
        <table class="sq-table">
            <thead>
                <tr>
                    <th>Quote #</th>
                    <th>Customer</th>
                    <th>Description</th>
                    <th>Amount</th>
                    <th>Sent</th>
                    <th>Follow-Up</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody id="quotesTableBody">
                <tr><td colspan="8" class="empty-state">Loading...</td></tr>
            </tbody>
        </table>
    </div>
</div>

<!-- Create/Edit Quote Modal -->
<div class="modal-overlay" id="createQuoteModal">
    <div class="modal">
        <h2 id="quoteModalTitle">Create Sales Quote</h2>
        <form id="createQuoteForm" onsubmit="submitQuote(event)">
            <input type="hidden" id="editQuoteId" value="">
            <div class="form-row">
                <div class="form-group">
                    <label>Customer Name</label>
                    <input type="text" name="customer" required placeholder="Customer or company name">
                </div>
                <div class="form-group">
                    <label>Contact Email</label>
                    <input type="email" name="email" placeholder="email@example.com">
                </div>
            </div>
            <div class="form-group">
                <label>Description</label>
                <textarea name="description" placeholder="Brief description of the quote scope..." required></textarea>
            </div>
            <div class="form-group">
                <label>Line Items</label>
                <div class="line-items" id="lineItems">
                    <div class="line-item">
                        <input type="text" placeholder="Item description" class="li-desc">
                        <input type="number" placeholder="Qty" class="li-qty" value="1" min="1" oninput="calcTotal(this)">
                        <input type="number" placeholder="Unit price" class="li-price" step="0.01" oninput="calcTotal(this)">
                        <div class="li-total">$0</div>
                        <button type="button" class="btn-remove" onclick="removeLine(this)" title="Remove">&times;</button>
                    </div>
                </div>
                <button type="button" class="btn-add-line" onclick="addLine()">+ Add Line Item</button>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Expiry Date</label>
                    <input type="date" name="expiry" required>
                </div>
                <div class="form-group">
                    <label>Follow-Up Date</label>
                    <input type="date" name="follow_up_date">
                </div>
            </div>
            <div class="form-group">
                <label>Notes / Terms</label>
                <textarea name="notes" placeholder="Payment terms, conditions, validity..." style="min-height:60px"></textarea>
            </div>
            <div class="modal-actions">
                <button type="button" class="btn-secondary" onclick="closeCreateModal()">Cancel</button>
                <button type="submit" class="btn-gold" id="quoteSubmitBtn">Create Quote</button>
            </div>
        </form>
    </div>
</div>

<!-- Send Quote Modal -->
<div class="modal-overlay" id="sendModal">
    <div class="modal" style="width:460px;">
        <h2>Send Quote</h2>
        <input type="hidden" id="sendQuoteId">
        <div class="send-modal-group">
            <div class="form-group">
                <label>Send Method</label>
                <select id="sendMethod">
                    <option value="email">Email</option>
                    <option value="hand_delivered">Hand-Delivered</option>
                    <option value="mail">Mail</option>
                    <option value="fax">Fax</option>
                </select>
            </div>
            <div class="form-group">
                <label>Follow-Up Date</label>
                <input type="date" id="sendFollowUp">
            </div>
        </div>
        <div class="modal-actions">
            <button type="button" class="btn-secondary" onclick="closeSendModal()">Cancel</button>
            <button type="button" class="btn-gold" onclick="doSendQuote()">Mark as Sent</button>
        </div>
    </div>
</div>

<!-- Revision History Modal -->
<div class="modal-overlay" id="revisionModal">
    <div class="modal" style="width:500px;">
        <h2>Revision History</h2>
        <div id="revisionContent"></div>
        <div class="modal-actions">
            <button type="button" class="btn-secondary" onclick="closeRevisionModal()">Close</button>
        </div>
    </div>
</div>

<script>
let allQuotes = [];

function formatCurrency(val) {
    if (val == null) return '$0';
    return '$' + Number(val).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
function formatCurrencyShort(val) {
    if (val == null) return '$0';
    const n = Number(val);
    if (n >= 1000000) return '$' + (n/1000000).toFixed(1) + 'M';
    if (n >= 1000) return '$' + (n/1000).toFixed(1) + 'K';
    return '$' + n.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}
function formatDate(d) {
    if (!d) return '--';
    const dt = new Date(d);
    if (isNaN(dt)) return d;
    return dt.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function isExpired(expiry) {
    if (!expiry) return false;
    return new Date(expiry) < new Date();
}

function getEffectiveStatus(q) {
    let s = (q.status || 'draft').toLowerCase();
    if (s === 'sent' && isExpired(q.expiry)) return 'expired';
    return s;
}

function statusBadge(q) {
    const s = getEffectiveStatus(q);
    const labels = { draft:'Draft', sent:'Sent', revised:'Revised', accepted:'Accepted', rejected:'Rejected', expired:'Expired' };
    let extra = '';
    if (q.revision && q.revision > 1) extra = '<span class="revision-tag">Rev ' + q.revision + '</span>';
    return '<span class="badge badge-' + s + '">' + (labels[s] || s) + '</span>' + extra;
}

function updateStats(quotes) {
    document.getElementById('stat-total').textContent = quotes.length;
    const pending = quotes.filter(q => getEffectiveStatus(q) === 'sent').length;
    document.getElementById('stat-pending').textContent = pending;
    const accepted = quotes.filter(q => getEffectiveStatus(q) === 'accepted').length;
    document.getElementById('stat-accepted').textContent = accepted;
    const totalVal = quotes.reduce((s, q) => s + (Number(q.amount) || 0), 0);
    document.getElementById('stat-value').textContent = formatCurrencyShort(totalVal);
}

function renderTable(quotes) {
    const tbody = document.getElementById('quotesTableBody');
    if (!quotes.length) {
        tbody.innerHTML = '<tr><td colspan="8" class="empty-state"><h3>No quotes found</h3><p>Create your first sales quote to get started</p></td></tr>';
        return;
    }
    tbody.innerHTML = quotes.map(q => {
        const es = getEffectiveStatus(q);
        const isActive = ['draft','sent','revised'].includes(es);
        return '<tr>' +
            '<td><span class="quote-num">' + (q.quote_number || q.id || '--') + '</span></td>' +
            '<td style="font-weight:600">' + (q.customer || '--') + '</td>' +
            '<td style="color:var(--tf-muted);max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">' + (q.description || '--') + '</td>' +
            '<td style="font-weight:700">' + formatCurrency(q.amount) + '</td>' +
            '<td>' + (q.sent_date ? '<div style="font-size:13px">' + formatDate(q.sent_date) + '</div><div class="sent-info">' + (q.send_method || '') + '</div>' : '<span style="color:var(--tf-muted)">Not sent</span>') + '</td>' +
            '<td style="color:var(--tf-muted);font-size:13px">' + (q.follow_up_date ? formatDate(q.follow_up_date) : '--') + '</td>' +
            '<td>' + statusBadge(q) + '</td>' +
            '<td>' + renderActions(q, es) + '</td>' +
            '</tr>';
    }).join('');
}

function renderActions(q, es) {
    let html = '';
    if (es === 'draft') {
        html += '<button class="btn-sm btn-send" onclick="openSendModal(\'' + q.id + '\')">Send</button> ';
    }
    if (['sent','revised'].includes(es)) {
        html += '<button class="btn-sm btn-accept" onclick="updateQuoteStatus(\'' + q.id + '\',\'accepted\')">Accept</button> ';
        html += '<button class="btn-sm btn-reject" onclick="updateQuoteStatus(\'' + q.id + '\',\'rejected\')">Reject</button> ';
    }
    if (['sent','revised','rejected','expired'].includes(es)) {
        html += '<button class="btn-sm btn-revise" onclick="reviseQuote(\'' + q.id + '\')">Revise</button> ';
    }
    if ((q.revisions || []).length > 0) {
        html += '<button class="btn-sm" style="background:rgba(255,255,255,0.04);color:var(--tf-muted)" onclick="showRevisions(\'' + q.id + '\')">History</button>';
    }
    return html;
}

function applyFilters() {
    const q = (document.getElementById('searchInput').value || '').toLowerCase();
    const status = document.getElementById('statusFilter').value;
    let filtered = allQuotes.filter(qt => {
        if (q && !(qt.customer||'').toLowerCase().includes(q) && !(qt.description||'').toLowerCase().includes(q) && !(qt.quote_number||'').toLowerCase().includes(q)) return false;
        if (status) {
            const es = getEffectiveStatus(qt);
            if (es !== status) return false;
        }
        return true;
    });
    renderTable(filtered);
}
function filterByStatus(s) { document.getElementById('statusFilter').value = s; applyFilters(); }

// --- Create Modal ---
function openCreateModal(prefill) {
    document.getElementById('editQuoteId').value = '';
    document.getElementById('quoteModalTitle').textContent = 'Create Sales Quote';
    document.getElementById('quoteSubmitBtn').textContent = 'Create Quote';
    document.getElementById('createQuoteForm').reset();
    const expiryInput = document.querySelector('input[name="expiry"]');
    const fuInput = document.querySelector('input[name="follow_up_date"]');
    const d = new Date(); d.setDate(d.getDate() + 30);
    expiryInput.value = d.toISOString().split('T')[0];
    const fu = new Date(); fu.setDate(fu.getDate() + 7);
    fuInput.value = fu.toISOString().split('T')[0];
    resetLineItems();
    if (prefill) {
        if (prefill.customer) document.querySelector('[name="customer"]').value = prefill.customer;
        if (prefill.description) document.querySelector('[name="description"]').value = prefill.description;
        if (prefill.email) document.querySelector('[name="email"]').value = prefill.email;
        if (prefill.line_items) {
            document.getElementById('lineItems').innerHTML = '';
            prefill.line_items.forEach(li => addLine(li.description, li.quantity, li.unit_price));
        }
    }
    document.getElementById('createQuoteModal').classList.add('active');
}
function closeCreateModal() { document.getElementById('createQuoteModal').classList.remove('active'); }

function resetLineItems() {
    document.getElementById('lineItems').innerHTML = '<div class="line-item">' +
        '<input type="text" placeholder="Item description" class="li-desc">' +
        '<input type="number" placeholder="Qty" class="li-qty" value="1" min="1" oninput="calcTotal(this)">' +
        '<input type="number" placeholder="Unit price" class="li-price" step="0.01" oninput="calcTotal(this)">' +
        '<div class="li-total">$0</div>' +
        '<button type="button" class="btn-remove" onclick="removeLine(this)" title="Remove">&times;</button></div>';
}

function addLine(desc, qty, price) {
    const container = document.getElementById('lineItems');
    const div = document.createElement('div');
    div.className = 'line-item';
    div.innerHTML = '<input type="text" placeholder="Item description" class="li-desc" value="' + (desc||'') + '">' +
        '<input type="number" placeholder="Qty" class="li-qty" value="' + (qty||1) + '" min="1" oninput="calcTotal(this)">' +
        '<input type="number" placeholder="Unit price" class="li-price" step="0.01" value="' + (price||'') + '" oninput="calcTotal(this)">' +
        '<div class="li-total">$0</div>' +
        '<button type="button" class="btn-remove" onclick="removeLine(this)" title="Remove">&times;</button>';
    container.appendChild(div);
    if (price) calcTotal(div.querySelector('.li-price'));
}

function removeLine(btn) {
    const items = document.querySelectorAll('.line-item');
    if (items.length > 1) btn.parentElement.remove();
}

function calcTotal(el) {
    const row = el.closest('.line-item');
    const qty = Number(row.querySelector('.li-qty').value) || 0;
    const price = Number(row.querySelector('.li-price').value) || 0;
    row.querySelector('.li-total').textContent = formatCurrency(qty * price);
}

async function submitQuote(e) {
    e.preventDefault();
    const form = e.target;
    const fd = new FormData(form);
    const data = Object.fromEntries(fd);
    const lines = [];
    document.querySelectorAll('.line-item').forEach(li => {
        const desc = li.querySelector('.li-desc').value;
        const qty = Number(li.querySelector('.li-qty').value) || 1;
        const price = Number(li.querySelector('.li-price').value) || 0;
        if (desc || price) lines.push({ description: desc, quantity: qty, unit_price: price, total: qty * price });
    });
    data.line_items = lines;
    data.amount = lines.reduce((s, l) => s + l.total, 0);
    data.status = 'draft';
    data.created_at = new Date().toISOString();

    const editId = document.getElementById('editQuoteId').value;
    if (editId) {
        data.id = editId;
        try {
            await fetch('/api/sales/quotes', { method: 'PUT', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data) });
            closeCreateModal(); form.reset(); loadQuotes();
        } catch(err) { console.error(err); }
    } else {
        try {
            const res = await fetch('/api/sales/quotes', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data) });
            if (res.ok) { closeCreateModal(); form.reset(); resetLineItems(); loadQuotes(); }
        } catch(err) { console.error(err); }
    }
}

// --- Status Actions ---
async function updateQuoteStatus(id, newStatus) {
    const data = { id, status: newStatus };
    if (newStatus === 'accepted') data.accepted_at = new Date().toISOString();
    if (newStatus === 'rejected') data.rejected_at = new Date().toISOString();
    try {
        await fetch('/api/sales/quotes', { method: 'PUT', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data) });
        loadQuotes();
    } catch(e) { console.error(e); }
}

// --- Send ---
function openSendModal(id) {
    document.getElementById('sendQuoteId').value = id;
    const fu = new Date(); fu.setDate(fu.getDate() + 7);
    document.getElementById('sendFollowUp').value = fu.toISOString().split('T')[0];
    document.getElementById('sendModal').classList.add('active');
}
function closeSendModal() { document.getElementById('sendModal').classList.remove('active'); }

async function doSendQuote() {
    const id = document.getElementById('sendQuoteId').value;
    const data = {
        id, status: 'sent',
        sent_date: new Date().toISOString(),
        send_method: document.getElementById('sendMethod').value,
        follow_up_date: document.getElementById('sendFollowUp').value,
    };
    try {
        await fetch('/api/sales/quotes', { method: 'PUT', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data) });
        closeSendModal(); loadQuotes();
    } catch(e) { console.error(e); }
}

// --- Revise ---
function reviseQuote(id) {
    const q = allQuotes.find(qt => qt.id === id);
    if (!q) return;
    openCreateModal({
        customer: q.customer, description: q.description + ' (Revised)',
        email: q.email, line_items: q.line_items || []
    });
    // Mark original as revised
    updateQuoteStatus(id, 'revised');
}

// --- Revision History ---
function showRevisions(id) {
    const q = allQuotes.find(qt => qt.id === id);
    if (!q) return;
    const revs = q.revisions || [];
    let html = '<div class="revision-list">';
    if (revs.length) {
        revs.forEach((r, i) => {
            html += '<div class="revision-item"><span class="rev-version">v' + (i+1) + '</span><span class="rev-amount">' + formatCurrency(r.amount) + '</span><span class="rev-date">' + formatDate(r.date) + '</span></div>';
        });
    } else {
        html += '<div style="color:var(--tf-muted);text-align:center;padding:20px;">No revision history available</div>';
    }
    html += '</div>';
    document.getElementById('revisionContent').innerHTML = html;
    document.getElementById('revisionModal').classList.add('active');
}
function closeRevisionModal() { document.getElementById('revisionModal').classList.remove('active'); }

// --- Load ---
async function loadQuotes() {
    try {
        const res = await fetch('/api/sales/quotes');
        if (!res.ok) throw new Error('API error');
        const data = await res.json();
        allQuotes = Array.isArray(data) ? data : (data.quotes || data.data || []);
    } catch(err) { console.warn('Could not load quotes:', err); allQuotes = []; }
    updateStats(allQuotes);
    applyFilters();
}

['createQuoteModal','sendModal','revisionModal'].forEach(id => {
    document.getElementById(id).addEventListener('click', function(e) { if (e.target === this) this.classList.remove('active'); });
});

loadQuotes();
</script>
"""
