/**
 * BUG-009 FIX — Misc Items Common Presets for TC Estimator
 * =========================================================
 *
 * INSTRUCTIONS:
 * In templates/tc_quote.py, REPLACE the misc card HTML (lines 560-571) with the
 * enhanced version below. Then REPLACE the addMiscItem/renderMiscTable functions
 * (lines 836-863) with the new versions below.
 */

// ── NEW HTML for Misc Card (replace lines 560-571) ──────────────────
/*
      <!-- Miscellaneous / Other — BUG-009 Enhanced -->
      <div class="card" id="card-misc">
        <div class="card-hdr gold"><span>&#128230;</span>Miscellaneous / Other</div>
        <div class="card-body">
          <!-- Preset selector -->
          <div style="display:flex;gap:8px;align-items:center;margin-bottom:10px;flex-wrap:wrap">
            <select id="misc_preset" style="flex:1;max-width:280px;padding:6px 10px;border:1.5px solid #D0D7E2;border-radius:6px;font-size:0.85rem">
              <option value="">Add common item...</option>
              <option value="permits|1500">Building Permits ($1,500)</option>
              <option value="inspections|500">Inspections ($500)</option>
              <option value="site_cleanup|800">Site Cleanup ($800)</option>
              <option value="dumpster|450">Dumpster Rental ($450)</option>
              <option value="porta_potty|250">Porta Potty Rental ($250)</option>
              <option value="temp_power|350">Temporary Power ($350)</option>
              <option value="survey_layout|600">Survey / Layout ($600)</option>
              <option value="bond|0">Performance Bond (enter amount)</option>
              <option value="insurance|0">Job-Specific Insurance (enter amount)</option>
              <option value="welding_supplies|400">Welding Supplies ($400)</option>
              <option value="anchor_bolts|300">Anchor Bolts ($300)</option>
              <option value="grout|200">Grout / Non-Shrink ($200)</option>
              <option value="water_truck|500">Water Truck ($500)</option>
              <option value="crane_mobilization|1200">Crane Mobilization ($1,200)</option>
              <option value="safety_supplies|350">Safety Supplies ($350)</option>
            </select>
            <button class="btn btn-outline btn-sm" onclick="addMiscPreset()" style="white-space:nowrap">+ Add Selected</button>
            <button class="btn btn-outline btn-sm" onclick="addMiscItem()" style="white-space:nowrap">+ Custom Item</button>
          </div>
          <table class="li-table">
            <thead><tr><th>Description</th><th>Amount ($)</th><th></th></tr></thead>
            <tbody id="misc_tbody"></tbody>
          </table>
        </div>
      </div>
*/

// ── NEW JS (replace addMiscItem/renderMiscTable around line 836) ──

const MISC_PRESET_LABELS = {
  permits: 'Building Permits',
  inspections: 'Inspections',
  site_cleanup: 'Site Cleanup',
  dumpster: 'Dumpster Rental',
  porta_potty: 'Porta Potty Rental',
  temp_power: 'Temporary Power',
  survey_layout: 'Survey / Layout',
  bond: 'Performance Bond',
  insurance: 'Job-Specific Insurance',
  welding_supplies: 'Welding Supplies',
  anchor_bolts: 'Anchor Bolts',
  grout: 'Grout / Non-Shrink',
  water_truck: 'Water Truck',
  crane_mobilization: 'Crane Mobilization',
  safety_supplies: 'Safety Supplies',
};

function addMiscPreset() {
  const sel = document.getElementById('misc_preset');
  if (!sel.value) return;
  const [key, amt] = sel.value.split('|');
  const desc = MISC_PRESET_LABELS[key] || key;
  miscItems.push({ desc: desc, amount: parseFloat(amt) || 0 });
  sel.value = '';
  renderMiscTable();
  renderSummary();
}

function addMiscItem() {
  miscItems.push({ desc: '', amount: 0 });
  renderMiscTable();
}

function removeMiscItem(idx) {
  miscItems.splice(idx, 1);
  renderMiscTable();
  renderSummary();
}

function renderMiscTable() {
  const tbody = document.getElementById('misc_tbody');
  tbody.innerHTML = '';
  if (miscItems.length === 0) {
    tbody.innerHTML = '<tr><td colspan="3" style="color:#aaa;text-align:center;padding:10px">No misc items. Use the dropdown above to add common items.</td></tr>';
    renderSummary();
    return;
  }
  miscItems.forEach((it, idx) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><input type="text" value="${it.desc}" placeholder="Description"
        style="width:100%" onchange="miscItems[${idx}].desc=this.value;renderSummary()"/></td>
      <td><input type="number" value="${it.amount}" min="0" step="100"
        style="width:120px" onchange="miscItems[${idx}].amount=parseFloat(this.value)||0;renderSummary()"/></td>
      <td><button class="btn btn-danger btn-sm" onclick="removeMiscItem(${idx})">&#10005;</button></td>`;
    tbody.appendChild(tr);
  });
  const totalTr = document.createElement('tr');
  totalTr.className = 'total-row';
  totalTr.innerHTML = `<td style="text-align:right">Misc Total:</td><td colspan="2">${fmt(miscTotal())}</td>`;
  tbody.appendChild(totalTr);
}
