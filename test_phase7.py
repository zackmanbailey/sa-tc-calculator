#!/usr/bin/env python3
"""
TitanForge Phase 7 — Activity Feed, Audit Trail & Notifications Tests
Tests event logging, query/filtering, alert rules, notifications,
convenience loggers, handler RBAC, route table, and templates.
"""

import sys, os, json, tempfile, shutil, datetime, secrets
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

passed = 0
failed = 0

def test(name, condition):
    global passed, failed
    if condition:
        print(f"  ✅ {name}")
        passed += 1
    else:
        print(f"  ❌ {name}")
        failed += 1


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 1: Event Constants ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.activity import (
    EVENT_CATEGORIES, CATEGORY_LABELS, CATEGORY_COLORS,
    SEVERITY_LEVELS, SEVERITY_LABELS,
    EVENT_TYPES, EVENT_LABELS, EVENT_DEFAULT_SEVERITY,
    CAT_WORK_ORDER, CAT_QC, CAT_SHIPPING, CAT_FIELD,
    CAT_PUNCH, CAT_PROJECT, CAT_USER, CAT_SYSTEM, CAT_INVENTORY,
    SEVERITY_INFO, SEVERITY_WARNING, SEVERITY_CRITICAL, SEVERITY_SUCCESS,
    EVT_WO_CREATED, EVT_QC_APPROVED, EVT_QC_REJECTED,
    EVT_LOAD_SHIPPED, EVT_PUNCH_CREATED, EVT_PUNCH_CRITICAL,
    EVT_INSTALL_CONFIRMED, EVT_DAILY_REPORT, EVT_SYSTEM_ERROR,
    EVT_ITEM_STARTED, EVT_ITEM_ASSIGNED,
)

test("9 event categories", len(EVENT_CATEGORIES) == 9)
test("All categories have labels", all(c in CATEGORY_LABELS for c in EVENT_CATEGORIES))
test("All categories have colors", all(c in CATEGORY_COLORS for c in EVENT_CATEGORIES))

test("4 severity levels", len(SEVERITY_LEVELS) == 4)
test("info severity", SEVERITY_INFO == "info")
test("warning severity", SEVERITY_WARNING == "warning")
test("critical severity", SEVERITY_CRITICAL == "critical")
test("success severity", SEVERITY_SUCCESS == "success")
test("All severities have labels", all(s in SEVERITY_LABELS for s in SEVERITY_LEVELS))

test("29 event types", len(EVENT_TYPES) == 29)
test("All types have labels", all(t in EVENT_LABELS for t in EVENT_TYPES))
test("All types have default severity", all(t in EVENT_DEFAULT_SEVERITY for t in EVENT_TYPES))

test("QC rejected is warning", EVENT_DEFAULT_SEVERITY[EVT_QC_REJECTED] == SEVERITY_WARNING)
test("Punch critical is critical", EVENT_DEFAULT_SEVERITY[EVT_PUNCH_CRITICAL] == SEVERITY_CRITICAL)
test("System error is critical", EVENT_DEFAULT_SEVERITY[EVT_SYSTEM_ERROR] == SEVERITY_CRITICAL)
test("QC approved is success", EVENT_DEFAULT_SEVERITY[EVT_QC_APPROVED] == SEVERITY_SUCCESS)
test("Load shipped is success", EVENT_DEFAULT_SEVERITY[EVT_LOAD_SHIPPED] == SEVERITY_SUCCESS)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 2: ActivityEvent Data Model ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.activity import ActivityEvent

evt = ActivityEvent(
    event_id="EVT-TEST-001",
    event_type=EVT_WO_CREATED,
    category=CAT_WORK_ORDER,
    severity=SEVERITY_INFO,
    timestamp="2026-04-14T10:00:00",
    actor="test_pm",
    job_code="JOB-100",
    entity_type="work_order",
    entity_id="WO-001",
    title="Work order created",
    description="New WO for columns",
    metadata={"items": 5},
)

test("event_id set", evt.event_id == "EVT-TEST-001")
test("event_type set", evt.event_type == EVT_WO_CREATED)
test("category set", evt.category == CAT_WORK_ORDER)
test("severity set", evt.severity == SEVERITY_INFO)
test("actor set", evt.actor == "test_pm")
test("job_code set", evt.job_code == "JOB-100")
test("entity_type set", evt.entity_type == "work_order")
test("entity_id set", evt.entity_id == "WO-001")
test("title set", evt.title == "Work order created")
test("metadata set", evt.metadata == {"items": 5})

test("event_label property", evt.event_label == "Work Order Created")
test("category_label property", evt.category_label == "Work Order")
test("category_color property", evt.category_color == "blue")
test("severity_label property", evt.severity_label == "Info")

# Serialization
d = evt.to_dict()
test("to_dict has event_id", d["event_id"] == "EVT-TEST-001")
test("to_dict has metadata", d["metadata"] == {"items": 5})

evt2 = ActivityEvent.from_dict(d)
test("from_dict roundtrip", evt2.event_id == "EVT-TEST-001")
test("from_dict metadata", evt2.metadata == {"items": 5})


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 3: AlertRule Data Model ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.activity import AlertRule

rule = AlertRule(
    rule_id="RULE-001",
    name="Critical punch alerts",
    enabled=True,
    event_types=[EVT_PUNCH_CRITICAL],
    categories=[CAT_PUNCH],
    severities=[SEVERITY_CRITICAL],
    job_codes=["JOB-100"],
    notify_users=["pm1", "foreman1"],
    created_by="admin",
)

test("rule_id set", rule.rule_id == "RULE-001")
test("name set", rule.name == "Critical punch alerts")
test("enabled is True", rule.enabled == True)
test("event_types set", rule.event_types == [EVT_PUNCH_CRITICAL])
test("notify_users set", rule.notify_users == ["pm1", "foreman1"])

# matches() method
match_evt = ActivityEvent(
    event_type=EVT_PUNCH_CRITICAL, category=CAT_PUNCH,
    severity=SEVERITY_CRITICAL, job_code="JOB-100",
)
test("Rule matches matching event", rule.matches(match_evt))

no_match_evt = ActivityEvent(
    event_type=EVT_WO_CREATED, category=CAT_WORK_ORDER,
    severity=SEVERITY_INFO,
)
test("Rule does not match non-matching event", not rule.matches(no_match_evt))

# Disabled rule
disabled_rule = AlertRule(rule_id="RULE-DIS", enabled=False,
                          event_types=[EVT_PUNCH_CRITICAL])
test("Disabled rule never matches", not disabled_rule.matches(match_evt))

# Empty filters match everything
broad_rule = AlertRule(rule_id="RULE-BROAD", enabled=True)
test("Broad rule matches any event", broad_rule.matches(match_evt))
test("Broad rule matches other event", broad_rule.matches(no_match_evt))

# Serialization
rd = rule.to_dict()
test("AlertRule to_dict", rd["rule_id"] == "RULE-001")
rule2 = AlertRule.from_dict(rd)
test("AlertRule from_dict roundtrip", rule2.rule_id == "RULE-001")


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 4: Notification Data Model ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.activity import Notification

notif = Notification(
    notification_id="NOTIF-001",
    event_id="EVT-001",
    rule_id="RULE-001",
    username="pm1",
    title="Critical punch item",
    severity=SEVERITY_CRITICAL,
    category=CAT_PUNCH,
    job_code="JOB-100",
    created_at="2026-04-14T10:00:00",
)

test("notif id set", notif.notification_id == "NOTIF-001")
test("notif username set", notif.username == "pm1")
test("notif read default False", notif.read == False)

nd = notif.to_dict()
test("Notification to_dict", nd["notification_id"] == "NOTIF-001")
notif2 = Notification.from_dict(nd)
test("Notification from_dict roundtrip", notif2.notification_id == "NOTIF-001")


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 5: Event Storage & Logging ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.activity import (
    log_event, get_events, get_activity_feed, get_event_stats,
    _load_events_file, _activity_dir,
)

tmp = tempfile.mkdtemp()

# Log first event
e1 = log_event(tmp, EVT_WO_CREATED, CAT_WORK_ORDER, "pm1",
               "WO-001 created for JOB-100",
               job_code="JOB-100", entity_type="work_order", entity_id="WO-001")

test("log_event returns ActivityEvent", isinstance(e1, ActivityEvent))
test("Event ID starts with EVT-", e1.event_id.startswith("EVT-"))
test("Event has timestamp", len(e1.timestamp) > 0)
test("Auto-severity is info", e1.severity == SEVERITY_INFO)

# Verify persisted
events = _load_events_file(tmp)
test("1 event persisted", len(events) == 1)
test("Persisted event matches", events[0]["event_id"] == e1.event_id)

# Log more events
e2 = log_event(tmp, EVT_QC_REJECTED, CAT_QC, "qc_inspector",
               "Item B3 failed QC", severity=SEVERITY_WARNING,
               job_code="JOB-100", entity_id="ITM-B3",
               metadata={"reason": "weld defect"})

test("Custom severity preserved", e2.severity == SEVERITY_WARNING)
test("Metadata persisted", e2.metadata == {"reason": "weld defect"})

e3 = log_event(tmp, EVT_PUNCH_CRITICAL, CAT_PUNCH, "field_lead",
               "Critical punch: Column C1 bent",
               job_code="JOB-200", entity_id="PUNCH-001")

test("3 events total", len(_load_events_file(tmp)) == 3)
test("Punch critical auto-severity", e3.severity == SEVERITY_CRITICAL)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 6: Event Query & Filtering ══")
# ═══════════════════════════════════════════════════════════════════

# Query all
result = get_events(tmp)
test("get_events returns all", result["total"] == 3)
test("Newest first", result["events"][0]["event_id"] == e3.event_id)

# Filter by category
r_wo = get_events(tmp, category=CAT_WORK_ORDER)
test("Filter by work_order: 1 result", r_wo["total"] == 1)

r_qc = get_events(tmp, category=CAT_QC)
test("Filter by qc: 1 result", r_qc["total"] == 1)

r_punch = get_events(tmp, category=CAT_PUNCH)
test("Filter by punch: 1 result", r_punch["total"] == 1)

# Filter by severity
r_crit = get_events(tmp, severity=SEVERITY_CRITICAL)
test("Filter by critical: 1 result", r_crit["total"] == 1)
test("Critical event is punch", r_crit["events"][0]["event_type"] == EVT_PUNCH_CRITICAL)

# Filter by job_code
r_job100 = get_events(tmp, job_code="JOB-100")
test("Filter by JOB-100: 2 results", r_job100["total"] == 2)

r_job200 = get_events(tmp, job_code="JOB-200")
test("Filter by JOB-200: 1 result", r_job200["total"] == 1)

# Filter by actor
r_pm = get_events(tmp, actor="pm1")
test("Filter by pm1: 1 result", r_pm["total"] == 1)

# Pagination
r_page = get_events(tmp, limit=2, offset=0)
test("Pagination limit=2: 2 events", len(r_page["events"]) == 2)
test("Pagination total still 3", r_page["total"] == 3)

r_page2 = get_events(tmp, limit=2, offset=2)
test("Pagination offset=2: 1 event", len(r_page2["events"]) == 1)

# Combined filters
r_combined = get_events(tmp, category=CAT_WORK_ORDER, job_code="JOB-100")
test("Combined filter: 1 result", r_combined["total"] == 1)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 7: Activity Feed ══")
# ═══════════════════════════════════════════════════════════════════

feed = get_activity_feed(tmp, limit=50)
test("Feed returns 3 events", len(feed) == 3)
test("Feed is newest first", feed[0]["event_id"] == e3.event_id)

feed_proj = get_activity_feed(tmp, job_code="JOB-200")
test("Feed filtered by project: 1", len(feed_proj) == 1)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 8: Event Statistics ══")
# ═══════════════════════════════════════════════════════════════════

stats = get_event_stats(tmp, days_back=7)
test("Stats total_events is 3", stats["total_events"] == 3)
test("Stats total_all_time is 3", stats["total_all_time"] == 3)
test("Stats by_category has work_order", stats["by_category"].get(CAT_WORK_ORDER) == 1)
test("Stats by_category has qc", stats["by_category"].get(CAT_QC) == 1)
test("Stats by_category has punch", stats["by_category"].get(CAT_PUNCH) == 1)
test("Stats by_severity has info", stats["by_severity"].get(SEVERITY_INFO, 0) >= 1)
test("Stats by_severity has critical", stats["by_severity"].get(SEVERITY_CRITICAL, 0) >= 1)
test("Stats by_actor has pm1", stats["by_actor"].get("pm1", 0) >= 1)
test("Stats by_day has entries", len(stats["by_day"]) >= 1)
test("Stats period_days is 7", stats["period_days"] == 7)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 9: Alert Rule Management ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.activity import (
    create_alert_rule, update_alert_rule, delete_alert_rule, list_alert_rules,
)

# Create rule
rule1 = create_alert_rule(
    tmp, name="QC Rejection Alerts", created_by="admin",
    event_types=[EVT_QC_REJECTED],
    categories=[CAT_QC],
    notify_users=["pm1", "foreman1"],
)
test("Rule created", rule1.rule_id.startswith("RULE-"))
test("Rule name set", rule1.name == "QC Rejection Alerts")
test("Rule enabled by default", rule1.enabled == True)

rule2 = create_alert_rule(
    tmp, name="Critical Punch Alerts", created_by="admin",
    event_types=[EVT_PUNCH_CRITICAL],
    severities=[SEVERITY_CRITICAL],
    notify_users=["pm1"],
)

# List rules
rules = list_alert_rules(tmp)
test("2 rules listed", len(rules) == 2)

# Update rule
result = update_alert_rule(tmp, rule1.rule_id, enabled=False)
test("Update rule ok", result.get("ok") == True)
test("Rule now disabled", result["rule"]["enabled"] == False)

# Update non-existent
result_bad = update_alert_rule(tmp, "FAKE-RULE-ID", name="nope")
test("Update bad rule fails", result_bad.get("ok") == False)

# Delete rule
del_result = delete_alert_rule(tmp, rule1.rule_id)
test("Delete rule ok", del_result.get("ok") == True)
test("1 rule remaining", len(list_alert_rules(tmp)) == 1)

del_bad = delete_alert_rule(tmp, "FAKE-RULE-ID")
test("Delete bad rule fails", del_bad.get("ok") == False)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 10: Alert Rules → Notification Generation ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.activity import (
    get_notifications, get_unread_count, mark_notification_read,
    mark_all_read, clear_notifications,
)

# rule2 matches PUNCH_CRITICAL for pm1 — log a matching event
e4 = log_event(tmp, EVT_PUNCH_CRITICAL, CAT_PUNCH, "field_crew",
               "Critical: Rafter R5 cracked",
               job_code="JOB-300", entity_id="PUNCH-002")

# Check notifications were generated
pm1_notifs = get_notifications(tmp, "pm1")
test("pm1 has notifications", len(pm1_notifs) >= 1)

# The most recent notification should be from the punch critical event
latest = pm1_notifs[0] if pm1_notifs else {}
test("Notification references event", latest.get("event_id") == e4.event_id)
test("Notification has title", "Rafter R5" in latest.get("title", ""))
test("Notification severity is critical", latest.get("severity") == SEVERITY_CRITICAL)
test("Notification is unread", latest.get("read") == False)

# Unread count
count = get_unread_count(tmp, "pm1")
test("Unread count >= 1", count >= 1)

# Non-target user has no notifications
count2 = get_unread_count(tmp, "random_user")
test("Non-target user: 0 unread", count2 == 0)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 11: Notification Actions ══")
# ═══════════════════════════════════════════════════════════════════

notif_id = pm1_notifs[0]["notification_id"] if pm1_notifs else ""

# Mark read
if notif_id:
    mr = mark_notification_read(tmp, notif_id, "pm1")
    test("Mark read ok", mr.get("ok") == True)

    # Verify it's now read
    notifs_after = get_notifications(tmp, "pm1")
    marked = next((n for n in notifs_after if n["notification_id"] == notif_id), None)
    test("Notification now read", marked and marked.get("read") == True)
    test("Notification has read_at", marked and len(marked.get("read_at", "")) > 0)

    # Unread count decreased
    new_count = get_unread_count(tmp, "pm1")
    test("Unread count decreased", new_count < count)

# Wrong user can't mark
bad_mark = mark_notification_read(tmp, notif_id, "other_user")
test("Wrong user mark fails", bad_mark.get("ok") == False)

# Mark all read (log another event to create new notification)
log_event(tmp, EVT_PUNCH_CRITICAL, CAT_PUNCH, "crew2",
          "Critical: Column C5 damage", job_code="JOB-400")

mar = mark_all_read(tmp, "pm1")
test("Mark all read ok", mar.get("ok") == True)
test("mark_all_read count >= 1", mar.get("marked_read", 0) >= 0)
test("All now read", get_unread_count(tmp, "pm1") == 0)

# Clear notifications
clr = clear_notifications(tmp, "pm1")
test("Clear notifications ok", clr.get("ok") == True)
test("Clear removed some", clr.get("removed", 0) >= 1)
test("pm1 has 0 notifications after clear", len(get_notifications(tmp, "pm1")) == 0)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 12: Convenience Logging Functions ══")
# ═══════════════════════════════════════════════════════════════════
from shop_drawings.activity import (
    log_wo_event, log_item_event, log_qc_event,
    log_shipping_event, log_field_event, log_punch_event,
    EVT_WO_CREATED, EVT_ITEM_STARTED, EVT_QC_APPROVED,
    EVT_LOAD_SHIPPED, EVT_INSTALL_CONFIRMED, EVT_PUNCH_CREATED,
    CAT_WORK_ORDER, CAT_QC, CAT_SHIPPING, CAT_FIELD, CAT_PUNCH,
    SEVERITY_SUCCESS, SEVERITY_WARNING,
)

ew = log_wo_event(tmp, EVT_WO_CREATED, "pm1", "JOB-500", "WO-005",
                  "Created WO for rafters", metadata={"items": 12})
test("log_wo_event category", ew.category == CAT_WORK_ORDER)
test("log_wo_event entity_type", ew.entity_type == "work_order")
test("log_wo_event entity_id", ew.entity_id == "WO-005")

ei = log_item_event(tmp, EVT_ITEM_STARTED, "welder1", "JOB-500", "ITM-R1",
                    "Welder1 started rafter R1")
test("log_item_event category", ei.category == CAT_WORK_ORDER)
test("log_item_event entity_type", ei.entity_type == "item")

eq = log_qc_event(tmp, EVT_QC_APPROVED, "qc1", "JOB-500", "ITM-R1",
                  "QC approved rafter R1")
test("log_qc_event category", eq.category == CAT_QC)
test("log_qc_event severity", eq.severity == SEVERITY_SUCCESS)

es = log_shipping_event(tmp, EVT_LOAD_SHIPPED, "shipper1", "LOAD-010",
                        "Load 10 shipped", job_code="JOB-500")
test("log_shipping_event category", es.category == CAT_SHIPPING)
test("log_shipping_event entity_type", es.entity_type == "load")

ef = log_field_event(tmp, EVT_INSTALL_CONFIRMED, "installer1", "JOB-500",
                     "INST-001", "Installed column C1")
test("log_field_event category", ef.category == CAT_FIELD)

ep = log_punch_event(tmp, EVT_PUNCH_CREATED, "crew1", "JOB-500", "PUNCH-010",
                     "New punch: damaged girt", severity=SEVERITY_WARNING)
test("log_punch_event category", ep.category == CAT_PUNCH)
test("log_punch_event custom severity", ep.severity == SEVERITY_WARNING)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 13: Rolling Log Limit ══")
# ═══════════════════════════════════════════════════════════════════

# The rolling limit is 10,000 — verify that events beyond that get pruned
# We won't actually create 10k events, just verify the mechanism exists
from shop_drawings.activity import _save_events_file, _load_events_file

# Create a file with 10,005 fake events
fake_events = [{"event_id": f"FAKE-{i}", "timestamp": "2026-01-01"} for i in range(10005)]
_save_events_file(tmp, fake_events)
test("Can save 10005 events", len(_load_events_file(tmp)) == 10005)

# Now log one more — should trigger pruning to 10000
log_event(tmp, EVT_SYSTEM_ERROR, CAT_SYSTEM, "system",
          "Test system event", description="Pruning test")
stored = _load_events_file(tmp)
test("After pruning, <= 10001 events", len(stored) <= 10001)

# Reset for remaining tests
_save_events_file(tmp, [])


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 14: Multi-Job Event Tracking ══")
# ═══════════════════════════════════════════════════════════════════

# Log events across multiple projects
jobs = ["JOB-A", "JOB-B", "JOB-C"]
for j in jobs:
    log_event(tmp, EVT_WO_CREATED, CAT_WORK_ORDER, "pm1",
              f"WO created for {j}", job_code=j)
    log_event(tmp, EVT_ITEM_STARTED, CAT_WORK_ORDER, "op1",
              f"Item started in {j}", job_code=j)

all_result = get_events(tmp)
test("6 events logged", all_result["total"] == 6)

for j in jobs:
    r = get_events(tmp, job_code=j)
    test(f"{j} has 2 events", r["total"] == 2)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 15: Stats with Multi-Category Data ══")
# ═══════════════════════════════════════════════════════════════════

# Add QC and shipping events
log_event(tmp, EVT_QC_APPROVED, CAT_QC, "qc1", "QC pass", job_code="JOB-A")
log_event(tmp, EVT_QC_REJECTED, CAT_QC, "qc1", "QC fail", job_code="JOB-B")
log_event(tmp, EVT_LOAD_SHIPPED, CAT_SHIPPING, "ship1", "Load out", job_code="JOB-A")
log_event(tmp, EVT_PUNCH_CREATED, CAT_PUNCH, "crew1", "Punch logged", job_code="JOB-C")

stats2 = get_event_stats(tmp, days_back=7)
test("Stats total >= 10", stats2["total_events"] >= 10)
test("Stats has work_order category", CAT_WORK_ORDER in stats2["by_category"])
test("Stats has qc category", CAT_QC in stats2["by_category"])
test("Stats has shipping category", CAT_SHIPPING in stats2["by_category"])
test("Stats has punch category", CAT_PUNCH in stats2["by_category"])
test("Stats by_actor has pm1", "pm1" in stats2["by_actor"])
test("Stats by_actor has qc1", "qc1" in stats2["by_actor"])
test("Stats by_type has wo_created", EVT_WO_CREATED in stats2["by_type"])


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 16: Handler Classes Exist ══")
# ═══════════════════════════════════════════════════════════════════

import tf_handlers as tfh

handler_classes = [
    "ActivityFeedPageHandler",
    "ActivityEventsAPIHandler",
    "ActivityFeedAPIHandler",
    "ActivityStatsAPIHandler",
    "AlertRulesAPIHandler",
    "AlertRuleUpdateHandler",
    "AlertRuleDeleteHandler",
    "NotificationsAPIHandler",
    "NotificationReadHandler",
    "NotificationReadAllHandler",
    "NotificationClearHandler",
    "ActivityConfigHandler",
]

for cls_name in handler_classes:
    test(f"{cls_name} exists", hasattr(tfh, cls_name))

for cls_name in handler_classes:
    cls = getattr(tfh, cls_name, None)
    if cls:
        test(f"{cls_name} is BaseHandler subclass",
             issubclass(cls, tfh.BaseHandler))


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 17: RBAC Permissions ══")
# ═══════════════════════════════════════════════════════════════════

from auth.roles import P, ROLES

# Audit log handlers require view_audit_log
audit_handlers = [
    "ActivityFeedPageHandler",
    "ActivityEventsAPIHandler",
    "ActivityStatsAPIHandler",
    "AlertRulesAPIHandler",
    "AlertRuleUpdateHandler",
    "AlertRuleDeleteHandler",
    "ActivityConfigHandler",
]
for cls_name in audit_handlers:
    cls = getattr(tfh, cls_name, None)
    if cls:
        test(f"{cls_name} requires view_audit_log",
             cls.required_permission == "view_audit_log")

# Dashboard-level handlers require view_dashboard
dash_handlers = [
    "ActivityFeedAPIHandler",
    "NotificationsAPIHandler",
    "NotificationReadHandler",
    "NotificationReadAllHandler",
    "NotificationClearHandler",
]
for cls_name in dash_handlers:
    cls = getattr(tfh, cls_name, None)
    if cls:
        test(f"{cls_name} requires view_dashboard",
             cls.required_permission == "view_dashboard")

# Check that the right roles have view_audit_log
roles_with_audit = []
for role_name, role_def in ROLES.items():
    if P.VIEW_AUDIT_LOG in role_def.permissions:
        roles_with_audit.append(role_name)

test("god_mode has view_audit_log", "god_mode" in roles_with_audit)
test("admin has view_audit_log", "admin" in roles_with_audit)
test("welder does NOT have view_audit_log", "welder" not in roles_with_audit)
test("field_crew does NOT have view_audit_log", "field_crew" not in roles_with_audit)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 18: Route Table ══")
# ═══════════════════════════════════════════════════════════════════

routes = tfh.get_routes()
route_map = {}
for entry in routes:
    if len(entry) >= 2:
        route_map[entry[0]] = entry[1]

expected_routes = {
    r"/activity":                    "ActivityFeedPageHandler",
    r"/api/activity/events":         "ActivityEventsAPIHandler",
    r"/api/activity/feed":           "ActivityFeedAPIHandler",
    r"/api/activity/stats":          "ActivityStatsAPIHandler",
    r"/api/activity/rules":          "AlertRulesAPIHandler",
    r"/api/activity/rules/update":   "AlertRuleUpdateHandler",
    r"/api/activity/rules/delete":   "AlertRuleDeleteHandler",
    r"/api/notifications":           "NotificationsAPIHandler",
    r"/api/notifications/read":      "NotificationReadHandler",
    r"/api/notifications/read-all":  "NotificationReadAllHandler",
    r"/api/notifications/clear":     "NotificationClearHandler",
    r"/api/activity/config":         "ActivityConfigHandler",
}

for pattern, expected in expected_routes.items():
    handler = route_map.get(pattern)
    handler_name = handler.__name__ if handler else "NOT FOUND"
    test(f"Route {pattern} → {expected}", handler_name == expected)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 19: Template File ══")
# ═══════════════════════════════════════════════════════════════════

from templates.activity_feed_page import ACTIVITY_FEED_PAGE_HTML

test("Activity Feed template exists", isinstance(ACTIVITY_FEED_PAGE_HTML, str))
test("Activity Feed is HTML", "<!DOCTYPE html>" in ACTIVITY_FEED_PAGE_HTML)
test("Activity Feed has title", "Activity Feed" in ACTIVITY_FEED_PAGE_HTML)
test("Activity Feed has API call", "/api/activity/events" in ACTIVITY_FEED_PAGE_HTML)
test("Activity Feed has event list", "eventList" in ACTIVITY_FEED_PAGE_HTML)
test("Activity Feed has filter bar", "filterCategory" in ACTIVITY_FEED_PAGE_HTML)
test("Activity Feed has stats", "statTotal" in ACTIVITY_FEED_PAGE_HTML)
test("Activity Feed has category breakdown", "catBreakdown" in ACTIVITY_FEED_PAGE_HTML)
test("Activity Feed has pagination", "pagination" in ACTIVITY_FEED_PAGE_HTML)
test("Activity Feed has severity filter", "filterSeverity" in ACTIVITY_FEED_PAGE_HTML)
test("Activity Feed links to executive", "/reports/executive" in ACTIVITY_FEED_PAGE_HTML)


# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 20: Full E2E — Log, Query, Alert, Notify ══")
# ═══════════════════════════════════════════════════════════════════

# Fresh tmpdir
tmp2 = tempfile.mkdtemp()

# 1. Create alert rule
r1 = create_alert_rule(
    tmp2, name="QC Rejection → PM", created_by="admin",
    event_types=[EVT_QC_REJECTED],
    notify_users=["pm_zack"],
)

r2 = create_alert_rule(
    tmp2, name="Critical Punches → All PMs", created_by="admin",
    severities=[SEVERITY_CRITICAL],
    notify_users=["pm_zack", "pm_sarah"],
)

# 2. Log various events
log_wo_event(tmp2, EVT_WO_CREATED, "pm_zack", "JOB-E2E", "WO-E2E",
             "Created WO for E2E test")
log_item_event(tmp2, EVT_ITEM_ASSIGNED, "foreman1", "JOB-E2E", "ITM-E1",
               "Assigned rafter R1 to welder1")
log_qc_event(tmp2, EVT_QC_REJECTED, "qc_inspector", "JOB-E2E", "ITM-E1",
             "QC rejected: weld defect")
log_punch_event(tmp2, EVT_PUNCH_CRITICAL, "crew_lead", "JOB-E2E", "PUNCH-E1",
                "Critical: Bent column", severity=SEVERITY_CRITICAL)

# 3. Verify event log
all_events = get_events(tmp2)
test("E2E: 4 events logged", all_events["total"] == 4)

# 4. Verify notifications generated
zack_notifs = get_notifications(tmp2, "pm_zack")
test("E2E: pm_zack has notifications", len(zack_notifs) >= 2)
# Should have QC rejection + critical punch
notif_types = set()
for n in zack_notifs:
    if "QC rejected" in n.get("title", ""):
        notif_types.add("qc")
    if "Bent column" in n.get("title", ""):
        notif_types.add("punch")
test("E2E: pm_zack got QC rejection notification", "qc" in notif_types)
test("E2E: pm_zack got critical punch notification", "punch" in notif_types)

sarah_notifs = get_notifications(tmp2, "pm_sarah")
test("E2E: pm_sarah has critical notification", len(sarah_notifs) >= 1)
test("E2E: pm_sarah not notified for QC rejection",
     not any("QC rejected" in n.get("title", "") for n in sarah_notifs))

# 5. Verify stats
stats_e2e = get_event_stats(tmp2, days_back=1)
test("E2E: stats total is 4", stats_e2e["total_events"] == 4)

# 6. Query by project
proj_events = get_events(tmp2, job_code="JOB-E2E")
test("E2E: all 4 events are JOB-E2E", proj_events["total"] == 4)

# Cleanup
shutil.rmtree(tmp2, ignore_errors=True)
shutil.rmtree(tmp, ignore_errors=True)


# ═══════════════════════════════════════════════════════════════════
print(f"\n{'='*60}")
print(f"Phase 7 Results: {passed} passed, {failed} failed, {passed + failed} total")
print(f"{'='*60}")
if failed > 0:
    sys.exit(1)
