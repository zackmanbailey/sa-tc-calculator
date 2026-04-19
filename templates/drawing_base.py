"""
TitanForge -- Shared Drawing Base Module
=========================================
Reusable string constants and builder functions for interactive shop drawing
templates.  Every interactive SVG drawing (purlin, sag rod, hurricane strap,
endcap, clip, splice plate, etc.) shares the same dark-theme CSS, SVG helper
functions, title-block layout, BOM panel, and Save-PDF plumbing.

Usage in a component template:

    import templates.drawing_base as drawing_base

    PURLIN_DRAWING_HTML = drawing_base.build_html_shell(
        title="Purlin Shop Drawing",
        drawing_type="purlin",
        config_var="PURLIN_CONFIG",
        controls_html='<div class="ctrl-group">...</div>',
        footer_html='<div>Span: <span class="s" id="fSpan">--</span></div>',
        drawing_js=PURLIN_JS,
    )
"""

# ═══════════════════════════════════════════════════════════════════════════════
# 1.  DRAWING_CSS — Full dark-theme stylesheet
#     Matches rafter_drawing.py lines 15-270 exactly (colours, SVG classes, UI)
# ═══════════════════════════════════════════════════════════════════════════════

DRAWING_CSS = r"""
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    background: #0F172A; color: #F1F5F9; min-height: 100vh;
    display: flex; flex-direction: column;
  }

  /* ── Top bar & controls ── */
  .top-bar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 20px; background: #1E293B; border-bottom: 1px solid #334155;
    flex-wrap: wrap; gap: 8px;
  }
  .top-bar h1 { font-size: 1rem; font-weight: 700; color: #F6AE2D; }
  .top-bar .back-link {
    padding: 6px 12px; background: #334155; color: #94A3B8; border: 1px solid #475569;
    border-radius: 5px; text-decoration: none; font-size: 0.78rem; cursor: pointer;
    transition: all 0.2s;
  }
  .top-bar .back-link:hover { background: #475569; color: #F1F5F9; }
  .top-bar .job-code-label { font-size: 0.85rem; color: #94A3B8; }
  .controls { display: flex; gap: 14px; align-items: center; flex-wrap: wrap; }
  .ctrl-group { display: flex; align-items: center; gap: 6px; }
  .ctrl-group label { font-size: 0.75rem; color: #94A3B8; white-space: nowrap; }
  .ctrl-group select, .ctrl-group input[type=number] {
    background: #334155; color: #F1F5F9; border: 1px solid #475569;
    border-radius: 5px; padding: 5px 8px; font-size: 0.8rem; width: 80px;
  }
  .ctrl-group input[type=text] {
    background: #334155; color: #F1F5F9; border: 1px solid #475569;
    border-radius: 5px; padding: 5px 8px; font-size: 0.8rem;
  }

  /* ── Toggle switch ── */
  .toggle-switch { position: relative; display: inline-block; width: 36px; height: 18px; cursor: pointer; }
  .toggle-switch input { opacity: 0; width: 0; height: 0; }
  .toggle-slider { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: #475569; border-radius: 18px; transition: 0.25s; }
  .toggle-slider::before { content: ''; position: absolute; height: 14px; width: 14px; left: 2px; bottom: 2px; background: #94A3B8; border-radius: 50%; transition: 0.25s; }
  .toggle-switch input:checked + .toggle-slider { background: #F6AE2D; }
  .toggle-switch input:checked + .toggle-slider::before { transform: translateX(18px); background: #0F172A; }

  /* ── Buttons ── */
  .toggle-btn {
    background: #334155; color: #94A3B8; border: 1px solid #475569;
    border-radius: 5px; padding: 5px 12px; font-size: 0.78rem; cursor: pointer;
    transition: all 0.2s;
  }
  .toggle-btn.active { background: #F6AE2D; color: #0F172A; border-color: #F6AE2D; font-weight: 700; }
  .btn-gold {
    background: #F6AE2D; color: #0F172A; border: none; border-radius: 5px;
    padding: 5px 14px; font-weight: 700; font-size: 0.78rem; cursor: pointer;
  }

  /* ── Canvas & drawing sheet ── */
  .canvas-wrap { flex: 1; overflow: auto; display: flex; justify-content: center; padding: 12px; }
  .drawing-sheet {
    background: #FFF; box-shadow: 0 4px 24px rgba(0,0,0,0.5);
    width: 1100px; height: 850px; flex-shrink: 0;
  }
  .drawing-sheet svg { width: 100%; height: 100%; }

  /* ── SVG drawing classes ── */
  .obj { stroke: #1a1a1a; fill: none; }
  .thick { stroke-width: 2.0; }
  .med { stroke-width: 1.0; }
  .thin { stroke-width: 0.5; }
  .hair { stroke-width: 0.3; }
  .hidden { stroke: #777; stroke-width: 0.5; stroke-dasharray: 6,3; fill: none; }
  .center { stroke: #999; stroke-width: 0.3; stroke-dasharray: 14,3,3,3; fill: none; }
  .dim { stroke: #555; stroke-width: 0.3; fill: none; }
  .dimtxt { font: 700 7.5px 'Courier New', monospace; fill: #333; text-anchor: middle; }
  .lbl { font: 8px Arial, sans-serif; fill: #333; }
  .lblb { font: 700 8px Arial, sans-serif; fill: #1a1a1a; }
  .ttl { font: 700 12px Arial, sans-serif; fill: #1a1a1a; text-anchor: middle; }
  .note { font: 6.5px Arial, sans-serif; fill: #555; }
  .noteb { font: 700 6.5px Arial, sans-serif; fill: #333; }
  .cee { fill: #F0F0F0; stroke: #1a1a1a; stroke-width: 1.5; }
  .cap { fill: #E0E0E0; stroke: #1a1a1a; stroke-width: 1.2; }
  .gus { fill: #D8D8D8; stroke: #1a1a1a; stroke-width: 1.0; }
  .bolt { fill: #FFF; stroke: #1a1a1a; stroke-width: 0.8; }
  .nopaint { fill: #FF6600; fill-opacity: 0.12; stroke: #FF6600; stroke-width: 0.4; stroke-dasharray: 4,2; }
  .cut-line { stroke: #CC0000; stroke-width: 0.8; fill: none; }
  .weld { stroke: #0055AA; stroke-width: 0.8; fill: none; }
  .ang-fill { fill: #FFF8E7; stroke: #C4960B; stroke-width: 0.6; }
  .clip-fill { fill: #C8D8E8; stroke: #1a1a1a; stroke-width: 0.8; }
  .conn-plate { fill: #B8B8B8; stroke: #1a1a1a; stroke-width: 1.2; }
  .dim-bold { font: 700 9.5px 'Courier New', monospace; fill: #1a1a1a; text-anchor: middle; }
  .warn-text { font: 700 8px Arial, sans-serif; fill: #CC0000; }

  /* ── AWS Weld Symbols ── */
  .weld-ref { stroke: #0055AA; stroke-width: 0.8; fill: none; }
  .weld-arrow { stroke: #0055AA; stroke-width: 0.8; fill: #0055AA; }
  .weld-sym { stroke: #0055AA; stroke-width: 0.7; fill: none; }
  .weld-sym-filled { stroke: #0055AA; stroke-width: 0.7; fill: #0055AA; }
  .weld-txt { font: 600 5.5px 'Courier New', monospace; fill: #0055AA; }
  .weld-tail { stroke: #0055AA; stroke-width: 0.6; fill: none; }
  .weld-circ { stroke: #0055AA; stroke-width: 0.7; fill: none; }
  .weld-leader { stroke: #0055AA; stroke-width: 0.6; fill: none; }

  /* ── Hover / tooltip ── */
  .hover-part { cursor: pointer; }
  .hover-part:hover { filter: drop-shadow(0 0 5px rgba(246,174,45,0.6)); }
  .tip {
    position: fixed; background: #1E293B; color: #F1F5F9;
    border: 1px solid #F6AE2D; border-radius: 8px; padding: 10px 14px;
    font-size: 0.78rem; pointer-events: none; z-index: 100; max-width: 300px; display: none;
    box-shadow: 0 4px 16px rgba(0,0,0,0.5);
  }
  .tip b { color: #F6AE2D; }
  .tip .r { display: flex; justify-content: space-between; gap: 12px; padding: 1px 0; }
  .tip .k { color: #94A3B8; } .tip .v { font-weight: 600; }

  /* ── BOM side panel ── */
  .bom { position: fixed; right: -400px; top: 0; bottom: 0; width: 380px;
    background: #1E293B; border-left: 2px solid #F6AE2D; z-index: 50;
    transition: right 0.3s; padding: 20px; overflow-y: auto; }
  .bom.open { right: 0; }
  .bom h2 { color: #F6AE2D; font-size: 1rem; margin-bottom: 12px; }
  .bom table { width: 100%; border-collapse: collapse; font-size: 0.75rem; }
  .bom th { background: #334155; color: #F6AE2D; padding: 5px 6px; text-align: left; }
  .bom td { padding: 4px 6px; border-bottom: 1px solid #334155; color: #CBD5E1; }
  .bom-x { position: absolute; top: 10px; right: 12px; background: none; border: none; color: #94A3B8; font-size: 1.2rem; cursor: pointer; }

  /* ── Footer stats bar ── */
  .foot { display: flex; gap: 20px; padding: 8px 20px; background: #1E293B;
    border-top: 1px solid #334155; font-size: 0.75rem; color: #94A3B8; flex-wrap: wrap; }
  .foot .s { color: #F6AE2D; font-weight: 600; }

  /* ── Settings panel ── */
  .settings-panel { position: fixed; left: -380px; top: 0; bottom: 0; width: 360px;
    background: #1E293B; border-right: 2px solid #F6AE2D; z-index: 50;
    transition: left 0.3s; padding: 20px; overflow-y: auto; }
  .settings-panel.open { left: 0; }
  .settings-panel h2 { color: #F6AE2D; font-size: 1rem; margin-bottom: 12px; }
  .settings-panel label { display: block; color: #94A3B8; font-size: 0.75rem; margin-top: 10px; }
  .settings-panel input { width: 100%; background: #334155; color: #F1F5F9; border: 1px solid #475569;
    border-radius: 5px; padding: 6px 8px; font-size: 0.8rem; margin-top: 4px; }
  .settings-x { position: absolute; top: 10px; right: 12px; background: none; border: none; color: #94A3B8; font-size: 1.2rem; cursor: pointer; }

  /* ── Modal / approval ── */
  .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.7); z-index: 200; display: none;
    align-items: center; justify-content: center; }
  .modal-overlay.show { display: flex; }
  .modal-box { background: #1E293B; border: 2px solid #F6AE2D; border-radius: 12px;
    padding: 28px 32px; max-width: 440px; width: 90%; text-align: center; }
  .modal-box h3 { color: #F6AE2D; font-size: 1.1rem; margin-bottom: 12px; }
  .modal-box p { color: #CBD5E1; font-size: 0.85rem; line-height: 1.5; margin-bottom: 16px; }
  .modal-box .warn { color: #EF4444; font-weight: 700; font-size: 0.8rem; margin-bottom: 16px; }
  .modal-btns { display: flex; gap: 12px; justify-content: center; }
  .modal-btns button { padding: 8px 20px; border-radius: 6px; font-size: 0.85rem; cursor: pointer; border: none; font-weight: 600; }
  .modal-btns .ok { background: #F6AE2D; color: #0F172A; }
  .modal-btns .cancel { background: #475569; color: #F1F5F9; }

  /* ── Export modal ── */
  .export-modal {
    display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6);
    z-index: 9999; justify-content: center; align-items: center;
  }
  .export-modal.show { display: flex; }
  .export-modal-content {
    background: #1E293B; border: 1px solid #475569; border-radius: 10px;
    padding: 20px; width: 600px; max-height: 80vh; display: flex; flex-direction: column; gap: 12px;
  }
  .export-modal-content h3 { color: #F6AE2D; margin: 0; }
  .export-modal-content textarea {
    background: #0F172A; color: #93C5FD; border: 1px solid #475569; border-radius: 6px;
    font: 12px 'Courier New', monospace; padding: 10px; height: 300px; resize: vertical;
  }
  .export-modal-content .modal-btns { display: flex; gap: 8px; justify-content: flex-end; }
  .export-modal-content .modal-btns button {
    padding: 6px 16px; border-radius: 5px; font-size: 0.8rem; cursor: pointer; border: none;
  }
  .btn-copy { background: #F6AE2D; color: #0F172A; font-weight: 700; }
  .btn-close-modal { background: #334155; color: #94A3B8; }

  /* ── Annotation styles ── */
  .anno-group { cursor: default; }
  .anno-mode .anno-group { cursor: grab; }
  .anno-group .anno-bg { fill: #FFFDE7; fill-opacity: 0; stroke: none; }
  .anno-mode .anno-group .anno-bg { fill-opacity: 0.7; stroke: #F6AE2D; stroke-width: 0.5; rx: 2; }
  .anno-mode .anno-group:hover .anno-bg { fill-opacity: 0.85; stroke: #F6AE2D; stroke-width: 1; }
  .anno-group.anno-selected .anno-bg { fill-opacity: 0.9; stroke: #E53E3E; stroke-width: 1.5; }
  .anno-group.anno-dragging { cursor: grabbing; opacity: 0.7; }
  .anno-hint { font: 600 6px Arial, sans-serif; fill: #E53E3E; }
  .anno-count-badge {
    background: #F6AE2D; color: #0F172A; font-size: 0.65rem; font-weight: 700;
    padding: 1px 5px; border-radius: 8px; margin-left: 4px;
  }

  /* ── Print media ── */
  @media print {
    @page { size: landscape; margin: 0.25in; }
    .top-bar, .foot, .tip, .bom, .modal-overlay, .settings-panel,
    .anno-count-badge { display: none !important; }
    html, body { margin: 0; padding: 0; background: #FFF; width: 100%; height: 100%; overflow: hidden; }
    .canvas-wrap { padding: 0; margin: 0; display: flex; align-items: center; justify-content: center;
                   width: 100%; height: 100%; }
    .drawing-sheet { box-shadow: none; width: 100%; height: auto; max-height: 100vh;
                     page-break-inside: avoid; break-inside: avoid; }
    .drawing-sheet svg { width: 100%; height: auto; max-height: 100vh; }
  }
"""

# ═══════════════════════════════════════════════════════════════════════════════
# 2.  DRAWING_JS_UTILS — Shared JavaScript SVG helper functions
#     Mirrors rafter_drawing.py lines 580-656
# ═══════════════════════════════════════════════════════════════════════════════

DRAWING_JS_UTILS = r"""
// ── SVG namespace & element helpers ──
const NS = 'http://www.w3.org/2000/svg';

function $e(tag, a, txt) {
  const e = document.createElementNS(NS, tag);
  if (a) Object.entries(a).forEach(([k,v]) => e.setAttribute(k,v));
  if (txt) e.textContent = txt;
  return e;
}

function $g(cls, dp) {
  const g = $e('g', {class: cls || ''});
  if (dp) g.dataset.part = dp;
  return g;
}

function $l(x1,y1,x2,y2,c) { return $e('line',{x1,y1,x2,y2,class:c||'obj med'}); }
function $r(x,y,w,h,c) { return $e('rect',{x,y,width:w,height:h,class:c||'obj thick'}); }
function $c(cx,cy,r,c) { return $e('circle',{cx,cy,r,class:c||'bolt'}); }
function $t(x,y,s,c,a) { const t=$e('text',{x,y,class:c||'lbl'},s); if(a)t.setAttribute('text-anchor',a); return t; }
function $p(d,c) { return $e('path',{d,class:c||'obj med'}); }

// ── Format scale for print ──
function fmtScale(pxPerRealIn) {
  var paperInchPx = 100;
  var realInPerPaperIn = paperInchPx / pxPerRealIn;
  var realFt = realInPerPaperIn / 12;
  var rounded = Math.round(realFt * 2) / 2;
  if (rounded < 1) {
    var ri = Math.round(realInPerPaperIn);
    return '1" = ' + ri + '"';
  }
  var ft = Math.floor(rounded);
  var frac = rounded - ft;
  if (frac >= 0.4) return '1" = ' + ft + "'-6\"";
  return '1" = ' + ft + "'-0\"";
}

// ── Format inches as ft-in with 1/8 fractions ──
function fmtFtIn(inches) {
  if (inches < 0) inches = 0;
  const ft = Math.floor(inches / 12);
  let inc = inches - ft * 12;
  const e8 = Math.round(inc * 8) / 8;
  if (e8 >= 12) return (ft+1) + "'-0\"";
  if (e8 === Math.floor(e8)) return ft + "'-" + Math.floor(e8) + "\"";
  const w = Math.floor(e8);
  let n = Math.round((e8 - w) * 8), dd = 8;
  while (n%2===0 && dd>1) { n/=2; dd/=2; }
  return w ? ft + "'-" + w + " " + n + "/" + dd + "\"" : ft + "'-" + n + "/" + dd + "\"";
}

// ── Format decimal ──
function fmtDec(val, places) {
  if (places === undefined) places = 2;
  return Number(val).toFixed(places);
}

// ── Horizontal dimension line with tick marks and centred label ──
function dimH(svg, x1, x2, y, off, label) {
  const dy = y + off;
  svg.appendChild($l(x1,y,x1,dy+(off>0?-2:2),'dim'));
  svg.appendChild($l(x2,y,x2,dy+(off>0?-2:2),'dim'));
  svg.appendChild($l(x1,dy,x2,dy,'dim'));
  svg.appendChild($l(x1-1.5,dy-1.5,x1+1.5,dy+1.5,'dim'));
  svg.appendChild($l(x2-1.5,dy-1.5,x2+1.5,dy+1.5,'dim'));
  svg.appendChild($t((x1+x2)/2, dy-3, label, 'dimtxt', 'middle'));
}

// ── Vertical dimension line with rotated label ──
function dimV(svg, x, y1, y2, off, label) {
  const dx = x + off;
  svg.appendChild($l(x,y1,dx+(off>0?-2:2),y1,'dim'));
  svg.appendChild($l(x,y2,dx+(off>0?-2:2),y2,'dim'));
  svg.appendChild($l(dx,y1,dx,y2,'dim'));
  svg.appendChild($l(dx-1.5,y1-1.5,dx+1.5,y1+1.5,'dim'));
  svg.appendChild($l(dx-1.5,y2-1.5,dx+1.5,y2+1.5,'dim'));
  const t = $t(dx+(off>0?4:-4), (y1+y2)/2+3, label, 'dimtxt', 'middle');
  t.setAttribute('transform', 'rotate(-90,'+(dx+(off>0?4:-4))+','+((y1+y2)/2+3)+')');
  svg.appendChild(t);
}
"""

# ═══════════════════════════════════════════════════════════════════════════════
# 3.  SAVE_PDF_JS(drawing_type, config_var) — Parameterised Save-PDF function
#     Mirrors rafter_drawing.py lines 4002-4081
# ═══════════════════════════════════════════════════════════════════════════════

def SAVE_PDF_JS(drawing_type: str, config_var: str) -> str:
    """Return the savePdfToProject() JS function, parameterised for the
    specific drawing type and config variable."""
    dt_upper = drawing_type.upper()
    return r"""
// ── Save PDF to project (jsPDF + svg2pdf.js) ──
function savePdfToProject() {
  var btn = document.getElementById('btnSavePdf');
  var status = document.getElementById('savePdfStatus');
  var jobCode = (window.%(config_var)s && window.%(config_var)s.job_code) || '{{JOB_CODE}}';
  if (!jobCode || jobCode === 'null') {
    alert('No project job code \u2014 open this drawing from a project to save.');
    return;
  }
  btn.disabled = true;
  btn.textContent = 'Generating...';
  status.textContent = '';

  try {
    var svgEl = document.getElementById('svg');
    var vb = svgEl.viewBox.baseVal;
    var svgW = vb.width || 1100;
    var svgH = vb.height || 850;

    var pdfW = svgW + 40;
    var pdfH = svgH + 80;
    var pdf = new jspdf.jsPDF({
      orientation: 'landscape',
      unit: 'pt',
      format: [pdfW, pdfH]
    });

    // ── Branded Header ──
    pdf.setFontSize(14);
    pdf.setFont('helvetica', 'bold');
    pdf.setTextColor(30, 64, 175);
    pdf.text('TITAN CARPORTS', 20, 22);
    pdf.setFontSize(7);
    pdf.setFont('helvetica', 'normal');
    pdf.setTextColor(150, 150, 150);
    pdf.text('Quality Steel Structures  |  710 Honea Egypt Rd, Conroe, TX 77385  |  (303) 909-5698  |  www.titancarports.com', 20, 32);
    // Title block info on right
    var drawingTitle = '%(dt_upper)s SHOP DRAWING';
    pdf.setFontSize(10);
    pdf.setFont('helvetica', 'bold');
    pdf.setTextColor(31, 78, 121);
    pdf.text(drawingTitle, pdfW - 20, 18, {align: 'right'});
    pdf.setFontSize(8);
    pdf.setFont('helvetica', 'normal');
    pdf.text('Job: ' + jobCode + '  |  Date: ' + new Date().toLocaleDateString(), pdfW - 20, 28, {align: 'right'});
    // Header line
    pdf.setDrawColor(192, 0, 0);
    pdf.setLineWidth(1.5);
    pdf.line(20, 36, pdfW - 20, 36);

    svg2pdf.svg2pdf(svgEl, pdf, { x: 20, y: 42, width: svgW, height: svgH }).then(function() {
      // ── Branded Footer ──
      var footY = pdfH - 16;
      pdf.setDrawColor(192, 0, 0);
      pdf.setLineWidth(0.5);
      pdf.line(20, footY - 8, pdfW - 20, footY - 8);
      pdf.setFontSize(6);
      pdf.setFont('helvetica', 'normal');
      pdf.setTextColor(140, 140, 140);
      pdf.text('Titan Carports — Quality Steel Structures  |  www.titancarports.com  |  Page 1 of 1', pdfW / 2, footY, {align: 'center'});
      var pdfData = pdf.output('arraybuffer');
      var blob = new Blob([pdfData], { type: 'application/pdf' });

      var formData = new FormData();
      formData.append('job_code', jobCode);
      formData.append('drawing_type', '%(drawing_type)s');
      formData.append('source', 'interactive');
      formData.append('pdf_file', blob, jobCode + '_%(dt_upper)s_INTERACTIVE.pdf');

      fetch('/api/shop-drawings/save-interactive-pdf', {
        method: 'POST',
        body: formData
      })
      .then(function(r) { return r.json(); })
      .then(function(data) {
        if (data.ok) {
          btn.textContent = 'Saved!';
          btn.style.background = '#059669';
          status.textContent = 'PDF saved to project';
          status.style.color = '#10B981';
          setTimeout(function() {
            btn.textContent = 'Save PDF to Project';
            btn.disabled = false;
            btn.style.background = '#F6AE2D';
          }, 3000);
        } else {
          btn.textContent = 'Save PDF to Project';
          btn.disabled = false;
          status.textContent = 'Error: ' + (data.error || 'unknown');
          status.style.color = '#EF4444';
        }
      })
      .catch(function(err) {
        btn.textContent = 'Save PDF to Project';
        btn.disabled = false;
        status.textContent = 'Network error';
        status.style.color = '#EF4444';
      });
    }).catch(function(err) {
      btn.textContent = 'Save PDF to Project';
      btn.disabled = false;
      status.textContent = 'PDF render error: ' + err.message;
      status.style.color = '#EF4444';
    });
  } catch(err) {
    btn.textContent = 'Save PDF to Project';
    btn.disabled = false;
    status.textContent = 'Error: ' + err.message;
    status.style.color = '#EF4444';
  }
}
""" % {
        "config_var": config_var,
        "drawing_type": drawing_type,
        "dt_upper": dt_upper,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 4.  build_title_block_js() — Zone 5 title block (y=680 to y=815)
#     Mirrors rafter_drawing.py lines 2474-2548
# ═══════════════════════════════════════════════════════════════════════════════

def build_title_block_js() -> str:
    """Return a JS function ``drawTitleBlock(svg, opts)`` that draws the
    standard title block in Zone 5 of the SVG.

    ``opts`` is an object with keys:
        projName, customer, jobNum, drawingNum, drawnBy, surfPrep,
        drawingTitle, partMark, projectNotes (array of strings),
        revision (int), revHistory (array of {date, rev, desc, by})
    """
    return r"""
// ── Standard Title Block — Zone 5 (y=680..815) ──
function drawTitleBlock(svg, opts) {
  var ty = 680, th = 135, tx = 20, tw = 1060;
  svg.appendChild($r(tx, ty, tw, th, 'obj thick'));

  // Column dividers
  var c1 = tx, c2 = tx + 220, c3 = c2 + 240, c4 = c3 + 160, c5 = c4 + 200;
  [c2, c3, c4, c5].forEach(function(cx) {
    svg.appendChild($l(cx, ty, cx, ty + th, 'obj med'));
  });

  // ── Col 1: Company info + design authority ──
  svg.appendChild($t(c1 + 110, ty + 16, 'Titan Carports', 'lblb', 'middle'));
  svg.appendChild($t(c1 + 110, ty + 28, 'Quality Steel Structures', 'note', 'middle'));
  svg.appendChild($t(c1 + 110, ty + 40, '710 Honea Egypt Rd', 'lbl', 'middle'));
  svg.appendChild($t(c1 + 110, ty + 50, 'Conroe, TX 77385', 'lbl', 'middle'));
  svg.appendChild($t(c1 + 110, ty + 60, '(303) 909-5698 | www.titancarports.com', 'note', 'middle'));
  svg.appendChild($l(c1, ty + 68, c2, ty + 68, 'obj hair'));
  svg.appendChild($t(c1 + 8, ty + 80, 'DESIGN/REVIEW AUTHORITY:', 'noteb'));
  svg.appendChild($t(c1 + 8, ty + 92, 'PLEASE REVIEW THIS DRAWING CAREFULLY', 'note'));
  svg.appendChild($t(c1 + 8, ty + 102, 'We assume NO responsibility for the accuracy', 'note'));
  svg.appendChild($t(c1 + 8, ty + 112, 'of information in the contract documents.', 'note'));

  // ── Col 2: Project rows ──
  var pRows = [
    ['PROJECT:', opts.projName  || ''],
    ['CUSTOMER:', opts.customer  || ''],
    ['JOB:',     opts.jobNum    || ''],
    ['DWG #:',   opts.drawingNum || ''],
    ['DATE:',    new Date().toLocaleDateString()],
    ['DRAWN:',   opts.drawnBy   || 'AUTO'],
    ['CHECKED:', opts.checkedBy || '\u2014'],
    ['SHEET:',   '1 OF 1'],
    ['REV:',     String(opts.revision || 0)]
  ];
  pRows.forEach(function(pair, i) {
    var py = ty + 12 + i * 13;
    svg.appendChild($t(c2 + 6, py, pair[0], 'note'));
    svg.appendChild($t(c2 + 55, py, pair[1], 'lbl'));
    if (i < pRows.length - 1) svg.appendChild($l(c2, py + 3, c3, py + 3, 'dim'));
  });

  // ── Col 3: Drawing title + part mark ──
  svg.appendChild($t(c3 + 80, ty + 45, opts.drawingTitle || '', 'ttl'));
  var markEl = $e('text', {x: c3 + 80, y: ty + 85, class: 'ttl', 'text-anchor': 'middle', 'font-size': '28px'}, opts.partMark || '');
  svg.appendChild(markEl);

  // ── Col 4: Revision history table ──
  svg.appendChild($e('rect', {x: c4, y: ty, width: 200, height: 16, fill: '#333', stroke: '#333'}));
  var hdrTexts = [
    $t(c4 + 8, ty + 12, 'DATE', 'note'),
    $t(c4 + 50, ty + 12, 'REV', 'note'),
    $t(c4 + 80, ty + 12, 'DESCRIPTION', 'note')
  ];
  hdrTexts.forEach(function(el) { el.setAttribute('fill', '#FFF'); svg.appendChild(el); });

  var hist = opts.revHistory || [];
  hist.forEach(function(h, i) {
    var ry2 = ty + 16 + 14 * (i + 1);
    svg.appendChild($t(c4 + 8, ry2, h.date || '', 'note'));
    svg.appendChild($t(c4 + 52, ry2, String(h.rev || ''), 'note'));
    svg.appendChild($t(c4 + 80, ry2, (h.desc || '') + (h.by ? ' \u2014 ' + h.by : ''), 'note'));
  });

  // ── Col 5: Project notes / weld schedule ──
  svg.appendChild($e('rect', {x: c5, y: ty, width: tw - (c5 - tx), height: 16, fill: '#333', stroke: '#333'}));
  var notesHdr = $t(c5 + (tw - (c5 - tx)) / 2, ty + 12, 'PROJECT NOTES', 'note', 'middle');
  notesHdr.setAttribute('fill', '#FFF');
  svg.appendChild(notesHdr);

  var notes = opts.projectNotes || [];
  notes.forEach(function(n, i) {
    svg.appendChild($t(c5 + 6, ty + 26 + i * 8, n, 'note'));
  });

  // Drawing title above title block
  if (opts.drawingTitle && opts.partMark) {
    svg.appendChild($t(480, ty - 8, opts.drawingTitle + ' - ' + opts.partMark, 'ttl'));
  }
}
"""


# ═══════════════════════════════════════════════════════════════════════════════
# 5.  build_bom_table_js() — BOM side-panel population
#     Mirrors rafter_drawing.py lines 2705-2830
# ═══════════════════════════════════════════════════════════════════════════════

def build_bom_table_js() -> str:
    """Return a JS function ``updateBOM(rows)`` that populates the BOM side
    panel.  ``rows`` is an array of {mk, qty, desc, size, mat, wt}."""
    return r"""
// ── Populate BOM side panel ──
function updateBOM(rows) {
  var tb = document.getElementById('bomTB');
  if (!tb) return;
  tb.innerHTML = '';

  var totalWt = 0;
  rows.forEach(function(r) {
    var tr = document.createElement('tr');
    tr.innerHTML = '<td>' + (r.mk || '') + '</td>' +
                   '<td>' + (r.qty || 0) + '</td>' +
                   '<td>' + (r.desc || '') + '</td>' +
                   '<td>' + (r.size || '') + '</td>' +
                   '<td>' + (r.mat || '') + '</td>' +
                   '<td>' + (r.wt || 0) + ' lbs</td>';
    tb.appendChild(tr);
    totalWt += (r.wt || 0);
  });

  // Total row
  var tr = document.createElement('tr');
  tr.style.fontWeight = 'bold';
  tr.style.borderTop = '1px solid #64748B';
  tr.innerHTML = '<td colspan="5" style="text-align:right;">TOTAL WEIGHT:</td><td>' + totalWt + ' lbs</td>';
  tb.appendChild(tr);

  var totalEl = document.getElementById('bomTotal');
  if (totalEl) totalEl.textContent = totalWt.toLocaleString() + ' lbs';
}
"""


# ═══════════════════════════════════════════════════════════════════════════════
# 6.  build_html_shell() — Assemble the complete HTML page
# ═══════════════════════════════════════════════════════════════════════════════

def build_html_shell(
    title: str,
    drawing_type: str,
    config_var: str,
    controls_html: str,
    footer_html: str,
    drawing_js: str,
) -> str:
    """Assemble a complete interactive shop-drawing HTML page.

    Parameters
    ----------
    title : str
        Page title shown in the browser tab and top-bar heading
        (e.g. "Purlin Shop Drawing").
    drawing_type : str
        Identifier used when saving PDFs (e.g. "purlin").
    config_var : str
        Name of the ``window`` config variable injected by the server
        (e.g. "PURLIN_CONFIG").
    controls_html : str
        Raw HTML for the control widgets specific to this drawing,
        inserted inside ``<div class="controls">...</div>``.
    footer_html : str
        Raw HTML for the footer stats specific to this drawing,
        inserted inside ``<div class="foot">...</div>``.
    drawing_js : str
        The component-specific JavaScript that implements the ``draw()``
        function and any helpers.  This block is emitted inside a
        ``<script>`` tag after the shared utilities.

    Returns
    -------
    str
        A complete HTML document string with ``{{CONFIG_JSON}}`` and
        ``{{JOB_CODE}}`` placeholders for server-side injection.
    """

    config_json_placeholder = "{{" + config_var + "_JSON}}"
    job_code_placeholder = "{{JOB_CODE}}"

    save_pdf_js = SAVE_PDF_JS(drawing_type, config_var)
    title_block_js = build_title_block_js()
    bom_table_js = build_bom_table_js()

    return r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TitanForge — %(title)s</title>
<style>
%(css)s
</style>
<script>window.%(config_var)s = %(config_json_ph)s;</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/svg2pdf.js/2.2.3/svg2pdf.umd.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script>
// ── svg2pdf compatibility shim ──────────────────────────────
(function() {
  if (window.jspdf && !window.jspdf.jsPDF.prototype.svg) {
    var s = document.createElement('script');
    s.src = 'https://cdn.jsdelivr.net/npm/svg2pdf.js@2.2.3/dist/svg2pdf.umd.min.js';
    document.head.appendChild(s);
  }
  if (typeof window.svg2pdf === 'undefined' || !window.svg2pdf.svg2pdf) {
    window.svg2pdf = window.svg2pdf || {};
    window.svg2pdf.svg2pdf = function(svgElement, pdfDoc, options) {
      if (typeof pdfDoc.svg === 'function') {
        return pdfDoc.svg(svgElement, options);
      }
      return new Promise(function(resolve, reject) {
        try {
          var serializer = new XMLSerializer();
          var svgString = serializer.serializeToString(svgElement);
          var canvas = document.createElement('canvas');
          var scale = 2;
          canvas.width = (options.width || 1100) * scale;
          canvas.height = (options.height || 850) * scale;
          var ctx = canvas.getContext('2d');
          ctx.fillStyle = '#FFFFFF';
          ctx.fillRect(0, 0, canvas.width, canvas.height);
          ctx.scale(scale, scale);
          var img = new Image();
          var blob = new Blob([svgString], {type:'image/svg+xml;charset=utf-8'});
          var url = URL.createObjectURL(blob);
          img.onload = function() {
            ctx.drawImage(img, 0, 0, options.width || 1100, options.height || 850);
            URL.revokeObjectURL(url);
            var imgData = canvas.toDataURL('image/png');
            pdfDoc.addImage(imgData, 'PNG', options.x||0, options.y||0,
              options.width||1100, options.height||850);
            resolve();
          };
          img.onerror = function() { URL.revokeObjectURL(url); reject(new Error('SVG render failed')); };
          img.src = url;
        } catch(e) { reject(e); }
      });
    };
  }
})();
</script>
</head>
<body>

<!-- TOP BAR -->
<div class="top-bar">
  <div style="display:flex;align-items:center;gap:12px;">
    <a class="back-link" href="/shop-drawings/%(job_code_ph)s">Back</a>
    <h1>%(title)s</h1>
    <span class="job-code-label" id="jobLabel">%(drawing_type_upper)s</span>
  </div>
  <div class="controls">
%(controls_html)s
    <button class="btn-gold" id="btnSavePdf" onclick="savePdfToProject()">Save PDF to Project</button>
    <span id="savePdfStatus" style="font-size:0.7rem;margin-left:4px;"></span>
    <button class="toggle-btn" onclick="document.getElementById('bomPanel').classList.toggle('open')">BOM</button>
    <button class="toggle-btn" onclick="document.getElementById('settingsPanel').classList.toggle('open')">Settings</button>
  </div>
</div>

<!-- CANVAS -->
<div class="canvas-wrap">
  <div class="drawing-sheet">
    <svg id="svg" viewBox="0 0 1100 850" xmlns="http://www.w3.org/2000/svg"></svg>
  </div>
</div>

<!-- FOOTER -->
<div class="foot">
%(footer_html)s
</div>

<!-- BOM SIDE PANEL -->
<div class="bom" id="bomPanel">
  <button class="bom-x" onclick="this.parentElement.classList.remove('open')">&#10005;</button>
  <h2>Bill of Materials</h2>
  <table>
    <thead>
      <tr><th>Mk</th><th>Qty</th><th>Description</th><th>Size</th><th>Material</th><th>Weight</th></tr>
    </thead>
    <tbody id="bomTB"></tbody>
  </table>
  <div style="margin-top:12px;padding:8px;background:#334155;border-radius:6px;text-align:right;">
    <span style="color:#94A3B8;">Total:</span> <strong style="color:#F6AE2D;" id="bomTotal">--</strong>
  </div>
</div>

<!-- TOOLTIP -->
<div class="tip" id="tip"></div>

<!-- SETTINGS PANEL -->
<div class="settings-panel" id="settingsPanel">
  <button class="settings-x" onclick="this.parentElement.classList.remove('open')">&#10005;</button>
  <h2>Project Settings</h2>
  <label>Project Name
    <input type="text" id="setProjectName" value="PROJECT" onchange="draw()">
  </label>
  <label>Customer
    <input type="text" id="setCustomer" value="Customer Name" onchange="draw()">
  </label>
  <label>Job Number
    <input type="text" id="setJobNumber" value="JOB-2026-001" onchange="draw()">
  </label>
  <label>Drawn By
    <input type="text" id="setDrawnBy" value="AUTO" onchange="draw()">
  </label>
  <label>Drawing Number
    <input type="text" id="setDrawingNum" value="SD-001" onchange="draw()">
  </label>
  <label>Surface Prep
    <input type="text" id="setSurfPrep" value="SSPC-SP2" onchange="draw()">
  </label>
</div>

<script>
// ── Server-injected project config ──
window.%(config_var)s = window.%(config_var)s || null;

%(js_utils)s

%(title_block_js)s

%(bom_table_js)s

%(save_pdf_js)s

// ═══════════════════════════════════════════════
// Component-specific drawing code
// ═══════════════════════════════════════════════

%(drawing_js)s

// ── Init on DOM ready ──
document.addEventListener('DOMContentLoaded', function() {
  // Apply server config if present
  var cfg = window.%(config_var)s;
  if (cfg) {
    if (cfg.project_name) { var el = document.getElementById('setProjectName'); if (el) el.value = cfg.project_name; }
    if (cfg.customer) { var el = document.getElementById('setCustomer'); if (el) el.value = cfg.customer; }
    if (cfg.job_code) {
      var el = document.getElementById('setJobNumber'); if (el) el.value = cfg.job_code;
      var lbl = document.getElementById('jobLabel'); if (lbl) lbl.textContent = cfg.job_code;
    }
    if (cfg.drawn_by) { var el = document.getElementById('setDrawnBy'); if (el) el.value = cfg.drawn_by; }
    if (cfg.drawing_num) { var el = document.getElementById('setDrawingNum'); if (el) el.value = cfg.drawing_num; }
    if (cfg.surface_prep) { var el = document.getElementById('setSurfPrep'); if (el) el.value = cfg.surface_prep; }
    // Let component-specific init handle remaining config
    if (typeof applyComponentConfig === 'function') applyComponentConfig(cfg);
  }
  if (typeof draw === 'function') draw();
});
</script>
</body>
</html>""" % {
        "title": title,
        "css": DRAWING_CSS,
        "config_var": config_var,
        "config_json_ph": config_json_placeholder,
        "job_code_ph": job_code_placeholder,
        "drawing_type": drawing_type,
        "drawing_type_upper": drawing_type.upper(),
        "controls_html": controls_html,
        "footer_html": footer_html,
        "js_utils": DRAWING_JS_UTILS,
        "title_block_js": title_block_js,
        "bom_table_js": bom_table_js,
        "save_pdf_js": save_pdf_js,
        "drawing_js": drawing_js,
    }
