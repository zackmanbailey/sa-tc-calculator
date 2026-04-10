"""
TitanForge — Shop Floor Gamification Engine
============================================
Tracks worker performance, streaks, badges, and daily goals.
Data stored in data/shop_drawings/_gamification/ as JSON.

Features:
  - Per-worker stats: items completed, avg fab time, best time, streak
  - Achievement badges earned automatically
  - Daily/shift production targets with progress tracking
  - Leaderboard ranking
"""

import os
import json
import datetime
from typing import Dict, List, Optional


# ─────────────────────────────────────────────
# BADGE DEFINITIONS
# ─────────────────────────────────────────────

BADGES = {
    # Volume badges
    "first_blood":     {"name": "First Blood",       "icon": "⚡", "desc": "Complete your first item",           "threshold": 1},
    "ten_banger":      {"name": "Ten Banger",        "icon": "🔥", "desc": "Complete 10 items in one day",       "threshold": 10},
    "twenty_club":     {"name": "Twenty Club",       "icon": "💪", "desc": "Complete 20 items in one day",       "threshold": 20},
    "centurion":       {"name": "Centurion",         "icon": "🏆", "desc": "100 total items completed",          "threshold": 100},
    "five_hundred":    {"name": "500 Club",          "icon": "👑", "desc": "500 total items completed",          "threshold": 500},

    # Streak badges
    "streak_3":        {"name": "Hat Trick",         "icon": "🎯", "desc": "3-day work streak",                  "threshold": 3},
    "streak_5":        {"name": "On Fire",           "icon": "🔥", "desc": "5-day work streak",                  "threshold": 5},
    "streak_10":       {"name": "Unstoppable",       "icon": "⚡", "desc": "10-day work streak",                 "threshold": 10},
    "streak_20":       {"name": "Machine Mode",      "icon": "🤖", "desc": "20-day work streak",                 "threshold": 20},

    # Speed badges
    "speed_demon":     {"name": "Speed Demon",       "icon": "🏎️", "desc": "Finish an item in under 10 min",    "threshold": 10},
    "lightning":       {"name": "Lightning",         "icon": "⚡", "desc": "Finish an item in under 5 min",     "threshold": 5},

    # Specialty badges
    "welder_king":     {"name": "Welding King",      "icon": "👨‍🏭", "desc": "Complete 50 welded assemblies",     "threshold": 50},
    "roll_master":     {"name": "Roll Master",       "icon": "🔄", "desc": "Complete 100 roll-formed items",     "threshold": 100},
    "qc_champion":     {"name": "QC Champion",       "icon": "✅", "desc": "Pass 25 QC checkpoints in a row",   "threshold": 25},
    "early_bird":      {"name": "Early Bird",        "icon": "🐦", "desc": "First scan before 7 AM",            "threshold": 1},
    "night_owl":       {"name": "Night Owl",         "icon": "🦉", "desc": "Scan after 8 PM",                   "threshold": 1},
}

# Daily shift target (items per worker)
DEFAULT_DAILY_TARGET = 15


# ─────────────────────────────────────────────
# WORKER STATS DATA
# ─────────────────────────────────────────────

def _gam_dir(base_dir: str) -> str:
    d = os.path.join(base_dir, "_gamification")
    os.makedirs(d, exist_ok=True)
    return d


def _worker_path(base_dir: str, worker: str) -> str:
    safe = worker.replace("/", "_").replace("\\", "_").strip() or "unknown"
    return os.path.join(_gam_dir(base_dir), f"{safe}.json")


def _load_worker(base_dir: str, worker: str) -> dict:
    path = _worker_path(base_dir, worker)
    if os.path.isfile(path):
        with open(path) as f:
            return json.load(f)
    return {
        "worker": worker,
        "total_completed": 0,
        "total_fab_minutes": 0.0,
        "best_time_minutes": None,
        "avg_time_minutes": 0.0,
        "current_streak": 0,
        "longest_streak": 0,
        "last_active_date": None,
        "badges": [],
        "daily_log": {},       # {"2026-04-10": {"completed": 5, "minutes": 120}}
        "machine_counts": {},  # {"WELDING": 30, "ROLL FORM": 12}
        "qc_streak": 0,
    }


def _save_worker(base_dir: str, worker: str, data: dict):
    path = _worker_path(base_dir, worker)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# ─────────────────────────────────────────────
# RECORD A COMPLETION
# ─────────────────────────────────────────────

def record_completion(base_dir: str, worker: str, duration_minutes: float,
                      machine: str = "", component_type: str = "",
                      qc_passed: bool = True) -> dict:
    """
    Record that a worker finished an item. Updates stats, streak, badges.
    Returns: {"new_badges": [...], "stats": {...}, "celebration": str|None}
    """
    data = _load_worker(base_dir, worker)
    today = datetime.date.today().isoformat()
    now = datetime.datetime.now()

    # Ensure numeric types
    duration_minutes = float(duration_minutes)

    # Update totals
    data["total_completed"] += 1
    data["total_fab_minutes"] += duration_minutes
    data["avg_time_minutes"] = round(data["total_fab_minutes"] / data["total_completed"], 1)

    if data["best_time_minutes"] is None or duration_minutes < data["best_time_minutes"]:
        data["best_time_minutes"] = round(duration_minutes, 1)

    # Daily log
    if today not in data["daily_log"]:
        data["daily_log"][today] = {"completed": 0, "minutes": 0.0}
    data["daily_log"][today]["completed"] += 1
    data["daily_log"][today]["minutes"] += duration_minutes

    # Streak tracking
    last = data.get("last_active_date")
    if last:
        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        if last == today:
            pass  # Same day, streak continues
        elif last == yesterday:
            data["current_streak"] += 1
        else:
            data["current_streak"] = 1
    else:
        data["current_streak"] = 1
    data["last_active_date"] = today
    data["longest_streak"] = max(data["longest_streak"], data["current_streak"])

    # Machine counts
    if machine:
        data["machine_counts"][machine] = data["machine_counts"].get(machine, 0) + 1

    # QC streak
    if qc_passed:
        data["qc_streak"] = data.get("qc_streak", 0) + 1
    else:
        data["qc_streak"] = 0

    # ── Check for new badges ──
    existing = set(data["badges"])
    new_badges = []

    tc = data["total_completed"]
    dc = data["daily_log"][today]["completed"]
    streak = data["current_streak"]
    hour = now.hour

    # Volume
    if tc >= 1 and "first_blood" not in existing:
        new_badges.append("first_blood")
    if dc >= 10 and "ten_banger" not in existing:
        new_badges.append("ten_banger")
    if dc >= 20 and "twenty_club" not in existing:
        new_badges.append("twenty_club")
    if tc >= 100 and "centurion" not in existing:
        new_badges.append("centurion")
    if tc >= 500 and "five_hundred" not in existing:
        new_badges.append("five_hundred")

    # Streaks
    if streak >= 3 and "streak_3" not in existing:
        new_badges.append("streak_3")
    if streak >= 5 and "streak_5" not in existing:
        new_badges.append("streak_5")
    if streak >= 10 and "streak_10" not in existing:
        new_badges.append("streak_10")
    if streak >= 20 and "streak_20" not in existing:
        new_badges.append("streak_20")

    # Speed
    if duration_minutes <= 10 and "speed_demon" not in existing:
        new_badges.append("speed_demon")
    if duration_minutes <= 5 and "lightning" not in existing:
        new_badges.append("lightning")

    # Specialty
    weld_count = data["machine_counts"].get("WELDING", 0)
    if weld_count >= 50 and "welder_king" not in existing:
        new_badges.append("welder_king")
    roll_count = sum(v for k, v in data["machine_counts"].items()
                     if "ROLL" in k.upper() or "FORM" in k.upper())
    if roll_count >= 100 and "roll_master" not in existing:
        new_badges.append("roll_master")
    if data["qc_streak"] >= 25 and "qc_champion" not in existing:
        new_badges.append("qc_champion")
    if hour < 7 and "early_bird" not in existing:
        new_badges.append("early_bird")
    if hour >= 20 and "night_owl" not in existing:
        new_badges.append("night_owl")

    data["badges"].extend(new_badges)
    _save_worker(base_dir, worker, data)

    # Celebration message
    celebration = None
    if dc == 10:
        celebration = "10_items"
    elif dc == 20:
        celebration = "20_items"
    elif new_badges:
        celebration = "new_badge"

    return {
        "new_badges": [BADGES[b] for b in new_badges],
        "stats": {
            "total_completed": tc,
            "today_completed": dc,
            "avg_time": data["avg_time_minutes"],
            "best_time": data["best_time_minutes"],
            "streak": streak,
            "daily_target": DEFAULT_DAILY_TARGET,
            "daily_progress_pct": round(100.0 * dc / DEFAULT_DAILY_TARGET, 1),
        },
        "celebration": celebration,
    }


# ─────────────────────────────────────────────
# LEADERBOARD
# ─────────────────────────────────────────────

def get_leaderboard(base_dir: str, period: str = "today") -> List[dict]:
    """
    Get ranked leaderboard. period: 'today', 'week', 'alltime'.
    Returns list of {rank, worker, completed, avg_time, streak, badges_count}.
    """
    gam = _gam_dir(base_dir)
    today = datetime.date.today().isoformat()
    week_start = (datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())).isoformat()

    entries = []
    for fname in os.listdir(gam):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(gam, fname)) as f:
            data = json.load(f)

        if period == "today":
            day_data = data.get("daily_log", {}).get(today, {})
            completed = day_data.get("completed", 0)
        elif period == "week":
            completed = 0
            for date_str, day_data in data.get("daily_log", {}).items():
                if date_str >= week_start:
                    completed += day_data.get("completed", 0)
        else:
            completed = data.get("total_completed", 0)

        if completed == 0 and period != "alltime":
            continue

        entries.append({
            "worker": data.get("worker", fname.replace(".json", "")),
            "completed": completed,
            "avg_time": data.get("avg_time_minutes", 0),
            "streak": data.get("current_streak", 0),
            "badges_count": len(data.get("badges", [])),
            "badges": [BADGES[b] for b in data.get("badges", []) if b in BADGES],
        })

    entries.sort(key=lambda x: (-x["completed"], x["avg_time"]))
    for i, e in enumerate(entries):
        e["rank"] = i + 1

    return entries


def get_worker_stats(base_dir: str, worker: str) -> dict:
    """Get full stats for a specific worker."""
    data = _load_worker(base_dir, worker)
    today = datetime.date.today().isoformat()
    today_data = data.get("daily_log", {}).get(today, {"completed": 0, "minutes": 0})

    return {
        "worker": worker,
        "total_completed": data.get("total_completed", 0),
        "today_completed": today_data.get("completed", 0),
        "avg_time": data.get("avg_time_minutes", 0),
        "best_time": data.get("best_time_minutes"),
        "streak": data.get("current_streak", 0),
        "longest_streak": data.get("longest_streak", 0),
        "badges": [BADGES[b] for b in data.get("badges", []) if b in BADGES],
        "daily_target": DEFAULT_DAILY_TARGET,
        "daily_progress_pct": round(100.0 * today_data.get("completed", 0) / DEFAULT_DAILY_TARGET, 1),
        "machine_counts": data.get("machine_counts", {}),
    }


# ─────────────────────────────────────────────
# DAILY TARGETS
# ─────────────────────────────────────────────

def get_daily_targets(base_dir: str) -> dict:
    """Get shop-wide daily production targets and progress."""
    gam = _gam_dir(base_dir)
    today = datetime.date.today().isoformat()

    total_today = 0
    total_minutes = 0
    active_workers = 0

    for fname in os.listdir(gam):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(gam, fname)) as f:
            data = json.load(f)
        day = data.get("daily_log", {}).get(today, {})
        if day.get("completed", 0) > 0:
            active_workers += 1
            total_today += day["completed"]
            total_minutes += day.get("minutes", 0)

    shop_target = active_workers * DEFAULT_DAILY_TARGET if active_workers > 0 else DEFAULT_DAILY_TARGET

    return {
        "date": today,
        "shop_target": shop_target,
        "shop_completed": total_today,
        "shop_progress_pct": round(100.0 * total_today / shop_target, 1) if shop_target > 0 else 0,
        "active_workers": active_workers,
        "total_minutes": round(total_minutes, 1),
        "per_worker_target": DEFAULT_DAILY_TARGET,
    }
