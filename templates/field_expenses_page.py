"""
TitanForge v4 -- Field Expense Tracking
=========================================
Per diem, fuel, materials purchased on site, receipt upload, approval workflow.
"""

FIELD_EXPENSES_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a; --tf-card: #1e293b; --tf-text: #e2e8f0;
        --tf-muted: #94a3b8; --tf-gold: #d4a843; --tf-blue: #3b82f6;
        --tf-green: #10b981; --tf-red: #ef4444; --tf-orange: #f59e0b;
    }
    .expenses-container {
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
    .stat-orange .value { color: var(--tf-orange); }

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
    .btn { padding: 10px 20px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
    .btn-primary { background: var(--tf-gold); color: #0f172a; }
    .btn-primary:hover { background: #e0b44e; }
    .btn-secondary { background: var(--tf-card); color: var(--tf-text); border: 1px solid rgba(255,255,255,0.06); }
    .btn-sm { padding: 6px 14px; font-size: 12px; }
    .btn-success { background: var(--tf-green); color: #fff; }
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
    .data-table td { padding: 14px 16px; font-size: 14px; border-bottom: 1px solid rgba(255,255,255,0.04); }
    .data-table tbody tr { cursor: pointer; transition: background 0.15s; }
    .data-table tbody tr:hover { background: rgba(59,130,246,0.06); }

    .badge { display: inline-block; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
    .badge-pending { background: rgba(245,158,11,0.15); color: var(--tf-orange); }
    .badge-approved { background: rgba(16,185,129,0.15); color: var(--tf-green); }
    .badge-rejected { background: rgba(239,68,68,0.15); color: var(--tf-red); }
    .badge-reimbursed { background: rgba(59,130,246,0.15); color: var(--tf-blue); }

    .category-tag {
        display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 11px;
        font-weight: 600; background: rgba(212,168,67,0.1); color: var(--tf-gold);
    }

    .empty-state { text-align: center; padding: 60px 20px; color: var(--tf-muted); }
    .empty-state .icon { font-size: 48px; margin-bottom: 16px; opacity: 0.5; }
    .empty-state h3 { font-size: 18px; color: var(--tf-text); margin-bottom: 8px; }
    .empty-state p { font-size: 14px; max-width: 400px; margin: 0 auto 20px; }

    .modal-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 1000; align-items: center; justify-content: center; }
    .modal-overlay.active { display: flex; }
    .modal { background: var(--tf-card); border-radius: 16px; padding: 32px; width: 90%; max-width: 600px; max-height: 90vh; overflow-y: auto; border: 1px solid rgba(255,255,255,0.08); }
    .modal h2 { font-size: 22px; font-weight: 800; margin: 0 0 24px 0; }
    .modal-close { float: right; background: none; border: none; color: var(--tf-muted); font-size: 24px; cursor: pointer; }
    .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .form-group { margin-bottom: 16px; }
    .form-group label { display: block; font-size: 13px; font-weight: 600; color: var(--tf-muted); margin-bottom: 6px; }
    .form-group input, .form-group select, .form-group textarea {
        width: 100%; background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px;
    }
    .form-group textarea { min-height: 60px; resize: vertical; }
    .form-group input:focus, .form-group select:focus { outline: none; border-color: var(--tf-blue); }
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

<div class="expenses-container">
    <div class="page-header">
        <h1>Field Expenses</h1>
        <p>Track per diem, fuel, materials, and other field expenses with receipt management and approval workflow</p>
    </div>

    <div class="stat-row">
        <div class="stat-card stat-gold"><div class="label">Total Expenses</div><div class="value" id="stat-total">$0</div></div>
        <div class="stat-card stat-orange"><div class="label">Pending Approval</div><div class="value" id="stat-pending">$0</div></div>
        <div class="stat-card stat-green"><div class="label">Approved</div><div class="value" id="stat-approved">$0</div></div>
        <div class="stat-card stat-blue"><div class="label">Reimbursed</div><div class="value" id="stat-reimbursed">$0</div></div>
        <div class="stat-card stat-red"><div class="label">This Month</div><div class="value" id="stat-month">$0</div></div>
    </div>

    <div class="toolbar">
        <div class="toolbar-left">
            <input type="text" id="searchInput" placeholder="Search expenses..." oninput="renderExpenses()">
            <select id="filterCategory" onchange="renderExpenses()">
                <option value="">All Categories</option>
                <option value="per_diem">Per Diem</option>
                <option value="fuel">Fuel</option>
                <option value="materials">Materials</option>
                <option value="tools">Tools</option>
                <option value="meals">Meals</option>
                <option value="travel">Travel</option>
                <option value="other">Other</option>
            </select>
            <select id="filterStatus" onchange="renderExpenses()">
                <option value="">All Status</option>
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
                <option value="reimbursed">Reimbursed</option>
            </select>
            <input type="date" id="filterFrom" onchange="renderExpenses()">
            <input type="date" id="filterTo" onchange="renderExpenses()">
        </div>
        <div style="display:flex;gap:10px;">
            <button class="btn btn-secondary" onclick="exportExpenses()">Export CSV</button>
            <button class="btn btn-primary" onclick="openExpenseModal()">+ New Expense</button>
        </div>
    </div>

    <table class="data-table">
        <thead>
            <tr>
                <th>Date</th>
                <th>Description</th>
                <th>Category</th>
                <th>Project</th>
                <th>Submitted By</th>
                <th>Amount</th>
                <th>Receipt</th>
                <th>Status</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody id="expensesTable"></tbody>
    </table>

    <div class="empty-state" id="emptyState">
        <div class="icon">&#128176;</div>
        <h3>No Field Expenses</h3>
        <p>Track field purchases, per diem, fuel costs, and more. Upload receipts for easy reimbursement.</p>
        <button class="btn btn-primary" onclick="openExpenseModal()">+ Submit First Expense</button>
    </div>
</div>

<!-- Expense Modal -->
<div class="modal-overlay" id="expenseModal">
    <div class="modal">
        <button class="modal-close" onclick="closeModal('expenseModal')">&times;</button>
        <h2 id="expenseModalTitle">New Expense</h2>
        <form id="expenseForm" onsubmit="saveExpense(event)">
            <div class="form-grid">
                <div class="form-group"><label>Date</label><input type="date" id="expDate" required></div>
                <div class="form-group"><label>Amount ($)</label><input type="number" id="expAmount" step="0.01" min="0" required></div>
                <div class="form-group"><label>Category</label>
                    <select id="expCategory" required>
                        <option value="">Select Category</option>
                        <option value="per_diem">Per Diem</option>
                        <option value="fuel">Fuel</option>
                        <option value="materials">Materials</option>
                        <option value="tools">Tools</option>
                        <option value="meals">Meals</option>
                        <option value="travel">Travel</option>
                        <option value="other">Other</option>
                    </select>
                </div>
                <div class="form-group"><label>Project</label>
                    <select id="expProject"><option value="">Select Project</option></select>
                </div>
                <div class="form-group form-full"><label>Description</label><input type="text" id="expDesc" placeholder="What was purchased?" required></div>
                <div class="form-group"><label>Vendor / Store</label><input type="text" id="expVendor"></div>
                <div class="form-group"><label>Payment Method</label>
                    <select id="expPayment">
                        <option value="company_card">Company Card</option>
                        <option value="personal">Personal (Reimburse)</option>
                        <option value="cash">Cash</option>
                    </select>
                </div>
                <div class="form-group form-full"><label>Receipt Image</label><input type="file" id="expReceipt" accept="image/*,.pdf" style="padding:8px;"></div>
                <div class="form-group form-full"><label>Notes</label><textarea id="expNotes" placeholder="Additional details..."></textarea></div>
            </div>
            <div class="modal-actions">
                <button type="button" class="btn btn-secondary" onclick="closeModal('expenseModal')">Cancel</button>
                <button type="submit" class="btn btn-primary">Submit Expense</button>
            </div>
        </form>
    </div>
</div>

<script>
    let expenses = [];
    let editingId = null;

    async function loadExpenses() {
        try {
            const resp = await fetch('/api/field/expenses');
            const data = await resp.json();
            expenses = data.expenses || [];
            renderExpenses();
            updateStats();
        } catch(e) { console.error('Failed to load expenses:', e); renderExpenses(); }
    }

    function renderExpenses() {
        const tbody = document.getElementById('expensesTable');
        const empty = document.getElementById('emptyState');
        const search = document.getElementById('searchInput').value.toLowerCase();
        const catFilter = document.getElementById('filterCategory').value;
        const statusFilter = document.getElementById('filterStatus').value;

        let filtered = expenses.filter(ex => {
            if (search && !JSON.stringify(ex).toLowerCase().includes(search)) return false;
            if (catFilter && ex.category !== catFilter) return false;
            if (statusFilter && ex.status !== statusFilter) return false;
            return true;
        });

        if (filtered.length === 0) { tbody.innerHTML = ''; empty.style.display = 'block'; return; }
        empty.style.display = 'none';

        const statusCls = { pending: 'badge-pending', approved: 'badge-approved', rejected: 'badge-rejected', reimbursed: 'badge-reimbursed' };
        const catLabels = { per_diem: 'Per Diem', fuel: 'Fuel', materials: 'Materials', tools: 'Tools', meals: 'Meals', travel: 'Travel', other: 'Other' };

        tbody.innerHTML = filtered.map(ex => `
            <tr onclick="editExpense('${ex.id}')">
                <td>${ex.date || ''}</td>
                <td>${ex.description || ''}</td>
                <td><span class="category-tag">${catLabels[ex.category] || ex.category}</span></td>
                <td>${ex.project_name || ''}</td>
                <td>${ex.submitted_by || ''}</td>
                <td style="font-weight:700">$${(ex.amount || 0).toFixed(2)}</td>
                <td>${ex.has_receipt ? '<span style="color:var(--tf-green)">Attached</span>' : '<span style="color:var(--tf-muted)">None</span>'}</td>
                <td><span class="badge ${statusCls[ex.status] || 'badge-pending'}">${ex.status || 'pending'}</span></td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="event.stopPropagation();editExpense('${ex.id}')">Edit</button>
                    ${ex.status === 'pending' ? `<button class="btn btn-sm btn-success" onclick="event.stopPropagation();approveExpense('${ex.id}')">Approve</button>` : ''}
                </td>
            </tr>
        `).join('');
    }

    function updateStats() {
        const total = expenses.reduce((s, e) => s + (e.amount || 0), 0);
        const pending = expenses.filter(e => e.status === 'pending').reduce((s, e) => s + (e.amount || 0), 0);
        const approved = expenses.filter(e => e.status === 'approved').reduce((s, e) => s + (e.amount || 0), 0);
        const reimbursed = expenses.filter(e => e.status === 'reimbursed').reduce((s, e) => s + (e.amount || 0), 0);
        document.getElementById('stat-total').textContent = '$' + total.toLocaleString(undefined, {minimumFractionDigits:0, maximumFractionDigits:0});
        document.getElementById('stat-pending').textContent = '$' + pending.toLocaleString(undefined, {minimumFractionDigits:0, maximumFractionDigits:0});
        document.getElementById('stat-approved').textContent = '$' + approved.toLocaleString(undefined, {minimumFractionDigits:0, maximumFractionDigits:0});
        document.getElementById('stat-reimbursed').textContent = '$' + reimbursed.toLocaleString(undefined, {minimumFractionDigits:0, maximumFractionDigits:0});
        const now = new Date();
        const monthTotal = expenses.filter(e => { const d = new Date(e.date); return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear(); }).reduce((s, e) => s + (e.amount || 0), 0);
        document.getElementById('stat-month').textContent = '$' + monthTotal.toLocaleString(undefined, {minimumFractionDigits:0, maximumFractionDigits:0});
    }

    function openExpenseModal() {
        editingId = null;
        document.getElementById('expenseModalTitle').textContent = 'New Expense';
        document.getElementById('expenseForm').reset();
        document.getElementById('expDate').value = new Date().toISOString().split('T')[0];
        document.getElementById('expenseModal').classList.add('active');
    }

    function editExpense(id) {
        const ex = expenses.find(e => e.id === id);
        if (!ex) return;
        editingId = id;
        document.getElementById('expenseModalTitle').textContent = 'Edit Expense';
        document.getElementById('expDate').value = ex.date || '';
        document.getElementById('expAmount').value = ex.amount || '';
        document.getElementById('expCategory').value = ex.category || '';
        document.getElementById('expProject').value = ex.project_id || '';
        document.getElementById('expDesc').value = ex.description || '';
        document.getElementById('expVendor').value = ex.vendor || '';
        document.getElementById('expPayment').value = ex.payment_method || '';
        document.getElementById('expNotes').value = ex.notes || '';
        document.getElementById('expenseModal').classList.add('active');
    }

    async function saveExpense(e) {
        e.preventDefault();
        const payload = {
            id: editingId,
            date: document.getElementById('expDate').value,
            amount: parseFloat(document.getElementById('expAmount').value),
            category: document.getElementById('expCategory').value,
            project_id: document.getElementById('expProject').value,
            description: document.getElementById('expDesc').value,
            vendor: document.getElementById('expVendor').value,
            payment_method: document.getElementById('expPayment').value,
            notes: document.getElementById('expNotes').value,
            status: 'pending'
        };
        try {
            await fetch('/api/field/expenses', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
            closeModal('expenseModal');
            loadExpenses();
        } catch(e) { alert('Error saving expense'); }
    }

    async function approveExpense(id) {
        try {
            await fetch('/api/field/expenses/approve', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ id: id }) });
            loadExpenses();
        } catch(e) { alert('Error approving expense'); }
    }

    function exportExpenses() { window.open('/api/field/expenses/export?format=csv', '_blank'); }

    function closeModal(id) { document.getElementById(id).classList.remove('active'); }
    window.addEventListener('click', e => { if (e.target.classList.contains('modal-overlay')) e.target.classList.remove('active'); });

    document.addEventListener('DOMContentLoaded', loadExpenses);
</script>
"""
