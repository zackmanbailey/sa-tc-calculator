from templates.shared_styles import DESIGN_SYSTEM_CSS

QUOTE_EDITOR_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TitanForge — Quote Editor</title>
    <style>
""" + DESIGN_SYSTEM_CSS + r"""

        .container { max-width: 1200px; margin: 0 auto; padding: var(--tf-sp-6) var(--tf-sp-8); }

        /* Section tabs */
        .quote-tabs {
            display: flex; gap: 0; border-bottom: 2px solid var(--tf-border);
            margin-bottom: var(--tf-sp-6); overflow-x: auto;
        }
        .quote-tab {
            padding: 10px 20px; font-size: var(--tf-text-sm); font-weight: 600;
            color: var(--tf-gray-500); background: none; border: none;
            border-bottom: 2px solid transparent; margin-bottom: -2px;
            cursor: pointer; white-space: nowrap;
            transition: all var(--tf-duration) var(--tf-ease);
        }
        .quote-tab:hover { color: var(--tf-gray-700); }
        .quote-tab.active { color: var(--tf-blue); border-bottom-color: var(--tf-blue); }

        .quote-section { display: none; }
        .quote-section.active { display: block; }

        /* Form rows */
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: var(--tf-sp-4); margin-bottom: var(--tf-sp-4); }
        .form-row.full { grid-template-columns: 1fr; }
        .form-row.triple { grid-template-columns: 1fr 1fr 1fr; }
        .form-group { display: flex; flex-direction: column; }
        .form-group label { font-size: var(--tf-text-xs); font-weight: 600; color: var(--tf-gray-500); text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 4px; }
        .form-group input, .form-group textarea, .form-group select {
            padding: 8px 12px; border: 1px solid var(--tf-border); border-radius: var(--tf-radius);
            font-size: var(--tf-text-sm); font-family: var(--tf-font);
            transition: border-color var(--tf-duration) var(--tf-ease);
        }
        .form-group input:focus, .form-group textarea:focus { outline: none; border-color: var(--tf-blue); box-shadow: 0 0 0 3px rgba(30,64,175,0.1); }

        /* Editable list */
        .editable-list { margin-bottom: var(--tf-sp-4); }
        .editable-item {
            display: flex; align-items: flex-start; gap: 8px; margin-bottom: 6px;
            padding: 8px 12px; border: 1px solid var(--tf-border); border-radius: var(--tf-radius);
            background: var(--tf-surface);
        }
        .editable-item .item-num { font-size: var(--tf-text-xs); font-weight: 700; color: var(--tf-gray-400); min-width: 24px; padding-top: 4px; }
        .editable-item input, .editable-item textarea {
            flex: 1; border: none; font-size: var(--tf-text-sm); font-family: var(--tf-font);
            padding: 2px 0; outline: none; resize: none; background: transparent;
        }
        .editable-item .remove-btn {
            background: none; border: none; color: var(--tf-gray-300); cursor: pointer;
            font-size: 1.1rem; padding: 0 4px; flex-shrink: 0;
        }
        .editable-item .remove-btn:hover { color: var(--tf-danger); }
        .add-item-btn {
            display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px;
            background: none; border: 1px dashed var(--tf-border); border-radius: var(--tf-radius);
            color: var(--tf-gray-500); font-size: var(--tf-text-sm); cursor: pointer;
            transition: all var(--tf-duration) var(--tf-ease);
        }
        .add-item-btn:hover { border-color: var(--tf-blue); color: var(--tf-blue); background: var(--tf-blue-light); }

        /* Pricing table */
        .price-row { display: grid; grid-template-columns: 1fr 160px 40px; gap: 8px; margin-bottom: 6px; align-items: center; }
        .price-row input { padding: 8px 12px; border: 1px solid var(--tf-border); border-radius: var(--tf-radius); font-size: var(--tf-text-sm); }
        .price-row .amount-input { text-align: right; font-weight: 600; }
        .price-total {
            display: flex; justify-content: space-between; padding: 12px 16px;
            background: var(--tf-blue-light); border-radius: var(--tf-radius);
            font-weight: 700; font-size: var(--tf-text-md); color: var(--tf-blue);
            margin-top: var(--tf-sp-3);
        }

        /* Milestone table */
        .milestone-row { display: grid; grid-template-columns: 1fr 80px 120px 40px; gap: 8px; margin-bottom: 6px; align-items: center; }
        .milestone-row input { padding: 8px 12px; border: 1px solid var(--tf-border); border-radius: var(--tf-radius); font-size: var(--tf-text-sm); }
        .milestone-row .pct-input { text-align: center; font-weight: 600; }

        /* Exclusion categories */
        .excl-category {
            margin-bottom: var(--tf-sp-5); border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-lg); overflow: hidden;
        }
        .excl-cat-header {
            display: flex; justify-content: space-between; align-items: center;
            padding: 10px 16px; background: var(--tf-gray-50); cursor: pointer;
            font-weight: 700; font-size: var(--tf-text-sm); color: var(--tf-gray-700);
        }
        .excl-cat-header:hover { background: var(--tf-gray-100); }
        .excl-cat-body { padding: 8px 16px; }

        /* Save indicator */
        .save-indicator {
            position: fixed; bottom: 24px; right: 24px; background: var(--tf-success);
            color: #fff; padding: 10px 20px; border-radius: var(--tf-radius);
            font-size: var(--tf-text-sm); font-weight: 600; box-shadow: var(--tf-shadow-lg);
            transform: translateY(80px); transition: transform 0.3s var(--tf-ease);
            z-index: 100;
        }
        .save-indicator.show { transform: translateY(0); }

        /* Global Search Overlay */
        .global-search-overlay {
            display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(15,23,42,0.5); z-index: 300; align-items: flex-start;
            justify-content: center; padding-top: 100px;
        }
        .global-search-overlay.open { display: flex; }
        .global-search-box {
            width: 600px; max-width: 90vw; background: var(--tf-surface);
            border-radius: var(--tf-radius-xl); box-shadow: var(--tf-shadow-lg); overflow: hidden;
        }
        .global-search-input {
            width: 100%; padding: 18px 20px; border: none; font-size: var(--tf-text-lg);
            outline: none; border-bottom: 1px solid var(--tf-border);
        }
        .global-search-results { max-height: 400px; overflow-y: auto; padding: var(--tf-sp-2); }
        .gsr-item {
            display: flex; align-items: center; gap: var(--tf-sp-3);
            padding: 10px 14px; border-radius: var(--tf-radius); cursor: pointer;
            transition: background var(--tf-duration) var(--tf-ease);
        }
        .gsr-item:hover { background: var(--tf-blue-light); }
        .gsr-icon {
            width: 32px; height: 32px; border-radius: var(--tf-radius-sm);
            display: flex; align-items: center; justify-content: center; font-size: 14px;
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
            .form-row, .form-row.triple { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="tf-topbar">
        <a href="/" class="tf-logo">
            <div class="tf-logo-icon">&#9878;</div>
            TITANFORGE
        </a>
        <nav>
            <a href="/">Dashboard</a>
            <a href="/sa">Structures America Estimator</a>
            <a href="/tc">Titan Carports Estimator</a>
            <a href="/customers">Customers</a>
        </nav>
        <div class="tf-user">
            <button onclick="openGlobalSearch()" style="background:none;border:1px solid rgba(255,255,255,0.2);color:#fff;padding:6px 14px;border-radius:var(--tf-radius);cursor:pointer;font-size:var(--tf-text-sm);margin-right:12px;display:flex;align-items:center;gap:6px;">
                &#128269; Search <kbd style="background:rgba(255,255,255,0.15);padding:1px 6px;border-radius:4px;font-size:10px;margin-left:4px;">Ctrl+K</kbd>
            </button>
            <div class="user-section">
                <span id="userName">{{USER_NAME}}</span>
                <span class="role-badge" id="userRole">{{USER_ROLE}}</span>
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

    <div class="container">
        <!-- Header -->
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:var(--tf-sp-5);">
            <div>
                <h1 style="font-size:var(--tf-text-2xl);font-weight:700;color:var(--tf-gray-900);">
                    Quote Editor <span style="font-size:var(--tf-text-base);color:var(--tf-blue);font-weight:600;">{{JOB_CODE}}</span>
                </h1>
                <p style="color:var(--tf-gray-500);font-size:var(--tf-text-sm);margin-top:2px;">
                    Edit all sections of the quote, then generate a professional PDF
                </p>
            </div>
            <div style="display:flex;gap:var(--tf-sp-3);">
                <button class="btn btn-outline" onclick="saveQuote()">&#128190; Save Draft</button>
                <button class="btn btn-primary" onclick="generatePDF()">&#128196; Generate PDF</button>
                <a href="/project/{{JOB_CODE}}" class="btn btn-outline">&#8592; Back to Project</a>
            </div>
        </div>

        <!-- Section Tabs -->
        <div class="quote-tabs">
            <button class="quote-tab active" onclick="switchTab('overview')">Project Overview</button>
            <button class="quote-tab" onclick="switchTab('pricing')">Pricing</button>
            <button class="quote-tab" onclick="switchTab('inclusions')">Inclusions</button>
            <button class="quote-tab" onclick="switchTab('exclusions')">Exclusions</button>
            <button class="quote-tab" onclick="switchTab('project_details')">Project Details</button>
            <button class="quote-tab" onclick="switchTab('payment')">Payment Terms</button>
            <button class="quote-tab" onclick="switchTab('signature')">Signature</button>
            <button class="quote-tab" onclick="switchTab('qualifications')">Qualifications</button>
            <button class="quote-tab" onclick="switchTab('conditions')">Conditions</button>
            <button class="quote-tab" onclick="switchTab('terms')">Terms</button>
        </div>

        <!-- ── PROJECT OVERVIEW TAB ── -->
        <div class="quote-section active" id="sec-overview">
            <h2 style="font-size:var(--tf-text-lg);font-weight:700;margin-bottom:var(--tf-sp-4);">1.1 Project Overview</h2>
            <div style="border:1px solid var(--tf-border);border-radius:var(--tf-radius-lg);padding:var(--tf-sp-5);background:var(--tf-surface);">
                <h3 style="font-size:var(--tf-text-sm);font-weight:700;color:var(--tf-gray-500);text-transform:uppercase;margin-bottom:var(--tf-sp-3);">Company Info</h3>
                <div class="form-row">
                    <div class="form-group"><label>Company Name</label><input type="text" id="qCompanyName" onchange="markDirty()"></div>
                    <div class="form-group"><label>Estimator Name</label><input type="text" id="qEstimatorName" onchange="markDirty()"></div>
                </div>
                <div class="form-row triple">
                    <div class="form-group"><label>Company Phone</label><input type="text" id="qCompanyPhone" onchange="markDirty()"></div>
                    <div class="form-group"><label>Estimator Phone</label><input type="text" id="qEstimatorPhone" onchange="markDirty()"></div>
                    <div class="form-group"><label>Estimator Email</label><input type="text" id="qEstimatorEmail" onchange="markDirty()"></div>
                </div>

                <h3 style="font-size:var(--tf-text-sm);font-weight:700;color:var(--tf-gray-500);text-transform:uppercase;margin:var(--tf-sp-5) 0 var(--tf-sp-3);">Customer Info</h3>
                <div class="form-row">
                    <div class="form-group"><label>Customer Name</label><input type="text" id="qCustomerName" onchange="markDirty()"></div>
                    <div class="form-group"><label>Customer Company</label><input type="text" id="qCustomerCompany" onchange="markDirty()"></div>
                </div>
                <div class="form-row full">
                    <div class="form-group"><label>Job Address</label><input type="text" id="qJobAddress" onchange="markDirty()"></div>
                </div>
                <div class="form-row triple">
                    <div class="form-group"><label>City</label><input type="text" id="qJobCity" onchange="markDirty()"></div>
                    <div class="form-group"><label>State</label><input type="text" id="qJobState" onchange="markDirty()"></div>
                    <div class="form-group"><label>Zip</label><input type="text" id="qJobZip" onchange="markDirty()"></div>
                </div>

                <h3 style="font-size:var(--tf-text-sm);font-weight:700;color:var(--tf-gray-500);text-transform:uppercase;margin:var(--tf-sp-5) 0 var(--tf-sp-3);">Quote Details</h3>
                <div class="form-row triple">
                    <div class="form-group"><label>Quote Number</label><input type="text" id="qQuoteNumber" onchange="markDirty()"></div>
                    <div class="form-group"><label>Quote Date</label><input type="date" id="qQuoteDate" onchange="markDirty()"></div>
                    <div class="form-group"><label>Valid For (days)</label><input type="number" id="qValidDays" value="30" onchange="markDirty()"></div>
                </div>
                <div class="form-row full">
                    <div class="form-group"><label>Project Description</label><textarea id="qProjectDesc" rows="3" onchange="markDirty()"></textarea></div>
                </div>
            </div>
        </div>

        <!-- ── PRICING TAB ── -->
        <div class="quote-section" id="sec-pricing">
            <h2 style="font-size:var(--tf-text-lg);font-weight:700;margin-bottom:var(--tf-sp-4);">1.2 Pricing</h2>
            <div style="border:1px solid var(--tf-border);border-radius:var(--tf-radius-lg);padding:var(--tf-sp-5);background:var(--tf-surface);">
                <h3 style="font-size:var(--tf-text-sm);font-weight:700;color:var(--tf-gray-500);text-transform:uppercase;margin-bottom:var(--tf-sp-3);">Base Pricing</h3>
                <div class="price-row" style="margin-bottom:2px;">
                    <span style="font-size:var(--tf-text-xs);font-weight:700;color:var(--tf-gray-500);">DESCRIPTION</span>
                    <span style="font-size:var(--tf-text-xs);font-weight:700;color:var(--tf-gray-500);text-align:right;">AMOUNT</span>
                    <span></span>
                </div>
                <div id="basePriceItems"></div>
                <button class="add-item-btn" onclick="addBaseItem()">+ Add Line Item</button>
                <div class="price-total"><span>BASE TOTAL</span><span id="baseTotalDisplay">$0.00</span></div>

                <h3 style="font-size:var(--tf-text-sm);font-weight:700;color:var(--tf-gray-500);text-transform:uppercase;margin:var(--tf-sp-5) 0 var(--tf-sp-3);">Options (not included in base)</h3>
                <div id="optionItems"></div>
                <button class="add-item-btn" onclick="addOptionItem()">+ Add Option</button>
            </div>
        </div>

        <!-- ── INCLUSIONS TAB ── -->
        <div class="quote-section" id="sec-inclusions">
            <h2 style="font-size:var(--tf-text-lg);font-weight:700;margin-bottom:var(--tf-sp-4);">Inclusions</h2>
            <div style="border:1px solid var(--tf-border);border-radius:var(--tf-radius-lg);padding:var(--tf-sp-5);background:var(--tf-surface);">
                <div class="editable-list" id="inclusionsList"></div>
                <button class="add-item-btn" onclick="addInclusion()">+ Add Inclusion</button>
            </div>
        </div>

        <!-- ── EXCLUSIONS TAB ── -->
        <div class="quote-section" id="sec-exclusions">
            <h2 style="font-size:var(--tf-text-lg);font-weight:700;margin-bottom:var(--tf-sp-4);">2.2 Exclusions (Categorized)</h2>
            <div id="exclusionsContainer"></div>
            <button class="add-item-btn" style="margin-top:var(--tf-sp-3);" onclick="addExclCategory()">+ Add Category</button>
        </div>

        <!-- ── PROJECT DETAILS TAB ── -->
        <div class="quote-section" id="sec-project_details">
            <h2 style="font-size:var(--tf-text-lg);font-weight:700;margin-bottom:var(--tf-sp-4);">1.4 General Project Overview</h2>
            <div style="border:1px solid var(--tf-border);border-radius:var(--tf-radius-lg);padding:var(--tf-sp-5);background:var(--tf-surface);">
                <div class="form-row full">
                    <div class="form-group"><label>Project Description</label><textarea id="qGpoDesc" rows="4" onchange="markDirty()"></textarea></div>
                </div>
                <h3 style="font-size:var(--tf-text-sm);font-weight:700;color:var(--tf-gray-500);text-transform:uppercase;margin:var(--tf-sp-4) 0 var(--tf-sp-3);">Project Specifications</h3>
                <div id="specsContainer"></div>
                <button class="add-item-btn" onclick="addSpec()">+ Add Specification</button>
            </div>
        </div>

        <!-- ── PAYMENT TERMS TAB ── -->
        <div class="quote-section" id="sec-payment">
            <h2 style="font-size:var(--tf-text-lg);font-weight:700;margin-bottom:var(--tf-sp-4);">1.6 Payment Terms</h2>
            <div style="border:1px solid var(--tf-border);border-radius:var(--tf-radius-lg);padding:var(--tf-sp-5);background:var(--tf-surface);">
                <div class="form-row full">
                    <div class="form-group"><label>Engineering Fee Note</label><textarea id="qEngNote" rows="2" onchange="markDirty()"></textarea></div>
                </div>
                <div class="form-row full">
                    <div class="form-group"><label>Billing Description</label><textarea id="qBillingDesc" rows="3" onchange="markDirty()"></textarea></div>
                </div>
                <div class="form-row triple">
                    <div class="form-group"><label>Net Days</label><input type="number" id="qNetDays" value="30" onchange="markDirty()"></div>
                    <div class="form-group"><label>Late Fee %</label><input type="number" id="qLateFee" value="1.5" step="0.1" onchange="markDirty()"></div>
                    <div class="form-group"><label>Retainage %</label><input type="number" id="qRetainage" value="0" step="0.5" onchange="markDirty()"></div>
                </div>
                <h3 style="font-size:var(--tf-text-sm);font-weight:700;color:var(--tf-gray-500);text-transform:uppercase;margin:var(--tf-sp-4) 0 var(--tf-sp-3);">Monthly Progress Billing Milestones</h3>
                <div class="milestone-row" style="margin-bottom:4px;">
                    <span style="font-size:var(--tf-text-xs);font-weight:700;color:var(--tf-gray-500);">MILESTONE</span>
                    <span style="font-size:var(--tf-text-xs);font-weight:700;color:var(--tf-gray-500);text-align:center;">%</span>
                    <span style="font-size:var(--tf-text-xs);font-weight:700;color:var(--tf-gray-500);text-align:right;">AMOUNT</span>
                    <span></span>
                </div>
                <div id="milestoneItems"></div>
                <button class="add-item-btn" onclick="addMilestone()">+ Add Milestone</button>
                <div class="price-total" style="margin-top:var(--tf-sp-3);">
                    <span>TOTAL</span><span id="milestoneTotalDisplay">100%</span>
                </div>
            </div>
        </div>

        <!-- ── SIGNATURE TAB ── -->
        <div class="quote-section" id="sec-signature">
            <h2 style="font-size:var(--tf-text-lg);font-weight:700;margin-bottom:var(--tf-sp-4);">Signature Block</h2>
            <div style="border:1px solid var(--tf-border);border-radius:var(--tf-radius-lg);padding:var(--tf-sp-5);background:var(--tf-surface);">
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:var(--tf-sp-6);">
                    <div>
                        <h3 style="font-size:var(--tf-text-sm);font-weight:700;color:var(--tf-gray-500);text-transform:uppercase;margin-bottom:var(--tf-sp-3);">Titan Carports</h3>
                        <div class="form-group" style="margin-bottom:var(--tf-sp-3);"><label>Signer Name</label><input type="text" id="qCompanySigner" onchange="markDirty()"></div>
                        <div class="form-group"><label>Title</label><input type="text" id="qCompanySignerTitle" onchange="markDirty()"></div>
                    </div>
                    <div>
                        <h3 style="font-size:var(--tf-text-sm);font-weight:700;color:var(--tf-gray-500);text-transform:uppercase;margin-bottom:var(--tf-sp-3);">Customer</h3>
                        <div class="form-group" style="margin-bottom:var(--tf-sp-3);"><label>Signer Name</label><input type="text" id="qCustomerSigner" onchange="markDirty()"></div>
                        <div class="form-group"><label>Title</label><input type="text" id="qCustomerSignerTitle" onchange="markDirty()"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- ── QUALIFICATIONS TAB ── -->
        <div class="quote-section" id="sec-qualifications">
            <h2 style="font-size:var(--tf-text-lg);font-weight:700;margin-bottom:var(--tf-sp-4);">2.1 Standard Qualifications</h2>
            <div style="border:1px solid var(--tf-border);border-radius:var(--tf-radius-lg);padding:var(--tf-sp-5);background:var(--tf-surface);">
                <div class="editable-list" id="qualificationsList"></div>
                <button class="add-item-btn" onclick="addQualification()">+ Add Qualification</button>
            </div>
        </div>

        <!-- ── CONDITIONS TAB ── -->
        <div class="quote-section" id="sec-conditions">
            <h2 style="font-size:var(--tf-text-lg);font-weight:700;margin-bottom:var(--tf-sp-4);">3.1 Conditions of Contract</h2>
            <div style="border:1px solid var(--tf-border);border-radius:var(--tf-radius-lg);padding:var(--tf-sp-5);background:var(--tf-surface);">
                <div class="editable-list" id="conditionsList"></div>
                <button class="add-item-btn" onclick="addCondition()">+ Add Condition</button>
            </div>
        </div>

        <!-- ── TERMS TAB ── -->
        <div class="quote-section" id="sec-terms">
            <h2 style="font-size:var(--tf-text-lg);font-weight:700;margin-bottom:var(--tf-sp-4);">3.2 Terms of Contract</h2>
            <div style="border:1px solid var(--tf-border);border-radius:var(--tf-radius-lg);padding:var(--tf-sp-5);background:var(--tf-surface);">
                <div class="editable-list" id="termsList"></div>
                <button class="add-item-btn" onclick="addTerm()">+ Add Term</button>
            </div>
        </div>
    </div>

    <!-- Save indicator -->
    <div class="save-indicator" id="saveIndicator">&#10003; Saved</div>

<script>
const JOB_CODE = '{{JOB_CODE}}';
let quoteData = null;
let isDirty = false;

document.addEventListener('DOMContentLoaded', loadQuoteData);
document.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && e.key === 's') { e.preventDefault(); saveQuote(); }
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') { e.preventDefault(); openGlobalSearch(); }
    if (e.key === 'Escape') closeGlobalSearch();
});

function switchTab(tab) {
    document.querySelectorAll('.quote-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.quote-section').forEach(s => s.classList.remove('active'));
    event.target.classList.add('active');
    document.getElementById('sec-' + tab).classList.add('active');
}

function markDirty() { isDirty = true; }

async function loadQuoteData() {
    try {
        const r = await fetch('/api/quote/data?job_code=' + encodeURIComponent(JOB_CODE));
        const d = await r.json();
        if (d.ok) { quoteData = d.data; populateForm(); }
    } catch(e) { console.error(e); }
}

function populateForm() {
    const po = quoteData.project_overview || {};
    document.getElementById('qCompanyName').value = po.company_name || '';
    document.getElementById('qEstimatorName').value = po.estimator_name || '';
    document.getElementById('qCompanyPhone').value = po.company_phone || '';
    document.getElementById('qEstimatorPhone').value = po.estimator_phone || '';
    document.getElementById('qEstimatorEmail').value = po.estimator_email || '';
    document.getElementById('qCustomerName').value = po.customer_name || '';
    document.getElementById('qCustomerCompany').value = po.customer_company || '';
    document.getElementById('qJobAddress').value = po.job_address || '';
    document.getElementById('qJobCity').value = po.job_city || '';
    document.getElementById('qJobState').value = po.job_state || '';
    document.getElementById('qJobZip').value = po.job_zip || '';
    document.getElementById('qQuoteNumber').value = po.quote_number || JOB_CODE;
    document.getElementById('qQuoteDate').value = po.quote_date || '';
    document.getElementById('qValidDays').value = po.valid_days || 30;
    document.getElementById('qProjectDesc').value = po.project_description || '';

    // Pricing
    renderBasePricing();
    renderOptions();

    // Inclusions
    renderEditableList('inclusionsList', quoteData.inclusions || []);

    // Exclusions
    renderExclusions();

    // GPO
    const gpo = quoteData.general_project_overview || {};
    document.getElementById('qGpoDesc').value = gpo.description || '';
    renderSpecs(gpo.specs || {});

    // Payment
    const pt = quoteData.payment_terms || {};
    document.getElementById('qEngNote').value = pt.engineering_fee_note || '';
    document.getElementById('qBillingDesc').value = pt.billing_description || '';
    document.getElementById('qNetDays').value = pt.net_days || 30;
    document.getElementById('qLateFee').value = pt.late_fee_percent || 1.5;
    document.getElementById('qRetainage').value = pt.retainage_percent || 0;
    renderMilestones();

    // Signature
    const sig = quoteData.signature_block || {};
    document.getElementById('qCompanySigner').value = sig.company_signer_name || '';
    document.getElementById('qCompanySignerTitle').value = sig.company_signer_title || '';
    document.getElementById('qCustomerSigner').value = sig.customer_signer_name || '';
    document.getElementById('qCustomerSignerTitle').value = sig.customer_signer_title || '';

    // Qualifications, Conditions, Terms
    renderEditableList('qualificationsList', quoteData.standard_qualifications || []);
    renderEditableList('conditionsList', quoteData.conditions_of_contract || []);
    renderEditableList('termsList', quoteData.terms_of_contract || []);
}

// ── Pricing ──
function renderBasePricing() {
    const container = document.getElementById('basePriceItems');
    const items = quoteData.pricing?.base_items || [];
    container.innerHTML = items.map((item, i) => `
        <div class="price-row">
            <input type="text" value="${item.description||''}" onchange="updateBaseItem(${i},'description',this.value)">
            <input type="number" class="amount-input" value="${item.amount||0}" step="0.01"
                   onchange="updateBaseItem(${i},'amount',parseFloat(this.value)||0)">
            <button class="editable-item .remove-btn" onclick="removeBaseItem(${i})"
                    style="background:none;border:none;color:var(--tf-gray-300);cursor:pointer;font-size:1.1rem;">&times;</button>
        </div>
    `).join('');
    updateBaseTotal();
}

function updateBaseItem(idx, field, val) {
    quoteData.pricing.base_items[idx][field] = val;
    updateBaseTotal(); markDirty();
}

function addBaseItem() {
    if (!quoteData.pricing) quoteData.pricing = {base_items:[], options:[]};
    quoteData.pricing.base_items.push({description:'', amount:0});
    renderBasePricing(); markDirty();
}

function removeBaseItem(idx) {
    quoteData.pricing.base_items.splice(idx, 1);
    renderBasePricing(); markDirty();
}

function updateBaseTotal() {
    const total = (quoteData.pricing?.base_items||[]).reduce((s,i) => s + (i.amount||0), 0);
    quoteData.pricing.base_total = total;
    document.getElementById('baseTotalDisplay').textContent = '$' + total.toLocaleString('en-US',{minimumFractionDigits:2});
    updateMilestoneAmounts();
}

function renderOptions() {
    const container = document.getElementById('optionItems');
    const items = quoteData.pricing?.options || [];
    container.innerHTML = items.map((item, i) => `
        <div class="price-row">
            <input type="text" value="${item.description||''}" onchange="updateOption(${i},'description',this.value)">
            <input type="number" class="amount-input" value="${item.amount||0}" step="0.01"
                   onchange="updateOption(${i},'amount',parseFloat(this.value)||0)">
            <button onclick="removeOption(${i})"
                    style="background:none;border:none;color:var(--tf-gray-300);cursor:pointer;font-size:1.1rem;">&times;</button>
        </div>
    `).join('');
}

function updateOption(idx, field, val) { quoteData.pricing.options[idx][field] = val; markDirty(); }
function addOptionItem() {
    if (!quoteData.pricing.options) quoteData.pricing.options = [];
    quoteData.pricing.options.push({description:'', amount:0});
    renderOptions(); markDirty();
}
function removeOption(idx) { quoteData.pricing.options.splice(idx,1); renderOptions(); markDirty(); }

// ── Editable Lists ──
function renderEditableList(containerId, items) {
    const container = document.getElementById(containerId);
    container.innerHTML = items.map((item, i) => `
        <div class="editable-item">
            <span class="item-num">${i+1}.</span>
            <input type="text" value="${(item||'').replace(/"/g,'&quot;')}"
                   onchange="updateListItem('${containerId}',${i},this.value)">
            <button class="remove-btn" onclick="removeListItem('${containerId}',${i})">&times;</button>
        </div>
    `).join('');
}

function getListRef(containerId) {
    const map = {
        'inclusionsList': 'inclusions',
        'qualificationsList': 'standard_qualifications',
        'conditionsList': 'conditions_of_contract',
        'termsList': 'terms_of_contract',
    };
    return map[containerId];
}

function updateListItem(cid, idx, val) { quoteData[getListRef(cid)][idx] = val; markDirty(); }
function removeListItem(cid, idx) { quoteData[getListRef(cid)].splice(idx,1); renderEditableList(cid, quoteData[getListRef(cid)]); markDirty(); }

function addInclusion() { quoteData.inclusions.push(''); renderEditableList('inclusionsList', quoteData.inclusions); markDirty(); }
function addQualification() { quoteData.standard_qualifications.push(''); renderEditableList('qualificationsList', quoteData.standard_qualifications); markDirty(); }
function addCondition() { quoteData.conditions_of_contract.push(''); renderEditableList('conditionsList', quoteData.conditions_of_contract); markDirty(); }
function addTerm() { quoteData.terms_of_contract.push(''); renderEditableList('termsList', quoteData.terms_of_contract); markDirty(); }

// ── Exclusions (categorized) ──
function renderExclusions() {
    const container = document.getElementById('exclusionsContainer');
    const cats = quoteData.exclusions_categorized || {};
    container.innerHTML = Object.entries(cats).map(([catName, items], ci) => {
        const itemsHtml = items.map((item, i) => `
            <div class="editable-item">
                <span class="item-num">${i+1}.</span>
                <input type="text" value="${(item||'').replace(/"/g,'&quot;')}"
                       onchange="updateExclItem('${catName}',${i},this.value)">
                <button class="remove-btn" onclick="removeExclItem('${catName}',${i})">&times;</button>
            </div>
        `).join('');
        return `<div class="excl-category">
            <div class="excl-cat-header">
                <span>${catName} (${items.length})</span>
                <div style="display:flex;gap:8px;">
                    <button class="add-item-btn" onclick="event.stopPropagation();addExclItem('${catName}')" style="font-size:11px;padding:2px 8px;">+ Add</button>
                    <button onclick="event.stopPropagation();removeExclCategory('${catName}')" style="background:none;border:none;color:var(--tf-danger);cursor:pointer;font-size:var(--tf-text-xs);">Remove Category</button>
                </div>
            </div>
            <div class="excl-cat-body">${itemsHtml}</div>
        </div>`;
    }).join('');
}

function updateExclItem(cat, idx, val) { quoteData.exclusions_categorized[cat][idx] = val; markDirty(); }
function removeExclItem(cat, idx) { quoteData.exclusions_categorized[cat].splice(idx, 1); renderExclusions(); markDirty(); }
function addExclItem(cat) { quoteData.exclusions_categorized[cat].push(''); renderExclusions(); markDirty(); }
function removeExclCategory(cat) {
    if (confirm('Remove category "' + cat + '" and all its exclusions?')) {
        delete quoteData.exclusions_categorized[cat];
        renderExclusions(); markDirty();
    }
}
function addExclCategory() {
    const name = prompt('Category name:');
    if (name) {
        quoteData.exclusions_categorized[name] = [];
        renderExclusions(); markDirty();
    }
}

// ── Specs ──
function renderSpecs(specs) {
    const container = document.getElementById('specsContainer');
    container.innerHTML = Object.entries(specs).map(([k, v], i) => `
        <div style="display:grid;grid-template-columns:1fr 1fr 40px;gap:8px;margin-bottom:6px;">
            <input type="text" value="${k}" onchange="updateSpecKey(${i},this.value)"
                   style="padding:8px 12px;border:1px solid var(--tf-border);border-radius:var(--tf-radius);font-size:var(--tf-text-sm);">
            <input type="text" value="${v}" onchange="updateSpecVal('${k}',this.value)"
                   style="padding:8px 12px;border:1px solid var(--tf-border);border-radius:var(--tf-radius);font-size:var(--tf-text-sm);">
            <button onclick="removeSpec('${k}')" style="background:none;border:none;color:var(--tf-gray-300);cursor:pointer;font-size:1.1rem;">&times;</button>
        </div>
    `).join('');
}

function updateSpecVal(key, val) { quoteData.general_project_overview.specs[key] = val; markDirty(); }
function updateSpecKey(idx, newKey) {
    const specs = quoteData.general_project_overview.specs;
    const entries = Object.entries(specs);
    const [oldKey, val] = entries[idx];
    delete specs[oldKey];
    specs[newKey] = val;
    markDirty();
}
function removeSpec(key) {
    delete quoteData.general_project_overview.specs[key];
    renderSpecs(quoteData.general_project_overview.specs); markDirty();
}
function addSpec() {
    if (!quoteData.general_project_overview) quoteData.general_project_overview = {specs:{}};
    if (!quoteData.general_project_overview.specs) quoteData.general_project_overview.specs = {};
    quoteData.general_project_overview.specs['New Spec'] = '';
    renderSpecs(quoteData.general_project_overview.specs); markDirty();
}

// ── Milestones ──
function renderMilestones() {
    const container = document.getElementById('milestoneItems');
    const ms = quoteData.payment_terms?.milestones || [];
    const baseTotal = quoteData.pricing?.base_total || 0;
    container.innerHTML = ms.map((m, i) => {
        const amt = baseTotal * (m.percent||0) / 100;
        return `<div class="milestone-row">
            <input type="text" value="${m.label||''}" onchange="updateMilestone(${i},'label',this.value)">
            <input type="number" class="pct-input" value="${m.percent||0}" step="1"
                   onchange="updateMilestone(${i},'percent',parseFloat(this.value)||0)">
            <span style="text-align:right;font-size:var(--tf-text-sm);color:var(--tf-gray-600);font-weight:600;">$${amt.toLocaleString('en-US',{minimumFractionDigits:2})}</span>
            <button onclick="removeMilestone(${i})" style="background:none;border:none;color:var(--tf-gray-300);cursor:pointer;font-size:1.1rem;">&times;</button>
        </div>`;
    }).join('');
    updateMilestoneTotal();
}

function updateMilestone(idx, field, val) {
    quoteData.payment_terms.milestones[idx][field] = val;
    renderMilestones(); markDirty();
}
function removeMilestone(idx) { quoteData.payment_terms.milestones.splice(idx,1); renderMilestones(); markDirty(); }
function addMilestone() {
    quoteData.payment_terms.milestones.push({label:'', percent:0});
    renderMilestones(); markDirty();
}
function updateMilestoneAmounts() { renderMilestones(); }
function updateMilestoneTotal() {
    const total = (quoteData.payment_terms?.milestones||[]).reduce((s,m) => s + (m.percent||0), 0);
    const disp = document.getElementById('milestoneTotalDisplay');
    disp.textContent = total + '%';
    disp.style.color = total === 100 ? '' : 'var(--tf-danger)';
}

// ── Collect form data ──
function collectData() {
    quoteData.project_overview = {
        company_name: document.getElementById('qCompanyName').value,
        estimator_name: document.getElementById('qEstimatorName').value,
        company_phone: document.getElementById('qCompanyPhone').value,
        estimator_phone: document.getElementById('qEstimatorPhone').value,
        estimator_email: document.getElementById('qEstimatorEmail').value,
        customer_name: document.getElementById('qCustomerName').value,
        customer_company: document.getElementById('qCustomerCompany').value,
        job_address: document.getElementById('qJobAddress').value,
        job_city: document.getElementById('qJobCity').value,
        job_state: document.getElementById('qJobState').value,
        job_zip: document.getElementById('qJobZip').value,
        quote_number: document.getElementById('qQuoteNumber').value,
        quote_date: document.getElementById('qQuoteDate').value,
        valid_days: parseInt(document.getElementById('qValidDays').value) || 30,
        project_description: document.getElementById('qProjectDesc').value,
    };
    quoteData.general_project_overview.description = document.getElementById('qGpoDesc').value;
    quoteData.payment_terms.engineering_fee_note = document.getElementById('qEngNote').value;
    quoteData.payment_terms.billing_description = document.getElementById('qBillingDesc').value;
    quoteData.payment_terms.net_days = parseInt(document.getElementById('qNetDays').value) || 30;
    quoteData.payment_terms.late_fee_percent = parseFloat(document.getElementById('qLateFee').value) || 1.5;
    quoteData.payment_terms.retainage_percent = parseFloat(document.getElementById('qRetainage').value) || 0;
    quoteData.signature_block = {
        company_signer_name: document.getElementById('qCompanySigner').value,
        company_signer_title: document.getElementById('qCompanySignerTitle').value,
        customer_signer_name: document.getElementById('qCustomerSigner').value,
        customer_signer_title: document.getElementById('qCustomerSignerTitle').value,
    };
    return quoteData;
}

// ── Save ──
async function saveQuote() {
    const data = collectData();
    try {
        const r = await fetch('/api/quote/data', {
            method: 'POST', headers: {'Content-Type':'application/json'},
            body: JSON.stringify({job_code: JOB_CODE, data})
        });
        const d = await r.json();
        if (d.ok) {
            isDirty = false;
            const ind = document.getElementById('saveIndicator');
            ind.classList.add('show');
            setTimeout(() => ind.classList.remove('show'), 2000);
        }
    } catch(e) { alert('Save failed'); }
}

// ── Generate PDF ──
async function generatePDF() {
    const data = collectData();
    // Save first
    await fetch('/api/quote/data', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({job_code: JOB_CODE, data})
    });
    // Generate
    try {
        const r = await fetch('/api/quote/pdf', {
            method: 'POST', headers: {'Content-Type':'application/json'},
            body: JSON.stringify({job_code: JOB_CODE, data})
        });
        if (r.ok) {
            const blob = await r.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'Quote_' + JOB_CODE + '.pdf';
            a.click();
            URL.revokeObjectURL(url);
        } else {
            const err = await r.json();
            alert('PDF generation failed: ' + (err.error || 'Unknown error'));
        }
    } catch(e) { alert('PDF generation error: ' + e.message); }
}

// ── Global Search ──
let searchTimeout = null;
function openGlobalSearch() {
    document.getElementById('globalSearchOverlay').classList.add('open');
    document.getElementById('globalSearchInput').value = '';
    document.getElementById('globalSearchInput').focus();
    document.getElementById('globalSearchResults').innerHTML = '<div class="gsr-empty">Type to search...</div>';
}
function closeGlobalSearch() { document.getElementById('globalSearchOverlay').classList.remove('open'); }
document.getElementById('globalSearchOverlay').addEventListener('click', e => {
    if (e.target.id === 'globalSearchOverlay') closeGlobalSearch();
});
function doGlobalSearch(q) {
    clearTimeout(searchTimeout);
    if (!q || q.length < 2) { document.getElementById('globalSearchResults').innerHTML = '<div class="gsr-empty">Type to search...</div>'; return; }
    searchTimeout = setTimeout(async () => {
        try {
            const r = await fetch('/api/search?q=' + encodeURIComponent(q));
            const d = await r.json();
            const c = document.getElementById('globalSearchResults');
            if (!d.results?.length) { c.innerHTML = '<div class="gsr-empty">No results</div>'; return; }
            const icons = {project:'&#128204;', customer:'&#128100;', inventory:'&#128230;'};
            c.innerHTML = d.results.map(r => `<a href="${r.url}" style="text-decoration:none;color:inherit;">
                <div class="gsr-item"><div class="gsr-icon ${r.type}">${icons[r.type]||''}</div>
                <div><div class="gsr-title">${r.title}</div><div class="gsr-sub">${r.subtitle||''}</div></div></div></a>`).join('');
        } catch(e) {}
    }, 300);
}
</script>
</body>
</html>
"""
