"""
TitanForge -- Interactive Endcap U-Channel Shop Drawing Template
================================================================
Full-featured SVG-based endcap U-channel shop drawing served as an
interactive page.  Pre-fills with project data via window.ENDCAP_CONFIG
injection.  Uses drawing_base.build_html_shell() for consistent
dark-theme UI.

Endcap U-Channel specs:
  - Roll-formed from 12GA Z-purlin coil (20.125" wide)
  - U-shaped channel: flat web with two inward-bent flanges (returns)
  - Default web width: 4", flange depth: 1.5", 12GA G90 galvanised
  - Forms front/back end closures of carport
  - Runs vertically between ground and rafter at each building end
  - Roof panels and optional wall panels terminate into the U-channel
  - TEK screw attachment to end rafter at top, embedment at bottom
"""

import templates.drawing_base as drawing_base

# ═══════════════════════════════════════════════════════════════════════════════
# Component-specific JavaScript: draw() and helpers
# ═══════════════════════════════════════════════════════════════════════════════

ENDCAP_JS = r"""
// ── Endcap U-channel constants ──
var GAUGE_THICK = {
  '12GA': 0.105,
  '14GA': 0.075
};

var GAUGE_LBS_LFT = {
  '12GA': 3.54,
  '14GA': 2.53
};

var DEFAULT_WEB_WIDTH = 4.0;    // inches
var DEFAULT_FLANGE_DEPTH = 1.5; // inches
var COIL_WIDTH = 20.125;        // inches (shared with Z-purlin line)
var EMBEDMENT = 3.0;            // inches below grade

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
  if (cfg.web_width) {
    var el = document.getElementById('inpWebWidth');
    if (el) el.value = cfg.web_width;
  }
  if (cfg.flange_depth) {
    var el = document.getElementById('inpFlangeDepth');
    if (el) el.value = cfg.flange_depth;
  }
  if (cfg.qty) {
    var el = document.getElementById('inpQty');
    if (el) el.value = cfg.qty;
  }
}

// ── Read current control values ──
function getParams() {
  var lengthIn = parseFloat(document.getElementById('inpLength').value) || 120;
  var gauge = document.getElementById('selGauge').value || '12GA';
  var webWidth = parseFloat(document.getElementById('inpWebWidth').value) || DEFAULT_WEB_WIDTH;
  var flangeDepth = parseFloat(document.getElementById('inpFlangeDepth').value) || DEFAULT_FLANGE_DEPTH;
  var qty = parseInt(document.getElementById('inpQty').value) || 4;
  var thick = GAUGE_THICK[gauge] || 0.105;
  var lbsLft = GAUGE_LBS_LFT[gauge] || 3.54;
  var wtPiece = lbsLft * (lengthIn / 12);
  var mark = (window.ENDCAP_CONFIG && window.ENDCAP_CONFIG.mark) || ('EC-' + gauge.replace('GA',''));

  return {
    lengthIn: lengthIn, gauge: gauge, thick: thick,
    webWidth: webWidth, flangeDepth: flangeDepth,
    qty: qty, lbsLft: lbsLft, wtPiece: wtPiece, mark: mark,
    material: 'G90', coilWidth: COIL_WIDTH, embedment: EMBEDMENT
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
  var projName = document.getElementById('setProjectName').value || 'PROJECT';
  var customer = document.getElementById('setCustomer').value || '';
  var jobNum = document.getElementById('setJobNumber').value || '';
  var drawingNum = document.getElementById('setDrawingNum').value || 'SD-001';
  var drawnBy = document.getElementById('setDrawnBy').value || 'AUTO';
  var surfPrep = document.getElementById('setSurfPrep').value || 'G90';

  // ════════════════════════════════════════════════════════════════════
  // ZONE 1: ELEVATION VIEW (x=30..420, y=25..440)
  // Front view of U-channel running full building height
  // ════════════════════════════════════════════════════════════════════
  svg.appendChild($t(225, 22, 'ELEVATION VIEW', 'ttl'));

  var evL = 120, evR = 320;       // horizontal extent
  var evTop = 55, evBot = 420;    // vertical extent
  var evH = evBot - evTop;        // available drawing height
  var totalLen = p.lengthIn + p.embedment;
  var sc = evH / totalLen;        // px per inch

  var channelW = p.webWidth * sc;
  if (channelW < 24) channelW = 24;
  var chX = (evL + evR) / 2 - channelW / 2;
  var chH = p.lengthIn * sc;
  var embH = p.embedment * sc;

  // Grade line
  var gradeY = evTop + chH;
  svg.appendChild($l(evL - 30, gradeY, evR + 30, gradeY, 'obj med'));
  svg.appendChild($t(evR + 35, gradeY + 4, 'GRADE', 'noteb'));
  // Hatch below grade
  for (var hx = evL - 20; hx < evR + 20; hx += 8) {
    svg.appendChild($l(hx, gradeY, hx - 6, gradeY + 8, 'dim'));
  }

  // End rafter at top
  var rafH = 20;
  var rafG = $g('hover-part', 'end-rafter');
  rafG.appendChild($r(evL - 10, evTop - rafH, evR - evL + 20, rafH, 'gus'));
  rafG.appendChild($t((evL + evR) / 2, evTop - rafH + 13, 'END RAFTER', 'noteb', 'middle'));
  svg.appendChild(rafG);

  // U-channel body (front view = rectangle)
  var ucG = $g('hover-part', 'endcap-channel');
  ucG.appendChild($r(chX, evTop, channelW, chH + embH, 'cee'));

  // Show U-shape returns as inner lines (flanges visible from front)
  var flangeVis = p.flangeDepth * sc;
  if (flangeVis < 4) flangeVis = 4;
  // Left return line
  ucG.appendChild($l(chX + 3, evTop + 2, chX + 3, evTop + chH + embH - 2, 'obj thin'));
  // Right return line
  ucG.appendChild($l(chX + channelW - 3, evTop + 2, chX + channelW - 3, evTop + chH + embH - 2, 'obj thin'));

  // Centerline
  ucG.appendChild($l(chX + channelW / 2, evTop - 25, chX + channelW / 2, evTop + chH + embH + 10, 'center'));
  svg.appendChild(ucG);

  // TEK screw at top connection (to rafter)
  var tekTopG = $g('hover-part', 'tek-top');
  var tekY1 = evTop + 6;
  var tekY2 = evTop + 16;
  tekTopG.appendChild($c(chX + channelW * 0.3, tekY1, 2, 'bolt'));
  tekTopG.appendChild($c(chX + channelW * 0.7, tekY1, 2, 'bolt'));
  tekTopG.appendChild($c(chX + channelW * 0.3, tekY2, 2, 'bolt'));
  tekTopG.appendChild($c(chX + channelW * 0.7, tekY2, 2, 'bolt'));
  svg.appendChild(tekTopG);

  // Section cut A-A indicator
  var secY = evTop + chH * 0.45;
  svg.appendChild($l(chX - 20, secY, chX + channelW + 20, secY, 'cut-line'));
  svg.appendChild($t(chX - 28, secY + 4, 'A', 'lblb', 'middle'));
  svg.appendChild($t(chX + channelW + 28, secY + 4, 'A', 'lblb', 'middle'));

  // ── Elevation dimensions ──
  // Total length (above grade)
  dimV(svg, chX - 8, evTop, evTop + chH, -30, fmtFtIn(p.lengthIn));

  // Embedment below grade
  dimV(svg, chX - 8, evTop + chH, evTop + chH + embH, -30, fmtDec(p.embedment) + '"');

  // Width dimension
  dimH(svg, chX, chX + channelW, evTop + chH + embH + 5, 18, fmtDec(p.webWidth) + '"');

  // Scale note
  var elevScale = fmtScale(sc);
  svg.appendChild($t(225, evBot + 42, 'SCALE: ' + elevScale, 'note', 'middle'));

  // ════════════════════════════════════════════════════════════════════
  // ZONE 2: SECTION A-A (x=460..720, y=25..280)
  // Full U-channel cross-section
  // ════════════════════════════════════════════════════════════════════
  svg.appendChild($t(590, 22, 'SECTION A-A', 'ttl'));

  var csX = 510, csY = 60;       // section origin
  var csSc = 18;                  // px per inch for cross-section
  var csWebW = p.webWidth * csSc;
  var csFlangeD = p.flangeDepth * csSc;
  var csThick = p.thick * csSc;
  if (csThick < 2) csThick = 2;

  // Draw U-channel cross-section (looking down the length)
  // Outer profile: U-shape opening upward (as if panel slides in from top)
  var csG = $g('hover-part', 'section-u');

  // Left flange (return) - outer
  csG.appendChild($r(csX, csY, csThick, csFlangeD, 'cee'));
  // Web - outer
  csG.appendChild($r(csX, csY + csFlangeD - csThick, csWebW, csThick, 'cee'));
  // Right flange (return) - outer
  csG.appendChild($r(csX + csWebW - csThick, csY, csThick, csFlangeD, 'cee'));

  // Material fill for visibility
  csG.appendChild($e('rect', {x: csX + csThick, y: csY + csFlangeD - csThick,
    width: csWebW - 2 * csThick, height: csThick,
    fill: '#E8E8E8', stroke: 'none'}));
  csG.appendChild($e('rect', {x: csX, y: csY,
    width: csThick, height: csFlangeD,
    fill: '#E8E8E8', stroke: 'none'}));
  csG.appendChild($e('rect', {x: csX + csWebW - csThick, y: csY,
    width: csThick, height: csFlangeD,
    fill: '#E8E8E8', stroke: 'none'}));

  svg.appendChild(csG);

  // TEK screw locations on flanges
  var tekSec = $g('hover-part', 'tek-section');
  tekSec.appendChild($c(csX + csThick / 2, csY + csFlangeD * 0.35, 2.5, 'bolt'));
  tekSec.appendChild($c(csX + csWebW - csThick / 2, csY + csFlangeD * 0.35, 2.5, 'bolt'));
  tekSec.appendChild($t(csX + csThick / 2, csY + csFlangeD * 0.35 - 6, 'TEK', 'note', 'middle'));
  tekSec.appendChild($t(csX + csWebW - csThick / 2, csY + csFlangeD * 0.35 - 6, 'TEK', 'note', 'middle'));
  svg.appendChild(tekSec);

  // ── Section dimensions ──
  // Web width
  dimH(svg, csX, csX + csWebW, csY + csFlangeD + 2, 16, fmtDec(p.webWidth) + '"');

  // Flange depth (left side)
  dimV(svg, csX - 2, csY, csY + csFlangeD, -18, fmtDec(p.flangeDepth) + '"');

  // Gauge callout
  svg.appendChild($t(csX + csWebW / 2, csY + csFlangeD + 40, p.gauge + ' (' + fmtDec(p.thick, 3) + '")', 'dimtxt', 'middle'));
  svg.appendChild($t(csX + csWebW / 2, csY + csFlangeD + 52, 'MATERIAL: G90 GALVANIZED', 'note', 'middle'));
  svg.appendChild($t(csX + csWebW / 2, csY + csFlangeD + 62, 'COIL: ' + fmtDec(p.coilWidth) + '" WIDE', 'note', 'middle'));

  // ════════════════════════════════════════════════════════════════════
  // ZONE 3: DETAILS (x=460..1070, y=290..660)
  // ════════════════════════════════════════════════════════════════════

  // ── DETAIL 1: Top Connection — U-channel to end rafter (x=460..700, y=290..460) ──
  svg.appendChild($t(580, 290, 'DETAIL 1: TOP CONNECTION', 'lblb', 'middle'));

  var d1X = 490, d1Y = 310;
  var d1Sc = 6;  // px per inch for detail

  // End rafter cross section
  var d1RafW = 60, d1RafH = 20;
  var d1G = $g('hover-part', 'detail-top');
  d1G.appendChild($r(d1X, d1Y, d1RafW + 60, d1RafH, 'gus'));
  d1G.appendChild($t(d1X + (d1RafW + 60) / 2, d1Y + 14, 'END RAFTER', 'note', 'middle'));

  // U-channel hanging below rafter
  var d1ChW = p.webWidth * d1Sc;
  var d1FlD = p.flangeDepth * d1Sc;
  var d1ChX = d1X + 30;
  var d1ChY = d1Y + d1RafH;
  var d1ChH = 90;

  // Left flange
  d1G.appendChild($r(d1ChX, d1ChY, 3, d1ChH, 'cee'));
  // Web (bottom of U)
  d1G.appendChild($r(d1ChX, d1ChY + d1ChH - 3, d1ChW, 3, 'cee'));
  // Right flange
  d1G.appendChild($r(d1ChX + d1ChW - 3, d1ChY, 3, d1ChH, 'cee'));

  // TEK screws through channel flanges into rafter
  d1G.appendChild($c(d1ChX + 1.5, d1ChY + 8, 2.5, 'bolt'));
  d1G.appendChild($c(d1ChX + d1ChW - 1.5, d1ChY + 8, 2.5, 'bolt'));
  d1G.appendChild($c(d1ChX + 1.5, d1ChY + 22, 2.5, 'bolt'));
  d1G.appendChild($c(d1ChX + d1ChW - 1.5, d1ChY + 22, 2.5, 'bolt'));

  // TEK screw callout
  d1G.appendChild($l(d1ChX + d1ChW + 5, d1ChY + 8, d1ChX + d1ChW + 40, d1ChY + 8, 'dim'));
  d1G.appendChild($t(d1ChX + d1ChW + 42, d1ChY + 11, '#12 TEK SCREW (TYP)', 'note'));
  svg.appendChild(d1G);

  // Detail 1 dimensions
  dimH(svg, d1ChX, d1ChX + d1ChW, d1ChY + d1ChH, 14, fmtDec(p.webWidth) + '"');

  // ── DETAIL 2: Bottom Connection — ground/embedment (x=460..700, y=470..600) ──
  svg.appendChild($t(580, 470, 'DETAIL 2: BOTTOM / EMBEDMENT', 'lblb', 'middle'));

  var d2X = 490, d2Y = 490;
  var d2G = $g('hover-part', 'detail-bottom');

  // U-channel coming down
  var d2ChW = p.webWidth * d1Sc;
  var d2ChH = 70;
  var d2ChX = d2X + 30;

  // Left flange
  d2G.appendChild($r(d2ChX, d2Y, 3, d2ChH, 'cee'));
  // Web
  d2G.appendChild($r(d2ChX, d2Y + d2ChH - 3, d2ChW, 3, 'cee'));
  // Right flange
  d2G.appendChild($r(d2ChX + d2ChW - 3, d2Y, 3, d2ChH, 'cee'));

  // Grade line
  var d2GradeY = d2Y + d2ChH - p.embedment * d1Sc;
  d2G.appendChild($l(d2X, d2GradeY, d2X + d2ChW + 80, d2GradeY, 'obj med'));
  d2G.appendChild($t(d2X + d2ChW + 85, d2GradeY + 4, 'GRADE', 'noteb'));

  // Hatch below grade
  for (var hx2 = d2X + 5; hx2 < d2X + d2ChW + 70; hx2 += 7) {
    d2G.appendChild($l(hx2, d2GradeY, hx2 - 5, d2GradeY + 7, 'dim'));
  }

  // Embedment dimension
  d2G.appendChild($l(d2ChX + d2ChW + 10, d2GradeY, d2ChX + d2ChW + 10, d2Y + d2ChH, 'dim'));
  d2G.appendChild($l(d2ChX + d2ChW + 8, d2GradeY, d2ChX + d2ChW + 12, d2GradeY, 'dim'));
  d2G.appendChild($l(d2ChX + d2ChW + 8, d2Y + d2ChH, d2ChX + d2ChW + 12, d2Y + d2ChH, 'dim'));
  d2G.appendChild($t(d2ChX + d2ChW + 18, d2GradeY + (d2ChH * 0.5), fmtDec(p.embedment) + '" EMBED', 'dimtxt', 'start'));
  svg.appendChild(d2G);

  // ── DETAIL 3: Panel Termination (x=740..1060, y=290..460) ──
  svg.appendChild($t(900, 290, 'DETAIL 3: PANEL TERMINATION', 'lblb', 'middle'));

  var d3X = 770, d3Y = 310;
  var d3G = $g('hover-part', 'detail-panel');

  // U-channel (vertical, cross-section from side)
  var d3ChW = p.webWidth * d1Sc;
  var d3FlD = p.flangeDepth * d1Sc;
  var d3ChH = 100;

  // Left flange
  d3G.appendChild($r(d3X, d3Y, 3, d3ChH, 'cee'));
  // Web
  d3G.appendChild($r(d3X, d3Y + d3ChH - 3, d3ChW, 3, 'cee'));
  // Right flange
  d3G.appendChild($r(d3X + d3ChW - 3, d3Y, 3, d3ChH, 'cee'));

  // Roof/wall panel sliding into U-channel
  var panelThick = 4;
  var panelLen = 80;
  var panelY = d3Y + 20;
  d3G.appendChild($e('rect', {x: d3X + 3 + 1, y: panelY, width: d3ChW - 6 - 2, height: panelLen,
    class: 'ang-fill'}));
  d3G.appendChild($t(d3X + d3ChW / 2, panelY + panelLen / 2, 'PANEL', 'note', 'middle'));

  // Arrow showing panel insertion direction
  var arrowY = panelY - 15;
  d3G.appendChild($l(d3X + d3ChW / 2, arrowY - 15, d3X + d3ChW / 2, arrowY, 'obj med'));
  d3G.appendChild($l(d3X + d3ChW / 2 - 4, arrowY - 6, d3X + d3ChW / 2, arrowY, 'obj med'));
  d3G.appendChild($l(d3X + d3ChW / 2 + 4, arrowY - 6, d3X + d3ChW / 2, arrowY, 'obj med'));
  d3G.appendChild($t(d3X + d3ChW / 2, arrowY - 20, 'PANEL SLIDES IN', 'note', 'middle'));

  // TEK screws through panel into channel flanges
  d3G.appendChild($c(d3X + 1.5, panelY + 15, 2, 'bolt'));
  d3G.appendChild($c(d3X + d3ChW - 1.5, panelY + 15, 2, 'bolt'));
  d3G.appendChild($c(d3X + 1.5, panelY + 55, 2, 'bolt'));
  d3G.appendChild($c(d3X + d3ChW - 1.5, panelY + 55, 2, 'bolt'));

  // TEK callout
  d3G.appendChild($l(d3X + d3ChW + 5, panelY + 15, d3X + d3ChW + 40, panelY + 15, 'dim'));
  d3G.appendChild($t(d3X + d3ChW + 42, panelY + 18, '#12 TEK (TYP)', 'note'));

  svg.appendChild(d3G);

  // Flange depth callout on Detail 3
  dimV(svg, d3X - 2, d3Y, d3Y + d3ChH, -16, fmtDec(p.flangeDepth) + '"');
  dimH(svg, d3X, d3X + d3ChW, d3Y + d3ChH, 14, fmtDec(p.webWidth) + '"');

  // ════════════════════════════════════════════════════════════════════
  // ZONE 4: BOM TABLE (x=740..1060, y=470..660)
  // ════════════════════════════════════════════════════════════════════
  svg.appendChild($t(900, 470, 'BILL OF MATERIALS', 'lblb', 'middle'));

  var bomX = 740, bomY = 482;
  var bomW = 320, bomRH = 16;
  var bomCols = [0, 50, 85, 150, 210, 260];  // column offsets

  // Header row
  svg.appendChild($e('rect', {x: bomX, y: bomY, width: bomW, height: bomRH, fill: '#333', stroke: '#333'}));
  var bomHeaders = ['MARK', 'QTY', 'LENGTH', 'MATERIAL', 'GAUGE', 'WEIGHT'];
  bomHeaders.forEach(function(h, i) {
    var ht = $t(bomX + bomCols[i] + 4, bomY + 12, h, 'note');
    ht.setAttribute('fill', '#FFF');
    svg.appendChild(ht);
  });

  // Data row
  var totalWeight = Math.round(p.wtPiece * p.qty);
  var bomData = [
    p.mark,
    String(p.qty),
    fmtFtIn(p.lengthIn),
    'G90',
    p.gauge,
    fmtDec(p.wtPiece, 1) + ' lbs'
  ];
  var dr1Y = bomY + bomRH;
  svg.appendChild($r(bomX, dr1Y, bomW, bomRH, 'obj hair'));
  bomData.forEach(function(d, i) {
    svg.appendChild($t(bomX + bomCols[i] + 4, dr1Y + 12, d, 'lbl'));
  });

  // TEK screw row
  var tekPerChannel = 8;
  var tekTotal = tekPerChannel * p.qty;
  var dr2Y = dr1Y + bomRH;
  svg.appendChild($r(bomX, dr2Y, bomW, bomRH, 'obj hair'));
  var tekData = ['TEK', String(tekTotal), '--', 'ZN PLATED', '#12', '--'];
  tekData.forEach(function(d, i) {
    svg.appendChild($t(bomX + bomCols[i] + 4, dr2Y + 12, d, 'lbl'));
  });

  // Total row
  var dr3Y = dr2Y + bomRH;
  svg.appendChild($e('rect', {x: bomX, y: dr3Y, width: bomW, height: bomRH, fill: '#EEE', stroke: '#333'}));
  svg.appendChild($t(bomX + bomCols[3] + 4, dr3Y + 12, 'TOTAL:', 'lblb'));
  svg.appendChild($t(bomX + bomCols[5] + 4, dr3Y + 12, totalWeight + ' lbs', 'lblb'));

  // ════════════════════════════════════════════════════════════════════
  // ZONE 5: TITLE BLOCK (y=680..815)
  // ════════════════════════════════════════════════════════════════════
  drawTitleBlock(svg, {
    projName: projName,
    customer: customer,
    jobNum: jobNum,
    drawingNum: drawingNum,
    drawnBy: drawnBy,
    surfPrep: surfPrep,
    drawingTitle: 'ENDCAP U-CHANNEL',
    partMark: p.mark,
    revision: (window.ENDCAP_CONFIG && window.ENDCAP_CONFIG.revision) || 0,
    revHistory: (window.ENDCAP_CONFIG && window.ENDCAP_CONFIG.rev_history) || [],
    projectNotes: [
      'MATERIAL: 12GA G90 GALVANIZED COIL',
      'ROLL-FORMED FROM ' + fmtDec(p.coilWidth) + '" COIL',
      'ATTACH W/ #12 TEK SCREWS',
      'EMBED ' + fmtDec(p.embedment) + '" BELOW GRADE',
      'SURFACE: ' + surfPrep
    ]
  });

  // ── Tooltip wiring ──
  var tip = document.getElementById('tip');
  svg.querySelectorAll('.hover-part').forEach(function(el) {
    el.addEventListener('mouseenter', function(ev) {
      var part = el.dataset.part || '';
      var html = '';
      if (part === 'endcap-channel') {
        html = '<b>Endcap U-Channel</b>' +
          '<div class="r"><span class="k">Mark</span><span class="v">' + p.mark + '</span></div>' +
          '<div class="r"><span class="k">Length</span><span class="v">' + fmtFtIn(p.lengthIn) + '</span></div>' +
          '<div class="r"><span class="k">Web Width</span><span class="v">' + fmtDec(p.webWidth) + '"</span></div>' +
          '<div class="r"><span class="k">Flange Depth</span><span class="v">' + fmtDec(p.flangeDepth) + '"</span></div>' +
          '<div class="r"><span class="k">Gauge</span><span class="v">' + p.gauge + ' (' + fmtDec(p.thick, 3) + '")</span></div>' +
          '<div class="r"><span class="k">Weight</span><span class="v">' + fmtDec(p.wtPiece, 1) + ' lbs</span></div>';
      } else if (part === 'end-rafter') {
        html = '<b>End Rafter</b><div class="r"><span class="k">Connection</span><span class="v">TEK screws</span></div>';
      } else if (part === 'tek-top' || part === 'tek-section') {
        html = '<b>TEK Screw Connection</b>' +
          '<div class="r"><span class="k">Type</span><span class="v">#12 TEK</span></div>' +
          '<div class="r"><span class="k">Pattern</span><span class="v">2 per flange</span></div>';
      } else if (part === 'section-u') {
        html = '<b>U-Channel Cross Section</b>' +
          '<div class="r"><span class="k">Web</span><span class="v">' + fmtDec(p.webWidth) + '"</span></div>' +
          '<div class="r"><span class="k">Flanges</span><span class="v">' + fmtDec(p.flangeDepth) + '" returns</span></div>' +
          '<div class="r"><span class="k">Gauge</span><span class="v">' + p.gauge + '</span></div>' +
          '<div class="r"><span class="k">Material</span><span class="v">G90 Galvanized</span></div>';
      } else if (part === 'detail-top') {
        html = '<b>Top Connection Detail</b>' +
          '<div class="r"><span class="k">Method</span><span class="v">#12 TEK to end rafter</span></div>' +
          '<div class="r"><span class="k">Qty</span><span class="v">4 per channel</span></div>';
      } else if (part === 'detail-bottom') {
        html = '<b>Bottom / Embedment Detail</b>' +
          '<div class="r"><span class="k">Embedment</span><span class="v">' + fmtDec(p.embedment) + '"</span></div>' +
          '<div class="r"><span class="k">Condition</span><span class="v">Below grade</span></div>';
      } else if (part === 'detail-panel') {
        html = '<b>Panel Termination Detail</b>' +
          '<div class="r"><span class="k">Method</span><span class="v">Panel slides into U-channel</span></div>' +
          '<div class="r"><span class="k">Fasteners</span><span class="v">#12 TEK through flanges</span></div>';
      }
      if (html) {
        tip.innerHTML = html;
        tip.style.display = 'block';
        tip.style.left = (ev.clientX + 14) + 'px';
        tip.style.top = (ev.clientY + 14) + 'px';
      }
    });
    el.addEventListener('mousemove', function(ev) {
      tip.style.left = (ev.clientX + 14) + 'px';
      tip.style.top = (ev.clientY + 14) + 'px';
    });
    el.addEventListener('mouseleave', function() {
      tip.style.display = 'none';
    });
  });

  // ── Update footer stats ──
  var fLen = document.getElementById('fLength');
  var fWidth = document.getElementById('fWidth');
  var fGauge = document.getElementById('fGauge');
  var fQty = document.getElementById('fQty');
  var fWt = document.getElementById('fWt');

  if (fLen) fLen.textContent = fmtFtIn(p.lengthIn);
  if (fWidth) fWidth.textContent = fmtDec(p.webWidth) + '" web / ' + fmtDec(p.flangeDepth) + '" flange';
  if (fGauge) fGauge.textContent = p.gauge;
  if (fQty) fQty.textContent = p.qty;
  if (fWt) fWt.textContent = totalWeight + ' lbs';

  // ── Update BOM side panel ──
  updateBOM([
    { mk: p.mark, qty: p.qty, desc: 'Endcap U-Channel', size: fmtFtIn(p.lengthIn) + ' x ' + fmtDec(p.webWidth) + '"W', mat: 'G90', wt: Math.round(p.wtPiece * p.qty) },
    { mk: 'TEK', qty: tekTotal, desc: '#12 TEK Screw', size: '3/4"', mat: 'ZN', wt: 0 }
  ]);
}
"""

# ═══════════════════════════════════════════════════════════════════════════════
# Controls HTML — endcap-specific inputs
# ═══════════════════════════════════════════════════════════════════════════════

ENDCAP_CONTROLS = """
    <div class="ctrl-group">
      <label>Length (in)</label>
      <input type="number" id="inpLength" value="120" min="24" max="240" step="1" onchange="draw()">
    </div>
    <div class="ctrl-group">
      <label>Gauge</label>
      <select id="selGauge" onchange="draw()">
        <option value="12GA" selected>12GA</option>
        <option value="14GA">14GA</option>
      </select>
    </div>
    <div class="ctrl-group">
      <label>Web Width (in)</label>
      <input type="number" id="inpWebWidth" value="4.0" min="2" max="8" step="0.25" onchange="draw()">
    </div>
    <div class="ctrl-group">
      <label>Flange Depth (in)</label>
      <input type="number" id="inpFlangeDepth" value="1.5" min="0.75" max="3" step="0.25" onchange="draw()">
    </div>
    <div class="ctrl-group">
      <label>Qty</label>
      <input type="number" id="inpQty" value="4" min="1" max="100" step="1" onchange="draw()">
    </div>
    <button class="toggle-btn" onclick="window.print()">Print</button>
"""

# ═══════════════════════════════════════════════════════════════════════════════
# Footer HTML — endcap-specific stats
# ═══════════════════════════════════════════════════════════════════════════════

ENDCAP_FOOTER = """
  <div>Length: <span class="s" id="fLength">--</span></div>
  <div>Width: <span class="s" id="fWidth">--</span></div>
  <div>Gauge: <span class="s" id="fGauge">--</span></div>
  <div>Qty: <span class="s" id="fQty">--</span></div>
  <div>Total Weight: <span class="s" id="fWt">--</span></div>
"""

# ═══════════════════════════════════════════════════════════════════════════════
# Assemble final HTML via drawing_base
# ═══════════════════════════════════════════════════════════════════════════════

ENDCAP_DRAWING_HTML = drawing_base.build_html_shell(
    title="Endcap U-Channel Shop Drawing",
    drawing_type="endcap",
    config_var="ENDCAP_CONFIG",
    controls_html=ENDCAP_CONTROLS,
    footer_html=ENDCAP_FOOTER,
    drawing_js=ENDCAP_JS,
)
