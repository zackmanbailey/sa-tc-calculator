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
  var evTitle = p.angled ? 'ELEVATION VIEW (' + p.angleDeg + '\u00B0 FROM AISLE)' : 'ELEVATION VIEW';
  svg.appendChild($t(730, 22, evTitle, 'ttl'));

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

  if (p.angled && p.angleFromPerp > 0) {
    // Draw angled purlin: rotate the purlin rectangle around its center
    var purlinCX = (pL + pR) / 2;
    var purlinCY = evY + purlinH / 2;
    var rotG = $e('g', {transform: 'rotate(' + (-p.angleFromPerp) + ' ' + purlinCX + ' ' + purlinCY + ')'});
    rotG.appendChild($r(pL, evY, pR - pL, purlinH, 'cee'));
    // Top flange hint
    rotG.appendChild($r(pL - flangeW + 2, evY - 2, flangeW + (pR - pL) * 0.02, 2, 'cee'));
    // Bottom flange hint
    rotG.appendChild($r(pR - (pR - pL) * 0.02, evY + purlinH, flangeW + (pR - pL) * 0.02, 2, 'cee'));
    // Centerline
    rotG.appendChild($l(purlinCX, evY - 15, purlinCX, evY + purlinH + 15, 'center'));
    purG.appendChild(rotG);

    // Angle indicator arc: show deviation from perpendicular
    var arcR = 30;
    var arcCX = pL + 15;
    var arcCY = evY + purlinH / 2;
    // Reference line (perpendicular = horizontal)
    purG.appendChild($l(arcCX, arcCY, arcCX + arcR + 10, arcCY, 'center'));
    // Arc from 0 to -angleFromPerp
    var startAngleRad = 0;
    var endAngleRad = -p.angleFromPerp * Math.PI / 180;
    var arcX1 = arcCX + arcR * Math.cos(startAngleRad);
    var arcY1 = arcCY + arcR * Math.sin(startAngleRad);
    var arcX2 = arcCX + arcR * Math.cos(endAngleRad);
    var arcY2 = arcCY + arcR * Math.sin(endAngleRad);
    var largeArc = (Math.abs(p.angleFromPerp) > 180) ? 1 : 0;
    var sweep = (p.angleFromPerp > 0) ? 0 : 1;
    var arcPath = 'M' + arcX1 + ' ' + arcY1 + ' A' + arcR + ' ' + arcR + ' 0 ' + largeArc + ' ' + sweep + ' ' + arcX2 + ' ' + arcY2;
    var arcEl = $e('path', {d: arcPath, fill: 'none', stroke: '#E03131', 'stroke-width': '1.2'});
    purG.appendChild(arcEl);
    // Angle label
    var labelAngle = -p.angleFromPerp / 2 * Math.PI / 180;
    var labelX = arcCX + (arcR + 12) * Math.cos(labelAngle);
    var labelY = arcCY + (arcR + 12) * Math.sin(labelAngle);
    purG.appendChild($t(labelX, labelY, p.angleFromPerp + '\u00B0 from \u22A5', 'warn-text', 'middle'));
  } else {
    // Standard perpendicular purlin
    purG.appendChild($r(pL, evY, pR - pL, purlinH, 'cee'));
    // Top flange hint
    purG.appendChild($r(pL - flangeW + 2, evY - 2, flangeW + (pR - pL) * 0.02, 2, 'cee'));
    // Bottom flange hint
    purG.appendChild($r(pR - (pR - pL) * 0.02, evY + purlinH, flangeW + (pR - pL) * 0.02, 2, 'cee'));
    // Centerline
    purG.appendChild($l((pL + pR)/2, evY - 15, (pL + pR)/2, evY + purlinH + 15, 'center'));
  }
  svg.appendChild(purG);

  // End plates: P6 (angled) or P1 clips (standard)
  if (p.angled) {
    // P6 end plates at rafter connections
    var plateG = $g('hover-part', 'p6-plates');
    var plateW = 8, plateH = purlinH + 4;
    // Left P6 plate
    plateG.appendChild($e('rect', {
      x: pL - 2, y: evY - 2, width: plateW, height: plateH,
      fill: '#DD8833', 'fill-opacity': '0.4', stroke: '#DD8833', 'stroke-width': '1'
    }));
    // Right P6 plate
    plateG.appendChild($e('rect', {
      x: pR - plateW + 2, y: evY - 2, width: plateW, height: plateH,
      fill: '#DD8833', 'fill-opacity': '0.4', stroke: '#DD8833', 'stroke-width': '1'
    }));
    svg.appendChild(plateG);
    svg.appendChild($t(pL + 4, evY - 8, 'P6 PLATE (TYP)', 'noteb', 'middle'));
    svg.appendChild($t(pL + 4, evY - 2, p.endPlateSize + ' 10GA', 'note', 'middle'));
  } else {
    // P1 clips (standard mode)
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
  }

  // ── Splice zone callout (Z-purlins only) ──
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

    // Splice center line
    splG.appendChild($l(splX, evY - 12, splX, evY + purlinH + 12, 'cut-line'));

    // Tek screw holes at splice (4 on each side of web)
    var screwSpacing = purlinH / 5;
    for (var si = 1; si <= 4; si++) {
      var sy = evY + si * screwSpacing;
      splG.appendChild($c(splX - 2, sy, 1.2, 'bolt'));
      splG.appendChild($c(splX + 2, sy, 1.2, 'bolt'));
    }
    svg.appendChild(splG);

    // Splice dimension callout
    dimH(svg, pL, splX, evY + purlinH + 30, 14,
      fmtFtIn(splPosIn) + ' TO SPLICE');

    // Splice label
    svg.appendChild($t(splX, evY - 16,
      'SPLICE: ' + p.spliceOverlapIn + '" OVERLAP, (' + p.spliceTekScrews + ') #10 TEK',
      'warn-text', 'middle'));
  }

  // ── Facing direction indicators (Z-purlins) ──
  if (!p.angled) {
    var facG = $g('hover-part', 'facing');
    var facY = evY + purlinH + 48;
    var facMid = (pL + pR) / 2;

    if (p.facing === 'right' || p.isFirst) {
      // Top flange points RIGHT — arrow pointing right
      var arrX = facMid - 30;
      facG.appendChild($l(arrX, facY, arrX + 60, facY, 'obj'));
      facG.appendChild($l(arrX + 50, facY - 4, arrX + 60, facY, 'obj'));
      facG.appendChild($l(arrX + 50, facY + 4, arrX + 60, facY, 'obj'));
      svg.appendChild($t(facMid, facY - 7, 'FACING: TOP FLANGE \u2192 (EAVE RIGHT)', 'note', 'middle'));
    } else if (p.facing === 'left' || p.isLast) {
      // Top flange points LEFT — arrow pointing left
      var arrX2 = facMid + 30;
      facG.appendChild($l(arrX2, facY, arrX2 - 60, facY, 'obj'));
      facG.appendChild($l(arrX2 - 50, facY - 4, arrX2 - 60, facY, 'obj'));
      facG.appendChild($l(arrX2 - 50, facY + 4, arrX2 - 60, facY, 'obj'));
      svg.appendChild($t(facMid, facY - 7, 'FACING: TOP FLANGE \u2190 (EAVE LEFT)', 'note', 'middle'));
    } else {
      // Middle purlins: alternating (show double-headed arrow)
      facG.appendChild($l(facMid - 30, facY, facMid + 30, facY, 'obj'));
      facG.appendChild($l(facMid + 20, facY - 4, facMid + 30, facY, 'obj'));
      facG.appendChild($l(facMid + 20, facY + 4, facMid + 30, facY, 'obj'));
      facG.appendChild($l(facMid - 20, facY - 4, facMid - 30, facY, 'obj'));
      facG.appendChild($l(facMid - 20, facY + 4, facMid - 30, facY, 'obj'));
      svg.appendChild($t(facMid, facY - 7, 'FACING: ALTERNATING (INTERIOR)', 'note', 'middle'));
    }
    svg.appendChild(facG);
  }

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
      '7. Z-PURLIN SPLICE: 6" OVERLAP, BOXED BEAM',
      '8. SPLICE FASTENED WITH (8) #10 TEK SCREWS PER SIDE',
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
      'Z-SPLICE: 6" OVERLAP, BOXED BEAM, (8) TEK/SIDE',
      p.needsSplice ? 'SPLICE AT ' + fmtFtIn(p.splicePositionFt * 12) + ' FROM END' : '',
      'SPACING: ' + fmtFtIn(p.spacingIn) + ' O.C.',
      p.solar ? 'SOLAR: HOLES PER SPEC (7/16" DIA)' : '',
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
