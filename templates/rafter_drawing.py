"""
TitanForge — Interactive Rafter Shop Drawing Template
=====================================================
Full-featured SVG-based rafter shop drawing served as an interactive page.
Pre-fills with project data via window.RAFTER_CONFIG injection.
Supports browser Print→PDF for clean shop-floor output.
"""

RAFTER_DRAWING_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TitanForge — Rafter Shop Drawing</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
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
  .top-bar .back-link:hover { background: #475569; color: #F1F5F9; }
  .top-bar .job-code-label { font-size: 0.85rem; color: #94A3B8; }
  .controls { display: flex; gap: 14px; align-items: center; flex-wrap: wrap; }
  .ctrl-group { display: flex; align-items: center; gap: 6px; }
  .ctrl-group label { font-size: 0.75rem; color: #94A3B8; white-space: nowrap; }
  .ctrl-group select, .ctrl-group input[type=number] {
    background: #334155; color: #F1F5F9; border: 1px solid #475569;
    border-radius: 5px; padding: 5px 8px; font-size: 0.8rem; width: 80px;
  }
  .toggle-switch { position: relative; display: inline-block; width: 36px; height: 18px; cursor: pointer; }
  .toggle-switch input { opacity: 0; width: 0; height: 0; }
  .toggle-slider { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: #475569; border-radius: 18px; transition: 0.25s; }
  .toggle-slider::before { content: ''; position: absolute; height: 14px; width: 14px; left: 2px; bottom: 2px; background: #94A3B8; border-radius: 50%; transition: 0.25s; }
  .toggle-switch input:checked + .toggle-slider { background: #F6AE2D; }
  .toggle-switch input:checked + .toggle-slider::before { transform: translateX(18px); background: #0F172A; }
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

  /* SVG drawing styles — EXACT match to column drawing */
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
  .rebar-solid { fill: #CC4400; fill-opacity: 0.4; stroke: #CC4400; stroke-width: 0.8; stroke-opacity: 0.7; }
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
  .clip-fill { fill: #C8D8E8; stroke: #1a1a1a; stroke-width: 0.8; }
  .conn-plate { fill: #B8B8B8; stroke: #1a1a1a; stroke-width: 1.2; }

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
  .warn-text { font: 700 8px Arial, sans-serif; fill: #CC0000; }

  /* Layout Edit Mode */
  [data-layout-id] { cursor: default; }
  .layout-mode [data-layout-id] { cursor: grab; }
  .layout-mode [data-layout-id]:hover { outline: 1.5px dashed #F6AE2D; outline-offset: 2px; }
  .layout-mode [data-layout-id].layout-selected { outline: 2px solid #F6AE2D; outline-offset: 2px; }
  .layout-mode [data-layout-id].layout-dragging { cursor: grabbing; opacity: 0.85; }
  .export-modal {
    display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6);
    z-index: 9999; justify-content: center; align-items: center;
  }
  .export-modal.show { display: flex; }
  .export-modal-content {
    background: #1E293B; border: 1px solid #475569; border-radius: 10px;
    padding: 20px; width: 600px; max-height: 80vh; display: flex; flex-direction: column; gap: 12px;
  }
  .export-modal-content h3 { color: #F6AE2D; margin: 0; }
  .export-modal-content textarea {
    background: #0F172A; color: #93C5FD; border: 1px solid #475569; border-radius: 6px;
    font: 12px 'Courier New', monospace; padding: 10px; height: 300px; resize: vertical;
  }
  .export-modal-content .modal-btns { display: flex; gap: 8px; justify-content: flex-end; }
  .export-modal-content .modal-btns button {
    padding: 6px 16px; border-radius: 5px; font-size: 0.8rem; cursor: pointer; border: none;
  }
  .btn-copy { background: #F6AE2D; color: #0F172A; font-weight: 700; }
  .btn-close-modal { background: #334155; color: #94A3B8; }

  /* Annotation styles */
  /* Piece selector tabs */
  .piece-tabs { display: flex; align-items: center; gap: 10px; padding: 6px 24px;
    background: #1E293B; border-bottom: 1px solid #334155; }
  .piece-tabs-label { color: #94A3B8; font-size: 0.75rem; font-weight: 600; letter-spacing: 0.05em; }
  .piece-tab { padding: 5px 16px; border-radius: 6px; border: 1px solid #475569; background: #334155;
    color: #CBD5E1; font-size: 0.8rem; font-weight: 600; cursor: pointer; transition: all 0.15s; }
  .piece-tab:hover { background: #475569; color: #F1F5F9; }
  .piece-tab.active { background: #0055AA; color: #FFF; border-color: #6CB4EE; }
  .splice-info { color: #F6AE2D; font-size: 0.7rem; margin-left: auto; }
  .splice-warn { color: #EF4444; font-weight: 600; }

  .drawing-sheet.add-weld-mode #svg { cursor: crosshair !important; }
  .drawing-sheet.add-weld-mode #svg * { cursor: crosshair !important; }

  /* Column Edit Mode — draggable P3 markers */
  .p3-drag-handle { cursor: ew-resize; }
  .p3-drag-handle:hover { filter: drop-shadow(0 0 4px rgba(246,174,45,0.7)); }
  .col-edit-mode .p3-drag-handle { cursor: ew-resize; }
  .p3-drag-ghost { stroke: #F6AE2D; stroke-width: 1; stroke-dasharray: 4,2; fill: rgba(246,174,45,0.08); pointer-events: none; }
  .col-pos-synced { background: #059669 !important; color: #ECFDF5 !important; transition: background 0.3s; }
  .ctrl-group input[type=text] {
    background: #334155; color: #F1F5F9; border: 1px solid #475569;
    border-radius: 5px; padding: 5px 8px; font-size: 0.8rem;
  }
  .anno-group { cursor: default; }
  .anno-mode .anno-group { cursor: grab; }
  .anno-group .anno-bg { fill: #FFFDE7; fill-opacity: 0; stroke: none; }
  .anno-mode .anno-group .anno-bg { fill-opacity: 0.7; stroke: #F6AE2D; stroke-width: 0.5; rx: 2; }
  .anno-mode .anno-group:hover .anno-bg { fill-opacity: 0.85; stroke: #F6AE2D; stroke-width: 1; }
  .anno-group.anno-selected .anno-bg { fill-opacity: 0.9; stroke: #E53E3E; stroke-width: 1.5; }
  .anno-group.anno-dragging { cursor: grabbing; opacity: 0.7; }
  .anno-hint { font: 600 6px Arial, sans-serif; fill: #E53E3E; }
  .anno-count-badge {
    background: #F6AE2D; color: #0F172A; font-size: 0.65rem; font-weight: 700;
    padding: 1px 5px; border-radius: 8px; margin-left: 4px;
  }

  .settings-panel { position: fixed; left: -380px; top: 0; bottom: 0; width: 360px;
    background: #1E293B; border-right: 2px solid #F6AE2D; z-index: 50;
    transition: left 0.3s; padding: 20px; overflow-y: auto; }
  .settings-panel.open { left: 0; }
  .settings-panel h2 { color: #F6AE2D; font-size: 1rem; margin-bottom: 12px; }
  .settings-panel label { display: block; color: #94A3B8; font-size: 0.75rem; margin-top: 10px; }
  .settings-panel input { width: 100%; background: #334155; color: #F1F5F9; border: 1px solid #475569;
    border-radius: 5px; padding: 6px 8px; font-size: 0.8rem; margin-top: 4px; }
  .settings-x { position: absolute; top: 10px; right: 12px; background: none; border: none; color: #94A3B8; font-size: 1.2rem; cursor: pointer; }

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

  /* Annotations */
  .anno-mode-btn { transition: all 0.2s; }
  .anno-mode-btn.active { background: #EF4444 !important; color: #FFF !important; border-color: #EF4444 !important; }

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
  .rotation-handle { cursor: grab; }
  .rotation-handle:hover { filter: brightness(1.3); }
  .label-interactive { cursor: move; }
  .label-interactive:hover { filter: drop-shadow(0 0 2px rgba(0,170,85,0.6)); }
  .label-interactive.selected { filter: drop-shadow(0 0 4px rgba(246,174,45,0.8)); }

  @media print {
    @page { size: landscape; margin: 0.25in; }
    .top-bar, .foot, .tip, .bom, .modal-overlay, .weld-editor, .settings-panel,
    .anno-count-badge, .piece-tabs { display: none !important; }
    html, body { margin: 0; padding: 0; background: #FFF; width: 100%; height: 100%; overflow: hidden; }
    .canvas-wrap { padding: 0; margin: 0; display: flex; align-items: center; justify-content: center;
                   width: 100%; height: 100%; }
    .drawing-sheet { box-shadow: none; width: 100%; height: auto; max-height: 100vh;
                     page-break-inside: avoid; break-inside: avoid; }
    .drawing-sheet svg { width: 100%; height: auto; max-height: 100vh; }
  }
</style>
<script>window.RAFTER_CONFIG = {{RAFTER_CONFIG_JSON}};</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/svg2pdf.js/2.2.3/svg2pdf.umd.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script>
// ── svg2pdf compatibility shim ──────────────────────────────
// svg2pdf.js v2.x registers as a jsPDF plugin (doc.svg method).
// If duplicate script loads clobber the registration, or if the
// old call-style svg2pdf.svg2pdf() is used, this shim fixes it.
(function() {
  // Re-register if doc.svg is missing (caused by duplicate jsPDF loads)
  if (window.jspdf && !window.jspdf.jsPDF.prototype.svg) {
    var s = document.createElement('script');
    s.src = 'https://cdn.jsdelivr.net/npm/svg2pdf.js@2.2.3/dist/svg2pdf.umd.min.js';
    document.head.appendChild(s);
  }
  // Create legacy-compatible global: svg2pdf.svg2pdf(el, doc, opts)
  if (typeof window.svg2pdf === 'undefined' || !window.svg2pdf.svg2pdf) {
    window.svg2pdf = window.svg2pdf || {};
    window.svg2pdf.svg2pdf = function(svgElement, pdfDoc, options) {
      if (typeof pdfDoc.svg === 'function') {
        return pdfDoc.svg(svgElement, options);
      }
      // Canvas fallback for SVG-to-PDF when plugin fails
      return new Promise(function(resolve, reject) {
        try {
          var serializer = new XMLSerializer();
          var svgString = serializer.serializeToString(svgElement);
          var canvas = document.createElement('canvas');
          var scale = 2;
          canvas.width = (options.width || 1100) * scale;
          canvas.height = (options.height || 850) * scale;
          var ctx = canvas.getContext('2d');
          ctx.fillStyle = '#FFFFFF';
          ctx.fillRect(0, 0, canvas.width, canvas.height);
          ctx.scale(scale, scale);
          var img = new Image();
          var blob = new Blob([svgString], {type:'image/svg+xml;charset=utf-8'});
          var url = URL.createObjectURL(blob);
          img.onload = function() {
            ctx.drawImage(img, 0, 0, options.width || 1100, options.height || 850);
            URL.revokeObjectURL(url);
            var imgData = canvas.toDataURL('image/png');
            pdfDoc.addImage(imgData, 'PNG', options.x||0, options.y||0,
              options.width||1100, options.height||850);
            resolve();
          };
          img.onerror = function() { URL.revokeObjectURL(url); reject(new Error('SVG render failed')); };
          img.src = url;
        } catch(e) { reject(e); }
      });
    };
  }
})();
</script>
</head>
<body>

<!-- TOP BAR -->
<div class="top-bar">
  <div style="display:flex;align-items:center;gap:12px;">
    <a class="back-link" href="/shop-drawings/{{JOB_CODE}}">Back</a>
    <h1>Rafter Shop Drawing</h1>
    <span class="job-code-label" id="jobLabel">RAFTER</span>
  </div>
  <div class="controls">
    <div class="ctrl-group">
      <label>Width (ft):</label>
      <input type="number" id="inputWidth" value="40" min="10" max="200" step="1">
    </div>
    <div class="ctrl-group">
      <label>Spacing (ft):</label>
      <input type="number" id="inputSpacing" value="5" min="2" max="12" step="0.5">
    </div>
    <div class="ctrl-group">
      <label>Overhang (ft):</label>
      <input type="number" id="inputOverhang" value="1" min="0" max="5" step="0.5">
    </div>
    <div class="ctrl-group">
      <label>Purlin:</label>
      <select id="inputPurlinType">
        <option value="Z" selected>Z</option>
        <option value="C">C</option>
      </select>
    </div>
    <div class="ctrl-group">
      <label><input type="checkbox" id="inputAngledPurlins"> Angled Purlins</label>
      <span id="angledInputs" style="display:none;">
        <input type="number" id="inputPurlinAngle" value="15" min="1" max="45" step="0.5" style="width:48px;" title="Purlin angle in degrees from perpendicular (0=square)">
        <label style="font-size:0.7rem;color:#94A3B8;">&deg;</label>
      </span>
    </div>
    <div class="ctrl-group">
      <label><input type="checkbox" id="inputBackWall"> Back Wall</label>
      <span id="backWallInputs" style="display:none;">
        <label style="font-size:0.7rem;color:#94A3B8;margin-left:4px;">Front Col (ft):</label>
        <input type="number" id="inputFrontCol" value="0" min="0" max="200" step="0.5" style="width:56px;" title="Front column position in feet from left end. 0 = auto (L/4).">
      </span>
    </div>
    <div class="ctrl-group">
      <label>Columns:</label>
      <select id="inputColMode" style="width:90px;">
        <option value="auto" selected>Auto</option>
        <option value="spacing">Spacing</option>
        <option value="manual">Manual</option>
      </select>
      <span id="colSpacingWrap" style="display:none;">
        <input type="number" id="inputColSpacing" value="25" min="5" max="100" step="0.5" style="width:56px;" title="Distance between columns in feet">
        <label style="font-size:0.7rem;color:#94A3B8;">ft apart</label>
      </span>
      <span id="colManualWrap" style="display:none;">
        <label style="font-size:0.7rem;color:#94A3B8;">Qty:</label>
        <input type="number" id="inputP3Count" value="1" min="1" max="10" step="1" style="width:48px;" title="Number of columns">
      </span>
    </div>
    <div class="ctrl-group">
      <label>Column Pos (ft):</label>
      <input type="text" id="inputColumnPositions" value="" style="width:160px;" placeholder="auto-filled or type positions" title="Comma-separated column positions in feet from left end.">
    </div>
    <div class="ctrl-group" id="spliceGroup" style="display:none;">
      <label>Splice (ft from L):</label>
      <input type="number" id="inputSpliceLocation" value="0" min="0" max="200" step="0.5" title="Distance from left end to splice">
    </div>
    <div class="ctrl-group">
      <label>Rebar:</label>
      <select id="inputRebarSize">
        <option value="#5">#5 (0.625")</option>
        <option value="#6">#6 (0.750")</option>
        <option value="#7">#7 (0.875")</option>
        <option value="#8">#8 (1.000")</option>
        <option value="#9" selected>#9 (1.128")</option>
        <option value="#10">#10 (1.270")</option>
        <option value="#11">#11 (1.410")</option>
      </select>
    </div>
    <div class="ctrl-group">
      <label>Rebar Length (ft):</label>
      <input type="number" id="inputMaxStick" value="20" min="4" max="40" step="1" title="Max rebar stick length in feet">
    </div>
    <div class="ctrl-group">
      <label>Gap from End to Rebar (ft):</label>
      <input type="number" id="inputEndGap" value="5" min="0" max="20" step="0.5" title="Distance from each rafter end before rebar starts">
    </div>
    <div class="ctrl-group">
      <button class="toggle-btn active" id="btnReinforced">Reinforced</button>
      <button class="toggle-btn" id="btnNonReinforced">Non-Reinforced</button>
    </div>
    <button class="btn-gold" onclick="document.getElementById('bomPanel').classList.toggle('open')">BOM</button>
    <button class="btn-gold" style="background:#475569;color:#F1F5F9;" onclick="window.print()">Print</button>
    <button class="btn-gold" id="btnSavePdf" style="background:#059669;color:#FFF;" onclick="savePdfToProject()" title="Generate PDF and save to project shop drawings">Save PDF to Project</button>
    <span id="savePdfStatus" style="font-size:0.7rem;color:#94A3B8;"></span>
    <button class="btn-gold" style="background:#334155;color:#F6AE2D;border:1px solid #F6AE2D;" onclick="resetZoom()">Reset Zoom</button>
    <button class="btn-gold" style="background:#334155;color:#94A3B8;border:1px solid #475569;font-size:0.9rem;" onclick="undo()" title="Undo (Cmd+Z)">&#8617;</button>
    <button class="btn-gold" style="background:#334155;color:#94A3B8;border:1px solid #475569;font-size:0.9rem;" onclick="redo()" title="Redo (Cmd+Shift+Z)">&#8618;</button>
    <button class="btn-gold" style="background:#334155;color:#F6AE2D;border:1px solid #475569;" onclick="document.getElementById('settingsPanel').classList.toggle('open')">&#9881; Settings</button>
    <span id="checkBadge" class="unchecked-badge" onclick="startApproval()">&#10007; UNCHECKED</span>
    <button class="btn-gold anno-mode-btn" id="btnAnnotate" onclick="toggleAnnotateMode()">&#128221; Annotate</button>
    <button class="btn-gold" id="btnWeldEdit" style="background:#0055AA;color:#FFF;" onclick="toggleWeldEditMode()">&#128295; Edit Welds</button>
    <button class="btn-gold" id="btnWeldReset" style="background:#7C2D12;color:#FDBA74;display:none;" onclick="resetAllWeldOverrides()">&#8634; Reset Welds</button>
    <button class="btn-gold" id="btnAddWeld" style="background:#059669;color:#ECFDF5;display:none;" onclick="toggleAddWeldMode()">&#10010; Add Weld</button>
    <button class="btn-gold" id="btnDeleteWeld" style="background:#DC2626;color:#FEE2E2;display:none;" onclick="deleteSelectedWeld()">&#128465; Delete Weld</button>
    <button class="btn-gold" id="btnExportWelds" style="background:#7C3AED;color:#DDD6FE;display:none;" onclick="exportWelds()">&#128230; Export Welds</button>
    <button class="btn-gold" id="btnColEdit" style="background:#7C3AED;color:#DDD6FE;" onclick="toggleColumnEditMode()">&#9881; Edit Columns</button>
    <button class="btn-gold" id="btnLayoutEdit" style="background:#065F46;color:#6EE7B7;" onclick="toggleLayoutMode()">&#9998; Layout Edit</button>
    <button class="btn-gold" id="btnExportLayout" style="background:#7C3AED;color:#DDD6FE;display:none;" onclick="exportLayout()">&#128230; Export Moves</button>
    <button class="btn-gold" id="btnResetLayout" style="background:#7C2D12;color:#FDBA74;display:none;" onclick="resetLayoutOverrides()">&#8634; Reset Layout</button>
  </div>
</div>

<!-- EXPORT LAYOUT MODAL -->
<div class="export-modal" id="exportModal">
  <div class="export-modal-content">
    <h3>Layout Moves — Copy &amp; Paste to Claude</h3>
    <p style="color:#94A3B8;font-size:0.8rem;">These are all the element moves you made. Copy this text and paste it to me so I can make the changes permanent.</p>
    <textarea id="exportText" readonly></textarea>
    <div class="modal-btns">
      <button class="btn-copy" onclick="copyExport()">&#128203; Copy to Clipboard</button>
      <button class="btn-close-modal" onclick="closeExportModal()">Close</button>
    </div>
  </div>
</div>


<!-- APPROVAL MODAL -->
<div class="modal-overlay" id="approvalModal">
  <div class="modal-box">
    <h3>Approve Drawing</h3>
    <p>Approver name:</p>
    <input id="approverName" type="text" style="width:100%;padding:8px;background:#334155;color:#F1F5F9;border:1px solid #475569;border-radius:4px;margin-bottom:12px;">
    <p class="warn">If something is incorrect, it is on YOU. This action creates a permanent record and can only be undone by creating a new revision.</p>
    <div class="modal-btns">
      <button class="ok" onclick="confirmApproval()">I Accept Responsibility</button>
      <button class="cancel" onclick="cancelApproval()">Cancel</button>
    </div>
  </div>
</div>

<!-- DRAWING CANVAS -->
<!-- PIECE SELECTOR TABS (visible only for spliced rafters) -->
<div class="piece-tabs" id="pieceTabs" style="display:none;">
  <span class="piece-tabs-label">PIECES:</span>
  <div id="pieceTabBtns"></div>
  <span class="splice-info" id="spliceInfo"></span>
</div>

<!-- SPAN DIAGRAM — auto-calc visualization -->
<div id="spanDiagramWrap" style="margin:0 auto;max-width:1100px;padding:4px 12px 0;background:#0F172A;">
  <svg id="spanSvg" viewBox="0 0 900 62" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:62px;display:block;"></svg>
</div>

<div class="canvas-wrap">
  <div class="drawing-sheet">
    <svg id="svg" viewBox="0 0 1100 850" xmlns="http://www.w3.org/2000/svg"></svg>
  </div>
</div>

<!-- FOOTER -->
<div class="foot">
  <div>Weight: <span class="s" id="fWt">--</span></div>
  <div>Rafter Length: <span class="s" id="fLen">--</span></div>
  <div>P1 Count: <span class="s" id="fP1">--</span></div>
  <div>Rebar Sticks: <span class="s" id="fRebar">--</span></div>
  <div>Purlin Type: <span class="s" id="fPurlin">Z</span></div>
  <div>Back Wall: <span class="s" id="fBackWall">No</span></div>
  <div>P3 Count: <span class="s" id="fP3">1</span></div>
</div>

<!-- BOM SIDE PANEL -->
<div class="bom" id="bomPanel">
  <button class="bom-x" onclick="this.parentElement.classList.remove('open')">&#10005;</button>
  <h2>Bill of Materials (per rafter)</h2>
  <table>
    <thead>
      <tr><th>Mk</th><th>Qty</th><th>Description</th><th>Size</th><th>Material</th><th>Weight</th></tr>
    </thead>
    <tbody id="bomTB"></tbody>
  </table>
  <div style="margin-top:12px;padding:8px;background:#334155;border-radius:6px;text-align:right;">
    <span style="color:#94A3B8;">Total:</span> <strong style="color:#F6AE2D;" id="bomTotal">--</strong>
  </div>
</div>

<!-- TOOLTIP -->
<div class="tip" id="tip"></div>

<!-- WELD EDITOR -->
<div class="weld-editor" id="weldEditor">
  <h3>Weld Editor <button class="we-close" onclick="closeWeldEditor()">&#10005;</button></h3>
  <div class="we-grid">
    <label>Size<input type="text" id="weSize" value="3/16"></label>
    <label>WPS<input type="text" id="weWps" value=""></label>
    <label>Stitch<input type="text" id="weStitch" value=""></label>
    <label>Ref Dir<select id="weRefDir"><option value="right">Right</option><option value="left">Left</option></select></label>
    <label>Rotation<input type="range" id="weRotation" min="-180" max="180" value="0"></label>
    <label></label>
    <label><input type="checkbox" id="weAllAround"> All-Around</label>
    <label><input type="checkbox" id="weBothSides"> Both Sides</label>
  </div>
  <div class="we-actions">
    <button style="background:#475569;color:#F1F5F9;" onclick="resetSelectedWeld()">Reset</button>
    <button class="we-apply-btn" style="background:#0055AA;color:#FFF;" onclick="applyWeldEdit()">&#10003; Apply</button>
  </div>
</div>

<!-- SETTINGS PANEL -->
<div class="settings-panel" id="settingsPanel">
  <button class="settings-x" onclick="this.parentElement.classList.remove('open')">&#10005;</button>
  <h2>Project Settings</h2>
  <label>Project Name
    <input type="text" id="setProjectName" value="RAFTER PROJECT" onchange="draw()">
  </label>
  <label>Customer
    <input type="text" id="setCustomer" value="" placeholder="Customer Name" onchange="draw()">
  </label>
  <label>Job Number
    <input type="text" id="setJobNumber" value="JOB-2026-001" onchange="draw()">
  </label>
  <label>Drawn By
    <input type="text" id="setDrawnBy" value="AUTO" onchange="draw()">
  </label>
  <label>Rafter Mark
    <input type="text" id="setRafterMark" value="B1" onchange="draw()">
  </label>
  <label>Drawing Number
    <input type="text" id="setDrawingNum" value="SD-B1-001" onchange="draw()">
  </label>
  <label>Surface Prep
    <input type="text" id="setSurfPrep" value="SSPC-SP2" onchange="draw()">
  </label>
</div>

<script>
// ── Server-injected project config ──
// TitanForge injects RAFTER_CONFIG with project data when serving this page.
// If not present (standalone mode), defaults are used from the input fields.
window.RAFTER_CONFIG = window.RAFTER_CONFIG || null;

function applyServerConfig() {
  var cfg = window.RAFTER_CONFIG;
  if (!cfg) return;  // standalone mode — use input defaults

  // Pre-fill inputs from server config
  if (cfg.width_ft) document.getElementById('inputWidth').value = cfg.width_ft;
  if (cfg.purlin_spacing_ft) document.getElementById('inputSpacing').value = cfg.purlin_spacing_ft;
  if (cfg.overhang_ft !== undefined) document.getElementById('inputOverhang').value = cfg.overhang_ft;
  if (cfg.purlin_type) document.getElementById('inputPurlinType').value = cfg.purlin_type;
  if (cfg.angled_purlins) {
    document.getElementById('inputAngledPurlins').checked = true;
    document.getElementById('angledInputs').style.display = '';
  }
  if (cfg.purlin_angle_deg) document.getElementById('inputPurlinAngle').value = cfg.purlin_angle_deg;
  if (cfg.back_wall) {
    document.getElementById('inputBackWall').checked = true;
    document.getElementById('backWallInputs').style.display = '';
  }
  if (cfg.front_col_position_ft) document.getElementById('inputFrontCol').value = cfg.front_col_position_ft;
  if (cfg.column_mode) {
    document.getElementById('inputColMode').value = cfg.column_mode;
    updateColModeUI();
  }
  if (cfg.column_spacing_ft) document.getElementById('inputColSpacing').value = cfg.column_spacing_ft;
  if (cfg.column_count_manual) {
    var el = document.getElementById('inputP3Count');
    if (el) el.value = cfg.column_count_manual;
  }
  if (cfg.column_positions_manual) {
    var el = document.getElementById('inputColumnPositions');
    if (el) el.value = cfg.column_positions_manual;
  }
  if (cfg.rebar_size) document.getElementById('inputRebarSize').value = cfg.rebar_size;
  if (cfg.rebar_max_stick_ft) document.getElementById('inputMaxStick').value = cfg.rebar_max_stick_ft;
  if (cfg.rebar_end_gap_ft) document.getElementById('inputEndGap').value = cfg.rebar_end_gap_ft;
  if (cfg.splice_location_ft) {
    var el = document.getElementById('inputSpliceLocation');
    if (el) el.value = cfg.splice_location_ft;
  }
  // Project info
  if (cfg.project_name) {
    var el = document.getElementById('setProjectName');
    if (el) el.value = cfg.project_name;
  }
  if (cfg.customer || cfg.customer_name) {
    var el = document.getElementById('setCustomer');
    if (el) el.value = cfg.customer || cfg.customer_name;
  }
  if (cfg.job_code) {
    var el = document.getElementById('setJobNumber');
    if (el) el.value = cfg.job_code;
    var lbl = document.getElementById('jobLabel');
    if (lbl) lbl.textContent = cfg.job_code;
  }
  if (cfg.rafter_mark) {
    var el = document.getElementById('setRafterMark');
    if (el) el.value = cfg.rafter_mark;
  }
}

// ═══════════════════════════════════════════════
// SVG HELPER FUNCTIONS — EXACT from column drawing
// ═══════════════════════════════════════════════
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

// Format inches to ft-in with 1/8 fractions
// Format scale for print: given px/real-inch scale factor, compute "1" = X'-Y""
// SVG sheet is 1100px wide; on 11" landscape paper, 1 paper inch = 100px
function fmtScale(pxPerRealIn) {
  var paperInchPx = 100;  // 1100px SVG / 11" paper width
  var realInPerPaperIn = paperInchPx / pxPerRealIn;  // how many real inches fit in 1 paper inch
  var realFt = realInPerPaperIn / 12;
  // Round to nearest 0.5'
  var rounded = Math.round(realFt * 2) / 2;
  if (rounded < 1) {
    // Show in inches for detail views
    var ri = Math.round(realInPerPaperIn);
    return '1" = ' + ri + '"';
  }
  // Show in feet
  var ft = Math.floor(rounded);
  var frac = rounded - ft;
  if (frac >= 0.4) return '1" = ' + ft + "'-6\"";
  return '1" = ' + ft + "'-0\"";
}

function fmtFtIn(inches) {
  if (inches < 0) inches = 0;
  const ft = Math.floor(inches / 12);
  let inc = inches - ft * 12;
  const e8 = Math.round(inc * 8) / 8;
  if (e8 >= 12) return (ft+1) + "'-0\"";
  if (e8 === Math.floor(e8)) return ft + "'-" + Math.floor(e8) + "\"";
  const w = Math.floor(e8);
  let n = Math.round((e8 - w) * 8), dd = 8;
  while (n%2===0 && dd>1) { n/=2; dd/=2; }
  return w ? ft + "'-" + w + " " + n + "/" + dd + "\"" : ft + "'-" + n + "/" + dd + "\"";
}

// Horizontal dimension line
function dimH(svg, x1, x2, y, off, label) {
  const dy = y + off;
  svg.appendChild($l(x1,y,x1,dy+(off>0?-2:2),'dim'));
  svg.appendChild($l(x2,y,x2,dy+(off>0?-2:2),'dim'));
  svg.appendChild($l(x1,dy,x2,dy,'dim'));
  // tick marks
  svg.appendChild($l(x1-1.5,dy-1.5,x1+1.5,dy+1.5,'dim'));
  svg.appendChild($l(x2-1.5,dy-1.5,x2+1.5,dy+1.5,'dim'));
  svg.appendChild($t((x1+x2)/2, dy-3, label, 'dimtxt', 'middle'));
}

// Vertical dimension line
function dimV(svg, x, y1, y2, off, label) {
  const dx = x + off;
  svg.appendChild($l(x,y1,dx+(off>0?-2:2),y1,'dim'));
  svg.appendChild($l(x,y2,dx+(off>0?-2:2),y2,'dim'));
  svg.appendChild($l(dx,y1,dx,y2,'dim'));
  svg.appendChild($l(dx-1.5,y1-1.5,dx+1.5,y1+1.5,'dim'));
  svg.appendChild($l(dx-1.5,y2-1.5,dx+1.5,y2+1.5,'dim'));
  const t = $t(dx+(off>0?4:-4), (y1+y2)/2+3, label, 'dimtxt', 'middle');
  t.setAttribute('transform', 'rotate(-90,'+(dx+(off>0?4:-4))+','+((y1+y2)/2+3)+')');
  svg.appendChild(t);
}

// Vertical dimension line — rebar colored
function dimVRebar(svg, x, y1, y2, off, label) {
  const dx = x + off;
  svg.appendChild($l(x,y1,dx+(off>0?-2:2),y1,'rebar-dim'));
  svg.appendChild($l(x,y2,dx+(off>0?-2:2),y2,'rebar-dim'));
  svg.appendChild($l(dx,y1,dx,y2,'rebar-dim'));
  svg.appendChild($l(dx-1.5,y1-1.5,dx+1.5,y1+1.5,'rebar-dim'));
  svg.appendChild($l(dx-1.5,y2-1.5,dx+1.5,y2+1.5,'rebar-dim'));
  const t = $t(dx+(off>0?4:-4), (y1+y2)/2+3, label, 'rebar-dimtxt', 'middle');
  t.setAttribute('transform', 'rotate(-90,'+(dx+(off>0?4:-4))+','+((y1+y2)/2+3)+')');
  svg.appendChild(t);
}

// Horizontal dimension — rebar colored
function dimHRebar(svg, x1, x2, y, off, label) {
  const dy = y + off;
  svg.appendChild($l(x1,y,x1,dy+(off>0?-2:2),'rebar-dim'));
  svg.appendChild($l(x2,y,x2,dy+(off>0?-2:2),'rebar-dim'));
  svg.appendChild($l(x1,dy,x2,dy,'rebar-dim'));
  svg.appendChild($l(x1-1.5,dy-1.5,x1+1.5,dy+1.5,'rebar-dim'));
  svg.appendChild($l(x2-1.5,dy-1.5,x2+1.5,dy+1.5,'rebar-dim'));
  svg.appendChild($t((x1+x2)/2, dy-3, label, 'rebar-dimtxt', 'middle'));
}

// ═══════════════════════════════════════════════
// AWS WELD SYMBOL — EXACT from column drawing
// ═══════════════════════════════════════════════
function awsWeld(svg, ax, ay, routeX, routeY, size, opts, weldId) {
  opts = opts || {};
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
  const gClass = weldEditMode ? 'weld-group weld-group-interactive' + (isSelected ? ' selected' : '') : 'weld-group';
  const g = $e('g', {class: gClass});
  if (weldId) g.setAttribute('data-weld-id', weldId);

  const filletLeg = 8;
  const refLineLen = 50;
  const arrHead = 4;
  const refDir = finalRefDir === 'left' ? -1 : 1;

  if (rotation !== 0) {
    g.setAttribute('transform', 'rotate('+rotation+', '+finalRouteX+', '+finalRouteY+')');
  }

  // Leader line: arrow point → knee → route point
  const kneeX = finalRouteX;
  const kneeY = ay;
  g.appendChild($l(ax, ay, kneeX, kneeY, 'weld-leader'));
  g.appendChild($l(kneeX, kneeY, finalRouteX, finalRouteY, 'weld-leader'));

  // Arrowhead
  const adx = kneeX - ax, ady = kneeY - ay;
  const aDist = Math.sqrt(adx*adx + ady*ady) || 1;
  const aUx = adx / aDist, aUy = ady / aDist;
  const aPx = -aUy, aPy = aUx;
  g.appendChild($p('M '+ax+' '+ay+' L '+(ax + aUx*arrHead + aPx*arrHead*0.4)+' '+(ay + aUy*arrHead + aPy*arrHead*0.4)+' L '+(ax + aUx*arrHead - aPx*arrHead*0.4)+' '+(ay + aUy*arrHead - aPy*arrHead*0.4)+' Z', 'weld-arrow'));

  // Reference line
  const refEndX = finalRouteX + refDir * refLineLen;
  g.appendChild($l(finalRouteX, finalRouteY, refEndX, finalRouteY, 'weld-ref'));

  // Both sides dashed line
  if (finalBothSides) {
    const dashLine = $l(finalRouteX, finalRouteY + 5, refEndX, finalRouteY + 5, 'weld-ref');
    dashLine.setAttribute('stroke-dasharray', '3,2');
    g.appendChild(dashLine);
  }

  // All-around circle
  if (finalAllAround) g.appendChild($c(finalRouteX, finalRouteY, 3.5, 'weld-circ'));

  // Fillet weld symbol (triangle)
  const symX = finalRouteX + refDir * 5;
  g.appendChild($p('M '+symX+' '+finalRouteY+' L '+symX+' '+(finalRouteY + filletLeg)+' L '+(symX + refDir * filletLeg)+' '+finalRouteY+' Z', 'weld-sym'));

  // Size text
  if (finalSize) g.appendChild($t(symX - refDir * 2, finalRouteY + filletLeg + 9, finalSize+'"', 'weld-txt'));
  // Stitch text
  if (finalStitch) g.appendChild($t(symX + refDir * (filletLeg + 6), finalRouteY + filletLeg + 9, finalStitch, 'weld-txt'));

  // WPS tail
  if (finalWps) {
    const tx = refEndX;
    g.appendChild($l(tx, finalRouteY, tx + refDir * 6, finalRouteY - 4, 'weld-tail'));
    g.appendChild($l(tx, finalRouteY, tx + refDir * 6, finalRouteY + 4, 'weld-tail'));
    g.appendChild($t(tx + refDir * 10, finalRouteY + 3, finalWps, 'weld-txt'));
  }

  // Interactive hit area in edit mode
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
  }

  svg.appendChild(g);
  return g;
}

// ═══════════════════════════════════════════════
// DRAGGABLE LABEL — from column drawing
// ═══════════════════════════════════════════════
function dlabel(x, y, id, buildFn) {
  const ov = labelOverrides[id] || {};
  const ox = x + (ov.dx || 0);
  const oy = y + (ov.dy || 0);
  const cls = weldEditMode ? 'label-interactive' : '';
  const g = $e('g', { class: cls, 'data-label-id': id, transform: 'translate('+ox+', '+oy+')' });
  buildFn(g);
  if (weldEditMode) {
    const hit = $e('rect', { x: -2, y: -12, width: 80, height: 16,
      fill: 'transparent', stroke: 'none', rx: 2 });
    g.insertBefore(hit, g.firstChild);
  }
  const svg = document.getElementById('svg');
  svg.appendChild(g);
  return g;
}

// ═══════════════════════════════════════════════
// STATE
// ═══════════════════════════════════════════════
let reinforced = true;
let weldEditMode = false;
let selectedWeldId = null;
let weldOverrides = {
  "ev-p1-weld":    { dx: 37.1, dy: -5.1 },
  "ev-cee-l":      { dx: 164.5, dy: -9 },
  "ev-p2-l-weld":  { dx: 63.3, dy: 64.3 },
  "ev-p2-r-weld":  { dx: 17.9, dy: 71.2 }
};
let labelOverrides = {};
let layoutOverrides = {
  "notes-block":  { dx: 282.7, dy: 94.1 },
  "top-view":     { dx: 212.2, dy: 9.5 },
  "bottom-view":  { dx: 212.9, dy: 34.5 },
  "side-view":    { dx: 339.3, dy: 199.2 },
  "bom-table":    { dx: 12.8,  dy: -440.9 },
  "section-aa":   { dx: 29.7,  dy: 16.7 },
  "detail-1":     { dx: 64.2,  dy: 47.6 },
  "detail-2":     { dx: 32.1,  dy: -26.2 },
  "detail-3":     { dx: -14.5, dy: 6.7 },
  "detail-4":     { dx: 243.2, dy: 46.7 },
  "detail-5":     { dx: 435, dy: -87 }
};
let layoutEditMode = false;
let selectedLayoutId = null;
let undoStack = [];
let redoStack = [];
let annotateMode = false;
let annotations = [];
let selectedAnnotation = null;  // index into annotations[]
let currentWeldDefs = [];
let customWelds = [];       // user-added welds [{id, anchorIn, anchorVIn, routeDx, routeDy, size, opts}]
let deletedWelds = [];      // IDs of built-in welds that have been deleted
let addWeldMode = false;    // true when placing a new weld
let activePiece = 0;        // 0-indexed piece selector (0 = full rafter or piece 1)
let columnEditMode = false; // true when dragging P3 markers on elevation

const drawingState = {
  checked: false,
  checkedBy: '',
  revision: 0,
  history: [
    { rev: 0, date: new Date().toLocaleDateString(), desc: 'FOR FABRICATION', by: '' },
  ],
};

// ═══════════════════════════════════════════════
// PARAMS & CALC
// ═══════════════════════════════════════════════
function getParams() {
  var colMode = document.getElementById('inputColMode').value;  // 'auto', 'spacing', 'manual'
  var p3Input = parseInt(document.getElementById('inputP3Count').value) || 1;
  var colSpacing = parseFloat(document.getElementById('inputColSpacing').value) || 25;
  var backWall = document.getElementById('inputBackWall').checked;
  var frontColFt = parseFloat(document.getElementById('inputFrontCol').value) || 0;  // 0 = auto (L/4)
  var p3CountOverride = colMode === 'manual' ? p3Input : 0;  // 0 = auto or spacing
  var spliceLocationFt = parseFloat(document.getElementById('inputSpliceLocation').value) || 0;

  // Parse user-specified column positions (comma-separated feet from left end)
  var colPosStr = (document.getElementById('inputColumnPositions').value || '').trim();
  var userColumnPositionsFt = [];
  if (colPosStr.length > 0) {
    colPosStr.split(',').forEach(function(s) {
      var v = parseFloat(s.trim());
      if (!isNaN(v) && v > 0) userColumnPositionsFt.push(v);
    });
    userColumnPositionsFt.sort(function(a, b) { return a - b; });
  }

  return {
    width: parseFloat(document.getElementById('inputWidth').value) || 40,
    spacing: parseFloat(document.getElementById('inputSpacing').value) || 5,
    overhang: parseFloat(document.getElementById('inputOverhang').value) || 1,
    purlinType: document.getElementById('inputPurlinType').value || 'Z',
    angledPurlins: document.getElementById('inputAngledPurlins').checked,
    purlinAngle: parseFloat(document.getElementById('inputPurlinAngle').value) || 0,
    backWall: backWall,
    frontColFt: frontColFt,
    colMode: colMode,
    colSpacing: colSpacing,
    reinforced: reinforced,
    rebarSize: document.getElementById('inputRebarSize').value || '#9',
    maxStickFt: parseFloat(document.getElementById('inputMaxStick').value) || 20,
    endGapFt: parseFloat(document.getElementById('inputEndGap').value) || 5,
    p3CountOverride: p3CountOverride,
    spliceLocationFt: spliceLocationFt,
    userColumnPositionsFt: userColumnPositionsFt,
  };
}

function calc(p) {
  const zReduction = p.purlinType === 'Z' ? 7 : 0;
  // Back wall: no overhang on right (back) side
  var overhangCount = p.backWall ? 1 : 2;
  const totalCutLengthIn = p.width * 12 - overhangCount * p.overhang * 12 - zReduction + 0.375;
  const totalCutLengthFt = totalCutLengthIn / 12;

  // ── Column count & positions ──
  // Three modes: auto (60' rule), spacing (user-defined gap), manual (user-defined count)
  // Auto columns: building width ≤45' = 1 column, >45' = at least 2, then more per 60' max span
  var autoP3 = p.width <= 45 ? 1 : Math.max(2, Math.ceil(p.width / 60));
  var p3Count, p3Positions = [];

  if (p.userColumnPositionsFt && p.userColumnPositionsFt.length > 0) {
    // User typed explicit positions — always takes priority, but clamp to valid range
    p.userColumnPositionsFt.forEach(function(ftVal) {
      var posIn = ftVal * 12;
      if (posIn > 0 && posIn < totalCutLengthIn) {
        posIn = Math.max(13, Math.min(totalCutLengthIn - 13, posIn));  // P3 can't overhang
        p3Positions.push(posIn);
      }
    });
    p3Count = p3Positions.length;
  } else if (p.backWall) {
    // ── BACK WALL override — applies in any mode ──
    // Back column fixed at 19" from right end
    var backColIn = totalCutLengthIn - 19;
    // Front column: user-specified or default to L/4
    var frontColIn = (p.frontColFt > 0) ? p.frontColFt * 12 : totalCutLengthIn / 4;
    if (frontColIn >= backColIn) frontColIn = backColIn / 2;  // safety

    // Determine count — back wall ALWAYS needs at least 2 (front + back)
    if (p.colMode === 'spacing') {
      var spacingIn = p.colSpacing * 12;
      p3Count = 2;  // front + back minimum
      var span = backColIn - frontColIn;
      if (span > spacingIn) {
        var innerCols = Math.floor(span / spacingIn);
        p3Count = innerCols + 2;
      }
    } else if (p.colMode === 'manual') {
      p3Count = Math.max(2, p.p3CountOverride);
    } else {
      p3Count = Math.max(2, autoP3);
    }

    // Place columns: front, evenly between, back
    p3Positions.push(frontColIn);
    if (p3Count > 2) {
      var innerZone = backColIn - frontColIn;
      var innerCount = p3Count - 2;
      for (var i = 0; i < innerCount; i++) {
        p3Positions.push(frontColIn + innerZone * (i + 1) / (innerCount + 1));
      }
    }
    p3Positions.push(backColIn);
  } else if (p.colMode === 'spacing') {
    // ── SPACING mode — centered columns ──
    var spacingIn = p.colSpacing * 12;
    p3Count = Math.max(1, Math.floor(totalCutLengthIn / spacingIn));
    // Center the column group
    var totalSpan = (p3Count - 1) * spacingIn;
    var startIn = (totalCutLengthIn - totalSpan) / 2;
    for (var i = 0; i < p3Count; i++) {
      p3Positions.push(startIn + i * spacingIn);
    }
  } else if (p.colMode === 'manual') {
    // ── MANUAL mode — quarter-point placement ──
    p3Count = Math.max(1, p.p3CountOverride);
    if (p3Count === 1) {
      p3Positions = [totalCutLengthIn / 2];
    } else {
      var qIn = totalCutLengthIn / 4;
      p3Positions.push(qIn);
      if (p3Count > 2) {
        var midZone = totalCutLengthIn / 2;
        var innerCount = p3Count - 2;
        for (var i = 0; i < innerCount; i++) {
          p3Positions.push(qIn + midZone * (i + 1) / (innerCount + 1));
        }
      }
      p3Positions.push(totalCutLengthIn - qIn);
    }
  } else {
    // ── AUTO mode — 60' rule, quarter-point placement ──
    p3Count = autoP3;
    if (p3Count === 1) {
      p3Positions = [totalCutLengthIn / 2];
    } else {
      var qIn = totalCutLengthIn / 4;
      p3Positions.push(qIn);
      if (p3Count > 2) {
        var midZone = totalCutLengthIn / 2;
        var innerCount = p3Count - 2;
        for (var i = 0; i < innerCount; i++) {
          p3Positions.push(qIn + midZone * (i + 1) / (innerCount + 1));
        }
      }
      p3Positions.push(totalCutLengthIn - qIn);
    }
  }

  // ── P3 overhang constraint: P3 is 26" long, center must be ≥13" from each rafter end ──
  var p3HalfLen = 13;  // half of 26" P3 plate
  for (var pi = 0; pi < p3Positions.length; pi++) {
    if (p3Positions[pi] < p3HalfLen) p3Positions[pi] = p3HalfLen;
    if (p3Positions[pi] > totalCutLengthIn - p3HalfLen) p3Positions[pi] = totalCutLengthIn - p3HalfLen;
  }

  // ── Splice logic ──
  var needsSplice = totalCutLengthFt > 53;
  var spliceCount = totalCutLengthFt > 106 ? 2 : (needsSplice ? 1 : 0);
  var pieceCount = spliceCount + 1;

  // Splice positions (inches from left end)
  var splicePositions = [];
  var spliceWarnings = [];
  if (needsSplice) {
    if (p.spliceLocationFt > 0 && p.spliceLocationFt < totalCutLengthFt) {
      splicePositions.push(p.spliceLocationFt * 12);
    } else {
      // Default: midpoint for 1 splice, thirds for 2
      if (spliceCount === 1) {
        splicePositions.push(totalCutLengthIn / 2);
      } else {
        splicePositions.push(totalCutLengthIn / 3);
        splicePositions.push(totalCutLengthIn * 2 / 3);
      }
    }

    // ── Splice-on-P3 constraint: splice cannot land within ±13" of a P3 center ──
    // If it does, nudge the splice to just outside the P3 plate (13" + 1" clearance)
    var spliceP3Clear = p3HalfLen + 1;  // 14" clearance from P3 center
    splicePositions.forEach(function(sp, si) {
      p3Positions.forEach(function(pp) {
        var dist = sp - pp;
        if (Math.abs(dist) < spliceP3Clear) {
          // Nudge splice away from P3 — move in the direction of the larger remaining span
          var nudgeDir = (sp < totalCutLengthIn / 2) ? 1 : -1;  // nudge toward center if on left half
          splicePositions[si] = pp + nudgeDir * spliceP3Clear;
          spliceWarnings.push('Splice ' + (si+1) + ' nudged away from P3 (was on plate)');
        }
      });
    });

    // Validate each splice
    splicePositions.forEach(function(sp, si) {
      // Must be within 10' of a P3
      var nearestP3Dist = Infinity;
      p3Positions.forEach(function(pp) { nearestP3Dist = Math.min(nearestP3Dist, Math.abs(sp - pp)); });
      if (nearestP3Dist / 12 > 10) spliceWarnings.push('Splice ' + (si+1) + ' is ' + Math.round(nearestP3Dist/12) + '\' from nearest P3 (max 10\')');
    });
  }

  // ── End plate type: P2 (standard) or P6 (angled purlins) ──
  var endPlateType = p.angledPurlins ? 'p6' : 'p2';

  // ── Angled purlin geometry ──
  var angleRad = p.angledPurlins ? (p.purlinAngle * Math.PI / 180) : 0;
  var p1ClipWidth = 6;  // P1 clip is 6" wide
  // Footprint of angled P1 along rafter centerline
  var p1FootprintIn = p.angledPurlins ? (0.5 + p1ClipWidth * Math.sin(angleRad)) : 0;
  // The far edge of the first/last angled P1 from the rafter end
  var p1FarEdgeIn = p1FootprintIn;  // ½" clearance + clip width projected along rafter

  // ── P1 clips for FULL rafter ──
  // RULE: No P1 clip edge can overhang the rafter — at least ½" clearance from each end
  const maxSpacingIn = p.spacing * 12;
  var p1Positions = [];
  if (p.angledPurlins) {
    // Angled: near edge of first P1 is ½" from front end
    // P1 center = ½" + half the clip footprint projected along rafter
    var halfFootprint = (p1ClipWidth / 2) * Math.sin(angleRad);
    var firstP1Center = 0.5 + halfFootprint;
    var lastP1Center = totalCutLengthIn - 0.5 - halfFootprint;
    var availableSpan = lastP1Center - firstP1Center;
    var p1Spans = Math.max(1, Math.ceil(availableSpan / maxSpacingIn));
    var p1ActualSpacingIn = availableSpan / p1Spans;
    for (var j = 0; j <= p1Spans; j++) {
      p1Positions.push(firstP1Center + j * p1ActualSpacingIn);
    }
  } else {
    // Standard (perpendicular): P1 is a thin fin but still needs ½" from each end
    var firstP1Std = 0.5;  // ½" clearance from front end
    var lastP1Std = totalCutLengthIn - 0.5;  // ½" clearance from back end
    var stdSpan = lastP1Std - firstP1Std;
    var p1Spans = Math.max(1, Math.ceil(stdSpan / maxSpacingIn));
    var p1ActualSpacingIn = stdSpan / p1Spans;
    for (var j = 0; j <= p1Spans; j++) {
      p1Positions.push(firstP1Std + j * p1ActualSpacingIn);
    }
  }
  const p1Count = p1Positions.length;

  // Validate splices don't land on P1 clips
  if (needsSplice) {
    splicePositions.forEach(function(sp, si) {
      p1Positions.forEach(function(pp) {
        if (Math.abs(sp - pp) < 6) spliceWarnings.push('Splice ' + (si+1) + ' conflicts with a P1 clip location');
      });
    });
  }

  // ── Build piece definitions ──
  var pieces = [];
  if (pieceCount === 1) {
    pieces.push({
      index: 0,
      label: 'Full Rafter',
      startIn: 0,
      endIn: totalCutLengthIn,
      lengthIn: totalCutLengthIn,
      leftEnd: endPlateType,
      rightEnd: endPlateType,
      p3Positions: p3Positions,
      p5Splice: false,
    });
  } else {
    var cuts = [0].concat(splicePositions).concat([totalCutLengthIn]);
    cuts.sort(function(a,b) { return a - b; });
    for (var k = 0; k < pieceCount; k++) {
      var pStart = cuts[k];
      var pEnd = cuts[k + 1];
      var pLen = pEnd - pStart;
      // P3s that fall within this piece
      var pieceP3 = p3Positions.filter(function(pp) { return pp >= pStart - 0.5 && pp <= pEnd + 0.5; })
                                .map(function(pp) { return pp - pStart; }); // relative to piece start
      pieces.push({
        index: k,
        label: 'Piece ' + (k + 1) + ' of ' + pieceCount,
        startIn: pStart,
        endIn: pEnd,
        lengthIn: pLen,
        leftEnd: k === 0 ? endPlateType : 'p5',
        rightEnd: k === pieceCount - 1 ? endPlateType : 'p5',
        p3Positions: pieceP3,
        p5Splice: (k > 0 || k < pieceCount - 1),
      });
    }
  }

  // ── Assign P1 positions to each piece (sliced from full rafter) ──
  pieces.forEach(function(pc) {
    // Find P1s that fall within this piece's span (with small tolerance)
    pc.p1Positions = p1Positions.filter(function(pp) {
      return pp >= pc.startIn - 0.5 && pp <= pc.endIn + 0.5;
    }).map(function(pp) {
      return pp - pc.startIn;  // convert to piece-relative position
    });
  });

  // ── Active piece calcs ──
  var ap = pieces[Math.min(activePiece, pieces.length - 1)];
  var cutLengthIn = ap.lengthIn;
  var cutLengthFt = cutLengthIn / 12;

  // P1 clips for this piece — from full-rafter layout, not independent calculation
  var pieceP1Count = ap.p1Positions.length;
  var pieceP1SpacingIn = pieceP1Count > 1 ? p1ActualSpacingIn : cutLengthIn;  // uniform spacing from full rafter
  var pieceP1Spans = Math.max(1, pieceP1Count - 1);
  // P2 count for this piece: 1 per P2-end, 0 per P5-end
  var pieceP2Count = (ap.leftEnd === 'p2' ? 1 : 0) + (ap.rightEnd === 'p2' ? 1 : 0);
  var pieceP5Count = (ap.leftEnd === 'p5' ? 1 : 0) + (ap.rightEnd === 'p5' ? 1 : 0);
  var pieceP3Count = ap.p3Positions.length;

  const p2Count = pieceP2Count;

  // ── Rebar stick layout ──
  const rebarGapEach = p.endGapFt * 12;         // end gap in inches
  const maxStickIn = p.maxStickFt * 12;          // max stick length in inches
  const rebarAvailIn = p.reinforced ? Math.max(0, cutLengthIn - 2 * rebarGapEach) : 0;

  // Compute individual stick positions (inches from left end of piece)
  var rebarStickPositions = [];  // [{startIn, endIn, lengthIn}]
  var rebarSticks = 0;
  var rebarLengthIn = 0;  // total rebar length (all sticks combined)
  if (p.reinforced && rebarAvailIn > 0) {
    var numSticks = Math.max(1, Math.floor(rebarAvailIn / maxStickIn));
    // If all sticks fit with no gaps (exact fill), that's fine
    // If there's leftover, it becomes evenly distributed gaps
    var totalRebarLen = numSticks * maxStickIn;
    // If total exceeds available (shouldn't happen with floor), trim last stick
    if (totalRebarLen > rebarAvailIn) {
      totalRebarLen = (numSticks - 1) * maxStickIn + (rebarAvailIn - (numSticks - 1) * maxStickIn);
    }
    rebarSticks = numSticks;
    rebarLengthIn = Math.min(totalRebarLen, rebarAvailIn);

    if (numSticks === 1) {
      // Single stick: centered in available zone
      var stickLen = Math.min(maxStickIn, rebarAvailIn);
      var edgeGap = (rebarAvailIn - stickLen) / 2;
      rebarStickPositions.push({
        startIn: rebarGapEach + edgeGap,
        endIn: rebarGapEach + edgeGap + stickLen,
        lengthIn: stickLen
      });
    } else {
      // Multiple sticks: evenly distributed
      var totalStickLen = numSticks * maxStickIn;
      var totalGap = rebarAvailIn - totalStickLen;
      var gapBetween = totalGap > 0 ? totalGap / (numSticks - 1) : 0;
      for (var si = 0; si < numSticks; si++) {
        var stStart = rebarGapEach + si * (maxStickIn + gapBetween);
        var stEnd = stStart + maxStickIn;
        // Clamp last stick to not exceed available zone
        if (stEnd > cutLengthIn - rebarGapEach) stEnd = cutLengthIn - rebarGapEach;
        rebarStickPositions.push({
          startIn: stStart,
          endIn: stEnd,
          lengthIn: stEnd - stStart
        });
      }
    }
  }

  const ceeWtPerFt = 10.83;
  const ceeWeight = cutLengthFt * ceeWtPerFt * 2;
  const p1Weight = pieceP1Count * 4.5;
  // P2: 9"x24"x10GA = 8.1 lbs. P6: 9"x15"x10GA = ~5.06 lbs (9*15*0.135*0.2836)
  var p6Count = 0;
  if (p.angledPurlins) {
    p6Count = pieceP2Count;  // P6 replaces P2 on all rafter ends
    pieceP2Count = 0;
  }
  const p2Weight = pieceP2Count * 8.1;
  const p6Weight = p6Count * 5.06;
  const p3Weight = Math.round(0.75 * 14 * 26 * 0.2836) * pieceP3Count;
  const p5Weight = pieceP5Count * 13.82;  // BS101 splice plate ~13.82 lbs
  // Rebar properties by size: [weight per ft (lbs), bar diameter (inches)]
  var rebarData = {
    '#5':  [1.043, 0.625],
    '#6':  [1.502, 0.750],
    '#7':  [2.044, 0.875],
    '#8':  [2.670, 1.000],
    '#9':  [3.400, 1.128],
    '#10': [4.303, 1.270],
    '#11': [5.313, 1.410]
  };
  var rbInfo = rebarData[p.rebarSize] || rebarData['#9'];
  const rebarWtPerFt = rbInfo[0];
  const rebarBarDia = rbInfo[1];
  const rebarTotalWeight = p.reinforced ? (rebarLengthIn / 12) * rebarWtPerFt * 4 : 0;
  const totalWeight = Math.round(ceeWeight + p1Weight + p2Weight + p6Weight + p3Weight + p5Weight + rebarTotalWeight);

  return {
    // Full rafter info
    totalCutLengthIn, totalCutLengthFt, p3Count, p3Positions, p1Positions: p1Positions,
    needsSplice, spliceCount, pieceCount, splicePositions, spliceWarnings, pieces,
    // Active piece info
    cutLengthIn, cutLengthFt,
    p1Count: pieceP1Count, p1Spans: pieceP1Spans, p1ActualSpacingIn: pieceP1SpacingIn,
    p2Count: pieceP2Count, p6Count: p6Count, p3CountPiece: pieceP3Count, p5Count: pieceP5Count,
    pieceP1Positions: ap.p1Positions, pieceP3Positions: ap.p3Positions,
    leftEnd: ap.leftEnd, rightEnd: ap.rightEnd,
    endPlateType: endPlateType, angleRad: angleRad, p1FootprintIn: p1FootprintIn,
    needsSplice, rebarLengthIn, rebarSticks, rebarGapEach,
    ceeWeight, p1Weight, p2Weight, p6Weight, p3Weight, p5Weight, rebarTotalWeight, totalWeight,
    rebarBarDia, rebarStickPositions, rebarAvailIn, activePieceData: ap,
  };
}

// ═══════════════════════════════════════════════
// MAIN DRAW FUNCTION
// ═══════════════════════════════════════════════
function draw() {
  const p = getParams();
  const d = calc(p);
  const svg = document.getElementById('svg');
  svg.innerHTML = '';
  currentWeldDefs = [];

  // Layout group helpers — wrap content sections in draggable <g> with stored offset
  function layoutGroup(id) {
    var g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    g.setAttribute('data-layout-id', id);
    var ov = layoutOverrides[id];
    if (ov && (ov.dx || ov.dy)) {
      g.setAttribute('transform', 'translate(' + (ov.dx || 0) + ',' + (ov.dy || 0) + ')');
    }
    return g;
  }
  // Mark start of a layout section
  function layoutStart() { return svg.childNodes.length; }
  // Wrap everything added since mark into a layout group
  function layoutEnd(id, startIdx) {
    var lg = layoutGroup(id);
    var nodes = [];
    for (var i = startIdx; i < svg.childNodes.length; i++) nodes.push(svg.childNodes[i]);
    nodes.forEach(function(n) { lg.appendChild(n); });
    svg.appendChild(lg);
  }

  const projName = (document.getElementById('setProjectName') || {}).value || 'RAFTER PROJECT';
  const customer = (document.getElementById('setCustomer') || {}).value || '';
  const jobNum = (document.getElementById('setJobNumber') || {}).value || 'JOB-001';
  const drawnBy = (document.getElementById('setDrawnBy') || {}).value || 'AUTO';
  const rafterMark = (document.getElementById('setRafterMark') || {}).value || 'B1';
  const drawingNum = (document.getElementById('setDrawingNum') || {}).value || 'SD-B1-001';
  const surfPrep = (document.getElementById('setSurfPrep') || {}).value || 'SSPC-SP2';

  // ── Sheet border ──
  svg.appendChild($r(10,10,1080,830,'obj thick'));
  svg.appendChild($r(12,12,1076,826,'obj hair'));

  // Helper to register and draw a weld (skips deleted welds)
  function weld(ax, ay, routeX, routeY, size, opts, id) {
    if (deletedWelds.indexOf(id) !== -1) return null;  // skip deleted welds
    currentWeldDefs.push({ id, ax, ay, routeX, routeY, size, opts: {...opts} });
    return awsWeld(svg, ax, ay, routeX, routeY, size, opts, id);
  }

  // ════════════════════════════════════════════════════════════════════
  // ZONE 1: ELEVATION VIEW (y=30 to y=200)
  // ════════════════════════════════════════════════════════════════════
  const beamL = 80;
  const beamR = 680;
  const beamW = beamR - beamL;
  const sc = beamW / d.cutLengthIn;
  const beamY = 95;
  const beamH = 14 * sc;  // SAME SCALE as horizontal (sc px/in everywhere)
  const beamCx = (beamL + beamR) / 2;
  const beamCy = beamY + beamH / 2;

  // Beam body
  const fv = $g('hover-part', 'rafter');
  fv.appendChild($p('M '+beamL+' '+beamY+' L '+beamR+' '+beamY+' L '+beamR+' '+(beamY+beamH)+' L '+beamL+' '+(beamY+beamH)+' Z', 'cee'));
  fv.appendChild($l(beamL, beamY + beamH*0.35, beamR, beamY + beamH*0.35, 'hidden'));
  fv.appendChild($l(beamL, beamY + beamH*0.65, beamR, beamY + beamH*0.65, 'hidden'));
  fv.appendChild($l(beamCx, beamY-20, beamCx, beamY+beamH+20, 'center'));
  svg.appendChild(fv);

  // P1 Clips — seen EDGE-ON in elevation = THIN VERTICAL LINES
  // Uses piece-relative positions from full-rafter layout (consistent spacing across all pieces)
  const p1g = $g('hover-part', 'clips');
  const spacingPx = d.p1ActualSpacingIn * sc;  // uniform spacing (used for section-cut pos, weld callouts)
  const p1Height = 10 * sc;   // 10" extending upward — true scale
  var pieceP1Px = (d.pieceP1Positions || []).map(function(posIn) { return beamL + posIn * sc; });

  pieceP1Px.forEach(function(cx) {
    p1g.appendChild($l(cx, beamY, cx, beamY - p1Height, 'obj med'));
  });
  svg.appendChild(p1g);

  // P1 label at far right
  if (d.p1Count > 0) {
    dlabel(beamR + 15, beamY - p1Height/2, 'ev-p1-lbl', function(g) {
      g.appendChild($t(0, 0, 'P1 CLIPS (x' + d.p1Count + ')', 'lblb'));
      g.appendChild($t(0, 10, 'SHOP WELD (WPS-C)', 'note'));
      g.appendChild($t(0, 18, '1/8" FILLET BOTH SIDES', 'note'));
    });
    var leaderStartX = pieceP1Px.length > 2 ? pieceP1Px[2] : (pieceP1Px.length > 0 ? pieceP1Px[pieceP1Px.length-1] : beamCx);
    svg.appendChild($l(leaderStartX, beamY - p1Height/2, beamR + 15, beamY - p1Height/2, 'obj thin'));
  }

  // Purlin spacing note (single label, no chain)
  svg.appendChild($t(beamR + 5, beamY - p1Height - 5, d.p1Count + ' P1 @ ' + fmtFtIn(d.p1ActualSpacingIn) + ' O.C.', 'note'));

  // Welds for CEE stitch (routed away)
  weld(beamL + beamW*0.15, beamY, 20, 30, '5/16', {stitch:'3"-36" O.C.', wpsCode:'B', refDir:'left', bothSides:true}, 'ev-cee-l');
  weld(beamR - beamW*0.15, beamY, beamR - 20, 30, '5/16', {stitch:'3"-36" O.C.', wpsCode:'B', refDir:'right', bothSides:true}, 'ev-cee-r');

  // P3 Connection Plates — seen EDGE-ON in elevation = THIN HORIZONTAL LINE under beam
  // In elevation we see the ¾" thickness edge-on, 26" long (along rafter)
  const p3g = $g('hover-part', 'connplate');
  const p3DrawLen = 26 * sc;  // 26" along rafter length — true rafter scale

  // P3 positions: use piece-relative positions from calc, convert to pixel coords
  var p3Positions = (d.pieceP3Positions || []).map(function(posIn) {
    return beamL + posIn * sc;
  });
  // Fallback for single-piece: evenly distribute if no calc positions
  if (p3Positions.length === 0 && d.pieceCount === 1 && d.p3Count > 0) {
    for (var fi = 0; fi < d.p3Count; fi++) {
      p3Positions.push(beamL + beamW * ((fi + 1) / (d.p3Count + 1)));
    }
  }

  var p3Y = beamY + beamH; // flush against beam bottom — no gap
  p3Positions.forEach(function(px, pi) {
    // Thin horizontal line at true rafter scale, touching beam bottom
    // 3/4" thick at elevation vertical scale (beamH/14)
    var p3Thk = Math.max(0.75 * (beamH / 14), 1.5);
    p3g.appendChild($r(px - p3DrawLen/2, p3Y, p3DrawLen, p3Thk, 'conn-plate'));

    // Draggable P3 handle in column edit mode
    if (columnEditMode) {
      var handleH = beamH + 30;  // extends above and below beam for easy grabbing
      var handleW = p3DrawLen + 10;
      var handle = $e('rect', {
        x: px - handleW/2,
        y: beamY - 10,
        width: handleW,
        height: handleH,
        fill: 'rgba(246,174,45,0.12)',
        stroke: '#F6AE2D',
        'stroke-width': '1',
        'stroke-dasharray': '4,2',
        rx: 3,
        class: 'p3-drag-handle',
        'data-p3-drag-idx': pi,
        'data-p3-px': px,
        'data-beam-l': beamL,
        'data-beam-w': beamW,
        'data-cut-in': d.cutLengthIn
      });
      p3g.appendChild(handle);
      // Position label above handle
      p3g.appendChild($t(px, beamY - 14, 'COL ' + (pi + 1), 'noteb', 'middle'));
      // Show current position in feet
      var posFt = Math.round(((px - beamL) / beamW) * d.cutLengthIn / 12 * 10) / 10;
      p3g.appendChild($t(px, beamY - 24, posFt + "'", 'note', 'middle'));
    }
  });
  svg.appendChild(p3g);

  // End Conditions — P2 end cap, P6 flat plate, or P5 splice plate at each end
  const p2ExtensionAbove = 9.5 * sc;  // 9.5" above beam — true scale (P2 only)
  const p2ExtensionBelow = 0.5 * sc;  // 0.5" below beam — true scale
  const p6Overhang = 0.5 * sc;        // P6: 0.5" overhang all around
  const p5HalfLen = 9 * sc;           // P5 splice plate: 18" total, 9" per piece (along rafter)
  // Compute effective extension above for dimension purposes
  var endExtAbove = (d.endPlateType === 'p6') ? p6Overhang : p2ExtensionAbove;
  var endExtBelow = p2ExtensionBelow;  // same for both P2 and P6
  const p2g = $g('hover-part', 'endcaps');

  // Left end
  if (d.leftEnd === 'p2') {
    p2g.appendChild($l(beamL, beamY + beamH + p2ExtensionBelow, beamL, beamY - p2ExtensionAbove, 'obj thick'));
  } else if (d.leftEnd === 'p6') {
    // P6: flat plate with ½" overhang all around — shorter vertical line
    p2g.appendChild($l(beamL, beamY + beamH + p6Overhang, beamL, beamY - p6Overhang, 'obj thick'));
  } else {
    // P5 splice
    var p5L = $e('rect', {x: beamL - 2, y: beamY - 1, width: p5HalfLen, height: beamH + 2,
      class: 'obj med', fill: 'none', 'stroke-dasharray': '4,2'});
    p2g.appendChild(p5L);
    p2g.appendChild($t(beamL + p5HalfLen/2, beamY - 6, 'P5 SPLICE (9")', 'noteb', 'middle'));
  }
  // Right end
  if (d.rightEnd === 'p2') {
    p2g.appendChild($l(beamR, beamY + beamH + p2ExtensionBelow, beamR, beamY - p2ExtensionAbove, 'obj thick'));
  } else if (d.rightEnd === 'p6') {
    p2g.appendChild($l(beamR, beamY + beamH + p6Overhang, beamR, beamY - p6Overhang, 'obj thick'));
  } else {
    var p5R = $e('rect', {x: beamR - p5HalfLen + 2, y: beamY - 1, width: p5HalfLen, height: beamH + 2,
      class: 'obj med', fill: 'none', 'stroke-dasharray': '4,2'});
    p2g.appendChild(p5R);
    p2g.appendChild($t(beamR - p5HalfLen/2, beamY - 6, 'P5 SPLICE (9")', 'noteb', 'middle'));
  }
  svg.appendChild(p2g);

  // No NP zones on rafters

  // Rebar — INSIDE BEAM at top and bottom (near flanges)
  // Individual sticks with gaps between them
  if (p.reinforced && d.rebarStickPositions && d.rebarStickPositions.length > 0) {
    const rbThk = 2.5;   // rebar thickness as small rectangle
    const rbOff = 1.5;   // very close to top/bottom edge of beam
    d.rebarStickPositions.forEach(function(stick) {
      var sxL = beamL + stick.startIn * sc;
      var sxR = beamL + stick.endIn * sc;
      var sLen = sxR - sxL;
      // 1 rebar at top of beam (represents both left+right top corner rebar overlapping)
      svg.appendChild($e('rect', {x:sxL, y:beamY + rbOff, width:sLen, height:rbThk, class:'rebar-solid', rx:0.5}));
      // 1 rebar at bottom of beam
      svg.appendChild($e('rect', {x:sxL, y:beamY + beamH - rbOff - rbThk, width:sLen, height:rbThk, class:'rebar-solid', rx:0.5}));
    });
  }

  // ── DIMENSION CHAINS FROM LEFT END ──

  // ROW 1: Cumulative P1 distances from left end of piece
  var dimRow1Y = beamY + beamH + 32;
  var pp1 = d.pieceP1Positions || [];
  // Baseline dimension line across full length
  svg.appendChild($l(beamL, dimRow1Y + 8, beamR, dimRow1Y + 8, 'dim'));
  // Tick mark and cumulative label at each P1 position
  for (var pi = 0; pi < pp1.length; pi++) {
    var px = beamL + pp1[pi] * sc;
    var cumDist = pp1[pi];
    // Tick mark
    svg.appendChild($l(px, dimRow1Y + 2, px, dimRow1Y + 14, 'dim'));
    // Label — cumulative distance from left end (stagger if many)
    var stagger = (pp1.length > 12 && pi % 2 === 1) ? 16 : 7;
    svg.appendChild($t(px, dimRow1Y - stagger + 7, fmtFtIn(cumDist), 'note', 'middle'));
  }
  svg.appendChild($t(beamL - 3, dimRow1Y + 12, 'P1', 'noteb', 'end'));

  // ROW 2: Individual rebar stick positions
  if (p.reinforced && d.rebarStickPositions && d.rebarStickPositions.length > 0) {
    var dimRow2Y = dimRow1Y + 34;
    var sticks = d.rebarStickPositions;

    // Left end gap dimension
    var firstStartX = beamL + sticks[0].startIn * sc;
    dimHRebar(svg, beamL, firstStartX, dimRow2Y, 8, fmtFtIn(sticks[0].startIn));
    svg.appendChild($t(firstStartX, dimRow2Y - 2, 'RB1 START', 'note', 'middle'));

    // Each stick and gap between them
    sticks.forEach(function(stick, si) {
      var sxL = beamL + stick.startIn * sc;
      var sxR = beamL + stick.endIn * sc;
      // Stick dimension
      dimHRebar(svg, sxL, sxR, dimRow2Y, 8, fmtFtIn(stick.lengthIn) + ' RB' + (si + 1));
      // Gap to next stick
      if (si < sticks.length - 1) {
        var nextStart = beamL + sticks[si + 1].startIn * sc;
        var gapIn = sticks[si + 1].startIn - stick.endIn;
        if (gapIn > 0.5) {
          dimHRebar(svg, sxR, nextStart, dimRow2Y, 8, fmtFtIn(gapIn) + ' GAP');
        }
      }
    });

    // Right end gap dimension
    var lastEndX = beamL + sticks[sticks.length - 1].endIn * sc;
    var rightGapIn = d.cutLengthIn - sticks[sticks.length - 1].endIn;
    dimHRebar(svg, lastEndX, beamR, dimRow2Y, 8, fmtFtIn(rightGapIn));
    svg.appendChild($t(lastEndX, dimRow2Y - 2, 'RB' + sticks.length + ' END', 'note', 'middle'));

    // Rebar weld symbol on elevation — route UP to avoid overlapping dim rows
    weld(firstStartX + 40, beamY + 3, firstStartX + 60, beamY - p1Height - 18, '3/16', {stitch:'3"-3\' O.C.', wpsCode:'D', refDir:'right'}, 'ev-rebar-weld');
  }

  // Section A-A cut indicator on elevation
  if (d.p1Count > 0) {
    const aaCutX = beamL + spacingPx * Math.max(1, Math.floor(d.p1Count/2));
    // Dashed vertical line through beam at cut location
    svg.appendChild($l(aaCutX, beamY - 16, aaCutX, beamY + beamH + 16, 'cut-line'));
    // Section labels A-A — positioned clear of beam edges
    svg.appendChild($t(aaCutX - 10, beamY - 18, 'A', 'lblb'));
    svg.appendChild($t(aaCutX - 10, beamY + beamH + 24, 'A', 'lblb'));
    // Small arrows pointing at cut line
    svg.appendChild($l(aaCutX - 12, beamY - 10, aaCutX - 2, beamY - 10, 'cut-line'));
    svg.appendChild($l(aaCutX - 12, beamY + beamH + 14, aaCutX - 2, beamY + beamH + 14, 'cut-line'));
  }

  // P1 weld symbols on elevation
  if (d.p1Count > 0) {
    weld(beamL + spacingPx, beamY, beamL + spacingPx - 30, beamY - 50, '1/8', {wpsCode:'C', refDir:'left'}, 'ev-p1-weld');
  }

  // End weld zone labels
  // No NP labels on rafters

  // P3 dimension labels on elevation — positioned just below P3 plate, above dim rows
  p3Positions.forEach(function(px, pi) {
    svg.appendChild($t(px, p3Y + 20, 'P3 (26"x14"x¾")', 'note', 'middle'));
  });

  // Welds P2/P5 & P3
  if (d.leftEnd === 'p2') {
    weld(beamL, beamCy, 10, beamY - 35, '3/16', {allAround:true, wpsCode:'F', refDir:'left'}, 'ev-p2-l-weld');
  } else if (d.leftEnd === 'p6') {
    weld(beamL, beamCy, 10, beamY - 35, '3/16', {allAround:true, wpsCode:'F', refDir:'left'}, 'ev-p6-l-weld');
  } else {
    weld(beamL + p5HalfLen/2, beamCy, beamL - 15, beamY - 35, '3/16', {stitch:'FIELD', wpsCode:'F', refDir:'left'}, 'ev-p5-l-weld');
  }
  if (d.rightEnd === 'p2') {
    weld(beamR, beamCy, beamR + 10, beamY - 35, '3/16', {allAround:true, wpsCode:'F', refDir:'right'}, 'ev-p2-r-weld');
  } else if (d.rightEnd === 'p6') {
    weld(beamR, beamCy, beamR + 10, beamY - 35, '3/16', {allAround:true, wpsCode:'F', refDir:'right'}, 'ev-p6-r-weld');
  } else {
    weld(beamR - p5HalfLen/2, beamCy, beamR + 15, beamY - 35, '3/16', {stitch:'FIELD', wpsCode:'F', refDir:'right'}, 'ev-p5-r-weld');
  }
  p3Positions.forEach(function(px, pi) {
    weld(px, p3Y + 2, px + 50, p3Y + 18, '3/16', {allAround:true, wpsCode:'F', refDir:'right'}, 'ev-p3-weld-'+pi);
  });

  // End labels
  if (d.leftEnd === 'p2') {
    dlabel(beamL - 40, beamY - p2ExtensionAbove - 8, 'ev-p2-lbl', function(g) {
      g.appendChild($t(0, 0, 'P2 END CAP', 'noteb'));
      g.appendChild($t(0, 8, '9.5" ABOVE', 'note'));
    });
  } else if (d.leftEnd === 'p6') {
    dlabel(beamL - 40, beamY - p6Overhang - 14, 'ev-p6l-lbl', function(g) {
      g.appendChild($t(0, 0, 'P6 END PLATE', 'noteb'));
      g.appendChild($t(0, 8, '9"x15" — \u00BD" OH', 'note'));
    });
  } else {
    dlabel(beamL - 5, beamY - 18, 'ev-p5l-lbl', function(g) {
      g.appendChild($t(0, 0, 'P5 SPLICE (FIELD)', 'noteb'));
      g.appendChild($t(0, 8, 'BS101 — TEK + WELD', 'note'));
    });
  }
  if (d.rightEnd === 'p2') {
    dlabel(beamR + 5, beamY - p2ExtensionAbove - 8, 'ev-p2r-lbl', function(g) {
      g.appendChild($t(0, 0, 'P2 END CAP', 'noteb'));
      g.appendChild($t(0, 8, '9.5" ABOVE', 'note'));
    });
  } else if (d.rightEnd === 'p6') {
    dlabel(beamR + 5, beamY - p6Overhang - 14, 'ev-p6r-lbl', function(g) {
      g.appendChild($t(0, 0, 'P6 END PLATE', 'noteb'));
      g.appendChild($t(0, 8, '9"x15" — \u00BD" OH', 'note'));
    });
  } else {
    dlabel(beamR - 50, beamY - 18, 'ev-p5r-lbl', function(g) {
      g.appendChild($t(0, 0, 'P5 SPLICE (FIELD)', 'noteb'));
      g.appendChild($t(0, 8, 'BS101 — TEK + WELD', 'note'));
    });
  }

  // Overall dimensions
  // Overall length — below all dimension rows
  var hasRebar = p.reinforced && d.rebarStickPositions && d.rebarStickPositions.length > 0;
  var overallDimY = hasRebar ? dimRow2Y + 26 : dimRow1Y + 32;
  dimH(svg, beamL, beamR, overallDimY, 15, fmtFtIn(d.cutLengthIn));
  dimV(svg, beamR + 10, beamY, beamY + beamH, 8, '14"');
  // End plate extension dimension
  if (d.leftEnd === 'p2') {
    dimV(svg, beamL - 12, beamY - p2ExtensionAbove, beamY, -8, '9.5"');
  } else if (d.leftEnd === 'p6') {
    dimV(svg, beamL - 12, beamY - p6Overhang, beamY, -8, '\u00BD"');
  }

  // Piece mark leaders on elevation — staggered vertically to avoid crossing
  var pmY1 = beamY - p1Height - 38;  // highest tier
  var pmY2 = beamY - p1Height - 26;  // second tier
  // B1 mark — pointing to beam center (highest tier, leftward)
  svg.appendChild($l(beamCx - 50, beamCy, beamCx - 90, pmY1, 'dim'));
  svg.appendChild($t(beamCx - 92, pmY1 - 2, rafterMark, 'lblb', 'end'));
  // P1 mark (second tier, rightward — well separated from B1)
  if (d.p1Count > 0) {
    var p1MarkX = beamL + spacingPx * Math.min(3, d.p1Count - 1);
    svg.appendChild($l(p1MarkX, beamY - p1Height, p1MarkX + 20, pmY2, 'dim'));
    svg.appendChild($t(p1MarkX + 22, pmY2 - 2, 'P1', 'lblb'));
  }
  // End plate mark — at left end, pointing up and left
  var epMarkLabel = (d.endPlateType === 'p6') ? 'P6' : 'P2';
  var epMarkAbove = (d.endPlateType === 'p6') ? p6Overhang : p2ExtensionAbove;
  svg.appendChild($l(beamL, beamY - epMarkAbove, beamL - 18, beamY - epMarkAbove - 14, 'dim'));
  svg.appendChild($t(beamL - 20, beamY - epMarkAbove - 16, epMarkLabel, 'lblb', 'end'));
  // P3 mark — below beam, well clear of dim rows
  if (p3Positions.length > 0) {
    var p3mkX = p3Positions[p3Positions.length - 1];
    svg.appendChild($l(p3mkX + 10, p3Y + 2, p3mkX + 30, p3Y + 14, 'dim'));
    svg.appendChild($t(p3mkX + 32, p3Y + 16, 'P3', 'lblb'));
  }
  // RB mark (if reinforced) — inside beam area to avoid dim rows
  if (hasRebar) {
    var rbMkX = beamL + d.rebarStickPositions[0].startIn * sc + 5;
    svg.appendChild($l(rbMkX, beamY + beamH * 0.3, rbMkX - 15, beamY - 6, 'dim'));
    svg.appendChild($t(rbMkX - 17, beamY - 8, 'RB', 'lblb', 'end'));
  }

  // Notes block
  var _lsNotes = layoutStart();
  var noteBlockX = 710, noteBlockY = 40;
  var noteBlockW = 80, noteBlockH = 130;
  svg.appendChild($r(noteBlockX, noteBlockY, noteBlockW, noteBlockH, 'obj med'));
  svg.appendChild($t(noteBlockX + noteBlockW/2, noteBlockY + 8, 'NOTES', 'lblb', 'middle'));
  svg.appendChild($l(noteBlockX, noteBlockY + 12, noteBlockX + noteBlockW, noteBlockY + 12, 'obj thin'));
  var noteY = noteBlockY + 20;
  svg.appendChild($t(noteBlockX + 3, noteY, 'CEE STITCH:', 'note'));
  svg.appendChild($t(noteBlockX + 3, noteY + 8, '5/16" — 3"@36" O.C.', 'note'));
  svg.appendChild($t(noteBlockX + 3, noteY + 15, 'ENDS: 1"@6"', 'note'));
  svg.appendChild($t(noteBlockX + 3, noteY + 22, 'FIRST 12"', 'note'));
  svg.appendChild($t(noteBlockX + 3, noteY + 32, 'P1: SHOP WELD (WPS-C)', 'note'));
  svg.appendChild($t(noteBlockX + 3, noteY + 39, '1/8" FILLET BOTH SIDES', 'note'));
  svg.appendChild($t(noteBlockX + 3, noteY + 46, 'PURLIN\u2192P1: FIELD TEK', 'note'));
  svg.appendChild($t(noteBlockX + 3, noteY + 53, 'REBAR: 3"@3\' O.C.', 'note'));
  if (p.angledPurlins) {
    svg.appendChild($t(noteBlockX + 3, noteY + 63, 'ANGLED P1: ' + p.purlinAngle + '\u00B0', 'noteb'));
    svg.appendChild($t(noteBlockX + 3, noteY + 70, 'P6 END PLATES (9"x15")', 'note'));
    svg.appendChild($t(noteBlockX + 3, noteY + 77, '\u00BD" OH ALL SIDES', 'note'));
  }
  layoutEnd('notes-block', _lsNotes);

  // Elevation title — below overall dim line
  var elevTitleY = overallDimY + 22;
  var elevTitle = d.pieceCount > 1 ? 'ELEVATION VIEW — ' + d.activePieceData.label.toUpperCase() : 'ELEVATION VIEW';
  svg.appendChild($t(beamCx, elevTitleY, elevTitle, 'ttl', 'middle'));
  svg.appendChild($t(beamCx, elevTitleY + 8, 'SCALE: ' + fmtScale(sc), 'note', 'middle'));

  // ════════════════════════════════════════════════════════════════════
  // ZONE 2: THREE VIEWS ROW (y=210 to y=400)
  // ════════════════════════════════════════════════════════════════════

  var _lsTopView = layoutStart();
  // ── TOP VIEW — Looking DOWN at the rafter ──
  // Beam = long rectangle 8" wide. P1 = thin lines across 8" width. P2 = thin 9" lines at ends.
  // Flange butt joint = dashed line down center. P3 visible but behind rafter.
  var tvZoneTop = elevTitleY + 22;  // dynamic — starts below elevation title
  var tvL = 30, tvR = 500, tvCy = tvZoneTop + 28;
  var tvW = tvR - tvL;
  var tvSc = tvW / d.cutLengthIn;
  var tvDepth = 8 * tvSc;  // TRUE SCALE — same px/in as horizontal
  var tvg = $g('hover-part', 'clips');

  // Beam body (plan view — long rect, 8" wide)
  tvg.appendChild($r(tvL, tvCy - tvDepth/2, tvW, tvDepth, 'cee'));

  // Flange butt joint — DASHED LINE down center of beam (where two CEE flanges meet)
  tvg.appendChild($l(tvL, tvCy, tvR, tvCy, 'hidden'));
  svg.appendChild($t((tvL+tvR)/2 + 40, tvCy - tvDepth/2 - 3, 'FLANGE BUTT JOINT', 'note'));

  // Center lines
  tvg.appendChild($l((tvL+tvR)/2, tvCy - tvDepth/2 - 5, (tvL+tvR)/2, tvCy + tvDepth/2 + 5, 'center'));

  // End caps/splices — THIN LINES across beam at each end
  var tvP2Ext = 0.5 * tvSc;
  // Helper for end plate rendering
  function tvEndPlate(x, endType, label, isLeft) {
    if (endType === 'p2') {
      tvg.appendChild($l(x, tvCy - tvDepth/2 - tvP2Ext, x, tvCy + tvDepth/2 + tvP2Ext, 'obj thick'));
      svg.appendChild($t(x, tvCy + tvDepth/2 + 14, 'P2', 'noteb', 'middle'));
    } else if (endType === 'p6') {
      tvg.appendChild($l(x, tvCy - tvDepth/2 - tvP2Ext, x, tvCy + tvDepth/2 + tvP2Ext, 'obj thick'));
      svg.appendChild($t(x, tvCy + tvDepth/2 + 14, 'P6', 'noteb', 'middle'));
    } else {
      var tvP5Half = 9 * tvSc;
      var rx = isLeft ? x : x - tvP5Half;
      tvg.appendChild($e('rect', {x: rx, y: tvCy - tvDepth/2 - 1, width: tvP5Half, height: tvDepth + 2, class: 'obj med', fill: 'none', 'stroke-dasharray': '3,1.5'}));
      svg.appendChild($t(rx + tvP5Half/2, tvCy + tvDepth/2 + 14, 'P5', 'noteb', 'middle'));
    }
  }
  tvEndPlate(tvL, d.leftEnd, 'L', true);
  tvEndPlate(tvR, d.rightEnd, 'R', false);

  // P1 clips — using piece-relative positions from full-rafter layout
  var tvP1Positions = (d.pieceP1Positions || []);
  var tvAngleRad = d.angleRad || 0;
  tvP1Positions.forEach(function(posIn, pi) {
    var cx = tvL + posIn * tvSc;
    if (tvAngleRad > 0) {
      // Angled P1: diagonal line across beam at the purlin angle
      var halfBeam = tvDepth / 2;
      var dx = halfBeam * Math.tan(tvAngleRad);
      // All P1 clips at the same angle — no mirroring
      tvg.appendChild($l(cx - dx, tvCy - halfBeam, cx + dx, tvCy + halfBeam, 'obj med'));
    } else {
      tvg.appendChild($l(cx, tvCy - tvDepth/2, cx, tvCy + tvDepth/2, 'obj med'));
    }
  });
  // P1 label
  if (d.p1Count > 0) {
    var tvP1LabelX = tvP1Positions.length > 2 ? tvL + tvP1Positions[2] * tvSc + 15 : tvL + tvW/3;
    var angleLabel = p.angledPurlins ? ' @ ' + p.purlinAngle + '\u00B0' : '';
    svg.appendChild($t(tvP1LabelX, tvCy - tvDepth/2 - 6, 'P1 (x'+d.p1Count+') TYP' + angleLabel, 'note'));
  }

  // P3 — below rafter (shown as hidden/dashed). 26" along × 14" across
  // MUST maintain 26:14 ratio. 14" across on 8" beam = 3" overhang each side.
  p3Positions.forEach(function(px, pi) {
    var relPos = (px - beamL) / beamW;
    var tvPx = tvL + tvW * relPos;
    // P3 at true scale — everything uses tvSc
    var tvP3Len = 26 * tvSc;
    var tvP3W = 14 * tvSc;
    var p3rect = $e('rect', {x: tvPx - tvP3Len/2, y: tvCy - tvP3W/2, width: tvP3Len, height: tvP3W, class: 'hidden'});
    tvg.appendChild(p3rect);
    svg.appendChild($t(tvPx, tvCy + tvP3W/2 + 8, 'P3 (BELOW)', 'note', 'middle'));
  });

  // Rebar — individual sticks, 1 near each web edge (top and bottom edge of beam in plan)
  if (p.reinforced && d.rebarStickPositions && d.rebarStickPositions.length > 0) {
    var tvRbThk = 2;
    var tvRbOff = 1;
    d.rebarStickPositions.forEach(function(stick) {
      var sxL = tvL + stick.startIn * tvSc;
      var sxR = tvL + stick.endIn * tvSc;
      var sLen = sxR - sxL;
      // 1 rebar near top edge (near one web)
      tvg.appendChild($e('rect', {x:sxL, y:tvCy - tvDepth/2 + tvRbOff, width:sLen, height:tvRbThk, class:'rebar-solid', rx:0.5}));
      // 1 rebar near bottom edge (near other web)
      tvg.appendChild($e('rect', {x:sxL, y:tvCy + tvDepth/2 - tvRbOff - tvRbThk, width:sLen, height:tvRbThk, class:'rebar-solid', rx:0.5}));
    });
  }

  // No NP zones on rafters

  svg.appendChild(tvg);

  // Top view dims
  dimH(svg, tvL, tvR, tvCy + tvDepth/2, 22, fmtFtIn(d.cutLengthIn));
  dimV(svg, tvL - 8, tvCy - tvDepth/2, tvCy + tvDepth/2, -6, '8"');

  svg.appendChild($t((tvL+tvR)/2, tvCy - tvDepth/2 - 14, 'TOP VIEW (Looking Down)', 'ttl', 'middle'));
  svg.appendChild($t((tvL+tvR)/2, tvCy - tvDepth/2 - 6, 'SCALE: ' + fmtScale(tvSc), 'note', 'middle'));
  layoutEnd('top-view', _lsTopView);

  var _lsBottomView = layoutStart();
  // ── BOTTOM VIEW — Looking UP at the rafter ──
  // Shows P3 plates with bolt holes, rebar lines, full-length
  var bvZoneTop = tvCy + tvDepth/2 + 42;  // 42px gap below top view dims
  var bvL = 30, bvR = 500, bvCy = bvZoneTop + 28;
  var bvW = bvR - bvL;
  var bvSc = bvW / d.cutLengthIn;
  var bvDepth = 8 * bvSc;  // TRUE SCALE — same px/in as horizontal
  var bvg = $g('hover-part', 'connplate');

  // Beam body (plan view from below)
  bvg.appendChild($r(bvL, bvCy - bvDepth/2, bvW, bvDepth, 'cee'));

  // Center line
  bvg.appendChild($l(bvL - 5, bvCy, bvR + 5, bvCy, 'center'));
  bvg.appendChild($l((bvL+bvR)/2, bvCy - bvDepth/2 - 5, (bvL+bvR)/2, bvCy + bvDepth/2 + 5, 'center'));

  // CEE seam
  bvg.appendChild($l(bvL, bvCy, bvR, bvCy, 'hidden'));

  // End plates on bottom view — P2/P6/P5 at each end
  var bvP2Ext = 0.5 * bvSc;
  function bvEndPlate(x, endType, isLeft) {
    if (endType === 'p2') {
      bvg.appendChild($l(x, bvCy - bvDepth/2 - bvP2Ext, x, bvCy + bvDepth/2 + bvP2Ext, 'obj thick'));
      svg.appendChild($t(x, bvCy - bvDepth/2 - 6, 'P2', 'noteb', 'middle'));
    } else if (endType === 'p6') {
      bvg.appendChild($l(x, bvCy - bvDepth/2 - bvP2Ext, x, bvCy + bvDepth/2 + bvP2Ext, 'obj thick'));
      svg.appendChild($t(x, bvCy - bvDepth/2 - 6, 'P6', 'noteb', 'middle'));
    } else {
      var bvP5Half = 9 * bvSc;
      var rx = isLeft ? x : x - bvP5Half;
      bvg.appendChild($e('rect', {x: rx, y: bvCy - bvDepth/2 - 1, width: bvP5Half, height: bvDepth + 2, class: 'obj med', fill: 'none', 'stroke-dasharray': '3,1.5'}));
      svg.appendChild($t(rx + bvP5Half/2, bvCy - bvDepth/2 - 6, 'P5', 'noteb', 'middle'));
    }
  }
  bvEndPlate(bvL, d.leftEnd, true);
  bvEndPlate(bvR, d.rightEnd, false);

  // P1 clips on bottom view — angled when applicable
  var bvP1Positions = (d.pieceP1Positions || []);
  var bvAngleRad = d.angleRad || 0;
  bvP1Positions.forEach(function(posIn, pi) {
    var cx = bvL + posIn * bvSc;
    if (bvAngleRad > 0) {
      var halfBeam = bvDepth / 2;
      var dx = halfBeam * Math.tan(bvAngleRad);
      // All P1 clips at the same angle — no mirroring
      bvg.appendChild($l(cx - dx, bvCy - halfBeam, cx + dx, bvCy + halfBeam, 'obj med'));
    } else {
      bvg.appendChild($l(cx, bvCy - bvDepth/2, cx, bvCy + bvDepth/2, 'obj med'));
    }
  });
  // P1 label on bottom view
  if (d.p1Count > 0) {
    var bvP1LabelX = bvP1Positions.length > 2 ? bvL + bvP1Positions[2] * bvSc + 15 : bvL + bvW/3;
    var bvAngleLabel = p.angledPurlins ? ' @ ' + p.purlinAngle + '\u00B0' : '';
    svg.appendChild($t(bvP1LabelX, bvCy + bvDepth/2 + 30, 'P1 (x'+d.p1Count+') TYP' + bvAngleLabel, 'note'));
  }

  // P3 connection plates — 26" along rafter (horizontal), 14" across (vertical)
  // Use rafter's horizontal scale for length, then derive width from 26:14 ratio
  // This keeps P3 proportionally correct and visually balanced with the beam
  // Then add visible overhang past beam to show the 3" extension each side
  p3Positions.forEach(function(px, pi) {
    var relPos = (px - beamL) / beamW;
    var bvPx = bvL + bvW * relPos;
    // P3 at true scale — everything uses bvSc
    var bvP3Len = 26 * bvSc;
    var bvP3W = 14 * bvSc;
    bvg.appendChild($r(bvPx - bvP3Len/2, bvCy - bvP3W/2, bvP3Len, bvP3W, 'conn-plate'));
    // Bolt holes proportional within the plate
    var boltAlongSpan = bvP3Len * (23/26);
    var boltAcrossSpan = bvP3W * (11/14);
    [[-boltAlongSpan/2, -boltAcrossSpan/2], [boltAlongSpan/2, -boltAcrossSpan/2],
     [-boltAlongSpan/2, boltAcrossSpan/2], [boltAlongSpan/2, boltAcrossSpan/2]].forEach(function(off) {
      bvg.appendChild($c(bvPx + off[0], bvCy + off[1], Math.max(0.46875 * bvSc, 0.8), 'bolt')); // 15/16" dia = 0.46875" radius, true scale
    });
    svg.appendChild($t(bvPx, bvCy + bvP3W/2 + 8, 'P3'+(d.p3Count>1?' ('+(pi+1)+')':''), 'noteb', 'middle'));
  });

  // Rebar — individual sticks, 1 near each web edge
  if (p.reinforced && d.rebarStickPositions && d.rebarStickPositions.length > 0) {
    var bvRbThk = 2.5;
    var bvRbOff = 1;
    d.rebarStickPositions.forEach(function(stick) {
      var sxL = bvL + stick.startIn * bvSc;
      var sxR = bvL + stick.endIn * bvSc;
      var sLen = sxR - sxL;
      // 1 rebar near top edge (near one web)
      bvg.appendChild($e('rect', {x:sxL, y:bvCy - bvDepth/2 + bvRbOff, width:sLen, height:bvRbThk, class:'rebar-solid', rx:0.5}));
      // 1 rebar near bottom edge (near other web)
      bvg.appendChild($e('rect', {x:sxL, y:bvCy + bvDepth/2 - bvRbOff - bvRbThk, width:sLen, height:bvRbThk, class:'rebar-solid', rx:0.5}));
    });
    var bvRbFirstStart = bvL + d.rebarStickPositions[0].startIn * bvSc;
    svg.appendChild($t(bvRbFirstStart - 3, bvCy - bvDepth/2 - 3, p.rebarSize+' x4 REBAR (INSIDE) — '+d.rebarStickPositions.length+' STICK'+(d.rebarStickPositions.length>1?'S':''), 'note'));
  }

  svg.appendChild(bvg);

  // Bottom view dims
  dimH(svg, bvL, bvR, bvCy + bvDepth/2 + 15, 12, fmtFtIn(d.cutLengthIn));
  dimV(svg, bvL - 8, bvCy - bvDepth/2, bvCy + bvDepth/2, -6, '8"');

  svg.appendChild($t((bvL+bvR)/2, bvCy - bvDepth/2 - 14, 'BOTTOM VIEW (Looking Up)', 'ttl', 'middle'));
  svg.appendChild($t((bvL+bvR)/2, bvCy - bvDepth/2 - 6, 'SCALE: ' + fmtScale(bvSc), 'note', 'middle'));
  layoutEnd('bottom-view', _lsBottomView);

  var _lsSideView = layoutStart();
  // ── SIDE VIEW (AT EAVE) — Looking at the END of the rafter ──
  var sideViewX = 620, sideViewY = bvCy + 10;
  var sideViewScale = 4.0;
  var sideViewW = 8 * sideViewScale;    // 32px wide
  var sideViewH = 14 * sideViewScale;   // 56px tall
  var sideViewP2Below = 0.5 * sideViewScale;  // 0.5" below
  var isP6Side = (d.endPlateType === 'p6');
  var sideViewP2Above = isP6Side ? (0.5 * sideViewScale) : (9.5 * sideViewScale);
  var sideViewCapH = sideViewH + sideViewP2Below + sideViewP2Above;
  // P6: 9"x15" plate = ½" overhang all around 8"×14" beam → plate is 9"W × 15"H
  // P2: 9"x24" plate = 0.5" below + 9.5" above + 14" beam
  var capWidth = isP6Side ? (9 * sideViewScale) : (sideViewW + 8);
  var svg_g = $g('hover-part', 'detP2');

  // Box beam cross-section
  var beamTopSV = sideViewY - sideViewH/2 + sideViewP2Below;
  svg_g.appendChild($r(sideViewX - sideViewW/2, beamTopSV, sideViewW, sideViewH, 'cee'));

  // End plate cap
  var capL = sideViewX - capWidth/2;
  var capT = sideViewY - sideViewH/2 - sideViewP2Above;
  svg_g.appendChild($r(capL, capT, capWidth, sideViewCapH, 'cap'));

  // Weld line indicator (all-around beam to cap joint)
  svg_g.appendChild($r(sideViewX - sideViewW/2 - 1, beamTopSV - 1, sideViewW + 2, sideViewH + 2, 'weld'));

  if (!isP6Side) {
    // P2: 8 holes in upper extension (4 rows × 2 columns)
    var holeR = 1.5;
    var holeStartY = capT + 6;
    var holeSpacingV = 2 * sideViewScale;
    var holeSpacingH = 3 * sideViewScale;
    for (var hRow = 0; hRow < 4; hRow++) {
      for (var hCol = 0; hCol < 2; hCol++) {
        var hx = sideViewX - holeSpacingH/2 + hCol * holeSpacingH;
        var hy = holeStartY + hRow * holeSpacingV;
        svg_g.appendChild($c(hx, hy, holeR, 'bolt'));
      }
    }
  }

  // Back-to-back CEE seam (horizontal dashed center line)
  svg_g.appendChild($l(sideViewX - sideViewW/2, sideViewY, sideViewX + sideViewW/2, sideViewY, 'hidden'));

  // Center lines
  svg_g.appendChild($l(sideViewX - sideViewW/2 - 8, sideViewY, sideViewX + sideViewW/2 + 8, sideViewY, 'center'));
  svg_g.appendChild($l(sideViewX, capT - 8, sideViewX, sideViewY + sideViewH/2 + sideViewP2Below + 8, 'center'));

  // Rebar dots if reinforced
  if (p.reinforced) {
    var svRbR = 2;
    var svRbOff = svRbR + 1;
    var svBeamTop = beamTopSV;
    var svBeamBot = sideViewY + sideViewH/2 + sideViewP2Below;
    var svBeamLeft = sideViewX - sideViewW/2;
    var svBeamRight = sideViewX + sideViewW/2;
    [[svBeamLeft + svRbOff, svBeamTop + svRbOff],
     [svBeamRight - svRbOff, svBeamTop + svRbOff],
     [svBeamLeft + svRbOff, svBeamBot - svRbOff],
     [svBeamRight - svRbOff, svBeamBot - svRbOff]].forEach(function(pt) {
      svg_g.appendChild($c(pt[0], pt[1], svRbR, 'rebar-circ'));
      svg_g.appendChild($c(pt[0], pt[1], svRbR + 1.5, 'rebar-circ-out'));
    });
  }

  svg.appendChild(svg_g);

  // Side view weld callout
  weld(sideViewX + sideViewW/2, sideViewY, sideViewX + sideViewW/2 + 35, sideViewY - 25, '3/16', {allAround:true, wpsCode:'F', refDir:'right'}, 'sv-ep-weld');

  // Side view dims
  dimH(svg, sideViewX - sideViewW/2, sideViewX + sideViewW/2, sideViewY + sideViewH/2 + sideViewP2Below + 6, 10, '8"');
  if (!isP6Side) {
    dimV(svg, sideViewX + sideViewW/2 + 6, capT, beamTopSV, 10, '9.5"');
  } else {
    dimV(svg, sideViewX + sideViewW/2 + 6, capT, beamTopSV, 10, '\u00BD"');
  }
  dimV(svg, sideViewX + sideViewW/2 + 6, beamTopSV, sideViewY + sideViewH/2 + sideViewP2Below, 25, '14"');
  // Show overall plate size dim
  if (isP6Side) {
    dimH(svg, capL, capL + capWidth, capT - 4, 8, '9"');
    dimV(svg, capL - 6, capT, capT + sideViewCapH, -8, '15"');
  }

  // Labels
  var svBotY = sideViewY + sideViewH/2 + sideViewP2Below;
  if (isP6Side) {
    svg.appendChild($t(sideViewX, svBotY + 26, 'P6 END PLATE (10GA G90)', 'note', 'middle'));
    svg.appendChild($t(sideViewX, svBotY + 36, '9"x15" — WELD ALL-AROUND (WPS-F)', 'note', 'middle'));
    svg.appendChild($t(sideViewX, svBotY + 46, '\u00BD" OVERHANG ALL SIDES', 'note', 'middle'));
    svg.appendChild($t(sideViewX, svBotY + 60, 'SIDE VIEW — P6 END PLATE', 'ttl', 'middle'));
  } else if (d.p2Count > 0) {
    svg.appendChild($t(sideViewX, svBotY + 26, 'P2 END CAP (10GA G90)', 'note', 'middle'));
    svg.appendChild($t(sideViewX, svBotY + 36, '9"x24" — WELD ALL-AROUND (WPS-F)', 'note', 'middle'));
    svg.appendChild($t(sideViewX, svBotY + 46, '1/4" DIA HOLES (x8)', 'note', 'middle'));
    svg.appendChild($t(sideViewX, svBotY + 60, 'SIDE VIEW (AT EAVE)', 'ttl', 'middle'));
  } else {
    svg.appendChild($t(sideViewX, svBotY + 26, 'NO P2 ON THIS PIECE', 'note', 'middle'));
    svg.appendChild($t(sideViewX, svBotY + 36, 'SEE P5 SPLICE DETAIL', 'note', 'middle'));
    svg.appendChild($t(sideViewX, svBotY + 60, 'SIDE VIEW (AT EAVE)', 'ttl', 'middle'));
  }
  svg.appendChild($t(sideViewX, svBotY + 68, 'SCALE: ' + fmtScale(sideViewScale), 'note', 'middle'));
  layoutEnd('side-view', _lsSideView);

  // ════════════════════════════════════════════════════════════════════
  // ZONE 3: DETAILS ROW — dynamically positioned below Zone 2
  // ════════════════════════════════════════════════════════════════════
  var zone3Top = Math.max(sideViewY + sideViewH/2 + sideViewP2Below + 72, bvCy + bvDepth/2 + 45);

  var _lsSectionAA = layoutStart();
  // SECTION A-A - Back-to-back CEE box beam (CORRECT orientation)
  // WEBS are LEFT and RIGHT outer walls (vertical)
  // FLANGES meet at TOP and BOTTOM (4" each = 8" total, butting)
  // LIPS fold INWARD from flange ends
  const aa = $g('hover-part', 'secAA');
  const aScale = 3.5;
  const aX = 110, aY = zone3Top + 70;
  const aW = 8 * aScale;
  const aH = 14 * aScale;
  const boxL = aX - aW/2, boxR2 = aX + aW/2, boxT = aY - aH/2, boxB = aY + aH/2;

  aa.appendChild($r(boxL, boxT, aW, aH, 'cee'));

  const gThk = 0.135 * aScale;
  const flangeW = 4 * aScale;
  const lipW = 0.75 * aScale;

  // LEFT CEE (C-shape opening to RIGHT)
  // Left web (vertical outer wall)
  aa.appendChild($l(boxL + gThk, boxT, boxL + gThk, boxB, 'obj med'));
  // Top flange (horizontal, 4" going RIGHT from web)
  aa.appendChild($l(boxL, boxT, boxL + flangeW, boxT, 'obj med'));
  // Top flange to web connection
  aa.appendChild($l(boxL, boxT, boxL + gThk, boxT, 'obj med'));
  aa.appendChild($l(boxL + gThk, boxT, boxL + gThk, boxT + gThk, 'obj med'));
  // Top lip (kicks DOWN inward, toward center)
  aa.appendChild($l(boxL + flangeW, boxT, boxL + flangeW, boxT + lipW, 'obj thin'));
  // Bottom flange (horizontal, 4" going RIGHT from web)
  aa.appendChild($l(boxL, boxB, boxL + flangeW, boxB, 'obj med'));
  // Bottom flange to web connection
  aa.appendChild($l(boxL, boxB, boxL + gThk, boxB, 'obj med'));
  aa.appendChild($l(boxL + gThk, boxB, boxL + gThk, boxB - gThk, 'obj med'));
  // Bottom lip (kicks UP inward, toward center)
  aa.appendChild($l(boxL + flangeW, boxB, boxL + flangeW, boxB - lipW, 'obj thin'));

  // RIGHT CEE (C-shape opening to LEFT - mirror)
  // Right web (vertical outer wall)
  aa.appendChild($l(boxR2 - gThk, boxT, boxR2 - gThk, boxB, 'obj med'));
  // Top flange (horizontal, 4" going LEFT from web)
  aa.appendChild($l(boxR2, boxT, boxR2 - flangeW, boxT, 'obj med'));
  // Top flange to web connection
  aa.appendChild($l(boxR2, boxT, boxR2 - gThk, boxT, 'obj med'));
  aa.appendChild($l(boxR2 - gThk, boxT, boxR2 - gThk, boxT + gThk, 'obj med'));
  // Top lip (kicks DOWN inward, toward center)
  aa.appendChild($l(boxR2 - flangeW, boxT, boxR2 - flangeW, boxT + lipW, 'obj thin'));
  // Bottom flange (horizontal, 4" going LEFT from web)
  aa.appendChild($l(boxR2, boxB, boxR2 - flangeW, boxB, 'obj med'));
  // Bottom flange to web connection
  aa.appendChild($l(boxR2, boxB, boxR2 - gThk, boxB, 'obj med'));
  aa.appendChild($l(boxR2 - gThk, boxB, boxR2 - gThk, boxB - gThk, 'obj med'));
  // Bottom lip (kicks UP inward, toward center)
  aa.appendChild($l(boxR2 - flangeW, boxB, boxR2 - flangeW, boxB - lipW, 'obj thin'));

  // Center line (where lips meet)
  aa.appendChild($l(aX, boxT, aX, boxB, 'hidden'));
  // Dashed lines showing flange butt joints at top and bottom
  aa.appendChild($l(boxL + flangeW - 1, boxT + 1, boxR2 - flangeW + 1, boxT + 1, 'hidden'));
  aa.appendChild($l(boxL + flangeW - 1, boxB - 1, boxR2 - flangeW + 1, boxB - 1, 'hidden'));

  // P1 clip on top of Section A-A — looking ALONG rafter, we see P1 face-on
  // P1 is 6" wide × 10" tall, centered on the 8" beam top
  const aaP1W = 6 * aScale;  // 6" base width (face-on view)
  const aaP1H = 10 * aScale;  // 10" tall extension
  aa.appendChild($r(aX - aaP1W/2, boxT - aaP1H, aaP1W, aaP1H, 'clip-fill'));
  // Fillet weld triangles at base on both 6" edges
  aa.appendChild($p('M '+(aX - aaP1W/2 - 3)+' '+boxT+' L '+(aX - aaP1W/2)+' '+(boxT - 4)+' L '+(aX - aaP1W/2)+' '+boxT+' Z', 'weld'));
  aa.appendChild($p('M '+(aX + aaP1W/2 + 3)+' '+boxT+' L '+(aX + aaP1W/2)+' '+(boxT - 4)+' L '+(aX + aaP1W/2)+' '+boxT+' Z', 'weld'));
  svg.appendChild($t(aX + aaP1W/2 + 6, boxT - aaP1H/2, 'P1', 'noteb'));
  // Dimension the P1 width
  dimH(svg, aX - aaP1W/2, aX + aaP1W/2, boxT - aaP1H, -8, '6"');
  dimV(svg, aX - aaP1W/2 - 6, boxT - aaP1H, boxT, -6, '10"');

  // P3 on bottom of Section A-A — ¾" thick × 14" wide (wider than 8" beam by 3" each side)
  const aaP3H = 0.75 * aScale;  // ¾" to scale
  const aaP3W = 14 * aScale;    // 14" wide — 3" wider than beam on each side
  const aaP3Overhang = (aaP3W - aW) / 2; // 3" each side
  aa.appendChild($r(boxL - aaP3Overhang, boxB, aaP3W, aaP3H, 'conn-plate'));
  svg.appendChild($t(aX + aaP3W/2 + 8, boxB + aaP3H/2 + 3, 'P3 (¾"×14")', 'noteb'));
  // Dimension showing P3 is wider than beam
  dimH(svg, boxL - aaP3Overhang, boxL, boxB + aaP3H, 6, '3"');
  dimH(svg, boxR2, boxR2 + aaP3Overhang, boxB + aaP3H, 6, '3"');

  // Stitch weld labels on Section A-A — bold for readability
  svg.appendChild($t(boxL - 22, aY - 2, 'STITCH', 'noteb', 'end'));
  svg.appendChild($t(boxL - 22, aY + 6, 'WELD', 'noteb', 'end'));
  svg.appendChild($t(boxL - 22, aY + 14, '(LIPS)', 'noteb', 'end'));
  svg.appendChild($l(boxL - 18, aY, boxL + gThk, aY, 'dim'));  // leader to lip joint
  svg.appendChild($t(aX, boxT - aaP1H - 22, 'STITCH WELD (FLANGES)', 'noteb', 'middle'));
  svg.appendChild($l(aX, boxT - aaP1H - 18, aX, boxT - 2, 'dim'));  // leader to top flange

  const rbR = (d.rebarBarDia / 2) * aScale;
  const rbInset = rbR + gThk + 1;
  if (p.reinforced) {
    [[boxL + rbInset, boxT + rbInset],
     [boxR2 - rbInset, boxT + rbInset],
     [boxL + rbInset, boxB - rbInset],
     [boxR2 - rbInset, boxB - rbInset]].forEach(function(pt) {
      aa.appendChild($c(pt[0], pt[1], rbR, 'rebar-circ'));
      aa.appendChild($c(pt[0], pt[1], rbR + 2, 'rebar-circ-out'));
    });
    svg.appendChild($t(aX, boxB + 42, '(Reinforced — 4x '+p.rebarSize+' rebar)', 'note', 'middle'));
  } else {
    svg.appendChild($t(aX, boxB + 42, '(Non-reinforced)', 'note', 'middle'));
  }

  aa.appendChild($l(aX, boxT - 10, aX, boxB + 10, 'center'));
  aa.appendChild($l(boxL - 10, aY, boxR2 + 10, aY, 'center'));

  dimH(svg, boxL, boxR2, boxT, -12, '8"');
  dimV(svg, boxR2, boxT, boxB, 12, '14"');
  dimH(svg, boxL, aX, boxB + aaP3H + 18, 8, '4"');
  dimH(svg, aX, boxR2, boxB + aaP3H + 18, 8, '4"');

  svg.appendChild(aa);
  svg.appendChild($t(aX, boxB + 56, 'SECTION A-A', 'ttl', 'middle'));
  svg.appendChild($t(aX, boxB + 64, 'SCALE: ' + fmtScale(aScale), 'note', 'middle'));

  weld(aX, boxT + aH*0.2, aX - 40, boxT - 15, '5/16', {stitch:'3"-36" O.C.', wpsCode:'B', refDir:'left', bothSides:true}, 'aa-cee-stitch');
  if (p.reinforced) {
    weld(boxL + rbInset, boxT + rbInset, aX + 40, boxT - 15, '3/16', {stitch:'3"-36" O.C.', wpsCode:'D', refDir:'right'}, 'aa-rebar');
  }
  layoutEnd('section-aa', _lsSectionAA);

  var _lsDetail1 = layoutStart();
  // DETAIL 1 — P1 CLIP (vertical fin) — 6"×10", 10GA G90
  const d1X = 275, d1Y = zone3Top + 10;
  const d1Scale = 2.2;
  const d1W = 6 * d1Scale, d1H = 10 * d1Scale;
  const d1g = $g('hover-part', 'detP1');
  d1g.appendChild($r(d1X, d1Y, d1W, d1H, 'clip-fill'));
  // Rafter cross-section below the P1 clip (8" wide × 14" tall beam)
  // The P1 sits on TOP of the rafter, so we show the beam below it
  var d1BeamW = 8 * d1Scale;  // 8" beam width
  var d1BeamH = 14 * d1Scale; // 14" beam height
  var d1BeamX = d1X + d1W/2 - d1BeamW/2; // centered under clip
  var d1BeamY = d1Y + d1H;  // beam starts right at bottom of clip
  d1g.appendChild($r(d1BeamX, d1BeamY, d1BeamW, d1BeamH, 'cee'));
  // Flange butt joint line down center of beam
  d1g.appendChild($l(d1BeamX, d1BeamY + d1BeamH/2, d1BeamX + d1BeamW, d1BeamY + d1BeamH/2, 'hidden'));
  // 1/8" fillet weld on BOTH 6" edges where clip meets beam top
  // Left side fillet weld triangle
  d1g.appendChild($p('M '+d1X+' '+(d1Y+d1H)+' L '+(d1X-3)+' '+(d1Y+d1H)+' L '+d1X+' '+(d1Y+d1H-4)+' Z', 'weld-sym-filled'));
  // Right side fillet weld triangle
  d1g.appendChild($p('M '+(d1X+d1W)+' '+(d1Y+d1H)+' L '+(d1X+d1W+3)+' '+(d1Y+d1H)+' L '+(d1X+d1W)+' '+(d1Y+d1H-4)+' Z', 'weld-sym-filled'));
  // Weld labels
  svg.appendChild($t(d1X - 8, d1Y + d1H - 4, '1/8" FILLET', 'note', 'middle'));
  svg.appendChild($t(d1X + d1W + 8, d1Y + d1H - 4, '1/8" FILLET', 'note', 'middle'));

  // 8 holes: 4 columns × 2 rows, 1/4" dia, 3" horiz × 2" vert spacing
  // Holes are in the upper portion (the 10" extension above beam)
  var d1HoleR = (0.25/2) * d1Scale; // 1/4" diameter to scale
  var d1HoleHSpacing = 3 * d1Scale;  // 3" horizontal
  var d1HoleVSpacing = 2 * d1Scale;  // 2" vertical
  var d1GridW = 3 * d1HoleHSpacing;  // 3 gaps = 9" (but plate is 6"... need to check)
  // Actually: 4 columns × 3" spacing = 9" total span. But plate is only 6" wide and 10" tall
  // So the 4 columns go vertically and 2 rows go horizontally. Let me re-read:
  // From user's drawing: 4 rows vertical × 2 columns horizontal, 3" horiz × 2" vert
  // 2 columns at 3" apart, 4 rows at 2" apart
  var d1ColSpacing = 3 * d1Scale; // 3" between 2 columns
  var d1RowSpacing = 2 * d1Scale; // 2" between rows
  var d1GridCX = d1X + d1W/2;
  var d1GridStartY = d1Y + d1H * 0.2; // start holes in upper area
  for (var hRow = 0; hRow < 4; hRow++) {
    for (var hCol = 0; hCol < 2; hCol++) {
      var hx = d1GridCX - d1ColSpacing/2 + hCol * d1ColSpacing;
      var hy = d1GridStartY + hRow * d1RowSpacing;
      d1g.appendChild($c(hx, hy, d1HoleR, 'bolt'));
    }
  }

  // Hole spacing dimensions
  dimH(svg, d1GridCX - d1ColSpacing/2, d1GridCX + d1ColSpacing/2, d1GridStartY - 4, -8, '3"');
  dimV(svg, d1GridCX + d1ColSpacing/2 + 4, d1GridStartY, d1GridStartY + d1RowSpacing, 6, '2" TYP');

  // Dimensions for clip
  dimH(svg, d1X, d1X+d1W, d1Y+d1H - 2, 4, '6"');
  dimV(svg, d1X - 4, d1Y, d1Y+d1H, -12, '10"');
  // Dimensions for beam below
  dimH(svg, d1BeamX, d1BeamX + d1BeamW, d1BeamY + d1BeamH, 8, '8"');
  dimV(svg, d1BeamX + d1BeamW + 2, d1BeamY, d1BeamY + d1BeamH, 8, '14"');
  svg.appendChild(d1g);
  svg.appendChild($t(d1X + d1W/2, d1Y - 12, 'DETAIL 1 — P1 CLIP', 'lblb', 'middle'));
  var d1NotesY = d1BeamY + d1BeamH + 12;
  svg.appendChild($t(d1X + d1W/2, d1NotesY, '10GA x 6" x 10" G90', 'note', 'middle'));
  svg.appendChild($t(d1X + d1W/2, d1NotesY + 8, '1/8" FILLET BOTH 6" EDGES (WPS-C)', 'note', 'middle'));
  svg.appendChild($t(d1X + d1W/2, d1NotesY + 16, '8 HOLES (4x2) 1/4" DIA', 'note', 'middle'));
  svg.appendChild($t(d1X + d1W/2, d1NotesY + 24, 'BEAM: 14x4x10GA BOX', 'note', 'middle'));

  weld(d1X, d1Y + d1H, d1X - 25, d1Y + d1H + 20, '1/8', {wpsCode:'C', refDir:'left'}, 'dt1-p1-weld');
  layoutEnd('detail-1', _lsDetail1);

  var _lsDetail2 = layoutStart();
  // DETAIL 2 — P2 END CAP (only shown if this piece has a P2 end)
  if (d.p2Count > 0) {
  // DETAIL 2 — P2 END CAP (with 9.5" extension above) — 10GA G90
  const d2X = 440, d2Y = zone3Top + 100;
  const d2Scale = 1.5;
  const d2W = 9 * d2Scale;
  const d2BelowH = 0.5 * d2Scale;
  const d2BeamH = 14 * d2Scale;
  const d2AboveH = 9.5 * d2Scale;
  const d2H = d2BelowH + d2BeamH + d2AboveH;
  const d2g = $g('hover-part', 'detP2');

  // P2 cap (full height)
  d2g.appendChild($r(d2X, d2Y - d2AboveH, d2W, d2H, 'cap'));

  // Beam outline inside cap (hidden lines showing where beam sits)
  const beamInD2W = 8 * d2Scale; // 8" beam width
  const beamInD2Y = d2Y;
  d2g.appendChild($r(d2X + (d2W - beamInD2W)/2, beamInD2Y, beamInD2W, d2BeamH, 'hidden'));

  // Weld indicator — only around the beam area (lower portion where P2 is welded to beam)
  // Weld is all-around the beam perimeter, NOT in the upper extension
  d2g.appendChild($r(d2X - 1, beamInD2Y - 1, d2W + 2, d2BeamH + d2BelowH + 2, 'weld'));

  // Dividing line between upper extension and beam area
  d2g.appendChild($l(d2X, d2Y, d2X + d2W, d2Y, 'obj thin'));

  // 8 holes in upper extension (4 rows × 2 cols, 3" horiz × 2" vert)
  var d2HoleR = (0.25/2) * d2Scale;
  var d2HoleSpacingV = 2 * d2Scale;
  var d2HoleSpacingH = 3 * d2Scale;
  var d2HoleCX = d2X + d2W/2;
  var d2HoleStartY = d2Y - d2AboveH + 3 * d2Scale; // edge distance from top
  for (var d2Row = 0; d2Row < 4; d2Row++) {
    for (var d2Col = 0; d2Col < 2; d2Col++) {
      var d2Hx = d2HoleCX - d2HoleSpacingH/2 + d2Col * d2HoleSpacingH;
      var d2Hy = d2HoleStartY + d2Row * d2HoleSpacingV;
      d2g.appendChild($c(d2Hx, d2Hy, d2HoleR, 'bolt'));
    }
  }

  // Dimension lines — positioned to avoid text overlap
  dimH(svg, d2X, d2X+d2W, d2Y + d2BeamH + d2BelowH, 10, '9"');
  dimV(svg, d2X + d2W + 4, d2Y - d2AboveH, d2Y, 8, '9.5"');
  dimV(svg, d2X + d2W + 4, d2Y, d2Y + d2BeamH, 8, '14"');
  dimV(svg, d2X + d2W + 4, d2Y + d2BeamH, d2Y + d2BeamH + d2BelowH, 8, '½"');
  svg.appendChild(d2g);

  // Title and notes — positioned ABOVE the detail to avoid overlap
  svg.appendChild($t(d2X + d2W/2, d2Y - d2AboveH - 14, 'DETAIL 2 — P2 END CAP', 'lblb', 'middle'));
  svg.appendChild($t(d2X + d2W/2, d2Y - d2AboveH - 6, '10GA x 9" x 24" G90', 'note', 'middle'));

  // Notes below — with enough space
  var d2NotesY = d2Y + d2BeamH + d2BelowH + 22;
  svg.appendChild($t(d2X + d2W/2, d2NotesY, '1/4" DIA HOLES (x8)', 'note', 'middle'));
  svg.appendChild($t(d2X + d2W/2, d2NotesY + 8, 'EAVE PURLIN ATTACH', 'note', 'middle'));

  weld(d2X + d2W, beamInD2Y + d2BeamH/2, d2X + d2W + 30, beamInD2Y - 5, '3/16', {allAround:true, wpsCode:'F', refDir:'right'}, 'dt2-cap-weld');
  } // end if p2Count > 0
  layoutEnd('detail-2', _lsDetail2);

  var _lsDetail3 = layoutStart();
  // DETAIL 3 — P3 CONN PLATE
  const d3X = 640, d3Y = zone3Top + 50;
  const d3Scale = 2.0;
  const d3W = 14 * d3Scale, d3H = 26 * d3Scale;
  const d3CX = d3X + d3W/2;
  const d3g = $g('hover-part', 'detP3');
  d3g.appendChild($r(d3X, d3Y, d3W, d3H, 'conn-plate'));
  d3g.appendChild($l(d3CX, d3Y - 5, d3CX, d3Y + d3H + 5, 'center'));
  d3g.appendChild($l(d3X - 5, d3Y + d3H/2, d3X + d3W + 5, d3Y + d3H/2, 'center'));
  const d3BoltR = Math.max((0.9375/2) * d3Scale, 1.5);
  const d3BoltInset = 1.5 * d3Scale;
  const d3BoltXs = [d3X + d3BoltInset, d3X + d3W - d3BoltInset];
  const d3BoltYs = [d3Y + d3BoltInset, d3Y + d3H - d3BoltInset];
  d3BoltXs.forEach(function(bx) {
    d3BoltYs.forEach(function(by) {
      d3g.appendChild($c(bx, by, d3BoltR, 'bolt'));
    });
  });
  dimH(svg, d3X, d3X+d3W, d3Y+d3H, 18, '14"');
  dimV(svg, d3X, d3Y, d3Y+d3H, -18, '26"');
  // Edge distance and spacing dimensions
  dimH(svg, d3X, d3X + d3BoltInset, d3Y + d3H + 26, -8, '1½"');
  dimV(svg, d3X - 22, d3Y + d3BoltInset, d3Y + d3H - d3BoltInset, -8, '23"');
  svg.appendChild(d3g);
  svg.appendChild($t(d3CX, d3Y - 12, 'DETAIL 3 — P3 CONN PLATE', 'lblb', 'middle'));
  svg.appendChild($t(d3CX, d3Y + d3H + 22, '3/4" x 14" x 26" A572 Gr.50', 'note', 'middle'));
  svg.appendChild($t(d3CX, d3Y + d3H + 30, '26" ALONG RAFTER / 14" ACROSS RAFTER', 'note', 'middle'));
  svg.appendChild($t(d3CX, d3Y + d3H + 38, 'WELDED TO BOTTOM OF RAFTER (WPS-F)', 'note', 'middle'));
  svg.appendChild($t(d3CX, d3Y + d3H + 46, 'BOLTS TO COLUMN CAP PLATE IN FIELD', 'note', 'middle'));
  weld(d3X + d3W, d3Y + d3H/2, d3X + d3W + 20, d3Y - 5, '3/16', {allAround:true, wpsCode:'F', refDir:'right'}, 'dt3-plate-weld');
  layoutEnd('detail-3', _lsDetail3);

  var _lsDetail4 = layoutStart();
  // DETAIL 4 — P3-TO-BEAM WELD CROSS-SECTION
  // Shows how the ¾" P3 plate attaches to the bottom of the box beam
  var d4Scale = 2.0;
  var d4CX = 560;  // between Detail 2 and Detail 3
  var d4Y = zone3Top + 16;
  var d4BeamW = 8 * d4Scale;   // 8" beam width — true scale
  var d4BeamH = 14 * d4Scale;  // 14" beam height — FULL HEIGHT true scale
  var d4P3W = 14 * d4Scale;    // 14" plate width
  var d4P3H = 0.75 * d4Scale;  // ¾" plate thickness
  var d4BeamX = d4CX - d4BeamW / 2;
  var d4P3X = d4CX - d4P3W / 2;
  var d4g = $g('hover-part', 'detP3weld');

  // Full beam cross-section — 8" wide × 14" tall
  d4g.appendChild($r(d4BeamX, d4Y, d4BeamW, d4BeamH, 'cee'));
  // Flange butt joint (horizontal dashed center)
  d4g.appendChild($l(d4BeamX, d4Y + d4BeamH/2, d4BeamX + d4BeamW, d4Y + d4BeamH/2, 'hidden'));

  // P3 plate attached to bottom of beam
  d4g.appendChild($r(d4P3X, d4Y + d4BeamH, d4P3W, d4P3H, 'conn-plate'));

  // Fillet welds at the junction — all-around the beam perimeter where P3 meets it
  // Left side fillet (beam corner to plate)
  d4g.appendChild($p('M '+d4BeamX+' '+(d4Y+d4BeamH)+' L '+(d4BeamX-3)+' '+(d4Y+d4BeamH)+' L '+d4BeamX+' '+(d4Y+d4BeamH-5)+' Z', 'weld-sym-filled'));
  // Right side fillet
  d4g.appendChild($p('M '+(d4BeamX+d4BeamW)+' '+(d4Y+d4BeamH)+' L '+(d4BeamX+d4BeamW+3)+' '+(d4Y+d4BeamH)+' L '+(d4BeamX+d4BeamW)+' '+(d4Y+d4BeamH-5)+' Z', 'weld-sym-filled'));
  // Overhang fillet (left)
  d4g.appendChild($p('M '+d4P3X+' '+(d4Y+d4BeamH)+' L '+d4P3X+' '+(d4Y+d4BeamH+d4P3H+3)+' L '+(d4P3X+4)+' '+(d4Y+d4BeamH)+' Z', 'weld-sym-filled'));
  // Overhang fillet (right)
  d4g.appendChild($p('M '+(d4P3X+d4P3W)+' '+(d4Y+d4BeamH)+' L '+(d4P3X+d4P3W)+' '+(d4Y+d4BeamH+d4P3H+3)+' L '+(d4P3X+d4P3W-4)+' '+(d4Y+d4BeamH)+' Z', 'weld-sym-filled'));

  // Center lines
  d4g.appendChild($l(d4CX, d4Y - 5, d4CX, d4Y + d4BeamH + d4P3H + 8, 'center'));
  d4g.appendChild($l(d4P3X - 5, d4Y + d4BeamH/2, d4P3X + d4P3W + 5, d4Y + d4BeamH/2, 'center'));

  // Dimensions
  dimH(svg, d4BeamX, d4BeamX + d4BeamW, d4Y, -10, '8"');
  dimV(svg, d4BeamX - 6, d4Y, d4Y + d4BeamH, -10, '14"');
  dimH(svg, d4P3X, d4P3X + d4P3W, d4Y + d4BeamH + d4P3H, 12, '14"');
  dimV(svg, d4P3X + d4P3W + 4, d4Y + d4BeamH, d4Y + d4BeamH + d4P3H, 8, '¾"');
  // Overhang dims
  var d4Overhang = (d4P3W - d4BeamW) / 2;
  dimH(svg, d4P3X, d4BeamX, d4Y + d4BeamH + d4P3H + 20, -6, '3"');
  dimH(svg, d4BeamX + d4BeamW, d4P3X + d4P3W, d4Y + d4BeamH + d4P3H + 20, -6, '3"');

  svg.appendChild(d4g);

  // Weld callout
  weld(d4BeamX + d4BeamW + 2, d4Y + d4BeamH, d4CX + d4P3W/2 + 25, d4Y + d4BeamH - 15, '3/16', {allAround:true, wpsCode:'F', refDir:'right'}, 'dt4-p3-weld');

  // Title and notes
  svg.appendChild($t(d4CX, d4Y - 18, 'DETAIL 4 — P3 WELD', 'lblb', 'middle'));
  svg.appendChild($t(d4CX, d4Y + d4BeamH + d4P3H + 34, '3/16" ALL-AROUND (WPS-F)', 'note', 'middle'));
  svg.appendChild($t(d4CX, d4Y + d4BeamH + d4P3H + 42, '3" OVERHANG EACH SIDE', 'note', 'middle'));
  svg.appendChild($t(d4CX, d4Y + d4BeamH + d4P3H + 50, 'MT INSPECT (CRITICAL)', 'note', 'middle'));
  layoutEnd('detail-4', _lsDetail4);

  // ════════════════════════════════════════════════════════════════════
  // DETAIL 5 — P5 BEAM SPLICE (BS101) — only when spliced rafter
  // ════════════════════════════════════════════════════════════════════
  if (d.p5Count > 0 || d.needsSplice) {
    var _lsDetail5 = layoutStart();
    var d5Scale = 1.8;
    var d5CX = 420;
    var d5Y = zone3Top + 16;
    // Splice plate wraps the beam: U-shape cross-section
    var d5BeamW = 8 * d5Scale;    // 8" beam width
    var d5BeamH = 14 * d5Scale;   // 14" beam height
    var d5PlateThk = 0.134 * d5Scale * 8; // 10GA ≈ 0.134", exaggerated for visibility
    var d5PlateW = 20.75 * d5Scale; // 20¾" plate width (wraps both sides + bottom)
    var d5BeamX = d5CX - d5BeamW / 2;
    var d5BeamY = d5Y;

    // Beam cross-section (same as Section A-A style)
    svg.appendChild($r(d5BeamX, d5BeamY, d5BeamW, d5BeamH, 'obj thick'));
    // Center line
    svg.appendChild($l(d5CX, d5Y - 5, d5CX, d5Y + d5BeamH + 15, 'center'));

    // Splice plate U-shape: left side, bottom, right side
    var spGap = 1;  // small gap to show it's a separate piece
    var spSideH = d5BeamH * 0.85;  // splice plate covers most of the web height
    // Left plate side
    svg.appendChild($r(d5BeamX - d5PlateThk - spGap, d5BeamY + d5BeamH - spSideH, d5PlateThk, spSideH, 'conn-plate'));
    // Right plate side
    svg.appendChild($r(d5BeamX + d5BeamW + spGap, d5BeamY + d5BeamH - spSideH, d5PlateThk, spSideH, 'conn-plate'));
    // Bottom plate (connects both sides)
    svg.appendChild($r(d5BeamX - d5PlateThk - spGap, d5BeamY + d5BeamH + spGap, d5BeamW + 2*d5PlateThk + 2*spGap, d5PlateThk, 'conn-plate'));

    // Tek screw holes (4 rows × 6 cols on each side, shown as small circles)
    var tekRows = 4, tekCols = 6;
    var tekStartY = d5BeamY + d5BeamH - spSideH + spSideH * 0.15;
    var tekEndY = d5BeamY + d5BeamH - spSideH * 0.1;
    var tekRowSpacing = (tekEndY - tekStartY) / (tekRows - 1);
    var tekColSpacing = 3 * d5Scale; // 3" spacing
    // Left side tek screws
    for (var tr = 0; tr < tekRows; tr++) {
      for (var tc = 0; tc < tekCols; tc++) {
        var ty = tekStartY + tr * tekRowSpacing;
        var tx = d5BeamX - d5PlateThk/2 - spGap;
        svg.appendChild($c(tx, ty, 0.8, 'bolt'));
      }
    }
    // Right side tek screws
    for (var tr2 = 0; tr2 < tekRows; tr2++) {
      for (var tc2 = 0; tc2 < tekCols; tc2++) {
        var ty2 = tekStartY + tr2 * tekRowSpacing;
        var tx2 = d5BeamX + d5BeamW + d5PlateThk/2 + spGap;
        svg.appendChild($c(tx2, ty2, 0.8, 'bolt'));
      }
    }

    // Field weld symbols at top and bottom flanges
    weld(d5CX, d5BeamY, d5CX + d5BeamW/2 + 25, d5BeamY - 15, '3/16', {stitch:'FIELD', wpsCode:'F', refDir:'right'}, 'dt5-top-weld');
    weld(d5CX, d5BeamY + d5BeamH + d5PlateThk + spGap, d5CX + d5BeamW/2 + 25, d5BeamY + d5BeamH + 20, '3/16', {stitch:'FIELD', wpsCode:'F', refDir:'right'}, 'dt5-bot-weld');

    // Dimensions
    dimH(svg, d5BeamX - d5PlateThk - spGap, d5BeamX + d5BeamW + d5PlateThk + spGap, d5BeamY + d5BeamH + d5PlateThk + 14, 8, '20¾"');
    dimV(svg, d5BeamX - d5PlateThk - spGap - 10, d5BeamY + d5BeamH - spSideH, d5BeamY + d5BeamH, -8, '18"');
    dimV(svg, d5BeamX + d5BeamW + d5PlateThk + spGap + 10, d5BeamY, d5BeamY + d5BeamH, 8, '14"');

    // Labels
    svg.appendChild($t(d5CX, d5Y - 18, 'DETAIL 5 — P5 SPLICE (BS101)', 'lblb', 'middle'));
    svg.appendChild($t(d5CX, d5BeamY + d5BeamH + d5PlateThk + 28, '10GA A36 G90 — BEND UP 90°', 'note', 'middle'));
    svg.appendChild($t(d5CX, d5BeamY + d5BeamH + d5PlateThk + 36, '24 TEK SCREWS PER SIDE (3/16")', 'note', 'middle'));
    svg.appendChild($t(d5CX, d5BeamY + d5BeamH + d5PlateThk + 44, 'FIELD WELD TOP & BOTTOM FLANGES', 'note', 'middle'));

    layoutEnd('detail-5', _lsDetail5);
  }

  var _lsBom = layoutStart();
  // ════════════════════════════════════════════════════════════════════
  // ZONE 4: BOM TABLE — aligned with Zone 3
  // ════════════════════════════════════════════════════════════════════
  const bomX = 800, bomStartY = zone3Top + 10;
  const bomColW = [22, 18, 80, 68, 48, 30];
  const bomTotalW = bomColW.reduce(function(a,b){return a+b;},0);
  const bomRowH = 10;

  svg.appendChild($r(bomX, bomStartY, bomTotalW, bomRowH, 'obj med'));
  var bomHeaders = ['Mk','Qty','Description','Size','Material','Wt'];
  var bx2 = bomX;
  bomHeaders.forEach(function(h,i) {
    svg.appendChild($t(bx2+2, bomStartY+7, h, 'noteb'));
    bx2 += bomColW[i];
  });

  var bomRows = [
    [rafterMark, '2', 'CEE (Box Beam)', '14x4x10GA x ' + fmtFtIn(d.cutLengthIn), 'Gr.80 G90', Math.round(d.ceeWeight)+'#'],
    ['P1', String(d.p1Count), 'Clip Fin (Shop)', '10GA(0.135") 6"x10"', 'G90 Galv', Math.round(d.p1Weight)+'#'],
  ];
  if (d.p2Count > 0) {
    bomRows.push(['P2', String(d.p2Count), 'End Cap', '10GA(0.135") 9"x24"', 'G90 Galv', Math.round(d.p2Weight)+'#']);
  }
  if (d.p6Count > 0) {
    bomRows.push(['P6', String(d.p6Count), 'End Plate', '10GA(0.135") 9"x15"', 'G90 Galv', Math.round(d.p6Weight)+'#']);
  }
  if (d.p3CountPiece > 0) {
    bomRows.push(['P3', String(d.p3CountPiece), 'Conn Plate', '3/4"x14"x26"', 'A572 Gr.50', Math.round(d.p3Weight)+'#']);
  }
  if (d.p5Count > 0) {
    bomRows.push(['P5', String(d.p5Count), 'Splice Plate (BS101)', '10GA x 20-3/4"x18"', 'A36 G90', Math.round(d.p5Weight)+'#']);
  }
  if (p.reinforced && d.rebarStickPositions && d.rebarStickPositions.length > 0) {
    // Show individual stick entries — each stick × 4 bars
    var stickLengths = {};
    d.rebarStickPositions.forEach(function(stick) {
      var key = fmtFtIn(stick.lengthIn);
      stickLengths[key] = (stickLengths[key] || 0) + 1;
    });
    Object.keys(stickLengths).forEach(function(lenStr) {
      var count = stickLengths[lenStr];
      var totalQty = count * 4; // 4 bars per rafter
      bomRows.push(['RB', String(totalQty), p.rebarSize + ' Rebar', lenStr + ' EA', 'A615 Gr.60', '—']);
    });
    bomRows.push(['', '', '', 'REBAR TOTAL', '', Math.round(d.rebarTotalWeight)+'#']);
  }
  var boltCount = d.p3CountPiece * 4;
  if (boltCount > 0) bomRows.push(['BL', String(boltCount), 'Bolt+Nut+Wash', '3/4"x3" A325-N', 'A325-N', Math.round(boltCount*0.5)+'#']);

  bomRows.forEach(function(row, ri) {
    var ry = bomStartY + bomRowH * (ri+1);
    svg.appendChild($l(bomX, ry, bomX+bomTotalW, ry, 'dim'));
    var rx = bomX;
    row.forEach(function(cell, ci) {
      svg.appendChild($t(rx+2, ry+7, cell, 'note'));
      rx += bomColW[ci];
    });
  });

  svg.appendChild($r(bomX, bomStartY, bomTotalW, bomRowH*(bomRows.length+1), 'obj hair'));
  svg.appendChild($t(bomX+bomTotalW/2, bomStartY-8, 'BILL OF MATERIALS', 'noteb', 'middle'));

  var bomEndY = bomStartY + bomRowH * (bomRows.length + 1) + 4;
  svg.appendChild($t(bomX + 2, bomEndY + 6, 'TOTAL WEIGHT: ' + d.totalWeight.toLocaleString() + ' lbs', 'note'));
  layoutEnd('bom-table', _lsBom);

  // ════════════════════════════════════════════════════════════════════
  // ZONE 5: TITLE BLOCK (y=680 to y=815)
  // ════════════════════════════════════════════════════════════════════
  var ty = 680, th = 135, tx = 20, tw = 1060;
  svg.appendChild($r(tx,ty,tw,th,'obj thick'));

  var c1=tx, c2=tx+220, c3=c2+240, c4=c3+160, c5=c4+200;
  [c2,c3,c4,c5].forEach(function(cx) { svg.appendChild($l(cx,ty,cx,ty+th,'obj med')); });

  svg.appendChild($t(c1+110, ty+20, 'Structures America', 'lblb', 'middle'));
  svg.appendChild($t(c1+110, ty+34, '14369 FM 1314', 'lbl', 'middle'));
  svg.appendChild($t(c1+110, ty+46, 'Conroe, TX 77302', 'lbl', 'middle'));
  svg.appendChild($t(c1+110, ty+58, '505-270-1877', 'lbl', 'middle'));
  svg.appendChild($l(c1,ty+68,c2,ty+68,'obj hair'));
  svg.appendChild($t(c1+8, ty+80, 'DESIGN/REVIEW AUTHORITY:', 'noteb'));
  svg.appendChild($t(c1+8, ty+92, 'PLEASE REVIEW THIS DRAWING CAREFULLY', 'note'));
  svg.appendChild($t(c1+8, ty+102, 'We assume NO responsibility for the accuracy', 'note'));
  svg.appendChild($t(c1+8, ty+112, 'of information in the contract documents.', 'note'));

  var checkedName = drawingState.checked ? drawingState.checkedBy : '\u2014';
  var checkedDate = drawingState.checked ? drawingState.checkedDate || '' : '\u2014';
  var curRev = drawingState.revision;
  var pRows = [['PROJECT:', projName],['CUSTOMER:', customer],
    ['JOB:', jobNum],['DWG #:', drawingNum],['DATE:', new Date().toLocaleDateString()],
    ['DRAWN:', drawnBy],['CHECKED:', checkedName + (checkedDate !== '\u2014' ? ' ('+checkedDate+')' : '')],
    ['SHEET:', '1 OF 1'],['REV:', String(curRev)]];
  pRows.forEach(function(pair,i) {
    var py = ty+12+i*13;
    svg.appendChild($t(c2+6, py, pair[0], 'note'));
    svg.appendChild($t(c2+55, py, pair[1], 'lbl'));
    if(i<pRows.length-1) svg.appendChild($l(c2,py+3,c3,py+3,'dim'));
  });

  svg.appendChild($t(c3+80, ty+45, 'RAFTER', 'ttl'));
  svg.appendChild($e('text',{x:c3+80,y:ty+85,class:'ttl','text-anchor':'middle','font-size':'28px'},rafterMark));

  svg.appendChild($e('rect',{x:c4,y:ty,width:200,height:16,fill:'#333',stroke:'#333'}));
  svg.appendChild($t(c4+8,ty+12,'DATE','note'));
  svg.appendChild($t(c4+50,ty+12,'REV','note'));
  svg.appendChild($t(c4+80,ty+12,'DESCRIPTION','note'));
  [svg.lastChild, svg.lastChild.previousSibling, svg.lastChild.previousSibling.previousSibling].forEach(function(el) {
    if (el && el.setAttribute) el.setAttribute('fill', '#FFF');
  });

  drawingState.history.forEach(function(h,i) {
    var ry2 = ty+16+14*(i+1);
    svg.appendChild($t(c4+8,ry2,h.date,'note'));
    svg.appendChild($t(c4+52,ry2,String(h.rev),'note'));
    svg.appendChild($t(c4+80,ry2,h.desc + (h.by ? ' \u2014 '+h.by : ''),'note'));
  });

  svg.appendChild($e('rect',{x:c5,y:ty,width:tw-(c5-tx),height:16,fill:'#333',stroke:'#333'}));
  svg.appendChild($t(c5+(tw-(c5-tx))/2, ty+12, 'PROJECT NOTES', 'note', 'middle'));
  svg.lastChild.setAttribute('fill', '#FFF');

  ['MATERIAL: CEE Gr.80 G90 / P1,P2: 10GA(0.135") G90 / P3: A572 Gr.50',
   'SURF PREP: '+surfPrep+' / COLD GALV 3.0 MIL DFT',
   'HOLES: 15/16" DIA STD \u2014 BOLTS: A325-N BEARING TYPE, SNUG TIGHT',
   'CAMBER: NONE',
   'REBAR PREHEAT: 300°F MIN (AWS D1.4) WHEN CHEM UNKNOWN',
   'PURLINS: '+d.p1Count+' @ '+fmtFtIn(d.p1ActualSpacingIn)+' O.C. (BOTH ENDS)',
   'FAB: AISC 360-22 / AWS D1.1',
   'WELD INSP: VT ALL / MT ON P3 & P2 (CRITICAL)',
   'WELD SCHEDULE:',
   '  B: CEE stitch 5/16 \u2014 3"@36 (1"@6 ends)',
   '  C: P1 clip 1/8" fillet both sides (shop)',
   '  D: Rebar 5/16 stitch 3"@3\' O.C.',
   '  F: End cap/conn plate 3/16 all-around',
   'SHOP ASSY: 1)Rebar→CEE 2)Box weld 3)P2 caps 4)P3 plate 5)P1 clips',
   'FIELD: Tek screw purlins to P1 clips',
   'DO NOT SCALE DRAWING',
   'PIECE MARK = ERECTION MARK',
   'TOL: LENGTH \u00B11/16" / HOLES \u00B11/32"'].forEach(function(n,i) {
    svg.appendChild($t(c5+6, ty+26+i*8, n, 'note'));
  });

  svg.appendChild($t(480, ty-8, 'Rafter Shop Drawing - ' + rafterMark, 'ttl'));

  document.getElementById('fWt').textContent = d.totalWeight.toLocaleString() + ' lbs';
  document.getElementById('fLen').textContent = fmtFtIn(d.cutLengthIn);
  document.getElementById('fP1').textContent = d.p1Count + ' @ ' + fmtFtIn(d.p1ActualSpacingIn) + ' O.C.';
  document.getElementById('fRebar').textContent = p.reinforced ? d.rebarSticks + ' sticks x4 (' + p.rebarSize + ')' : '0 (non-reinforced)';
  document.getElementById('fPurlin').textContent = p.purlinType;
  document.getElementById('fBackWall').textContent = p.backWall ? 'Yes' : 'No';
  document.getElementById('fP3').textContent = d.p3Count;

  updateBOM(p, d, rafterMark);
  setupTips(p, d);
  drawSpanDiagram(p, d);

  // Render custom (user-added) welds — piece-relative coordinates
  customWelds.forEach(function(cw) {
    if (deletedWelds.indexOf(cw.id) !== -1) return;  // skip deleted custom welds
    // Convert piece-relative inches to absolute SVG pixels
    var cwAx, cwAy;
    if (cw.anchorIn !== undefined) {
      // New format: piece-relative
      cwAx = beamL + cw.anchorIn * sc;
      cwAy = beamY + (cw.anchorVIn || 0) * sc;
    } else {
      // Legacy format: absolute SVG coords (backward compat)
      cwAx = cw.ax;
      cwAy = cw.ay;
    }
    var cwRouteX = cwAx + (cw.routeDx || 0);
    var cwRouteY = cwAy + (cw.routeDy || -30);
    currentWeldDefs.push({ id: cw.id, ax: cwAx, ay: cwAy, routeX: cwRouteX, routeY: cwRouteY, size: cw.size, opts: {...cw.opts} });
    awsWeld(svg, cwAx, cwAy, cwRouteX, cwRouteY, cw.size, cw.opts, cw.id);
  });

  // Render annotations as interactive groups
  annotations.forEach(function(a, idx) {
    var ag = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    ag.setAttribute('class', 'anno-group' + (selectedAnnotation === idx ? ' anno-selected' : ''));
    ag.setAttribute('data-anno-idx', idx);
    // Approximate text bbox for hit target (8px per char width, 10px height)
    var estW = Math.max(a.text.length * 5.5, 20);
    var bgRect = $e('rect', { x: a.x - 2, y: a.y - 9, width: estW + 4, height: 12, class: 'anno-bg' });
    ag.appendChild(bgRect);
    ag.appendChild($t(a.x, a.y, a.text, 'lblb'));
    // Show delete hint on selected annotation in annotate mode
    if (annotateMode && selectedAnnotation === idx) {
      ag.appendChild($t(a.x, a.y + 10, '[Del] delete  [Dbl-click] edit', 'anno-hint'));
    }
    svg.appendChild(ag);
  });
}

// ═══════════════════════════════════════════════
// SPAN DIAGRAM — column auto-calc visualization
// ═══════════════════════════════════════════════
function drawSpanDiagram(p, d) {
  var svg = document.getElementById('spanSvg');
  if (!svg) return;
  svg.innerHTML = '';
  var ns = 'http://www.w3.org/2000/svg';

  var totalIn = d.totalCutLengthIn;
  var totalFt = d.totalCutLengthFt;
  var padL = 60, padR = 40;
  var w = 900 - padL - padR;  // available width for rafter line
  var midY = 36;

  function sc(inches) { return padL + (inches / totalIn) * w; }
  function ft(inches) { return Math.round(inches / 12 * 10) / 10; }

  // Helper to create SVG elements
  function el(tag, attrs) {
    var e = document.createElementNS(ns, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    return e;
  }

  // Title
  svg.appendChild(el('text', {x: 4, y: 10, fill: '#94A3B8', 'font-size': '8', 'font-family': 'monospace'}));
  svg.lastChild.textContent = 'SPAN DIAGRAM';

  // Column mode info
  var colMode = document.getElementById('inputColMode').value;
  var bldgWidth = parseFloat(document.getElementById('inputWidth').value) || 40;
  var autoCount = bldgWidth <= 45 ? 1 : Math.max(2, Math.ceil(bldgWidth / 60));
  var modeLabel = colMode === 'auto' ? 'AUTO' : (colMode === 'spacing' ? 'SPACING ' + p.colSpacing + '\'' : 'MANUAL');
  var infoText = 'Bldg: ' + bldgWidth + '\' | Rafter: ' + ft(totalIn) + '\' | ' + modeLabel + ': ' + d.p3Count + ' col' + (d.p3Count > 1 ? 's' : '');
  if (colMode !== 'auto') infoText += ' (auto=' + autoCount + ')';
  if (p.backWall) infoText += ' | BACK WALL';
  svg.appendChild(el('text', {x: 4, y: 20, fill: '#F6AE2D', 'font-size': '8', 'font-family': 'monospace', 'font-weight': 'bold'}));
  svg.lastChild.textContent = infoText;

  // Rafter line
  svg.appendChild(el('line', {x1: sc(0), y1: midY, x2: sc(totalIn), y2: midY, stroke: '#475569', 'stroke-width': '3'}));

  // End supports (triangles)
  [sc(0), sc(totalIn)].forEach(function(x) {
    var pts = (x-5)+','+(midY+4)+' '+(x+5)+','+(midY+4)+' '+x+','+(midY+14);
    svg.appendChild(el('polygon', {points: pts, fill: '#64748B', stroke: '#94A3B8', 'stroke-width': '0.5'}));
  });
  // End labels
  svg.appendChild(el('text', {x: sc(0), y: midY - 6, fill: '#94A3B8', 'font-size': '7', 'font-family': 'monospace', 'text-anchor': 'middle'}));
  svg.lastChild.textContent = 'L END';
  svg.appendChild(el('text', {x: sc(totalIn), y: midY - 6, fill: '#94A3B8', 'font-size': '7', 'font-family': 'monospace', 'text-anchor': 'middle'}));
  svg.lastChild.textContent = p.backWall ? 'BACK WALL' : 'R END';

  // Column positions (from calc)
  var colPositions = d.p3Positions || [];
  colPositions.forEach(function(posIn, ci) {
    var x = sc(posIn);
    // Column marker — inverted triangle + vertical line
    svg.appendChild(el('line', {x1: x, y1: midY - 12, x2: x, y2: midY + 4, stroke: '#F6AE2D', 'stroke-width': '1.5'}));
    var pts = (x-4)+','+(midY+4)+' '+(x+4)+','+(midY+4)+' '+x+','+(midY+14);
    svg.appendChild(el('polygon', {points: pts, fill: '#F6AE2D', stroke: '#B45309', 'stroke-width': '0.5'}));
    // Column label
    svg.appendChild(el('text', {x: x, y: midY - 14, fill: '#F6AE2D', 'font-size': '7', 'font-family': 'monospace', 'text-anchor': 'middle', 'font-weight': 'bold'}));
    svg.lastChild.textContent = 'COL ' + (ci + 1);
  });

  // Span dimensions — between each pair of supports
  var supports = [0].concat(colPositions).concat([totalIn]);
  supports.sort(function(a, b) { return a - b; });
  var dimY = midY + 22;
  var maxSpanFt = 60;

  for (var i = 0; i < supports.length - 1; i++) {
    var leftIn = supports[i];
    var rightIn = supports[i + 1];
    var spanIn = rightIn - leftIn;
    var spanFt = spanIn / 12;
    var x1 = sc(leftIn);
    var x2 = sc(rightIn);
    var cx = (x1 + x2) / 2;
    var ok = spanFt <= maxSpanFt + 0.1;

    // Span bracket
    svg.appendChild(el('line', {x1: x1 + 2, y1: dimY, x2: x2 - 2, y2: dimY, stroke: ok ? '#22C55E' : '#EF4444', 'stroke-width': '1'}));
    svg.appendChild(el('line', {x1: x1 + 2, y1: dimY - 3, x2: x1 + 2, y2: dimY + 3, stroke: ok ? '#22C55E' : '#EF4444', 'stroke-width': '1'}));
    svg.appendChild(el('line', {x1: x2 - 2, y1: dimY - 3, x2: x2 - 2, y2: dimY + 3, stroke: ok ? '#22C55E' : '#EF4444', 'stroke-width': '1'}));

    // Span label
    var label = ft(spanIn) + '\'';
    var color = ok ? '#22C55E' : '#EF4444';
    svg.appendChild(el('text', {x: cx, y: dimY - 2, fill: color, 'font-size': '8', 'font-family': 'monospace', 'text-anchor': 'middle', 'font-weight': 'bold'}));
    svg.lastChild.textContent = label;

    // Warning icon if over limit
    if (!ok) {
      svg.appendChild(el('text', {x: cx + (label.length * 2.5) + 6, y: dimY - 2, fill: '#EF4444', 'font-size': '9', 'font-family': 'monospace'}));
      svg.lastChild.textContent = '\u26A0';
    }
  }
}

// Update BOM sidebar with current part descriptions
function updateBOM(p, d, rafterMark) {
  var tb = document.getElementById('bomTB');
  if (!tb) return;
  tb.innerHTML = '';

  var rows = [];

  // B1 Rafter - 2x CEE beam
  rows.push({
    mk: rafterMark || 'B1',
    qty: 2,
    desc: 'Box Beam',
    size: 'CEE 14x4x10GA',
    mat: 'Gr.80 G90 Galv',
    wt: Math.round(d.ceeWeight)
  });

  // P1 Clips
  if (d.p1Count > 0) {
    rows.push({
      mk: 'P1',
      qty: d.p1Count,
      desc: 'Clip Fin',
      size: '10GA x 6" x 10"',
      mat: 'G90 Galv',
      wt: Math.round(d.p1Weight)
    });
  }

  // P2 End Caps (piece-specific count)
  if (d.p2Count > 0) {
    rows.push({
      mk: 'P2',
      qty: d.p2Count,
      desc: 'End Cap',
      size: '10GA x 9" x 24"',
      mat: 'G90 Galv',
      wt: Math.round(d.p2Weight)
    });
  }

  // P6 End Plates (angled purlin configuration)
  if (d.p6Count > 0) {
    rows.push({
      mk: 'P6',
      qty: d.p6Count,
      desc: 'End Plate',
      size: '10GA x 9" x 15"',
      mat: 'G90 Galv',
      wt: Math.round(d.p6Weight)
    });
  }

  // P3 Connection Plates (piece-specific)
  if (d.p3CountPiece > 0) {
    rows.push({
      mk: 'P3',
      qty: d.p3CountPiece,
      desc: 'Connection Plate',
      size: '14"x26"x3/4"',
      mat: 'A572 Gr.50',
      wt: Math.round(d.p3Weight)
    });
  }

  // P5 Splice Plates (piece-specific)
  if (d.p5Count > 0) {
    rows.push({
      mk: 'P5',
      qty: d.p5Count,
      desc: 'Splice Plate (BS101)',
      size: '10GA x 20-3/4" x 18"',
      mat: 'A36 G90',
      wt: Math.round(d.p5Weight)
    });
  }

  // Rebar (if reinforced) — individual stick entries
  if (p.reinforced && d.rebarStickPositions && d.rebarStickPositions.length > 0) {
    var stickLens = {};
    d.rebarStickPositions.forEach(function(stick) {
      var key = fmtFtIn(stick.lengthIn);
      stickLens[key] = (stickLens[key] || 0) + 1;
    });
    Object.keys(stickLens).forEach(function(lenStr) {
      var count = stickLens[lenStr];
      rows.push({
        mk: 'RB',
        qty: count * 4,
        desc: p.rebarSize + ' Rebar',
        size: lenStr + ' EA',
        mat: 'A615 Gr.60',
        wt: Math.round(d.rebarTotalWeight / d.rebarStickPositions.length * count)
      });
    });
  }

  // Bolts (4 per P3)
  var boltQty = (d.p3CountPiece || 0) * 4;
  if (boltQty > 0) {
    rows.push({
      mk: 'BL',
      qty: boltQty,
      desc: 'Bolt',
      size: '3/4" dia, 2" lg',
      mat: 'A325-N',
      wt: Math.round(boltQty * 0.5)
    });
  }

  // Populate table
  var totalWt = 0;
  rows.forEach(function(r) {
    var tr = document.createElement('tr');
    tr.innerHTML = '<td>' + (r.mk || '') + '</td><td>' + r.qty + '</td><td>' + r.desc + '</td>' +
                   '<td>' + r.size + '</td><td>' + r.mat + '</td><td>' + r.wt + ' lbs</td>';
    tb.appendChild(tr);
    totalWt += r.wt;
  });

  // Total row
  var tr = document.createElement('tr');
  tr.style.fontWeight = 'bold';
  tr.style.borderTop = '1px solid #64748B';
  tr.innerHTML = '<td colspan="5" style="text-align:right;">TOTAL WEIGHT:</td><td>' + totalWt + ' lbs</td>';
  tb.appendChild(tr);

  // Update total display
  var totalSpan = document.getElementById('bomTotal');
  if (totalSpan) totalSpan.textContent = totalWt + ' lbs';
}

// Setup tooltips for parts
function setupTips(p, d) {
  var tip = document.getElementById('tip');
  if (!tip) return;

  var parts = {
    'rafter': 'Box Beam - 2x CEE 14x4x10GA Gr.80 G90, Length: ' + fmtFtIn(d.cutLengthIn) + ', Weight: ' + Math.round(d.ceeWeight) + ' lbs',
    'clips': 'P1 Clips - ' + d.p1Count + 'x vertical fins, 10GA x 6"x10" G90, Shop weld WPS-C, 8 holes (4x2)',
    'endcaps': d.p6Count > 0 ? 'P6 End Plates - ' + d.p6Count + 'x, 10GA x 9"x15" G90, \u00BD" overhang, Weld all-around WPS-F' : 'P2 End Caps - ' + d.p2Count + 'x, 10GA x 9"x24" G90, 9.5" ext above, Weld all-around WPS-F',
    'connplate': 'P3 Connection Plate - ' + d.p3Count + 'x, 3/4"x14"x26" A572 Gr.50, Welded to bottom WPS-F',
    'secAA': 'Section A-A - Box beam cross-section, webs=sides, flanges=top/bottom, Stitch weld lips',
    'detP1': 'P1 Clip Detail - 6"x10" fin, 1/8" fillet weld, typical installation',
    'detP2': d.p6Count > 0 ? 'P6 End Plate Detail - 9"x15" plate, \u00BD" overhang all sides' : 'P2 End Cap Detail - 9"x24" plate, 9.5" above beam, eave purlin attachment',
    'detP3': 'P3 Connection Plate Detail - 3/4" thick, bolted to bottom, A325 bolts'
  };

  Object.keys(parts).forEach(function(partId) {
    var els = document.querySelectorAll('.' + partId);
    els.forEach(function(el) {
      el.addEventListener('mouseover', function() {
        tip.innerHTML = '<span class="k">Part:</span> <span class="v">' + parts[partId] + '</span>';
        tip.style.display = 'block';
      });
      el.addEventListener('mousemove', function(e) {
        tip.style.left = (e.clientX + 12) + 'px';
        tip.style.top = (e.clientY + 12) + 'px';
      });
      el.addEventListener('mouseout', function() {
        tip.style.display = 'none';
      });
    });
  });
}

function openWeldEditor(weldId) {
  selectedWeldId = weldId;
  var ov = weldOverrides[weldId] || {};
  document.getElementById('weSize').value = ov.size || '3/16';
  document.getElementById('weWps').value = ov.wpsCode || '';
  document.getElementById('weStitch').value = ov.stitch || '';
  document.getElementById('weRefDir').value = ov.refDir || 'right';
  document.getElementById('weRotation').value = ov.rotation || 0;
  document.getElementById('weAllAround').checked = ov.allAround || false;
  document.getElementById('weBothSides').checked = ov.bothSides || false;
  document.getElementById('weldEditor').classList.add('show');
  draw();
}

function liveApply() {
  if (!selectedWeldId) return;
  pushUndoDebounced();
  if (!weldOverrides[selectedWeldId]) weldOverrides[selectedWeldId] = {};
  var ov = weldOverrides[selectedWeldId];
  ov.size = document.getElementById('weSize').value;
  ov.wpsCode = document.getElementById('weWps').value;
  ov.stitch = document.getElementById('weStitch').value;
  ov.refDir = document.getElementById('weRefDir').value;
  ov.rotation = parseInt(document.getElementById('weRotation').value) || 0;
  ov.allAround = document.getElementById('weAllAround').checked;
  ov.bothSides = document.getElementById('weBothSides').checked;
  document.getElementById('btnWeldReset').style.display = 'inline-block';
  draw();
}

['weSize','weWps','weStitch'].forEach(function(id) {
  document.getElementById(id).addEventListener('input', liveApply);
});
['weRefDir'].forEach(function(id) {
  document.getElementById(id).addEventListener('change', liveApply);
});
document.getElementById('weRotation').addEventListener('input', liveApply);
document.getElementById('weAllAround').addEventListener('change', liveApply);
document.getElementById('weBothSides').addEventListener('change', liveApply);

function applyWeldEdit() {
  liveApply();
  var btn = document.querySelector('.we-apply-btn');
  if (btn) { btn.textContent = '\u2713 Applied'; setTimeout(function(){ btn.textContent = '\u2713 Apply'; }, 800); }
}

function resetSelectedWeld() {
  if (!selectedWeldId) return;
  pushUndo();
  delete weldOverrides[selectedWeldId];
  openWeldEditor(selectedWeldId);
  draw();
}

function closeWeldEditor() {
  selectedWeldId = null;
  document.getElementById('weldEditor').classList.remove('show');
  draw();
}

function resetAllWeldOverrides() {
  if (!confirm('Reset ALL weld & label positions, restore deleted welds, and remove custom welds? (Layout moves are separate)')) return;
  pushUndo();
  Object.keys(weldOverrides).forEach(function(k) { delete weldOverrides[k]; });
  Object.keys(labelOverrides).forEach(function(k) { delete labelOverrides[k]; });
  customWelds = [];
  deletedWelds = [];
  selectedWeldId = null;
  document.getElementById('weldEditor').classList.remove('show');
  document.getElementById('btnWeldReset').style.display = 'none';
  document.getElementById('btnDeleteWeld').style.display = 'none';
  draw();
}

// Toggle weld edit mode
function toggleWeldEditMode() {
  weldEditMode = !weldEditMode;
  addWeldMode = false;
  document.querySelector('.drawing-sheet').classList.remove('add-weld-mode');
  var btn = document.getElementById('btnWeldEdit');
  var expBtn = document.getElementById('btnExportWelds');
  var addBtn = document.getElementById('btnAddWeld');
  var delBtn = document.getElementById('btnDeleteWeld');
  if (weldEditMode) {
    btn.classList.add('active');
    btn.style.background = '#F6AE2D'; btn.style.color = '#0F172A';
    expBtn.style.display = 'inline-block';
    addBtn.style.display = 'inline-block';
    delBtn.style.display = 'none';
    // Disable other modes
    if (annotateMode) toggleAnnotateMode();
    if (layoutEditMode) toggleLayoutMode();
    if (columnEditMode) toggleColumnEditMode();
  } else {
    btn.classList.remove('active');
    btn.style.background = '#0055AA'; btn.style.color = '#FFF';
    expBtn.style.display = 'none';
    addBtn.style.display = 'none';
    delBtn.style.display = 'none';
    selectedWeldId = null;
    document.getElementById('weldEditor').classList.remove('show');
  }
  draw();
}

// Toggle "Add Weld" placement mode
function toggleAddWeldMode() {
  addWeldMode = !addWeldMode;
  var btn = document.getElementById('btnAddWeld');
  if (addWeldMode) {
    btn.style.background = '#F6AE2D'; btn.style.color = '#0F172A';
    btn.textContent = '\u2716 Cancel Add';
    document.querySelector('.drawing-sheet').classList.add('add-weld-mode');
    selectedWeldId = null;
    document.getElementById('weldEditor').classList.remove('show');
    document.getElementById('btnDeleteWeld').style.display = 'none';
  } else {
    btn.style.background = '#059669'; btn.style.color = '#ECFDF5';
    btn.textContent = '\u271A Add Weld';
    document.querySelector('.drawing-sheet').classList.remove('add-weld-mode');
  }
  draw();
}

// Delete ANY weld — built-in or custom
function deleteSelectedWeld() {
  if (!selectedWeldId) return;
  pushUndo();
  // Check if it's a custom weld
  var idx = customWelds.findIndex(function(w) { return w.id === selectedWeldId; });
  if (idx !== -1) {
    // Remove custom weld entirely
    customWelds.splice(idx, 1);
  } else {
    // Built-in weld — add to deleted list
    if (deletedWelds.indexOf(selectedWeldId) === -1) {
      deletedWelds.push(selectedWeldId);
    }
  }
  delete weldOverrides[selectedWeldId];
  selectedWeldId = null;
  document.getElementById('weldEditor').classList.remove('show');
  document.getElementById('btnDeleteWeld').style.display = 'none';
  draw();
}

// SVG click: place new weld or select existing
function svgToViewBox(e) {
  var svg = document.getElementById('svg');
  var pt = new DOMPoint(e.clientX, e.clientY);
  return pt.matrixTransform(svg.getScreenCTM().inverse());
}

// Weld click handler
document.addEventListener('click', function(e) {
  if (!weldEditMode) return;

  // If in add-weld mode, place a new weld at click location
  if (addWeldMode) {
    var svgEl = document.getElementById('svg');
    if (!svgEl.contains(e.target)) return;
    var pos = svgToViewBox(e);
    pushUndo();
    // Convert absolute SVG click position to piece-relative inches
    // Get current beam geometry from the draw state
    var p = getParams();
    var d = calc(p);
    var _beamL = 80, _beamR = 680, _beamW = _beamR - _beamL;
    var _sc = _beamW / d.cutLengthIn;
    var _beamY = 95;
    var anchorIn = Math.max(0, Math.min(d.cutLengthIn, (pos.x - _beamL) / _sc));
    var anchorVIn = (pos.y - _beamY) / _sc;
    var newId = 'custom-weld-' + (customWelds.length + 1) + '-' + Date.now();
    var newWeld = {
      id: newId,
      anchorIn: Math.round(anchorIn * 10) / 10,   // inches from left end of piece
      anchorVIn: Math.round(anchorVIn * 10) / 10,  // inches from beam top
      routeDx: 0,    // pixel offset from anchor to route point
      routeDy: -30,  // route point 30px above anchor
      size: '3/16',
      opts: { wpsCode: '', stitch: '', refDir: 'right', allAround: false, bothSides: false }
    };
    customWelds.push(newWeld);
    // Exit add mode and select the new weld for editing
    addWeldMode = false;
    var addBtn = document.getElementById('btnAddWeld');
    addBtn.style.background = '#059669'; addBtn.style.color = '#ECFDF5';
    addBtn.textContent = '\u271A Add Weld';
    document.querySelector('.drawing-sheet').classList.remove('add-weld-mode');
    selectedWeldId = newId;
    draw();
    openWeldEditor(newId);
    return;
  }

  var wg = e.target.closest('[data-weld-id]');
  if (wg) {
    var wid = wg.getAttribute('data-weld-id');
    openWeldEditor(wid);
    // Show delete button for ALL welds (built-in and custom)
    document.getElementById('btnDeleteWeld').style.display = 'inline-block';
  }
});

// Weld drag handler
(function() {
  var dragging = null, dragStart = null;
  document.addEventListener('mousedown', function(e) {
    if (!weldEditMode) return;
    var wg = e.target.closest('[data-weld-id]');
    if (wg && selectedWeldId === wg.getAttribute('data-weld-id')) {
      dragging = wg.getAttribute('data-weld-id');
      var svg = document.getElementById('svg');
      var rect = svg.getBoundingClientRect();
      var pt = new DOMPoint(e.clientX, e.clientY);
      var svgPt = pt.matrixTransform(svg.getScreenCTM().inverse());
      dragStart = { x: svgPt.x, y: svgPt.y };
      e.preventDefault();
    }
  });
  document.addEventListener('mousemove', function(e) {
    if (!dragging) return;
    var svg = document.getElementById('svg');
    var pt = new DOMPoint(e.clientX, e.clientY);
    var svgPt = pt.matrixTransform(svg.getScreenCTM().inverse());
    if (!weldOverrides[dragging]) weldOverrides[dragging] = {};
    weldOverrides[dragging].dx = (weldOverrides[dragging].dx || 0) + (svgPt.x - dragStart.x);
    weldOverrides[dragging].dy = (weldOverrides[dragging].dy || 0) + (svgPt.y - dragStart.y);
    dragStart = { x: svgPt.x, y: svgPt.y };
    document.getElementById('btnWeldReset').style.display = 'inline-block';
    draw();
  });
  document.addEventListener('mouseup', function() {
    if (dragging) { pushUndo(); dragging = null; }
  });
})();

// ═══════════════════════════════════════════════
// UNDO / REDO
// ═══════════════════════════════════════════════
function pushUndo() {
  var state = {
    weldOverrides: JSON.parse(JSON.stringify(weldOverrides)),
    labelOverrides: JSON.parse(JSON.stringify(labelOverrides)),
    layoutOverrides: JSON.parse(JSON.stringify(layoutOverrides)),
    annotations: JSON.parse(JSON.stringify(annotations)),
    customWelds: JSON.parse(JSON.stringify(customWelds)),
    deletedWelds: JSON.parse(JSON.stringify(deletedWelds)),
    reinforced: reinforced
  };
  undoStack.push(state);
  if (undoStack.length > 60) undoStack.shift();
  redoStack = [];
}

var undoDebounceTimer;
function pushUndoDebounced() {
  clearTimeout(undoDebounceTimer);
  undoDebounceTimer = setTimeout(function() { pushUndo(); }, 500);
}

function undo() {
  if (undoStack.length === 0) return;
  var state = undoStack.pop();
  redoStack.push({ weldOverrides: JSON.parse(JSON.stringify(weldOverrides)), labelOverrides: JSON.parse(JSON.stringify(labelOverrides)), layoutOverrides: JSON.parse(JSON.stringify(layoutOverrides)), annotations: JSON.parse(JSON.stringify(annotations)), customWelds: JSON.parse(JSON.stringify(customWelds)), deletedWelds: JSON.parse(JSON.stringify(deletedWelds)), reinforced: reinforced });
  weldOverrides = state.weldOverrides;
  labelOverrides = state.labelOverrides;
  layoutOverrides = state.layoutOverrides || {};
  annotations = state.annotations || [];
  customWelds = state.customWelds || [];
  deletedWelds = state.deletedWelds || [];
  selectedAnnotation = null;
  reinforced = state.reinforced;
  document.getElementById('btnReinforced').classList.toggle('active', reinforced);
  document.getElementById('btnNonReinforced').classList.toggle('active', !reinforced);
  draw();
}

function redo() {
  if (redoStack.length === 0) return;
  var state = redoStack.pop();
  undoStack.push({ weldOverrides: JSON.parse(JSON.stringify(weldOverrides)), labelOverrides: JSON.parse(JSON.stringify(labelOverrides)), layoutOverrides: JSON.parse(JSON.stringify(layoutOverrides)), annotations: JSON.parse(JSON.stringify(annotations)), customWelds: JSON.parse(JSON.stringify(customWelds)), deletedWelds: JSON.parse(JSON.stringify(deletedWelds)), reinforced: reinforced });
  weldOverrides = state.weldOverrides;
  labelOverrides = state.labelOverrides;
  layoutOverrides = state.layoutOverrides || {};
  annotations = state.annotations || [];
  customWelds = state.customWelds || [];
  deletedWelds = state.deletedWelds || [];
  selectedAnnotation = null;
  reinforced = state.reinforced;
  document.getElementById('btnReinforced').classList.toggle('active', reinforced);
  document.getElementById('btnNonReinforced').classList.toggle('active', !reinforced);
  draw();
}

// ═══════════════════════════════════════════════
// APPROVAL WORKFLOW
// ═══════════════════════════════════════════════
function startApproval() {
  if (drawingState.checked) return;
  document.getElementById('approverName').value = '';
  document.getElementById('approvalModal').classList.add('show');
}

function confirmApproval() {
  var name = document.getElementById('approverName').value || 'Unknown';
  drawingState.checked = true;
  drawingState.checkedBy = name;
  drawingState.revision += 1;
  drawingState.history.push({ date: new Date().toLocaleDateString(), rev: drawingState.revision, desc: 'Approved', by: name });
  document.getElementById('approvalModal').classList.remove('show');
  updateCheckBadge();
  draw();
}

function cancelApproval() {
  document.getElementById('approvalModal').classList.remove('show');
}

function updateCheckBadge() {
  var badge = document.getElementById('checkBadge');
  if (drawingState.checked) {
    badge.className = 'checked-badge';
    badge.innerHTML = '\u2713 CHECKED by ' + drawingState.checkedBy;
    badge.onclick = null;
  }
}

// ═══════════════════════════════════════════════
// ANNOTATIONS — select, move, edit, delete
// ═══════════════════════════════════════════════
function toggleAnnotateMode() {
  annotateMode = !annotateMode;
  var btn = document.getElementById('btnAnnotate');
  btn.classList.toggle('active', annotateMode);
  var svgEl = document.getElementById('svg');
  var sheet = document.querySelector('.drawing-sheet');
  if (annotateMode) {
    svgEl.style.cursor = 'text';
    sheet.classList.add('anno-mode');
    // Disable other modes
    if (weldEditMode) toggleWeldEditMode();
    if (layoutEditMode) toggleLayoutMode();
    if (columnEditMode) toggleColumnEditMode();
  } else {
    svgEl.style.cursor = '';
    sheet.classList.remove('anno-mode');
    selectedAnnotation = null;
    draw();
  }
  updateAnnoBadge();
}

function updateAnnoBadge() {
  var btn = document.getElementById('btnAnnotate');
  var badge = document.getElementById('annoBadge');
  if (!badge) {
    badge = document.createElement('span');
    badge.id = 'annoBadge';
    badge.className = 'anno-count-badge';
    btn.parentNode.insertBefore(badge, btn.nextSibling);
  }
  badge.textContent = annotations.length > 0 ? annotations.length : '';
  badge.style.display = annotations.length > 0 ? 'inline' : 'none';
}

// Click handler for annotations — select existing or add new
(function() {
  var annoDragging = null, annoDragStart = null;

  document.addEventListener('mousedown', function(e) {
    if (!annotateMode) return;
    // Check if clicking on an existing annotation
    var ag = e.target.closest('[data-anno-idx]');
    if (ag) {
      var idx = parseInt(ag.getAttribute('data-anno-idx'));
      selectedAnnotation = idx;
      annoDragging = idx;
      var svg = document.getElementById('svg');
      var pt = new DOMPoint(e.clientX, e.clientY);
      var svgPt = pt.matrixTransform(svg.getScreenCTM().inverse());
      annoDragStart = { x: svgPt.x, y: svgPt.y };
      ag.classList.add('anno-dragging');
      e.preventDefault();
      e.stopPropagation();
      draw();
      return;
    }
  });

  document.addEventListener('mousemove', function(e) {
    if (annoDragging === null || !annotateMode) return;
    var svg = document.getElementById('svg');
    var pt = new DOMPoint(e.clientX, e.clientY);
    var svgPt = pt.matrixTransform(svg.getScreenCTM().inverse());
    var a = annotations[annoDragging];
    if (a) {
      a.x += (svgPt.x - annoDragStart.x);
      a.y += (svgPt.y - annoDragStart.y);
      annoDragStart = { x: svgPt.x, y: svgPt.y };
      // Move the group directly for smooth dragging
      var ag = document.querySelector('[data-anno-idx="' + annoDragging + '"]');
      if (ag) {
        var dx = a.x, dy = a.y;
        // Rebuild the translate — but since positions are absolute in the annotation, just redraw
      }
      draw();
    }
  });

  document.addEventListener('mouseup', function() {
    if (annoDragging !== null && annotateMode) {
      var ag = document.querySelector('[data-anno-idx="' + annoDragging + '"]');
      if (ag) ag.classList.remove('anno-dragging');
      pushUndo();
      annoDragging = null;
    }
  });

  // Click on blank area = add new annotation
  document.getElementById('svg').addEventListener('click', function(e) {
    if (!annotateMode) return;
    // If clicked on an existing annotation, don't add new
    if (e.target.closest('[data-anno-idx]')) return;

    var svg = document.getElementById('svg');
    var pt = new DOMPoint(e.clientX, e.clientY);
    var svgPt = pt.matrixTransform(svg.getScreenCTM().inverse());

    // Deselect if clicking blank area
    if (selectedAnnotation !== null) {
      selectedAnnotation = null;
      draw();
      return;
    }

    var text = prompt('Enter annotation:');
    if (text) {
      pushUndo();
      annotations.push({ x: svgPt.x, y: svgPt.y, text: text });
      selectedAnnotation = annotations.length - 1;
      updateAnnoBadge();
      draw();
    }
  });

  // Double-click to edit annotation text
  document.addEventListener('dblclick', function(e) {
    if (!annotateMode) return;
    var ag = e.target.closest('[data-anno-idx]');
    if (!ag) return;
    var idx = parseInt(ag.getAttribute('data-anno-idx'));
    var a = annotations[idx];
    if (!a) return;
    var newText = prompt('Edit annotation:', a.text);
    if (newText !== null && newText !== a.text) {
      pushUndo();
      a.text = newText;
      draw();
    }
  });
})();

// Keyboard: Delete/Backspace removes selected annotation, Escape deselects
document.addEventListener('keydown', function(e) {
  if (!annotateMode || selectedAnnotation === null) return;
  if (e.key === 'Delete' || e.key === 'Backspace') {
    // Don't delete if a prompt/input is focused
    if (document.activeElement && (document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'TEXTAREA')) return;
    e.preventDefault();
    pushUndo();
    annotations.splice(selectedAnnotation, 1);
    selectedAnnotation = null;
    updateAnnoBadge();
    draw();
  } else if (e.key === 'Escape') {
    selectedAnnotation = null;
    draw();
  }
});

// ═══════════════════════════════════════════════
// ═══════════════════════════════════════════════
// LAYOUT EDIT MODE
// ═══════════════════════════════════════════════
function toggleLayoutMode() {
  layoutEditMode = !layoutEditMode;
  var btn = document.getElementById('btnLayoutEdit');
  var expBtn = document.getElementById('btnExportLayout');
  var rstBtn = document.getElementById('btnResetLayout');
  var sheet = document.querySelector('.drawing-sheet');

  btn.classList.toggle('active', layoutEditMode);
  if (layoutEditMode) {
    btn.style.background = '#F6AE2D'; btn.style.color = '#0F172A';
    expBtn.style.display = 'inline-block';
    rstBtn.style.display = Object.keys(layoutOverrides).length > 0 ? 'inline-block' : 'none';
    sheet.classList.add('layout-mode');
    // Disable other modes
    if (weldEditMode) toggleWeldEditMode();
    if (annotateMode) toggleAnnotateMode();
    if (columnEditMode) toggleColumnEditMode();
  } else {
    btn.style.background = '#065F46'; btn.style.color = '#6EE7B7';
    expBtn.style.display = 'none';
    rstBtn.style.display = 'none';
    sheet.classList.remove('layout-mode');
    selectedLayoutId = null;
  }
}

// Layout drag handler
(function() {
  var dragging = null, dragStart = null;

  document.addEventListener('mousedown', function(e) {
    if (!layoutEditMode) return;
    var lg = e.target.closest('[data-layout-id]');
    if (!lg) return;
    var lid = lg.getAttribute('data-layout-id');
    selectedLayoutId = lid;
    // Deselect all, select this one
    document.querySelectorAll('[data-layout-id]').forEach(function(el) {
      el.classList.remove('layout-selected');
    });
    lg.classList.add('layout-selected');

    dragging = lid;
    var svg = document.getElementById('svg');
    var pt = new DOMPoint(e.clientX, e.clientY);
    var svgPt = pt.matrixTransform(svg.getScreenCTM().inverse());
    dragStart = { x: svgPt.x, y: svgPt.y };
    lg.classList.add('layout-dragging');
    e.preventDefault();
    e.stopPropagation();
  });

  document.addEventListener('mousemove', function(e) {
    if (!dragging || !layoutEditMode) return;
    var svg = document.getElementById('svg');
    var pt = new DOMPoint(e.clientX, e.clientY);
    var svgPt = pt.matrixTransform(svg.getScreenCTM().inverse());
    if (!layoutOverrides[dragging]) layoutOverrides[dragging] = { dx: 0, dy: 0 };
    layoutOverrides[dragging].dx += (svgPt.x - dragStart.x);
    layoutOverrides[dragging].dy += (svgPt.y - dragStart.y);
    dragStart = { x: svgPt.x, y: svgPt.y };
    // Apply transform directly (no full redraw during drag for smooth performance)
    var lg = document.querySelector('[data-layout-id="' + dragging + '"]');
    if (lg) {
      lg.setAttribute('transform', 'translate(' + layoutOverrides[dragging].dx + ',' + layoutOverrides[dragging].dy + ')');
    }
    document.getElementById('btnResetLayout').style.display = 'inline-block';
  });

  document.addEventListener('mouseup', function() {
    if (dragging && layoutEditMode) {
      var lg = document.querySelector('[data-layout-id="' + dragging + '"]');
      if (lg) lg.classList.remove('layout-dragging');
      pushUndo();
      dragging = null;
    }
  });
})();

function exportLayout() {
  var moves = {};
  var hasAny = false;
  Object.keys(layoutOverrides).forEach(function(id) {
    var ov = layoutOverrides[id];
    if (ov && (Math.abs(ov.dx) > 0.5 || Math.abs(ov.dy) > 0.5)) {
      moves[id] = { dx: Math.round(ov.dx * 10) / 10, dy: Math.round(ov.dy * 10) / 10 };
      hasAny = true;
    }
  });

  var text = '';
  if (!hasAny) {
    text = '(No layout moves to export — drag elements in Layout Edit mode first)';
  } else {
    text = 'LAYOUT MOVES — Paste this to Claude:\n';
    text += '═══════════════════════════════════════\n\n';
    Object.keys(moves).forEach(function(id) {
      var m = moves[id];
      var dir = [];
      if (m.dx > 0) dir.push('right ' + m.dx + 'px');
      else if (m.dx < 0) dir.push('left ' + Math.abs(m.dx) + 'px');
      if (m.dy > 0) dir.push('down ' + m.dy + 'px');
      else if (m.dy < 0) dir.push('up ' + Math.abs(m.dy) + 'px');
      text += '• ' + id + ': move ' + dir.join(', ') + '\n';
    });
    text += '\nRAW JSON:\n';
    text += JSON.stringify(moves, null, 2);
  }

  document.getElementById('exportText').value = text;
  document.getElementById('exportModal').classList.add('show');
}

function copyExport() {
  var ta = document.getElementById('exportText');
  ta.select();
  document.execCommand('copy');
  var btn = document.querySelector('.btn-copy');
  btn.textContent = '\u2713 Copied!';
  setTimeout(function() { btn.textContent = '\uD83D\uDCCB Copy to Clipboard'; }, 1500);
}

function closeExportModal() {
  document.getElementById('exportModal').classList.remove('show');
}

function exportWelds() {
  var hasAny = false;
  var text = '';

  // Gather weld overrides (position moves + property edits)
  var weldMoves = {};
  Object.keys(weldOverrides).forEach(function(id) {
    var ov = weldOverrides[id];
    if (!ov) return;
    var entry = {};
    var hasSomething = false;
    if (ov.dx && Math.abs(ov.dx) > 0.5) { entry.dx = Math.round(ov.dx * 10) / 10; hasSomething = true; }
    if (ov.dy && Math.abs(ov.dy) > 0.5) { entry.dy = Math.round(ov.dy * 10) / 10; hasSomething = true; }
    if (ov.size) { entry.size = ov.size; hasSomething = true; }
    if (ov.wpsCode) { entry.wpsCode = ov.wpsCode; hasSomething = true; }
    if (ov.stitch) { entry.stitch = ov.stitch; hasSomething = true; }
    if (ov.refDir) { entry.refDir = ov.refDir; hasSomething = true; }
    if (ov.rotation) { entry.rotation = ov.rotation; hasSomething = true; }
    if (ov.allAround) { entry.allAround = true; hasSomething = true; }
    if (ov.bothSides) { entry.bothSides = true; hasSomething = true; }
    if (hasSomething) { weldMoves[id] = entry; hasAny = true; }
  });

  // Gather label overrides
  var labelMoves = {};
  Object.keys(labelOverrides).forEach(function(id) {
    var ov = labelOverrides[id];
    if (ov && (Math.abs(ov.dx || 0) > 0.5 || Math.abs(ov.dy || 0) > 0.5)) {
      labelMoves[id] = { dx: Math.round((ov.dx || 0) * 10) / 10, dy: Math.round((ov.dy || 0) * 10) / 10 };
      hasAny = true;
    }
  });

  // Gather custom (user-added) welds
  var customWeldExport = [];
  customWelds.forEach(function(cw) {
    var ov = weldOverrides[cw.id] || {};
    customWeldExport.push({
      id: cw.id,
      anchorIn: cw.anchorIn, anchorVIn: cw.anchorVIn,
      routeDx: (cw.routeDx || 0) + (ov.dx || 0),
      routeDy: (cw.routeDy || -30) + (ov.dy || 0),
      size: ov.size || cw.size,
      wpsCode: ov.wpsCode || cw.opts.wpsCode || '',
      stitch: ov.stitch || cw.opts.stitch || '',
      refDir: ov.refDir || cw.opts.refDir || 'right',
      allAround: ov.allAround || cw.opts.allAround || false,
      bothSides: ov.bothSides || cw.opts.bothSides || false
    });
    hasAny = true;
  });

  // Gather deleted welds
  if (deletedWelds.length > 0) hasAny = true;

  if (!hasAny) {
    text = '(No weld or label edits to export — drag welds, edit properties, add/delete welds first)';
  } else {
    text = 'WELD & LABEL EDITS — Paste this to Claude:\n';
    text += '═══════════════════════════════════════\n\n';

    if (Object.keys(weldMoves).length > 0) {
      text += 'WELD OVERRIDES:\n';
      Object.keys(weldMoves).forEach(function(id) {
        var m = weldMoves[id];
        var parts = [];
        if (m.dx) parts.push((m.dx > 0 ? 'right ' : 'left ') + Math.abs(m.dx) + 'px');
        if (m.dy) parts.push((m.dy > 0 ? 'down ' : 'up ') + Math.abs(m.dy) + 'px');
        if (m.size) parts.push('size=' + m.size);
        if (m.wpsCode) parts.push('WPS=' + m.wpsCode);
        if (m.stitch) parts.push('stitch=' + m.stitch);
        if (m.refDir) parts.push('dir=' + m.refDir);
        if (m.rotation) parts.push('rot=' + m.rotation + '°');
        if (m.allAround) parts.push('all-around');
        if (m.bothSides) parts.push('both-sides');
        text += '  \u2022 ' + id + ': ' + parts.join(', ') + '\n';
      });
      text += '\n';
    }

    if (deletedWelds.length > 0) {
      text += 'DELETED WELDS (' + deletedWelds.length + '):\n';
      deletedWelds.forEach(function(wid) {
        text += '  \u2022 ' + wid + '\n';
      });
      text += '\n';
    }

    if (customWeldExport.length > 0) {
      text += 'NEW WELDS ADDED (' + customWeldExport.length + '):\n';
      customWeldExport.forEach(function(cw) {
        var parts = ['anchor=' + Math.round(cw.anchorIn) + '" from L, ' + Math.round(cw.anchorVIn) + '" from top'];
        parts.push('size=' + cw.size + '"');
        if (cw.wpsCode) parts.push('WPS=' + cw.wpsCode);
        if (cw.stitch) parts.push('stitch=' + cw.stitch);
        if (cw.allAround) parts.push('all-around');
        if (cw.bothSides) parts.push('both-sides');
        text += '  \u2022 ' + cw.id + ': ' + parts.join(', ') + '\n';
      });
      text += '\n';
    }

    if (Object.keys(labelMoves).length > 0) {
      text += 'LABEL MOVES:\n';
      Object.keys(labelMoves).forEach(function(id) {
        var m = labelMoves[id];
        var dir = [];
        if (m.dx > 0) dir.push('right ' + m.dx + 'px');
        else if (m.dx < 0) dir.push('left ' + Math.abs(m.dx) + 'px');
        if (m.dy > 0) dir.push('down ' + m.dy + 'px');
        else if (m.dy < 0) dir.push('up ' + Math.abs(m.dy) + 'px');
        text += '  \u2022 ' + id + ': move ' + dir.join(', ') + '\n';
      });
      text += '\n';
    }

    text += 'RAW JSON:\n';
    var raw = {};
    if (Object.keys(weldMoves).length > 0) raw.weldOverrides = weldMoves;
    if (Object.keys(labelMoves).length > 0) raw.labelOverrides = labelMoves;
    if (customWeldExport.length > 0) raw.customWelds = customWeldExport;
    if (deletedWelds.length > 0) raw.deletedWelds = deletedWelds;
    text += JSON.stringify(raw, null, 2);
  }

  document.getElementById('exportText').value = text;
  document.getElementById('exportModal').classList.add('show');
}

var defaultLayoutOverrides = JSON.parse(JSON.stringify(layoutOverrides));

function resetLayoutOverrides() {
  if (!confirm('Reset layout to auto-calculated positions? (Your saved defaults can be restored with Undo)')) return;
  pushUndo();
  layoutOverrides = {};
  selectedLayoutId = null;
  draw();
}

function restoreDefaultLayout() {
  pushUndo();
  layoutOverrides = JSON.parse(JSON.stringify(defaultLayoutOverrides));
  selectedLayoutId = null;
  draw();
}

// ═══════════════════════════════════════════════
// PAN / ZOOM — EXACT from column drawing
// ═══════════════════════════════════════════════
(function() {
  var svgEl = document.getElementById('svg');
  var origVB = { x: 0, y: 0, w: 1100, h: 850 };
  var vb = { x: 0, y: 0, w: 1100, h: 850 };
  var isPanning = false, startPt = null;
  var lastPinchDist = 0;

  function applyVB() {
    svgEl.setAttribute('viewBox', vb.x+' '+vb.y+' '+vb.w+' '+vb.h);
  }

  // Mouse wheel zoom
  svgEl.addEventListener('wheel', function(e) {
    e.preventDefault();
    var rect = svgEl.getBoundingClientRect();
    var mx = (e.clientX - rect.left) / rect.width;
    var my = (e.clientY - rect.top) / rect.height;
    var factor = e.deltaY > 0 ? 1.08 : 0.93;
    var nw = vb.w * factor, nh = vb.h * factor;
    vb.x += (vb.w - nw) * mx;
    vb.y += (vb.h - nh) * my;
    vb.w = nw; vb.h = nh;
    applyVB();
  }, { passive: false });

  // Mouse pan
  svgEl.addEventListener('mousedown', function(e) {
    if (e.button === 0 && !annotateMode && !weldEditMode && !layoutEditMode && !columnEditMode) {
      isPanning = true;
      startPt = { x: e.clientX, y: e.clientY };
      svgEl.style.cursor = 'grabbing';
    }
  });

  window.addEventListener('mousemove', function(e) {
    if (!isPanning) return;
    var rect = svgEl.getBoundingClientRect();
    var dx = (e.clientX - startPt.x) * (vb.w / rect.width);
    var dy = (e.clientY - startPt.y) * (vb.h / rect.height);
    vb.x -= dx;  // SUBTRACT to move in SAME direction as mouse
    vb.y -= dy;
    startPt = { x: e.clientX, y: e.clientY };
    applyVB();
  });

  window.addEventListener('mouseup', function() {
    isPanning = false;
    svgEl.style.cursor = '';
  });

  // Touch pinch zoom
  svgEl.addEventListener('touchstart', function(e) {
    if (e.touches.length === 2) {
      isPanning = false;
      var dx = e.touches[0].clientX - e.touches[1].clientX;
      var dy = e.touches[0].clientY - e.touches[1].clientY;
      lastPinchDist = Math.sqrt(dx*dx + dy*dy);
    }
  }, { passive: true });

  svgEl.addEventListener('touchmove', function(e) {
    if (e.touches.length === 2) {
      e.preventDefault();
      var dx = e.touches[0].clientX - e.touches[1].clientX;
      var dy = e.touches[0].clientY - e.touches[1].clientY;
      var dist = Math.sqrt(dx*dx + dy*dy);
      if (lastPinchDist > 0) {
        var zoomFactor = lastPinchDist / dist;
        var cx = vb.x + vb.w / 2;
        var cy = vb.y + vb.h / 2;
        vb.w *= zoomFactor;
        vb.h *= zoomFactor;
        vb.x = cx - vb.w / 2;
        vb.y = cy - vb.h / 2;
        applyVB();
      }
      lastPinchDist = dist;
    }
  }, { passive: false });

  window.resetZoom = function() {
    vb = { x: origVB.x, y: origVB.y, w: origVB.w, h: origVB.h };
    applyVB();
  };
})();

// ═══════════════════════════════════════════════
// KEYBOARD SHORTCUTS
// ═══════════════════════════════════════════════
document.addEventListener('keydown', function(e) {
  if ((e.metaKey || e.ctrlKey) && e.key === 'z' && !e.shiftKey) { e.preventDefault(); undo(); }
  if ((e.metaKey || e.ctrlKey) && e.shiftKey && (e.key === 'z' || e.key === 'Z')) { e.preventDefault(); redo(); }
});

// ═══════════════════════════════════════════════
// PIECE TABS & SPLICE CONTROLS
// ═══════════════════════════════════════════════
function updatePieceTabs() {
  var p = getParams();
  var d = calc(p);
  var tabsDiv = document.getElementById('pieceTabs');
  var btnsDiv = document.getElementById('pieceTabBtns');
  var spliceGroup = document.getElementById('spliceGroup');
  var infoSpan = document.getElementById('spliceInfo');

  // Show/hide splice input
  if (d.totalCutLengthFt > 53) {
    spliceGroup.style.display = '';
    // Default splice location to midpoint if not set
    var spliceInput = document.getElementById('inputSpliceLocation');
    if (parseFloat(spliceInput.value) === 0) {
      spliceInput.value = Math.round(d.totalCutLengthFt / 2 * 10) / 10;
    }
  } else {
    spliceGroup.style.display = 'none';
  }

  // Show/hide piece tabs
  if (d.pieceCount > 1) {
    tabsDiv.style.display = 'flex';
    btnsDiv.innerHTML = '';
    for (var i = 0; i < d.pieceCount; i++) {
      var btn = document.createElement('button');
      btn.className = 'piece-tab' + (activePiece === i ? ' active' : '');
      btn.textContent = 'Piece ' + (i + 1) + ' (' + fmtFtIn(d.pieces[i].lengthIn) + ')';
      btn.setAttribute('data-piece', i);
      btn.onclick = function() { selectPiece(parseInt(this.getAttribute('data-piece'))); };
      btnsDiv.appendChild(btn);
    }
    // Show warnings
    if (d.spliceWarnings.length > 0) {
      infoSpan.innerHTML = '<span class="splice-warn">\u26A0 ' + d.spliceWarnings.join(' | ') + '</span>';
    } else {
      infoSpan.textContent = 'Splice at ' + fmtFtIn(d.splicePositions[0]) + ' from left end';
    }
  } else {
    tabsDiv.style.display = 'none';
  }

  // Clamp active piece
  if (activePiece >= d.pieceCount) {
    activePiece = 0;
  }
}

function selectPiece(idx) {
  activePiece = idx;
  updatePieceTabs();
  draw();
}

// ═══════════════════════════════════════════════
// COLUMN POSITION AUTO-FILL & EDIT MODE
// ═══════════════════════════════════════════════

// Auto-fill column positions input — delegates to calc() for all placement logic
function autoFillColumnPositions() {
  // Clear column positions first so getParams() doesn't read stale typed values
  document.getElementById('inputColumnPositions').value = '';
  var p = getParams();
  var d = calc(p);
  // calc() computed p3Positions — write them back as feet
  var ftStrs = (d.p3Positions || []).map(function(posIn) {
    return Math.round(posIn / 12 * 10) / 10;
  });
  document.getElementById('inputColumnPositions').value = ftStrs.join(', ');
}

// Update column positions text from P3 pixel positions after drag
function updateColumnPosFromPixels(p3PositionsPx, beamL, beamW, cutLengthIn) {
  var ftStrs = p3PositionsPx.map(function(px) {
    var posIn = ((px - beamL) / beamW) * cutLengthIn;
    return Math.round(posIn / 12 * 10) / 10;
  });
  document.getElementById('inputColumnPositions').value = ftStrs.join(', ');
}

// Toggle column edit mode (drag P3 markers on elevation)
function toggleColumnEditMode() {
  columnEditMode = !columnEditMode;
  var btn = document.getElementById('btnColEdit');
  var sheet = document.querySelector('.drawing-sheet');
  if (columnEditMode) {
    btn.style.background = '#F6AE2D'; btn.style.color = '#0F172A';
    btn.classList.add('active');
    sheet.classList.add('col-edit-mode');
    // Disable other modes
    if (weldEditMode) toggleWeldEditMode();
    if (annotateMode) toggleAnnotateMode();
    if (layoutEditMode) toggleLayoutMode();
  } else {
    btn.style.background = '#7C3AED'; btn.style.color = '#DDD6FE';
    btn.classList.remove('active');
    sheet.classList.remove('col-edit-mode');
  }
  draw();
}

// P3 column drag handler
(function() {
  var draggingP3 = null;  // index into p3Positions array
  var dragStartX = 0;
  var p3DragInfo = null;  // { beamL, beamW, cutLengthIn, positions[] }

  document.addEventListener('mousedown', function(e) {
    if (!columnEditMode) return;
    var handle = e.target.closest('[data-p3-drag-idx]');
    if (!handle) return;
    var idx = parseInt(handle.getAttribute('data-p3-drag-idx'));
    draggingP3 = idx;
    var svg = document.getElementById('svg');
    var pt = new DOMPoint(e.clientX, e.clientY);
    var svgPt = pt.matrixTransform(svg.getScreenCTM().inverse());
    dragStartX = svgPt.x;
    // Store current P3 pixel positions for live update
    var handles = document.querySelectorAll('[data-p3-drag-idx]');
    var positions = [];
    handles.forEach(function(h) {
      positions.push(parseFloat(h.getAttribute('data-p3-px')));
    });
    p3DragInfo = {
      beamL: parseFloat(handle.getAttribute('data-beam-l')),
      beamW: parseFloat(handle.getAttribute('data-beam-w')),
      cutLengthIn: parseFloat(handle.getAttribute('data-cut-in')),
      positions: positions
    };
    e.preventDefault();
    e.stopPropagation();
  });

  document.addEventListener('mousemove', function(e) {
    if (draggingP3 === null || !columnEditMode || !p3DragInfo) return;
    var svg = document.getElementById('svg');
    var pt = new DOMPoint(e.clientX, e.clientY);
    var svgPt = pt.matrixTransform(svg.getScreenCTM().inverse());
    var dx = svgPt.x - dragStartX;
    dragStartX = svgPt.x;

    // Update the position
    p3DragInfo.positions[draggingP3] += dx;
    // Clamp to beam extents (with 12" margin from ends)
    var minX = p3DragInfo.beamL + 12 * (p3DragInfo.beamW / p3DragInfo.cutLengthIn);
    var maxX = p3DragInfo.beamL + p3DragInfo.beamW - 12 * (p3DragInfo.beamW / p3DragInfo.cutLengthIn);
    p3DragInfo.positions[draggingP3] = Math.max(minX, Math.min(maxX, p3DragInfo.positions[draggingP3]));

    // Update text input in real-time
    updateColumnPosFromPixels(p3DragInfo.positions, p3DragInfo.beamL, p3DragInfo.beamW, p3DragInfo.cutLengthIn);
    // Redraw with new positions
    draw();
  });

  document.addEventListener('mouseup', function() {
    if (draggingP3 !== null && columnEditMode) {
      pushUndo();
      draggingP3 = null;
      p3DragInfo = null;
    }
  });
})();

// ═══════════════════════════════════════════════
// INPUT LISTENERS
// ═══════════════════════════════════════════════
['inputWidth','inputSpacing','inputOverhang','inputPurlinType','inputBackWall','inputSpliceLocation','inputRebarSize','inputMaxStick','inputEndGap','inputAngledPurlins','inputPurlinAngle'].forEach(function(id) {
  var el = document.getElementById(id);
  if (!el) return;
  el.addEventListener('change', function() {
    pushUndo();
    if (id === 'inputBackWall' || id === 'inputAngledPurlins') updateColModeUI();
    if (id === 'inputBackWall' || id === 'inputWidth' || id === 'inputOverhang') {
      autoFillColumnPositions();
    }
    updatePieceTabs(); draw();
  });
  el.addEventListener('input', function() {
    if (id === 'inputBackWall' || id === 'inputAngledPurlins') updateColModeUI();
    if (id === 'inputBackWall' || id === 'inputWidth' || id === 'inputOverhang') {
      autoFillColumnPositions();
    }
    updatePieceTabs(); draw();
  });
});

// Column mode show/hide helper
function updateColModeUI() {
  var mode = document.getElementById('inputColMode').value;
  document.getElementById('colSpacingWrap').style.display = mode === 'spacing' ? '' : 'none';
  document.getElementById('colManualWrap').style.display = mode === 'manual' ? '' : 'none';
  // Back wall inputs
  document.getElementById('backWallInputs').style.display = document.getElementById('inputBackWall').checked ? '' : 'none';
  // Angled purlin inputs
  var angledEl = document.getElementById('angledInputs');
  if (angledEl) angledEl.style.display = document.getElementById('inputAngledPurlins').checked ? '' : 'none';
}

// Column mode selector
document.getElementById('inputColMode').addEventListener('change', function() {
  pushUndo();
  updateColModeUI();
  autoFillColumnPositions();
  updatePieceTabs(); draw();
});

// Column spacing input
document.getElementById('inputColSpacing').addEventListener('change', function() {
  pushUndo(); autoFillColumnPositions(); updatePieceTabs(); draw();
});
document.getElementById('inputColSpacing').addEventListener('input', function() {
  autoFillColumnPositions(); updatePieceTabs(); draw();
});

// Column qty manual input
document.getElementById('inputP3Count').addEventListener('change', function() {
  pushUndo(); autoFillColumnPositions(); updatePieceTabs(); draw();
});
document.getElementById('inputP3Count').addEventListener('input', function() {
  autoFillColumnPositions(); updatePieceTabs(); draw();
});

// Front column position (back wall)
document.getElementById('inputFrontCol').addEventListener('change', function() {
  pushUndo(); autoFillColumnPositions(); updatePieceTabs(); draw();
});
document.getElementById('inputFrontCol').addEventListener('input', function() {
  autoFillColumnPositions(); updatePieceTabs(); draw();
});

// Column positions text input
document.getElementById('inputColumnPositions').addEventListener('change', function() {
  pushUndo();
  // If user types positions manually, switch to manual mode
  var vals = this.value.split(',').filter(function(s) { return !isNaN(parseFloat(s.trim())) && parseFloat(s.trim()) > 0; });
  if (vals.length > 0) {
    document.getElementById('inputColMode').value = 'manual';
    document.getElementById('inputP3Count').value = vals.length;
    updateColModeUI();
  }
  updatePieceTabs(); draw();
});
document.getElementById('inputColumnPositions').addEventListener('input', function() {
  updatePieceTabs(); draw();
});

['setProjectName','setCustomer','setJobNumber','setDrawnBy','setRafterMark','setDrawingNum','setSurfPrep'].forEach(function(id) {
  var el = document.getElementById(id);
  if (el) el.addEventListener('input', function() { pushUndoDebounced(); draw(); });
});

// ═══════════════════════════════════════════════
// INITIALIZE
// ═══════════════════════════════════════════════
// Reinforced / Non-Reinforced toggle buttons
document.getElementById('btnReinforced').addEventListener('click', function() {
  if (!reinforced) {
    pushUndo();
    reinforced = true;
    this.classList.add('active');
    document.getElementById('btnNonReinforced').classList.remove('active');
    draw();
  }
});
document.getElementById('btnNonReinforced').addEventListener('click', function() {
  if (reinforced) {
    pushUndo();
    reinforced = false;
    this.classList.add('active');
    document.getElementById('btnReinforced').classList.remove('active');
    draw();
  }
});

// ═══════════════════════════════════════════════
// SAVE PDF TO PROJECT (via jsPDF + svg2pdf.js)
// ═══════════════════════════════════════════════
function savePdfToProject() {
  var btn = document.getElementById('btnSavePdf');
  var status = document.getElementById('savePdfStatus');
  var jobCode = (window.RAFTER_CONFIG && window.RAFTER_CONFIG.job_code) || '{{JOB_CODE}}';
  if (!jobCode || jobCode === 'null') {
    alert('No project job code — open this drawing from a project to save.');
    return;
  }
  btn.disabled = true;
  btn.textContent = 'Generating...';
  status.textContent = '';

  try {
    var svgEl = document.getElementById('svg');
    // Get the SVG's viewBox dimensions for the PDF page size
    var vb = svgEl.viewBox.baseVal;
    var svgW = vb.width || 1100;
    var svgH = vb.height || 850;

    // Create landscape PDF matching the drawing proportions
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
      formData.append('drawing_type', 'rafter');
      formData.append('source', 'interactive');
      formData.append('pdf_file', blob, jobCode + '_RAFTER_INTERACTIVE.pdf');

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

document.addEventListener('DOMContentLoaded', function() {

  applyServerConfig();
  updateColModeUI();
  // Auto-fill column positions on initial load if empty
  if (!document.getElementById('inputColumnPositions').value.trim()) {
    autoFillColumnPositions();
  }
  pushUndo();
  updatePieceTabs();
  draw();
});
</script>
</body>
</html>
"""
