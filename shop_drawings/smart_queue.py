"""
TitanForge — Smart Queue & Alert Engine
========================================
Auto-prioritizes work order items and generates shop floor alerts.

Features:
  - Priority scoring: due date urgency, dependency chain, machine availability
  - Idle machine detection with configurable threshold
  - QC checkpoint reminders
  - Bottleneck detection (machines falling behind)
  - Push-style alerts stored in JSON, consumed by dashboard/scanner
"""

import os
import json
import datetime
from typing import List, Dict, Optional, Tuple


# ─────────────────────────────────────────────
# PRIORITY SCORING
# ─────────────────────────────────────────────

PRIORITY_WEIGHTS = {
    "due_date":       40,   # How close to due date (0-40 points)
    "dependency":     25,   # Items blocking other items (0-25 points)
    "machine_idle":   20,   # Assigned machine is idle (0 or 20 points)
    "quantity":       10,   # Higher quantity = higher priority (0-10)
    "age":             5,   # How long it's been in queue (0-5)
}

# Urgency levels based on total score
URGENCY_LEVELS = {
    "critical": 80,   # Score >= 80 → red
    "high":     60,   # Score >= 60 → orange
    "normal":   30,   # Score >= 30 → yellow
    "low":       0,   # Score <  30 → gray
}

URGENCY_COLORS = {
    "critical": "#DC2626",
    "high":     "#F59E0B",
    "normal":   "#3B82F6",
    "low":      "#64748B",
}

# Idle threshold (minutes) before alerting
IDLE_THRESHOLD_MINUTES = 15

# QC checkpoint reminder (minutes after item started)
QC_REMINDER_MINUTES = {
    "column":  45,   # Remind to QC check columns after 45 min
    "rafter":  50,
    "purlin":  20,
    "default": 30,
}


# ─────────────────────────────────────────────
# PRIORITY CALCULATOR
# ─────────────────────────────────────────────

def score_item(item: dict, due_date: Optional[str] = None,
               machine_status: Optional[dict] = None,
               dependency_map: Optional[dict] = None) -> dict:
    """
    Calculate priority score for a work order item.
    Returns item dict with added 'priority_score', 'urgency', 'urgency_color' fields.
    """
    score = 0
    reasons = []

    # ── Due date urgency ──
    if due_date:
        try:
            due = datetime.date.fromisoformat(due_date)
            today = datetime.date.today()
            days_left = (due - today).days
            if days_left <= 0:
                score += 40
                reasons.append("OVERDUE")
            elif days_left <= 1:
                score += 35
                reasons.append("Due tomorrow")
            elif days_left <= 3:
                score += 25
                reasons.append(f"Due in {days_left} days")
            elif days_left <= 7:
                score += 15
                reasons.append(f"Due in {days_left} days")
            else:
                score += max(0, 10 - days_left)
        except (ValueError, TypeError):
            pass

    # ── Dependency chain ──
    item_id = item.get("item_id", "")
    if dependency_map and item_id in dependency_map:
        blocked_count = len(dependency_map[item_id])
        dep_score = min(25, blocked_count * 8)
        score += dep_score
        if blocked_count > 0:
            reasons.append(f"Blocking {blocked_count} items")

    # ── Machine idle bonus ──
    machine = item.get("machine", "")
    if machine_status and machine in machine_status:
        ms = machine_status[machine]
        if ms.get("in_progress", 0) == 0 and ms.get("queued", 0) > 0:
            score += 20
            reasons.append(f"{machine} is idle")

    # ── Quantity weight ──
    qty = item.get("quantity", 1)
    score += min(10, qty)

    # ── Age in queue ──
    created = item.get("created_at") or item.get("queued_at", "")
    if created:
        try:
            created_dt = datetime.datetime.fromisoformat(created.replace("Z", "+00:00"))
            age_hours = (datetime.datetime.now(datetime.timezone.utc) - created_dt).total_seconds() / 3600
            score += min(5, int(age_hours / 24))
            if age_hours > 48:
                reasons.append(f"In queue {int(age_hours/24)}d")
        except (ValueError, TypeError):
            pass

    # ── Determine urgency ──
    urgency = "low"
    for level, threshold in sorted(URGENCY_LEVELS.items(),
                                    key=lambda x: -x[1]):
        if score >= threshold:
            urgency = level
            break

    item["priority_score"] = score
    item["urgency"] = urgency
    item["urgency_color"] = URGENCY_COLORS.get(urgency, "#64748B")
    item["priority_reasons"] = reasons

    return item


def prioritize_queue(items: List[dict], due_date: Optional[str] = None,
                     machine_status: Optional[dict] = None) -> List[dict]:
    """
    Score and sort a list of items by priority (highest first).
    Only scores items that are not complete or in_progress.
    """
    scored = []
    for item in items:
        status = item.get("status", "queued")
        if status in ("complete",):
            item["priority_score"] = -1
            item["urgency"] = "done"
            item["urgency_color"] = "#10B981"
            item["priority_reasons"] = []
            scored.append(item)
            continue
        if status == "in_progress":
            item["priority_score"] = 999
            item["urgency"] = "active"
            item["urgency_color"] = "#10B981"
            item["priority_reasons"] = ["Currently in progress"]
            scored.append(item)
            continue

        scored.append(score_item(item, due_date, machine_status))

    scored.sort(key=lambda x: -x.get("priority_score", 0))
    return scored


# ─────────────────────────────────────────────
# ALERT ENGINE
# ─────────────────────────────────────────────

ALERT_TYPES = {
    "machine_idle":     {"icon": "⚠️", "color": "#F59E0B", "sound": "warning"},
    "qc_checkpoint":    {"icon": "✅", "color": "#3B82F6", "sound": "info"},
    "bottleneck":       {"icon": "🚨", "color": "#DC2626", "sound": "alarm"},
    "target_reached":   {"icon": "🎉", "color": "#10B981", "sound": "celebration"},
    "item_overdue":     {"icon": "⏰", "color": "#DC2626", "sound": "warning"},
    "shift_ending":     {"icon": "🕐", "color": "#F59E0B", "sound": "info"},
}


def _alerts_path(base_dir: str) -> str:
    d = os.path.join(base_dir, "_alerts")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "active.json")


def _load_alerts(base_dir: str) -> List[dict]:
    path = _alerts_path(base_dir)
    if os.path.isfile(path):
        with open(path) as f:
            return json.load(f)
    return []


def _save_alerts(base_dir: str, alerts: List[dict]):
    path = _alerts_path(base_dir)
    with open(path, "w") as f:
        json.dump(alerts, f, indent=2)


def generate_alerts(base_dir: str, machines: dict, items: List[dict],
                     daily_target: int = 15, daily_completed: int = 0) -> List[dict]:
    """
    Scan current state and generate/update alerts.
    Returns list of active alerts.
    """
    now = datetime.datetime.now()
    alerts = []

    # ── Idle machine alerts ──
    for machine_id, mdata in machines.items():
        in_prog = mdata.get("in_progress", 0)
        queued = mdata.get("queued", 0)
        name = mdata.get("name", machine_id)

        if in_prog == 0 and queued > 0:
            alerts.append({
                "type": "machine_idle",
                "machine": name,
                "message": f"{name} has {queued} items queued but nothing running",
                "icon": ALERT_TYPES["machine_idle"]["icon"],
                "color": ALERT_TYPES["machine_idle"]["color"],
                "timestamp": now.isoformat(),
                "priority": "high",
            })

    # ── QC checkpoint reminders ──
    for item in items:
        if item.get("status") != "in_progress":
            continue
        started = item.get("started_at", "")
        if not started:
            continue
        try:
            started_dt = datetime.datetime.fromisoformat(started.replace("Z", "+00:00"))
            elapsed_min = (now - started_dt.replace(tzinfo=None)).total_seconds() / 60
            comp_type = item.get("component_type", "default")
            threshold = QC_REMINDER_MINUTES.get(comp_type,
                        QC_REMINDER_MINUTES["default"])
            if elapsed_min >= threshold:
                alerts.append({
                    "type": "qc_checkpoint",
                    "item_id": item.get("item_id"),
                    "ship_mark": item.get("ship_mark", "?"),
                    "message": f"QC check needed: {item.get('ship_mark', '?')} — "
                               f"running {int(elapsed_min)} min (threshold: {threshold} min)",
                    "icon": ALERT_TYPES["qc_checkpoint"]["icon"],
                    "color": ALERT_TYPES["qc_checkpoint"]["color"],
                    "timestamp": now.isoformat(),
                    "priority": "medium",
                })
        except (ValueError, TypeError):
            pass

    # ── Bottleneck detection ──
    machine_loads = {}
    for item in items:
        if item.get("status") in ("queued", "approved", "stickers_printed"):
            m = item.get("machine", "")
            if m:
                machine_loads[m] = machine_loads.get(m, 0) + 1

    for m, count in machine_loads.items():
        if count >= 10:  # More than 10 items queued = bottleneck
            name = machines.get(m, {}).get("name", m)
            alerts.append({
                "type": "bottleneck",
                "machine": name,
                "message": f"Bottleneck: {name} has {count} items in queue",
                "icon": ALERT_TYPES["bottleneck"]["icon"],
                "color": ALERT_TYPES["bottleneck"]["color"],
                "timestamp": now.isoformat(),
                "priority": "critical",
            })

    # ── Daily target celebration ──
    if daily_completed >= daily_target and daily_target > 0:
        alerts.append({
            "type": "target_reached",
            "message": f"Daily target reached! {daily_completed}/{daily_target} items complete",
            "icon": ALERT_TYPES["target_reached"]["icon"],
            "color": ALERT_TYPES["target_reached"]["color"],
            "timestamp": now.isoformat(),
            "priority": "info",
        })

    # ── Shift ending warning (5:30 PM) ──
    if now.hour == 17 and now.minute >= 30:
        remaining = sum(1 for i in items if i.get("status") == "in_progress")
        if remaining > 0:
            alerts.append({
                "type": "shift_ending",
                "message": f"Shift ending soon — {remaining} items still in progress",
                "icon": ALERT_TYPES["shift_ending"]["icon"],
                "color": ALERT_TYPES["shift_ending"]["color"],
                "timestamp": now.isoformat(),
                "priority": "medium",
            })

    # Sort: critical first
    priority_order = {"critical": 0, "high": 1, "medium": 2, "info": 3}
    alerts.sort(key=lambda a: priority_order.get(a.get("priority", "info"), 99))

    _save_alerts(base_dir, alerts)
    return alerts


def dismiss_alert(base_dir: str, alert_index: int) -> bool:
    """Dismiss an alert by index."""
    alerts = _load_alerts(base_dir)
    if 0 <= alert_index < len(alerts):
        alerts.pop(alert_index)
        _save_alerts(base_dir, alerts)
        return True
    return False


def get_active_alerts(base_dir: str) -> List[dict]:
    """Get current active alerts."""
    return _load_alerts(base_dir)
