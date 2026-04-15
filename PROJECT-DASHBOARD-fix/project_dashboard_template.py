"""
PROJECT DASHBOARD — HTML Template
===================================

Single source-of-truth view for each project.
Shows colored status cards for every module:
  - Green (solid) = Complete — white text, green checkmark, version number
  - Blue (solid)  = In Progress — white text, spinner icon
  - Red (solid)   = Needs Completion — white text, link to appropriate screen
  - Amber (solid) = Needs Attention — white text, warning icon

INSTRUCTIONS:
1. Add this file as: combined_calc/templates/project_dashboard_template.py
2. Import in tf_handlers.py:
     from templates.project_dashboard_template import get_project_dashboard_html
3. Use in ProjectDashboardPageHandler.get() to render the page.
"""


def get_project_dashboard_html(job_code=None):
    """Return the full HTML for the project dashboard page.

    If job_code is provided, it auto-loads that project on page load.
    If None, shows the project selector.
    """
    auto_load_js = ""
    if job_code:
        auto_load_js = f'loadProject("{job_code}");'

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Project Dashboard — TitanForge</title>
<style>
:root {{
  --tf-blue: #1E3A5F;
  --tf-red: #EF4444;
  --tf-green: #22C55E;
  --tf-in-progress: #3B82F6;
  --tf-amber: #F59E0B;
  --tf-dark: #1E293B;
  --tf-light: #F1F5F9;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:'Segoe UI',system-ui,-apple-system,sans-serif; background:var(--tf-light); color:var(--tf-dark); }}

/* ── HEADER ── */
.dash-header {{
  background: linear-gradient(135deg, #1E3A5F 0%, #2C5282 100%);
  color: white;
  padding: 20px 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}}
.dash-header h1 {{ font-size:1.4rem; font-weight:700; }}
.dash-header .subtitle {{ font-size:0.85rem; opacity:0.8; }}

/* ── PROJECT SELECTOR ── */
.project-selector {{
  display: flex;
  align-items: center;
  gap: 10px;
}}
.project-selector select {{
  padding: 8px 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-radius: 8px;
  background: rgba(255,255,255,0.15);
  color: white;
  font-size: 0.9rem;
  font-weight: 600;
  min-width: 220px;
  cursor: pointer;
}}
.project-selector select option {{ color: #1E293B; background: white; }}
.project-selector select:focus {{ outline: none; border-color: rgba(255,255,255,0.6); }}

/* ── PROGRESS BAR ── */
.progress-section {{
  padding: 20px 32px 0;
  max-width: 1200px;
}}
.progress-bar-container {{
  background: #E2E8F0;
  border-radius: 12px;
  height: 18px;
  overflow: hidden;
  position: relative;
}}
.progress-bar-fill {{
  height: 100%;
  border-radius: 12px;
  background: linear-gradient(90deg, var(--tf-green), #16A34A);
  transition: width 0.6s ease;
  min-width: 0;
}}
.progress-label {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 6px;
  font-size: 0.8rem;
  color: #64748B;
}}
.progress-pct {{
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--tf-dark);
}}

/* ── MODULE CARDS GRID ── */
.modules-section {{
  padding: 24px 32px;
  max-width: 1200px;
}}
.modules-section h2 {{
  font-size: 1.1rem;
  color: var(--tf-dark);
  margin-bottom: 16px;
  font-weight: 700;
}}
.modules-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}}

/* ── MODULE CARD ── */
.module-card {{
  border-radius: 12px;
  padding: 20px;
  color: white;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  text-decoration: none;
  display: block;
}}
.module-card:hover {{
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}}

/* Status-specific card backgrounds */
.module-card.status-complete {{
  background: linear-gradient(135deg, #22C55E, #16A34A);
  border: 2px solid #16A34A;
}}
.module-card.status-in_progress {{
  background: linear-gradient(135deg, #3B82F6, #2563EB);
  border: 2px solid #2563EB;
}}
.module-card.status-not_started {{
  background: linear-gradient(135deg, #EF4444, #DC2626);
  border: 2px solid #DC2626;
}}
.module-card.status-needs_attention {{
  background: linear-gradient(135deg, #F59E0B, #D97706);
  border: 2px solid #D97706;
}}

.card-header {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}}
.card-icon {{
  font-size: 1.6rem;
  line-height: 1;
}}
.card-badge {{
  background: rgba(255,255,255,0.25);
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}}
.card-title {{
  font-size: 1.05rem;
  font-weight: 700;
  margin-bottom: 4px;
}}
.card-desc {{
  font-size: 0.78rem;
  opacity: 0.85;
  margin-bottom: 10px;
  line-height: 1.4;
}}

/* Status row: checkmark/x + version + details */
.card-status-row {{
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.8rem;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(255,255,255,0.2);
}}
.status-icon {{
  font-size: 1.1rem;
}}
.card-version {{
  background: rgba(255,255,255,0.3);
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 700;
}}
.card-detail {{
  font-size: 0.75rem;
  opacity: 0.85;
}}
.card-action {{
  display: inline-block;
  margin-top: 8px;
  padding: 5px 14px;
  background: rgba(255,255,255,0.25);
  border-radius: 6px;
  font-size: 0.78rem;
  font-weight: 600;
  color: white;
  text-decoration: none;
  transition: background 0.15s;
}}
.card-action:hover {{
  background: rgba(255,255,255,0.4);
}}

/* ── NEXT ACTION BANNER ── */
.next-action {{
  margin: 0 32px 20px;
  max-width: 1136px;
  padding: 14px 20px;
  background: linear-gradient(90deg, #1E3A5F, #2C5282);
  color: white;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}}
.next-action-text {{
  font-size: 0.9rem;
  font-weight: 600;
}}
.next-action-btn {{
  padding: 6px 18px;
  background: white;
  color: var(--tf-blue);
  border: none;
  border-radius: 6px;
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
  text-decoration: none;
}}
.next-action-btn:hover {{
  background: #E2E8F0;
}}

/* ── PROJECT META ── */
.project-meta {{
  padding: 0 32px;
  max-width: 1200px;
  margin-bottom: 16px;
}}
.meta-cards {{
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}}
.meta-card {{
  background: white;
  border-radius: 8px;
  padding: 10px 16px;
  border-left: 4px solid var(--tf-blue);
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}}
.meta-card .label {{ font-size:0.7rem; color:#64748B; text-transform:uppercase; font-weight:600; }}
.meta-card .value {{ font-size:1rem; font-weight:700; color:var(--tf-dark); }}

/* ── DEPENDENCY FLOW ── */
.dep-flow {{
  padding: 0 32px;
  max-width: 1200px;
  margin-bottom: 20px;
}}
.dep-flow h3 {{
  font-size: 0.85rem;
  color: #64748B;
  margin-bottom: 10px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}}
.flow-track {{
  display: flex;
  align-items: center;
  gap: 0;
  overflow-x: auto;
  padding-bottom: 8px;
}}
.flow-node {{
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 100px;
  text-align: center;
}}
.flow-dot {{
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  color: white;
  font-weight: 700;
}}
.flow-dot.complete {{ background: var(--tf-green); }}
.flow-dot.in_progress {{ background: var(--tf-in-progress); }}
.flow-dot.not_started {{ background: var(--tf-red); }}
.flow-dot.needs_attention {{ background: var(--tf-amber); }}
.flow-label {{
  font-size: 0.65rem;
  color: #64748B;
  margin-top: 4px;
  max-width: 90px;
  line-height: 1.2;
}}
.flow-arrow {{
  width: 30px;
  height: 2px;
  background: #CBD5E1;
  flex-shrink: 0;
  margin-bottom: 18px;
}}

/* ── EMPTY / LOADING STATE ── */
.empty-state {{
  text-align: center;
  padding: 80px 20px;
  color: #94A3B8;
}}
.empty-state .icon {{ font-size: 3rem; margin-bottom: 12px; }}
.empty-state p {{ font-size: 1rem; margin-bottom: 4px; }}
.empty-state .sub {{ font-size: 0.85rem; }}

.loading {{ text-align:center; padding:40px; color:#94A3B8; }}

/* ── TOAST ── */
.toast {{
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 12px 20px;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  font-size: 0.85rem;
  z-index: 10000;
  opacity: 0;
  transition: opacity 0.3s;
  max-width: 350px;
}}
.toast.show {{ opacity: 1; }}
.toast.success {{ background: #22C55E; }}
.toast.error {{ background: #EF4444; }}
.toast.info {{ background: #3B82F6; }}
</style>
</head>
<body>

<!-- HEADER -->
<div class="dash-header">
  <div>
    <h1>&#128203; Project Dashboard</h1>
    <div class="subtitle">Single source of truth — every module, every status</div>
  </div>
  <div class="project-selector">
    <select id="project-select" onchange="onProjectSelected(this.value)">
      <option value="">Select a Project...</option>
    </select>
  </div>
</div>

<!-- MAIN CONTENT (hidden until project loaded) -->
<div id="dashboard-content" style="display:none">

  <!-- Project metadata -->
  <div class="project-meta" style="margin-top:20px">
    <div class="meta-cards" id="meta-cards"></div>
  </div>

  <!-- Progress bar -->
  <div class="progress-section">
    <div class="progress-bar-container">
      <div class="progress-bar-fill" id="progress-fill" style="width:0%"></div>
    </div>
    <div class="progress-label">
      <span id="progress-text">0 of 7 modules complete</span>
      <span class="progress-pct" id="progress-pct">0%</span>
    </div>
  </div>

  <!-- Dependency flow visualization -->
  <div class="dep-flow" style="margin-top:20px">
    <h3>Pipeline Flow</h3>
    <div class="flow-track" id="flow-track"></div>
  </div>

  <!-- Next action banner -->
  <div id="next-action-container"></div>

  <!-- Module cards -->
  <div class="modules-section">
    <h2>Module Status</h2>
    <div class="modules-grid" id="modules-grid"></div>
  </div>
</div>

<!-- EMPTY STATE (shown when no project selected) -->
<div id="empty-state" class="empty-state">
  <div class="icon">&#128203;</div>
  <p>Select a project to view its dashboard</p>
  <div class="sub">Every module, every status, one source of truth</div>
</div>

<!-- LOADING -->
<div id="loading" class="loading" style="display:none">
  Loading project data...
</div>

<div id="toast" class="toast"></div>

<script>
// ─────────────────────────────────────────
// MODULE DEFINITIONS (mirrors project_tracker.py)
// ─────────────────────────────────────────
const MODULE_DEFS = [
  {{ key:"sa_estimate", label:"SA Estimator", icon:"&#127959;", urlTpl:"/sa?project={{job}}", description:"Structures America fabrication estimate", dependsOn:[] }},
  {{ key:"tc_estimate", label:"TC Estimator", icon:"&#128663;", urlTpl:"/tc?project={{job}}", description:"Titan Carports construction quote", dependsOn:["sa_estimate"] }},
  {{ key:"bom",         label:"Bill of Materials", icon:"&#128203;", urlTpl:"/project/{{job}}#bom", description:"Generated from SA estimate", dependsOn:["sa_estimate"] }},
  {{ key:"shop_drawings",label:"Shop Drawings", icon:"&#128208;", urlTpl:"/shop-drawings/{{job}}", description:"Fabrication drawings per component", dependsOn:["bom"] }},
  {{ key:"work_orders", label:"Work Orders", icon:"&#128203;", urlTpl:"/work-orders/{{job}}", description:"Shop floor fabrication tasks", dependsOn:["bom"] }},
  {{ key:"field_ops",   label:"Field Operations", icon:"&#127959;", urlTpl:"/field-ops?project={{job}}", description:"Installation tracking & crew dispatch", dependsOn:["work_orders"] }},
  {{ key:"shipping",    label:"Shipping", icon:"&#128666;", urlTpl:"/shipping/{{job}}", description:"Shipment management & tracking", dependsOn:["work_orders"] }},
];

const STATUS_LABELS = {{
  "not_started":     "Needs Completion",
  "in_progress":     "In Progress",
  "complete":        "Complete",
  "needs_attention": "Needs Attention",
}};

const STATUS_ICONS = {{
  "complete":        "&#9989;",
  "in_progress":     "&#9203;",
  "not_started":     "&#10060;",
  "needs_attention": "&#9888;&#65039;",
}};

let currentJobCode = "";
let currentState = null;

// ─────────────────────────────────────────
// INIT
// ─────────────────────────────────────────
document.addEventListener("DOMContentLoaded", async () => {{
  await loadProjectList();
  {auto_load_js}
}});

async function loadProjectList() {{
  try {{
    const resp = await fetch("/api/project-dashboard/list");
    const data = await resp.json();
    if (data.ok) {{
      const sel = document.getElementById("project-select");
      (data.projects || []).forEach(p => {{
        const opt = document.createElement("option");
        opt.value = p.job_code;
        opt.textContent = p.job_code + (p.name && p.name !== p.job_code ? " — " + p.name : "")
                        + (p.customer ? " (" + p.customer + ")" : "");
        sel.appendChild(opt);
      }});
      if (currentJobCode) sel.value = currentJobCode;
    }}
  }} catch(e) {{ console.error("Failed to load project list:", e); }}
}}

function onProjectSelected(jobCode) {{
  if (!jobCode) {{
    document.getElementById("dashboard-content").style.display = "none";
    document.getElementById("empty-state").style.display = "";
    return;
  }}
  loadProject(jobCode);
}}

async function loadProject(jobCode) {{
  currentJobCode = jobCode;
  document.getElementById("empty-state").style.display = "none";
  document.getElementById("dashboard-content").style.display = "none";
  document.getElementById("loading").style.display = "";

  // Update selector
  const sel = document.getElementById("project-select");
  if (sel.value !== jobCode) sel.value = jobCode;

  // Update URL without reload
  history.replaceState(null, "", "/project-dashboard/" + jobCode);

  try {{
    const resp = await fetch("/api/project-dashboard/state?job_code=" + encodeURIComponent(jobCode));
    const data = await resp.json();
    if (data.ok) {{
      currentState = data;
      renderDashboard(data);
    }} else {{
      showToast("Error loading project: " + (data.error || "Unknown"), "error");
    }}
  }} catch(e) {{
    showToast("Error: " + e.message, "error");
  }} finally {{
    document.getElementById("loading").style.display = "none";
  }}
}}

// ─────────────────────────────────────────
// RENDER
// ─────────────────────────────────────────
function renderDashboard(data) {{
  const state = data.state;
  const meta = data.meta || {{}};

  // Meta cards
  renderMeta(meta, state);

  // Progress bar
  renderProgress(state);

  // Flow visualization
  renderFlow(state);

  // Next action
  renderNextAction(state);

  // Module cards
  renderModules(state);

  document.getElementById("dashboard-content").style.display = "";
}}

function renderMeta(meta, state) {{
  const cards = document.getElementById("meta-cards");
  const complete = Object.values(state.modules).filter(m => m.status === "complete").length;
  const total = Object.keys(state.modules).length;

  let html = '';
  html += '<div class="meta-card"><div class="label">Job Code</div><div class="value">' + state.job_code + '</div></div>';
  if (meta.name || meta.project_name) {{
    html += '<div class="meta-card"><div class="label">Project Name</div><div class="value">' + (meta.name || meta.project_name) + '</div></div>';
  }}
  if (meta.customer_name) {{
    html += '<div class="meta-card"><div class="label">Customer</div><div class="value">' + meta.customer_name + '</div></div>';
  }}
  html += '<div class="meta-card"><div class="label">Modules Complete</div><div class="value">' + complete + ' / ' + total + '</div></div>';
  html += '<div class="meta-card"><div class="label">Last Scanned</div><div class="value">' + formatTime(state.scanned_at) + '</div></div>';
  cards.innerHTML = html;
}}

function renderProgress(state) {{
  const pct = state.overall_progress || 0;
  const complete = Object.values(state.modules).filter(m => m.status === "complete").length;
  const total = Object.keys(state.modules).length;

  document.getElementById("progress-fill").style.width = pct + "%";
  document.getElementById("progress-pct").textContent = pct + "%";
  document.getElementById("progress-text").textContent = complete + " of " + total + " modules complete";
}}

function renderFlow(state) {{
  const track = document.getElementById("flow-track");
  let html = "";
  MODULE_DEFS.forEach((mod, i) => {{
    const ms = state.modules[mod.key] || {{}};
    const st = ms.status || "not_started";
    html += '<div class="flow-node">';
    html += '  <div class="flow-dot ' + st + '">' + STATUS_ICONS[st] + '</div>';
    html += '  <div class="flow-label">' + mod.label + '</div>';
    html += '</div>';
    if (i < MODULE_DEFS.length - 1) {{
      html += '<div class="flow-arrow"></div>';
    }}
  }});
  track.innerHTML = html;
}}

function renderNextAction(state) {{
  const container = document.getElementById("next-action-container");
  if (!state.next_action) {{
    container.innerHTML = "";
    return;
  }}
  const na = state.next_action;
  container.innerHTML =
    '<div class="next-action">' +
    '  <span class="next-action-text">&#9889; ' + na.message + '</span>' +
    '  <a href="' + na.url + '" class="next-action-btn">Go to ' + na.label + ' &rarr;</a>' +
    '</div>';
}}

function renderModules(state) {{
  const grid = document.getElementById("modules-grid");
  let html = "";

  MODULE_DEFS.forEach(mod => {{
    const ms = state.modules[mod.key] || {{}};
    const st = ms.status || "not_started";
    const url = mod.urlTpl.replace("{{job}}", currentJobCode);

    html += '<a href="' + url + '" class="module-card status-' + st + '">';

    // Header: icon + badge
    html += '<div class="card-header">';
    html += '  <span class="card-icon">' + mod.icon + '</span>';
    html += '  <span class="card-badge">' + STATUS_LABELS[st] + '</span>';
    html += '</div>';

    // Title & description
    html += '<div class="card-title">' + mod.label + '</div>';
    html += '<div class="card-desc">' + mod.description + '</div>';

    // Status row with details
    html += '<div class="card-status-row">';
    html += '  <span class="status-icon">' + STATUS_ICONS[st] + '</span>';

    if (st === "complete") {{
      if (ms.version) {{
        html += '<span class="card-version">' + ms.version + '</span>';
      }}
      html += '<span class="card-detail">' + renderCompleteDetails(mod.key, ms) + '</span>';
    }} else if (st === "in_progress") {{
      html += '<span class="card-detail">' + renderProgressDetails(mod.key, ms) + '</span>';
    }} else if (st === "not_started") {{
      html += '<span class="card-detail">' + renderRequirements(mod) + '</span>';
    }} else if (st === "needs_attention") {{
      html += '<span class="card-detail">' + (ms.details?.error || "Review needed") + '</span>';
    }}

    html += '</div>';

    // Action link for incomplete items
    if (st === "not_started") {{
      html += '<span class="card-action">Open ' + mod.label + ' &rarr;</span>';
    }} else if (st === "in_progress") {{
      html += '<span class="card-action">Continue &rarr;</span>';
    }}

    html += '</a>';
  }});

  grid.innerHTML = html;
}}

function renderCompleteDetails(key, ms) {{
  const d = ms.details || {{}};
  switch(key) {{
    case "sa_estimate":
      return (d.buildings || 0) + " building(s), " + formatMoney(d.total_cost) + " material, " + formatNum(d.total_weight) + " lbs";
    case "tc_estimate":
      return "Sell: " + formatMoney(d.total_sell);
    case "bom":
      return (d.buildings || 0) + " building(s), " + (d.total_items || 0) + " line items";
    case "shop_drawings":
      return (d.drawing_count || 0) + " drawings generated";
    case "work_orders":
      return (d.complete || 0) + "/" + (d.total || 0) + " complete";
    case "field_ops":
      return (d.complete || 0) + "/" + (d.total || 0) + " installations done";
    case "shipping":
      return (d.shipment_count || 0) + " shipment(s)";
    default:
      return "Saved";
  }}
}}

function renderProgressDetails(key, ms) {{
  const d = ms.details || {{}};
  switch(key) {{
    case "work_orders":
      return (d.complete || 0) + " done, " + (d.in_progress || 0) + " in progress, " + (d.total || 0) + " total";
    case "field_ops":
      return (d.complete || 0) + " of " + (d.total || 0) + " installations";
    case "shipping":
      return (d.shipment_count || 0) + " shipment(s) processing";
    default:
      return "Work in progress";
  }}
}}

function renderRequirements(mod) {{
  if (mod.dependsOn.length === 0) return "Start here";
  return "Requires: " + mod.dependsOn.map(d => {{
    const def = MODULE_DEFS.find(m => m.key === d);
    return def ? def.label : d;
  }}).join(", ");
}}

// ─────────────────────────────────────────
// UTILITIES
// ─────────────────────────────────────────
function formatMoney(val) {{
  if (!val) return "$0";
  return "$" + Number(val).toLocaleString("en-US", {{minimumFractionDigits:0, maximumFractionDigits:0}});
}}
function formatNum(val) {{
  if (!val) return "0";
  return Number(val).toLocaleString("en-US");
}}
function formatTime(iso) {{
  if (!iso) return "—";
  try {{ return new Date(iso).toLocaleString(); }}
  catch {{ return iso; }}
}}
function showToast(msg, type) {{
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.className = "toast show " + (type || "info");
  setTimeout(() => {{ t.className = "toast"; }}, 3500);
}}
</script>
</body></html>'''
