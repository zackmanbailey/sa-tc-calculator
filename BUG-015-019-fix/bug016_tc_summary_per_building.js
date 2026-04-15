/**
 * BUG-016 FIX — TC Summary Per-Building SA Line Items
 * =====================================================
 *
 * INSTRUCTIONS:
 * In templates/tc_quote.py, find the renderSummary() function.
 * After the main summary table, add a per-building breakdown section.
 *
 * This fix adds a collapsible per-building detail section below the
 * summary table showing each building's SA fabrication cost contribution.
 *
 * ADD this function alongside the existing renderSummary():
 */

/**
 * Render per-building SA cost breakdown in the summary tab.
 * Called after the main summary table is rendered.
 */
async function renderPerBuildingBreakdown() {
  const container = document.getElementById('per-building-breakdown');
  if (!container) return;

  const jobCode = strVal('proj_code').replace(/^TC-/, '');
  if (!jobCode) {
    container.innerHTML = '<p style="color:#94A3B8;text-align:center;padding:12px;font-size:0.85rem">Enter a project code to see per-building breakdown.</p>';
    return;
  }

  try {
    const resp = await fetch('/api/project/bom-summary?job_code=' + encodeURIComponent(jobCode));
    const result = await resp.json();

    if (!result.ok || !result.buildings || result.buildings.length === 0) {
      container.innerHTML = '<p style="color:#94A3B8;text-align:center;padding:12px;font-size:0.85rem">No SA BOM data found for this project. Run the SA calculator first.</p>';
      return;
    }

    let html = '<table style="width:100%;border-collapse:collapse;font-size:0.85rem">';
    html += '<thead><tr style="background:#1E3A5F;color:white">';
    html += '<th style="padding:8px 12px;text-align:left;border-radius:6px 0 0 0">Building</th>';
    html += '<th style="padding:8px 12px;text-align:center">Type</th>';
    html += '<th style="padding:8px 12px;text-align:center">Dimensions</th>';
    html += '<th style="padding:8px 12px;text-align:right">Weight (lbs)</th>';
    html += '<th style="padding:8px 12px;text-align:right">Material Cost</th>';
    html += '<th style="padding:8px 12px;text-align:right;border-radius:0 6px 0 0">Sell Price</th>';
    html += '</tr></thead><tbody>';

    let totalWeight = 0, totalCost = 0, totalSell = 0;

    result.buildings.forEach((b, i) => {
      const bg = i % 2 === 0 ? '#F7F9FC' : '#FFFFFF';
      const weight = b.total_weight_lbs || 0;
      const cost = b.total_material_cost || 0;
      const sell = b.total_sell_price || 0;
      totalWeight += weight;
      totalCost += cost;
      totalSell += sell;

      html += `<tr style="background:${bg}">`;
      html += `<td style="padding:6px 12px;border-bottom:1px solid #E2E8F0;font-weight:600">${b.building_name || 'Building ' + (i+1)}</td>`;
      html += `<td style="padding:6px 12px;text-align:center;border-bottom:1px solid #E2E8F0;text-transform:capitalize">${b.type || 'tee'}</td>`;
      html += `<td style="padding:6px 12px;text-align:center;border-bottom:1px solid #E2E8F0">${b.width_ft || 0}'W × ${b.length_ft || 0}'L</td>`;
      html += `<td style="padding:6px 12px;text-align:right;border-bottom:1px solid #E2E8F0">${weight.toLocaleString('en-US', {maximumFractionDigits:0})}</td>`;
      html += `<td style="padding:6px 12px;text-align:right;border-bottom:1px solid #E2E8F0">${fmt(cost)}</td>`;
      html += `<td style="padding:6px 12px;text-align:right;border-bottom:1px solid #E2E8F0;font-weight:600;color:#1E3A5F">${fmt(sell)}</td>`;
      html += '</tr>';
    });

    // Total row
    html += '<tr style="background:#1E3A5F;color:white;font-weight:700">';
    html += `<td colspan="3" style="padding:8px 12px;border-radius:0 0 0 6px">TOTAL (${result.buildings.length} buildings)</td>`;
    html += `<td style="padding:8px 12px;text-align:right">${totalWeight.toLocaleString('en-US', {maximumFractionDigits:0})}</td>`;
    html += `<td style="padding:8px 12px;text-align:right">${fmt(totalCost)}</td>`;
    html += `<td style="padding:8px 12px;text-align:right;border-radius:0 0 6px 0">${fmt(totalSell)}</td>`;
    html += '</tr></tbody></table>';

    container.innerHTML = html;
  } catch(e) {
    container.innerHTML = '<p style="color:#EF4444;text-align:center;padding:12px;font-size:0.85rem">Error loading building data: ' + e.message + '</p>';
  }
}

/*
 * ADD this HTML in the Summary tab section of tc_quote.py,
 * after the summary-table card (around line 583, before intelPanel):
 *
 *   <div class="card" style="margin-top:16px;">
 *     <div class="card-hdr blue" style="cursor:pointer" onclick="this.nextElementSibling.style.display=this.nextElementSibling.style.display==='none'?'block':'none';renderPerBuildingBreakdown()">
 *       <span>&#127959;</span>SA Fabrication — Per-Building Breakdown
 *       <span style="margin-left:auto;font-size:0.75rem;opacity:0.7">Click to expand</span>
 *     </div>
 *     <div class="card-body" id="per-building-breakdown" style="display:none">
 *       <p style="color:#94A3B8;text-align:center;padding:12px;font-size:0.85rem">Click the header to load per-building data.</p>
 *     </div>
 *   </div>
 */
