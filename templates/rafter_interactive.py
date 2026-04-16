"""
TitanForge — Interactive Rafter Shop Drawing Template
======================================================
Full-featured SVG-based rafter shop drawing served as an interactive page.
Pre-fills with project data via window.RAFTER_CONFIG injection.
Supports PDF export via jsPDF + svg2pdf for clean shop-floor output.

This template follows the exact same pattern as column_interactive.py,
with 5 interactive views:
  - Top View: Purlin layout with clip positions & spacing
  - Side View: Rafter elevation showing depth, splice location, rebar
  - Section A-A: Cross-section through rafter body (box beam)
  - Splice Detail / Clip Details: Enlarged views
  - BOM: Bill of materials table

All recalculations happen in JavaScript on control changes.
PDF save uses `/api/shop-drawings/save-interactive-pdf` endpoint.
"""

RAFTER_DRAWING_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TitanForge — Rafter Shop Drawing v1</title>
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
  .controls { display: flex; gap: 14px; align-items: center; flex-wrap: wrap; }
  .ctrl-group { display: flex; align-items: center; gap: 6px; }
  .ctrl-group label { font-size: 0.75rem; color: #94A3B8; white-space: nowrap; }
  .ctrl-group select, .ctrl-group input[type=text], .ctrl-group input[type=number] {
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
  .cap { fill: #FFDDAA; stroke: #DD6600; stroke-width: 1.2; }
  .clip { fill: #E8E8F0; stroke: #1a1a1a; stroke-width: 1.0; }
  .rebar-solid { fill: #CC4400; stroke: #993300; stroke-width: 0.6; }
  .rebar-circ { fill: #CC4400; stroke: #993300; stroke-width: 0.8; }
  .splice { fill: #FFEECC; stroke: #AA4400; stroke-width: 1.0; }
  .nopaint { fill: #FF6600; fill-opacity: 0.12; stroke: #FF6600; stroke-width: 0.4; stroke-dasharray: 4,2; }
  .cut-line { stroke: #CC3333; stroke-width: 0.8; fill: none; }
  .weld { stroke: #0055AA; stroke-width: 0.8; fill: none; }
  .dimtxt { font: 700 7px 'Courier New', monospace; fill: #333; text-anchor: middle; }

  .foot { display: flex; gap: 20px; padding: 8px 20px; background: #1E293B;
    border-top: 1px solid #334155; font-size: 0.75rem; color: #94A3B8; flex-wrap: wrap; }
  .foot .s { color: #F6AE2D; font-weight: 600; }

  /* BOM panel */
  .bom { position: fixed; right: -400px; top: 0; bottom: 0; width: 380px;
    background: #1E293B; border-left: 2px solid #F6AE2D; z-index: 50;
    transition: right 0.3s; padding: 20px; overflow-y: auto; }
  .bom.open { right: 0; }
  .bom h2 { color: #F6AE2D; font-size: 1rem; margin-bottom: 12px; }
  .bom table { width: 100%; border-collapse: collapse; font-size: 0.75rem; }
  .bom th { background: #334155; color: #F6AE2D; padding: 5px 6px; text-align: left; }
  .bom td { padding: 4px 6px; border-bottom: 1px solid #334155; color: #CBD5E1; }
  .bom-x { position: absolute; top: 10px; right: 12px; background: none; border: none; color: #94A3B8; font-size: 1.2rem; cursor: pointer; }

  /* Status indicator */
  #savePdfStatus { font-size: 0.75rem; color: #94A3B8; margin-left: 8px; }
  .spinner { display: inline-block; width: 12px; height: 12px; border: 2px solid #F6AE2D; border-radius: 50%;
    border-top-color: transparent; animation: spin 0.6s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }

  @media print {
    .top-bar, .foot, .bom { display: none !important; }
    .drawing-sheet { box-shadow: none; width: 100%; height: auto; }
    .canvas-wrap { padding: 0; }
    body { background: #fff; }
  }
</style>

<script>
// ── Server-injected project config ──
window.RAFTER_CONFIG = window.RAFTER_CONFIG || null;

function _setVal(id, val) { var el = document.getElementById(id); if (el && val !== undefined && val !== null) el.value = val; }

function applyServerConfig() {
  var cfg = window.RAFTER_CONFIG;
  if (!cfg) return;

  _setVal('inJobCode', cfg.job_code);
  _setVal('inBuildingWidth', cfg.building_width_ft);
  _setVal('inRoofingOverhang', cfg.raft_roofing_overhang_ft);
  _setVal('inPurlinSpacing', cfg.purlin_spacing_ft);
  _setVal('inPurlinType', cfg.raft_purlin_type);
  _setVal('inRafterMark', cfg.rafter_mark);
  if (cfg.raft_reinforced !== undefined) {
    if (cfg.raft_reinforced) {
      document.getElementById('btnReinforced').classList.add('active');
      document.getElementById('btnNonReinforced').classList.remove('active');
    } else {
      document.getElementById('btnReinforced').classList.remove('active');
      document.getElementById('btnNonReinforced').classList.add('active');
    }
  }

  var h1 = document.querySelector('.top-bar h1');
  if (h1) {
    var mark = cfg.rafter_mark || 'B1';
    h1.textContent = 'TitanForge — Rafter Shop Drawing — ' + mark + ' — ' + (cfg.job_code || '');
  }
}

window.RAFTER_CONFIG = {{RAFTER_CONFIG_JSON}};
</script>

<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/svg2pdf.js/2.2.3/svg2pdf.umd.min.js"></script>
<script>
// ── svg2pdf compatibility shim ──────────────────────────────
(function() {
  if (window.jspdf && !window.jspdf.jsPDF.prototype.svg) {
    var s = document.createElement('script');
    s.src = 'https://cdn.jsdelivr.net/npm/svg2pdf.js@2.2.3/dist/svg2pdf.umd.min.js';
    document.head.appendChild(s);
  }
  if (typeof window.svg2pdf === 'undefined' || !window.svg2pdf.svg2pdf) {
    window.svg2pdf = window.svg2pdf || {};
    window.svg2pdf.svg2pdf = function(svgElement, pdfDoc, options) {
      if (typeof pdfDoc.svg === 'function') {
        return pdfDoc.svg(svgElement, options);
      }
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

<input type="hidden" id="inJobCode" value="">
<div class="top-bar">
  <h1>TitanForge — Rafter Shop Drawing</h1>
  <div class="controls">
    <div class="ctrl-group">
      <label>Mark:</label>
      <input type="text" id="inRafterMark" value="B1" style="width:50px;">
    </div>
    <div class="ctrl-group">
      <label>Bldg Width:</label>
      <input type="number" id="inBuildingWidth" value="60" min="20" max="150" step="5" style="width:60px;">
      <span class="lbl" style="color:#94A3B8;">ft</span>
    </div>
    <div class="ctrl-group">
      <label>Roofing OH:</label>
      <input type="number" id="inRoofingOverhang" value="1" min="0" max="3" step="0.25" style="width:60px;">
      <span class="lbl" style="color:#94A3B8;">ft</span>
    </div>
    <div class="ctrl-group">
      <label>Purlin Spacing:</label>
      <input type="number" id="inPurlinSpacing" value="6" min="3" max="12" step="0.5" style="width:60px;">
      <span class="lbl" style="color:#94A3B8;">ft</span>
    </div>
    <div class="ctrl-group">
      <label>Purlin Type:</label>
      <select id="inPurlinType">
        <option value="z">Z-Purlin</option>
        <option value="c">C-Purlin</option>
      </select>
    </div>
    <div class="ctrl-group">
      <button class="toggle-btn active" id="btnReinforced" onclick="toggleReinforced(true)">Reinforced</button>
      <button class="toggle-btn" id="btnNonReinforced" onclick="toggleReinforced(false)">Non-Reinforced</button>
    </div>
    <div class="ctrl-group">
      <label>Zoom:</label>
      <input type="range" id="inZoom" min="0.6" max="2.0" step="0.1" value="1.0">
    </div>
    <button class="btn-gold" style="background:#059669;color:#FFF;" onclick="savePdfToProject()">Save PDF to Project</button>
    <span id="savePdfStatus"></span>
    <button class="btn-gold" style="background:#475569;color:#F1F5F9;" onclick="window.print()">Print</button>
    <a style="padding:6px 12px;background:#334155;color:#94A3B8;border:1px solid #475569;border-radius:5px;text-decoration:none;font-size:0.78rem;cursor:pointer;" href="/shop-drawings/{{JOB_CODE}}">← Back</a>
  </div>
</div>

<div class="canvas-wrap">
  <div class="drawing-sheet" id="drawingSheet">
    <svg id="svg" viewBox="0 0 1100 850" xmlns="http://www.w3.org/2000/svg"></svg>
  </div>
</div>

<div class="foot">
  <div>Rafter Mark: <span class="s" id="fMark">B1</span></div>
  <div>Length: <span class="s" id="fLength">—</span></div>
  <div>Purlin Clips: <span class="s" id="fClips">—</span></div>
  <div>Weight: <span class="s" id="fWeight">—</span></div>
  <div>Status: <span class="s" id="fStatus">READY</span></div>
</div>

<div class="bom" id="bomPanel">
  <button class="bom-x" onclick="this.parentElement.classList.remove('open')">✕</button>
  <h2>Bill of Materials</h2>
  <table id="bomTable">
    <thead>
      <tr><th>Mark</th><th>Qty</th><th>Description</th><th>Size</th><th>Material</th></tr>
    </thead>
    <tbody></tbody>
  </table>
</div>

<script>
// ═══════════════════════════════════════════════════════════════════════════════
// RAFTER CALCULATION & DRAWING ENGINE
// ═══════════════════════════════════════════════════════════════════════════════

var R = {
  // Configuration
  rafterMark: 'B1',
  buildingWidth_ft: 60,
  roofingOverhang_ft: 1,
  purlinSpacing_ft: 6,
  purlinType: 'z',  // 'z' or 'c'
  reinforced: true,
  zoom: 1.0,

  // Calculated values
  rafterLength_ft: 0,
  rafterLength_in: 0,
  needsSplice: false,
  clipCount: 0,
  clipPositions: [],
  weight_lbs: 0,

  // Constants
  CEE_SIZE: '14x4x10GA',
  BOX_WIDTH_IN: 14,
  BOX_DEPTH_IN: 8,
  P1_WIDTH_IN: 6,
  P1_LENGTH_IN: 10,
  P2_WIDTH_IN: 9,
  P2_LENGTH_IN: 24,
  SPLICE_MAX_FT: 53,
  WEIGHT_PER_FT: 10.83,
  MATERIAL_GRADE: 'G90 80 KSI',

  // Calculation
  calcRafterLength: function() {
    var use_z = this.purlinType === 'z';
    var z_deduction_in = use_z ? 7 : 0;
    var overhang_in = this.roofingOverhang_ft * 12;
    this.rafterLength_in = this.buildingWidth_ft * 12 - 2 * overhang_in - z_deduction_in;
    this.rafterLength_ft = this.rafterLength_in / 12;
    this.needsSplice = this.rafterLength_ft > this.SPLICE_MAX_FT;
  },

  calcClips: function() {
    var spacing_in = this.purlinSpacing_ft * 12;
    var n_clips = Math.max(2, Math.floor(this.rafterLength_in / spacing_in) + 1);
    this.clipCount = n_clips;

    this.clipPositions = [];
    // P2 at left
    this.clipPositions.push({pos_in: 0, type: 'p2', label: 'P2'});

    // Interior P1 clips evenly spaced
    if (n_clips > 2) {
      var actual_spacing = this.rafterLength_in / (n_clips - 1);
      for (var i = 1; i < n_clips - 1; i++) {
        this.clipPositions.push({pos_in: i * actual_spacing, type: 'p1', label: 'P1'});
      }
    }

    // P2 at right
    this.clipPositions.push({pos_in: this.rafterLength_in, type: 'p2', label: 'P2'});
  },

  calcWeight: function() {
    this.weight_lbs = this.rafterLength_ft * 2 * this.WEIGHT_PER_FT;
  },

  recalc: function() {
    this.calcRafterLength();
    this.calcClips();
    this.calcWeight();
  },

  fmt_ft_in: function(inches) {
    var ft = Math.floor(inches / 12);
    var in_rem = inches % 12;
    var int_part = Math.floor(in_rem);
    var frac_part = (in_rem - int_part) * 16;
    var frac_num = Math.round(frac_part);
    if (frac_num === 16) {
      int_part++;
      frac_num = 0;
    }
    var frac_str = '';
    if (frac_num > 0) {
      frac_str = (frac_num === 1) ? '1/16' :
                 (frac_num === 2) ? '1/8' :
                 (frac_num === 4) ? '1/4' :
                 (frac_num === 8) ? '1/2' :
                 (frac_num === 3) ? '3/16' :
                 (frac_num === 5) ? '5/16' :
                 (frac_num === 6) ? '3/8' :
                 (frac_num === 7) ? '7/16' :
                 (frac_num === 9) ? '9/16' :
                 (frac_num === 10) ? '5/8' :
                 (frac_num === 11) ? '11/16' :
                 (frac_num === 12) ? '3/4' :
                 (frac_num === 13) ? '13/16' :
                 (frac_num === 14) ? '7/8' :
                 (frac_num === 15) ? '15/16' : (frac_num + '/16');
    }
    return (ft > 0 ? ft + "'-" : '') + int_part + (frac_str ? '"' + frac_str : '"');
  }
};

// ═══════════════════════════════════════════════════════════════════════════════
// EVENT HANDLERS
// ═══════════════════════════════════════════════════════════════════════════════

function updateFromInputs() {
  R.rafterMark = document.getElementById('inRafterMark').value || 'B1';
  R.buildingWidth_ft = parseFloat(document.getElementById('inBuildingWidth').value) || 60;
  R.roofingOverhang_ft = parseFloat(document.getElementById('inRoofingOverhang').value) || 1;
  R.purlinSpacing_ft = parseFloat(document.getElementById('inPurlinSpacing').value) || 6;
  R.purlinType = document.getElementById('inPurlinType').value || 'z';
  R.zoom = parseFloat(document.getElementById('inZoom').value) || 1.0;
  R.recalc();
  updateFooter();
  drawRafterSheet();
  updateBom();
}

function toggleReinforced(isReinforced) {
  R.reinforced = isReinforced;
  document.getElementById('btnReinforced').classList.toggle('active', isReinforced);
  document.getElementById('btnNonReinforced').classList.toggle('active', !isReinforced);
  updateFromInputs();
}

function updateFooter() {
  document.getElementById('fMark').textContent = R.rafterMark;
  document.getElementById('fLength').textContent = R.fmt_ft_in(R.rafterLength_in);
  document.getElementById('fClips').textContent = R.clipCount;
  document.getElementById('fWeight').textContent = Math.round(R.weight_lbs) + ' lbs';
  document.getElementById('fStatus').textContent = R.needsSplice ? 'SPLICED' : 'SINGLE PIECE';
}

// ═══════════════════════════════════════════════════════════════════════════════
// SVG DRAWING
// ═══════════════════════════════════════════════════════════════════════════════

function drawRafterSheet() {
  var svg = document.getElementById('svg');
  svg.innerHTML = '';

  // Apply zoom transform
  var g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  g.setAttribute('transform', 'scale(' + R.zoom + ')');
  svg.appendChild(g);

  // White background
  var rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
  rect.setAttribute('width', 1100);
  rect.setAttribute('height', 850);
  rect.setAttribute('fill', '#FFF');
  g.appendChild(rect);

  // ── LAYOUT ──
  // Top View: y=60-320 (full width)
  // Side View: y=340-580, x=30-730
  // Section A-A: y=340-580, x=750-1070
  // Splice Detail: y=600-760, x=750-1070
  // BOM + Title: y=600-820, x=30-740

  drawTopView(g, 30, 60, 1040, 260);
  drawSideView(g, 30, 340, 700, 240);
  drawSectionAA(g, 750, 340, 320, 240);
  if (R.needsSplice) {
    drawSpliceDetail(g, 750, 600, 320, 160);
  } else {
    drawClipDetails(g, 750, 600, 320, 160);
  }
  drawBOM(g, 30, 600, 710, 160);
  drawTitleBlock(g, 750, 600, 320, 160);
}

function drawTopView(g, ox, oy, w, h) {
  // Top/plan view with purlin layout
  var margin = 20;
  var avail_w = w - 2 * margin;
  var scale = avail_w / R.rafterLength_in;

  var rw = R.rafterLength_in * scale;
  var rh = R.BOX_WIDTH_IN * scale;
  var rx = ox + margin;
  var ry = oy + h / 2 - rh / 2;

  // Rafter outline
  addRect(g, rx, ry, rw, rh, '#1a1a1a', 'none', 2);

  // Center seam
  addLine(g, rx, ry + rh / 2, rx + rw, ry + rh / 2, '#777', 0.5, [3,2]);

  // Clips
  var clip_h_p1 = R.P1_LENGTH_IN * scale;
  var clip_w_p1 = R.P1_WIDTH_IN * scale;
  var clip_h_p2 = R.P2_LENGTH_IN * scale;
  var clip_w_p2 = R.P2_WIDTH_IN * scale;

  for (var i = 0; i < R.clipPositions.length; i++) {
    var clip = R.clipPositions[i];
    var pos_x = rx + clip.pos_in * scale;
    if (clip.type === 'p2') {
      var cw = clip_w_p2;
      var ch = clip_h_p2;
      addRect(g, pos_x - cw/2, ry + rh/2 - ch/2, cw, ch, '#DD6600', '#FFDDAA', 1.2);
    } else {
      cw = clip_w_p1;
      ch = clip_h_p1;
      addRect(g, pos_x - cw/2, ry + rh/2 - ch/2, cw, ch, '#1a1a1a', '#E8E8F0', 1);
    }
  }

  // Splice line
  if (R.needsSplice) {
    var splice_in = R.rafterLength_in / 2;
    var splice_x = rx + splice_in * scale;
    addLine(g, splice_x, ry - 10, splice_x, ry + rh + 10, '#CC3333', 1.2, [4,3]);
    addText(g, splice_x, ry - 15, 'SPLICE @ ' + R.fmt_ft_in(splice_in), 6, 'bold', '#CC3333');
  }

  // Total length dimension
  addText(g, rx + rw / 2, ry + rh + 30, 'RAFTER: ' + R.fmt_ft_in(R.rafterLength_in), 7, 'bold', '#1a1a1a');

  // Material
  addText(g, rx + rw / 2, ry + rh / 2 + 2, 'CEE ' + R.CEE_SIZE + ' ' + R.MATERIAL_GRADE, 6, 'bold', '#555');

  // View label
  addText(g, ox + w / 2, oy + 10, 'TOP VIEW — PURLIN LAYOUT', 8, 'bold', '#1a1a1a');
}

function drawSideView(g, ox, oy, w, h) {
  // Side elevation
  var margin = 20;
  var avail_w = w - 2 * margin;
  var scale = avail_w / R.rafterLength_in;

  var rw = R.rafterLength_in * scale;
  var rd = R.BOX_DEPTH_IN * scale;
  var rx = ox + margin;
  var ry = oy + h / 2 - rd / 2;

  // Rafter body
  addRect(g, rx, ry, rw, rd, '#1a1a1a', '#F0F0F0', 2);

  // End plates
  var plate_w = 3 * scale;
  addRect(g, rx - plate_w, ry - 2, plate_w, rd + 4, '#1a1a1a', '#E0E0E0', 1.2);
  addRect(g, rx + rw, ry - 2, plate_w, rd + 4, '#1a1a1a', '#E0E0E0', 1.2);

  // Rebar (if reinforced)
  if (R.reinforced) {
    addLine(g, rx + 5, ry + 2, rx + rw - 5, ry + 2, '#CC3333', 1, [4,3]);
    addLine(g, rx + 5, ry + rd - 2, rx + rw - 5, ry + rd - 2, '#CC3333', 1, [4,3]);
    addText(g, rx + rw / 2, ry - 10, '#9 A706 REBAR (4 EA INSIDE)', 5, 'normal', '#CC3333');
  }

  // Splice location
  if (R.needsSplice) {
    var splice_in = R.rafterLength_in / 2;
    var splice_x = rx + splice_in * scale;
    addLine(g, splice_x, ry - 8, splice_x, ry + rd + 8, '#CC3333', 1, [4,2]);
    var sp_w = 18 * scale;
    addRect(g, splice_x - sp_w/2, ry + rd, sp_w, 3, '#AA4400', '#FFEECC', 1);
    addText(g, splice_x, ry + rd + 8, 'SPLICE PL 10GA G90 20-3/4" x 1\'-6"', 5, 'normal', '#AA4400');
  }

  // Stitch weld marks
  var n_marks = Math.max(3, Math.floor(rw / 40));
  for (var i = 1; i < n_marks; i++) {
    var wx = rx + i * (rw / n_marks);
    addLine(g, wx - 2, ry + rd, wx, ry + rd + 3, '#0055AA', 0.5);
    addLine(g, wx, ry + rd + 3, wx + 2, ry + rd, '#0055AA', 0.5);
  }
  addText(g, rx + rw * 0.7, ry + rd + 15, 'STITCH WELD 5/16 3-36 WPS-B', 5, 'normal', '#0055AA');

  // Dimensions
  addText(g, rx + rw / 2, ry - 20, R.fmt_ft_in(R.rafterLength_in), 7, 'bold', '#1a1a1a');
  addText(g, rx + rw + 10, ry + rd / 2, R.BOX_DEPTH_IN + '"', 6, 'normal', '#555');

  // Section marker
  addText(g, rx + rw * 0.35, ry - 25, 'A', 8, 'bold', '#CC3333');
  addText(g, rx + rw * 0.35, ry + rd + 25, 'A', 8, 'bold', '#CC3333');

  // View label
  addText(g, ox + w / 2, oy + 10, 'SIDE VIEW', 8, 'bold', '#1a1a1a');
}

function drawSectionAA(g, ox, oy, w, h) {
  // Cross-section through rafter body
  var margin = 10;
  var scale = (w - 2 * margin) / Math.max(R.BOX_WIDTH_IN, R.BOX_DEPTH_IN) * 0.6;

  var sw = R.BOX_WIDTH_IN * scale;
  var sd = R.BOX_DEPTH_IN * scale;
  var cx = ox + w / 2;
  var cy = oy + h / 2;

  // Box beam
  addRect(g, cx - sw/2, cy - sd/2, sw, sd, '#1a1a1a', '#F0F0F0', 2);

  // Inner void
  var wall_t = 4;
  addRect(g, cx - sw/2 + wall_t, cy - sd/2 + wall_t, sw - 2*wall_t, sd - 2*wall_t, '#777', 'none', 0.5);

  // Center seam
  addLine(g, cx, cy - sd/2, cx, cy + sd/2, '#1a1a1a', 1);

  // Rebar
  if (R.reinforced) {
    var inset = 5;
    var rebar_r = 2.5;
    var corners = [[-1, -1], [1, -1], [-1, 1], [1, 1]];
    for (var i = 0; i < corners.length; i++) {
      var rx = cx + corners[i][0] * (sw/2 - inset - rebar_r);
      var ry = cy + corners[i][1] * (sd/2 - inset - rebar_r);
      addCircle(g, rx, ry, rebar_r, '#993300', '#CC4400', 0.8);
    }
    addText(g, cx, cy - sd/2 - 15, '#9 REBAR (4 CORNERS)', 5, 'normal', '#CC3333');
  } else {
    addText(g, cx, cy - sd/2 - 15, 'NO REBAR (NON-REINFORCED)', 5, 'normal', '#555');
  }

  // Dimensions
  addText(g, cx, cy + sd/2 + 15, R.BOX_WIDTH_IN + '"', 6, 'normal', '#555');
  addText(g, cx + sw/2 + 12, cy, R.BOX_DEPTH_IN + '"', 6, 'normal', '#555');

  // View label
  addText(g, ox + w / 2, oy + 10, 'SECTION A-A', 8, 'bold', '#1a1a1a');
}

function drawSpliceDetail(g, ox, oy, w, h) {
  // Splice detail view
  var cx = ox + w / 2;
  var cy = oy + h / 2;

  var zoom = 2.0;
  var rd = R.BOX_DEPTH_IN * zoom;
  var gap = 3;

  // Left rafter piece
  addRect(g, cx - 35 - gap/2, cy - rd/2, 35, rd, '#1a1a1a', '#F0F0F0', 2);

  // Right rafter piece
  addRect(g, cx + gap/2, cy - rd/2, 35, rd, '#1a1a1a', '#F0F0F0', 2);

  // Splice plate on top
  var sp_w = 52;
  var sp_h = 4;
  addRect(g, cx - sp_w/2, cy + rd/2, sp_w, sp_h, '#AA4400', '#FFEECC', 1.5);

  // Tek screw marks
  for (var i = 0; i < 8; i++) {
    var sx = cx - sp_w/2 + (i + 0.5) * (sp_w / 8);
    addCircle(g, sx, cy + rd/2 + sp_h/2, 1, '#1a1a1a', '#1a1a1a', 0.5);
  }

  // Labels
  addText(g, cx, cy + rd/2 + sp_h + 10, 'SPLICE PL 10GA G90 20-3/4" x 1\'-6"', 5, 'normal', '#AA4400');
  addText(g, cx, cy + rd/2 + sp_h + 18, '8x #10 TEK SCREWS + FIELD WELD', 5, 'normal', '#1a1a1a');

  // View label
  addText(g, ox + w / 2, oy + 10, 'SPLICE DETAIL', 8, 'bold', '#1a1a1a');
}

function drawClipDetails(g, ox, oy, w, h) {
  // P1 and P2 clip details (when no splice needed)
  var cx = ox + w / 2;
  var cy = oy + h / 2;

  // P2 cap
  var p2w = R.P2_WIDTH_IN * 2.5;
  var p2h = R.P2_LENGTH_IN * 1.5;
  addRect(g, cx - p2w - 10, cy - p2h/2, p2w, p2h, '#DD6600', '#FFDDAA', 1.2);
  addText(g, cx - p2w/2 - 10, cy - p2h/2 - 8, 'P2 CAP PL 1/8" x 9" x 24"', 5, 'normal', '#AA4400');
  addText(g, cx - p2w/2 - 10, cy - p2h/2 - 16, 'WELDED ALL AROUND', 5, 'normal', '#1a1a1a');

  // P1 clip
  var p1w = R.P1_WIDTH_IN * 2.5;
  var p1h = R.P1_LENGTH_IN * 1.5;
  addRect(g, cx + 10, cy - p1h/2, p1w, p1h, '#1a1a1a', '#E8E8F0', 1);
  addText(g, cx + 10 + p1w/2, cy - p1h/2 - 8, 'P1 CLIP PL 1/8" x 6" x 10"', 5, 'normal', '#1a1a1a');
  addText(g, cx + 10 + p1w/2, cy - p1h/2 - 16, '8x TEK SCREWS WPS-C', 5, 'normal', '#1a1a1a');

  // View label
  addText(g, ox + w / 2, oy + 10, 'CLIP DETAILS', 8, 'bold', '#1a1a1a');
}

function drawBOM(g, ox, oy, w, h) {
  // BOM table
  addText(g, ox + w/2, oy + 8, 'BILL OF MATERIALS', 8, 'bold', '#1a1a1a');

  var row_h = 12;
  var col_ws = [w*0.12, w*0.08, w*0.40, w*0.20, w*0.20];
  var headers = ['MARK', 'QTY', 'DESCRIPTION', 'SIZE', 'MATERIAL'];

  // Header
  addRect(g, ox, oy + 15, w, row_h, '#1a1a1a', '#2A2A4A', 0.5);
  var x_pos = ox;
  for (var i = 0; i < headers.length; i++) {
    addText(g, x_pos + col_ws[i]/2, oy + 15 + row_h/2 + 2, headers[i], 5, 'bold', '#FFF');
    x_pos += col_ws[i];
  }

  // Rows
  var rows = [
    [R.rafterMark, '2', 'CEE Section (Box Beam)', R.CEE_SIZE, R.MATERIAL_GRADE],
    [R.rafterMark, '2', 'P2 Cap Clip', '1/8" x 9" x 24"', 'A572 Gr 50'],
    [R.rafterMark, String(Math.max(0, R.clipCount - 2)), 'P1 Interior Clip', '1/8" x 6" x 10"', 'A572 Gr 50'],
  ];

  if (R.reinforced) {
    rows.push([R.rafterMark, '4', 'Rebar (#9 A706)', '40\' stick', 'A706']);
  }

  if (R.needsSplice) {
    rows.push([R.rafterMark, '2', 'Splice Plate', '10GA G90 20-3/4" x 1\'-6"', 'G90']);
  }

  var y_pos = oy + 15 + row_h;
  for (var r = 0; r < rows.length; r++) {
    var row = rows[r];
    y_pos += row_h;
    if (r % 2 === 1) addRect(g, ox, y_pos - row_h, w, row_h, 'none', '#F5F5F5', 0.5);
    x_pos = ox;
    for (i = 0; i < row.length; i++) {
      addText(g, x_pos + col_ws[i]/2, y_pos - row_h/2 + 2, String(row[i]), 4.5, 'normal', '#333');
      x_pos += col_ws[i];
    }
  }
}

function drawTitleBlock(g, ox, oy, w, h) {
  // Title block
  var tb_w = w - 10;
  var tb_h = h - 10;
  var tb_x = ox + 5;
  var tb_y = oy + 5;

  addRect(g, tb_x, tb_y, tb_w, tb_h, '#1a1a1a', '#F9F9F9', 1);

  var y_off = 15;
  addText(g, tb_x + tb_w/2, tb_y + y_off, 'Structures America', 7, 'bold', '#1a1a1a');
  y_off += 10;
  addText(g, tb_x + tb_w/2, tb_y + y_off, '14369 FM 1314, Conroe, TX 77302', 5, 'normal', '#555');
  y_off += 12;

  var cfg = window.RAFTER_CONFIG || {};
  addText(g, tb_x + 5, tb_y + y_off, 'PROJECT: ' + (cfg.project_name || '—'), 5, 'normal', '#333');
  y_off += 8;
  addText(g, tb_x + 5, tb_y + y_off, 'JOB: ' + (cfg.job_code || '—'), 5, 'normal', '#333');
  y_off += 8;
  addText(g, tb_x + 5, tb_y + y_off, 'CUSTOMER: ' + (cfg.customer_name || '—'), 5, 'normal', '#333');
  y_off += 10;

  var today = new Date();
  var dateStr = (today.getMonth() + 1) + '/' + today.getDate() + '/' + today.getFullYear();
  addText(g, tb_x + 5, tb_y + y_off, 'DATE: ' + dateStr + '  REV: -  DRAWN: AUTO', 5, 'normal', '#333');
  y_off += 12;

  addText(g, tb_x + tb_w/2, tb_y + y_off, 'RAFTER ' + R.rafterMark + (R.needsSplice ? ' (SPLICED)' : ''), 7, 'bold', '#1a1a1a');
  y_off += 10;
  addText(g, tb_x + tb_w/2, tb_y + y_off, 'SHEET 1 OF 1', 5, 'normal', '#555');
}

// ═══════════════════════════════════════════════════════════════════════════════
// SVG HELPER FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

function addRect(g, x, y, w, h, stroke, fill, sw) {
  var rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
  rect.setAttribute('x', x);
  rect.setAttribute('y', y);
  rect.setAttribute('width', w);
  rect.setAttribute('height', h);
  if (stroke !== 'none') rect.setAttribute('stroke', stroke);
  if (fill !== 'none') rect.setAttribute('fill', fill);
  rect.setAttribute('stroke-width', sw || 1);
  g.appendChild(rect);
  return rect;
}

function addLine(g, x1, y1, x2, y2, stroke, sw, dash) {
  var line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
  line.setAttribute('x1', x1);
  line.setAttribute('y1', y1);
  line.setAttribute('x2', x2);
  line.setAttribute('y2', y2);
  line.setAttribute('stroke', stroke);
  line.setAttribute('stroke-width', sw || 1);
  if (dash) line.setAttribute('stroke-dasharray', dash.join(','));
  g.appendChild(line);
  return line;
}

function addCircle(g, cx, cy, r, stroke, fill, sw) {
  var circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
  circle.setAttribute('cx', cx);
  circle.setAttribute('cy', cy);
  circle.setAttribute('r', r);
  circle.setAttribute('stroke', stroke);
  circle.setAttribute('fill', fill);
  circle.setAttribute('stroke-width', sw || 0.5);
  g.appendChild(circle);
  return circle;
}

function addText(g, x, y, text, size, weight, color) {
  var txt = document.createElementNS('http://www.w3.org/2000/svg', 'text');
  txt.setAttribute('x', x);
  txt.setAttribute('y', y);
  txt.setAttribute('font-size', size);
  txt.setAttribute('font-weight', weight === 'bold' ? 700 : 400);
  txt.setAttribute('fill', color);
  txt.setAttribute('text-anchor', 'middle');
  txt.setAttribute('font-family', 'Arial, sans-serif');
  txt.textContent = text;
  g.appendChild(txt);
  return txt;
}

// ═══════════════════════════════════════════════════════════════════════════════
// BOM TABLE UPDATE
// ═══════════════════════════════════════════════════════════════════════════════

function updateBom() {
  var tbody = document.querySelector('#bomTable tbody');
  tbody.innerHTML = '';

  var rows = [
    [R.rafterMark, '2', 'CEE Section (Box Beam)', R.CEE_SIZE, R.MATERIAL_GRADE],
    [R.rafterMark, '2', 'Connection Plate', '3/4" x 14" x 26"', 'A572 Gr 50'],
    [R.rafterMark, '2', 'P2 Cap Clip', '1/8" x 9" x 24"', 'A572 Gr 50'],
  ];

  var n_p1 = Math.max(0, R.clipCount - 2);
  if (n_p1 > 0) {
    rows.push([R.rafterMark, String(n_p1), 'P1 Interior Clip', '1/8" x 6" x 10"', 'A572 Gr 50']);
  }

  if (R.reinforced) {
    rows.push([R.rafterMark, '4', 'Rebar (#9 A706)', '40\' stick', 'A706']);
  }

  if (R.needsSplice) {
    rows.push([R.rafterMark, '2', 'Splice Plate (FIELD)', '10GA G90 20-3/4" x 1\'-6"', 'G90']);
  }

  for (var i = 0; i < rows.length; i++) {
    var tr = document.createElement('tr');
    for (var j = 0; j < rows[i].length; j++) {
      var td = document.createElement('td');
      td.textContent = rows[i][j];
      tr.appendChild(td);
    }
    tbody.appendChild(tr);
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// PDF EXPORT
// ═══════════════════════════════════════════════════════════════════════════════

function savePdfToProject() {
  var statusEl = document.getElementById('savePdfStatus');
  statusEl.innerHTML = '<span class="spinner"></span> Generating PDF...';
  var jobCode = document.getElementById('inJobCode').value || 'RAFTER';

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

    // Fill white background — SVG has no background rect, CSS bg doesn't
    // carry into PDF, so without this the PDF renders on a black canvas.
    pdf.setFillColor(255, 255, 255);
    pdf.rect(0, 0, svgW, svgH, 'F');

    svg2pdf.svg2pdf(svgEl, pdf, { x: 0, y: 0, width: svgW, height: svgH }).then(function() {
      var pdfData = pdf.output('arraybuffer');
      var blob = new Blob([pdfData], { type: 'application/pdf' });

      var formData = new FormData();
      formData.append('job_code', jobCode);
      formData.append('drawing_type', 'rafter');
      formData.append('source', 'interactive');
      formData.append('pdf_file', blob, jobCode + '_B1.pdf');

      fetch('/api/shop-drawings/save-interactive-pdf', {
        method: 'POST',
        body: formData
      })
      .then(function(resp) {
        if (resp.ok) {
          statusEl.innerHTML = '<span style="color:#059669;">PDF saved to project</span>';
          setTimeout(function() { statusEl.innerHTML = ''; }, 3000);
        } else {
          statusEl.innerHTML = '<span style="color:#EF4444;">Upload failed</span>';
        }
      })
      .catch(function(err) {
        statusEl.innerHTML = '<span style="color:#EF4444;">Error: ' + err.message + '</span>';
      });
    }).catch(function(err) {
      statusEl.innerHTML = '<span style="color:#EF4444;">PDF render error: ' + err.message + '</span>';
    });
  } catch(err) {
    statusEl.innerHTML = '<span style="color:#EF4444;">Error: ' + err.message + '</span>';
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// INITIALIZATION
// ═══════════════════════════════════════════════════════════════════════════════

// Attach event listeners
document.getElementById('inRafterMark').addEventListener('change', updateFromInputs);
document.getElementById('inBuildingWidth').addEventListener('input', updateFromInputs);
document.getElementById('inRoofingOverhang').addEventListener('input', updateFromInputs);
document.getElementById('inPurlinSpacing').addEventListener('input', updateFromInputs);
document.getElementById('inPurlinType').addEventListener('change', updateFromInputs);
document.getElementById('inZoom').addEventListener('input', updateFromInputs);

// Initial draw
window.addEventListener('load', function() {
  applyServerConfig();
  updateFromInputs();
});
</script>

</body>
</html>
"""

# Export the template
__all__ = ['RAFTER_DRAWING_HTML']
