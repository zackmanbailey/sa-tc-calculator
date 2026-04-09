from templates.shared_styles import DESIGN_SYSTEM_CSS

CUSTOMERS_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TitanForge — Customer Database</title>
    <style>
""" + DESIGN_SYSTEM_CSS + r"""

        .container { max-width: 1400px; margin: 0 auto; padding: var(--tf-sp-6) var(--tf-sp-8); }

        /* Search & Filter Bar */
        .toolbar {
            display: flex; gap: var(--tf-sp-3); align-items: center;
            margin-bottom: var(--tf-sp-6); flex-wrap: wrap;
        }
        .toolbar .search-box {
            flex: 1; min-width: 280px; padding: 10px 16px 10px 40px;
            border: 1px solid var(--tf-border); border-radius: var(--tf-radius);
            font-size: var(--tf-text-base); background: var(--tf-surface);
            transition: border-color var(--tf-duration) var(--tf-ease);
        }
        .toolbar .search-box:focus { outline: none; border-color: var(--tf-blue); box-shadow: 0 0 0 3px rgba(30,64,175,0.1); }
        .search-wrap { position: relative; flex: 1; min-width: 280px; }
        .search-wrap::before {
            content: '\1F50D'; position: absolute; left: 12px; top: 50%;
            transform: translateY(-50%); font-size: 14px; opacity: 0.5;
        }
        .tag-filter {
            padding: 8px 16px; border: 1px solid var(--tf-border); border-radius: var(--tf-radius);
            background: var(--tf-surface); font-size: var(--tf-text-sm); cursor: pointer;
        }
        .tag-filter.active { background: var(--tf-blue); color: #fff; border-color: var(--tf-blue); }

        /* Customer Cards */
        .customers-grid {
            display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: var(--tf-sp-4);
        }
        .customer-card {
            background: var(--tf-surface); border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-lg); padding: var(--tf-sp-5);
            cursor: pointer; transition: all var(--tf-duration) var(--tf-ease);
        }
        .customer-card:hover { box-shadow: var(--tf-shadow-md); border-color: var(--tf-blue); transform: translateY(-1px); }
        .customer-card .cc-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: var(--tf-sp-3); }
        .customer-card .cc-company { font-size: var(--tf-text-lg); font-weight: 700; color: var(--tf-gray-900); }
        .customer-card .cc-contact { font-size: var(--tf-text-sm); color: var(--tf-gray-600); margin-bottom: var(--tf-sp-2); }
        .customer-card .cc-meta { display: flex; gap: var(--tf-sp-3); font-size: var(--tf-text-xs); color: var(--tf-gray-500); flex-wrap: wrap; }
        .customer-card .cc-tags { display: flex; gap: 6px; flex-wrap: wrap; margin-top: var(--tf-sp-2); }
        .cc-tag {
            padding: 2px 10px; border-radius: 12px; font-size: 11px;
            font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em;
        }
        .cc-tag.solar { background: #FEF3C7; color: #92400E; }
        .cc-tag.commercial { background: var(--tf-blue-light); color: var(--tf-blue); }
        .cc-tag.residential { background: var(--tf-success-bg); color: var(--tf-success); }
        .cc-tag.government { background: #EDE9FE; color: #6D28D9; }
        .cc-tag.default { background: var(--tf-gray-100); color: var(--tf-gray-600); }
        .cc-project-count {
            background: var(--tf-blue-light); color: var(--tf-blue); padding: 2px 10px;
            border-radius: 12px; font-size: 11px; font-weight: 700;
        }

        /* Detail Drawer */
        .drawer-overlay {
            display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(15,23,42,0.4); z-index: 200;
        }
        .drawer-overlay.open { display: block; }
        .drawer {
            position: fixed; top: 0; right: -560px; width: 560px; height: 100vh;
            background: var(--tf-surface); box-shadow: -4px 0 24px rgba(0,0,0,0.15);
            z-index: 201; transition: right 0.3s var(--tf-ease); overflow-y: auto;
        }
        .drawer.open { right: 0; }
        .drawer-header {
            padding: var(--tf-sp-5) var(--tf-sp-6); border-bottom: 1px solid var(--tf-border);
            display: flex; justify-content: space-between; align-items: center;
            position: sticky; top: 0; background: var(--tf-surface); z-index: 10;
        }
        .drawer-body { padding: var(--tf-sp-6); }
        .drawer-close {
            background: none; border: none; font-size: 1.5rem; cursor: pointer;
            color: var(--tf-gray-400); padding: 4px 8px; border-radius: var(--tf-radius-sm);
        }
        .drawer-close:hover { background: var(--tf-gray-100); color: var(--tf-gray-700); }

        /* Detail sections */
        .detail-section { margin-bottom: var(--tf-sp-6); }
        .detail-section h3 {
            font-size: var(--tf-text-sm); font-weight: 700; color: var(--tf-gray-500);
            text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: var(--tf-sp-3);
            padding-bottom: var(--tf-sp-2); border-bottom: 1px solid var(--tf-border);
        }
        .detail-row { display: flex; justify-content: space-between; padding: 6px 0; font-size: var(--tf-text-sm); }
        .detail-row .label { color: var(--tf-gray-500); font-weight: 500; }
        .detail-row .value { color: var(--tf-gray-900); font-weight: 600; text-align: right; max-width: 60%; }
        .project-history-item {
            display: flex; justify-content: space-between; align-items: center;
            padding: 8px 12px; border: 1px solid var(--tf-border); border-radius: var(--tf-radius);
            margin-bottom: 6px; font-size: var(--tf-text-sm); cursor: pointer;
            transition: all var(--tf-duration) var(--tf-ease);
        }
        .project-history-item:hover { background: var(--tf-blue-light); border-color: var(--tf-blue); }
        .doc-upload-area {
            border: 2px dashed var(--tf-border); border-radius: var(--tf-radius);
            padding: var(--tf-sp-4); text-align: center; cursor: pointer;
            transition: all var(--tf-duration) var(--tf-ease); font-size: var(--tf-text-sm);
            color: var(--tf-gray-500);
        }
        .doc-upload-area:hover { border-color: var(--tf-blue); background: var(--tf-blue-light); }
        .doc-file {
            display: flex; justify-content: space-between; align-items: center;
            padding: 6px 10px; background: var(--tf-gray-50); border-radius: var(--tf-radius-sm);
            margin-top: 6px; font-size: var(--tf-text-xs);
        }
        .doc-file a { color: var(--tf-blue); text-decoration: none; font-weight: 600; }

        /* Notes */
        .notes-area {
            width: 100%; min-height: 80px; padding: 10px; border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius); font-family: var(--tf-font); font-size: var(--tf-text-sm);
            resize: vertical;
        }

        /* Global Search Overlay */
        .global-search-overlay {
            display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(15,23,42,0.5); z-index: 300; align-items: flex-start;
            justify-content: center; padding-top: 100px;
        }
        .global-search-overlay.open { display: flex; }
        .global-search-box {
            width: 600px; max-width: 90vw; background: var(--tf-surface);
            border-radius: var(--tf-radius-xl); box-shadow: var(--tf-shadow-lg);
            overflow: hidden;
        }
        .global-search-input {
            width: 100%; padding: 18px 20px; border: none; font-size: var(--tf-text-lg);
            outline: none; border-bottom: 1px solid var(--tf-border);
        }
        .global-search-results {
            max-height: 400px; overflow-y: auto; padding: var(--tf-sp-2);
        }
        .gsr-item {
            display: flex; align-items: center; gap: var(--tf-sp-3);
            padding: 10px 14px; border-radius: var(--tf-radius); cursor: pointer;
            transition: background var(--tf-duration) var(--tf-ease);
        }
        .gsr-item:hover, .gsr-item.active { background: var(--tf-blue-light); }
        .gsr-icon {
            width: 32px; height: 32px; border-radius: var(--tf-radius-sm);
            display: flex; align-items: center; justify-content: center; font-size: 14px; flex-shrink: 0;
        }
        .gsr-icon.project { background: var(--tf-blue-light); }
        .gsr-icon.customer { background: var(--tf-success-bg); }
        .gsr-icon.inventory { background: var(--tf-amber-light); }
        .gsr-title { font-weight: 600; font-size: var(--tf-text-sm); color: var(--tf-gray-900); }
        .gsr-sub { font-size: var(--tf-text-xs); color: var(--tf-gray-500); }
        .gsr-empty { padding: 20px; text-align: center; color: var(--tf-gray-400); font-size: var(--tf-text-sm); }

        @media (max-width: 768px) {
            .tf-topbar nav { display: none; }
            .container { padding: var(--tf-sp-4); }
            .customers-grid { grid-template-columns: 1fr; }
            .drawer { width: 100%; right: -100%; }
        }
    </style>
</head>
<body>
    <!-- TOP NAVIGATION BAR -->
    <div class="tf-topbar">
        <a href="/" class="tf-logo">
            <div class="tf-logo-icon">&#9878;</div>
            TITANFORGE
        </a>
        <nav>
            <a href="/">Dashboard</a>
            <a href="/sa">Structures America Estimator</a>
            <a href="/tc">Titan Carports Estimator</a>
            <a href="/customers" class="active">Customers</a>
        </nav>
        <div class="tf-user">
            <button onclick="openGlobalSearch()" style="background:none;border:1px solid rgba(255,255,255,0.2);color:#fff;padding:6px 14px;border-radius:var(--tf-radius);cursor:pointer;font-size:var(--tf-text-sm);margin-right:12px;display:flex;align-items:center;gap:6px;">
                &#128269; Search <kbd style="background:rgba(255,255,255,0.15);padding:1px 6px;border-radius:4px;font-size:10px;margin-left:4px;">Ctrl+K</kbd>
            </button>
            <div class="user-section">
                <span id="userName">User</span>
                <span class="role-badge" id="userRole">USER</span>
                <button class="logout-btn" onclick="location.href='/auth/logout'">Logout</button>
            </div>
        </div>
    </div>

    <!-- GLOBAL SEARCH OVERLAY -->
    <div class="global-search-overlay" id="globalSearchOverlay">
        <div class="global-search-box">
            <input type="text" class="global-search-input" id="globalSearchInput"
                   placeholder="Search projects, customers, inventory..." oninput="doGlobalSearch(this.value)">
            <div class="global-search-results" id="globalSearchResults">
                <div class="gsr-empty">Type to search across everything...</div>
            </div>
        </div>
    </div>

    <!-- MAIN CONTENT -->
    <div class="container">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:var(--tf-sp-6);">
            <div>
                <h1 style="font-size:var(--tf-text-2xl);font-weight:700;color:var(--tf-gray-900);">Customer Database</h1>
                <p style="color:var(--tf-gray-500);font-size:var(--tf-text-base);margin-top:var(--tf-sp-1);">Manage contacts, documents, and project history</p>
            </div>
            <button class="btn btn-primary" onclick="openAddCustomer()" id="addCustomerBtn" style="display:none;">+ New Customer</button>
        </div>

        <!-- Stats -->
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:var(--tf-sp-4);margin-bottom:var(--tf-sp-6);">
            <div class="stat-card">
                <div class="stat-icon blue">&#127970;</div>
                <div class="stat-info"><div class="stat-label">Total Customers</div><div class="stat-value" id="statTotal">0</div></div>
            </div>
            <div class="stat-card">
                <div class="stat-icon amber">&#9728;</div>
                <div class="stat-info"><div class="stat-label">Solar</div><div class="stat-value" id="statSolar">0</div></div>
            </div>
            <div class="stat-card">
                <div class="stat-icon green">&#127959;</div>
                <div class="stat-info"><div class="stat-label">Commercial</div><div class="stat-value" id="statCommercial">0</div></div>
            </div>
            <div class="stat-card">
                <div class="stat-icon purple">&#127968;</div>
                <div class="stat-info"><div class="stat-label">Residential</div><div class="stat-value" id="statResidential">0</div></div>
            </div>
        </div>

        <!-- Toolbar -->
        <div class="toolbar">
            <div class="search-wrap">
                <input type="text" class="search-box" id="custSearch" placeholder="Search customers..." oninput="filterCustomers()">
            </div>
            <button class="tag-filter" data-tag="all" onclick="setTagFilter('all', this)">All</button>
            <button class="tag-filter" data-tag="solar" onclick="setTagFilter('solar', this)">Solar</button>
            <button class="tag-filter" data-tag="commercial" onclick="setTagFilter('commercial', this)">Commercial</button>
            <button class="tag-filter" data-tag="residential" onclick="setTagFilter('residential', this)">Residential</button>
            <button class="tag-filter" data-tag="government" onclick="setTagFilter('government', this)">Government</button>
        </div>

        <!-- Customer Grid -->
        <div class="customers-grid" id="customersGrid"></div>
    </div>

    <!-- DETAIL DRAWER -->
    <div class="drawer-overlay" id="drawerOverlay" onclick="closeDrawer()"></div>
    <div class="drawer" id="drawer">
        <div class="drawer-header">
            <h2 id="drawerTitle" style="font-size:var(--tf-text-xl);font-weight:700;color:var(--tf-gray-900);"></h2>
            <div style="display:flex;gap:8px;align-items:center;">
                <button class="btn btn-outline" onclick="editCustomer()" id="editBtn" style="font-size:var(--tf-text-xs);padding:4px 12px;">Edit</button>
                <button class="drawer-close" onclick="closeDrawer()">&times;</button>
            </div>
        </div>
        <div class="drawer-body" id="drawerBody"></div>
    </div>

    <!-- ADD/EDIT MODAL -->
    <div class="modal-overlay" id="modalOverlay" style="display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(15,23,42,0.5);z-index:300;align-items:center;justify-content:center;">
        <div style="background:var(--tf-surface);border-radius:var(--tf-radius-xl);width:640px;max-width:95vw;max-height:90vh;overflow-y:auto;box-shadow:var(--tf-shadow-lg);">
            <div style="padding:var(--tf-sp-5) var(--tf-sp-6);border-bottom:1px solid var(--tf-border);display:flex;justify-content:space-between;align-items:center;">
                <h2 id="modalTitle" style="font-size:var(--tf-text-xl);font-weight:700;">New Customer</h2>
                <button onclick="closeModal()" style="background:none;border:none;font-size:1.5rem;cursor:pointer;color:var(--tf-gray-400);">&times;</button>
            </div>
            <div style="padding:var(--tf-sp-6);" id="modalBody">
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:var(--tf-sp-4);">
                    <div style="grid-column:span 2;">
                        <label class="form-label">Company Name *</label>
                        <input type="text" class="form-input" id="fCompany" placeholder="Company name">
                    </div>
                    <div>
                        <label class="form-label">Primary Contact Name</label>
                        <input type="text" class="form-input" id="fContactName" placeholder="Full name">
                    </div>
                    <div>
                        <label class="form-label">Phone</label>
                        <input type="text" class="form-input" id="fContactPhone" placeholder="(555) 123-4567">
                    </div>
                    <div>
                        <label class="form-label">Email</label>
                        <input type="email" class="form-input" id="fContactEmail" placeholder="email@company.com">
                    </div>
                    <div>
                        <label class="form-label">Title / Role</label>
                        <input type="text" class="form-input" id="fContactTitle" placeholder="Project Manager">
                    </div>
                    <div style="grid-column:span 2;">
                        <label class="form-label">Street Address</label>
                        <input type="text" class="form-input" id="fStreet" placeholder="123 Main St">
                    </div>
                    <div>
                        <label class="form-label">City</label>
                        <input type="text" class="form-input" id="fCity" placeholder="City">
                    </div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:var(--tf-sp-3);">
                        <div>
                            <label class="form-label">State</label>
                            <input type="text" class="form-input" id="fState" placeholder="NM" maxlength="2">
                        </div>
                        <div>
                            <label class="form-label">Zip</label>
                            <input type="text" class="form-input" id="fZip" placeholder="87501">
                        </div>
                    </div>
                    <div style="grid-column:span 2;">
                        <label class="form-label">Tags</label>
                        <div style="display:flex;gap:8px;flex-wrap:wrap;">
                            <label style="font-size:var(--tf-text-sm);cursor:pointer;"><input type="checkbox" class="tagCheck" value="solar"> Solar</label>
                            <label style="font-size:var(--tf-text-sm);cursor:pointer;"><input type="checkbox" class="tagCheck" value="commercial"> Commercial</label>
                            <label style="font-size:var(--tf-text-sm);cursor:pointer;"><input type="checkbox" class="tagCheck" value="residential"> Residential</label>
                            <label style="font-size:var(--tf-text-sm);cursor:pointer;"><input type="checkbox" class="tagCheck" value="government"> Government</label>
                        </div>
                    </div>
                    <div>
                        <label class="form-label">Payment Terms</label>
                        <select class="form-input" id="fPayTerms">
                            <option value="Net 30">Net 30</option>
                            <option value="Net 15">Net 15</option>
                            <option value="Net 45">Net 45</option>
                            <option value="Net 60">Net 60</option>
                            <option value="Due on Receipt">Due on Receipt</option>
                            <option value="Monthly Progress Billing">Monthly Progress Billing</option>
                        </select>
                    </div>
                    <div>
                        <label class="form-label">Credit Limit</label>
                        <input type="text" class="form-input" id="fCreditLimit" placeholder="$100,000">
                    </div>
                    <div>
                        <label class="form-label">Tax ID / EIN</label>
                        <input type="text" class="form-input" id="fTaxId" placeholder="XX-XXXXXXX">
                    </div>
                    <div>
                        <label class="form-label">Credit Terms</label>
                        <input type="text" class="form-input" id="fCreditTerms" placeholder="Credit terms">
                    </div>
                    <div style="grid-column:span 2;">
                        <label class="form-label">Notes</label>
                        <textarea class="form-input" id="fNotes" rows="3" placeholder="Internal notes about this customer..."></textarea>
                    </div>
                </div>

                <!-- Additional Contacts Section -->
                <div style="margin-top:var(--tf-sp-5);border-top:1px solid var(--tf-border);padding-top:var(--tf-sp-4);">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:var(--tf-sp-3);">
                        <label class="form-label" style="margin-bottom:0;">Additional Contacts</label>
                        <button class="btn btn-outline" onclick="addContactRow()" style="font-size:var(--tf-text-xs);padding:4px 10px;">+ Add Contact</button>
                    </div>
                    <div id="additionalContacts"></div>
                </div>
            </div>
            <div style="padding:var(--tf-sp-4) var(--tf-sp-6);border-top:1px solid var(--tf-border);display:flex;justify-content:flex-end;gap:var(--tf-sp-3);">
                <button class="btn btn-outline" onclick="closeModal()">Cancel</button>
                <button class="btn btn-primary" onclick="saveCustomer()" id="saveBtn">Save Customer</button>
            </div>
        </div>
    </div>

<script>
let allCustomers = [];
let activeTagFilter = 'all';
let editingCustomerId = null;
let currentDetail = null;

// ── Init ──
document.addEventListener('DOMContentLoaded', () => {
    loadCustomers();
    // Show add button for admin/estimator
    const role = document.cookie.match(/sa_user=([^;]+)/)?.[1] || '';
    document.getElementById('addCustomerBtn').style.display = '';
    // Check URL for pre-selected customer
    const params = new URLSearchParams(location.search);
    if (params.get('id')) {
        setTimeout(() => openDetail(params.get('id')), 500);
    }
});

// Keyboard shortcut
document.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') { e.preventDefault(); openGlobalSearch(); }
    if (e.key === 'Escape') { closeGlobalSearch(); closeDrawer(); closeModal(); }
});

async function loadCustomers() {
    try {
        const r = await fetch('/api/customers');
        const d = await r.json();
        if (d.ok) { allCustomers = d.customers; renderCustomers(); updateStats(); }
    } catch(e) { console.error(e); }
}

function updateStats() {
    document.getElementById('statTotal').textContent = allCustomers.length;
    document.getElementById('statSolar').textContent = allCustomers.filter(c => (c.tags||[]).includes('solar')).length;
    document.getElementById('statCommercial').textContent = allCustomers.filter(c => (c.tags||[]).includes('commercial')).length;
    document.getElementById('statResidential').textContent = allCustomers.filter(c => (c.tags||[]).includes('residential')).length;
}

function renderCustomers() {
    const q = document.getElementById('custSearch').value.toLowerCase();
    let filtered = allCustomers;
    if (q) {
        filtered = filtered.filter(c =>
            (c.company||'').toLowerCase().includes(q) ||
            (c.primary_contact?.name||'').toLowerCase().includes(q) ||
            (c.primary_contact?.email||'').toLowerCase().includes(q)
        );
    }
    if (activeTagFilter !== 'all') {
        filtered = filtered.filter(c => (c.tags||[]).map(t=>t.toLowerCase()).includes(activeTagFilter));
    }

    const grid = document.getElementById('customersGrid');
    if (!filtered.length) {
        grid.innerHTML = '<div style="grid-column:span 3;text-align:center;padding:60px 20px;color:var(--tf-gray-400);">'
            + '<div style="font-size:2rem;margin-bottom:8px;">&#128100;</div>'
            + '<div>No customers found. Click "+ New Customer" to add one.</div></div>';
        return;
    }

    grid.innerHTML = filtered.map(c => {
        const tags = (c.tags||[]).map(t => `<span class="cc-tag ${t}">${t}</span>`).join('');
        const contact = c.primary_contact || {};
        const contactStr = [contact.name, contact.phone, contact.email].filter(Boolean).join(' &middot; ');
        return `<div class="customer-card" onclick="openDetail('${c.id}')">
            <div class="cc-header">
                <div class="cc-company">${c.company || 'Unnamed'}</div>
            </div>
            <div class="cc-contact">${contactStr || 'No contact info'}</div>
            <div class="cc-meta">
                <span>&#128197; ${c.created_at ? new Date(c.created_at).toLocaleDateString() : ''}</span>
                <span>&#128179; ${c.payment_terms || 'Net 30'}</span>
            </div>
            <div class="cc-tags">${tags}</div>
        </div>`;
    }).join('');
}

function filterCustomers() { renderCustomers(); }

function setTagFilter(tag, btn) {
    activeTagFilter = tag;
    document.querySelectorAll('.tag-filter').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    renderCustomers();
}

// ── Add / Edit Modal ──
function openAddCustomer() {
    editingCustomerId = null;
    document.getElementById('modalTitle').textContent = 'New Customer';
    clearForm();
    document.getElementById('modalOverlay').style.display = 'flex';
}

function editCustomer() {
    if (!currentDetail) return;
    editingCustomerId = currentDetail.id;
    document.getElementById('modalTitle').textContent = 'Edit Customer';
    fillForm(currentDetail);
    closeDrawer();
    document.getElementById('modalOverlay').style.display = 'flex';
}

function clearForm() {
    ['fCompany','fContactName','fContactPhone','fContactEmail','fContactTitle',
     'fStreet','fCity','fState','fZip','fTaxId','fCreditLimit','fCreditTerms','fNotes'].forEach(id => {
        document.getElementById(id).value = '';
    });
    document.getElementById('fPayTerms').value = 'Net 30';
    document.querySelectorAll('.tagCheck').forEach(cb => cb.checked = false);
    document.getElementById('additionalContacts').innerHTML = '';
}

function fillForm(c) {
    document.getElementById('fCompany').value = c.company || '';
    document.getElementById('fContactName').value = c.primary_contact?.name || '';
    document.getElementById('fContactPhone').value = c.primary_contact?.phone || '';
    document.getElementById('fContactEmail').value = c.primary_contact?.email || '';
    document.getElementById('fContactTitle').value = c.primary_contact?.title || '';
    document.getElementById('fStreet').value = c.address?.street || '';
    document.getElementById('fCity').value = c.address?.city || '';
    document.getElementById('fState').value = c.address?.state || '';
    document.getElementById('fZip').value = c.address?.zip || '';
    document.getElementById('fPayTerms').value = c.payment_terms || 'Net 30';
    document.getElementById('fCreditLimit').value = c.credit_limit || '';
    document.getElementById('fTaxId').value = c.tax_id || '';
    document.getElementById('fCreditTerms').value = c.credit_terms || '';
    document.getElementById('fNotes').value = c.notes || '';
    document.querySelectorAll('.tagCheck').forEach(cb => {
        cb.checked = (c.tags||[]).includes(cb.value);
    });
    // Additional contacts
    const ac = document.getElementById('additionalContacts');
    ac.innerHTML = '';
    (c.contacts||[]).forEach(ct => addContactRow(ct));
}

function addContactRow(data) {
    const div = document.createElement('div');
    div.style.cssText = 'display:grid;grid-template-columns:1fr 1fr 1fr auto;gap:8px;margin-bottom:8px;';
    div.innerHTML = `
        <input type="text" class="form-input ac-name" placeholder="Name" value="${data?.name||''}">
        <input type="text" class="form-input ac-phone" placeholder="Phone" value="${data?.phone||''}">
        <input type="email" class="form-input ac-email" placeholder="Email" value="${data?.email||''}">
        <button onclick="this.parentElement.remove()" style="background:none;border:none;color:var(--tf-danger);cursor:pointer;font-size:1.2rem;padding:0 4px;">&times;</button>
    `;
    document.getElementById('additionalContacts').appendChild(div);
}

function closeModal() { document.getElementById('modalOverlay').style.display = 'none'; }

async function saveCustomer() {
    const company = document.getElementById('fCompany').value.trim();
    if (!company) { alert('Company name is required'); return; }

    const tags = [];
    document.querySelectorAll('.tagCheck:checked').forEach(cb => tags.push(cb.value));

    const contacts = [];
    document.querySelectorAll('#additionalContacts > div').forEach(row => {
        const n = row.querySelector('.ac-name').value.trim();
        const p = row.querySelector('.ac-phone').value.trim();
        const e = row.querySelector('.ac-email').value.trim();
        if (n || p || e) contacts.push({name:n, phone:p, email:e});
    });

    const payload = {
        company,
        primary_contact: {
            name: document.getElementById('fContactName').value.trim(),
            phone: document.getElementById('fContactPhone').value.trim(),
            email: document.getElementById('fContactEmail').value.trim(),
            title: document.getElementById('fContactTitle').value.trim(),
        },
        contacts,
        address: {
            street: document.getElementById('fStreet').value.trim(),
            city: document.getElementById('fCity').value.trim(),
            state: document.getElementById('fState').value.trim(),
            zip: document.getElementById('fZip').value.trim(),
        },
        tags,
        notes: document.getElementById('fNotes').value.trim(),
        payment_terms: document.getElementById('fPayTerms').value,
        credit_limit: document.getElementById('fCreditLimit').value.trim(),
        tax_id: document.getElementById('fTaxId').value.trim(),
        credit_terms: document.getElementById('fCreditTerms').value.trim(),
    };

    const url = editingCustomerId ? '/api/customers/update' : '/api/customers/create';
    if (editingCustomerId) payload.id = editingCustomerId;

    try {
        const r = await fetch(url, {
            method: 'POST', headers: {'Content-Type':'application/json'},
            body: JSON.stringify(payload)
        });
        const d = await r.json();
        if (d.ok) { closeModal(); loadCustomers(); }
        else alert(d.error || 'Save failed');
    } catch(e) { alert('Error saving customer'); }
}

// ── Detail Drawer ──
async function openDetail(cid) {
    try {
        const r = await fetch('/api/customers/detail?id=' + encodeURIComponent(cid));
        const d = await r.json();
        if (!d.ok) return;
        currentDetail = d.customer;
        renderDrawer(d.customer);
        document.getElementById('drawerOverlay').classList.add('open');
        document.getElementById('drawer').classList.add('open');
    } catch(e) { console.error(e); }
}

function closeDrawer() {
    document.getElementById('drawerOverlay').classList.remove('open');
    document.getElementById('drawer').classList.remove('open');
    currentDetail = null;
}

function renderDrawer(c) {
    document.getElementById('drawerTitle').textContent = c.company || 'Customer';
    const contact = c.primary_contact || {};
    const tags = (c.tags||[]).map(t => `<span class="cc-tag ${t}">${t}</span>`).join(' ');

    let html = `
        <div class="detail-section">
            <h3>Primary Contact</h3>
            <div class="detail-row"><span class="label">Name</span><span class="value">${contact.name||'—'}</span></div>
            <div class="detail-row"><span class="label">Title</span><span class="value">${contact.title||'—'}</span></div>
            <div class="detail-row"><span class="label">Phone</span><span class="value">${contact.phone ? '<a href="tel:'+contact.phone+'">'+contact.phone+'</a>' : '—'}</span></div>
            <div class="detail-row"><span class="label">Email</span><span class="value">${contact.email ? '<a href="mailto:'+contact.email+'">'+contact.email+'</a>' : '—'}</span></div>
        </div>`;

    if ((c.contacts||[]).length) {
        html += `<div class="detail-section"><h3>Additional Contacts</h3>`;
        c.contacts.forEach(ct => {
            html += `<div class="detail-row"><span class="label">${ct.name||''}</span><span class="value">${ct.phone||''} ${ct.email||''}</span></div>`;
        });
        html += `</div>`;
    }

    const addr = c.address || {};
    html += `
        <div class="detail-section">
            <h3>Address</h3>
            <div style="font-size:var(--tf-text-sm);color:var(--tf-gray-700);">
                ${addr.street||''}<br>${addr.city||''} ${addr.state||''} ${addr.zip||''}
            </div>
        </div>
        <div class="detail-section">
            <h3>Business Details</h3>
            <div class="detail-row"><span class="label">Payment Terms</span><span class="value">${c.payment_terms||'Net 30'}</span></div>
            <div class="detail-row"><span class="label">Credit Limit</span><span class="value">${c.credit_limit||'—'}</span></div>
            <div class="detail-row"><span class="label">Tax ID</span><span class="value">${c.tax_id||'—'}</span></div>
            <div class="detail-row"><span class="label">Credit Terms</span><span class="value">${c.credit_terms||'—'}</span></div>
            <div class="detail-row"><span class="label">Tags</span><span class="value">${tags||'None'}</span></div>
        </div>`;

    // Project history
    html += `<div class="detail-section"><h3>Project History</h3>`;
    if ((c.projects||[]).length) {
        c.projects.forEach(p => {
            html += `<div class="project-history-item" onclick="location.href='/project/${p.job_code}'">
                <div><div style="font-weight:600;">${p.project_name||p.job_code}</div><div style="font-size:11px;color:var(--tf-gray-500);">${p.job_code}</div></div>
                <span class="badge badge-info">${p.stage||''}</span>
            </div>`;
        });
    } else {
        html += `<div style="color:var(--tf-gray-400);font-size:var(--tf-text-sm);padding:12px 0;">No projects linked yet</div>`;
    }
    html += `</div>`;

    // Documents
    html += `<div class="detail-section"><h3>Documents</h3>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px;">
            ${['contract','insurance','tax_id','credit_terms','other'].map(t =>
                `<div class="doc-upload-area" onclick="uploadCustomerDoc('${c.id}','${t}')">
                    &#128206; Upload ${t.replace('_',' ')}</div>`
            ).join('')}
        </div>
        <div id="customerDocs"></div>
    </div>`;

    // Notes
    html += `<div class="detail-section"><h3>Notes</h3>
        <textarea class="notes-area" id="drawerNotes" onblur="saveNote('${c.id}')">${c.notes||''}</textarea>
    </div>`;

    document.getElementById('drawerBody').innerHTML = html;
    loadCustomerDocs(c.id);
}

async function loadCustomerDocs(cid) {
    try {
        const r = await fetch('/api/customers/docs?customer_id=' + encodeURIComponent(cid));
        const d = await r.json();
        if (!d.ok) return;
        const container = document.getElementById('customerDocs');
        let html = '';
        for (const [dtype, files] of Object.entries(d.docs)) {
            if (files.length) {
                html += `<div style="margin-bottom:8px;font-size:var(--tf-text-xs);font-weight:700;color:var(--tf-gray-500);text-transform:uppercase;">${dtype.replace('_',' ')}</div>`;
                files.forEach(f => {
                    html += `<div class="doc-file"><a href="${f.url}" target="_blank">${f.name}</a><span>${(f.size/1024).toFixed(1)} KB</span></div>`;
                });
            }
        }
        container.innerHTML = html || '<div style="color:var(--tf-gray-400);font-size:var(--tf-text-sm);">No documents uploaded</div>';
    } catch(e) {}
}

function uploadCustomerDoc(cid, dtype) {
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.onchange = async () => {
        const fd = new FormData();
        fd.append('customer_id', cid);
        fd.append('doc_type', dtype);
        for (const f of input.files) fd.append('file', f);
        try {
            const r = await fetch('/api/customers/docs/upload', {method:'POST', body:fd});
            const d = await r.json();
            if (d.ok) loadCustomerDocs(cid);
        } catch(e) { alert('Upload failed'); }
    };
    input.click();
}

async function saveNote(cid) {
    const notes = document.getElementById('drawerNotes')?.value || '';
    try {
        await fetch('/api/customers/update', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({id: cid, notes})
        });
    } catch(e) {}
}

// ── Global Search ──
let searchTimeout = null;
function openGlobalSearch() {
    document.getElementById('globalSearchOverlay').classList.add('open');
    document.getElementById('globalSearchInput').value = '';
    document.getElementById('globalSearchInput').focus();
    document.getElementById('globalSearchResults').innerHTML = '<div class="gsr-empty">Type to search across everything...</div>';
}

function closeGlobalSearch() {
    document.getElementById('globalSearchOverlay').classList.remove('open');
}

document.getElementById('globalSearchOverlay').addEventListener('click', e => {
    if (e.target.id === 'globalSearchOverlay') closeGlobalSearch();
});

function doGlobalSearch(q) {
    clearTimeout(searchTimeout);
    if (!q || q.length < 2) {
        document.getElementById('globalSearchResults').innerHTML = '<div class="gsr-empty">Type to search across everything...</div>';
        return;
    }
    searchTimeout = setTimeout(async () => {
        try {
            const r = await fetch('/api/search?q=' + encodeURIComponent(q));
            const d = await r.json();
            const container = document.getElementById('globalSearchResults');
            if (!d.results?.length) {
                container.innerHTML = '<div class="gsr-empty">No results found</div>';
                return;
            }
            container.innerHTML = d.results.map(r => {
                const icons = {project:'&#128204;', customer:'&#128100;', inventory:'&#128230;'};
                return `<a href="${r.url}" style="text-decoration:none;color:inherit;">
                    <div class="gsr-item">
                        <div class="gsr-icon ${r.type}">${icons[r.type]||'&#128196;'}</div>
                        <div>
                            <div class="gsr-title">${r.title}</div>
                            <div class="gsr-sub">${r.subtitle||''} ${r.stage ? '<span class="badge badge-info" style="font-size:10px;padding:1px 6px;">'+r.stage+'</span>' : ''}</div>
                        </div>
                    </div>
                </a>`;
            }).join('');
        } catch(e) { console.error(e); }
    }, 300);
}
</script>
</body>
</html>
"""
