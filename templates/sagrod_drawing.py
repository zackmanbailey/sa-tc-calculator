"""
TitanForge -- Interactive Sag Rod (2"x2" Angle) Shop Drawing Template
=====================================================================
Full-featured SVG-based sag rod shop drawing served as an interactive page.
Pre-fills with project data via window.SAGROD_CONFIG injection.
Uses drawing_base.build_html_shell() for consistent dark-theme UI.

Sag Rod specs (from defaults.py / angle_4_16ga coil):
  - 4" coil width, 16GA, G90 galvanised
  - 2"x2" L-angle profile (roll-formed in-house from 4" coil)
  - 0.8656 lbs/lft
  - 4,000 lb rolls, $0.86/lb
  - Max piece length 20'-3"
  - Attached to purlin webs via #10 TEK screws
  - Runs perpendicular to purlins, bracing pairs together
"""

import templates.drawing_base as drawing_base

# ═══════════════════════════════════════════════════════════════════════════════
# Component-specific JavaScript: draw() and helpers
# ═══════════════════════════════════════════════════════════════════════════════

SAGROD_JS = r"""
// ── Sag Rod specs ──
var SAGROD_SPECS = {
  leg_in: 2,
  coil_width_in: 4,
  lbs_per_lft: 0.8656,
  roll_weight_lbs: 4000,
  price_per_lb: 0.86,
  max_piece_in: 243,          // 20'-3"
  material: 'G90 GALVANIZED',
  tek_per_purlin: 2           // (2) #10 TEK per purlin connection
};

var GAUGE_THICK = {
  '16GA': 0.060
};

// ── Apply server config to controls ──
function applyComponentConfig(cfg) {
  if (cfg.gauge) {
    var el = document.getElementById('selGauge');
    if (el) el.value = cfg.gauge;
  }
  if (cfg.length_in) {
    var el = document.getElementById('inpLength');
    if (el) el.value = cfg.length_in;
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
  var gauge = document.getElementById('selGauge').value || '16GA';
  var lengthIn = parseFloat(document.getElementById('inpLength').value) || 60;
  var qty = parseInt(document.getElementById('inpQty').value) || 1;
  var mark = document.getElementById('inpMark').value || 'SR-1';
  var thick = GAUGE_THICK[gauge] || 0.060;
  var lbsLft = SAGROD_SPECS.lbs_per_lft;
  var wtPiece = lbsLft * (lengthIn / 12);
  var totalWt = wtPiece * qty;
  var bundleSize = Math.floor(SAGROD_SPECS.roll_weight_lbs / wtPiece);

  return {
    gauge: gauge, thick: thick, lengthIn: lengthIn, qty: qty,
    mark: mark, lbsLft: lbsLft, wtPiece: wtPiece, totalWt: totalWt,
    bundleSize: bundleSize, leg: SAGROD_SPECS.leg_in,
    coilWidth: SAGROD_SPECS.coil_width_in,
    material: SAGROD_SPECS.material
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
  // ZONE 1: ELEVATION VIEW (y=25 to y=220)
  // Side view of L-shaped angle running between two purlins
  // ════════════════════════════════════════════════════════════════════
  svg.appendChild($t(330, 22, 'ELEVATION VIEW', 'ttl'));

  // Layout constants
  var evL = 60, evR = 650;
  var evY = 80;               // top of angle in elevation
  var purW = 12;              // purlin width in side view
  var purH = 70;              // purlin depth in side view
  var evSpan = evR - evL - 2 * purW;
  var sc = evSpan / p.lengthIn;  // px per inch
  var angH = Math.max(p.leg * sc, 8);   // angle leg height at scale (side view shows one leg)
  var angThk = Math.max(p.thick * sc, 1.5);

  // Left purlin (cross-section rectangle)
  var lpG = $g('hover-part', 'purlin-L');
  lpG.appendChild($r(evL, evY - 10, purW, purH, 'cee'));
  lpG.appendChild($t(evL + purW/2, evY + purH + 8, 'PURLIN', 'note', 'middle'));
  svg.appendChild(lpG);

  // Right purlin
  var rpG = $g('hover-part', 'purlin-R');
  rpG.appendChild($r(evR - purW, evY - 10, purW, purH, 'cee'));
  rpG.appendChild($t(evR - purW/2, evY + purH + 8, 'PURLIN', 'note', 'middle'));
  svg.appendChild(rpG);

  // Sag rod angle body (side view = horizontal rectangle with L-profile hint)
  var aL = evL + purW;
  var aR = evR - purW;
  var aMid = evY + purH / 2 - angH / 2;  // vertically centered on purlin

  var srG = $g('hover-part', 'sagrod');

  // Horizontal leg (main visible body from side)
  srG.appendChild($r(aL, aMid, aR - aL, angH, 'ang-fill'));

  // Vertical leg (L-profile) - shown as a thin strip along the top
  srG.appendChild($r(aL, aMid - angH + angThk, aR - aL, angH, 'ang-fill'));

  // Outline the combined L from side
  srG.appendChild($l(aL, aMid - angH + angThk, aR, aMid - angH + angThk, 'obj med'));
  srG.appendChild($l(aL, aMid + angH, aR, aMid + angH, 'obj med'));
  srG.appendChild($l(aL, aMid - angH + angThk, aL, aMid + angH, 'obj med'));
  srG.appendChild($l(aR, aMid - angH + angThk, aR, aMid + angH, 'obj med'));

  // Internal bend line (the L corner from side view)
  srG.appendChild($l(aL, aMid, aR, aMid, 'hidden'));

  // Centerline
  srG.appendChild($l((aL + aR)/2, aMid - angH - 15, (aL + aR)/2, aMid + angH + 25, 'center'));

  // Bolt holes at left end
  var boltInset = 12;  // px from end
  srG.appendChild($c(aL + boltInset, aMid + angH/2, 2.5, 'bolt'));
  srG.appendChild($c(aL + boltInset, aMid - angH/2, 2.5, 'bolt'));

  // Bolt holes at right end
  srG.appendChild($c(aR - boltInset, aMid + angH/2, 2.5, 'bolt'));
  srG.appendChild($c(aR - boltInset, aMid - angH/2, 2.5, 'bolt'));

  svg.appendChild(srG);

  // Labels at attachment points
  svg.appendChild($t(aL + boltInset, aMid + angH + 18, 'PURLIN ATTACH', 'noteb', 'middle'));
  svg.appendChild($t(aL + boltInset, aMid + angH + 27, '(2) #10 TEK', 'note', 'middle'));
  svg.appendChild($t(aR - boltInset, aMid + angH + 18, 'PURLIN ATTACH', 'noteb', 'middle'));
  svg.appendChild($t(aR - boltInset, aMid + angH + 27, '(2) #10 TEK', 'note', 'middle'));

  // Section cut indicator A-A
  var secX = (aL + aR) / 2;
  svg.appendChild($l(secX - 8, aMid - angH - 20, secX - 8, aMid + angH + 30, 'cut-line'));
  svg.appendChild($l(secX + 8, aMid - angH - 20, secX + 8, aMid + angH + 30, 'cut-line'));
  svg.appendChild($t(secX - 8, aMid - angH - 23, 'A', 'lblb', 'middle'));
  svg.appendChild($t(secX + 8, aMid - angH - 23, 'A', 'lblb', 'middle'));

  // Mark label
  svg.appendChild($t((aL + aR)/2, aMid - angH - 8, p.mark + '  (L2x2x' + p.gauge + ')', 'lblb', 'middle'));

  // ── Elevation dimensions ──
  // Total length
  dimH(svg, aL, aR, aMid + angH + 8, 38, fmtFtIn(p.lengthIn));

  // Bolt hole edge distance (left)
  var boltEdge = boltInset / sc;
  dimH(svg, aL, aL + boltInset, aMid - angH - 5, -16, fmtDec(boltEdge, 1) + '"');

  // Bolt hole edge distance (right)
  dimH(svg, aR - boltInset, aR, aMid - angH - 5, -16, fmtDec(boltEdge, 1) + '"');

  // Leg depth (right side)
  dimV(svg, aR + 8, aMid, aMid + angH, 16, p.leg + '"');

  // Scale note
  var elevScale = fmtScale(sc);
  svg.appendChild($t(330, aMid + angH + 62, 'SCALE: ' + elevScale, 'note', 'middle'));

  // ── Sag rod schedule (right side) ──
  var infoX = 700;
  svg.appendChild($t(infoX + 100, 35, 'SAG ROD SCHEDULE', 'lblb', 'middle'));
  svg.appendChild($l(infoX + 10, 40, infoX + 190, 40, 'obj hair'));

  var infoLines = [
    ['MARK:', p.mark],
    ['PROFILE:', 'L2"x2"'],
    ['GAUGE:', p.gauge + ' (' + fmtDec(p.thick, 3) + '")'],
    ['MATERIAL:', p.material],
    ['COIL WIDTH:', p.coilWidth + '"'],
    ['LENGTH:', fmtFtIn(p.lengthIn)],
    ['WT/LFT:', fmtDec(p.lbsLft, 4) + ' lbs/ft'],
    ['WT/PIECE:', fmtDec(p.wtPiece) + ' lbs'],
    ['QTY:', p.qty],
    ['TOTAL WT:', fmtDec(p.totalWt) + ' lbs'],
    ['MAX PIECE:', "20'-3\""],
    ['ROLL WT:', SAGROD_SPECS.roll_weight_lbs + ' lbs'],
    ['BUNDLE:', '~' + p.bundleSize + ' pcs/roll']
  ];
  infoLines.forEach(function(pair, i) {
    var iy = 55 + i * 13;
    svg.appendChild($t(infoX + 12, iy, pair[0], 'note'));
    svg.appendChild($t(infoX + 80, iy, String(pair[1]), 'lbl'));
  });

  // ════════════════════════════════════════════════════════════════════
  // ZONE 2: SECTION A-A (y=230 to y=450)
  // Full L-shaped cross-section with dimensions
  // ════════════════════════════════════════════════════════════════════
  svg.appendChild($t(180, 235, 'SECTION A-A', 'ttl'));

  var cx = 180;   // section center X
  var cy = 350;   // section center Y
  var zScale = 18; // px per inch for cross-section detail (large for 2" legs)

  var legPx = p.leg * zScale;         // leg length in px
  var tPx = Math.max(p.thick * zScale, 2); // material thickness in px

  var secG = $g('hover-part', 'l-section');

  // L-angle cross-section (outer profile)
  // Origin at inside corner of the L
  var ox = cx - legPx/2 + tPx;   // left edge of vertical leg
  var oy = cy + legPx/2 - tPx;   // bottom of horizontal leg

  // Draw L-shape as a filled path (clockwise outer)
  var lPath = 'M ' + ox + ' ' + (oy - legPx) +           // top of vertical leg
              ' L ' + (ox + tPx) + ' ' + (oy - legPx) +  // top-right of vertical leg
              ' L ' + (ox + tPx) + ' ' + oy +             // inside corner
              ' L ' + (ox + legPx) + ' ' + oy +           // right end of horiz leg (inner top)
              ' L ' + (ox + legPx) + ' ' + (oy + tPx) +   // right end of horiz leg (outer bottom)
              ' L ' + ox + ' ' + (oy + tPx) +              // bottom-left corner
              ' Z';
  secG.appendChild($p(lPath, 'ang-fill'));
  // Heavy outline
  secG.appendChild($p(lPath, 'obj thick'));

  // Centerlines through the L
  secG.appendChild($l(ox - 15, cy, ox + legPx + 15, cy, 'center'));
  secG.appendChild($l(cx, oy - legPx - 15, cx, oy + tPx + 15, 'center'));

  // Bolt hole in vertical leg
  var boltCx = ox + tPx/2;
  var boltCy = oy - legPx/2;
  secG.appendChild($c(boltCx, boltCy, 3, 'bolt'));
  svg.appendChild(secG);

  svg.appendChild($t(boltCx + 12, boltCy + 3, '#10 TEK', 'noteb'));

  // ── Section A-A dimensions ──
  // Vertical leg height (left side)
  dimV(svg, ox - 5, oy - legPx, oy + tPx, -20, p.leg + '"');

  // Horizontal leg width (bottom)
  dimH(svg, ox, ox + legPx, oy + tPx + 5, 18, p.leg + '"');

  // Thickness callout on vertical leg
  dimH(svg, ox, ox + tPx, oy - legPx - 5, -14, fmtDec(p.thick, 3) + '"');

  // Gauge callout
  svg.appendChild($t(ox + legPx + 20, oy - legPx/2, p.gauge, 'lblb'));
  svg.appendChild($t(ox + legPx + 20, oy - legPx/2 + 11, '(' + fmtDec(p.thick, 3) + '")', 'note'));

  // Material callout
  svg.appendChild($t(ox + legPx + 20, oy + 5, 'MATERIAL:', 'noteb'));
  svg.appendChild($t(ox + legPx + 20, oy + 15, p.material, 'note'));
  svg.appendChild($t(ox + legPx + 20, oy + 25, 'STEEL', 'note'));

  // Coil width note
  svg.appendChild($t(ox + legPx + 20, oy + 40, 'FROM ' + p.coilWidth + '" COIL', 'note'));

  // Scale note
  svg.appendChild($t(180, oy + tPx + 50, 'SCALE: 1" = ' + fmtDec(1/zScale * 12, 1) + '"', 'note', 'middle'));

  // ════════════════════════════════════════════════════════════════════
  // ZONE 3: DETAIL VIEWS (y=230 to y=450, right side)
  // ════════════════════════════════════════════════════════════════════

  // ── DETAIL 1: Sag Rod to Purlin Web Connection (x=420, y=240) ──
  svg.appendChild($t(500, 235, 'DETAIL 1: SAG ROD TO PURLIN CONNECTION', 'ttl'));

  var d1x = 500, d1y = 340;
  var d1G = $g('hover-part', 'detail-tek');

  // Purlin web (vertical rectangle)
  d1G.appendChild($r(d1x - 3, d1y - 55, 6, 110, 'cee'));
  d1G.appendChild($t(d1x + 8, d1y - 48, 'PURLIN', 'note'));
  d1G.appendChild($t(d1x + 8, d1y - 38, 'WEB', 'note'));

  // Sag rod angle (L-shape from side, butting against purlin web)
  // Vertical leg against purlin
  var srVLegH = 32;
  var srHLegW = 32;
  var srThk = 4;
  var srTop = d1y - srVLegH/2;

  // Vertical leg (against purlin web)
  d1G.appendChild($e('rect', {x: d1x + 3, y: srTop, width: srThk, height: srVLegH,
    class: 'ang-fill'}));

  // Horizontal leg (extending away from purlin)
  d1G.appendChild($e('rect', {x: d1x + 3, y: srTop + srVLegH - srThk, width: srHLegW, height: srThk,
    class: 'ang-fill'}));

  // L-shape outline
  var detLPath = 'M ' + (d1x + 3) + ' ' + srTop +
                 ' L ' + (d1x + 3 + srThk) + ' ' + srTop +
                 ' L ' + (d1x + 3 + srThk) + ' ' + (srTop + srVLegH - srThk) +
                 ' L ' + (d1x + 3 + srHLegW) + ' ' + (srTop + srVLegH - srThk) +
                 ' L ' + (d1x + 3 + srHLegW) + ' ' + (srTop + srVLegH) +
                 ' L ' + (d1x + 3) + ' ' + (srTop + srVLegH) +
                 ' Z';
  d1G.appendChild($p(detLPath, 'obj med'));

  // Label the angle
  d1G.appendChild($t(d1x + 3 + srHLegW + 6, srTop + srVLegH/2, 'L2"x2"x' + p.gauge, 'noteb'));
  d1G.appendChild($t(d1x + 3 + srHLegW + 6, srTop + srVLegH/2 + 10, 'SAG ROD', 'note'));

  // TEK screws through vertical leg into purlin web
  d1G.appendChild($c(d1x + 3 + srThk/2, srTop + 8, 2.5, 'bolt'));
  d1G.appendChild($c(d1x + 3 + srThk/2, srTop + srVLegH - 8, 2.5, 'bolt'));

  // TEK screw callout with leader
  d1G.appendChild($l(d1x + 3 + srThk/2 + 2.5, srTop + 8, d1x + 45, srTop - 8, 'dim'));
  d1G.appendChild($t(d1x + 47, srTop - 12, '(2) #10 TEK SCREWS', 'noteb'));
  d1G.appendChild($t(d1x + 47, srTop - 3, 'THRU ANGLE INTO PURLIN WEB', 'note'));

  // Cross-hatch/arrow showing attachment direction
  d1G.appendChild($l(d1x - 15, d1y, d1x - 3, d1y, 'dim'));
  d1G.appendChild($l(d1x - 8, d1y - 3, d1x - 3, d1y, 'dim'));
  d1G.appendChild($l(d1x - 8, d1y + 3, d1x - 3, d1y, 'dim'));

  svg.appendChild(d1G);
  svg.appendChild($t(500, d1y + 65, 'NTS', 'note', 'middle'));

  // ── DETAIL 2: Angle Cut Detail (x=750, y=240) ──
  svg.appendChild($t(830, 235, 'DETAIL 2: ANGLE CUT DETAIL', 'ttl'));

  var d2x = 790, d2y = 330;
  var d2G = $g('hover-part', 'detail-cut');

  // Show the end of the angle with a square cut (standard)
  var cutLegH = 36;
  var cutLegW = 36;
  var cutThk = 5;

  // L-angle end view (same as section but showing cut line)
  // Vertical leg
  d2G.appendChild($e('rect', {x: d2x, y: d2y - cutLegH, width: cutThk, height: cutLegH,
    class: 'ang-fill'}));
  // Horizontal leg
  d2G.appendChild($e('rect', {x: d2x, y: d2y - cutThk, width: cutLegW, height: cutThk,
    class: 'ang-fill'}));

  // Cut line on right side (square cut - standard)
  d2G.appendChild($l(d2x + cutLegW, d2y - cutThk, d2x + cutLegW, d2y + 3, 'cut-line'));
  d2G.appendChild($l(d2x + cutThk, d2y - cutLegH, d2x + cutThk + 3, d2y - cutLegH, 'cut-line'));

  // Show sag rod extending to the left
  d2G.appendChild($r(d2x - 50, d2y - cutLegH, cutThk, cutLegH, 'ang-fill'));
  d2G.appendChild($r(d2x - 50, d2y - cutThk, cutLegW + 50, cutThk, 'ang-fill'));

  // Dashed lines showing continued length
  d2G.appendChild($l(d2x - 65, d2y - cutLegH/2, d2x - 52, d2y - cutLegH/2, 'hidden'));

  // Square cut label
  d2G.appendChild($t(d2x + cutLegW + 8, d2y - cutThk/2, 'SQUARE CUT', 'noteb'));
  d2G.appendChild($t(d2x + cutLegW + 8, d2y - cutThk/2 + 10, '(BOTH ENDS)', 'note'));

  // 90-degree symbol at the cut
  d2G.appendChild($e('rect', {x: d2x + cutLegW - 6, y: d2y - cutThk - 6, width: 6, height: 6,
    fill: 'none', stroke: '#CC0000', 'stroke-width': '0.5'}));

  // Cut length dimension
  dimH(svg, d2x - 50, d2x + cutLegW, d2y + 8, 16, 'CUT TO LENGTH');

  // Deburr note
  d2G.appendChild($t(d2x - 20, d2y + 38, 'DEBURR ALL CUT EDGES', 'noteb', 'middle'));

  svg.appendChild(d2G);
  svg.appendChild($t(830, d2y + cutLegH + 30, 'NTS', 'note', 'middle'));

  // ════════════════════════════════════════════════════════════════════
  // ZONE 4: BOM TABLE (y=480 to y=660)
  // ════════════════════════════════════════════════════════════════════
  svg.appendChild($t(300, 480, 'BILL OF MATERIALS', 'ttl'));

  var bomX = 40, bomY = 492, bomW = 620;
  var cols = [0, 80, 120, 250, 370, 450, 530];
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

  // Row 1: Sag Rod
  bomRows.push({
    mk: p.mark, qty: p.qty,
    desc: 'SAG ROD L2"x2" ANGLE',
    len: fmtFtIn(p.lengthIn),
    mat: 'G90', ga: p.gauge,
    wt: fmtDec(p.wtPiece * p.qty)
  });

  // Row 2: TEK Screws
  var tekQty = p.qty * 2 * SAGROD_SPECS.tek_per_purlin;  // 2 purlins per rod, 2 TEK per purlin
  bomRows.push({
    mk: 'TEK', qty: tekQty,
    desc: '#10 TEK SCREW',
    len: '3/4"',
    mat: 'ZN', ga: '--',
    wt: '--'
  });

  var totalWeight = p.totalWt;

  bomRows.forEach(function(row, i) {
    var ry = bomY + 14 + i * 14;
    svg.appendChild($l(bomX, ry + 14, bomX + bomW, ry + 14, 'dim'));
    var vals = [row.mk, String(row.qty), row.desc, row.len, row.mat, row.ga, row.wt];
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
    '1. SAG RODS ROLL-FORMED IN-HOUSE FROM ' + p.coilWidth + '" COIL',
    '2. MATERIAL: ' + p.gauge + ' ' + p.material + ' STEEL',
    '3. PROFILE: L2"x2" ANGLE',
    '4. SAG RODS RUN PERPENDICULAR TO PURLINS',
    '5. CONNECTS PAIRS OF PURLINS FOR LATERAL BRACING',
    '6. ATTACHED TO PURLIN WEB VIA (2) #10 TEK SCREWS',
    '7. SQUARE CUT BOTH ENDS — DEBURR',
    '8. MAX SINGLE PIECE LENGTH: 20\'-3"',
    '9. ROLL WEIGHT: ' + SAGROD_SPECS.roll_weight_lbs + ' LBS',
    '10. DO NOT SCALE DRAWING',
    '11. TOL: LENGTH +/-1/16"',
    '12. ALL HOLES FIELD-DRILLED AS REQUIRED'
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
    drawingTitle: 'SAGROD',
    partMark: p.mark,
    revision: 0,
    revHistory: [],
    projectNotes: [
      'MATERIAL: ' + p.gauge + ' ' + p.material + ' STEEL',
      'COIL: ' + p.coilWidth + '" ROLL-FORMED IN-HOUSE',
      'PROFILE: L2"x2" ANGLE',
      'SURF PREP: G90 GALVANIZED (NO PAINT)',
      'FASTENERS: #10 TEK SCREWS (FIELD)',
      'SAG RODS BRACE PURLINS LATERALLY',
      'SQUARE CUT BOTH ENDS',
      'MAX PIECE: 20\'-3" (SINGLE LENGTH)',
      'WT/LFT: ' + fmtDec(p.lbsLft, 4) + ' LBS/FT',
      'ROLL WT: ' + SAGROD_SPECS.roll_weight_lbs + ' LBS',
      'FAB: AISC 360-22 / AWS D1.1',
      'DO NOT SCALE DRAWING',
      'TOL: LENGTH +/-1/16"'
    ]
  });

  // ── Update footer stats ──
  var fLen = document.getElementById('fLength');
  var fGauge = document.getElementById('fGauge');
  var fQty = document.getElementById('fQty');
  var fBundle = document.getElementById('fBundle');
  var fWt = document.getElementById('fWt');
  if (fLen) fLen.textContent = fmtFtIn(p.lengthIn);
  if (fGauge) fGauge.textContent = p.gauge;
  if (fQty) fQty.textContent = p.qty;
  if (fBundle) fBundle.textContent = '~' + p.bundleSize + ' pcs/roll';
  if (fWt) fWt.textContent = fmtDec(p.totalWt) + ' lbs';

  // ── Update BOM side panel ──
  updateBOM([
    { mk: p.mark, qty: p.qty, desc: 'Sag Rod L2"x2"', size: fmtFtIn(p.lengthIn) + ' x ' + p.gauge, mat: 'G90', wt: Math.round(p.totalWt) },
    { mk: 'TEK', qty: tekQty, desc: '#10 TEK Screw', size: '3/4"', mat: 'ZN', wt: 0 }
  ]);
}
"""

# ═══════════════════════════════════════════════════════════════════════════════
# Controls HTML — sag rod-specific inputs
# ═══════════════════════════════════════════════════════════════════════════════

SAGROD_CONTROLS = """
    <div class="ctrl-group">
      <label>Gauge</label>
      <select id="selGauge" onchange="draw()">
        <option value="16GA" selected>16GA</option>
      </select>
    </div>
    <div class="ctrl-group">
      <label>Length (in)</label>
      <input type="number" id="inpLength" value="60" min="6" max="243" step="1" onchange="draw()">
    </div>
    <div class="ctrl-group">
      <label>Qty</label>
      <input type="number" id="inpQty" value="1" min="1" max="500" step="1" onchange="draw()">
    </div>
    <div class="ctrl-group">
      <label>Mark</label>
      <input type="text" id="inpMark" value="SR-1" style="width:60px;" onchange="draw()">
    </div>
    <button class="toggle-btn" onclick="window.print()">Print</button>
"""

# ═══════════════════════════════════════════════════════════════════════════════
# Footer HTML — sag rod-specific stats
# ═══════════════════════════════════════════════════════════════════════════════

SAGROD_FOOTER = """
  <div>Length: <span class="s" id="fLength">--</span></div>
  <div>Gauge: <span class="s" id="fGauge">--</span></div>
  <div>Qty: <span class="s" id="fQty">--</span></div>
  <div>Bundle: <span class="s" id="fBundle">--</span></div>
  <div>Total Weight: <span class="s" id="fWt">--</span></div>
"""

# ═══════════════════════════════════════════════════════════════════════════════
# Assemble final HTML via drawing_base
# ═══════════════════════════════════════════════════════════════════════════════

SAGROD_DRAWING_HTML = drawing_base.build_html_shell(
    title="Sag Rod Shop Drawing",
    drawing_type="sagrod",
    config_var="SAGROD_CONFIG",
    controls_html=SAGROD_CONTROLS,
    footer_html=SAGROD_FOOTER,
    drawing_js=SAGROD_JS,
)
