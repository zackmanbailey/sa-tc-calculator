from templates.shared_styles import DESIGN_SYSTEM_CSS

QC_PAGE_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TitanForge — QC Dashboard</title>
    <style>
""" + DESIGN_SYSTEM_CSS + r"""

        .container { max-width: 1400px; margin: 0 auto; padding: var(--tf-sp-6) var(--tf-sp-8); }

        /* QC Tabs */
        .qc-tabs { display: flex; gap: 0; border-bottom: 2px solid var(--tf-border); margin-bottom: var(--tf-sp-6); }
        .qc-tab {
            padding: 10px 20px; font-size: var(--tf-text-sm); font-weight: 600;
            color: var(--tf-gray-500); background: none; border: none;
            border-bottom: 2px solid transparent; margin-bottom: -2px;
            cursor: pointer; transition: all var(--tf-duration) var(--tf-ease);
        }
        .qc-tab:hover { color: var(--tf-gray-700); }
        .qc-tab.active { color: var(--tf-blue); border-bottom-color: var(--tf-blue); }
        .qc-tab .count-badge {
            display: inline-block; background: var(--tf-gray-200); color: var(--tf-gray-600);
            border-radius: 10px; padding: 1px 8px; font-size: 11px; margin-left: 6px;
        }
        .qc-tab.active .count-badge { background: var(--tf-blue-light); color: var(--tf-blue); }
        .qc-section { display: none; }
        .qc-section.active { display: block; }

        /* Inspection cards */
        .insp-card {
            background: var(--tf-surface); border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-lg); padding: var(--tf-sp-5);
            margin-bottom: var(--tf-sp-4); transition: all var(--tf-duration) var(--tf-ease);
        }
        .insp-card:hover { box-shadow: var(--tf-shadow-md); }
        .insp-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: var(--tf-sp-3); }
        .insp-title { font-weight: 700; font-size: var(--tf-text-md); color: var(--tf-gray-900); }
        .insp-standard { font-size: var(--tf-text-xs); color: var(--tf-gray-500); margin-top: 2px; }
        .insp-meta { display: flex; gap: var(--tf-sp-4); font-size: var(--tf-text-xs); color: var(--tf-gray-500); margin-bottom: var(--tf-sp-3); flex-wrap: wrap; }

        /* Status badges */
        .status-badge { padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
        .status-badge.in_progress { background: var(--tf-amber-light); color: var(--tf-warning); }
        .status-badge.passed { background: var(--tf-success-bg); color: var(--tf-success); }
        .status-badge.failed { background: var(--tf-danger-bg); color: var(--tf-danger); }
        .status-badge.incomplete { background: var(--tf-gray-100); color: var(--tf-gray-500); }
        .status-badge.open { background: var(--tf-danger-bg); color: var(--tf-danger); }
        .status-badge.closed { background: var(--tf-success-bg); color: var(--tf-success); }
        .status-badge.under_review { background: var(--tf-amber-light); color: var(--tf-warning); }
        .status-badge.corrective_action { background: var(--tf-info-bg); color: var(--tf-info); }

        /* Severity */
        .severity-badge { padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; text-transform: uppercase; }
        .severity-badge.minor { background: var(--tf-amber-light); color: #92400E; }
        .severity-badge.major { background: #FEE2E2; color: #991B1B; }
        .severity-badge.critical { background: #7F1D1D; color: #FEE2E2; }

        /* Checklist */
        .checklist-grid { display: grid; gap: 8px; }
        .check-item {
            display: flex; align-items: center; gap: 10px; padding: 8px 12px;
            border: 1px solid var(--tf-border); border-radius: var(--tf-radius); font-size: var(--tf-text-sm);
            background: var(--tf-surface); transition: all var(--tf-duration) var(--tf-ease);
        }
        .check-item.checked { background: var(--tf-success-bg); border-color: var(--tf-success); }
        .check-item.failed-item { background: var(--tf-danger-bg); border-color: var(--tf-danger); }
        .check-item label { flex: 1; cursor: pointer; }
        .check-item input[type="checkbox"] { width: 18px; height: 18px; cursor: pointer; accent-color: var(--tf-success); }
        .check-item select, .check-item input[type="text"] {
            padding: 4px 8px; border: 1px solid var(--tf-border); border-radius: 4px;
            font-size: var(--tf-text-xs); max-width: 220px;
        }

        /* NCR cards */
        .ncr-card {
            background: var(--tf-surface); border: 1px solid var(--tf-border); border-left: 4px solid var(--tf-danger);
            border-radius: var(--tf-radius-lg); padding: var(--tf-sp-5); margin-bottom: var(--tf-sp-4);
        }
        .ncr-card.minor { border-left-color: var(--tf-warning); }
        .ncr-card.major { border-left-color: var(--tf-danger); }
        .ncr-card.critical { border-left-color: #7F1D1D; }
        .ncr-card.closed { opacity: 0.7; border-left-color: var(--tf-success); }

        /* Traceability table */
        .trace-table { width: 100%; border-collapse: collapse; font-size: var(--tf-text-sm); }
        .trace-table th {
            background: var(--tf-navy); color: #fff; padding: 10px 12px;
            text-align: left; font-size: var(--tf-text-xs); text-transform: uppercase;
            letter-spacing: 0.04em; font-weight: 700;
        }
        .trace-table td { padding: 10px 12px; border-bottom: 1px solid var(--tf-border); }
        .trace-table tr:hover td { background: var(--tf-blue-light); }
        .trace-tag {
            background: var(--tf-gray-100); padding: 2px 8px; border-radius: 4px;
            font-family: var(--tf-font-mono); font-size: 11px; font-weight: 600;
        }

        /* Empty states */
        .empty-state { text-align: center; padding: 60px 20px; color: var(--tf-gray-400); }
        .empty-state .icon { font-size: 2.5rem; margin-bottom: 8px; }

        /* Modal */
        .modal-bg {
            display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(15,23,42,0.5); z-index: 300; align-items: center; justify-content: center;
        }
        .modal-bg.open { display: flex; }
        .modal-box {
            background: var(--tf-surface); border-radius: var(--tf-radius-xl);
            width: 640px; max-width: 95vw; max-height: 90vh; overflow-y: auto;
            box-shadow: var(--tf-shadow-lg);
        }
        .modal-header {
            padding: var(--tf-sp-5) var(--tf-sp-6); border-bottom: 1px solid var(--tf-border);
            display: flex; justify-content: space-between; align-items: center;
        }
        .modal-body { padding: var(--tf-sp-6); }
        .modal-footer {
            padding: var(--tf-sp-4) var(--tf-sp-6); border-top: 1px solid var(--tf-border);
            display: flex; justify-content: flex-end; gap: var(--tf-sp-3);
        }

        @media (max-width: 768px) {
            .tf-topbar nav { display: none; }
            .container { padding: var(--tf-sp-4); }
        }
    </style>
</head>
<body>
    <div class="tf-topbar">
        <a href="/" class="tf-logo"><div class="tf-logo-icon">&#9878;</div> TITANFORGE</a>
        <nav>
            <a href="/">Dashboard</a>
            <a href="/sa">Structures America Estimator</a>
            <a href="/tc">Titan Carports Estimator</a>
            <a href="/customers">Customers</a>
        </nav>
        <div class="tf-user">
            <button onclick="openGlobalSearch()" style="background:none;border:1px solid rgba(255,255,255,0.2);color:#fff;padding:6px 14px;border-radius:var(--tf-radius);cursor:pointer;font-size:var(--tf-text-sm);margin-right:12px;display:flex;align-items:center;gap:6px;">&#128269; Search <kbd style="background:rgba(255,255,255,0.15);padding:1px 6px;border-radius:4px;font-size:10px;">Ctrl+K</kbd></button>
            <span>{{USER_NAME}}</span>
            <span class="role-badge">{{USER_ROLE}}</span>
            <a href="/auth/logout">Logout</a>
        </div>
    </div>

    <!-- Global Search -->
    <div id="globalSearchOverlay" style="display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(15,23,42,0.5);z-index:400;align-items:flex-start;justify-content:center;padding-top:100px;">
        <div style="width:600px;max-width:90vw;background:var(--tf-surface);border-radius:var(--tf-radius-xl);box-shadow:var(--tf-shadow-lg);overflow:hidden;">
            <input type="text" id="globalSearchInput" placeholder="Search..." style="width:100%;padding:18px 20px;border:none;font-size:var(--tf-text-lg);outline:none;border-bottom:1px solid var(--tf-border);" oninput="_doGS(this.value)">
            <div id="globalSearchResults" style="max-height:400px;overflow-y:auto;padding:8px;"></div>
        </div>
    </div>

    <div class="container">
        <!-- Header -->
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:var(--tf-sp-5);">
            <div>
                <h1 style="font-size:var(--tf-text-2xl);font-weight:700;color:var(--tf-gray-900);">
                    QC Dashboard <span style="font-size:var(--tf-text-base);color:var(--tf-blue);font-weight:600;">{{JOB_CODE}}</span>
                </h1>
                <p style="color:var(--tf-gray-500);font-size:var(--tf-text-sm);">AISC Quality Control &amp; Material Traceability</p>
            </div>
            <div style="display:flex;gap:var(--tf-sp-3);">
                <button class="btn btn-primary" onclick="openNewInspection()">+ New Inspection</button>
                <button class="btn btn-outline" style="border-color:var(--tf-danger);color:var(--tf-danger);" onclick="openNewNCR()">+ New NCR</button>
                <a href="/project/{{JOB_CODE}}" class="btn btn-outline">&#8592; Project</a>
            </div>
        </div>

        <!-- Stats -->
        <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:var(--tf-sp-4);margin-bottom:var(--tf-sp-6);">
            <div class="stat-card"><div class="stat-icon blue">&#128203;</div><div class="stat-info"><div class="stat-label">Inspections</div><div class="stat-value" id="statInsp">0</div></div></div>
            <div class="stat-card"><div class="stat-icon green">&#10003;</div><div class="stat-info"><div class="stat-label">Passed</div><div class="stat-value" id="statPassed">0</div></div></div>
            <div class="stat-card"><div class="stat-icon amber">&#9888;</div><div class="stat-info"><div class="stat-label">Open NCRs</div><div class="stat-value" id="statNCR">0</div></div></div>
            <div class="stat-card"><div class="stat-icon purple">&#128279;</div><div class="stat-info"><div class="stat-label">Heat Numbers</div><div class="stat-value" id="statHeats">0</div></div></div>
            <div class="stat-card"><div class="stat-icon blue">&#128296;</div><div class="stat-info"><div class="stat-label">Members Traced</div><div class="stat-value" id="statMembers">0</div></div></div>
        </div>

        <!-- Tabs -->
        <div class="qc-tabs">
            <button class="qc-tab active" onclick="switchQCTab('inspections')">Inspections <span class="count-badge" id="inspCount">0</span></button>
            <button class="qc-tab" onclick="switchQCTab('ncrs')">NCRs <span class="count-badge" id="ncrCount">0</span></button>
            <button class="qc-tab" onclick="switchQCTab('traceability')">Material Traceability</button>
        </div>

        <!-- INSPECTIONS TAB -->
        <div class="qc-section active" id="sec-inspections">
            <div id="inspectionsList"></div>
        </div>

        <!-- NCRs TAB -->
        <div class="qc-section" id="sec-ncrs">
            <div id="ncrsList"></div>
        </div>

        <!-- TRACEABILITY TAB -->
        <div class="qc-section" id="sec-traceability">
            <div style="display:flex;gap:var(--tf-sp-3);margin-bottom:var(--tf-sp-4);">
                <button class="btn btn-primary btn-sm" onclick="openRegisterHeat()">+ Register Heat Number</button>
                <button class="btn btn-outline btn-sm" onclick="openAssignMember()">+ Assign Member</button>
            </div>
            <div id="traceabilityTable"></div>
        </div>
    </div>

    <!-- NEW INSPECTION MODAL -->
    <div class="modal-bg" id="inspModal">
        <div class="modal-box">
            <div class="modal-header">
                <h2 style="font-size:var(--tf-text-xl);font-weight:700;">New Inspection</h2>
                <button onclick="closeModal('inspModal')" style="background:none;border:none;font-size:1.5rem;cursor:pointer;color:var(--tf-gray-400);">&times;</button>
            </div>
            <div class="modal-body">
                <div style="margin-bottom:var(--tf-sp-4);">
                    <label class="form-label">Inspection Type *</label>
                    <select class="form-input" id="inspType" onchange="showInspPreview()">
                        <option value="">Select type...</option>
                    </select>
                    <div id="inspPreview" style="margin-top:8px;font-size:var(--tf-text-xs);color:var(--tf-gray-500);"></div>
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:var(--tf-sp-4);">
                    <div><label class="form-label">Inspector</label><input type="text" class="form-input" id="inspInspector" value="{{USER_NAME}}"></div>
                    <div><label class="form-label">Location / Area</label><input type="text" class="form-input" id="inspLocation" placeholder="Shop floor, Column line A-3..."></div>
                </div>
                <div style="margin-top:var(--tf-sp-4);">
                    <label class="form-label">Member Marks (comma separated)</label>
                    <input type="text" class="form-input" id="inspMembers" placeholder="C1, B2, W3-A...">
                </div>
                <div style="margin-top:var(--tf-sp-4);">
                    <label class="form-label">Notes</label>
                    <textarea class="form-input" id="inspNotes" rows="2" placeholder="Initial notes..."></textarea>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-outline" onclick="closeModal('inspModal')">Cancel</button>
                <button class="btn btn-primary" onclick="createInspection()">Create Inspection</button>
            </div>
        </div>
    </div>

    <!-- NEW NCR MODAL -->
    <div class="modal-bg" id="ncrModal">
        <div class="modal-box">
            <div class="modal-header">
                <h2 style="font-size:var(--tf-text-xl);font-weight:700;">New NCR (Non-Conformance Report)</h2>
                <button onclick="closeModal('ncrModal')" style="background:none;border:none;font-size:1.5rem;cursor:pointer;color:var(--tf-gray-400);">&times;</button>
            </div>
            <div class="modal-body">
                <div style="margin-bottom:var(--tf-sp-4);">
                    <label class="form-label">Title *</label>
                    <input type="text" class="form-input" id="ncrTitle" placeholder="Brief description of non-conformance">
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:var(--tf-sp-4);margin-bottom:var(--tf-sp-4);">
                    <div><label class="form-label">Severity *</label>
                        <select class="form-input" id="ncrSeverity">
                            <option value="minor">Minor</option>
                            <option value="major">Major</option>
                            <option value="critical">Critical</option>
                        </select>
                    </div>
                    <div><label class="form-label">Assign To</label><input type="text" class="form-input" id="ncrAssign" placeholder="Name or role"></div>
                </div>
                <div style="margin-bottom:var(--tf-sp-4);">
                    <label class="form-label">Member Marks (comma separated)</label>
                    <input type="text" class="form-input" id="ncrMembers" placeholder="C1, B2...">
                </div>
                <div>
                    <label class="form-label">Description *</label>
                    <textarea class="form-input" id="ncrDesc" rows="4" placeholder="Detailed description of the non-conformance, reference drawings/specs..."></textarea>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-outline" onclick="closeModal('ncrModal')">Cancel</button>
                <button class="btn btn-primary" style="background:var(--tf-danger);" onclick="createNCR()">Create NCR</button>
            </div>
        </div>
    </div>

    <!-- REGISTER HEAT NUMBER MODAL -->
    <div class="modal-bg" id="heatModal">
        <div class="modal-box">
            <div class="modal-header">
                <h2 style="font-size:var(--tf-text-xl);font-weight:700;">Register Heat Number</h2>
                <button onclick="closeModal('heatModal')" style="background:none;border:none;font-size:1.5rem;cursor:pointer;color:var(--tf-gray-400);">&times;</button>
            </div>
            <div class="modal-body">
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:var(--tf-sp-4);">
                    <div><label class="form-label">Heat Number *</label><input type="text" class="form-input" id="heatNumber" placeholder="e.g. H-123456"></div>
                    <div><label class="form-label">Coil Tag *</label><input type="text" class="form-input" id="heatCoilTag" placeholder="e.g. COIL-001"></div>
                    <div><label class="form-label">Material Spec</label><input type="text" class="form-input" id="heatSpec" placeholder="A572 Gr 50, A500 Gr B/C..."></div>
                    <div><label class="form-label">Mill Name</label><input type="text" class="form-input" id="heatMill" placeholder="Mill/manufacturer name"></div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-outline" onclick="closeModal('heatModal')">Cancel</button>
                <button class="btn btn-primary" onclick="registerHeat()">Register</button>
            </div>
        </div>
    </div>

    <!-- ASSIGN MEMBER MODAL -->
    <div class="modal-bg" id="assignModal">
        <div class="modal-box">
            <div class="modal-header">
                <h2 style="font-size:var(--tf-text-xl);font-weight:700;">Assign Member to Heat Number</h2>
                <button onclick="closeModal('assignModal')" style="background:none;border:none;font-size:1.5rem;cursor:pointer;color:var(--tf-gray-400);">&times;</button>
            </div>
            <div class="modal-body">
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:var(--tf-sp-4);">
                    <div><label class="form-label">Heat Number *</label><input type="text" class="form-input" id="assignHeat" placeholder="H-123456"></div>
                    <div><label class="form-label">Member Mark *</label><input type="text" class="form-input" id="assignMember" placeholder="C1, B2, W3-A..."></div>
                </div>
                <div style="margin-top:var(--tf-sp-4);"><label class="form-label">Description</label><input type="text" class="form-input" id="assignDesc" placeholder="W12x26 column, HSS 6x6x3/8..."></div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-outline" onclick="closeModal('assignModal')">Cancel</button>
                <button class="btn btn-primary" onclick="assignMember()">Assign</button>
            </div>
        </div>
    </div>

    <!-- INSPECTION DETAIL MODAL -->
    <div class="modal-bg" id="inspDetailModal">
        <div class="modal-box" style="width:800px;">
            <div class="modal-header">
                <h2 id="inspDetailTitle" style="font-size:var(--tf-text-xl);font-weight:700;"></h2>
                <button onclick="closeModal('inspDetailModal')" style="background:none;border:none;font-size:1.5rem;cursor:pointer;color:var(--tf-gray-400);">&times;</button>
            </div>
            <div class="modal-body" id="inspDetailBody"></div>
            <div class="modal-footer" id="inspDetailFooter"></div>
        </div>
    </div>

<script>
const JOB_CODE = '{{JOB_CODE}}';
let qcData = null;
let inspTypes = {};
let traceData = null;

document.addEventListener('DOMContentLoaded', () => {
    if (typeof setProjectContext === 'function') {
        setProjectContext(JOB_CODE);
    }
    loadInspTypes(); loadQCData(); loadTraceability();
});
document.addEventListener('keydown', e => {
    if ((e.ctrlKey||e.metaKey) && e.key==='k') { e.preventDefault(); openGlobalSearch(); }
    if (e.key==='Escape') { document.querySelectorAll('.modal-bg.open').forEach(m=>m.classList.remove('open')); _closeGS(); }
});

function switchQCTab(tab) {
    document.querySelectorAll('.qc-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.qc-section').forEach(s => s.classList.remove('active'));
    event.target.closest('.qc-tab').classList.add('active');
    document.getElementById('sec-' + tab).classList.add('active');
}

function closeModal(id) { document.getElementById(id).classList.remove('open'); }

async function loadInspTypes() {
    const r = await fetch('/api/qc/types');
    const d = await r.json();
    if (d.ok) {
        inspTypes = d.types;
        const sel = document.getElementById('inspType');
        for (const [k, v] of Object.entries(inspTypes)) {
            sel.innerHTML += `<option value="${k}">${v.label}</option>`;
        }
    }
}

function showInspPreview() {
    const type = document.getElementById('inspType').value;
    const div = document.getElementById('inspPreview');
    if (type && inspTypes[type]) {
        div.innerHTML = `<b>Standard:</b> ${inspTypes[type].standard}<br><b>Checklist items:</b> ${inspTypes[type].checklist.length}`;
    } else div.innerHTML = '';
}

async function loadQCData() {
    const r = await fetch('/api/qc/data?job_code=' + encodeURIComponent(JOB_CODE));
    const d = await r.json();
    if (d.ok) { qcData = d.data; renderAll(); }
}

async function loadTraceability() {
    const r = await fetch('/api/traceability/report?job_code=' + encodeURIComponent(JOB_CODE));
    const d = await r.json();
    if (d.ok) { traceData = d; renderTraceability(); updateStats(); }
}

function renderAll() {
    renderInspections();
    renderNCRs();
    updateStats();
}

function updateStats() {
    const ins = qcData?.inspections || [];
    const ncrs = qcData?.ncrs || [];
    document.getElementById('statInsp').textContent = ins.length;
    document.getElementById('statPassed').textContent = ins.filter(i=>i.status==='passed').length;
    document.getElementById('statNCR').textContent = ncrs.filter(n=>n.status!=='closed'&&n.status!=='voided').length;
    document.getElementById('inspCount').textContent = ins.length;
    document.getElementById('ncrCount').textContent = ncrs.length;
    const heats = traceData?.heat_numbers || {};
    document.getElementById('statHeats').textContent = Object.keys(heats).length;
    let memberCount = 0;
    for (const h of Object.values(heats)) memberCount += (h.members||[]).length;
    document.getElementById('statMembers').textContent = memberCount;
}

function renderInspections() {
    const list = document.getElementById('inspectionsList');
    const ins = qcData?.inspections || [];
    if (!ins.length) {
        list.innerHTML = '<div class="empty-state"><div class="icon">&#128203;</div><div>No inspections yet. Create one to start tracking QC.</div></div>';
        return;
    }
    list.innerHTML = ins.map(i => {
        const checkCount = Object.keys(i.items||{}).length;
        const totalChecks = inspTypes[i.type]?.checklist?.length || 0;
        const pct = totalChecks ? Math.round(checkCount/totalChecks*100) : 0;
        return `<div class="insp-card" onclick="openInspDetail('${i.id}')" style="cursor:pointer;">
            <div class="insp-header">
                <div>
                    <div class="insp-title">${i.type_label||i.type}</div>
                    <div class="insp-standard">${i.standard||''}</div>
                </div>
                <span class="status-badge ${i.status}">${i.status.replace('_',' ')}</span>
            </div>
            <div class="insp-meta">
                <span>&#128100; ${i.inspector||''}</span>
                <span>&#128205; ${i.location||'—'}</span>
                <span>&#128197; ${i.created_at ? new Date(i.created_at).toLocaleDateString() : ''}</span>
                <span>&#9745; ${checkCount}/${totalChecks} (${pct}%)</span>
                ${(i.member_marks||[]).length ? '<span>Members: '+(i.member_marks||[]).join(', ')+'</span>' : ''}
            </div>
            ${i.notes ? '<div style="font-size:var(--tf-text-xs);color:var(--tf-gray-500);margin-top:4px;">'+i.notes.substring(0,100)+'</div>' : ''}
        </div>`;
    }).join('');
}

function renderNCRs() {
    const list = document.getElementById('ncrsList');
    const ncrs = qcData?.ncrs || [];
    if (!ncrs.length) {
        list.innerHTML = '<div class="empty-state"><div class="icon">&#10003;</div><div>No NCRs — great quality work!</div></div>';
        return;
    }
    list.innerHTML = ncrs.map(n => `
        <div class="ncr-card ${n.severity} ${n.status}">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
                <div>
                    <div style="font-weight:700;font-size:var(--tf-text-md);color:var(--tf-gray-900);">${n.id}: ${n.title}</div>
                    <div style="font-size:var(--tf-text-xs);color:var(--tf-gray-500);margin-top:2px;">
                        Reported by ${n.reported_by||'—'} on ${n.created_at ? new Date(n.created_at).toLocaleDateString() : ''}
                        ${n.assigned_to ? ' &middot; Assigned to '+n.assigned_to : ''}
                    </div>
                </div>
                <div style="display:flex;gap:6px;">
                    <span class="severity-badge ${n.severity}">${n.severity}</span>
                    <span class="status-badge ${n.status}">${n.status.replace('_',' ')}</span>
                </div>
            </div>
            <div style="font-size:var(--tf-text-sm);color:var(--tf-gray-700);margin-bottom:8px;">${n.description||''}</div>
            ${(n.member_marks||[]).length ? '<div style="font-size:var(--tf-text-xs);color:var(--tf-gray-500);">Members: '+(n.member_marks||[]).join(', ')+'</div>' : ''}
            ${n.corrective_action ? '<div style="margin-top:8px;padding:8px 12px;background:var(--tf-info-bg);border-radius:var(--tf-radius);font-size:var(--tf-text-xs);"><b>Corrective Action:</b> '+n.corrective_action+'</div>' : ''}
            <div style="margin-top:8px;display:flex;gap:8px;">
                ${n.status!=='closed' ? '<button class="btn btn-outline btn-sm" onclick="updateNCRStatus(\''+n.id+'\',\'closed\')">Close NCR</button>' : ''}
                ${n.status==='open' ? '<button class="btn btn-outline btn-sm" onclick="updateNCRStatus(\''+n.id+'\',\'under_review\')">Start Review</button>' : ''}
            </div>
        </div>
    `).join('');
}

function renderTraceability() {
    const container = document.getElementById('traceabilityTable');
    const heats = traceData?.heat_numbers || {};
    if (!Object.keys(heats).length) {
        container.innerHTML = '<div class="empty-state"><div class="icon">&#128279;</div><div>No heat numbers registered. Register one to start tracking material traceability.</div></div>';
        return;
    }
    let rows = '';
    for (const [hn, data] of Object.entries(heats)) {
        const coils = (data.coils||[]).map(c => `<span class="trace-tag">${c.coil_tag}</span>`).join(' ');
        const members = (data.members||[]).map(m => `<span class="trace-tag">${m.member_mark}</span>`).join(' ');
        rows += `<tr>
            <td style="font-weight:700;font-family:var(--tf-font-mono);">${hn}</td>
            <td>${data.material_spec||'—'}</td>
            <td>${data.mill_name||'—'}</td>
            <td>${coils||'—'}</td>
            <td>${members||'None assigned'}</td>
        </tr>`;
    }
    container.innerHTML = `<table class="trace-table">
        <thead><tr><th>Heat Number</th><th>Material Spec</th><th>Mill</th><th>Coils</th><th>Members</th></tr></thead>
        <tbody>${rows}</tbody>
    </table>`;
}

// ── Create Inspection ──
function openNewInspection() { document.getElementById('inspModal').classList.add('open'); }

async function createInspection() {
    const type = document.getElementById('inspType').value;
    if (!type) { alert('Select an inspection type'); return; }
    const members = document.getElementById('inspMembers').value.split(',').map(s=>s.trim()).filter(Boolean);
    const r = await fetch('/api/qc/inspection/create', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({
            job_code: JOB_CODE, type,
            inspector: document.getElementById('inspInspector').value,
            location: document.getElementById('inspLocation').value,
            member_marks: members,
            notes: document.getElementById('inspNotes').value,
        })
    });
    const d = await r.json();
    if (d.ok) { closeModal('inspModal'); loadQCData(); }
    else alert(d.error);
}

// ── Inspection Detail ──
function openInspDetail(inspId) {
    const insp = (qcData?.inspections||[]).find(i => i.id === inspId);
    if (!insp) return;
    document.getElementById('inspDetailTitle').textContent = insp.type_label || insp.type;
    const checklist = inspTypes[insp.type]?.checklist || [];
    const items = insp.items || {};

    let html = `<div style="margin-bottom:var(--tf-sp-4);">
        <div class="insp-meta">
            <span>&#128100; ${insp.inspector}</span>
            <span>&#128205; ${insp.location||'—'}</span>
            <span class="status-badge ${insp.status}">${insp.status.replace('_',' ')}</span>
        </div>
    </div>
    <div class="checklist-grid">`;

    checklist.forEach(ci => {
        const val = items[ci.key] || '';
        const checked = val === true || val === 'true' || val === 'passed';
        const cssClass = checked ? 'checked' : (val === 'failed' ? 'failed-item' : '');

        if (ci.type === 'check') {
            html += `<div class="check-item ${cssClass}">
                <input type="checkbox" ${checked?'checked':''} onchange="updateInspItem('${inspId}','${ci.key}',this.checked)">
                <label>${ci.label}</label>
            </div>`;
        } else if (ci.type === 'select') {
            html += `<div class="check-item">
                <label>${ci.label}</label>
                <select onchange="updateInspItem('${inspId}','${ci.key}',this.value)">
                    <option value="">Select...</option>
                    ${(ci.options||[]).map(o => `<option value="${o}" ${val===o?'selected':''}>${o}</option>`).join('')}
                </select>
            </div>`;
        } else {
            html += `<div class="check-item">
                <label>${ci.label}</label>
                <input type="text" value="${val}" placeholder="Enter value..." onblur="updateInspItem('${inspId}','${ci.key}',this.value)">
            </div>`;
        }
    });

    html += `</div>
    <div style="margin-top:var(--tf-sp-4);">
        <label class="form-label">Notes</label>
        <textarea class="form-input" rows="2" id="inspDetailNotes" onblur="updateInspNotes('${inspId}')">${insp.notes||''}</textarea>
    </div>`;

    document.getElementById('inspDetailBody').innerHTML = html;
    document.getElementById('inspDetailFooter').innerHTML = `
        <button class="btn btn-outline" onclick="closeModal('inspDetailModal')">Close</button>
        ${insp.status!=='passed' ? '<button class="btn btn-primary" style="background:var(--tf-success);" onclick="setInspStatus(\''+inspId+'\',\'passed\')">&#10003; Mark Passed</button>' : ''}
        ${insp.status!=='failed' ? '<button class="btn btn-primary" style="background:var(--tf-danger);" onclick="setInspStatus(\''+inspId+'\',\'failed\')">&#10007; Mark Failed</button>' : ''}
    `;
    document.getElementById('inspDetailModal').classList.add('open');
}

async function updateInspItem(inspId, key, val) {
    const insp = (qcData?.inspections||[]).find(i => i.id === inspId);
    if (!insp) return;
    if (!insp.items) insp.items = {};
    insp.items[key] = val;
    await fetch('/api/qc/inspection/update', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ job_code: JOB_CODE, inspection_id: inspId, items: insp.items })
    });
    renderInspections();
}

async function updateInspNotes(inspId) {
    const notes = document.getElementById('inspDetailNotes')?.value || '';
    await fetch('/api/qc/inspection/update', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ job_code: JOB_CODE, inspection_id: inspId, notes })
    });
}

async function setInspStatus(inspId, status) {
    await fetch('/api/qc/inspection/update', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ job_code: JOB_CODE, inspection_id: inspId, status })
    });
    closeModal('inspDetailModal');
    loadQCData();
}

// ── NCR ──
function openNewNCR() { document.getElementById('ncrModal').classList.add('open'); }

async function createNCR() {
    const title = document.getElementById('ncrTitle').value.trim();
    const desc = document.getElementById('ncrDesc').value.trim();
    if (!title || !desc) { alert('Title and description required'); return; }
    const members = document.getElementById('ncrMembers').value.split(',').map(s=>s.trim()).filter(Boolean);
    const r = await fetch('/api/qc/ncr/create', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({
            job_code: JOB_CODE, title, description: desc,
            severity: document.getElementById('ncrSeverity').value,
            assigned_to: document.getElementById('ncrAssign').value,
            member_marks: members,
        })
    });
    const d = await r.json();
    if (d.ok) { closeModal('ncrModal'); loadQCData(); }
}

async function updateNCRStatus(ncrId, status) {
    await fetch('/api/qc/ncr/update', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ job_code: JOB_CODE, ncr_id: ncrId, status })
    });
    loadQCData();
}

// ── Traceability ──
function openRegisterHeat() { document.getElementById('heatModal').classList.add('open'); }
function openAssignMember() { document.getElementById('assignModal').classList.add('open'); }

async function registerHeat() {
    const hn = document.getElementById('heatNumber').value.trim();
    const ct = document.getElementById('heatCoilTag').value.trim();
    if (!hn || !ct) { alert('Heat number and coil tag required'); return; }
    await fetch('/api/traceability/register', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({
            heat_number: hn, coil_tag: ct,
            material_spec: document.getElementById('heatSpec').value,
            mill_name: document.getElementById('heatMill').value,
        })
    });
    closeModal('heatModal'); loadTraceability();
}

async function assignMember() {
    const hn = document.getElementById('assignHeat').value.trim();
    const mm = document.getElementById('assignMember').value.trim();
    if (!hn || !mm) { alert('Heat number and member mark required'); return; }
    await fetch('/api/traceability/assign', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({
            heat_number: hn, job_code: JOB_CODE,
            member_mark: mm, description: document.getElementById('assignDesc').value,
        })
    });
    closeModal('assignModal'); loadTraceability(); loadQCData();
}

// ── Global Search ──
var _gst=null;
function openGlobalSearch(){document.getElementById('globalSearchOverlay').style.display='flex';document.getElementById('globalSearchInput').value='';document.getElementById('globalSearchInput').focus();}
function _closeGS(){document.getElementById('globalSearchOverlay').style.display='none';}
document.getElementById('globalSearchOverlay').addEventListener('click',function(e){if(e.target.id==='globalSearchOverlay')_closeGS();});
function _doGS(q){clearTimeout(_gst);if(!q||q.length<2){document.getElementById('globalSearchResults').innerHTML='<div style="padding:20px;text-align:center;color:var(--tf-gray-400);">Type to search...</div>';return;}
_gst=setTimeout(function(){fetch('/api/search?q='+encodeURIComponent(q)).then(r=>r.json()).then(d=>{var c=document.getElementById('globalSearchResults');if(!d.results?.length){c.innerHTML='<div style="padding:20px;text-align:center;color:var(--tf-gray-400);">No results</div>';return;}
var ic={project:'&#128204;',customer:'&#128100;',inventory:'&#128230;'};c.innerHTML=d.results.map(r=>'<a href="'+r.url+'" style="text-decoration:none;color:inherit;"><div style="display:flex;align-items:center;gap:12px;padding:10px 14px;border-radius:8px;cursor:pointer;" onmouseover="this.style.background=\'var(--tf-blue-light)\'" onmouseout="this.style.background=\'\'"><div style="width:32px;height:32px;border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:14px;background:var(--tf-blue-light);">'+(ic[r.type]||'')+'</div><div><div style="font-weight:600;font-size:var(--tf-text-sm);color:var(--tf-gray-900);">'+r.title+'</div><div style="font-size:var(--tf-text-xs);color:var(--tf-gray-500);">'+(r.subtitle||'')+'</div></div></div></a>').join('');});},300);}
</script>
</body>
</html>
"""
