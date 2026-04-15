"""
TitanForge — Production Scheduling & Gantt Data
================================================
Backend module for scheduling work orders, estimating completion times,
and calculating machine utilization for the Gantt view dashboard.

Functions:
  - get_gantt_data(shop_drawings_dir, projects_dir)
  - estimate_completion(items_list)
  - get_machine_utilization(shop_drawings_dir, days_ahead=14)
"""

import os
import json
import datetime
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, asdict


# ─────────────────────────────────────────────
# FABRICATION TIME CONSTANTS (in minutes)
# ─────────────────────────────────────────────

FAB_TIMES = {
    "column": 90,
    "rafter": 110,
    "purlin": 20,
    "sag_rod": 10,
    "clip": 8,
    "panel": 45,
    "trim": 15,
    "base_plate": 12,
    "gusset": 18,
    "plate": 15,
}

DEFAULT_FAB_TIME = 30  # fallback if component type not known


# ─────────────────────────────────────────────
# ESTIMATE_COMPLETION
# ─────────────────────────────────────────────

def estimate_completion(items_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Estimate fabrication completion time based on work order items.

    Assumes:
      - 8-hour workday (480 minutes)
      - 2 machines running in parallel
      - Sequential processing per machine

    Args:
        items_list: List of WorkOrderItem dicts with component_type, quantity, machine

    Returns:
        {
            estimated_hours: float,
            estimated_days: float,
            completion_date: ISO date string (or None if no items)
        }
    """
    if not items_list:
        return {
            "estimated_hours": 0,
            "estimated_days": 0,
            "completion_date": None,
        }

    # Group items by machine to estimate parallel processing
    machine_times = {}
    for item in items_list:
        machine = item.get("machine", "UNKNOWN")
        component_type = item.get("component_type", "unknown")
        quantity = item.get("quantity", 1)

        # Get base time per component
        base_time = FAB_TIMES.get(component_type, DEFAULT_FAB_TIME)
        total_time = base_time * quantity

        if machine not in machine_times:
            machine_times[machine] = 0
        machine_times[machine] += total_time

    # Bottleneck is the machine with most work (parallel execution)
    if machine_times:
        total_minutes = max(machine_times.values())
    else:
        total_minutes = 0

    # Convert to hours and days
    workday_minutes = 480  # 8 hours
    estimated_hours = total_minutes / 60.0
    estimated_days = total_minutes / workday_minutes

    # Round up to nearest half day
    estimated_days = round(estimated_days * 2) / 2
    if estimated_days < 0.5:
        estimated_days = 0.5

    completion_date = None
    if estimated_days > 0:
        today = datetime.datetime.now()
        completion = today + datetime.timedelta(days=estimated_days)
        completion_date = completion.strftime("%Y-%m-%d")

    return {
        "estimated_hours": round(estimated_hours, 1),
        "estimated_days": estimated_days,
        "completion_date": completion_date,
    }


# ─────────────────────────────────────────────
# GET_MACHINE_UTILIZATION
# ─────────────────────────────────────────────

def get_machine_utilization(shop_drawings_dir: str, days_ahead: int = 14) -> Dict[str, List[Dict[str, Any]]]:
    """
    Calculate per-machine daily utilization over the next N days.

    Returns dict mapping machine_name → list of daily records:
    [
        {
            "date": "2026-04-10",
            "item_count": 5,
            "jobs": ["2026-0001", "2026-0002"],
            "is_overloaded": bool (>15 items)
        },
        ...
    ]

    Args:
        shop_drawings_dir: Path to shop_drawings directory
        days_ahead: Number of days to look ahead

    Returns:
        Dict mapping machine names to daily utilization
    """
    machine_schedule = {}
    today = datetime.datetime.now()

    # Scan all jobs for active work orders
    try:
        for job_code in os.listdir(shop_drawings_dir):
            job_path = os.path.join(shop_drawings_dir, job_code)
            if not os.path.isdir(job_path):
                continue

            wo_dir = os.path.join(job_path, "work_orders")
            if not os.path.isdir(wo_dir):
                continue

            # Load each work order
            for wo_file in os.listdir(wo_dir):
                if not wo_file.endswith(".json"):
                    continue

                wo_path = os.path.join(wo_dir, wo_file)
                try:
                    with open(wo_path, 'r') as f:
                        wo_data = json.load(f)
                except:
                    continue

                # Skip completed work orders
                if wo_data.get("status") == "complete":
                    continue

                # Process items
                items = wo_data.get("items", [])
                if not items:
                    continue

                created_at = wo_data.get("created_at", "")
                try:
                    wo_date = datetime.datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                except:
                    wo_date = today

                # Distribute work across the next days_ahead period
                for item in items:
                    machine = item.get("machine", "UNASSIGNED")
                    status = item.get("status", "queued")

                    # Skip completed items
                    if status == "complete":
                        continue

                    if machine not in machine_schedule:
                        machine_schedule[machine] = {}

                    # Estimate item start date (when it would start processing)
                    # For now, assume it starts on the day the WO was created
                    item_date = wo_date.strftime("%Y-%m-%d")

                    if item_date not in machine_schedule[machine]:
                        machine_schedule[machine][item_date] = {
                            "date": item_date,
                            "item_count": 0,
                            "jobs": set(),
                            "is_overloaded": False,
                        }

                    machine_schedule[machine][item_date]["item_count"] += 1
                    machine_schedule[machine][item_date]["jobs"].add(job_code)

    except Exception as e:
        # If directory doesn't exist or scan fails, return empty
        pass

    # Convert sets to lists and check for overload
    result = {}
    for machine, daily_data in machine_schedule.items():
        result[machine] = []
        for date_str, data in sorted(daily_data.items()):
            is_overloaded = data["item_count"] > 15
            result[machine].append({
                "date": date_str,
                "item_count": data["item_count"],
                "jobs": list(data["jobs"]),
                "is_overloaded": is_overloaded,
            })

    return result


# ─────────────────────────────────────────────
# GET_GANTT_DATA
# ─────────────────────────────────────────────

def get_gantt_data(shop_drawings_dir: str, projects_dir: str) -> Dict[str, Any]:
    """
    Aggregate all scheduling data for the Gantt view.

    Returns:
    {
        "today": "2026-04-10",
        "jobs": [
            {
                "job_code": "2026-0001",
                "name": "Acme Corp Warehouse",
                "customer": "Acme Corporation",
                "due_date": "2026-05-01",
                "start_date": "2026-04-01",
                "items_total": 24,
                "items_complete": 6,
                "items_in_progress": 3,
                "items_queued": 15,
                "estimated_days": 5.5,
                "estimated_completion": "2026-04-15",
                "machines_used": ["PressBrake", "Shear"],
                "status": "active",
                "work_orders": [
                    {
                        "work_order_id": "wo_abc123",
                        "revision": "R2",
                        "status": "in_progress",
                        "created_at": "2026-04-01T08:00:00Z",
                        "items": [...]
                    }
                ]
            },
            ...
        ],
        "machine_schedule": {
            "PressBrake": [
                {"date": "2026-04-10", "item_count": 8, "jobs": [...], "is_overloaded": false}
            ]
        }
    }
    """
    today = datetime.datetime.now()
    today_str = today.strftime("%Y-%m-%d")

    jobs_data = []

    try:
        # Iterate through all projects
        for job_code in os.listdir(projects_dir):
            job_proj_path = os.path.join(projects_dir, job_code)
            if not os.path.isdir(job_proj_path):
                continue

            # Load project metadata
            meta_path = os.path.join(job_proj_path, "metadata.json")
            if not os.path.exists(meta_path):
                continue

            try:
                with open(meta_path, 'r') as f:
                    proj_meta = json.load(f)
            except:
                continue

            # Skip inactive projects
            status = proj_meta.get("status", "").lower()
            if status in ["completed", "cancelled", "on_hold"]:
                continue

            # Load work orders for this job
            shop_job_path = os.path.join(shop_drawings_dir, job_code)
            wo_dir = os.path.join(shop_job_path, "work_orders")

            work_orders = []
            all_items = []
            all_machines = set()
            items_complete = 0
            items_in_progress = 0
            items_queued = 0
            earliest_created = None

            if os.path.isdir(wo_dir):
                for wo_file in os.listdir(wo_dir):
                    if not wo_file.endswith(".json"):
                        continue

                    wo_path = os.path.join(wo_dir, wo_file)
                    try:
                        with open(wo_path, 'r') as f:
                            wo_data = json.load(f)
                    except:
                        continue

                    # Skip if not active
                    wo_status = wo_data.get("status", "")
                    if wo_status == "complete":
                        continue

                    # Track earliest creation
                    created_at = wo_data.get("created_at", "")
                    if created_at:
                        if earliest_created is None:
                            earliest_created = created_at
                        else:
                            if created_at < earliest_created:
                                earliest_created = created_at

                    items = wo_data.get("items", [])
                    all_items.extend(items)

                    # Count item statuses
                    for item in items:
                        item_status = item.get("status", "queued")
                        if item_status == "complete":
                            items_complete += 1
                        elif item_status == "in_progress":
                            items_in_progress += 1
                        else:
                            items_queued += 1

                        machine = item.get("machine", "")
                        if machine:
                            all_machines.add(machine)

                    work_orders.append({
                        "work_order_id": wo_data.get("work_order_id", ""),
                        "revision": wo_data.get("revision", ""),
                        "status": wo_status,
                        "created_at": created_at,
                        "items": items,
                    })

            # Estimate completion
            completion_data = estimate_completion(all_items)

            # Build job record
            job_record = {
                "job_code": job_code,
                "name": proj_meta.get("name", job_code),
                "customer": proj_meta.get("customer", ""),
                "due_date": proj_meta.get("due_date", ""),
                "start_date": earliest_created[:10] if earliest_created else today_str,
                "items_total": items_complete + items_in_progress + items_queued,
                "items_complete": items_complete,
                "items_in_progress": items_in_progress,
                "items_queued": items_queued,
                "estimated_days": completion_data["estimated_days"],
                "estimated_completion": completion_data["completion_date"],
                "machines_used": sorted(list(all_machines)),
                "status": "active",
                "work_orders": work_orders,
            }

            jobs_data.append(job_record)

    except Exception as e:
        pass

    # Sort jobs by due date
    jobs_data.sort(key=lambda j: j.get("due_date", "9999-12-31"))

    # Get machine utilization
    machine_schedule = get_machine_utilization(shop_drawings_dir, days_ahead=14)

    return {
        "today": today_str,
        "jobs": jobs_data,
        "machine_schedule": machine_schedule,
    }
