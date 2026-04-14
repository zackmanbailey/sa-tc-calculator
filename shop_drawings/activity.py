"""
TitanForge v4 — Activity Feed, Audit Trail & Notification System
=================================================================
Cross-cutting accountability layer. Every significant action across the
platform gets logged as an ActivityEvent. Alert rules trigger notifications
when specific conditions are met.

Storage: data/activity/events.json (append-only log)
         data/activity/alerts.json (alert rules)
         data/activity/notifications.json (user notifications)

Reference: RULES.md §2 (Roles & Permissions — view_audit_log)
"""

import os
import json
import datetime
import secrets
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from collections import defaultdict


# ─────────────────────────────────────────────
# EVENT CATEGORIES
# ─────────────────────────────────────────────

CAT_WORK_ORDER = "work_order"
CAT_QC = "qc"
CAT_SHIPPING = "shipping"
CAT_FIELD = "field"
CAT_PUNCH = "punch"
CAT_PROJECT = "project"
CAT_USER = "user"
CAT_SYSTEM = "system"
CAT_INVENTORY = "inventory"

EVENT_CATEGORIES = [
    CAT_WORK_ORDER, CAT_QC, CAT_SHIPPING, CAT_FIELD,
    CAT_PUNCH, CAT_PROJECT, CAT_USER, CAT_SYSTEM, CAT_INVENTORY,
]

CATEGORY_LABELS = {
    CAT_WORK_ORDER: "Work Order",
    CAT_QC: "Quality Control",
    CAT_SHIPPING: "Shipping",
    CAT_FIELD: "Field Ops",
    CAT_PUNCH: "Punch List",
    CAT_PROJECT: "Project",
    CAT_USER: "User",
    CAT_SYSTEM: "System",
    CAT_INVENTORY: "Inventory",
}

CATEGORY_COLORS = {
    CAT_WORK_ORDER: "blue",
    CAT_QC: "purple",
    CAT_SHIPPING: "amber",
    CAT_FIELD: "green",
    CAT_PUNCH: "red",
    CAT_PROJECT: "blue",
    CAT_USER: "gray",
    CAT_SYSTEM: "gray",
    CAT_INVENTORY: "amber",
}

# ─────────────────────────────────────────────
# EVENT SEVERITY LEVELS
# ─────────────────────────────────────────────

SEVERITY_INFO = "info"
SEVERITY_WARNING = "warning"
SEVERITY_CRITICAL = "critical"
SEVERITY_SUCCESS = "success"

SEVERITY_LEVELS = [SEVERITY_INFO, SEVERITY_WARNING, SEVERITY_CRITICAL, SEVERITY_SUCCESS]

SEVERITY_LABELS = {
    SEVERITY_INFO: "Info",
    SEVERITY_WARNING: "Warning",
    SEVERITY_CRITICAL: "Critical",
    SEVERITY_SUCCESS: "Success",
}


# ─────────────────────────────────────────────
# EVENT TYPES (specific actions)
# ─────────────────────────────────────────────

# Work Order events
EVT_WO_CREATED = "wo_created"
EVT_WO_APPROVED = "wo_approved"
EVT_ITEM_ASSIGNED = "item_assigned"
EVT_ITEM_STARTED = "item_started"
EVT_ITEM_COMPLETED = "item_completed"
EVT_ITEM_STATUS_CHANGED = "item_status_changed"
EVT_ITEM_ON_HOLD = "item_on_hold"

# QC events
EVT_QC_APPROVED = "qc_approved"
EVT_QC_REJECTED = "qc_rejected"
EVT_NCR_CREATED = "ncr_created"
EVT_INSPECTION_CREATED = "inspection_created"

# Shipping events
EVT_LOAD_CREATED = "load_created"
EVT_LOAD_READY = "load_ready"
EVT_LOAD_SHIPPED = "load_shipped"
EVT_LOAD_DELIVERED = "load_delivered"
EVT_LOAD_COMPLETE = "load_complete"
EVT_BOL_GENERATED = "bol_generated"

# Field events
EVT_INSTALL_CONFIRMED = "install_confirmed"
EVT_DAILY_REPORT = "daily_report"

# Punch events
EVT_PUNCH_CREATED = "punch_created"
EVT_PUNCH_RESOLVED = "punch_resolved"
EVT_PUNCH_VERIFIED = "punch_verified"
EVT_PUNCH_CRITICAL = "punch_critical"

# Project events
EVT_PROJECT_CREATED = "project_created"
EVT_PROJECT_UPDATED = "project_updated"
EVT_PROJECT_CAN_CLOSE = "project_can_close"

# User events
EVT_USER_LOGIN = "user_login"
EVT_USER_CREATED = "user_created"

# System events
EVT_SYSTEM_ERROR = "system_error"

EVENT_TYPES = [
    EVT_WO_CREATED, EVT_WO_APPROVED, EVT_ITEM_ASSIGNED, EVT_ITEM_STARTED,
    EVT_ITEM_COMPLETED, EVT_ITEM_STATUS_CHANGED, EVT_ITEM_ON_HOLD,
    EVT_QC_APPROVED, EVT_QC_REJECTED, EVT_NCR_CREATED, EVT_INSPECTION_CREATED,
    EVT_LOAD_CREATED, EVT_LOAD_READY, EVT_LOAD_SHIPPED, EVT_LOAD_DELIVERED,
    EVT_LOAD_COMPLETE, EVT_BOL_GENERATED,
    EVT_INSTALL_CONFIRMED, EVT_DAILY_REPORT,
    EVT_PUNCH_CREATED, EVT_PUNCH_RESOLVED, EVT_PUNCH_VERIFIED, EVT_PUNCH_CRITICAL,
    EVT_PROJECT_CREATED, EVT_PROJECT_UPDATED, EVT_PROJECT_CAN_CLOSE,
    EVT_USER_LOGIN, EVT_USER_CREATED,
    EVT_SYSTEM_ERROR,
]

EVENT_LABELS = {
    EVT_WO_CREATED: "Work Order Created",
    EVT_WO_APPROVED: "Work Order Approved",
    EVT_ITEM_ASSIGNED: "Item Assigned",
    EVT_ITEM_STARTED: "Item Started",
    EVT_ITEM_COMPLETED: "Item Completed",
    EVT_ITEM_STATUS_CHANGED: "Item Status Changed",
    EVT_ITEM_ON_HOLD: "Item Put On Hold",
    EVT_QC_APPROVED: "QC Approved",
    EVT_QC_REJECTED: "QC Rejected",
    EVT_NCR_CREATED: "NCR Created",
    EVT_INSPECTION_CREATED: "Inspection Created",
    EVT_LOAD_CREATED: "Load Created",
    EVT_LOAD_READY: "Load Ready to Ship",
    EVT_LOAD_SHIPPED: "Load Shipped",
    EVT_LOAD_DELIVERED: "Load Delivered",
    EVT_LOAD_COMPLETE: "Load Complete",
    EVT_BOL_GENERATED: "BOL Generated",
    EVT_INSTALL_CONFIRMED: "Installation Confirmed",
    EVT_DAILY_REPORT: "Daily Report Submitted",
    EVT_PUNCH_CREATED: "Punch Item Created",
    EVT_PUNCH_RESOLVED: "Punch Item Resolved",
    EVT_PUNCH_VERIFIED: "Punch Item Verified",
    EVT_PUNCH_CRITICAL: "Critical Punch Item",
    EVT_PROJECT_CREATED: "Project Created",
    EVT_PROJECT_UPDATED: "Project Updated",
    EVT_PROJECT_CAN_CLOSE: "Project Ready to Close",
    EVT_USER_LOGIN: "User Login",
    EVT_USER_CREATED: "User Created",
    EVT_SYSTEM_ERROR: "System Error",
}

# Default severity for event types
EVENT_DEFAULT_SEVERITY = {
    EVT_WO_CREATED: SEVERITY_INFO,
    EVT_WO_APPROVED: SEVERITY_SUCCESS,
    EVT_ITEM_ASSIGNED: SEVERITY_INFO,
    EVT_ITEM_STARTED: SEVERITY_INFO,
    EVT_ITEM_COMPLETED: SEVERITY_SUCCESS,
    EVT_ITEM_STATUS_CHANGED: SEVERITY_INFO,
    EVT_ITEM_ON_HOLD: SEVERITY_WARNING,
    EVT_QC_APPROVED: SEVERITY_SUCCESS,
    EVT_QC_REJECTED: SEVERITY_WARNING,
    EVT_NCR_CREATED: SEVERITY_WARNING,
    EVT_INSPECTION_CREATED: SEVERITY_INFO,
    EVT_LOAD_CREATED: SEVERITY_INFO,
    EVT_LOAD_READY: SEVERITY_INFO,
    EVT_LOAD_SHIPPED: SEVERITY_SUCCESS,
    EVT_LOAD_DELIVERED: SEVERITY_SUCCESS,
    EVT_LOAD_COMPLETE: SEVERITY_SUCCESS,
    EVT_BOL_GENERATED: SEVERITY_INFO,
    EVT_INSTALL_CONFIRMED: SEVERITY_SUCCESS,
    EVT_DAILY_REPORT: SEVERITY_INFO,
    EVT_PUNCH_CREATED: SEVERITY_WARNING,
    EVT_PUNCH_RESOLVED: SEVERITY_SUCCESS,
    EVT_PUNCH_VERIFIED: SEVERITY_SUCCESS,
    EVT_PUNCH_CRITICAL: SEVERITY_CRITICAL,
    EVT_PROJECT_CREATED: SEVERITY_INFO,
    EVT_PROJECT_UPDATED: SEVERITY_INFO,
    EVT_PROJECT_CAN_CLOSE: SEVERITY_SUCCESS,
    EVT_USER_LOGIN: SEVERITY_INFO,
    EVT_USER_CREATED: SEVERITY_INFO,
    EVT_SYSTEM_ERROR: SEVERITY_CRITICAL,
}


# ─────────────────────────────────────────────
# DATA MODELS
# ─────────────────────────────────────────────

@dataclass
class ActivityEvent:
    """A single auditable event in the system."""
    event_id: str = ""
    event_type: str = ""            # From EVENT_TYPES
    category: str = ""              # From EVENT_CATEGORIES
    severity: str = SEVERITY_INFO   # From SEVERITY_LEVELS
    timestamp: str = ""             # ISO datetime
    actor: str = ""                 # Username who performed the action
    job_code: str = ""              # Related project (if any)
    entity_type: str = ""           # "work_order", "item", "load", "punch", etc.
    entity_id: str = ""             # ID of the affected entity
    title: str = ""                 # Human-readable summary
    description: str = ""           # Detailed description
    metadata: dict = field(default_factory=dict)  # Extra key-value data
    ip_address: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "ActivityEvent":
        evt = cls()
        for k, v in d.items():
            if hasattr(evt, k):
                setattr(evt, k, v)
        return evt

    @property
    def event_label(self) -> str:
        return EVENT_LABELS.get(self.event_type, self.event_type)

    @property
    def category_label(self) -> str:
        return CATEGORY_LABELS.get(self.category, self.category)

    @property
    def category_color(self) -> str:
        return CATEGORY_COLORS.get(self.category, "gray")

    @property
    def severity_label(self) -> str:
        return SEVERITY_LABELS.get(self.severity, self.severity)


@dataclass
class AlertRule:
    """A rule that generates notifications when matching events occur."""
    rule_id: str = ""
    name: str = ""
    enabled: bool = True
    event_types: list = field(default_factory=list)    # Match these event types
    categories: list = field(default_factory=list)     # Match these categories
    severities: list = field(default_factory=list)     # Match these severities
    job_codes: list = field(default_factory=list)      # Match these projects (empty = all)
    notify_roles: list = field(default_factory=list)   # Notify users with these roles
    notify_users: list = field(default_factory=list)   # Notify these specific users
    created_by: str = ""
    created_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "AlertRule":
        rule = cls()
        for k, v in d.items():
            if hasattr(rule, k):
                setattr(rule, k, v)
        return rule

    def matches(self, event: ActivityEvent) -> bool:
        """Check if this rule matches an event."""
        if not self.enabled:
            return False
        if self.event_types and event.event_type not in self.event_types:
            return False
        if self.categories and event.category not in self.categories:
            return False
        if self.severities and event.severity not in self.severities:
            return False
        if self.job_codes and event.job_code and event.job_code not in self.job_codes:
            return False
        return True


@dataclass
class Notification:
    """A notification generated by an alert rule for a specific user."""
    notification_id: str = ""
    event_id: str = ""              # Which event triggered this
    rule_id: str = ""               # Which rule matched
    username: str = ""              # Recipient
    title: str = ""
    description: str = ""
    severity: str = SEVERITY_INFO
    category: str = ""
    job_code: str = ""
    read: bool = False
    read_at: str = ""
    created_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Notification":
        n = cls()
        for k, v in d.items():
            if hasattr(n, k):
                setattr(n, k, v)
        return n


# ─────────────────────────────────────────────
# STORAGE
# ─────────────────────────────────────────────

def _activity_dir(base_dir: str) -> str:
    d = os.path.join(base_dir, "data", "activity")
    os.makedirs(d, exist_ok=True)
    return d


def _load_events_file(base_dir: str) -> list:
    path = os.path.join(_activity_dir(base_dir), "events.json")
    if not os.path.isfile(path):
        return []
    with open(path) as f:
        return json.load(f)


def _save_events_file(base_dir: str, events: list):
    path = os.path.join(_activity_dir(base_dir), "events.json")
    with open(path, "w") as f:
        json.dump(events, f, indent=2, default=str)


def _load_rules_file(base_dir: str) -> list:
    path = os.path.join(_activity_dir(base_dir), "alert_rules.json")
    if not os.path.isfile(path):
        return []
    with open(path) as f:
        return json.load(f)


def _save_rules_file(base_dir: str, rules: list):
    path = os.path.join(_activity_dir(base_dir), "alert_rules.json")
    with open(path, "w") as f:
        json.dump(rules, f, indent=2, default=str)


def _load_notifications_file(base_dir: str) -> list:
    path = os.path.join(_activity_dir(base_dir), "notifications.json")
    if not os.path.isfile(path):
        return []
    with open(path) as f:
        return json.load(f)


def _save_notifications_file(base_dir: str, notifications: list):
    path = os.path.join(_activity_dir(base_dir), "notifications.json")
    with open(path, "w") as f:
        json.dump(notifications, f, indent=2, default=str)


# ─────────────────────────────────────────────
# EVENT LOGGING
# ─────────────────────────────────────────────

def log_event(base_dir: str, event_type: str, category: str,
              actor: str, title: str,
              description: str = "", job_code: str = "",
              entity_type: str = "", entity_id: str = "",
              severity: str = "", metadata: dict = None,
              ip_address: str = "") -> ActivityEvent:
    """
    Log an activity event. This is the primary entry point for the audit trail.
    Auto-determines severity from event type if not specified.
    After logging, evaluates alert rules and generates notifications.
    """
    now = datetime.datetime.now()

    if not severity:
        severity = EVENT_DEFAULT_SEVERITY.get(event_type, SEVERITY_INFO)

    event = ActivityEvent(
        event_id=f"EVT-{now.strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(3).upper()}",
        event_type=event_type,
        category=category,
        severity=severity,
        timestamp=now.isoformat(),
        actor=actor,
        job_code=job_code,
        entity_type=entity_type,
        entity_id=entity_id,
        title=title,
        description=description,
        metadata=metadata or {},
        ip_address=ip_address,
    )

    # Append to events file
    events = _load_events_file(base_dir)
    events.append(event.to_dict())

    # Keep last 10,000 events (rolling log)
    if len(events) > 10000:
        events = events[-10000:]

    _save_events_file(base_dir, events)

    # Evaluate alert rules
    _evaluate_rules(base_dir, event)

    return event


def _evaluate_rules(base_dir: str, event: ActivityEvent):
    """Evaluate all alert rules against an event and generate notifications."""
    rules_data = _load_rules_file(base_dir)
    rules = [AlertRule.from_dict(r) for r in rules_data]
    notifications = _load_notifications_file(base_dir)
    now = datetime.datetime.now().isoformat()

    for rule in rules:
        if rule.matches(event):
            # Generate notifications for all target users
            target_users = set(rule.notify_users)
            # Note: role-based notification targets would need user lookup
            # For now, we use the explicit user list

            for username in target_users:
                notif = Notification(
                    notification_id=f"NOTIF-{secrets.token_hex(4).upper()}",
                    event_id=event.event_id,
                    rule_id=rule.rule_id,
                    username=username,
                    title=event.title,
                    description=event.description,
                    severity=event.severity,
                    category=event.category,
                    job_code=event.job_code,
                    created_at=now,
                )
                notifications.append(notif.to_dict())

    # Keep last 5,000 notifications
    if len(notifications) > 5000:
        notifications = notifications[-5000:]

    _save_notifications_file(base_dir, notifications)


# ─────────────────────────────────────────────
# EVENT QUERY
# ─────────────────────────────────────────────

def get_events(base_dir: str, category: str = "", event_type: str = "",
               severity: str = "", job_code: str = "", actor: str = "",
               since: str = "", limit: int = 100, offset: int = 0) -> dict:
    """Query activity events with filters. Returns newest first."""
    all_events = _load_events_file(base_dir)

    # Apply filters
    filtered = all_events
    if category:
        filtered = [e for e in filtered if e.get("category") == category]
    if event_type:
        filtered = [e for e in filtered if e.get("event_type") == event_type]
    if severity:
        filtered = [e for e in filtered if e.get("severity") == severity]
    if job_code:
        filtered = [e for e in filtered if e.get("job_code") == job_code]
    if actor:
        filtered = [e for e in filtered if e.get("actor") == actor]
    if since:
        filtered = [e for e in filtered if e.get("timestamp", "") >= since]

    # Sort newest first
    filtered.sort(key=lambda e: e.get("timestamp", ""), reverse=True)

    total = len(filtered)
    page = filtered[offset:offset + limit]

    return {
        "events": page,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


def get_activity_feed(base_dir: str, limit: int = 50, job_code: str = "") -> list:
    """Get recent activity for the feed view. Returns event dicts."""
    result = get_events(base_dir, job_code=job_code, limit=limit)
    return result["events"]


def get_event_stats(base_dir: str, days_back: int = 7) -> dict:
    """Get event statistics for the dashboard."""
    cutoff = (datetime.date.today() - datetime.timedelta(days=days_back)).isoformat()
    all_events = _load_events_file(base_dir)

    recent = [e for e in all_events if e.get("timestamp", "")[:10] >= cutoff]

    by_category = defaultdict(int)
    by_severity = defaultdict(int)
    by_type = defaultdict(int)
    by_day = defaultdict(int)
    by_actor = defaultdict(int)

    for e in recent:
        by_category[e.get("category", "unknown")] += 1
        by_severity[e.get("severity", "info")] += 1
        by_type[e.get("event_type", "unknown")] += 1
        day = e.get("timestamp", "")[:10]
        if day:
            by_day[day] += 1
        actor = e.get("actor", "")
        if actor:
            by_actor[actor] += 1

    return {
        "total_events": len(recent),
        "total_all_time": len(all_events),
        "by_category": dict(by_category),
        "by_severity": dict(by_severity),
        "by_type": dict(by_type),
        "by_day": dict(by_day),
        "by_actor": dict(by_actor),
        "period_days": days_back,
    }


# ─────────────────────────────────────────────
# ALERT RULE MANAGEMENT
# ─────────────────────────────────────────────

def create_alert_rule(base_dir: str, name: str, created_by: str,
                      event_types: list = None, categories: list = None,
                      severities: list = None, job_codes: list = None,
                      notify_roles: list = None, notify_users: list = None) -> AlertRule:
    """Create a new alert rule."""
    now = datetime.datetime.now()
    rule = AlertRule(
        rule_id=f"RULE-{now.strftime('%Y%m%d')}-{secrets.token_hex(3).upper()}",
        name=name,
        enabled=True,
        event_types=event_types or [],
        categories=categories or [],
        severities=severities or [],
        job_codes=job_codes or [],
        notify_roles=notify_roles or [],
        notify_users=notify_users or [],
        created_by=created_by,
        created_at=now.isoformat(),
    )

    rules = _load_rules_file(base_dir)
    rules.append(rule.to_dict())
    _save_rules_file(base_dir, rules)

    return rule


def update_alert_rule(base_dir: str, rule_id: str, **kwargs) -> dict:
    """Update an existing alert rule."""
    rules = _load_rules_file(base_dir)
    for i, r in enumerate(rules):
        if r.get("rule_id") == rule_id:
            for k, v in kwargs.items():
                if k in r:
                    rules[i][k] = v
            _save_rules_file(base_dir, rules)
            return {"ok": True, "rule": rules[i]}
    return {"ok": False, "error": "Rule not found"}


def delete_alert_rule(base_dir: str, rule_id: str) -> dict:
    """Delete an alert rule."""
    rules = _load_rules_file(base_dir)
    original_len = len(rules)
    rules = [r for r in rules if r.get("rule_id") != rule_id]
    if len(rules) == original_len:
        return {"ok": False, "error": "Rule not found"}
    _save_rules_file(base_dir, rules)
    return {"ok": True}


def list_alert_rules(base_dir: str) -> List[dict]:
    """List all alert rules."""
    return _load_rules_file(base_dir)


# ─────────────────────────────────────────────
# NOTIFICATION MANAGEMENT
# ─────────────────────────────────────────────

def get_notifications(base_dir: str, username: str,
                      unread_only: bool = False,
                      limit: int = 50) -> List[dict]:
    """Get notifications for a specific user."""
    all_notifs = _load_notifications_file(base_dir)
    user_notifs = [n for n in all_notifs if n.get("username") == username]

    if unread_only:
        user_notifs = [n for n in user_notifs if not n.get("read")]

    # Sort newest first
    user_notifs.sort(key=lambda n: n.get("created_at", ""), reverse=True)
    return user_notifs[:limit]


def get_unread_count(base_dir: str, username: str) -> int:
    """Get count of unread notifications for a user."""
    all_notifs = _load_notifications_file(base_dir)
    return len([n for n in all_notifs
                if n.get("username") == username and not n.get("read")])


def mark_notification_read(base_dir: str, notification_id: str,
                           username: str) -> dict:
    """Mark a notification as read."""
    all_notifs = _load_notifications_file(base_dir)
    for i, n in enumerate(all_notifs):
        if n.get("notification_id") == notification_id and n.get("username") == username:
            all_notifs[i]["read"] = True
            all_notifs[i]["read_at"] = datetime.datetime.now().isoformat()
            _save_notifications_file(base_dir, all_notifs)
            return {"ok": True}
    return {"ok": False, "error": "Notification not found"}


def mark_all_read(base_dir: str, username: str) -> dict:
    """Mark all notifications as read for a user."""
    all_notifs = _load_notifications_file(base_dir)
    now = datetime.datetime.now().isoformat()
    count = 0
    for i, n in enumerate(all_notifs):
        if n.get("username") == username and not n.get("read"):
            all_notifs[i]["read"] = True
            all_notifs[i]["read_at"] = now
            count += 1
    _save_notifications_file(base_dir, all_notifs)
    return {"ok": True, "marked_read": count}


def clear_notifications(base_dir: str, username: str) -> dict:
    """Remove all notifications for a user."""
    all_notifs = _load_notifications_file(base_dir)
    original = len(all_notifs)
    all_notifs = [n for n in all_notifs if n.get("username") != username]
    _save_notifications_file(base_dir, all_notifs)
    return {"ok": True, "removed": original - len(all_notifs)}


# ─────────────────────────────────────────────
# CONVENIENCE LOGGING FUNCTIONS
# ─────────────────────────────────────────────

def log_wo_event(base_dir: str, event_type: str, actor: str,
                 job_code: str, wo_id: str, title: str,
                 description: str = "", metadata: dict = None) -> ActivityEvent:
    """Log a work-order-related event."""
    return log_event(
        base_dir, event_type, CAT_WORK_ORDER, actor, title,
        description=description, job_code=job_code,
        entity_type="work_order", entity_id=wo_id,
        metadata=metadata,
    )


def log_item_event(base_dir: str, event_type: str, actor: str,
                   job_code: str, item_id: str, title: str,
                   description: str = "", metadata: dict = None) -> ActivityEvent:
    """Log a work-order-item-related event."""
    return log_event(
        base_dir, event_type, CAT_WORK_ORDER, actor, title,
        description=description, job_code=job_code,
        entity_type="item", entity_id=item_id,
        metadata=metadata,
    )


def log_qc_event(base_dir: str, event_type: str, actor: str,
                 job_code: str, item_id: str, title: str,
                 description: str = "", metadata: dict = None) -> ActivityEvent:
    """Log a QC-related event."""
    return log_event(
        base_dir, event_type, CAT_QC, actor, title,
        description=description, job_code=job_code,
        entity_type="item", entity_id=item_id,
        metadata=metadata,
    )


def log_shipping_event(base_dir: str, event_type: str, actor: str,
                       load_id: str, title: str,
                       job_code: str = "", description: str = "",
                       metadata: dict = None) -> ActivityEvent:
    """Log a shipping-related event."""
    return log_event(
        base_dir, event_type, CAT_SHIPPING, actor, title,
        description=description, job_code=job_code,
        entity_type="load", entity_id=load_id,
        metadata=metadata,
    )


def log_field_event(base_dir: str, event_type: str, actor: str,
                    job_code: str, entity_id: str, title: str,
                    description: str = "", metadata: dict = None) -> ActivityEvent:
    """Log a field-ops-related event."""
    return log_event(
        base_dir, event_type, CAT_FIELD, actor, title,
        description=description, job_code=job_code,
        entity_type="field", entity_id=entity_id,
        metadata=metadata,
    )


def log_punch_event(base_dir: str, event_type: str, actor: str,
                    job_code: str, punch_id: str, title: str,
                    description: str = "", severity: str = "",
                    metadata: dict = None) -> ActivityEvent:
    """Log a punch-list-related event."""
    return log_event(
        base_dir, event_type, CAT_PUNCH, actor, title,
        description=description, job_code=job_code, severity=severity,
        entity_type="punch", entity_id=punch_id,
        metadata=metadata,
    )
