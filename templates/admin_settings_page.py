"""
TitanForge v4 — Admin Settings
================================
System settings: company info, tax rates, markup, email, notifications, backup/restore, feature toggles.
"""

ADMIN_SETTINGS_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a;
        --tf-card: #1e293b;
        --tf-text: #e2e8f0;
        --tf-muted: #94a3b8;
        --tf-gold: #d4a843;
        --tf-blue: #3b82f6;
    }
    .settings-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 24px 32px;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        color: var(--tf-text);
    }
    .page-header { margin-bottom: 32px; }
    .page-header h1 { font-size: 28px; font-weight: 800; margin: 0 0 6px 0; color: var(--tf-text); }
    .page-header p { font-size: 14px; color: var(--tf-muted); margin: 0; }
    .toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
    .btn-gold { background: var(--tf-gold); color: #0f172a; border: none; border-radius: 8px; padding: 10px 20px; font-weight: 700; font-size: 14px; cursor: pointer; }
    .btn-gold:hover { opacity: 0.9; }
    .btn-blue { background: var(--tf-blue); color: #fff; border: none; border-radius: 8px; padding: 10px 20px; font-weight: 700; font-size: 14px; cursor: pointer; }
    .btn-blue:hover { opacity: 0.9; }
    .btn-outline { background: transparent; color: var(--tf-muted); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 10px 20px; font-weight: 600; font-size: 14px; cursor: pointer; }
    .btn-outline:hover { border-color: var(--tf-gold); color: var(--tf-gold); }
    .settings-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    @media (max-width: 900px) { .settings-grid { grid-template-columns: 1fr; } }
    .settings-card {
        background: var(--tf-card);
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06);
        padding: 24px;
    }
    .settings-card h3 { font-size: 16px; font-weight: 700; margin: 0 0 4px 0; color: var(--tf-text); }
    .settings-card .card-desc { font-size: 13px; color: var(--tf-muted); margin: 0 0 20px 0; }
    .form-group { margin-bottom: 16px; }
    .form-group label { display: block; font-size: 13px; font-weight: 600; color: var(--tf-muted); margin-bottom: 6px; }
    .form-group input, .form-group select, .form-group textarea {
        width: 100%; background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px; font-family: inherit; box-sizing: border-box;
    }
    .form-group textarea { min-height: 80px; resize: vertical; }
    .form-group input:focus, .form-group select:focus, .form-group textarea:focus { outline: none; border-color: var(--tf-blue); }
    .toggle-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.04); }
    .toggle-row:last-child { border-bottom: none; }
    .toggle-label { font-size: 14px; color: var(--tf-text); }
    .toggle-label small { display: block; font-size: 12px; color: var(--tf-muted); margin-top: 2px; }
    .toggle-switch { position: relative; width: 44px; height: 24px; cursor: pointer; }
    .toggle-switch input { opacity: 0; width: 0; height: 0; }
    .toggle-slider {
        position: absolute; top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(255,255,255,0.1); border-radius: 24px; transition: 0.3s;
    }
    .toggle-slider:before {
        content: ''; position: absolute; height: 18px; width: 18px; left: 3px; bottom: 3px;
        background: #fff; border-radius: 50%; transition: 0.3s;
    }
    .toggle-switch input:checked + .toggle-slider { background: var(--tf-blue); }
    .toggle-switch input:checked + .toggle-slider:before { transform: translateX(20px); }
    .save-status { font-size: 13px; color: #4ade80; display: none; margin-left: 12px; }
    .modal-overlay {
        display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 1000;
        justify-content: center; align-items: center;
    }
    .modal-overlay.active { display: flex; }
    .modal {
        background: var(--tf-card); border-radius: 12px; padding: 28px; width: 500px; max-width: 90vw;
        border: 1px solid rgba(255,255,255,0.1); max-height: 80vh; overflow-y: auto;
    }
    .modal h2 { font-size: 20px; margin: 0 0 20px 0; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 24px; }
</style>

<div class="settings-container">
    <div class="page-header">
        <h1>Admin Settings</h1>
        <p>Configure system settings, company information, and feature toggles</p>
    </div>
    <div class="toolbar">
        <div style="display:flex;gap:10px;">
            <button class="btn-outline" onclick="exportSettings()">Export Settings</button>
            <button class="btn-outline" onclick="openModal('importModal')">Import / Restore</button>
        </div>
        <div style="display:flex;align-items:center;">
            <span id="saveStatus" class="save-status">Settings saved</span>
            <button class="btn-gold" onclick="saveAllSettings()">Save All Changes</button>
        </div>
    </div>
    <div class="settings-grid">
        <div class="settings-card">
            <h3>Company Information</h3>
            <p class="card-desc">Basic company details used across the system</p>
            <div class="form-group"><label>Company Name</label><input type="text" id="companyName" value="Titan Carports"></div>
            <div class="form-group"><label>Address</label><textarea id="companyAddress">123 Industrial Blvd, City, ST 12345</textarea></div>
            <div class="form-group"><label>Phone</label><input type="text" id="companyPhone" value=""></div>
            <div class="form-group"><label>Email</label><input type="email" id="companyEmail" value=""></div>
        </div>
        <div class="settings-card">
            <h3>Financial Defaults</h3>
            <p class="card-desc">Default tax rates, markup percentages, and pricing</p>
            <div class="form-group"><label>Default Tax Rate (%)</label><input type="number" id="taxRate" value="7.5" step="0.1"></div>
            <div class="form-group"><label>Default Markup (%)</label><input type="number" id="markupRate" value="35" step="1"></div>
            <div class="form-group"><label>Default Labor Rate ($/hr)</label><input type="number" id="laborRate" value="65" step="1"></div>
            <div class="form-group"><label>Currency</label><select id="currency"><option value="USD">USD ($)</option><option value="CAD">CAD ($)</option></select></div>
        </div>
        <div class="settings-card">
            <h3>Email Settings</h3>
            <p class="card-desc">SMTP configuration for outgoing emails</p>
            <div class="form-group"><label>SMTP Host</label><input type="text" id="smtpHost" value=""></div>
            <div class="form-group"><label>SMTP Port</label><input type="number" id="smtpPort" value="587"></div>
            <div class="form-group"><label>SMTP Username</label><input type="text" id="smtpUser" value=""></div>
            <div class="form-group"><label>SMTP Password</label><input type="password" id="smtpPass" value=""></div>
            <div class="form-group"><label>From Address</label><input type="email" id="smtpFrom" value=""></div>
            <button class="btn-outline" onclick="testEmail()" style="margin-top:4px;">Send Test Email</button>
        </div>
        <div class="settings-card">
            <h3>Notification Preferences</h3>
            <p class="card-desc">Control when and how notifications are sent</p>
            <div class="toggle-row">
                <div class="toggle-label">Quote Approved<small>Notify when a quote is approved</small></div>
                <label class="toggle-switch"><input type="checkbox" checked data-key="notify_quote_approved"><span class="toggle-slider"></span></label>
            </div>
            <div class="toggle-row">
                <div class="toggle-label">NCR Created<small>Notify QC manager on new NCR</small></div>
                <label class="toggle-switch"><input type="checkbox" checked data-key="notify_ncr_created"><span class="toggle-slider"></span></label>
            </div>
            <div class="toggle-row">
                <div class="toggle-label">Shipment Delivered<small>Notify PM on delivery confirmation</small></div>
                <label class="toggle-switch"><input type="checkbox" checked data-key="notify_shipment_delivered"><span class="toggle-slider"></span></label>
            </div>
            <div class="toggle-row">
                <div class="toggle-label">Daily Summary<small>Send daily activity summary email</small></div>
                <label class="toggle-switch"><input type="checkbox" data-key="notify_daily_summary"><span class="toggle-slider"></span></label>
            </div>
        </div>
        <div class="settings-card" style="grid-column: 1 / -1;">
            <h3>Feature Toggles</h3>
            <p class="card-desc">Enable or disable system modules</p>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:0 32px;">
                <div class="toggle-row">
                    <div class="toggle-label">Customer Portal<small>Allow customer login for project status</small></div>
                    <label class="toggle-switch"><input type="checkbox" checked data-key="feat_portal"><span class="toggle-slider"></span></label>
                </div>
                <div class="toggle-row">
                    <div class="toggle-label">QC Module<small>Quality control inspections and NCRs</small></div>
                    <label class="toggle-switch"><input type="checkbox" checked data-key="feat_qc"><span class="toggle-slider"></span></label>
                </div>
                <div class="toggle-row">
                    <div class="toggle-label">Traceability<small>Material heat number tracking</small></div>
                    <label class="toggle-switch"><input type="checkbox" checked data-key="feat_traceability"><span class="toggle-slider"></span></label>
                </div>
                <div class="toggle-row">
                    <div class="toggle-label">AISC Compliance<small>Certification tracking features</small></div>
                    <label class="toggle-switch"><input type="checkbox" data-key="feat_aisc"><span class="toggle-slider"></span></label>
                </div>
                <div class="toggle-row">
                    <div class="toggle-label">Workflow Engine<small>Custom workflow automation</small></div>
                    <label class="toggle-switch"><input type="checkbox" data-key="feat_workflows"><span class="toggle-slider"></span></label>
                </div>
                <div class="toggle-row">
                    <div class="toggle-label">Barcode Scanner<small>QR/barcode scanning features</small></div>
                    <label class="toggle-switch"><input type="checkbox" checked data-key="feat_scanner"><span class="toggle-slider"></span></label>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="modal-overlay" id="importModal">
    <div class="modal">
        <h2>Import / Restore Settings</h2>
        <p style="color:var(--tf-muted);font-size:14px;">Upload a previously exported settings JSON file to restore configuration.</p>
        <div class="form-group"><label>Settings File</label><input type="file" id="importFile" accept=".json" style="padding:8px;"></div>
        <div class="modal-actions">
            <button class="btn-outline" onclick="closeModal('importModal')">Cancel</button>
            <button class="btn-gold" onclick="importSettings()">Import</button>
        </div>
    </div>
</div>

<script>
function openModal(id) { document.getElementById(id).classList.add('active'); }
function closeModal(id) { document.getElementById(id).classList.remove('active'); }
document.querySelectorAll('.modal-overlay').forEach(m => m.addEventListener('click', function(e) { if (e.target === this) this.classList.remove('active'); }));

async function loadSettings() {
    try {
        const resp = await fetch('/api/admin/settings');
        if (!resp.ok) return;
        const data = await resp.json();
        if (data.company_name) document.getElementById('companyName').value = data.company_name;
        if (data.company_address) document.getElementById('companyAddress').value = data.company_address;
        if (data.company_phone) document.getElementById('companyPhone').value = data.company_phone;
        if (data.company_email) document.getElementById('companyEmail').value = data.company_email;
        if (data.tax_rate != null) document.getElementById('taxRate').value = data.tax_rate;
        if (data.markup_rate != null) document.getElementById('markupRate').value = data.markup_rate;
        if (data.labor_rate != null) document.getElementById('laborRate').value = data.labor_rate;
        if (data.toggles) {
            document.querySelectorAll('.toggle-switch input').forEach(inp => {
                if (data.toggles[inp.dataset.key] !== undefined) inp.checked = data.toggles[inp.dataset.key];
            });
        }
    } catch(e) { console.log('Settings load:', e); }
}

async function saveAllSettings() {
    const toggles = {};
    document.querySelectorAll('.toggle-switch input').forEach(inp => { toggles[inp.dataset.key] = inp.checked; });
    const payload = {
        company_name: document.getElementById('companyName').value,
        company_address: document.getElementById('companyAddress').value,
        company_phone: document.getElementById('companyPhone').value,
        company_email: document.getElementById('companyEmail').value,
        tax_rate: parseFloat(document.getElementById('taxRate').value),
        markup_rate: parseFloat(document.getElementById('markupRate').value),
        labor_rate: parseFloat(document.getElementById('laborRate').value),
        currency: document.getElementById('currency').value,
        smtp_host: document.getElementById('smtpHost').value,
        smtp_port: parseInt(document.getElementById('smtpPort').value),
        smtp_user: document.getElementById('smtpUser').value,
        smtp_from: document.getElementById('smtpFrom').value,
        toggles: toggles
    };
    try {
        await fetch('/api/admin/settings', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
        const el = document.getElementById('saveStatus');
        el.style.display = 'inline'; setTimeout(() => el.style.display = 'none', 3000);
    } catch(e) { alert('Failed to save: ' + e.message); }
}

function exportSettings() {
    const data = {
        company_name: document.getElementById('companyName').value,
        tax_rate: document.getElementById('taxRate').value,
        markup_rate: document.getElementById('markupRate').value,
        exported_at: new Date().toISOString()
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob); a.download = 'titanforge_settings.json'; a.click();
}

async function testEmail() {
    try {
        const resp = await fetch('/api/admin/test-email', { method: 'POST' });
        alert(resp.ok ? 'Test email sent!' : 'Failed to send test email');
    } catch(e) { alert('Error: ' + e.message); }
}

function importSettings() {
    const file = document.getElementById('importFile').files[0];
    if (!file) { alert('Please select a file'); return; }
    const reader = new FileReader();
    reader.onload = async function(e) {
        try {
            const data = JSON.parse(e.target.result);
            await fetch('/api/admin/settings', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data) });
            closeModal('importModal');
            loadSettings();
            alert('Settings restored successfully');
        } catch(err) { alert('Invalid file: ' + err.message); }
    };
    reader.readAsText(file);
}

loadSettings();
</script>
"""
