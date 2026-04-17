"""
TitanForge -- Interactive P2 Eave/Exterior Purlin Plate Shop Drawing
=====================================================================
Full-featured SVG-based shop drawing for P2 eave plates served as an
interactive page.  Pre-fills with project data via window.P2PLATE_CONFIG
injection.  Uses drawing_base.build_html_shell() for consistent dark-theme UI.

P2 Plate specs:
  - 9" wide x 24" long, 10GA (0.135") plate
  - Roll-formed from 9" 10GA plate coil (4.24 lbs/LFT, 3000 lb rolls)
  - 8 holes (4x2 pattern) for 1/4" DIA TEK screws
  - 9.5" extension wraps over rafter top flange (L-bend at 90 deg)
  - 2 per rafter (one at each eave end)
  - Used at exterior purlin positions where rafter meets the eave
"""

import templates.drawing_base as drawing_base

# ==============================================================================
# Component-specific JavaScript: draw() and helpers
# ==============================================================================

P2PLATE_JS = r"""
// ── P2 Plate gauge thickness lookup ──
var GAUGE_THICK = {
  '10GA': 0.135,
  '12GA': 0.105,
  '14GA': 0.075
};

var GAUGE_LBS_LFT = {
  '10GA': 4.24,
  '12GA': 3.40,
  '14GA': 2.45
};

// ── Apply server config to controls ──
function applyComponentConfig(cfg) {
  if (cfg.width_in) {
    var el = document.getElementById('inpWidth');
    if (el) el.value = cfg.width_in;
  }
  if (cfg.length_in) {
    var el = document.getElementById('inpLength');
    if (el) el.value = cfg.length_in;
  }
  if (cfg.extension_in) {
    var el = document.getElementById('inpExtension');
    if (el) el.value = cfg.extension_in;
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
  var widthIn = parseFloat(document.getElementById('inpWidth').value) || 9;
  var lengthIn = parseFloat(document.getElementById('inpLength').value) || 24;
  var extensionIn = parseFloat(document.getElementById('inpExtension').value) || 9.5;
  var gauge = document.getElementById('selGauge').value || '10GA';
  var qty = parseInt(document.getElementById('inpQty').value) || 2;
  var thick = GAUGE_THICK[gauge] || 0.135;
  var lbsLft = GAUGE_LBS_LFT[gauge] || 4.24;

  // Weight: flat plate portion + extension
  var totalLenIn = lengthIn; // plate length (extension is vertical wrap, same material width)
  var wtEach = lbsLft * (totalLenIn / 12);
  var mark = (window.P2PLATE_CONFIG && window.P2PLATE_CONFIG.mark) || 'P2';

  return {
    widthIn: widthIn,
    lengthIn: lengthIn,
    extensionIn: extensionIn,
    gauge: gauge,
    thick: thick,
    lbsLft: lbsLft,
    qty: qty,
    wtEach: wtEach,
    wtTotal: wtEach * qty,
    mark: mark,
    material: '10GA PLATE',
    coating: 'G90'
  };
}

// ── Hole pattern constants (4x2) ──
// Edge distances and spacing for 8 holes on 24"x9" plate
// 4 holes across (along 24" length), 2 rows (along 9" width)
var HOLE_DIA = 0.281; // 9/32" clearance for 1/4" TEK screws

function getHolePattern(lengthIn, widthIn) {
  // Edge distances
  var edgeX = 2.0;   // from short edge to first hole center
  var edgeY = 1.5;   // from long edge to first hole center

  // Spacing
  var spacingX = (lengthIn - 2 * edgeX) / 3; // 3 gaps for 4 holes across
  var spacingY = widthIn - 2 * edgeY;         // 1 gap for 2 rows

  var holes = [];
  for (var row = 0; row < 2; row++) {
    for (var col = 0; col < 4; col++) {
      holes.push({
        x: edgeX + col * spacingX,
        y: edgeY + row * spacingY
      });
    }
  }
  return {
    holes: holes,
    edgeX: edgeX,
    edgeY: edgeY,
    spacingX: spacingX,
    spacingY: spacingY,
    holeDia: HOLE_DIA
  };
}

// ═══════════════════════════════════════════════════════════════════════
// MAIN DRAW FUNCTION
// ═══════════════════════════════════════════════════════════════════════

function draw() {
  var svg = document.getElementById('svg');
  svg.innerHTML = '';
  var p = getParams();
  var hp = getHolePattern(p.lengthIn, p.widthIn);

  // ── Drawing border ──
  svg.appendChild($r(10, 10, 1080, 660, 'obj thin'));

  // ═══════════════════════════════════════════════════════════
  // ZONE 1 — FRONT VIEW (top-left, 20,30 to 520,340)
  // Flat plate view: 24" x 9" with 8-hole pattern
  // ═══════════════════════════════════════════════════════════

  var z1x = 40, z1y = 50;
  svg.appendChild($t(z1x + 200, z1y - 8, 'FRONT VIEW - P2 EAVE PLATE', 'lblb', 'middle'));

  // Scale plate to fit zone: ~400px wide x ~200px tall
  var plateScaleX = 380 / p.lengthIn;
  var plateScaleY = 180 / p.widthIn;
  var plateScale = Math.min(plateScaleX, plateScaleY);

  var pW = p.lengthIn * plateScale;  // drawn width (length dimension)
  var pH = p.widthIn * plateScale;   // drawn height (width dimension)
  var px = z1x + (400 - pW) / 2;
  var py = z1y + 20 + (200 - pH) / 2;

  // Plate outline
  var plateG = $g('hover-part', 'p2plate');
  plateG.appendChild($e('rect', {x: px, y: py, width: pW, height: pH, class: 'conn-plate', rx: 1}));

  // Center lines
  plateG.appendChild($l(px + pW/2, py - 8, px + pW/2, py + pH + 8, 'center'));
  plateG.appendChild($l(px - 8, py + pH/2, px + pW + 8, py + pH/2, 'center'));

  // Draw 8 holes
  hp.holes.forEach(function(h) {
    var hx = px + h.x * plateScale;
    var hy = py + h.y * plateScale;
    var hr = (hp.holeDia / 2) * plateScale * 3; // exaggerated for visibility
    if (hr < 2.5) hr = 2.5;
    plateG.appendChild($c(hx, hy, hr, 'bolt'));
    // Cross-hair inside hole
    plateG.appendChild($l(hx - hr*0.7, hy, hx + hr*0.7, hy, 'center'));
    plateG.appendChild($l(hx, hy - hr*0.7, hx, hy + hr*0.7, 'center'));
  });

  // Bend line (dashed) showing where the L-bend starts
  var bendLineX = px + pW; // right edge is the bend location
  plateG.appendChild($l(bendLineX - 2, py - 4, bendLineX - 2, py + pH + 4, 'hidden'));
  svg.appendChild(plateG);

  // Label bend line
  svg.appendChild($t(bendLineX + 4, py + pH/2, 'BEND', 'note'));
  svg.appendChild($t(bendLineX + 4, py + pH/2 + 8, 'LINE', 'note'));

  // ── Dimensions for front view ──
  // Overall length (horizontal)
  dimH(svg, px, px + pW, py + pH, 25, fmtDec(p.lengthIn) + '"');
  // Overall width (vertical)
  dimV(svg, px, py, py + pH, -25, fmtDec(p.widthIn) + '"');

  // Hole edge distances and spacing
  var h0x = px + hp.edgeX * plateScale;
  var h1x = px + (hp.edgeX + hp.spacingX) * plateScale;
  var hLastX = px + (hp.edgeX + 3 * hp.spacingX) * plateScale;
  var h0y = py + hp.edgeY * plateScale;
  var h1y = py + (hp.edgeY + hp.spacingY) * plateScale;

  // Edge distance - left
  dimH(svg, px, h0x, py, -18, fmtDec(hp.edgeX) + '"');
  // Hole spacing X (one span)
  dimH(svg, h0x, h1x, py, -18, fmtDec(hp.spacingX, 2) + '"');
  // Edge distance - right
  dimH(svg, hLastX, px + pW, py, -18, fmtDec(hp.edgeX) + '"');

  // Edge distance - top
  dimV(svg, px + pW, py, h0y, 20, fmtDec(hp.edgeY) + '"');
  // Row spacing
  dimV(svg, px + pW, h0y, h1y, 20, fmtDec(hp.spacingY, 2) + '"');
  // Edge distance - bottom
  dimV(svg, px + pW, h1y, py + pH, 20, fmtDec(hp.edgeY) + '"');

  // Hole callout
  svg.appendChild($t(px + pW/2, py + pH + 52, '(8) 9/32" DIA HOLES FOR 1/4" TEK SCREWS', 'noteb', 'middle'));
  svg.appendChild($t(px + pW/2, py + pH + 62, '4x2 PATTERN', 'note', 'middle'));

  // Material note
  svg.appendChild($t(px + pW/2, py + pH + 75, p.gauge + ' PLATE  (' + fmtDec(p.thick, 3) + '" THK)', 'noteb', 'middle'));

  // ═══════════════════════════════════════════════════════════
  // ZONE 2 — SIDE VIEW (top-right, 550,30 to 1070,340)
  // L-bend profile: main plate + 9.5" extension
  // ═══════════════════════════════════════════════════════════

  var z2x = 570, z2y = 50;
  svg.appendChild($t(z2x + 230, z2y - 8, 'SIDE VIEW - L-BEND PROFILE', 'lblb', 'middle'));

  // Scale: fit 24" + 9.5" vertically in ~260px
  var totalProfileH = p.widthIn + p.extensionIn;
  var sideScale = 240 / totalProfileH;
  var sideThick = p.thick * sideScale;
  if (sideThick < 2) sideThick = 2;

  // Plate horizontal portion (the 9" width shown as horizontal span)
  var sideW = p.widthIn * sideScale;     // horizontal span of plate
  var sideExt = p.extensionIn * sideScale; // vertical extension

  var sx = z2x + 80;
  var sy = z2y + 40;

  var sideG = $g('hover-part', 'p2side');

  // Main horizontal plate (outer rect)
  sideG.appendChild($e('rect', {
    x: sx, y: sy,
    width: sideW, height: sideThick,
    class: 'conn-plate'
  }));

  // Vertical extension going down from right edge
  sideG.appendChild($e('rect', {
    x: sx + sideW - sideThick, y: sy,
    width: sideThick, height: sideExt,
    class: 'conn-plate'
  }));

  // Bend radius indicator (small arc at corner)
  var bendCX = sx + sideW - sideThick;
  var bendCY = sy + sideThick;
  sideG.appendChild($p(
    'M ' + bendCX + ' ' + (bendCY - 6) +
    ' A 6 6 0 0 1 ' + (bendCX + 6) + ' ' + bendCY,
    'dim'
  ));

  svg.appendChild(sideG);

  // 90-degree angle annotation
  svg.appendChild($t(bendCX - 18, bendCY + 16, '90\u00B0', 'lblb'));

  // Dimension: plate width (horizontal span)
  dimH(svg, sx, sx + sideW, sy, -20, fmtDec(p.widthIn) + '"');

  // Dimension: extension (vertical)
  dimV(svg, sx + sideW - sideThick, sy, sy + sideExt, 30, fmtDec(p.extensionIn) + '"');

  // Dimension: material thickness
  dimV(svg, sx, sy, sy + sideThick, -22, fmtDec(p.thick, 3) + '"');

  // Labels
  svg.appendChild($t(sx + sideW/2 - 10, sy - 28, 'PLATE WIDTH', 'note', 'middle'));
  svg.appendChild($t(sx + sideW + 40, sy + sideExt/2, 'EXTENSION', 'note', 'middle'));
  svg.appendChild($t(sx + sideW + 40, sy + sideExt/2 + 10, 'WRAPS OVER', 'note', 'middle'));
  svg.appendChild($t(sx + sideW + 40, sy + sideExt/2 + 20, 'RAFTER FLANGE', 'note', 'middle'));

  // Rafter flange ghost (context)
  var rfY = sy + sideThick;
  var rfW = 50;
  var rfH = sideExt - 10;
  svg.appendChild($e('rect', {
    x: sx + sideW - sideThick - rfW, y: rfY,
    width: rfW, height: rfH,
    class: 'hidden', fill: 'none'
  }));
  svg.appendChild($t(sx + sideW - sideThick - rfW/2, rfY + rfH/2 + 3, 'RAFTER', 'note', 'middle'));
  svg.appendChild($t(sx + sideW - sideThick - rfW/2, rfY + rfH/2 + 12, 'FLANGE', 'note', 'middle'));

  // ═══════════════════════════════════════════════════════════
  // ZONE 3 — DETAILS (bottom area, 20,360 to 1070,660)
  // ═══════════════════════════════════════════════════════════

  var z3y = 365;
  svg.appendChild($l(20, z3y - 5, 1080, z3y - 5, 'obj hair'));

  // ── DETAIL 1: Enlarged hole pattern (left) ──
  var d1x = 40, d1y = z3y + 15;
  svg.appendChild($t(d1x + 140, d1y - 5, 'DETAIL 1 - HOLE PATTERN', 'lblb', 'middle'));

  var detScale = 9.5; // enlarged scale
  var detPW = p.lengthIn * detScale * 0.48;
  var detPH = p.widthIn * detScale * 0.48;
  if (detPW > 280) { detScale = 280 / (p.lengthIn * 0.48); detPW = 280; detPH = p.widthIn * detScale * 0.48; }

  var detPx = d1x;
  var detPy = d1y + 10;
  var dSc = detPW / p.lengthIn;

  // Plate outline (detail)
  svg.appendChild($r(detPx, detPy, detPW, detPH, 'obj med'));

  // Draw holes in detail
  hp.holes.forEach(function(h) {
    var hx = detPx + h.x * dSc;
    var hy = detPy + h.y * dSc;
    var hr = 3.5;
    svg.appendChild($c(hx, hy, hr, 'bolt'));
    svg.appendChild($l(hx - 5, hy, hx + 5, hy, 'center'));
    svg.appendChild($l(hx, hy - 5, hx, hy + 5, 'center'));
  });

  // Detail dims
  var dh0x = detPx + hp.edgeX * dSc;
  var dh1x = detPx + (hp.edgeX + hp.spacingX) * dSc;
  var dh0y = detPy + hp.edgeY * dSc;
  var dh1y = detPy + (hp.edgeY + hp.spacingY) * dSc;

  dimH(svg, detPx, dh0x, detPy, -12, fmtDec(hp.edgeX) + '"');
  dimH(svg, dh0x, dh1x, detPy, -12, fmtDec(hp.spacingX, 2) + '" TYP');
  dimV(svg, detPx, detPy, dh0y, -14, fmtDec(hp.edgeY) + '"');
  dimV(svg, detPx, dh0y, dh1y, -14, fmtDec(hp.spacingY, 2) + '"');

  svg.appendChild($t(detPx + detPW/2, detPy + detPH + 16, '9/32" DIA (TYP 8 HOLES)', 'noteb', 'middle'));
  svg.appendChild($t(detPx + detPW/2, detPy + detPH + 26, '1/4" DIA TEK SCREWS', 'note', 'middle'));

  // ── DETAIL 2: Installed view — plate at eave (center) ──
  var d2x = 380, d2y = z3y + 15;
  svg.appendChild($t(d2x + 140, d2y - 5, 'DETAIL 2 - INSTALLED VIEW', 'lblb', 'middle'));

  var ivG = $g('hover-part', 'p2installed');
  var ivScale = 3.2;

  // Rafter (vertical C-section, simplified)
  var raftX = d2x + 60, raftY = d2y + 20;
  var raftW = 20, raftH = 180;
  ivG.appendChild($e('rect', {x: raftX, y: raftY, width: raftW, height: raftH, class: 'cee'}));
  svg.appendChild($t(raftX + raftW/2, raftY + raftH/2, 'R', 'lblb', 'middle'));
  svg.appendChild($t(raftX + raftW/2, raftY + raftH/2 + 10, 'A', 'lblb', 'middle'));
  svg.appendChild($t(raftX + raftW/2, raftY + raftH/2 + 20, 'F', 'lblb', 'middle'));
  svg.appendChild($t(raftX + raftW/2, raftY + raftH/2 + 30, 'T', 'lblb', 'middle'));

  // Purlin (horizontal Z, coming from left)
  var purX = d2x, purY = raftY + 20;
  var purW = 60, purH = 14;
  ivG.appendChild($e('rect', {x: purX, y: purY, width: purW, height: purH, class: 'cee'}));
  svg.appendChild($t(purX + purW/2, purY + purH/2 + 3, 'PURLIN', 'note', 'middle'));

  // P2 Plate at eave position (wrapping over rafter flange)
  var plateIvX = raftX - 2;
  var plateIvY = purY - 4;
  var plateIvW = raftW + 8;
  var plateIvH = 3;
  // Horizontal portion
  ivG.appendChild($e('rect', {
    x: plateIvX, y: plateIvY,
    width: plateIvW, height: plateIvH,
    fill: '#F6AE2D', 'fill-opacity': '0.35', stroke: '#C4960B', 'stroke-width': '1.5'
  }));
  // Extension wrap (vertical, going down right side of rafter)
  var extIvH = 45;
  ivG.appendChild($e('rect', {
    x: raftX + raftW - 1, y: plateIvY,
    width: plateIvH, height: extIvH,
    fill: '#F6AE2D', 'fill-opacity': '0.35', stroke: '#C4960B', 'stroke-width': '1.5'
  }));

  // TEK screw indicators
  var tekR = 2;
  [plateIvX + 6, plateIvX + plateIvW - 8].forEach(function(tx) {
    [plateIvY + 1.5].forEach(function(ty) {
      ivG.appendChild($c(tx, ty, tekR, 'bolt'));
    });
  });

  svg.appendChild(ivG);

  // Labels
  svg.appendChild($t(plateIvX - 20, plateIvY + 2, 'P2', 'lblb'));
  svg.appendChild($t(plateIvX - 28, plateIvY + 12, 'PLATE', 'lblb'));

  var arrowX = raftX + raftW + 6;
  svg.appendChild($l(arrowX, plateIvY + extIvH, arrowX + 25, plateIvY + extIvH, 'dim'));
  svg.appendChild($t(arrowX + 28, plateIvY + extIvH + 3, fmtDec(p.extensionIn) + '"', 'dimtxt'));
  svg.appendChild($t(arrowX + 28, plateIvY + extIvH + 12, 'EXT', 'note'));

  svg.appendChild($t(d2x + 130, d2y + 210, 'EAVE CONNECTION', 'noteb', 'middle'));
  svg.appendChild($t(d2x + 130, d2y + 220, '2 PER RAFTER (EACH EAVE END)', 'note', 'middle'));

  // ── DETAIL 3: Bend/extension detail (right) ──
  var d3x = 740, d3y = z3y + 15;
  svg.appendChild($t(d3x + 140, d3y - 5, 'DETAIL 3 - BEND DETAIL', 'lblb', 'middle'));

  var bdScale = 6;
  var bdW = p.widthIn * bdScale;  // horizontal = plate width
  var bdExt = p.extensionIn * bdScale;
  if (bdW > 200) { bdScale = 200 / p.widthIn; bdW = 200; bdExt = p.extensionIn * bdScale; }
  if (bdExt > 200) { bdScale = 200 / p.extensionIn; bdExt = 200; bdW = p.widthIn * bdScale; }
  var bdThick = Math.max(p.thick * bdScale, 2.5);

  var bdX = d3x + 40, bdY = d3y + 30;

  // Outer profile of L-bend
  svg.appendChild($p(
    'M ' + bdX + ' ' + bdY +
    ' L ' + (bdX + bdW) + ' ' + bdY +
    ' L ' + (bdX + bdW) + ' ' + (bdY + bdExt) +
    ' L ' + (bdX + bdW - bdThick) + ' ' + (bdY + bdExt) +
    ' L ' + (bdX + bdW - bdThick) + ' ' + (bdY + bdThick) +
    ' L ' + bdX + ' ' + (bdY + bdThick) +
    ' Z',
    'conn-plate'
  ));

  // Bend radius arc annotation
  var arcCX = bdX + bdW - bdThick;
  var arcCY = bdY + bdThick;
  var arcR = 12;
  svg.appendChild($p(
    'M ' + (arcCX + arcR) + ' ' + arcCY +
    ' A ' + arcR + ' ' + arcR + ' 0 0 0 ' + arcCX + ' ' + (arcCY + arcR),
    'dim'
  ));
  svg.appendChild($t(arcCX + arcR + 4, arcCY + arcR - 2, '90\u00B0', 'lblb'));

  // Dims
  dimH(svg, bdX, bdX + bdW, bdY, -16, fmtDec(p.widthIn) + '"');
  dimV(svg, bdX + bdW, bdY, bdY + bdExt, 22, fmtDec(p.extensionIn) + '"');
  dimH(svg, bdX, bdX + bdW, bdY + bdThick, bdThick + 12, fmtDec(p.thick, 3) + '" THK');

  // Material note
  svg.appendChild($t(d3x + 140, d3y + Math.max(bdExt, 160) + 50, 'BEND AT 90\u00B0', 'noteb', 'middle'));
  svg.appendChild($t(d3x + 140, d3y + Math.max(bdExt, 160) + 62, 'INSIDE RADIUS = 2x MATERIAL THK', 'note', 'middle'));
  svg.appendChild($t(d3x + 140, d3y + Math.max(bdExt, 160) + 72, p.gauge + ' PLATE (' + fmtDec(p.thick, 3) + '")', 'note', 'middle'));

  // ═══════════════════════════════════════════════════════════
  // ZONE 4 — BOM TABLE (drawn in SVG, bottom-right of details)
  // ═══════════════════════════════════════════════════════════

  var bomX = 740, bomY = z3y + 230;
  svg.appendChild($e('rect', {x: bomX, y: bomY, width: 320, height: 16, fill: '#333', stroke: '#333'}));
  var bomHeaders = ['MARK', 'QTY', 'SIZE', 'MATERIAL', 'GAUGE', 'WT (LBS)'];
  var bomColX = [bomX+8, bomX+50, bomX+85, bomX+170, bomX+235, bomX+280];
  bomHeaders.forEach(function(h, i) {
    var th = $t(bomColX[i], bomY + 12, h, 'note');
    th.setAttribute('fill', '#FFF');
    svg.appendChild(th);
  });

  // Data row
  var rowY = bomY + 28;
  var bomVals = [
    p.mark,
    String(p.qty),
    fmtDec(p.lengthIn) + '" x ' + fmtDec(p.widthIn) + '"',
    'PLATE',
    p.gauge,
    fmtDec(p.wtEach, 1)
  ];
  bomVals.forEach(function(v, i) {
    svg.appendChild($t(bomColX[i], rowY, v, 'lbl'));
  });

  // Total row
  svg.appendChild($l(bomX, rowY + 6, bomX + 320, rowY + 6, 'obj hair'));
  svg.appendChild($t(bomColX[4], rowY + 18, 'TOTAL:', 'noteb'));
  svg.appendChild($t(bomColX[5], rowY + 18, fmtDec(p.wtTotal, 1) + ' lbs', 'lblb'));

  svg.appendChild($e('rect', {x: bomX, y: bomY, width: 320, height: 50, class: 'obj thin'}));

  // ═══════════════════════════════════════════════════════════
  // ZONE 5 — TITLE BLOCK (y=680..815)
  // ═══════════════════════════════════════════════════════════

  drawTitleBlock(svg, {
    projName:     document.getElementById('setProjectName').value || 'PROJECT',
    customer:     document.getElementById('setCustomer').value || '',
    jobNum:       document.getElementById('setJobNumber').value || '',
    drawingNum:   document.getElementById('setDrawingNum').value || 'SD-P2-001',
    drawnBy:      document.getElementById('setDrawnBy').value || 'AUTO',
    surfPrep:     document.getElementById('setSurfPrep').value || 'SSPC-SP2',
    drawingTitle: 'P2 EAVE/EXTERIOR PURLIN PLATE',
    partMark:     p.mark,
    revision:     0,
    revHistory:   [],
    projectNotes: [
      'MATERIAL: ' + p.gauge + ' PLATE (' + fmtDec(p.thick, 3) + '" THK)',
      'HOLES: (8) 9/32" DIA FOR 1/4" TEK SCREWS',
      'BEND: 90\u00B0 L-BEND, ' + fmtDec(p.extensionIn) + '" EXTENSION',
      'COIL: 9" 10GA PLATE COIL, 4.24 LBS/LFT',
      'ROLL SIZE: 3000 LB ROLLS',
      'QTY: ' + p.qty + ' (' + (p.qty / 2) + ' RAFTERS x 2 EAVE ENDS)',
      'WEIGHT EACH: ' + fmtDec(p.wtEach, 1) + ' LBS',
      'TOTAL WEIGHT: ' + fmtDec(p.wtTotal, 1) + ' LBS'
    ]
  });

  // ═══════════════════════════════════════════════════════════
  // BOM SIDE PANEL
  // ═══════════════════════════════════════════════════════════

  updateBOM([
    {
      mk: p.mark,
      qty: p.qty,
      desc: 'P2 Eave Plate',
      size: fmtDec(p.lengthIn) + '" x ' + fmtDec(p.widthIn) + '" + ' + fmtDec(p.extensionIn) + '" ext',
      mat: p.gauge + ' Plate G90',
      wt: Math.round(p.wtTotal * 10) / 10
    }
  ]);

  // ═══════════════════════════════════════════════════════════
  // FOOTER STATS
  // ═══════════════════════════════════════════════════════════

  document.getElementById('fDims').textContent = fmtDec(p.lengthIn) + '" x ' + fmtDec(p.widthIn) + '"';
  document.getElementById('fGauge').textContent = p.gauge + ' (' + fmtDec(p.thick, 3) + '")';
  document.getElementById('fQty').textContent = String(p.qty);
  document.getElementById('fWtEach').textContent = fmtDec(p.wtEach, 1) + ' lbs';
  document.getElementById('fWtTotal').textContent = fmtDec(p.wtTotal, 1) + ' lbs';

  // ── Tooltip wiring ──
  wireTooltips(p);
}

// ── Tooltip setup ──
function wireTooltips(p) {
  var tip = document.getElementById('tip');
  var parts = document.querySelectorAll('.hover-part');
  parts.forEach(function(el) {
    el.addEventListener('mouseenter', function(e) {
      var dp = el.dataset.part || '';
      var html = '';
      if (dp === 'p2plate' || dp === 'p2side') {
        html = '<b>P2 Eave Plate</b><br>' +
          '<div class="r"><span class="k">Mark:</span><span class="v">' + p.mark + '</span></div>' +
          '<div class="r"><span class="k">Size:</span><span class="v">' + fmtDec(p.lengthIn) + '" x ' + fmtDec(p.widthIn) + '"</span></div>' +
          '<div class="r"><span class="k">Extension:</span><span class="v">' + fmtDec(p.extensionIn) + '"</span></div>' +
          '<div class="r"><span class="k">Gauge:</span><span class="v">' + p.gauge + ' (' + fmtDec(p.thick, 3) + '")</span></div>' +
          '<div class="r"><span class="k">Holes:</span><span class="v">8 (4x2) - 1/4" TEK</span></div>' +
          '<div class="r"><span class="k">Weight:</span><span class="v">' + fmtDec(p.wtEach, 1) + ' lbs ea</span></div>' +
          '<div class="r"><span class="k">Coil:</span><span class="v">9" 10GA, 4.24 lbs/lft</span></div>';
      } else if (dp === 'p2installed') {
        html = '<b>Installed Assembly</b><br>' +
          '<div class="r"><span class="k">Location:</span><span class="v">Eave / Exterior Purlin</span></div>' +
          '<div class="r"><span class="k">Per Rafter:</span><span class="v">2 (each eave end)</span></div>' +
          '<div class="r"><span class="k">Attachment:</span><span class="v">1/4" TEK Screws (8 per plate)</span></div>' +
          '<div class="r"><span class="k">Bend:</span><span class="v">90\u00B0, ' + fmtDec(p.extensionIn) + '" wrap</span></div>';
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
}
"""

# ==============================================================================
# Controls HTML -- P2 plate-specific inputs
# ==============================================================================

P2PLATE_CONTROLS = """
    <div class="ctrl-group">
      <label>Width (in)</label>
      <input type="number" id="inpWidth" value="9" min="4" max="16" step="0.5" onchange="draw()">
    </div>
    <div class="ctrl-group">
      <label>Length (in)</label>
      <input type="number" id="inpLength" value="24" min="12" max="48" step="1" onchange="draw()">
    </div>
    <div class="ctrl-group">
      <label>Extension (in)</label>
      <input type="number" id="inpExtension" value="9.5" min="4" max="16" step="0.5" onchange="draw()">
    </div>
    <div class="ctrl-group">
      <label>Gauge</label>
      <select id="selGauge" onchange="draw()">
        <option value="10GA" selected>10GA</option>
        <option value="12GA">12GA</option>
        <option value="14GA">14GA</option>
      </select>
    </div>
    <div class="ctrl-group">
      <label>Qty</label>
      <input type="number" id="inpQty" value="2" min="1" max="200" step="1" onchange="draw()">
    </div>
    <button class="toggle-btn" onclick="window.print()">Print</button>
"""

# ==============================================================================
# Footer HTML -- P2 plate-specific stats
# ==============================================================================

P2PLATE_FOOTER = """
  <div>Dimensions: <span class="s" id="fDims">--</span></div>
  <div>Gauge: <span class="s" id="fGauge">--</span></div>
  <div>Qty: <span class="s" id="fQty">--</span></div>
  <div>Weight Each: <span class="s" id="fWtEach">--</span></div>
  <div>Total Weight: <span class="s" id="fWtTotal">--</span></div>
"""

# ==============================================================================
# Assemble final HTML via drawing_base
# ==============================================================================

P2PLATE_DRAWING_HTML = drawing_base.build_html_shell(
    title="P2 Eave Plate Shop Drawing",
    drawing_type="p2plate",
    config_var="P2PLATE_CONFIG",
    controls_html=P2PLATE_CONTROLS,
    footer_html=P2PLATE_FOOTER,
    drawing_js=P2PLATE_JS,
)
