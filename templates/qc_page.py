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
        .ncr-card.voided { opacity: 0.5; border-left-color: var(--tf-gray-400); }

        /* NCR workflow stepper */
        .ncr-stepper { display:flex; gap:0; margin:12px 0; }
        .ncr-step { flex:1; text-align:center; padding:8px 4px; font-size:11px; font-weight:600;
            background:var(--tf-gray-100); color:var(--tf-gray-500); position:relative; }
        .ncr-step:first-child { border-radius:6px 0 0 6px; }
        .ncr-step:last-child { border-radius:0 6px 6px 0; }
        .ncr-step.active { background:var(--tf-primary); color:#fff; }
        .ncr-step.done { background:var(--tf-success); color:#fff; }
        .ncr-step.done::after { content:'\\2713'; margin-left:4px; }

        /* NCR detail panel */
        .ncr-detail { margin-top:12px; border-top:1px solid var(--tf-border); padding-top:12px; }
        .ncr-detail-section { background:var(--tf-gray-50); border:1px solid var(--tf-border);
            border-radius:var(--tf-radius); padding:16px; margin-bottom:12px; }
        .ncr-detail-section h4 { font-size:13px; font-weight:700; margin:0 0 10px; color:var(--tf-gray-800); }
        .ncr-detail-section textarea { width:100%; min-height:60px; padding:8px 10px;
            border:1px solid var(--tf-border); border-radius:6px; font-size:13px; font-family:inherit;
            background:var(--tf-surface); color:var(--tf-gray-900); resize:vertical; }
        .ncr-detail-section select { padding:6px 10px; border:1px solid var(--tf-border); border-radius:6px;
            font-size:13px; background:var(--tf-surface); color:var(--tf-gray-900); }
        .ncr-history { max-height:160px; overflow-y:auto; font-size:11px; color:var(--tf-gray-500); }
        .ncr-history-item { padding:4px 0; border-bottom:1px solid var(--tf-gray-100); }
        .ncr-history-item:last-child { border-bottom:none; }

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
            <button class="qc-tab" onclick="switchQCTab('holdpoints')">&#128721; Hold Points <span class="count-badge" id="holdCount" style="background:#FEF3C7;color:#92400E;">0</span></button>
            <button class="qc-tab" onclick="switchQCTab('ncrs')">NCRs <span class="count-badge" id="ncrCount">0</span></button>
            <button class="qc-tab" onclick="switchQCTab('traceability')">Material Traceability</button>
            <button class="qc-tab" onclick="switchQCTab('reports')">&#128196; Inspection Reports <span class="count-badge" id="reportsCount">0</span></button>
        </div>

        <!-- INSPECTIONS TAB -->
        <div class="qc-section active" id="sec-inspections">
            <div id="inspectionsList"></div>
        </div>

        <!-- QC HOLD POINTS TAB -->
        <div class="qc-section" id="sec-holdpoints">
            <div style="background:#FEF3C7;border:1px solid #F59E0B;border-radius:var(--tf-radius-lg);padding:14px 18px;margin-bottom:var(--tf-sp-4);">
                <div style="font-weight:700;font-size:14px;color:#92400E;margin-bottom:4px;">&#128721; QC Hold Points — Mandatory Inspection Gates</div>
                <div style="font-size:12px;color:#78350F;">
                    These items have completed fabrication but require QC inspection before they can be loaded or shipped.
                    Per AISC 360 Chapter N, primary structural members (columns, rafters, splices) must pass QC before release.
                </div>
            </div>
            <div id="holdPointsList"></div>
        </div>

        <!-- NCRs TAB -->
        <div class="qc-section" id="sec-ncrs">
            <div style="display:flex;gap:var(--tf-sp-3);margin-bottom:var(--tf-sp-4);flex-wrap:wrap;align-items:center;">
                <select class="form-input" id="ncrFilterStatus" onchange="renderNCRs()" style="width:auto;font-size:13px;">
                    <option value="all">All Statuses</option>
                    <option value="open" selected>Open</option>
                    <option value="under_review">Under Review</option>
                    <option value="corrective_action">Corrective Action</option>
                    <option value="re_inspect">Re-Inspection</option>
                    <option value="closed">Closed</option>
                    <option value="voided">Voided</option>
                </select>
                <select class="form-input" id="ncrFilterSeverity" onchange="renderNCRs()" style="width:auto;font-size:13px;">
                    <option value="all">All Severities</option>
                    <option value="critical">Critical</option>
                    <option value="major">Major</option>
                    <option value="minor">Minor</option>
                </select>
            </div>
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

        <!-- INSPECTION REPORTS TAB -->
        <div class="qc-section" id="sec-reports">

            <!-- Report Generator Panel -->
            <div style="background:var(--tf-surface);border:1px solid var(--tf-border);border-radius:var(--tf-radius-lg);padding:var(--tf-sp-5);margin-bottom:var(--tf-sp-5);">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:var(--tf-sp-4);">
                    <div>
                        <h3 style="font-size:var(--tf-text-lg);font-weight:700;color:var(--tf-gray-900);margin:0;">AISC Inspection Report Generator</h3>
                        <p style="font-size:var(--tf-text-xs);color:var(--tf-gray-500);margin:4px 0 0;">Generate printable inspection reports with auto-populated project data. Print, inspect, sign, and file.</p>
                    </div>
                    <div style="display:flex;gap:8px;">
                        <button class="btn btn-outline btn-sm" onclick="loadInspRequirements()" title="View required inspections for this job">&#128203; View Requirements</button>
                    </div>
                </div>

                <!-- Single Report Generator -->
                <div style="background:var(--tf-gray-50);border:1px solid var(--tf-border);border-radius:var(--tf-radius);padding:var(--tf-sp-4);margin-bottom:var(--tf-sp-3);">
                    <h4 style="font-size:var(--tf-text-sm);font-weight:700;margin:0 0 12px;">Generate Single Inspection Report</h4>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr auto;gap:var(--tf-sp-3);align-items:end;">
                        <div>
                            <label class="form-label" style="font-size:11px;">Ship Mark *</label>
                            <input type="text" class="form-input" id="rptShipMark" placeholder="C1, B1, PG-A1..." style="font-size:13px;">
                        </div>
                        <div>
                            <label class="form-label" style="font-size:11px;">Component Type *</label>
                            <select class="form-input" id="rptCompType" style="font-size:13px;">
                                <option value="">Select...</option>
                                <option value="column">Column (Box Beam)</option>
                                <option value="rafter">Rafter (Box Beam)</option>
                                <option value="purlin">Purlin (Z/C Section)</option>
                                <option value="sag_rod">Sag Rod</option>
                                <option value="strap">Hurricane Strap</option>
                                <option value="endcap">Endcap U-Channel</option>
                                <option value="p1clip">P1 Interior Clip</option>
                                <option value="p2plate">P2 Eave Plate</option>
                                <option value="splice">Splice Plate</option>
                            </select>
                        </div>
                        <div>
                            <label class="form-label" style="font-size:11px;">Inspection Stage *</label>
                            <select class="form-input" id="rptStage" style="font-size:13px;">
                                <option value="">Select type first...</option>
                            </select>
                        </div>
                        <button class="btn btn-primary btn-sm" onclick="generateSingleReport()" style="white-space:nowrap;">
                            &#128196; Generate PDF
                        </button>
                    </div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:var(--tf-sp-3);margin-top:var(--tf-sp-3);">
                        <div>
                            <label class="form-label" style="font-size:11px;">Description (optional)</label>
                            <input type="text" class="form-input" id="rptDesc" placeholder="14x4x10GA Box Beam, 19'-6 3/8&quot;" style="font-size:13px;">
                        </div>
                        <div>
                            <label class="form-label" style="font-size:11px;">Heat Number (optional — auto-pulls from traceability)</label>
                            <input type="text" class="form-input" id="rptHeatNum" placeholder="Auto-populated if registered" style="font-size:13px;">
                        </div>
                    </div>
                </div>

                <!-- Full Packet Generator -->
                <div style="background:linear-gradient(135deg,#0F172A,#1E293B);border-radius:var(--tf-radius);padding:var(--tf-sp-4);color:#fff;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <h4 style="font-size:var(--tf-text-sm);font-weight:700;margin:0;color:#FFF;">&#128230; Full Inspection Packet</h4>
                            <p style="font-size:11px;color:#94A3B8;margin:4px 0 0;">Generates ALL required inspection reports for a member in one PDF — material receiving, dimensional, weld VT, and final QC release. Print the whole packet and hand it to the inspector.</p>
                        </div>
                        <button class="btn btn-sm" style="background:#C89A2E;color:#000;font-weight:700;white-space:nowrap;" onclick="generateFullPacket()">
                            &#128230; Generate Full Packet
                        </button>
                    </div>
                </div>
            </div>

            <!-- Requirements Matrix (loaded dynamically) -->
            <div id="requirementsMatrix" style="display:none;background:var(--tf-surface);border:1px solid var(--tf-border);border-radius:var(--tf-radius-lg);padding:var(--tf-sp-5);margin-bottom:var(--tf-sp-5);">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:var(--tf-sp-4);">
                    <h3 style="font-size:var(--tf-text-md);font-weight:700;color:var(--tf-gray-900);margin:0;">&#128203; Inspection Requirements Matrix</h3>
                    <button class="btn btn-outline btn-sm" onclick="document.getElementById('requirementsMatrix').style.display='none'">Close</button>
                </div>
                <div id="requirementsContent"></div>
            </div>

            <!-- Saved Reports List -->
            <div style="background:var(--tf-surface);border:1px solid var(--tf-border);border-radius:var(--tf-radius-lg);padding:var(--tf-sp-5);">
                <h3 style="font-size:var(--tf-text-md);font-weight:700;color:var(--tf-gray-900);margin:0 0 var(--tf-sp-4);">Saved Inspection Reports</h3>
                <div id="savedReportsList">
                    <div class="empty-state"><div class="icon">&#128196;</div>No inspection reports generated yet.<br>Use the generator above to create reports.</div>
                </div>
            </div>
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

document.addEventListener('DOMContentLoaded', () => { loadInspTypes(); loadQCData(); loadTraceability(); loadSavedReports(); initReportStageSelector(); });
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
    loadHoldPoints();
    updateStats();
}

// QC Hold Points — items that completed fab but need QC before shipping
const QC_HOLD_TYPES = new Set(['column','rafter','splice']);
var holdPointItems = [];

async function loadHoldPoints() {
    try {
        const r = await fetch('/api/work-orders/list?job_code=' + encodeURIComponent(JOB_CODE));
        const d = await r.json();
        holdPointItems = [];
        const wos = d.work_orders || [];
        for (const wo of wos) {
            const woId = wo.work_order_id || wo.wo_id;
            try {
                const r2 = await fetch('/api/work-orders/detail?job_code=' + encodeURIComponent(JOB_CODE) + '&wo_id=' + encodeURIComponent(woId));
                const d2 = await r2.json();
                if (d2.ok && d2.work_order) {
                    (d2.work_order.items||[]).forEach(item => {
                        // Items that completed fab AND need QC hold
                        if (item.status === 'complete' && item.qc_status !== 'passed') {
                            const ctype = (item.component_type||'').toLowerCase();
                            if (QC_HOLD_TYPES.has(ctype)) {
                                item._wo_id = woId;
                                holdPointItems.push(item);
                            }
                        }
                    });
                }
            } catch(e) {}
        }
        renderHoldPoints();
    } catch(e) { console.error('loadHoldPoints error:', e); }
}

function renderHoldPoints() {
    const list = document.getElementById('holdPointsList');
    document.getElementById('holdCount').textContent = holdPointItems.length;
    if (!holdPointItems.length) {
        list.innerHTML = '<div class="empty-state"><div class="icon">&#10003;</div><div>No items awaiting QC hold point release. All structural members are either still in fabrication or have been QC approved.</div></div>';
        return;
    }
    list.innerHTML = holdPointItems.map(item => {
        const ctype = (item.component_type||'').charAt(0).toUpperCase() + (item.component_type||'').slice(1);
        const isPending = item.qc_status === 'pending' || !item.qc_status;
        const isFailed = item.qc_status === 'failed';
        return `
        <div style="background:var(--tf-surface);border:1px solid ${isFailed?'var(--tf-danger)':'#F59E0B'};border-left:4px solid ${isFailed?'var(--tf-danger)':'#F59E0B'};border-radius:var(--tf-radius-lg);padding:14px 18px;margin-bottom:8px;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div>
                    <div style="font-weight:700;font-size:15px;color:var(--tf-gray-900);">
                        ${item.ship_mark} — ${ctype}
                        ${isFailed ? '<span style="color:var(--tf-danger);font-size:12px;margin-left:8px;">&#10060; QC FAILED — requires re-inspection</span>' : ''}
                    </div>
                    <div style="font-size:12px;color:var(--tf-gray-500);margin-top:2px;">
                        ${item.description||''} &middot; Finished ${item.finished_at ? new Date(item.finished_at).toLocaleString() : 'N/A'}
                        ${item.finished_by ? ' by '+item.finished_by : ''}
                    </div>
                </div>
                <span style="padding:4px 12px;border-radius:10px;font-size:11px;font-weight:700;background:${isFailed?'#FEE2E2;color:#DC2626':'#FEF3C7;color:#92400E'};">
                    ${isFailed ? 'FAILED' : 'QC HOLD'}
                </span>
            </div>
            ${item.qc_notes ? '<div style="font-size:12px;color:var(--tf-gray-600);margin-top:6px;padding:6px 10px;background:var(--tf-gray-50);border-radius:6px;"><b>QC Notes:</b> '+item.qc_notes+'</div>' : ''}
            <div style="margin-top:10px;display:flex;gap:8px;align-items:center;">
                <input type="text" id="hold-insp-${item.item_id}" placeholder="Inspector name" class="form-input" style="max-width:180px;font-size:13px;padding:6px 10px;">
                <input type="text" id="hold-notes-${item.item_id}" placeholder="QC notes (optional)" class="form-input" style="max-width:240px;font-size:13px;padding:6px 10px;">
                <button class="btn btn-primary btn-sm" style="background:var(--tf-success);" onclick="approveHoldPoint('${item.item_id}')">&#10003; Approve</button>
                <button class="btn btn-outline btn-sm" style="color:var(--tf-danger);border-color:var(--tf-danger);" onclick="rejectHoldPoint('${item.item_id}')">&#10060; Reject / NCR</button>
            </div>
        </div>`;
    }).join('');
}

async function approveHoldPoint(itemId) {
    const insp = document.getElementById('hold-insp-'+itemId);
    if (!insp || !insp.value.trim()) { alert('Inspector name is required to approve.'); return; }
    const notes = document.getElementById('hold-notes-'+itemId);
    const r = await fetch('/api/qc/item-inspect', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({
            job_code: JOB_CODE, item_id: itemId,
            inspector: insp.value.trim(),
            qc_status: 'passed',
            qc_notes: (notes ? notes.value.trim() : '') || 'QC hold point approved'
        })
    });
    const d = await r.json();
    if (d.ok) {
        if (d.inspector_warning) {
            alert('Warning: ' + d.inspector_warning + '\\n\\nThe inspection was recorded, but this inspector may not be qualified per AISC requirements. Add their credentials in QA > Inspector Registry.');
        }
        loadHoldPoints(); loadQCData();
    } else { alert(d.error || 'Error approving item'); }
}

async function rejectHoldPoint(itemId) {
    const insp = document.getElementById('hold-insp-'+itemId);
    if (!insp || !insp.value.trim()) { alert('Inspector name is required.'); return; }
    const notes = document.getElementById('hold-notes-'+itemId);
    const r = await fetch('/api/qc/item-inspect', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({
            job_code: JOB_CODE, item_id: itemId,
            inspector: insp.value.trim(),
            qc_status: 'failed',
            qc_notes: (notes ? notes.value.trim() : '') || 'QC hold point rejected'
        })
    });
    const d = await r.json();
    if (d.ok) { loadHoldPoints(); loadQCData(); } else { alert(d.error || 'Error'); }
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

// NCR workflow stages
const NCR_STAGES = ['open','under_review','corrective_action','re_inspect','closed'];
const NCR_STAGE_LABELS = {open:'Reported',under_review:'Root Cause',corrective_action:'Corrective Action',re_inspect:'Verification',closed:'Closed'};

function ncrStepClass(ncrStatus, step) {
    const ci = NCR_STAGES.indexOf(ncrStatus);
    const si = NCR_STAGES.indexOf(step);
    if (ncrStatus === 'voided') return '';
    if (si < ci) return 'done';
    if (si === ci) return 'active';
    return '';
}

function renderNCRs() {
    const list = document.getElementById('ncrsList');
    let ncrs = qcData?.ncrs || [];
    // Filters
    const fStatus = document.getElementById('ncrFilterStatus').value;
    const fSev = document.getElementById('ncrFilterSeverity').value;
    if (fStatus !== 'all') ncrs = ncrs.filter(n => n.status === fStatus);
    if (fSev !== 'all') ncrs = ncrs.filter(n => n.severity === fSev);
    // Sort: open first, then by severity (critical > major > minor), then by date
    const sevOrder = {critical:0, major:1, minor:2};
    ncrs.sort((a,b) => {
        if (a.status === 'closed' && b.status !== 'closed') return 1;
        if (a.status !== 'closed' && b.status === 'closed') return -1;
        if ((sevOrder[a.severity]||9) !== (sevOrder[b.severity]||9)) return (sevOrder[a.severity]||9) - (sevOrder[b.severity]||9);
        return (b.created_at||'').localeCompare(a.created_at||'');
    });
    if (!ncrs.length) {
        list.innerHTML = '<div class="empty-state"><div class="icon">&#10003;</div><div>No NCRs matching filter — great quality work!</div></div>';
        return;
    }
    list.innerHTML = ncrs.map(n => {
        const isExpanded = (window._expandedNCR === n.id);
        return `
        <div class="ncr-card ${n.severity} ${n.status}" id="ncr-${n.id}">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:4px;cursor:pointer;" onclick="toggleNCRDetail('${n.id}')">
                <div>
                    <div style="font-weight:700;font-size:var(--tf-text-md);color:var(--tf-gray-900);">${n.id}: ${n.title}</div>
                    <div style="font-size:var(--tf-text-xs);color:var(--tf-gray-500);margin-top:2px;">
                        Reported by ${n.reported_by||'—'} on ${n.created_at ? new Date(n.created_at).toLocaleDateString() : ''}
                        ${n.assigned_to ? ' &middot; Assigned to <b>'+n.assigned_to+'</b>' : ''}
                    </div>
                </div>
                <div style="display:flex;gap:6px;align-items:center;">
                    <span class="severity-badge ${n.severity}">${n.severity}</span>
                    <span class="status-badge ${n.status}">${(n.status||'').replace(/_/g,' ')}</span>
                    <span style="font-size:18px;color:var(--tf-gray-400);">${isExpanded ? '&#9650;' : '&#9660;'}</span>
                </div>
            </div>
            <!-- Workflow stepper -->
            <div class="ncr-stepper">
                ${NCR_STAGES.map(s => '<div class="ncr-step '+ncrStepClass(n.status,s)+'">'+NCR_STAGE_LABELS[s]+'</div>').join('')}
            </div>
            <div style="font-size:var(--tf-text-sm);color:var(--tf-gray-700);margin-bottom:4px;">${n.description||''}</div>
            ${(n.member_marks||[]).length ? '<div style="font-size:var(--tf-text-xs);color:var(--tf-gray-500);">Members: '+(n.member_marks||[]).join(', ')+'</div>' : ''}
            ${n.root_cause ? '<div style="margin-top:6px;padding:6px 10px;background:#FEF3C7;border:1px solid #F59E0B;border-radius:6px;font-size:12px;"><b>Root Cause:</b> '+n.root_cause+'</div>' : ''}
            ${n.corrective_action ? '<div style="margin-top:6px;padding:6px 10px;background:#DBEAFE;border:1px solid #3B82F6;border-radius:6px;font-size:12px;"><b>Corrective Action:</b> '+n.corrective_action+'</div>' : ''}
            ${n.disposition ? '<div style="margin-top:6px;padding:6px 10px;background:#D1FAE5;border:1px solid #10B981;border-radius:6px;font-size:12px;"><b>Disposition:</b> '+n.disposition+'</div>' : ''}

            <!-- EXPANDED DETAIL (workflow forms) -->
            ${isExpanded ? renderNCRDetail(n) : ''}

            <!-- Quick action buttons -->
            <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap;">
                ${!isExpanded && n.status!=='closed' && n.status!=='voided' ? '<button class="btn btn-outline btn-sm" onclick="toggleNCRDetail(\''+n.id+'\')">Expand</button>' : ''}
                ${n.status==='open' ? '<button class="btn btn-primary btn-sm" style="background:var(--tf-primary);" onclick="advanceNCR(\''+n.id+'\',\'under_review\')">Begin Investigation</button>' : ''}
                ${n.status==='under_review' ? '<button class="btn btn-primary btn-sm" style="background:#D97706;" onclick="saveNCRRootCause(\''+n.id+'\')">Save Root Cause &amp; Advance</button>' : ''}
                ${n.status==='corrective_action' ? '<button class="btn btn-primary btn-sm" style="background:#2563EB;" onclick="saveNCRCorrectiveAction(\''+n.id+'\')">Save Action &amp; Request Verification</button>' : ''}
                ${n.status==='re_inspect' ? '<button class="btn btn-primary btn-sm" style="background:var(--tf-success);" onclick="saveNCRVerification(\''+n.id+'\')">Verify &amp; Close</button>' : ''}
                ${n.status!=='closed' && n.status!=='voided' ? '<button class="btn btn-outline btn-sm" style="color:var(--tf-gray-500);border-color:var(--tf-gray-300);" onclick="voidNCR(\''+n.id+'\')">Void</button>' : ''}
            </div>
        </div>`;
    }).join('');
}

function renderNCRDetail(n) {
    const hist = (n.history||[]).slice().reverse();
    return `<div class="ncr-detail">
        <!-- Root Cause Section -->
        <div class="ncr-detail-section">
            <h4>&#128269; Root Cause Analysis</h4>
            ${n.status==='under_review' ?
                '<textarea id="ncr-rc-'+n.id+'" placeholder="Describe the root cause of this non-conformance...&#10;&#10;Use 5-Why or Fishbone analysis methods.">'+(n.root_cause||'')+'</textarea>' :
                '<div style="font-size:13px;color:var(--tf-gray-700);">'+(n.root_cause||'<em style=&quot;color:var(--tf-gray-400)&quot;>Not yet documented</em>')+'</div>'
            }
        </div>

        <!-- Corrective Action Section -->
        <div class="ncr-detail-section">
            <h4>&#128736; Corrective &amp; Preventive Action</h4>
            ${n.status==='corrective_action' ? `
                <label style="font-size:12px;font-weight:600;margin-bottom:4px;display:block;">Corrective Action *</label>
                <textarea id="ncr-ca-${n.id}" placeholder="What action will be taken to correct this specific non-conformance?">${n.corrective_action||''}</textarea>
                <label style="font-size:12px;font-weight:600;margin:10px 0 4px;display:block;">Preventive Action</label>
                <textarea id="ncr-pa-${n.id}" placeholder="What systemic changes will prevent recurrence?">${n.preventive_action||''}</textarea>
                <label style="font-size:12px;font-weight:600;margin:10px 0 4px;display:block;">Disposition *</label>
                <select id="ncr-disp-${n.id}">
                    <option value="">Select disposition...</option>
                    <option value="rework" ${n.disposition==='rework'?'selected':''}>Rework — Correct to meet specifications</option>
                    <option value="repair" ${n.disposition==='repair'?'selected':''}>Repair — Restore to serviceable condition</option>
                    <option value="accept-as-is" ${n.disposition==='accept-as-is'?'selected':''}>Accept As-Is — Use without correction (engineer approval)</option>
                    <option value="reject" ${n.disposition==='reject'?'selected':''}>Reject — Scrap or return material</option>
                </select>
            ` : `
                <div style="font-size:13px;color:var(--tf-gray-700);">${n.corrective_action||'<em style=&quot;color:var(--tf-gray-400)&quot;>Not yet documented</em>'}</div>
                ${n.preventive_action ? '<div style="font-size:13px;color:var(--tf-gray-700);margin-top:6px;"><b>Preventive:</b> '+n.preventive_action+'</div>' : ''}
            `}
        </div>

        <!-- Verification Section -->
        <div class="ncr-detail-section">
            <h4>&#9989; Verification / Re-Inspection</h4>
            ${n.status==='re_inspect' ? `
                <label style="font-size:12px;font-weight:600;margin-bottom:4px;display:block;">Verification Inspector</label>
                <input type="text" id="ncr-vinsp-${n.id}" class="form-input" placeholder="Inspector name" style="margin-bottom:8px;max-width:300px;">
                <label style="font-size:12px;font-weight:600;margin-bottom:4px;display:block;">Verification Notes</label>
                <textarea id="ncr-vnotes-${n.id}" placeholder="Confirm corrective action was implemented and non-conformance is resolved."></textarea>
                <label style="font-size:12px;font-weight:600;margin:10px 0 4px;display:block;">Verification Result</label>
                <select id="ncr-vresult-${n.id}">
                    <option value="passed">Passed — Corrective action effective</option>
                    <option value="failed">Failed — Further action required</option>
                </select>
            ` : `
                ${n.verification_inspector ? '<div style="font-size:13px;color:var(--tf-gray-700);"><b>Inspector:</b> '+n.verification_inspector+'</div>' : ''}
                ${n.verification_notes ? '<div style="font-size:13px;color:var(--tf-gray-700);margin-top:4px;">'+n.verification_notes+'</div>' : ''}
                ${n.status==='closed' && n.closed_at ? '<div style="font-size:12px;color:var(--tf-success);margin-top:4px;font-weight:600;">Closed on '+new Date(n.closed_at).toLocaleDateString()+'</div>' : ''}
                ${!n.verification_inspector && n.status!=='re_inspect' ? '<em style="font-size:13px;color:var(--tf-gray-400);">Pending — corrective action must be completed first</em>' : ''}
            `}
        </div>

        <!-- Audit History -->
        <div class="ncr-detail-section">
            <h4>&#128203; Audit Trail (${hist.length} entries)</h4>
            <div class="ncr-history">
                ${hist.map(h => '<div class="ncr-history-item"><b>'+h.action+'</b> by '+(h.by||'system')+' on '+(h.at ? new Date(h.at).toLocaleString() : '—')+'</div>').join('')}
            </div>
        </div>
    </div>`;
}

function toggleNCRDetail(ncrId) {
    window._expandedNCR = (window._expandedNCR === ncrId) ? null : ncrId;
    renderNCRs();
}

async function advanceNCR(ncrId, newStatus) {
    await fetch('/api/qc/ncr/update', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ job_code: JOB_CODE, ncr_id: ncrId, status: newStatus })
    });
    window._expandedNCR = ncrId;
    loadQCData();
}

async function saveNCRRootCause(ncrId) {
    const rc = document.getElementById('ncr-rc-'+ncrId);
    if (!rc || !rc.value.trim()) { alert('Please document the root cause before advancing.'); return; }
    await fetch('/api/qc/ncr/update', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({
            job_code: JOB_CODE, ncr_id: ncrId,
            root_cause: rc.value.trim(),
            status: 'corrective_action'
        })
    });
    window._expandedNCR = ncrId;
    loadQCData();
}

async function saveNCRCorrectiveAction(ncrId) {
    const ca = document.getElementById('ncr-ca-'+ncrId);
    const pa = document.getElementById('ncr-pa-'+ncrId);
    const disp = document.getElementById('ncr-disp-'+ncrId);
    if (!ca || !ca.value.trim()) { alert('Corrective action is required.'); return; }
    if (!disp || !disp.value) { alert('Disposition is required.'); return; }
    await fetch('/api/qc/ncr/update', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({
            job_code: JOB_CODE, ncr_id: ncrId,
            corrective_action: ca.value.trim(),
            preventive_action: (pa ? pa.value.trim() : ''),
            disposition: disp.value,
            status: 're_inspect'
        })
    });
    window._expandedNCR = ncrId;
    loadQCData();
}

async function saveNCRVerification(ncrId) {
    const vinsp = document.getElementById('ncr-vinsp-'+ncrId);
    const vnotes = document.getElementById('ncr-vnotes-'+ncrId);
    const vresult = document.getElementById('ncr-vresult-'+ncrId);
    if (!vinsp || !vinsp.value.trim()) { alert('Verification inspector name is required.'); return; }
    if (!vnotes || !vnotes.value.trim()) { alert('Verification notes are required.'); return; }
    const passed = vresult && vresult.value === 'passed';
    await fetch('/api/qc/ncr/update', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({
            job_code: JOB_CODE, ncr_id: ncrId,
            verification_inspector: vinsp.value.trim(),
            verification_notes: vnotes.value.trim(),
            verification_result: vresult ? vresult.value : 'passed',
            status: passed ? 'closed' : 'corrective_action'
        })
    });
    window._expandedNCR = passed ? null : ncrId;
    loadQCData();
}

async function voidNCR(ncrId) {
    if (!confirm('Are you sure you want to void this NCR? This cannot be undone.')) return;
    await fetch('/api/qc/ncr/update', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ job_code: JOB_CODE, ncr_id: ncrId, status: 'voided' })
    });
    loadQCData();
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

// updateNCRStatus kept for backward compat
async function updateNCRStatus(ncrId, status) { advanceNCR(ncrId, status); }

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

// ═══════════════════════════════════════════════════
// AISC INSPECTION REPORT GENERATION
// ═══════════════════════════════════════════════════

const COMP_STAGES = {
    column:   [{v:'material_receiving',l:'Material Receiving'},{v:'dimensional',l:'Dimensional / Fit-Up'},{v:'weld_visual',l:'Weld Visual (VT)'},{v:'surface_prep',l:'Surface Prep / Coating'},{v:'final_inspection',l:'Final QC Release'}],
    rafter:   [{v:'material_receiving',l:'Material Receiving'},{v:'dimensional',l:'Dimensional / Fit-Up'},{v:'weld_visual',l:'Weld Visual (VT)'},{v:'surface_prep',l:'Surface Prep / Coating'},{v:'final_inspection',l:'Final QC Release'}],
    purlin:   [{v:'material_receiving',l:'Material Receiving'},{v:'dimensional',l:'Dimensional'},{v:'final_inspection',l:'Final QC Release'}],
    sag_rod:  [{v:'material_receiving',l:'Material Receiving'},{v:'dimensional',l:'Dimensional'}],
    strap:    [{v:'material_receiving',l:'Material Receiving'},{v:'dimensional',l:'Dimensional'}],
    endcap:   [{v:'material_receiving',l:'Material Receiving'},{v:'dimensional',l:'Dimensional'}],
    p1clip:   [{v:'material_receiving',l:'Material Receiving'},{v:'dimensional',l:'Dimensional'}],
    p2plate:  [{v:'material_receiving',l:'Material Receiving'},{v:'dimensional',l:'Dimensional'}],
    splice:   [{v:'material_receiving',l:'Material Receiving'},{v:'dimensional',l:'Dimensional'}],
};

function initReportStageSelector() {
    const compSel = document.getElementById('rptCompType');
    const stageSel = document.getElementById('rptStage');
    compSel.addEventListener('change', function() {
        stageSel.innerHTML = '<option value="">Select stage...</option>';
        const stages = COMP_STAGES[this.value] || [];
        stages.forEach(s => {
            stageSel.innerHTML += '<option value="' + s.v + '">' + s.l + '</option>';
        });
    });
}

async function generateSingleReport() {
    const shipMark = document.getElementById('rptShipMark').value.trim();
    const compType = document.getElementById('rptCompType').value;
    const stage = document.getElementById('rptStage').value;
    const desc = document.getElementById('rptDesc').value.trim();
    const heatNum = document.getElementById('rptHeatNum').value.trim();

    if (!shipMark || !compType || !stage) {
        alert('Please fill in Ship Mark, Component Type, and Inspection Stage.');
        return;
    }

    try {
        const resp = await fetch('/api/qc/inspection-report/pdf', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                job_code: JOB_CODE,
                ship_mark: shipMark,
                component_type: compType,
                stage: stage,
                description: desc,
                heat_number: heatNum,
            })
        });
        if (!resp.ok) {
            const err = await resp.json();
            alert('Error: ' + (err.error || 'Failed to generate report'));
            return;
        }
        const blob = await resp.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        const cd = resp.headers.get('content-disposition') || '';
        const fnMatch = cd.match(/filename="?([^"]+)"?/);
        a.download = fnMatch ? fnMatch[1] : 'inspection_report.pdf';
        a.href = url;
        a.click();
        URL.revokeObjectURL(url);
        loadSavedReports();
    } catch (e) {
        alert('Error generating report: ' + e.message);
    }
}

async function generateFullPacket() {
    const shipMark = document.getElementById('rptShipMark').value.trim();
    const compType = document.getElementById('rptCompType').value;
    const desc = document.getElementById('rptDesc').value.trim();
    const heatNum = document.getElementById('rptHeatNum').value.trim();

    if (!shipMark || !compType) {
        alert('Please fill in Ship Mark and Component Type to generate a full packet.');
        return;
    }

    try {
        const resp = await fetch('/api/qc/inspection-packet/pdf', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                job_code: JOB_CODE,
                ship_mark: shipMark,
                component_type: compType,
                description: desc,
                heat_number: heatNum,
                required_only: true,
            })
        });
        if (!resp.ok) {
            const err = await resp.json();
            alert('Error: ' + (err.error || 'Failed to generate packet'));
            return;
        }
        const blob = await resp.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        const cd = resp.headers.get('content-disposition') || '';
        const fnMatch = cd.match(/filename="?([^"]+)"?/);
        a.download = fnMatch ? fnMatch[1] : 'inspection_packet.pdf';
        a.href = url;
        a.click();
        URL.revokeObjectURL(url);
        loadSavedReports();
    } catch (e) {
        alert('Error generating packet: ' + e.message);
    }
}

async function loadSavedReports() {
    try {
        const r = await fetch('/api/qc/inspection-reports?job_code=' + encodeURIComponent(JOB_CODE));
        const d = await r.json();
        if (!d.ok) return;
        const list = document.getElementById('savedReportsList');
        const badge = document.getElementById('reportsCount');
        badge.textContent = d.reports.length;
        if (!d.reports.length) {
            list.innerHTML = '<div class="empty-state"><div class="icon">&#128196;</div>No inspection reports generated yet.<br>Use the generator above to create reports.</div>';
            return;
        }
        list.innerHTML = d.reports.map(r => {
            const dt = new Date(r.created_at);
            const timeStr = dt.toLocaleDateString() + ' ' + dt.toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});
            const parts = r.filename.replace('.pdf','').split('_');
            const reportType = parts[0] === 'IR' ? 'Single Report' : 'Full Packet';
            const mark = parts[1] || '';
            const stage = parts.length > 2 ? parts[2].replace(/_/g,' ') : '';
            const icon = parts[0] === 'IP' ? '&#128230;' : '&#128196;';
            const badgeClass = parts[0] === 'IP' ? 'background:#C89A2E;color:#000;' : 'background:var(--tf-blue-light);color:var(--tf-blue);';
            return '<div style="display:flex;justify-content:space-between;align-items:center;padding:10px 12px;border:1px solid var(--tf-border);border-radius:var(--tf-radius);margin-bottom:6px;background:var(--tf-surface);transition:all 0.15s;" onmouseover="this.style.boxShadow=\'var(--tf-shadow-md)\'" onmouseout="this.style.boxShadow=\'\'">' +
                '<div style="display:flex;align-items:center;gap:12px;">' +
                    '<span style="font-size:1.4rem;">' + icon + '</span>' +
                    '<div>' +
                        '<div style="font-weight:600;font-size:var(--tf-text-sm);color:var(--tf-gray-900);">' + mark + ' — ' + stage + '</div>' +
                        '<div style="font-size:11px;color:var(--tf-gray-500);">' +
                            '<span style="display:inline-block;padding:1px 6px;border-radius:4px;font-size:10px;font-weight:700;margin-right:6px;' + badgeClass + '">' + reportType + '</span>' +
                            timeStr + ' &middot; ' + r.size_kb + ' KB' +
                        '</div>' +
                    '</div>' +
                '</div>' +
                '<div style="display:flex;gap:8px;">' +
                    '<a href="' + r.url + '" target="_blank" class="btn btn-outline btn-sm" style="font-size:11px;">&#128065; View</a>' +
                    '<a href="' + r.url + '" download class="btn btn-primary btn-sm" style="font-size:11px;">&#11015; Download</a>' +
                '</div>' +
            '</div>';
        }).join('');
    } catch (e) {
        console.error('Failed to load saved reports:', e);
    }
}

async function loadInspRequirements() {
    try {
        const r = await fetch('/api/qc/inspection-requirements?job_code=' + encodeURIComponent(JOB_CODE));
        const d = await r.json();
        if (!d.ok) { alert('Could not load requirements'); return; }
        const container = document.getElementById('requirementsMatrix');
        const content = document.getElementById('requirementsContent');
        container.style.display = 'block';

        const summary = d.summary;
        if (!summary || !summary.summary_table || summary.summary_table.length === 0) {
            content.innerHTML = '<div class="empty-state"><div class="icon">&#128203;</div>No work order items found for this job.<br>Create a work order first to see required inspections.</div>';
            return;
        }

        let html = '<div style="margin-bottom:12px;font-size:var(--tf-text-sm);color:var(--tf-gray-700);">' +
            '<strong>' + summary.total_inspections + '</strong> total inspections required across all members.</div>';

        html += '<table class="trace-table"><thead><tr>' +
            '<th>Ship Mark</th><th>Component</th><th>Inspection Stage</th><th>When</th><th>Actions</th><th>Qty</th><th>Generate</th>' +
            '</tr></thead><tbody>';

        summary.summary_table.forEach(row => {
            html += '<tr>' +
                '<td><span class="trace-tag">' + row.ship_mark + '</span></td>' +
                '<td>' + row.component_label + '</td>' +
                '<td style="font-weight:600;">' + row.stage_label + '</td>' +
                '<td style="font-size:11px;color:var(--tf-gray-500);">' + row.when + '</td>' +
                '<td style="text-align:center;">' + row.action_count + '</td>' +
                '<td style="text-align:center;">' + row.quantity + '</td>' +
                '<td><button class="btn btn-outline btn-sm" style="font-size:10px;padding:2px 8px;" onclick="quickGenReport(\'' + row.ship_mark + '\',\'' + row.component_type + '\',\'' + row.stage + '\')">&#128196; PDF</button></td>' +
                '</tr>';
        });
        html += '</tbody></table>';
        content.innerHTML = html;
    } catch (e) {
        alert('Error loading requirements: ' + e.message);
    }
}

function quickGenReport(mark, compType, stage) {
    document.getElementById('rptShipMark').value = mark;
    document.getElementById('rptCompType').value = compType;
    document.getElementById('rptCompType').dispatchEvent(new Event('change'));
    setTimeout(() => {
        document.getElementById('rptStage').value = stage;
        generateSingleReport();
    }, 100);
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
