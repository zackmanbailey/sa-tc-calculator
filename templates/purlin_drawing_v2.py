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

// ── Solar panel mount specs (real values from panel datasheet) ──
// Panel bolts through top flange at mount_hole_from_edge_mm (20mm) from
// each panel edge.  mount_hole_inset_mm (250mm) from short edges sets
// the purlin Y positions in portrait mode.
// In this cross-section / elevation view we just show the bolt holes on
// the top flange at the positions where panels attach.
var SOLAR_SPEC = {
  holeDia: 0.34375,        // 11/32" clearance for M8 bolt (8mm + 0.7mm)
  mountHoleFromEdgeMm: 20  // mm from panel long-edge to bolt center
};

// ── State ──
var activeGroupIdx = 0;
var solarEnabled = false;
var angledPurlins = false;
var purlinAngleDeg = 90;  // 90 = perpendicular to rafter (standard)

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
  // Angled purlin settings from server config
  if (cfg.angled_purlins) {
    angledPurlins = true;
    var btn = document.getElementById('btnAngled');
    if (btn) { btn.classList.add('active'); btn.textContent = 'Angled: ON'; }
  }
  if (cfg.purlin_angle_deg) {
    purlinAngleDeg = cfg.purlin_angle_deg;
  }
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

  // Angled purlin adjustment: actual cut length = span / cos(angle from perpendicular)
  // purlinAngleDeg is angle from the drive aisle. 90 = perpendicular (standard).
  // Deviation from perpendicular = 90 - purlinAngleDeg
  var angleFromPerp = angledPurlins ? (90 - purlinAngleDeg) : 0;
  var cosAngle = Math.cos(angleFromPerp * Math.PI / 180);
  var angledCutLen = angledPurlins ? (cutLen / cosAngle) : cutLen;
  var angledWtPiece = lbsLft * (angledCutLen / 12);

  // End plate type: P6 for angled, P2 for standard
  var endPlateType = angledPurlins ? 'P6' : 'P2';
  var endPlateSize = angledPurlins ? '9"x15"' : '9"x24"';

  // Splice data from server (calc_purlin_groups)
  var needsSplice = g.needs_splice || false;
  var splicePositionFt = g.splice_position_ft || 0;
  var spliceOverlapIn = g.splice_overlap_in || 6;
  var spliceTekScrews = g.splice_tek_screws || 8;

  // Facing direction: right (first/eave-right), left (last/eave-left), alternating (middle)
  var facing = g.facing || 'alternating';
  var isFirst = g.is_first || false;
  var isLast = g.is_last || false;

  return {
    depth: depth, gauge: gauge, thick: thick, spanFt: spanFt, spanIn: spanIn,
    spacingFt: spacingFt, spacingIn: spacingIn, qty: qty,
    spec: { topFlange: g.topFlange || spec.topFlange, botFlange: g.botFlange || spec.botFlange,
            lip: g.lip || spec.lip, coilWidth: g.coilWidth || spec.coilWidth },
    lbsLft: lbsLft, cutLen: angledCutLen, wtPiece: angledWtPiece, mark: mark,
    groupType: groupType, material: 'G90', coating: 'G90',
    solar: solarEnabled,
    angled: angledPurlins,
    angleDeg: purlinAngleDeg,
    angleFromPerp: angleFromPerp,
    endPlateType: endPlateType,
    endPlateSize: endPlateSize,
    needsSplice: needsSplice,
    splicePositionFt: splicePositionFt,
    spliceOverlapIn: spliceOverlapIn,
    spliceTekScrews: spliceTekScrews,
    facing: facing,
    isFirst: isFirst,
    isLast: isLast
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

  // Lips — angled stiffeners at flange ends
  // Top lip: at right end of top flange, angles DOWN-RIGHT
  // Bottom lip: at left end of bottom flange, angles UP-LEFT
  var lipLen = zLip;
  var lip45 = lipLen * Math.cos(Math.PI/4);
  var lipNx = zT * Math.cos(Math.PI/4) / 2;
  var lipNy = zT * Math.sin(Math.PI/4) / 2;

  // Top lip: from right end of top flange, angles DOWN and RIGHT
  var topLipX1 = cx + zTF;
  var topLipY1 = zTop;
  var topLipX2 = topLipX1 + lip45;
  var topLipY2 = topLipY1 + lip45;
  var topLipPts = [
    (topLipX1 - lipNy) + ',' + (topLipY1 + lipNx),
    (topLipX2 - lipNy) + ',' + (topLipY2 + lipNx),
    (topLipX2 + lipNy) + ',' + (topLipY2 - lipNx),
    (topLipX1 + lipNy) + ',' + (topLipY1 - lipNx)
  ].join(' ');
  secG.appendChild($e('polygon', {points: topLipPts, class: 'cee'}));

  // Bottom lip: from left end of bottom flange, angles UP and LEFT
  var botLipX1 = cx - zBF;
  var botLipY1 = zBot;
  var botLipX2 = botLipX1 - lip45;
  var botLipY2 = botLipY1 - lip45;
  // Normal perpendicular to UP-LEFT direction (-1,-1) is (+1,-1) and (-1,+1)
  var botLipPts = [
    (botLipX1 + lipNy) + ',' + (botLipY1 - lipNx),
    (botLipX2 + lipNy) + ',' + (botLipY2 - lipNx),
    (botLipX2 - lipNy) + ',' + (botLipY2 + lipNx),
    (botLipX1 - lipNy) + ',' + (botLipY1 + lipNx)
  ].join(' ');
  secG.appendChild($e('polygon', {points: botLipPts, class: 'cee'}));

  // Centerlines
  secG.appendChild($l(cx, zTop - 15, cx, zBot + 15, 'center'));
  secG.appendChild($l(cx - zBF - 20, cy, cx + zTF + 20, cy, 'center'));
  svg.appendChild(secG);

  // ── Part labels ──
  // Web label (left side of web)
  svg.appendChild($t(cx - 18, cy + 3, 'WEB', 'lblb', 'middle'));
  // Top flange label (above top flange)
  svg.appendChild($t(cx + zTF/2, zTop - 8, 'TOP FLANGE', 'lblb', 'middle'));
  // Bottom flange label (below bottom flange)
  svg.appendChild($t(cx - zBF/2, zBot + 14, 'BOTTOM FLANGE', 'lblb', 'middle'));
  // Top lip label (down-right from top flange end)
  svg.appendChild($t(topLipX2 + 5, topLipY2 + 3, 'LIP', 'noteb'));
  // Bottom lip label (up-left from bottom flange end)
  svg.appendChild($t(botLipX2 - 18, botLipY2 + 3, 'LIP', 'noteb'));

  // Profile dimensions
  dimV(svg, cx + zTF + 15, zTop, zBot, 30, p.depth + '"');
  dimH(svg, cx, cx + zTF, zTop - 5, -20, sp.topFlange + '"');
  dimH(svg, cx - zBF, cx, zBot + 5, 20, sp.botFlange + '"');
  // Lip dimension labels (top lip DOWN, bottom lip UP)
  dimV(svg, topLipX2 + 3, topLipY1, topLipY2, 10, sp.lip + '"');
  dimV(svg, botLipX2 - 3, botLipY2, botLipY1, -10, sp.lip + '"');

  // Gauge callout (left side)
  svg.appendChild($t(cx - zBF - 45, cy, p.gauge, 'lblb', 'middle'));
  svg.appendChild($t(cx - zBF - 45, cy + 10, '(' + fmtDec(p.thick, 3) + '")', 'note', 'middle'));

  // Material callout (right side)
  svg.appendChild($t(cx + zTF + 50, cy + 20, 'MATERIAL:', 'noteb'));
  svg.appendChild($t(cx + zTF + 50, cy + 30, 'G90 GALVANIZED', 'note'));
  svg.appendChild($t(cx + zTF + 50, cy + 40, 'STEEL', 'note'));

  // Solar holes on top flange (if enabled)
  if (p.solar) {
    var solarG = $g('hover-part', 'solar-holes');
    // Show holes along top flange in cross-section
    var hx1 = cx + zTF * 0.4;
    var hx2 = cx + zTF * 0.6;
    solarG.appendChild($c(hx1, zTop + zT/2, 1.8, 'bolt'));
    solarG.appendChild($c(hx2, zTop + zT/2, 1.8, 'bolt'));
    svg.appendChild(solarG);
    svg.appendChild($t(cx + zTF + 5, zTop - 10, 'SOLAR MOUNT HOLES', 'warn-text'));
    svg.appendChild($t(cx + zTF + 5, zTop - 3, '11/32" DIA (M8 CLR)', 'note'));
  }

  svg.appendChild($t(200, zBot + lipLen + 30, 'SCALE: 1" = ' + fmtDec(1/zScale * 12, 1) + '"', 'note', 'middle'));

  // ================================================================
  // ZONE 2: ELEVATION VIEW — RIGHT SIDE (x=420..1060, y=30..280)
  // ================================================================
  var evTitle = p.angled ? 'ELEVATION VIEW (' + p.angleDeg + '\u00B0 FROM AISLE)' : 'ELEVATION VIEW';
  svg.appendChild($t(730, 22, evTitle, 'ttl'));

  // Elevation view: just the purlin — its length, flanges, depth. No rafters,
  // no clips, no screws, no connection hardware. This is a purlin shop drawing.
  var evL = 440, evR = 1040;
  var evY = 80;
  var evSpan = evR - evL;
  var sc = evSpan / p.spanIn;
  var purlinH = p.depth * sc;
  if (purlinH < 16) purlinH = 16;
  var scaleFactor = purlinH / p.depth;

  var pL = evL;
  var pR = evR;
  var purG = $g('hover-part', 'purlin');

  // Purlin web (main body)
  purG.appendChild($r(pL, evY, pR - pL, purlinH, 'cee'));
  // Top flange — full length
  purG.appendChild($r(pL, evY - 3, pR - pL, 3, 'cee'));
  // Bottom flange — full length
  purG.appendChild($r(pL, evY + purlinH, pR - pL, 3, 'cee'));
  // Centerline
  purG.appendChild($l((pL + pR)/2, evY - 15, (pL + pR)/2, evY + purlinH + 15, 'center'));
  svg.appendChild(purG);

  // Depth dimension (right side)
  dimV(svg, pR + 5, evY, evY + purlinH, 15, p.depth + '"');

  // Length dimension (below)
  dimH(svg, pL, pR, evY + purlinH + 8, 18, fmtFtIn(p.spanIn));

  // Mark label centered on purlin
  svg.appendChild($t((pL + pR)/2, evY + purlinH/2 + 3, p.mark, 'lblb', 'middle'));

  // Splice zone callout (if applicable — still relevant to the purlin itself)
  if (p.needsSplice && p.splicePositionFt > 0) {
    var splG = $g('hover-part', 'splice-zone');
    var splPosIn = p.splicePositionFt * 12;
    var splOverlapPx = p.spliceOverlapIn * sc;
    var splX = pL + splPosIn * sc;

    // Splice zone highlight band
    splG.appendChild($e('rect', {
      x: splX - splOverlapPx/2, y: evY - 4,
      width: splOverlapPx, height: purlinH + 8,
      fill: '#FF6B35', 'fill-opacity': '0.25',
      stroke: '#FF6B35', 'stroke-width': '1.2',
      'stroke-dasharray': '4,2'
    }));
    splG.appendChild($l(splX, evY - 12, splX, evY + purlinH + 12, 'cut-line'));
    svg.appendChild(splG);

    // Splice dimension
    dimH(svg, pL, splX, evY + purlinH + 30, 14,
      fmtFtIn(splPosIn) + ' TO SPLICE');

    svg.appendChild($t(splX, evY - 16,
      'SPLICE: ' + p.spliceOverlapIn + '" OVERLAP',
      'warn-text', 'middle'));
  }

  var elevScale = fmtScale(sc);
  svg.appendChild($t(730, evY + purlinH + 50, 'SCALE: ' + elevScale, 'note', 'middle'));

  // ================================================================
  // ZONE 3: PURLIN SCHEDULE TABLE (y=310..470)
  // ================================================================
  svg.appendChild($t(300, 310, 'PURLIN SCHEDULE', 'ttl'));

  var groups = getGroups();
  var tblX = 40, tblY = 322, tblW = 620;
  var tCols = [0, 80, 115, 250, 360, 440, 530];
  var tHdrs = ['MARK', 'QTY', 'DESCRIPTION', 'SIZE', 'GAUGE', 'WT/PC (LBS)', 'TOTAL (LBS)'];

  // Header row
  svg.appendChild($e('rect', {x: tblX, y: tblY, width: tblW, height: 14, fill: '#1E3A5F', stroke: '#1E3A5F'}));
  tHdrs.forEach(function(h, i) {
    var ht = $t(tblX + tCols[i] + 4, tblY + 11, h, 'note');
    ht.style.fill = '#FF0000';
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
  if (p.angled) {
    infoLines.push(['ANGLE:', p.angleDeg + '\u00B0 from aisle']);
    infoLines.push(['CUT LEN:', fmtFtIn(p.cutLen)]);
    infoLines.push(['END PLATE:', p.endPlateType + ' (' + p.endPlateSize + ')']);
  }
  if (p.needsSplice) {
    infoLines.push(['SPLICE:', 'YES @ ' + fmtFtIn(p.splicePositionFt * 12)]);
    infoLines.push(['OVERLAP:', p.spliceOverlapIn + '" w/ (' + p.spliceTekScrews + ') TEK']);
  }
  if (p.facing && !p.angled) {
    var facLabel = p.facing === 'right' ? 'Top flange RIGHT (eave)' :
                   p.facing === 'left' ? 'Top flange LEFT (eave)' : 'Alternating (interior)';
    infoLines.push(['FACING:', facLabel]);
  }
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

    // Draw single bolt holes at panel mount positions along top flange
    // Real panels bolt through top flange — one bolt per panel rail attach point
    var numHoles = 6;
    var holeSpacing = flangeLen / (numHoles + 1);
    for (var hi = 1; hi <= numHoles; hi++) {
      var hcx = solX + hi * holeSpacing;
      solG.appendChild($c(hcx, solY + 5, 3, 'bolt'));
    }
    svg.appendChild(solG);

    // Dimensions
    dimH(svg, solX + holeSpacing, solX + 2*holeSpacing, solY + 12, 16,
      'VARIES BY PANEL LAYOUT');
    dimH(svg, solX, solX + holeSpacing, solY + 12, 30,
      fmtDec(SOLAR_SPEC.mountHoleFromEdgeMm / 25.4, 2) + '" (~' + SOLAR_SPEC.mountHoleFromEdgeMm + 'mm) FROM PANEL EDGE');

    // Hole schedule
    var solNotes = [
      'HOLE DIAMETER: 11/32" (0.344") — M8 BOLT CLEARANCE',
      'HOLES: 1 PER PANEL MOUNT RAIL ATTACH POINT',
      'HOLE POSITION: SET BY PANEL mount_hole_from_edge_mm (' + SOLAR_SPEC.mountHoleFromEdgeMm + 'mm)',
      'LOCATION: TOP FLANGE ONLY',
      'PANEL BOLT THROUGH TOP FLANGE INTO MOUNT RAIL',
      'HOLE SPACING VARIES BY PANEL ORIENTATION & COUNT',
      'SEE SOLAR LAYOUT DRAWING FOR EXACT POSITIONS'
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
      '3. P1 CLIP: FLAT PLATE WELDED TO RAFTER TOP (1/8" FILLET)',
      '4. PURLIN WEB TEK-SCREWED TO P1 CLIP AT EACH RAFTER',
      '5. (2) #10 TEK SCREWS THROUGH PURLIN WEB INTO P1 PLATE PER CONNECTION',
      '6. SAG RODS AT MID-SPAN FOR LATERAL BRACING',
      '7. Z-PURLIN SPLICE: 6" OVERLAP, BOXED BEAM',
      '8. SPLICE FASTENED WITH (8) #10 TEK SCREWS PER SIDE',
      '9. SPACING: ' + fmtFtIn(p.spacingIn) + ' O.C.',
      '10. DO NOT SCALE DRAWING',
      '11. TOL: LENGTH +/-1/16"',
      '12. TOL: LENGTH +/-1/16", HOLES +/-1/32"'
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
      'FASTENERS: #10 TEK SCREWS (FIELD)',
      'P1 CLIP: FLAT PLATE WELDED TO RAFTER TOP (WPS-C)',
      'SAG RODS: CONTINUOUS, ANGLE-BRACKET ATTACH',
      'Z-SPLICE: 6" OVERLAP, BOXED BEAM, (8) TEK/SIDE',
      p.needsSplice ? 'SPLICE AT ' + fmtFtIn(p.splicePositionFt * 12) + ' FROM END' : '',
      'SPACING: ' + fmtFtIn(p.spacingIn) + ' O.C.',
      p.solar ? 'SOLAR: M8 BOLT HOLES ON TOP FLANGE (11/32" DIA)' : '',
      p.angled ? 'ANGLED PURLINS: ' + p.angleDeg + '\u00B0 FROM AISLE' : '',
      p.angled ? 'END PLATES: ' + p.endPlateType + ' (' + p.endPlateSize + ' 10GA)' : '',
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
    var spanIn = (g.span_ft || 25) * 12;
    var cutLenIn = spanIn;
    if (p.angled && p.angleFromPerp > 0) {
      cutLenIn = spanIn / Math.cos(p.angleFromPerp * Math.PI / 180);
    }
    var wtPc = g.lbs_per_ft * (cutLenIn / 12);
    bomRows.push({
      mk: g.mark, qty: g.qty,
      desc: 'Z-Purlin ' + g.depth + '"' + (p.angled ? ' (ANGLED)' : ''),
      size: fmtFtIn(cutLenIn) + ' x ' + (g.gauge || '12GA'),
      mat: 'G90', wt: Math.round(wtPc * g.qty)
    });
  });
  // Add P6 end plates to BOM when angled
  if (p.angled) {
    var p6Qty = p.qty * 2;  // 2 per purlin line (one each end)
    var p6Wt = 9 * 15 * 0.135 * 0.2836;  // 10GA steel
    bomRows.push({
      mk: 'P6', qty: p6Qty,
      desc: 'End Plate (Angled)',
      size: p.endPlateSize + ' x 10GA',
      mat: 'G90', wt: Math.round(p6Wt * p6Qty)
    });
  }
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

// ── Angled purlin toggle handler ──
function toggleAngled() {
  angledPurlins = !angledPurlins;
  var btn = document.getElementById('btnAngled');
  if (btn) {
    btn.classList.toggle('active', angledPurlins);
    btn.textContent = angledPurlins ? 'Angled: ON' : 'Angled: OFF';
  }
  var angleInput = document.getElementById('angledAngleInput');
  if (angleInput) angleInput.style.display = angledPurlins ? 'inline-flex' : 'none';
  draw();
}

function onAngleChange() {
  var el = document.getElementById('inpPurlinAngle');
  if (el) purlinAngleDeg = parseFloat(el.value) || 15;
  draw();
}
"""

# ===================================================================
# Controls HTML
# ===================================================================

PURLIN_V2_CONTROLS = """
    <div id="groupTabBar" style="display:flex;gap:6px;flex-wrap:wrap;"></div>
    <button class="toggle-btn" id="btnSolar" onclick="toggleSolar()">Solar: OFF</button>
    <button class="toggle-btn" id="btnAngled" onclick="toggleAngled()">Angled: OFF</button>
    <span id="angledAngleInput" style="display:none;align-items:center;gap:4px;">
      <label style="font-size:11px;">Angle(&deg;):</label>
      <input type="number" id="inpPurlinAngle" value="15" min="5" max="45" step="0.5"
        style="width:55px;" onchange="onAngleChange()">
    </span>
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
