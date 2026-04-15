/**
 * BUG-014 FIX — Building Duplication & Templates for SA Estimator
 * ================================================================
 *
 * INSTRUCTIONS:
 *
 * 1. In templates/sa_calc.py, find the building buttons (lines 235-237):
 *
 *    <button class="btn btn-primary btn-sm" onclick="addBuilding()">+ Add Building</button>
 *    <button class="btn btn-outline btn-sm" onclick="removeBuilding()">Remove Last</button>
 *
 *    REPLACE with:
 *
 *    <div class="btn-group" style="display:flex;gap:6px;flex-wrap:wrap">
 *      <button class="btn btn-primary btn-sm" onclick="addBuilding()">+ Add Building</button>
 *      <button class="btn btn-outline btn-sm" onclick="removeBuilding()">Remove Last</button>
 *      <button class="btn btn-outline btn-sm" onclick="duplicateBuilding()" style="border-color:#6366F1;color:#6366F1">
 *        &#128203; Duplicate Selected
 *      </button>
 *      <button class="btn btn-outline btn-sm" onclick="showSaveTemplateModal()" style="border-color:#F59E0B;color:#F59E0B">
 *        &#128190; Save as Template
 *      </button>
 *      <button class="btn btn-outline btn-sm" onclick="showLoadTemplateModal()" style="border-color:#22C55E;color:#22C55E">
 *        &#128194; Load Template
 *      </button>
 *    </div>
 *
 * 2. Add the modal HTML (before </body> or at end of form):
 *
 *    <div class="modal-overlay" id="modal-save-template" style="display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);z-index:1000;align-items:center;justify-content:center">
 *      <div style="background:white;border-radius:12px;padding:24px;width:400px;max-width:90vw;box-shadow:0 20px 60px rgba(0,0,0,0.2)">
 *        <h3 style="margin:0 0 16px;color:#1E3A5F">Save Building Template</h3>
 *        <label style="display:block;font-size:0.8rem;font-weight:600;margin-bottom:4px">Template Name</label>
 *        <input type="text" id="template-name" placeholder="e.g., 40x60 Standard Tee" style="width:100%;padding:8px 12px;border:1.5px solid #D0D7E2;border-radius:6px;margin-bottom:12px"/>
 *        <p style="font-size:0.8rem;color:#64748B">Saves the currently selected building's dimensions and settings.</p>
 *        <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:16px">
 *          <button class="btn btn-outline btn-sm" onclick="closeSaveTemplateModal()">Cancel</button>
 *          <button class="btn btn-primary btn-sm" onclick="saveTemplate()">Save Template</button>
 *        </div>
 *      </div>
 *    </div>
 *
 *    <div class="modal-overlay" id="modal-load-template" style="display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);z-index:1000;align-items:center;justify-content:center">
 *      <div style="background:white;border-radius:12px;padding:24px;width:500px;max-width:90vw;box-shadow:0 20px 60px rgba(0,0,0,0.2)">
 *        <h3 style="margin:0 0 16px;color:#1E3A5F">Load Building Template</h3>
 *        <div id="template-list" style="max-height:300px;overflow-y:auto"></div>
 *        <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:16px">
 *          <button class="btn btn-outline btn-sm" onclick="closeLoadTemplateModal()">Cancel</button>
 *        </div>
 *      </div>
 *    </div>
 *
 * 3. Add these JS functions to the script section:
 */

// ─────────────────────────────────────────────
// BUILDING DUPLICATION (BUG-014)
// ─────────────────────────────────────────────

let selectedBuildingIdx = 0; // Track which building is selected

/**
 * Duplicate the currently selected building.
 */
function duplicateBuilding() {
  if (buildings.length === 0) return;

  const idx = selectedBuildingIdx || 0;
  const source = buildings[idx];
  bldgCounter++;

  // Deep clone the building config
  const clone = JSON.parse(JSON.stringify(source));
  clone.id = `B${bldgCounter}`;
  clone.building_id = `B${bldgCounter}`;
  clone.building_name = source.building_name + ' (Copy)';

  buildings.push(clone);
  renderBuildingList();
  renderBuildingForms();

  // Show toast or feedback
  const toast = document.createElement('div');
  toast.style.cssText = 'position:fixed;top:20px;right:20px;background:#22C55E;color:white;padding:12px 20px;border-radius:8px;z-index:9999;font-weight:600;box-shadow:0 4px 12px rgba(0,0,0,0.15)';
  toast.textContent = `Duplicated "${source.building_name}" as "${clone.building_name}"`;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

// ─────────────────────────────────────────────
// BUILDING TEMPLATES (BUG-014)
// ─────────────────────────────────────────────

const TEMPLATE_STORAGE_KEY = 'tf_building_templates';

function getBuildingTemplates() {
  try {
    const raw = localStorage.getItem(TEMPLATE_STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch(e) {
    return [];
  }
}

function saveBuildingTemplates(templates) {
  try {
    localStorage.setItem(TEMPLATE_STORAGE_KEY, JSON.stringify(templates));
  } catch(e) {
    // Fallback: save via API
    fetch('/api/building-templates', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({templates: templates})
    }).catch(() => {});
  }
}

function showSaveTemplateModal() {
  if (buildings.length === 0) return;
  const modal = document.getElementById('modal-save-template');
  modal.style.display = 'flex';
  document.getElementById('template-name').value = buildings[selectedBuildingIdx || 0].building_name;
  document.getElementById('template-name').focus();
}

function closeSaveTemplateModal() {
  document.getElementById('modal-save-template').style.display = 'none';
}

function saveTemplate() {
  const name = document.getElementById('template-name').value.trim();
  if (!name) { alert('Please enter a template name'); return; }

  const source = buildings[selectedBuildingIdx || 0];
  const template = {
    name: name,
    created: new Date().toISOString(),
    config: {
      type: source.type,
      width_ft: source.width_ft,
      length_mode: source.length_mode,
      length_ft: source.length_ft,
      n_spaces: source.n_spaces,
      space_width_ft: source.space_width_ft,
      overhang_mode: source.overhang_mode,
      clear_height_ft: source.clear_height_ft,
      max_bay_ft: source.max_bay_ft,
      pitch_key: source.pitch_key,
      purlin_spacing_override: source.purlin_spacing_override,
      embedment_ft: source.embedment_ft,
      column_buffer_ft: source.column_buffer_ft,
      reinforced: source.reinforced,
      rebar_col_size: source.rebar_col_size,
      rebar_beam_size: source.rebar_beam_size,
      straps_per_rafter: source.straps_per_rafter,
      strap_length_in: source.strap_length_in,
      include_back_wall: source.include_back_wall,
      include_end_walls: source.include_end_walls,
      include_side_walls: source.include_side_walls,
      include_rafter_rebar: source.include_rafter_rebar,
      rebar_rafter_size: source.rebar_rafter_size,
      include_trim: source.include_trim,
      include_labor: source.include_labor,
    }
  };

  const templates = getBuildingTemplates();
  templates.push(template);
  saveBuildingTemplates(templates);
  closeSaveTemplateModal();

  // Toast
  const toast = document.createElement('div');
  toast.style.cssText = 'position:fixed;top:20px;right:20px;background:#F59E0B;color:white;padding:12px 20px;border-radius:8px;z-index:9999;font-weight:600;box-shadow:0 4px 12px rgba(0,0,0,0.15)';
  toast.textContent = `Template "${name}" saved!`;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

function showLoadTemplateModal() {
  const templates = getBuildingTemplates();
  const listEl = document.getElementById('template-list');

  if (templates.length === 0) {
    listEl.innerHTML = '<p style="color:#94A3B8;text-align:center;padding:20px">No saved templates yet. Save a building configuration first.</p>';
  } else {
    listEl.innerHTML = templates.map((t, i) => `
      <div style="display:flex;align-items:center;justify-content:space-between;padding:10px 14px;border:1px solid #E2E8F0;border-radius:8px;margin-bottom:8px;background:#F8FAFC">
        <div>
          <div style="font-weight:600;color:#1E3A5F">${t.name}</div>
          <div style="font-size:0.75rem;color:#94A3B8">${t.config.type} — ${t.config.width_ft}'W × ${t.config.length_ft}'L × ${t.config.clear_height_ft}'H | Created ${new Date(t.created).toLocaleDateString()}</div>
        </div>
        <div style="display:flex;gap:6px">
          <button class="btn btn-primary btn-sm" onclick="loadTemplate(${i})">Load</button>
          <button class="btn btn-outline btn-sm" style="color:#EF4444;border-color:#EF4444" onclick="deleteTemplate(${i})">&#10005;</button>
        </div>
      </div>
    `).join('');
  }

  document.getElementById('modal-load-template').style.display = 'flex';
}

function closeLoadTemplateModal() {
  document.getElementById('modal-load-template').style.display = 'none';
}

function loadTemplate(idx) {
  const templates = getBuildingTemplates();
  if (!templates[idx]) return;

  bldgCounter++;
  const config = templates[idx].config;
  const newBldg = {
    id: `B${bldgCounter}`,
    building_id: `B${bldgCounter}`,
    building_name: templates[idx].name,
    ...config,
    coil_prices: {},
  };

  buildings.push(newBldg);
  renderBuildingList();
  renderBuildingForms();
  closeLoadTemplateModal();

  const toast = document.createElement('div');
  toast.style.cssText = 'position:fixed;top:20px;right:20px;background:#22C55E;color:white;padding:12px 20px;border-radius:8px;z-index:9999;font-weight:600;box-shadow:0 4px 12px rgba(0,0,0,0.15)';
  toast.textContent = `Loaded template "${templates[idx].name}"`;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

function deleteTemplate(idx) {
  if (!confirm('Delete this template?')) return;
  const templates = getBuildingTemplates();
  templates.splice(idx, 1);
  saveBuildingTemplates(templates);
  showLoadTemplateModal(); // Refresh the list
}
