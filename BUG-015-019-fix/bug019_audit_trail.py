"""
BUG-019 FIX — Audit Trail / Activity Log
==========================================

System-wide activity logging for all write operations.
Stores logs in data/audit/audit_log.json (append-only JSONL format).

INSTRUCTIONS:

1. Add this file as: combined_calc/shop_drawings/audit_trail.py

2. Add handler classes to tf_handlers.py

3. Add routes to get_routes():
   (r"/api/audit-log", AuditLogHandler),
   (r"/api/audit-log/recent", AuditLogRecentHandler),
   (r"/admin/audit", AuditLogPageHandler),

4. Call log_action() from any handler where you want to track changes.
   Example usage in a handler:
     from shop_drawings.audit_trail import log_action
     log_action(BASE_DIR, "inventory.update", user="admin",
                details={"coil_id": "gusset_10ga", "field": "stock_lbs", "old": 1000, "new": 1500},
                job_code="SA-2024-001")
"""

import os
import json
import uuid
from datetime import datetime


# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────

ACTION_CATEGORIES = {
    # Project actions
    "project.create": "Project Created",
    "project.update": "Project Updated",
    "project.delete": "Project Deleted",

    # Estimate actions
    "sa.calculate": "SA Estimate Calculated",
    "sa.save": "SA Estimate Saved",
    "tc.save": "TC Quote Saved",
    "tc.export": "TC Quote Exported",

    # Work order actions
    "wo.create": "Work Order Created",
    "wo.status_change": "WO Status Changed",
    "wo.approve": "Work Order Approved",
    "wo.item_start": "WO Item Started",
    "wo.item_finish": "WO Item Finished",
    "wo.machine_reassign": "Machine Reassigned",
    "wo.rollback": "WO Status Rolled Back",

    # Inventory actions
    "inventory.receive": "Stock Received",
    "inventory.consume": "Stock Consumed",
    "inventory.adjust": "Stock Adjusted",
    "inventory.coil_create": "Coil Added",
    "inventory.coil_update": "Coil Updated",
    "inventory.coil_delete": "Coil Deleted",
    "inventory.po_create": "PO Created",
    "inventory.po_receive": "Received Against PO",

    # Field ops
    "fieldops.install_create": "Installation Created",
    "fieldops.status_change": "Install Status Changed",
    "fieldops.daily_log": "Daily Log Submitted",
    "fieldops.delay": "Delay Reported",

    # Admin actions
    "admin.user_create": "User Created",
    "admin.user_update": "User Updated",
    "admin.role_change": "User Role Changed",
    "admin.settings_change": "Settings Changed",

    # Shipping
    "shipping.create": "Shipment Created",
    "shipping.status_change": "Shipment Status Changed",
}

LOG_LEVELS = ["info", "warning", "critical"]


# ─────────────────────────────────────────────
# CORE FUNCTIONS
# ─────────────────────────────────────────────

def _audit_log_path(base_dir):
    return os.path.join(base_dir, "data", "audit", "audit_log.jsonl")


def log_action(base_dir, action, user="system", details=None, job_code="",
               level="info", ip_address=""):
    """Log an action to the audit trail.

    Args:
        base_dir: Application base directory
        action: Action key (e.g., "inventory.receive")
        user: Username/email who performed the action
        details: dict with action-specific details (old_value, new_value, etc.)
        job_code: Associated project job code (if applicable)
        level: "info", "warning", or "critical"
        ip_address: Client IP (if available)

    Returns:
        dict with log entry
    """
    log_path = _audit_log_path(base_dir)
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    entry = {
        "id": str(uuid.uuid4())[:12],
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "action": action,
        "action_label": ACTION_CATEGORIES.get(action, action),
        "user": user,
        "job_code": job_code,
        "level": level,
        "details": details or {},
        "ip_address": ip_address,
    }

    # Append to JSONL file (one JSON object per line)
    with open(log_path, "a") as f:
        f.write(json.dumps(entry, default=str) + "\n")

    return entry


def get_recent_logs(base_dir, limit=50, user=None, action=None,
                    job_code=None, level=None, since=None):
    """Get recent audit log entries with optional filtering.

    Args:
        base_dir: Application base directory
        limit: Max entries to return
        user: Filter by user
        action: Filter by action key (supports prefix, e.g., "inventory." matches all inventory actions)
        job_code: Filter by project
        level: Filter by level
        since: ISO timestamp — only entries after this time

    Returns:
        list of log entries (newest first)
    """
    log_path = _audit_log_path(base_dir)
    if not os.path.exists(log_path):
        return []

    entries = []
    try:
        with open(log_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    entries.append(entry)
                except json.JSONDecodeError:
                    continue
    except IOError:
        return []

    # Apply filters
    if user:
        entries = [e for e in entries if e.get("user", "").lower() == user.lower()]
    if action:
        entries = [e for e in entries if e.get("action", "").startswith(action)]
    if job_code:
        entries = [e for e in entries if e.get("job_code", "") == job_code]
    if level:
        entries = [e for e in entries if e.get("level", "") == level]
    if since:
        entries = [e for e in entries if e.get("timestamp", "") > since]

    # Sort newest first, limit
    entries.sort(key=lambda e: e.get("timestamp", ""), reverse=True)
    return entries[:limit]


def get_audit_stats(base_dir, days=7):
    """Get audit statistics for the dashboard.

    Returns:
        dict with counts by action category, user activity, etc.
    """
    from datetime import timedelta
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
    entries = get_recent_logs(base_dir, limit=10000, since=cutoff)

    stats = {
        "total_actions": len(entries),
        "by_category": {},
        "by_user": {},
        "by_level": {"info": 0, "warning": 0, "critical": 0},
        "by_day": {},
    }

    for e in entries:
        # By category (first part of action key)
        cat = e.get("action", "unknown").split(".")[0]
        stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1

        # By user
        user = e.get("user", "unknown")
        stats["by_user"][user] = stats["by_user"].get(user, 0) + 1

        # By level
        lvl = e.get("level", "info")
        stats["by_level"][lvl] = stats["by_level"].get(lvl, 0) + 1

        # By day
        day = e.get("timestamp", "")[:10]
        stats["by_day"][day] = stats["by_day"].get(day, 0) + 1

    return stats


# ─────────────────────────────────────────────
# HANDLER CLASSES (add to tf_handlers.py)
# ─────────────────────────────────────────────

"""
from shop_drawings.audit_trail import log_action, get_recent_logs, get_audit_stats, ACTION_CATEGORIES


class AuditLogHandler(BaseHandler):
    '''GET /api/audit-log — Query audit log with filters.

    Query params: limit, user, action, job_code, level, since
    '''
    required_roles = ["admin"]

    def get(self):
        try:
            limit = int(self.get_query_argument("limit", "50"))
            user = self.get_query_argument("user", None)
            action = self.get_query_argument("action", None)
            job_code = self.get_query_argument("job_code", None)
            level = self.get_query_argument("level", None)
            since = self.get_query_argument("since", None)

            entries = get_recent_logs(
                BASE_DIR, limit=limit, user=user, action=action,
                job_code=job_code, level=level, since=since
            )

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({
                "ok": True,
                "entries": entries,
                "count": len(entries),
                "action_categories": ACTION_CATEGORIES,
            }))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class AuditLogRecentHandler(BaseHandler):
    '''GET /api/audit-log/recent — Get recent activity + stats for dashboard widget.'''
    required_roles = ["admin", "estimator"]

    def get(self):
        try:
            entries = get_recent_logs(BASE_DIR, limit=20)
            stats = get_audit_stats(BASE_DIR, days=7)

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({
                "ok": True,
                "recent": entries,
                "stats": stats,
            }))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class AuditLogPageHandler(BaseHandler):
    '''GET /admin/audit — Audit trail viewer page.'''
    required_roles = ["admin"]

    def get(self):
        html = self._build_page()
        self.render_with_nav(html, active_page="admin")

    def _build_page(self):
        return '''<!DOCTYPE html><html><head><meta charset="UTF-8"/>
<title>Audit Trail — TitanForge</title>
<style>
:root { --tf-blue:#1E3A5F; --tf-red:#C0392B; --tf-green:#22C55E; --tf-orange:#F59E0B; }
* { margin:0;padding:0;box-sizing:border-box; }
body { font-family:'Segoe UI',system-ui,sans-serif;background:#F1F5F9;color:#1E293B; }
.audit-header { background:linear-gradient(135deg,#1E3A5F,#2C5282);color:white;padding:20px 32px; }
.audit-header h1 { font-size:1.4rem; }
.audit-content { padding:24px 32px;max-width:1200px; }
.filters { display:flex;gap:12px;margin-bottom:20px;flex-wrap:wrap;align-items:center;background:white;padding:12px 16px;border-radius:8px;border:1px solid #E2E8F0; }
.filters select,.filters input { padding:6px 10px;border:1.5px solid #D0D7E2;border-radius:6px;font-size:0.85rem; }
.filters button { padding:6px 16px;background:var(--tf-blue);color:white;border:none;border-radius:6px;cursor:pointer;font-weight:600;font-size:0.85rem; }
.log-table { width:100%;border-collapse:collapse;background:white;border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.08); }
.log-table th { background:var(--tf-blue);color:white;padding:8px 12px;text-align:left;font-size:0.8rem; }
.log-table td { padding:6px 12px;border-bottom:1px solid #E2E8F0;font-size:0.8rem; }
.log-table tr:hover { background:#F8FAFC; }
.level-info { color:var(--tf-blue); }
.level-warning { color:var(--tf-orange);font-weight:600; }
.level-critical { color:var(--tf-red);font-weight:700; }
.stats-row { display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:20px; }
.stat-card { background:white;border-radius:8px;padding:12px 16px;border-left:4px solid var(--tf-blue); }
.stat-card .value { font-size:1.5rem;font-weight:700;color:var(--tf-blue); }
.stat-card .label { font-size:0.7rem;color:#64748B;text-transform:uppercase; }
</style>
</head><body>
<div class="audit-header"><h1>&#128203; Audit Trail</h1><p style="font-size:0.85rem;opacity:0.8">System-wide activity log</p></div>
<div class="audit-content">
  <div class="stats-row" id="audit-stats"></div>
  <div class="filters">
    <select id="filter-action"><option value="">All Actions</option></select>
    <input type="text" id="filter-user" placeholder="User..."/>
    <input type="text" id="filter-job" placeholder="Job Code..."/>
    <select id="filter-level"><option value="">All Levels</option><option value="info">Info</option><option value="warning">Warning</option><option value="critical">Critical</option></select>
    <button onclick="loadAuditLog()">Filter</button>
  </div>
  <table class="log-table"><thead><tr>
    <th>Timestamp</th><th>Action</th><th>User</th><th>Project</th><th>Level</th><th>Details</th>
  </tr></thead><tbody id="audit-tbody"><tr><td colspan="6" style="text-align:center;padding:20px;color:#94A3B8">Loading...</td></tr></tbody></table>
</div>
<script>
async function loadAuditLog() {
  const params = new URLSearchParams();
  const action = document.getElementById("filter-action").value;
  const user = document.getElementById("filter-user").value.trim();
  const job = document.getElementById("filter-job").value.trim();
  const level = document.getElementById("filter-level").value;
  if (action) params.set("action", action);
  if (user) params.set("user", user);
  if (job) params.set("job_code", job);
  if (level) params.set("level", level);
  params.set("limit", "100");

  try {
    const resp = await fetch("/api/audit-log?" + params.toString());
    const data = await resp.json();
    if (data.ok) {
      renderLog(data.entries);
      populateActionFilter(data.action_categories);
    }
  } catch(e) { console.error(e); }
}
async function loadStats() {
  try {
    const resp = await fetch("/api/audit-log/recent");
    const data = await resp.json();
    if (data.ok && data.stats) {
      const s = data.stats;
      document.getElementById("audit-stats").innerHTML =
        '<div class="stat-card"><div class="value">'+s.total_actions+'</div><div class="label">Total (7 days)</div></div>'+
        '<div class="stat-card" style="border-color:#22C55E"><div class="value" style="color:#22C55E">'+Object.keys(s.by_user).length+'</div><div class="label">Active Users</div></div>'+
        '<div class="stat-card" style="border-color:#F59E0B"><div class="value" style="color:#F59E0B">'+(s.by_level.warning||0)+'</div><div class="label">Warnings</div></div>'+
        '<div class="stat-card" style="border-color:#EF4444"><div class="value" style="color:#EF4444">'+(s.by_level.critical||0)+'</div><div class="label">Critical</div></div>';
    }
  } catch(e) {}
}
function renderLog(entries) {
  const tbody = document.getElementById("audit-tbody");
  if (!entries.length) { tbody.innerHTML='<tr><td colspan="6" style="text-align:center;padding:20px;color:#94A3B8">No log entries found.</td></tr>'; return; }
  tbody.innerHTML = entries.map(e => {
    const ts = new Date(e.timestamp).toLocaleString();
    const details = e.details ? JSON.stringify(e.details).slice(0,80) : "";
    return '<tr><td>'+ts+'</td><td>'+e.action_label+'</td><td>'+e.user+'</td><td>'+(e.job_code||"-")+'</td><td class="level-'+e.level+'">'+e.level+'</td><td style="font-size:0.75rem;color:#64748B">'+details+'</td></tr>';
  }).join("");
}
function populateActionFilter(cats) {
  const sel = document.getElementById("filter-action");
  if (sel.options.length > 1) return;
  const prefixes = {};
  Object.keys(cats).forEach(k => { const p=k.split(".")[0]; prefixes[p]=true; });
  Object.keys(prefixes).sort().forEach(p => {
    const opt = document.createElement("option");
    opt.value = p + ".";
    opt.textContent = p.charAt(0).toUpperCase() + p.slice(1);
    sel.appendChild(opt);
  });
}
document.addEventListener("DOMContentLoaded", () => { loadStats(); loadAuditLog(); });
</script></body></html>'''
"""
