"""
TitanForge -- Interactive Z-Purlin Shop Drawing Template
========================================================
Full-featured SVG-based Z-purlin shop drawing served as an interactive page.
Pre-fills with project data via window.PURLIN_CONFIG injection.
Uses drawing_base.build_html_shell() for consistent dark-theme UI.

Z-Purlin specs (from defaults.py):
  - 20.125" coil width, 12GA default, G90 galvanised
  - Z-12"x3.5"x12GA profile (roll-formed in-house)
  - 7.43 lbs/lft
  - Attached to rafters via P1 clips
  - Connected with sag rods for lateral bracing
"""

import templates.drawing_base as drawing_base

# ═══════════════════════════════════════════════════════════════════════════════
# Component-specific JavaScript: draw() and helpers
# ═══════════════════════════════════════════════════════════════════════════════

PURLIN_JS = r"""
// ── Z-Purlin dimension tables ──
var PURLIN_SPECS = {
  '8':  { depth: 8,  topFlange: 2.75, botFlange: 2.75, lip: 0.625, coilWidth: 14.75 },
  '10': { depth: 10, topFlange: 3.25, botFlange: 3.25, lip: 0.625, coilWidth: 17.875 },
  '12': { depth: 12, topFlange: 3.5,  botFlange: 3.5,  lip: 0.75,  coilWidth: 20.125 }
};

var GAUGE_THICK = {
  '12GA': 0.105,
  '14GA': 0.075
};

var GAUGE_LBS = {
  '12GA': { '8': 5.20, '10': 6.30, '12': 7.43 },
  '14GA': { '8': 3.70, '10': 4.50, '12': 5.30 }
};

// ── Apply server config to controls ──
function applyComponentConfig(cfg) {
  if (cfg.depth) {
    var el = document.getElementById('selDepth');
    if (el) el.value = String(cfg.depth);
  }
  if (cfg.gauge) {
    var el = document.getElementById('selGauge');
    if (el) el.value = cfg.gauge;
  }
  if (cfg.span_ft) {
    var el = document.getElementById('inpSpan');
    if (el) el.value = cfg.span_ft;
  }
  if (cfg.spacing_in) {
    var el = document.getElementById('inpSpacing');
    if (el) el.value = cfg.spacing_in;
  }
}

// ── Read current control values ──
function getParams() {
  var depth = parseInt(document.getElementById('selDepth').value) || 12;
  var gauge = document.getElementById('selGauge').value || '12GA';
  var spanFt = parseFloat(document.getElementById('inpSpan').value) || 25;
  var spacingIn = parseFloat(document.getElementById('inpSpacing').value) || 60;
  var qty = (window.PURLIN_CONFIG && window.PURLIN_CONFIG.qty) || Math.ceil(spanFt * 12 / spacingIn) + 1;
  var spec = PURLIN_SPECS[String(depth)] || PURLIN_SPECS['12'];
  var thick = GAUGE_THICK[gauge] || 0.105;
  var lbsLft = (GAUGE_LBS[gauge] && GAUGE_LBS[gauge][String(depth)]) || 7.43;
  var spanIn = spanFt * 12;
  var cutLen = spanIn;  // purlin cut length = span between rafter faces
  var wtPiece = lbsLft * (cutLen / 12);
  var mark = (window.PURLIN_CONFIG && window.PURLIN_CONFIG.mark) || ('Z' + depth + '-' + gauge.replace('GA',''));

  return {
    depth: depth, gauge: gauge, thick: thick, spanFt: spanFt, spanIn: spanIn,
    spacingIn: spacingIn, qty: qty, spec: spec, lbsLft: lbsLft,
    cutLen: cutLen, wtPiece: wtPiece, mark: mark,
    material: 'G90', coating: 'G90'
  };
}

// ═══════════════════════════════════════════════
// MAIN DRAW FUNCTION
// ═══════════════════════════════════════════════
function draw() {
  var svg = document.getElementById('svg');
  while (svg.firstChild) svg.removeChild(svg.firstChild);
  svg.setAttribute('viewBox', '0 0 1100 940');

  var p = getParams();
  var sp = p.spec;

  // Settings panel values
  var projName = document.getElementById('setProjectName').value || 'PROJECT';
  var customer = document.getElementById('setCustomer').value || '';
  var jobNum = document.getElementById('setJobNumber').value || '';
  var drawingNum = document.getElementById('setDrawingNum').value || 'SD-001';
  var drawnBy = document.getElementById('setDrawnBy').value || 'AUTO';
  var surfPrep = document.getElementById('setSurfPrep').value || 'G90';

  // ════════════════════════════════════════════════════════════════════
  // ZONE 1: ELEVATION VIEW (y=25 to y=220)
  // Side view of Z-purlin spanning between rafters — CAD-quality
  // ════════════════════════════════════════════════════════════════════
  svg.appendChild($t(350, 22, 'ELEVATION VIEW', 'ttl'));

  // Layout dimensions
  var evL = 60, evR = 650;    // left/right extent of elevation
  var evY = 65;                // top of purlin in elevation
  var rafW = 30;               // rafter width seen in side view
  var evSpan = evR - evL - 2 * rafW;  // clear span between rafters
  var sc = evSpan / p.spanIn;  // px per inch
  var purlinH = p.depth * sc;  // depth at scale
  if (purlinH < 20) purlinH = 20;  // min visual height
  var scaleFactor = purlinH / p.depth;  // actual px/in for vertical

  // ── Rafters (cross-section blocks at each end) ──
  var lgR = $g('hover-part', 'rafter-L');
  // Rafter body with hatching (cut surface indicator)
  lgR.appendChild($r(evL, evY - 15, rafW, purlinH + 30, 'gus'));
  // Cross-hatch lines inside rafter (indicates cut section)
  for (var hi = 0; hi < 5; hi++) {
    var hy = evY - 10 + hi * (purlinH + 20) / 5;
    lgR.appendChild($l(evL + 2, hy, evL + rafW - 2, hy + 8, 'dim'));
  }
  lgR.appendChild($t(evL + rafW/2, evY + purlinH + 28, 'RAFTER', 'note', 'middle'));
  svg.appendChild(lgR);

  var rgR = $g('hover-part', 'rafter-R');
  rgR.appendChild($r(evR - rafW, evY - 15, rafW, purlinH + 30, 'gus'));
  for (var hi = 0; hi < 5; hi++) {
    var hy = evY - 10 + hi * (purlinH + 20) / 5;
    rgR.appendChild($l(evR - rafW + 2, hy, evR - 2, hy + 8, 'dim'));
  }
  rgR.appendChild($t(evR - rafW/2, evY + purlinH + 28, 'RAFTER', 'note', 'middle'));
  svg.appendChild(rgR);

  // ── Purlin body (side view showing Z-shape profile) ──
  var pL = evL + rafW;       // purlin left edge
  var pR = evR - rafW;       // purlin right edge
  var purG = $g('hover-part', 'purlin');

  // Web (thick object line)
  purG.appendChild($r(pL, evY, pR - pL, purlinH, 'obj thick'));

  // Top flange extends to left (Z-shape characteristic)
  var flangeW = sp.topFlange * scaleFactor;
  if (flangeW < 8) flangeW = 8;
  purG.appendChild($r(pL - flangeW + 2, evY - 3, flangeW + (pR - pL) * 0.02, 3, 'cee'));

  // Bottom flange extends to right (Z-shape characteristic)
  purG.appendChild($r(pR - (pR - pL) * 0.02, evY + purlinH, flangeW + (pR - pL) * 0.02, 3, 'cee'));

  // Centerline (long-short-long dash pattern)
  purG.appendChild($l((pL + pR)/2, evY - 20, (pL + pR)/2, evY + purlinH + 20, 'center'));
  svg.appendChild(purG);

  // ── P1 Clip connections at each end (detailed) ──
  var clipG = $g('hover-part', 'p1-clips');
  var clipH = Math.max(14, purlinH * 0.6);
  var clipW = 8;

  // Left P1 clip — vertical leg + horizontal seat
  clipG.appendChild($r(pL - 2, evY - 2, clipW, clipH, 'clip-fill'));
  clipG.appendChild($r(pL - 2, evY + clipH - 4, clipW + 4, 4, 'clip-fill'));  // seat
  clipG.appendChild($c(pL + 2, evY + 4, 1.5, 'bolt'));
  clipG.appendChild($c(pL + 2, evY + clipH - 8, 1.5, 'bolt'));
  // Weld tick mark at clip base
  clipG.appendChild($l(pL - 2, evY + clipH - 2, pL - 6, evY + clipH + 3, 'weld-ref'));

  // Right P1 clip
  clipG.appendChild($r(pR - clipW + 2, evY - 2, clipW, clipH, 'clip-fill'));
  clipG.appendChild($r(pR - clipW - 2, evY + clipH - 4, clipW + 4, 4, 'clip-fill'));
  clipG.appendChild($c(pR - 2, evY + 4, 1.5, 'bolt'));
  clipG.appendChild($c(pR - 2, evY + clipH - 8, 1.5, 'bolt'));
  clipG.appendChild($l(pR + 2, evY + clipH - 2, pR + 6, evY + clipH + 3, 'weld-ref'));
  svg.appendChild(clipG);

  svg.appendChild($t(pL + 2, evY - 10, 'P1 CLIP (TYP)', 'noteb', 'middle'));

  // ── Sag rod location indicator(s) along span ──
  // Sag rods at mid-span (or 1/3 points if span > 30ft)
  var sagG = $g('hover-part', 'sag-rods');
  var numSagPts = p.spanFt > 30 ? 2 : 1;
  for (var si = 0; si < numSagPts; si++) {
    var sagFrac = numSagPts === 1 ? 0.5 : (si + 1) / (numSagPts + 1);
    var sagX = pL + (pR - pL) * sagFrac;
    // Triangle pointer indicating sag rod location
    sagG.appendChild($l(sagX, evY + purlinH + 2, sagX, evY + purlinH + 14, 'obj med'));
    sagG.appendChild($l(sagX - 3, evY + purlinH + 14, sagX + 3, evY + purlinH + 14, 'obj med'));
    sagG.appendChild($t(sagX, evY + purlinH + 23, 'SR', 'noteb', 'middle'));
  }
  // Sag rod dimension from end
  if (numSagPts === 1) {
    dimH(svg, pL, pL + (pR - pL) * 0.5, evY - 15, -14, fmtFtIn(p.spanIn / 2));
  }
  svg.appendChild(sagG);

  // ── Splice location indicator (if span exceeds typical stock length) ──
  var maxStockFt = 53;  // max single-piece purlin length
  if (p.spanFt > maxStockFt) {
    var splG = $g('hover-part', 'splice-loc');
    var splX = pL + (pR - pL) * 0.5;  // splice at midpoint
    // Dashed vertical line at splice
    splG.appendChild($l(splX - 12, evY - 5, splX - 12, evY + purlinH + 5, 'hidden'));
    splG.appendChild($l(splX + 12, evY - 5, splX + 12, evY + purlinH + 5, 'hidden'));
    // Lap overlap hatching
    splG.appendChild($e('rect', {x: splX - 12, y: evY, width: 24, height: purlinH,
      fill: '#F6AE2D', 'fill-opacity': '0.12', stroke: 'none'}));
    splG.appendChild($t(splX, evY - 8, 'LAP SPLICE', 'noteb', 'middle'));
    svg.appendChild(splG);
  }

  // ── Section cut indicator A-A (through center) ──
  var secX = (pL + pR) / 2;
  svg.appendChild($l(secX - 8, evY - 25, secX - 8, evY + purlinH + 25, 'cut-line'));
  svg.appendChild($l(secX + 8, evY - 25, secX + 8, evY + purlinH + 25, 'cut-line'));
  svg.appendChild($t(secX - 8, evY - 28, 'A', 'lblb', 'middle'));
  svg.appendChild($t(secX + 8, evY - 28, 'A', 'lblb', 'middle'));

  // ── Elevation dimensions ──
  dimH(svg, pL, pR, evY + purlinH + 30, 20, fmtFtIn(p.spanIn));
  dimV(svg, pL - flangeW - 5, evY, evY + purlinH, -18, p.depth + '"');

  // Scale note
  var elevScale = fmtScale(sc);
  svg.appendChild($t(350, evY + purlinH + 64, 'SCALE: ' + elevScale, 'note', 'middle'));

  // ════════════════════════════════════════════════════════════════════
  // ZONE 1b: ADDITIONAL ELEVATION INFO (right side, y=25 to y=220)
  // ════════════════════════════════════════════════════════════════════
  var infoX = 700;
  svg.appendChild($t(infoX + 100, 35, 'PURLIN SCHEDULE', 'lblb', 'middle'));
  svg.appendChild($l(infoX + 10, 40, infoX + 190, 40, 'obj hair'));

  var infoLines = [
    ['MARK:', p.mark],
    ['DEPTH:', p.depth + '"'],
    ['GAUGE:', p.gauge + ' (' + fmtDec(p.thick, 3) + '")'],
    ['MATERIAL:', 'G90 GALVANIZED'],
    ['TOP FLANGE:', sp.topFlange + '"'],
    ['BOT FLANGE:', sp.botFlange + '"'],
    ['LIP:', sp.lip + '"'],
    ['COIL WIDTH:', sp.coilWidth + '"'],
    ['SPAN:', fmtFtIn(p.spanIn)],
    ['SPACING:', fmtFtIn(p.spacingIn) + ' O.C.'],
    ['WT/LFT:', fmtDec(p.lbsLft) + ' lbs/ft'],
    ['WT/PIECE:', fmtDec(p.wtPiece) + ' lbs'],
    ['QTY:', p.qty]
  ];
  infoLines.forEach(function(pair, i) {
    var iy = 55 + i * 13;
    svg.appendChild($t(infoX + 12, iy, pair[0], 'note'));
    svg.appendChild($t(infoX + 80, iy, String(pair[1]), 'lbl'));
  });

  // ════════════════════════════════════════════════════════════════════
  // ZONE 2: SECTION A-A (y=230 to y=450)
  // Full Z-shape cross-section
  // ════════════════════════════════════════════════════════════════════
  svg.appendChild($t(200, 235, 'SECTION A-A', 'ttl'));

  var cx = 200;   // section center X
  var cy = 350;   // section center Y
  var zScale = 6; // px per inch for cross-section detail

  var zD = p.depth * zScale;          // web height
  var zTF = sp.topFlange * zScale;    // top flange width
  var zBF = sp.botFlange * zScale;    // bottom flange width
  var zLip = sp.lip * zScale;         // lip height
  var zT = Math.max(p.thick * zScale, 1.5); // material thickness

  // The Z-shape: top flange goes LEFT, bottom flange goes RIGHT
  // Drawing from top-left, clockwise for outer, with thickness

  var zTop = cy - zD / 2;
  var zBot = cy + zD / 2;

  var secG = $g('hover-part', 'z-section');

  // Top lip — angled 45° going RIGHT (opposite of top flange direction)
  // Lip starts at left end of top flange and angles up-right
  var lipLen = zLip;  // lip length in px
  var lip45 = lipLen * Math.cos(Math.PI/4);  // 45° component
  var topLipX1 = cx - zTF;
  var topLipY1 = zTop;
  var topLipX2 = topLipX1 + lip45;
  var topLipY2 = topLipY1 - lip45;
  // Draw as a thick polygon (two parallel lines with thickness)
  var lipNx = zT * Math.cos(Math.PI/4) / 2;  // normal offset for thickness
  var lipNy = zT * Math.sin(Math.PI/4) / 2;
  var topLipPts = [
    (topLipX1 - lipNy) + ',' + (topLipY1 - lipNx),
    (topLipX2 - lipNy) + ',' + (topLipY2 - lipNx),
    (topLipX2 + lipNy) + ',' + (topLipY2 + lipNx),
    (topLipX1 + lipNy) + ',' + (topLipY1 + lipNx)
  ].join(' ');
  secG.appendChild($p(topLipPts, 'cee'));

  // Top flange (extends left from web top)
  secG.appendChild($r(cx - zTF, zTop, zTF, zT, 'cee'));

  // Web (vertical, centered)
  secG.appendChild($r(cx - zT/2, zTop, zT, zD, 'cee'));

  // Bottom flange (extends right from web bottom)
  secG.appendChild($r(cx, zBot - zT, zBF, zT, 'cee'));

  // Bottom lip — angled 45° going LEFT (opposite of bottom flange direction)
  // Lip starts at right end of bottom flange and angles down-left
  var botLipX1 = cx + zBF;
  var botLipY1 = zBot;
  var botLipX2 = botLipX1 - lip45;
  var botLipY2 = botLipY1 + lip45;
  var botLipPts = [
    (botLipX1 - lipNy) + ',' + (botLipY1 + lipNx),
    (botLipX2 - lipNy) + ',' + (botLipY2 + lipNx),
    (botLipX2 + lipNy) + ',' + (botLipY2 - lipNx),
    (botLipX1 + lipNy) + ',' + (botLipY1 - lipNx)
  ].join(' ');
  secG.appendChild($p(botLipPts, 'cee'));

  // Centerlines
  secG.appendChild($l(cx, zTop - lip45 - 15, cx, zBot + lip45 + 15, 'center'));
  secG.appendChild($l(cx - zTF - 20, cy, cx + zBF + 20, cy, 'center'));
  svg.appendChild(secG);

  // Bolt hole locations (for P1 clip attachment)
  var boltG = $g('hover-part', 'bolt-holes');
  // Two holes in web near top
  boltG.appendChild($c(cx, zTop + zD * 0.2, 2.5, 'bolt'));
  boltG.appendChild($c(cx, zTop + zD * 0.4, 2.5, 'bolt'));
  // Two holes in web near bottom
  boltG.appendChild($c(cx, zBot - zD * 0.2, 2.5, 'bolt'));
  boltG.appendChild($c(cx, zBot - zD * 0.4, 2.5, 'bolt'));
  svg.appendChild(boltG);
  svg.appendChild($t(cx + 12, zTop + zD * 0.3, '15/16" HOLES (TYP)', 'note'));

  // ── Section A-A dimensions ──
  // Depth
  dimV(svg, cx + zBF + 8, zTop, zBot, 18, p.depth + '"');

  // Top flange width
  dimH(svg, cx - zTF, cx, zTop - 5, -14, sp.topFlange + '"');

  // Bottom flange width
  dimH(svg, cx, cx + zBF, zBot + 5, 14, sp.botFlange + '"');

  // Top lip (angled — show length along the 45° lip)
  // Dimension line running parallel to the lip
  svg.appendChild($t(topLipX2 + 5, topLipY2 - 3, sp.lip + '"', 'note'));

  // Bottom lip (angled — show length along the 45° lip)
  svg.appendChild($t(botLipX2 - 25, botLipY2 + 10, sp.lip + '"', 'note'));

  // Gauge callout
  svg.appendChild($t(cx - zTF - 30, cy, p.gauge, 'lblb', 'middle'));
  svg.appendChild($t(cx - zTF - 30, cy + 10, '(' + fmtDec(p.thick, 3) + '")', 'note', 'middle'));

  // Material callout
  svg.appendChild($t(cx + zBF + 35, cy + 30, 'MATERIAL:', 'noteb'));
  svg.appendChild($t(cx + zBF + 35, cy + 40, 'G90 GALVANIZED', 'note'));
  svg.appendChild($t(cx + zBF + 35, cy + 50, 'STEEL', 'note'));

  // Scale
  svg.appendChild($t(200, zBot + lip45 + 35, 'SCALE: 1" = ' + fmtDec(1/zScale * 12, 1) + '"', 'note', 'middle'));

  // ════════════════════════════════════════════════════════════════════
  // ZONE 3: DETAIL VIEWS (y=230 to y=450, right side + below)
  // ════════════════════════════════════════════════════════════════════

  // ── DETAIL 1: P1 Clip Connection (x=420, y=240) ──
  svg.appendChild($t(530, 235, 'DETAIL 1: P1 CLIP CONNECTION', 'ttl'));

  var d1x = 480, d1y = 310;
  var d1Scale = 4; // px per inch

  var d1G = $g('hover-part', 'detail-p1');

  // Rafter top chord (horizontal beam cross-section)
  var rafDepth = 14 * d1Scale;
  var rafThk = 3;
  d1G.appendChild($r(d1x - 30, d1y, 60, rafDepth, 'gus'));
  d1G.appendChild($t(d1x, d1y + rafDepth + 12, 'RAFTER', 'note', 'middle'));

  // P1 clip (L-shaped bracket sitting on rafter, holding purlin)
  var clipTop = d1y - 2;
  var clipLen = 10 * d1Scale;
  // Vertical leg of clip (welded to rafter)
  d1G.appendChild($r(d1x - 3, d1y - clipLen * 0.3, 6, clipLen * 0.6, 'clip-fill'));
  // Horizontal seat of clip
  d1G.appendChild($r(d1x - 3, d1y - clipLen * 0.3, clipLen * 0.4, 4, 'clip-fill'));

  // Purlin cross-section sitting on clip
  var pSectH = p.depth * d1Scale * 0.6;
  var pSectW = 4;
  d1G.appendChild($r(d1x - pSectW/2, d1y - clipLen * 0.3 - pSectH, pSectW, pSectH, 'cee'));
  d1G.appendChild($t(d1x + 15, d1y - clipLen * 0.3 - pSectH/2, 'Z-PURLIN', 'note'));

  // Bolts through clip to purlin
  d1G.appendChild($c(d1x, d1y - clipLen * 0.3 - pSectH * 0.3, 2, 'bolt'));
  d1G.appendChild($c(d1x, d1y - clipLen * 0.3 - pSectH * 0.7, 2, 'bolt'));

  // Weld symbol at clip-to-rafter junction
  d1G.appendChild($l(d1x - 8, d1y + 2, d1x - 18, d1y - 12, 'weld-ref'));
  d1G.appendChild($t(d1x - 28, d1y - 15, '1/8"', 'weld-txt'));
  d1G.appendChild($t(d1x - 35, d1y - 8, 'FILLET', 'weld-txt'));

  // TEK screw callout
  d1G.appendChild($t(d1x + 20, d1y - clipLen * 0.1, '(2) #10 TEK', 'noteb'));
  d1G.appendChild($t(d1x + 20, d1y - clipLen * 0.1 + 9, 'SCREWS', 'note'));

  svg.appendChild(d1G);
  svg.appendChild($t(530, d1y + rafDepth + 30, 'NTS', 'note', 'middle'));

  // ── DETAIL 2: Sag Rod Connection (x=720, y=240) ──
  svg.appendChild($t(820, 235, 'DETAIL 2: SAG ROD', 'ttl'));

  var d2x = 780, d2y = 310;
  var d2G = $g('hover-part', 'detail-sag');

  // Purlin web (vertical)
  d2G.appendChild($r(d2x - 2, d2y - 40, 4, 80, 'cee'));
  d2G.appendChild($t(d2x + 8, d2y - 35, 'PURLIN WEB', 'note'));

  // Angle bracket
  d2G.appendChild($p('M ' + (d2x - 2) + ' ' + (d2y - 10) +
                      ' L ' + (d2x - 25) + ' ' + (d2y - 10) +
                      ' L ' + (d2x - 25) + ' ' + (d2y + 10) +
                      ' L ' + (d2x - 2) + ' ' + (d2y + 10), 'ang-fill'));
  d2G.appendChild($t(d2x - 30, d2y, 'L2x2x', 'note', 'end'));
  d2G.appendChild($t(d2x - 30, d2y + 9, p.gauge, 'note', 'end'));

  // Sag rod (horizontal line extending from angle)
  d2G.appendChild($l(d2x - 25, d2y, d2x - 70, d2y, 'obj thick'));
  d2G.appendChild($c(d2x - 25, d2y, 2, 'bolt'));
  d2G.appendChild($t(d2x - 70, d2y - 5, 'SAG ROD', 'noteb'));
  d2G.appendChild($t(d2x - 70, d2y + 8, '(CONTINUOUS)', 'note'));

  // TEK screws through angle to purlin web
  d2G.appendChild($c(d2x, d2y - 5, 1.5, 'bolt'));
  d2G.appendChild($c(d2x, d2y + 5, 1.5, 'bolt'));
  d2G.appendChild($t(d2x + 8, d2y + 5, '(2) #10 TEK', 'noteb'));

  svg.appendChild(d2G);
  svg.appendChild($t(820, d2y + 55, 'NTS', 'note', 'middle'));

  // ── DETAIL 3: Purlin Lap Splice (x=720, y=410) ──
  svg.appendChild($t(820, 400, 'DETAIL 3: PURLIN LAP SPLICE', 'ttl'));

  var d3x = 780, d3y = 460;
  var d3G = $g('hover-part', 'detail-splice');

  // Two overlapping purlins (side view)
  var lapLen = 50;
  // Bottom purlin
  d3G.appendChild($r(d3x - 80, d3y, 80 + lapLen/2, 10, 'cee'));
  d3G.appendChild($t(d3x - 75, d3y + 8, 'PURLIN A', 'note'));

  // Top purlin (overlapping)
  d3G.appendChild($r(d3x - lapLen/2, d3y - 3, 80 + lapLen/2, 10, 'cee'));
  d3G.appendChild($t(d3x + 50, d3y + 5, 'PURLIN B', 'note'));

  // Overlap region hatching
  svg.appendChild($e('rect', {x: d3x - lapLen/2, y: d3y - 3, width: lapLen, height: 13,
    fill: '#F6AE2D', 'fill-opacity': '0.15', stroke: '#F6AE2D', 'stroke-width': '0.5', 'stroke-dasharray': '3,2'}));

  // Bolts through lap
  d3G.appendChild($c(d3x - 12, d3y + 4, 2, 'bolt'));
  d3G.appendChild($c(d3x + 12, d3y + 4, 2, 'bolt'));

  // Dimension: lap length
  dimH(svg, d3x - lapLen/2, d3x + lapLen/2, d3y + 12, 14, 'LAP = 24"');

  // Rafter below
  d3G.appendChild($r(d3x - 15, d3y + 15, 30, 25, 'gus'));
  d3G.appendChild($t(d3x, d3y + 30, 'RAFTER', 'note', 'middle'));

  // TEK screw callout
  d3G.appendChild($t(d3x + 30, d3y - 10, '(8) #10 TEK SCREWS', 'noteb'));
  d3G.appendChild($t(d3x + 30, d3y - 1, 'THRU OVERLAP', 'note'));

  svg.appendChild(d3G);
  svg.appendChild($t(820, d3y + 55, 'NTS', 'note', 'middle'));

  // ════════════════════════════════════════════════════════════════════
  // ZONE 4: BOM TABLE (y=480 to y=660)
  // ════════════════════════════════════════════════════════════════════
  svg.appendChild($t(300, 480, 'BILL OF MATERIALS', 'ttl'));

  var bomX = 40, bomY = 492, bomW = 620;
  var cols = [0, 80, 120, 220, 340, 410, 510];
  var hdrs = ['MARK', 'QTY', 'DESCRIPTION', 'SIZE', 'MATERIAL', 'WT/PC (LBS)', 'TOTAL (LBS)'];

  // Header row
  svg.appendChild($e('rect', {x: bomX, y: bomY, width: bomW, height: 14, fill: '#333', stroke: '#333'}));
  hdrs.forEach(function(h, i) {
    var ht = $t(bomX + cols[i] + 4, bomY + 11, h, 'note');
    ht.setAttribute('fill', '#FFF');
    svg.appendChild(ht);
  });

  // BOM rows
  var bomRows = [];

  // Row 1: Z-Purlin
  var totalWtPurlin = p.wtPiece * p.qty;
  bomRows.push({
    mk: p.mark, qty: p.qty,
    desc: 'Z-PURLIN ' + p.depth + '"x' + sp.topFlange + '"',
    size: fmtFtIn(p.cutLen) + ' x ' + p.gauge,
    mat: 'G90', wtPc: fmtDec(p.wtPiece), wtTot: fmtDec(totalWtPurlin)
  });

  // Row 2: P1 Clips
  var p1Qty = p.qty * 2;
  var p1Wt = 2.8;  // approx weight per P1 clip
  bomRows.push({
    mk: 'P1', qty: p1Qty,
    desc: 'PURLIN CLIP',
    size: '10GA x 4"',
    mat: 'G90', wtPc: fmtDec(p1Wt), wtTot: fmtDec(p1Wt * p1Qty)
  });

  // Row 3: TEK Screws (per purlin)
  var tekQty = p1Qty * 2;
  bomRows.push({
    mk: 'TEK', qty: tekQty,
    desc: '#10 TEK SCREW',
    size: '3/4"',
    mat: 'ZN', wtPc: '--', wtTot: '--'
  });

  // Row 4: Sag rod angle brackets (estimate 1 per purlin)
  var sagQty = p.qty;
  var sagWt = 1.2;
  bomRows.push({
    mk: 'SR-A', qty: sagQty,
    desc: 'SAG ROD ANGLE',
    size: 'L2x2x' + p.gauge,
    mat: 'G90', wtPc: fmtDec(sagWt), wtTot: fmtDec(sagWt * sagQty)
  });

  var totalWeight = totalWtPurlin + (p1Wt * p1Qty) + (sagWt * sagQty);

  bomRows.forEach(function(row, i) {
    var ry = bomY + 14 + i * 14;
    svg.appendChild($l(bomX, ry + 14, bomX + bomW, ry + 14, 'dim'));
    var vals = [row.mk, String(row.qty), row.desc, row.size, row.mat, row.wtPc, row.wtTot];
    vals.forEach(function(v, ci) {
      svg.appendChild($t(bomX + cols[ci] + 4, ry + 11, v, 'lbl'));
    });
  });

  // Total row
  var totY = bomY + 14 + bomRows.length * 14;
  svg.appendChild($l(bomX, totY, bomX + bomW, totY, 'obj med'));
  svg.appendChild($t(bomX + cols[5] + 4, totY + 12, 'TOTAL:', 'lblb'));
  svg.appendChild($t(bomX + cols[6] + 4, totY + 12, fmtDec(totalWeight) + ' LBS', 'lblb'));

  // Outer box for BOM table
  var bomH = 14 + (bomRows.length + 1) * 14 + 4;
  svg.appendChild($r(bomX, bomY, bomW, bomH, 'obj med'));

  // ── Notes area (right of BOM) ──
  var noteX = 700, noteY = 490;
  svg.appendChild($t(noteX + 100, 480, 'NOTES', 'ttl'));
  var notes = [
    '1. ALL PURLINS ROLL-FORMED IN-HOUSE FROM ' + sp.coilWidth + '" COIL',
    '2. MATERIAL: ' + p.gauge + ' G90 GALVANIZED STEEL',
    '3. PURLINS ATTACHED TO RAFTERS VIA P1 CLIPS',
    '4. P1 CLIPS SHOP-WELDED TO RAFTER (1/8" FILLET)',
    '5. FIELD-ATTACHED WITH (2) #10 TEK SCREWS PER CLIP',
    '6. SAG RODS AT MID-SPAN FOR LATERAL BRACING',
    '7. LAP SPLICE 24" MIN AT INTERIOR RAFTERS',
    '8. SPLICE FASTENED WITH (8) #10 TEK SCREWS',
    '9. SPACING: ' + fmtFtIn(p.spacingIn) + ' O.C.',
    '10. DO NOT SCALE DRAWING',
    '11. TOL: LENGTH +/-1/16"',
    '12. HOLES: 15/16" DIA STD (FOR CLIP BOLTS)'
  ];
  notes.forEach(function(n, i) {
    svg.appendChild($t(noteX, noteY + 4 + i * 10, n, 'note'));
  });

  // ════════════════════════════════════════════════════════════════════
  // ZONE 4b: DRILL SCHEDULE (y=620 to y=680)
  // Fabrication-ready hole pattern table
  // ════════════════════════════════════════════════════════════════════
  var dsY = 625;
  svg.appendChild($t(noteX + 100, dsY - 5, 'DRILL SCHEDULE', 'ttl'));

  var dsX = noteX, dsW = 340;
  var dsCols = [0, 55, 110, 180, 260];
  var dsHdrs = ['MARK', 'HOLE DIA', 'QTY/PC', 'LOCATION', 'NOTES'];

  // Header row
  svg.appendChild($e('rect', {x: dsX, y: dsY, width: dsW, height: 14, fill: '#333', stroke: '#333'}));
  dsHdrs.forEach(function(h, i) {
    var ht = $t(dsX + dsCols[i] + 4, dsY + 11, h, 'note');
    ht.setAttribute('fill', '#FFF');
    svg.appendChild(ht);
  });

  // Drill schedule rows
  var dsRows = [
    { mk: p.mark, dia: '15/16"', qtyPc: '4', loc: 'WEB — CLIP BOLT', note: 'STD' },
    { mk: p.mark, dia: '9/16"', qtyPc: '2', loc: 'WEB — SAG ROD', note: 'MID-SPAN' }
  ];

  // Add splice holes if span requires splice
  if (p.spanFt > 53) {
    dsRows.push({ mk: p.mark, dia: '15/16"', qtyPc: '8', loc: 'FLANGES — SPLICE', note: 'LAP ZONE' });
  }

  dsRows.forEach(function(row, i) {
    var ry = dsY + 14 + i * 14;
    svg.appendChild($l(dsX, ry + 14, dsX + dsW, ry + 14, 'dim'));
    var vals = [row.mk, row.dia, row.qtyPc, row.loc, row.note];
    vals.forEach(function(v, ci) {
      svg.appendChild($t(dsX + dsCols[ci] + 4, ry + 11, v, 'lbl'));
    });
  });

  // Outer box for drill schedule
  var dsH = 14 + (dsRows.length + 1) * 14;
  svg.appendChild($r(dsX, dsY, dsW, dsH, 'obj med'));

  // ════════════════════════════════════════════════════════════════════
  // ZONE 5: TITLE BLOCK (y=770 to y=905)
  // ════════════════════════════════════════════════════════════════════
  drawTitleBlock(svg, {
    projName: projName,
    customer: customer,
    jobNum: jobNum,
    drawingNum: drawingNum,
    drawnBy: drawnBy,
    surfPrep: surfPrep,
    drawingTitle: 'PURLIN',
    partMark: p.mark,
    revision: 0,
    revHistory: [],
    projectNotes: [
      'MATERIAL: ' + p.gauge + ' G90 GALVANIZED STEEL',
      'COIL: ' + sp.coilWidth + '" ROLL-FORMED IN-HOUSE',
      'SURF PREP: G90 GALVANIZED (NO PAINT)',
      'HOLES: 15/16" DIA STD',
      'FASTENERS: #10 TEK SCREWS (FIELD)',
      'P1 CLIPS: SHOP WELD 1/8" FILLET (WPS-C)',
      'SAG RODS: CONTINUOUS, ANGLE-BRACKET ATTACH',
      'LAP SPLICE: 24" MIN, (8) TEK SCREWS',
      'SPACING: ' + fmtFtIn(p.spacingIn) + ' O.C.',
      'FAB: AISC 360-22 / AWS D1.1',
      'DO NOT SCALE DRAWING',
      'PIECE MARK = ERECTION MARK',
      'TOL: LENGTH +/-1/16" / HOLES +/-1/32"'
    ]
  });

  // ── Update footer stats ──
  var fSpan = document.getElementById('fSpan');
  var fDepth = document.getElementById('fDepth');
  var fGauge = document.getElementById('fGauge');
  var fSpacing = document.getElementById('fSpacing');
  var fQty = document.getElementById('fQty');
  var fWt = document.getElementById('fWt');
  if (fSpan) fSpan.textContent = fmtFtIn(p.spanIn);
  if (fDepth) fDepth.textContent = p.depth + '"';
  if (fGauge) fGauge.textContent = p.gauge;
  if (fSpacing) fSpacing.textContent = fmtFtIn(p.spacingIn) + ' O.C.';
  if (fQty) fQty.textContent = p.qty;
  if (fWt) fWt.textContent = fmtDec(totalWeight) + ' lbs';

  // ── Update BOM side panel ──
  updateBOM([
    { mk: p.mark, qty: p.qty, desc: 'Z-Purlin ' + p.depth + '"', size: fmtFtIn(p.cutLen) + ' x ' + p.gauge, mat: 'G90', wt: Math.round(totalWtPurlin) },
    { mk: 'P1', qty: p1Qty, desc: 'Purlin Clip', size: '10GA x 4"', mat: 'G90', wt: Math.round(p1Wt * p1Qty) },
    { mk: 'TEK', qty: tekQty, desc: '#10 TEK Screw', size: '3/4"', mat: 'ZN', wt: 0 },
    { mk: 'SR-A', qty: sagQty, desc: 'Sag Rod Angle', size: 'L2x2', mat: 'G90', wt: Math.round(sagWt * sagQty) }
  ]);
}
"""

# ═══════════════════════════════════════════════════════════════════════════════
# Controls HTML — purlin-specific inputs
# ═══════════════════════════════════════════════════════════════════════════════

PURLIN_CONTROLS = """
    <div class="ctrl-group">
      <label>Depth</label>
      <select id="selDepth" onchange="draw()">
        <option value="8">8"</option>
        <option value="10">10"</option>
        <option value="12" selected>12"</option>
      </select>
    </div>
    <div class="ctrl-group">
      <label>Gauge</label>
      <select id="selGauge" onchange="draw()">
        <option value="12GA" selected>12GA</option>
        <option value="14GA">14GA</option>
      </select>
    </div>
    <div class="ctrl-group">
      <label>Span (ft)</label>
      <input type="number" id="inpSpan" value="25" min="5" max="60" step="0.5" onchange="draw()">
    </div>
    <div class="ctrl-group">
      <label>Spacing (in)</label>
      <input type="number" id="inpSpacing" value="60" min="12" max="96" step="6" onchange="draw()">
    </div>
    <button class="toggle-btn" onclick="window.print()">Print</button>
"""

# ═══════════════════════════════════════════════════════════════════════════════
# Footer HTML — purlin-specific stats
# ═══════════════════════════════════════════════════════════════════════════════

PURLIN_FOOTER = """
  <div>Span: <span class="s" id="fSpan">--</span></div>
  <div>Depth: <span class="s" id="fDepth">--</span></div>
  <div>Gauge: <span class="s" id="fGauge">--</span></div>
  <div>Spacing: <span class="s" id="fSpacing">--</span></div>
  <div>Qty/Bay: <span class="s" id="fQty">--</span></div>
  <div>Total Wt: <span class="s" id="fWt">--</span></div>
"""

# ═══════════════════════════════════════════════════════════════════════════════
# Assemble final HTML via drawing_base
# ═══════════════════════════════════════════════════════════════════════════════

PURLIN_DRAWING_HTML = drawing_base.build_html_shell(
    title="Purlin Shop Drawing",
    drawing_type="purlin",
    config_var="PURLIN_CONFIG",
    controls_html=PURLIN_CONTROLS,
    footer_html=PURLIN_FOOTER,
    drawing_js=PURLIN_JS,
)
