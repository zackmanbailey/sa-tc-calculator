"""
TitanForge v4 — Sales Quotes
==============================
Manage pre-project sales quotes for prospective customers.
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
    }
    .quotes-container {
        max-width: 1400px;
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
    .stat-orange .value { color: #fb923c; }

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
    .sq-table {
        width: 100%; border-collapse: collapse; font-size: 14px;
    }
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
    .badge-accepted { background: rgba(16,185,129,0.15); color: #34d399; }
    .badge-declined { background: rgba(239,68,68,0.15); color: #f87171; }
    .badge-expired { background: rgba(249,115,22,0.15); color: #fb923c; }

    .expiry-warn { color: var(--tf-red); font-weight: 600; }

    .empty-state {
        text-align: center; padding: 60px 20px; color: var(--tf-muted);
    }
    .empty-state svg { margin-bottom: 16px; opacity: 0.4; }
    .empty-state h3 { color: var(--tf-text); margin-bottom: 8px; }

    .actions-cell { display: flex; gap: 6px; }
    .btn-icon {
        background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06);
        border-radius: 6px; width: 32px; height: 32px; display: inline-flex;
        align-items: center; justify-content: center; cursor: pointer; color: var(--tf-muted);
        transition: all 0.15s;
    }
    .btn-icon:hover { color: var(--tf-text); border-color: rgba(255,255,255,0.15); }

    /* Modal */
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

    /* Line items in modal */
    .line-items { margin-bottom: 16px; }
    .line-item {
        display: grid; grid-template-columns: 2fr 1fr 1fr auto; gap: 8px;
        align-items: center; margin-bottom: 8px;
    }
    .line-item input {
        background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px; padding: 8px 12px; color: var(--tf-text); font-size: 13px;
        box-sizing: border-box;
    }
    .btn-remove {
        background: none; border: none; color: var(--tf-red); cursor: pointer;
        font-size: 18px; padding: 4px; line-height: 1;
    }
    .btn-add-line {
        background: none; border: 1px dashed rgba(255,255,255,0.1);
        border-radius: 8px; padding: 8px 16px; color: var(--tf-muted);
        font-size: 13px; cursor: pointer; width: 100%;
    }
    .btn-add-line:hover { color: var(--tf-text); border-color: rgba(255,255,255,0.2); }

/* ── Responsive ── */
@media (max-width: 768px) {
    .page-header h1 { font-size: 22px; }
    .toolbar { flex-direction: column; align-items: stretch; }
    .toolbar input[type="text"] { width: 100%; }
    .stat-row { grid-template-columns: 1fr 1fr; gap: 10px; }
    .modal-overlay .modal, .modal { width: 95%; max-width: 95vw; margin: 20px auto; padding: 20px; }
    .form-row { grid-template-columns: 1fr; }
    .sq-table { display: block; overflow-x: auto; -webkit-overflow-scrolling: touch; }
    .line-items { display: block; overflow-x: auto; }
}
@media (max-width: 480px) {
    .stat-row { grid-template-columns: 1fr; }
    .toolbar { gap: 8px; }
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
                <option value="accepted">Accepted</option>
                <option value="declined">Declined</option>
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
                    <th>Date</th>
                    <th>Expiry</th>
                    <th>Status</th>
                    <th></th>
                </tr>
            </thead>
            <tbody id="quotesTableBody">
                <tr><td colspan="8" class="empty-state">Loading...</td></tr>
            </tbody>
        </table>
    </div>
</div>

<!-- Create Quote Modal -->
<div class="modal-overlay" id="createQuoteModal">
    <div class="modal">
        <h2>Create Sales Quote</h2>
        <form id="createQuoteForm" onsubmit="submitQuote(event)">
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
                        <input type="number" placeholder="Qty" class="li-qty" value="1" min="1">
                        <input type="number" placeholder="Unit price" class="li-price" step="0.01">
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
                    <label>Status</label>
                    <select name="status">
                        <option value="draft">Draft</option>
                        <option value="sent">Sent</option>
                    </select>
                </div>
            </div>
            <div class="form-group">
                <label>Notes</label>
                <textarea name="notes" placeholder="Internal notes, terms, conditions..." style="min-height:60px"></textarea>
            </div>
            <div class="modal-actions">
                <button type="button" class="btn-secondary" onclick="closeCreateModal()">Cancel</button>
                <button type="submit" class="btn-gold">Create Quote</button>
            </div>
        </form>
    </div>
</div>

<script>
let allQuotes = [];

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

function isExpiringSoon(expiry) {
    if (!expiry) return false;
    const exp = new Date(expiry);
    const daysLeft = (exp - Date.now()) / 86400000;
    return daysLeft >= 0 && daysLeft <= 7;
}

function isExpired(expiry) {
    if (!expiry) return false;
    return new Date(expiry) < new Date();
}

function statusBadge(status, expiry) {
    let s = (status || 'draft').toLowerCase();
    if (s === 'sent' && isExpired(expiry)) s = 'expired';
    const labels = { draft:'Draft', sent:'Sent', accepted:'Accepted', declined:'Declined', expired:'Expired' };
    return '<span class="badge badge-' + s + '">' + (labels[s] || s) + '</span>';
}

function updateStats(quotes) {
    document.getElementById('stat-total').textContent = quotes.length;
    const pending = quotes.filter(q => (q.status||'').toLowerCase() === 'sent' && !isExpired(q.expiry)).length;
    document.getElementById('stat-pending').textContent = pending;
    const accepted = quotes.filter(q => (q.status||'').toLowerCase() === 'accepted').length;
    document.getElementById('stat-accepted').textContent = accepted;
    const totalVal = quotes.reduce((s, q) => s + (Number(q.amount) || 0), 0);
    document.getElementById('stat-value').textContent = formatCurrency(totalVal);
}

function renderTable(quotes) {
    const tbody = document.getElementById('quotesTableBody');
    if (!quotes.length) {
        tbody.innerHTML = '<tr><td colspan="8" class="empty-state">' +
            '<svg width="48" height="48" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" stroke-width="1.5" d="M9 12h6m-3-3v6m-7 4h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>' +
            '<h3>No quotes found</h3><p>Create your first sales quote to get started</p></td></tr>';
        return;
    }
    tbody.innerHTML = quotes.map(q => {
        const expiryClass = isExpiringSoon(q.expiry) || isExpired(q.expiry) ? ' expiry-warn' : '';
        return '<tr>' +
            '<td><span class="quote-num">' + (q.quote_number || q.id || '--') + '</span></td>' +
            '<td style="font-weight:600">' + (q.customer || '--') + '</td>' +
            '<td style="color:var(--tf-muted);max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">' + (q.description || '--') + '</td>' +
            '<td style="font-weight:700">' + formatCurrency(q.amount) + '</td>' +
            '<td style="color:var(--tf-muted)">' + formatDate(q.created_at || q.date) + '</td>' +
            '<td class="' + expiryClass + '">' + formatDate(q.expiry) + '</td>' +
            '<td>' + statusBadge(q.status, q.expiry) + '</td>' +
            '<td><div class="actions-cell">' +
                '<button class="btn-icon" title="View" onclick="viewQuote(\'' + (q.id||'') + '\')"><svg width="14" height="14" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke="currentColor" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg></button>' +
                '<button class="btn-icon" title="Duplicate" onclick="duplicateQuote(\'' + (q.id||'') + '\')"><svg width="14" height="14" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg></button>' +
            '</div></td>' +
            '</tr>';
    }).join('');
}

function applyFilters() {
    const q = (document.getElementById('searchInput').value || '').toLowerCase();
    const status = document.getElementById('statusFilter').value;
    let filtered = allQuotes.filter(qt => {
        if (q && !(qt.customer||'').toLowerCase().includes(q) && !(qt.description||'').toLowerCase().includes(q) && !(qt.quote_number||'').toLowerCase().includes(q)) return false;
        if (status && (qt.status||'').toLowerCase() !== status) return false;
        return true;
    });
    renderTable(filtered);
}

function filterByStatus(s) {
    document.getElementById('statusFilter').value = s;
    applyFilters();
}

function openCreateModal() {
    document.getElementById('createQuoteModal').classList.add('active');
    // Default expiry to 30 days from now
    const expiryInput = document.querySelector('input[name="expiry"]');
    if (expiryInput && !expiryInput.value) {
        const d = new Date(); d.setDate(d.getDate() + 30);
        expiryInput.value = d.toISOString().split('T')[0];
    }
}
function closeCreateModal() { document.getElementById('createQuoteModal').classList.remove('active'); }

function addLine() {
    const container = document.getElementById('lineItems');
    const div = document.createElement('div');
    div.className = 'line-item';
    div.innerHTML = '<input type="text" placeholder="Item description" class="li-desc">' +
        '<input type="number" placeholder="Qty" class="li-qty" value="1" min="1">' +
        '<input type="number" placeholder="Unit price" class="li-price" step="0.01">' +
        '<button type="button" class="btn-remove" onclick="removeLine(this)" title="Remove">&times;</button>';
    container.appendChild(div);
}

function removeLine(btn) {
    const items = document.querySelectorAll('.line-item');
    if (items.length > 1) btn.parentElement.remove();
}

async function submitQuote(e) {
    e.preventDefault();
    const form = e.target;
    const fd = new FormData(form);
    const data = Object.fromEntries(fd);

    // Collect line items
    const lines = [];
    document.querySelectorAll('.line-item').forEach(li => {
        const desc = li.querySelector('.li-desc').value;
        const qty = Number(li.querySelector('.li-qty').value) || 1;
        const price = Number(li.querySelector('.li-price').value) || 0;
        if (desc || price) lines.push({ description: desc, quantity: qty, unit_price: price, total: qty * price });
    });
    data.line_items = lines;
    data.amount = lines.reduce((s, l) => s + l.total, 0);
    data.created_at = new Date().toISOString();

    try {
        const res = await fetch('/api/sales/quotes', {
            method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data)
        });
        if (res.ok) {
            closeCreateModal();
            form.reset();
            document.getElementById('lineItems').innerHTML = '<div class="line-item">' +
                '<input type="text" placeholder="Item description" class="li-desc">' +
                '<input type="number" placeholder="Qty" class="li-qty" value="1" min="1">' +
                '<input type="number" placeholder="Unit price" class="li-price" step="0.01">' +
                '<button type="button" class="btn-remove" onclick="removeLine(this)" title="Remove">&times;</button></div>';
            loadQuotes();
        }
    } catch(err) {
        console.error('Failed to create quote:', err);
    }
}

function viewQuote(id) {
    // Navigate to quote detail if route exists, otherwise log
    if (id) window.location.href = '/sales/quotes/' + id;
}

function duplicateQuote(id) {
    const q = allQuotes.find(qt => String(qt.id) === id);
    if (!q) return;
    openCreateModal();
    const form = document.getElementById('createQuoteForm');
    if (q.customer) form.querySelector('[name="customer"]').value = q.customer;
    if (q.description) form.querySelector('[name="description"]').value = q.description;
    if (q.email) form.querySelector('[name="email"]').value = q.email;
}

async function loadQuotes() {
    try {
        const res = await fetch('/api/sales/quotes');
        if (!res.ok) throw new Error('API error');
        const data = await res.json();
        allQuotes = Array.isArray(data) ? data : (data.quotes || data.data || []);
    } catch(err) {
        console.warn('Could not load quotes:', err);
        allQuotes = [];
    }
    updateStats(allQuotes);
    applyFilters();
}

// Close modal on overlay click
document.getElementById('createQuoteModal').addEventListener('click', function(e) {
    if (e.target === this) closeCreateModal();
});

loadQuotes();
</script>
"""
