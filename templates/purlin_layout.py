"""
TitanForge -- Interactive Purlin Layout Shop Drawing
=====================================================
Full building-length purlin layout showing piece breaks, bay sizes,
and optional solar panel overlay. Supports C-purlin (butt-joint) and
Z-purlin (overlap/splice) modes with cost comparison across 4 options.

Uses drawing_base.build_html_shell() for the outer wrapper.
"""

import templates.drawing_base as drawing_base

# ===================================================================
# Component-specific JavaScript: draw() and helpers
# ===================================================================

PURLIN_LAYOUT_JS = r"""
// ── State Variables ──
var mode = 'standard';
var purlinType = 'C';
var orientation = 'landscape';
var maxPurlinLenFt = 45;
var zExtensionFt = 4;
var overhangEnabled = false;
var rafterWidthIn = 8;
var endcapClearanceIn = 4;
var slopeDefault = 5;

// Solar panel spec
var panelWidthMm = 992;
var panelLengthMm = 1675;
var mountHoleDistMm = 990;
var holeInsetMm = 200;
var panelsAcross = 5;
var panelsAlong = 20;
var gapWidthIn = 0.25;
var gapLengthIn = 0.25;

// Cost
var costPerFtC = 2.50;
var costPerFtZ = 3.00;

// Building / layout
var buildingLengthFt = 60;
var buildingWidthFt = 20;
var nFrames = 4;
var baySizes = [];
var purlinSpacingFt = 5;
var overhangFt = 1;

// Comparison results
var comparisonResults = null;

// ── MM to inches ──
function mmToIn(mm) { return mm / 25.4; }

// ── Compute rafter positions from bay sizes ──
function computeRafterPositions() {
  var bays = baySizes.length > 0 ? baySizes : [];
  if (bays.length === 0) {
    // Equal bays
    var numBays = Math.max(nFrames - 1, 1);
    var bayLen = (buildingLengthFt * 12) / numBays;
    for (var i = 0; i < numBays; i++) bays.push(bayLen);
  }
  var positions = [0];
  var pos = 0;
  for (var i = 0; i < bays.length; i++) {
    pos += (typeof bays[i] === 'number' ? bays[i] : bays[i] * 12);
    positions.push(pos);
  }
  return positions;
}

// ── Core Algorithm: computeLayout ──
function computeLayout(buildingLengthIn, rafterPositions, type, maxLen, zExt) {
  var maxLenIn = maxLen * 12;
  var zExtIn = zExt * 12;
  var numRafters = rafterPositions.length;
  var pieces = [];

  if (type === 'C') {
    // C-purlin: butt-joint at rafter center
    // Each piece sits 4" on the rafter (half of 8" rafter)
    var idx = 0;
    while (idx < numRafters - 1) {
      // Try to span as many bays as possible up to max length
      var bestEnd = idx + 1;
      for (var tryEnd = idx + 1; tryEnd < numRafters; tryEnd++) {
        var startPos = rafterPositions[idx];
        var endPos = rafterPositions[tryEnd];
        var pieceLen = endPos - startPos;
        // Add half-rafter on each end (4" each)
        // But internal joints share: each piece gets 4" on each rafter
        // For end pieces with no overhang: +4" endcap + 4" half-rafter
        var extra = 0;
        if (idx === 0 && !overhangEnabled) extra += endcapClearanceIn + rafterWidthIn / 2;
        if (tryEnd === numRafters - 1 && !overhangEnabled) extra += endcapClearanceIn + rafterWidthIn / 2;
        if (pieceLen + extra <= maxLenIn && tryEnd - idx >= 1) {
          bestEnd = tryEnd;
        } else {
          break;
        }
      }
      // Ensure at least 2 rafters spanned
      if (bestEnd - idx < 1) bestEnd = Math.min(idx + 1, numRafters - 1);

      var startIn = rafterPositions[idx];
      var endIn = rafterPositions[bestEnd];
      var lenIn = endIn - startIn;
      if (idx === 0 && !overhangEnabled) {
        startIn -= (endcapClearanceIn + rafterWidthIn / 2);
        lenIn += (endcapClearanceIn + rafterWidthIn / 2);
      }
      if (bestEnd === numRafters - 1 && !overhangEnabled) {
        endIn += (endcapClearanceIn + rafterWidthIn / 2);
        lenIn += (endcapClearanceIn + rafterWidthIn / 2);
      }

      pieces.push({
        startIn: startIn,
        endIn: endIn,
        lengthIn: lenIn,
        group: pieces.length + 1,
        spansFrom: idx,
        spansTo: bestEnd
      });
      idx = bestEnd;
    }
  } else {
    // Z-purlin: overlap past rafter by extension distance
    var overlapIn = 6; // 6" overlap where purlins meet
    var idx = 0;
    while (idx < numRafters - 1) {
      var bestEnd = idx + 1;
      for (var tryEnd = idx + 1; tryEnd < numRafters; tryEnd++) {
        var startPos = rafterPositions[idx];
        var endPos = rafterPositions[tryEnd];
        var pieceLen = endPos - startPos;
        // Z-purlins extend past rafter by zExtension
        var totalLen = pieceLen;
        if (idx > 0) totalLen += zExtIn; // extends past start rafter
        if (tryEnd < numRafters - 1) totalLen += zExtIn; // extends past end rafter
        if (idx === 0 && !overhangEnabled) totalLen += endcapClearanceIn + rafterWidthIn / 2;
        if (tryEnd === numRafters - 1 && !overhangEnabled) totalLen += endcapClearanceIn + rafterWidthIn / 2;

        if (totalLen <= maxLenIn && tryEnd - idx >= 1) {
          bestEnd = tryEnd;
        } else {
          break;
        }
      }
      if (bestEnd - idx < 1) bestEnd = Math.min(idx + 1, numRafters - 1);

      var startIn = rafterPositions[idx];
      var endIn = rafterPositions[bestEnd];
      var lenIn = endIn - startIn;

      // Extensions
      var extStart = 0, extEnd = 0;
      if (idx > 0) { extStart = zExtIn; }
      else if (!overhangEnabled) { extStart = endcapClearanceIn + rafterWidthIn / 2; }

      if (bestEnd < numRafters - 1) { extEnd = zExtIn; }
      else if (!overhangEnabled) { extEnd = endcapClearanceIn + rafterWidthIn / 2; }

      pieces.push({
        startIn: startIn - extStart,
        endIn: endIn + extEnd,
        lengthIn: lenIn + extStart + extEnd,
        group: pieces.length + 1,
        spansFrom: idx,
        spansTo: bestEnd,
        extStart: extStart,
        extEnd: extEnd,
        overlapIn: overlapIn
      });
      idx = bestEnd;
    }
  }
  return pieces;
}

// ── Solar building computation ──
function computeSolarBuilding(panelW, panelL, orient, across, along, gapW, gapL) {
  var pWidthIn, pLengthIn;
  if (orient === 'landscape') {
    pWidthIn = mmToIn(panelW);   // short side across
    pLengthIn = mmToIn(panelL);  // long side along building
  } else {
    pWidthIn = mmToIn(panelL);   // long side across
    pLengthIn = mmToIn(panelW);  // short side along building
  }

  var totalWidth = across * pWidthIn + (across - 1) * gapW + 2 * endcapClearanceIn;
  var totalLength = along * pLengthIn + (along - 1) * gapL + 2 * endcapClearanceIn;

  // Purlin line positions (along width direction)
  var purlinLines = [];
  if (orient === 'landscape') {
    // Panels share purlins: N panels across = N+1 purlin lines
    for (var i = 0; i <= across; i++) {
      purlinLines.push(endcapClearanceIn + i * (pWidthIn + gapW) - gapW / 2);
    }
    purlinLines[0] = endcapClearanceIn;
    purlinLines[purlinLines.length - 1] = totalWidth - endcapClearanceIn;
  } else {
    // Each panel gets 2 purlins: 2N purlin lines
    for (var i = 0; i < across; i++) {
      var panelStart = endcapClearanceIn + i * (pWidthIn + gapW);
      var holeDistIn = mmToIn(mountHoleDistMm);
      var inset = (pWidthIn - holeDistIn) / 2;
      purlinLines.push(panelStart + inset);
      purlinLines.push(panelStart + pWidthIn - inset);
    }
  }

  // Bolt hole positions along building length for each panel
  var boltPositions = [];
  var holeInsetIn = mmToIn(holeInsetMm);
  for (var j = 0; j < along; j++) {
    var panelStartAlong = endcapClearanceIn + j * (pLengthIn + gapL);
    boltPositions.push(panelStartAlong + holeInsetIn);
    boltPositions.push(panelStartAlong + pLengthIn - holeInsetIn);
  }

  return {
    widthIn: totalWidth,
    lengthIn: totalLength,
    purlinLines: purlinLines,
    boltPositions: boltPositions,
    panelWidthIn: pWidthIn,
    panelLengthIn: pLengthIn,
    numPurlinLines: purlinLines.length
  };
}

// ── Run 4-option comparison ──
function runComparison() {
  var rafterPositions = computeRafterPositions();
  var bldgLen = rafterPositions[rafterPositions.length - 1];
  var numLines;

  if (mode === 'solar') {
    var solar = computeSolarBuilding(panelWidthMm, panelLengthMm, 'landscape', panelsAcross, panelsAlong, gapWidthIn, gapLengthIn);
    var solarP = computeSolarBuilding(panelWidthMm, panelLengthMm, 'portrait', panelsAcross, panelsAlong, gapWidthIn, gapLengthIn);
    var linesLandscape = solar.numPurlinLines;
    var linesPortrait = solarP.numPurlinLines;
  } else {
    var numLines = Math.max(Math.floor(buildingWidthFt * 12 / (purlinSpacingFt * 12)) + 1, 2);
    var linesLandscape = numLines;
    var linesPortrait = numLines;
  }

  var results = [];

  // Landscape + C
  var piecesLC = computeLayout(bldgLen, rafterPositions, 'C', maxPurlinLenFt, zExtensionFt);
  var totalLfLC = 0;
  for (var i = 0; i < piecesLC.length; i++) totalLfLC += piecesLC[i].lengthIn / 12;
  results.push({
    label: 'Landscape + C-Purlin',
    orient: 'landscape', type: 'C',
    pieces: piecesLC.length * linesLandscape,
    totalLF: totalLfLC * linesLandscape,
    cost: totalLfLC * linesLandscape * costPerFtC,
    perLine: piecesLC
  });

  // Landscape + Z
  var piecesLZ = computeLayout(bldgLen, rafterPositions, 'Z', maxPurlinLenFt, zExtensionFt);
  var totalLfLZ = 0;
  for (var i = 0; i < piecesLZ.length; i++) totalLfLZ += piecesLZ[i].lengthIn / 12;
  results.push({
    label: 'Landscape + Z-Purlin',
    orient: 'landscape', type: 'Z',
    pieces: piecesLZ.length * linesLandscape,
    totalLF: totalLfLZ * linesLandscape,
    cost: totalLfLZ * linesLandscape * costPerFtZ,
    perLine: piecesLZ
  });

  // Portrait + C
  var piecesPC = computeLayout(bldgLen, rafterPositions, 'C', maxPurlinLenFt, zExtensionFt);
  var totalLfPC = 0;
  for (var i = 0; i < piecesPC.length; i++) totalLfPC += piecesPC[i].lengthIn / 12;
  results.push({
    label: 'Portrait + C-Purlin',
    orient: 'portrait', type: 'C',
    pieces: piecesPC.length * linesPortrait,
    totalLF: totalLfPC * linesPortrait,
    cost: totalLfPC * linesPortrait * costPerFtC,
    perLine: piecesPC
  });

  // Portrait + Z
  var piecesPZ = computeLayout(bldgLen, rafterPositions, 'Z', maxPurlinLenFt, zExtensionFt);
  var totalLfPZ = 0;
  for (var i = 0; i < piecesPZ.length; i++) totalLfPZ += piecesPZ[i].lengthIn / 12;
  results.push({
    label: 'Portrait + Z-Purlin',
    orient: 'portrait', type: 'Z',
    pieces: piecesPZ.length * linesPortrait,
    totalLF: totalLfPZ * linesPortrait,
    cost: totalLfPZ * linesPortrait * costPerFtZ,
    perLine: piecesPZ
  });

  // Find cheapest
  var minCost = Infinity;
  var minIdx = 0;
  for (var i = 0; i < results.length; i++) {
    if (results[i].cost < minCost) { minCost = results[i].cost; minIdx = i; }
  }
  results[minIdx].recommended = true;

  comparisonResults = results;
  draw();
}

// ── Read UI values ──
function readControls() {
  var el;
  el = document.getElementById('inpMode');
  if (el) mode = el.value;
  el = document.getElementById('inpMaxLen');
  if (el) maxPurlinLenFt = parseFloat(el.value) || 45;
  if (maxPurlinLenFt > 53) maxPurlinLenFt = 53;
  el = document.getElementById('inpZExt');
  if (el) zExtensionFt = parseFloat(el.value) || 4;
  el = document.getElementById('inpBldgLen');
  if (el) buildingLengthFt = parseFloat(el.value) || 60;
  el = document.getElementById('inpFrames');
  if (el) nFrames = parseInt(el.value) || 4;
  el = document.getElementById('inpBldgWidth');
  if (el) buildingWidthFt = parseFloat(el.value) || 20;
  el = document.getElementById('inpSpacing');
  if (el) purlinSpacingFt = parseFloat(el.value) || 5;
  el = document.getElementById('inpPanelW');
  if (el) panelWidthMm = parseFloat(el.value) || 992;
  el = document.getElementById('inpPanelL');
  if (el) panelLengthMm = parseFloat(el.value) || 1675;
  el = document.getElementById('inpPanelsAcross');
  if (el) panelsAcross = parseInt(el.value) || 5;
  el = document.getElementById('inpPanelsAlong');
  if (el) panelsAlong = parseInt(el.value) || 20;
  el = document.getElementById('inpMtgHole');
  if (el) mountHoleDistMm = parseFloat(el.value) || 990;
  el = document.getElementById('inpHoleInset');
  if (el) holeInsetMm = parseFloat(el.value) || 200;
  el = document.getElementById('inpGapW');
  if (el) gapWidthIn = parseFloat(el.value) || 0.25;
  el = document.getElementById('inpGapL');
  if (el) gapLengthIn = parseFloat(el.value) || 0.25;
  el = document.getElementById('inpCostC');
  if (el) costPerFtC = parseFloat(el.value) || 2.50;
  el = document.getElementById('inpCostZ');
  if (el) costPerFtZ = parseFloat(el.value) || 3.00;
}

// ── UI toggle handlers ──
function setMode(m) {
  mode = m;
  var el = document.getElementById('inpMode');
  if (el) el.value = m;
  updateModeVisibility();
  comparisonResults = null;
  draw();
}

function setPurlinType(t) {
  purlinType = t;
  var btns = document.querySelectorAll('.ptype-btn');
  for (var i = 0; i < btns.length; i++) {
    btns[i].classList.toggle('active', btns[i].dataset.type === t);
  }
  var zExtGroup = document.getElementById('zExtGroup');
  if (zExtGroup) zExtGroup.style.display = (t === 'Z') ? 'flex' : 'none';
  comparisonResults = null;
  draw();
}

function setOrientation(o) {
  orientation = o;
  var btns = document.querySelectorAll('.orient-btn');
  for (var i = 0; i < btns.length; i++) {
    btns[i].classList.toggle('active', btns[i].dataset.orient === o);
  }
  comparisonResults = null;
  draw();
}

function toggleOverhang() {
  overhangEnabled = !overhangEnabled;
  var btn = document.getElementById('btnOverhang');
  if (btn) {
    btn.classList.toggle('active', overhangEnabled);
    btn.textContent = overhangEnabled ? 'Overhang: ON' : 'Overhang: OFF';
  }
  comparisonResults = null;
  draw();
}

function updateModeVisibility() {
  var solarCtrls = document.getElementById('solarControls');
  var stdCtrls = document.getElementById('stdControls');
  var orientCtrls = document.getElementById('orientControls');
  if (solarCtrls) solarCtrls.style.display = (mode === 'solar') ? 'flex' : 'none';
  if (stdCtrls) stdCtrls.style.display = (mode === 'standard') ? 'flex' : 'none';
  if (orientCtrls) orientCtrls.style.display = (mode === 'solar') ? 'flex' : 'none';
}

function onControlChange() {
  readControls();
  comparisonResults = null;
  draw();
}

// ==============================================
// MAIN DRAW FUNCTION
// ==============================================
function draw() {
  var svg = document.getElementById('svg');
  while (svg.firstChild) svg.removeChild(svg.firstChild);
  svg.setAttribute('viewBox', '0 0 1100 850');

  readControls();

  var projName = document.getElementById('setProjectName').value || 'PROJECT';
  var customer = document.getElementById('setCustomer').value || '';
  var jobNum = document.getElementById('setJobNumber').value || '';
  var drawingNum = document.getElementById('setDrawingNum').value || 'SD-001';
  var drawnBy = document.getElementById('setDrawnBy').value || 'AUTO';
  var surfPrep = document.getElementById('setSurfPrep').value || 'G90';

  // Compute layout
  var rafterPositions = computeRafterPositions();
  var bldgLenIn = rafterPositions[rafterPositions.length - 1];
  var pieces = computeLayout(bldgLenIn, rafterPositions, purlinType, maxPurlinLenFt, zExtensionFt);

  // Solar data
  var solarData = null;
  if (mode === 'solar') {
    solarData = computeSolarBuilding(panelWidthMm, panelLengthMm, orientation, panelsAcross, panelsAlong, gapWidthIn, gapLengthIn);
  }

  // Overall building length including endcaps
  var totalBldgIn = bldgLenIn;
  if (!overhangEnabled) {
    totalBldgIn = bldgLenIn + (rafterWidthIn / 2 + endcapClearanceIn) * 2;
  }

  // ================================================================
  // ZONE 1: TOP-DOWN PLAN VIEW (x=40..1060, y=20..350)
  // ================================================================
  svg.appendChild($t(550, 18, 'PURLIN LAYOUT - PLAN VIEW (' + purlinType + '-PURLIN, ' + mode.toUpperCase() + ')', 'ttl'));

  var planL = 60, planR = 1040;
  var planT = 35, planB = 330;
  var planW = planR - planL;
  var planH = planB - planT;

  // Scale factor: building length maps to planW
  var sc = planW / totalBldgIn;

  // Offset for endcap clearance
  var offsetX = 0;
  if (!overhangEnabled) {
    offsetX = (endcapClearanceIn + rafterWidthIn / 2) * sc;
  }

  // Draw rafters as vertical gray bars
  var rafG = $g('', 'rafters');
  for (var i = 0; i < rafterPositions.length; i++) {
    var rx = planL + offsetX + rafterPositions[i] * sc;
    var rw = rafterWidthIn * sc;
    if (rw < 3) rw = 3;
    rafG.appendChild($e('rect', {
      x: rx - rw / 2, y: planT + 10, width: rw, height: planH - 40,
      fill: '#D0D0D0', stroke: '#999', 'stroke-width': '0.5'
    }));
    // Rafter label
    if (i === 0 || i === rafterPositions.length - 1 || rafterPositions.length <= 8) {
      svg.appendChild($t(rx, planB - 15, 'R' + (i + 1), 'note', 'middle'));
    }
  }
  svg.appendChild(rafG);

  // Number of purlin lines to show
  var numPurlinLines;
  if (mode === 'solar' && solarData) {
    numPurlinLines = solarData.numPurlinLines;
  } else {
    numPurlinLines = Math.max(Math.floor(buildingWidthFt * 12 / (purlinSpacingFt * 12)) + 1, 2);
  }
  var maxLines = Math.min(numPurlinLines, 8); // Show max 8 lines for readability
  var lineSpacing = (planH - 80) / (maxLines + 1);

  // Draw purlin lines
  var purG = $g('hover-part', 'purlins');
  for (var line = 0; line < maxLines; line++) {
    var ly = planT + 40 + (line + 1) * lineSpacing;

    // Z-purlin facing: groups of 2 (right, left, right, left)
    var facing = (Math.floor(line / 2) % 2 === 0) ? 1 : -1;
    if (line % 2 === 1) facing = -facing;

    for (var p = 0; p < pieces.length; p++) {
      var piece = pieces[p];
      var px1 = planL + offsetX + (piece.startIn + (overhangEnabled ? 0 : (endcapClearanceIn + rafterWidthIn / 2))) * sc;
      var px2 = planL + offsetX + (piece.endIn + (overhangEnabled ? 0 : (endcapClearanceIn + rafterWidthIn / 2))) * sc;

      // Adjust for actual piece positions
      px1 = planL + (piece.startIn + (overhangEnabled ? 0 : (endcapClearanceIn + rafterWidthIn / 2))) * sc;
      px2 = planL + (piece.endIn + (overhangEnabled ? 0 : (endcapClearanceIn + rafterWidthIn / 2))) * sc;

      var barH = 4;
      var fillColor = (purlinType === 'C') ? '#4A90D9' : '#D9534F';
      purG.appendChild($e('rect', {
        x: px1, y: ly - barH / 2, width: px2 - px1, height: barH,
        fill: fillColor, stroke: '#333', 'stroke-width': '0.5', opacity: '0.8'
      }));

      // Piece break marker
      if (p < pieces.length - 1) {
        var breakX = px2;
        purG.appendChild($e('line', {
          x1: breakX, y1: ly - 6, x2: breakX, y2: ly + 6,
          stroke: '#CC0000', 'stroke-width': '1'
        }));

        // Z-purlin overlap indicator
        if (purlinType === 'Z' && piece.extEnd > 0) {
          var overlapW = piece.overlapIn * sc;
          purG.appendChild($e('rect', {
            x: breakX - overlapW / 2, y: ly - barH / 2 - 1,
            width: overlapW, height: barH + 2,
            fill: '#FF6600', stroke: 'none', opacity: '0.4'
          }));
        }
      }

      // Piece length label (only on first line)
      if (line === 0 && pieces.length <= 6) {
        var midX = (px1 + px2) / 2;
        svg.appendChild($t(midX, ly - 8, fmtFtIn(piece.lengthIn), 'note', 'middle'));
      }
    }
  }
  svg.appendChild(purG);

  // Solar panel overlay
  if (mode === 'solar' && solarData) {
    var solG = $g('', 'solar-panels');
    var panelScY = (planH - 80) / (solarData.widthIn);
    var panelScX = planW / solarData.lengthIn;
    var useSc = Math.min(panelScX, panelScY, sc);

    for (var pa = 0; pa < panelsAlong; pa++) {
      for (var pw = 0; pw < panelsAcross; pw++) {
        var pxStart = endcapClearanceIn + pa * (solarData.panelLengthIn + gapLengthIn);
        var pyStart = endcapClearanceIn + pw * (solarData.panelWidthIn + gapWidthIn);

        var drawX = planL + pxStart * sc;
        var drawY = planT + 40 + pyStart * panelScY;
        var drawW = solarData.panelLengthIn * sc;
        var drawH = solarData.panelWidthIn * panelScY;

        // Only draw if it fits in the view
        if (drawX + drawW <= planR && drawY + drawH <= planB - 20) {
          solG.appendChild($e('rect', {
            x: drawX, y: drawY, width: drawW, height: drawH,
            fill: '#4DABF7', 'fill-opacity': '0.15',
            stroke: '#4DABF7', 'stroke-width': '0.5'
          }));

          // Bolt holes (4 per panel)
          var hInset = mmToIn(holeInsetMm) * sc;
          var hDist = mmToIn(mountHoleDistMm) * panelScY;
          var holeR = 1.5;
          var holes = [
            [drawX + hInset, drawY + (drawH - hDist) / 2],
            [drawX + hInset, drawY + (drawH + hDist) / 2],
            [drawX + drawW - hInset, drawY + (drawH - hDist) / 2],
            [drawX + drawW - hInset, drawY + (drawH + hDist) / 2]
          ];
          for (var h = 0; h < holes.length; h++) {
            if (holes[h][0] > planL && holes[h][0] < planR && holes[h][1] > planT && holes[h][1] < planB) {
              solG.appendChild($e('circle', {
                cx: holes[h][0], cy: holes[h][1], r: holeR,
                fill: 'none', stroke: '#E03131', 'stroke-width': '0.6'
              }));
            }
          }
        }
      }
    }
    svg.appendChild(solG);
  }

  // Dimension lines
  // Overall building length
  dimH(svg, planL, planR, planB - 5, 12, fmtFtIn(totalBldgIn));

  // Bay sizes (between rafters)
  if (rafterPositions.length <= 8) {
    for (var i = 0; i < rafterPositions.length - 1; i++) {
      var x1 = planL + offsetX + rafterPositions[i] * sc;
      var x2 = planL + offsetX + rafterPositions[i + 1] * sc;
      var bayIn = rafterPositions[i + 1] - rafterPositions[i];
      dimH(svg, x1, x2, planT + 5, -12, fmtFtIn(bayIn));
    }
  }

  // ================================================================
  // ZONE 2: PURLIN CROSS-SECTION (y=370..520)
  // ================================================================
  var secTitle = (purlinType === 'Z') ? 'Z-PURLIN CROSS-SECTION' : 'C-PURLIN CROSS-SECTION';
  svg.appendChild($t(180, 365, secTitle, 'ttl'));

  var cx = 180, cy = 445;
  var zScale = 5;
  var depth = 8; // default purlin depth
  var topFlange = 2.75, botFlange = 2.75, lip = 0.625;

  var zD = depth * zScale;
  var zTF = topFlange * zScale;
  var zBF = botFlange * zScale;
  var zLip = lip * zScale;
  var zT = 2;

  var zTop = cy - zD / 2;
  var zBot = cy + zD / 2;

  var secG = $g('hover-part', 'purlin-section');

  if (purlinType === 'Z') {
    // Z-purlin: top flange right, bottom flange left
    // Web
    secG.appendChild($r(cx - zT / 2, zTop, zT, zD, 'cee'));
    // Top flange (right)
    secG.appendChild($r(cx, zTop, zTF, zT, 'cee'));
    // Bottom flange (left)
    secG.appendChild($r(cx - zBF, zBot - zT, zBF, zT, 'cee'));
    // Lips at 45 degrees
    var lipLen = zLip;
    var lip45 = lipLen * Math.cos(Math.PI / 4);
    // Top lip (up-right from right end of top flange)
    var tlx = cx + zTF;
    secG.appendChild($l(tlx, zTop, tlx + lip45, zTop - lip45, 'obj med'));
    // Bottom lip (down-left from left end of bottom flange)
    var blx = cx - zBF;
    secG.appendChild($l(blx, zBot, blx - lip45, zBot + lip45, 'obj med'));
  } else {
    // C-purlin: both flanges right, lips inward
    // Web
    secG.appendChild($r(cx - zT / 2, zTop, zT, zD, 'cee'));
    // Top flange (right)
    secG.appendChild($r(cx, zTop, zTF, zT, 'cee'));
    // Bottom flange (right)
    secG.appendChild($r(cx, zBot - zT, zBF, zT, 'cee'));
    // Top lip (downward from right end of top flange)
    var tlx = cx + zTF;
    secG.appendChild($l(tlx, zTop, tlx, zTop + zLip, 'obj med'));
    // Bottom lip (upward from right end of bottom flange)
    secG.appendChild($l(tlx, zBot, tlx, zBot - zLip, 'obj med'));
  }

  // Centerlines
  secG.appendChild($l(cx, zTop - 15, cx, zBot + 15, 'center'));
  secG.appendChild($l(cx - zBF - 10, cy, cx + zTF + 10, cy, 'center'));
  svg.appendChild(secG);

  // Dimensions
  dimV(svg, cx + zTF + 10, zTop, zBot, 15, depth + '"');
  dimH(svg, cx, cx + zTF, zTop - 3, -12, topFlange + '"');
  if (purlinType === 'Z') {
    dimH(svg, cx - zBF, cx, zBot + 3, 12, botFlange + '"');
  } else {
    dimH(svg, cx, cx + zBF, zBot + 3, 12, botFlange + '"');
  }

  // Type label
  svg.appendChild($t(cx, zBot + 35, purlinType + '-PURLIN', 'lblb', 'middle'));
  svg.appendChild($t(cx, zBot + 45, depth + '" DEPTH', 'note', 'middle'));

  // ================================================================
  // ZONE 3: CUT LIST / PURLIN SCHEDULE (y=370..520, right side)
  // ================================================================
  svg.appendChild($t(720, 365, 'PURLIN SCHEDULE', 'ttl'));

  var tblX = 500, tblY = 378, tblW = 560;
  var tCols = [0, 50, 90, 200, 310, 410, 480];
  var tHdrs = ['GRP', 'QTY', 'LENGTH', 'PIECES/LINE', 'TOTAL PCS', 'TOTAL LF', 'NOTES'];

  // Header row
  svg.appendChild($e('rect', {x: tblX, y: tblY, width: tblW, height: 14, fill: '#333', stroke: '#333'}));
  for (var i = 0; i < tHdrs.length; i++) {
    var ht = $t(tblX + tCols[i] + 4, tblY + 11, tHdrs[i], 'note');
    ht.setAttribute('fill', '#FFF');
    svg.appendChild(ht);
  }

  // Group pieces by length
  var groups = {};
  for (var i = 0; i < pieces.length; i++) {
    var lenKey = Math.round(pieces[i].lengthIn * 8) / 8; // round to 1/8"
    if (!groups[lenKey]) groups[lenKey] = { lengthIn: pieces[i].lengthIn, count: 0 };
    groups[lenKey].count++;
  }

  var groupKeys = Object.keys(groups).sort(function(a, b) { return parseFloat(b) - parseFloat(a); });
  var totalLF = 0;
  var totalPcs = 0;
  var numLines = mode === 'solar' ? (solarData ? solarData.numPurlinLines : numPurlinLines) : numPurlinLines;

  for (var gi = 0; gi < groupKeys.length && gi < 8; gi++) {
    var grp = groups[groupKeys[gi]];
    var ry = tblY + 14 + gi * 14;
    svg.appendChild($l(tblX, ry + 14, tblX + tblW, ry + 14, 'dim'));

    var qtyPerLine = grp.count;
    var totalQty = qtyPerLine * numLines;
    var lfPerPiece = grp.lengthIn / 12;
    var grpTotalLF = lfPerPiece * totalQty;
    totalLF += grpTotalLF;
    totalPcs += totalQty;

    var noteStr = purlinType === 'Z' ? 'SPLICE @ OVERLAP' : 'BUTT JOINT';

    var vals = [
      String(gi + 1),
      String(numLines),
      fmtFtIn(grp.lengthIn),
      String(qtyPerLine),
      String(totalQty),
      fmtDec(grpTotalLF, 1),
      noteStr
    ];
    for (var ci = 0; ci < vals.length; ci++) {
      svg.appendChild($t(tblX + tCols[ci] + 4, ry + 11, vals[ci], 'lbl'));
    }
  }

  // Total row
  var totY = tblY + 14 + Math.min(groupKeys.length, 8) * 14;
  svg.appendChild($l(tblX, totY, tblX + tblW, totY, 'obj med'));
  svg.appendChild($t(tblX + tCols[3] + 4, totY + 12, 'TOTALS:', 'lblb'));
  svg.appendChild($t(tblX + tCols[4] + 4, totY + 12, String(totalPcs), 'lblb'));
  svg.appendChild($t(tblX + tCols[5] + 4, totY + 12, fmtDec(totalLF, 1) + ' LF', 'lblb'));

  var tblH = 14 + (Math.min(groupKeys.length, 8) + 1) * 14 + 4;
  svg.appendChild($r(tblX, tblY, tblW, tblH, 'obj med'));

  // ================================================================
  // ZONE 4: COST COMPARISON TABLE (y=530..660)
  // ================================================================
  svg.appendChild($t(550, 535, 'COST COMPARISON', 'ttl'));

  if (comparisonResults) {
    var cmpX = 80, cmpY = 548, cmpW = 940;
    var cCols = [0, 240, 380, 520, 660, 800];
    var cHdrs = ['OPTION', 'TOTAL LF', 'PIECES', 'COST', 'SAVINGS', 'STATUS'];

    // Header
    svg.appendChild($e('rect', {x: cmpX, y: cmpY, width: cmpW, height: 14, fill: '#333', stroke: '#333'}));
    for (var i = 0; i < cHdrs.length; i++) {
      var ht = $t(cmpX + cCols[i] + 4, cmpY + 11, cHdrs[i], 'note');
      ht.setAttribute('fill', '#FFF');
      svg.appendChild(ht);
    }

    var minCost = Infinity;
    for (var i = 0; i < comparisonResults.length; i++) {
      if (comparisonResults[i].cost < minCost) minCost = comparisonResults[i].cost;
    }

    for (var i = 0; i < comparisonResults.length; i++) {
      var res = comparisonResults[i];
      var ry = cmpY + 14 + i * 18;

      // Highlight recommended
      if (res.recommended) {
        svg.appendChild($e('rect', {
          x: cmpX + 1, y: ry - 1, width: cmpW - 2, height: 16,
          fill: '#D4EDDA', stroke: '#28A745', 'stroke-width': '0.5'
        }));
      }

      svg.appendChild($l(cmpX, ry + 16, cmpX + cmpW, ry + 16, 'dim'));

      var savings = res.cost - minCost;
      var savingsStr = savings > 0 ? '+$' + fmtDec(savings, 0) : '--';
      var statusStr = res.recommended ? 'RECOMMENDED' : '';

      var cVals = [
        res.label,
        fmtDec(res.totalLF, 0) + ' LF',
        String(res.pieces),
        '$' + fmtDec(res.cost, 0),
        savingsStr,
        statusStr
      ];
      for (var ci = 0; ci < cVals.length; ci++) {
        var cls = res.recommended ? 'lblb' : 'lbl';
        if (ci === 5 && res.recommended) cls = 'warn-text';
        svg.appendChild($t(cmpX + cCols[ci] + 4, ry + 11, cVals[ci], cls));
      }
    }

    var cmpH = 14 + comparisonResults.length * 18 + 4;
    svg.appendChild($r(cmpX, cmpY, cmpW, cmpH, 'obj med'));
  } else {
    svg.appendChild($t(550, 570, 'Click "Compare All" to run 4-option cost analysis', 'note', 'middle'));
    svg.appendChild($t(550, 585, '(Landscape+C, Landscape+Z, Portrait+C, Portrait+Z)', 'note', 'middle'));

    // Show current option summary
    var currentCost = totalLF * (purlinType === 'C' ? costPerFtC : costPerFtZ);
    svg.appendChild($t(550, 610, 'CURRENT: ' + purlinType + '-Purlin, ' + orientation + ', ' + fmtDec(totalLF, 0) + ' LF, ' + totalPcs + ' pcs, $' + fmtDec(currentCost, 0), 'lblb', 'middle'));
  }

  // ================================================================
  // ZONE 5: TITLE BLOCK (y=680..815)
  // ================================================================
  var buildingId = (window.PURLIN_LAYOUT_CONFIG && window.PURLIN_LAYOUT_CONFIG.building_id) || '';
  var titleSuffix = buildingId ? ' - ' + buildingId : '';
  drawTitleBlock(svg, {
    projName: projName,
    customer: customer,
    jobNum: jobNum,
    drawingNum: drawingNum,
    drawnBy: drawnBy,
    surfPrep: surfPrep,
    drawingTitle: 'PURLIN LAYOUT' + titleSuffix,
    partMark: purlinType + '-PURLIN',
    revision: 0,
    revHistory: [],
    projectNotes: [
      'MODE: ' + mode.toUpperCase(),
      'PURLIN TYPE: ' + purlinType + '-PURLIN',
      'MAX LENGTH: ' + maxPurlinLenFt + ' FT',
      purlinType === 'Z' ? 'Z-EXTENSION: ' + zExtensionFt + ' FT' : '',
      'BUILDING: ' + fmtFtIn(totalBldgIn) + ' LONG',
      'FRAMES: ' + nFrames,
      'PURLIN LINES: ' + numLines,
      'TOTAL PIECES: ' + totalPcs,
      'TOTAL LF: ' + fmtDec(totalLF, 0),
      'OVERHANG: ' + (overhangEnabled ? 'YES' : 'NO'),
      'DO NOT SCALE DRAWING'
    ].filter(Boolean)
  });

  // ── Update footer stats ──
  var fMode = document.getElementById('fMode');
  var fType = document.getElementById('fType');
  var fPieces = document.getElementById('fPieces');
  var fTotalLF = document.getElementById('fTotalLF');
  var fLines = document.getElementById('fLines');
  var fCost = document.getElementById('fCost');
  if (fMode) fMode.textContent = mode;
  if (fType) fType.textContent = purlinType;
  if (fPieces) fPieces.textContent = totalPcs;
  if (fTotalLF) fTotalLF.textContent = fmtDec(totalLF, 0) + ' LF';
  if (fLines) fLines.textContent = numLines;
  var currentCostCalc = totalLF * (purlinType === 'C' ? costPerFtC : costPerFtZ);
  if (fCost) fCost.textContent = '$' + fmtDec(currentCostCalc, 0);

  // ── Update BOM ──
  var bomRows = [];
  for (var gi2 = 0; gi2 < groupKeys.length; gi2++) {
    var grp2 = groups[groupKeys[gi2]];
    bomRows.push({
      mk: purlinType + '-' + (gi2 + 1),
      qty: grp2.count * numLines,
      desc: purlinType + '-Purlin ' + depth + '"',
      size: fmtFtIn(grp2.lengthIn),
      mat: 'G90',
      wt: Math.round(grp2.lengthIn / 12 * 3.5 * grp2.count * numLines)
    });
  }
  updateBOM(bomRows);
}

// ── Apply server config ──
function applyComponentConfig(cfg) {
  if (cfg.building_length_ft) {
    buildingLengthFt = cfg.building_length_ft;
    var el = document.getElementById('inpBldgLen');
    if (el) el.value = buildingLengthFt;
  }
  if (cfg.building_width_ft) {
    buildingWidthFt = cfg.building_width_ft;
    var el = document.getElementById('inpBldgWidth');
    if (el) el.value = buildingWidthFt;
  }
  if (cfg.n_frames) {
    nFrames = cfg.n_frames;
    var el = document.getElementById('inpFrames');
    if (el) el.value = nFrames;
  }
  if (cfg.bay_sizes && cfg.bay_sizes.length > 0) {
    baySizes = cfg.bay_sizes;
  }
  if (cfg.purlin_type) {
    purlinType = cfg.purlin_type.toUpperCase().charAt(0) === 'Z' ? 'Z' : 'C';
    setPurlinType(purlinType);
  }
  if (cfg.purlin_spacing_ft) {
    purlinSpacingFt = cfg.purlin_spacing_ft;
    var el = document.getElementById('inpSpacing');
    if (el) el.value = purlinSpacingFt;
  }
  if (cfg.overhang_ft && cfg.overhang_ft > 0) {
    overhangEnabled = true;
    overhangFt = cfg.overhang_ft;
    var btn = document.getElementById('btnOverhang');
    if (btn) { btn.classList.add('active'); btn.textContent = 'Overhang: ON'; }
  }
  if (cfg.max_purlin_length_ft) {
    maxPurlinLenFt = cfg.max_purlin_length_ft;
    var el = document.getElementById('inpMaxLen');
    if (el) el.value = maxPurlinLenFt;
  }
  if (cfg.solar_mode) {
    mode = 'solar';
    setMode('solar');
  }
  updateModeVisibility();
}
"""

# ===================================================================
# Controls HTML
# ===================================================================

PURLIN_LAYOUT_CONTROLS = """
    <div class="ctrl-group">
      <label>Mode:</label>
      <select id="inpMode" onchange="setMode(this.value)">
        <option value="standard">Standard</option>
        <option value="solar">Solar</option>
      </select>
    </div>
    <div class="ctrl-group">
      <label>Type:</label>
      <button class="toggle-btn ptype-btn active" data-type="C" onclick="setPurlinType('C')">C-Purlin</button>
      <button class="toggle-btn ptype-btn" data-type="Z" onclick="setPurlinType('Z')">Z-Purlin</button>
    </div>
    <div class="ctrl-group" id="orientControls" style="display:none;">
      <label>Orient:</label>
      <button class="toggle-btn orient-btn active" data-orient="landscape" onclick="setOrientation('landscape')">Landscape</button>
      <button class="toggle-btn orient-btn" data-orient="portrait" onclick="setOrientation('portrait')">Portrait</button>
    </div>
    <div class="ctrl-group" id="stdControls">
      <label>Length(ft):</label>
      <input type="number" id="inpBldgLen" value="60" min="10" max="300" onchange="onControlChange()">
      <label>Frames:</label>
      <input type="number" id="inpFrames" value="4" min="2" max="20" onchange="onControlChange()">
      <label>Width(ft):</label>
      <input type="number" id="inpBldgWidth" value="20" min="10" max="80" onchange="onControlChange()">
      <label>Spacing(ft):</label>
      <input type="number" id="inpSpacing" value="5" min="1" max="10" step="0.5" onchange="onControlChange()">
    </div>
    <div class="ctrl-group" id="solarControls" style="display:none;">
      <label>Panel W(mm):</label>
      <input type="number" id="inpPanelW" value="992" style="width:60px;" onchange="onControlChange()">
      <label>Panel L(mm):</label>
      <input type="number" id="inpPanelL" value="1675" style="width:60px;" onchange="onControlChange()">
      <label>Mtg Hole(mm):</label>
      <input type="number" id="inpMtgHole" value="990" style="width:60px;" onchange="onControlChange()" title="Mounting hole distance from panel edge">
      <label>Hole Inset(mm):</label>
      <input type="number" id="inpHoleInset" value="200" style="width:60px;" onchange="onControlChange()" title="Hole inset from panel short edge">
      <label>Across:</label>
      <input type="number" id="inpPanelsAcross" value="5" style="width:45px;" onchange="onControlChange()">
      <label>Along:</label>
      <input type="number" id="inpPanelsAlong" value="20" style="width:45px;" onchange="onControlChange()">
      <label>Gap W(in):</label>
      <input type="number" id="inpGapW" value="0.25" step="0.125" style="width:50px;" onchange="onControlChange()" title="Gap between panels across width">
      <label>Gap L(in):</label>
      <input type="number" id="inpGapL" value="0.25" step="0.125" style="width:50px;" onchange="onControlChange()" title="Gap between panels along length">
    </div>
    <div class="ctrl-group">
      <label>Max Len(ft):</label>
      <input type="number" id="inpMaxLen" value="45" min="10" max="53" onchange="onControlChange()">
    </div>
    <div class="ctrl-group" id="zExtGroup" style="display:none;">
      <label>Z-Ext(ft):</label>
      <input type="number" id="inpZExt" value="4" min="1" max="8" onchange="onControlChange()">
    </div>
    <div class="ctrl-group">
      <button class="toggle-btn" id="btnOverhang" onclick="toggleOverhang()">Overhang: OFF</button>
    </div>
    <div class="ctrl-group">
      <label>$/ft C:</label>
      <input type="number" id="inpCostC" value="2.50" step="0.25" style="width:55px;" onchange="onControlChange()">
      <label>$/ft Z:</label>
      <input type="number" id="inpCostZ" value="3.00" step="0.25" style="width:55px;" onchange="onControlChange()">
    </div>
    <div class="ctrl-group">
      <button class="btn-gold" onclick="runComparison()">Compare All</button>
    </div>
    <button class="toggle-btn" onclick="window.print()">Print</button>
"""

# ===================================================================
# Footer HTML
# ===================================================================

PURLIN_LAYOUT_FOOTER = """
  <div>Mode: <span class="s" id="fMode">standard</span></div>
  <div>Type: <span class="s" id="fType">C</span></div>
  <div>Lines: <span class="s" id="fLines">--</span></div>
  <div>Pieces: <span class="s" id="fPieces">--</span></div>
  <div>Total LF: <span class="s" id="fTotalLF">--</span></div>
  <div>Est. Cost: <span class="s" id="fCost">--</span></div>
"""

# ===================================================================
# Assemble final HTML via drawing_base
# ===================================================================

PURLIN_LAYOUT_HTML = drawing_base.build_html_shell(
    title="Purlin Layout",
    drawing_type="purlin_layout",
    config_var="PURLIN_LAYOUT_CONFIG",
    controls_html=PURLIN_LAYOUT_CONTROLS,
    footer_html=PURLIN_LAYOUT_FOOTER,
    drawing_js=PURLIN_LAYOUT_JS,
)
