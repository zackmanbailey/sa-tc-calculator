"""
TitanForge — Getting Started Page
===================================
Role-based onboarding page that shows new users exactly what to do first.
Detects the user's role and presents the right workflow guide.
"""

GETTING_STARTED_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Getting Started — TitanForge</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    background: #0B1120; color: #E2E8F0;
    min-height: 100vh;
  }

  .page-wrap { max-width: 900px; margin: 0 auto; padding: 32px 20px; }

  /* ── Hero ── */
  .hero {
    text-align: center; padding: 40px 20px 32px;
    border-bottom: 2px solid #1E293B; margin-bottom: 32px;
  }
  .hero h1 { font-size: 28px; font-weight: 800; color: #FFF; margin-bottom: 8px; }
  .hero h1 span { color: #C89A2E; }
  .hero .subtitle { font-size: 15px; color: #94A3B8; max-width: 600px; margin: 0 auto; line-height: 1.6; }
  .hero .role-badge {
    display: inline-block; margin-top: 16px; padding: 6px 16px;
    background: #1E40AF; color: #BFDBFE; border-radius: 20px;
    font-size: 13px; font-weight: 600; letter-spacing: 0.5px;
  }

  /* ── Workflow Steps ── */
  .workflow { margin-bottom: 40px; }
  .workflow h2 {
    font-size: 18px; color: #FFF; margin-bottom: 16px;
    display: flex; align-items: center; gap: 10px;
  }
  .workflow h2 .num {
    display: flex; align-items: center; justify-content: center;
    width: 28px; height: 28px; background: #C89A2E; color: #0F172A;
    border-radius: 50%; font-size: 14px; font-weight: 800;
  }

  .step-card {
    background: #111827; border: 1px solid #1E293B; border-radius: 12px;
    padding: 20px; margin-bottom: 12px;
    display: flex; gap: 16px; align-items: flex-start;
    transition: all 0.2s;
  }
  .step-card:hover { border-color: #334155; background: #1A2332; }

  .step-icon {
    width: 48px; height: 48px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px; flex-shrink: 0;
  }
  .step-icon.blue { background: #1E3A5F; }
  .step-icon.green { background: #14532D; }
  .step-icon.amber { background: #78350F; }
  .step-icon.purple { background: #3B0764; }

  .step-body { flex: 1; }
  .step-body h3 { font-size: 15px; font-weight: 700; color: #FFF; margin-bottom: 4px; }
  .step-body p { font-size: 13px; color: #94A3B8; line-height: 1.6; margin-bottom: 8px; }
  .step-body .go-link {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 13px; color: #C89A2E; text-decoration: none; font-weight: 600;
  }
  .step-body .go-link:hover { color: #F59E0B; }

  /* ── Quick Reference Cards ── */
  .ref-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 12px; margin-bottom: 32px;
  }
  .ref-card {
    background: #111827; border: 1px solid #1E293B; border-radius: 10px;
    padding: 16px; transition: all 0.2s;
  }
  .ref-card:hover { border-color: #334155; }
  .ref-card h4 { font-size: 13px; color: #C89A2E; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; }
  .ref-card p { font-size: 13px; color: #94A3B8; line-height: 1.5; }
  .ref-card code { background: #1E293B; padding: 2px 6px; border-radius: 4px; font-size: 12px; color: #CBD5E1; }

  /* ── Status Legend ── */
  .legend { margin-bottom: 32px; }
  .legend h3 { font-size: 14px; color: #64748B; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px; }
  .legend-row {
    display: flex; align-items: center; gap: 10px;
    padding: 8px 0; border-bottom: 1px solid #1E293B;
    font-size: 13px;
  }
  .legend-dot { width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }
  .legend-label { color: #FFF; font-weight: 600; min-width: 120px; }
  .legend-desc { color: #94A3B8; }

  /* ── Tips ── */
  .tip-box {
    background: #1E293B; border-left: 3px solid #C89A2E;
    border-radius: 0 8px 8px 0; padding: 14px 16px;
    margin-bottom: 12px; font-size: 13px; color: #CBD5E1; line-height: 1.6;
  }
  .tip-box strong { color: #C89A2E; }

  /* ── Footer ── */
  .gs-footer {
    text-align: center; padding: 24px; color: #94A3B8; font-size: 12px;
    border-top: 1px solid #1E293B; margin-top: 32px;
  }
  .gs-footer a { color: #C89A2E; text-decoration: none; }

  /* Role selector tabs */
  .role-tabs {
    display: flex; gap: 8px; margin-bottom: 24px;
    flex-wrap: wrap; justify-content: center;
  }
  .role-tab {
    padding: 8px 20px; border-radius: 8px;
    background: #1E293B; border: 1px solid #334155;
    color: #94A3B8; font-size: 13px; font-weight: 600;
    cursor: pointer; transition: all 0.2s;
  }
  .role-tab:hover { border-color: #94A3B8; color: #CBD5E1; }
  .role-tab.active { background: #1E40AF; border-color: #3B82F6; color: #FFF; }

  .role-section { display: none; }
  .role-section.active { display: block; }

/* ── Responsive ── */
@media (max-width: 768px) {
    .page-header h1 { font-size: 22px; }
    .ref-grid { grid-template-columns: 1fr; }
    .role-tabs { overflow-x: auto; -webkit-overflow-scrolling: touch; flex-wrap: nowrap; }
    .role-tab { white-space: nowrap; }
    .step-card { padding: 16px; }
}
@media (max-width: 480px) {
    .ref-grid { grid-template-columns: 1fr; }
    .legend-row { flex-direction: column; gap: 8px; }
}
</style>
</head>
<body>

<div class="page-wrap">

  <!-- Hero -->
  <div class="hero">
    <h1>Welcome to <span>TitanForge</span></h1>
    <p class="subtitle">
      TitanForge is the shop management system for Structures America.
      It handles everything from quoting a building to tracking every piece on the shop floor.
      Here's how to get started based on your role.
    </p>
    <div class="role-badge">Your role: {{USER_ROLE}}</div>
  </div>

  <!-- Role Tabs -->
  <div class="role-tabs">
    <div class="role-tab" data-role="shop" onclick="showRole('shop')">Shop Floor</div>
    <div class="role-tab" data-role="estimator" onclick="showRole('estimator')">Estimator</div>
    <div class="role-tab" data-role="admin" onclick="showRole('admin')">Admin</div>
  </div>

  <!-- ═══════════════════════════════════════════ -->
  <!-- SHOP FLOOR GUIDE -->
  <!-- ═══════════════════════════════════════════ -->
  <div class="role-section" id="role-shop">
    <div class="workflow">
      <h2><span class="num">1</span> Check your work orders</h2>
      <div class="step-card">
        <div class="step-icon blue">📋</div>
        <div class="step-body">
          <h3>Go to Work Orders</h3>
          <p>Work orders tell you what to build. Each one lists the parts (columns, rafters, purlins) for a job, which machine to use, and how many of each. Start here every morning.</p>
          <a class="go-link" href="/shop-floor">Open Shop Floor Dashboard &rarr;</a>
        </div>
      </div>
    </div>

    <div class="workflow">
      <h2><span class="num">2</span> Go to your machine's work station</h2>
      <div class="step-card">
        <div class="step-icon green">🖥️</div>
        <div class="step-body">
          <h3>Open Work Station on your tablet</h3>
          <p>The Work Station page shows items assigned to YOUR machine. Tap your machine name to see what's queued up. Items are sorted by priority — <strong>grab the top one first</strong>.</p>
          <p>Each item has step-by-step instructions. Follow them in order: pull material, align, tack weld, stitch weld, clean, inspect, tag.</p>
        </div>
      </div>
    </div>

    <div class="workflow">
      <h2><span class="num">3</span> Scan QR stickers to track your work</h2>
      <div class="step-card">
        <div class="step-icon amber">📱</div>
        <div class="step-body">
          <h3>Scan START when you begin, FINISH when you're done</h3>
          <p>Every piece has a sticker with a QR code. Open the scanner on your phone, point it at the sticker, and tap START. When you're done with the piece, scan again and tap FINISH. This tracks your time and updates the dashboard.</p>
          <p>You can also type the item ID manually if the QR won't scan.</p>
        </div>
      </div>
    </div>

    <div class="workflow">
      <h2><span class="num">4</span> Watch for alerts and QC checkpoints</h2>
      <div class="step-card">
        <div class="step-icon purple">✅</div>
        <div class="step-body">
          <h3>Don't skip the quality check</h3>
          <p>At certain steps (marked with a checkpoint flag), you need to pause and inspect the piece. Check weld quality, measure dimensions, verify the right WPS was used. The system will remind you if a piece has been running longer than expected.</p>
        </div>
      </div>
    </div>

    <div class="workflow">
      <h2><span class="num">5</span> Take photos for QC inspections</h2>
      <div class="step-card">
        <div class="step-icon green">📸</div>
        <div class="step-body">
          <h3>Document your welds and assemblies with photos</h3>
          <p>When you complete a QC checkpoint, use the photo upload button to snap a picture with your phone's camera. Photos attach directly to the inspection record and are visible to auditors. Tap the camera icon, point at the weld, and snap — the photo uploads automatically with a caption.</p>
        </div>
      </div>
    </div>

    <div class="workflow">
      <h2><span class="num">6</span> Works offline too</h2>
      <div class="step-card">
        <div class="step-icon purple">📡</div>
        <div class="step-body">
          <h3>Keep scanning even when WiFi drops</h3>
          <p>Install TitanForge on your phone ("Add to Home Screen") for offline support. If WiFi drops, your QR scans are saved locally and automatically sync when connection returns. You'll see a small "offline" badge when disconnected — just keep working.</p>
        </div>
      </div>
    </div>

    <div class="tip-box">
      <strong>Tip:</strong> Check the TV dashboard for the daily leaderboard. Every item you complete earns points, and you can unlock badges like "Speed Demon" (under 10 min) and "Welding King" (50 welded assemblies).
    </div>
  </div>

  <!-- ═══════════════════════════════════════════ -->
  <!-- ESTIMATOR GUIDE -->
  <!-- ═══════════════════════════════════════════ -->
  <div class="role-section" id="role-estimator">
    <div class="workflow">
      <h2><span class="num">1</span> Create a new project</h2>
      <div class="step-card">
        <div class="step-icon blue">🏗️</div>
        <div class="step-body">
          <h3>Enter building dimensions in the SA Calculator</h3>
          <p>Go to the Structures America Estimator. Fill in the building width, length, eave height, number of bays, roof pitch, and wind speed. This generates the Bill of Materials (BOM) — the complete parts list.</p>
          <a class="go-link" href="/">Open SA Estimator &rarr;</a>
        </div>
      </div>
    </div>

    <div class="workflow">
      <h2><span class="num">2</span> Review and price the BOM</h2>
      <div class="step-card">
        <div class="step-icon green">💰</div>
        <div class="step-body">
          <h3>Check quantities, adjust pricing, save the project</h3>
          <p>After calculating, review each line item. The BOM shows every column, rafter, purlin, sag rod, strap, and panel with quantities and weights. Adjust the unit prices, then save the project with a job code.</p>
        </div>
      </div>
    </div>

    <div class="workflow">
      <h2><span class="num">3</span> Generate the quote</h2>
      <div class="step-card">
        <div class="step-icon amber">📄</div>
        <div class="step-body">
          <h3>Create a PDF quote for the customer</h3>
          <p>Once pricing is set, generate a professional quote PDF. You can also export the BOM to Excel for further editing. The quote includes material breakdown, labor, freight, and total pricing.</p>
        </div>
      </div>
    </div>

    <div class="workflow">
      <h2><span class="num">4</span> Hand off to the shop</h2>
      <div class="step-card">
        <div class="step-icon purple">🏭</div>
        <div class="step-body">
          <h3>Create work orders and print stickers</h3>
          <p>When a job is approved, create a work order from the project page. This generates the item list, assigns machines, and lets you print QR stickers for the shop floor. The shop takes it from here.</p>
        </div>
      </div>
    </div>

    <div class="workflow">
      <h2><span class="num">5</span> Ship the finished product</h2>
      <div class="step-card">
        <div class="step-icon purple">🚛</div>
        <div class="step-body">
          <h3>Generate packing lists, BOLs, and shipping manifests</h3>
          <p>When fabrication is complete, go to <strong>Shipping Hub</strong> for the job. Select completed items, enter truck and carrier info, and generate a Packing List and Bill of Lading. Print them for the driver. The BOL auto-fills Structures America as shipper with NMFC codes for structural steel.</p>
          <p>For multi-truck loads, use the Shipping Manifest to assign items to each truck by weight.</p>
        </div>
      </div>
    </div>

    <div class="workflow">
      <h2><span class="num">6</span> Create purchase orders for materials</h2>
      <div class="step-card">
        <div class="step-icon blue">📦</div>
        <div class="step-body">
          <h3>Reorder coils when inventory gets low</h3>
          <p>Check the <strong>Reorder Alerts</strong> tab in the Shipping Hub. It shows any coil gauges below the 5,000 lb threshold. Click "Create PO" to auto-generate a Purchase Order with Texas tax (8.25%) calculated. POs are auto-numbered and saved for your records.</p>
        </div>
      </div>
    </div>

    <div class="tip-box">
      <strong>Tip:</strong> Use the "Compare Revisions" feature to see what changed between versions of a design. Check <strong>Production Schedule</strong> for a Gantt view of all active jobs — it shows estimated completion dates, machine conflicts, and helps with capacity planning.
    </div>
  </div>

  <!-- ═══════════════════════════════════════════ -->
  <!-- ADMIN GUIDE -->
  <!-- ═══════════════════════════════════════════ -->
  <div class="role-section" id="role-admin">
    <div class="workflow">
      <h2><span class="num">1</span> Manage users and roles</h2>
      <div class="step-card">
        <div class="step-icon blue">👥</div>
        <div class="step-body">
          <h3>Set up accounts for your team</h3>
          <p>Go to Admin &rarr; Users. Create accounts and assign roles: <strong>Admin</strong> (full access), <strong>Estimator</strong> (quoting + projects), <strong>Shop</strong> (work orders + scanning), or <strong>Viewer</strong> (read-only). Each role only sees what they need.</p>
          <a class="go-link" href="/admin/users">Manage Users &rarr;</a>
        </div>
      </div>
    </div>

    <div class="workflow">
      <h2><span class="num">2</span> Monitor production</h2>
      <div class="step-card">
        <div class="step-icon green">📊</div>
        <div class="step-body">
          <h3>Use the Shop Floor Dashboard and TV Dashboard</h3>
          <p>The Shop Floor page shows real-time machine utilization, active work orders, and an activity feed. Put the TV Dashboard on a shop floor monitor — it auto-refreshes every 10 seconds with the leaderboard, production targets, and alerts.</p>
          <a class="go-link" href="/tv-dashboard">Open TV Dashboard &rarr;</a>
        </div>
      </div>
    </div>

    <div class="workflow">
      <h2><span class="num">3</span> Customize fab steps</h2>
      <div class="step-card">
        <div class="step-icon amber">⚙️</div>
        <div class="step-body">
          <h3>Edit the step-by-step instructions workers see</h3>
          <p>Each component type (column, rafter, purlin) has a default set of fabrication steps. You can override these globally or per-job if a particular building needs different procedures. Workers see these on their tablet at each station.</p>
        </div>
      </div>
    </div>

    <div class="workflow">
      <h2><span class="num">4</span> Review quality and traceability</h2>
      <div class="step-card">
        <div class="step-icon purple">🔍</div>
        <div class="step-body">
          <h3>Track QC inspections and material certifications</h3>
          <p>The QC module tracks inspection results per component. The traceability system links every piece back to its steel coil heat number. This is required for AISC certification.</p>
        </div>
      </div>
    </div>

    <div class="workflow">
      <h2><span class="num">5</span> Manage AISC documentation</h2>
      <div class="step-card">
        <div class="step-icon blue">📑</div>
        <div class="step-body">
          <h3>Keep your QA/QC records audit-ready</h3>
          <p>The <strong>QA/QC Hub</strong> is your central command for AISC certification. It tracks WPS procedures (welding specs), welder certifications (with expiration warnings), calibration logs, and the complete procedures library. Check the readiness checklist — green means you're covered for that requirement.</p>
          <a class="go-link" href="/qa">Open QA/QC Hub &rarr;</a>
        </div>
      </div>
    </div>

    <div class="workflow">
      <h2><span class="num">6</span> Plan capacity with the Production Schedule</h2>
      <div class="step-card">
        <div class="step-icon green">📊</div>
        <div class="step-body">
          <h3>See all active jobs on a timeline</h3>
          <p>The <strong>Production Schedule</strong> shows a Gantt chart of every active job. Colored bars show progress, red diamonds mark due dates, and the gold line shows today. Below the timeline, a machine utilization heatmap warns you when machines are overloaded (15+ items/day). Use this to decide when to take on new jobs.</p>
          <a class="go-link" href="/schedule">Open Production Schedule &rarr;</a>
        </div>
      </div>
    </div>

    <div class="workflow">
      <h2><span class="num">7</span> Track shipping and procurement</h2>
      <div class="step-card">
        <div class="step-icon amber">🚛</div>
        <div class="step-body">
          <h3>Generate shipping docs and monitor inventory levels</h3>
          <p>The Shipping Hub generates print-ready Packing Lists, Bills of Lading, and multi-truck Shipping Manifests. The Purchase Orders section handles vendor POs with auto-numbering and tax calculation. Reorder Alerts flag when any coil gauge drops below 5,000 lbs.</p>
        </div>
      </div>
    </div>

    <div class="tip-box">
      <strong>Tip:</strong> The Smart Queue automatically prioritizes items by due date, machine availability, and how long they've been waiting. Photo attachments on QC inspections make audit prep much faster — encourage shop workers to snap photos of completed welds and assemblies.
    </div>
  </div>

  <!-- ═══════════════════════════════════════════ -->
  <!-- QUICK REFERENCE (all roles) -->
  <!-- ═══════════════════════════════════════════ -->
  <h2 style="font-size:16px;color:#64748B;text-transform:uppercase;letter-spacing:1px;margin:32px 0 16px;">Quick Reference</h2>

  <div class="ref-grid">
    <div class="ref-card">
      <h4>Status Colors</h4>
      <p>
        <span style="color:#64748B">&#x25CF;</span> Queued (waiting)&nbsp;&nbsp;
        <span style="color:#3B82F6">&#x25CF;</span> Approved&nbsp;&nbsp;
        <span style="color:#F59E0B">&#x25CF;</span> In Progress&nbsp;&nbsp;
        <span style="color:#10B981">&#x25CF;</span> Complete&nbsp;&nbsp;
        <span style="color:#DC2626">&#x25CF;</span> On Hold
      </p>
    </div>
    <div class="ref-card">
      <h4>Ship Mark Codes</h4>
      <p><code>C1</code> = Column 1, <code>R1</code> = Rafter 1, <code>P1</code> = Purlin 1, <code>SR</code> = Sag Rod, <code>PG</code> = Panel</p>
    </div>
    <div class="ref-card">
      <h4>WPS Codes</h4>
      <p><code>WPS-B</code> = Stitch welds, <code>WPS-C</code> = Clip welds, <code>WPS-D</code> = Rebar welds, <code>WPS-F</code> = End plate welds</p>
    </div>
    <div class="ref-card">
      <h4>Machines</h4>
      <p>C1/C2 = Roll Formers, Z1 = Z-Purlin Former, P1 = Plate Former, SPARTAN = Roof Panels, WELDING = Weld Bay</p>
    </div>
    <div class="ref-card">
      <h4>Key Pages</h4>
      <p><code>/shop-floor</code> Dashboard, <code>/scan/{job}</code> QR Scanner, <code>/tv-dashboard</code> Live TV, <code>/work-station/{job}</code> Tablet View</p>
    </div>
    <div class="ref-card">
      <h4>New: Shipping &amp; Procurement</h4>
      <p><code>/shipping/{job}</code> Packing Lists, BOLs, Manifests. <code>/schedule</code> Production Gantt. PO creation with auto-numbering.</p>
    </div>
    <div class="ref-card">
      <h4>New: QA/QC Hub</h4>
      <p><code>/qa</code> AISC documentation center. WPS Library, Welder Certs, Procedures, NCR Log, Calibration. Photo attachments on inspections.</p>
    </div>
    <div class="ref-card">
      <h4>Offline Mode</h4>
      <p>Install on your phone for offline QR scanning. Failed scans queue locally and sync when WiFi returns. Look for "Add to Home Screen" prompt.</p>
    </div>
    <div class="ref-card">
      <h4>Need Help?</h4>
      <p>Look for the <span style="display:inline-flex;align-items:center;justify-content:center;width:16px;height:16px;border-radius:50%;background:#334155;color:#94A3B8;font-size:10px;font-weight:700;">i</span> icons throughout the app. Click one to see a plain-English explanation. Or open the full Glossary from the nav bar.</p>
    </div>
  </div>

  <!-- ═══════════════════════════════════════════ -->
  <!-- INTERACTIVE WALKTHROUGH LAUNCH -->
  <!-- ═══════════════════════════════════════════ -->
  <div style="margin-top:32px;border-top:2px solid #1E293B;padding-top:32px;margin-bottom:32px;">
    <div style="background:linear-gradient(135deg, rgba(200,154,46,0.12) 0%, rgba(200,154,46,0.04) 100%);border:1px solid rgba(200,154,46,0.3);border-radius:14px;padding:28px;text-align:center;">
      <div style="font-size:40px;margin-bottom:12px;">🎓</div>
      <h2 style="font-size:20px;color:#FFF;margin-bottom:8px;">Interactive Walkthrough</h2>
      <p style="font-size:14px;color:#94A3B8;max-width:500px;margin:0 auto 20px;line-height:1.6;">
        New to TitanForge? Take our guided tour! We'll walk you step-by-step through creating your first building project — from entering dimensions to generating a full Bill of Materials.
      </p>
      <button onclick="TFWalkthrough.start(0)" style="padding:12px 32px;border-radius:10px;border:none;background:linear-gradient(135deg,#C89A2E,#D4A84B);color:#0F172A;font-size:15px;font-weight:700;cursor:pointer;transition:all 0.2s;box-shadow:0 4px 16px rgba(200,154,46,0.3);" onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 6px 20px rgba(200,154,46,0.4)'" onmouseout="this.style.transform='';this.style.boxShadow='0 4px 16px rgba(200,154,46,0.3)'">
        Start Interactive Walkthrough →
      </button>
      <p style="font-size:11px;color:#64748B;margin-top:12px;">Takes about 3 minutes · Guides you through Dashboard → SA Estimator → BOM → Save</p>
    </div>
  </div>

  <!-- ═══════════════════════════════════════════ -->
  <!-- INTERACTIVE ONBOARDING WIZARD -->
  <!-- ═══════════════════════════════════════════ -->
  <div style="margin-top:32px;border-top:2px solid #1E293B;padding-top:32px;">
    <h2 style="font-size:18px;color:#FFF;margin-bottom:4px;">Your Onboarding Progress</h2>
    <p style="font-size:13px;color:#94A3B8;margin-bottom:16px;">Complete these steps to get up and running. Your progress is saved automatically.</p>

    <!-- Progress Bar -->
    <div style="background:#1E293B;border-radius:8px;height:12px;overflow:hidden;margin-bottom:20px;">
      <div id="onboardProgressBar" style="height:100%;width:0%;background:linear-gradient(90deg,#C89A2E,#F59E0B);border-radius:8px;transition:width 0.6s ease;"></div>
    </div>
    <div id="onboardProgressText" style="font-size:12px;color:#94A3B8;margin-bottom:20px;text-align:center;">0 of 5 steps completed</div>

    <!-- Step 1 -->
    <div class="step-card" id="onboard-step-1" style="border-left:3px solid #334155;">
      <div class="step-icon blue">1</div>
      <div class="step-body" style="flex:1;">
        <h3>Create your first customer</h3>
        <p>Every project starts with a customer. Go to the Customers page and click "+ New Customer" to add one.</p>
        <a class="go-link" href="/customers">Open Customers &rarr;</a>
      </div>
      <label style="cursor:pointer;display:flex;align-items:center;gap:6px;color:#94A3B8;font-size:12px;">
        <input type="checkbox" class="onboard-check" data-step="1" onchange="toggleOnboardStep(1, this.checked)"> Done
      </label>
    </div>

    <!-- Step 2 -->
    <div class="step-card" id="onboard-step-2" style="border-left:3px solid #334155;">
      <div class="step-icon green">2</div>
      <div class="step-body" style="flex:1;">
        <h3>Start an estimate</h3>
        <p>Open the SA Estimator, fill in building dimensions (width, length, height, pitch), and click CALCULATE BOM to generate a full bill of materials.</p>
        <a class="go-link" href="/sa">Open SA Estimator &rarr;</a>
      </div>
      <label style="cursor:pointer;display:flex;align-items:center;gap:6px;color:#94A3B8;font-size:12px;">
        <input type="checkbox" class="onboard-check" data-step="2" onchange="toggleOnboardStep(2, this.checked)"> Done
      </label>
    </div>

    <!-- Step 3 -->
    <div class="step-card" id="onboard-step-3" style="border-left:3px solid #334155;">
      <div class="step-icon amber">3</div>
      <div class="step-body" style="flex:1;">
        <h3>Generate shop drawings</h3>
        <p>From the project page, click "Shop Drawings" to access interactive drawings for rafters, columns, purlins, and more. These are parametric SVG drawings you can customize and save as PDFs.</p>
        <a class="go-link" href="/shop-drawings">Open Shop Drawings &rarr;</a>
      </div>
      <label style="cursor:pointer;display:flex;align-items:center;gap:6px;color:#94A3B8;font-size:12px;">
        <input type="checkbox" class="onboard-check" data-step="3" onchange="toggleOnboardStep(3, this.checked)"> Done
      </label>
    </div>

    <!-- Step 4 -->
    <div class="step-card" id="onboard-step-4" style="border-left:3px solid #334155;">
      <div class="step-icon purple">4</div>
      <div class="step-body" style="flex:1;">
        <h3>Create work orders</h3>
        <p>Once shop drawings are ready, create a work order from the project page. This assigns items to machines, generates QR stickers, and pushes work to the shop floor queue.</p>
        <a class="go-link" href="/work-orders">View Work Orders &rarr;</a>
      </div>
      <label style="cursor:pointer;display:flex;align-items:center;gap:6px;color:#94A3B8;font-size:12px;">
        <input type="checkbox" class="onboard-check" data-step="4" onchange="toggleOnboardStep(4, this.checked)"> Done
      </label>
    </div>

    <!-- Step 5 -->
    <div class="step-card" id="onboard-step-5" style="border-left:3px solid #334155;">
      <div class="step-icon blue">5</div>
      <div class="step-body" style="flex:1;">
        <h3>Track through shipping</h3>
        <p>As items are fabricated, track progress via the Shop Floor dashboard. When complete, generate packing lists and bills of lading from the Shipping Hub to send the order out.</p>
        <a class="go-link" href="/shipping">Open Shipping Hub &rarr;</a>
      </div>
      <label style="cursor:pointer;display:flex;align-items:center;gap:6px;color:#94A3B8;font-size:12px;">
        <input type="checkbox" class="onboard-check" data-step="5" onchange="toggleOnboardStep(5, this.checked)"> Done
      </label>
    </div>
  </div>

  <div class="gs-footer">
    TitanForge v4.0 &mdash; Titan Carports &mdash; <a href="/">Back to Dashboard</a>
  </div>

</div>

<script>
  var userRole = '{{USER_ROLE}}'.toLowerCase();
  function showRole(role) {
    document.querySelectorAll('.role-section').forEach(function(s) { s.classList.remove('active'); });
    document.querySelectorAll('.role-tab').forEach(function(t) { t.classList.remove('active'); });
    var section = document.getElementById('role-' + role);
    var tab = document.querySelector('.role-tab[data-role="' + role + '"]');
    if (section) section.classList.add('active');
    if (tab) tab.classList.add('active');
  }
  // Auto-select based on user role
  if (userRole === 'shop') showRole('shop');
  else if (userRole === 'estimator') showRole('estimator');
  else if (userRole === 'admin') showRole('admin');
  else showRole('shop'); // Default

  // ── Onboarding Progress Tracking ──
  var ONBOARD_STEPS = 5;

  function loadOnboardProgress() {
    fetch('/api/onboarding/progress')
      .then(function(r) { return r.json(); })
      .then(function(data) {
        if (data.ok && data.steps) {
          Object.keys(data.steps).forEach(function(stepKey) {
            var stepNum = parseInt(stepKey);
            if (data.steps[stepKey]) {
              var cb = document.querySelector('.onboard-check[data-step="' + stepNum + '"]');
              if (cb) cb.checked = true;
              markStepDone(stepNum);
            }
          });
          updateProgressBar();
        }
      })
      .catch(function() {
        // Fallback to cookie
        var cookie = getCookie('tf_onboard');
        if (cookie) {
          try {
            var steps = JSON.parse(cookie);
            for (var i = 1; i <= ONBOARD_STEPS; i++) {
              if (steps[i]) {
                var cb = document.querySelector('.onboard-check[data-step="' + i + '"]');
                if (cb) cb.checked = true;
                markStepDone(i);
              }
            }
            updateProgressBar();
          } catch(e) {}
        }
      });
  }

  function toggleOnboardStep(step, done) {
    if (done) markStepDone(step);
    else markStepUndone(step);
    updateProgressBar();
    saveOnboardProgress();
  }

  function markStepDone(step) {
    var card = document.getElementById('onboard-step-' + step);
    if (card) {
      card.style.borderLeftColor = '#10B981';
      card.style.background = '#0D2818';
    }
  }

  function markStepUndone(step) {
    var card = document.getElementById('onboard-step-' + step);
    if (card) {
      card.style.borderLeftColor = '#334155';
      card.style.background = '';
    }
  }

  function updateProgressBar() {
    var done = document.querySelectorAll('.onboard-check:checked').length;
    var pct = Math.round((done / ONBOARD_STEPS) * 100);
    var bar = document.getElementById('onboardProgressBar');
    var txt = document.getElementById('onboardProgressText');
    if (bar) bar.style.width = pct + '%';
    if (txt) txt.textContent = done + ' of ' + ONBOARD_STEPS + ' steps completed' + (done === ONBOARD_STEPS ? ' — You are all set!' : '');
  }

  function saveOnboardProgress() {
    var steps = {};
    for (var i = 1; i <= ONBOARD_STEPS; i++) {
      var cb = document.querySelector('.onboard-check[data-step="' + i + '"]');
      steps[i] = cb ? cb.checked : false;
    }
    // Save to API
    fetch('/api/onboarding/progress', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({steps: steps})
    }).catch(function() {});
    // Also save to cookie as fallback
    setCookie('tf_onboard', JSON.stringify(steps), 365);
  }

  function getCookie(name) {
    var m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return m ? decodeURIComponent(m[2]) : null;
  }
  function setCookie(name, value, days) {
    var d = new Date();
    d.setTime(d.getTime() + days * 86400000);
    document.cookie = name + '=' + encodeURIComponent(value) + ';expires=' + d.toUTCString() + ';path=/';
  }

  loadOnboardProgress();
</script>
</body>
</html>
"""
