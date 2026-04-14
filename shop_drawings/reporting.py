"""
TitanForge v4 — Reporting & Analytics Engine
==============================================
Aggregation layer that pulls metrics from all subsystems:
  - Work Orders (get_shop_floor_summary, cycle times, throughput)
  - Shipping (get_shipping_summary, on-time delivery)
  - Field Ops (get_field_summary, punch list health)
  - QC (inspection pass rates)

Produces cross-cutting reports for PMs, executives, and plant managers.

Reference: RULES.md §3 (Role Definitions — view_financials, view_project_pnl)
"""

import os
import json
import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from collections import defaultdict

from shop_drawings.work_orders import (
    WorkOrder, WorkOrderItem,
    VALID_STATUSES, STATUS_LABELS, STATUS_COLORS,
    PHASE_PREFAB, PHASE_FABRICATION, PHASE_QC, PHASE_SHIPPING,
    STATUS_IN_PROGRESS, STATUS_FABRICATED, STATUS_QC_APPROVED,
    STATUS_QC_REJECTED, STATUS_INSTALLED, STATUS_ON_HOLD,
    MACHINE_TYPES,
    load_work_order, list_work_orders, list_all_work_orders,
    get_shop_floor_summary,
)
from shop_drawings.shipping import (
    LOAD_STATUS_BUILDING, LOAD_STATUS_READY, LOAD_STATUS_IN_TRANSIT,
    LOAD_STATUS_DELIVERED, LOAD_STATUS_COMPLETE,
    list_loads, get_shipping_summary,
)
from shop_drawings.field_ops import (
    get_project_completion, get_field_summary,
    load_punch_items, load_all_punch_items,
    load_daily_reports, load_installation_records,
    PUNCH_STATUS_OPEN, PUNCH_STATUS_IN_PROGRESS as PUNCH_IN_PROGRESS,
    PUNCH_STATUS_RESOLVED, PUNCH_STATUS_VERIFIED,
    PUNCH_PRIORITY_CRITICAL, PUNCH_PRIORITY_HIGH,
)


# ─────────────────────────────────────────────
# REPORT TYPES
# ─────────────────────────────────────────────

REPORT_PRODUCTION_METRICS = "production_metrics"
REPORT_EXECUTIVE_SUMMARY = "executive_summary"
REPORT_OPERATOR_PERFORMANCE = "operator_performance"
REPORT_PROJECT_STATUS = "project_status"
REPORT_DELIVERY_ANALYSIS = "delivery_analysis"
REPORT_QC_ANALYSIS = "qc_analysis"

REPORT_TYPES = [
    REPORT_PRODUCTION_METRICS,
    REPORT_EXECUTIVE_SUMMARY,
    REPORT_OPERATOR_PERFORMANCE,
    REPORT_PROJECT_STATUS,
    REPORT_DELIVERY_ANALYSIS,
    REPORT_QC_ANALYSIS,
]

REPORT_LABELS = {
    REPORT_PRODUCTION_METRICS: "Production Metrics",
    REPORT_EXECUTIVE_SUMMARY: "Executive Summary",
    REPORT_OPERATOR_PERFORMANCE: "Operator Performance",
    REPORT_PROJECT_STATUS: "Project Status",
    REPORT_DELIVERY_ANALYSIS: "Delivery Analysis",
    REPORT_QC_ANALYSIS: "QC Analysis",
}


# ─────────────────────────────────────────────
# TIME PERIOD HELPERS
# ─────────────────────────────────────────────

def _today() -> str:
    return datetime.date.today().isoformat()

def _days_ago(n: int) -> str:
    return (datetime.date.today() - datetime.timedelta(days=n)).isoformat()

def _this_week_start() -> str:
    today = datetime.date.today()
    return (today - datetime.timedelta(days=today.weekday())).isoformat()

def _this_month_start() -> str:
    today = datetime.date.today()
    return today.replace(day=1).isoformat()

def _parse_iso(s: str) -> Optional[datetime.datetime]:
    """Parse an ISO timestamp, returning None on failure."""
    if not s:
        return None
    try:
        return datetime.datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return None

def _date_from_iso(s: str) -> Optional[str]:
    """Extract YYYY-MM-DD from an ISO datetime string."""
    if not s:
        return None
    return s[:10] if len(s) >= 10 else None


# ─────────────────────────────────────────────
# CORE: Load all WO items with enriched data
# ─────────────────────────────────────────────

def _load_all_wo_items(wo_base_dir: str) -> List[dict]:
    """Load every WO item across all projects with job_code and wo_id context."""
    results = []
    if not os.path.isdir(wo_base_dir):
        return results
    for project_dir in os.listdir(wo_base_dir):
        wo_dir = os.path.join(wo_base_dir, project_dir, "work_orders")
        if not os.path.isdir(wo_dir):
            continue
        for fname in os.listdir(wo_dir):
            if not fname.endswith(".json"):
                continue
            try:
                wo = load_work_order(wo_base_dir, project_dir, fname.replace(".json", ""))
                if not wo:
                    continue
                for item in wo.items:
                    d = item.to_dict()
                    d["job_code"] = wo.job_code
                    d["work_order_id"] = wo.work_order_id
                    results.append(d)
            except Exception:
                continue
    return results


# ─────────────────────────────────────────────
# PRODUCTION METRICS REPORT
# ─────────────────────────────────────────────

def get_production_metrics(wo_base_dir: str, shipping_base_dir: str,
                           field_base_dir: str,
                           days_back: int = 30) -> dict:
    """
    Comprehensive production metrics report.
    Covers throughput, cycle times, machine utilization,
    bottleneck detection, and trend data.
    """
    all_items = _load_all_wo_items(wo_base_dir)
    cutoff = _days_ago(days_back)
    today = _today()

    # ── Overall counts ─────────────────────────
    total_items = len(all_items)
    status_counts = defaultdict(int)
    for item in all_items:
        status_counts[item.get("status", "unknown")] += 1

    # ── Throughput: items completed per day in last N days ──
    completed_items = []
    for item in all_items:
        finished = item.get("finished_at", "")
        if finished and _date_from_iso(finished) and _date_from_iso(finished) >= cutoff:
            completed_items.append(item)

    days_map = defaultdict(int)
    for item in completed_items:
        day = _date_from_iso(item["finished_at"])
        if day:
            days_map[day] += 1

    # Build daily throughput series
    throughput_series = []
    d = datetime.date.today() - datetime.timedelta(days=days_back)
    while d <= datetime.date.today():
        ds = d.isoformat()
        throughput_series.append({"date": ds, "count": days_map.get(ds, 0)})
        d += datetime.timedelta(days=1)

    avg_daily_throughput = round(len(completed_items) / max(days_back, 1), 1)

    # ── Cycle times (started_at → finished_at) ──
    cycle_times = []
    for item in all_items:
        started = _parse_iso(item.get("started_at", ""))
        finished = _parse_iso(item.get("finished_at", ""))
        if started and finished and finished > started:
            mins = (finished - started).total_seconds() / 60.0
            cycle_times.append({
                "item_id": item.get("item_id"),
                "job_code": item.get("job_code"),
                "machine": item.get("machine", ""),
                "minutes": round(mins, 1),
            })

    avg_cycle_time = round(
        sum(c["minutes"] for c in cycle_times) / max(len(cycle_times), 1), 1
    )

    # ── Machine utilization ──
    machine_stats = {}
    for m_key, m_info in MACHINE_TYPES.items():
        m_items = [i for i in all_items if i.get("machine") == m_key]
        active = len([i for i in m_items if i.get("status") == STATUS_IN_PROGRESS])
        queued = len([i for i in m_items
                      if i.get("status") in ["queued", "approved", "stickers_printed", "staged"]])
        completed = len([i for i in m_items if i.get("finished_at")])
        total_mins = sum(i.get("duration_minutes", 0) for i in m_items)

        # Cycle time for this machine
        m_cycles = [c for c in cycle_times if c["machine"] == m_key]
        avg_m_cycle = round(
            sum(c["minutes"] for c in m_cycles) / max(len(m_cycles), 1), 1
        ) if m_cycles else 0.0

        machine_stats[m_key] = {
            "label": m_info["label"],
            "active": active,
            "queued": queued,
            "completed": completed,
            "total_minutes": round(total_mins, 1),
            "avg_cycle_minutes": avg_m_cycle,
        }

    # ── Bottleneck detection ──
    bottlenecks = []
    # Items on hold
    on_hold = [i for i in all_items if i.get("status") == STATUS_ON_HOLD]
    if on_hold:
        bottlenecks.append({
            "type": "on_hold",
            "label": "Items on Hold",
            "count": len(on_hold),
            "severity": "high" if len(on_hold) > 5 else "medium",
        })

    # QC rejected items (need rework)
    rejected = [i for i in all_items if i.get("status") == "qc_rejected"]
    if rejected:
        bottlenecks.append({
            "type": "qc_rejected",
            "label": "QC Rejections (Rework)",
            "count": len(rejected),
            "severity": "high" if len(rejected) > 3 else "medium",
        })

    # Queued items waiting too long (>3 days since approved)
    stale_queued = []
    for item in all_items:
        if item.get("status") in ["approved", "stickers_printed"] and not item.get("started_at"):
            # Rough check: if assigned_at is old
            assigned = _parse_iso(item.get("assigned_at", ""))
            if assigned:
                age_days = (datetime.datetime.now() - assigned).days
                if age_days > 3:
                    stale_queued.append(item)
    if stale_queued:
        bottlenecks.append({
            "type": "stale_queued",
            "label": "Items Waiting >3 Days",
            "count": len(stale_queued),
            "severity": "medium",
        })

    # ── Items needing attention ──
    needs_attention = [i for i in all_items if i.get("needs_attention")]

    # ── Phase distribution ──
    phase_dist = {"prefab": 0, "fabrication": 0, "qc": 0, "shipping": 0, "installed": 0, "on_hold": 0}
    for item in all_items:
        s = item.get("status", "")
        if s in ["queued", "approved", "stickers_printed", "staged"]:
            phase_dist["prefab"] += 1
        elif s in ["in_progress", "fabricated"]:
            phase_dist["fabrication"] += 1
        elif s in ["qc_pending", "qc_approved", "qc_rejected"]:
            phase_dist["qc"] += 1
        elif s in ["ready_to_ship", "shipped", "delivered"]:
            phase_dist["shipping"] += 1
        elif s == "installed":
            phase_dist["installed"] += 1
        elif s == "on_hold":
            phase_dist["on_hold"] += 1

    return {
        "report_type": REPORT_PRODUCTION_METRICS,
        "generated_at": datetime.datetime.now().isoformat(),
        "period_days": days_back,
        "total_items": total_items,
        "status_counts": dict(status_counts),
        "phase_distribution": phase_dist,
        "throughput": {
            "avg_daily": avg_daily_throughput,
            "total_completed": len(completed_items),
            "series": throughput_series,
        },
        "cycle_times": {
            "avg_minutes": avg_cycle_time,
            "total_tracked": len(cycle_times),
            "by_machine": {m: machine_stats[m]["avg_cycle_minutes"] for m in machine_stats},
        },
        "machine_utilization": machine_stats,
        "bottlenecks": bottlenecks,
        "needs_attention_count": len(needs_attention),
    }


# ─────────────────────────────────────────────
# EXECUTIVE SUMMARY REPORT
# ─────────────────────────────────────────────

def get_executive_summary(wo_base_dir: str, shipping_base_dir: str,
                          field_base_dir: str) -> dict:
    """
    High-level executive dashboard combining all subsystems.
    KPIs: active projects, total items, completion rate, shipping pipeline,
    field progress, punch list health.
    """
    # Shop floor
    shop_summary = get_shop_floor_summary(wo_base_dir)

    # Shipping
    ship_summary = get_shipping_summary(shipping_base_dir)

    # Field
    field_summary = get_field_summary(wo_base_dir, field_base_dir)

    # All WO items for additional analysis
    all_items = _load_all_wo_items(wo_base_dir)
    total_items = len(all_items)

    # Projects
    all_wo_summaries = list_all_work_orders(wo_base_dir)
    project_codes = set()
    for s in all_wo_summaries:
        jc = s.get("job_code", "")
        if jc:
            project_codes.add(jc)

    # Fabrication progress
    fab_complete = len([i for i in all_items
                        if i.get("status") in ["fabricated", "qc_pending", "qc_approved",
                                                "ready_to_ship", "shipped", "delivered", "installed"]])
    fab_pct = round(fab_complete / max(total_items, 1) * 100, 1)

    # QC metrics
    qc_approved = len([i for i in all_items if i.get("qc_result") == "approved"])
    qc_rejected = len([i for i in all_items if i.get("qc_result") == "rejected"])
    qc_total = qc_approved + qc_rejected
    qc_pass_rate = round(qc_approved / max(qc_total, 1) * 100, 1)

    # On-time shipping (loads delivered vs total non-building)
    loads = list_loads(shipping_base_dir)
    delivered_loads = len([l for l in loads if l.status in [LOAD_STATUS_DELIVERED, LOAD_STATUS_COMPLETE]])
    shipped_loads = len([l for l in loads if l.status != LOAD_STATUS_BUILDING])
    on_time_pct = round(delivered_loads / max(shipped_loads, 1) * 100, 1) if shipped_loads > 0 else 0.0

    # Today's activity
    today = _today()
    items_completed_today = len([i for i in all_items
                                  if i.get("finished_at", "")[:10] == today])
    items_started_today = len([i for i in all_items
                                if i.get("started_at", "")[:10] == today])

    # Weekly trend
    week_start = _this_week_start()
    items_completed_this_week = len([i for i in all_items
                                     if _date_from_iso(i.get("finished_at", "")) and
                                     _date_from_iso(i["finished_at"]) >= week_start])

    return {
        "report_type": REPORT_EXECUTIVE_SUMMARY,
        "generated_at": datetime.datetime.now().isoformat(),
        "kpis": {
            "active_projects": len(project_codes),
            "total_items": total_items,
            "fabrication_complete_pct": fab_pct,
            "qc_pass_rate": qc_pass_rate,
            "on_time_delivery_pct": on_time_pct,
            "field_completion_pct": field_summary.get("overall_completion_pct", 0),
            "open_punch_items": field_summary.get("total_open_punches", 0),
        },
        "today": {
            "items_started": items_started_today,
            "items_completed": items_completed_today,
        },
        "this_week": {
            "items_completed": items_completed_this_week,
        },
        "shop_floor": {
            "machines": {m: {"active": v["active"], "queued": v["queued"]}
                         for m, v in shop_summary.get("machines", {}).items()},
            "status_counts": shop_summary.get("status_counts", {}),
            "total_fab_minutes": shop_summary.get("total_fab_minutes", 0),
            "needs_attention": len(shop_summary.get("needs_attention", [])),
        },
        "shipping": {
            "total_loads": ship_summary.get("total_loads", 0),
            "building": ship_summary.get("building", 0),
            "ready": ship_summary.get("ready", 0),
            "in_transit": ship_summary.get("in_transit", 0),
            "delivered": ship_summary.get("delivered", 0),
            "complete": ship_summary.get("complete", 0),
            "total_items_shipped": ship_summary.get("total_items_shipped", 0),
            "total_weight_shipped": ship_summary.get("total_weight_shipped", 0),
        },
        "field": {
            "active_projects": field_summary.get("active_projects", 0),
            "total_installed": field_summary.get("total_installed", 0),
            "total_delivered": field_summary.get("total_delivered", 0),
            "open_punches": field_summary.get("total_open_punches", 0),
            "critical_punches": field_summary.get("total_critical_punches", 0),
        },
    }


# ─────────────────────────────────────────────
# OPERATOR PERFORMANCE REPORT
# ─────────────────────────────────────────────

def get_operator_performance(wo_base_dir: str, days_back: int = 30) -> dict:
    """
    Per-operator metrics: items completed, avg cycle time,
    QC pass rate, items in progress.
    """
    all_items = _load_all_wo_items(wo_base_dir)
    cutoff = _days_ago(days_back)

    operators = defaultdict(lambda: {
        "items_completed": 0,
        "items_in_progress": 0,
        "items_assigned": 0,
        "total_minutes": 0.0,
        "cycle_times": [],
        "qc_approved": 0,
        "qc_rejected": 0,
        "machines_used": set(),
    })

    for item in all_items:
        assigned = item.get("assigned_to", "")
        if not assigned:
            continue

        op = operators[assigned]
        op["items_assigned"] += 1

        if item.get("status") == STATUS_IN_PROGRESS:
            op["items_in_progress"] += 1

        # Completed in period?
        finished = item.get("finished_at", "")
        if finished and _date_from_iso(finished) and _date_from_iso(finished) >= cutoff:
            op["items_completed"] += 1

        # Cycle time
        started = _parse_iso(item.get("started_at", ""))
        finished_dt = _parse_iso(finished)
        if started and finished_dt and finished_dt > started:
            mins = (finished_dt - started).total_seconds() / 60.0
            op["total_minutes"] += mins
            op["cycle_times"].append(mins)

        # QC results
        if item.get("qc_result") == "approved":
            op["qc_approved"] += 1
        elif item.get("qc_result") == "rejected":
            op["qc_rejected"] += 1

        # Machines
        m = item.get("machine", "")
        if m:
            op["machines_used"].add(m)

    # Build output
    operator_list = []
    for username, data in sorted(operators.items()):
        total_qc = data["qc_approved"] + data["qc_rejected"]
        avg_cycle = round(
            sum(data["cycle_times"]) / max(len(data["cycle_times"]), 1), 1
        ) if data["cycle_times"] else 0.0

        operator_list.append({
            "username": username,
            "items_assigned": data["items_assigned"],
            "items_completed": data["items_completed"],
            "items_in_progress": data["items_in_progress"],
            "total_minutes": round(data["total_minutes"], 1),
            "avg_cycle_minutes": avg_cycle,
            "qc_pass_rate": round(data["qc_approved"] / max(total_qc, 1) * 100, 1) if total_qc > 0 else 0.0,
            "qc_approved": data["qc_approved"],
            "qc_rejected": data["qc_rejected"],
            "machines_used": sorted(data["machines_used"]),
        })

    # Sort by items completed (desc)
    operator_list.sort(key=lambda x: x["items_completed"], reverse=True)

    return {
        "report_type": REPORT_OPERATOR_PERFORMANCE,
        "generated_at": datetime.datetime.now().isoformat(),
        "period_days": days_back,
        "total_operators": len(operator_list),
        "operators": operator_list,
    }


# ─────────────────────────────────────────────
# PROJECT STATUS REPORT
# ─────────────────────────────────────────────

def get_project_status_report(wo_base_dir: str, shipping_base_dir: str,
                               field_base_dir: str) -> dict:
    """
    Per-project status breakdown: fabrication progress, shipping status,
    field completion, and punch list health for each active project.
    """
    all_items = _load_all_wo_items(wo_base_dir)

    # Group by project
    by_project = defaultdict(list)
    for item in all_items:
        by_project[item.get("job_code", "UNKNOWN")].append(item)

    projects = []
    for job_code in sorted(by_project.keys()):
        items = by_project[job_code]
        total = len(items)

        # Status breakdown
        status_counts = defaultdict(int)
        for item in items:
            status_counts[item.get("status", "unknown")] += 1

        # Phase progress
        prefab = len([i for i in items if i.get("status") in ["queued", "approved", "stickers_printed", "staged"]])
        fab = len([i for i in items if i.get("status") in ["in_progress", "fabricated"]])
        qc = len([i for i in items if i.get("status") in ["qc_pending", "qc_approved", "qc_rejected"]])
        shipping = len([i for i in items if i.get("status") in ["ready_to_ship", "shipped", "delivered"]])
        installed = len([i for i in items if i.get("status") == "installed"])
        on_hold = len([i for i in items if i.get("status") == "on_hold"])

        # Fab completion (past fabricated)
        past_fab = len([i for i in items
                        if i.get("status") in ["fabricated", "qc_pending", "qc_approved",
                                                "ready_to_ship", "shipped", "delivered", "installed"]])
        fab_pct = round(past_fab / max(total, 1) * 100, 1)

        # Field completion
        field_pct = round(installed / max(total, 1) * 100, 1)

        # QC results for this project
        qc_approved = len([i for i in items if i.get("qc_result") == "approved"])
        qc_rejected = len([i for i in items if i.get("qc_result") == "rejected"])

        # Punch items
        try:
            punches = load_punch_items(field_base_dir, job_code)
            open_punches = len([p for p in punches if p.status in [PUNCH_STATUS_OPEN, PUNCH_IN_PROGRESS]])
            critical_punches = len([p for p in punches
                                    if p.priority == PUNCH_PRIORITY_CRITICAL
                                    and p.status not in [PUNCH_STATUS_VERIFIED]])
        except Exception:
            open_punches = 0
            critical_punches = 0

        projects.append({
            "job_code": job_code,
            "total_items": total,
            "status_counts": dict(status_counts),
            "phases": {
                "prefab": prefab,
                "fabrication": fab,
                "qc": qc,
                "shipping": shipping,
                "installed": installed,
                "on_hold": on_hold,
            },
            "fabrication_complete_pct": fab_pct,
            "field_complete_pct": field_pct,
            "qc_approved": qc_approved,
            "qc_rejected": qc_rejected,
            "open_punches": open_punches,
            "critical_punches": critical_punches,
        })

    return {
        "report_type": REPORT_PROJECT_STATUS,
        "generated_at": datetime.datetime.now().isoformat(),
        "total_projects": len(projects),
        "projects": projects,
    }


# ─────────────────────────────────────────────
# DELIVERY ANALYSIS REPORT
# ─────────────────────────────────────────────

def get_delivery_analysis(shipping_base_dir: str, field_base_dir: str,
                          wo_base_dir: str) -> dict:
    """
    Shipping and delivery metrics: loads by status, delivery timeline,
    items per load averages, weight shipped by project.
    """
    loads = list_loads(shipping_base_dir)

    # Status counts
    status_counts = defaultdict(int)
    for load in loads:
        status_counts[load.status] += 1

    # Items per load
    items_per_load = [load.total_items for load in loads if load.total_items > 0]
    avg_items_per_load = round(
        sum(items_per_load) / max(len(items_per_load), 1), 1
    ) if items_per_load else 0.0

    # Weight per load
    weights = [load.total_weight for load in loads if load.total_weight > 0]
    avg_weight_per_load = round(
        sum(weights) / max(len(weights), 1), 1
    ) if weights else 0.0

    # Delivery timeline (shipped_at → delivered_at)
    delivery_times = []
    for load in loads:
        shipped = _parse_iso(load.shipped_at)
        delivered = _parse_iso(load.delivered_at)
        if shipped and delivered and delivered > shipped:
            hours = (delivered - shipped).total_seconds() / 3600.0
            delivery_times.append({
                "load_id": load.load_id,
                "hours": round(hours, 1),
            })

    avg_delivery_hours = round(
        sum(d["hours"] for d in delivery_times) / max(len(delivery_times), 1), 1
    ) if delivery_times else 0.0

    # Shipments by project
    by_project = defaultdict(lambda: {"loads": 0, "items": 0, "weight": 0})
    for load in loads:
        project_codes = set()
        for li in load.items:
            project_codes.add(li.job_code)
        for pc in project_codes:
            by_project[pc]["loads"] += 1
        for li in load.items:
            by_project[li.job_code]["items"] += 1
            by_project[li.job_code]["weight"] += li.weight_lbs

    shipments_by_project = [
        {"job_code": jc, **data}
        for jc, data in sorted(by_project.items())
    ]

    # Recent deliveries
    recent_deliveries = []
    for load in sorted(loads, key=lambda l: l.delivered_at or "", reverse=True):
        if load.delivered_at:
            recent_deliveries.append({
                "load_id": load.load_id,
                "load_number": load.load_number,
                "delivered_at": load.delivered_at,
                "total_items": load.total_items,
                "total_weight": load.total_weight,
                "status": load.status,
            })
    recent_deliveries = recent_deliveries[:15]

    return {
        "report_type": REPORT_DELIVERY_ANALYSIS,
        "generated_at": datetime.datetime.now().isoformat(),
        "total_loads": len(loads),
        "status_counts": dict(status_counts),
        "avg_items_per_load": avg_items_per_load,
        "avg_weight_per_load": avg_weight_per_load,
        "delivery_times": {
            "avg_hours": avg_delivery_hours,
            "total_tracked": len(delivery_times),
        },
        "shipments_by_project": shipments_by_project,
        "recent_deliveries": recent_deliveries,
    }


# ─────────────────────────────────────────────
# QC ANALYSIS REPORT
# ─────────────────────────────────────────────

def get_qc_analysis(wo_base_dir: str) -> dict:
    """
    QC pass/fail rates, rejection reasons, inspector activity,
    rework time analysis.
    """
    all_items = _load_all_wo_items(wo_base_dir)

    # Items that went through QC
    qc_items = [i for i in all_items if i.get("qc_result")]
    approved = [i for i in qc_items if i.get("qc_result") == "approved"]
    rejected = [i for i in qc_items if i.get("qc_result") == "rejected"]

    pass_rate = round(len(approved) / max(len(qc_items), 1) * 100, 1) if qc_items else 0.0

    # By inspector
    by_inspector = defaultdict(lambda: {"approved": 0, "rejected": 0, "total": 0})
    for item in qc_items:
        inspector = item.get("qc_inspector", "unknown")
        by_inspector[inspector]["total"] += 1
        if item.get("qc_result") == "approved":
            by_inspector[inspector]["approved"] += 1
        else:
            by_inspector[inspector]["rejected"] += 1

    inspector_stats = []
    for name, data in sorted(by_inspector.items()):
        inspector_stats.append({
            "inspector": name,
            "total_inspections": data["total"],
            "approved": data["approved"],
            "rejected": data["rejected"],
            "pass_rate": round(data["approved"] / max(data["total"], 1) * 100, 1),
        })

    # By machine (rejection rate)
    by_machine = defaultdict(lambda: {"approved": 0, "rejected": 0})
    for item in qc_items:
        m = item.get("machine", "unknown")
        if item.get("qc_result") == "approved":
            by_machine[m]["approved"] += 1
        else:
            by_machine[m]["rejected"] += 1

    machine_qc = []
    for m, data in sorted(by_machine.items()):
        total = data["approved"] + data["rejected"]
        machine_qc.append({
            "machine": m,
            "total": total,
            "approved": data["approved"],
            "rejected": data["rejected"],
            "rejection_rate": round(data["rejected"] / max(total, 1) * 100, 1),
        })

    # Rejection notes analysis
    rejection_notes = [i.get("qc_notes", "") for i in rejected if i.get("qc_notes")]

    # Items currently awaiting QC
    awaiting_qc = len([i for i in all_items if i.get("status") in ["fabricated", "qc_pending"]])

    # Currently rejected (needs rework)
    needs_rework = len([i for i in all_items if i.get("status") == "qc_rejected"])

    return {
        "report_type": REPORT_QC_ANALYSIS,
        "generated_at": datetime.datetime.now().isoformat(),
        "total_inspected": len(qc_items),
        "approved": len(approved),
        "rejected": len(rejected),
        "pass_rate": pass_rate,
        "awaiting_qc": awaiting_qc,
        "needs_rework": needs_rework,
        "by_inspector": inspector_stats,
        "by_machine": machine_qc,
        "rejection_note_count": len(rejection_notes),
    }


# ─────────────────────────────────────────────
# UNIFIED REPORT GENERATOR
# ─────────────────────────────────────────────

def generate_report(report_type: str, wo_base_dir: str,
                    shipping_base_dir: str, field_base_dir: str,
                    **kwargs) -> dict:
    """Generate a report by type. Returns report dict or error."""
    if report_type not in REPORT_TYPES:
        return {"ok": False, "error": f"Unknown report type: {report_type}. Valid: {REPORT_TYPES}"}

    try:
        if report_type == REPORT_PRODUCTION_METRICS:
            data = get_production_metrics(
                wo_base_dir, shipping_base_dir, field_base_dir,
                days_back=kwargs.get("days_back", 30)
            )
        elif report_type == REPORT_EXECUTIVE_SUMMARY:
            data = get_executive_summary(wo_base_dir, shipping_base_dir, field_base_dir)
        elif report_type == REPORT_OPERATOR_PERFORMANCE:
            data = get_operator_performance(
                wo_base_dir, days_back=kwargs.get("days_back", 30)
            )
        elif report_type == REPORT_PROJECT_STATUS:
            data = get_project_status_report(wo_base_dir, shipping_base_dir, field_base_dir)
        elif report_type == REPORT_DELIVERY_ANALYSIS:
            data = get_delivery_analysis(shipping_base_dir, field_base_dir, wo_base_dir)
        elif report_type == REPORT_QC_ANALYSIS:
            data = get_qc_analysis(wo_base_dir)
        else:
            return {"ok": False, "error": f"Report type not implemented: {report_type}"}

        return {"ok": True, "report": data}

    except Exception as e:
        return {"ok": False, "error": f"Report generation failed: {str(e)}"}


def list_available_reports() -> List[dict]:
    """List all available report types with labels."""
    return [
        {"type": rt, "label": REPORT_LABELS.get(rt, rt)}
        for rt in REPORT_TYPES
    ]
