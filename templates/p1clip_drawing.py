"""
TitanForge -- Interactive P1 Clip Shop Drawing Template
=======================================================
Full-featured SVG-based P1 interior purlin clip shop drawing served as an
interactive page.  Pre-fills with project data via window.P1CLIP_CONFIG
injection.  Uses drawing_base.build_html_shell() for consistent dark-theme UI.

P1 Clip specs:
  - Roll-formed from 6" 10GA plate coil (2.83 lbs/LFT, 3000 lb rolls)
  - 10" long x 6" wide, L-shaped bent plate
  - One leg sits flat on rafter top flange, other leg stands vertical as fin
  - Purlin web TEK-screws into the vertical fin
  - 4x 1/4" DIA holes (2 per leg) for TEK screws
  - Each interior purlin line gets one P1 clip per rafter connection
"""

import templates.drawing_base as drawing_base

# ══════════════════════════════════════════════════════════════════════════════
# Component-specific JavaScript: draw() and helpers
# ══════════════════════════════════════════════════════════════════════════════

P1CLIP_JS = r"""
// ── P1 Clip gauge / material tables ──
var GAUGE_THICK = {
  '10GA': 0.135,
  '12GA': 0.105,
  '14GA': 0.075
};

var GAUGE_LBS_LFT = {
  '10GA': 2.83,
  '12GA': 2.18,
  '14GA': 1.56
};

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
  var widthIn  = parseFloat(document.getElementById('inpWidth').value)  || 10;
  var heightIn = parseFloat(document.getElementById('inpHeight').value) || 6;
  var gauge    = document.getElementById('selGauge').value || '10GA';
  var qty      = parseInt(document.getElementById('inpQty').value) || 1;
  var mark     = document.getElementById('inpMark').value || 'P1';

  var thick    = GAUGE_THICK[gauge] || 0.135;
  var lbsLft   = GAUGE_LBS_LFT[gauge] || 2.83;

  // Weight: clip is cut from 6" coil, 10" long = 10/12 LFT
  var wtEach   = Math.round(lbsLft * (widthIn / 12) * 100) / 100;
  var wtTotal  = Math.round(wtEach * qty * 100) / 100;

  // Hole spacing defaults
  var holeDia     = 0.25;
  var holeLegEdge = 1.25;           // edge distance from bend line
  var holeEndEdge = 2.0;            // edge distance from clip ends
  var holeSpanW   = widthIn - 2 * holeEndEdge;  // spacing along width
  var holeSpanH   = heightIn / 2;   // spacing between holes on each leg

  // Bend radius ~ 2x thickness
  var bendR = Math.round(thick * 2 * 1000) / 1000;

  return {
    widthIn: widthIn, heightIn: heightIn, gauge: gauge, thick: thick,
    qty: qty, mark: mark, lbsLft: lbsLft, wtEach: wtEach, wtTotal: wtTotal,
    holeDia: holeDia, holeLegEdge: holeLegEdge, holeEndEdge: holeEndEdge,
    holeSpanW: holeSpanW, holeSpanH: holeSpanH, bendR: bendR,
    material: '10GA G90'
  };
}

// ── Update footer stats ──
function updateFooter(p) {
  var el;
  el = document.getElementById('fDims');   if (el) el.textContent = p.widthIn + '" x ' + p.heightIn + '"';
  el = document.getElementById('fGauge');  if (el) el.textContent = p.gauge;
  el = document.getElementById('fQty');    if (el) el.textContent = p.qty;
  el = document.getElementById('fWtEach'); if (el) el.textContent = fmtDec(p.wtEach) + ' lbs';
  el = document.getElementById('fWtTot');  if (el) el.textContent = fmtDec(p.wtTotal) + ' lbs';
}

// ══════════════════════════════════════════════════════════════════════════
// ZONE 1 — FRONT VIEW  (top-left quadrant)
// Shows clip from front: vertical fin + horizontal base
// ══════════════════════════════════════════════════════════════════════════
function drawFrontView(svg, p) {
  var g = $g('hover-part', 'front-view');

  // Drawing area: x 40..520, y 30..340
  var ox = 100, oy = 60;
  // Scale so the clip fits nicely
  var maxDim = Math.max(p.widthIn, p.heightIn);
  var sc = 220 / maxDim;

  var W = p.widthIn * sc;   // scaled width (horizontal base)
  var H = p.heightIn * sc;  // scaled total height
  var T = p.thick * sc * 8; // exaggerated thickness for visibility
  if (T < 3) T = 3;

  // Vertical fin (centred above base)
  var finL = ox + (W - H) / 2;  // fin left (fin width = heightIn when viewed from front we see the fin edge-on)
  // Actually from the FRONT we see: horizontal base full width, vertical fin full width (same width as base)
  // The fin extends upward from the base.  Both legs are heightIn/2 long.
  var legLen = (p.heightIn / 2) * sc;
  var baseY = oy + legLen;  // bend line y

  // Horizontal base leg (bottom)
  g.appendChild($e('rect', {
    x: ox, y: baseY, width: W, height: T,
    class: 'clip-fill'
  }));

  // Vertical fin (top) — from bend line going up
  g.appendChild($e('rect', {
    x: ox, y: baseY - legLen, width: W, height: legLen,
    class: 'clip-fill'
  }));

  // Bend line indicator
  g.appendChild($l(ox - 5, baseY, ox + W + 5, baseY, 'center'));

  // Holes on vertical fin (2 holes)
  var hy1 = baseY - legLen / 2;
  var hx1 = ox + p.holeEndEdge * sc;
  var hx2 = ox + W - p.holeEndEdge * sc;
  var hr  = (p.holeDia / 2) * sc * 4; // exaggerated for visibility
  if (hr < 3) hr = 3;

  g.appendChild($c(hx1, hy1, hr, 'bolt'));
  g.appendChild($c(hx2, hy1, hr, 'bolt'));
  // Crosshairs
  [hx1, hx2].forEach(function(hx) {
    g.appendChild($l(hx - hr - 2, hy1, hx + hr + 2, hy1, 'center'));
    g.appendChild($l(hx, hy1 - hr - 2, hx, hy1 + hr + 2, 'center'));
  });

  // Holes on horizontal base (2 holes)
  var hy2 = baseY + T / 2 + legLen * 0.35;
  // Draw base leg extending down too for clarity
  g.appendChild($e('rect', {
    x: ox, y: baseY + T, width: W, height: legLen - T,
    class: 'clip-fill'
  }));
  var hy2b = baseY + T + (legLen - T) / 2;
  g.appendChild($c(hx1, hy2b, hr, 'bolt'));
  g.appendChild($c(hx2, hy2b, hr, 'bolt'));
  [hx1, hx2].forEach(function(hx) {
    g.appendChild($l(hx - hr - 2, hy2b, hx + hr + 2, hy2b, 'center'));
    g.appendChild($l(hx, hy2b - hr - 2, hx, hy2b + hr + 2, 'center'));
  });

  // ── Dimensions ──
  var totalH = legLen * 2 + T;
  var topY = baseY - legLen;
  var botY = baseY + legLen;

  dimH(svg, ox, ox + W, botY, 22, fmtDec(p.widthIn) + '"');
  dimV(svg, ox + W, topY, botY, 22, fmtDec(p.heightIn) + '"');

  // Leg length dims
  dimV(svg, ox, topY, baseY, -22, fmtDec(p.heightIn / 2) + '" FIN');
  dimV(svg, ox, baseY, botY, -22, fmtDec(p.heightIn / 2) + '" BASE');

  // Hole spacing horizontal
  dimH(svg, hx1, hx2, topY, -16, fmtDec(p.holeSpanW) + '"');

  // Zone label
  g.appendChild($t(ox + W / 2, topY - 30, 'FRONT VIEW', 'ttl', 'middle'));

  svg.appendChild(g);

  // Tooltip data
  g.addEventListener('mouseenter', function(ev) { showTip(ev, 'Front View',
    [['Width', fmtDec(p.widthIn) + '"'], ['Height', fmtDec(p.heightIn) + '"'],
     ['Gauge', p.gauge], ['Holes', '4x 1/4" DIA']]); });
  g.addEventListener('mouseleave', hideTip);
}

// ══════════════════════════════════════════════════════════════════════════
// ZONE 2 — SIDE VIEW  (top-right quadrant)
// Shows L-profile from the side
// ══════════════════════════════════════════════════════════════════════════
function drawSideView(svg, p) {
  var g = $g('hover-part', 'side-view');

  var ox = 620, oy = 80;
  var sc = 30;  // px per inch
  var legH = (p.heightIn / 2) * sc;
  var T = p.thick * sc * 6;
  if (T < 3) T = 3;

  var bendX = ox + legH;
  var bendY = oy + legH;

  // Vertical fin (going up from bend)
  g.appendChild($e('rect', {
    x: bendX - T / 2, y: bendY - legH, width: T, height: legH,
    class: 'clip-fill'
  }));

  // Horizontal base (going right from bend)
  g.appendChild($e('rect', {
    x: bendX, y: bendY - T / 2, width: legH, height: T,
    class: 'clip-fill'
  }));

  // Bend arc indicator
  var arcR = 12;
  g.appendChild($p(
    'M ' + bendX + ' ' + (bendY - arcR) +
    ' A ' + arcR + ' ' + arcR + ' 0 0 1 ' + (bendX + arcR) + ' ' + bendY,
    'dim'
  ));

  // 90-degree angle annotation
  g.appendChild($t(bendX + arcR + 4, bendY - arcR + 2, '90\u00B0', 'dimtxt'));

  // Dimension: vertical leg
  dimV(svg, bendX - T / 2, bendY - legH, bendY, -20, fmtDec(p.heightIn / 2) + '"');

  // Dimension: horizontal leg
  dimH(svg, bendX, bendX + legH, bendY + T / 2, 20, fmtDec(p.heightIn / 2) + '"');

  // Thickness callout
  var callX = bendX + legH * 0.6;
  var callY = bendY - T / 2 - 8;
  g.appendChild($l(callX, bendY - T / 2, callX, callY - 2, 'dim'));
  g.appendChild($l(callX, callY - 2, callX + 30, callY - 2, 'dim'));
  g.appendChild($t(callX + 32, callY, p.gauge + ' (' + fmtDec(p.thick, 3) + '")', 'note'));

  // Zone label
  g.appendChild($t(ox + legH, oy - 20, 'SIDE VIEW', 'ttl', 'middle'));

  svg.appendChild(g);

  g.addEventListener('mouseenter', function(ev) { showTip(ev, 'Side View (L-Profile)',
    [['Bend Angle', '90\u00B0'], ['Leg Length', fmtDec(p.heightIn / 2) + '" ea.'],
     ['Thickness', p.gauge + ' (' + fmtDec(p.thick, 3) + '")']]); });
  g.addEventListener('mouseleave', hideTip);
}

// ══════════════════════════════════════════════════════════════════════════
// ZONE 3 — DETAILS (bottom-left area, y 360..660)
// ══════════════════════════════════════════════════════════════════════════

// DETAIL 1: Hole pattern
function drawDetail1(svg, p) {
  var g = $g('hover-part', 'hole-pattern');
  var ox = 40, oy = 380;

  g.appendChild($t(ox + 100, oy, 'DETAIL 1: HOLE PATTERN', 'lblb'));

  // Flat plate outline (unfolded for clarity)
  var sc = 16;
  var W = p.widthIn * sc;
  var H = p.heightIn * sc;
  var py = oy + 16;

  g.appendChild($e('rect', {
    x: ox, y: py, width: W, height: H / 2,
    class: 'obj thin', fill: '#F8F8F8'
  }));

  // 4 holes
  var hr = 5;
  var hx1 = ox + p.holeEndEdge * sc;
  var hx2 = ox + W - p.holeEndEdge * sc;
  var hy1 = py + H * 0.12;
  var hy2 = py + H * 0.38;

  [hx1, hx2].forEach(function(hx) {
    [hy1, hy2].forEach(function(hy) {
      g.appendChild($c(hx, hy, hr, 'bolt'));
      g.appendChild($l(hx - hr - 1, hy, hx + hr + 1, hy, 'center'));
      g.appendChild($l(hx, hy - hr - 1, hx, hy + hr + 1, 'center'));
    });
  });

  // Dimension: hole-to-hole horizontal
  dimH(svg, hx1, hx2, hy1, -14, fmtDec(p.holeSpanW) + '"');

  // Dimension: hole-to-hole vertical
  dimV(svg, hx2, hy1, hy2, 16, fmtDec(p.holeSpanH) + '"');

  // Edge distance callouts
  dimH(svg, ox, hx1, hy2, 14, fmtDec(p.holeEndEdge) + '"');
  dimH(svg, hx2, ox + W, hy2, 14, fmtDec(p.holeEndEdge) + '"');

  // Hole callout
  g.appendChild($l(hx1 + hr, hy1 - hr, hx1 + 40, hy1 - 20, 'dim'));
  g.appendChild($t(hx1 + 42, hy1 - 22, '4x \u00D8' + fmtDec(p.holeDia) + '" (1/4" TEK)', 'noteb'));

  svg.appendChild(g);

  g.addEventListener('mouseenter', function(ev) { showTip(ev, 'Hole Pattern',
    [['Qty', '4x holes'], ['Diameter', '1/4"'], ['Edge Dist', fmtDec(p.holeEndEdge) + '"'],
     ['H Spacing', fmtDec(p.holeSpanW) + '"']]); });
  g.addEventListener('mouseleave', hideTip);
}

// DETAIL 2: Installed assembly view
function drawDetail2(svg, p) {
  var g = $g('hover-part', 'installed-view');
  var ox = 340, oy = 380;

  g.appendChild($t(ox + 100, oy, 'DETAIL 2: INSTALLED VIEW', 'lblb'));

  var py = oy + 20;
  // Rafter top flange (horizontal beam)
  g.appendChild($e('rect', {
    x: ox, y: py + 60, width: 220, height: 10,
    class: 'cee'
  }));
  g.appendChild($t(ox + 230, py + 68, 'RAFTER', 'note'));
  // Rafter web going down
  g.appendChild($e('rect', {
    x: ox + 105, y: py + 70, width: 6, height: 50,
    class: 'cee'
  }));

  // P1 clip sitting on top of rafter flange
  // Horizontal base of clip on rafter flange
  g.appendChild($e('rect', {
    x: ox + 70, y: py + 55, width: 80, height: 5,
    class: 'clip-fill'
  }));
  // Vertical fin of clip going up
  g.appendChild($e('rect', {
    x: ox + 107, y: py + 10, width: 5, height: 45,
    class: 'clip-fill'
  }));

  // Purlin (Z-shape) attached to fin
  // Top flange
  g.appendChild($e('rect', {
    x: ox + 90, y: py + 10, width: 40, height: 4,
    class: 'conn-plate'
  }));
  // Web
  g.appendChild($e('rect', {
    x: ox + 112, y: py + 14, width: 4, height: 36,
    class: 'conn-plate'
  }));
  // Bottom flange
  g.appendChild($e('rect', {
    x: ox + 88, y: py + 46, width: 40, height: 4,
    class: 'conn-plate'
  }));

  g.appendChild($t(ox + 140, py + 30, 'PURLIN', 'note'));

  // TEK screw indicators
  g.appendChild($c(ox + 110, py + 22, 2.5, 'bolt'));
  g.appendChild($c(ox + 110, py + 40, 2.5, 'bolt'));
  g.appendChild($l(ox + 114, py + 22, ox + 150, py + 18, 'dim'));
  g.appendChild($t(ox + 152, py + 18, 'TEK SCREW', 'note'));

  // TEK screws through base into rafter
  g.appendChild($c(ox + 90, py + 58, 2.5, 'bolt'));
  g.appendChild($c(ox + 130, py + 58, 2.5, 'bolt'));
  g.appendChild($l(ox + 134, py + 58, ox + 158, py + 78, 'dim'));
  g.appendChild($t(ox + 160, py + 80, 'TEK TO RAFTER', 'note'));

  // Clip label
  g.appendChild($l(ox + 80, py + 52, ox + 50, py + 42, 'dim'));
  g.appendChild($t(ox + 12, py + 40, 'P1 CLIP', 'noteb'));

  svg.appendChild(g);

  g.addEventListener('mouseenter', function(ev) { showTip(ev, 'Installed Assembly',
    [['Clip', 'P1 on rafter flange'], ['Attachment', '1/4" TEK screws'],
     ['Purlin', 'Z-purlin TEK\'d to fin']]); });
  g.addEventListener('mouseleave', hideTip);
}

// DETAIL 3: Bend detail
function drawDetail3(svg, p) {
  var g = $g('hover-part', 'bend-detail');
  var ox = 620, oy = 380;

  g.appendChild($t(ox + 80, oy, 'DETAIL 3: BEND DETAIL', 'lblb'));

  var py = oy + 30;
  var sc = 3;

  // Large-scale bend cross-section
  var legPx = 50;
  var thkPx = 8;
  var bendCx = ox + 80;
  var bendCy = py + legPx;

  // Vertical leg (going up)
  g.appendChild($e('rect', {
    x: bendCx - thkPx / 2, y: bendCy - legPx, width: thkPx, height: legPx,
    class: 'clip-fill'
  }));

  // Horizontal leg (going right)
  g.appendChild($e('rect', {
    x: bendCx, y: bendCy - thkPx / 2, width: legPx, height: thkPx,
    class: 'clip-fill'
  }));

  // Inner bend radius arc
  var rInner = 14;
  g.appendChild($p(
    'M ' + bendCx + ' ' + (bendCy - rInner) +
    ' A ' + rInner + ' ' + rInner + ' 0 0 1 ' + (bendCx + rInner) + ' ' + bendCy,
    'obj med'
  ));

  // Outer bend radius arc
  var rOuter = rInner + thkPx;
  g.appendChild($p(
    'M ' + (bendCx - thkPx / 2) + ' ' + (bendCy - rOuter + thkPx / 2) +
    ' A ' + rOuter + ' ' + rOuter + ' 0 0 1 ' + (bendCx + rOuter - thkPx / 2) + ' ' + (bendCy + thkPx / 2),
    'obj thin'
  ));

  // Radius callout line
  var rCallX = bendCx + rInner * 0.7;
  var rCallY = bendCy - rInner * 0.7;
  g.appendChild($l(bendCx, bendCy, rCallX + 20, rCallY - 20, 'dim'));
  g.appendChild($t(rCallX + 22, rCallY - 22, 'R = ' + fmtDec(p.bendR, 3) + '"', 'noteb'));

  // Gauge callout
  g.appendChild($l(bendCx + legPx * 0.5, bendCy - thkPx / 2, bendCx + legPx * 0.5, bendCy - thkPx / 2 - 20, 'dim'));
  g.appendChild($l(bendCx + legPx * 0.5, bendCy + thkPx / 2, bendCx + legPx * 0.5, bendCy + thkPx / 2 + 5, 'dim'));
  g.appendChild($l(bendCx + legPx * 0.5, bendCy - thkPx / 2 - 20, bendCx + legPx * 0.5 + 35, bendCy - thkPx / 2 - 20, 'dim'));
  g.appendChild($t(bendCx + legPx * 0.5 + 37, bendCy - thkPx / 2 - 18, p.gauge + ' (' + fmtDec(p.thick, 3) + '")', 'noteb'));

  // 90-deg angle arc
  var angR = 22;
  g.appendChild($p(
    'M ' + bendCx + ' ' + (bendCy - angR) +
    ' A ' + angR + ' ' + angR + ' 0 0 1 ' + (bendCx + angR) + ' ' + bendCy,
    'dim'
  ));
  g.appendChild($t(bendCx + angR + 4, bendCy - angR + 4, '90\u00B0', 'dimtxt'));

  // Notes
  g.appendChild($t(ox + 10, py + legPx + 40, 'BEND: 90\u00B0 INSIDE', 'note'));
  g.appendChild($t(ox + 10, py + legPx + 50, 'RADIUS: ' + fmtDec(p.bendR, 3) + '"', 'note'));
  g.appendChild($t(ox + 10, py + legPx + 60, 'MATERIAL: ' + p.gauge + ' G90 GALV', 'note'));
  g.appendChild($t(ox + 10, py + legPx + 70, 'COIL: 6" WIDE, 2.83 LBS/LFT', 'note'));

  svg.appendChild(g);

  g.addEventListener('mouseenter', function(ev) { showTip(ev, 'Bend Detail',
    [['Bend Angle', '90\u00B0'], ['Inside Radius', fmtDec(p.bendR, 3) + '"'],
     ['Gauge at Bend', p.gauge + ' (' + fmtDec(p.thick, 3) + '")']]); });
  g.addEventListener('mouseleave', hideTip);
}

// ══════════════════════════════════════════════════════════════════════════
// ZONE 4 — BOM TABLE  (drawn in SVG, bottom-centre area)
// ══════════════════════════════════════════════════════════════════════════
function drawBomTable(svg, p) {
  var g = $g('', 'bom-table');
  var ox = 40, oy = 560, cw = [80, 40, 110, 100, 90, 80];
  var tw = 0; cw.forEach(function(w) { tw += w; });
  var rh = 16;

  // Header row
  g.appendChild($e('rect', {x: ox, y: oy, width: tw, height: rh, fill: '#333', stroke: '#333'}));
  var headers = ['MARK', 'QTY', 'MATERIAL', 'SIZE', 'GAUGE', 'WT EA'];
  var cx = ox;
  headers.forEach(function(h, i) {
    var t = $t(cx + 4, oy + 12, h, 'note');
    t.setAttribute('fill', '#FFF');
    g.appendChild(t);
    cx += cw[i];
  });

  // Data row
  var dy = oy + rh;
  g.appendChild($e('rect', {x: ox, y: dy, width: tw, height: rh, fill: 'none', stroke: '#999', 'stroke-width': '0.5'}));
  var vals = [
    p.mark,
    String(p.qty),
    p.material,
    fmtDec(p.widthIn) + '" x ' + fmtDec(p.heightIn) + '"',
    p.gauge,
    fmtDec(p.wtEach) + ' lbs'
  ];
  cx = ox;
  vals.forEach(function(v, i) {
    g.appendChild($t(cx + 4, dy + 12, v, 'lbl'));
    cx += cw[i];
  });

  // Total row
  var ty = dy + rh;
  g.appendChild($e('rect', {x: ox, y: ty, width: tw, height: rh, fill: '#F8F8F0', stroke: '#999', 'stroke-width': '0.5'}));
  g.appendChild($t(ox + 4, ty + 12, 'TOTAL WEIGHT:', 'lblb'));
  g.appendChild($t(ox + cw[0] + cw[1] + cw[2] + cw[3] + cw[4] + 4, ty + 12, fmtDec(p.wtTotal) + ' lbs', 'lblb'));

  // Table title
  g.appendChild($t(ox + tw / 2, oy - 8, 'BILL OF MATERIALS', 'lblb', 'middle'));

  svg.appendChild(g);

  // Also populate the BOM side panel
  updateBOM([{
    mk: p.mark,
    qty: p.qty,
    desc: 'P1 Interior Purlin Clip',
    size: fmtDec(p.widthIn) + '" x ' + fmtDec(p.heightIn) + '"',
    mat: p.material,
    wt: p.wtTotal
  }]);
}

// ══════════════════════════════════════════════════════════════════════════
// ZONE 5 — TITLE BLOCK  (uses shared drawTitleBlock)
// ══════════════════════════════════════════════════════════════════════════
function drawTitleBlockZone(svg, p) {
  var cfg = window.P1CLIP_CONFIG || {};
  drawTitleBlock(svg, {
    projName:     document.getElementById('setProjectName').value || cfg.project_name || '',
    customer:     document.getElementById('setCustomer').value || cfg.customer || '',
    jobNum:       document.getElementById('setJobNumber').value || cfg.job_code || '',
    drawingNum:   document.getElementById('setDrawingNum').value || cfg.drawing_num || 'SD-P1C-001',
    drawnBy:      document.getElementById('setDrawnBy').value || 'AUTO',
    surfPrep:     document.getElementById('setSurfPrep').value || 'G90 GALV',
    drawingTitle: 'P1 CLIP SHOP DRAWING',
    partMark:     p.mark,
    revision:     0,
    revHistory:   [],
    projectNotes: [
      'MATERIAL: ' + p.gauge + ' G90 GALVANIZED',
      'COIL WIDTH: 6" (2.83 LBS/LFT)',
      'ROLL SIZE: 3000 LB ROLLS',
      'ALL HOLES: 1/4" DIA FOR TEK SCREWS',
      'BEND: 90\u00B0 INSIDE, R=' + fmtDec(p.bendR, 3) + '"',
      'FINISH: G90 GALVANIZED (NO PAINT)'
    ]
  });
}

// ══════════════════════════════════════════════════════════════════════════
// TOOLTIP helpers
// ══════════════════════════════════════════════════════════════════════════
function showTip(ev, title, rows) {
  var tip = document.getElementById('tip');
  var html = '<b>' + title + '</b>';
  rows.forEach(function(r) {
    html += '<div class="r"><span class="k">' + r[0] + '</span><span class="v">' + r[1] + '</span></div>';
  });
  tip.innerHTML = html;
  tip.style.display = 'block';
  tip.style.left = (ev.clientX + 14) + 'px';
  tip.style.top = (ev.clientY + 14) + 'px';
}
function hideTip() {
  document.getElementById('tip').style.display = 'none';
}

// Track mouse for tooltip positioning
document.addEventListener('mousemove', function(ev) {
  var tip = document.getElementById('tip');
  if (tip && tip.style.display === 'block') {
    tip.style.left = (ev.clientX + 14) + 'px';
    tip.style.top = (ev.clientY + 14) + 'px';
  }
});

// ══════════════════════════════════════════════════════════════════════════
// MAIN DRAW
// ══════════════════════════════════════════════════════════════════════════
function draw() {
  var svg = document.getElementById('svg');
  svg.innerHTML = '';

  // Sheet border
  svg.appendChild($r(10, 10, 1080, 830, 'obj thick'));

  var p = getParams();
  updateFooter(p);

  // Zone separator lines
  svg.appendChild($l(540, 10, 540, 350, 'obj hair'));   // vertical split top
  svg.appendChild($l(10, 350, 1080, 350, 'obj hair'));   // horizontal split mid
  svg.appendChild($l(10, 550, 1080, 550, 'obj hair'));   // above BOM
  svg.appendChild($l(10, 670, 1080, 670, 'obj hair'));   // above title block

  drawFrontView(svg, p);
  drawSideView(svg, p);
  drawDetail1(svg, p);
  drawDetail2(svg, p);
  drawDetail3(svg, p);
  drawBomTable(svg, p);
  drawTitleBlockZone(svg, p);
}
"""

# ══════════════════════════════════════════════════════════════════════════════
# Controls HTML — inserted into the top bar
# ══════════════════════════════════════════════════════════════════════════════

P1CLIP_CONTROLS = """
    <div class="ctrl-group">
      <label>Width (in)</label>
      <input type="number" id="inpWidth" value="10" min="4" max="24" step="0.5" onchange="draw()">
    </div>
    <div class="ctrl-group">
      <label>Height (in)</label>
      <input type="number" id="inpHeight" value="6" min="3" max="12" step="0.5" onchange="draw()">
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
      <input type="text" id="inpMark" value="P1" style="width:60px;" onchange="draw()">
    </div>
    <button class="toggle-btn" onclick="window.print()">Print</button>
"""

# ══════════════════════════════════════════════════════════════════════════════
# Footer HTML — stats bar at bottom
# ══════════════════════════════════════════════════════════════════════════════

P1CLIP_FOOTER = """
  <div>Dimensions: <span class="s" id="fDims">--</span></div>
  <div>Gauge: <span class="s" id="fGauge">--</span></div>
  <div>Qty: <span class="s" id="fQty">--</span></div>
  <div>Wt Each: <span class="s" id="fWtEach">--</span></div>
  <div>Total Wt: <span class="s" id="fWtTot">--</span></div>
"""

# ══════════════════════════════════════════════════════════════════════════════
# Assemble final HTML via shared builder
# ══════════════════════════════════════════════════════════════════════════════

P1CLIP_DRAWING_HTML = drawing_base.build_html_shell(
    title="P1 Clip Shop Drawing",
    drawing_type="p1clip",
    config_var="P1CLIP_CONFIG",
    controls_html=P1CLIP_CONTROLS,
    footer_html=P1CLIP_FOOTER,
    drawing_js=P1CLIP_JS,
)
