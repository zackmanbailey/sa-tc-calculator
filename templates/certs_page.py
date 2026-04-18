"""
TitanForge v4 -- Material Certifications
==========================================
MTR tracking, heat numbers, cert upload/view, traceability links, compliance status.
"""

CERTS_PAGE_HTML = r"""
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
    .certs-container {
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
    .toolbar input[type="text"], .toolbar select {
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
    .badge-verified { background: rgba(16,185,129,0.15); color: var(--tf-green); }
    .badge-pending { background: rgba(245,158,11,0.15); color: var(--tf-orange); }
    .badge-missing { background: rgba(239,68,68,0.15); color: var(--tf-red); }
    .badge-expired { background: rgba(148,163,184,0.15); color: var(--tf-muted); }

    .empty-state {
        text-align: center; padding: 60px 20px; color: var(--tf-muted);
    }
    .empty-state .icon { font-size: 48px; margin-bottom: 16px; opacity: 0.5; }
    .empty-state h3 { font-size: 18px; color: var(--tf-text); margin-bottom: 8px; }
    .empty-state p { font-size: 14px; max-width: 400px; margin: 0 auto 20px; }

    .modal-overlay {
        display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6);
        z-index: 1000; justify-content: center; align-items: center;
    }
    .modal-overlay.active { display: flex; }
    .modal {
        background: var(--tf-card); border-radius: 16px; padding: 32px;
        width: 90%; max-width: 600px; border: 1px solid rgba(255,255,255,0.1);
        max-height: 80vh; overflow-y: auto;
    }
    .modal h2 { font-size: 20px; font-weight: 700; margin: 0 0 24px 0; }
    .form-group { margin-bottom: 18px; }
    .form-group label { display: block; font-size: 12px; font-weight: 600; color: var(--tf-muted); text-transform: uppercase; margin-bottom: 6px; }
    .form-group input, .form-group select, .form-group textarea {
        width: 100%; background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px;
    }
    .form-group input:focus, .form-group select:focus { outline: none; border-color: var(--tf-blue); }
    .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 24px; }

    .upload-zone {
        border: 2px dashed rgba(255,255,255,0.1); border-radius: 12px;
        padding: 32px; text-align: center; cursor: pointer; transition: border-color 0.2s;
    }
    .upload-zone:hover { border-color: var(--tf-gold); }
    .upload-zone p { margin: 8px 0 0; font-size: 13px; color: var(--tf-muted); }
</style>

<div class="certs-container">
    <div class="page-header">
        <h1>Material Certifications</h1>
        <p>MTR tracking, heat numbers, compliance verification, and traceability</p>
    </div>

    <div class="stat-row">
        <div class="stat-card stat-gold">
            <div class="label">Total Certs</div>
            <div class="value" id="stat-total">0</div>
        </div>
        <div class="stat-card stat-green">
            <div class="label">Verified</div>
            <div class="value" id="stat-verified">0</div>
        </div>
        <div class="stat-card stat-orange">
            <div class="label">Pending Review</div>
            <div class="value" id="stat-pending">0</div>
        </div>
        <div class="stat-card stat-red">
            <div class="label">Missing</div>
            <div class="value" id="stat-missing">0</div>
        </div>
    </div>

    <div class="toolbar">
        <div class="toolbar-left">
            <input type="text" id="search-input" placeholder="Search by heat number, material..." oninput="filterTable()">
            <select id="status-filter" onchange="filterTable()">
                <option value="">All Statuses</option>
                <option value="verified">Verified</option>
                <option value="pending">Pending</option>
                <option value="missing">Missing</option>
                <option value="expired">Expired</option>
            </select>
            <select id="type-filter" onchange="filterTable()">
                <option value="">All Types</option>
                <option value="mtr">MTR</option>
                <option value="galv">Galvanizing Cert</option>
                <option value="paint">Paint Cert</option>
                <option value="hardware">Hardware Cert</option>
            </select>
        </div>
        <button class="btn btn-primary" onclick="openModal()">+ Upload Cert</button>
    </div>

    <div id="table-container">
        <table class="data-table">
            <thead>
                <tr>
                    <th>Cert ID</th>
                    <th>Type</th>
                    <th>Heat Number</th>
                    <th>Material</th>
                    <th>Vendor</th>
                    <th>Received</th>
                    <th>Status</th>
                    <th>Linked Items</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody id="certs-tbody"></tbody>
        </table>
        <div class="empty-state" id="empty-state">
            <div class="icon">&#x1F4DC;</div>
            <h3>No Certifications Found</h3>
            <p>Upload material test reports and certifications to maintain compliance traceability.</p>
            <button class="btn btn-primary" onclick="openModal()">+ Upload Cert</button>
        </div>
    </div>
</div>

<!-- Cert Upload Modal -->
<div class="modal-overlay" id="cert-modal">
    <div class="modal">
        <h2 id="modal-title">Upload Material Certification</h2>
        <div class="form-row">
            <div class="form-group">
                <label>Cert Type</label>
                <select id="cert-type">
                    <option value="">Select type...</option>
                    <option value="mtr">Mill Test Report (MTR)</option>
                    <option value="galv">Galvanizing Certificate</option>
                    <option value="paint">Paint Certificate</option>
                    <option value="hardware">Hardware Certificate</option>
                </select>
            </div>
            <div class="form-group">
                <label>Heat Number</label>
                <input type="text" id="cert-heat" placeholder="e.g., H-284756">
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Material</label>
                <input type="text" id="cert-material" placeholder="e.g., A572 Gr50">
            </div>
            <div class="form-group">
                <label>Vendor</label>
                <input type="text" id="cert-vendor" placeholder="Vendor name">
            </div>
        </div>
        <div class="form-group">
            <label>Upload Document</label>
            <div class="upload-zone" onclick="document.getElementById('cert-file').click()">
                <div style="font-size:32px;opacity:0.5;">&#x1F4C4;</div>
                <p>Click to upload MTR / Certificate PDF</p>
                <input type="file" id="cert-file" style="display:none" accept=".pdf,.jpg,.png">
            </div>
        </div>
        <div class="form-group">
            <label>Notes</label>
            <textarea id="cert-notes" rows="3" placeholder="Additional notes..."></textarea>
        </div>
        <div class="modal-actions">
            <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
            <button class="btn btn-primary" onclick="saveCert()">Save Certification</button>
        </div>
    </div>
</div>

<script>
let certs = [];

async function loadCerts() {
    try {
        const resp = await fetch('/api/certs');
        const data = await resp.json();
        certs = data.certs || [];
        renderTable();
        updateStats();
    } catch(e) { console.error('Failed to load certs:', e); renderTable(); }
}

function updateStats() {
    document.getElementById('stat-total').textContent = certs.length;
    document.getElementById('stat-verified').textContent = certs.filter(c => c.status === 'verified').length;
    document.getElementById('stat-pending').textContent = certs.filter(c => c.status === 'pending').length;
    document.getElementById('stat-missing').textContent = certs.filter(c => c.status === 'missing').length;
}

function renderTable() {
    const tbody = document.getElementById('certs-tbody');
    const empty = document.getElementById('empty-state');
    const filtered = getFiltered();
    if (filtered.length === 0) { tbody.innerHTML = ''; empty.style.display = 'block'; return; }
    empty.style.display = 'none';
    tbody.innerHTML = filtered.map(c => `
        <tr>
            <td><strong>${c.id || '--'}</strong></td>
            <td>${c.type || '--'}</td>
            <td style="font-family:monospace">${c.heat_number || '--'}</td>
            <td>${c.material || '--'}</td>
            <td>${c.vendor || '--'}</td>
            <td>${c.received_date || '--'}</td>
            <td><span class="badge badge-${c.status || 'pending'}">${c.status || 'pending'}</span></td>
            <td>${c.linked_items || 0}</td>
            <td>
                <button class="btn btn-sm btn-secondary" onclick="viewCert('${c.id}')">View</button>
            </td>
        </tr>
    `).join('');
}

function getFiltered() {
    const search = (document.getElementById('search-input').value || '').toLowerCase();
    const status = document.getElementById('status-filter').value;
    const type = document.getElementById('type-filter').value;
    return certs.filter(c => {
        if (search && !JSON.stringify(c).toLowerCase().includes(search)) return false;
        if (status && c.status !== status) return false;
        if (type && c.type !== type) return false;
        return true;
    });
}

function filterTable() { renderTable(); }
function openModal() { document.getElementById('cert-modal').classList.add('active'); }
function closeModal() { document.getElementById('cert-modal').classList.remove('active'); }
function viewCert(id) { openModal(); }

async function saveCert() {
    const payload = {
        type: document.getElementById('cert-type').value,
        heat_number: document.getElementById('cert-heat').value,
        material: document.getElementById('cert-material').value,
        vendor: document.getElementById('cert-vendor').value,
        notes: document.getElementById('cert-notes').value,
    };
    try {
        await fetch('/api/certs', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
        closeModal();
        loadCerts();
    } catch(e) { console.error('Save failed:', e); }
}

document.addEventListener('DOMContentLoaded', loadCerts);
</script>
"""
