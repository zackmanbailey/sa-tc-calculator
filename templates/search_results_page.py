"""
TitanForge v5 — Search Results Page
====================================
Dedicated search results page with categorized results from /api/search.
Supports ?q= query parameter, debounced live search, and category filtering.
"""
from templates.shared_styles import DESIGN_SYSTEM_CSS

SEARCH_RESULTS_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TitanForge — Search Results</title>
    <style>
""" + DESIGN_SYSTEM_CSS + r"""

        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: var(--tf-font, 'Inter', -apple-system, BlinkMacSystemFont, sans-serif);
            background: #0F172A;
            color: #E2E8F0;
            min-height: 100vh;
        }

        .search-page { max-width: 960px; margin: 0 auto; padding: 32px 24px; }

        /* ── Search Header ── */
        .search-header { margin-bottom: 32px; }
        .search-header h1 {
            font-size: 1.5rem;
            font-weight: 700;
            color: #F8FAFC;
            margin-bottom: 16px;
        }
        .search-input-wrap {
            display: flex;
            align-items: center;
            background: #1E293B;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 0 16px;
            transition: border-color 0.2s;
        }
        .search-input-wrap:focus-within {
            border-color: #3B82F6;
            box-shadow: 0 0 0 3px rgba(59,130,246,0.15);
        }
        .search-input-wrap .icon {
            font-size: 1.2rem;
            color: #64748B;
            margin-right: 12px;
            flex-shrink: 0;
        }
        .search-input-wrap input {
            flex: 1;
            border: none;
            outline: none;
            background: transparent;
            color: #F8FAFC;
            font-size: 1rem;
            padding: 14px 0;
            font-family: inherit;
        }
        .search-input-wrap input::placeholder { color: #64748B; }
        .search-input-wrap .clear-btn {
            background: none;
            border: none;
            color: #64748B;
            cursor: pointer;
            font-size: 1.1rem;
            padding: 4px 8px;
            border-radius: 4px;
            display: none;
        }
        .search-input-wrap .clear-btn.visible { display: block; }
        .search-input-wrap .clear-btn:hover { color: #E2E8F0; background: rgba(255,255,255,0.06); }

        /* ── Summary Bar ── */
        .search-summary {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .search-summary .total {
            font-size: 0.9rem;
            color: #94A3B8;
        }
        .search-summary .total strong { color: #F8FAFC; }

        /* ── Category Tabs ── */
        .category-tabs {
            display: flex;
            gap: 6px;
            margin-bottom: 24px;
            flex-wrap: wrap;
        }
        .cat-tab {
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            cursor: pointer;
            border: 1px solid #334155;
            background: transparent;
            color: #94A3B8;
            transition: all 0.15s;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .cat-tab:hover { border-color: #94A3B8; color: #E2E8F0; }
        .cat-tab.active { background: #1E40AF; border-color: #1E40AF; color: #fff; }
        .cat-tab .count {
            background: rgba(255,255,255,0.15);
            padding: 1px 7px;
            border-radius: 10px;
            font-size: 0.7rem;
        }
        .cat-tab.active .count { background: rgba(255,255,255,0.25); }

        /* ── Results List ── */
        .results-section { margin-bottom: 32px; }
        .results-section-header {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid #1E293B;
        }
        .results-section-header .section-icon {
            width: 28px;
            height: 28px;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.9rem;
        }
        .results-section-header h2 {
            font-size: 0.85rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #94A3B8;
        }
        .results-section-header .section-count {
            margin-left: auto;
            font-size: 0.75rem;
            color: #64748B;
        }

        /* ── Result Card ── */
        .result-card {
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 14px 16px;
            background: #1E293B;
            border: 1px solid #334155;
            border-radius: 8px;
            margin-bottom: 8px;
            text-decoration: none;
            color: inherit;
            transition: all 0.15s;
            cursor: pointer;
        }
        .result-card:hover {
            border-color: #94A3B8;
            background: #253449;
            transform: translateX(2px);
        }
        .result-card .rc-icon {
            width: 40px;
            height: 40px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1rem;
            flex-shrink: 0;
        }
        .result-card .rc-body { flex: 1; min-width: 0; }
        .result-card .rc-title {
            font-weight: 600;
            font-size: 0.9rem;
            color: #F8FAFC;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .result-card .rc-subtitle {
            font-size: 0.8rem;
            color: #94A3B8;
            margin-top: 2px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .result-card .rc-badge {
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.7rem;
            font-weight: 600;
            flex-shrink: 0;
        }
        .result-card .rc-arrow {
            color: #94A3B8;
            font-size: 1rem;
            flex-shrink: 0;
            transition: color 0.15s;
        }
        .result-card:hover .rc-arrow { color: #94A3B8; }

        /* Category color coding */
        .cat-project .rc-icon, .cat-project .section-icon { background: rgba(30,64,175,0.2); color: #60A5FA; }
        .cat-customer .rc-icon, .cat-customer .section-icon { background: rgba(5,150,105,0.2); color: #34D399; }
        .cat-inventory .rc-icon, .cat-inventory .section-icon { background: rgba(217,119,6,0.2); color: #FBBF24; }
        .cat-work_order .rc-icon, .cat-work_order .section-icon { background: rgba(139,92,246,0.2); color: #A78BFA; }
        .cat-user .rc-icon, .cat-user .section-icon { background: rgba(236,72,153,0.2); color: #F472B6; }

        .badge-project { background: rgba(30,64,175,0.2); color: #60A5FA; }
        .badge-customer { background: rgba(5,150,105,0.2); color: #34D399; }
        .badge-inventory { background: rgba(217,119,6,0.2); color: #FBBF24; }
        .badge-work_order { background: rgba(139,92,246,0.2); color: #A78BFA; }
        .badge-user { background: rgba(236,72,153,0.2); color: #F472B6; }

        /* ── Empty State ── */
        .empty-state {
            text-align: center;
            padding: 60px 20px;
        }
        .empty-state .empty-icon {
            font-size: 3rem;
            margin-bottom: 16px;
            opacity: 0.4;
        }
        .empty-state h3 {
            font-size: 1.1rem;
            color: #94A3B8;
            margin-bottom: 8px;
        }
        .empty-state p {
            font-size: 0.85rem;
            color: #64748B;
            max-width: 400px;
            margin: 0 auto;
        }

        /* ── Loading ── */
        .loading-state {
            text-align: center;
            padding: 40px 20px;
            color: #64748B;
        }
        .loading-spinner {
            display: inline-block;
            width: 28px;
            height: 28px;
            border: 3px solid #334155;
            border-top-color: #3B82F6;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin-bottom: 12px;
        }
        @keyframes spin { to { transform: rotate(360deg); } }

        /* ── Responsive ── */
        @media (max-width: 768px) {
            .search-page { padding: 16px 12px; }
            .result-card { padding: 12px; gap: 10px; }
            .result-card .rc-badge { display: none; }
            .category-tabs { gap: 4px; }
            .cat-tab { padding: 5px 10px; font-size: 0.75rem; }
        }
    </style>
</head>
<body>
    <div class="search-page">
        <!-- Search Header -->
        <div class="search-header">
            <h1>Search</h1>
            <div class="search-input-wrap">
                <span class="icon">&#128269;</span>
                <input type="text" id="searchInput" placeholder="Search projects, customers, inventory, work orders..." autofocus>
                <button class="clear-btn" id="clearBtn" onclick="clearSearch()">&#10005;</button>
            </div>
        </div>

        <!-- Summary -->
        <div class="search-summary" id="searchSummary" style="display:none;">
            <div class="total" id="totalCount"></div>
        </div>

        <!-- Category Tabs -->
        <div class="category-tabs" id="categoryTabs" style="display:none;"></div>

        <!-- Results Container -->
        <div id="resultsContainer">
            <div class="empty-state" id="initialState">
                <div class="empty-icon">&#128269;</div>
                <h3>Search across TitanForge</h3>
                <p>Find projects, customers, inventory items, and work orders. Start typing to see results.</p>
            </div>
        </div>
    </div>

    <script>
    (function() {
        const input = document.getElementById('searchInput');
        const clearBtn = document.getElementById('clearBtn');
        const container = document.getElementById('resultsContainer');
        const summaryEl = document.getElementById('searchSummary');
        const totalCountEl = document.getElementById('totalCount');
        const tabsEl = document.getElementById('categoryTabs');
        const initialState = document.getElementById('initialState');

        let debounceTimer = null;
        let currentResults = [];
        let activeFilter = 'all';

        // Category config
        const CATEGORIES = {
            project:    { label: 'Projects',     icon: '&#128194;', order: 0 },
            customer:   { label: 'Customers',    icon: '&#128101;', order: 1 },
            inventory:  { label: 'Inventory',    icon: '&#128230;', order: 2 },
            work_order: { label: 'Work Orders',  icon: '&#128203;', order: 3 },
            user:       { label: 'Users',        icon: '&#128100;', order: 4 }
        };

        // Read ?q= from URL on load
        const params = new URLSearchParams(window.location.search);
        const initialQ = params.get('q') || '';
        if (initialQ) {
            input.value = initialQ;
            clearBtn.classList.add('visible');
            runSearch(initialQ);
        }

        // Input handling
        input.addEventListener('input', function() {
            const q = input.value.trim();
            clearBtn.classList.toggle('visible', q.length > 0);

            clearTimeout(debounceTimer);
            if (q.length < 2) {
                showInitialState();
                updateURL('');
                return;
            }
            debounceTimer = setTimeout(function() {
                updateURL(q);
                runSearch(q);
            }, 300);
        });

        input.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                clearSearch();
            }
        });

        function clearSearch() {
            input.value = '';
            clearBtn.classList.remove('visible');
            showInitialState();
            updateURL('');
            input.focus();
        }

        function updateURL(q) {
            const url = new URL(window.location);
            if (q) {
                url.searchParams.set('q', q);
            } else {
                url.searchParams.delete('q');
            }
            history.replaceState(null, '', url);
        }

        function showInitialState() {
            currentResults = [];
            activeFilter = 'all';
            summaryEl.style.display = 'none';
            tabsEl.style.display = 'none';
            container.innerHTML = '<div class="empty-state" id="initialState">' +
                '<div class="empty-icon">&#128269;</div>' +
                '<h3>Search across TitanForge</h3>' +
                '<p>Find projects, customers, inventory items, and work orders. Start typing to see results.</p></div>';
        }

        function showLoading() {
            summaryEl.style.display = 'none';
            tabsEl.style.display = 'none';
            container.innerHTML = '<div class="loading-state"><div class="loading-spinner"></div><div>Searching...</div></div>';
        }

        async function runSearch(query) {
            showLoading();
            try {
                const resp = await fetch('/api/search?q=' + encodeURIComponent(query));
                const data = await resp.json();
                currentResults = data.results || [];
                activeFilter = 'all';
                renderResults();
            } catch (err) {
                container.innerHTML = '<div class="empty-state"><div class="empty-icon">&#9888;</div>' +
                    '<h3>Search failed</h3><p>Could not connect to the search API. Please try again.</p></div>';
                summaryEl.style.display = 'none';
                tabsEl.style.display = 'none';
            }
        }

        function renderResults() {
            if (currentResults.length === 0) {
                const q = escHtml(input.value.trim());
                container.innerHTML = '<div class="empty-state"><div class="empty-icon">&#128683;</div>' +
                    '<h3>No results found</h3><p>No matches for "' + q + '". Try a different search term or check your spelling.</p></div>';
                summaryEl.style.display = 'none';
                tabsEl.style.display = 'none';
                return;
            }

            // Count by category
            var counts = {};
            for (var i = 0; i < currentResults.length; i++) {
                var t = currentResults[i].type || 'other';
                counts[t] = (counts[t] || 0) + 1;
            }

            // Filter
            var filtered = activeFilter === 'all' ? currentResults :
                currentResults.filter(function(r) { return r.type === activeFilter; });

            // Summary
            summaryEl.style.display = 'flex';
            totalCountEl.innerHTML = '<strong>' + currentResults.length + '</strong> result' +
                (currentResults.length !== 1 ? 's' : '') + ' found';

            // Category tabs
            var tabsHtml = '<button class="cat-tab ' + (activeFilter === 'all' ? 'active' : '') +
                '" onclick="window._searchFilterBy(\'all\')">All <span class="count">' + currentResults.length + '</span></button>';
            var sortedCats = Object.keys(counts).sort(function(a, b) {
                return ((CATEGORIES[a] || {}).order || 99) - ((CATEGORIES[b] || {}).order || 99);
            });
            for (var ci = 0; ci < sortedCats.length; ci++) {
                var cat = sortedCats[ci];
                var catInfo = CATEGORIES[cat] || { label: cat, icon: '&#128196;' };
                tabsHtml += '<button class="cat-tab ' + (activeFilter === cat ? 'active' : '') +
                    '" onclick="window._searchFilterBy(\'' + cat + '\')">' +
                    catInfo.label + ' <span class="count">' + counts[cat] + '</span></button>';
            }
            tabsEl.innerHTML = tabsHtml;
            tabsEl.style.display = 'flex';

            // Group results by type
            var grouped = {};
            for (var j = 0; j < filtered.length; j++) {
                var type = filtered[j].type || 'other';
                if (!grouped[type]) grouped[type] = [];
                grouped[type].push(filtered[j]);
            }

            // Render sections
            var html = '';
            var orderedTypes = Object.keys(grouped).sort(function(a, b) {
                return ((CATEGORIES[a] || {}).order || 99) - ((CATEGORIES[b] || {}).order || 99);
            });

            for (var k = 0; k < orderedTypes.length; k++) {
                var secType = orderedTypes[k];
                var secInfo = CATEGORIES[secType] || { label: secType, icon: '&#128196;' };
                var items = grouped[secType];

                html += '<div class="results-section">';
                html += '<div class="results-section-header cat-' + secType + '">';
                html += '<div class="section-icon">' + secInfo.icon + '</div>';
                html += '<h2>' + secInfo.label + '</h2>';
                html += '<span class="section-count">' + items.length + ' result' + (items.length !== 1 ? 's' : '') + '</span>';
                html += '</div>';

                for (var m = 0; m < items.length; m++) {
                    var item = items[m];
                    var url = item.url || '#';
                    html += '<a href="' + escAttr(url) + '" class="result-card cat-' + secType + '">';
                    html += '<div class="rc-icon">' + secInfo.icon + '</div>';
                    html += '<div class="rc-body">';
                    html += '<div class="rc-title">' + escHtml(item.title || item.name || '') + '</div>';
                    html += '<div class="rc-subtitle">' + escHtml(item.subtitle || '') + '</div>';
                    html += '</div>';
                    if (item.stage || item.status) {
                        html += '<span class="rc-badge badge-' + secType + '">' + escHtml(item.stage || item.status) + '</span>';
                    }
                    html += '<span class="rc-arrow">&#8250;</span>';
                    html += '</a>';
                }
                html += '</div>';
            }

            container.innerHTML = html;
        }

        // Global filter function
        window._searchFilterBy = function(cat) {
            activeFilter = cat;
            renderResults();
        };

        // Escape helpers
        function escHtml(s) {
            var d = document.createElement('div');
            d.textContent = s || '';
            return d.innerHTML;
        }
        function escAttr(s) {
            return (s || '').replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        }
    })();
    </script>
</body>
</html>
"""
