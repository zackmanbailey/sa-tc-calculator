"""
TitanForge -- Interactive Splice Plate Shop Drawing Template
============================================================
Full-featured SVG-based splice plate shop drawing served as an interactive page.
Pre-fills with project data via window.SPLICE_CONFIG injection.
Uses drawing_base.build_html_shell() for consistent dark-theme UI.

Splice Plate specs:
  - BS101 mark (beam splice)
  - 20.75" wide x 18" tall (standard)
  - 4 rows x 3 columns bolt pattern (13/16" holes for 3/4" A325 bolts)
  - Two plates per splice (sandwich the rafter webs)
  - Only used when a rafter exceeds 53' and must be spliced into two pieces
  - A36 steel plate, typical 3/8" thick
"""

import templates.drawing_base as drawing_base

# ═══════════════════════════════════════════════════════════════════════════════
# Component-specific JavaScript: draw() and helpers
# ═══════════════════════════════════════════════════════════════════════════════

SPLICE_JS = r"""
// ── Gauge thickness / weight lookup (plate gauge) ──
var GAUGE_THICK = {
  '3/16': 0.1875,
  '1/4':  0.250,
  '5/16': 0.3125,
  '3/8':  0.375,
  '1/2':  0.500
};

// Steel weight: 490 lb/ft^3 = 0.2836 lb/in^3
var STEEL_DENSITY = 0.2836;

// ── Apply server config to controls ──
function applyComponentConfig(cfg) {
  if (cfg.width_in) {
    var el = document.getElementById('inpWidth');
    if (el) el.value = cfg.width_in;
  }
  if (cfg.height_in) {
    var el = document.getElementById('inpHeight');
    if (el) el.value = cfg.height_in;
  }
  if (cfg.bolt_rows) {
    var el = document.getElementById('inpBoltRows');
    if (el) el.value = cfg.bolt_rows;
  }
  if (cfg.bolt_cols) {
    var el = document.getElementById('inpBoltCols');
    if (el) el.value = cfg.bolt_cols;
  }
  if (cfg.bolt_dia) {
    var el = document.getElementById('selBoltDia');
    if (el) el.value = cfg.bolt_dia;
  }
  if (cfg.gauge) {
    var el = document.getElementById('selGauge');
    if (el) el.value = cfg.gauge;
  }
  if (cfg.qty) {
    var el = document.getElementById('inpQty');
    if (el) el.value = cfg.qty;
  }
}

// ── Read current control values ──
function getParams() {
  var widthIn  = parseFloat(document.getElementById('inpWidth').value) || 20.75;
  var heightIn = parseFloat(document.getElementById('inpHeight').value) || 18;
  var boltRows = parseInt(document.getElementById('inpBoltRows').value) || 4;
  var boltCols = parseInt(document.getElementById('inpBoltCols').value) || 3;
  var boltDia  = document.getElementById('selBoltDia').value || '3/4';
  var gauge    = document.getElementById('selGauge').value || '3/8';
  var qty      = parseInt(document.getElementById('inpQty').value) || 1;

  var thick = GAUGE_THICK[gauge] || 0.375;

  // Bolt hole diameter: bolt + 1/16"
  var boltDiaNum = 0.75;
  if (boltDia === '5/8') boltDiaNum = 0.625;
  else if (boltDia === '3/4') boltDiaNum = 0.75;
  else if (boltDia === '7/8') boltDiaNum = 0.875;
  else if (boltDia === '1') boltDiaNum = 1.0;
  var holeDia = boltDiaNum + 0.0625;  // standard oversize 1/16"

  // Edge distances (minimum 1.5 x bolt dia per AISC)
  var edgeDist = Math.max(1.5, Math.ceil(boltDiaNum * 1.5 * 8) / 8);
  // Bolt spacing
  var hSpacing = boltCols > 1 ? (widthIn - 2 * edgeDist) / (boltCols - 1) : 0;
  var vSpacing = boltRows > 1 ? (heightIn - 2 * edgeDist) / (boltRows - 1) : 0;
  var boltsPerPlate = boltRows * boltCols;
  var boltsPerSplice = boltsPerPlate;  // bolts go through both plates at once
  var platesPerSplice = 2;  // top and bottom

  // Weight per plate
  var volIn3 = widthIn * heightIn * thick;
  var wtPlate = volIn3 * STEEL_DENSITY;
  var wtBolts = boltsPerSplice * (boltDiaNum * 2.5);  // approximate bolt weight
  var wtPerSplice = (wtPlate * platesPerSplice) + wtBolts;
  var totalWeight = wtPerSplice * qty;

  var mark = (window.SPLICE_CONFIG && window.SPLICE_CONFIG.mark) || 'BS101';

  return {
    widthIn: widthIn, heightIn: heightIn,
    boltRows: boltRows, boltCols: boltCols,
    boltDia: boltDia, boltDiaNum: boltDiaNum,
    holeDia: holeDia, edgeDist: edgeDist,
    hSpacing: hSpacing, vSpacing: vSpacing,
    boltsPerPlate: boltsPerPlate, boltsPerSplice: boltsPerSplice,
    platesPerSplice: platesPerSplice,
    gauge: gauge, thick: thick, qty: qty,
    wtPlate: wtPlate, wtBolts: wtBolts,
    wtPerSplice: wtPerSplice, totalWeight: totalWeight,
    mark: mark, material: 'A36'
  };
}

// ── Format fraction for display ──
function fmtFrac(val) {
  var whole = Math.floor(val);
  var frac = val - whole;
  if (frac < 0.02) return whole + '"';
  var n16 = Math.round(frac * 16);
  var num = n16, den = 16;
  while (num % 2 === 0 && den > 1) { num /= 2; den /= 2; }
  if (whole > 0) return whole + '-' + num + '/' + den + '"';
  return num + '/' + den + '"';
}

// ═══════════════════════════════════════════════
// MAIN DRAW FUNCTION
// ═══════════════════════════════════════════════
function draw() {
  var svg = document.getElementById('svg');
  while (svg.firstChild) svg.removeChild(svg.firstChild);
  svg.setAttribute('viewBox', '0 0 1100 850');

  var p = getParams();

  // Settings panel values
  var projName   = document.getElementById('setProjectName').value || 'PROJECT';
  var customer   = document.getElementById('setCustomer').value || '';
  var jobNum     = document.getElementById('setJobNumber').value || '';
  var drawingNum = document.getElementById('setDrawingNum').value || 'SD-001';
  var drawnBy    = document.getElementById('setDrawnBy').value || 'AUTO';
  var surfPrep   = document.getElementById('setSurfPrep').value || 'SSPC-SP2';

  // ════════════════════════════════════════════════════════════════════
  // ZONE 1: FRONT VIEW (x=30..420, y=25..380)
  // Flat plate showing full dimensions and bolt hole pattern
  // ════════════════════════════════════════════════════════════════════
  svg.appendChild($t(225, 22, 'FRONT VIEW - SPLICE PLATE', 'ttl'));

  var z1L = 80, z1T = 50;
  // Scale plate to fit zone
  var maxW = 300, maxH = 280;
  var sc = Math.min(maxW / p.widthIn, maxH / p.heightIn);
  var plateW = p.widthIn * sc;
  var plateH = p.heightIn * sc;
  // Center in zone
  var plateX = z1L + (maxW - plateW) / 2;
  var plateY = z1T + (maxH - plateH) / 2;

  // Plate outline
  var plateG = $g('hover-part', 'splice-plate');
  plateG.appendChild($r(plateX, plateY, plateW, plateH, 'conn-plate'));

  // Centerlines
  var cx = plateX + plateW / 2;
  var cy = plateY + plateH / 2;
  plateG.appendChild($l(cx, plateY - 12, cx, plateY + plateH + 12, 'center'));
  plateG.appendChild($l(plateX - 12, cy, plateX + plateW + 12, cy, 'center'));

  // Bolt holes
  for (var r = 0; r < p.boltRows; r++) {
    for (var c = 0; c < p.boltCols; c++) {
      var bx = plateX + p.edgeDist * sc + (p.boltCols > 1 ? c * p.hSpacing * sc : 0);
      var by = plateY + p.edgeDist * sc + (p.boltRows > 1 ? r * p.vSpacing * sc : 0);
      var holeR = (p.holeDia / 2) * sc;
      if (holeR < 3) holeR = 3;
      plateG.appendChild($c(bx, by, holeR, 'bolt'));
      // Cross-hair in bolt hole
      plateG.appendChild($l(bx - holeR * 0.7, by, bx + holeR * 0.7, by, 'dim'));
      plateG.appendChild($l(bx, by - holeR * 0.7, bx, by + holeR * 0.7, 'dim'));
    }
  }
  svg.appendChild(plateG);

  // ── Front view dimensions ──
  // Plate width (bottom)
  dimH(svg, plateX, plateX + plateW, plateY + plateH + 4, 22, fmtDec(p.widthIn, 2) + '"');

  // Plate height (right)
  dimV(svg, plateX + plateW + 4, plateY, plateY + plateH, 22, fmtDec(p.heightIn, 2) + '"');

  // Left edge distance (vertical, left side)
  var firstBoltY = plateY + p.edgeDist * sc;
  dimV(svg, plateX - 4, plateY, firstBoltY, -18, fmtFrac(p.edgeDist));

  // Top edge distance (horizontal, top)
  var firstBoltX = plateX + p.edgeDist * sc;
  dimH(svg, plateX, firstBoltX, plateY - 4, -16, fmtFrac(p.edgeDist));

  // Horizontal bolt spacing
  if (p.boltCols > 1) {
    var bx1 = plateX + p.edgeDist * sc;
    var bx2 = bx1 + p.hSpacing * sc;
    dimH(svg, bx1, bx2, plateY - 4, -30, fmtDec(p.hSpacing, 2) + '" TYP');
  }

  // Vertical bolt spacing
  if (p.boltRows > 1) {
    var by1 = plateY + p.edgeDist * sc;
    var by2 = by1 + p.vSpacing * sc;
    dimV(svg, plateX - 4, by1, by2, -32, fmtDec(p.vSpacing, 2) + '" TYP');
  }

  // Hole callout
  var holeTxt = p.boltCols * p.boltRows + 'x ' + fmtFrac(p.holeDia) + ' DIA HOLES';
  svg.appendChild($t(plateX + plateW / 2, plateY + plateH + 55, holeTxt, 'noteb', 'middle'));
  svg.appendChild($t(plateX + plateW / 2, plateY + plateH + 65, '(FOR ' + p.boltDia + '" A325 BOLTS)', 'note', 'middle'));

  // Scale note
  svg.appendChild($t(225, plateY + plateH + 80, 'SCALE: ' + fmtScale(sc), 'note', 'middle'));

  // Mark label
  svg.appendChild($t(plateX + plateW / 2, plateY - 20, p.mark, 'dim-bold', 'middle'));


  // ════════════════════════════════════════════════════════════════════
  // ZONE 2: SIDE VIEW (x=450..760, y=25..380)
  // Splice assembly from side — two rafter halves + splice plates
  // ════════════════════════════════════════════════════════════════════
  svg.appendChild($t(605, 22, 'SIDE VIEW - SPLICE ASSEMBLY', 'ttl'));

  var z2L = 470, z2T = 60;
  var rafterDepth = 80;    // visual rafter depth in px
  var rafterLen = 100;     // each half-rafter visible length
  var plateThPx = Math.max(8, p.thick * sc * 1.5);  // visual plate thickness
  var gapPx = 3;           // butt joint gap
  var z2CenterX = z2L + 140;
  var z2CenterY = z2T + 130;

  // Left rafter half
  var leftRafG = $g('hover-part', 'rafter-left');
  var lrX = z2CenterX - gapPx / 2 - rafterLen;
  var lrY = z2CenterY - rafterDepth / 2;
  leftRafG.appendChild($r(lrX, lrY, rafterLen, rafterDepth, 'cee'));
  leftRafG.appendChild($t(lrX + rafterLen / 2, lrY + rafterDepth / 2 + 3, 'RAFTER (L)', 'note', 'middle'));
  svg.appendChild(leftRafG);

  // Right rafter half
  var rightRafG = $g('hover-part', 'rafter-right');
  var rrX = z2CenterX + gapPx / 2;
  rightRafG.appendChild($r(rrX, lrY, rafterLen, rafterDepth, 'cee'));
  rightRafG.appendChild($t(rrX + rafterLen / 2, lrY + rafterDepth / 2 + 3, 'RAFTER (R)', 'note', 'middle'));
  svg.appendChild(rightRafG);

  // Butt joint indicator
  svg.appendChild($l(z2CenterX, lrY - 8, z2CenterX, lrY + rafterDepth + 8, 'cut-line'));
  svg.appendChild($t(z2CenterX, lrY - 12, 'BUTT JOINT', 'noteb', 'middle'));

  // Top splice plate
  var topPlateG = $g('hover-part', 'top-plate');
  var tpX = z2CenterX - (p.heightIn * sc * 0.45);
  var tpY = lrY - plateThPx - 2;
  var tpW = p.heightIn * sc * 0.9;
  if (tpW > 220) tpW = 220;
  tpX = z2CenterX - tpW / 2;
  topPlateG.appendChild($r(tpX, tpY, tpW, plateThPx, 'conn-plate'));
  topPlateG.appendChild($t(tpX + tpW / 2, tpY - 4, 'SPLICE PL (TOP)', 'noteb', 'middle'));
  svg.appendChild(topPlateG);

  // Bottom splice plate
  var botPlateG = $g('hover-part', 'bot-plate');
  var bpY = lrY + rafterDepth + 2;
  botPlateG.appendChild($r(tpX, bpY, tpW, plateThPx, 'conn-plate'));
  botPlateG.appendChild($t(tpX + tpW / 2, bpY + plateThPx + 10, 'SPLICE PL (BOT)', 'noteb', 'middle'));
  svg.appendChild(botPlateG);

  // Bolts through assembly (shown as vertical lines through both plates + rafter)
  var numVisibleBolts = Math.min(p.boltCols, 5);
  var boltSpacingPx = tpW / (numVisibleBolts + 1);
  for (var b = 1; b <= numVisibleBolts; b++) {
    var boltX = tpX + b * boltSpacingPx;
    // Bolt shaft line through entire assembly
    svg.appendChild($l(boltX, tpY - 3, boltX, bpY + plateThPx + 3, 'obj thin'));
    // Bolt head (top)
    svg.appendChild($l(boltX - 4, tpY - 3, boltX + 4, tpY - 3, 'obj med'));
    // Nut (bottom)
    svg.appendChild($r(boltX - 4, bpY + plateThPx + 1, 8, 4, 'gus'));
  }

  // Side view dimensions
  dimV(svg, tpX - 8, tpY, bpY + plateThPx, -18, 'ASSEMBLY');

  // Plate thickness callout
  svg.appendChild($l(tpX + tpW + 5, tpY, tpX + tpW + 30, tpY - 15, 'dim'));
  svg.appendChild($t(tpX + tpW + 32, tpY - 17, 'PL ' + p.gauge + '"', 'noteb'));

  // Rafter depth callout
  svg.appendChild($l(lrX - 5, lrY, lrX - 25, lrY, 'dim'));
  svg.appendChild($l(lrX - 5, lrY + rafterDepth, lrX - 25, lrY + rafterDepth, 'dim'));
  svg.appendChild($l(lrX - 20, lrY, lrX - 20, lrY + rafterDepth, 'dim'));
  svg.appendChild($t(lrX - 28, lrY + rafterDepth / 2 + 3, 'RAFTER', 'note', 'middle'));

  // Note about splice usage
  svg.appendChild($t(z2CenterX, bpY + plateThPx + 30, 'SPLICE REQUIRED WHEN RAFTER > 53\'-0"', 'warn-text', 'middle'));
  svg.appendChild($t(z2CenterX, bpY + plateThPx + 42, '2 PLATES PER SPLICE (TOP & BOTTOM)', 'noteb', 'middle'));


  // ════════════════════════════════════════════════════════════════════
  // ZONE 3: DETAILS (x=30..1080, y=400..670)
  // ════════════════════════════════════════════════════════════════════

  // ── DETAIL 1: Bolt hole pattern enlarged (x=30..380, y=400..660) ──
  svg.appendChild($t(200, 400, 'DETAIL 1: BOLT HOLE PATTERN', 'lblb', 'middle'));

  var d1L = 60, d1T = 420;
  var d1Sc = Math.min(160 / (p.hSpacing * Math.max(p.boltCols - 1, 1) + 2 * p.edgeDist),
                      180 / (p.vSpacing * Math.max(p.boltRows - 1, 1) + 2 * p.edgeDist));
  if (!isFinite(d1Sc) || d1Sc < 2) d1Sc = 8;
  if (d1Sc > 18) d1Sc = 18;

  var d1PatW = (p.hSpacing * (p.boltCols - 1) + 2 * p.edgeDist) * d1Sc;
  var d1PatH = (p.vSpacing * (p.boltRows - 1) + 2 * p.edgeDist) * d1Sc;
  var d1X = d1L + (300 - d1PatW) / 2;
  var d1Y = d1T + (200 - d1PatH) / 2;

  // Plate outline (dashed to show this is detail of the plate)
  svg.appendChild($e('rect', {x: d1X, y: d1Y, width: d1PatW, height: d1PatH,
    class: 'hidden', 'stroke-dasharray': '4,2'}));

  // Draw bolt holes with full detail
  for (var r = 0; r < p.boltRows; r++) {
    for (var c = 0; c < p.boltCols; c++) {
      var hx = d1X + p.edgeDist * d1Sc + c * p.hSpacing * d1Sc;
      var hy = d1Y + p.edgeDist * d1Sc + r * p.vSpacing * d1Sc;
      var hr = (p.holeDia / 2) * d1Sc;
      if (hr < 4) hr = 4;
      svg.appendChild($c(hx, hy, hr, 'bolt'));
      // Crosshairs
      svg.appendChild($l(hx - hr - 3, hy, hx + hr + 3, hy, 'center'));
      svg.appendChild($l(hx, hy - hr - 3, hx, hy + hr + 3, 'center'));
    }
  }

  // Detail dimensions - hole diameter callout (leader from first hole)
  var ldrX = d1X + p.edgeDist * d1Sc;
  var ldrY = d1Y + p.edgeDist * d1Sc;
  svg.appendChild($l(ldrX, ldrY, ldrX - 25, ldrY - 25, 'dim'));
  svg.appendChild($t(ldrX - 28, ldrY - 28, fmtFrac(p.holeDia) + ' DIA (TYP)', 'dimtxt'));

  // Detail edge distance
  if (p.boltCols > 0) {
    dimH(svg, d1X, d1X + p.edgeDist * d1Sc, d1Y + d1PatH + 2, 14, fmtFrac(p.edgeDist));
  }
  if (p.boltRows > 0) {
    dimV(svg, d1X - 2, d1Y, d1Y + p.edgeDist * d1Sc, -14, fmtFrac(p.edgeDist));
  }

  // Detail bolt spacing
  if (p.boltCols > 1) {
    var dx1 = d1X + p.edgeDist * d1Sc;
    var dx2 = dx1 + p.hSpacing * d1Sc;
    dimH(svg, dx1, dx2, d1Y - 4, -14, fmtDec(p.hSpacing, 2) + '"');
  }
  if (p.boltRows > 1) {
    var dy1 = d1Y + p.edgeDist * d1Sc;
    var dy2 = dy1 + p.vSpacing * d1Sc;
    dimV(svg, d1X + d1PatW + 4, dy1, dy2, 14, fmtDec(p.vSpacing, 2) + '"');
  }

  // Bolt spec note
  svg.appendChild($t(200, d1Y + d1PatH + 45, p.boltDia + '" A325-N STRUCTURAL BOLTS', 'noteb', 'middle'));
  svg.appendChild($t(200, d1Y + d1PatH + 57, p.boltsPerPlate + ' BOLTS PER PLATE', 'note', 'middle'));


  // ── DETAIL 2: Installed cross-section (x=400..700, y=400..660) ──
  svg.appendChild($t(550, 400, 'DETAIL 2: CROSS-SECTION AT SPLICE', 'lblb', 'middle'));

  var d2CX = 550, d2CY = 530;
  var csRafW = 120;   // rafter box beam width in px
  var csRafH = 80;    // rafter box beam height (web depth)
  var csWebTh = 6;    // visual web thickness
  var csPlateTh = Math.max(6, plateThPx);
  var csPlateW = csRafW + 30;  // plates extend beyond rafter

  // Rafter box beam cross-section (two webs, top & bottom flanges)
  var csG = $g('hover-part', 'cross-section');

  // Left web
  csG.appendChild($r(d2CX - csRafW/2, d2CY - csRafH/2, csWebTh, csRafH, 'cee'));
  // Right web
  csG.appendChild($r(d2CX + csRafW/2 - csWebTh, d2CY - csRafH/2, csWebTh, csRafH, 'cee'));
  // Top flange
  csG.appendChild($r(d2CX - csRafW/2, d2CY - csRafH/2, csRafW, csWebTh, 'cee'));
  // Bottom flange
  csG.appendChild($r(d2CX - csRafW/2, d2CY + csRafH/2 - csWebTh, csRafW, csWebTh, 'cee'));

  // Label rafter
  csG.appendChild($t(d2CX, d2CY + 3, 'RAFTER', 'note', 'middle'));
  svg.appendChild(csG);

  // Top splice plate (sits on top flange)
  var csTopY = d2CY - csRafH/2 - csPlateTh - 1;
  svg.appendChild($r(d2CX - csPlateW/2, csTopY, csPlateW, csPlateTh, 'conn-plate'));
  svg.appendChild($t(d2CX - csPlateW/2 - 5, csTopY + csPlateTh/2 + 2, 'PL', 'noteb', 'end'));

  // Bottom splice plate (under bottom flange)
  var csBotY = d2CY + csRafH/2 + 1;
  svg.appendChild($r(d2CX - csPlateW/2, csBotY, csPlateW, csPlateTh, 'conn-plate'));
  svg.appendChild($t(d2CX - csPlateW/2 - 5, csBotY + csPlateTh/2 + 2, 'PL', 'noteb', 'end'));

  // Bolts through webs
  var csBoltY1 = d2CY - csRafH * 0.25;
  var csBoltY2 = d2CY + csRafH * 0.25;
  [csBoltY1, csBoltY2].forEach(function(by) {
    // Left web bolt
    svg.appendChild($c(d2CX - csRafW/2 + csWebTh/2, by, 3, 'bolt'));
    // Right web bolt
    svg.appendChild($c(d2CX + csRafW/2 - csWebTh/2, by, 3, 'bolt'));
  });

  // Dimension: plate thickness
  dimV(svg, d2CX + csPlateW/2 + 4, csTopY, csTopY + csPlateTh, 14, p.gauge + '"');

  // Section label
  svg.appendChild($t(d2CX, d2CY + csRafH/2 + csPlateTh + 22, 'SECTION THROUGH SPLICE', 'note', 'middle'));
  svg.appendChild($t(d2CX, d2CY + csRafH/2 + csPlateTh + 34, '2 PLATES SANDWICH RAFTER WEBS', 'note', 'middle'));


  // ── DETAIL 3: Torque spec & installation notes (x=720..1070, y=400..660) ──
  svg.appendChild($t(895, 400, 'DETAIL 3: INSTALLATION NOTES', 'lblb', 'middle'));

  var d3X = 730, d3Y = 420;
  var noteLines = [
    'BOLT INSTALLATION REQUIREMENTS:',
    '',
    '1. BOLT TYPE: ASTM A325-N',
    '   Dia: ' + p.boltDia + '"  |  Hole: ' + fmtFrac(p.holeDia) + ' DIA',
    '',
    '2. INSTALLATION METHOD:',
    '   Snug-tight minimum per AISC/RCSC',
    '   Spec for Structural Joints',
    '',
    '3. TORQUE SPECIFICATION:',
    '   3/4" A325: 150 ft-lbs min (snug-tight)',
    '   Verify with calibrated wrench or',
    '   turn-of-nut method',
    '',
    '4. WASHER: F436 hardened washer',
    '   under nut (minimum)',
    '',
    '5. TIGHTENING SEQUENCE:',
    '   Start from center of pattern,',
    '   work outward in star pattern',
    '',
    '6. INSPECTION:',
    '   All bolts to be inspected prior',
    '   to final acceptance'
  ];

  // Installation notes box
  svg.appendChild($r(d3X, d3Y, 330, 240, 'obj thin'));

  noteLines.forEach(function(line, i) {
    var cls = (i === 0) ? 'noteb' : 'note';
    svg.appendChild($t(d3X + 8, d3Y + 14 + i * 10, line, cls));
  });

  // Bolt detail sketch (small bolt diagram)
  var bSkX = d3X + 240, bSkY = d3Y + 180;
  // Bolt head
  svg.appendChild($r(bSkX - 8, bSkY, 16, 5, 'gus'));
  // Shaft
  svg.appendChild($r(bSkX - 3, bSkY + 5, 6, 35, 'obj thin'));
  // Nut
  svg.appendChild($r(bSkX - 7, bSkY + 40, 14, 5, 'gus'));
  // Washer
  svg.appendChild($r(bSkX - 9, bSkY + 37, 18, 3, 'obj thin'));
  // Labels
  svg.appendChild($t(bSkX + 14, bSkY + 4, 'HEAD', 'note'));
  svg.appendChild($t(bSkX + 14, bSkY + 24, 'SHAFT', 'note'));
  svg.appendChild($t(bSkX + 14, bSkY + 40, 'WASHER', 'note'));
  svg.appendChild($t(bSkX + 14, bSkY + 48, 'NUT', 'note'));


  // ════════════════════════════════════════════════════════════════════
  // ZONE 4: BOM TABLE (x=450..1080, y=25..380) — right side area
  // Rendered as SVG table within the drawing
  // ════════════════════════════════════════════════════════════════════
  svg.appendChild($t(920, 22, 'BILL OF MATERIALS', 'lblb', 'middle'));

  var bomX = 770, bomY = 40;
  var bomW = 300, bomRH = 18;
  var bomCols = [0, 50, 80, 160, 210, 260];  // column offsets

  // Header row
  svg.appendChild($e('rect', {x: bomX, y: bomY, width: bomW, height: bomRH, fill: '#333', stroke: '#333'}));
  var bomHeaders = ['MARK', 'QTY', 'DESCRIPTION', 'SIZE', 'MATL', 'WT'];
  bomHeaders.forEach(function(h, i) {
    var ht = $t(bomX + bomCols[i] + 4, bomY + 13, h, 'note');
    ht.setAttribute('fill', '#FFF');
    svg.appendChild(ht);
  });

  // BOM data rows
  var bomRows = [
    { mk: p.mark, qty: p.platesPerSplice * p.qty, desc: 'Splice Plate',
      size: fmtDec(p.widthIn,2) + 'x' + fmtDec(p.heightIn,2) + 'x' + p.gauge, mat: 'A36',
      wt: fmtDec(p.wtPlate * p.platesPerSplice * p.qty, 1) },
    { mk: 'A325', qty: p.boltsPerSplice * p.qty, desc: p.boltDia + '" A325 Bolt',
      size: p.boltDia + '" x GRIP', mat: 'A325',
      wt: fmtDec(p.wtBolts * p.qty, 1) },
    { mk: 'F436', qty: p.boltsPerSplice * p.qty, desc: 'Hardened Washer',
      size: p.boltDia + '"', mat: 'F436', wt: '--' },
    { mk: 'A563', qty: p.boltsPerSplice * p.qty, desc: 'Heavy Hex Nut',
      size: p.boltDia + '"', mat: 'A563', wt: '--' }
  ];

  bomRows.forEach(function(row, i) {
    var ry = bomY + bomRH * (i + 1);
    svg.appendChild($l(bomX, ry, bomX + bomW, ry, 'dim'));
    var vals = [row.mk, row.qty, row.desc, row.size, row.mat, row.wt];
    vals.forEach(function(v, j) {
      svg.appendChild($t(bomX + bomCols[j] + 4, ry + 13, String(v), 'note'));
    });
  });

  // BOM box outline
  var bomTotalH = bomRH * (bomRows.length + 1);
  svg.appendChild($r(bomX, bomY, bomW, bomTotalH, 'obj thin'));

  // Total weight row
  var totY = bomY + bomTotalH;
  svg.appendChild($l(bomX, totY, bomX + bomW, totY, 'obj thin'));
  svg.appendChild($t(bomX + bomCols[4] + 4, totY + 13, 'TOTAL:', 'noteb'));
  svg.appendChild($t(bomX + bomCols[5] + 4, totY + 13, fmtDec(p.totalWeight, 1) + ' lbs', 'noteb'));
  svg.appendChild($r(bomX, totY, bomW, bomRH, 'obj thin'));

  // Splice count note
  svg.appendChild($t(bomX + bomW / 2, totY + 35,
    p.qty + ' SPLICE(S) x ' + p.platesPerSplice + ' PLATES = ' + (p.platesPerSplice * p.qty) + ' PLATES TOTAL',
    'noteb', 'middle'));


  // ════════════════════════════════════════════════════════════════════
  // ZONE 5: TITLE BLOCK (y=680..815)
  // ════════════════════════════════════════════════════════════════════
  drawTitleBlock(svg, {
    projName:     projName,
    customer:     customer,
    jobNum:       jobNum,
    drawingNum:   drawingNum,
    drawnBy:      drawnBy,
    surfPrep:     surfPrep,
    drawingTitle: 'SPLICE PLATE SHOP DRAWING',
    partMark:     p.mark,
    revision:     0,
    revHistory:   [],
    projectNotes: [
      'MATERIAL: ASTM A36 STEEL',
      'BOLTS: ASTM A325-N, ' + p.boltDia + '" DIA',
      'HOLES: ' + fmtFrac(p.holeDia) + ' DIA STD',
      'SURFACE PREP: ' + surfPrep,
      'PLATES: ' + p.platesPerSplice + ' PER SPLICE',
      'SPLICE REQD WHEN RAFTER > 53\'-0"',
      'SNUG-TIGHT MINIMUM INSTALLATION'
    ]
  });


  // ── Tooltip wiring ──
  var tip = document.getElementById('tip');
  svg.querySelectorAll('.hover-part').forEach(function(el) {
    el.addEventListener('mouseenter', function(e) {
      var part = el.dataset.part;
      var html = '';
      if (part === 'splice-plate') {
        html = '<b>Splice Plate - ' + p.mark + '</b><br>' +
          '<div class="r"><span class="k">Size:</span><span class="v">' + fmtDec(p.widthIn,2) + '" x ' + fmtDec(p.heightIn,2) + '"</span></div>' +
          '<div class="r"><span class="k">Thickness:</span><span class="v">' + p.gauge + '"</span></div>' +
          '<div class="r"><span class="k">Material:</span><span class="v">A36 Steel</span></div>' +
          '<div class="r"><span class="k">Bolt Pattern:</span><span class="v">' + p.boltRows + ' x ' + p.boltCols + '</span></div>' +
          '<div class="r"><span class="k">Bolts/Plate:</span><span class="v">' + p.boltsPerPlate + '</span></div>' +
          '<div class="r"><span class="k">Weight/Plate:</span><span class="v">' + fmtDec(p.wtPlate, 1) + ' lbs</span></div>';
      } else if (part === 'rafter-left' || part === 'rafter-right') {
        html = '<b>Rafter Half</b><br>' +
          '<div class="r"><span class="k">Note:</span><span class="v">Box beam rafter exceeding 53\' spliced into two halves</span></div>';
      } else if (part === 'top-plate' || part === 'bot-plate') {
        html = '<b>Splice Plate (' + (part === 'top-plate' ? 'Top' : 'Bottom') + ')</b><br>' +
          '<div class="r"><span class="k">Size:</span><span class="v">' + fmtDec(p.widthIn,2) + '" x ' + fmtDec(p.heightIn,2) + '" x ' + p.gauge + '"</span></div>' +
          '<div class="r"><span class="k">Bolts:</span><span class="v">' + p.boltsPerSplice + 'x ' + p.boltDia + '" A325</span></div>';
      } else if (part === 'cross-section') {
        html = '<b>Splice Cross-Section</b><br>' +
          '<div class="r"><span class="k">Assembly:</span><span class="v">2 plates sandwiching rafter webs</span></div>' +
          '<div class="r"><span class="k">Plate Thickness:</span><span class="v">' + p.gauge + '"</span></div>';
      }
      if (html) {
        tip.innerHTML = html;
        tip.style.display = 'block';
      }
    });
    el.addEventListener('mousemove', function(e) {
      tip.style.left = (e.clientX + 14) + 'px';
      tip.style.top = (e.clientY + 14) + 'px';
    });
    el.addEventListener('mouseleave', function() {
      tip.style.display = 'none';
    });
  });


  // ── Update footer stats ──
  var fDims = document.getElementById('fDims');
  if (fDims) fDims.textContent = fmtDec(p.widthIn,2) + '" x ' + fmtDec(p.heightIn,2) + '" x ' + p.gauge + '"';
  var fBolts = document.getElementById('fBolts');
  if (fBolts) fBolts.textContent = p.boltRows + 'x' + p.boltCols + ' (' + p.boltsPerPlate + ' per plate) ' + p.boltDia + '" A325';
  var fQty = document.getElementById('fQty');
  if (fQty) fQty.textContent = p.qty + ' splice(s), ' + (p.platesPerSplice * p.qty) + ' plates total';
  var fWt = document.getElementById('fWt');
  if (fWt) fWt.textContent = fmtDec(p.totalWeight, 1) + ' lbs';

  // ── Update BOM side panel ──
  updateBOM([
    { mk: p.mark, qty: p.platesPerSplice * p.qty, desc: 'Splice Plate',
      size: fmtDec(p.widthIn,2) + '"x' + fmtDec(p.heightIn,2) + '"x' + p.gauge + '"',
      mat: 'A36', wt: Math.round(p.wtPlate * p.platesPerSplice * p.qty) },
    { mk: 'A325', qty: p.boltsPerSplice * p.qty, desc: p.boltDia + '" Structural Bolt',
      size: p.boltDia + '" A325-N', mat: 'A325', wt: Math.round(p.wtBolts * p.qty) },
    { mk: 'F436', qty: p.boltsPerSplice * p.qty, desc: 'Hardened Washer',
      size: p.boltDia + '"', mat: 'F436', wt: 0 },
    { mk: 'A563', qty: p.boltsPerSplice * p.qty, desc: 'Heavy Hex Nut',
      size: p.boltDia + '"', mat: 'A563', wt: 0 }
  ]);
}
"""

# ═══════════════════════════════════════════════════════════════════════════════
# Controls HTML — splice-specific inputs
# ═══════════════════════════════════════════════════════════════════════════════

SPLICE_CONTROLS = """
    <div class="ctrl-group">
      <label>Width (in)</label>
      <input type="number" id="inpWidth" value="20.75" min="6" max="36" step="0.25" onchange="draw()">
    </div>
    <div class="ctrl-group">
      <label>Height (in)</label>
      <input type="number" id="inpHeight" value="18" min="6" max="36" step="0.25" onchange="draw()">
    </div>
    <div class="ctrl-group">
      <label>Bolt Rows</label>
      <input type="number" id="inpBoltRows" value="4" min="2" max="8" step="1" onchange="draw()">
    </div>
    <div class="ctrl-group">
      <label>Bolt Cols</label>
      <input type="number" id="inpBoltCols" value="3" min="2" max="6" step="1" onchange="draw()">
    </div>
    <div class="ctrl-group">
      <label>Bolt Dia</label>
      <select id="selBoltDia" onchange="draw()">
        <option value="5/8">5/8"</option>
        <option value="3/4" selected>3/4"</option>
        <option value="7/8">7/8"</option>
        <option value="1">1"</option>
      </select>
    </div>
    <div class="ctrl-group">
      <label>Gauge</label>
      <select id="selGauge" onchange="draw()">
        <option value="3/16">3/16"</option>
        <option value="1/4">1/4"</option>
        <option value="5/16">5/16"</option>
        <option value="3/8" selected>3/8"</option>
        <option value="1/2">1/2"</option>
      </select>
    </div>
    <div class="ctrl-group">
      <label>Qty</label>
      <input type="number" id="inpQty" value="1" min="1" max="20" step="1" onchange="draw()">
    </div>
    <button class="toggle-btn" onclick="window.print()">Print</button>
"""

# ═══════════════════════════════════════════════════════════════════════════════
# Footer HTML — splice-specific stats
# ═══════════════════════════════════════════════════════════════════════════════

SPLICE_FOOTER = """
  <div>Dimensions: <span class="s" id="fDims">--</span></div>
  <div>Bolt Pattern: <span class="s" id="fBolts">--</span></div>
  <div>Qty: <span class="s" id="fQty">--</span></div>
  <div>Total Weight: <span class="s" id="fWt">--</span></div>
"""

# ═══════════════════════════════════════════════════════════════════════════════
# Assemble final HTML via drawing_base
# ═══════════════════════════════════════════════════════════════════════════════

SPLICE_DRAWING_HTML = drawing_base.build_html_shell(
    title="Splice Plate Shop Drawing",
    drawing_type="splice",
    config_var="SPLICE_CONFIG",
    controls_html=SPLICE_CONTROLS,
    footer_html=SPLICE_FOOTER,
    drawing_js=SPLICE_JS,
)
