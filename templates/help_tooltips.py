"""
TitanForge — Help Tooltip System
=================================
Reusable glossary tooltips for all pages. Any page can include TOOLTIP_CSS + TOOLTIP_JS
and then use <span class="tf-help" data-term="bom"> next to any jargon.

The tooltip shows a plain-English explanation on click/tap (mobile-friendly).
Also provides a searchable glossary panel accessible from the nav bar.
"""

# ─────────────────────────────────────────────
# GLOSSARY — Plain English definitions
# ─────────────────────────────────────────────

GLOSSARY = {
    # ── General Terms ──
    "bom": {
        "term": "BOM (Bill of Materials)",
        "short": "The complete parts list for a building",
        "detail": "A Bill of Materials lists every piece of steel, hardware, and material needed to build the structure. It includes quantities, sizes, gauges, and weights. Think of it like a recipe — it tells the shop exactly what to cut, form, and weld."
    },
    "ship_mark": {
        "term": "Ship Mark",
        "short": "A label that identifies each piece",
        "detail": "Every component gets a unique ship mark (like C1, R1, P1) so the shop floor knows which piece is which. It's stamped on stickers and used for tracking from fabrication through shipping. C = Column, R = Rafter, P = Purlin."
    },
    "job_code": {
        "term": "Job Code",
        "short": "Unique ID for each project",
        "detail": "Every building project gets a job code (like SA2401-A). SA = Structures America, 24 = year, 01 = sequence, A = revision. This ties everything together — quotes, drawings, work orders, and stickers all reference the same job code."
    },
    "work_order": {
        "term": "Work Order (WO)",
        "short": "An instruction to build specific parts",
        "detail": "A work order tells the shop floor to fabricate a set of components for a job. It starts as 'Queued', gets approved, stickers printed, and then workers scan QR codes to track start/finish times on each piece."
    },
    "revision": {
        "term": "Revision",
        "short": "Version letter for design changes",
        "detail": "When a building design changes after the initial drawing, the revision letter increments (A → B → C). This makes sure the shop is always building from the latest approved version."
    },

    # ── Building Components ──
    "column": {
        "term": "Column",
        "short": "Vertical steel post that holds up the building",
        "detail": "Columns are the main vertical supports. In metal buildings, they're usually made by welding two C-shaped channels (CEEs) together into a box beam. They carry the weight of rafters, purlins, and the roof down to the foundation."
    },
    "rafter": {
        "term": "Rafter",
        "short": "Angled beam that forms the roof slope",
        "detail": "Rafters run from the top of the columns to the ridge (peak) of the roof. They're built the same way as columns — two CEEs welded into a box beam — but cut at an angle to match the roof pitch. Purlins attach to the rafters."
    },
    "purlin": {
        "term": "Purlin",
        "short": "Horizontal roof member that supports panels",
        "detail": "Purlins are the lighter horizontal members that span between rafters. Roof panels bolt directly to purlins. They come in C-shape (CEE purlins) or Z-shape (zee purlins) and are roll-formed from steel coils."
    },
    "cee": {
        "term": "CEE (C-Channel)",
        "short": "C-shaped steel section",
        "detail": "A CEE is a piece of steel formed into a C shape by the roll former. Two CEEs are welded back-to-back to make columns and rafters (creating a strong box beam). CEEs come in different sizes like 14x4 (14 inches tall, 4 inch flange)."
    },
    "girt": {
        "term": "Girt",
        "short": "Horizontal wall member",
        "detail": "Girts are like purlins but for walls instead of roofs. They run horizontally between columns and wall panels bolt to them. They support the wall sheeting and transfer wind loads to the columns."
    },
    "sag_rod": {
        "term": "Sag Rod",
        "short": "Thin rod that keeps purlins from twisting",
        "detail": "Sag rods are long threaded rods that run between purlins to prevent them from rolling or sagging sideways. They're typically 1/2 inch or 5/8 inch diameter and thread through holes in the purlin webs."
    },
    "strap": {
        "term": "Strap / Bracing",
        "short": "Diagonal brace for wind resistance",
        "detail": "Straps (also called flange braces) are flat steel pieces that connect purlins to rafters diagonally. They keep the roof structure from racking sideways in wind. Some are hurricane straps for high-wind zones."
    },
    "endcap": {
        "term": "Endcap",
        "short": "Cover plate at the end of a member",
        "detail": "Endcaps are flat plates welded to the open ends of columns, rafters, or purlins to close them off. They prevent water intrusion and provide a surface for bolted connections."
    },
    "clip": {
        "term": "Clip",
        "short": "Small bracket that connects two parts",
        "detail": "Clips are small L-shaped or flat brackets welded to rafters or columns. Purlins bolt to these clips. There are P1 clips (standard) and P2 clips (for endwall conditions)."
    },
    "base_plate": {
        "term": "Base Plate",
        "short": "Steel plate at the bottom of a column",
        "detail": "The base plate is welded to the bottom of each column and sits on the concrete foundation. Anchor bolts go through holes in the plate to secure the column to the footing."
    },
    "cap_plate": {
        "term": "Cap Plate",
        "short": "Steel plate at the top of a column",
        "detail": "The cap plate (or end plate) is welded to the top of the column where it connects to the rafter. It's cut at the roof pitch angle so the rafter sits flush against it."
    },
    "rebar": {
        "term": "Rebar (Reinforcement Bar)",
        "short": "Steel bar inside columns for extra strength",
        "detail": "On taller or heavier-loaded columns, a steel rebar is welded inside the box beam for additional bending strength. Not all columns need rebar — it depends on the engineering calculation."
    },

    # ── Measurements & Engineering ──
    "gauge": {
        "term": "Gauge (GA)",
        "short": "Steel thickness — lower number = thicker",
        "detail": "Gauge measures steel thickness. Common gauges: 10GA = 0.135 inch (thick, for columns/rafters), 12GA = 0.105 inch (medium), 14GA = 0.075 inch (lighter, for purlins). Counter-intuitively, a LOWER gauge number means THICKER steel."
    },
    "pitch": {
        "term": "Roof Pitch",
        "short": "The angle/slope of the roof",
        "detail": "Pitch is usually expressed in degrees (like 1.2° or 5°) or as rise-over-run (like 1:12). Low-slope metal buildings are typically 0.5° to 5°. The pitch determines the angle cuts on rafters and cap plates."
    },
    "span": {
        "term": "Span / Bay Spacing",
        "short": "Distance between frame lines",
        "detail": "Span is the width of the building (column to column). Bay spacing is the distance between frames along the length. A 60' x 100' building with 20' bays has 6 frame lines spaced 20' apart across the 100' length."
    },
    "eave_height": {
        "term": "Eave Height",
        "short": "Height from ground to where the roof starts",
        "detail": "The eave height is measured from the finished floor to the bottom of the rafter at the outside wall. A 16' eave height means the wall columns are approximately 16 feet tall."
    },
    "embedment": {
        "term": "Embedment / Footing Depth",
        "short": "How deep the column sits in concrete",
        "detail": "Embedment depth is how far the base plate and bottom of the column are set into the concrete footing. This varies by state and soil conditions — typically 24 to 48 inches. Deeper in cold climates to get below the frost line."
    },
    "wind_speed": {
        "term": "Wind Speed",
        "short": "Design wind speed for structural calculations",
        "detail": "This is the 3-second gust wind speed per ASCE 7 building code, measured in mph. It varies by location — coastal Texas might be 150 mph, inland might be 115 mph. Higher wind speed = heavier steel needed."
    },
    "overhang": {
        "term": "Overhang",
        "short": "Roof extension past the wall",
        "detail": "The overhang is how far the roof sticks out beyond the sidewall. It provides shade and rain protection. Typical overhangs are 6 inches to 24 inches. Can be flush (no overhang) or extended."
    },

    # ── Fabrication Terms ──
    "wps": {
        "term": "WPS (Welding Procedure Specification)",
        "short": "The official recipe for how to weld a joint",
        "detail": "A WPS defines exactly how a weld should be done — wire type, gas, amperage, travel speed, etc. Each joint type has its own WPS code: WPS-B = stitch welds (CEE body), WPS-C = clip welds, WPS-D = rebar welds, WPS-F = end plate welds."
    },
    "stitch_weld": {
        "term": "Stitch Weld",
        "short": "Short welds spaced along a seam",
        "detail": "Instead of welding the entire length of a joint (which would warp the steel from heat), stitch welds are short weld segments spaced evenly apart. For example, 2-inch welds every 12 inches along the CEE-to-CEE joint."
    },
    "tack_weld": {
        "term": "Tack Weld",
        "short": "Small temporary weld to hold parts in place",
        "detail": "Before doing the final stitch welds, the welder does small tack welds to hold the two CEEs in alignment. These are temporary — just enough to keep things from shifting during the full welding pass."
    },
    "roll_former": {
        "term": "Roll Former",
        "short": "Machine that bends flat steel into shapes",
        "detail": "A roll former feeds flat steel coil through a series of rollers that gradually bend it into a C-shape (for purlins/CEEs) or a panel profile (for roofing). It's the first step — the steel comes off the coil, goes through the machine, and gets cut to length."
    },
    "coil": {
        "term": "Coil",
        "short": "Large roll of flat steel",
        "detail": "Steel arrives at the shop as large rolls (coils) that weigh 5,000-10,000 lbs each. The coil is loaded onto the roll former, which feeds it through and shapes it. Coils come in different widths, gauges, and paint colors."
    },
    "cold_galv": {
        "term": "Cold Galvanizing",
        "short": "Zinc spray coating to prevent rust",
        "detail": "After welding, the weld areas lose their protective coating. Cold galvanizing is a zinc-rich spray paint applied to exposed steel and weld joints to prevent corrosion. It's the last step before tagging and staging."
    },
    "qc_checkpoint": {
        "term": "QC Checkpoint",
        "short": "Quality inspection pause",
        "detail": "At specific points during fabrication (usually after welding and before tagging), the piece must be inspected. The checker verifies weld quality, dimensions, straightness, and that the right WPS was used. This is mandatory — no skipping."
    },

    # ── App-Specific Terms ──
    "fab_steps": {
        "term": "Fab Steps",
        "short": "Step-by-step build instructions",
        "detail": "Each component type (column, rafter, purlin, etc.) has a template of fabrication steps that appear on the work station tablet. Workers follow these steps in order — pull material, align, tack, weld, clean, inspect, tag."
    },
    "smart_queue": {
        "term": "Smart Queue",
        "short": "Auto-sorted work priority list",
        "detail": "The smart queue scores each item based on due date urgency, machine availability, how long it's been waiting, and whether it's blocking other items. Higher-priority items sort to the top so workers grab the most important piece next."
    },
    "qr_scan": {
        "term": "QR Scan (Start/Finish)",
        "short": "Scan a sticker to track fabrication time",
        "detail": "Each sticker has a QR code. Workers scan it with their phone when they START working on a piece, and scan again when they FINISH. This tracks fabrication time per item, feeds the leaderboard, and updates the dashboard in real time."
    },

    # ── Shipping & Procurement ──
    "packing_list": {
        "term": "Packing List",
        "short": "Inventory of items loaded on a truck",
        "detail": "A packing list itemizes every piece loaded for shipment — grouped by type (columns, rafters, purlins) with piece counts and estimated weights. It's signed by the loader, driver, and receiver as proof of what was shipped."
    },
    "bol": {
        "term": "BOL (Bill of Lading)",
        "short": "Legal shipping document between shipper and carrier",
        "detail": "The Bill of Lading is the contract between Structures America (shipper) and the trucking company (carrier). It lists freight class (65 for structural steel), NMFC code 48620, total weight, and piece count. The driver signs it at pickup and the customer signs at delivery."
    },
    "shipping_manifest": {
        "term": "Shipping Manifest",
        "short": "Master list of all loads for a job",
        "detail": "When a job requires multiple truck loads, the manifest shows which items go on each truck, the weight per load, and a recommended loading sequence (heaviest items first). It helps the shop plan truck staging."
    },
    "purchase_order": {
        "term": "Purchase Order (PO)",
        "short": "Order form sent to a material supplier",
        "detail": "A PO is generated when coil inventory gets low or when materials are needed for a specific job. It includes gauge, width, weight, unit price per pound, subtotal, and Texas tax (8.25%). POs are auto-numbered (PO-YYYYMMDD-NNN)."
    },
    "nmfc": {
        "term": "NMFC Code",
        "short": "National freight classification number",
        "detail": "NMFC (National Motor Freight Classification) assigns codes to different types of freight. Structural steel fabrications use NMFC 48620, Freight Class 65. This determines shipping rates."
    },
    "reorder_point": {
        "term": "Reorder Point",
        "short": "Inventory level that triggers a new purchase order",
        "detail": "When available stock for any gauge/width coil drops below the reorder threshold (default 5,000 lbs), the system flags it as a reorder alert. The Shipping Hub shows these alerts with a one-click option to create a PO."
    },

    # ── QA / AISC Documentation ──
    "ncr": {
        "term": "NCR (Non-Conformance Report)",
        "short": "Document for when something doesn't meet spec",
        "detail": "An NCR is filed when an inspection finds a defect — wrong dimension, bad weld, surface damage, etc. It tracks severity (minor/major/critical), root cause, corrective action, and final disposition (rework, accept-as-is, or reject). Required by AISC."
    },
    "pqr": {
        "term": "PQR (Procedure Qualification Record)",
        "short": "Test record that proves a WPS works",
        "detail": "Before a WPS can be used in production, it must be proven by testing. The PQR documents the test welds, mechanical testing results, and certifies that the WPS produces acceptable welds. Each WPS references its supporting PQR."
    },
    "calibration": {
        "term": "Calibration",
        "short": "Regular testing of measurement tools",
        "detail": "Measuring tools (weld gauges, tape measures, torque wrenches) must be calibrated on a schedule to ensure accuracy. The calibration log tracks tool name, serial number, last calibration date, and next due date. AISC auditors check this."
    },
    "welder_cert": {
        "term": "Welder Certification",
        "short": "Proof that a welder passed their welding test",
        "detail": "Each welder must be certified for the processes (FCAW, SMAW) and positions (1G, 2G, 3G, 4G) they perform. Certs expire (typically every 2 years) and must be renewed by passing a test. The system tracks expirations and warns 30 days before."
    },
    "aisc": {
        "term": "AISC Certification",
        "short": "Quality standard for steel fabricators",
        "detail": "AISC (American Institute of Steel Construction) certification proves the shop follows documented quality procedures — WPS, welder certs, inspection records, calibration, NCRs, and traceability. Auditors visit periodically to verify compliance."
    },

    # ── Production Planning ──
    "gantt_chart": {
        "term": "Gantt Chart / Production Schedule",
        "short": "Visual timeline showing when jobs will be built",
        "detail": "The Gantt chart shows all active jobs as horizontal bars on a timeline. Bar length = estimated fabrication time, color = status (gray=queued, blue=in progress, green=done). Red diamonds show due dates. The gold line marks today."
    },
    "machine_utilization": {
        "term": "Machine Utilization",
        "short": "How busy each machine is per day",
        "detail": "The heatmap below the Gantt chart shows item counts per machine per day. Green = light load, amber = moderate, red = overloaded (15+ items). This helps decide when to start new jobs without overloading machines."
    },
    "gamification": {
        "term": "Gamification (Badges & Leaderboard)",
        "short": "Points, badges, and rankings for shop workers",
        "detail": "Every completed piece earns progress toward badges like 'Iron Worker' (10 items), 'Speed Demon' (under 10 min), and 'Welding King' (50 welded assemblies). The TV dashboard shows the daily leaderboard and production targets."
    },
    "pwa": {
        "term": "PWA / Offline Mode",
        "short": "Install the app on your phone for offline use",
        "detail": "TitanForge can be installed as a Progressive Web App on phones and tablets. When WiFi drops, QR scans are saved locally and sync automatically when connection returns. Tap 'Add to Home Screen' to install."
    },
}


# ─────────────────────────────────────────────
# CSS for tooltip system (include in any page)
# ─────────────────────────────────────────────

TOOLTIP_CSS = """
/* ── TitanForge Help Tooltip System ── */
.tf-help {
  display: inline-flex; align-items: center; justify-content: center;
  width: 16px; height: 16px; border-radius: 50%;
  background: #334155; color: #94A3B8; cursor: pointer;
  font-size: 10px; font-weight: 700; font-style: normal;
  margin-left: 4px; vertical-align: middle;
  transition: all 0.2s; position: relative;
  user-select: none; -webkit-tap-highlight-color: transparent;
  border: 1px solid #475569;
}
.tf-help:hover, .tf-help.active {
  background: #1E40AF; color: #FFF; border-color: #3B82F6;
}
.tf-help::after { content: 'i'; }

.tf-tooltip {
  display: none; position: fixed; z-index: 99999;
  background: #1E293B; border: 1px solid #475569;
  border-radius: 10px; padding: 14px 16px;
  max-width: 340px; min-width: 220px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.4);
  font-size: 13px; line-height: 1.5; color: #CBD5E1;
  animation: tfTooltipIn 0.15s ease;
}
.tf-tooltip.visible { display: block; }
@keyframes tfTooltipIn { from { opacity:0; transform:translateY(4px); } to { opacity:1; transform:translateY(0); } }

.tf-tooltip .tt-term {
  font-size: 14px; font-weight: 700; color: #C89A2E;
  margin-bottom: 4px;
}
.tf-tooltip .tt-short {
  font-size: 12px; color: #94A3B8; margin-bottom: 8px;
  font-style: italic;
}
.tf-tooltip .tt-detail {
  font-size: 13px; color: #E2E8F0; line-height: 1.6;
}
.tf-tooltip .tt-close {
  position: absolute; top: 8px; right: 10px;
  background: none; border: none; color: #64748B;
  font-size: 16px; cursor: pointer; padding: 0 4px;
}
.tf-tooltip .tt-close:hover { color: #F1F5F9; }

/* Glossary panel */
.tf-glossary-btn {
  display: flex; align-items: center; gap: 6px;
  padding: 6px 12px; background: #334155; border: 1px solid #475569;
  border-radius: 6px; color: #CBD5E1; font-size: 12px;
  cursor: pointer; transition: all 0.2s;
}
.tf-glossary-btn:hover { background: #1E40AF; border-color: #3B82F6; color: #FFF; }

.tf-glossary-overlay {
  display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.6); z-index: 99998;
}
.tf-glossary-overlay.visible { display: block; }

.tf-glossary-panel {
  position: fixed; top: 0; right: 0; bottom: 0; width: 400px;
  max-width: 90vw; background: #0F172A; z-index: 99999;
  overflow-y: auto; padding: 20px;
  box-shadow: -4px 0 30px rgba(0,0,0,0.5);
  transform: translateX(100%); transition: transform 0.25s ease;
}
.tf-glossary-panel.visible { transform: translateX(0); }

.tf-glossary-panel h2 {
  font-size: 18px; color: #FFF; margin-bottom: 4px;
}
.tf-glossary-panel .subtitle {
  font-size: 12px; color: #64748B; margin-bottom: 16px;
}
.tf-glossary-search {
  width: 100%; padding: 10px 12px; background: #1E293B;
  border: 1px solid #334155; border-radius: 8px;
  color: #F1F5F9; font-size: 14px; margin-bottom: 16px;
}
.tf-glossary-search:focus { outline: none; border-color: #C89A2E; }
.tf-glossary-search::placeholder { color: #475569; }

.tf-glossary-item {
  padding: 12px; margin-bottom: 8px; background: #1E293B;
  border-radius: 8px; border-left: 3px solid #334155;
  cursor: pointer; transition: all 0.2s;
}
.tf-glossary-item:hover { border-left-color: #C89A2E; background: #253347; }
.tf-glossary-item .gi-term { font-weight: 700; color: #C89A2E; font-size: 14px; }
.tf-glossary-item .gi-short { font-size: 12px; color: #94A3B8; margin-top: 2px; }
.tf-glossary-item .gi-detail {
  display: none; font-size: 13px; color: #CBD5E1;
  margin-top: 8px; line-height: 1.6;
}
.tf-glossary-item.expanded .gi-detail { display: block; }
.tf-glossary-item.expanded { border-left-color: #1E40AF; }
"""


# ─────────────────────────────────────────────
# JS for tooltip system (include in any page)
# ─────────────────────────────────────────────

TOOLTIP_JS = """
<script>
(function() {
  var GLOSSARY = ##GLOSSARY_JSON##;

  // ── Tooltip singleton ──
  var tooltip = document.createElement('div');
  tooltip.className = 'tf-tooltip';
  tooltip.innerHTML = '<button class="tt-close">&times;</button>'
    + '<div class="tt-term"></div><div class="tt-short"></div><div class="tt-detail"></div>';
  document.body.appendChild(tooltip);

  tooltip.querySelector('.tt-close').addEventListener('click', function() {
    tooltip.classList.remove('visible');
    document.querySelectorAll('.tf-help.active').forEach(function(el) { el.classList.remove('active'); });
  });

  // ── Click handler for all help icons ──
  document.addEventListener('click', function(e) {
    var help = e.target.closest('.tf-help');
    if (!help) {
      if (!e.target.closest('.tf-tooltip')) {
        tooltip.classList.remove('visible');
        document.querySelectorAll('.tf-help.active').forEach(function(el) { el.classList.remove('active'); });
      }
      return;
    }

    var term = help.getAttribute('data-term');
    var entry = GLOSSARY[term];
    if (!entry) return;

    // Position tooltip near the icon
    var rect = help.getBoundingClientRect();
    var left = rect.right + 8;
    var top = rect.top - 10;

    // Keep on screen
    if (left + 350 > window.innerWidth) left = rect.left - 360;
    if (left < 8) left = 8;
    if (top + 200 > window.innerHeight) top = window.innerHeight - 210;
    if (top < 8) top = 8;

    tooltip.style.left = left + 'px';
    tooltip.style.top = top + 'px';
    tooltip.querySelector('.tt-term').textContent = entry.term;
    tooltip.querySelector('.tt-short').textContent = entry.short;
    tooltip.querySelector('.tt-detail').textContent = entry.detail;

    document.querySelectorAll('.tf-help.active').forEach(function(el) { el.classList.remove('active'); });
    help.classList.add('active');
    tooltip.classList.add('visible');
  });

  // ── Glossary panel ──
  window.tfOpenGlossary = function() {
    var overlay = document.getElementById('tfGlossaryOverlay');
    var panel = document.getElementById('tfGlossaryPanel');
    if (!overlay) return;
    overlay.classList.add('visible');
    panel.classList.add('visible');
    var search = panel.querySelector('.tf-glossary-search');
    if (search) { search.value = ''; search.focus(); filterGlossary(''); }
  };

  window.tfCloseGlossary = function() {
    var overlay = document.getElementById('tfGlossaryOverlay');
    var panel = document.getElementById('tfGlossaryPanel');
    if (overlay) overlay.classList.remove('visible');
    if (panel) panel.classList.remove('visible');
  };

  function filterGlossary(q) {
    var items = document.querySelectorAll('.tf-glossary-item');
    var lower = q.toLowerCase();
    items.forEach(function(item) {
      var text = (item.getAttribute('data-search') || '').toLowerCase();
      item.style.display = (!q || text.indexOf(lower) >= 0) ? '' : 'none';
    });
  }

  document.addEventListener('DOMContentLoaded', function() {
    // Build glossary items
    var list = document.getElementById('tfGlossaryList');
    if (!list) return;
    var html = '';
    var keys = Object.keys(GLOSSARY).sort(function(a,b) {
      return GLOSSARY[a].term.localeCompare(GLOSSARY[b].term);
    });
    keys.forEach(function(k) {
      var e = GLOSSARY[k];
      html += '<div class="tf-glossary-item" data-search="' + e.term + ' ' + e.short + ' ' + e.detail
        + '" onclick="this.classList.toggle(\\\'expanded\\\')">'
        + '<div class="gi-term">' + e.term + '</div>'
        + '<div class="gi-short">' + e.short + '</div>'
        + '<div class="gi-detail">' + e.detail + '</div>'
        + '</div>';
    });
    list.innerHTML = html;

    var search = document.querySelector('.tf-glossary-search');
    if (search) {
      search.addEventListener('input', function() { filterGlossary(this.value); });
    }
  });
})();
</script>
"""


# ─────────────────────────────────────────────
# GLOSSARY PANEL HTML (include once per page)
# ─────────────────────────────────────────────

GLOSSARY_PANEL_HTML = """
<div class="tf-glossary-overlay" id="tfGlossaryOverlay" onclick="tfCloseGlossary()"></div>
<div class="tf-glossary-panel" id="tfGlossaryPanel">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
    <div>
      <h2>Glossary</h2>
      <div class="subtitle">Tap any term to expand its definition</div>
    </div>
    <button onclick="tfCloseGlossary()" style="background:none;border:none;color:#64748B;font-size:24px;cursor:pointer;">&times;</button>
  </div>
  <input class="tf-glossary-search" type="text" placeholder="Search terms..." autocomplete="off">
  <div id="tfGlossaryList"></div>
</div>
"""


def get_tooltip_bundle() -> str:
    """Returns the complete CSS + JS + glossary panel HTML for inclusion in any page."""
    import json as _json
    js = TOOLTIP_JS.replace("##GLOSSARY_JSON##", _json.dumps(GLOSSARY))
    return f"<style>{TOOLTIP_CSS}</style>\n{GLOSSARY_PANEL_HTML}\n{js}"
