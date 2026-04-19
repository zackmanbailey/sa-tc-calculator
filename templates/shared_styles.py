"""
TitanForge v3.0 — Shared Design System
========================================
Single source of truth for colors, typography, spacing, and component styles.
Imported by each template to ensure visual consistency across the entire app.
"""

DESIGN_SYSTEM_CSS = """
/* ============================================================
   TitanForge Design System v3.0
   ============================================================ */

/* ── Design Tokens ──────────────────────────────────────────── */
:root {
    /* Brand Colors */
    --tf-navy:       #0F172A;
    --tf-navy-light: #1E293B;
    --tf-blue:       #1E40AF;
    --tf-blue-mid:   #2563EB;
    --tf-blue-light: #1E3A5F;
    --tf-amber:      #F59E0B;
    --tf-amber-light:#3B2A1A;

    /* Semantic Colors */
    --tf-success:    #059669;
    --tf-success-bg: #0D2818;
    --tf-warning:    #D97706;
    --tf-warning-bg: #3B2A1A;
    --tf-danger:     #DC2626;
    --tf-danger-bg:  #3B1A1A;
    --tf-info:       #0284C7;
    --tf-info-bg:    #0C2A3B;

    /* Neutrals (dark-theme mapped) */
    --tf-gray-50:    #0F172A;
    --tf-gray-100:   #1E293B;
    --tf-gray-200:   #334155;
    --tf-gray-300:   #475569;
    --tf-gray-400:   #94A3B8;
    --tf-gray-500:   #94A3B8;
    --tf-gray-600:   #CBD5E1;
    --tf-gray-700:   #E2E8F0;
    --tf-gray-800:   #F1F5F9;
    --tf-gray-900:   #F8FAFC;

    /* Surfaces */
    --tf-bg:         #0F172A;
    --tf-surface:    #1E293B;
    --tf-border:     #334155;
    --tf-border-dark:#475569;

    /* Typography */
    --tf-font: 'Inter', system-ui, -apple-system, sans-serif;
    --tf-font-mono:  'JetBrains Mono', 'Fira Code', 'Consolas', monospace;

    /* Type Scale (Major Third — 1.25) */
    --tf-text-xs:    0.75rem;   /* 12px */
    --tf-text-sm:    0.8125rem; /* 13px */
    --tf-text-base:  0.875rem;  /* 14px */
    --tf-text-md:    1rem;      /* 16px */
    --tf-text-lg:    1.125rem;  /* 18px */
    --tf-text-xl:    1.25rem;   /* 20px */
    --tf-text-2xl:   1.5rem;    /* 24px */
    --tf-text-3xl:   1.875rem;  /* 30px */

    /* Spacing (8px grid) */
    --tf-sp-1:  0.25rem;  /* 4px  */
    --tf-sp-2:  0.5rem;   /* 8px  */
    --tf-sp-3:  0.75rem;  /* 12px */
    --tf-sp-4:  1rem;     /* 16px */
    --tf-sp-5:  1.25rem;  /* 20px */
    --tf-sp-6:  1.5rem;   /* 24px */
    --tf-sp-8:  2rem;     /* 32px */
    --tf-sp-10: 2.5rem;   /* 40px */
    --tf-sp-12: 3rem;     /* 48px */

    /* Radii */
    --tf-radius-sm: 6px;
    --tf-radius:    8px;
    --tf-radius-lg: 12px;
    --tf-radius-xl: 16px;

    /* Shadows */
    --tf-shadow-sm:  0 1px 2px rgba(0,0,0,0.05);
    --tf-shadow:     0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04);
    --tf-shadow-md:  0 4px 6px -1px rgba(0,0,0,0.08), 0 2px 4px -2px rgba(0,0,0,0.04);
    --tf-shadow-lg:  0 10px 15px -3px rgba(0,0,0,0.08), 0 4px 6px -4px rgba(0,0,0,0.03);

    /* Transitions */
    --tf-ease:       cubic-bezier(0.4, 0, 0.2, 1);
    --tf-duration:   150ms;
}

/* ── Google Fonts ────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* ── Global Reset ────────────────────────────────────────────── */
*, *::before, *::after {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

html { -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }

body {
    font-family: var(--tf-font);
    font-size: var(--tf-text-base);
    line-height: 1.6;
    color: var(--tf-gray-400);
    background: var(--tf-bg);
}

/* ── Shared Topbar ───────────────────────────────────────────── */
.tf-topbar {
    background: var(--tf-navy);
    color: #fff;
    height: 56px;
    display: flex;
    align-items: center;
    padding: 0 var(--tf-sp-6);
    box-shadow: 0 2px 8px rgba(0,0,0,0.25);
    position: sticky;
    top: 0;
    z-index: 100;
}

.tf-topbar .tf-logo {
    display: flex;
    align-items: center;
    gap: var(--tf-sp-3);
    font-size: var(--tf-text-lg);
    font-weight: 700;
    color: #fff;
    text-decoration: none;
    letter-spacing: -0.02em;
}

.tf-topbar .tf-logo .tf-logo-icon {
    width: 32px;
    height: 32px;
    background: linear-gradient(135deg, var(--tf-amber) 0%, #F97316 100%);
    border-radius: var(--tf-radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: var(--tf-text-md);
}

.tf-topbar nav {
    display: flex;
    align-items: center;
    gap: var(--tf-sp-1);
    margin-left: var(--tf-sp-8);
}

.tf-topbar nav a {
    color: var(--tf-gray-400);
    text-decoration: none;
    font-size: var(--tf-text-sm);
    font-weight: 500;
    padding: var(--tf-sp-2) var(--tf-sp-3);
    border-radius: var(--tf-radius-sm);
    transition: all var(--tf-duration) var(--tf-ease);
}

.tf-topbar nav a:hover {
    color: #fff;
    background: rgba(255,255,255,0.08);
}

.tf-topbar nav a.active {
    color: var(--tf-amber);
    background: rgba(245,158,11,0.1);
}

.tf-topbar .tf-user {
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: var(--tf-sp-3);
    font-size: var(--tf-text-sm);
    color: var(--tf-gray-400);
}

.tf-topbar .tf-user a {
    color: var(--tf-gray-400);
    text-decoration: none;
    font-size: var(--tf-text-xs);
    padding: var(--tf-sp-1) var(--tf-sp-2);
    border: 1px solid var(--tf-gray-600);
    border-radius: var(--tf-radius-sm);
    transition: all var(--tf-duration) var(--tf-ease);
}

.tf-topbar .tf-user a:hover {
    color: #fff;
    border-color: var(--tf-gray-400);
}

/* ── Buttons (Unified) ──────────────────────────────────────── */
.tf-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: var(--tf-sp-2);
    padding: 10px 18px;
    font-family: var(--tf-font);
    font-size: var(--tf-text-sm);
    font-weight: 600;
    line-height: 1;
    border: 1px solid transparent;
    border-radius: var(--tf-radius);
    cursor: pointer;
    transition: all var(--tf-duration) var(--tf-ease);
    white-space: nowrap;
    text-decoration: none;
}

.tf-btn:active { transform: translateY(1px); }

.tf-btn-primary {
    background: var(--tf-blue);
    color: #fff;
    border-color: var(--tf-blue);
}
.tf-btn-primary:hover { background: #1D4ED8; border-color: #1D4ED8; }

.tf-btn-amber {
    background: var(--tf-amber);
    color: var(--tf-navy);
    border-color: var(--tf-amber);
}
.tf-btn-amber:hover { background: #E8920A; }

.tf-btn-success {
    background: var(--tf-success);
    color: #fff;
}
.tf-btn-success:hover { background: #047857; }

.tf-btn-danger {
    background: var(--tf-danger);
    color: #fff;
}
.tf-btn-danger:hover { background: #B91C1C; }

.tf-btn-outline {
    background: transparent;
    color: var(--tf-gray-600);
    border-color: var(--tf-border-dark);
}
.tf-btn-outline:hover { background: var(--tf-gray-50); color: var(--tf-gray-800); border-color: var(--tf-gray-400); }

.tf-btn-ghost {
    background: transparent;
    color: var(--tf-gray-600);
    border: none;
    padding: 8px 12px;
}
.tf-btn-ghost:hover { background: var(--tf-gray-100); color: var(--tf-gray-800); }

.tf-btn-sm {
    padding: 6px 12px;
    font-size: var(--tf-text-xs);
    border-radius: var(--tf-radius-sm);
}

.tf-btn-lg {
    padding: 12px 24px;
    font-size: var(--tf-text-base);
}

.tf-btn-icon {
    padding: 8px;
    min-width: 36px;
    min-height: 36px;
}

.tf-btn:disabled, .tf-btn.disabled {
    opacity: 0.5;
    cursor: not-allowed;
    pointer-events: none;
}

/* ── Form Elements (Unified) ────────────────────────────────── */
.tf-label {
    display: block;
    font-size: var(--tf-text-xs);
    font-weight: 600;
    color: var(--tf-gray-600);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: var(--tf-sp-1);
}

.tf-input, .tf-select, .tf-textarea {
    width: 100%;
    padding: 10px 12px;
    font-family: var(--tf-font);
    font-size: var(--tf-text-base);
    color: var(--tf-gray-800);
    background: #1E293B;
    border: 1px solid var(--tf-border);
    border-radius: var(--tf-radius);
    transition: all var(--tf-duration) var(--tf-ease);
    outline: none;
}

.tf-input:focus, .tf-select:focus, .tf-textarea:focus {
    border-color: var(--tf-blue-mid);
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
}

.tf-input::placeholder { color: var(--tf-gray-400); }

.tf-form-group {
    margin-bottom: var(--tf-sp-4);
}

/* ── Cards (Unified) ────────────────────────────────────────── */
.tf-card {
    background: var(--tf-surface);
    border: 1px solid var(--tf-border);
    border-radius: var(--tf-radius-lg);
    box-shadow: var(--tf-shadow-sm);
    overflow: hidden;
}

.tf-card-header {
    padding: var(--tf-sp-3) var(--tf-sp-4);
    font-size: var(--tf-text-sm);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    border-bottom: 1px solid var(--tf-border);
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--tf-gray-50);
    color: var(--tf-gray-700);
}

/* Card header accent colors (reduced from 6 to 4) */
.tf-card-header.accent-blue    { border-left: 4px solid var(--tf-blue); }
.tf-card-header.accent-amber   { border-left: 4px solid var(--tf-amber); }
.tf-card-header.accent-success { border-left: 4px solid var(--tf-success); }
.tf-card-header.accent-danger  { border-left: 4px solid var(--tf-danger); }

.tf-card-body {
    padding: var(--tf-sp-4);
}

/* ── Tables (Unified) ───────────────────────────────────────── */
.tf-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: var(--tf-text-sm);
}

.tf-table thead th {
    background: var(--tf-navy);
    color: #fff;
    font-weight: 600;
    font-size: var(--tf-text-xs);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    padding: var(--tf-sp-3) var(--tf-sp-4);
    text-align: left;
    white-space: nowrap;
    position: sticky;
    top: 0;
    z-index: 2;
}

.tf-table thead th:first-child { border-radius: var(--tf-radius) 0 0 0; }
.tf-table thead th:last-child  { border-radius: 0 var(--tf-radius) 0 0; }

.tf-table tbody td {
    padding: var(--tf-sp-3) var(--tf-sp-4);
    border-bottom: 1px solid var(--tf-gray-100);
    color: var(--tf-gray-700);
}

.tf-table tbody tr:hover td {
    background: var(--tf-blue-light);
}

.tf-table tbody tr:last-child td {
    border-bottom: none;
}

.tf-table .tf-table-total td {
    background: var(--tf-gray-50);
    font-weight: 700;
    color: var(--tf-gray-900);
    border-top: 2px solid var(--tf-border-dark);
}

.tf-table .tf-table-highlight td {
    background: var(--tf-amber-light);
    font-weight: 600;
    color: var(--tf-gray-900);
}

/* ── Badges ──────────────────────────────────────────────────── */
.tf-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 10px;
    font-size: var(--tf-text-xs);
    font-weight: 600;
    border-radius: 999px;
    white-space: nowrap;
}

.tf-badge-blue    { background: var(--tf-blue-light); color: var(--tf-blue); }
.tf-badge-amber   { background: var(--tf-amber-light); color: var(--tf-warning); }
.tf-badge-success { background: var(--tf-success-bg); color: var(--tf-success); }
.tf-badge-danger  { background: var(--tf-danger-bg); color: var(--tf-danger); }
.tf-badge-gray    { background: var(--tf-gray-100); color: var(--tf-gray-600); }

/* ── Alerts ──────────────────────────────────────────────────── */
.tf-alert {
    padding: var(--tf-sp-3) var(--tf-sp-4);
    border-radius: var(--tf-radius);
    font-size: var(--tf-text-sm);
    display: flex;
    align-items: flex-start;
    gap: var(--tf-sp-3);
    border-left: 4px solid;
}

.tf-alert-info    { background: var(--tf-info-bg); border-left-color: var(--tf-info); color: #0C4A6E; }
.tf-alert-success { background: var(--tf-success-bg); border-left-color: var(--tf-success); color: #064E3B; }
.tf-alert-warning { background: var(--tf-warning-bg); border-left-color: var(--tf-warning); color: #78350F; }
.tf-alert-danger  { background: var(--tf-danger-bg); border-left-color: var(--tf-danger); color: #7F1D1D; }

/* ── Spinner ─────────────────────────────────────────────────── */
.tf-spinner {
    display: none;
    width: 36px;
    height: 36px;
    border: 3px solid var(--tf-gray-200);
    border-top-color: var(--tf-blue-mid);
    border-radius: 50%;
    animation: tf-spin 0.7s ease-in-out infinite;
    margin: var(--tf-sp-4) auto;
}

@keyframes tf-spin { to { transform: rotate(360deg); } }

/* ── Modal ───────────────────────────────────────────────────── */
.tf-modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(4px);
    z-index: 1000;
    display: none;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 200ms var(--tf-ease);
}

.tf-modal-overlay.show {
    display: flex;
    opacity: 1;
}

.tf-modal {
    background: var(--tf-surface);
    border-radius: var(--tf-radius-xl);
    box-shadow: var(--tf-shadow-lg);
    max-width: 800px;
    width: 95%;
    max-height: 85vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

.tf-modal-header {
    padding: var(--tf-sp-5) var(--tf-sp-6);
    border-bottom: 1px solid var(--tf-border);
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.tf-modal-header h3 {
    font-size: var(--tf-text-lg);
    font-weight: 700;
    color: var(--tf-gray-900);
}

.tf-modal-body {
    padding: var(--tf-sp-6);
    overflow-y: auto;
    flex: 1;
}

.tf-modal-close {
    background: none;
    border: none;
    font-size: 1.25rem;
    color: var(--tf-gray-400);
    cursor: pointer;
    padding: var(--tf-sp-2);
    border-radius: var(--tf-radius-sm);
    transition: all var(--tf-duration) var(--tf-ease);
}

.tf-modal-close:hover { background: var(--tf-gray-100); color: var(--tf-gray-700); }

/* ── Stat Cards ──────────────────────────────────────────────── */
.tf-stat {
    background: var(--tf-surface);
    border: 1px solid var(--tf-border);
    border-radius: var(--tf-radius-lg);
    padding: var(--tf-sp-5);
    display: flex;
    align-items: center;
    gap: var(--tf-sp-4);
}

.tf-stat-icon {
    width: 44px;
    height: 44px;
    border-radius: var(--tf-radius);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    flex-shrink: 0;
}

.tf-stat-icon.blue   { background: var(--tf-blue-light); color: var(--tf-blue); }
.tf-stat-icon.amber  { background: var(--tf-amber-light); color: var(--tf-warning); }
.tf-stat-icon.green  { background: var(--tf-success-bg); color: var(--tf-success); }
.tf-stat-icon.red    { background: var(--tf-danger-bg); color: var(--tf-danger); }

.tf-stat-value {
    font-size: var(--tf-text-2xl);
    font-weight: 700;
    color: var(--tf-gray-900);
    line-height: 1.1;
}

.tf-stat-label {
    font-size: var(--tf-text-xs);
    color: var(--tf-gray-500);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    font-weight: 600;
}

/* ── Tabs ────────────────────────────────────────────────────── */
.tf-tabs {
    display: flex;
    gap: var(--tf-sp-1);
    border-bottom: 2px solid var(--tf-border);
    margin-bottom: var(--tf-sp-5);
}

.tf-tab {
    padding: var(--tf-sp-3) var(--tf-sp-4);
    font-size: var(--tf-text-sm);
    font-weight: 500;
    color: var(--tf-gray-500);
    background: none;
    border: none;
    cursor: pointer;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
    transition: all var(--tf-duration) var(--tf-ease);
}

.tf-tab:hover { color: var(--tf-gray-700); }

.tf-tab.active {
    color: var(--tf-blue);
    border-bottom-color: var(--tf-blue);
    font-weight: 600;
}

/* ── Utility Classes ─────────────────────────────────────────── */
.tf-flex        { display: flex; }
.tf-flex-col    { display: flex; flex-direction: column; }
.tf-items-center{ align-items: center; }
.tf-justify-between { justify-content: space-between; }
.tf-gap-2      { gap: var(--tf-sp-2); }
.tf-gap-3      { gap: var(--tf-sp-3); }
.tf-gap-4      { gap: var(--tf-sp-4); }
.tf-gap-6      { gap: var(--tf-sp-6); }
.tf-mt-4       { margin-top: var(--tf-sp-4); }
.tf-mt-6       { margin-top: var(--tf-sp-6); }
.tf-mb-4       { margin-bottom: var(--tf-sp-4); }
.tf-mb-6       { margin-bottom: var(--tf-sp-6); }
.tf-text-right { text-align: right; }
.tf-text-center{ text-align: center; }
.tf-text-muted { color: var(--tf-gray-500); }
.tf-truncate   { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.tf-sr-only    { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0,0,0,0); }

/* ── Responsive ──────────────────────────────────────────────── */
@media (max-width: 1024px) {
    .tf-topbar nav { gap: 0; }
    .tf-topbar nav a { padding: var(--tf-sp-2); font-size: var(--tf-text-xs); }
}

@media (max-width: 768px) {
    .tf-topbar { padding: 0 var(--tf-sp-3); height: 48px; }
    .tf-topbar nav { margin-left: var(--tf-sp-3); gap: 0; }
    .tf-topbar nav a { font-size: 11px; padding: 6px 8px; }
    .tf-topbar .tf-user span { display: none; }
}

/* ── Scrollbar Styling ───────────────────────────────────────── */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--tf-gray-300); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--tf-gray-400); }
"""
