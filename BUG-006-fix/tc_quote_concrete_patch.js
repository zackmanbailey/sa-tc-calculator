/**
 * BUG-006 FIX — Per-Building Concrete Breakdown for TC Estimator
 * ================================================================
 *
 * INSTRUCTIONS:
 * 1. In templates/tc_quote.py, find the existing calcConcrete() function (around line 699)
 * 2. REPLACE the entire calcConcrete() function AND the syncConcreteFromSA() function
 *    with the contents below (everything between the START/END markers)
 * 3. Also add the new HTML for the concrete card (see tc_quote_html_patch.html)
 *
 * This replaces the single-total concrete calculation with a per-building
 * breakdown table that auto-populates from SA BOM data.
 */

// ─────────────────────────────────────────────
// CONCRETE — PER-BUILDING BREAKDOWN (BUG-006 FIX)
// ─────────────────────────────────────────────

// Global: per-building concrete data
let concreteBuildings = [];
let concreteGlobalPriceCY = 165;

/**
 * Fetch per-building BOM data from the saved SA calculation.
 * Falls back to single-building mode using the SA aggregate values on the TC page.
 */
async function loadBuildingConcreteData() {
  const jobCode = strVal('proj_code').replace(/^TC-/, '');
  if (!jobCode) {
    // No job code yet — initialize with single default row
    initSingleBuildingFallback();
    return;
  }

  try {
    const resp = await fetch('/api/project/bom-summary?job_code=' + encodeURIComponent(jobCode));
    const result = await resp.json();

    if (result.ok && result.buildings && result.buildings.length > 0) {
      concreteBuildings = result.buildings.map((b, i) => ({
        building_id: b.building_id || `bldg_${i+1}`,
        building_name: b.building_name || `Building ${i+1}`,
        type: b.type || 'tee',
        n_piers: b.concrete_n_piers || b.n_struct_cols || 0,
        dia_in: 24,  // Default 24" diameter per user spec
        depth_ft: b.footing_depth_ft || numVal('sa_footing_depth') || 10,
        price_cy: concreteGlobalPriceCY,
        // Read-only reference data from SA
        sa_n_piers: b.concrete_n_piers || b.n_struct_cols || 0,
        sa_depth_ft: b.footing_depth_ft || 10,
        sa_concrete_cy: b.concrete_cy || 0,
      }));
      renderConcreteTable();
      calcConcrete();
      showToast('Loaded concrete data for ' + concreteBuildings.length + ' building(s) from SA BOM', 'success');
    } else {
      initSingleBuildingFallback();
    }
  } catch (e) {
    console.warn('Could not load SA BOM data for concrete breakdown:', e);
    initSingleBuildingFallback();
  }
}

/**
 * Fallback: create single building from SA aggregate values on the TC page.
 */
function initSingleBuildingFallback() {
  const nCols = numVal('sa_n_cols');
  const depth = numVal('sa_footing_depth') || 10;
  concreteBuildings = [{
    building_id: 'bldg_1',
    building_name: 'Building 1',
    type: 'tee',
    n_piers: nCols || 0,
    dia_in: 24,
    depth_ft: depth,
    price_cy: concreteGlobalPriceCY,
    sa_n_piers: nCols || 0,
    sa_depth_ft: depth,
    sa_concrete_cy: 0,
  }];
  renderConcreteTable();
  calcConcrete();
}

/**
 * Add a building row manually (for projects without SA BOM data).
 */
function addConcreteBuilding() {
  const idx = concreteBuildings.length + 1;
  concreteBuildings.push({
    building_id: `bldg_${idx}`,
    building_name: `Building ${idx}`,
    type: 'tee',
    n_piers: 0,
    dia_in: 24,
    depth_ft: numVal('sa_footing_depth') || 10,
    price_cy: concreteGlobalPriceCY,
    sa_n_piers: 0,
    sa_depth_ft: 10,
    sa_concrete_cy: 0,
  });
  renderConcreteTable();
  calcConcrete();
}

/**
 * Remove a building row.
 */
function removeConcreteBuilding(idx) {
  if (concreteBuildings.length <= 1) {
    showToast('Cannot remove the last building', 'error');
    return;
  }
  concreteBuildings.splice(idx, 1);
  renderConcreteTable();
  calcConcrete();
}

/**
 * Update a building's concrete parameter.
 */
function updateConcreteField(idx, field, value) {
  if (concreteBuildings[idx]) {
    concreteBuildings[idx][field] = parseFloat(value) || 0;
    calcConcrete();
  }
}

/**
 * Update building name.
 */
function updateConcreteName(idx, value) {
  if (concreteBuildings[idx]) {
    concreteBuildings[idx].building_name = value;
  }
}

/**
 * Apply global price per CY to all buildings.
 */
function applyGlobalPriceCY() {
  concreteGlobalPriceCY = numVal('conc_global_price_cy') || 165;
  concreteBuildings.forEach(b => { b.price_cy = concreteGlobalPriceCY; });
  renderConcreteTable();
  calcConcrete();
}

/**
 * Calculate concrete for a single building row.
 */
function calcBuildingConcrete(b) {
  const rFt = (b.dia_in / 2) / 12;
  const volCY = Math.PI * rFt * rFt * b.depth_ft / 27;
  const totalCY = b.n_piers * volCY * 1.10; // 10% waste
  const cost = totalCY * b.price_cy;
  return { volCY: totalCY, cost: cost };
}

/**
 * Recalculate all buildings and update totals (replaces old calcConcrete).
 */
function calcConcrete() {
  let totalCY = 0;
  let totalCost = 0;

  concreteBuildings.forEach((b, i) => {
    const r = calcBuildingConcrete(b);
    totalCY += r.volCY;
    totalCost += r.cost;

    // Update row displays if they exist
    const cyEl = document.getElementById(`conc_bldg_cy_${i}`);
    const costEl = document.getElementById(`conc_bldg_cost_${i}`);
    if (cyEl) cyEl.textContent = r.volCY.toFixed(2) + ' CY';
    if (costEl) costEl.textContent = fmt(r.cost);
  });

  concreteCost = totalCost;

  // Update summary displays
  document.getElementById('conc_qty_display').textContent = totalCY.toFixed(2) + ' CY';
  document.getElementById('conc_cost_display').textContent = fmt(totalCost);

  // Update building count badge
  const badge = document.getElementById('conc_bldg_count');
  if (badge) badge.textContent = concreteBuildings.length + ' building(s)';

  renderSummary();
}

/**
 * Render the per-building concrete table.
 */
function renderConcreteTable() {
  const container = document.getElementById('conc_buildings_table');
  if (!container) return;

  if (concreteBuildings.length === 0) {
    container.innerHTML = '<p style="color:#888;text-align:center;padding:12px">No buildings configured. Click "Add Building" or sync from SA BOM.</p>';
    return;
  }

  let html = `
    <table style="width:100%;border-collapse:collapse;font-size:13px;margin-top:8px">
      <thead>
        <tr style="background:#1E3A5F;color:white">
          <th style="padding:6px 8px;text-align:left;border-radius:4px 0 0 0">Building</th>
          <th style="padding:6px 8px;text-align:center"># Piers</th>
          <th style="padding:6px 8px;text-align:center">Dia (in)</th>
          <th style="padding:6px 8px;text-align:center">Depth (ft)</th>
          <th style="padding:6px 8px;text-align:center">$/CY</th>
          <th style="padding:6px 8px;text-align:right">Cubic Yards</th>
          <th style="padding:6px 8px;text-align:right">Cost</th>
          <th style="padding:6px 4px;text-align:center;border-radius:0 4px 0 0;width:32px"></th>
        </tr>
      </thead>
      <tbody>`;

  concreteBuildings.forEach((b, i) => {
    const r = calcBuildingConcrete(b);
    const bgColor = i % 2 === 0 ? '#F7F9FC' : '#FFFFFF';
    const fromSA = b.sa_n_piers > 0 ? ' title="SA BOM: ' + b.sa_n_piers + ' piers, ' + b.sa_depth_ft + '\' depth, ' + (b.sa_concrete_cy || 0).toFixed(2) + ' CY"' : '';

    html += `
      <tr style="background:${bgColor}">
        <td style="padding:5px 8px;border-bottom:1px solid #E2E8F0">
          <input type="text" value="${b.building_name}" onchange="updateConcreteName(${i}, this.value)"
            style="border:1px solid #D0D7E2;border-radius:4px;padding:3px 6px;width:120px;font-size:12px"${fromSA}/>
        </td>
        <td style="padding:5px 4px;text-align:center;border-bottom:1px solid #E2E8F0">
          <input type="number" value="${b.n_piers}" min="0"
            onchange="updateConcreteField(${i},'n_piers',this.value);renderConcreteTable()"
            style="width:60px;text-align:center;border:1px solid #D0D7E2;border-radius:4px;padding:3px;font-size:12px"/>
        </td>
        <td style="padding:5px 4px;text-align:center;border-bottom:1px solid #E2E8F0">
          <input type="number" value="${b.dia_in}" min="6" max="60"
            onchange="updateConcreteField(${i},'dia_in',this.value);renderConcreteTable()"
            style="width:60px;text-align:center;border:1px solid #D0D7E2;border-radius:4px;padding:3px;font-size:12px"/>
        </td>
        <td style="padding:5px 4px;text-align:center;border-bottom:1px solid #E2E8F0">
          <input type="number" value="${b.depth_ft}" min="4" max="25" step="0.5"
            onchange="updateConcreteField(${i},'depth_ft',this.value);renderConcreteTable()"
            style="width:60px;text-align:center;border:1px solid #D0D7E2;border-radius:4px;padding:3px;font-size:12px"/>
        </td>
        <td style="padding:5px 4px;text-align:center;border-bottom:1px solid #E2E8F0">
          <input type="number" value="${b.price_cy}" min="0" step="5"
            onchange="updateConcreteField(${i},'price_cy',this.value)"
            style="width:70px;text-align:center;border:1px solid #D0D7E2;border-radius:4px;padding:3px;font-size:12px"/>
        </td>
        <td style="padding:5px 8px;text-align:right;border-bottom:1px solid #E2E8F0;font-weight:600;color:#1E3A5F">
          <span id="conc_bldg_cy_${i}">${r.volCY.toFixed(2)} CY</span>
        </td>
        <td style="padding:5px 8px;text-align:right;border-bottom:1px solid #E2E8F0;font-weight:600;color:#C0392B">
          <span id="conc_bldg_cost_${i}">${fmt(r.cost)}</span>
        </td>
        <td style="padding:5px 4px;text-align:center;border-bottom:1px solid #E2E8F0">
          <button onclick="removeConcreteBuilding(${i})" title="Remove building"
            style="background:none;border:none;cursor:pointer;color:#C0392B;font-size:14px;padding:2px">✕</button>
        </td>
      </tr>`;
  });

  // Total row
  let totalCY = 0, totalCost = 0;
  concreteBuildings.forEach(b => {
    const r = calcBuildingConcrete(b);
    totalCY += r.volCY;
    totalCost += r.cost;
  });

  html += `
      <tr style="background:#1E3A5F;color:white;font-weight:700">
        <td colspan="5" style="padding:6px 8px;border-radius:0 0 0 4px">TOTAL</td>
        <td style="padding:6px 8px;text-align:right">${totalCY.toFixed(2)} CY</td>
        <td style="padding:6px 8px;text-align:right">${fmt(totalCost)}</td>
        <td style="border-radius:0 0 4px 0"></td>
      </tr>
    </tbody></table>`;

  container.innerHTML = html;
}

/**
 * Sync concrete from SA values (updated for per-building).
 * If BOM data available, loads per-building. Otherwise uses aggregate values.
 */
function syncConcreteFromSA() {
  loadBuildingConcreteData();
}

/**
 * Build concrete payload for saving/exporting (replaces the old single-value payload).
 */
function buildConcretePayload() {
  let totalCY = 0, totalCost = 0;
  const buildings = concreteBuildings.map(b => {
    const r = calcBuildingConcrete(b);
    totalCY += r.volCY;
    totalCost += r.cost;
    return {
      building_id: b.building_id,
      building_name: b.building_name,
      n_piers: b.n_piers,
      dia_in: b.dia_in,
      depth_ft: b.depth_ft,
      price_cy: b.price_cy,
      cubic_yards: parseFloat(r.volCY.toFixed(2)),
      cost: parseFloat(r.cost.toFixed(2)),
    };
  });
  return {
    buildings: buildings,
    total_cy: parseFloat(totalCY.toFixed(2)),
    total: parseFloat(totalCost.toFixed(2)),
    global_price_cy: concreteGlobalPriceCY,
  };
}

// On page load, initialize concrete
document.addEventListener('DOMContentLoaded', function() {
  prefillFromURL();
  // After URL params are loaded, try to load per-building data
  setTimeout(loadBuildingConcreteData, 500);
});
