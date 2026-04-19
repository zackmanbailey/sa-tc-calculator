"""
TitanForge v4 — Quote Manager
===============================
View, compare, and manage all project quotes.
"""

QUOTES_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a;
        --tf-card: #1e293b;
        --tf-text: #e2e8f0;
        --tf-muted: #94a3b8;
        --tf-gold: #d4a843;
        --tf-blue: #3b82f6;
    }
    .quotes-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 24px 32px;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
        color: var(--tf-text);
    }
    .page-header {
        margin-bottom: 32px;
    }
    .page-header h1 {
        font-size: 28px;
        font-weight: 800;
        margin: 0 0 6px 0;
        color: var(--tf-text);
    }
    .page-header p {
        font-size: 14px;
        color: var(--tf-muted);
        margin: 0;
    }
    .toolbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        flex-wrap: wrap;
        gap: 12px;
    }
    .toolbar input[type="text"] {
        background: var(--tf-card);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 8px;
        padding: 10px 16px;
        color: var(--tf-text);
        font-size: 14px;
        width: 300px;
    }
    .toolbar input[type="text"]::placeholder { color: var(--tf-muted); }
    .btn-gold {
        background: var(--tf-gold);
        color: #0f172a;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 700;
        font-size: 14px;
        cursor: pointer;
        text-decoration: none;
        display: inline-block;
    }
    .btn-gold:hover { opacity: 0.9; }
    .quotes-card {
        background: var(--tf-card);
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06);
        padding: 0;
        overflow: hidden;
    }
    .quotes-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
    }
    .quotes-table thead th {
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
    .quotes-table tbody td {
        padding: 12px 16px;
        border-bottom: 1px solid rgba(255,255,255,0.04);
        color: var(--tf-text);
    }
    .quotes-table tbody tr { cursor: pointer; transition: background 0.15s ease; }
    .quotes-table tbody tr:hover { background: rgba(255,255,255,0.04); }
    .project-link {
        color: var(--tf-text);
        text-decoration: none;
        font-weight: 600;
        cursor: pointer;
    }
    .project-link:hover { color: var(--tf-blue); text-decoration: underline; }
    .customer-link {
        color: var(--tf-muted);
        text-decoration: none;
        cursor: pointer;
    }
    .customer-link:hover { color: #60a5fa; text-decoration: underline; }
    .status-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        cursor: pointer;
        transition: opacity 0.2s ease;
    }
    .status-badge:hover { opacity: 0.75; }
    .status-draft { background: rgba(148,163,184,0.2); color: #94a3b8; }
    .status-sent { background: rgba(59,130,246,0.2); color: #60a5fa; }
    .status-approved { background: rgba(34,197,94,0.2); color: #4ade80; }
    .status-rejected { background: rgba(239,68,68,0.2); color: #f87171; }
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        color: var(--tf-muted);
    }
    .empty-state h3 { font-size: 18px; margin-bottom: 8px; color: var(--tf-text); }
    .loading { text-align: center; padding: 40px; color: var(--tf-muted); }
    a.link-blue { color: var(--tf-blue); text-decoration: none; }
    a.link-blue:hover { text-decoration: underline; }

/* ── Responsive ── */
@media (max-width: 768px) {
    .page-header h1 { font-size: 22px; }
    .toolbar { flex-direction: column; align-items: stretch; }
    .toolbar input[type="text"] { width: 100%; }
    .quotes-table { display: block; overflow-x: auto; -webkit-overflow-scrolling: touch; }
    .quotes-card { padding: 12px; }
}
@media (max-width: 480px) {
    .toolbar { gap: 8px; }
    .btn-gold { width: 100%; text-align: center; }
}
</style>

<div class="quotes-container">
    <div class="page-header">
        <h1>Quote Manager</h1>
        <p>View, compare, and manage all project quotes</p>
    </div>
    <div class="toolbar">
        <input type="text" id="quoteSearch" placeholder="Search quotes..." oninput="filterQuotes()">
        <a href="/sa" class="btn-gold">+ New Quote</a>
    </div>
    <div class="quotes-card">
        <div id="quotesTableWrap" class="loading">Loading quotes...</div>
    </div>
</div>

<script>
let allQuotes = [];

async function loadQuotes() {
    try {
        const resp = await fetch('/api/projects/full');
        const data = await resp.json();
        allQuotes = Array.isArray(data) ? data : (data.projects || []);
        renderQuotes(allQuotes);
    } catch (err) {
        document.getElementById('quotesTableWrap').innerHTML =
            '<div class="empty-state"><h3>Unable to load quotes</h3><p>' + err.message + '</p></div>';
    }
}

function formatCurrency(v) {
    if (v == null || v === '') return '—';
    return '$' + Number(v).toLocaleString('en-US', {minimumFractionDigits: 0, maximumFractionDigits: 0});
}

function getStatusClass(stage) {
    if (!stage) return 'status-draft';
    const s = stage.toLowerCase();
    if (s.includes('draft') || s.includes('quote')) return 'status-draft';
    if (s.includes('approved') || s.includes('complete')) return 'status-approved';
    if (s.includes('reject') || s.includes('cancel')) return 'status-rejected';
    return 'status-sent';
}

function renderQuotes(quotes) {
    const wrap = document.getElementById('quotesTableWrap');
    if (!quotes.length) {
        wrap.innerHTML = '<div class="empty-state"><h3>No quotes found</h3><p>Create a new quote to get started.</p></div>';
        return;
    }
    let html = '<table class="quotes-table"><thead><tr>' +
        '<th>Job Code</th><th>Project Name</th><th>Customer</th><th>Quote Date</th>' +
        '<th>Material Cost</th><th>Sell Price</th><th>Status</th></tr></thead><tbody>';
    let activeStatusFilter = null;
    quotes.forEach(q => {
        const statusCls = getStatusClass(q.stage || q.status);
        const projectUrl = '/project/' + encodeURIComponent(q.id || q.job_code || '');
        const custName = q.customer || q.customer_name || '—';
        const stageTxt = q.stage || q.status || 'Draft';
        html += '<tr onclick="window.location.href=\'' + projectUrl + '\'" title="Click to view project">' +
            '<td><a class="link-blue" href="' + projectUrl + '" onclick="event.stopPropagation()">' + (q.job_code || q.id || '—') + '</a></td>' +
            '<td><a class="project-link" href="' + projectUrl + '" onclick="event.stopPropagation()">' + (q.project_name || q.name || '—') + '</a></td>' +
            '<td><span class="customer-link" onclick="event.stopPropagation();window.location.href=\'/customers\'" title="View customers">' + custName + '</span></td>' +
            '<td>' + (q.quote_date || q.created_at || '—') + '</td>' +
            '<td>' + formatCurrency(q.material_cost || q.materialCost) + '</td>' +
            '<td>' + formatCurrency(q.sell_price || q.sellPrice || q.total_price) + '</td>' +
            '<td><span class="status-badge ' + statusCls + '" onclick="event.stopPropagation();filterByStatus(\'' + stageTxt.replace(/'/g, "\\'") + '\')" title="Filter by ' + stageTxt + '">' + stageTxt + '</span></td>' +
            '</tr>';
    });
    html += '</tbody></table>';
    wrap.innerHTML = html;
}

function filterQuotes() {
    const term = document.getElementById('quoteSearch').value.toLowerCase();
    if (!term) { renderQuotes(allQuotes); return; }
    const filtered = allQuotes.filter(q =>
        (q.job_code || '').toLowerCase().includes(term) ||
        (q.project_name || q.name || '').toLowerCase().includes(term) ||
        (q.customer || q.customer_name || '').toLowerCase().includes(term)
    );
    renderQuotes(filtered);
}

function filterByStatus(status) {
    const s = (status || '').toLowerCase();
    const filtered = allQuotes.filter(q => {
        const qs = (q.stage || q.status || 'draft').toLowerCase();
        return qs === s || qs.includes(s);
    });
    if (filtered.length) {
        renderQuotes(filtered);
        // Put the filter term in the search box so user can clear it
        document.getElementById('quoteSearch').value = status;
    }
}

loadQuotes();
</script>
"""
