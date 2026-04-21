"""
TitanForge -- Interactive Z-Purlin Shop Drawing Template v2
============================================================
Redesigned purlin drawing with per-group tabs, Z-profile cross-section,
elevation view, purlin schedule table, and solar hole punch toggle.

Groups come from the building's BOM data (injected via window.PURLIN_CONFIG.purlin_groups).
Each group has: depth, gauge, qty, span_ft, spacing_ft, mark.

Uses drawing_base.build_html_shell() for the outer wrapper.
"""

import templates.drawing_base as drawing_base

# ===================================================================
# Component-specific JavaScript: draw() and helpers
# ===================================================================

PURLIN_V2_JS = r"""
// ── Z-Purlin dimension tables ──
var PURLIN_SPECS = {
  '8':  { depth: 8,  topFlange: 2.75, botFlange: 2.75, lip: 0.625, coilWidth: 14.75 },
  '10': { depth: 10, topFlange: 3.25, botFlange: 3.25, lip: 0.625, coilWidth: 17.875 },
  '12': { depth: 12, topFlange: 3.5,  botFlange: 3.5,  lip: 0.75,  coilWidth: 20.125 }
};

var GAUGE_THICK = { '12GA': 0.105, '14GA': 0.075 };
var GAUGE_LBS = {
  '12GA': { '8': 5.20, '10': 6.30, '12': 7.43 },
  '14GA': { '8': 3.70, '10': 4.50, '12': 5.30 }
};

// ── Solar hole pattern specs ──
var SOLAR_SPEC = {
  holeDia: 0.4375,         // 7/16" holes
  holeSpacing: 24,         // 24" O.C. between attachment points
  edgeDist: 3,             // 3" from purlin end
  holesPerPoint: 2,        // 2 holes per attachment bracket
  holePairGap: 2,          // 2" between paired holes
  bracketWidth: 4          // 4" bracket footprint
};

// ── State ──
var activeGroupIdx = 0;
var solarEnabled = false;

// ── Get purlin groups from config ──
function getGroups() {
  var cfg = window.PURLIN_CONFIG || {};
  var groups = cfg.purlin_groups || [];
  if (groups.length === 0) {
    // Fallback default group
    groups = [{
      group: 1, label: '12" Z-Purlin @ 25\'', type: 'standard',
      depth: 12, gauge: '12GA', thickness: 0.105, span_ft: 25,
      spacing_ft: 5, qty: 6, topFlange: 3.5, botFlange: 3.5,
      lip: 0.75, coilWidth: 20.125, lbs_per_ft: 7.43, mark: 'Z12-12'
    }];
  }
  return groups;
}

// ── Apply server config to controls ──
function applyComponentConfig(cfg) {
  // Build tab bar from purlin groups
  buildGroupTabs();
}

// ── Build group tab bar ──
function buildGroupTabs() {
  var groups = getGroups();
  var container = document.getElementById('groupTabBar');
  if (!container) return;
  container.innerHTML = '';

  groups.forEach(function(g, i) {
    var btn = document.createElement('button');
    btn.className = 'toggle-btn' + (i === activeGroupIdx ? ' active' : '');
    btn.textContent = g.label || ('Group ' + g.group);
    btn.onclick = function() {
      activeGroupIdx = i;
      buildGroupTabs();
      draw();
    };
    container.appendChild(btn);
  });
}

// ── Get active group params ──
function getParams() {
  var groups = getGroups();
  var g = groups[activeGroupIdx] || groups[0];

  var depth = g.depth || 12;
  var gauge = g.gauge || '12GA';
  var spec = PURLIN_SPECS[String(depth)] || PURLIN_SPECS['12'];
  var thick = g.thickness || GAUGE_THICK[gauge] || 0.105;
  var lbsLft = g.lbs_per_ft || (GAUGE_LBS[gauge] && GAUGE_LBS[gauge][String(depth)]) || 7.43;
  var spanFt = g.span_ft || 25;
  var spanIn = spanFt * 12;
  var spacingFt = g.spacing_ft || 5;
  var spacingIn = spacingFt * 12;
  var qty = g.qty || 6;
  var cutLen = spanIn;
  var wtPiece = lbsLft * (cutLen / 12);
  var mark = g.mark || ('Z' + depth + '-' + gauge.replace('GA',''));
  var groupType = g.type || 'standard';

  return {
    depth: depth, gauge: gauge, thick: thick, spanFt: spanFt, spanIn: spanIn,
    spacingFt: spacingFt, spacingIn: spacingIn, qty: qty,
    spec: { topFlange: g.topFlange || spec.topFlange, botFlange: g.botFlange || spec.botFlange,
            lip: g.lip || spec.lip, coilWidth: g.coilWidth || spec.coilWidth },
    lbsLft: lbsLft, cutLen: cutLen, wtPiece: wtPiece, mark: mark,
    groupType: groupType, material: 'G90', coating: 'G90',
    solar: solarEnabled
  };
}

// ==============================================
// MAIN DRAW FUNCTION
// ==============================================
function draw() {
  var svg = document.getElementById('svg');
  while (svg.firstChild) svg.removeChild(svg.firstChild);
  svg.setAttribute('viewBox', '0 0 1100 850');

  var p = getParams();
  var sp = p.spec;

  // Settings panel values
  var projName = document.getElementById('setProjectName').value || 'PROJECT';
  var customer = document.getElementById('setCustomer').value || '';
  var jobNum = document.getElementById('setJobNumber').value || '';
  var drawingNum = document.getElementById('setDrawingNum').value || 'SD-001';
  var drawnBy = document.getElementById('setDrawnBy').value || 'AUTO';
  var surfPrep = document.getElementById('setSurfPrep').value || 'G90';

  // ================================================================
  // ZONE 1: Z-PURLIN PROFILE (cross-section) — LEFT SIDE (x=40..380)
  // ================================================================
  // Z-purlin: top flange RIGHT, bottom flange LEFT, lips at ends
  svg.appendChild($t(200, 22, 'SECTION A-A: Z-PURLIN PROFILE', 'ttl'));

  var cx = 200, cy = 220;
  var zScale = 7;

  var zD = p.depth * zScale;
  var zTF = sp.topFlange * zScale;
  var zBF = sp.botFlange * zScale;
  var zLip = sp.lip * zScale;
  var zT = Math.max(p.thick * zScale, 1.5);

  var zTop = cy - zD / 2;
  var zBot = cy + zD / 2;

  var secG = $g('hover-part', 'z-section');

  // Web (vertical, centered on cx)
  secG.appendChild($r(cx - zT/2, zTop, zT, zD, 'cee'));

  // Top flange (extends RIGHT from top of web)
  secG.appendChild($r(cx, zTop, zTF, zT, 'cee'));

  // Bottom flange (extends LEFT from bottom of web)
  secG.appendChild($r(cx - zBF, zBot - zT, zBF, zT, 'cee'));

  // Top lip — at right end of top flange, curls UP-RIGHT at ~45deg
  var lipLen = zLip;
  var lip45 = lipLen * Math.cos(Math.PI/4);
  var lipNx = zT * Math.cos(Math.PI/4) / 2;
  var lipNy = zT * Math.sin(Math.PI/4) / 2;

  var topLipX1 = cx + zTF;
  var topLipY1 = zTop;
  var topLipX2 = topLipX1 + lip45;
  var topLipY2 = topLipY1 - lip45;
  var topLipPts = [
    (topLipX1 - lipNy) + ',' + (topLipY1 - lipNx),
    (topLipX2 - lipNy) + ',' + (topLipY2 - lipNx),
    (topLipX2 + lipNy) + ',' + (topLipY2 + lipNx),
    (topLipX1 + lipNy) + ',' + (topLipY1 + lipNx)
  ].join(' ');
  secG.appendChild($e('polygon', {points: topLipPts, class: 'cee'}));

  // Bottom lip — at left end of bottom flange, curls DOWN-LEFT at ~45deg
  var botLipX1 = cx - zBF;
  var botLipY1 = zBot;
  var botLipX2 = botLipX1 - lip45;
  var botLipY2 = botLipY1 + lip45;
  var botLipPts = [
    (botLipX1 + lipNy) + ',' + (botLipY1 + lipNx),
    (botLipX2 + lipNy) + ',' + (botLipY2 + lipNx),
    (botLipX2 - lipNy) + ',' + (botLipY2 - lipNx),
    (botLipX1 - lipNy) + ',' + (botLipY1 - lipNx)
  ].join(' ');
  secG.appendChild($e('polygon', {points: botLipPts, class: 'cee'}));

  // Centerlines
  secG.appendChild($l(cx, zTop - lip45 - 15, cx, zBot + lip45 + 15, 'center'));
  secG.appendChild($l(cx - zBF - 20, cy, cx + zTF + 20, cy, 'center'));
  svg.appendChild(secG);

  // Bolt holes in web
  var boltG = $g('hover-part', 'bolt-holes');
  boltG.appendChild($c(cx, zTop + zD * 0.2, 2.5, 'bolt'));
  boltG.appendChild($c(cx, zTop + zD * 0.4, 2.5, 'bolt'));
  boltG.appendChild($c(cx, zBot - zD * 0.2, 2.5, 'bolt'));
  boltG.appendChild($c(cx, zBot - zD * 0.4, 2.5, 'bolt'));
  svg.appendChild(boltG);
  svg.appendChild($t(cx + 12, zTop + zD * 0.3, '15/16" HOLES (TYP)', 'note'));

  // Profile dimensions
  dimV(svg, cx + zTF + 15, zTop, zBot, 20, p.depth + '"');
  dimH(svg, cx, cx + zTF, zTop - 5, -16, sp.topFlange + '"');
  dimH(svg, cx - zBF, cx, zBot + 5, 16, sp.botFlange + '"');
  svg.appendChild($t(topLipX2 + 5, topLipY2 - 3, sp.lip + '"', 'note'));
  svg.appendChild($t(botLipX2 - 25, botLipY2 + 12, sp.lip + '"', 'note'));

  // Gauge callout (left side)
  svg.appendChild($t(cx - zBF - 40, cy, p.gauge, 'lblb', 'middle'));
  svg.appendChild($t(cx - zBF - 40, cy + 10, '(' + fmtDec(p.thick, 3) + '")', 'note', 'middle'));

  // Material callout (right side)
  svg.appendChild($t(cx + zTF + 40, cy + 20, 'MATERIAL:', 'noteb'));
  svg.appendChild($t(cx + zTF + 40, cy + 30, 'G90 GALVANIZED', 'note'));
  svg.appendChild($t(cx + zTF + 40, cy + 40, 'STEEL', 'note'));

  // Solar holes on top flange (if enabled)
  if (p.solar) {
    var solarG = $g('hover-part', 'solar-holes');
    // Show holes along top flange in cross-section
    var hx1 = cx + zTF * 0.4;
    var hx2 = cx + zTF * 0.6;
    solarG.appendChild($c(hx1, zTop + zT/2, 1.8, 'bolt'));
    solarG.appendChild($c(hx2, zTop + zT/2, 1.8, 'bolt'));
    svg.appendChild(solarG);
    svg.appendChild($t(cx + zTF + 5, zTop - 10, 'SOLAR HOLES', 'warn-text'));
    svg.appendChild($t(cx + zTF + 5, zTop - 3, '7/16" DIA (TYP)', 'note'));
  }

  svg.appendChild($t(200, zBot + lip45 + 30, 'SCALE: 1" = ' + fmtDec(1/zScale * 12, 1) + '"', 'note', 'middle'));

  // ================================================================
  // ZONE 2: ELEVATION VIEW — RIGHT SIDE (x=420..1060, y=30..280)
  // ================================================================
  svg.appendChild($t(730, 22, 'ELEVATION VIEW', 'ttl'));

  var evL = 440, evR = 1040;
  var evY = 65;
  var rafW = 20;
  var evSpan = evR - evL - 2 * rafW;
  var sc = evSpan / p.spanIn;
  var purlinH = p.depth * sc;
  if (purlinH < 16) purlinH = 16;
  var scaleFactor = purlinH / p.depth;

  // Left rafter
  var lgR = $g('hover-part', 'rafter-L');
  lgR.appendChild($r(evL, evY - 10, rafW, purlinH + 20, 'gus'));
  lgR.appendChild($t(evL + rafW/2, evY + purlinH + 22, 'RAFTER', 'note', 'middle'));
  svg.appendChild(lgR);

  // Right rafter
  var rgR = $g('hover-part', 'rafter-R');
  rgR.appendChild($r(evR - rafW, evY - 10, rafW, purlinH + 20, 'gus'));
  rgR.appendChild($t(evR - rafW/2, evY + purlinH + 22, 'RAFTER', 'note', 'middle'));
  svg.appendChild(rgR);

  // Purlin body
  var pL = evL + rafW;
  var pR = evR - rafW;
  var flangeW = sp.topFlange * scaleFactor;
  if (flangeW < 6) flangeW = 6;
  var purG = $g('hover-part', 'purlin');
  purG.appendChild($r(pL, evY, pR - pL, purlinH, 'cee'));
  // Top flange hint
  purG.appendChild($r(pL - flangeW + 2, evY - 2, flangeW + (pR - pL) * 0.02, 2, 'cee'));
  // Bottom flange hint
  purG.appendChild($r(pR - (pR - pL) * 0.02, evY + purlinH, flangeW + (pR - pL) * 0.02, 2, 'cee'));
  // Centerline
  purG.appendChild($l((pL + pR)/2, evY - 15, (pL + pR)/2, evY + purlinH + 15, 'center'));
  svg.appendChild(purG);

  // P1 clips
  var clipG = $g('hover-part', 'p1-clips');
  var clipH = 10, clipW = 6;
  clipG.appendChild($r(pL - 2, evY - 1, clipW, clipH, 'clip-fill'));
  clipG.appendChild($c(pL + 2, evY + 3, 1.2, 'bolt'));
  clipG.appendChild($c(pL + 2, evY + clipH - 3, 1.2, 'bolt'));
  clipG.appendChild($r(pR - clipW + 2, evY - 1, clipW, clipH, 'clip-fill'));
  clipG.appendChild($c(pR - 2, evY + 3, 1.2, 'bolt'));
  clipG.appendChild($c(pR - 2, evY + clipH - 3, 1.2, 'bolt'));
  svg.appendChild(clipG);
  svg.appendChild($t(pL + 2, evY - 8, 'P1 CLIP (TYP)', 'noteb', 'middle'));

  // Solar holes on elevation view
  if (p.solar) {
    var solarEvG = $g('hover-part', 'solar-elev');
    var solSpec = SOLAR_SPEC;
    var startX = pL + solSpec.edgeDist * sc;
    var endX = pR - solSpec.edgeDist * sc;
    var solSpacing = solSpec.holeSpacing * sc;
    var pairGap = solSpec.holePairGap * sc;
    var holR = Math.max(1, solSpec.holeDia * sc / 2);

    for (var sx = startX; sx <= endX; sx += solSpacing) {
      solarEvG.appendChild($c(sx - pairGap/2, evY - 1, holR, 'bolt'));
      solarEvG.appendChild($c(sx + pairGap/2, evY - 1, holR, 'bolt'));
      // Small tick marks
      solarEvG.appendChild($l(sx, evY - 4, sx, evY + 2, 'cut-line'));
    }
    svg.appendChild(solarEvG);
    // Solar dimension callout
    if (solSpacing > 20) {
      dimH(svg, startX, startX + solSpacing, evY - 6, -12, solSpec.holeSpacing + '" O.C.');
    }
    svg.appendChild($t(pL + (pR - pL) * 0.5, evY - 18, 'SOLAR ATTACHMENT HOLES - 7/16" DIA @ ' + solSpec.holeSpacing + '" O.C.', 'warn-text', 'middle'));
  }

  // Span dimension
  dimH(svg, pL, pR, evY + purlinH + 6, 18, fmtFtIn(p.spanIn));

  // Section cut A-A indicator
  var secX = (pL + pR) / 2;
  svg.appendChild($l(secX - 6, evY - 20, secX - 6, evY + purlinH + 20, 'cut-line'));
  svg.appendChild($l(secX + 6, evY - 20, secX + 6, evY + purlinH + 20, 'cut-line'));
  svg.appendChild($t(secX - 6, evY - 23, 'A', 'lblb', 'middle'));
  svg.appendChild($t(secX + 6, evY - 23, 'A', 'lblb', 'middle'));

  var elevScale = fmtScale(sc);
  svg.appendChild($t(730, evY + purlinH + 42, 'SCALE: ' + elevScale, 'note', 'middle'));

  // ================================================================
  // ZONE 3: PURLIN SCHEDULE TABLE (y=310..470)
  // ================================================================
  svg.appendChild($t(300, 310, 'PURLIN SCHEDULE', 'ttl'));

  var groups = getGroups();
  var tblX = 40, tblY = 322, tblW = 620;
  var tCols = [0, 80, 115, 250, 360, 440, 530];
  var tHdrs = ['MARK', 'QTY', 'DESCRIPTION', 'SIZE', 'GAUGE', 'WT/PC (LBS)', 'TOTAL (LBS)'];

  // Header row
  svg.appendChild($e('rect', {x: tblX, y: tblY, width: tblW, height: 14, fill: '#333', stroke: '#333'}));
  tHdrs.forEach(function(h, i) {
    var ht = $t(tblX + tCols[i] + 4, tblY + 11, h, 'note');
    ht.setAttribute('fill', '#FFF');
    svg.appendChild(ht);
  });

  var totalWt = 0;
  groups.forEach(function(g, i) {
    var ry = tblY + 14 + i * 14;
    svg.appendChild($l(tblX, ry + 14, tblX + tblW, ry + 14, 'dim'));

    var wtPc = g.lbs_per_ft * (g.span_ft || 25);
    var wtTot = wtPc * (g.qty || 1);
    totalWt += wtTot;

    var desc = 'Z-PURLIN ' + g.depth + '"x' + (g.topFlange || 3.5) + '"';
    var sizeStr = fmtFtIn((g.span_ft || 25) * 12) + ' LG';

    var rowBg = (i === activeGroupIdx) ? '#FFFDE7' : 'transparent';
    if (i === activeGroupIdx) {
      svg.appendChild($e('rect', {x: tblX + 1, y: ry + 1, width: tblW - 2, height: 13, fill: rowBg, stroke: 'none'}));
    }

    var vals = [g.mark || '', String(g.qty || 0), desc, sizeStr, g.gauge || '12GA', fmtDec(wtPc), fmtDec(wtTot)];
    vals.forEach(function(v, ci) {
      svg.appendChild($t(tblX + tCols[ci] + 4, ry + 11, v, i === activeGroupIdx ? 'lblb' : 'lbl'));
    });
  });

  // Total row
  var totY = tblY + 14 + groups.length * 14;
  svg.appendChild($l(tblX, totY, tblX + tblW, totY, 'obj med'));
  svg.appendChild($t(tblX + tCols[5] + 4, totY + 12, 'TOTAL:', 'lblb'));
  svg.appendChild($t(tblX + tCols[6] + 4, totY + 12, fmtDec(totalWt) + ' LBS', 'lblb'));

  var tblH = 14 + (groups.length + 1) * 14 + 4;
  svg.appendChild($r(tblX, tblY, tblW, tblH, 'obj med'));

  // ================================================================
  // ZONE 3b: SPECS & NOTES (right side, y=310..470)
  // ================================================================
  var infoX = 700;
  svg.appendChild($t(infoX + 100, 310, 'SPECIFICATIONS', 'ttl'));

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
    var iy = 325 + i * 13;
    svg.appendChild($t(infoX + 12, iy, pair[0], 'note'));
    svg.appendChild($t(infoX + 80, iy, String(pair[1]), 'lbl'));
  });

  // ================================================================
  // ZONE 4: SOLAR HOLE DETAIL (y=500..660) — shown only when solar enabled
  // ================================================================
  if (p.solar) {
    svg.appendChild($t(300, 500, 'SOLAR HOLE PUNCH DETAIL', 'ttl'));

    var solX = 80, solY = 530;
    var solG = $g('hover-part', 'solar-detail');

    // Show a section of top flange with holes
    var flangeLen = 300;
    solG.appendChild($r(solX, solY, flangeLen, 10, 'cee'));
    svg.appendChild($t(solX + flangeLen/2, solY - 5, 'TOP FLANGE (PLAN VIEW)', 'note', 'middle'));

    // Draw hole pairs
    var numPairs = 5;
    var pairSpacing = flangeLen / (numPairs + 1);
    for (var hi = 1; hi <= numPairs; hi++) {
      var hcx = solX + hi * pairSpacing;
      solG.appendChild($c(hcx - 4, solY + 5, 3, 'bolt'));
      solG.appendChild($c(hcx + 4, solY + 5, 3, 'bolt'));
    }
    svg.appendChild(solG);

    // Dimensions
    dimH(svg, solX + pairSpacing - 4, solX + pairSpacing + 4, solY + 12, 12, SOLAR_SPEC.holePairGap + '"');
    dimH(svg, solX + pairSpacing, solX + 2*pairSpacing, solY + 12, 24, SOLAR_SPEC.holeSpacing + '" O.C.');
    dimH(svg, solX, solX + pairSpacing, solY + 12, 36, SOLAR_SPEC.edgeDist + '" EDGE');

    // Hole schedule
    var solNotes = [
      'HOLE DIAMETER: 7/16" (0.4375")',
      'HOLES PER ATTACHMENT: 2',
      'HOLE PAIR SPACING: ' + SOLAR_SPEC.holePairGap + '" CENTER-TO-CENTER',
      'ATTACHMENT SPACING: ' + SOLAR_SPEC.holeSpacing + '" O.C.',
      'EDGE DISTANCE: ' + SOLAR_SPEC.edgeDist + '" MIN FROM PURLIN END',
      'LOCATION: TOP FLANGE ONLY',
      'PUNCHED BEFORE ROLL FORMING'
    ];
    solNotes.forEach(function(n, i) {
      svg.appendChild($t(solX + flangeLen + 40, solY - 5 + i * 10, n, 'note'));
    });
  } else {
    // Standard notes area
    svg.appendChild($t(300, 500, 'FABRICATION NOTES', 'ttl'));
    var fnotes = [
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
    fnotes.forEach(function(n, i) {
      svg.appendChild($t(60, 518 + i * 11, n, 'note'));
    });
  }

  // ================================================================
  // ZONE 5: TITLE BLOCK (y=680..815)
  // ================================================================
  var buildingId = (window.PURLIN_CONFIG && window.PURLIN_CONFIG.building_id) || '';
  var titleSuffix = buildingId ? ' - ' + buildingId : '';
  drawTitleBlock(svg, {
    projName: projName,
    customer: customer,
    jobNum: jobNum,
    drawingNum: drawingNum,
    drawnBy: drawnBy,
    surfPrep: surfPrep,
    drawingTitle: 'PURLIN' + titleSuffix,
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
      p.solar ? 'SOLAR: HOLES PER SPEC (7/16" DIA)' : '',
      'FAB: AISC 360-22 / AWS D1.1',
      'DO NOT SCALE DRAWING',
      'TOL: LENGTH +/-1/16" / HOLES +/-1/32"'
    ].filter(Boolean)
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
  if (fWt) fWt.textContent = fmtDec(totalWt) + ' lbs';

  // ── Update BOM side panel ──
  var bomRows = [];
  groups.forEach(function(g) {
    var wtPc = g.lbs_per_ft * (g.span_ft || 25);
    bomRows.push({
      mk: g.mark, qty: g.qty,
      desc: 'Z-Purlin ' + g.depth + '"',
      size: fmtFtIn((g.span_ft || 25) * 12) + ' x ' + (g.gauge || '12GA'),
      mat: 'G90', wt: Math.round(wtPc * g.qty)
    });
  });
  updateBOM(bomRows);
}

// ── Solar toggle handler ──
function toggleSolar() {
  solarEnabled = !solarEnabled;
  var btn = document.getElementById('btnSolar');
  if (btn) {
    btn.classList.toggle('active', solarEnabled);
    btn.textContent = solarEnabled ? 'Solar: ON' : 'Solar: OFF';
  }
  draw();
}
"""

# ===================================================================
# Controls HTML
# ===================================================================

PURLIN_V2_CONTROLS = """
    <div id="groupTabBar" style="display:flex;gap:6px;flex-wrap:wrap;"></div>
    <button class="toggle-btn" id="btnSolar" onclick="toggleSolar()">Solar: OFF</button>
    <button class="toggle-btn" onclick="window.print()">Print</button>
"""

# ===================================================================
# Footer HTML
# ===================================================================

PURLIN_V2_FOOTER = """
  <div>Span: <span class="s" id="fSpan">--</span></div>
  <div>Depth: <span class="s" id="fDepth">--</span></div>
  <div>Gauge: <span class="s" id="fGauge">--</span></div>
  <div>Spacing: <span class="s" id="fSpacing">--</span></div>
  <div>Qty/Bay: <span class="s" id="fQty">--</span></div>
  <div>Total Wt: <span class="s" id="fWt">--</span></div>
"""

# ===================================================================
# Assemble final HTML via drawing_base
# ===================================================================

PURLIN_DRAWING_V2_HTML = drawing_base.build_html_shell(
    title="Purlin Shop Drawing",
    drawing_type="purlin",
    config_var="PURLIN_CONFIG",
    controls_html=PURLIN_V2_CONTROLS,
    footer_html=PURLIN_V2_FOOTER,
    drawing_js=PURLIN_V2_JS,
)
