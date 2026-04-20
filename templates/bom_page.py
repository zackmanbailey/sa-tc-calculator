"""
BOM Page — Dedicated Bill of Materials view for a project.
"""

BOM_PAGE_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BOM — {{PROJECT_NAME}} | TitanForge</title>
<style>
:root {
    --tf-primary: #C89A2E;
    --tf-primary-dark: #A67E1E;
    --tf-surface: #FFFFFF;
    --tf-bg: #F5F5F0;
    --tf-border: #E5E5DD;
    --tf-gray-400: #9CA3AF;
    --tf-gray-500: #6B7280;
    --tf-gray-600: #4B5563;
    --tf-gray-700: #374151;
    --tf-gray-800: #1F2937;
    --tf-radius-md: 8px;
    --tf-radius-lg: 12px;
    --tf-sp-2: 8px;
    --tf-sp-3: 12px;
    --tf-sp-4: 16px;
    --tf-sp-5: 20px;
    --tf-sp-6: 24px;
    --tf-text-xs: 0.75rem;
    --tf-text-sm: 0.875rem;
    --tf-text-base: 1rem;
    --tf-text-lg: 1.125rem;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Inter', -apple-system, sans-serif; background: var(--tf-bg); color: var(--tf-gray-800); }

.bom-header {
    background: var(--tf-surface);
    border-bottom: 1px solid var(--tf-border);
    padding: var(--tf-sp-5) var(--tf-sp-6);
    display: flex;
    align-items: center;
    gap: var(--tf-sp-4);
    flex-wrap: wrap;
}
.bom-header h1 { font-size: var(--tf-text-lg); font-weight: 700; color: var(--tf-gray-800); }
.bom-header .job-code { font-size: var(--tf-text-sm); color: var(--tf-gray-500); font-weight: 500; }
.bom-header .spacer { flex: 1; }

.bom-actions { display: flex; gap: var(--tf-sp-2); flex-wrap: wrap; }
.bom-btn {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 8px 16px; border-radius: var(--tf-radius-md);
    font-size: var(--tf-text-sm); font-weight: 600;
    cursor: pointer; border: 1px solid var(--tf-border);
    background: var(--tf-surface); color: var(--tf-gray-700);
    transition: all 0.15s;
    text-decoration: none;
}
.bom-btn:hover { background: var(--tf-bg); border-color: var(--tf-gray-400); }
.bom-btn-primary { background: var(--tf-primary); color: #fff; border-color: var(--tf-primary); }
.bom-btn-primary:hover { background: var(--tf-primary-dark); }

.bom-content { padding: var(--tf-sp-6); max-width: 1400px; margin: 0 auto; }

.bom-tabs {
    display: flex; gap: 4px; margin-bottom: var(--tf-sp-4);
    border-bottom: 2px solid var(--tf-border);
    padding-bottom: 0;
}
.bom-tab {
    padding: 10px 20px; font-size: var(--tf-text-sm); font-weight: 600;
    color: var(--tf-gray-500); cursor: pointer; border: none; background: none;
    border-bottom: 2px solid transparent; margin-bottom: -2px;
    transition: all 0.15s;
}
.bom-tab:hover { color: var(--tf-gray-700); }
.bom-tab.active { color: var(--tf-primary); border-bottom-color: var(--tf-primary); }

.bom-panel { display: none; }
.bom-panel.active { display: block; }

.bom-table-wrap {
    background: var(--tf-surface); border: 1px solid var(--tf-border);
    border-radius: var(--tf-radius-lg); overflow: hidden; margin-bottom: var(--tf-sp-5);
}
.bom-cat-header {
    background: linear-gradient(135deg, rgba(200,154,46,0.08), rgba(200,154,46,0.02));
    padding: var(--tf-sp-3) var(--tf-sp-4);
    font-size: var(--tf-text-sm); font-weight: 700; color: var(--tf-gray-700);
    border-bottom: 1px solid var(--tf-border);
    display: flex; align-items: center; gap: 8px;
    cursor: pointer;
}
.bom-cat-header .count { font-weight: 400; color: var(--tf-gray-500); font-size: var(--tf-text-xs); }

table.bom-tbl {
    width: 100%; border-collapse: collapse; font-size: var(--tf-text-sm);
}
table.bom-tbl th {
    text-align: left; padding: 8px 12px; font-weight: 600;
    color: var(--tf-gray-600); background: var(--tf-bg);
    border-bottom: 1px solid var(--tf-border); font-size: var(--tf-text-xs);
    text-transform: uppercase; letter-spacing: 0.05em;
}
table.bom-tbl td {
    padding: 8px 12px; border-bottom: 1px solid rgba(0,0,0,0.04);
    color: var(--tf-gray-700);
}
table.bom-tbl tr:last-child td { border-bottom: none; }
table.bom-tbl tr:hover td { background: rgba(200,154,46,0.03); }
.text-right { text-align: right; }

.bom-summary {
    background: var(--tf-surface); border: 1px solid var(--tf-border);
    border-radius: var(--tf-radius-lg); padding: var(--tf-sp-5);
    display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: var(--tf-sp-4);
}
.summary-item { text-align: center; }
.summary-item .label { font-size: var(--tf-text-xs); color: var(--tf-gray-500); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
.summary-item .value { font-size: 1.5rem; font-weight: 700; color: var(--tf-gray-800); margin-top: 4px; }
.summary-item .value.gold { color: var(--tf-primary); }

.empty-state {
    text-align: center; padding: 60px 20px; color: var(--tf-gray-500);
}
.empty-state h3 { font-size: var(--tf-text-lg); margin-bottom: 8px; color: var(--tf-gray-700); }
.empty-state p { font-size: var(--tf-text-sm); margin-bottom: 20px; }

@media (max-width: 768px) {
    .bom-header { padding: var(--tf-sp-3) var(--tf-sp-4); }
    .bom-content { padding: var(--tf-sp-3); }
    .bom-actions { width: 100%; }
    .bom-btn { flex: 1; justify-content: center; padding: 6px 10px; font-size: var(--tf-text-xs); }
    table.bom-tbl th, table.bom-tbl td { padding: 6px 8px; font-size: var(--tf-text-xs); }
    .bom-summary { grid-template-columns: repeat(2, 1fr); }
}
</style>
</head>
<body>

<div class="bom-header">
    <div>
        <h1>Bill of Materials</h1>
        <span class="job-code">{{JOB_CODE}} &mdash; {{PROJECT_NAME}}</span>
    </div>
    <div class="spacer"></div>
    <div class="bom-actions">
        <a class="bom-btn" href="/project/{{JOB_CODE}}">&#8592; Back to Project</a>
        <a class="bom-btn bom-btn-primary" href="/sa?project={{JOB_CODE}}&tab=bom">&#9850; Recalculate BOM</a>
        <button class="bom-btn" onclick="exportPDF()">&#128196; Export PDF</button>
        <button class="bom-btn" onclick="exportExcel()">&#128202; Export Excel</button>
        <a class="bom-btn" href="/tc?project={{JOB_CODE}}">&#128221; Send to TC Estimator</a>
    </div>
</div>

<div class="bom-content">
    <div id="bomTabs" class="bom-tabs" style="display:none;"></div>
    <div id="bomPanels"></div>
    <div id="bomEmpty" class="empty-state" style="display:none;">
        <h3>No BOM Data Yet</h3>
        <p>Run the SA Estimator to generate a Bill of Materials for this project.</p>
        <a class="bom-btn bom-btn-primary" href="/sa?project={{JOB_CODE}}">Open SA Estimator</a>
    </div>

    <div id="bomSummary" class="bom-summary" style="display:none; margin-top: 24px;">
        <div class="summary-item">
            <div class="label">Total Items</div>
            <div class="value" id="sumItems">0</div>
        </div>
        <div class="summary-item">
            <div class="label">Total Weight</div>
            <div class="value" id="sumWeight">0 lbs</div>
        </div>
        <div class="summary-item cost-field">
            <div class="label">Material Cost</div>
            <div class="value gold" id="sumCost">$0</div>
        </div>
        <div class="summary-item cost-field">
            <div class="label">Sell Price</div>
            <div class="value gold" id="sumSell">$0</div>
        </div>
        <div class="summary-item cost-field">
            <div class="label">Margin</div>
            <div class="value" id="sumMargin">0%</div>
        </div>
    </div>
</div>

<script>
(function() {
    'use strict';

    const JOB_CODE = '{{JOB_CODE}}';
    const META = {{METADATA_JSON}};
    const BOM_RAW = {{BOM_JSON}};
    const USER_ROLE = (META._user_role || 'viewer').toLowerCase();
    const CAN_SEE_COSTS = ['admin','estimator','owner','executive','finance'].indexOf(USER_ROLE) >= 0;

    // Hide cost columns if not authorized
    if (!CAN_SEE_COSTS) {
        document.querySelectorAll('.cost-field').forEach(el => el.style.display = 'none');
    }

    function fmt$(v) { return '$' + Number(v||0).toLocaleString('en-US', {minimumFractionDigits:2, maximumFractionDigits:2}); }
    function fmtN(v) { return Number(v||0).toLocaleString('en-US'); }
    function fmtW(v) { return Number(v||0).toLocaleString('en-US', {maximumFractionDigits:1}) + ' lbs'; }

    // Normalize BOM data — it can come in different shapes
    let buildings = [];
    if (BOM_RAW && BOM_RAW.buildings && BOM_RAW.buildings.length) {
        buildings = BOM_RAW.buildings;
    } else if (BOM_RAW && BOM_RAW.line_items) {
        // Single building flat format
        buildings = [{ id: 'B1', label: 'Building 1', line_items: BOM_RAW.line_items, summary: BOM_RAW.summary || {} }];
    } else if (BOM_RAW && typeof BOM_RAW === 'object' && Object.keys(BOM_RAW).length > 0) {
        // Legacy format — try to extract something useful
        let items = [];
        if (Array.isArray(BOM_RAW.items)) items = BOM_RAW.items;
        else if (Array.isArray(BOM_RAW.bom)) items = BOM_RAW.bom;
        if (items.length) {
            buildings = [{ id: 'B1', label: 'Building 1', line_items: items, summary: BOM_RAW.summary || {} }];
        }
    }

    if (!buildings.length) {
        document.getElementById('bomEmpty').style.display = 'block';
        return;
    }

    // Build tabs if multiple buildings
    const tabsEl = document.getElementById('bomTabs');
    const panelsEl = document.getElementById('bomPanels');

    if (buildings.length > 1) {
        tabsEl.style.display = 'flex';
        buildings.forEach((b, i) => {
            const tab = document.createElement('button');
            tab.className = 'bom-tab' + (i === 0 ? ' active' : '');
            tab.textContent = b.label || ('Building ' + (i+1));
            tab.onclick = () => switchTab(i);
            tabsEl.appendChild(tab);
        });
    }

    // Render each building panel
    let totalItems = 0, totalWeight = 0, totalCost = 0, totalSell = 0;

    buildings.forEach((bldg, idx) => {
        const panel = document.createElement('div');
        panel.className = 'bom-panel' + (idx === 0 ? ' active' : '');
        panel.id = 'bom-panel-' + idx;

        const items = bldg.line_items || [];
        if (!items.length) {
            panel.innerHTML = '<div class="empty-state"><p>No line items for this building.</p></div>';
            panelsEl.appendChild(panel);
            return;
        }

        // Group by category
        const cats = {};
        items.forEach(item => {
            const cat = item.category || item.section || 'Other';
            if (!cats[cat]) cats[cat] = [];
            cats[cat].push(item);
        });

        let html = '';
        Object.keys(cats).sort().forEach(cat => {
            const catItems = cats[cat];
            html += '<div class="bom-table-wrap">';
            html += '<div class="bom-cat-header">' + escHtml(cat) + ' <span class="count">(' + catItems.length + ' items)</span></div>';
            html += '<table class="bom-tbl"><thead><tr>';
            html += '<th>Item</th><th>Description</th><th class="text-right">Qty</th><th>Unit</th><th class="text-right">Weight</th>';
            if (CAN_SEE_COSTS) html += '<th class="text-right">Unit Cost</th><th class="text-right">Total Cost</th>';
            html += '</tr></thead><tbody>';

            catItems.forEach(item => {
                const qty = item.quantity || item.qty || 0;
                const wt = item.total_weight_lbs || item.weight || item.total_weight || 0;
                const uc = item.unit_cost || 0;
                const tc = item.total_cost || (uc * qty) || 0;
                totalItems++;
                totalWeight += Number(wt) || 0;
                totalCost += Number(tc) || 0;

                html += '<tr>';
                html += '<td>' + escHtml(item.item || item.name || item.part || '') + '</td>';
                html += '<td>' + escHtml(item.description || item.desc || item.notes || '') + '</td>';
                html += '<td class="text-right">' + fmtN(qty) + '</td>';
                html += '<td>' + escHtml(item.unit || item.uom || 'ea') + '</td>';
                html += '<td class="text-right">' + fmtW(wt) + '</td>';
                if (CAN_SEE_COSTS) {
                    html += '<td class="text-right">' + fmt$(uc) + '</td>';
                    html += '<td class="text-right">' + fmt$(tc) + '</td>';
                }
                html += '</tr>';
            });

            html += '</tbody></table></div>';
        });

        panel.innerHTML = html;
        panelsEl.appendChild(panel);

        // Accumulate building summary
        const s = bldg.summary || {};
        totalSell += Number(s.sell_price || s.total_sell || 0);
    });

    // Summary
    document.getElementById('sumItems').textContent = fmtN(totalItems);
    document.getElementById('sumWeight').textContent = fmtW(totalWeight);
    document.getElementById('sumCost').textContent = fmt$(totalCost);
    document.getElementById('sumSell').textContent = fmt$(totalSell);
    const margin = totalSell > 0 ? ((totalSell - totalCost) / totalSell * 100) : 0;
    document.getElementById('sumMargin').textContent = margin.toFixed(1) + '%';
    document.getElementById('bomSummary').style.display = 'grid';

    function switchTab(idx) {
        tabsEl.querySelectorAll('.bom-tab').forEach((t,i) => t.classList.toggle('active', i===idx));
        document.querySelectorAll('.bom-panel').forEach((p,i) => p.classList.toggle('active', i===idx));
    }

    function escHtml(s) {
        const d = document.createElement('div');
        d.textContent = s || '';
        return d.innerHTML;
    }

    // Export functions
    window.exportPDF = function() {
        window.open('/api/project/' + encodeURIComponent(JOB_CODE) + '/bom?format=pdf', '_blank');
    };
    window.exportExcel = function() {
        window.open('/api/project/' + encodeURIComponent(JOB_CODE) + '/bom?format=excel', '_blank');
    };
})();
</script>
</body>
</html>
"""
