"""
TitanForge v3.0 — Shared Navigation Component
===============================================
Unified sidebar navigation + breadcrumbs + global search.
Imported by every template to ensure consistent navigation.

Usage in templates:
    from templates.shared_nav import NAV_CSS, NAV_HTML, NAV_JS

    Then in the HTML:
    <style>  ... NAV_CSS ...  </style>
    ... NAV_HTML ...   (right after <body>)
    <script> ... NAV_JS ... </script>
"""

# ─────────────────────────────────────────────
# SIDEBAR CSS
# ─────────────────────────────────────────────

NAV_CSS = r"""
/* ── Sidebar Navigation ─────────────────────────────── */
.tf-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    width: 240px;
    background: var(--tf-navy, #0F172A);
    color: #fff;
    z-index: 200;
    display: flex;
    flex-direction: column;
    transition: transform 0.25s cubic-bezier(0.4,0,0.2,1), width 0.25s cubic-bezier(0.4,0,0.2,1);
    overflow: hidden;
}

.tf-sidebar.collapsed {
    width: 60px;
}

/* Logo area */
.tf-sidebar-logo {
    padding: 16px;
    display: flex;
    align-items: center;
    gap: 10px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    min-height: 56px;
    cursor: pointer;
    transition: padding 0.25s;
}

.tf-sidebar.collapsed .tf-sidebar-logo {
    padding: 16px 14px;
    justify-content: center;
}

.tf-sidebar-logo .logo-mark {
    width: 32px;
    height: 32px;
    min-width: 32px;
    background: linear-gradient(135deg, #F59E0B 0%, #F97316 100%);
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    font-weight: 800;
}

.tf-sidebar-logo .logo-text {
    font-size: 1.05rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    white-space: nowrap;
    opacity: 1;
    transition: opacity 0.2s;
}

.tf-sidebar.collapsed .logo-text { opacity: 0; width: 0; overflow: hidden; }

/* Search trigger */
.tf-sidebar-search {
    margin: 8px 12px;
    padding: 9px 12px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    color: rgba(255,255,255,0.45);
    font-size: 0.8rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: all 0.15s;
    white-space: nowrap;
    overflow: hidden;
}

.tf-sidebar-search:hover {
    background: rgba(255,255,255,0.1);
    color: rgba(255,255,255,0.7);
}

.tf-sidebar.collapsed .tf-sidebar-search span,
.tf-sidebar.collapsed .tf-sidebar-search kbd { display: none; }
.tf-sidebar.collapsed .tf-sidebar-search { justify-content: center; padding: 9px; margin: 8px 8px; }

.tf-sidebar-search kbd {
    margin-left: auto;
    background: rgba(255,255,255,0.1);
    padding: 1px 5px;
    border-radius: 3px;
    font-size: 10px;
    font-family: var(--tf-font);
}

/* Nav sections */
.tf-sidebar-nav {
    flex: 1;
    overflow-y: auto;
    padding: 8px 0;
}

.tf-sidebar-section {
    margin-bottom: 2px;
}

.tf-sidebar-section-label {
    padding: 8px 16px 4px;
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: rgba(255,255,255,0.3);
    white-space: nowrap;
    overflow: hidden;
}

/* Collapsible group header */
.tf-group-header {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 7px 12px;
    margin: 1px 8px;
    font-size: 0.78rem;
    font-weight: 600;
    color: rgba(255,255,255,0.55);
    cursor: pointer;
    border-radius: 6px;
    transition: background 0.15s, color 0.15s;
    user-select: none;
}
.tf-group-header:hover { background: rgba(255,255,255,0.06); color: rgba(255,255,255,0.85); }
.tf-group-header .gh-icon { font-size: 0.9rem; width: 20px; text-align: center; flex-shrink: 0; }
.tf-group-header .gh-label { flex: 1; white-space: nowrap; overflow: hidden; }
.tf-group-header .gh-chevron {
    font-size: 0.55rem; color: rgba(255,255,255,0.25); transition: transform 0.2s;
}
.tf-group-header.expanded .gh-chevron { transform: rotate(90deg); }
.tf-group-header.has-active { color: rgba(255,255,255,0.85); }
.tf-group-header.has-active .gh-icon { color: #F59E0B; }

/* Collapsible children container */
.tf-group-children {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.25s ease;
}
.tf-group-children.open { max-height: 600px; }

.tf-sidebar.collapsed .tf-sidebar-section-label { opacity: 0; height: 0; padding: 0; margin: 0; }
.tf-sidebar.collapsed .tf-group-header .gh-label,
.tf-sidebar.collapsed .tf-group-header .gh-chevron { display: none; }
.tf-sidebar.collapsed .tf-group-header { justify-content: center; padding: 7px 0; }
.tf-sidebar.collapsed .tf-group-children.open { max-height: 600px; }

.tf-nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px 16px;
    color: rgba(255,255,255,0.55);
    text-decoration: none;
    font-size: 0.85rem;
    font-weight: 500;
    border-radius: 0;
    margin: 1px 8px;
    border-radius: 6px;
    transition: all 0.15s;
    white-space: nowrap;
    position: relative;
}

.tf-nav-item:hover {
    background: rgba(255,255,255,0.08);
    color: rgba(255,255,255,0.9);
}

.tf-nav-item.active {
    background: rgba(30,64,175,0.35);
    color: #fff;
}

.tf-nav-item.active::before {
    content: '';
    position: absolute;
    left: -8px;
    top: 4px;
    bottom: 4px;
    width: 3px;
    border-radius: 0 3px 3px 0;
    background: #F59E0B;
}

.tf-nav-icon {
    width: 20px;
    min-width: 20px;
    text-align: center;
    font-size: 1rem;
    line-height: 1;
}

.tf-nav-label {
    opacity: 1;
    transition: opacity 0.2s;
}

.tf-sidebar.collapsed .tf-nav-label { opacity: 0; width: 0; overflow: hidden; }
.tf-sidebar.collapsed .tf-nav-item { justify-content: center; padding: 10px 8px; margin: 1px 6px; }

.tf-nav-badge {
    margin-left: auto;
    background: rgba(245,158,11,0.25);
    color: #F59E0B;
    padding: 1px 7px;
    border-radius: 10px;
    font-size: 0.7rem;
    font-weight: 600;
}

.tf-sidebar.collapsed .tf-nav-badge { display: none; }

/* Sidebar footer */
.tf-sidebar-footer {
    padding: 12px 16px;
    border-top: 1px solid rgba(255,255,255,0.08);
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.8rem;
}

.tf-sidebar-footer .user-avatar {
    width: 30px;
    height: 30px;
    min-width: 30px;
    border-radius: 50%;
    background: var(--tf-blue);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.75rem;
    color: #fff;
}

.tf-sidebar-footer .user-info {
    overflow: hidden;
    transition: opacity 0.2s;
}

.tf-sidebar.collapsed .tf-sidebar-footer .user-info { opacity: 0; width: 0; }
.tf-sidebar.collapsed .tf-sidebar-footer { justify-content: center; padding: 12px 8px; }

.tf-sidebar-footer .user-name {
    font-weight: 600;
    color: rgba(255,255,255,0.85);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.tf-sidebar-footer .user-role {
    font-size: 0.7rem;
    color: rgba(255,255,255,0.4);
    text-transform: capitalize;
}
.tf-logout-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: 6px;
    color: rgba(255,255,255,0.4);
    text-decoration: none;
    transition: all 0.2s ease;
    margin-left: auto;
    flex-shrink: 0;
}
.tf-logout-btn:hover {
    background: rgba(220,38,38,0.2);
    color: #f87171;
}
.tf-sidebar.collapsed .tf-logout-btn { display: none; }

/* Toggle button */
.tf-sidebar-toggle {
    position: absolute;
    top: 16px;
    right: -12px;
    width: 24px;
    height: 24px;
    background: var(--tf-navy, #0F172A);
    border: 2px solid rgba(255,255,255,0.15);
    border-radius: 50%;
    color: rgba(255,255,255,0.6);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    z-index: 201;
    transition: all 0.15s;
}

.tf-sidebar-toggle:hover {
    background: var(--tf-blue);
    color: #fff;
    border-color: var(--tf-blue);
}

/* ── Main Content Area (pushed by sidebar) ─── */
.tf-main {
    margin-left: 240px;
    min-height: 100vh;
    transition: margin-left 0.25s cubic-bezier(0.4,0,0.2,1);
}

.tf-sidebar.collapsed ~ .tf-main,
body.sidebar-collapsed .tf-main {
    margin-left: 60px;
}

/* ── Top Context Bar (replaces old topbar) ─── */
.tf-contextbar {
    background: #fff;
    border-bottom: 1px solid var(--tf-border);
    padding: 0 24px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 100;
}

.tf-breadcrumb {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.85rem;
    color: var(--tf-gray-500);
}

.tf-breadcrumb a {
    color: var(--tf-gray-500);
    text-decoration: none;
    transition: color 0.15s;
}

.tf-breadcrumb a:hover { color: var(--tf-blue); }
.tf-breadcrumb .bc-sep { color: var(--tf-gray-300); }
.tf-breadcrumb .bc-current { color: var(--tf-gray-800); font-weight: 600; }

.tf-contextbar-actions {
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ── Global Search Modal ─── */
.tf-search-overlay {
    position: fixed;
    inset: 0;
    background: rgba(15,23,42,0.5);
    backdrop-filter: blur(4px);
    z-index: 500;
    display: none;
    align-items: flex-start;
    justify-content: center;
    padding-top: 120px;
}

.tf-search-overlay.show { display: flex; }

.tf-search-box {
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.25);
    width: 560px;
    max-width: 95vw;
    overflow: hidden;
}

.tf-search-input-wrap {
    display: flex;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid var(--tf-border);
    gap: 10px;
}

.tf-search-input-wrap .search-icon { font-size: 1.1rem; color: var(--tf-gray-400); }

.tf-search-input {
    flex: 1;
    border: none;
    outline: none;
    font-size: 1rem;
    font-family: var(--tf-font);
    color: var(--tf-gray-800);
}

.tf-search-input::placeholder { color: var(--tf-gray-400); }

.tf-search-results {
    max-height: 360px;
    overflow-y: auto;
    padding: 8px;
}

.tf-search-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 12px;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.1s;
    text-decoration: none;
    color: inherit;
}

.tf-search-item:hover, .tf-search-item.focused { background: var(--tf-blue-light); }

.tf-search-item .si-icon {
    width: 36px;
    height: 36px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    flex-shrink: 0;
}

.tf-search-item .si-label { font-weight: 600; font-size: 0.85rem; color: var(--tf-gray-800); }
.tf-search-item .si-desc { font-size: 0.75rem; color: var(--tf-gray-500); }
.tf-search-item .si-kbd { margin-left: auto; font-size: 0.7rem; color: var(--tf-gray-400); }

.tf-search-footer {
    padding: 10px 16px;
    border-top: 1px solid var(--tf-border);
    font-size: 0.75rem;
    color: var(--tf-gray-400);
    display: flex;
    gap: 16px;
}

.tf-search-footer kbd {
    background: var(--tf-gray-100);
    padding: 1px 5px;
    border-radius: 3px;
    font-size: 10px;
}

/* ── Mobile responsive ─── */
@media (max-width: 768px) {
    .tf-sidebar {
        position: fixed !important;
        left: -280px;
        top: 0;
        height: 100vh;
        z-index: 1000;
        transition: left 0.3s ease;
        width: 260px;
        transform: none !important;
    }
    .tf-sidebar.mobile-open {
        left: 0;
    }
    .tf-sidebar.collapsed {
        left: -280px;
        width: 260px;
        transform: none !important;
    }
    .tf-sidebar.collapsed.mobile-open {
        left: 0;
        width: 260px;
    }
    .tf-main {
        margin-left: 0 !important;
        padding: 12px !important;
        padding-top: 56px !important;
    }
    .tf-main-content {
        margin-left: 0 !important;
        padding: 12px !important;
    }
    .tf-sidebar-toggle { display: none !important; }
    .tf-contextbar {
        padding: 0 12px 0 48px;
    }
    /* Fixed hamburger menu button for mobile */
    .mobile-menu-btn {
        display: block !important;
        position: fixed;
        top: 12px;
        left: 12px;
        z-index: 999;
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 8px 12px;
        color: #E2E8F0;
        font-size: 20px;
        cursor: pointer;
    }
    .mobile-overlay {
        display: block;
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.5);
        z-index: 999;
    }
    .tf-mobile-overlay {
        position: fixed; inset: 0; background: rgba(0,0,0,0.5);
        z-index: 999; display: none;
    }
    .tf-mobile-overlay.show { display: block; }

    /* Tables scroll horizontally on mobile */
    table { display: block; overflow-x: auto; -webkit-overflow-scrolling: touch; }
    /* Touch-friendly buttons */
    .btn, button:not(.tf-sidebar-toggle):not(.mobile-menu-btn):not(.tf-notif-bell):not(.tf-notif-mark-all):not(.tf-notif-read-btn) {
        min-height: 44px;
        min-width: 44px;
    }
    /* Cards stack vertically on mobile */
    .grid-2col, .grid-3col, [style*="grid-template-columns"] {
        grid-template-columns: 1fr !important;
    }
    /* Modals full-width on mobile */
    .modal-box, .tf-search-box { width: 95vw !important; max-height: 90vh; overflow-y: auto; }
    /* Form inputs bigger for touch (prevents iOS zoom) */
    input, select, textarea { font-size: 16px !important; }
    /* Search overlay adjustments for mobile */
    .tf-search-overlay { padding-top: 60px; }
    /* Notification dropdown full-width on mobile */
    .tf-notif-dropdown { width: 90vw; right: -60px; }
    /* XP Panel repositioning for mobile */
    #xpPanel { left: 8px !important; right: 8px !important; width: auto !important; bottom: 60px !important; }
}

@media (min-width: 769px) {
    .mobile-menu-btn { display: none !important; }
    .mobile-overlay { display: none !important; }
}

.tf-mobile-hamburger {
    display: none;
    background: none;
    border: none;
    font-size: 1.3rem;
    cursor: pointer;
    padding: 6px;
    color: var(--tf-gray-600);
    border-radius: 6px;
}

.tf-mobile-hamburger:hover { background: var(--tf-gray-100); }

/* ── Notification Bell ─────────────────────── */
.tf-notif-bell {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border-radius: 8px;
    cursor: pointer;
    color: rgba(255,255,255,0.55);
    transition: all 0.15s;
    border: none;
    background: none;
    font-size: 1.2rem;
}
.tf-notif-bell:hover {
    background: rgba(255,255,255,0.08);
    color: rgba(255,255,255,0.9);
}
.tf-notif-badge {
    position: absolute;
    top: 2px;
    right: 2px;
    min-width: 16px;
    height: 16px;
    padding: 0 4px;
    border-radius: 8px;
    background: #EF4444;
    color: #fff;
    font-size: 10px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    line-height: 1;
}
.tf-notif-badge.hidden { display: none; }
.tf-notif-dropdown {
    display: none;
    position: fixed;
    width: 360px;
    max-height: 440px;
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
    z-index: 500;
    overflow: hidden;
}
.tf-notif-dropdown.show { display: block; }
.tf-notif-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    border-bottom: 1px solid #334155;
}
.tf-notif-header h3 {
    margin: 0;
    font-size: 14px;
    color: #F8FAFC;
    font-weight: 700;
}
.tf-notif-mark-all {
    font-size: 11px;
    color: #60A5FA;
    cursor: pointer;
    background: none;
    border: none;
    font-weight: 600;
}
.tf-notif-mark-all:hover { text-decoration: underline; }
.tf-notif-list {
    overflow-y: auto;
    max-height: 360px;
    padding: 4px 0;
}
.tf-notif-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 10px 16px;
    transition: background 0.1s;
    cursor: default;
}
.tf-notif-item:hover { background: rgba(255,255,255,0.04); }
.tf-notif-item.unread { background: rgba(59,130,246,0.06); }
.tf-notif-icon {
    width: 32px;
    height: 32px;
    min-width: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    background: rgba(255,255,255,0.06);
}
.tf-notif-body { flex: 1; min-width: 0; }
.tf-notif-msg {
    font-size: 12px;
    color: #CBD5E1;
    line-height: 1.4;
}
.tf-notif-time {
    font-size: 10px;
    color: #64748B;
    margin-top: 2px;
}
.tf-notif-read-btn {
    background: none;
    border: none;
    color: #64748B;
    font-size: 14px;
    cursor: pointer;
    padding: 2px;
    border-radius: 4px;
    flex-shrink: 0;
    margin-top: 2px;
}
.tf-notif-read-btn:hover { color: #60A5FA; background: rgba(96,165,250,0.1); }
.tf-notif-empty {
    text-align: center;
    padding: 32px 16px;
    color: #64748B;
    font-size: 13px;
}
.tf-notif-wrap {
    position: relative;
    display: inline-flex;
}
"""

# ─────────────────────────────────────────────
# SIDEBAR HTML TEMPLATE
# ─────────────────────────────────────────────

# The {{ACTIVE_PAGE}} placeholder is replaced per-page.
# The {{JOB_CODE}} placeholder is replaced if in a project context.

NAV_HTML = r"""
<!-- Mobile hamburger button (fixed, visible only on mobile) -->
<button class="mobile-menu-btn" id="mobileMenuBtn" onclick="toggleMobileSidebar()" style="display:none;">&#9776;</button>
<!-- Mobile overlay -->
<div class="mobile-overlay" id="mobileOverlayFixed" onclick="toggleMobileSidebar()" style="display:none;"></div>
<div class="tf-mobile-overlay" id="mobileOverlay" onclick="closeMobileSidebar()"></div>

<!-- Sidebar -->
<aside class="tf-sidebar" id="tfSidebar">
    <button class="tf-sidebar-toggle" id="sidebarToggle" onclick="toggleSidebar()" title="Collapse sidebar">&#10094;</button>

    <a href="/" class="tf-sidebar-logo" style="text-decoration:none;color:#fff;">
        <div class="logo-mark">TF</div>
        <span class="logo-text">TitanForge</span>
    </a>

    <div class="tf-sidebar-search" onclick="openGlobalSearch()" title="Search (Ctrl+K)">
        <span style="font-size:0.9rem;">&#128269;</span>
        <span>Search...</span>
        <kbd>Ctrl+K</kbd>
    </div>

    <nav class="tf-sidebar-nav">
        <div class="tf-sidebar-section">
            <div class="tf-sidebar-section-label">Main</div>
            <a href="/" class="tf-nav-item {{ACTIVE_dashboard}}">
                <span class="tf-nav-icon">&#127968;</span>
                <span class="tf-nav-label">Dashboard</span>
            </a>
            <a href="/work-orders" class="tf-nav-item {{ACTIVE_workorders_global}}">
                <span class="tf-nav-icon">&#128203;</span>
                <span class="tf-nav-label">Work Orders</span>
            </a>
            <a href="/shop-floor" class="tf-nav-item {{ACTIVE_shopfloor}}">
                <span class="tf-nav-icon">&#9881;</span>
                <span class="tf-nav-label">Shop Floor</span>
            </a>
            <a href="/work-station/mine" class="tf-nav-item {{ACTIVE_myqueue}}">
                <span class="tf-nav-icon">&#128190;</span>
                <span class="tf-nav-label">My Queue</span>
            </a>
            <a href="/customers" class="tf-nav-item {{ACTIVE_customers}}">
                <span class="tf-nav-icon">&#128101;</span>
                <span class="tf-nav-label">Customers</span>
            </a>
        </div>

        <div class="tf-sidebar-section">
            <div class="tf-sidebar-section-label">Estimators</div>
            <a href="/sa" class="tf-nav-item {{ACTIVE_sa}}">
                <span class="tf-nav-icon">&#127959;</span>
                <span class="tf-nav-label">Structures America</span>
            </a>
            <a href="/tc" class="tf-nav-item {{ACTIVE_tc}}">
                <span class="tf-nav-icon">&#128663;</span>
                <span class="tf-nav-label">Titan Carports</span>
            </a>
        </div>

        <div class="tf-sidebar-section" id="projectNavSection" style="display:none;">
            <div class="tf-sidebar-section-label">Current Project</div>
            <a href="#" class="tf-nav-item {{ACTIVE_project}}" id="navProjectLink">
                <span class="tf-nav-icon">&#128194;</span>
                <span class="tf-nav-label" id="navProjectLabel">Project</span>
            </a>
            <a href="#" class="tf-nav-item {{ACTIVE_shopdrw}}" id="navShopDrwLink">
                <span class="tf-nav-icon">&#128208;</span>
                <span class="tf-nav-label">Shop Drawings</span>
            </a>
            <a href="#" class="tf-nav-item {{ACTIVE_workorders}}" id="navWorkOrdersLink">
                <span class="tf-nav-icon">&#128203;</span>
                <span class="tf-nav-label">Work Orders</span>
            </a>
            <a href="#" class="tf-nav-item {{ACTIVE_workstation}}" id="navWorkStationLink">
                <span class="tf-nav-icon">&#128241;</span>
                <span class="tf-nav-label">Work Station</span>
            </a>
            <a href="#" class="tf-nav-item {{ACTIVE_qc}}" id="navQCLink">
                <span class="tf-nav-icon">&#9989;</span>
                <span class="tf-nav-label">QC Dashboard</span>
            </a>
            <a href="#" class="tf-nav-item {{ACTIVE_quote}}" id="navQuoteLink">
                <span class="tf-nav-icon">&#128196;</span>
                <span class="tf-nav-label">Quote Editor</span>
            </a>
        </div>

        <div class="tf-sidebar-section">
            <div class="tf-sidebar-section-label">Admin</div>
            <a href="/admin" class="tf-nav-item {{ACTIVE_admin}}">
                <span class="tf-nav-icon">&#128274;</span>
                <span class="tf-nav-label">User Management</span>
            </a>
        </div>
    </nav>

    <!-- Notification Bell (positioned in sidebar footer area) -->
    <div style="padding:4px 12px 0;display:flex;justify-content:flex-end;">
        <div class="tf-notif-wrap" id="notifWrap">
            <button class="tf-notif-bell" onclick="toggleNotifDropdown()" title="Notifications">&#128276;</button>
            <span class="tf-notif-badge hidden" id="notifBadge">0</span>
            <div class="tf-notif-dropdown" id="notifDropdown">
                <div class="tf-notif-header">
                    <h3>Notifications</h3>
                    <button class="tf-notif-mark-all" onclick="markAllNotifRead()">Mark all read</button>
                </div>
                <div class="tf-notif-list" id="notifList">
                    <div class="tf-notif-empty">No notifications</div>
                </div>
                <div style="padding:8px 12px;border-top:1px solid #334155;text-align:center;">
                    <button onclick="clearAllNotifications()" style="background:none;border:1px solid #475569;color:#EF4444;font-size:11px;padding:4px 12px;border-radius:6px;cursor:pointer;font-weight:600;">Clear All</button>
                </div>
            </div>
        </div>
    </div>

    <div class="tf-sidebar-footer" style="flex-direction:column;align-items:stretch;gap:6px;padding:10px 12px;">
        <!-- XP Level Bar -->
        <div id="xpWidget" style="display:none;cursor:pointer;" onclick="toggleXPPanel()">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
                <div class="user-avatar" id="userAvatar" style="width:32px;height:32px;font-size:12px;">U</div>
                <div style="flex:1;min-width:0;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span class="user-name" id="userName" style="font-size:13px;">{{USER_NAME}}</span>
                        <span id="xpLevelBadge" style="font-size:10px;background:#f59e0b;color:#000;border-radius:10px;padding:1px 8px;font-weight:700;">Lv 1</span>
                    </div>
                    <div id="xpLevelName" style="font-size:10px;color:#94a3b8;margin-top:1px;">Apprentice</div>
                </div>
            </div>
            <div style="background:#1e293b;border-radius:6px;height:6px;overflow:hidden;margin-top:2px;">
                <div id="xpProgressBar" style="height:100%;background:linear-gradient(90deg,#f59e0b,#ef4444);width:0%;border-radius:6px;transition:width 0.8s ease;"></div>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:9px;color:#64748b;margin-top:2px;">
                <span id="xpProgressText">0 / 100 XP</span>
                <span id="xpStreakText" style="color:#f59e0b;"></span>
            </div>
        </div>
        <!-- Fallback for no-gamification -->
        <div id="xpFallback" style="display:flex;align-items:center;gap:8px;">
            <div class="user-avatar" id="userAvatarFb" style="width:32px;height:32px;font-size:12px;">U</div>
            <div class="user-info">
                <div class="user-name" id="userNameFb">{{USER_NAME}}</div>
                <div class="user-role" id="userRole">{{USER_ROLE}}</div>
            </div>
        </div>
    </div>
</aside>

<!-- XP Toast Notification -->
<div id="xpToast" style="position:fixed;bottom:24px;right:24px;z-index:10000;pointer-events:none;"></div>

<!-- XP Panel (achievements/leaderboard) -->
<div id="xpPanel" style="display:none;position:fixed;bottom:80px;left:200px;width:360px;max-height:480px;background:#1e293b;border:1px solid #334155;border-radius:12px;box-shadow:0 8px 32px rgba(0,0,0,0.5);z-index:9999;overflow-y:auto;color:#e2e8f0;">
    <div style="padding:16px;border-bottom:1px solid #334155;">
        <div style="display:flex;align-items:center;justify-content:space-between;">
            <h3 style="margin:0;font-size:16px;color:#f59e0b;">Your Profile</h3>
            <button onclick="toggleXPPanel()" style="background:none;border:none;color:#64748b;font-size:18px;cursor:pointer;">&times;</button>
        </div>
    </div>
    <div id="xpPanelContent" style="padding:16px;">Loading...</div>
</div>

<script>
// ── Gamification Widget ──
(function(){
    let xpPanelOpen = false;
    window.toggleXPPanel = function(){
        xpPanelOpen = !xpPanelOpen;
        document.getElementById('xpPanel').style.display = xpPanelOpen ? 'block' : 'none';
        if (xpPanelOpen) loadXPPanel();
    };

    async function loadGamification(){
        try {
            const resp = await fetch('/api/gamification/profile');
            const data = await resp.json();
            if (!data.ok) return;
            const p = data.profile;
            document.getElementById('xpWidget').style.display = 'block';
            document.getElementById('xpFallback').style.display = 'none';
            document.getElementById('xpLevelBadge').textContent = 'Lv ' + p.level;
            document.getElementById('xpLevelName').textContent = p.name;
            document.getElementById('xpProgressBar').style.width = p.progress_pct + '%';
            document.getElementById('xpProgressText').textContent = p.xp_in_level + ' / ' + p.xp_needed + ' XP';
            if (p.streak_days > 0) {
                document.getElementById('xpStreakText').textContent = p.streak_days + '-day streak ' + (p.streak_days >= 7 ? '🔥🔥' : p.streak_days >= 3 ? '🔥' : '✨');
            }
        } catch(e) { console.debug('Gamification load failed', e); }
    }

    window.showXPToast = function(xp, action, levelUp, newBadges) {
        const toast = document.getElementById('xpToast');
        const el = document.createElement('div');
        el.style.cssText = 'background:linear-gradient(135deg,#1e293b,#0f172a);border:1px solid #f59e0b;border-radius:12px;padding:12px 20px;margin-bottom:8px;display:flex;align-items:center;gap:10px;animation:xpSlideIn 0.4s ease,xpFadeOut 0.4s ease 2.6s forwards;box-shadow:0 4px 20px rgba(245,158,11,0.3);';
        let html = '<span style="font-size:24px;animation:xpBounce 0.5s ease;">⚡</span>';
        html += '<div><div style="color:#f59e0b;font-weight:700;font-size:14px;">+' + xp + ' XP</div>';
        html += '<div style="color:#94a3b8;font-size:11px;">' + action.replace(/_/g,' ') + '</div></div>';
        el.innerHTML = html;
        toast.appendChild(el);
        if (levelUp) {
            setTimeout(()=>{
                const lvl = document.createElement('div');
                lvl.style.cssText = 'background:linear-gradient(135deg,#f59e0b,#ef4444);border-radius:12px;padding:16px 24px;margin-bottom:8px;text-align:center;animation:xpSlideIn 0.4s ease,xpFadeOut 0.4s ease 3.6s forwards;box-shadow:0 4px 20px rgba(245,158,11,0.5);';
                lvl.innerHTML = '<div style="font-size:28px;margin-bottom:4px;">🎉</div><div style="color:#000;font-weight:800;font-size:16px;">LEVEL UP!</div>';
                toast.appendChild(lvl);
                setTimeout(()=>lvl.remove(), 4000);
            }, 500);
        }
        if (newBadges && newBadges.length) {
            newBadges.forEach((b,i)=>{
                setTimeout(()=>{
                    const badge = document.createElement('div');
                    badge.style.cssText = 'background:linear-gradient(135deg,#1e293b,#0f172a);border:1px solid #22c55e;border-radius:12px;padding:12px 20px;margin-bottom:8px;animation:xpSlideIn 0.4s ease,xpFadeOut 0.4s ease 3.6s forwards;box-shadow:0 4px 20px rgba(34,197,94,0.3);';
                    badge.innerHTML = '<div style="display:flex;align-items:center;gap:10px;"><span style="font-size:28px;">' + b.icon + '</span><div><div style="color:#22c55e;font-weight:700;">Achievement Unlocked!</div><div style="color:#e2e8f0;font-size:13px;">' + b.name + '</div></div></div>';
                    toast.appendChild(badge);
                    setTimeout(()=>badge.remove(), 4000);
                }, 800 * (i+1));
            });
        }
        setTimeout(()=>el.remove(), 3000);
        loadGamification(); // refresh bar
    };

    async function loadXPPanel(){
        const pc = document.getElementById('xpPanelContent');
        try {
            const [pResp, lResp, aResp] = await Promise.all([
                fetch('/api/gamification/profile').then(r=>r.json()),
                fetch('/api/gamification/leaderboard').then(r=>r.json()),
                fetch('/api/gamification/achievements').then(r=>r.json()),
            ]);
            let html = '';
            if (pResp.ok) {
                const p = pResp.profile;
                html += '<div style="text-align:center;margin-bottom:16px;">';
                html += '<div style="font-size:36px;font-weight:800;color:#f59e0b;">' + p.total_xp + ' XP</div>';
                html += '<div style="font-size:14px;color:#94a3b8;">Level ' + p.level + ' — ' + p.name + '</div>';
                if (p.streak_days > 0) html += '<div style="margin-top:4px;font-size:13px;color:#f59e0b;">' + (p.streak_days >= 7 ? '🔥🔥' : '🔥') + ' ' + p.streak_days + '-day streak</div>';
                html += '</div>';
            }
            if (aResp.ok) {
                html += '<div style="margin-bottom:16px;"><h4 style="margin:0 0 8px;font-size:13px;color:#94a3b8;text-transform:uppercase;letter-spacing:1px;">Achievements (' + aResp.earned_count + '/' + aResp.achievements.length + ')</h4>';
                html += '<div style="display:flex;flex-wrap:wrap;gap:6px;">';
                aResp.achievements.forEach(a=>{
                    const opacity = a.earned ? '1' : '0.3';
                    const bg = a.earned ? '#334155' : '#1e293b';
                    html += '<div title="' + a.name + ': ' + a.desc + '" style="background:' + bg + ';opacity:' + opacity + ';border-radius:8px;padding:6px 10px;font-size:12px;cursor:default;">' + a.icon + ' ' + a.name + '</div>';
                });
                html += '</div></div>';
            }
            if (lResp.ok && lResp.leaderboard.length) {
                html += '<h4 style="margin:0 0 8px;font-size:13px;color:#94a3b8;text-transform:uppercase;letter-spacing:1px;">Leaderboard</h4>';
                html += '<div style="display:flex;flex-direction:column;gap:4px;">';
                lResp.leaderboard.forEach(u=>{
                    const medal = u.rank===1?'🥇':u.rank===2?'🥈':u.rank===3?'🥉':'#'+u.rank;
                    html += '<div style="display:flex;align-items:center;gap:8px;background:#0f172a;border-radius:8px;padding:8px 12px;"><span style="font-size:16px;width:28px;text-align:center;">' + medal + '</span><div style="flex:1;"><div style="font-size:13px;font-weight:600;">' + u.username + '</div><div style="font-size:10px;color:#64748b;">' + u.level_name + '</div></div><div style="color:#f59e0b;font-weight:700;font-size:13px;">' + u.total_xp + ' XP</div></div>';
                });
                html += '</div>';
            }
            pc.innerHTML = html || '<p style="color:#64748b;">No data yet. Start working to earn XP!</p>';
        } catch(e) { pc.innerHTML = '<p style="color:#ef4444;">Failed to load</p>'; }
    }

    // Load on page ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', loadGamification);
    } else {
        loadGamification();
    }
})();
</script>
<style>
@keyframes xpSlideIn { from { transform: translateX(100px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
@keyframes xpFadeOut { from { opacity: 1; } to { opacity: 0; transform: translateY(-10px); } }
@keyframes xpBounce { 0%,100% { transform: scale(1); } 50% { transform: scale(1.3); } }
</style>

<!-- Global Search Modal -->
<div class="tf-search-overlay" id="searchOverlay" onclick="if(event.target===this)closeGlobalSearch()">
    <div class="tf-search-box">
        <div class="tf-search-input-wrap">
            <span class="search-icon">&#128269;</span>
            <input type="text" class="tf-search-input" id="globalSearchInput"
                   placeholder="Search projects, customers, tools..." autocomplete="off">
        </div>
        <div class="tf-search-results" id="searchResults">
            <div style="padding:20px;text-align:center;color:var(--tf-gray-400);font-size:0.85rem;">
                Type to search across projects, customers, and tools
            </div>
        </div>
        <div class="tf-search-footer">
            <span><kbd>&#8593;&#8595;</kbd> Navigate</span>
            <span><kbd>&#9166;</kbd> Open</span>
            <span><kbd>Esc</kbd> Close</span>
        </div>
    </div>
</div>
"""

# ─────────────────────────────────────────────
# NAV JAVASCRIPT
# ─────────────────────────────────────────────

NAV_JS = r"""
// ── Sidebar Toggle ──
function toggleSidebar() {
    const sb = document.getElementById('tfSidebar');
    sb.classList.toggle('collapsed');
    const btn = document.getElementById('sidebarToggle');
    btn.innerHTML = sb.classList.contains('collapsed') ? '&#10095;' : '&#10094;';
    document.body.classList.toggle('sidebar-collapsed', sb.classList.contains('collapsed'));
    localStorage.setItem('tf-sidebar-collapsed', sb.classList.contains('collapsed'));
}

// Restore sidebar state
(function() {
    if (localStorage.getItem('tf-sidebar-collapsed') === 'true') {
        const sb = document.getElementById('tfSidebar');
        if (sb) {
            sb.classList.add('collapsed');
            document.body.classList.add('sidebar-collapsed');
            const btn = document.getElementById('sidebarToggle');
            if (btn) btn.innerHTML = '&#10095;';
        }
    }
})();

// ── Collapsible Nav Groups ──
function toggleNavGroup(header) {
    var group = header.getAttribute('data-group');
    var children = document.querySelector('[data-group-children="' + group + '"]');
    if (!children) return;
    var isOpen = children.classList.contains('open');
    children.classList.toggle('open');
    header.classList.toggle('expanded');
    // Save state
    var state = JSON.parse(localStorage.getItem('tf-nav-groups') || '{}');
    state[group] = !isOpen;
    localStorage.setItem('tf-nav-groups', JSON.stringify(state));
}

// Restore nav group state from localStorage
(function() {
    var state = JSON.parse(localStorage.getItem('tf-nav-groups') || '{}');
    document.querySelectorAll('.tf-group-header').forEach(function(h) {
        var group = h.getAttribute('data-group');
        // If localStorage has a saved state, use it; otherwise keep server-rendered state (active sections open)
        if (group in state) {
            var children = document.querySelector('[data-group-children="' + group + '"]');
            if (children) {
                if (state[group]) {
                    children.classList.add('open');
                    h.classList.add('expanded');
                } else if (!h.classList.contains('has-active')) {
                    // Don't collapse if it has the active page
                    children.classList.remove('open');
                    h.classList.remove('expanded');
                }
            }
        }
    });
})();

// ── Mobile Sidebar ──
function toggleMobileSidebar() {
    const sb = document.querySelector('.tf-sidebar');
    const ov = document.getElementById('mobileOverlayFixed');
    const legacyOv = document.getElementById('mobileOverlay');
    if (sb.classList.contains('mobile-open')) {
        sb.classList.remove('mobile-open');
        if (ov) ov.style.display = 'none';
        if (legacyOv) legacyOv.classList.remove('show');
    } else {
        sb.classList.add('mobile-open');
        if (ov) ov.style.display = 'block';
        if (legacyOv) legacyOv.classList.add('show');
    }
}
function openMobileSidebar() {
    document.getElementById('tfSidebar').classList.add('mobile-open');
    document.getElementById('mobileOverlay').classList.add('show');
    var ov = document.getElementById('mobileOverlayFixed');
    if (ov) ov.style.display = 'block';
}
function closeMobileSidebar() {
    document.getElementById('tfSidebar').classList.remove('mobile-open');
    document.getElementById('mobileOverlay').classList.remove('show');
    var ov = document.getElementById('mobileOverlayFixed');
    if (ov) ov.style.display = 'none';
}

// ── Project Context ──
// Call this to show the "Current Project" section in the sidebar
function setProjectContext(jobCode) {
    if (!jobCode) return;
    const section = document.getElementById('projectNavSection');
    if (section) section.style.display = 'block';

    const setLink = (id, href, label) => {
        const el = document.getElementById(id);
        if (el) { el.href = href; if (label) { const lbl = el.querySelector('.tf-nav-label'); if (lbl) lbl.textContent = label; } }
    };

    setLink('navProjectLink', '/project/' + encodeURIComponent(jobCode), jobCode);
    setLink('navShopDrwLink', '/shop-drawings/' + encodeURIComponent(jobCode));
    setLink('navWorkOrdersLink', '/work-orders/' + encodeURIComponent(jobCode));
    setLink('navWorkStationLink', '/work-station/' + encodeURIComponent(jobCode));
    setLink('navQCLink', '/qc/' + encodeURIComponent(jobCode));
    setLink('navQuoteLink', '/quote/' + encodeURIComponent(jobCode));
}

// ── Global Search ──
function openGlobalSearch() {
    document.getElementById('searchOverlay').classList.add('show');
    setTimeout(() => document.getElementById('globalSearchInput').focus(), 100);
}

function closeGlobalSearch() {
    document.getElementById('searchOverlay').classList.remove('show');
    document.getElementById('globalSearchInput').value = '';
}

// Ctrl+K shortcut
document.addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const overlay = document.getElementById('searchOverlay');
        if (overlay.classList.contains('show')) {
            closeGlobalSearch();
        } else {
            openGlobalSearch();
        }
    }
    if (e.key === 'Escape') {
        closeGlobalSearch();
    }
});

// Search input handler (connects to /api/search if available)
document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('globalSearchInput');
    if (!input) return;

    let debounce = null;
    input.addEventListener('input', function() {
        clearTimeout(debounce);
        const q = input.value.trim();
        if (q.length < 2) {
            document.getElementById('searchResults').innerHTML =
                '<div style="padding:20px;text-align:center;color:var(--tf-gray-400);font-size:0.85rem;">Type to search across projects, customers, and tools</div>';
            return;
        }
        debounce = setTimeout(() => runGlobalSearch(q), 250);
    });

    input.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            const focused = document.querySelector('.tf-search-item.focused');
            if (focused) {
                window.location.href = focused.href || focused.getAttribute('data-href');
            } else {
                const q = input.value.trim();
                if (q.length >= 2) {
                    closeGlobalSearch();
                    window.location.href = '/search?q=' + encodeURIComponent(q);
                }
            }
        }
    });
});

async function runGlobalSearch(query) {
    const container = document.getElementById('searchResults');
    try {
        const resp = await fetch('/api/search?q=' + encodeURIComponent(query));
        const data = await resp.json();
        let html = '';
        const results = data.results || [];

        if (results.length === 0) {
            // Show quick nav links as fallback
            html = quickNavResults(query);
        } else {
            for (const r of results.slice(0, 8)) {
                const colors = {project:'#EFF6FF;color:#1E40AF', customer:'#ECFDF5;color:#059669', coil:'#FEF3C7;color:#92400E'};
                const icons = {project:'&#128194;', customer:'&#128101;', coil:'&#128230;'};
                html += '<a class="tf-search-item" href="' + (r.url || '#') + '">' +
                    '<div class="si-icon" style="background:' + (colors[r.type] || '#F1F5F9;color:#64748B') + '">' +
                    (icons[r.type] || '&#128196;') + '</div>' +
                    '<div><div class="si-label">' + escNavHtml(r.title || r.name || '') + '</div>' +
                    '<div class="si-desc">' + escNavHtml(r.subtitle || r.type || '') + '</div></div></a>';
            }
        }
        container.innerHTML = html || quickNavResults(query);
    } catch(e) {
        container.innerHTML = quickNavResults(query);
    }
}

function quickNavResults(query) {
    const q = query.toLowerCase();
    const links = [
        {label:'Dashboard', desc:'Home', icon:'&#127968;', href:'/', bg:'#EFF6FF;color:#1E40AF'},
        {label:'Shop Floor', desc:'Live fabrication tracking', icon:'&#9881;', href:'/shop-floor', bg:'#ECFDF5;color:#059669'},
        {label:'Customers', desc:'Customer database', icon:'&#128101;', href:'/customers', bg:'#FEF3C7;color:#92400E'},
        {label:'SA Estimator', desc:'Structures America calculator', icon:'&#127959;', href:'/sa', bg:'#EFF6FF;color:#1E40AF'},
        {label:'TC Estimator', desc:'Titan Carports calculator', icon:'&#128663;', href:'/tc', bg:'#F0F9FF;color:#0284C7'},
        {label:'Admin', desc:'User management', icon:'&#128274;', href:'/admin', bg:'#F1F5F9;color:#64748B'},
    ];
    const filtered = links.filter(l => l.label.toLowerCase().includes(q) || l.desc.toLowerCase().includes(q));
    if (filtered.length === 0) return '<div style="padding:20px;text-align:center;color:var(--tf-gray-400);font-size:0.85rem;">No results for "' + escNavHtml(query) + '"</div>';
    return filtered.map(l =>
        '<a class="tf-search-item" href="' + l.href + '">' +
        '<div class="si-icon" style="background:' + l.bg + '">' + l.icon + '</div>' +
        '<div><div class="si-label">' + l.label + '</div><div class="si-desc">' + l.desc + '</div></div></a>'
    ).join('');
}

function escNavHtml(s) {
    const d = document.createElement('div');
    d.textContent = s || '';
    return d.innerHTML;
}

// Set user avatar initials
(function() {
    const name = document.getElementById('userName');
    const avatar = document.getElementById('userAvatar');
    if (name && avatar && name.textContent) {
        const parts = name.textContent.trim().split(' ');
        avatar.textContent = parts.map(p => p[0]).join('').toUpperCase().slice(0,2) || 'U';
    }
})();

// ── Notification Bell System ──
(function(){
    let notifOpen = false;

    window.toggleNotifDropdown = function() {
        notifOpen = !notifOpen;
        const dd = document.getElementById('notifDropdown');
        if (dd) {
            dd.classList.toggle('show', notifOpen);
            if (notifOpen) {
                // Position the dropdown next to the bell, outside the sidebar
                const bell = document.querySelector('.tf-notif-bell');
                if (bell) {
                    const rect = bell.getBoundingClientRect();
                    const sidebar = document.getElementById('tfSidebar');
                    const sidebarRight = sidebar ? sidebar.getBoundingClientRect().right : rect.right;
                    dd.style.left = sidebarRight + 8 + 'px';
                    dd.style.bottom = (window.innerHeight - rect.bottom) + 'px';
                    dd.style.top = 'auto';
                    // On small screens, position it centered
                    if (window.innerWidth < 768) {
                        dd.style.left = '50%';
                        dd.style.transform = 'translateX(-50%)';
                        dd.style.bottom = (window.innerHeight - rect.top + 8) + 'px';
                    } else {
                        dd.style.transform = '';
                    }
                }
                loadNotifications();
            }
        }
    };

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        const wrap = document.getElementById('notifWrap');
        if (wrap && !wrap.contains(e.target)) {
            notifOpen = false;
            const dd = document.getElementById('notifDropdown');
            if (dd) dd.classList.remove('show');
        }
    });

    async function loadNotifications() {
        try {
            const resp = await fetch('/api/notifications');
            const data = await resp.json();
            if (!data.ok) return;
            renderNotifications(data.notifications || [], data.unread_count || 0);
        } catch(e) {
            console.debug('Notification load failed', e);
        }
    }

    function renderNotifications(notifs, unreadCount) {
        const badge = document.getElementById('notifBadge');
        if (badge) {
            if (unreadCount > 0) {
                badge.textContent = unreadCount > 99 ? '99+' : unreadCount;
                badge.classList.remove('hidden');
            } else {
                badge.classList.add('hidden');
            }
        }

        const list = document.getElementById('notifList');
        if (!list) return;

        if (notifs.length === 0) {
            list.innerHTML = '<div class="tf-notif-empty">No recent notifications</div>';
            return;
        }

        let html = '';
        for (const n of notifs) {
            const unread = n.is_read ? '' : ' unread';
            const icon = notifIcon(n.action || '');
            const ago = timeAgo(n.timestamp || n.created_at || '');
            html += '<div class="tf-notif-item' + unread + '" data-id="' + (n.id || '') + '">';
            html += '  <div class="tf-notif-icon">' + icon + '</div>';
            html += '  <div class="tf-notif-body">';
            html += '    <div class="tf-notif-msg">' + escNavHtml(n.message || formatNotifMsg(n)) + '</div>';
            html += '    <div class="tf-notif-time">' + ago + '</div>';
            html += '  </div>';
            if (!n.is_read) {
                html += '  <button class="tf-notif-read-btn" onclick="markNotifRead(\'' + (n.id || '') + '\', this)" title="Mark read">&#10003;</button>';
            }
            html += '</div>';
        }
        list.innerHTML = html;
    }

    function notifIcon(action) {
        const icons = {
            'qr_scan_start': '&#9654;',
            'qr_scan_finish': '&#10003;',
            'create_work_order': '&#128203;',
            'approve_work_order': '&#128077;',
            'generate_shop_drawing': '&#128208;',
            'update_item_status': '&#9881;',
            'create_project': '&#128194;',
            'add_customer': '&#128101;',
            'upload_document': '&#128196;',
            'qc_inspection': '&#128737;',
        };
        return icons[action] || '&#128276;';
    }

    function formatNotifMsg(n) {
        const user = n.user || 'Someone';
        const action = (n.action || '').replace(/_/g, ' ');
        const entity = n.entity_type ? (' on ' + n.entity_type.replace(/_/g, ' ')) : '';
        const eid = n.entity_id ? (' ' + n.entity_id) : '';
        return user + ' ' + action + entity + eid;
    }

    function timeAgo(ts) {
        if (!ts) return '';
        const d = new Date(ts);
        const now = new Date();
        const diff = Math.floor((now - d) / 1000);
        if (diff < 60) return 'just now';
        if (diff < 3600) return Math.floor(diff/60) + 'm ago';
        if (diff < 86400) return Math.floor(diff/3600) + 'h ago';
        if (diff < 604800) return Math.floor(diff/86400) + 'd ago';
        return d.toLocaleDateString();
    }

    window.markNotifRead = async function(id, btn) {
        try {
            await fetch('/api/notifications', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: 'mark_read', id: id})
            });
            if (btn) {
                const item = btn.closest('.tf-notif-item');
                if (item) item.classList.remove('unread');
                btn.remove();
            }
            // Refresh count
            loadNotifications();
        } catch(e) { console.debug('Mark read failed', e); }
    };

    window.markAllNotifRead = async function() {
        try {
            await fetch('/api/notifications', {
                method: 'PUT'
            });
            loadNotifications();
        } catch(e) { console.debug('Mark all read failed', e); }
    };

    window.clearAllNotifications = async function() {
        try {
            await fetch('/api/notifications', {
                method: 'DELETE'
            });
            loadNotifications();
            var dd = document.getElementById('notifDropdown');
            if (dd) dd.classList.remove('show');
        } catch(e) { console.debug('Clear all failed', e); }
    };

    // Poll notifications every 60 seconds + initial load
    function initNotif() {
        loadNotifications();
        setInterval(loadNotifications, 60000);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initNotif);
    } else {
        initNotif();
    }
})();
"""


# ─────────────────────────────────────────────
# HELPER: Build full nav for a page
# ─────────────────────────────────────────────

def inject_nav(html: str, active_page: str = "", job_code: str = "",
               user_name: str = "User", user_role: str = "admin",
               user_roles: list = None, request_path: str = "") -> str:
    """Inject sidebar navigation into an existing HTML page.

    This is the primary integration method. It:
      1. Adds NAV_CSS to the <style> or <head> section
      2. Adds sidebar HTML right after <body>
      3. Wraps existing content in <div class="tf-main">
      4. Removes old topbar if present
      5. Adds NAV_JS before </body>

    Works with any existing template — no template changes needed.
    """
    import re

    # If the HTML is a fragment (no <body> tag), wrap it in a full document
    # skeleton so the sidebar injection points (<body>, </body>) exist.
    if not re.search(r'<body[\s>]', html, re.IGNORECASE):
        # Extract any <style> blocks from the fragment to put in <head>
        style_blocks = []
        def _collect_style(m):
            style_blocks.append(m.group(0))
            return ''
        fragment = re.sub(r'<style[^>]*>.*?</style>', _collect_style, html, flags=re.DOTALL)
        styles = '\n'.join(style_blocks)
        html = (
            '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
            '<meta charset="UTF-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            '<title>TitanForge</title>\n'
            f'{styles}\n'
            '</head>\n<body>\n'
            f'{fragment}\n'
            '</body>\n</html>'
        )

    nav = build_nav(active_page, job_code, user_name, user_role, user_roles=user_roles,
                    request_path=request_path)

    # Prepend CSS to hide old nav elements across all templates
    hide_old = """
.tf-topbar { display: none !important; }
.topbar { display: none !important; }
#topbar { display: none !important; }
.navbar { display: none !important; }
.ws-topbar { display: none !important; }
#globalSearchOverlay { display: none !important; }
"""
    nav['css'] = hide_old + nav['css']

    # 1. Inject CSS before </style> or </head>
    if '</style>' in html:
        idx = html.rfind('</style>')
        html = html[:idx] + '\n' + nav['css'] + '\n</style>' + html[idx + 8:]
    elif '</head>' in html:
        html = html.replace('</head>', '<style>' + nav['css'] + '</style>\n</head>')

    # 3. Add sidebar HTML + wrap content in tf-main after <body>
    body_match = re.search(r'<body[^>]*>', html)
    if body_match:
        insert_pos = body_match.end()
        # Find the main content area to wrap
        html = (html[:insert_pos] +
                '\n' + nav['html'] +
                '\n<div class="tf-main">' +
                '\n<div class="tf-contextbar">' +
                '  <div class="tf-breadcrumb">' +
                '  </div>' +
                '  <div class="tf-contextbar-actions"></div>' +
                '</div>\n' +
                html[insert_pos:])

        # Close the tf-main div before </body>
        html = html.replace('</body>', '</div><!-- /tf-main -->\n</body>')

    # 4. Add JS before </body>
    html = html.replace('</body>',
                         '<script>' + nav['js'] + '</script>\n</body>')

    return html


def build_nav(active_page: str = "", job_code: str = "",
              user_name: str = "User", user_role: str = "admin",
              user_roles: list = None, request_path: str = "") -> dict:
    """Build nav component strings for a specific page.

    Args:
        active_page: One of: dashboard, shopfloor, customers, sa, tc,
                     project, shopdrw, workorders, workstation, qc, quote, admin
        job_code: If set, shows the project section in sidebar
        user_name: Display name
        user_role: User role (primary)
        user_roles: List of role IDs (new RBAC). Falls back to [user_role].

    Returns:
        dict with keys: css, html, js
    """
    # Build role-aware sidebar if the auth package is available
    sidebar_html = _build_role_sidebar(active_page, job_code, user_name, user_role, user_roles, request_path)

    # Project context JS
    context_js = ""
    if job_code:
        context_js = f"\nsetProjectContext('{job_code}');"

    return {
        "css": NAV_CSS,
        "html": sidebar_html,
        "js": NAV_JS + context_js,
    }


def _build_role_sidebar(active_page, job_code, user_name, user_role, user_roles, request_path=""):
    """Build sidebar HTML dynamically from user's RBAC roles.

    Uses perm.get_sidebar() from auth.permissions to get the role-filtered
    sidebar sections defined in auth/roles.py, then renders them as HTML.
    Falls back to the static NAV_HTML if the auth module is not available.
    """
    # Try to use new auth system
    perm = None
    try:
        from auth.permissions import merge_permissions
        roles = user_roles or [user_role]
        perm = merge_permissions(roles)
    except ImportError:
        perm = None

    # If auth not available, fall back to static NAV_HTML
    if not perm:
        html = NAV_HTML
        pages = ["dashboard", "workorders_global", "shopfloor", "myqueue", "customers", "sa", "tc",
                 "project", "shopdrw", "workorders", "workstation", "qc", "quote", "admin"]
        for p in pages:
            html = html.replace("{{ACTIVE_" + p + "}}", "active" if p == active_page else "")
        html = html.replace("{{USER_NAME}}", user_name)
        html = html.replace("{{USER_ROLE}}", user_role)
        return html

    # ── Build dynamic sidebar from role-filtered sections ──

    # Icon mapping: sidebar section icon name -> HTML entity
    ICON_MAP = {
        "home":           "&#127968;",
        "calculator":     "&#127959;",
        "folder":         "&#128194;",
        "factory":        "&#9881;",
        "shield-check":   "&#128737;",
        "package":        "&#128230;",
        "shopping-cart":  "&#128722;",
        "truck":          "&#128666;",
        "hard-hat":       "&#127959;",
        "alert-triangle": "&#9888;",
        "dollar-sign":    "&#128176;",
        "trending-up":    "&#128200;",
        "settings":       "&#128274;",
        "cpu":            "&#128190;",
        "flame":          "&#128293;",
        "clipboard":      "&#128203;",
        "eye":            "&#128065;",
        "calendar":       "&#128197;",
        "bar-chart":      "&#128200;",
        "file-text":      "&#128196;",
        "users":          "&#128101;",
    }

    # Role display labels
    role_labels = []
    for r in (user_roles or [user_role]):
        role_labels.append(r.replace("_", " ").title())
    role_display = " + ".join(role_labels) if role_labels else user_role.replace("_", " ").title()

    # Get role-filtered sidebar sections from the permission system
    sidebar_sections = perm.get_sidebar()

    # ── Render sidebar sections to HTML ──
    nav_items_html = ""
    for section in sidebar_sections:
        sid = section.get("id", "")
        label = section.get("label", "")
        icon_name = section.get("icon", "")
        icon_html = ICON_MAP.get(icon_name, "&#128194;")
        children = section.get("children", [])
        url = section.get("url", "")

        nav_items_html += '        <div class="tf-sidebar-section">\n'

        if children:
            # Check if any child is active (to auto-expand)
            has_active = any(_is_nav_active(c.get("url", ""), active_page, request_path) for c in children)
            expanded_cls = " expanded" if has_active else ""
            active_hdr = " has-active" if has_active else ""
            open_cls = " open" if has_active else ""

            # Collapsible group header
            nav_items_html += f'            <div class="tf-group-header{expanded_cls}{active_hdr}" data-group="{sid}" onclick="toggleNavGroup(this)">\n'
            nav_items_html += f'                <span class="gh-icon">{icon_html}</span>\n'
            nav_items_html += f'                <span class="gh-label">{label}</span>\n'
            nav_items_html += f'                <span class="gh-chevron">&#9654;</span>\n'
            nav_items_html += f'            </div>\n'

            # Children container
            nav_items_html += f'            <div class="tf-group-children{open_cls}" data-group-children="{sid}">\n'
            for child in children:
                child_url = child.get("url", "#")
                child_label = child.get("label", "")
                is_active = _is_nav_active(child_url, active_page, request_path)
                active_cls = " active" if is_active else ""
                nav_items_html += f'              <a href="{child_url}" class="tf-nav-item{active_cls}">\n'
                nav_items_html += f'                  <span class="tf-nav-icon">{icon_html}</span>\n'
                nav_items_html += f'                  <span class="tf-nav-label">{child_label}</span>\n'
                nav_items_html += f'              </a>\n'
            nav_items_html += f'            </div>\n'
        elif url:
            # Single-link section (e.g., Dashboard)
            is_active = _is_nav_active(url, active_page, request_path)
            active_cls = " active" if is_active else ""
            nav_items_html += f'            <a href="{url}" class="tf-nav-item{active_cls}">\n'
            nav_items_html += f'                <span class="tf-nav-icon">{icon_html}</span>\n'
            nav_items_html += f'                <span class="tf-nav-label">{label}</span>\n'
            nav_items_html += f'            </a>\n'

        nav_items_html += '        </div>\n'

    # Current Project (context-aware — shown when in a project page)
    project_section = """
        <div class="tf-sidebar-section" id="projectNavSection" style="display:none;">
            <div class="tf-sidebar-section-label">Current Project</div>
            <a href="#" class="tf-nav-item" id="navProjectLink">
                <span class="tf-nav-icon">&#128194;</span>
                <span class="tf-nav-label" id="navProjectLabel">Project</span>
            </a>"""
    if perm.can("view_shop_drawings"):
        project_section += """
            <a href="#" class="tf-nav-item" id="navShopDrwLink">
                <span class="tf-nav-icon">&#128208;</span>
                <span class="tf-nav-label">Shop Drawings</span>
            </a>"""
    if perm.can("view_work_orders") or perm.can("view_own_work_items"):
        project_section += """
            <a href="#" class="tf-nav-item" id="navWorkOrdersLink">
                <span class="tf-nav-icon">&#128203;</span>
                <span class="tf-nav-label">Work Orders</span>
            </a>
            <a href="#" class="tf-nav-item" id="navWorkStationLink">
                <span class="tf-nav-icon">&#128241;</span>
                <span class="tf-nav-label">Work Station</span>
            </a>"""
    if perm.can("view_qc"):
        project_section += """
            <a href="#" class="tf-nav-item" id="navQCLink">
                <span class="tf-nav-icon">&#9989;</span>
                <span class="tf-nav-label">QC Dashboard</span>
            </a>"""
    if perm.can("create_quotes") or perm.can("view_quotes"):
        project_section += """
            <a href="#" class="tf-nav-item" id="navQuoteLink">
                <span class="tf-nav-icon">&#128196;</span>
                <span class="tf-nav-label">Quote Editor</span>
            </a>"""
    project_section += "\n        </div>"

    nav_items_html += project_section

    # ── Assemble the full sidebar HTML ──
    sidebar = f"""
<!-- Mobile hamburger button (fixed, visible only on mobile) -->
<button class="mobile-menu-btn" id="mobileMenuBtn" onclick="toggleMobileSidebar()" style="display:none;">&#9776;</button>
<!-- Mobile overlay -->
<div class="mobile-overlay" id="mobileOverlayFixed" onclick="toggleMobileSidebar()" style="display:none;"></div>
<div class="tf-mobile-overlay" id="mobileOverlay" onclick="closeMobileSidebar()"></div>

<!-- Sidebar -->
<aside class="tf-sidebar" id="tfSidebar">
    <button class="tf-sidebar-toggle" id="sidebarToggle" onclick="toggleSidebar()" title="Collapse sidebar">&#10094;</button>

    <a href="/" class="tf-sidebar-logo" style="text-decoration:none;color:#fff;">
        <div class="logo-mark">TF</div>
        <span class="logo-text">TitanForge</span>
    </a>

    <div class="tf-sidebar-search" onclick="openGlobalSearch()" title="Search (Ctrl+K)">
        <span style="font-size:0.9rem;">&#128269;</span>
        <span>Search...</span>
        <kbd>Ctrl+K</kbd>
    </div>

    <nav class="tf-sidebar-nav">
{nav_items_html}
    </nav>

    <!-- Notification Bell -->
    <div style="padding:4px 12px 0;display:flex;justify-content:flex-end;">
        <div class="tf-notif-wrap" id="notifWrap">
            <button class="tf-notif-bell" onclick="toggleNotifDropdown()" title="Notifications">&#128276;</button>
            <span class="tf-notif-badge hidden" id="notifBadge">0</span>
            <div class="tf-notif-dropdown" id="notifDropdown">
                <div class="tf-notif-header">
                    <h3>Notifications</h3>
                    <button class="tf-notif-mark-all" onclick="markAllNotifRead()">Mark all read</button>
                </div>
                <div class="tf-notif-list" id="notifList">
                    <div class="tf-notif-empty">No notifications</div>
                </div>
                <div style="padding:8px 12px;border-top:1px solid #334155;text-align:center;">
                    <button onclick="clearAllNotifications()" style="background:none;border:1px solid #475569;color:#EF4444;font-size:11px;padding:4px 12px;border-radius:6px;cursor:pointer;font-weight:600;">Clear All</button>
                </div>
            </div>
        </div>
    </div>

    <div class="tf-sidebar-footer" style="flex-direction:column;align-items:stretch;gap:6px;padding:10px 12px;">
        <!-- XP Level Bar -->
        <div id="xpWidget" style="display:none;cursor:pointer;" onclick="toggleXPPanel()">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
                <div class="user-avatar" id="userAvatar" style="width:32px;height:32px;font-size:12px;">{user_name[0:1].upper()}</div>
                <div style="flex:1;min-width:0;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span class="user-name" id="userName" style="font-size:13px;">{user_name}</span>
                        <span id="xpLevelBadge" style="font-size:10px;background:#f59e0b;color:#000;border-radius:10px;padding:1px 8px;font-weight:700;">Lv 1</span>
                    </div>
                    <div id="xpLevelName" style="font-size:10px;color:#94a3b8;margin-top:1px;">Apprentice</div>
                </div>
            </div>
            <div style="background:#1e293b;border-radius:6px;height:6px;overflow:hidden;margin-top:2px;">
                <div id="xpProgressBar" style="height:100%;background:linear-gradient(90deg,#f59e0b,#ef4444);width:0%;border-radius:6px;transition:width 0.8s ease;"></div>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:9px;color:#64748b;margin-top:2px;">
                <span id="xpProgressText">0 / 100 XP</span>
                <span id="xpStreakText" style="color:#f59e0b;"></span>
            </div>
        </div>
        <!-- Fallback for no-gamification -->
        <div id="xpFallback" style="display:flex;align-items:center;gap:8px;">
            <div class="user-avatar" id="userAvatarFb" style="width:32px;height:32px;font-size:12px;">{user_name[0:1].upper()}</div>
            <div class="user-info">
                <div class="user-name" id="userNameFb">{user_name}</div>
                <div class="user-role" id="userRole">{role_display}</div>
            </div>
            <a href="/auth/logout" class="tf-logout-btn" title="Logout" onclick="return confirm('Are you sure you want to logout?')" style="margin-left:auto;">
                <span style="font-size:16px;">&#9211;</span>
            </a>
        </div>
    </div>
</aside>

<!-- XP Toast Notification -->
<div id="xpToast" style="position:fixed;bottom:24px;right:24px;z-index:10000;pointer-events:none;"></div>

<!-- XP Panel (achievements/leaderboard) -->
<div id="xpPanel" style="display:none;position:fixed;bottom:80px;left:200px;width:360px;max-height:480px;background:#1e293b;border:1px solid #334155;border-radius:12px;box-shadow:0 8px 32px rgba(0,0,0,0.5);z-index:9999;overflow-y:auto;color:#e2e8f0;">
    <div style="padding:16px;border-bottom:1px solid #334155;">
        <div style="display:flex;align-items:center;justify-content:space-between;">
            <h3 style="margin:0;font-size:16px;color:#f59e0b;">Your Profile</h3>
            <button onclick="toggleXPPanel()" style="background:none;border:none;color:#64748b;font-size:18px;cursor:pointer;">&times;</button>
        </div>
    </div>
    <div id="xpPanelContent" style="padding:16px;">Loading...</div>
</div>

<!-- Global Search Modal -->
<div class="tf-search-overlay" id="searchOverlay" onclick="if(event.target===this)closeGlobalSearch()">
    <div class="tf-search-box">
        <div class="tf-search-input-wrap">
            <span class="search-icon">&#128269;</span>
            <input type="text" class="tf-search-input" id="globalSearchInput"
                   placeholder="Search projects, customers, tools..." autocomplete="off">
        </div>
        <div class="tf-search-results" id="searchResults">
            <div style="padding:20px;text-align:center;color:var(--tf-gray-400);font-size:0.85rem;">
                Type to search across projects, customers, and tools
            </div>
        </div>
        <div class="tf-search-footer">
            <span><kbd>&#8593;&#8595;</kbd> Navigate</span>
            <span><kbd>&#9166;</kbd> Open</span>
            <span><kbd>Esc</kbd> Close</span>
        </div>
    </div>
</div>
"""
    return sidebar


def _is_nav_active(url: str, active_page: str, request_path: str = "") -> bool:
    """Determine if a nav link should be highlighted as active.

    Uses exact URL matching — only the nav item whose URL matches the
    active_page identifier (or its mapped URLs) gets highlighted.
    The active_page value can be either a known key or a raw URL path.
    request_path is the actual browser URL path for precise matching.
    """
    _ACTIVE_MAP = {
        "dashboard":         ["/dashboard", "/"],
        "shopfloor":         ["/shop-floor"],
        "workorders_global": ["/work-orders"],
        "customers":         ["/customers"],
        "sa":                ["/sa"],
        "tc":                ["/tc"],
        "admin":             ["/admin"],
        "qc":                ["/qc"],
        "inventory":         ["/inventory"],
        "shipping":          ["/shipping"],
        "schedule":          ["/schedule"],
        "documents":         ["/documents"],
        "field":             ["/field"],
        "reports":           ["/reports"],
        "projects":          ["/projects"],
        "workstation":       ["/work-station"],
        "shopdrw":           ["/shop-drawings"],
    }
    if not active_page and not request_path:
        return False

    # Normalise: strip trailing slash from path portion only
    url_path = url.split("?")[0].rstrip("/") if url else ""
    url_qs   = url.split("?", 1)[1] if url and "?" in url else ""
    ap_clean = active_page.split("?")[0].rstrip("/") if active_page else ""
    rp_path  = request_path.split("?")[0].rstrip("/") if request_path else ""
    rp_qs    = request_path.split("?", 1)[1] if request_path and "?" in request_path else ""

    # Best match: compare nav item URL against the actual browser request path
    # For URLs with query strings (e.g. /inventory?type=coils), require both
    # path AND query string to match so only one child highlights.
    if url_path and rp_path and url_path == rp_path:
        if url_qs:
            # Nav item has a query string — require it to match request
            if url_qs == rp_qs:
                return True
        else:
            # Nav item has no query string — path match is enough
            if not rp_qs:
                return True

    # Direct match: active_page is a URL that matches this nav item
    if url_path and ap_clean and (url_path == ap_clean or url == active_page):
        # If the nav URL has a query string, only match if active_page also has it
        if url_qs:
            ap_qs = active_page.split("?", 1)[1] if "?" in active_page else ""
            if url_qs == ap_qs:
                return True
        else:
            return True

    # Map-based match: active_page is a known key, use EXACT url matching
    # Skip if the nav URL has a query string — query-param children should
    # only match via request_path (handled above), not via the broad map key.
    if not url_qs:
        active_urls = _ACTIVE_MAP.get(active_page, [])
        for pattern in active_urls:
            pattern_clean = pattern.rstrip("/")
            if url_path == pattern_clean:
                return True

    return False
