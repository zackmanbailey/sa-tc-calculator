"""
TitanForge v4.0 — Work Order Tracking Template (AISC-Compliant)
================================================================
Full work order management page with:
  - 14-status pipeline (queued -> approved -> stickers_printed -> in_fabrication
    -> qc_in_process -> qc_final -> qc_approved_wo -> ncr_hold -> ready_to_ship -> shipped)
  - Per-item QC checklists with pass/fail/n_a
  - NCR (Non-Conformance Report) workflow
  - Heat number / MTR / coil tag traceability
  - Welder IDs, WPS reference, calibration ID
  - Immutable audit trail
  - WO revision handling
  - Paperless mode toggle
  - is_critical flag (columns + rafters)
  - 6-tab detail view: Overview, Items & QC, Traceability, NCRs, Audit Log, Documents
"""

from templates.shared_styles import DESIGN_SYSTEM_CSS

WORK_ORDERS_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TitanForge — Work Orders</title>
<style>
""" + DESIGN_SYSTEM_CSS + r"""

/* ── Work Order Specific Styles ─── */
.wo-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 24px;
    padding-bottom: 80px;
}

.wo-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 24px;
}

.wo-header h1 {
    font-size: 1.5rem;
    font-weight: 700;
    color: #E2E8F0;
    margin: 0;
}

.wo-header .job-badge {
    background: var(--tf-blue);
    color: white;
    padding: 4px 14px;
    border-radius: 6px;
    font-family: 'SF Mono', monospace;
    font-size: 0.9rem;
    margin-left: 12px;
}

.wo-breadcrumb {
    font-size: 0.85rem;
    color: var(--tf-slate);
    margin-bottom: 16px;
}

.wo-breadcrumb a {
    color: var(--tf-blue-mid);
    text-decoration: none;
}

.wo-breadcrumb a:hover {
    text-decoration: underline;
}

/* ── Tabs ─── */
.wo-tabs {
    display: flex;
    gap: 0;
    border-bottom: 2px solid var(--tf-border);
    margin-bottom: 24px;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}

.wo-tab {
    padding: 10px 20px;
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--tf-slate);
    cursor: pointer;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
    transition: all 0.2s;
    background: none;
    border-top: none;
    border-left: none;
    border-right: none;
    white-space: nowrap;
    position: relative;
}

.wo-tab:hover {
    color: var(--tf-blue-mid);
}

.wo-tab.active {
    color: var(--tf-blue);
    border-bottom-color: var(--tf-blue);
}

.wo-tab .tab-badge {
    position: absolute;
    top: 4px;
    right: 4px;
    background: var(--tf-danger);
    color: white;
    font-size: 0.6rem;
    padding: 1px 5px;
    border-radius: 8px;
    font-weight: 700;
    min-width: 16px;
    text-align: center;
}

.wo-tab-content {
    display: none;
}

.wo-tab-content.active {
    display: block;
}

/* ── Pipeline status bar (14-step) ─── */
.status-pipeline {
    display: flex;
    align-items: center;
    gap: 0;
    margin-bottom: 24px;
    background: var(--tf-bg);
    border-radius: 10px;
    padding: 12px 16px;
    border: 1px solid var(--tf-border);
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}

.pipeline-step {
    flex: 1;
    text-align: center;
    padding: 8px 2px;
    font-size: 0.68rem;
    font-weight: 600;
    color: var(--tf-slate);
    position: relative;
    opacity: 0.5;
    transition: all 0.3s;
    min-width: 70px;
}

.pipeline-step.reached {
    opacity: 1;
    color: #E2E8F0;
}

.pipeline-step.current {
    opacity: 1;
    color: var(--tf-blue);
}

.pipeline-step .step-dot {
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: var(--tf-border);
    margin: 0 auto 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.65rem;
    color: white;
    transition: all 0.3s;
}

.pipeline-step.reached .step-dot {
    background: var(--tf-green);
}

.pipeline-step.current .step-dot {
    background: var(--tf-blue);
    box-shadow: 0 0 0 4px rgba(30, 64, 175, 0.15);
}

.pipeline-step.hold .step-dot {
    background: var(--tf-amber);
}

.pipeline-step.ncr .step-dot {
    background: var(--tf-danger);
}

.pipeline-connector {
    width: 20px;
    height: 2px;
    background: var(--tf-border);
    flex-shrink: 0;
}

.pipeline-connector.reached {
    background: var(--tf-green);
}

/* ── Cards ─── */
.wo-card {
    background: #1E293B;
    border: 1px solid var(--tf-border);
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 16px;
    transition: box-shadow 0.2s;
}

.wo-card:hover {
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.wo-card.critical {
    border-left: 3px solid var(--tf-danger);
}

.wo-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
}

.wo-card-header h3 {
    font-size: 1.05rem;
    font-weight: 700;
    margin: 0;
    color: #E2E8F0;
}

/* ── Status badges ─── */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    white-space: nowrap;
}

.status-badge.queued { background: #0F172A; color: #64748B; }
.status-badge.approved { background: #1E3A5F; color: #93C5FD; }
.status-badge.stickers_printed { background: #312E81; color: #A5B4FC; }
.status-badge.in_fabrication { background: #3B2A1A; color: #FBBF24; }
.status-badge.in_progress { background: #3B2A1A; color: #FBBF24; }
.status-badge.qc_in_process { background: #1E3A5F; color: #67E8F9; }
.status-badge.qc_final { background: #164E63; color: #22D3EE; }
.status-badge.qc_approved_wo { background: #0D2818; color: #34D399; }
.status-badge.ncr_hold { background: #3B1A1A; color: #FCA5A5; }
.status-badge.ready_to_ship { background: #1A2E1A; color: #86EFAC; }
.status-badge.shipped { background: #0D2818; color: #10B981; }
.status-badge.on_hold { background: #3B1A1A; color: #FCA5A5; }
.status-badge.complete { background: #0D2818; color: #10B981; }
.status-badge.passed { background: #0D2818; color: #10B981; }
.status-badge.failed { background: #3B1A1A; color: #FCA5A5; }
.status-badge.pending { background: #0F172A; color: #64748B; }

/* ── Paperless mode indicator ─── */
.paperless-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.paperless-badge.on {
    background: #0D3320;
    color: #34D399;
    border: 1px solid #065F46;
}

.paperless-badge.off {
    background: #1E293B;
    color: #94A3B8;
    border: 1px solid var(--tf-border);
}

/* ── Critical badge ─── */
.critical-badge {
    background: var(--tf-danger-bg);
    color: var(--tf-danger);
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}

/* ── Progress bar ─── */
.progress-bar-wrap {
    background: var(--tf-border);
    border-radius: 8px;
    height: 10px;
    overflow: hidden;
    margin: 8px 0;
}

.progress-bar-fill {
    height: 100%;
    border-radius: 8px;
    background: linear-gradient(90deg, var(--tf-blue-mid), var(--tf-green));
    transition: width 0.5s ease;
}

/* ── Items table ─── */
.items-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
}

.items-table th {
    text-align: left;
    padding: 10px 12px;
    font-weight: 600;
    color: var(--tf-slate);
    background: var(--tf-bg);
    border-bottom: 2px solid var(--tf-border);
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    position: sticky;
    top: 0;
    z-index: 1;
}

.items-table td {
    padding: 10px 12px;
    border-bottom: 1px solid var(--tf-border);
    vertical-align: middle;
}

.items-table tr:last-child td {
    border-bottom: none;
}

.items-table tr:hover td {
    background: #0F172A;
}

.items-table tr.critical-row {
    border-left: 3px solid var(--tf-danger);
}

.items-table tr.critical-row td:first-child {
    padding-left: 9px;
}

.ship-mark {
    font-family: 'SF Mono', monospace;
    font-weight: 700;
    color: #E2E8F0;
    font-size: 0.9rem;
}

.component-type-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}

.component-type-badge.column { background: #1E3A5F; color: #93C5FD; }
.component-type-badge.rafter { background: #312E81; color: #A5B4FC; }
.component-type-badge.purlin { background: #0D2818; color: #34D399; }
.component-type-badge.sag_rod { background: #3B2A1A; color: #FBBF24; }
.component-type-badge.strap { background: #831843; color: #F9A8D4; }
.component-type-badge.endcap { background: #3B0764; color: #C4B5FD; }
.component-type-badge.roofing { background: #134E4A; color: #5EEAD4; }

.machine-badge {
    font-family: 'SF Mono', monospace;
    font-size: 0.78rem;
    background: var(--tf-navy);
    color: white;
    padding: 2px 8px;
    border-radius: 4px;
}

.duration-cell {
    font-family: 'SF Mono', monospace;
    font-weight: 600;
}

/* ── QR Scan Panel ─── */
.qr-panel {
    background: linear-gradient(135deg, #1E293B, #0F172A);
    border-radius: 12px;
    padding: 24px;
    color: white;
    margin-bottom: 24px;
}

.qr-panel h3 {
    font-size: 1.1rem;
    margin: 0 0 16px;
    font-weight: 700;
}

.qr-input-row {
    display: flex;
    gap: 12px;
    align-items: center;
}

.qr-input-row input {
    flex: 1;
    padding: 12px 16px;
    border-radius: 8px;
    border: 2px solid rgba(255,255,255,0.2);
    background: rgba(255,255,255,0.1);
    color: white;
    font-size: 1rem;
    font-family: 'SF Mono', monospace;
}

.qr-input-row input::placeholder {
    color: rgba(255,255,255,0.4);
}

.qr-input-row input:focus {
    outline: none;
    border-color: var(--tf-blue-mid);
    background: rgba(255,255,255,0.15);
}

.btn-qr-start {
    padding: 12px 24px;
    border-radius: 8px;
    border: none;
    font-weight: 700;
    font-size: 0.9rem;
    cursor: pointer;
    background: var(--tf-green);
    color: white;
    transition: all 0.2s;
}

.btn-qr-start:hover {
    background: #059669;
    transform: translateY(-1px);
}

.btn-qr-finish {
    padding: 12px 24px;
    border-radius: 8px;
    border: none;
    font-weight: 700;
    font-size: 0.9rem;
    cursor: pointer;
    background: var(--tf-blue-mid);
    color: white;
    transition: all 0.2s;
}

.btn-qr-finish:hover {
    background: #1D4ED8;
    transform: translateY(-1px);
}

.qr-result {
    margin-top: 16px;
    padding: 12px 16px;
    border-radius: 8px;
    font-size: 0.9rem;
    display: none;
}

.qr-result.success {
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.3);
    display: block;
}

.qr-result.error {
    background: rgba(239, 68, 68, 0.15);
    border: 1px solid rgba(239, 68, 68, 0.3);
    display: block;
}

/* ── Metrics row ─── */
.metrics-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}

.metric-card {
    background: #1E293B;
    border: 1px solid var(--tf-border);
    border-radius: 10px;
    padding: 16px;
    text-align: center;
}

.metric-value {
    font-size: 1.8rem;
    font-weight: 800;
    color: #E2E8F0;
    font-family: 'SF Mono', monospace;
}

.metric-label {
    font-size: 0.78rem;
    color: var(--tf-slate);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 4px;
}

/* ── Action buttons ─── */
.wo-actions {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.btn-wo {
    padding: 8px 18px;
    border-radius: 8px;
    border: none;
    font-weight: 600;
    font-size: 0.85rem;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-wo.primary { background: var(--tf-blue); color: white; }
.btn-wo.primary:hover { background: var(--tf-blue-mid); }
.btn-wo.success { background: var(--tf-green); color: white; }
.btn-wo.success:hover { background: #059669; }
.btn-wo.warning { background: var(--tf-amber); color: white; }
.btn-wo.warning:hover { background: #D97706; }
.btn-wo.danger { background: #EF4444; color: white; }
.btn-wo.danger:hover { background: #DC2626; }
.btn-wo.outline { background: #1E293B; color: #E2E8F0; border: 1px solid var(--tf-border); }
.btn-wo.outline:hover { background: var(--tf-bg); }

[id^="fabMenu_"] a:hover { background: var(--tf-bg); }

.btn-wo:disabled { opacity: 0.5; cursor: not-allowed; }

/* ── Item row action buttons ─── */
.item-actions {
    display: flex;
    gap: 6px;
}

.btn-item {
    padding: 4px 10px;
    border-radius: 6px;
    border: none;
    font-size: 0.75rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s;
}

.btn-item.start { background: var(--tf-green); color: white; }
.btn-item.finish { background: var(--tf-blue-mid); color: white; }
.btn-item:disabled { opacity: 0.3; cursor: not-allowed; }

/* ── QC Checklist inline ─── */
.qc-checklist-panel {
    background: rgba(0,0,0,0.3);
    border-radius: 0 0 8px 8px;
    padding: 12px 16px;
}

.qc-check-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    font-size: 0.85rem;
}

.qc-check-item:last-child { border-bottom: none; }

.qc-btn-group {
    display: flex;
    gap: 4px;
    margin-left: auto;
}

.qc-btn {
    padding: 3px 10px;
    border-radius: 4px;
    border: 1px solid var(--tf-border);
    font-size: 0.72rem;
    font-weight: 600;
    cursor: pointer;
    background: transparent;
    color: var(--tf-slate);
    transition: all 0.15s;
}

.qc-btn.pass-active { background: #065F46; color: #34D399; border-color: #065F46; }
.qc-btn.fail-active { background: #991B1B; color: #FCA5A5; border-color: #991B1B; }
.qc-btn.na-active { background: #374151; color: #9CA3AF; border-color: #374151; }

/* ── Fab checklist ─── */
.checklist-panel { background: rgba(0,0,0,0.3); border-radius: 0 0 8px 8px; margin: 0; }
.checklist-step:hover { background: rgba(255,255,255,0.03); }

/* ── Inline editable field ─── */
.inline-edit {
    background: transparent;
    border: 1px solid transparent;
    color: #E2E8F0;
    font-size: 0.82rem;
    padding: 4px 8px;
    border-radius: 4px;
    width: 100%;
    font-family: 'SF Mono', monospace;
    transition: all 0.15s;
}

.inline-edit:hover { border-color: var(--tf-border); }
.inline-edit:focus {
    outline: none;
    border-color: var(--tf-blue-mid);
    background: var(--tf-bg);
}

/* ── NCR Cards ─── */
.ncr-card {
    background: #1E293B;
    border: 1px solid var(--tf-border);
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 12px;
}

.ncr-card.severity-critical { border-left: 3px solid var(--tf-danger); }
.ncr-card.severity-major { border-left: 3px solid var(--tf-amber); }
.ncr-card.severity-minor { border-left: 3px solid var(--tf-info); }

.ncr-status-badge {
    display: inline-flex;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.72rem;
    font-weight: 600;
}

.ncr-status-badge.open { background: #3B1A1A; color: #FCA5A5; }
.ncr-status-badge.in_review { background: #3B2A1A; color: #FBBF24; }
.ncr-status-badge.resolved { background: #0D2818; color: #34D399; }
.ncr-status-badge.closed { background: #1E293B; color: #64748B; }

/* ── Audit timeline ─── */
.audit-timeline {
    position: relative;
    padding-left: 24px;
}

.audit-timeline::before {
    content: '';
    position: absolute;
    left: 8px;
    top: 0;
    bottom: 0;
    width: 2px;
    background: var(--tf-border);
}

.audit-entry {
    position: relative;
    padding: 12px 0 12px 16px;
    border-bottom: 1px solid rgba(255,255,255,0.03);
}

.audit-entry::before {
    content: '';
    position: absolute;
    left: -20px;
    top: 18px;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: var(--tf-blue-mid);
    border: 2px solid var(--tf-bg);
}

.audit-entry .audit-time {
    font-size: 0.72rem;
    color: var(--tf-slate);
    font-family: 'SF Mono', monospace;
}

.audit-entry .audit-action {
    font-size: 0.85rem;
    color: #E2E8F0;
    margin: 2px 0;
}

.audit-entry .audit-detail {
    font-size: 0.78rem;
    color: var(--tf-slate);
}

.audit-entry .audit-diff {
    margin-top: 6px;
    padding: 6px 10px;
    background: var(--tf-bg);
    border-radius: 6px;
    font-size: 0.75rem;
    font-family: 'SF Mono', monospace;
}

.audit-diff .diff-old { color: #FCA5A5; }
.audit-diff .diff-new { color: #34D399; }

/* ── Filter bar ─── */
.filter-bar {
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
    flex-wrap: wrap;
    align-items: center;
}

.filter-btn {
    padding: 6px 14px;
    border-radius: 20px;
    border: 1px solid var(--tf-border);
    background: transparent;
    color: var(--tf-slate);
    font-size: 0.78rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s;
}

.filter-btn:hover { border-color: var(--tf-blue-mid); color: var(--tf-blue-mid); }
.filter-btn.active { background: var(--tf-blue); border-color: var(--tf-blue); color: white; }

/* ── Empty state ─── */
.empty-state {
    text-align: center;
    padding: 60px 20px;
    color: var(--tf-slate);
}

.empty-state .empty-icon {
    font-size: 3rem;
    margin-bottom: 12px;
    opacity: 0.4;
}

.empty-state h3 {
    font-size: 1.1rem;
    margin: 0 0 8px;
    color: #E2E8F0;
}

.empty-state p {
    font-size: 0.9rem;
    margin: 0 0 20px;
}

/* ── Toast notification ─── */
.toast {
    position: fixed;
    bottom: 80px;
    right: 24px;
    padding: 14px 24px;
    border-radius: 10px;
    font-weight: 600;
    font-size: 0.9rem;
    z-index: 9999;
    transform: translateY(100px);
    opacity: 0;
    transition: all 0.3s;
    max-width: 400px;
}

.toast.show { transform: translateY(0); opacity: 1; }
.toast.success { background: #065F46; color: white; }
.toast.error { background: #991B1B; color: white; }
.toast.info { background: var(--tf-blue); color: white; }

/* ── Modal overlay ─── */
.modal-overlay {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.6);
    z-index: 5000;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.2s;
}

.modal-overlay.active { opacity: 1; pointer-events: all; }

.modal-content {
    background: #1E293B;
    border: 1px solid var(--tf-border);
    border-radius: 12px;
    padding: 24px;
    max-width: 600px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
}

.modal-content h3 {
    color: #E2E8F0;
    margin: 0 0 16px;
    font-size: 1.1rem;
}

.modal-content label {
    display: block;
    font-size: 0.82rem;
    color: var(--tf-slate);
    margin-bottom: 4px;
    font-weight: 600;
}

.modal-content input,
.modal-content select,
.modal-content textarea {
    width: 100%;
    padding: 8px 12px;
    border-radius: 6px;
    border: 1px solid var(--tf-border);
    background: var(--tf-bg);
    color: #E2E8F0;
    font-size: 0.85rem;
    margin-bottom: 12px;
    font-family: inherit;
}

.modal-content textarea { min-height: 80px; resize: vertical; }
.modal-content input:focus,
.modal-content select:focus,
.modal-content textarea:focus {
    outline: none;
    border-color: var(--tf-blue-mid);
}

.modal-actions {
    display: flex;
    gap: 10px;
    justify-content: flex-end;
    margin-top: 16px;
}

/* ── Traceability % indicator ─── */
.trace-pct-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
}

.trace-pct-fill {
    flex: 1;
    height: 8px;
    border-radius: 4px;
    background: var(--tf-border);
    overflow: hidden;
}

.trace-pct-fill-inner {
    height: 100%;
    border-radius: 4px;
    background: linear-gradient(90deg, var(--tf-blue-mid), var(--tf-green));
    transition: width 0.5s ease;
}

/* ── Mobile bottom action bar ─── */
.mobile-action-bar {
    display: none;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #1E293B;
    border-top: 1px solid var(--tf-border);
    padding: 8px 16px;
    z-index: 4000;
    gap: 8px;
    justify-content: space-around;
}

.mobile-action-bar button {
    flex: 1;
    padding: 10px 8px;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.78rem;
    cursor: pointer;
    color: white;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    background: transparent;
}

.mobile-action-bar button .bar-icon { font-size: 1.2rem; }
.mobile-action-bar button.active { color: var(--tf-blue); }

/* ── Revision badge ─── */
.revision-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: #312E81;
    color: #A5B4FC;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.72rem;
    font-weight: 600;
    font-family: 'SF Mono', monospace;
}

/* ── Responsive ─── */
@media (max-width: 768px) {
    .wo-container { padding: 12px; padding-bottom: 80px; }
    .metrics-row { grid-template-columns: repeat(2, 1fr); }
    .wo-header { flex-wrap: wrap; gap: 8px; }
    .qr-input-row { flex-direction: column; }
    .items-table { font-size: 0.78rem; }
    .items-table th, .items-table td { padding: 6px 8px; }
    .status-pipeline { padding: 8px; }
    .pipeline-step { font-size: 0.6rem; min-width: 55px; padding: 6px 1px; }
    .pipeline-step .step-dot { width: 18px; height: 18px; font-size: 0.55rem; }
    .pipeline-connector { width: 12px; }
    .wo-tabs { gap: 0; }
    .wo-tab { padding: 8px 12px; font-size: 0.8rem; }
    .mobile-action-bar { display: flex; }
    .filter-bar { gap: 4px; }
    .filter-btn { padding: 4px 10px; font-size: 0.72rem; }
}

@media (max-width: 480px) {
    .metrics-row { grid-template-columns: 1fr 1fr; gap: 8px; }
    .metric-value { font-size: 1.3rem; }
    .metric-card { padding: 10px; }
    .wo-header h1 { font-size: 1.2rem; }
}
</style>
</head>
<body>

<div class="wo-container">

    <!-- Breadcrumb -->
    <div class="wo-breadcrumb" style="display:flex;justify-content:space-between;align-items:center;">
        <div>
            <a href="/">Dashboard</a> &nbsp;/&nbsp;
            <a href="/project/{{JOB_CODE}}">{{JOB_CODE}}</a> &nbsp;/&nbsp;
            <a href="/shop-drawings/{{JOB_CODE}}">Shop Drawings</a> &nbsp;/&nbsp;
            <strong>Work Orders</strong>
        </div>
        <div style="display:flex;gap:12px;align-items:center;">
            <span id="paperless-indicator"></span>
            <a href="/shop-floor" style="color:var(--tf-blue);font-size:0.85rem;text-decoration:none;display:flex;align-items:center;gap:4px;">&#9881; Shop Floor Dashboard</a>
        </div>
    </div>

    <!-- Header -->
    <div class="wo-header">
        <div style="display:flex;align-items:center;">
            <h1>Work Orders</h1>
            <span class="job-badge">{{JOB_CODE}}</span>
        </div>
        <div class="wo-actions">
            <button class="btn-wo primary" onclick="createWorkOrder()">+ New Work Order</button>
            <a href="/work-station/{{JOB_CODE}}" class="btn-wo outline" style="text-decoration:none;display:inline-flex;align-items:center;gap:4px;">&#128241; Work Station</a>
            <button class="btn-wo outline" onclick="refreshAll()">Refresh</button>
        </div>
    </div>

    <!-- WO List area -->
    <div id="wo-list-area">
        <div class="empty-state" id="empty-state">
            <div class="empty-icon">&#128203;</div>
            <h3>No Work Orders Yet</h3>
            <p>Generate shop drawings first, then create a work order to track fabrication.</p>
            <button class="btn-wo primary" onclick="createWorkOrder()">Create Work Order</button>
        </div>
    </div>

    <!-- Detail area (shown when WO selected) -->
    <div id="wo-detail-area" style="display:none;">
        <!-- Back button -->
        <div style="margin-bottom:16px;">
            <button class="btn-wo outline" onclick="backToList()" style="font-size:0.82rem;">&#8592; Back to WO List</button>
        </div>

        <!-- WO Header info -->
        <div id="wo-detail-header"></div>

        <!-- 6-Tab navigation -->
        <div class="wo-tabs" id="detail-tabs">
            <button class="wo-tab active" data-tab="overview" onclick="switchDetailTab('overview')">Overview</button>
            <button class="wo-tab" data-tab="items-qc" onclick="switchDetailTab('items-qc')">Items &amp; QC</button>
            <button class="wo-tab" data-tab="traceability" onclick="switchDetailTab('traceability')">Traceability</button>
            <button class="wo-tab" data-tab="ncrs" onclick="switchDetailTab('ncrs')">NCRs <span class="tab-badge" id="ncr-count-badge" style="display:none;">0</span></button>
            <button class="wo-tab" data-tab="audit" onclick="switchDetailTab('audit')">Audit Log</button>
            <button class="wo-tab" data-tab="documents" onclick="switchDetailTab('documents')">Documents</button>
        </div>

        <!-- Tab 1: Overview -->
        <div class="wo-tab-content active" id="tab-overview">
            <div id="overview-content"></div>
        </div>

        <!-- Tab 2: Items & QC -->
        <div class="wo-tab-content" id="tab-items-qc">
            <div id="items-qc-content"></div>
        </div>

        <!-- Tab 3: Traceability -->
        <div class="wo-tab-content" id="tab-traceability">
            <div id="traceability-content"></div>
        </div>

        <!-- Tab 4: NCRs -->
        <div class="wo-tab-content" id="tab-ncrs">
            <div id="ncrs-content"></div>
        </div>

        <!-- Tab 5: Audit Log -->
        <div class="wo-tab-content" id="tab-audit">
            <div id="audit-content"></div>
        </div>

        <!-- Tab 6: Documents -->
        <div class="wo-tab-content" id="tab-documents">
            <div id="documents-content"></div>
        </div>
    </div>
</div>

<!-- Modal overlay -->
<div class="modal-overlay" id="modal-overlay" onclick="if(event.target===this)closeModal()">
    <div class="modal-content" id="modal-content"></div>
</div>

<!-- Toast -->
<div class="toast" id="toast"></div>

<!-- Mobile bottom action bar -->
<div class="mobile-action-bar" id="mobile-bar">
    <button onclick="switchDetailTab('overview')" class="active" data-mtab="overview">
        <span class="bar-icon">&#128200;</span>
        <span>Overview</span>
    </button>
    <button onclick="switchDetailTab('items-qc')" data-mtab="items-qc">
        <span class="bar-icon">&#128295;</span>
        <span>Items</span>
    </button>
    <button onclick="switchDetailTab('traceability')" data-mtab="traceability">
        <span class="bar-icon">&#128279;</span>
        <span>Trace</span>
    </button>
    <button onclick="switchDetailTab('ncrs')" data-mtab="ncrs">
        <span class="bar-icon">&#9888;</span>
        <span>NCRs</span>
    </button>
    <button onclick="switchDetailTab('audit')" data-mtab="audit">
        <span class="bar-icon">&#128220;</span>
        <span>Audit</span>
    </button>
    <button onclick="switchDetailTab('documents')" data-mtab="documents">
        <span class="bar-icon">&#128196;</span>
        <span>Docs</span>
    </button>
</div>

<script>
const JOB_CODE = '{{JOB_CODE}}';
let workOrders = [];
let currentWO = null;
let scanHistory = [];
let currentItemFilter = 'all';
let auditLog = [];
let ncrList = [];
let traceData = {};
let qcChecklists = {};
let paperlessMode = false;

// ── 14-Status Pipeline Configuration ──
const PIPELINE_STEPS = [
    'queued', 'approved', 'stickers_printed', 'in_fabrication',
    'qc_in_process', 'qc_final', 'qc_approved_wo',
    'ncr_hold', 'ready_to_ship', 'shipped'
];

const PIPELINE_LABELS = {
    'queued': 'Queued',
    'approved': 'Approved',
    'stickers_printed': 'Stickers Printed',
    'in_fabrication': 'In Fabrication',
    'qc_in_process': 'QC In Process',
    'qc_final': 'QC Final',
    'qc_approved_wo': 'QC Approved',
    'ncr_hold': 'NCR Hold',
    'ready_to_ship': 'Ready to Ship',
    'shipped': 'Shipped'
};

const ON_HOLD_ALIASES = ['on_hold', 'ncr_hold'];

// ── INIT ──
document.addEventListener('DOMContentLoaded', () => {
    refreshAll();
});

async function refreshAll() {
    await loadWorkOrders();
    renderWOList();
    if (currentWO) {
        await loadWODetail(currentWO.work_order_id, true);
    }
}

// ── API Helpers ──
async function apiCall(url, method, body) {
    const opts = { method, headers: {'Content-Type': 'application/json'} };
    if (body) opts.body = JSON.stringify(body);
    try {
        const resp = await fetch(url, opts);
        if (!resp.ok) {
            const text = await resp.text();
            try { return JSON.parse(text); } catch(e) {}
            return { ok: false, error: 'Server error ' + resp.status + ': ' + text.substring(0, 200) };
        }
        return resp.json();
    } catch(err) {
        return { ok: false, error: 'Network error: ' + err.message };
    }
}

// ── Data Loading ──
async function loadWorkOrders() {
    const data = await apiCall('/api/work-orders/list?job_code=' + JOB_CODE, 'GET');
    if (data.ok) {
        workOrders = data.work_orders || [];
    }
}

async function loadWODetail(woId, silent) {
    const data = await apiCall('/api/work-orders/detail?job_code=' + JOB_CODE + '&wo_id=' + woId, 'GET');
    if (data.ok) {
        currentWO = data.work_order;
        showDetailView();
        renderAllDetailTabs();
        if (!silent) switchDetailTab('overview');
    } else {
        showToast(data.error || 'Failed to load work order', 'error');
    }
}

async function loadAuditLog() {
    if (!currentWO) return;
    const data = await apiCall('/api/work-orders/audit-log?job_code=' + JOB_CODE + '&wo_id=' + currentWO.work_order_id, 'GET');
    if (data.ok) {
        auditLog = data.entries || data.audit_log || [];
    }
}

async function loadNCRs() {
    if (!currentWO) return;
    const data = await apiCall('/api/work-orders/ncr?job_code=' + JOB_CODE + '&wo_id=' + currentWO.work_order_id, 'GET');
    if (data.ok) {
        ncrList = data.ncrs || [];
        updateNCRBadge();
    }
}

async function loadTraceability() {
    if (!currentWO) return;
    const data = await apiCall('/api/work-orders/traceability?job_code=' + JOB_CODE + '&wo_id=' + currentWO.work_order_id, 'GET');
    if (data.ok) {
        traceData = data;
    }
}

function updateNCRBadge() {
    const badge = document.getElementById('ncr-count-badge');
    const openCount = ncrList.filter(function(n) { return n.status === 'open' || n.status === 'in_review'; }).length;
    if (openCount > 0) {
        badge.style.display = 'inline';
        badge.textContent = openCount;
    } else {
        badge.style.display = 'none';
    }
}

// ── View Switching ──
function showDetailView() {
    document.getElementById('wo-list-area').style.display = 'none';
    document.getElementById('wo-detail-area').style.display = 'block';
    document.getElementById('mobile-bar').style.display = 'flex';
}

function backToList() {
    document.getElementById('wo-list-area').style.display = 'block';
    document.getElementById('wo-detail-area').style.display = 'none';
    document.getElementById('mobile-bar').style.display = 'none';
    currentWO = null;
    renderWOList();
}

function switchDetailTab(tab) {
    document.querySelectorAll('#detail-tabs .wo-tab').forEach(function(t) {
        t.classList.toggle('active', t.dataset.tab === tab);
    });
    document.querySelectorAll('#wo-detail-area .wo-tab-content').forEach(function(c) {
        c.classList.toggle('active', c.id === 'tab-' + tab);
    });
    // Mobile bar
    document.querySelectorAll('.mobile-action-bar button').forEach(function(b) {
        b.classList.toggle('active', b.dataset.mtab === tab);
    });
    // Lazy load data for certain tabs
    if (tab === 'audit') { loadAuditLog().then(renderAuditTab); }
    if (tab === 'ncrs') { loadNCRs().then(renderNCRsTab); }
    if (tab === 'traceability') { loadTraceability().then(renderTraceabilityTab); }
}

// ── WO List Render ──
function renderWOList() {
    var area = document.getElementById('wo-list-area');
    if (workOrders.length === 0) {
        area.innerHTML = '<div class="empty-state">' +
            '<div class="empty-icon">&#128203;</div>' +
            '<h3>No Work Orders Yet</h3>' +
            '<p>Generate shop drawings first, then create a work order to track fabrication.</p>' +
            '<button class="btn-wo primary" onclick="createWorkOrder()">Create Work Order</button>' +
            '</div>';
        return;
    }

    var html = '';
    workOrders.forEach(function(wo) {
        var statusClass = (wo.status || '').replace(/ /g, '_');
        var label = PIPELINE_LABELS[wo.status] || wo.status_label || wo.status;
        var pct = wo.progress_pct || 0;
        var priorityTag = '';
        if (wo.priority && wo.priority !== 'normal') {
            priorityTag = ' <span style="color:var(--tf-danger);font-weight:700;font-size:0.75rem;">' + wo.priority.toUpperCase() + '</span>';
        }
        var revBadge = wo.revision > 1 ? ' <span class="revision-badge">Rev ' + wo.revision + '</span>' : '';
        html += '<div class="wo-card" style="cursor:pointer" onclick="loadWODetail(\'' + wo.work_order_id + '\')">' +
            '<div class="wo-card-header">' +
                '<h3 style="font-family:\'SF Mono\',monospace;">' + wo.work_order_id + revBadge + '</h3>' +
                '<div style="display:flex;gap:8px;align-items:center;">' + priorityTag +
                    '<span class="status-badge ' + statusClass + '">' + label + '</span>' +
                '</div>' +
            '</div>' +
            '<div style="display:flex;gap:24px;font-size:0.85rem;color:var(--tf-slate);margin-bottom:10px;flex-wrap:wrap;">' +
                '<span>Rev: <strong>' + wo.revision + '</strong></span>' +
                '<span>Created: ' + new Date(wo.created_at).toLocaleDateString() + '</span>' +
                '<span>Items: <strong>' + (wo.completed_items || 0) + '/' + (wo.total_items || 0) + '</strong></span>' +
                (wo.total_fab_minutes > 0 ? '<span>Fab Time: <strong>' + wo.total_fab_minutes + ' min</strong></span>' : '') +
                (wo.purchased_items > 0 ? '<span>Purchased: <strong>' + (wo.purchased_picked || 0) + '/' + wo.purchased_items + '</strong> picked</span>' : '') +
                (wo.purchased_cost > 0 ? '<span style="color:var(--tf-amber);">Hardware: <strong>$' + wo.purchased_cost.toFixed(2) + '</strong></span>' : '') +
            '</div>' +
            '<div class="progress-bar-wrap">' +
                '<div class="progress-bar-fill" style="width:' + pct + '%"></div>' +
            '</div>' +
            '<div style="font-size:0.78rem;color:var(--tf-slate);text-align:right;">' + pct + '% complete</div>' +
        '</div>';
    });
    area.innerHTML = html;
}

// ── Render All Detail Tabs ──
function renderAllDetailTabs() {
    if (!currentWO) return;
    renderDetailHeader();
    renderOverviewTab();
    renderItemsQCTab();
    renderDocumentsTab();
    // NCRs, Audit, Traceability loaded on demand
}

// ── Detail Header ──
function renderDetailHeader() {
    var wo = currentWO;
    var isOnHold = ON_HOLD_ALIASES.indexOf(wo.status) !== -1;
    var statusClass = (wo.status || '').replace(/ /g, '_');
    var label = PIPELINE_LABELS[wo.status] || wo.status;

    var html = '<div class="wo-card-header" style="margin-bottom:16px;">' +
        '<div>' +
            '<h3 style="font-family:\'SF Mono\',monospace;font-size:1.1rem;">' + wo.work_order_id + '</h3>' +
            '<div style="font-size:0.82rem;color:var(--tf-slate);margin-top:4px;">' +
                'Rev ' + wo.revision + ' &bull; Created ' + new Date(wo.created_at).toLocaleString() +
                (wo.approved_by ? ' &bull; Approved by ' + wo.approved_by : '') +
                (wo.project_name ? ' &bull; ' + wo.project_name : '') +
                (wo.customer_name ? ' &mdash; ' + wo.customer_name : '') +
            '</div>' +
            (wo.building_specs ? '<div style="font-size:0.8rem;color:var(--tf-blue);margin-top:2px;font-weight:600;">' + wo.building_specs + '</div>' : '') +
        '</div>' +
        '<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">' +
            (isOnHold ? '<span class="status-badge on_hold">ON HOLD</span>' : '<span class="status-badge ' + statusClass + '">' + label + '</span>') +
            (wo.revision > 1 ? '<span class="revision-badge">Rev ' + wo.revision + '</span>' : '') +
        '</div>' +
    '</div>';
    document.getElementById('wo-detail-header').innerHTML = html;
}

// ── Tab 1: Overview ──
function renderOverviewTab() {
    var wo = currentWO;
    var items = wo.items || [];
    var statusClass = (wo.status || '').replace(/ /g, '_');
    var isOnHold = ON_HOLD_ALIASES.indexOf(wo.status) !== -1;

    // Pipeline
    var pipelineHtml = buildPipeline(wo.status);

    // Metrics
    var completedItems = items.filter(function(i) { return i.status === 'complete' || i.status === 'shipped' || i.status === 'ready_to_ship' || i.status === 'qc_approved_wo'; }).length;
    var inProgressItems = items.filter(function(i) { return i.status === 'in_progress' || i.status === 'in_fabrication'; }).length;
    var qcPending = items.filter(function(i) { return i.qc_status === 'pending' || !i.qc_status; }).length;
    var criticalItems = items.filter(function(i) { return i.is_critical; }).length;
    var totalFabMin = items.reduce(function(s, i) { return s + (i.duration_minutes || 0); }, 0);
    var totalEstimated = items.reduce(function(s, i) { return s + (i.estimated_minutes || 0); }, 0);
    var pct = items.length > 0 ? Math.round(100 * completedItems / items.length) : 0;
    var totalWeight = items.reduce(function(s, i) { return s + (i.weight || 0); }, 0);

    // Paperless mode
    var plBadge = paperlessMode
        ? '<span class="paperless-badge on">&#9889; Paperless Mode</span>'
        : '<span class="paperless-badge off">&#128196; Paper Mode</span>';

    // Action buttons
    var actionsHtml = buildActionButtons(wo);

    var html = pipelineHtml +
        '<div style="display:flex;gap:8px;align-items:center;margin-bottom:16px;flex-wrap:wrap;">' +
            plBadge +
            (wo.priority && wo.priority !== 'normal' ? '<span class="critical-badge">' + wo.priority.toUpperCase() + ' PRIORITY</span>' : '') +
            (wo.due_date ? '<span style="font-size:0.82rem;color:var(--tf-slate);">Due: <strong>' + wo.due_date + '</strong></span>' : '') +
            (wo.delivery_date ? '<span style="font-size:0.82rem;color:var(--tf-slate);">Delivery: <strong>' + wo.delivery_date + '</strong></span>' : '') +
        '</div>' +
        '<div class="metrics-row">' +
            '<div class="metric-card">' +
                '<div class="metric-value">' + items.length + '</div>' +
                '<div class="metric-label">Total Items</div>' +
            '</div>' +
            '<div class="metric-card">' +
                '<div class="metric-value">' + completedItems + '</div>' +
                '<div class="metric-label">Completed</div>' +
            '</div>' +
            '<div class="metric-card">' +
                '<div class="metric-value">' + inProgressItems + '</div>' +
                '<div class="metric-label">In Progress</div>' +
            '</div>' +
            '<div class="metric-card">' +
                '<div class="metric-value">' + pct + '%</div>' +
                '<div class="metric-label">Progress</div>' +
            '</div>' +
            '<div class="metric-card">' +
                '<div class="metric-value">' + (totalFabMin > 0 ? totalFabMin.toFixed(1) : '—') + '</div>' +
                '<div class="metric-label">Actual Min</div>' +
            '</div>' +
            '<div class="metric-card">' +
                '<div class="metric-value">' + (totalEstimated > 0 ? totalEstimated.toFixed(0) : '—') + '</div>' +
                '<div class="metric-label">Est. Min</div>' +
            '</div>' +
            '<div class="metric-card">' +
                '<div class="metric-value">' + qcPending + '</div>' +
                '<div class="metric-label">QC Pending</div>' +
            '</div>' +
            (criticalItems > 0 ? '<div class="metric-card" style="border-color:var(--tf-danger);">' +
                '<div class="metric-value" style="color:var(--tf-danger);">' + criticalItems + '</div>' +
                '<div class="metric-label">Critical Items</div>' +
            '</div>' : '') +
            (totalWeight > 0 ? '<div class="metric-card">' +
                '<div class="metric-value">' + totalWeight.toFixed(0) + '</div>' +
                '<div class="metric-label">Total Lbs</div>' +
            '</div>' : '') +
        '</div>' +
        '<div class="progress-bar-wrap" style="height:14px;margin-bottom:24px;">' +
            '<div class="progress-bar-fill" style="width:' + pct + '%"></div>' +
        '</div>' +
        '<div class="wo-card">' +
            '<div class="wo-card-header">' +
                '<h3>Quick Actions</h3>' +
            '</div>' +
            '<div class="wo-actions" style="flex-wrap:wrap;">' + actionsHtml + '</div>' +
        '</div>' +
        (wo.notes ? '<div class="wo-card"><div class="wo-card-header"><h3>Notes</h3></div><p style="color:var(--tf-slate);font-size:0.85rem;">' + wo.notes + '</p></div>' : '') +
        '<div class="wo-card">' +
            '<div class="wo-card-header"><h3>QR Scanner</h3></div>' +
            '<div class="qr-input-row">' +
                '<input type="text" id="qr-input" placeholder="Scan or type item ID" onkeydown="if(event.key===\'Enter\')processQRScan()">' +
                '<button class="btn-qr-start" onclick="processQRScan(\'start\')">Start</button>' +
                '<button class="btn-qr-finish" onclick="processQRScan(\'finish\')">Finish</button>' +
            '</div>' +
            '<div class="qr-result" id="qr-result"></div>' +
            '<div style="margin-top:12px;padding:12px;background:rgba(0,0,0,0.2);border-radius:8px;">' +
                '<h4 style="color:var(--tf-amber);margin:0 0 8px;font-size:0.85rem;">Batch Scan by Group</h4>' +
                '<div style="display:flex;gap:6px;flex-wrap:wrap;">' +
                    '<button class="btn-qr-start" style="padding:8px 14px;font-size:0.78rem;" onclick="batchScan(\'PG\',\'start\')">Start Purlins</button>' +
                    '<button class="btn-qr-finish" style="padding:8px 14px;font-size:0.78rem;" onclick="batchScan(\'PG\',\'finish\')">Finish Purlins</button>' +
                    '<button class="btn-qr-start" style="padding:8px 14px;font-size:0.78rem;" onclick="batchScan(\'SR\',\'start\')">Start Sag Rods</button>' +
                    '<button class="btn-qr-finish" style="padding:8px 14px;font-size:0.78rem;" onclick="batchScan(\'SR\',\'finish\')">Finish Sag Rods</button>' +
                    '<button class="btn-qr-start" style="padding:8px 14px;font-size:0.78rem;" onclick="batchScan(\'HS\',\'start\')">Start Straps</button>' +
                    '<button class="btn-qr-finish" style="padding:8px 14px;font-size:0.78rem;" onclick="batchScan(\'HS\',\'finish\')">Finish Straps</button>' +
                    '<button class="btn-qr-start" style="padding:8px 14px;font-size:0.78rem;" onclick="batchScan(\'EC\',\'start\')">Start Endcaps</button>' +
                    '<button class="btn-qr-finish" style="padding:8px 14px;font-size:0.78rem;" onclick="batchScan(\'EC\',\'finish\')">Finish Endcaps</button>' +
                '</div>' +
            '</div>' +
        '</div>';

    document.getElementById('overview-content').innerHTML = html;
}

// ── Pipeline Builder ──
function buildPipeline(currentStatus) {
    var isOnHold = ON_HOLD_ALIASES.indexOf(currentStatus) !== -1;
    var isNCR = currentStatus === 'ncr_hold';
    var currentIdx = PIPELINE_STEPS.indexOf(currentStatus);
    // Map on_hold to show where we are
    if (currentStatus === 'on_hold') currentIdx = -1;

    var html = '<div class="status-pipeline">';
    PIPELINE_STEPS.forEach(function(step, i) {
        var cls = '';
        if (isOnHold && !isNCR) {
            cls = 'hold';
        } else if (step === 'ncr_hold' && isNCR) {
            cls = 'ncr current';
        } else if (i < currentIdx) {
            cls = 'reached';
        } else if (i === currentIdx) {
            cls = 'current';
        }

        if (i > 0) {
            html += '<div class="pipeline-connector ' + (i <= currentIdx && !isOnHold ? 'reached' : '') + '"></div>';
        }
        var icon = (i < currentIdx && !isOnHold) ? '&#10003;' : (i + 1);
        if (step === 'ncr_hold') icon = '!';
        html += '<div class="pipeline-step ' + cls + '">' +
            '<div class="step-dot">' + icon + '</div>' +
            PIPELINE_LABELS[step] +
        '</div>';
    });
    html += '</div>';
    return html;
}

// ── Action Buttons Builder ──
function buildActionButtons(wo) {
    var stickerBtns = '';
    if (wo.status !== 'queued') {
        stickerBtns = '<div class="btn-group" style="display:inline-flex;gap:0;border:1px solid var(--tf-border);border-radius:8px;overflow:hidden;">' +
            '<button class="btn-wo outline" style="border:none;border-radius:0;border-right:1px solid var(--tf-border);" onclick="printStickers(\'' + wo.work_order_id + '\',\'pdf\')">WO Stickers</button>' +
            '<button class="btn-wo outline" style="border:none;border-radius:0;border-right:1px solid var(--tf-border);" onclick="printStickers(\'' + wo.work_order_id + '\',\'zpl\')">ZPL</button>' +
            '<button class="btn-wo outline" style="border:none;border-radius:0;" onclick="printStickers(\'' + wo.work_order_id + '\',\'csv\')">CSV</button>' +
        '</div>' +
        '<div style="position:relative;display:inline-block;margin-left:6px;">' +
            '<button class="btn-wo outline" onclick="toggleFabMenu(\'' + wo.work_order_id + '\')">&#127991; Fab Stickers &#9662;</button>' +
            '<div id="fabMenu_' + wo.work_order_id + '" style="display:none;position:absolute;top:100%;left:0;z-index:999;background:var(--tf-bg);border:1px solid var(--tf-border);border-radius:8px;box-shadow:0 4px 16px rgba(0,0,0,0.15);min-width:220px;padding:6px 0;margin-top:4px;">' +
                '<div style="padding:4px 12px;font-size:11px;color:var(--tf-slate);font-weight:600;">ASSEMBLY STICKERS</div>' +
                '<a href="#" onclick="fabSticker(\'' + wo.work_order_id + '\',\'assembly-pdf\');return false;" style="display:block;padding:6px 12px;color:#E2E8F0;text-decoration:none;">&#128196; Assembly PDF</a>' +
                '<a href="#" onclick="fabSticker(\'' + wo.work_order_id + '\',\'assembly-zpl\');return false;" style="display:block;padding:6px 12px;color:#E2E8F0;text-decoration:none;">&#9000; Assembly ZPL</a>' +
                '<div style="border-top:1px solid var(--tf-border);margin:4px 0;"></div>' +
                '<div style="padding:4px 12px;font-size:11px;color:var(--tf-slate);font-weight:600;">MATERIAL STICKERS</div>' +
                '<a href="#" onclick="fabSticker(\'' + wo.work_order_id + '\',\'material-master-pdf\');return false;" style="display:block;padding:6px 12px;color:#E2E8F0;text-decoration:none;">&#128196; Material Master PDF</a>' +
                '<a href="#" onclick="fabSticker(\'' + wo.work_order_id + '\',\'material-master-zpl\');return false;" style="display:block;padding:6px 12px;color:#E2E8F0;text-decoration:none;">&#9000; Material Master ZPL</a>' +
                '<a href="#" onclick="fabSticker(\'' + wo.work_order_id + '\',\'material-sub-pdf\');return false;" style="display:block;padding:6px 12px;color:#E2E8F0;text-decoration:none;">&#128196; Material Sub PDF</a>' +
                '<a href="#" onclick="fabSticker(\'' + wo.work_order_id + '\',\'material-sub-zpl\');return false;" style="display:block;padding:6px 12px;color:#E2E8F0;text-decoration:none;">&#9000; Material Sub ZPL</a>' +
                '<div style="border-top:1px solid var(--tf-border);margin:4px 0;"></div>' +
                '<div style="padding:4px 12px;font-size:11px;color:var(--tf-slate);font-weight:600;">NICELABEL / CSV</div>' +
                '<a href="#" onclick="fabSticker(\'' + wo.work_order_id + '\',\'nlbl/assembly\');return false;" style="display:block;padding:6px 12px;color:#E2E8F0;text-decoration:none;">&#128196; Assembly NLBL</a>' +
                '<a href="#" onclick="fabSticker(\'' + wo.work_order_id + '\',\'nlbl/material\');return false;" style="display:block;padding:6px 12px;color:#E2E8F0;text-decoration:none;">&#128196; Material NLBL</a>' +
                '<a href="#" onclick="fabSticker(\'' + wo.work_order_id + '\',\'csv/assembly\');return false;" style="display:block;padding:6px 12px;color:#E2E8F0;text-decoration:none;">&#128462; Assembly CSV</a>' +
                '<a href="#" onclick="fabSticker(\'' + wo.work_order_id + '\',\'csv/material\');return false;" style="display:block;padding:6px 12px;color:#E2E8F0;text-decoration:none;">&#128462; Material CSV</a>' +
            '</div>' +
        '</div>' +
        '<button class="btn-wo outline" onclick="downloadPacketPDF(\'' + wo.work_order_id + '\')" style="margin-left:6px;">&#128196; Packet PDF</button>';
    }

    var html = '';
    var s = wo.status;
    if (s === 'queued') {
        html = '<button class="btn-wo success" onclick="approveWO(\'' + wo.work_order_id + '\')">&#10003; Approve</button>' +
               '<button class="btn-wo warning" onclick="holdWO(\'' + wo.work_order_id + '\',\'hold\')">Hold</button>';
    } else if (s === 'approved') {
        html = stickerBtns +
               '<button class="btn-wo primary" onclick="printAndMark(\'' + wo.work_order_id + '\')">Print Stickers &amp; Mark</button>' +
               '<button class="btn-wo warning" onclick="holdWO(\'' + wo.work_order_id + '\',\'hold\')">Hold</button>';
    } else if (s === 'on_hold') {
        html = '<button class="btn-wo success" onclick="holdWO(\'' + wo.work_order_id + '\',\'resume\')">Resume</button>';
    } else if (s === 'ncr_hold') {
        html = '<button class="btn-wo warning" onclick="switchDetailTab(\'ncrs\')">View NCRs</button>' +
               '<button class="btn-wo success" onclick="holdWO(\'' + wo.work_order_id + '\',\'resume\')">Resume</button>';
    } else if (s === 'stickers_printed' || s === 'in_fabrication' || s === 'in_progress') {
        html = stickerBtns +
               '<button class="btn-wo warning" onclick="holdWO(\'' + wo.work_order_id + '\',\'hold\')">Hold</button>';
    } else if (s === 'qc_in_process' || s === 'qc_final') {
        html = stickerBtns +
               '<button class="btn-wo primary" onclick="switchDetailTab(\'items-qc\')">QC Items</button>';
    } else if (s === 'qc_approved_wo') {
        html = stickerBtns +
               '<button class="btn-wo success" onclick="changeWOStatus(\'' + wo.work_order_id + '\',\'ready_to_ship\')">Mark Ready to Ship</button>';
    } else if (s === 'ready_to_ship') {
        html = stickerBtns +
               '<button class="btn-wo success" onclick="changeWOStatus(\'' + wo.work_order_id + '\',\'shipped\')">Mark Shipped</button>';
    } else if (s === 'shipped' || s === 'complete') {
        html = stickerBtns;
    }

    // Status transition dropdown
    html += '<div style="position:relative;display:inline-block;margin-left:8px;">' +
        '<button class="btn-wo outline" onclick="toggleStatusMenu()">Status &#9662;</button>' +
        '<div id="statusMenu" style="display:none;position:absolute;top:100%;right:0;z-index:999;background:var(--tf-bg);border:1px solid var(--tf-border);border-radius:8px;box-shadow:0 4px 16px rgba(0,0,0,0.15);min-width:180px;padding:6px 0;margin-top:4px;">';
    PIPELINE_STEPS.forEach(function(st) {
        var active = st === wo.status ? 'font-weight:700;color:var(--tf-blue);' : '';
        html += '<a href="#" onclick="changeWOStatus(\'' + wo.work_order_id + '\',\'' + st + '\');return false;" style="display:block;padding:6px 12px;color:#E2E8F0;text-decoration:none;font-size:0.82rem;' + active + '">' + PIPELINE_LABELS[st] + '</a>';
    });
    html += '</div></div>';

    // Revision button
    html += '<button class="btn-wo outline" onclick="createRevision(\'' + wo.work_order_id + '\')" style="margin-left:4px;">&#128260; New Revision</button>';

    // Edit & Delete
    var canDelete = s !== 'in_fabrication' && s !== 'in_progress';
    html += '<button class="btn-wo outline" onclick="editWO(\'' + wo.work_order_id + '\')" style="margin-left:4px;">&#9998; Edit</button>' +
            '<button class="btn-wo" style="background:#dc3545;color:#fff;margin-left:4px;' + (canDelete ? '' : 'opacity:0.4;pointer-events:none;') + '" onclick="deleteWO(\'' + wo.work_order_id + '\')">&#128465; Delete</button>';

    return html;
}

// ── Tab 2: Items & QC ──
function renderItemsQCTab() {
    if (!currentWO) return;
    var items = currentWO.items || [];

    // Filter bar
    var filterHtml = '<div class="filter-bar">' +
        '<button class="filter-btn ' + (currentItemFilter === 'all' ? 'active' : '') + '" onclick="setItemFilter(\'all\')">All (' + items.length + ')</button>' +
        '<button class="filter-btn ' + (currentItemFilter === 'fabricated' ? 'active' : '') + '" onclick="setItemFilter(\'fabricated\')">Fabricated</button>' +
        '<button class="filter-btn ' + (currentItemFilter === 'purchased' ? 'active' : '') + '" onclick="setItemFilter(\'purchased\')">Purchased</button>' +
        '<button class="filter-btn ' + (currentItemFilter === 'critical' ? 'active' : '') + '" onclick="setItemFilter(\'critical\')">Critical</button>' +
        '<button class="filter-btn ' + (currentItemFilter === 'qc_pending' ? 'active' : '') + '" onclick="setItemFilter(\'qc_pending\')">QC Pending</button>' +
    '</div>';

    // Filter items
    var filtered = items;
    if (currentItemFilter === 'fabricated') {
        filtered = items.filter(function(i) { return (i.item_category || 'fabricated') === 'fabricated'; });
    } else if (currentItemFilter === 'purchased') {
        filtered = items.filter(function(i) { return (i.item_category || 'fabricated') === 'purchased'; });
    } else if (currentItemFilter === 'critical') {
        filtered = items.filter(function(i) { return i.is_critical; });
    } else if (currentItemFilter === 'qc_pending') {
        filtered = items.filter(function(i) { return !i.qc_status || i.qc_status === 'pending'; });
    }

    // Items table
    var tableHtml = '<table class="items-table">' +
        '<thead><tr>' +
            '<th>Ship Mark</th>' +
            '<th>Type</th>' +
            '<th>Status</th>' +
            '<th>QC Status</th>' +
            '<th>Critical</th>' +
            '<th>Assigned To</th>' +
            '<th>Duration</th>' +
            '<th>Actions</th>' +
        '</tr></thead><tbody>';

    filtered.forEach(function(item) {
        var iStatus = item.status || 'queued';
        var iStatusClass = iStatus.replace(/ /g, '_');
        var qcSt = item.qc_status || 'pending';
        var qcClass = qcSt === 'passed' ? 'passed' : (qcSt === 'failed' ? 'failed' : 'pending');
        var isCritical = item.is_critical;
        var isPurchased = (item.item_category || 'fabricated') === 'purchased';
        var est = item.estimated_minutes > 0 ? item.estimated_minutes.toFixed(0) : '-';
        var dur = item.duration_minutes > 0 ? item.duration_minutes.toFixed(1) + '/' + est + ' min' : (est !== '-' ? '—/' + est + ' min' : '—');
        var canStart = !isPurchased && (currentWO.status === 'stickers_printed' || currentWO.status === 'in_fabrication' || currentWO.status === 'in_progress') && iStatus !== 'in_progress' && iStatus !== 'in_fabrication' && iStatus !== 'complete';
        var canFinish = iStatus === 'in_progress' || iStatus === 'in_fabrication';

        var statusLabel = PIPELINE_LABELS[iStatus] || iStatus.charAt(0).toUpperCase() + iStatus.slice(1);

        tableHtml += '<tr class="' + (isCritical ? 'critical-row' : '') + '" id="item-row-' + item.item_id.replace(/[^a-zA-Z0-9]/g, '_') + '">' +
            '<td><span class="ship-mark">' + item.ship_mark + '</span></td>' +
            '<td><span class="component-type-badge ' + (item.component_type || '') + '">' + (item.component_type || '').replace(/_/g, ' ') + '</span></td>' +
            '<td><span class="status-badge ' + iStatusClass + '">' + statusLabel + '</span></td>' +
            '<td><span class="status-badge ' + qcClass + '" style="font-size:0.7rem;">' + qcSt.toUpperCase() + '</span></td>' +
            '<td>' + (isCritical ? '<span class="critical-badge">CRITICAL</span>' : '') + '</td>' +
            '<td style="font-size:0.82rem;">' + (item.assigned_to || item.welder_ids || '—') + '</td>' +
            '<td class="duration-cell">' + dur + '</td>' +
            '<td class="item-actions">' +
                (isPurchased
                    ? '<button class="btn-item" style="background:#10B981;color:white;" onclick="pickPurchasedItem(\'' + item.item_id + '\',\'picked\')">Pick</button>' +
                      '<button class="btn-item" style="background:var(--tf-blue);color:white;" onclick="pickPurchasedItem(\'' + item.item_id + '\',\'staged\')">Stage</button>'
                    : '<button class="btn-item start" ' + (canStart ? '' : 'disabled') + ' onclick="scanItem(\'' + item.item_id + '\',\'start\')">Start</button>' +
                      '<button class="btn-item finish" ' + (canFinish ? '' : 'disabled') + ' onclick="scanItem(\'' + item.item_id + '\',\'finish\')">Finish</button>'
                ) +
                '<button class="btn-item" style="background:var(--tf-navy);color:white;" onclick="printSingleSticker(\'' + item.item_id + '\')" title="Print sticker">QR</button>' +
                '<button class="btn-item" style="background:#0EA5E9;color:white;" onclick="toggleQCPanel(\'' + item.item_id + '\')" title="QC Checklist">QC</button>' +
                '<button class="btn-item" style="background:var(--tf-amber);color:#111;" onclick="toggleChecklist(\'' + item.item_id + '\',\'' + (item.component_type || '') + '\')" title="Fab Steps">&#9776;</button>' +
                '<a href="/wo/' + JOB_CODE + '/' + item.item_id + '" target="_blank" class="btn-item" style="background:var(--tf-blue);color:white;text-decoration:none;display:inline-block;text-align:center;" title="Mobile scan page">&#128241;</a>' +
            '</td>' +
        '</tr>';
    });

    tableHtml += '</tbody></table>';

    if (filtered.length === 0) {
        tableHtml = '<div class="empty-state"><p>No items match this filter.</p></div>';
    }

    document.getElementById('items-qc-content').innerHTML = filterHtml +
        '<div class="wo-card">' +
            '<div class="wo-card-header">' +
                '<h3>Items (' + filtered.length + ')</h3>' +
                '<div style="display:flex;gap:8px;">' +
                    '<button class="btn-wo primary" style="font-size:0.78rem;padding:6px 12px;" onclick="batchQCPass()">Batch QC Pass</button>' +
                '</div>' +
            '</div>' +
            '<div style="overflow-x:auto;">' + tableHtml + '</div>' +
        '</div>';
}

function setItemFilter(filter) {
    currentItemFilter = filter;
    renderItemsQCTab();
}

// ── QC Checklist Panel (inline) ──
function toggleQCPanel(itemId) {
    var safeId = 'qcpanel-' + itemId.replace(/[^a-zA-Z0-9]/g, '_');
    var existing = document.getElementById(safeId);
    if (existing) { existing.remove(); return; }

    apiCall('/api/work-orders/qc-checklist?job_code=' + JOB_CODE + '&item_id=' + encodeURIComponent(itemId), 'GET')
    .then(function(data) {
        if (!data.ok && !data.checklist) {
            // Provide default checklist if endpoint returns no data
            data = { ok: true, checklist: [
                { check_id: 'dimensions', name: 'Dimensions per Drawing', result: null },
                { check_id: 'welds', name: 'Weld Quality Visual', result: null },
                { check_id: 'material', name: 'Material Verification', result: null },
                { check_id: 'finish', name: 'Surface Finish', result: null },
                { check_id: 'bolts', name: 'Bolt Holes / Connections', result: null }
            ]};
        }
        var checklist = data.checklist || [];
        var row = document.getElementById('item-row-' + itemId.replace(/[^a-zA-Z0-9]/g, '_'));
        if (!row) return;

        var newRow = document.createElement('tr');
        newRow.id = safeId;
        var checkHtml = checklist.map(function(c) {
            var passActive = c.result === 'pass' ? ' pass-active' : '';
            var failActive = c.result === 'fail' ? ' fail-active' : '';
            var naActive = c.result === 'n_a' ? ' na-active' : '';
            return '<div class="qc-check-item">' +
                '<span style="color:#E2E8F0;">' + (c.name || c.check_id) + '</span>' +
                '<div class="qc-btn-group">' +
                    '<button class="qc-btn' + passActive + '" onclick="setQCResult(\'' + itemId + '\',\'' + c.check_id + '\',\'pass\',this)">Pass</button>' +
                    '<button class="qc-btn' + failActive + '" onclick="setQCResult(\'' + itemId + '\',\'' + c.check_id + '\',\'fail\',this)">Fail</button>' +
                    '<button class="qc-btn' + naActive + '" onclick="setQCResult(\'' + itemId + '\',\'' + c.check_id + '\',\'n_a\',this)">N/A</button>' +
                '</div>' +
            '</div>';
        }).join('');

        newRow.innerHTML = '<td colspan="8" style="padding:0;"><div class="qc-checklist-panel">' +
            '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">' +
                '<h4 style="margin:0;color:#67E8F9;font-size:0.9rem;">QC Checklist</h4>' +
                '<div style="display:flex;gap:6px;">' +
                    '<button class="btn-wo success" style="font-size:0.75rem;padding:4px 12px;" onclick="qcPassItem(\'' + itemId + '\',false)">QC Pass</button>' +
                    '<button class="btn-wo primary" style="font-size:0.75rem;padding:4px 12px;" onclick="qcPassItem(\'' + itemId + '\',true)">QC Final Pass</button>' +
                    '<button class="btn-wo danger" style="font-size:0.75rem;padding:4px 12px;" onclick="qcFailItem(\'' + itemId + '\')">QC Fail</button>' +
                '</div>' +
            '</div>' +
            checkHtml +
        '</div></td>';
        row.after(newRow);
    });
}

async function setQCResult(itemId, checkId, result, btn) {
    var data = await apiCall('/api/work-orders/qc-checklist', 'POST', {
        job_code: JOB_CODE, item_id: itemId, check_id: checkId, result: result
    });
    if (data.ok) {
        // Update button states
        var group = btn.parentElement;
        group.querySelectorAll('.qc-btn').forEach(function(b) {
            b.classList.remove('pass-active', 'fail-active', 'na-active');
        });
        btn.classList.add(result + '-active');
        if (result === 'fail') {
            showToast('QC check failed - NCR may be required', 'error');
        }
    } else {
        showToast(data.error || 'Failed to save QC result', 'error');
    }
}

async function qcPassItem(itemId, isFinal) {
    var data = await apiCall('/api/work-orders/qc', 'POST', {
        job_code: JOB_CODE, item_id: itemId, result: 'pass', is_final: isFinal
    });
    if (data.ok) {
        showToast(isFinal ? 'QC Final Pass recorded' : 'QC Pass recorded', 'success');
        await loadWODetail(currentWO.work_order_id, true);
        renderItemsQCTab();
    } else {
        showToast(data.error || 'QC pass failed', 'error');
    }
}

async function qcFailItem(itemId) {
    var reason = prompt('Failure reason (NCR will be auto-created):');
    if (!reason) return;
    var data = await apiCall('/api/work-orders/qc', 'POST', {
        job_code: JOB_CODE, item_id: itemId, result: 'fail', reason: reason
    });
    if (data.ok) {
        showToast('QC Fail recorded. NCR created.', 'error');
        await loadWODetail(currentWO.work_order_id, true);
        renderItemsQCTab();
    } else {
        showToast(data.error || 'QC fail failed', 'error');
    }
}

async function batchQCPass() {
    if (!confirm('Mark all pending items as QC Pass?')) return;
    var items = (currentWO.items || []).filter(function(i) { return !i.qc_status || i.qc_status === 'pending'; });
    var count = 0;
    for (var idx = 0; idx < items.length; idx++) {
        var data = await apiCall('/api/work-orders/qc', 'POST', {
            job_code: JOB_CODE, item_id: items[idx].item_id, result: 'pass', is_final: false
        });
        if (data.ok) count++;
    }
    showToast(count + ' items passed QC', 'success');
    await loadWODetail(currentWO.work_order_id, true);
    renderItemsQCTab();
}

// ── Fab Checklist (existing functionality) ──
async function toggleChecklist(itemId, compType) {
    var rowId = 'checklist-' + itemId.replace(/[^a-zA-Z0-9]/g, '_');
    var existing = document.getElementById(rowId);
    if (existing) { existing.remove(); return; }

    var data = await apiCall('/api/work-orders/checklist?job_code=' + JOB_CODE + '&item_id=' + encodeURIComponent(itemId), 'GET');
    if (!data.ok) { showToast(data.error || 'Could not load checklist', 'error'); return; }

    var checklist = data.checklist || [];
    var row = document.getElementById('item-row-' + itemId.replace(/[^a-zA-Z0-9]/g, '_'));
    if (!row) return;

    var newRow = document.createElement('tr');
    newRow.id = rowId;
    newRow.innerHTML = '<td colspan="8" style="padding:0;"><div class="checklist-panel">' +
        '<h4 style="margin:8px 12px 4px;color:var(--tf-amber);">Fabrication Steps</h4>' +
        '<div class="checklist-steps">' +
        checklist.map(function(s) {
            var icon = s.checked ? '&#9745;' : (s.checkpoint ? '&#9888;' : '&#9744;');
            var style = s.checked ? 'opacity:0.6;text-decoration:line-through;' : '';
            var cpBadge = s.checkpoint ? '<span style="background:var(--tf-amber);color:#111;padding:1px 5px;border-radius:3px;font-size:0.65rem;margin-left:4px;">QC CHECKPOINT</span>' : '';
            return '<div class="checklist-step" style="' + style + 'padding:6px 12px;border-bottom:1px solid rgba(255,255,255,0.05);display:flex;align-items:center;gap:8px;cursor:' + (s.checked ? 'default' : 'pointer') + ';" ' +
                (s.checked ? '' : 'onclick="checkStep(\'' + itemId + '\',' + s.step_num + ',this)"') + '>' +
                '<span style="font-size:1.2rem;">' + icon + '</span>' +
                '<span><strong>Step ' + s.step_num + ':</strong> ' + s.title + cpBadge + '</span>' +
                '<span style="margin-left:auto;font-size:0.7rem;color:#888;">' + (s.checked ? (s.checked_by || '') + ' ' + (s.checked_at ? new Date(s.checked_at).toLocaleTimeString() : '') : (s.estimated_minutes || 0) + ' min est.') + '</span>' +
            '</div>';
        }).join('') +
        '</div></div></td>';
    row.after(newRow);
}

async function checkStep(itemId, stepNum, el) {
    var data = await apiCall('/api/work-orders/checklist', 'POST', {
        job_code: JOB_CODE, item_id: itemId, step_num: stepNum
    });
    if (data.ok) {
        showToast(data.message || 'Step completed', 'success');
        var rowId = 'checklist-' + itemId.replace(/[^a-zA-Z0-9]/g, '_');
        var existing = document.getElementById(rowId);
        if (existing) existing.remove();
        toggleChecklist(itemId, '');
    } else {
        showToast(data.error || 'Failed', 'error');
    }
}

// ── Tab 3: Traceability ──
function renderTraceabilityTab() {
    if (!currentWO) return;
    var items = currentWO.items || [];
    var traceItems = traceData.items || items;

    // Calculate % traced
    var totalItems = items.length;
    var tracedCount = items.filter(function(i) { return i.heat_number || (traceData.items && traceData.items.find(function(t) { return t.item_id === i.item_id && t.heat_number; })); }).length;
    var tracePct = totalItems > 0 ? Math.round(100 * tracedCount / totalItems) : 0;

    var html = '<div class="trace-pct-bar">' +
        '<span style="font-size:0.85rem;font-weight:600;color:#E2E8F0;white-space:nowrap;">' + tracePct + '% Traced</span>' +
        '<div class="trace-pct-fill"><div class="trace-pct-fill-inner" style="width:' + tracePct + '%"></div></div>' +
        '<span style="font-size:0.78rem;color:var(--tf-slate);">' + tracedCount + '/' + totalItems + ' items</span>' +
    '</div>';

    // Lost ID procedure notice
    html += '<div class="wo-card" style="border-left:3px solid var(--tf-amber);margin-bottom:16px;">' +
        '<div style="display:flex;align-items:center;gap:8px;">' +
            '<span style="font-size:1.2rem;">&#9888;</span>' +
            '<div>' +
                '<strong style="color:var(--tf-amber);font-size:0.85rem;">Lost Material ID Procedure</strong>' +
                '<p style="color:var(--tf-slate);font-size:0.78rem;margin:2px 0 0;">If material identification is lost, the item must be re-tested or quarantined per AISC Chapter 6. Contact QC Manager immediately.</p>' +
            '</div>' +
        '</div>' +
    '</div>';

    // Material receipt inspection section
    html += '<div class="wo-card" style="margin-bottom:16px;">' +
        '<div class="wo-card-header"><h3>Material Receipt Inspection</h3></div>' +
        '<p style="color:var(--tf-slate);font-size:0.82rem;">Incoming materials must be inspected for damage, dimensions, grade marking, and MTR verification before being released to fabrication.</p>' +
    '</div>';

    // Traceability table
    html += '<div class="wo-card">' +
        '<div class="wo-card-header"><h3>Material Traceability</h3></div>' +
        '<div style="overflow-x:auto;">' +
        '<table class="items-table">' +
        '<thead><tr>' +
            '<th>Ship Mark</th>' +
            '<th>Type</th>' +
            '<th>Heat Number</th>' +
            '<th>MTR Link</th>' +
            '<th>Coil Tag</th>' +
            '<th>Welder IDs</th>' +
            '<th>WPS Ref</th>' +
            '<th>Calibration ID</th>' +
        '</tr></thead><tbody>';

    items.forEach(function(item) {
        var tr = (traceData.items || []).find(function(t) { return t.item_id === item.item_id; }) || item;
        var safeItemId = item.item_id.replace(/'/g, "\\'");
        html += '<tr>' +
            '<td><span class="ship-mark">' + item.ship_mark + '</span>' +
                (item.is_critical ? ' <span class="critical-badge">CRIT</span>' : '') +
            '</td>' +
            '<td><span class="component-type-badge ' + (item.component_type || '') + '">' + (item.component_type || '').replace(/_/g, ' ') + '</span></td>' +
            '<td><input class="inline-edit" value="' + (tr.heat_number || item.heat_number || '') + '" onchange="saveTraceField(\'' + safeItemId + '\',\'heat_number\',this.value)" placeholder="Enter heat #"></td>' +
            '<td><input class="inline-edit" value="' + (tr.mtr_link || item.mtr_link || '') + '" onchange="saveTraceField(\'' + safeItemId + '\',\'mtr_link\',this.value)" placeholder="MTR link/ref"></td>' +
            '<td><input class="inline-edit" value="' + (tr.coil_tag || item.coil_tag || '') + '" onchange="saveTraceField(\'' + safeItemId + '\',\'coil_tag\',this.value)" placeholder="Coil tag"></td>' +
            '<td><input class="inline-edit" value="' + (tr.welder_ids || item.welder_ids || '') + '" onchange="saveTraceField(\'' + safeItemId + '\',\'welder_ids\',this.value)" placeholder="W1, W2"></td>' +
            '<td><input class="inline-edit" value="' + (tr.wps_reference || item.wps_reference || '') + '" onchange="saveTraceField(\'' + safeItemId + '\',\'wps_reference\',this.value)" placeholder="WPS ref"></td>' +
            '<td><input class="inline-edit" value="' + (tr.calibration_id || item.calibration_id || '') + '" onchange="saveTraceField(\'' + safeItemId + '\',\'calibration_id\',this.value)" placeholder="Cal ID"></td>' +
        '</tr>';
    });

    html += '</tbody></table></div></div>';

    document.getElementById('traceability-content').innerHTML = html;
}

async function saveTraceField(itemId, field, value) {
    var body = { job_code: JOB_CODE, item_id: itemId };
    body[field] = value;
    var data = await apiCall('/api/work-orders/item-edit', 'POST', body);
    if (data.ok) {
        showToast(field.replace(/_/g, ' ') + ' updated', 'success');
    } else {
        showToast(data.error || 'Failed to save', 'error');
    }
}

// ── Tab 4: NCRs ──
function renderNCRsTab() {
    if (!currentWO) return;

    var html = '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">' +
        '<h3 style="color:#E2E8F0;margin:0;">Non-Conformance Reports</h3>' +
        '<button class="btn-wo danger" onclick="showCreateNCRModal()">+ New NCR</button>' +
    '</div>';

    if (ncrList.length === 0) {
        html += '<div class="empty-state"><p>No NCRs for this work order.</p></div>';
    } else {
        ncrList.forEach(function(ncr) {
            var sevClass = 'severity-' + (ncr.severity || 'minor');
            var statusClass = (ncr.status || 'open').replace(/ /g, '_');
            html += '<div class="ncr-card ' + sevClass + '">' +
                '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">' +
                    '<div>' +
                        '<strong style="color:#E2E8F0;font-size:0.9rem;">' + (ncr.ncr_id || 'NCR') + '</strong>' +
                        ' <span class="ncr-status-badge ' + statusClass + '">' + (ncr.status || 'open').toUpperCase() + '</span>' +
                        ' <span style="font-size:0.72rem;padding:2px 8px;border-radius:4px;background:' +
                            (ncr.severity === 'critical' ? 'var(--tf-danger-bg);color:var(--tf-danger)' :
                             ncr.severity === 'major' ? 'var(--tf-warning-bg);color:var(--tf-warning)' :
                             'var(--tf-info-bg);color:var(--tf-info)') + ';font-weight:600;">' +
                            (ncr.severity || 'minor').toUpperCase() + '</span>' +
                    '</div>' +
                    '<span style="font-size:0.72rem;color:var(--tf-slate);">' + (ncr.created_at ? new Date(ncr.created_at).toLocaleString() : '') + '</span>' +
                '</div>' +
                (ncr.item_id ? '<div style="font-size:0.78rem;color:var(--tf-slate);margin-bottom:4px;">Item: <span style="font-family:\'SF Mono\',monospace;">' + ncr.item_id + '</span></div>' : '') +
                '<div style="font-size:0.85rem;color:#E2E8F0;margin-bottom:8px;">' + (ncr.description || '') + '</div>' +
                (ncr.root_cause ? '<div style="font-size:0.78rem;color:var(--tf-slate);margin-bottom:4px;"><strong>Root Cause:</strong> ' + ncr.root_cause + '</div>' : '') +
                (ncr.corrective_action ? '<div style="font-size:0.78rem;color:var(--tf-slate);margin-bottom:4px;"><strong>Corrective Action:</strong> ' + ncr.corrective_action + '</div>' : '') +
                (ncr.disposition ? '<div style="font-size:0.78rem;color:var(--tf-slate);margin-bottom:4px;"><strong>Disposition:</strong> ' + ncr.disposition + '</div>' : '') +
                '<div style="display:flex;gap:6px;margin-top:8px;">' +
                    (ncr.status === 'open' ? '<button class="btn-wo warning" style="font-size:0.75rem;padding:4px 12px;" onclick="updateNCRStatus(\'' + ncr.ncr_id + '\',\'in_review\')">Start Review</button>' : '') +
                    (ncr.status === 'in_review' ? '<button class="btn-wo success" style="font-size:0.75rem;padding:4px 12px;" onclick="updateNCRStatus(\'' + ncr.ncr_id + '\',\'resolved\')">Resolve</button>' : '') +
                    (ncr.status === 'resolved' ? '<button class="btn-wo outline" style="font-size:0.75rem;padding:4px 12px;" onclick="updateNCRStatus(\'' + ncr.ncr_id + '\',\'closed\')">Close</button>' : '') +
                    '<button class="btn-wo outline" style="font-size:0.75rem;padding:4px 12px;" onclick="editNCR(\'' + ncr.ncr_id + '\')">Edit</button>' +
                '</div>' +
            '</div>';
        });
    }

    document.getElementById('ncrs-content').innerHTML = html;
}

function showCreateNCRModal() {
    var items = currentWO.items || [];
    var itemOptions = '<option value="">-- Select Item (optional) --</option>';
    items.forEach(function(i) { itemOptions += '<option value="' + i.item_id + '">' + i.ship_mark + ' (' + (i.component_type || '') + ')</option>'; });

    document.getElementById('modal-content').innerHTML =
        '<h3>Create Non-Conformance Report</h3>' +
        '<label>Affected Item</label>' +
        '<select id="ncr-item">' + itemOptions + '</select>' +
        '<label>Severity</label>' +
        '<select id="ncr-severity">' +
            '<option value="minor">Minor</option>' +
            '<option value="major">Major</option>' +
            '<option value="critical">Critical</option>' +
        '</select>' +
        '<label>Description</label>' +
        '<textarea id="ncr-desc" placeholder="Describe the non-conformance..."></textarea>' +
        '<label>Root Cause</label>' +
        '<textarea id="ncr-root" placeholder="Root cause analysis..."></textarea>' +
        '<label>Corrective Action</label>' +
        '<textarea id="ncr-action" placeholder="Proposed corrective action..."></textarea>' +
        '<label>Disposition</label>' +
        '<select id="ncr-disposition">' +
            '<option value="">-- Select --</option>' +
            '<option value="rework">Rework</option>' +
            '<option value="repair">Repair</option>' +
            '<option value="use_as_is">Use As-Is</option>' +
            '<option value="scrap">Scrap</option>' +
            '<option value="return_to_supplier">Return to Supplier</option>' +
        '</select>' +
        '<div class="modal-actions">' +
            '<button class="btn-wo outline" onclick="closeModal()">Cancel</button>' +
            '<button class="btn-wo danger" onclick="submitNCR()">Create NCR</button>' +
        '</div>';
    openModal();
}

async function submitNCR() {
    var data = await apiCall('/api/work-orders/ncr', 'POST', {
        job_code: JOB_CODE,
        wo_id: currentWO.work_order_id,
        item_id: document.getElementById('ncr-item').value || null,
        severity: document.getElementById('ncr-severity').value,
        description: document.getElementById('ncr-desc').value,
        root_cause: document.getElementById('ncr-root').value,
        corrective_action: document.getElementById('ncr-action').value,
        disposition: document.getElementById('ncr-disposition').value
    });
    if (data.ok) {
        showToast('NCR created', 'info');
        closeModal();
        await loadNCRs();
        renderNCRsTab();
    } else {
        showToast(data.error || 'Failed to create NCR', 'error');
    }
}

async function updateNCRStatus(ncrId, newStatus) {
    var data = await apiCall('/api/work-orders/ncr', 'POST', {
        job_code: JOB_CODE,
        wo_id: currentWO.work_order_id,
        ncr_id: ncrId,
        status: newStatus
    });
    if (data.ok) {
        showToast('NCR status updated to ' + newStatus, 'success');
        await loadNCRs();
        renderNCRsTab();
    } else {
        showToast(data.error || 'Failed to update NCR', 'error');
    }
}

async function editNCR(ncrId) {
    var ncr = ncrList.find(function(n) { return n.ncr_id === ncrId; });
    if (!ncr) return;

    document.getElementById('modal-content').innerHTML =
        '<h3>Edit NCR: ' + ncrId + '</h3>' +
        '<label>Description</label>' +
        '<textarea id="ncr-edit-desc">' + (ncr.description || '') + '</textarea>' +
        '<label>Root Cause</label>' +
        '<textarea id="ncr-edit-root">' + (ncr.root_cause || '') + '</textarea>' +
        '<label>Corrective Action</label>' +
        '<textarea id="ncr-edit-action">' + (ncr.corrective_action || '') + '</textarea>' +
        '<label>Disposition</label>' +
        '<select id="ncr-edit-disposition">' +
            '<option value="" ' + (!ncr.disposition ? 'selected' : '') + '>-- Select --</option>' +
            '<option value="rework" ' + (ncr.disposition === 'rework' ? 'selected' : '') + '>Rework</option>' +
            '<option value="repair" ' + (ncr.disposition === 'repair' ? 'selected' : '') + '>Repair</option>' +
            '<option value="use_as_is" ' + (ncr.disposition === 'use_as_is' ? 'selected' : '') + '>Use As-Is</option>' +
            '<option value="scrap" ' + (ncr.disposition === 'scrap' ? 'selected' : '') + '>Scrap</option>' +
            '<option value="return_to_supplier" ' + (ncr.disposition === 'return_to_supplier' ? 'selected' : '') + '>Return to Supplier</option>' +
        '</select>' +
        '<div class="modal-actions">' +
            '<button class="btn-wo outline" onclick="closeModal()">Cancel</button>' +
            '<button class="btn-wo primary" onclick="saveNCREdit(\'' + ncrId + '\')">Save</button>' +
        '</div>';
    openModal();
}

async function saveNCREdit(ncrId) {
    var data = await apiCall('/api/work-orders/ncr', 'POST', {
        job_code: JOB_CODE,
        wo_id: currentWO.work_order_id,
        ncr_id: ncrId,
        description: document.getElementById('ncr-edit-desc').value,
        root_cause: document.getElementById('ncr-edit-root').value,
        corrective_action: document.getElementById('ncr-edit-action').value,
        disposition: document.getElementById('ncr-edit-disposition').value
    });
    if (data.ok) {
        showToast('NCR updated', 'success');
        closeModal();
        await loadNCRs();
        renderNCRsTab();
    } else {
        showToast(data.error || 'Failed to update NCR', 'error');
    }
}

// ── Tab 5: Audit Log ──
function renderAuditTab() {
    if (!currentWO) return;

    var html = '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:8px;">' +
        '<h3 style="color:#E2E8F0;margin:0;">Audit Trail</h3>' +
        '<div class="filter-bar" style="margin-bottom:0;">' +
            '<input type="text" id="audit-filter-item" placeholder="Filter by item ID..." style="padding:6px 12px;border-radius:6px;border:1px solid var(--tf-border);background:var(--tf-bg);color:#E2E8F0;font-size:0.78rem;width:180px;" oninput="filterAuditLog()">' +
            '<select id="audit-filter-action" style="padding:6px 12px;border-radius:6px;border:1px solid var(--tf-border);background:var(--tf-bg);color:#E2E8F0;font-size:0.78rem;" onchange="filterAuditLog()">' +
                '<option value="">All Actions</option>' +
                '<option value="created">Created</option>' +
                '<option value="status_change">Status Change</option>' +
                '<option value="qc_pass">QC Pass</option>' +
                '<option value="qc_fail">QC Fail</option>' +
                '<option value="ncr_created">NCR Created</option>' +
                '<option value="scan_start">Scan Start</option>' +
                '<option value="scan_finish">Scan Finish</option>' +
                '<option value="edit">Edit</option>' +
                '<option value="revision">Revision</option>' +
            '</select>' +
        '</div>' +
    '</div>';

    html += '<div class="audit-timeline" id="audit-timeline-content">';

    if (auditLog.length === 0) {
        html += '<div class="empty-state" style="padding:30px;"><p>No audit entries yet.</p></div>';
    } else {
        auditLog.forEach(function(entry) {
            var diffHtml = '';
            if (entry.before_value || entry.after_value) {
                diffHtml = '<div class="audit-diff">' +
                    (entry.before_value ? '<span class="diff-old">- ' + entry.before_value + '</span><br>' : '') +
                    (entry.after_value ? '<span class="diff-new">+ ' + entry.after_value + '</span>' : '') +
                '</div>';
            }
            html += '<div class="audit-entry" data-item="' + (entry.item_id || '') + '" data-action="' + (entry.action || '') + '">' +
                '<div class="audit-time">' + (entry.timestamp ? new Date(entry.timestamp).toLocaleString() : '') + '</div>' +
                '<div class="audit-action">' +
                    '<strong>' + (entry.user || 'System') + '</strong> ' +
                    (entry.action || entry.description || '') +
                    (entry.item_id ? ' <span style="font-family:\'SF Mono\',monospace;font-size:0.78rem;color:var(--tf-blue-mid);">' + entry.item_id + '</span>' : '') +
                '</div>' +
                (entry.details ? '<div class="audit-detail">' + entry.details + '</div>' : '') +
                diffHtml +
            '</div>';
        });
    }

    html += '</div>';
    document.getElementById('audit-content').innerHTML = html;
}

function filterAuditLog() {
    var itemFilter = (document.getElementById('audit-filter-item').value || '').toLowerCase();
    var actionFilter = document.getElementById('audit-filter-action').value;
    document.querySelectorAll('.audit-entry').forEach(function(entry) {
        var itemMatch = !itemFilter || (entry.dataset.item || '').toLowerCase().indexOf(itemFilter) !== -1;
        var actionMatch = !actionFilter || entry.dataset.action === actionFilter;
        entry.style.display = (itemMatch && actionMatch) ? '' : 'none';
    });
}

// ── Tab 6: Documents ──
function renderDocumentsTab() {
    if (!currentWO) return;
    var wo = currentWO;

    var html = '<div class="wo-card">' +
        '<div class="wo-card-header"><h3>Documents &amp; Reports</h3></div>' +
        '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;">' +
            '<div class="wo-card" style="margin-bottom:0;cursor:pointer;" onclick="window.open(\'/shop-drawings/' + JOB_CODE + '\',\'_blank\')">' +
                '<div style="font-size:1.5rem;margin-bottom:6px;">&#128209;</div>' +
                '<strong style="color:#E2E8F0;">Shop Drawings</strong>' +
                '<p style="color:var(--tf-slate);font-size:0.78rem;margin:4px 0 0;">View all shop drawings for this project</p>' +
            '</div>' +
            '<div class="wo-card" style="margin-bottom:0;cursor:pointer;" onclick="downloadPacketPDF(\'' + wo.work_order_id + '\')">' +
                '<div style="font-size:1.5rem;margin-bottom:6px;">&#128196;</div>' +
                '<strong style="color:#E2E8F0;">WO Packet PDF</strong>' +
                '<p style="color:var(--tf-slate);font-size:0.78rem;margin:4px 0 0;">Complete work order packet with all details</p>' +
            '</div>' +
            '<div class="wo-card" style="margin-bottom:0;cursor:pointer;" onclick="printStickers(\'' + wo.work_order_id + '\',\'pdf\')">' +
                '<div style="font-size:1.5rem;margin-bottom:6px;">&#127991;</div>' +
                '<strong style="color:#E2E8F0;">Sticker PDFs</strong>' +
                '<p style="color:var(--tf-slate);font-size:0.78rem;margin:4px 0 0;">QR code stickers for all items</p>' +
            '</div>' +
            '<div class="wo-card" style="margin-bottom:0;cursor:pointer;" onclick="switchDetailTab(\'traceability\')">' +
                '<div style="font-size:1.5rem;margin-bottom:6px;">&#128220;</div>' +
                '<strong style="color:#E2E8F0;">MTR Documents</strong>' +
                '<p style="color:var(--tf-slate);font-size:0.78rem;margin:4px 0 0;">Mill Test Reports linked to items</p>' +
            '</div>' +
            '<div class="wo-card" style="margin-bottom:0;cursor:pointer;" onclick="switchDetailTab(\'ncrs\')">' +
                '<div style="font-size:1.5rem;margin-bottom:6px;">&#9888;</div>' +
                '<strong style="color:#E2E8F0;">Inspection Reports</strong>' +
                '<p style="color:var(--tf-slate);font-size:0.78rem;margin:4px 0 0;">QC inspection results and NCRs</p>' +
            '</div>' +
            '<div class="wo-card" style="margin-bottom:0;cursor:pointer;" onclick="switchDetailTab(\'audit\')">' +
                '<div style="font-size:1.5rem;margin-bottom:6px;">&#128214;</div>' +
                '<strong style="color:#E2E8F0;">Audit Trail Report</strong>' +
                '<p style="color:var(--tf-slate);font-size:0.78rem;margin:4px 0 0;">Complete history of all WO actions</p>' +
            '</div>' +
        '</div>' +
    '</div>';

    document.getElementById('documents-content').innerHTML = html;
}

// ── WO Actions ──
async function createWorkOrder() {
    if (!JOB_CODE || JOB_CODE === '{{JOB_CODE}}') {
        showToast('No project selected - open work orders from a project page', 'error');
        return;
    }
    var data = await apiCall('/api/work-orders/create', 'POST', { job_code: JOB_CODE });
    if (data.ok) {
        showToast('Work order created!', 'success');
        await refreshAll();
        if (data.work_order) {
            currentWO = data.work_order;
            showDetailView();
            renderAllDetailTabs();
            switchDetailTab('overview');
        }
    } else {
        showToast(data.error || 'Failed to create work order', 'error');
    }
}

async function approveWO(woId) {
    var data = await apiCall('/api/work-orders/approve', 'POST', { job_code: JOB_CODE, wo_id: woId });
    if (data.ok) {
        showToast('Work order approved!', 'success');
        currentWO = data.work_order;
        await loadWorkOrders();
        renderAllDetailTabs();
    } else {
        showToast(data.error || 'Failed to approve', 'error');
    }
}

async function markStickersPrinted(woId) {
    var data = await apiCall('/api/work-orders/stickers-printed', 'POST', { job_code: JOB_CODE, wo_id: woId });
    if (data.ok) {
        showToast('Stickers marked as printed!', 'success');
        currentWO = data.work_order;
        await loadWorkOrders();
        renderAllDetailTabs();
    } else {
        showToast(data.error || 'Failed', 'error');
    }
}

async function holdWO(woId, action) {
    var data = await apiCall('/api/work-orders/hold', 'POST', { job_code: JOB_CODE, wo_id: woId, action: action });
    if (data.ok) {
        showToast(action === 'hold' ? 'Work order on hold' : 'Work order resumed', 'info');
        currentWO = data.work_order;
        await loadWorkOrders();
        renderAllDetailTabs();
    } else {
        showToast(data.error || 'Failed', 'error');
    }
}

async function changeWOStatus(woId, newStatus) {
    var menu = document.getElementById('statusMenu');
    if (menu) menu.style.display = 'none';
    var data = await apiCall('/api/work-orders/status', 'POST', { job_code: JOB_CODE, wo_id: woId, status: newStatus });
    if (data.ok) {
        showToast('Status changed to ' + PIPELINE_LABELS[newStatus], 'success');
        currentWO = data.work_order || currentWO;
        if (currentWO) currentWO.status = newStatus;
        await loadWorkOrders();
        renderAllDetailTabs();
    } else {
        showToast(data.error || 'Status change failed', 'error');
    }
}

async function createRevision(woId) {
    if (!confirm('Create a new revision of this work order?')) return;
    var data = await apiCall('/api/work-orders/revision', 'POST', { job_code: JOB_CODE, wo_id: woId });
    if (data.ok) {
        showToast('Revision created! Now at Rev ' + (data.revision || ''), 'success');
        currentWO = data.work_order || currentWO;
        await loadWorkOrders();
        renderAllDetailTabs();
    } else {
        showToast(data.error || 'Failed to create revision', 'error');
    }
}

async function scanItem(itemId, action) {
    var data = await apiCall('/api/work-orders/qr-scan', 'POST', {
        job_code: JOB_CODE, item_id: itemId, action: action
    });
    if (data.ok) {
        showToast(data.message || 'Item ' + action + 'ed', 'success');
        scanHistory.unshift({
            time: new Date().toLocaleTimeString(),
            item_id: itemId,
            action: data.action,
            message: data.message
        });
        if (currentWO) {
            await loadWODetail(currentWO.work_order_id, true);
            renderItemsQCTab();
        }
    } else {
        showToast(data.error || 'Scan failed', 'error');
    }
    return data;
}

async function pickPurchasedItem(itemId, pickStatus) {
    var data = await apiCall('/api/work-orders/purchased', 'POST', {
        job_code: JOB_CODE, item_id: itemId, pick_status: pickStatus
    });
    if (data.ok) {
        showToast('Item ' + pickStatus.replace(/_/g, ' '), 'success');
        if (currentWO) {
            await loadWODetail(currentWO.work_order_id, true);
            renderItemsQCTab();
        }
    } else {
        showToast(data.error || 'Pick update failed', 'error');
    }
}

async function processQRScan(action) {
    var input = document.getElementById('qr-input');
    var itemId = input.value.trim();
    if (!itemId) {
        showToast('Enter or scan an item ID', 'error');
        return;
    }
    var resultEl = document.getElementById('qr-result');
    if (!action) action = 'start';
    var data = await scanItem(itemId, action);
    if (data.ok) {
        resultEl.className = 'qr-result success';
        resultEl.innerHTML = data.message || 'Scan processed';
        input.value = '';
        input.focus();
    } else {
        resultEl.className = 'qr-result error';
        resultEl.innerHTML = data.error || 'Scan failed';
    }
}

async function batchScan(prefix, action) {
    var data = await apiCall('/api/work-orders/batch-scan', 'POST', {
        job_code: JOB_CODE, prefix: prefix, action: action
    });
    if (data.ok) {
        showToast(data.message || 'Batch scan complete', 'success');
        if (currentWO) {
            await loadWODetail(currentWO.work_order_id, true);
            renderItemsQCTab();
        }
    } else {
        showToast(data.error || 'Batch scan failed', 'error');
    }
}

// ── Sticker/Document Functions ──
function printStickers(woId, format) {
    window.open('/api/work-orders/stickers/' + format + '?job_code=' + JOB_CODE + '&wo_id=' + woId, '_blank');
}

function printSingleSticker(itemId) {
    window.open('/api/work-orders/stickers/single?job_code=' + JOB_CODE + '&item_id=' + itemId, '_blank');
}

function fabSticker(woId, type) {
    window.open('/api/work-orders/fab-stickers/' + type + '?job_code=' + JOB_CODE + '&wo_id=' + woId, '_blank');
    var menu = document.getElementById('fabMenu_' + woId);
    if (menu) menu.style.display = 'none';
}

function toggleFabMenu(woId) {
    document.querySelectorAll('[id^="fabMenu_"]').forEach(function(m) {
        if (m.id !== 'fabMenu_' + woId) m.style.display = 'none';
    });
    var menu = document.getElementById('fabMenu_' + woId);
    if (menu) menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
}

function toggleStatusMenu() {
    var menu = document.getElementById('statusMenu');
    if (menu) menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
}

document.addEventListener('click', function(e) {
    if (!e.target.closest('[id^="fabMenu_"]') && !e.target.textContent.includes('Fab Stickers')) {
        document.querySelectorAll('[id^="fabMenu_"]').forEach(function(m) { m.style.display = 'none'; });
    }
    if (!e.target.closest('#statusMenu') && !e.target.textContent.includes('Status')) {
        var sm = document.getElementById('statusMenu');
        if (sm) sm.style.display = 'none';
    }
});

async function printAndMark(woId) {
    printStickers(woId, 'pdf');
    await markStickersPrinted(woId);
}

function downloadPacketPDF(woId) {
    window.open('/api/work-orders/packet/pdf?job_code=' + JOB_CODE + '&wo_id=' + woId, '_blank');
}

async function editWO(woId) {
    if (!currentWO) return;
    var priority = prompt('Priority (normal / rush / hot):', currentWO.priority || 'normal');
    if (priority === null) return;
    var dueDate = prompt('Due date (YYYY-MM-DD or leave empty):', currentWO.due_date || '');
    if (dueDate === null) return;
    var deliveryDate = prompt('Delivery date (YYYY-MM-DD or leave empty):', currentWO.delivery_date || '');
    if (deliveryDate === null) return;
    var notes = prompt('Notes:', currentWO.notes || '');
    if (notes === null) return;

    var data = await apiCall('/api/work-orders/edit', 'POST', {
        job_code: JOB_CODE, wo_id: woId,
        priority: priority, due_date: dueDate, delivery_date: deliveryDate, notes: notes
    });
    if (data.ok) {
        showToast('Work order updated!', 'success');
        currentWO = data.work_order;
        await loadWorkOrders();
        renderAllDetailTabs();
    } else {
        showToast(data.error || 'Failed to edit', 'error');
    }
}

async function deleteWO(woId) {
    if (!confirm('Are you sure you want to delete this work order? This cannot be undone.')) return;
    var data = await apiCall('/api/work-orders/delete', 'POST', { job_code: JOB_CODE, wo_id: woId });
    if (data.ok) {
        showToast('Work order deleted', 'info');
        currentWO = null;
        await loadWorkOrders();
        backToList();
    } else {
        showToast(data.error || 'Failed to delete', 'error');
    }
}

// ── Modal Helpers ──
function openModal() {
    document.getElementById('modal-overlay').classList.add('active');
}

function closeModal() {
    document.getElementById('modal-overlay').classList.remove('active');
}

// ── Toast ──
function showToast(msg, type) {
    var toast = document.getElementById('toast');
    toast.textContent = msg;
    toast.className = 'toast ' + (type || 'info') + ' show';
    setTimeout(function() { toast.className = 'toast'; }, 4000);
}

// ── Auto-refresh every 30 seconds ──
setInterval(async function() {
    if (currentWO) {
        await loadWODetail(currentWO.work_order_id, true);
    }
}, 30000);
</script>
</body>
</html>
"""
