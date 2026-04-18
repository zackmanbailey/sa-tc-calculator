"""
TitanForge — PQR (Procedure Qualification Record) Management Page
==================================================================
Lists all PQR records with add/edit/delete functionality.
PQRs back WPS documents with tensile, bend, macro etch, and impact test results.
"""

PQR_PAGE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TitanForge — PQR Management</title>
</head>
<body>
<style>
  .pqr-page { padding: 24px; max-width: 1200px; }
  .pqr-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
  .pqr-header h1 { font-size: 24px; font-weight: 800; color: #FFF; margin-bottom: 4px; }
  .pqr-header p { color: #94A3B8; font-size: 14px; }
  .pqr-add-btn {
    padding: 10px 20px; background: #1E40AF; color: #FFF; border: none;
    border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; white-space: nowrap;
  }
  .pqr-add-btn:hover { background: #1D4ED8; }

  .pqr-table-wrap {
    background: #111827; border: 1px solid #1E293B; border-radius: 12px;
    overflow-x: auto;
  }
  .pqr-table {
    width: 100%; border-collapse: collapse; font-size: 13px;
  }
  .pqr-table th {
    text-align: left; padding: 12px 14px; color: #64748B; font-size: 11px;
    text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid #1E293B;
    background: #0F172A; white-space: nowrap;
  }
  .pqr-table td {
    padding: 12px 14px; color: #CBD5E1; border-bottom: 1px solid #1E293B;
    vertical-align: middle;
  }
  .pqr-table tr:last-child td { border-bottom: none; }
  .pqr-table tr:hover td { background: #1A2332; }

  .pqr-badge {
    display: inline-block; padding: 3px 10px; border-radius: 20px;
    font-size: 11px; font-weight: 700; text-transform: uppercase;
  }
  .pqr-badge.active { background: #14532D; color: #10B981; }
  .pqr-badge.expired { background: #7F1D1D; color: #DC2626; }
  .pqr-badge.superseded { background: #78350F; color: #F59E0B; }

  .pqr-wps-tag {
    display: inline-block; padding: 2px 8px; border-radius: 4px;
    font-size: 11px; font-weight: 600; background: #1E3A5F; color: #60A5FA;
    margin: 1px 2px; cursor: pointer; text-decoration: none;
  }
  .pqr-wps-tag:hover { background: #1E40AF; color: #FFF; }

  .pqr-test-dot {
    display: inline-block; width: 8px; height: 8px; border-radius: 50%;
    margin-right: 4px; vertical-align: middle;
  }
  .pqr-test-dot.passed { background: #10B981; }
  .pqr-test-dot.failed { background: #DC2626; }
  .pqr-test-dot.na { background: #475569; }

  .pqr-actions button {
    padding: 5px 10px; border: 1px solid #334155; border-radius: 6px;
    font-size: 12px; cursor: pointer; margin-left: 4px;
  }
  .pqr-edit-btn { background: #1E293B; color: #94A3B8; }
  .pqr-edit-btn:hover { background: #334155; color: #FFF; }
  .pqr-del-btn { background: #1E293B; color: #DC2626; border-color: #7F1D1D; }
  .pqr-del-btn:hover { background: #7F1D1D; color: #FFF; }

  .pqr-empty {
    color: #475569; padding: 48px; text-align: center;
    background: #111827; border: 1px solid #1E293B; border-radius: 12px;
  }

  /* Modal */
  .pqr-overlay {
    display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 999;
  }
  .pqr-modal {
    display: none; position: fixed; top: 50%; left: 50%; transform: translate(-50%,-50%);
    z-index: 1000; width: 620px; max-height: 90vh; overflow-y: auto;
    background: #111827; border: 1px solid #1E293B; border-radius: 12px; padding: 24px;
  }
  .pqr-modal h3 { color: #FFF; margin-bottom: 16px; font-size: 18px; }
  .pqr-modal label {
    font-size: 12px; color: #64748B; display: block; margin-bottom: 4px;
  }
  .pqr-modal input, .pqr-modal select, .pqr-modal textarea {
    width: 100%; padding: 8px; background: #0F172A; border: 1px solid #334155;
    border-radius: 6px; color: #FFF; box-sizing: border-box; font-size: 13px;
  }
  .pqr-modal textarea { resize: vertical; }
  .pqr-form-grid {
    display: grid; grid-template-columns: 1fr 1fr; gap: 12px;
  }
  .pqr-form-grid .span2 { grid-column: span 2; }

  .pqr-test-section {
    margin-top: 12px; padding: 14px; background: #0F172A; border: 1px solid #1E293B;
    border-radius: 8px;
  }
  .pqr-test-section h4 { color: #94A3B8; font-size: 13px; margin-bottom: 10px; font-weight: 700; }
  .pqr-test-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }

  .pqr-modal-actions { margin-top: 16px; display: flex; gap: 8px; }
  .pqr-save-btn {
    padding: 8px 24px; background: #10B981; color: #FFF; border: none;
    border-radius: 6px; font-weight: 600; cursor: pointer;
  }
  .pqr-save-btn:hover { background: #059669; }
  .pqr-cancel-btn {
    padding: 8px 24px; background: #334155; color: #CBD5E1; border: none;
    border-radius: 6px; cursor: pointer;
  }
  .pqr-cancel-btn:hover { background: #475569; }
</style>

<div class="pqr-page">
  <div class="pqr-header">
    <div>
      <h1>Procedure Qualification Records (PQR)</h1>
      <p>Test records backing each WPS &mdash; tensile, bend, macro etch, and impact results per AWS D1.1 &sect;4.8.</p>
    </div>
    <button class="pqr-add-btn" onclick="pqrShowAdd()">+ Add PQR</button>
  </div>

  <div id="pqrTableWrap"></div>

  <!-- Modal Overlay -->
  <div class="pqr-overlay" id="pqrOverlay" onclick="pqrCloseModal()"></div>

  <!-- Add/Edit Modal -->
  <div class="pqr-modal" id="pqrModal">
    <h3 id="pqrModalTitle">Add PQR</h3>
    <input type="hidden" id="fPqrId">
    <div class="pqr-form-grid">
      <div>
        <label>PQR Number (user-facing)</label>
        <input id="fPqrNumber" placeholder="e.g. PQR-001">
      </div>
      <div>
        <label>Welding Process</label>
        <select id="fProcess">
          <option value="GMAW">GMAW (MIG)</option>
          <option value="SMAW">SMAW (Stick)</option>
          <option value="FCAW">FCAW (Flux Core)</option>
          <option value="GTAW">GTAW (TIG)</option>
          <option value="SAW">SAW (Submerged Arc)</option>
        </select>
      </div>
      <div>
        <label>Base Metal 1</label>
        <input id="fBaseMetal1" placeholder="e.g. A36">
      </div>
      <div>
        <label>Base Metal 2</label>
        <input id="fBaseMetal2" placeholder="e.g. A572 Gr 50">
      </div>
      <div>
        <label>Filler Metal</label>
        <input id="fFillerMetal" placeholder="e.g. E7018">
      </div>
      <div>
        <label>Thickness Range</label>
        <input id="fThicknessRange" placeholder='e.g. 1/4" to 3/4"'>
      </div>
      <div>
        <label>Position</label>
        <select id="fPosition">
          <option value="All">All Positions</option>
          <option value="1G">1G (Flat)</option>
          <option value="2G">2G (Horizontal)</option>
          <option value="3G">3G (Vertical)</option>
          <option value="4G">4G (Overhead)</option>
          <option value="1F">1F (Flat Fillet)</option>
          <option value="2F">2F (Horizontal Fillet)</option>
          <option value="3F">3F (Vertical Fillet)</option>
          <option value="4F">4F (Overhead Fillet)</option>
          <option value="1G,2G,3G">1G, 2G, 3G</option>
          <option value="1F,2F,3F,4F">1F, 2F, 3F, 4F</option>
        </select>
      </div>
      <div>
        <label>Status</label>
        <select id="fStatus">
          <option value="active">Active</option>
          <option value="expired">Expired</option>
          <option value="superseded">Superseded</option>
        </select>
      </div>
      <div>
        <label>Test Date</label>
        <input id="fTestDate" type="date">
      </div>
      <div>
        <label>Tested By</label>
        <input id="fTestedBy" placeholder="Inspector name">
      </div>
      <div class="span2">
        <label>Test Lab</label>
        <input id="fTestLab" placeholder="Lab name">
      </div>
      <div class="span2">
        <label>WPS References (comma-separated)</label>
        <input id="fWpsRefs" placeholder="e.g. WPS-B, WPS-C">
      </div>
    </div>

    <!-- Test Results Section -->
    <div class="pqr-test-section">
      <h4>Test Results</h4>
      <div class="pqr-test-grid">
        <div>
          <label>Tensile Test</label>
          <select id="fTestTensile">
            <option value="passed">Passed</option>
            <option value="failed">Failed</option>
            <option value="N/A">N/A</option>
          </select>
        </div>
        <div>
          <label>Bend Test</label>
          <select id="fTestBend">
            <option value="passed">Passed</option>
            <option value="failed">Failed</option>
            <option value="N/A">N/A</option>
          </select>
        </div>
        <div>
          <label>Macro Etch</label>
          <select id="fTestMacro">
            <option value="passed">Passed</option>
            <option value="failed">Failed</option>
            <option value="N/A">N/A</option>
          </select>
        </div>
        <div>
          <label>Impact Test</label>
          <select id="fTestImpact">
            <option value="N/A">N/A</option>
            <option value="passed">Passed</option>
            <option value="failed">Failed</option>
          </select>
        </div>
      </div>
    </div>

    <div class="pqr-form-grid" style="margin-top:12px;">
      <div class="span2">
        <label>Notes</label>
        <textarea id="fNotes" rows="2" placeholder="Additional notes..."></textarea>
      </div>
    </div>

    <div class="pqr-modal-actions">
      <button class="pqr-save-btn" onclick="pqrSave()">Save</button>
      <button class="pqr-cancel-btn" onclick="pqrCloseModal()">Cancel</button>
    </div>
  </div>
</div>

<script>
(function() {
  var STATUS_BADGE = {active:'active', expired:'expired', superseded:'superseded'};
  var TEST_DOT = {passed:'passed', failed:'failed'};

  function dotClass(v) { return TEST_DOT[v] || 'na'; }
  function dotLabel(v) { return v === 'N/A' ? 'N/A' : (v || 'N/A'); }

  function renderTestDot(val) {
    var cls = dotClass(val);
    var label = dotLabel(val);
    return '<span class="pqr-test-dot ' + cls + '"></span>' + label;
  }

  function renderWpsTags(refs) {
    if (!refs || !refs.length) return '<span style="color:#475569;">None</span>';
    var h = '';
    for (var i = 0; i < refs.length; i++) {
      h += '<a href="/qa/wps" class="pqr-wps-tag">' + refs[i] + '</a>';
    }
    return h;
  }

  function renderTable(pqrs) {
    if (!pqrs || pqrs.length === 0) {
      return '<div class="pqr-empty">No PQR records yet. Click <strong>+ Add PQR</strong> to create the first record.</div>';
    }
    var h = '<div class="pqr-table-wrap"><table class="pqr-table"><thead><tr>';
    h += '<th>PQR #</th><th>Process</th><th>Base Metals</th><th>Filler</th>';
    h += '<th>Thickness</th><th>Position</th><th>Tests</th><th>Status</th>';
    h += '<th>Test Date</th><th>WPS Refs</th><th>Actions</th>';
    h += '</tr></thead><tbody>';
    for (var i = 0; i < pqrs.length; i++) {
      var p = pqrs[i];
      var st = p.status || 'active';
      var tr = p.test_results || {};
      h += '<tr>';
      h += '<td style="font-weight:700;color:#FFF;">' + (p.pqr_number || p.pqr_id || '—') + '</td>';
      h += '<td>' + (p.process || '—') + '</td>';
      h += '<td>' + (p.base_metal_1 || '—') + ' / ' + (p.base_metal_2 || '—') + '</td>';
      h += '<td>' + (p.filler_metal || '—') + '</td>';
      h += '<td>' + (p.thickness_range || '—') + '</td>';
      h += '<td>' + (p.position || '—') + '</td>';
      h += '<td style="font-size:11px;line-height:1.8;">';
      h += 'T:' + renderTestDot(tr.tensile) + ' B:' + renderTestDot(tr.bend) + '<br>';
      h += 'M:' + renderTestDot(tr.macro_etch) + ' I:' + renderTestDot(tr.impact);
      h += '</td>';
      h += '<td><span class="pqr-badge ' + STATUS_BADGE[st] + '">' + st + '</span></td>';
      h += '<td>' + (p.test_date || '—') + '</td>';
      h += '<td>' + renderWpsTags(p.wps_refs) + '</td>';
      h += '<td class="pqr-actions">';
      h += '<button class="pqr-edit-btn" data-rec="' + btoa(JSON.stringify(p)) + '" onclick="pqrEdit(this)">Edit</button>';
      h += '<button class="pqr-del-btn" onclick="pqrDelete(\'' + (p.pqr_id || '') + '\')">Del</button>';
      h += '</td>';
      h += '</tr>';
    }
    h += '</tbody></table></div>';
    return h;
  }

  window.pqrLoadAll = function() {
    fetch('/api/qa/pqr').then(function(r){ return r.json(); }).then(function(d) {
      if (!d.ok) { document.getElementById('pqrTableWrap').innerHTML = '<div style="color:#DC2626;">Error loading PQRs</div>'; return; }
      document.getElementById('pqrTableWrap').innerHTML = renderTable(d.pqrs || []);
    }).catch(function(e) {
      document.getElementById('pqrTableWrap').innerHTML = '<div style="color:#DC2626;">Failed to load PQR data.</div>';
    });
  };

  window.pqrShowAdd = function() {
    document.getElementById('pqrModalTitle').textContent = 'Add PQR';
    document.getElementById('fPqrId').value = '';
    document.getElementById('fPqrNumber').value = '';
    document.getElementById('fProcess').value = 'GMAW';
    document.getElementById('fBaseMetal1').value = '';
    document.getElementById('fBaseMetal2').value = '';
    document.getElementById('fFillerMetal').value = '';
    document.getElementById('fThicknessRange').value = '';
    document.getElementById('fPosition').value = 'All';
    document.getElementById('fStatus').value = 'active';
    document.getElementById('fTestDate').value = '';
    document.getElementById('fTestedBy').value = '';
    document.getElementById('fTestLab').value = '';
    document.getElementById('fWpsRefs').value = '';
    document.getElementById('fTestTensile').value = 'passed';
    document.getElementById('fTestBend').value = 'passed';
    document.getElementById('fTestMacro').value = 'passed';
    document.getElementById('fTestImpact').value = 'N/A';
    document.getElementById('fNotes').value = '';
    document.getElementById('pqrModal').style.display = 'block';
    document.getElementById('pqrOverlay').style.display = 'block';
  };

  window.pqrEdit = function(btn) {
    var p = JSON.parse(atob(btn.dataset.rec));
    document.getElementById('pqrModalTitle').textContent = 'Edit PQR';
    document.getElementById('fPqrId').value = p.pqr_id || '';
    document.getElementById('fPqrNumber').value = p.pqr_number || '';
    document.getElementById('fProcess').value = p.process || 'GMAW';
    document.getElementById('fBaseMetal1').value = p.base_metal_1 || '';
    document.getElementById('fBaseMetal2').value = p.base_metal_2 || '';
    document.getElementById('fFillerMetal').value = p.filler_metal || '';
    document.getElementById('fThicknessRange').value = p.thickness_range || '';
    document.getElementById('fPosition').value = p.position || 'All';
    document.getElementById('fStatus').value = p.status || 'active';
    document.getElementById('fTestDate').value = p.test_date || '';
    document.getElementById('fTestedBy').value = p.tested_by || '';
    document.getElementById('fTestLab').value = p.test_lab || '';
    document.getElementById('fWpsRefs').value = (p.wps_refs || []).join(', ');
    var tr = p.test_results || {};
    document.getElementById('fTestTensile').value = tr.tensile || 'N/A';
    document.getElementById('fTestBend').value = tr.bend || 'N/A';
    document.getElementById('fTestMacro').value = tr.macro_etch || 'N/A';
    document.getElementById('fTestImpact').value = tr.impact || 'N/A';
    document.getElementById('fNotes').value = p.notes || '';
    document.getElementById('pqrModal').style.display = 'block';
    document.getElementById('pqrOverlay').style.display = 'block';
  };

  window.pqrCloseModal = function() {
    document.getElementById('pqrModal').style.display = 'none';
    document.getElementById('pqrOverlay').style.display = 'none';
  };

  window.pqrSave = function() {
    var wpsRaw = document.getElementById('fWpsRefs').value;
    var wpsRefs = wpsRaw ? wpsRaw.split(',').map(function(s){ return s.trim(); }).filter(function(s){ return s; }) : [];
    var record = {
      pqr_number: document.getElementById('fPqrNumber').value,
      process: document.getElementById('fProcess').value,
      base_metal_1: document.getElementById('fBaseMetal1').value,
      base_metal_2: document.getElementById('fBaseMetal2').value,
      filler_metal: document.getElementById('fFillerMetal').value,
      thickness_range: document.getElementById('fThicknessRange').value,
      position: document.getElementById('fPosition').value,
      status: document.getElementById('fStatus').value,
      test_date: document.getElementById('fTestDate').value,
      tested_by: document.getElementById('fTestedBy').value,
      test_lab: document.getElementById('fTestLab').value,
      wps_refs: wpsRefs,
      test_results: {
        tensile: document.getElementById('fTestTensile').value,
        bend: document.getElementById('fTestBend').value,
        macro_etch: document.getElementById('fTestMacro').value,
        impact: document.getElementById('fTestImpact').value
      },
      notes: document.getElementById('fNotes').value
    };
    var pqrId = document.getElementById('fPqrId').value;
    if (pqrId) record.pqr_id = pqrId;

    fetch('/api/qa/pqr', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(record)
    }).then(function(r){ return r.json(); }).then(function(d) {
      if (d.ok) { pqrCloseModal(); pqrLoadAll(); }
      else { alert('Error: ' + (d.error || 'Unknown')); }
    }).catch(function(e) { alert('Save failed: ' + e); });
  };

  window.pqrDelete = function(pqrId) {
    if (!confirm('Delete this PQR record? This cannot be undone.')) return;
    fetch('/api/qa/pqr', {
      method: 'DELETE',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({pqr_id: pqrId})
    }).then(function(r){ return r.json(); }).then(function(d) {
      if (d.ok) { pqrLoadAll(); }
      else { alert('Error: ' + (d.error || 'Unknown')); }
    });
  };

  // Load on page init
  pqrLoadAll();
})();
</script>
</body>
</html>
"""
