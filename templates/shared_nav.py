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

NAV_CSS = """
/* ── Sidebar Navigation ─────────────────────────────── */
.tf-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    width: 240px;
    background: var(--tf-navy);
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
    margin-bottom: 4px;
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

.tf-sidebar.collapsed .tf-sidebar-section-label { opacity: 0; height: 0; padding: 0; margin: 0; }

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

/* Toggle button */
.tf-sidebar-toggle {
    position: absolute;
    top: 16px;
    right: -12px;
    width: 24px;
    height: 24px;
    background: var(--tf-navy);
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
        transform: translateX(-100%);
        width: 260px;
    }
    .tf-sidebar.mobile-open { transform: translateX(0); }
    .tf-sidebar.collapsed { transform: translateX(-100%); }
    .tf-main { margin-left: 0 !important; }
    .tf-sidebar-toggle { display: none; }
    .tf-mobile-hamburger { display: flex !important; }
    .tf-mobile-overlay {
        position: fixed; inset: 0; background: rgba(0,0,0,0.4);
        z-index: 199; display: none;
    }
    .tf-mobile-overlay.show { display: block; }
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
"""

# ─────────────────────────────────────────────
# SIDEBAR HTML TEMPLATE
# ─────────────────────────────────────────────

# The {{ACTIVE_PAGE}} placeholder is replaced per-page.
# The {{JOB_CODE}} placeholder is replaced if in a project context.

NAV_HTML = """
<!-- Mobile overlay -->
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
            <a href="/shop-floor" class="tf-nav-item {{ACTIVE_shopfloor}}">
                <span class="tf-nav-icon">&#9881;</span>
                <span class="tf-nav-label">Shop Floor</span>
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
            <a href="#" class="tf-nav-item {{ACTIVE_shipping}}" id="navShippingLink2">
                <span class="tf-nav-icon">&#128666;</span>
                <span class="tf-nav-label">Shipping</span>
            </a>
        </div>

        <div class="tf-sidebar-section">
            <div class="tf-sidebar-section-label">Shipping</div>
            <a href="#" class="tf-nav-item {{ACTIVE_shipping}}" id="navShippingLink" onclick="var jc=localStorage.getItem('tf_current_job');if(jc)location.href='/shipping/'+jc;else alert('Open a project first');return false;">
                <span class="tf-nav-icon">&#128666;</span>
                <span class="tf-nav-label">Shipping Hub</span>
            </a>
            <a href="/schedule" class="tf-nav-item {{ACTIVE_schedule}}">
                <span class="tf-nav-icon">&#128197;</span>
                <span class="tf-nav-label">Production Schedule</span>
            </a>
        </div>

        <div class="tf-sidebar-section">
            <div class="tf-sidebar-section-label">Inventory</div>
            <a href="/inventory" class="tf-nav-item {{ACTIVE_inventory}}">
                <span class="tf-nav-icon">&#128230;</span>
                <span class="tf-nav-label">Coil Inventory</span>
            </a>
            <a href="/inventory/traceability" class="tf-nav-item {{ACTIVE_traceability}}">
                <span class="tf-nav-icon">&#128279;</span>
                <span class="tf-nav-label">Traceability</span>
            </a>
        </div>

        <div class="tf-sidebar-section">
            <div class="tf-sidebar-section-label">QA / QC</div>
            <a href="/qa" class="tf-nav-item {{ACTIVE_qa}}">
                <span class="tf-nav-icon">&#128203;</span>
                <span class="tf-nav-label">QA/QC Hub</span>
            </a>
            <a href="/qa/wps" class="tf-nav-item {{ACTIVE_wps}}">
                <span class="tf-nav-icon">&#128293;</span>
                <span class="tf-nav-label">WPS Library</span>
            </a>
            <a href="/qa/welder-certs" class="tf-nav-item {{ACTIVE_weldercerts}}">
                <span class="tf-nav-icon">&#127891;</span>
                <span class="tf-nav-label">Welder Certs</span>
            </a>
            <a href="/qa/procedures" class="tf-nav-item {{ACTIVE_procedures}}">
                <span class="tf-nav-icon">&#128220;</span>
                <span class="tf-nav-label">Procedures</span>
            </a>
            <a href="/qa/ncr-log" class="tf-nav-item {{ACTIVE_ncrlog}}">
                <span class="tf-nav-icon">&#9888;</span>
                <span class="tf-nav-label">NCR Log</span>
            </a>
            <a href="/qa/calibration" class="tf-nav-item {{ACTIVE_calibration}}">
                <span class="tf-nav-icon">&#128295;</span>
                <span class="tf-nav-label">Calibration Log</span>
            </a>
        </div>

        <div class="tf-sidebar-section">
            <div class="tf-sidebar-section-label">Help</div>
            <a href="/getting-started" class="tf-nav-item {{ACTIVE_gettingstarted}}">
                <span class="tf-nav-icon">&#128218;</span>
                <span class="tf-nav-label">Getting Started</span>
            </a>
        </div>

        <div class="tf-sidebar-section">
            <div class="tf-sidebar-section-label">Admin</div>
            <a href="/admin" class="tf-nav-item {{ACTIVE_admin}}">
                <span class="tf-nav-icon">&#128274;</span>
                <span class="tf-nav-label">User Management</span>
            </a>
            <a href="/tv-dashboard" class="tf-nav-item {{ACTIVE_tvdash}}">
                <span class="tf-nav-icon">&#128250;</span>
                <span class="tf-nav-label">TV Dashboard</span>
            </a>
        </div>
    </nav>

    <div class="tf-sidebar-footer">
        <div class="user-avatar" id="userAvatar">U</div>
        <div class="user-info">
            <div class="user-name" id="userName">{{USER_NAME}}</div>
            <div class="user-role" id="userRole">{{USER_ROLE}}</div>
        </div>
    </div>
</aside>

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

NAV_JS = """
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

// ── Mobile Sidebar ──
function openMobileSidebar() {
    document.getElementById('tfSidebar').classList.add('mobile-open');
    document.getElementById('mobileOverlay').classList.add('show');
}
function closeMobileSidebar() {
    document.getElementById('tfSidebar').classList.remove('mobile-open');
    document.getElementById('mobileOverlay').classList.remove('show');
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
    setLink('navShippingLink2', '/shipping/' + encodeURIComponent(jobCode));
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
            if (focused) { window.location.href = focused.href || focused.getAttribute('data-href'); }
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
"""


# ─────────────────────────────────────────────
# HELPER: Build full nav for a page
# ─────────────────────────────────────────────

def inject_nav(html: str, active_page: str = "", job_code: str = "",
               user_name: str = "User", user_role: str = "admin") -> str:
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
    nav = build_nav(active_page, job_code, user_name, user_role)

    # Prepend CSS to hide old nav elements across all templates
    # Also ensure --tf-navy is defined (some pages only define --tf-dark)
    hide_old = """
:root { --tf-navy: #0F172A; --tf-navy-light: #1E293B; }
.tf-topbar { display: none !important; }
.topbar { display: none !important; }
.navbar { display: none !important; }
.ws-topbar { display: none !important; }
#topbar { display: none !important; }
#tabs { display: none !important; }
#globalSearchOverlay { display: none !important; }
/* Fix layout height when old topbar/tabs are hidden */
#main { height: calc(100vh - 48px) !important; margin-top: 0 !important; }
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
                '    <button class="tf-mobile-hamburger" onclick="openMobileSidebar()">&#9776;</button>' +
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
              user_name: str = "User", user_role: str = "admin") -> dict:
    """Build nav component strings for a specific page.

    Args:
        active_page: One of: dashboard, shopfloor, customers, sa, tc,
                     project, shopdrw, workorders, workstation, qc, quote, admin
        job_code: If set, shows the project section in sidebar
        user_name: Display name
        user_role: User role

    Returns:
        dict with keys: css, html, js, context_bar_html
    """
    # Set active classes
    html = NAV_HTML
    pages = ["dashboard", "shopfloor", "customers", "sa", "tc",
             "project", "shopdrw", "workorders", "workstation", "qc", "quote",
             "shipping", "schedule",
             "inventory", "traceability",
             "qa", "wps", "weldercerts", "procedures", "ncrlog", "calibration",
             "gettingstarted", "tvdash", "admin"]
    for p in pages:
        placeholder = "{{ACTIVE_" + p + "}}"
        html = html.replace(placeholder, "active" if p == active_page else "")

    html = html.replace("{{USER_NAME}}", user_name)
    html = html.replace("{{USER_ROLE}}", user_role)

    # Project context JS
    context_js = ""
    if job_code:
        context_js = f"\nsetProjectContext('{job_code}');"

    return {
        "css": NAV_CSS,
        "html": html,
        "js": NAV_JS + context_js,
    }
