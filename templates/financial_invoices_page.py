"""
TitanForge v4 — Invoice Management (Production)
==================================================
Full invoice lifecycle: draft -> sent -> viewed -> paid -> overdue
with line items, payment terms, and professional detail view.
"""

FINANCIAL_INVOICES_PAGE_HTML = r"""
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
    }
    .inv-container {
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
    .stat-purple .value { color: var(--tf-purple); }

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
    .btn-blue {
        background: var(--tf-blue); color: #fff; border: none; border-radius: 8px;
        padding: 8px 16px; font-weight: 600; font-size: 13px; cursor: pointer;
    }
    .btn-blue:hover { opacity: 0.9; }
    .btn-green {
        background: var(--tf-green); color: #fff; border: none; border-radius: 8px;
        padding: 8px 16px; font-weight: 600; font-size: 13px; cursor: pointer;
    }
    .btn-green:hover { opacity: 0.9; }
    .btn-sm {
        padding: 5px 12px; font-size: 12px; border-radius: 6px; border: none;
        font-weight: 600; cursor: pointer; transition: opacity 0.15s;
    }
    .btn-sm:hover { opacity: 0.85; }

    .table-card {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06); overflow: hidden;
    }
    .inv-table { width: 100%; border-collapse: collapse; font-size: 14px; }
    .inv-table th {
        text-align: left; padding: 14px 16px; font-size: 11px;
        text-transform: uppercase; letter-spacing: 0.5px; color: var(--tf-muted);
        border-bottom: 1px solid rgba(255,255,255,0.06); font-weight: 600;
    }
    .inv-table td {
        padding: 14px 16px; border-bottom: 1px solid rgba(255,255,255,0.04); vertical-align: middle;
    }
    .inv-table tr:hover { background: rgba(255,255,255,0.02); cursor: pointer; }
    .inv-table tr:last-child td { border-bottom: none; }

    .inv-num { font-weight: 700; color: var(--tf-gold); font-family: 'JetBrains Mono', monospace; }

    .badge {
        display: inline-block; padding: 4px 10px; border-radius: 20px;
        font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;
        cursor: pointer;
    }
    .badge-draft { background: rgba(148,163,184,0.15); color: #94a3b8; }
    .badge-sent { background: rgba(59,130,246,0.15); color: #60a5fa; }
    .badge-viewed { background: rgba(167,139,250,0.15); color: #a78bfa; }
    .badge-paid { background: rgba(16,185,129,0.15); color: #34d399; }
    .badge-overdue { background: rgba(239,68,68,0.15); color: #f87171; }
    .badge-partial { background: rgba(249,115,22,0.15); color: #fb923c; }

    .overdue-days { color: var(--tf-red); font-size: 11px; font-weight: 600; }

    .empty-state { text-align: center; padding: 60px 20px; color: var(--tf-muted); }
    .empty-state h3 { color: var(--tf-text); margin-bottom: 8px; }

    /* Modal styles */
    .modal-overlay {
        display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.6); z-index: 9999; justify-content: center; align-items: center;
    }
    .modal-overlay.active { display: flex; }
    .modal {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.1); padding: 32px;
        width: 720px; max-width: 95vw; max-height: 90vh; overflow-y: auto;
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
    .form-row-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 24px; }
    .btn-secondary {
        background: transparent; border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px; padding: 10px 20px; color: var(--tf-muted);
        font-weight: 600; font-size: 14px; cursor: pointer;
    }
    .btn-secondary:hover { color: var(--tf-text); border-color: rgba(255,255,255,0.2); }

    /* Line items */
    .line-items-header {
        display: grid; grid-template-columns: 3fr 1fr 1fr 1fr auto; gap: 8px;
        padding: 8px 0; font-size: 11px; color: var(--tf-muted); text-transform: uppercase;
        letter-spacing: 0.5px; font-weight: 600; border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .line-item {
        display: grid; grid-template-columns: 3fr 1fr 1fr 1fr auto; gap: 8px;
        align-items: center; padding: 6px 0;
    }
    .line-item input {
        background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.1);
        border-radius: 6px; padding: 8px 10px; color: var(--tf-text); font-size: 13px;
        box-sizing: border-box; width: 100%;
    }
    .line-item .li-total { font-weight: 600; color: var(--tf-gold); font-size: 13px; padding: 8px 4px; }
    .btn-remove { background: none; border: none; color: var(--tf-red); cursor: pointer; font-size: 18px; padding: 4px; }
    .btn-add-line {
        background: none; border: 1px dashed rgba(255,255,255,0.1);
        border-radius: 8px; padding: 8px 16px; color: var(--tf-muted);
        font-size: 13px; cursor: pointer; width: 100%; margin-top: 8px;
    }
    .btn-add-line:hover { color: var(--tf-text); border-color: rgba(255,255,255,0.2); }
    .subtotal-row { display: flex; justify-content: flex-end; gap: 20px; margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.06); }
    .subtotal-row span { font-size: 14px; }
    .subtotal-row .st-label { color: var(--tf-muted); }
    .subtotal-row .st-value { font-weight: 700; color: var(--tf-gold); }

    /* Detail View Modal */
    .invoice-detail { padding: 0; }
    .inv-detail-header {
        display: flex; justify-content: space-between; align-items: flex-start;
        padding: 24px 32px; border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .inv-company { font-size: 22px; font-weight: 800; color: var(--tf-gold); }
    .inv-company-sub { font-size: 13px; color: var(--tf-muted); margin-top: 4px; }
    .inv-detail-meta { text-align: right; }
    .inv-detail-meta .inv-number { font-size: 18px; font-weight: 700; color: var(--tf-text); }
    .inv-detail-body { padding: 24px 32px; }
    .inv-bill-to {
        display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 24px;
    }
    .inv-bill-section h4 { font-size: 11px; color: var(--tf-muted); text-transform: uppercase; letter-spacing: 0.5px; margin: 0 0 8px 0; }
    .inv-bill-section p { font-size: 14px; margin: 2px 0; }
    .inv-items-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
    .inv-items-table th {
        text-align: left; padding: 10px 12px; font-size: 11px;
        text-transform: uppercase; color: var(--tf-muted); border-bottom: 1px solid rgba(255,255,255,0.08);
    }
    .inv-items-table th:last-child, .inv-items-table td:last-child { text-align: right; }
    .inv-items-table td { padding: 10px 12px; border-bottom: 1px solid rgba(255,255,255,0.04); }
    .inv-totals { display: flex; flex-direction: column; align-items: flex-end; gap: 6px; margin-bottom: 20px; }
    .inv-totals .tot-row { display: flex; gap: 40px; font-size: 14px; }
    .inv-totals .tot-label { color: var(--tf-muted); min-width: 100px; text-align: right; }
    .inv-totals .tot-value { font-weight: 600; min-width: 100px; text-align: right; }
    .inv-totals .tot-grand { font-size: 18px; font-weight: 800; color: var(--tf-gold); border-top: 2px solid rgba(255,255,255,0.1); padding-top: 8px; }
    .inv-notes { background: rgba(255,255,255,0.02); border-radius: 8px; padding: 16px; margin-bottom: 20px; }
    .inv-notes h4 { font-size: 12px; color: var(--tf-muted); text-transform: uppercase; margin: 0 0 8px 0; }
    .inv-notes p { font-size: 13px; color: var(--tf-text); margin: 0; white-space: pre-wrap; }
    .inv-detail-actions {
        display: flex; gap: 10px; padding: 20px 32px; border-top: 1px solid rgba(255,255,255,0.06);
        justify-content: flex-end; flex-wrap: wrap;
    }

/* Responsive */
@media (max-width: 768px) {
    .page-header h1 { font-size: 22px; }
    .toolbar { flex-direction: column; align-items: stretch; }
    .toolbar input[type="text"] { width: 100%; }
    .stat-row { grid-template-columns: 1fr 1fr; gap: 10px; }
    .modal-overlay .modal, .modal { width: 95%; max-width: 95vw; margin: 20px auto; padding: 20px; }
    .form-row, .form-row-3 { grid-template-columns: 1fr; }
    .inv-table { display: block; overflow-x: auto; -webkit-overflow-scrolling: touch; }
    .line-items-header, .line-item { grid-template-columns: 2fr 1fr 1fr auto; }
    .inv-bill-to { grid-template-columns: 1fr; }
}
@media (max-width: 480px) {
    .stat-row { grid-template-columns: 1fr; }
    .toolbar { gap: 8px; }
}
</style>

<div class="inv-container">
    <div class="page-header">
        <h1>Invoices</h1>
        <p>Create, send, and track invoices for customers and projects</p>
    </div>

    <div class="stat-row">
        <div class="stat-card stat-blue" onclick="filterByStatus('')">
            <div class="label">Total Invoices</div>
            <div class="value" id="stat-total">--</div>
            <div class="sub">All time</div>
        </div>
        <div class="stat-card stat-gold" onclick="filterByStatus('sent')">
            <div class="label">Outstanding</div>
            <div class="value" id="stat-outstanding">--</div>
            <div class="sub">Awaiting payment</div>
        </div>
        <div class="stat-card stat-green" onclick="filterByStatus('paid')">
            <div class="label">Collected</div>
            <div class="value" id="stat-paid">--</div>
            <div class="sub">Payments received</div>
        </div>
        <div class="stat-card stat-red" onclick="filterByStatus('overdue')">
            <div class="label">Overdue</div>
            <div class="value" id="stat-overdue">--</div>
            <div class="sub" id="stat-overdue-count">0 invoices past due</div>
        </div>
        <div class="stat-card stat-purple" onclick="filterByStatus('draft')">
            <div class="label">Drafts</div>
            <div class="value" id="stat-drafts">--</div>
            <div class="sub">Not yet sent</div>
        </div>
    </div>

    <div class="toolbar">
        <div class="toolbar-left">
            <input type="text" id="searchInput" placeholder="Search invoices..." oninput="applyFilters()">
            <select id="statusFilter" onchange="applyFilters()">
                <option value="">All Statuses</option>
                <option value="draft">Draft</option>
                <option value="sent">Sent</option>
                <option value="viewed">Viewed</option>
                <option value="paid">Paid</option>
                <option value="overdue">Overdue</option>
            </select>
        </div>
        <button class="btn-gold" onclick="openCreateModal()">+ Create Invoice</button>
    </div>

    <div class="table-card">
        <table class="inv-table">
            <thead>
                <tr>
                    <th>Invoice #</th>
                    <th>Customer</th>
                    <th>Project</th>
                    <th>Amount</th>
                    <th>Terms</th>
                    <th>Date</th>
                    <th>Due Date</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody id="invoicesBody">
                <tr><td colspan="9" class="empty-state">Loading...</td></tr>
            </tbody>
        </table>
    </div>
</div>

<!-- Create Invoice Modal -->
<div class="modal-overlay" id="createModal">
    <div class="modal">
        <h2 id="createModalTitle">Create Invoice</h2>
        <form id="invoiceForm" onsubmit="submitInvoice(event)">
            <input type="hidden" id="editInvoiceId" value="">
            <div class="form-row">
                <div class="form-group">
                    <label>Project</label>
                    <select name="project_id" id="projectSelect" onchange="onProjectSelect()">
                        <option value="">-- Select a project --</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Customer</label>
                    <input type="text" name="customer" id="customerInput" required placeholder="Customer or company">
                </div>
            </div>
            <div class="form-group">
                <label>Customer Email</label>
                <input type="email" name="customer_email" placeholder="billing@company.com">
            </div>
            <div class="form-row-3">
                <div class="form-group">
                    <label>Payment Terms</label>
                    <select name="terms" id="termsSelect" onchange="updateDueFromTerms()">
                        <option value="net_30">Net 30</option>
                        <option value="net_60">Net 60</option>
                        <option value="due_on_receipt">Due on Receipt</option>
                        <option value="net_15">Net 15</option>
                        <option value="net_45">Net 45</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Invoice Date</label>
                    <input type="date" name="invoice_date" id="invoiceDateInput">
                </div>
                <div class="form-group">
                    <label>Due Date</label>
                    <input type="date" name="due_date" id="dueDateInput" required>
                </div>
            </div>

            <div class="form-group">
                <label>Line Items</label>
                <div class="line-items-header">
                    <span>Description</span><span>Qty</span><span>Unit Price</span><span>Total</span><span></span>
                </div>
                <div id="lineItemsContainer">
                    <div class="line-item">
                        <input type="text" placeholder="Item description" class="li-desc">
                        <input type="number" placeholder="1" class="li-qty" value="1" min="1" oninput="calcLineTotal(this)">
                        <input type="number" placeholder="0.00" class="li-price" step="0.01" oninput="calcLineTotal(this)">
                        <div class="li-total">$0</div>
                        <button type="button" class="btn-remove" onclick="removeLine(this)">&times;</button>
                    </div>
                </div>
                <button type="button" class="btn-add-line" onclick="addLineItem()">+ Add Line Item</button>
                <div class="subtotal-row">
                    <span class="st-label">Subtotal:</span><span class="st-value" id="subtotalDisplay">$0</span>
                </div>
                <div class="subtotal-row" style="margin-top:4px;">
                    <span class="st-label">Tax (%):</span>
                    <input type="number" id="taxRateInput" value="0" min="0" max="100" step="0.1"
                           style="width:60px;background:var(--tf-bg);border:1px solid rgba(255,255,255,0.1);border-radius:6px;padding:4px 8px;color:var(--tf-text);font-size:13px;text-align:right;"
                           oninput="recalcTotals()">
                    <span class="st-value" id="taxDisplay">$0</span>
                </div>
                <div class="subtotal-row" style="margin-top:4px;">
                    <span class="st-label" style="font-weight:700;color:var(--tf-text);">Total:</span>
                    <span class="st-value" style="font-size:18px;" id="grandTotalDisplay">$0</span>
                </div>
            </div>

            <div class="form-group">
                <label>Notes</label>
                <textarea name="notes" placeholder="Payment instructions, terms, or additional notes..."></textarea>
            </div>
            <div class="modal-actions">
                <button type="button" class="btn-secondary" onclick="closeCreateModal()">Cancel</button>
                <button type="submit" class="btn-gold" id="submitBtn">Create Invoice</button>
            </div>
        </form>
    </div>
</div>

<!-- Invoice Detail Modal -->
<div class="modal-overlay" id="detailModal">
    <div class="modal invoice-detail" style="width:800px;">
        <div class="inv-detail-header">
            <div>
                <div class="inv-company">TITAN CARPORTS</div>
                <div class="inv-company-sub">Metal Building Solutions</div>
                <div class="inv-company-sub">info@titancarports.com</div>
            </div>
            <div class="inv-detail-meta">
                <div class="inv-number" id="detailInvNumber">INV-0000</div>
                <div style="margin-top:6px;" id="detailStatus"></div>
            </div>
        </div>
        <div class="inv-detail-body">
            <div class="inv-bill-to">
                <div class="inv-bill-section">
                    <h4>Bill To</h4>
                    <p id="detailCustomer" style="font-weight:600;"></p>
                    <p id="detailCustomerEmail" style="color:var(--tf-muted);font-size:13px;"></p>
                </div>
                <div class="inv-bill-section" style="text-align:right;">
                    <h4>Invoice Details</h4>
                    <p><span style="color:var(--tf-muted);">Invoice Date:</span> <span id="detailDate"></span></p>
                    <p><span style="color:var(--tf-muted);">Due Date:</span> <span id="detailDueDate"></span></p>
                    <p><span style="color:var(--tf-muted);">Terms:</span> <span id="detailTerms"></span></p>
                    <p><span style="color:var(--tf-muted);">Project:</span> <span id="detailProject"></span></p>
                </div>
            </div>
            <table class="inv-items-table">
                <thead><tr><th>Description</th><th>Qty</th><th>Unit Price</th><th>Total</th></tr></thead>
                <tbody id="detailLineItems"></tbody>
            </table>
            <div class="inv-totals" id="detailTotals"></div>
            <div class="inv-notes" id="detailNotesSection" style="display:none;">
                <h4>Notes</h4>
                <p id="detailNotes"></p>
            </div>
            <div id="detailPaymentInfo" style="display:none;background:rgba(16,185,129,0.08);border-radius:8px;padding:16px;margin-bottom:20px;">
                <h4 style="font-size:12px;color:var(--tf-green);text-transform:uppercase;margin:0 0 8px 0;">Payment Received</h4>
                <p id="detailPaymentDetails" style="font-size:14px;margin:0;"></p>
            </div>
        </div>
        <div class="inv-detail-actions" id="detailActions"></div>
    </div>
</div>

<!-- Payment Modal -->
<div class="modal-overlay" id="paymentModal">
    <div class="modal" style="width:440px;">
        <h2>Record Payment</h2>
        <input type="hidden" id="payInvoiceId">
        <div class="form-group">
            <label>Amount Received ($)</label>
            <input type="number" id="payAmount" step="0.01" placeholder="0.00">
        </div>
        <div class="form-group">
            <label>Payment Method</label>
            <select id="payMethod">
                <option value="check">Check</option>
                <option value="ach">ACH / Bank Transfer</option>
                <option value="credit_card">Credit Card</option>
                <option value="wire">Wire Transfer</option>
                <option value="cash">Cash</option>
                <option value="other">Other</option>
            </select>
        </div>
        <div class="form-group">
            <label>Payment Date</label>
            <input type="date" id="payDate">
        </div>
        <div class="form-group">
            <label>Reference / Check #</label>
            <input type="text" id="payReference" placeholder="Optional">
        </div>
        <div class="modal-actions">
            <button type="button" class="btn-secondary" onclick="closePaymentModal()">Cancel</button>
            <button type="button" class="btn-green" onclick="submitPayment()">Record Payment</button>
        </div>
    </div>
</div>

<script>
let allInvoices = [];
let projectsCache = [];

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
function today() { return new Date().toISOString().split('T')[0]; }

const termsLabels = { net_30: 'Net 30', net_60: 'Net 60', due_on_receipt: 'Due on Receipt', net_15: 'Net 15', net_45: 'Net 45' };
const termsDays = { net_30: 30, net_60: 60, due_on_receipt: 0, net_15: 15, net_45: 45 };

function getEffectiveStatus(inv) {
    const s = (inv.status || 'draft').toLowerCase();
    if (s === 'paid') return 'paid';
    if (['sent','viewed'].includes(s) && inv.due_date && new Date(inv.due_date) < new Date()) return 'overdue';
    return s;
}

function daysOverdue(inv) {
    if (!inv.due_date) return 0;
    const diff = Math.floor((Date.now() - new Date(inv.due_date).getTime()) / 86400000);
    return Math.max(0, diff);
}

function statusBadge(inv) {
    const s = getEffectiveStatus(inv);
    const labels = { draft:'Draft', sent:'Sent', viewed:'Viewed', paid:'Paid', overdue:'Overdue', partial:'Partial' };
    let extra = '';
    if (s === 'overdue') extra = '<span class="overdue-days"> (' + daysOverdue(inv) + 'd)</span>';
    return '<span class="badge badge-' + s + '">' + (labels[s] || s) + '</span>' + extra;
}

function updateStats(invoices) {
    document.getElementById('stat-total').textContent = invoices.length;
    const outstanding = invoices.filter(i => ['sent','viewed'].includes(getEffectiveStatus(i)) || getEffectiveStatus(i) === 'overdue');
    document.getElementById('stat-outstanding').textContent = formatCurrencyShort(
        outstanding.reduce((s, i) => s + (Number(i.amount) || 0), 0)
    );
    document.getElementById('stat-paid').textContent = formatCurrencyShort(
        invoices.filter(i => getEffectiveStatus(i) === 'paid').reduce((s, i) => s + (Number(i.amount) || 0), 0)
    );
    const overdue = invoices.filter(i => getEffectiveStatus(i) === 'overdue');
    document.getElementById('stat-overdue').textContent = formatCurrencyShort(
        overdue.reduce((s, i) => s + (Number(i.amount) || 0), 0)
    );
    document.getElementById('stat-overdue-count').textContent = overdue.length + ' invoice' + (overdue.length !== 1 ? 's' : '') + ' past due';
    document.getElementById('stat-drafts').textContent = invoices.filter(i => getEffectiveStatus(i) === 'draft').length;
}

function renderTable(invoices) {
    const tbody = document.getElementById('invoicesBody');
    if (!invoices.length) {
        tbody.innerHTML = '<tr><td colspan="9" class="empty-state"><h3>No invoices found</h3><p>Create your first invoice to start tracking payments</p></td></tr>';
        return;
    }
    tbody.innerHTML = invoices.map(i => {
        const es = getEffectiveStatus(i);
        const dueDateStyle = es === 'overdue' ? 'color:var(--tf-red);font-weight:600' : 'color:var(--tf-muted)';
        return '<tr onclick="viewInvoice(\'' + (i.id||'') + '\')">' +
            '<td><span class="inv-num">' + (i.invoice_number || i.id || '--') + '</span></td>' +
            '<td style="font-weight:600">' + (i.customer || '--') + '</td>' +
            '<td style="color:var(--tf-muted)">' + (i.project_name || i.project || '--') + '</td>' +
            '<td style="font-weight:700">' + formatCurrency(i.amount) + '</td>' +
            '<td style="color:var(--tf-muted);font-size:12px;">' + (termsLabels[i.terms] || i.terms || '--') + '</td>' +
            '<td style="color:var(--tf-muted)">' + formatDate(i.invoice_date || i.created_at || i.date) + '</td>' +
            '<td style="' + dueDateStyle + '">' + formatDate(i.due_date) + '</td>' +
            '<td>' + statusBadge(i) + '</td>' +
            '<td onclick="event.stopPropagation()">' + renderActions(i) + '</td>' +
            '</tr>';
    }).join('');
}

function renderActions(inv) {
    const s = getEffectiveStatus(inv);
    let html = '';
    if (s === 'draft') {
        html += '<button class="btn-sm btn-blue" onclick="markSent(\'' + inv.id + '\')">Send</button> ';
    }
    if (['sent','viewed','overdue'].includes(s)) {
        html += '<button class="btn-sm btn-green" onclick="openPaymentModal(\'' + inv.id + '\')">Pay</button> ';
    }
    return html;
}

function applyFilters() {
    const q = (document.getElementById('searchInput').value || '').toLowerCase();
    const status = document.getElementById('statusFilter').value;
    let filtered = allInvoices.filter(i => {
        if (q && !(i.customer||'').toLowerCase().includes(q) && !(i.invoice_number||i.id||'').toLowerCase().includes(q) && !(i.project_name||i.project||'').toLowerCase().includes(q)) return false;
        if (status) {
            const es = getEffectiveStatus(i);
            if (es !== status) return false;
        }
        return true;
    });
    renderTable(filtered);
}
function filterByStatus(s) { document.getElementById('statusFilter').value = s; applyFilters(); }

// --- Create/Edit Modal ---
function openCreateModal() {
    document.getElementById('editInvoiceId').value = '';
    document.getElementById('createModalTitle').textContent = 'Create Invoice';
    document.getElementById('submitBtn').textContent = 'Create Invoice';
    document.getElementById('invoiceForm').reset();
    document.getElementById('invoiceDateInput').value = today();
    updateDueFromTerms();
    resetLineItems();
    loadProjectsForSelect();
    document.getElementById('createModal').classList.add('active');
}
function closeCreateModal() { document.getElementById('createModal').classList.remove('active'); }

function resetLineItems() {
    document.getElementById('lineItemsContainer').innerHTML = `
        <div class="line-item">
            <input type="text" placeholder="Item description" class="li-desc">
            <input type="number" placeholder="1" class="li-qty" value="1" min="1" oninput="calcLineTotal(this)">
            <input type="number" placeholder="0.00" class="li-price" step="0.01" oninput="calcLineTotal(this)">
            <div class="li-total">$0</div>
            <button type="button" class="btn-remove" onclick="removeLine(this)">&times;</button>
        </div>`;
    recalcTotals();
}

function addLineItem(desc, qty, price) {
    const container = document.getElementById('lineItemsContainer');
    const div = document.createElement('div');
    div.className = 'line-item';
    div.innerHTML = '<input type="text" placeholder="Item description" class="li-desc" value="' + (desc||'') + '">' +
        '<input type="number" placeholder="1" class="li-qty" value="' + (qty||1) + '" min="1" oninput="calcLineTotal(this)">' +
        '<input type="number" placeholder="0.00" class="li-price" step="0.01" value="' + (price||'') + '" oninput="calcLineTotal(this)">' +
        '<div class="li-total">$0</div>' +
        '<button type="button" class="btn-remove" onclick="removeLine(this)">&times;</button>';
    container.appendChild(div);
    calcLineTotal(div.querySelector('.li-price'));
}

function removeLine(btn) {
    const items = document.querySelectorAll('.line-item');
    if (items.length > 1) { btn.closest('.line-item').remove(); recalcTotals(); }
}

function calcLineTotal(el) {
    const row = el.closest('.line-item');
    const qty = Number(row.querySelector('.li-qty').value) || 0;
    const price = Number(row.querySelector('.li-price').value) || 0;
    row.querySelector('.li-total').textContent = formatCurrency(qty * price);
    recalcTotals();
}

function recalcTotals() {
    let subtotal = 0;
    document.querySelectorAll('#lineItemsContainer .line-item').forEach(row => {
        const qty = Number(row.querySelector('.li-qty').value) || 0;
        const price = Number(row.querySelector('.li-price').value) || 0;
        subtotal += qty * price;
    });
    const taxRate = Number(document.getElementById('taxRateInput').value) || 0;
    const tax = subtotal * (taxRate / 100);
    document.getElementById('subtotalDisplay').textContent = formatCurrency(subtotal);
    document.getElementById('taxDisplay').textContent = formatCurrency(tax);
    document.getElementById('grandTotalDisplay').textContent = formatCurrency(subtotal + tax);
}

function updateDueFromTerms() {
    const terms = document.getElementById('termsSelect').value;
    const invDate = document.getElementById('invoiceDateInput').value || today();
    const d = new Date(invDate + 'T12:00:00');
    d.setDate(d.getDate() + (termsDays[terms] || 30));
    document.getElementById('dueDateInput').value = d.toISOString().split('T')[0];
}

async function loadProjectsForSelect() {
    if (projectsCache.length) { populateProjectSelect(); return; }
    try {
        const res = await fetch('/api/financial/projects');
        if (res.ok) {
            const data = await res.json();
            projectsCache = data.projects || [];
        }
    } catch(e) {}
    populateProjectSelect();
}

function populateProjectSelect() {
    const sel = document.getElementById('projectSelect');
    sel.innerHTML = '<option value="">-- Select a project (optional) --</option>';
    projectsCache.forEach(p => {
        sel.innerHTML += '<option value="' + p.job_code + '" data-customer="' + (p.customer||'') + '" data-sell="' + (p.sell_price||0) + '" data-name="' + (p.project_name||p.job_code) + '">' + p.job_code + ' - ' + (p.project_name||'') + '</option>';
    });
}

function onProjectSelect() {
    const sel = document.getElementById('projectSelect');
    const opt = sel.options[sel.selectedIndex];
    if (!opt || !opt.value) return;
    const customer = opt.getAttribute('data-customer');
    const sell = Number(opt.getAttribute('data-sell')) || 0;
    const name = opt.getAttribute('data-name');
    if (customer) document.getElementById('customerInput').value = customer;
    if (sell > 0) {
        document.getElementById('lineItemsContainer').innerHTML = '';
        addLineItem(name + ' - Project Quote', 1, sell.toFixed(2));
    }
}

function collectLineItems() {
    const items = [];
    document.querySelectorAll('#lineItemsContainer .line-item').forEach(row => {
        const desc = row.querySelector('.li-desc').value;
        const qty = Number(row.querySelector('.li-qty').value) || 1;
        const price = Number(row.querySelector('.li-price').value) || 0;
        if (desc || price > 0) items.push({ description: desc, quantity: qty, unit_price: price, total: qty * price });
    });
    return items;
}

async function submitInvoice(e) {
    e.preventDefault();
    const fd = new FormData(e.target);
    const data = Object.fromEntries(fd);
    data.line_items = collectLineItems();
    const subtotal = data.line_items.reduce((s, li) => s + li.total, 0);
    const taxRate = Number(document.getElementById('taxRateInput').value) || 0;
    data.tax_rate = taxRate;
    data.tax = subtotal * (taxRate / 100);
    data.subtotal = subtotal;
    data.amount = subtotal + data.tax;
    data.project_name = document.getElementById('projectSelect').options[document.getElementById('projectSelect').selectedIndex]?.getAttribute('data-name') || data.project_id || '';

    const editId = document.getElementById('editInvoiceId').value;
    const method = editId ? 'PUT' : 'POST';
    if (editId) data.id = editId;

    try {
        const res = await fetch('/api/financial/invoices', {
            method, headers: {'Content-Type':'application/json'}, body: JSON.stringify(data)
        });
        if (res.ok) { closeCreateModal(); loadInvoices(); }
    } catch(err) { console.error('Failed:', err); }
}

// --- Detail View ---
function viewInvoice(id) {
    const inv = allInvoices.find(i => i.id === id);
    if (!inv) return;
    document.getElementById('detailInvNumber').textContent = inv.invoice_number || inv.id;
    document.getElementById('detailStatus').innerHTML = statusBadge(inv);
    document.getElementById('detailCustomer').textContent = inv.customer || '--';
    document.getElementById('detailCustomerEmail').textContent = inv.customer_email || '';
    document.getElementById('detailDate').textContent = formatDate(inv.invoice_date || inv.created_at || inv.date);
    document.getElementById('detailDueDate').textContent = formatDate(inv.due_date);
    document.getElementById('detailTerms').textContent = termsLabels[inv.terms] || inv.terms || '--';
    document.getElementById('detailProject').textContent = inv.project_name || inv.project || '--';

    // Line items
    const tbody = document.getElementById('detailLineItems');
    const items = inv.line_items || [];
    if (items.length) {
        tbody.innerHTML = items.map(li =>
            '<tr><td>' + (li.description||'--') + '</td><td>' + (li.quantity||1) + '</td><td>' + formatCurrency(li.unit_price) + '</td><td style="font-weight:600">' + formatCurrency(li.total||((li.quantity||1)*(li.unit_price||0))) + '</td></tr>'
        ).join('');
    } else {
        tbody.innerHTML = '<tr><td colspan="4" style="color:var(--tf-muted);">Project total</td><td></td><td></td><td style="font-weight:600">' + formatCurrency(inv.amount) + '</td></tr>';
    }

    // Totals
    const totals = document.getElementById('detailTotals');
    const subtotal = inv.subtotal || inv.amount || 0;
    const tax = inv.tax || 0;
    const total = inv.amount || (subtotal + tax);
    totals.innerHTML = '<div class="tot-row"><span class="tot-label">Subtotal</span><span class="tot-value">' + formatCurrency(subtotal) + '</span></div>';
    if (tax > 0) totals.innerHTML += '<div class="tot-row"><span class="tot-label">Tax (' + (inv.tax_rate||0) + '%)</span><span class="tot-value">' + formatCurrency(tax) + '</span></div>';
    totals.innerHTML += '<div class="tot-row tot-grand"><span class="tot-label">Total Due</span><span class="tot-value">' + formatCurrency(total) + '</span></div>';

    // Notes
    if (inv.notes) {
        document.getElementById('detailNotesSection').style.display = '';
        document.getElementById('detailNotes').textContent = inv.notes;
    } else {
        document.getElementById('detailNotesSection').style.display = 'none';
    }

    // Payment info
    if (inv.payment_date) {
        document.getElementById('detailPaymentInfo').style.display = '';
        document.getElementById('detailPaymentDetails').textContent =
            formatCurrency(inv.payment_amount || inv.amount) + ' received on ' + formatDate(inv.payment_date) +
            (inv.payment_method ? ' via ' + inv.payment_method : '') +
            (inv.payment_reference ? ' (Ref: ' + inv.payment_reference + ')' : '');
    } else {
        document.getElementById('detailPaymentInfo').style.display = 'none';
    }

    // Actions
    const es = getEffectiveStatus(inv);
    let actionsHtml = '<button class="btn-secondary" onclick="closeDetailModal()">Close</button>';
    if (es === 'draft') {
        actionsHtml += ' <button class="btn-blue" onclick="closeDetailModal();markSent(\'' + inv.id + '\')">Mark as Sent</button>';
    }
    if (['sent','viewed','overdue'].includes(es)) {
        actionsHtml += ' <button class="btn-green" onclick="closeDetailModal();openPaymentModal(\'' + inv.id + '\')">Record Payment</button>';
    }
    document.getElementById('detailActions').innerHTML = actionsHtml;

    document.getElementById('detailModal').classList.add('active');
}
function closeDetailModal() { document.getElementById('detailModal').classList.remove('active'); }

// --- Status Actions ---
async function markSent(id) {
    try {
        await fetch('/api/financial/invoices', {
            method: 'PUT', headers: {'Content-Type':'application/json'},
            body: JSON.stringify({ id, status: 'sent', sent_date: new Date().toISOString() })
        });
        loadInvoices();
    } catch(e) { console.error(e); }
}

function openPaymentModal(id) {
    const inv = allInvoices.find(i => i.id === id);
    document.getElementById('payInvoiceId').value = id;
    document.getElementById('payAmount').value = inv ? (inv.amount || 0) : '';
    document.getElementById('payDate').value = today();
    document.getElementById('paymentModal').classList.add('active');
}
function closePaymentModal() { document.getElementById('paymentModal').classList.remove('active'); }

async function submitPayment() {
    const id = document.getElementById('payInvoiceId').value;
    const data = {
        id,
        status: 'paid',
        payment_amount: Number(document.getElementById('payAmount').value) || 0,
        payment_method: document.getElementById('payMethod').value,
        payment_date: document.getElementById('payDate').value,
        payment_reference: document.getElementById('payReference').value,
    };
    try {
        await fetch('/api/financial/invoices', {
            method: 'PUT', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data)
        });
        closePaymentModal();
        loadInvoices();
    } catch(e) { console.error(e); }
}

// --- Load ---
async function loadInvoices() {
    try {
        const res = await fetch('/api/financial/invoices');
        if (!res.ok) throw new Error('API error');
        const data = await res.json();
        allInvoices = Array.isArray(data) ? data : (data.invoices || []);
    } catch(err) { console.warn('Could not load invoices:', err); allInvoices = []; }
    // Sort: overdue first, then by date desc
    allInvoices.sort((a, b) => {
        const aOver = getEffectiveStatus(a) === 'overdue' ? 0 : 1;
        const bOver = getEffectiveStatus(b) === 'overdue' ? 0 : 1;
        if (aOver !== bOver) return aOver - bOver;
        return (b.created_at || '').localeCompare(a.created_at || '');
    });
    updateStats(allInvoices);
    applyFilters();
}

// Close modals on overlay click
['createModal','detailModal','paymentModal'].forEach(id => {
    document.getElementById(id).addEventListener('click', function(e) { if (e.target === this) this.classList.remove('active'); });
});

loadInvoices();
</script>
"""
