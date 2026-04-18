"""
TitanForge v4 — Workflow Builder
==================================
Visual workflow definitions, step sequences, approval chains, status transitions.
"""

WORKFLOWS_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a;
        --tf-card: #1e293b;
        --tf-text: #e2e8f0;
        --tf-muted: #94a3b8;
        --tf-gold: #d4a843;
        --tf-blue: #3b82f6;
    }
    .wf-container {
        max-width: 1400px; margin: 0 auto; padding: 24px 32px;
        font-family: 'Inter', 'Segoe UI', sans-serif; color: var(--tf-text);
    }
    .page-header { margin-bottom: 32px; }
    .page-header h1 { font-size: 28px; font-weight: 800; margin: 0 0 6px 0; }
    .page-header p { font-size: 14px; color: var(--tf-muted); margin: 0; }
    .toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
    .toolbar input[type="text"] { background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px 16px; color: var(--tf-text); font-size: 14px; width: 260px; }
    .toolbar input::placeholder { color: var(--tf-muted); }
    .btn-gold { background: var(--tf-gold); color: #0f172a; border: none; border-radius: 8px; padding: 10px 20px; font-weight: 700; font-size: 14px; cursor: pointer; }
    .btn-gold:hover { opacity: 0.9; }
    .btn-blue { background: var(--tf-blue); color: #fff; border: none; border-radius: 8px; padding: 10px 20px; font-weight: 700; font-size: 14px; cursor: pointer; }
    .btn-outline { background: transparent; color: var(--tf-muted); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 10px 20px; font-weight: 600; font-size: 14px; cursor: pointer; }
    .btn-outline:hover { border-color: var(--tf-gold); color: var(--tf-gold); }
    .btn-sm { padding: 6px 14px; font-size: 13px; border-radius: 6px; }
    .wf-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); gap: 20px; }
    .wf-card {
        background: var(--tf-card); border-radius: 12px; border: 1px solid rgba(255,255,255,0.06);
        padding: 20px; cursor: pointer; transition: border-color 0.2s;
    }
    .wf-card:hover { border-color: var(--tf-blue); }
    .wf-card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
    .wf-card-header h3 { font-size: 16px; font-weight: 700; margin: 0; }
    .wf-status { display: inline-block; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
    .wf-status-active { background: rgba(34,197,94,0.2); color: #4ade80; }
    .wf-status-draft { background: rgba(148,163,184,0.2); color: #94a3b8; }
    .wf-status-disabled { background: rgba(239,68,68,0.2); color: #f87171; }
    .wf-card p { font-size: 13px; color: var(--tf-muted); margin: 0 0 16px 0; }
    .wf-steps { display: flex; align-items: center; gap: 4px; flex-wrap: wrap; }
    .wf-step {
        background: var(--tf-bg); border-radius: 6px; padding: 5px 10px; font-size: 12px;
        color: var(--tf-text); white-space: nowrap;
    }
    .wf-arrow { color: var(--tf-muted); font-size: 14px; }
    .wf-card-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(255,255,255,0.04); font-size: 12px; color: var(--tf-muted); }
    .empty-state { text-align: center; padding: 60px 20px; color: var(--tf-muted); }
    .empty-state h3 { font-size: 18px; margin-bottom: 8px; color: var(--tf-text); }
    .loading { text-align: center; padding: 40px; color: var(--tf-muted); }
    .modal-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 1000; justify-content: center; align-items: center; }
    .modal-overlay.active { display: flex; }
    .modal { background: var(--tf-card); border-radius: 12px; padding: 28px; width: 600px; max-width: 90vw; border: 1px solid rgba(255,255,255,0.1); max-height: 80vh; overflow-y: auto; }
    .modal h2 { font-size: 20px; margin: 0 0 20px 0; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 24px; }
    .form-group { margin-bottom: 16px; }
    .form-group label { display: block; font-size: 13px; font-weight: 600; color: var(--tf-muted); margin-bottom: 6px; }
    .form-group input, .form-group select, .form-group textarea {
        width: 100%; background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px; font-family: inherit; box-sizing: border-box;
    }
    .form-group textarea { min-height: 60px; resize: vertical; }
    .step-builder { margin-top: 12px; }
    .step-item { display: flex; gap: 8px; align-items: center; margin-bottom: 8px; }
    .step-item input { flex: 1; }
    .step-item select { width: 140px; }
    .btn-remove { background: rgba(239,68,68,0.2); color: #f87171; border: none; border-radius: 6px; padding: 8px 12px; cursor: pointer; font-size: 13px; }

/* ── Responsive ── */
@media (max-width: 768px) {
    .page-header h1 { font-size: 22px; }
    .toolbar { flex-direction: column; align-items: stretch; }
    .toolbar input[type="text"] { width: 100%; }
    .modal-overlay .modal, .modal { width: 95%; max-width: 95vw; margin: 20px auto; padding: 20px; }
    .wf-grid { grid-template-columns: 1fr; }
    .step-builder { padding: 12px; }
    .step-item { flex-direction: column; gap: 8px; }
}
@media (max-width: 480px) {
    .toolbar { gap: 8px; }
    .wf-grid { grid-template-columns: 1fr; }
    .btn-gold, .btn-blue { width: 100%; text-align: center; }
}
</style>

<div class="wf-container">
    <div class="page-header">
        <h1>Workflow Builder</h1>
        <p>Define and manage workflow automations, approval chains, and status transitions</p>
    </div>
    <div class="toolbar">
        <input type="text" id="wfSearch" placeholder="Search workflows..." oninput="filterWorkflows()">
        <button class="btn-gold" onclick="openNewWorkflow()">+ New Workflow</button>
    </div>
    <div class="wf-grid" id="wfGrid">
        <div class="loading">Loading workflows...</div>
    </div>
</div>

<div class="modal-overlay" id="wfModal">
    <div class="modal">
        <h2 id="wfModalTitle">New Workflow</h2>
        <input type="hidden" id="wfId">
        <div class="form-group"><label>Workflow Name</label><input type="text" id="wfName" placeholder="e.g. Quote Approval"></div>
        <div class="form-group"><label>Description</label><textarea id="wfDesc" placeholder="What this workflow does..."></textarea></div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div class="form-group"><label>Trigger</label><select id="wfTrigger"><option value="manual">Manual</option><option value="status_change">Status Change</option><option value="creation">On Creation</option><option value="schedule">Scheduled</option></select></div>
            <div class="form-group"><label>Status</label><select id="wfStatus"><option value="active">Active</option><option value="draft">Draft</option><option value="disabled">Disabled</option></select></div>
        </div>
        <div class="form-group">
            <label>Steps</label>
            <div class="step-builder" id="stepBuilder"></div>
            <button class="btn-outline btn-sm" onclick="addStep()" style="margin-top:8px;">+ Add Step</button>
        </div>
        <div class="modal-actions">
            <button class="btn-outline" onclick="closeModal('wfModal')">Cancel</button>
            <button class="btn-gold" onclick="saveWorkflow()">Save Workflow</button>
        </div>
    </div>
</div>

<script>
let allWorkflows = [];
let stepCount = 0;

function openModal(id) { document.getElementById(id).classList.add('active'); }
function closeModal(id) { document.getElementById(id).classList.remove('active'); }
document.querySelectorAll('.modal-overlay').forEach(m => m.addEventListener('click', function(e) { if (e.target === this) closeModal(this.id); }));

function addStep(name, type) {
    stepCount++;
    const div = document.createElement('div');
    div.className = 'step-item';
    div.id = 'step-' + stepCount;
    div.innerHTML = '<input type="text" placeholder="Step name" value="' + (name || '') + '">' +
        '<select><option value="action"' + (type==='action'?' selected':'') + '>Action</option><option value="approval"' + (type==='approval'?' selected':'') + '>Approval</option><option value="notification"' + (type==='notification'?' selected':'') + '>Notification</option><option value="condition"' + (type==='condition'?' selected':'') + '>Condition</option></select>' +
        '<button class="btn-remove" onclick="this.parentElement.remove()">X</button>';
    document.getElementById('stepBuilder').appendChild(div);
}

function openNewWorkflow() {
    document.getElementById('wfModalTitle').textContent = 'New Workflow';
    document.getElementById('wfId').value = '';
    document.getElementById('wfName').value = '';
    document.getElementById('wfDesc').value = '';
    document.getElementById('wfTrigger').value = 'manual';
    document.getElementById('wfStatus').value = 'active';
    document.getElementById('stepBuilder').innerHTML = '';
    stepCount = 0;
    addStep('Review', 'action');
    addStep('Approve', 'approval');
    openModal('wfModal');
}

function editWorkflow(wf) {
    document.getElementById('wfModalTitle').textContent = 'Edit Workflow';
    document.getElementById('wfId').value = wf.id || '';
    document.getElementById('wfName').value = wf.name || '';
    document.getElementById('wfDesc').value = wf.description || '';
    document.getElementById('wfTrigger').value = wf.trigger || 'manual';
    document.getElementById('wfStatus').value = wf.status || 'draft';
    document.getElementById('stepBuilder').innerHTML = '';
    stepCount = 0;
    (wf.steps || []).forEach(s => addStep(s.name, s.type));
    openModal('wfModal');
}

function renderWorkflows(workflows) {
    const grid = document.getElementById('wfGrid');
    if (!workflows.length) {
        grid.innerHTML = '<div class="empty-state" style="grid-column:1/-1;"><h3>No workflows defined</h3><p>Create a workflow to automate processes.</p></div>';
        return;
    }
    grid.innerHTML = workflows.map(wf => {
        const statusCls = wf.status === 'active' ? 'wf-status-active' : (wf.status === 'disabled' ? 'wf-status-disabled' : 'wf-status-draft');
        const steps = (wf.steps || []).map(s => '<span class="wf-step">' + (s.name || s) + '</span>').join('<span class="wf-arrow">&rarr;</span>');
        return '<div class="wf-card" onclick=\'editWorkflow(' + JSON.stringify(wf).replace(/'/g,"&#39;") + ')\'>' +
            '<div class="wf-card-header"><h3>' + (wf.name || 'Unnamed') + '</h3><span class="wf-status ' + statusCls + '">' + (wf.status || 'draft') + '</span></div>' +
            '<p>' + (wf.description || 'No description') + '</p>' +
            '<div class="wf-steps">' + (steps || '<span style="color:var(--tf-muted);font-size:12px;">No steps defined</span>') + '</div>' +
            '<div class="wf-card-footer"><span>Trigger: ' + (wf.trigger || 'Manual') + '</span><span>' + (wf.steps || []).length + ' steps</span></div></div>';
    }).join('');
}

function filterWorkflows() {
    const search = document.getElementById('wfSearch').value.toLowerCase();
    const filtered = allWorkflows.filter(w => !search || (w.name||'').toLowerCase().includes(search) || (w.description||'').toLowerCase().includes(search));
    renderWorkflows(filtered);
}

async function loadWorkflows() {
    try {
        const resp = await fetch('/api/workflows');
        const data = await resp.json();
        allWorkflows = Array.isArray(data) ? data : (data.workflows || []);
        renderWorkflows(allWorkflows);
    } catch(e) { renderWorkflows([]); }
}

async function saveWorkflow() {
    const steps = [];
    document.querySelectorAll('.step-item').forEach(el => {
        const name = el.querySelector('input').value;
        const type = el.querySelector('select').value;
        if (name) steps.push({ name, type });
    });
    const payload = {
        id: document.getElementById('wfId').value || undefined,
        name: document.getElementById('wfName').value,
        description: document.getElementById('wfDesc').value,
        trigger: document.getElementById('wfTrigger').value,
        status: document.getElementById('wfStatus').value,
        steps: steps
    };
    if (!payload.name) { alert('Name is required'); return; }
    try {
        await fetch('/api/workflows', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
        closeModal('wfModal');
        loadWorkflows();
    } catch(e) { alert('Error: ' + e.message); }
}

loadWorkflows();
</script>
"""
