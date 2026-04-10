"""
TitanForge — QA/QC Hub Page
==============================
Central landing page for all quality assurance and quality control documentation.
Covers AISC certification requirements, WPS library, welder certs, procedures,
NCR log, calibration records, and audit readiness status.
"""

QA_HUB_HTML = """
<style>
  .qa-page { padding: 24px; max-width: 1200px; }
  .qa-hero {
    background: linear-gradient(135deg, #111827, #1E293B);
    border-radius: 14px; padding: 32px; margin-bottom: 24px;
    border: 1px solid #1E293B;
  }
  .qa-hero h1 { font-size: 26px; font-weight: 800; color: #FFF; margin-bottom: 6px; }
  .qa-hero h1 span { color: #C89A2E; }
  .qa-hero .sub { font-size: 14px; color: #94A3B8; max-width: 700px; line-height: 1.6; }

  /* Audit readiness bar */
  .audit-bar {
    display: flex; gap: 16px; margin: 20px 0 0;
    flex-wrap: wrap;
  }
  .audit-stat {
    background: #0F172A; border-radius: 10px; padding: 14px 20px;
    border: 1px solid #1E293B; min-width: 140px; flex: 1;
  }
  .audit-stat .as-val { font-size: 28px; font-weight: 800; color: #FFF; }
  .audit-stat .as-val.green { color: #10B981; }
  .audit-stat .as-val.amber { color: #F59E0B; }
  .audit-stat .as-val.red { color: #DC2626; }
  .audit-stat .as-lbl { font-size: 11px; color: #64748B; text-transform: uppercase;
    letter-spacing: 0.5px; margin-top: 2px; }

  /* Section cards grid */
  .qa-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 16px; margin-bottom: 32px;
  }
  .qa-card {
    background: #111827; border: 1px solid #1E293B; border-radius: 12px;
    padding: 24px; transition: all 0.2s; cursor: pointer;
    text-decoration: none; color: inherit; display: block;
  }
  .qa-card:hover { border-color: #334155; background: #1A2332; transform: translateY(-2px); }
  .qa-card .qc-icon {
    width: 48px; height: 48px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 24px; margin-bottom: 14px;
  }
  .qa-card .qc-icon.blue { background: #1E3A5F; }
  .qa-card .qc-icon.green { background: #14532D; }
  .qa-card .qc-icon.amber { background: #78350F; }
  .qa-card .qc-icon.red { background: #7F1D1D; }
  .qa-card .qc-icon.purple { background: #3B0764; }
  .qa-card .qc-icon.gray { background: #1E293B; }
  .qa-card h3 { font-size: 16px; font-weight: 700; color: #FFF; margin-bottom: 6px; }
  .qa-card p { font-size: 13px; color: #94A3B8; line-height: 1.5; margin-bottom: 12px; }
  .qa-card .qc-status {
    display: flex; align-items: center; gap: 6px;
    font-size: 12px; font-weight: 600;
  }
  .qa-card .qc-dot { width: 8px; height: 8px; border-radius: 50%; }
  .qa-card .qc-dot.green { background: #10B981; }
  .qa-card .qc-dot.amber { background: #F59E0B; }
  .qa-card .qc-dot.red { background: #DC2626; }
  .qa-card .qc-status-text.green { color: #10B981; }
  .qa-card .qc-status-text.amber { color: #F59E0B; }
  .qa-card .qc-status-text.red { color: #DC2626; }

  /* AISC Checklist */
  .aisc-section {
    background: #111827; border: 1px solid #1E293B; border-radius: 12px;
    padding: 24px; margin-bottom: 24px;
  }
  .aisc-section h2 {
    font-size: 18px; color: #FFF; margin-bottom: 4px;
    display: flex; align-items: center; gap: 10px;
  }
  .aisc-section .aisc-sub { font-size: 13px; color: #64748B; margin-bottom: 16px; }

  .aisc-checklist { list-style: none; }
  .aisc-checklist li {
    display: flex; align-items: flex-start; gap: 12px;
    padding: 12px 0; border-bottom: 1px solid #1E293B;
    font-size: 14px;
  }
  .aisc-checklist li:last-child { border-bottom: none; }
  .aisc-check {
    width: 22px; height: 22px; border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; flex-shrink: 0; margin-top: 2px;
  }
  .aisc-check.done { background: #14532D; color: #10B981; }
  .aisc-check.partial { background: #78350F; color: #F59E0B; }
  .aisc-check.missing { background: #7F1D1D; color: #DC2626; }
  .aisc-item-text { flex: 1; }
  .aisc-item-text strong { color: #FFF; display: block; }
  .aisc-item-text span { color: #94A3B8; font-size: 12px; }
  .aisc-ref { font-size: 11px; color: #475569; font-style: italic; white-space: nowrap; }
</style>

<div class="qa-page">

  <!-- Hero -->
  <div class="qa-hero">
    <h1>QA / QC <span>Hub</span></h1>
    <p class="sub">
      Central hub for all quality documentation required by AISC, AWS D1.1, and company quality manual.
      Everything an auditor needs — WPS library, welder certifications, inspection records, NCRs,
      traceability, calibration logs, and procedures — all in one place.
    </p>
    <div class="audit-bar" id="auditBar">
      <div class="audit-stat">
        <div class="as-val green" id="abWPS">4</div>
        <div class="as-lbl">Active WPS</div>
      </div>
      <div class="audit-stat">
        <div class="as-val green" id="abWelders">—</div>
        <div class="as-lbl">Certified Welders</div>
      </div>
      <div class="audit-stat">
        <div class="as-val" id="abInspections">—</div>
        <div class="as-lbl">Inspections (30d)</div>
      </div>
      <div class="audit-stat">
        <div class="as-val amber" id="abNCR">—</div>
        <div class="as-lbl">Open NCRs</div>
      </div>
      <div class="audit-stat">
        <div class="as-val" id="abCalib">—</div>
        <div class="as-lbl">Calibrated Tools</div>
      </div>
    </div>
  </div>

  <!-- Main Section Cards -->
  <div class="qa-grid">

    <a href="/qa/wps" class="qa-card">
      <div class="qc-icon amber">&#128293;</div>
      <h3>WPS Library</h3>
      <p>Welding Procedure Specifications for all joint types. Includes WPS-B (stitch welds), WPS-C (clip welds), WPS-D (rebar), and WPS-F (end plates). Each WPS has the qualified parameters, filler metals, shielding gas, and approved ranges.</p>
      <div class="qc-status">
        <div class="qc-dot green"></div>
        <span class="qc-status-text green">4 Active WPS Documents</span>
      </div>
    </a>

    <a href="/qa/welder-certs" class="qa-card">
      <div class="qc-icon blue">&#127891;</div>
      <h3>Welder Certifications</h3>
      <p>Welder qualification records per AWS D1.1. Tracks each welder's test date, qualified positions (1G, 2G, 3G, 4G), process (GMAW, FCAW, SMAW), expiration date, and continuity log. Alerts when certs are expiring.</p>
      <div class="qc-status">
        <div class="qc-dot amber"></div>
        <span class="qc-status-text amber">Check expiration dates</span>
      </div>
    </a>

    <a href="/qa/procedures" class="qa-card">
      <div class="qc-icon green">&#128220;</div>
      <h3>Procedures & Quality Manual</h3>
      <p>All standard operating procedures: receiving inspection, fabrication, welding, NDT, final inspection, material handling, shipping. Plus the company Quality Manual required by AISC Chapter M.</p>
      <div class="qc-status">
        <div class="qc-dot green"></div>
        <span class="qc-status-text green">Quality Manual current</span>
      </div>
    </a>

    <a href="/qa/ncr-log" class="qa-card">
      <div class="qc-icon red">&#9888;</div>
      <h3>NCR Log</h3>
      <p>Non-Conformance Reports — log of all quality deviations. Tracks root cause, corrective action, disposition (rework / accept / reject), and closure. Required for AISC audit trail.</p>
      <div class="qc-status">
        <div class="qc-dot amber"></div>
        <span class="qc-status-text amber" id="ncrStatus">Loading...</span>
      </div>
    </a>

    <a href="/qa/calibration" class="qa-card">
      <div class="qc-icon purple">&#128295;</div>
      <h3>Calibration Log</h3>
      <p>Equipment calibration records for all measuring and testing tools: tape measures, fillet gauges, torque wrenches, MIG wire speed, UT equipment, paint gauges. Tracks cal dates, due dates, and certificates.</p>
      <div class="qc-status">
        <div class="qc-dot green"></div>
        <span class="qc-status-text green">All tools in cal</span>
      </div>
    </a>

    <a href="/inventory/traceability" class="qa-card">
      <div class="qc-icon gray">&#128279;</div>
      <h3>Material Traceability</h3>
      <p>Full chain of custody from mill cert to finished member. Links heat numbers to coils, coils to members, and members to jobs. ASTM material verification and MTR storage.</p>
      <div class="qc-status">
        <div class="qc-dot green"></div>
        <span class="qc-status-text green">Traceability active</span>
      </div>
    </a>

  </div>

  <!-- AISC Certification Checklist -->
  <div class="aisc-section">
    <h2>&#128203; AISC Certification Readiness Checklist</h2>
    <p class="aisc-sub">Requirements per AISC 360 Chapter M, AWS D1.1, and AISC Quality Systems Manual</p>

    <ul class="aisc-checklist">
      <li>
        <div class="aisc-check done">&#10003;</div>
        <div class="aisc-item-text">
          <strong>Quality Manual</strong>
          <span>Written quality management system document covering all fabrication processes</span>
        </div>
        <div class="aisc-ref">AISC 360 Ch. M</div>
      </li>
      <li>
        <div class="aisc-check done">&#10003;</div>
        <div class="aisc-item-text">
          <strong>Welding Procedure Specifications (WPS)</strong>
          <span>Qualified WPS documents for all joint types used in production</span>
        </div>
        <div class="aisc-ref">AWS D1.1 §4</div>
      </li>
      <li>
        <div class="aisc-check done">&#10003;</div>
        <div class="aisc-item-text">
          <strong>Procedure Qualification Records (PQR)</strong>
          <span>Test records backing each WPS — tensile, bend, macro etch results</span>
        </div>
        <div class="aisc-ref">AWS D1.1 §4.8</div>
      </li>
      <li>
        <div class="aisc-check done">&#10003;</div>
        <div class="aisc-item-text">
          <strong>Welder Qualification / Continuity</strong>
          <span>Welder performance qualification tests and 6-month continuity records</span>
        </div>
        <div class="aisc-ref">AWS D1.1 §4.19</div>
      </li>
      <li>
        <div class="aisc-check done">&#10003;</div>
        <div class="aisc-item-text">
          <strong>Material Test Reports (MTRs)</strong>
          <span>Mill certs on file for all steel received, linked to coil inventory</span>
        </div>
        <div class="aisc-ref">AISC 360 §A3.1</div>
      </li>
      <li>
        <div class="aisc-check done">&#10003;</div>
        <div class="aisc-item-text">
          <strong>Material Traceability</strong>
          <span>Heat number tracking from receiving through fabrication to shipping</span>
        </div>
        <div class="aisc-ref">AISC 360 §M5</div>
      </li>
      <li>
        <div class="aisc-check done">&#10003;</div>
        <div class="aisc-item-text">
          <strong>Receiving Inspection Procedure</strong>
          <span>Documented process for inspecting incoming steel: grade, dimensions, certs</span>
        </div>
        <div class="aisc-ref">AISC QM §5.3</div>
      </li>
      <li>
        <div class="aisc-check done">&#10003;</div>
        <div class="aisc-item-text">
          <strong>Visual Weld Inspection</strong>
          <span>In-process and final weld inspection per AWS D1.1 Table 6.1</span>
        </div>
        <div class="aisc-ref">AWS D1.1 §6.9</div>
      </li>
      <li>
        <div class="aisc-check done">&#10003;</div>
        <div class="aisc-item-text">
          <strong>NDT (Ultrasonic) Procedures</strong>
          <span>Non-destructive testing procedures and personnel qualifications</span>
        </div>
        <div class="aisc-ref">AWS D1.1 §6.12</div>
      </li>
      <li>
        <div class="aisc-check done">&#10003;</div>
        <div class="aisc-item-text">
          <strong>Non-Conformance Reporting (NCR)</strong>
          <span>System for documenting, tracking, and resolving quality deviations</span>
        </div>
        <div class="aisc-ref">AISC QM §8.3</div>
      </li>
      <li>
        <div class="aisc-check done">&#10003;</div>
        <div class="aisc-item-text">
          <strong>Calibration Program</strong>
          <span>Records for all measuring and testing equipment calibration</span>
        </div>
        <div class="aisc-ref">AISC QM §7.6</div>
      </li>
      <li>
        <div class="aisc-check done">&#10003;</div>
        <div class="aisc-item-text">
          <strong>Corrective Action Procedure</strong>
          <span>Process for addressing root cause of NCRs and preventing recurrence</span>
        </div>
        <div class="aisc-ref">AISC QM §8.5</div>
      </li>
      <li>
        <div class="aisc-check done">&#10003;</div>
        <div class="aisc-item-text">
          <strong>Document Control</strong>
          <span>Version control and approval process for all quality documents</span>
        </div>
        <div class="aisc-ref">AISC QM §4.2</div>
      </li>
      <li>
        <div class="aisc-check done">&#10003;</div>
        <div class="aisc-item-text">
          <strong>Shop Drawing Control</strong>
          <span>Approval workflow ensuring shop works from current revision drawings</span>
        </div>
        <div class="aisc-ref">AISC 360 §M4</div>
      </li>
      <li>
        <div class="aisc-check done">&#10003;</div>
        <div class="aisc-item-text">
          <strong>Coating / Galvanizing Inspection</strong>
          <span>Inspection of surface prep and cold galvanizing application</span>
        </div>
        <div class="aisc-ref">SSPC / AISC CoP</div>
      </li>
    </ul>
  </div>

</div>

<script>
  // Load QA stats on page load
  (function() {
    // Try to load NCR count
    fetch('/api/qa/stats').then(function(r){return r.json()}).then(function(d) {
      if (d.ok) {
        if (d.open_ncrs !== undefined) {
          document.getElementById('abNCR').textContent = d.open_ncrs;
          document.getElementById('ncrStatus').textContent = d.open_ncrs + ' open NCRs';
        }
        if (d.certified_welders !== undefined)
          document.getElementById('abWelders').textContent = d.certified_welders;
        if (d.inspections_30d !== undefined)
          document.getElementById('abInspections').textContent = d.inspections_30d;
        if (d.calibrated_tools !== undefined)
          document.getElementById('abCalib').textContent = d.calibrated_tools;
      }
    }).catch(function(){});
  })();
</script>
"""
