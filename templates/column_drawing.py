"""
TitanForge v4.2 — Interactive Column Shop Drawing Template
==============================================================
Interactive SVG-based column drawing with parameter controls and
AWS weld notation. Embeds the full ColumnShopDrawing_v9 application
with TitanForge integration for fetching project configuration.
"""

COLUMN_DRAWING_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TitanForge — Column Shop Drawing v9</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #0F172A; color: #F1F5F9; min-height: 100vh;
    display: flex; flex-direction: column;
  }
  .top-bar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 20px; background: #1E293B; border-bottom: 1px solid #334155;
    flex-wrap: wrap; gap: 8px;
  }
  .top-bar h1 { font-size: 1rem; font-weight: 700; color: #F6AE2D; }
  .top-bar .back-link {
    padding: 6px 12px; background: #334155; color: #94A3B8; border: 1px solid #475569;
    border-radius: 5px; text-decoration: none; font-size: 0.78rem; cursor: pointer;
    transition: all 0.2s;
  }
  .top-bar .back-link:hover {
    background: #475569; color: #F1F5F9;
  }
  .top-bar .job-code-label {
    font-size: 0.85rem; color: #94A3B8;
  }
  .controls { display: flex; gap: 14px; align-items: center; flex-wrap: wrap; }
  .ctrl-group { display: flex; align-items: center; gap: 6px; }
  .ctrl-group label { font-size: 0.75rem; color: #94A3B8; white-space: nowrap; }
  .ctrl-group select, .ctrl-group input[type=number] {
    background: #334155; color: #F1F5F9; border: 1px solid #475569;
    border-radius: 5px; padding: 5px 8px; font-size: 0.8rem; width: 80px;
  }
  .ctrl-group input[type=range] { width: 100px; }
  .ctrl-val { color: #F6AE2D; font-weight: 700; font-size: 0.85rem; min-width: 28px; }
  .toggle-btn {
    background: #334155; color: #94A3B8; border: 1px solid #475569;
    border-radius: 5px; padding: 5px 12px; font-size: 0.78rem; cursor: pointer;
    transition: all 0.2s;
  }
  .toggle-btn.active { background: #F6AE2D; color: #0F172A; border-color: #F6AE2D; font-weight: 700; }
  .btn-gold {
    background: #F6AE2D; color: #0F172A; border: none; border-radius: 5px;
    padding: 5px 14px; font-weight: 700; font-size: 0.78rem; cursor: pointer;
  }
  .canvas-wrap { flex: 1; overflow: auto; display: flex; justify-content: center; padding: 12px; }
  .drawing-sheet {
    background: #FFF; box-shadow: 0 4px 24px rgba(0,0,0,0.5);
    width: 1100px; height: 850px; flex-shrink: 0;
  }
  .drawing-sheet svg { width: 100%; height: 100%; }

  .obj { stroke: #1a1a1a; fill: none; }
  .thick { stroke-width: 2.0; }
  .med { stroke-width: 1.0; }
  .thin { stroke-width: 0.5; }
  .hair { stroke-width: 0.3; }
  .hidden { stroke: #777; stroke-width: 0.5; stroke-dasharray: 6,3; fill: none; }
  .center { stroke: #999; stroke-width: 0.3; stroke-dasharray: 14,3,3,3; fill: none; }
  .dim { stroke: #555; stroke-width: 0.3; fill: none; }
  .dimtxt { font: 700 7.5px 'Courier New', monospace; fill: #333; text-anchor: middle; }
  .lbl { font: 8px Arial, sans-serif; fill: #333; }
  .lblb { font: 700 8px Arial, sans-serif; fill: #1a1a1a; }
  .ttl { font: 700 12px Arial, sans-serif; fill: #1a1a1a; text-anchor: middle; }
  .note { font: 6.5px Arial, sans-serif; fill: #555; }
  .noteb { font: 700 6.5px Arial, sans-serif; fill: #333; }
  .cee { fill: #F0F0F0; stroke: #1a1a1a; stroke-width: 1.5; }
  .cap { fill: #E0E0E0; stroke: #1a1a1a; stroke-width: 1.2; }
  .gus { fill: #D8D8D8; stroke: #1a1a1a; stroke-width: 1.0; }
  .rebar-solid { fill: #CC4400; stroke: #993300; stroke-width: 0.6; }
  .rebar-dot-rect { fill: #CC440050; stroke: #CC4400; stroke-width: 1.5; stroke-dasharray: 4,3; }
  .rebar-circ { fill: #CC4400; stroke: #993300; stroke-width: 0.8; }
  .rebar-circ-out { fill: none; stroke: #CC4400; stroke-width: 1.2; }
  .bolt { fill: #FFF; stroke: #1a1a1a; stroke-width: 0.8; }
  .nopaint { fill: #FF6600; fill-opacity: 0.12; stroke: #FF6600; stroke-width: 0.4; stroke-dasharray: 4,2; }
  .cut-line { stroke: #CC0000; stroke-width: 0.8; fill: none; }
  .weld { stroke: #0055AA; stroke-width: 0.8; fill: none; }
  .ang-fill { fill: #FFF8E7; stroke: #C4960B; stroke-width: 0.6; }
  .rebar-dim { stroke: #CC4400; stroke-width: 0.3; fill: none; }
  .rebar-dimtxt { font: 700 7px 'Courier New', monospace; fill: #CC4400; text-anchor: middle; }

  /* AWS Weld Symbols */
  .weld-ref { stroke: #0055AA; stroke-width: 0.8; fill: none; }
  .weld-arrow { stroke: #0055AA; stroke-width: 0.8; fill: #0055AA; }
  .weld-sym { stroke: #0055AA; stroke-width: 0.7; fill: none; }
  .weld-sym-filled { stroke: #0055AA; stroke-width: 0.7; fill: #0055AA; }
  .weld-txt { font: 600 5.5px 'Courier New', monospace; fill: #0055AA; }
  .weld-tail { stroke: #0055AA; stroke-width: 0.6; fill: none; }
  .weld-circ { stroke: #0055AA; stroke-width: 0.7; fill: none; }
  .weld-leader { stroke: #0055AA; stroke-width: 0.6; fill: none; }
  .dim-bold { font: 700 9.5px 'Courier New', monospace; fill: #1a1a1a; text-anchor: middle; }
  .settings-panel { position: fixed; left: -380px; top: 0; bottom: 0; width: 360px;
    background: #1E293B; border-right: 2px solid #F6AE2D; z-index: 50;
    transition: left 0.3s; padding: 20px; overflow-y: auto; }
  .settings-panel.open { left: 0; }
  .settings-panel h2 { color: #F6AE2D; font-size: 1rem; margin-bottom: 12px; }
  .settings-panel label { display: block; color: #94A3B8; font-size: 0.75rem; margin-top: 10px; }
  .settings-panel input { width: 100%; background: #334155; color: #F1F5F9; border: 1px solid #475569;
    border-radius: 5px; padding: 6px 8px; font-size: 0.8rem; margin-top: 4px; }
  .settings-x { position: absolute; top: 10px; right: 12px; background: none; border: none; color: #94A3B8; font-size: 1.2rem; cursor: pointer; }
  .warn-text { font: 700 8px Arial, sans-serif; fill: #CC0000; }

  .hover-part { cursor: pointer; }
  .hover-part:hover { filter: drop-shadow(0 0 5px rgba(246,174,45,0.6)); }

  .tip {
    position: fixed; background: #1E293B; color: #F1F5F9;
    border: 1px solid #F6AE2D; border-radius: 8px; padding: 10px 14px;
    font-size: 0.78rem; pointer-events: none; z-index: 100; max-width: 300px; display: none;
    box-shadow: 0 4px 16px rgba(0,0,0,0.5);
  }
  .tip b { color: #F6AE2D; }
  .tip .r { display: flex; justify-content: space-between; gap: 12px; padding: 1px 0; }
  .tip .k { color: #94A3B8; } .tip .v { font-weight: 600; }

  .bom { position: fixed; right: -400px; top: 0; bottom: 0; width: 380px;
    background: #1E293B; border-left: 2px solid #F6AE2D; z-index: 50;
    transition: right 0.3s; padding: 20px; overflow-y: auto; }
  .bom.open { right: 0; }
  .bom h2 { color: #F6AE2D; font-size: 1rem; margin-bottom: 12px; }
  .bom table { width: 100%; border-collapse: collapse; font-size: 0.75rem; }
  .bom th { background: #334155; color: #F6AE2D; padding: 5px 6px; text-align: left; }
  .bom td { padding: 4px 6px; border-bottom: 1px solid #334155; color: #CBD5E1; }
  .bom-x { position: absolute; top: 10px; right: 12px; background: none; border: none; color: #94A3B8; font-size: 1.2rem; cursor: pointer; }

  .foot { display: flex; gap: 20px; padding: 8px 20px; background: #1E293B;
    border-top: 1px solid #334155; font-size: 0.75rem; color: #94A3B8; flex-wrap: wrap; }
  .foot .s { color: #F6AE2D; font-weight: 600; }

  /* Approval modal */
  .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.7); z-index: 200; display: none;
    align-items: center; justify-content: center; }
  .modal-overlay.show { display: flex; }
  .modal-box { background: #1E293B; border: 2px solid #F6AE2D; border-radius: 12px;
    padding: 28px 32px; max-width: 440px; width: 90%; text-align: center; }
  .modal-box h3 { color: #F6AE2D; font-size: 1.1rem; margin-bottom: 12px; }
  .modal-box p { color: #CBD5E1; font-size: 0.85rem; line-height: 1.5; margin-bottom: 16px; }
  .modal-box .warn { color: #EF4444; font-weight: 700; font-size: 0.8rem; margin-bottom: 16px; }
  .modal-btns { display: flex; gap: 12px; justify-content: center; }
  .modal-btns button { padding: 8px 20px; border-radius: 6px; font-size: 0.85rem; cursor: pointer; border: none; font-weight: 600; }
  .modal-btns .ok { background: #F6AE2D; color: #0F172A; }
  .modal-btns .cancel { background: #475569; color: #F1F5F9; }
  .checked-badge { display: inline-flex; align-items: center; gap: 6px; background: #065F46; color: #6EE7B7;
    padding: 3px 10px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; }
  .unchecked-badge { display: inline-flex; align-items: center; gap: 6px; background: #7C2D12; color: #FDBA74;
    padding: 3px 10px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; cursor: pointer; }
  .rev-history { margin-top: 8px; font-size: 0.7rem; color: #94A3B8; }
  .rev-history span { color: #F6AE2D; }

  /* Annotations */
  .anno-mode-btn { transition: all 0.2s; }
  .anno-mode-btn.active { background: #EF4444 !important; color: #FFF !important; border-color: #EF4444 !important; }
  .svg-annotation { cursor: move; }
  .svg-annotation:hover rect { filter: brightness(0.95); }
  .anno-del-circle:hover { opacity: 1 !important; }

  /* Weld Symbol Editor */
  .weld-editor { position: fixed; bottom: 0; left: 50%; transform: translateX(-50%);
    background: #1E293B; border: 2px solid #0055AA; border-bottom: none; border-radius: 12px 12px 0 0;
    padding: 14px 20px 10px; z-index: 60; display: none; min-width: 560px; max-width: 700px;
    box-shadow: 0 -4px 24px rgba(0,0,0,0.5); }
  .weld-editor.show { display: block; }
  .weld-editor h3 { color: #6CB4EE; font-size: 0.9rem; margin-bottom: 8px; display: flex;
    align-items: center; justify-content: space-between; }
  .weld-editor .we-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
  .weld-editor label { font-size: 0.7rem; color: #94A3B8; display: flex; flex-direction: column; gap: 2px; }
  .weld-editor input, .weld-editor select { background: #334155; color: #F1F5F9; border: 1px solid #475569;
    border-radius: 4px; padding: 4px 6px; font-size: 0.75rem; }
  .weld-editor input[type=range] { width: 100%; }
  .weld-editor .we-actions { display: flex; gap: 8px; margin-top: 10px; justify-content: flex-end; }
  .weld-editor .we-actions button { padding: 5px 14px; border-radius: 5px; font-size: 0.75rem;
    font-weight: 600; cursor: pointer; border: none; }
  .we-close { background: none; border: none; color: #94A3B8; font-size: 1.1rem; cursor: pointer; }
  .weld-group-interactive { cursor: pointer; }
  .weld-group-interactive:hover { filter: drop-shadow(0 0 3px rgba(0,85,170,0.6)); }
  .weld-group-interactive.selected { filter: drop-shadow(0 0 5px rgba(246,174,45,0.8)); }
  .weld-group-interactive.dragging { cursor: grabbing; }
  .rotation-handle { cursor: grab; }
  .rotation-handle:hover { filter: brightness(1.3); }
  .label-interactive { cursor: move; }
  .label-interactive:hover { filter: drop-shadow(0 0 2px rgba(0,170,85,0.6)); }
  .label-interactive.selected { filter: drop-shadow(0 0 4px rgba(246,174,45,0.8)); }

  @media print {
    .top-bar, .foot, .tip, .bom, .modal-overlay, .weld-editor { display: none !important; }
    .drawing-sheet { box-shadow: none; width: 100%; height: auto; }
    .canvas-wrap { padding: 0; }
    body { background: #fff; }
  }
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/svg2pdf.js/2.2.3/svg2pdf.umd.min.js"></script>
</head>
<body>

<div class="top-bar">
  <div style="display: flex; align-items: center; gap: 12px;">
    <a href="/shop-drawings/{{JOB_CODE}}" class="back-link">← Back to Shop Drawings</a>
    <h1>TitanForge — Column Shop Drawing</h1>
    <span class="job-code-label" id="jobCodeDisplay">Job: {{JOB_CODE}}</span>
  </div>
  <div class="controls">
    <div class="ctrl-group">
      <label>Pitch:</label>
      <input type="range" id="inPitch" min="0" max="20" step="0.1" value="1.2">
      <span class="ctrl-val" id="vPitch">1.2°</span>
    </div>
    <div class="ctrl-group">
      <label>Clear Ht:</label>
      <input type="number" id="inClearHt" value="14" min="8" max="40" step="0.5" style="width:60px;">
      <span class="lbl" style="color:#94A3B8;">ft</span>
    </div>
    <div class="ctrl-group">
      <label>Bldg Width:</label>
      <input type="number" id="inWidth" value="40" min="20" max="120" step="5" style="width:60px;">
      <span class="lbl" style="color:#94A3B8;">ft</span>
    </div>
    <div class="ctrl-group">
      <label>Footing:</label>
      <input type="number" id="inFooting" value="10" min="4" max="20" step="0.5" style="width:60px;">
      <span class="lbl" style="color:#94A3B8;">ft</span>
    </div>
    <div class="ctrl-group">
      <label>Rebar:</label>
      <select id="inRebar"><option>#5</option><option>#7</option><option selected>#9</option><option>#11</option></select>
    </div>
    <div class="ctrl-group">
      <label>Above Grade:</label>
      <input type="number" id="inAboveGrade" value="8" min="4" max="20" step="0.5" style="width:60px;">
      <span class="lbl" style="color:#94A3B8;">ft</span>
    </div>
    <div class="ctrl-group">
      <label>Cut Allow:</label>
      <input type="number" id="inCutAllowance" value="6" min="0" max="24" step="1" style="width:50px;">
      <span class="lbl" style="color:#94A3B8;">in</span>
    </div>
    <div class="ctrl-group">
      <button class="toggle-btn active" id="btnReinforced" onclick="toggleReinforced()">Reinforced</button>
      <button class="toggle-btn" id="btnNonReinforced" onclick="toggleReinforced()">Non-Reinforced</button>
    </div>
    <button class="btn-gold" onclick="document.getElementById('bomPanel').classList.toggle('open')">BOM</button>
    <button class="btn-gold" style="background:#475569;color:#F1F5F9;" onclick="window.print()">Print</button>
    <button class="btn-gold" id="btnSavePdf" style="background:#059669;color:#FFF;" onclick="savePdfToProject()" title="Generate PDF and save to project shop drawings">Save PDF to Project</button>
    <span id="savePdfStatus" style="font-size:0.7rem;color:#94A3B8;margin-left:4px;"></span>
    <button class="btn-gold" style="background:#334155;color:#F6AE2D;border:1px solid #F6AE2D;" onclick="resetZoom()">Reset Zoom</button>
    <button class="btn-gold" style="background:#334155;color:#94A3B8;border:1px solid #475569;font-size:0.9rem;" onclick="undo()" title="Undo (Cmd+Z)">↩</button>
    <button class="btn-gold" style="background:#334155;color:#94A3B8;border:1px solid #475569;font-size:0.9rem;" onclick="redo()" title="Redo (Cmd+Shift+Z)">↪</button>
    <button class="btn-gold" style="background:#334155;color:#F6AE2D;border:1px solid #475569;" onclick="document.getElementById('settingsPanel').classList.toggle('open')">⚙ Settings</button>
    <span id="checkBadge" class="unchecked-badge" onclick="startApproval()">✗ UNCHECKED</span>
    <button class="btn-gold anno-mode-btn" id="btnAnnotate" onclick="toggleAnnotateMode()">📝 Annotate</button>
    <button class="btn-gold" id="btnWeldEdit" style="background:#0055AA;color:#FFF;" onclick="toggleWeldEditMode()">🔧 Edit Welds</button>
    <button class="btn-gold" id="btnWeldReset" style="background:#7C2D12;color:#FDBA74;display:none;" onclick="resetAllWeldOverrides()">↺ Reset Welds</button>
    <button class="btn-gold" id="btnExportLayout" style="background:#334155;color:#94A3B8;border:1px solid #475569;display:none;" onclick="exportLayout()">📋 Export Layout</button>
  </div>
</div>

<!-- Approval modal -->
<div class="modal-overlay" id="approvalModal">
  <div class="modal-box">
    <h3>⚠ Drawing Approval</h3>
    <p>By checking this drawing, you are taking <b>full responsibility</b> for the accuracy of all dimensions, materials, and specifications shown.</p>
    <p class="warn">If something is incorrect, it is on YOU. This action creates a permanent record and can only be undone by creating a new revision.</p>
    <label style="display:block;color:#94A3B8;font-size:0.75rem;margin-bottom:10px;">Your Name:
      <input id="approverName" style="width:100%;background:#334155;color:#F1F5F9;border:1px solid #475569;border-radius:5px;padding:6px 8px;margin-top:4px;" placeholder="Enter your name">
    </label>
    <div class="modal-btns">
      <button class="ok" onclick="confirmApproval()">I Accept Responsibility</button>
      <button class="cancel" onclick="cancelApproval()">Cancel</button>
    </div>
  </div>
</div>

<div class="canvas-wrap">
  <div class="drawing-sheet">
    <svg id="svg" viewBox="0 0 1100 850" xmlns="http://www.w3.org/2000/svg"></svg>
  </div>
</div>

<div class="foot">
  <div>Weight: <span class="s" id="fWt">—</span></div>
  <div>Columns: <span class="s" id="fCols">10</span></div>
  <div>Col Length: <span class="s" id="fLen">—</span></div>
  <div>Rebar: <span class="s" id="fRbLen">—</span></div>
  <div>Gusset high: <span class="s" id="fGusH">—</span></div>
  <div>Gusset low: <span class="s" id="fGusL">—</span></div>
  <div>Angle Add: <span class="s" id="fAngAdd">—</span></div>
</div>

<div class="bom" id="bomPanel">
  <button class="bom-x" onclick="this.parentElement.classList.remove('open')">✕</button>
  <h2>Bill of Materials — Column <span id="bomMark">C1</span></h2>
  <table><thead><tr><th>Mk</th><th>Qty</th><th>Description</th><th>Size</th><th>Mat'l</th><th>Wt</th></tr></thead>
  <tbody id="bomTB"></tbody></table>
  <div style="margin-top:12px;border-top:1px solid #475569;padding-top:8px;font-size:0.85rem;">
    Total: <span class="s" id="bomTotal">—</span>
  </div>
</div>

<div class="tip" id="tip"></div>

<!-- Weld Symbol Editor Panel -->
<div class="weld-editor" id="weldEditor">
  <h3>
    <span>🔧 Weld Symbol: <span id="weId">—</span></span>
    <button class="we-close" onclick="closeWeldEditor()">✕</button>
  </h3>
  <div class="we-grid">
    <label>Fillet Size
      <input type="text" id="weSize" value="3/16" style="width:100%;">
    </label>
    <label>WPS Code
      <input type="text" id="weWps" value="F" style="width:100%;">
    </label>
    <label>Stitch
      <input type="text" id="weStitch" value="" placeholder="e.g. 3&quot;-36&quot; O.C." style="width:100%;">
    </label>
    <label>Ref Dir
      <select id="weRefDir"><option value="left">Left</option><option value="right">Right</option></select>
    </label>
    <label>Rotation (°)
      <input type="range" id="weRotation" min="-180" max="180" step="5" value="0">
      <span style="color:#6CB4EE;font-weight:600;font-size:0.75rem;" id="weRotVal">0°</span>
    </label>
    <label style="align-self:end;">
      <span style="display:flex;gap:8px;align-items:center;">
        <input type="checkbox" id="weAllAround" style="width:auto;"> All Around
      </span>
    </label>
    <label style="align-self:end;">
      <span style="display:flex;gap:8px;align-items:center;">
        <input type="checkbox" id="weBothSides" style="width:auto;"> Both Sides
      </span>
    </label>
  </div>
  <div style="margin-top:6px;padding:6px 0 0;border-top:1px solid #334155;font-size:0.68rem;color:#64748B;">
    Drag symbol to move · Rotation slider or grab handle to rotate · All changes are live
  </div>
  <div class="we-actions">
    <button style="background:#475569;color:#F1F5F9;" onclick="resetSelectedWeld()">↺ Reset This</button>
    <button class="we-apply-btn" style="background:#0055AA;color:#FFF;" onclick="applyWeldEdit()">✓ Apply</button>
    <button id="weSaveBtn" style="background:#F6AE2D;color:#0F172A;" onclick="saveWeldOverrides()">💾 Save All</button>
  </div>
</div>

<div class="settings-panel" id="settingsPanel">
  <button class="settings-x" onclick="this.parentElement.classList.remove('open')">✕</button>
  <h2>Project Settings</h2>
  <label>Project Name<input id="setProjectName" value="SMITH RESIDENCE 40x60"></label>
  <label>Customer<input id="setCustomer" value="" placeholder="Customer Name"></label>
  <label>Job Number<input id="setJobNumber" value="SA-2026-0147"></label>
  <label>Drawn By<input id="setDrawnBy" value="AUTO"></label>
  <label>Column Mark<input id="setColumnMark" value="C1"></label>
</div>

<script>
const C = {
  nFrames: 5, frameType: 'tee',
  ceeW: 14, ceeD: 4, ceeGauge: 0.135,
  capW: 26, capH: 14, capThick: 0.75,
  boltInset: 1.5, boltDia: 0.9375,
  gussetLeg: 6, gussetThick: 0.375,
  embedment: 4.333, colBuffer: 0.5,
};

function getParams() {
  return {
    pitch: parseFloat(document.getElementById('inPitch').value),
    clearHt: parseFloat(document.getElementById('inClearHt').value),
    width: parseFloat(document.getElementById('inWidth').value),
    footing: parseFloat(document.getElementById('inFooting').value),
    rebarSize: document.getElementById('inRebar').value,
    reinforced: document.getElementById('btnReinforced').classList.contains('active'),
    aboveGrade: parseFloat(document.getElementById('inAboveGrade').value),
    cutAllowance: parseFloat(document.getElementById('inCutAllowance').value), // inches
  };
}

function calc(p) {
  const rad = p.pitch * Math.PI / 180;
  const tan_s = Math.tan(rad);
  const sin_s = Math.sin(rad);

  const dist = p.width / (C.frameType === 'tee' ? 2 : 3);
  const angleAdd = dist * tan_s;
  const totalLengthFt = p.clearHt + angleAdd + C.embedment + C.colBuffer;
  const totalLengthIn = totalLengthFt * 12;

  // Short side / long side — angle cut adds/subtracts half column width * tan(pitch)
  const halfColFt = (C.ceeW / 2) / 12; // half column width in feet
  const angleDiffFt = halfColFt * tan_s;
  const longSideFt = totalLengthFt + angleDiffFt;   // high side (left)
  const shortSideFt = totalLengthFt - angleDiffFt;  // low side (right)
  const longSideIn = longSideFt * 12;
  const shortSideIn = shortSideFt * 12;

  // Cut length = long side + cut allowance (for bandsaw vise)
  const cutLengthIn = longSideIn + p.cutAllowance;

  // Rebar
  const ag = p.aboveGrade; // above-grade amount (default 8')
  const rebarLenFt = p.reinforced ? (p.footing + ag - C.embedment) : (p.footing - C.embedment);
  // Clamp negative rebar length to 0
  const rebarLenFtClamped = Math.max(rebarLenFt, 0);
  const rebarLenIn = rebarLenFtClamped * 12;

  // Reinforced rebar: ag' measured up from grade line inside column
  // rebarLenFt = (footing + ag) - embedment  (corrected v8)
  // Inside column (dotted): ag + embed from bottom of column
  // Gap at top: totalLengthFt - (ag + embed)
  // Stickout below column: rebarLenFt - ag = footing - embed
  const rebarInsideFt = p.reinforced ? Math.min(ag + C.embedment, totalLengthFt) : 0;
  const rebarGapTopFt = p.reinforced ? Math.max(totalLengthFt - rebarInsideFt, 0) : 0;
  const rebarStickoutFt = p.reinforced ? Math.max(rebarLenFt - ag, 0) : 0;

  // Non-reinforced: welded 6" from bottom, runs down alongside, sticks out
  const nrWeldFromBottom = 0.5; // 6 inches
  const nrAlongsideFt = C.embedment - nrWeldFromBottom;
  const nrStickoutFt = Math.max(rebarLenFt - nrAlongsideFt - nrWeldFromBottom, 0);

  // Gusset hypotenuse
  const baseHyp = Math.sqrt(2) * C.gussetLeg;
  const uphillHyp = baseHyp * (1 + sin_s * 0.3);
  const downhillHyp = baseHyp * (1 - sin_s * 0.3);

  const totalCols = C.nFrames * (C.frameType === 'tee' ? 2 : 3);

  const rebarWtMap = {'#5': 1.043, '#7': 2.044, '#9': 3.40, '#11': 5.313};
  const ceeQty = totalCols * 2;
  const capQty = totalCols;
  const gusQty = totalCols * 4;
  const rebarTotal = totalCols * 4;
  const ceeWt = Math.round(totalLengthFt * 10.83 * ceeQty);
  const capWt = Math.round(C.capW * C.capH * C.capThick * 0.2836 * capQty);
  const gusWt = Math.round(0.5 * C.gussetLeg * C.gussetLeg * C.gussetThick * 0.2836 * gusQty);
  const rebarWt = Math.round(rebarLenFtClamped * (rebarWtMap[p.rebarSize]||3.4) * rebarTotal);
  const totalWt = ceeWt + capWt + gusWt + rebarWt;

  return {
    totalLengthFt, totalLengthIn,
    longSideFt, longSideIn, shortSideFt, shortSideIn,
    angleDiffFt, cutLengthIn,
    rebarLenFt, rebarLenIn,
    uphillHyp, downhillHyp, totalCols, angleAdd,
    rebarGapTopFt, rebarInsideFt, rebarStickoutFt,
    nrWeldFromBottom, nrAlongsideFt, nrStickoutFt,
    ceeQty, capQty, gusQty, rebarTotal,
    ceeWt, capWt, gusWt, rebarWt, totalWt,
    rad, tan_s, sin_s, dist,
  };
}

const NS = 'http://www.w3.org/2000/svg';
function $e(tag, a, txt) {
  const e = document.createElementNS(NS, tag);
  if (a) Object.entries(a).forEach(([k,v]) => e.setAttribute(k,v));
  if (txt) e.textContent = txt;
  return e;
}
function $g(cls, dp) {
  const g = $e('g', {class: cls || ''});
  if (dp) g.dataset.part = dp;
  return g;
}
function $l(x1,y1,x2,y2,c) { return $e('line',{x1,y1,x2,y2,class:c||'obj med'}); }
function $r(x,y,w,h,c) { return $e('rect',{x,y,width:w,height:h,class:c||'obj thick'}); }
function $c(cx,cy,r,c) { return $e('circle',{cx,cy,r,class:c||'bolt'}); }
function $t(x,y,s,c,a) { const t=$e('text',{x,y,class:c||'lbl'},s); if(a)t.setAttribute('text-anchor',a); return t; }
function $p(d,c) { return $e('path',{d,class:c||'obj med'}); }

const rebarDiaMap = {'#5': 0.625, '#7': 0.875, '#9': 1.128, '#11': 1.41};

function fmtFtIn(inches) {
  if (inches < 0) inches = 0;
  const ft = Math.floor(inches / 12);
  let inc = inches - ft * 12;
  const e8 = Math.round(inc * 8) / 8;
  if (e8 >= 12) return `${ft+1}'-0"`;
  if (e8 === Math.floor(e8)) return `${ft}'-${Math.floor(e8)}"`;
  const w = Math.floor(e8);
  let n = Math.round((e8 - w) * 8), dd = 8;
  while (n%2===0 && dd>1) { n/=2; dd/=2; }
  return w ? `${ft}'-${w} ${n}/${dd}"` : `${ft}'-${n}/${dd}"`;
}

function dimH(svg, x1, x2, y, off, label) {
  const dy = y + off;
  svg.appendChild($l(x1,y,x1,dy+(off>0?-2:2),'dim'));
  svg.appendChild($l(x2,y,x2,dy+(off>0?-2:2),'dim'));
  svg.appendChild($l(x1,dy,x2,dy,'dim'));
  svg.appendChild($l(x1-1.5,dy-1.5,x1+1.5,dy+1.5,'dim'));
  svg.appendChild($l(x2-1.5,dy-1.5,x2+1.5,dy+1.5,'dim'));
  svg.appendChild($t((x1+x2)/2, dy-3, label, 'dimtxt', 'middle'));
}
function dimV(svg, x, y1, y2, off, label) {
  const dx = x + off;
  svg.appendChild($l(x,y1,dx+(off>0?-2:2),y1,'dim'));
  svg.appendChild($l(x,y2,dx+(off>0?-2:2),y2,'dim'));
  svg.appendChild($l(dx,y1,dx,y2,'dim'));
  svg.appendChild($l(dx-1.5,y1-1.5,dx+1.5,y1+1.5,'dim'));
  svg.appendChild($l(dx-1.5,y2-1.5,dx+1.5,y2+1.5,'dim'));
  const t = $t(dx+(off>0?4:-4), (y1+y2)/2+3, label, 'dimtxt', 'middle');
  t.setAttribute('transform', `rotate(-90,${dx+(off>0?4:-4)},${(y1+y2)/2+3})`);
  svg.appendChild(t);
}
// Rebar dimension (red colored)
function dimVRebar(svg, x, y1, y2, off, label) {
  const dx = x + off;
  svg.appendChild($l(x,y1,dx+(off>0?-2:2),y1,'rebar-dim'));
  svg.appendChild($l(x,y2,dx+(off>0?-2:2),y2,'rebar-dim'));
  svg.appendChild($l(dx,y1,dx,y2,'rebar-dim'));
  svg.appendChild($l(dx-1.5,y1-1.5,dx+1.5,y1+1.5,'rebar-dim'));
  svg.appendChild($l(dx-1.5,y2-1.5,dx+1.5,y2+1.5,'rebar-dim'));
  const t = $t(dx+(off>0?4:-4), (y1+y2)/2+3, label, 'rebar-dimtxt', 'middle');
  t.setAttribute('transform', `rotate(-90,${dx+(off>0?4:-4)},${(y1+y2)/2+3})`);
  svg.appendChild(t);
}

// ════════════════════════════════════
// AWS WELDING SYMBOL FUNCTIONS (v8)
// Per AWS A2.4 Standard Symbols
// ════════════════════════════════════

function awsWeld(svg, ax, ay, routeX, routeY, size, opts, weldId) {
  opts = opts || {};
  // Apply overrides if they exist
  const ov = weldId ? (weldOverrides[weldId] || {}) : {};
  const finalRouteX = routeX + (ov.dx || 0);
  const finalRouteY = routeY + (ov.dy || 0);
  const finalSize = ov.size !== undefined ? ov.size : size;
  const finalRefDir = ov.refDir !== undefined ? ov.refDir : opts.refDir;
  const finalStitch = ov.stitch !== undefined ? ov.stitch : opts.stitch;
  const finalWps = ov.wpsCode !== undefined ? ov.wpsCode : opts.wpsCode;
  const finalAllAround = ov.allAround !== undefined ? ov.allAround : opts.allAround;
  const finalBothSides = ov.bothSides !== undefined ? ov.bothSides : opts.bothSides;
  const rotation = ov.rotation || 0;

  const isSelected = weldEditMode && selectedWeldId === weldId;
  const gClass = weldEditMode ? `weld-group weld-group-interactive${isSelected ? ' selected' : ''}` : 'weld-group';
  const g = $e('g', {class: gClass});
  if (weldId) g.setAttribute('data-weld-id', weldId);

  const filletLeg = 8;
  const refLineLen = 50;
  const arrHead = 4;
  const refDir = finalRefDir === 'left' ? -1 : 1;

  // Apply rotation around the route point
  if (rotation !== 0) {
    g.setAttribute('transform', `rotate(${rotation}, ${finalRouteX}, ${finalRouteY})`);
  }

  // Leader line: arrow tip -> knee -> route point
  const kneeX = finalRouteX;
  const kneeY = ay;
  g.appendChild($l(ax, ay, kneeX, kneeY, 'weld-leader'));
  g.appendChild($l(kneeX, kneeY, finalRouteX, finalRouteY, 'weld-leader'));

  // Arrowhead pointing toward joint
  const adx = kneeX - ax, ady = kneeY - ay;
  const aDist = Math.sqrt(adx*adx + ady*ady) || 1;
  const aUx = adx / aDist, aUy = ady / aDist;
  const aPx = -aUy, aPy = aUx;
  g.appendChild($p(`M ${ax} ${ay} L ${ax + aUx*arrHead + aPx*arrHead*0.4} ${ay + aUy*arrHead + aPy*arrHead*0.4} L ${ax + aUx*arrHead - aPx*arrHead*0.4} ${ay + aUy*arrHead - aPy*arrHead*0.4} Z`, 'weld-arrow'));

  // Reference line (solid = arrow side)
  const refEndX = finalRouteX + refDir * refLineLen;
  g.appendChild($l(finalRouteX, finalRouteY, refEndX, finalRouteY, 'weld-ref'));

  // Other-side dashed reference line (if bothSides)
  if (finalBothSides) {
    const dashLine = $l(finalRouteX, finalRouteY + 5, refEndX, finalRouteY + 5, 'weld-ref');
    dashLine.setAttribute('stroke-dasharray', '3,2');
    g.appendChild(dashLine);
  }

  // All-around circle
  if (finalAllAround) g.appendChild($c(finalRouteX, finalRouteY, 3.5, 'weld-circ'));

  // Fillet triangle (below ref line on arrow side)
  const symX = finalRouteX + refDir * 5;
  g.appendChild($p(`M ${symX} ${finalRouteY} L ${symX} ${finalRouteY + filletLeg} L ${symX + refDir * filletLeg} ${finalRouteY} Z`, 'weld-sym'));

  // Size text
  if (finalSize) g.appendChild($t(symX - refDir * 2, finalRouteY + filletLeg + 9, finalSize + '"', 'weld-txt'));

  // Stitch notation
  if (finalStitch) g.appendChild($t(symX + refDir * (filletLeg + 6), finalRouteY + filletLeg + 9, finalStitch, 'weld-txt'));

  // WPS code at tail
  if (finalWps) {
    const tx = refEndX;
    g.appendChild($l(tx, finalRouteY, tx + refDir * 6, finalRouteY - 4, 'weld-tail'));
    g.appendChild($l(tx, finalRouteY, tx + refDir * 6, finalRouteY + 4, 'weld-tail'));
    g.appendChild($t(tx + refDir * 10, finalRouteY + 3, finalWps, 'weld-txt'));
  }

  // In edit mode, add a grab handle / highlight boundary
  if (weldEditMode && weldId) {
    const hRect = $e('rect', {
      x: Math.min(ax, finalRouteX, refEndX) - 4,
      y: Math.min(ay, finalRouteY) - 14,
      width: Math.abs(refEndX - Math.min(ax, finalRouteX)) + 20,
      height: Math.abs(finalRouteY - ay) + 34,
      fill: isSelected ? 'rgba(246,174,45,0.08)' : 'rgba(0,85,170,0.04)',
      stroke: isSelected ? '#F6AE2D' : 'none',
      'stroke-width': isSelected ? '0.5' : '0',
      'stroke-dasharray': '3,2',
      rx: 3
    });
    g.insertBefore(hRect, g.firstChild);

    // Rotation handle — a draggable circle above the route point
    if (isSelected) {
      const rhDist = 22; // distance above route point
      const rhX = finalRouteX;
      const rhY = finalRouteY - rhDist;
      // Connecting line from route to handle
      g.appendChild($l(finalRouteX, finalRouteY - 4, rhX, rhY + 4, 'weld-ref'));
      // Handle circle
      const rh = $c(rhX, rhY, 5, 'rotation-handle');
      rh.setAttribute('fill', '#F6AE2D');
      rh.setAttribute('stroke', '#0F172A');
      rh.setAttribute('stroke-width', '1');
      rh.setAttribute('data-rot-handle', weldId);
      g.appendChild(rh);
      // Small "↻" label
      const rl = $t(rhX, rhY + 2.5, '↻', 'weld-txt');
      rl.setAttribute('text-anchor', 'middle');
      rl.setAttribute('fill', '#0F172A');
      rl.setAttribute('font-size', '6');
      rl.setAttribute('style', 'pointer-events:none;');
      g.appendChild(rl);
    }
  }

  svg.appendChild(g);
  return g;
}

function draw() {
  const p = getParams();
  const d = calc(p);
  const svg = document.getElementById('svg');
  svg.innerHTML = '';
  const rad = d.rad;

  // Project settings from side panel
  const projName = (document.getElementById('setProjectName') || {}).value || 'SMITH RESIDENCE 40x60';
  const customer = (document.getElementById('setCustomer') || {}).value || '';
  const jobNum = (document.getElementById('setJobNumber') || {}).value || 'SA-2026-0147';
  const drawnBy = (document.getElementById('setDrawnBy') || {}).value || 'AUTO';
  const colMark = (document.getElementById('setColumnMark') || {}).value || 'C1';

  svg.appendChild($r(10,10,1080,830,'obj thick'));
  svg.appendChild($r(12,12,1076,826,'obj hair'));

  // ════════════════════════
  // FRONT VIEW — shifted UP so rebar stickout doesn't hit title block
  // ════════════════════════
  // Calculate max stickout to ensure we have room
  const maxStickoutFt = p.reinforced ? d.rebarStickoutFt : d.nrStickoutFt;
  const maxStickoutPx = maxStickoutFt * 12 * Math.min(420 / d.totalLengthIn, 2.2);
  const sc = Math.min(420 / d.totalLengthIn, 2.2); // v8: MUCH bigger scale
  const fvBot = Math.min(640, 680 - maxStickoutPx); // v8: dynamic bottom, leaves room for stickout + title
  const fvTop = fvBot - d.totalLengthIn * sc;
  const colW = C.ceeW * sc;
  const colL = 420;
  const colR = colL + colW;
  const colCx = (colL + colR) / 2;
  const fl = C.ceeD * sc; // flange depth in pixels

  const fv = $g('hover-part', 'column');

  // Angle cut at top
  const topL = fvTop - (colW/2) * Math.tan(rad);
  const topR = fvTop + (colW/2) * Math.tan(rad);

  // Column body
  fv.appendChild($p(`M ${colL} ${topL} L ${colR} ${topR} L ${colR} ${fvBot} L ${colL} ${fvBot} Z`, 'cee'));

  if (p.pitch > 0.5) {
    fv.appendChild($p(`M ${colL} ${Math.min(topL,topR)} L ${colR} ${Math.min(topL,topR)} L ${colR} ${topR} L ${colL} ${topL} Z`, 'ang-fill'));
  }

  // Inner CEE flange lines
  fv.appendChild($l(colL+fl, topL+fl*Math.tan(rad), colL+fl, fvBot, 'hidden'));
  fv.appendChild($l(colR-fl, topR-fl*Math.tan(rad), colR-fl, fvBot, 'hidden'));

  // Center line
  fv.appendChild($l(colCx, fvTop-20, colCx, fvBot+20, 'center'));

  svg.appendChild(fv);

  // ── REBAR FRONT VIEW ──
  const rebarDia = rebarDiaMap[p.rebarSize] || 1.128;
  // Rebar width to scale with column (rebarDia in inches * sc pixels per inch)
  // Minimum 1.5px so it's still visible
  const rbW = Math.max(rebarDia * sc, 1.5);

  if (p.reinforced) {
    // Reinforced: rebar inside column at INNER CORNERS
    // Left rebar against left inner wall (right side of left flange)
    // Right rebar against right inner wall (left side of right flange)
    const gapTopPx = d.rebarGapTopFt * 12 * sc;
    const insidePx = d.rebarInsideFt * 12 * sc;
    const stickoutPx = Math.max(d.rebarStickoutFt * 12 * sc, 0);

    const rbStartY = fvTop + gapTopPx;

    // Left rebar: inside left corner — pushed left against left inner flange wall
    const rbLx = colL + 1; // touching left wall of column (inside corner)
    // Right rebar: inside right corner — pushed right against right inner flange wall
    const rbRx = colR - rbW - 1; // touching right wall of column (inside corner)

    // Dotted portion inside column
    const insideH = Math.min(insidePx, fvBot - rbStartY);
    if (insideH > 0) {
      svg.appendChild($e('rect', {x:rbLx, y:rbStartY, width:rbW, height:insideH, class:'rebar-dot-rect'}));
      svg.appendChild($e('rect', {x:rbRx, y:rbStartY, width:rbW, height:insideH, class:'rebar-dot-rect'}));
    }

    // Solid red stickout below column
    if (stickoutPx > 1) {
      svg.appendChild($e('rect', {x:rbLx, y:fvBot, width:rbW, height:stickoutPx, class:'rebar-solid'}));
      svg.appendChild($e('rect', {x:rbRx, y:fvBot, width:rbW, height:stickoutPx, class:'rebar-solid'}));
    }

    // Rebar length dimension (red) — total length
    const rbTotalTopY = rbStartY;
    const rbTotalBotY = fvBot + stickoutPx;
    dimVRebar(svg, colL - 5, rbTotalTopY, rbTotalBotY, -20, fmtFtIn(d.rebarLenIn));

    // v8: Dimension showing total inside length (8' + embedment)
    const insideBotY = fvBot; // bottom of column
    const insideTopY = rbStartY; // where rebar starts inside
    dimVRebar(svg, colR + 5, insideTopY, insideBotY, 42, fmtFtIn(d.rebarInsideFt * 12) + ' INSIDE');

    // Label
    dlabel(colR+75, fvTop+55, 'fv-rebar-lbl', (g) => {
      g.appendChild($t(0, 0, `${p.rebarSize} REBAR x4 (INSIDE)`, 'lblb'));
      g.appendChild($t(0, 12, fmtFtIn(d.rebarLenIn) + ' total', 'lbl'));
      g.appendChild($t(0, 24, `${p.aboveGrade}' up from grade line`, 'note'));
      g.appendChild($t(0, 36, fmtFtIn(d.rebarInsideFt * 12) + ' inside col', 'note'));
    });
    svg.appendChild($l(colR+73, fvTop+64, colR-2, rbStartY+15, 'dim'));

  } else if (d.rebarLenFt <= 0) {
    // Footing <= embedment: no rebar needed
    svg.appendChild($t(colR+75, fvTop+55, 'NOTE: Footing ≤ embedment', 'warn-text'));
    svg.appendChild($t(colR+75, fvTop+67, 'No rebar required (non-reinforced)', 'warn-text'));
  } else {
    // Non-reinforced: rebar OUTSIDE, touching column edges
    // Weld 6" from bottom of column, rebar goes down from there
    const weldFromBotPx = 6 * sc;
    const weldPointY = fvBot - weldFromBotPx;
    const stickoutPx = Math.max(d.nrStickoutFt * 12 * sc, 0);

    // Left rebar touching left edge
    const nrLx = colL - rbW;
    const nrRx = colR;

    // Solid red from weld point to bottom of column
    svg.appendChild($e('rect', {x:nrLx, y:weldPointY, width:rbW, height:fvBot-weldPointY, class:'rebar-solid'}));
    svg.appendChild($e('rect', {x:nrRx, y:weldPointY, width:rbW, height:fvBot-weldPointY, class:'rebar-solid'}));

    // Solid red stickout below
    if (stickoutPx > 1) {
      svg.appendChild($e('rect', {x:nrLx, y:fvBot, width:rbW, height:stickoutPx, class:'rebar-solid'}));
      svg.appendChild($e('rect', {x:nrRx, y:fvBot, width:rbW, height:stickoutPx, class:'rebar-solid'}));
    }

    // Weld symbol at top (attachment point only)
    [colL-rbW/2, colR+rbW/2].forEach(wx => {
      svg.appendChild($p(`M ${wx-4} ${weldPointY+4} L ${wx} ${weldPointY} L ${wx+4} ${weldPointY+4}`, 'weld'));
    });

    // Rebar length dimension (red)
    const rbBotY = fvBot + stickoutPx;
    dimVRebar(svg, colL - rbW - 5, weldPointY, rbBotY, -20, fmtFtIn(d.rebarLenIn));

    // Label
    dlabel(colR+75, fvTop+55, 'fv-rebar-lbl', (g) => {
      g.appendChild($t(0, 0, `${p.rebarSize} REBAR x4 (OUTSIDE)`, 'lblb'));
      g.appendChild($t(0, 12, `${fmtFtIn(d.rebarLenIn)} long`, 'lbl'));
      g.appendChild($t(0, 24, `6" weld from col bottom`, 'note'));
    });
    svg.appendChild($l(colR+73, fvTop+64, colR+rbW+2, weldPointY+5, 'dim'));
  }

  // ── No-paint zones — BOTH ENDS ──
  const npH = 12 * sc;
  // Bottom NP zone
  svg.appendChild($r(colL, fvBot-npH, colW, npH, 'nopaint'));
  dlabel(colR+8, fvBot-npH/2+3, 'fv-np-bot', (g) => { g.appendChild($t(0, 0, 'NP', 'noteb')); });
  // Top NP zone
  const npTopY = Math.min(topL, topR);
  svg.appendChild($r(colL, npTopY, colW, npH, 'nopaint'));
  dlabel(colL-18, npTopY+npH/2+3, 'fv-np-top', (g) => { g.appendChild($t(0, 0, 'NP', 'noteb')); });

  // CEE stitch note at column ends
  dlabel(colR+35, fvBot-npH/2+3, 'fv-cee-note', (g) => {
    g.appendChild($t(0, 0, 'CEE STITCH: 3"@6" O.C.', 'noteb'));
    g.appendChild($t(0, 9, 'AT FIRST 12" EACH END', 'note'));
  });

  // ── Cap Plate ──
  const cp = $g('hover-part', 'capplate');
  const capDrawW = C.capW * sc;
  const capDrawT = Math.max(C.capThick * sc * 3, 4);
  const capL = colCx - capDrawW/2;
  const capR2 = colCx + capDrawW/2;
  const capMidY = (topL + topR) / 2 - 1;
  const capPL = -(capDrawW/2) * Math.tan(rad);
  const capPR = (capDrawW/2) * Math.tan(rad);

  cp.appendChild($p(`M ${capL} ${capMidY+capPL} L ${capR2} ${capMidY+capPR}
                     L ${capR2} ${capMidY+capPR-capDrawT} L ${capL} ${capMidY+capPL-capDrawT} Z`, 'cap'));

  // 4 bolt holes on cap plate — 15/16" dia = 0.9375", to scale
  const boltR = Math.max((C.boltDia / 2) * sc, 1);
  const boltXs = [capL + C.boltInset*sc, capR2 - C.boltInset*sc];
  const boltYoffs = [-(capDrawT * 0.3), (capDrawT * 0.3)]; // two rows: near top edge and near bottom edge of cap
  boltXs.forEach(bx2 => {
    boltYoffs.forEach(yOff => {
      const interp = (bx2 - colCx) / (capDrawW/2);
      const by = capMidY + interp * (capDrawW/2) * Math.tan(rad) - capDrawT/2 + yOff;
      cp.appendChild($c(bx2, by, boltR, 'bolt'));
    });
  });

  if (p.pitch > 0.5) {
    svg.appendChild($t(capL-5, capMidY+capPL-capDrawT-12, `${p.pitch}°`, 'lblb'));
    const aR=18, plX=capL-5, plY=capMidY+capPL-capDrawT-4;
    svg.appendChild($l(plX,plY,plX+aR,plY,'dim'));
    svg.appendChild($l(plX,plY,plX+aR*Math.cos(-rad),plY+aR*Math.sin(-rad),'dim'));
  }
  svg.appendChild(cp);

  // ── GUSSETS on Front View — SAME as Section B-B ──
  // Below cap plate on column sides
  // Vertical leg along column, sloped leg follows roof pitch
  const gg = $g('hover-part', 'gussets');
  const gusLeg = C.gussetLeg * sc;

  // High-side (left): vertical leg down along column, sloped leg up-left following pitch
  const gHx = colL;
  const gHy = topL;  // top-left corner of column (angle cut)
  const gHbotY = gHy + gusLeg;
  const gHslopeX = gHx - gusLeg * Math.cos(rad);
  const gHslopeY = gHy - gusLeg * Math.sin(rad);
  gg.appendChild($p(`M ${gHx} ${gHy} L ${gHslopeX} ${gHslopeY} L ${gHx} ${gHbotY} Z`, 'gus'));
  dlabel(gHslopeX-4, (gHslopeY+gHbotY)/2, 'fv-p4', (g) => {
    g.appendChild($t(0, 0, 'p4', 'lblb'));
    g.appendChild($t(-12, 10, `${d.uphillHyp.toFixed(3)}"`, 'note'));
  });

  // Low-side (right): vertical leg down, sloped leg up-right following pitch
  const gLx2 = colR;
  const gLy2 = topR;  // top-right corner of column (angle cut)
  const gLbotY = gLy2 + gusLeg;
  const gLslopeX = gLx2 + gusLeg * Math.cos(rad);
  const gLslopeY = gLy2 + gusLeg * Math.sin(rad);
  gg.appendChild($p(`M ${gLx2} ${gLy2} L ${gLslopeX} ${gLslopeY} L ${gLx2} ${gLbotY} Z`, 'gus'));
  dlabel(gLslopeX+2, (gLslopeY+gLbotY)/2, 'fv-p5', (g) => {
    g.appendChild($t(0, 0, 'p5', 'lblb'));
    g.appendChild($t(6, 10, `${d.downhillHyp.toFixed(3)}"`, 'note'));
  });

  svg.appendChild(gg);

  // ── AWS WELD SYMBOLS — Front View (with IDs for interactive editing) ──
  // Reset weld defs tracking for this draw cycle
  currentWeldDefs = [];

  // Helper to register and draw a weld
  function weld(ax, ay, routeX, routeY, size, opts, id) {
    currentWeldDefs.push({ id, ax, ay, routeX, routeY, size, opts: {...opts} });
    return awsWeld(svg, ax, ay, routeX, routeY, size, opts, id);
  }

  // Helper to create a draggable label group
  // Returns an SVG <g> that can be moved in edit mode
  // Usage: dlabel(svg, x, y, id, function(g, ox, oy) { /* add text/lines relative to ox,oy */ })
  function dlabel(x, y, id, buildFn) {
    const ov = labelOverrides[id] || {};
    const ox = x + (ov.dx || 0);
    const oy = y + (ov.dy || 0);
    const isSelected = weldEditMode && selectedLabelId === id;
    const cls = weldEditMode ? `label-interactive${isSelected ? ' selected' : ''}` : '';
    const g = $e('g', { class: cls, 'data-label-id': id, transform: `translate(${ox}, ${oy})` });
    // Build content at (0,0) relative coordinates
    buildFn(g, 0, 0);
    // Add a hit area in edit mode
    if (weldEditMode) {
      const bb = { x: -2, y: -12, w: 80, h: 16 }; // rough default hit box
      const hit = $e('rect', { x: bb.x, y: bb.y, width: bb.w, height: bb.h,
        fill: isSelected ? 'rgba(246,174,45,0.1)' : 'transparent', stroke: isSelected ? '#F6AE2D' : 'none',
        'stroke-width': '0.4', 'stroke-dasharray': '2,1', rx: 2 });
      g.insertBefore(hit, g.firstChild);
    }
    svg.appendChild(g);
    return g;
  }

  // 1) Cap plate to column
  const capJointY = (topL + topR) / 2 + capDrawT * 0.1;
  weld(colCx, capJointY, colR+85, fvTop-65, '3/16', {allAround:true, wpsCode:'F', refDir:'right'}, 'fv-cap');

  const ceeMidY_pre = (fvTop + fvBot) / 2;
  weld(colL, gHy+gusLeg*0.5, colL-65, gHy+gusLeg*0.7, '3/16', {wpsCode:'C', refDir:'left'}, 'fv-gus-hl-col');
  weld(gHslopeX+gusLeg*0.3, gHslopeY+gusLeg*0.15, colL-120, gHy-25, '3/16', {wpsCode:'C', refDir:'left'}, 'fv-gus-hl-cap');
  weld(colR, gLy2+gusLeg*0.5, colR+65, gLy2+gusLeg*0.7, '3/16', {wpsCode:'C', refDir:'right'}, 'fv-gus-lr-col');
  weld(gLslopeX-gusLeg*0.3, gLslopeY+gusLeg*0.15, colR+120, gLy2-25, '3/16', {wpsCode:'C', refDir:'right'}, 'fv-gus-lr-cap');

  // 4) Rebar welds
  if (p.reinforced) {
    const gapTopPx = d.rebarGapTopFt * 12 * sc;
    const insidePx = d.rebarInsideFt * 12 * sc;
    const rbStartY = fvTop + gapTopPx;
    const insideH = Math.min(insidePx, fvBot - rbStartY);
    const rbRouteY = Math.max(rbStartY+insideH*0.7, ceeMidY_pre+40);
    weld(colL+1, rbStartY+insideH/2, colL-85, rbRouteY, '3/16', {stitch:'3"-36" O.C.', wpsCode:'D', refDir:'left'}, 'fv-rebar-l');
    weld(colR-1, rbStartY+insideH/2, colR+85, rbRouteY, '3/16', {stitch:'3"-36" O.C.', wpsCode:'D', refDir:'right'}, 'fv-rebar-r');
  } else {
    const nrWeldY = fvBot - 6 * sc;
    weld(colL-rbW, nrWeldY, colL-85, nrWeldY+25, '3/16', {wpsCode:'D', refDir:'left'}, 'fv-rebar-l');
    weld(colR+rbW, nrWeldY, colR+85, nrWeldY+25, '3/16', {wpsCode:'D', refDir:'right'}, 'fv-rebar-r');
  }

  // 5) CEE stitch welds
  const ceeMidY = (fvTop + fvBot) / 2;
  const ceeRouteY = fvBot - 15;
  weld(colL, ceeMidY, colL-85, ceeRouteY, '', {stitch:'3"-36" O.C.', wpsCode:'B', refDir:'left', bothSides:true}, 'fv-cee-l');
  weld(colR, ceeMidY, colR+85, ceeRouteY, '', {stitch:'3"-36" O.C.', wpsCode:'B', refDir:'right', bothSides:true}, 'fv-cee-r');

  // ── Front View Dimensions ──
  // Long side (left / high side) dimension
  dimV(svg, colL, topL, fvBot, -25, fmtFtIn(d.longSideIn) + ' (LONG)');
  // Short side (right / low side) dimension
  dimV(svg, colR, topR, fvBot, 90, fmtFtIn(d.shortSideIn) + ' (SHORT)');
  dimH(svg, capL, capR2, capMidY+capPL-capDrawT, -16, fmtFtIn(C.capW));
  dimH(svg, colL, colR, fvBot, 16, fmtFtIn(C.ceeW));

  // Grade line
  const embedPx = C.embedment * 12 * sc;
  const gradeY = fvBot - embedPx;
  svg.appendChild($l(colL-55, gradeY, colR+20, gradeY, 'obj thin'));
  dlabel(colL-55, gradeY-3, 'fv-grade', (g) => { g.appendChild($t(0, 0, 'GRADE', 'note')); });

  // Embedment dimension
  dimV(svg, colL, gradeY, fvBot, -50, fmtFtIn(C.embedment * 12) + ' EMBED');

  if (d.angleAdd > 0.1) {
    dlabel(colR+90, topR+12, 'fv-angle-cut', (g) => {
      g.appendChild($t(0, 0, `+${(d.angleDiffFt*12).toFixed(1)}" ea. side`, 'noteb'));
      g.appendChild($t(0, 9, 'ANGLE CUT', 'note'));
    });
  }

  // High/Low side callouts
  dlabel(colL-45, topL+4, 'fv-high', (g) => { g.appendChild($t(0, 0, '◄ HIGH', 'noteb')); });
  dlabel(colR+8, topR-12, 'fv-low', (g) => { g.appendChild($t(0, 0, 'LOW ►', 'noteb')); });

  // Section cut lines
  const secAy = fvBot - 80;
  svg.appendChild($l(colL-25, secAy, colR+25, secAy, 'cut-line'));
  svg.appendChild($t(colL-35, secAy+4, 'A', 'lblb'));
  svg.appendChild($t(colR+28, secAy+4, 'A', 'lblb'));

  const secBy = capMidY + Math.max(capPL,capPR) + capDrawT + gusLeg + 8;
  svg.appendChild($l(colL-30, secBy, colR+30, secBy, 'cut-line'));
  svg.appendChild($t(colL-40, secBy+4, 'B', 'lblb'));
  svg.appendChild($t(colR+33, secBy+4, 'B', 'lblb'));

  // Piece marks on front view
  dlabel(colCx, (fvTop+fvBot)/2, 'fv-mark', (g) => { const t = $t(0, 0, colMark, 'lblb', 'middle'); g.appendChild(t); });
  dlabel(capR2+12, capMidY+capPR-capDrawT/2+2, 'fv-p3', (g) => { g.appendChild($t(0, 0, 'p3', 'lblb')); });

  dlabel(colCx, fvBot+36, 'fv-title', (g) => { g.appendChild($t(0, 0, 'FRONT VIEW', 'ttl', 'middle')); });

  // ════════════════════════
  // SECTION A-A
  // ════════════════════════
  const aa = $g('hover-part', 'secAA');
  const as2 = 5.5;
  const ax = 140, ay = Math.max(fvBot - 60, 480);
  const aw = C.ceeW * as2, ah = C.ceeD * 2 * as2;
  const boxL = ax-aw/2, boxR3 = ax+aw/2, boxT = ay-ah/2, boxB = ay+ah/2;

  aa.appendChild($r(boxL, boxT, aw, ah, 'cee'));

  const gThk = C.ceeGauge * as2;
  const afH = C.ceeD * as2;
  const lipH = 0.75 * as2; // 3/4" lip/turndown
  const lipVis = Math.max(gThk, 2); // minimum 2px so lips are visible

  // Top CEE — flanges with lip turndowns extending past centerline
  aa.appendChild($p(`M ${boxL} ${boxT} v ${afH + lipH} h ${lipVis} v ${-lipH} V ${boxT+gThk} H ${boxR3-gThk} V ${boxT+afH} v ${lipH} h ${lipVis} V ${boxT}`, 'obj med'));
  // Bottom CEE — flanges with lip turndowns extending past centerline
  aa.appendChild($p(`M ${boxL} ${boxB} v ${-(afH + lipH)} h ${lipVis} v ${lipH} V ${boxB-gThk} H ${boxR3-gThk} V ${boxB-afH} v ${-lipH} h ${lipVis} V ${boxB}`, 'obj med'));

  const rebarR = ((rebarDiaMap[p.rebarSize] || 1.128) / 2) * as2;

  if (p.reinforced) {
    // Inside corners: tangent to both edges
    [[boxL + rebarR, boxT + rebarR],
     [boxR3 - rebarR, boxT + rebarR],
     [boxL + rebarR, boxB - rebarR],
     [boxR3 - rebarR, boxB - rebarR]].forEach(([rx,ry]) => {
      aa.appendChild($c(rx, ry, rebarR, 'rebar-circ'));
    });
    // Rebar position dims — distance from inner corner
    svg.appendChild($t(boxL+rebarR*2+4, boxT+rebarR+3, `${(rebarDiaMap[p.rebarSize]||1.128).toFixed(3)}"Ø`, 'note'));
    svg.appendChild($t(ax, ay+ah/2+42, '(Reinforced — rebar inside corners)', 'note'));
  } else {
    // Outside corners: tangent to vertical edge (outside),
    // TOP of circle flush with horizontal edge
    // Top circles: top of circle = boxT, so cy = boxT + rebarR
    // Bottom circles: top of circle = boxB, so cy = boxB + rebarR
    [[boxL - rebarR, boxT + rebarR],   // top-left outside, top flush with top edge
     [boxR3 + rebarR, boxT + rebarR],  // top-right outside
     [boxL - rebarR, boxB - rebarR],   // bottom-left outside, bottom flush with bottom edge
     [boxR3 + rebarR, boxB - rebarR]   // bottom-right outside
    ].forEach(([rx,ry]) => {
      aa.appendChild($c(rx, ry, rebarR, 'rebar-circ-out'));
      // Weld mark
      const dx2 = rx < ax ? 2 : -2;
      const dy2 = ry < ay ? 2 : -2;
      aa.appendChild($l(rx+dx2, ry+dy2, rx+dx2*2.5, ry+dy2*2.5, 'weld'));
    });
    svg.appendChild($t(ax, ay+ah/2+42, '(Non-reinforced — rebar outside, 6" weld)', 'note'));
  }

  aa.appendChild($l(ax, boxT-8, ax, boxB+8, 'center'));
  aa.appendChild($l(boxL-8, ay, boxR3+8, ay, 'center'));
  dimH(svg, boxL, boxR3, boxT, -14, fmtFtIn(C.ceeW));
  dimV(svg, boxR3, boxT, boxB, 14, fmtFtIn(C.ceeD*2));

  svg.appendChild(aa);

  // ── AWS WELD SYMBOLS — Section A-A (with IDs) ──

  weld(boxL+gThk, boxT+afH, ax-65, boxT-25, '', {stitch:'3"-36" O.C.', wpsCode:'B', refDir:'left', bothSides:true}, 'aa-cee-top');

  weld(boxR3-gThk, boxB-afH, ax+65, boxB+25, '', {stitch:'3"-36" O.C.', wpsCode:'B', refDir:'right', bothSides:true}, 'aa-cee-bot');

  if (p.reinforced) {
    weld(boxL+rebarR, boxT+rebarR, ax+65, boxT-25, '3/16', {stitch:'3"-36" O.C.', wpsCode:'D', refDir:'right'}, 'aa-rebar');
  } else {
    weld(boxL-rebarR, boxT+rebarR, ax+65, boxT-25, '3/16', {wpsCode:'D', refDir:'right'}, 'aa-rebar');
  }

  dlabel(ax, ay+ah/2+18, 'aa-info', (g) => {
    g.appendChild($t(0, 0, 'A36 — 14"x4"x10GA CEE (x2)', 'note', 'middle'));
    g.appendChild($t(0, 12, 'SECTION A-A', 'ttl', 'middle'));
  });

  // ════════════════════════
  // SECTION B-B — PERFECT, keeping as-is from v4
  // ════════════════════════
  const bb = $g('hover-part', 'secBB');
  const bs = 3.2;
  const bx = 150, by2 = 180;
  const bCapW = C.capW * bs, bCapT = Math.max(C.capThick * bs * 3, 4);
  const bColW = C.ceeW * bs, bColH = C.ceeD * 2 * bs;
  const bHalf = bCapW / 2;
  const bPL = -bHalf * Math.tan(rad);
  const bPR = bHalf * Math.tan(rad);

  bb.appendChild($p(`M ${bx-bHalf} ${by2+bPL} L ${bx+bHalf} ${by2+bPR}
                     L ${bx+bHalf} ${by2+bPR+bCapT} L ${bx-bHalf} ${by2+bPL+bCapT} Z`, 'cap'));

  const bColHalf = bColW / 2;
  const bColTopY = by2 + bCapT + 2;
  const bColTopPL = -(bColHalf) * Math.tan(rad);
  const bColTopPR = (bColHalf) * Math.tan(rad);
  const bColBotY = bColTopY + bColH;

  bb.appendChild($p(`M ${bx-bColHalf} ${bColTopY+bColTopPL}
                     L ${bx+bColHalf} ${bColTopY+bColTopPR}
                     L ${bx+bColHalf} ${bColBotY}
                     L ${bx-bColHalf} ${bColBotY} Z`, 'cee'));

  const bfl = C.ceeD * bs;
  bb.appendChild($l(bx-bColHalf+bfl, bColTopY+bColTopPL+bfl*Math.tan(rad), bx-bColHalf+bfl, bColBotY, 'hidden'));
  bb.appendChild($l(bx+bColHalf-bfl, bColTopY+bColTopPR-bfl*Math.tan(rad), bx+bColHalf-bfl, bColBotY, 'hidden'));

  // 4 bolt holes — to scale (15/16" dia)
  const bbBoltR = Math.max((C.boltDia / 2) * bs, 0.8);
  [[-1,-1],[-1,1],[1,-1],[1,1]].forEach(([sx,sy]) => {
    const hx = bx + sx * (bHalf - C.boltInset*bs);
    const hy = by2 + (hx-bx)/bHalf * bHalf * Math.tan(rad) + bCapT/2 + sy * (bCapT * 0.25);
    bb.appendChild($c(hx, hy, bbBoltR, 'bolt'));
  });

  const bGusLeg = C.gussetLeg * bs;

  // High-side (left)
  const bgHx = bx - bColHalf;
  const bgHy = bColTopY + bColTopPL;
  const bgHbotY = bgHy + bGusLeg;
  const bgHslopeX = bgHx - bGusLeg * Math.cos(rad);
  const bgHslopeY = bgHy - bGusLeg * Math.sin(rad);
  bb.appendChild($p(`M ${bgHx} ${bgHy} L ${bgHslopeX} ${bgHslopeY} L ${bgHx} ${bgHbotY} Z`, 'gus'));
  bb.appendChild($t(bgHslopeX-4, (bgHslopeY+bgHbotY)/2+3, 'p4', 'noteb'));
  bb.appendChild($t(bgHslopeX-16, (bgHslopeY+bgHbotY)/2+13, `${d.uphillHyp.toFixed(3)}"`, 'note'));

  // Low-side (right)
  const bgLx = bx + bColHalf;
  const bgLy = bColTopY + bColTopPR;
  const bgLbotY = bgLy + bGusLeg;
  const bgLslopeX = bgLx + bGusLeg * Math.cos(rad);
  const bgLslopeY = bgLy + bGusLeg * Math.sin(rad);
  bb.appendChild($p(`M ${bgLx} ${bgLy} L ${bgLslopeX} ${bgLslopeY} L ${bgLx} ${bgLbotY} Z`, 'gus'));
  bb.appendChild($t(bgLslopeX+2, (bgLslopeY+bgLbotY)/2+3, 'p5', 'noteb'));
  bb.appendChild($t(bgLslopeX+10, (bgLslopeY+bgLbotY)/2+13, `${d.downhillHyp.toFixed(3)}"`, 'note'));

  if (p.pitch > 0.5) {
    bb.appendChild($t(bx-bHalf+4, by2+bPL-8, `${p.pitch}°`, 'lblb'));
  }

  // Material callouts on B-B
  bb.appendChild($t(bx, by2+bPR+bCapT/2, 'A572 Gr.50', 'note', 'middle'));
  bb.appendChild($t(bx, bColBotY-3, 'A36 — 10GA', 'note', 'middle'));
  bb.appendChild($t(bgHslopeX-4, bgHbotY+8, 'A572', 'note'));
  bb.appendChild($t(bgLslopeX+2, bgLbotY+8, 'A572', 'note'));

  dimH(svg, bx-bHalf, bx+bHalf, by2+bPL, -18, fmtFtIn(C.capW));
  dimH(svg, bx-bColHalf, bx+bColHalf, bColBotY, 14, fmtFtIn(C.ceeW));

  svg.appendChild(bb);

  // ── AWS WELD SYMBOLS — Section B-B (with IDs) ──

  weld(bx, bColTopY+(bColTopPL+bColTopPR)/2, bx+bHalf+30, bColTopY-20, '3/16', {allAround:true, wpsCode:'F', refDir:'right'}, 'bb-cap');

  weld(bgHx, bgHy+bGusLeg*0.5, bgHx-35, bgHy+bGusLeg*0.8, '3/16', {wpsCode:'C', refDir:'left'}, 'bb-gus-l-col');

  weld(bgHslopeX+bGusLeg*0.2, bgHslopeY+bGusLeg*0.1, bgHx-55, bgHy-20, '3/16', {wpsCode:'C', refDir:'left'}, 'bb-gus-l-cap');

  weld(bgLx, bgLy+bGusLeg*0.5, bgLx+35, bgLy+bGusLeg*0.8, '3/16', {wpsCode:'C', refDir:'right'}, 'bb-gus-r-col');

  weld(bgLslopeX-bGusLeg*0.2, bgLslopeY+bGusLeg*0.1, bgLx+55, bgLy-20, '3/16', {wpsCode:'C', refDir:'right'}, 'bb-gus-r-cap');

  dlabel(bx, bColBotY+32, 'bb-title', (g) => { g.appendChild($t(0, 0, 'SECTION B-B', 'ttl', 'middle')); });

  // ════════════════════════
  // SIDE VIEW — shifted UP to match front view
  // ════════════════════════
  const sv = $g('hover-part', 'side');
  const svX = 660;
  const svW = C.ceeD * 2 * sc;
  const svCx = svX + svW/2;

  // Side view top is flat — pitch slope is only visible in front view
  // Anchor to the front view's long-side top (highest point) so it doesn't shift with pitch
  const svTopY = fvBot - d.longSideIn * sc;
  sv.appendChild($p(`M ${svX} ${svTopY} L ${svX+svW} ${svTopY} L ${svX+svW} ${fvBot} L ${svX} ${fvBot} Z`, 'cee'));
  sv.appendChild($l(svCx, svTopY-15, svCx, fvBot+15, 'center'));

  // Side cap plate
  const svCapH = C.capH * sc;
  svg.appendChild($r(svCx-svCapH/2, svTopY-3, svCapH, 3, 'cap'));

  // Grade line on side view
  const svGradeY = fvBot - C.embedment * 12 * sc;
  svg.appendChild($l(svX-10, svGradeY, svX+svW+10, svGradeY, 'obj thin'));

  dimH(svg, svX, svX+svW, fvBot, 16, fmtFtIn(C.ceeD*2));
  // Bold 8" label for visibility
  const svDimBold = $t(svCx, fvBot+28, '8" DEPTH', 'dim-bold');
  svg.appendChild(svDimBold);
  dimV(svg, svX+svW, svTopY, fvBot, 35, fmtFtIn(d.longSideIn) + ' (LONG)');

  // v8: Append side view column body FIRST so rebar draws ON TOP
  svg.appendChild(sv);

  // Rebar in side view — drawn AFTER column body so it's visible on top
  const svRbW = Math.max(rbW, 3); // minimum 3px for side view visibility
  if (p.reinforced) {
    // Inside: red dotted lines flush against inner walls of column
    const svGapTopPx = d.rebarGapTopFt * 12 * sc;
    const svInsidePx = d.rebarInsideFt * 12 * sc;
    const svStickoutPx = Math.max(d.rebarStickoutFt * 12 * sc, 0);
    const svRbStartY = fvTop + svGapTopPx;
    const svInsideH = Math.min(svInsidePx, fvBot - svRbStartY);

    // Left rebar: flush against left inside wall (x = svX)
    // Right rebar: flush against right inside wall (x = svX+svW-svRbW)
    if (svInsideH > 0) {
      svg.appendChild($e('rect', {x:svX, y:svRbStartY, width:svRbW, height:svInsideH, class:'rebar-dot-rect'}));
      svg.appendChild($e('rect', {x:svX+svW-svRbW, y:svRbStartY, width:svRbW, height:svInsideH, class:'rebar-dot-rect'}));
    }
    // Solid red stickout below column
    if (svStickoutPx > 1) {
      svg.appendChild($e('rect', {x:svX, y:fvBot, width:svRbW, height:svStickoutPx, class:'rebar-solid'}));
      svg.appendChild($e('rect', {x:svX+svW-svRbW, y:fvBot, width:svRbW, height:svStickoutPx, class:'rebar-solid'}));
    }
  } else {
    // Outside: solid red touching column edges
    const weldPointY = fvBot - 6 * sc;
    const stickoutPx = Math.max(d.nrStickoutFt * 12 * sc, 0);

    svg.appendChild($e('rect', {x:svX-rbW, y:weldPointY, width:rbW, height:fvBot-weldPointY, class:'rebar-solid'}));
    svg.appendChild($e('rect', {x:svX+svW, y:weldPointY, width:rbW, height:fvBot-weldPointY, class:'rebar-solid'}));
    if (stickoutPx > 1) {
      svg.appendChild($e('rect', {x:svX-rbW, y:fvBot, width:rbW, height:stickoutPx, class:'rebar-solid'}));
      svg.appendChild($e('rect', {x:svX+svW, y:fvBot, width:rbW, height:stickoutPx, class:'rebar-solid'}));
    }
    [svX-rbW/2, svX+svW+rbW/2].forEach(wx => {
      svg.appendChild($p(`M ${wx-4} ${weldPointY+4} L ${wx} ${weldPointY} L ${wx+4} ${weldPointY+4}`, 'weld'));
    });
  }

  // ── AWS WELD SYMBOLS — Side View (with IDs) ──

  weld(svCx, svTopY-2, svX+svW+55, svTopY-50, '3/16', {allAround:true, wpsCode:'F', refDir:'right'}, 'sv-cap');

  const svCeeMidY = (fvTop + fvBot) / 2;
  weld(svCx, svCeeMidY, svX+svW+55, fvBot-20, '', {stitch:'3"-36" O.C.', wpsCode:'B', refDir:'right', bothSides:true}, 'sv-cee');

  if (p.reinforced) {
    const svGapTopPx = d.rebarGapTopFt * 12 * sc;
    const svInsidePx = d.rebarInsideFt * 12 * sc;
    const svRbStartY = fvTop + svGapTopPx;
    const svInsideH = Math.min(svInsidePx, fvBot - svRbStartY);
    weld(svX, svRbStartY+svInsideH/2, svX-65, svRbStartY+svInsideH*0.3, '3/16', {stitch:'3"-36" O.C.', wpsCode:'D', refDir:'left'}, 'sv-rebar-l');
    const svRbRouteY = Math.min(svRbStartY+svInsideH*0.3, fvBot-55);
    weld(svX+svW, svRbStartY+svInsideH/2, svX+svW+55, svRbRouteY, '3/16', {stitch:'3"-36" O.C.', wpsCode:'D', refDir:'right'}, 'sv-rebar-r');
  } else {
    const svNrWeldY = fvBot - 6 * sc;
    weld(svX-rbW, svNrWeldY, svX-65, svNrWeldY+25, '3/16', {wpsCode:'D', refDir:'left'}, 'sv-rebar-l');
    weld(svX+svW+rbW, svNrWeldY, svX+svW+55, svNrWeldY-30, '3/16', {wpsCode:'D', refDir:'right'}, 'sv-rebar-r');
  }

  dlabel(svCx, fvBot+36, 'sv-title', (g) => { g.appendChild($t(0, 0, 'SIDE VIEW', 'ttl', 'middle')); });

  // ── ON-SHEET BOM (per column) ──
  const bomX = 750, bomStartY = 200;
  const bomColW = [30, 25, 120, 80];
  const bomTotalW = bomColW.reduce((a,b)=>a+b,0);
  const bomRowH = 11;

  // Header
  svg.appendChild($r(bomX, bomStartY, bomTotalW, bomRowH, 'obj med'));
  const bomHeaders = ['Mk','Qty','Description','Size'];
  let bx2 = bomX;
  bomHeaders.forEach((h,i) => {
    svg.appendChild($t(bx2+3, bomStartY+8, h, 'noteb'));
    bx2 += bomColW[i];
  });

  // Rows
  const cutAst = p.cutAllowance > 0 ? '*' : '';
  const bomRows = [
    [colMark+cutAst, '2', 'CEE (Box Beam)', `14x4x10GA x ${fmtFtIn(d.cutLengthIn)}${cutAst}`],
    ['p3', '1', 'Cap Plate 3/4"', `${C.capW}" x ${C.capH}"`],
    ['p4', '2', 'Gusset High', `3/8" x ${d.uphillHyp.toFixed(3)}"`],
    ['p5', '2', 'Gusset Low', `3/8" x ${d.downhillHyp.toFixed(3)}"`],
    ['rb', '4', `${p.rebarSize} Rebar`, `${fmtFtIn(Math.max(d.rebarLenIn,0))} ${p.reinforced?'(in)':'(out)'}`],
    ['—', '4', 'Bolts 15/16"', 'A325'],
  ];
  bomRows.forEach((row, ri) => {
    const ry = bomStartY + bomRowH * (ri+1);
    svg.appendChild($l(bomX, ry, bomX+bomTotalW, ry, 'dim'));
    let rx = bomX;
    row.forEach((cell, ci) => {
      svg.appendChild($t(rx+3, ry+8, cell, 'note'));
      rx += bomColW[ci];
    });
  });
  // Cut allowance note
  if (p.cutAllowance > 0) {
    const noteY = bomStartY + bomRowH * (bomRows.length+1) + 8;
    svg.appendChild($t(bomX+3, noteY, `* +${p.cutAllowance}" cut allowance (bandsaw)`, 'note'));
    svg.appendChild($t(bomX+3, noteY+9, `  Finished long: ${fmtFtIn(d.longSideIn)} / short: ${fmtFtIn(d.shortSideIn)}`, 'note'));
  }
  svg.appendChild($r(bomX, bomStartY, bomTotalW, bomRowH*(bomRows.length+1), 'obj hair'));
  svg.appendChild($t(bomX+bomTotalW/2, bomStartY-6, 'BILL OF MATERIALS (per column)', 'noteb', 'middle'));

  // ── GUSSET DETAIL — TWO GUSSETS SIDE BY SIDE (moved further right, spread out) ──
  const gdStartX = 880, gdY = 300 + bomRowH*(bomRows.length+1) + 40;
  const gdScale = 3.5;
  const gdLeg = C.gussetLeg * gdScale;
  const gdBaseW = gdLeg * Math.cos(rad);
  const gdSpacing = gdBaseW + 50; // wider gap between triangles

  // ── p4 (high side / uphill) — left triangle ──
  const gd4X = gdStartX;
  const gd4g = $g('hover-part','gusDetail');
  gd4g.appendChild($p(`M ${gd4X} ${gdY} L ${gd4X} ${gdY+gdLeg} L ${gd4X+gdBaseW} ${gdY+gdLeg-gdLeg*Math.sin(rad)} Z`, 'gus'));

  dimV(svg, gd4X-5, gdY, gdY+gdLeg, -15, `${C.gussetLeg}"`);
  dimH(svg, gd4X, gd4X+gdBaseW, gdY+gdLeg, 14, `${(C.gussetLeg*Math.cos(d.rad)).toFixed(1)}"`);
  // Hypotenuse dim — offset outside the triangle
  const gd4HypEndX = gd4X + gdBaseW;
  const gd4HypEndY = gdY + gdLeg - gdLeg*Math.sin(rad);
  const gd4HypMidX = (gd4X + gd4HypEndX)/2 + 12;
  const gd4HypMidY = (gdY + gd4HypEndY)/2 - 8;
  svg.appendChild($t(gd4HypMidX, gd4HypMidY, `${d.uphillHyp.toFixed(3)}"`, 'dimtxt'));
  svg.appendChild(gd4g);
  svg.appendChild($t(gd4X + gdBaseW/2, gdY - 8, 'p4 (high)', 'lblb', 'middle'));

  // ── p5 (low side / downhill) — right triangle ──
  const gd5X = gdStartX + gdSpacing;
  const gd5g = $g('hover-part','gusDetail');
  gd5g.appendChild($p(`M ${gd5X} ${gdY} L ${gd5X} ${gdY+gdLeg} L ${gd5X+gdBaseW} ${gdY+gdLeg-gdLeg*Math.sin(rad)} Z`, 'gus'));

  dimV(svg, gd5X-5, gdY, gdY+gdLeg, -15, `${C.gussetLeg}"`);
  dimH(svg, gd5X, gd5X+gdBaseW, gdY+gdLeg, 14, `${(C.gussetLeg*Math.cos(d.rad)).toFixed(1)}"`);
  const gd5HypEndX = gd5X + gdBaseW;
  const gd5HypEndY = gdY + gdLeg - gdLeg*Math.sin(rad);
  const gd5HypMidX = (gd5X + gd5HypEndX)/2 + 12;
  const gd5HypMidY = (gdY + gd5HypEndY)/2 - 8;
  svg.appendChild($t(gd5HypMidX, gd5HypMidY, `${d.downhillHyp.toFixed(3)}"`, 'dimtxt'));
  svg.appendChild(gd5g);
  svg.appendChild($t(gd5X + gdBaseW/2, gdY - 8, 'p5 (low)', 'lblb', 'middle'));

  // Title centered between both
  const gdCenterX = gdStartX + (gdSpacing + gdBaseW) / 2;
  svg.appendChild($t(gdCenterX, gdY + gdLeg + 32, 'DETAIL 1 — GUSSETS', 'lblb', 'middle'));
  svg.appendChild($t(gdCenterX, gdY + gdLeg + 43, `A572 Gr.50 — 3/8" THK`, 'note', 'middle'));

  // ── DETAIL 2 — CAP PLATE BOLT PATTERN (plan view) ──
  const cpDtlX = 920, cpDtlY = gdY + gdLeg + 120;
  const cpScale = 3.0;
  const cpW = C.capW * cpScale, cpH = C.capH * cpScale;
  const cpL2 = cpDtlX - cpW/2, cpR2d = cpDtlX + cpW/2;
  const cpT2 = cpDtlY, cpB2 = cpDtlY + cpH;

  // Plate outline
  svg.appendChild($r(cpL2, cpT2, cpW, cpH, 'cap'));

  // Column footprint (dashed)
  const cpColW = C.ceeW * cpScale, cpColH = C.ceeD * 2 * cpScale;
  const cpColL = cpDtlX - cpColW/2, cpColT = cpDtlY + (cpH - cpColH)/2;
  svg.appendChild($r(cpColL, cpColT, cpColW, cpColH, 'hidden'));
  svg.appendChild($t(cpDtlX, cpDtlY + cpH/2 + 2, 'COL', 'note', 'middle'));

  // 4 bolt holes
  const cpBoltR = Math.max((C.boltDia / 2) * cpScale, 1.5);
  const cpBoltInX = C.boltInset * cpScale;
  const cpBoltInY = C.boltInset * cpScale;
  const boltPositions = [
    [cpL2 + cpBoltInX, cpT2 + cpBoltInY],
    [cpR2d - cpBoltInX, cpT2 + cpBoltInY],
    [cpL2 + cpBoltInX, cpB2 - cpBoltInY],
    [cpR2d - cpBoltInX, cpB2 - cpBoltInY],
  ];
  boltPositions.forEach(([bx3,by3]) => {
    svg.appendChild($c(bx3, by3, cpBoltR, 'bolt'));
  });

  // Dimensions — edge distances
  dimH(svg, cpL2, cpL2 + cpBoltInX, cpT2, -10, `${C.boltInset}"`);
  dimH(svg, cpR2d - cpBoltInX, cpR2d, cpT2, -10, `${C.boltInset}"`);
  dimV(svg, cpL2, cpT2, cpT2 + cpBoltInY, -14, `${C.boltInset}"`);
  dimV(svg, cpL2, cpB2 - cpBoltInY, cpB2, -14, `${C.boltInset}"`);

  // Bolt-to-bolt gage dims
  const boltGageX = (cpR2d - cpBoltInX) - (cpL2 + cpBoltInX);
  const boltGageY = (cpB2 - cpBoltInY) - (cpT2 + cpBoltInY);
  dimH(svg, cpL2 + cpBoltInX, cpR2d - cpBoltInX, cpB2, 12, `${(C.capW - 2*C.boltInset).toFixed(2)}"`);
  dimV(svg, cpR2d, cpT2 + cpBoltInY, cpB2 - cpBoltInY, 14, `${(C.capH - 2*C.boltInset).toFixed(2)}"`);

  // Overall dims
  dimH(svg, cpL2, cpR2d, cpT2, -24, `${C.capW}"`);
  dimV(svg, cpL2, cpT2, cpB2, -28, `${C.capH}"`);

  // Labels
  svg.appendChild($t(cpDtlX, cpB2 + 22, 'DETAIL 2 — CAP PLATE (p3)', 'lblb', 'middle'));
  svg.appendChild($t(cpDtlX, cpB2 + 33, `A572 Gr.50 — 3/4" THK — 4x 15/16" DIA HOLES`, 'note', 'middle'));

  // ════════════════════════
  // TITLE BLOCK
  // ════════════════════════
  const ty = 695, th = 135, tx = 20, tw = 1060;
  svg.appendChild($r(tx,ty,tw,th,'obj thick'));

  const c1=tx, c2=tx+220, c3=c2+240, c4=c3+160, c5=c4+200;
  [c2,c3,c4,c5].forEach(cx => svg.appendChild($l(cx,ty,cx,ty+th,'obj med')));

  svg.appendChild($t(c1+110, ty+20, 'Structures America', 'lblb', 'middle'));
  svg.appendChild($t(c1+110, ty+34, '14369 FM 1314', 'lbl', 'middle'));
  svg.appendChild($t(c1+110, ty+46, 'Conroe, TX 77302', 'lbl', 'middle'));
  svg.appendChild($t(c1+110, ty+58, '505-270-1877', 'lbl', 'middle'));
  svg.appendChild($l(c1,ty+68,c2,ty+68,'obj hair'));
  svg.appendChild($t(c1+8, ty+80, 'DESIGN/REVIEW AUTHORITY:', 'noteb'));
  svg.appendChild($t(c1+8, ty+92, 'PLEASE REVIEW THIS DRAWING CAREFULLY', 'note'));
  svg.appendChild($t(c1+8, ty+102, 'We assume NO responsibility for the accuracy', 'note'));
  svg.appendChild($t(c1+8, ty+112, 'of information in the contract documents.', 'note'));

  const checkedName = drawingState.checked ? drawingState.checkedBy : '—';
  const curRev = drawingState.revision;
  const pRows = [['PROJECT:', projName],['CUSTOMER:', customer],
    ['JOB:', jobNum],['DATE:', new Date().toLocaleDateString()],
    ['DRAWN:', drawnBy],['CHECKED:', checkedName],['SHEET:', '1 OF 1'],['REV:', String(curRev)]];
  pRows.forEach(([l,v],i) => {
    const py = ty+14+i*15;
    svg.appendChild($t(c2+6, py, l, 'note'));
    svg.appendChild($t(c2+55, py, v, 'lbl'));
    if(i<pRows.length-1) svg.appendChild($l(c2,py+3,c3,py+3,'dim'));
  });

  svg.appendChild($t(c3+80, ty+45, 'COLUMN', 'ttl'));
  svg.appendChild($e('text',{x:c3+80,y:ty+85,class:'ttl','text-anchor':'middle','font-size':'28px'},colMark));

  svg.appendChild($e('rect',{x:c4,y:ty,width:200,height:16,fill:'#333',stroke:'#333'}));
  svg.appendChild($t(c4+8,ty+12,'DATE','note'));
  svg.appendChild($t(c4+50,ty+12,'REV','note'));
  svg.appendChild($t(c4+80,ty+12,'DESCRIPTION','note'));
  drawingState.history.forEach((h,i) => {
    const ry = ty+16+14*(i+1);
    svg.appendChild($t(c4+8,ry,h.date,'note'));
    svg.appendChild($t(c4+52,ry,String(h.rev),'note'));
    svg.appendChild($t(c4+80,ry,h.desc + (h.by ? ' — '+h.by : ''),'note'));
  });

  svg.appendChild($e('rect',{x:c5,y:ty,width:tw-(c5-tx),height:16,fill:'#333',stroke:'#333'}));
  svg.appendChild($t(c5+(tw-(c5-tx))/2, ty+12, 'PROJECT NOTES', 'note', 'middle'));
  ['MATERIAL: A36 UNO','PAINT: COLD GALV 3.0 MIL DFT MIN',
   'HOLES: 15/16" DIA — UNO','NP ZONES: DO NOT PAINT (BOTH ENDS)',
   'FAB PER AISC 360 / AWS D1.1','WELD INSP: VT ALL / MT CRITICAL',
   'WELD SCHEDULE:',
   '  B: CEE stitch 3/16 — 3"@36 (3"@6 ends)',
   '  C: Gusset 3/16 fillet',
   '  D: Rebar 3/16 fillet(NR)/3"@36 stitch(R)',
   '  F: Cap plate 3/16 fillet all-around',
   'ASSY: 1)CEEs 2)Cap 3)Gussets 4)Rebar'].forEach((n,i) =>
    svg.appendChild($t(c5+6, ty+26+i*9, n, 'note')));

  svg.appendChild($t(480, ty-8, `${d.totalCols} - Columns - ${colMark}`, 'ttl'));

  // Footer
  document.getElementById('fWt').textContent = d.totalWt.toLocaleString() + ' lbs';
  document.getElementById('fLen').textContent = `Long: ${fmtFtIn(d.longSideIn)} / Short: ${fmtFtIn(d.shortSideIn)}`;
  document.getElementById('fRbLen').textContent = fmtFtIn(d.rebarLenIn) + (p.reinforced ? ' (inside)' : ' (outside)');
  document.getElementById('fGusH').textContent = d.uphillHyp.toFixed(3) + '"';
  document.getElementById('fGusL').textContent = d.downhillHyp.toFixed(3) + '"';
  document.getElementById('fCols').textContent = d.totalCols;
  document.getElementById('fAngAdd').textContent = `${(d.angleAdd*12).toFixed(1)}" (from ${p.width}' width)`;
  document.getElementById('bomMark').textContent = colMark;

  updateBOM(p, d, colMark);
  setupTips(p, d);

  // Render SVG-based annotations
  renderAnnotations(svg);
}

function updateBOM(p, d, colMark) {
  const cutNote = p.cutAllowance > 0 ? `*` : '';
  const rows = [
    [colMark + cutNote, d.ceeQty, 'CEE Section (Box Beam)', `14x4x10GA x ${fmtFtIn(d.cutLengthIn)}${cutNote}`, 'A36', d.ceeWt],
    ['p3', d.capQty, 'Cap Plate', `3/4" x ${C.capW}" x ${C.capH}"`, 'A572', d.capWt],
    ['p4', d.totalCols*2, `Gusset (High Side)`, `3/8" x 6" x ${d.uphillHyp.toFixed(3)}"`, 'A572', Math.round(d.gusWt/2)],
    ['p5', d.totalCols*2, `Gusset (Low Side)`, `3/8" x 6" x ${d.downhillHyp.toFixed(3)}"`, 'A572', Math.round(d.gusWt/2)],
    ['rb', d.rebarTotal, `${p.rebarSize} Rebar`, `${fmtFtIn(d.rebarLenIn)} ${p.reinforced?'(inside)':'(outside)'}`, 'A706', d.rebarWt],
    ['—', d.totalCols*4, 'Connection Bolts', '9/16" DIA', 'A325', ''],
  ];
  const tb = document.getElementById('bomTB');
  tb.innerHTML = '';
  rows.forEach(r => {
    const tr = document.createElement('tr');
    tr.innerHTML = r.map(v => `<td>${typeof v==='number'?v.toLocaleString():v}</td>`).join('');
    tb.appendChild(tr);
  });
  if (p.cutAllowance > 0) {
    const noteRow = document.createElement('tr');
    noteRow.innerHTML = `<td colspan="6" style="color:#F6AE2D;font-size:0.7rem;padding-top:6px;">* Includes ${p.cutAllowance}" cut allowance for bandsaw vise. Finished long side: ${fmtFtIn(d.longSideIn)}</td>`;
    tb.appendChild(noteRow);
  }
  document.getElementById('bomTotal').textContent = d.totalWt.toLocaleString() + ' lbs';
}

function setupTips(p, d) {
  const info = {
    column: {title:'Column Body — Box Beam', rows:[
      ['CEE Size','14"x4"x10GA'],['Long Side',fmtFtIn(d.longSideIn)],['Short Side',fmtFtIn(d.shortSideIn)],['Cut Length',fmtFtIn(d.cutLengthIn)+' *'],
      ['Top Cut',p.pitch>0.5?`${p.pitch}° angle cut`:'Square cut'],
      ['Angle Add',`${(d.angleAdd*12).toFixed(1)}" (${p.width}' width)`]]},
    capplate: {title:'Cap Plate', rows:[
      ['Size',`${C.capW}" x ${C.capH}" x 3/4"`],['Bolt Holes','4 x 15/16" DIA'],
      ['Pitch',`${p.pitch}°`]]},
    gussets: {title:'Triangle Gussets (4 per column)', rows:[
      ['High Side (p4)',`${d.uphillHyp.toFixed(3)}" hyp`],
      ['Low Side (p5)',`${d.downhillHyp.toFixed(3)}" hyp`],
      ['Legs','6"']]},
    secAA: {title:'Section A-A', rows:[
      ['Box','14" x 8"'],
      ['Rebar',`4x ${p.rebarSize} ${p.reinforced?'INSIDE':'OUTSIDE'}`],
      ['Rebar Len',fmtFtIn(d.rebarLenIn)]]},
    secBB: {title:'Section B-B — Top Assembly', rows:[
      ['Cap Plate',`${C.capW}" x ${C.capH}"`],['Pitch',`${p.pitch}°`],
      ['Gusset p4',`${d.uphillHyp.toFixed(3)}" hyp`],
      ['Gusset p5',`${d.downhillHyp.toFixed(3)}" hyp`]]},
    side: {title:'Side View', rows:[
      ['Depth','8"'],['Long Side',fmtFtIn(d.longSideIn)],['Short Side',fmtFtIn(d.shortSideIn)],
      ['Rebar',p.reinforced?'Inside (dotted)':'Outside (solid)']]},
  };

  const tip = document.getElementById('tip');
  document.querySelectorAll('.hover-part').forEach(el => {
    const key = el.dataset.part;
    const inf = info[key]; if(!inf) return;
    el.onmouseenter = () => {
      tip.innerHTML = `<b>${inf.title}</b>` + inf.rows.map(([k,v])=>`<div class="r"><span class="k">${k}</span><span class="v">${v}</span></div>`).join('');
      tip.style.display = 'block';
    };
    el.onmousemove = e => { tip.style.left=(e.clientX+14)+'px'; tip.style.top=(e.clientY-8)+'px'; };
    el.onmouseleave = () => tip.style.display = 'none';
  });
}

function toggleReinforced() {
  pushUndo(); // snapshot before toggle
  const a = document.getElementById('btnReinforced');
  const b = document.getElementById('btnNonReinforced');
  if (a.classList.contains('active')) {
    a.classList.remove('active'); b.classList.add('active');
  } else {
    b.classList.remove('active'); a.classList.add('active');
  }
  draw();
  scheduleConfigSync(); // sync reinforced toggle back to project
}

['inPitch','inClearHt','inWidth','inFooting','inRebar','inAboveGrade','inCutAllowance'].forEach(id => {
  document.getElementById(id).addEventListener('input', () => {
    pushUndoDebounced(); // snapshot before change
    if (id === 'inPitch') document.getElementById('vPitch').textContent = document.getElementById('inPitch').value + '°';
    draw();
    scheduleConfigSync(); // sync changes back to project
  });
});

['setProjectName','setCustomer','setJobNumber','setDrawnBy','setColumnMark'].forEach(id => {
  const el = document.getElementById(id);
  if (el) el.addEventListener('input', () => { pushUndoDebounced(); draw(); scheduleConfigSync(); });
});

// ════════════════════════
// BIDIRECTIONAL SYNC — Save drawing input changes back to project
// ════════════════════════
let _syncTimer = null;
let _lastSyncPayload = '';

function scheduleConfigSync() {
  clearTimeout(_syncTimer);
  _syncTimer = setTimeout(syncConfigToProject, 1500); // debounce 1.5s
}

function collectDrawingConfig() {
  return {
    roof_pitch_deg: parseFloat(document.getElementById('inPitch').value) || 1.2,
    clear_height_ft: parseFloat(document.getElementById('inClearHt').value) || 14,
    building_width_ft: parseFloat(document.getElementById('inWidth').value) || 40,
    footing_depth_ft: parseFloat(document.getElementById('inFooting').value) || 0,
    col_rebar_size: document.getElementById('inRebar').value || '#9',
    above_grade_ft: parseFloat(document.getElementById('inAboveGrade').value) || 8,
    cut_allowance_in: parseFloat(document.getElementById('inCutAllowance').value) || 6,
    col_reinforced: document.querySelector('.toggle-btn.active')?.textContent?.trim() === 'Reinforced',
    project_name: document.getElementById('setProjectName')?.value || '',
    customer_name: document.getElementById('setCustomer')?.value || '',
    drawn_by: document.getElementById('setDrawnBy')?.value || '',
  };
}

async function syncConfigToProject() {
  const jobCode = window.location.pathname.match(/\/column-drawing\/([^\/]+)/)?.[1];
  if (!jobCode) return;

  const cfg = collectDrawingConfig();
  const payload = JSON.stringify(cfg);

  // Skip if nothing actually changed
  if (payload === _lastSyncPayload) return;
  _lastSyncPayload = payload;

  try {
    // 1. Save to shop drawing config
    await fetch('/api/shop-drawings/config', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ job_code: jobCode, config: cfg }),
    });

    // 2. Push changes back to project buildings array (reverse sync)
    await fetch('/api/project/sync-from-drawing', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ job_code: jobCode, drawing_config: cfg }),
    });

    console.log('[Sync] Drawing config saved for', jobCode);
  } catch(e) {
    console.warn('[Sync] Failed to save config:', e);
  }
}

// ════════════════════════
// DRAWING STATE — Approval, Revision, Annotations
// ════════════════════════
const drawingState = {
  checked: false,
  checkedBy: '',
  revision: 0,
  history: [
    { rev: 0, date: new Date().toLocaleDateString(), desc: 'FOR FABRICATION', by: '' },
  ],
  annotations: [],
};

// ════════════════════════════════════
// INTERACTIVE WELD SYMBOL SYSTEM
// ════════════════════════════════════
// Each weld symbol gets an ID. Overrides store offsets relative to computed defaults.
// On save, offsets are stored so symbols track their anchors when params change.

let weldEditMode = false;
let selectedWeldId = null;
let currentWeldDefs = []; // rebuilt each draw()

// weldOverrides[id] = { dx, dy, rotation, size, stitch, wpsCode, allAround, bothSides, refDir }
const weldOverrides = {
  "bb-gus-l-cap": { "dx": -1.4932022094726562, "dy": 9.8551025390625 },
  "bb-gus-l-col": { "dx": -5.674140930175781, "dy": 5.6741485595703125 },
  "bb-gus-r-cap": { "dx": 20.967315673828125, "dy": 9.697402954101562 },
  "bb-gus-r-col": { "dx": 20.1810302734375, "dy": 6.028106689453125 },
  "fv-gus-hl-cap": { "dx": 43.326751708984375, "dy": 21.07788848876953 },
  "fv-gus-hl-col": { "dx": 9.367950439453125, "dy": 19.321395874023438 },
  "fv-gus-lr-cap": { "dx": -17.93792724609375, "dy": -6.239288330078125 },
  "fv-gus-lr-col": { "dx": 1.81976318359375, "dy": 22.357452392578125 },
  "fv-cee-l": { "dx": 3.35382080078125, "dy": -186.9681396484375 },
  "fv-rebar-l": { "dx": -14.56341552734375, "dy": -40.453948974609375, "size": "3/16", "wpsCode": "D", "stitch": "3\"-36\" O.C.", "refDir": "right", "rotation": 0, "allAround": false, "bothSides": false },
  "aa-cee-bot": { "dx": 18.8785400390625, "dy": -25.89056396484375 },
  "aa-cee-top": { "dx": 0, "dy": 47.0439453125 },
  "sv-cee": { "dx": 25.85491943359375, "dy": -170.35906982421875 },
  "sv-rebar-r": { "dx": 2.479248046875, "dy": 70.12698364257812 },
  "sv-cap": { "dx": 4.60430908203125, "dy": 65.87687683105469 },
  "sv-rebar-l": { "dx": -10.87933349609375, "dy": 6.719635009765625, "size": "3/16", "wpsCode": "D", "stitch": "3\"-36\" O.C.", "refDir": "right", "rotation": 0, "allAround": false, "bothSides": false },
  "fv-cee-r": { "dx": -63.055267333984375, "dy": -219.74072265625 },
  "fv-rebar-r": { "dx": -22.3560791015625, "dy": -38.32476806640625 }
};
// labelOverrides[id] = { dx, dy }
const labelOverrides = {
  "fv-title": { "dx": 58.30224609375, "dy": 9.2945556640625 },
  "sv-title": { "dx": 53.23248291015625, "dy": 8.4495849609375 }
};
let selectedLabelId = null;

// Load saved overrides
try {
  const sw = JSON.parse(localStorage.getItem('titanforge-weld-overrides'));
  if (sw) Object.assign(weldOverrides, sw);
} catch(e) {}
try {
  const sl = JSON.parse(localStorage.getItem('titanforge-label-overrides'));
  if (sl) Object.assign(labelOverrides, sl);
} catch(e) {}

function toggleWeldEditMode() {
  weldEditMode = !weldEditMode;
  const btn = document.getElementById('btnWeldEdit');
  btn.style.background = weldEditMode ? '#EF4444' : '#0055AA';
  btn.textContent = weldEditMode ? '🔧 Done Editing' : '🔧 Edit Welds';
  const hasOverrides = Object.keys(weldOverrides).length > 0 || Object.keys(labelOverrides).length > 0;
  document.getElementById('btnWeldReset').style.display = hasOverrides ? 'inline-block' : 'none';
  document.getElementById('btnExportLayout').style.display = weldEditMode ? 'inline-block' : 'none';
  if (!weldEditMode) {
    selectedWeldId = null;
    selectedLabelId = null;
    document.getElementById('weldEditor').classList.remove('show');
  }
  draw();
}

function openWeldEditor(id) {
  const def = currentWeldDefs.find(w => w.id === id);
  if (!def) return;
  selectedWeldId = id;
  const ov = weldOverrides[id] || {};
  document.getElementById('weId').textContent = id;
  document.getElementById('weSize').value = ov.size !== undefined ? ov.size : (def.size || '');
  document.getElementById('weWps').value = ov.wpsCode !== undefined ? ov.wpsCode : (def.opts.wpsCode || '');
  document.getElementById('weStitch').value = ov.stitch !== undefined ? ov.stitch : (def.opts.stitch || '');
  document.getElementById('weRefDir').value = ov.refDir !== undefined ? ov.refDir : (def.opts.refDir || 'right');
  document.getElementById('weRotation').value = ov.rotation || 0;
  document.getElementById('weRotVal').textContent = (ov.rotation || 0) + '°';
  document.getElementById('weAllAround').checked = ov.allAround !== undefined ? ov.allAround : !!def.opts.allAround;
  document.getElementById('weBothSides').checked = ov.bothSides !== undefined ? ov.bothSides : !!def.opts.bothSides;
  document.getElementById('weldEditor').classList.add('show');
  draw();
}

// ── LIVE EDITING — every field change updates the drawing instantly ──
function liveApply() {
  if (!selectedWeldId) return;
  pushUndoDebounced(); // snapshot before live edit
  if (!weldOverrides[selectedWeldId]) weldOverrides[selectedWeldId] = {};
  const ov = weldOverrides[selectedWeldId];
  ov.size = document.getElementById('weSize').value;
  ov.wpsCode = document.getElementById('weWps').value;
  ov.stitch = document.getElementById('weStitch').value;
  ov.refDir = document.getElementById('weRefDir').value;
  ov.rotation = parseInt(document.getElementById('weRotation').value) || 0;
  ov.allAround = document.getElementById('weAllAround').checked;
  ov.bothSides = document.getElementById('weBothSides').checked;
  document.getElementById('weRotVal').textContent = ov.rotation + '°';
  draw();
}

// Hook up LIVE listeners on every editor field
['weSize','weWps','weStitch'].forEach(id => {
  document.getElementById(id).addEventListener('input', liveApply);
});
['weRefDir'].forEach(id => {
  document.getElementById(id).addEventListener('change', liveApply);
});
document.getElementById('weRotation').addEventListener('input', liveApply);
document.getElementById('weAllAround').addEventListener('change', liveApply);
document.getElementById('weBothSides').addEventListener('change', liveApply);

function applyWeldEdit() {
  // With live editing, Apply just confirms — flash green
  liveApply();
  const btn = document.querySelector('.we-actions .we-apply-btn');
  if (btn) { btn.textContent = '✓ Applied'; setTimeout(() => btn.textContent = '✓ Apply', 800); }
}

function resetSelectedWeld() {
  if (!selectedWeldId) return;
  pushUndo(); // snapshot before reset
  delete weldOverrides[selectedWeldId];
  openWeldEditor(selectedWeldId); // refresh panel with defaults
  draw();
}

function closeWeldEditor() {
  selectedWeldId = null;
  document.getElementById('weldEditor').classList.remove('show');
  draw();
}

function saveWeldOverrides() {
  // Persist both weld and label overrides to localStorage
  try { localStorage.setItem('titanforge-weld-overrides', JSON.stringify(weldOverrides)); } catch(e) {}
  try { localStorage.setItem('titanforge-label-overrides', JSON.stringify(labelOverrides)); } catch(e) {}
  const hasOverrides = Object.keys(weldOverrides).length > 0 || Object.keys(labelOverrides).length > 0;
  document.getElementById('btnWeldReset').style.display = hasOverrides ? 'inline-block' : 'none';
  // Flash save confirmation
  const btn = document.getElementById('weSaveBtn');
  if (btn) {
    const orig = btn.textContent;
    btn.textContent = '✓ Saved!';
    btn.style.background = '#065F46';
    btn.style.color = '#6EE7B7';
    setTimeout(() => { btn.textContent = orig; btn.style.background = '#F6AE2D'; btn.style.color = '#0F172A'; }, 1200);
  }
}

function resetAllWeldOverrides() {
  if (!confirm('Reset ALL weld & label positions back to defaults?')) return;
  pushUndo();
  Object.keys(weldOverrides).forEach(k => delete weldOverrides[k]);
  Object.keys(labelOverrides).forEach(k => delete labelOverrides[k]);
  try { localStorage.removeItem('titanforge-weld-overrides'); } catch(e) {}
  try { localStorage.removeItem('titanforge-label-overrides'); } catch(e) {}
  selectedWeldId = null;
  selectedLabelId = null;
  document.getElementById('weldEditor').classList.remove('show');
  document.getElementById('btnWeldReset').style.display = 'none';
  draw();
}

function exportLayout() {
  const layout = { weldOverrides: {...weldOverrides}, labelOverrides: {...labelOverrides} };
  const json = JSON.stringify(layout, null, 2);
  // Always show modal — clipboard API is unreliable on local files
  showExportModal(json);
}

function showExportModal(json) {
  let modal = document.getElementById('exportModal');
  if (modal) modal.remove();
  modal = document.createElement('div');
  modal.id = 'exportModal';
  modal.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.7);display:flex;align-items:center;justify-content:center;z-index:9999;';
  const box = document.createElement('div');
  box.style.cssText = 'background:#1E293B;border:1px solid #475569;border-radius:8px;padding:20px;max-width:600px;width:90%;color:#E2E8F0;';
  box.innerHTML = '<h3 style="margin:0 0 8px 0;font-size:14px;">Export Layout JSON</h3><p style="margin:0 0 8px 0;font-size:12px;color:#94A3B8;">Select all and copy (Cmd+A then Cmd+C):</p>';
  const ta = document.createElement('textarea');
  ta.value = json;
  ta.style.cssText = 'width:100%;height:250px;background:#0F172A;color:#E2E8F0;border:1px solid #334155;border-radius:4px;padding:8px;font-family:monospace;font-size:11px;resize:vertical;';
  ta.readOnly = true;
  box.appendChild(ta);
  const btnRow = document.createElement('div');
  btnRow.style.cssText = 'display:flex;gap:8px;margin-top:12px;justify-content:flex-end;';
  const copyBtn = document.createElement('button');
  copyBtn.textContent = 'Copy to Clipboard';
  copyBtn.style.cssText = 'padding:6px 14px;background:#0055AA;color:white;border:none;border-radius:4px;cursor:pointer;font-size:12px;';
  copyBtn.onclick = function() {
    ta.select();
    document.execCommand('copy');
    copyBtn.textContent = '✓ Copied!';
    setTimeout(() => { copyBtn.textContent = 'Copy to Clipboard'; }, 2000);
  };
  const closeBtn = document.createElement('button');
  closeBtn.textContent = 'Close';
  closeBtn.style.cssText = 'padding:6px 14px;background:#475569;color:white;border:none;border-radius:4px;cursor:pointer;font-size:12px;';
  closeBtn.onclick = function() { modal.remove(); };
  btnRow.appendChild(copyBtn);
  btnRow.appendChild(closeBtn);
  box.appendChild(btnRow);
  modal.appendChild(box);
  modal.onclick = function(e) { if (e.target === modal) modal.remove(); };
  document.body.appendChild(modal);
  setTimeout(() => { ta.focus(); ta.select(); }, 100);
}

function updateCheckBadge() {
  const badge = document.getElementById('checkBadge');
  if (drawingState.checked) {
    badge.className = 'checked-badge';
    badge.textContent = '✓ CHECKED — ' + drawingState.checkedBy;
    badge.style.cursor = 'default';
    badge.onclick = null;
  } else {
    badge.className = 'unchecked-badge';
    badge.textContent = '✗ UNCHECKED';
    badge.style.cursor = 'pointer';
    badge.onclick = startApproval;
  }
}

function startApproval() {
  if (drawingState.checked) return;
  document.getElementById('approverName').value = '';
  document.getElementById('approvalModal').classList.add('show');
}

function cancelApproval() {
  document.getElementById('approvalModal').classList.remove('show');
}

function confirmApproval() {
  const name = document.getElementById('approverName').value.trim();
  if (!name) { alert('Please enter your name.'); return; }
  drawingState.checked = true;
  drawingState.checkedBy = name;
  drawingState.revision++;
  drawingState.history.push({
    rev: drawingState.revision,
    date: new Date().toLocaleDateString(),
    desc: 'CHECKED & APPROVED',
    by: name,
  });
  document.getElementById('approvalModal').classList.remove('show');
  updateCheckBadge();
  draw();
}

function createNewRevision() {
  drawingState.checked = false;
  drawingState.checkedBy = '';
  drawingState.revision++;
  drawingState.history.push({
    rev: drawingState.revision,
    date: new Date().toLocaleDateString(),
    desc: 'REVISED',
    by: '',
  });
  updateCheckBadge();
  draw();
}

// ════════════════════════
// FREEFORM ANNOTATIONS (SVG-BASED)
// ════════════════════════
let annotateMode = false;

function toggleAnnotateMode() {
  annotateMode = !annotateMode;
  const btn = document.getElementById('btnAnnotate');
  btn.classList.toggle('active', annotateMode);
  btn.textContent = annotateMode ? '📝 Click to Place' : '📝 Annotate';
  document.getElementById('svg').style.cursor = annotateMode ? 'crosshair' : '';
}

function svgPoint(e) {
  const svgEl = document.getElementById('svg');
  const pt = svgEl.createSVGPoint();
  pt.x = e.clientX;
  pt.y = e.clientY;
  return pt.matrixTransform(svgEl.getScreenCTM().inverse());
}

document.getElementById('svg').addEventListener('click', function(e) {
  if (!annotateMode) return;
  const pt = svgPoint(e);
  const text = prompt('Enter annotation text:');
  if (!text || !text.trim()) return;
  pushUndo(); // snapshot before adding annotation
  drawingState.annotations.push({ id: Math.random(), text: text.trim(), svgX: pt.x, svgY: pt.y });
  draw();
});

function renderAnnotations(svg) {
  drawingState.annotations.forEach((a, i) => {
    const g = document.createElementNS(NS, 'g');
    g.setAttribute('class', 'svg-annotation');
    g.setAttribute('transform', `translate(${a.svgX}, ${a.svgY})`);
    g.setAttribute('data-anno-idx', i);

    // Background rect
    const rectW = Math.max(a.text.length * 5, 40);
    const r = document.createElementNS(NS, 'rect');
    r.setAttribute('x', 0);
    r.setAttribute('y', -10);
    r.setAttribute('width', rectW);
    r.setAttribute('height', 14);
    r.setAttribute('rx', 2);
    r.setAttribute('fill', '#FEF3C7');
    r.setAttribute('stroke', '#F59E0B');
    r.setAttribute('stroke-width', '0.5');
    g.appendChild(r);

    // Text
    const t = document.createElementNS(NS, 'text');
    t.setAttribute('x', 3);
    t.setAttribute('y', 0);
    t.setAttribute('font-size', '7');
    t.setAttribute('font-family', 'Arial');
    t.setAttribute('fill', '#92400E');
    t.textContent = a.text;
    g.appendChild(t);

    // Delete circle
    const dc = document.createElementNS(NS, 'circle');
    dc.setAttribute('cx', rectW + 4);
    dc.setAttribute('cy', -10);
    dc.setAttribute('r', 4);
    dc.setAttribute('fill', '#EF4444');
    dc.setAttribute('stroke', 'none');
    dc.setAttribute('style', 'cursor:pointer; opacity:0');
    dc.setAttribute('class', 'anno-del-circle');
    g.appendChild(dc);

    // Delete X text
    const dx = document.createElementNS(NS, 'text');
    dx.setAttribute('x', rectW + 4);
    dx.setAttribute('y', -7);
    dx.setAttribute('font-size', '6');
    dx.setAttribute('text-anchor', 'middle');
    dx.setAttribute('fill', '#FFF');
    dx.setAttribute('style', 'cursor:pointer; opacity:0; pointer-events:none');
    dx.setAttribute('class', 'anno-del-x');
    dx.textContent = '✕';
    g.appendChild(dx);

    // Hover show/hide delete
    g.addEventListener('mouseenter', () => {
      dc.style.opacity = '1';
      dx.style.opacity = '1';
    });
    g.addEventListener('mouseleave', () => {
      dc.style.opacity = '0';
      dx.style.opacity = '0';
    });

    // Delete handler
    dc.addEventListener('click', (e) => {
      e.stopPropagation();
      pushUndo(); // snapshot before deleting annotation
      drawingState.annotations.splice(i, 1);
      draw();
    });

    // Drag handler
    let dragging = false, startSvgX, startSvgY, origX, origY;
    g.addEventListener('mousedown', (e) => {
      if (e.target === dc) return;
      e.stopPropagation();
      dragging = true;
      const pt = svgPoint(e);
      startSvgX = pt.x;
      startSvgY = pt.y;
      origX = a.svgX;
      origY = a.svgY;
    });

    // Drag move and end handlers attached to SVG
    const dragMoveHandler = function(e) {
      if (!dragging) return;
      const pt = svgPoint(e);
      a.svgX = origX + (pt.x - startSvgX);
      a.svgY = origY + (pt.y - startSvgY);
      g.setAttribute('transform', `translate(${a.svgX}, ${a.svgY})`);
    };

    const dragEndHandler = function() {
      dragging = false;
    };

    svg.addEventListener('mousemove', dragMoveHandler);
    svg.addEventListener('mouseup', dragEndHandler);

    svg.appendChild(g);
  });
}

updateCheckBadge();
draw();

// Push initial state so first Cmd+Z has something to revert to
setTimeout(() => { undoHistory.push(captureState()); }, 100);

// ════════════════════════════════════
// WELD SYMBOL DRAG + ROTATE + SELECT HANDLERS
// ════════════════════════════════════
(function() {
  const svgEl = document.getElementById('svg');
  let dragWeld = null;  // {id, startX, startY, origDx, origDy}
  let rotWeld = null;   // {id, centerX, centerY, startAngle, origRotation}

  svgEl.addEventListener('mousedown', function(e) {
    if (!weldEditMode) return;

    // Check for rotation handle first
    const rotHandle = e.target.closest('[data-rot-handle]');
    if (rotHandle) {
      e.stopPropagation();
      e.preventDefault();
      pushUndo(); // snapshot before rotation
      const id = rotHandle.getAttribute('data-rot-handle');
      const def = currentWeldDefs.find(w => w.id === id);
      if (!def) return;
      const ov = weldOverrides[id] || {};
      const centerX = def.routeX + (ov.dx || 0);
      const centerY = def.routeY + (ov.dy || 0);
      const pt = svgPoint(e);
      const startAngle = Math.atan2(pt.y - centerY, pt.x - centerX) * 180 / Math.PI;
      rotWeld = {
        id: id,
        centerX: centerX,
        centerY: centerY,
        startAngle: startAngle,
        origRotation: ov.rotation || 0
      };
      return;
    }

    // Check for draggable label
    const lg = e.target.closest('[data-label-id]');
    if (lg) {
      e.stopPropagation();
      e.preventDefault();
      const lid = lg.getAttribute('data-label-id');
      selectedLabelId = lid;
      selectedWeldId = null;
      document.getElementById('weldEditor').classList.remove('show');
      pushUndo();
      const pt = svgPoint(e);
      const lov = labelOverrides[lid] || {};
      dragWeld = {
        id: lid,
        startX: pt.x,
        startY: pt.y,
        origDx: lov.dx || 0,
        origDy: lov.dy || 0,
        isLabel: true
      };
      draw();
      return;
    }

    // Check for weld group (drag)
    const wg = e.target.closest('[data-weld-id]');
    if (!wg) return;
    const id = wg.getAttribute('data-weld-id');

    e.stopPropagation();
    e.preventDefault();

    // Select it and open editor
    selectedLabelId = null;
    openWeldEditor(id);
    pushUndo(); // snapshot before drag

    // Start drag
    const pt = svgPoint(e);
    const ov = weldOverrides[id] || {};
    dragWeld = {
      id: id,
      startX: pt.x,
      startY: pt.y,
      origDx: ov.dx || 0,
      origDy: ov.dy || 0,
      isLabel: false
    };
    wg.classList.add('dragging');
  });

  window.addEventListener('mousemove', function(e) {
    // Handle rotation drag
    if (rotWeld) {
      const pt = svgPoint(e);
      const currentAngle = Math.atan2(pt.y - rotWeld.centerY, pt.x - rotWeld.centerX) * 180 / Math.PI;
      let delta = currentAngle - rotWeld.startAngle;
      // Snap to 5-degree increments
      const newRot = Math.round((rotWeld.origRotation + delta) / 5) * 5;
      if (!weldOverrides[rotWeld.id]) weldOverrides[rotWeld.id] = {};
      weldOverrides[rotWeld.id].rotation = newRot;
      // Sync the slider in the editor
      if (selectedWeldId === rotWeld.id) {
        document.getElementById('weRotation').value = newRot;
        document.getElementById('weRotVal').textContent = newRot + '°';
      }
      draw();
      return;
    }

    // Handle position drag (weld or label)
    if (!dragWeld) return;
    const pt = svgPoint(e);
    const dx = pt.x - dragWeld.startX;
    const dy = pt.y - dragWeld.startY;
    if (dragWeld.isLabel) {
      if (!labelOverrides[dragWeld.id]) labelOverrides[dragWeld.id] = {};
      labelOverrides[dragWeld.id].dx = dragWeld.origDx + dx;
      labelOverrides[dragWeld.id].dy = dragWeld.origDy + dy;
    } else {
      if (!weldOverrides[dragWeld.id]) weldOverrides[dragWeld.id] = {};
      weldOverrides[dragWeld.id].dx = dragWeld.origDx + dx;
      weldOverrides[dragWeld.id].dy = dragWeld.origDy + dy;
    }
    draw();
  });

  window.addEventListener('mouseup', function() {
    if (dragWeld) {
      const wg = document.querySelector(`[data-weld-id="${dragWeld.id}"]`);
      if (wg) wg.classList.remove('dragging');
      dragWeld = null;
    }
    if (rotWeld) {
      rotWeld = null;
    }
  });

  // Click on empty space in edit mode = deselect
  svgEl.addEventListener('click', function(e) {
    if (!weldEditMode) return;
    if (!e.target.closest('[data-weld-id]') && !e.target.closest('[data-rot-handle]') && !e.target.closest('[data-label-id]')) {
      selectedWeldId = null;
      selectedLabelId = null;
      document.getElementById('weldEditor').classList.remove('show');
      draw();
    }
  });
})();

// ════════════════════════════════════
// UNDO / REDO SYSTEM
// ════════════════════════════════════
const undoHistory = [];
const redoHistory = [];
const MAX_UNDO = 60;

function captureState() {
  // Snapshot everything that can change: weld overrides, label overrides, annotations, input values
  return JSON.stringify({
    weldOverrides: JSON.parse(JSON.stringify(weldOverrides)),
    labelOverrides: JSON.parse(JSON.stringify(labelOverrides)),
    annotations: JSON.parse(JSON.stringify(drawingState.annotations)),
    inputs: {
      pitch: document.getElementById('inPitch').value,
      clearHt: document.getElementById('inClearHt').value,
      width: document.getElementById('inWidth').value,
      footing: document.getElementById('inFooting').value,
      rebar: document.getElementById('inRebar').value,
      aboveGrade: document.getElementById('inAboveGrade').value,
      cutAllowance: document.getElementById('inCutAllowance').value,
      reinforced: document.getElementById('btnReinforced').classList.contains('active'),
    },
    settings: {
      projectName: document.getElementById('setProjectName').value,
      customer: document.getElementById('setCustomer').value,
      jobNumber: document.getElementById('setJobNumber').value,
      drawnBy: document.getElementById('setDrawnBy').value,
      columnMark: document.getElementById('setColumnMark').value,
    },
  });
}

function restoreState(snapshot) {
  const s = JSON.parse(snapshot);

  // Restore weld overrides
  Object.keys(weldOverrides).forEach(k => delete weldOverrides[k]);
  Object.assign(weldOverrides, s.weldOverrides);

  // Restore label overrides
  Object.keys(labelOverrides).forEach(k => delete labelOverrides[k]);
  if (s.labelOverrides) Object.assign(labelOverrides, s.labelOverrides);

  // Restore annotations
  drawingState.annotations = s.annotations;

  // Restore inputs
  document.getElementById('inPitch').value = s.inputs.pitch;
  document.getElementById('vPitch').textContent = s.inputs.pitch + '°';
  document.getElementById('inClearHt').value = s.inputs.clearHt;
  document.getElementById('inWidth').value = s.inputs.width;
  document.getElementById('inFooting').value = s.inputs.footing;
  document.getElementById('inRebar').value = s.inputs.rebar;
  document.getElementById('inAboveGrade').value = s.inputs.aboveGrade;
  document.getElementById('inCutAllowance').value = s.inputs.cutAllowance;

  // Restore reinforced toggle
  const btnR = document.getElementById('btnReinforced');
  const btnN = document.getElementById('btnNonReinforced');
  if (s.inputs.reinforced) {
    btnR.classList.add('active'); btnN.classList.remove('active');
  } else {
    btnR.classList.remove('active'); btnN.classList.add('active');
  }

  // Restore settings
  document.getElementById('setProjectName').value = s.settings.projectName;
  document.getElementById('setCustomer').value = s.settings.customer;
  document.getElementById('setJobNumber').value = s.settings.jobNumber;
  document.getElementById('setDrawnBy').value = s.settings.drawnBy;
  document.getElementById('setColumnMark').value = s.settings.columnMark;

  // Refresh editor panel if a weld is selected
  if (selectedWeldId && weldOverrides[selectedWeldId]) {
    openWeldEditor(selectedWeldId);
  } else {
    draw();
  }
}

// Push current state onto undo stack (call BEFORE making a change)
function pushUndo() {
  const snap = captureState();
  // Don't push duplicates
  if (undoHistory.length > 0 && undoHistory[undoHistory.length - 1] === snap) return;
  undoHistory.push(snap);
  if (undoHistory.length > MAX_UNDO) undoHistory.shift();
  // Clear redo stack on new action
  redoHistory.length = 0;
  updateUndoUI();
}

function undo() {
  if (undoHistory.length === 0) return;
  // Save current state to redo
  redoHistory.push(captureState());
  // Pop and restore
  const prev = undoHistory.pop();
  restoreState(prev);
  updateUndoUI();
  flashStatus('Undo');
}

function redo() {
  if (redoHistory.length === 0) return;
  // Save current state to undo
  undoHistory.push(captureState());
  // Pop and restore
  const next = redoHistory.pop();
  restoreState(next);
  updateUndoUI();
  flashStatus('Redo');
}

function updateUndoUI() {
  // Show undo/redo count in status (optional — we'll use footer)
}

function flashStatus(msg) {
  // Brief status flash in the footer
  const fWt = document.getElementById('fWt');
  const orig = fWt.textContent;
  fWt.textContent = msg;
  fWt.style.color = '#6CB4EE';
  setTimeout(() => { fWt.textContent = orig; fWt.style.color = ''; }, 600);
}

// Debounced push — for input fields that fire rapidly (sliders, typing)
let undoPushTimer = null;
function pushUndoDebounced() {
  if (undoPushTimer) clearTimeout(undoPushTimer);
  // Capture BEFORE the change (on first call of a burst)
  if (!undoPushTimer) {
    const snap = captureState();
    undoPushTimer = setTimeout(() => {
      // Only push if state actually changed
      if (undoHistory.length === 0 || undoHistory[undoHistory.length - 1] !== snap) {
        undoHistory.push(snap);
        if (undoHistory.length > MAX_UNDO) undoHistory.shift();
        redoHistory.length = 0;
      }
      undoPushTimer = null;
    }, 400);
  }
}

// ════════════════════════════════════
// COPY / PASTE WELD SYMBOLS
// ════════════════════════════════════
let copiedWeld = null; // { size, opts, rotation }

function copySelectedWeld() {
  if (!selectedWeldId) return;
  const def = currentWeldDefs.find(w => w.id === selectedWeldId);
  if (!def) return;
  const ov = weldOverrides[selectedWeldId] || {};
  copiedWeld = {
    size: ov.size !== undefined ? ov.size : def.size,
    wpsCode: ov.wpsCode !== undefined ? ov.wpsCode : def.opts.wpsCode,
    stitch: ov.stitch !== undefined ? ov.stitch : def.opts.stitch,
    refDir: ov.refDir !== undefined ? ov.refDir : def.opts.refDir,
    rotation: ov.rotation || 0,
    allAround: ov.allAround !== undefined ? ov.allAround : def.opts.allAround,
    bothSides: ov.bothSides !== undefined ? ov.bothSides : def.opts.bothSides,
  };
  flashStatus('Copied: ' + selectedWeldId);
}

function pasteToSelectedWeld() {
  if (!selectedWeldId || !copiedWeld) return;
  pushUndo();
  if (!weldOverrides[selectedWeldId]) weldOverrides[selectedWeldId] = {};
  const ov = weldOverrides[selectedWeldId];
  // Paste all style properties (but NOT position — keep the target's position)
  ov.size = copiedWeld.size;
  ov.wpsCode = copiedWeld.wpsCode;
  ov.stitch = copiedWeld.stitch;
  ov.refDir = copiedWeld.refDir;
  ov.rotation = copiedWeld.rotation;
  ov.allAround = copiedWeld.allAround;
  ov.bothSides = copiedWeld.bothSides;
  // Refresh editor
  openWeldEditor(selectedWeldId);
  flashStatus('Pasted to: ' + selectedWeldId);
}

// ════════════════════════════════════
// KEYBOARD SHORTCUTS
// ════════════════════════════════════
window.addEventListener('keydown', function(e) {
  // Don't intercept if user is typing in an input/textarea
  const tag = (e.target.tagName || '').toLowerCase();
  if (tag === 'input' || tag === 'textarea' || tag === 'select') {
    // Allow Cmd+Z in inputs only for native undo (don't override)
    return;
  }

  const isMeta = e.metaKey || e.ctrlKey;

  // Cmd+Z = Undo, Cmd+Shift+Z = Redo
  if (isMeta && e.key === 'z' && !e.shiftKey) {
    e.preventDefault();
    e.stopPropagation();
    undo();
    return;
  }
  if (isMeta && e.key === 'z' && e.shiftKey) {
    e.preventDefault();
    e.stopPropagation();
    redo();
    return;
  }
  // Cmd+Y = Redo (Windows convention)
  if (isMeta && e.key === 'y') {
    e.preventDefault();
    e.stopPropagation();
    redo();
    return;
  }

  // Cmd+C = Copy weld symbol
  if (isMeta && e.key === 'c' && weldEditMode && selectedWeldId) {
    e.preventDefault();
    e.stopPropagation();
    copySelectedWeld();
    return;
  }

  // Cmd+V = Paste weld symbol style
  if (isMeta && e.key === 'v' && weldEditMode && selectedWeldId && copiedWeld) {
    e.preventDefault();
    e.stopPropagation();
    pasteToSelectedWeld();
    return;
  }

  // Delete / Backspace = reset selected weld to defaults
  if ((e.key === 'Delete' || e.key === 'Backspace') && weldEditMode && selectedWeldId) {
    e.preventDefault();
    pushUndo();
    resetSelectedWeld();
    return;
  }

  // Escape = deselect / close editor
  if (e.key === 'Escape') {
    if (weldEditMode && selectedWeldId) {
      selectedWeldId = null;
      document.getElementById('weldEditor').classList.remove('show');
      draw();
    } else if (weldEditMode) {
      toggleWeldEditMode();
    }
    return;
  }
});

// ════════════════════════
// ZOOM + PAN (v8)
// ════════════════════════
(function() {
  const svgEl = document.getElementById('svg');
  const origVB = { x: 0, y: 0, w: 1100, h: 850 };
  let vb = { ...origVB };
  let isPanning = false;
  let startPt = { x: 0, y: 0 };
  let startVB = { x: 0, y: 0 };

  function applyVB() {
    svgEl.setAttribute('viewBox', `${vb.x} ${vb.y} ${vb.w} ${vb.h}`);
  }

  function getSVGPoint(evt) {
    const rect = svgEl.getBoundingClientRect();
    return {
      x: (evt.clientX - rect.left) / rect.width * vb.w + vb.x,
      y: (evt.clientY - rect.top) / rect.height * vb.h + vb.y
    };
  }

  // Mouse wheel zoom
  svgEl.addEventListener('wheel', function(e) {
    e.preventDefault();
    const zoomFactor = e.deltaY > 0 ? 1.12 : 0.88;
    const pt = getSVGPoint(e);

    const newW = vb.w * zoomFactor;
    const newH = vb.h * zoomFactor;
    // Zoom toward mouse position
    vb.x = pt.x - (pt.x - vb.x) * zoomFactor;
    vb.y = pt.y - (pt.y - vb.y) * zoomFactor;
    vb.w = newW;
    vb.h = newH;
    applyVB();
  }, { passive: false });

  // Mouse drag pan
  svgEl.addEventListener('mousedown', function(e) {
    if (e.button !== 0) return;
    // Don't pan when clicking weld symbols or labels in edit mode
    if (weldEditMode && (e.target.closest('[data-weld-id]') || e.target.closest('[data-label-id]'))) return;
    isPanning = true;
    startPt = { x: e.clientX, y: e.clientY };
    startVB = { x: vb.x, y: vb.y };
    svgEl.style.cursor = 'grabbing';
  });
  window.addEventListener('mousemove', function(e) {
    if (!isPanning) return;
    const rect = svgEl.getBoundingClientRect();
    const dx = (e.clientX - startPt.x) / rect.width * vb.w;
    const dy = (e.clientY - startPt.y) / rect.height * vb.h;
    vb.x = startVB.x - dx;
    vb.y = startVB.y - dy;
    applyVB();
  });
  window.addEventListener('mouseup', function() {
    isPanning = false;
    svgEl.style.cursor = '';
  });

  // Touch drag pan
  svgEl.addEventListener('touchstart', function(e) {
    if (e.touches.length === 1) {
      isPanning = true;
      startPt = { x: e.touches[0].clientX, y: e.touches[0].clientY };
      startVB = { x: vb.x, y: vb.y };
    }
  }, { passive: true });
  svgEl.addEventListener('touchmove', function(e) {
    if (!isPanning || e.touches.length !== 1) return;
    e.preventDefault();
    const rect = svgEl.getBoundingClientRect();
    const dx = (e.touches[0].clientX - startPt.x) / rect.width * vb.w;
    const dy = (e.touches[0].clientY - startPt.y) / rect.height * vb.h;
    vb.x = startVB.x - dx;
    vb.y = startVB.y - dy;
    applyVB();
  }, { passive: false });
  svgEl.addEventListener('touchend', function() {
    isPanning = false;
  });

  // Pinch zoom (two fingers)
  let lastPinchDist = 0;
  svgEl.addEventListener('touchstart', function(e) {
    if (e.touches.length === 2) {
      isPanning = false;
      const dx = e.touches[0].clientX - e.touches[1].clientX;
      const dy = e.touches[0].clientY - e.touches[1].clientY;
      lastPinchDist = Math.sqrt(dx*dx + dy*dy);
    }
  }, { passive: true });
  svgEl.addEventListener('touchmove', function(e) {
    if (e.touches.length === 2) {
      e.preventDefault();
      const dx = e.touches[0].clientX - e.touches[1].clientX;
      const dy = e.touches[0].clientY - e.touches[1].clientY;
      const dist = Math.sqrt(dx*dx + dy*dy);
      if (lastPinchDist > 0) {
        const zoomFactor = lastPinchDist / dist;
        const cx = vb.x + vb.w / 2;
        const cy = vb.y + vb.h / 2;
        vb.w *= zoomFactor;
        vb.h *= zoomFactor;
        vb.x = cx - vb.w / 2;
        vb.y = cy - vb.h / 2;
        applyVB();
      }
      lastPinchDist = dist;
    }
  }, { passive: false });

  // Reset zoom function (global)
  window.resetZoom = function() {
    vb = { ...origVB };
    applyVB();
  };
})();

// ══════════════════════════════════════════════════════
//  TITANFORGE INTEGRATION
// ══════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', function() {
  // Extract job code from URL
  const jobCode = window.location.pathname.match(/\/column-drawing\/([^\/]+)/)?.[1];
  if (jobCode) {
    // Fetch project config from TitanForge API
    fetch('/api/shop-drawings/config?job_code=' + encodeURIComponent(jobCode))
      .then(resp => resp.json())
      .then(data => {
        if (data.ok && data.config) {
          applyConfigToDrawing(data.config);
        }
      })
      .catch(err => console.error('Failed to load project config:', err));
  }
});

// Map TitanForge ShopDrawingConfig fields to drawing input elements
function applyConfigToDrawing(config) {
  // Map config field names → [inputId, optional transform]
  const mappings = [
    ['roof_pitch_deg', 'inPitch'],
    ['clear_height_ft', 'inClearHt'],
    ['building_width_ft', 'inWidth'],
    ['footing_depth_ft', 'inFooting'],
    ['col_rebar_size', 'inRebar'],
    // fallback aliases from older/derived configs
    ['pitch', 'inPitch'],
    ['clearHt', 'inClearHt'],
    ['width', 'inWidth'],
    ['footing', 'inFooting'],
    ['rebar_size', 'inRebar'],
    ['rebar', 'inRebar'],
    ['above_grade_ft', 'inAboveGrade'],
    ['above_grade', 'inAboveGrade'],
    ['above_grade_depth', 'inAboveGrade'],
    ['cut_allowance_in', 'inCutAllowance'],
    ['cut_allowance', 'inCutAllowance'],
    ['cut_allow', 'inCutAllowance'],
  ];

  for (const [cfgKey, inputId] of mappings) {
    const value = config[cfgKey];
    const inputEl = document.getElementById(inputId);
    if (inputEl && value !== undefined && value !== null) {
      inputEl.value = String(value);
      inputEl.dispatchEvent(new Event('input', { bubbles: true }));
      inputEl.dispatchEvent(new Event('change', { bubbles: true }));
    }
  }

  // Project info fields
  if (config.project_name) {
    const el = document.getElementById('inProject');
    if (el) { el.value = config.project_name; el.dispatchEvent(new Event('input', { bubbles: true })); }
  }
  if (config.customer_name || config.customer) {
    const el = document.getElementById('setCustomer');
    if (el) { el.value = config.customer_name || config.customer; el.dispatchEvent(new Event('input', { bubbles: true })); }
  }
  if (config.job_code) {
    const el = document.getElementById('inJobNo');
    if (el) { el.value = config.job_code; el.dispatchEvent(new Event('input', { bubbles: true })); }
  }
  if (config.drawn_by) {
    const el = document.getElementById('inDrawnBy');
    if (el) { el.value = config.drawn_by; el.dispatchEvent(new Event('input', { bubbles: true })); }
  }

  // Handle reinforced/non-reinforced toggle
  const reinforced = config.col_reinforced !== undefined ? config.col_reinforced : config.reinforced;
  if (reinforced !== undefined) {
    const isReinforced = reinforced === true || String(reinforced).toLowerCase() === 'true';
    // The drawing defaults to reinforced — only toggle if non-reinforced
    if (!isReinforced) {
      toggleReinforced();
    }
  }

  // Trigger full redraw after all fields are set
  if (typeof draw === 'function') draw();
}

// ═══════════════════════════════════════════════
// SAVE PDF TO PROJECT (via jsPDF + svg2pdf.js)
// ═══════════════════════════════════════════════
function savePdfToProject() {
  var btn = document.getElementById('btnSavePdf');
  var status = document.getElementById('savePdfStatus');
  var jobCode = (window.COLUMN_CONFIG && window.COLUMN_CONFIG.job_code) || '{{JOB_CODE}}';
  if (!jobCode || jobCode === 'null') {
    alert('No project job code \u2014 open this drawing from a project to save.');
    return;
  }
  btn.disabled = true;
  btn.textContent = 'Generating...';
  status.textContent = '';

  try {
    var svgEl = document.getElementById('svg');
    var vb = svgEl.viewBox.baseVal;
    var svgW = vb.width || 1100;
    var svgH = vb.height || 850;

    var pdf = new jspdf.jsPDF({
      orientation: 'landscape',
      unit: 'pt',
      format: [svgW, svgH]
    });

    svg2pdf.svg2pdf(svgEl, pdf, { x: 0, y: 0, width: svgW, height: svgH }).then(function() {
      var pdfData = pdf.output('arraybuffer');
      var blob = new Blob([pdfData], { type: 'application/pdf' });

      var formData = new FormData();
      formData.append('job_code', jobCode);
      formData.append('drawing_type', 'column');
      formData.append('source', 'interactive');
      formData.append('pdf_file', blob, jobCode + '_COLUMN_INTERACTIVE.pdf');

      fetch('/api/shop-drawings/save-interactive-pdf', {
        method: 'POST',
        body: formData
      })
      .then(function(r) { return r.json(); })
      .then(function(data) {
        if (data.ok) {
          btn.textContent = 'Saved!';
          btn.style.background = '#059669';
          status.textContent = 'PDF saved to project';
          status.style.color = '#10B981';
          setTimeout(function() {
            btn.textContent = 'Save PDF to Project';
            btn.disabled = false;
          }, 3000);
        } else {
          btn.textContent = 'Save PDF to Project';
          btn.disabled = false;
          status.textContent = 'Error: ' + (data.error || 'unknown');
          status.style.color = '#EF4444';
        }
      })
      .catch(function(err) {
        btn.textContent = 'Save PDF to Project';
        btn.disabled = false;
        status.textContent = 'Network error';
        status.style.color = '#EF4444';
      });
    }).catch(function(err) {
      btn.textContent = 'Save PDF to Project';
      btn.disabled = false;
      status.textContent = 'PDF render error: ' + err.message;
      status.style.color = '#EF4444';
    });
  } catch(err) {
    btn.textContent = 'Save PDF to Project';
    btn.disabled = false;
    status.textContent = 'Error: ' + err.message;
    status.style.color = '#EF4444';
  }
}
</script>
</body>
</html>
"""
