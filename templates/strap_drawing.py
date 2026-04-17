"""
TitanForge -- Interactive Hurricane Strap Shop Drawing Template
===============================================================
Full-featured SVG-based hurricane strap shop drawing served as an
interactive page.  Pre-fills with project data via window.STRAP_CONFIG
injection.  Uses drawing_base.build_html_shell() for consistent
dark-theme UI.

Hurricane Strap specs:
  - 1.5" wide flat strap, 10GA (0.135" thick)
  - 0.706 lbs/LFT (from 3000 lb rolls)
  - Standard length 28" with bolt holes at each end
  - Connects purlins to rafters for wind uplift resistance
  - TEK screw attachment at both purlin and rafter flanges
"""

import templates.drawing_base as drawing_base

# ═══════════════════════════════════════════════════════════════════════════════
# Component-specific JavaScript: draw() and helpers
# ═══════════════════════════════════════════════════════════════════════════════

STRAP_JS = r"""
// ── Hurricane strap constants ──
var GAUGE_DATA = {
  '10GA': { thick: 0.135, lbsLft: 0.706 },
  '12GA': { thick: 0.105, lbsLft: 0.551 },
  '14GA': { thick: 0.075, lbsLft: 0.394 }
};

var STRAP_WIDTH = 1.5;           // inches
var HOLE_DIA    = 0.375;         // 3/8" bolt holes
var EDGE_DIST   = 1.0;           // hole edge distance
var HOLE_SPACING = 2.0;          // between holes at each end

// ── Apply server config to controls ──
function applyComponentConfig(cfg) {
  if (cfg.length_in) {
    var el = document.getElementById('inpLength');
    if (el) el.value = cfg.length_in;
  }
  if (cfg.gauge) {
    var el = document.getElementById('selGauge');
    if (el) el.value = cfg.gauge;
  }
  if (cfg.qty) {
    var el = document.getElementById('inpQty');
    if (el) el.value = cfg.qty;
  }
  if (cfg.mark) {
    var el = document.getElementById('inpMark');
    if (el) el.value = cfg.mark;
  }
}

// ── Read current control values ──
function getParams() {
  var lengthIn = parseFloat(document.getElementById('inpLength').value) || 28;
  var gauge    = document.getElementById('selGauge').value || '10GA';
  var qty      = parseInt(document.getElementById('inpQty').value) || 1;
  var mark     = document.getElementById('inpMark').value || 'HS-1';

  var gd      = GAUGE_DATA[gauge] || GAUGE_DATA['10GA'];
  var thick   = gd.thick;
  var lbsLft  = gd.lbsLft;
  var wtPiece = lbsLft * (lengthIn / 12);
  var wtTotal = wtPiece * qty;

  return {
    lengthIn: lengthIn, gauge: gauge, thick: thick, qty: qty,
    mark: mark, lbsLft: lbsLft, wtPiece: wtPiece, wtTotal: wtTotal,
    width: STRAP_WIDTH, holeDia: HOLE_DIA,
    edgeDist: EDGE_DIST, holeSpacing: HOLE_SPACING
  };
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
  var surfPrep   = document.getElementById('setSurfPrep').value || 'GALVANIZED';

  // ════════════════════════════════════════════════════════════════════
  // ZONE 1: ELEVATION VIEW (y=25 to y=280)
  // Top-down view of flat strap showing full length, width, holes
  // ════════════════════════════════════════════════════════════════════
  svg.appendChild($t(330, 22, 'ELEVATION VIEW', 'ttl'));

  var evL = 80, evR = 640;
  var evY = 100;
  var drawLen = evR - evL;
  var sc = drawLen / p.lengthIn;        // px per inch
  var strapH = Math.max(p.width * sc, 18);  // visual strap width (height in view)
  if (strapH > 50) strapH = 50;
  var strapTop = evY;
  var strapBot = evY + strapH;
  var strapMidY = evY + strapH / 2;

  // ── Purlin flange (left end) ──
  var purG = $g('hover-part', 'purlin-flange');
  var flangeW = 35;
  purG.appendChild($r(evL - flangeW - 4, evY - 20, flangeW, strapH + 40, 'gus'));
  purG.appendChild($t(evL - flangeW/2 - 4, evY + strapH + 32, 'PURLIN', 'note', 'middle'));
  purG.appendChild($t(evL - flangeW/2 - 4, evY + strapH + 42, 'FLANGE', 'note', 'middle'));
  svg.appendChild(purG);

  // ── Rafter flange (right end) ──
  var rafG = $g('hover-part', 'rafter-flange');
  rafG.appendChild($r(evR + 4, evY - 20, flangeW, strapH + 40, 'gus'));
  rafG.appendChild($t(evR + flangeW/2 + 4, evY + strapH + 32, 'RAFTER', 'note', 'middle'));
  rafG.appendChild($t(evR + flangeW/2 + 4, evY + strapH + 42, 'FLANGE', 'note', 'middle'));
  svg.appendChild(rafG);

  // ── Strap body ──
  var strapG = $g('hover-part', 'strap');
  strapG.appendChild($r(evL, strapTop, drawLen, strapH, 'conn-plate'));

  // Centerline along length
  strapG.appendChild($l(evL - 15, strapMidY, evR + 15, strapMidY, 'center'));

  // Centerline along width (midpoint)
  var midX = (evL + evR) / 2;
  strapG.appendChild($l(midX, strapTop - 12, midX, strapBot + 12, 'center'));

  // ── Hole pattern — left end ──
  var hEdgePx  = p.edgeDist * sc;
  var hSpacePx = p.holeSpacing * sc;
  var holePx   = Math.max(p.holeDia * sc / 2, 2.5);

  // Left hole 1 (near edge)
  var lh1x = evL + hEdgePx;
  strapG.appendChild($c(lh1x, strapMidY, holePx, 'bolt'));
  // Left hole 2
  var lh2x = evL + hEdgePx + hSpacePx;
  strapG.appendChild($c(lh2x, strapMidY, holePx, 'bolt'));

  // ── Hole pattern — right end ──
  var rh1x = evR - hEdgePx;
  strapG.appendChild($c(rh1x, strapMidY, holePx, 'bolt'));
  var rh2x = evR - hEdgePx - hSpacePx;
  strapG.appendChild($c(rh2x, strapMidY, holePx, 'bolt'));

  svg.appendChild(strapG);

  // ── Section cut indicator A-A (through strap width) ──
  var secX = midX;
  svg.appendChild($l(secX - 8, strapTop - 25, secX - 8, strapBot + 25, 'cut-line'));
  svg.appendChild($l(secX + 8, strapTop - 25, secX + 8, strapBot + 25, 'cut-line'));
  svg.appendChild($t(secX - 8, strapTop - 28, 'A', 'lblb', 'middle'));
  svg.appendChild($t(secX + 8, strapTop - 28, 'A', 'lblb', 'middle'));

  // ── Elevation dimensions ──
  // Total length
  dimH(svg, evL, evR, strapBot + 8, 22, fmtDec(p.lengthIn, 2) + '"');

  // Left edge distance
  dimH(svg, evL, lh1x, strapTop - 6, -16, fmtDec(p.edgeDist, 2) + '"');

  // Left hole spacing
  dimH(svg, lh1x, lh2x, strapTop - 6, -30, fmtDec(p.holeSpacing, 2) + '"');

  // Right edge distance
  dimH(svg, rh1x, evR, strapTop - 6, -16, fmtDec(p.edgeDist, 2) + '"');

  // Right hole spacing
  dimH(svg, rh2x, rh1x, strapTop - 6, -30, fmtDec(p.holeSpacing, 2) + '"');

  // Width dimension (left side)
  dimV(svg, evL - 8, strapTop, strapBot, -20, fmtDec(p.width, 2) + '"');

  // Hole diameter callout
  svg.appendChild($t(lh1x + 8, strapMidY - holePx - 6, fmtDec(p.holeDia, 3) + '" DIA', 'noteb'));
  svg.appendChild($t(lh1x + 8, strapMidY - holePx - 14, 'HOLES (TYP 4)', 'note'));

  // Scale note
  var elevScale = fmtScale(sc);
  svg.appendChild($t(330, strapBot + 55, 'SCALE: ' + elevScale, 'note', 'middle'));

  // ── Strap schedule (right side of Zone 1) ──
  var infoX = 700;
  svg.appendChild($t(infoX + 100, 35, 'STRAP SCHEDULE', 'lblb', 'middle'));
  svg.appendChild($l(infoX + 10, 40, infoX + 190, 40, 'obj hair'));

  var infoLines = [
    ['MARK:',       p.mark],
    ['LENGTH:',     fmtDec(p.lengthIn, 2) + '"'],
    ['WIDTH:',      fmtDec(p.width, 2) + '"'],
    ['GAUGE:',      p.gauge + ' (' + fmtDec(p.thick, 3) + '")'],
    ['MATERIAL:',   '10GA FLAT STRAP'],
    ['ROLL STOCK:', '3,000 LB ROLLS'],
    ['HOLE DIA:',   fmtDec(p.holeDia, 3) + '"'],
    ['EDGE DIST:',  fmtDec(p.edgeDist, 2) + '"'],
    ['HOLE SPC:',   fmtDec(p.holeSpacing, 2) + '"'],
    ['WT/LFT:',     fmtDec(p.lbsLft, 3) + ' lbs/ft'],
    ['WT/PIECE:',   fmtDec(p.wtPiece, 2) + ' lbs'],
    ['QTY:',        p.qty],
    ['TOTAL WT:',   fmtDec(p.wtTotal, 2) + ' lbs']
  ];
  infoLines.forEach(function(pair, i) {
    var iy = 55 + i * 13;
    svg.appendChild($t(infoX + 12, iy, pair[0], 'note'));
    svg.appendChild($t(infoX + 90, iy, String(pair[1]), 'lbl'));
  });

  // ════════════════════════════════════════════════════════════════════
  // ZONE 2: SECTION A-A (y=260 to y=420)
  // Cross-section: 1.5" wide x 10GA thick flat rectangle
  // ════════════════════════════════════════════════════════════════════
  svg.appendChild($t(140, 260, 'SECTION A-A', 'ttl'));

  var cx = 140;
  var cy = 345;
  var zScaleW = 30;   // px per inch for width
  var zScaleT = 120;  // px per inch for thickness (exaggerated for visibility)

  var rectW = p.width * zScaleW;          // visual width
  var rectH = Math.max(p.thick * zScaleT, 6); // visual thickness

  var secG = $g('hover-part', 'strap-section');

  // Flat rectangle cross-section
  secG.appendChild($r(cx - rectW/2, cy - rectH/2, rectW, rectH, 'conn-plate'));

  // Centerlines
  secG.appendChild($l(cx, cy - rectH/2 - 20, cx, cy + rectH/2 + 20, 'center'));
  secG.appendChild($l(cx - rectW/2 - 20, cy, cx + rectW/2 + 20, cy, 'center'));

  svg.appendChild(secG);

  // Width dimension
  dimH(svg, cx - rectW/2, cx + rectW/2, cy + rectH/2 + 4, 18, fmtDec(p.width, 2) + '"');

  // Thickness dimension
  dimV(svg, cx + rectW/2 + 4, cy - rectH/2, cy + rectH/2, 22, fmtDec(p.thick, 3) + '"');

  // Gauge callout
  svg.appendChild($t(cx - rectW/2 - 30, cy - 4, p.gauge, 'lblb', 'middle'));
  svg.appendChild($t(cx - rectW/2 - 30, cy + 8, '(' + fmtDec(p.thick, 3) + '")', 'note', 'middle'));

  // Material callout
  svg.appendChild($t(cx + rectW/2 + 35, cy - 12, 'MATERIAL:', 'noteb'));
  svg.appendChild($t(cx + rectW/2 + 35, cy - 2, 'FLAT STRAP', 'note'));
  svg.appendChild($t(cx + rectW/2 + 35, cy + 8, p.width + '" x ' + p.gauge, 'note'));
  svg.appendChild($t(cx + rectW/2 + 35, cy + 18, fmtDec(p.lbsLft, 3) + ' lbs/LFT', 'note'));

  // Scale note
  svg.appendChild($t(140, cy + rectH/2 + 45, 'SCALE: NTS (THICKNESS EXAGGERATED)', 'note', 'middle'));

  // ════════════════════════════════════════════════════════════════════
  // ZONE 3: DETAIL VIEWS (right side, y=240 to y=650)
  // ════════════════════════════════════════════════════════════════════

  // ── DETAIL 1: Strap-to-Purlin Connection ──
  svg.appendChild($t(480, 260, 'DETAIL 1: STRAP-TO-PURLIN', 'ttl'));

  var d1x = 460, d1y = 330;
  var d1G = $g('hover-part', 'detail-purlin');

  // Purlin flange (cross-section, horizontal beam)
  var pflgW = 80, pflgH = 8;
  d1G.appendChild($r(d1x - pflgW/2, d1y, pflgW, pflgH, 'cee'));
  d1G.appendChild($t(d1x, d1y + pflgH + 12, 'PURLIN FLANGE', 'note', 'middle'));

  // Strap on top of flange
  var stW = 50, stH = 5;
  d1G.appendChild($r(d1x - stW/2, d1y - stH, stW, stH, 'conn-plate'));
  d1G.appendChild($t(d1x + stW/2 + 6, d1y - stH/2 + 2, 'STRAP', 'noteb'));

  // TEK screws through strap into purlin flange
  d1G.appendChild($c(d1x - 12, d1y - 1, 2, 'bolt'));
  d1G.appendChild($c(d1x + 12, d1y - 1, 2, 'bolt'));

  // TEK screw leader lines
  d1G.appendChild($l(d1x - 12, d1y - 1, d1x - 40, d1y - 25, 'dim'));
  d1G.appendChild($t(d1x - 70, d1y - 30, '(2) #12 TEK', 'noteb'));
  d1G.appendChild($t(d1x - 70, d1y - 21, 'SCREWS', 'note'));

  // Strap extending upward (continues to rafter)
  d1G.appendChild($l(d1x - stW/2, d1y - stH, d1x - stW/2, d1y - 45, 'obj med'));
  d1G.appendChild($l(d1x + stW/2, d1y - stH, d1x + stW/2, d1y - 45, 'obj med'));
  d1G.appendChild($t(d1x, d1y - 38, 'TO RAFTER', 'note', 'middle'));

  // Dimension: screw spacing
  dimH(svg, d1x - 12, d1x + 12, d1y + pflgH + 4, 14, '1"');

  svg.appendChild(d1G);
  svg.appendChild($t(480, d1y + pflgH + 38, 'NTS', 'note', 'middle'));

  // ── DETAIL 2: Strap-to-Rafter Connection ──
  svg.appendChild($t(730, 260, 'DETAIL 2: STRAP-TO-RAFTER', 'ttl'));

  var d2x = 720, d2y = 330;
  var d2G = $g('hover-part', 'detail-rafter');

  // Rafter flange (cross-section, horizontal beam)
  var rflgW = 80, rflgH = 10;
  d2G.appendChild($r(d2x - rflgW/2, d2y, rflgW, rflgH, 'gus'));
  d2G.appendChild($t(d2x, d2y + rflgH + 12, 'RAFTER FLANGE', 'note', 'middle'));

  // Strap wrapping around / over rafter flange
  var st2W = 50, st2H = 5;
  d2G.appendChild($r(d2x - st2W/2, d2y - st2H, st2W, st2H, 'conn-plate'));
  d2G.appendChild($t(d2x + st2W/2 + 6, d2y - st2H/2 + 2, 'STRAP', 'noteb'));

  // TEK screws through strap into rafter flange
  d2G.appendChild($c(d2x - 12, d2y - 1, 2, 'bolt'));
  d2G.appendChild($c(d2x + 12, d2y - 1, 2, 'bolt'));

  // TEK screw leader lines
  d2G.appendChild($l(d2x + 12, d2y - 1, d2x + 40, d2y - 25, 'dim'));
  d2G.appendChild($t(d2x + 44, d2y - 30, '(2) #12 TEK', 'noteb'));
  d2G.appendChild($t(d2x + 44, d2y - 21, 'SCREWS', 'note'));

  // Strap extending downward (continues to purlin)
  d2G.appendChild($l(d2x - st2W/2, d2y - st2H, d2x - st2W/2, d2y - 45, 'obj med'));
  d2G.appendChild($l(d2x + st2W/2, d2y - st2H, d2x + st2W/2, d2y - 45, 'obj med'));
  d2G.appendChild($t(d2x, d2y - 38, 'TO PURLIN', 'note', 'middle'));

  // Weld symbol note
  d2G.appendChild($t(d2x - rflgW/2 - 5, d2y + 5, 'NO WELD', 'weld-txt', 'end'));
  d2G.appendChild($t(d2x - rflgW/2 - 5, d2y + 13, '(MECH. FASTENED)', 'weld-txt', 'end'));

  // Dimension: screw spacing
  dimH(svg, d2x - 12, d2x + 12, d2y + rflgH + 4, 14, '1"');

  svg.appendChild(d2G);
  svg.appendChild($t(730, d2y + rflgH + 38, 'NTS', 'note', 'middle'));

  // ── DETAIL 3: Hole Pattern Detail ──
  svg.appendChild($t(940, 260, 'DETAIL 3: HOLE PATTERN', 'ttl'));

  var d3x = 940, d3y = 310;
  var d3Scale = 14; // px per inch for hole detail
  var d3G = $g('hover-part', 'detail-holes');

  // End of strap (enlarged)
  var d3W = (p.edgeDist + p.holeSpacing + p.edgeDist) * d3Scale;
  var d3H = p.width * d3Scale;
  d3G.appendChild($r(d3x - d3W/2, d3y, d3W, d3H, 'conn-plate'));

  // Centerline
  d3G.appendChild($l(d3x - d3W/2 - 8, d3y + d3H/2, d3x + d3W/2 + 8, d3y + d3H/2, 'center'));

  // Hole 1 (near edge)
  var h1x = d3x - d3W/2 + p.edgeDist * d3Scale;
  var hRad = Math.max(p.holeDia * d3Scale / 2, 3);
  d3G.appendChild($c(h1x, d3y + d3H/2, hRad, 'bolt'));

  // Hole 2
  var h2x = h1x + p.holeSpacing * d3Scale;
  d3G.appendChild($c(h2x, d3y + d3H/2, hRad, 'bolt'));

  svg.appendChild(d3G);

  // Dimensions for hole pattern
  // Edge distance
  dimH(svg, d3x - d3W/2, h1x, d3y - 4, -14, fmtDec(p.edgeDist, 2) + '"');

  // Hole spacing
  dimH(svg, h1x, h2x, d3y - 4, -28, fmtDec(p.holeSpacing, 2) + '"');

  // Trailing edge
  dimH(svg, h2x, d3x + d3W/2, d3y - 4, -14, fmtDec(p.edgeDist, 2) + '"');

  // Width dimension
  dimV(svg, d3x + d3W/2 + 4, d3y, d3y + d3H, 16, fmtDec(p.width, 2) + '"');

  // Hole diameter callout
  svg.appendChild($t(h1x + hRad + 4, d3y + d3H/2 - hRad - 4, fmtDec(p.holeDia, 3) + '" DIA', 'noteb'));
  svg.appendChild($t(h1x + hRad + 4, d3y + d3H/2 - hRad - 12, '(TYP 2 EA END)', 'note'));

  svg.appendChild($t(940, d3y + d3H + 22, 'SCALE: 1" = ' + fmtDec(1/d3Scale, 2) + '"', 'note', 'middle'));

  // ════════════════════════════════════════════════════════════════════
  // ZONE 4: BOM TABLE (y=450 to y=650)
  // ════════════════════════════════════════════════════════════════════
  svg.appendChild($t(300, 455, 'BILL OF MATERIALS', 'ttl'));

  var bomX = 40, bomY = 468, bomW = 620;
  var cols = [0, 80, 120, 240, 360, 440, 530];
  var hdrs = ['MARK', 'QTY', 'DESCRIPTION', 'LENGTH', 'MATERIAL', 'GAUGE', 'WEIGHT (LBS)'];

  // Header row
  svg.appendChild($e('rect', {x: bomX, y: bomY, width: bomW, height: 14, fill: '#333', stroke: '#333'}));
  hdrs.forEach(function(h, i) {
    var ht = $t(bomX + cols[i] + 4, bomY + 11, h, 'note');
    ht.setAttribute('fill', '#FFF');
    svg.appendChild(ht);
  });

  // BOM rows
  var bomRows = [];

  // Row 1: Hurricane Strap
  bomRows.push({
    mk: p.mark, qty: p.qty,
    desc: 'HURRICANE STRAP ' + fmtDec(p.width, 1) + '"W',
    length: fmtDec(p.lengthIn, 2) + '"',
    mat: 'FLAT STRAP', gauge: p.gauge,
    wt: fmtDec(p.wtTotal, 2)
  });

  // Row 2: TEK Screws (4 per strap: 2 at purlin, 2 at rafter)
  var tekQty = p.qty * 4;
  bomRows.push({
    mk: 'TEK', qty: tekQty,
    desc: '#12 TEK SCREW',
    length: '3/4"',
    mat: 'ZN PLATED', gauge: '--',
    wt: '--'
  });

  bomRows.forEach(function(row, i) {
    var ry = bomY + 14 + i * 14;
    svg.appendChild($l(bomX, ry + 14, bomX + bomW, ry + 14, 'dim'));
    var vals = [row.mk, String(row.qty), row.desc, row.length, row.mat, row.gauge, row.wt];
    vals.forEach(function(v, ci) {
      svg.appendChild($t(bomX + cols[ci] + 4, ry + 11, v, 'lbl'));
    });
  });

  // Total row
  var totY = bomY + 14 + bomRows.length * 14;
  svg.appendChild($l(bomX, totY, bomX + bomW, totY, 'obj med'));
  svg.appendChild($t(bomX + cols[5] + 4, totY + 12, 'TOTAL:', 'lblb'));
  svg.appendChild($t(bomX + cols[6] + 4, totY + 12, fmtDec(p.wtTotal, 2) + ' LBS', 'lblb'));

  // Outer box for BOM table
  var bomH = 14 + (bomRows.length + 1) * 14 + 4;
  svg.appendChild($r(bomX, bomY, bomW, bomH, 'obj med'));

  // ── Notes area (right of BOM) ──
  var noteX = 700, noteY = 465;
  svg.appendChild($t(noteX + 100, 455, 'NOTES', 'ttl'));
  var notes = [
    '1. HURRICANE STRAPS CUT FROM 3,000 LB ROLLS',
    '2. MATERIAL: ' + p.gauge + ' FLAT STRAP (' + fmtDec(p.thick, 3) + '" THK)',
    '3. WIDTH: ' + fmtDec(p.width, 2) + '"',
    '4. STRAPS CONNECT PURLINS TO RAFTERS',
    '5. PURPOSE: WIND UPLIFT RESISTANCE',
    '6. ATTACH WITH (2) #12 TEK SCREWS EA END',
    '7. HOLE DIA: ' + fmtDec(p.holeDia, 3) + '"',
    '8. EDGE DISTANCE: ' + fmtDec(p.edgeDist, 2) + '" MIN',
    '9. HOLE SPACING: ' + fmtDec(p.holeSpacing, 2) + '"',
    '10. WT/LFT: ' + fmtDec(p.lbsLft, 3) + ' LBS/FT',
    '11. DO NOT SCALE DRAWING',
    '12. TOL: LENGTH +/-1/16"',
    '13. INSTALL PER ENGINEER\'S UPLIFT SCHEDULE'
  ];
  notes.forEach(function(n, i) {
    svg.appendChild($t(noteX, noteY + 4 + i * 10, n, 'note'));
  });

  // ════════════════════════════════════════════════════════════════════
  // ZONE 5: TITLE BLOCK (y=680 to y=815)
  // ════════════════════════════════════════════════════════════════════
  drawTitleBlock(svg, {
    projName: projName,
    customer: customer,
    jobNum: jobNum,
    drawingNum: drawingNum,
    drawnBy: drawnBy,
    surfPrep: surfPrep,
    drawingTitle: 'STRAP',
    partMark: p.mark,
    revision: 0,
    revHistory: [],
    projectNotes: [
      'MATERIAL: ' + p.gauge + ' FLAT STRAP',
      'WIDTH: ' + fmtDec(p.width, 2) + '"',
      'THICKNESS: ' + fmtDec(p.thick, 3) + '"',
      'WEIGHT: ' + fmtDec(p.lbsLft, 3) + ' LBS/LFT',
      'ROLL STOCK: 3,000 LB ROLLS',
      'HOLE DIA: ' + fmtDec(p.holeDia, 3) + '"',
      'PURPOSE: WIND UPLIFT RESISTANCE',
      'ATTACH: (2) #12 TEK SCREWS EA END',
      'SURF PREP: GALVANIZED',
      'FAB: AISC 360-22 / AWS D1.1',
      'DO NOT SCALE DRAWING',
      'PIECE MARK = ERECTION MARK',
      'TOL: LENGTH +/-1/16" / HOLES +/-1/32"'
    ]
  });

  // ── Update footer stats ──
  var fLen   = document.getElementById('fLength');
  var fWidth = document.getElementById('fWidth');
  var fGauge = document.getElementById('fGauge');
  var fQty   = document.getElementById('fQty');
  var fWt    = document.getElementById('fTotalWt');
  if (fLen)   fLen.textContent   = fmtDec(p.lengthIn, 2) + '"';
  if (fWidth) fWidth.textContent = fmtDec(p.width, 2) + '"';
  if (fGauge) fGauge.textContent = p.gauge;
  if (fQty)   fQty.textContent   = p.qty;
  if (fWt)    fWt.textContent    = fmtDec(p.wtTotal, 2) + ' lbs';

  // ── Update BOM side panel ──
  updateBOM([
    { mk: p.mark, qty: p.qty, desc: 'Hurricane Strap ' + fmtDec(p.width, 1) + '"W x ' + fmtDec(p.lengthIn, 0) + '"L', size: p.gauge, mat: 'FLAT STRAP', wt: Math.round(p.wtTotal * 100) / 100 },
    { mk: 'TEK', qty: tekQty, desc: '#12 TEK Screw', size: '3/4"', mat: 'ZN', wt: 0 }
  ]);
}
"""

# ═══════════════════════════════════════════════════════════════════════════════
# Controls HTML — strap-specific inputs
# ═══════════════════════════════════════════════════════════════════════════════

STRAP_CONTROLS = """
    <div class="ctrl-group">
      <label>Length (in)</label>
      <input type="number" id="inpLength" value="28" min="6" max="96" step="0.5" onchange="draw()">
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
      <input type="number" id="inpQty" value="1" min="1" max="500" step="1" onchange="draw()">
    </div>
    <div class="ctrl-group">
      <label>Mark</label>
      <input type="text" id="inpMark" value="HS-1" style="width:60px;" onchange="draw()">
    </div>
    <button class="toggle-btn" onclick="window.print()">Print</button>
"""

# ═══════════════════════════════════════════════════════════════════════════════
# Footer HTML — strap-specific stats
# ═══════════════════════════════════════════════════════════════════════════════

STRAP_FOOTER = """
  <div>Length: <span class="s" id="fLength">--</span></div>
  <div>Width: <span class="s" id="fWidth">--</span></div>
  <div>Gauge: <span class="s" id="fGauge">--</span></div>
  <div>Qty: <span class="s" id="fQty">--</span></div>
  <div>Total Wt: <span class="s" id="fTotalWt">--</span></div>
"""

# ═══════════════════════════════════════════════════════════════════════════════
# Assemble final HTML via drawing_base
# ═══════════════════════════════════════════════════════════════════════════════

STRAP_DRAWING_HTML = drawing_base.build_html_shell(
    title="Hurricane Strap Shop Drawing",
    drawing_type="strap",
    config_var="STRAP_CONFIG",
    controls_html=STRAP_CONTROLS,
    footer_html=STRAP_FOOTER,
    drawing_js=STRAP_JS,
)
